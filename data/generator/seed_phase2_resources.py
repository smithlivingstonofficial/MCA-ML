"""
Synthetic Seeder for Phase 2: Resource Intelligence.
Seeds pharmaceutical items, FEFO lots, stock movements, equipment fleet (ventilators, oxygen),
and clinical staff registry with multi-shift rosters.
"""

import sys
import os
from datetime import date, datetime, timedelta
import numpy as np

# Add repo root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.db.session import SessionLocal
from backend.app.db.models import (
    Ward, InventoryItem, InventoryLot, StockMovement, Equipment, StaffMember, RosterAssignment
)


def seed_phase2_resources(seed: int = 42):
    print(f"[*] Seeding Phase 2 Resources (Inventory, Equipment, Workforce)...")
    rng = np.random.default_rng(seed)
    db = SessionLocal()

    # 1. Seed Inventory Items
    items_meta = [
        {"sku": "MED-AMOX-500", "name": "Amoxicillin 500mg Injection", "cat": "Antibiotic", "uom": "Vial", "reorder": 60, "target": 250, "lead": 2},
        {"sku": "MED-CEFT-1G", "name": "Ceftriaxone 1g IV", "cat": "Antibiotic", "uom": "Vial", "reorder": 50, "target": 200, "lead": 2},
        {"sku": "MED-PROP-20", "name": "Propofol 20ml (1%) Emulsion", "cat": "Critical_Care", "uom": "Ampoule", "reorder": 40, "target": 180, "lead": 3},
        {"sku": "MED-NOREP-4", "name": "Norepinephrine 4mg/4ml", "cat": "Critical_Care", "uom": "Ampoule", "reorder": 35, "target": 150, "lead": 2},
        {"sku": "MED-HEP-5K", "name": "Heparin Sodium 5,000 IU/ml", "cat": "Anticoagulant", "uom": "Vial", "reorder": 30, "target": 120, "lead": 2},
        {"sku": "MED-PARAC-1G", "name": "Paracetamol 10mg/ml IV Infusion", "cat": "Analgesic", "uom": "Bottle", "reorder": 70, "target": 300, "lead": 1},
        {"sku": "BLD-PRBC-OPOS", "name": "Packed Red Blood Cells (O Positive)", "cat": "Blood_PRBC", "uom": "Unit", "reorder": 20, "target": 60, "lead": 1},
        {"sku": "BLD-PRBC-ONEG", "name": "Packed Red Blood Cells (O Negative - Universal)", "cat": "Blood_PRBC", "uom": "Unit", "reorder": 15, "target": 40, "lead": 1},
        {"sku": "OXY-BULK-LIQ", "name": "Liquid Medical Oxygen Bulk Reserve", "cat": "Oxygen_Supply", "uom": "Liter", "reorder": 3000, "target": 10000, "lead": 1},
    ]

    today = date.today()
    item_objs = {}

    for im in items_meta:
        existing = db.query(InventoryItem).filter(InventoryItem.sku_code == im["sku"]).first()
        if not existing:
            item = InventoryItem(
                sku_code=im["sku"],
                generic_name=im["name"],
                category=im["cat"],
                unit_of_measure=im["uom"],
                reorder_threshold=im["reorder"],
                target_stock_level=im["target"],
                standard_lead_time_days=im["lead"]
            )
            db.add(item)
            item_objs[im["sku"]] = item
        else:
            item_objs[im["sku"]] = existing
    db.flush()

    # 2. Seed Lots (Ensuring multiple lots per item with varying expiry for FEFO)
    for sku, item in item_objs.items():
        existing_lots = db.query(InventoryLot).filter(InventoryLot.item_id == item.id).count()
        if existing_lots == 0:
            if sku == "OXY-BULK-LIQ":
                # Single continuous bulk tank lot
                lot = InventoryLot(
                    item_id=item.id,
                    lot_number="OXY-BULK-2026-A",
                    quantity_on_hand=7800,
                    expiry_date=today + timedelta(days=365),
                    received_date=today - timedelta(days=10)
                )
                db.add(lot)
            else:
                # Lot 1: Near expiry (15 to 45 days) - FEFO Priority 1
                lot1 = InventoryLot(
                    item_id=item.id,
                    lot_number=f"LOT-{rng.integers(1000, 9999)}-A",
                    quantity_on_hand=int(rng.integers(30, 70)),
                    expiry_date=today + timedelta(days=int(rng.integers(15, 45))),
                    received_date=today - timedelta(days=60)
                )
                # Lot 2: Longer expiry (180 to 365 days) - FEFO Priority 2
                lot2 = InventoryLot(
                    item_id=item.id,
                    lot_number=f"LOT-{rng.integers(1000, 9999)}-B",
                    quantity_on_hand=int(rng.integers(80, 150)),
                    expiry_date=today + timedelta(days=int(rng.integers(180, 365))),
                    received_date=today - timedelta(days=20)
                )
                # Lot 3: Expired lot for testing quarantine filter
                lot3 = InventoryLot(
                    item_id=item.id,
                    lot_number=f"LOT-EXP-{rng.integers(1000, 9999)}",
                    quantity_on_hand=int(rng.integers(5, 15)),
                    expiry_date=today - timedelta(days=int(rng.integers(2, 20))),
                    received_date=today - timedelta(days=180),
                    is_quarantined=True
                )
                db.add_all([lot1, lot2, lot3])
    db.flush()

    # 3. Seed Equipment (Ventilators, Oxygen Banks, Defibrillators)
    wards = db.query(Ward).all()
    icu_wards = [w for w in wards if "ICU" in w.code]
    ed_wards = [w for w in wards if "ED" in w.code]

    existing_equip = db.query(Equipment).count()
    if existing_equip == 0:
        # Ventilators (10 total: 6 In Use, 3 Available, 1 Maintenance)
        vent_statuses = ["In_Use", "In_Use", "In_Use", "In_Use", "In_Use", "In_Use", "Available", "Available", "Available", "Maintenance"]
        for idx, st in enumerate(vent_statuses, start=1):
            assigned_ward = icu_wards[idx % len(icu_wards)].id if icu_wards else None
            vent = Equipment(
                equipment_code=f"VENT-{idx:02d}",
                equipment_type="Ventilator",
                ward_id=assigned_ward,
                status=st,
                telemetry_metric_name="airway_pressure_cmh2o",
                telemetry_metric_value=float(rng.uniform(14.0, 24.0)) if st == "In_Use" else 0.0,
                last_service_date=datetime.utcnow() - timedelta(days=int(rng.integers(5, 60)))
            )
            db.add(vent)

        # Oxygen Bulk Tanks
        tank_a = Equipment(
            equipment_code="OXY-BANK-NORTH",
            equipment_type="Oxygen_Bank",
            status="In_Use",
            telemetry_metric_name="pressure_psi",
            telemetry_metric_value=1850.0,
            last_service_date=datetime.utcnow() - timedelta(days=15)
        )
        tank_b = Equipment(
            equipment_code="OXY-BANK-SOUTH",
            equipment_type="Oxygen_Bank",
            status="In_Use",
            telemetry_metric_name="pressure_psi",
            telemetry_metric_value=1920.0,
            last_service_date=datetime.utcnow() - timedelta(days=15)
        )
        db.add_all([tank_a, tank_b])

        # Defibrillators
        for idx in range(1, 5):
            defib = Equipment(
                equipment_code=f"DEFIB-{idx:02d}",
                equipment_type="Defibrillator",
                ward_id=ed_wards[idx % len(ed_wards)].id if ed_wards else None,
                status="Available",
                telemetry_metric_name="battery_health_pct",
                telemetry_metric_value=98.0,
                last_service_date=datetime.utcnow() - timedelta(days=30)
            )
            db.add(defib)
    db.flush()

    # 4. Seed Staff Registry (StaffMember)
    existing_staff = db.query(StaffMember).count()
    if existing_staff == 0:
        nurse_names = [
            ("NUR-101", "Sarah Jenkins, RN", "Staff_Nurse", "Emergency"),
            ("NUR-102", "Michael Chang, RN", "Charge_Nurse", "Emergency"),
            ("NUR-103", "Emily Davis, BSN", "Staff_Nurse", "ICU"),
            ("NUR-104", "Robert Taylor, CCRN", "Charge_Nurse", "ICU"),
            ("NUR-105", "Priya Sharma, RN", "Staff_Nurse", "ICU"),
            ("NUR-106", "David Kim, BSN", "Staff_Nurse", "Medical_Surgical"),
            ("NUR-107", "Elena Rostova, RN", "Staff_Nurse", "Medical_Surgical"),
            ("NUR-108", "Marcus Vance, RN", "Staff_Nurse", "Medical_Surgical"),
            ("NUR-109", "Hannah Abbott, RN", "Staff_Nurse", "ICU"),
            ("NUR-110", "Carlos Mendez, RN", "Staff_Nurse", "Emergency"),
            ("DOC-201", "Dr. Richard Adams, MD", "Physician", "Emergency"),
            ("DOC-202", "Dr. Aisha Patel, MD", "Physician", "ICU"),
            ("DOC-203", "Dr. Gregory House, MD", "Physician", "Medical_Surgical"),
            ("DOC-204", "Dr. Lisa Cuddy, MD", "Physician", "Medical_Surgical"),
        ]

        staff_objs = []
        for code, name, role, spec in nurse_names:
            staff = StaffMember(
                employee_code=code,
                name=name,
                role=role,
                specialty_qualification=spec,
                is_active=True
            )
            db.add(staff)
            staff_objs.append(staff)
        db.flush()

    db.commit()
    db.close()
    print("[+] Phase 2 Resource Seeding Complete!")


if __name__ == "__main__":
    seed_phase2_resources(seed=42)

