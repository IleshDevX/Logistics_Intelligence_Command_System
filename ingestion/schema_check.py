EXPECTED_COLUMNS = {
    "shipments": {
        "shipment_id","product_type","weight_kg","volumetric_weight",
        "payment_type","priority_flag","destination_city","current_risk_score"
    },
    "addresses": {
        "shipment_id","raw_address_text","area_type",
        "road_accessibility","address_confidence_score","vehicle_access_score"
    },
    "delivery_history": {
        "shipment_id","delivery_outcome","human_override_flag",
        "failure_reason","delivery_delay_minutes"
    },
    "weather": {
        "city","weather_severity","weather_impact_factor"
    },
    "resources": {
        "resource_type","vehicle_type","max_load_kg",
        "emission_factor_gkm","area_familiarity_score"
    }
}

def validate_schema(df, expected_cols, name):
    missing = expected_cols - set(df.columns)
    if missing:
        raise ValueError(f"{name} missing columns: {missing}")
