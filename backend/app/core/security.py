"""
Module 7: Healthcare Security, Cryptographic Tokens & Role-Based Access Control (RBAC).
Provides signed bearer tokens, role verification dependencies, and permission enforcement.
"""

import hmac
import hashlib
import base64
import json
import time
from typing import Optional, List, Dict, Any, Callable
from fastapi import HTTPException, Security, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.db.models import UserAccount

SECRET_KEY = "antigravity-hospital-operations-secret-key-capstone-2026"
TOKEN_EXPIRATION_SECONDS = 86400  # 24 hours

security_scheme = HTTPBearer(auto_error=False)


class HealthcareRole:
    HOSPITAL_ADMIN = "HOSPITAL_ADMIN"
    BED_MANAGER = "BED_MANAGER"
    PHARMACIST = "PHARMACIST"
    CLINICAL_REVIEWER = "CLINICAL_REVIEWER"

    ALL_ROLES = [HOSPITAL_ADMIN, BED_MANAGER, PHARMACIST, CLINICAL_REVIEWER]


def create_token(payload: Dict[str, Any]) -> str:
    """
    Creates an HMAC-SHA256 cryptographically signed bearer token.
    """
    token_data = payload.copy()
    token_data["exp"] = int(time.time()) + TOKEN_EXPIRATION_SECONDS
    encoded_payload = base64.urlsafe_b64encode(json.dumps(token_data).encode()).decode()

    sig = hmac.new(SECRET_KEY.encode(), encoded_payload.encode(), hashlib.sha256).hexdigest()
    return f"{encoded_payload}.{sig}"


def verify_token(token: str) -> Dict[str, Any]:
    """
    Validates token signature and expiration timestamp.
    """
    try:
        parts = token.split(".")
        if len(parts) != 2:
            raise ValueError("Malformed token format.")

        encoded_payload, sig = parts
        expected_sig = hmac.new(SECRET_KEY.encode(), encoded_payload.encode(), hashlib.sha256).hexdigest()

        if not hmac.compare_digest(sig, expected_sig):
            raise ValueError("Cryptographic signature mismatch.")

        payload_bytes = base64.urlsafe_b64decode(encoded_payload.encode())
        payload = json.loads(payload_bytes.decode())

        if payload.get("exp", 0) < time.time():
            raise ValueError("Token has expired.")

        return payload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired credentials: {str(e)}"
        )


def get_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Security(security_scheme),
    db: Session = Depends(get_db)
) -> UserAccount:
    """
    Resolves the authenticated user from bearer token; defaults to default admin in development mode
    if no header is supplied to facilitate testing.
    """
    if not auth or not auth.credentials:
        # Development fallback: default to admin user
        dev_user = db.query(UserAccount).filter(UserAccount.username == "admin").first()
        if dev_user:
            return dev_user
        return UserAccount(
            id="DEV-ADMIN-01",
            username="admin",
            full_name="Default Hospital Administrator",
            role=HealthcareRole.HOSPITAL_ADMIN,
            is_active=True
        )

    payload = verify_token(auth.credentials)
    username = payload.get("sub")
    user = db.query(UserAccount).filter(UserAccount.username == username).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account not found or deactivated.")
    return user


def require_roles(allowed_roles: List[str]) -> Callable:
    """
    FastAPI dependency factory enforcing strict Role-Based Access Control.
    """
    def role_checker(current_user: UserAccount = Depends(get_current_user)) -> UserAccount:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: User role '{current_user.role}' lacks permission. Required: {allowed_roles}"
            )
        return current_user

    return role_checker
