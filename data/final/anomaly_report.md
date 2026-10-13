# Data anomaly report

Generated 2026-10-13 16:18 from `data/final/final.xlsx`. Charts show the indicator for that operator, one bar per quarter (taller = larger value); `^` marks the flagged quarter.

## Summary

```
                                      check  count
                             Values checked   3553
                    found on the index line   3007
                 found elsewhere in the PDF    428
                found loosely (digits only)     17
      calculated by the pipeline (expected)     60
  weak match (small number not on its line)     41
                  NOT FOUND in PDF — review      0
                  Source PDFs with problems      0
                Source PDFs to check by eye      6
                   Totals that don't add up      0
        Anomalies — HIGH (spike, x10, zero)     14
             Anomalies — LOW (level shifts)     30
                  Consistency checks failed      4
                        Completeness issues      0
```

## Major anomalies (14)

Values far from both neighbouring quarters, x10/x1000 the usual level, or 0 between normal quarters. If the value is in the PDF, the operator reported it that way — decide whether it is a real event or a reporting error before using it.

### 1. Team — 1.1.10 Other revenues — 2021 Q4

- **Type:** spike (jumps and comes back)
- **Value:** 114,119 · previous quarter 42,655 (+168%) · next quarter 32,284 (+253%) · usual 67,311
- **In the PDF:** yes, on its own line

```
2021 Q1  ▁▁▁▂ ▁▁▁▁ ▁▁▁▂ ▁▂▃▃ ▄▅█▃  2025 Q4
            ^
```

### 2. Team — 4 Depreciation of fixed assets and amortization of intangible assets — 2021 Q4

- **Type:** spike (jumps and comes back)
- **Value:** 205,129 · previous quarter 1,079,955 (-81%) · next quarter 886,620 (-77%) · usual 797,272
- **In the PDF:** yes

```
2021 Q1  ▆▄▆▁ ▅▄▅▆ ▁▅▂▂ ▆▄▄▂ ▂▆█▆  2025 Q4
            ^
```

### 3. Team — 4 Depreciation of fixed assets and amortization of intangible assets — 2023 Q1

- **Type:** spike (jumps and comes back)
- **Value:** 197,351 · previous quarter 988,434 (-80%) · next quarter 899,004 (-78%) · usual 797,272
- **In the PDF:** yes, on its own line

```
2021 Q1  ▆▄▆▁ ▅▄▅▆ ▁▅▂▂ ▆▄▄▂ ▂▆█▆  2025 Q4
                   ^
```

### 4. Team — 9.5.3 Broadband internet subscribers (other than by phone) — 2025 Q1

- **Type:** spike (jumps and comes back)
- **Value:** 170 · previous quarter 6,150 (-97%) · next quarter 2,785 (-94%) · usual 6,180
- **In the PDF:** yes, on its own line

```
2021 Q1  ▂▃▂▂ ▅▂▃▂ ▂▂▂▃ ▂█▃▂ ▁▁▂▃  2025 Q4
                             ^
```

### 5. Team — 9.6.2 Postpaid subscribers — 2021 Q4

- **Type:** spike (jumps and comes back)
- **Value:** 14,488 · previous quarter 3,452 (+320%) · next quarter 5,164 (+181%) · usual 4,572
- **In the PDF:** yes, on its own line

```
2021 Q1  ▂▂▂█ ▃▃▂▂ ▂▂▃▅ ▂▁▅▆ ▂▁▃▂  2025 Q4
            ^
```

### 6. Team — 9.6.2 Postpaid subscribers — 2025 Q2

- **Type:** spike (jumps and comes back)
- **Value:** 1,015 · previous quarter 4,499 (-77%) · next quarter 5,200 (-80%) · usual 4,572
- **In the PDF:** yes, on its own line

```
2021 Q1  ▂▂▂█ ▃▃▂▂ ▂▂▃▅ ▂▁▅▆ ▂▁▃▂  2025 Q4
                              ^
```

### 7. Ucom — 2.7 Other expenses — 2022 Q3

- **Type:** spike (jumps and comes back)
- **Value:** 278,335 · previous quarter 1,033,047 (-73%) · next quarter 1,443,879 (-81%) · usual 1,126,010
- **In the PDF:** yes, on its own line

```
2021 Q1  ▃▅▄▅ ▅▅▁▇ ▅▆▆█ ▄▅▇▇ ▅▅▇▇  2025 Q4
                ^
```

### 8. Ucom — 9.6.3 Broadband internet subscribers (other than by phone) — 2024 Q2

- **Type:** spike (jumps and comes back)
- **Value:** 36,736 · previous quarter 12,797 (+187%) · next quarter 12,324 (+198%) · usual 9,007
- **In the PDF:** yes, on its own line

```
2021 Q1  ▁▂▁▃ ▃▁▁▂ ▁▁▂▁ ▂█▂▃ ▁▁▁▁  2025 Q4
                         ^
```

### 9. Viva — 1.1.6 From international roaming revenue (subscribers from abroad) — 2022 Q2

- **Type:** spike (jumps and comes back)
- **Value:** 193,389 · previous quarter 70,003 (+176%) · next quarter 33,617 (+475%) · usual 139,258
- **In the PDF:** yes, on its own line

```
2021 Q1  ▁▂▂▂ ▁▄▁▂ ▁▂█▄ ▂▄▅▃ ▃▆▆▅  2025 Q4
               ^
```

### 10. Viva — 1.1.6 From international roaming revenue (subscribers from abroad) — 2022 Q3

- **Type:** spike (jumps and comes back)
- **Value:** 33,617 · previous quarter 193,389 (-83%) · next quarter 84,253 (-60%) · usual 139,258
- **In the PDF:** yes, on its own line

```
2021 Q1  ▁▂▂▂ ▁▄▁▂ ▁▂█▄ ▂▄▅▃ ▃▆▆▅  2025 Q4
                ^
```

### 11. Viva — 2.6 Mobile network exploitation and maintenance expenses — 2024 Q4

- **Type:** spike (jumps and comes back)
- **Value:** 1,492,875 · previous quarter 240,048 (+522%) · next quarter 557,919 (+168%) · usual 239,158
- **In the PDF:** yes, on its own line

```
2021 Q1  ▁▁▁▁ ▁▁▁▁ ▁▁▁▁ ▁▁▁█ ▂▂▂▂  2025 Q4
                           ^
```

### 12. Viva — 2.7 Other expenses — 2024 Q4

- **Type:** spike (jumps and comes back)
- **Value:** 323,432 · previous quarter 3,045,667 (-89%) · next quarter 1,724,632 (-81%) · usual 2,622,280
- **In the PDF:** yes, on its own line

```
2021 Q1  ▅▅▆▆ ▅▆▆▇ ▆▆▆█ ▆▆▇▁ ▄▄▄▄  2025 Q4
                           ^
```

### 13. Viva — 9.6.3 Broadband internet subscribers (other than by phone) — 2022 Q3

- **Type:** spike (jumps and comes back)
- **Value:** 11,492 · previous quarter 4,012 (+186%) · next quarter 2,087 (+451%) · usual 4,041
- **In the PDF:** yes, on its own line

```
2021 Q1  ▁▁▁▁ ▁▁▂▁ ▁▁█▁ ▁▁▁▁ ▁▁▁▁  2025 Q4
                ^
```

### 14. Viva — 9.6.3 Broadband internet subscribers (other than by phone) — 2023 Q3

- **Type:** spike (jumps and comes back)
- **Value:** 47,744 · previous quarter 8,336 (+473%) · next quarter 4,510 (+959%) · usual 4,041
- **In the PDF:** yes, on its own line

```
2021 Q1  ▁▁▁▁ ▁▁▂▁ ▁▁█▁ ▁▁▁▁ ▁▁▁▁  2025 Q4
                     ^
```


## Consistency failures (4)

Related indicators that should agree: ARPU vs revenue / subscribers, and subscribers = previous quarter + new activations − churn.

| Check | Operator | Quarter | Actual | Expected | Difference |
|---|---|---|---|---|---|
| subscriber balance (prev + new - churn) | Ucom | 2022 Q1 | 594,054 | 606,903 | -2.1% |
| subscriber balance (prev + new - churn) | Ucom | 2022 Q4 | 652,956 | 660,569 | -1.2% |
| subscriber balance (prev + new - churn) | Ucom | 2024 Q2 | 681,138 | 709,604 | -4.0% |
| subscriber balance (prev + new - churn) | Ucom | 2024 Q4 | 686,720 | 694,273 | -1.1% |

## Level shifts (30)

The indicator moved to a new level and stayed there — usually a real change (new tariff, reclassified costs), listed for context.

| Operator | Indicator | Quarter | Before | After |
|---|---|---|---|---|
| Team | 1.1.10 Other revenues | 2025 Q4 | 426,309 | 149,502 (-65%) |
| Team | 1.1.4 From short and multimedia messages (sms and mms) | 2025 Q4 | 190,911 | 540,856 (+183%) |
| Team | 1.1.6 From international roaming revenue (subscribers from abroad) | 2021 Q4 | 180,199 | 69,181 (-62%) |
| Team | 1.1.6 From international roaming revenue (subscribers from abroad) | 2023 Q4 | 259,925 | 94,558 (-64%) |
| Team | 9.4 Unit price (  interconnection and incoming roaming) (appm) | 2024 Q4 | 5.8 | 2 (-66%) |
| Team | 9.5.2 Postpaid subscribers | 2024 Q2 | 9,132 | 28,894 (+216%) |
| Team | 9.5.3 Broadband internet subscribers (other than by phone) | 2022 Q1 | 5,088 | 14,512 (+185%) |
| Team | 9.5.3 Broadband internet subscribers (other than by phone) | 2024 Q2 | 4,901 | 24,949 (+409%) |
| Team | 9.6.2 Postpaid subscribers | 2024 Q3 | 2,801 | 8,755 (+213%) |
| Team | 9.6.3 Broadband internet subscribers (other than by phone) | 2024 Q1 | 8,678 | 2,731 (-69%) |
| Team | 9.6.3 Broadband internet subscribers (other than by phone) | 2024 Q3 | 1,257 | 6,476 (+415%) |
| Team | 9.6.3 Broadband internet subscribers (other than by phone) | 2025 Q4 | 829 | 2,335 (+182%) |
| Ucom | 2.2 Line rental expenses | 2024 Q1 | 2,977 | 66,963 (+2149%) |
| Ucom | 2.3 Advertising and marketing expenses | 2021 Q2 | 30,347 | 123,073 (+306%) |
| Ucom | 2.3 Advertising and marketing expenses | 2022 Q2 | 101,119 | 30,635 (-70%) |
| Ucom | 2.3 Advertising and marketing expenses | 2022 Q4 | 34,699 | 96,213 (+177%) |
| Ucom | 2.3 Advertising and marketing expenses | 2025 Q2 | 48,904 | 199,390 (+308%) |
| Ucom | 5 Other operating income | 2022 Q1 | -95,182 | 28,501 (-70%) |
| Ucom | 5 Other operating income | 2022 Q3 | -15,007 | -38,046 (+154%) |
| Ucom | 5 Other operating income | 2025 Q3 | 11,159 | 29,016 (+160%) |
| Ucom | 9.5.3 Broadband internet subscribers (other than by phone) | 2022 Q1 | 11,730 | 4,499 (-62%) |
| Ucom | 9.6.3 Broadband internet subscribers (other than by phone) | 2025 Q1 | 14,648 | 5,741 (-61%) |
| Viva | 1.1.6 From international roaming revenue (subscribers from abroad) | 2023 Q3 | 125,644 | 367,814 (+193%) |
| Viva | 2.3 Advertising and marketing expenses | 2024 Q4 | 231,615 | 74,254 (-68%) |
| Viva | 2.3 Advertising and marketing expenses | 2025 Q3 | 96,544 | 249,465 (+158%) |
| Viva | 9.5.2 Postpaid subscribers | 2023 Q3 | 35,610 | 12,028 (-66%) |
| Viva | 9.5.3 Broadband internet subscribers (other than by phone) | 2022 Q1 | 3,931 | 12,464 (+217%) |
| Viva | 9.5.3 Broadband internet subscribers (other than by phone) | 2023 Q3 | 18,198 | 5,797 (-68%) |
| Viva | 9.6.2 Postpaid subscribers | 2023 Q3 | 12,566 | 57,756 (+360%) |
| Viva | 9.6.3 Broadband internet subscribers (other than by phone) | 2024 Q2 | 4,536 | 1,784 (-61%) |
