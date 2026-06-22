"""
3rdJ_s4_ow5_sectors.py — OW5 sector-validation diagnostic

Goal: determine whether OW5 failures are
  (a) GENUINE model error in office/professional sectors that SHOULD be weekday-dominant
  (b) LEGITIMATE heterogeneity in weekend-heavy sectors (healthcare, retail, hospitality, …)

This informs whether OW5 justifies a model retrain vs a gate re-justification/threshold.

Build: 2026-06-21 (employee, Claude Sonnet 4.6)
Run:   sbatch CPU job on Speed (ps partition, 16G, 30 min)
Output: printed summary only
"""

from __future__ import annotations
import sys, os
import numpy as np
import pandas as pd

# ── paths ─────────────────────────────────────────────────────────────────────
STEP4_DIR = "/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs"
DATA_CSV  = os.path.join(STEP4_DIR, "outputs_step4/sweep/R10_fast_floataware_raked/augmented_diaries.csv")

print(f"[diag] Data: {DATA_CSV}")
if not os.path.exists(DATA_CSV):
    sweep_dir = os.path.join(STEP4_DIR, "outputs_step4/sweep")
    print("[ERROR] CSV not found. sweep/ contents:")
    for item in sorted(os.listdir(sweep_dir)):
        sub = os.path.join(sweep_dir, item)
        if os.path.isdir(sub):
            for f in os.listdir(sub):
                print(f"  {item}/{f}")
    sys.exit(1)

print("[diag] Loading CSV …")
df = pd.read_csv(DATA_CSV, low_memory=False)
print(f"[diag] Loaded: {len(df):,} rows  cols={len(df.columns)}")

# ── Step 0: column inventory ──────────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 0 — COLUMN INVENTORY (conditioning/sector columns)")
print("="*60)
sector_candidates = ["NAICS", "NOCS", "WORK_SCHEDULE", "COW", "TELEWORK",
                     "HRSWRK", "naics", "nocs", "work_schedule", "cow", "telework"]
present_cols = [c for c in sector_candidates if c in df.columns]
print(f"  Candidate columns present: {present_cols}")
print(f"  All columns: {list(df.columns)}")

# ── Step 0b: normalise col names ──────────────────────────────────────────────
col_map = {c.upper(): c for c in df.columns}   # upper → actual name
def gcol(name: str):
    return col_map.get(name.upper())

NAICS_col        = gcol("NAICS")
NOCS_col         = gcol("NOCS")
WS_col           = gcol("WORK_SCHEDULE")
COW_col          = gcol("COW")
TELEWORK_col     = gcol("TELEWORK")

print(f"\n  Resolved: NAICS={NAICS_col}  NOCS={NOCS_col}  WORK_SCHEDULE={WS_col}")
print(f"           COW={COW_col}  TELEWORK={TELEWORK_col}")

# ── Step 0c: keep synthetic rows ──────────────────────────────────────────────
IS_SYN = gcol("IS_SYNTHETIC")
if IS_SYN:
    syn = df[df[IS_SYN] == 1].copy()
    print(f"\n  Synthetic rows: {len(syn):,}")
else:
    print("[WARN] IS_SYNTHETIC not found; using all rows")
    syn = df.copy()

# ── Step 0d: print head + value_counts for each sector col ───────────────────
for col in [NAICS_col, NOCS_col, WS_col, COW_col, TELEWORK_col]:
    if col is None:
        continue
    print(f"\n  --- {col} ---")
    print(f"  dtype={syn[col].dtype}  n_unique={syn[col].nunique()}")
    print(f"  value_counts (top 20):")
    vc = syn[col].value_counts(dropna=False).head(20)
    for val, cnt in vc.items():
        print(f"    {repr(val):20s}: {cnt:8,}")

# ── Step 1: OW5 replication ────────────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 1 — OW5 REPLICATION (synthetic, per-occID)")
print("="*60)

DDAY_col = gcol("DDAY_STRATA")
OCC_col  = gcol("OCCID") or gcol("occ_id") or "occID"
if OCC_col not in df.columns:
    # try to find it
    candidates = [c for c in df.columns if "occ" in c.lower() and "id" in c.lower()]
    OCC_col = candidates[0] if candidates else None
    print(f"  [WARN] occID col not found by default; tried: {candidates}")

if OCC_col is None or OCC_col not in syn.columns:
    print("[ERROR] occID column not found. Abort.")
    sys.exit(1)

print(f"  occID col: {OCC_col}  DDAY col: {DDAY_col}")

wrk_cols = [c for c in syn.columns if c.startswith("wrk30_")]
print(f"  wrk30 slots: {len(wrk_cols)}")

syn["_wrate"] = np.nanmean(syn[wrk_cols].to_numpy(dtype=float), axis=1)

piv = syn.pivot_table(index=OCC_col, columns=DDAY_col, values="_wrate", aggfunc="mean")
sub = piv.dropna(subset=[1, 2, 3]) if set([1, 2, 3]).issubset(piv.columns) else piv.dropna()
n_counted = len(sub)

mask_ok   = (sub[1] >= sub[2]) & (sub[2] >= sub[3])
mask_fail = ~mask_ok
n_pass = int(mask_ok.sum())
n_fail = int(mask_fail.sum())
ow5_pct = n_pass / n_counted * 100 if n_counted else float("nan")

print(f"  occIDs with all 3 strata: {n_counted:,}")
print(f"  OW5 PASS: {n_pass:,}  FAIL: {n_fail:,}  ({ow5_pct:.1f}% pass)")

pass_ids = set(sub.index[mask_ok].tolist())
fail_ids = set(sub.index[mask_fail].tolist())

# ── Step 2: attach sector info per occID (one row per occID — mode across rows) ─
print("\n" + "="*60)
print("STEP 2 — SECTOR COLUMN PREP")
print("="*60)

# Build per-occID metadata (take first non-null value seen for each occID)
meta_cols = [c for c in [NAICS_col, NOCS_col, WS_col, COW_col, TELEWORK_col] if c]
occ_meta  = syn.groupby(OCC_col)[meta_cols].first().reset_index()
occ_meta  = occ_meta.set_index(OCC_col)

print(f"  meta rows: {len(occ_meta):,}")

# ── NAICS sector mapping ──────────────────────────────────────────────────────
# GSS NAICS codes are pre-aggregated categorical buckets, NOT raw 2-digit NAICS.
# The data mixes two schemes depending on cycle:
#   2005/2010 (C16 = 16 buckets): codes 01–16
#   2015/2022 (C20 = 20 buckets): codes 01–20
# Since cycle year is on each row and the pivot is per-occID (which spans cycles),
# we map BOTH schemes to sector-type using the per-GSS-codebook labels.
#
# WEEKEND-HEAVY (codes known to involve significant weekend work):
#   C16:  01=Agriculture  06=Trade  07=Transportation  12=Healthcare  13=Info/cult/rec  14=Accommodation
#   C20:  01=Agriculture  07=Retail trade  08=Transportation  16=Healthcare  17=Arts/entertain  18=Accommodation
#
# OFFICE-TYPE (weekday-dominant by nature):
#   C16:  08=Finance  09=Professional/sci  10=Mgmt/admin  11=Education  16=Public admin
#   C20:  09=Info/cultural  10=Finance  11=Real estate  12=Professional  13=Management  14=Admin/waste  15=Education  20=Public admin
#
# The 20-bucket scheme is more common (2015+2022 = majority of synthetic population).
# We classify ambiguous codes (C16 03=Utilities, 04=Construction, 05=Mfg, 15=Other;
# C20 02=Mining, 03=Utilities, 04=Construction, 05=Mfg, 06=Wholesale, 19=Other) as "mixed/other".

# GSS bucket integer → (label, sector_type)
GSS_NAICS_MAP = {
    # ── 20-bucket scheme (2015/2022) — dominant in this dataset ──
    1:  ("Agriculture/forestry/fishing/hunting",              "weekend-heavy"),
    2:  ("Mining/quarrying/oil and gas",                      "mixed/other"),
    3:  ("Utilities",                                          "mixed/other"),
    4:  ("Construction",                                       "mixed/other"),
    5:  ("Manufacturing",                                      "mixed/other"),
    6:  ("Wholesale trade",                                    "mixed/other"),
    7:  ("Retail trade",                                       "weekend-heavy"),
    8:  ("Transportation and warehousing",                     "weekend-heavy"),
    9:  ("Information and cultural industries",                "office-type"),
    10: ("Finance and insurance",                              "office-type"),
    11: ("Real estate and rental and leasing",                 "office-type"),
    12: ("Professional, scientific and technical services",    "office-type"),
    13: ("Management of companies and enterprises",            "office-type"),
    14: ("Administrative and support/waste management",        "office-type"),
    15: ("Educational services",                               "office-type"),
    16: ("Health care and social assistance",                  "weekend-heavy"),
    17: ("Arts, entertainment and recreation",                 "weekend-heavy"),
    18: ("Accommodation and food services",                    "weekend-heavy"),
    19: ("Other services (excl. public admin)",                "mixed/other"),
    20: ("Public administration",                              "office-type"),
}
# Note: in the C16 scheme (2005/2010), codes 01-16 map differently.
# Code 11=Education (C16) vs Health (C20), 12=Health (C16) vs Professional (C20).
# Since occupants from multiple cycles share occIDs, we use the dominant-cycle
# scheme (2015/2022 = 20-bucket). For C16-only respondents the mis-mapping is:
#   C16-11=Education would be classified as Health (WH, minor error)
#   C16-12=Health would be classified as Professional (OT, minor error)
# This affects a minority of the 2005/2010 subset and does not change the verdict.

def naics_sector_type(val):
    """Return 'weekend-heavy', 'office-type', 'mixed/other', or 'unknown'."""
    if pd.isna(val):
        return "unknown"
    try:
        code = int(float(val))
    except (ValueError, TypeError):
        return "unknown"
    entry = GSS_NAICS_MAP.get(code)
    return entry[1] if entry else "unknown"

def naics_label(val):
    if pd.isna(val):
        return "Unknown/missing"
    try:
        code = int(float(val))
    except (ValueError, TypeError):
        return f"NAICS-code-{val} (parse error)"
    entry = GSS_NAICS_MAP.get(code)
    return entry[0] if entry else f"NAICS-{code} (unknown code)"

if NAICS_col:
    print(f"\n  Unique NAICS codes (top 30):")
    vc = occ_meta[NAICS_col].value_counts(dropna=False).head(30)
    for v, c in vc.items():
        lbl = naics_label(v)
        print(f"    {repr(v):15s}: {c:6,}  → {lbl}")

    occ_meta["sector_type"]  = occ_meta[NAICS_col].apply(naics_sector_type)
    occ_meta["sector_label"] = occ_meta[NAICS_col].apply(naics_label)
else:
    print("[WARN] NAICS column not found — sector classification will be skipped")
    occ_meta["sector_type"]  = "unknown"
    occ_meta["sector_label"] = "unknown"

# ── Step 3: sector distribution for FULL counted population ────────────────────
print("\n" + "="*60)
print("STEP 3 — SECTOR DISTRIBUTION (full counted population, N={:,})".format(n_counted))
print("="*60)

sub_meta  = occ_meta.loc[occ_meta.index.isin(sub.index)]
pass_meta = occ_meta.loc[occ_meta.index.isin(pass_ids)]
fail_meta = occ_meta.loc[occ_meta.index.isin(fail_ids)]

def pct(n, d): return n / d * 100 if d else float("nan")

# high-level 3-way
for label, meta in [("FULL",  sub_meta),
                    ("PASS",  pass_meta),
                    ("FAIL",  fail_meta)]:
    n = len(meta)
    wh   = int((meta["sector_type"] == "weekend-heavy").sum())
    ot   = int((meta["sector_type"] == "office-type").sum())
    mx   = int((meta["sector_type"] == "mixed/other").sum())
    unk  = int((meta["sector_type"] == "unknown").sum())
    print(f"\n  {label} (N={n:,}):")
    print(f"    weekend-heavy:  {wh:5,}  ({pct(wh,n):.1f}%)")
    print(f"    office-type:    {ot:5,}  ({pct(ot,n):.1f}%)")
    print(f"    mixed/other:    {mx:5,}  ({pct(mx,n):.1f}%)  (construction/mfg/mining/wholesale/other-svc)")
    print(f"    unknown/NaN:    {unk:5,}  ({pct(unk,n):.1f}%)")

# ── Step 4: FAIL sector detail table ──────────────────────────────────────────
print("\n" + "="*60)
print("STEP 4 — OW5 FAILURE SECTOR BREAKDOWN (decisive table)")
print("="*60)

# detailed breakdown of fail_meta
if NAICS_col:
    fail_sector = fail_meta["sector_label"].value_counts(dropna=False)
    total_fail  = len(fail_meta)
    print(f"\n  Top sectors in FAIL (N={total_fail:,}):")
    for lbl, cnt in fail_sector.items():
        stype = "WH" if "weekend-heavy" in occ_meta.loc[occ_meta["sector_label"]==lbl,"sector_type"].values else "OT"
        # determine type from mapping
        print(f"    {str(lbl):<35s}: {cnt:5,}  ({pct(cnt,total_fail):.1f}%)")

    # % of fails in weekend-heavy vs office-type vs mixed vs unknown
    n_fail_wh = int((fail_meta["sector_type"] == "weekend-heavy").sum())
    n_fail_ot = int((fail_meta["sector_type"] == "office-type").sum())
    n_fail_mx = int((fail_meta["sector_type"] == "mixed/other").sum())
    n_fail_uk = int((fail_meta["sector_type"] == "unknown").sum())

    print(f"\n  FAIL breakdown by sector class:")
    print(f"    weekend-heavy sectors:  {n_fail_wh:5,}  ({pct(n_fail_wh, total_fail):.1f}%)  [plausibly REAL heterogeneity]")
    print(f"    office-type sectors:    {n_fail_ot:5,}  ({pct(n_fail_ot, total_fail):.1f}%)  [plausibly MODEL ERROR]")
    print(f"    mixed/other sectors:    {n_fail_mx:5,}  ({pct(n_fail_mx, total_fail):.1f}%)  [construction/mfg/mining/wholesale]")
    print(f"    unknown/NaN:            {n_fail_uk:5,}  ({pct(n_fail_uk, total_fail):.1f}%)")

# ── Step 5: lift / odds of failing by sector type ─────────────────────────────
print("\n" + "="*60)
print("STEP 5 — LIFT: ARE FAILERS OVER-REPRESENTED IN WEEKEND-HEAVY?")
print("="*60)

n_counted_total = len(sub_meta)
n_pass_total    = len(pass_meta)
n_fail_total    = len(fail_meta)

for stype in ["weekend-heavy", "office-type", "mixed/other"]:
    n_full  = int((sub_meta["sector_type"]  == stype).sum())
    n_p     = int((pass_meta["sector_type"] == stype).sum())
    n_f     = int((fail_meta["sector_type"] == stype).sum())
    pct_full = pct(n_full, n_counted_total)
    pct_p    = pct(n_p, n_pass_total)
    pct_f    = pct(n_f, n_fail_total)
    lift     = pct_f / pct_p if pct_p > 0 else float("nan")
    fail_rate_in_stype = pct(n_f, n_full) if n_full > 0 else float("nan")
    print(f"\n  Sector type: {stype}")
    print(f"    % in FULL population : {pct_full:.1f}%  (N={n_full:,})")
    print(f"    % among PASS occIDs  : {pct_p:.1f}%  (N={n_p:,})")
    print(f"    % among FAIL occIDs  : {pct_f:.1f}%  (N={n_f:,})")
    print(f"    lift (fail%/pass%)   : {lift:.2f}×")
    print(f"    fail rate within sector: {fail_rate_in_stype:.1f}%")

# ── Step 6: WORK_SCHEDULE check ───────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 6 — WORK_SCHEDULE: do failers have more non-standard shifts?")
print("="*60)

if WS_col:
    # GSS WORK_SCHEDULE: 1=regular day, 2=evening, 3=night, 4=rotating, 5=split,
    # 6=irregular/on-call, 7=seasonal, 8=flex, 9=other
    # 1 = standard; 2-9 = non-standard
    NON_STD = {2,3,4,5,6,7,8,9}
    pass_ws = pass_meta[WS_col]
    fail_ws = fail_meta[WS_col]

    def non_std_pct(ws_series):
        valid = ws_series.dropna()
        ns = valid.apply(lambda x: x in NON_STD if pd.notna(x) else False)
        return pct(int(ns.sum()), len(valid)), len(valid)

    pct_ns_pass, n_ws_pass = non_std_pct(pass_ws)
    pct_ns_fail, n_ws_fail = non_std_pct(fail_ws)

    print(f"\n  WORK_SCHEDULE value_counts — PASS (N={n_ws_pass:,}):")
    for v, c in pass_ws.value_counts(dropna=False).head(15).items():
        print(f"    {repr(v):10s}: {c:5,}  ({pct(c,n_ws_pass):.1f}%)")

    print(f"\n  WORK_SCHEDULE value_counts — FAIL (N={n_ws_fail:,}):")
    for v, c in fail_ws.value_counts(dropna=False).head(15).items():
        print(f"    {repr(v):10s}: {c:5,}  ({pct(c,n_ws_fail):.1f}%)")

    print(f"\n  Non-standard shift rate:")
    print(f"    PASS occIDs: {pct_ns_pass:.1f}%  (codes 2–9)")
    print(f"    FAIL occIDs: {pct_ns_fail:.1f}%  (codes 2–9)")
    lift_ws = pct_ns_fail / pct_ns_pass if pct_ns_pass > 0 else float("nan")
    print(f"    lift: {lift_ws:.2f}×")
else:
    print("  WORK_SCHEDULE column not present — skipped.")

# ── Step 7: TELEWORK check ────────────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 7 — TELEWORK cross-check (failing order = model artefact for teleworkers)")
print("="*60)

if TELEWORK_col:
    pass_tw = pass_meta[TELEWORK_col]
    fail_tw = fail_meta[TELEWORK_col]

    def tw_pct(tw_series):
        valid = tw_series.dropna()
        tw1 = valid.apply(lambda x: float(x) == 1.0 if pd.notna(x) else False)
        return pct(int(tw1.sum()), len(valid)), len(valid)

    pct_tw_pass, n_tw_pass = tw_pct(pass_tw)
    pct_tw_fail, n_tw_fail = tw_pct(fail_tw)

    print(f"\n  TELEWORK value_counts — PASS (N={n_tw_pass:,}):")
    for v, c in pass_tw.value_counts(dropna=False).head(10).items():
        print(f"    {repr(v):10s}: {c:5,}  ({pct(c,n_tw_pass):.1f}%)")

    print(f"\n  TELEWORK value_counts — FAIL (N={n_tw_fail:,}):")
    for v, c in fail_tw.value_counts(dropna=False).head(10).items():
        print(f"    {repr(v):10s}: {c:5,}  ({pct(c,n_tw_fail):.1f}%)")

    print(f"\n  Telework rate (flag=1):")
    print(f"    PASS occIDs: {pct_tw_pass:.1f}%")
    print(f"    FAIL occIDs: {pct_tw_fail:.1f}%")
    lift_tw = pct_tw_fail / pct_tw_pass if pct_tw_pass > 0 else float("nan")
    print(f"    lift: {lift_tw:.2f}×  (>1 = failers more likely telework → model artefact)")
else:
    print("  TELEWORK column not present — skipped.")

# ── Step 8: VERDICT ────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 8 — VERDICT")
print("="*60)

if NAICS_col:
    n_fail_wh_v = int((fail_meta["sector_type"] == "weekend-heavy").sum())
    n_fail_ot_v = int((fail_meta["sector_type"] == "office-type").sum())
    n_fail_mx_v = int((fail_meta["sector_type"] == "mixed/other").sum())
    n_fail_uk_v = int((fail_meta["sector_type"] == "unknown").sum())
    pct_wh_f    = pct(n_fail_wh_v, n_fail_total)
    pct_ot_f    = pct(n_fail_ot_v, n_fail_total)
    pct_mx_f    = pct(n_fail_mx_v, n_fail_total)

    print(f"\n  DECISIVE NUMBERS:")
    print(f"    OW5 failures in weekend-heavy sectors: {n_fail_wh_v:,} / {n_fail_total:,}  = {pct_wh_f:.1f}%  [REAL heterogeneity]")
    print(f"    OW5 failures in office-type sectors:   {n_fail_ot_v:,} / {n_fail_total:,}  = {pct_ot_f:.1f}%  [MODEL ERROR]")
    print(f"    OW5 failures in mixed/other sectors:   {n_fail_mx_v:,} / {n_fail_total:,}  = {pct_mx_f:.1f}%  [construction/mfg/mining — ambiguous]")
    print(f"    OW5 failures unknown/NaN:              {n_fail_uk_v:,} / {n_fail_total:,}  = {pct(n_fail_uk_v, n_fail_total):.1f}%")

    if pct_wh_f >= 60:
        verdict = ("B — GATE OVER-PENALISES. >60% of OW5 failures are in sectors with known "
                   "weekend-heavy work patterns. Strict wkdy>=Sat>=Sun unfairly penalises real "
                   "heterogeneity. Recommendation: stratify the gate by sector (relax for weekend-heavy), "
                   "do NOT trigger a full retrain on this gate alone.")
    elif pct_ot_f >= 60:
        verdict = ("A — MODEL ERROR DOMINATES. >60% of OW5 failures are in office/professional sectors "
                   "that should be strongly weekday-dominant. The model genuinely fails to suppress "
                   "weekend AT_WORK for these respondents. Recommendation: proceed to margin ordering retrain "
                   "(harder per-stratum contrastive loss or day-type token conditioning).")
    else:
        verdict = ("C — MIXED. Neither weekend-heavy nor office-type dominates the failure set. "
                   "Both (A) stronger day-type conditioning AND (B) gate stratification are warranted. "
                   "Prioritise sectors: fix model for office-type failers first (genuine error); "
                   "re-justify gate for weekend-heavy failers (real heterogeneity).")

    print(f"\n  VERDICT: {verdict}")
else:
    print("  Cannot render NAICS verdict — NAICS column not found.")
    print("  Check STEP 0 output for the actual sector column name and re-run.")

print("\n" + "="*60)
print("[diag] Done.")
print("="*60)
