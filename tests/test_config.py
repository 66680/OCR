from pathlib import Path

from invstruct.config import load_settings


def test_load_settings_from_yaml(tmp_path: Path) -> None:
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        "app_name: invstruct-custom\nlow_conf_threshold: 0.8\npdf_enabled: true\n",
        encoding="utf-8",
    )
    settings = load_settings(config_file)
    assert settings.app_name == "invstruct-custom"
    assert settings.low_conf_threshold == 0.8
    assert settings.pdf_enabled is True
