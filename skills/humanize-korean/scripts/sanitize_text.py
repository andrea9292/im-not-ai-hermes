#!/usr/bin/env python3
"""텍스트 위생(sanitize) — 결정적 처리, LLM 호출 0회.

하는 일: 눈에 보이지 않으면서 실제로 문제를 일으키는 문자들을 정리한다.
  - 한글 자모 분해(NFD) → 완성형(NFC) 정규화. macOS 경유 텍스트는 눈에는
    같아 보여도 글자수·검색·변경률 게이트가 어긋날 수 있다.
  - 제로폭 문자·BOM·소프트하이픈·양방향 제어 문자·태그 문자를 제거한다.
  - NBSP 등 특수 공백을 보통 공백으로 바꾸고 줄바꿈과 줄 끝 공백을 정리한다.
  - 전각공백 변환과 과다 빈 줄 축소는 눈에 보이는 편집이므로 opt-in이다.

하지 않는 일:
  - AI 워터마크를 제거하지 않는다. 이 처리는 문자 정규화일 뿐 단어 선택의
    통계 패턴과 무관하다. 문서나 UI에서 워터마크 제거로 표기해서는 안 된다.
  - 맞춤법·띄어쓰기·문장부호를 고치지 않는다.
  - 따옴표·대시·이모지 결합 문자를 일괄 변경하지 않는다.

설계 원칙:
  - 멱등(idempotent): sanitize(sanitize(x)) == sanitize(x)
  - stdlib only
  - 소스에 비가시 문자를 리터럴로 쓰지 않고 코드포인트로 조립한다.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import re
import unicodedata

SOFT_HYPHEN = 0x00AD
NBSP = 0x00A0
MONGOLIAN_VOWEL_SEP = 0x180E
OGHAM_SPACE = 0x1680
ZWSP = 0x200B
ZWNJ = 0x200C
ZWJ = 0x200D
WORD_JOINER = 0x2060
BOM = 0xFEFF
NARROW_NBSP = 0x202F
MED_MATH_SPACE = 0x205F
IDEOGRAPHIC_SPACE = 0x3000
LINE_SEP = 0x2028
PARA_SEP = 0x2029


def _cls(*ranges) -> str:
    """코드포인트/범위 목록을 정규식 문자 클래스 본문으로 만든다."""
    out = []
    for item in ranges:
        if isinstance(item, tuple):
            out.append(f"\\U{item[0]:08x}-\\U{item[1]:08x}")
        else:
            out.append(f"\\U{item:08x}")
    return "".join(out)


INVISIBLE_ALWAYS = re.compile(
    "[" + _cls(SOFT_HYPHEN, MONGOLIAN_VOWEL_SEP, ZWSP, WORD_JOINER, BOM) + "]"
)
BIDI = re.compile(
    "[" + _cls(0x061C, (0x200E, 0x200F), (0x202A, 0x202E), (0x2066, 0x2069)) + "]"
)
TAG_CHARS = re.compile("[" + _cls((0xE0000, 0xE007F)) + "]")
SPECIAL_SPACES = re.compile(
    "["
    + _cls(
        NBSP,
        OGHAM_SPACE,
        (0x2000, 0x200A),
        NARROW_NBSP,
        MED_MATH_SPACE,
    )
    + "]"
)
IDEOGRAPHIC_SPACE_RE = re.compile("[" + _cls(IDEOGRAPHIC_SPACE) + "]")
UNI_BREAKS = re.compile("[" + _cls(LINE_SEP, PARA_SEP) + "]")
DECOMPOSED_HANGUL = re.compile(
    "[" + _cls((0x1100, 0x1112)) + "]"
    "[" + _cls((0x1161, 0x1175)) + "]"
    "[" + _cls((0x11A8, 0x11C2)) + "]?"
)

# ZWJ/ZWNJ는 이모지 결합에 필요하므로 양옆이 평범한 문자일 때만 제거한다.
PLAIN_NEIGHBOR = re.compile(r"[가-힣0-9A-Za-z\s.,!?;:'\"()\[\]{}-]")
_ZWNJ_CH = chr(ZWNJ)
_ZWJ_CH = chr(ZWJ)


@dataclass
class SanitizeReport:
    changed: bool = False
    before_chars: int = 0
    after_chars: int = 0
    counts: dict = field(default_factory=dict)
    summary: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def _strip_joiners_outside_emoji(text: str) -> tuple[str, int]:
    if _ZWJ_CH not in text and _ZWNJ_CH not in text:
        return text, 0
    removed = 0
    kept: list[str] = []
    size = len(text)
    for index, char in enumerate(text):
        if char in (_ZWNJ_CH, _ZWJ_CH):
            previous = kept[-1] if kept else ""
            following = text[index + 1] if index + 1 < size else ""
            previous_plain = previous == "" or bool(PLAIN_NEIGHBOR.match(previous))
            following_plain = following == "" or bool(PLAIN_NEIGHBOR.match(following))
            if previous_plain and following_plain:
                removed += 1
                continue
        kept.append(char)
    return "".join(kept), removed


def _summary(counts: dict, changed: bool) -> str:
    if not changed:
        return ""
    parts = []
    if counts.get("hangul_recomposed"):
        parts.append(f"분해된 한글 {counts['hangul_recomposed']}자 결합")
    if counts.get("invisible"):
        parts.append(f"보이지 않는 문자 {counts['invisible']}개 제거")
    if counts.get("bidi"):
        parts.append(f"방향 제어 문자 {counts['bidi']}개 제거")
    if counts.get("tag_chars"):
        parts.append(f"숨은 태그 문자 {counts['tag_chars']}개 제거")
    if counts.get("special_spaces"):
        parts.append(f"특수 공백 {counts['special_spaces']}개 정리")
    if counts.get("line_breaks"):
        parts.append(f"줄바꿈 {counts['line_breaks']}개 통일")
    if counts.get("trailing_space_lines"):
        parts.append(f"줄 끝 공백 {counts['trailing_space_lines']}줄 정리")
    return " · ".join(parts)


def sanitize(
    text: str,
    *,
    normalize_unicode: bool = True,
    strip_invisible: bool = True,
    normalize_spaces: bool = True,
    normalize_lines: bool = True,
    normalize_ideographic_space: bool = False,
    collapse_blank_lines: bool = False,
) -> tuple[str, SanitizeReport]:
    """텍스트를 정리하고 처리 보고서를 반환한다."""
    original = text
    counts = {
        "hangul_recomposed": 0,
        "invisible": 0,
        "bidi": 0,
        "tag_chars": 0,
        "special_spaces": 0,
        "line_breaks": 0,
        "trailing_space_lines": 0,
    }

    if strip_invisible:
        counts["invisible"] = len(INVISIBLE_ALWAYS.findall(text))
        text = INVISIBLE_ALWAYS.sub("", text)
        counts["bidi"] = len(BIDI.findall(text))
        text = BIDI.sub("", text)
        counts["tag_chars"] = len(TAG_CHARS.findall(text))
        text = TAG_CHARS.sub("", text)
        text, removed = _strip_joiners_outside_emoji(text)
        counts["invisible"] += removed

    if normalize_unicode:
        counts["hangul_recomposed"] = len(DECOMPOSED_HANGUL.findall(text))
        text = unicodedata.normalize("NFC", text)

    if normalize_spaces:
        counts["special_spaces"] = len(SPECIAL_SPACES.findall(text))
        text = SPECIAL_SPACES.sub(" ", text)
    if normalize_ideographic_space:
        counts["special_spaces"] += len(IDEOGRAPHIC_SPACE_RE.findall(text))
        text = IDEOGRAPHIC_SPACE_RE.sub(" ", text)

    if normalize_lines:
        counts["line_breaks"] = (
            text.count("\r\n")
            + len(re.findall(r"\r(?!\n)", text))
            + len(UNI_BREAKS.findall(text))
        )
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = UNI_BREAKS.sub("\n", text)
        counts["trailing_space_lines"] = len(
            re.findall(r"[ \t]+$", text, re.MULTILINE)
        )
        text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)

    if collapse_blank_lines:
        text = re.sub(r"\n{3,}", "\n\n", text)

    changed = text != original
    return text, SanitizeReport(
        changed=changed,
        before_chars=len(original),
        after_chars=len(text),
        counts=counts,
        summary=_summary(counts, changed),
    )


def inspect(text: str, **options) -> SanitizeReport:
    """원본 문자열을 바꾸지 않고 정리 대상 보고서만 반환한다."""
    return sanitize(text, **options)[1]


def _main(argv: list[str] | None = None) -> int:
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(
        description="텍스트 위생 — 보이지 않는 오염 문자 정리 (워터마크 제거 아님)"
    )
    parser.add_argument("path", nargs="?", help="입력 파일 (없으면 stdin)")
    parser.add_argument(
        "--in-place", action="store_true", help="입력 파일을 제자리에서 수정"
    )
    parser.add_argument(
        "--report", action="store_true", help="본문 대신 JSON 보고서만 출력"
    )
    args = parser.parse_args(argv)

    if args.path:
        with open(args.path, encoding="utf-8", newline="") as stream:
            source = stream.read()
    else:
        source = sys.stdin.read()
    output, report = sanitize(source)

    if args.report:
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
        return 0
    if args.in_place:
        if not args.path:
            parser.error("--in-place는 파일 경로가 필요합니다")
        if report.changed:
            open(args.path, "w", encoding="utf-8", newline="").write(output)
        print(report.summary or "정리할 항목 없음")
        return 0
    sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
