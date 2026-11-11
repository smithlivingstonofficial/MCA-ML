"""
Training and evaluation script for Module 1 Emergency Department Arrival Forecaster.
Trains HistGradientBoostingRegressor (Poisson loss) against Seasonal Naive baseline.
Evaluates out-of-sample holdout metrics (MAE, RMSE, WAPE) and serializes artifacts.
"""

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from backend.ml.features.temporal import build_arrival_features, FEATURE_COLUMNS
from backend.ml.baselines.seasonal_naive import SeasonalNaiveForecaster


def compute_wape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sum(np.abs(y_true - y_pred)) / np.sum(y_true))


def train_and_evaluate(data_path: str = None):
    if data_path is None:
        data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/fixtures/ed_hourly_arrivals.csv"))
    
    print(f"[*] Loading historical arrivals from: {data_path}")
    raw_df = pd.read_csv(data_path)
    raw_df["timestamp"] = pd.to_datetime(raw_df["timestamp"])
    raw_df = raw_df.sort_values("timestamp").reset_index(drop=True)

    # 1. Feature Engineering
    print("[*] Engineering temporal and lag features...")
    df_features = build_arrival_features(raw_df, target_col="arrival_count")
    
    # Drop warm-up period (first 168 hours for 1-week lag)
    valid_df = df_features.dropna(subset=FEATURE_COLUMNS).reset_index(drop=True)
    
    # 2. Train / Holdout Test Split (Last 30 days = 720 hours for holdout)
    holdout_hours = 30 * 24
    train_df = valid_df.iloc[:-holdout_hours].copy()
    test_df = valid_df.iloc[-holdout_hours:].copy()

    X_train = train_df[FEATURE_COLUMNS]
    y_train = train_df["arrival_count"].values
    
    X_test = test_df[FEATURE_COLUMNS]
    y_test = test_df["arrival_count"].values

    print(f"    - Training Set: {len(X_train)} hours")
    print(f"    - Holdout Test: {len(X_test)} hours")

    # 3. Seasonal Naive Baseline Evaluation
    print("[*] Evaluating Seasonal Naive Baseline...")
    naive_forecaster = SeasonalNaiveForecaster()
    # Align naive predictions from test_df's lag_168h
    y_pred_naive = test_df["lag_168h"].values

    naive_mae = float(mean_absolute_error(y_test, y_pred_naive))
    naive_rmse = float(np.sqrt(mean_squared_error(y_test, y_pred_naive)))
    naive_wape = compute_wape(y_test, y_pred_naive)

    print(f"    [BASELINE - Seasonal Naive]")
    print(f"    MAE:  {naive_mae:.3f}")
    print(f"    RMSE: {naive_rmse:.3f}")
    print(f"    WAPE: {naive_wape * 100:.2f}%")

    # 4. Primary ML Model: HistGradientBoostingRegressor (Poisson Loss)
    print("[*] Training HistGradientBoostingRegressor (Poisson objective)...")
    model = HistGradientBoostingRegressor(
        loss="poisson",
        max_iter=250,
        learning_rate=0.06,
        max_leaf_nodes=31,
        min_samples_leaf=20,
        random_state=42
    )
    model.fit(X_train, y_train)

    y_pred_ml = model.predict(X_test)
    ml_mae = float(mean_absolute_error(y_test, y_pred_ml))
    ml_rmse = float(np.sqrt(mean_squared_error(y_test, y_pred_ml)))
    ml_wape = compute_wape(y_test, y_pred_ml)

    print(f"    [PRIMARY ML - HistGBDT Poisson]")
    print(f"    MAE:  {ml_mae:.3f}")
    print(f"    RMSE: {ml_rmse:.3f}")
    print(f"    WAPE: {ml_wape * 100:.2f}%")

    # 5. Verification of Acceptance Criteria
    wape_reduction = (naive_wape - ml_wape) / naive_wape * 100
    print(f"[*] Out-of-sample WAPE Improvement: +{wape_reduction:.2f}%")
    assert ml_wape < naive_wape, "Model failed acceptance criterion: ML WAPE must be strictly lower than baseline!"
    print("[+] Acceptance Criterion PASSED: ML Forecaster outperforms Seasonal Naive baseline.")

    # Calculate residual error std for 80% prediction intervals (z = 1.28)
    residuals = y_train - model.predict(X_train)
    residual_std = float(np.std(residuals))

    # 6. Serialize Model Artifacts
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../models"))
    os.makedirs(output_dir, exist_ok=True)
    
    artifact = {
        "model": model,
        "feature_columns": FEATURE_COLUMNS,
        "residual_std": residual_std,
        "metrics": {
            "baseline": {"mae": naive_mae, "rmse": naive_rmse, "wape": naive_wape},
            "primary_ml": {"mae": ml_mae, "rmse": ml_rmse, "wape": ml_wape},
            "wape_improvement_pct": wape_reduction
        },
        "model_version": "v1.0.0-gbdt-poisson"
    }

    model_path = os.path.join(output_dir, "ed_arrival_model.joblib")
    joblib.dump(artifact, model_path)
    
    metrics_path = os.path.join(output_dir, "model_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(artifact["metrics"], f, indent=2)

    print(f"[+] Serialized model artifact saved to: {model_path}")
    return artifact


if __name__ == "__main__":
    train_and_evaluate()

