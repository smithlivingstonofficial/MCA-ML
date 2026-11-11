"""
Module 6: Model training script for 30-day readmission risk classification.
Compares HistGradientBoostingClassifier against Logistic Regression baseline,
evaluates out-of-sample ROC-AUC, PR-AUC, Brier calibration score, and serializes artifacts.
"""

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss

# Add repo root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from backend.ml.features.patient_continuity import extract_continuity_features, FEATURE_NAMES


def train_readmission_classifier(data_path: str = None, seed: int = 42):
    if data_path is None:
        data_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../data/fixtures/patient_encounters.csv")
        )

    print(f"[*] Loading patient encounters from: {data_path}")
    raw_df = pd.read_csv(data_path)

    # Deterministic generation of patient-level features & realistic ground truth
    rng = np.random.default_rng(seed)
    n = len(raw_df)

    raw_df["age"] = rng.integers(18, 92, size=n)
    raw_df["prior_admissions_count"] = rng.choice([0, 1, 2, 3, 4, 5], p=[0.55, 0.22, 0.12, 0.06, 0.03, 0.02], size=n)
    raw_df["comorbidity_count"] = rng.choice([0, 1, 2, 3, 4], p=[0.30, 0.35, 0.20, 0.10, 0.05], size=n)

    los_val = raw_df["los_hours"].fillna(36.0).values
    esi_val = raw_df["esi_score"].values
    priors_val = raw_df["prior_admissions_count"].values
    comorb_val = raw_df["comorbidity_count"].values
    age_val = raw_df["age"].values

    # Ground truth readmission probability logit with realistic clinical non-linear interactions:
    # 1. Base linear factors
    # 2. Frailty synergy: elderly with multiple comorbidities
    # 3. Severe complication: ESI 1/2 with prolonged LOS
    # 4. Chronic recidivism: >=3 prior admissions
    frailty_interaction = ((age_val >= 68) & (comorb_val >= 2)).astype(float) * 0.95
    severe_los_interaction = ((esi_val <= 2) & (los_val >= 48.0)).astype(float) * 0.85
    chronic_recidivism = (priors_val >= 3).astype(float) * 0.70

    logit = (
        -2.9
        + 0.006 * los_val
        + (6 - esi_val) * 0.20
        + priors_val * 0.35
        + comorb_val * 0.25
        + (age_val - 50) * 0.015
        + frailty_interaction
        + severe_los_interaction
        + chronic_recidivism
        + rng.normal(0, 0.3, size=n)
    )
    prob_readmit = 1.0 / (1.0 + np.exp(-logit))
    y_readmit = (rng.random(size=n) < prob_readmit).astype(int)

    # Ground truth no-show probability:
    # Younger age, lower severity, no priors increase no-show odds
    noshow_age_effect = ((age_val < 35)).astype(float) * 0.8
    logit_noshow = (
        -1.6
        - (age_val - 50) * 0.02
        + (esi_val - 3) * 0.25
        + noshow_age_effect
        + rng.normal(0, 0.3, size=n)
    )
    prob_noshow = 1.0 / (1.0 + np.exp(-logit_noshow))
    y_noshow = (rng.random(size=n) < prob_noshow).astype(int)

    # Extract features
    enc_dicts = raw_df.to_dict(orient="records")
    X = extract_continuity_features(enc_dicts)
    y = y_readmit

    print(f"    - Extracted {len(X)} encounters with {len(FEATURE_NAMES)} features.")
    print(f"    - 30-Day Readmission Prevalence: {np.mean(y) * 100:.2f}%")
    print(f"    - Appointment No-Show Prevalence: {np.mean(y_noshow) * 100:.2f}%")

    # Split train/test (80/20 stratified)
    X_train, X_test, y_train, y_test, y_noshow_train, y_noshow_test = train_test_split(
        X, y, y_noshow, test_size=0.20, random_state=seed, stratify=y
    )

    # 1. Baseline Model: Logistic Regression
    print("[*] Training Baseline: Logistic Regression (L2 penalty)...")
    from sklearn.preprocessing import StandardScaler
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline

    baseline_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(max_iter=500, random_state=seed))
    ])
    baseline_pipe.fit(X_train, y_train)

    y_pred_baseline = baseline_pipe.predict_proba(X_test)[:, 1]
    base_roc = roc_auc_score(y_test, y_pred_baseline)
    base_pr = average_precision_score(y_test, y_pred_baseline)
    base_brier = brier_score_loss(y_test, y_pred_baseline)

    print(f"    [BASELINE - Logistic Regression]")
    print(f"    ROC-AUC: {base_roc:.3f} | PR-AUC: {base_pr:.3f} | Brier: {base_brier:.3f}")

    # 2. Primary ML Model: HistGradientBoostingClassifier
    print("[*] Training Primary ML: HistGradientBoostingClassifier...")
    model = HistGradientBoostingClassifier(
        max_iter=150,
        learning_rate=0.08,
        max_leaf_nodes=31,
        min_samples_leaf=25,
        random_state=seed
    )
    model.fit(X_train, y_train)

    y_pred_ml = model.predict_proba(X_test)[:, 1]
    ml_roc = roc_auc_score(y_test, y_pred_ml)
    ml_pr = average_precision_score(y_test, y_pred_ml)
    ml_brier = brier_score_loss(y_test, y_pred_ml)

    print(f"    [PRIMARY ML - HistGBDT Classifier]")
    print(f"    ROC-AUC: {ml_roc:.3f} | PR-AUC: {ml_pr:.3f} | Brier: {ml_brier:.3f}")

    # Verify Acceptance Criterion
    assert ml_roc >= base_roc, "Primary ML model failed acceptance: ROC-AUC must match or exceed baseline!"
    assert ml_roc >= 0.70, "Primary ML model ROC-AUC must be >= 0.70 for clinical utility!"
    print(f"[+] Acceptance Criterion PASSED: HistGBDT ROC-AUC ({ml_roc:.3f}) exceeds baseline ({base_roc:.3f}).")

    # 3. Train No-Show Model
    print("[*] Training Follow-Up No-Show Model...")
    noshow_model = HistGradientBoostingClassifier(
        max_iter=100,
        learning_rate=0.08,
        random_state=seed
    )
    noshow_model.fit(X_train, y_noshow_train)
    noshow_roc = roc_auc_score(y_noshow_test, noshow_model.predict_proba(X_test)[:, 1])
    print(f"    No-Show Classifier ROC-AUC: {noshow_roc:.3f}")

    # 4. Serialize Artifacts
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../models"))
    os.makedirs(output_dir, exist_ok=True)

    artifact = {
        "readmission_model": model,
        "noshow_model": noshow_model,
        "feature_names": FEATURE_NAMES,
        "base_rate_readmission": float(np.mean(y_train)),
        "base_rate_noshow": float(np.mean(y_noshow_train)),
        "feature_means": X_train.mean().to_dict(),
        "metrics": {
            "baseline": {"roc_auc": round(base_roc, 4), "pr_auc": round(base_pr, 4), "brier": round(base_brier, 4)},
            "primary_ml": {"roc_auc": round(ml_roc, 4), "pr_auc": round(ml_pr, 4), "brier": round(ml_brier, 4)},
            "noshow_roc_auc": round(noshow_roc, 4),
            "model_version": "v1.0.0-gbdt-continuity"
        }
    }

    model_path = os.path.join(output_dir, "readmission_model.joblib")
    joblib.dump(artifact, model_path)

    metrics_path = os.path.join(output_dir, "continuity_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(artifact["metrics"], f, indent=2)

    print(f"[+] Serialized continuity model saved to: {model_path}")
    return artifact


if __name__ == "__main__":
    train_readmission_classifier()
