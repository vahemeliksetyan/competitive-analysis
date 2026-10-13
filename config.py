"""All paths and settings in one place. Paths are relative to the repo root."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# ── Folders ──────────────────────────────────────────────────────────────────
DATA_DIR         = ROOT / "data"
RAW_DIR          = DATA_DIR / "raw"            # input PDFs: data/raw/<operator>/
PROCESSED_DIR    = DATA_DIR / "processed"      # per-PDF Excel: data/processed/<extractor>/<operator>/
EXTERNAL_DIR     = DATA_DIR / "external"       # extra inputs (employee & branch counts)
FINAL_DIR        = DATA_DIR / "final"
INTERMEDIATE_DIR = FINAL_DIR / "intermediate"  # combined / unified / translated files
MAPPINGS_DIR     = ROOT / "mappings"

# ── Settings ─────────────────────────────────────────────────────────────────
OPERATORS = ["Viva", "Ucom", "Team"]         # order rows appear in the final file
EXTRACTORS = ["plumber", "camelot"]

# Official brand colours — use only these for each operator in charts
BRAND_COLORS = {"Viva": "#E30613", "Ucom": "#7EBD43", "Team": "#02415F"}
DEFAULT_EXTRACTOR = "plumber"                   # camelot is kept as a cross-check

# ── Mapping / input files ────────────────────────────────────────────────────
TEAM_LABEL_REF = MAPPINGS_DIR / "team_label_ref.xlsx"   # built automatically if missing
UNIFICATION_MAP   = MAPPINGS_DIR / "unification.xlsx"
TRANSLATION_MAP   = MAPPINGS_DIR / "translation.xlsx"
UNITS_MAP         = MAPPINGS_DIR / "units.xlsx"
EMPLOYEE_FILE     = EXTERNAL_DIR / "employee_count_2025Q4.xlsx"

COMPARISON_FILE   = FINAL_DIR / "comparison_camelot_vs_plumber.xlsx"


# ── Path helpers ─────────────────────────────────────────────────────────────
def suffix(extractor):
    """plumber is the main output (no suffix); other extractors get '_<name>'."""
    return "" if extractor == "plumber" else f"_{extractor}"


def raw_dir(operator):
    return RAW_DIR / operator.lower()


def processed_dir(operator, extractor):
    return PROCESSED_DIR / extractor / operator.lower()


def combined_file(operator, extractor):
    return INTERMEDIATE_DIR / f"{operator}_combined{suffix(extractor)}.xlsx"


def all_combined_file(extractor):
    return INTERMEDIATE_DIR / f"all_combined{suffix(extractor)}.xlsx"


def unified_file(extractor):
    return INTERMEDIATE_DIR / f"all_combined_unified{suffix(extractor)}.xlsx"


def unique_labels_file(extractor):
    return INTERMEDIATE_DIR / f"unique_labels{suffix(extractor)}.xlsx"


def translated_file(extractor):
    return INTERMEDIATE_DIR / f"all_combined_unified_translated{suffix(extractor)}.xlsx"


def unique_values_file(extractor):
    return INTERMEDIATE_DIR / f"unique_values{suffix(extractor)}.xlsx"


def final_file(extractor):
    return FINAL_DIR / f"final{suffix(extractor)}.xlsx"


def validation_file(extractor):
    return FINAL_DIR / f"validation_report{suffix(extractor)}.xlsx"


def anomaly_report_file(extractor):
    return FINAL_DIR / f"anomaly_report{suffix(extractor)}.md"
