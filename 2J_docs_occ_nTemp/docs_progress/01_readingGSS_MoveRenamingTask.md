# Task: Move Column Renaming from Step 2 → Step 1

**Goal:** Both validation reports (`step1_validation_report.html` and
`step2_validation_report.html`) should show the same unified column names
(`SEX`, `MARSTH`, `AGEGRP`, etc.) instead of raw GSS names.

---

## 1. Modify `01_readingGSS.py`

- [ ] Copy `MAIN_RENAME_MAP` (per-cycle dicts) from `02_harmonizeGSS.py` into
      `01_readingGSS.py`, placed after the `MAIN_COLS_*` constants.
- [ ] Copy `EPISODE_RENAME_MAP` similarly.
- [ ] Add helper function `apply_rename_map(df, cycle, rename_map)` that calls
      `df.rename(columns=rename_map.get(cycle, {}))`.
- [ ] In `read_gss_main()`, call `apply_rename_map()` on the returned DataFrame
      before returning (one line per cycle branch, or after the final return).
- [ ] In `read_gss_episode()`, same — call `apply_rename_map()` before returning.

## 2. Modify `02_harmonizeGSS.py`

- [ ] Remove `MAIN_RENAME_MAP` constant (lines 17–90).
- [ ] Remove `EPISODE_RENAME_MAP` constant (lines 92–114).
- [ ] In `harmonize_main()`: remove the `rename_dict = ...` + `df.rename(...)` lines
      (columns are already renamed by Step 1).
- [ ] In `harmonize_episode()`: same — remove the `rename_dict` + `df.rename()` lines.
- [ ] Verify all `recode_*` functions still reference the correct unified column names
      (they already do — no logic changes needed).

## 3. Modify `01_readingGSS_val.py`

- [ ] Update `DEMO_VARS` dictionary: replace per-cycle raw column names with the
      unified names (same name for all cycles, e.g., `"2005": "SEX"` instead of
      `"2005": "sex"`).
  - `Sex / Gender` → all cycles: `SEX`
  - `Marital Status` → all cycles: `MARSTH`
  - `Province / Region` → all cycles: `PR`
  - `Labour Force Activity` → all cycles: `LFTAG`
  - `Employment Type (COW)` → all cycles: `COW`
  - `Hours Worked` → all cycles: `HRSWRK`
  - `Language at Home` → all cycles: `KOL`
  - `Commute Mode` → all cycles: `MODE` (keep `None` for 2005; remove `__CTW_*__`
    sentinel logic since Step 1 now derives and stores `MODE` directly)
  - `Age Group`, `Household Size`, `Urban / Rural (CMA)` keys already use the same
    raw name across cycles — confirm no change needed.
- [ ] Update `EXPECTED_MAIN_COLS` to reference unified column names (or derive from the
      new `MAIN_RENAME_MAP` imported from `01_readingGSS.py`).
- [ ] Remove or simplify `_derive_commute_mode()` helper and `__CTW_*__` sentinel
      logic in `compare_categories()` and `_plot_demo_frequencies()` — no longer needed
      once `MODE` is available directly in Step 1 output.

## 4. Modify `02_harmonizeGSS_val.py`

- [ ] Update `STEP1_SEX_COL` (line 51): change all cycle entries to `"SEX"` since
      Step 1 now outputs the unified name for all cycles.
  ```python
  STEP1_SEX_COL = {2005: "SEX", 2010: "SEX", 2015: "SEX", 2022: "SEX"}
  ```
- [ ] Confirm `method9_regression()` NaN comparison still works correctly with the
      updated column name (no other changes expected).

## 5. Re-run Step 1 and Verify Output CSVs

- [ ] Run `python 01_readingGSS.py` from `2J_docs_occ_nTemp/`.
- [ ] Spot-check `outputs_step1/main_2005.csv` columns — confirm `SEX` (not `sex`),
      `MARSTH` (not `marstat`), `PR` (not `REGION`), etc.
- [ ] Confirm `step1_validation_report.html` is regenerated without errors.

## 6. Re-run Step 2 and Verify Output CSVs

- [ ] Run `python 02_harmonizeGSS.py` from `2J_docs_occ_nTemp/`.
- [ ] Confirm `outputs_step2/main_*.csv` row counts match Step 1 outputs (preserved).
- [ ] Confirm `step2_validation_report.html` is regenerated without errors.

## 7. Manual Validation — Compare Both Reports

- [ ] Open `outputs_step1/step1_validation_report.html` in browser.
- [ ] Open `outputs_step2/step2_validation_report.html` in browser.
- [ ] Confirm Chart 3 (Step 1) and Chart 4 (Step 2) row labels are now consistent.
- [ ] Confirm no new failures or regressions appear in either report's scorecard.

## 8. Update Documentation to Reflect Renaming Moved to Step 1

### `00_GSS_Occupancy_Documentation.md`

- [ ] **Step 1A table** — add a `Renamed To` column note clarifying that renaming
      now happens at read time in Step 1 (not Step 2). No content changes needed;
      just confirm the table already lists unified target names.
- [ ] **Step 2 header / preamble** — remove or update any reference to
      *"Column renames → unified schema"* as a Step 2 action (e.g., in section
      `2B. Harmonization Procedure`, step 2: *"Rename columns to unified schema (see
      Step 1 naming)"*) → change to reflect that renaming is already done after Step 1.
- [ ] **Step 2B procedure list** — update step 2 of the procedure block from
      *"Rename columns to unified schema"* to something like
      *"Columns already renamed to unified schema by Step 1 — verify schema before
      recoding."*

### `00_GSS_Occupancy_Pipeline_Overview.md`

- [ ] **Step 1 box** — add *"Column renames → unified schema"* to the Step 1 block
      (currently listed under Step 2).
- [ ] **Step 2 box** — remove *"Column renames → unified schema"* from the Step 2
      box (line 45 in the ASCII art block), since it now belongs to Step 1.
- [ ] **Key Design Decisions table** (if present) — add or update a row noting that
      *renaming is applied at read time in Step 1* to keep Step 2 focused purely on
      category recoding and harmonization logic.
