# Implementation Roadmap & Task Backlog: Integrated Hospital Operations Intelligence

**Document Version:** 1.0.0  
**Status:** Approved Phase 0 Baseline  
**Execution Paradigm:** Agile Phased Delivery with Automated Test-Driven Verification  

---

## 1. Phased Delivery Overview

```mermaid
flowchart TD
    P0["Phase 0: Discovery & Blueprint (COMPLETED)"]
    P1["Phase 1: Operational MVP (M1, M2, M7 Foundation)"]
    P2["Phase 2: Resource Intelligence (M3 Inventory, M4 Workforce)"]
    P3["Phase 3: Mathematical Optimization & Simulation (M5 PuLP Engine)"]
    P4["Phase 4: Patient Continuity & Explainable AI (M6 SHAP Models)"]
    P5["Phase 5: Governance, Evaluation & Viva Defense Readiness"]

    P0 --> P1 --> P2 --> P3 --> P4 --> P5
```

---

## 2. Detailed Phase Backlog & Acceptance Criteria

### Phase 0: Discovery, Architecture & Baseline Specifications (Status: DONE ✅)
* [x] Review workspace instructions, `AGENTS.md`, and `PROJECT_MEMORY.md`.
* [x] Verify local environment (Python 3.11.4, Node.js v20.19.2, Git).
* [x] Formulate architecture, monorepo layout, and canonical data models.
* [x] Author comprehensive documentation suite in `docs/`.

---

### Phase 1: Operational Minimum Viable Product (MVP)
**Focus:** Connect the complete loop for patient flow, bed capacity, and command-center visualization.

* **Task 1.1: Project Scaffolding & Environment Setup**
  * Initialize `/backend` with FastAPI, SQLAlchemy 2.0, Pydantic v2, and SQLite.
  * Initialize `/frontend` with Vite + React 18 + TypeScript + Tailwind CSS + Lucide Icons.
  * Configure environment configuration (`.env.example`) and CORS boundaries.
* **Task 1.2: Synthetic Healthcare Data Engine (`/data/generator`)**
  * Build deterministic synthetic generator with seed control (`numpy.random.default_rng`).
  * Generate 6 months of historical hospital data: 4 departments, 8 wards, 120 beds, 15,000 encounters, and hourly arrival aggregates.
  * Implement multi-scenario generator: Baseline routines, weekend dips/peaks, and seasonal surge events.
* **Task 1.3: Module 1 — Emergency Department Arrival Forecasting**
  * Feature pipeline: Cyclical hours, day-of-week, lag variables (24h, 168h), rolling 6h/24h statistics.
  * Baseline model: Seasonal Naive ($t-168$).
  * Primary model: Tuned LightGBM regressor with Poisson objective.
  * Rolling-origin backtesting evaluating MAE, RMSE, and WAPE across 24h, 48h, and 72h horizons.
* **Task 1.4: Module 2 — Operational Bed Usability & Lifecycle State Machine**
  * Implement 6-state transition validator: `Ready` ➔ `Reserved` ➔ `Occupied` ➔ `Cleaning` ➔ `Maintenance` / `Blocked`.
  * Compute real-time operational capacity: Physical bed count vs. Staffed usable capacity based on on-duty nurse ratios.
* **Task 1.5: Module 7 — Operations Command Center (Dark Mode Telemetry)**
  * Hospital Executive Telemetry header: Total census, staffed occupancy %, ED arrivals (last 24h), active alerts.
  * Real-time 24h/48h/72h forecast chart with 80% prediction interval bands.
  * Interactive Bed Matrix component displaying color-coded statuses by ward with drill-down modals.
  * API integration using TanStack Query with loading, error, and stale data states.

**Phase 1 Acceptance Criteria:**
1. Backend runs locally (`uvicorn app.main:app`) and serves OpenAPI docs at `/docs`.
2. Frontend loads in dark mode (`npm run dev`) and renders live data without console errors.
3. LightGBM arrival model proves lower out-of-sample WAPE than the Seasonal Naive baseline on a 30-day holdout set.
4. Bed state transitions reject invalid transitions (e.g., admitting to a cleaning bed) with HTTP 422.

---

### Phase 2: Resource Intelligence (Modules 3 & 4)
* **Task 2.1: Module 3 — Pharmacy, Blood & Equipment Tracking**
  * Inventory management with batch/lot number, expiry date, and First Expiry, First Out (FEFO) dispensing logic.
  * Oxygen cylinder pressure/supply tracking and ventilator utilization tracking.
  * Intermittent demand consumption forecasting and low-stock reorder alerts.
* **Task 2.2: Module 4 — Workforce & Clinical Staff Intelligence**
  * Doctor and nurse shift scheduling across Morning, Evening, and Night shifts.
  * Dynamic acuity-based staffing deficit calculations (e.g., ICU 1:1, General Ward 1:4).
  * Departmental staff shortage warning triggers.

---

### Phase 3: Mathematical Optimization & Scenario Simulation (Module 5)
* **Task 3.1: PuLP Mathematical Optimization Engine**
  * Formulate Mixed-Integer Linear Programming (MILP) model for Dynamic Bed & Acuity Allocation.
  * Implement hard constraints: Acuity matching, infection isolation, and staffed ratio ceilings.
  * Implement soft objectives: Wait time minimization, inter-ward transfer penalties, capacity balancing.
  * Integrated CBC solver execution with execution time tracking and immutable input snapshots.
  * Explicit `INFEASIBLE` diagnostics preventing hallucinated allocations.
* **Task 3.2: What-If Scenario Simulator**
  * Interactive UI sliders: Arrival surge % multiplier, Staff absenteeism %, Out-of-service beds %.
  * One-click crisis templates: *“Flu Epidemic (+40% arrivals)”*, *“Mass Casualty (+80% trauma)”*, *“Blizzard (30% staff absent)”*.
  * Side-by-side comparative KPI matrix: Baseline vs. Simulated outcome.

---

### Phase 4: Patient Continuity & Explainable AI (Module 6)
* **Task 4.1: 30-Day Readmission Risk Classifier**
  * Train calibrated XGBoost classifier on index encounter features (LOS, diagnoses, prior visits).
  * Evaluate PR-AUC, ROC-AUC, and Brier calibration score against Logistic Regression baseline.
* **Task 4.2: SHAP Explainability Engine**
  * Integrate TreeExplainer to produce local waterfall plots for clinical review.
  * Interactive UI component explaining why a patient was flagged as high readmission risk.
* **Task 4.3: Follow-Up Appointment No-Show Predictor**
  * Classify non-attendance risk to support proactive reminder outreach.

---

### Phase 5: Model Governance, Verification & Academic Viva Defense
* **Task 5.1: Model Governance & Data Drift Suite (Module 7)**
  * Automated Population Stability Index (PSI) and Kolmogorov-Smirnov (KS) test calculations.
  * Rolling residual monitoring (MAE/RMSE tracking over sliding 7-day windows).
  * Data quality validation rules (timestamp ordering, range bounds, foreign key integrity).
* **Task 5.2: Comprehensive Test Suite & Reproducibility Documentation**
  * Pytest unit and integration tests covering API endpoints, bed state machine, ML leakage, and PuLP constraints.
  * Single-command local startup script and evaluation benchmark report for academic submission.

---

## 3. Immediate Next Implementation Step (Task 1.1)

With Phase 0 documentation completed and approved, the immediate next step is **Task 1.1 & 1.2: Repository Scaffolding & Synthetic Data Generation**:
1. Create `/backend` skeleton with FastAPI, SQLAlchemy models, and SQLite database connection.
2. Build the seed-controlled synthetic generator in `/data/generator/` to produce the validated operational dataset.
3. Initialize the React + Vite + TypeScript `/frontend` app.
