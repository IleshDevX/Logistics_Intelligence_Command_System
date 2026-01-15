# engines/input_validation_engine.py

import pandas as pd
from datetime import date

REQUIRED_FIELDS = [
    "weight_kg",
    "length_cm",
    "width_cm",
    "height_cm",
    "distance_km",
    "source_city",
    "destination_city",
    "area_type",
    "address_type",
    "delivery_date",
    "delivery_urgency"
]


VALID_AREA_TYPES = ["URBAN", "RURAL", "OLD_CITY"]
VALID_ADDRESS_TYPES = ["RESIDENTIAL", "COMMERCIAL"]
VALID_URGENCY = ["NORMAL", "EXPRESS"]


def validate_and_normalize(input_data: dict):
    """
    Validates seller input and returns:
    - success flag
    - cleaned shipment object OR error messages
    """

    errors = []

    # 1. Missing field check
    for field in REQUIRED_FIELDS:
        if field not in input_data or input_data[field] in ["", None]:
            errors.append(f"{field} is required.")

    if errors:
        return False, errors

    # 2. Numeric validation
    try:
        weight = float(input_data["weight_kg"])
        distance = float(input_data["distance_km"])
        length = float(input_data["length_cm"])
        width = float(input_data["width_cm"])
        height = float(input_data["height_cm"])
    except ValueError:
        return False, ["Numeric fields must contain valid numbers."]

    if weight <= 0 or distance <= 0:
        return False, ["Weight and distance must be greater than zero."]

    # 3. Category normalization
    area_type = input_data["area_type"].upper()
    address_type = input_data["address_type"].upper()
    urgency = input_data["delivery_urgency"].upper()

    if area_type not in VALID_AREA_TYPES:
        errors.append("Invalid area type.")

    if address_type not in VALID_ADDRESS_TYPES:
        errors.append("Invalid address type.")

    if urgency not in VALID_URGENCY:
        errors.append("Invalid delivery urgency.")

    # 4. Date validation
    if input_data["delivery_date"] < date.today():
        errors.append("Delivery date cannot be in the past.")

    if errors:
        return False, errors

    # 5. Normalized output
    cleaned_data = {
        "weight_kg": round(weight, 2),
        "dimensions_cm": {
            "length": length,
            "width": width,
            "height": height
        },
        "volume_cm3": round(length * width * height, 2),
        "distance_km": round(distance, 2),
        "source_city": input_data["source_city"].strip(),
        "destination_city": input_data["destination_city"].strip(),
        "area_type": area_type,
        "address_type": address_type,
        "delivery_date": input_data["delivery_date"],
        "delivery_urgency": urgency
    }

    return True, cleaned_data
