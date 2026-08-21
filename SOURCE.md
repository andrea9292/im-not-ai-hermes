# 출처 동기화 기록

이 문서는 `im-not-ai-hermes`가 기준으로 삼은 원본과 Hermes 포트에서 바꾼 점을 기록합니다.

## 원본 기준

| 항목 | 내용 |
|---|---|
| Original repository | https://github.com/epoko77-ai/im-not-ai |
| Original license | MIT |
| Original release | `v2.3.2` |
| Upstream commit used for this port | `bad4ef0a2b514318b2278b65cb4545414ad84d82` |
| Hermes port version | `2.3.2-hermes.1` |
| Sync date | `2026-08-21` |
| Hermes repository | https://github.com/andrea9292/im-not-ai-hermes |

원본 v2.3.2는 v2.3.0의 taxonomy·`route_hint` 기반 3경로·4축 구조 수렴 게이트를 유지하면서, v2.3.1~v2.3.2에서 실행 경로, 내용 앵커, 텍스트 위생, Windows 콘솔, 런타임 패키지 위치를 보정했습니다. Taxonomy와 baseline의 의미 내용은 v2.3.0 대비 바뀌지 않았습니다.

## 파일 매핑

| 원본 또는 개념 | Hermes 포트 |
|---|---|
| `skills/humanize-korean/SKILL.md`의 규칙·경로 정책 | `skills/humanize-korean/SKILL.md`의 Hermes-native workflow |
| `skills/humanize-korean/references/*.md` | `skills/humanize-korean/references/*.md` |
| `skills/humanize-korean/references/*.json` | `skills/humanize-korean/references/*.json` |
| `skills/humanize-korean/references/*.py` | `skills/humanize-korean/references/*.py` |
| `agents/humanize-diagnostician.md` | `skills/humanize-korean/references/runtime-agents/diagnostician.md` |
| `agents/humanize-monolith.md` | `skills/humanize-korean/references/runtime-agents/monolith.md` |
| `agents/humanize-finalizer.md` | `skills/humanize-korean/references/runtime-agents/finalizer.md` |
| `scripts/prepare_monolith_input.py` | `skills/humanize-korean/scripts/prepare_monolith_input.py` |
| `scripts/sanitize_text.py` | `skills/humanize-korean/scripts/sanitize_text.py` |
| `scripts/console.py` | `skills/humanize-korean/scripts/console.py` |
| `scripts/checks.py` | `skills/humanize-korean/scripts/golden_checks.py` |
| `scripts/build_quick_rules.py` | `skills/humanize-korean/scripts/build_quick_rules.py` |
| `scripts/build_diagnosis_rules.py` | `skills/humanize-korean/scripts/build_diagnosis_rules.py` |
| `scripts/reassemble_chunks.py` | `skills/humanize-korean/scripts/reassemble_chunks.py` |
| `scripts/verify_gates.py` | `skills/humanize-korean/scripts/verify_gates.py` |
| `scripts/verify_change_rate.py` | `skills/humanize-korean/scripts/verify_change_rate.py` |
| strict 단계·표면 보존 실행 계약 | `skills/humanize-korean/scripts/validate_stage_artifacts.py` |
| Hermes 비동기 역할 completion 증적 | `skills/humanize-korean/scripts/update_execution_state.py` |
| 결정적·골든·청킹·route 테스트 | `skills/humanize-korean/tests/` |
| `.github/workflows/test.yml`의 검증 의도 | `.github/workflows/test.yml`의 Hermes 패키지 경로 |
| `LICENSE` | `LICENSE` |
| 원본 출처 고지 | `NOTICE.md`, `README.md`, 이 문서 |

## Hermes 포트에서 바꾼 점

이 포트는 원본의 글쓰기 규칙과 검증 코드를 보존하되, 운영 방식을 Hermes Agent에 맞게 조정합니다.

- Claude Code의 `.claude/agents/*.md`를 Hermes runtime agent로 등록하지 않습니다.
- Claude Code의 `Agent`, `TeamCreate`, `TeamDelete`, `model: opus` 라우팅은 직접 사용하지 않습니다.
- Claude Code slash command인 `/humanize`, `/humanize-redo`를 제공하지 않습니다.
- upstream 런타임 3역할은 패키지된 참조 프롬프트와 Hermes `delegate_task`로 변환합니다.
- `light`는 monolith 1콜, `standard`는 diagnostician→monolith 2콜, `heavy/strict`는 diagnostician→monolith→finalizer 3+콜을 실행 계약으로 둡니다.
- Hermes 부모 agent는 각 child 산출물을 다시 읽고 결정적 검증을 실행한 뒤 최종 채택 여부를 판단합니다.
- strict run은 실제 delegation ID, 역할 completion 순서, 부모 구조 게이트의 문자율과 통합 exit code를 `00_execution.json`의 하위 호환 `change_rate` 필드에 기록합니다.
- `delegate_task`가 없는 strict fallback은 자동으로 upstream-equivalent라고 간주하지 않습니다.
- helper script는 저장소 루트의 `.claude` 경로가 아니라 설치된 skill package의 `references/`를 찾습니다.
- repository 구조는 Hermes tap discovery를 위해 `skills/humanize-korean/`를 사용합니다.
- raw `SKILL.md` URL 설치보다 `hermes skills tap add`와 `hermes skills install`을 우선합니다.
- 개인 문체, 기관별 house style, 비공개 프로젝트 어휘는 public skill에 넣지 않습니다.

## 반영한 v2.3 계열 내용

- 전체 taxonomy와 taxonomy-to-quick-rules 생성 계약
- taxonomy-to-diagnosis-rules 생성 계약과 71패턴 슬림 인덱스
- B-2 전문용어 보존, C-1 심각도·학술구조 예외, C-8 부정-긍정 대구 보강
- scholarship의 이론적 종합과 후속 근거
- `metrics_v2.py`의 sibling import·baseline 경로 수정
- `route_hint`: `light`, `standard`, `heavy`
- 문자율·S1 목표 달성·C-8 대구 전멸·golden/수치 주입의 4축 구조 게이트
- 하위 호환 `verify_change_rate.py`와 Hermes summary/provenance stamping
- 헤딩 승격, 각주 passthrough, source hash를 포함한 손실 없는 청킹·재조립
- register, 구조, 각주, 직접 인용 보존을 점검하는 골든 회귀 테스트
- 진단 ID·summary·finalize JSON·헤딩·수치·인용·코드·각주 보존을 점검하는 단계 검증기
- Hermes fresh-context delegation용 diagnostician·monolith·finalizer 역할 계약
- Light finalizer의 선택적 `diagnosis_path`와 내용 앵커 보존 계약
- NFD·비가시 문자 입력 위생 처리와 Windows cp949 콘솔·게이트 exit 3 보호
- cwd 기준 run-dir 해석, 절대 rule path dispatch, 설치형 transitive package 검사
- GitHub Actions에서 Python 3.11·3.12 회귀 테스트와 quick-rules·diagnosis-rules 동기화 검사

A-17은 upstream v2.3에서도 hold 상태입니다. 지표·학술 참고로만 유지하며 기본 윤문 트리거로 사용하지 않습니다.

## 제외하거나 바꾼 것

- Claude·Codex·Gemini용 plugin manifest, command, installer는 포함하지 않습니다.
- 원본 role agent frontmatter와 `model: opus` 힌트는 복제하지 않습니다. 역할 본문과 입출력 계약만 Hermes 참조 프롬프트로 옮깁니다.
- 원본의 경로별 역할 호출 수는 Hermes `delegate_task` 실행 계약으로 보존하되, 모델 선택은 Hermes 전역 delegation 설정에 맡깁니다.
- web service 구현은 포함하지 않습니다. `web-service-spec.md`는 참고 문서로만 유지합니다.
- 원본의 live Claude CLI 테스트는 포함하지 않습니다. 공개 CI는 결정적·stdlib 기반 테스트만 실행합니다.
- Claude live runner에 결합된 `eval_baseline.py`, `eval_compare.py`, watermark snapshot·runbook은 포함하지 않습니다.
- upstream의 Claude plugin layout 이동은 Hermes가 이미 사용하는 루트 `skills/` 구조와 동등하므로 별도 manifest·installer를 가져오지 않습니다.

## 동기화 시 점검 항목

1. upstream release tag와 commit을 기록합니다.
2. taxonomy, quick rules, playbook, scholarship, metrics, baseline 변경 여부를 확인합니다.
3. Hermes 경로에 맞게 script import와 file path를 조정합니다.
4. `python3 -m pytest skills/humanize-korean/tests -q`를 실행합니다.
5. `python3 skills/humanize-korean/scripts/build_quick_rules.py --check`를 실행합니다.
6. `python3 skills/humanize-korean/scripts/build_diagnosis_rules.py --check`를 실행합니다.
7. package contents와 Git archive 경계를 검사합니다.
8. README, RELEASE_NOTES, 이 문서를 함께 갱신합니다.
