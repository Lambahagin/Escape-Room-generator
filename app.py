import streamlit as st
import streamlit.components.v1 as components
import ai_manager
import game_engine

# --- 1. OPSÆTNING ---
st.set_page_config(page_title="Sumvival Game", page_icon="💀", layout="centered")

st.markdown("""
<style>
    /* Globalt Sort Tema */
    .stApp { background-color: #000000 !important; color: white !important; }
    
    /* Success Boks */
    .success-box { 
        border: 2px solid lime; 
        padding: 20px; 
        text-align: center; 
        background: #002200; 
        margin-top: 20px; 
        border-radius: 10px;
    }
    
    /* Level Badge */
    .level-badge { 
        font-size: 20px; 
        font-weight: bold; 
        color: cyan; 
        border: 1px solid cyan; 
        padding: 5px 15px; 
        border-radius: 5px; 
        display: inline-block;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. STATE (Hukommelse) ---
if 'game_active' not in st.session_state:
    st.session_state.game_active = False
if 'scenario' not in st.session_state:
    st.session_state.scenario = None
if 'current_level' not in st.session_state:
    st.session_state.current_level = 1

# --- 3. MENU (Sidebar) ---
st.sidebar.title("💀 MENU")
st.sidebar.markdown(f"### NUVÆRENDE LEVEL: {st.session_state.current_level}")

fag = st.sidebar.selectbox("Fag", ["Matematik", "Fysik"])
emne = st.sidebar.text_input("Emne", "Funktioner")

if st.sidebar.button("GENERER NYT SPIL (Genstart Level 1)"):
    # Nulstil alt
    st.session_state.current_level = 1
    st.session_state.game_active = False
    st.rerun()

# --- 4. HOVEDSKÆRM ---
st.title("🦑 SUMVIVAL GAME")

# A) Startskærm (Før spil)
if not st.session_state.game_active:
    st.info(f"Klar til Niveau {st.session_state.current_level}. Tryk på knappen for at starte.")
    
    if st.button("START NÆSTE RUM", type="primary"):
        with st.spinner(f"Dungeon Master genererer Niveau {st.session_state.current_level}..."):
            # Hent data fra AI
            st.session_state.scenario = ai_manager.generate_scenario(fag, emne)
            st.session_state.game_active = True
            st.rerun()

# B) Spilskærm (Mens spillet kører)
else:
    # Vis hvilket level vi er på
    st.markdown(f"<div class='level-badge'>NIVEAU {st.session_state.current_level}</div>", unsafe_allow_html=True)
    
    # VIS SPILLET (HTML/JS Containeren)
    # Dette er "den sorte boks" hvor alt spillet foregår
    game_html = game_engine.render_js_game(st.session_state.scenario)
    components.html(game_html, height=500)
    
    st.markdown("---")
    st.markdown("### 🔒 SIKKERHEDSSLUSE")
    
    # Formular til koden
    with st.form("code_form"):
        col1, col2 = st.columns([3, 1])
        code_input = col1.text_input("Indtast kode fra spillet:", placeholder="LEVEL-UP")
        submitted = col2.form_submit_button("LÅS OP")
        
        if submitted:
            clean_code = code_input.strip().upper()
            
            if clean_code == "LEVEL-UP":
                # Succes! Gå videre til næste level
                st.session_state.current_level += 1
                st.session_state.game_active = False # Gå tilbage til startskærm (klar til nyt rum)
                
                st.balloons()
                st.success("KODE ACCEPTERET! Gør dig klar til næste niveau...")
                
                # Lille pause så man når at se beskeden
                import time
                time.sleep(2)
                st.rerun()
            else:
                st.error(f"❌ FORKERT KODE: '{clean_code}'. Du skal klare spillet for at få koden.")
