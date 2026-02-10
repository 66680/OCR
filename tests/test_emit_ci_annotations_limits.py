import json
from pathlib import Path

from scripts import emit_ci_annotations


def test_emit_annotations_respects_max_and_contains_failed_step(tmp_path: Path, capsys, monkeypatch) -> None:
    report = {
        "ok": False,
        "failed_step": "contract_validate_export",
        "steps": [
            {
                "name": f"step-{index}",
                "command": ["python", "cmd.py", str(index)],
                "returncode": 1,
                "ok": False,
                "stdout_tail": f"stdout {index}",
                "stderr_tail": f"stderr {index}",
            }
            for index in range(10)
        ],
        "reproduce_commands": ["python scripts/ci_contract_gates.py"],
    }
    report_path = tmp_path / "ci_gate_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")

    monkeypatch.setenv("INVSTRUCT_ANNOTATION_MAX", "5")
    monkeypatch.setenv("INVSTRUCT_ANNOTATION_LEVEL", "error")
    exit_code = emit_ci_annotations.main(["--report", str(report_path)])
    assert exit_code == 0

    output_lines = [line for line in capsys.readouterr().out.splitlines() if line.strip()]
    error_lines = [line for line in output_lines if line.startswith("::error ")]
    assert len(error_lines) <= 5
    assert any("failed_step=contract_validate_export" in line for line in error_lines)
