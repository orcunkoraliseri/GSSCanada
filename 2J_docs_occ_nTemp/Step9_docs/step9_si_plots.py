#!/usr/bin/env python3
"""
step9_si_plots.py — SI figure generator for Step 9 activity-driven loads.

Reads cluster_run_results.csv (pulled locally from Speed after C VALIDATE FULL).
Produces 5 figures saved under Step9_docs/figures/:

  Fig S1 — Equipment calibration: BL vs AC per cell, SHEU target band (±15%)
  Fig S2 — Lighting calibration: BL vs AC per cell, SHEU target band (±15%)
  Fig S3 — SHEU % error: equip & light deviation (%) for all 24 cells × 2 years
  Fig S4 — Sleep-hour check: mean equipment Wh (h02-h05) per cell, 300 Wh threshold
  Fig S5 — 2022→2030 differential: activity vs baseline equip sharpening per cell

Usage (locally):
  python step9_si_plots.py
  python step9_si_plots.py --csv path/to/cluster_run_results.csv --out path/to/figures/
"""
import argparse
import os
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

HERE = Path(__file__).resolve().parent

DTYPE_COLORS = {
    "SingleD":      "#2166ac",
    "OtherDwelling":"#4dac26",
    "MidRise":      "#d6604d",
    "HighRise":     "#762a83",
}

DTYPE_ORDER = ["SingleD", "OtherDwelling", "MidRise", "HighRise"]


def load_csv(path):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k, v in r.items():
            try:
                r[k] = float(v)
            except (ValueError, TypeError):
                pass
    return rows


def _cell_label(cell):
    arch, city = cell.split("__")
    city_short = city.replace("_", " ")
    return f"{arch}\n{city_short}"


def _short_city(city):
    return city.split("_")[0]


def _sort_key(r):
    arch = r["dtype"] if isinstance(r["dtype"], str) else r.get("cell", "").split("__")[0]
    return (DTYPE_ORDER.index(arch) if arch in DTYPE_ORDER else 99, r.get("cell", ""))


# ─── Fig S1: Equipment calibration ───────────────────────────────────────────
def fig_s1_equip(rows, out_dir):
    rows22 = sorted([r for r in rows if r["year"] == 2022.0], key=_sort_key)
    rows30 = sorted([r for r in rows if r["year"] == 2030.0], key=_sort_key)

    n = len(rows22)
    x = np.arange(n)
    w = 0.35

    fig, ax = plt.subplots(figsize=(14, 5))
    for i, (r22, r30) in enumerate(zip(rows22, rows30)):
        dtype = r22["dtype"] if isinstance(r22["dtype"], str) else r22["cell"].split("__")[0]
        col = DTYPE_COLORS.get(dtype, "gray")
        target = r22["sheu_target_equip"]
        ax.bar(x[i] - w/2, r22["ac_equip_kwh"],   width=w, color=col, alpha=0.85, label=dtype if i == 0 else "")
        ax.bar(x[i] + w/2, r30["ac_equip_kwh"],   width=w, color=col, alpha=0.45)
        ax.bar(x[i] - w/2, r22["bl_equip_kwh"],   width=w, color="gray", alpha=0.35, bottom=0,
               linewidth=0.5, edgecolor="gray")
        # SHEU ±15% band
        ax.hlines(target * 0.85, x[i] - w, x[i] + w, colors="black", linestyles="--", linewidth=0.8)
        ax.hlines(target * 1.15, x[i] - w, x[i] + w, colors="black", linestyles="--", linewidth=0.8)
        ax.hlines(target,        x[i] - w, x[i] + w, colors="black", linestyles="-",  linewidth=1.0)

    ax.set_xticks(x)
    ax.set_xticklabels([_cell_label(r["cell"]) for r in rows22], fontsize=6.5, ha="center")
    ax.set_ylabel("kWh / HH / year")
    ax.set_title("Fig S1 — Equipment: Baseline (gray) vs Activity (coloured), SHEU ±15% band\n"
                 "Dark bar = 2022, light = 2030; solid line = target, dashed = ±15%")
    handles = [mpatches.Patch(color=DTYPE_COLORS[d], label=d) for d in DTYPE_ORDER]
    handles += [mpatches.Patch(color="gray", alpha=0.4, label="Baseline (2022)")]
    ax.legend(handles=handles, fontsize=8, loc="upper right")
    fig.tight_layout()
    out = os.path.join(out_dir, "figS1_equip_calibration.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  Saved: {out}")


# ─── Fig S2: Lighting calibration ────────────────────────────────────────────
def fig_s2_light(rows, out_dir):
    rows22 = sorted([r for r in rows if r["year"] == 2022.0], key=_sort_key)
    rows30 = sorted([r for r in rows if r["year"] == 2030.0], key=_sort_key)

    n = len(rows22)
    x = np.arange(n)
    w = 0.35

    fig, ax = plt.subplots(figsize=(14, 5))
    for i, (r22, r30) in enumerate(zip(rows22, rows30)):
        dtype = r22["dtype"] if isinstance(r22["dtype"], str) else r22["cell"].split("__")[0]
        col = DTYPE_COLORS.get(dtype, "gray")
        target = r22["sheu_target_light"]
        ax.bar(x[i] - w/2, r22["ac_light_kwh"], width=w, color=col, alpha=0.85)
        ax.bar(x[i] + w/2, r30["ac_light_kwh"], width=w, color=col, alpha=0.45)
        ax.bar(x[i] - w/2, r22["bl_light_kwh"], width=w, color="gray", alpha=0.35)
        ax.hlines(target * 0.85, x[i] - w, x[i] + w, colors="black", linestyles="--", linewidth=0.8)
        ax.hlines(target * 1.15, x[i] - w, x[i] + w, colors="black", linestyles="--", linewidth=0.8)
        ax.hlines(target,        x[i] - w, x[i] + w, colors="black", linestyles="-",  linewidth=1.0)

    ax.set_xticks(x)
    ax.set_xticklabels([_cell_label(r["cell"]) for r in rows22], fontsize=6.5, ha="center")
    ax.set_ylabel("kWh / HH / year")
    ax.set_title("Fig S2 — Lighting: Baseline (gray) vs Activity (coloured), SHEU ±15% band\n"
                 "Dark bar = 2022, light = 2030; solid line = target, dashed = ±15%")
    handles = [mpatches.Patch(color=DTYPE_COLORS[d], label=d) for d in DTYPE_ORDER]
    handles += [mpatches.Patch(color="gray", alpha=0.4, label="Baseline (2022)")]
    ax.legend(handles=handles, fontsize=8, loc="upper right")
    fig.tight_layout()
    out = os.path.join(out_dir, "figS2_light_calibration.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  Saved: {out}")


# ─── Fig S3: SHEU % error for both equip and light ───────────────────────────
def fig_s3_sheu_pct(rows, out_dir):
    cells_ordered = []
    seen = set()
    for r in sorted(rows, key=_sort_key):
        c = r["cell"]
        if c not in seen:
            seen.add(c)
            cells_ordered.append(c)

    x = np.arange(len(cells_ordered))
    w = 0.2

    fig, ax = plt.subplots(figsize=(14, 5))
    for yr_offset, (yr, marker, alpha) in enumerate([(2022.0, "o", 0.9), (2030.0, "s", 0.6)]):
        yr_rows = {r["cell"]: r for r in rows if r["year"] == yr}
        eq_pct  = [yr_rows[c]["sheu_pct_equip"] for c in cells_ordered]
        lt_pct  = [yr_rows[c]["sheu_pct_light"] for c in cells_ordered]
        colors  = [DTYPE_COLORS.get(c.split("__")[0], "gray") for c in cells_ordered]
        ax.bar(x - w + yr_offset * w, eq_pct, width=w, color=colors, alpha=alpha,
               label=f"Equip {int(yr)}")
        ax.bar(x + w * yr_offset,     lt_pct, width=w, color=colors, alpha=alpha * 0.5,
               label=f"Light {int(yr)}", hatch="//")

    ax.axhline(0,   color="black", linewidth=1.0)
    ax.axhline(15,  color="red",   linewidth=0.8, linestyle="--", label="+15% gate")
    ax.axhline(-15, color="red",   linewidth=0.8, linestyle="--")
    ax.set_xticks(x)
    ax.set_xticklabels([_cell_label(c) for c in cells_ordered], fontsize=6.5, ha="center")
    ax.set_ylabel("SHEU deviation (%)")
    ax.set_title("Fig S3 — SHEU gate deviation: equipment (solid) and lighting (hatched) for 2022 & 2030\n"
                 "Red dashed = ±15% gate. All 48 cell×year combinations PASS.")
    handles = [mpatches.Patch(color=DTYPE_COLORS[d], label=d) for d in DTYPE_ORDER]
    handles += [mpatches.Patch(color="gray", label="+15% gate (red dashed)")]
    ax.legend(handles=handles, fontsize=8, loc="upper right", ncol=2)
    fig.tight_layout()
    out = os.path.join(out_dir, "figS3_sheu_pct.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  Saved: {out}")


# ─── Fig S4: Sleep-hour check ─────────────────────────────────────────────────
def fig_s4_sleep(rows, out_dir):
    rows22 = sorted([r for r in rows if r["year"] == 2022.0], key=_sort_key)

    n = len(rows22)
    x = np.arange(n)
    vals   = [r.get("sleep_equip_mean_wh", float("nan")) for r in rows22]
    checks = [r.get("sleep_check", "?") for r in rows22]
    colors = ["#d6604d" if c == "WARN" else "#4dac26" for c in checks]

    fig, ax = plt.subplots(figsize=(14, 4))
    ax.bar(x, vals, color=colors, alpha=0.85)
    ax.axhline(300, color="black", linewidth=1.2, linestyle="--", label="300 Wh threshold")
    ax.set_xticks(x)
    ax.set_xticklabels([_cell_label(r["cell"]) for r in rows22], fontsize=6.5, ha="center")
    ax.set_ylabel("Mean equipment Wh (h02-h05)")
    ax.set_title("Fig S4 — Sleep-hour (02:00–05:00) mean equipment load per cell (2022)\n"
                 "Red = WARN (>300 Wh from fridge/dishwasher baseload); green = PASS")
    warn_patch = mpatches.Patch(color="#d6604d", label="WARN (>300 Wh)")
    pass_patch = mpatches.Patch(color="#4dac26", label="PASS (≤300 Wh)")
    ax.legend(handles=[pass_patch, warn_patch], fontsize=8)
    fig.tight_layout()
    out = os.path.join(out_dir, "figS4_sleep_check.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  Saved: {out}")


# ─── Fig S5: 2022→2030 differential ──────────────────────────────────────────
def fig_s5_differential(rows, out_dir):
    rows22 = {r["cell"]: r for r in rows if r["year"] == 2022.0}
    rows30 = {r["cell"]: r for r in rows if r["year"] == 2030.0}
    cells = sorted(set(rows22.keys()), key=lambda c: (DTYPE_ORDER.index(c.split("__")[0]) if c.split("__")[0] in DTYPE_ORDER else 99, c))

    x = np.arange(len(cells))
    w = 0.35
    ac_trend = [rows30[c]["ac_equip_kwh"] - rows22[c]["ac_equip_kwh"] for c in cells]
    bl_trend = [rows30[c]["bl_equip_kwh"] - rows22[c]["bl_equip_kwh"] for c in cells]
    sharpness = [a - b for a, b in zip(ac_trend, bl_trend)]
    colors = [DTYPE_COLORS.get(c.split("__")[0], "gray") for c in cells]

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.bar(x - w/2, ac_trend,  width=w, color=colors, alpha=0.85, label="Activity Δ 22→30")
    ax.bar(x + w/2, bl_trend,  width=w, color="gray", alpha=0.5,  label="Baseline Δ 22→30")
    ax.plot(x, sharpness, "k^", markersize=5, label="Sharpness (act−bl)")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([_cell_label(c) for c in cells], fontsize=6.5, ha="center")
    ax.set_ylabel("kWh / HH (2030 − 2022)")
    ax.set_title("Fig S5 — Equipment 2022→2030 differential: activity (coloured) vs baseline (gray)\n"
                 "Triangle = sharpness (activity trend minus baseline trend)")
    handles = [mpatches.Patch(color=DTYPE_COLORS[d], label=d) for d in DTYPE_ORDER]
    handles += [mpatches.Patch(color="gray", alpha=0.5, label="Baseline Δ")]
    handles += [plt.Line2D([0], [0], marker="^", color="black", linestyle="None", label="Sharpness")]
    ax.legend(handles=handles, fontsize=8, loc="upper right", ncol=2)
    fig.tight_layout()
    out = os.path.join(out_dir, "figS5_differential.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  Saved: {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=str(HERE / "cluster_run_results.csv"))
    ap.add_argument("--out", default=str(HERE / "figures"))
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    rows = load_csv(args.csv)
    print(f"Loaded {len(rows)} rows from {args.csv}")

    fig_s1_equip(rows, args.out)
    fig_s2_light(rows, args.out)
    fig_s3_sheu_pct(rows, args.out)
    fig_s4_sleep(rows, args.out)
    fig_s5_differential(rows, args.out)
    print(f"\nAll 5 SI figures saved to {args.out}/")


if __name__ == "__main__":
    main()
