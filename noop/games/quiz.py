"""
noop — games/quiz.py
퀴즈 게임: block / choice 두 가지 subtype 지원
"""
import curses
import json
import random
import unicodedata
from .base import BaseGame
from ..i18n import t


# ── 상수 ─────────────────────────────────────────────────────────

KEY_LEFT  = curses.KEY_LEFT
KEY_RIGHT = curses.KEY_RIGHT
KEY_ENTER = ord('\n')
KEY_SPACE = ord(' ')


# ── 유틸 ─────────────────────────────────────────────────────────

def _cols(text: str) -> int:
    """
    터미널 실제 출력 폭(컬럼 수) 계산.
    한글·한자·이모지 등 전각 문자 = 2컬럼, 나머지 = 1컬럼.
    """
    w = 0
    for ch in text:
        eaw = unicodedata.east_asian_width(ch)
        w += 2 if eaw in ('W', 'F') else 1
    return w


def _clip(text: str, max_cols: int) -> str:
    """text 를 max_cols 컬럼 이하로 자름."""
    w = 0
    for i, ch in enumerate(text):
        eaw = unicodedata.east_asian_width(ch)
        w  += 2 if eaw in ('W', 'F') else 1
        if w > max_cols:
            return text[:i]
    return text


def _wrap(text: str, width: int) -> list:
    """width 컬럼 기준 줄바꿈. 한글/이모지 폭 고려."""
    if not text:
        return []
    words = text.split()
    lines, line, line_w = [], "", 0
    for word in words:
        word_w = _cols(word)
        if line_w == 0:
            line, line_w = word, word_w
        elif line_w + 1 + word_w <= width:
            line   += " " + word
            line_w += 1 + word_w
        else:
            lines.append(line)
            while word_w > width:
                part  = _clip(word, width)
                lines.append(part)
                word   = word[len(part):]
                word_w = _cols(word)
            line, line_w = word, word_w
    if line:
        lines.append(line)
    return lines


def _addstr(stdscr, y, x, text, attr=0):
    """안전한 addstr. x 음수 방어 + 컬럼 클리핑."""
    if not text:
        return
    try:
        avail = curses.COLS - x - 1
        if avail <= 0:
            return
        stdscr.addstr(y, max(0, x), _clip(text, avail), attr)
    except curses.error:
        pass


def _center(stdscr, y, x, w, text, attr=0):
    """x ~ x+w 구간 안에서 text 를 정확히 가운데 정렬."""
    text = _clip(text, w)
    cx   = x + max(0, (w - _cols(text)) // 2)
    _addstr(stdscr, y, cx, text, attr)


def _render_lines(stdscr, y, x, w, lines, attr=0):
    """줄 목록을 y 부터 순서대로 출력."""
    for i, line in enumerate(lines):
        _addstr(stdscr, y + i, x, line[:w], attr)


# ── 퀴즈 게임 ─────────────────────────────────────────────────────

class QuizGame(BaseGame):
    name = "퀴즈"

    def __init__(self, items: list | None = None, pack_path: str | None = None):
        """
        items: 문제 리스트를 직접 전달 (pack_loader 사용 시)
        pack_path: content.json 경로를 전달 (레거시 호환)
        """
        if items is not None:
            raw = items
        elif pack_path is not None:
            raw = self._load(pack_path)
        else:
            raw = []

        # fill 타입은 지원하지 않으므로 걸러냄
        self.items    = [it for it in raw
                         if (it.get("subtype") or it.get("type")) in ("block", "choice")]
        self.index    = 0
        self.correct  = 0
        self.answered = 0
        self._state   = None
        self._result  = None
        self._load_item()

    def _load(self, pack_path: str) -> list:
        with open(pack_path, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        return data.get("items", [])

    def _load_item(self):
        if self.index >= len(self.items):
            self._state = None
            return
        item = self.items[self.index]
        st   = item.get("subtype") or item.get("type")
        if st == "block":
            self._state = BlockState(item)
        elif st == "choice":
            self._state = ChoiceState(item)
        else:
            self._state = None
        self._result = None

    @property
    def total(self):
        return len(self.items)

    @property
    def footer_hint(self):
        if self._result is not None:
            return t("quiz.next")
        return self._state.hint if self._state else ""

    # ── 키 처리 ─────────────────────────────────────────────────

    def handle_key(self, key) -> bool:
        if self._state is None:
            return False

        if self._result is not None:
            if key in (KEY_ENTER, KEY_SPACE):
                self.index += 1
                self._load_item()
            return False

        submitted = self._state.handle_key(key)
        if submitted:
            correct      = self._state.check()
            self._result = "correct" if correct else "wrong"
            self.answered += 1
            if correct:
                self.correct += 1
        return False

    # ── 렌더 ────────────────────────────────────────────────────

    def render(self, stdscr, y, x, h, w):
        if self._state is None:
            self._render_done(stdscr, y, x, h, w)
            return

        _addstr(stdscr, y, x, f"{self.index + 1}/{self.total}", curses.A_DIM)
        self._state.render(stdscr, y + 2, x, h - 4, w)

        if self._result is not None:
            self._render_result(stdscr, y, x, h, w)

    def _render_result(self, stdscr, y, x, h, w):
        item        = self.items[self.index]
        explanation = item.get("explanation", "")
        is_correct  = self._result == "correct"

        mid_y = y + h // 2 - 2
        for row in range(mid_y, mid_y + 6):
            _addstr(stdscr, row, x, " " * w)

        mark = t("quiz.correct") if is_correct else t("quiz.wrong")
        attr = curses.A_BOLD | curses.A_REVERSE
        _center(stdscr, mid_y,     x, w, mark,           attr)
        _center(stdscr, mid_y + 1, x, w, "─" * (w // 2), curses.A_DIM)

        for i, line in enumerate(_wrap(explanation, w)[:3]):
            _center(stdscr, mid_y + 2 + i, x, w, line, curses.A_DIM)

    def _render_done(self, stdscr, y, x, h, w):
        acc   = self.correct * 100 // self.total if self.total else 0
        lines = [
            (t("quiz.done"),                                          curses.A_BOLD),
            ("",                                                      0),
            (t("quiz.score",    correct=self.correct, total=self.total), 0),
            (t("quiz.accuracy", acc=acc),                             0),
        ]
        sy = y + h // 2 - len(lines) // 2
        for i, (text, attr) in enumerate(lines):
            _center(stdscr, sy + i, x, w, text, attr)

    def get_stats(self) -> dict:
        acc = self.correct * 100 // self.total if self.total else 0
        return {
            "accuracy": acc,
            "count":    self.answered,
            "elapsed":  "N/A",
            "streak":   self.correct,
        }


# ── Block 상태 ───────────────────────────────────────────────────

class BlockState:
    @property
    def hint(self):
        return t("quiz.hint_block")

    def __init__(self, item: dict):
        self.question = item.get("question", "")
        blocks        = list(item["blocks"])
        if item.get("shuffle", False):
            random.shuffle(blocks)
        self.blocks   = blocks
        self.cursor   = 0
        self.selected = None
        self.answer   = item["answer"]

    def handle_key(self, key) -> bool:
        n = len(self.blocks)
        if key == KEY_LEFT:
            if self.selected is not None:
                i = self.selected
                if i > 0:
                    self.blocks[i], self.blocks[i-1] = self.blocks[i-1], self.blocks[i]
                    self.selected -= 1
                    self.cursor   -= 1
            else:
                self.cursor = max(0, self.cursor - 1)
        elif key == KEY_RIGHT:
            if self.selected is not None:
                i = self.selected
                if i < n - 1:
                    self.blocks[i], self.blocks[i+1] = self.blocks[i+1], self.blocks[i]
                    self.selected += 1
                    self.cursor   += 1
            else:
                self.cursor = min(n - 1, self.cursor + 1)
        elif key == KEY_SPACE:
            self.selected = self.cursor if self.selected is None else None
        elif key == KEY_ENTER:
            self.selected = None
            return True
        return False

    def check(self) -> bool:
        return [b["id"] for b in self.blocks] == self.answer

    def render(self, stdscr, y, x, h, w):
        q_lines = _wrap(self.question, w)
        _render_lines(stdscr, y, x, w, q_lines[:2], curses.A_BOLD)
        qh = min(len(q_lines), 2) + 1

        for i, block in enumerate(self.blocks):
            if y + qh + i >= y + h:
                break
            text        = block["text"]
            is_cursor   = i == self.cursor
            is_selected = i == self.selected

            if is_selected:
                prefix = "▶ "
                attr   = curses.A_REVERSE | curses.A_BOLD
            elif is_cursor:
                prefix = "  "
                attr   = curses.A_UNDERLINE
            else:
                prefix = "  "
                attr   = 0

            line = f"{prefix}[ {text} ]"
            _addstr(stdscr, y + qh + i, x, line[:w], attr)


# ── Choice 상태 ──────────────────────────────────────────────────

class ChoiceState:
    @property
    def hint(self):
        return t("quiz.hint_choice")

    def __init__(self, item: dict):
        self.question = item["question"]
        self.options  = item["options"]
        self.answer   = item["answer"]
        self.multi    = item.get("multi", False)
        self.cursor   = 0
        self.selected = set()

    def handle_key(self, key) -> bool:
        n = len(self.options)
        if key == KEY_LEFT:
            self.cursor = max(0, self.cursor - 1)
        elif key == KEY_RIGHT:
            self.cursor = min(n - 1, self.cursor + 1)
        elif key == KEY_SPACE:
            oid = self.options[self.cursor]["id"]
            if oid in self.selected:
                self.selected.discard(oid)
            elif self.multi:
                self.selected.add(oid)
            else:
                self.selected = {oid}
        elif key == KEY_ENTER:
            return True
        return False

    def check(self) -> bool:
        return self.selected == set(self.answer)

    def render(self, stdscr, y, x, h, w):
        q_lines = _wrap(self.question, w)
        _render_lines(stdscr, y, x, w, q_lines[:3], curses.A_BOLD)
        qh = min(len(q_lines), 3) + 1

        if self.multi:
            _addstr(stdscr, y + qh - 1, x, t("quiz.multi_select")[:w], curses.A_DIM)

        for i, opt in enumerate(self.options):
            row = y + qh + i
            if row >= y + h:
                break
            oid  = opt["id"]
            text = opt["text"]

            is_cursor   = i == self.cursor
            is_selected = oid in self.selected

            mark   = "●" if is_selected else "○"
            prefix = "▶" if is_cursor else " "
            line   = f"{prefix} {mark} {text}"

            attr = curses.A_BOLD if is_selected else 0
            if is_cursor:
                attr |= curses.A_UNDERLINE

            _addstr(stdscr, row, x, line[:w], attr)
