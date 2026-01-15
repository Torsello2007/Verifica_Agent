# app.py
import streamlit as st
from dotenv import load_dotenv
import os

# Carica ambiente prima di importare l'agente
load_dotenv()

from agent_brain import KitchenAgent
from state_manager import update_pantry_state
from langchain_core.messages import HumanMessage, AIMessage

st.set_page_config(page_title="AI Kitchen Agent", layout="wide", page_icon="👨‍🍳")

# Verifica chiave API
if not os.getenv("GROQ_API_KEY"):
    st.error("⚠️ Chiave GROQ_API_KEY mancante nel file .env!")
    st.stop()

# Inizializzazione
if "agent" not in st.session_state:
    st.session_state.agent = KitchenAgent()
if "pantry" not in st.session_state:
    st.session_state.pantry = {"ingredients": [], "preferences": [], "health_constraints": []}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- SIDEBAR ---
st.sidebar.title("🍱 Dispensa Aggiornata")
st.sidebar.info("L'agente estrae i dati dalla chat in tempo reale.")

st.sidebar.subheader("🛒 Ingredienti")
if not st.session_state.pantry["ingredients"]:
    st.sidebar.write("*Nessun ingrediente rilevato*")
for ing in st.session_state.pantry["ingredients"]:
    warn = "⚠️" if ing.get("near_expiry") else "✅"
    st.sidebar.write(f"{warn} **{ing['name']}** ({ing.get('amount', 'q.b.')})")

st.sidebar.subheader("👤 Note Utente")
for p in st.session_state.pantry["preferences"] + st.session_state.pantry["health_constraints"]:
    st.sidebar.write(f"🔹 {p}")

if st.sidebar.button("Reset Conversazione"):
    st.session_state.chat_history = []
    st.session_state.pantry = {"ingredients": [], "preferences": [], "health_constraints": []}
    st.rerun()

# --- CHAT ---
st.title("👨‍🍳 Assistant Chef AI")
st.write("Applicazione basata sul Capitolo 6 del libro 'AI Engineering' di Chip Huyen.")

for msg in st.session_state.chat_history:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.write(msg.content)

if user_input := st.chat_input("Ciao! Cosa hai in cucina oggi?"):
    st.chat_message("user").write(user_input)
    
    with st.spinner("L'agente sta elaborando..."):
        result = st.session_state.agent.think(
            user_input, 
            st.session_state.chat_history, 
            st.session_state.pantry
        )
    
    if result:
        # Aggiorna lo stato dei dati
        if result.get("extracted_data"):
            st.session_state.pantry = update_pantry_state(st.session_state.pantry, result["extracted_data"])
        
        reply = result.get("reply", "Capito, dimmi altro.")
        st.chat_message("assistant").write(reply)
        
        # Salva in cronologia
        st.session_state.chat_history.append(HumanMessage(content=user_input))
        st.session_state.chat_history.append(AIMessage(content=reply))
        
        # Ricarica per la sidebar
        st.rerun()