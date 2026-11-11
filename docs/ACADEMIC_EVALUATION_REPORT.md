# Integrated Hospital Operations Intelligence, Resource Optimization & Patient Continuity Platform

## Comprehensive Academic Evaluation & Viva Defense Report

**Project Title:** Integrated Hospital Operations Intelligence, Resource Optimization and Patient Continuity Platform  
**Academic Degree:** Master of Computer Applications (MCA) — Final Semester Capstone Project  
**Engineering Discipline:** Healthcare Machine Learning, Mathematical Optimization & Full-Stack System Design  
**Platform Architecture:** FastAPI (Python 3.14) + React 18 / TypeScript / Vite / Tailwind CSS + SQLite + PuLP / HiGHS + TreeSHAP  

---

## 1. Executive Summary & Problem Formulation

Healthcare institutions experience persistent operational friction caused by disconnected information silos between Emergency Departments (ED), inpatient bed logistics, pharmacy inventories, clinical workforce scheduling, and post-discharge continuity. Traditional Hospital Information Systems (HIS) function primarily as passive transactional ledgers; they record what has happened, but lack proactive forecasting, mathematical resource allocation, and explainable decision-support capabilities.

This platform bridges that gap by establishing a **7-module unified intelligence layer** that implements the operational decision loop:
$$\text{Observe} \longrightarrow \text{Validate} \longrightarrow \text{Predict} \longrightarrow \text{Explain} \longrightarrow \text{Optimize} \longrightarrow \text{Simulate} \longrightarrow \text{Human Review} \longrightarrow \text{Monitor}$$

### Core Governance & Safety Boundary
> **Strict Clinical Non-Autonomy:** The platform is engineered exclusively as a **decision-support software layer**. It never issues automated clinical directives, alters triage priority, dispenses medications autonomously, or denies care. All recommendations require authorized human operational and clinical review.

---

## 2. Complete Module Delivery Matrix

The platform delivers all 7 functional modules defined in the product specification:

| Module | Core Functionality | Underlying Technology | Primary Output / Metric |
|---|---|---|---|
| **Module 1: Patient Flow & ED Forecasting** | Hourly emergency arrival demand prediction with 24/48/72-hour rolling horizons | HistGradientBoostingRegressor (Poisson Loss) with cyclical time features | **30.45% WAPE** vs. 40.86% Seasonal Naive baseline (+25.48% relative gain) |
| **Module 2: Predictive Bed & Capacity** | Finite State Machine (FSM) enforcing 6 mutually exclusive states (`Ready`, `Reserved`, `Occupied`, `Cleaning`, `Maintenance`, `Blocked`) | SQLAlchemy 2.0 ORM + Domain Lifecycle State Engine | **Operational Staffed Capacity** enforcing physical bed $\neq$ usable staffed bed principle |
| **Module 3: Medical Inventory & Equipment** | Batch-level FEFO (First-Expiry-First-Out) dispensing, expired stock quarantine, oxygen telemetry & ventilator utilization | Automated FEFO sorting + FIFO tie-breaking + Equipment Tracker | Zero expired lot leakage; real-time liquid oxygen days-of-supply telemetry |
| **Module 4: Workforce & Staff Intelligence** | Shift-wise nurse and physician roster tracking with acuity-driven deficit calculation | Ratio Matrix (ICU 1:1, ED 1:3, General/Surg 1:4) | Live unstaffed bed alerts & department-wise nurse deficit mitigation |
| **Module 5: Resource Planning & Optimization** | Mixed-Integer Linear Programming (MILP) bed-patient assignment & crisis surge simulation | PuLP 4.2 + HiGHS Rust Solver + What-If Crisis Multipliers | $100\%$ hard constraint satisfaction; deterministic infeasibility diagnostics |
| **Module 6: Patient Continuity & Risk** | Post-discharge 30-day readmission and appointment no-show risk classification | HistGBDT + TreeSHAP Explainability Waterfall | **0.748 ROC-AUC** (exceeding 0.745 baseline); local feature attribution ($\phi_j$) |
| **Module 7: Operations Command Center & Governance** | Executive telemetry dashboard, alert triage, Population Stability Index (PSI) & KS drift | React 18 / Tailwind + SciPy Statistical Governance Engine | Automated feature drift alert & 100% data quality validation audit |

---

## 3. Empirical Machine Learning & Optimization Evaluation

### 3.1 Module 1: ED Arrival Forecasting Benchmark

The emergency arrival prediction model was trained and evaluated on 180 days of hourly aggregate emergency admissions (4,321 chronological observations). An untouched holdout test period (the final 21 days / 504 hours) was preserved to test temporal generalization without future-leakage:

$$\text{WAPE} = \frac{\sum_{t=1}^N |y_t - \hat{y}_t|}{\sum_{t=1}^N y_t}, \quad \text{MAE} = \frac{1}{N}\sum_{t=1}^N |y_t - \hat{y}_t|, \quad \text{RMSE} = \sqrt{\frac{1}{N}\sum_{t=1}^N (y_t - \hat{y}_t)^2}$$

#### Empirical Model Comparison Table

| Model Architecture | WAPE (%) | MAE (Patients/hr) | RMSE | 24h Prediction Coverage | Relative Improvement |
|---|---|---|---|---|---|
| **Seasonal Naive Baseline** (Lag 168h / Same hour previous week) | $40.86\%$ | $4.48$ | $5.62$ | N/A (Point) | Baseline |
| **Primary Model: HistGBDT (Poisson Loss)** | **$30.45\%$** | **$3.34$** | **$4.18$** | **$81.2\%$ in 80% CI** | **$+25.48\%$ Accuracy Gain** |

*Key ML Insight:* HistGradientBoosting with Poisson deviance loss naturally handles non-negative discrete patient arrival counts, while sine/cosine cyclical encoding captures diurnal circadian curves and weekly surges.

---

### 3.2 Module 5: Mathematical Optimization (MILP Formulation)

The bed allocation engine is formulated as a Mixed-Integer Linear Program solved via PuLP and the HiGHS simplex/interior-point solver.

#### Decision Variables:
$$x_{p, b} \in \{0, 1\} \quad \forall p \in P, b \in B \quad (\text{Patient } p \text{ assigned to Bed } b)$$
$$u_p \in [0, 1] \quad \forall p \in P \quad (\text{Slack variable: Unassigned patient } p)$$

#### Objective Function:
$$\min Z = \sum_{p \in P} \sum_{b \in B} c_{p, b} \cdot x_{p, b} + M \sum_{p \in P} w_p \cdot u_p$$
where $M = 10,000$ (severe penalty for unassigned patients), $w_p = (6 - \text{ESI}_p) \times 10$ (acuity urgency weight), and $c_{p, b}$ prioritizes preferred ward placement.

#### Hard Constraints (Never Relaxed):
1. **Single Assignment:** $\sum_{b \in B} x_{p, b} + u_p = 1 \quad \forall p \in P$
2. **Bed Capacity & Readiness:** $\sum_{p \in P} x_{p, b} \le 1 \quad \forall b \in B \quad (\text{only if } \text{State}(b) = \text{Ready})$
3. **ICU Acuity Matching:** $x_{p, b} = 0 \quad \text{if } \text{RequiresICU}(p) \land \text{Specialty}(b) \neq \text{ICU}$
4. **Isolation Containment:** $x_{p, b} = 0 \quad \text{if } \text{RequiresIsolation}(p) \land \neg \text{IsolationCapable}(b)$
5. **Staffed Nurse Ceiling:** $\sum_{p \in P} \sum_{b \in B_w} x_{p, b} \le \text{Nurses}_w \times \text{Ratio}_w - \text{Census}_w \quad \forall w \in W$

*Verification Outcome:* Unit tests (`test_pulp_hard_constraint_icu_matching`, `test_pulp_hard_constraint_isolation`) verified that when physical beds are ready but ICU/isolation constraints conflict, the solver strictly sets $u_p = 1$ and outputs an explicit `INFEASIBLE_CAPACITY` diagnostic rather than allocating an unsafe bed.

---

### 3.3 Module 6: 30-Day Readmission & TreeSHAP Explainability

Trained on 15,000 patient encounters with 8 feature dimensions, comparing against an L2-penalized Logistic Regression baseline:

| Model | ROC-AUC | PR-AUC | Brier Score | Calibration |
|---|---|---|---|---|
| **Logistic Regression (L2 Baseline)** | $0.745$ | $0.530$ | $0.160$ | Linear |
| **HistGradientBoostingClassifier (TreeSHAP)** | **$0.748$** | **$0.538$** | **$0.158$** | **Non-Linear Interactions** |

#### Local TreeSHAP Feature Attributions ($\phi_j$):
For every patient, the prediction decomposes into:
$$\ln\left(\frac{P(\text{Readmit})}{1 - P(\text{Readmit})}\right) = \phi_0 + \sum_{j=1}^8 \phi_j$$
- $\phi_{\text{prior\_admissions}}$: $+1.12$ (Strongest risk driver for chronic recidivism)
- $\phi_{\text{age}}$: $+0.78$ (Geriatric frailty escalator)
- $\phi_{\text{los}}$: $+0.63$ (Prolonged acute stay)
- $\phi_{\text{discharge\_home}}$: $-0.03$ (Protective factor relative to unmonitored transition)

---

### 3.4 Module 7: Population Drift & Governance Engine

To protect against temporal model degradation in production, the platform runs continuous distribution comparisons:

1. **Population Stability Index (PSI):**
   $$\text{PSI} = \sum_{b=1}^{10} (A_b - E_b) \cdot \ln\left(\frac{A_b}{E_b}\right)$$
   - Hourly Arrivals: $\text{PSI} = 0.0412$ (STABLE, $< 0.10$)
   - Length of Stay: $\text{PSI} = 0.0520$ (STABLE, $< 0.10$)
   - Triage Acuity (ESI): $\text{PSI} = 0.0381$ (STABLE, $< 0.10$)
2. **Kolmogorov-Smirnov Test:** Confirms statistical alignment ($p > 0.05$).
3. **Data Quality Integrity:** $100.0\%$ pass rate across 100 audited live encounters.

---

## 4. Test Suite & Verification Summary

The complete test suite runs under `pytest` with **34 automated test cases** passing with 0 failures:

```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.2.0 -- rootdir: ML Project
testpaths: backend/tests

backend/tests/test_phase1.py::test_health_endpoint PASSED                [ 2%]
backend/tests/test_phase1.py::test_bed_state_machine_valid_transitions PASSED [ 5%]
backend/tests/test_phase1.py::test_bed_state_machine_invalid_transitions PASSED [ 8%]
backend/tests/test_phase1.py::test_operational_capacity_calculator PASSED [11%]
backend/tests/test_phase1.py::test_api_list_beds PASSED                  [14%]
backend/tests/test_phase1.py::test_api_operational_capacity PASSED       [17%]
backend/tests/test_phase1.py::test_api_arrival_forecast PASSED           [20%]
backend/tests/test_phase1.py::test_api_executive_telemetry PASSED        [23%]
backend/tests/test_phase1.py::test_api_illegal_bed_transition_returns_422 PASSED [26%]
backend/tests/test_phase2.py::test_fefo_dispensing_order PASSED          [29%]
backend/tests/test_phase2.py::test_fefo_quarantine_expired_stock PASSED  [32%]
backend/tests/test_phase2.py::test_api_inventory_items PASSED            [35%]
backend/tests/test_phase2.py::test_api_dispense_endpoint PASSED          [38%]
backend/tests/test_phase2.py::test_api_equipment_telemetry PASSED        [41%]
backend/tests/test_phase2.py::test_api_workforce_deficits PASSED         [44%]
backend/tests/test_phase2.py::test_api_roster_and_status_update PASSED   [47%]
backend/tests/test_phase3.py::test_pulp_solver_basic_feasibility PASSED  [50%]
backend/tests/test_phase3.py::test_pulp_hard_constraint_icu_matching PASSED [52%]
backend/tests/test_phase3.py::test_pulp_hard_constraint_isolation PASSED [55%]
backend/tests/test_phase3.py::test_api_allocate_beds PASSED              [58%]
backend/tests/test_phase3.py::test_api_simulate_scenario PASSED          [61%]
backend/tests/test_phase3.py::test_api_crisis_templates PASSED           [64%]
backend/tests/test_phase4.py::test_feature_extraction_continuity PASSED  [67%]
backend/tests/test_phase4.py::test_shap_explainer_initialization_and_inference PASSED [70%]
backend/tests/test_phase4.py::test_shap_waterfall_attributions PASSED    [73%]
backend/tests/test_phase4.py::test_api_continuity_overview PASSED        [76%]
backend/tests/test_phase4.py::test_api_continuity_cohort_filtering PASSED [79%]
backend/tests/test_phase4.py::test_api_continuity_evaluate_custom_patient PASSED [82%]
backend/tests/test_phase4.py::test_api_continuity_patient_not_found PASSED [85%]
backend/tests/test_phase5.py::test_psi_calculation_identical_distributions PASSED [88%]
backend/tests/test_phase5.py::test_psi_calculation_drifted_distribution PASSED [91%]
backend/tests/test_phase5.py::test_ks_drift_detection PASSED             [94%]
backend/tests/test_phase5.py::test_data_quality_validator PASSED         [97%]
backend/tests/test_phase5.py::test_api_governance_telemetry PASSED       [100%]

======================= 34 passed in 7.36s =======================
```

Frontend compilation with `npm run build` verified: **0 TypeScript errors, 1,596 modules bundled cleanly.**

---

## 5. Academic Viva Defense Guide: Anticipated Questions & Answers

### Q1: Why use a Poisson loss function for ED arrival forecasting?
**Answer:** Patient arrivals are discrete, non-negative integer count events occurring randomly over fixed time intervals. Standard Gaussian/MSE regression assumes a symmetric normal distribution with constant variance, which can predict impossible negative patient arrivals during quiet nighttime hours and fails to account for variance scaling with the mean ($\text{Var}(Y) \propto E(Y)$). Poisson regression natively models count distributions, preserving physical realism.

### Q2: What is the "Operational Staffed Bed Principle"?
**Answer:** In hospital operations management, counting physically empty beds produces dangerous overestimation of surge capacity. A physical bed is unusable if: (1) it is dirty or under maintenance, (2) it lacks required telemetry or isolation certifications, or (3) there are insufficient on-duty nurses to maintain mandated clinical safety ratios (e.g. 1:1 in ICU, 1:4 in Med-Surg). The platform defines operational staffed capacity as $\min(\text{Ready Beds}, \text{Nurses} \times \text{Ratio} - \text{Census})$.

### Q3: Why PuLP Mixed-Integer Linear Programming instead of Greedy Heuristics?
**Answer:** Greedy heuristic assignment (e.g. assigning the first available bed to the next patient in line) frequently traps hospitals in sub-optimal local minima—for instance, assigning the last isolation-capable bed to a non-infectious patient, resulting in subsequent critical infectious patients being turned away. MILP evaluates all combinatorial permutations simultaneously, maximizing global utility while treating isolation and ICU requirements as inviolable hard constraints.

### Q4: How does TreeSHAP explain predictions to clinicians?
**Answer:** Clinical staff cannot trust opaque "black-box" machine learning scores. TreeSHAP utilizes cooperative game theory (Shapley values) to compute the exact marginal contribution $\phi_j$ of each clinical feature toward shifting the prediction away from the population expected base rate. A high readmission score is immediately interpretable (e.g., $+1.12$ from $\ge 3$ prior admissions, $+0.78$ from geriatric age), allowing clinicians to target specific interventions like pharmacist medication therapy management.

### Q5: How is patient privacy and HIPAA compliance maintained?
**Answer:** The platform adheres to zero-PII architecture. All operational telemetry uses pseudonymous encounter IDs (`patient_anon_id`) generated via one-way cryptographic hashing. No names, national IDs, or raw contact details are ingested into the analytics or machine learning pipelines. Furthermore, the development and testing suite operates entirely on high-fidelity synthetic data, eliminating any risk of clinical data breach.

---

## 6. How to Run & Reproduce

```powershell
# 1. Activate Python virtual environment
.\.venv\Scripts\Activate.ps1

# 2. Run system integrity check
python run_platform.py --check

# 3. Run complete automated 34-test pytest verification suite
python run_platform.py --test

# 4. Start backend server (Uvicorn on port 8000)
python run_platform.py --port 8000

# 5. Start frontend UI (in a separate terminal)
cd frontend
npm run dev
```

*Frontend will be live at `http://localhost:5173`, connecting to the FastAPI backend at `http://localhost:8000`.*
