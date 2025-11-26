import streamlit as st
from openai import OpenAI
import json
import time

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Sumvival Game", page_icon="☠️", layout="centered")

# CSS: Sort baggrund og spil-styling
st.markdown("""
<style>
    .stApp { background-color: #000000; color: #ffffff; }
    
    /* Knapper til spillet */
    .game-btn {
        width: 100%; height: 80px; margin-bottom: 10px;
        font-size: 22px; font-weight: bold; border-radius: 8px;
        background-color: #111; color: cyan; border: 2px solid cyan;
        cursor: pointer; transition: 0.2s;
    }
    .game-btn:hover { background-color: #004444; box-shadow: 0 0 15px cyan; }
    
    /* Info boks styling */
    .info-box {
        border: 1px solid #444; padding: 15px; border-radius: 10px;
        background-color: #1a1a1a; margin-bottom: 20px;
        font-family: 'Courier New', monospace;
    }
</style>
""", unsafe_allow_html=True)

# Hent API nøgle
if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.warning("⚠️ Mangler API nøgle. Kører i offline-tilstand (Demo).")
    client = None

# --- 2. STATE MANAGEMENT ---
if 'game_state' not in st.session_state:
    st.session_state.update({
        'mode': 'MENU',          # MENU, PLAYING, DEATH_ANIMATION, VICTORY
        'scenario': None,
        'current_room_idx': 0,
        'lives': 3,
        'bridge_progress': 0,    # Hvor langt er vi på broen (0-3)
        'start_time': 0,         # Starttidspunkt for nuværende forsøg
        'death_reason': ""       # Hvorfor døde vi?
    })

# --- 3. FUNKTIONER: GENERERING OG GRAFIK ---

def get_fallback_scenario():
    """Bruges hvis AI fejler, så spillet ikke går i stå."""
    return {
        "title": "Nød-protokol (Offline)",
        "intro": "AI forbindelsen røg, men spillet fortsætter...",
        "rooms": [
            {
                "type": "BRIDGE",
                "story": "Du står på en glasbro. Skyggen nærmer sig.",
                "time_limit": 30,
                "steps": [
                    {"q": "Hvad er 2+2?", "options": ["4", "5"], "correct": "4"},
                    {"q": "Hvad er 5*5?", "options": ["25", "10"], "correct": "25"},
                    {"q": "Hvad er 10-2?", "options": ["8", "2"], "correct": "8"}
                ]
            }
        ]
    }

def generate_scenario_ai(fag, emne):
    if not client:
        return get_fallback_scenario()
        
    prompt = f"""
    Du er Game Master for et dødeligt spil. Generer et scenarie med 1 'BRIDGE' type rum baseret på {fag} ({emne}).
    Output SKAL være gyldig JSON:
    {{
        "title": "Kort titel",
        "intro": "Kort introhistorie",
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
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception:
        return get_fallback_scenario()

def render_svg_animation(state_mode, progress, time_limit):
    """Tegner spillets grafik baseret på tilstand"""
    
    # Farver
    player_color = "#00ff00" # Grøn spiller
    shadow_color = "#000000" # Sort skygge
    
    # Animation variabler
    if state_mode == 'PLAYING':
        # Skyggen bevæger sig fra x=0 til x=180 over 'time_limit' sekunder
        shadow_anim = f'<animate attributeName="cx" from="20" to="200" dur="{time_limit}s" fill="freeze" />'
        # Spilleren står fast (men flytter sig ved rigtigt svar)
        player_y = 100
        player_anim = "" 
        shadow_cx = 20 # Start position (bliver overskrevet af animation)
        
    elif state_mode == 'DEATH_ANIMATION':
        # Spilleren falder
        shadow_anim = ""
        shadow_cx = 200 # Skyggen har fanget dig
        player_y = 100
        player_anim = '<animate attributeName="cy" from="100" to="400" dur="1s" fill="freeze" />'
    
    else: # Victory etc
        return ""

    # Spillerens X position afhænger af hvor langt vi er på broen (0, 1, 2)
    # Broen er 250px bred. Start = 200px (højre side), Slut = ?
    # I dette design kommer skyggen fra venstre, så spilleren er til højre.
    player_x = 200 + (progress * 40) 

    svg = f"""
    <svg width="100%" height="300" style="background: #444; border-radius: 10px; border: 2px solid #666;">
        <rect x="0" y="150" width="100%" height="150" fill="#222" />
        
        <rect x="50" y="120" width="300" height="10" fill="cyan" opacity="0.5" />
        <line x1="50" y1="120" x2="350" y2="120" stroke="cyan" stroke-width="2" />
        
        <g>
            <circle cx="{shadow_cx}" cy="90" r="30" fill="black" filter="url(#blurMe)">
                {shadow_anim}
            </circle>
            <circle cx="{shadow_cx+10}" cy="85" r="3" fill="red">
               {shadow_anim.replace('attributeName="cx"', 'attributeName="cx" values="' + str(20+10) + ';' + str(200+10) + '"')}
            </circle>
        </g>
        
        <circle cx="{player_x}" cy="{player_y}" r="15" fill="{player_color}" stroke="white" stroke-width="2">
            {player_anim}
        </circle>
        
        <defs>
            <filter id="blurMe">
                <feGaussianBlur in="SourceGraphic" stdDeviation="5" />
            </filter>
        </defs>
        
        <text x="20" y="30" fill="white" font-family="monospace">TRUSSEL NIVEAU:</text>
    </svg>
    """
    st.markdown(svg, unsafe_allow_html=True)

# --- 4. SPIL LOGIK (MAIN LOOP) ---

if st.session_state.mode == 'MENU':
    st.title("💀 SUMVIVAL GAME")
    st.write("Dungeon Masteren er klar. Vælg emne.")
    
    c1, c2 = st.columns(2)
    fag = c1.selectbox("Fag", ["Matematik", "Fysik"])
    emne = c2.text_input("Emne", "Lineære funktioner")
    
    if st.button("START SPILLET", use_container_width=True):
        with st.spinner("Genererer fælder..."):
            scenarie = generate_scenario_ai(fag, emne)
            st.session_state.scenario = scenarie
            st.session_state.mode = 'PLAYING'
            st.session_state.start_time = time.time()
            st.session_state.bridge_progress = 0
            st.session_state.lives = 3
            st.rerun()

elif st.session_state.mode == 'PLAYING':
    rum = st.session_state.scenario['rooms'][0] # Vi tager første rum for nu
    steps = rum['steps']
    current_step_idx = st.session_state.bridge_progress
    
    # Tids-tjek
    elapsed = time.time() - st.session_state.start_time
    
    if elapsed > rum['time_limit']:
        st.session_state.mode = 'DEATH_ANIMATION'
        st.session_state.death_reason = "Tiden løb ud! Skyggen fangede dig."
        st.rerun()
    
    # 1. VIS HISTORIE
    st.info(f"**RUM 1:** {rum['story']}")
    st.markdown(f"❤️ LIV: {'💚'*st.session_state.lives}")
    
    # 2. VIS ANIMATIONEN (Skyggen kommer!)
    render_svg_animation('PLAYING', current_step_idx, rum['time_limit'])
    
    # 3. VIS SPØRGSMÅL
    if current_step_idx < len(steps):
        q_data = steps[current_step_idx]
        st.markdown(f"### ❓ {q_data['q']}")
        
        cols = st.columns(2)
        for i, opt in enumerate(q_data['options']):
            # Vi bruger keys for at gøre knapperne unikke
            if cols[i].button(opt, key=f"btn_{current_step_idx}_{i}", use_container_width=True):
                if opt == q_data['correct']:
                    st.success("Korrekt!")
                    st.session_state.bridge_progress += 1
                    if st.session_state.bridge_progress >= len(steps):
                        st.session_state.mode = 'VICTORY'
                    st.rerun()
                else:
                    st.session_state.mode = 'DEATH_ANIMATION'
                    st.session_state.death_reason = "Forkert svar! Du mistede balancen."
                    st.rerun()
    else:
        st.session_state.mode = 'VICTORY'
        st.rerun()

elif st.session_state.mode == 'DEATH_ANIMATION':
    st.error(f"💀 {st.session_state.death_reason}")
    
    # Vis fald-animationen
    render_svg_animation('DEATH_ANIMATION', st.session_state.bridge_progress, 1)
    
    st.markdown("## DU DØDE")
    
    if st.button("PRØV IGEN (-1 Liv)", use_container_width=True):
        st.session_state.lives -= 1
        if st.session_state.lives <= 0:
            st.error("GAME OVER - Ingen liv tilbage.")
            if st.button("Tilbage til menu"):
                st.session_state.mode = 'MENU'
                st.rerun()
        else:
            # Genstart niveauet
            st.session_state.mode = 'PLAYING'
            st.session_state.bridge_progress = 0
            st.session_state.start_time = time.time() # Nulstil tid
            st.rerun()

elif st.session_state.mode == 'VICTORY':
    st.balloons()
    st.markdown("# 🏆 DU OVERLEVEDE RUMMET!")
    st.success("Godt gået! Du klarede presset.")
    if st.button("Start forfra"):
        st.session_state.mode = 'MENU'
        st.rerun()
