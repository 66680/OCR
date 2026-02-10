from __future__ import annotations

import hashlib
import re
import zipfile
from pathlib import Path

DIST_WHEEL_RE = r"^invstruct-{version}-.*\.whl$"
DIST_SDIST_RE = r"^invstruct-{version}\.tar\.gz$"


def _load_version(pyproject_path: Path) -> str:
    text = pyproject_path.read_text(encoding="utf-8")
    match = re.search(r'(?ms)^\[project\]\n.*?^version\s*=\s*"([^"]+)"\s*$', text)
    if not match:
        raise ValueError("Could not find [project].version in pyproject.toml")
    return match.group(1)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pick_dist_artifacts(dist_dir: Path, version: str) -> list[Path]:
    wheel_pattern = re.compile(DIST_WHEEL_RE.format(version=re.escape(version)))
    sdist_pattern = re.compile(DIST_SDIST_RE.format(version=re.escape(version)))
    selected: list[Path] = []
    for path in sorted(dist_dir.glob("*")):
        if not path.is_file():
            continue
        name = path.name
        if wheel_pattern.fullmatch(name) or sdist_pattern.fullmatch(name):
            selected.append(path)
    return selected


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    version = _load_version(repo_root / "pyproject.toml")

    dist_dir = repo_root / "dist"
    dist_files = pick_dist_artifacts(dist_dir, version) if dist_dir.exists() else []
    if not dist_files:
        raise FileNotFoundError(
            f"dist/ missing artifacts for version {version}; run `python -m build` first",
        )

    required_files = [
        repo_root / "docs" / "api" / "openapi.json",
        repo_root / "docs" / "api" / "examples.md",
        repo_root / "scripts" / "demo.sh",
        repo_root / "scripts" / "demo.ps1",
    ]
    missing = [path for path in required_files if not path.exists()]
    if missing:
        missing_text = ", ".join(str(path.relative_to(repo_root)) for path in missing)
        raise FileNotFoundError(f"missing required artifacts: {missing_text}")

    release_dir = repo_root / "release"
    release_dir.mkdir(parents=True, exist_ok=True)
    bundle_path = release_dir / f"invstruct_{version}_release_bundle.zip"

    with zipfile.ZipFile(bundle_path, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in dist_files:
            archive.write(path, arcname=f"dist/{path.name}")
        for path in required_files:
            archive.write(path, arcname=str(path.relative_to(repo_root)).replace("\\", "/"))

    checksum = _sha256_file(bundle_path)
    checksum_path = release_dir / f"invstruct_{version}_release_bundle.sha256"
    checksum_path.write_text(f"{checksum}  {bundle_path.name}\n", encoding="utf-8")

    print(f"release bundle: {bundle_path}")
    print(f"sha256 file: {checksum_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
