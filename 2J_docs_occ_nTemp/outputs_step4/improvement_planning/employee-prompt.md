# Employee Prompt — Task D (Improvement 4): `step4_validation_report_v7.html`

> **Paste everything below this line into a fresh Sonnet employee session.**

---

You are the **employee**. Execute the task below **end-to-end without stopping for questions** — all Open Decisions are already resolved by the manager and stated inline. If you hit a genuine blocker or must deviate, do **not** silently work around it: record the deviation in the Progress Log entry and continue with the rest. Append Progress Log entries on completion (Step D8 lists exactly where). Work locally with `py` — no cluster access is needed or allowed for this task.

## Context (read first, ~10 min)

The Step-4 validation report `2J_docs_occ_nTemp/outputs_step4/step4_validation_report_v6.html` is **internally inconsistent**: its prose, tables, and the three Task-C figures are post-fix (Task A region-tier linkage: 2005 matched share 9.03%→15.76%; Task B joint 3-head rake: gate 6.2 PASS, 22P/0W/0F), but the **seven section charts inherited from v5** (Sections 1–7) were rendered on 2026-07-09 ~12:23 against the *old* population — **before** Task A/B rebuilt `0_Occupancy/Outputs_21CEN22GSS/aug_pipeline/21CEN22GSS_aug_Full_Schedules_excl.csv` (final rebuild timestamp 2026-07-09 20:47). A reader comparing the Section-2/6/7 figures against the update boxes sees contradictory data (e.g. weekday Paid-work over-firing +12.3 pp that Task B already fixed).

Your job: produce **`step4_validation_report_v7.html`** — a copy of v6 in which every inherited section chart is re-rendered on the final corrected population and every stale number/sentence is refreshed. **v5 and v6 must remain byte-identical** (record sha256 before and after your work).

**Required reading before writing any code:**
1. `2J_docs_occ_nTemp/outputs_step4/step4_improvement_notes.md` — section "Improvement 4" (the full defect analysis; your task is its execution).
2. `2J_docs_occ_nTemp/outputs_step4/improvement_planning/step4_improvements_implementation.md` — section "Task D" (spec) + the Remediation checklist R1–R7 and the final Progress Log entries (these carry the *authoritative post-fix numbers* you will need for prose/table refreshes).
3. `2J_docs_occ_nTemp/outputs_step4/_gen_v5_plots.py` — the `CalVal` class you will reuse (chart rendering on the calibrated population, `usecols`-guarded load).
4. `2J_docs_occ_nTemp/outputs_step4/_gen_v6_plots.py` — the anchor-injection / idempotency-guard pattern and (for Fig 1/2) the token-revert regeneration trick.
5. `2J_docs_occ_nTemp/04F_validation.py` — only the chart-producing methods (`validate_activity_distribution`, `validate_at_home_rate`, `validate_temporal_structure`, `validate_demographic_conditioning`, `validate_cross_stratum_consistency`, `validate_training_curves`) and `fig_to_b64`.

## Inputs (all already exist — do not regenerate any data)

| File | Role | Caution |
|---|---|---|
| `0_Occupancy/Outputs_21CEN22GSS/aug_pipeline/21CEN22GSS_aug_Full_Schedules_excl.csv` | **Final corrected population** (Task A+B, 2026-07-09 20:47, ~571 MB) | Load with the `NEED` `usecols` filter exactly as `_gen_v5_plots.py` does — never whole-load all 545 columns. Close other heavy processes first (local box cannot be rebooted remotely). |
| `2J_docs_occ_nTemp/outputs_step3/hetus_30min.csv` | Observed GSS side | unchanged |
| `2J_docs_occ_nTemp/outputs_step4/outputs_step4_J3_PSB/step4_training_log.csv` | Section-1 curves | unchanged input — chart re-renders identically; re-render anyway for uniform provenance |
| `2J_docs_occ_nTemp/outputs_step4/step4_validation_report_v6.html` | Source of v7 copy | **read-only** |

## Steps

### D1 — Copy + hashes
- Record `sha256` of `step4_validation_report_v5.html` and `_v6.html` (you will re-verify at the end).
- Copy `_v6.html` → `step4_validation_report_v7.html` (same directory). All edits below happen **only** in v7.

### D2 — `_gen_v7_plots.py` (new file, `outputs_step4/`)
Copy the structure of `_gen_v5_plots.py` (importlib load of `04F_validation.py`, the `CalVal` subclass with its `_load_data` override and the chart-only `validate_cross_stratum_consistency`). Changes vs v5's generator:
- Point `HTML` at `step4_validation_report_v7.html`.
- The `{{CHART_*}}` placeholders **no longer exist** (consumed when v5 was built). Replace by **alt-keyed substitution**: each inherited chart lives in v7 as `<img src="data:image/png;base64,…" alt="<TITLE>"/>`. Regex-replace the whole `<img …>` tag keyed on these **exact seven alt titles** (verify each against the file with a grep before relying on it):
  1. `Training Curves`
  2. `Activity Distribution by Stratum`
  3. `JS Heatmap`
  4. `AT_HOME Daily Rhythm`
  5. `Activity Heatmap`
  6. `Work Proportion by LFTAG`  *(note: the section heading says "Paid-Work Proportion by LFTAG" — the alt is the shorter title)*
  7. `Work by Stratum`
- **Do not touch** the three Task-C figures (their alts differ — e.g. the §9.1 funnel); a strict alt-match on the seven titles above protects them automatically.
- Idempotency guard: embed a short provenance token in each new tag (e.g. `data-regen="v7-20260709"`); on a second run, tags carrying the token are skipped (report `0 replaced, 7 skipped-present`).
- While rendering, **capture and print** the fresh aggregate activity JS (returned/computed inside `validate_activity_distribution`) and the weekday observed-vs-synthetic Paid-work slot shares — you need both for D3 and D5.

### D3 — Prose/number refresh in v7 (surgical, keep everything else)
The v5-era text carries numbers computed on the old population. Fix, using values you either (a) re-derived in D2 or (b) take from the implementation doc's R3–R7 Progress Log entries (state the source for each in your Progress Log):
1. **Header block**: retitle to v7; add a "Supersedes v6" line stating: section charts (Sections 1–7) re-rendered 2026-07-09 on the final Task-A+B population (`Full_Schedules_excl.csv`, rebuild 20:47); v6 retained for history. Gate tally stays **22 PASS / 0 WARN / 0 FAIL**.
2. **Section 2 intro**: replace "Raking touches hom30 only, so activity (act30) is J3-native here. Aggregate activity JS = 0.0191 (gate ≤ 0.05)." with a post-Task-B statement (act30 jointly raked per stratum×slot×LFTAG since Task B, 2026-07-09) + the **freshly computed** aggregate JS from D2.
3. **Section 3 table**: the row "4.4 single-person 0.30-floor 1,413 HH → 1,118 HH" — the exclusion count changed after the rebuild (A6d logged 1,198 HHs / 0.42% on the Task-A rebuild; confirm the final R5 value from the logs or the `_excl` artifacts). Update the number and, if the `--excl` population row count changed, every occurrence of the stale count (v6 carries **285,419** in Section 8 — re-derive the final value; do a global grep for `285,419` and `1,118`).
4. **Section 7 caption + 2030 gate table** (OD-2, resolved as *verify-don't-assume*): check WD 78.44 / Sat 79.15 / Sun 81.48 and gates 5.1–5.5 values against the final Step-6 validator output (R6). Update if different; leave if identical; say which in the Progress Log.
5. **Section 8 dataset statistics + BEM Readiness table**: v6 still shows 144,507 HH / 6,936,336 rows / WE-2022 0.749. The post-rebuild values logged at A6e/A6f are **144,428 HH / 6,932,544 rows / Occupancy 2022 WD 0.703 / WE 0.745; 2030 WD 0.785 / WE 0.803** — confirm against the final R5 rebuild logs (not the Task-A-only ones) and update the table. Also re-check "Calibrated synthetic diary-days 128,316" and the linked-population count.
6. Anywhere else a grep for the known-stale tokens (`0.0191`, `J3-native here`, `144,507`, `6,936,336`, `285,419`, `1,118 HH`) still hits in v7 — fix or justify in the Progress Log.

### D4 — Run
`py _gen_v7_plots.py` from `outputs_step4/`. Expect the same runtime class as the v5 render (it did complete locally before). If `MemoryError`: fall back to chunked accumulation per chart (accumulate slot×category counts chunk-wise, then plot) — do not reduce the data.

### D5 — Verification (all mandatory)
1. **Spot re-derivation (independent of the plotting code):** with a small chunked script over `Full_Schedules_excl.csv` (synthetic rows only): (a) weekday % of slots in Paid work — must match the new Section-2/7 figures and sit close to the observed 13.3% (Task B raked it); (b) one LFTAG paid-work level vs the new Section-6 figure; (c) the 2005 weekday Work-by-Stratum bar — must have **risen** vs the old ~22% (residual gap vs other cycles is allowed: the 15.76% linkage ceiling improves, not perfects, composition).
2. **Expected visual deltas** (open v7 in a browser): Section-2 weekday Paid-work bars converge; Section-6 levels converge with ordering (Employed ≫ NILF) preserved; Section-7 2005 bar rises. **Section 3 (AT_HOME Daily Rhythm) must look unchanged** — the hom30 rake is the same; a visible AT_HOME change means you loaded the wrong file: stop and investigate.
3. **Idempotency:** run `_gen_v7_plots.py` a second time → `0 replaced, 7 skipped-present`.
4. **Integrity:** v7 opens offline in a plain browser, all `<img>` are base64 data-URIs, no external requests, no layout break; the three Task-C figures are still present and untouched; `sha256` of v5 and v6 identical to the D1 values.

### D6 — Rollback statement
Nothing to roll back: v5/v6 untouched, v7 and `_gen_v7_plots.py` are new files. If v7 is unsatisfactory, delete both.

### D7 — Do-NOT-touch list
- Any file under `0_Occupancy/` or `aug_pipeline/` (read-only inputs).
- `augmented_diaries.csv` (530 MB — not needed at all for this task).
- `_gen_v5_plots.py`, `_gen_v6_plots.py`, `04F_validation.py`, all pipeline scripts (import/read only; if you believe an edit is required, that is a deviation — log it, don't do it).
- v5/v6 HTML, everything in `previous/` and `archive/`.

### D8 — Progress Log entries (append-only, dated 2026-07-09 or actual date)
1. `outputs_step4/step4_improvement_notes.md` → Improvement 4's Progress Log + flip its Index row and Status to DONE (only if all of D5 passed).
2. `improvement_planning/step4_improvements_implementation.md` → tick the Task D checklist items in "Live progress checklist" + append a dated entry to the main Progress Log: what was replaced, the fresh aggregate JS, every prose/table value changed (old → new, with source: re-derived vs R-log), the D5 spot-check numbers, sha256 confirmation, any deviation.
3. `improvement_planning/step4_improvements_confirmation.md` → one-line append under its Progress Log: Task D executed, v7 delivered, verdict outcome.

## Acceptance criteria (the manager will check these)
- [ ] `step4_validation_report_v7.html` exists; opens offline; 7 section charts re-rendered on the 20:47 `_excl` population; 3 Task-C figures untouched.
- [ ] No stale tokens left unjustified (`0.0191`, `J3-native here`, `144,507`, `6,936,336`, `285,419`, `1,118 HH`).
- [ ] Section 3 chart visually unchanged; Sections 2/6/7 show the post-Task-B convergence; 2005 Section-7 bar risen.
- [ ] D5.1 spot values re-derived independently and matching the figures.
- [ ] v5/v6 sha256 unchanged; idempotent second run.
- [ ] All three Progress Logs appended; deviations (if any) explicitly flagged.
