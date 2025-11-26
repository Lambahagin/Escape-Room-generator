import streamlit as st
import time
import ai_manager  # Vi importerer vores hjerne
import graphics    # Vi importerer vores grafik

# --- 1. OPSÆTNING ---
st.set_page_config(page_title="Sumvival Game Modular", page_icon="🦑")

# CSS Styling
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .big-btn { width: 100%; height: 70px; font-size: 24px; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 2. SESSION STATE (Hukommelse) ---
if 'mode' not in st.session_state:
    st.session_state.mode = 'MENU'
    st.session_state.scenario = None
    st.session_state.lives = 3
    st.session_state.progress = 0
    st.session_state.start_time = 0
    st.session_state.msg = ""

# --- 3. SPIL LOGIK ---

# MENU TILSTAND
if st.session_state.mode == 'MENU':
    st.title("🦑 SUMVIVAL GAME")
    st.write("Systemet er klar. Vælg din udfordring.")
    
    c1, c2 = st.columns(2)
    fag = c1.selectbox("Fag", ["Matematik", "Fysik"])
    emne = c2.text_input("Emne", "Funktioner")
    
    if st.button("START SCENARIE", type="primary", use_container_width=True):
        with st.spinner("Henter data fra hovedcomputeren..."):
            # HER KALDER VI VORES NYE AI FIL
            scenarie = ai_manager.generate_scenario(fag, emne)
            
            # Opdater tilstand
            st.session_state.scenario = scenarie
            st.session_state.mode = 'PLAYING'
            st.session_state.progress = 0
            st.session_state.lives = 3
            st.session_state.start_time = time.time()
            st.rerun()

# SPIL TILSTAND
elif st.session_state.mode == 'PLAYING':
    room = st.session_state.scenario['rooms'][0] # Henter første rum
    steps = room['steps']
    idx = st.session_state.progress
    
    # Tjek tid
    elapsed = time.time() - st.session_state.start_time
    if elapsed > room['time_limit']:
        st.session_state.mode = 'DEATH'
        st.session_state.msg = "Tiden løb ud! Skyggen fangede dig."
        st.rerun()

    # Vis Info
    st.info(f"**{st.session_state.scenario['title']}** | {room['story']}")
    st.write(f"❤️ Liv: {st.session_state.lives}")
    
    if st.session_state.msg:
        st.warning(st.session_state.msg)

    # HER KALDER VI VORES NYE GRAFIK FIL
    graphics.render_game_scene('PLAYING', idx, room['time_limit'])
    
    # Vis Spørgsmål
    if idx < len(steps):
        q = steps[idx]
        st.markdown(f"### ❓ {q['q']}")
        
        c1, c2 = st.columns(2)
        if c1.button(q['options'][0], use_container_width=True):
            if q['options'][0] == q['correct']:
                st.session_state.progress += 1
                st.session_state.msg = "✅ Korrekt!"
                st.rerun()
            else:
                st.session_state.mode = 'DEATH'
                st.session_state.msg = "❌ Forkert svar! Du faldt."
                st.rerun()
                
        if c2.button(q['options'][1], use_container_width=True):
            if q['options'][1] == q['correct']:
                st.session_state.progress += 1
                st.session_state.msg = "✅ Korrekt!"
                st.rerun()
            else:
                st.session_state.mode = 'DEATH'
                st.session_state.msg = "❌ Forkert svar! Du faldt."
                st.rerun()
    else:
        st.balloons()
        st.success("DU KLAREDE DET!")
        if st.button("Start forfra"):
            st.session_state.mode = 'MENU'
            st.rerun()

# DØDS TILSTAND
elif st.session_state.mode == 'DEATH':
    st.error(f"💀 {st.session_state.msg}")
    
    # Vis Døds-animationen
    graphics.render_game_scene('DEATH', st.session_state.progress, 1)
    
    st.markdown("# DU DØDE")
    
    if st.button("PRØV IGEN (-1 Liv)", type="primary"):
        st.session_state.lives -= 1
        if st.session_state.lives <= 0:
            st.session_state.mode = 'MENU' # Game over helt
        else:
            st.session_state.mode = 'PLAYING'
            st.session_state.progress = 0 # Start forfra på broen
            st.session_state.start_time = time.time() # Nulstil tid
            st.session_state.msg = ""
        st.rerun()
