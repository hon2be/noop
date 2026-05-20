---
name: noop
description: |
  터미널 미니게임(퀴즈/스네이크)을 새 터미널 창에서 실행한다.
  사용자가 "게임 해", "심심해", "noop 실행해" 같은 말을 할 때 사용한다.

  실행 시 Bash 도구로 아래 명령을 실행할 것 (프로젝트 루트 기준 상대경로):
    python3 launch.py

  launch.py가 새 터미널 창을 열고 거기서 게임을 실행한다.
  현재 터미널은 방해받지 않는다.
  이 명령은 즉시 리턴(non-blocking)이므로 Bash 도구로 실행 가능하다.
version: "0.1.0"
author: noop contributors
---

# noop — while you wait.

새 터미널 창에서 게임 실행:

```bash
python3 launch.py
```

## 게임 흐름

```
인트로 → 카테고리 선택 → 문항 수 선택 → 퀴즈 게임 → 결과
```

## 조작키

| 키 | 동작 |
|----|------|
| `← →` | 선택지 이동 |
| `Space / Enter` | 확정 |
| `h` | 창 접기 / 펼치기 |
| `q` | 종료 |
