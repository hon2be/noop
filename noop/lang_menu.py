"""
noop — lang_menu.py
첫 실행 시 언어 선택 화면.
선택 후 i18n.load_lang() + config 저장.
"""

import curses
from .renderer import draw_box, get_game_size, get_key
from .i18n import LANGUAGES, load_lang

KEY_UP = curses.KEY_UP
KEY_DOWN = curses.KEY_DOWN
KEY_ENTER = ord("\n")
KEY_SPACE = ord(" ")
KEY_QUIT = ord("q")


def render_lang_menu(stdscr) -> str | None:
    """
    언어 선택 화면. 선택한 언어 코드를 반환.
    q → None (종료 요청).
    """
    stdscr.keypad(True)
    stdscr.timeout(50)
    curses.curs_set(0)

    cursor = 0
    n = len(LANGUAGES)

    while True:
        stdscr.erase()
        _draw(stdscr, cursor)
        stdscr.refresh()

        key = get_key(stdscr)
        if key == -1 or isinstance(key, str):
            continue

        if key == KEY_QUIT:
            return None
        elif key == KEY_UP:
            cursor = (cursor - 1) % n
        elif key == KEY_DOWN:
            cursor = (cursor + 1) % n
        elif key in (KEY_ENTER, KEY_SPACE):
            code = LANGUAGES[cursor][0]
            load_lang(code)
            return code
        elif ord("1") <= key <= ord("6"):
            idx = key - ord("1")
            if idx < n:
                code = LANGUAGES[idx][0]
                load_lang(code)
                return code


def _draw(stdscr, cursor: int):
    w, h = get_game_size()
    ox = (curses.COLS - w) // 2
    oy = (curses.LINES - h) // 2

    draw_box(stdscr, oy, ox, h, w)

    # 타이틀 — 다국어 병기로 누구나 알아볼 수 있게
    title = "Select Language / 언어 선택 / 言語選択"
    try:
        stdscr.addstr(
            oy + 1, ox + max(0, (w - len(title)) // 2), title[: w - 4], curses.A_BOLD
        )
        stdscr.addstr(oy + 2, ox + 1, "─" * (w - 2), curses.A_DIM)
    except curses.error:
        pass

    # 언어 목록
    menu_top = oy + 3
    for i, (code, name) in enumerate(LANGUAGES):
        row = menu_top + i
        line = f"  {i + 1}.  {name}"
        if i == cursor:
            try:
                stdscr.addstr(
                    row, ox + 1, " " * (w - 2), curses.A_REVERSE | curses.A_BOLD
                )
                stdscr.addstr(row, ox + 2, line, curses.A_REVERSE | curses.A_BOLD)
            except curses.error:
                pass
        else:
            try:
                stdscr.addstr(row, ox + 2, line)
            except curses.error:
                pass

    # 푸터
    footer_y = oy + h - 2
    hint = "↑↓ move   number key   Enter select"
    try:
        stdscr.addstr(footer_y - 1, ox + 1, "─" * (w - 2), curses.A_DIM)
        stdscr.addstr(
            footer_y, ox + max(0, (w - len(hint)) // 2), hint[: w - 4], curses.A_DIM
        )
    except curses.error:
        pass
