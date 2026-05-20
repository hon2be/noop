"""
noop — intro.py
인트로 / 아웃트로 화면
"""
import curses
import time
from .renderer import draw_text_center, draw_box, draw_progress_bar, get_game_size
from .i18n     import t

LOGO = [
    r" ███╗   ██╗ ██████╗  ██████╗ ██████╗ ",
    r" ████╗  ██║██╔═══██╗██╔═══██╗██╔══██╗",
    r" ██╔██╗ ██║██║   ██║██║   ██║██████╔╝",
    r" ██║╚██╗██║██║   ██║██║   ██║██╔═══╝ ",
    r" ██║ ╚████║╚██████╔╝╚██████╔╝██║     ",
    r" ╚═╝  ╚═══╝ ╚═════╝  ╚═════╝ ╚═╝     ",
]
TAGLINE = "while you wait."

def _loading_stages():
    return [
        (20,  t("loading.packs")),
        (50,  t("loading.shuffle")),
        (80,  t("loading.ads")),
        (100, t("loading.ready")),
    ]


def render_intro(stdscr):
    """인트로 화면. 아무 키나 누르면 게임 시작."""
    curses.curs_set(0)
    stdscr.nodelay(False)
    w, h = get_game_size()
    ox = (curses.COLS - w) // 2  # 가로 오프셋 (중앙 배치)
    oy = (curses.LINES - h) // 2  # 세로 오프셋

    # ── 1단계: 로고 한 줄씩 등장 ──
    stdscr.clear()
    draw_box(stdscr, oy, ox, h, w)
    logo_y = oy + 2
    for i, line in enumerate(LOGO):
        stdscr.addstr(logo_y + i, ox + (w - len(line)) // 2, line, curses.A_BOLD)
        stdscr.refresh()
        time.sleep(0.07)

    draw_text_center(stdscr, logo_y + len(LOGO) + 1, curses.COLS, TAGLINE, curses.A_DIM)
    stdscr.refresh()
    time.sleep(0.4)

    # ── 2단계: 로딩바 ──
    bar_w = w - 8
    bar_y = oy + h - 4
    bar_x = ox + 4

    for pct, label in _loading_stages():
        draw_progress_bar(stdscr, bar_y, bar_x, bar_w, pct, label)
        stdscr.refresh()
        time.sleep(0.3)

    # ── 3단계: 시작 대기 ──
    prompt = t("intro.start")
    draw_text_center(stdscr, bar_y + 2, curses.COLS, prompt, curses.A_BLINK)
    stdscr.refresh()
    stdscr.getch()


def render_outro(stdscr, stats: dict):
    """
    아웃트로 화면. 세션 통계 보여주고 3초 후 종료.
    stats = { accuracy, count, elapsed, streak }
    """
    curses.curs_set(0)
    stdscr.nodelay(False)
    w, h = get_game_size()
    ox = (curses.COLS - w) // 2
    oy = (curses.LINES - h) // 2

    stdscr.clear()
    draw_box(stdscr, oy, ox, h, w)

    lines = [
        (t("outro.title"),                    curses.A_BOLD),
        ("─" * (w // 2),                   curses.A_DIM),
        ("",                               0),
        (t("outro.accuracy", val=stats.get("accuracy", 0)),   0),
        (t("outro.count", val=stats.get("count", 0)),   0),
        (t("outro.elapsed", val=stats.get("elapsed", "N/A")),  0),
        (t("outro.streak", val=stats.get("streak", 0)),    0),
        ("",                               0),
        ("─" * (w // 2),                   curses.A_DIM),
        ("",                               0),
        (t("outro.bye"),   curses.A_BOLD),
    ]

    start_y = oy + (h - len(lines)) // 2
    for i, (text, attr) in enumerate(lines):
        draw_text_center(stdscr, start_y + i, curses.COLS, text, attr)

    # 카운트다운
    for remaining in range(3, 0, -1):
        msg = t("outro.countdown", n=remaining)
        draw_text_center(stdscr, oy + h - 2, curses.COLS, msg, curses.A_DIM)
        stdscr.refresh()
        time.sleep(1)
