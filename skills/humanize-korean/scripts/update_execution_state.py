#!/usr/bin/env python3
"""Create and update humanize-korean execution provenance.

The parent Hermes agent records verified delegation completions here. Child
self-reports are not accepted as provenance; `record` refuses missing outputs.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

FILE_NAME = "00_execution.json"
STAGES = ("diagnostician", "monolith", "finalizer")


def _atomic_write(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _run_dir(raw: str) -> Path:
    path = Path(raw).expanduser().resolve()
    if not path.is_dir():
        raise ValueError(f"run directory not found: {path}")
    return path


def _load(run_dir: Path) -> tuple[Path, dict[str, Any]]:
    path = run_dir / FILE_NAME
    if not path.is_file():
        raise ValueError(f"{FILE_NAME} not found; run init first")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {FILE_NAME}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{FILE_NAME} root must be an object")
    return path, payload


def _relative_verified_output(run_dir: Path, raw: str) -> str:
    path = Path(raw).expanduser()
    resolved = path.resolve() if path.is_absolute() else (run_dir / path).resolve()
    if not resolved.is_relative_to(run_dir):
        raise ValueError(f"output must stay inside run directory: {resolved}")
    if not resolved.is_file() or not resolved.read_text(encoding="utf-8").strip():
        raise ValueError(f"verified output missing or empty: {resolved}")
    return str(resolved.relative_to(run_dir))


def _next_sequence(payload: dict[str, Any]) -> int:
    values: list[int] = []
    stages = payload.get("stages", {})
    if isinstance(stages, dict):
        for records in stages.values():
            if not isinstance(records, list):
                continue
            for record in records:
                if isinstance(record, dict) and type(record.get("sequence")) is int:
                    values.append(record["sequence"])
    return max(values, default=0) + 1


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init")
    init.add_argument("--run-dir", required=True)
    init.add_argument("--run-id", required=True)
    init.add_argument("--requested-mode", required=True)
    init.add_argument("--resolved-route", choices=("light", "standard", "heavy"), required=True)
    init.add_argument("--route-source", required=True)
    init.add_argument(
        "--execution-mode",
        choices=("delegated", "degraded_in_process"),
        default="delegated",
    )
    init.add_argument("--force", action="store_true")

    record = sub.add_parser("record")
    record.add_argument("--run-dir", required=True)
    record.add_argument("--stage", choices=STAGES, required=True)
    record.add_argument("--delegation-id", required=True)
    record.add_argument("--output", required=True)
    record.add_argument("--batch-id")
    record.add_argument("--task-index", type=int)

    rate = sub.add_parser("rate")
    rate.add_argument("--run-dir", required=True)
    rate.add_argument("--percent", type=float, required=True)
    rate.add_argument("--exit-code", type=int, choices=(0, 1, 2, 3), required=True)
    rate.add_argument("--scope", choices=("full", "body"), default="full")

    finish = sub.add_parser("finish")
    finish.add_argument("--run-dir", required=True)
    finish.add_argument(
        "--status",
        choices=("completed", "hold_and_report", "delegation_unavailable", "failed"),
        required=True,
    )
    finish.add_argument("--note", default="")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        run_dir = _run_dir(args.run_dir)
        path = run_dir / FILE_NAME
        if args.command == "init":
            if path.exists() and not args.force:
                raise ValueError(f"{FILE_NAME} already exists; refuse to overwrite")
            execution_mode = args.execution_mode
            payload: dict[str, Any] = {
                "schema_version": 1,
                "run_id": args.run_id,
                "requested_mode": args.requested_mode,
                "resolved_route": args.resolved_route,
                "route_source": args.route_source,
                "execution_mode": execution_mode,
                "degraded": execution_mode != "delegated",
                "stages": {name: [] for name in STAGES},
                "change_rate": None,
                "status": "running",
                "note": "",
            }
            _atomic_write(path, payload)
        elif args.command == "record":
            path, payload = _load(run_dir)
            if payload.get("status") != "running":
                raise ValueError("cannot record a stage after execution is finished")
            stages = payload.get("stages")
            if not isinstance(stages, dict) or not isinstance(stages.get(args.stage), list):
                raise ValueError("execution stages schema is invalid")
            output = _relative_verified_output(run_dir, args.output)
            record: dict[str, Any] = {
                "sequence": _next_sequence(payload),
                "status": "completed",
                "delegation_id": args.delegation_id,
                "output": output,
            }
            if args.batch_id:
                record["batch_id"] = args.batch_id
            if args.task_index is not None:
                if args.task_index < 0:
                    raise ValueError("task-index must be non-negative")
                record["task_index"] = args.task_index
            stages[args.stage].append(record)
            _atomic_write(path, payload)
        elif args.command == "rate":
            path, payload = _load(run_dir)
            payload["change_rate"] = {
                "percent": round(args.percent, 3),
                "exit_code": args.exit_code,
                "scope": args.scope,
            }
            _atomic_write(path, payload)
        elif args.command == "finish":
            path, payload = _load(run_dir)
            payload["status"] = args.status
            payload["note"] = args.note
            _atomic_write(path, payload)
        print(path)
        return 0
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    import console as _console

    _console.force_utf8_console()
    raise SystemExit(main())
