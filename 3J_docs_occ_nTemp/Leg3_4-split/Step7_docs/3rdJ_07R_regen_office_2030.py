"""Regenerate ONLY `office_presence_multiplier_2030.csv` on the stock frame (FINDING 6 fix).

User decision 2026-08-02: "every cycle's schedules must come from the same sample pool". The 2030
office product was built straight from the D2030 pool while the 2022 office and the 2030 residential
products are built on the augmented stock. This rebuilds the office file through
`step7.build_office_2030_product()` -- the SAME function `3rdJ_07_aug_to_bem_4split.py:main()` now
calls, so the two cannot drift.

Why a targeted script instead of re-running Step-7's 2030 command: that command also rewrites
`BEM_Schedules_4split_2030_{cons,central,opt}.csv`. Those are frozen, in use by a running campaign,
and are NOT affected by this fix (residential already used the stock frame). Rewriting a frozen
product to change a different one is how provenance gets lost.

The predecessor file is BACKED UP, never overwritten in place.

Usage:  py -3 3rdJ_07R_regen_office_2030.py [--dry-run]
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import shutil
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
STEP7 = os.path.join(HERE, "3rdJ_07_aug_to_bem_4split.py")
OUT = os.path.join(HERE, "outputs_step7", "office_presence_multiplier_2030.csv")
STAMP = "2026-08-02"
ARCH = "Office_Knowledge"


def load_step7():
    spec = importlib.util.spec_from_file_location("step7_mod", STEP7)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["step7_mod"] = mod
    spec.loader.exec_module(mod)
    return mod


def band_table(df, title):
    print(f"\n  {title}")
    print(f"    {'BAND':<14}{'n_wd':>7}{'n_we':>7}{'mean_wd':>10}{'mean_we':>10}")
    d = df[df["office_archetype"] == ARCH]
    rows = {}
    for b in ["conservative", "hybrid", "fullyhybrid"]:
        s = d[d["BAND"] == b]
        wd, we = s[s.Day_Type == "Weekday"], s[s.Day_Type == "Weekend"]
        if wd.empty:
            continue
        rows[b] = (float(wd.AT_WORK_fraction.mean()), float(we.AT_WORK_fraction.mean()))
        print(f"    {b:<14}{int(wd.n_persons.iloc[0]):>7}{int(we.n_persons.iloc[0]):>7}"
              f"{rows[b][0]:>10.4f}{rows[b][1]:>10.4f}")
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="build and report, write nothing")
    a = ap.parse_args()
    m = load_step7()
    lookup = pd.read_csv(m.LOOKUP_OFFICE)

    print(f"AUG   : {m.AUG}")
    print(f"D2030 : {m.D2030}")
    print(f"target: {OUT}")

    before = pd.read_csv(OUT)
    before.columns = before.columns.str.strip()
    old = band_table(before, "BEFORE -- shipped product (built from the D2030 pool)")

    print("\nrebuilding on the stock frame (3 bands, each re-reads AUG + D2030) ...", flush=True)
    office_out = m.build_office_2030_product(lookup, d2030_path=m.D2030)

    # Step-7's own gates. These raise on failure -- a broken product must not reach disk.
    m.run_office_gates(office_out, is_2030=True, label="2030/FINDING-6-refit")
    new = band_table(office_out, "AFTER -- rebuilt on the stock frame")

    print("\n  delta (after vs before), same band:")
    for b in ["conservative", "hybrid", "fullyhybrid"]:
        if b in old and b in new:
            dwd = 100.0 * (new[b][0] - old[b][0]) / old[b][0]
            dwe = 100.0 * (new[b][1] - old[b][1]) / old[b][1]
            print(f"    {b:<14} weekday {dwd:+7.2f} %   weekend {dwe:+7.2f} %")

    # Band monotonicity has to survive the refit, or the WFH axis itself is in question.
    mono_wd = new["conservative"][0] > new["hybrid"][0] > new["fullyhybrid"][0]
    mono_we = new["conservative"][1] > new["hybrid"][1] > new["fullyhybrid"][1]
    print(f"\n  band monotonicity cons > hybrid > fullyhybrid: weekday {mono_wd}, weekend {mono_we}")
    if not (mono_wd and mono_we):
        print("  *** MONOTONICITY LOST -- reporting it, not hiding it. The WFH band axis must be")
        print("      re-examined before this product is used. Writing nothing.")
        sys.exit(1)

    lever_old = 100.0 * (old["fullyhybrid"][0] - old["conservative"][0]) / old["conservative"][0]
    lever_new = 100.0 * (new["fullyhybrid"][0] - new["conservative"][0]) / new["conservative"][0]
    print(f"  WFH lever (weekday cons -> fullyhybrid): {lever_old:+.2f} % -> {lever_new:+.2f} %")

    if a.dry_run:
        print("\n--dry-run: nothing written.")
        return

    bak = OUT.replace(".csv", f"_BAK_{STAMP}.csv")
    if not os.path.exists(bak):
        shutil.copy2(OUT, bak)
        print(f"\n  predecessor preserved -> {os.path.basename(bak)}")
    else:
        print(f"\n  backup already exists, not overwriting -> {os.path.basename(bak)}")

    m.atomic_write(office_out, OUT, "%.4f")
    print(f"  written -> {OUT}")
    print("\nDownstream: every 2030-family cell's OFFICE channel changes. Y2022 and the historical")
    print("years are untouched (they already used this frame). Re-run of the affected campaign")
    print("cells is required before any 2030 office number is quoted.")


if __name__ == "__main__":
    main()
