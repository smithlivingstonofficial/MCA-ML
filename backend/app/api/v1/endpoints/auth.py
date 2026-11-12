"""
Module 7: Authentication & Role-Based Access Control Endpoints.
"""

import hashlib
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.db.models import UserAccount
from backend.app.schemas.enterprise import LoginRequest, TokenResponse, UserProfileResponse, RoleInfo
from backend.app.core.security import create_token, get_current_user, HealthcareRole

router = APIRouter()


def _verify_pw(raw: str, hashed: str) -> bool:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest() == hashed


@router.post("/login", response_model=TokenResponse)
def login_for_access_token(req: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticates user credentials and issues a signed cryptographic bearer token.
    """
    user = db.query(UserAccount).filter(UserAccount.username == req.username).first()
    if not user or not _verify_pw(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password."
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated.")

    token = create_token({
        "sub": user.username,
        "role": user.role,
        "name": user.full_name
    })

    return TokenResponse(
        access_token=token,
        token_type="Bearer",
        user=UserProfileResponse(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            role=user.role,
            department=user.department,
            is_active=user.is_active
        )
    )


@router.get("/me", response_model=UserProfileResponse)
def get_authenticated_user_profile(current_user: UserAccount = Depends(get_current_user)):
    """
    Returns profile information for the current authenticated session.
    """
    return UserProfileResponse(
        id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name,
        role=current_user.role,
        department=current_user.department,
        is_active=current_user.is_active
    )


@router.get("/roles", response_model=List[RoleInfo])
def get_available_roles_and_credentials():
    """
    Returns healthcare role descriptions and pre-configured demonstration credentials.
    """
    return [
        RoleInfo(
            role_key=HealthcareRole.HOSPITAL_ADMIN,
            title="Hospital Operations Administrator",
            description="Full system governance, audit trail oversight, model recalibration, and system administration.",
            demo_username="admin (Password: admin123)",
            permissions=["VIEW_ALL", "EDIT_ALL", "GOVERNANCE_OVERRIDE", "AUDIT_EXPORT"]
        ),
        RoleInfo(
            role_key=HealthcareRole.BED_MANAGER,
            title="Bed Management & Patient Placement",
            description="Controls bed lifecycle state changes and triggers PuLP optimization solver runs.",
            demo_username="bedmanager (Password: bed123)",
            permissions=["VIEW_BEDS", "UPDATE_BED_STATE", "RUN_OPTIMIZATION", "SIMULATE_SCENARIOS"]
        ),
        RoleInfo(
            role_key=HealthcareRole.PHARMACIST,
            title="Clinical Pharmacist & Inventory Lead",
            description="Executes FEFO medication dispensing, lot tracking, and oxygen reserve telemetry.",
            demo_username="pharmacist (Password: rx123)",
            permissions=["VIEW_INVENTORY", "FEFO_DISPENSE", "MANAGE_LOTS", "EQUIPMENT_TELEMETRY"]
        ),
        RoleInfo(
            role_key=HealthcareRole.CLINICAL_REVIEWER,
            title="Care Transition & Clinical Reviewer",
            description="Reviews 30-day readmission risk cohorts, TreeSHAP waterfall attributions, and appointment adherence.",
            demo_username="reviewer (Password: review123)",
            permissions=["VIEW_READMISSION_COHORT", "INSPECT_SHAP_WATERFALL", "OUTREACH_FLAGGING"]
        )
    ]
