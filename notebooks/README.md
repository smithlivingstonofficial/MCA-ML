# Academic Demonstration & Viva Defense Notebooks

This directory contains executable, reproducible Jupyter Notebooks specifically designed for **academic evaluations, viva defenses, and machine learning model validation** for the **Integrated Hospital Operations Intelligence, Resource Optimization & Patient Continuity Platform** (MCA III-Semester Machine Learning Capstone).

---

## Notebook Suite Overview

| Notebook | Focus Module | Scientific / Mathematical Techniques | Key Evaluation Metrics |
| :--- | :--- | :--- | :--- |
| [`01_emergency_arrival_forecasting_benchmark.ipynb`](./01_emergency_arrival_forecasting_benchmark.ipynb) | **Module 1: Patient Flow & Emergency Management** | Cyclical time features, lag aggregations, Seasonal Naive baseline vs. Ridge vs. HistGBDT with Poisson Loss | WAPE (30.45% vs 40.86% Naive), MAE, RMSE, 7-day holdout visual trajectory |
| [`02_pulp_milp_bed_allocation_optimization.ipynb`](./02_pulp_milp_bed_allocation_optimization.ipynb) | **Module 5: Resource Optimization Engine** | Mixed-Integer Linear Programming (MILP) in PuLP, hard constraints (acuity matching, isolation, nurse ceilings), soft objectives, deliberate infeasibility test | Constraint satisfaction (100%), Big-M unallocated deficit audit, What-If absenteeism stress curve |
| [`03_readmission_risk_and_tree_shap_explainability.ipynb`](./03_readmission_risk_and_tree_shap_explainability.ipynb) | **Module 6: Patient Continuity & Risk** | Class imbalance calibration, Logistic Regression vs. HistGBDT vs. Random Forest, TreeSHAP global beeswarm & local waterfall | ROC-AUC (>0.74), PR-AUC, Brier score, local patient attribution waterfall |

---

## How to Run the Notebooks

### 1. Prerequisites
Ensure the backend Python dependencies are installed (including `jupyter`, `matplotlib`, `seaborn`, `shap`, `pulp`, `scikit-learn`):
```bash
pip install jupyter matplotlib seaborn shap pulp scikit-learn
```

### 2. Launching Jupyter Lab or Notebook
From the repository root:
```bash
jupyter notebook notebooks/
```
Alternatively, open any `.ipynb` file directly in **VS Code** with the Python / Jupyter extension enabled.

---

## Viva Defense Guidance Notes

### 1. Module 1: Time-Series Leakage Prevention
* Evaluators will check whether rolling statistics or lags contain future information.
* **Defense:** All rolling windows are strictly shifted by 1 hour ($t-1$ to $t-24$) so the model never consumes the target observation. An untouched 21-day holdout period ensures out-of-sample temporal generalization.

### 2. Module 5: PuLP Optimization Safety
* Evaluators will check if the optimizer relaxes clinical safety constraints to force a feasible solution.
* **Defense:** Hard constraints (Acuity matching, isolation, staffed capacity) are strict mathematical inequalities. Notebook 2 proves that under extreme surges, the solver flags unassigned patients as `INFEASIBLE` rather than placing critical patients into unsafe beds.

### 3. Module 6: Explainable AI (SHAP)
* Evaluators will ask whether SHAP explains disease etiology or treatment efficacy.
* **Defense:** SHAP provides mathematical feature contribution weights ($\phi_j$) to the model's prediction log-odds. It indicates model transparency, not medical or biological causation.
