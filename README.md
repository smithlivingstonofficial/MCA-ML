# MCA-ML

# Integrated Hospital Operations Intelligence, Resource Optimization & Patient Continuity Platform

An AI-powered hospital operations intelligence and decision-support platform designed to forecast patient demand, evaluate usable operational capacity, optimize resource allocations using Mixed-Integer Linear Programming (PuLP), and support patient continuity through explainable AI (SHAP).

## Academic & Project Context
- **Course:** Master of Computer Applications (MCA) — III Semester — Machine Learning
- **Repository:** [MCA-ML](https://github.com/smithlivingstonofficial/MCA-ML.git)
- **Status:** Phase 0 & Phase 1 (Operational MVP) Completed ✅ / Phase 2 (Resource Intelligence) Next

---

## The 7 Modules

1. **Intelligent Patient Flow & Emergency Management:** Hourly emergency arrivals forecasting (24h/48h/72h), queue waiting time estimation, and overcrowding risk prediction.
2. **Predictive Bed & Capacity Management:** Operational staffed bed usability, Length of Stay (LOS) estimation, and bed release forecasting across a 6-state lifecycle (`Ready`, `Reserved`, `Occupied`, `Cleaning`, `Maintenance`, `Blocked`).
3. **Smart Medical Inventory & Equipment Intelligence:** Medicine batch/lot tracking, First Expiry First Out (FEFO) dispensing, oxygen supplies, and critical equipment (ventilators).
4. **Workforce & Clinical Staff Intelligence:** Shift scheduling, doctor/nurse availability, and acuity-driven staffing deficit detection.
5. **Predictive Resource Planning & Optimization Engine:** Mixed-Integer Linear Programming (MILP) with PuLP (CBC Solver) for dynamic bed and acuity allocation under hard clinical constraints.
6. **Patient Continuity & Predictive Risk Intelligence:** 30-day readmission risk classification, appointment no-show prediction, and SHAP explainability.
7. **Hospital Operations Command Center & Model Governance:** Centralized dark-mode telemetry dashboard, Population Stability Index (PSI) drift monitoring, and audit trails.

---

## Repository Documentation

Comprehensive architectural and design specifications are located in the [`docs/`](./docs) directory:
- [Project Blueprint](./docs/PROJECT_BLUEPRINT.md) — Scope, traceability matrix, and MVP definition.
- [System Architecture](./docs/ARCHITECTURE.md) — Monorepo layout, state machines, PuLP solver formulation, and data flow.
- [Canonical Data Model](./docs/DATA_MODEL.md) — Entity-relationship diagrams and schema definitions.
- [Machine Learning Roadmap](./docs/ML_ROADMAP.md) — Target variables, feature engineering, baselines, and drift monitoring.
- [Implementation Roadmap](./docs/IMPLEMENTATION_ROADMAP.md) — Phased backlog, acceptance criteria, and task timeline.

---

## Running the Application Locally

### 1. Start the Backend API (FastAPI)
```bash
# Activate virtual environment
.\.venv\Scripts\activate

# Run backend with uvicorn
python -m uvicorn backend.app.main:app --reload --port 8000
```
- OpenAPI interactive documentation available at: `http://127.0.0.1:8000/docs`
- Health check endpoint: `http://127.0.0.1:8000/health`

### 2. Start the Frontend Dashboard (React + Vite)
```bash
cd frontend
npm run dev
```
- Command Center dashboard available at: `http://localhost:5173`

### 3. Run Automated Tests
```bash
.\.venv\Scripts\pytest -v
```

---

## Technology Stack

- **Backend:** Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0
- **Machine Learning:** Scikit-Learn, LightGBM, XGBoost, Statsmodels, SHAP
- **Optimization:** PuLP (CBC Solver)
- **Database:** SQLite (Local Dev) / PostgreSQL (Production)
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons
