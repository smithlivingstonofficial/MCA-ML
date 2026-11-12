"""
Module 5 & 7: AI Clinical Decision Support Copilot REST Endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.domain.copilot_engine import copilot_engine
from backend.app.schemas.realtime import (
    CopilotRecommendationsResponse,
    CopilotRecommendationItem,
    CopilotActionRequest,
    CopilotActionResponse
)
from backend.app.core.security import get_current_user, UserAccount

router = APIRouter()


@router.get("/recommendations", response_model=CopilotRecommendationsResponse)
def get_copilot_mitigation_recommendations(db: Session = Depends(get_db)):
    """
    Returns prioritized AI copilot operational rebalancing recommendations.
    """
    recs = copilot_engine.get_active_recommendations(db)
    items = [CopilotRecommendationItem(**r) for r in recs]
    immediate = sum(1 for r in items if r.urgency == "IMMEDIATE" and r.status == "PENDING")

    return CopilotRecommendationsResponse(
        total_recommendations=len(items),
        immediate_actions_count=immediate,
        recommendations=items
    )


@router.post("/action/{recommendation_id}/dispatch", response_model=CopilotActionResponse)
def dispatch_copilot_mitigation(
    recommendation_id: str,
    req: CopilotActionRequest,
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Authorizes and dispatches an operational copilot recommendation.
    Generates an immutable compliance audit trail entry and broadcasts event via WebSockets.
    """
    try:
        res = copilot_engine.dispatch_recommendation(
            recommendation_id=recommendation_id,
            actor_id=current_user.username,
            actor_role=current_user.role,
            notes=req.notes or "Approved mitigation action.",
            db=db
        )
        return CopilotActionResponse(**res)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
