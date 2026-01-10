"""
CO₂ vs Speed Trade-off Engine - Sustainability-Aware Decisions

Purpose: Quantify the trade-off between delivery speed and carbon emissions
Input: Distance, Vehicle emission factor, Traffic conditions
Output: Fast vs Green route comparison with ETA and CO₂ metrics

Philosophy:
- DON'T optimize automatically
- VISUALIZE trade-offs and let humans decide
- Show the COST of speed in carbon emissions

Used for:
- ESG reporting
- Sustainability-aware dispatch decisions
- Control tower decision support
"""

# Traffic impact on emissions
TRAFFIC_MULTIPLIERS = {
    "Smooth": 1.0,      # Free-flowing traffic, optimal fuel efficiency
    "Stop-Start": 1.3   # Heavy traffic, frequent braking, 30% more emissions
}


def calculate_co2_emission(
    distance_km: float,
    emission_factor_gkm: float,
    traffic_type: str
) -> float:
    """
    Calculate CO₂ emissions for a route.
    
    Formula (Industry-standard approximation):
        CO₂ (kg) = (distance_km × emission_factor_gkm × traffic_multiplier) / 1000
    
    Parameters:
        distance_km (float): Route distance in kilometers
        emission_factor_gkm (float): Vehicle emission factor (grams CO₂ per km)
        traffic_type (str): "Smooth" or "Stop-Start"
    
    Returns:
        float: CO₂ emissions in kilograms
    
    Example:
        20km × 120g/km × 1.3 (stop-start) = 3,120g = 3.12kg CO₂
    """
    traffic_multiplier = TRAFFIC_MULTIPLIERS.get(traffic_type, 1.0)
    co2_kg = (distance_km * emission_factor_gkm * traffic_multiplier) / 1000
    return round(co2_kg, 2)


def calculate_eta(distance_km: float, avg_speed_kmph: float) -> float:
    """
    Calculate Estimated Time of Arrival.
    
    Parameters:
        distance_km (float): Route distance in kilometers
        avg_speed_kmph (float): Average speed in km/h
    
    Returns:
        float: ETA in hours
    
    Example:
        20km ÷ 25km/h = 0.8 hours (48 minutes)
    """
    eta_hours = distance_km / avg_speed_kmph
    return round(eta_hours, 2)


def co2_speed_tradeoff(emission_factor_gkm: float) -> dict:
    """
    Compare Fast route vs Green route for sustainability-aware decision making.
    
    Route Definitions:
        Fast Route:  Shorter distance (20km), Heavy traffic (stop-start), Slower speed (25 km/h)
                     → Lower ETA but HIGHER emissions (stop-start traffic)
        
        Green Route: Longer distance (24km), Smooth traffic, Faster speed (40 km/h)
                     → Higher ETA but LOWER emissions (smooth traffic)
    
    Parameters:
        emission_factor_gkm (float): Vehicle emission factor (g CO₂/km)
                                     - Bike: ~50 g/km
                                     - Van: ~120 g/km
                                     - Truck: ~200 g/km
    
    Returns:
        dict: {
            "fast_route": {"eta_hours": float, "co2_kg": float},
            "green_route": {"eta_hours": float, "co2_kg": float},
            "co2_saved_kg": float,
            "time_cost_hours": float,
            "recommendation": str
        }
    
    Use Case:
        Control Tower Dashboard shows this trade-off
        → Let humans decide: Speed vs Sustainability
    """
    # Route A: Fast (but polluting)
    fast_route = {
        "route": "Fast",
        "distance_km": 20,      # Shorter distance
        "traffic": "Stop-Start", # Heavy traffic (more emissions)
        "avg_speed": 25          # Slow due to traffic
    }
    
    # Route B: Green (but slower)
    green_route = {
        "route": "Green",
        "distance_km": 24,      # Longer distance
        "traffic": "Smooth",    # Free-flowing (less emissions)
        "avg_speed": 40         # Faster due to smooth traffic
    }
    
    # Calculate emissions for both routes
    fast_co2 = calculate_co2_emission(
        fast_route["distance_km"],
        emission_factor_gkm,
        fast_route["traffic"]
    )
    
    green_co2 = calculate_co2_emission(
        green_route["distance_km"],
        emission_factor_gkm,
        green_route["traffic"]
    )
    
    # Calculate ETA for both routes
    fast_eta = calculate_eta(
        fast_route["distance_km"],
        fast_route["avg_speed"]
    )
    
    green_eta = calculate_eta(
        green_route["distance_km"],
        green_route["avg_speed"]
    )
    
    # Calculate trade-offs
    co2_saved = round(fast_co2 - green_co2, 2)
    time_cost = round(green_eta - fast_eta, 2)
    
    # Generate recommendation (informative, not prescriptive)
    if co2_saved > 1.0:
        recommendation = f"Green route saves {co2_saved}kg CO₂ at cost of {abs(time_cost)} extra hours"
    else:
        recommendation = f"Minimal CO₂ difference ({co2_saved}kg), fast route recommended"
    
    return {
        "fast_route": {
            "eta_hours": fast_eta,
            "co2_kg": fast_co2,
            "distance_km": fast_route["distance_km"],
            "traffic": fast_route["traffic"]
        },
        "green_route": {
            "eta_hours": green_eta,
            "co2_kg": green_co2,
            "distance_km": green_route["distance_km"],
            "traffic": green_route["traffic"]
        },
        "co2_saved_kg": co2_saved,
        "time_cost_hours": time_cost,
        "recommendation": recommendation
    }


def get_vehicle_emission_factor(vehicle_type: str) -> float:
    """
    Get standard emission factors for different vehicle types.
    
    Parameters:
        vehicle_type (str): Bike / Van / Truck
    
    Returns:
        float: Emission factor in grams CO₂ per km
    
    Sources: Industry averages for Indian logistics vehicles
    """
    emission_factors = {
        "Bike": 50,      # Two-wheeler: Low emissions
        "Van": 120,      # Small commercial vehicle: Moderate
        "Truck": 200     # Heavy goods vehicle: High emissions
    }
    return emission_factors.get(vehicle_type, 120)


def calculate_co2_percentage_saved(fast_co2: float, green_co2: float) -> float:
    """
    Calculate percentage of CO₂ saved by choosing green route.
    
    Parameters:
        fast_co2 (float): CO₂ from fast route (kg)
        green_co2 (float): CO₂ from green route (kg)
    
    Returns:
        float: Percentage saved
    """
    if fast_co2 == 0:
        return 0.0
    percentage = ((fast_co2 - green_co2) / fast_co2) * 100
    return round(percentage, 1)


def sustainability_score(co2_kg: float) -> str:
    """
    Convert CO₂ emissions to sustainability grade.
    
    Parameters:
        co2_kg (float): CO₂ emissions in kg
    
    Returns:
        str: Grade (A/B/C/D/F)
    
    Grading Scale (per delivery):
        A: < 1.0 kg   (Excellent - Bike/short distance)
        B: 1.0-2.0 kg (Good - Van/moderate)
        C: 2.0-3.0 kg (Average)
        D: 3.0-5.0 kg (Poor - Heavy vehicle/long distance)
        F: > 5.0 kg   (Very Poor)
    """
    if co2_kg < 1.0:
        return "A (Excellent)"
    elif co2_kg < 2.0:
        return "B (Good)"
    elif co2_kg < 3.0:
        return "C (Average)"
    elif co2_kg < 5.0:
        return "D (Poor)"
    else:
        return "F (Very Poor)"


def format_tradeoff_for_dashboard(tradeoff: dict) -> str:
    """
    Format trade-off data for human-readable display.
    
    Parameters:
        tradeoff (dict): Output from co2_speed_tradeoff()
    
    Returns:
        str: Formatted comparison text
    """
    fast = tradeoff["fast_route"]
    green = tradeoff["green_route"]
    
    output = []
    output.append("=" * 50)
    output.append("CO₂ vs SPEED TRADE-OFF ANALYSIS")
    output.append("=" * 50)
    output.append("")
    output.append("🚀 FAST ROUTE:")
    output.append(f"   ETA: {fast['eta_hours']} hours")
    output.append(f"   CO₂: {fast['co2_kg']} kg")
    output.append(f"   Grade: {sustainability_score(fast['co2_kg'])}")
    output.append("")
    output.append("🌍 GREEN ROUTE:")
    output.append(f"   ETA: {green['eta_hours']} hours")
    output.append(f"   CO₂: {green['co2_kg']} kg")
    output.append(f"   Grade: {sustainability_score(green['co2_kg'])}")
    output.append("")
    output.append("📊 COMPARISON:")
    output.append(f"   CO₂ Saved: {tradeoff['co2_saved_kg']} kg")
    
    pct_saved = calculate_co2_percentage_saved(fast['co2_kg'], green['co2_kg'])
    output.append(f"   Percentage Saved: {pct_saved}%")
    output.append(f"   Time Cost: {abs(tradeoff['time_cost_hours'])} hours extra")
    output.append("")
    output.append(f"💡 RECOMMENDATION: {tradeoff['recommendation']}")
    output.append("=" * 50)
    
    return "\n".join(output)
