import streamlit as st
import json

def render_js_game(scenario_json):
    """
    Genererer en komplet HTML/JS spil-pakke baseret på scenariet.
    """
    # Vi konverterer Python-data til JSON streng som JS kan læse
    game_data = json.dumps(scenario_json)
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{ margin: 0; background: #000; color: white; font-family: monospace; overflow: hidden; }}
        #game-container {{ position: relative; width: 600px; height: 450px; border: 2px solid #444; border-radius: 10px; background: radial-gradient(circle, #444 0%, #111 100%); margin: 0 auto; }}
        svg {{ width: 100%; height: 350px; display: block; }}
        #ui-layer {{ height: 100px; padding: 10px; background: #222; display: flex; flex-direction: column; align-items: center; justify-content: center; border-top: 2px solid #444; }}
        .btn {{ background: #111; color: cyan; border: 1px solid cyan; padding: 10px 20px; margin: 5px; cursor: pointer; font-size: 16px; width: 200px; transition: 0.2s; }}
        .btn:hover {{ background: #004444; }}
        #status-bar {{ position: absolute; top: 10px; left: 10px; right: 10px; display: flex; justify-content: space-between; font-size: 18px; font-weight: bold; pointer-events: none; }}
        #overlay {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 10; display: none; }}
        .overlay-msg {{ font-size: 30px; color: red; margin-bottom: 20px; text-align: center; }}
        .code-box {{ font-size: 24px; color: lime; border: 2px dashed lime; padding: 10px; margin-top: 10px; }}
    </style>
    </head>
    <body>

    <div id="game-container">
        <div id="status-bar">
            <span id="lives-display">❤️❤️❤️</span>
            <span id="timer-display">TID: 20.0s</span>
        </div>

        <svg id="game-canvas">
            <rect x="0" y="200" width="100" height="150" fill="#333" />
            <rect x="500" y="200" width="100" height="150" fill="#333" />
            <line x1="100" y1="205" x2="500" y2="205" stroke="cyan" stroke-width="4" />
            <line x1="100" y1="235" x2="500" y2="235" stroke="cyan" stroke-width="4" />
            <g id="panels" fill="rgba(0,255,255,0.2)"></g>
            
            <g id="player" transform="translate(50, 150)">
                <circle cx="0" cy="0" r="12" fill="none" stroke="#0f0" stroke-width="2" />
                <line x1="0" y1="12" x2="0" y2="40" stroke="#0f0" stroke-width="2" />
                <line x1="0" y1="20" x2="-15" y2="35" stroke="#0f0" stroke-width="2" />
                <line x1="0" y1="20" x2="15" y2="35" stroke="#0f0" stroke-width="2" />
                <line x1="0" y1="40" x2="-10" y2="60" stroke="#0f0" stroke-width="2" />
                <line x1="0" y1="40" x2="10" y2="60" stroke="#0f0" stroke-width="2" />
            </g>

            <g id="monster" transform="translate(20, 140)">
                <path d="M -20,0 Q -30,-40 0,-60 Q 30,-40 20,0 Q 10,20 -20,0" fill="black" opacity="0.9" />
                <circle cx="-8" cy="-35" r="4" fill="red" />
                <circle cx="8" cy="-35" r="4" fill="red" />
            </g>
        </svg>

        <div id="ui-layer">
            <div id="question-text" style="margin-bottom: 10px; font-weight:bold;">Klar?</div>
            <div style="display:flex;">
                <button id="btn1" class="btn" onclick="checkAnswer(0)">Start</button>
                <button id="btn2" class="btn" onclick="checkAnswer(1)" style="display:none;">-</button>
            </div>
        </div>

        <div id="overlay">
            <div class="overlay-msg" id="overlay-text">GAME OVER</div>
            <button class="btn" id="restart-btn" onclick="startGame()">Prøv Igen</button>
            <div id="win-code" style="display:none;">
                <div>Indtast denne kode i Python:</div>
                <div class="code-box">SEJR-456</div>
            </div>
        </div>
    </div>

    <script>
        // DATA FRA PYTHON
        const gameData = {game_data};
        const room = gameData.rooms[0];
        const steps = room.steps;
        const totalTime = room.time_limit;

        // TILSTAND
        let currentStep = 0;
        let lives = 3;
        let startTime = 0;
        let isPlaying = false;
        let animationFrame;
        let playerX = 50; // Start position
        
        // ELEMENTER
        const playerEl = document.getElementById('player');
        const monsterEl = document.getElementById('monster');
        const timeEl = document.getElementById('timer-display');
        const livesEl = document.getElementById('lives-display');
        const qText = document.getElementById('question-text');
        const btn1 = document.getElementById('btn1');
        const btn2 = document.getElementById('btn2');
        const overlay = document.getElementById('overlay');
        const overlayText = document.getElementById('overlay-text');
        const winCodeDiv = document.getElementById('win-code');
        const restartBtn = document.getElementById('restart-btn');

        // TEGN PANELER
        const panelsGroup = document.getElementById('panels');
        for(let i=0; i<4; i++) {{
            let rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
            rect.setAttribute("x", 110 + (i*100));
            rect.setAttribute("y", 205);
            rect.setAttribute("width", 80);
            rect.setAttribute("height", 30);
            panelsGroup.appendChild(rect);
        }}

        function startGame() {{
            currentStep = 0;
            startTime = Date.now();
            isPlaying = true;
            playerX = 50; // Reset player pos
            updatePlayerPos();
            overlay.style.display = 'none';
            lives = 3; // Eller behold liv fra Python? Lad os resette her for JS-flow
            livesEl.innerHTML = "❤️❤️❤️";
            
            showQuestion();
            gameLoop();
        }}

        function showQuestion() {{
            if (currentStep >= steps.length) {{
                winGame();
                return;
            }}
            let q = steps[currentStep];
            qText.innerText = q.q;
            btn1.innerText = q.options[0];
            btn2.innerText = q.options[1];
            btn1.style.display = "block";
            btn2.style.display = "block";
            
            // Flyt spiller visuelt
            // Start: 50. Panel 1: 150. Panel 2: 250... Sikkerhed: 550
            playerX = 50 + (currentStep * 100);
            if (currentStep > 0) playerX += 50; // Justering til midten af panel
            updatePlayerPos();
        }}

        function checkAnswer(optionIdx) {{
            if (!isPlaying) {{
                if (optionIdx === 0) startGame(); // Start knap funktion
                return;
            }}

            let q = steps[currentStep];
            let choice = q.options[optionIdx];

            if (choice === q.correct) {{
                currentStep++;
                showQuestion();
            }} else {{
                takeDamage("Forkert svar!");
            }}
        }}

        function takeDamage(reason) {{
            lives--;
            livesEl.innerHTML = "❤️".repeat(lives) + "🖤".repeat(3-lives);
            if (lives <= 0) {{
                gameOver(reason);
            }} else {{
                // Lille straf: Reset step? Eller bare mist liv?
                // Lad os resette til start af broen for drama
                currentStep = 0;
                showQuestion();
                // Visuelt flash
                document.body.style.background = "#500";
                setTimeout(() => document.body.style.background = "#000", 100);
            }}
        }}

        function updatePlayerPos() {{
            playerEl.setAttribute('transform', `translate(${{playerX}}, 150)`);
        }}

        function gameLoop() {{
            if (!isPlaying) return;

            let elapsed = (Date.now() - startTime) / 1000;
            let timeLeft = totalTime - elapsed;

            // Opdater timer tekst
            timeEl.innerText = `TID: ${{Math.max(0, timeLeft).toFixed(1)}}s`;

            // 1. FLYT MONSTER (SMOOTH)
            // Monster starter ved 20. Skal fange spiller ved playerX præcis når tid er gået.
            // MEN playerX ændrer sig.
            
            // Simpel logik: Monster bevæger sig med konstant hastighed mod spilleren
            // Hastighed = Distance / Tid_Tilbage
            
            // Faktisk, for at det ser "jagtende" ud:
            // Monster Position = StartPos + (TotalDist * (Elapsed / TotalTime))
            // Det betyder monsteret altid er "på vej" og når frem ved 100%
            
            let monsterStart = 20;
            // Målet er spillerens nuværende position
            let target = playerX; 
            
            // Hvor langt burde monsteret være i % af tiden?
            let percent = elapsed / totalTime;
            
            let monsterCurrent = monsterStart + ((target - monsterStart) * percent);
            
            // Tegn monster
            monsterEl.setAttribute('transform', `translate(${{monsterCurrent}}, 140)`);

            // Tjek om tiden er gået
            if (timeLeft <= 0) {{
                // Animation slut - monster er ved spiller
                gameOver("Tiden er gået! Monsteret fangede dig.");
            }} else {{
                requestAnimationFrame(gameLoop);
            }}
        }}

        function gameOver(msg) {{
            isPlaying = false;
            overlay.style.display = "flex";
            overlayText.innerText = msg;
            overlayText.style.color = "red";
            winCodeDiv.style.display = "none";
            restartBtn.style.display = "block";
            
            // Fald animation
            playerEl.setAttribute('transform', `translate(${{playerX}}, 400)`); // Drop
        }}

        function winGame() {{
            isPlaying = false;
            overlay.style.display = "flex";
            overlayText.innerText = "DU KLAREDE DET!";
            overlayText.style.color = "lime";
            winCodeDiv.style.display = "block";
            restartBtn.style.display = "none";
            
            // Spiller til sikkerhed
            playerEl.setAttribute('transform', `translate(550, 150)`);
        }}
        
        // Initielt setup (Før start trykkes)
        btn1.innerText = "START SPIL";
        btn2.style.display = "none";
        qText.innerText = "Tryk start når du er klar...";

    </script>
    </body>
    </html>
    """
    return html_code
