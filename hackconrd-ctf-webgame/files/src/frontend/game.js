const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

// Estado
let ws;
let myId = null;
let myMoney = 0;
let players = {};
let keys = {};

const SPEED = 4;
const SIZE = 48; // Tamaño de los sprites

// Elementos UI
const loginScreen = document.getElementById("login-screen");
const joinBtn = document.getElementById("join-btn");
const statsPanel = document.getElementById("stats-panel");
const chatPanel = document.getElementById("chat-panel");
const vControls = document.getElementById("virtual-controls");
const shopPanel = document.getElementById("shop-panel");

// Assets Visuales (Pixel Art Originales y sin copyright)
const playerImg = new Image();
playerImg.src = "/game/assets/player.png";

const merchantImg = new Image();
merchantImg.src = "/game/assets/merchant.png";

const npcShop = { x: 650, y: 150, size: 64 };

// Audio
const sfxCoin = new Audio("/game/assets/coin.wav");
sfxCoin.volume = 0.5;
const sfxError = new Audio("/game/assets/error.wav");
sfxError.volume = 0.5;
const bgm = new Audio("/game/assets/bgm.wav");
bgm.loop = true;
bgm.volume = 0.25;

function playSound(type) {
    if (type === 'coin') {
        sfxCoin.currentTime = 0;
        sfxCoin.play().catch(e => console.log("Audio prevented", e));
    } else if (type === 'error') {
        sfxError.currentTime = 0;
        sfxError.play().catch(e => console.log("Audio prevented", e));
    }
}

joinBtn.onclick = () => {
    myId = document.getElementById("username-input").value.trim();
    if (myId) {
        initGame();
    }
};

function initGame() {
    loginScreen.style.display = "none";
    statsPanel.style.display = "block";
    chatPanel.style.display = "flex";
    vControls.style.display = "flex"; // Mostrar botones
    document.getElementById("player-name").innerText = myId;

    bgm.play().catch(e => console.log("BGM prevented", e));

    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    ws = new WebSocket(`${protocol}://${window.location.host}/ws/${myId}`);

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        switch (data.type) {
            case "init":
                data.players.forEach(p => players[p.id] = p);
                requestAnimationFrame(gameLoop);
                break;
            case "player_joined":
                players[data.player.id] = data.player;
                addChatMessage("SISTEMA", `${data.player.id} se conectó.`, "#3498db");
                break;
            case "player_left":
                delete players[data.id];
                addChatMessage("SISTEMA", `${data.id} se desconectó.`, "#e74c3c");
                break;
            case "player_moved":
                if (players[data.id]) { 
                    players[data.id].x = data.x; 
                    players[data.id].y = data.y; 
                }
                break;
            case "chat":
                addChatMessage(data.id, data.text, data.color);
                break;
            case "system_message":
                addChatMessage("SISTEMA", data.text, "#f1c40f");
                break;
            case "update_stats":
                if (data.money > myMoney) playSound('coin');
                myMoney = data.money;
                document.getElementById("player-money").innerText = myMoney;
                break;
        }
    };
}

// Input de Teclado
window.addEventListener("keydown", (e) => {
    if (document.activeElement === document.getElementById("chat-input")) return;
    const k = e.key.toLowerCase();
    keys[k] = true;
    if (k === "e") checkInteractions();
});
window.addEventListener("keyup", (e) => { 
    keys[e.key.toLowerCase()] = false; 
});

// Lógica de los Botones Virtuales en Pantalla
const bindVirtualButton = (id, key) => {
    const btn = document.getElementById(id);
    btn.addEventListener("mousedown", () => keys[key] = true);
    btn.addEventListener("mouseup", () => keys[key] = false);
    btn.addEventListener("mouseleave", () => keys[key] = false);
    btn.addEventListener("touchstart", (e) => { e.preventDefault(); keys[key] = true; });
    btn.addEventListener("touchend", (e) => { e.preventDefault(); keys[key] = false; });
};

bindVirtualButton("btn-up", "w");
bindVirtualButton("btn-down", "s");
bindVirtualButton("btn-left", "a");
bindVirtualButton("btn-right", "d");

const btnInteract = document.getElementById("btn-interact");
btnInteract.addEventListener("mousedown", checkInteractions);
btnInteract.addEventListener("touchstart", (e) => { 
    e.preventDefault(); 
    checkInteractions(); 
});

// Chat
const chatInput = document.getElementById("chat-input");
chatInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter" && chatInput.value.trim() !== "") {
        ws.send(JSON.stringify({ action: "chat", text: chatInput.value }));
        chatInput.value = "";
    }
});

function addChatMessage(sender, text, color) {
    const msg = document.createElement("div");
    msg.innerHTML = `<span style="color:${color};">[${sender}]</span> ${text}`;
    const cm = document.getElementById("chat-messages");
    cm.appendChild(msg);
    cm.scrollTop = cm.scrollHeight;
}

// Interacción con Mercader
function checkInteractions() {
    const me = players[myId];
    if (!me) return;
    // Centro del jugador al centro del npc
    const dist = Math.hypot((me.x + SIZE/2) - (npcShop.x + npcShop.size/2), (me.y + SIZE/2) - (npcShop.y + npcShop.size/2));
    if (dist < 80) {
        openShop();
    } else {
        playSound('error');
        addChatMessage("INFO", "Estás muy lejos del mercader para interactuar.", "#95a5a6");
    }
}

const shopItems = [
    { id: "potion", name: "Poción HP", price: 10 },
    { id: "sword", name: "Espada Básica", price: 150 },
    { id: "flag", name: "Bandera Secreta", price: 999999 }
];

function openShop() {
    shopPanel.style.display = "block";
    const container = document.getElementById("shop-items");
    container.innerHTML = "";
    shopItems.forEach(item => {
        container.innerHTML += `
            <div class="shop-item">
                <span>${item.name} <br><span style="color:#2ecc71;">$${item.price}</span></span>
                <div>
                    <input type="number" id="qty-${item.id}" value="1">
                    <button onclick="buyItem('${item.id}')">COMPRAR</button>
                </div>
            </div>`;
    });
}

function closeShop() { 
    shopPanel.style.display = "none"; 
}

// Handler de compra
window.buyItem = function(itemId) {
    const qtyInput = document.getElementById(`qty-${itemId}`);
    const qty = parseInt(qtyInput.value); 
    ws.send(JSON.stringify({ action: "buy", item_id: itemId, quantity: qty }));
};

// Main Game Loop
function gameLoop() {
    if (!players[myId]) return;
    let me = players[myId];
    let moved = false;

    if ((keys["arrowup"] || keys["w"]) && me.y > 0) { me.y -= SPEED; moved = true; }
    if ((keys["arrowdown"] || keys["s"]) && me.y < canvas.height - SIZE) { me.y += SPEED; moved = true; }
    if ((keys["arrowleft"] || keys["a"]) && me.x > 0) { me.x -= SPEED; moved = true; }
    if ((keys["arrowright"] || keys["d"]) && me.x < canvas.width - SIZE) { me.x += SPEED; moved = true; }

    if (moved) ws.send(JSON.stringify({ action: "move", x: me.x, y: me.y }));

    draw();
    requestAnimationFrame(gameLoop);
}

// Función para pintar un suelo retro tipo cuadriculado (césped de GBA)
const drawBackground = () => {
    ctx.fillStyle = "#78a252"; // Color base césped
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#6b914a"; // Color cuadros oscuros
    for (let i = 0; i < canvas.width; i += 40) {
        for (let j = 0; j < canvas.height; j += 40) {
            if ((i / 40 + j / 40) % 2 === 0) {
                ctx.fillRect(i, j, 40, 40);
            }
        }
    }
};

function draw() {
    drawBackground();

    // Sombra del Mercader
    ctx.fillStyle = "rgba(0, 0, 0, 0.3)";
    ctx.beginPath(); 
    ctx.ellipse(npcShop.x + npcShop.size/2, npcShop.y + npcShop.size - 5, 25, 10, 0, 0, Math.PI * 2); 
    ctx.fill();

    // Dibujar Mercader
    if (merchantImg.complete) {
        ctx.drawImage(merchantImg, npcShop.x, npcShop.y, npcShop.size, npcShop.size);
    } else {
        ctx.fillStyle = "#000"; ctx.fillRect(npcShop.x, npcShop.y, npcShop.size, npcShop.size);
    }
    
    // Texto del mercader
    ctx.fillStyle = "#f1c40f"; 
    ctx.font = "10px 'Press Start 2P'"; 
    ctx.textAlign = "center";
    ctx.fillText("MERCADER", npcShop.x + npcShop.size/2, npcShop.y - 10);

    // Dibujar Jugadores
    for (let id in players) {
        let p = players[id];
        
        // Sombra de los jugadores
        ctx.fillStyle = "rgba(0, 0, 0, 0.3)";
        ctx.beginPath(); 
        ctx.ellipse(p.x + SIZE/2, p.y + SIZE - 5, 15, 6, 0, 0, Math.PI * 2); 
        ctx.fill();

        if (playerImg.complete) {
            ctx.drawImage(playerImg, p.x, p.y, SIZE, SIZE);
        } else {
            ctx.fillStyle = p.color; 
            ctx.fillRect(p.x, p.y, SIZE, SIZE);
        }
        
        ctx.fillStyle = p.color;
        ctx.fillText(p.id, p.x + SIZE/2, p.y - 5);
    }
}