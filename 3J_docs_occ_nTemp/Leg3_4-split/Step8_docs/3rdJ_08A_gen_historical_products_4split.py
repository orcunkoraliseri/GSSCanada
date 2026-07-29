"""3rdJ_08A_gen_historical_products_4split.py -- Step 8A: Historical BEM/UBEM products (3J Leg-3
4-split).

Generates, for CYCLE_YEAR in {2005, 2010, 2015}:
  - BEM_Schedules_4split_{year}.csv          (residential REPLACE)
  - office_presence_multiplier_{year}.csv    (office MODULATE, BAND="observed")
  - retail_presence_multiplier_{year}.csv    (retail MODULATE, self-normalizing)

so Step 8's scenario matrix gains 3 historical anchor points on the SAME method already used
for 2022/2030 (3rdJ_07_aug_to_bem_4split.py).

HOTEL IS DELIBERATELY NOT GENERATED HERE. Manager decision (already taken, not reopened):
`0_Occupancy/processed/hotel_multiplier_lookup.csv` only covers 2011-2022, and QC ground truth
starts 2019 (3rdJ_06_hotel_sarima_4split.py:24-29). Fabricating a 2005/2010/2015 hotel curve from
data that starts in 2011/2019 would either extrapolate blindly or hold hotel constant while
letting residential/office/retail vary -- a real confound. Instead, for ALL THREE historical
years, on BOTH cities, the hotel channel stays at NECB baseline, uninjected -- uniform across the
whole historical arm of the matrix, so there is no province x channel confound and nothing is
fabricated. This is a scope decision, not an oversight; do not "fix" it by inventing a hotel
curve without reopening the decision with the manager.

--------------------------------------------------------------------------------------------
Reuse discipline (why this file is thin)
--------------------------------------------------------------------------------------------
`3rdJ_07_aug_to_bem_4split.py` (Step7_docs/) is loaded as a module via importlib (its filename
is not a valid Python identifier, so a normal `import` cannot reach it) and its functions are
called DIRECTLY, not copy-pasted:
  - convert()                    -- residential REPLACE, byte-for-byte the function Step 7 uses.
  - complete_day_types()         -- donor-draw day-type completion (DRAW_COLS already includes
                                     RET -- Step 7 already extended this for the 4-split).
  - build_office_multiplier()    -- office MODULATE, shared-peak (band-independent) normalizer.
  - build_retail_product_2022()  -- retail MODULATE. Despite the name this function is fully
                                     generic: it only reads PR/DDAY_STRATA/RET off whatever
                                     DataFrame it is given and calls
                                     _retail_rows_from_slotarray(..., ref_peak=None) internally --
                                     i.e. it is ALREADY the self-normalizing (ref_peak=None) path.
                                     That is the CORRECT path for historical years (see below) --
                                     calling this function unmodified is not a workaround, it is
                                     the intended reuse.
  - check_mutex(), run_residential_gates(), run_office_gates(), run_retail_gates(),
    atomic_write() -- all reused verbatim.
A second implementation of any of the above would be a second source of truth -- exactly the
failure mode already found and fixed once in this codebase (the retail `multiplier`
self-cancellation bug, see 3rdJ_08_implementation_improvements.md Defaut 1).

--------------------------------------------------------------------------------------------
Retail normalization -- ref_peak=None is the CORRECT path here, not a shortcut
--------------------------------------------------------------------------------------------
`_retail_rows_from_slotarray(..., ref_peak=...)` grew a `ref_peak` parameter because the 2030
BAND LEVERS (cons/central/opt scalar multipliers on top of a shared base) were being erased by
naive self-normalization: dividing a band-levered array by its OWN max cancels the lever
identically for every band. 2005/2010/2015 have no such lever -- each historical year's retail
signal is the survey's own diary-derived shape, with nothing else scaling it up or down, so there
is nothing for self-normalization to erase. `build_retail_product_2022()` uses `ref_peak=None`
(self-normalizing) precisely because 2022 is in the same situation -- one band, no lever -- and
that is exactly why calling it unmodified for 2005/2010/2015 is correct rather than a mechanical
misapplication of the 2030 fix.

--------------------------------------------------------------------------------------------
What is genuinely NEW here: demographic-tiered-matched assembly onto the frozen stock frame
--------------------------------------------------------------------------------------------
Ported from Leg2_2-split/Step8_docs/3rdJ_08A_gen_historical_schedules.py::demo_assemble(), with
one substantive extension: the swapped diary-column block is ACT+HOM+WRK+RET (4-split) instead of
ACT+HOM+WRK (2-split) -- retail's ret30_* columns must move as a unit with the other three so a
historical year's whole diary (not 3/4 of it) gets substituted in.

For each historical year:
  1. pool  = rows of the 3J AUG file (`3rdJ_25CEN_aug_Full_Aggregated_excl.csv`, Step 5 output)
     with CYCLE_YEAR == year AND IS_SYNTHETIC == 0 (OBSERVED rows only -- see "Judgement call"
     below for why the Leg-2 rake step that also recovered IS_SYNTHETIC==1 rows is NOT ported).
  2. stock = the SAME frame Step 7 already uses for the 2022 product: `pd.read_csv(step7.AUG)`
     with NO CYCLE_YEAR/IS_SYNTHETIC filter (verified below, not assumed -- see "Stock frame").
     This is what makes the historical products comparable to 2022/2030 on the same population.
  3. demo_assemble(stock, pool): tiered demographic match on AGEGRP/SEX/MARSTH/HHSIZE/LFTAG +
     DDAY_STRATA (same TIERS cascade as Leg-2, unchanged), then a WHOLESALE copy of that matched
     pool row's ACT+HOM+WRK+RET block onto the stock row. Dwelling attributes (HHSIZE, DTYPE,
     BEDRM, CONDO, PR, MATCH_TIER, DDAY_STRATA, NOCS, LFTAG) come from `stock`, unchanged, for
     every year -- exactly Leg-2's REPLACE-only-the-diary discipline. NOCS/LFTAG (and therefore
     office archetype / employed-status) are NOT re-drawn from the historical pool; only
     time-use (what a person is doing) is. This is inherited from Leg-2's own demo_assemble, not
     a new judgement call.
  4. complete_day_types(assembled) -- reused verbatim from Step 7.
  5. convert() / build_office_multiplier() / build_retail_product_2022() -- reused verbatim.

--------------------------------------------------------------------------------------------
Judgement call: the Leg-2 "Phase-8B rake" step is deliberately NOT ported
--------------------------------------------------------------------------------------------
Leg-2's 08A script has a `rake_cycle()` step that flips IS_SYNTHETIC==1 rows' hom30/wrk30 values,
slot-by-slot and independently per column, to match each cycle's OWN observed marginal -- done on
the pool BEFORE demographic assembly, to recover the ~40-45% of each historical cycle's rows that
are synthetic rather than discarding them.

That independent per-column flip is NOT safe to port to 4-split. The 2J-to-3J bug audit (see this
repo's MEMORY.md / 2J improvements log) found that flipping hom30 and wrk30 independently, with no
cross-column mutex awareness, is EXACTLY the mechanism that produced a real hom30/wrk30 mutex
conflict bug in the 2-channel pipeline. `3rdJ_07_aug_to_bem_4split.py::check_mutex()` (H8) exists
specifically because "Leg-2's Step-7 validator had no mutex check" let that bug cascade
undetected. Adding a THIRD independently-flipped channel (ret30) on top of a mechanism already
proven to produce mutex violations would very likely reproduce the same bug class, worse.

Decision taken here: use IS_SYNTHETIC==0 (observed) pool rows only, and copy the matched pool
row's ACT+HOM+WRK+RET block WHOLESALE (one shave-and-copy, not three independent column edits).
A real diary row's own hom/wrk/ret triplet is mutex-consistent by construction (a person cannot
already be simultaneously "at home" and "at work" and "at retail" in the same real diary), and
copying it as a block preserves that. This is confirmed, not assumed: `check_mutex()` is run on
the assembled AND the completed frame for every year below, and must PASS before the year's
products are built. This also matches Leg-2's own `stock` definition, which was ALSO
IS_SYNTHETIC==0-only (`aug[(CYCLE_YEAR==2022)&(IS_SYNTHETIC==0)]`) -- using observed-only pools
for the historical years is consistent with what Leg-2 already did for its stock, just without
the extra (and, with 3 channels, unsafe) rake-recovery step for the synthetic remainder.
Consequence: pool sizes are smaller than Leg-2's raked pools (2005: 5,184 / 2010: 3,963 /
2015: 4,112 observed rows -- verified at runtime, printed below), but still ample for the 4-tier
demographic cascade to fully resolve (see printed match-tier report per year).

--------------------------------------------------------------------------------------------
Stock frame -- read from Step-7's own code, not hardcoded
--------------------------------------------------------------------------------------------
Verified by inspection before writing this script (not assumed): `3rdJ_25CEN_aug_Full_Aggregated_
excl.csv` contains ALL FOUR cycles' rows in one file (CYCLE_YEAR in {2005,2010,2015,2022}, 29,502
total person-rows). `cmd_year_2022()` in Step 7 reads this file with `pd.read_csv(AUG)` and NO
CYCLE_YEAR filter -- so the "stock" that already produced the LOCKED
`BEM_Schedules_4split_2022.csv` (md5 unchanged by this script, verified in the Step-8 Progress
Log) is the FULL unfiltered file: 29,502 person-rows, 23,115 unique SIM_HH_ID. This script reuses
that exact same stock (same file, same lack of filter) so the historical products sit on the
identical household/dwelling population as 2022/2030 -- only the injected diary differs.

seed=42 throughout (demo_assemble's own rng, plus complete_day_types()'s internal rng=42 reused
unmodified from Step 7). Deps: pandas, numpy (existing env). No new packages.

Usage (run-from-anywhere):
  py -3 3rdJ_08A_gen_historical_products_4split.py --year 2015
  py -3 3rdJ_08A_gen_historical_products_4split.py --year all

2026-07-28 built.
"""
import sys
import argparse
import importlib.util
import hashlib
from pathlib import Path
from collections import defaultdict

import numpy as np
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# Paths + load Step-7's module (functions REUSED, not reimplemented)
# ---------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent            # Step8_docs/
LEG3 = HERE.parent                                 # Leg3_4-split/
STEP7_PATH = LEG3 / "Step7_docs" / "3rdJ_07_aug_to_bem_4split.py"
S7_OUT = LEG3 / "Step7_docs" / "outputs_step7"

_spec = importlib.util.spec_from_file_location("_step7_4split_reused", STEP7_PATH)
step7 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(step7)

OUT_DIR = HERE / "outputs_step8" / "historical_schedules"
CYCLES = [2005, 2010, 2015]

ACT, HOM, WRK, RET = step7.ACT, step7.HOM, step7.WRK, step7.RET

KEYS = ["AGEGRP", "SEX", "MARSTH", "HHSIZE", "LFTAG"]
TIERS = [KEYS,
         ["AGEGRP", "SEX", "LFTAG"],
         ["AGEGRP", "SEX"],
         []]


# ---------------------------------------------------------------------------
# demo_assemble -- ported from Leg-2 08A, extended ACT+HOM+WRK -> ACT+HOM+WRK+RET
# ---------------------------------------------------------------------------
def _canon(df, cols):
    return {k: pd.to_numeric(df[k], errors="coerce").astype("Int64").astype(str).values for k in cols}


def demo_assemble(stock, pool):
    """Match each stock person-row to a historical-cycle pool row by tiered demographics +
    DDAY_STRATA, then copy that pool row's ACT+HOM+WRK+RET diary block onto the stock row
    WHOLESALE (mutex-safe by construction -- see file docstring 'Judgement call')."""
    rng = np.random.default_rng(42)
    pool = pool.reset_index(drop=True)
    allk = KEYS + ["DDAY_STRATA"]
    sc, pc = _canon(stock, allk), _canon(pool, allk)

    def ck(canon, gk):
        out = canon[gk[0]].astype(object)
        for k in gk[1:]:
            out = out + "|" + canon[k]
        return out

    n = len(stock)
    chosen = np.full(n, -1, np.int64)
    tier_of = np.zeros(n, np.int8)
    remaining = np.ones(n, bool)
    for ti, ks in enumerate(TIERS, 1):
        gk = ks + ["DDAY_STRATA"]
        grp = defaultdict(list)
        for pos, key in enumerate(ck(pc, gk)):
            grp[key].append(pos)
        grp = {k: np.asarray(v) for k, v in grp.items()}
        sck = ck(sc, gk)
        for j in np.where(remaining)[0]:
            arr = grp.get(sck[j])
            if arr is not None and len(arr):
                chosen[j] = arr[rng.integers(len(arr))]
                tier_of[j] = ti
                remaining[j] = False
        lbl = ",".join(ks) if ks else "strata-only"
        print(f"    tier {ti} ({lbl}): matched {int((tier_of == ti).sum()):,}, "
              f"remaining {int(remaining.sum()):,}", flush=True)
        if not remaining.any():
            break
    assert chosen.min() >= 0, "unmatched stock rows remain after all tiers"
    out = stock.copy()
    out[ACT + HOM + WRK + RET] = pool.iloc[chosen][ACT + HOM + WRK + RET].values
    return out


# ---------------------------------------------------------------------------
# Per-year runner
# ---------------------------------------------------------------------------
def gen_year(year, stock, aug_full, lookup_df):
    print(f"\n{'=' * 64}\n  CYCLE {year}\n{'=' * 64}", flush=True)
    pool = aug_full[(aug_full["CYCLE_YEAR"] == year) & (aug_full["IS_SYNTHETIC"] == 0)].copy()
    print(f"  pool (observed only): {len(pool):,} rows, "
          f"{pool['SIM_HH_ID'].nunique():,} unique SIM_HH_ID", flush=True)
    step7.check_mutex(pool, f"{year} pool (pre-assembly, sanity check)")

    print("  demographic-tiered-matched assembly onto frozen stock:", flush=True)
    assembled = demo_assemble(stock, pool)
    step7.check_mutex(assembled, f"{year} assembled")

    completed = step7.complete_day_types(assembled)
    step7.check_mutex(completed, f"{year} completed")

    # ---- Residential (reused convert()) ----
    bem = step7.convert(completed)
    step7.run_residential_gates(bem, label=str(year))
    out_r = OUT_DIR / f"BEM_Schedules_4split_{year}.csv"
    step7.atomic_write(bem, out_r, "%.3f")

    # ---- Office (reused build_office_multiplier(), single "observed" band) ----
    off = step7.build_office_multiplier(completed, "observed", lookup_df)
    step7.run_office_gates(off, is_2030=False, label=str(year))
    out_o = OUT_DIR / f"office_presence_multiplier_{year}.csv"
    step7.atomic_write(off, out_o, "%.4f")

    # ---- Retail (reused build_retail_product_2022(); ref_peak=None self-normalizing path,
    #      correct here per file docstring -- no band lever exists for historical years) ----
    ret = step7.build_retail_product_2022(completed)
    step7.run_retail_gates(ret, label=str(year))   # retail_scenario=None -> expected_peak=0.95
    out_ret = OUT_DIR / f"retail_presence_multiplier_{year}.csv"
    step7.atomic_write(ret, out_ret, "%.6f")

    print(f"  CYCLE {year} COMPLETE -> {out_r.name}, {out_o.name}, {out_ret.name}", flush=True)
    return bem, off, ret


# ---------------------------------------------------------------------------
# Defaut-2 verification: consumed-column pairwise comparison (not md5)
# ---------------------------------------------------------------------------
def _md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def compare_consumed_columns():
    """Pairwise (2005,2010,2015,2022) comparison on the columns the BEM actually reads --
    the Defaut-2 rule. A Delta=0 on any pair means that pair is not a distinct scenario."""
    years = [2005, 2010, 2015, 2022]
    print(f"\n{'=' * 64}\n  DEFAUT-2 VERIFICATION -- consumed columns, pairwise\n{'=' * 64}", flush=True)

    # Residential: Occupancy_Schedule, Metabolic_Rate
    res = {}
    for y in years:
        p = (OUT_DIR / f"BEM_Schedules_4split_{y}.csv") if y != 2022 else (S7_OUT / "BEM_Schedules_4split_2022.csv")
        df = pd.read_csv(p, usecols=["SIM_HH_ID", "Day_Type", "Hour", "Occupancy_Schedule", "Metabolic_Rate"])
        res[y] = df.set_index(["SIM_HH_ID", "Day_Type", "Hour"]).sort_index()
    print("\n  [Residential] Occupancy_Schedule / Metabolic_Rate:", flush=True)
    for i, y1 in enumerate(years):
        for y2 in years[i + 1:]:
            a, b = res[y1].align(res[y2], join="inner")
            assert len(a) == len(res[y1]) == len(res[y2]), \
                f"row-key mismatch {y1} vs {y2}: {len(a)} aligned vs {len(res[y1])}/{len(res[y2])}"
            d_occ = (a["Occupancy_Schedule"] - b["Occupancy_Schedule"]).abs()
            d_met = (a["Metabolic_Rate"] - b["Metabolic_Rate"]).abs()
            print(f"    {y1} vs {y2}: Occupancy_Schedule max|D|={d_occ.max():.4f} "
                  f"({int((d_occ > 1e-9).sum()):,}/{len(a):,} rows differ) | "
                  f"Metabolic_Rate max|D|={d_met.max():.2f} "
                  f"({int((d_met > 1e-9).sum()):,}/{len(a):,} rows differ)", flush=True)

    # Office: AT_WORK_fraction
    off = {}
    for y in years:
        p = (OUT_DIR / f"office_presence_multiplier_{y}.csv") if y != 2022 else (S7_OUT / "office_presence_multiplier_2022.csv")
        df = pd.read_csv(p, usecols=["office_archetype", "Day_Type", "Hour", "AT_WORK_fraction"])
        off[y] = df.set_index(["office_archetype", "Day_Type", "Hour"]).sort_index()
    print("\n  [Office] AT_WORK_fraction:", flush=True)
    for i, y1 in enumerate(years):
        for y2 in years[i + 1:]:
            a, b = off[y1].align(off[y2], join="inner")
            assert len(a) == len(off[y1]) == len(off[y2]), \
                f"row-key mismatch {y1} vs {y2}"
            d = (a["AT_WORK_fraction"] - b["AT_WORK_fraction"]).abs()
            print(f"    {y1} vs {y2}: AT_WORK_fraction max|D|={d.max():.4f} "
                  f"({int((d > 1e-9).sum()):,}/{len(a):,} rows differ)", flush=True)

    # Retail: multiplier
    ret = {}
    for y in years:
        p = (OUT_DIR / f"retail_presence_multiplier_{y}.csv") if y != 2022 else (S7_OUT / "retail_presence_multiplier_2022.csv")
        df = pd.read_csv(p, usecols=["Day_Type", "PR", "slot", "multiplier"])
        ret[y] = df.set_index(["Day_Type", "PR", "slot"]).sort_index()
    print("\n  [Retail] multiplier:", flush=True)
    for i, y1 in enumerate(years):
        for y2 in years[i + 1:]:
            a, b = ret[y1].align(ret[y2], join="inner")
            assert len(a) == len(ret[y1]) == len(ret[y2]), \
                f"row-key mismatch {y1} vs {y2}"
            d = (a["multiplier"] - b["multiplier"]).abs()
            print(f"    {y1} vs {y2}: multiplier max|D|={d.max():.4f} "
                  f"({int((d > 1e-9).sum()):,}/{len(a):,} rows differ)", flush=True)

    print(f"\n{'=' * 64}\n  DEFAUT-2 VERIFICATION COMPLETE\n{'=' * 64}", flush=True)


def report_md5s():
    print(f"\n{'=' * 64}\n  MD5 / ROW COUNTS -- newly generated products\n{'=' * 64}", flush=True)
    for y in CYCLES:
        for prefix in ("BEM_Schedules_4split", "office_presence_multiplier", "retail_presence_multiplier"):
            p = OUT_DIR / f"{prefix}_{y}.csv"
            if p.exists():
                with open(p, encoding="utf-8") as fh:
                    n = sum(1 for _ in fh) - 1
                print(f"    {p.name}: md5={_md5(p)}  rows={n:,}", flush=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", choices=["2005", "2010", "2015", "all"], default="all")
    ap.add_argument("--skip-compare", action="store_true",
                     help="skip the Defaut-2 pairwise consumed-column comparison against 2022")
    args = ap.parse_args()
    years = CYCLES if args.year == "all" else [int(args.year)]

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Loading 3J Leg-3 AUG file (Step-7's own AUG constant): {step7.AUG}", flush=True)
    aug_full = pd.read_csv(step7.AUG, low_memory=False)
    print(f"  {len(aug_full):,} rows; cycles {sorted(aug_full['CYCLE_YEAR'].unique())}", flush=True)

    # Stock frame -- literally Step-7's own definition (same file, unfiltered). Verified, not
    # hardcoded: this equals the frame that already produced the locked 2022/2030 products.
    stock = aug_full
    print(f"  Stock frame (= Step-7's unfiltered AUG read): {len(stock):,} rows, "
          f"{stock['SIM_HH_ID'].nunique():,} unique SIM_HH_ID", flush=True)

    print(f"Loading office lookup: {step7.LOOKUP_OFFICE.name}", flush=True)
    lookup_df = pd.read_csv(step7.LOOKUP_OFFICE)

    for y in years:
        gen_year(y, stock, aug_full, lookup_df)

    report_md5s()

    if args.year == "all" and not args.skip_compare:
        compare_consumed_columns()

    print("\nDONE", flush=True)


if __name__ == "__main__":
    main()
