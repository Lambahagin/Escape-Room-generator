import streamlit as st
import streamlit.components.v1 as components
import ai_manager
import game_engine

st.set_page_config(page_title="Sumvival Game", page_icon="💀", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #000000 !important; color: white !important; }
    .success-box { border: 2px solid lime; padding: 20px; text-align: center; background: #002200; margin-top: 20px; }
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

# --- MENU ---
st.sidebar.title("💀 MENU")
st.sidebar.markdown(f"### NUVÆRENDE LEVEL: {st.session_state.current_level}")

fag = st.sidebar.selectbox("Fag", ["Matematik", "Fysik"])
emne = st.sidebar.text_input("Emne", "Funktioner")

if st.sidebar.button("GENERER NYT SPIL (Genstart Level 1)"):
    st.session_state.current_level = 1
    st.session_state.game_active = False
    st.rerun()

# --- HOVEDSKÆRM ---
st.title("🦑 SUMVIVAL GAME")

if not st.session_state.game_active:
    st.info(f"Klar til Niveau {st.session_state.current_level}. Tryk på knappen for at starte.")
    
    if st.button("START NÆSTE RUM", type="primary"):
        with st.spinner(f"Dungeon Master genererer Niveau {st.session_state.current_level}..."):
            st.session_state.scenario = ai_manager.generate_scenario(fag, emne)
            st.session_state.game_active = True
            st.rerun()

else:
    st.markdown(f"<div class='level-badge'>NIVEAU {st.session_state.current_level}</div>", unsafe_allow_html=True)
    
    # Vis Spillet
    game_html = game_engine.render_js_game(st.session_state.scenario)
    components.html(game_html, height=500)
    
    st.markdown("---")
    st.markdown("### 🔒 SIKKERHEDSSLUSE")
    
    # Brug en form for at gøre det nemmere at trykke enter
    with st.form("code_form"):
        col1, col2 = st.columns([3, 1])
        code_input = col1.text_input("Indtast kode fra spillet:", placeholder="LEVEL-UP")
        submitted = col2.form_submit_button("LÅS OP")
        
        if submitted:
            # Rens input for mellemrum og gør det til store bogstaver
            clean_code = code_input.strip().upper()
            
            if clean_code == "LEVEL-UP":
                st.session_state.current_level += 1
                st.session_state.game_active = False # Sluk spillet
                st.balloons()
                st.success("KODE ACCEPTERET! Gør dig klar til næste niveau...")
                # Vi laver en lille pause før rerun, så success beskeden ses
                import time
                time.sleep(2)
                st.rerun()
            else:
                st.error(f"❌ FORKERT KODE: '{clean_code}'. Prøv igen.")
