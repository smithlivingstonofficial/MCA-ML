# Hospital Operations Intelligence Platform — Workspace Instructions

These instructions apply to the entire repository. Treat this file as the persistent project rulebook for Antigravity.

## 1. Mandatory project context

Before planning or changing project code, use the project memory below as the source of truth for the product vision, module boundaries, architecture principles, safety requirements, development phases and current decisions.

@[Hospital Project Memory](PROJECT_MEMORY.md)

If the memory and the current source code disagree, do not silently assume either is correct. Inspect the implementation, identify the conflict, and report it. Prefer an explicitly approved newer decision over an older memory entry. Update `PROJECT_MEMORY.md` when a lasting project decision changes.

## 2. How to work in this repository

- Inspect the existing repository before proposing a stack, changing files, installing dependencies or generating code.
- Preserve working code and existing conventions. Do not replace a project structure simply because you prefer another framework.
- For a new subsystem or significant architectural change, first provide a concise implementation plan with scope, affected files, data contracts, security considerations and tests.
- For a small, clearly scoped change, proceed directly while following the same engineering and safety rules.
- Implement in small, verifiable increments. Do not attempt to build all seven modules in one pass.
- Do not invent hospital workflows, datasets, API integrations, clinical policies, performance results or regulatory certifications.
- When a detail is unknown, state a reasonable provisional assumption, isolate it in configuration or documentation, and continue where safe. Ask only when the missing information materially changes safety, architecture, data access or the requested outcome.
- Do not claim a feature, test, migration, integration or model works unless it has actually been implemented and verified.

## 3. Non-negotiable healthcare safeguards

- This is an operational and clinical-support decision-support platform, not an autonomous clinical decision-maker and not a replacement for an existing Hospital Information System or Electronic Health Record.
- Never automate diagnosis, triage priority, treatment, medication selection, patient discharge, blood compatibility decisions or other clinical decisions.
- Predictions and optimization outputs are advisory. Clearly show their source, timestamp, limitations and uncertainty where applicable. Require authorized human review for consequential actions.
- Never use identifiable real patient data in examples, fixtures, screenshots, logs, committed files or public repositories.
- Use synthetic or properly authorized, de-identified data only. Clearly label synthetic/demo data and never present synthetic model metrics as real-world evidence.
- Apply least-privilege access, data minimization, secure secret handling, auditability and appropriate retention controls.
- Do not claim HIPAA, DPDP, ABDM, HL7 FHIR or other regulatory/standards compliance or certification merely because a feature or mapping exists. Describe only what has been implemented and independently validated.

## 4. Engineering quality rules

- Prefer modular, typed, testable code and explicit boundaries between UI, API, domain logic, data access, ML pipelines and optimization.
- Keep business rules out of UI components and avoid embedding domain logic inside route handlers.
- Validate all external inputs and imported data at system boundaries.
- Use database migrations for schema changes; make migrations reviewable and reversible where practical.
- Keep secrets in environment variables or a secret manager. Commit only safe `.env.example` templates, never real credentials.
- Add or update tests and relevant documentation with each meaningful feature.
- Use deterministic random seeds for reproducible synthetic datasets and ML experiments.
- Record model version, training-data window, feature definition, evaluation results and prediction timestamp.
- Use temporal validation for forecasting and prevent target leakage and patient/encounter leakage.
- Enforce hard safety and feasibility constraints in optimization. Never relax a hard safety constraint to obtain a solver result.
- If data is stale, incomplete, invalid or outside the model's supported range, flag the output and avoid presenting it as reliable.

## 5. User experience and product quality

- Build a polished, professional, responsive hospital operations interface for desktop, tablet and mobile.
- Prefer calm, restrained colors, strong information hierarchy, readable typography, accessible contrast and clear status communication.
- Avoid childish styling, excessive gradients, unnecessary animation, overloaded dashboards and repetitive card layouts.
- Distinguish actual operational facts, forecasts, alerts, simulations and proposed actions visually and textually.
- Show data freshness and time horizon on operational and predictive views.
- Design for busy hospital staff: important risks and next actions should be easy to identify without hiding context or uncertainty.

## 6. Completion report

At the end of each substantial task, report:

1. What changed.
2. Files created or modified.
3. Tests, checks or experiments actually run and their results.
4. Remaining limitations, assumptions or risks.
5. The most useful next implementation step.

Keep this file focused on durable project-wide rules. Put detailed product requirements and evolving decisions in `PROJECT_MEMORY.md`, and task procedures in the relevant skill.
