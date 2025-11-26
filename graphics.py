import streamlit as st

def render_game_scene(state_mode, progress, total_time, elapsed_time=0):
    """
    Tegner spillets grafik.
    """
    
    # --- 1. BEREGNINGER ---
    
    # Farver
    player_color = "#00ff00" # Grøn
    bridge_color = "cyan"
    shadow_color = "black"
    
    # Dimensioner
    start_x = 20
    end_x = 250
    dist = end_x - start_x
    
    # Animation logik
    shadow_cx_start = start_x
    shadow_anim = ""
    player_y_anim = "" 
    
    if state_mode == 'PLAYING':
        # Beregn hvor skyggen skal starte LIGE NU
        if total_time > 0:
            percent_done = elapsed_time / total_time
            # Sikkerheds-tjek så den ikke går over 100%
            percent_done = min(percent_done, 1.0)
            
            shadow_cx_start = start_x + (dist * percent_done)
            time_left = max(0, total_time - elapsed_time)
        else:
            time_left = 0
            
        # Skyggen bevæger sig fra nuværende punkt til slutningen
        shadow_anim = f'<animate attributeName="cx" from="{shadow_cx_start}" to="{end_x}" dur="{time_left}s" fill="freeze" />'
        
    elif state_mode == 'DEATH':
        shadow_cx_start = end_x # Skyggen har fanget dig
        shadow_anim = "" 
        # Falde-animation (y går fra 120 til 500)
        player_y_anim = '<animate attributeName="cy" from="120" to="500" dur="1.5s" fill="freeze" />'
    
    else:
        return 

    # Spillerens position
    player_x = 250 + (progress * 50)

    # --- 2. BYG HTML (LINJE FOR LINJE) ---
    # Vi bygger strengen sådan her for at undgå indrykningsfejl
    
    svg = '<div style="width:100%; display:flex; justify-content:center; margin-bottom:20px;">'
    svg += '<svg width="600" height="300" style="background-color:#222; border:4px solid #444; border-radius:15px;">'
    
    # Baggrund
    svg += '<rect x="0" y="150" width="100%" height="150" fill="#111" />'
    
    # Broen
    svg += f'<line x1="0" y1="150" x2="600" y2="150" stroke="{bridge_color}" stroke-width="2" />'
    svg += f'<rect x="100" y="140" width="400" height="20" fill="{bridge_color}" opacity="0.3" />'
    
    # Skyggen
    svg += '<g>'
    svg += f'<circle cx="{shadow_cx_start}" cy="110" r="40" fill="{shadow_color}" opacity="0.9">{shadow_anim}</circle>'
    # Røde øjne på skyggen
    eye_anim = shadow_anim.replace('attributeName="cx"', f'attributeName="cx" values="{shadow_cx_start+10};{end_x+10}"') if shadow_anim else ""
    svg += f'<circle cx="{shadow_cx_start + 10}" cy="100" r="5" fill="red">{eye_anim}</circle>'
    svg += '</g>'
    
    # Spilleren
    svg += '<g>'
    svg += f'<circle cx="{player_x}" cy="120" r="20" fill="{player_color}" stroke="white" stroke-width="3">{player_y_anim}</circle>'
    svg += f'<text x="{player_x}" y="125" font-size="10" text-anchor="middle" fill="black" font-weight="bold">456</text>'
    svg += '</g>'
    
    # Advarselstekst
    svg += '<text x="20" y="30" fill="white" font-family="monospace" font-size="16">⚠️ TRUSSEL NÆRMER SIG</text>'
    
    svg += '</svg></div>'
    
    # Vis det som rå HTML
    st.markdown(svg, unsafe_allow_html=True)
