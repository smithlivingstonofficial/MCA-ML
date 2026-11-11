---
name: hospital-ml-development
description: Plans, implements, tests and documents the Integrated Hospital Operations Intelligence, Resource Optimization and Patient Continuity Platform. Use when designing or changing hospital workflows, healthcare data pipelines, forecasting models, bed or inventory capacity logic, workforce analytics, PuLP optimization, simulations, dashboards, security, model validation or project architecture.
---

# Hospital ML Platform Development Skill

## Mission

Act as a careful lead software architect, data engineer, ML engineer and implementation partner for this project. Deliver a coherent, testable hospital decision-support platform in small increments. Follow the repository `AGENTS.md` and `PROJECT_MEMORY.md`; they define the product and its non-negotiable constraints.

This skill describes the workflow for development tasks. It does not authorize autonomous clinical decisions, use of unauthorized patient data, unreviewed deployment or claims of regulatory compliance.

## 1. Start every task with discovery

1. Read the root `AGENTS.md` and relevant project memory.
2. Inspect the repository tree, Git status, existing README, dependency files, tests, migrations, environment examples and current architecture.
3. Identify the current stack and versions from the actual repository. Do not assume the provisional stack in memory has been approved.
4. Locate the relevant module, data contracts, domain services, API routes, UI and tests before editing.
5. Identify any existing implementation that must be preserved.
6. Check whether a similar feature or helper already exists before introducing another one.

Do not install packages, replace frameworks, delete files or rewrite architecture before this inspection.

## 2. Classify the request and choose the right workflow

- **Planning/architecture:** Produce requirements, diagrams in text/Mermaid where useful, boundaries, data model, API contracts, risks, acceptance criteria and a phased plan. Do not start a large implementation unless requested.
- **New feature:** Trace the end-to-end flow, define data contracts, implement a small vertical slice, test it, document it and report results.
- **Bug fix:** Reproduce or isolate the cause, create a regression test, apply the smallest safe fix and run relevant tests.
- **ML task:** Define target, prediction timestamp, unit, horizon, baseline, leakage controls, validation strategy and metrics before choosing the final algorithm.
- **Optimization task:** Define decision variables, objective, hard constraints, soft constraints, feasibility behaviour and review workflow before writing the PuLP model.
- **UI task:** Inspect existing design system and routes, preserve consistency, support loading/empty/error/stale states, and verify responsive layouts.
- **Data/integration task:** Inspect source schema and licence/authorization, create a mapping and validation plan, preserve provenance and handle incomplete/stale feeds.

If a request is broad or high impact, first provide a short implementation plan. For a small, unambiguous task, proceed without unnecessary ceremony.

## 3. Define a testable task contract

Before implementation, state or record:

- User/problem being addressed.
- In-scope and out-of-scope behaviour.
- Inputs, outputs, units, identifiers and timestamps.
- Data freshness and failure behaviour.
- Authorization and audit requirements.
- Safety or clinical constraints.
- Acceptance criteria.
- Tests and validation evidence required.

When details are missing, make the smallest safe provisional assumption and label it. Ask a question only if a missing fact materially changes a safety decision, a data-rights decision, an irreversible action or the architecture.

## 4. Preserve modular boundaries

Use the existing repository structure if it is sound. Otherwise, propose clear separation between:

- Presentation/UI.
- API and request/response contracts.
- Domain rules and use cases.
- Persistence and repository/data access.
- Integration/ingestion adapters.
- Feature engineering and ML training/inference.
- Optimization and simulation.
- Monitoring, audit and reporting.

Do not put business rules in React components, SQL models, notebooks or API route handlers. Keep training code separate from production inference. Keep optimization models independent from UI code. Use typed schemas at system boundaries.

Avoid needless microservices. A modular monolith or clearly separated Python packages are acceptable until scaling or organizational needs justify service separation.

## 5. Data engineering workflow

1. Identify source, licence/authorization and data owner.
2. Inspect schema and sample rows only if the data is approved for access.
3. Document field meanings, units, identifiers, timezone and source timestamp.
4. Preserve source provenance and ingestion timestamps.
5. Validate required fields, ranges, duplicates, referential integrity and temporal consistency.
6. Separate raw, validated and derived data where useful.
7. Quarantine invalid records or surface a clear data-quality issue; do not silently fabricate values.
8. Track data freshness and ingestion failures.
9. Use pseudonymous identifiers and minimum necessary data for analytical work.
10. Never commit patient data or credentials.

For synthetic data, use a fixed seed, documented generation rules, realistic but clearly fictional identifiers and internally consistent event timelines. Mark all demo outputs as synthetic.

## 6. ML development workflow

Follow this sequence for every predictive feature:

### A. Define the prediction

- Target variable and exact definition.
- Prediction unit (hospital, department, bed, encounter, patient, item or staff shift).
- Prediction timestamp (what was known at that moment).
- Forecast horizon (for example 24, 48 or 72 hours, or 30-day readmission).
- Expected update frequency and data-latency tolerance.
- Intended decision supported and explicitly excluded uses.

### B. Inspect and prepare data

- Check target quality, missingness, class imbalance, timestamp coverage and possible label delay.
- Identify leakage risks, patient/encounter overlap and future-derived features.
- Create time-aware features only from information available at prediction time.
- Document transformations and feature definitions.
- Keep preprocessing reproducible and fitted only on training data.

### C. Establish baselines

Use a simple, defensible baseline before complex models. Depending on the task, this may be last-value, moving average, seasonal naive, a rule-based capacity calculation, mean/median predictor or logistic/linear regression.

### D. Train and validate

- Use chronological splits or rolling-origin validation for forecasting.
- Use patient/encounter grouping where appropriate to avoid leakage.
- Preserve a final evaluation period where data volume allows.
- Tune only on training/validation data, never on the final test period.
- Compare candidates using appropriate metrics and operational consequences.
- Evaluate calibration, prediction intervals, subgroup performance and false-alert burden where relevant.

### E. Record and serve

Record model name/version, data window, feature version, training code/configuration, metric results, limitations and created timestamp. Keep inference inputs aligned with training features. Return a clear unavailable/low-confidence state when required inputs are missing or stale.

### F. Monitor

Track data freshness, schema changes, missingness, feature drift, prediction distribution, model performance when labels become available, calibration and operational alert volume. Do not automatically retrain or replace production models without a documented validation and approval process.

### Model-specific guidance

- **Emergency arrivals:** Aggregate by appropriate department and time bucket; consider calendar patterns, seasonality and known events only when available and permitted. Compare with seasonal-naive/statistical baselines.
- **Waiting time:** Define start/end events carefully; account for incomplete/ongoing cases and queue position. Report uncertainty. Never use the score to determine triage.
- **Overcrowding:** Define a hospital-approved operational threshold and forecast usable capacity as well as demand. Evaluate warning lead time and false alerts, not just classification accuracy.
- **Length of Stay:** Define whether the target is total LOS, remaining LOS or discharge probability. Handle censored/current admissions correctly; consider survival analysis when appropriate.
- **Bed demand:** Distinguish physical capacity, ready beds, compatible beds and staffed capacity. Avoid double-counting transfers and expected discharges.
- **Medicine demand/stock-out:** Preserve item, unit, lot, expiry, location, consumption and replenishment lead time. Consider intermittent demand and safety stock.
- **Workforce:** Model workload and required competencies, not patient count alone. Respect local rules and minimum staffing constraints.
- **Readmission/no-show:** Use only approved patient-level data. Evaluate PR-AUC, sensitivity, calibration and subgroup outcomes. Keep model outputs advisory.
- **Anomaly detection:** Validate whether alerts are actionable and quantify false-positive burden; unusual does not automatically mean erroneous or unsafe.
- **SHAP:** Explain contributions to a model output, not clinical causality. Explain the actual prediction and model version.

## 7. Hospital bed and capacity logic

Before implementing bed logic, define the bed lifecycle and allowed transitions. Model bed status as a history/event stream or equivalent auditable structure when practical.

At minimum distinguish:

- Physical beds.
- Occupied beds.
- Reserved beds.
- Cleaning/infection-control hold.
- Maintenance/blocked beds.
- Ready beds.
- Specialty/acuity-compatible beds.
- Beds that can be staffed with the current qualified workforce.

Prevent double counting between mutually exclusive statuses. Derive operational availability from approved hospital policy, compatibility and workforce constraints. Make thresholds and rules configurable by hospital/department rather than embedding assumptions in code.

## 8. PuLP optimization workflow

Do not begin with code. First write a small mathematical specification:

1. Sets and indices (departments, wards, time slots, resources).
2. Input parameters with units and timestamps.
3. Decision variables and domains.
4. Objective function, including units and priority/weight rationale.
5. Hard constraints.
6. Soft constraints/penalties.
7. Solver and time-limit behaviour.
8. Infeasibility and no-solution behaviour.
9. Review, approval and audit requirements.

Test both feasible and deliberately infeasible cases. Check all hard constraints independently after solving. Do not rely solely on the solver's status string. Never allow the objective function to trade away a hard safety rule. Record solver status, objective value, input snapshot, constraint configuration and solution version.

## 9. What-if simulation workflow

- Define scenario inputs separately from live observations.
- State baseline, changes, assumptions, time horizon and random seed if stochastic.
- Keep scenario results separate from actual operational facts.
- Test edge cases such as sudden demand surges, reduced staffing, equipment outages, delayed supply and unavailable beds.
- Present comparative outcomes and uncertainty, not a single falsely precise answer.
- Do not label an illustrative calculation as a validated hospital simulation.

## 10. API and integration workflow

- Define typed request and response schemas.
- Validate payloads and reject invalid state transitions.
- Apply authentication and role-based authorization at server boundaries.
- Use pagination/filtering for lists that can grow.
- Make import jobs idempotent where possible; prevent duplicate admissions, transfers or stock movements.
- Return structured, non-sensitive error details.
- Record source system, external ID, ingestion time and sync status.
- Keep API and integration failures visible; do not silently display stale data as current.
- Consider FHIR-compatible mappings if a source system supports them, but do not claim conformance without testing against the relevant specification.

## 11. UI implementation workflow

- Review the current component library and design conventions before adding new ones.
- Organize screens by real staff tasks and role permissions.
- Show key operational facts, forecasts, alerts and recommendations as distinct information types.
- Include loading, empty, error, stale-data and permission-denied states.
- Display timestamps, forecast horizons, filters and definitions of key metrics.
- Keep tables useful for operational lists; use charts only when they add insight.
- Provide drill-down from aggregate metrics to authorized details.
- Ensure keyboard access, accessible contrast, responsive layout and readable density.
- Never expose patient-level information to a role that does not require it.

## 12. Security and privacy checks

Before completing any data/API/UI task, ask:

- Is the data source authorized for this purpose?
- Is every field necessary?
- Could a patient be identified in logs, screenshots, fixtures or URLs?
- Are permissions checked on the server, not just hidden in the UI?
- Are credentials excluded from source control?
- Are access and consequential recommendations auditable?
- Are retention, backup and deletion needs documented?

Use synthetic data for demos. Do not paste patient records into prompts, public repositories or third-party services. Do not claim legal or standards compliance without a current, scoped validation.

## 13. Testing strategy

Add the right tests for the change:

- Unit tests for domain rules, transformations and feature calculations.
- Data validation tests for ranges, required columns and timestamp logic.
- API tests for schemas, authorization, error cases and idempotency.
- Database tests for constraints and migrations.
- ML tests for leakage guards, deterministic preprocessing, target/feature alignment and baseline comparisons.
- Optimization tests for feasible, infeasible, boundary and hard-constraint cases.
- Simulation tests for scenario assumptions and reproducibility.
- UI tests for loading/empty/error/stale states, permissions and responsive behaviour.
- Integration tests for ingestion-to-dashboard vertical slices.

Run the smallest relevant test set after each change, then the broader suite when practical. Report exactly which commands ran and their outcomes. Do not say “all tests pass” if some were not run.

## 14. Documentation and change management

For meaningful changes, update the relevant documents:

- `PROJECT_MEMORY.md` for durable product decisions or changed scope.
- Architecture diagram/document for boundary or dependency changes.
- Data dictionary for data field or entity changes.
- API docs for contracts and error changes.
- Model card for a new or revised model.
- Optimization specification for objective/constraint changes.
- README/runbook for setup, commands or environment changes.

Do not rewrite history. Add dated decision-log entries and mark superseded decisions.

## 15. Task completion format

Finish substantial tasks with:

### Completed
- Concise list of implemented outcomes.

### Files changed
- Paths and purpose.

### Validation
- Commands/tests actually run and result.
- For ML: data split, baseline, metrics and limitations.
- For optimization: solver status and independent constraint checks.

### Assumptions and remaining risks
- Clearly state what is still synthetic, unverified, missing or provisional.

### Next step
- One specific logical next implementation step.

Never report a forecast as clinically validated, an optimization as safe for live use, or an integration as working unless evidence supports the claim.
