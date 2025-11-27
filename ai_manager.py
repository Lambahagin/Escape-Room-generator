from openai import OpenAI
import json
import streamlit as st

def get_client():
    if "OPENAI_API_KEY" in st.secrets:
        return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    return None

def get_fallback_scenario(theme):
    """Nød-scenarie hvis AI fejler (Tilpasset tema)"""
    if theme == "wonderland":
        return {
            "title": "Eventyrlandet (Offline)",
            "intro": "Du er faldet ned i kaninhullet. For at komme hjem må du løse gåden.",
            "rooms": [{
                "type": "BRIDGE",
                "story": "En magisk bro af svævende kort viser sig. Den Grinende Kat ser på dig.",
                "time_limit": 25,
                "steps": [
                    {"q": "2+2?", "options": ["4", "5"], "correct": "4"},
                    {"q": "3*3?", "options": ["9", "6"], "correct": "9"},
                    {"q": "10/2?", "options": ["5", "2"], "correct": "5"},
                    {"q": "100-1?", "options": ["99", "100"], "correct": "99"}
                ]
            }]
        }
    else: # Squid default
        return {
            "title": "Nød-protokol (Offline)",
            "intro": "AI-forbindelsen svigtede. Manuel protokol aktiveret.",
            "rooms": [{
                "type": "BRIDGE",
                "story": "Du står på glasbroen. Systemet er nede, men matematikken gælder stadig.",
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
    
    # Hvis klient mangler, brug fallback
    if not client:
        return get_fallback_scenario(theme)

    # Vælg instruks baseret på tema
    if theme == "wonderland":
        role_description = "Du er The Cheshire Cat fra Alice i Eventyrland. Din tone er drilsk, mystisk og eventyrlig. Du taler i gåder."
        context_description = "Spilleren er fanget i en magisk verden og skal over en bro af tryllestøv."
    else:
        role_description = "Du er Game Master for et spil baseret på Squid Game (Dødsspillet). Din tone er kold, autoritær og uhyggelig."
        context_description = "Spilleren står på en glasbro over en dyb afgrund."

    prompt = f"""
    {role_description}
    Generer et scenarie med 1 rum af typen 'BRIDGE' baseret på faget {fag} og emnet {emne}.
    {context_description}
    
    REGLER FOR OPGAVER:
    1. Der skal være PRÆCIS 4 spørgsmål (steps).
    2. Hvert step har 2 'options', kun én er rigtig.
    3. 'correct' SKAL matche den rigtige option præcist.
    4. Tiden skal være 25 sekunder.
    
    Output SKAL være gyldig JSON:
    {{
        "title": "Kort titel",
        "intro": "Kort intro historie",
        "rooms": [
            {{
                "type": "BRIDGE",
                "story": "Beskrivelse af situationen (i din karakters tone).",
                "time_limit": 25,
                "steps": [
                    {{"q": "Spørgsmål 1", "options": ["Svar A", "Svar B"], "correct": "Svar A"}},
                    {{"q": "Spørgsmål 2", "options": ["Svar A", "Svar B"], "correct": "Svar A"}},
                    {{"q": "Spørgsmål 3", "options": ["Svar A", "Svar B"], "correct": "Svar A"}},
                    {{"q": "Spørgsmål 4", "options": ["Svar A", "Svar B"], "correct": "Svar A"}}
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
