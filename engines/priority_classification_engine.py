# engines/priority_classification_engine.py

import joblib
import os

MODEL_PATH = "services/priority_model.pkl"


def classify_priority(shipment: dict):
    """
    Classifies shipment priority as HIGH / MEDIUM / LOW
    """

    if not os.path.exists(MODEL_PATH):
        return {
            "priority": "MEDIUM",
            "reason": "Priority model unavailable. Defaulting to MEDIUM."
        }

    model = joblib.load(MODEL_PATH)

    # Encode urgency
    urgency_encoded = 1 if shipment["delivery_urgency"] == "EXPRESS" else 0

    features = [[
        shipment["weight_kg"],
        shipment["distance_km"],
        urgency_encoded
    ]]

    priority = model.predict(features)[0]

    # Explainable thresholds
    if priority == "HIGH":
        reason = "Express delivery or high operational importance."
    elif priority == "LOW":
        reason = "Non-urgent and operationally flexible shipment."
    else:
        reason = "Standard priority shipment."

    return {
        "priority": priority,
        "reason": reason
    }
