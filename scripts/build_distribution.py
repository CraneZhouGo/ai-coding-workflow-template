#!/usr/bin/env python3
"""根据平台清单构建内容可复现的 Claude Code/Codex 发行压缩包。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "distribution-manifest.json"
CODEX_MANIFEST_PATH = ROOT / "codex-distribution-manifest.json"
FIXED_TIMESTAMP = (2026, 1, 1, 0, 0, 0)


def included_files(base: Path, entries: list[str]) -> list[Path]:
    files: set[Path] = set()
    for entry in entries:
        path = base / entry
        if not path.exists():
            raise SystemExit(f"distribution entry does not exist: {entry}")
        if path.is_file():
            files.add(path)
        else:
            files.update(candidate for candidate in path.rglob("*") if candidate.is_file())
    return sorted(files, key=lambda path: path.relative_to(base).as_posix())


def build(output: Path, manifest_path: Path = MANIFEST_PATH) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    base = ROOT / manifest.get("base", ".")
    files = included_files(base, manifest["include"])
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            relative = path.relative_to(base).as_posix()
            info = ZipInfo(relative, FIXED_TIMESTAMP)
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, path.read_bytes())
    print(f"built {output} with {len(files)} files")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--platform", choices=("claude", "codex", "all"), default="claude")
    args = parser.parse_args()
    if args.platform == "all":
        if args.output:
            parser.error("--platform all 不能与 --output 同时使用")
        for manifest_path in (MANIFEST_PATH, CODEX_MANIFEST_PATH):
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            build((ROOT / manifest["archive_name"]).resolve(), manifest_path)
        return 0
    manifest_path = MANIFEST_PATH if args.platform == "claude" else CODEX_MANIFEST_PATH
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    output = args.output or ROOT / manifest["archive_name"]
    build(output.resolve(), manifest_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
