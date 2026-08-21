# Hermes 포트 노트

## 출처

- 원본 저장소: `epoko77-ai/im-not-ai`
- 원본 라이선스: MIT
- 원본 Claude Code 스킬: `skills/humanize-korean/`
- 포팅 기준: upstream `v2.3.2`, commit `bad4ef0a2b514318b2278b65cb4545414ad84d82` (2026-08-18)
- Hermes 포트: `2.3.2-hermes.1` (2026-08-21)

이 Hermes 포트는 원저자와 기여자의 attribution을 보존합니다. Taxonomy, quick rules, rewriting playbook, scholarship reference, metrics와 결정적 검증 도구는 원본 프로젝트에서 가져와 Hermes Agent에서 사용할 수 있도록 운영 방식을 조정했습니다.

## Hermes 포트에서 바꾼 점

원본 프로젝트는 Claude Code의 agent, command, plugin, model routing을 전제로 합니다. Hermes는 이를 그대로 실행 가능한 skill machinery로 취급하지 않으므로 다음과 같이 바꿉니다.

- upstream의 diagnostician·monolith·finalizer 역할을 `references/runtime-agents/`의 Hermes 참조 프롬프트로 보존합니다.
- `light` 1콜, `standard` 2콜, `heavy/strict` 3+콜을 Hermes `delegate_task` 실행 계약으로 둡니다.
- 기본 규칙 출처는 자동 생성된 `references/quick-rules.md`입니다.
- taxonomy와 고정 header/footer가 quick rules의 SSOT입니다.
- metrics와 `route_hint`는 참고 신호이며 AI 판정 결과로 사용하지 않습니다.
- 파일 작업은 `verify_gates.py`의 문자율·S1 목표·C-8 전멸·golden/수치 주입 통합 결과를 사용합니다. `verify_change_rate.py`는 하위 호환용으로 유지합니다.
- 입력 길이는 route를 바꾸지 않습니다. Heavy/strict에서도 단일 child가 안정적으로 처리하기 어려운 장문이거나 사용자가 요청한 경우에만 `--chunk`를 쓰며, body chunk가 2개 이상일 때만 청크 경로를 사용합니다.
- 부모 agent는 child의 완료 보고를 그대로 믿지 않고 모든 산출물을 다시 읽어 결정적 검증을 수행합니다.
- strict에서 delegation을 사용할 수 없으면 자동 fallback하지 않습니다. 승인된 in-process 결과는 degraded non-strict로 구분하며, `hold_and_report`는 finalizer가 해결하지 못한 보존 의심에만 사용합니다.
- 개인 문체 matching은 public skill에 넣지 않습니다.

## v2.3.2 포트 구성

- `references/ai-tell-taxonomy.md`: 활성 70개 패턴과 A-17 hold를 포함한 taxonomy
- `references/quick-rules.md`: taxonomy에서 생성한 빠른 경로 규칙
- `references/quick-rules.header.md`, `quick-rules.footer.md`: 생성물 고정 템플릿
- `references/rewriting-playbook.md`: 카테고리별 윤문 처방
- `references/scholarship.md`: 외부 학술 근거와 이론적 종합
- `references/metrics.py`, `metrics_v2.py`: 정량 보조 지표와 변경률 계산
- `scripts/prepare_monolith_input.py`: metrics, `route_hint`, 선택적 lossless chunk 생성
- `scripts/sanitize_text.py`: NFD 한글·비가시 문자·특수공백·줄바꿈 입력 위생 처리
- `scripts/console.py`: Windows cp949 콘솔 출력과 게이트 실행 오류 exit 3 보호
- `scripts/build_quick_rules.py`: taxonomy-to-quick-rules 생성·동기화 검사
- `scripts/build_diagnosis_rules.py`: taxonomy-to-diagnosis-rules 생성·동기화 검사
- `scripts/reassemble_chunks.py`: source hash와 문자 수 대사를 포함한 청크 재조립
- `scripts/verify_gates.py`: 문자율·S1 목표·C-8 전멸·golden/수치 주입의 통합 구조 게이트
- `scripts/golden_checks.py`: 설치형 패키지 안에서 실행되는 golden·수치 보존 검사
- `scripts/verify_change_rate.py`: 하위 호환 문자율 게이트와 Hermes summary/provenance 기록 helper
- `scripts/validate_stage_artifacts.py`: 역할별 필수 산출물과 구조·수치·인용·코드·각주의 표면 보존 검증. 주체 귀속·범위·판단 강도 같은 의미 보존은 fresh-context finalizer가 원문과 직접 대조
- `scripts/update_execution_state.py`: 부모가 검증한 Hermes 역할 completion과 게이트 결과 기록
- `references/runtime-agents/`: Hermes용 diagnostician·monolith·finalizer 역할 계약
- `tests/`: metrics, route, 청킹, 골든 픽스처 회귀 테스트
- `scripts/check_package_contents.py`: 설치형 transitive runtime 의존 파일과 source 테스트 경계 검사

## 공개 배포 경계

이 skill은 범용 한국어 글쓰기 품질 개선 도구로 유지합니다. 다음 항목은 추가하지 않습니다.

- 특정 개인의 voice profile
- private style-guide rule
- 기관별 house style
- 공개되지 않은 프로젝트 용어
- 한 사용자에게만 의미 있는 writing preference

사용자가 개인 문체 반영을 원하면 별도 local skill, style guide, voice sample을 이 skill 위에 조합합니다.

## 유지보수

- taxonomy를 수정하면 `python scripts/build_quick_rules.py`와 `python scripts/build_diagnosis_rules.py`로 생성물을 갱신합니다.
- 배포 전 `python -m pytest tests -q`, 두 생성기의 `--check`, package contents 검사를 모두 통과해야 합니다.
- upstream sync가 바뀌면 `README.md`, `SOURCE.md`, `RELEASE_NOTES.md`, `MAINTAINING.md`를 함께 갱신합니다.