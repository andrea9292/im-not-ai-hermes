# im-not-ai-hermes

`im-not-ai-hermes`는 [`epoko77-ai/im-not-ai`](https://github.com/epoko77-ai/im-not-ai)를 Hermes Agent에서 사용할 수 있도록 옮겨 만든 한국어 글쓰기 품질 개선 스킬이다.

이 저장소는 `andrea9292`가 관리하는 개인 downstream 포트다. 원본 프로젝트의 공식 배포판이 아니며, 특정 기관이나 연구소의 공식 배포물처럼 소개하지 않는다.

## 무엇을 하는 스킬인가

`humanize-korean`은 한국어 초안에서 AI 생성문처럼 읽히는 반복 표현, 번역투, 기계번역 후편집투, 과도하게 정돈된 문장 구조, 반복적인 연결어와 결론 표현을 줄이기 위한 Hermes 스킬이다.

목표는 작성자를 지우거나 작성 과정을 감추는 데 있지 않다. 의미, 사실, 장르, 문체 수준, 인용, 수치, 고유명사, 기술 용어를 보존하면서 한국어 문장의 리듬과 표현을 더 자연스럽게 다듬는다.

저작권, 학업, 업무, 출판, 연구 윤리상 AI 사용 공개가 필요한 상황에서는 이 스킬을 공개 의무를 피하는 용도로 사용해서는 안 된다.

## 상태

| 항목 | 내용 |
|---|---|
| Hermes skill name | `humanize-korean` |
| Repository | `andrea9292/im-not-ai-hermes` |
| Package path | `skills/humanize-korean/` |
| Hermes port version | `2.0.0-hermes.1` |
| Original project | `epoko77-ai/im-not-ai` |
| Original baseline | v2.0.0-era, upstream commit `8071726`까지 반영 |
| License | MIT |
| Distribution | Hermes tap-friendly skill source |

## 버전 정책

이 포트의 버전은 원본 버전과 Hermes 포트 패치 번호를 함께 표기한다.

```text
2.0.0-hermes.1
```

이 버전 표기의 의미는 다음과 같다.

- `2.0.0`: 원본 `epoko77-ai/im-not-ai`의 v2.0.0 계열 taxonomy, quick rules, metrics, scholarship reference를 기준으로 한다.
- `hermes.1`: Hermes Agent용 설치 구조, frontmatter, 작업 지시, 경로 처리, tap 배포 방식을 반영한 첫 번째 Hermes 포트다.

원본이 새 버전으로 올라가면, 원본 변경분을 검토한 뒤 `2.1.0-hermes.1`처럼 원본 버전과 Hermes 포트 번호를 함께 갱신한다.

## 왜 한국어 특화인가

한국어 AI 문체는 영어권 humanizer가 다루는 일반적인 과잉 수사와 달리, 영한 번역투와 한국어 문장 리듬 문제로 드러나는 경우가 많다.

예를 들면 다음과 같다.

| 기계적으로 느껴지는 표현 | 더 자연스러운 방향 |
|---|---|
| AI 기술을 통해 효율을 높일 수 있다 | AI로 효율을 높인다 |
| 이에 있어서 중요한 점은 | 여기서 중요한 건 |
| 시스템에 의해 생성된 결과 | 시스템이 만든 결과 |
| 결론적으로 이는 시사하는 바가 크다 | 문맥에 따라 삭제하거나 구체화 |

이 스킬은 이런 표현을 무조건 삭제하지 않는다. 장르와 맥락에 맞을 때는 보존하고, 반복되거나 번역투로 읽히는 경우에만 필요한 부분을 다듬는다.

## 4대 원칙

1. **의미 보존** — 사실, 주장, 수치, 고유명사, 날짜, 직접 인용, 법률·기술 용어를 바꾸지 않는다.
2. **근거 기반 수정** — 감으로 전체를 다시 쓰지 않고, 확인 가능한 AI 문체·번역투 신호를 중심으로 고친다.
3. **장르와 격식 유지** — 보고서는 보고서답게, 칼럼은 칼럼답게, 공지는 공지답게 유지한다.
4. **과윤문 금지** — 매끈하지만 개성이 없는 글, 지나치게 문학적인 글, 저자 목소리가 사라진 글로 만들지 않는다.

## 저장소 구조

이 저장소는 Hermes tap source로 사용할 수 있도록 `skills/` 아래에 스킬 패키지를 둔다.

```text
skills/humanize-korean/SKILL.md                         # Hermes 스킬 진입점
skills/humanize-korean/references/quick-rules.md        # 빠른 윤문용 핵심 규칙
skills/humanize-korean/references/ai-tell-taxonomy.md   # 전체 분류 체계
skills/humanize-korean/references/rewriting-playbook.md # 카테고리별 윤문 처방
skills/humanize-korean/references/scholarship.md        # 번역투·후편집투 관련 근거 메모
skills/humanize-korean/references/metrics.py            # v1.6 계열 정량 지표 보조 도구
skills/humanize-korean/references/metrics_v2.py         # v2.0 후편집투·간섭 지표 보조 도구
skills/humanize-korean/scripts/prepare_monolith_input.py# 파일 작업용 입력 준비 스크립트
skills/humanize-korean/tests/                           # 지표 도구 회귀 테스트
```

## 설치

권장 설치 방법은 Hermes tap을 등록한 뒤 설치하는 것이다.

```bash
hermes skills tap add andrea9292/im-not-ai-hermes
hermes skills install andrea9292/im-not-ai-hermes/skills/humanize-korean --category writing --yes
```

설치 전 내용을 확인하려면 다음 명령을 사용한다.

```bash
hermes skills inspect andrea9292/im-not-ai-hermes/skills/humanize-korean
```

설치 내용을 현재 Hermes 세션에 반영하려면 새 세션을 시작하거나 다음 명령을 실행한다.

```text
/reload-skills
/skill humanize-korean
```

Tap을 추가하지 않고 직접 설치할 수도 있다.

```bash
hermes skills install andrea9292/im-not-ai-hermes/skills/humanize-korean --category writing --yes
```

Hub 설치가 어려운 환경에서는 수동 복사를 사용할 수 있다.

```bash
git clone https://github.com/andrea9292/im-not-ai-hermes.git
mkdir -p "$HOME/.hermes/skills/writing"
cp -R im-not-ai-hermes/skills/humanize-korean "$HOME/.hermes/skills/writing/humanize-korean"
```

특정 Hermes profile에 설치하려면 profile별 `skills` 디렉터리에 복사한다.

```bash
mkdir -p "$HOME/.hermes/profiles/writer/skills/writing"
cp -R im-not-ai-hermes/skills/humanize-korean "$HOME/.hermes/profiles/writer/skills/writing/humanize-korean"
```

Raw `SKILL.md` URL 설치는 권장하지 않는다. 이 스킬은 `references/`와 `scripts/` 파일을 함께 사용한다. 따라서 단일 파일 설치 방식에서는 필요한 참고 파일이 빠질 수 있다.

## 사용법

Hermes에서 자연어로 요청한다.

```text
humanize-korean으로 이 글의 번역투와 기계적으로 느껴지는 표현을 줄여줘:

[다듬을 한국어 초안]
```

예시 요청은 다음과 같다.

```text
기계적으로 느껴지는 표현만 보수적으로 줄여줘.
번역투와 피동 표현을 중심으로 봐줘.
내용은 바꾸지 말고 문장 리듬만 자연스럽게 다듬어줘.
이 보고서 문체는 유지하면서 기계적인 연결어를 줄여줘.
긴 글이라 정밀하게 검토해줘.
```

## 빠른 경로와 정밀 경로

기본은 빠른 경로다. 짧거나 중간 길이의 글에서는 `quick-rules.md`와 핵심 분류 체계를 중심으로 읽고, 의미 보존을 우선하면서 문장 단위로 다듬는다.

정밀 경로는 다음 상황에서 사용한다.

- 사용자가 정밀 검토를 요청한 경우
- 긴 글이거나 게시·제출 전 검토인 경우
- 첫 윤문 결과가 여전히 기계적으로 느껴지는 경우
- 변경 전후의 근거와 카테고리별 설명이 필요한 경우

Hermes에서는 원본의 고정된 5-role runtime을 그대로 실행하지 않는다. 대신 `SKILL.md`에 적힌 Hermes workflow를 따르고, 필요하면 `delegate_task` 같은 Hermes 도구로 탐지, 윤문, 의미 보존 검토를 분리할 수 있다.

## 산출물 기대값

인라인 텍스트를 다듬을 때는 보통 다음 항목을 반환한다.

- 다듬은 본문
- 주요 변경 요약
- 의미 보존이나 사람 검토가 필요한 부분

파일 작업에서는 원본을 보존하고 별도 출력 파일을 만드는 방식을 선호한다. 필요할 경우 `final.md` 끝에 다음과 같은 숨은 요약 블록을 둘 수 있다.

```html
<!-- HUMANIZE-SUMMARY
metrics:
  change_rate: ...
  grade: A|B|C|D
  categories: [A-7, C-11, D-1]
self_check:
  preserved_names_numbers_quotes: pass
  genre_register: pass
  over_polish: pass
notes:
  - ...
-->
```

## 선택 지표

정량 지표는 긴 글이나 파일 기반 검토에서 보조 신호로 쓸 수 있다. 지표 도구는 표준 라이브러리만 사용한다.

```bash
cd skills/humanize-korean
python scripts/prepare_monolith_input.py --text "분석할 한국어 원문" --genre essay
python references/metrics_v2.py --input _workspace/2026-05-25-001/01_input.txt --genre essay --output _workspace/2026-05-25-001/00_metrics_v2.json
```

정량값은 판정기가 아니라 참고 신호다. 최종 판단은 의미 보존, 장르 적합성, 문장 맥락, 사용자의 목적을 기준으로 한다.

## 윤문 대상에서 제외할 것

다음 항목은 원칙적으로 보존한다.

- 수치, 단위, 날짜
- 인명, 기관명, 제품명, 모델명
- 큰따옴표 안의 직접 인용
- 법률, 규정, 표준 문구
- 학술 개념어와 업계 표준 약어
- 사용자가 의도적으로 반복한 표현

## 원본과 다른 점

원본 `epoko77-ai/im-not-ai`는 Claude Code 구조를 사용한다.

```text
.claude/skills/humanize-korean/
.claude/agents/*.md
.claude/commands/humanize.md
.claude/commands/humanize-redo.md
```

이 Hermes 포트는 taxonomy, quick rules, rewriting playbook, metrics, scholarship reference를 보존하되, Claude Code 전용 실행 개념을 Hermes 스킬 구조에 맞게 조정한다.

- `Agent`, `TeamCreate`, `TeamDelete`를 사용하지 않는다.
- `/humanize`, `/humanize-redo` 같은 Claude Code slash command를 제공하지 않는다.
- Hermes의 `skill_view`, file tools, terminal tools, 선택적 `delegate_task`에 맞게 설명한다.
- 설치 경로는 Hermes tap-friendly 구조인 `skills/humanize-korean/`를 사용한다.

자세한 출처와 파일 매핑은 [`SOURCE.md`](./SOURCE.md)를 참고한다.

## 문서

- [`SOURCE.md`](./SOURCE.md): 원본 기준, 파일 매핑, Hermes-specific adaptation
- [`RELEASE_NOTES.md`](./RELEASE_NOTES.md): Hermes 포트 릴리즈 노트
- [`MAINTAINING.md`](./MAINTAINING.md): 배포·검증·유지보수 체크리스트
- [`NOTICE.md`](./NOTICE.md): 원본 프로젝트와 MIT attribution

## 공개 경계

이 저장소는 범용 한국어 글쓰기 품질 개선 스킬로 유지한다. 다음 항목은 포함하지 않는다.

- 특정 개인의 비공개 문체
- 기관별 house style
- 공개되지 않은 프로젝트 용어
- 한 사용자에게만 맞는 로컬 workflow 가정

개인 문체 반영이 필요하면 별도 private skill, style guide, voice sample을 이 스킬 위에 조합한다.

## 개인정보와 처리 범위

이 저장소 자체는 Hermes skill instruction, Markdown reference, Python helper script만 포함한다. 별도 서버, telemetry endpoint, background service, 외부 API connector는 포함하지 않는다.

다만 실제 텍스트 처리는 사용자가 실행하는 Hermes Agent와 선택한 LLM provider 설정을 따른다. 민감한 문서를 처리하기 전에는 현재 Hermes profile, provider, logging, memory 설정을 확인해야 한다.

## 이용 조건

이 community port는 MIT License로 제공된다. 원본 `epoko77-ai/im-not-ai`의 공식 Hermes 배포판이 아니며, OpenAI Codex plugin 또는 Claude Code edition도 아니다.

사용자는 이 스킬을 사용할 때 자신의 기관, 학교, 출판처, 고객과 맺은 AI 사용 공개·저작권·보안 규정을 따라야 한다.

## 라이선스

MIT. 자세한 내용은 [`LICENSE`](./LICENSE)를 참고한다.
