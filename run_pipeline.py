"""
Run the full pipeline:  PDFs → data/final/final.xlsx

  1. Extract    each operator's PDFs → data/processed/<extractor>/<operator>/
  2. Combine    → data/final/intermediate/<Operator>_combined.xlsx
  3. Unify      → data/final/intermediate/all_combined_unified.xlsx
  4. Translate  → data/final/intermediate/all_combined_unified_translated.xlsx
  5. Assemble   (+ employee & branch counts) → data/final/final.xlsx
  6. Validate   final.xlsx against the PDFs → data/final/validation_report.xlsx

Examples:
  python run_pipeline.py                          # everything with pdfplumber (default)
  python run_pipeline.py --extractor camelot      # same with Camelot → final_camelot.xlsx
  python run_pipeline.py --extractor both         # both + comparison report
  python run_pipeline.py --operator ucom          # re-extract only Ucom, then steps 2–5
  python run_pipeline.py --skip-extraction        # steps 2–5 only
"""
import argparse
import time

import config
from src import assemble, combine, compare, translate, unify, validate
from src.extraction import extract_team, extract_ucom, extract_viva

EXTRACTORS_BY_OPERATOR = {
    "viva": extract_viva,
    "ucom": extract_ucom,
    "team": extract_team,
}


def banner(text):
    print(f"\n{'=' * 60}\n  {text}\n{'=' * 60}")


def run(extractor, operators, skip_extraction):
    if not skip_extraction:
        for op in operators:
            banner(f"Step 1: Extracting {op.capitalize()} ({extractor})")
            EXTRACTORS_BY_OPERATOR[op].run(extractor)

    banner(f"Step 2: Combining processed files ({extractor})")
    combine.run(extractor)

    banner(f"Step 3: Unifying labels ({extractor})")
    unify.run(extractor)

    banner(f"Step 4: Translating labels ({extractor})")
    translate.run(extractor)

    banner(f"Step 5: Appending employee and branch data ({extractor})")
    assemble.run(extractor)

    banner(f"Step 6: Validating against the PDFs ({extractor})")
    validate.run(extractor)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--extractor", choices=config.EXTRACTORS + ["both"], default=config.DEFAULT_EXTRACTOR,
                        help="PDF extraction method (default: plumber). 'both' also writes a comparison report.")
    parser.add_argument("--operator", nargs="+", choices=list(EXTRACTORS_BY_OPERATOR), default=list(EXTRACTORS_BY_OPERATOR),
                        help="Operators to (re-)extract (default: all). Steps 2–5 always use all operators.")
    parser.add_argument("--skip-extraction", action="store_true",
                        help="Skip step 1 and reuse existing files in data/processed/")
    parser.add_argument("--compare", action="store_true",
                        help="After running, compare final_camelot.xlsx with final.xlsx")
    args = parser.parse_args()

    start = time.time()
    extractors = config.EXTRACTORS if args.extractor == "both" else [args.extractor]
    for extractor in extractors:
        run(extractor, args.operator, args.skip_extraction)

    if args.extractor == "both" or args.compare:
        banner("Comparing Camelot vs pdfplumber")
        compare.run()

    banner(f"Done in {time.time() - start:.0f}s")
    for extractor in extractors:
        print(f"  Final output: {config.final_file(extractor).relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
