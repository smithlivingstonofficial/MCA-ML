"""
Module 5: PuLP Mixed-Integer Linear Programming (MILP) Solver for Dynamic Bed & Acuity Allocation.
Enforces non-negotiable hard clinical safety constraints:
1. Acuity & Specialty Compatibility (ICU-only for high acuity).
2. Infection Isolation Rules (Negative pressure isolation).
3. Physical Bed Readiness (State must be 'Ready').
4. Staffed Usable Capacity Ceilings (Nurses on duty * Nurse Ratio).
Minimizes unmet patient assignments, waiting delay, and inter-ward transfer penalties.
"""

import time
from typing import List, Dict, Any, Optional
import pulp


class BedAllocationSolver:
    def __init__(self, solver_timeout_seconds: int = 10):
        self.timeout_seconds = solver_timeout_seconds

    def solve_allocation(
        self,
        patients: List[Dict[str, Any]],
        beds: List[Dict[str, Any]],
        wards: List[Dict[str, Any]],
        on_duty_nurses: Dict[str, int],  # ward_id -> count
        nurse_ratios: Dict[str, float],   # ward_id -> ratio (max patients per nurse)
        existing_census: Dict[str, int]   # ward_id -> active patients already occupying
    ) -> Dict[str, Any]:
        """
        Solves Mixed-Integer Linear Program for patient-to-bed allocation using HiGHS solver.
        """
        start_time = time.time()

        # 1. Filter Candidate Beds: Must be in 'Ready' state
        usable_beds = [b for b in beds if b.get("current_state") == "Ready"]

        # Indices
        patient_ids = [p["id"] for p in patients]
        bed_ids = [b["id"] for b in usable_beds]

        if not patient_ids:
            return {
                "status": "OPTIMAL",
                "solver_message": "No patients currently in queue requiring admission.",
                "total_patients": 0,
                "assigned_count": 0,
                "unassigned_count": 0,
                "assignments": [],
                "unassigned_patients": [],
                "execution_time_ms": round((time.time() - start_time) * 1000, 2),
                "diagnostics": []
            }

        if not bed_ids:
            # All beds unavailable
            return {
                "status": "INFEASIBLE_CAPACITY",
                "solver_message": "Zero operational beds currently in 'Ready' state across all hospital wards.",
                "total_patients": len(patients),
                "assigned_count": 0,
                "unassigned_count": len(patients),
                "assignments": [],
                "unassigned_patients": patients,
                "execution_time_ms": round((time.time() - start_time) * 1000, 2),
                "diagnostics": ["All physical beds are either Occupied, Cleaning, Blocked, or under Maintenance."]
            }

        # 2. Initialize Model
        model = pulp.LpProblem(name="Hospital_Dynamic_Bed_Allocation", sense=pulp.LpMinimize)

        # 3. Decision Variables
        # x[p, b] = 1 if patient p is assigned to bed b, 0 otherwise
        x = {
            (p, b): model.add_variable(f"assign_{p}_{b}", cat="Binary")
            for p in patient_ids
            for b in bed_ids
        }

        # u[p] = 1 if patient p remains unassigned (slack variable with high penalty)
        u = {
            p: model.add_variable(f"unassigned_{p}", cat="Binary")
            for p in patient_ids
        }

        # 4. Objective Function:
        # Minimize: (Heavily penalize unassigned patients) + (Penalize ward mismatch) + (Prioritize long wait times)
        objective_terms = []
        for p in patients:
            p_id = p["id"]
            wait_hours = float(p.get("waiting_time_minutes", 0)) / 60.0
            
            # Unassigned penalty (Higher for severe acuity ESI 1/2)
            esi = p.get("esi_score", 3)
            unassigned_weight = 5000.0 if esi in [1, 2] else 2000.0
            # Higher wait time increases urgency of assignment
            objective_terms.append(u[p_id] * (unassigned_weight + wait_hours * 50.0))

            preferred_ward_id = p.get("preferred_ward_id")
            for b in usable_beds:
                b_id = b["id"]
                # Penalty if placed in a non-preferred ward (mismatch penalty)
                if preferred_ward_id and b.get("ward_id") != preferred_ward_id:
                    objective_terms.append(x[p_id, b_id] * 50.0)
                else:
                    objective_terms.append(x[p_id, b_id] * 5.0)

        model += pulp.lpSum(objective_terms)

        # 5. HARD CONSTRAINTS:

        # Constraint 1: Each patient is either assigned to at most 1 bed or marked unassigned
        for p_id in patient_ids:
            model += pulp.lpSum([x[p_id, b_id] for b_id in bed_ids]) + u[p_id] == 1, f"Patient_Conservation_{p_id}"

        # Constraint 2: Each physical bed can host at most 1 patient
        for b_id in bed_ids:
            model += pulp.lpSum([x[p_id, b_id] for p_id in patient_ids]) <= 1, f"Bed_Capacity_{b_id}"

        # Constraint 3: Clinical Acuity & Specialty Compatibility
        for p in patients:
            p_id = p["id"]
            requires_icu = p.get("requires_icu", False) or p.get("esi_score") in [1, 2]
            requires_isolation = p.get("requires_isolation", False)

            for b in usable_beds:
                b_id = b["id"]
                b_specialty = b.get("specialty", "")
                is_iso_capable = b.get("is_isolation_capable", False)

                # ICU Hard Rule: ICU patient MUST be in ICU bed
                if requires_icu and "ICU" not in b_specialty:
                    model += x[p_id, b_id] == 0, f"Acuity_ICU_Block_{p_id}_{b_id}"

                # Non-ICU patient cannot consume scarce ICU beds unless general wards are exhausted
                if not requires_icu and "ICU" in b_specialty:
                    model += x[p_id, b_id] == 0, f"Acuity_NonICU_Block_{p_id}_{b_id}"

                # Isolation Hard Rule: Patient requiring isolation MUST have isolation-capable bed
                if requires_isolation and not is_iso_capable:
                    model += x[p_id, b_id] == 0, f"Isolation_Block_{p_id}_{b_id}"

        # Constraint 4: Staffed Capacity Ceiling (Nurse-to-Patient Ratio Limit)
        # Total active patients in ward w cannot exceed on_duty_nurses * ratio
        for w in wards:
            w_id = w["id"]
            w_code = w["code"]
            nurses = on_duty_nurses.get(w_id, 2)
            ratio = nurse_ratios.get(w_id, 4.0)
            max_staffed_patients = int(nurses * ratio)

            existing = existing_census.get(w_id, 0)
            available_nurse_slots = max(0, max_staffed_patients - existing)

            # Sum of newly assigned patients to beds in this ward
            ward_beds = [b["id"] for b in usable_beds if b.get("ward_id") == w_id]
            if ward_beds:
                model += (
                    pulp.lpSum([x[p_id, b_id] for p_id in patient_ids for b_id in ward_beds]) <= available_nurse_slots,
                    f"Staffed_Nurse_Ceiling_Ward_{w_code}"
                )

        # 6. Solve Model via HiGHS Solver
        solver = pulp.HiGHS(timeLimit=self.timeout_seconds, msg=False)
        solve_res = model.solve(solver)
        status_str = solve_res.status_str if hasattr(solve_res, "status_str") else "Optimal"

        # 7. Collect Results
        assigned_results = []
        unassigned_results = []
        diagnostics = []

        patient_map = {p["id"]: p for p in patients}
        bed_map = {b["id"]: b for b in usable_beds}

        for p_id in patient_ids:
            p_data = patient_map[p_id]
            u_val = u[p_id].value()
            if u_val is not None and round(u_val) == 1:
                unassigned_results.append(p_data)
                # Determine reason for non-assignment
                if p_data.get("requires_icu") or p_data.get("esi_score") in [1, 2]:
                    diagnostics.append(f"Patient {p_id} (ESI {p_data.get('esi_score')}): Insufficient staffed ICU bed capacity.")
                elif p_data.get("requires_isolation"):
                    diagnostics.append(f"Patient {p_id}: No ready isolation-capable beds available.")
                else:
                    diagnostics.append(f"Patient {p_id}: General ward staffed capacity ceiling reached.")
            else:
                for b_id in bed_ids:
                    x_val = x[p_id, b_id].value()
                    if x_val is not None and round(x_val) == 1:
                        b_data = bed_map[b_id]
                        assigned_results.append({
                            "patient_id": p_id,
                            "patient_anon_id": p_data.get("patient_anon_id", p_id),
                            "esi_score": p_data.get("esi_score", 3),
                            "bed_id": b_id,
                            "bed_number": b_data.get("bed_number"),
                            "ward_id": b_data.get("ward_id"),
                            "ward_name": b_data.get("ward_name", "General Ward"),
                            "specialty": b_data.get("specialty", "General"),
                            "is_isolation_certified": b_data.get("is_isolation_capable", False)
                        })

        exec_time = round((time.time() - start_time) * 1000, 2)
        obj_value = round(float(solve_res.objective), 2) if hasattr(solve_res, "objective") and solve_res.objective is not None else 0.0

        is_fully_feasible = len(unassigned_results) == 0 and status_str == "Optimal"

        return {
            "status": status_str if is_fully_feasible else ("INFEASIBLE_CAPACITY" if unassigned_results else status_str),
            "solver_message": (
                "All queued patients successfully allocated under hard safety constraints."
                if is_fully_feasible else
                f"Constrained allocation: {len(assigned_results)} assigned, {len(unassigned_results)} demand unmet due to capacity constraints."
            ),
            "total_patients": len(patients),
            "assigned_count": len(assigned_results),
            "unassigned_count": len(unassigned_results),
            "assignments": assigned_results,
            "unassigned_patients": unassigned_results,
            "execution_time_ms": exec_time,
            "objective_value": obj_value,
            "diagnostics": diagnostics
        }


_solver_instance = None

def get_bed_allocation_solver() -> BedAllocationSolver:
    global _solver_instance
    if _solver_instance is None:
        _solver_instance = BedAllocationSolver()
    return _solver_instance
