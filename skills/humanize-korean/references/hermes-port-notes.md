# Hermes 포트 노트

## 출처

- 원본 저장소: `epoko77-ai/im-not-ai`
- 원본 라이선스: MIT
- 원본 Claude Code 스킬: `.claude/skills/humanize-korean/`
- 포팅 기준: upstream `v2.2.0`, commit `3120cb81e3b9910ba393cd8289864c583f0ac50a` (2026-07-18)
- Hermes 포트: `2.2.0-hermes.1` (2026-07-21)

이 Hermes 포트는 원저자와 기여자의 attribution을 보존합니다. Taxonomy, quick rules, rewriting playbook, scholarship reference, metrics와 결정적 검증 도구는 원본 프로젝트에서 가져와 Hermes Agent에서 사용할 수 있도록 운영 방식을 조정했습니다.

## Hermes 포트에서 바꾼 점

원본 프로젝트는 Claude Code의 agent, command, plugin, model routing을 전제로 합니다. Hermes는 이를 그대로 실행 가능한 skill machinery로 취급하지 않으므로 다음과 같이 바꿉니다.

- main Hermes agent가 `light`, `standard`, `heavy` 경로를 직접 수행합니다.
- 기본 규칙 출처는 자동 생성된 `references/quick-rules.md`입니다.
- taxonomy와 고정 header/footer가 quick rules의 SSOT입니다.
- metrics와 `route_hint`는 참고 신호이며 AI 판정 결과로 사용하지 않습니다.
- 파일 작업은 `verify_change_rate.py`의 실제 계산값을 사용합니다.
- 15,000자 이하는 길이만으로 heavy가 되지 않습니다. 15,000자 초과는 upstream 계약에 따라 heavy 신호이며, 그때도 `--chunk`가 body chunk를 2개 이상 만들 때만 청크 경로를 사용합니다.
- 정밀 검토에 `delegate_task`를 쓸 수 있지만, 부모 agent가 최종 결과와 외부 부작용을 검증합니다.
- 개인 문체 matching은 public skill에 넣지 않습니다.

## v2.2 포트 구성

- `references/ai-tell-taxonomy.md`: 활성 70개 패턴과 A-17 hold를 포함한 taxonomy
- `references/quick-rules.md`: taxonomy에서 생성한 빠른 경로 규칙
- `references/quick-rules.header.md`, `quick-rules.footer.md`: 생성물 고정 템플릿
- `references/rewriting-playbook.md`: 카테고리별 윤문 처방
- `references/scholarship.md`: 외부 학술 근거와 이론적 종합
- `references/metrics.py`, `metrics_v2.py`: 정량 보조 지표와 변경률 계산
- `scripts/prepare_monolith_input.py`: metrics, `route_hint`, 선택적 lossless chunk 생성
- `scripts/build_quick_rules.py`: taxonomy-to-quick-rules 생성·동기화 검사
- `scripts/reassemble_chunks.py`: source hash와 문자 수 대사를 포함한 청크 재조립
- `scripts/verify_change_rate.py`: 30% 경고·50% 중단의 결정적 게이트
- `tests/`: metrics, route, 청킹, 골든 픽스처 회귀 테스트

## 공개 배포 경계

이 skill은 범용 한국어 글쓰기 품질 개선 도구로 유지합니다. 다음 항목은 추가하지 않습니다.

- 특정 개인의 voice profile
- private style-guide rule
- 기관별 house style
- 공개되지 않은 프로젝트 용어
- 한 사용자에게만 의미 있는 writing preference

사용자가 개인 문체 반영을 원하면 별도 local skill, style guide, voice sample을 이 skill 위에 조합합니다.

## 유지보수

- taxonomy를 수정하면 `python scripts/build_quick_rules.py`로 생성물을 갱신합니다.
- 배포 전 `python -m pytest tests -q`와 `python scripts/build_quick_rules.py --check`를 모두 통과해야 합니다.
- upstream sync가 바뀌면 `README.md`, `SOURCE.md`, `RELEASE_NOTES.md`, `MAINTAINING.md`를 함께 갱신합니다.
