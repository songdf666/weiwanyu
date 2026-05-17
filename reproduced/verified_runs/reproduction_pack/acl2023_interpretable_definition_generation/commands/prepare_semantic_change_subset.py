#!/usr/bin/env python3
import argparse
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-root", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--words", nargs="+", required=True)
    args = parser.parse_args()

    root = Path(args.dataset_root)
    rows = []

    for word in args.words:
        uses_path = root / "data" / word / "uses.tsv"
        clusters_path = root / "clusters" / "opt" / f"{word}.tsv"

        uses_df = pd.read_csv(uses_path, sep="\t")
        clusters_df = pd.read_csv(clusters_path, sep="\t")
        merged = uses_df.merge(clusters_df, on="identifier", how="left")
        merged = merged[merged["cluster"] != -1].copy()

        for _, row in merged.iterrows():
            rows.append(
                {
                    "id": row["identifier"],
                    "word": row["lemma"],
                    "pos": row["pos"],
                    "date": row["date"],
                    "period": row["grouping"],
                    "cluster": int(row["cluster"]),
                    "target_indices": row["indexes_target_token"],
                    "Targets": row["lemma"],
                    "Context": row["context"],
                }
            )

    output_df = pd.DataFrame(rows)
    output_df.to_csv(args.output, sep="\t", index=False)


if __name__ == "__main__":
    main()
