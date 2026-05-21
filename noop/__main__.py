"""
python -m noop 진입점.

Claude Code Stop hook에서 실행될 때:
  - stdin이 JSON 파이프 상태 (isatty=False)
  - /dev/tty를 직접 열어 curses에 연결해야 정상 동작
"""

import curses
import os
import sys

from .launcher import main


def run():
    # Stop hook 실행 환경: stdin이 파이프일 수 있음.
    # curses(ncurses)는 stdin/stdout이 tty여야 동작하므로
    # /dev/tty를 fd 0, 1 로 리디렉션.
    _tty_fd = None
    if not sys.stdin.isatty() and os.path.exists("/dev/tty"):
        try:
            _tty_fd = os.open("/dev/tty", os.O_RDWR)
            os.dup2(_tty_fd, 0)  # stdin  → /dev/tty
            os.dup2(_tty_fd, 1)  # stdout → /dev/tty
        except OSError:
            # /dev/tty 열 수 없으면 (CI, headless 등) 조용히 종료
            return

    try:
        curses.wrapper(main)
    except (KeyboardInterrupt, curses.error):
        pass
    finally:
        if _tty_fd is not None:
            try:
                os.close(_tty_fd)
            except OSError:
                pass


if __name__ == "__main__":
    run()
