from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="INVSTRUCT_", extra="ignore")

    app_name: str = "invstruct"
    low_conf_threshold: float = 0.75
    pdf_enabled: bool = False


def load_yaml_config(path: str | Path) -> dict[str, Any]:
    config_path = Path(path)
    if not config_path.exists():
        return {}
    parsed = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    if isinstance(parsed, dict):
        return parsed
    return {}


def load_settings(path: str | Path | None = None) -> Settings:
    if path is None:
        return Settings()
    overrides = load_yaml_config(path)
    return Settings(**overrides)
