import streamlit as st

def render_game_scene(state_mode, progress, total_time, elapsed_time, monster_anchor_x=0):
    """
    Tegner spillets grafik. Version 8.0 - SVG Chaining.
    Animationer afløser hinanden automatisk uden Python-reload.
    """
    
    # --- 1. KONSTANTER ---
    scene_width = 600
    ground_y = 200
    monster_y = ground_y - 60
    player_y = ground_y - 50
    
    step_size = 100         
    
    # Beregn spillerens position (Målet)
    # Vi starter spilleren ved 150. Trin 0 = 150.
    target_player_x = 150 + (progress * step_size)
    
    # --- 2. ANIMATIONS LOGIK ---
    
    monster_anim = ""
    player_anim = "" # Her styrer vi faldet
    
    # Hvor starter monsteret denne gang?
    initial_monster_x = monster_anchor_x
    
    if state_mode == 'PLAYING':
        # Beregn rest-tid
        time_left = max(0, total_time - elapsed_time)
        
        if time_left > 0:
            # 1. MONSTER ANIMATION (Jagt)
            # Vi giver den 'id="hunt"' så vi kan henvise til den
            monster_anim = f'<animateTransform id="hunt" attributeName="transform" type="translate" from="{initial_monster_x} {monster_y}" to="{target_player_x} {monster_y}" dur="{time_left}s" fill="freeze" />'
            
            # 2. SPILLER ANIMATION (Auto-død)
            # Denne starter KUN når 'hunt' er færdig (begin="hunt.end")
            player_anim = '<animateTransform attributeName="transform" type="translate" from="0 0" to="0 300" begin="hunt.end" dur="0.5s" fill="freeze" />'
        else:
            # Tiden er allerede gået -> Monster står ved spiller
            initial_monster_x = target_player_x
            monster_anim = ""
            # Spiller falder med det samme
            player_anim = '<animateTransform attributeName="transform" type="translate" from="0 0" to="0 300" begin="0s" dur="0.5s" fill="freeze" />'
        
    elif state_mode == 'DEATH':
        # Spilleren døde pga forkert svar -> Monster står ved spilleren
        initial_monster_x = target_player_x
        monster_anim = ""
        
        # Spiller falder med det samme (Straf)
        player_anim = '<animateTransform attributeName="transform" type="translate" from="0 0" to="0 300" begin="0s" dur="0.5s" fill="freeze" />'
        
    elif state_mode == 'BRIEFING':
        initial_monster_x = 0 # Start platform
        monster_anim = ""
    else:
        return 

    # --- 3. BYG SVG ---
    
    html = f'<div style="width:100%; display:flex; justify-content:center; margin-bottom:20px;">'
    html += f'<svg width="{scene_width}" height="350" style="background: radial-gradient(circle, #444 0%, #111 100%); border: 2px solid #666; border-radius: 10px;">'
    
    # BAGGRUND
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

    # SPILLEREN
    html += f'<g transform="translate({target_player_x}, {player_y})">'
    html += player_anim  # Her indsættes den betingede animation
    html += '<circle cx="0" cy="0" r="12" fill="none" stroke="#00ff00" stroke-width="2" />'
    html += '<line x1="0" y1="12" x2="0" y2="40" stroke="#00ff00" stroke-width="2" />'
    html += '<line x1="0" y1="20" x2="-15" y2="35" stroke="#00ff00" stroke-width="2" />'
    html += '<line x1="0" y1="20" x2="15" y2="35" stroke="#00ff00" stroke-width="2" />'
    html += '<line x1="0" y1="40" x2="-10" y2="60" stroke="#00ff00" stroke-width="2" />'
    html += '<line x1="0" y1="40" x2="10" y2="60" stroke="#00ff00" stroke-width="2" />'
    html += '<text x="0" y="-20" fill="#00ff00" font-size="10" text-anchor="middle" font-weight="bold">456</text>'
    html += '</g>'

    # MONSTER
    html += f'<g transform="translate({initial_monster_x}, {monster_y})">'
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
