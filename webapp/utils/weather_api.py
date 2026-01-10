"""
Weather API Integration for LICS
Real-time weather data with multiple provider fallback
"""

import requests
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import asyncio
import aiohttp
from dataclasses import dataclass
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Weather API Configuration
WEATHER_API_KEY = "591b801978da489596c71644260901"
WEATHER_API_BASE_URL = "http://api.weatherapi.com/v1"

# Backup weather APIs (free tiers)
OPENWEATHER_API_KEY = "your_openweather_key"  # You can get free API key
BACKUP_APIS = {
    "weatherapi": {
        "base_url": "http://api.weatherapi.com/v1",
        "key": WEATHER_API_KEY,
        "active": True
    },
    "openweathermap": {
        "base_url": "http://api.openweathermap.org/data/2.5",
        "key": OPENWEATHER_API_KEY,
        "active": False  # Set to True when you have API key
    }
}

@dataclass
class WeatherData:
    """Weather data structure"""
    city: str
    temperature: float
    condition: str
    humidity: int
    wind_speed: float
    visibility: float
    precipitation: float
    weather_code: int
    description: str
    feels_like: float
    uv_index: float
    pressure: float
    cloud_cover: int
    last_updated: datetime
    source: str

@dataclass 
class WeatherForecast:
    """Weather forecast structure"""
    date: str
    max_temp: float
    min_temp: float
    condition: str
    precipitation_chance: int
    precipitation_mm: float
    wind_speed: float
    humidity: int

class WeatherService:
    """Weather service with multiple provider fallback"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = 10
        self.cache = {}  # Simple in-memory cache
        self.cache_duration = 600  # 10 minutes in seconds
    
    def _is_cache_valid(self, city: str) -> bool:
        """Check if cached data is still valid"""
        if city not in self.cache:
            return False
        
        cache_time = self.cache[city].get('timestamp', 0)
        return (datetime.now().timestamp() - cache_time) < self.cache_duration
    
    def _get_cached_weather(self, city: str) -> Optional[WeatherData]:
        """Get weather data from cache"""
        if self._is_cache_valid(city):
            return self.cache[city]['data']
        return None
    
    def _cache_weather_data(self, city: str, data: WeatherData):
        """Cache weather data"""
        self.cache[city] = {
            'data': data,
            'timestamp': datetime.now().timestamp()
        }
    
    def get_current_weather(self, city: str) -> Optional[WeatherData]:
        """Get current weather for a city"""
        # Check cache first
        cached_data = self._get_cached_weather(city)
        if cached_data:
            logger.info(f"🔄 Using cached weather data for {city}")
            return cached_data
        
        # Try primary API (WeatherAPI.com)
        try:
            weather_data = self._get_weatherapi_current(city)
            if weather_data:
                self._cache_weather_data(city, weather_data)
                logger.info(f"🌤️ Weather data fetched for {city} from WeatherAPI")
                return weather_data
        except Exception as e:
            logger.warning(f"⚠️ WeatherAPI failed for {city}: {str(e)}")
        
        # Fallback to OpenWeatherMap (if configured)
        if BACKUP_APIS["openweathermap"]["active"]:
            try:
                weather_data = self._get_openweather_current(city)
                if weather_data:
                    self._cache_weather_data(city, weather_data)
                    logger.info(f"🌤️ Weather data fetched for {city} from OpenWeatherMap")
                    return weather_data
            except Exception as e:
                logger.warning(f"⚠️ OpenWeatherMap failed for {city}: {str(e)}")
        
        logger.error(f"❌ All weather APIs failed for {city}")
        return None
    
    def _get_weatherapi_current(self, city: str) -> Optional[WeatherData]:
        """Get weather from WeatherAPI.com"""
        url = f"{WEATHER_API_BASE_URL}/current.json"
        params = {
            "key": WEATHER_API_KEY,
            "q": city,
            "aqi": "no"
        }
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        current = data["current"]
        location = data["location"]
        
        return WeatherData(
            city=f"{location['name']}, {location['region']}",
            temperature=current["temp_c"],
            condition=current["condition"]["text"],
            humidity=current["humidity"],
            wind_speed=current["wind_kph"],
            visibility=current["vis_km"],
            precipitation=current["precip_mm"],
            weather_code=current["condition"]["code"],
            description=current["condition"]["text"],
            feels_like=current["feelslike_c"],
            uv_index=current["uv"],
            pressure=current["pressure_mb"],
            cloud_cover=current["cloud"],
            last_updated=datetime.strptime(current["last_updated"], "%Y-%m-%d %H:%M"),
            source="WeatherAPI"
        )
    
    def _get_openweather_current(self, city: str) -> Optional[WeatherData]:
        """Get weather from OpenWeatherMap (backup)"""
        if not BACKUP_APIS["openweathermap"]["active"]:
            return None
        
        url = f"{BACKUP_APIS['openweathermap']['base_url']}/weather"
        params = {
            "q": city,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"
        }
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        main = data["main"]
        weather = data["weather"][0]
        wind = data.get("wind", {})
        
        return WeatherData(
            city=f"{data['name']}, {data['sys']['country']}",
            temperature=main["temp"],
            condition=weather["main"],
            humidity=main["humidity"],
            wind_speed=wind.get("speed", 0) * 3.6,  # Convert m/s to km/h
            visibility=data.get("visibility", 10000) / 1000,  # Convert m to km
            precipitation=0,  # Not available in current weather
            weather_code=weather["id"],
            description=weather["description"].title(),
            feels_like=main["feels_like"],
            uv_index=0,  # Not available in free tier
            pressure=main["pressure"],
            cloud_cover=data.get("clouds", {}).get("all", 0),
            last_updated=datetime.utcnow(),
            source="OpenWeatherMap"
        )
    
    def get_forecast(self, city: str, days: int = 3) -> List[WeatherForecast]:
        """Get weather forecast for a city"""
        try:
            url = f"{WEATHER_API_BASE_URL}/forecast.json"
            params = {
                "key": WEATHER_API_KEY,
                "q": city,
                "days": min(days, 10),  # API limit
                "aqi": "no",
                "alerts": "no"
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            forecast_days = data["forecast"]["forecastday"]
            
            forecasts = []
            for day_data in forecast_days:
                day = day_data["day"]
                forecasts.append(WeatherForecast(
                    date=day_data["date"],
                    max_temp=day["maxtemp_c"],
                    min_temp=day["mintemp_c"],
                    condition=day["condition"]["text"],
                    precipitation_chance=day["daily_chance_of_rain"],
                    precipitation_mm=day["totalprecip_mm"],
                    wind_speed=day["maxwind_kph"],
                    humidity=day["avghumidity"]
                ))
            
            logger.info(f"📅 {days}-day forecast fetched for {city}")
            return forecasts
            
        except Exception as e:
            logger.error(f"❌ Failed to get forecast for {city}: {str(e)}")
            return []
    
    def calculate_weather_impact(self, weather_data: WeatherData) -> Dict[str, Any]:
        """Calculate weather impact on delivery"""
        if not weather_data:
            return {
                "severity": "unknown",
                "delay_factor": 1.0,
                "risk_score": 50,
                "recommendations": ["Weather data unavailable"]
            }
        
        risk_score = 0
        recommendations = []
        delay_factor = 1.0
        
        # Temperature impact
        if weather_data.temperature > 40 or weather_data.temperature < 5:
            risk_score += 15
            recommendations.append("Extreme temperature conditions")
            delay_factor += 0.1
        
        # Precipitation impact
        if weather_data.precipitation > 10:
            risk_score += 25
            recommendations.append("Heavy precipitation expected")
            delay_factor += 0.3
        elif weather_data.precipitation > 5:
            risk_score += 15
            recommendations.append("Moderate precipitation expected")
            delay_factor += 0.15
        elif weather_data.precipitation > 0:
            risk_score += 5
            recommendations.append("Light precipitation possible")
            delay_factor += 0.05
        
        # Wind impact
        if weather_data.wind_speed > 50:
            risk_score += 20
            recommendations.append("High wind conditions")
            delay_factor += 0.2
        elif weather_data.wind_speed > 30:
            risk_score += 10
            recommendations.append("Moderate wind conditions")
            delay_factor += 0.1
        
        # Visibility impact
        if weather_data.visibility < 1:
            risk_score += 30
            recommendations.append("Very poor visibility")
            delay_factor += 0.4
        elif weather_data.visibility < 5:
            risk_score += 15
            recommendations.append("Poor visibility conditions")
            delay_factor += 0.2
        
        # Determine severity
        if risk_score >= 50:
            severity = "high"
        elif risk_score >= 25:
            severity = "medium"
        else:
            severity = "low"
        
        # Add general recommendations
        if severity == "high":
            recommendations.extend([
                "Consider delaying dispatch",
                "Use experienced drivers only",
                "Increase delivery time buffer"
            ])
        elif severity == "medium":
            recommendations.extend([
                "Monitor weather closely",
                "Add extra delivery time",
                "Inform customers of potential delays"
            ])
        else:
            recommendations.append("Normal delivery conditions")
        
        return {
            "severity": severity,
            "delay_factor": min(delay_factor, 2.0),  # Cap at 2x delay
            "risk_score": min(risk_score, 100),
            "recommendations": recommendations,
            "weather_condition": weather_data.condition,
            "temperature": weather_data.temperature,
            "precipitation": weather_data.precipitation,
            "wind_speed": weather_data.wind_speed,
            "visibility": weather_data.visibility
        }
    
    def get_weather_alerts(self, cities: List[str]) -> List[Dict[str, Any]]:
        """Get weather alerts for multiple cities"""
        alerts = []
        
        for city in cities:
            weather = self.get_current_weather(city)
            if weather:
                impact = self.calculate_weather_impact(weather)
                
                if impact["severity"] in ["medium", "high"]:
                    alerts.append({
                        "city": city,
                        "severity": impact["severity"],
                        "condition": weather.condition,
                        "risk_score": impact["risk_score"],
                        "recommendations": impact["recommendations"],
                        "timestamp": weather.last_updated.isoformat()
                    })
        
        return alerts

# Global weather service instance
weather_service = WeatherService()

# Convenience functions
def get_weather(city: str) -> Optional[WeatherData]:
    """Get current weather for a city"""
    return weather_service.get_current_weather(city)

def get_weather_impact(city: str) -> Dict[str, Any]:
    """Get weather impact analysis for a city"""
    weather_data = get_weather(city)
    return weather_service.calculate_weather_impact(weather_data)

def get_weather_forecast(city: str, days: int = 3) -> List[WeatherForecast]:
    """Get weather forecast for a city"""
    return weather_service.get_forecast(city, days)

def test_weather_api():
    """Test weather API functionality"""
    test_cities = ["Delhi", "Mumbai", "Bangalore"]
    results = {}
    
    for city in test_cities:
        try:
            weather = get_weather(city)
            if weather:
                impact = weather_service.calculate_weather_impact(weather)
                results[city] = {
                    "status": "success",
                    "temperature": weather.temperature,
                    "condition": weather.condition,
                    "impact_severity": impact["severity"],
                    "source": weather.source
                }
            else:
                results[city] = {"status": "failed", "error": "No data"}
        except Exception as e:
            results[city] = {"status": "error", "error": str(e)}
    
    return results

# Indian major cities for quick reference
INDIAN_MAJOR_CITIES = [
    "Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata", 
    "Hyderabad", "Pune", "Ahmedabad", "Jaipur", "Lucknow",
    "Kanpur", "Nagpur", "Indore", "Thane", "Bhopal",
    "Visakhapatnam", "Pimpri-Chinchwad", "Patna", "Vadodara", "Ghaziabad"
]