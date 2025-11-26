import streamlit as st
import time

def render_game_scene(state_mode, progress, total_time, elapsed_time, monster_anchor_x=50):
    """
    Version 10.0 - Stable Release.
    Fixer animations-caching og skygge-hop.
    """
    
    # --- 1. KONSTANTER ---
    scene_width = 600
    ground_y = 200
    monster_y = ground_y - 60
    player_y = ground_y - 50
    
    start_platform_x = 50   
    # 4 trin á 80px + mellemrum. 
    # Start plat slut: 100. 
    # Panel 1 center: 150. Panel 2: 250. Panel 3: 350. Panel 4: 450.
    # Sikkerhed: 550.
    
    # Beregn spillerens mål
    if progress >= 4:
        target_player_x = 550 # Sikkerhed!
    else:
        target_player_x = 150 + (progress * 100)
    
    # --- 2. ANIMATION LOGIK ---
    
    monster_anim = ""
    initial_monster_x = monster_anchor_x
    
    # SPILLER (Default: Står stille)
    # Vi tvinger y-positionen i translate, så vi er sikre på han starter oppe
    player_transform = f'translate({target_player_x}, {player_y})'
    player_anim_content = ""
    player_opacity = "1.0"
    
    if state_mode == 'PLAYING':
        time_left = max(0, total_time - elapsed_time)
        if time_left > 0:
            # Animation fra ANKER (hvor den var sidst) til SPILLER (hvor han er nu)
            monster_anim = f'<animateTransform attributeName="transform" type="translate" from="{initial_monster_x} {monster_y}" to="{target_player_x} {monster_y}" dur="{time_left}s" fill="freeze" />'
        else:
            initial_monster_x = target_player_x
            
    elif state_mode == 'DEATH':
        # Monster står ved spilleren (bruger target_player_x da det er der han døde)
        initial_monster_x = target_player_x
        monster_anim = "" 
        
        # Spiller falder
        # VIGTIGT: Vi bruger et unikt ID for at tvinge browseren til at afspille igen
        player_anim_content = '<animateTransform attributeName="transform" type="translate" from="0 0" to="0 300" begin="0s" dur="1s" fill="freeze" />'
        player_opacity = "0.6"

    elif state_mode == 'BRIEFING':
        initial_monster_x = start_platform_x
        monster_anim = ""

    # --- 3. BYG SVG ---
    
    # Vi genererer et unikt ID baseret på tiden for at undgå browser-caching af animationer
    unique_id = int(time.time() * 1000)
    
    html = f'<div style="width:100%; display:flex; justify-content:center; margin-bottom:20px;">'
    html += f'<svg id="game_svg_{unique_id}" width="{scene_width}" height="350" style="background: radial-gradient(circle, #444 0%, #111 100%); border: 2px solid #666; border-radius: 10px;">'
    
    # BAGGRUND
    html += '<rect x="0" y="0" width="100%" height="100%" fill="none" />'
    
    # START PLATFORM
    html += f'<rect x="0" y="{ground_y}" width="100" height="150" fill="#555" stroke="#777" stroke-width="2"/>'
    html += f'<text x="50" y="{ground_y + 40}" fill="#aaa" font-family="monospace" text-anchor="middle" font-size="12">START</text>'

    # SLUT PLATFORM
    html += f'<rect x="500" y="{ground_y}" width="100" height="150" fill="#555" stroke="#777" stroke-width="2"/>'
    html += f'<text x="550" y="{ground_y + 40}" fill="#aaa" font-family="monospace" text-anchor="middle" font-size="12">MÅL</text>'

    # BROEN
    html += f'<line x1="100" y1="{ground_y+5}" x2="500" y2="{ground_y+5}" stroke="#00ffff" stroke-width="4" />'
    html += f'<line x1="100" y1="{ground_y+35}" x2="500" y2="{ground_y+35}" stroke="#00ffff" stroke-width="4" />'
    
    # 4 Glaspaneler
    html += f'<g stroke="#00ffff" stroke-width="1" fill="rgba(200, 255, 255, 0.2)">'
    for i in range(4):
        panel_x = 110 + (i * 100)
        html += f'<rect x="{panel_x}" y="{ground_y+5}" width="80" height="30" />'
    html += '</g>'

    # SPILLEREN
    html += f'<g transform="{player_transform}" opacity="{player_opacity}">'
    html += player_anim_content
    html += '<circle cx="0" cy="0" r="12" fill="none" stroke="#00ff00" stroke-width="2" />'
    html += '<line x1="0" y1="12" x2="0" y2="40" stroke="#00ff00" stroke-width="2" />'
    html += '<line x1="0" y1="20" x2="-15" y2="35" stroke="#00ff00" stroke-width="2" />'
    html += '<line x1="0" y1="20" x2="15" y2="35" stroke="#00ff00" stroke-width="2" />'
    html += '<line x1="0" y1="40" x2="-10" y2="60" stroke="#00ff00" stroke-width="2" />'
    html += '<line x1="0" y1="40" x2="10" y2="60" stroke="#00ff00" stroke-width="2" />'
    html += '<text x="0" y="-20" fill="#00ff00" font-size="10" text-anchor="middle" font-weight="bold">456</text>'
    html += '</g>'

    # MONSTER
    monster_transform = f'translate({initial_monster_x}, {monster_y})'
    html += f'<g transform="{monster_transform}">'
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
