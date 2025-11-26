import streamlit as st
from openai import OpenAI
import json
import time

# --- 1. KONFIGURATION OG STATE ---
st.set_page_config(page_title="Sumvival Game v2", page_icon="🦑")

# CSS for at skjule standard Streamlit elementer og gøre det mere spil-agtigt
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        height: 3em;
        font-size: 20px;
        font-weight: bold;
    }
    .life-container {
        font-size: 30px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session states
if 'game_state' not in st.session_state:
    st.session_state.update({
        'game_state': 'SETUP',  # SETUP, BRIDGE, VAULT, WIN, LOSE
        'lives': 3,
        'current_challenge': {},
        'bridge_step': 0
    })

# Hent API nøgle
if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("Mangler API nøgle i Secrets!")
    st.stop()

# --- 2. AI MOTOR (PROMPT ENGINEERING) ---
def get_ai_content(game_type, fag, emne):
    # Vi beder AI om at være en Game Master og levere JSON
    if game_type == "BRIDGE":
        system_prompt = f"""
        Du er gamemaster i et dødeligt spil. Generer 3 trins opgaver inden for {fag} ({emne}).
        Hvert trin skal have et spørgsmål og to svarmuligheder (en rigtig, en forkert).
        Output SKAL være ren JSON i dette format:
        {{
            "story": "Kort intro (f.eks. 'Foran dig er en glasbro med to paneler... du skal vælge det rigtige svar for ikke at falde.')",
            "steps": [
                {{"q": "Spørgsmål 1", "options": ["Rigtigt Svar", "Forkert Svar"], "correct": "Rigtigt Svar"}},
                {{"q": "Spørgsmål 2", "options": ["Rigtigt Svar", "Forkert Svar"], "correct": "Rigtigt Svar"}},
                {{"q": "Spørgsmål 3", "options": ["Rigtigt Svar", "Forkert Svar"], "correct": "Rigtigt Svar"}}
            ]
        }}
        Bland rækkefølgen af 'options' tilfældigt i dit svar.
        """
    
    elif game_type == "VAULT":
        system_prompt = f"""
        Du er gamemaster. Spilleren skal finde en 4-cifret kode til en dør.
        Generer 4 korte matematiske/fysiske gåder inden for {fag} ({emne}).
        Hver gåde SKAL resultere i et enkeltcifret heltal (0-9).
        Output SKAL være ren JSON:
        {{
            "story": "Kort intro (f.eks. 'Døren er låst. På væggen ser du 4 ligninger...')",
            "tasks": [
                {{"desc": "Beskrivelse af delopgave 1 (f.eks. 'Find x når 2x=10')", "res": "5"}},
                {{"desc": "Beskrivelse af delopgave 2", "res": "tal"}},
                {{"desc": "Beskrivelse af delopgave 3", "res": "tal"}},
                {{"desc": "Beskrivelse af delopgave 4", "res": "tal"}}
            ]
        }}
        """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": system_prompt}],
            temperature=0.7,
            response_format={"type": "json_object"} # Sikrer valid JSON (kræver nyere modeller)
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"AI Fejl: {e}")
        return None

# --- 3. SPIL LOGIK FUNKTIONER ---
def reset_game():
    st.session_state.game_state = 'SETUP'
    st.session_state.lives = 3
    st.session_state.bridge_step = 0

def damage_player():
    st.session_state.lives -= 1
    if st.session_state.lives <= 0:
        st.session_state.game_state = 'LOSE'
    else:
        st.toast("❌ FORKERT! Du mistede et liv!", icon="💥")

# --- 4. GUI: SETUP SKÆRM ---
if st.session_state.game_state == 'SETUP':
    st.title("🦑 Sumvival Game")
    st.markdown("Velkommen, spiller 456. Vælg din udfordring.")
    
    col1, col2 = st.columns(2)
    with col1:
        fag = st.selectbox("Fag", ["Matematik", "Fysik"])
    with col2:
        emne = st.text_input("Emne (f.eks. Funktioner, Mekanik)", "Lineære funktioner")
    
    st.markdown("### Vælg Spiltype:")
    c1, c2 = st.columns(2)
    
    # Knap til Glasbroen
    if c1.button("🌉 Glasbroen (Multiple Choice)"):
        with st.spinner("Bygger broen..."):
            data = get_ai_content("BRIDGE", fag, emne)
            if data:
                st.session_state.current_challenge = data
                st.session_state.game_state = 'BRIDGE'
                st.session_state.bridge_step = 0
                st.rerun()

    # Knap til Boksen
    if c2.button("🔐 Boksen (Kodelås)"):
        with st.spinner("Låser døren..."):
            data = get_ai_content("VAULT", fag, emne)
            if data:
                st.session_state.current_challenge = data
                st.session_state.game_state = 'VAULT'
                st.rerun()

# --- GUI: VIS LIV ---
if st.session_state.game_state not in ['SETUP', 'LOSE', 'WIN']:
    lives_html = "❤️" * st.session_state.lives + "🖤" * (3 - st.session_state.lives)
    st.markdown(f"<div class='life-container'>{lives_html}</div>", unsafe_allow_html=True)
    st.progress(st.session_state.lives / 3)

# --- 5. GUI: GLASBROEN (GAME A) ---
if st.session_state.game_state == 'BRIDGE':
    data = st.session_state.current_challenge
    step_idx = st.session_state.bridge_step
    
    st.subheader(f"Trin {step_idx + 1} af 3")
    st.info(data['story'])
    
    current_q = data['steps'][step_idx]
    st.markdown(f"### {current_q['q']}")
    
    # Vis to knapper
    b1, b2 = st.columns(2)
    opt1 = current_q['options'][0]
    opt2 = current_q['options'][1]
    
    # Håndter klik
    if b1.button(opt1):
        if opt1 == current_q['correct']:
            st.success("Korrekt! Du landede sikkert.")
            time.sleep(1)
            if step_idx + 1 >= len(data['steps']):
                st.session_state.game_state = 'WIN'
            else:
                st.session_state.bridge_step += 1
            st.rerun()
        else:
            damage_player()
            st.rerun()
            
    if b2.button(opt2):
        if opt2 == current_q['correct']:
            st.success("Korrekt! Du landede sikkert.")
            time.sleep(1)
            if step_idx + 1 >= len(data['steps']):
                st.session_state.game_state = 'WIN'
            else:
                st.session_state.bridge_step += 1
            st.rerun()
        else:
            damage_player()
            st.rerun()

# --- 6. GUI: BOKSEN (GAME B) ---
if st.session_state.game_state == 'VAULT':
    data = st.session_state.current_challenge
    
    st.info(data['story'])
    
    st.markdown("### Løs de 4 delopgaver for at finde koden:")
    
    # Vis opgaverne
    cols = st.columns(4)
    for i, task in enumerate(data['tasks']):
        with cols[i]:
            st.markdown(f"**Ciffer {i+1}:**")
            st.caption(task['desc'])
            st.markdown("---")
            
    # Input felt
    code_input = st.text_input("Indtast 4-cifret kode:", max_chars=4)
    
    if st.button("Lås op"):
        # Byg det korrekte svar fra data
        correct_code = "".join([t['res'] for t in data['tasks']])
        
        if code_input == correct_code:
            st.session_state.game_state = 'WIN'
            st.rerun()
        else:
            damage_player()
            st.error("Koden er forkert! Alarmen lyder.")

# --- 7. GUI: SLUT SKÆRME ---
if st.session_state.game_state == 'WIN':
    st.balloons()
    st.header("🏆 DU OVERLEVEDE!")
    st.success("Du har gennemført udfordringen og er klar til næste niveau.")
    if st.button("Spil igen"):
        reset_game()
        st.rerun()

if st.session_state.game_state == 'LOSE':
    st.header("💀 ELIMINERET")
    st.error("Du løb tør for liv. Vagterne fører dig bort...")
    if st.button("Prøv igen"):
        reset_game()
        st.rerun()
