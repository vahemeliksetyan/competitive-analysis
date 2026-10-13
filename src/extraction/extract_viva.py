"""
Viva: PDFs → one Excel per PDF in data/processed/<extractor>/viva/

Fixes applied after extraction:
  - The value for 'Կանխավճարային բաժանորդներ' sometimes lands on the next
    empty row (PDF artifact) → shifted back up, empty row removed.
  - Index 1 (operating revenue) empty → copied from 1.1 (mobile revenue).

Run alone:   python src/extraction/extract_viva.py [--extractor camelot]
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd

import config
from src.extraction.report_processor import ReportProcessor

OPERATOR = "Viva"
TARGET_LABEL = 'Կանխավճարային բաժանորդներ'


def run(extractor=config.DEFAULT_EXTRACTOR):
    raw_folder = config.raw_dir(OPERATOR)
    out_folder = config.processed_dir(OPERATOR, extractor)
    out_folder.mkdir(parents=True, exist_ok=True)

    fixed_index1_files = []
    ok_index1_files = []
    fixed_arpu_files = []
    ok_arpu_files = []

    for pdf in sorted(raw_folder.glob("*.pdf")):
        file_name = pdf.name

        # extract quarter and year from filename, e.g., q1_2022
        m = re.search(r'q([1-4])_(\d{4})', file_name.lower())
        quarter, year = m.groups() if m else ('', '')

        rp = (
            ReportProcessor(pdf, skip_rows=1, skip_last_rows=0)
            .extract_with(extractor)
            .annotate()
            .fix_index_text_only()
            .assign_main_value()
            .remove_parentheses()
        )

        df = rp.df

        # PDF artifact: the value for TARGET_LABEL sometimes lands on the next
        # empty row. Find that orphan row and shift the value up.
        arpu_fixed = False
        for i in range(1, len(df)):
            prev_label = str(df.at[df.index[i - 1], 'Արժեք']).strip()
            row_idx = df.index[i]
            idx_empty = str(df.at[row_idx, 'Ինդեքս']).strip() in ('', 'nan')
            val_empty = str(df.at[row_idx, 'Արժեք']).strip() in ('', 'nan')
            if prev_label == TARGET_LABEL and idx_empty and val_empty:
                orphan_val = df.at[row_idx, 'Ցուցիչ']
                if pd.notna(orphan_val) and str(orphan_val).strip() not in ('', 'nan'):
                    prev_row_idx = df.index[i - 1]
                    if pd.isna(df.at[prev_row_idx, 'Ցուցիչ']):
                        df.at[prev_row_idx, 'Ցուցիչ'] = orphan_val
                        df = df.drop(index=row_idx).reset_index(drop=True)
                        fixed_arpu_files.append(file_name)
                        arpu_fixed = True
                        break

        if not arpu_fixed:
            ok_arpu_files.append(file_name)

        # If top-level operating revenue (index 1) has no value, copy from mobile revenue (index 1.1)
        mask_1 = df['Ինդեքս'].astype(str).str.strip() == '1'
        mask_11 = df['Ինդեքս'].astype(str).str.strip() == '1.1'
        if mask_1.any() and mask_11.any():
            idx_1 = df.index[mask_1][0]
            idx_11 = df.index[mask_11][0]
            if pd.isna(df.at[idx_1, 'Ցուցիչ']):
                df.at[idx_1, 'Ցուցիչ'] = df.at[idx_11, 'Ցուցիչ']
                fixed_index1_files.append(file_name)
            else:
                ok_index1_files.append(file_name)

        df["quarter"] = quarter
        df["year"] = year
        df["source_file"] = file_name

        excel_name = pdf.stem + ".xlsx"
        df.to_excel(out_folder / excel_name, index=False)
        print(f"Saved: {excel_name}")

    print(f"Done! Viva ({extractor})")

    for title, files in [
        ("Fixed — index 1 was null, copied from 1.1", fixed_index1_files),
        ("OK — index 1 already had a value", ok_index1_files),
        (f"Fixed — {TARGET_LABEL} orphan value shifted up", fixed_arpu_files),
        (f"OK — {TARGET_LABEL} had no orphan row", ok_arpu_files),
    ]:
        print(f"\n{title} ({len(files)} files):")
        for f in sorted(files):
            print(f"  - {f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--extractor", choices=config.EXTRACTORS, default=config.DEFAULT_EXTRACTOR)
    run(parser.parse_args().extractor)
