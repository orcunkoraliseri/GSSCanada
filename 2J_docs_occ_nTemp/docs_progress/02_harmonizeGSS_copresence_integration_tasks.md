, can yo# Co-Presence Integration — Task List

**Implementation plan:** `docs_debug/copresence_integration_plan.md`
**Files to modify:** `02_harmonizeGSS.py`, `03_mergingGSS.py`, `02_harmonizeGSS_val.py`, `03_mergingGSS_val.py`, `01_readingGSS_val.py`
**Working directory:** `2J_docs_occ_nTemp/`

---

## Background (read before implementing)

The pipeline already selects all raw co-presence columns in Step 1 and the 8 unified columns (`Alone`, `Spouse`, `Children`, `parents`, `otherInFAMs`, `otherHHs`, `friends`, `others`) do reach the merged output. The problem is that **5 additional raw columns are silently dropped** in `harmonize_copresence()` instead of being merged into the unified schema:

| Dropped column | Cycle | Concept | Proposed fix |
|---|---|---|---|
| `NHSDCL15` | 2005, 2010 | Children of respondent outside HH, < 15 yrs | OR-merge into `Children` |
| `NHSDC15P` | 2005, 2010 | Children of respondent outside HH, ≥ 15 yrs | OR-merge into `otherInFAMs` |
| `NHSDPAR`  | 2005, 2010 | Parents / parents-in-law outside HH | OR-merge into `parents` |
| `TUI_06F`  | 2015, 2022 | Other household adult(s) | OR-merge into `otherInFAMs` |
| `TUI_06I`  | 2015, 2022 | Colleague(s) / classmate(s) | New `colleagues` column (NaN for 2005/2010) |

**OR-merge rule for binary 1/2/NaN columns:**
- Result = `1` if ANY source column equals `1`
- Result = `2` if NO source equals `1` and AT LEAST ONE equals `2`
- Result = `NaN` if ALL sources are `NaN`

**Final unified schema (9 columns):**
`Alone`, `Spouse`, `Children`, `parents`, `otherInFAMs`, `otherHHs`, `friends`, `others`, `colleagues`

All validation files use:
- `matplotlib` + `seaborn` for plots
- `_b64(fig)` helper to convert figures to base64 PNG strings
- `self.plots_b64["key"] = _b64(fig)` to store plots
- `self._rec("pass"/"fail"/"warn", message)` to record check results

---

## Task List

Tasks must be done in order within each group. Groups can be parallelized where noted.

---

### GROUP 0 — Verify current state (do first, unblocks Group 1)

---

**Task #1 — Confirm which raw co-presence columns exist in Step 1 outputs**

Run the following diagnostic in a Python session (or as a quick script) from `2J_docs_occ_nTemp/`:

```python
import pandas as pd

RAW_COPRE = {
    2005: ["ALONE", "SPOUSE", "CHILDHSD", "FRIENDS", "OTHFAM", "OTHERS",
           "PARHSD", "MEMBHSD", "NHSDCL15", "NHSDC15P", "NHSDPAR"],
    2010: ["ALONE", "SPOUSE", "CHILDHSD", "FRIENDS", "OTHFAM", "OTHERS",
           "PARHSD", "MEMBHSD", "NHSDCL15", "NHSDC15P", "NHSDPAR"],
    2015: ["TUI_06A", "TUI_06B", "TUI_06C", "TUI_06D", "TUI_06E", "TUI_06F",
           "TUI_06G", "TUI_06H", "TUI_06I", "TUI_06J"],
    2022: ["TUI_06A", "TUI_06B", "TUI_06C", "TUI_06D", "TUI_06E", "TUI_06F",
           "TUI_06G", "TUI_06H", "TUI_06I", "TUI_06J"],
}

for cycle, expected_cols in RAW_COPRE.items():
    df = pd.read_csv(f"outputs_step1/episode_{cycle}.csv", low_memory=False, nrows=5)
    present = [c for c in expected_cols if c in df.columns]
    missing = [c for c in expected_cols if c not in df.columns]
    print(f"\n{cycle}: present={present}")
    if missing:
        print(f"  ⚠ MISSING: {missing}")
```

**Expected result:** All columns listed above should be present for each cycle.
**If any column is missing:** Add it to the corresponding `EPISODE_COLS_*` list in `01_readingGSS.py` and re-run Step 1 before continuing.

---

### GROUP 1 — `02_harmonizeGSS.py` — Core logic (Tasks #2–#3, sequential)

---

**Task #2 — Add `or_merge_copresence()` helper function**

In `02_harmonizeGSS.py`, find the line:
```python
def harmonize_copresence(df: pd.DataFrame, cycle: int) -> pd.DataFrame:
```

Insert the following **new function immediately before it** (do not replace `harmonize_copresence` yet):

```python
def or_merge_copresence(
    df: pd.DataFrame, target_col: str, source_cols: list[str]
) -> pd.DataFrame:
    """OR-merge binary (1/2/NaN) source columns into target_col.

    Rules:
        result = 1   if any source == 1                  (person was present)
        result = 2   if no source == 1, at least one == 2 (person was absent)
        result = NaN if all sources are NaN               (not measured)

    Operates in-place on target_col; drops no columns itself.

    Args:
        df:          Episode DataFrame for one cycle.
        target_col:  Name of the unified column to write the result into.
        source_cols: List of column names to OR-merge (may include target_col itself).

    Returns:
        df with target_col updated.
    """
    available = [c for c in source_cols if c in df.columns]
    if not available:
        return df
    any_present = (df[available] == 1).any(axis=1)
    any_absent  = (df[available] == 2).any(axis=1)
    result = pd.Series(pd.NA, index=df.index, dtype="Int8")
    result[any_present]            = 1
    result[~any_present & any_absent] = 2
    df[target_col] = result
    return df

```

---

**Task #3 — Rewrite `harmonize_copresence()` body**

In `02_harmonizeGSS.py`, **replace the entire existing `harmonize_copresence` function** (lines 454–468, the full function including def line) with the following:

```python
def harmonize_copresence(df: pd.DataFrame, cycle: int) -> pd.DataFrame:
    """Rename, OR-merge, and clean all co-presence columns.

    Steps:
        A. Standardize missing codes (7/8/9 → NaN) on ALL raw co-presence
           columns (both mapped and unmapped) before any renaming.
        B. Rename primary columns to unified names via COPRESENCE_MAP.
        C. OR-merge unmapped columns into existing unified targets.
        D. Add `colleagues` column (TUI_06I for 2015/2022; NaN for 2005/2010).
        E. Drop all residual raw co-presence columns.

    Produces 9 unified columns:
        Alone, Spouse, Children, parents, otherInFAMs, otherHHs,
        friends, others, colleagues
    """
    rename_map = COPRESENCE_MAP.get(cycle, {})

    # Step A: Standardize missing codes on raw columns before rename
    extra_raw = (
        ["NHSDCL15", "NHSDC15P", "NHSDPAR"] if cycle in (2005, 2010)
        else ["TUI_06F", "TUI_06I"]
    )
    for col in list(rename_map.keys()) + extra_raw:
        if col in df.columns:
            df[col] = df[col].replace({7: pd.NA, 8: pd.NA, 9: pd.NA})

    # Step B: Rename primary columns to unified names
    df = df.rename(columns=rename_map)

    # Step C: OR-merge unmapped columns into unified targets
    if cycle in (2005, 2010):
        # NHSDCL15: children outside HH <15 → merge into Children
        df = or_merge_copresence(df, "Children",    ["Children",    "NHSDCL15"])
        # NHSDPAR:  parents outside HH   → merge into parents
        df = or_merge_copresence(df, "parents",     ["parents",     "NHSDPAR"])
        # NHSDC15P: children outside HH ≥15 → merge into otherInFAMs
        df = or_merge_copresence(df, "otherInFAMs", ["otherInFAMs", "NHSDC15P"])
        # No equivalent for colleagues in 2005/2010
        df["colleagues"] = pd.NA

    else:  # 2015, 2022
        # TUI_06F: other HH adults → merge into otherInFAMs (alongside TUI_06D→otherInFAMs)
        df = or_merge_copresence(df, "otherInFAMs", ["otherInFAMs", "TUI_06F"])
        # TUI_06I: colleagues/classmates → new unified column
        df["colleagues"] = df["TUI_06I"].copy() if "TUI_06I" in df.columns else pd.NA

    # Step D: Drop residual raw co-presence columns
    raw_to_drop = [
        c for c in df.columns
        if c in {"NHSDCL15", "NHSDC15P", "NHSDPAR", "TUI_06F", "TUI_06I"}
    ]
    df = df.drop(columns=raw_to_drop, errors="ignore")

    return df
```

---

### GROUP 2 — `03_mergingGSS.py` — Add `colleagues` to column list

---

**Task #4 — Add `"colleagues"` to `EPISODE_COMMON_COLS`**

In `03_mergingGSS.py`, find the `EPISODE_COMMON_COLS` list (around line 64). Find this block:

```python
    # Co-presence
    "Alone",
    "Spouse",
    "Children",
    "parents",
    "otherInFAMs",
    "otherHHs",
    "friends",
    "others",
```

Replace it with:

```python
    # Co-presence
    "Alone",
    "Spouse",
    "Children",
    "parents",
    "otherInFAMs",
    "otherHHs",
    "friends",
    "others",
    "colleagues",    # TUI_06I (2015/2022 only) → NaN for 2005/2010
```

No other changes to `03_mergingGSS.py` are needed. `standardize_columns()` already handles missing columns by filling `pd.NA`.

---

### GROUP 3 — `02_harmonizeGSS_val.py` — Co-presence validation method (Tasks #5–#9, sequential)

---

**Task #5 — Add `COPRE_COLS` constant near top of file**

In `02_harmonizeGSS_val.py`, find the line:
```python
CYCLES = [2005, 2010, 2015, 2022]
```

Add the following constant **directly below it**:

```python
COPRE_COLS = [
    "Alone", "Spouse", "Children", "parents",
    "otherInFAMs", "otherHHs", "friends", "others", "colleagues",
]
```

---

**Task #6 — Add `method10_copresence()` to `GSSHarmonizationValidator` — Plot 1 (prevalence bar)**

In `02_harmonizeGSS_val.py`, find `def export_html(self)` (around line 748). Insert the following new method **immediately before `export_html`**:

```python
    # --------------------------------------------------------------- Method 10
    def method10_copresence(self) -> None:
        """Co-Presence Quality Report — 4 charts."""
        print("\n--- Method 10: Co-Presence Quality Report ---")
        _apply_dark()

        # --- Plot 1: Weighted prevalence grouped bar -------------------------
        fig, ax = plt.subplots(figsize=(13, 5))
        x = np.arange(len(COPRE_COLS))
        width = 0.18
        for i, c in enumerate(CYCLES):
            df = self.epi_s2[c]
            rates = []
            for col in COPRE_COLS:
                if col in df.columns:
                    valid_mask = df[col].notna()
                    total_valid = valid_mask.sum()
                    rate = 100.0 * (df.loc[valid_mask, col] == 1).sum() / total_valid if total_valid else 0.0
                else:
                    rate = 0.0
                rates.append(rate)
            ax.bar(
                x + (i - 1.5) * width, rates, width,
                label=str(c), color=CYCLE_COLORS[i], edgecolor="#1e1e2e", linewidth=0.5
            )
        ax.set_xticks(x)
        ax.set_xticklabels(COPRE_COLS, rotation=30, ha="right", fontsize=9)
        ax.set_ylabel("% of non-NaN episodes with presence = 1")
        ax.set_ylim(0, 100)
        ax.legend(title="Cycle", fontsize=9)
        ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        ax.set_title(
            "Co-Presence Prevalence by Category and Cycle\n"
            "(weighted by episode count; NaN excluded from denominator)",
            fontsize=12,
        )
        self.plots_b64["10a_copre_prevalence"] = _b64(fig)

        # Record pass/fail for Alone column plausibility (expect 10–60% present)
        for c in CYCLES:
            df = self.epi_s2[c]
            if "Alone" not in df.columns:
                self._rec("fail", f"{c} — 'Alone' column missing from Step 2 episode file.")
                continue
            valid = df["Alone"].dropna()
            alone_pct = 100.0 * (valid == 1).mean()
            level = "pass" if 10 <= alone_pct <= 60 else "warn"
            self._rec(level, f"{c} — Alone prevalence: {alone_pct:.1f}% (expected 10–60%)")
```

---

**Task #7 — Extend `method10_copresence()` — Plot 2 (missing rate heatmap)**

Directly inside `method10_copresence()`, **after** the line `self.plots_b64["10a_copre_prevalence"] = _b64(fig)`, add:

```python
        # --- Plot 2: Missing rate heatmap -----------------------------------
        nan_matrix = []
        for col in COPRE_COLS:
            row = []
            for c in CYCLES:
                df = self.epi_s2[c]
                pct_nan = 100.0 * df[col].isna().mean() if col in df.columns else 100.0
                row.append(pct_nan)
            nan_matrix.append(row)
        arr = np.array(nan_matrix)

        fig2, ax2 = plt.subplots(figsize=(8, 5))
        im = ax2.imshow(arr, aspect="auto", cmap="YlOrRd", vmin=0, vmax=100)
        ax2.set_xticks(range(len(CYCLES)))
        ax2.set_xticklabels([str(c) for c in CYCLES])
        ax2.set_yticks(range(len(COPRE_COLS)))
        ax2.set_yticklabels(COPRE_COLS, fontsize=9)
        for i in range(len(COPRE_COLS)):
            for j in range(len(CYCLES)):
                ax2.text(j, i, f"{arr[i, j]:.1f}%", ha="center", va="center", fontsize=8,
                         color="black" if arr[i, j] < 60 else "white")
        plt.colorbar(im, ax=ax2, label="% NaN")
        ax2.set_title("Co-Presence Missing Rate (% NaN) per Column × Cycle\n"
                      "(`colleagues` should be 100% NaN for 2005/2010)", fontsize=11)
        self.plots_b64["10b_copre_missing"] = _b64(fig2)

        # Record pass/fail: colleagues must be 100% NaN for 2005/2010
        for c in (2005, 2010):
            df = self.epi_s2[c]
            if "colleagues" in df.columns:
                all_nan = df["colleagues"].isna().all()
                level = "pass" if all_nan else "fail"
                self._rec(level, f"{c} — colleagues column all-NaN: {all_nan}")
            else:
                self._rec("warn", f"{c} — colleagues column absent from Step 2 output (expected).")
```

---

**Task #8 — Extend `method10_copresence()` — Plot 3 (Alone vs. With Someone)**

Inside `method10_copresence()`, after the line `self.plots_b64["10b_copre_missing"] = _b64(fig2)`, add:

```python
        # --- Plot 3: Alone vs. With Someone per cycle -----------------------
        fig3, ax3 = plt.subplots(figsize=(8, 4))
        x3 = np.arange(len(CYCLES))
        width3 = 0.35
        alone_rates = []
        social_rates = []
        for c in CYCLES:
            df = self.epi_s2[c]
            if "Alone" in df.columns:
                valid = df["Alone"].dropna()
                alone_rates.append(100.0 * (valid == 1).mean())
                social_rates.append(100.0 * (valid == 2).mean())
            else:
                alone_rates.append(0.0)
                social_rates.append(0.0)
        ax3.bar(x3 - width3 / 2, alone_rates,  width3, label="Alone (=1)",         color="#f38ba8", edgecolor="#1e1e2e")
        ax3.bar(x3 + width3 / 2, social_rates, width3, label="With someone (=2)",  color="#89b4fa", edgecolor="#1e1e2e")
        ax3.set_xticks(x3)
        ax3.set_xticklabels([str(c) for c in CYCLES])
        ax3.set_ylabel("% of non-NaN episodes")
        ax3.set_ylim(0, 100)
        ax3.set_title("Alone vs. With Someone per Cycle (NaN excluded)", fontsize=12)
        ax3.legend()
        ax3.yaxis.grid(True, linestyle="--", alpha=0.3)
        for bar, val in zip(ax3.patches, alone_rates + social_rates):
            ax3.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                     f"{val:.1f}%", ha="center", fontsize=8)
        self.plots_b64["10c_copre_alone"] = _b64(fig3)
```

---

**Task #9 — Extend `method10_copresence()` — Plot 4 (colleagues coverage)**

Inside `method10_copresence()`, after the line `self.plots_b64["10c_copre_alone"] = _b64(fig3)`, add:

```python
        # --- Plot 4: colleagues column coverage per cycle -------------------
        fig4, ax4 = plt.subplots(figsize=(8, 4))
        x4 = np.arange(len(CYCLES))
        width4 = 0.25
        yes_rates, no_rates, nan_rates = [], [], []
        for c in CYCLES:
            df = self.epi_s2[c]
            if "colleagues" in df.columns:
                total = len(df)
                yes_rates.append(100.0 * (df["colleagues"] == 1).sum() / total)
                no_rates.append(100.0 * (df["colleagues"] == 2).sum() / total)
                nan_rates.append(100.0 * df["colleagues"].isna().mean())
            else:
                yes_rates.append(0.0); no_rates.append(0.0); nan_rates.append(100.0)
        ax4.bar(x4 - width4, yes_rates, width4, label="Present (=1)",  color="#a6e3a1", edgecolor="#1e1e2e")
        ax4.bar(x4,           no_rates,  width4, label="Absent (=2)",   color="#89b4fa", edgecolor="#1e1e2e")
        ax4.bar(x4 + width4, nan_rates,  width4, label="NaN (missing)", color="#585b70", edgecolor="#1e1e2e")
        ax4.set_xticks(x4)
        ax4.set_xticklabels([str(c) for c in CYCLES])
        ax4.set_ylabel("% of all episodes")
        ax4.set_ylim(0, 110)
        ax4.set_title(
            "colleagues Column Coverage per Cycle\n"
            "(expect ~100% NaN for 2005/2010; mix of 1/2/NaN for 2015/2022)",
            fontsize=11,
        )
        ax4.legend()
        ax4.yaxis.grid(True, linestyle="--", alpha=0.3)
        self.plots_b64["10d_copre_colleagues"] = _b64(fig4)
        print("  [DONE] Method 10 complete — 4 co-presence charts generated.")
```

---

**Task #10 — Register `method10_copresence()` in `run_all()`**

In `02_harmonizeGSS_val.py`, find:
```python
    def run_all(self) -> None:
        """Execute all 9 validation methods and export HTML."""
        _apply_dark()
        print("=== Step 2 Harmonization Validation ===\n")
        self.method1_schema()
        self.method2_rowcounts()
        self.method3_sentinels()
        self.method4_categories()
        self.method5_activity()
        self.method6_location()
        self.method7_metadata()
        self.method8_diary()
        self.method9_regression()
        self.export_html()
```

Replace with:
```python
    def run_all(self) -> None:
        """Execute all 10 validation methods and export HTML."""
        _apply_dark()
        print("=== Step 2 Harmonization Validation ===\n")
        self.method1_schema()
        self.method2_rowcounts()
        self.method3_sentinels()
        self.method4_categories()
        self.method5_activity()
        self.method6_location()
        self.method7_metadata()
        self.method8_diary()
        self.method9_regression()
        self.method10_copresence()
        self.export_html()
```

---

**Task #11 — Register the 4 new charts in `export_html()`**

In `02_harmonizeGSS_val.py`, find `chart_titles: dict[str, str] = {` inside `export_html()`. Find this block:

```python
        chart_titles: dict[str, str] = {
            "4_categories": "Chart 4 — Demographic Category Distributions (all vars × 4 cycles)",
            "5_activity": "Chart 5 — Activity Code Crosswalk Heatmap (14 categories × 4 cycles)",
            "6_location": "Chart 6 — AT_HOME Rate per Cycle",
            "8_diary": "Chart 8 — Diary Closure Pass Rate & Episode Distribution",
            "9a_weights": "Chart 9a — Survey Weight: Step 1 vs Step 2 Box Plots",
            "9b_nan_heatmap": "Chart 9b — NaN % per Harmonized Column (Regression Check)",
        }
```

Replace with:
```python
        chart_titles: dict[str, str] = {
            "4_categories":        "Chart 4 — Demographic Category Distributions (all vars × 4 cycles)",
            "5_activity":          "Chart 5 — Activity Code Crosswalk Heatmap (14 categories × 4 cycles)",
            "6_location":          "Chart 6 — AT_HOME Rate per Cycle",
            "8_diary":             "Chart 8 — Diary Closure Pass Rate & Episode Distribution",
            "9a_weights":          "Chart 9a — Survey Weight: Step 1 vs Step 2 Box Plots",
            "9b_nan_heatmap":      "Chart 9b — NaN % per Harmonized Column (Regression Check)",
            "10a_copre_prevalence":"Chart 10a — Co-Presence Prevalence by Category and Cycle",
            "10b_copre_missing":   "Chart 10b — Co-Presence Missing Rate Heatmap",
            "10c_copre_alone":     "Chart 10c — Alone vs. With Someone per Cycle",
            "10d_copre_colleagues":"Chart 10d — colleagues Column Coverage per Cycle",
        }
```

---

### GROUP 4 — `03_mergingGSS_val.py` — Co-presence validation (Tasks #12–#16, sequential)

---

**Task #12 — Add `COPRE_COLS` constant near top of `03_mergingGSS_val.py`**

In `03_mergingGSS_val.py`, find the line:
```python
CYCLES = [2005, 2010, 2015, 2022]
```

Add the following constant **directly below it**:

```python
COPRE_COLS = [
    "Alone", "Spouse", "Children", "parents",
    "otherInFAMs", "otherHHs", "friends", "others", "colleagues",
]
```

---

**Task #13 — Add `validate_copresence()` to `GSSMergeValidator` — Plots 6a & 6b**

In `03_mergingGSS_val.py`, find `def build_html_report(self) -> str:` (around line 1302). Insert the following new method **immediately before it**:

```python
    def validate_copresence(self) -> None:
        """Section 6 — Co-Presence Completeness and Prevalence in Merged Dataset."""
        print("\n--- Section 6: Co-Presence Validation ---")

        df = self.merged  # full merged_episodes DataFrame

        # --- Plot 6a: Completeness heatmap (% non-NaN per column × cycle) ---
        completeness_matrix = []
        for col in COPRE_COLS:
            row = []
            for c in CYCLES:
                sub = df[df["CYCLE_YEAR"] == c]
                pct_filled = 100.0 * sub[col].notna().mean() if col in df.columns else 0.0
                row.append(pct_filled)
            completeness_matrix.append(row)
        arr6a = np.array(completeness_matrix)

        fig6a, ax6a = plt.subplots(figsize=(8, 5))
        im6a = ax6a.imshow(arr6a, aspect="auto", cmap="YlGn", vmin=0, vmax=100)
        ax6a.set_xticks(range(len(CYCLES)))
        ax6a.set_xticklabels([str(c) for c in CYCLES])
        ax6a.set_yticks(range(len(COPRE_COLS)))
        ax6a.set_yticklabels(COPRE_COLS, fontsize=9)
        for i in range(len(COPRE_COLS)):
            for j in range(len(CYCLES)):
                ax6a.text(j, i, f"{arr6a[i, j]:.1f}%", ha="center", va="center", fontsize=8,
                          color="black" if arr6a[i, j] > 30 else "white")
        plt.colorbar(im6a, ax=ax6a, label="% non-NaN")
        ax6a.set_title(
            "Co-Presence Column Completeness in Merged Dataset\n"
            "(`colleagues` should be ~0% filled for 2005/2010)",
            fontsize=11,
        )
        self.plots_b64["6a_copre_completeness"] = _b64(fig6a)

        # Check: all 8 primary co-presence columns must have >50% fill for each cycle
        for col in COPRE_COLS[:-1]:  # exclude colleagues
            for c in CYCLES:
                sub = df[df["CYCLE_YEAR"] == c]
                if col not in df.columns:
                    self._rec("fail", f"Merged dataset missing co-presence column '{col}'")
                    continue
                fill = 100.0 * sub[col].notna().mean()
                level = "pass" if fill > 50 else "warn"
                self._rec(level, f"{c} '{col}' fill: {fill:.1f}%")

        # --- Plot 6b: Weighted prevalence grouped bar -----------------------
        fig6b, ax6b = plt.subplots(figsize=(13, 5))
        x = np.arange(len(COPRE_COLS))
        width = 0.18
        CYCLE_COLORS = ["#89b4fa", "#f38ba8", "#fab387", "#a6e3a1"]
        for i, c in enumerate(CYCLES):
            sub = df[df["CYCLE_YEAR"] == c].copy()
            rates = []
            for col in COPRE_COLS:
                if col not in sub.columns:
                    rates.append(0.0)
                    continue
                valid_mask = sub[col].notna()
                total = valid_mask.sum()
                rate = 100.0 * (sub.loc[valid_mask, col] == 1).sum() / total if total else 0.0
                rates.append(rate)
            ax6b.bar(
                x + (i - 1.5) * width, rates, width,
                label=str(c), color=CYCLE_COLORS[i], edgecolor="#1e1e2e", linewidth=0.5,
            )
        ax6b.set_xticks(x)
        ax6b.set_xticklabels(COPRE_COLS, rotation=30, ha="right", fontsize=9)
        ax6b.set_ylabel("% of non-NaN episodes with presence = 1")
        ax6b.set_ylim(0, 100)
        ax6b.legend(title="Cycle", fontsize=9)
        ax6b.yaxis.grid(True, linestyle="--", alpha=0.3)
        ax6b.set_title(
            "Co-Presence Prevalence by Category and Cycle — Merged Dataset",
            fontsize=12,
        )
        self.plots_b64["6b_copre_prevalence"] = _b64(fig6b)
```

---

**Task #14 — Extend `validate_copresence()` — Plot 6c (Alone by hour of day)**

Directly inside `validate_copresence()`, after the line `self.plots_b64["6b_copre_prevalence"] = _b64(fig6b)`, add:

```python
        # --- Plot 6c: Alone rate by hour of day per cycle -------------------
        if "HOUR_OF_DAY" in df.columns and "Alone" in df.columns:
            fig6c, ax6c = plt.subplots(figsize=(12, 5))
            CYCLE_COLORS = ["#89b4fa", "#f38ba8", "#fab387", "#a6e3a1"]
            for i, c in enumerate(CYCLES):
                sub = df[(df["CYCLE_YEAR"] == c) & df["Alone"].notna()].copy()
                hourly = sub.groupby("HOUR_OF_DAY").apply(
                    lambda g: 100.0 * (g["Alone"] == 1).mean()
                )
                ax6c.plot(hourly.index, hourly.values, label=str(c),
                          color=CYCLE_COLORS[i], linewidth=2, marker="o", markersize=3)
            ax6c.set_xlabel("Hour of Day (0 = midnight, 4 = 4 AM diary start)")
            ax6c.set_ylabel("% of episodes where Alone = 1")
            ax6c.set_xticks(range(0, 24))
            ax6c.set_xlim(0, 23)
            ax6c.set_ylim(0, 100)
            ax6c.yaxis.grid(True, linestyle="--", alpha=0.3)
            ax6c.legend(title="Cycle")
            ax6c.set_title(
                "% Alone by Hour of Day per Cycle\n"
                "(expect high solo at night/early morning, low during work/social hours)",
                fontsize=11,
            )
            self.plots_b64["6c_copre_alone_hourly"] = _b64(fig6c)
        else:
            print("  [SKIP] HOUR_OF_DAY or Alone column not available — skipping Plot 6c.")
        print("  [DONE] Section 6 complete — co-presence charts generated.")
```

---

**Task #15 — Register `validate_copresence()` in the run sequence**

In `03_mergingGSS_val.py`, find the lines (around line 1556):
```python
        self.validate_row_counts()
        self.validate_merge_integrity()
        self.validate_derived_features()
        self.validate_hetus_slots()
        self.validate_cross_cycle_consistency()
```

Add `self.validate_copresence()` **after `validate_cross_cycle_consistency()`**, before the `validate_30min_downsampling()` call:

```python
        self.validate_row_counts()
        self.validate_merge_integrity()
        self.validate_derived_features()
        self.validate_hetus_slots()
        self.validate_cross_cycle_consistency()
        self.validate_copresence()
```

---

**Task #16 — Register the 3 new charts in `build_html_report()` `chart_sections` list**

In `03_mergingGSS_val.py`, find the `chart_sections` list inside `build_html_report()`. Find the last entry in it, which looks like:
```python
            ("7c_act_heatmap",
             "Section 7c — Activity Heatmap at 30-min Resolution"),
```

Add the following **after that last entry, before the closing `]`**:

```python
            ("6a_copre_completeness",
             "Section 6a — Co-Presence Column Completeness in Merged Dataset"),
            ("6b_copre_prevalence",
             "Section 6b — Co-Presence Prevalence by Category and Cycle"),
            ("6c_copre_alone_hourly",
             "Section 6c — Alone Rate by Hour of Day per Cycle"),
```

---

### GROUP 5 — `01_readingGSS_val.py` — Raw column coverage check (can run in parallel with Groups 3–4)

---

**Task #17 — Add raw co-presence column presence check**

In `01_readingGSS_val.py`, locate the validator class and find where the last validation method ends (before `export_html()` or the equivalent final export call). Add the following new method **before the export call**:

```python
    def check_raw_copresence_coverage(self) -> None:
        """Verify that all raw co-presence columns are present in Step 1 episode files."""
        print("\n--- Raw Co-Presence Column Coverage ---")

        RAW_COPRE_EXPECTED = {
            2005: ["ALONE", "SPOUSE", "CHILDHSD", "FRIENDS", "OTHFAM", "OTHERS",
                   "PARHSD", "MEMBHSD", "NHSDCL15", "NHSDC15P", "NHSDPAR"],
            2010: ["ALONE", "SPOUSE", "CHILDHSD", "FRIENDS", "OTHFAM", "OTHERS",
                   "PARHSD", "MEMBHSD", "NHSDCL15", "NHSDC15P", "NHSDPAR"],
            2015: ["TUI_06A", "TUI_06B", "TUI_06C", "TUI_06D", "TUI_06E",
                   "TUI_06F", "TUI_06G", "TUI_06H", "TUI_06I", "TUI_06J"],
            2022: ["TUI_06A", "TUI_06B", "TUI_06C", "TUI_06D", "TUI_06E",
                   "TUI_06F", "TUI_06G", "TUI_06H", "TUI_06I", "TUI_06J"],
        }

        for c in CYCLES:
            # Use whichever attribute name your class uses for step 1 episode DataFrames
            # Typically self.epi_s1[c] or self.episode[c] — check class __init__ to confirm
            df = self.epi_s1[c]
            expected = RAW_COPRE_EXPECTED[c]
            present = [col for col in expected if col in df.columns]
            missing = [col for col in expected if col not in df.columns]

            if not missing:
                self._rec("pass", f"{c} — All {len(expected)} raw co-presence columns present.")
            else:
                self._rec("fail", f"{c} — Missing raw co-presence columns: {missing}")
```

Also **add a call to this method** in the `run_all()` (or equivalent orchestration method) of the validator, alongside the other check methods.

**Important:** Check the `__init__` of the Step 1 validator class to confirm the attribute name for Step 1 episode DataFrames (may be `self.epi_s1`, `self.episode`, or similar). Use the correct attribute name in the method body above.

---

### GROUP 6 — Pipeline execution and acceptance verification (do last)

---

**Task #18 — Re-run Step 2 harmonization**

From `2J_docs_occ_nTemp/`:
```bash
python 02_harmonizeGSS.py
```

**Check the console output for each cycle. Confirm:**
- No `KeyError` or column-not-found warnings during `harmonize_copresence`
- Output line for each cycle shows shape with the extra `colleagues` column, e.g.:
  `[2005] Main: (19221, N), Epi: (M, 34+)`

---

**Task #19 — Re-run Step 3 merge**

From `2J_docs_occ_nTemp/`:
```bash
python 03_mergingGSS.py
```

**Check console output. Confirm:**
- `EPISODE_COMMON_COLS` loads cleanly for all 4 cycles
- No `standardize_columns` warnings for `colleagues` being absent (it will fill NaN for 2005/2010, which is expected behavior, but should not error)

---

**Task #20 — Acceptance checks (run as a quick Python script)**

From `2J_docs_occ_nTemp/`, run:

```python
import pandas as pd

COPRE_COLS = ["Alone", "Spouse", "Children", "parents",
              "otherInFAMs", "otherHHs", "friends", "others", "colleagues"]

print("=== ACCEPTANCE CHECKS ===\n")

# Check 1: colleagues column in step2 outputs
for cycle in [2005, 2010, 2015, 2022]:
    df = pd.read_csv(f"outputs_step2/episode_{cycle}.csv", low_memory=False)
    present = [c for c in COPRE_COLS if c in df.columns]
    missing = [c for c in COPRE_COLS if c not in df.columns]
    colg_all_nan = df["colleagues"].isna().all() if "colleagues" in df.columns else None
    print(f"[{cycle}] Step2 present={len(present)}/9  missing={missing}  colleagues_all_nan={colg_all_nan}")

print()

# Check 2: colleagues all-NaN for 2005/2010 in step2
for cycle in [2005, 2010]:
    df = pd.read_csv(f"outputs_step2/episode_{cycle}.csv", low_memory=False)
    ok = df["colleagues"].isna().all() if "colleagues" in df.columns else False
    print(f"[PASS] {cycle} colleagues all-NaN" if ok else f"[FAIL] {cycle} colleagues has unexpected values")

# Check 3: colleagues NOT all-NaN for 2015/2022
for cycle in [2015, 2022]:
    df = pd.read_csv(f"outputs_step2/episode_{cycle}.csv", low_memory=False)
    ok = df["colleagues"].notna().any() if "colleagues" in df.columns else False
    print(f"[PASS] {cycle} colleagues has values" if ok else f"[FAIL] {cycle} colleagues all-NaN or missing")

print()

# Check 4: OR-merge increased coverage for Children/parents/otherInFAMs in 2005/2010
# (compare against the old dropped columns: NHSDCL15 should have contributed to Children)
# This is a soft check — just verify Children fill > 0 in 2005/2010
for cycle in [2005, 2010]:
    df = pd.read_csv(f"outputs_step2/episode_{cycle}.csv", low_memory=False)
    for col in ["Children", "parents", "otherInFAMs"]:
        fill = df[col].notna().mean() if col in df.columns else 0
        print(f"[{cycle}] {col} fill: {fill*100:.1f}%")

print()

# Check 5: 9 co-presence columns in merged step3 output
merged = pd.read_csv("outputs_step3/merged_episodes.csv", low_memory=False)
for col in COPRE_COLS:
    present = col in merged.columns
    print(f"merged: '{col}' present={present}")
```

**All checks should pass before closing this task list.**

---

## Execution Order Summary

```
Task #1  (verify step1 outputs)
    │
    ├── GROUP 1: Tasks #2 → #3   (02_harmonizeGSS.py)
    │                │
    │                └── Task #18  (python 02_harmonizeGSS.py)
    │                        │
    │                        └── GROUP 2: Task #4  (03_mergingGSS.py)
    │                                        │
    │                                        └── Task #19  (python 03_mergingGSS.py)
    │
    ├── GROUP 3: Tasks #5 → #11  (02_harmonizeGSS_val.py)  [parallel with GROUP 4]
    │
    ├── GROUP 4: Tasks #12 → #16 (03_mergingGSS_val.py)    [parallel with GROUP 3]
    │
    ├── GROUP 5: Task #17        (01_readingGSS_val.py)     [parallel with GROUPs 3+4]
    │
    └── GROUP 6: Tasks #18 → #20 (pipeline re-run + acceptance checks)  [last]
```

---

## Quick Reference

| Task | File | What changes |
|---|---|---|
| #1  | — | Diagnostic only, no code change |
| #2  | `02_harmonizeGSS.py` | Add `or_merge_copresence()` helper before `harmonize_copresence` |
| #3  | `02_harmonizeGSS.py` | Replace body of `harmonize_copresence()` |
| #4  | `03_mergingGSS.py` | Add `"colleagues"` to `EPISODE_COMMON_COLS` |
| #5  | `02_harmonizeGSS_val.py` | Add `COPRE_COLS` constant |
| #6  | `02_harmonizeGSS_val.py` | Add `method10_copresence()` skeleton + Plot 1 |
| #7  | `02_harmonizeGSS_val.py` | Extend `method10_copresence()` + Plot 2 |
| #8  | `02_harmonizeGSS_val.py` | Extend `method10_copresence()` + Plot 3 |
| #9  | `02_harmonizeGSS_val.py` | Extend `method10_copresence()` + Plot 4 |
| #10 | `02_harmonizeGSS_val.py` | Register method in `run_all()` |
| #11 | `02_harmonizeGSS_val.py` | Register 4 chart keys in `export_html()` |
| #12 | `03_mergingGSS_val.py` | Add `COPRE_COLS` constant |
| #13 | `03_mergingGSS_val.py` | Add `validate_copresence()` + Plots 6a & 6b |
| #14 | `03_mergingGSS_val.py` | Extend `validate_copresence()` + Plot 6c |
| #15 | `03_mergingGSS_val.py` | Register method in run sequence |
| #16 | `03_mergingGSS_val.py` | Register 3 chart keys in `build_html_report()` |
| #17 | `01_readingGSS_val.py` | Add `check_raw_copresence_coverage()` method |
| #18 | — | Run `02_harmonizeGSS.py` |
| #19 | — | Run `03_mergingGSS.py` |
| #20 | — | Run acceptance checks script |
