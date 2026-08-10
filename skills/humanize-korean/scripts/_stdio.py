#!/usr/bin/env python3
"""콘솔/스트림의 표준 입출력 인코딩을 UTF-8로 강제한다.

Windows 콘솔(cp949)에서 em dash(—) 같은 비 cp949 문자를 print()할 때
UnicodeEncodeError로 죽는 문제를 방지한다. 판정 문구에 em dash가 들어가는
CLI 게이트(verify_change_rate 등)는 인코딩 실패로 "통과(exit 0) 후 출력 중
크래시 → exit 1"이 되어 호출부가 판정을 오독할 수 있다.

사용법: 각 CLI 스크립트의 main() 첫 줄에서 호출.

    import _stdio  # noqa: E402
    _stdio.force_utf8_stdio()

참고: sys.stdout/stderr를 재구성해 UTF-8로 바꾼다. 파일/파이프 리다이렉트
대상도 포함되므로 크래시 없이 항상 UTF-8 바이트를 출력한다.
"""

from __future__ import annotations

import sys


def force_utf8_stdio() -> None:
    """stdout/stderr를 UTF-8로 재구성한다 (있으면 reconfigure 사용)."""
    for stream in (sys.stdout, sys.stderr):
        # TextIOWrapper가 아닌 대상(예: StringIO, 이미 닫힌 스트림)은 건너뛴다.
        if not hasattr(stream, "reconfigure"):
            continue
        try:
            stream.reconfigure(encoding="utf-8")
        except (ValueError, OSError):
            # 이미 닫혔거나 재구성 불가한 스트림은 무시하고 진행한다.
            pass
