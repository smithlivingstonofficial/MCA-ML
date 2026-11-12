"""
Module 7: Real-Time WebSocket Streaming & Simulation Trigger Endpoints.
"""

from typing import Dict, Any
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from backend.app.core.broadcaster import broadcaster
from backend.app.schemas.realtime import TriggerStreamEventRequest, WebSocketEventMessage
from backend.app.db.session import get_db

router = APIRouter()


@router.websocket("/ws/live-stream")
async def websocket_live_stream_endpoint(websocket: WebSocket):
    """
    Bi-directional WebSocket streaming live operational events, anomalies, and copilot actions.
    """
    await broadcaster.connect(websocket)
    try:
        while True:
            # Listen for client heartbeats or incoming telemetry pings
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text('{"event_type": "PONG", "timestamp": "' + datetime.utcnow().isoformat() + '"}')
    except WebSocketDisconnect:
        broadcaster.disconnect(websocket)
    except Exception:
        broadcaster.disconnect(websocket)


@router.post("/trigger-event", response_model=Dict[str, Any])
def trigger_simulated_stream_event(req: TriggerStreamEventRequest):
    """
    Injects a real-time event into the hospital WebSocket broadcast stream.
    Used for live demonstrations and testing event-driven dashboard reactivity.
    """
    broadcaster.broadcast_sync(
        event_type=req.event_type,
        message=req.message,
        module=req.module,
        severity=req.severity,
        payload=req.payload
    )

    return {
        "status": "DISPATCHED",
        "broadcast_to_clients": len(broadcaster.active_connections),
        "event_type": req.event_type,
        "message": req.message
    }
