# assets.py
import textwrap

# Liste over alle mulige temaer - bruges af app.py til at vælge tilfældigt
AVAILABLE_THEMES = ["squid", "wonderland", "cyberpunk", "jungle"]

def get_theme_colors(theme):
    if theme == "wonderland":
        return {
            "bg_center": "#a8c0ff", "bg_edge": "#3f2b96",   
            "platform": "#8E44AD", "bridge": "#ff00ff", "glass": "rgba(255, 200, 255, 0.3)"
        }
    elif theme == "cyberpunk":
        return {
            "bg_center": "#003300", "bg_edge": "#000000",   
            "platform": "#001100", "bridge": "#00ff00", "glass": "rgba(0, 255, 0, 0.15)" # Matrix stil
        }
    elif theme == "jungle":
        return {
            "bg_center": "#88aa00", "bg_edge": "#223300",   
            "platform": "#5c4033", "bridge": "#d2b48c", "glass": "rgba(255, 255, 255, 0.15)" # Træbro look
        }
    else: # Default: squid
        return {
            "bg_center": "#444444", "bg_edge": "#111111",
            "platform": "#333333", "bridge": "#00ffff", "glass": "rgba(200, 255, 255, 0.2)"
        }

def get_player_svg(theme):
    if theme == "wonderland":
        # Alice (Blå kjole)
        return """
            <circle cx="0" cy="0" r="10" fill="#ffccaa" />
            <path d="M -10,10 L 10,10 L 15,40 L -15,40 Z" fill="#3498db" />
            <line x1="-10" y1="15" x2="-20" y2="30" stroke="#ffccaa" stroke-width="3" />
            <line x1="10" y1="15" x2="20" y2="30" stroke="#ffccaa" stroke-width="3" />
            <line x1="-5" y1="40" x2="-5" y2="60" stroke="white" stroke-width="3" />
            <line x1="5" y1="40" x2="5" y2="60" stroke="white" stroke-width="3" />
        """
    elif theme == "cyberpunk":
        # Hacker (Grøn data-mand)
        return """
            <rect x="-10" y="-15" width="20" height="20" fill="none" stroke="#0f0" stroke-width="2" />
            <line x1="-5" y1="-8" x2="5" y2="-8" stroke="#0f0" stroke-width="2" />
            <line x1="0" y1="5" x2="0" y2="40" stroke="#0f0" stroke-width="2" />
            <line x1="0" y1="20" x2="-15" y2="35" stroke="#0f0" stroke-width="2" />
            <line x1="0" y1="20" x2="15" y2="35" stroke="#0f0" stroke-width="2" />
            <line x1="0" y1="40" x2="-10" y2="60" stroke="#0f0" stroke-width="2" />
            <line x1="0" y1="40" x2="10" y2="60" stroke="#0f0" stroke-width="2" />
        """
    elif theme == "jungle":
        # Eventyrer (Brun hat)
        return """
            <circle cx="0" cy="0" r="10" fill="#ffccaa" />
            <path d="M -15,-5 L 15,-5 L 10,-15 L -10,-15 Z" fill="#8B4513" /> <line x1="0" y1="10" x2="0" y2="40" stroke="#d2b48c" stroke-width="4" /> <line x1="0" y1="20" x2="-15" y2="35" stroke="#ffccaa" stroke-width="3" />
            <line x1="0" y1="20" x2="15" y2="35" stroke="#ffccaa" stroke-width="3" />
            <line x1="0" y1="40" x2="-10" y2="60" stroke="#5c4033" stroke-width="3" />
            <line x1="0" y1="40" x2="10" y2="60" stroke="#5c4033" stroke-width="3" />
        """
    else:
        # Squid Stickman
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
    if theme == "wonderland":
        # Cheshire Cat
        return """
            <path d="M -25,0 Q -35,-40 0,-50 Q 35,-40 25,0 Q 12,20 -25,0" fill="#8e44ad" opacity="0.9" filter="url(#glow)"/>
            <path d="M -20,-45 L -25,-60 L -10,-50 Z" fill="#8e44ad" />
            <path d="M 20,-45 L 25,-60 L 10,-50 Z" fill="#8e44ad" />
            <path d="M -15,-10 Q 0,10 15,-10" stroke="white" stroke-width="3" fill="none" />
            <circle cx="-10" cy="-25" r="5" fill="#f1c40f" />
            <circle cx="10" cy="-25" r="5" fill="#f1c40f" />
        """
    elif theme == "cyberpunk":
        # Glitch Virus (Rød og kantet)
        return """
            <path d="M -20,0 L -30,-30 L 0,-50 L 30,-30 L 20,0 L 0,20 Z" fill="#ff0000" opacity="0.8" filter="url(#glow)"/>
            <rect x="-15" y="-35" width="10" height="10" fill="black" />
            <rect x="5" y="-35" width="10" height="10" fill="black" />
            <path d="M -25,-10 L -40,-20 M 25,-10 L 40,-20 M 0,20 L 0,40" stroke="red" stroke-width="2" />
        """
    elif theme == "jungle":
        # Kæmpe Edderkop
        return """
            <circle cx="0" cy="-20" r="20" fill="#111" /> <circle cx="0" cy="-45" r="12" fill="#111" /> <path d="M -10,-20 L -35,-40 M -10,-10 L -40,0 M -10,0 L -35,30" stroke="black" stroke-width="4" fill="none" />
            <path d="M 10,-20 L 35,-40 M 10,-10 L 40,0 M 10,0 L 35,30" stroke="black" stroke-width="4" fill="none" />
            <circle cx="-4" cy="-48" r="2" fill="red" />
            <circle cx="4" cy="-48" r="2" fill="red" />
        """
    else:
        # Shadow Blob
        return """
            <path d="M -25,0 Q -35,-50 0,-70 Q 35,-50 25,0 Q 12,20 -25,0" fill="black" opacity="0.95" filter="url(#glow)"/>
            <circle cx="-10" cy="-40" r="5" fill="red" />
            <circle cx="10" cy="-40" r="5" fill="red" />
        """
