import json
import os
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.list import MDList, TwoLineListItem, ThreeLineListItem
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivy.properties import StringProperty, ObjectProperty, ListProperty
from kivy.clock import Clock

KV = '''
MDScreen:
    MDBottomNavigation:
        panel_color: app.theme_cls.primary_color
        text_color_active: 1, 1, 1, 1
        text_color_normal: 0.8, 0.8, 0.8, 1

        MDBottomNavigationItem:
            name: 'screen_matches'
            text: 'Partite'
            icon: 'soccer'

            MatchListScreen:

        MDBottomNavigationItem:
            name: 'screen_bets'
            text: 'Mie Scommesse'
            icon: 'ticket'
            on_tab_press: app.update_bets_screen()

            MyBetsScreen:
                id: my_bets_screen

<MatchListScreen>:
    ScrollView:
        MDList:
            id: match_list

<MyBetsScreen>:
    ScrollView:
        MDList:
            id: bets_list
'''

# Mock data for upcoming World Cup matches
MOCK_MATCHES = [
    {"id": 1, "team1": "Italia", "team2": "Brasile", "odds": {"1": 2.50, "X": 3.10, "2": 2.80}, "date": "2026-06-15 18:00"},
    {"id": 2, "team1": "Francia", "team2": "Argentina", "odds": {"1": 2.20, "X": 3.20, "2": 3.10}, "date": "2026-06-16 21:00"},
    {"id": 3, "team1": "Germania", "team2": "Spagna", "odds": {"1": 2.60, "X": 3.00, "2": 2.70}, "date": "2026-06-17 18:00"},
    {"id": 4, "team1": "Inghilterra", "team2": "Portogallo", "odds": {"1": 2.10, "X": 3.30, "2": 3.50}, "date": "2026-06-18 21:00"},
]

class BetManager:
    def __init__(self, storage_file="scommesse.json"):
        self.storage_file = storage_file
        self.bets = self.load_bets()

    def load_bets(self):
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading bets: {e}")
                return []
        return []

    def save_bets(self):
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.bets, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error saving bets: {e}")

    def place_bet(self, match_id, team1, team2, choice, odd, stake):
        bet = {
            "match_id": match_id,
            "match_name": f"{team1} - {team2}",
            "choice": choice,
            "odd": odd,
            "stake": stake,
            "potential_win": round(odd * stake, 2),
            "status": "In attesa" # Pending
        }
        self.bets.append(bet)
        self.save_bets()
        return bet

class MatchItem(ThreeLineListItem):
    match_data = ObjectProperty(None)

    def on_release(self):
        app = MDApp.get_running_app()
        app.show_betting_dialog(self.match_data)

class MatchListScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(lambda dt: self.populate_matches())

    def populate_matches(self):
        match_list = self.ids.match_list
        match_list.clear_widgets()
        for match in MOCK_MATCHES:
            item = MatchItem(
                text=f"{match['team1']} vs {match['team2']}",
                secondary_text=f"Data: {match['date']}",
                tertiary_text=f"Quote: 1: {match['odds']['1']} | X: {match['odds']['X']} | 2: {match['odds']['2']}",
                match_data=match
            )
            match_list.add_widget(item)

class BetItem(ThreeLineListItem):
    pass

class MyBetsScreen(Screen):
    def on_enter(self):
        app = MDApp.get_running_app()
        app.update_bets_screen()

from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.segmentedcontrol import MDSegmentedControl, MDSegmentedControlItem

class BetDialogContent(BoxLayout):
    match_data = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = "12dp"
        self.size_hint_y = None
        self.height = "150dp"

        self.segmented_control = MDSegmentedControl(
            md_bg_color="#e0e0e0",
            segment_color="#4caf50"
        )
        self.item_1 = MDSegmentedControlItem(text="1")
        self.item_x = MDSegmentedControlItem(text="X")
        self.item_2 = MDSegmentedControlItem(text="2")

        self.segmented_control.add_widget(self.item_1)
        self.segmented_control.add_widget(self.item_x)
        self.segmented_control.add_widget(self.item_2)

        self.stake_input = MDTextField(
            hint_text="Importo puntata (€)",
            input_filter="float",
            size_hint_x=1
        )

        self.add_widget(self.segmented_control)
        self.add_widget(self.stake_input)

    def get_selected_choice(self):
        active = self.segmented_control.current_active_segment
        if not active:
            return None

        if isinstance(active, list):
            active_item = active[0] if active else None
        else:
            active_item = active

        if active_item == self.item_1:
            return "1"
        if active_item == self.item_x:
            return "X"
        if active_item == self.item_2:
            return "2"

        if hasattr(active_item, 'text'):
            return active_item.text
        return None

class WorldCupBettingApp(MDApp):
    bet_manager = ObjectProperty(None)
    dialog = None
    current_match_bet = None

    def build(self):
        self.bet_manager = BetManager()
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.theme_style = "Light"
        return Builder.load_string(KV)

    def show_betting_dialog(self, match_data):
        self.current_match_bet = match_data

        if not self.dialog:
            self.dialog = MDDialog(
                title=f"Scommetti su {match_data['team1']} - {match_data['team2']}",
                type="custom",
                content_cls=BetDialogContent(),
                buttons=[
                    MDFlatButton(
                        text="ANNULLA",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                    MDRaisedButton(
                        text="SCOMMETTI",
                        theme_text_color="Custom",
                        text_color="white",
                        on_release=self.place_bet
                    ),
                ],
            )
        else:
            self.dialog.title = f"Scommetti su {match_data['team1']} - {match_data['team2']}"
            self.dialog.content_cls.match_data = match_data

        self.dialog.open()

    def place_bet(self, instance):
        content = self.dialog.content_cls
        choice = content.get_selected_choice()
        stake_text = content.stake_input.text

        if not choice or not stake_text:
            return # Should show a snackbar or error message here

        try:
            stake = float(stake_text)
            if stake <= 0:
                return
        except ValueError:
            return

        odd = self.current_match_bet['odds'][choice]

        self.bet_manager.place_bet(
            self.current_match_bet['id'],
            self.current_match_bet['team1'],
            self.current_match_bet['team2'],
            choice,
            odd,
            stake
        )

        content.stake_input.text = ""
        self.dialog.dismiss()
        self.update_bets_screen()

    def update_bets_screen(self):
        root = self.root
        if not root:
            return

        bets_screen = root.ids.my_bets_screen
        bets_list = bets_screen.ids.bets_list
        bets_list.clear_widgets()

        bets = self.bet_manager.bets
        for bet in reversed(bets):
            item = BetItem(
                text=f"{bet['match_name']} - Esito: {bet['choice']} ({bet['odd']})",
                secondary_text=f"Puntata: €{bet['stake']:.2f} | Potenziale Vincita: €{bet['potential_win']:.2f}",
                tertiary_text=f"Stato: {bet['status']}"
            )
            bets_list.add_widget(item)

if __name__ == '__main__':
    WorldCupBettingApp().run()
