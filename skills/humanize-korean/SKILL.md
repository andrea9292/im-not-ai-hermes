---
name: humanize-korean
description: Use when polishing Korean text that sounds AI-generated, translated, over-structured, post-edited, or mechanically formal. Detect and reduce Korean-specific AI tells, translationese, metric-backed post-editese signals, and template-like rhythm while preserving meaning, facts, genre, register, citations, numbers, and the author's own voice.
version: 2.2.0-hermes.2
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

This Hermes port does not register or invoke Claude Code-only `.claude/agents`, `Agent`, `TeamCreate`, `TeamDelete`, `model: opus`, or slash commands such as `/humanize` and `/humanize-redo`. It preserves the upstream role separation with Hermes-native `delegate_task` calls and packaged runtime-role prompts. The parent Hermes agent orchestrates the run, executes deterministic scripts, verifies every child artifact, and alone decides whether a result may be adopted.

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
- `scripts/validate_stage_artifacts.py`: Validates diagnosis, rewrite, and strict/finalize artifacts plus deterministic surface-preservation invariants. Semantic attribution, scope, and judgment strength remain the fresh-context finalizer's responsibility.
- `scripts/update_execution_state.py`: Records parent-verified Hermes delegation completions and final gate provenance for strict runs.
- `scripts/check_package_contents.py`: Fails release-candidate validation if a required runtime role, script, or regression test is missing.
- `references/runtime-agents/diagnostician.md`: Hermes `delegate_task` role contract for dominant-pattern diagnosis.
- `references/runtime-agents/monolith.md`: Hermes `delegate_task` role contract for targeted rewriting and self-checking.
- `references/runtime-agents/finalizer.md`: Hermes `delegate_task` role contract for direct original-versus-rewrite review and local correction.
- `references/web-service-spec.md`: Optional product/web-service expansion note. Do not load for ordinary text polishing.
- `references/hermes-port-notes.md`: Porting notes and public-boundary reminders.

Resolve the absolute installed skill directory from the skill activation/loader output before running a helper. `SKILL_ROOT` below is notation, not an automatically exported environment variable. In a shell, assign it explicitly, for example `SKILL_ROOT="<absolute-installed-skill-directory>"`. Call `skill_view(name='humanize-korean', file_path='references/quick-rules.md')` when a child cannot access the same filesystem path or when concrete rule lookup is cheaper through progressive disclosure. If linked files are unavailable through the skill loader, use the local path inside this repository.

## Relationship to `humanizer`

Hermes may also provide a broader `humanizer` skill. Treat that skill as the general cross-language option for reducing generic AI phrasing. Use `humanize-korean` when the input is Korean and the important problems are Korean-specific: translationese particles and predicates, mechanical Korean connectors, padded formal nouns, Korean sentence rhythm, Korean register drift, Hangul/English term balance, and post-editese interference.

Do not stack both skills mechanically. If both are relevant, let this skill govern Korean-specific edits and use the broader humanizer only for general naturalness checks that do not conflict with the preservation rules here.

## Route-Aware Workflow

Use one of three paths. User instructions override metrics: `정밀`, `엄격`, or `strict` forces `heavy`; `가볍게` or `빠르게만` forces `light`. Otherwise follow the shim's `route_hint`. Input length alone never changes the route in upstream v2.2. `heavy` may ask the shim for chunks when a single reliable rewrite call would exceed the practical context boundary; explicit `strict` forces the fresh-context three-role path, not chunking.

| Route | Default work | Use when |
|---|---|---|
| `light` | one conservative monolith child | well-written text with few lexical or passive-form tells |
| `standard` | diagnostician child, then monolith child | ordinary AI draft or mixed signals |
| `heavy` | diagnostician child, monolith child or chunk batch, deterministic gate, then finalizer child | dense AI patterns, explicit strict request, or evidence-sensitive publication work |

### 1. Identify the boundary

- Determine inline text versus file workflow, genre, register, formatting constraints, and requested strength.
- Preserve meaning-bearing structure, headings as independent lines, tables, footnotes, links, frontmatter, and direct quotations. Do not flatten useful lists or checklists. A mechanical list may become prose only when an upstream C-2/C-9 rule clearly applies, the genre supports it, and no item or ordering information is lost. Explicit user preservation constraints override that option.
- Do not infer a private house style from unrelated local files. A separate user-provided style guide may be layered on top.

### 2. Load the smallest rule set

- Load `references/quick-rules.md` for every normal rewrite.
- Load `references/ai-tell-taxonomy.md` for `standard`/`heavy`, ambiguous cases, or category-level reporting.
- Load `references/rewriting-playbook.md` only when the quick prescription is insufficient.
- Load `references/scholarship.md` only when auditing or citing the taxonomy's translation-studies basis.

### 3. Compute route signals when files are available

For a file workflow or repeatable diagnostic, run:

```bash
SKILL_ROOT="<absolute-installed-skill-directory>"
python "$SKILL_ROOT/scripts/prepare_monolith_input.py" \
  --run-dir <run-dir> --genre <genre>
```

`SKILL_ROOT` is the absolute installed package path. Run from the user's working
directory: relative `--run-dir`, `--diagnosis`, and automatic `_workspace/`
paths resolve against the current working directory, never the installed skill.

Read `route_hint` from `00_metrics.json`. If metrics fail or `route_hint` is absent, use `standard`. Treat the route as an advisory, not a detector verdict.

Inline text follows the same upstream Phase 1. Materialize it as `01_input.txt` in a run directory (or use the shim's `--text` entry point), run the shim, and then follow `route_hint`. The user may still request the revised text inline at delivery time; that does not remove the file-backed runtime contract required by delegated children.

After selecting the route, show one compact status line before dispatch:

```text
humanize-korean 2.2.0-hermes.2 — 경로: {light|standard|heavy} ({route_hint|사용자 지정}) / 역할: {monolith | diagnostician→monolith | diagnostician→monolith[N]→finalizer} / run_id: {run_id}
```

### 4. Hermes-native delegation contract

The role call count is part of the route contract, not an optional optimization. When `delegate_task` is available, use leaf children and the packaged role prompts:

- `light`: monolith ×1
- `standard`: diagnostician ×1, then monolith ×1
- `heavy` / explicit `strict`: diagnostician ×1, monolith ×1 or chunk batch ×N, then finalizer ×1

Do not replace these fresh-context roles with one parent-agent rewrite merely because the parent can perform the prose edit. The external diagnosis and finalizer perspectives are the quality mechanism inherited from upstream.

Each child starts without conversation history. Its `goal` and `context` must therefore include:

- the absolute path of the appropriate `references/runtime-agents/*.md` contract; if the child cannot access it, tell the child to load the same file with `skill_view`
- all absolute input and output paths; rule/taxonomy references may use `skill_view` only when the installed filesystem path is unavailable
- route, mode, genre, strength, `run_id`, and user preservation constraints
- an instruction to read the role contract first, write only the declared output, and return a compact artifact summary
- an instruction not to ask the user, modify the source file, call another agent, or infer missing context

Top-level Hermes delegation is asynchronous. Dispatch one dependent stage, continue unrelated work if useful, and wait for its completion event to re-enter the session before starting the next stage. For a chunk fan-out, send one `delegate_task(tasks=[...])` batch and do not reassemble until its consolidated completion event reports every task. Do not poll or claim completion early.

Child summaries are self-reports. After every completion, the parent must read or stat the declared artifact and run the applicable stage validator. A claimed write that cannot be read back is a failed stage.

For `heavy`/strict, initialize `00_execution.json` after route selection with `scripts/update_execution_state.py init`. After the parent has read and validated a role output, call `record` with the actual Hermes delegation or batch ID and that output path. Record every chunk task separately, using its shared batch ID plus task index. The change-rate gate writes `change_rate`; after the finalizer verdict, call `finish --status completed` or `finish --status hold_and_report`. Never record a child merely because it was dispatched.

**Delegation fallback**

- If `delegate_task` is unavailable, `light` may run in the parent with `degraded_in_process_fallback: true` in the summary.
- `standard` may use an in-process diagnosis pass followed by a separate rewrite pass only after disclosing the degraded path.
- `heavy` / explicit `strict` must never silently fall back. On an interrupted or unknown outcome, inspect and validate the declared artifact before retrying; if no valid artifact exists, use an attempt-specific output path so two attempts cannot race on one file. If delegation remains unavailable, stop as `delegation_unavailable`. A user-approved in-process result is a separately labelled degraded non-strict run, never upstream-equivalent strict and never `hold_and_report` (which is reserved for a finalizer verdict).

### 5. Execute the selected route

**Light**

1. Dispatch one leaf child using `references/runtime-agents/monolith.md`, `mode=document`, and `strength=보수`.
2. Verify `final.md`, its single `HUMANIZE-SUMMARY` block, and preservation invariants.
3. If little needs changing, report that rather than manufacturing edits.

**Standard**

1. Dispatch one leaf child using `references/runtime-agents/diagnostician.md` to write `02_diagnosis.md`.
2. Read back and validate the diagnosis, then rerun the shim with `--diagnosis`.
3. Dispatch one leaf child using `references/runtime-agents/monolith.md`, `mode=document`, targeting the diagnosed 3–6 patterns.
4. Read back and validate `final.md`, then apply the deterministic change-rate gate.
5. Run a finalizer only under the upstream escalation table: gate exit 1, two or more failed monolith self-checks, or an explicit request for verification evidence. Otherwise standard ends after the two required role calls. When escalation applies, copy the current `final.md` to `final_pre_finalize.md` before dispatch, then call `references/runtime-agents/finalizer.md` with the original, diagnosis, rewritten, backup, and `09_finalize.json` report paths. After completion, read back and validate both `final.md` and `09_finalize.json`, rerun the deterministic change-rate gate with `--stamp-summary`, and apply the resulting gate and finalizer verdict. `hold_and_report` is a human-review stop and must not be reported as an adopted final result.

**Heavy / strict**

1. Dispatch and validate the diagnostician stage exactly as in `standard`.
2. Rerun the shim with `--diagnosis`. Add `--chunk` only when the document exceeds a reliable single-child context boundary or the user explicitly requests chunking. Treat the shim's small-input warning as a reason to keep one monolith call. Route selection and chunk selection are separate decisions.
3. Without a chunk manifest, dispatch one monolith child with `mode=document`, `input_path=01_input_with_metrics.txt`, and `output_path=final.md`. With a deliberate chunk manifest, if `body_chunk_count` is one, use `mode=document` and the manifest-declared `input_file`; if it is two or more, create one `delegate_task(tasks=[...])` batch whose leaf tasks each use `mode=chunk` and distinct manifest-declared `input_file` and `rewritten_file` paths.
4. Run at most four chunk children concurrently for upstream parity and respect any lower Hermes runtime cap. Split larger manifests into sequential batches. Children must never write the same file.
5. After the consolidated batch completion, verify every rewritten chunk. Then run `scripts/reassemble_chunks.py --run-dir <run-dir> --strict --output final.md`. For a single-document path, validate `final.md` directly.
6. Run `scripts/verify_change_rate.py`. Exit 1 triggers finalizer review. Exit 2 forbids adoption: restore the last safe version and rerun monolith conservatively once; a second exit 2 stops as `hold_and_report`. Exit 3 must be fixed and rerun, never skipped.
7. Copy the current `final.md` to `final_pre_finalize.md` before finalization.
8. Dispatch one leaf child using `references/runtime-agents/finalizer.md`. It must directly compare `01_input.txt`, `final.md`, and `02_diagnosis.md`, perform only local corrections, and write `09_finalize.json`.
9. Read back `final.md` and `09_finalize.json`, rerun the change-rate gate, stamp the parent-measured value into the summary/provenance, then run `scripts/validate_stage_artifacts.py --stage all --strict`. `hold_and_report` is a safe human-review stop, not a successfully adopted final result.

The parent must not substitute a bulk string-replacement script for the monolith role. Mechanical replacement is especially unsafe for `할 수 있다`, passive forms, formal nouns, and connective endings.

### 6. Apply the deterministic gate for file output

```bash
python "$SKILL_ROOT/scripts/verify_change_rate.py" \
  --before <original> --after <final> --stamp-summary
```

For strict/heavy, also pass `--execution-state <run-dir>/00_execution.json` so the same parent-measured gate result is recorded in provenance.

- exit `0`, below 30%: proceed
- exit `1`, 30–50%: warn about possible over-editing and perform fidelity review
- exit `2`, 50% or more: do not adopt the rewrite; roll back or re-run conservatively once
- exit `3`: fix the input problem; never report an unverified rate

`--ignore-markup` may be used only as a secondary measurement when heading/list conversion inflates the rate. If it changes the interpretation, report both measurements.

### 7. Return the result

- Inline work: revised text plus a compact change summary.
- File work: output path, route, deterministic change rate, changed areas, and any unresolved review issue.
- Do not silently overwrite an important source file.

## Standalone Metrics Workflow

The route shim and `00_metrics.json`/`00_metrics.error` are part of upstream Phase 1 for every delegated route. The additional `metrics_v2.py` command below is optional and is useful when the user asks for a separate diagnostic report.

Run from the user's working directory with `SKILL_ROOT` set to the absolute
installed package path:

```bash
SKILL_ROOT="<absolute-installed-skill-directory>"
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
SKILL_ROOT="<absolute-installed-skill-directory>"
# Confirm the generated quick rules match taxonomy metadata.
python "$SKILL_ROOT/scripts/build_quick_rules.py" --check

# Prepare a normal route-aware input bundle.
python "$SKILL_ROOT/scripts/prepare_monolith_input.py" --run-dir <run-dir> --genre essay

# Heavy-only and only when a single reliable child would exceed the practical
# context boundary: ask the shim for a lossless chunk layout.
python "$SKILL_ROOT/scripts/prepare_monolith_input.py" --run-dir <run-dir> --genre essay --diagnosis <run-dir>/02_diagnosis.md --chunk
python "$SKILL_ROOT/scripts/reassemble_chunks.py" --run-dir <run-dir> --strict --output final.md

# Measure the adopted rewrite rather than trusting an LLM estimate.
python "$SKILL_ROOT/scripts/verify_change_rate.py" --before <original> --after <final> --stamp-summary

# Validate stage contracts and deterministic surface-preservation invariants.
python "$SKILL_ROOT/scripts/validate_stage_artifacts.py" \
  --run-dir <run-dir> --stage all --strict

# Add --preserve-lists only when the user explicitly required list/checklist preservation.
```

The helper scripts are standard-library only. Metrics and route hints support editorial attention; they do not establish whether a text was written by AI.

## File Workflow Output

When writing files, prefer this pattern:

1. Preserve the original input file unless the user explicitly asks for in-place edits.
2. Write the edited text to `final.md` or a clearly named output file.
3. For file workflows, append a hidden HTML summary block to `final.md` instead of requiring a second `summary.md` file:

```html
<!-- HUMANIZE-SUMMARY v2.2
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
notes:
  - ...
-->
```

The hidden block keeps rendered Markdown clean while preserving machine-readable review metadata. If the user wants a separate summary file, create one explicitly.

Strict/heavy file work is complete only when these artifacts exist and validate:

- `01_input.txt`
- `00_metrics.json` or `00_metrics.error`
- `00_execution.json` (Hermes parent-verified delegation provenance)
- `02_diagnosis.md`
- `final_pre_finalize.md`
- `final.md`
- `09_finalize.json`

Chunked runs additionally require `chunk_manifest.json`, every manifest-declared rewritten body chunk, and a successfully verified reassembly. Missing `02_diagnosis.md` or `09_finalize.json` means the run is not upstream-equivalent strict, regardless of the final prose quality.

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

10. Copying Claude Code runtime mechanics instead of translating their intent.
   - Do not depend on `Agent`, `TeamCreate`, `TeamDelete`, `/humanize`, or `.claude/agents`. Preserve their role separation with Hermes `delegate_task`, packaged role contracts, isolated outputs, and parent-side verification.

11. Treating delegation as cosmetic.
   - A single parent pass followed by a self-review is not the strict three-stage path. Diagnosis and finalization must run in fresh child contexts when delegation is available.

12. Trusting a child summary without reading the artifact.
   - Verify each declared file and run the stage validator. Subagent completion text is not proof of a successful write.

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
- [ ] The selected route used its required runtime roles, or a degraded fallback is explicitly recorded.
- [ ] Every child artifact was read back and validated by the parent.
- [ ] Heavy/strict produced a parseable `09_finalize.json` with an accepted verdict.

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
