"""
noop — renderer.py
터미널 렌더링 유틸리티. curses 래퍼.
"""
import curses
import shutil
import unicodedata


# ── 키 입력 유틸 ─────────────────────────────────────────────────

def get_key(win):
    """
    get_wch() 래퍼. 반환값 정규화:
    - int  : 특수키(KEY_UP 등) 또는 ASCII(0~255) 문자
    - str  : 한글·이모지 등 멀티바이트 와이드 문자 (ord > 255)
    - -1   : 타임아웃 (입력 없음)

    getch() 와 달리 한글처럼 3바이트인 문자도 한 번에 받을 수 있다.
    ASCII 범위(ord ≤ 255)는 기존 코드와의 호환을 위해 int로 반환.
    """
    try:
        raw = win.get_wch()
    except curses.error:
        return -1
    if isinstance(raw, str) and len(raw) == 1:
        cp = ord(raw)
        return cp if cp <= 0xFF else raw   # ASCII → int, 와이드 문자 → str
    if isinstance(raw, int):
        return raw
    return -1


# ── 전각 문자 폭 유틸 ────────────────────────────────────────────

def _cols(text: str) -> int:
    """터미널 실제 출력 폭 계산. 한글/이모지 = 2컬럼."""
    w = 0
    for ch in text:
        eaw = unicodedata.east_asian_width(ch)
        w  += 2 if eaw in ('W', 'F') else 1
    return w


def _clip(text: str, max_cols: int) -> str:
    """text를 max_cols 컬럼 이하로 자름."""
    w = 0
    for i, ch in enumerate(text):
        eaw = unicodedata.east_asian_width(ch)
        w  += 2 if eaw in ('W', 'F') else 1
        if w > max_cols:
            return text[:i]
    return text


# ── 렌더 유틸 ────────────────────────────────────────────────────

def get_game_size():
    """터미널 크기 감지 후 게임 창 크기 반환 (col, row)"""
    cols, rows = shutil.get_terminal_size()
    w = min(52, cols - 4)
    h = min(17, rows - 4)
    return w, h


def draw_box(win, y, x, h, w, title=""):
    """테두리 박스 그리기"""
    top = "─" * (w - 2)
    if title:
        t   = f" {title} "
        top = top[:2] + t + top[2 + len(t):]
    try:
        win.addstr(y,     x, "┌" + top + "┐")
        win.addstr(y+h-1, x, "└" + "─"*(w-2) + "┘")
    except curses.error:
        pass
    for i in range(1, h - 1):
        try:
            win.addstr(y+i, x,     "│")
            win.addstr(y+i, x+w-1, "│")
        except curses.error:
            pass


def draw_text_center(win, y, max_w, text, attr=0):
    """
    전체 화면(max_w) 기준 가운데 정렬.
    한글/이모지 전각 폭 반영으로 정확한 정렬.
    """
    text = _clip(text, max_w)
    x    = max(0, (max_w - _cols(text)) // 2)
    try:
        win.addstr(y, x, text, attr)
    except curses.error:
        pass


def draw_progress_bar(win, y, x, width, pct, label=""):
    """진행바. pct: 0~100"""
    filled = int((width - 2) * pct / 100)
    empty  = (width - 2) - filled
    bar    = "█" * filled + "░" * empty
    suffix = f" {pct:3d}%" + (f"  {label}" if label else "")
    try:
        win.addstr(y, x, f"[{bar}]{suffix}")
    except curses.error:
        pass
