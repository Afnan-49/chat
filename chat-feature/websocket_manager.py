from fastapi import WebSocket, WebSocketDisconnect, Depends
from typing import Dict, List
import json
import asyncio
from auth import get_current_user_ws

class ConnectionManager:
    def __init__(self):
        # chat_room_id: list of connections
        self.active_connections: Dict[int, List[WebSocket]] = {}
        # user_id: chat_room_id
        self.user_rooms: Dict[int, int] = {}

    async def connect(self, websocket: WebSocket, chat_room_id: int, user_id: int):
        await websocket.accept()

        if chat_room_id not in self.active_connections:
            self.active_connections[chat_room_id] = []

        self.active_connections[chat_room_id].append(websocket)
        self.user_rooms[user_id] = chat_room_id

        # Notify others that user joined
        await self.broadcast_to_chat_room(chat_room_id, {
            "type": "user_joined",
            "user_id": user_id,
            "message": f"User {user_id} joined the chat"
        })

    def disconnect(self, websocket: WebSocket, chat_room_id: int, user_id: int):
        if chat_room_id in self.active_connections:
            self.active_connections[room_id].remove(websocket)
            if len(self.active_connections[chat_room_id]) == 0:
                del self.active_connections[chat_room_id]

        if user_id in self.user_rooms:
            del self.user_rooms[user_id]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast_to_room(self, chat_room_id: int, message: dict):
        if chat_room_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[chat_room_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception:
                    disconnected.append(connection)

            # Remove disconnected clients
            for connection in disconnected:
                self.active_connections[chat_room_id].remove(connection)
# WebSocket endpoint
@app.websocket("/ws/chat/{chat_room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    chat_room_id: int,
    token: str,
    db: Session = Depends(get_db)
):
    # Authenticate user from token
    try:
        user = await authenticate_websocket(token, db)
    except HTTPException:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    manager = ConnectionManager()

    try:
        await manager.connect(websocket, chat_room_id, user.id)

        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Handle different message types
            if message_data["type"] == "chat_message":
                # Save message to database
                db_message = Message(
                    chat_room_id=chat_room_id,
                    user_id=user.id,
                    content=message_data["content"],
                    message_type=message_data.get("message_type", "text")
                )
                db.add(db_message)
                db.commit()
                db.refresh(db_message)

                # Broadcast to room
                await manager.broadcast_to_room(chat_room_id, {
                    "type": "new_message",
                    "message_id": db_message.uuid,
                    "user_id": user.id,
                    "username": user.username,
                    "content": message_data["content"],
                    "timestamp": db_message.created_at.isoformat(),
                    "message_type": message_data.get("message_type", "text")
                })

            elif message_data["type"] == "typing_start":
                await manager.broadcast_to_room(chat_room_id, {
                    "type": "user_typing",
                    "user_id": user.id,
                    "username": user.username,
                    "typing": True
                })

            elif message_data["type"] == "typing_stop":
                await manager.broadcast_to_room(chat_room_id, {
                    "type": "user_typing",
                    "user_id": user.id,
                    "username": user.username,
                    "typing": False
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket, chat_room_id, user.id)
        await manager.broadcast_to_room(chat_room_id, {
            "type": "user_left",
            "user_id": user.id,
            "message": f"User {user.username} left the chat"
        })
