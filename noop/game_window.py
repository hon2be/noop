"""
noop — game_window.py
GameWindow: 게임 루프, 접기/펼치기, 키 라우팅
"""

import curses
import time
from .renderer import draw_box, draw_text_center, get_game_size, get_key
from .i18n import t

AD_INTERVAL = 10  # 퀴즈 N문제마다 광고 1회
AD_MIN_TOTAL = 5  # 총 문제 수가 이 값 이상일 때만 중간 광고 표시

KEY_TOGGLE = ord("h")  # h — 접기/펼치기 (hide)
KEY_QUIT = ord("q")  # q — 종료
KEY_LEFT = curses.KEY_LEFT
KEY_RIGHT = curses.KEY_RIGHT
KEY_ENTER = ord("\n")
KEY_SPACE = ord(" ")
KEY_TAB = ord("\t")


class GameWindow:
    def __init__(self, stdscr, game=None, ad_client=None):
        self.stdscr = stdscr
        self.game = game
        self.ad_client = ad_client  # None이면 광고 없음

        self.collapsed = False
        self.current = 1
        self.total = 10
        self.game_type = game.name if game else "준비 중"

        self._last_ad_at = 0  # 마지막으로 광고를 표시한 answered 값

    # ── 메인 루프 ──────────────────────────────────────────────

    def run(self):
        self.stdscr.keypad(True)
        self.stdscr.timeout(16)
        curses.curs_set(0)

        while True:
            self._render()
            key = get_key(self.stdscr)

            if isinstance(key, str):
                if not self.collapsed and self.game:
                    self.game.handle_key(key)
            else:
                if key == KEY_QUIT:
                    break
                elif key == KEY_TOGGLE:
                    self.collapsed = not self.collapsed
                elif not self.collapsed and self.game:
                    self.game.handle_key(key)

            # 10문제마다 중간 광고 체크
            if self._should_show_mid_ad():
                self._show_ad()

            time.sleep(0.016)

    # ── 광고 타이밍 체크 ────────────────────────────────────────

    def _should_show_mid_ad(self) -> bool:
        """
        퀴즈 게임이고, 총 문제 수 >= AD_MIN_TOTAL 이며,
        answered 가 AD_INTERVAL 의 배수일 때 한 번만 표시.
        """
        if not self.ad_client:
            return False
        from .games.quiz import QuizGame

        if not isinstance(self.game, QuizGame):
            return False
        answered = self.game.answered
        if answered == 0 or answered == self._last_ad_at:
            return False
        if self.game.total < AD_MIN_TOTAL:
            return False
        if answered % AD_INTERVAL == 0:
            return True
        return False

    def _show_ad(self):
        """광고 표시 후 게임 루프 복귀."""
        from .ad_renderer import render_ad

        self._last_ad_at = self.game.answered
        # timeout을 풀고 광고 렌더러에 넘김
        self.stdscr.timeout(-1)
        render_ad(self.stdscr, self.ad_client)
        # 돌아와서 timeout 복원
        self.stdscr.timeout(16)
        self.stdscr.keypad(True)
        curses.curs_set(0)

    # ── 렌더 ────────────────────────────────────────────────────

    def _render(self):
        self.stdscr.erase()
        if self.collapsed:
            self._render_collapsed()
        else:
            self._render_expanded()
        self.stdscr.refresh()

    def _render_collapsed(self):
        """1줄 상태바"""
        cols = curses.COLS
        bar = (
            f" ▶  {self.game_type}"
            f"  {self.current}/{self.total}"
            f"  │  " + t("game.hint_expand") + "  " + t("game.hint_quit") + " "
        ).ljust(cols)[: cols - 1]
        try:
            self.stdscr.attron(curses.A_REVERSE)
            self.stdscr.addstr(curses.LINES - 1, 0, bar)
            self.stdscr.attroff(curses.A_REVERSE)
        except curses.error:
            pass

    def _render_expanded(self):
        """풀 게임 창"""
        w, h = get_game_size()
        ox = (curses.COLS - w) // 2
        oy = (curses.LINES - h) // 2

        draw_box(self.stdscr, oy, ox, h, w)

        from .games.quiz import QuizGame

        if isinstance(self.game, QuizGame):
            header = f" {self.game.index + 1}/{self.game.total}  [{self.game_type}] "
        else:
            header = f" [{self.game_type}] "
        self.stdscr.addstr(oy + 1, ox + 2, header, curses.A_BOLD)

        content_y = oy + 3
        content_x = ox + 2
        content_h = h - 6
        content_w = w - 4

        if self.game:
            self.game.render(self.stdscr, content_y, content_x, content_h, content_w)
        else:
            draw_text_center(
                self.stdscr,
                content_y + content_h // 2,
                curses.COLS,
                t("game.loading"),
                curses.A_DIM,
            )

        footer = self._footer_hint()
        self.stdscr.addstr(oy + h - 2, ox + 2, footer[: w - 4], curses.A_DIM)

    def _footer_hint(self):
        if self.game:
            return self.game.footer_hint + "  " + t("game.hint_collapse")
        return t("game.hint_collapse")
