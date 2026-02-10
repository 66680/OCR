from __future__ import annotations

import csv
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import typer
from openpyxl import Workbook

from invstruct import __version__
from invstruct.contracts.export_schema import (
    REQUIRED_COLUMNS,
    get_export_contract_schema,
    validate_export_csv,
    validate_export_xlsx,
)
from invstruct.contracts.record_schema import get_invoice_record_json_schema
from invstruct.errors import error_payload
from invstruct.schema_version import EXPORT_SCHEMA_VERSION, RECORD_SCHEMA_VERSION
from invstruct.schemas import InvoiceRecord, SourceInfo
from invstruct.utils.trace import generate_trace_id

app = typer.Typer(help="invstruct command line interface")
contract_app = typer.Typer(help="Contract governance commands")
app.add_typer(contract_app, name="contract")


@app.command("parse")
def parse(
    path: Path = typer.Argument(..., exists=True, readable=True),
    allow_pdf: bool = typer.Option(False, "--allow-pdf"),
) -> None:
    trace_id = generate_trace_id()
    suffix = path.suffix.lower()
    if suffix == ".pdf" and not allow_pdf:
        typer.echo(
            json.dumps(
                error_payload(
                    code="E3001",
                    message="PDF not supported yet",
                    trace_id=trace_id,
                    details={"file_name": path.name},
                ),
                ensure_ascii=False,
            )
        )
        raise typer.Exit(code=1)

    payload = path.read_bytes()
    record = InvoiceRecord(
        source=SourceInfo(
            file_name=path.name,
            sha256=hashlib.sha256(payload).hexdigest(),
            trace_id=trace_id,
        ),
        status="success",
    )
    typer.echo(record.to_json())


@app.command("health")
def health() -> None:
    typer.echo("ok")


def _record_to_export_row(record: InvoiceRecord) -> dict[str, str | float | int | None]:
    return {
        "file_name": record.source.file_name,
        "sha256": record.source.sha256,
        "trace_id": record.source.trace_id,
        "merchant": record.merchant,
        "issue_date": record.issue_date,
        "total_amount_gross": record.total_amount_gross,
        "currency": record.currency,
        "status": record.status,
        "error_code": record.error_code,
        "error_message": record.error_message,
        "warnings_count": len(record.warnings),
        "parser_version": record.parser_version,
        "retry_key": record.retry_key,
    }


def _write_export_csv(
    csv_path: Path,
    rows: list[dict[str, str | float | int | None]],
    *,
    no_header_comments: bool,
) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as file_obj:
        if not no_header_comments:
            file_obj.write(f"# invstruct_export_schema_version={EXPORT_SCHEMA_VERSION}\n")
            file_obj.write(f"# generated_at={datetime.now(UTC).isoformat()}\n")
        writer = csv.DictWriter(file_obj, fieldnames=REQUIRED_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in REQUIRED_COLUMNS})


def _write_export_xlsx(
    xlsx_path: Path,
    rows: list[dict[str, str | float | int | None]],
) -> None:
    xlsx_path.parent.mkdir(parents=True, exist_ok=True)
    workbook = Workbook()
    records_sheet = workbook.active
    records_sheet.title = "records"
    records_sheet.append(REQUIRED_COLUMNS)
    for row in rows:
        records_sheet.append([row.get(column, "") for column in REQUIRED_COLUMNS])

    meta_sheet = workbook.create_sheet("_meta")
    meta_sheet["A1"] = "invstruct_export_schema_version"
    meta_sheet["B1"] = EXPORT_SCHEMA_VERSION
    meta_sheet["A2"] = "generated_at"
    meta_sheet["B2"] = datetime.now(UTC).isoformat()
    meta_sheet["A3"] = "tool_version"
    meta_sheet["B3"] = __version__
    workbook.save(xlsx_path)
    workbook.close()


@app.command("export")
def export(
    records_jsonl: Path = typer.Argument(..., exists=True, readable=True),
    csv_path: Path = typer.Option(..., "--csv"),
    xlsx_path: Path = typer.Option(..., "--xlsx"),
    no_header_comments: bool = typer.Option(False, "--no-header-comments"),
) -> None:
    rows: list[dict[str, str | float | int | None]] = []
    with records_jsonl.open("r", encoding="utf-8", errors="ignore") as file_obj:
        for line_no, line in enumerate(file_obj, start=1):
            content = line.strip()
            if not content:
                continue
            try:
                data = json.loads(content)
                record = InvoiceRecord.model_validate(data)
            except Exception as exc:
                trace_id = generate_trace_id()
                typer.echo(
                    json.dumps(
                        error_payload(
                            code="E5002",
                            message="Contract validation failed",
                            trace_id=trace_id,
                            details={"reason": "invalid_record_for_export", "line_no": line_no, "message": str(exc)},
                        ),
                        ensure_ascii=False,
                    )
                )
                raise typer.Exit(code=2)
            rows.append(_record_to_export_row(record))

    _write_export_csv(csv_path, rows, no_header_comments=no_header_comments)
    _write_export_xlsx(xlsx_path, rows)
    typer.echo(
        json.dumps(
            {
                "ok": True,
                "rows": len(rows),
                "csv": str(csv_path),
                "xlsx": str(xlsx_path),
                "export_schema_version": EXPORT_SCHEMA_VERSION,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


@contract_app.command("show")
def contract_show() -> None:
    payload = {
        "tool_version": __version__,
        "record_schema_version": RECORD_SCHEMA_VERSION,
        "export_schema_version": EXPORT_SCHEMA_VERSION,
        "paths": {
            "record_schema": "src/invstruct/contracts/record_schema.py",
            "export_schema": "src/invstruct/contracts/export_schema.py",
        },
    }
    typer.echo(json.dumps(payload, ensure_ascii=False, sort_keys=True))


@contract_app.command("schema")
def contract_schema(
    target: str = typer.Argument(..., help="record|export"),
) -> None:
    if target not in {"record", "export"}:
        trace_id = generate_trace_id()
        typer.echo(
            json.dumps(
                error_payload(
                    code="E5002",
                    message="Contract validation failed",
                    trace_id=trace_id,
                    details={"reason": "schema_target_invalid", "target": target},
                ),
                ensure_ascii=False,
            )
        )
        raise typer.Exit(code=2)

    schema = (
        get_invoice_record_json_schema()
        if target == "record"
        else get_export_contract_schema()
    )
    typer.echo(json.dumps(schema, ensure_ascii=False, sort_keys=True))


@contract_app.command("validate-records")
def validate_records(
    records_jsonl: Path = typer.Argument(..., exists=True, readable=True),
    max_errors: int = typer.Option(10, "--max-errors"),
) -> None:
    total = 0
    valid = 0
    invalid = 0
    invalid_examples: list[dict[str, object]] = []

    with records_jsonl.open("r", encoding="utf-8", errors="ignore") as file_obj:
        for line_no, line in enumerate(file_obj, start=1):
            content = line.strip()
            if not content:
                continue
            total += 1
            try:
                data = json.loads(content)
            except json.JSONDecodeError as exc:
                invalid += 1
                if len(invalid_examples) < max_errors:
                    invalid_examples.append(
                        {
                            "line_no": line_no,
                            "reason": "invalid_json",
                            "message": str(exc),
                        }
                    )
                continue

            try:
                InvoiceRecord.model_validate(data)
                valid += 1
            except Exception as exc:
                invalid += 1
                if len(invalid_examples) < max_errors:
                    trace_id = ""
                    if isinstance(data, dict):
                        source = data.get("source")
                        if isinstance(source, dict):
                            trace_id = str(source.get("trace_id", ""))
                    invalid_examples.append(
                        {
                            "line_no": line_no,
                            "reason": "record_schema_invalid",
                            "trace_id": trace_id,
                            "message": str(exc),
                        }
                    )

    summary = {
        "total": total,
        "ok": valid,
        "invalid": invalid,
        "record_schema_version": RECORD_SCHEMA_VERSION,
    }
    if invalid > 0:
        trace_id = generate_trace_id()
        typer.echo(
            json.dumps(
                error_payload(
                    code="E5002",
                    message="Contract validation failed",
                    trace_id=trace_id,
                    details={
                        "summary": summary,
                        "invalid_examples": invalid_examples,
                    },
                ),
                ensure_ascii=False,
            )
        )
        raise typer.Exit(code=2)

    typer.echo(
        json.dumps(
            {
                "ok": True,
                "summary": summary,
                "invalid_examples": [],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


@contract_app.command("validate-export")
def validate_export(
    csv_path: Path | None = typer.Option(None, "--csv"),
    xlsx_path: Path | None = typer.Option(None, "--xlsx"),
    no_header_comments: bool = typer.Option(False, "--no-header-comments"),
) -> None:
    if csv_path is None and xlsx_path is None:
        trace_id = generate_trace_id()
        typer.echo(
            json.dumps(
                error_payload(
                    code="E5002",
                    message="Contract validation failed",
                    trace_id=trace_id,
                    details={"reason": "missing_export_input"},
                ),
                ensure_ascii=False,
            )
        )
        raise typer.Exit(code=2)

    errors: list[str] = []
    details: dict[str, object] = {}
    if csv_path is not None:
        csv_result = validate_export_csv(
            csv_path,
            expect_version=EXPORT_SCHEMA_VERSION,
            header_comments=not no_header_comments,
        )
        details["csv"] = csv_result.as_dict()
        if not csv_result.ok:
            errors.extend(csv_result.errors)

    if xlsx_path is not None:
        xlsx_result = validate_export_xlsx(
            xlsx_path,
            expect_version=EXPORT_SCHEMA_VERSION,
        )
        details["xlsx"] = xlsx_result.as_dict()
        if not xlsx_result.ok:
            errors.extend(xlsx_result.errors)

    if errors:
        trace_id = generate_trace_id()
        typer.echo(
            json.dumps(
                error_payload(
                    code="E5002",
                    message="Contract validation failed",
                    trace_id=trace_id,
                    details={"errors": errors, "results": details},
                ),
                ensure_ascii=False,
            )
        )
        raise typer.Exit(code=2)

    typer.echo(
        json.dumps(
            {
                "ok": True,
                "export_schema_version": EXPORT_SCHEMA_VERSION,
                "results": details,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


def main() -> None:
    app()


if __name__ == "__main__":
    main()
