# Changelog

Tutte le modifiche significative di questo progetto saranno documentate in questo file.

Il formato è ispirato a [Keep a Changelog](https://keepachangelog.com/it-IT/1.0.0/).

## [1.0.0] - 2026-06-11

### Fixed

- **BUG #3 — Banner offline**: visibilità del banner offline gestita correttamente tramite `opacity` e `height`.
- **BUG #4 — Race condition coordinate**: risolta con `threading.Lock`; le coordinate vengono passate esplicitamente ai thread di fetch anziché accedere a stato condiviso.
- **BUG #5 — Index array previsioni**: aggiunta validazione della lunghezza minima degli array prima dell'iterazione sulle previsioni orarie.
- **BUG CRITICO UI — MDIcon**: sostituito widget `MDIcon` (inesistente in KivyMD) con `MDIconButton`.
- **Gestione errori rete**: `weather_service.py` gestisce ora in modo specifico `Timeout`, `ConnectionError` e HTTP error.
- **Logging robusto GPS/geocoding**: `gps_service.py` gestisce fallback su coordinate default e logga errori Nominatim.

### Added

- Logging su file rotante (`RotatingFileHandler`, 1MB × 3 backup) in `user_data_dir`, compatibile desktop e Android.
- Asset grafici: `icon.png` (512×512) e `presplash.png` (1080×1920) in `skyview/assets/`.
- Test unitari con `pytest`: 50 test per `utils.py` e `weather_service.py`, con rete e filesystem mockati.
- `buildozer.spec` configurato per build Android (API 33, NDK 25b, arch `arm64-v8a`, permessi GPS/Internet, `openssl`).
- Script di esecuzione test: `run_tests.sh` e `run_tests.bat`.
- `requirements-dev.txt` separato per non appesantire l'APK Android.

### Changed

- Restrutturazione repository: `skyview/` è l'unica root del progetto Python.
- Rimossi duplicati (`weather-app/` vs `skyview_fix/`) e progetto Android Kotlin orfano (`PrevisoniMeteo/`).
- Spostati strumenti di manutenzione in `tools/`.
