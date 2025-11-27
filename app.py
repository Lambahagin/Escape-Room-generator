import streamlit as st
import streamlit.components.v1 as components
import ai_manager
import game_bridge
import assets 
import random

st.set_page_config(page_title="Fagligt Escape Room", page_icon="🎓", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #000000 !important; color: white !important; }
    .success-box { border: 2px solid lime; padding: 20px; text-align: center; background: #002200; margin-top: 20px; border-radius: 10px; }
    .level-badge { font-size: 20px; font-weight: bold; color: cyan; border: 1px solid cyan; padding: 5px 15px; border-radius: 5px; display: inline-block; margin-bottom: 10px; }
    .theme-badge { font-size: 14px; color: #aaa; margin-left: 10px; font-style: italic; }
</style>
""", unsafe_allow_html=True)

if 'game_active' not in st.session_state: st.session_state.game_active = False
if 'scenario' not in st.session_state: st.session_state.scenario = None
if 'current_level' not in st.session_state: st.session_state.current_level = 1
if 'current_theme' not in st.session_state: st.session_state.current_theme = "squid"

st.sidebar.title("💀 GAMEMASTER")
st.sidebar.markdown(f"### LEVEL: {st.session_state.current_level}")

fag = st.sidebar.selectbox("Fag", ["Matematik", "Fysik"])
emne = st.sidebar.text_input("Emne", "Funktioner")

if st.sidebar.button("RESET GAME (Level 1)"):
    st.session_state.current_level = 1
    st.session_state.game_active = False
    st.rerun()

st.title("🎓 Fagligt Escape Room")

if not st.session_state.game_active:
    st.info(f"Klar til Niveau {st.session_state.current_level}. Game Masteren vælger et univers...")
    
    if st.button("START NY VERDEN", type="primary"):
        with st.spinner("Rejser gennem multiverset..."):
            new_theme = random.choice(assets.AVAILABLE_THEMES)
            st.session_state.current_theme = new_theme
            st.session_state.scenario = ai_manager.generate_scenario(fag, emne, new_theme)
            st.session_state.game_active = True
            st.rerun()

else:
    theme_name = st.session_state.current_theme.upper()
    st.markdown(f"""
        <div class='level-badge'>NIVEAU {st.session_state.current_level}</div>
        <span class='theme-badge'>VERDEN: {theme_name}</span>
    """, unsafe_allow_html=True)
    
    # KORREKT KALD TIL RENDER_GAME
    game_html = game_bridge.render_game(st.session_state.scenario, theme=st.session_state.current_theme)
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
                st.success("KORREKT! Portalen åbner sig...")
                import time
                time.sleep(2)
                st.rerun()
            else:
                st.error("FORKERT KODE.")
