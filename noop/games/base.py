"""
noop — games/base.py
모든 게임이 상속받는 베이스 클래스
"""


class BaseGame:
    name = "게임"
    footer_hint = "Ctrl+Q 종료"

    def handle_key(self, key) -> bool:
        """키 입력 처리. True 반환 시 게임 종료."""
        return False

    def render(self, stdscr, y, x, h, w):
        """게임 콘텐츠를 (y, x) 위치에 (h x w) 크기로 렌더."""
        pass

    def get_stats(self) -> dict:
        """아웃트로용 세션 통계 반환"""
        return {"accuracy": 0, "count": 0, "elapsed": "0분", "streak": 0}
