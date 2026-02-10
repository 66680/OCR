from __future__ import annotations

import hashlib
import json
from pathlib import Path

import typer

from invstruct.errors import error_payload
from invstruct.schemas import InvoiceRecord, SourceInfo
from invstruct.utils.trace import generate_trace_id

app = typer.Typer(help="invstruct command line interface")


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


def main() -> None:
    app()


if __name__ == "__main__":
    main()
