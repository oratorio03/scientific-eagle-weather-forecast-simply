# SkyView - App Meteo Iper-Locale

SkyView è un'app meteo completa scritta in Python usando Kivy e KivyMD. Fornisce previsioni iper-locali basate sulle coordinate GPS esatte.

## Requisiti di Sistema
- Python 3.9 o superiore

## Istruzioni di Installazione

1. Crea e attiva un ambiente virtuale (opzionale ma consigliato):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Su Linux/Mac
   venv\Scripts\activate     # Su Windows
   ```

2. Installa le dipendenze richieste:
   ```bash
   pip install -r requirements.txt
   garden install mapview
   ```

3. Note per Android (Buildozer):
   Assicurati di includere `kivy_garden.mapview` nei requirements del tuo `buildozer.spec`.
   Esempio: `requirements = python3,kivy,kivymd,plyer,requests,kivy_garden.mapview`

4. Avvia l'applicazione:
   ```bash
   python main.py
   ```

## Caratteristiche Principali
- **Posizione GPS Reale:** Utilizza `plyer` per ottenere le coordinate esatte. Se il GPS non è disponibile, permette l'inserimento manuale.
- **Open-Meteo API:** Nessuna API key richiesta. Recupera le condizioni attuali, le previsioni orarie e settimanali.
- **Reverse Geocoding:** Converte le coordinate in nomi di città usando Nominatim di OpenStreetMap, implementando il caching per rispettare il rate limiting (1 req/sec).
- **Interfaccia Material Design 3:** Utilizza KivyMD per un'interfaccia moderna con temi e icone dinamiche (drawer laterale, navigazione inferiore).
- **Supporto Offline:** Salva i dati localmente in file JSON (`ultima_posizione.json` e `geocode_cache.json`). Se non c'è rete, mostra l'ultima situazione nota con un banner di avviso.
- **Asincrono/Non bloccante:** Utilizza il modulo `threading` e `kivy.clock.Clock` per mantenere l'interfaccia fluida durante i caricamenti di rete.
