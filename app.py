import streamlit as st
import time
import ai_manager
import graphics

# --- 1. OPSÆTNING & DESIGN ---
st.set_page_config(page_title="Sumvival Game", page_icon="💀", layout="centered")

# HØJ KONTRAST CSS
st.markdown("""
<style>
    /* Tving sort baggrund og hvid tekst overalt */
    .stApp {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    
    /* Sørg for at al tekst er hvid og læselig */
    p, h1, h2, h3, li, .stMarkdown {
        color: #ffffff !important;
    }

    /* Fix Streamlits blå info-bokse så de er læselige */
    div[data-baseweb="notification"] {
        background-color: #1a1a1a !important;
        border: 1px solid cyan !important;
        color: #ffffff !important;
    }
    
    /* Knapper */
    div.stButton > button {
        width: 100%;
        height: 60px;
        background-color: #111111;
        color: #00ff00; /* Matrix grøn */
        border: 2px solid #00ff00;
        font-size: 20px;
        font-weight: bold;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #003300;
        border-color: #ffffff;
        color: #ffffff;
    }
    
    /* Status bar */
    .status-bar {
        padding: 10px;
        border-bottom: 2px solid #333;
        margin-bottom: 20px;
        font-family: monospace;
        font-size: 18px;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. SIKKER INITIALISERING AF STATE ---
# Dette forhindrer "AttributeError" ved at sikre, at alle variabler findes
default_values = {
    'mode': 'MENU',
    'scenario': None,
    'lives': 3,
    'progress': 0,
    'start_time': 0,
    'msg': ""  # Denne manglede før og skabte fejlen
}

for key, value in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- 3. SPIL LOGIK ---

# MENU
if st.session_state.mode == 'MENU':
    st.title("💀 SUMVIVAL GAME")
    st.markdown("### OPERATOR MENU")
    st.write("Systemet er klar. Vælg parametre for simulationen.")
    
    c1, c2 = st.columns(2)
    fag = c1.selectbox("Fag", ["Matematik", "Fysik"])
    emne = c2.text_input("Emne", "Funktioner")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("INITIALISER SCENARIE", use_container_width=True):
        with st.spinner("Indlæser scenarie..."):
            scenarie = ai_manager.generate_scenario(fag, emne)
            st.session_state.scenario = scenarie
            st.session_state.mode = 'PLAYING'
            st.session_state.progress = 0
            st.session_state.lives = 3
            st.session_state.start_time = time.time()
            st.session_state.msg = "" # Nulstil besked
            st.rerun()

# SPILLET KØRER
elif st.session_state.mode == 'PLAYING':
    # Hent nuværende data
    room = st.session_state.scenario['rooms'][0]
    steps = room['steps']
    idx = st.session_state.progress
    
    # Tidsstyring
    elapsed = time.time() - st.session_state.start_time
    time_left = max(0, room['time_limit'] - elapsed)
    
    # Død ved tid
    if elapsed > room['time_limit']:
        st.session_state.mode = 'DEATH'
        st.session_state.msg = "TIDEN UDLØB! Du var for langsom."
        st.rerun()

    # --- HUD (Heads Up Display) ---
    lives_icon = "❤️" * st.session_state.lives
    st.markdown(f"""
    <div class="status-bar">
        LIV: {lives_icon} &nbsp;|&nbsp; TID: {int(time_left)}s &nbsp;|&nbsp; TRIN: {idx+1}/{len(steps)}
    </div>
    """, unsafe_allow_html=True)

    # Vis Historie/Besked
    st.info(f"**SCENARIE:** {room['story']}")
    
    if st.session_state.msg:
        if "Korrekt" in st.session_state.msg:
            st.success(st.session_state.msg)
        else:
            st.error(st.session_state.msg)

    # Tegn Grafik
    graphics.render_game_scene('PLAYING', idx, room['time_limit'])
    
    # Vis Spørgsmål
    if idx < len(steps):
        q = steps[idx]
        st.markdown(f"### ❓ {q['q']}")
        
        c1, c2 = st.columns(2)
        
        # Vi bruger keys for at undgå konflikter
        if c1.button(q['options'][0], key="opt1", use_container_width=True):
            if q['options'][0] == q['correct']:
                st.session_state.progress += 1
                st.session_state.msg = "✅ Korrekt svar! Du rykkede frem."
                st.rerun()
            else:
                st.session_state.mode = 'DEATH'
                st.session_state.msg = "❌ Forkert svar! Du mistede balancen."
                st.rerun()
                
        if c2.button(q['options'][1], key="opt2", use_container_width=True):
            if q['options'][1] == q['correct']:
                st.session_state.progress += 1
                st.session_state.msg = "✅ Korrekt svar! Du rykkede frem."
                st.rerun()
            else:
                st.session_state.mode = 'DEATH'
                st.session_state.msg = "❌ Forkert svar! Du mistede balancen."
                st.rerun()
    else:
        # Alle trin klaret
        st.balloons()
        st.success("RUM GENNEMFØRT!")
        if st.button("Gå til hovedmenu"):
            st.session_state.mode = 'MENU'
            st.rerun()

# DØD SKÆRM
elif st.session_state.mode == 'DEATH':
    st.error(f"💀 {st.session_state.msg}")
    
    # Tegn dødsanimation
    graphics.render_game_scene('DEATH', st.session_state.progress, 1)
    
    st.markdown("# DU DØDE")
    
    if st.button(f"PRØV IGEN (-1 Liv)", use_container_width=True):
        st.session_state.lives -= 1
        if st.session_state.lives <= 0:
            st.session_state.mode = 'MENU' # Game Over
        else:
            st.session_state.mode = 'PLAYING'
            st.session_state.progress = 0 # Start forfra på broen
            st.session_state.start_time = time.time() # Nulstil tid
            st.session_state.msg = ""
        st.rerun()
