from scripts.check_schema_bump_policy import evaluate_tag_policy


def test_tag_mode_requires_migration_notes_when_no_diff_context() -> None:
    ok, reason = evaluate_tag_policy(
        previous_schema_content="",
        head_schema_content="EXPORT_SCHEMA_VERSION = 1\nRECORD_SCHEMA_VERSION = 1\n",
        m1_plan_content="No migration section",
        migrations_content="",
    )
    assert ok is False
    assert "Migration Notes" in reason


def test_tag_mode_passes_when_no_diff_but_notes_exist() -> None:
    ok, reason = evaluate_tag_policy(
        previous_schema_content="",
        head_schema_content="EXPORT_SCHEMA_VERSION = 1\nRECORD_SCHEMA_VERSION = 1\n",
        m1_plan_content="## Migration Notes\n- release note",
        migrations_content="",
    )
    assert ok is True
    assert "Migration Notes" in reason


def test_tag_mode_fails_on_version_change_without_notes() -> None:
    ok, reason = evaluate_tag_policy(
        previous_schema_content="EXPORT_SCHEMA_VERSION = 1\nRECORD_SCHEMA_VERSION = 1\n",
        head_schema_content="EXPORT_SCHEMA_VERSION = 2\nRECORD_SCHEMA_VERSION = 1\n",
        m1_plan_content="No notes",
        migrations_content="",
    )
    assert ok is False
    assert "changed" in reason
