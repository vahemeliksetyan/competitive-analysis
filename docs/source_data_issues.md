# Source data issues — questions for the operators

Problems found in the operators' **own quarterly reports** (the PDFs in `data/raw/`), not in the
extraction. The pipeline keeps the values exactly as reported; this file records what to ask
each operator. Amounts are in thousand AMD unless stated otherwise.

Status: **open** = not yet asked · **asked** = waiting for an answer · **resolved** = answered/fixed

---

## Team (Telecom Armenia)

### 1. Q2 2025 — profit before tax overstated by ~1.9 bn AMD · open

File: `data/raw/team/Team_q2_2025.pdf`, page 1, items 3–7.

| Item | Line | Reported |
|---|---|---|
| 3 | Operating profit before depreciation (OIBDA) | 1,539,101 |
| 4 | Depreciation and amortization | **-958,462** (negative, unlike every other quarter) |
| 5 | Other operating result | 0 |
| 6 | Non-operating result | (337,184) |
| 7 | **Profit before tax** | **2,160,378** |

- Correct: 1,539,101 − 958,462 + 0 − 337,184 = **243,455**
- Reported value equals 1,539,101 **+** 958,462 − 337,184 = 2,160,379 → depreciation was entered
  as a negative number and the formula added it instead of subtracting it.
- All other identities in the report hold (1 − 2 = 3; 6 = 6.1 − 6.2 + 6.3 + 6.4), only item 7 is off.

**Question:** Is profit before tax for Q2 2025 243,455 rather than 2,160,378? Was a corrected report filed?

### 2. Q4 2025 — profit before tax and capital expenditure look wrong · open

File: `data/raw/team/Team_q4_2025.pdf`.

| Item | Line | Reported |
|---|---|---|
| 3 | OIBDA | 994,803 |
| 4 | Depreciation and amortization | **-1,087,882** (negative again) |
| 5 | Other operating result | 0 |
| 6 | Non-operating result | (72,263) |
| 7 | **Profit before tax** | **2,166,394** |
| 8 | **Capital expenditure** | **43,978** |

- Correct: 994,803 − 1,087,882 − 72,263 = **-165,342** (a loss).
- Unlike Q2, the reported 2,166,394 is not explained by the sign error alone (that would give 2,010,422).
  It is also almost identical to Q2's 2,160,378.
- Capital expenditure of 43,978 vs 2,244,514 in Q3 2025 and 2.2–3.6 bn in the other 2025 quarters.

**Question:** What are the correct profit before tax and capital expenditure for Q4 2025?

### 3. Q4 2024 — unit price (APPM) of 2 · open

Item 9.4 (average price per minute) is **2** AMD in Q4 2024; it is 5.0–6.2 in every other quarter
(Q3 2024: 5.8, Q1 2025: 5.0). Sub-items 9.4.1 (prepaid) and 9.4.2 (postpaid) for the same quarter
are 4 and 9 — their average must lie between 4 and 9, so it cannot be 2.

**Question:** Is 9.4 for Q4 2024 a typo (e.g. 5.2)?

### 4. Depreciation dips in Q4 2021 and Q1 2023 · open (question, may be correct)

Item 4 is 205,129 (Q4 2021) and 197,351 (Q1 2023), vs 0.7–1.1 m in neighbouring quarters.
Profit before tax is consistent with these values, so the report is internally consistent.

**Question:** Were these one-off adjustments, or reporting errors?

### 5. Q1 2022 — report originally missing · resolved

`Team_q1_2022.pdf` was a copy of the Q2 2022 report. Replaced with the real Q1 2022 report on 2026-10-07.

---

## Ucom

### 6. Active subscribers include broadband — different definition · open (question)

Ucom's item 9.1 = prepaid (9.1.1) + postpaid (9.1.2) **+ broadband (9.1.3)**.
Viva and Team report 9.1 = prepaid + postpaid only. Broadband adds 72–150 k subscribers to Ucom's total.

**Question:** Is this the regulator's intended definition? (Affects comparability of subscriber counts and ARPU.)

### 7. Voice / data revenue split · open (question)

Voice (1.1.1) rose from 37% to 49% of mobile revenue in 2021–2025 while data (1.1.3) fell from
26% to 14% — the opposite of Viva and Team. Most likely bundled tariffs are booked under voice.

**Question:** How is bundled-tariff revenue split between voice and data?

### 8. Q4 2025 — operating profit off by 13,851 · open (minor)

Revenue 5,677,640 − expenses 3,791,279 = 1,886,361, but item 3 is reported as 1,872,510.

---

## Viva

### 9. Q1 2025 — profit before tax off by 59,684 · open (minor)

7,771,173 (item 3) − 3,157,545 (item 4) − 426,326 (item 6) = 4,187,302, but item 7 is 4,127,618.
Viva reports no item 5, so the difference may be an unreported "other operating result".

### 10. Q4 2024 — costs moved between categories · open (question)

Network operation and maintenance (2.6) jumped to 1,492,875 (240,048 in Q3 2024), while other
expenses (2.7) fell to 323,432 (3,045,667 in Q3 2024). Total operating expenses look normal.

**Question:** Was there a reclassification between 2.6 and 2.7 from Q4 2024?

---

*Found by the validation step (`src/validate.py`): profit identities, anomaly checks and PDF matching.
See also `data/final/anomaly_report.md`.*
