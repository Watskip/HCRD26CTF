from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import json
import uuid

app = FastAPI()

# Servir archivos estáticos del frontend
app.mount("/game", StaticFiles(directory="frontend", html=True), name="frontend")

@app.get("/")
async def root():
    return FileResponse("frontend/index.html")

class Player(BaseModel):
    id: str
    x: int
    y: int
    color: str
    money: int = 0
    inventory: list = []

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.players: dict[str, Player] = {}

    async def connect(self, websocket: WebSocket, player_id: str):
        await websocket.accept()
        self.active_connections[player_id] = websocket
        
        # Color aleatorio para cada jugador
        import random
        color = f"hsl({random.randint(0, 360)}, 70%, 50%)"
        
        self.players[player_id] = Player(id=player_id, x=400, y=300, color=color)
        
        # Enviar el estado actual de todos al nuevo jugador
        await self.send_personal_message(
            {"type": "init", "id": player_id, "players": [p.dict() for p in self.players.values()]}, 
            player_id
        )
        # Avisar a los demás del nuevo jugador
        await self.broadcast({"type": "player_joined", "player": self.players[player_id].dict()}, exclude=player_id)

    def disconnect(self, player_id: str):
        if player_id in self.active_connections:
            del self.active_connections[player_id]
        if player_id in self.players:
            del self.players[player_id]

    async def send_personal_message(self, message: dict, player_id: str):
        if player_id in self.active_connections:
            await self.active_connections[player_id].send_text(json.dumps(message))

    async def broadcast(self, message: dict, exclude: str = None):
        dead_connections = []
        for pid, connection in self.active_connections.items():
            if pid != exclude:
                try:
                    await connection.send_text(json.dumps(message))
                except RuntimeError:
                    dead_connections.append(pid)
        
        for pid in dead_connections:
             self.disconnect(pid)

manager = ConnectionManager()

# --- LÓGICA DEL JUEGO / TIENDA ---
# Los items disponibles en la tienda del juego
SHOP_ITEMS = {
    "potion": {"price": 10, "name": "Poción de Vida"},
    "sword": {"price": 150, "name": "Espada Básica"},
    "flag": {"price": 999999, "name": "Bandera Secreta"} 
}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            action = message.get("action")
            
            if action == "move":
                if client_id in manager.players:
                    manager.players[client_id].x = message.get("x", manager.players[client_id].x)
                    manager.players[client_id].y = message.get("y", manager.players[client_id].y)
                    # Retransmitir movimiento a todos menos al que lo originó
                    await manager.broadcast(
                        {"type": "player_moved", "id": client_id, "x": manager.players[client_id].x, "y": manager.players[client_id].y},
                        exclude=client_id
                    )
            
            elif action == "chat":
                msg = message.get("text", "")
                await manager.broadcast({"type": "chat", "id": client_id, "text": msg, "color": manager.players[client_id].color})

            elif action == "buy":
                item_id = message.get("item_id")
                quantity = int(message.get("quantity", 1))
                
                if item_id in SHOP_ITEMS:
                    player = manager.players[client_id]
                    item = SHOP_ITEMS[item_id]
                    total_cost = item["price"] * quantity
                    
                    if player.money >= total_cost:
                        player.money -= total_cost
                        
                        # Si compró la bandera y tiene el dinero
                        if item_id == "flag" and quantity > 0:
                            flag = "HCRD{bU51n3s5_l0g1c_unD3rfl0w_m4st3r}"
                            await manager.send_personal_message({
                                "type": "system_message", 
                                "text": f"¡Increíble! Has comprado la reliquia. Tu flag es: {flag}"
                            }, client_id)
                        else:
                             await manager.send_personal_message({
                                "type": "system_message", 
                                "text": f"Has comprado {quantity}x {item['name']}. Balance: ${player.money}"
                            }, client_id)
                            
                        # Notificar actualización de estado
                        await manager.send_personal_message({
                            "type": "update_stats", "money": player.money
                        }, client_id)
                    else:
                        await manager.send_personal_message({
                                "type": "system_message", 
                                "text": "No tienes suficiente dinero."
                            }, client_id)

    except WebSocketDisconnect:
        manager.disconnect(client_id)
        await manager.broadcast({"type": "player_left", "id": client_id})
