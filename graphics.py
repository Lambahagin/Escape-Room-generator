import streamlit as st

def render_game_scene(state_mode, progress, total_time, elapsed_time=0):
    """
    Tegner spillets grafik. Version 5.4 - Korrekt jagt-logik.
    """
    
    # --- 1. KONSTANTER & FARVER ---
    bridge_color = "#00ffff"     # Neon cyan
    platform_color = "#555555"   # Endnu lysere grå platforme for kontrast
    glass_color = "rgba(200, 255, 255, 0.2)" 
    
    # Baggrund (Lysere end før for at se skyggen)
    bg_center = "#555555" 
    bg_edge = "#222222"   
    
    # Koordinater
    scene_width = 600
    ground_y = 200
    monster_y_pos = ground_y - 60
    
    start_x = 50   # Monster start
    
    # Spillerens position (Dynamisk)
    step_size = 100
    player_base_x = 150 + (progress * step_size)
    
    # --- 2. BEREGN POSITIONER ---
    
    monster_current_x = start_x
    monster_anim = ""
    
    if state_mode == 'PLAYING' and total_time > 0:
        # 1. Hvor stor procentdel af tiden er gået?
        percent_done = min(elapsed_time / total_time, 1.0)
        
        # 2. Hvad er den totale distance monsteret skal dække for at fange spilleren LIGE NU?
        total_distance_to_catch = player_base_x - start_x
        
        # 3. Hvor burde monsteret være lige nu baseret på tiden?
        monster_current_x = start_x + (total_distance_to_catch * percent_done)
        
        # 4. Hvor lang tid er der tilbage?
        time_left = max(0, total_time - elapsed_time)
        
        # 5. ANIMATION:
        # Start: Nuværende beregnede position
        # Slut: Spillerens position (IKKE banens slutning)
        # Tid: Resterende tid
        # Dette sikrer, at hastigheden (Distance / Tid) opdateres, når spilleren rykker sig.
        monster_anim = f'<animateTransform attributeName="transform" type="translate" from="{monster_current_x} {monster_y_pos}" to="{player_base_x} {monster_y_pos}" dur="{time_left}s" fill="freeze" />'
        
    elif state_mode == 'DEATH':
        monster_current_x = player_base_x # Skyggen står oven i spilleren
        monster_anim = ""
    elif state_mode == 'BRIEFING':
        monster_current_x = start_x
        monster_anim = ""
    else:
        return 

    # Spiller animation
    player_y_anim = ""
    player_opacity = "1.0"
    
    if state_mode == 'DEATH':
        player_y_anim = '<animateTransform attributeName="transform" type="translate" from="0 0" to="0 300" dur="1s" fill="freeze" />'
        player_opacity = "0.8"

    # --- 3. BYG SVG ---
    
    html = f'<div style="width:100%; display:flex; justify-content:center; margin-bottom:20px;">'
    html += f'<svg width="{scene_width}" height="350" style="background: radial-gradient(circle, {bg_center} 0%, {bg_edge} 100%); border: 2px solid #666; border-radius: 10px;">'
    
    # 1. BAGGRUND
    html += '<rect x="0" y="0" width="100%" height="100%" fill="none" />'
    
    # 2. START PLATFORM
    html += f'<rect x="0" y="{ground_y}" width="100" height="150" fill="{platform_color}" stroke="#777" stroke-width="2"/>'
    html += f'<text x="50" y="{ground_y + 40}" fill="#aaa" font-family="monospace" text-anchor="middle" font-size="12">START</text>'

    # 3. SLUT PLATFORM
    html += f'<rect x="500" y="{ground_y}" width="100" height="150" fill="{platform_color}" stroke="#777" stroke-width="2"/>'
    html += f'<text x="550" y="{ground_y + 40}" fill="#aaa" font-family="monospace" text-anchor="middle" font-size="12">SIKKERHED</text>'

    # 4. GLASBROEN
    html += f'<line x1="100" y1="{ground_y+5}" x2="500" y2="{ground_y+5}" stroke="{bridge_color}" stroke-width="4" />'
    html += f'<line x1="100" y1="{ground_y+35}" x2="500" y2="{ground_y+35}" stroke="{bridge_color}" stroke-width="4" />'
    
    html += f'<g stroke="{bridge_color}" stroke-width="1" fill="{glass_color}">'
    html += f'<rect x="110" y="{ground_y+5}" width="80" height="30" />'
    html += f'<rect x="210" y="{ground_y+5}" width="80" height="30" />'
    html += f'<rect x="310" y="{ground_y+5}" width="80" height="30" />'
    html += f'<rect x="410" y="{ground_y+5}" width="80" height="30" />'
    html += '</g>'

    # 5. SPILLEREN (Stickman)
    # Vi bruger en gruppe med transform, så vi nemt kan flytte hele manden
    html += f'<g transform="translate({player_base_x}, {ground_y - 50})" opacity="{player_opacity}">'
    html += player_y_anim
    html += '<circle cx="0" cy="0" r="12" fill="none" stroke="#00ff00" stroke-width="2" />'
    html += '<line x1="0" y1="12" x2="0" y2="40" stroke="#00ff00" stroke-width="2" />'
    html += '<line x1="0" y1="20" x2="-15" y2="35" stroke="#00ff00" stroke-width="2" />'
    html += '<line x1="0" y1="20" x2="15" y2="35" stroke="#00ff00" stroke-width="2" />'
    html += '<line x1="0" y1="40" x2="-10" y2="60" stroke="#00ff00" stroke-width="2" />'
    html += '<line x1="0" y1="40" x2="10" y2="60" stroke="#00ff00" stroke-width="2" />'
    html += '<text x="0" y="-15" fill="#00ff00" font-size="10" text-anchor="middle">456</text>'
    html += '</g>'

    # 6. SKYGGE MONSTERET
    # Monsteret bruger også en gruppe. 
    # Vi sætter start-positionen direkte i transform
    html += f'<g transform="translate({monster_current_x}, {monster_y_pos})">'
    html += monster_anim
    
    # Blob krop
    html += '<path d="M -20,0 Q -30,-40 0,-60 Q 30,-40 20,0 Q 10,20 -20,0" fill="black" filter="url(#glow)" opacity="0.9" />'
    # Arme
    html += '<path d="M -15,-20 Q -40,-10 -30,10" stroke="black" stroke-width="3" fill="none" />'
    html += '<path d="M 15,-20 Q 40,-10 30,10" stroke="black" stroke-width="3" fill="none" />'
    # Øjne
    html += '<circle cx="-8" cy="-35" r="4" fill="red"><animate attributeName="r" values="4;5;4" dur="0.5s" repeatCount="indefinite" /></circle>'
    html += '<circle cx="8" cy="-35" r="4" fill="red"><animate attributeName="r" values="4;5;4" dur="0.5s" repeatCount="indefinite" /></circle>'
    html += '</g>'

    html += '<defs><filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.5" result="coloredBlur"/><feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>'

    html += '</svg></div>'
    
    st.markdown(html, unsafe_allow_html=True)
