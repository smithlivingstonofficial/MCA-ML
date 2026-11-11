"""
Module 6: Explainable AI pipeline using TreeSHAP for patient continuity risk scoring.
Generates localized feature attributions (waterfall breakdown) explaining 30-day readmission risk
and follow-up no-show likelihood with clinical interpretability.
"""

import os
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
import joblib
import shap

from backend.ml.features.patient_continuity import extract_continuity_features, FEATURE_NAMES

# Friendly clinical labels for features
FEATURE_DISPLAY_NAMES = {
    "actual_los_hours": "Length of Stay (Hours)",
    "esi_score": "Emergency Triage Acuity (ESI)",
    "prior_admissions_count": "Prior Hospitalizations (12 Mo)",
    "comorbidity_count": "Documented Comorbidities",
    "age": "Patient Age",
    "is_emergency_admission": "Emergency Dept Admission",
    "discharge_to_home": "Discharged to Home Residence",
    "high_risk_chief_complaint": "Cardiopulmonary Chief Complaint"
}


class ContinuityExplainer:
    """
    TreeSHAP explanation engine for post-discharge patient continuity models.
    """

    def __init__(self, model_path: Optional[str] = None):
        if model_path is None:
            model_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../models/readmission_model.joblib")
            )

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Trained continuity model not found at {model_path}. Run training pipeline first."
            )

        artifact = joblib.load(model_path)
        self.readmission_model = artifact["readmission_model"]
        self.noshow_model = artifact.get("noshow_model")
        self.feature_names = artifact.get("feature_names", FEATURE_NAMES)
        self.base_rate_readmission = artifact.get("base_rate_readmission", 0.25)
        self.base_rate_noshow = artifact.get("base_rate_noshow", 0.20)

        # Initialize TreeExplainer
        self.explainer = shap.TreeExplainer(self.readmission_model)

        raw_ev = self.explainer.expected_value
        if isinstance(raw_ev, (list, np.ndarray)):
            self.base_log_odds = float(raw_ev[0])
        else:
            self.base_log_odds = float(raw_ev)

    def explain_patient(self, feature_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculates local SHAP attributions for a single patient feature row.
        """
        if len(feature_df) != 1:
            raise ValueError("explain_patient expects a single row DataFrame.")

        # SHAP attribution calculation
        shap_vals = self.explainer.shap_values(feature_df)
        if isinstance(shap_vals, list):
            vals = np.array(shap_vals[0]).flatten()
        elif hasattr(shap_vals, "values"):
            vals = np.array(shap_vals.values[0]).flatten()
        else:
            vals = np.array(shap_vals[0]).flatten()

        row_dict = feature_df.iloc[0].to_dict()

        # Model predicted probabilities
        prob_readmit = float(self.readmission_model.predict_proba(feature_df)[0, 1])
        prob_noshow = float(self.noshow_model.predict_proba(feature_df)[0, 1]) if self.noshow_model else None

        # Build feature attribution list
        attributions: List[Dict[str, Any]] = []
        for name in self.feature_names:
            val = float(row_dict.get(name, 0.0))
            idx = self.feature_names.index(name)
            phi = float(vals[idx]) if idx < len(vals) else 0.0

            if phi > 0.01:
                effect = "risk_increasing"
            elif phi < -0.01:
                effect = "protective"
            else:
                effect = "neutral"

            # Clinical interpretation generator
            interp = self._generate_interpretation(name, val, phi)

            attributions.append({
                "feature_name": name,
                "display_name": FEATURE_DISPLAY_NAMES.get(name, name),
                "feature_value": val,
                "shap_value": round(phi, 4),
                "effect": effect,
                "clinical_interpretation": interp
            })

        # Sort by absolute SHAP impact descending
        attributions.sort(key=lambda x: abs(x["shap_value"]), reverse=True)

        # Risk tier calculation
        if prob_readmit >= 0.35:
            risk_tier = "HIGH"
            recommended_outreach = "Priority Clinical Outreach (Pharmacist MTM + 48h Home Health Nurse Check)"
        elif prob_readmit >= 0.20:
            risk_tier = "MODERATE"
            recommended_outreach = "Standard Care Transition (Follow-up Call within 72h + Transportation Aid)"
        else:
            risk_tier = "LOW"
            recommended_outreach = "Routine Post-Discharge Instructions & Patient Portal Summary"

        return {
            "predicted_readmission_risk": round(prob_readmit, 4),
            "predicted_noshow_risk": round(prob_noshow, 4) if prob_noshow is not None else None,
            "base_log_odds": round(self.base_log_odds, 4),
            "risk_tier": risk_tier,
            "recommended_outreach": recommended_outreach,
            "feature_attributions": attributions
        }

    def explain_encounter(self, encounter_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convenience method taking an encounter dictionary directly.
        """
        df = extract_continuity_features([encounter_dict])
        return self.explain_patient(df)

    def _generate_interpretation(self, name: str, val: float, phi: float) -> str:
        """
        Generates readable clinical commentary for operational decision support.
        """
        if name == "prior_admissions_count":
            if val >= 2:
                return f"{int(val)} prior admissions indicate chronic disease recidivism."
            return "No frequent prior hospitalizations recorded."
        elif name == "comorbidity_count":
            if val >= 2:
                return f"{int(val)} active chronic comorbidities increase post-acute vulnerability."
            return "Minimal documented comorbidity burden."
        elif name == "actual_los_hours":
            if val > 72:
                return f"Extended inpatient stay ({val:.0f}h) reflects complicated clinical course."
            return f"Standard hospitalization duration ({val:.0f}h)."
        elif name == "esi_score":
            if val <= 2:
                return f"High triage acuity (ESI {int(val)}) at original admission."
            return f"Moderate to low triage acuity (ESI {int(val)})."
        elif name == "age":
            if val >= 65:
                return f"Geriatric age ({int(val)}) contributes to elevated readmission risk."
            return f"Patient age {int(val)}."
        elif name == "high_risk_chief_complaint":
            if val == 1:
                return "Cardiopulmonary presentation warrants stringent outpatient continuity."
            return "Non-cardiopulmonary presentation."
        elif name == "is_emergency_admission":
            if val == 1:
                return "Unplanned emergency admission indicates acute decompensation."
            return "Elective or scheduled admission."
        elif name == "discharge_to_home":
            if val == 1:
                return "Discharged to independent home care without skilled nursing facility."
            return "Facility-supported post-acute disposition."
        return f"Contribution score: {phi:+.3f}"


# Global singleton instance for API endpoints
_explainer_instance: Optional[ContinuityExplainer] = None


def get_continuity_explainer() -> ContinuityExplainer:
    global _explainer_instance
    if _explainer_instance is None:
        _explainer_instance = ContinuityExplainer()
    return _explainer_instance
