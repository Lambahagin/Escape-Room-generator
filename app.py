import streamlit as st
from openai import OpenAI
import json

# --- 1. OPSÆTNING ---
st.set_page_config(page_title="Sumvival Game", page_icon="🦑")

# Hent nøglen fra det hemmelige pengeskab
if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("Mangler API nøgle i Secrets! Se Trin 2 i guiden.")
    st.stop()

# --- 2. FUNKTION: SNAK MED AI ---
def hent_ai_udfordring(fag, emne, sværhedsgrad):
    # Dette er instruksen til AI'en (Prompt Engineering)
    system_besked = f"""
    Du er 'The Front Man' fra et spil, der minder om Squid Game. Din tone er mystisk, autoritær og lidt uhyggelig.
    Du skal generere en gåde eller opgave til en elev i gymnasiet.
    
    Fag: {fag}
    Emne: {emne}
    Niveau: {sværhedsgrad}
    
    Du SKAL svare i præcist dette JSON-format (uden markdown formatering udenom):
    {{
        "historie": "En kort, spændingsfyldt situation (max 3 sætninger). F.eks. 'Vagterne peger på dig...', 'Døren smækker i...'",
        "opgave": "Selve den matematiske/fysiske opgave, der skal løses for at overleve.",
        "svar": "Kun det korrekte resultat (tal eller kort tekst)",
        "hint": "Et hjælpsomt hint, hvis de sidder fast"
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # Eller "gpt-4" for endnu klogere AI (lidt dyrere)
            messages=[
                {"role": "system", "content": system_besked},
                {"role": "user", "content": "Generer en ny udfordring nu."}
            ],
            temperature=0.7
        )
        # Vi oversætter AI'ens tekst-svar til et Python-objekt (JSON)
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"historie": "Fejl i systemet...", "opgave": f"AI kunne ikke svare: {e}", "svar": "0000", "hint": "Prøv igen"}

# --- 3. UI (BRUGERFLADE) ---
st.title("🦑 Sumvival Game Generator")
st.markdown("*Spillet er i gang. Svar rigtigt, eller bliv elimineret.*")

# Sidebar til valg
with st.sidebar:
    st.header("Konfiguration")
    valgt_fag = st.selectbox("Fag", ["Matematik", "Fysik"])
    
    if valgt_fag == "Matematik":
        valgt_emne = st.selectbox("Emne", ["Funktioner", "Differentialregning", "Vektorer", "Sandsynlighed", "Geometri"])
    else:
        valgt_emne = st.selectbox("Emne", ["Mekanik", "Energi", "El-lære", "Bølger", "Kernefysik"])
        
    niveau = st.select_slider("Sværhedsgrad", options=["Let", "Mellem", "Svær"])
    
    if st.button("Start Nyt Rum"):
        with st.spinner('Vagterne forbereder næste rum...'):
            # Kald AI funktionen
            st.session_state.current_riddle = hent_ai_udfordring(valgt_fag, valgt_emne, niveau)
            st.session_state.game_active = True
            st.session_state.solved = False

# --- 4. SPILLET ---
if 'game_active' in st.session_state and st.session_state.game_active:
    data = st.session_state.current_riddle
    
    st.markdown("---")
    st.markdown(f"### 🚪 {data['historie']}")
    
    st.info(f"**Opgave:** {data['opgave']}")
    
    user_answer = st.text_input("Indtast koden for at overleve:", key="user_answer")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Bekræft svar"):
            # Simpel tjek: Vi fjerner mellemrum og gør det til små bogstaver for at være flinke
            clean_user = user_answer.strip().lower().replace(",", ".")
            clean_correct = str(data['svar']).strip().lower().replace(",", ".")
            
            if clean_user == clean_correct:
                st.session_state.solved = True
                st.success("✅ KORREKT! Døren åbner sig.")
                st.balloons()
            else:
                st.error("❌ FORKERT! Alarmen går i gang. Prøv igen.")
                
    with col2:
        with st.expander("Jeg har brug for hjælp!"):
            st.warning(data['hint'])
            
    if st.session_state.solved:
        st.markdown("### [Klik her for at gå til næste rum](#)") 
        # Her kunne man lave logik der genererer et nyt rum automatisk

else:
    st.write("👈 Vælg indstillinger i menuen til venstre for at starte.")
