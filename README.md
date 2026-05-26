# im-not-ai-hermes

Experimental Hermes Agent port of the Korean AI-writing cleanup skill from [`epoko77-ai/im-not-ai`](https://github.com/epoko77-ai/im-not-ai).

This repository is a personal downstream port maintained under `andrea9292`. It is not an official upstream release and is not presented as an institutional or lab-official skill.

## What this is

`humanize-korean` is a Hermes skill for polishing Korean text that sounds AI-generated, translated, over-structured, post-edited, or mechanically formal. It focuses on Korean-specific AI tells and translationese while preserving meaning, facts, genre, register, citations, numbers, and the author’s own voice.

The goal is writing-quality improvement, not deception. The skill should not be used to misrepresent authorship, fabricate provenance, bypass academic or workplace disclosure rules, or hide material AI assistance where disclosure is required.

## Attribution

Original project: [`epoko77-ai/im-not-ai`](https://github.com/epoko77-ai/im-not-ai)

The Korean AI-tell taxonomy, quick rules, rewriting playbook, scholarship reference, baselines, and metrics utilities are derived from the original MIT-licensed project. This repository adapts that workflow for Hermes Agent and preserves attribution to the original author and contributors.

## Repository layout

This repository is laid out as a Hermes tap-friendly skill source. The skill package lives under `skills/humanize-korean/` so Hermes can discover it through `hermes skills tap add`.

```text
skills/humanize-korean/SKILL.md                         # Hermes skill entry point
skills/humanize-korean/references/quick-rules.md        # Fast-path rules
skills/humanize-korean/references/ai-tell-taxonomy.md   # Full taxonomy
skills/humanize-korean/references/rewriting-playbook.md # Detailed rewriting recipes
skills/humanize-korean/references/scholarship.md        # Scholarship notes
skills/humanize-korean/references/metrics.py            # Optional v1 metrics helper
skills/humanize-korean/references/metrics_v2.py         # Optional v2 post-editese metrics helper
skills/humanize-korean/scripts/prepare_monolith_input.py# Optional file-workflow helper
skills/humanize-korean/tests/                           # Metrics/helper tests
```

## Install for Hermes

Recommended tap-based install:

```bash
hermes skills tap add andrea9292/im-not-ai-hermes
hermes skills install andrea9292/im-not-ai-hermes/skills/humanize-korean --category writing --yes
```

You can inspect the skill before installing:

```bash
hermes skills inspect andrea9292/im-not-ai-hermes/skills/humanize-korean
```

After installing, start a new Hermes session or reload skills, then load `humanize-korean`.

```text
/reload-skills
/skill humanize-korean
```

Direct install without a tap also works:

```bash
hermes skills install andrea9292/im-not-ai-hermes/skills/humanize-korean --category writing --yes
```

Manual copy fallback, if hub installation is unavailable:

```bash
git clone https://github.com/andrea9292/im-not-ai-hermes.git
mkdir -p "$HOME/.hermes/skills/writing"
cp -R im-not-ai-hermes/skills/humanize-korean "$HOME/.hermes/skills/writing/humanize-korean"
```

For a named Hermes profile, for example `writer`:

```bash
mkdir -p "$HOME/.hermes/profiles/writer/skills/writing"
cp -R im-not-ai-hermes/skills/humanize-korean "$HOME/.hermes/profiles/writer/skills/writing/humanize-korean"
```

Avoid raw `SKILL.md` URL installation for this skill. URL installs are single-file oriented and may not preserve the required `references/` and `scripts/` files.

## Optional metrics

The metrics helpers use the Python standard library only. From the skill package directory:

```bash
cd skills/humanize-korean
python scripts/prepare_monolith_input.py --text "분석할 한국어 원문" --genre essay
python references/metrics_v2.py --input _workspace/2026-05-25-001/01_input.txt --genre essay --output _workspace/2026-05-25-001/00_metrics_v2.json
```

Metrics are signals, not verdicts. Human review remains necessary for meaning preservation, genre fit, and ethical use.

## Public boundary

This repository is intended to stay general-purpose. Do not add a specific person’s private writing style, institutional house style, unpublished project vocabulary, or local-only workflow assumptions. Personal voice matching belongs in a separate private skill or style guide layered on top.

## License

MIT. See `LICENSE`.
