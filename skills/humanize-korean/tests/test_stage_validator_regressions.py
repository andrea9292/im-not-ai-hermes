"""Regression counterexamples for the production stage validator.

Keep these cases generic and tied to upstream preservation rules. Do not add
fixtures copied from a private or publication-specific document.
"""

from __future__ import annotations

import importlib.util
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "scripts" / "validate_stage_artifacts.py"
SPEC = importlib.util.spec_from_file_location("stage_validator_regressions", SCRIPT)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VALIDATOR
SPEC.loader.exec_module(VALIDATOR)


def _codes(original: str, rewritten: str, **kwargs: bool) -> set[str]:
    return {issue.code for issue in VALIDATOR._fidelity_issues(original, rewritten, **kwargs)}


class FidelityCounterexampleTests(unittest.TestCase):
    def test_order_swaps_do_not_pass_as_equal_multisets(self) -> None:
        cases = [
            ("A는 10명, B는 20명이다.", "A는 20명, B는 10명이다.", "number"),
            (
                "A는 https://example.com/a, B는 https://example.com/b를 쓴다.",
                "A는 https://example.com/b, B는 https://example.com/a를 쓴다.",
                "url",
            ),
            (
                'A는 "첫 번째 직접 인용문입니다"라고 했고 B는 "두 번째 직접 인용문입니다"라고 했다.',
                'A는 "두 번째 직접 인용문입니다"라고 했고 B는 "첫 번째 직접 인용문입니다"라고 했다.',
                "quote",
            ),
        ]
        for original, rewritten, expected in cases:
            with self.subTest(expected=expected):
                self.assertIn(expected, _codes(original, rewritten))

    def test_short_emphasis_quotes_are_not_frozen_as_direct_quotes(self) -> None:
        self.assertNotIn("quote", _codes('"AI" 기술을 쓴다.', '"기계" 기술을 쓴다.'))

    def test_short_quote_with_speech_context_is_protected(self) -> None:
        self.assertIn("quote", _codes("그는 “안 돼”라고 말했다.", "그는 “좋아”라고 말했다."))

    def test_korean_url_particles_and_unicode_paths_are_parsed(self) -> None:
        text = "https://example.com/a를 보고 https://example.com/한글경로에서 확인했다."
        self.assertNotIn("url", _codes(text, text))

    def test_multiline_markdown_footnote_definition_is_protected(self) -> None:
        original = "대상은 10명이다.[^a]\n\n[^a]: 첫 줄\n    둘째 줄\n"
        changed = "대상은 10명이다.[^a]\n\n[^a]: 첫 줄\n    바뀐 둘째 줄\n"
        self.assertIn("footnote_definition", _codes(original, changed))

    def test_footnote_anchor_uses_nearby_immutable_number(self) -> None:
        original = "대상은 10명이다.[^a]\n\n비교군은 20명이다.\n\n[^a]: 출처\n"
        moved = "대상은 10명이다.\n\n비교군은 20명이다.[^a]\n\n[^a]: 출처\n"
        self.assertIn("footnote_anchor", _codes(original, moved))

    def test_lists_are_transformable_by_default_but_can_be_explicitly_preserved(self) -> None:
        original = "1. 접근성 개선\n2. 오류 수정\n"
        rewritten = "접근성을 개선하고 오류를 수정한다.\n"
        default_codes = _codes(original, rewritten)
        self.assertEqual(default_codes, set())
        self.assertIn("list_structure", _codes(original, rewritten, preserve_lists=True))

    def test_existing_placeholder_or_cliche_is_not_a_new_violation(self) -> None:
        original = "TODO: 결론적으로 이 문제를 검토한다."
        self.assertNotIn("placeholder", _codes(original, original))
        self.assertNotIn("cliche_injection", _codes(original, original))
        expanded = original + " TODO: 기록적인 성과를 이뤘다."
        expanded_codes = _codes(original, expanded)
        self.assertIn("placeholder", expanded_codes)
        self.assertIn("cliche_injection", expanded_codes)


class ManifestCounterexampleTests(unittest.TestCase):
    def test_passthrough_nulls_are_valid_and_first_missing_body_output_is_caught(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)
            source = "서문\n\n본문 하나\n\n본문 둘\n"
            (run / "01_input.txt").write_text(source, encoding="utf-8")
            for index in (2, 3):
                (run / f"01_chunk_{index:02d}_input_with_metrics.txt").write_text(
                    f"본문 {index}\n", encoding="utf-8"
                )
            (run / "02_chunk_03_rewritten.txt").write_text("본문 둘\n", encoding="utf-8")
            manifest = {
                "version": 1,
                "source_file": "01_input.txt",
                "source_chars": len(source),
                "source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
                "chunk_count": 3,
                "body_chunk_count": 2,
                "passthrough_chunk_count": 1,
                "chunks": [
                    {
                        "index": 1,
                        "start": 0,
                        "end": 4,
                        "char_count": 4,
                        "passthrough": True,
                        "input_file": None,
                        "rewritten_file": None,
                    },
                    {
                        "index": 2,
                        "start": 4,
                        "end": 10,
                        "char_count": 6,
                        "passthrough": False,
                        "input_file": "01_chunk_02_input_with_metrics.txt",
                        "rewritten_file": "02_chunk_02_rewritten.txt",
                    },
                    {
                        "index": 3,
                        "start": 10,
                        "end": len(source),
                        "char_count": len(source) - 10,
                        "passthrough": False,
                        "input_file": "01_chunk_03_input_with_metrics.txt",
                        "rewritten_file": "02_chunk_03_rewritten.txt",
                    },
                ],
            }
            (run / "chunk_manifest.json").write_text(
                json.dumps(manifest, ensure_ascii=False), encoding="utf-8"
            )
            issues: list = []
            VALIDATOR._validate_chunks(run.resolve(), issues)
            codes = [issue.code for issue in issues]
            self.assertNotIn("manifest_schema", codes)
            self.assertEqual(codes.count("missing_chunk_output"), 1)

            manifest["source_sha256"] = "0" * 64
            manifest["chunks"][1]["start"] = 3
            (run / "chunk_manifest.json").write_text(
                json.dumps(manifest, ensure_ascii=False), encoding="utf-8"
            )
            corrupt: list = []
            VALIDATOR._validate_chunks(run.resolve(), corrupt)
            corrupt_codes = {issue.code for issue in corrupt}
            self.assertIn("manifest_source", corrupt_codes)
            self.assertIn("manifest_coverage", corrupt_codes)


class TaxonomyCounterexampleTests(unittest.TestCase):
    def test_hold_heading_is_not_an_active_diagnosis_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)
            taxonomy = run / "taxonomy.md"
            taxonomy.write_text(
                "### A-17. 보류 항목 (hold)\n\n### A-18. 활성 항목\n\n### A-19. 활성 항목\n",
                encoding="utf-8",
            )
            (run / "02_diagnosis.md").write_text(
                "# 진단\n\n## 장르·레지스터\n- 장르: 리포트\n\n"
                "## 지배 패턴 (겨냥 순서)\n"
                "1. **A-17** 보류\n2. **A-18** 활성\n3. **A-19** 활성\n\n"
                "## 보존 지침\n- 의미 보존\n",
                encoding="utf-8",
            )
            issues: list = []
            VALIDATOR._validate_diagnosis(run, taxonomy, issues)
            self.assertIn("diagnosis_unknown_id", {issue.code for issue in issues})


if __name__ == "__main__":
    unittest.main()
