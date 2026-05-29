# im-not-ai-hermes 유지보수 체크리스트

이 문서는 `im-not-ai-hermes`를 공개 Hermes skill source로 유지보수할 때 참고하는 체크리스트다.

## 1. 일반 원칙

- 원본 `epoko77-ai/im-not-ai`의 MIT attribution을 보존한다.
- public skill에는 개인 문체, 기관별 house style, 비공개 프로젝트 어휘를 넣지 않는다.
- “공개 의무를 피하는 도구”가 아니라 “한국어 글쓰기 품질 개선 도구”로 설명한다.
- 원본 Claude Code 구조를 Hermes runtime으로 오해하게 만들지 않는다.
- 변경 후에는 README, SOURCE, RELEASE_NOTES, NOTICE의 정합성을 확인한다.

## 2. 새 원본 버전 반영 절차

1. 원본 release/tag/commit을 확인한다.
2. 변경된 파일을 분류한다.
   - taxonomy
   - quick rules
   - rewriting playbook
   - scholarship reference
   - metrics/baseline
   - scripts/tests
   - README 또는 운영 정책
3. Hermes 포트에 필요한 파일만 반영한다.
4. Claude Code 전용 요소는 Hermes workflow에 맞게 조정하거나 제외한다.
5. `SOURCE.md`에 upstream commit, sync date, file mapping 변경을 기록한다.
6. `RELEASE_NOTES.md`에 새 Hermes port version을 기록한다.

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
```

### Hermes inspect 확인

```bash
hermes skills inspect andrea9292/im-not-ai-hermes/skills/humanize-korean
```

### 임시 HERMES_HOME 설치 테스트

```bash
tmp=/Users/Andrea/Documents/hermes/tmp/im-not-ai-hermes-install-test-$$
rm -rf "$tmp"
mkdir -p "$tmp"
HERMES_HOME="$tmp" hermes skills tap add andrea9292/im-not-ai-hermes
HERMES_HOME="$tmp" hermes skills install andrea9292/im-not-ai-hermes/skills/humanize-korean --category writing --yes
find "$tmp/skills/writing/humanize-korean" -maxdepth 3 -type f | sort
rm -rf "$tmp"
```

macOS의 `/var`와 `/private/var` symlink 정규화 때문에 `mktemp` 아래 임시 홈에서는 Hermes installer의 path 검증이 경고를 낼 수 있다. 이 경우 `/Users/Andrea/Documents/hermes/tmp` 아래 임시 디렉터리를 사용한다.

## 4. 공개 전 문구 점검

임시 표기와 공개 저장소에 맞지 않는 내부 브랜딩·로컬 경로가 남아 있지 않은지 확인한다.

```bash
rg 'TODO|TBD|PLACEHOLDER' .
rg '/Users/|/private/|/tmp/' .
```

두 번째 검색은 예시 코드나 유지보수 문서에서 의도적으로 언급한 경로까지 잡을 수 있으므로, 실제 비공개 경로, 개인정보, 공식 배포물처럼 보이게 하는 표현인지 문맥을 확인한다.

허용되는 표현과 금지되는 표현을 구분한다.

| 구분 | 권장 | 피함 |
|---|---|---|
| 목적 | 한국어 글쓰기 품질 개선 | 공개 의무 회피 |
| 작업 | 번역투·후편집투 완화 | 판정 결과 보장 |
| 범위 | 의미 보존 윤문 | 작성 과정 은폐 |
| 소유 | personal downstream port | 공식 배포물처럼 보이는 표현 |

## 5. 커밋과 push

```bash
git add README.md SOURCE.md RELEASE_NOTES.md MAINTAINING.md NOTICE.md skills/humanize-korean
git commit -m "docs: improve Korean user documentation"
git push
```

## 6. 설치본 갱신

writer profile 등에 설치된 hub skill을 갱신하려면 다음을 사용한다.

```bash
hermes --profile writer skills update
```

필요하면 명시적으로 다시 설치한다.

```bash
hermes --profile writer skills tap add andrea9292/im-not-ai-hermes
hermes --profile writer skills install andrea9292/im-not-ai-hermes/skills/humanize-korean --category writing --yes
```

기존 로컬 스킬이 있는 profile에 덮어쓸 때는 먼저 백업한다.

```bash
tar -czf /Users/Andrea/Documents/hermes/output/$(date +%F)_writer-humanize-korean-backup.tar.gz   -C "$HOME/.hermes/profiles/writer/skills/writing" humanize-korean
```
