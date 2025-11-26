import streamlit as st
import textwrap

def render_game_scene(state_mode, progress, total_time, elapsed_time=0):
    """
    Tegner spillets grafik.
    Nu med korrekt tidsstyring af skyggen.
    """
    
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
        # Beregn hvor skyggen skal starte LIGE NU (så den ikke starter forfra ved svar)
        if total_time > 0:
            percent_done = elapsed_time / total_time
            shadow_cx_start = start_x + (dist * percent_done)
            time_left = max(0, total_time - elapsed_time)
        else:
            time_left = 0
            
        # Skyggen bevæger sig fra nuværende punkt til slutningen
        shadow_anim = f'<animate attributeName="cx" from="{shadow_cx_start}" to="{end_x}" dur="{time_left}s" fill="freeze" />'
        
    elif state_mode == 'DEATH':
        shadow_cx_start = end_x # Skyggen har fanget dig
        shadow_anim = "" 
        # Falde-animation
        player_y_anim = '<animate attributeName="cy" from="120" to="500" dur="1.5s" fill="freeze" />'
    
    else:
        return 

    # Spillerens position (250px start + 50px pr skridt)
    player_x = 250 + (progress * 50)

    # Vi bruger dedent for at fjerne indrykning, så Streamlit ikke tror det er kode
    html_code = textwrap.dedent(f"""
    <div style="width:100%; display:flex; justify-content:center; margin-bottom:20px;">
        <svg width="600" height="300" style="background-color:#222; border:4px solid #444; border-radius:15px;">
            <rect x="0" y="150" width="100%" height="150" fill="#111" />
            
            <line x1="0" y1="150" x2="600" y2="150" stroke="{bridge_color}" stroke-width="2" />
            <rect x="100" y="140" width="400" height="20" fill="{bridge_color}" opacity="0.3" />
            
            <g>
                <circle cx="{shadow_cx_start}" cy="110" r="40" fill="{shadow_color}" opacity="0.9">
                    {shadow_anim}
                </circle>
                <circle cx="{shadow_cx_start + 10}" cy="100" r="5" fill="red">
                    {shadow_anim.replace('attributeName="cx"', 'attributeName="cx" values="' + str(shadow_cx_start+10) + ';' + str(end_x+10) + '"')}
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
    """)
    
    st.markdown(html_code, unsafe_allow_html=True)
