from typing import List, Dict, Any
from backend.app.domain.bed_lifecycle import BedState


def calculate_ward_operational_capacity(
    beds: List[Dict[str, Any]],
    on_duty_nurses: int,
    nurse_to_patient_ratio: float = 4.0
) -> Dict[str, Any]:
    """
    Computes physical vs. operational (staffed) capacity for a given ward.
    
    Args:
        beds: List of bed records with at least 'state' key.
        on_duty_nurses: Number of qualified nurses actively on duty in this ward.
        nurse_to_patient_ratio: Maximum patients supported per nurse (e.g., 1.0 for ICU, 4.0 for General).
        
    Returns:
        Summary dict containing physical count, state breakdown, staffed ceiling, and usable ready beds.
    """
    total_physical = len(beds)
    state_counts = {state.value: 0 for state in BedState}
    
    for bed in beds:
        state = bed.get("state")
        if state in state_counts:
            state_counts[state] += 1
            
    occupied_count = state_counts[BedState.OCCUPIED.value]
    reserved_count = state_counts[BedState.RESERVED.value]
    ready_count = state_counts[BedState.READY.value]
    
    # Maximum patients supported by current on-duty nursing staff
    nurse_capacity_ceiling = int(on_duty_nurses * nurse_to_patient_ratio)
    
    # Active patient census
    current_census = occupied_count + reserved_count
    
    # Remaining nurse capacity for new patients
    available_nurse_capacity = max(0, nurse_capacity_ceiling - current_census)
    
    # Staffed usable beds cannot exceed physically ready beds or available nurse capacity
    staffed_usable_beds = min(ready_count, available_nurse_capacity)
    
    # Staffing deficit flag: when there are physically ready beds that cannot be used due to nurse shortages
    staffing_deficit = ready_count > available_nurse_capacity
    unstaffed_ready_beds = max(0, ready_count - available_nurse_capacity)
    
    occupancy_rate = (current_census / total_physical) if total_physical > 0 else 0.0
    staffed_occupancy_rate = (current_census / nurse_capacity_ceiling) if nurse_capacity_ceiling > 0 else 1.0

    return {
        "total_physical_beds": total_physical,
        "ready_beds": ready_count,
        "occupied_beds": occupied_count,
        "reserved_beds": reserved_count,
        "cleaning_beds": state_counts[BedState.CLEANING.value],
        "maintenance_beds": state_counts[BedState.MAINTENANCE.value],
        "blocked_beds": state_counts[BedState.BLOCKED.value],
        "on_duty_nurses": on_duty_nurses,
        "nurse_to_patient_ratio": nurse_to_patient_ratio,
        "nurse_capacity_ceiling": nurse_capacity_ceiling,
        "staffed_usable_beds": staffed_usable_beds,
        "unstaffed_ready_beds": unstaffed_ready_beds,
        "staffing_deficit": staffing_deficit,
        "physical_occupancy_rate": round(occupancy_rate, 4),
        "staffed_occupancy_rate": round(staffed_occupancy_rate, 4),
    }

