from fastapi import APIRouter
from backend.app.api.v1.endpoints import arrivals, beds, telemetry

api_router = APIRouter()
api_router.include_router(arrivals.router, prefix="/arrivals", tags=["Module 1: Patient Flow & Arrivals"])
api_router.include_router(beds.router, prefix="/beds", tags=["Module 2: Bed & Capacity Management"])
api_router.include_router(telemetry.router, prefix="/telemetry", tags=["Module 7: Command Center Telemetry"])

