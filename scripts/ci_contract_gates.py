from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable

from fastapi.testclient import TestClient

from invstruct.api.app import app
from invstruct.schemas import InvoiceRecord, SourceInfo


def _run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, check=False)


def _tail_text(text: str, *, max_lines: int = 200, max_bytes: int = 8192) -> str:
    if not text:
        return ""
    clipped_bytes = text.encode("utf-8", errors="ignore")[-max_bytes:]
    clipped = clipped_bytes.decode("utf-8", errors="ignore")
    lines = clipped.splitlines()
    return "\n".join(lines[-max_lines:])


def _resolve_report_path(report_path: str | Path | None = None) -> Path:
    if report_path is not None:
        resolved = Path(report_path)
    else:
        resolved = Path(os.getenv("INVSTRUCT_CI_REPORT", "out/ci_gate_report.json"))
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved


def _write_report(report: dict, report_path: str | Path | None = None) -> Path:
    target = _resolve_report_path(report_path)
    target.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2), encoding="utf-8")
    return target


def _build_sample_records(records_path: Path) -> None:
    success_record = InvoiceRecord(
        source=SourceInfo(file_name="invoice-a.png", sha256="a" * 64, trace_id="trace-a"),
        status="success",
        merchant="Demo Merchant",
        currency="CNY",
    )
    skipped_record = InvoiceRecord(
        source=SourceInfo(file_name="invoice-b.pdf", sha256="b" * 64, trace_id="trace-b"),
        status="skipped",
        error_code="E3001",
        error_message="PDF not supported yet",
    )
    records_path.write_text(
        f"{success_record.model_dump_json()}\n{skipped_record.model_dump_json()}\n",
        encoding="utf-8",
    )


def _schema_endpoint_smoke() -> tuple[bool, str]:
    client = TestClient(app)
    targets = [
        "/v1/meta/contracts",
        "/v1/meta/contracts/record-schema",
        "/v1/meta/contracts/export-schema",
    ]
    for target in targets:
        response = client.get(target)
        if response.status_code != 200:
            return False, f"{target} returned {response.status_code}"
    return True, ""


def run_contract_gates(
    runner: Callable[[list[str]], subprocess.CompletedProcess[str]] = _run_command,
    *,
    dry_run: bool = False,
    report_path: str | Path | None = None,
) -> int:
    with tempfile.TemporaryDirectory(prefix="invstruct_ci_gates_") as temp_dir:
        tmp = Path(temp_dir)
        records_path = tmp / "records.jsonl"
        csv_path = tmp / "out.csv"
        xlsx_path = tmp / "out.xlsx"
        _build_sample_records(records_path)
        report: dict[str, object] = {
            "ok": False,
            "records_path": str(records_path),
            "csv_path": str(csv_path),
            "xlsx_path": str(xlsx_path),
            "steps": [],
            "reproduce_commands": [
                "python scripts/ci_contract_gates.py",
                "python scripts/check_schema_bump_policy.py",
            ],
        }

        commands = [
            [
                sys.executable,
                "-m",
                "invstruct.cli",
                "export",
                str(records_path),
                "--csv",
                str(csv_path),
                "--xlsx",
                str(xlsx_path),
            ],
            [
                sys.executable,
                "-m",
                "invstruct.cli",
                "contract",
                "validate-records",
                str(records_path),
            ],
            [
                sys.executable,
                "-m",
                "invstruct.cli",
                "contract",
                "validate-export",
                "--csv",
                str(csv_path),
                "--xlsx",
                str(xlsx_path),
            ],
        ]

        if dry_run:
            output = {
                "ok": True,
                "dry_run": True,
                "records_path": str(records_path),
                "commands": commands,
            }
            report["ok"] = True
            report["dry_run"] = True
            report["commands"] = commands
            report["steps"] = [
                {
                    "name": "dry-run",
                    "ok": True,
                    "commands": commands,
                }
            ]
            report_file = _write_report(report, report_path=report_path)
            output["report_path"] = str(report_file)
            print(json.dumps(output, ensure_ascii=False, sort_keys=True))
            return 0

        for command in commands:
            result = runner(command)
            step_entry = {
                "name": command[3] if len(command) > 3 else "command",
                "command": command,
                "returncode": result.returncode,
                "stdout_tail": _tail_text(result.stdout),
                "stderr_tail": _tail_text(result.stderr),
                "ok": result.returncode == 0,
            }
            report["steps"].append(step_entry)
            if result.returncode != 0:
                print(f"[contract-gate] command failed: {' '.join(command)}")
                if result.stdout:
                    print("[stdout]")
                    print(result.stdout)
                if result.stderr:
                    print("[stderr]")
                    print(result.stderr)
                report["failed_step"] = step_entry["name"]
                report["ok"] = False
                report_file = _write_report(report, report_path=report_path)
                print(f"[contract-gate] report written: {report_file}")
                return 1

        endpoint_ok, endpoint_message = _schema_endpoint_smoke()
        endpoint_step = {
            "name": "schema_endpoint_smoke",
            "ok": endpoint_ok,
            "returncode": 0 if endpoint_ok else 1,
            "stdout_tail": endpoint_message if endpoint_ok else "",
            "stderr_tail": endpoint_message if not endpoint_ok else "",
        }
        report["steps"].append(endpoint_step)
        if not endpoint_ok:
            print(f"[contract-gate] schema endpoint smoke failed: {endpoint_message}")
            report["failed_step"] = endpoint_step["name"]
            report["ok"] = False
            report_file = _write_report(report, report_path=report_path)
            print(f"[contract-gate] report written: {report_file}")
            return 1

        report["ok"] = True
        report_file = _write_report(report, report_path=report_path)
        print(
            json.dumps(
                {
                    "ok": True,
                    "records_path": str(records_path),
                    "csv_path": str(csv_path),
                    "xlsx_path": str(xlsx_path),
                    "report_path": str(report_file),
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 0


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    dry_run = "--dry-run" in args
    report_path = os.getenv("INVSTRUCT_CI_REPORT", "out/ci_gate_report.json")
    return run_contract_gates(dry_run=dry_run, report_path=report_path)


if __name__ == "__main__":
    raise SystemExit(main())
