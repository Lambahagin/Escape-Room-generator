import streamlit as st
import random
import time

# --- 1. OPSÆTNING AF SIDEN ---
st.set_page_config(page_title="Edu-Escape Room", page_icon="🔐")

st.title("🎓 Edu-Escape Room Generator")
st.markdown("Velkommen til det dynamiske læringsrum. Vælg dit fag for at starte missionen.")

# --- 2. INPUT FRA BRUGEREN ---
with st.sidebar:
    st.header("Indstillinger")
    fag = st.selectbox("Vælg Fag", ["Matematik", "Fysik"])
    
    if fag == "Matematik":
        emne = st.selectbox("Emne", ["Lineære funktioner", "Andengradsligninger", "Vektorer"])
    else:
        emne = st.selectbox("Emne", ["Mekanik", "El-lære", "Termodynamik"])
        
    start_knap = st.button("Generer Nyt Escape Room")

# --- 3. LOGIK OG VARIABLER (SESSION STATE) ---
# Vi bruger session_state til at huske, hvor i spillet eleven er, selvom siden genindlæses.
if 'game_active' not in st.session_state:
    st.session_state.game_active = False
if 'current_riddle' not in st.session_state:
    st.session_state.current_riddle = {}

# --- 4. DEN "KUNSTIGE INTELLIGENS" (SIMULERET) ---
# I en rigtig løsning vil denne funktion sende en prompt til OpenAI/Gemini API.
# Her simulerer vi det for at vise princippet.
def generer_udfordring(fag, emne):
    # Simulering af AI respons baseret på emne
    historier = [
        "Du er fanget i et laboratorium, og ilten slipper op!",
        "Rumvæsner har overtaget skolen, og du skal hacke hovedcomputeren.",
        "Du er en hemmelig agent, der skal desarmere en bombe."
    ]
    
    valgt_historie = random.choice(historier)
    
    if emne == "Lineære funktioner":
        opgave_tekst = "Døren er låst med en kode. På skærmen står: f(x) = 2x + 4. Hvad er f(5)?"
        svar = "14"
        hint = "Indsæt 5 på x's plads i ligningen."
    elif emne == "Mekanik":
        opgave_tekst = "En kasse vejer 10 kg og påvirkes af en kraft på 50 N. Hvad er accelerationen (a) ifølge Newtons 2. lov (F=m*a)?"
        svar = "5"
        hint = "Isoler a i formlen F = m * a."
    else:
        # Fallback for andre emner i denne prototype
        opgave_tekst = f"Løs denne gåde inden for {emne}: Hvad er kvadratroden af 16?"
        svar = "4"
        hint = "Hvilket tal ganget med sig selv giver 16?"

    return {
        "historie": valgt_historie,
        "opgave": opgave_tekst,
        "korrekt_svar": svar,
        "hint": hint
    }

# --- 5. SPIL-LOGIK ---

if start_knap:
    with st.spinner('AI genererer dit scenarie...'):
        time.sleep(1.5) # For effekt
        st.session_state.current_riddle = generer_udfordring(fag, emne)
        st.session_state.game_active = True
        st.session_state.feedback = "" # Nulstil feedback

if st.session_state.game_active:
    riddle = st.session_state.current_riddle
    
    # Vis historien og opgaven
    st.markdown("---")
    st.subheader("📜 Scenariet")
    st.info(riddle["historie"])
    
    st.subheader("🧩 Udfordringen")
    st.write(riddle["opgave"])
    
    # Input felt til elevens svar
    bruger_svar = st.text_input("Indtast dit svar her:", key="answer_input")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Tjek Svar"):
            if bruker_svar.strip() == riddle["korrekt_svar"]:
                st.success("Korrekt! Døren åbner sig. Du klarede det! 🎉")
                st.balloons()
            else:
                st.error("Forkert kode. Prøv igen! ⛔")
    with col2:
        with st.expander("Brug for et hint?"):
            st.write(riddle["hint"])

else:
    st.info("Vælg fag og emne i menuen til venstre for at starte.")
