"""
Baseline time-series forecaster: Seasonal Naive.
Predicts arrival_count at timestamp t using historical observations from t - 168h (1 week prior).
"""

import numpy as np
import pandas as pd


class SeasonalNaiveForecaster:
    """
    Standard healthcare benchmark: predicts same hour from exactly 1 week ago (t - 168 hours).
    Falls back to t - 24 hours if weekly lag is missing.
    """
    def __init__(self, seasonal_lag: int = 168, fallback_lag: int = 24):
        self.seasonal_lag = seasonal_lag
        self.fallback_lag = fallback_lag

    def predict(self, df: pd.DataFrame, target_col: str = "arrival_count") -> np.ndarray:
        preds = []
        for i in range(len(df)):
            if i >= self.seasonal_lag:
                val = df[target_col].iloc[i - self.seasonal_lag]
            elif i >= self.fallback_lag:
                val = df[target_col].iloc[i - self.fallback_lag]
            elif i >= 1:
                val = df[target_col].iloc[i - 1]
            else:
                val = df[target_col].mean()
            preds.append(val)
        return np.array(preds)

