# Piano di Finalizzazione — Progetto SkyView

> Data: 2026-06-11
> Stato: Bozza — in attesa di approvazione

---

## 1. Stato di Avanzamento Attuale

### 1.1 App Python/KivyMD (`skyview_fix/` / `weather-app/`)
| Componente | Stato | Note |
|---|---|---|
| `main.py` | ✅ Completo | Navigation drawer, bottom nav, 4 schermate, thread-safe con `Lock` |
| `screens.py` | ✅ Completo | Home, Hourly, Daily, Info. Banner offline, check array length, input manuale |
| `ui_components.py` | ✅ Completo | `MDIconButton` fixato (era `MDIcon`), init order corretto |
| `weather_service.py` | ✅ Completo | Open-Meteo API, cache JSON, gestione errori specifica (Timeout, ConnectionError) |
| `gps_service.py` | ✅ Completo | Plyer GPS, fallback default, Nominatim reverse geocoding con cache e rate-limit |
| `utils.py` | ✅ Completo | Type hints, WMO codes, formattazione date/ore |
| `config.py` | ✅ Completo | Endpoint, default Roma, timing |
| `requirements.txt` | ✅ Completo | kivy, kivymd, plyer, requests |
| `README.md` | ⚠️ Basico | Manca architettura, screenshot, istruzioni build mobile |

**Bug fix già applicati:**
1. **BUG #3** — Banner offline toggle corretto (`opacity` + `height`).
2. **BUG #4** — Race condition risolta con `threading.Lock` e passaggio coordinate ai thread.
3. **BUG #5** — Validazione lunghezza array prima di iterare su previsioni orarie.
4. **BUG CRITICO UI** — `MDIcon` (inesistente) sostituito con `MDIconButton`.

### 1.2 Progetto Android Kotlin (`weather-app/PrevisoniMeteo/`)
| Componente | Stato | Note |
|---|---|---|
| `MainActivity.kt` | ❌ Buggato | Errori sintattici (righe `}` duplicate alla fine) |
| `activity_main.xml` | ❌ Buggato | Tag di chiusura duplicati (righe 86-93) |
| `WeatherApi.kt` | ⚠️ Incompleto | Usa OpenWeatherMap (richiede API key) invece di Open-Meteo |
| Logica app | ⚠️ Incompleta | Solo condizione attuale, niente previsioni orarie/giornaliere |
| Gradle/Manifest | ⚠️ OK strutturalmente | Ma librerie datate (Kotlin 1.6, SDK 33) |

### 1.3 Strumenti di Manutenzione
| Componente | Stato | Note |
|---|---|---|
| `fix_github.py` | ✅ Funzionale | Script CLI per pushare i fix su GitHub (richiede token) |
| `skyview-site/index.html` | ✅ Funzionale | Versione web/UI del fix automatico |

---

## 2. Problematiche & Debito Tecnico

1. **Duplicazione codice**: `skyview_fix/` e `weather-app/` contengono gli stessi file Python. Causa confusione su quale sia la "sorgente della verità".
2. **Progetto Kotlin orfano**: `PrevisoniMeteo` è una bozza incompleta con errori. Se non si intende mantenerlo, va rimosso o isolato.
3. **Mancanza build mobile per Python**: Non c'è `buildozer.spec` per compilare l'app Kivy su Android.
4. **Gitignore insufficiente**: Manca esclusione per cache JSON, `__pycache__`, `.buildozer/`, `bin/`.
5. **Documentazione scarsa**: Nessuna guida architetturale, nessun CHANGELOG, nessuna nota sulle bug fix.
6. **Asset grafici mancanti**: Nessuna icona dell'app, nessuno splash screen.

---

## 3. Piano di Finalizzazione (Roadmap)

### Fase A — Consolidamento Repository (Priorità Alta)
**Obiettivo**: avere una struttura di cartelle pulita e univoca.

- [ ] **A.1** Scegliere la root dell'app Python (proposta: rinominare `skyview_fix/` → `skyview/` e renderla la cartella principale).
- [ ] **A.2** Eliminare `weather-app/` (duplicato) o, in alternativa, mantenerla solo se destinazione diversa.
- [ ] **A.3** Decidere il destino di `PrevisoniMeteo/`:
  - **Opzione 1 (Consigliata)**: rimuoverlo dal branch `main` e spostarlo su un branch `legacy-android-kotlin`.
  - **Opzione 2**: correggerlo e completarlo (richiede refactoring API + fix sintattici).
- [ ] **A.4** Spostare `fix_github.py` e `skyview-site/` in una cartella `tools/` o `scripts/`.
- [ ] **A.5** Aggiornare `.gitignore` con regole complete per Python + Kivy + Buildozer.

### Fase B — Stabilizzazione & Build Mobile (Priorità Alta)
**Obiettivo**: rendere l'app compilabile e installabile su Android.

- [ ] **B.1** Creare `buildozer.spec` configurato per:
  - `package.name = skyview`
  - `package.domain = com.oratorio03`
  - Permessi: `INTERNET`, `ACCESS_FINE_LOCATION`, `ACCESS_COARSE_LOCATION`
  - Requisiti: `kivy>=2.2.0,kivymd>=1.1.1,plyer>=2.1.0,requests>=2.28.0`
- [ ] **B.2** Aggiungere icone app (`icon.png`) e splash screen (`presplash.png`) nella root.
- [ ] **B.3** Verificare che `plyer.gps` funzioni su Android (test con Buildozer debug APK).
- [ ] **B.4** Aggiungere logging su file (`skyview.log`) per debug su dispositivo.

### Fase C — Qualità & Testing (Priorità Media)
**Obiettivo**: ridurre i rischi di regressione.

- [ ] **C.1** Aggiungere test unitari minimi per `utils.py` e `weather_service.py` (usando `pytest`).
- [ ] **C.2** Aggiungere script `run_tests.sh` / `run_tests.bat`.
- [ ] **C.3** Test desktop end-to-end (avvio app, switch schermate, refresh manuale coordinate).

### Fase D — Documentazione & Rilascio (Priorità Media)
**Obiettivo**: rendere il progetto comprensibile e rilasciabile.

- [ ] **D.1** Riscrivere `README.md` con:
  - Descrizione app e screenshot (placeholder)
  - Architettura (diagramma testuale)
  - Istruzioni installazione desktop
  - Istruzioni build Android con Buildozer
  - Elenco bug fix applicati (CHANGELOG incorporato)
- [ ] **D.2** Creare `CHANGELOG.md` con versionamento (v1.0.0 — Final Release).
- [ ] **D.3** Aggiungere `LICENSE` (MIT o altro a scelta).
- [ ] **D.4** Tag Git `v1.0.0` e Release Notes su GitHub.

### Fase E — Miglioramenti Funzionali (Priorità Bassa / Futuro)
**Obiettivo**: feature aggiuntive post-rilascio.

- [ ] **E.1** Tema scuro / toggle Light-Dark.
- [ ] **E.2** Salvataggio preferiti/città cercate manualmente.
- [ ] **E.3** Notifiche push per allerte meteo (richiede servizio background).
- [ ] **E.4** Widget home screen (Android).

---

## 4. Struttura Target Finale

```
Kimi_Agent_METEO/
├── skyview/                    # App Python/KivyMD (unica sorgente)
│   ├── main.py
│   ├── screens.py
│   ├── ui_components.py
│   ├── weather_service.py
│   ├── gps_service.py
│   ├── utils.py
│   ├── config.py
│   ├── requirements.txt
│   └── assets/
│       ├── icon.png
│       └── presplash.png
├── tests/                      # Test unitari
│   ├── test_utils.py
│   └── test_weather_service.py
├── tools/                      # Script di manutenzione
│   ├── fix_github.py
│   └── skyview-site/
│       └── index.html
├── docs/
│   └── ARCHITETTURA.md
├── buildozer.spec
├── README.md
├── CHANGELOG.md
├── LICENSE
├── .gitignore
└── PIANO_FINALIZZAZIONE.md     # Questo file
```

---

## 5. Prossimi Passi Suggeriti

1. **Approva questo piano** (o modifica le priorità).
2. **Decidi il destino di `PrevisoniMeteo`**: mantieni il branch legacy o lo eliminiamo?
3. **Avvio Fase A**: io procedo con la ristrutturazione delle cartelle e la pulizia del repo.
4. **Avvio Fase B**: creazione `buildozer.spec` e asset grafici minimi.

> Se vuoi, posso iniziare subito con la **Fase A** (consolidamento) e poi proseguire con la **Fase B**.
