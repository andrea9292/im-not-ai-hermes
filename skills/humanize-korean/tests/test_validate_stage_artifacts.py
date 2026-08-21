"""Runtime artifact and orchestration-contract tests."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = SKILL_ROOT / "scripts" / "validate_stage_artifacts.py"
SPEC = importlib.util.spec_from_file_location("validate_stage_artifacts", SCRIPT_PATH)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


ORIGINAL = """# 검토 보고서

기관은 2026년 7월 21일에 “원문 인용은 그대로 둔다”고 밝혔다. 자세한 내용은 https://example.com/a를 참고한다. `aria-label`을 확인했다.[^1]

- 첫 번째 항목
- 두 번째 항목

| 항목 | 값 |
| --- | --- |
| 표본 | 42 |

```html
<button aria-label="저장">저장</button>
```

[^1]: 원문 각주 정의.
"""

REWRITTEN_BODY = """# 검토 보고서

기관은 2026년 7월 21일 “원문 인용은 그대로 둔다”고 밝혔다. 자세한 내용은 https://example.com/a에서 확인할 수 있다. `aria-label`을 점검했다.[^1]

- 첫 항목을 확인한다.
- 둘째 항목도 확인한다.

| 항목 | 값 |
| --- | --- |
| 표본 | 42 |

```html
<button aria-label="저장">저장</button>
```

[^1]: 원문 각주 정의.
"""

SUMMARY = """

<!-- HUMANIZE-SUMMARY
run_id: test-001
metrics:
  change_rate_claim: 2.0%
  self_check: 6/6
  grade: A
-->
"""

DIAGNOSIS = """# 진단 — test-001

## 장르·레지스터
- 장르: 리포트
- 격식: 한다체

## 지배 패턴 (겨냥 순서)
1. **A-1** 번역투 — 근거
2. **C-11** 쉼표 — 근거
3. **I-4** 형식명사 — 근거

## 정량 앵커
- 없음

## 보존 지침
- 제목·수치·인용·코드·각주 보존
"""

TAXONOMY = """# taxonomy

### A-1. 번역투
### C-11. 연결어미 뒤 쉼표
### I-4. 형식명사
### D-1. 상투구
"""

FINALIZE = {
    "verdict": "accept",
    "fidelity": {"pass": True, "violations": []},
    "naturalness": {"residual": [], "over_polish": [], "malformed_rewrites": []},
    "corrections_applied": 0,
    "note": "",
}

EXECUTION = {
    "schema_version": 1,
    "run_id": "test-001",
    "requested_mode": "strict",
    "resolved_route": "heavy",
    "execution_mode": "delegated",
    "degraded": False,
    "stages": {
        "diagnostician": [
            {
                "sequence": 1,
                "status": "completed",
                "delegation_id": "deleg-d",
                "output": "02_diagnosis.md",
            }
        ],
        "monolith": [
            {
                "sequence": 2,
                "status": "completed",
                "delegation_id": "deleg-m",
                "output": "final.md",
            }
        ],
        "finalizer": [
            {
                "sequence": 3,
                "status": "completed",
                "delegation_id": "deleg-f",
                "output": "09_finalize.json",
            }
        ],
    },
    "change_rate": {"percent": 2.0, "exit_code": 0, "scope": "full"},
    "status": "completed",
}


class RunFixture:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.taxonomy = root / "taxonomy.md"
        self.taxonomy.write_text(TAXONOMY, encoding="utf-8")
        (root / "01_input.txt").write_text(ORIGINAL, encoding="utf-8")
        (root / "00_metrics.json").write_text(
            '{"route_hint": "light"}\n', encoding="utf-8"
        )
        (root / "02_diagnosis.md").write_text(DIAGNOSIS, encoding="utf-8")
        final = REWRITTEN_BODY + SUMMARY
        (root / "final_pre_finalize.md").write_text(final, encoding="utf-8")
        (root / "final.md").write_text(final, encoding="utf-8")
        (root / "09_finalize.json").write_text(
            json.dumps(FINALIZE, ensure_ascii=False), encoding="utf-8"
        )
        (root / "00_execution.json").write_text(
            json.dumps(EXECUTION, ensure_ascii=False), encoding="utf-8"
        )

    def validate(
        self,
        *,
        stage: str = "all",
        strict: bool = True,
        preserve_lists: bool = False,
    ):
        return validator.validate_run(
            self.root,
            stage=stage,
            strict=strict,
            taxonomy_path=self.taxonomy,
            preserve_lists=preserve_lists,
        )


class ValidateStageArtifactsTests(unittest.TestCase):
    def test_valid_strict_run_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = RunFixture(Path(tmp))
            issues, hold = fixture.validate()
            self.assertEqual(issues, [])
            self.assertFalse(hold)

    def test_diagnosis_requires_three_to_six_known_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = RunFixture(Path(tmp))
            bad = DIAGNOSIS.replace("3. **I-4** 형식명사 — 근거\n", "")
            (fixture.root / "02_diagnosis.md").write_text(bad, encoding="utf-8")
            issues, _ = fixture.validate(stage="diagnosis", strict=False)
            self.assertIn("diagnosis_count", {x.code for x in issues})

            unknown = DIAGNOSIS.replace("**I-4**", "**J-99**")
            (fixture.root / "02_diagnosis.md").write_text(unknown, encoding="utf-8")
            issues, _ = fixture.validate(stage="diagnosis", strict=False)
            self.assertIn("diagnosis_unknown_id", {x.code for x in issues})

    def test_rewrite_detects_protected_surface_changes(self) -> None:
        cases = {
            "heading_lost": ("# 검토 보고서", "# 접근성 검토"),
            "number": ("2026년", "2025년"),
            "quote": ("원문 인용은 그대로 둔다", "인용은 그대로 둔다"),
            "url": ("https://example.com/a", "https://example.com/b"),
            "inline_code": ("`aria-label`", "`aria-labelledby`"),
            "fenced_code": (">저장</button>", ">제출</button>"),
            "footnote_definition": ("원문 각주 정의", "바뀐 각주 정의"),
            "table_structure": ("| 표본 | 42 |", "표본은 42다."),
        }
        for expected_code, (old, new) in cases.items():
            with self.subTest(expected_code=expected_code), tempfile.TemporaryDirectory() as tmp:
                fixture = RunFixture(Path(tmp))
                text = (REWRITTEN_BODY + SUMMARY).replace(old, new)
                (fixture.root / "final.md").write_text(text, encoding="utf-8")
                issues, _ = fixture.validate(stage="rewrite", strict=False)
                self.assertIn(expected_code, {x.code for x in issues})

    def test_lists_are_only_frozen_when_explicitly_requested(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = RunFixture(Path(tmp))
            text = (REWRITTEN_BODY + SUMMARY).replace(
                "- 첫 항목을 확인한다.", "첫 항목을 확인한다."
            )
            (fixture.root / "final.md").write_text(text, encoding="utf-8")
            default_issues, _ = fixture.validate(stage="rewrite", strict=False)
            preserved_issues, _ = fixture.validate(
                stage="rewrite", strict=False, preserve_lists=True
            )
            self.assertNotIn("list_structure", {x.code for x in default_issues})
            self.assertIn("list_structure", {x.code for x in preserved_issues})

    def test_rewrite_detects_malformed_bulk_replacement(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = RunFixture(Path(tmp))
            text = (REWRITTEN_BODY + " 전달하지 못가능합니다." + SUMMARY)
            (fixture.root / "final.md").write_text(text, encoding="utf-8")
            issues, _ = fixture.validate(stage="rewrite", strict=False)
            self.assertIn("malformed_rewrite", {x.code for x in issues})

    def test_strict_requires_finalize_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = RunFixture(Path(tmp))
            (fixture.root / "09_finalize.json").unlink()
            issues, _ = fixture.validate()
            self.assertIn("missing_artifact", {x.code for x in issues})

    def test_hold_and_report_is_distinct_from_contract_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = RunFixture(Path(tmp))
            payload = dict(FINALIZE)
            payload["verdict"] = "hold_and_report"
            payload["fidelity"] = {"pass": False, "violations": [{"item": 3}]}
            (fixture.root / "09_finalize.json").write_text(
                json.dumps(payload, ensure_ascii=False), encoding="utf-8"
            )
            execution = dict(EXECUTION)
            execution["status"] = "hold_and_report"
            (fixture.root / "00_execution.json").write_text(
                json.dumps(execution, ensure_ascii=False), encoding="utf-8"
            )
            issues, hold = fixture.validate()
            self.assertEqual(issues, [])
            self.assertTrue(hold)

    def test_hold_and_report_requires_an_unresolved_reason(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = RunFixture(Path(tmp))
            payload = dict(FINALIZE)
            payload["verdict"] = "hold_and_report"
            payload["fidelity"] = {"pass": False, "violations": []}
            payload["note"] = ""
            (fixture.root / "09_finalize.json").write_text(
                json.dumps(payload, ensure_ascii=False), encoding="utf-8"
            )
            execution = dict(EXECUTION)
            execution["status"] = "hold_and_report"
            (fixture.root / "00_execution.json").write_text(
                json.dumps(execution, ensure_ascii=False), encoding="utf-8"
            )

            issues, hold = fixture.validate()

            self.assertIn("finalize_inconsistent", {x.code for x in issues})
            self.assertTrue(hold)

            payload["note"] = "원문 의미 보존 여부를 사람이 확인해야 합니다."
            (fixture.root / "09_finalize.json").write_text(
                json.dumps(payload, ensure_ascii=False), encoding="utf-8"
            )
            issues, hold = fixture.validate()
            self.assertEqual(issues, [])
            self.assertTrue(hold)

    def test_single_chunk_document_mode_does_not_require_chunk_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = RunFixture(Path(tmp))
            manifest = {
                "body_chunk_count": 1,
                "chunks": [
                    {
                        "index": 1,
                        "passthrough": False,
                        "input_file": "01_chunk_01_input_with_metrics.txt",
                        "rewritten_file": "02_chunk_01_rewritten.txt",
                    }
                ],
            }
            (fixture.root / "chunk_manifest.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )
            issues, _ = fixture.validate(stage="rewrite", strict=False)
            self.assertNotIn("missing_chunk_output", {x.code for x in issues})

    def test_manifest_declared_chunk_output_must_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = RunFixture(Path(tmp))
            manifest = {
                "body_chunk_count": 2,
                "chunks": [
                    {
                        "index": 1,
                        "passthrough": False,
                        "input_file": "01_chunk_01_input_with_metrics.txt",
                        "rewritten_file": "02_chunk_01_rewritten.txt",
                    },
                    {
                        "index": 2,
                        "passthrough": False,
                        "input_file": "01_chunk_02_input_with_metrics.txt",
                        "rewritten_file": "02_chunk_02_rewritten.txt",
                    }
                ],
            }
            (fixture.root / "chunk_manifest.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )
            issues, _ = fixture.validate(stage="rewrite", strict=False)
            self.assertIn("missing_chunk_output", {x.code for x in issues})


class OrchestrationContractTests(unittest.TestCase):
    def test_skill_requires_hermes_runtime_roles(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("version: 2.3.0-hermes.1", skill)
        self.assertNotIn(
            "references/runtime-agents/*.md",
            skill,
            "Hermes skill installers treat support-path wildcards as literal files",
        )
        self.assertIn("### 4. Hermes-native delegation contract", skill)
        self.assertIn("heavy` / explicit `strict` must never silently fall back", skill)
        self.assertIn("final_pre_finalize.md", skill)
        self.assertIn("09_finalize.json", skill)
        self.assertIn("references/diagnosis-rules.md", skill)
        self.assertIn("scripts/verify_gates.py", skill)
        self.assertIn("explicit `strict` forces the fresh-context three-role path, not chunking", skill)
        self.assertIn("Add `--chunk` only when", skill)
        self.assertIn("if `body_chunk_count` is one", skill)
        self.assertIn("one `delegate_task(tasks=[...])` batch", skill)
        self.assertIn("at most four chunk children", skill)
        self.assertNotIn("Optional `delegate_task` review", skill)

    def test_runtime_role_prompts_are_packaged(self) -> None:
        role_dir = SKILL_ROOT / "references" / "runtime-agents"
        required = {
            "diagnostician.md": "## 역할",
            "monolith.md": "범용 문자열 치환을 금지",
            "finalizer.md": "전체 재작성은 금지",
        }
        for name, marker in required.items():
            with self.subTest(name=name):
                text = (role_dir / name).read_text(encoding="utf-8")
                self.assertIn(marker, text)
                self.assertNotIn("model: opus", text)
                self.assertNotIn("TeamCreate", text)

        diagnostician = (role_dir / "diagnostician.md").read_text(encoding="utf-8")
        self.assertIn("diagnosis-rules.md", diagnostician)
        self.assertNotIn("taxonomy_skill_ref=humanize-korean:references/ai-tell-taxonomy.md", diagnostician)

        monolith = (role_dir / "monolith.md").read_text(encoding="utf-8")
        self.assertIn("HUMANIZE-SUMMARY v2.3", monolith)
        self.assertIn("verify_gates.py", monolith)

    def test_route_dispatch_uses_absolute_rule_paths(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        taxonomy_path = (
            "taxonomy_path=<absolute-SKILL_ROOT>/references/diagnosis-rules.md"
        )
        quick_rules_path = (
            "quick_rules_path=<absolute-SKILL_ROOT>/references/quick-rules.md"
        )

        self.assertNotIn("taxonomy_path=references/", skill)
        self.assertNotIn("quick_rules_path=references/", skill)
        self.assertIn(taxonomy_path, skill)
        self.assertGreaterEqual(skill.count(quick_rules_path), 3)

    def test_runtime_contracts_preserve_content_anchors(self) -> None:
        contract_paths = (
            SKILL_ROOT / "SKILL.md",
            SKILL_ROOT / "references" / "runtime-agents" / "monolith.md",
            SKILL_ROOT / "references" / "runtime-agents" / "finalizer.md",
            SKILL_ROOT / "references" / "quick-rules.header.md",
            SKILL_ROOT / "references" / "quick-rules.footer.md",
        )
        for path in contract_paths:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("핵심 내용 명사·개념어", text)
                self.assertIn("원형", text)

        monolith = contract_paths[1].read_text(encoding="utf-8")
        self.assertIn("anchor_ledger", monolith)

    def test_light_finalizer_allows_missing_diagnosis(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        finalizer = (
            SKILL_ROOT / "references" / "runtime-agents" / "finalizer.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Light escalation without a diagnosis", skill)
        self.assertIn("Do not add a diagnostician call", skill)
        self.assertIn("--stage finalize", skill)
        self.assertIn("`diagnosis_path` (선택)", finalizer)
        self.assertIn("Light 경로에는 진단 파일이 없다", finalizer)
        self.assertIn("중단하지 않는다", finalizer)
        self.assertIn("Light·standard 승급 또는 heavy/strict", finalizer)


if __name__ == "__main__":
    unittest.main()
