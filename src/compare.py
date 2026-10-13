"""
Cross-check — compare final_camelot.xlsx with final.xlsx (pdfplumber).

Rows are matched on company + date + index + label (pass 1), then leftovers on
company + date + index (pass 2), so a row whose label differs still pairs up and
the label shows as a difference. Every difference is listed as one line:

  camelot row X / plumber row Y, column 'C': camelot = ...  |  plumber = ...

Writes data/final/comparison_camelot_vs_plumber.xlsx.
Run alone:   python src/compare.py   (needs both final files)
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

import config

KEY_PASS1 = ["company", "Տերեթիվ", "Ինդեքս", "Ցուցանիշ"]
KEY_PASS2 = ["company", "Տերեթիվ", "Ինդեքս"]

# Columns that differ by design and are not compared
SKIP_COLS = ["source_file"]


def norm_text(x):
    """Collapse whitespace so 'a  b' and 'a b' count as the same."""
    if pd.isna(x):
        return ""
    return re.sub(r"\s+", " ", str(x)).strip()


def same(a, b):
    """NaN == NaN, 5 == 5.0, text compared after whitespace cleanup."""
    if pd.isna(a) and pd.isna(b):
        return True
    if pd.isna(a) or pd.isna(b):
        return False
    try:
        return abs(float(a) - float(b)) < 1e-6
    except (TypeError, ValueError):
        return norm_text(a) == norm_text(b)


def show(x):
    return "(empty)" if pd.isna(x) or str(x).strip() == "" else str(x)


def excel_row(i):
    return i + 2      # +1 for header, +1 for 1-based rows


def match(a, b, key_cols):
    """Pair rows of a and b on key_cols (+ occurrence number). Returns list of (a_idx, b_idx)."""
    def keyed(df):
        k = pd.DataFrame({c: df[c].map(norm_text) for c in key_cols}, index=df.index)
        k["_occ"] = k.groupby(key_cols).cumcount()
        return k.reset_index(names="_row")
    m = keyed(a).merge(keyed(b), on=key_cols + ["_occ"], suffixes=("_a", "_b"))
    return list(zip(m["_row_a"], m["_row_b"]))


def run():
    camelot = pd.read_excel(config.final_file("camelot"))
    plumber = pd.read_excel(config.final_file("plumber"))

    pairs = match(camelot, plumber, KEY_PASS1)

    # Pass 2: pair leftovers on company/date/index (only rows that have an index)
    left_c = camelot.drop(index=[c for c, _ in pairs])
    left_p = plumber.drop(index=[p for _, p in pairs])
    left_c = left_c[left_c["Ինդեքս"].map(norm_text) != ""]
    left_p = left_p[left_p["Ինդեքս"].map(norm_text) != ""]
    pairs += match(left_c, left_p, KEY_PASS2)

    matched_c = {c for c, _ in pairs}
    matched_p = {p for _, p in pairs}
    compare_cols = [c for c in camelot.columns if c not in SKIP_COLS]

    rows = []
    for c, p in sorted(pairs):
        for col in compare_cols:
            a, b = camelot.at[c, col], plumber.at[p, col]
            if not same(a, b):
                rows.append({
                    "camelot_row": excel_row(c), "plumber_row": excel_row(p),
                    "company": camelot.at[c, "company"], "Տերեթիվ": camelot.at[c, "Տերեթիվ"],
                    "Ինդեքս": camelot.at[c, "Ինդեքս"], "column": col,
                    "camelot_value": show(a), "plumber_value": show(b),
                    "description": f"camelot row {excel_row(c)} / plumber row {excel_row(p)}, column '{col}': "
                                   f"camelot = {show(a)}  |  plumber = {show(b)}",
                })

    for c in camelot.index.difference(list(matched_c)):
        r = camelot.loc[c]
        rows.append({
            "camelot_row": excel_row(c), "plumber_row": None,
            "company": r["company"], "Տերեթիվ": r["Տերեթիվ"], "Ինդեքս": r["Ինդեքս"],
            "column": "(whole row)",
            "camelot_value": f"{show(r['Ցուցանիշ'])} = {show(r['Արժեք'])}", "plumber_value": "(row missing)",
            "description": f"camelot row {excel_row(c)}: only in camelot — "
                           f"{show(r['Ցուցանիշ'])} = {show(r['Արժեք'])}  |  plumber = (row missing)",
        })

    for p in plumber.index.difference(list(matched_p)):
        r = plumber.loc[p]
        rows.append({
            "camelot_row": None, "plumber_row": excel_row(p),
            "company": r["company"], "Տերեթիվ": r["Տերեթիվ"], "Ինդեքս": r["Ինդեքս"],
            "column": "(whole row)",
            "camelot_value": "(row missing)", "plumber_value": f"{show(r['Ցուցանիշ'])} = {show(r['Արժեք'])}",
            "description": f"plumber row {excel_row(p)}: only in plumber — "
                           f"camelot = (row missing)  |  {show(r['Ցուցանիշ'])} = {show(r['Արժեք'])}",
        })

    diffs = pd.DataFrame(rows, columns=["camelot_row", "plumber_row", "company", "Տերեթիվ", "Ինդեքս",
                                        "column", "camelot_value", "plumber_value", "description"])

    summary = pd.DataFrame([
        ("Rows in final_camelot.xlsx",         len(camelot)),
        ("Rows in final.xlsx (plumber)",       len(plumber)),
        ("Matched rows",                       len(pairs)),
        ("Different cells in matched rows",    (diffs["column"] != "(whole row)").sum()),
        ("Rows only in final_camelot.xlsx",    len(camelot) - len(matched_c)),
        ("Rows only in final.xlsx (plumber)",  len(plumber) - len(matched_p)),
    ], columns=["metric", "value"])

    with pd.ExcelWriter(config.COMPARISON_FILE) as writer:
        diffs.to_excel(writer, sheet_name="differences", index=False)
        summary.to_excel(writer, sheet_name="summary", index=False)

    print(summary.to_string(index=False))
    print("\nDifferences:")
    for d in diffs["description"]:
        print("  -", d)
    print(f"\nSaved: {config.COMPARISON_FILE.relative_to(config.ROOT)}")


if __name__ == "__main__":
    run()
