"""
Step 5 — Assemble: append employee & branch counts and save the final file.

data/external/employee_count_2025Q4.xlsx holds manually collected rows
(index 'EMP': employee count, branch count Yerevan / total per operator).
They are added as extra rows at the bottom — nothing is joined onto PDF rows.

Writes data/final/final.xlsx (plumber) or data/final/final_camelot.xlsx.
Run alone:   python src/assemble.py [--extractor camelot]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

import config


def run(extractor=config.DEFAULT_EXTRACTOR):
    df_main = pd.read_excel(config.translated_file(extractor))
    emp_df = pd.read_excel(config.EMPLOYEE_FILE, header=0)
    print(f"  Main data rows  : {len(df_main)}")
    print(f"  Employee rows   : {len(emp_df)}")

    df_final = pd.concat([df_main, emp_df], ignore_index=True)
    out = config.final_file(extractor)
    df_final.to_excel(out, index=False)
    print(f"  Final rows      : {len(df_final)}")
    print(f"  Saved → {out.relative_to(config.ROOT)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--extractor", choices=config.EXTRACTORS, default=config.DEFAULT_EXTRACTOR)
    run(parser.parse_args().extractor)
