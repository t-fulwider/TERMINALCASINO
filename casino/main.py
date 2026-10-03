import shutil
from typing import Callable

from . import games
from .accounts import Account
from .config import Config
from .types import GameContext
from .utils import cprint, cinput, clear_screen, display_topbar, get_theme

from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, Container, Vertical, VerticalScroll, Grid, Horizontal
from textual.widgets import Footer, Button, Static, Input, Label


ACCOUNT_STARTING_BALANCE = 100

ENTER_OR_QUIT_PROMPT = "[E]nter   [Q]uit: "
INVALID_CHOICE_PROMPT = "\nInvalid input. Please try again.\n"
GAME_CHOICE_PROMPT = "Please choose a game to play: "


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

def term_width() -> int:
    """Safe terminal width fallback."""
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return 80


def prompt_with_refresh(
    render_fn: Callable[[], None],
    prompt: str,
    error_message: str,
    validator: Callable[[str], bool],
    transform: Callable[[str], str] = lambda s: s.strip(),
) -> str:
    """
    Repeatedly render screen, show last error (if any), ask for input and validate.
    On EOF/KeyboardInterrupt return 'q' so caller can decide how to exit.
    """
    last_error = ""
    while True:
        render_fn()
        if last_error:
            cprint(last_error)
        answer = transform(cinput(prompt).strip())
        if validator(answer):
            return answer
        last_error = error_message


'''
def main_menu(ctx: GameContext) -> None:
    """
    Main loop: show welcome, then (if chosen) show game menu, call handler,
    then return to top-level menu. No recursion used.
    """
    account = ctx.account
    while True: # ** need to skip over name input for textual menu somehow (app.run each time) **
        def render_welcome():
            clear_screen()
            display_topbar(account, **CASINO_HEADER_OPTIONS)
            cprint("")  # spacing
        # remove
        action = prompt_with_refresh(
            render_fn = render_welcome,
            prompt = ENTER_OR_QUIT_PROMPT.center(term_width()),
            error_message = INVALID_CHOICE_PROMPT,
            validator = lambda x: x.lower() in {"e", "q"},
            transform = lambda s: s.strip().lower(),
        )
    # remove
        if action == "q":
            clear_screen()
            display_topbar(account, **CASINO_HEADER_OPTIONS)
            cprint("\nGoodbye!\n")
            break  # exit loop -> program ends

        # --- choose game --- CAN REMOVE
        def render_choose_game():
            clear_screen()
            display_topbar(account, **CASINO_HEADER_OPTIONS)
            cprint("")  # spacing
            width = term_width()
            max_length = max(map(len, ALL_GAMES))
            cprint("┌" + "─" * 30 + "┐")
            cprint("│" + " " * 30 + "│")
            for i, name in enumerate(ALL_GAMES, start=1):
                cprint(
                    f"│{('[{}] {}'.format(i, name.title()) + ' ' * (max_length - len(name))).center(30)}│".center(width)
                )
            cprint("│" + " " * 30 + "│")
            cprint("└" + "─" * 30 + "┘")


        # --- don't need ---
        choice = prompt_with_refresh(
            render_fn = render_choose_game,
            prompt = GAME_CHOICE_PROMPT.center(term_width()),
            error_message = INVALID_CHOICE_PROMPT,
            validator = lambda x: x.isdigit() and 1 <= int(x) <= len(ALL_GAMES),
        )

        selected_game = ALL_GAMES[int(choice) - 1]
        global HANDLER
        HANDLER = GAME_HANDLERS.get(selected_game)
        if HANDLER:
            clear_screen()
            HANDLER(ctx)  # returns to loop after game finishes
        else:
            clear_screen()
            display_topbar(account, **CASINO_HEADER_OPTIONS)
            cprint("\nNo such game!\n")

# ***** insert Textual app run *****
def main():
    clear_screen()
    display_topbar(account=None, **CASINO_HEADER_OPTIONS)
    # remove
    name = cinput("Enter your name: ").strip()
    while not name:
        clear_screen()
        display_topbar(account=None, **CASINO_HEADER_OPTIONS)
        cprint("\nInvalid input. Please enter a valid name.\n")
        name = cinput("Enter your name: ").strip()
    
    # theme selection
    #clear_screen()
    #display_topbar(account=None, **CASINO_HEADER_OPTIONS)
    #get_theme()


    account = Account.generate(name, ACCOUNT_STARTING_BALANCE)
    config = Config.default()
    ctx = GameContext(account=account, config=config)
    main_menu(ctx) # dont need
'''

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
        yield CasinoHeader() # add check to see if already logged in, then skip over
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