#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import json
import shutil
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Sync lightweight reproduced source snapshots.")
    parser.add_argument("--workspace-root", default=repo_root.parent, type=Path)
    parser.add_argument("--manifest", default=repo_root / "configs" / "source_manifest.json", type=Path)
    parser.add_argument("--repo-root", default=repo_root, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    repo_root = args.repo_root.resolve()
    workspace_root = args.workspace_root.resolve()

    summary: list[tuple[str, int]] = []
    for source in manifest["sources"]:
        source_root = _resolve_path(workspace_root, source["source_path"])
        dest_root = _resolve_path(repo_root, source["dest_path"])
        copied = sync_source(source, source_root, dest_root, dry_run=args.dry_run)
        summary.append((source["id"], copied))

    for source_id, count in summary:
        print(f"{source_id}: {count} files")
    return 0


def sync_source(source: dict[str, Any], source_root: Path, dest_root: Path, *, dry_run: bool) -> int:
    if not source_root.exists():
        print(f"SKIP missing source: {source['id']} -> {source_root}")
        return 0

    include = source.get("include", ["**/*"])
    exclude = source.get("exclude", [])
    files = [
        path
        for path in source_root.rglob("*")
        if path.is_file() and _included(path.relative_to(source_root).as_posix(), include, exclude)
    ]

    if not dry_run:
        if dest_root.exists():
            shutil.rmtree(dest_root)
        dest_root.mkdir(parents=True, exist_ok=True)
        for file_path in files:
            rel_path = file_path.relative_to(source_root)
            target = dest_root / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, target)
        (dest_root / "SOURCE_NOTE.md").write_text(_source_note(source, len(files)), encoding="utf-8")

    return len(files)


def _included(rel_path: str, include: list[str], exclude: list[str]) -> bool:
    return any(_match(rel_path, pattern) for pattern in include) and not any(
        _match(rel_path, pattern) for pattern in exclude
    )


def _match(rel_path: str, pattern: str) -> bool:
    if fnmatch.fnmatch(rel_path, pattern):
        return True
    if "/" not in pattern and fnmatch.fnmatch(Path(rel_path).name, pattern):
        return True
    if pattern.endswith("/**"):
        prefix = pattern[:-3]
        return rel_path.startswith(prefix) or f"/{prefix}" in rel_path
    return False


def _resolve_path(root: Path, path_value: str) -> Path:
    path = Path(path_value)
    return path if path.is_absolute() else root / path


def _source_note(source: dict[str, Any], copied_count: int) -> str:
    entrypoints = "\n".join(f"- `{item}`" for item in source.get("entrypoints", []))
    excludes = "\n".join(f"- `{item}`" for item in source.get("exclude", []))
    return f"""# Source Note: {source['title']}

- Source id: `{source['id']}`
- Domain: {source.get('domain', '')}
- Status: {source.get('status', '')}
- Original path: `{source['source_path']}`
- Copied files: {copied_count}

## Entrypoints

{entrypoints or '- Not specified'}

## Excluded From Lightweight Snapshot

{excludes or '- Nothing specified'}

## Maintenance Note

This directory is a managed lightweight copy generated from `configs/source_manifest.json`.
Do not store large datasets, model weights, virtual environments, or run outputs here.
"""


if __name__ == "__main__":
    raise SystemExit(main())
