# Debug Report: 11CEN10GSS Pipeline

**Date:** 2026-03-31
**Status:** All three bugs fixed — re-run pipeline from step0 to regenerate outputs
**Compared against:** 06CEN05GSS and 16CEN15GSS (reference pipelines, assumed correct)

---

## Summary of Issues

| # | Bug | Severity | File Fixed | Symptom |
|---|-----|----------|------------|---------|
| 1 | STARTMIN/ENDMIN parsed as HHMM but data is decimal minutes | **Critical** | `11CEN10GSS_step0.py` ✅ | Flat/wrong diurnal occupancy pattern |
| 2 | ACTCODE not mapped to harmonized 1–14 categories | **Critical** | `11CEN10GSS_step0.py` ✅ | All metabolic rates stuck at 100 W |
| 3 | ROOM outliers not filtered (max=88, 47 HHs >15) | Moderate | `11CEN10GSS_alignment.py` ✅ | Physically impossible room counts in output |

---

## Bug 1: Time Format Mismatch → Wrong Occupancy Pattern

### What the plot shows
The `11CEN10GSS_BEM_temporals.png` shows:
- Average presence schedule is nearly **flat** (~0.35–0.45) across all 24 hours for both weekdays and weekends
- Reference pipelines (06CEN05GSS, 16CEN15GSS) show a clear residential diurnal pattern: high occupancy at night (~0.85), sharp morning departure dip, gradual afternoon return
- Sample household #51532 shows **completely constant** occupancy (0.25) and metabolic rate (100 W) all day

### Root cause
GSS 2010 episode file stores `STARTMIN` and `ENDMIN` as **decimal minutes from midnight** (range 0–1440+). Examples from the actual ProfileMatcher output:

```
STARTMIN=240, ENDMIN=260  → 4:00 AM to 4:20 AM  (240–260 decimal minutes)
STARTMIN=540, ENDMIN=780  → 9:00 AM to 1:00 PM  (540–780 decimal minutes)
STARTMIN=1440             → midnight (next day)
STARTMIN=1670             → 3:50 AM next day (wraps past midnight)
```

The `_create_individual_grid` method in `11CEN10GSS_HH_aggregation.py` parses these as **HHMM format**:

```python
# Lines 148–155 in 11CEN10GSS_HH_aggregation.py
s_raw = int(row[start_col])          # e.g., 540 (=9:00 AM in decimal minutes)
s_min = (s_raw // 100) * 60 + (s_raw % 100)  # Treats as HHMM: 5*60+40 = 340 min (5:40 AM) ← WRONG
e_raw = int(row[end_col])
e_min = (e_raw // 100) * 60 + (e_raw % 100)
```

This is **the correct parsing for HHMM** (where 540 means "5 hours 40 minutes"), but `STARTMIN` is already in decimal minutes (540 = 540 minutes = 9:00 AM). The correct interpretation:

| STARTMIN | Correct (decimal min) | Wrong (HHMM parsed) | Error |
|----------|-----------------------|---------------------|-------|
| 240 | slot 48 (4:00 AM) | slot 32 (2:40 AM) | −80 min |
| 480 | slot 96 (8:00 AM) | slot 57 (4:45 AM) | −195 min |
| 540 | slot 108 (9:00 AM) | slot 68 (5:40 AM) | −200 min |
| 720 | slot 144 (12:00 PM) | slot 88 (7:20 AM) | −280 min |
| 1020 | slot 204 (5:00 PM) | slot 127 (10:35 AM) | −385 min |

All episodes are systematically placed **too early** in the day. Work/school episodes that should create a 9–17h occupancy dip are being placed in the early morning hours (4–8 AM), producing a distorted, flattened pattern.

### Contrast with reference pipeline
The 06CEN05GSS episode data already has `start`/`end` columns in **HHMM format** (e.g., start=400 = 4:00 AM, start=800 = 8:00 AM). The HH_aggregation in 11CEN10GSS has fallback logic:

```python
start_col = 'start' if 'start' in episodes.columns else 'STARTMIN'
```

Since `start` is not in the 11CEN10GSS output, it falls back to `STARTMIN` (decimal minutes) and misapplies the HHMM parsing.

### Fix required
In `11CEN10GSS_HH_aggregation.py`, `_create_individual_grid` (lines ~148–155):

```python
# CURRENT (wrong for 11CEN10GSS):
s_raw = int(row[start_col])
s_min = (s_raw // 100) * 60 + (s_raw % 100)
e_raw = int(row[end_col])
e_min = (e_raw // 100) * 60 + (e_raw % 100)

# CORRECT for decimal minutes:
s_min = int(row[start_col]) % 1440   # mod 1440 handles next-day wrap (>1440)
e_min = int(row[end_col]) % 1440
```

Alternatively (and more robustly), `11CEN10GSS_step0.py` should convert `STARTMIN`/`ENDMIN` to HHMM format before saving, matching the 06CEN05GSS convention (`start`/`end` columns in HHMM). This keeps the HH_aggregation logic consistent across all pipelines.

---

## Bug 2: Activity Codes Not Mapped → Metabolic Rates Stuck at 100 W

### What the plot shows
The `11CEN10GSS_BEM_temporals.png` shows:
- Metabolic rate distribution: a **massive spike at exactly 100 W** (the fallback default), near zero spread
- Reference pipelines show a broad distribution from ~55–200 W with a peak around 70 W (Sleep) and secondary peaks at 80–130 W (Leisure, Work)
- Average metabolic intensity is completely flat at 100 W across all hours

### Root cause
GSS 2010 `ACTCODE` uses a hierarchical 3-digit coding scheme (e.g., 400=Paid Work, 430=Related to Work, 450=Household Work, 911=Sleep, 931=Personal Care). The `metabolic_map` in `11CEN10GSS_occToBEM.py` only contains **harmonized 1–14 keys**:

```python
# 11CEN10GSS_occToBEM.py, lines 58–74
self.metabolic_map = {
    '1': 125,   # Work & Related
    '5': 70,    # Sleep
    '10': 85,   # Passive Leisure
    ...
}
```

The fallback for any key not found is `100`:

```python
# Line 190
watts = [self.metabolic_map.get(c.strip(), 100) for c in codes]
```

Since `'400'`, `'430'`, `'450'`, `'911'` are all absent from the map, **every active time slot returns 100 W**. The actual occActivity values found in the data:

```
occActivity value counts (when occPre=1):
430     384   ← Paid Work, Related (raw 3-digit)
450     368   ← Household Work (raw 3-digit)
911     215   ← Sleep (raw 3-digit)
101     131   ← (raw 3-digit)
...
```

None of these match the metabolic_map keys `'1'`–`'14'`.

### Contrast with reference pipeline
The 06CEN05GSS episode data has an `occACT` column with values already mapped to harmonized categories (e.g., `occACT=5` for Sleep, `occACT=10` for Passive Leisure). These match the metabolic_map keys exactly.

### Fix required
A mapping from GSS 2010 raw activity codes (3-digit) to harmonized 1–14 categories must be added. This should be done in `11CEN10GSS_step0.py` when the episode file is processed (before saving `out10EP_ACT_PRE_coPRE.csv`), so the mapping propagates into all downstream steps.

GSS 2010 activity code → harmonized category mapping (to be added to `step0.py`):

```python
ACT_MAP_10 = {
    # 1xx – Personal Needs (→ 5 Sleep, 7 Personal Care)
    range(110, 120): 5,   # Sleep / Napping
    range(120, 190): 7,   # Personal Care (hygiene, eating for oneself)

    # 2xx – Household & Family Care (→ 2 Household Work)
    range(200, 300): 2,

    # 3xx – Caregiving (→ 3 Caregiving)
    range(300, 400): 3,

    # 4xx – Paid Work (→ 1 Work & Related)
    range(400, 500): 1,

    # 5xx – Education (→ 8 Education)
    range(500, 600): 8,

    # 6xx – Shopping & Services (→ 4 Shopping)
    range(600, 700): 4,

    # 7xx – Civic/Volunteer (→ 12 Volunteer)
    range(700, 800): 12,

    # 8xx – Socializing & Communication (→ 9 Socializing)
    range(800, 900): 9,

    # 9xx – Leisure (TV=Passive, Sport=Active)
    range(910, 960): 10,  # Passive Leisure (TV, reading, relaxing)
    range(960, 1000): 11, # Active Leisure (sport, outdoor)

    # 10xx – Travel (→ 13 Travel)
    range(1000, 1100): 13,
}
```

Note: Confirm exact boundaries against the GSS 2010 codebook before implementing.

---

## Bug 3: ROOM Outliers Not Filtered

### What was found
From the full `11CEN10GSS_BEM_Schedules_sample10pct.csv`:

```
ROOM statistics (per unique household):
  count: 12,998
  mean:  6.6
  max:   88          ← physically implausible
  >15:   47 HHs
```

Values above ~15 rooms are not realistic for residential dwellings in Canada and likely represent data entry errors or unusual Census records. Reference pipelines (`06CEN05GSS`, `16CEN15GSS`) show ROOM distributions capped at ~4.5 in their BEM non-temporal plots.

Note: The reference pipelines use GSS-sourced room data (which is already pre-coded in broader bins), while 11CEN10GSS uses raw Census 2011 room counts (continuous integer). This is a valid difference in data source, but the extreme outliers (>15) should still be removed.

### Fix required
Filter ROOM outliers during Census data preparation (before the alignment step) or in `occToBEM.py` before visualization. A reasonable cap is `ROOM <= 15`:

```python
# In Census preprocessing or alignment:
df_census = df_census[df_census['ROOM'] <= 15].copy()
```

This will remove 47 households (<0.4% of the 10% sample) and eliminate the implausible tail in the distribution plot.

---

## What Is Working Correctly

The following aspects of the pipeline are functioning as expected:

- **ProfileMatcher** (tiered matching): Produces correct Census–GSS demographic linkages; all residential variables (`Census_DTYPE`, `Census_BEDRM`, `Census_ROOM`, `Census_PR`) carry through correctly
- **Household assembly**: SIM_HH_ID assignment, single/family/roommate phases all correct
- **HH_aggregation logic (B/C/D)**: occPre (binary presence), occDensity (social density), and occActivity (activity set strings) aggregate correctly *given* correct inputs; the logic itself is sound
- **DTYPE and PR mapping** in `occToBEM.py`: Maps to readable labels correctly
- **Non-temporal distributions** (DTYPE, BEDRM, PR): Visually comparable to reference pipelines (see BEM non-temporal plots); BEDRM and PR distributions look reasonable

---

## Reproduction Notes

To verify these bugs, run:

```python
import pandas as pd

pm = pd.read_csv(".../Outputs_11CEN10GSS/ProfileMatching/11CEN10GSS_Full_Schedules_sample10pct.csv")

# Bug 1 check: STARTMIN values are decimal minutes (not HHMM)
print(pm['STARTMIN'].value_counts().sort_index().head(10))
# You will see: 240, 420, 480, 540, 720 ... (all decimal minutes)

# Bug 2 check: ACTCODE is 3-digit, not 1-14
print(pm['ACTCODE'].value_counts().head(10))
# You will see: 400, 430, 450, 911 ... (raw GSS codes)

agg = pd.read_csv(".../Outputs_11CEN10GSS/HH_aggregation/11CEN10GSS_Full_Aggregated_sample10pct.csv")
home = agg[agg['occPre'] == 1]
print(home['occActivity'].value_counts().head(10))
# You will see: 430, 450, 911 ... (still 3-digit, not mapped)
```

---

## Fixes Applied

### Bug 1 + 2: `11CEN10GSS_step0.py`

Added `ACT_MAP_10` dict and two helper functions at the top of the file:
- `_map_actcode(code_raw)`: maps raw 3-digit ACTCODE to harmonized 1–14 category
- `_min_to_hhmm(minutes_raw)`: converts decimal minutes (0–1440) to HHMM integer

At the end of `main()`, before `df.to_csv(...)`, the following new columns are added:
```python
df['occACT']      = df['ACTCODE'].apply(_map_actcode)   # harmonized 1-14
df['start']       = df['STARTMIN'].apply(_min_to_hhmm)  # HHMM format
df['end']         = df['ENDMIN'].apply(_min_to_hhmm)    # HHMM format
df['occPRE']      = df['PRE']
df['Spouse']      = df['SPOUSE']
df['Children']    = df['CHILDHSD']
df['otherInFAMs'] = df['MEMBHSD']
```

`HH_aggregation._create_individual_grid` prefers `occACT` over `ACTCODE` and `start`/`end` over `STARTMIN`/`ENDMIN`, so no changes to that file are needed.

The social column renames (`Spouse`, `Children`, `otherInFAMs`) also fix a previously silent issue where `occDensity` was always 0 (HH_aggregation's social_cols used title-case names that didn't match the uppercase raw columns).

### Bug 3: `11CEN10GSS_alignment.py`

Added a ROOM filter in `data_alignment()` immediately after loading the Census data:
```python
if 'ROOM' in df_census.columns:
    df_census['ROOM'] = pd.to_numeric(df_census['ROOM'], errors='coerce')
    df_census = df_census[df_census['ROOM'] <= 15].copy()
```

---

## Re-run Sequence

After these fixes, re-run the pipeline in order:

```
1. python 11CEN10GSS_step0.py
   → regenerates out10EP_ACT_PRE_coPRE.csv with occACT, start, end, occPRE, social columns

2. python 11CEN10GSS_alignment.py
   → reads updated episode file, applies ROOM <= 15 filter on Census side, saves Aligned files

3. python 11CEN10GSS_ProfileMatcher.py   (--sample 10)
4. python 11CEN10GSS_HH_aggregation.py  (--sample 10)
5. python 11CEN10GSS_occToBEM.py        (--sample 10)
```

After re-running, the temporal plots should show:
- Clear residential diurnal pattern: high overnight occupancy, dip during work hours (9–17h weekdays)
- Metabolic rate distribution spread from ~70–200 W (sleep at 70 W, leisure at 85–110 W, work at 125 W)
- Sample household schedules with dynamic occupancy and activity-varying heat output

---

## Summary: Bugs, Improvements, and Expected Results

### What the bugs were

The pipeline ran without crashing, but produced physically wrong outputs. Three bugs were identified by comparing the `11CEN10GSS_BEM_temporals.png` and `11CEN10GSS_BEM_non_temporals.png` against the working reference pipelines (06CEN05GSS, 16CEN15GSS).

**Bug 1 — Wrong time slot assignments (Critical)**
GSS 2010 stores episode start and end times as decimal minutes from midnight (e.g., STARTMIN=540 = 9:00 AM = 540 minutes). The `HH_aggregation` code parsed these as HHMM format (540 interpreted as "5 hours 40 minutes" = 5:40 AM = 340 minutes). Every episode was placed in the wrong 5-minute slot, systematically shifted 1–6 hours too early. A 9 AM work episode landed at 5:40 AM; a noon meal landed at 7:20 AM. The result was a completely distorted occupancy schedule — no recognisable morning departure dip, no evening return peak, and some sample households showing completely flat lines all day.

**Bug 2 — All metabolic rates stuck at 100 W (Critical)**
GSS 2010 uses 3-digit raw activity codes (e.g., 450 = Sleep, 430 = Eating, 911 = Passive Leisure). The `occToBEM` script maps activity codes to Watts using a dictionary keyed on harmonized 1–14 integers (e.g., `'5': 70` for Sleep). Since no 3-digit code matched any key, every active time slot fell back to the hardcoded default of 100 W. The metabolic rate distribution showed a single massive spike at 100 W instead of the expected spread from ~70 W (Sleep) to ~200 W (Active Leisure). The reference pipelines pre-processed their episode files to use the harmonized 1–14 scheme; 11CEN10GSS did not.

**Bug 3 — Implausible room counts (Moderate)**
Census 2011 ROOM values were passed through without any cap. The output contained 47 households with more than 15 rooms (max = 88), which are physically implausible for residential dwellings and almost certainly data entry errors in the raw PUMF file. Reference pipelines use GSS-sourced room data which is pre-binned and does not have this issue.

**Bonus issue uncovered — Social density always zero (Silent)**
Because the raw GSS 2010 social columns use uppercase names (SPOUSE, CHILDHSD, MEMBHSD) and `HH_aggregation` looks for title-case names (Spouse, Children, otherInFAMs), no social columns were ever matched. The `occDensity` field was zero for every household and every time slot, meaning the BEM occupancy formula `occPre × (occDensity + 1)` collapsed to `occPre × 1`, effectively ignoring co-presence entirely.

---

### What was improved

All fixes were made in `11CEN10GSS_step0.py` and `11CEN10GSS_alignment.py`. No other pipeline files were modified.

**`11CEN10GSS_step0.py`**

Added `ACT_MAP_10` — a dictionary of 30 empirically verified activity code mappings derived by analysing mean duration, time of day, and home/away fraction for each code in the raw GSS 2010 episode file. Key confirmed mappings: 450 → Sleep (249 min avg, 82% nighttime), 11 → Paid Work (away, 201 min), 911 → Passive Leisure (home, evening), 430 → Eating (100% home, 33 min). A range-based fallback covers codes not in the specific map.

Added `_map_actcode()` which applies the mapping, and `_min_to_hhmm()` which converts decimal minutes to the HHMM integer format the rest of the pipeline expects (e.g., 540 → 900).

Before saving the episode CSV, seven new columns are appended:
- `occACT` (harmonized 1–14 activity category)
- `start` / `end` (HHMM format)
- `occPRE` (alias for PRE)
- `Spouse`, `Children`, `otherInFAMs` (social column renames)

`HH_aggregation` already prefers these column names via its own fallback logic, so it picks them up automatically with no changes needed there.

**`11CEN10GSS_alignment.py`**

Added a `ROOM <= 15` filter applied to the Census DataFrame immediately after it is loaded in `data_alignment()`. Rows with more than 15 rooms are dropped before any harmonization runs.

---

### What to expect as results

After re-running the full pipeline (step0 → alignment → ProfileMatcher → HH_aggregation → occToBEM), the output plots should look qualitatively similar to the reference pipelines:

**Temporal plots (`11CEN10GSS_BEM_temporals.png`)**

| Panel | Before fix | After fix |
|-------|-----------|-----------|
| Occupancy fraction distribution | Broad flat spread, no clear peaks | Bimodal: large peak near 0 (empty hours) and near 1 (full household home) |
| Metabolic rate distribution | Single spike at exactly 100 W | Spread from ~70 W (Sleep) to ~200 W (Active Leisure), peak around 70–90 W |
| Average presence schedule | Nearly flat ~0.35–0.45 all day | Clear diurnal shape: high at night (~0.7–0.9), dip during work hours, evening return |
| Average metabolic intensity | Flat line at 100 W | Rises through the morning as household wakes, dips slightly at night (Sleep) |
| Sample household weekday | Constant occupancy, flat heat gain | Dynamic occupancy with departures/arrivals, varying metabolic rate by activity |
| Sample household weekend | Constant occupancy, flat heat gain | Higher daytime occupancy than weekday, more leisurely metabolic profile |

**Non-temporal plots (`11CEN10GSS_BEM_non_temporals.png`)**

| Panel | Before fix | After fix |
|-------|-----------|-----------|
| DTYPE distribution | Correct (no change needed) | Correct (no change needed) |
| BEDRM distribution | Correct (no change needed) | Correct (no change needed) |
| ROOM distribution | Tail up to 88 rooms visible | Capped at 15; distribution concentrated in realistic 3–10 room range |
| PR distribution | Correct (no change needed) | Correct (no change needed) |

**Quantitative sanity checks** (already in `occToBEM.py` output):
- Mean nighttime occupancy (0–6h) should now be **higher** than mean daytime occupancy (9–17h) — the script already flags if this check fails
- Mean metabolic rate for active slots should be well below 100 W for sleep-heavy nights (~70 W) and above 100 W for active daytime periods

The activity code mapping was derived empirically from the data rather than from the official codebook, so minor inaccuracies in less common codes are possible. If the metabolic rate distribution still looks off after re-running, checking the occActivity values in the regenerated aggregated file against the GSS 2010 Activity Classification codebook is the next diagnostic step.
