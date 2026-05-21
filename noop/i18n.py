"""
noop — i18n.py
언어 파일 로드 및 번역 함수 t().

사용:
  from .i18n import t, load_lang, get_lang, LANGUAGES
  t("quiz.correct")            → "  ✓  정답!  "
  t("count_menu.desc", total=10, count=5)  → "총 10문항 중 5문제를 풉니다"
"""

import json
from pathlib import Path

_LANG_DIR = Path(__file__).parent.parent / "lang"
_CONFIG = Path.home() / ".config" / "noop" / "config.json"

# 지원 언어 목록: (code, 표시명)
LANGUAGES = [
    ("ko", "한국어"),
    ("en", "English"),
    ("ja", "日本語"),
    ("ar", "العربية"),
    ("ru", "Русский"),
    ("fr", "Français"),
]

_strings: dict = {}
_lang: str = "ko"


# ── 공개 API ──────────────────────────────────────────────────────


def t(key: str, **kwargs) -> str:
    """키에 해당하는 번역 문자열 반환. 없으면 키 자체 반환."""
    s = _strings.get(key, key)
    return s.format(**kwargs) if kwargs else s


def get_lang() -> str:
    return _lang


def load_lang(code: str):
    """언어 코드로 lang/{code}.json 을 로드하고 config에 저장."""
    global _strings, _lang
    path = _LANG_DIR / f"{code}.json"
    if not path.exists():
        return
    with open(path, encoding="utf-8") as f:
        _strings = json.load(f)
    _lang = code
    _save_config(code)


def load_from_config():
    """config 파일에서 언어를 읽어 로드. 없으면 None 반환(첫 실행)."""
    code = _read_config()
    if code is None:
        return None  # 첫 실행 → 언어 선택 필요
    load_lang(code)
    return code


# ── 내부 ─────────────────────────────────────────────────────────


def _read_config() -> str | None:
    try:
        with open(_CONFIG, encoding="utf-8") as f:
            data = json.load(f)
        code = data.get("lang")
        # 유효한 코드인지 확인
        valid = {c for c, _ in LANGUAGES}
        return code if code in valid else None
    except Exception:
        return None


def _save_config(code: str):
    try:
        _CONFIG.parent.mkdir(parents=True, exist_ok=True)
        existing = {}
        if _CONFIG.exists():
            with open(_CONFIG, encoding="utf-8") as f:
                existing = json.load(f)
        existing["lang"] = code
        with open(_CONFIG, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# 모듈 임포트 시 config가 있으면 자동 로드 (없으면 ko 기본값)
_code = _read_config()
if _code:
    load_lang(_code)
else:
    load_lang("ko")  # 언어 선택 전 기본값
