import shutil
from typing import Callable

from . import games
from .accounts import Account
from .config import Config
from .types import GameContext

from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, Container, Vertical, VerticalScroll, Grid, Horizontal
from textual.widgets import Footer, Button, Static, Input, Label

ACCOUNT_STARTING_BALANCE = 100


ACTIVE = True
USER_NAME = None
CONFIG = None
CTX = None
ACCOUNT = None
SELECTED_GAME = None

# To add a new game, just add a handler function to GAME_HANDLERS

GAME_HANDLERS: dict[str, Callable[[GameContext], None]] = {
    "bjUS": games.blackjack.play_blackjack,
    "bjEU": games.blackjack.play_european_blackjack,
    "slots": games.slots.play_slots,
    "poker": games.poker.play_poker,
    "roulette": games.roulette.play_roulette,
    "uno": games.uno.play_uno,
    "eurorou": games.roulette.play_european_roulette,
}
ALL_GAMES = list(GAME_HANDLERS.keys())


class AllGames(Grid):

    def compose(self) -> ComposeResult:
        yield Button(label="Blackjack (U.S.)", classes="button", id="bjUS")
        yield Button(label="Blackjack (E.U.)", classes="button", id="bjEU")
        yield Button(label="Slots", classes="button", id="slots")
        yield Button(label="Poker", classes="button", id="poker")
        yield Button(label="Roulette", classes="button", id="roulette")
        yield Button(label="European Roulette", classes="button", id="eurorou")
        yield Button(label="Uno", classes="button", id="uno")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        global SELECTED_GAME
        SELECTED_GAME = str(event.button.id)
        self.app.exit()


class Messages(Horizontal):

    def compose(self) -> ComposeResult:
        global ACCOUNT, USER_NAME
        yield Label(("Welcome, " + USER_NAME), id='input')
        yield Label("Cash: " + str(ACCOUNT.balance), id='cash')


class CasinoHeader(HorizontalGroup):

    def compose(self) -> ComposeResult:
        yield Static("♦ TERMINAL CASINO ♦", id="header")


class CasinoApp(App):
    CSS_PATH = "assets/styles.tcss"
    BINDINGS = [
        ("q", "quit", "Quit")
    ]

    def compose(self) -> ComposeResult:
        yield Footer()
        yield CasinoHeader()  # add check to see if already logged in, then skip over
        global USER_NAME
        if not USER_NAME:
            yield Input(placeholder="Enter your name:")
        else:
            yield Messages()
            yield VerticalScroll(AllGames(id="games"), id="games-container")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        global USER_NAME, ACCOUNT_STARTING_BALANCE, ACCOUNT, CONFIG, CTX
        USER_NAME = event.value.strip()
        if USER_NAME:
            ACCOUNT = Account.generate(USER_NAME, ACCOUNT_STARTING_BALANCE)
            self.mount(Messages())
            event.input.remove()
            self.mount(VerticalScroll(AllGames(id="games"), id="games-container"))
            CONFIG = Config.default()
            CTX = GameContext(account=ACCOUNT, config=CONFIG)

    def action_quit(self) -> None:
        global ACTIVE
        ACTIVE = False
        self.app.exit()


def main() -> None:
    global SELECTED_GAME

    while ACTIVE:
        app = CasinoApp()
        app.run()

        if SELECTED_GAME:
            handler = GAME_HANDLERS.get(SELECTED_GAME)

            if handler:
                handler(CTX)

            SELECTED_GAME = None


if __name__ == "__main__":
    main()