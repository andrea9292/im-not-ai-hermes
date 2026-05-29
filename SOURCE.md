# 출처 동기화 기록

이 문서는 `im-not-ai-hermes`를 만들 때 기준으로 삼은 원본과 Hermes 포트에서 바꾼 점을 기록합니다.

## 원본 기준

| 항목 | 내용 |
|---|---|
| Original repository | https://github.com/epoko77-ai/im-not-ai |
| Original license | MIT |
| Original release line | `v2.0.0` |
| Upstream commit used for this port | `807172694d75a9e9e0390f93331387c389ce748e` |
| Hermes port version | `2.0.0-hermes.1` |
| Sync date | `2026-05-29` |
| Hermes repository | https://github.com/andrea9292/im-not-ai-hermes |

원본 v2.0.0 계열은 v1.6.1의 fast monolith 흐름과 `final.md` 메타데이터 정책을 유지하면서, 한국 번역학계 기반 번역투 유형, post-editese metric layer, v2 baseline, scholarship reference를 추가합니다.

## 파일 매핑

| 원본 또는 개념 | Hermes 포트 |
|---|---|
| `.claude/skills/humanize-korean/SKILL.md` | `skills/humanize-korean/SKILL.md` |
| `.claude/skills/humanize-korean/references/*.md` | `skills/humanize-korean/references/*.md` |
| `.claude/skills/humanize-korean/references/*.json` | `skills/humanize-korean/references/*.json` |
| `.claude/skills/humanize-korean/references/*.py` | `skills/humanize-korean/references/*.py` |
| `scripts/prepare_monolith_input.py` | `skills/humanize-korean/scripts/prepare_monolith_input.py` |
| `tests/test_metrics.py` | `skills/humanize-korean/tests/test_metrics.py` |
| `tests/test_metrics_v2.py` | `skills/humanize-korean/tests/test_metrics_v2.py` |
| `LICENSE` | `LICENSE` |
| 원본 출처 고지 | `NOTICE.md`, `README.md`, 이 문서 |

## Hermes 포트에서 바꾼 점

이 포트는 원본의 글쓰기 규칙과 참고 자료를 보존하되, 운영 방식을 Hermes Agent에 맞게 조정합니다.

- Claude Code의 `.claude/agents/*.md`를 Hermes runtime agent로 등록하지 않습니다.
- Claude Code의 `Agent`, `TeamCreate`, `TeamDelete`, `model: opus` 라우팅을 사용하지 않습니다.
- Claude Code slash command인 `/humanize`, `/humanize-redo`를 제공하지 않습니다.
- Hermes에서는 `humanize-korean` skill instruction, reference files, file tools, terminal tools, 선택적 `delegate_task`로 workflow를 진행합니다.
- repository 구조는 Hermes tap discovery를 위해 `skills/humanize-korean/`를 사용합니다.
- raw `SKILL.md` URL 설치보다 `hermes skills tap add`와 `hermes skills install`을 우선합니다.
- personal voice matching, 기관별 house style, 비공개 프로젝트 어휘는 public skill에 넣지 않습니다.

## 포함한 v2.0 계열 내용

- `ai-tell-taxonomy.md`: 한국 번역학계 유형을 포함한 전체 taxonomy
- `quick-rules.md`: fast path용 S1/S2 핵심 규칙
- `rewriting-playbook.md`: 카테고리별 윤문 처방
- `scholarship.md`: 번역투와 post-editese 관련 근거 메모
- `metrics.py`: v1.6 계열 KatFish/LREAD-style 정량 지표
- `metrics_v2.py`: v2.0 post-editese/interference 지표
- `baseline.json`, `baseline_v2.json`: 지표 기준값과 placeholder cell
- `prepare_monolith_input.py`: 파일 workflow용 metrics/input 준비 스크립트
- metrics 회귀 테스트

## 제외하거나 바꾼 것

- marketplace용 이미지 asset은 포함하지 않습니다.
- Codex plugin manifest나 Claude Code command 파일은 포함하지 않습니다.
- 원본 role agent prompt를 별도 `references/agents/`로 복제하지 않습니다. Hermes에서는 strict review를 고정된 5-agent runtime 대신 optional multi-pass workflow로 설명합니다.
- web service 구현은 포함하지 않습니다. `web-service-spec.md`는 참고 문서로만 유지합니다.

## 동기화 시 점검 항목

원본이 업데이트되면 다음 항목을 확인합니다.

1. upstream release tag와 commit을 기록합니다.
2. taxonomy, quick rules, playbook, scholarship, metrics, baseline 변경 여부를 확인합니다.
3. Hermes 경로에 맞게 script import와 file path를 조정합니다.
4. `python3 -m pytest skills/humanize-korean/tests -q`를 실행합니다.
5. `hermes skills inspect andrea9292/im-not-ai-hermes/skills/humanize-korean`로 설치 가능성을 확인합니다.
6. README, RELEASE_NOTES, 이 문서를 함께 갱신합니다.
