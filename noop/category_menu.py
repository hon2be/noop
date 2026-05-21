"""
noop — category_menu.py
퀴즈 카테고리 선택 + 문항 수 선택 TUI.
"""

import curses
from .renderer import draw_box, get_game_size, get_key
from .i18n import t

# (표시명, 내부 카테고리 키) — 표시명은 t()로 동적 생성
_CATEGORY_KEYS = ["random", "korean", "english", "dev", "news", "nonsense"]
MENU_ITEMS = [
    ("랜덤", "random"),
    ("한국어", "korean"),
    ("영어", "english"),
    ("개발상식", "dev"),
    ("시사상식", "news"),
    ("넌센스", "nonsense"),
]


def _menu_items():
    return [(t(f"category.{k}"), k) for k in _CATEGORY_KEYS]


KEY_UP = curses.KEY_UP
KEY_DOWN = curses.KEY_DOWN
KEY_LEFT = curses.KEY_LEFT
KEY_RIGHT = curses.KEY_RIGHT
KEY_ENTER = ord("\n")
KEY_QUIT = ord("q")


def render_count_menu(stdscr, max_count: int) -> int | None:
    """
    문항 수 선택 화면.
    ← / → (또는 ↓ / ↑) 로 1씩 조정, Enter 로 확정.
    q 로 종료 → None 반환.
    max_count 이상은 설정 불가.
    """
    DEFAULT = min(10, max_count)
    count = DEFAULT

    stdscr.keypad(True)
    stdscr.timeout(50)
    curses.curs_set(0)

    while True:
        stdscr.erase()
        _draw_count(stdscr, count, max_count)
        stdscr.refresh()

        key = get_key(stdscr)
        if key == -1 or isinstance(key, str):
            continue

        if key == KEY_QUIT:
            return None
        elif key in (KEY_LEFT, KEY_DOWN):
            count = max(1, count - 1)
        elif key in (KEY_RIGHT, KEY_UP):
            count = min(max_count, count + 1)
        elif key == KEY_ENTER:
            return count
        # 숫자 1~9 직접 입력: 해당 숫자 × 10 또는 단순 값
        elif ord("1") <= key <= ord("9"):
            v = key - ord("0")
            count = min(max_count, v)


def _draw_count(stdscr, count: int, max_count: int):
    w, h = get_game_size()
    ox = (curses.COLS - w) // 2
    oy = (curses.LINES - h) // 2

    draw_box(stdscr, oy, ox, h, w)

    # 타이틀
    title = t("count_menu.title")
    try:
        stdscr.addstr(oy + 1, ox + (w - len(title)) // 2, title, curses.A_BOLD)
        stdscr.addstr(oy + 2, ox + 1, "─" * (w - 2), curses.A_DIM)
    except curses.error:
        pass

    # 카운터 — ← [ 10 ] →
    center_y = oy + h // 2 - 1
    label_l = "  ◀  "
    label_r = "  ▶  "
    num_str = f"  {count:2d}  "
    total_w = len(label_l) + len(num_str) + len(label_r)
    cx = ox + (w - total_w) // 2

    try:
        l_attr = curses.A_DIM if count <= 1 else curses.A_BOLD
        r_attr = curses.A_DIM if count >= max_count else curses.A_BOLD
        stdscr.addstr(center_y, cx, label_l, l_attr)
        stdscr.addstr(
            center_y, cx + len(label_l), num_str, curses.A_REVERSE | curses.A_BOLD
        )
        stdscr.addstr(center_y, cx + len(label_l) + len(num_str), label_r, r_attr)
    except curses.error:
        pass

    # 진행 바 — ████░░░░░░
    bar_w = min(20, w - 8)
    filled = round(bar_w * count / max_count)
    bar_str = "█" * filled + "░" * (bar_w - filled)
    bar_x = ox + (w - bar_w) // 2
    try:
        stdscr.addstr(center_y + 1, bar_x, bar_str, curses.A_DIM)
    except curses.error:
        pass

    # 설명
    desc = t("count_menu.desc", total=max_count, count=count)
    try:
        stdscr.addstr(center_y + 3, ox + (w - len(desc)) // 2, desc)
    except curses.error:
        pass

    # 푸터
    footer_y = oy + h - 2
    try:
        stdscr.addstr(footer_y - 1, ox + 1, "─" * (w - 2), curses.A_DIM)
        hint = t("count_menu.hint")
        stdscr.addstr(footer_y, ox + (w - len(hint)) // 2, hint, curses.A_DIM)
    except curses.error:
        pass


def render_category_menu(stdscr) -> str | None:
    """
    카테고리 선택 화면을 표시하고 선택된 카테고리 키를 반환.
    사용자가 q 를 누르면 None 반환.
    """
    stdscr.keypad(True)
    stdscr.timeout(50)
    curses.curs_set(0)

    items = _menu_items()
    cursor = 0
    n = len(items)

    while True:
        items = _menu_items()
        stdscr.erase()
        _draw(stdscr, cursor, items)
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
        elif key == KEY_ENTER:
            return items[cursor][1]
        elif ord("1") <= key <= ord("6"):
            idx = key - ord("1")
            if idx < n:
                return items[idx][1]


def _draw(stdscr, cursor: int, items=None):
    w, h = get_game_size()
    ox = (curses.COLS - w) // 2
    oy = (curses.LINES - h) // 2

    draw_box(stdscr, oy, ox, h, w)

    if items is None:
        items = _menu_items()
    # 타이틀
    title = t("category_menu.title")
    tx = ox + max(0, (w - len(title)) // 2)
    try:
        stdscr.addstr(oy + 1, tx, title, curses.A_BOLD)
    except curses.error:
        pass

    # 구분선
    try:
        stdscr.addstr(oy + 2, ox + 1, "─" * (w - 2), curses.A_DIM)
    except curses.error:
        pass

    # 메뉴 목록
    menu_top = oy + 3
    for i, (label, _) in enumerate(items):
        row = menu_top + i
        num = str(i + 1)
        line = f"  {num}.  {label}"

        if i == cursor:
            attr = curses.A_REVERSE | curses.A_BOLD
            # 선택 행 전체 하이라이트
            try:
                stdscr.addstr(row, ox + 1, " " * (w - 2), attr)
                stdscr.addstr(row, ox + 2, line, attr)
            except curses.error:
                pass
        else:
            try:
                stdscr.addstr(row, ox + 2, line)
            except curses.error:
                pass

    # 구분선 + 푸터
    footer_y = oy + h - 2
    try:
        stdscr.addstr(footer_y - 1, ox + 1, "─" * (w - 2), curses.A_DIM)
        hint = t("category_menu.hint")
        stdscr.addstr(footer_y, ox + 2, hint[: w - 4], curses.A_DIM)
    except curses.error:
        pass
