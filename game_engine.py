import streamlit as st
import json

def render_js_game(scenario_json):
    """
    Genererer HTML/JS spil.
    Version: Perfect Timing & Sound Control
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
            20% {{ fill: white; opacity: 0.8; }}
            100% {{ opacity: 0; }}
        }}
        .shattering {{ animation: shatter 0.3s forwards; }}
        
        .panel-normal {{ fill: rgba(0,255,255,0.2); stroke: cyan; stroke-width: 1; }}
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

        // 1. Initialiser paneler
        let panels = [];
        for(let i=0; i<4; i++) {{
            let rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
            // Beregning af panel positioner:
            // Panel 1 start: 110. Bredde 80. Center = 150.
            // Panel 2 start: 210. Bredde 80. Center = 250.
            rect.setAttribute("x", 110 + (i*100));
            rect.setAttribute("y", 205);
            rect.setAttribute("width", 80);
            rect.setAttribute("height", 30);
            rect.setAttribute("class", "panel-normal");
            panelsGroup.appendChild(rect);
            panels.push(rect);
        }}

        // Hjælpefunktion til at stoppe lyde
        function stopSounds() {{
            [sfxGlass, sfxScream, sfxWin].forEach(s => {{
                s.pause();
                s.currentTime = 0;
            }});
        }}

        function startGame() {{
            stopSounds(); // STOP GAMLE SKRIG
            
            currentStep = 0;
            isPlaying = true;
            timeRemaining = totalTime;
            lastFrameTime = performance.now();
            
            // Start Position: Hop direkte ud på første panel!
            // Start platform er x=50. Første panel center er x=150.
            playerX = 150; 
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
            stopSounds();
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
            
            // Opdater spiller position (allerede sat i checkAnswer eller startGame)
            // Vi sikrer os bare at den passer
            let targetX = 150 + (currentStep * 100);
            playerX = targetX;
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

            enableButtons(false);

            if (choice === q.correct) {{
                // KORREKT: Hop til næste panel
                currentStep++;
                // Hvis vi er færdige (step 4), hopper vi til safety (550), ellers næste panel
                if (currentStep < 4) {{
                    playerX = 150 + (currentStep * 100);
                }} else {{
                    playerX = 550; // Safety
                }}
                updatePositions();
                showQuestion(); 
                enableButtons(true);
                
            }} else {{
                // FORKERT: Dødsproces
                // Vi står allerede på det "forkerte" panel (fordi vi hopper derud ved start/forrige svar)
                
                // 1. Vent lille øjeblik (Suspense)
                setTimeout(() => {{
                    breakGlassAndDie("Forkert svar!");
                }}, 300);
            }}
        }}

        function breakGlassAndDie(reason) {{
            let panel = panels[currentStep];
            
            // 1. Visuel splintring & Lyd
            if(panel) {{
                panel.classList.add('shattering');
                sfxGlass.play().catch(e => console.log("Audio error:", e));
            }}
            
            // 2. Fald & Skrig (lidt forsinket for at matche glasbrud)
            setTimeout(() => {{
                sfxScream.play().catch(e => console.log("Audio error:", e));
                
                // Fald animation
                playerEl.setAttribute('transform', `translate(${{playerX}}, 450)`); 
                
                // 3. Game Over skærm
                setTimeout(() => {{
                    playerDie(reason);
                }}, 1500);
                
            }}, 400); 
        }}

        function updatePositions() {{
            // Direkte opdatering
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

            // Monster Jagt
            let targetX = playerX;
            let distance = targetX - monsterX;
            let safeTime = Math.max(timeRemaining, 0.01);
            let speed = distance / safeTime;
            
            monsterX += speed * dt;
            
            monsterEl.setAttribute('transform', `translate(${{monsterX}}, 140)`);

            // Tjek tid/fangst (Giv lidt buffer på 10px)
            if (timeRemaining <= 0 || monsterX >= (playerX - 10)) {{
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
            stopSounds();
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
