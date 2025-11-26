import streamlit as st
import time
import ai_manager
import graphics

# --- 1. OPSÆTNING ---
st.set_page_config(page_title="Sumvival Game", page_icon="💀", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #000000 !important; color: #ffffff !important; }
    p, h1, h2, h3, li, .stMarkdown { color: #ffffff !important; }
    
    /* Knapper */
    div.stButton > button {
        width: 100%; height: 60px; background-color: #111111;
        color: #00ff00; border: 2px solid #00ff00;
        font-size: 20px; font-weight: bold; transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #003300; border-color: #ffffff; color: #ffffff;
    }
    
    /* Status bar */
    .status-bar {
        padding: 10px; border-bottom: 2px solid #333;
        margin-bottom: 20px; font-family: monospace; font-size: 18px;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. STATE ---
defaults = {'mode': 'MENU', 'scenario': None, 'lives': 3, 'progress': 0, 'start_time': 0, 'msg': ""}
for k, v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v

# --- 3. LOGIK ---

# --- FASE 1: MENU ---
if st.session_state.mode == 'MENU':
    st.title("💀 SUMVIVAL GAME")
    st.write("Vælg parametre for simulationen.")
    
    c1, c2 = st.columns(2)
    fag = c1.selectbox("Fag", ["Matematik", "Fysik"])
    emne = c2.text_input("Emne", "Funktioner")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("HENT MISSION", use_container_width=True):
        with st.spinner("Downloader scenarie fra hovedcomputeren..."):
            scenarie = ai_manager.generate_scenario(fag, emne)
            st.session_state.scenario = scenarie
            st.session_state.mode = 'BRIEFING' # Gå til briefing først!
            st.session_state.progress = 0
            st.session_state.lives = 3
            st.session_state.msg = ""
            st.rerun()

# --- FASE 2: BRIEFING (Historie før start) ---
elif st.session_state.mode == 'BRIEFING':
    room = st.session_state.scenario['rooms'][0]
    
    st.title("📁 MISSION BRIEFING")
    st.info(f"**SITUATION:** {room['story']}")
    
    st.write("Du skal krydse broen ved at svare rigtigt på 3 spørgsmål.")
    st.warning(f"⚠️ ADVARSEL: Du har kun {room['time_limit']} sekunder, når du starter!")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Her starter vi spillet og tiden
    if st.button("JEG ER KLAR - START SPIL", use_container_width=True):
        st.session_state.mode = 'PLAYING'
        st.session_state.start_time = time.time() # Tiden starter NU
        st.rerun()

# --- FASE 3: SPILLET KØRER ---
elif st.session_state.mode == 'PLAYING':
    room = st.session_state.scenario['rooms'][0]
    steps = room['steps']
    idx = st.session_state.progress
    
    # Tidsstyring
    elapsed = time.time() - st.session_state.start_time
    time_left = max(0, room['time_limit'] - elapsed)
    
    if elapsed > room['time_limit']:
        st.session_state.mode = 'DEATH'
        st.session_state.msg = "TIDEN UDLØB! Du var for langsom."
        st.rerun()

    # HUD
    lives_icon = "❤️" * st.session_state.lives
    st.markdown(f"""<div class="status-bar">LIV: {lives_icon} &nbsp;|&nbsp; TID: {int(time_left)}s &nbsp;|&nbsp; TRIN: {idx+1}/{len(steps)}</div>""", unsafe_allow_html=True)

    # Grafik
    graphics.render_game_scene('PLAYING', idx, room['time_limit'])
    
    # Spørgsmål (Vises kun her, ikke i briefing)
    if idx < len(steps):
        q = steps[idx]
        st.markdown(f"### ❓ {q['q']}")
        
        if st.session_state.msg:
            st.caption(st.session_state.msg)

        c1, c2 = st.columns(2)
        if c1.button(q['options'][0], key="opt1", use_container_width=True):
            if q['options'][0] == q['correct']:
                st.session_state.progress += 1
                st.session_state.msg = "✅ Korrekt! Videre!"
                st.rerun()
            else:
                st.session_state.mode = 'DEATH'
                st.session_state.msg = "❌ Forkert valg! Du faldt."
                st.rerun()
        
        if c2.button(q['options'][1], key="opt2", use_container_width=True):
            if q['options'][1] == q['correct']:
                st.session_state.progress += 1
                st.session_state.msg = "✅ Korrekt! Videre!"
                st.rerun()
            else:
                st.session_state.mode = 'DEATH'
                st.session_state.msg = "❌ Forkert valg! Du faldt."
                st.rerun()
    else:
        st.balloons()
        st.success("RUM GENNEMFØRT!")
        if st.button("Gå til hovedmenu"):
            st.session_state.mode = 'MENU'
            st.rerun()

# --- FASE 4: DØD ---
elif st.session_state.mode == 'DEATH':
    st.error(f"💀 {st.session_state.msg}")
    graphics.render_game_scene('DEATH', st.session_state.progress, 1)
    
    st.markdown("# DU DØDE")
    if st.button(f"PRØV IGEN (-1 Liv)", use_container_width=True):
        st.session_state.lives -= 1
        if st.session_state.lives <= 0:
            st.session_state.mode = 'MENU'
        else:
            st.session_state.mode = 'PLAYING'
            st.session_state.progress = 0 
            st.session_state.start_time = time.time()
            st.session_state.msg = ""
        st.rerun()
