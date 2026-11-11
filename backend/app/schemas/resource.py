from datetime import date, datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


# ==================== MODULE 3 SCHEMAS ====================

class InventoryLotResponse(BaseModel):
    id: str
    item_id: str
    lot_number: str
    quantity_on_hand: int
    expiry_date: date
    received_date: date
    is_quarantined: bool

    model_config = ConfigDict(from_attributes=True)


class InventoryItemResponse(BaseModel):
    id: str
    sku_code: str
    generic_name: str
    category: str
    unit_of_measure: str
    reorder_threshold: int
    target_stock_level: int
    standard_lead_time_days: int
    total_usable_stock: int
    reorder_required: bool
    active_lots: List[InventoryLotResponse]

    model_config = ConfigDict(from_attributes=True)


class DispenseRequest(BaseModel):
    sku_code: str
    requested_qty: int
    dispensed_by: str = "PHARMACY_STAFF"
    reason: Optional[str] = "Clinical prescription fulfillment"


class DispenseAllocation(BaseModel):
    lot_id: str
    lot_number: str
    expiry_date: str
    quantity_deducted: int
    remaining_in_lot: int


class DispenseResponse(BaseModel):
    sku_code: str
    generic_name: str
    requested_qty: int
    dispensed_allocations: List[DispenseAllocation]
    remaining_stock: int
    reorder_threshold: int
    reorder_triggered: bool


class VentilatorSummary(BaseModel):
    total: int
    in_use: int
    available: int
    maintenance: int
    utilization_rate: float
    utilization_pct: float
    critical_threshold_exceeded: bool


class OxygenSummary(BaseModel):
    current_volume_liters: float
    nominal_capacity_liters: float
    hourly_burn_rate_lph: float
    days_of_supply_remaining: float
    capacity_pct: float
    low_supply_alert: bool


class EquipmentMetricsResponse(BaseModel):
    ventilators: VentilatorSummary
    oxygen_supply: OxygenSummary
    fleet_summary: List[Dict[str, Any]]


# ==================== MODULE 4 SCHEMAS ====================

class WardWorkforceSummary(BaseModel):
    ward_id: str
    ward_code: str
    ward_name: str
    specialty: str
    patient_census: int
    target_ratio: str
    required_nurses: int
    present_nurses: int
    nurse_deficit: int
    coverage_pct: float
    has_deficit: bool


class StaffingAlert(BaseModel):
    severity: str
    ward_code: str
    ward_name: str
    message: str
    type: str


class WorkforceDeficitResponse(BaseModel):
    shift_name: str
    target_date: Optional[str]
    hospital_coverage_pct: float
    total_required_nurses: int
    total_present_nurses: int
    total_nurse_deficits: int
    staffing_alerts: List[StaffingAlert]
    ward_summaries: List[WardWorkforceSummary]


class RosterAssignmentResponse(BaseModel):
    id: str
    ward_id: str
    staff_member_name: str
    role: str
    shift_name: str
    shift_date: str
    status: str
    is_on_duty: bool

    model_config = ConfigDict(from_attributes=True)


class StatusUpdateRequest(BaseModel):
    status: str  # Scheduled, Present, Absent, OnCall
    is_on_duty: Optional[bool] = None

