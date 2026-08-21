# im-not-ai-hermes 유지보수 체크리스트

이 문서는 `im-not-ai-hermes`를 공개 Hermes skill source로 유지보수할 때 참고하는 체크리스트입니다.

## 1. 일반 원칙

- 원본 `epoko77-ai/im-not-ai`의 MIT attribution을 보존합니다.
- public skill에는 개인 문체, 기관별 house style, 비공개 프로젝트 어휘를 넣지 않습니다.
- “공개 의무를 피하는 도구”가 아니라 “한국어 글쓰기 품질 개선 도구”로 설명합니다.
- 원본 Claude Code 구조를 Hermes runtime으로 오해하게 만들지 않습니다.
- 원본의 역할 분리는 Hermes `delegate_task`와 참조 프롬프트로 옮기되 Claude 전용 agent 등록·모델 라우팅은 복제하지 않습니다.
- 변경 후에는 README, SOURCE, RELEASE_NOTES, NOTICE의 정합성을 확인합니다.

## 2. 새 원본 버전 반영 절차

1. 원본 release/tag/commit을 확인합니다.
2. 변경된 파일을 분류합니다.
   - taxonomy
   - quick rules
   - rewriting playbook
   - scholarship reference
   - metrics/baseline
   - scripts/tests
   - runtime agent role contracts
   - README 또는 운영 정책
3. Hermes 포트에 필요한 파일만 반영합니다.
4. Claude Code 전용 요소는 Hermes workflow에 맞게 조정하거나 제외합니다.
5. `SOURCE.md`에 upstream commit, sync date, file mapping 변경을 기록합니다.
6. `RELEASE_NOTES.md`에 새 Hermes port version을 기록합니다.
7. taxonomy를 바꾸면 `build_quick_rules.py`로 생성물을 갱신합니다.

## 3. 배포 전 검증

### Git 상태

```bash
git status --short --branch
git diff --stat
```

### SKILL.md frontmatter 확인

```bash
python3 - <<'PY'
from pathlib import Path
import re, yaml
p = Path('skills/humanize-korean/SKILL.md')
content = p.read_text(encoding='utf-8')
assert content.startswith('---')
m = re.search(r'
---\s*
', content[3:])
assert m, 'frontmatter closing delimiter missing'
fm = yaml.safe_load(content[3:m.start()+3])
assert fm['name'] == 'humanize-korean'
assert 'description' in fm and len(fm['description']) <= 1024
assert len(content) <= 100000
print('frontmatter_ok', fm.get('version'))
PY
```

### 테스트

```bash
python3 -m pytest skills/humanize-korean/tests -q
python3 skills/humanize-korean/scripts/build_quick_rules.py --check
python3 skills/humanize-korean/scripts/build_diagnosis_rules.py --check
python3 skills/humanize-korean/scripts/check_package_contents.py
```

새 runtime role을 바꾸면 `test_validate_stage_artifacts.py`의 orchestration 계약과 prompt 패키징 검사를 함께 갱신합니다. strict 실행 결과는 다음 명령으로 별도 확인합니다.

```bash
python3 skills/humanize-korean/scripts/validate_stage_artifacts.py \
  --run-dir <run-dir> --stage all --strict
```

### CI 확인

GitHub Actions는 Python 3.11·3.12에서 전체 테스트, quick-rules·diagnosis-rules 동기화, package contents와 compile 검사를 수행합니다.

### Hermes inspect 확인

```bash
hermes skills inspect andrea9292/im-not-ai-hermes/skills/humanize-korean
```

### 후보 working tree 임시 설치 테스트

```bash
tmp=$(mktemp -d)
mkdir -p "$tmp/skills/writing"
cp -R skills/humanize-korean "$tmp/skills/writing/humanize-korean"
python3 "$tmp/skills/writing/humanize-korean/scripts/check_package_contents.py"
HERMES_HOME="$tmp" hermes skills list --source local | tee "$tmp/skills-list.txt"
python3 -c 'from pathlib import Path; import sys; text=Path(sys.argv[1]).read_text(); assert "humanize-korean" in text, text' "$tmp/skills-list.txt"
rm -rf "$tmp"
```

이 절차는 아직 공개되지 않은 candidate working tree 자체를 검사합니다. GitHub tap을 다시 설치하면 공개 `main`만 검증하게 되므로 릴리즈 후보 파일 누락을 잡을 수 없습니다. `hermes skills inspect`는 현재 로컬 절대 경로를 source identifier로 받지 않으므로, 공식 수동 설치 구조와 `skills list --source local` discovery를 사용합니다.

## 4. 공개 전 문구 점검

임시 표기와 공개 저장소에 맞지 않는 내부 브랜딩·로컬 경로가 남아 있지 않은지 확인합니다.

```bash
rg 'TODO|TBD|PLACEHOLDER' .
rg '/Users/|/private/|/tmp/' .
```

두 번째 검색은 예시 코드나 유지보수 문서에서 의도적으로 언급한 경로까지 잡을 수 있으므로, 실제 비공개 경로, 개인정보, 공식 배포물처럼 보이게 하는 표현인지 문맥을 확인합니다.

허용되는 표현과 금지되는 표현을 구분합니다.

| 구분 | 권장 | 피함 |
|---|---|---|
| 목적 | 한국어 글쓰기 품질 개선 | 공개 의무 회피 |
| 작업 | 번역투·후편집투 완화 | 판정 결과 보장 |
| 범위 | 의미 보존 윤문 | 작성 과정 은폐 |
| 소유 | community downstream port | 공식 배포물처럼 보이는 표현 |

## 5. 커밋과 push

```bash
git add README.md SOURCE.md RELEASE_NOTES.md MAINTAINING.md NOTICE.md skills/humanize-korean
git commit -m "docs: improve Korean user documentation"
git push
```

## 6. 설치본 갱신

별도 프로필에 설치된 hub skill을 갱신하려면 다음을 사용합니다.

```bash
PROFILE=<profile-name>
hermes --profile "$PROFILE" skills check
```

필요하면 명시적으로 다시 설치합니다.

```bash
hermes --profile "$PROFILE" skills tap add andrea9292/im-not-ai-hermes
hermes --profile "$PROFILE" skills install andrea9292/im-not-ai-hermes/skills/humanize-korean --category writing --yes
```

기존 설치본을 직접 수정했다면 갱신 전에 별도로 백업합니다. 공개 패키지는 사용자별 수정본이나 추가 파일의 자동 병합을 보장하지 않습니다.
