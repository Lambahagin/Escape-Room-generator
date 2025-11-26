import streamlit as st

def render_game_scene(state_mode, progress, total_time, elapsed_time=0):
    """
    Tegner spillets grafik. Version 5.6 - Fixet Dødsanimation.
    """
    
    # --- 1. KONSTANTER ---
    scene_width = 600
    ground_y = 200
    monster_y = ground_y - 60
    player_y = ground_y - 50
    
    # X-Koordinater
    start_platform_x = 50   
    player_start_x = 150    
    step_size = 100         
    
    # Beregn spillerens position
    target_player_x = player_start_x + (progress * step_size)
    
    # --- 2. LOGIK ---
    
    monster_current_x = start_platform_x
    monster_anim = ""
    
    # Spiller Animation (Default: Ingen)
    player_transform_anim = "" 
    player_opacity = "1.0"
    
    if state_mode == 'PLAYING' and total_time > 0:
        # --- SPIL TILSTAND ---
        percent_done = min(elapsed_time / total_time, 1.0)
        total_hunt_distance = target_player_x - start_platform_x
        monster_current_x = start_platform_x + (total_hunt_distance * percent_done)
        time_left = max(0, total_time - elapsed_time)
        
        # Monster jagter spilleren
        monster_anim = f'<animateTransform attributeName="transform" type="translate" from="{monster_current_x} {monster_y}" to="{target_player_x} {monster_y}" dur="{time_left}s" fill="freeze" />'
        
    elif state_mode == 'DEATH':
        # --- DØD TILSTAND ---
        # Monsteret står nu præcis hvor spilleren er
        monster_current_x = target_player_x
        monster_anim = "" # Ingen bevægelse, den har fanget dig
        
        # Spiller falder ned
        # Vi bruger 'begin="0s"' for at tvinge den i gang med det samme
        player_transform_anim = '<animateTransform attributeName="transform" type="translate" from="0 0" to="0 300" begin="0s" dur="1s" fill="freeze" />'
        player_opacity = "0.6"

    elif state_mode == 'BRIEFING':
        monster_current_x = start_platform_x
        monster_anim = ""
    else:
        return 

    # --- 3. BYG SVG ---
    
    html = f'<div style="width:100%; display:flex; justify-content:center; margin-bottom:20px;">'
    html += f'<svg width="{scene_width}" height="350" style="background: radial-gradient(circle, #444 0%, #111 100%); border: 2px solid #666; border-radius: 10px;">'
    
    # BAGGRUND & PLATFORME
    html += '<rect x="0" y="0" width="100%" height="100%" fill="none" />'
    html += f'<rect x="0" y="{ground_y}" width="100" height="150" fill="#555" stroke="#777" stroke-width="2"/>'
    html += f'<text x="50" y="{ground_y + 40}" fill="#aaa" font-family="monospace" text-anchor="middle" font-size="12">START</text>'
    html += f'<rect x="500" y="{ground_y}" width="100" height="150" fill="#555" stroke="#777" stroke-width="2"/>'
    html += f'<text x="550" y="{ground_y + 40}" fill="#aaa" font-family="monospace" text-anchor="middle" font-size="12">SIKKERHED</text>'

    # BROEN
    html += f'<line x1="100" y1="{ground_y+5}" x2="500" y2="{ground_y+5}" stroke="#00ffff" stroke-width="4" />'
    html += f'<line x1="100" y1="{ground_y+35}" x2="500" y2="{ground_y+35}" stroke="#00ffff" stroke-width="4" />'
    html += f'<g stroke="#00ffff" stroke-width="1" fill="rgba(200, 255, 255, 0.2)">'
    for i in range(4):
        html += f'<rect x="{110 + (i * 100)}" y="{ground_y+5}" width="80" height="30" />'
    html += '</g>'

    # SPILLEREN (Stickman)
    # Vi anvender animationen her
    html += f'<g transform="translate({target_player_x}, {player_y})" opacity="{player_opacity}">'
    html += player_transform_anim
    html += '<circle cx="0" cy="0" r="12" fill="none" stroke="#00ff00" stroke-width="2" />'
    html += '<line x1="0" y1="12" x2="0" y2="40" stroke="#00ff00" stroke-width="2" />'
    html += '<line x1="0" y1="20" x2="-15" y2="35" stroke="#00ff00" stroke-width="2" />'
    html += '<line x1="0" y1="20" x2="15" y2="35" stroke="#00ff00" stroke-width="2" />'
    html += '<line x1="0" y1="40" x2="-10" y2="60" stroke="#00ff00" stroke-width="2" />'
    html += '<line x1="0" y1="40" x2="10" y2="60" stroke="#00ff00" stroke-width="2" />'
    html += '<text x="0" y="-20" fill="#00ff00" font-size="10" text-anchor="middle" font-weight="bold">456</text>'
    html += '</g>'

    # SKYGGE MONSTERET
    # Transform bruges enten til fast position ELLER animation
    transform_val = f'translate({monster_current_x}, {monster_y})'
    html += f'<g transform="{transform_val}">'
    html += monster_anim
    
    html += '<path d="M -20,0 Q -30,-40 0,-60 Q 30,-40 20,0 Q 10,20 -20,0" fill="black" filter="url(#glow)" opacity="0.95" />'
    html += '<path d="M -15,-20 Q -40,-10 -30,10" stroke="black" stroke-width="3" fill="none" />'
    html += '<path d="M 15,-20 Q 40,-10 30,10" stroke="black" stroke-width="3" fill="none" />'
    html += '<circle cx="-8" cy="-35" r="4" fill="red"><animate attributeName="r" values="4;6;4" dur="0.5s" repeatCount="indefinite" /></circle>'
    html += '<circle cx="8" cy="-35" r="4" fill="red"><animate attributeName="r" values="4;6;4" dur="0.5s" repeatCount="indefinite" /></circle>'
    html += '</g>'

    html += '<defs><filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3" result="coloredBlur"/><feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>'
    html += '</svg></div>'
    
    st.markdown(html, unsafe_allow_html=True)
