"""
ReportProcessor: turns one quarterly operator PDF into a clean table.

Pipeline (each step returns self, so steps can be chained):
    extract_with('plumber' | 'camelot')  → raw table, first 4 columns renamed
    annotate()                           → organization / date / report type columns
    fix_index_text_only()                → split index numbers from label text
    assign_main_value()                  → parent label for every row
    remove_parentheses()                 → '(1,234)' → number

Column names (Armenian):
    Ինդեքս         index (1, 1.1, 1.1.1 ...)
    Արժեք          label
    Չափման միավոր  unit
    Ցուցիչ         numeric value
"""
import os
import re
from datetime import datetime

import pandas as pd


class QuarterMeta:
    """Parse '<Org>_q<N>_<YYYY>.pdf' into organization, quarter, year and start date."""
    _QUARTER_INFO = {
        'q1': ('01-01', [1, 2, 3]),
        'q2': ('04-01', [4, 5, 6]),
        'q3': ('07-01', [7, 8, 9]),
        'q4': ('10-01', [10, 11, 12]),
    }

    def __init__(self, filename: str):
        base = os.path.splitext(os.path.basename(filename))[0]
        org, quarter, year = base.split('_')
        self.organization = org
        self.quarter = quarter.lower()
        self.year = int(year)
        start_md, self.months = self._QUARTER_INFO[self.quarter]
        self.start_date = pd.to_datetime(f"{year}-{start_md}")
        print(f"Parsed filename -> Org: {self.organization}, Quarter: {self.quarter.upper()}, Year: {self.year}")

    def month_start(self, idx: int) -> pd.Timestamp:
        m = self.months[idx - 1]
        return pd.Timestamp(self.year, m, 1)


class ReportProcessor:
    COLUMN_NAMES = ['Ինդեքս', 'Արժեք', 'Չափման միավոր', 'Ցուցիչ']

    def __init__(self, pdf_path: str, skip_rows: int = 0, skip_last_rows: int = 0):
        self.pdf_path = str(pdf_path)
        self.skip_rows = skip_rows
        self.skip_last_rows = skip_last_rows
        self.meta = QuarterMeta(self.pdf_path)
        self.df: pd.DataFrame = pd.DataFrame()
        print(f"Initialized ReportProcessor for file: {self.pdf_path} (skip_rows={self.skip_rows})")

    # ── Extraction ───────────────────────────────────────────────────────────
    def extract_with(self, extractor: str) -> 'ReportProcessor':
        """Run the extraction method for 'plumber' (default) or 'camelot'."""
        if extractor == 'plumber':
            return self.extract_plumber()
        if extractor == 'camelot':
            return self.extract()
        raise ValueError(f"Unknown extractor '{extractor}'. Use 'plumber' or 'camelot'.")

    def _finish_extraction(self, df: pd.DataFrame) -> 'ReportProcessor':
        """Trim skip rows, rename the first 4 columns and capitalize labels."""
        self.df = (
            df
            .iloc[self.skip_rows : len(df) - self.skip_last_rows]
            .reset_index(drop=True)
        )
        # Rename only first 4 columns, keep rest as-is
        self.df.columns = self.COLUMN_NAMES + list(self.df.columns[len(self.COLUMN_NAMES):])
        self.df['Արժեք'] = self.df['Արժեք'].fillna('').astype(str).str.capitalize()
        print(f"Extraction complete. DataFrame shape: {self.df.shape}")
        return self

    def extract(
        self,
        flavor: str = 'lattice',
        split_text: bool = False,
        strip_text: str = '\n'
    ) -> 'ReportProcessor':
        """
        Extract tables with Camelot (kept as a cross-check for pdfplumber).
        Removes exact duplicate rows before trimming.

        Note: Camelot finds no table on a page that holds a single table row,
        so such a row is lost (e.g. Viva Q1/Q2 2023, index 9.6.4 on page 4).
        """
        import camelot
        import PyPDF2

        print("Starting extraction (camelot)...")
        if not os.path.isfile(self.pdf_path):
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")

        with open(self.pdf_path, 'rb') as f:
            num_pages = len(PyPDF2.PdfReader(f).pages)
        print(f"Total pages in PDF: {num_pages}")

        tables = []
        for p in range(1, num_pages + 1):
            ts = camelot.read_pdf(
                self.pdf_path,
                pages=str(p),
                flavor=flavor,
                split_text=split_text,
                strip_text=strip_text
            )
            print(f"  → Found {len(ts)} table(s) on page {p}")
            tables.extend(ts)

        if not tables:
            raise ValueError("No tables extracted from the PDF.")

        # concatenate all tables, then drop exact duplicates
        df = pd.concat([t.df for t in tables], ignore_index=True).drop_duplicates()
        return self._finish_extraction(df)

    def extract_plumber(self) -> 'ReportProcessor':
        """
        Extract tables with pdfplumber (default).
        Unlike extract(), duplicate rows are kept so row positions stay stable.
        """
        import pdfplumber

        print("Starting extraction (pdfplumber)...")
        if not os.path.isfile(self.pdf_path):
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")

        tables = []
        with pdfplumber.open(self.pdf_path) as pdf:
            print(f"Total pages in PDF: {len(pdf.pages)}")
            for p, page in enumerate(pdf.pages, start=1):
                ts = page.extract_tables()
                print(f"  → Found {len(ts)} table(s) on page {p}")
                tables.extend(pd.DataFrame(t) for t in ts)

        if not tables:
            raise ValueError("No tables extracted from the PDF.")

        # Tables on later pages repeat the page-1 column-header row — drop those copies
        def norm_row(row):
            return [re.sub(r'\s+', ' ', str(c or '')).strip() for c in row]

        header = norm_row(tables[0].iloc[0])
        tables = [tables[0]] + [
            t.iloc[1:] if len(t) and norm_row(t.iloc[0]) == header else t
            for t in tables[1:]
        ]

        df = pd.concat(tables, ignore_index=True).fillna('')

        # pdfplumber keeps line breaks inside cells — join wrapped text with a space
        df = df.apply(lambda col: col.astype(str).str.replace(r'\s*\n\s*', ' ', regex=True).str.strip())
        return self._finish_extraction(df)

    # ── Metadata ─────────────────────────────────────────────────────────────
    def parse_type_and_year(self, pdf_path):
        name = os.path.basename(pdf_path).lower()

        # Quarterly: _q1_2023
        m = re.search(r'_q([1-4])_(\d{4})', name)
        if m:
            return "Quarterly", int(m.group(2)), int(m.group(1))

        # Yearly: _y_2023
        m = re.search(r'_y_(\d{4})', name)
        if m:
            return "Yearly", int(m.group(1)), 1   # fake Q1

        raise ValueError("Filename must contain _qN_YEAR or _y_YEAR")

    def annotate(self) -> 'ReportProcessor':
        print("Annotating DataFrame with organization and date...")

        report_type, year, quarter = self.parse_type_and_year(self.pdf_path)
        self.meta.report_type = report_type

        # If yearly -> force date to Q1 start (Jan 1)
        if report_type == "Yearly":
            self.meta.start_date = datetime(year, 1, 1)

        self.df['Կազմակերպություն'] = self.meta.organization
        self.df['Տերեթիվ'] = self.meta.start_date.strftime('%Y-%m-%d')
        self.df['ReportType'] = self.meta.report_type
        return self

    # ── Cleaning ─────────────────────────────────────────────────────────────
    def fix_index_text_only(self) -> 'ReportProcessor':
        """
        Normalize Ինդեքս and Արժեք columns according to rules.

        Handles:
        - Single digits: 1 text
        - Multi-level digits: 1.1 text, 1.1.3 text
        - Digits with optional ')'
        - Text immediately after number without space: 1.1.10այլ
        - Text-only rows
        - Values starting with numbers
        """
        df = self.df.copy()
        raw = df['Ինդեքս'].fillna('').astype(str).str.strip()

        def capitalize_first(s: str) -> str:
            s = s.strip()
            return s[:1].upper() + s[1:] if s else s

        # --- Pattern for digits (multi-level) with optional ')' and optional space ---
        pattern_index_text = r'^(\d+(?:\.\d+)*\)?)(?:[ \t]*)(.*)$'

        # --- CASE 1: digits + optional ')' + optional SPACE + text in Ինդեքս ---
        m = raw.str.extract(pattern_index_text)
        mask_index_text = m[0].notna() & m[1].notna() & (m[1] != '')

        df.loc[mask_index_text, 'Ինդեքս'] = m.loc[mask_index_text, 0]
        transferred = m.loc[mask_index_text, 1].map(capitalize_first)
        existing = df.loc[mask_index_text, 'Արժեք'].fillna('').astype(str).str.strip()
        df.loc[mask_index_text, 'Արժեք'] = (existing + ' ' + transferred).str.strip()

        # --- CASE 2: text only in Ինդեքս ---
        mask_text_only = (
            raw.ne('') &
            raw.ne('.') &
            ~raw.str.match(r'^\d')
        )
        transferred = raw[mask_text_only].map(capitalize_first)
        existing = df.loc[mask_text_only, 'Արժեք'].fillna('').astype(str).str.strip()
        df.loc[mask_text_only, 'Արժեք'] = (existing + ' ' + transferred).str.strip()
        df.loc[mask_text_only, 'Ինդեքս'] = ''

        # --- CASE 3: digits + optional ')' + optional SPACE + text at start of Արժեք ---
        value_raw = df['Արժեք'].fillna('').astype(str).str.strip()
        m_value = value_raw.str.extract(pattern_index_text)
        mask_value_index = m_value[0].notna() & m_value[1].notna() & (m_value[1] != '') & df['Ինդեքս'].fillna('').eq('')

        df.loc[mask_value_index, 'Ինդեքս'] = m_value.loc[mask_value_index, 0]
        df.loc[mask_value_index, 'Արժեք'] = m_value.loc[mask_value_index, 1].map(capitalize_first).str.strip()

        self.df = df
        return self

    def assign_main_value(self) -> 'ReportProcessor':
        """Every row gets the label of the nearest pure-digit (top-level) row above it."""
        df = self.df.copy()

        idx = df['Ինդեքս'].astype(str).str.strip()

        # MAIN = pure digits only
        is_main = idx.str.fullmatch(r'\d+').fillna(False)

        # Assign main value ONLY from pure-digit rows, then forward-fill
        df['Գլխավոր արժեք'] = df['Արժեք'].where(is_main).ffill()

        # Marker EXACTLY matches the same condition
        df['Գլխավոր արժեքի մարկեր'] = is_main

        self.df = df
        return self

    def remove_parentheses(self) -> 'ReportProcessor':
        """Convert value cells to numbers. Only labels in SIGN_MATTERS keep a negative sign."""
        SIGN_MATTERS = [
            # Pretax Profit
            'Շահույթ մինչև հարկումը',       # Ucom, Team
            'Շահույթ՝ մինչև հարկումը',      # Viva

            # Non-operating result
            'Ոչ գործառնական գործունեության արդյունք, որից',   # Ucom, Team
            'Ոչ գործառնական գործունեության արդյունք, որից՝',  # Viva

            # FX gains/losses
            'Արտարժույթի փոխարժեքային տարբերություններից օգուտներ/կորուստներ',  # all three

            # Other operating activity result
            'Գործառնական այլ գործունեության արդյունք',  # all three

            # Financial income (can be near zero but always positive — optional to include)
            'Ֆինանսական եկամուտ',  # all three

            # Other non-operating income/expenses
            'Այլ ոչ գործառնական եկամուտ/ծախսեր',  # all three
        ]

        def clean_numeric(value, apply_sign):
            if isinstance(value, (int, float)):
                num = abs(value)
                if value < 0 and apply_sign:
                    return -num
                return num

            if not isinstance(value, str):
                return value

            value = value.strip()

            if value in ('', 'N/A', 'n/a', '-', '—'):
                return None

            is_negative = bool(re.match(r'^\([\d,\.]+\)$', value)) or value.startswith('-')

            # Decimal comma: '4,8' / '5 ,4' mean 4.8 / 5.4 (a thousands comma is always followed by 3 digits)
            if re.fullmatch(r'\(?-?\d+,\d{1,2}\)?', value.replace(' ', '')):
                value = value.replace(' ', '').replace(',', '.')

            clean = value.replace('(', '').replace(')', '').replace(',', '').replace(' ', '').lstrip('-')

            try:
                num = abs(float(clean))
                if is_negative and apply_sign:
                    num = -num
                return num
            except ValueError:
                return value

        self.df['Ցուցիչ'] = self.df['Ցուցիչ'].astype(object)

        # Extraction sometimes merges the unit into the value cell, e.g. 'բաժանորդ   (8,631)'.
        # Split it: number stays as the value, text moves to the unit column if that is empty.
        unit_and_number = r'^\s*([^\d()\-]+?)\s+(\(?-?[\d][\d,\. ]*\)?)\s*$'
        for i, row in self.df.iterrows():
            value = row['Ցուցիչ']
            if not isinstance(value, str):
                continue
            m = re.match(unit_and_number, value)
            if not m:
                continue
            unit, number = m.groups()
            self.df.at[i, 'Ցուցիչ'] = number
            current_unit = row.get('Չափման միավոր', '')
            if pd.isna(current_unit) or not str(current_unit).strip():
                self.df.at[i, 'Չափման միավոր'] = unit.strip()
            print(f"  Split unit from value in row {i}: '{value}' -> unit='{unit.strip()}', value='{number}'")

        for i, row in self.df.iterrows():
            label = str(row.get('Արժեք', '')).strip()
            apply_sign = any(s.lower() == label.lower() for s in SIGN_MATTERS)
            self.df.at[i, 'Ցուցիչ'] = clean_numeric(row['Ցուցիչ'], apply_sign)

        return self
