import pandas as pd

def load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"{path} is empty")
    return df

def load_all_data():
    shipments = load_csv("data/shipments.csv")
    addresses = load_csv("data/addresses.csv")
    delivery_history = load_csv("data/delivery_history.csv")
    weather = load_csv("data/weather_and_environment.csv")
    resources = load_csv("data/resources_capability.csv")

    return shipments, addresses, delivery_history, weather, resources
