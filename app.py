import streamlit as st
import streamlit.components.v1 as components
import ai_manager
import game_engine

st.set_page_config(page_title="Sumvival Game", page_icon="💀", layout="centered")

# CSS
st.markdown("""
<style>
    .stApp { background-color: #000000 !important; color: white !important; }
    .success-box { border: 2px solid lime; padding: 20px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# STATE
if 'game_active' not in st.session_state:
    st.session_state.game_active = False
if 'scenario' not in st.session_state:
    st.session_state.scenario = None

# --- SIDEBAR / MENU ---
st.sidebar.title("💀 MENU")
fag = st.sidebar.selectbox("Fag", ["Matematik", "Fysik"])
emne = st.sidebar.text_input("Emne", "Funktioner")

if st.sidebar.button("GENERER NYT SPIL"):
    with st.spinner("AI bygger banen..."):
        st.session_state.scenario = ai_manager.generate_scenario(fag, emne)
        st.session_state.game_active = True
        st.rerun()

# --- HOVEDSKÆRM ---
st.title("🦑 SUMVIVAL GAME")

if not st.session_state.game_active:
    st.info("👈 Brug menuen til venstre for at starte et nyt spil.")
    st.markdown("---")
    st.write("Dette spil kører direkte i din browser for maksimal hastighed.")

else:
    # 1. VIS SPILLET (HTML/JS)
    # Vi henter HTML-koden fra game_engine og viser den
    game_html = game_engine.render_js_game(st.session_state.scenario)
    
    # Vi bruger en iframe med fast højde
    components.html(game_html, height=500)
    
    st.markdown("---")
    
    # 2. VERIFICER SEJR
    st.markdown("### 🔒 SIKKERHEDSSLUSE")
    st.write("Når du har gennemført banen, får du en kode. Indtast den her:")
    
    code = st.text_input("Indtast kode:", max_chars=10)
    
    if st.button("LÅS OP FOR NÆSTE RUM"):
        if code.upper().strip() == "SEJR-456":
            st.balloons()
            st.markdown("""
            <div class="success-box">
                <h1>🏆 KORREKT!</h1>
                <p>Du har overlevet dette rum. Du er nu klar til næste udfordring.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("❌ FORKERT KODE! Du må klare spillet først.")
