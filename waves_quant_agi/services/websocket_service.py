### services/websocket_service.py

from fastapi import WebSocket
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class WebSocketManager:
    """
    Manage real-time WebSocket connections
    """

    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"User {user_id} connected via WebSocket")

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info(f"User {user_id} disconnected from WebSocket")

    async def send_personal_message(self, user_id: int, message: str):
        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_text(message)
            logger.info(f"Sent message to user {user_id}: {message}")

    async def broadcast(self, message: str):
        for user_id, connection in self.active_connections.items():
            await connection.send_text(message)
            logger.info(f"Broadcasted message to user {user_id}")
