"""
Weather Impact Engine - Environmental Risk Assessment

Purpose: Integrate live weather data and compute delivery impact
Output: Weather Impact Factor, ETA Buffer Multiplier, Risk Assessment
Approach: Live API + Historical flood data

Used before dispatch to:
- Adjust delivery expectations
- Calculate risk scores
- Trigger weather-based delays
"""

import requests
from datetime import datetime
from typing import Dict, Optional

# Weather API Configuration
# Primary: WeatherAPI.com (Free: 1M calls/month, instant activation)
# Fallback: OpenWeatherMap
WEATHER_API_PROVIDER = "weatherapi"  # Options: "weatherapi", "openweathermap"

# WeatherAPI.com (Recommended - instant activation)
WEATHERAPI_KEY = "591b801978da489596c71644260901"
WEATHERAPI_BASE = "http://api.weatherapi.com/v1/current.json"

# OpenWeatherMap (Alternative)
OPENWEATHER_KEY = "030a7b27f63df5e520c3e9e08a58804a"
OPENWEATHER_BASE = "https://api.openweathermap.org/data/2.5/weather"

# Weather severity thresholds
RAIN_THRESHOLDS = {
    "Clear": 0,
    "Light Rain": 2.5,
    "Moderate Rain": 7.6,
    "Heavy Rain": 50
}

WIND_THRESHOLDS = {
    "Calm": 5,
    "Moderate": 15,
    "Strong": 25
}

# Historical flood-prone cities (India)
FLOOD_RISK_CITIES = {
    "Mumbai": "High",
    "Kolkata": "High",
    "Chennai": "High",
    "Bangalore": "Medium",
    "Hyderabad": "Medium",
    "Delhi": "Low",
    "Pune": "Low",
    "Ahmedabad": "Low"
}


def fetch_live_weather(city: str, provider: str = WEATHER_API_PROVIDER) -> Optional[Dict]:
    """
    Fetch live weather data from weather API.
    
    Parameters:
        city (str): City name
        provider (str): "weatherapi" or "openweathermap"
    
    Returns:
        dict: Weather data or None if failed
    """
    try:
        if provider == "weatherapi":
            # WeatherAPI.com
            params = {
                "key": WEATHERAPI_KEY,
                "q": f"{city},India",
                "aqi": "no"
            }
            response = requests.get(WEATHERAPI_BASE, params=params, timeout=5)
            
            if response.status_code == 200:
                return {"provider": "weatherapi", "data": response.json()}
            else:
                print(f"⚠️  WeatherAPI error for {city}: {response.status_code}")
                return None
        
        else:  # openweathermap
            params = {
                "q": f"{city},IN",
                "appid": OPENWEATHER_KEY,
                "units": "metric"
            }
            response = requests.get(OPENWEATHER_BASE, params=params, timeout=5)
            
            if response.status_code == 200:
                return {"provider": "openweathermap", "data": response.json()}
            else:
                print(f"⚠️  OpenWeather error for {city}: {response.status_code}")
                return None
                
    except Exception as e:
        print(f"⚠️  Failed to fetch weather for {city}: {str(e)}")
        return None


def parse_weather_data(weather_response: Dict) -> Dict:
    """
    Parse weather API response into useful metrics.
    
    Parameters:
        weather_response (dict): Response with provider and data
    
    Returns:
        dict: Parsed weather metrics
    """
    if not weather_response:
        return None
    
    try:
        provider = weather_response.get("provider")
        data = weather_response.get("data")
        
        if provider == "weatherapi":
            # Parse WeatherAPI.com response
            current = data.get("current", {})
            condition = current.get("condition", {}).get("text", "Clear")
            
            # Map condition to standard format
            if "rain" in condition.lower() or "drizzle" in condition.lower():
                weather_main = "Rain"
            elif "storm" in condition.lower() or "thunder" in condition.lower():
                weather_main = "Thunderstorm"
            elif "cloud" in condition.lower():
                weather_main = "Clouds"
            else:
                weather_main = "Clear"
            
            return {
                "condition": weather_main,
                "description": condition.lower(),
                "temperature": current.get("temp_c", 25),
                "humidity": current.get("humidity", 50),
                "wind_speed": current.get("wind_kph", 0) / 3.6,  # Convert to m/s
                "rainfall_mm": current.get("precip_mm", 0),
                "timestamp": datetime.now().isoformat()
            }
        
        else:  # openweathermap
            weather_main = data.get("weather", [{}])[0].get("main", "Clear")
            weather_desc = data.get("weather", [{}])[0].get("description", "clear sky")
            
            temp = data.get("main", {}).get("temp", 25)
            humidity = data.get("main", {}).get("humidity", 50)
            wind_speed = data.get("wind", {}).get("speed", 0)
            rain_1h = data.get("rain", {}).get("1h", 0)
            
            return {
                "condition": weather_main,
                "description": weather_desc,
                "temperature": temp,
                "humidity": humidity,
                "wind_speed": wind_speed,
                "rainfall_mm": rain_1h,
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        print(f"⚠️  Error parsing weather data: {str(e)}")
        return None


def determine_weather_severity(rainfall_mm: float, wind_speed: float, condition: str) -> str:
    """
    Determine weather severity level based on conditions.
    
    Parameters:
        rainfall_mm (float): Rainfall in mm/hour
        wind_speed (float): Wind speed in m/s
        condition (str): Weather condition (Clear/Rain/Storm/etc)
    
    Returns:
        str: "Low", "Medium", or "High"
    """
    severity = "Low"
    
    # Check rainfall
    if rainfall_mm > RAIN_THRESHOLDS["Heavy Rain"]:
        severity = "High"
    elif rainfall_mm > RAIN_THRESHOLDS["Moderate Rain"]:
        severity = "Medium" if severity == "Low" else severity
    elif rainfall_mm > RAIN_THRESHOLDS["Light Rain"]:
        severity = "Medium" if severity == "Low" else severity
    
    # Check wind
    if wind_speed > WIND_THRESHOLDS["Strong"]:
        severity = "High"
    elif wind_speed > WIND_THRESHOLDS["Moderate"]:
        severity = "Medium" if severity == "Low" else severity
    
    # Check extreme conditions
    if condition in ["Thunderstorm", "Storm", "Tornado"]:
        severity = "High"
    elif condition in ["Drizzle", "Rain", "Snow"]:
        severity = "Medium" if severity == "Low" else severity
    
    return severity


def get_flood_risk(city: str) -> str:
    """
    Get historical flood risk for a city.
    
    Parameters:
        city (str): City name
    
    Returns:
        str: "High", "Medium", or "Low"
    """
    return FLOOD_RISK_CITIES.get(city, "Low")


def calculate_weather_impact_factor(
    weather_severity: str,
    flood_risk: str,
    rainfall_mm: float,
    humidity: float
) -> float:
    """
    Calculate weather impact factor (0-100).
    
    Higher score = Higher impact on delivery
    
    Parameters:
        weather_severity (str): Low/Medium/High
        flood_risk (str): Low/Medium/High
        rainfall_mm (float): Current rainfall
        humidity (float): Humidity percentage
    
    Returns:
        float: Impact factor 0-100
    """
    impact = 10  # Base impact
    
    # Weather severity
    if weather_severity == "High":
        impact += 40
    elif weather_severity == "Medium":
        impact += 20
    
    # Flood risk
    if flood_risk == "High":
        impact += 25
    elif flood_risk == "Medium":
        impact += 15
    
    # Rainfall impact
    if rainfall_mm > 10:
        impact += 15
    elif rainfall_mm > 5:
        impact += 10
    
    # Humidity impact (high humidity + rain = worse)
    if humidity > 80 and rainfall_mm > 0:
        impact += 10
    
    return min(100, impact)


def calculate_eta_buffer_multiplier(weather_impact_factor: float) -> float:
    """
    Calculate ETA buffer multiplier based on weather impact.
    
    Multiplier is applied to normal ETA to get realistic delivery time.
    
    Parameters:
        weather_impact_factor (float): Impact factor 0-100
    
    Returns:
        float: Multiplier (1.0 = no delay, 2.0 = double time, etc.)
    """
    if weather_impact_factor >= 70:
        return 2.0  # Double the delivery time
    elif weather_impact_factor >= 50:
        return 1.5  # 50% more time
    elif weather_impact_factor >= 30:
        return 1.2  # 20% more time
    else:
        return 1.0  # No delay


def get_weather_impact(city: str, use_live_api: bool = True, provider: str = WEATHER_API_PROVIDER) -> Dict:
    """
    End-to-end weather impact assessment for a city.
    
    Parameters:
        city (str): City name
        use_live_api (bool): If False, use simulated data
        provider (str): "weatherapi" or "openweathermap"
    
    Returns:
        dict: Complete weather impact assessment
    """
    # Get flood risk
    flood_risk = get_flood_risk(city)
    
    if use_live_api:
        # Fetch live weather
        weather_response = fetch_live_weather(city, provider)
        
        if weather_response:
            weather_data = parse_weather_data(weather_response)
            
            if weather_data:
                severity = determine_weather_severity(
                    weather_data["rainfall_mm"],
                    weather_data["wind_speed"],
                    weather_data["condition"]
                )
                
                impact_factor = calculate_weather_impact_factor(
                    severity,
                    flood_risk,
                    weather_data["rainfall_mm"],
                    weather_data["humidity"]
                )
                
                eta_multiplier = calculate_eta_buffer_multiplier(impact_factor)
                
                return {
                    "city": city,
                    "weather_condition": weather_data["condition"],
                    "weather_description": weather_data["description"],
                    "temperature": weather_data["temperature"],
                    "rainfall_mm": weather_data["rainfall_mm"],
                    "wind_speed": weather_data["wind_speed"],
                    "humidity": weather_data["humidity"],
                    "weather_severity": severity,
                    "flood_risk": flood_risk,
                    "weather_impact_factor": impact_factor,
                    "eta_buffer_multiplier": eta_multiplier,
                    "timestamp": weather_data["timestamp"],
                    "source": f"live_api_{provider}"
                }
    
    # Fallback: Use simulated/historical data
    return get_simulated_weather_impact(city, flood_risk)


def get_simulated_weather_impact(city: str, flood_risk: str) -> Dict:
    """
    Generate simulated weather impact (fallback when API unavailable).
    
    Parameters:
        city (str): City name
        flood_risk (str): Flood risk level
    
    Returns:
        dict: Simulated weather impact
    """
    import random
    
    # Simulate weather conditions
    conditions = ["Clear", "Clouds", "Rain", "Drizzle"]
    weights = [0.5, 0.3, 0.15, 0.05]
    condition = random.choices(conditions, weights=weights)[0]
    
    rainfall = random.uniform(0, 15) if condition in ["Rain", "Drizzle"] else 0
    wind_speed = random.uniform(2, 20)
    humidity = random.uniform(40, 90)
    temp = random.uniform(15, 35)
    
    severity = determine_weather_severity(rainfall, wind_speed, condition)
    impact_factor = calculate_weather_impact_factor(severity, flood_risk, rainfall, humidity)
    eta_multiplier = calculate_eta_buffer_multiplier(impact_factor)
    
    return {
        "city": city,
        "weather_condition": condition,
        "weather_description": condition.lower(),
        "temperature": round(temp, 1),
        "rainfall_mm": round(rainfall, 2),
        "wind_speed": round(wind_speed, 1),
        "humidity": round(humidity, 1),
        "weather_severity": severity,
        "flood_risk": flood_risk,
        "weather_impact_factor": round(impact_factor, 1),
        "eta_buffer_multiplier": eta_multiplier,
        "timestamp": datetime.now().isoformat(),
        "source": "simulated"
    }


def should_delay_dispatch(weather_impact_factor: float, weather_severity: str) -> bool:
    """
    Determine if dispatch should be delayed due to weather.
    
    Parameters:
        weather_impact_factor (float): Impact factor 0-100
        weather_severity (str): Low/Medium/High
    
    Returns:
        bool: True if dispatch should be delayed
    """
    # High impact OR high severity = delay
    return weather_impact_factor >= 70 or weather_severity == "High"
