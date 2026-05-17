#!/usr/bin/env python3
import argparse

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    df = pd.read_csv(args.input, sep="\t")
    df = df.copy()
    df["Definitions"] = df["Generated_Definition"]
    df.to_csv(args.output, sep="\t", index=False)


if __name__ == "__main__":
    main()
