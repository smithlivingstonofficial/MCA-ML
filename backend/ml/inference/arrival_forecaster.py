"""
Real-time inference wrapper for Emergency Department arrival forecasting.
Generates 24h, 48h, and 72h arrival forecasts with 80% prediction interval bands
and overcrowding alert detection.
"""

import os
import joblib
from datetime import datetime, timedelta
from typing import List, Dict, Any
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from backend.app.db.models import HourlyArrivalAggregate
from backend.ml.features.temporal import build_arrival_features, FEATURE_COLUMNS


class ArrivalForecaster:
    def __init__(self, model_path: str = None):
        if model_path is None:
            model_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../models/ed_arrival_model.joblib")
            )
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model artifact not found at: {model_path}. Run train_arrival_model.py first.")
            
        artifact = joblib.load(model_path)
        self.model = artifact["model"]
        self.feature_columns = artifact["feature_columns"]
        self.residual_std = artifact["residual_std"]
        self.version = artifact.get("model_version", "v1.0.0")

    def forecast_arrivals(self, db: Session, horizon_hours: int = 24, overcrowding_threshold: float = 12.0) -> List[Dict[str, Any]]:
        """
        Produces multi-hour arrival forecast using real-time database state and model features.
        """
        horizon_hours = min(72, max(1, horizon_hours))

        # Fetch recent historical aggregates for lags (need at least 168 hours)
        recent_records = (
            db.query(HourlyArrivalAggregate)
            .filter(HourlyArrivalAggregate.department_code == "ED")
            .order_by(HourlyArrivalAggregate.timestamp.desc())
            .limit(200)
            .all()
        )

        if not recent_records:
            # Fallback if no history exists yet
            base_time = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
            return [
                {
                    "timestamp": base_time + timedelta(hours=h),
                    "predicted_arrivals": 7.5,
                    "lower_bound_80": 4.5,
                    "upper_bound_80": 10.5,
                    "overcrowding_risk": False
                }
                for h in range(1, horizon_hours + 1)
            ]

        # Convert to DataFrame
        recent_records = list(reversed(recent_records))
        history_df = pd.DataFrame([
            {"timestamp": r.timestamp, "arrival_count": r.arrival_count}
            for r in recent_records
        ])

        forecast_points = []
        last_ts = history_df["timestamp"].iloc[-1]

        # Multi-step autoregressive rollout
        current_history = history_df.copy()

        for step in range(1, horizon_hours + 1):
            next_ts = last_ts + timedelta(hours=step)
            
            # Append placeholder for step
            temp_row = pd.DataFrame([{"timestamp": next_ts, "arrival_count": np.nan}])
            augmented_df = pd.concat([current_history, temp_row], ignore_index=True)
            
            # Compute features
            feature_df = build_arrival_features(augmented_df, target_col="arrival_count")
            step_features = feature_df[self.feature_columns].iloc[[-1]]

            # Handle possible NaNs in autoregressive steps with rolling mean
            if step_features.isnull().values.any():
                step_features = step_features.fillna(current_history["arrival_count"].mean())

            # Predict
            pred_val = float(self.model.predict(step_features)[0])
            pred_val = max(0.0, round(pred_val, 1))

            # 80% prediction interval (z = 1.28)
            z_score = 1.28
            margin = z_score * self.residual_std
            lower_b = max(0.0, round(pred_val - margin, 1))
            upper_b = round(pred_val + margin, 1)

            is_overcrowded = pred_val >= overcrowding_threshold

            forecast_points.append({
                "timestamp": next_ts,
                "predicted_arrivals": pred_val,
                "lower_bound_80": lower_b,
                "upper_bound_80": upper_b,
                "overcrowding_risk": is_overcrowded
            })

            # Update history with predicted value for next lags
            augmented_df.loc[augmented_df.index[-1], "arrival_count"] = pred_val
            current_history = augmented_df

        return forecast_points


_forecaster_instance = None

def get_arrival_forecaster() -> ArrivalForecaster:
    global _forecaster_instance
    if _forecaster_instance is None:
        _forecaster_instance = ArrivalForecaster()
    return _forecaster_instance

