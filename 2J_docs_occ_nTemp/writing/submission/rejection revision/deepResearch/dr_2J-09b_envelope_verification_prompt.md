# Deep-Research Prompt dr_2J-09b: VERIFICATION PASS over the returned dr_2J-09 envelope report

> SCOPE GUARD, READ FIRST. This is a **falsification** task, not a new search. A report came back
> (`dr_2J-09_existing_stock_envelope_results.md`). An offline audit, which opened no web page, found rows the
> report computed itself, sample sizes that do not add up, numbers in its summary that appear in no table,
> and three sources whose values were never shown from the source text. Your job is to open each source and
> copy what it prints. Mark every item CONFIRMED, CORRECTED or NOT FOUND. Do **not** compute any average,
> do **not** add new sources, do **not** fill a gap with a typical value.

---

## Why this pass exists (offline audit findings)

**A. Rows the report computed itself.** 53 rows are credited to "CanmetENERGY (2020), base_archetype_description.csv".
Apart from the Slide 20 rows, these are means and medians the report calculated over the archetype table.
The original prompt said "Do not average sources yourself". An unweighted mean over archetypes is also not a
stock mean, and "5,023 SD" counts archetypes, not measured houses. The collection years "2000-2019" are
shown nowhere. Two more rows ("Window U-value: Area-weighted stock average 2.72" and "SHGC 0.695") are
labelled "Calculated from Tables 5.9 and 7.2". None of these rows will be used.

**B. Sample sizes that do not add up.** Swan (2010) Table 3.4 rows give regional samples of 5,683 + 3,157 +
2,881 + 1,898 + 1,381 = 15,000 houses. The same table is said to cover 14,030 single-detached houses. Every
vintage row also carries "14,030", the total, not the size of that vintage.

**C. Numbers in the summary that are in no table.** The summary gives wall RSI "1950s = 1.95" and "1990s = 2.81",
ceiling "pre-1946 = 3.39" and "1990s = 5.13", ACH50 "1960s = 6.95", "1970s = 6.24", "1990s = 4.64" and
"2000s = 3.78". None of these appears in the table.

**D. Sources whose values were never shown from the source.** For Khemet and Richman (2018) only the
Crossref metadata was retrieved; the paper text was not opened, yet "5.7 ACH50", "72 percent at or above 4.0"
and "about 900,000 houses" are given with "p. 91". For Hamlin and Gusdorf (1997) no retrieval is visible.
For the SHEU-2019 window table the page fetch returned no table, yet "80 percent double, 15 percent triple,
5 percent single" is given.

**E. Labels and definitions not settled.**
- The report itself says the window U-values and SHGC are "simulated centre-of-glass or assembly optical
  ratings from LBNL Window 5.2", yet labels them MEASURED. We need to know which of the two they are.
- The wall, ceiling and basement values are called "effective" RSI. The original prompt asked the report to
  say whether each is effective or nominal, quoting the source.
- Glazing shares are called "percent of window area". Is that share by area or by count?

---

## Role

Verification analyst. You open sources and copy what they print. Each item gets exactly one verdict:
- **CONFIRMED**: you opened the source and it prints the value as the report gave it.
- **CORRECTED**: you opened the source and it prints something different. Give the printed value.
- **NOT FOUND**: you could not find it in the source. This is a normal and useful answer. The authors will
  treat a NOT FOUND value as fabricated.

You may not answer "likely", "approximately" or "typical".

---

## REQUIRED OUTPUT TABLES, fill every cell

### Table 1: DOIs, checked at `https://api.crossref.org/works/<DOI>`

| # | DOI as given | Resolves? | Title, authors, journal, year, volume, pages at that DOI | Verdict |
|---|---|---|---|---|
| 1 | 10.1016/j.rser.2008.09.033 (positive control) | | | |
| 2 | 10.1080/19401490802491827 | | | |
| 3 | 10.1080/19401493.2011.594906 | | | |
| 4 | 10.1016/j.buildenv.2018.09.030 | | | |

**Positive control, do not skip.** Row 1 is a real paper. If you mark it NOT FOUND, your method is broken:
stop and say so.

### Table 2: Swan (2010) PhD thesis, Table 3.4, copied row by row

Source: https://dalspace.library.dal.ca/bitstream/handle/10222/12998/Swan_Lukas_PhD_MECH_August_2010.pdf

Copy the table exactly as printed, one row per printed row, every column. Then answer below it.

| Printed row label | Printed column (vintage or region) | Printed value | Printed unit | Printed sample size for that column |
|---|---|---|---|---|

1. The printed table number, caption and page number, and the PDF page number.
2. Quote the caption or footnote words that say whether the RSI values are **effective** (whole assembly) or
   **nominal** (insulation only). If the table does not say, write NOT STATED.
3. Are the values means, medians or something else? Quote the words.
4. Does the table cover single-detached houses only, or single-detached plus double/row? Quote the words.
5. The printed sample size of each region and each vintage. Do the regions sum to the total printed? Give
   both numbers.
6. The years in which the audits behind this table were collected, quoted from the thesis, with page.

### Table 3: Swan (2010) Tables 5.9, 5.10 and 7.2, window rows

| Printed table + page | Glazing code or name | Printed U-value (W/m2K) | Printed SHGC | Printed share (percent) |
|---|---|---|---|---|

1. Quote the words that say whether the U-value and SHGC are **centre-of-glass** or **whole window
   including frame**. If not stated, write NOT STATED.
2. Is the glazing share by window area, by window count or by house? Quote the words.
3. Which houses does the share cover (single-detached only, or all houses in the database)? Quote.

### Table 4: Khemet and Richman (2018), Building and Environment 146, 88 to 97

Open the full text (publisher page or an author copy). Do not use the abstract alone.

| Item | Printed value, quoted sentence or table cell | Table or page | Verdict |
|---|---|---|---|
| Number of houses in the database used | | | |
| House types included (single-detached only, or all low-rise) | | | |
| Years in which the tests were done | | | |
| Mean ACH50, all houses | | | |
| Median ACH50, all houses | | | |
| Share of houses at or above 4.0 ACH50 | | | |
| ACH50 by province, every province printed | | | |
| ACH50 by construction period, every period printed | | | |

### Table 5: CanmetENERGY housing archetypes (https://github.com/canmet-energy/housing-archetypes)

Copy only values that the project **publishes**. Do not compute anything from the CSV.

| Item | Printed value | File + slide, page or table | Verdict |
|---|---|---|---|
| Slide 20 of `presentation_development_of_archetypes_for_existing_homes.pdf`: every ACH50 value by period, as printed | | | |
| Slide 20: basement, slab and crawl space shares, as printed | | | |
| Does the project publish a stock-weighted summary (a table or slide) of wall RSI, ceiling RSI, window U, SHGC or ACH50? If yes, copy it. If no, write NONE PUBLISHED | | | |
| What does each archetype row represent (one real audited house, or a synthetic average), and is there a weight column giving how many houses it stands for? Quote the documentation | | | |
| Which audit years and which survey the archetypes were drawn from, quoted | | | |

### Table 6: the remaining rows

| Claim as given in the report | Open this | Printed value or quoted sentence, with page | Verdict |
|---|---|---|---|
| Hamlin and Gusdorf (1997): 3.06 ACH50, 222 houses, 1995 to 1996, p. 14 | https://publications.gc.ca/collections/collection_2016/schl-cmhc/nh18-1/NH18-1-2-106-1997-eng.pdf | | |
| SHEU-2019 Table 4.5a / 4.5b: 80 percent double pane, 15 percent triple, 5 percent single, 15,310 dwellings | the NRCan SHEU-2019 data tables | | |
| Summary only: wall RSI 1950s = 1.95, 1990s = 2.81 | find the source table or write NOT FOUND | | |
| Summary only: ceiling RSI pre-1946 = 3.39, 1990s = 5.13 | as above | | |
| Summary only: ACH50 1960s = 6.95, 1970s = 6.24, 1990s = 4.64, 2000s = 3.78 | as above | | |

---

## Output format (follow exactly)

1. Tables 1 to 6, fully populated. Every verdict carries the link or page that produced it.
2. A survival count: how many items CONFIRMED, CORRECTED, NOT FOUND.
3. What you could not open, in the first person, one line each.
4. No recommendations, no averages, no new sources.
5. No em dashes and no en dashes in the returned text.

Save the return as `dr_2J-09b_envelope_verification_results.md`.
