"""FINDING 6 measurement. READ-ONLY: writes nothing into the pipeline, changes no product.

The shipped 2030 office multiplier is built from the D2030 pool DIRECTLY
(`3rdJ_07_aug_to_bem_4split.py:964-967`), while the 2022 one is built from the augmented STOCK
(`:869`) and the residential 2030 product -- three lines above the office block -- is built from
`assemble_2030()`'s output. This script builds the office multiplier BOTH ways on the same band and
prints the two weekend means side by side, so the question "does the source choice matter?" is
answered by measurement instead of argument.

It imports the real Step-7 functions rather than re-implementing them, so there is no chance of
measuring my own copy of the logic instead of the pipeline's.

Usage:  py -3 3rdJ_09E_office_source_probe.py [--band hybrid]
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
LEG3 = os.path.dirname(HERE)
STEP7 = os.path.join(LEG3, "Step7_docs", "3rdJ_07_aug_to_bem_4split.py")
ARCH = "Office_Knowledge"


def load_step7():
    spec = importlib.util.spec_from_file_location("step7_mod", STEP7)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["step7_mod"] = mod
    spec.loader.exec_module(mod)          # module-level constants only; main() is not called
    return mod


def summarise(df, label, band):
    d = df[(df["office_archetype"] == ARCH) & (df["BAND"] == band)]
    wd = d[d["Day_Type"] == "Weekday"].sort_values("Hour")
    we = d[d["Day_Type"] == "Weekend"].sort_values("Hour")
    return {
        "label": label,
        "n_wd": int(wd["n_persons"].iloc[0]), "n_we": int(we["n_persons"].iloc[0]),
        "mean_wd": float(wd["AT_WORK_fraction"].mean()),
        "mean_we": float(we["AT_WORK_fraction"].mean()),
        "max_we": float(we["AT_WORK_fraction"].max()),
        "argmax_we": int(we["AT_WORK_fraction"].to_numpy().argmax()),
    }


def era_mode(m, lookup):
    """The HISTORICAL half of FINDING 6.

    Y2005/2010/2015 are built as `build_office_multiplier(complete_day_types(assembled), ...)`
    (`3rdJ_08A_gen_historical_products_4split.py:237,247`), but Y2022 is built on the RAW stock
    (`3rdJ_07_aug_to_bem_4split.py:869`) with no day-type completion. So the historical years and
    the observed year do not share a frame either. This applies both frames to the SAME 2022 data,
    which isolates the frame from the year.
    """
    stock = pd.read_csv(m.AUG, low_memory=False)
    raw = m.build_office_multiplier(stock, "observed", lookup)
    print("\ncompleting day types (the historical frame) ...", flush=True)
    completed = m.complete_day_types(stock)
    comp = m.build_office_multiplier(completed, "observed", lookup)

    rows = [summarise(raw, "2022 data, RAW stock frame (= shipped Y2022)", "observed"),
            summarise(comp, "2022 data, COMPLETED frame (= historical years)", "observed")]
    print("\n" + "=" * 96)
    print(f"{'frame applied to the SAME 2022 data':<52}{'n_wd':>7}{'n_we':>7}"
          f"{'mean_wd':>10}{'mean_we':>10}")
    print("=" * 96)
    for r in rows:
        print(f"{r['label']:<52}{r['n_wd']:>7}{r['n_we']:>7}{r['mean_wd']:>10.4f}{r['mean_we']:>10.4f}")
    d_we = 100.0 * (rows[1]["mean_we"] - rows[0]["mean_we"]) / max(1e-12, rows[0]["mean_we"])
    d_wd = 100.0 * (rows[1]["mean_wd"] - rows[0]["mean_wd"]) / max(1e-12, rows[0]["mean_wd"])
    print(f"\ncompleted vs raw, same year and same data: weekday {d_wd:+.2f} %, weekend {d_we:+.2f} %")
    print("If these differ, the historical-to-2022 office comparison also crosses a frame boundary,")
    print("independently of the 2030 pool issue -- i.e. the era axis carries THREE frames.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--band", default="hybrid", help="conservative | hybrid | fullyhybrid")
    ap.add_argument("--era", action="store_true",
                    help="run the historical-frame half instead of the 2030-pool half")
    a = ap.parse_args()
    m = load_step7()
    if a.era:
        era_mode(m, pd.read_csv(m.LOOKUP_OFFICE))
        return

    print(f"AUG   : {m.AUG}")
    print(f"D2030 : {m.D2030}")
    lookup = pd.read_csv(m.LOOKUP_OFFICE)

    print("\nloading the 2030 pool ...", flush=True)
    d30 = pd.read_csv(m.D2030, low_memory=False)
    band_slice = d30[d30["BAND"] == a.band].copy()
    shipped = m.build_office_multiplier(band_slice, a.band, lookup)

    print("\nassembling the stock with 2030 activity columns (the residential path) ...", flush=True)
    assembled = m.assemble_2030(a.band)
    viaStock = m.build_office_multiplier(assembled, a.band, lookup)

    print("\nloading the 2022 observed product for reference ...", flush=True)
    obs = pd.read_csv(os.path.join(LEG3, "Step7_docs", "outputs_step7",
                                   "office_presence_multiplier_2022.csv"))
    obs.columns = obs.columns.str.strip()

    rows = [summarise(shipped, f"2030 {a.band} -- FROM POOL (shipped)", a.band),
            summarise(viaStock, f"2030 {a.band} -- FROM STOCK (residential path)", a.band),
            summarise(obs, "2022 observed (from stock)", "observed")]

    print("\n" + "=" * 96)
    print(f"{'source':<44}{'n_wd':>7}{'n_we':>7}{'mean_wd':>10}{'mean_we':>10}{'max_we':>9}{'argmax':>8}")
    print("=" * 96)
    for r in rows:
        print(f"{r['label']:<44}{r['n_wd']:>7}{r['n_we']:>7}{r['mean_wd']:>10.4f}"
              f"{r['mean_we']:>10.4f}{r['max_we']:>9.4f}{r['argmax_we']:>8}")

    pool, stock, o22 = rows[0], rows[1], rows[2]
    print("\n--- verdict ---")
    d_we = 100.0 * (pool["mean_we"] - stock["mean_we"]) / max(1e-12, stock["mean_we"])
    d_wd = 100.0 * (pool["mean_wd"] - stock["mean_wd"]) / max(1e-12, stock["mean_wd"])
    print(f"pool vs stock, same band: weekday {d_wd:+.2f} %, weekend {d_we:+.2f} %")
    r_pool = pool["mean_we"] / max(1e-12, o22["mean_we"])
    r_stock = stock["mean_we"] / max(1e-12, o22["mean_we"])
    print(f"weekend rise vs 2022 observed: from pool x{r_pool:.2f}, from stock x{r_stock:.2f}")
    if abs(d_we) < 5.0:
        print("=> SOURCES AGREE on the weekend mean. The 1:2 vs 2.48:1 sample split does not move")
        print("   it, so FINDING 6 is a DOCUMENTATION matter: the era jump is a property of the")
        print("   2030 diaries themselves, not of which frame the office product was built from.")
    else:
        print("=> SOURCES DISAGREE. The shipped 2030 office product depends on the frame it was")
        print("   built from, so the era axis for office mixes population with behaviour and needs")
        print("   re-specification. This is a manuscript-level decision, NOT a silent fix.")
    print("\nNothing was written. This script is read-only by construction.")


if __name__ == "__main__":
    main()
