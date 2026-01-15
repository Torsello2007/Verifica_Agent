# agent_brain.py
import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage 
from prompts import KITCHEN_SYSTEM_PROMPT

# Caricamento variabili d'ambiente
load_dotenv()

class KitchenAgent:
    def __init__(self):
        # Recupero della chiave corretta dal file .env
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("ERRORE: Chiave GROQ_API_KEY non trovata nel file .env")

        self.llm = ChatGroq(
            model_name="llama-3.3-70b-versatile",
            temperature=0.1,
            groq_api_key=api_key
        )

    def think(self, user_input, history, current_state):
        messages = [
            SystemMessage(content=KITCHEN_SYSTEM_PROMPT),
            SystemMessage(content=f"INFORMAZIONI ATTUALI NELLA SIDEBAR: {json.dumps(current_state)}")
        ]
        messages.extend(history)
        messages.append(HumanMessage(content=user_input))

        try:
            response = self.llm.invoke(messages)
            return self._parse_json(response.content)
        except Exception as e:
            return {
                "extracted_data": None,
                "reply": f"Errore tecnico: {str(e)}",
                "status": "GATHERING"
            }

    def _parse_json(self, content):
        try:
            clean = content.strip().replace("```json", "").replace("```", "")
            return json.loads(clean)
        except:
            return None
