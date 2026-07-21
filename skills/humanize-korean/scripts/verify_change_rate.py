#!/usr/bin/env python3
"""철칙 #4 변경률 게이트 — 결정적 사후 검증.

윤문 전후 변경률을 `metrics_v2.change_rate()`로 계산해 exit code로 게이트한다.
Hermes agent가 윤문본을 쓴 뒤 terminal에서 1회 실행한다.

왜 필요한가: 변경률은 철칙 #4(30% 경고 / 50% 강제 중단)의 게이트 수치인데,
지금까지 통제 대상인 에이전트가 스스로 계산해 자가 보고했다. LLM 산수는
부정확하므로 과윤문 가드 자체가 무른 상태였다. 이 스크립트가 SSOT다.

final.md 본문 끝의 `<!-- HUMANIZE-SUMMARY -->` 주석 블록은 윤문 산출물이 아니라
메타데이터이므로 비교 전에 제거한다. 제거하지 않으면 변경률이 부풀려진다.

Exit code:
    0 — 수렴 (변경률 < 30%)
    1 — 경고 (30% <= 변경률 < 50%). Hermes agent가 사용자에게 고지.
    2 — 중단 (변경률 >= 50%). 윤문본 채택 금지, 롤백 또는 사람 검토.
    3 — 실행 오류 (입력 파일 없음 등). 게이트 판정 불가.

CLI:
    python3 scripts/verify_change_rate.py \
        --before _workspace/{run_id}/01_input.txt \
        --after  _workspace/{run_id}/final.md
    python3 scripts/verify_change_rate.py --before a.txt --after b.md --ignore-markup
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_REFS = os.path.join(_HERE, "..", "references")
_REFS = os.path.abspath(_REFS)
if _REFS not in sys.path:
    sys.path.insert(0, _REFS)

import metrics_v2 as _m  # noqa: E402  (sys.path mutation is intentional)

# final.md 본문 끝의 메타데이터 주석 블록. 여는 마커부터 파일 끝까지.
_SUMMARY_BLOCK_RE = re.compile(r"<!--\s*HUMANIZE-SUMMARY\b.*", re.DOTALL)
_SUMMARY_TAIL_RE = re.compile(
    r"<!--\s*HUMANIZE-SUMMARY\b(?P<body>.*?)-->\s*\Z",
    re.DOTALL,
)


def strip_summary_block(text: str) -> str:
    """final.md에서 `<!-- HUMANIZE-SUMMARY -->` 메타 블록을 제거한다.

    블록이 없으면 원문 그대로 반환한다 (01_input.txt 등에 안전).
    """
    return _SUMMARY_BLOCK_RE.sub("", text).strip()


def _read(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _atomic_text(path: Path, text: str) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def stamp_summary(path: str, pct: float, code: int, scope: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    match = _SUMMARY_TAIL_RE.search(text)
    if match is None:
        raise ValueError("완결된 말미 HUMANIZE-SUMMARY 블록이 없습니다")
    body = match.group("body")
    values = {
        "change_rate_actual": f"{pct:.1f}%",
        "gate_exit": str(code),
        "change_rate_scope": scope,
    }
    for key, value in values.items():
        pattern = re.compile(rf"(?m)^\s{{2}}{re.escape(key)}:\s*.*$")
        replacement = f"  {key}: {value}"
        if pattern.search(body):
            body = pattern.sub(replacement, body, count=1)
        else:
            metrics = re.search(r"(?m)^metrics:\s*$", body)
            if metrics is None:
                raise ValueError("HUMANIZE-SUMMARY에 metrics 섹션이 없습니다")
            insert_at = metrics.end()
            body = body[:insert_at] + "\n" + replacement + body[insert_at:]
    stamped = text[: match.start("body")] + body + text[match.end("body") :]
    _atomic_text(target, stamped)


def stamp_execution_state(path: str, pct: float, code: int, scope: str) -> None:
    target = Path(path)
    payload = json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("execution state 최상위 값이 object가 아닙니다")
    payload["change_rate"] = {
        "percent": round(pct, 3),
        "exit_code": code,
        "scope": scope,
    }
    _atomic_text(target, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="철칙 #4 변경률 게이트")
    p.add_argument("--before", required=True, help="원문 경로 (01_input.txt)")
    p.add_argument("--after", required=True, help="윤문본 경로 (final.md)")
    p.add_argument(
        "--ignore-markup",
        action="store_true",
        help="마크업 줄·줄머리 장식을 제외하고 본문만 비교 "
        "(헤딩·불릿 산문화가 변경률을 부풀리는 경우)",
    )
    p.add_argument(
        "--stamp-summary",
        action="store_true",
        help="계산값을 --after 파일의 HUMANIZE-SUMMARY에 기록",
    )
    p.add_argument(
        "--execution-state",
        help="계산값을 기록할 00_execution.json 경로",
    )
    args = p.parse_args(argv)

    for path in (args.before, args.after):
        if not os.path.exists(path):
            print(f"error: 파일 없음: {path}", file=sys.stderr)
            return 3

    before = strip_summary_block(_read(args.before))
    after = strip_summary_block(_read(args.after))

    rate = _m.change_rate(before, after, ignore_markup=args.ignore_markup)
    pct = rate * 100

    if rate >= _m.CHANGE_RATE_ABORT:
        verdict, code = "ABORT — 강제 중단. 윤문본 채택 금지", 2
    elif rate >= _m.CHANGE_RATE_WARN:
        verdict, code = "WARN — 과윤문 경고. 사용자 고지 필요", 1
    else:
        verdict, code = "OK — 수렴", 0

    scope = "본문만 (마크업 제외)" if args.ignore_markup else "전문"
    scope_key = "body" if args.ignore_markup else "full"
    try:
        if args.stamp_summary:
            stamp_summary(args.after, pct, code, scope_key)
        if args.execution_state:
            stamp_execution_state(args.execution_state, pct, code, scope_key)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: 게이트 결과 기록 실패: {exc}", file=sys.stderr)
        return 3
    print(f"change_rate: {pct:.1f}%  [{scope}]")
    print(
        f"gate: {verdict}  "
        f"(경고 {_m.CHANGE_RATE_WARN * 100:.0f}% / 중단 {_m.CHANGE_RATE_ABORT * 100:.0f}%)"
    )
    return code


if __name__ == "__main__":
    sys.exit(main())
