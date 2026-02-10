from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

VERSION_FILE = "src/invstruct/schema_version.py"
M1_PLAN_FILE = "docs/plans/M1_plan.md"
MIGRATIONS_FILE = "docs/migrations.md"
MIGRATION_KEYWORD_PATTERN = re.compile(r"migration notes", re.IGNORECASE)
_VERSION_RE = re.compile(r"^\s*(RECORD_SCHEMA_VERSION|EXPORT_SCHEMA_VERSION)\s*=\s*(\d+)\s*$", re.MULTILINE)


def parse_versions(content: str) -> dict[str, int | None]:
    versions: dict[str, int | None] = {"RECORD_SCHEMA_VERSION": None, "EXPORT_SCHEMA_VERSION": None}
    for key, value in _VERSION_RE.findall(content):
        versions[key] = int(value)
    return versions


def versions_changed(base_content: str, head_content: str) -> bool:
    base_versions = parse_versions(base_content)
    head_versions = parse_versions(head_content)
    return any(base_versions[key] != head_versions[key] for key in base_versions)


def has_migration_notes(*docs_content: str) -> bool:
    return any(MIGRATION_KEYWORD_PATTERN.search(content or "") for content in docs_content)


def evaluate_policy(
    changed_files: list[str],
    *,
    base_schema_content: str,
    head_schema_content: str,
    m1_plan_content: str,
    migrations_content: str,
) -> tuple[bool, str]:
    if VERSION_FILE not in changed_files:
        return True, "schema_version.py not changed; policy check passed."

    if not versions_changed(base_schema_content, head_schema_content):
        return True, "schema_version.py changed but version numbers unchanged; policy check passed."

    if has_migration_notes(m1_plan_content, migrations_content):
        return True, "Schema version changed and Migration Notes were provided."

    return (
        False,
        "Schema version was changed, but Migration Notes were not found in docs/plans/M1_plan.md or docs/migrations.md.",
    )


def evaluate_tag_policy(
    *,
    previous_schema_content: str,
    head_schema_content: str,
    m1_plan_content: str,
    migrations_content: str,
) -> tuple[bool, str]:
    has_notes = has_migration_notes(m1_plan_content, migrations_content)

    if not previous_schema_content.strip():
        if has_notes:
            return True, "Tag mode: no previous schema diff context; Migration Notes found."
        return False, "Tag mode: no previous schema diff context and Migration Notes missing."

    if versions_changed(previous_schema_content, head_schema_content):
        if has_notes:
            return True, "Tag mode: schema versions changed and Migration Notes were provided."
        return False, "Tag mode: schema versions changed but Migration Notes were not found."

    return True, "Tag mode: schema versions unchanged."


def _run_git_command(args: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(["git", *args], capture_output=True, text=True, check=False)
    return result.returncode, result.stdout, result.stderr


def _get_changed_files(base_ref: str) -> list[str] | None:
    returncode, stdout, stderr = _run_git_command(["diff", "--name-only", f"origin/{base_ref}...HEAD"])
    if returncode != 0:
        print("[schema-policy] failed to read git diff")
        if stdout:
            print(stdout)
        if stderr:
            print(stderr)
        return None
    return [line.strip() for line in stdout.splitlines() if line.strip()]


def _get_ref_file_content(ref: str, path: str) -> str:
    returncode, stdout, _ = _run_git_command(["show", f"{ref}:{path}"])
    if returncode != 0:
        return ""
    return stdout


def main() -> int:
    policy_mode = os.getenv("INVSTRUCT_POLICY_MODE", "").strip().lower()
    ref_type = os.getenv("GITHUB_REF_TYPE", "").strip().lower()
    tag_mode = policy_mode == "tag" or ref_type == "tag"
    if tag_mode:
        head_schema_content = Path(VERSION_FILE).read_text(encoding="utf-8", errors="ignore")
        previous_schema_content = _get_ref_file_content("HEAD~1", VERSION_FILE)
        m1_plan_content = (
            Path(M1_PLAN_FILE).read_text(encoding="utf-8", errors="ignore") if Path(M1_PLAN_FILE).exists() else ""
        )
        migrations_content = (
            Path(MIGRATIONS_FILE).read_text(encoding="utf-8", errors="ignore") if Path(MIGRATIONS_FILE).exists() else ""
        )
        ok, reason = evaluate_tag_policy(
            previous_schema_content=previous_schema_content,
            head_schema_content=head_schema_content,
            m1_plan_content=m1_plan_content,
            migrations_content=migrations_content,
        )
        print(f"[schema-policy] {reason}")
        return 0 if ok else 2

    base_ref = os.getenv("GITHUB_BASE_REF", "").strip()
    if not base_ref:
        print("[schema-policy] no GITHUB_BASE_REF available, no diff context; pass.")
        return 0

    changed_files = _get_changed_files(base_ref)
    if changed_files is None:
        return 1

    if VERSION_FILE not in changed_files:
        print("[schema-policy] VERSION file not changed; pass.")
        return 0

    base_schema_content = _get_ref_file_content(f"origin/{base_ref}", VERSION_FILE)
    head_schema_content = Path(VERSION_FILE).read_text(encoding="utf-8", errors="ignore")
    m1_plan_content = Path(M1_PLAN_FILE).read_text(encoding="utf-8", errors="ignore") if Path(M1_PLAN_FILE).exists() else ""
    migrations_content = (
        Path(MIGRATIONS_FILE).read_text(encoding="utf-8", errors="ignore") if Path(MIGRATIONS_FILE).exists() else ""
    )

    ok, reason = evaluate_policy(
        changed_files,
        base_schema_content=base_schema_content,
        head_schema_content=head_schema_content,
        m1_plan_content=m1_plan_content,
        migrations_content=migrations_content,
    )
    if ok:
        print(f"[schema-policy] {reason}")
        return 0

    print(f"[schema-policy] {reason}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
