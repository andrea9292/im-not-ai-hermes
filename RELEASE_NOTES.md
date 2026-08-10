# 릴리즈 노트

## 2.2.1-hermes.1 (2026-08-10)

Windows 콘솔(cp949)에서 CLI 게이트가 em dash(—) 출력 시 `UnicodeEncodeError`로 죽는 버그를 수정했습니다.

### 핵심 변경

- `scripts/_stdio.py`를 신설해 stdout/stderr를 UTF-8로 재구성하는 `force_utf8_stdio()`를 제공합니다.
- `verify_change_rate.py`, `build_quick_rules.py`, `prepare_monolith_input.py`, `reassemble_chunks.py` 4종의 `main()`에서 이를 호출합니다.
- 이전에는 `verify_change_rate.py`가 cp949 콘솔에서 "통과(exit 0) 후 출력 중 크래시 → exit 1"이 되어 호출부가 **과윤문 경고로 오독**하는 문제가 있었습니다. 이제 판정 문구(em dash 포함)가 항상 UTF-8로 안전하게 출력됩니다.
- `main()` 내에서 스크립트 자신의 디렉토리를 `sys.path`에 명시적으로 추가해 테스트 모듈 import 방식과 충돌하지 않습니다.

### 검증

- cp949 강제(`PYTHONIOENCODING=cp949`) 환경에서 em dash 문구 출력이 크래시 없이 정상 동작합니다.
- pytest 133개(1 skip) 전체 통과를 유지합니다.

## 2.2.0-hermes.1 (2026-07-21)

원본 `epoko77-ai/im-not-ai` v2.2.0(`3120cb81`)의 taxonomy·검증·경로 선택 변경을 Hermes-native skill package에 반영했습니다.

### 핵심 변경

- `route_hint` 기반 `light`·`standard`·`heavy` 경로를 도입했습니다.
- 15,000자 이하에서는 길이만으로 heavy를 강제하지 않으며, 15,000자 초과는 upstream과 같이 heavy 신호로 처리합니다. Heavy여도 실제 body chunk가 2개 이상일 때만 청킹합니다.
- 30% 경고·50% 중단의 결정적 변경률 게이트를 추가했습니다.
- taxonomy에서 `quick-rules.md`를 생성하는 빌드 계약을 추가했습니다.
- 헤딩 승격, 숫자식·Markdown 다중행 각주 passthrough, source hash 검증을 포함한 손실 없는 청킹·재조립 도구를 추가했습니다.
- register, 구조, 각주, 직접 인용 보존을 점검하는 골든 회귀 테스트를 추가했습니다.

### taxonomy와 근거

- B-2의 전문용어 보존 원칙을 반영했습니다.
- C-1을 S2로 조정하고 학술·보고서 구조 예외를 보강했습니다.
- C-8에 `A가 아니라 B`형 부정-긍정 대구 반복을 포함했습니다.
- scholarship의 이론적 종합과 후속 근거를 반영했습니다.
- A-17은 upstream과 같이 hold 상태로 유지합니다.

### Hermes 적응

- Claude Code의 agent·command·plugin·model routing은 포함하지 않았습니다.
- main Hermes agent가 세 경로를 직접 수행하도록 `SKILL.md`를 재작성했습니다.
- helper script가 설치된 skill package의 `references/`를 찾도록 경로를 조정했습니다.
- 상대 `--run-dir`·`--diagnosis`·자동 `_workspace/`는 사용자 CWD를 기준으로 처리해 설치된 skill package에 작업 결과를 쓰지 않도록 했습니다.
- `delegate_task`는 heavy 검토의 선택 사항이며, 부모 agent가 최종 결과를 검증하도록 했습니다.

### 검증

- Python 3.11·3.12 GitHub Actions를 추가했습니다.
- 개발 환경에서 pytest 133개와 unittest 134개(각 1개 skip), quick-rules 동기화 검사를 통과했습니다.
- 임시 `HERMES_HOME`에서 패키지 설치와 skill 로딩을 검증했습니다.

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
- 별도 Hermes 프로필에서 hub/tap 설치본을 검증했습니다.

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

별도 프로필에는 다음 방식으로 설치 검증했습니다.

```bash
PROFILE=<profile-name>
hermes --profile "$PROFILE" skills tap add andrea9292/im-not-ai-hermes
hermes --profile "$PROFILE" skills install andrea9292/im-not-ai-hermes/skills/humanize-korean --category writing --yes
```

설치 결과에는 `skills.sh` source, community trust, safe scan verdict가 기록되었습니다.

### 알려진 제한

- 이 저장소는 Hermes skill package이며 웹 서비스 구현을 포함하지 않습니다.
- `metrics.py`와 `metrics_v2.py`는 보조 신호 도구입니다. AI 여부를 판정하는 검출기가 아닙니다.
- raw URL 설치는 reference/script 파일을 누락할 수 있으므로 권장하지 않습니다.
- 이 버전에는 GitHub Actions CI가 없었으며 릴리즈 전 로컬 smoke test만 수행했습니다.
