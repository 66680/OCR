from typer.testing import CliRunner

from invstruct.cli import app


def test_cli_help() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "invstruct" in result.output


def test_cli_parse_help() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["parse", "--help"])
    assert result.exit_code == 0
    assert "--allow-pdf" in result.output
