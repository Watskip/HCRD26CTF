const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// Game State
let gameState = 'START'; // START, PLAYING, GAMEOVER
let score = 0;
let frames = 0;
let animationId;

// Audio
const sfxJump = new Audio('assets/jump.wav');
const sfxCrash = new Audio('assets/crash.wav');
const bgm = new Audio('assets/bgm.wav');
bgm.loop = true;
bgm.volume = 0.3;

// Game Config
const GRAVITY = 0.32;
const LIFT = -8;
const TERMINAL_VELOCITY = 10;

// Player Ship (Neon Triangle)
const player = {
    x: 150,
    y: 300,
    velocity: 0,
    size: 20,
    color: '#0ff',
    particles: []
};

// Obstacles
let obstacles = [];
const INITIAL_OBSTACLE_SPEED = 3;
const SPEED_RAMP_AFTER_MS = 3000;
const SPEED_RAMP_AMOUNT = 2.5; // applied once after ramp delay (e.g. 3 → 5.5)
let obstacleSpeed = INITIAL_OBSTACLE_SPEED;
let obstacleSpawnRate = 100;
let gameStartMs = 0;
let speedRampApplied = false;
const DROP_GRACE_MS = 500;
let dropHoldUntilMs = 0;

// The Secret / Obfuscated Data
const _0x1a2b = [35, 40, 57, 47, 16, 5, 88, 91, 5, 52, 12, 7, 90, 15, 88, 25, 52, 91, 29, 88, 25, 25, 90, 15, 88, 52, 6, 95, 24, 31, 88, 25, 22];

function _0xDecrypt(score) {
    if (score !== 50) return "";
    let res = "";
    let key = score ^ 89; // 50 ^ 89 = 107
    for(let i=0; i<_0x1a2b.length; i++) {
        res += String.fromCharCode(_0x1a2b[i] ^ key);
    }
    return res;
}

// Input Handling
let isBoosting = false;

function handleInputDown(e) {
    if (e.type === 'keydown' && e.code === 'Space') {
        e.preventDefault();
        if (e.repeat) return;
        if (gameState === 'START') {
            startGame();
            return;
        }
        if (gameState === 'GAMEOVER') {
            resetGame();
            return;
        }
    }
    if (e.type === 'keydown' && e.code !== 'Space') return;
    if (gameState === 'PLAYING') {
        isBoosting = true;
    }
}

function handleInputUp(e) {
    if(e.type === 'keyup' && e.code !== 'Space') return;
    isBoosting = false;
}

window.addEventListener('keydown', handleInputDown);
window.addEventListener('keyup', handleInputUp);
window.addEventListener('mousedown', handleInputDown);
window.addEventListener('mouseup', handleInputUp);
window.addEventListener('touchstart', handleInputDown);
window.addEventListener('touchend', handleInputUp);

window._DEBUG_GOD_MODE_ = false;

function startGame() {
    document.getElementById('start-screen').style.display = 'none';
    resetGame();
    bgm.play().catch(e => console.log('Audio blocked'));
}

function resetGame() {
    isBoosting = false;
    player.y = canvas.height / 2;
    player.velocity = 0;
    player.particles = [];
    obstacles = [];
    score = 0;
    frames = 0;
    obstacleSpeed = INITIAL_OBSTACLE_SPEED;
    obstacleSpawnRate = 100;
    gameStartMs = performance.now();
    speedRampApplied = false;
    dropHoldUntilMs = gameStartMs + DROP_GRACE_MS;
    gameState = 'PLAYING';
    document.getElementById('game-over-screen').style.display = 'none';
    document.getElementById('flag-container').innerText = "";
    updateScore();
    if(animationId) cancelAnimationFrame(animationId);
    gameLoop();
}

function updateScore() {
    let s = score.toString();
    while(s.length < 4) s = "0" + s;
    document.getElementById('score-display').innerText = s;
}

function spawnObstacle() {
    // Math to make it increasingly impossible
    let gap = 200 - (score * 2);
    if(gap < 120) gap = 120; // Absolute minimum gap
    
    let minHeight = 50;
    let maxPos = canvas.height - minHeight - gap;
    let topHeight = Math.floor(Math.random() * maxPos) + minHeight;
    
    obstacles.push({
        x: canvas.width,
        y: 0,
        width: 40,
        height: topHeight,
        passed: false
    });
    
    obstacles.push({
        x: canvas.width,
        y: topHeight + gap,
        width: 40,
        height: canvas.height - topHeight - gap,
        passed: true // Only count the top one for score
    });
}

function updatePhysics() {
    const gravityOn = performance.now() >= dropHoldUntilMs;
    // Player
    if(isBoosting) {
        player.velocity = LIFT;
        sfxJump.currentTime = 0;
        sfxJump.play().catch(e=>{});
        
        // Particles
        player.particles.push({
            x: player.x - 10,
            y: player.y,
            vx: -Math.random()*5,
            vy: (Math.random()-0.5)*2,
            life: 1.0
        });
    } else if (gravityOn) {
        player.velocity += GRAVITY;
    } else {
        player.velocity = 0;
    }
    
    if(player.velocity > TERMINAL_VELOCITY) player.velocity = TERMINAL_VELOCITY;
    player.y += player.velocity;

    // Floor / Ceiling collision
    if (player.y + player.size > canvas.height || player.y - player.size < 0) {
        if(!window._DEBUG_GOD_MODE_) triggerGameOver();
        else {
            if(player.y - player.size < 0) player.y = player.size;
            if(player.y + player.size > canvas.height) player.y = canvas.height - player.size;
            player.velocity = 0;
        }
    }

    // One-time speed bump after a few seconds of play
    if (!speedRampApplied && performance.now() - gameStartMs >= SPEED_RAMP_AFTER_MS) {
        obstacleSpeed += SPEED_RAMP_AMOUNT;
        speedRampApplied = true;
    }

    // Difficulty ramp (skip frame 0 so initial speed stays low until timers kick in)
    if (frames > 0 && frames % 600 === 0) {
        obstacleSpeed += 1.5;
        if(obstacleSpawnRate > 30) obstacleSpawnRate -= 10;
    }

    // Obstacles
    if (frames % obstacleSpawnRate === 0) {
        spawnObstacle();
    }

    for (let i = 0; i < obstacles.length; i++) {
        let obs = obstacles[i];
        obs.x -= obstacleSpeed;

        // Collision Check
        if (!window._DEBUG_GOD_MODE_) {
            if (
                player.x + player.size > obs.x &&
                player.x - player.size < obs.x + obs.width &&
                player.y + player.size > obs.y &&
                player.y - player.size < obs.y + obs.height
            ) {
                triggerGameOver();
            }
        }

        // Score
        if (obs.x + obs.width < player.x && !obs.passed) {
            score++;
            obs.passed = true;
            updateScore();
            
            // WIN CONDITION
            if(score === 50) {
                triggerWin();
            }
        }
    }

    // Remove off-screen obstacles
    obstacles = obstacles.filter(obs => obs.x + obs.width > 0);
    
    // Update particles
    for(let i=0; i<player.particles.length; i++) {
        let p = player.particles[i];
        p.x += p.vx;
        p.y += p.vy;
        p.life -= 0.05;
    }
    player.particles = player.particles.filter(p => p.life > 0);
}

function triggerGameOver() {
    gameState = 'GAMEOVER';
    sfxCrash.play().catch(e=>{});
    document.getElementById('final-score').innerText = "PUNTAJE: " + score;
    document.getElementById('game-over-screen').style.display = 'block';
    bgm.pause();
}

function triggerWin() {
    gameState = 'GAMEOVER';
    bgm.pause();
    document.getElementById('final-score').innerText = "50 - ANOMALÍA DETECTADA";
    document.getElementById('final-score').style.color = "#0ff";
    
    let flag = _0xDecrypt(score);
    document.getElementById('flag-container').innerText = ">>> " + flag;
    document.getElementById('game-over-screen').style.borderColor = "#0ff";
    document.getElementById('game-over-screen').style.boxShadow = "0 0 30px rgba(0, 255, 255, 0.4)";
    document.getElementById('game-over-screen').querySelector('h1').innerText = "SISTEMA COMPROMETIDO";
    document.getElementById('game-over-screen').querySelector('h1').style.color = "#0ff";
    document.getElementById('game-over-screen').style.display = 'block';
}

function drawBackground() {
    ctx.fillStyle = '#050510';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw Grid
    ctx.strokeStyle = 'rgba(0, 255, 255, 0.1)';
    ctx.lineWidth = 1;
    
    let offset = (frames * 2) % 40;
    
    ctx.beginPath();
    for(let i = -offset; i < canvas.width; i+= 40) {
        ctx.moveTo(i, 0);
        ctx.lineTo(i, canvas.height);
    }
    for(let j = 0; j < canvas.height; j+= 40) {
        ctx.moveTo(0, j);
        ctx.lineTo(canvas.width, j);
    }
    ctx.stroke();
}

function draw() {
    drawBackground();

    // Draw Particles
    for(let p of player.particles) {
        ctx.fillStyle = `rgba(0, 255, 255, ${p.life})`;
        ctx.fillRect(p.x, p.y, 4, 4);
    }

    // Draw Player
    ctx.fillStyle = player.color;
    ctx.shadowBlur = 15;
    ctx.shadowColor = player.color;
    ctx.beginPath();
    ctx.moveTo(player.x + player.size, player.y);
    ctx.lineTo(player.x - player.size, player.y - player.size);
    ctx.lineTo(player.x - player.size/2, player.y);
    ctx.lineTo(player.x - player.size, player.y + player.size);
    ctx.closePath();
    ctx.fill();
    ctx.shadowBlur = 0;

    // Draw Obstacles
    ctx.fillStyle = '#f0f';
    ctx.shadowBlur = 10;
    ctx.shadowColor = '#f0f';
    for (let obs of obstacles) {
        ctx.fillRect(obs.x, obs.y, obs.width, obs.height);
    }
    ctx.shadowBlur = 0;
}

function gameLoop() {
    if(gameState === 'PLAYING') {
        updatePhysics();
        draw();
        frames++;
        animationId = requestAnimationFrame(gameLoop);
    }
}
