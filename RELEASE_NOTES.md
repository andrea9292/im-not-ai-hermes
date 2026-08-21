# 릴리즈 노트

## Unreleased

### Hermes 적응

- upstream `v2.3.1`에서 확정된 이슈 #54 계약을 선택적으로 백포트했습니다. Light가 finalizer로 승급해도 diagnostician 콜을 추가하지 않으며, `diagnosis_path` 없이 원문과 윤문본을 직접 대조합니다.
- upstream `v2.3.1`의 `anchor_ledger` 계약을 선택적으로 백포트했습니다. monolith가 편집 전에 문장별 핵심 내용 명사·개념어를 원형으로 기록하고, 앵커가 사라지는 edit을 롤백하며, finalizer가 원문과 직접 대조해 누락을 복원합니다.
- upstream `v2.3.1`의 입력 위생 처리를 선택적으로 백포트했습니다. metrics·route·청크 해시 전에 NFD 한글과 비가시 제어문자·특수공백·줄바꿈을 정리하고, 변경 시 `00_sanitize.json`을 남기며, `--no-sanitize`로 비활성화할 수 있습니다. 전각공백과 반복 빈 줄은 기본 보존합니다.
- upstream `v2.3.2`의 Windows 콘솔 하드닝을 선택적으로 백포트했습니다. 패키지 CLI가 stdout·stderr를 UTF-8로 재설정하며, 구조 게이트와 하위 호환 변경률 게이트의 예기치 못한 예외는 경고 exit `1`과 구분되는 실행 오류 exit `3`으로 정규화합니다.

## 2.3.0-hermes.1 (2026-08-02)

원본 `epoko77-ai/im-not-ai` v2.3.0(`82137e85`)의 구조 수렴 게이트와 진단 슬림 인덱스를 기존 Hermes-native delegation·부모 검증 계약 위에 선택적으로 이식했습니다.

### 핵심 변경

- 문자 변경률, S1 목표 달성, C-8 대구 전멸, golden/수치 주입을 결합한 `verify_gates.py`를 새 채택 게이트로 추가했습니다.
- 문장 터치율과 원문 수치 소실은 관찰값으로 보고하되 독립 실패 축으로 사용하지 않습니다.
- taxonomy에서 71패턴 `diagnosis-rules.md`를 생성하는 `build_diagnosis_rules.py`와 drift 검사를 추가했습니다.
- diagnostician은 전체 taxonomy 대신 슬림 진단 인덱스를 읽습니다. taxonomy는 유지보수·감사 SSOT로 남습니다.
- `metrics_v2.antithesis_count()`와 golden `number_injected` 검사를 추가했습니다.
- `verify_change_rate.py`는 하위 호환 및 Hermes summary/provenance 기록 helper로 유지합니다.

### Hermes 적응

- `verify_gates.py`에 `--stamp-summary`와 `--execution-state`를 추가해 부모가 측정한 문자율과 통합 gate exit를 기존 필드에 기록합니다.
- `delegate_task`, fresh-context 3역할, child artifact read-back, stage validator, `final_pre_finalize.md`, `00_execution.json` 계약을 유지했습니다.
- Claude Code 전용 `Agent`, `model: opus`, slash command는 가져오지 않았습니다.

### 검증

- Python 3.12 pytest: 208 passed, 1 skipped, 22 subtests passed.
- Python 3.11 stdlib unittest: 209 tests passed, 1 skipped.
- quick-rules·diagnosis-rules drift 검사와 22개 필수 package contents 검사를 통과했습니다.

## 2.2.0-hermes.2 (2026-07-21)

upstream v2.2의 경로별 역할 분리를 Hermes-native delegation으로 복원했습니다. Claude Code 전용 agent 등록과 모델 라우팅은 가져오지 않지만, diagnostician→monolith→finalizer의 fresh-context 효과와 산출물 계약은 보존합니다.

### 핵심 변경

- `references/runtime-agents/`에 diagnostician·monolith·finalizer 역할 계약을 추가했습니다.
- `light` 1콜, `standard` 2콜, `heavy/strict` 3+콜을 `delegate_task` 실행 계약으로 명시했습니다.
- strict에서 delegation을 선택 사항으로 두던 기존 규칙을 폐기했습니다. 도구가 없거나 반복 실패하면 자동으로 strict 완료를 주장하지 않습니다.
- 입력 길이로 route를 바꾸지 않습니다. Strict는 3역할을 강제하지만 청킹은 강제하지 않으며, 단일 child가 안정적으로 처리하기 어려운 장문이나 사용자 요청에서만 청크 경로를 선택합니다.
- 청크 병렬은 manifest가 실제 body chunk를 2개 이상 만들 때만 하나의 Hermes batch로 실행하고, 각 child가 서로 다른 출력 파일만 쓰도록 했습니다.
- main agent가 child 산출물을 다시 읽고 검증한 뒤 채택하도록 책임 경계를 정리했습니다.
- `00_execution.json`에 실제 delegation ID, 역할 completion 순서, 부모가 측정한 변경률을 기록합니다.
- Standard의 finalizer 승급 조건(변경률 경고, 자체검증 2개 이상 실패, 명시적 검증 증적 요청)을 복원했습니다.
- 범용 문자열 치환을 monolith 역할의 대체물로 쓰지 못하도록 금지했습니다.

### 결정적 검증

- `validate_stage_artifacts.py`를 추가했습니다.
- 진단 패턴 3~6개와 taxonomy ID, strict 필수 산출물, `09_finalize.json` 스키마와 verdict를 검사합니다.
- 헤딩, 코드 펜스, 인라인 코드, URL, 수치, 직접 인용, Markdown 각주를 원문과 대조합니다.
- `전달하지 못가능합니다`류 기계 치환 비문, 격식 상향, 새 상투구 주입을 검사합니다.
- 목록 구조는 upstream C-2/C-9 변환을 기본 허용하고, 사용자가 명시적으로 보존한 실행에서만 `--preserve-lists`로 고정합니다.
- 결정적 validator는 파일·스키마와 표면 보존 토큰을 검사합니다. 주체 귀속·범위·판단 강도 같은 의미 보존 판정은 fresh-context finalizer가 맡습니다.
- chunk→non-chunk 모드 전환 때 낡은 manifest·청크·재조립 산출물을 제거해 이전 실행이 섞이지 않게 했습니다.
- orchestration 계약과 runtime prompt 패키징을 회귀 테스트로 고정했습니다.

### 검증

- Python 3.12에서 pytest 160개 통과, 1개 skip, 22개 하위 사례 통과를 확인했습니다. Python 3.11 stdlib unittest에서는 161개 테스트 통과, 1개 skip을 확인했습니다.
- quick-rules 동기화, Python 구문 검사, `git diff --check`를 통과했습니다.
- 이전의 불완전 strict 실행을 단계 검증기에 넣어 diagnosis·pre-finalize·finalize 산출물 누락을 실제로 차단하는지 확인했습니다.

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