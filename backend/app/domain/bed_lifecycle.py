from enum import Enum
from typing import Set, Dict


class BedState(str, Enum):
    READY = "Ready"
    RESERVED = "Reserved"
    OCCUPIED = "Occupied"
    CLEANING = "Cleaning"
    MAINTENANCE = "Maintenance"
    BLOCKED = "Blocked"


# Allowed state transitions
VALID_BED_TRANSITIONS: Dict[BedState, Set[BedState]] = {
    BedState.READY: {BedState.RESERVED, BedState.OCCUPIED, BedState.BLOCKED},
    BedState.RESERVED: {BedState.OCCUPIED, BedState.READY, BedState.BLOCKED},
    BedState.OCCUPIED: {BedState.CLEANING},
    BedState.CLEANING: {BedState.READY, BedState.BLOCKED, BedState.MAINTENANCE},
    BedState.MAINTENANCE: {BedState.CLEANING, BedState.BLOCKED},
    BedState.BLOCKED: {BedState.MAINTENANCE, BedState.CLEANING, BedState.READY},
}


class InvalidBedStateTransitionError(ValueError):
    """Raised when an illegal bed state transition is attempted."""
    def __init__(self, from_state: BedState, to_state: BedState, bed_id: str, reason: str = ""):
        super().__init__(
            f"Cannot transition bed '{bed_id}' from '{from_state.value}' to '{to_state.value}'. "
            f"Allowed transitions from '{from_state.value}': {[s.value for s in VALID_BED_TRANSITIONS.get(from_state, set())]}. "
            f"{reason}".strip()
        )
        self.from_state = from_state
        self.to_state = to_state
        self.bed_id = bed_id


def validate_bed_transition(from_state: BedState, to_state: BedState, bed_id: str = "unknown") -> bool:
    """
    Validates whether a proposed transition from from_state to to_state is valid.
    Raises InvalidBedStateTransitionError if illegal.
    """
    if from_state == to_state:
        return True
        
    allowed = VALID_BED_TRANSITIONS.get(from_state, set())
    if to_state not in allowed:
        raise InvalidBedStateTransitionError(
            from_state=from_state,
            to_state=to_state,
            bed_id=bed_id,
            reason="Violates hospital operational bed state machine protocol."
        )
    return True

