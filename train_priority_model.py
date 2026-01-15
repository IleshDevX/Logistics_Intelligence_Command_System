# train_priority_model.py

import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import joblib
import os

data = {
    "weight_kg": [1, 5, 10, 30, 60, 5, 15, 40],
    "distance_km": [5, 50, 300, 100, 800, 20, 200, 600],
    "delivery_urgency": [1, 1, 0, 1, 0, 0, 1, 0],
    "priority": ["HIGH", "HIGH", "MEDIUM", "HIGH", "LOW", "MEDIUM", "HIGH", "LOW"]
}

df = pd.DataFrame(data)

X = df[["weight_kg", "distance_km", "delivery_urgency"]]
y = df["priority"]

model = DecisionTreeClassifier(max_depth=3)
model.fit(X, y)

MODEL_DIR = "services"
MODEL_PATH = os.path.join(MODEL_DIR, "priority_model.pkl")

os.makedirs(MODEL_DIR, exist_ok=True)

joblib.dump(model, MODEL_PATH)

print(f"✅ Priority model trained and saved at: {MODEL_PATH}")
