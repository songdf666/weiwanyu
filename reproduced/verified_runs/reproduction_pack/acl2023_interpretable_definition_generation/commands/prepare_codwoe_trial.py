#!/usr/bin/env python3
import argparse
import json

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-json", required=True)
    parser.add_argument("--output-tsv", required=True)
    args = parser.parse_args()

    with open(args.input_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    rows = []
    for row in data:
        rows.append(
            {
                "id": row["id"],
                "Targets": row["word"],
                "Context": row["example"],
                "Definition": row["gloss"],
                "POS": row.get("pos", ""),
                "Type": row.get("type", ""),
            }
        )

    pd.DataFrame(rows).to_csv(args.output_tsv, sep="\t", index=False)


if __name__ == "__main__":
    main()
