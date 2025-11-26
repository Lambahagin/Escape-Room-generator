import streamlit as st

def render_game_scene(state_mode, player_step, total_time, elapsed_time, monster_start_x):
    """
    Version 7.0: Dum grafik-motor.
    Den tegner kun fra A (monster_start_x) til B (player_x) over T (remaining_time).
    """
    
    # --- KONSTANTER ---
    scene_width = 600
    ground_y = 200
    monster_y = ground_y - 60
    player_y = ground_y - 50
    
    step_size = 100
    player_x = 150 + (player_step * step_size)
    
    # --- LOGIK ---
    monster_anim = ""
    current_monster_visual_x = monster_start_x # Hvor tegner vi monsteret?
    
    if state_mode == 'PLAYING':
        time_left = max(0, total_time - elapsed_time)
        
        # Hvis tiden er gået, skal den ikke animere, men stå ved målet
        if time_left <= 0:
            current_monster_visual_x = player_x
        else:
            # Animation fra ANKERET (monster_start_x) til SPILLEREN (player_x)
            monster_anim = f'<animateTransform attributeName="transform" type="translate" from="{monster_start_x} {monster_y}" to="{player_x} {monster_y}" dur="{time_left}s" fill="freeze" />'
            current_monster_visual_x = monster_start_x # Start animation herfra

    elif state_mode == 'DEATH':
        current_monster_visual_x = player_x # Monster står oven på spiller
    
    elif state_mode == 'BRIEFING':
        current_monster_visual_x = 0 # Start helt til venstre

    # --- TEGNING (SVG) ---
    html = f'<div style="width:100%; display:flex; justify-content:center; margin-bottom:20px;">'
    html += f'<svg width="{scene_width}" height="350" style="background: radial-gradient(circle, #444 0%, #111 100%); border: 2px solid #666; border-radius: 10px;">'
    
    # Baggrund & Platforme
    html += '<rect x="0" y="0" width="100%" height="100%" fill="none" />'
    html += f'<rect x="0" y="{ground_y}" width="100" height="150" fill="#555" stroke="#777" stroke-width="2"/>' # Start plat
    html += f'<rect x="500" y="{ground_y}" width="100" height="150" fill="#555" stroke="#777" stroke-width="2"/>' # Slut plat
    
    # Broen
    html += f'<line x1="100" y1="{ground_y+5}" x2="500" y2="{ground_y+5}" stroke="#00ffff" stroke-width="4" />'
    html += f'<line x1="100" y1="{ground_y+35}" x2="500" y2="{ground_y+35}" stroke="#00ffff" stroke-width="4" />'
    html += f'<g stroke="#00ffff" stroke-width="1" fill="rgba(200, 255, 255, 0.2)">'
    for i in range(4):
        html += f'<rect x="{110 + (i * 100)}" y="{ground_y+5}" width="80" height="30" />'
    html += '</g>'

    # SPILLER
    player_anim = ""
    if state_mode == 'DEATH':
        player_anim = '<animateTransform attributeName="transform" type="translate" from="0 0" to="0 300" dur="1s" fill="freeze" />'
    
    html += f'<g transform="translate({player_x}, {player_y})">'
    html += player_anim
    html += '<circle cx="0" cy="0" r="12" fill="none" stroke="#00ff00" stroke-width="2" />'
    html += '<line x1="0" y1="12" x2="0" y2="40" stroke="#00ff00" stroke-width="2" />'
    html += '<line x1="0" y1="20" x2="-15" y2="35" stroke="#00ff00" stroke-width="2" />'
    html += '<line x1="0" y1="20" x2="15" y2="35" stroke="#00ff00" stroke-width="2" />'
    html += '<line x1="0" y1="40" x2="-10" y2="60" stroke="#00ff00" stroke-width="2" />'
    html += '<line x1="0" y1="40" x2="10" y2="60" stroke="#00ff00" stroke-width="2" />'
    html += '<text x="0" y="-20" fill="#00ff00" font-size="10" text-anchor="middle" font-weight="bold">456</text>'
    html += '</g>'

    # MONSTER
    # Transform bruger animationen hvis den findes, ellers fast position
    html += f'<g transform="translate({current_monster_visual_x}, {monster_y})">'
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
