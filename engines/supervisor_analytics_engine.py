# engines/supervisor_analytics_engine.py

import pandas as pd
from config import DATA_PATH

DECISION_FILE = f"{DATA_PATH}/manager_decisions.csv"


def load_governance_metrics():
    """
    Computes governance and oversight metrics for supervisors.
    """
    try:
        df = pd.read_csv(DECISION_FILE)
    except Exception:
        return {
            "total_decisions": 0,
            "decision_counts": {},
            "risk_distribution": {},
            "override_rate": 0.0,
            "high_risk_accepts": 0
        }

    total = len(df)

    decision_counts = df["decision"].value_counts().to_dict()
    risk_distribution = df["risk_band"].value_counts().to_dict()

    override_rate = (
        decision_counts.get("OVERRIDE", 0) / total
        if total > 0 else 0
    )

    high_risk_accepts = len(
        df[(df["risk_band"] == "HIGH") & (df["decision"] == "ACCEPT")]
    )

    return {
        "total_decisions": total,
        "decision_counts": decision_counts,
        "risk_distribution": risk_distribution,
        "override_rate": round(override_rate * 100, 2),
        "high_risk_accepts": high_risk_accepts
    }


def load_override_records():
    """
    Returns all override decisions with reasons for supervisor visibility.
    """
    try:
        df = pd.read_csv(DECISION_FILE)
    except Exception:
        return pd.DataFrame()

    overrides = df[df["decision"] == "OVERRIDE"]
    return overrides
