# Hermes port notes

## Source

- Original repository: `epoko77-ai/im-not-ai`
- Original license: MIT
- Original Claude Code skill: `.claude/skills/humanize-korean/`
- Ported upstream baseline: `upstream/main` at v2.0.0-era commits through `8071726` (2026-05-07)

This Hermes port preserves attribution to the original author and contributors. The taxonomy, quick rules, rewriting playbook, scholarship reference, and metrics utilities are adapted from the original project; this directory changes the operating model so the workflow can be used as a Hermes Agent skill.

## What changed in the Hermes port

The original project assumes Claude Code features:

- `.claude/agents/*.md`
- `.claude/commands/*.md`
- `Agent` calls
- `TeamCreate` / `TeamDelete`
- Claude model routing such as `model: opus`
- root-level helper scripts and tests

Hermes does not treat those files or concepts as executable skill machinery. The Hermes port therefore changes the operation model:

- The main Hermes agent performs the fast path directly.
- `references/quick-rules.md` is the default rule source.
- `references/metrics.py` and `references/metrics_v2.py` are optional local preprocessors.
- `scripts/prepare_monolith_input.py` resolves references from this skill directory and creates `_workspace/` under the caller's cwd.
- Strict multi-pass detection, rewriting, fidelity audit, and naturalness review are described as a Hermes workflow rather than Claude Code agent calls.
- Personal voice matching is intentionally excluded from the public skill.

## v2.0 port contents

- `references/ai-tell-taxonomy.md`: full v2.0 taxonomy, including Korean translation-studies additions.
- `references/quick-rules.md`: fast-path S1/S2 rules updated through v2.0.
- `references/rewriting-playbook.md`: category-level rewrite recipes.
- `references/scholarship.md`: external scholarship SSOT.
- `references/metrics.py`: v1.6 KatFish/LREAD-style quantitative metrics.
- `references/metrics_v2.py`: v2.0 post-editese and translation-interference metric layer.
- `references/baseline.json`, `references/baseline_v2.json`: metric baselines/placeholders.
- `scripts/prepare_monolith_input.py`: optional metrics-prep shim for file workflows.
- `tests/`: local regression tests for the metrics modules.

## Public distribution boundary

This skill should stay general-purpose. Do not add:

- a specific person's voice profile
- private style-guide rules
- organization-specific house style
- unpublished project vocabulary
- writing preferences that only make sense for one user

If a user wants their own writing style preserved, combine this skill with a separate local skill, style guide, or voice sample.

## Suggested future work

- Add sample input/output fixtures for Korean AI-tell patterns.
- Add repository/tap installation instructions once the preferred public Hermes distribution workflow is settled. Until then, document manual directory-copy installation so `references/`, `scripts/`, and `tests/` are preserved.
- Consider a strict-mode helper prompt using Hermes `delegate_task`, but keep fast mode as the default.
