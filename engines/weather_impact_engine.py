# engines/weather_impact_engine.py

import requests
from config import WEATHER_API_KEY, WEATHER_API_URL


def get_weather_risk(destination_city: str):
    """
    Fetches live weather and converts it into delivery risk advisory.
    """

    try:
        response = requests.get(
            WEATHER_API_URL,
            params={
                "key": WEATHER_API_KEY,
                "q": destination_city
            },
            timeout=5
        )

        data = response.json()

        condition_text = data["current"]["condition"]["text"].lower()

    except Exception:
        return {
            "weather_condition": "UNKNOWN",
            "severity": "LOW",
            "risk_adjustment": 0,
            "reason": "Weather data unavailable. No adjustment applied."
        }

    # Rule-based weather risk mapping
    if "rain" in condition_text:
        return {
            "weather_condition": "RAIN",
            "severity": "MODERATE",
            "risk_adjustment": 15,
            "reason": "Rain may slow traffic and last-mile delivery."
        }

    if "storm" in condition_text or "thunder" in condition_text:
        return {
            "weather_condition": "STORM",
            "severity": "HIGH",
            "risk_adjustment": 30,
            "reason": "Storm conditions significantly increase delay risk."
        }

    if "heat" in condition_text or "hot" in condition_text:
        return {
            "weather_condition": "HEATWAVE",
            "severity": "MODERATE",
            "risk_adjustment": 10,
            "reason": "High temperature may stress vehicles and staff."
        }

    return {
        "weather_condition": "CLEAR",
        "severity": "LOW",
        "risk_adjustment": 0,
        "reason": "Weather conditions are normal."
    }
