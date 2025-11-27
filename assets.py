# assets.py
import textwrap

def get_theme_colors(theme):
    if theme == "wonderland":
        return {
            "bg_center": "#a8c0ff", # Lys blå
            "bg_edge": "#3f2b96",   # Mørk lilla
            "platform": "#8E44AD",  # Lilla platforme
            "bridge": "#ff00ff",    # Neon pink bro
            "glass": "rgba(255, 200, 255, 0.3)"
        }
    else: # Default: squid
        return {
            "bg_center": "#444444",
            "bg_edge": "#111111",
            "platform": "#333333",
            "bridge": "#00ffff",
            "glass": "rgba(200, 255, 255, 0.2)"
        }

def get_player_svg(theme):
    """Returnerer SVG-indholdet for spilleren (inde i en <g> tag)"""
    if theme == "wonderland":
        # En lille blå kjole (Alice stil)
        return """
            <circle cx="0" cy="0" r="10" fill="#ffccaa" stroke="none" /> <path d="M -10,10 L 10,10 L 15,40 L -15,40 Z" fill="#3498db" /> <line x1="-10" y1="15" x2="-20" y2="30" stroke="#ffccaa" stroke-width="3" /> <line x1="10" y1="15" x2="20" y2="30" stroke="#ffccaa" stroke-width="3" /> <line x1="-5" y1="40" x2="-5" y2="60" stroke="white" stroke-width="3" /> <line x1="5" y1="40" x2="5" y2="60" stroke="white" stroke-width="3" /> """
    else:
        # Squid Game Stickman (Grøn)
        return """
            <circle cx="0" cy="0" r="12" fill="none" stroke="#0f0" stroke-width="2" />
            <line x1="0" y1="12" x2="0" y2="40" stroke="#0f0" stroke-width="2" />
            <line x1="0" y1="20" x2="-15" y2="35" stroke="#0f0" stroke-width="2" />
            <line x1="0" y1="20" x2="15" y2="35" stroke="#0f0" stroke-width="2" />
            <line x1="0" y1="40" x2="-10" y2="60" stroke="#0f0" stroke-width="2" />
            <line x1="0" y1="40" x2="10" y2="60" stroke="#0f0" stroke-width="2" />
            <text x="0" y="-20" fill="#0f0" font-size="10" text-anchor="middle">456</text>
        """

def get_monster_svg(theme):
    """Returnerer SVG-indholdet for monsteret"""
    if theme == "wonderland":
        # En lilla katte-skygge (Cheshire Cat vibe)
        return """
            <path d="M -25,0 Q -35,-40 0,-50 Q 35,-40 25,0 Q 12,20 -25,0" fill="#8e44ad" opacity="0.9" filter="url(#glow)"/>
            <path d="M -20,-45 L -25,-60 L -10,-50 Z" fill="#8e44ad" /> <path d="M 20,-45 L 25,-60 L 10,-50 Z" fill="#8e44ad" /> <path d="M -15,-10 Q 0,10 15,-10" stroke="white" stroke-width="3" fill="none" /> <circle cx="-10" cy="-25" r="5" fill="#f1c40f" /> <circle cx="10" cy="-25" r="5" fill="#f1c40f" /> """
    else:
        # Skygge Monsteret (Sort Blob)
        return """
            <path d="M -25,0 Q -35,-50 0,-70 Q 35,-50 25,0 Q 12,20 -25,0" fill="black" opacity="0.95" filter="url(#glow)"/>
            <circle cx="-10" cy="-40" r="5" fill="red" />
            <circle cx="10" cy="-40" r="5" fill="red" />
        """
