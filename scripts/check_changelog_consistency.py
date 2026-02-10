from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any

CHANGELOG_CANDIDATES = ("CHANGELOG.md", "docs/CHANGELOG.md")
VERSION_HEADING_TEMPLATE = r"^##\s+v?{version}\s*$"
SCHEMA_NOTE_PATTERN = re.compile(r"(schema:|migration notes)", re.IGNORECASE)
VERSION_RE = re.compile(r"^\s*(RECORD_SCHEMA_VERSION|EXPORT_SCHEMA_VERSION)\s*=\s*(\d+)\s*$", re.MULTILINE)


def parse_versions(content: str) -> dict[str, int | None]:
    versions: dict[str, int | None] = {"RECORD_SCHEMA_VERSION": None, "EXPORT_SCHEMA_VERSION": None}
    for key, value in VERSION_RE.findall(content):
        versions[key] = int(value)
    return versions


def versions_changed(base_content: str, head_content: str) -> bool:
    base_versions = parse_versions(base_content)
    head_versions = parse_versions(head_content)
    return any(base_versions[key] != head_versions[key] for key in base_versions)


def _extract_version_from_ref(value: str) -> str | None:
    raw = value.strip()
    if not raw:
        return None
    match = re.search(r"v?(\d+\.\d+\.\d+)$", raw)
    if not match:
        return None
    return match.group(1)


def _find_changelog(root: Path) -> Path | None:
    for candidate in CHANGELOG_CANDIDATES:
        path = root / candidate
        if path.exists():
            return path
    return None


def _extract_section(content: str, version: str) -> str | None:
    pattern = re.compile(VERSION_HEADING_TEMPLATE.format(version=re.escape(version)), re.MULTILINE)
    match = pattern.search(content)
    if not match:
        return None
    start = match.end()
    next_heading = re.compile(r"^##\s+.+$", re.MULTILINE).search(content, start)
    end = next_heading.start() if next_heading else len(content)
    return content[start:end].strip()


def _read_previous_schema(root: Path) -> str:
    import subprocess

    result = subprocess.run(
        ["git", "show", "HEAD~1:src/invstruct/schema_version.py"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout


def evaluate_changelog_consistency(
    *,
    root: Path,
    version: str,
    previous_schema_content: str,
    current_schema_content: str,
) -> dict[str, Any]:
    report: dict[str, Any] = {
        "ok": False,
        "version": version,
        "path": None,
        "reason": "",
        "schema_versions": {
            "current": parse_versions(current_schema_content),
            "previous": parse_versions(previous_schema_content),
            "changed": versions_changed(previous_schema_content, current_schema_content)
            if previous_schema_content
            else False,
        },
    }

    changelog_path = _find_changelog(root)
    if changelog_path is None:
        report["reason"] = "changelog_not_found"
        return report

    report["path"] = str(changelog_path.relative_to(root))
    content = changelog_path.read_text(encoding="utf-8", errors="ignore")
    section = _extract_section(content, version)
    if section is None:
        report["reason"] = "version_heading_not_found"
        return report

    if report["schema_versions"]["changed"] and not SCHEMA_NOTE_PATTERN.search(section):
        report["reason"] = "schema_changed_without_migration_notes"
        return report

    report["ok"] = True
    report["reason"] = "ok"
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check changelog consistency for release gates.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", default="out/changelog_report.json")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    output_path = (root / args.output).resolve() if not Path(args.output).is_absolute() else Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    raw_version = os.getenv("INVSTRUCT_VERSION", "").strip() or os.getenv("GITHUB_REF_NAME", "").strip()
    version = _extract_version_from_ref(raw_version)
    if version is None:
        report = {
            "ok": False,
            "version": raw_version,
            "path": None,
            "reason": "version_not_provided",
            "schema_versions": {},
        }
        output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
        return 2

    current_schema_path = root / "src/invstruct/schema_version.py"
    current_schema_content = current_schema_path.read_text(encoding="utf-8", errors="ignore")
    previous_schema_content = _read_previous_schema(root)
    report = evaluate_changelog_consistency(
        root=root,
        version=version,
        previous_schema_content=previous_schema_content,
        current_schema_content=current_schema_content,
    )
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
