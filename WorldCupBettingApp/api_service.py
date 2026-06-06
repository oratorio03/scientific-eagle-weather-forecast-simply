import requests
import json
from datetime import datetime

class ApiFootballService:
    def __init__(self, api_key):
        self.api_key = api_key
        # Usiamo l'endpoint v3 ufficiale di api-football
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {
            'x-apisports-key': self.api_key
        }

    def get_upcoming_fixtures(self, league_id=1, season=2026):
        """
        Recupera le prossime partite di una lega (es. Mondiale id=1)
        """
        if not self.api_key or self.api_key == "INSERISCI_LA_TUA_API_KEY_QUI":
            return self._get_mock_fixtures()

        url = f"{self.base_url}/fixtures"
        params = {
            "league": league_id,
            "season": season,
            "next": 10 # Prossime 10 partite
        }

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("response", [])
        except Exception as e:
            print(f"Errore nel fetch delle partite: {e}")
            return []

    def get_odds(self, fixture_id, bookmaker_id=1):
        """
        Recupera le quote (1, X, 2) per una specifica partita.
        """
        if not self.api_key or self.api_key == "INSERISCI_LA_TUA_API_KEY_QUI":
            return self._get_mock_odds(fixture_id)

        url = f"{self.base_url}/odds"
        params = {
            "fixture": fixture_id,
            "bookmaker": bookmaker_id
        }

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Estrai le quote Match Winner (id 1)
            response_list = data.get("response", [])
            if response_list:
                bookmakers = response_list[0].get("bookmakers", [])
                if bookmakers:
                    bets = bookmakers[0].get("bets", [])
                    for bet in bets:
                        if bet.get("id") == 1: # Match Winner
                            values = bet.get("values", [])
                            odds = {}
                            for v in values:
                                val = v.get("value")
                                odd = v.get("odd")
                                if val == "Home":
                                    odds["1"] = float(odd)
                                elif val == "Draw":
                                    odds["X"] = float(odd)
                                elif val == "Away":
                                    odds["2"] = float(odd)
                            return odds
            return None
        except Exception as e:
            print(f"Errore nel fetch delle quote per fixture {fixture_id}: {e}")
            return None

    def _get_mock_fixtures(self):
        print("ATTENZIONE: Nessuna API key fornita, uso dati simulati per le partite.")
        return [
            {
                "fixture": {"id": 1001, "date": "2026-06-15T18:00:00+00:00"},
                "teams": {"home": {"name": "Italia"}, "away": {"name": "Brasile"}}
            },
            {
                "fixture": {"id": 1002, "date": "2026-06-16T21:00:00+00:00"},
                "teams": {"home": {"name": "Francia"}, "away": {"name": "Argentina"}}
            },
            {
                "fixture": {"id": 1003, "date": "2026-06-17T18:00:00+00:00"},
                "teams": {"home": {"name": "Germania"}, "away": {"name": "Spagna"}}
            }
        ]

    def _get_mock_odds(self, fixture_id):
        print(f"ATTENZIONE: Nessuna API key fornita, uso quote simulate per fixture {fixture_id}.")
        mocks = {
            1001: {"1": 2.50, "X": 3.10, "2": 2.80},
            1002: {"1": 2.20, "X": 3.20, "2": 3.10},
            1003: {"1": 2.60, "X": 3.00, "2": 2.70}
        }
        return mocks.get(fixture_id, {"1": 2.00, "X": 3.00, "2": 3.50})
