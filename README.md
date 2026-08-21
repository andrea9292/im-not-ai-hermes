# im-not-ai-hermes

`im-not-ai-hermes`는 [`epoko77-ai/im-not-ai`](https://github.com/epoko77-ai/im-not-ai)를 Hermes Agent에서 사용할 수 있도록 옮겨 만든 한국어 글쓰기 품질 개선 스킬입니다.

이 저장소는 `andrea9292`가 관리하는 community downstream 포트입니다. 원본 프로젝트의 공식 배포판이 아니며, 특정 기관이나 연구소의 공식 배포물처럼 소개하지 않습니다.

## 무엇을 하는 스킬인가

`humanize-korean`은 한국어 초안에서 AI 생성문처럼 읽히는 반복 표현, 번역투, 기계번역 후편집투, 과도하게 정돈된 문장 구조, 반복적인 연결어와 결론 표현을 줄이기 위한 Hermes 스킬입니다.

목표는 작성자를 지우거나 작성 과정을 감추는 데 있지 않습니다. 의미, 사실, 장르, 문체 수준, 인용, 수치, 고유명사, 기술 용어를 보존하면서 한국어 문장의 리듬과 표현을 더 자연스럽게 다듬습니다.

저작권, 학업, 업무, 출판, 연구 윤리상 AI 사용 공개가 필요한 상황에서는 이 스킬을 공개 의무를 피하는 용도로 사용해서는 안 됩니다.

## 상태

| 항목 | 내용 |
|---|---|
| Hermes skill name | `humanize-korean` |
| Repository | `andrea9292/im-not-ai-hermes` |
| Package path | `skills/humanize-korean/` |
| Hermes port version | `2.3.0-hermes.1` |
| Original project | `epoko77-ai/im-not-ai` |
| Original baseline | v2.3.0, upstream commit `82137e85`까지 반영 |
| License | MIT |
| Distribution | Hermes tap-friendly skill source |

## 버전 정책

이 포트의 버전은 원본 버전과 Hermes 포트 패치 번호를 함께 표기합니다.

```text
2.3.0-hermes.1
```

이 버전 표기의 의미는 다음과 같습니다.

- `2.3.0`: 원본 `epoko77-ai/im-not-ai`의 v2.3.0 taxonomy, route-aware workflow, 구조 수렴 게이트, 진단 슬림 인덱스를 기준으로 합니다.
- `hermes.1`: v2.3.0의 새 검증·진단 계약을 기존 Hermes `delegate_task`와 부모 검증 방식에 선택적으로 이식한 첫 번째 포트 패치입니다.

원본이 새 버전으로 올라가면 원본 변경분을 검토한 뒤 `2.4.0-hermes.1`처럼 원본 버전과 Hermes 포트 번호를 함께 갱신합니다.

## 왜 한국어 특화인가

한국어 AI 문체는 영어권 humanizer가 다루는 일반적인 과잉 수사와 달리, 영한 번역투와 한국어 문장 리듬 문제로 드러나는 경우가 많습니다.

예를 들면 다음과 같습니다.

| 기계적으로 느껴지는 표현 | 더 자연스러운 방향 |
|---|---|
| AI 기술을 통해 효율을 높일 수 있다 | AI로 효율을 높인다 |
| 이에 있어서 중요한 점은 | 여기서 중요한 건 |
| 시스템에 의해 생성된 결과 | 시스템이 만든 결과 |
| 결론적으로 이는 시사하는 바가 크다 | 문맥에 따라 삭제하거나 구체화 |

이 스킬은 이런 표현을 무조건 삭제하지 않습니다. 장르와 맥락에 맞을 때는 보존하고, 반복되거나 번역투로 읽히는 경우에만 필요한 부분을 다듬습니다.

## 4대 원칙

1. **의미 보존** — 사실, 주장, 수치, 고유명사, 날짜, 직접 인용, 법률·기술 용어를 바꾸지 않습니다.
2. **근거 기반 수정** — 감으로 전체를 다시 쓰지 않고, 확인 가능한 AI 문체·번역투 신호를 중심으로 고칩니다.
3. **장르와 격식 유지** — 보고서는 보고서답게, 칼럼은 칼럼답게, 공지는 공지답게 유지합니다.
4. **과윤문 금지** — 매끈하지만 개성이 없는 글, 지나치게 문학적인 글, 저자 목소리가 사라진 글로 만들지 않습니다.

## 저장소 구조

이 저장소는 Hermes tap source로 사용할 수 있도록 `skills/` 아래에 스킬 패키지를 둡니다.

```text
skills/humanize-korean/SKILL.md                         # Hermes 스킬 진입점
skills/humanize-korean/references/quick-rules.md        # 빠른 윤문용 핵심 규칙
skills/humanize-korean/references/diagnosis-rules.md    # 진단 전용 슬림 인덱스
skills/humanize-korean/references/ai-tell-taxonomy.md   # 전체 분류 체계
skills/humanize-korean/references/rewriting-playbook.md # 카테고리별 윤문 처방
skills/humanize-korean/references/scholarship.md        # 번역투·후편집투 관련 근거 메모
skills/humanize-korean/references/runtime-agents/       # Hermes용 진단·윤문·finalize 역할 계약
skills/humanize-korean/references/metrics.py            # v1.6 계열 정량 지표 보조 도구
skills/humanize-korean/references/metrics_v2.py         # v2.0 후편집투·간섭 지표 보조 도구
skills/humanize-korean/scripts/prepare_monolith_input.py# metrics·route_hint·청킹 준비
skills/humanize-korean/scripts/sanitize_text.py         # NFD·비가시 문자·줄바꿈 입력 위생 처리
skills/humanize-korean/scripts/console.py               # Windows cp949 콘솔 출력·게이트 종료 코드 보호
skills/humanize-korean/scripts/build_quick_rules.py     # taxonomy 기반 quick rules 생성
skills/humanize-korean/scripts/build_diagnosis_rules.py # taxonomy 기반 진단 인덱스 생성
skills/humanize-korean/scripts/verify_gates.py          # 4축 구조 수렴 게이트
skills/humanize-korean/scripts/verify_change_rate.py    # 하위 호환 문자율 게이트
skills/humanize-korean/scripts/reassemble_chunks.py     # 손실 없는 청크 재조립
skills/humanize-korean/scripts/validate_stage_artifacts.py # 단계 산출물·표면 보존 검증
skills/humanize-korean/scripts/update_execution_state.py # Hermes 역할 완료 provenance
skills/humanize-korean/scripts/check_package_contents.py # 릴리즈 후보 필수 파일 검사
skills/humanize-korean/tests/                           # 지표·경로·청킹·골든 회귀 테스트
```

## 설치

권장 설치 방법은 Hermes tap을 등록한 뒤 설치하는 방식입니다.

```bash
hermes skills tap add andrea9292/im-not-ai-hermes
hermes skills install andrea9292/im-not-ai-hermes/skills/humanize-korean --category writing --yes
```

설치 전 내용을 확인하려면 다음 명령을 사용합니다.

```bash
hermes skills inspect andrea9292/im-not-ai-hermes/skills/humanize-korean
```

설치 내용을 현재 Hermes 세션에 반영하려면 새 세션을 시작하거나 다음 명령을 실행합니다.

```text
/reload-skills
/skill humanize-korean
```

Tap을 추가하지 않고 직접 설치할 수도 있습니다.

```bash
hermes skills install andrea9292/im-not-ai-hermes/skills/humanize-korean --category writing --yes
```

Hub 설치가 어려운 환경에서는 수동 복사를 사용할 수 있습니다.

```bash
git clone https://github.com/andrea9292/im-not-ai-hermes.git
mkdir -p "$HOME/.hermes/skills/writing"
cp -R im-not-ai-hermes/skills/humanize-korean "$HOME/.hermes/skills/writing/humanize-korean"
```

특정 Hermes profile에 설치하려면 profile별 `skills` 디렉터리에 복사합니다.

```bash
PROFILE=<profile-name>
mkdir -p "$HOME/.hermes/profiles/$PROFILE/skills/writing"
cp -R im-not-ai-hermes/skills/humanize-korean "$HOME/.hermes/profiles/$PROFILE/skills/writing/humanize-korean"
```

Raw `SKILL.md` URL 설치는 권장하지 않습니다. 이 스킬은 `references/`와 `scripts/` 파일을 함께 사용합니다. 따라서 단일 파일 설치 방식에서는 필요한 참고 파일이 빠질 수 있습니다.

## 사용법

Hermes에서 자연어로 요청합니다.

```text
humanize-korean으로 이 글의 번역투와 기계적으로 느껴지는 표현을 줄여줘:

[다듬을 한국어 초안]
```

예시 요청은 다음과 같습니다.

```text
기계적으로 느껴지는 표현만 보수적으로 줄여줘.
번역투와 피동 표현을 중심으로 봐줘.
내용은 바꾸지 말고 문장 리듬만 자연스럽게 다듬어줘.
이 보고서 문체는 유지하면서 기계적인 연결어를 줄여줘.
긴 글이라 정밀하게 검토해줘.
```

## 세 가지 경로

v2.3 포트는 `route_hint`와 사용자 요청에 따라 작업 강도를 나눕니다.

| 경로 | 기본 처리 | 대상 |
|---|---|---|
| `light` | monolith subagent 1회 | 이미 잘 쓴 글, 기계적 신호가 적은 글 |
| `standard` | diagnostician → monolith subagent | 보통의 AI 초안과 혼합형 글 |
| `heavy` | diagnostician → monolith/필요 시 청크 병렬 → finalizer subagent | 중증 패턴, 정밀 요청, 검증 증적이 필요한 글 |

입력 길이만으로 경로를 바꾸지 않습니다. `strict`는 fresh-context 3역할을 강제하지만 청킹을 강제하지 않습니다. Heavy에서도 단일 child가 안정적으로 처리하기 어려운 장문이거나 사용자가 청킹을 요청한 경우에만 `--chunk`를 쓰며, 실제 body chunk가 2개 이상일 때만 청크별 윤문과 재조립을 사용합니다.

Hermes에서는 원본의 Claude Code agent 등록 방식과 `model: opus` 라우팅을 실행하지 않습니다. 대신 upstream의 런타임 3역할을 `references/runtime-agents/`의 역할 계약과 Hermes `delegate_task`로 보존합니다. 경로별 subagent 호출은 실행 계약이며, main agent는 오케스트레이션·결정적 스크립트·산출물 검증·최종 채택을 맡습니다.

## 산출물 기대값

인라인 텍스트를 다듬을 때는 보통 다음 항목을 반환합니다.

- 다듬은 본문
- 주요 변경 요약
- 의미 보존이나 사람 검토가 필요한 부분

파일 작업에서는 원본을 보존하고 별도 출력 파일을 만드는 방식을 선호합니다. 필요할 경우 `final.md` 끝에 다음과 같은 숨은 요약 블록을 둘 수 있습니다.

```html
<!-- HUMANIZE-SUMMARY v2.3
run_id: ...
metrics:
  char_in: ...
  char_out: ...
  change_rate_claim: ...
  change_rate_actual: ...
  gate_exit: 0|1|2
  grade: A|B|C|D
categories:
  - id: C-11
    before: ...
    after: ...
self_check:
  preserved_names_numbers_quotes: pass
  genre_register: pass
  over_polish: pass
-->
```

`change_rate_actual`과 통합 `gate_exit`은 child가 확정하지 않고, 부모가 `verify_gates.py --stamp-summary`로 기록합니다. `gate_exit`은 문자율뿐 아니라 S1 목표 달성, C-8 전멸, golden/수치 주입 검사까지 반영합니다.

`heavy` 또는 `--strict` 파일 작업은 `00_execution.json`, `00_metrics.json` 또는 `00_metrics.error`, `01_input.txt`, `02_diagnosis.md`, `final_pre_finalize.md`, `final.md`, `09_finalize.json`이 모두 존재하고 단계 검증기를 통과해야 완료로 봅니다. 여러 body chunk를 사용했다면 `chunk_manifest.json`, manifest가 지정한 청크 윤문본, `03_reassembly_report.json`도 필요합니다. 결정적 validator는 파일·스키마와 구조·수치·인용·코드·각주의 표면 보존을 검사하며, 주체 귀속·범위·판단 강도 같은 의미 보존은 fresh-context finalizer가 원문과 직접 대조합니다. `delegate_task`를 사용할 수 없는 환경에서 main agent가 대신 처리했다면 이를 upstream-equivalent strict라고 부르지 않고 degraded fallback으로 명시합니다.

## 입력 위생 처리

`prepare_monolith_input.py`는 metrics·route·청크 해시를 계산하기 전에 실행 디렉터리의 `01_input.txt`를 같은 기준선으로 정리합니다. 기본 처리는 한글 NFD→NFC 결합, 제로폭·BOM·소프트하이픈·bidi·태그 제어문자 제거, NBSP 계열 공백과 줄바꿈·줄 끝 공백 정리입니다. 이모지 결합자, 전각공백, 반복 빈 줄은 기본적으로 보존합니다.

실제로 바뀐 경우에만 `00_sanitize.json` 보고서를 남깁니다. 원문 바이트를 그대로 유지해야 하면 `--no-sanitize`를 사용합니다. 이 기능은 맞춤법 교정이나 AI 워터마크 제거가 아니라, 눈에 보이지 않는 문자 차이 때문에 검색·글자수·변경률 게이트가 어긋나는 것을 막는 결정적 전처리입니다.

## 선택 지표

정량 지표는 파일 기반 검토에서 보조 신호로 쓸 수 있습니다. 지표 도구는 표준 라이브러리만 사용하며, `prepare_monolith_input.py`는 `route_hint`도 함께 기록합니다.

다음 예제는 저장소 루트에서 실행합니다.

```bash
SKILL_ROOT="$PWD/skills/humanize-korean"
python "$SKILL_ROOT/scripts/prepare_monolith_input.py" --text "분석할 한국어 원문" --genre essay
python "$SKILL_ROOT/references/metrics_v2.py" --input _workspace/2026-05-25-001/01_input.txt --genre essay --output _workspace/2026-05-25-001/00_metrics_v2.json
python "$SKILL_ROOT/scripts/verify_gates.py" --before 원문.md --after 윤문본.md --stamp-summary
python "$SKILL_ROOT/scripts/validate_stage_artifacts.py" --run-dir _workspace/2026-05-25-001 --stage all --strict
```

상대 입력·출력 경로와 자동 `_workspace/`는 현재 작업 디렉터리를 기준으로
해석합니다. 설치된 skill package 안에는 작업 결과를 쓰지 않습니다.

정량값과 경로 권고는 판정기가 아니라 참고 신호입니다. 변경률은 실제 전후 파일을 비교한 결정적 검증값으로 사용하되, 최종 문장 판단은 의미 보존, 장르 적합성, 문장 맥락, 사용자의 목적을 기준으로 합니다.

## 윤문 대상에서 제외할 것

다음 항목은 원칙적으로 보존합니다.

- 수치, 단위, 날짜
- 인명, 기관명, 제품명, 모델명
- 큰따옴표 안의 직접 인용
- 법률, 규정, 표준 문구
- 학술 개념어와 업계 표준 약어
- 사용자가 의도적으로 반복한 표현

## 원본과 다른 점

원본 `epoko77-ai/im-not-ai`는 Claude Code 구조를 사용합니다.

```text
.claude/skills/humanize-korean/
.claude/agents/*.md
.claude/commands/humanize.md
.claude/commands/humanize-redo.md
```

이 Hermes 포트는 taxonomy, quick rules, rewriting playbook, metrics, scholarship reference를 보존하되, Claude Code 전용 실행 개념을 Hermes 스킬 구조에 맞게 조정합니다.

- Claude Code의 `Agent`, `TeamCreate`, `TeamDelete`를 직접 사용하지 않습니다.
- `/humanize`, `/humanize-redo` 같은 Claude Code slash command를 제공하지 않습니다.
- upstream 런타임 역할은 Hermes `delegate_task`와 패키지된 역할 계약으로 변환합니다.
- subagent의 파일 작성 주장은 main agent가 read-back과 결정적 검증기로 확인합니다.
- 설치 경로는 Hermes tap-friendly 구조인 `skills/humanize-korean/`를 사용합니다.

자세한 출처와 파일 매핑은 [`SOURCE.md`](./SOURCE.md)를 참고합니다.

## 문서

- [`SOURCE.md`](./SOURCE.md): 원본 기준, 파일 매핑, Hermes-specific adaptation
- [`RELEASE_NOTES.md`](./RELEASE_NOTES.md): Hermes 포트 릴리즈 노트
- [`MAINTAINING.md`](./MAINTAINING.md): 배포·검증·유지보수 체크리스트
- [`NOTICE.md`](./NOTICE.md): 원본 프로젝트와 MIT attribution

## 공개 경계

이 저장소는 범용 한국어 글쓰기 품질 개선 스킬로 유지합니다. 다음 항목은 포함하지 않습니다.

- 특정 개인의 비공개 문체
- 기관별 house style
- 공개되지 않은 프로젝트 용어
- 한 사용자에게만 맞는 로컬 workflow 가정

개인 문체 반영이 필요하면 별도 private skill, style guide, voice sample을 이 스킬 위에 조합합니다.

## 개인정보와 처리 범위

이 저장소 자체는 Hermes skill instruction, Markdown reference, Python helper script만 포함합니다. 별도 서버, telemetry endpoint, background service, 외부 API connector는 포함하지 않습니다.

다만 실제 텍스트 처리는 사용자가 실행하는 Hermes Agent와 선택한 LLM provider 설정을 따릅니다. 민감한 문서를 처리하기 전에는 현재 Hermes profile, provider, logging, memory 설정을 확인해야 합니다.

## 이용 조건

이 community port는 MIT License로 제공됩니다. 원본 `epoko77-ai/im-not-ai`의 공식 Hermes 배포판이 아니며, OpenAI Codex plugin 또는 Claude Code edition도 아닙니다.

사용자는 이 스킬을 사용할 때 자신의 기관, 학교, 출판처, 고객과 맺은 AI 사용 공개·저작권·보안 규정을 따라야 합니다.

## 라이선스

MIT. 자세한 내용은 [`LICENSE`](./LICENSE)를 참고합니다.