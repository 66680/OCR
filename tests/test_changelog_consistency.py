import json
from pathlib import Path

from scripts import check_changelog_consistency


def test_changelog_consistency_passes_with_matching_version(tmp_path: Path) -> None:
    (tmp_path / "src" / "invstruct").mkdir(parents=True)
    (tmp_path / "src" / "invstruct" / "schema_version.py").write_text(
        "EXPORT_SCHEMA_VERSION = 1\nRECORD_SCHEMA_VERSION = 1\n",
        encoding="utf-8",
    )
    (tmp_path / "CHANGELOG.md").write_text(
        "# Changelog\n\n## v0.1.0\n- Initial release notes.\n",
        encoding="utf-8",
    )

    report = check_changelog_consistency.evaluate_changelog_consistency(
        root=tmp_path,
        version="0.1.0",
        previous_schema_content="EXPORT_SCHEMA_VERSION = 1\nRECORD_SCHEMA_VERSION = 1\n",
        current_schema_content="EXPORT_SCHEMA_VERSION = 1\nRECORD_SCHEMA_VERSION = 1\n",
    )
    assert report["ok"] is True
    assert report["path"] == "CHANGELOG.md"


def test_changelog_consistency_fails_when_version_heading_missing(tmp_path: Path) -> None:
    (tmp_path / "src" / "invstruct").mkdir(parents=True)
    (tmp_path / "src" / "invstruct" / "schema_version.py").write_text(
        "EXPORT_SCHEMA_VERSION = 1\nRECORD_SCHEMA_VERSION = 1\n",
        encoding="utf-8",
    )
    (tmp_path / "CHANGELOG.md").write_text(
        "# Changelog\n\n## v0.0.9\n- Previous release.\n",
        encoding="utf-8",
    )

    report = check_changelog_consistency.evaluate_changelog_consistency(
        root=tmp_path,
        version="0.1.0",
        previous_schema_content="EXPORT_SCHEMA_VERSION = 1\nRECORD_SCHEMA_VERSION = 1\n",
        current_schema_content="EXPORT_SCHEMA_VERSION = 1\nRECORD_SCHEMA_VERSION = 1\n",
    )
    assert report["ok"] is False
    assert report["reason"] == "version_heading_not_found"


def test_changelog_script_writes_report_json(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "src" / "invstruct").mkdir(parents=True)
    (tmp_path / "src" / "invstruct" / "schema_version.py").write_text(
        "EXPORT_SCHEMA_VERSION = 1\nRECORD_SCHEMA_VERSION = 1\n",
        encoding="utf-8",
    )
    (tmp_path / "CHANGELOG.md").write_text(
        "# Changelog\n\n## v0.1.0\n- Migration Notes: none.\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("INVSTRUCT_VERSION", "v0.1.0")
    output_rel = "out/changelog_report.json"

    exit_code = check_changelog_consistency.main(
        ["--root", str(tmp_path), "--output", output_rel]
    )
    assert exit_code == 0

    report_path = tmp_path / output_rel
    assert report_path.exists()
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["version"] == "0.1.0"
    assert "ok" in payload
