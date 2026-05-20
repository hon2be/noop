# 프로젝트 지침 — noop

```
 ███╗   ██╗ ██████╗  ██████╗ ██████╗
 ████╗  ██║██╔═══██╗██╔═══██╗██╔══██╗
 ██╔██╗ ██║██║   ██║██║   ██║██████╔╝
 ██║╚██╗██║██║   ██║██║   ██║██╔═══╝
 ██║ ╚████║╚██████╔╝╚██████╔╝██║
 ╚═╝  ╚═══╝ ╚═════╝  ╚═════╝ ╚═╝
          while you wait.
```

터미널 에이전트 유휴 시간에 미니게임 + 학습 콘텐츠를 띄우는 Claude Code 스킬 프로젝트.

> 이름: **noop** — "no operation"의 약어. 아무것도 안 하는 척하지만 실제론 배우고 있다는 아이러니.

---

## PRD 구조

모든 기획/설계 결정은 아래 파일에 기록되어 있다. 새로운 결정이 생기면 해당 파일을 업데이트할 것.

```
PRD/
├── README.md                     인덱스 및 빠른 참조
├── product/
│   ├── 00.overview.md            제품 비전, 목표, 성공 지표
│   └── 01.user-stories.md        유저 스토리
├── design/
│   ├── 00.screen-flow.md         화면 흐름 (인트로/게임/아웃트로)
│   └── 01.interaction.md         키보드 인터랙션 전체 정의
├── content/
│   ├── 00.pack-schema.md         콘텐츠 팩 JSON 스키마
│   ├── 01.quiz-types.md          fill / block / choice / typing 포맷
│   └── 02.contribution-guide.md  콘텐츠 기여 및 광고 포맷 가이드
├── engineering/
│   ├── 00.tech-stack.md          기술 스택 결정 및 근거
│   ├── 01.architecture.md        컴포넌트 다이어그램, 파일 구조
│   ├── 02.rendering.md           터미널 렌더링 원리
│   └── 03.game-engine.md         게임 엔진 구조 및 코드 skeleton
└── distribution/
    └── 00.skill-packaging.md     스킬 패키징, Hooks 연동, 배포 채널
```

---

## 핵심 결정 사항 요약

### 기술 스택
- 런타임: **Python + curses** (표준 라이브러리, 의존성 없음)
- 트리거: **Claude Code Stop hook**
- 배포: **Claude Code 스킬 + Plugin**
- 광고 서버: **Cloudflare Worker**

### 게임 타입
- 퀴즈 계열: `fill` (빈칸채우기) / `block` (블럭이동) / `choice` (선다형)
- 기타: Snake, 타이핑 레이서, (추후) 2048·명령어 퀴즈

### 창 크기
- 목표: 가로 9cm × 세로 6cm
- 터미널 기준: 약 52col × 17row (14pt 모노스페이스)
- 구현: `shutil.get_terminal_size()` 로 감지 후 비율 맞춤

### 전역 단축키
- `h` — 창 접기/펼치기 토글
- `q` — 스킬 종료
- Mac에서 Ctrl+\는 SIGQUIT, Ctrl+Q는 flow control이라 사용 불가

### 콘텐츠 팩 포맷
- `pack.json` (메타데이터) + `content.json` (문제)
- `type`: `quiz` / `typing`
- `subtype` (quiz일 때): `fill` / `block` / `choice`

---

## 작업 규칙

- 구현 시작 전 관련 PRD 파일을 먼저 확인할 것
- 설계 결정이 바뀌면 PRD 해당 파일도 함께 업데이트할 것
- 새로운 게임 타입 추가 시 `content/01.quiz-types.md`와 `engineering/03.game-engine.md` 동시 업데이트
