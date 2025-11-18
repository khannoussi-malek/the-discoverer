"""WebSocket API routes for real-time updates."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Any, List
import json
import asyncio

from src.application.services.query_service import QueryService
from src.utils.logger import logger


router = APIRouter(prefix="/api/ws", tags=["websocket"])


class ConnectionManager:
    """WebSocket connection manager."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.query_subscriptions: Dict[str, List[WebSocket]] = {}  # query_id -> connections
    
    async def connect(self, websocket: WebSocket):
        """Accept new connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Remove from all subscriptions
        for query_id, connections in self.query_subscriptions.items():
            if websocket in connections:
                connections.remove(websocket)
        
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send message to specific connection."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connections."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for conn in disconnected:
            self.disconnect(conn)
    
    def subscribe_to_query(self, query_id: str, websocket: WebSocket):
        """Subscribe connection to query updates."""
        if query_id not in self.query_subscriptions:
            self.query_subscriptions[query_id] = []
        
        if websocket not in self.query_subscriptions[query_id]:
            self.query_subscriptions[query_id].append(websocket)
    
    async def notify_query_update(self, query_id: str, update: Dict[str, Any]):
        """Notify subscribers of query update."""
        if query_id in self.query_subscriptions:
            disconnected = []
            for connection in self.query_subscriptions[query_id]:
                try:
                    await connection.send_json({
                        "type": "query_update",
                        "query_id": query_id,
                        "data": update
                    })
                except Exception as e:
                    logger.error(f"Error notifying query update: {e}")
                    disconnected.append(connection)
            
            # Remove disconnected
            for conn in disconnected:
                self.disconnect(conn)


# Global connection manager
manager = ConnectionManager()


@router.websocket("/query/{query_id}")
async def websocket_query_updates(websocket: WebSocket, query_id: str):
    """WebSocket endpoint for query updates."""
    await manager.connect(websocket)
    manager.subscribe_to_query(query_id, websocket)
    
    try:
        # Send initial connection confirmation
        await manager.send_personal_message({
            "type": "connected",
            "query_id": query_id,
            "message": "Subscribed to query updates"
        }, websocket)
        
        # Keep connection alive and handle messages
        while True:
            try:
                # Wait for messages from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle ping/pong
                if message.get("type") == "ping":
                    await manager.send_personal_message({
                        "type": "pong",
                        "timestamp": asyncio.get_event_loop().time()
                    }, websocket)
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                await manager.send_personal_message({
                    "type": "error",
                    "message": str(e)
                }, websocket)
    
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)


@router.websocket("/general")
async def websocket_general(websocket: WebSocket):
    """General WebSocket endpoint for system updates."""
    await manager.connect(websocket)
    
    try:
        # Send initial connection confirmation
        await manager.send_personal_message({
            "type": "connected",
            "message": "Connected to general updates"
        }, websocket)
        
        # Keep connection alive
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle ping/pong
                if message.get("type") == "ping":
                    await manager.send_personal_message({
                        "type": "pong",
                        "timestamp": asyncio.get_event_loop().time()
                    }, websocket)
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                await manager.send_personal_message({
                    "type": "error",
                    "message": str(e)
                }, websocket)
    
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)


# Export manager for use in other modules
def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager."""
    return manager


