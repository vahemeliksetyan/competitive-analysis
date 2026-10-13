"""
Ucom: PDFs → one Excel per PDF in data/processed/<extractor>/ucom/

Fixes applied after extraction:
  9.1  empty           → sum of 9.1.1 + 9.1.2 + 9.1.3
  9.2  ARPU empty/zero → subscriber-weighted average of 9.2.1 / 9.2.2 (/ 9.2.3)
  9.5  unit empty      → copied from 9.5.1;  value empty/zero → 9.5.1 + 9.5.2
  9.6  empty/zero      → 9.6.1 + 9.6.2

Run alone:   python src/extraction/extract_ucom.py [--extractor camelot]
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd

import config
from src.extraction.report_processor import ReportProcessor

OPERATOR = "Ucom"


def run(extractor=config.DEFAULT_EXTRACTOR):
    raw_folder = config.raw_dir(OPERATOR)
    out_folder = config.processed_dir(OPERATOR, extractor)
    out_folder.mkdir(parents=True, exist_ok=True)

    fixed_91_files = []
    ok_91_files = []
    fixed_92_files = []
    missing_92_files = []
    ok_92_files = []
    fixed_95_chafm_files = []
    fixed_95_tsuts_null_files = []
    fixed_95_tsuts_zero_files = []
    ok_95_files = []
    fixed_96_null_files = []
    fixed_96_zero_files = []
    ok_96_files = []

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
        idx_col = df.columns[0]
        chafm_col = df.columns[2]
        tsuts_col = df.columns[3]

        def get_value(index_code):
            mask = df[idx_col].astype(str).str.strip() == index_code
            if not mask.any():
                return None
            return pd.to_numeric(df.at[df.index[mask][0], tsuts_col], errors='coerce')

        # 9.1 active subscribers: if empty, sum the next 3 rows
        mask_91 = df[idx_col].astype(str).str.strip() == '9.1'
        if mask_91.any():
            row_91 = df.index[mask_91][0]
            pos = df.index.get_loc(row_91)
            if pd.isna(df.at[row_91, tsuts_col]):
                next_3 = pd.to_numeric(df.iloc[pos + 1 : pos + 4][tsuts_col], errors='coerce')
                df.at[row_91, tsuts_col] = next_3.sum()
                fixed_91_files.append(file_name)
            else:
                ok_91_files.append(file_name)

        # 9.2 overall ARPU: if missing, weighted average
        # ((9.1.1 * 9.2.1) + (9.1.2 * 9.2.2) [+ (9.1.3 * 9.2.3)]) / (9.1.1 + 9.1.2 [+ 9.1.3])
        mask_92 = df[idx_col].astype(str).str.strip() == '9.2'
        if mask_92.any():
            row_92 = df.index[mask_92][0]
            current_92 = df.at[row_92, tsuts_col]
            if pd.isna(current_92) or current_92 == 0:
                prepaid_subs  = get_value('9.1.1')
                postpaid_subs = get_value('9.1.2')
                prepaid_arpu  = get_value('9.2.1')
                postpaid_arpu = get_value('9.2.2')
                if (
                    pd.notna(prepaid_subs) and pd.notna(postpaid_subs)
                    and pd.notna(prepaid_arpu) and pd.notna(postpaid_arpu)
                    and (prepaid_subs + postpaid_subs) != 0
                ):
                    broadband_subs = get_value('9.1.3')
                    broadband_arpu = get_value('9.2.3')

                    has_broadband = (
                        pd.notna(broadband_subs) and pd.notna(broadband_arpu)
                        and broadband_subs > 0 and broadband_arpu > 0
                    )

                    if has_broadband:
                        numerator   = (prepaid_subs * prepaid_arpu) + (postpaid_subs * postpaid_arpu) + (broadband_subs * broadband_arpu)
                        denominator = prepaid_subs + postpaid_subs + broadband_subs
                    else:
                        numerator   = (prepaid_subs * prepaid_arpu) + (postpaid_subs * postpaid_arpu)
                        denominator = prepaid_subs + postpaid_subs

                    computed = numerator / denominator

                    if 300 <= computed <= 10_000:
                        df.at[row_92, tsuts_col] = computed
                        fixed_92_files.append((file_name, 'filled'))
                    else:
                        missing_92_files.append(file_name)
                else:
                    missing_92_files.append(file_name)
            else:
                ok_92_files.append(file_name)

        # 9.5 new activations: copy unit from next row if missing,
        # and fill value with sum of next 2 rows if missing/zero
        mask_95 = df[idx_col].astype(str).str.strip() == '9.5'
        if mask_95.any():
            row_95 = df.index[mask_95][0]
            pos_95 = df.index.get_loc(row_95)
            if pd.isna(df.at[row_95, chafm_col]):
                df.at[row_95, chafm_col] = df.iloc[pos_95 + 1][chafm_col]
                fixed_95_chafm_files.append(file_name)
            current_95 = df.at[row_95, tsuts_col]
            if pd.isna(current_95) or current_95 == 0:
                next_2 = pd.to_numeric(df.iloc[pos_95 + 1 : pos_95 + 3][tsuts_col], errors='coerce')
                df.at[row_95, tsuts_col] = next_2.sum()
                if pd.isna(current_95):
                    fixed_95_tsuts_null_files.append(file_name)
                else:
                    fixed_95_tsuts_zero_files.append(file_name)
            else:
                ok_95_files.append(file_name)

        # 9.6 churn: if empty/zero, sum next 2 rows (9.6.1 + 9.6.2)
        mask_96 = df[idx_col].astype(str).str.strip() == '9.6'
        if mask_96.any():
            row_96 = df.index[mask_96][0]
            pos_96 = df.index.get_loc(row_96)
            current_96 = df.at[row_96, tsuts_col]
            if pd.isna(current_96) or current_96 == 0:
                next_2 = pd.to_numeric(df.iloc[pos_96 + 1 : pos_96 + 3][tsuts_col], errors='coerce')
                df.at[row_96, tsuts_col] = next_2.sum()
                if pd.isna(current_96):
                    fixed_96_null_files.append(file_name)
                else:
                    fixed_96_zero_files.append(file_name)
            else:
                ok_96_files.append(file_name)

        df["quarter"] = quarter
        df["year"] = year
        df["source_file"] = file_name

        excel_name = pdf.stem + ".xlsx"
        df.to_excel(out_folder / excel_name, index=False)
        print(f"Saved: {excel_name}")

    print(f"Done! Ucom ({extractor})")

    def report(title, files):
        print(f"\n{title} ({len(files)} files):")
        for f in sorted(files):
            print(f"  - {f}" if isinstance(f, str) else f"  - {f[0]}  [{f[1]}]")

    report("Fixed — 9.1 was empty, filled with sum of 9.1.1+9.1.2+9.1.3", fixed_91_files)
    report("OK — 9.1 already had a value", ok_91_files)
    report("Fixed — 9.2 ARPU was missing/zero, calculated as weighted average", fixed_92_files)
    report("Missing — 9.2 could not be calculated (sub-rows missing)", missing_92_files)
    report("OK — 9.2 already had a value", ok_92_files)
    report("Fixed — 9.5 unit was empty, copied from 9.5.1", fixed_95_chafm_files)
    report("Fixed — 9.5 value was null, filled with 9.5.1+9.5.2", fixed_95_tsuts_null_files)
    report("Fixed — 9.5 value was zero, recalculated with 9.5.1+9.5.2", fixed_95_tsuts_zero_files)
    report("OK — 9.5 already had a value", ok_95_files)
    report("Fixed — 9.6 was null, filled with 9.6.1+9.6.2", fixed_96_null_files)
    report("Fixed — 9.6 was zero, recalculated with 9.6.1+9.6.2", fixed_96_zero_files)
    report("OK — 9.6 already had a value", ok_96_files)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--extractor", choices=config.EXTRACTORS, default=config.DEFAULT_EXTRACTOR)
    run(parser.parse_args().extractor)
