"""
Step 2 — Combine: stack the per-PDF Excel files of each operator.

Writes data/final/intermediate/<Operator>_combined.xlsx and all_combined.xlsx.
Run alone:   python src/combine.py [--extractor camelot]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

import config

# Rows to exclude — add Armenian Արժեք values here
EXCLUDE_ROWS = [
    # "Օրինակ",
]


def run(extractor=config.DEFAULT_EXTRACTOR):
    config.INTERMEDIATE_DIR.mkdir(parents=True, exist_ok=True)
    all_dfs = []

    for operator in config.OPERATORS:
        folder = config.processed_dir(operator, extractor)
        files = sorted(folder.glob("*.xlsx"))
        if not files:
            raise FileNotFoundError(f"No processed files in {folder} — run the {operator} extraction first")

        df = pd.concat([pd.read_excel(f) for f in files], ignore_index=True)
        if EXCLUDE_ROWS:
            df = df[~df["Արժեք"].isin(EXCLUDE_ROWS)]

        out = config.combined_file(operator, extractor)
        df.to_excel(out, index=False)
        print(f"{operator}: {len(df)} rows saved to {out.name}")
        all_dfs.append(df)

    final = pd.concat(all_dfs, ignore_index=True)
    out = config.all_combined_file(extractor)
    final.to_excel(out, index=False)
    print(f"\nAll combined: {len(final)} rows saved to {out.relative_to(config.ROOT)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--extractor", choices=config.EXTRACTORS, default=config.DEFAULT_EXTRACTOR)
    run(parser.parse_args().extractor)
