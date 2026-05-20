# noop · PRD

> no operation. while you wait.

터미널 에이전트 유휴 시간에 미니게임 + 학습 콘텐츠를 띄우는 Claude Code 스킬

---

## 디렉토리 구조

```
PRD/
├── product/
│   ├── 00.overview.md          제품 비전, 목표, 성공 지표
│   └── 01.user-stories.md      유저 스토리
│
├── design/
│   ├── 00.screen-flow.md       화면 흐름 (인트로/게임/아웃트로 ASCII 스케치 포함)
│   └── 01.interaction.md       키보드 인터랙션 전체 정의
│
├── content/
│   ├── 00.pack-schema.md       콘텐츠 팩 JSON 스키마 (pack.json / content.json)
│   ├── 01.quiz-types.md        fill / block / choice / typing 상세 포맷
│   └── 02.contribution-guide.md 콘텐츠 기여 및 광고 포맷 가이드
│
├── engineering/
│   ├── 00.tech-stack.md        기술 스택 결정 및 근거
│   ├── 01.architecture.md      컴포넌트 다이어그램, 파일 구조
│   ├── 02.rendering.md         터미널 렌더링 원리 (ANSI, curses, 더블버퍼링)
│   └── 03.game-engine.md       게임 엔진 구조 및 코드 skeleton
│
└── distribution/
    └── 00.skill-packaging.md   스킬 패키징, Hooks 연동, 배포 채널
```

---

## 빠른 참조

| 궁금한 것 | 파일 |
|---|---|
| 이 제품이 뭔지 | product/00.overview.md |
| 어떤 키로 뭘 하는지 | design/01.interaction.md |
| JSON을 어떻게 써야 하는지 | content/00.pack-schema.md |
| 퀴즈 타입별 포맷 | content/01.quiz-types.md |
| 터미널 그리기 원리 | engineering/02.rendering.md |
| 배포 방법 | distribution/00.skill-packaging.md |
