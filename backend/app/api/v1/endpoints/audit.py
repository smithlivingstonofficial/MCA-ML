"""
Module 7: Clinical and Operational Audit Trail API.
Exposes queryable audit logs and manual compliance event logging.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.db.models import AuditEvent, UserAccount
from backend.app.schemas.enterprise import AuditLogResponse, AuditLogItem, RecordAuditRequest
from backend.app.domain.audit_logger import record_audit_event
from backend.app.core.security import get_current_user

router = APIRouter()


@router.get("/logs", response_model=AuditLogResponse)
def get_audit_trail_events(
    module: Optional[str] = Query(default=None, description="Filter by module: Module 1, Module 2, etc."),
    action: Optional[str] = Query(default=None, description="Filter by action code"),
    actor_role: Optional[str] = Query(default=None, description="Filter by actor role"),
    limit: int = Query(default=50, ge=5, le=200),
    db: Session = Depends(get_db)
):
    """
    Returns immutable audit trail entries with filtering capabilities.
    """
    query = db.query(AuditEvent)

    if module and module != "ALL":
        query = query.filter(AuditEvent.module == module)
    if action and action != "ALL":
        query = query.filter(AuditEvent.action == action)
    if actor_role and actor_role != "ALL":
        query = query.filter(AuditEvent.actor_role == actor_role)

    total = query.count()
    events = query.order_by(AuditEvent.timestamp.desc()).limit(limit).all()

    items = [
        AuditLogItem(
            id=e.id,
            timestamp=e.timestamp,
            actor_id=e.actor_id,
            actor_role=e.actor_role,
            action=e.action,
            module=e.module,
            resource_id=e.resource_id,
            details=e.details,
            status=e.status,
            ip_address=e.ip_address
        )
        for e in events
    ]

    return AuditLogResponse(total_events=total, events=items)


@router.post("/log", response_model=AuditLogItem)
def record_custom_audit_event(
    req: RecordAuditRequest,
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Records an authorized manual or system audit event into the compliance log.
    """
    event = record_audit_event(
        db=db,
        actor_id=current_user.username,
        actor_role=current_user.role,
        action=req.action,
        module=req.module,
        resource_id=req.resource_id,
        details=req.details,
        status=req.status
    )

    return AuditLogItem(
        id=event.id,
        timestamp=event.timestamp,
        actor_id=event.actor_id,
        actor_role=event.actor_role,
        action=event.action,
        module=event.module,
        resource_id=event.resource_id,
        details=event.details,
        status=event.status,
        ip_address=event.ip_address
    )
