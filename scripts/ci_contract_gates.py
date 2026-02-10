from __future__ import annotations

import json
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
) -> int:
    with tempfile.TemporaryDirectory(prefix="invstruct_ci_gates_") as temp_dir:
        tmp = Path(temp_dir)
        records_path = tmp / "records.jsonl"
        csv_path = tmp / "out.csv"
        xlsx_path = tmp / "out.xlsx"
        _build_sample_records(records_path)

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
            print(json.dumps(output, ensure_ascii=False, sort_keys=True))
            return 0

        for command in commands:
            result = runner(command)
            if result.returncode != 0:
                print(f"[contract-gate] command failed: {' '.join(command)}")
                if result.stdout:
                    print("[stdout]")
                    print(result.stdout)
                if result.stderr:
                    print("[stderr]")
                    print(result.stderr)
                return 1

        endpoint_ok, endpoint_message = _schema_endpoint_smoke()
        if not endpoint_ok:
            print(f"[contract-gate] schema endpoint smoke failed: {endpoint_message}")
            return 1

        print(
            json.dumps(
                {
                    "ok": True,
                    "records_path": str(records_path),
                    "csv_path": str(csv_path),
                    "xlsx_path": str(xlsx_path),
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 0


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    dry_run = "--dry-run" in args
    return run_contract_gates(dry_run=dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
