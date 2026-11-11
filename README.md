# MCA-ML

# Integrated Hospital Operations Intelligence, Resource Optimization & Patient Continuity Platform

An AI-powered hospital operations intelligence and decision-support platform designed to forecast patient demand, evaluate usable operational capacity, optimize resource allocations using Mixed-Integer Linear Programming (PuLP), and support patient continuity through explainable AI (SHAP).

## Academic & Project Context
- **Course:** Master of Computer Applications (MCA) — III Semester — Machine Learning
- **Repository:** [MCA-ML](https://github.com/smithlivingstonofficial/MCA-ML.git)
- **Status:** Complete Delivery — All Phases 0, 1, 2, 3, 4 & 5 Fully Implemented and Verified ✅
- **Automated Test Suite:** 34 / 34 Tests Passing (100% Coverage across All Modules)

---

## The 7 Modules

1. **Intelligent Patient Flow & Emergency Management:** Hourly emergency arrivals forecasting (24h/48h/72h), queue waiting time estimation, and overcrowding risk prediction using HistGradientBoosting (Poisson deviance loss) yielding 30.45% WAPE (+25.48% improvement over seasonal baseline).
2. **Predictive Bed & Capacity Management:** Operational staffed bed usability, Length of Stay (LOS) estimation, and strict 6-state bed lifecycle FSM (`Ready`, `Reserved`, `Occupied`, `Cleaning`, `Maintenance`, `Blocked`).
3. **Smart Medical Inventory & Equipment Intelligence:** Medicine batch/lot tracking, First Expiry First Out (FEFO) dispensing, expired stock quarantine, oxygen supply telemetry, and ventilator utilization fleet tracking.
4. **Workforce & Clinical Staff Intelligence:** Shift scheduling, doctor/nurse roster availability, and acuity-driven staffing deficit detection (ICU 1:1, ED 1:3, Med-Surg 1:4).
5. **Predictive Resource Planning & Optimization Engine:** Mixed-Integer Linear Programming (MILP) with PuLP & HiGHS solver for dynamic bed and acuity allocation under hard clinical constraints, paired with interactive What-If Crisis surge simulation.
6. **Patient Continuity & Predictive Risk Intelligence:** 30-day readmission risk classification (ROC-AUC 0.748), appointment no-show prediction, and local TreeSHAP waterfall explainability for clinical decision support.
7. **Hospital Operations Command Center & Model Governance:** Centralized dark-mode telemetry dashboard, Population Stability Index (PSI) drift monitoring, two-sample Kolmogorov-Smirnov distribution tests, and data quality integrity audits.

---

## Repository Documentation

Comprehensive architectural and design specifications are located in the [`docs/`](./docs) directory:
- [Academic Evaluation & Viva Defense Report](./docs/ACADEMIC_EVALUATION_REPORT.md) — Comprehensive capstone benchmark report, empirical validation tables, and viva Q&A guide.
- [Project Blueprint](./docs/PROJECT_BLUEPRINT.md) — Scope, traceability matrix, and MVP definition.
- [System Architecture](./docs/ARCHITECTURE.md) — Monorepo layout, state machines, PuLP solver formulation, and data flow.
- [Canonical Data Model](./docs/DATA_MODEL.md) — Entity-relationship diagrams and schema definitions.
- [Machine Learning Roadmap](./docs/ML_ROADMAP.md) — Target variables, feature engineering, baselines, and drift monitoring.
- [Implementation Roadmap](./docs/IMPLEMENTATION_ROADMAP.md) — Phased backlog, acceptance criteria, and task timeline.

---

## Running the Application Locally

### 1. Platform Single-Command Launcher
```powershell
# Run system integrity diagnostics
python run_platform.py --check

# Run complete 34-test automated verification suite
python run_platform.py --test

# Launch FastAPI backend on port 8000
python run_platform.py --port 8000
```
- OpenAPI interactive documentation available at: `http://127.0.0.1:8000/docs`
- Health check endpoint: `http://127.0.0.1:8000/health`

### 2. Start the Frontend Dashboard (React + Vite)
```powershell
cd frontend
npm run dev
```
- Command Center dashboard available at: `http://localhost:5173`

### 3. Run Automated Pytest Suite
```powershell
.\.venv\Scripts\pytest -v
```

---

## Technology Stack

- **Backend:** Python 3.11+ / 3.14, FastAPI, Pydantic v2, SQLAlchemy 2.0, Uvicorn
- **Machine Learning & Explainability:** Scikit-Learn (HistGradientBoosting), SciPy, TreeSHAP, Pandas, NumPy
- **Optimization Solver:** PuLP 4.2 with HiGHS Rust MILP Solver
- **Database:** SQLite (Local Dev Zero-Friction) / Alembic-ready for PostgreSQL
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons, TanStack React Query
