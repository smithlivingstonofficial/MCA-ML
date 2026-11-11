"""
Module 6: Feature engineering pipeline for 30-day readmission and appointment no-show prediction.
Extracts clinical severity, prior utilization, length of stay, and comorbidity indicators.
"""

from typing import List, Dict, Any
import numpy as np
import pandas as pd


FEATURE_NAMES = [
    "actual_los_hours",
    "esi_score",
    "prior_admissions_count",
    "comorbidity_count",
    "age",
    "is_emergency_admission",
    "discharge_to_home",
    "high_risk_chief_complaint"
]


def extract_continuity_features(encounters: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Transforms list of patient encounter dictionaries into model-ready feature DataFrame.
    """
    rows = []
    for enc in encounters:
        raw_los = enc.get("actual_los_hours")
        if raw_los is None or pd.isna(raw_los):
            raw_los = enc.get("los_hours")
        if raw_los is None or pd.isna(raw_los):
            los = 36.0
        else:
            los = float(raw_los)

        raw_esi = enc.get("esi_score")
        esi = int(raw_esi) if (raw_esi is not None and not pd.isna(raw_esi)) else 3

        raw_priors = enc.get("prior_admissions_count", 0)
        priors = int(raw_priors) if (raw_priors is not None and not pd.isna(raw_priors)) else 0

        raw_comorb = enc.get("comorbidity_count", 1)
        comorbidities = int(raw_comorb) if (raw_comorb is not None and not pd.isna(raw_comorb)) else 1

        raw_age = enc.get("age", 58)
        age = int(raw_age) if (raw_age is not None and not pd.isna(raw_age)) else 58
        
        is_emerg = 1 if enc.get("encounter_type") == "Emergency" else 0
        disp = str(enc.get("disposition") or "Discharged")
        is_home = 1 if disp in ["Home", "Discharged"] else 0
        
        complaint = str(enc.get("chief_complaint", "")).lower()
        is_high_risk = 1 if any(k in complaint for k in ["cardiac", "chest", "shortness", "arrest", "heart"]) else 0

        rows.append({
            "actual_los_hours": los,
            "esi_score": esi,
            "prior_admissions_count": priors,
            "comorbidity_count": comorbidities,
            "age": age,
            "is_emergency_admission": is_emerg,
            "discharge_to_home": is_home,
            "high_risk_chief_complaint": is_high_risk
        })

    df = pd.DataFrame(rows, columns=FEATURE_NAMES)
    return df.fillna(0.0)
