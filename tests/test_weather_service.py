import json
import os
import tempfile
from unittest.mock import patch, MagicMock

import requests

from weather_service import WeatherService
import weather_service as weather_service_module


class TestFetchWeather:
    def setup_method(self):
        self.service = WeatherService()

    @patch("skyview.weather_service.requests.get")
    def test_fetch_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"current": {"temperature_2m": 22.5}}
        mock_get.return_value = mock_response

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(
                weather_service_module, "CACHE_FILE", os.path.join(tmpdir, "cache.json")
            ):
                data, is_offline = self.service.fetch_weather(41.9, 12.5)
                assert is_offline is False
                assert data is not None
                assert "current" in data
                assert "timestamp" in data
                assert isinstance(data["timestamp"], str)

    @patch("skyview.weather_service.requests.get")
    def test_fetch_timeout_fallback(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = os.path.join(tmpdir, "cache.json")
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(
                    {"cached": True, "timestamp": "2024-01-01T00:00:00"}, f
                )
            with patch.object(weather_service_module, "CACHE_FILE", cache_path):
                data, is_offline = self.service.fetch_weather(41.9, 12.5)
                assert is_offline is True
                assert data == {"cached": True, "timestamp": "2024-01-01T00:00:00"}

    @patch("skyview.weather_service.requests.get")
    def test_fetch_connection_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(
                weather_service_module, "CACHE_FILE", os.path.join(tmpdir, "cache.json")
            ):
                data, is_offline = self.service.fetch_weather(41.9, 12.5)
                assert is_offline is True
                assert data is None

    @patch("skyview.weather_service.requests.get")
    def test_fetch_http_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(
                weather_service_module, "CACHE_FILE", os.path.join(tmpdir, "cache.json")
            ):
                data, is_offline = self.service.fetch_weather(41.9, 12.5)
                assert is_offline is True

    @patch("skyview.weather_service.requests.get")
    def test_fetch_generic_exception(self, mock_get):
        mock_get.side_effect = ValueError("unexpected failure")

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(
                weather_service_module, "CACHE_FILE", os.path.join(tmpdir, "cache.json")
            ):
                data, is_offline = self.service.fetch_weather(41.9, 12.5)
                assert is_offline is True


class TestCacheOperations:
    def test_save_and_load_cache(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(
                weather_service_module, "CACHE_FILE", os.path.join(tmpdir, "cache.json")
            ):
                service = WeatherService()
                test_data = {
                    "key": "value",
                    "timestamp": "2024-01-01T00:00:00",
                }
                service._save_cache(test_data)
                loaded = service._load_cache()
                assert loaded == test_data

    def test_load_missing_cache(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(
                weather_service_module,
                "CACHE_FILE",
                os.path.join(tmpdir, "missing.json"),
            ):
                service = WeatherService()
                assert service._load_cache() is None

    def test_load_corrupted_cache(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "bad.json")
            with open(path, "w", encoding="utf-8") as f:
                f.write("{not json")
            with patch.object(weather_service_module, "CACHE_FILE", path):
                service = WeatherService()
                assert service._load_cache() is None
