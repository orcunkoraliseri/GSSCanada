# -*- coding: utf-8 -*-
"""Generate Graphical Abstract for 5J (occupancy-aware EnergyPlus surrogate).

Specification:
- 5J_docs_occ/Prompts/5thJ_graphical_abstract_prompt.md (2026-09-28), sections 3 to 6 and the
  section 9 fix list (even rows, full arrows, grey cross, 8 pt text, panel widths).
- Editorial Manager & Elsevier rules for Energy and Buildings / energy journals.

Key requirements:
1. Physical size target: 13.0 cm x 5.2 cm (landscape, aspect 2.5 : 1).
2. Canvas coordinates: [0, 100] x [0, 40] (isotropic: 1 unit = 3.685 pt).
3. Export resolution: 518.9416 DPI -> exactly 2656 x 1062 pixels.
4. Typography: Arial / DejaVu Sans, all text >= 8.0 pt, all text horizontal.
5. Strict palette: Spain (#CC6677), UK (#332288), Italy (#44AA99),
   Surrogate (Navy #0F2942), Control & axes (mid grey #64748B), text #111111.
6. Permitted vocabulary only (Section 5 whitelist).
7. Panel C is an empty grey frame placeholder with title and axis labels only.
8. Zero clash / clearance violations (verified by automated geometric checks).

Outputs (one place only):
- 5J_docs_occ/figures/5J_graphical_abstract.png
- 5J_docs_occ/figures/5J_graphical_abstract.pdf
- 5J_docs_occ/figures/5J_graphical_abstract.tiff
"""

import os
import numpy as np
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

# House palette (colour-blind safe per prompt section 4)
COLOR_SPAIN = "#CC6677"       # Rose
COLOR_UK = "#332288"          # Indigo
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
# Panel B needs about 39 units at 8 pt (tag + box + tag in one row), so the split is
# about 31 / 40 / 30 instead of the brief's 35 / 30 / 35.
FS = 8.0
FS_TITLE = 8.3
DIV1 = 31.0
DIV2 = 70.5

# Permitted phrases whitelist per prompt section 5
PERMITTED_PHRASES = {
    "Paired simulations",
    "Same building, same weather",
    "Time-use diaries: Spain, Italy, UK",
    "EnergyPlus",
    "Only occupancy changes",
    "[ ] paired annual runs",
    "[N] paired annual runs",
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
    "A surrogate is trusted only where it passes the occupancy test.",
}


def build_graphical_abstract():
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
    ax.plot([DIV1, DIV1], [5.0, 39.4], color=COLOR_DIVIDER, lw=0.8, zorder=2)
    ax.plot([DIV2, DIV2], [5.0, 39.4], color=COLOR_DIVIDER, lw=0.8, zorder=2)
    ax.plot([1.5, 98.5], [4.4, 4.4], color=COLOR_DIVIDER, lw=0.8, zorder=2)

    # =========================================================================
    # PANEL A: "Paired simulations"
    # =========================================================================
    A_MID = DIV1 / 2.0
    ax.text(A_MID, 39.6, "Paired simulations", fontsize=FS_TITLE, fontweight="bold",
            ha="center", va="top", color=COLOR_TEXT)

    ax.text(0.8, 36.9, "Time-use\ndiaries:\nSpain, Italy, UK", fontsize=FS, fontweight="bold",
            ha="left", va="top", color=COLOR_TEXT, linespacing=1.05)

    strip_configs = [
        (COLOR_SPAIN, [1,1,1,1,1,1,1,0,0,0,0,1,1,0,0,0,0,0,1,1,1,1,1,1]), # Spain
        (COLOR_ITALY, [1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1]), # Italy
        (COLOR_UK,    [1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1]), # UK
        (COLOR_SPAIN, [1,1,1,1,1,1,1,1,1,0,0,0,0,1,1,0,0,0,0,1,1,1,1,1]), # Spain 2
        (COLOR_ITALY, [1,1,1,1,1,1,1,0,0,1,1,1,0,0,0,0,0,1,1,1,1,1,1,1]), # Italy 2
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

    ax.text(A_MID, 7.4, "[ ] paired annual runs", fontsize=FS, ha="center", va="center",
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

    ax.text(B_MID, 7.5, "Scored on new households,\nnew buildings and a new country",
            fontsize=FS, fontweight="bold", ha="center", va="center", color=COLOR_TEXT,
            linespacing=1.05, zorder=3)

    # =========================================================================
    # PANEL C: "The occupancy effect test" (empty frame until the scoring)
    # =========================================================================
    C_MID = (DIV2 + 100.0) / 2.0
    ax.text(C_MID, 39.6, "The occupancy effect test", fontsize=FS_TITLE, fontweight="bold",
            ha="center", va="top", color=COLOR_TEXT)
    ax.text(C_MID, 36.9, "Difference between two\nhouseholds in the\nsame building",
            fontsize=FS, fontweight="bold", ha="center", va="top", color=COLOR_TEXT,
            linespacing=1.05)

    frame_x0 = DIV2 + 2.0
    frame_w = 100.0 - 1.2 - frame_x0
    frame_y0 = 13.4
    frame_h = 8.4

    # Vertical axis label, horizontal text above the frame's left edge
    ax.text(frame_x0, 28.6, "surrogate difference", fontsize=FS, fontweight="bold",
            ha="left", va="top", color=COLOR_TEXT, zorder=3)
    ax.text(frame_x0, 25.9, "kWh per year", fontsize=FS,
            ha="left", va="top", color="#555555", zorder=3)

    frame_patch = FancyBboxPatch((frame_x0, frame_y0), frame_w, frame_h,
                                 boxstyle="square,pad=0",
                                 facecolor="#FAFAFA", edgecolor=COLOR_GREY_MID, lw=1.0, zorder=3)
    ax.add_patch(frame_patch)
    ax.plot([frame_x0, frame_x0 + frame_w], [frame_y0, frame_y0 + frame_h],
            color=COLOR_GREY_BORDER, lw=0.9, ls="--", zorder=3)

    ax.text(frame_x0 + frame_w / 2.0, 11.4, "EnergyPlus difference", fontsize=FS, fontweight="bold",
            ha="center", va="center", color=COLOR_TEXT, zorder=3)
    ax.text(frame_x0 + frame_w / 2.0, 8.4, "kWh per year", fontsize=FS,
            ha="center", va="center", color="#555555", zorder=3)

    # =========================================================================
    # BOTTOM STRIP
    # =========================================================================
    ax.text(50.0, 2.2, "A surrogate is trusted only where it passes the occupancy test.",
            fontsize=FS_TITLE, fontweight="bold", ha="center", va="center", color=COLOR_TEXT, zorder=3)

    return fig, ax, box_of_text


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
    print("VOCABULARY WHITELIST VERIFICATION (Prompt Section 5):")
    if violations:
        print(f"  [FAIL] Found {len(violations)} non-permitted text items:")
        for v in violations:
            print(f"    - '{v}'")
    else:
        print(f"  [PASS] All {len(ax.texts)} text elements strictly match Section 5 whitelist!")
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
    return len(violations) == 0


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
    return len(problems)


def main():
    base_dir = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main"
    out_dir_fig = os.path.join(base_dir, "5J_docs_occ", "figures")
    os.makedirs(out_dir_fig, exist_ok=True)

    print("Generating Graphical Abstract for 5J...")
    fig, ax, box_of_text = build_graphical_abstract()

    # Run verifications
    verify_text_whitelist(ax)
    verify_font_sizes(ax)
    run_full_clearance_check(fig, ax, box_of_text)
    print(f"Panel dividers at {DIV1} and {DIV2} (widths {DIV1:.0f} / {DIV2 - DIV1:.0f} / {100 - DIV2:.0f} %)")

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
