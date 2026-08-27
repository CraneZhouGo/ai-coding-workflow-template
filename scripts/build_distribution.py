#!/usr/bin/env python3
"""Build a deterministic distribution archive from distribution-manifest.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "distribution-manifest.json"
FIXED_TIMESTAMP = (2026, 1, 1, 0, 0, 0)


def included_files(entries: list[str]) -> list[Path]:
    files: set[Path] = set()
    for entry in entries:
        path = ROOT / entry
        if not path.exists():
            raise SystemExit(f"distribution entry does not exist: {entry}")
        if path.is_file():
            files.add(path)
        else:
            files.update(candidate for candidate in path.rglob("*") if candidate.is_file())
    return sorted(files, key=lambda path: path.relative_to(ROOT).as_posix())


def build(output: Path) -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    files = included_files(manifest["include"])
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            relative = path.relative_to(ROOT).as_posix()
            info = ZipInfo(relative, FIXED_TIMESTAMP)
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, path.read_bytes())
    print(f"built {output} with {len(files)} files")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    output = args.output or ROOT / manifest["archive_name"]
    build(output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
