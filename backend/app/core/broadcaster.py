"""
Module 7: Real-Time WebSocket Connection Manager & Broadcast Hub.
Broadcasts hospital events, anomaly alerts, and telemetry changes to connected browser clients.
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import WebSocket


class EventBroadcaster:
    """
    Manages active WebSocket connections and broadcasts real-time hospital operational telemetry.
    """

    def __init__(self, history_limit: int = 50):
        self.active_connections: List[WebSocket] = []
        self.history_limit = history_limit
        self.event_history: List[Dict[str, Any]] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

        # Replay recent event history to the newly connected client
        if self.event_history:
            try:
                await websocket.send_text(json.dumps({
                    "event_type": "HISTORY_REPLAY",
                    "timestamp": datetime.utcnow().isoformat(),
                    "payload": {"events": self.event_history[-15:]}
                }))
            except Exception:
                pass

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, event_type: str, message: str, module: str = "System", severity: str = "INFO", payload: Optional[Dict[str, Any]] = None):
        """
        Asynchronously broadcasts a typed event to all active WebSocket connections.
        """
        now = datetime.utcnow()
        event_dict = {
            "event_id": str(uuid.uuid4())[:8],
            "event_type": event_type,
            "timestamp": now.isoformat(),
            "module": module,
            "severity": severity,
            "message": message,
            "payload": payload or {}
        }

        # Append to bounded history
        self.event_history.append(event_dict)
        if len(self.event_history) > self.history_limit:
            self.event_history.pop(0)

        data_text = json.dumps(event_dict)
        disconnected = []

        for conn in self.active_connections:
            try:
                await conn.send_text(data_text)
            except Exception:
                disconnected.append(conn)

        for conn in disconnected:
            self.disconnect(conn)

    def broadcast_sync(self, event_type: str, message: str, module: str = "System", severity: str = "INFO", payload: Optional[Dict[str, Any]] = None):
        """
        Synchronous wrapper allowing standard FastAPI endpoints and domain services
        to dispatch real-time events without managing async task loops.
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self.broadcast(event_type, message, module, severity, payload))
            else:
                loop.run_until_complete(self.broadcast(event_type, message, module, severity, payload))
        except RuntimeError:
            # Fallback if no active loop in thread
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            new_loop.run_until_complete(self.broadcast(event_type, message, module, severity, payload))
            new_loop.close()


# Global Singleton Instance
broadcaster = EventBroadcaster()

