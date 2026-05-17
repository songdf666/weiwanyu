#!/usr/bin/env python3
from __future__ import annotations

import argparse
import filecmp
import fnmatch
import json
from pathlib import Path
from typing import Any

FORBIDDEN_FILE_PATTERNS = [
    ".DS_Store",
    "*.npy",
    "*.npz",
    "*.pkl",
    "*.pt",
    "*.pth",
    "*.ckpt",
    "*.safetensors",
    "*.zip",
    "*.tar",
    "*.tar.gz",
    "*.gz",
]

FORBIDDEN_DIR_NAMES = {
    ".git",
    ".venv",
    "venv",
    ".conda",
    "__pycache__",
    "checkpoints",
    "outputs",
}

ALLOWED_GENERATED_FILES = {"SOURCE_NOTE.md", "PAPER.md"}


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(
        description="Audit paper/code mappings and lightweight reproduced source snapshots."
    )
    parser.add_argument("--repo-root", default=repo_root, type=Path)
    parser.add_argument("--workspace-root", default=repo_root.parent, type=Path)
    parser.add_argument("--manifest", default=repo_root / "configs" / "source_manifest.json", type=Path)
    parser.add_argument("--paper-map", default=repo_root / "configs" / "paper_code_map.json", type=Path)
    parser.add_argument("--markdown-out", type=Path, help="Optional Markdown report path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    workspace_root = args.workspace_root.resolve()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    paper_map = json.loads(args.paper_map.read_text(encoding="utf-8"))

    results = audit(manifest, paper_map, repo_root, workspace_root)
    report = render_markdown(results)
    if args.markdown_out:
        out_path = args.markdown_out if args.markdown_out.is_absolute() else repo_root / args.markdown_out
        out_path.write_text(report, encoding="utf-8")
    print(render_summary(results))
    return 0 if all(result["ok"] for result in results) else 1


def audit(
    manifest: dict[str, Any],
    paper_map: dict[str, Any],
    repo_root: Path,
    workspace_root: Path,
) -> list[dict[str, Any]]:
    source_by_id = {source["id"]: source for source in manifest["sources"]}
    map_by_id = {entry["id"]: entry for entry in paper_map["entries"]}
    all_ids = sorted(set(source_by_id) | set(map_by_id))
    return [
        audit_one(source_id, source_by_id.get(source_id), map_by_id.get(source_id), repo_root, workspace_root)
        for source_id in all_ids
    ]


def audit_one(
    source_id: str,
    source: dict[str, Any] | None,
    mapping: dict[str, Any] | None,
    repo_root: Path,
    workspace_root: Path,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    metrics: dict[str, int] = {}

    if source is None:
        return _result(source_id, None, None, errors=["missing source_manifest entry"])
    if mapping is None:
        return _result(source_id, source, None, errors=["missing paper_code_map entry"])

    dest_root = _resolve(repo_root, source["dest_path"])
    source_root = _resolve(workspace_root, source["source_path"])
    code = mapping.get("code", {})
    paper = mapping.get("paper", {})

    if code.get("type") != "reproducible_code":
        errors.append("code.type must be reproducible_code")
    if paper.get("type") not in {"paper", "paper_group"}:
        errors.append("paper.type must be paper or paper_group")
    if code.get("path") != source["dest_path"]:
        errors.append(f"code.path does not match manifest dest_path: {code.get('path')}")
    if code.get("source_path") != source["source_path"]:
        errors.append(f"code.source_path does not match manifest source_path: {code.get('source_path')}")

    if not dest_root.exists():
        errors.append(f"missing reproduced code directory: {source['dest_path']}")
    if not source_root.exists():
        errors.append(f"missing local source directory: {source['source_path']}")
    if errors:
        return _result(source_id, source, mapping, errors=errors, warnings=warnings, metrics=metrics)

    for required in ("SOURCE_NOTE.md", "PAPER.md"):
        if not (dest_root / required).is_file():
            errors.append(f"missing {required}")

    entrypoint_errors = _check_entrypoints(dest_root, source.get("entrypoints", []))
    errors.extend(entrypoint_errors)

    forbidden = _find_forbidden(dest_root)
    if forbidden:
        errors.extend(f"forbidden file or directory present: {path}" for path in forbidden[:20])
        if len(forbidden) > 20:
            errors.append(f"forbidden entries truncated: {len(forbidden) - 20} more")

    expected_files = _expected_files(source_root, source.get("include", ["**/*"]), source.get("exclude", []))
    metrics["expected_source_files"] = len(expected_files)
    compared = 0
    for rel_path in sorted(expected_files):
        src_file = source_root / rel_path
        dst_file = dest_root / rel_path
        if not dst_file.is_file():
            errors.append(f"missing copied source file: {rel_path.as_posix()}")
            continue
        compared += 1
        if not filecmp.cmp(src_file, dst_file, shallow=False):
            errors.append(f"copied source differs from local source: {rel_path.as_posix()}")

    metrics["compared_source_files"] = compared

    extra_files = []
    for dst_file in dest_root.rglob("*"):
        if not dst_file.is_file():
            continue
        rel_path = dst_file.relative_to(dest_root)
        if rel_path.name in ALLOWED_GENERATED_FILES:
            continue
        if rel_path not in expected_files:
            extra_files.append(rel_path.as_posix())
    metrics["extra_files"] = len(extra_files)
    if extra_files:
        warnings.extend(f"extra file not copied from local source: {path}" for path in extra_files[:20])
        if len(extra_files) > 20:
            warnings.append(f"extra files truncated: {len(extra_files) - 20} more")

    return _result(source_id, source, mapping, errors=errors, warnings=warnings, metrics=metrics)


def _check_entrypoints(dest_root: Path, entrypoints: list[str]) -> list[str]:
    errors: list[str] = []
    for entrypoint in entrypoints:
        if any(char in entrypoint for char in "*?[]"):
            matches = list(dest_root.glob(entrypoint))
            if not matches:
                errors.append(f"entrypoint pattern not found: {entrypoint}")
            continue
        if entrypoint.endswith("/"):
            if not (dest_root / entrypoint).is_dir():
                errors.append(f"entrypoint directory not found: {entrypoint}")
            continue
        if not (dest_root / entrypoint).exists():
            errors.append(f"entrypoint not found: {entrypoint}")
    return errors


def _expected_files(source_root: Path, include: list[str], exclude: list[str]) -> set[Path]:
    expected: set[Path] = set()
    for path in source_root.rglob("*"):
        if not path.is_file():
            continue
        rel_path = path.relative_to(source_root)
        rel_posix = rel_path.as_posix()
        if _included(rel_posix, include, exclude):
            expected.add(rel_path)
    return expected


def _find_forbidden(root: Path) -> list[str]:
    forbidden: list[str] = []
    for path in root.rglob("*"):
        rel = path.relative_to(root).as_posix()
        if path.is_dir() and path.name in FORBIDDEN_DIR_NAMES:
            forbidden.append(rel + "/")
        if path.is_file() and any(_match(rel, pattern) for pattern in FORBIDDEN_FILE_PATTERNS):
            forbidden.append(rel)
    return forbidden


def _included(rel_path: str, include: list[str], exclude: list[str]) -> bool:
    return any(_match(rel_path, pattern) for pattern in include) and not any(
        _match(rel_path, pattern) for pattern in exclude
    )


def _match(rel_path: str, pattern: str) -> bool:
    path = Path(rel_path)
    if pattern in {"**", "**/*"}:
        return True
    if fnmatch.fnmatch(rel_path, pattern):
        return True
    if "/" not in pattern and fnmatch.fnmatch(path.name, pattern):
        return True
    if pattern.endswith("/**"):
        prefix = pattern[:-3]
        return rel_path.startswith(prefix) or f"/{prefix}" in rel_path
    return False


def _resolve(root: Path, path_value: str) -> Path:
    path = Path(path_value)
    return path if path.is_absolute() else root / path


def _result(
    source_id: str,
    source: dict[str, Any] | None,
    mapping: dict[str, Any] | None,
    *,
    errors: list[str],
    warnings: list[str] | None = None,
    metrics: dict[str, int] | None = None,
) -> dict[str, Any]:
    return {
        "id": source_id,
        "paper_title": (mapping or {}).get("paper", {}).get("title", ""),
        "code_path": (source or {}).get("dest_path", ""),
        "ok": not errors,
        "errors": errors,
        "warnings": warnings or [],
        "metrics": metrics or {},
    }


def render_summary(results: list[dict[str, Any]]) -> str:
    ok_count = sum(1 for result in results if result["ok"])
    lines = [f"Audit result: {ok_count}/{len(results)} code snapshots passed"]
    for result in results:
        status = "OK" if result["ok"] else "FAIL"
        warning_suffix = f", warnings={len(result['warnings'])}" if result["warnings"] else ""
        lines.append(f"- {status}: {result['id']}{warning_suffix}")
    return "\n".join(lines)


def render_markdown(results: list[dict[str, Any]]) -> str:
    ok_count = sum(1 for result in results if result["ok"])
    lines = [
        "# Reproducible Code Audit",
        "",
        "This report checks that each paper has a corresponding reproduced-code snapshot,",
        "that each snapshot has nearby paper/source notes, that entrypoints exist, that",
        "copied files match the local source directories, and that large/runtime artifacts",
        "are not present in the lightweight GitHub copy.",
        "",
        f"Summary: **{ok_count}/{len(results)}** reproduced-code snapshots passed.",
        "",
        "| ID | Paper | Reproducible code | Status | Checked files | Notes |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for result in results:
        status = "PASS" if result["ok"] else "FAIL"
        metrics = result["metrics"]
        checked = f"{metrics.get('compared_source_files', 0)}/{metrics.get('expected_source_files', 0)}"
        notes = []
        if result["errors"]:
            notes.append(f"errors={len(result['errors'])}")
        if result["warnings"]:
            notes.append(f"warnings={len(result['warnings'])}")
        lines.append(
            "| {id} | {paper} | `{code}` | {status} | {checked} | {notes} |".format(
                id=result["id"],
                paper=result["paper_title"].replace("|", "\\|"),
                code=result["code_path"],
                status=status,
                checked=checked,
                notes=", ".join(notes) or "-",
            )
        )

    lines.append("")
    lines.append("## Detailed Findings")
    for result in results:
        lines.append("")
        lines.append(f"### {result['id']}")
        lines.append("")
        lines.append(f"- Status: {'PASS' if result['ok'] else 'FAIL'}")
        lines.append(f"- Paper: {result['paper_title']}")
        lines.append(f"- Reproducible code: `{result['code_path']}`")
        for key, value in sorted(result["metrics"].items()):
            lines.append(f"- {key}: {value}")
        if result["errors"]:
            lines.append("- Errors:")
            for item in result["errors"]:
                lines.append(f"  - {item}")
        if result["warnings"]:
            lines.append("- Warnings:")
            for item in result["warnings"]:
                lines.append(f"  - {item}")
        if not result["errors"] and not result["warnings"]:
            lines.append("- Notes: no issues found in this audit scope.")

    lines.append("")
    lines.append("## Audit Scope")
    lines.append("")
    lines.append("This audit verifies repository organization and source snapshot integrity.")
    lines.append("It does not rerun full paper experiments, because several projects require")
    lines.append("external corpora, model checkpoints, GPUs, or publisher-controlled datasets.")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
