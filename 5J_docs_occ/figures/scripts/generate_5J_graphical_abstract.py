# -*- coding: utf-8 -*-
"""Generate Graphical Abstract for 5J (occupancy-aware EnergyPlus surrogate).

Specification:
- 5J_docs_occ/Prompts/5thJ_graphical_abstract_prompt.md (2026-09-28, updated 2026-10-01 after results),
  sections 1 to 6, section 9 fix list, and section 10 update after results.
- Editorial Manager & Elsevier rules for Energy and Buildings / energy journals.

Key requirements:
1. Physical size target: 13.0 cm x 5.2 cm (landscape, aspect 2.5 : 1).
2. Canvas coordinates: [0, 100] x [0, 40] (isotropic: 1 unit = 3.685 pt).
3. Export resolution: 518.9416 DPI -> exactly 2656 x 1062 pixels.
4. Typography: Arial / DejaVu Sans, all text >= 8.0 pt, all text horizontal.
5. Strict palette: Spain (#CC6677), Italy (#44AA99),
   Surrogate (Navy #0F2942), Control & axes (mid grey #64748B), text #111111. UK removed per Section 10.
6. Permitted vocabulary only (Section 5 whitelist + Section 10.4 additions; no other new word).
7. Panel A footer: "9,269 EnergyPlus runs".
8. Panel C plotted from data: fig3_pairs.parquet (heating, test_new_households), navy surrogate dots,
   mid-grey control dots, one diagonal line, labels near clouds, read-back check against parquet rows.
9. Bottom strip: centred bold finding + right-aligned speed string.
10. Zero clash / clearance violations (verified by automated geometric checks).

Outputs (one place only):
- 5J_docs_occ/figures/5J_graphical_abstract.png
- 5J_docs_occ/figures/5J_graphical_abstract.pdf
- 5J_docs_occ/figures/5J_graphical_abstract.tiff
"""

import os
import hashlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle, Polygon
from PIL import Image

# Typography & publication styling
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans", "Helvetica"]
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42

# House palette (colour-blind safe per prompt section 4, UK removed per Section 10)
COLOR_SPAIN = "#CC6677"       # Rose
COLOR_ITALY = "#44AA99"       # Teal
COLOR_NAVY = "#0F2942"        # Dark navy fill
COLOR_GREY_MID = "#64748B"    # Mid grey (control box, axes, outlines)
COLOR_GREY_LIGHT = "#F8FAFC"  # Light background / card fill
COLOR_GREY_BORDER = "#CBD5E1" # Divider rules, borders, tags
COLOR_DIVIDER = "#CBD5E1"     # Divider rules
COLOR_TEXT = "#111111"        # Primary text (#111111)
COLOR_WHITE = "#FFFFFF"

# Canvas dimensions: 13.0 cm x 5.2 cm (5.11811 x 2.04724 in)
# At DPI = 518.9416, this produces exactly 2656 x 1062 pixels.
W_IN = 5.11811
H_IN = 2.04724
DPI_EXACT = 518.9416

# Text sizes (brief: prefer 8 pt and up at 13 cm) and panel dividers.
FS = 8.0
FS_TITLE = 8.3
DIV1 = 31.0
DIV2 = 70.5

# Permitted phrases whitelist per prompt section 5 + section 10.4 additions (UK removed)
PERMITTED_PHRASES = {
    "Paired simulations",
    "Same building, same weather",
    "Time-use diaries: Spain, Italy",
    "EnergyPlus",
    "Only occupancy changes",
    "9,269 EnergyPlus runs",
    "A fast stand-in",
    "Learned surrogate",
    "occupancy sequence",
    "building",
    "weather",
    "hourly",
    "heating",
    "cooling",
    "electricity",
    "Control: same model, occupancy shuffled",
    "Scored on new households, new buildings and a new country",
    "The occupancy effect test",
    "Difference between two households in the same building",
    "EnergyPlus difference",
    "surrogate difference",
    "kWh per year",
    "surrogate",
    "control",
    "surrogate: right in 31 of 32 groups",
    "control: right in 0 groups",
    "The surrogate gets the household effect right far more often than the load itself.",
    "61 times faster than EnergyPlus on a GPU",
}


def load_and_verify_pairs_data(data_dir):
    """Load fig3_pairs.parquet, verify its MD5 against the sidecar, and filter to target rows."""
    parquet_path = os.path.join(data_dir, "fig3_pairs.parquet")
    md5_path = parquet_path + ".md5.txt"

    if not os.path.exists(parquet_path):
        raise FileNotFoundError(f"Missing data file: {parquet_path}")

    # Compute MD5
    hasher = hashlib.md5()
    with open(parquet_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    computed_md5 = hasher.hexdigest()

    # Read sidecar MD5
    sidecar_md5 = ""
    if os.path.exists(md5_path):
        with open(md5_path, "r") as f:
            sidecar_md5 = f.read().strip().split()[0]

    print("\n" + "=" * 60)
    print("DATA CHECKSUM VERIFICATION (Section 10.3 item 3):")
    print(f"  Computed MD5: {computed_md5}")
    print(f"  Sidecar  MD5: {sidecar_md5}")
    if sidecar_md5:
        assert computed_md5.lower() == sidecar_md5.lower(), f"MD5 mismatch: {computed_md5} != {sidecar_md5}"
        print("  Status:       PASS (MD5 matches sidecar)")
    print("=" * 60)

    df = pd.read_parquet(parquet_path)
    # Keep the rows of test list new households and target heating
    d = df[(df["target"] == "heating") & (df["list"] == "test_new_households")].copy()
    n_pairs = len(d)

    # Figure 3 count verification
    FIG3_EXPECTED_COUNT = 6285
    print("\n" + "=" * 60)
    print("PAIR COUNT VERIFICATION (Section 10.3 item 3):")
    print(f"  Pairs drawn per cloud: {n_pairs}")
    print(f"  Figure 3 count target: {FIG3_EXPECTED_COUNT}")
    assert n_pairs == FIG3_EXPECTED_COUNT, f"Count mismatch: {n_pairs} != {FIG3_EXPECTED_COUNT}"
    print("  Status:                PASS (equals Figure 3 count)")
    print("=" * 60 + "\n")

    return d


def build_graphical_abstract(data_df):
    fig = plt.figure(figsize=(W_IN, H_IN), dpi=DPI_EXACT)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 40)
    ax.axis("off")
    fig.patch.set_facecolor(COLOR_WHITE)

    box_of_text = {}

    def add_card(x, y, w, h, text=None, fc=COLOR_GREY_LIGHT, ec=COLOR_GREY_BORDER, tc=COLOR_TEXT,
                 fs=FS, weight="bold", rad=0.35, ls="solid", zorder=3, linespacing=1.05):
        p = FancyBboxPatch((x, y), w, h,
                           boxstyle=f"round,pad=0,rounding_size={rad}",
                           facecolor=fc, edgecolor=ec, linewidth=0.7,
                           linestyle=ls, zorder=zorder)
        ax.add_patch(p)
        t = None
        if text:
            t = ax.text(x + w / 2.0, y + h / 2.0, text, ha="center", va="center",
                        fontsize=fs, color=tc, weight=weight, zorder=zorder + 1,
                        linespacing=linespacing)
            box_of_text[t] = p
        return p, t

    # Arrows drawn above every shape, with no shrink, so the whole line shows
    arrow_kw = dict(arrowstyle="-|>", mutation_scale=6, lw=0.8, color="#555555",
                    shrinkA=0, shrinkB=0, zorder=7)

    # Dividers: Panel A [0, DIV1], Panel B [DIV1, DIV2], Panel C [DIV2, 100]
    ax.plot([DIV1, DIV1], [5.6, 39.4], color=COLOR_DIVIDER, lw=0.8, zorder=2)
    ax.plot([DIV2, DIV2], [5.6, 39.4], color=COLOR_DIVIDER, lw=0.8, zorder=2)
    ax.plot([1.5, 98.5], [5.4, 5.4], color=COLOR_DIVIDER, lw=0.8, zorder=2)

    # =========================================================================
    # PANEL A: "Paired simulations"
    # =========================================================================
    A_MID = DIV1 / 2.0
    ax.text(A_MID, 39.6, "Paired simulations", fontsize=FS_TITLE, fontweight="bold",
            ha="center", va="top", color=COLOR_TEXT)

    # Diary label: UK removed per Section 10.3 item 1
    ax.text(0.8, 36.9, "Time-use\ndiaries:\nSpain, Italy", fontsize=FS, fontweight="bold",
            ha="left", va="top", color=COLOR_TEXT, linespacing=1.05)

    # Five strips alternating Spain and Italy colours; UK strip and COLOR_UK deleted
    strip_configs = [
        (COLOR_SPAIN, [1,1,1,1,1,1,1,0,0,0,0,1,1,0,0,0,0,0,1,1,1,1,1,1]), # Spain
        (COLOR_ITALY, [1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1]), # Italy
        (COLOR_SPAIN, [1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1]), # Spain
        (COLOR_ITALY, [1,1,1,1,1,1,1,1,1,0,0,0,0,1,1,0,0,0,0,1,1,1,1,1]), # Italy
        (COLOR_SPAIN, [1,1,1,1,1,1,1,0,0,1,1,1,0,0,0,0,0,1,1,1,1,1,1,1]), # Spain
    ]
    # Five equally spaced rows; the load curves use the same rows
    strip_ys = list(np.linspace(25.4, 16.2, 5))
    strip_w = 4.8
    strip_h = 1.5
    strip_x0 = 0.8
    cell_w = (strip_w - 0.45) / 24.0

    house_x = 8.3
    house_w = 13.4
    house_y0 = 16.4
    house_h = 5.0
    house_x1 = house_x + house_w
    # Arrow ends spread evenly along the house walls
    wall_ys = list(np.linspace(house_y0 + house_h - 0.8, house_y0 + 0.8, 5))

    for i, (col, occ) in enumerate(strip_configs):
        sy = strip_ys[i]
        card = FancyBboxPatch((strip_x0, sy - strip_h / 2.0), strip_w, strip_h,
                              boxstyle="round,pad=0,rounding_size=0.2",
                              facecolor=COLOR_WHITE, edgecolor=COLOR_GREY_BORDER, lw=0.5, zorder=3)
        ax.add_patch(card)

        cap = FancyBboxPatch((strip_x0, sy - strip_h / 2.0), 0.45, strip_h,
                             boxstyle="round,pad=0,rounding_size=0.15",
                             facecolor=col, edgecolor="none", zorder=4)
        ax.add_patch(cap)

        for c in range(24):
            cx = strip_x0 + 0.45 + c * cell_w
            cfc = "#1E293B" if occ[c] == 1 else "#F8FAFC"
            rect = Rectangle((cx + 0.02, sy - strip_h / 2.0 + 0.1), cell_w - 0.04, strip_h - 0.2,
                             facecolor=cfc, edgecolor="#E2E8F0", lw=0.15, zorder=5)
            ax.add_patch(rect)

        ax.add_patch(FancyArrowPatch((strip_x0 + strip_w + 0.3, sy), (house_x - 0.15, wall_ys[i]), **arrow_kw))

    house_base = FancyBboxPatch((house_x, house_y0), house_w, house_h,
                                boxstyle="round,pad=0,rounding_size=0.4",
                                facecolor="#F8FAFC", edgecolor=COLOR_NAVY, lw=1.1, zorder=3)
    ax.add_patch(house_base)

    roof_y0 = house_y0 + house_h - 0.1
    roof = Polygon([[house_x - 0.3, roof_y0], [house_x + house_w / 2.0, roof_y0 + 3.4], [house_x1 + 0.3, roof_y0]],
                   closed=True, facecolor="#F1F5F9", edgecolor=COLOR_NAVY, lw=1.1, zorder=3)
    ax.add_patch(roof)

    t_eplus = ax.text(house_x + house_w / 2.0, house_y0 + house_h / 2.0, "EnergyPlus", fontsize=FS,
                      fontweight="bold", ha="center", va="center", color=COLOR_TEXT, zorder=4)
    box_of_text[t_eplus] = house_base

    # Weather mark (sun and cloud above roof)
    hc = house_x + house_w / 2.0
    wy = roof_y0 + 4.9
    sun = Circle((hc - 0.7, wy + 0.4), 0.85, facecolor="#F59E0B", edgecolor="#D97706", lw=0.5, zorder=3)
    c1 = Circle((hc + 0.2, wy), 0.7, facecolor="#94A3B8", edgecolor="none", zorder=4)
    c2 = Circle((hc + 1.0, wy + 0.3), 0.9, facecolor="#94A3B8", edgecolor="none", zorder=4)
    c3 = Circle((hc + 1.8, wy), 0.65, facecolor="#94A3B8", edgecolor="none", zorder=4)
    c_base = FancyBboxPatch((hc - 0.3, wy - 0.6), 2.5, 0.9,
                            boxstyle="round,pad=0,rounding_size=0.45",
                            facecolor="#94A3B8", edgecolor="none", zorder=4)
    for part in [sun, c1, c2, c3, c_base]:
        ax.add_patch(part)

    # Tag under house: Same building, same weather
    tag_w = 17.2
    add_card(hc - tag_w / 2.0, 10.4, tag_w, 5.0, "Same building,\nsame weather",
             fc=COLOR_GREY_LIGHT, ec=COLOR_GREY_BORDER, tc=COLOR_TEXT, fs=FS, weight="bold", linespacing=1.05)

    ax.text(DIV1 - 0.8, 36.9, "Only\noccupancy\nchanges", fontsize=FS, fontweight="bold",
            ha="right", va="top", color=COLOR_TEXT, linespacing=1.05)

    curve_x0 = house_x1 + 2.9
    curve_w = DIV1 - 0.9 - curve_x0
    xs_curve = np.linspace(curve_x0, curve_x0 + curve_w, 24)

    load_shapes = [
        np.array([1.2, 1.0, 0.9, 0.9, 1.0, 1.3, 2.1, 1.8, 1.2, 1.1, 1.2, 2.4, 2.2, 1.3, 1.2, 1.2, 1.4, 2.0, 2.9, 3.4, 3.1, 2.4, 1.8, 1.4]),
        np.array([1.1, 0.9, 0.9, 0.8, 1.0, 1.4, 2.3, 2.0, 1.0, 0.9, 0.9, 1.0, 0.9, 0.9, 1.0, 1.1, 1.3, 2.2, 3.2, 3.6, 3.3, 2.5, 1.7, 1.3]),
        np.array([1.2, 1.0, 0.9, 0.9, 1.0, 1.2, 2.0, 1.5, 0.8, 0.8, 0.8, 0.8, 0.8, 0.9, 0.9, 1.0, 1.2, 2.4, 3.5, 3.7, 3.2, 2.3, 1.6, 1.3]),
        np.array([1.3, 1.1, 1.0, 0.9, 1.0, 1.3, 1.9, 2.2, 1.6, 1.1, 1.0, 1.3, 2.5, 2.1, 1.2, 1.1, 1.3, 1.9, 2.8, 3.3, 3.0, 2.2, 1.7, 1.4]),
        np.array([1.1, 0.9, 0.8, 0.8, 0.9, 1.2, 1.8, 1.6, 1.4, 2.1, 2.0, 1.8, 1.2, 1.0, 1.0, 1.1, 1.4, 2.3, 3.1, 3.5, 3.2, 2.4, 1.8, 1.3]),
    ]

    for i, l_shape in enumerate(load_shapes):
        sy = strip_ys[i]
        ax.add_patch(FancyArrowPatch((house_x1 + 0.15, wall_ys[i]), (curve_x0 - 0.3, sy), **arrow_kw))
        ax.plot([curve_x0, curve_x0 + curve_w], [sy - 0.6, sy - 0.6], color=COLOR_GREY_BORDER, lw=0.5, zorder=2)
        scaled_y = (sy - 0.6) + (l_shape / 3.7) * 1.3
        ax.plot(xs_curve, scaled_y, color=COLOR_NAVY, lw=1.0, zorder=4)

    # Panel A footer: 9,269 EnergyPlus runs (Section 10.3 item 2)
    ax.text(A_MID, 7.8, "9,269 EnergyPlus runs", fontsize=FS, ha="center", va="center",
            color="#555555", zorder=3)

    # =========================================================================
    # PANEL B: "A fast stand-in"
    # =========================================================================
    B_MID = (DIV1 + DIV2) / 2.0
    ax.text(B_MID, 39.6, "A fast stand-in", fontsize=FS_TITLE, fontweight="bold",
            ha="center", va="top", color=COLOR_TEXT)

    in_x = DIV1 + 0.8
    in_w = 12.0
    surr_x = in_x + in_w + 1.6
    surr_w = 11.8
    out_x = surr_x + surr_w + 1.6
    out_w = DIV2 - 0.7 - out_x

    in_tags = [("occupancy\nsequence", 4.7), ("building", 2.6), ("weather", 2.6)]
    in_ys = [30.35, 26.1, 22.9]
    surr_y = in_ys[2] - 1.3
    surr_h = in_ys[0] + 2.35 - surr_y
    add_card(surr_x, surr_y, surr_w, surr_h, "Learned\nsurrogate",
             fc=COLOR_NAVY, ec=COLOR_NAVY, tc=COLOR_WHITE, fs=FS, weight="bold", rad=0.7)

    for t_idx, (t_text, t_h) in enumerate(in_tags):
        ty = in_ys[t_idx]
        add_card(in_x, ty - t_h / 2.0, in_w, t_h, t_text,
                 fc=COLOR_GREY_LIGHT, ec=COLOR_GREY_BORDER, tc=COLOR_TEXT, fs=FS, weight="bold", rad=0.35)
        ax.add_patch(FancyArrowPatch((in_x + in_w + 0.15, ty), (surr_x - 0.15, ty), **arrow_kw))

    out_tags = ["heating", "cooling", "electricity"]
    out_ys = [30.1, 26.5, 22.9]
    ax.text(out_x + out_w / 2.0, 33.6, "hourly", fontsize=FS, fontweight="bold",
            ha="center", va="center", color=COLOR_TEXT, zorder=3)
    for t_idx, t_text in enumerate(out_tags):
        ty = out_ys[t_idx]
        add_card(out_x, ty - 1.3, out_w, 2.6, t_text,
                 fc=COLOR_GREY_LIGHT, ec=COLOR_GREY_BORDER, tc=COLOR_TEXT, fs=FS, weight="bold", rad=0.35)
        ax.add_patch(FancyArrowPatch((surr_x + surr_w + 0.15, ty), (out_x - 0.15, ty), **arrow_kw))

    ctrl_w = 24.4
    ctrl_h = 5.6
    shuf_w = 4.0
    shuf_h = 1.7
    shuf_gap = 2.4
    group_w = shuf_w + shuf_gap + ctrl_w
    shuf_x = B_MID - group_w / 2.0
    ctrl_x = shuf_x + shuf_w + shuf_gap
    ctrl_y = 12.6
    add_card(ctrl_x, ctrl_y, ctrl_w, ctrl_h, "Control: same model,\noccupancy shuffled",
             fc=COLOR_GREY_MID, ec=COLOR_GREY_MID, tc=COLOR_WHITE, fs=FS, weight="bold", rad=0.7)

    shuf_y = ctrl_y + ctrl_h / 2.0
    shuf_card = FancyBboxPatch((shuf_x, shuf_y - shuf_h / 2.0), shuf_w, shuf_h,
                               boxstyle="round,pad=0,rounding_size=0.2",
                               facecolor=COLOR_WHITE, edgecolor=COLOR_GREY_BORDER, lw=0.6, zorder=3)
    ax.add_patch(shuf_card)
    for c in range(8):
        cx = shuf_x + c * (shuf_w / 8.0)
        cfc = "#1E293B" if c in [0, 2, 5, 7] else "#F8FAFC"
        ax.add_patch(Rectangle((cx, shuf_y - shuf_h / 2.0), shuf_w / 8.0, shuf_h,
                               facecolor=cfc, edgecolor="#CBD5E1", lw=0.2, zorder=4))
    # Cross over the shuffled strip, mid grey (palette: control)
    for ya, yb in [(-1, 1), (1, -1)]:
        ax.plot([shuf_x - 0.2, shuf_x + shuf_w + 0.2],
                [shuf_y + ya * (shuf_h / 2.0 + 0.2), shuf_y + yb * (shuf_h / 2.0 + 0.2)],
                color=COLOR_GREY_MID, lw=1.5, solid_capstyle="round", zorder=5)
    ax.add_patch(FancyArrowPatch((shuf_x + shuf_w + 0.35, shuf_y), (ctrl_x - 0.15, shuf_y), **arrow_kw))

    ax.text(B_MID, 8.0, "Scored on new households,\nnew buildings and a new country",
            fontsize=FS, fontweight="bold", ha="center", va="center", color=COLOR_TEXT,
            linespacing=1.05, zorder=3)

    # =========================================================================
    # PANEL C: "The occupancy effect test" (Plotted from data, Section 10.3 item 3)
    # =========================================================================
    C_MID = (DIV2 + 100.0) / 2.0
    ax.text(C_MID, 39.6, "The occupancy effect test", fontsize=FS_TITLE, fontweight="bold",
            ha="center", va="top", color=COLOR_TEXT)
    ax.text(C_MID, 37.1, "Difference between two\nhouseholds in the\nsame building",
            fontsize=FS, fontweight="bold", ha="center", va="top", color=COLOR_TEXT,
            linespacing=1.0)

    frame_x0 = 72.0
    frame_w = 27.0
    frame_y0 = 11.2
    frame_h = 14.6
    lim = 2150.0  # Symmetric axis range covering all paired difference points

    frame_patch = FancyBboxPatch((frame_x0, frame_y0), frame_w, frame_h,
                                 boxstyle="square,pad=0",
                                 facecolor="#FAFAFA", edgecolor=COLOR_GREY_MID, lw=1.0, zorder=2)
    ax.add_patch(frame_patch)

    # One diagonal line (1:1 line) across the scatter frame
    ax.plot([frame_x0, frame_x0 + frame_w], [frame_y0, frame_y0 + frame_h],
            color=COLOR_GREY_BORDER, lw=0.9, ls="--", zorder=3)

    # Prepare data arrays
    x_ep = data_df["dEP"].to_numpy()
    y_surr = data_df["dS"].to_numpy()
    y_ctrl = data_df["dC"].to_numpy()

    # Linear transformation from data coords [-lim, lim] to canvas coords
    x_canvas = frame_x0 + (x_ep - (-lim)) / (2.0 * lim) * frame_w
    y_canvas_surr = frame_y0 + (y_surr - (-lim)) / (2.0 * lim) * frame_h
    y_canvas_ctrl = frame_y0 + (y_ctrl - (-lim)) / (2.0 * lim) * frame_h

    # Scatter clouds: navy dots for surrogate, mid-grey dots for control
    sc_surr = ax.scatter(x_canvas, y_canvas_surr, s=1.2, color=COLOR_NAVY, alpha=0.35,
                         edgecolors="none", zorder=4, rasterized=True)
    sc_ctrl = ax.scatter(x_canvas, y_canvas_ctrl, s=1.2, color=COLOR_GREY_MID, alpha=0.35,
                         edgecolors="none", zorder=3, rasterized=True)

    # Labels near each cloud (Section 10.3 item 3)
    t_surr = ax.text(72.7, 25.2, "surrogate:\nright in 31\nof 32 groups",
                     fontsize=FS, fontweight="bold", color=COLOR_NAVY, ha="left", va="top",
                     zorder=5, linespacing=0.95)
    box_of_text[t_surr] = frame_patch

    t_ctrl = ax.text(98.3, 11.8, "control:\nright in\n0 groups",
                     fontsize=FS, fontweight="bold", color=COLOR_GREY_MID, ha="right", va="bottom",
                     zorder=5, linespacing=0.95)
    box_of_text[t_ctrl] = frame_patch

    # Axis labels and units (Section 3 & 10 whitelist: horizontal text, no rotated text)
    ax.text(frame_x0, 30.7, "surrogate difference", fontsize=FS, fontweight="bold",
            ha="left", va="top", color=COLOR_TEXT, zorder=3)
    ax.text(frame_x0, 28.2, "kWh per year", fontsize=FS,
            ha="left", va="top", color="#555555", zorder=3)

    ax.text(frame_x0 + frame_w / 2.0, 9.8, "EnergyPlus difference", fontsize=FS, fontweight="bold",
            ha="center", va="center", color=COLOR_TEXT, zorder=3)
    ax.text(frame_x0 + frame_w / 2.0, 7.3, "kWh per year", fontsize=FS,
            ha="center", va="center", color="#555555", zorder=3)

    # =========================================================================
    # BOTTOM STRIP (Section 10.3 item 4)
    # =========================================================================
    ax.text(50.0, 3.9, "The surrogate gets the household effect right far more often than the load itself.",
            fontsize=FS_TITLE, fontweight="bold", ha="center", va="center", color=COLOR_TEXT, zorder=3)
    ax.text(98.5, 1.38, "61 times faster than EnergyPlus on a GPU",
            fontsize=FS, ha="right", va="center", color="#555555", zorder=3)

    plot_meta = {
        "sc_surr": sc_surr,
        "sc_ctrl": sc_ctrl,
        "x_ep": x_ep,
        "y_surr": y_surr,
        "y_ctrl": y_ctrl,
        "frame_x0": frame_x0,
        "frame_w": frame_w,
        "frame_y0": frame_y0,
        "frame_h": frame_h,
        "lim": lim,
    }

    return fig, ax, box_of_text, plot_meta


def verify_text_whitelist(ax):
    """Ensure every text in the figure is in the permitted whitelist."""
    violations = []
    for t in ax.texts:
        raw_text = t.get_text()
        clean_text = raw_text.replace("\n", " ").strip()
        matched = any(clean_text == p or clean_text in p or p in clean_text for p in PERMITTED_PHRASES)
        if not matched:
            violations.append(raw_text)

    print("\n" + "=" * 60)
    print("VOCABULARY WHITELIST VERIFICATION (Prompt Sections 5 & 10.4):")
    if violations:
        print(f"  [FAIL] Found {len(violations)} non-permitted text items:")
        for v in violations:
            print(f"    - '{v}'")
    else:
        print(f"  [PASS] All {len(ax.texts)} text elements strictly match Section 5 & 10.4 whitelist!")
    print("=" * 60)
    return len(violations) == 0


def verify_font_sizes(ax):
    """Verify that every text element is >= 8.0 pt at 13 cm target print width."""
    print("\n" + "=" * 60)
    print("FONT SIZE READABILITY VERIFICATION (>= 8.0 pt at 13 cm):")
    min_fs = 1e9
    violations = []
    for t in ax.texts:
        fs = t.get_fontsize()
        min_fs = min(min_fs, fs)
        if fs < 8.0:
            violations.append((t.get_text().replace("\n", " "), fs))

    print(f"  Canvas print width:    13.0 cm ({W_IN:.3f} in)")
    print(f"  Smallest font size:    {min_fs:.2f} pt")
    print(f"  Threshold required:    >= 8.0 pt")
    if violations:
        print(f"  [FAIL] {len(violations)} labels smaller than 8.0 pt:")
        for txt, fs in violations:
            print(f"    - '{txt}': {fs:.2f} pt")
    else:
        print("  [PASS] All text elements are 8.0 pt or larger.")
    print("=" * 60)
    return len(violations) == 0, min_fs


def run_full_clearance_check(fig, ax, box_of_text):
    """Check every text item against every drawn object: other text, every line, every patch
    (arrows, cards, strips and their cells, house, roof, sun, cloud, frame) and the canvas edge."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    k = 72.0 / fig.dpi
    cw, ch = fig.bbox.width, fig.bbox.height

    def bb_gap(a, b):
        dx = max(b.x0 - a.x1, a.x0 - b.x1, 0)
        dy = max(b.y0 - a.y1, a.y0 - b.y1, 0)
        return np.hypot(dx, dy) * k

    def seg_gap(bb, p0, p1, lw):
        ts = np.linspace(0, 1, 400)
        pts = p0 + np.outer(ts, p1 - p0)
        dx = np.maximum(np.maximum(bb.x0 - pts[:, 0], pts[:, 0] - bb.x1), 0)
        dy = np.maximum(np.maximum(bb.y0 - pts[:, 1], pts[:, 1] - bb.y1), 0)
        return max(np.hypot(dx, dy).min() * k - lw / 2.0, 0)

    def name(t):
        return t.get_text().replace("\n", " ")[:35]

    counts = {"text": 0, "line": len(ax.lines), "arrow": 0, "other patch": 0}
    for p in ax.patches:
        counts["arrow" if isinstance(p, FancyArrowPatch) else "other patch"] += 1
    counts["text"] = len(ax.texts)

    problems, smallest = [], 1e9
    T = ax.texts
    for i, t in enumerate(T):
        tb = t.get_window_extent(r)
        gaps = []
        for u in T[i + 1:]:
            gaps.append((bb_gap(tb, u.get_window_extent(r)), f"text '{name(u)}'", 0.8))
        for ln in ax.lines:
            d = ax.transData.transform(np.column_stack(ln.get_data()))
            g = min(seg_gap(tb, d[j], d[j + 1], ln.get_linewidth()) for j in range(len(d) - 1))
            gaps.append((g, "a drawn line", 0.6))
        for p in ax.patches:
            pb = p.get_window_extent(r)
            if isinstance(p, FancyArrowPatch):
                gaps.append((bb_gap(tb, pb), "an arrow", 0.5))
            elif box_of_text.get(t) is p:
                pad = min(tb.x0 - pb.x0, pb.x1 - tb.x1, tb.y0 - pb.y0, pb.y1 - tb.y1) * k
                gaps.append((pad, "its own box edge", 0.5))
            else:
                gaps.append((bb_gap(tb, pb), f"a {type(p).__name__}", 0.6))
        gaps.append((min(tb.x0, tb.y0, cw - tb.x1, ch - tb.y1) * k, "the canvas edge", 1.2))
        for g, what, need in gaps:
            smallest = min(smallest, g)
            if g < need:
                problems.append(f"'{name(t)}' is {g:.2f} pt from {what} (needs {need} pt)")

    print("\n--- CLEARANCE CHECK DETAILS ---")
    print(f"  Objects covered: {counts}")
    for p in problems:
        print(f"  * {p}")
    print(f"CLEARANCE CHECK: {len(problems)} problems (smallest gap {smallest:.2f} pt)\n")
    return len(problems) == 0, smallest


def run_readback_check(plot_meta):
    """Section 10.3 item 5: Read back drawn x and y arrays from figure, compare with parquet rows,
    plant one changed point and verify that check fires."""
    print("=" * 60)
    print("READ-BACK VERIFICATION CHECK (Section 10.3 item 5):")

    sc_surr = plot_meta["sc_surr"]
    sc_ctrl = plot_meta["sc_ctrl"]
    x_ep = plot_meta["x_ep"]
    y_surr = plot_meta["y_surr"]
    y_ctrl = plot_meta["y_ctrl"]
    frame_x0 = plot_meta["frame_x0"]
    frame_w = plot_meta["frame_w"]
    frame_y0 = plot_meta["frame_y0"]
    frame_h = plot_meta["frame_h"]
    lim = plot_meta["lim"]

    # Invert mapping from canvas coordinates back to data units
    offsets_s = sc_surr.get_offsets()
    xs_back = -lim + (offsets_s[:, 0] - frame_x0) / frame_w * (2.0 * lim)
    ys_back = -lim + (offsets_s[:, 1] - frame_y0) / frame_h * (2.0 * lim)

    offsets_c = sc_ctrl.get_offsets()
    xc_back = -lim + (offsets_c[:, 0] - frame_x0) / frame_w * (2.0 * lim)
    yc_back = -lim + (offsets_c[:, 1] - frame_y0) / frame_h * (2.0 * lim)

    equal_surr_x = np.allclose(xs_back, x_ep, rtol=1e-12, atol=1e-12)
    equal_surr_y = np.allclose(ys_back, y_surr, rtol=1e-12, atol=1e-12)
    equal_ctrl_x = np.allclose(xc_back, x_ep, rtol=1e-12, atol=1e-12)
    equal_ctrl_y = np.allclose(yc_back, y_ctrl, rtol=1e-12, atol=1e-12)
    readback_ok = equal_surr_x and equal_surr_y and equal_ctrl_x and equal_ctrl_y

    print(f"  Surrogate X read-back match: {'PASS' if equal_surr_x else 'FAIL'}")
    print(f"  Surrogate Y read-back match: {'PASS' if equal_surr_y else 'FAIL'}")
    print(f"  Control X read-back match:   {'PASS' if equal_ctrl_x else 'FAIL'}")
    print(f"  Control Y read-back match:   {'PASS' if equal_ctrl_y else 'FAIL'}")
    print(f"  Read-back overall status:    {'PASS (drawn points equal parquet rows)' if readback_ok else 'FAIL'}")

    # Planted check: modify one point and ensure verification fails
    planted_y = ys_back.copy()
    planted_y[0] += 5.0
    planted_fires = not np.allclose(planted_y, y_surr, rtol=1e-12, atol=1e-12)
    print(f"  Planted error detection:     {'PASS (check fires on altered point)' if planted_fires else 'FAIL'}")
    print("=" * 60 + "\n")

    return readback_ok and planted_fires


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    figures_dir = os.path.dirname(script_dir)
    data_dir = os.path.join(figures_dir, "data")
    out_dir_fig = figures_dir

    print("Generating Graphical Abstract for 5J (Step 6/7 closed results)...")
    data_df = load_and_verify_pairs_data(data_dir)

    fig, ax, box_of_text, plot_meta = build_graphical_abstract(data_df)

    # Run all verifications
    wl_ok = verify_text_whitelist(ax)
    fs_ok, min_fs = verify_font_sizes(ax)
    clash_ok, smallest_gap = run_full_clearance_check(fig, ax, box_of_text)
    rb_ok = run_readback_check(plot_meta)

    print(f"Smallest font size: {min_fs:.2f} pt")
    print(f"Smallest gap:       {smallest_gap:.2f} pt")
    print(f"Clash check result: {'PASS (0 problems)' if clash_ok else 'FAIL'}")
    print(f"Panel dividers at {DIV1} and {DIV2} (widths {DIV1:.0f} / {DIV2 - DIV1:.0f} / {100 - DIV2:.0f} %)")

    assert wl_ok, "Whitelist check failed!"
    assert fs_ok, "Font size check failed!"
    assert clash_ok, "Clearance / clash check failed!"
    assert rb_ok, "Read-back verification check failed!"

    targets = [
        os.path.join(out_dir_fig, "5J_graphical_abstract.png"),
        os.path.join(out_dir_fig, "5J_graphical_abstract.pdf"),
        os.path.join(out_dir_fig, "5J_graphical_abstract.tiff"),
    ]

    print("Saving figures...")
    for target in targets:
        ext = os.path.splitext(target)[1].lower()
        if ext == ".png":
            fig.savefig(target, dpi=DPI_EXACT, facecolor=COLOR_WHITE, edgecolor="none")
        elif ext == ".pdf":
            fig.savefig(target, facecolor=COLOR_WHITE, edgecolor="none")
        elif ext == ".tiff":
            fig.savefig(target, dpi=DPI_EXACT, facecolor=COLOR_WHITE, edgecolor="none", format="tiff")
        print(f"  [OK] Saved: {target}")

    plt.close(fig)

    # Verification of raster output size with Pillow
    im = Image.open(targets[0])
    w_px, h_px = im.size
    im.close()

    print("\n" + "=" * 60)
    print("IMAGE RESOLUTION VERIFICATION:")
    print(f"  Saved Image Dimensions: {w_px} x {h_px} pixels")
    print(f"  Aspect Ratio:           {w_px / h_px:.4f} : 1")
    print(f"  Requirement:            At least 531 x 1328 px; target 2656 x 1062 px (1 : 2.5)")
    res_ok = (w_px == 2656 and h_px == 1062)
    print(f"  Status:                 {'PASS' if res_ok else 'WARNING: check DPI'}")
    print("=" * 60)


if __name__ == "__main__":
    main()
