"""
noop — ad_renderer.py
광고 배너 렌더링.

흐름:
  1. 광고 박스 표시
  2. 3초 카운트다운 + ← / → 로 [스킵] / [방문] 선택
  3. Space / Enter → 선택 확정
     q             → 종료 요청
  4. 3초 지나면 [스킵] 선택과 동일하게 자동 넘어감

아스키아트 영역 고정 규격:
  ART_H = 7   줄 (초과 줄은 무시, 미달 줄은 빈 줄로 패딩)
  ART_W = 42  시각 컬럼 (전각·한글 = 2컬럼, 초과 문자는 잘림)
"""

import curses
import subprocess
import sys
import unicodedata
from .ad_client import Ad, AdClient
from .renderer import get_key
from .i18n import t

KEY_LEFT = curses.KEY_LEFT
KEY_RIGHT = curses.KEY_RIGHT
KEY_ENTER = ord("\n")
KEY_SPACE = ord(" ")
KEY_QUIT = ord("q")

_SKIP = 0
_VISIT = 1

# ── 아트 영역 고정 규격 ────────────────────────────────────────────
ART_H = 7  # 아스키아트 고정 줄 수
ART_W = 42  # 아스키아트 최대 시각 너비 (컬럼)

# ── 박스 높이 상수 ─────────────────────────────────────────────────
# 아트 있음: AD라벨(1) + 상단테두리(1) + 아트(ART_H) + 구분선(1) + 텍스트(4) + 하단테두리(1)
_BOX_H_ART = 1 + ART_H + 1 + 4 + 1  # = 14
# 아트 없음: AD라벨(1) + 상단테두리(1) + 텍스트(4) + 하단테두리(1)
_BOX_H_TEXT = 1 + 4 + 1  # = 7


# ── 유틸 ──────────────────────────────────────────────────────────


def _vis_len(s: str) -> int:
    """터미널 시각적 너비 (한글·전각문자 = 2컬럼)"""
    w = 0
    for ch in s:
        ea = unicodedata.east_asian_width(ch)
        w += 2 if ea in ("W", "F") else 1
    return w


def _clip_to_vis(s: str, max_w: int) -> str:
    """시각적 너비 max_w 이하로 잘라냄"""
    w = 0
    for i, ch in enumerate(s):
        cw = 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
        if w + cw > max_w:
            return s[:i]
        w += cw
    return s


# ── 공개 API ──────────────────────────────────────────────────────


def render_ad(stdscr, ad_client: AdClient) -> bool:
    """
    광고 표시. 반환값: True(정상 진행) / False(q → 종료 요청)
    """
    ad = ad_client.get_ad()
    if not ad:
        return True

    cursor = _SKIP
    has_art = bool(ad.ascii_art)
    box_h = _BOX_H_ART if has_art else _BOX_H_TEXT
    # box_h 는 "AD 라벨 행 포함" 높이 (oy 기준 box_h 번째 행이 하단 테두리)

    for remaining_ms in range(50, -1, -1):
        stdscr.erase()
        rows, cols = stdscr.getmaxyx()
        w = min(50, cols - 4)
        ox = (cols - w) // 2

        # 전체 필요 줄: box_h + 빈줄(1) + 버튼(1) + 힌트(1) + 카운트다운(1)
        total_h = box_h + 4
        oy = max(0, (rows - total_h) // 2)

        _draw_ad_box(stdscr, ad, oy, ox, w, has_art, box_h)
        _draw_choices(stdscr, oy, ox, w, cursor, box_h)
        _draw_countdown(stdscr, oy, ox, w, remaining_ms / 10, box_h)
        stdscr.refresh()

        stdscr.timeout(100)
        key = get_key(stdscr)

        if key == KEY_QUIT:
            return False
        if key == KEY_LEFT:
            cursor = _SKIP
        elif key == KEY_RIGHT:
            cursor = _VISIT
        elif key in (KEY_ENTER, KEY_SPACE):
            if cursor == _VISIT:
                _open_browser(ad.link)
                ad_client.track_click(ad)
            return True

    return True


# ── 내부 렌더 함수 ────────────────────────────────────────────────


def _draw_ad_box(stdscr, ad: Ad, oy: int, ox: int, w: int, has_art: bool, box_h: int):
    """
    광고 박스 전체.

    레이아웃 (has_art=True):
      oy+0  [AD]
      oy+1  ┌──────────────────────────┐
      oy+2  │  < 아트 영역 ART_H줄 >  │
      ...
      oy+1+ART_H  ┄┄┄┄┄ (구분선)
      oy+2+ART_H  │  headline
      oy+3+ART_H  │  content
      oy+4+ART_H  │  content(계속)
      oy+5+ART_H  │  domain
      oy+6+ART_H  └──────────────────────────┘  via source

    레이아웃 (has_art=False):
      oy+0  [AD]
      oy+1  ┌──┐
      oy+2  │ headline
      oy+3  │ content
      oy+4  │ content
      oy+5  │ domain
      oy+6  └──┘
    """
    inner = w - 4  # 좌우 테두리(│) + 패딩(각 1) = 4

    # AD 라벨
    try:
        stdscr.addstr(oy, ox + 2, " AD ", curses.A_REVERSE | curses.A_DIM)
    except curses.error:
        pass

    # 테두리
    top_line = "─" * (w - 2)
    try:
        stdscr.addstr(oy + 1, ox, "┌" + top_line + "┐")
        stdscr.addstr(oy + box_h, ox, "└" + top_line + "┘")
    except curses.error:
        pass
    for i in range(2, box_h):
        try:
            stdscr.addstr(oy + i, ox, "│")
            stdscr.addstr(oy + i, ox + w - 1, "│")
        except curses.error:
            pass

    # ── 아트 영역 ─────────────────────────────────────────────────
    if has_art:
        art = ad.ascii_art or []
        art_w = min(ART_W, inner)  # 실제 사용 가능한 아트 너비

        for row_i in range(ART_H):
            if row_i < len(art):
                line = _clip_to_vis(art[row_i], art_w)
                vw = _vis_len(line)
                # 아트를 아트 영역 안에서 가운데 정렬
                pad = max(0, (art_w - vw) // 2)
                ax = ox + 2 + pad
            else:
                line = ""
                ax = ox + 2

            try:
                stdscr.addstr(oy + 2 + row_i, ax, line)
            except curses.error:
                pass

        # 구분선
        sep_y = oy + 2 + ART_H
        try:
            stdscr.addstr(sep_y, ox + 1, "┄" * (w - 2), curses.A_DIM)
        except curses.error:
            pass
        text_y = sep_y + 1

    else:
        text_y = oy + 2

    # ── 광고 텍스트 ────────────────────────────────────────────────
    lines = ad.to_banner_lines(w)
    for i, line in enumerate(lines[:3]):
        attr = curses.A_BOLD if i == 0 else 0
        try:
            stdscr.addstr(text_y + i, ox + 2, _clip_to_vis(line, inner), attr)
        except curses.error:
            pass

    # 링크 도메인
    domain = _extract_domain(ad.link)
    if domain:
        try:
            stdscr.addstr(
                text_y + 3,
                ox + 2,
                _clip_to_vis(domain, inner),
                curses.A_DIM | curses.A_UNDERLINE,
            )
        except curses.error:
            pass

    # 출처 (하단 테두리 위에 겹쳐 표시)
    src = f" via {ad.source} "
    try:
        stdscr.addstr(oy + box_h, ox + w - len(src) - 1, src, curses.A_DIM)
    except curses.error:
        pass


def _draw_choices(stdscr, oy: int, ox: int, w: int, cursor: int, box_h: int):
    """
    [ ← 스킵 ]   [ 방문 → ]
    박스 하단 테두리 바로 아래 배치.
    """
    skip_label = t("ad.skip")
    visit_label = t("ad.visit")

    skip_attr = curses.A_REVERSE | curses.A_BOLD if cursor == _SKIP else curses.A_DIM
    visit_attr = curses.A_REVERSE | curses.A_BOLD if cursor == _VISIT else curses.A_DIM

    gap = 4
    total_w = _vis_len(skip_label) + gap + _vis_len(visit_label)
    bx = ox + max(0, (w - total_w) // 2)
    row = oy + box_h + 1  # 하단 테두리 아래 한 줄

    try:
        stdscr.addstr(row, bx, skip_label, skip_attr)
        stdscr.addstr(row, bx + _vis_len(skip_label) + gap, visit_label, visit_attr)
    except curses.error:
        pass

    hint = t("ad.hint")
    hint_x = ox + max(0, (w - _vis_len(hint)) // 2)
    try:
        stdscr.addstr(row + 1, hint_x, hint, curses.A_DIM)
    except curses.error:
        pass


def _draw_countdown(stdscr, oy: int, ox: int, w: int, sec: float, box_h: int):
    """자동 스킵 카운트다운 — 버튼 아래 두 줄"""
    text = t("ad.countdown", sec=f"{sec:.1f}")
    row = oy + box_h + 3
    try:
        stdscr.addstr(row, ox + max(0, (w - _vis_len(text)) // 2), text, curses.A_DIM)
    except curses.error:
        pass


def _open_browser(url: str):
    """OS에 맞게 브라우저 열기"""
    if not url:
        return
    try:
        if sys.platform == "darwin":
            subprocess.Popen(["open", url])
        elif sys.platform.startswith("linux"):
            subprocess.Popen(["xdg-open", url])
        elif sys.platform == "win32":
            subprocess.Popen(["start", url], shell=True)
    except Exception:
        pass


def _extract_domain(url: str) -> str:
    """https://vercel.com/... → vercel.com"""
    try:
        return url.split("//")[1].split("/")[0]
    except Exception:
        return ""
