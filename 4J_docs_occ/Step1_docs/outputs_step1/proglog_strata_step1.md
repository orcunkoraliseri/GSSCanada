## Progress Log fragment — Task B, Step 1 (M-8 / D-S2-18 / D-S2-19 additive round)

**Fragment for the manager to merge. Not the Progress Log itself.**

### What was built

Extended all three readers (`tools/4thJ_read_spain.py`, `4thJ_read_italy.py`, `4thJ_read_uk.py`) to
carry the six conditioning-strata raw values, per D-S2-18 M-8-b / D-S2-19, exactly as approved in
`Step1_docs/outputs_step1/strata_proposal.md` (Task A, already accepted). No mapping, no banding, no
collapsing at Step 1 — six new columns per country, `strat_<name>_raw`.

* **Spain**: `strat_age_band_raw` (EDAD), `strat_sex_raw` (SEXO), `strat_hh_type_raw` (TIPOHOG, new
  household join), `strat_econ_status_raw` (HRELACTIV), `strat_day_type_raw` (DDIASEM),
  `strat_season_raw` (TRIM). 🔴 **New household-type join**: `DHOGAR.TIPOHOG` on `hid` — the first time
  any round has read `DHOGAR.TXT` (F-ES-10). Join asserted non-zero and zero-unmatched (D-S2-16):
  9,541 distinct households matched, 0 unmatched episodes of 430,754.
* **Italy**: `strat_age_band_raw` (claseta2), `strat_sex_raw` (sesso), `strat_hh_type_raw` (tipfa2m),
  `strat_econ_status_raw` (newcondm), `strat_day_type_raw` (gsett), `strat_season_raw` (meseri).
  `tipfa2m` and `newcondm` added to the existing `Individui.txt` join (no second file, no second join
  — both already live in the person file already joined for sesso/claseta2).
* **UK**: `strat_age_band_raw` (DVAge), `strat_sex_raw` (DMSex), `strat_hh_type_raw` (dhhtype),
  `strat_econ_status_raw` (deconact), `strat_day_type_raw` (ddayw — 🔴 **not** `DiaryDay_Act`, per
  F-UK-17/D-S2-19), `strat_season_raw` (dmonth). `dhhtype` and `deconact` both live in
  `uktus15_individual.tab` (DD:individual pos. 588, 598) — **not** `uktus15_household.tab`, which
  still is not read (F-UK-14 stands unchanged).

### Three defects found and fixed during this round, none a policy question

All three were caught by the pipeline's own refuse-rather-than-assume design on a first sbatch
attempt — the mechanism worked as designed — and were corrected against the raw file, not assumed
from the codebook's prose. The first two below were caught by the readers' own V1.d refusal
(`ParseFailure`); the third (below, its own subsection) was caught one step downstream, by the
harmoniser's crosswalk-join assertion.

1. **Italy `tipfa2m` is zero-padded 2-digit** (`"08"`, not `"8"`), the same convention as `claseta2`.
   `codebook_facts_italy_strata.md`'s condensed code table (and `strata_proposal.md`/
   `crosswalk_strata.csv`, both built from it) used the codebook's unpadded prose listing. First
   sbatch run (job 1254922) FAILed loudly: `tipfa2m: ['01','02',...,'09'] are neither a
   CLS-var16-documented code nor a known enumeration gap`. Corrected in the reader's
   `TIPFA2M_DOCUMENTED_CODES` set and in `crosswalk_strata.csv`'s `strat_hh_type`/it rows
   (zero-padded to match); re-run succeeded.
2. **UK `dhhtype`/`deconact`'s blank sentinel is a literal single space (`" "`)**, the same
   convention already documented for the weight columns (F-UK-8), not an empty string. First sbatch
   run (job 1254923) FAILed loudly: `individual.dhhtype: unrecognised values [' ']`. Measured directly
   against the raw file: `dhhtype` `" "` count = 411 (matches the codebook's 3.6 % exactly);
   `deconact` `" "` count = 25 (matches the "25 blank" component of its 722-row breakdown exactly).
   Normalised `" "` → `""` in the reader before the domain check and before `strat_hh_type_raw`/
   `strat_econ_status_raw` are set, so the crosswalk's declared blank→`unknown` row matches; re-run
   succeeded.

### A third defect, found only when the reader's downstream (Step 2) consumer ran it

3. **Italy `newcondm`'s blank sentinel is also a literal single space (`" "`)**, same class as fix #2,
   not caught by the reader's own alphabet check because that check used `.str.strip()` (which
   silently normalises `" "` to `""` before comparison) while the emitted `strat_econ_status_raw`
   column used the unstripped raw value. Surfaced one step downstream, in the Step 2 harmoniser
   (job 1254934 FAILed: `strat_econ_status (it): 39515 episode(s) have a raw value not in
   crosswalk_strata.csv: [' ']`), not in the reader itself. Measured directly: `newcondm` `" "` count
   = 6,067, matching the codebook's 13.5 % exactly. Normalised `" "` → `""` in the reader (Italy
   reader re-run, job 1254940) before `strat_econ_status_raw` is set. `tipfa2m` carries no such
   sentinel (measured: 0 blank/space rows), so it needed no equivalent fix.

### B2 acceptance test

Three unchained `sbatch` jobs re-ran the readers (1254921 Spain; 1254922 Italy FAILed on the
zero-padding defect, 1254927 re-run FAILed on the `newcondm` space-sentinel defect two steps later in
Step 2, 1254940 final re-run succeeded; 1254923 UK FAILed on the space-sentinel defect, 1254928 re-run
succeeded), then the sixteen-gate battery ran on all three against a fresh run-stamped directory
`outputs_step1/run_20260817-strata`, copying in the reference inputs (`crosswalk_source_*`,
`acquisition_manifest.json`, `codebook_facts_<country>.md`, `parse_report_<country>.txt`) the same way
the accepted `run_20260816-2210` round did.

* **Episode counts, unchanged**: ES **430,754** / UK **587,632** / IT **1,077,657** — verified against
  `episodes_<country>.parquet` row counts and each reader's own parse-completeness section, all three.
* **Column counts**: ES 31, IT 33, UK 40 (25/27/34 original + 6 new `strat_*_raw` each).
* **Sixteen gate verdicts, verdict-for-verdict identical to `run_20260816-2210`**:
  - Italy: 13 gates scored (`G1.1,G1.2,G1.3,G1.4,G1.5,G1.6a,G1.6b,G1.7a,G1.7d,G1.9,G1.10,G1.11,G1.12`),
    NOT CHECKED `{G1.7b,G1.7c,G1.8}`, **PASS 12 / FAIL 1** — same set, same per-gate verdicts, same
    perturbations-that-fell-it, as the reference report.
  - UK: 14 gates scored (adds `G1.7c`), NOT CHECKED `{G1.7b,G1.8}`, **PASS 13 / FAIL 1** — identical
    to the reference report.
  - Spain: 15 gates scored, NOT CHECKED `{G1.7b}`, **PASS 15 / FAIL 0** — every one of the fifteen
    per-gate lines (verdict, perturbations that felled it) checked byte-for-byte identical to the
    reference report.
* **Standing FAILs, confirmed unrepaired**: Italy's `G1.6b` **still FAILs** (`never fell` —
  acquisition-manifest provenance URL gap, unrelated to strata) and the UK's `G1.4` **still FAILs**
  (activity/location code-list membership, unrelated to strata). Neither round quietly repaired a
  known FAIL.
* 🔴 **A process mistake, not a data defect, that cost two extra gate re-runs**: my first Italy and
  UK gate-battery jobs (1254932, 1254931) were pointed at a run-stamped directory I had seeded with
  `episodes_<country>.parquet` and every reference file the wrapper scripts copy — **except
  `parse_report_<country>.txt`**, which `G1.5` reads from disk. Both runs scored `G1.5` as
  `NOT CHECKED ("no parse report on disk")` instead of `PASS`, a real mismatch against the reference
  report's gate count (13→12 for Italy, 14→13 for UK). Caught by comparing gate counts against
  `run_20260816-2210` rather than only checking pass/fail totals; fixed by copying the three
  `parse_report_<country>.txt` files into the run dir and re-running all three gate batteries
  (1254938 Italy, 1254939 UK, 1254949 Spain).

### WHAT I DID NOT VERIFY

* I did not independently re-derive `codebook_facts_<country>_strata.md` or `strata_proposal.md` —
  Task A was completed and accepted (D-S2-19) before this round started; I read them, transcribed the
  approved band set literally, and treated a value mismatch (see the two fixes above) as a defect in
  my own crosswalk/reader code to fix against the raw file, not as licence to re-open Task A's
  transcription.
* I did not verify `weight_ind`/`weight_dia` or any pre-existing Step 1 column beyond confirming the
  new join and new columns did not disturb them — this round is additive by construction and the B2
  acceptance test (all sixteen gate verdicts unchanged) is the check that matters for that claim.
* Whether `dhhtype`'s, `deconact`'s and `newcondm`'s `" "` sentinels are the *only* undocumented
  formatting quirks among the newly-read fields, versus three coincidences I happened to catch — not
  independently re-audited beyond what the domain-refusal check (readers) and the crosswalk-join
  assertion (harmoniser) surfaced. `tipfa2m`, `claseta2`, `sesso`, `gsett`, `meseri`, `EDAD`, `SEXO`,
  `HRELACTIV`, `DDIASEM`, `TRIM`, `DVAge`, `DMSex`, `ddayw`, `dmonth`, `TIPOHOG` were all measured
  clean (0 unrecognised values on the real run) but not exhaustively re-audited byte-for-byte beyond
  what the reader's own domain checks already assert.
* I did not check whether the fifteen/sixteen gates unrelated to the two standing FAILs would have
  caught any of the three defects above if they had gone unfixed — all three were caught by the
  pipeline's own refuse-rather-than-assume design (reader `ParseFailure` for two, harmoniser
  `SystemExit` for one) before or instead of any gate running, which is a stronger check than a gate
  would have been: a `ParseFailure`/`SystemExit` means nothing downstream is trusted at all, not just
  one gate's verdict.
