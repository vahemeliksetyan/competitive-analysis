"""
Team: PDFs → one Excel per PDF in data/processed/<extractor>/team/

Team PDFs sometimes come out with empty labels. These are filled from a
reference table (mappings/team_label_ref.xlsx), built automatically from the
first complete file. Rows are aligned at index '1' and filled by position.

Run alone:   python src/extraction/extract_team.py [--extractor camelot]
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd

import config
from src.extraction.report_processor import ReportProcessor

OPERATOR = "Team"

# Header/title rows that are not real data
EXCLUDE_PATTERNS = ["Տեղեկատվություն", "Աղյուսակ", "^N$", "ԱՂՅՈՒՍԱԿ"]


# ── Helpers ──────────────────────────────────────────────────────────────────
def save_label_ref(df):
    """Save full ordered (idx, label, unit) table from a complete file."""
    df[list(df.columns[:3])].to_excel(config.TEAM_LABEL_REF, index=False)
    print(f"  Label reference saved ({len(df)} rows)")


def load_label_ref():
    """Return reference DataFrame or None."""
    if config.TEAM_LABEL_REF.exists():
        return pd.read_excel(config.TEAM_LABEL_REF)
    return None


def fill_missing(df, ref_df):
    """
    Copy label and measurement-unit columns positionally.
    Aligns both DataFrames at the row where index == '1',
    then pastes reference values for every empty label row.
    Covers indexed rows AND blank-index sub-rows alike.
    """
    idx_col, label_col, meas_col = df.columns[:3]
    ref_idx_col, ref_label_col, ref_meas_col = ref_df.columns[:3]

    mask = df[label_col].isna()
    if not mask.any():
        return df

    broken_starts = df.index[df[idx_col].astype(str).str.strip() == '1']
    ref_starts    = ref_df.index[ref_df[ref_idx_col].astype(str).str.strip() == '1']

    if len(broken_starts) == 0 or len(ref_starts) == 0:
        print("  WARNING: could not find section-1 anchor — skipping fill")
        return df

    broken_anchor = broken_starts[0]
    ref_anchor    = ref_starts[0]

    for pos in df.index[mask]:
        ref_pos = ref_anchor + (pos - broken_anchor)
        if 0 <= ref_pos < len(ref_df):
            lbl = ref_df.at[ref_pos, ref_label_col]
            if pd.notna(lbl) and str(lbl).strip():
                df.at[pos, label_col] = lbl
            meas = ref_df.at[ref_pos, ref_meas_col]
            if pd.notna(meas) and str(meas).strip():
                df.at[pos, meas_col] = meas

    still  = df[label_col].isna().sum()
    filled = mask.sum() - still
    print(f"  Labels filled: {filled}  |  still missing: {still}")
    return df


def exclude_rows(df):
    """Remove header/title rows that are not real data."""
    label_col = df.columns[1]
    mask = df[label_col].str.contains("|".join(EXCLUDE_PATTERNS), na=False, regex=True)
    if mask.sum():
        print(f"  Excluded {mask.sum()} non-data rows")
    return df[~mask].reset_index(drop=True)


# ── Main ─────────────────────────────────────────────────────────────────────
def run(extractor=config.DEFAULT_EXTRACTOR):
    raw_folder = config.raw_dir(OPERATOR)
    out_folder = config.processed_dir(OPERATOR, extractor)
    out_folder.mkdir(parents=True, exist_ok=True)

    label_ref = load_label_ref()

    filled_files = {}   # file_name -> number of labels filled
    ok_files = []       # files with no missing labels
    warned_files = []   # files missing labels but no reference available

    for pdf in sorted(raw_folder.glob("*.pdf")):
        m = re.search(r'q([1-4])_(\d{4})', pdf.name.lower())
        quarter, year = m.groups() if m else ('', '')

        print(f"\nProcessing: {pdf.name}")

        # Run pipeline up to fix_index_text_only — fill BEFORE assign_main_value
        rp = (
            ReportProcessor(pdf, skip_rows=1)
            .extract_with(extractor)
            .annotate()
            .fix_index_text_only()
        )

        df = rp.df
        label_col, meas_col = df.columns[1], df.columns[2]

        # Normalize empty/whitespace strings to NaN
        df[label_col] = df[label_col].replace(r'^\s*$', pd.NA, regex=True)
        df[meas_col]  = df[meas_col].replace(r'^\s*$', pd.NA, regex=True)
        missing = df[label_col].isna().sum()

        if missing == 0:
            if label_ref is None:
                save_label_ref(df)
                label_ref = load_label_ref()
            ok_files.append(pdf.name)
        elif label_ref is None:
            print(f"  WARNING: {missing} missing labels but no reference yet — process a complete file first")
            warned_files.append(pdf.name)
        else:
            df = fill_missing(df, label_ref)
            filled_files[pdf.name] = missing - df[label_col].isna().sum()

        # Continue pipeline with filled labels so assign_main_value sees correct data
        rp.df = df
        df = rp.assign_main_value().remove_parentheses().df

        df["quarter"]     = quarter
        df["year"]        = year
        df["source_file"] = pdf.name

        df = exclude_rows(df)

        excel_name = pdf.stem + ".xlsx"
        df.to_excel(out_folder / excel_name, index=False)
        print(f"  Saved: {excel_name}")

    print(f"\nDone! Team ({extractor})")

    print(f"\nOK — no missing labels ({len(ok_files)} files):")
    for f in ok_files:
        print(f"  - {f}")

    print(f"\nFixed — missing labels filled from reference ({len(filled_files)} files):")
    for f, count in sorted(filled_files.items()):
        print(f"  - {f}  ({count} labels filled)")

    if warned_files:
        print(f"\nWARNING — missing labels but no reference available ({len(warned_files)} files):")
        for f in warned_files:
            print(f"  - {f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--extractor", choices=config.EXTRACTORS, default=config.DEFAULT_EXTRACTOR)
    run(parser.parse_args().extractor)
