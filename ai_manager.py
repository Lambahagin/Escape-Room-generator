from openai import OpenAI
import json
import streamlit as st

def get_client():
    if "OPENAI_API_KEY" in st.secrets:
        return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    return None

def get_fallback_scenario():
    return {
        "title": "Nød-protokol (Offline)",
        "intro": "AI-forbindelsen svigtede. Manuel protokol aktiveret.",
        "rooms": [
            {
                "type": "BRIDGE",
                "story": "Du står på glasbroen. Du skal svare rigtigt 4 gange for at nå sikkerhed.",
                "time_limit": 25, # Lidt mere tid til 4 spørgsmål
                "steps": [
                    {"q": "Hvad er 2+2?", "options": ["4", "5"], "correct": "4"},
                    {"q": "Hvad er 3*3?", "options": ["9", "6"], "correct": "9"},
                    {"q": "Hvad er 10/2?", "options": ["5", "2"], "correct": "5"},
                    {"q": "Hvad er 100-1?", "options": ["99", "100"], "correct": "99"}
                ]
            }
        ]
    }

def generate_scenario(fag, emne):
    client = get_client()
    if not client: return get_fallback_scenario()

    prompt = f"""
    Du er Game Master for et Squid Game. Generer 1 'BRIDGE' rum baseret på {fag} ({emne}).
    
    REGLER:
    1. Der skal være PRÆCIS 4 spørgsmål (steps).
    2. Hvert step har 2 'options', kun én er rigtig.
    3. 'correct' SKAL matche den rigtige option præcist.
    4. Tiden skal være 25 sekunder.
    
    JSON FORMAT:
    {{
        "title": "Titel", "intro": "Intro",
        "rooms": [
            {{
                "type": "BRIDGE", "story": "Historie", "time_limit": 25,
                "steps": [
                    {{"q": "Q1", "options": ["A", "B"], "correct": "A"}},
                    {{"q": "Q2", "options": ["A", "B"], "correct": "A"}},
                    {{"q": "Q3", "options": ["A", "B"], "correct": "A"}},
                    {{"q": "Q4", "options": ["A", "B"], "correct": "A"}}
                ]
            }}
        ]
    }}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=[{"role": "system", "content": prompt}],
            temperature=0.5,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception:
        return get_fallback_scenario()
