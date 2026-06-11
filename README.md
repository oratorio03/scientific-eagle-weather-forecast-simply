# SkyView — App Meteo Iper-Locale

Applicazione meteo scritta in **Python** con **KivyMD**. Fornisce previsioni iper-locali basate sulle coordinate GPS esatte, senza necessità di API key.

## Panoramica

SkyView è un'app mobile e desktop che recupera le condizioni meteorologiche attuali, le previsioni orarie delle prossime 24 ore e quelle giornaliere dei prossimi 7 giorni utilizzando le coordinate geografiche dell'utente. Il reverse geocoding converte le coordinate in nome della città, mentre una cache JSON locale garantisce il funzionamento anche offline.

## Caratteristiche principali

- **Posizione GPS reale** tramite `plyer`, con fallback manuale se il GPS non è disponibile.
- **Open-Meteo API** — nessuna API key richiesta.
- **Reverse geocoding** con Nominatim (OpenStreetMap), cache locale e rate limiting.
- **Interfaccia Material Design 3** con navigation drawer e bottom navigation.
- **Supporto offline** con cache JSON locale e banner visivo di avviso.
- **Thread-safe**: fetch di rete in background con `threading.Lock` sulle coordinate.
- **Logging su file rotante** in `user_data_dir` per il debug su dispositivo Android.
- **Test unitari** con `pytest` per garantire stabilità e prevenire regressioni.

## Screenshot

> _Screenshot dell'app da aggiungere in questa sezione._

## Requisiti di sistema

- Python ≥ 3.9
- Windows / Linux / macOS per l'uso desktop
- Linux / macOS per la build Android (Buildozer non è supportato su Windows)

## Installazione e uso desktop

```bash
# 1. Entra nella cartella dell'app
cd skyview

# 2. Crea e attiva un ambiente virtuale (consigliato)
python -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate         # Windows

# 3. Installa le dipendenze
pip install -r requirements.txt

# 4. Avvia l'applicazione
python main.py
```

Se il GPS non è supportato sulla piattaforma desktop, l'app userà le coordinate di default (Roma, Italia) e mostrerà l'input manuale.

## Build Android con Buildozer

Requisiti: Buildozer, Android SDK/NDK, Java 17. L'intero processo viene gestito dal file `buildozer.spec` nella root.

```bash
# 1. Installa le dipendenze di sviluppo (opzionale, per i test)
pip install -r requirements-dev.txt

# 2. Esegui la build debug
cd skyview
buildozer android debug

# 3. Deploy e avvio su dispositivo/emulatore connesso
buildozer android deploy run
```

I permessi Android necessari (`INTERNET`, `ACCESS_FINE_LOCATION`, `ACCESS_COARSE_LOCATION`) sono già configurati in `buildozer.spec`.

## Architettura

```
skyview/
├── main.py              # Entrypoint, gestione app e thread
├── screens.py           # Schermate (Home, Hourly, Daily, Info)
├── ui_components.py     # Widget custom (card, griglia, lista giornaliera)
├── weather_service.py   # Fetch Open-Meteo + cache JSON
├── gps_service.py       # GPS + reverse geocoding Nominatim
├── utils.py             # Helper (WMO codes, formattazione date/ore)
└── config.py            # Costanti e default
```

`main.py` coordina i servizi e le schermate: avvia il GPS, richiede i dati meteo e aggiorna l'UI tramite `kivy.clock.Clock` per mantenere fluida l'interfaccia durante le operazioni di rete.

## Struttura del repository

```
Kimi_Agent_METEO/
├── skyview/                 # Codice sorgente Python/KivyMD
│   ├── assets/              # icon.png e presplash.png
│   ├── main.py
│   ├── screens.py
│   ├── ui_components.py
│   ├── weather_service.py
│   ├── gps_service.py
│   ├── utils.py
│   ├── config.py
│   ├── requirements.txt
│   └── .gitignore
├── tests/                   # Test unitari con pytest
│   ├── conftest.py
│   ├── test_utils.py
│   └── test_weather_service.py
├── tools/                   # Script di manutenzione
│   ├── fix_github.py
│   └── skyview-site/
│       └── index.html
├── buildozer.spec           # Configurazione build Android
├── requirements-dev.txt     # Dipendenze di sviluppo
├── run_tests.sh             # Esecuzione test Linux/macOS
├── run_tests.bat            # Esecuzione test Windows
├── CHANGELOG.md
├── LICENSE
└── README.md
```

## Testing

Installa le dipendenze di sviluppo ed esegui la suite di test:

```bash
pip install -r requirements-dev.txt

# Linux / macOS
./run_tests.sh

# Windows
run_tests.bat
```

Oppure direttamente con pytest:

```bash
python -m pytest tests/ -v
```

La suite include 50 test che coprono `utils.py` e `weather_service.py` con rete e filesystem completamente mockati.

## Bug fix critici applicati

- **BUG #3**: banner offline con toggle visibilità corretto.
- **BUG #4**: race condition risolta con `threading.Lock` e passaggio coordinate ai thread.
- **BUG #5**: validazione lunghezza array previsioni orarie.
- **BUG CRITICO UI**: `MDIcon` sostituito con `MDIconButton`.

Per il dettaglio completo delle modifiche consulta il file `CHANGELOG.md`.

## Licenza

Distribuito sotto licenza MIT. Vedi il file `LICENSE` per i dettagli.
