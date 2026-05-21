"""
noop — games/snake.py
Snake 게임
"""

import curses
import random
import time
from .base import BaseGame


class SnakeGame(BaseGame):
    name = "Snake"

    @property
    def footer_hint(self):
        if not self.alive:
            return "r 재시작"
        return "방향키 이동"

    TICK = 0.12  # 뱀 이동 간격 (초)

    def __init__(self):
        self.reset()

    def reset(self):
        self._w = 0
        self._h = 0
        self.snake = []  # [(y, x), ...] head first
        self.dir = (0, 1)  # (dy, dx) 초기 방향: 오른쪽
        self.food = None
        self.score = 0
        self.alive = True
        self._last_tick = time.time()
        self._initialized = False

    def _init_board(self, h, w):
        """첫 렌더 시 보드 크기 확정 후 초기화"""
        self._h = h - 2  # 테두리 제외
        self._w = w - 2
        cy, cx = self._h // 2, self._w // 2
        self.snake = [(cy, cx), (cy, cx - 1), (cy, cx - 2)]
        self._place_food()
        self._initialized = True

    def _place_food(self):
        empty = [
            (y, x)
            for y in range(self._h)
            for x in range(self._w)
            if (y, x) not in self.snake
        ]
        self.food = random.choice(empty) if empty else None

    # ── 키 처리 ──────────────────────────────────────────────

    def handle_key(self, key) -> bool:
        # 게임 오버 상태에서 r 누르면 재시작
        if not self.alive:
            if key == ord("r"):
                self.reset()
            return False

        DIR_MAP = {
            curses.KEY_UP: (-1, 0),
            curses.KEY_DOWN: (1, 0),
            curses.KEY_LEFT: (0, -1),
            curses.KEY_RIGHT: (0, 1),
        }
        if key in DIR_MAP:
            dy, dx = DIR_MAP[key]
            # 반대 방향 무시 (뱀이 자기 몸으로 바로 파고드는 것 방지)
            if (dy, dx) != (-self.dir[0], -self.dir[1]):
                self.dir = (dy, dx)
        return False

    # ── 업데이트 ─────────────────────────────────────────────

    def _tick(self):
        if not self.alive:
            return
        now = time.time()
        if now - self._last_tick < self.TICK:
            return
        self._last_tick = now

        hy, hx = self.snake[0]
        dy, dx = self.dir
        ny, nx = hy + dy, hx + dx

        # 벽 충돌
        if not (0 <= ny < self._h and 0 <= nx < self._w):
            self.alive = False
            return

        # 자기 충돌
        if (ny, nx) in self.snake:
            self.alive = False
            return

        self.snake.insert(0, (ny, nx))

        if (ny, nx) == self.food:
            self.score += 1
            self._place_food()
        else:
            self.snake.pop()

    # ── 렌더 ─────────────────────────────────────────────────

    def render(self, stdscr, y, x, h, w):
        if not self._initialized:
            self._init_board(h, w)

        self._tick()

        # 보드 테두리
        for col in range(w):
            stdscr.addch(y, x + col, "─")
            stdscr.addch(y + h - 1, x + col, "─")
        for row in range(h):
            stdscr.addch(y + row, x, "│")
            stdscr.addch(y + row, x + w - 1, "│")
        stdscr.addch(y, x, "┌")
        stdscr.addch(y, x + w - 1, "┐")
        stdscr.addch(y + h - 1, x, "└")
        stdscr.addch(y + h - 1, x + w - 1, "┘")

        # 음식
        if self.food:
            fy, fx = self.food
            try:
                stdscr.addch(y + 1 + fy, x + 1 + fx, "●", curses.A_BOLD)
            except curses.error:
                pass

        # 뱀
        for i, (sy, sx) in enumerate(self.snake):
            ch = "█" if i == 0 else "▓"
            attr = curses.A_BOLD if i == 0 else 0
            try:
                stdscr.addch(y + 1 + sy, x + 1 + sx, ch, attr)
            except curses.error:
                pass

        # 점수
        score_str = f" Score: {self.score} "
        stdscr.addstr(y, x + 2, score_str, curses.A_REVERSE)

        # 게임 오버
        if not self.alive:
            msg1 = f" GAME OVER  Score: {self.score} "
            msg2 = " r 재시작  q 종료 "
            my = y + h // 2
            stdscr.addstr(
                my, x + (w - len(msg1)) // 2, msg1, curses.A_REVERSE | curses.A_BOLD
            )
            stdscr.addstr(my + 1, x + (w - len(msg2)) // 2, msg2, curses.A_REVERSE)

    def get_stats(self) -> dict:
        return {
            "accuracy": 100,
            "count": self.score,
            "elapsed": "N/A",
            "streak": self.score,
        }
