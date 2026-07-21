# AGENTS.md

이 문서는 `im-not-ai-hermes` 저장소에서 작업하는 Hermes, Claude Code, Codex 및 기타 에이전트가 따라야 할 프로젝트 운영 계약이다. 기능 설명의 기준은 `skills/humanize-korean/SKILL.md`이며, 이 문서는 작업 범위·승인·검증·Git 운영 원칙을 정한다.

## 1. 기본 원칙

- 사용자와의 대화는 한국어 존댓말 해요체로 한다.
- 한 번에 하나의 독립된 문제만 조사·수정한다.
- 현재 승인받은 문제와 무관한 정리, 리팩터링, 기능 추가를 끼워 넣지 않는다.
- 다음 문제로 자동 진행하지 않는다. 현재 문제의 결과를 보고한 뒤 멈춘다.
- 더 엄격하거나 완전해 보인다는 이유만으로 복잡도를 늘리지 않는다.
- 실제 재현 사례, 명시적 사용자 요구, 고정 upstream 계약 중 하나로 필요성이 입증된 변경만 제안한다.
- 모르면 추측하지 않는다. 코드·테스트·문서·고정 upstream을 직접 확인한다.

## 2. 승인과 범위 통제

### 2.1 승인의 의미

- 사용자가 구현할 문제 하나를 명시적으로 선택하면 그 문제에 한해 수정 승인이 주어진다.
- `검토해 줘`, `문제를 찾아 줘`, `리뷰해 줘`는 기본적으로 읽기 전용 요청이다.
- reviewer나 subagent의 결과는 제안이며 수정 승인이 아니다.
- 심각도 `High`, `Critical`, `blocking` 표시는 우선순위 의견일 뿐 자동 구현 명령이 아니다.

### 2.2 수정 전에 알릴 내용

파일을 수정하기 전에 다음을 짧게 밝힌다.

1. 재현되거나 확인된 문제
2. 수정이 필요한 이유
3. 수정할 파일과 범위
4. 최소 수정안
5. 예상되는 복잡도나 호환성 영향

정책, schema, 실행 경로, validator 책임 범위, 공개 API를 바꾸는 경우에는 사용자의 명시적 선택을 먼저 받는다.

### 2.3 범위가 커질 때

작업 중 다음 상황이 생기면 수정 범위를 넓히지 말고 멈춰 보고한다.

- 처음 설명하지 않은 파일까지 수정해야 함
- 독립된 두 번째 문제가 발견됨
- upstream 문서·코드·테스트가 서로 모순됨
- 둘 이상의 정책 선택지가 있음
- 새 schema나 마이그레이션이 필요함
- 실제 재현 없이 추측해야 함
- 한 문제를 고치기 위해 unrelated refactor가 필요함

## 3. Reviewer와 subagent 운영

- 리뷰 subagent는 기본적으로 읽기 전용이다. 파일 수정과 외부 side effect를 금지한다.
- 구현 subagent는 사용자가 승인한 한 문제와 지정된 출력만 다룬다.
- 여러 reviewer를 병렬 호출하더라도 결과를 하나의 구현 묶음으로 자동 변환하지 않는다.
- reviewer 결과는 `필수`, `선택`, `비권장`으로 분류해 사용자에게 설명한다.
- subagent의 완료 보고는 self-report다. 부모 agent가 실제 파일을 다시 읽고 검증해야 완료로 인정한다.
- dependent runtime role은 순서대로 실행한다. 완료 이벤트를 받기 전에 다음 단계를 시작하지 않는다.
- 사용자가 승인하지 않은 후속 문제를 새 subagent에 맡기지 않는다.

## 4. Upstream과 Hermes 포트 경계

- 고정 upstream 출처와 버전은 `SOURCE.md` 및 `skills/humanize-korean/references/hermes-port-notes.md`를 따른다.
- upstream의 taxonomy, quick rules, 변경률 기준, 역할 분리를 우선 보존한다.
- Claude Code 전용 agent 등록, slash command, model routing을 Hermes에서 그대로 실행한다고 가정하지 않는다.
- Hermes 포트 차이는 Hermes 공식 확장 지점과 `delegate_task` 계약 안에서 최소화한다.
- upstream 내부에 모순이 있으면 임의로 한쪽을 선택하지 않는다. 근거와 선택지를 사용자에게 보고한다.
- hypothetical edge case를 이유로 upstream보다 큰 실행 시스템을 만들지 않는다.

## 5. Humanize-korean 역할 경계

### 5.1 Runtime roles

- **Diagnostician**: 장르·레지스터·지배 패턴·보존 지침을 진단한다. 본문을 윤문하지 않는다.
- **Monolith**: 승인된 경로와 진단 범위 안에서 실제 윤문을 수행한다. 범용 문자열 치환으로 대체하지 않는다.
- **Finalizer**: 원문·진단·윤문본을 직접 대조하고 문제 구간만 국소 보정한다. 전체 재작성하지 않는다.
- **Parent agent**: 경로 선택, 입력 준비, 역할 dispatch, 산출물 read-back, 결정적 검증, 변경률 gate, 최종 채택을 담당한다.

### 5.2 Validator와 finalizer

- Deterministic validator는 필수 파일, JSON schema, 구조와 표면 보존 토큰을 검사한다.
- 수치·인용·코드·각주의 존재와 순서 같은 결정 가능한 항목을 검증한다.
- 주체 귀속, 의미 범위, 인과, 조건, 판단 강도는 fresh-context finalizer가 원문과 대조한다.
- 정규식 validator를 의미 분석기로 확대하지 않는다.
- validator 통과를 의미 보존 전체의 증명이라고 표현하지 않는다.

### 5.3 경로 계약

- `light`: monolith 1회
- `standard`: diagnostician → monolith
- `standard` finalizer 승급: `SKILL.md`에 명시된 조건이 있을 때만 실행
- `heavy` 또는 explicit `strict`: diagnostician → monolith 1회 또는 승인된 chunk batch → finalizer
- 입력 길이만으로 route를 변경하지 않는다.
- route 선택과 chunk 선택을 분리한다.
- 실제 body chunk가 두 개 이상일 때만 청크 병렬·재조립 경로를 사용한다.
- strict에서 delegation이 불가능하면 upstream-equivalent라고 가장하지 않는다.

## 6. 최소 수정 원칙

- 한 문제를 해결하는 데 필요한 가장 작은 변경을 우선한다.
- 기존 함수·schema·파일로 해결할 수 있으면 새 계층을 추가하지 않는다.
- 공통화는 실제 중복이 반복해서 확인된 뒤에만 한다.
- 의미상 모호한 Markdown 문법을 정규식 추측으로 과도하게 분류하지 않는다.
- Markdown edge case는 실제 실패 fixture가 있을 때 한 건씩 고친다.
- 기존 사용자 문서와 공개 계약을 깨는 변경은 호환성 영향을 먼저 설명한다.
- private style, 개인 경로, 실제 비공개 원문을 public fixture나 문서에 넣지 않는다.

## 7. 테스트와 검증

수정 후 다음 순서를 따른다.

1. 저장소에 이미 있는 관련 테스트를 먼저 찾는다.
2. 수정 문제와 직접 관련된 테스트를 실행한다.
3. 저장소 루트에서 전체 pytest를 실행한다.
4. `git diff --check`를 실행한다.
5. 패키지 변경이면 package contents와 Git archive 경계를 검사한다.
6. 테스트가 저장소를 변경하지 않았는지 `git status --short`로 확인한다.
7. 실제 통과·실패·skip 수와 exit code를 그대로 보고한다.

기본 명령:

```bash
python3 -m pytest -q
python3 skills/humanize-korean/scripts/build_quick_rules.py --check
python3 skills/humanize-korean/scripts/check_package_contents.py
git diff --check
git status --short
```

릴리즈 후보이거나 Python 호환성을 바꾼 경우에만 Python 3.11 stdlib suite와 compile 검사를 추가한다.

```bash
python3.11 -m unittest discover -s skills/humanize-korean/tests -p 'test_*.py'
python3 -m compileall -q skills/humanize-korean
```

테스트가 통과해도 변경 필요성이나 범위 승인을 대신하지 않는다.

## 8. Git 운영

- 하나의 독립된 문제는 하나의 독립된 커밋으로 남긴다.
- 승인받은 문제 외의 정리나 수정은 같은 커밋에 섞지 않는다.
- 커밋 전 변경 파일 목록과 diff 범위를 확인한다.
- 사용자 요청 없이 push, merge, release, tag 생성을 하지 않는다.
- 파괴적 변경, 파일 삭제, 산출물 덮어쓰기와 이동은 별도 승인을 받는다.
- 테스트나 빌드가 실패하면 성공한 것처럼 커밋·보고하지 않는다.

## 9. 보고 형식

작업 완료 보고에는 다음을 포함한다.

- 해결한 문제 한 가지
- 변경 파일
- 핵심 변경 내용
- 실행한 관련 테스트와 전체 테스트 결과
- working tree 상태
- 생성한 커밋이 있다면 commit hash
- 남은 문제는 자동 처리하지 말고 별도 후보로만 제시

## 10. 금지 사항

- 리뷰 결과를 사용자 승인으로 간주하지 않는다.
- 여러 독립 문제를 한꺼번에 구현하지 않는다.
- 테스트 통과를 제품 범위 승인으로 간주하지 않는다.
- subagent self-report만으로 파일 생성·수정 성공을 주장하지 않는다.
- 의미 보존을 정규식 하나로 해결했다고 주장하지 않는다.
- 실행하지 않은 테스트나 명령의 결과를 추정하지 않는다.
- 사용자 승인 없이 다음 작업으로 넘어가지 않는다.
