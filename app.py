import streamlit as st
import time
import ai_manager
import graphics

st.set_page_config(page_title="Sumvival Game", page_icon="💀", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #000000 !important; color: #ffffff !important; }
    p, h1, h2, h3, li, .stMarkdown, .stCaption { color: #ffffff !important; }
    div.stButton > button {
        width: 100%; height: 60px; background-color: #111111;
        color: #00ff00; border: 2px solid #00ff00;
        font-size: 20px; font-weight: bold; transition: 0.3s;
    }
    div.stButton > button:hover { background-color: #003300; border-color: #ffffff; color: #ffffff; }
    .status-bar { padding: 10px; border-bottom: 2px solid #333; margin-bottom: 20px; font-family: monospace; font-size: 18px; }
</style>
""", unsafe_allow_html=True)

# STATE
defaults = {
    'mode': 'MENU', 'scenario': None, 'lives': 3, 'progress': 0, 
    'start_time': 0, 'msg': "", 'monster_anchor': 0,
    'last_update_time': 0 # Hvornår opdaterede vi sidst ankeret?
}
for k, v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v

# --- FUNKTION TIL AT OPDATERE MONSTER ---
def update_monster_position():
    """
    Beregner hvor monsteret er LIGE NU, før vi ændrer spillerens position.
    Dette forhindrer monsteret i at hoppe.
    """
    # 1. Find nuværende mål (hvor monsteret var på vej hen før klik)
    current_player_x = 150 + (st.session_state.progress * 100)
    
    # 2. Hvor startede monsteret sidst?
    start_x = st.session_state.monster_anchor
    
    # 3. Hvor meget tid havde vi til den tur?
    # Vi gemmer start-tidspunktet for HVERT skridt
    time_spent_on_this_step = time.time() - st.session_state.last_update_time
    
    # 4. Hvor meget tid er der tilbage totalt?
    total_time_left = 20 - (time.time() - st.session_state.start_time)
    
    # Hvis tiden er gået, er monsteret ved spilleren
    if total_time_left <= 0:
        return current_player_x
        
    # Monsteret bevæger sig lineært mod spilleren over resterende tid.
    # MEN SVG animationen er "dumb". Den starter ved anchor og kører til player over rest-tid.
    # Så vi skal bare finde ud af hvor "SVG-stregen" er nået til.
    
    # Total distance den skulle dække i dette step
    total_dist = current_player_x - start_x
    
    # Tid den havde til rådighed (Total tid minus tiden der var gået da steppet startede)
    # Dette er lidt tricky. Lad os gøre det simplere:
    # Monsteret når ALTID frem ved T=20.
    # Så procentdel af rejsen = (Tid brugt nu) / (Total tid - Tid ved start af step)
    # NEJ, endnu simplere: Monsteret er ved 0 ved T=0. Monster er ved Player ved T=20.
    # MEN Player flytter sig.
    
    # Den mest præcise metode til at undgå hop:
    # Monsterets position = StartAnchor + (Distance * (TidBrugt / TidTilRådighed))
    
    # Tid der var tilbage da vi startede dette step:
    time_left_at_step_start = 20 - (st.session_state.last_update_time - st.session_state.start_time)
    
    if time_left_at_step_start <= 0: 
        pct = 1.0
    else:
        pct = time_spent_on_this_step / time_left_at_step_start
        
    pct = min(pct, 1.0)
    
    new_anchor = start_x + (total_dist * pct)
    return new_anchor

# --- MENU ---
if st.session_state.mode == 'MENU':
    st.title("💀 SUMVIVAL GAME")
    c1, c2 = st.columns(2)
    fag = c1.selectbox("Fag", ["Matematik", "Fysik"])
    emne = c2.text_input("Emne", "Funktioner")
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("HENT MISSION", use_container_width=True):
        with st.spinner("Indlæser..."):
            scenarie = ai_manager.generate_scenario(fag, emne)
            st.session_state.scenario = scenarie
            st.session_state.mode = 'BRIEFING'
            st.session_state.progress = 0
            st.session_state.lives = 3
            st.session_state.msg = ""
            st.session_state.monster_anchor = 0
            st.rerun()

# --- BRIEFING ---
elif st.session_state.mode == 'BRIEFING':
    room = st.session_state.scenario['rooms'][0]
    st.title("MISSION BRIEFING")
    graphics.render_game_scene('BRIEFING', 0, 20, 0, 0)
    st.info(f"{room['story']}")
    st.warning("⚠️ 20 sekunder til at overleve.")
    
    if st.button("START SPIL", use_container_width=True):
        st.session_state.mode = 'PLAYING'
        st.session_state.start_time = time.time()
        st.session_state.last_update_time = time.time() # Vigtigt for hop-fix
        st.session_state.monster_anchor = 0
        st.rerun()

# --- PLAYING ---
elif st.session_state.mode == 'PLAYING':
    # AUTO-UPDATE LOOP (Får spillet til at tjekke tid selvom du ikke klikker)
    time.sleep(1) 
    st.rerun()
    
    room = st.session_state.scenario['rooms'][0]
    steps = room['steps']
    idx = st.session_state.progress
    
    elapsed = time.time() - st.session_state.start_time
    time_left = max(0, 20 - elapsed)
    
    # TJEK DØD (TID)
    if time_left <= 0:
        st.session_state.mode = 'DEATH'
        st.session_state.msg = "TIDEN ER UDLØBET!"
        st.rerun()

    lives_icon = "❤️" * st.session_state.lives
    st.markdown(f"""<div class="status-bar">LIV: {lives_icon} &nbsp;|&nbsp; TID: {int(time_left)}s</div>""", unsafe_allow_html=True)

    # Grafik
    graphics.render_game_scene('PLAYING', idx, 20, elapsed, st.session_state.monster_anchor)
    
    if idx < len(steps):
        q = steps[idx]
        st.markdown(f"### ❓ {q['q']}")
        
        c1, c2 = st.columns(2)
        
        def answer(opt):
            # 1. Beregn hvor monsteret er LIGE NU og gem det
            new_anchor = update_monster_position()
            st.session_state.monster_anchor = new_anchor
            st.session_state.last_update_time = time.time() # Nulstil step-tid
            
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

# --- DEATH ---
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
            st.session_state.start_time = time.time()
            st.session_state.last_update_time = time.time()
            st.session_state.monster_anchor = 0 # Nulstil monster helt
            st.session_state.msg = ""
        st.rerun()
