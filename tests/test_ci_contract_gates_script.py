import json
import subprocess
from pathlib import Path

from scripts import ci_contract_gates


def test_build_sample_records_writes_two_lines(tmp_path: Path) -> None:
    records_path = tmp_path / "records.jsonl"
    ci_contract_gates._build_sample_records(records_path)
    lines = [line for line in records_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) == 2
    first = json.loads(lines[0])
    second = json.loads(lines[1])
    assert first["status"] == "success"
    assert second["status"] == "skipped"


def test_run_contract_gates_prints_subprocess_failure(capsys) -> None:
    def fake_runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        if "validate-export" in command:
            return subprocess.CompletedProcess(command, 1, stdout="bad stdout", stderr="bad stderr")
        return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

    exit_code = ci_contract_gates.run_contract_gates(runner=fake_runner)
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "bad stderr" in captured.out
    assert "command failed" in captured.out
