# Preprocessing precedents — where the earlier papers already ruled

**What this file is.** A lookup table for preprocessing decisions that were already taken and
defended in the 2nd and 3rd papers, so a 4J decision can start from a precedent instead of from
zero. Pointed at by the author on 2026-08-20.

🔴 **What transfers and what does not.** 4J is **HETUS-only** (ES / UK / IT). The earlier papers are
**GSS Canada** (cycles 2005 / 2010 / 2015 / 2022). **No variable name, code value or crosswalk row
transfers.** What transfers is the *method*: how a column gap is investigated before it is called
absent, how a sentinel is separated from a real value, how a universe skip is separated from
non-response, and how a change is proved additive. Every entry below is marked **METHOD** (reusable)
or **CANADA-ONLY** (read for shape, never for content).

---

## 1. The map

| # | Path (relative to `GSSCanada-main/`) | Lines | What it holds |
|---|---|---|---|
| 1 | `3J_docs_occ_nTemp/Leg2_2-split/Step1_docs/3rdJ_01_readingGSS.md` | 465 | Column **selection** per cycle, with the codebook citation for each pull. The longest and most detailed of the six step docs. |
| 2 | `3J_docs_occ_nTemp/Leg2_2-split/Step2_docs/00_column_availability_investigation.md` | 309 | 🟢 **The single most useful file here.** A stand-alone read-only investigation of three data gaps, each ending in a verdict plus a costed recommendation. Model this whenever a 4J field looks absent. |
| 3 | `3J_docs_occ_nTemp/Leg2_2-split/Step2_docs/3rdJ_02_harmonizeGSS.md` | 160 | Harmonization as five lettered **Deltas** (A-E). The delta convention itself is the reusable part. |
| 4 | `3J_docs_occ_nTemp/Leg2_2-split/Step3_docs/3rdJ_03_mergingGSS.md` | 159 | Merge plus 30-minute tiling, again as Deltas. |
| 5 | `3J_docs_occ_nTemp/Leg3_4-split/Step1_docs/3rdJ_01_readingGSS_4split.md` | 115 | Leg-3 = Leg-2 **reused verbatim** on the GSS side plus a new non-GSS external acquisition (hotel ISQ/CBRE). The precedent for "add a channel without touching what shipped". |
| 6 | `3J_docs_occ_nTemp/Leg3_4-split/Step2_docs/3rdJ_02_harmonizeGSS_4split.md` | 110 | Deltas A-D; Delta B records a **frozen** rule and still ships its leak cross-tab. |
| 7 | `3J_docs_occ_nTemp/Leg3_4-split/Step3_docs/3rdJ_03_mergingGSS_4split.md` | 105 | 🟢 The **bit-identity gate** (Delta D). See section 4. |
| 8 | `2J_docs_occ_nTemp/outputs_step2/column_categories_comparison.txt` | 62 | Every harmonized column's category distribution side by side across the four cycles. **The cheapest cross-wave sanity check there is.** See section 5. |
| 9 | `2J_docs_occ_nTemp/examples/JournalZero/2ndJ_datapreprocessing.py` | 642 | The original preprocessing script: readers for SAV / DAT+SPS / fixed-width+sps / sas7bdat, plus the raw-to-canonical mapping dicts inline. CANADA-ONLY for content. |
| 10 | `2J_docs_occ_nTemp/examples/Journal1st/submission_Occ_NUsJournal.docx` | 13 MB | The 1st-paper submission. Not read for this index. |
| — | `2J_docs_occ_nTemp/outputs_step1/`, `outputs_step2/`, `outputs_step3/` | — | The actual per-cycle CSVs at each stage (`main_<cycle>.csv`, `episode_<cycle>.csv`, then `merged_episodes`, `hetus_wide`, `hetus_30min`, `copresence_30min`). Useful to diff a claim against, not to read. |

⚪ Each `*_val.md` / `*_val.py` twin next to a step doc is the **validator**, written separately from
the builder. That separation is itself the precedent 4J's gate batteries follow.

⚪ `2J_docs_occ_nTemp/examples/JournalZero/preProcessing_Func.py` is listed in the directory but the
helper functions are actually inlined at the top of `2ndJ_datapreprocessing.py` (lines 9-430).

---

## 2. METHOD — how a "missing" column was investigated before it was declared absent

`00_column_availability_investigation.md` is the template. Its shape:

1. **Question**, stated as a falsifiable claim ("is there genuinely NO telework variable in 2005?").
2. **Sources checked**, listed by path, with the read-only status stated.
3. **Verdict** in capitals, on its own line, *before* the evidence.
4. **Evidence** as a numbered list — the header catalogue, the loaded file, the value distribution
   side by side with a wave where the field is known good, and the codebook question text.
5. **Per-cycle verdict table** — one row per wave, one column for "comparable to the reference?"
6. **Recommendation** with an **estimated implementation cost** ("2-line change in `derive_telework()`").

🔴 **The finding that justifies the whole method.** The pipeline had `TELEWORK` as all-NaN for 2005
*by design*, on the belief that no instrument existed. `MAR_Q190` was there the whole time — in the
header catalogue, in the loaded CSV, with 2,177 Yes / 9,531 No and value codes identical to 2010.
The doc's own verdict on the earlier note: **the "2005: no instrument" claim in Delta E is wrong.**

Directly relevant to 4J: the same class of error was hit twice this year — the TABULA
"scraping only" verdict, and the first wrong Nomis query syntax. Both nearly declared a real source
non-existent. **An absence claim needs the same six-part treatment a positive finding gets.**

---

## 3. METHOD — universe skip vs non-response vs structural absence

Gap 2 of the same document separates three things that all look like missing data:

| | What it is | How it was proved | What you may do |
|---|---|---|---|
| **Universe skip** | The question was never asked for that row | Missingness is *structured*: 96.5 % of 2005 co-presence NaNs sit at one location code, concentrated on sleep (37,873) and personal care (24,365); the codebook carries an explicit `7 "Not asked for activity code 002.0"` | **Never impute.** NaN means "not collected", not "alone" |
| **Non-response** | Asked, not answered | Missingness is *diffuse* across categories (2022, 6.8 %) | Handle as non-response, declare the rate |
| **Structural absence** | The category did not exist in that wave's instrument | 0 % fill, not low fill (`colleagues` is 0 % in 2005 and 2010, introduced 2015) | Declare, do not backfill |

🔴 **The distinguishing test is the *shape* of the missingness, not its size.** A 20 % gap that is
96 % concentrated in one cell is a skip; a 7 % gap spread evenly is non-response.

🟢 **4J already hit this exact fork and got it right by the same test.** `FINDING 48`: Italy's whole
`strat_econ_status = unknown` mass is the `11-14` band, *exactly* (1,644 of 1,644) — so what Step 2
had logged as an Italian non-response asymmetry is an **age rule**, not non-response. Same shape of
evidence, same conclusion. And `FINDING 51` is the third row of that table: the Spanish census has
no `homemaker` category at all — structural absence, so it is declared and the fold is fitted on
five bands, not backfilled.

---

## 4. METHOD — the additive-delta convention and its proof

Both legs of 3J structure every change as lettered **Deltas** (A, B, C…), each one a short block
saying what is added and what is left untouched. Leg 3 then proves the claim rather than asserting it:

🟢 **Delta D, `3rdJ_03_mergingGSS_4split.md`** — the **bit-identity gate**. After adding a whole new
channel, all six legacy outputs were re-hashed and shown SHA-256 identical to the Leg-2 files,
*including the parquet*: `merged_episodes.csv 32b9905d…`, `hetus_wide.csv b1bf8dc1…`,
`hetus_30min.csv 6e3add7c…`, `copresence_30min.csv 9fe76f96…`, `work_30min.csv 9e5fd816…`,
`merged_episodes.parquet 9b4046f1…`. Its conclusion: the retail delta is purely additive, so there
is zero risk to the shipped Leg-1 / Leg-2 results.

🔴 **This is the precedent behind the standing 4J rule that fixes must be additive.** When a 4J change
claims to disturb nothing, the precedent says: re-hash the untouched artefacts and show it. It is
what `D-S6-1` did (the household re-split was proved a **re-label** — 0 texts differ, 13,149 labels
changed — so no Step 3 gate was disturbed) and what the `FINDING 52` fix did (the existing
rakeddonor selftest was re-run 23/23 green *before* the new cases were added, so the new guard is
shown not to have moved anything old).

⚪ **Also worth copying.** Leg-3 Delta B records a rule that is **frozen** and *still* produces its
per-cycle leak cross-tab as a Step-2 validation output. A frozen decision keeps emitting its
diagnostic. That is exactly the posture 4J's frozen `prereg.md` takes.

---

## 5. METHOD — the cheapest cross-wave check that exists

`2J_docs_occ_nTemp/outputs_step2/column_categories_comparison.txt` prints, for each harmonized
column, the category share in every wave on adjacent lines:

```
--- Column: AGEGRP ---
  2005: [1.0: 12.7%, 2.0: 15.6%, 3.0: 19.7%, ...]
  2010: [1:  8.9%,  2: 12.5%,  3: 15.9%, ...]
```

🔴 **Two failure modes fall out of it immediately and neither needs a gate:**

1. **A dtype split.** `2005: [1.0: …]` against `2015: [1: …]` — same column, float in two waves and
   int in the other two. Any code comparing category keys as strings silently matches nothing.
   *4J has been bitten by this class twice: the awk `hi=ab[2]` string-versus-number comparison that
   truncated Spain's `75+` band by 985.088, and `-F,` applied to a tab-separated lookup, where the
   subtraction silently did nothing and the counts came back unchanged.*
2. **An empty cell.** `MODE 2005: []` says the field does not exist in that wave, in one glance.

🟢 **Worth building the 4J equivalent** — one file, one block per prefix field, one line per country,
shares side by side. It would have shown the `FINDING 48` `(11-14, econ)` country fingerprint on
sight instead of after a Step-2 asymmetry had been logged as non-response.

---

## 6. CANADA-ONLY — what the crosswalks actually look like

Read only for shape. From `2ndJ_datapreprocessing.py` (the `__main__` block, lines ~470-530) and
reused through both 3J legs:

* **Activity**: raw `ACTCODE` to **13 canonical classes**, written as a `{canonical: [raw, raw, …]}`
  dict. Class `13` is the catch-all for residual/unspecified codes (`30, 90, 190, 291, …, 990`).
* **Location**: raw `PLACE` to **18 canonical classes**, same dict form. Note `18: ["97","98","99"]`
  — **the sentinels get their own class; they are not dropped and not merged into a real location.**
* **Co-presence**: eleven raw binaries mapped `{1:[1], 2:[2], 9:[7,8,9]}` — again **sentinels to a
  distinct code, never to "no"** — then merged with an explicit `merge_map`
  (`otherHHs = OTHFAM + NHSDCL15 + NHSDC15P`, `parents = PARHSD + NHSDPAR`) and renamed to the
  canonical names (`occID`, `occACT`, `occPRE`, `start`, `end`, `Alone`, `Spouse`, `Children`,
  `otherInFAMs`, `Friends`, `Others`).
* **Wave drift inside one code system**: 2005 uses integer codes (`80`), 2010 uses decimal sub-codes
  for the same concepts (`80.1, 80.2, 80.3, 80.9`). **The crosswalk is per wave even when the
  variable name is identical.** Directly analogous to 4J's ES `TRIM` against IT `meseri` — both
  pre-banded, offset by one month, sharing no boundary — which is why `D-S2-19` **dropped `season`**
  rather than forcing a shared boundary onto them.

🔴 **Sentinel handling is the one content rule that generalises.** `7 / 8 / 9` (and `97 / 98 / 99`)
are *Not asked / Not stated / Don't know*. They go to their own class or to NaN, **never to a
substantive category**, and the three are kept distinct from each other wherever the analysis cares
about the difference.

⚪ **Caveat on file 9.** Every path in it is a hardcoded macOS path
(`/Users/orcunkoraliseri/Desktop/Postdoc/…`). It does not run here. Read it, do not invoke it.

---

## 7. Where 4J deliberately departs from these precedents

| Precedent | 4J | Why |
|---|---|---|
| Deltas are described in prose and then built | Every gate must be **seen failing**, with a named perturbation that fells it | 52 recorded failure classes; a gate nobody watched fail is not evidence |
| Validators are a `*_val.py` twin | Full gate batteries with a coverage clause and one perturbation per gate | Same instinct, more of it |
| Decisions live in the step doc's Progress Log | Decisions are numbered (`D-S<step>-<n>`), ruled by the author, and a ruling may **reopen a closed step** (`D-S2-18` did) | LOCO means a preprocessing choice can leak country identity, so it needs an audit trail, not a note |
| Recommendation plus estimated cost | Same, and the author may overrule — when that happens the cost is **recorded, not re-litigated** (`D-S5-4` (b), which created the declared econ-marginal asymmetry) | — |

---

## 8. How to use this file

1. A 4J preprocessing question comes up.
2. Look in sections 2-5 for a **METHOD** entry matching its shape — absent column / skip versus
   non-response / additive change / cross-wave drift.
3. Open the one file named there. Do not read all ten.
4. If the precedent settles it, cite it in the decision record. If it does not, say so explicitly —
   these are GSS Canada papers and most *content* questions will not transfer.

**Read in full for this index:** files 2, 8, and the `__main__` mapping block of file 9.
**Headings and Progress Logs only:** files 1, 3, 4, 5, 6, 7. **Not opened:** file 10.
