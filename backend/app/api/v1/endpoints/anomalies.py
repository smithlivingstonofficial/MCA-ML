"""
Module 6 & 7: Operational Anomaly Detection API Endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.domain.anomaly_detector import get_anomaly_detector
from backend.app.schemas.realtime import AnomalyDetectionResponse, OperationalAnomalyItem

router = APIRouter()


@router.get("/detect", response_model=AnomalyDetectionResponse)
def detect_operational_anomalies(db: Session = Depends(get_db)):
    """
    Scans real-time hospital queues, bed states, and biomedical telemetry
    to detect acute operational bottlenecks and distribution deviations.
    """
    detector = get_anomaly_detector()
    report = detector.scan_for_anomalies(db)

    items = [OperationalAnomalyItem(**a) for a in report["anomalies"]]

    return AnomalyDetectionResponse(
        evaluated_at=report["evaluated_at"],
        anomalies_detected_count=report["anomalies_detected_count"],
        critical_count=report["critical_count"],
        warning_count=report["warning_count"],
        overall_operational_health_score=report["overall_operational_health_score"],
        anomalies=items,
        diagnostic_summary=report["diagnostic_summary"]
    )

