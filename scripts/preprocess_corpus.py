#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from euphemism_repro.preprocess.pipeline import load_config, run_pipeline, stats_to_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preprocess corpus files into normalized JSONL.")
    parser.add_argument("--input", required=True, type=Path, help="Input directory containing raw corpus files.")
    parser.add_argument("--output", required=True, type=Path, help="Output JSONL path.")
    parser.add_argument(
        "--config",
        default=REPO_ROOT / "configs" / "preprocess.default.json",
        type=Path,
        help="Preprocessing config JSON.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_config(args.config)
    stats = run_pipeline(args.input, args.output, config)
    print(stats_to_text(stats))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
