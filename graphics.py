import streamlit as st

def render_game_scene(state_mode, progress, total_time, elapsed_time=0):
    """
    Tegner spillets grafik.
    Bygger HTML-strengen manuelt for at undgå indrykningsfejl.
    """
    
    # --- 1. KONSTANTER & FARVER ---
    bridge_color = "#00ffff"     # Neon cyan
    platform_color = "#333333"   # Mørkegrå platforme
    glass_color = "rgba(200, 255, 255, 0.2)" # Halvgennemsigtig glas
    
    # Koordinater
    scene_width = 600
    ground_y = 200
    
    start_x = 50   # Monster start
    end_x = 500    # Spiller start (og monster slut)
    
    # --- 2. BEREGN POSITIONER ---
    
    # Monsterets position
    monster_x = start_x
    monster_anim = ""
    monster_start_pos = 0 # Justering til gruppe-transform
    
    if state_mode == 'PLAYING' and total_time > 0:
        percent_done = min(elapsed_time / total_time, 1.0)
        monster_x = start_x + ((end_x - start_x) * percent_done)
        time_left = max(0, total_time - elapsed_time)
        # Animation fra nuværende punkt til slut
        monster_anim = f'<animateTransform attributeName="transform" type="translate" from="{monster_x} 0" to="{end_x} 0" dur="{time_left}s" fill="freeze" />'
        monster_start_pos = 0 
    elif state_mode == 'DEATH':
        monster_start_pos = end_x 
        monster_anim = ""
    elif state_mode == 'BRIEFING':
        monster_start_pos = start_x
        monster_anim = ""
    else:
        return # Ingen tegning

    # Spillerens position
    step_size = 100
    player_base_x = 150 + (progress * step_size)
    
    player_y_anim = ""
    player_opacity = "1.0"
    
    if state_mode == 'DEATH':
        # Falde animation
        player_y_anim = '<animateTransform attributeName="transform" type="translate" from="0 0" to="0 300" dur="1s" fill="freeze" />'
        player_opacity = "0.8"

    # --- 3. BYG SVG (LINJE FOR LINJE) ---
    # Vi samler strengen uden indrykning for at sikre, at Streamlit læser det som HTML
    
    html = f'<div style="width:100%; display:flex; justify-content:center; margin-bottom:20px;">'
    html += f'<svg width="{scene_width}" height="350" style="background: radial-gradient(circle, #222 0%, #000 100%); border: 2px solid #444; border-radius: 10px;">'
    
    # 1. BAGGRUND
    html += '<rect x="0" y="0" width="100%" height="100%" fill="none" />'
    
    # 2. START PLATFORM
    html += f'<rect x="0" y="{ground_y}" width="100" height="150" fill="{platform_color}" stroke="#555" stroke-width="2"/>'
    html += f'<text x="50" y="{ground_y + 40}" fill="#555" font-family="monospace" text-anchor="middle" font-size="12">START</text>'

    # 3. SLUT PLATFORM
    html += f'<rect x="500" y="{ground_y}" width="100" height="150" fill="{platform_color}" stroke="#555" stroke-width="2"/>'
    html += f'<text x="550" y="{ground_y + 40}" fill="#555" font-family="monospace" text-anchor="middle" font-size="12">SIKKERHED</text>'

    # 4. GLASBROEN
    html += f'<line x1="100" y1="{ground_y+5}" x2="500" y2="{ground_y+5}" stroke="{bridge_color}" stroke-width="4" />'
    html += f'<line x1="100" y1="{ground_y+35}" x2="500" y2="{ground_y+35}" stroke="{bridge_color}" stroke-width="4" />'
    
    # Glaspaneler
    html += f'<g stroke="{bridge_color}" stroke-width="1" fill="{glass_color}">'
    html += f'<rect x="110" y="{ground_y+5}" width="80" height="30" />'
    html += f'<rect x="210" y="{ground_y+5}" width="80" height="30" />'
    html += f'<rect x="310" y="{ground_y+5}" width="80" height="30" />'
    html += f'<rect x="410" y="{ground_y+5}" width="80" height="30" />'
    html += '</g>'

    # 5. SPILLEREN (Stickman)
    html += f'<g transform="translate({player_base_x}, {ground_y - 50})" opacity="{player_opacity}">'
    html += player_y_anim
    html += '<circle cx="0" cy="0" r="12" fill="none" stroke="#00ff00" stroke-width="2" />' # Hoved
    html += '<line x1="0" y1="12" x2="0" y2="40" stroke="#00ff00" stroke-width="2" />' # Krop
    html += '<line x1="0" y1="20" x2="-15" y2="35" stroke="#00ff00" stroke-width="2" />' # Arm V
    html += '<line x1="0" y1="20" x2="15" y2="35" stroke="#00ff00" stroke-width="2" />' # Arm H
    html += '<line x1="0" y1="40" x2="-10" y2="60" stroke="#00ff00" stroke-width="2" />' # Ben V
    html += '<line x1="0" y1="40" x2="10" y2="60" stroke="#00ff00" stroke-width="2" />' # Ben H
    html += '<text x="0" y="-15" fill="#00ff00" font-size="10" text-anchor="middle">456</text>'
    html += '</g>'

    # 6. SKYGGE MONSTERET
    html += f'<g transform="translate({monster_start_pos}, {ground_y - 60})">'
    html += monster_anim
    # Krop (Blob)
    html += '<path d="M -20,0 Q -30,-40 0,-60 Q 30,-40 20,0 Q 10,20 -20,0" fill="black" filter="url(#glow)" opacity="0.9" />'
    # Arme
    html += '<path d="M -15,-20 Q -40,-10 -30,10" stroke="black" stroke-width="3" fill="none" />'
    html += '<path d="M 15,-20 Q 40,-10 30,10" stroke="black" stroke-width="3" fill="none" />'
    # Øjne
    html += '<circle cx="-8" cy="-35" r="4" fill="red"><animate attributeName="r" values="4;5;4" dur="0.5s" repeatCount="indefinite" /></circle>'
    html += '<circle cx="8" cy="-35" r="4" fill="red"><animate attributeName="r" values="4;5;4" dur="0.5s" repeatCount="indefinite" /></circle>'
    html += '</g>'

    # Filtre
    html += '<defs><filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.5" result="coloredBlur"/><feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>'

    html += '</svg></div>'
    
    # Vis det som rå HTML
    st.markdown(html, unsafe_allow_html=True)
