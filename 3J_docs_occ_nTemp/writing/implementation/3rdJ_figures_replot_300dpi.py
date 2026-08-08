#!/usr/bin/env python3
"""Re-render the five Step-9 result figures at publication resolution.

WHY. Figures 7 to 11 of the manuscript are the paper's only data figures and every one of them is
**140 dpi** (`3rdJ_09_activityDrivenLoads_4split.py:870`, `fig.savefig(..., dpi=140)`). Elsevier's
artwork minimum for combination art is higher than that, and the previous paper of this line went
into review with 13 of 16 figures under 600 dpi. This script is the fix.

WHAT IT DOES NOT DO, and this is the whole design.

  * It does not re-simulate. It reads the frozen Step-8 §8E aggregate CSVs, the same four files the
    shipped Step-9 run read, and rebuilds the same four frames with the same builder functions
    imported from the Step-9 module itself. No plotting code is copied or reimplemented here.
  * It does not overwrite anything frozen. Output goes to a NEW directory,
    `outputs_step9_deliverable/figures_300dpi/`. The 140 dpi originals stay exactly where they are,
    with the md5s the freeze document already registers.
  * It does not evaluate gates, does not write CSVs, and does not touch `step9_report.html`. Nothing
    that carries a number is rewritten. Only the rendering resolution of five PNGs changes.

The claim "same figure, more pixels" is not asserted here. It is tested separately by
`improvements/v5/f6_figure_replot_equivalence.py`, which downsamples each new figure back to the
original's pixel dimensions and compares. Run that before copying anything into `writing/figures/`.

    py -3 writing/implementation/3rdJ_figures_replot_300dpi.py [--dpi 300]
"""
import argparse
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))            # 3J_docs_occ_nTemp/
STEP9_DIR = os.path.join(ROOT, "Leg3_4-split", "Step9_docs")
STEP9_PY = os.path.join(STEP9_DIR, "3rdJ_09_activityDrivenLoads_4split.py")
# 🔴 `agg`, NOT `agg_deliverable`, is what the Step-9 script's own `DEFAULT_AGG` points at
# (`3rdJ_09_activityDrivenLoads_4split.py:63`), and it is the SUPERSEDED arm. The canonical
# deliverable was built from `agg_deliverable/` (both stamped 2026-08-06 00:05; `agg/` is from
# 2026-07-30). Running this script on the script's own default produced five figures whose
# EUI values, peak hours and 16 `verdict_asmodelled` cells did not match the shipped deliverable.
# A default inside a pipeline script is not provenance. Do not "simplify" this back to DEFAULT_AGG.
AGG_DIR = os.path.join(ROOT, "Leg3_4-split", "Step8_docs", "outputs_step8", "agg_deliverable")
OUT_ROOT = os.path.join(STEP9_DIR, "outputs_step9_deliverable")
OUT_SUBDIR = "figures_hires"

# 🔴 600, not 300. `RV10` item 7 reports Elsevier's artwork minimums as 300 dpi for halftones,
# **500 dpi for combination art**, and 1000 dpi for bitmapped line drawings. These five figures are
# line plots with embedded text, which is combination art, so 300 dpi would have shipped a figure
# that still fails the stated minimum. 600 clears 500 with margin and matches the "600+ dpi"
# recommendation in that report's own blocking list. A vector PDF is written alongside each PNG,
# because Elsevier prefers vector for plots and Figures 1 to 6 already ship both.
DEFAULT_DPI = 600


def load_step9():
    """Import the Step-9 module by path. Its name starts with a digit, so it is not importable
    by name, and copying its plotting code here would defeat the point of the exercise."""
    spec = importlib.util.spec_from_file_location("step9_4split", STEP9_PY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["step9_4split"] = mod
    spec.loader.exec_module(mod)
    return mod


def main(dpi):
    if not os.path.isdir(AGG_DIR):
        raise SystemExit("[FAIL] §8E aggregate directory not found: %s" % AGG_DIR)
    s9 = load_step9()

    # Redirect _save: same figures, same filenames, new directory, new dpi. Everything else about
    # the original _save is preserved, bbox_inches included, because the framing must not move.
    staging = os.path.join(OUT_ROOT, "_replot_tmp")
    real_out = os.path.join(OUT_ROOT, OUT_SUBDIR)
    os.makedirs(real_out, exist_ok=True)

    written = []

    def _save(fig, outdir, fname):
        p = os.path.join(real_out, fname)
        fig.savefig(p, dpi=dpi, bbox_inches="tight")
        # the vector twin, same figure, no resolution to be below a minimum
        fig.savefig(os.path.splitext(p)[0] + ".pdf", bbox_inches="tight")
        s9.plt.close(fig)
        written.append(p)
        return p

    s9._save = _save

    print("=== Step-9 figure replot | agg = %s | dpi = %d ===" % (AGG_DIR, dpi))
    d = s9.load_agg(AGG_DIR)
    annual, peak, diur, meta = d["annual"], d["peak"], d["diurnal"], d["meta"]
    print("  loaded %d cells, %d annual rows" % (len(meta), len(annual)))

    # The exact build order of main(), including the SCEN_OF update between build_eui and
    # build_loadshape. Reordering these would silently change what the figures plot.
    eui = s9.build_eui(annual, meta)
    s9.SCEN_OF.update(dict(zip(meta["cell_tag"], meta["scenario"])))
    ls = s9.build_loadshape(peak, diur)
    scen = s9.build_scenario(eui, annual)
    lon = s9.build_longitudinal(eui, ls)
    print("  tables: eui=%d loadshape=%d scenario=%d longitudinal=%d"
          % (len(eui), len(ls), len(scen), len(lon)))

    s9.fig_eui(eui, staging)
    s9.fig_diurnal(diur, staging)
    s9.fig_peakhour(ls, staging)
    s9.fig_scenario(scen, staging)
    s9.fig_longitudinal(lon, staging)

    print("\n  %d figure(s) written to %s"
          % (len(written), os.path.relpath(real_out, ROOT).replace("\\", "/")))
    for p in written:
        print("    %s" % os.path.basename(p))
    print("\n  NOT YET USABLE. Run improvements/v5/f6_figure_replot_equivalence.py and read its")
    print("  verdict before copying any of these into writing/figures/.")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dpi", type=int, default=DEFAULT_DPI)
    sys.exit(main(ap.parse_args().dpi))
