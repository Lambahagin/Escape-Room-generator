# ai_manager.py
from openai import OpenAI
import json
import streamlit as st

def get_client():
    if "OPENAI_API_KEY" in st.secrets:
        return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    return None

def get_fallback_scenario(theme):
    # En simpel fallback titel hvis AI fejler
    return {
        "title": f"{theme.capitalize()} Mission (Offline)",
        "intro": "Forbindelsen til AI røg. Kører manuel protokol.",
        "rooms": [{
            "type": "BRIDGE",
            "story": "Du skal krydse broen ved at løse opgaverne.",
            "time_limit": 25,
            "steps": [
                {"q": "2+2?", "options": ["4", "5"], "correct": "4"},
                {"q": "3*3?", "options": ["9", "6"], "correct": "9"},
                {"q": "10/2?", "options": ["5", "2"], "correct": "5"},
                {"q": "100-1?", "options": ["99", "100"], "correct": "99"}
            ]
        }]
    }

def generate_scenario(fag, emne, theme="squid"):
    client = get_client()
    if not client: return get_fallback_scenario(theme)

    # 1. Definer Roller baseret på tema
    if theme == "wonderland":
        role = "Du er The Cheshire Cat. Drilsk, mystisk og eventyrlig tone."
        context = "Spilleren er i en magisk verden og skal over en bro af lyserødt glas."
    elif theme == "cyberpunk":
        role = "Du er 'The Mainframe', en kold kunstig intelligens. Binær, logisk og truende tone."
        context = "Spilleren er en hacker, der skal krydse en firewall (digital bro) før en virus fanger dem."
    elif theme == "jungle":
        role = "Du er 'Tempelvogteren', en ældgammel ånd. Højtidelig, mystisk og advarende tone."
        context = "Spilleren er en opdagelsesrejsende på en rådden hængebro over en kløft med en kæmpe edderkop bag sig."
    else: # Squid
        role = "Du er Game Master for Squid Game. Kold, autoritær og uhyggelig tone."
        context = "Spilleren står på en glasbro over en dyb afgrund."

    prompt = f"""
    {role}
    Generer et scenarie med 1 rum af typen 'BRIDGE' baseret på faget {fag} og emnet {emne}.
    {context}
    
    REGLER:
    1. 4 spørgsmål (steps).
    2. Hvert step har 2 options, én er korrekt.
    3. Tiden skal være 25 sekunder.
    
    JSON FORMAT:
    {{
        "title": "Kort titel (Passende til temaet)",
        "intro": "Kort intro historie",
        "rooms": [
            {{
                "type": "BRIDGE",
                "story": "Beskrivelse af situationen (i din karakters tone).",
                "time_limit": 25,
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
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"AI FEJL: {e}")
        return get_fallback_scenario(theme)
