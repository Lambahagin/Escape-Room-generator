import streamlit as st
import time
import ai_manager
import graphics

st.set_page_config(page_title="Sumvival Game", page_icon="💀", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #000000 !important; color: #ffffff !important; }
    p, h1, h2, h3, li, .stMarkdown, .stCaption { color: #ffffff !important; }
    div.stButton > button { width: 100%; height: 60px; background-color: #111111; color: #00ff00; border: 2px solid #00ff00; font-size: 20px; font-weight: bold; transition: 0.3s; }
    div.stButton > button:hover { background-color: #003300; border-color: #ffffff; color: #ffffff; }
    .status-bar { padding: 10px; border-bottom: 2px solid #333; margin-bottom: 20px; font-family: monospace; font-size: 18px; }
</style>
""", unsafe_allow_html=True)

defaults = {
    'mode': 'MENU', 'scenario': None, 'lives': 3, 'progress': 0, 
    'start_time': 0, 'msg': "", 'monster_anchor': 50, 'last_update_time': 0
}
for k, v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v

# --- BEREGN ANKER (VIGTIGSTE FUNKTION) ---
def get_current_monster_pos(total_time, current_progress):
    """Finder hvor monsteret er LIGE NU, så vi kan starte næste animation derfra."""
    
    # 1. Hvor startede den sidst?
    start_x = st.session_state.monster_anchor
    
    # 2. Hvor var den på vej hen (Spillerens position FØR han rykkede)?
    target_x = 150 + (current_progress * 100)
    
    # 3. Hvor lang tid har den haft til at bevæge sig siden sidste update?
    time_spent = time.time() - st.session_state.last_update_time
    
    # 4. Hvor lang tid var der tilbage totalt da denne bevægelse startede?
    # (Total tid - tid der var gået ved sidste update)
    time_left_at_start = total_time - (st.session_state.last_update_time - st.session_state.start_time)
    
    if time_left_at_start <= 0.1: return target_x # Den er fremme
    
    # 5. Procentdel af rejsen
    pct = min(time_spent / time_left_at_start, 1.0)
    
    # 6. Nuværende position
    current_x = start_x + ((target_x - start_x) * pct)
    return current_x

if st.session_state.mode == 'MENU':
    st.title("💀 SUMVIVAL GAME")
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
            st.session_state.monster_anchor = 50
            st.rerun()

elif st.session_state.mode == 'BRIEFING':
    room = st.session_state.scenario['rooms'][0]
    st.title("📁 MISSION BRIEFING")
    graphics.render_game_scene('BRIEFING', 0, room['time_limit'], 0, 50)
    st.info(f"{room['story']}")
    st.warning(f"⚠️ Tid: {room['time_limit']} sekunder. 4 Spørgsmål.")
    
    if st.button("JEG ER KLAR - START SPIL", use_container_width=True):
        st.session_state.mode = 'PLAYING'
        now = time.time()
        st.session_state.start_time = now
        st.session_state.last_update_time = now
        st.session_state.monster_anchor = 50 
        st.rerun()

elif st.session_state.mode == 'PLAYING':
    room = st.session_state.scenario['rooms'][0]
    steps = room['steps']
    idx = st.session_state.progress
    
    elapsed = time.time() - st.session_state.start_time
    time_left = max(0, room['time_limit'] - elapsed)
    
    # Tidsstyring ved klik
    if elapsed > room['time_limit']:
        st.session_state.mode = 'DEATH'
        st.session_state.msg = "TIDEN ER UDLØBET!"
        st.rerun()

    lives_icon = "❤️" * st.session_state.lives
    st.markdown(f"""<div class="status-bar">LIV: {lives_icon} &nbsp;|&nbsp; TRIN: {idx+1}/4</div>""", unsafe_allow_html=True)

    graphics.render_game_scene('PLAYING', idx, room['time_limit'], elapsed, st.session_state.monster_anchor)
    
    if idx < len(steps):
        q = steps[idx]
        st.markdown(f"### ❓ {q['q']}")
        if st.session_state.msg: st.caption(st.session_state.msg)

        c1, c2 = st.columns(2)
        
        def answer(opt):
            # Tjek tid igen for en sikkerheds skyld
            real_elapsed = time.time() - st.session_state.start_time
            if real_elapsed > room['time_limit']:
                st.session_state.mode = 'DEATH'
                st.session_state.msg = "For sent!"
                return

            # Opdater monster anker (FØR vi ændrer progress)
            new_anchor = get_current_monster_pos(room['time_limit'], st.session_state.progress)
            st.session_state.monster_anchor = new_anchor
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
        st.success("DU NÅEDE SIKKERHED!")
        if st.button("Tilbage til Menu"):
            st.session_state.mode = 'MENU'
            st.rerun()

elif st.session_state.mode == 'DEATH':
    st.error(f"💀 {st.session_state.msg}")
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
            st.session_state.monster_anchor = 50 # RESET HELT
            st.session_state.msg = ""
        st.rerun()

st.markdown("---")
if st.button("🔧 REBOOT APP"):
    st.session_state.clear()
    st.rerun()
