from fastapi import APIRouter
from backend.app.api.v1.endpoints import (
    arrivals,
    beds,
    telemetry,
    inventory,
    workforce,
    optimization,
    continuity,
    auth,
    fhir,
    audit,
    reports
)

api_router = APIRouter()
api_router.include_router(arrivals.router, prefix="/arrivals", tags=["Module 1: Patient Flow & Arrivals"])
api_router.include_router(beds.router, prefix="/beds", tags=["Module 2: Bed & Capacity Management"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["Module 3: Medical Inventory & Equipment"])
api_router.include_router(workforce.router, prefix="/workforce", tags=["Module 4: Workforce & Staff Intelligence"])
api_router.include_router(optimization.router, prefix="/optimization", tags=["Module 5: PuLP Optimization & Simulation"])
api_router.include_router(continuity.router, prefix="/continuity", tags=["Module 6: Patient Continuity & Risk Intelligence"])
api_router.include_router(telemetry.router, prefix="/telemetry", tags=["Module 7: Command Center Telemetry"])
api_router.include_router(auth.router, prefix="/auth", tags=["Phase 6: Authentication & RBAC"])
api_router.include_router(fhir.router, prefix="/fhir", tags=["Phase 6: HL7 FHIR Interoperability"])
api_router.include_router(audit.router, prefix="/audit", tags=["Phase 6: Clinical Audit Trail"])
api_router.include_router(reports.router, prefix="/reports", tags=["Phase 6: Executive Reports & Data Export"])
