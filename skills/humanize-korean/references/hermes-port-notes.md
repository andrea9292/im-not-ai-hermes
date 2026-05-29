# Hermes 포트 노트

## 출처

- 원본 저장소: `epoko77-ai/im-not-ai`
- 원본 라이선스: MIT
- 원본 Claude Code 스킬: `.claude/skills/humanize-korean/`
- 포팅 기준: `upstream/main`의 v2.0.0 계열 commit, `8071726`까지 반영 (2026-05-07)

이 Hermes 포트는 원저자와 기여자의 attribution을 보존한다. taxonomy, quick rules, rewriting playbook, scholarship reference, metrics utility는 원본 프로젝트에서 가져와 Hermes Agent에서 사용할 수 있도록 운영 방식을 조정한 것이다.

## Hermes 포트에서 바꾼 점

원본 프로젝트는 Claude Code의 다음 기능을 전제로 한다.

- `.claude/agents/*.md`
- `.claude/commands/*.md`
- `Agent` 호출
- `TeamCreate` / `TeamDelete`
- `model: opus` 같은 Claude model routing
- repository root 기준 helper script와 test

Hermes는 이 파일과 개념을 그대로 실행 가능한 skill machinery로 취급하지 않는다. 그래서 Hermes 포트는 다음처럼 운영 방식을 조정한다.

- 빠른 경로는 main Hermes agent가 직접 진행한다.
- 기본 규칙 출처는 `references/quick-rules.md`다.
- `references/metrics.py`와 `references/metrics_v2.py`는 선택적 local preprocessor로 둔다.
- `scripts/prepare_monolith_input.py`는 이 skill directory를 기준으로 references를 찾고, 호출자의 현재 작업 디렉터리 아래 `_workspace/`를 만든다.
- 정밀한 탐지, 윤문, 의미 보존 감사, 자연스러움 검토는 Claude Code agent 호출이 아니라 Hermes workflow로 설명한다.
- 개인 문체 matching은 public skill에 넣지 않는다.

## v2.0 포트 구성

- `references/ai-tell-taxonomy.md`: 한국 번역학계 보강을 포함한 전체 v2.0 taxonomy
- `references/quick-rules.md`: v2.0 기준 fast-path S1/S2 규칙
- `references/rewriting-playbook.md`: 카테고리별 윤문 처방
- `references/scholarship.md`: 외부 학술 근거 메모
- `references/metrics.py`: v1.6 KatFish/LREAD-style 정량 지표
- `references/metrics_v2.py`: v2.0 post-editese와 translation-interference 지표
- `references/baseline.json`, `references/baseline_v2.json`: 지표 baseline과 placeholder cell
- `scripts/prepare_monolith_input.py`: 파일 workflow용 metrics prep shim
- `tests/`: metrics module 회귀 테스트

## 공개 배포 경계

이 skill은 범용 한국어 글쓰기 품질 개선 도구로 유지한다. 다음 항목은 추가하지 않는다.

- 특정 개인의 voice profile
- private style-guide rule
- 기관별 house style
- 공개되지 않은 프로젝트 용어
- 한 사용자에게만 의미 있는 writing preference

사용자가 개인 문체 반영을 원하면, 이 skill 위에 별도 local skill, style guide, voice sample을 조합한다.

## 향후 작업

- 한국어 AI 문체 패턴별 sample input/output fixture를 추가한다.
- public `andrea9292/im-not-ai-hermes` tap source에 맞춰 설치 안내를 계속 최신 상태로 유지한다.
- strict-mode helper prompt를 Hermes `delegate_task` 기반으로 실험할 수 있지만, fast mode를 기본으로 유지한다.
- upstream sync가 바뀔 때 `README.md`, `SOURCE.md`, `RELEASE_NOTES.md`, `MAINTAINING.md`를 함께 갱신한다.
