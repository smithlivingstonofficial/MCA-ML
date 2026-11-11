"""
Feature engineering pipeline for Emergency Department arrival forecasting.
Extracts cyclical calendar representations, temporal lags, and rolling statistical features.
"""

import numpy as np
import pandas as pd


def build_arrival_features(df: pd.DataFrame, target_col: str = "arrival_count") -> pd.DataFrame:
    """
    Constructs leak-free feature matrix from time-indexed arrival dataframe.
    Expects df with 'timestamp' and target_col columns.
    """
    data = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(data["timestamp"]):
        data["timestamp"] = pd.to_datetime(data["timestamp"])
    
    data = data.sort_values("timestamp").reset_index(drop=True)

    # 1. Cyclical Calendar Features
    hour = data["timestamp"].dt.hour
    dow = data["timestamp"].dt.dayofweek  # Monday=0, Sunday=6
    
    data["sin_hour"] = np.sin(2 * np.pi * hour / 24.0)
    data["cos_hour"] = np.cos(2 * np.pi * hour / 24.0)
    
    data["sin_dow"] = np.sin(2 * np.pi * dow / 7.0)
    data["cos_dow"] = np.cos(2 * np.pi * dow / 7.0)
    
    data["is_weekend"] = (dow >= 5).astype(int)

    # 2. Lag Features (Available at forecast creation timestamp)
    data["lag_1h"] = data[target_col].shift(1)
    data["lag_2h"] = data[target_col].shift(2)
    data["lag_3h"] = data[target_col].shift(3)
    data["lag_24h"] = data[target_col].shift(24)    # Same hour previous day
    data["lag_168h"] = data[target_col].shift(168)  # Same hour previous week

    # 3. Rolling Summary Statistics
    data["rolling_mean_6h"] = data[target_col].shift(1).rolling(window=6, min_periods=1).mean()
    data["rolling_std_6h"] = data[target_col].shift(1).rolling(window=6, min_periods=1).std().fillna(0.0)
    data["rolling_mean_24h"] = data[target_col].shift(1).rolling(window=24, min_periods=1).mean()
    data["rolling_max_24h"] = data[target_col].shift(1).rolling(window=24, min_periods=1).max()

    return data


FEATURE_COLUMNS = [
    "sin_hour", "cos_hour", "sin_dow", "cos_dow", "is_weekend",
    "lag_1h", "lag_2h", "lag_3h", "lag_24h", "lag_168h",
    "rolling_mean_6h", "rolling_std_6h", "rolling_mean_24h", "rolling_max_24h"
]

