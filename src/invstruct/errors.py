from __future__ import annotations

from typing import Any


def error_payload(
    code: str,
    message: str,
    trace_id: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "error": {
            "code": code,
            "message": message,
            "trace_id": trace_id,
            "details": details or {},
        }
    }
