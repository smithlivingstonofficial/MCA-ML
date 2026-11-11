# Project Memory — Integrated Hospital Operations Intelligence Platform

> This is the durable product and engineering memory for the project. Keep it accurate as decisions are made. Do not treat proposed features as implemented features. Update the decision log when a lasting decision changes.

## 1. Project identity

**Working title:** Integrated Hospital Operations Intelligence, Resource Optimization & Patient Continuity Platform

**Short description:** An AI-powered hospital decision-support platform that integrates operational data, forecasts patient demand and resource constraints, evaluates feasible resource-allocation options, and supports continuity of patient care through explainable, human-supervised insights.

**Project category:** Healthcare operations intelligence / predictive analytics / resource optimization / decision-support software.

**Primary users:** Hospital administrators, operations managers, bed managers, emergency department operations staff, pharmacy and inventory managers, workforce planners, authorized clinical reviewers, and platform administrators.

**Development context:** Build a credible, testable ML project that can begin as an academic/research prototype and evolve toward a hospital-pilot-ready product. Prefer cost-conscious, open-source components where practical. Do not assume a hospital partnership, production data access, paid APIs, cloud budget or regulatory approval exists until confirmed.

**Current project status:** Concept and scope defined; implementation stack, dataset availability, target hospital workflow and deployment environment must be verified during repository and requirements discovery.

## 2. Product vision and positioning

The platform should help hospital teams:

1. Understand current operational conditions across departments.
2. Forecast near-future patient demand, waiting times, occupancy and resource requirements.
3. Identify likely capacity, workforce, inventory and equipment constraints early.
4. Compare feasible resource-allocation options under explicit hospital-defined constraints.
5. Simulate operational scenarios before authorized personnel act.
6. Identify patients who may benefit from additional follow-up support, where appropriate data and clinical governance exist.
7. Monitor data quality, model reliability, prediction uncertainty and drift over time.

**Positioning:** This is a decision-support and intelligence layer that should integrate with existing Hospital Information Systems (HIS), Electronic Health Records (EHR), Admission/Discharge/Transfer (ADT), pharmacy, inventory and workforce systems where feasible. It is not intended to replace those systems or become a full EHR/HMS in the initial project.

**Core product loop:** Observe → Validate → Predict → Explain → Optimize → Simulate → Human review → Monitor outcomes.

## 3. Consolidated abstract

Healthcare institutions face increasing challenges in managing fluctuating patient demand, hospital capacity constraints, workforce availability, medical inventory, equipment utilization and continuity of patient care. Traditional Hospital Management Systems primarily focus on recording and managing operational activities, with limited capabilities for predicting future demands, identifying potential resource shortages and coordinating decisions across hospital departments. This project proposes an Integrated Hospital Operations Intelligence, Resource Optimization and Patient Continuity Platform, an AI-powered decision-support system designed to improve hospital operational visibility, predictive planning and resource utilization through Machine Learning, predictive analytics and mathematical optimization.

The proposed platform integrates hospital operational data from patient admission, discharge and transfer records, emergency departments, bed management systems, medical inventory, equipment tracking and staff scheduling into a unified and validated data architecture. Its patient flow intelligence module analyzes patient movement, estimates waiting times, forecasts emergency arrivals and identifies potential overcrowding risks over 24-, 48- and 72-hour periods. The predictive bed and capacity management module monitors operational bed availability, estimates Length of Stay (LOS), forecasts future bed requirements and evaluates hospital capacity under changing demand conditions. The medical inventory and equipment intelligence module manages medicine stocks, expiry dates, oxygen supplies, ventilators, blood inventory and equipment availability while forecasting consumption patterns and identifying potential stock-out risks. Workforce intelligence evaluates department-wise doctor and nurse availability, shift schedules, workload requirements and potential staffing shortages.

An integrated resource forecasting and optimization engine combines predictions from these modules to evaluate resource requirements and generate feasible department-wise allocation recommendations using Linear Programming and Mixed-Integer Programming techniques implemented through PuLP. It also supports what-if scenario simulation to assess the operational impact of emergency surges, capacity changes and resource constraints. The patient continuity module extends the platform beyond hospital operations by estimating 30-day readmission and follow-up appointment non-attendance risks, enabling healthcare teams to identify patients who may benefit from proactive follow-up support. Explainable AI techniques, including SHAP, provide insights into model predictions, while anomaly detection helps identify unusual operational patterns.

A centralized Hospital Operations Intelligence Dashboard brings together operational monitoring, predictive forecasts, prioritized alerts, resource utilization analytics and optimization recommendations. The platform also incorporates data quality validation, secure data access, audit logging, model performance monitoring and data drift detection to support reliable and responsible system operation. Designed for interoperability with existing hospital information systems, the proposed solution aims to provide a scalable and configurable decision-support framework without requiring the replacement of existing hospital infrastructure. All clinical and safety-critical decisions remain under the supervision of authorized healthcare professionals.

The overall objective is to transform conventional hospital operations into a predictive, coordinated and data-driven ecosystem that anticipates operational challenges, supports efficient resource allocation, improves hospital capacity planning and strengthens continuity of patient care. Effectiveness must be assessed through historical data validation, predictive model evaluation, optimization experiments, scenario simulations and supervised pilot testing. These are intended outcomes, not claims of already achieved improvements.

## 4. Scope and module requirements

### Module 1 — Intelligent Patient Flow & Emergency Management

**Purpose:** Understand and forecast movement of patients through the hospital.

- Admission, discharge and interdepartmental transfer tracking.
- Aggregate emergency arrival forecasting by department and time interval.
- Waiting-time estimation using queue conditions and recorded triage categories.
- Overcrowding-risk forecasting for 24-, 48- and 72-hour horizons.
- Patient flow monitoring across emergency, wards, ICU and discharge.
- Department-wise demand analysis and delay/bottleneck identification.

**Rules:** Waiting-time forecasts must never replace triage. Clinical urgency and triage priority are determined by authorized clinical staff. Forecasts should indicate their time window, freshness and uncertainty.

### Module 2 — Predictive Bed & Hospital Capacity Management

**Purpose:** Estimate usable operational capacity, not just physically empty beds.

- General ward, ICU, emergency and surgery/post-operative bed capacity.
- Bed state and status history.
- Length of Stay estimation and expected bed-release forecasting.
- Future bed demand and occupancy projections.
- Capacity simulation for surges, discharges, maintenance and temporary closures.

**Bed-state concepts to model explicitly:** occupied, reserved, cleaning, blocked, maintenance, ready/available and other hospital-approved states. Define states so a bed cannot be counted in two mutually exclusive categories at the same time.

**Operational capacity principle:** An empty physical bed may not be usable. Usability may depend on cleaning status, maintenance, specialty/acuity compatibility, required equipment, isolation requirements and available qualified staff. Define hospital-specific rules with authorized operational stakeholders. Do not hard-code one universal capacity formula.

### Module 3 — Smart Medical Inventory & Equipment Intelligence

- Medicine inventory with item, batch/lot, quantity, location and expiry tracking.
- FEFO (First Expiry, First Out) support where applicable.
- Low-stock and reorder alerts.
- Consumption forecasting and stock-out risk estimation.
- Supplier lead time, safety stock and replenishment information.
- Oxygen supply tracking, including the relevant local measurement and refill process.
- Ventilator and other critical equipment availability, location, utilization and maintenance state.
- Blood-component inventory and expiry records, integrated with authorized blood-bank workflows.

**Rules:** Never make independent blood compatibility or transfusion allocation decisions. Represent stock movements as auditable transactions. Avoid treating all stock as interchangeable; preserve unit, batch, location, expiry and item-specific constraints.

### Module 4 — Workforce & Clinical Staff Intelligence

- Doctor and nurse availability by department and shift.
- Duty schedules, roster, leave, absence and assignment tracking where authorized.
- Emergency/on-call coverage.
- Predicted workforce demand and potential coverage gaps.
- Skill-mix and qualification-aware analysis.
- Department-wise workload and workforce reports.

**Rules:** Patient count alone is not enough to calculate staffing need. Consider patient dependency/workload, department, shift, qualifications, minimum coverage rules, existing assignments, leave and hospital-defined standards. Recommendations are advisory and require manager approval. Do not autonomously publish or alter a duty roster.

### Module 5 — Predictive Resource Planning & Optimization Engine

**Purpose:** Consume forecasts from Modules 1–4 and evaluate feasible allocation options. Do not duplicate forecasting logic already owned by those modules.

- Combined resource-demand picture.
- Shortage and bottleneck detection.
- Department-wise resource allocation recommendations.
- Bed, staff, equipment and inventory planning within defined scopes.
- What-if scenario simulation.
- Optimization run history, input snapshots, solver status and recommendation explanations.

**Optimization methods:** Linear Programming and Mixed-Integer Linear Programming using PuLP. A discrete-event simulation tool such as SimPy may be considered for queue/flow scenarios if the use case justifies it.

**Optimization safety:** Separate hard constraints from soft objectives. Hard constraints may include bed/specialty compatibility, required equipment, minimum staffing, qualifications, stock availability, location restrictions and hospital-approved safety policies. The solver must never relax hard constraints just to find a solution. If constraints are infeasible, return an explicit infeasible status and explain which constraints conflict where possible. Do not invent an allocation. All recommendations require authorized human review.

### Module 6 — Patient Continuity & Predictive Risk Intelligence

- 30-day readmission risk estimation.
- Follow-up appointment non-attendance risk estimation.
- Patient segmentation only where the segments lead to a clear, reviewed operational use.
- Anomaly detection for data or operational patterns.
- SHAP-based feature-contribution explanations for supported models.
- Model calibration, subgroup evaluation and risk monitoring.

**Rules:** These models are support signals, not diagnoses or treatment recommendations. Do not use a prediction to deny admission, lower care priority, force discharge or withhold services. A no-show score should support reminders and barrier-reduction outreach, not punishment. SHAP shows model feature contributions, not causation. Require appropriate clinical/data governance and lawful access before using patient-level records. This module is later-phase and must not delay the operational MVP.

### Module 7 — Hospital Operations Command Center & Model Governance

- Hospital-wide and department-level operational analytics.
- Bed occupancy, patient flow, workforce coverage and inventory utilization.
- Predictions, forecast ranges, data freshness and confidence/uncertainty context.
- Prioritized alerts with severity, source, timestamp, owner and status.
- Recommendation and scenario comparison.
- Model registry/version information and performance monitoring.
- Data quality and drift monitoring.
- Audit trails and historical prediction/decision records.

**Display principle:** Clearly distinguish (1) observed operational facts, (2) forecasts, (3) anomaly alerts, (4) simulated scenarios and (5) proposed actions. Do not display all five as if they were equally certain facts.

## 5. Shared architecture principles

Use a modular architecture with clear boundaries. A conceptual data flow is:

1. Source systems or authorized manual/import workflows.
2. Integration adapters and ingestion jobs.
3. Raw/staging layer with source provenance.
4. Data validation, normalization and canonical operational data model.
5. Operational database and versioned analytical/feature datasets.
6. Forecasting and risk-model services.
7. Optimization and scenario-simulation services.
8. API/application services with authentication and authorization.
9. Responsive operations dashboard and reports.
10. Feedback, audit events, model monitoring and outcome capture.

Do not assume every hospital has a real-time feed. Support scheduled batch ingestion and manual/demo imports initially. Every view should show the last successful refresh and source status. Use real-time claims only when a real streaming/feed integration has been implemented and tested.

### Suggested logical boundaries

- `frontend`: dashboard, forms, tables, charts and user workflows.
- `backend/api`: authentication, authorization, request/response schemas and API routes.
- `backend/domain`: hospital business rules and services.
- `backend/data`: database models, repositories, migrations and ingestion.
- `ml`: dataset preparation, features, baselines, training, evaluation and inference.
- `optimization`: decision variables, objective functions, hard/soft constraints, solver adapters and results.
- `simulation`: scenario definitions and simulation execution where needed.
- `integrations`: adapters and mappings for external hospital systems.
- `tests`: unit, integration, API, data, model and optimization tests.
- `docs`: architecture, data dictionary, API contracts, model cards, decisions and runbooks.

This is a conceptual organization, not a command to force these exact folders into an existing repository. Inspect the repository first.

## 6. Recommended technology direction (provisional, not yet locked)

Choose technology based on the existing repository, the academic deliverable, local hardware, deployment target and team capability. Do not install a stack before inspecting what already exists.

**Possible default reference stack:**

- ML/API backend: Python 3.11+ with FastAPI and Pydantic.
- Data processing: pandas, NumPy and SciPy.
- Baseline/statistical/ML models: scikit-learn and statsmodels; XGBoost only where validation justifies it.
- Optimization: PuLP; evaluate solver availability/licensing and problem size before choosing a solver.
- Explainability: SHAP for compatible models.
- Simulation: SimPy if discrete-event simulation is needed.
- Database: PostgreSQL with SQLAlchemy and Alembic, if a relational store is suitable.
- Frontend: React + TypeScript; choose Next.js or Vite after repository and routing/deployment needs are reviewed.
- Testing: pytest for Python; use the existing frontend test framework or select one compatible with the chosen UI stack.
- Packaging/local services: use a simple local setup first; Docker Compose may be added if it reduces setup friction.

Do not add Redis, Kafka, Kubernetes, cloud ML platforms, vector databases, paid APIs or microservices by default. Introduce infrastructure only when a measured requirement exists.

## 7. Data strategy and canonical entities

### Initial data approach

If real hospital data is not available, use clearly labelled synthetic data for software development, demonstrations and pipeline testing. Make the generator reproducible with a fixed seed and document every assumption. Synthetic data is not evidence of real-world model performance.

Before using an external dataset, document:

- Original source and dataset name.
- Collection/publication date and relevant time period.
- Licence and permitted use.
- Data dictionary and target definition.
- Missingness and known limitations.
- De-identification/privacy conditions.
- Whether data can be redistributed or committed (usually do not commit raw data).

Never scrape private patient portals or obtain data through unauthorized access. Never commit real or identifiable patient records.

### Candidate canonical entities

Define the schema only after mapping real requirements. Candidate entities include:

- `Hospital`, `Department`, `Ward`, `Bed`, `BedStatusEvent`.
- `PatientReference` (pseudonymous analytics reference; keep identity mapping outside analytics where possible).
- `Encounter`, `Admission`, `Discharge`, `Transfer`, `TriageObservation` (only fields approved for the use case).
- `StaffMember`, `StaffRole`, `Qualification`, `Shift`, `RosterAssignment`, `LeaveOrAbsence`.
- `InventoryItem`, `InventoryLot`, `StockMovement`, `Supplier`, `ReplenishmentLeadTime`.
- `Equipment`, `EquipmentStatusEvent`, `MaintenanceEvent`.
- `BloodComponentStock` for authorized inventory integration only.
- `ForecastRun`, `Forecast`, `ModelVersion`, `Prediction`, `ModelEvaluation`.
- `Alert`, `Scenario`, `OptimizationRun`, `OptimizationConstraint`, `Recommendation`, `RecommendationReview`.
- `DataQualityIssue`, `SourceIngestionRun`, `AuditEvent`.

Do not create an unnecessary patient identity table if a pseudonymous encounter-level reference is sufficient. Keep external source identifiers and mappings protected and separate from model feature tables.

### Data quality checks

Validate, at minimum, where relevant:

- Required fields and timestamp validity.
- Duplicate encounters, events and source messages.
- Admission/discharge/transfer time ordering.
- Impossible or conflicting bed state transitions.
- Negative or inconsistent inventory balances.
- Expiry dates, units of measure and batch consistency.
- Staff assignment overlaps and qualification validity.
- Stale source data and missing time periods.
- Out-of-range numeric values and unexpected category values.

Invalid or stale data should be quarantined or clearly flagged. Do not silently coerce important errors into plausible values. Preserve source provenance and validation outcomes.

## 8. Machine-learning and forecasting principles

### Model selection

Start with transparent baselines. Compare more complex models only when they demonstrate meaningful out-of-sample improvement and acceptable calibration/operational usefulness.

Candidate approaches (not mandatory choices):

- Emergency arrivals: naive/seasonal-naive baselines, statistical time-series methods, regression with calendar/operational features, gradient boosting.
- Waiting time: quantile regression or regression models with queue, time, department and priority context; evaluate prediction intervals.
- Overcrowding: forecast demand and usable capacity, then calculate risk using hospital-defined thresholds; consider classification only when labels and decision thresholds are reliable.
- Length of Stay: regression or survival analysis depending on censoring and intended target.
- Bed demand: time-series/demand forecasting plus capacity rules and scenario modelling.
- Medicine/consumable demand: time-series or intermittent-demand methods as appropriate; incorporate supplier lead time and safety stock for shortage risk.
- Workforce demand: workload-based demand modelling and schedule/coverage constraints.
- Readmission/no-show: baseline logistic regression and tree-based classifiers; evaluate calibration and subgroup performance.
- Segmentation: clustering only with a clear operational purpose and documented stability.
- Anomalies: statistical rules and Isolation Forest as candidates; validate alert usefulness and false-positive burden.

### Validation rules

- Define prediction target, observation time, forecast horizon and prediction unit before feature engineering.
- Use time-based/rolling-origin validation for time-series tasks.
- Prevent future-information leakage: only use data available at the prediction timestamp.
- Where patient-level predictions are used, consider patient-level grouping to prevent the same patient's information leaking between train and test.
- Keep a final untouched evaluation period where data volume permits.
- Compare against a simple baseline and document why a model is selected.
- Report metrics suited to the task, not accuracy alone.
- Track confidence intervals, calibration, subgroup performance and operational false-alert burden where applicable.
- Never fabricate model metrics. Label demo metrics as synthetic-data results.

### Suggested evaluation metrics

- Forecasting/regression: MAE, RMSE, WAPE or MASE where suitable; prediction interval coverage and width.
- Classification: precision, recall/sensitivity, specificity, F1, PR-AUC, ROC-AUC where appropriate, calibration and confusion matrix at an explicitly chosen threshold.
- Overcrowding alerts: event-level recall, false alarms per time period and warning lead time.
- Optimization: feasibility, hard-constraint violations (must be zero), unmet demand, objective value and sensitivity to assumptions.
- Operations: compare operational KPIs only with appropriate baseline and pilot design; do not infer causal impact from a demo.

## 9. Resource optimization and simulation principles

Before implementing a solver, define:

1. Decision variables and their units.
2. Planning horizon and time granularity.
3. Objective function and priorities.
4. Hard constraints that can never be violated.
5. Soft constraints/penalties and how they are approved.
6. Required input data and its freshness.
7. Infeasibility handling.
8. Human review and approval workflow.

Save an immutable snapshot of solver inputs, constraints, software/model version, solver status and output for audit and reproducibility. Display assumptions. A solver's mathematically optimal result is not automatically operationally or clinically appropriate.

What-if simulation must clearly distinguish simulated inputs and outputs from actual hospital observations. Do not blend simulated scenario results into the live dashboard as actual data.

## 10. Patient continuity and clinical governance

- Treat readmission and no-show models as assistive prioritization signals for authorized care teams.
- Do not automate care decisions, discharge, admission, treatment, medication or triage.
- Assess class imbalance, calibration, subgroup fairness and consequences of false negatives/false positives.
- Avoid proxy features that could create unjustified discrimination; document feature rationale and review.
- Restrict access to patient-level information by role and purpose.
- Use aggregate or pseudonymized data whenever an individual-level record is not required.
- Document intended use, excluded uses, known limitations and escalation guidance in a model card.

## 11. Security, privacy and interoperability

- Apply role-based access control and least privilege.
- Separate identity-bearing clinical records from analytical feature datasets where possible.
- Encrypt data in transit and use appropriate encryption at rest for the chosen environment.
- Keep credentials in environment variables or managed secrets; include only placeholders in `.env.example`.
- Redact patient identifiers and sensitive fields from logs, traces, test output and screenshots.
- Log security-relevant access and consequential recommendation reviews without exposing unnecessary patient content.
- Define backup, recovery, retention and deletion expectations.
- Use only authorized data and confirm permitted use before importing or training.
- Consider HL7 FHIR-compatible mappings/APIs where source systems support them. Consider applicable Indian ABDM workflows and current requirements if the project is deployed in India.
- A standard mapping or API endpoint does not itself establish interoperability certification, ABDM compliance or legal compliance. Validate against the relevant current specifications and processes.

## 12. Dashboard and interaction principles

The dashboard should serve different roles with role-appropriate views and permissions. Candidate screens:

- Executive/hospital operations overview.
- Patient flow and emergency demand.
- Bed and capacity status.
- Inventory and critical equipment.
- Workforce coverage.
- Forecasts and alert inbox.
- Resource optimization and scenario simulation.
- Patient continuity (restricted, authorized users only).
- Analytics, model performance and data quality.
- Administration, roles, source integrations and audit history.

Every forecast panel should communicate:

- What is being predicted.
- Which department/location and time horizon it covers.
- When its input data was refreshed.
- When the prediction was generated.
- Estimate plus uncertainty/range where available.
- Important limitations or unavailable data.
- Whether it is a forecast, not an observed fact.

Do not use color as the only signal. Provide labels/icons/text for status and accessible contrast. Avoid unnecessary charts or metrics without an operational decision they support.

## 13. Development phases and scope control

### Phase 0 — Discovery and blueprint

- Inspect repository and existing code.
- Confirm development environment and intended deployment.
- Define workflows, roles, assumptions and acceptance criteria.
- Define data dictionary, canonical entities and architecture.
- Confirm data source/licence/privacy feasibility.

**Deliverable:** approved technical blueprint, repository plan, data model proposal and MVP backlog.

### Phase 1 — Operational MVP

- Admission/discharge/transfer tracking (or safe demo workflow if data is unavailable).
- Operational bed status and capacity calculations.
- Emergency arrival data pipeline and baseline forecast.
- 24/48/72-hour overcrowding/bed-demand forecast prototype.
- Central operations dashboard with freshness and data-quality indicators.

**Deliverable:** one end-to-end demonstrable workflow using synthetic or authorized data.

### Phase 2 — Resource intelligence

- Medicine and inventory records, batch/expiry and stock movements.
- Consumption/stock-out forecasting.
- Equipment availability and maintenance tracking.
- Workforce roster/coverage and workload forecasting.

### Phase 3 — Optimization and simulation

- Constraint definitions.
- PuLP optimization model and infeasibility reporting.
- What-if scenarios and comparison interface.
- Audit and review workflow for recommendations.

### Phase 4 — Patient continuity and advanced intelligence

- Readmission/no-show risk modelling where permitted data exists.
- Explainability, anomaly detection and fairness/calibration assessment.
- Clinical governance and model cards.

### Phase 5 — Validation and pilot readiness

- Historical replay, backtesting, integration/security tests.
- Shadow-mode evaluation.
- User acceptance and supervised pilot design.
- Operational KPI evaluation with limitations clearly documented.

**Scope rule:** Do not start all seven modules simultaneously. Complete a thin end-to-end slice, prove the data contracts and validation pipeline, then expand module by module.

## 14. Definition of done for a feature

A feature is not complete merely because a UI screen or model file exists. Where applicable, completion requires:

- Documented user need and acceptance criteria.
- Validated data contract and timestamp semantics.
- Backend/domain logic separated from presentation.
- Authorization and audit considerations addressed.
- Input validation and failure/empty/stale-data states handled.
- Unit and integration tests.
- Model baseline and evaluation for ML functionality.
- Hard-constraint tests for optimization functionality.
- Responsive and accessible UI states.
- Useful documentation, configuration example and run instructions.
- Actual test results reported without exaggeration.

## 15. Project decisions and assumptions register

Keep this table current. Add a date and rationale when a decision is confirmed or changed.

| Topic | Current position | Status |
|---|---|---|
| Product identity | Hospital operations intelligence and decision-support platform | Confirmed concept |
| Initial focus | Operational MVP before advanced patient-risk modelling | Confirmed plan |
| Existing HIS/EHR | Integrate where feasible; do not replace initially | Design principle |
| Data availability | High-fidelity multi-scenario synthetic generator with reproducible seed | Confirmed choice |
| Real patient data | None used; synthetic data ensures total privacy and zero PII leakage | Confirmed rule |
| Frontend stack | React 18 + TypeScript (Vite) + Tailwind CSS (Dark-mode telemetry command center) | Confirmed choice |
| Backend stack | Python 3.11+ with FastAPI, Pydantic v2, SQLAlchemy 2.0 | Confirmed choice |
| Database | SQLite for local zero-friction reproducibility (Alembic-ready for PostgreSQL) | Confirmed choice |
| ML algorithms | Seasonal Naive vs. LightGBM / XGBoost / Random Forest + SHAP explainability | Confirmed plan |
| Forecast horizon | Hourly ED arrival & bed demand projections across 24h, 48h, and 72h | Confirmed choice |
| Bed capacity | Operational Staffed Capacity (only ready & staffed beds are operational) | Confirmed rule |
| Optimization | PuLP Mixed-Integer Linear Programming (CBC Solver) for Dynamic Bed & Acuity Allocation | Confirmed choice |
| Simulation | Interactive What-If surge sliders & crisis templates (Flu, Mass Casualty) | Confirmed choice |
| Governance | Population Stability Index (PSI), KS tests, and rolling residual error monitoring | Confirmed choice |
| Repository layout | Clean Modular Monorepo (/backend, /frontend, /data, /docs, /tests) | Confirmed choice |

## 16. Decision log

Append durable decisions here. Do not erase history; mark superseded decisions clearly.

| Date | Decision | Rationale / impact | Status |
|---|---|---|---|
| 2026-11-10 | Consolidate the original seven modules into one integrated hospital intelligence platform with shared data, prediction and optimization layers | Avoid disconnected mini-projects and duplicate forecasting responsibilities | Active |
| 2026-11-10 | Treat the platform as human-supervised decision support, not autonomous clinical software | Protect clinical accountability and prevent unsafe automation | Active |
| 2026-11-10 | Build operational MVP before patient continuity risk models | Reduce data, governance and implementation risk while proving the core workflow | Active |
| 2026-11-10 | Adopt FastAPI + React/TS (Vite) modular monorepo with SQLite and Dark Mode Command Center | Ensures high visual fidelity for hospital operations telemetry and zero-friction local execution on Windows | Active |
| 2026-11-10 | Commit to seed-controlled Multi-Scenario Synthetic Data Generator | Enables deterministic testing across baseline, surge, and catastrophe scenarios without privacy exposure | Active |
| 2026-11-10 | Implement PuLP MILP for Dynamic Bed & Acuity Allocation with strict hard constraints | Prevents unsafe clinical assignments; returns explicit infeasible diagnostics when capacity is exceeded | Active |
| 2026-11-10 | Finalize and approve Phase 0 Documentation Suite in `docs/` | Formulates the definitive architecture, data model, ML roadmap, and implementation backlog | Active |
