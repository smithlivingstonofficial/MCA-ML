"""
Deterministic Synthetic Healthcare Data Generator for Hospital Operations Intelligence Platform.
Generates realistic hospital infrastructure, patient encounters, triage logs, bed statuses,
roster assignments, and hourly arrival aggregates.
"""

import sys
import os
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

# Add repo root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.db.session import SessionLocal, engine, Base
from backend.app.db.models import (
    Department, Ward, Bed, BedStatusEvent, Encounter,
    TriageObservation, RosterAssignment, HourlyArrivalAggregate
)
from backend.app.domain.bed_lifecycle import BedState


def generate_all_synthetic_data(seed: int = 42, days: int = 180):
    print(f"[*] Initializing Synthetic Data Generator (Seed: {seed}, Horizon: {days} days)...")
    rng = np.random.default_rng(seed)

    # Recreate tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # 1. Departments & Wards
    departments_meta = [
        {"code": "ED", "name": "Emergency Department"},
        {"code": "ICU", "name": "Intensive Care Unit"},
        {"code": "GEN_MED", "name": "General Medicine"},
        {"code": "SURG", "name": "General Surgery"},
    ]

    dept_objs = {}
    for d in departments_meta:
        dept = Department(code=d["code"], name=d["name"])
        db.add(dept)
        dept_objs[d["code"]] = dept
    db.flush()

    wards_meta = [
        {"code": "ED_ACUTE", "name": "ED Acute Care", "dept": "ED", "specialty": "Emergency", "beds": 15, "ratio": 3.0},
        {"code": "ED_OBS", "name": "ED Observation", "dept": "ED", "specialty": "Emergency", "beds": 15, "ratio": 4.0},
        {"code": "ICU_NORTH", "name": "ICU North", "dept": "ICU", "specialty": "ICU", "beds": 12, "ratio": 1.0},
        {"code": "ICU_SOUTH", "name": "ICU South", "dept": "ICU", "specialty": "ICU", "beds": 12, "ratio": 1.0},
        {"code": "MED_WARD_A", "name": "Internal Medicine A", "dept": "GEN_MED", "specialty": "General", "beds": 18, "ratio": 4.0},
        {"code": "MED_WARD_B", "name": "Internal Medicine B", "dept": "GEN_MED", "specialty": "General", "beds": 18, "ratio": 4.0},
        {"code": "SURG_WARD_A", "name": "Post-Op Surgery A", "dept": "SURG", "specialty": "Surgical", "beds": 15, "ratio": 4.0},
        {"code": "SURG_WARD_B", "name": "Post-Op Surgery B", "dept": "SURG", "specialty": "Surgical", "beds": 15, "ratio": 4.0},
    ]

    ward_objs = {}
    for w in wards_meta:
        ward = Ward(
            department_id=dept_objs[w["dept"]].id,
            code=w["code"],
            name=w["name"],
            specialty=w["specialty"],
            total_physical_beds=w["beds"],
            target_nurse_to_patient_ratio=w["ratio"]
        )
        db.add(ward)
        ward_objs[w["code"]] = ward
    db.flush()

    # 2. Beds (Total = 120)
    all_beds = []
    initial_states_distribution = [
        BedState.OCCUPIED.value,
        BedState.READY.value,
        BedState.RESERVED.value,
        BedState.CLEANING.value,
        BedState.MAINTENANCE.value,
        BedState.BLOCKED.value,
    ]
    # Realistic distribution probabilities
    state_probs = [0.60, 0.22, 0.06, 0.06, 0.03, 0.03]

    for w in wards_meta:
        ward = ward_objs[w["code"]]
        for b_idx in range(1, w["beds"] + 1):
            chosen_state = rng.choice(initial_states_distribution, p=state_probs)
            is_iso = bool(rng.random() < 0.20) if "ICU" in w["code"] or "MED" in w["code"] else False
            is_tele = bool(rng.random() < 0.70) if "ICU" in w["code"] or "ED" in w["code"] else False
            
            bed = Bed(
                ward_id=ward.id,
                bed_number=f"{w['code']}-{b_idx:02d}",
                current_state=chosen_state,
                is_isolation_capable=is_iso,
                is_telemetry_capable=is_tele,
                last_state_change=datetime.utcnow() - timedelta(hours=int(rng.integers(1, 48)))
            )
            db.add(bed)
            all_beds.append(bed)
    db.flush()

    # 3. Staff Roster (Active shifts for today)
    shifts = ["Morning", "Evening", "Night"]
    nurse_names = ["Sarah Jenkins", "Michael Chang", "Emily Davis", "Robert Taylor", "Priya Sharma", "David Kim", "Elena Rostova", "Marcus Vance"]
    doctor_names = ["Dr. Richard Adams", "Dr. Aisha Patel", "Dr. Gregory House", "Dr. Lisa Cuddy", "Dr. Eric Foreman"]

    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    for ward_code, ward in ward_objs.items():
        # Assign 2-4 nurses per ward per shift
        num_nurses = 3 if "ICU" in ward_code else 2
        for shift in shifts:
            for n_idx in range(num_nurses):
                nurse_assignment = RosterAssignment(
                    ward_id=ward.id,
                    staff_member_name=f"Nurse {nurse_names[(n_idx + hash(ward_code)) % len(nurse_names)]}",
                    role="Nurse",
                    shift_name=shift,
                    shift_date=today_str,
                    is_on_duty=(shift == "Morning")  # Currently on duty for Morning
                )
                db.add(nurse_assignment)
            # Add 1 doctor per ward/department
            doc_assignment = RosterAssignment(
                ward_id=ward.id,
                staff_member_name=doctor_names[hash(ward_code) % len(doctor_names)],
                role="Doctor",
                shift_name=shift,
                shift_date=today_str,
                is_on_duty=(shift == "Morning")
            )
            db.add(doc_assignment)

    # 4. Hourly Emergency Arrivals Time Series (Historical 180 days)
    print("[*] Generating hourly emergency arrivals time series...")
    end_time = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    start_time = end_time - timedelta(days=days)
    
    current_ts = start_time
    hourly_records = []
    
    # Pre-compute hourly base rates:
    # Diurnal multiplier by hour of day (0-23)
    diurnal_profile = np.array([
        0.35, 0.25, 0.20, 0.18, 0.22, 0.30,  # 00:00 - 05:00
        0.50, 0.80, 1.20, 1.45, 1.60, 1.55,  # 06:00 - 11:00
        1.40, 1.35, 1.40, 1.45, 1.50, 1.55,  # 12:00 - 17:00
        1.60, 1.50, 1.30, 1.05, 0.75, 0.50   # 18:00 - 23:00
    ])
    
    # Day-of-week multiplier (Monday=0 to Sunday=6)
    dow_profile = np.array([1.25, 1.10, 1.00, 0.95, 1.05, 1.15, 0.90])
    
    base_hourly_arrival_rate = 7.5  # Mean 7.5 patients/hour for ED

    while current_ts <= end_time:
        hr = current_ts.hour
        dow = current_ts.weekday()
        
        # Surge event simulation: 3% probability of surge hours (e.g. multi-car pileup or infectious spike)
        is_surge = bool(rng.random() < 0.03)
        surge_mult = rng.uniform(1.6, 2.5) if is_surge else 1.0
        
        expected_lambda = base_hourly_arrival_rate * diurnal_profile[hr] * dow_profile[dow] * surge_mult
        arrivals = int(rng.poisson(lam=expected_lambda))
        mean_esi = float(rng.normal(loc=3.1, scale=0.3))
        mean_esi = min(4.5, max(1.5, mean_esi))

        agg = HourlyArrivalAggregate(
            department_code="ED",
            timestamp=current_ts,
            arrival_count=arrivals,
            mean_esi=round(mean_esi, 2),
            is_surge=is_surge
        )
        db.add(agg)
        hourly_records.append({
            "timestamp": current_ts.isoformat(),
            "department_code": "ED",
            "arrival_count": arrivals,
            "mean_esi": round(mean_esi, 2),
            "is_surge": is_surge,
            "hour": hr,
            "day_of_week": dow,
        })
        current_ts += timedelta(hours=1)

    db.flush()

    # 5. Patient Encounters & Triage (Recent 15,000 patients across 180 days)
    print("[*] Generating 15,000 patient encounters and triage records...")
    complaints = [
        ("Chest Pain", 2, 45.0),
        ("Shortness of Breath", 2, 35.0),
        ("Abdominal Pain", 3, 75.0),
        ("Trauma / Fracture", 3, 60.0),
        ("High Fever", 3, 50.0),
        ("Laceration / Minor Injury", 4, 90.0),
        ("Migraine / Headache", 4, 110.0),
        ("Rash / Skin Condition", 5, 130.0),
        ("Medication Refill", 5, 140.0),
        ("Cardiac Arrest", 1, 0.0)
    ]
    complaint_weights = [0.12, 0.10, 0.20, 0.15, 0.10, 0.15, 0.08, 0.05, 0.03, 0.02]

    # Generate encounters distributed over the 180-day window
    total_encounters = 15000
    random_minute_offsets = rng.integers(0, days * 24 * 60, size=total_encounters)
    random_minute_offsets.sort()

    encounters_data = []
    triage_data = []

    for i in range(total_encounters):
        arrival_dt = start_time + timedelta(minutes=int(random_minute_offsets[i]))
        patient_anon = f"PAT-{rng.integers(100000, 999999)}"
        enc_type = "Emergency" if rng.random() < 0.75 else ("Elective" if rng.random() < 0.6 else "Inpatient")
        
        # Select complaint and ESI
        c_idx = rng.choice(len(complaints), p=complaint_weights)
        chief_c, base_esi, base_wait = complaints[c_idx]
        actual_esi = base_esi
        actual_wait = max(0.0, float(rng.normal(loc=base_wait, scale=base_wait * 0.25)))

        # LOS and disposition
        is_admitted = (actual_esi in [1, 2] and rng.random() < 0.85) or (actual_esi == 3 and rng.random() < 0.40)
        disposition = "Admitted" if is_admitted else ("Discharged" if rng.random() < 0.95 else "AMA")
        
        if is_admitted:
            admit_dt = arrival_dt + timedelta(minutes=int(actual_wait + rng.integers(30, 180)))
            # Length of Stay: log-normal distribution
            los_hours = float(np.exp(rng.normal(loc=3.8, scale=0.6)))  # ~30 to 90 hours
            discharge_dt = admit_dt + timedelta(hours=los_hours)
            if discharge_dt > datetime.utcnow():
                discharge_dt = None  # Currently active admission
                actual_los = None
            else:
                actual_los = round(los_hours, 2)
        else:
            admit_dt = None
            los_hours = float(rng.uniform(1.5, 6.0))
            discharge_dt = arrival_dt + timedelta(hours=los_hours)
            actual_los = round(los_hours, 2)

        enc = Encounter(
            patient_anon_id=patient_anon,
            encounter_type=enc_type,
            arrival_time=arrival_dt,
            admitted_time=admit_dt,
            discharge_time=discharge_dt,
            disposition=disposition,
            primary_diagnosis_category=chief_c,
            actual_los_hours=actual_los
        )
        db.add(enc)
        db.flush()

        triage = TriageObservation(
            encounter_id=enc.id,
            esi_score=actual_esi,
            chief_complaint=chief_c,
            triage_timestamp=arrival_dt,
            waiting_time_minutes=round(actual_wait, 1)
        )
        db.add(triage)

        encounters_data.append({
            "encounter_id": enc.id,
            "patient_anon_id": patient_anon,
            "encounter_type": enc_type,
            "arrival_time": arrival_dt.isoformat(),
            "admitted_time": admit_dt.isoformat() if admit_dt else None,
            "discharge_time": discharge_dt.isoformat() if discharge_dt else None,
            "disposition": disposition,
            "los_hours": actual_los,
            "esi_score": actual_esi,
            "chief_complaint": chief_c,
            "waiting_time_minutes": round(actual_wait, 1)
        })

        if (i + 1) % 3000 == 0:
            print(f"    --> Committed {i + 1} / {total_encounters} encounters...")
            db.commit()

    db.commit()
    db.close()

    # 6. Save Fixtures as CSV for Fast Data Science Pipeline
    fixtures_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../fixtures"))
    os.makedirs(fixtures_dir, exist_ok=True)
    
    hourly_df = pd.DataFrame(hourly_records)
    hourly_csv_path = os.path.join(fixtures_dir, "ed_hourly_arrivals.csv")
    hourly_df.to_csv(hourly_csv_path, index=False)
    
    encounters_df = pd.DataFrame(encounters_data)
    encounters_csv_path = os.path.join(fixtures_dir, "patient_encounters.csv")
    encounters_df.to_csv(encounters_csv_path, index=False)

    print(f"[+] Synthetic Healthcare Generation Complete!")
    print(f"    - SQLite DB: hospital.db")
    print(f"    - Hourly Arrivals CSV: {hourly_csv_path} ({len(hourly_df)} records)")
    print(f"    - Encounters CSV: {encounters_csv_path} ({len(encounters_df)} records)")
    print(f"    - Wards: {len(wards_meta)} | Beds: {len(all_beds)}")


if __name__ == "__main__":
    generate_all_synthetic_data(seed=42, days=180)

