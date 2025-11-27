import streamlit as st
import json

def render_js_game(scenario_json):
    """
    Genererer HTML/JS spil.
    Version: Death Animation & Sound Effects
    """
    game_data = json.dumps(scenario_json)
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{ margin: 0; background: #000; color: white; font-family: monospace; overflow: hidden; user-select: none; }}
        #game-container {{ position: relative; width: 600px; height: 450px; border: 2px solid #444; border-radius: 10px; background: radial-gradient(circle, #444 0%, #111 100%); margin: 0 auto; }}
        svg {{ width: 100%; height: 350px; display: block; }}
        #ui-layer {{ height: 100px; padding: 10px; background: #222; display: flex; flex-direction: column; align-items: center; justify-content: center; border-top: 2px solid #444; }}
        .btn {{ background: #111; color: cyan; border: 1px solid cyan; padding: 10px 20px; margin: 5px; cursor: pointer; font-size: 16px; width: 200px; transition: 0.2s; }}
        .btn:hover {{ background: #004444; }}
        .btn:disabled {{ background: #333; color: #555; border-color: #555; cursor: not-allowed; }}
        #status-bar {{ position: absolute; top: 10px; left: 10px; right: 10px; display: flex; justify-content: space-between; font-size: 18px; font-weight: bold; pointer-events: none; }}
        #overlay {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 10; display: none; }}
        .overlay-msg {{ font-size: 30px; color: red; margin-bottom: 20px; text-align: center; }}
        .code-box {{ font-size: 24px; color: lime; border: 2px dashed lime; padding: 10px; margin-top: 10px; user-select: text; }}
        
        /* Animationer */
        @keyframes shatter {{
            0% {{ fill: rgba(0,255,255,0.2); }}
            50% {{ fill: white; }}
            100% {{ opacity: 0; }}
        }}
        .shattering {{ animation: shatter 0.2s forwards; }}
    </style>
    </head>
    <body>

    <audio id="sfx-glass" src="https://assets.mixkit.co/active_storage/sfx/2515/2515-preview.mp3"></audio>
    <audio id="sfx-scream" src="https://assets.mixkit.co/active_storage/sfx/144/144-preview.mp3"></audio>
    <audio id="sfx-win" src="https://assets.mixkit.co/active_storage/sfx/1435/1435-preview.mp3"></audio>

    <div id="game-container">
        <div id="status-bar">
            <span id="lives-display">❤️❤️❤️</span>
            <span id="timer-display">KLAR?</span>
        </div>

        <svg id="game-canvas">
            <rect x="0" y="200" width="100" height="150" fill="#333" />
            <rect x="500" y="200" width="100" height="150" fill="#333" />
            
            <line x1="100" y1="205" x2="500" y2="205" stroke="cyan" stroke-width="4" />
            <line x1="100" y1="235" x2="500" y2="235" stroke="cyan" stroke-width="4" />
            
            <g id="panels"></g>
            
            <g id="player" transform="translate(50, 150)">
                <circle cx="0" cy="0" r="12" fill="none" stroke="#0f0" stroke-width="2" />
                <line x1="0" y1="12" x2="0" y2="40" stroke="#0f0" stroke-width="2" />
                <line x1="0" y1="20" x2="-15" y2="35" stroke="#0f0" stroke-width="2" />
                <line x1="0" y1="20" x2="15" y2="35" stroke="#0f0" stroke-width="2" />
                <line x1="0" y1="40" x2="-10" y2="60" stroke="#0f0" stroke-width="2" />
                <line x1="0" y1="40" x2="10" y2="60" stroke="#0f0" stroke-width="2" />
                <text x="0" y="-20" fill="#0f0" font-size="10" text-anchor="middle">456</text>
            </g>

            <g id="monster" transform="translate(-100, 140)">
                <path d="M -25,0 Q -35,-50 0,-70 Q 35,-50 25,0 Q 12,20 -25,0" fill="black" opacity="0.95" filter="url(#glow)"/>
                <circle cx="-10" cy="-40" r="5" fill="red" />
                <circle cx="10" cy="-40" r="5" fill="red" />
            </g>
            
            <defs>
                <filter id="glow"><feGaussianBlur stdDeviation="2.5" result="coloredBlur"/><feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
            </defs>
        </svg>

        <div id="ui-layer">
            <div id="question-text" style="margin-bottom: 10px; font-weight:bold;">Tryk Start for at begynde</div>
            <div style="display:flex;">
                <button id="btn1" class="btn" onclick="checkAnswer(0)">Start Level</button>
                <button id="btn2" class="btn" onclick="checkAnswer(1)" style="display:none;">-</button>
            </div>
        </div>

        <div id="overlay">
            <div class="overlay-msg" id="overlay-text">GAME OVER</div>
            <button class="btn" id="restart-btn" onclick="restartLevel()">Prøv Igen (-1 Liv)</button>
            <div id="win-code" style="display:none;">
                <div>KODE TIL NÆSTE RUM:</div>
                <div class="code-box">LEVEL-UP</div>
            </div>
        </div>
    </div>

    <script>
        const gameData = {game_data};
        const room = gameData.rooms[0];
        const steps = room.steps;
        const totalTime = room.time_limit;

        let currentStep = 0;
        let lives = 3;
        let isPlaying = false;
        
        let playerX = 50;
        let monsterX = -70; 
        let timeRemaining = totalTime;
        let lastFrameTime = 0;

        // UI Refs
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
        const panelsGroup = document.getElementById('panels');

        // Sounds
        const sfxGlass = document.getElementById('sfx-glass');
        const sfxScream = document.getElementById('sfx-scream');
        const sfxWin = document.getElementById('sfx-win');

        // Initialiser paneler
        let panels = [];
        for(let i=0; i<4; i++) {{
            let rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
            rect.setAttribute("x", 110 + (i*100));
            rect.setAttribute("y", 205);
            rect.setAttribute("width", 80);
            rect.setAttribute("height", 30);
            rect.setAttribute("fill", "rgba(0,255,255,0.2)");
            rect.setAttribute("stroke", "cyan");
            rect.setAttribute("stroke-width", "1");
            panelsGroup.appendChild(rect);
            panels.push(rect);
        }}

        function startGame() {{
            currentStep = 0;
            isPlaying = true;
            timeRemaining = totalTime;
            lastFrameTime = performance.now();
            
            playerX = 50;
            monsterX = -70; 
            updatePositions();
            
            // Nulstil paneler
            panels.forEach(p => {{
                p.style.display = 'block';
                p.classList.remove('shattering');
            }});
            
            overlay.style.display = 'none';
            livesEl.innerHTML = "❤️".repeat(lives) + "🖤".repeat(3-lives);
            
            enableButtons(true);
            showQuestion();
            requestAnimationFrame(gameLoop);
        }}

        function restartLevel() {{
            lives--;
            if (lives <= 0) {{
                alert("GAME OVER - Du skal genstarte spillet.");
                location.reload();
                return;
            }}
            startGame();
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
            
            // Flyt spiller til FORRIGE sikre position
            // Start: 50. Panel 1: 150. Panel 2: 250...
            // Hvis vi er på step 0, står vi på 50.
            // Hvis vi er på step 1, står vi på 150 (midten af panel 1).
            
            playerX = 50 + (currentStep * 100);
            if (currentStep > 0) playerX += 50;
            
            updatePositions();
        }}

        function enableButtons(enable) {{
            btn1.disabled = !enable;
            btn2.disabled = !enable;
        }}

        function checkAnswer(optionIdx) {{
            if (!isPlaying) {{
                if (optionIdx === 0) startGame();
                return;
            }}

            let q = steps[currentStep];
            let choice = q.options[optionIdx];

            // Deaktiver knapper midlertidigt for effekt
            enableButtons(false);

            if (choice === q.correct) {{
                // KORREKT: Hop til næste panel sikkert
                currentStep++;
                showQuestion(); // Flytter spilleren visuelt i showQuestion
                enableButtons(true);
            }} else {{
                // FORKERT: Hop ud på panelet og DØ
                
                // 1. Beregn hvor spilleren hopper hen (Det forkerte panel)
                // Det er panelet svarende til currentStep
                let targetPanelX = 150 + (currentStep * 100);
                
                // Flyt spiller visuelt
                playerX = targetPanelX;
                updatePositions();
                
                // 2. Vent et øjeblik (Suspense...)
                setTimeout(() => {{
                    breakGlassAndDie("Forkert svar!");
                }}, 600);
            }}
        }}

        function breakGlassAndDie(reason) {{
            // Find det aktuelle panel
            let panel = panels[currentStep];
            
            // 1. Visuel splintring
            if(panel) {{
                panel.classList.add('shattering');
            }}
            
            // 2. Lyd
            sfxGlass.currentTime = 0;
            sfxGlass.play();
            
            setTimeout(() => {{
                sfxScream.currentTime = 0;
                sfxScream.play();
                
                // 3. Fald ned
                playerEl.setAttribute('transform', `translate(${{playerX}}, 450)`); // Drop langt ned
                
                // 4. Game Over skærm
                setTimeout(() => {{
                    playerDie(reason);
                }}, 1000);
                
            }}, 200); // Lille forsinkelse før fald
        }}

        function updatePositions() {{
            // Simpel direkte opdatering (ingen fald her)
            if (isPlaying) {{
                playerEl.setAttribute('transform', `translate(${{playerX}}, 150)`);
            }}
            monsterEl.setAttribute('transform', `translate(${{monsterX}}, 140)`);
        }}

        function gameLoop(timestamp) {{
            if (!isPlaying) return;

            let dt = (timestamp - lastFrameTime) / 1000;
            lastFrameTime = timestamp;

            timeRemaining -= dt;
            timeEl.innerText = `TID: ${{Math.max(0, timeRemaining).toFixed(1)}}s`;

            // Monster Movement (Fysik)
            let targetX = playerX;
            let distance = targetX - monsterX;
            let safeTime = Math.max(timeRemaining, 0.01);
            let speed = distance / safeTime;
            
            monsterX += speed * dt;
            
            // Opdater kun monster her, spiller opdateres ved svar
            monsterEl.setAttribute('transform', `translate(${{monsterX}}, 140)`);

            // Tjek død ved tid
            if (timeRemaining <= 0 || monsterX >= (playerX - 5)) {{
                // Tiden gik -> Monster fangede dig
                // Her falder glasset ikke, man bliver bare "taget"
                playerDie("Skyggen fangede dig!");
            }} else {{
                requestAnimationFrame(gameLoop);
            }}
        }}

        function playerDie(reason) {{
            isPlaying = false;
            overlay.style.display = "flex";
            overlayText.innerText = reason;
            overlayText.style.color = "red";
            winCodeDiv.style.display = "none";
            restartBtn.style.display = "block";
        }}

        function winGame() {{
            isPlaying = false;
            sfxWin.play();
            overlay.style.display = "flex";
            overlayText.innerText = "RUM KLARET!";
            overlayText.style.color = "lime";
            winCodeDiv.style.display = "block";
            restartBtn.style.display = "none";
            playerEl.setAttribute('transform', `translate(550, 150)`);
        }}
    </script>
    </body>
    </html>
    """
    return html_code
