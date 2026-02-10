from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_package_release_module():
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "package_release.py"
    spec = importlib.util.spec_from_file_location("package_release_script", script_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_pick_dist_artifacts_only_current_version(tmp_path: Path):
    module = _load_package_release_module()
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)

    (dist_dir / "invstruct-0.1.0-py3-none-any.whl").write_text("x", encoding="utf-8")
    (dist_dir / "invstruct-0.1.0.tar.gz").write_text("x", encoding="utf-8")
    (dist_dir / "invstruct-0.1.1-py3-none-any.whl").write_text("x", encoding="utf-8")
    (dist_dir / "invstruct-0.1.1.tar.gz").write_text("x", encoding="utf-8")
    (dist_dir / "other-0.1.0.whl").write_text("x", encoding="utf-8")

    picked = module.pick_dist_artifacts(dist_dir, "0.1.0")

    assert [item.name for item in picked] == [
        "invstruct-0.1.0-py3-none-any.whl",
        "invstruct-0.1.0.tar.gz",
    ]
