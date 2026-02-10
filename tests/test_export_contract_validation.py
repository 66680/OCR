from pathlib import Path

from openpyxl import Workbook
from typer.testing import CliRunner

from invstruct.cli import app
from invstruct.contracts.export_schema import REQUIRED_COLUMNS
from invstruct.schema_version import EXPORT_SCHEMA_VERSION


def _write_csv(path: Path, include_comments: bool) -> None:
    lines: list[str] = []
    if include_comments:
        lines.extend(
            [
                f"# invstruct_export_schema_version={EXPORT_SCHEMA_VERSION}",
                "# generated_at=2026-02-10T00:00:00+00:00",
            ]
        )
    lines.append(",".join(REQUIRED_COLUMNS))
    lines.append(",".join(["v" for _ in REQUIRED_COLUMNS]))
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_xlsx(path: Path) -> None:
    workbook = Workbook()
    records_sheet = workbook.active
    records_sheet.title = "records"
    records_sheet.append(REQUIRED_COLUMNS)
    records_sheet.append(["value" for _ in REQUIRED_COLUMNS])
    meta_sheet = workbook.create_sheet("_meta")
    meta_sheet["A1"] = "invstruct_export_schema_version"
    meta_sheet["B1"] = EXPORT_SCHEMA_VERSION
    meta_sheet["A2"] = "generated_at"
    meta_sheet["B2"] = "2026-02-10T00:00:00+00:00"
    workbook.save(path)
    workbook.close()


def test_validate_export_with_and_without_header_comments(tmp_path: Path) -> None:
    csv_path = tmp_path / "export.csv"
    xlsx_path = tmp_path / "export.xlsx"
    _write_csv(csv_path, include_comments=True)
    _write_xlsx(xlsx_path)

    runner = CliRunner()
    ok_result = runner.invoke(
        app,
        [
            "contract",
            "validate-export",
            "--csv",
            str(csv_path),
            "--xlsx",
            str(xlsx_path),
        ],
    )
    assert ok_result.exit_code == 0

    csv_no_comments = tmp_path / "export_no_comments.csv"
    _write_csv(csv_no_comments, include_comments=False)
    fail_result = runner.invoke(
        app,
        ["contract", "validate-export", "--csv", str(csv_no_comments)],
    )
    assert fail_result.exit_code == 2

    no_comment_result = runner.invoke(
        app,
        [
            "contract",
            "validate-export",
            "--csv",
            str(csv_no_comments),
            "--no-header-comments",
        ],
    )
    assert no_comment_result.exit_code == 0
