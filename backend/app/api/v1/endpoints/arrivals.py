from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.db.models import HourlyArrivalAggregate
from backend.app.schemas.hospital import ArrivalForecastResponse, HourlyForecastPoint
from backend.ml.inference.arrival_forecaster import get_arrival_forecaster

router = APIRouter()


@router.get("/forecast", response_model=ArrivalForecastResponse)
def get_emergency_arrival_forecast(
    horizon: int = Query(24, ge=1, le=72, description="Forecast horizon in hours (1-72)"),
    db: Session = Depends(get_db)
):
    """
    Module 1: Generates hourly Emergency Department arrival forecasts for 24h, 48h, or 72h
    with 80% prediction intervals and overcrowding risk flags.
    """
    forecaster = get_arrival_forecaster()
    points = forecaster.forecast_arrivals(db=db, horizon_hours=horizon)

    return ArrivalForecastResponse(
        generated_at=datetime.utcnow(),
        horizon_hours=horizon,
        model_version=forecaster.version,
        data_source="SYNTHETIC DEMO DATA",
        forecasts=[HourlyForecastPoint(**p) for p in points]
    )


@router.get("/history")
def get_emergency_arrival_history(
    hours: int = Query(24, ge=1, le=168, description="Historical hours to retrieve"),
    db: Session = Depends(get_db)
):
    """
    Module 1: Returns recent observed hourly arrivals in the Emergency Department.
    """
    records = (
        db.query(HourlyArrivalAggregate)
        .filter(HourlyArrivalAggregate.department_code == "ED")
        .order_by(HourlyArrivalAggregate.timestamp.desc())
        .limit(hours)
        .all()
    )
    return [
        {
            "timestamp": r.timestamp,
            "arrival_count": r.arrival_count,
            "mean_esi": r.mean_esi,
            "is_surge": r.is_surge
        }
        for r in reversed(records)
    ]

