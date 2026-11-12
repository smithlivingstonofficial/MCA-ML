"""
Module 6 & 7: Seed demo users and initial compliance audit logs for Phase 6.
"""

import hashlib
from datetime import datetime, timedelta
from backend.app.db.session import SessionLocal, engine, Base
from backend.app.db.models import UserAccount, AuditEvent


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def seed_phase6_security_and_audit():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # 1. Seed User Accounts if not present
        existing_users = {u.username: u for u in db.query(UserAccount).all()}
        
        users_to_seed = [
            {
                "username": "admin",
                "password": "admin123",
                "full_name": "Dr. Aris Thorne",
                "role": "HOSPITAL_ADMIN",
                "department": "Executive Leadership & Medical Affairs"
            },
            {
                "username": "bedmanager",
                "password": "bed123",
                "full_name": "Elena Vance, RN",
                "role": "BED_MANAGER",
                "department": "Central Patient Placement Operations"
            },
            {
                "username": "pharmacist",
                "password": "rx123",
                "full_name": "Marcus Chen, PharmD",
                "role": "PHARMACIST",
                "department": "Central Pharmacy & Sterile Compounding"
            },
            {
                "username": "reviewer",
                "password": "review123",
                "full_name": "Dr. Sarah Lin, MD",
                "role": "CLINICAL_REVIEWER",
                "department": "Care Transition & Readmission Reduction"
            }
        ]

        for u in users_to_seed:
            if u["username"] not in existing_users:
                acc = UserAccount(
                    username=u["username"],
                    hashed_password=hash_password(u["password"]),
                    full_name=u["full_name"],
                    role=u["role"],
                    department=u["department"]
                )
                db.add(acc)
                print(f"[+] Created user account: {u['username']} ({u['role']})")

        # 2. Seed Initial Audit Log Events if empty
        event_count = db.query(AuditEvent).count()
        if event_count == 0:
            now = datetime.utcnow()
            audit_events = [
                AuditEvent(
                    timestamp=now - timedelta(minutes=145),
                    actor_id="admin",
                    actor_role="HOSPITAL_ADMIN",
                    action="MODEL_RECALIBRATION_AUDIT",
                    module="Module 7",
                    resource_id="MODEL-HISTGBDT-ED-v1.0",
                    details="Automated Population Stability Index (PSI) verification passed with PSI=0.0412.",
                    status="SUCCESS",
                    ip_address="192.168.1.10"
                ),
                AuditEvent(
                    timestamp=now - timedelta(minutes=95),
                    actor_id="bedmanager",
                    actor_role="BED_MANAGER",
                    action="BED_STATE_CHANGE",
                    module="Module 2",
                    resource_id="BED-ICU-02",
                    details="Transitioned bed state from Cleaning to Ready following sterile terminal disinfection.",
                    status="SUCCESS",
                    ip_address="192.168.1.45"
                ),
                AuditEvent(
                    timestamp=now - timedelta(minutes=60),
                    actor_id="bedmanager",
                    actor_role="BED_MANAGER",
                    action="OPTIMIZATION_EXECUTED",
                    module="Module 5",
                    resource_id="OPT-RUN-5501",
                    details="Executed PuLP HiGHS MILP allocation solver for 14 queued patients. 14 assigned with 0 slack violations.",
                    status="SUCCESS",
                    ip_address="192.168.1.45"
                ),
                AuditEvent(
                    timestamp=now - timedelta(minutes=35),
                    actor_id="pharmacist",
                    actor_role="PHARMACIST",
                    action="MEDICATION_DISPENSED",
                    module="Module 3",
                    resource_id="SKU-ABX-001",
                    details="Dispensed 20 vials of Piperacillin/Tazobactam via FEFO from Lot LOT-2026-A1 (Expiry: 2026-11-20).",
                    status="SUCCESS",
                    ip_address="192.168.1.88"
                ),
                AuditEvent(
                    timestamp=now - timedelta(minutes=15),
                    actor_id="reviewer",
                    actor_role="CLINICAL_REVIEWER",
                    action="CONTINUITY_EVALUATION",
                    module="Module 6",
                    resource_id="MRN-7819A20B",
                    details="Generated local TreeSHAP attribution waterfall. Identified geriatric age and chronic recidivism as primary readmission drivers.",
                    status="SUCCESS",
                    ip_address="192.168.1.92"
                ),
                AuditEvent(
                    timestamp=now - timedelta(minutes=5),
                    actor_id="admin",
                    actor_role="HOSPITAL_ADMIN",
                    action="FHIR_BUNDLE_EXPORT",
                    module="Module 1",
                    resource_id="FHIR-BUNDLE-EXPORT-01",
                    details="Exported operational bed matrix and encounter census to HL7 FHIR R4 Bundle standard.",
                    status="SUCCESS",
                    ip_address="192.168.1.10"
                )
            ]
            for ev in audit_events:
                db.add(ev)
            print(f"[+] Seeded {len(audit_events)} clinical audit log entries.")

        db.commit()
        print("[+] Phase 6 security & audit initialization complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_phase6_security_and_audit()
