import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Date, ForeignKey, Index
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
    equipment = relationship("Equipment", back_populates="ward")


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


# ==================== MODULE 4: WORKFORCE ENTITIES ====================

class StaffMember(Base):
    __tablename__ = "staff_members"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    employee_code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    role = Column(String(30), nullable=False)  # Physician, Staff_Nurse, Charge_Nurse
    specialty_qualification = Column(String(50), nullable=False)  # Emergency, ICU, Medical_Surgical
    is_active = Column(Boolean, default=True, nullable=False)

    assignments = relationship("RosterAssignment", back_populates="staff_member")


class RosterAssignment(Base):
    __tablename__ = "roster_assignments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    staff_id = Column(String(36), ForeignKey("staff_members.id"), nullable=True)
    ward_id = Column(String(36), ForeignKey("wards.id"), nullable=False)
    staff_member_name = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False)  # Doctor, Nurse, Triage Nurse
    shift_name = Column(String(20), nullable=False)  # Morning, Evening, Night
    shift_date = Column(String(10), nullable=False, index=True)  # YYYY-MM-DD
    status = Column(String(20), default="Scheduled", nullable=False)  # Scheduled, Present, Absent, OnCall
    is_on_duty = Column(Boolean, default=True, nullable=False)

    ward = relationship("Ward", back_populates="roster_assignments")
    staff_member = relationship("StaffMember", back_populates="assignments")


# ==================== MODULE 3: INVENTORY & EQUIPMENT ENTITIES ====================

class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    sku_code = Column(String(30), unique=True, nullable=False, index=True)
    generic_name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)  # Antibiotic, Analgesic, Oxygen_Supply, Blood_PRBC, Critical_Care
    unit_of_measure = Column(String(20), nullable=False)  # Vial, Tablet, Liter, Unit
    reorder_threshold = Column(Integer, nullable=False, default=50)
    target_stock_level = Column(Integer, nullable=False, default=200)
    standard_lead_time_days = Column(Integer, nullable=False, default=2)

    lots = relationship("InventoryLot", back_populates="item", cascade="all, delete-orphan")
    stock_movements = relationship("StockMovement", back_populates="item", cascade="all, delete-orphan")


class InventoryLot(Base):
    __tablename__ = "inventory_lots"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    item_id = Column(String(36), ForeignKey("inventory_items.id"), nullable=False, index=True)
    lot_number = Column(String(50), nullable=False, index=True)
    quantity_on_hand = Column(Integer, nullable=False, default=0)
    expiry_date = Column(Date, nullable=False, index=True)
    received_date = Column(Date, nullable=False)
    is_quarantined = Column(Boolean, default=False, nullable=False)

    item = relationship("InventoryItem", back_populates="lots")
    stock_movements = relationship("StockMovement", back_populates="lot")


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    item_id = Column(String(36), ForeignKey("inventory_items.id"), nullable=False)
    lot_id = Column(String(36), ForeignKey("inventory_lots.id"), nullable=True)
    movement_type = Column(String(20), nullable=False)  # DISPENSE, RECEIVE, ADJUST, EXPIRED_DISCARD
    quantity = Column(Integer, nullable=False)
    reason = Column(String(255), nullable=True)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    recorded_by = Column(String(50), default="system", nullable=False)

    item = relationship("InventoryItem", back_populates="stock_movements")
    lot = relationship("InventoryLot", back_populates="stock_movements")


class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    equipment_code = Column(String(30), unique=True, nullable=False, index=True)  # e.g. VENT-01, OXY-BANK-A
    equipment_type = Column(String(50), nullable=False)  # Ventilator, Oxygen_Bank, Defibrillator, Dialysis_Machine
    ward_id = Column(String(36), ForeignKey("wards.id"), nullable=True)
    status = Column(String(20), default="Available", nullable=False)  # In_Use, Available, Maintenance
    telemetry_metric_name = Column(String(50), nullable=True)  # e.g. pressure_psi, flow_rate_lpm
    telemetry_metric_value = Column(Float, nullable=True)
    last_service_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    ward = relationship("Ward", back_populates="equipment")


# ==================== HISTORICAL AGGREGATES & FORECASTS ====================

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
