# state_manager.py

def update_pantry_state(current_state, new_data):
    """Sincronizza lo stato della dispensa con le nuove info estratte dall'IA."""
    if not new_data:
        return current_state
    
    # Aggiorna o aggiungi ingredienti
    for new_ing in new_data.get("ingredients", []):
        exists = False
        for old_ing in current_state["ingredients"]:
            if old_ing["name"].lower() == new_ing["name"].lower():
                old_ing.update(new_ing)
                exists = True
        if not exists:
            current_state["ingredients"].append(new_ing)

    # Aggiorna preferenze e vincoli
    current_state["preferences"] = list(set(current_state["preferences"] + new_data.get("preferences", [])))
    current_state["health_constraints"] = list(set(current_state["health_constraints"] + new_data.get("health_constraints", [])))
    
    # AGGIUNTA: Aggiorna numero di persone se rilevato
    if new_data.get("people"):
        current_state["people"] = new_data["people"]
    
    return current_state