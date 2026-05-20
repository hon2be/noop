"""
noop — launcher.py
메인 진입점. curses wrapper 에서 호출.
"""
import curses
import os
import signal
import pathlib

signal.signal(signal.SIGQUIT, signal.SIG_IGN)
signal.signal(signal.SIGINT,  signal.SIG_IGN)

from .intro          import render_intro, render_outro
from .game_window    import GameWindow
from .games          import SnakeGame, QuizGame
from .category_menu  import render_category_menu, render_count_menu
from .lang_menu      import render_lang_menu
from .i18n           import load_from_config, t
from .pack_loader    import load_items
from .ad_client      import make_client_from_env
from .ad_renderer    import render_ad

PACKS_DIR = str(pathlib.Path(__file__).parent.parent / "packs")


def main(stdscr):
    curses.start_color()
    curses.use_default_colors()
    curses.curs_set(0)

    ad_client = make_client_from_env()

    # 첫 실행 시 언어 선택
    if load_from_config() is None:
        lang = render_lang_menu(stdscr)
        if lang is None:
            return

    render_intro(stdscr)

    mode = os.environ.get("NOOP_GAME", "quiz")
    if mode == "snake":
        game = SnakeGame()
    else:
        category = render_category_menu(stdscr)
        if category is None:
            return

        items = load_items(category=category, packs_dir=PACKS_DIR)
        if not items:
            items = load_items(category="random", packs_dir=PACKS_DIR)

        # 문항 수 선택 (최대: 실제 문항 수)
        count = render_count_menu(stdscr, max_count=len(items))
        if count is None:
            return

        game = QuizGame(items=items[:count])
        from .category_menu import MENU_ITEMS
        label_map = {key: label for label, key in MENU_ITEMS}
        game.name = f"퀴즈 · {label_map.get(category, category)}"

    window = GameWindow(stdscr, game=game, ad_client=ad_client)
    window.run()

    render_ad(stdscr, ad_client)
    render_outro(stdscr, game.get_stats())
