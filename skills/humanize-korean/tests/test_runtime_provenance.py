"""Hermes runtime provenance and parent gate stamping tests.

These tests cover only the Hermes adapter. Korean rewrite quality remains in
upstream-derived golden tests and role contracts.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


STATE = _load("update_execution_state_test", "update_execution_state.py")
RATE = _load("verify_change_rate_test", "verify_change_rate.py")

SUMMARY = """윤문한 본문이다.

<!-- HUMANIZE-SUMMARY v2.2
run_id: test-001
metrics:
  char_in: 9
  char_out: 9
  change_rate_claim: 0.0%
  change_rate_actual: pending_parent_gate
  gate_exit: pending_parent_gate
  self_check: 6/6
  grade: A
self_check:
  preserved_names_numbers_quotes: pass
-->
"""


class ExecutionStateTests(unittest.TestCase):
    def test_records_verified_role_order_and_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)
            outputs = {
                "diagnostician": run / "02_diagnosis.md",
                "monolith": run / "final.md",
                "finalizer": run / "09_finalize.json",
            }
            for path in outputs.values():
                path.write_text("verified\n", encoding="utf-8")

            self.assertEqual(
                STATE.main(
                    [
                        "init",
                        "--run-dir",
                        str(run),
                        "--run-id",
                        "test-001",
                        "--requested-mode",
                        "strict",
                        "--resolved-route",
                        "heavy",
                        "--route-source",
                        "user_override",
                    ]
                ),
                0,
            )
            for stage, delegation_id in (
                ("diagnostician", "deleg-d"),
                ("monolith", "deleg-m"),
                ("finalizer", "deleg-f"),
            ):
                self.assertEqual(
                    STATE.main(
                        [
                            "record",
                            "--run-dir",
                            str(run),
                            "--stage",
                            stage,
                            "--delegation-id",
                            delegation_id,
                            "--output",
                            str(outputs[stage]),
                        ]
                    ),
                    0,
                )

            self.assertEqual(
                STATE.main(
                    [
                        "rate",
                        "--run-dir",
                        str(run),
                        "--percent",
                        "12.3",
                        "--exit-code",
                        "0",
                        "--scope",
                        "full",
                    ]
                ),
                0,
            )
            self.assertEqual(
                STATE.main(
                    [
                        "finish",
                        "--run-dir",
                        str(run),
                        "--status",
                        "completed",
                    ]
                ),
                0,
            )

            payload = json.loads((run / "00_execution.json").read_text(encoding="utf-8"))
            sequences = [
                payload["stages"][name][0]["sequence"]
                for name in ("diagnostician", "monolith", "finalizer")
            ]
            self.assertEqual(sequences, [1, 2, 3])
            self.assertEqual(payload["change_rate"]["percent"], 12.3)
            self.assertEqual(payload["status"], "completed")

    def test_record_refuses_missing_or_external_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as other:
            run = Path(tmp)
            STATE.main(
                [
                    "init",
                    "--run-dir",
                    str(run),
                    "--run-id",
                    "test-002",
                    "--requested-mode",
                    "strict",
                    "--resolved-route",
                    "heavy",
                    "--route-source",
                    "user_override",
                ]
            )
            external = Path(other) / "output.md"
            external.write_text("outside\n", encoding="utf-8")
            for output in (run / "missing.md", external):
                with self.subTest(output=output):
                    code = STATE.main(
                        [
                            "record",
                            "--run-dir",
                            str(run),
                            "--stage",
                            "monolith",
                            "--delegation-id",
                            "deleg-x",
                            "--output",
                            str(output),
                        ]
                    )
                    self.assertEqual(code, 3)


class ChangeRateStampTests(unittest.TestCase):
    def test_parent_gate_stamps_summary_and_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)
            before = run / "01_input.txt"
            after = run / "final.md"
            execution = run / "00_execution.json"
            before.write_text("윤문한 본문이다.\n", encoding="utf-8")
            after.write_text(SUMMARY, encoding="utf-8")
            execution.write_text('{"change_rate": null}\n', encoding="utf-8")

            code = RATE.main(
                [
                    "--before",
                    str(before),
                    "--after",
                    str(after),
                    "--stamp-summary",
                    "--execution-state",
                    str(execution),
                ]
            )
            self.assertEqual(code, 0)
            stamped = after.read_text(encoding="utf-8")
            self.assertIn("change_rate_actual: 0.0%", stamped)
            self.assertIn("gate_exit: 0", stamped)
            self.assertIn("change_rate_scope: full", stamped)
            payload = json.loads(execution.read_text(encoding="utf-8"))
            self.assertEqual(payload["change_rate"]["exit_code"], 0)
            self.assertEqual(payload["change_rate"]["scope"], "full")

    def test_requested_stamp_requires_complete_tail_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)
            before = run / "before.txt"
            after = run / "after.md"
            before.write_text("같은 본문", encoding="utf-8")
            after.write_text("같은 본문\n<!-- HUMANIZE-SUMMARY", encoding="utf-8")
            self.assertEqual(
                RATE.main(
                    [
                        "--before",
                        str(before),
                        "--after",
                        str(after),
                        "--stamp-summary",
                    ]
                ),
                3,
            )


if __name__ == "__main__":
    unittest.main()
