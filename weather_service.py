import json
import os
import logging
import datetime

import requests

from config import OPEN_METEO_URL, CACHE_FILE

logger = logging.getLogger("SkyView.WeatherService")


class WeatherService:
    """Service for fetching weather data from Open-Meteo API with local caching."""

    def __init__(self):
        self.cached_data = None
        self.is_offline = False

    def fetch_weather(self, lat: float, lon: float) -> tuple:
        """
        Fetch weather data from Open-Meteo API.

        Returns:
            tuple: (data_dict, is_offline_bool)
        """
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": (
                "temperature_2m,apparent_temperature,is_day,precipitation,"
                "weather_code,cloud_cover,pressure_msl,surface_pressure,"
                "wind_speed_10m,wind_direction_10m,wind_gusts_10m,"
                "relative_humidity_2m,uv_index"
            ),
            "hourly": "temperature_2m,precipitation_probability,weather_code",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min",
            "timezone": "auto"
        }

        try:
            response = requests.get(OPEN_METEO_URL, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                data['timestamp'] = datetime.datetime.now().isoformat()
                self._save_cache(data)
                self.cached_data = data
                self.is_offline = False
                logger.info(f"Weather fetched for ({lat}, {lon})")
                return data, False
            else:
                logger.warning(f"Open-Meteo returned status {response.status_code}")
                return self._load_cache(), True
        except requests.exceptions.Timeout:
            logger.error("Timeout fetching weather data")
            return self._load_cache(), True
        except requests.exceptions.ConnectionError:
            logger.error("Connection error fetching weather data")
            return self._load_cache(), True
        except Exception as e:
            logger.error(f"Unexpected error fetching weather: {e}")
            return self._load_cache(), True

    def _save_cache(self, data: dict) -> None:
        """Save weather data to local cache file."""
        try:
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.debug("Weather cache saved")
        except (OSError, TypeError) as e:
            logger.error(f"Error saving cache: {e}")

    def _load_cache(self) -> dict | None:
        """Load weather data from local cache file."""
        self.is_offline = True
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                    self.cached_data = json.load(f)
                    logger.info("Weather loaded from cache")
                    return self.cached_data
            except (OSError, json.JSONDecodeError) as e:
                logger.error(f"Error loading cache: {e}")
        return None
