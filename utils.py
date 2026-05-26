import datetime
from typing import Optional, Tuple


def wind_direction_to_cardinal(degrees: Optional[float]) -> str:
    """Convert wind direction in degrees to cardinal direction."""
    if degrees is None:
        return "N/A"
    directions = ["N", "NE", "E", "SE", "S", "SO", "O", "NO"]
    index = round(degrees / 45) % 8
    return directions[index]


def wmo_code_to_italian(code: Optional[int]) -> Tuple[str, str]:
    """
    Convert WMO weather code to Italian description and Material icon name.

    Returns:
        Tuple of (description, icon_name)
    """
    if code is None:
        return ("Sconosciuto", "cloud-question")

    weather_codes = {
        0: ("Cielo sereno", "weather-sunny"),
        1: ("Prevalentemente sereno", "weather-partly-cloudy"),
        2: ("Parzialmente nuvoloso", "weather-partly-cloudy"),
        3: ("Coperto", "weather-cloudy"),
        45: ("Nebbia", "weather-fog"),
        48: ("Nebbia con brina", "weather-fog"),
        51: ("Pioviggine leggera", "weather-rainy"),
        53: ("Pioviggine moderata", "weather-rainy"),
        55: ("Pioviggine fitta", "weather-pouring"),
        56: ("Pioviggine gelata leggera", "weather-snowy-rainy"),
        57: ("Pioviggine gelata fitta", "weather-snowy-rainy"),
        61: ("Pioggia debole", "weather-rainy"),
        63: ("Pioggia moderata", "weather-pouring"),
        65: ("Pioggia forte", "weather-pouring"),
        66: ("Pioggia gelata debole", "weather-snowy-rainy"),
        67: ("Pioggia gelata forte", "weather-snowy-rainy"),
        71: ("Neve debole", "weather-snowy"),
        73: ("Neve moderata", "weather-snowy"),
        75: ("Neve forte", "weather-snowy-heavy"),
        77: ("Neve granulare", "weather-hail"),
        80: ("Rovesci di pioggia deboli", "weather-partly-rainy"),
        81: ("Rovesci di pioggia moderati", "weather-pouring"),
        82: ("Rovesci di pioggia violenti", "weather-pouring"),
        85: ("Rovesci di neve deboli", "weather-snowy"),
        86: ("Rovesci di neve forti", "weather-snowy-heavy"),
        95: ("Temporale", "weather-lightning"),
        96: ("Temporale con grandine leggera", "weather-lightning-rainy"),
        99: ("Temporale con grandine forte", "weather-lightning-rainy"),
    }
    return weather_codes.get(code, ("Sconosciuto", "cloud-question"))


def format_timestamp(iso_string: Optional[str]) -> str:
    """Format ISO timestamp to Italian datetime string."""
    if not iso_string:
        return ""
    try:
        dt = datetime.datetime.fromisoformat(iso_string)
        return dt.strftime("%d/%m/%Y %H:%M")
    except (ValueError, TypeError):
        return str(iso_string)


def get_day_name(iso_string: Optional[str]) -> str:
    """Get Italian day name from ISO date string."""
    if not iso_string:
        return ""
    try:
        dt = datetime.datetime.fromisoformat(iso_string)
        giorni = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
        return giorni[dt.weekday()]
    except (ValueError, TypeError):
        return str(iso_string)


def format_hour(iso_string: Optional[str]) -> str:
    """Extract hour:minute from ISO datetime string."""
    if not iso_string:
        return ""
    try:
        dt = datetime.datetime.fromisoformat(iso_string)
        return dt.strftime("%H:%M")
    except (ValueError, TypeError):
        return str(iso_string)
