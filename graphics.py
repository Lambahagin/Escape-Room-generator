import streamlit as st

def render_game_scene(state_mode, progress, time_limit):
    """
    Tegner spillets grafik.
    state_mode: 'PLAYING' eller 'DEATH'
    progress: Hvor langt er spilleren (0, 1, 2...)
    time_limit: Hvor lang tid animationen skal tage
    """
    
    # Farve-indstillinger (Nemme at ændre her)
    player_color = "#00ff00" # Grøn
    bridge_color = "cyan"
    shadow_color = "black"
    
    # Animation logik
    if state_mode == 'PLAYING':
        # Skyggen bevæger sig fra venstre mod højre
        shadow_anim = f'<animate attributeName="cx" from="20" to="250" dur="{time_limit}s" fill="freeze" />'
        # Spilleren står stille (flytter sig kun ved klik)
        player_y_anim = "" 
        shadow_x_start = 20
        
    elif state_mode == 'DEATH':
        # Skyggen er nået frem
        shadow_anim = "" 
        shadow_x_start = 250 
        # Spilleren falder ned
        player_y_anim = '<animate attributeName="cy" from="100" to="500" dur="1.5s" fill="freeze" />'
    
    else:
        return # Tegn ingenting

    # Beregn spillerens position på broen
    # Start position er 250px. Hvert skridt flytter ham 50px til højre.
    player_x = 250 + (progress * 50)

    # Her laver vi SVG grafikken (Vector grafik)
    html_code = f"""
    <div style="display: flex; justify-content: center;">
    <svg width="600" height="300" style="background: #222; border: 4px solid #444; border-radius: 15px;">
        
        <rect x="0" y="150" width="100%" height="150" fill="#111" />
        
        <line x1="0" y1="150" x2="600" y2="150" stroke="{bridge_color}" stroke-width="2" />
        <rect x="100" y="140" width="400" height="20" fill="{bridge_color}" opacity="0.3" />
        
        <g>
            <circle cx="{shadow_x_start}" cy="110" r="40" fill="{shadow_color}" opacity="0.9">
                {shadow_anim}
            </circle>
            <circle cx="{shadow_x_start + 10}" cy="100" r="5" fill="red">
                {shadow_anim.replace('attributeName="cx"', 'attributeName="cx" values="' + str(30) + ';' + str(260) + '"')}
            </circle>
        </g>
        
        <g>
            <circle cx="{player_x}" cy="120" r="20" fill="{player_color}" stroke="white" stroke-width="3">
                {player_y_anim}
            </circle>
            <text x="{player_x}" y="125" font-size="10" text-anchor="middle" fill="black" font-weight="bold">456</text>
        </g>
        
        <text x="20" y="30" fill="white" font-family="monospace" font-size="16">⚠️ TRUSSEL NÆRMER SIG</text>
    </svg>
    </div>
    """
    
    # Indsæt i Streamlit
    st.markdown(html_code, unsafe_allow_html=True)
