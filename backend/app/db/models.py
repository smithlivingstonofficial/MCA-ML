import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.app.db.session import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Department(Base):
    __tablename__ = "departments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    wards = relationship("Ward", back_populates="department", cascade="all, delete-orphan")


class Ward(Base):
    __tablename__ = "wards"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    department_id = Column(String(36), ForeignKey("departments.id"), nullable=False)
    code = Column(String(20), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    specialty = Column(String(50), nullable=False)  # General, ICU, Surgical, Emergency
    total_physical_beds = Column(Integer, nullable=False)
    target_nurse_to_patient_ratio = Column(Float, default=4.0, nullable=False)  # Max patients per nurse

    department = relationship("Department", back_populates="wards")
    beds = relationship("Bed", back_populates="ward", cascade="all, delete-orphan")
    roster_assignments = relationship("RosterAssignment", back_populates="ward")


class Bed(Base):
    __tablename__ = "beds"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    ward_id = Column(String(36), ForeignKey("wards.id"), nullable=False)
    bed_number = Column(String(20), nullable=False, index=True)
    current_state = Column(String(20), default="Ready", nullable=False)  # Ready, Reserved, Occupied, Cleaning, Maintenance, Blocked
    is_isolation_capable = Column(Boolean, default=False, nullable=False)
    is_telemetry_capable = Column(Boolean, default=False, nullable=False)
    last_state_change = Column(DateTime, default=datetime.utcnow, nullable=False)

    ward = relationship("Ward", back_populates="beds")
    status_events = relationship("BedStatusEvent", back_populates="bed", cascade="all, delete-orphan")


class BedStatusEvent(Base):
    __tablename__ = "bed_status_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    bed_id = Column(String(36), ForeignKey("beds.id"), nullable=False, index=True)
    from_state = Column(String(20), nullable=False)
    to_state = Column(String(20), nullable=False)
    reason = Column(String(255), nullable=True)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    recorded_by = Column(String(50), default="system", nullable=False)

    bed = relationship("Bed", back_populates="status_events")


class Encounter(Base):
    __tablename__ = "encounters"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    patient_anon_id = Column(String(64), nullable=False, index=True)
    encounter_type = Column(String(20), nullable=False)  # Emergency, Inpatient, Elective
    arrival_time = Column(DateTime, nullable=False, index=True)
    admitted_time = Column(DateTime, nullable=True)
    discharge_time = Column(DateTime, nullable=True)
    disposition = Column(String(50), nullable=True)  # Discharged, Admitted, Transferred, AMA
    primary_diagnosis_category = Column(String(100), nullable=True)
    actual_los_hours = Column(Float, nullable=True)

    triage = relationship("TriageObservation", back_populates="encounter", uselist=False, cascade="all, delete-orphan")


class TriageObservation(Base):
    __tablename__ = "triage_observations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    encounter_id = Column(String(36), ForeignKey("encounters.id"), unique=True, nullable=False)
    esi_score = Column(Integer, nullable=False)  # 1 to 5
    chief_complaint = Column(String(100), nullable=False)
    triage_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    waiting_time_minutes = Column(Float, default=0.0, nullable=False)

    encounter = relationship("Encounter", back_populates="triage")


class RosterAssignment(Base):
    __tablename__ = "roster_assignments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    ward_id = Column(String(36), ForeignKey("wards.id"), nullable=False)
    staff_member_name = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False)  # Doctor, Nurse, Triage Nurse
    shift_name = Column(String(20), nullable=False)  # Morning, Evening, Night
    shift_date = Column(String(10), nullable=False)  # YYYY-MM-DD
    is_on_duty = Column(Boolean, default=True, nullable=False)

    ward = relationship("Ward", back_populates="roster_assignments")


class HourlyArrivalAggregate(Base):
    __tablename__ = "hourly_arrival_aggregates"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    department_code = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    arrival_count = Column(Integer, nullable=False)
    mean_esi = Column(Float, nullable=True)
    is_surge = Column(Boolean, default=False, nullable=False)


class ForecastRecord(Base):
    __tablename__ = "forecast_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    forecast_type = Column(String(50), nullable=False)  # ED_ARRIVALS, BED_OCCUPANCY
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    target_timestamp = Column(DateTime, nullable=False, index=True)
    horizon_hours = Column(Integer, nullable=False)
    predicted_value = Column(Float, nullable=False)
    lower_bound_80 = Column(Float, nullable=True)
    upper_bound_80 = Column(Float, nullable=True)
    model_version = Column(String(50), nullable=False)
    actual_value = Column(Float, nullable=True)

