import streamlit as st
import time
import ai_manager
import graphics

# --- 1. OPSÆTNING ---
st.set_page_config(page_title="Sumvival Game", page_icon="💀", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #000000 !important; color: #ffffff !important; }
    p, h1, h2, h3, li, .stMarkdown, .stCaption { color: #ffffff !important; }
    
    /* Menu synlig */
    header { visibility: visible !important; }
    .stDeployButton { display:none; }
    div[data-testid="stToolbar"] { visibility: visible !important; opacity: 1 !important; color: white !important; }
    div[data-testid="stToolbar"] button { color: white !important; }

    div.stButton > button {
        width: 100%; height: 60px; background-color: #111111;
        color: #00ff00; border: 2px solid #00ff00;
        font-size: 20px; font-weight: bold; transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #003300; border-color: #ffffff; color: #ffffff;
    }
    .status-bar {
        padding: 10px; border-bottom: 2px solid #333; margin-bottom: 20px; font-family: monospace; font-size: 18px;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. STATE ---
defaults = {
    'mode': 'MENU', 'scenario': None, 'lives': 3, 'progress': 0, 
    'start_time': 0, 'msg': "", 'monster_anchor': 0,
    'last_update_time': 0
}
for k, v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v

# --- HELPER: MONSTER POS ---
def calculate_current_monster_x(total_time, elapsed):
    """Hjælper til at finde anker-punktet uden hop"""
    start_x = st.session_state.monster_anchor
    target_x = 150 + (st.session_state.progress * 100)
    
    # Hvor lang tid har dette 'step' varet indtil nu?
    step_elapsed = time.time() - st.session_state.last_update_time
    
    # Hvor lang tid var der tilbage totalt, da dette step startede?
    time_left_at_start = total_time - (st.session_state.last_update_time - st.session_state.start_time)
    
    if time_left_at_start <= 0: return target_x
    
    pct = min(step_elapsed / time_left_at_start, 1.0)
    dist = target_x - start_x
    return start_x + (dist * pct)

# --- 3. LOGIK ---

if st.session_state.mode == 'MENU':
    st.title("💀 SUMVIVAL GAME")
    st.write("Systemet er klar.")
    c1, c2 = st.columns(2)
    fag = c1.selectbox("Fag", ["Matematik", "Fysik"])
    emne = c2.text_input("Emne", "Funktioner")
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("HENT MISSION", use_container_width=True):
        with st.spinner("Forbereder..."):
            scenarie = ai_manager.generate_scenario(fag, emne)
            st.session_state.scenario = scenarie
            st.session_state.mode = 'BRIEFING'
            st.session_state.progress = 0
            st.session_state.lives = 3
            st.session_state.msg = ""
            st.session_state.monster_anchor = 0
            st.rerun()

elif st.session_state.mode == 'BRIEFING':
    room = st.session_state.scenario['rooms'][0]
    st.title("📁 MISSION BRIEFING")
    
    graphics.render_game_scene('BRIEFING', 0, 20, 0, 0)
    
    st.info(f"**HISTORIE:** {room['story']}")
    st.warning(f"⚠️ Tid: {room['time_limit']} sekunder.")
    
    if st.button("JEG ER KLAR - START SPIL", use_container_width=True):
        st.session_state.mode = 'PLAYING'
        now = time.time()
        st.session_state.start_time = now
        st.session_state.last_update_time = now
        st.session_state.monster_anchor = 0 
        st.rerun()

elif st.session_state.mode == 'PLAYING':
    room = st.session_state.scenario['rooms'][0]
    steps = room['steps']
    idx = st.session_state.progress
    
    elapsed = time.time() - st.session_state.start_time
    time_left = max(0, room['time_limit'] - elapsed)
    
    # VIGTIGT: Vi har fjernet auto-rerun loopet her!
    # Siden blinker ikke længere.
    
    # Hvis brugeren klikker, og tiden ER gået -> DØD
    if elapsed > room['time_limit']:
        st.session_state.mode = 'DEATH'
        st.session_state.msg = "TIDEN ER UDLØBET!"
        st.rerun()

    lives_icon = "❤️" * st.session_state.lives
    st.markdown(f"""<div class="status-bar">LIV: {lives_icon} &nbsp;|&nbsp; TRIN: {idx+1}/{len(steps)}</div>""", unsafe_allow_html=True)

    # Grafik
    graphics.render_game_scene('PLAYING', idx, room['time_limit'], elapsed, st.session_state.monster_anchor)
    
    if idx < len(steps):
        q = steps[idx]
        st.markdown(f"### ❓ {q['q']}")
        if st.session_state.msg: st.caption(st.session_state.msg)

        c1, c2 = st.columns(2)
        
        def answer(opt):
            # 1. Beregn hvor monsteret er lige nu (Anker)
            current_pos = calculate_current_monster_x(room['time_limit'], elapsed)
            st.session_state.monster_anchor = current_pos
            st.session_state.last_update_time = time.time()
            
            if opt == q['correct']:
                st.session_state.progress += 1
                st.session_state.msg = "✅"
            else:
                st.session_state.mode = 'DEATH'
                st.session_state.msg = "❌ FORKERT!"
        
        if c1.button(q['options'][0], key="1", use_container_width=True):
            answer(q['options'][0])
            st.rerun()
        if c2.button(q['options'][1], key="2", use_container_width=True):
            answer(q['options'][1])
            st.rerun()
    else:
        st.balloons()
        st.success("DU KLAREDE DET!")
        if st.button("Menu"):
            st.session_state.mode = 'MENU'
            st.rerun()

elif st.session_state.mode == 'DEATH':
    st.error(f"💀 {st.session_state.msg}")
    # Vis dødsscene
    graphics.render_game_scene('DEATH', st.session_state.progress, 1, 0, 0)
    
    if st.button("PRØV IGEN (-1 Liv)", use_container_width=True):
        st.session_state.lives -= 1
        if st.session_state.lives <= 0:
            st.session_state.mode = 'MENU'
        else:
            st.session_state.mode = 'PLAYING'
            st.session_state.progress = 0
            now = time.time()
            st.session_state.start_time = now
            st.session_state.last_update_time = now
            st.session_state.monster_anchor = 0 # Nulstil monster
            st.session_state.msg = ""
        st.rerun()

st.markdown("---")
if st.button("🔧 REBOOT APP"):
    st.session_state.clear()
    st.rerun()
