from scripts.check_schema_bump_policy import VERSION_FILE, evaluate_policy, parse_versions


def test_parse_versions_reads_both_constants() -> None:
    payload = "EXPORT_SCHEMA_VERSION = 1\nRECORD_SCHEMA_VERSION = 2\n"
    parsed = parse_versions(payload)
    assert parsed["EXPORT_SCHEMA_VERSION"] == 1
    assert parsed["RECORD_SCHEMA_VERSION"] == 2


def test_evaluate_policy_passes_without_schema_change() -> None:
    ok, reason = evaluate_policy(
        changed_files=["src/invstruct/cli.py"],
        base_schema_content="EXPORT_SCHEMA_VERSION = 1\nRECORD_SCHEMA_VERSION = 1\n",
        head_schema_content="EXPORT_SCHEMA_VERSION = 1\nRECORD_SCHEMA_VERSION = 1\n",
        m1_plan_content="",
        migrations_content="",
    )
    assert ok is True
    assert "not changed" in reason


def test_evaluate_policy_requires_migration_notes_on_version_bump() -> None:
    changed_files = [VERSION_FILE]
    base_content = "EXPORT_SCHEMA_VERSION = 1\nRECORD_SCHEMA_VERSION = 1\n"
    head_content = "EXPORT_SCHEMA_VERSION = 2\nRECORD_SCHEMA_VERSION = 1\n"

    ok_without_notes, _ = evaluate_policy(
        changed_files=changed_files,
        base_schema_content=base_content,
        head_schema_content=head_content,
        m1_plan_content="No special text",
        migrations_content="",
    )
    assert ok_without_notes is False

    ok_with_notes, reason = evaluate_policy(
        changed_files=changed_files,
        base_schema_content=base_content,
        head_schema_content=head_content,
        m1_plan_content="## Migration Notes\n- bump details",
        migrations_content="",
    )
    assert ok_with_notes is True
    assert "Migration Notes" in reason
