import json
from pathlib import Path

from scripts import emit_ci_annotations


def test_emit_annotations_ok_report_outputs_notice(tmp_path: Path, capsys) -> None:
    report = {
        "ok": True,
        "steps": [],
        "reproduce_commands": [],
    }
    report_path = tmp_path / "ci_gate_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")

    exit_code = emit_ci_annotations.main(["--report", str(report_path)])
    assert exit_code == 0

    output = capsys.readouterr().out
    assert output.startswith("::notice ")
    assert "CI gates ok" in output
