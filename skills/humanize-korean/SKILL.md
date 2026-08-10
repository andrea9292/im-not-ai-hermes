---
name: humanize-korean
description: Use when polishing Korean text that sounds AI-generated, translated, over-structured, post-edited, or mechanically formal. Detect and reduce Korean-specific AI tells, translationese, metric-backed post-editese signals, and template-like rhythm while preserving meaning, facts, genre, register, citations, numbers, and the author's own voice.
version: 2.2.1-hermes.1
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

This Hermes port intentionally avoids Claude Code-only mechanisms from the original repository. Do not assume `.claude/agents`, `Agent`, `TeamCreate`, `TeamDelete`, model routing such as `model: opus`, or slash commands such as `/humanize` and `/humanize-redo` are available. In Hermes, the main agent performs the route-aware workflow directly using this skill and its reference files. For heavy review, use normal Hermes reasoning, file tools, deterministic gates, and optional `delegate_task` subtasks with self-contained prompts.

## Upstream and Version Notes

This port incorporates upstream changes through v2.2.0 (`3120cb81`):

- v1.6 KatFish/LREAD-inspired quantitative metrics layer (`metrics.py`, `baseline.json`)
- v1.6.1 single-output summary pattern: prefer `final.md` with a hidden `HUMANIZE-SUMMARY` block for file workflows
- v2.0 Korean translation-studies additions: A-16, A-18, A-19, E-7 plus A-7, A-15, E-2, F-4 reinforcements
- v2.0 post-editese metric track (`metrics_v2.py`, `baseline_v2.json`)
- external scholarship SSOT (`scholarship.md`)
- v2.0.1 deterministic change-rate gate, register/structure/footnote preservation checks, and fresh-clone path fixes
- v2.1 taxonomy-to-quick-rules generation, golden regression checks, lossless chunking, and a diagnosis/rewrite/fidelity three-stage strict path
- v2.2 `route_hint` (`light` / `standard` / `heavy`) so well-written text stays on a minimal path and long text is not chunked merely because it is long
- v2.2 B-2 technical-term preservation, C-1 severity correction and academic-structure exception, and C-8 negative-positive parallelism expansion

A-17, inanimate/abstract noun `-들`, remains a hold item in upstream v2.2. Treat it as a metric/scholarship reference, not a default rewrite trigger.

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
- `references/quick-rules.header.md`, `references/quick-rules.footer.md`: Fixed templates used to generate `quick-rules.md`; edit these or the taxonomy, not the generated rule file.
- `scripts/prepare_monolith_input.py`: File-workflow helper that computes metrics, emits `route_hint`, and optionally creates lossless chunks.
- `scripts/build_quick_rules.py`: Rebuilds `quick-rules.md` from taxonomy metadata; `--check` verifies that it is current.
- `scripts/verify_change_rate.py`: Deterministic post-edit gate; below 30% passes, 30–50% warns, and 50% or more aborts adoption.
- `scripts/reassemble_chunks.py`: Lossless chunk reassembler with source-hash and size-ratio checks.
- `references/web-service-spec.md`: Optional product/web-service expansion note. Do not load for ordinary text polishing.
- `references/hermes-port-notes.md`: Porting notes and public-boundary reminders.

In Hermes, call `skill_view(name='humanize-korean', file_path='references/quick-rules.md')` when the current task requires concrete rule lookup and the reference is available in the installed skill. If linked files are not available through the skill loader, use the local file path when working inside this repository.

## Relationship to `humanizer`

Hermes may also provide a broader `humanizer` skill. Treat that skill as the general cross-language option for reducing generic AI phrasing. Use `humanize-korean` when the input is Korean and the important problems are Korean-specific: translationese particles and predicates, mechanical Korean connectors, padded formal nouns, Korean sentence rhythm, Korean register drift, Hangul/English term balance, and post-editese interference.

Do not stack both skills mechanically. If both are relevant, let this skill govern Korean-specific edits and use the broader humanizer only for general naturalness checks that do not conflict with the preservation rules here.

## Route-Aware Workflow

Use one of three paths. User instructions override metrics: `정밀`, `엄격`, or `strict` forces `heavy`; `가볍게` or `빠르게만` forces `light`. Length does not force `heavy` at or below 15,000 characters; text over 15,000 characters is an upstream-defined `heavy` signal. Even then, chunk only when the shim actually creates two or more body chunks.

| Route | Default work | Use when |
|---|---|---|
| `light` | one direct conservative rewrite | well-written text with few lexical or passive-form tells |
| `standard` | diagnosis, then one targeted rewrite | ordinary AI draft or mixed signals |
| `heavy` | diagnosis, rewrite, deterministic gate, and fidelity/final review | dense AI patterns, more than 15,000 characters, explicit strict request, or evidence-sensitive publication work |

### 1. Identify the boundary

- Determine inline text versus file workflow, genre, register, formatting constraints, and requested strength.
- Preserve headings, lists, tables, footnotes, links, frontmatter, and direct quotations unless the user explicitly asks to restructure them.
- Do not infer a private house style from unrelated local files. A separate user-provided style guide may be layered on top.

### 2. Load the smallest rule set

- Load `references/quick-rules.md` for every normal rewrite.
- Load `references/ai-tell-taxonomy.md` for `standard`/`heavy`, ambiguous cases, or category-level reporting.
- Load `references/rewriting-playbook.md` only when the quick prescription is insufficient.
- Load `references/scholarship.md` only when auditing or citing the taxonomy's translation-studies basis.

### 3. Compute route signals when files are available

For a file workflow or repeatable diagnostic, run:

```bash
python "$SKILL_ROOT/scripts/prepare_monolith_input.py" \
  --run-dir <run-dir> --genre <genre>
```

`SKILL_ROOT` is the absolute installed package path. Run from the user's working
directory: relative `--run-dir`, `--diagnosis`, and automatic `_workspace/`
paths resolve against the current working directory, never the installed skill.

Read `route_hint` from `00_metrics.json`. If metrics fail or `route_hint` is absent, use `standard`. Treat the route as an advisory, not a detector verdict.

For inline or very short work where creating files adds no value, choose conservatively from the text itself: use `light` unless clear repeated S1/S2 patterns justify `standard`. Do not claim a computed `route_hint` when the script was not run.

### 4. Execute the chosen route

**Light**

1. Rewrite directly with `quick-rules.md`, using `보수` strength.
2. Keep changes local. If little needs changing, say so rather than manufacturing edits.
3. Perform the preservation self-check before returning.

**Standard**

1. Diagnose the 3–6 dominant patterns with taxonomy IDs, genre/register, and preservation constraints.
2. Rewrite once, targeting only those dominant patterns. Do not enumerate every possible span.
3. Perform the preservation self-check. Use the deterministic change-rate gate for file output.

**Heavy**

1. Diagnose dominant patterns and explicit preservation constraints.
2. Rewrite the whole document once unless the shim actually creates two or more body chunks.
3. If `--chunk` is justified, use manifest `input_file` and `rewritten_file` names exactly, then run `scripts/reassemble_chunks.py`. Never invent chunk filenames.
4. Run `scripts/verify_change_rate.py` and compare original versus rewrite for facts, names, numbers, dates, quotes, citations, URLs, headings, footnotes, and register.
5. Correct only the suspicious passages. Do not run an unrestricted whole-document rewrite as the final review.

Optional `delegate_task` review is allowed for heavy work, but the parent Hermes agent owns the final text and must verify any returned file or claim.

### 5. Apply the deterministic gate for file output

```bash
python "$SKILL_ROOT/scripts/verify_change_rate.py" --before <original> --after <final>
```

- exit `0`, below 30%: proceed
- exit `1`, 30–50%: warn about possible over-editing and perform fidelity review
- exit `2`, 50% or more: do not adopt the rewrite; roll back or re-run conservatively once
- exit `3`: fix the input problem; never report an unverified rate

`--ignore-markup` may be used only as a secondary measurement when heading/list conversion inflates the rate. If it changes the interpretation, report both measurements.

### 6. Return the result

- Inline work: revised text plus a compact change summary.
- File work: output path, route, deterministic change rate, changed areas, and any unresolved review issue.
- Do not silently overwrite an important source file.

## Optional Metrics Workflow

Metrics are optional. Use them when the text is long, when the user asks for a diagnostic report, or when a file workflow benefits from repeatable evidence.

Run from the user's working directory with `SKILL_ROOT` set to the absolute
installed package path:

```bash
python "$SKILL_ROOT/scripts/prepare_monolith_input.py" \
  --text "분석할 한국어 원문" \
  --genre essay

python "$SKILL_ROOT/references/metrics_v2.py" \
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

## Deterministic Helper Commands

Run these from the user's working directory. Relative input/output paths resolve
against that directory; `SKILL_ROOT` points to the installed package.

```bash
# Confirm the generated quick rules match taxonomy metadata.
python "$SKILL_ROOT/scripts/build_quick_rules.py" --check

# Prepare a normal route-aware input bundle.
python "$SKILL_ROOT/scripts/prepare_monolith_input.py" --run-dir <run-dir> --genre essay

# Heavy-only: create lossless chunks when the text truly exceeds the threshold.
python "$SKILL_ROOT/scripts/prepare_monolith_input.py" --run-dir <run-dir> --genre essay --chunk
python "$SKILL_ROOT/scripts/reassemble_chunks.py" --run-dir <run-dir> --strict

# Measure the adopted rewrite rather than trusting an LLM estimate.
python "$SKILL_ROOT/scripts/verify_change_rate.py" --before <original> --after <final>
```

The helper scripts are standard-library only. Metrics and route hints support editorial attention; they do not establish whether a text was written by AI.

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

For `heavy` review, use:

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
PROFILE=<profile-name>
mkdir -p "$HOME/.hermes/profiles/$PROFILE/skills/writing"
cp -R im-not-ai-hermes/skills/humanize-korean "$HOME/.hermes/profiles/$PROFILE/skills/writing/humanize-korean"
```

Start a new Hermes session or reset/reload skills after installation so the skill registry can refresh.
