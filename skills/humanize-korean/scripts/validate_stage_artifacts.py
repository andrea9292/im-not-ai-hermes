#!/usr/bin/env python3
"""Validate humanize-korean runtime stage artifacts.

This deterministic gate verifies delegated-stage artifacts and protected
surface forms. It does not decide whether prose is elegant or AI-authored.

Exit codes:
  0  requested checks passed
  1  artifact, schema, provenance, or fidelity contract failed
  2  finalizer returned hold_and_report (safe stop; do not adopt)
  3  validator could not inspect the run or CLI usage was invalid
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Iterable, NoReturn, Sequence

SUMMARY_START_RE = re.compile(r"<!--\s*HUMANIZE-SUMMARY\b", re.IGNORECASE)
SUMMARY_TAIL_RE = re.compile(
    r"<!--\s*HUMANIZE-SUMMARY\b(?P<body>.*?)-->\s*\Z",
    re.DOTALL | re.IGNORECASE,
)
TAX_HEADING_RE = re.compile(r"^###\s+([A-J]-\d{1,2})\.\s*(.*)$", re.MULTILINE)
DIAG_ROW_RE = re.compile(r"^\s*\d+\.\s+\*\*([A-J]-\d{1,2})\*\*", re.MULTILINE)
FENCE_OPEN_RE = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})(.*)$")
INLINE_CODE_RE = re.compile(r"(?<!`)(`+)([^`\n]+?)\1(?!`)")
RAW_URL_RE = re.compile(r"https?://[^\s<>\"']+")
NUMBER_RE = re.compile(
    r"제\d+(?:\.\d+)*[조장절항호]|(?<![A-Za-z])[-+]?\d+(?:[.,]\d+)*(?:%|‰)?"
)
DIRECT_QUOTE_CONTEXT_RE = re.compile(
    r"(?:라고|라며|라면서|말(?:했|한다|하였다|했다)|밝혔|전했|답했|물었|인용|발언)"
)
MD_FOOTNOTE_RE = re.compile(r"\[\^([^\]]+)\]")
MD_FOOTNOTE_DEF_LINE_RE = re.compile(r"^\[\^([^\]]+)\]:\s*(.*)$")
NUMERIC_INLINE_RE = re.compile(r"(?<=\S)(?<![(\d])(\d{1,3})\)")
NUMERIC_DEF_LINE_RE = re.compile(r"^\s*(\d{1,3})\)\s+(.*)$")
LIST_LINE_RE = re.compile(
    r"^(?P<indent>[ \t]*)(?P<marker>(?:[-+*]\s+\[(?: |x|X)\]|[-+*]|\d+[.)]))\s+"
)
ATX_HEADING_RE = re.compile(r"^#{1,6}\s+\S")
ROMAN_HEADING_RE = re.compile(r"^[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫ]+\.\s*\S")
LEGAL_HEADING_RE = re.compile(r"^제\d+[장절]\s*\S")
NUMERIC_HEADING_RE = re.compile(r"^(?:\d{1,2}\.\s+|\(\d{1,2}\)\s*)\S")
PROSE_ENDING_RE = re.compile(r"(?:다|요|음|함|까)\s*[.?!]$")
TABLE_SEPARATOR_CELL_RE = re.compile(r"^:?-{3,}:?$")
PLACEHOLDER_RE = re.compile(
    r"\b(?:TODO|TBD|FIXME|PLACEHOLDER)\b|\{\{[^{}]+\}\}", re.IGNORECASE
)
MALFORMED_RE = re.compile(
    r"(?:못|않|없|확정|판단|확인|제공|누락|전달|수정|검토)가능(?:하|했|합|한|할|성)"
)
YO_ENDING_RE = re.compile(r"요\s*(?:[.?!…]|$)", re.MULTILINE)
CLICHE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("기록적인 성과", re.compile(r"기록적인\s*성과")),
    ("괄목할 만한", re.compile(r"괄목할\s*만한")),
    ("~로 평가된다", re.compile(r"로\s*평가(?:된다|받|되)")),
    ("주목받-", re.compile(r"주목받")),
    ("크게 기여", re.compile(r"크게\s*기여")),
    ("중요한 역할을 한다", re.compile(r"중요한\s*역할을\s*(?:한다|했다|할)")),
    ("시사하는 바가 크다", re.compile(r"시사하는\s*바가\s*크")),
    ("의미가 크다", re.compile(r"의미가\s*크다")),
)


@dataclass(frozen=True)
class Issue:
    code: str
    message: str

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise RuntimeError(f"{path}: {exc}") from exc


def strip_summary(text: str) -> str:
    return SUMMARY_TAIL_RE.sub("", text).rstrip()


def _split_fences(text: str) -> tuple[list[str], str]:
    """Return ordered fenced blocks and text outside them."""
    lines = text.splitlines(keepends=True)
    blocks: list[str] = []
    outside: list[str] = []
    i = 0
    while i < len(lines):
        open_match = FENCE_OPEN_RE.match(lines[i].rstrip("\r\n"))
        if not open_match:
            outside.append(lines[i])
            i += 1
            continue
        marker = open_match.group(1)
        char = marker[0]
        minimum = len(marker)
        block = [lines[i]]
        outside.append("\n" if lines[i].endswith(("\n", "\r")) else "")
        i += 1
        closed = False
        while i < len(lines):
            block.append(lines[i])
            stripped = lines[i].strip()
            outside.append("\n" if lines[i].endswith(("\n", "\r")) else "")
            if stripped and set(stripped) == {char} and len(stripped) >= minimum:
                closed = True
                i += 1
                break
            i += 1
        if not closed:
            # An unclosed fence is still a protected block; a changed closing
            # delimiter will therefore fail the ordered block comparison.
            pass
        blocks.append("".join(block))
    return blocks, "".join(outside)


def _outside_fences(text: str) -> str:
    return _split_fences(text)[1]


def _inline_code(text: str) -> list[tuple[str, str]]:
    return INLINE_CODE_RE.findall(_outside_fences(text))


def _urls(text: str) -> list[str]:
    result: list[str] = []
    for match in RAW_URL_RE.finditer(_outside_fences(text)):
        value = match.group(0).rstrip(".,;:!?")
        while value.endswith(")") and value.count(")") > value.count("("):
            value = value[:-1]
        while value.endswith("]") and value.count("]") > value.count("["):
            value = value[:-1]
        for particle in ("에서", "으로", "를", "을", "은", "는", "이", "가", "와", "과", "에", "도", "만"):
            if value.endswith(particle) and len(value) > len(particle):
                previous = value[-len(particle) - 1]
                if previous.isascii() and (previous.isalnum() or previous in "/=_-%"):
                    value = value[: -len(particle)]
                    break
        result.append(value)
    return result


def _numbers(text: str, *, ignore_list_markers: bool = False) -> list[str]:
    source = _outside_fences(text)
    if ignore_list_markers:
        masked: list[str] = []
        for line in source.splitlines():
            match = LIST_LINE_RE.match(line)
            if match and match.group("marker")[0].isdigit():
                start, end = match.span("marker")
                line = line[:start] + (" " * (end - start)) + line[end:]
            masked.append(line)
        source = "\n".join(masked)
    return NUMBER_RE.findall(source)


def _quotes(text: str, min_len: int = 8) -> list[str]:
    source = _outside_fences(text)
    result: list[tuple[int, str]] = []
    pairs = (("「", "」"), ("『", "』"), ("“", "”"))
    for opener, closer in pairs:
        pattern = re.compile(re.escape(opener) + r"([^" + re.escape(closer) + r"]+)" + re.escape(closer))
        for match in pattern.finditer(source):
            context = source[max(0, match.start() - 20) : min(len(source), match.end() + 24)]
            if len(match.group(1).strip()) >= min_len or DIRECT_QUOTE_CONTEXT_RE.search(context):
                result.append((match.start(), match.group(1)))
    parts = list(re.finditer(r'"([^"\n]+)"', source))
    for match in parts:
        context = source[max(0, match.start() - 20) : min(len(source), match.end() + 24)]
        if len(match.group(1).strip()) >= min_len or DIRECT_QUOTE_CONTEXT_RE.search(context):
            result.append((match.start(), match.group(1)))
    return [value for _, value in sorted(result)]


def _heading_indices(lines: Sequence[str]) -> set[int]:
    result: set[int] = set()
    for i, raw in enumerate(lines):
        line = " ".join(raw.strip().split())
        if not line or len(line) > 120 or PROSE_ENDING_RE.search(line):
            continue
        if ATX_HEADING_RE.match(line) or ROMAN_HEADING_RE.match(line) or LEGAL_HEADING_RE.match(line):
            result.add(i)
            continue
        if NUMERIC_HEADING_RE.match(line) and not LIST_LINE_RE.match(raw):
            prev_blank = i == 0 or not lines[i - 1].strip()
            next_blank = i + 1 >= len(lines) or not lines[i + 1].strip()
            if prev_blank and next_blank:
                result.add(i)
    return result


def _headings(text: str) -> list[str]:
    lines = _outside_fences(text).splitlines()
    return [" ".join(lines[i].strip().split()) for i in sorted(_heading_indices(lines))]


def _list_structure(text: str) -> list[tuple[int, str]]:
    lines = _outside_fences(text).splitlines()
    heading_lines = _heading_indices(lines)
    result: list[tuple[int, str]] = []
    for i, line in enumerate(lines):
        if i in heading_lines:
            continue
        match = LIST_LINE_RE.match(line)
        if not match:
            continue
        indent = match.group("indent").replace("\t", "    ")
        marker = re.sub(r"\s+", " ", match.group("marker"))
        result.append((len(indent), marker))
    return result


def _table_structure(text: str) -> list[tuple[int, bool]]:
    result: list[tuple[int, bool]] = []
    for line in _outside_fences(text).splitlines():
        stripped = line.strip()
        if not (stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") >= 3):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        is_separator = bool(cells) and all(TABLE_SEPARATOR_CELL_RE.fullmatch(cell) for cell in cells)
        result.append((stripped.count("|"), is_separator))
    return result


def _definition_blocks(
    text: str, pattern: re.Pattern[str]
) -> tuple[list[tuple[str, str]], set[int]]:
    lines = _outside_fences(text).splitlines()
    definitions: list[tuple[str, str]] = []
    consumed: set[int] = set()
    i = 0
    while i < len(lines):
        match = pattern.match(lines[i])
        if not match:
            i += 1
            continue
        label = match.group(1)
        body = [match.group(2).rstrip()]
        consumed.add(i)
        j = i + 1
        while j < len(lines):
            line = lines[j]
            if line.startswith(("  ", "\t")):
                body.append(line.rstrip())
                consumed.add(j)
                j += 1
                continue
            if not line.strip() and j + 1 < len(lines) and lines[j + 1].startswith(("  ", "\t")):
                body.append("")
                consumed.add(j)
                j += 1
                continue
            break
        definitions.append((label, "\n".join(body).rstrip()))
        i = j
    return definitions, consumed


def _reference_data(
    text: str,
    marker_pattern: re.Pattern[str],
    definition_lines: set[int],
) -> tuple[list[str], list[tuple[str, str]]]:
    lines = _outside_fences(text).splitlines()
    labels: list[str] = []
    anchored: list[tuple[str, str]] = []
    for i, line in enumerate(lines):
        if i in definition_lines:
            continue
        for match in marker_pattern.finditer(line):
            label = match.group(1)
            labels.append(label)
            prefix = line[max(0, match.start() - 50) : match.start()]
            numbers = NUMBER_RE.findall(prefix)
            if numbers:
                anchored.append((label, numbers[-1]))
    return labels, anchored


def _footnotes(text: str) -> tuple[tuple[list[str], list[tuple[str, str]]], list[tuple[str, str]], tuple[list[str], list[tuple[str, str]]], list[tuple[str, str]]]:
    md_defs, md_lines = _definition_blocks(text, MD_FOOTNOTE_DEF_LINE_RE)
    md_refs = _reference_data(text, MD_FOOTNOTE_RE, md_lines)

    numeric_candidates, numeric_lines = _definition_blocks(text, NUMERIC_DEF_LINE_RE)
    numeric_refs = _reference_data(text, NUMERIC_INLINE_RE, numeric_lines)
    referenced = set(numeric_refs[0])
    numeric_defs = [item for item in numeric_candidates if item[0] in referenced]
    return md_refs, md_defs, numeric_refs, numeric_defs


def _heading_issues(original: str, rewritten: str) -> list[Issue]:
    original_headings = _headings(original)
    output_lines = {
        " ".join(line.strip().split())
        for line in _outside_fences(rewritten).splitlines()
        if line.strip()
    }
    output_joined = " ".join(_outside_fences(rewritten).split())
    issues: list[Issue] = []
    for heading in original_headings:
        if heading in output_lines:
            continue
        core = re.sub(
            r"^(?:#{1,6}\s+|[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫ]+\.\s*|\d{1,2}\.\s+|\(\d{1,2}\)\s*|제\d+[장절]\s*)",
            "",
            heading,
        ).strip()
        code = "heading_absorbed" if core and core in output_joined else "heading_lost"
        issues.append(Issue(code, f"제목 줄이 독립적으로 보존되지 않았습니다: {heading}"))
    return issues


def _increase(pattern: re.Pattern[str], original: str, rewritten: str) -> Counter[str]:
    before = Counter(pattern.findall(_outside_fences(original)))
    after = Counter(pattern.findall(_outside_fences(rewritten)))
    return after - before


def _fidelity_issues(
    original: str,
    rewritten: str,
    *,
    allow_structure_change: bool = False,
    preserve_lists: bool = False,
) -> list[Issue]:
    issues: list[Issue] = []
    # HUMANIZE-SUMMARY is runtime metadata, not rewritten prose. Its metrics,
    # examples, and YAML-like lists must never enter preservation comparisons.
    original = strip_summary(original)
    rewritten = strip_summary(rewritten)
    if not rewritten.strip():
        return [Issue("empty_output", "윤문본이 비어 있습니다")]

    before_footnotes = _footnotes(original)
    after_footnotes = _footnotes(rewritten)
    ordered_checks: list[tuple[str, object, object, str]] = [
        ("fenced_code", _split_fences(original)[0], _split_fences(rewritten)[0], "코드 펜스의 내용 또는 순서가 변경되었습니다"),
        ("inline_code", _inline_code(original), _inline_code(rewritten), "인라인 코드의 내용 또는 순서가 변경되었습니다"),
        ("url", _urls(original), _urls(rewritten), "URL의 내용 또는 순서가 변경되었습니다"),
        ("number", _numbers(original, ignore_list_markers=not preserve_lists), _numbers(rewritten, ignore_list_markers=not preserve_lists), "수치·날짜·법조문 토큰의 내용 또는 순서가 변경되었습니다"),
        ("quote", _quotes(original), _quotes(rewritten), "직접 인용의 내용 또는 순서가 변경되었습니다"),
        ("footnote_anchor", (before_footnotes[0], before_footnotes[2]), (after_footnotes[0], after_footnotes[2]), "각주 표지의 문단 귀속 또는 순서가 변경되었습니다"),
        ("footnote_definition", (before_footnotes[1], before_footnotes[3]), (after_footnotes[1], after_footnotes[3]), "한 줄·여러 줄 각주 정의가 변경되었습니다"),
    ]
    if not allow_structure_change:
        ordered_checks.append(
            ("table_structure", _table_structure(original), _table_structure(rewritten), "Markdown 표의 행·열 구조가 변경되었습니다")
        )
        if preserve_lists:
            ordered_checks.append(
                ("list_structure", _list_structure(original), _list_structure(rewritten), "명시적으로 보존하기로 한 목록·체크리스트 구조가 변경되었습니다")
            )
    for code, before, after, message in ordered_checks:
        if before != after:
            issues.append(Issue(code, message))
    if not allow_structure_change:
        issues.extend(_heading_issues(original, rewritten))

    placeholders = _increase(PLACEHOLDER_RE, original, rewritten)
    if placeholders:
        issues.append(Issue("placeholder", f"원문보다 미완성 표지가 늘었습니다: {list(placeholders)[:5]}"))
    malformed = _increase(MALFORMED_RE, original, rewritten)
    if malformed:
        issues.append(Issue("malformed_rewrite", f"기계 치환 비문 후보가 새로 생겼습니다: {list(malformed)[:5]}"))
    if rewritten.count("하였") > original.count("하였"):
        issues.append(Issue("register_raise", "원문보다 '-하였-' 표현이 늘었습니다"))

    for name, pattern in CLICHE_PATTERNS:
        before = len(pattern.findall(_outside_fences(original)))
        after = len(pattern.findall(_outside_fences(rewritten)))
        if after > before:
            issues.append(Issue("cliche_injection", f"상투구 '{name}'이 {before}회에서 {after}회로 늘었습니다"))

    before_yo = len(YO_ENDING_RE.findall(_outside_fences(original)))
    after_yo = len(YO_ENDING_RE.findall(_outside_fences(rewritten)))
    if before_yo >= 3 and after_yo < before_yo * 0.5:
        issues.append(Issue("colloquial_erased", f"구어 종결(~요)이 {before_yo}회에서 {after_yo}회로 격감했습니다"))
    return issues


def _required_file(run_dir: Path, name: str, issues: list[Issue]) -> Path | None:
    path = run_dir / name
    if not path.is_file():
        issues.append(Issue("missing_artifact", f"필수 산출물 누락: {name}"))
        return None
    try:
        if not _read(path).strip():
            issues.append(Issue("empty_artifact", f"산출물이 비어 있습니다: {name}"))
    except RuntimeError as exc:
        issues.append(Issue("unreadable_artifact", str(exc)))
        return None
    return path


def _json_object(path: Path, code: str, issues: list[Issue]) -> dict | None:
    try:
        payload = json.loads(_read(path))
    except (RuntimeError, json.JSONDecodeError) as exc:
        issues.append(Issue(code, f"{path.name}을 파싱할 수 없습니다: {exc}"))
        return None
    if not isinstance(payload, dict):
        issues.append(Issue(code, f"{path.name}의 최상위 값은 JSON object여야 합니다"))
        return None
    return payload


def _validate_diagnosis(run_dir: Path, taxonomy_path: Path, issues: list[Issue]) -> None:
    path = _required_file(run_dir, "02_diagnosis.md", issues)
    if path is None:
        return
    diagnosis = _read(path)
    required_sections = ("## 장르·레지스터", "## 지배 패턴 (겨냥 순서)", "## 보존 지침")
    for section in required_sections:
        if section not in diagnosis:
            issues.append(Issue("diagnosis_section", f"진단 섹션 누락: {section}"))

    section_match = re.search(
        r"^## 지배 패턴 \(겨냥 순서\)\s*$\n(?P<body>.*?)(?=^##\s|\Z)",
        diagnosis,
        re.MULTILINE | re.DOTALL,
    )
    rows = DIAG_ROW_RE.findall(section_match.group("body")) if section_match else []
    if not 3 <= len(rows) <= 6:
        issues.append(Issue("diagnosis_count", f"지배 패턴 행은 3~6개여야 합니다: {rows}"))
    if len(rows) != len(set(rows)):
        issues.append(Issue("diagnosis_duplicate_id", f"지배 패턴 ID가 중복됐습니다: {rows}"))

    if not taxonomy_path.is_file():
        issues.append(Issue("taxonomy_missing", f"taxonomy 파일을 찾을 수 없습니다: {taxonomy_path}"))
        return
    valid_ids = {
        identifier
        for identifier, title in TAX_HEADING_RE.findall(_read(taxonomy_path))
        if "보류" not in title and "hold" not in title.lower()
    }
    unknown = [identifier for identifier in rows if identifier not in valid_ids]
    if unknown:
        issues.append(Issue("diagnosis_unknown_id", f"활성 taxonomy에 없는 ID: {unknown}"))


def _validate_summary(final: str, issues: list[Issue]) -> None:
    outside = _outside_fences(final)
    starts = len(SUMMARY_START_RE.findall(outside))
    match = SUMMARY_TAIL_RE.search(outside)
    completed = 1 if match else 0
    if starts != 1 or completed != 1:
        issues.append(Issue("summary_count", f"말미의 완결된 HUMANIZE-SUMMARY가 정확히 1개여야 합니다: starts={starts}, complete_tail={completed}"))
        return
    assert match is not None
    body = match.group("body")
    for field in ("run_id:", "metrics:", "self_check:"):
        if field not in body:
            issues.append(Issue("summary_schema", f"HUMANIZE-SUMMARY 필수 필드 누락: {field}"))


def _validate_rewrite(
    run_dir: Path,
    issues: list[Issue],
    *,
    allow_structure_change: bool,
    preserve_lists: bool,
) -> None:
    original_path = _required_file(run_dir, "01_input.txt", issues)
    final_path = _required_file(run_dir, "final.md", issues)
    if original_path is None or final_path is None:
        return
    original = _read(original_path)
    final = _read(final_path)
    _validate_summary(final, issues)
    issues.extend(
        _fidelity_issues(
            original,
            final,
            allow_structure_change=allow_structure_change,
            preserve_lists=preserve_lists,
        )
    )


def _safe_run_path(run_dir: Path, raw: object, label: str, issues: list[Issue]) -> Path | None:
    if not isinstance(raw, str) or not raw:
        issues.append(Issue("manifest_schema", f"{label}은 비어 있지 않은 문자열이어야 합니다"))
        return None
    candidate = Path(raw)
    if candidate.is_absolute():
        issues.append(Issue("manifest_path", f"{label}은 run directory 상대 경로여야 합니다: {raw}"))
        return None
    resolved = (run_dir / candidate).resolve()
    if not resolved.is_relative_to(run_dir):
        issues.append(Issue("manifest_path", f"{label}이 run directory 밖을 가리킵니다: {raw}"))
        return None
    return resolved


def _validate_chunks(run_dir: Path, issues: list[Issue]) -> None:
    manifest_path = run_dir / "chunk_manifest.json"
    if not manifest_path.exists():
        return
    payload = _json_object(manifest_path, "manifest_json", issues)
    if payload is None:
        return
    if payload.get("version") != 1:
        issues.append(Issue("manifest_version", "chunk manifest version은 1이어야 합니다"))
    chunks = payload.get("chunks")
    if not isinstance(chunks, list) or not chunks:
        issues.append(Issue("manifest_schema", "chunk_manifest.json의 chunks는 비어 있지 않은 배열이어야 합니다"))
        return

    source_path = _safe_run_path(run_dir, payload.get("source_file"), "source_file", issues)
    source = ""
    if source_path is None or not source_path.is_file():
        issues.append(Issue("manifest_source", "manifest source_file이 run directory 안의 파일이 아닙니다"))
    else:
        source = _read(source_path)
        if payload.get("source_chars") != len(source):
            issues.append(Issue("manifest_source", "source_chars가 실제 원문 문자 수와 다릅니다"))
        digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
        if payload.get("source_sha256") != digest:
            issues.append(Issue("manifest_source", "source_sha256이 실제 원문과 다릅니다"))

    body: list[dict] = []
    spans: list[tuple[int, int]] = []
    passthrough_count = 0
    outputs: set[Path] = set()
    body_outputs: list[Path] = []
    indices: list[int] = []
    for position, item in enumerate(chunks, start=1):
        if not isinstance(item, dict):
            issues.append(Issue("manifest_schema", f"chunks[{position}]는 object여야 합니다"))
            continue
        index = item.get("index")
        if type(index) is not int:
            issues.append(Issue("manifest_schema", f"chunks[{position}].index는 정수여야 합니다"))
        else:
            indices.append(index)
        if type(item.get("passthrough")) is not bool:
            issues.append(Issue("manifest_schema", f"chunks[{position}].passthrough는 boolean이어야 합니다"))
            continue
        for key in ("start", "end", "char_count"):
            if type(item.get(key)) is not int:
                issues.append(Issue("manifest_schema", f"chunks[{position}].{key}는 정수여야 합니다"))
        start, end = item.get("start"), item.get("end")
        if type(start) is int and type(end) is int:
            spans.append((start, end))
            if not (0 <= start < end <= len(source)):
                issues.append(Issue("manifest_span", f"chunks[{position}] 범위가 원문 밖이거나 역전됐습니다"))
            if item.get("char_count") != end - start:
                issues.append(Issue("manifest_span", f"chunks[{position}].char_count가 범위 길이와 다릅니다"))
        if item["passthrough"]:
            passthrough_count += 1
            if item.get("input_file") is not None or item.get("rewritten_file") is not None:
                issues.append(Issue("manifest_schema", f"passthrough chunks[{position}]의 파일 필드는 null이어야 합니다"))
            continue
        body.append(item)
        input_path = _safe_run_path(run_dir, item.get("input_file"), f"chunks[{position}].input_file", issues)
        if input_path is not None and not input_path.is_file():
            issues.append(Issue("manifest_input", f"청크 입력 파일이 없습니다: {input_path.name}"))
        output = _safe_run_path(run_dir, item.get("rewritten_file"), f"chunks[{position}].rewritten_file", issues)
        if output is None:
            continue
        if output in outputs:
            issues.append(Issue("manifest_duplicate_output", f"청크 출력 경로가 중복됩니다: {output.name}"))
        outputs.add(output)
        body_outputs.append(output)

    if indices != list(range(1, len(chunks) + 1)):
        issues.append(Issue("manifest_index", f"chunk index가 1부터 연속되지 않습니다: {indices}"))
    if payload.get("chunk_count") != len(chunks):
        issues.append(Issue("manifest_count", "chunk_count와 실제 전체 청크 수가 다릅니다"))
    if type(payload.get("body_chunk_count")) is not int or payload.get("body_chunk_count") != len(body):
        issues.append(Issue("manifest_count", "body_chunk_count와 실제 body 청크 수가 다릅니다"))
    if payload.get("passthrough_chunk_count") != passthrough_count:
        issues.append(Issue("manifest_count", "passthrough_chunk_count와 실제 passthrough 수가 다릅니다"))
    cursor = 0
    for position, (start, end) in enumerate(spans, start=1):
        if start != cursor:
            issues.append(Issue("manifest_coverage", f"chunks[{position}] 앞에 공백 또는 겹침이 있습니다"))
        cursor = end
    if source and cursor != len(source):
        issues.append(Issue("manifest_coverage", "청크 범위가 원문 전체를 덮지 않습니다"))

    if len(body) >= 2:
        for output in body_outputs:
            if not output.is_file() or not _read(output).strip():
                issues.append(Issue("missing_chunk_output", f"청크 윤문본 누락 또는 빈 파일: {output.name}"))
        report_path = _required_file(run_dir, "03_reassembly_report.json", issues)
        if report_path is not None:
            report = _json_object(report_path, "reassembly_json", issues)
            if report is not None:
                warnings = report.get("warnings")
                if not isinstance(warnings, list):
                    issues.append(Issue("reassembly_schema", "reassembly warnings는 배열이어야 합니다"))
                elif warnings:
                    issues.append(Issue("reassembly_warning", f"strict 재조립 경고가 남았습니다: {warnings}"))


def _validate_metrics(run_dir: Path, issues: list[Issue]) -> None:
    metrics = run_dir / "00_metrics.json"
    error = run_dir / "00_metrics.error"
    if metrics.exists() and error.exists():
        issues.append(Issue("metrics_stale", "00_metrics.json과 00_metrics.error가 동시에 존재합니다"))
        return
    if metrics.exists():
        payload = _json_object(metrics, "metrics_json", issues)
        if payload is not None and not payload:
            issues.append(Issue("metrics_schema", "00_metrics.json은 비어 있지 않은 object여야 합니다"))
        return
    if error.exists():
        if not _read(error).strip():
            issues.append(Issue("metrics_error", "00_metrics.error가 비어 있습니다"))
        return
    issues.append(Issue("metrics_artifact", "strict run에는 00_metrics.json 또는 00_metrics.error가 필요합니다"))


def _validate_finalize(run_dir: Path, issues: list[Issue]) -> bool:
    backup = _required_file(run_dir, "final_pre_finalize.md", issues)
    final = _required_file(run_dir, "final.md", issues)
    report_path = _required_file(run_dir, "09_finalize.json", issues)
    if backup is None or final is None or report_path is None:
        return False
    payload = _json_object(report_path, "finalize_json", issues)
    if payload is None:
        return False

    verdict = payload.get("verdict")
    if verdict not in {"accept", "corrected", "hold_and_report"}:
        issues.append(Issue("finalize_verdict", f"허용되지 않은 verdict: {verdict!r}"))
        verdict = None

    fidelity = payload.get("fidelity")
    fidelity_pass: bool | None = None
    fidelity_violations: list[object] | None = None
    if not isinstance(fidelity, dict):
        issues.append(Issue("finalize_fidelity", "fidelity는 object여야 합니다"))
    else:
        if type(fidelity.get("pass")) is not bool:
            issues.append(Issue("finalize_fidelity", "fidelity.pass는 boolean이어야 합니다"))
        else:
            fidelity_pass = fidelity["pass"]
        if not isinstance(fidelity.get("violations"), list):
            issues.append(Issue("finalize_fidelity", "fidelity.violations는 배열이어야 합니다"))
        else:
            fidelity_violations = fidelity["violations"]

    naturalness = payload.get("naturalness")
    if not isinstance(naturalness, dict):
        issues.append(Issue("finalize_naturalness", "naturalness는 object여야 합니다"))
    else:
        for key in ("residual", "over_polish"):
            if not isinstance(naturalness.get(key), list):
                issues.append(Issue("finalize_naturalness", f"naturalness.{key}는 배열이어야 합니다"))

    corrections = payload.get("corrections_applied")
    if type(corrections) is not int or corrections < 0:
        issues.append(Issue("finalize_corrections", "corrections_applied는 0 이상의 정수여야 합니다"))
        corrections = None
    note = payload.get("note")
    if not isinstance(note, str):
        issues.append(Issue("finalize_note", "note는 문자열이어야 합니다"))

    before_body = strip_summary(_read(backup))
    final_body = strip_summary(_read(final))
    if verdict == "accept":
        if fidelity_pass is not True or corrections != 0:
            issues.append(Issue("finalize_inconsistent", "accept는 fidelity.pass=true, corrections_applied=0이어야 합니다"))
        if before_body != final_body:
            issues.append(Issue("finalize_inconsistent", "accept인데 finalizer가 본문을 변경했습니다"))
    elif verdict == "corrected":
        if fidelity_pass is not True or corrections is None or corrections <= 0:
            issues.append(Issue("finalize_inconsistent", "corrected는 fidelity.pass=true, corrections_applied>0이어야 합니다"))
        if before_body == final_body:
            issues.append(Issue("finalize_inconsistent", "corrected인데 실제 본문 변경이 없습니다"))
    elif verdict == "hold_and_report":
        if fidelity_pass is not False:
            issues.append(Issue("finalize_inconsistent", "hold_and_report는 fidelity.pass=false여야 합니다"))
        if fidelity_violations == [] and isinstance(note, str) and not note.strip():
            issues.append(Issue("finalize_inconsistent", "hold_and_report는 미해결 사유를 violations 또는 note에 기록해야 합니다"))
        return True
    return False


def _validate_execution(run_dir: Path, issues: list[Issue]) -> str | None:
    path = _required_file(run_dir, "00_execution.json", issues)
    if path is None:
        return None
    payload = _json_object(path, "execution_json", issues)
    if payload is None:
        return None
    if payload.get("schema_version") != 1:
        issues.append(Issue("execution_schema", "schema_version은 1이어야 합니다"))
    if payload.get("execution_mode") != "delegated" or payload.get("degraded") is not False:
        issues.append(Issue("execution_degraded", "strict run은 execution_mode=delegated, degraded=false여야 합니다"))
    if payload.get("resolved_route") != "heavy":
        issues.append(Issue("execution_route", "strict run의 resolved_route는 heavy여야 합니다"))

    stages = payload.get("stages")
    if not isinstance(stages, dict):
        issues.append(Issue("execution_schema", "stages는 object여야 합니다"))
        return payload.get("status") if isinstance(payload.get("status"), str) else None
    sequences: dict[str, list[int]] = {}
    for stage, minimum, maximum in (("diagnostician", 1, 1), ("monolith", 1, None), ("finalizer", 1, 1)):
        records = stages.get(stage)
        if not isinstance(records, list) or len(records) < minimum or (maximum is not None and len(records) > maximum):
            issues.append(Issue("execution_stage", f"{stage} 완료 기록 수가 잘못됐습니다"))
            continue
        sequences[stage] = []
        for index, record in enumerate(records):
            if not isinstance(record, dict):
                issues.append(Issue("execution_stage", f"{stage}[{index}]는 object여야 합니다"))
                continue
            if record.get("status") != "completed":
                issues.append(Issue("execution_stage", f"{stage}[{index}] status가 completed가 아닙니다"))
            if not isinstance(record.get("delegation_id"), str) or not record["delegation_id"]:
                issues.append(Issue("execution_stage", f"{stage}[{index}] delegation_id가 없습니다"))
            sequence = record.get("sequence")
            if type(sequence) is not int:
                issues.append(Issue("execution_stage", f"{stage}[{index}] sequence는 정수여야 합니다"))
            else:
                sequences[stage].append(sequence)
            output = _safe_run_path(run_dir, record.get("output"), f"{stage}[{index}].output", issues)
            if output is not None and not output.is_file():
                issues.append(Issue("execution_output", f"역할 산출물이 없습니다: {output.name}"))

    if all(sequences.get(name) for name in ("diagnostician", "monolith", "finalizer")):
        if not (
            max(sequences["diagnostician"])
            < min(sequences["monolith"])
            <= max(sequences["monolith"])
            < min(sequences["finalizer"])
        ):
            issues.append(Issue("execution_order", "diagnostician→monolith→finalizer sequence가 보존되지 않았습니다"))

    rate = payload.get("change_rate")
    if not isinstance(rate, dict) or type(rate.get("percent")) not in {int, float} or type(rate.get("exit_code")) is not int:
        issues.append(Issue("execution_rate", "부모가 측정한 change_rate percent/exit_code가 없습니다"))
    elif rate["exit_code"] not in {0, 1}:
        issues.append(Issue("execution_rate", f"채택할 수 없는 change-rate exit code: {rate['exit_code']}"))

    status = payload.get("status")
    if status not in {"completed", "hold_and_report"}:
        issues.append(Issue("execution_status", f"strict 종료 상태가 유효하지 않습니다: {status!r}"))
    return status if isinstance(status, str) else None


def validate_run(
    run_dir: Path,
    stage: str = "all",
    strict: bool = False,
    taxonomy_path: Path | None = None,
    *,
    allow_structure_change: bool = False,
    preserve_lists: bool = False,
) -> tuple[list[Issue], bool]:
    run_dir = run_dir.expanduser().resolve()
    if not run_dir.is_dir():
        raise RuntimeError(f"run directory not found: {run_dir}")
    if taxonomy_path is None:
        taxonomy_path = Path(__file__).resolve().parents[1] / "references" / "ai-tell-taxonomy.md"

    issues: list[Issue] = []
    hold = False
    if strict:
        _validate_metrics(run_dir, issues)
    if stage in {"diagnosis", "all"}:
        _validate_diagnosis(run_dir, taxonomy_path, issues)
    if stage in {"rewrite", "all"}:
        _validate_rewrite(
            run_dir,
            issues,
            allow_structure_change=allow_structure_change,
            preserve_lists=preserve_lists,
        )
        _validate_chunks(run_dir, issues)
    if stage in {"finalize", "all"} or strict:
        hold = _validate_finalize(run_dir, issues)
    if strict:
        execution_status = _validate_execution(run_dir, issues)
        if hold and execution_status not in {None, "hold_and_report"}:
            issues.append(Issue("execution_status", "finalizer hold와 execution 종료 상태가 일치하지 않습니다"))
        if not hold and execution_status == "hold_and_report":
            issues.append(Issue("execution_status", "execution은 hold인데 finalizer verdict가 hold가 아닙니다"))
        if execution_status == "hold_and_report":
            hold = True
    return issues, hold


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise ValueError(message)


def _build_parser() -> argparse.ArgumentParser:
    parser = _Parser(description=__doc__)
    parser.add_argument("--run-dir", required=True, help="humanize run directory")
    parser.add_argument(
        "--stage",
        choices=("diagnosis", "rewrite", "finalize", "all"),
        default="all",
    )
    parser.add_argument("--strict", action="store_true", help="require strict/finalize/provenance artifacts")
    parser.add_argument("--taxonomy", help="override taxonomy path")
    parser.add_argument(
        "--allow-structure-change",
        action="store_true",
        help="skip heading/table checks only when the user explicitly requested restructuring",
    )
    parser.add_argument(
        "--preserve-lists",
        action="store_true",
        help="enforce list/checklist structure only when the user explicitly requested it",
    )
    parser.add_argument("--json", action="store_true", help="emit machine-readable result")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    argv_list = list(argv) if argv is not None else sys.argv[1:]
    wants_json = "--json" in argv_list
    try:
        args = _build_parser().parse_args(argv_list)
    except ValueError as exc:
        payload = {"ok": False, "error": f"usage: {exc}"}
        if wants_json:
            print(json.dumps(payload, ensure_ascii=False))
        else:
            print(f"ERROR — {payload['error']}", file=sys.stderr)
        return 3
    try:
        issues, hold = validate_run(
            Path(args.run_dir),
            stage=args.stage,
            strict=args.strict,
            taxonomy_path=Path(args.taxonomy).expanduser().resolve() if args.taxonomy else None,
            allow_structure_change=args.allow_structure_change,
            preserve_lists=args.preserve_lists,
        )
    except RuntimeError as exc:
        if args.json:
            print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        else:
            print(f"ERROR — {exc}", file=sys.stderr)
        return 3

    payload = {
        "ok": not issues and not hold,
        "hold": hold,
        "issue_count": len(issues),
        "issues": [{"code": item.code, "message": item.message} for item in issues],
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif not issues and not hold:
        print("OK — stage artifacts and deterministic fidelity checks passed")
    else:
        for issue in issues:
            print(issue, file=sys.stderr)
        if hold:
            print("[hold_and_report] finalizer requires human review", file=sys.stderr)
    if issues:
        return 1
    if hold:
        return 2
    return 0


if __name__ == "__main__":
    import console as _console

    _console.force_utf8_console()
    raise SystemExit(main())
