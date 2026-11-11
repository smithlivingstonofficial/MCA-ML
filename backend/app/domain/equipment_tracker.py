"""
Module 3: Biomedical equipment tracking and oxygen telemetry engine.
Monitors ventilator fleet utilization, oxygen tank reserves, days-of-supply forecasts,
and maintenance status.
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.app.db.models import Equipment


def calculate_equipment_and_oxygen_metrics(db: Session) -> Dict[str, Any]:
    """
    Computes real-time equipment availability, ventilator utilization, and oxygen bank reserves.
    """
    all_equipment = db.query(Equipment).all()

    # 1. Ventilator Fleet Metrics
    ventilators = [e for e in all_equipment if e.equipment_type == "Ventilator"]
    total_vents = len(ventilators)
    in_use_vents = sum(1 for e in ventilators if e.status == "In_Use")
    available_vents = sum(1 for e in ventilators if e.status == "Available")
    maintenance_vents = sum(1 for e in ventilators if e.status == "Maintenance")
    
    vent_utilization = (in_use_vents / (total_vents - maintenance_vents)) if (total_vents - maintenance_vents) > 0 else 0.0

    # 2. Oxygen Supply Bank Metrics
    oxygen_units = [e for e in all_equipment if e.equipment_type == "Oxygen_Bank"]
    # Total volume in liters or pressure (aggregate)
    current_o2_volume = sum(e.telemetry_metric_value or 0.0 for e in oxygen_units) if oxygen_units else 7500.0
    nominal_capacity = 10000.0  # Liters
    hourly_burn_rate = 85.0     # Liters / hour standard consumption
    
    # Days of supply remaining
    hours_remaining = current_o2_volume / hourly_burn_rate if hourly_burn_rate > 0 else 0.0
    days_of_supply = round(hours_remaining / 24.0, 1)

    o2_alert = days_of_supply < 3.0  # Alert if less than 3 days of oxygen remaining

    return {
        "ventilators": {
            "total": total_vents,
            "in_use": in_use_vents,
            "available": available_vents,
            "maintenance": maintenance_vents,
            "utilization_rate": round(vent_utilization, 4),
            "utilization_pct": round(vent_utilization * 100, 1),
            "critical_threshold_exceeded": vent_utilization >= 0.85
        },
        "oxygen_supply": {
            "current_volume_liters": round(current_o2_volume, 1),
            "nominal_capacity_liters": nominal_capacity,
            "hourly_burn_rate_lph": hourly_burn_rate,
            "days_of_supply_remaining": days_of_supply,
            "capacity_pct": round((current_o2_volume / nominal_capacity) * 100, 1),
            "low_supply_alert": o2_alert
        },
        "fleet_summary": [
            {
                "code": e.equipment_code,
                "type": e.equipment_type,
                "status": e.status,
                "telemetry": f"{e.telemetry_metric_name}: {e.telemetry_metric_value}" if e.telemetry_metric_name else "N/A",
                "ward_id": e.ward_id
            }
            for e in all_equipment
        ]
    }

