import json
import os
import time
import logging

import requests
from plyer import gps

from config import (
    NOMINATIM_URL,
    GEOCODE_CACHE_FILE,
    DEFAULT_LAT,
    DEFAULT_LON,
    DEFAULT_CITY,
    NOMINATIM_RATE_LIMIT,
)

logger = logging.getLogger("SkyView.GPSService")


class GPSService:
    """Service for GPS location tracking and reverse geocoding."""

    def __init__(self):
        self.lat = None
        self.lon = None
        self.city_name = None
        self.gps_active = False
        self.last_geocode_time = 0
        self.geocode_cache = self._load_geocode_cache()

    def start_gps(self, on_location_update, on_status_change=None):
        """Start GPS tracking with fallback to default coordinates."""
        try:
            gps.configure(on_location=on_location_update, on_status=on_status_change)
            gps.start(minTime=300000, minDistance=100)  # 5 min or 100m
            self.gps_active = True
            logger.info("GPS started")
        except NotImplementedError:
            logger.warning("GPS not supported on this platform. Using default/fallback.")
            self.lat = DEFAULT_LAT
            self.lon = DEFAULT_LON
            self.gps_active = False
            if on_location_update:
                on_location_update(lat=self.lat, lon=self.lon)
        except Exception as e:
            logger.error(f"Unexpected GPS error: {e}")
            self.lat = DEFAULT_LAT
            self.lon = DEFAULT_LON
            self.gps_active = False
            if on_location_update:
                on_location_update(lat=self.lat, lon=self.lon)

    def stop_gps(self):
        """Stop GPS tracking."""
        if self.gps_active:
            try:
                gps.stop()
                self.gps_active = False
                logger.info("GPS stopped")
            except Exception as e:
                logger.warning(f"Error stopping GPS: {e}")

    def _load_geocode_cache(self) -> dict:
        """Load geocode cache from disk."""
        if os.path.exists(GEOCODE_CACHE_FILE):
            try:
                with open(GEOCODE_CACHE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (OSError, json.JSONDecodeError) as e:
                logger.warning(f"Error loading geocode cache: {e}")
        return {}

    def _save_geocode_cache(self) -> None:
        """Save geocode cache to disk."""
        try:
            with open(GEOCODE_CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.geocode_cache, f, ensure_ascii=False, indent=2)
        except OSError as e:
            logger.warning(f"Error saving geocode cache: {e}")

    def get_city_name(self, lat: float, lon: float) -> str:
        """
        Get city name from coordinates using Nominatim reverse geocoding.
        Uses local cache and respects rate limits.
        """
        # Round coords to increase cache hit rate
        cache_key = f"{round(lat, 3)},{round(lon, 3)}"

        if cache_key in self.geocode_cache:
            logger.debug(f"Geocode cache hit for {cache_key}")
            return self.geocode_cache[cache_key]

        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_geocode_time
        if time_since_last < NOMINATIM_RATE_LIMIT:
            time.sleep(NOMINATIM_RATE_LIMIT - time_since_last)

        try:
            headers = {'User-Agent': 'SkyViewWeatherApp/1.0'}
            params = {
                'lat': lat,
                'lon': lon,
                'format': 'json',
                'zoom': 10,  # city level
                'addressdetails': 1
            }
            response = requests.get(
                NOMINATIM_URL,
                params=params,
                headers=headers,
                timeout=5
            )
            self.last_geocode_time = time.time()

            if response.status_code == 200:
                data = response.json()
                address = data.get('address', {})
                city = (
                    address.get('city')
                    or address.get('town')
                    or address.get('village')
                    or address.get('county')
                    or DEFAULT_CITY
                )

                self.geocode_cache[cache_key] = city
                self._save_geocode_cache()
                logger.info(f"Geocoded ({lat}, {lon}) -> {city}")
                return city
            else:
                logger.warning(f"Nominatim returned status {response.status_code}")
        except requests.exceptions.Timeout:
            logger.error("Timeout contacting Nominatim")
        except requests.exceptions.ConnectionError:
            logger.error("Connection error contacting Nominatim")
        except Exception as e:
            logger.error(f"Error reverse geocoding: {e}")

        return DEFAULT_CITY
