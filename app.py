import streamlit as st
import streamlit.components.v1 as components
import ai_manager
import game_engine

st.set_page_config(page_title="Sumvival Game", page_icon="💀", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #000000 !important; color: white !important; }
    .success-box { border: 2px solid lime; padding: 20px; text-align: center; background: #001100; }
    .level-badge { font-size: 20px; font-weight: bold; color: cyan; border: 1px solid cyan; padding: 5px 15px; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# STATE
if 'game_active' not in st.session_state:
    st.session_state.game_active = False
if 'scenario' not in st.session_state:
    st.session_state.scenario = None
if 'current_level' not in st.session_state:
    st.session_state.current_level = 1

# --- SIDEBAR ---
st.sidebar.title("💀 MENU")
st.sidebar.markdown(f"### NUVÆRENDE LEVEL: {st.session_state.current_level}")

fag = st.sidebar.selectbox("Fag", ["Matematik", "Fysik"])
emne = st.sidebar.text_input("Emne", "Funktioner")

if st.sidebar.button("GENERER NYT SPIL (Reset Level)"):
    st.session_state.current_level = 1
    st.session_state.game_active = False
    st.rerun()

# --- HOVEDSKÆRM ---
st.title("🦑 SUMVIVAL GAME")

# Hvis intet spil er aktivt, vis start-knap
if not st.session_state.game_active:
    st.info(f"Klar til Niveau {st.session_state.current_level}. Tryk på knappen for at starte.")
    
    if st.button("START NÆSTE RUM", type="primary"):
        with st.spinner(f"Dungeon Master genererer Niveau {st.session_state.current_level}..."):
            # Vi sender niveauet med til AI'en (kan bruges til at gøre det sværere)
            # Du kan udvide ai_manager til at bruge dette tal
            st.session_state.scenario = ai_manager.generate_scenario(fag, emne)
            st.session_state.game_active = True
            st.rerun()

else:
    # VIS NIVAU
    st.markdown(f"<div class='level-badge'>NIVEAU {st.session_state.current_level}</div>", unsafe_allow_html=True)
    
    # VIS SPILLET
    game_html = game_engine.render_js_game(st.session_state.scenario)
    components.html(game_html, height=500)
    
    st.markdown("---")
    
    # LEVEL UP LOGIK
    st.write("Når du har vundet, får du en kode. Indtast den her for at komme videre:")
    
    c1, c2 = st.columns([3, 1])
    code = c1.text_input("Sikkerhedskode", placeholder="Indtast koden fra spillet")
    
    if c2.button("LÅS OP"):
        if code.upper().strip() == "LEVEL-UP":
            st.balloons()
            st.session_state.current_level += 1
            st.session_state.game_active = False # Sluk spillet for at gøre klar til næste
            st.success("KORREKT! Gør dig klar til næste rum...")
            # Lille pause så man når at se ballonerne
            st.rerun()
        else:
            st.error("Forkert kode.")
