"""
noop — pack_loader.py
팩 디렉토리를 스캔하여 카테고리별 문제 목록을 반환.
"""

import json
import os
import pathlib
import random

# 카테고리 매핑 (표시명 → 내부 키)
CATEGORIES = {
    "random": "랜덤",
    "korean": "한국어",
    "english": "영어",
    "dev": "개발상식",
    "news": "시사상식",
    "nonsense": "넌센스",
}

# packs/ 디렉토리 기본 경로 (이 파일 기준 ../packs)
_DEFAULT_PACKS_DIR = str(pathlib.Path(__file__).parent.parent / "packs")


def discover_packs(packs_dir: str = _DEFAULT_PACKS_DIR) -> list[dict]:
    """
    packs/ 하위 모든 디렉토리를 탐색해 pack.json 정보를 반환.
    반환값: [{"meta": {...}, "content_path": "..."}]
    """
    result = []
    if not os.path.isdir(packs_dir):
        return result

    for entry in sorted(os.listdir(packs_dir)):
        pack_dir = os.path.join(packs_dir, entry)
        pack_json = os.path.join(pack_dir, "pack.json")
        content = os.path.join(pack_dir, "content.json")

        if not (
            os.path.isdir(pack_dir)
            and os.path.isfile(pack_json)
            and os.path.isfile(content)
        ):
            continue

        try:
            with open(pack_json, encoding="utf-8") as f:
                meta = json.load(f)
            result.append({"meta": meta, "content_path": content})
        except (json.JSONDecodeError, OSError):
            pass

    return result


def load_items(
    category: str = "random", packs_dir: str = _DEFAULT_PACKS_DIR, shuffle: bool = True
) -> list[dict]:
    """
    카테고리에 해당하는 모든 팩을 로드해 문제 리스트를 합쳐 반환.
    category: "random" | "korean" | "english" | "dev" | "news" | "nonsense"
    """
    packs = discover_packs(packs_dir)
    items = []

    for pack in packs:
        meta = pack["meta"]
        # "quiz" 게임이 포함된 팩만
        if "quiz" not in meta.get("games", []):
            continue
        # 카테고리 필터
        if category != "random":
            if meta.get("category", "") != category:
                continue
        # content.json 로드
        try:
            with open(pack["content_path"], encoding="utf-8") as f:
                data = json.load(f)
            # content.json이 리스트 or {"items": [...]} 두 형태 모두 지원
            if isinstance(data, list):
                items.extend(data)
            elif isinstance(data, dict) and "items" in data:
                items.extend(data["items"])
        except (json.JSONDecodeError, OSError):
            pass

    if shuffle:
        random.shuffle(items)

    return items
