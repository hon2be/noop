"""
noop 새 터미널 창 실행기 — macOS / Linux / Windows 지원
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

DIR = Path(__file__).parent.resolve()
CMD = f"cd '{DIR}' && python3 -m noop"


def launch():
    if sys.platform == "darwin":
        _launch_macos()
    elif sys.platform == "win32":
        _launch_windows()
    else:
        _launch_linux()


_DEVNULL = {"stdin": subprocess.DEVNULL, "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL, "close_fds": True}


def _launch_macos():
    sq = "'"
    script = (
        f'tell application "Terminal"\n'
        f'    do script "cd {sq}{DIR}{sq} && python3 -m noop; exec bash"\n'
        f'    activate\n'
        f'end tell'
    )
    subprocess.Popen(["osascript", "-e", script], **_DEVNULL)


def _launch_windows():
    if shutil.which("wt"):
        subprocess.Popen(
            ["wt", "-d", str(DIR), "python3", "-m", "noop"],
            **_DEVNULL,
        )
    else:
        subprocess.Popen(
            ["cmd", "/k", f"cd /d \"{DIR}\" && python3 -m noop"],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            **{k: v for k, v in _DEVNULL.items() if k != "close_fds"},
        )


def _launch_linux():
    terminals = [
        ["gnome-terminal", "--", "bash", "-c", f"cd '{DIR}' && python3 -m noop; exec bash"],
        ["konsole", "-e", "bash", "-c", f"cd '{DIR}' && python3 -m noop; exec bash"],
        ["xfce4-terminal", "-e", f"bash -c \"cd '{DIR}' && python3 -m noop; exec bash\""],
        ["xterm", "-e", "bash", "-c", f"cd '{DIR}' && python3 -m noop; exec bash"],
    ]
    for cmd in terminals:
        if shutil.which(cmd[0]):
            subprocess.Popen(cmd, **_DEVNULL)
            return
    print("새 창을 열 수 없습니다. 직접 실행하세요:")
    print(f"  cd '{DIR}' && python3 -m noop")


if __name__ == "__main__":
    launch()
