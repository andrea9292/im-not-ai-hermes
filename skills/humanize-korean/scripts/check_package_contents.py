#!/usr/bin/env python3
"""Validate source or installed humanize-korean package contents."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

RUNTIME_REQUIRED = (
    "SKILL.md",
    "references/quick-rules.md",
    "references/diagnosis-rules.md",
    "references/ai-tell-taxonomy.md",
    "references/design-notes.md",
    "references/empirical-validation.md",
    "references/runtime-agents/diagnostician.md",
    "references/runtime-agents/monolith.md",
    "references/runtime-agents/finalizer.md",
    "scripts/prepare_monolith_input.py",
    "scripts/sanitize_text.py",
    "scripts/build_diagnosis_rules.py",
    "scripts/golden_checks.py",
    "scripts/verify_gates.py",
    "scripts/verify_change_rate.py",
    "scripts/reassemble_chunks.py",
    "scripts/validate_stage_artifacts.py",
    "scripts/update_execution_state.py",
    "scripts/check_package_contents.py",
)

TEST_REQUIRED = (
    "tests/test_validate_stage_artifacts.py",
    "tests/test_diagnosis_rules_build.py",
    "tests/test_verify_gates.py",
    "tests/test_runtime_provenance.py",
    "tests/test_stage_validator_regressions.py",
    "tests/test_sanitize.py",
)

SOURCE_REQUIRED = RUNTIME_REQUIRED + TEST_REQUIRED


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skill-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="candidate skills/humanize-korean directory",
    )
    parser.add_argument("--expected-version", default="2.3.0-hermes.1")
    parser.add_argument(
        "--installed",
        action="store_true",
        help="check only files required in a Hermes-installed skill package",
    )
    args = parser.parse_args(argv)
    root = args.skill_root.resolve()
    required = RUNTIME_REQUIRED if args.installed else SOURCE_REQUIRED

    missing = [relative for relative in required if not (root / relative).is_file()]
    if missing:
        for relative in missing:
            print(f"missing: {relative}", file=sys.stderr)
        return 1

    skill = (root / "SKILL.md").read_text(encoding="utf-8")
    match = re.search(r"(?m)^version:\s*(\S+)\s*$", skill)
    actual = match.group(1) if match else None
    if actual != args.expected_version:
        print(
            f"version mismatch: expected {args.expected_version}, found {actual!r}",
            file=sys.stderr,
        )
        return 1

    print(f"package_ok version={actual} required_files={len(required)} root={root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
