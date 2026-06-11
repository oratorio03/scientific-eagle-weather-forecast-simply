import pytest
from utils import (
    wind_direction_to_cardinal,
    wmo_code_to_italian,
    format_timestamp,
    get_day_name,
    format_hour,
)


class TestWindDirectionToCardinal:
    @pytest.mark.parametrize(
        "degrees,expected",
        [
            (0, "N"),
            (45, "NE"),
            (90, "E"),
            (135, "SE"),
            (180, "S"),
            (225, "SO"),
            (270, "O"),
            (315, "NO"),
            (360, "N"),
            (23, "NE"),     # arrotondamento per eccesso
            (None, "N/A"),
            (-45, "NO"),    # angolo negativo, robustezza
            (720, "N"),     # angolo > 360, robustezza
        ],
    )
    def test_wind_direction(self, degrees, expected):
        assert wind_direction_to_cardinal(degrees) == expected


class TestWmoCodeToItalian:
    @pytest.mark.parametrize(
        "code,expected_desc,expected_icon",
        [
            (0, "Cielo sereno", "weather-sunny"),
            (1, "Prevalentemente sereno", "weather-partly-cloudy"),
            (3, "Coperto", "weather-cloudy"),
            (45, "Nebbia", "weather-fog"),
            (61, "Pioggia debole", "weather-rainy"),
            (95, "Temporale", "weather-lightning"),
            (99, "Temporale con grandine forte", "weather-lightning-rainy"),
            (999, "Sconosciuto", "cloud-question"),  # codice inesistente
            (None, "Sconosciuto", "cloud-question"), # None
        ],
    )
    def test_known_codes(self, code, expected_desc, expected_icon):
        desc, icon = wmo_code_to_italian(code)
        assert desc == expected_desc
        assert icon == expected_icon
        assert isinstance(desc, str)
        assert isinstance(icon, str)


class TestFormatTimestamp:
    @pytest.mark.parametrize(
        "input_val,expected",
        [
            (None, ""),
            ("", ""),
            ("2024-06-11T14:30:00", "11/06/2024 14:30"),
            ("2024-01-01T00:00:00", "01/01/2024 00:00"),
            ("not-a-date", "not-a-date"),  # fallback
        ],
    )
    def test_format_timestamp(self, input_val, expected):
        assert format_timestamp(input_val) == expected


class TestGetDayName:
    @pytest.mark.parametrize(
        "input_val,expected",
        [
            (None, ""),
            ("", ""),
            ("2024-01-01", "Lunedì"),     # lunedì
            ("2024-01-02", "Martedì"),   # martedì
            ("2024-01-03", "Mercoledì"), # mercoledì
            ("2024-01-04", "Giovedì"),   # giovedì
            ("2024-01-05", "Venerdì"),   # venerdì
            ("2024-01-06", "Sabato"),    # sabato
            ("2024-01-07", "Domenica"),  # domenica
            ("malformed", "malformed"),  # fallback
        ],
    )
    def test_get_day_name(self, input_val, expected):
        assert get_day_name(input_val) == expected


class TestFormatHour:
    @pytest.mark.parametrize(
        "input_val,expected",
        [
            (None, ""),
            ("", ""),
            ("2024-06-11T09:05:00", "09:05"),
            ("2024-06-11T23:59:00", "23:59"),
            ("bad-time", "bad-time"),  # fallback
        ],
    )
    def test_format_hour(self, input_val, expected):
        assert format_hour(input_val) == expected
