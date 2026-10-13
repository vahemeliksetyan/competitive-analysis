"""
Step 4 — Translate: add English columns.

  Արժեք          → Values             (mappings/translation.xlsx)
  Գլխավոր արժեք  → Main value         (mappings/translation.xlsx)
  Չափման միավոր  → Measurement unit   (mappings/units.xlsx)

Both mapping files: column A = Armenian, column B = English, no header row.
Untranslated labels keep the Armenian text. Afterwards the columns are renamed:
Արժեք → Ցուցանիշ (label) and Ցուցիչ → Արժեք (value).

Writes data/final/intermediate/all_combined_unified_translated.xlsx and unique_values.xlsx.
Run alone:   python src/translate.py [--extractor camelot]
"""
import argparse
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

import config


def norm(x):
    """Collapse repeated spaces so 'a  b' matches the key 'a b'."""
    return re.sub(r"\s+", " ", str(x)).strip() if pd.notna(x) else x


def heading_key(x):
    """Looser key for section headings, which differ between operators: drops the
    trailing 'այդ թվում' / 'որից' ('including'), '(opex)' / '(capex)', punctuation,
    and Armenian ligatures (ﬕ → մի) found in some Team PDFs."""
    s = unicodedata.normalize("NFKC", str(x)).lower()
    s = re.sub(r"\((opex|capex)\)", "", s)
    s = re.sub(r"(այդ թվում|որից)\W*$", "", s)
    s = re.sub(r"[՝`',]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def load_map(path, key=norm):
    df = pd.read_excel(path, header=None)
    out = {}
    for k, v in zip(df.iloc[:, 0], df.iloc[:, 1]):
        out.setdefault(key(k), v)
    return out


def run(extractor=config.DEFAULT_EXTRACTOR):
    labels = load_map(config.TRANSLATION_MAP)
    headings = load_map(config.TRANSLATION_MAP, key=heading_key)
    units = load_map(config.UNITS_MAP)

    df = pd.read_excel(config.unified_file(extractor))

    df["Values"] = df["Արժեք"].map(norm).map(labels).fillna(df["Արժեք"])
    df["Measurement unit"] = df["Չափման միավոր"].map(norm).map(units)
    df["Main value"] = df["Գլխավոր արժեք"].map(heading_key).map(headings).fillna(df["Գլխավոր արժեք"])

    # Rename Armenian column headers
    df = df.rename(columns={'Արժեք': 'Ցուցանիշ'})
    df = df.rename(columns={'Ցուցիչ': 'Արժեք'})

    out = config.translated_file(extractor)
    df.to_excel(out, index=False)

    unique_values = pd.DataFrame(sorted(df["Values"].dropna().unique(), key=str), columns=["Unique Values"])
    out_unique = config.unique_values_file(extractor)
    unique_values.to_excel(out_unique, index=False)

    print("Created files:")
    print("-", out.relative_to(config.ROOT))
    print("-", out_unique.relative_to(config.ROOT))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--extractor", choices=config.EXTRACTORS, default=config.DEFAULT_EXTRACTOR)
    run(parser.parse_args().extractor)
