#!/usr/bin/env bash
# noop 실행 래퍼 — SKILL.md Stop hook에서 호출됨
# BASH_SOURCE[0] 으로 이 스크립트 위치(= 프로젝트 루트)를 찾아서 cd
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR" && exec python3 -m noop
