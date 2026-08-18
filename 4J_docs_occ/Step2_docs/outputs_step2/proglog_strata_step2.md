## Progress Log fragment — Task B, Step 2 (M-8 / D-S2-18 / D-S2-19 additive round)

**Fragment for the manager to merge. Not the Progress Log itself.**

### What was built

* `Step2_docs/outputs_step2/crosswalk_strata.csv` — the fifth crosswalk, 127 rows,
  `stratum, country, source_value, source_label, target_band, citation`. Built from
  `strata_proposal.md` and the three `codebook_facts_<country>_strata.md` files (Task A, accepted),
  against D-S2-19's approved band set. `season` carries **no rows** (dropped from the prefix,
  D-S2-19 §1). `unknown` is declared for `strat_econ_status` and `strat_hh_type` **for all three
  countries**, including the two country/stratum pairs measured at 0.0 % prevalence (Spain, both
  strata; Italy, household type) — per D-S2-19 §3, availability, not prevalence, is what matters.
  `strat_age_band`/`strat_sex`/`strat_day_type` carry no `unknown` row for any country (0.0 %
  measured, all three, all three strata; not part of the approved band set).
* Extended `tools/4thJ_harmonise_step2.py`: reads `crosswalk_strata.csv`, emits the five harmonised
  columns (`strat_age_band`, `strat_sex`, `strat_hh_type`, `strat_econ_status`, `strat_day_type`)
  beside the six `_raw` carriers. `strat_season_raw` ships with no harmonised partner. Age mapping is
  an exact categorical crosswalk join for Italy (already banded, `claseta2`) and a numeric-range
  `pd.cut` for Spain/UK, with bin edges parsed directly from the crosswalk's own `"11-14"`/`"75+"`
  style rows rather than hardcoded separately. Every stratum join asserts a non-zero match count and
  FAILs loudly (raises `SystemExit`) on any raw value not present in the crosswalk (D-S2-16) — no
  stratum may resolve to a silent null. `country` is lowercased via the existing
  `COUNTRY_CROSSWALK_TAG` mechanism already in the harmoniser (unchanged from D-S2-16's original fix).
* Italy's `tipfa2m` gap-code guard: if any of the eight undocumented CLS-var16 codes
  (`12,13,17,18,26,27,31,32`) is observed unmapped for `strat_hh_type`/it, the harmoniser FAILs
  explicitly rather than folding it into `other_complex`. **Measured this round: all eight occur 0
  times** in `uso_tempo_Microdati_Anno_2013_Individui.txt` (44,866 rows; 32 distinct non-blank
  `tipfa2m` codes observed, exactly the CLS-var16-documented set). The guard did not fire. Recorded
  in `crosswalk_unmapped.md` PART E with the measured frequency either way, per the task's explicit
  instruction.

### Three defects found and fixed, all caught by the pipeline's own refuse-rather-than-assume design
### (full detail in the Step 1 fragment)

1. Italy `tipfa2m` is zero-padded 2-digit — caught by the Step 1 reader's own domain check (job
   1254922 FAILed). Corrected in `crosswalk_strata.csv`'s `strat_hh_type`/it rows and the reader.
2. UK `dhhtype`/`deconact`'s blank sentinel is a literal single space, not an empty string — caught
   by the Step 1 reader's own domain check (job 1254923 FAILed). Corrected in the reader; the
   crosswalk's declared blank→`unknown` rows already used `""`, so no crosswalk change was needed.
3. **Italy `newcondm`'s blank sentinel is also a literal single space** — caught one step later, by
   **this harmoniser's own crosswalk-join assertion** (job 1254934 FAILed: `strat_econ_status (it):
   39515 episode(s) have a raw value not in crosswalk_strata.csv: [' ']`), not by the Step 1 reader,
   because the reader's own alphabet check used `.str.strip()` (which silently normalises `" "` to
   `""`) while the emitted raw column did not. This is the exact class of near-miss D-S2-16 exists to
   catch: a join that would otherwise have produced 39,515 silent nulls instead FAILed loudly.
   Corrected in the Step 1 reader (re-run, job 1254940), then the Italy harmoniser re-ran clean
   (job 1254952).

None was a policy question — all three were data-format mistakes in the crosswalk/reader I built,
fixed against the measured raw file rather than coded around.

### B5 acceptance test — the four fixed numbers, all confirmed exactly

| | ES | UK | IT |
|---|---|---|---|
| **episodes (target / measured)** | 446,547 / **446,547** ✅ | 567,381 / **567,381** ✅ | 1,010,140 / **1,010,140** ✅ |
| **splits (target / measured)** | 37,830 / **37,830** ✅ | 0 / **0** ✅ | 0 / **0** ✅ |

🔴 **Note on the "splits" unit**: the harmoniser's own log line ("splits at origin for es: 18915")
counts split *events* (one 04:00-crossing Spanish episode → two output rows). The task's acceptance
figure (37,830) counts *rows carrying `split_at_origin=True`* — two per event, `18,915 × 2 = 37,830`
— confirmed directly on the combined table (`combined.groupby("country")["split_at_origin"].sum()`).
Same underlying result, two different units; not a discrepancy.

**Combined `harmonised.parquet`**, built locally (`py`, not the cluster — a concatenation of three
already-computed parquets, same precedent as the 2026-08-16 combine): **2,024,068 rows, 51 columns**
(40 → 51, eleven new: five harmonised `strat_*` + six `strat_*_raw`, no `strat_season`). **73,254
diaries**, every one tiling `[0,1440)` exactly once (0 gap/overlap rows, 0 diaries not summing to
1440, checked directly on the combined table, not assumed from the per-country logs). **`act2` nulls
= 587** (exact). **Only `split_at_origin` contains "origin"** in any column name (checked directly:
`[c for c in combined.columns if "origin" in c.lower()] == ['split_at_origin']`). Age floor 11, passed
explicitly (`--age-floor 11`, no default) to all three harmoniser jobs.

Every stratum's crosswalk join matched 100 % of episodes for all three countries (printed by the
harmoniser and re-checked against the per-country `filter_report_<country>.md` addenda): ES 446,547/
446,547, UK 567,381/567,381, IT 1,010,140/1,010,140, for all five harmonised strata.

### Deliverables

`crosswalk_strata.csv`, updated `tools/4thJ_harmonise_step2.py`, `harmonised_{es,it,uk}.parquet`,
combined `harmonised.parquet` (51 columns), this fragment, plus a strata-specific addendum written
into each per-country `filter_report_<country>.md` (crosswalk join match counts per stratum).

### WHAT I DID NOT VERIFY

* I did **not** run the Step 2 gate battery (`G2.17`/`G2.18`/`V2.j`/`V2.k`) — per the task document,
  that is explicitly a different employee session's job, and running it here would make the
  column-build and the gate-scoring the same session, which the task forbids.
* I did not re-derive the other four crosswalks (activity, secondary activity, location, co-presence)
  or touch anything in the D-S2-12 base record contract — this round is additive by construction and
  the acceptance test (four fixed row counts, 51 columns, unchanged) is the check that the rest of
  the table was not disturbed.
* I did not independently verify that `crosswalk_strata.csv`'s citations resolve to the exact page/
  sheet named — they are copied from `codebook_facts_<country>_strata.md`'s own citation column,
  which I did not re-derive from the source documents myself (Task A's job, already accepted).
* Whether the `strat_econ_status`/`strat_hh_type` `unknown`-band prevalence asymmetry
  (ES 0.0 %/UK 6.3 %/IT 13.5 % for econ status; ES 0.0 %/IT 0.0 %/UK 3.6 % for household type) is
  missing-at-random or structurally concentrated — not investigated here; D-S2-19 §3 already rules
  that this is scored on availability, not prevalence, so it does not gate this round, but the
  underlying data question is still open per `strata_proposal.md`'s own "WHAT I DID NOT VERIFY".
* The two named limitations D-S2-19 §4 requires carrying rather than repairing: UK `dhhtype=3`
  cannot separate a childless couple from one whose children are all 16+ (F-UK-18), and UK
  `deconact=-1` → `unknown` is the generic "not applicable" reading, an assumption. Both are recorded
  in `crosswalk_strata.csv`'s `source_label`/`citation` fields for the affected rows, not resolved.
