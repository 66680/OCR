import json
import subprocess
from pathlib import Path

from scripts import ci_contract_gates


def test_ci_gate_report_written_on_success(tmp_path: Path) -> None:
    report_path = tmp_path / "ci_gate_report.json"

    def fake_success(command: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

    exit_code = ci_contract_gates.run_contract_gates(runner=fake_success, report_path=report_path)
    assert exit_code == 0
    assert report_path.exists()

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["ok"] is True
    assert isinstance(report["steps"], list)
    assert len(report["steps"]) >= 4
    assert all("name" in step for step in report["steps"])


def test_ci_gate_report_written_on_failure(tmp_path: Path) -> None:
    report_path = tmp_path / "ci_gate_report.json"

    def fake_failure(command: list[str]) -> subprocess.CompletedProcess[str]:
        if "export" in command:
            return subprocess.CompletedProcess(command, 1, stdout="bad stdout", stderr="bad stderr")
        return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

    exit_code = ci_contract_gates.run_contract_gates(runner=fake_failure, report_path=report_path)
    assert exit_code == 1
    assert report_path.exists()

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["ok"] is False
    assert report["failed_step"] == "export"
    first_step = report["steps"][0]
    assert first_step["ok"] is False
    assert "bad stderr" in first_step["stderr_tail"]
