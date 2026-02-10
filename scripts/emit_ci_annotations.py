from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any


def _parse_max_annotations(raw: str | None, default: int = 5) -> int:
    if not raw:
        return default
    try:
        value = int(raw)
        return value if value > 0 else default
    except ValueError:
        return default


def _escape_command_value(value: str) -> str:
    return value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def _truncate_message(value: str, limit: int = 800) -> str:
    return value if len(value) <= limit else value[: limit - 3] + "..."


def _emit(level: str, title: str, message: str) -> None:
    safe_level = "warning" if level == "warning" else "error"
    print(f"::{safe_level} title={_escape_command_value(title)}::{_escape_command_value(_truncate_message(message))}")


def _emit_notice(title: str, message: str) -> None:
    print(f"::notice title={_escape_command_value(title)}::{_escape_command_value(_truncate_message(message))}")


def _format_step_message(step: dict[str, Any]) -> str:
    name = str(step.get("name", "unknown"))
    command = " ".join(step.get("command", [])) if isinstance(step.get("command"), list) else str(step.get("command", ""))
    stdout_tail = str(step.get("stdout_tail", "")).strip()
    stderr_tail = str(step.get("stderr_tail", "")).strip()
    combined_tail = "\n".join(part for part in [stdout_tail, stderr_tail] if part).strip()
    tail_lines = combined_tail.splitlines()[-8:] if combined_tail else []
    tail_excerpt = " | ".join(line.strip() for line in tail_lines if line.strip())
    suffix = f" tail={tail_excerpt}" if tail_excerpt else ""
    return f"step={name}; command={command};{suffix}"


def emit_annotations_from_report(
    report_path: str | Path,
    *,
    max_annotations: int,
    level: str,
) -> int:
    path = Path(report_path)
    if not path.exists():
        _emit_notice("invstruct gate report", f"report not found: {path}")
        return 0

    report = json.loads(path.read_text(encoding="utf-8"))
    if report.get("ok", False):
        _emit_notice("invstruct gates", f"CI gates ok. report={path}")
        return 0

    emitted = 0
    failed_step = str(report.get("failed_step", "")).strip()
    if failed_step and emitted < max_annotations:
        _emit(
            level,
            "invstruct gate failed",
            f"failed_step={failed_step}; report={path}",
        )
        emitted += 1

    for step in report.get("steps", []):
        if emitted >= max_annotations:
            break
        if not isinstance(step, dict):
            continue
        return_code = int(step.get("returncode", 0))
        ok = bool(step.get("ok", return_code == 0))
        if ok and return_code == 0:
            continue
        _emit(level, "invstruct gate step", _format_step_message(step))
        emitted += 1

    for command in report.get("reproduce_commands", []):
        _emit_notice("invstruct reproduce", str(command))

    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Emit GitHub Actions annotations from ci gate report.")
    parser.add_argument("--report", default=os.getenv("INVSTRUCT_CI_REPORT", "out/ci_gate_report.json"))
    args = parser.parse_args(argv)

    max_annotations = _parse_max_annotations(os.getenv("INVSTRUCT_ANNOTATION_MAX"), default=5)
    level = os.getenv("INVSTRUCT_ANNOTATION_LEVEL", "error").strip().lower()
    level = "warning" if level == "warning" else "error"

    return emit_annotations_from_report(
        args.report,
        max_annotations=max_annotations,
        level=level,
    )


if __name__ == "__main__":
    raise SystemExit(main())
