"""Harden command-line output for legacy Windows console encodings."""

from __future__ import annotations

import sys
import traceback
from collections.abc import Callable


def force_utf8_console() -> None:
    """Use UTF-8 replacement output when a stream supports reconfiguration."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass


def run_gate(main: Callable[[], int], *, error_exit_code: int = 3) -> int:
    """Run a gate with UTF-8 output and map unexpected failures to an error."""
    force_utf8_console()
    try:
        return main()
    except SystemExit:
        raise
    except BaseException as exc:
        print(f"[gate] 실행 오류 — {type(exc).__name__}: {exc}", file=sys.stderr)
        traceback.print_exc()
        return error_exit_code
