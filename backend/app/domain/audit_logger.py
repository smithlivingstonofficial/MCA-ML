"""
Module 7: Clinical and Operational Audit Logging Service.
Records immutable events for healthcare governance, regulatory traceability, and action audit trails.
"""

from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from backend.app.db.models import AuditEvent


def record_audit_event(
    db: Session,
    actor_id: str,
    actor_role: str,
    action: str,
    module: str,
    resource_id: Optional[str] = None,
    details: str = "",
    status: str = "SUCCESS",
    ip_address: str = "127.0.0.1"
) -> AuditEvent:
    """
    Persists an immutable audit log entry into the hospital database.
    """
    event = AuditEvent(
        timestamp=datetime.utcnow(),
        actor_id=actor_id,
        actor_role=actor_role,
        action=action,
        module=module,
        resource_id=resource_id,
        details=details,
        status=status,
        ip_address=ip_address
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
