from openai import OpenAI
import json
import streamlit as st

def get_client():
    # Tjekker om nøglen findes, ellers returnerer None
    if "OPENAI_API_KEY" in st.secrets:
        return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    return None

def get_fallback_scenario():
    """Returnerer et fast scenarie hvis AI fejler"""
    return {
        "title": "Nød-protokol (Offline)",
        "intro": "AI-forbindelsen svigtede, men spillet fortsætter...",
        "rooms": [
            {
                "type": "BRIDGE",
                "story": "Du står på en glasbro. En mørk skygge nærmer sig bagfra. Vælg rigtigt for at overleve.",
                "time_limit": 30,
                "steps": [
                    {"q": "Hvad er 2x = 10?", "options": ["x=5", "x=2"], "correct": "x=5"},
                    {"q": "Find f'(x) af x^2", "options": ["2x", "x"], "correct": "2x"},
                    {"q": "Er pi > 3?", "options": ["Ja", "Nej"], "correct": "Ja"}
                ]
            }
        ]
    }

def generate_scenario(fag, emne):
    client = get_client()
    
    # Hvis vi ikke har en klient, eller hvis kaldet fejler, brug fallback
    if not client:
        return get_fallback_scenario()

    prompt = f"""
    Du er Game Master. Lav et spil scenarie baseret på {fag} ({emne}).
    Output SKAL være rå JSON (ingen markdown '```json' rundt om):
    {{
        "title": "Kort titel",
        "intro": "Kort intro historie",
        "rooms": [
            {{
                "type": "BRIDGE",
                "story": "Beskrivelse af situationen.",
                "time_limit": 45,
                "steps": [
                    {{"q": "Spørgsmål 1", "options": ["Rigtigt Svar", "Forkert"], "correct": "Rigtigt Svar"}},
                    {{"q": "Spørgsmål 2", "options": ["Rigtigt Svar", "Forkert"], "correct": "Rigtigt Svar"}},
                    {{"q": "Spørgsmål 3", "options": ["Rigtigt Svar", "Forkert"], "correct": "Rigtigt Svar"}}
                ]
            }}
        ]
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # Skift til gpt-4-turbo for bedre matematik
            messages=[{"role": "system", "content": prompt}],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        # Vi parser JSON svaret
        data = json.loads(response.choices[0].message.content)
        return data
    except Exception as e:
        print(f"AI FEJL: {e}")
        return get_fallback_scenario()
