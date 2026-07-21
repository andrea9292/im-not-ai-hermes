# 출처 동기화 기록

이 문서는 `im-not-ai-hermes`가 기준으로 삼은 원본과 Hermes 포트에서 바꾼 점을 기록합니다.

## 원본 기준

| 항목 | 내용 |
|---|---|
| Original repository | https://github.com/epoko77-ai/im-not-ai |
| Original license | MIT |
| Original release | `v2.2.0` |
| Upstream commit used for this port | `3120cb81e3b9910ba393cd8289864c583f0ac50a` |
| Hermes port version | `2.2.0-hermes.1` |
| Sync date | `2026-07-21` |
| Hermes repository | https://github.com/andrea9292/im-not-ai-hermes |

원본 v2.2.0은 v2.0의 한국 번역학계 기반 taxonomy와 post-editese 지표를 유지하면서, 결정적 변경률 게이트, taxonomy 기반 quick-rules 생성, 손실 없는 장문 청킹, 골든 회귀 테스트, `route_hint` 기반 3경로를 추가했습니다.

## 파일 매핑

| 원본 또는 개념 | Hermes 포트 |
|---|---|
| `.claude/skills/humanize-korean/SKILL.md`의 규칙·경로 정책 | `skills/humanize-korean/SKILL.md`의 Hermes-native workflow |
| `.claude/skills/humanize-korean/references/*.md` | `skills/humanize-korean/references/*.md` |
| `.claude/skills/humanize-korean/references/*.json` | `skills/humanize-korean/references/*.json` |
| `.claude/skills/humanize-korean/references/*.py` | `skills/humanize-korean/references/*.py` |
| `scripts/prepare_monolith_input.py` | `skills/humanize-korean/scripts/prepare_monolith_input.py` |
| `scripts/build_quick_rules.py` | `skills/humanize-korean/scripts/build_quick_rules.py` |
| `scripts/reassemble_chunks.py` | `skills/humanize-korean/scripts/reassemble_chunks.py` |
| `scripts/verify_change_rate.py` | `skills/humanize-korean/scripts/verify_change_rate.py` |
| 결정적·골든·청킹·route 테스트 | `skills/humanize-korean/tests/` |
| `.github/workflows/test.yml`의 검증 의도 | `.github/workflows/test.yml`의 Hermes 패키지 경로 |
| `LICENSE` | `LICENSE` |
| 원본 출처 고지 | `NOTICE.md`, `README.md`, 이 문서 |

## Hermes 포트에서 바꾼 점

이 포트는 원본의 글쓰기 규칙과 검증 코드를 보존하되, 운영 방식을 Hermes Agent에 맞게 조정합니다.

- Claude Code의 `.claude/agents/*.md`를 Hermes runtime agent로 등록하지 않습니다.
- Claude Code의 `Agent`, `TeamCreate`, `TeamDelete`, `model: opus` 라우팅을 사용하지 않습니다.
- Claude Code slash command인 `/humanize`, `/humanize-redo`를 제공하지 않습니다.
- Hermes main agent가 `light`, `standard`, `heavy` 경로를 직접 수행합니다.
- 정밀 검토가 필요할 때만 선택적으로 `delegate_task`를 사용하며, 최종 판단과 파일 검증은 부모 agent가 맡습니다.
- helper script는 저장소 루트의 `.claude` 경로가 아니라 설치된 skill package의 `references/`를 찾습니다.
- repository 구조는 Hermes tap discovery를 위해 `skills/humanize-korean/`를 사용합니다.
- raw `SKILL.md` URL 설치보다 `hermes skills tap add`와 `hermes skills install`을 우선합니다.
- 개인 문체, 기관별 house style, 비공개 프로젝트 어휘는 public skill에 넣지 않습니다.

## 반영한 v2.2 계열 내용

- 전체 taxonomy와 taxonomy-to-quick-rules 생성 계약
- B-2 전문용어 보존, C-1 심각도·학술구조 예외, C-8 부정-긍정 대구 보강
- scholarship의 이론적 종합과 후속 근거
- `metrics_v2.py`의 sibling import·baseline 경로 수정
- `route_hint`: `light`, `standard`, `heavy`
- 30% 경고·50% 중단의 결정적 변경률 게이트
- 헤딩 승격, 각주 passthrough, source hash를 포함한 손실 없는 청킹·재조립
- register, 구조, 각주, 직접 인용 보존을 점검하는 골든 회귀 테스트
- GitHub Actions에서 Python 3.11·3.12 회귀 테스트와 quick-rules 동기화 검사

A-17은 upstream v2.2에서도 hold 상태입니다. 지표·학술 참고로만 유지하며 기본 윤문 트리거로 사용하지 않습니다.

## 제외하거나 바꾼 것

- Claude·Codex·Gemini용 plugin manifest, command, installer는 포함하지 않습니다.
- 원본 role agent prompt를 Hermes runtime에 복제하지 않습니다.
- 원본의 고정 agent 호출 수와 모델 힌트는 Hermes 실행 요구사항으로 옮기지 않습니다.
- web service 구현은 포함하지 않습니다. `web-service-spec.md`는 참고 문서로만 유지합니다.
- 원본의 live Claude CLI 테스트는 포함하지 않습니다. 공개 CI는 결정적·stdlib 기반 테스트만 실행합니다.

## 동기화 시 점검 항목

1. upstream release tag와 commit을 기록합니다.
2. taxonomy, quick rules, playbook, scholarship, metrics, baseline 변경 여부를 확인합니다.
3. Hermes 경로에 맞게 script import와 file path를 조정합니다.
4. `python3 -m pytest skills/humanize-korean/tests -q`를 실행합니다.
5. `python3 skills/humanize-korean/scripts/build_quick_rules.py --check`를 실행합니다.
6. 임시 `HERMES_HOME`에 패키지를 설치해 파일 누락 여부를 확인합니다.
7. README, RELEASE_NOTES, 이 문서를 함께 갱신합니다.
