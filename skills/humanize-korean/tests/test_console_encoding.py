"""Windows cp949 콘솔과 게이트 종료 코드 회귀 테스트."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

SKILL_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = SKILL_ROOT / "scripts"

BEFORE = "원문은 이러하다. 수치는 1,200명이다."
AFTER = "원문은 이렇다. 수치는 1,200명이다."


def _cp949_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "cp949"
    return env


class ConsoleEncodingTests(unittest.TestCase):
    def test_verify_gates_survives_cp949(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = Path(temporary)
            before = run_dir / "before.txt"
            after = run_dir / "after.md"
            before.write_text(BEFORE, encoding="utf-8")
            after.write_text(AFTER, encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "verify_gates.py"),
                    "--before",
                    str(before),
                    "--after",
                    str(after),
                ],
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                env=_cp949_env(),
                timeout=120,
            )

        self.assertNotIn("UnicodeEncodeError", result.stderr)
        self.assertIn("[P0", result.stdout)
        self.assertIn("[P3 golden]", result.stdout)
        self.assertIn(result.returncode, (0, 1, 2))

    def test_unhandled_gate_exception_exits_3(self) -> None:
        sys.path.insert(0, str(SCRIPTS))
        import console

        with mock.patch("sys.stderr"):
            result = console.run_gate(lambda: (_ for _ in ()).throw(RuntimeError("boom")))

        self.assertEqual(result, 3)

    def test_packaged_cli_entrypoints_enable_utf8(self) -> None:
        targets = (
            "build_diagnosis_rules.py",
            "build_quick_rules.py",
            "check_package_contents.py",
            "golden_checks.py",
            "prepare_monolith_input.py",
            "reassemble_chunks.py",
            "sanitize_text.py",
            "update_execution_state.py",
            "validate_stage_artifacts.py",
            "verify_change_rate.py",
            "verify_gates.py",
        )
        missing = [
            name
            for name in targets
            if "_console." not in (SCRIPTS / name).read_text(encoding="utf-8")
        ]
        self.assertEqual(missing, [])

    def test_package_contract_includes_console_regression_files(self) -> None:
        checker = (SCRIPTS / "check_package_contents.py").read_text(encoding="utf-8")
        self.assertIn('"scripts/console.py"', checker)
        self.assertIn('"tests/test_console_encoding.py"', checker)


if __name__ == "__main__":
    unittest.main()
