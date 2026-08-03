"""FINDING 7 option B -- regenerate ONLY the three 2030 retail products, from the calibrated pool.

Why a standalone script rather than `--year 2030 --bundle <b>`: the full command rebuilds
residential + office + hotel too, and `--sens retail` covers only cons and opt (central retail is
produced solely by a no-sens run). This rewire changes the retail channel and nothing else, so the
regeneration must touch the retail channel and nothing else -- rewriting four other products with
identical content would still bump their mtimes and their _BAK chain for no reason.

It calls the SAME `build_retail_product_2030` / `run_retail_gates` / `atomic_write` the pipeline
call site uses -- same discipline as `build_office_2030_product`, so this script and
`cmd_year_2030` cannot drift apart. `atomic_write` makes the `_BAK_<today>` predecessor copy
itself; the predecessors are kept on disk, never deleted.

Usage (locally):  py -3 3rdJ_07R_regen_retail_2030.py
"""
from __future__ import annotations

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STEP7 = os.path.join(HERE, "3rdJ_07_aug_to_bem_4split.py")


def main():
    spec = importlib.util.spec_from_file_location("step7_mod", STEP7)
    m = importlib.util.module_from_spec(spec)
    sys.modules["step7_mod"] = m
    spec.loader.exec_module(m)

    m.assert_d2030_is_c(m.D2030)
    m.OUT_DIR.mkdir(parents=True, exist_ok=True)

    for bundle in ("cons", "central", "opt"):
        scenario = m.BUNDLE_MAP[bundle]["retail_scenario"]
        print(f"\n[Retail/FINDING-7] bundle={bundle} scenario={scenario}", flush=True)
        out = m.build_retail_product_2030(scenario, d2030_path=m.D2030)
        m.run_retail_gates(out, label=f"2030/{bundle}", retail_scenario=scenario)
        m.atomic_write(out, m.OUT_DIR / f"retail_presence_multiplier_2030_{bundle}.csv", "%.6f")

    m._check_h5_monotonicity()
    print("\nretail 2030 regeneration COMPLETE (source = calibrated _C_v2)", flush=True)


if __name__ == "__main__":
    main()
