"""
Module 5 & 7: AI Hospital Operations Copilot & Automated Mitigation Engine.
Consumes multi-vector operational anomalies, staffing deficits, and PuLP solver bottlenecks
to generate explainable, prioritized clinical operations mitigation recommendations.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from sqlalchemy.orm import Session

from backend.app.domain.anomaly_detector import get_anomaly_detector
from backend.app.domain.audit_logger import record_audit_event
from backend.app.core.broadcaster import broadcaster


class HospitalOperationsCopilot:
    """
    Intelligent decision-support copilot proposing proactive operational mitigations
    under clinical supervision guidelines.
    """

    def __init__(self):
        # In-memory recommendation registry
        self.recommendations_store: Dict[str, Dict[str, Any]] = {}
        self._seed_default_recommendations()

    def _seed_default_recommendations(self):
        now = datetime.utcnow()
        default_recs = [
            {
                "recommendation_id": "COPILOT-REC-01",
                "urgency": "IMMEDIATE",
                "category": "STAFF_DISPATCH",
                "title": "Dispatch Float Nurses to ICU East",
                "rationalization": "ICU bed occupancy is at 92% with 1:1 acuity ratios requiring immediate clinical reinforcement.",
                "recommended_action": "Reassign 2 float-pool certified ICU registered nurses for the evening shift.",
                "projected_impact": "Prevents mandatory patient diversion; stabilizes ICU nurse-patient safety ceiling.",
                "status": "PENDING",
                "target_department": "Intensive Care Unit (ICU)",
                "created_at": now
            },
            {
                "recommendation_id": "COPILOT-REC-02",
                "urgency": "HIGH",
                "category": "BED_REBALANCING",
                "title": "Fast-Track Terminal Bed Cleaning in Surgical Ward B",
                "rationalization": "6 postoperative recovery beds have been in 'Cleaning' status for over 90 minutes.",
                "recommended_action": "Dispatch Environmental Services (EVS) Rapid Turn team to Ward SURG-B.",
                "projected_impact": "Releases 6 usable staffed beds into the admission pool within 30 minutes.",
                "status": "PENDING",
                "target_department": "Surgical Inpatient Ward",
                "created_at": now
            },
            {
                "recommendation_id": "COPILOT-REC-03",
                "urgency": "HIGH",
                "category": "FLOW_DIVERSION",
                "title": "Activate Ambulatory Fast-Track Bay for ESI 4/5 Arrivals",
                "rationalization": "ED main queue waiting times are escalating due to concurrent low-acuity minor complaint volume.",
                "recommended_action": "Reroute walking-wounded ESI 4 and 5 patients to Fast-Track Pod C.",
                "projected_impact": "Reduces acute triage waiting times by an estimated 35% within 45 minutes.",
                "status": "PENDING",
                "target_department": "Emergency Department",
                "created_at": now
            },
            {
                "recommendation_id": "COPILOT-REC-04",
                "urgency": "MEDIUM",
                "category": "OXYGEN_SAFETY",
                "title": "Expedite Bulk Liquid Oxygen Secondary Tank Refill",
                "rationalization": "Current oxygen burn rate of 85 L/h projects 3.5 days of reserves before safety buffer breach.",
                "recommended_action": "Submit stat bulk delivery order to certified medical gas supplier (Air Liquide/Linde).",
                "projected_impact": "Preempts weekend tank pressure drops and guarantees continuous ventilator support.",
                "status": "PENDING",
                "target_department": "Biomedical Gas Depots",
                "created_at": now
            }
        ]
        for r in default_recs:
            self.recommendations_store[r["recommendation_id"]] = r

    def get_active_recommendations(self, db: Optional[Session] = None) -> List[Dict[str, Any]]:
        """
        Returns active recommendations, dynamically refreshing from anomaly scans if db is provided.
        """
        if db is not None:
            anomaly_data = get_anomaly_detector().scan_for_anomalies(db)
            now = datetime.utcnow()
            for ano in anomaly_data["anomalies"]:
                rec_id = f"COPILOT-DYN-{ano['anomaly_id'][-6:]}"
                if rec_id not in self.recommendations_store:
                    self.recommendations_store[rec_id] = {
                        "recommendation_id": rec_id,
                        "urgency": "IMMEDIATE" if ano["severity"] == "CRITICAL" else "HIGH",
                        "category": "BED_REBALANCING" if "BED" in ano["category"] else "FLOW_DIVERSION",
                        "title": f"Mitigate {ano['title']}",
                        "rationalization": ano["root_cause_analysis"],
                        "recommended_action": f"Operational intervention targeted at {ano['target_entity']}.",
                        "projected_impact": "Expected to normalize statistical variance within 60 minutes.",
                        "status": "PENDING",
                        "target_department": ano["target_entity"],
                        "created_at": now
                    }

        # Return sorted by urgency (IMMEDIATE > HIGH > MEDIUM)
        urgency_order = {"IMMEDIATE": 0, "HIGH": 1, "MEDIUM": 2}
        recs = list(self.recommendations_store.values())
        recs.sort(key=lambda x: (urgency_order.get(x["urgency"], 3), x["status"] != "PENDING"))
        return recs

    def dispatch_recommendation(
        self,
        recommendation_id: str,
        actor_id: str,
        actor_role: str,
        notes: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Executes and logs the dispatch of a copilot recommendation.
        """
        rec = self.recommendations_store.get(recommendation_id)
        if not rec:
            raise ValueError(f"Recommendation {recommendation_id} not found.")

        now = datetime.utcnow()
        rec["status"] = "DISPATCHED"
        rec["dispatched_at"] = now
        rec["dispatched_by"] = actor_id

        # 1. Audit Trail Record
        record_audit_event(
            db=db,
            actor_id=actor_id,
            actor_role=actor_role,
            action="COPILOT_ACTION_DISPATCHED",
            module="Module 7",
            resource_id=recommendation_id,
            details=f"Dispatched Copilot Action '{rec['title']}' for {rec['target_department']}. Notes: {notes}"
        )

        # 2. Real-Time WebSocket Broadcast
        broadcaster.broadcast_sync(
            event_type="COPILOT_ACTION_DISPATCHED",
            message=f"Mitigation Dispatched: {rec['title']} ({actor_role})",
            module="Copilot",
            severity="INFO",
            payload={
                "recommendation_id": recommendation_id,
                "dispatched_by": actor_id,
                "target_department": rec["target_department"]
            }
        )

        return {
            "recommendation_id": recommendation_id,
            "status": "DISPATCHED",
            "dispatched_at": now,
            "actor_id": actor_id,
            "message": f"Successfully executed dispatch protocol for '{rec['title']}'."
        }


# Global Singleton
copilot_engine = HospitalOperationsCopilot()

