from openai import OpenAI
import json
import streamlit as st

def get_client():
    if "OPENAI_API_KEY" in st.secrets:
        return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    return None

def get_fallback_scenario():
    """Nød-scenarie med korrekt matematik."""
    return {
        "title": "Nød-protokol (Offline)",
        "intro": "AI-forbindelsen svigtede. Vi kører manuel protokol.",
        "rooms": [
            {
                "type": "BRIDGE",
                "story": "Du står på glasbroen. Systemet er nede, men matematikken gælder stadig.",
                "time_limit": 20,
                "steps": [
                    {"q": "Hvad er 10 + 10?", "options": ["20", "22"], "correct": "20"},
                    {"q": "Isoler x i: 2x = 8", "options": ["x=4", "x=2"], "correct": "x=4"},
                    {"q": "Hvad er kvadratroden af 49?", "options": ["7", "9"], "correct": "7"}
                ]
            }
        ]
    }

def generate_scenario(fag, emne):
    client = get_client()
    
    if not client:
        return get_fallback_scenario()

    # Opdateret prompt med strammere regler
    prompt = f"""
    Du er Game Master for et spil baseret på Squid Game.
    Generer et scenarie med 1 rum af typen 'BRIDGE' baseret på faget {fag} og emnet {emne}.
    
    REGLER FOR OPGAVER:
    1. Der skal være præcis 3 spørgsmål (steps).
    2. 'options' SKAL indeholde præcis 2 svarmuligheder.
    3. Én af mulighederne SKAL være matematisk/fysisk 100% korrekt.
    4. Den anden mulighed skal være forkert.
    5. Feltet 'correct' SKAL være helt identisk (tegn for tegn) med den rigtige af de to 'options'.
    
    Tiden skal være 20 sekunder.
    
    Output SKAL være gyldig JSON:
    {{
        "title": "Kort titel",
        "intro": "Kort intro historie",
        "rooms": [
            {{
                "type": "BRIDGE",
                "story": "Beskrivelse af situationen.",
                "time_limit": 20,
                "steps": [
                    {{"q": "Spørgsmål 1", "options": ["Svar A", "Svar B"], "correct": "Svar A"}},
                    {{"q": "Spørgsmål 2", "options": ["Svar A", "Svar B"], "correct": "Svar A"}},
                    {{"q": "Spørgsmål 3", "options": ["Svar A", "Svar B"], "correct": "Svar A"}}
                ]
            }}
        ]
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=[{"role": "system", "content": prompt}],
            temperature=0.5, # Lavere temperatur = mere præcis matematik
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)
        return data
    except Exception as e:
        print(f"AI FEJL: {e}")
        return get_fallback_scenario()
