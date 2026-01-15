# engines/manager_decision_engine.py

import pandas as pd
from datetime import datetime
from config import DATA_PATH


DECISION_FILE = f"{DATA_PATH}/manager_decisions.csv"


def record_manager_decision(
    parcel_id: str,
    decision: str,
    risk_band: str,
    override_reason: str = ""
):

    """
    Records manager decision to CSV.
    """

    data = {
        "parcel_id": parcel_id,
        "timestamp": datetime.now().isoformat(),
        "decision": decision,
        "risk_band": risk_band,
        "override_reason": override_reason
    }


    df = pd.DataFrame([data])

    df.to_csv(
        DECISION_FILE,
        mode="a",
        header=False,
        index=False
    )
