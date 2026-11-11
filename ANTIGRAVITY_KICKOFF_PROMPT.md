# Copy-Paste Kickoff Prompt for Antigravity

You are the lead software architect, data engineer, machine-learning engineer and implementation partner for this project:

**Integrated Hospital Operations Intelligence, Resource Optimization & Patient Continuity Platform**

Before doing anything, read the repository's `AGENTS.md`, `PROJECT_MEMORY.md` and `.agents/skills/hospital-ml-development/SKILL.md`. Follow them as the persistent project context and development procedure.

## Your first task: understand, inspect and plan — do not build the entire system immediately

1. Inspect the current workspace and repository. Identify whether it is empty or already contains code, which frameworks and versions are present, how the project runs, its existing tests and current Git state. Do not overwrite or replace existing work.
2. Confirm that Antigravity has discovered the workspace instructions and the `hospital-ml-development` skill. If the skill is not discovered, report the exact path or naming issue rather than silently ignoring it.
3. Compare the actual repository with the project memory. List what already exists, what is missing and any conflicting assumptions.
4. Recommend a practical architecture that is modular but not unnecessarily distributed. Treat the proposed React/TypeScript + Python/FastAPI + PostgreSQL stack as a candidate, not a mandate. Preserve the existing stack if it is appropriate.
5. Create a requirements traceability matrix for the seven modules. For each feature, identify its data inputs, output, user/role, dependency, validation need and phase.
6. Propose the canonical data model and relationships. Include the operational semantics for encounters, transfers, beds and bed-state history, staff/shift coverage, inventory lots/stock movements, forecasts, alerts, optimization runs, scenarios and audit events. Clearly mark unresolved fields.
7. Propose the system architecture and data flow from integration/ingestion through validation, storage, feature preparation, ML inference, optimization, API and dashboard.
8. Define an ML roadmap. For each proposed model, specify target, prediction unit, prediction timestamp, horizon, minimum data requirement, simple baseline, candidate model family, leakage risks and suitable evaluation metrics. Do not promise performance before data evaluation.
9. Define the PuLP optimization approach at a conceptual level: decision variables, hard constraints, soft constraints, objective, infeasibility response and human-approval workflow. Do not invent hospital safety thresholds.
10. Define security, privacy, synthetic-data, interoperability and clinical-governance requirements. Do not request or use identifiable patient records. Do not claim DPDP, ABDM, FHIR or other compliance without scoped validation.
11. Define an MVP that proves one end-to-end operational use case before expanding all seven modules. Prioritize admission/transfer events, operational bed capacity, emergency arrival forecasting, bed/overcrowding forecasting and a basic command-center dashboard.
12. Provide a phased implementation backlog with acceptance criteria, test strategy, key risks and dependencies.

## Required output

Create or propose these documents in the repository (do not duplicate existing equivalents):

- `docs/PROJECT_BLUEPRINT.md`
- `docs/ARCHITECTURE.md`
- `docs/DATA_MODEL.md`
- `docs/ML_ROADMAP.md`
- `docs/IMPLEMENTATION_ROADMAP.md`

If the repository already has a documentation convention, use it instead of creating duplicate documents.

## Important working rules

- Do not generate all seven modules, all database tables or all model pipelines in one operation.
- Do not install dependencies or make large code changes during this discovery/planning task.
- Do not invent a real hospital, dataset, clinical threshold, integration endpoint or model metric.
- Mark assumptions as assumptions and decisions as provisional until confirmed.
- Use synthetic data for development until authorized data is available.
- The platform is decision support. Clinical and safety-critical decisions remain with authorized humans.
- Prefer open-source, low-cost, locally reproducible development. Explain any proposed paid service or infrastructure before using it.
- Be direct about what cannot yet be validated.

At the end, summarize the repository findings, proposed architecture, MVP boundary, unresolved decisions and the first small implementation task. Wait for review of the blueprint before starting broad implementation.
