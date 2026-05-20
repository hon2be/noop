# noop — while you wait.

```
 ███╗   ██╗ ██████╗  ██████╗ ██████╗
 ████╗  ██║██╔═══██╗██╔═══██╗██╔══██╗
 ██╔██╗ ██║██║   ██║██║   ██║██████╔╝
 ██║╚██╗██║██║   ██║██║   ██║██╔═══╝
 ██║ ╚████║╚██████╔╝╚██████╔╝██║
 ╚═╝  ╚═══╝ ╚═════╝  ╚═════╝ ╚═╝
```

> 에이전트가 일하는 동안, 터미널에서 퀴즈 풀고 배우세요.

**noop**은 Claude Code 같은 AI 에이전트가 작업하는 유휴 시간에 터미널 미니게임과 학습 콘텐츠를 띄워주는 도구입니다. 이름은 "no operation"의 약어 — 아무것도 안 하는 척하지만 실제론 배우고 있다는 아이러니에서 왔습니다.

---

## 실행 방법

```bash
# 새 터미널 창에서 실행 (권장)
python3 launch.py

# 또는 직접 실행
python3 -m noop
```

Python 표준 라이브러리만 사용합니다. **별도 설치 필요 없음.**

---

## 기능

- **퀴즈 게임** — 개발상식, 한국어, 영어, 시사상식, 넌센스 5개 카테고리, 총 100문항
- **Snake 게임** — `NOOP_GAME=snake python3 -m noop`
- **6개 언어 지원** — 한국어, English, 日本語, العربية, Русский, Français
- **광고** — 게임 종료 후 5초 광고 (← 스킵 / → 방문 선택)

---

## Claude Code 스킬로 사용

`.claude/skills/noop/SKILL.md`가 포함되어 있어 Claude Code 스킬로 등록됩니다.

Claude에게 이렇게 요청하세요:

> "noop 실행해줘" 또는 "잠깐 게임 하나 켜줘"

---

## 콘텐츠 팩 구조

```
packs/
├── dev/          # 개발상식
├── korean/       # 한국어·맞춤법
├── english/      # 영어
├── news/         # 시사상식
└── nonsense/     # 넌센스 퀴즈
```

각 팩은 `pack.json` (메타데이터) + `content.json` (문제 목록)으로 구성됩니다.  
콘텐츠 기여 방법은 [`PRD/content/02.contribution-guide.md`](PRD/content/02.contribution-guide.md)를 참고하세요.

---

## 광고 협찬

`ads/ads.json`에 광고를 추가하면 게임 종료 후 노출됩니다.

- 형식: [`PRD/content/02.contribution-guide.md`](PRD/content/02.contribution-guide.md) 참고
- 문의: GitHub Issues 또는 이메일

---

## 키보드 단축키

| 키 | 동작 |
|---|---|
| `← →` | 선택 이동 |
| `Space` / `Enter` | 확인 |
| `h` | 창 접기/펼치기 |
| `q` | 종료 |

---

## 라이선스

MIT
