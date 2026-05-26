---
name: humanize-korean
description: Use when polishing Korean text that sounds AI-generated, translated, over-structured, post-edited, or mechanically formal. Detect and reduce Korean-specific AI tells, translationese, metric-backed post-editese signals, and template-like rhythm while preserving meaning, facts, genre, register, citations, numbers, and the author's own voice.
version: 2.0.0-hermes.1
author: epoko77-ai, Hermes port maintained by andrea9292
license: MIT
metadata:
  hermes:
    tags: [writing, korean, editing, humanize, ai-writing, translationese, post-editese, prose]
    category: writing
    homepage: https://github.com/andrea9292/im-not-ai-hermes
    related_skills: [humanizer]
---

# Humanize Korean for Hermes

## Overview

`humanize-korean` is a Hermes-native port of the Korean AI-writing cleanup workflow from `epoko77-ai/im-not-ai`. It is for Korean prose that sounds like it came from ChatGPT, Claude, Gemini, a translation engine, or a machine-translation post-editing pipeline: translationese, mechanical connectors, inflated conclusion phrases, long left-branching relative clauses, excessive pronouns, uniform rhythm, over-neat Markdown structure, or post-editese-like normalization.

The goal is not to erase the author. The goal is to reduce Korean-specific AI tells while preserving meaning, factual claims, genre, register, field vocabulary, citations, numbers, and authorial voice. Formal Korean is not an AI tell by itself. Humanized text should not become casual, literary, opinionated, or generically smooth unless the user explicitly asks for that style.

This Hermes port intentionally avoids Claude Code-only mechanisms from the original repository. Do not assume `.claude/agents`, `Agent`, `TeamCreate`, `TeamDelete`, model routing such as `model: opus`, or slash commands such as `/humanize` and `/humanize-redo` are available. In Hermes, the main agent performs the fast path directly using this skill and its reference files. For strict review, use normal Hermes reasoning, file tools, and optional `delegate_task` subtasks with self-contained prompts.

## Upstream and Version Notes

This port incorporates upstream v2.0-era changes:

- v1.6 KatFish/LREAD-inspired quantitative metrics layer (`metrics.py`, `baseline.json`)
- v1.6.1 single-output summary pattern: prefer `final.md` with a hidden `HUMANIZE-SUMMARY` block for file workflows
- v2.0 Korean translation-studies additions: A-16, A-18, A-19, E-7 plus A-7, A-15, E-2, F-4 reinforcements
- v2.0 post-editese metric track (`metrics_v2.py`, `baseline_v2.json`)
- external scholarship SSOT (`scholarship.md`)

A-17, inanimate/abstract noun `-들`, remains a hold item in the upstream v2.0 taxonomy: it has strong scholarship anchors but no positive cases in the 2026-05-07 external wiki sample pass. Treat it as a metric/scholarship reference, not a default rewrite trigger.

## Attribution and Public Boundary

Original project: `epoko77-ai/im-not-ai`, MIT License. The Korean AI-tell taxonomy, quick rules, rewriting playbook, scholarship reference, baselines, and metrics utilities are derived from the original project. This Hermes port adapts the workflow for Hermes Agent while preserving credit to the original author and contributors.

This public skill must stay general-purpose. Do not add a specific person's private writing style, institutional house style, unpublished project vocabulary, or local-only workflow assumptions. Personal voice matching belongs in a separate local skill, style guide, or voice sample layered on top when requested.

## When to Use

Use this skill when the user asks in Korean or English to:

- remove "AI 티" from Korean text
- make Korean AI-generated prose sound more natural
- reduce ChatGPT/GPT/Claude/Gemini-like wording
- fix Korean translationese or post-edited machine-translation feel
- polish a Korean draft without changing content
- reduce mechanical bullet lists, headings, repeated connectors, or template-like structure
- review Korean prose for AI tells before publishing
- humanize Korean text while preserving meaning

Trigger examples:

- "AI 티 없애줘"
- "ChatGPT 문체 좀 지워줘"
- "한글 AI 글 사람처럼 다듬어줘"
- "번역투와 피동 표현을 줄여줘"
- "기계번역 후편집 티가 나지 않게 봐줘"
- "내용은 건드리지 말고 문체만 자연스럽게"
- "humanize Korean"

Do not use this skill as the primary method for:

- pure spelling and typo correction only
- translation between languages
- adding new evidence, examples, claims, or citations
- rewriting the argument structure from scratch
- matching a specific person's voice without a separate voice sample or style guide
- academic, legal, policy, or standards text where formulaic register is required and the user only asked for proofreading

## Core Principles

1. Preserve meaning. Do not add, remove, or reinterpret facts, claims, dates, numbers, names, citations, legal provisions, quotes, or technical terms.
2. Preserve genre. A report remains a report. A column remains a column. A formal notice remains formal.
3. Preserve register. Formal Korean is not an AI tell by itself. Remove mechanical padding, not formality.
4. Preserve authorial voice. Remove mechanical AI patterns, not the writer's stance, field vocabulary, or useful emphasis.
5. Avoid over-polishing. If the rewrite becomes too smooth, generic, literary, or uniformly polished, it has failed.
6. Make local edits before global rewrites. Prefer surgical changes tied to detectable patterns.
7. Explain material changes. If a change affects tone, structure, emphasis, or publication risk, mention it briefly.
8. Treat metrics as signals, not verdicts. Numeric scores guide attention; the final judgment is semantic, stylistic, and genre-aware.

## Reference Files

Load the smallest useful reference first.

- `references/quick-rules.md`: Fast-path S1/S2 rules. Use this by default.
- `references/ai-tell-taxonomy.md`: Full taxonomy. Use for strict review, ambiguous cases, or taxonomy-level reasoning.
- `references/rewriting-playbook.md`: Detailed rewriting recipes. Use when quick rules are not enough.
- `references/scholarship.md`: Full scholarship reference for translationese/post-editese claims. Use when citing or auditing the taxonomy.
- `references/metrics.py`: Optional v1.6 quantitative metrics. Standard-library only.
- `references/metrics_v2.py`: Optional v2.0 post-editese/interference metrics. Standard-library only.
- `references/baseline.json`, `references/baseline_v2.json`: Baselines and placeholder cells for metrics.
- `scripts/prepare_monolith_input.py`: Optional file-workflow helper that prepends a metrics block to input.
- `references/web-service-spec.md`: Optional product/web-service expansion note. Do not load for ordinary text polishing.
- `references/hermes-port-notes.md`: Porting notes and public-boundary reminders.

In Hermes, call `skill_view(name='humanize-korean', file_path='references/quick-rules.md')` when the current task requires concrete rule lookup and the reference is available in the installed skill. If linked files are not available through the skill loader, use the local file path when working inside this repository.

## Relationship to `humanizer`

Hermes may also provide a broader `humanizer` skill. Treat that skill as the general cross-language option for reducing generic AI phrasing. Use `humanize-korean` when the input is Korean and the important problems are Korean-specific: translationese particles and predicates, mechanical Korean connectors, padded formal nouns, Korean sentence rhythm, Korean register drift, Hangul/English term balance, and post-editese interference.

Do not stack both skills mechanically. If both are relevant, let this skill govern Korean-specific edits and use the broader humanizer only for general naturalness checks that do not conflict with the preservation rules here.

## Fast Path Workflow

Use the fast path for most requests, especially texts under roughly 5,000 Korean characters.

1. Identify the task boundary.
   - Is the input inline text or a file?
   - Did the user ask to preserve formatting?
   - Did the user specify genre, strength, or minimum severity?
   - Is this a direct rewrite, a review report, or both?

2. Load the rules.
   - Use `quick-rules.md` as the main reference.
   - Only load the full taxonomy, scholarship, or playbook if the text is difficult, long, publication-sensitive, or the user asks for strict review.

3. Estimate genre and register.
   - Possible genre hints: 칼럼, 블로그, 리포트, 공지, 발표문, 학술문, 정책문, 제품 문서.
   - Preserve the original level of formality unless instructed otherwise.

4. Optionally compute metrics for file workflows.
   - For longer or publication-sensitive file edits, run `scripts/prepare_monolith_input.py` or the metrics modules directly.
   - Use metrics to identify likely hotspots: comma patterns, conclusion lexicon, safe-balance lexicon, hanja nominalizers, lexical diversity, pronoun density, passive/by patterns, double particles, relative-clause nesting, progressive aspect, and interference index.
   - Do not let metrics override semantic preservation or genre judgment.

5. Scan for Korean AI tells.
   Focus first on high-impact categories:
   - A: translationese such as `~에 대해`, `~를 통해`, `~에 있어서`, `가지고 있다`, `~에 의해`, English pronoun literalism, long left-branching relative clauses, double particles
   - C: structural AI patterns such as mechanical numbering, colon headings, and connective-ending comma patterns
   - D: AI signature phrases such as `결론적으로`, `시사하는 바가 크다`, `주목할 만하다`, `본질적으로`
   - E: uniform rhythm, repeated endings, progressive-aspect overuse, honorific-register inconsistency in dialogue
   - F: redundant modifiers, abstract noun chains, hanja/English nominalization
   - G/H/I/J: hedging, repeated connectors, padded formal nouns, and visual decoration

6. Rewrite surgically.
   - Fix the strongest and most repeated patterns first.
   - Do not change terms that are domain-standard.
   - Do not flatten a writer's intentional repetition unless it reads mechanical.
   - Prefer sentence-level edits over full-paragraph replacement unless the paragraph structure itself is the AI tell.

7. Self-check.
   - Did any number, date, name, quote, citation, URL, legal term, or technical identifier change?
   - Did the genre or register drift?
   - Did the rewrite remove the author's point of view?
   - Did the rewrite add claims, examples, metaphors, or emotional color?
   - Did the rewrite become too smooth, generic, or literary?
   - Are S1 patterns still left in obvious places?

8. Return the result.
   - For inline text: show the revised text and a compact change summary.
   - For file edits: show the changed file path and diff summary. Do not silently overwrite important files.

## Optional Metrics Workflow

Metrics are optional. Use them when the text is long, when the user asks for a diagnostic report, or when a file workflow benefits from repeatable evidence.

Example commands from the repository root or any working directory:

```bash
python scripts/prepare_monolith_input.py \
  --text "분석할 한국어 원문" \
  --genre essay

python references/metrics_v2.py \
  --input _workspace/2026-05-25-001/01_input.txt \
  --genre essay \
  --output _workspace/2026-05-25-001/00_metrics_v2.json
```

The metrics CLI prints the final `risk_band` to stdout. Read the JSON file named
by `--output` for the full metric payload.
`metrics_v2.py` defaults to the sibling `references/baseline_v2.json` file when
`--baseline-v2` is omitted, and `prepare_monolith_input.py` uses that default via
`compute_all()`.

The prep script writes:

- `00_metrics.json`
- `01_input.txt`
- `01_input_with_metrics.txt`
- `00_metrics.error` only if metrics fail and the workflow gracefully degrades

For human-facing output, do not dump raw metrics unless requested. Summarize the signals that affected edits.

## Optional Strict Path

Use a stricter path when:

- the text is long, usually over 8,000 Korean characters
- the user asks for strict, careful, or multi-pass review
- the text will be published or submitted and meaning preservation is critical
- the first rewrite still feels AI-like
- the user asks for a category-level report

Strict path in Hermes:

1. Detection pass:
   - Produce findings with category ID, severity, span or excerpt, reason, and suggested fix.
   - Use `ai-tell-taxonomy.md`, and `scholarship.md` when the category depends on translation-studies claims.

2. Rewrite pass:
   - Rewrite only findings that justify intervention.
   - Track before/after examples.

3. Fidelity audit:
   - Compare original and rewrite for changed facts, claims, examples, names, numbers, dates, citations, URLs, and quotes.
   - Roll back or revise suspicious edits.

4. Naturalness review:
   - Re-scan for remaining high-severity AI tells.
   - Check for over-polishing, register drift, and loss of field vocabulary.

5. Final response:
   - Provide final text.
   - Summarize key categories changed.
   - Mention any unresolved issue that needs human judgment.

If using `delegate_task`, keep subtask prompts self-contained and require verifiable outputs: text, finding list, or file path. The parent agent must make the final judgment.

## File Workflow Output

When writing files, prefer this pattern:

1. Preserve the original input file unless the user explicitly asks for in-place edits.
2. Write the edited text to `final.md` or a clearly named output file.
3. For file workflows, append a hidden HTML summary block to `final.md` instead of requiring a second `summary.md` file:

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

The hidden block keeps rendered Markdown clean while preserving machine-readable review metadata. If the user wants a separate summary file, create one explicitly.

## Editing Strength

If the user does not specify strength, use `기본`.

- `보수`: Fix only obvious S1 patterns and repeated mechanical phrases. Best for academic, legal, official, or sensitive text.
- `기본`: Fix clear S1 and repeated S2 patterns while preserving most structure.
- `적극`: Reshape mechanical lists and paragraph rhythm more visibly, but still do not add or remove content.

Never use `적극` as an excuse to rewrite the author's argument or introduce new examples.

## What to Preserve Absolutely

Do not change:

- personal names, organization names, product names, model names
- dates, numbers, percentages, units, prices, section numbers
- citations, bibliography entries, footnote labels, URLs, DOIs
- direct quotes inside quotation marks
- legal provisions, policy names, standards, technical identifiers
- mathematical, chemical, statistical, or code notation
- established abbreviations such as LLM, GPU, API, MCP, HTML, WCAG when they are field-standard

If any of these must be changed for a real reason, stop and ask or clearly mark the issue instead of silently editing.

## Korean AI-Tell Categories

Use the quick rules for the exact pattern list. The main categories are:

| Category | Focus | Typical intervention |
|---|---|---|
| A | 번역투 | Restore natural Korean particles, predicates, agency, pronoun handling, and clause order |
| B | 영어 인용·용어 과다 | Keep standard terms, reduce unnecessary English glosses |
| C | 구조적 AI 패턴 | Reduce mechanical numbering, headings, connective-comma patterns, and template symmetry |
| D | AI 관용구 | Remove inflated or generic significance phrases |
| E | 리듬·종결어미 | Vary sentence length and endings without stylizing the text |
| F | 과도한 수식·중복 | Remove redundant modifiers and abstract noun chains |
| G | Hedging | Replace excessive hedging with appropriate certainty |
| H | 접속사 남발 | Let paragraph flow carry transitions where possible |
| I | 형식명사·의존명사 | Convert padded endings into direct statements |
| J | 시각 장식 | Reduce excessive bold, quotes, emojis, and bullets |

## Output Format

For normal inline work, use this compact format:

```text
윤문본
[revised Korean text]

주요 변경
- 번역투/피동 표현을 줄였습니다.
- 반복 접속사와 형식명사를 정리했습니다.
- 고유명사, 수치, 인용은 유지했습니다.
```

For strict review, use:

```text
윤문본
[final text]

점검 요약
| 항목 | 결과 |
|---|---|
| 의미 보존 | 통과 / 확인 필요 |
| 고유명사·수치·인용 보존 | 통과 / 확인 필요 |
| 주요 처리 범주 | A, C, D, H, I 등 |
| 과윤문 위험 | 낮음 / 보통 / 높음 |
| metric 참고 | 사용 / 미사용 |

주요 변경 예
- before → after
```

For file edits, include:

- edited file path
- whether the file was patched or rewritten
- short summary of changed areas
- whether metrics were used
- any remaining manual-review note

## Common Pitfalls

1. Treating all formality as AI style.
   - Formal Korean can be appropriate. Remove mechanical padding, not formality itself.

2. Mechanically deleting every passive form.
   - Some passive or intransitive forms are natural. Fix forms that hide agency, sound translated, or repeat mechanically.

3. Replacing domain terms with vague everyday words.
   - Keep technical, legal, academic, accessibility, policy, and product vocabulary when it is accurate.

4. Making the text more emotional or literary than the original.
   - Humanized does not mean dramatic.

5. Collapsing useful structure.
   - Lists, headings, and bullets are not automatically bad. Remove them only when decorative, repetitive, or genre-inappropriate.

6. Adding examples to make the text feel human.
   - Do not add examples, anecdotes, facts, or citations unless the user explicitly asks for content development.

7. Letting metrics become a detector verdict.
   - Metrics are evidence, not proof. Use them to focus reading, then judge the sentence in context.

8. Overwriting files without showing what changed.
   - Use targeted patches when possible and show the user the changed sections or a summary.

9. Confusing public skill behavior with private voice matching.
   - This skill is general-purpose. Specific writer style belongs in a separate skill or style guide.

10. Porting Claude Code mechanics into Hermes.
   - Do not mention or depend on `Agent`, `TeamCreate`, `TeamDelete`, `/humanize`, or `.claude/agents` in the executable Hermes workflow.

## Verification Checklist

Before finalizing, verify:

- [ ] The output is still Korean unless the user requested otherwise.
- [ ] Meaning and factual claims are unchanged.
- [ ] Names, numbers, dates, citations, URLs, and direct quotes are preserved.
- [ ] Genre and register are preserved.
- [ ] The rewrite targets identifiable AI tells.
- [ ] Metrics, if used, are treated as supporting evidence only.
- [ ] The text does not become over-polished, generic, or artificially literary.
- [ ] Any uncertain edit is explained or left for human review.

## Installation Notes

This repository is tap-friendly: the skill package lives at `skills/humanize-korean/`. Prefer Hermes hub/tap installation over raw `SKILL.md` URL installation, because this skill depends on sibling `references/` and `scripts/` files.

Recommended install:

```bash
hermes skills tap add andrea9292/im-not-ai-hermes
hermes skills install andrea9292/im-not-ai-hermes/skills/humanize-korean --category writing --yes
```

Inspect before installing:

```bash
hermes skills inspect andrea9292/im-not-ai-hermes/skills/humanize-korean
```

Direct install without adding a tap also works:

```bash
hermes skills install andrea9292/im-not-ai-hermes/skills/humanize-korean --category writing --yes
```

Manual copy fallback after cloning:

```bash
# Default Hermes home
mkdir -p "$HOME/.hermes/skills/writing"
cp -R im-not-ai-hermes/skills/humanize-korean "$HOME/.hermes/skills/writing/humanize-korean"

# Named profile
mkdir -p "$HOME/.hermes/profiles/writer/skills/writing"
cp -R im-not-ai-hermes/skills/humanize-korean "$HOME/.hermes/profiles/writer/skills/writing/humanize-korean"
```

Start a new Hermes session or reset/reload skills after installation so the skill registry can refresh.
