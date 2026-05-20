"""
noop — ad_client.py

광고 클라이언트. 두 소스를 지원:
  1. SelfAdProvider    — 자체 광고 서버 (Cloudflare Worker)
  2. EthicalAdsProvider — EthicalAds API

우선순위: self → ethicalads → 로컬 캐시 → None
"""

import json
import os
import pathlib
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from typing import Optional

# ── 광고 데이터 모델 ────────────────────────────────────────────

@dataclass
class Ad:
    headline: str        # 짧은 제목
    content: str         # 본문
    cta: str             # Call to action (예: "Try free →")
    link: str            # 클릭 URL
    view_url: str        # 노출 추적 URL (빈 문자열이면 추적 없음)
    source: str          # "self" | "ethicalads"
    ascii_art: list      = field(default_factory=list)
    # 사진 기반 아스키아트 (문자열 라인 배열). 없으면 빈 리스트.

    def to_banner_lines(self, width: int = 46) -> list[str]:
        """터미널 배너용 텍스트 라인 리스트 반환"""
        inner = width - 4  # 테두리 + 패딩
        lines = []

        if self.headline:
            lines.append(self.headline[:inner])

        # content를 inner 폭으로 줄바꿈
        words = self.content.split()
        line = ""
        for word in words:
            if len(line) + len(word) + 1 <= inner:
                line = (line + " " + word).strip()
            else:
                if line:
                    lines.append(line)
                line = word
        if line:
            lines.append(line)

        if self.cta:
            lines.append(self.cta[:inner])

        return lines


# ── 베이스 프로바이더 ────────────────────────────────────────────

class BaseAdProvider:
    name = "base"
    timeout = 3  # 네트워크 요청 타임아웃 (초)

    def fetch(self) -> Optional[Ad]:
        raise NotImplementedError

    def _get(self, url: str, headers: dict = None) -> dict:
        req = urllib.request.Request(url, headers=headers or {})
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read().decode())

    def _post(self, url: str, data: dict, headers: dict = None) -> dict:
        body = json.dumps(data).encode()
        h = {"Content-Type": "application/json", **(headers or {})}
        req = urllib.request.Request(url, data=body, headers=h, method="POST")
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read().decode())


# ── 1. 자체 광고 서버 ────────────────────────────────────────────

_DEFAULT_ADS_FILE = str(pathlib.Path(__file__).parent.parent / "ads" / "ads.json")


class SelfAdProvider(BaseAdProvider):
    """
    자체 Cloudflare Worker 광고 서버 또는 로컬 JSON 파일.

    server_url 이 있으면 → GET /ad?keywords=... 호출
    server_url 이 없으면 → ads/ads.json 에서 랜덤 1개 반환 (로컬 테스트용)

    서버/파일 응답 포맷:
    {
      "headline": "...",
      "content": "...",
      "cta": "...",
      "link": "...",
      "view_url": ""
    }
    """
    name = "self"

    def __init__(self, server_url: str = None, keywords: list[str] = None,
                 ads_file: str = None):
        self.server_url = server_url.rstrip("/") if server_url else None
        self.keywords   = keywords or ["developer", "cli"]
        self.ads_file   = ads_file or _DEFAULT_ADS_FILE

    def fetch(self) -> Optional[Ad]:
        if self.server_url:
            return self._fetch_remote()
        return self._fetch_local()

    def _fetch_remote(self) -> Optional[Ad]:
        try:
            kw  = ",".join(self.keywords)
            url = f"{self.server_url}/ad?keywords={kw}"
            raw = self._get(url)
            return self._parse(raw)
        except Exception:
            return None

    def _fetch_local(self) -> Optional[Ad]:
        """ads/ads.json 에서 랜덤 1개 반환."""
        import random
        try:
            with open(self.ads_file, encoding="utf-8") as f:
                ads = json.load(f)
            if not ads:
                return None
            raw = random.choice(ads)
            return self._parse(raw)
        except Exception:
            return None

    def _parse(self, raw: dict) -> Ad:
        return Ad(
            headline  = raw.get("headline", ""),
            content   = raw.get("content", ""),
            cta       = raw.get("cta", ""),
            link      = raw.get("link", ""),
            view_url  = raw.get("view_url", ""),
            source    = "self",
            ascii_art = raw.get("ascii_art", []),
        )


# ── 2. EthicalAds ────────────────────────────────────────────────

class EthicalAdsProvider(BaseAdProvider):
    """
    EthicalAds API.
    POST https://server.ethicalads.io/api/v1/decision/

    필요한 환경변수:
      ETHICALADS_TOKEN     — API 토큰
      ETHICALADS_PUBLISHER — publisher slug
    """
    name      = "ethicalads"
    API_URL   = "https://server.ethicalads.io/api/v1/decision/"

    def __init__(self, token: str, publisher: str, keywords: list[str] = None):
        self.token     = token
        self.publisher = publisher
        self.keywords  = keywords or ["python", "cli", "developer-tools"]

    def fetch(self) -> Optional[Ad]:
        try:
            headers = {"Authorization": f"Token {self.token}"}
            payload = {
                "publisher": self.publisher,
                "placements": [{
                    "div_id":  "noop-terminal",
                    "ad_type": "text-v1",
                }],
                "keywords":       self.keywords,
                "campaign_types": ["paid"],
            }
            raw  = self._post(self.API_URL, payload, headers)
            copy = raw.get("copy", {})
            return Ad(
                headline = copy.get("headline", ""),
                content  = copy.get("content", raw.get("body", "")),
                cta      = copy.get("cta", ""),
                link     = raw.get("link", ""),
                view_url = raw.get("view_url", ""),
                source   = "ethicalads",
            )
        except Exception:
            return None


# ── AdClient (통합 진입점) ────────────────────────────────────────

CACHE_FILE = os.path.join(os.path.dirname(__file__), ".ad_cache.json")
CACHE_TTL  = 3600  # 1시간 캐시


class AdClient:
    """
    두 프로바이더를 순서대로 시도하고 로컬 캐시로 폴백.

    우선순위: self → ethicalads → 캐시 → None
    """

    def __init__(
        self,
        self_url:       Optional[str] = None,
        ethical_token:  Optional[str] = None,
        ethical_pub:    Optional[str] = None,
        keywords:       list[str] = None,
    ):
        kw = keywords or ["python", "cli", "developer-tools"]
        self.providers: list[BaseAdProvider] = []

        # 서버 URL 없어도 로컬 ads.json 모드로 항상 추가
        self.providers.append(SelfAdProvider(self_url, kw))

        if ethical_token and ethical_pub:
            self.providers.append(EthicalAdsProvider(ethical_token, ethical_pub, kw))

    # ── 퍼블릭 API ───────────────────────────────────────────────

    def get_ad(self) -> Optional[Ad]:
        """광고 1개 반환. 실패 시 캐시, 캐시도 없으면 None."""
        for provider in self.providers:
            ad = provider.fetch()
            if ad:
                self._save_cache(ad)
                self._track_view(ad)
                return ad

        return self._load_cache()

    # ── 노출 추적 ────────────────────────────────────────────────

    def _track_view(self, ad: Ad):
        """view_url 이 있으면 비동기로 노출 카운트"""
        if not ad.view_url:
            return
        try:
            urllib.request.urlopen(ad.view_url, timeout=2)
        except Exception:
            pass

    def track_click(self, ad: Ad):
        """클릭 시 호출. 현재는 로그만, 추후 확장."""
        pass  # 필요시 click tracking URL 추가

    # ── 캐시 ─────────────────────────────────────────────────────

    def _save_cache(self, ad: Ad):
        try:
            data = {
                "ts":       time.time(),
                "headline": ad.headline,
                "content":  ad.content,
                "cta":      ad.cta,
                "link":     ad.link,
                "view_url": "",      # 캐시된 광고는 재추적 안 함
                "source":   ad.source + "_cached",
            }
            with open(CACHE_FILE, "w") as f:
                json.dump(data, f)
        except Exception:
            pass

    def _load_cache(self) -> Optional[Ad]:
        try:
            with open(CACHE_FILE) as f:
                data = json.load(f)
            if time.time() - data["ts"] > CACHE_TTL:
                return None
            return Ad(**{k: v for k, v in data.items() if k != "ts"})
        except Exception:
            return None


# ── 편의 함수: 환경변수에서 자동 설정 ────────────────────────────

def make_client_from_env(keywords: list[str] = None) -> AdClient:
    """
    환경변수에서 설정을 읽어 AdClient 생성.

    NOOP_AD_SERVER_URL     — 자체 광고 서버 URL
    ETHICALADS_TOKEN       — EthicalAds API 토큰
    ETHICALADS_PUBLISHER   — EthicalAds publisher slug
    """
    return AdClient(
        self_url      = os.environ.get("NOOP_AD_SERVER_URL"),
        ethical_token = os.environ.get("ETHICALADS_TOKEN"),
        ethical_pub   = os.environ.get("ETHICALADS_PUBLISHER"),
        keywords      = keywords,
    )
