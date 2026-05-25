import os

# API Endpoints
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"

# Cache Files
CACHE_FILE = "ultima_posizione.json"
GEOCODE_CACHE_FILE = "geocode_cache.json"
NOMINATIM_MAP_CACHE_FILE = "nominatim_cache.json"
FAVORITES_FILE = "favorites.json"

# Settings
RAINVIEWER_URL = "https://tilecache.rainviewer.com"
MAX_FAVORITES = 20

# Timing
GPS_UPDATE_INTERVAL = 300  # 5 minutes
NOMINATIM_RATE_LIMIT = 1.0 # Max 1 req/sec

# Defaults
DEFAULT_LAT = 41.9028  # Rome
DEFAULT_LON = 12.4964
DEFAULT_CITY = "Roma"
