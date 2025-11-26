import streamlit as st
from openai import OpenAI
import json
import time

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Sumvival Game: Campaign", page_icon="💀", layout="wide")

# CSS til animationer og spil-look
st.markdown("""
<style>
    /* Generel stil */
    .main { background-color: #0e1117; color: #ffffff; }
    
    /* Glasbro Knapper */
    .glass-btn {
        width: 100%; height: 100px; font-size: 24px; font-weight: bold;
        background: rgba(255, 255, 255, 0.1); border: 2px solid cyan; color: cyan;
        border-radius: 10px; cursor: pointer; transition: 0.3s;
    }
    .glass-btn:hover { background: rgba(0, 255, 255, 0.3); box-shadow: 0 0 20px cyan; }
    
    /* Trussel Bar (Tiden) */
    .threat-container { width: 100%; background-color: #333; border-radius: 5px; margin-bottom: 20px; }
    .threat-bar {
        height: 20px; background-color: #ff0044; border-radius: 5px;
        transition: width 1s linear;
    }
    
    /* Intro tekst */
    .story-text { font-size: 18px; font-family: 'Courier New', monospace; line-height: 1.5; }
</style>
""", unsafe_allow_html=True)

# API Nøgle Check
if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("Mangler API nøgle i Secrets!")
    st.stop()

# --- 2. STATE MANAGEMENT ---
if 'campaign_state' not in st.session_state:
    st.session_state.update({
        'mode': 'MENU',          # MENU, BRIEFING, PLAYING, GAMEOVER, VICTORY
        'scenario': [],          # Listen af rum fra AI
        'current_room_idx': 0,   # Hvilket rum er vi i?
        'lives': 3,
        'bridge_progress': 0,    # Hvor langt er vi på broen?
        'start_time': 0,         # Hvornår startede opgaven?
        'last_msg': ""           # Feedback til spilleren
    })

# --- 3. AI DUNGEON MASTER ---
def generate_scenario(fag, emne):
    system_prompt = f"""
    Du er Game Master for et dødeligt spil (Squid Game stil). 
    Generer et sammenhængende scenarie med 2 rum baseret på {fag} ({emne}).
    
    Output SKAL være JSON i dette format:
    {{
        "title": "Titlen på scenariet",
        "intro": "Den overordnede historie",
        "rooms": [
            {{
                "type": "BRIDGE",
                "story": "Beskrivelse af rummet. F.eks: 'Du står foran en dyb kløft...'",
                "time_limit": 45,
                "steps": [
                    {{"q": "Opgave 1", "options": ["Rigtig", "Forkert"], "correct": "Rigtig"}},
                    {{"q": "Opgave 2", "options": ["Rigtig", "Forkert"], "correct": "Rigtig"}},
                    {{"q": "Opgave 3", "options": ["Rigtig", "Forkert"], "correct": "Rigtig"}}
                ]
            }},
            {{
                "type": "VAULT",
                "story": "Beskrivelse af rummet. F.eks: 'En låst dør blokerer vejen...'",
                "time_limit": 300,
                "tasks": [
                    {{"desc": "Delopgave 1", "res": "5"}},
                    {{"desc": "Delopgave 2", "res": "2"}},
                    {{"desc": "Delopgave 3", "res": "9"}},
                    {{"desc": "Delopgave 4", "res": "1"}}
                ]
            }}
        ]
    }}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": system_prompt}],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"AI fejl: {e}")
        return None

# --- 4. GRAFIK FUNKTIONER ---
def draw_bridge_scene(progress, total_steps, time_left_pct):
    # Dette tegner en SVG scene med en bro og en "skygge"
    # time_left_pct (0 til 1) styrer hvor tæt skyggen er
    shadow_opacity = 1.0 - time_left_pct
    
    svg_code = f"""
    <svg width="100%" height="200" style="background: #222; border-radius: 10px;">
        <line x1="10%" y1="200" x2="40%" y2="50" stroke="cyan" stroke-width="2" />
        <line x1="90%" y1="200" x2="60%" y2="50" stroke="cyan" stroke-width="2" />
        
        <rect x="40%" y="50" width="20%" height="10" fill="#aaf" opacity="0.5" />
        <rect x="30%" y="100" width="40%" height="20" fill="#aaf" opacity="0.3" />
        <rect x="20%" y="150" width="60%" height="30" fill="#aaf" opacity="0.1" />
        
        <circle cx="{50}%" cy="{180 - (progress * 40)}" r="10" fill="lime" stroke="white" stroke-width="2" />
        
        <path d="M 0 200 L 50 50 L 100 200 Z" fill="black" opacity="{shadow_opacity * 0.9}" />
        <text x="50%" y="30" fill="red" font-size="20" text-anchor="middle" font-family="monospace">
            ⚠️ VAGTEN KOMMER ⚠️
        </text>
    </svg>
    """
    st.markdown(svg_code, unsafe_allow_html=True)

# --- 5. SPIL LOGIK ---
def check_time():
    room = st.session_state.scenario['rooms'][st.session_state.current_room_idx]
    elapsed = time.time() - st.session_state.start_time
    remaining = room['time_limit'] - elapsed
    return max(0, remaining)

def handle_damage(reset_level=False):
    st.session_state.lives -= 1
    st.toast("💥 AV! Du mistede et liv!", icon="❤️")
    if st.session_state.lives <= 0:
        st.session_state.mode = 'GAMEOVER'
    elif reset_level:
        st.session_state.bridge_progress = 0
        st.session_state.start_time = time.time() # Genstart tid ved fald
        st.session_state.last_msg = "Du faldt igennem! Prøv igen fra starten af broen."

# --- 6. HOVEDPROGRAM ---

# VIS LIV (Altid synlig)
if st.session_state.mode != 'MENU':
    st.markdown(f"### ❤️ Liv: {' '.join(['💖']*st.session_state.lives)}")

# --- MENU ---
if st.session_state.mode == 'MENU':
    st.title("🦑 Sumvival Game: The Campaign")
    st.markdown("Vælg dine fag for at generere en unik historie.")
    
    c1, c2 = st.columns(2)
    fag = c1.selectbox("Fag", ["Matematik", "Fysik"])
    emne = c2.text_input("Emne", "Funktioner")
    
    if st.button("START NY HISTORIE", type="primary"):
        with st.spinner("AI'en udtænker fælderne..."):
            scenario = generate_scenario(fag, emne)
            if scenario:
                st.session_state.scenario = scenario
                st.session_state.mode = 'BRIEFING'
                st.session_state.current_room_idx = 0
                st.session_state.lives = 3
                st.session_state.last_msg = ""
                st.rerun()

# --- BRIEFING SCREEN ---
elif st.session_state.mode == 'BRIEFING':
    room_idx = st.session_state.current_room_idx
    if room_idx >= len(st.session_state.scenario['rooms']):
        st.session_state.mode = 'VICTORY'
        st.rerun()
    
    room = st.session_state.scenario['rooms'][room_idx]
    
    st.header(f"Rum {room_idx + 1}: {room['type']}")
    st.info(room['story'])
    
    st.markdown(f"**⏱️ Tidsgrænse:** {room['time_limit']} sekunder")
    st.warning("Når du trykker start, begynder nedtællingen. Vær klar.")
    
    if st.button("JEG ER KLAR - START RUMMET"):
        st.session_state.mode = 'PLAYING'
        st.session_state.start_time = time.time()
        st.session_state.bridge_progress = 0
        st.rerun()

# --- PLAYING STATE ---
elif st.session_state.mode == 'PLAYING':
    room = st.session_state.scenario['rooms'][st.session_state.current_room_idx]
    time_left = check_time()
    time_pct = time_left / room['time_limit']
    
    # Tidsstraf
    if time_left <= 0:
        handle_damage(reset_level=True)
        st.error("TIDEN ER UDLØBET! Vagten fangede dig.")
        if st.session_state.mode != 'GAMEOVER':
            # Genstart tiden hvis man har flere liv
            st.session_state.start_time = time.time() 
            st.rerun()

    # Visuel Tidsbar (HTML/CSS)
    st.markdown(f"""
    <div class="threat-container">
        <div class="threat-bar" style="width: {time_pct*100}%;"></div>
    </div>
    <p style="text-align:right">Tid tilbage: {int(time_left)}s</p>
    """, unsafe_allow_html=True)

    if st.session_state.last_msg:
        st.warning(st.session_state.last_msg)

    # --- SPILTYPE: GLASBROEN ---
    if room['type'] == 'BRIDGE':
        step = st.session_state.bridge_progress
        
        # Visuel Scene
        draw_bridge_scene(step, len(room['steps']), time_pct)
        
        current_step = room['steps'][step]
        st.markdown(f"### {current_step['q']}")
        
        c1, c2 = st.columns(2)
        opt1, opt2 = current_step['options'][0], current_step['options'][1]
        
        # Knapper
        if c1.button(opt1, use_container_width=True):
            if opt1 == current_step['correct']:
                st.session_state.bridge_progress += 1
                st.session_state.last_msg = "Korrekt! Du rykkede frem."
            else:
                handle_damage(reset_level=True)
            st.rerun()
            
        if c2.button(opt2, use_container_width=True):
            if opt2 == current_step['correct']:
                st.session_state.bridge_progress += 1
                st.session_state.last_msg = "Korrekt! Du rykkede frem."
            else:
                handle_damage(reset_level=True)
            st.rerun()
            
        # Tjek om færdig
        if st.session_state.bridge_progress >= len(room['steps']):
            st.success("DU KLAREDE BROEN!")
            time.sleep(1)
            st.session_state.current_room_idx += 1
            st.session_state.mode = 'BRIEFING'
            st.rerun()

    # --- SPILTYPE: THE VAULT ---
    elif room['type'] == 'VAULT':
        st.image("https://img.icons8.com/ios/100/ffffff/safe.png", width=50)
        st.markdown("### Løs koderne før tiden løber ud")
        
        cols = st.columns(4)
        for i, task in enumerate(room['tasks']):
            with cols[i]:
                st.markdown(f"**Tal {i+1}**")
                st.caption(task['desc'])
        
        user_code = st.text_input("Indtast 4-cifret kode", max_chars=4)
        
        if st.button("Lås op"):
            correct = "".join([t['res'] for t in room['tasks']])
            if user_code == correct:
                st.balloons()
                st.success("DØREN ÅBNES!")
                time.sleep(2)
                st.session_state.current_room_idx += 1
                st.session_state.mode = 'BRIEFING'
                st.rerun()
            else:
                handle_damage()
                st.error("Forkert kode!")

# --- SLUT SKÆRME ---
elif st.session_state.mode == 'GAMEOVER':
    st.header("💀 GAME OVER")
    st.error("Du blev elimineret.")
    if st.button("Prøv igen"):
        st.session_state.mode = 'MENU'
        st.rerun()

elif st.session_state.mode == 'VICTORY':
    st.balloons()
    st.header("🏆 DU OVERLEVEDE!")
    st.success("Tillykke! Du gennemførte hele scenariet.")
    st.markdown(f"Scenarie: *{st.session_state.scenario.get('title', 'Ukendt')}*")
    if st.button("Spil nyt spil"):
        st.session_state.mode = 'MENU'
        st.rerun()
