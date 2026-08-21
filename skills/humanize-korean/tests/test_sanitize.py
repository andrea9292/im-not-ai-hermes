"""텍스트 위생 모듈과 Hermes 입력 shim 배선 회귀 테스트."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from typing import Any
import unicodedata
import unittest

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
SANITIZE_PATH = SCRIPTS / "sanitize_text.py"
PREPARE_PATH = SCRIPTS / "prepare_monolith_input.py"
PACKAGE_CHECK_PATH = SCRIPTS / "check_package_contents.py"


def _load_module(name: str, path: Path) -> Any:
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ST = _load_module("sanitize_text", SANITIZE_PATH)
PREP = _load_module("prepare_monolith_input_sanitize_test", PREPARE_PATH)
PACKAGE_CHECK = _load_module("check_package_contents_sanitize_test", PACKAGE_CHECK_PATH)

ZWSP = chr(0x200B)
BOM = chr(0xFEFF)
SHY = chr(0x00AD)
WJ = chr(0x2060)
NBSP = chr(0x00A0)
IDEO = chr(0x3000)
NARROW_NBSP = chr(0x202F)
RLO = chr(0x202E)
LRM = chr(0x200E)
ZWJ = chr(0x200D)
ZWNJ = chr(0x200C)
TAG_A = chr(0xE0061)
LINE_SEP = chr(0x2028)
PARA_SEP = chr(0x2029)


class SanitizeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assertIsNotNone(ST, "scripts/sanitize_text.py 런타임 모듈이 필요합니다")

    def test_clean_korean_untouched(self) -> None:
        clean = "\n".join(
            [
                "AI가 쓴 글을 사람 글처럼 다듬습니다.",
                "",
                "첫째, 번역투를 걷어냅니다. 둘째, 리듬을 살립니다.",
                "가격은 1,200원이며 — 부가세 별도입니다.",
                '그는 "그렇게는 못 한다"고 잘라 말했다.',
                "이모지도 그대로: 👨" + ZWJ + "👩" + ZWJ + "👧 가족",
            ]
        )
        out, report = ST.sanitize(clean)
        self.assertEqual(out, clean)
        self.assertFalse(report.changed)
        self.assertEqual(report.summary, "")

    def test_invisible_removed(self) -> None:
        dirty = "안" + ZWSP + "녕" + BOM + "하" + SHY + "세" + WJ + "요"
        out, report = ST.sanitize(dirty)
        self.assertEqual(out, "안녕하세요")
        self.assertEqual(report.counts["invisible"], 4)
        self.assertLess(report.after_chars, report.before_chars)

    def test_emoji_zwj_preserved(self) -> None:
        emoji = "👨" + ZWJ + "👩" + ZWJ + "👧"
        self.assertEqual(ST.sanitize(emoji)[0], emoji)

    def test_hangul_joiner_removed(self) -> None:
        dirty = "한" + ZWJ + "글" + ZWNJ + "테스트"
        out, report = ST.sanitize(dirty)
        self.assertEqual(out, "한글테스트")
        self.assertEqual(report.counts["invisible"], 2)

    def test_bidi_removed(self) -> None:
        dirty = "정상" + RLO + "뒤집기" + LRM + "끝"
        out, report = ST.sanitize(dirty)
        self.assertEqual(out, "정상뒤집기끝")
        self.assertEqual(report.counts["bidi"], 2)

    def test_tag_chars_removed(self) -> None:
        dirty = "본문" + TAG_A + TAG_A + "끝"
        out, report = ST.sanitize(dirty)
        self.assertEqual(out, "본문끝")
        self.assertEqual(report.counts["tag_chars"], 2)

    def test_nfc_normalization(self) -> None:
        nfd = unicodedata.normalize("NFD", "한글 테스트")
        self.assertNotEqual(nfd, "한글 테스트")
        out, report = ST.sanitize(nfd)
        self.assertEqual(out, "한글 테스트")
        self.assertEqual(report.counts["hangul_recomposed"], 5)

    def test_special_spaces_preserve_ideographic_space_by_default(self) -> None:
        dirty = "가" + NBSP + "나" + IDEO + "다" + NARROW_NBSP + "라"
        out, report = ST.sanitize(dirty)
        self.assertEqual(out, "가 나" + IDEO + "다 라")
        self.assertEqual(report.counts["special_spaces"], 2)

    def test_ideographic_space_opt_in(self) -> None:
        out, report = ST.sanitize(
            "가" + IDEO + "나", normalize_ideographic_space=True
        )
        self.assertEqual(out, "가 나")
        self.assertEqual(report.counts["special_spaces"], 1)

    def test_line_normalization_preserves_blank_line_count(self) -> None:
        dirty = (
            "첫 줄   \r\n둘째 줄"
            + LINE_SEP
            + "셋째 줄"
            + PARA_SEP
            + "\n\n\n\n넷째 줄"
        )
        out, report = ST.sanitize(dirty)
        self.assertEqual(out, "첫 줄\n둘째 줄\n셋째 줄\n\n\n\n\n넷째 줄")
        self.assertGreaterEqual(report.counts["line_breaks"], 3)
        self.assertGreaterEqual(report.counts["trailing_space_lines"], 1)

    def test_collapse_blank_lines_opt_in(self) -> None:
        source = "가\n\n\n\n나"
        self.assertEqual(ST.sanitize(source, collapse_blank_lines=True)[0], "가\n\n나")
        self.assertEqual(ST.sanitize(source)[0], source)

    def test_idempotent(self) -> None:
        dirty = (
            "안"
            + ZWSP
            + "녕"
            + NBSP
            + "하세요"
            + RLO
            + "\r\n\r\n\r\n"
            + unicodedata.normalize("NFD", "둘째")
            + "   \n"
            + TAG_A
        )
        once, _ = ST.sanitize(dirty)
        twice, report = ST.sanitize(once)
        self.assertEqual(twice, once)
        self.assertFalse(report.changed)

    def test_options_can_disable_individual_steps(self) -> None:
        dirty = "가" + NBSP + "나" + ZWSP + "다"
        only_spaces, _ = ST.sanitize(dirty, strip_invisible=False)
        self.assertEqual(only_spaces, "가 나" + ZWSP + "다")
        only_invisible, _ = ST.sanitize(dirty, normalize_spaces=False)
        self.assertIn(NBSP, only_invisible)

    def test_protected_tokens_survive(self) -> None:
        source = (
            "2026년 8월 2일, EU AI Act 발효."
            + ZWSP
            + " 앤트로픽은 "
            + NBSP
            + '"별도 문자를 추가하지 않는다"고 밝혔다. 수치는 4,500개.'
        )
        out, _ = ST.sanitize(source)
        for token in (
            "2026",
            "8월 2일",
            "EU AI Act",
            "앤트로픽",
            "4,500",
            "별도 문자를 추가하지 않는다",
        ):
            self.assertIn(token, out)

    def test_inspect_does_not_mutate_input(self) -> None:
        dirty = "가" + ZWSP + "나"
        before = dirty
        report = ST.inspect(dirty)
        self.assertEqual(dirty, before)
        self.assertTrue(report.changed)
        self.assertTrue(report.summary)

    def test_empty(self) -> None:
        out, report = ST.sanitize("")
        self.assertEqual(out, "")
        self.assertFalse(report.changed)
        self.assertEqual(ST.sanitize("   \n  \n")[0], "\n\n")

    def test_source_has_no_literal_invisibles(self) -> None:
        source = SANITIZE_PATH.read_text(encoding="utf-8")
        bad = [
            (index, hex(ord(char)))
            for index, char in enumerate(source)
            if char not in "\n\t"
            and (
                unicodedata.category(char) in ("Cf", "Cc", "Co", "Cs")
                or ord(char) in (0xA0, 0x3000, 0x2028, 0x2029)
                or 0x2000 <= ord(char) <= 0x200F
            )
        ]
        self.assertEqual(bad, [])


class SanitizeShimIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assertIsNotNone(PREP, "prepare_monolith_input.py를 로드할 수 없습니다")
        self.assertTrue(
            hasattr(PREP, "_sanitize_mod") and PREP._sanitize_mod is not None,
            "prepare_monolith_input.py에 sanitize 런타임 배선이 필요합니다",
        )

    def test_single_mode_sanitizes_input_and_writes_report(self) -> None:
        dirty = unicodedata.normalize("NFD", "한글") + ZWSP + " 테스트\n"
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td)
            (run_dir / "01_input.txt").write_text(dirty, encoding="utf-8")
            self.assertEqual(PREP.main(["--run-dir", td]), 0)
            self.assertEqual(
                (run_dir / "01_input.txt").read_text(encoding="utf-8"),
                "한글 테스트\n",
            )
            report = json.loads(
                (run_dir / "00_sanitize.json").read_text(encoding="utf-8")
            )
            self.assertTrue(report["changed"])
            combined = (run_dir / "01_input_with_metrics.txt").read_text(
                encoding="utf-8"
            )
            self.assertIn("한글 테스트", combined)

    def test_single_mode_normalizes_line_endings_on_disk(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td)
            input_path = run_dir / "01_input.txt"
            input_path.write_bytes("첫째\r\n둘째\r셋째\n".encode("utf-8"))
            self.assertEqual(PREP.main(["--run-dir", td]), 0)
            self.assertEqual(
                input_path.read_bytes(), "첫째\n둘째\n셋째\n".encode("utf-8")
            )
            report = json.loads(
                (run_dir / "00_sanitize.json").read_text(encoding="utf-8")
            )
            self.assertEqual(report["counts"]["line_breaks"], 2)

    def test_no_sanitize_preserves_input(self) -> None:
        dirty = unicodedata.normalize("NFD", "한글") + ZWSP + " 테스트\n"
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td)
            (run_dir / "01_input.txt").write_text(dirty, encoding="utf-8")
            self.assertEqual(PREP.main(["--run-dir", td, "--no-sanitize"]), 0)
            self.assertEqual(
                (run_dir / "01_input.txt").read_text(encoding="utf-8"), dirty
            )
            self.assertFalse((run_dir / "00_sanitize.json").exists())

    def test_clean_rerun_removes_stale_report(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td)
            input_path = run_dir / "01_input.txt"
            input_path.write_text("한" + ZWSP + "글\n", encoding="utf-8")
            self.assertEqual(PREP.main(["--run-dir", td]), 0)
            self.assertTrue((run_dir / "00_sanitize.json").exists())

            input_path.write_text("깨끗한 입력\n", encoding="utf-8")
            self.assertEqual(PREP.main(["--run-dir", td]), 0)
            self.assertFalse((run_dir / "00_sanitize.json").exists())

    def test_no_sanitize_rerun_removes_stale_report(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td)
            input_path = run_dir / "01_input.txt"
            input_path.write_text("한" + ZWSP + "글\n", encoding="utf-8")
            self.assertEqual(PREP.main(["--run-dir", td]), 0)
            self.assertTrue((run_dir / "00_sanitize.json").exists())

            dirty = "다" + ZWSP + "시\n"
            input_path.write_text(dirty, encoding="utf-8")
            self.assertEqual(PREP.main(["--run-dir", td, "--no-sanitize"]), 0)
            self.assertEqual(input_path.read_text(encoding="utf-8"), dirty)
            self.assertFalse((run_dir / "00_sanitize.json").exists())

    def test_chunk_mode_hashes_sanitized_input(self) -> None:
        dirty = unicodedata.normalize("NFD", "한글 테스트") + ZWSP + "\n"
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td)
            (run_dir / "01_input.txt").write_text(dirty, encoding="utf-8")
            self.assertEqual(PREP.main(["--chunk", "--run-dir", td]), 0)
            cleaned = (run_dir / "01_input.txt").read_text(encoding="utf-8")
            manifest = json.loads(
                (run_dir / "chunk_manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(cleaned, "한글 테스트\n")
            self.assertEqual(manifest["source_chars"], len(cleaned))


class SanitizePackageContractTests(unittest.TestCase):
    def test_sanitize_runtime_and_test_are_required_package_files(self) -> None:
        self.assertIn("scripts/sanitize_text.py", PACKAGE_CHECK.RUNTIME_REQUIRED)
        self.assertIn("tests/test_sanitize.py", PACKAGE_CHECK.TEST_REQUIRED)


if __name__ == "__main__":
    unittest.main()
