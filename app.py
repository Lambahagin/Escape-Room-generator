import streamlit as st
import streamlit.components.v1 as components
import ai_manager
import game_bridge # HUSK AT IMPORTERE DET NYE MODUL

st.set_page_config(page_title="Sumvival Game", page_icon="💀", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #000000 !important; color: white !important; }
    .success-box { border: 2px solid lime; padding: 20px; text-align: center; background: #002200; margin-top: 20px; }
    .level-badge { font-size: 20px; font-weight: bold; color: cyan; border: 1px solid cyan; padding: 5px 15px; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

if 'game_active' not in st.session_state: st.session_state.game_active = False
if 'scenario' not in st.session_state: st.session_state.scenario = None
if 'current_level' not in st.session_state: st.session_state.current_level = 1

# --- MENU ---
st.sidebar.title("💀 GAMEMASTER")
st.sidebar.markdown(f"### LEVEL: {st.session_state.current_level}")

fag = st.sidebar.selectbox("Fag", ["Matematik", "Fysik"])
emne = st.sidebar.text_input("Emne", "Funktioner")
tema = st.sidebar.selectbox("Tema", ["squid", "wonderland"]) # NY TEMA VÆLGER

if st.sidebar.button("RESET GAME"):
    st.session_state.current_level = 1
    st.session_state.game_active = False
    st.rerun()

# --- MAIN ---
st.title("🦑 SUMVIVAL GAME")

if not st.session_state.game_active:
    st.info(f"Klar til Niveau {st.session_state.current_level}. Vælg tema og start.")
    
    if st.button("START LEVEL", type="primary"):
        with st.spinner("Genererer bane..."):
            st.session_state.scenario = ai_manager.generate_scenario(fag, emne, tema)
            st.session_state.game_active = True
            st.rerun()

else:
    st.markdown(f"<div class='level-badge'>NIVEAU {st.session_state.current_level}</div>", unsafe_allow_html=True)
    
    # HER ER ÆNDRINGEN:
    # Vi sender det valgte tema med til game_bridge
    game_html = game_bridge.render(st.session_state.scenario, theme=tema)
    components.html(game_html, height=500)
    
    st.markdown("---")
    st.markdown("### 🔒 SIKKERHEDSSLUSE")
    
    with st.form("code_form"):
        col1, col2 = st.columns([3, 1])
        code_input = col1.text_input("Kode:", placeholder="LEVEL-UP")
        submitted = col2.form_submit_button("LÅS OP")
        
        if submitted:
            if code_input.strip().upper() == "LEVEL-UP":
                st.session_state.current_level += 1
                st.session_state.game_active = False
                st.balloons()
                st.success("KORREKT!")
                import time
                time.sleep(2)
                st.rerun()
            else:
                st.error("FORKERT KODE.")
