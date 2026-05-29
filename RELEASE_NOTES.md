# 릴리즈 노트

## 2.0.0-hermes.1 (2026-05-29)

첫 공개 Hermes Agent 포트입니다. 원본 `epoko77-ai/im-not-ai` v2.0.0 계열의 한국어 글쓰기 품질 개선과 번역투·후편집투 완화 workflow를 Hermes skill package로 옮겼습니다.

### 핵심 내용

- Hermes tap-friendly repository 구조를 적용했습니다.
  - `skills/humanize-korean/SKILL.md`
  - `skills/humanize-korean/references/`
  - `skills/humanize-korean/scripts/`
  - `skills/humanize-korean/tests/`
- `hermes skills tap add`와 `hermes skills install`로 설치할 수 있도록 README를 정리했습니다.
- 원본 MIT attribution을 `NOTICE.md`와 문서에 보존했습니다.
- public skill boundary를 문서에 명시했습니다.
  - 개인 문체, 기관 house style, 비공개 프로젝트 어휘를 포함하지 않습니다.
  - 작성 과정을 숨기거나 AI 사용 공개 의무를 피하는 목적으로 사용하지 않습니다.
- writer profile에서 hub/tap 설치본을 검증했습니다.

### 반영한 원본 v2.0-era 요소

- v1.6 KatFish/LREAD-inspired metrics layer
- v1.6.1 `final.md` 단일 산출물과 `HUMANIZE-SUMMARY` 메타데이터 패턴
- v2.0 한국 번역학계 기반 taxonomy 보강
- v2.0 post-editese/interference metric track
- `scholarship.md` 근거 메모
- `baseline.json`, `baseline_v2.json`
- metrics 회귀 테스트

### Hermes 포트 변경

- Claude Code 전용 `Agent`, `TeamCreate`, `TeamDelete`, slash command, model routing을 실행 전제로 삼지 않도록 정리했습니다.
- Hermes Agent가 fast path를 직접 수행하도록 `SKILL.md`를 재작성했습니다.
- strict path는 고정된 5-agent runtime이 아니라 Hermes multi-pass workflow와 선택적 `delegate_task`로 설명했습니다.
- raw `SKILL.md` URL 설치 대신 tap/hub 설치를 권장합니다.

### 검증

다음 검증을 통과했습니다.

```bash
python3 -m pytest skills/humanize-korean/tests -q
hermes skills inspect andrea9292/im-not-ai-hermes/skills/humanize-korean
```

writer profile에는 다음 방식으로 설치 검증했습니다.

```bash
hermes --profile writer skills tap add andrea9292/im-not-ai-hermes
hermes --profile writer skills install andrea9292/im-not-ai-hermes/skills/humanize-korean --category writing --yes
```

설치 결과에는 `skills.sh` source, community trust, safe scan verdict가 기록되었습니다.

### 알려진 제한

- 이 저장소는 Hermes skill package이며 웹 서비스 구현을 포함하지 않습니다.
- `metrics.py`와 `metrics_v2.py`는 보조 신호 도구입니다. AI 여부를 판정하는 검출기가 아닙니다.
- raw URL 설치는 reference/script 파일을 누락할 수 있으므로 권장하지 않습니다.
- 현재는 GitHub Actions CI를 포함하지 않습니다. 릴리즈 전 로컬 smoke test를 수행합니다.
