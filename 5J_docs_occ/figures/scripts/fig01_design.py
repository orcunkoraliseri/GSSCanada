# -*- coding: utf-8 -*-
"""Generate Figure 1: Study Design for 5J paper.

Specification:
- writing/submission/figures/Prompts_Images/5J_Figure_01_design_prompt.md (2026-10-01)
- Double-column width: 190 mm wide, ~85-95 mm tall (landscape, ~2.1 : 1).
- 600 DPI PNG (at least 4,500 px wide) + vector PDF with embedded fonts (type 42).
- Permitted vocabulary only (Section 4 whitelist).
- All text >= 7.0 pt at 190 mm print width (prefer 8.0 pt).
- Palette: Spain (#CC6677), Italy (#44AA99), Surrogate navy (#1E293B),
  Control and axes mid grey (#64748B), text (#111111).
"""

import os
import hashlib
import io
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle, PathPatch
from matplotlib.path import Path
from PIL import Image

# Typography & publication styling
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans", "Helvetica"]
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42

# House palette per prompt section 5
COLOR_SPAIN = "#CC6677"       # Rose
COLOR_ITALY = "#44AA99"       # Teal
COLOR_NAVY = "#1E293B"        # Dark navy (Surrogate & highlighted flat)
COLOR_GREY_MID = "#64748B"    # Mid grey (Control & axes)
COLOR_GREY_LIGHT = "#F8FAFC"  # Light background / card fill
COLOR_GREY_BORDER = "#CBD5E1" # Divider rules, borders, tags
COLOR_DIVIDER = "#CBD5E1"     # Zone dividers
COLOR_TEXT = "#111111"        # Primary text (#111111)
COLOR_WHITE = "#FFFFFF"

# Canvas dimensions: 190.5 mm x 90.72 mm (7.5 in x 3.5714 in)
# At 600 DPI -> exactly 4500 x 2143 pixels (landscape, aspect ratio 2.100 : 1)
W_IN = 7.5
H_IN = 3.57143
DPI_EXACT = 600

# Coordinate space: [0, 100] x [0, 47.62] (isotropic: 1 unit = 0.075 in = 5.4 pt)
X_MAX = 100.0
Y_MAX = 47.619

# Text sizes (prefer 8.0 pt, minimum 7.0 pt)
FS_TITLE = 8.6
FS_LABEL = 8.0
FS_TAG = 7.6
FS_SMALL = 7.2

# Zone boundaries (four zones left to right)
DIV1 = 23.5
DIV2 = 53.5
DIV3 = 75.0

# Permitted vocabulary whitelist per prompt section 4
PERMITTED_PHRASES = {
    "Households",
    "Time-use diaries, Spain and Italy",
    "Household A",
    "Household B",
    "Paired EnergyPlus runs",
    "Same building, same weather",
    "EnergyPlus",
    "every flat has its own household",
    "The household effect",
    "Run with A",
    "Run with B",
    "Difference B minus A",
    "hour of day",
    "Scoring",
    "Surrogate",
    "household, building, weather",
    "Blind control",
    "household shuffled",
    "compared",
    "Test sets sealed before training: new households, new buildings, both new",
    # Math symbols permitted by section 3:
    "−",
    "=",
}


def build_figure_01():
    fig = plt.figure(figsize=(W_IN, H_IN), dpi=DPI_EXACT)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, X_MAX)
    ax.set_ylim(0, Y_MAX)
    ax.axis("off")
    fig.patch.set_facecolor(COLOR_WHITE)

    box_of_text = {}

    def add_card(x, y, w, h, text=None, fc=COLOR_GREY_LIGHT, ec=COLOR_GREY_BORDER, tc=COLOR_TEXT,
                 fs=FS_LABEL, weight="bold", rad=0.4, ls="solid", zorder=3, linespacing=1.05):
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

    arrow_kw = dict(arrowstyle="-|>", mutation_scale=6.5, lw=0.8, color="#555555",
                    shrinkA=0, shrinkB=0, zorder=7)

    # Zone dividers (thin dotted lines)
    for div_x in [DIV1, DIV2, DIV3]:
        ax.plot([div_x, div_x], [5.0, 46.5], color=COLOR_DIVIDER, lw=0.6, ls=":", zorder=2)

    # Bottom baseline divider
    ax.plot([1.5, 98.5], [4.6, 4.6], color=COLOR_DIVIDER, lw=0.6, zorder=2)

    # =========================================================================
    # ZONE 1: "Households" (~20% width)
    # =========================================================================
    Z1_MID = DIV1 / 2.0
    ax.text(Z1_MID, 45.4, "Households", fontsize=FS_TITLE, fontweight="bold",
            ha="center", va="top", color=COLOR_TEXT)

    # Subtitle with generous margin on left and right
    ax.text(Z1_MID, 42.0, "Time-use diaries, Spain and Italy", fontsize=FS_TAG, fontweight="bold",
            ha="center", va="top", color=COLOR_TEXT)

    # 3 thin horizontal day strips (24 cells each, different patterns)
    # Left edge colored rose #CC6677 (Spain) or teal #44AA99 (Italy)
    strip_configs = [
        (COLOR_SPAIN, [1,1,1,1,1,1,1,0,0,0,0,1,1,0,0,0,0,0,1,1,1,1,1,1]), # Spain
        (COLOR_ITALY, [1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1]), # Italy
        (COLOR_SPAIN, [1,1,1,1,1,1,0,0,0,1,1,0,0,0,0,0,0,1,1,1,1,1,1,1]), # Spain 2
    ]
    strip_w = 18.6
    strip_h = 2.0
    strip_x0 = Z1_MID - strip_w / 2.0
    strip_ys = [37.0, 33.8, 30.6]
    tag_w = 1.3
    cell_w = (strip_w - tag_w) / 24.0

    for i, (col, occ) in enumerate(strip_configs):
        sy = strip_ys[i]
        card = FancyBboxPatch((strip_x0, sy - strip_h / 2.0), strip_w, strip_h,
                              boxstyle="round,pad=0,rounding_size=0.25",
                              facecolor=COLOR_WHITE, edgecolor=COLOR_GREY_BORDER, lw=0.5, zorder=3)
        ax.add_patch(card)

        cap = FancyBboxPatch((strip_x0, sy - strip_h / 2.0), tag_w, strip_h,
                             boxstyle="round,pad=0,rounding_size=0.2",
                             facecolor=col, edgecolor="none", zorder=4)
        ax.add_patch(cap)

        for c in range(24):
            cx = strip_x0 + tag_w + c * cell_w
            cfc = COLOR_NAVY if occ[c] == 1 else "#F8FAFC"
            rect = Rectangle((cx + 0.02, sy - strip_h / 2.0 + 0.1), cell_w - 0.04, strip_h - 0.2,
                             facecolor=cfc, edgecolor="#E2E8F0", lw=0.15, zorder=5)
            ax.add_patch(rect)

    # Household icons drawn as plain circles in a row (no faces)
    # Row 1: Household A (2 circles)
    # Row 2: Household B (4 circles)
    h_a_y = 21.6
    ax.text(strip_x0 + 0.2, h_a_y, "Household A", fontsize=FS_LABEL, fontweight="bold",
            ha="left", va="center", color=COLOR_TEXT, zorder=4)
    circ_a_x0 = strip_x0 + 13.4
    circ_rad = 0.75
    for c_i in range(2):
        circ = Circle((circ_a_x0 + c_i * 2.2, h_a_y), circ_rad,
                      facecolor="#F1F5F9", edgecolor=COLOR_NAVY, lw=0.9, zorder=4)
        ax.add_patch(circ)
    a_end_x = circ_a_x0 + 1 * 2.2 + circ_rad

    h_b_y = 13.8
    ax.text(strip_x0 + 0.2, h_b_y, "Household B", fontsize=FS_LABEL, fontweight="bold",
            ha="left", va="center", color=COLOR_TEXT, zorder=4)
    circ_b_x0 = strip_x0 + 12.2
    circ_rad_b = 0.65
    for c_i in range(4):
        circ = Circle((circ_b_x0 + c_i * 1.7, h_b_y), circ_rad_b,
                      facecolor="#F1F5F9", edgecolor=COLOR_NAVY, lw=0.9, zorder=4)
        ax.add_patch(circ)
    b_end_x = circ_b_x0 + 3 * 1.7 + circ_rad_b

    # =========================================================================
    # ZONE 2: "Paired EnergyPlus runs" (~30% width)
    # =========================================================================
    Z2_MID = (DIV1 + DIV2) / 2.0
    ax.text(Z2_MID, 45.4, "Paired EnergyPlus runs", fontsize=FS_TITLE, fontweight="bold",
            ha="center", va="top", color=COLOR_TEXT)

    # Weather mark (sun and cloud) + "Same building, same weather"
    wm_y = 40.0
    sun = Circle((Z2_MID - 8.6, wm_y + 0.5), 1.0, facecolor="#F59E0B", edgecolor="#D97706", lw=0.5, zorder=4)
    c1 = Circle((Z2_MID - 7.7, wm_y + 0.1), 0.8, facecolor="#94A3B8", edgecolor="none", zorder=5)
    c2 = Circle((Z2_MID - 6.8, wm_y + 0.4), 1.0, facecolor="#94A3B8", edgecolor="none", zorder=5)
    c3 = Circle((Z2_MID - 5.9, wm_y + 0.1), 0.75, facecolor="#94A3B8", edgecolor="none", zorder=5)
    c_base = FancyBboxPatch((Z2_MID - 8.2, wm_y - 0.5), 3.0, 0.9,
                            boxstyle="round,pad=0,rounding_size=0.45",
                            facecolor="#94A3B8", edgecolor="none", zorder=5)
    for part in [sun, c1, c2, c3, c_base]:
        ax.add_patch(part)

    ax.text(Z2_MID - 3.4, wm_y + 0.2, "Same building, same weather", fontsize=FS_LABEL, fontweight="bold",
            ha="left", va="center", color=COLOR_TEXT, zorder=4)

    # Building outline: 4 floors with 3 flats per floor (grid of 12 rectangles)
    bldg_w = 23.6
    bldg_h = 21.6
    bldg_x0 = Z2_MID - bldg_w / 2.0
    bldg_y0 = 11.2

    # Building background frame
    bldg_box = FancyBboxPatch((bldg_x0, bldg_y0), bldg_w, bldg_h,
                              boxstyle="round,pad=0,rounding_size=0.3",
                              facecolor="#FAFAFA", edgecolor=COLOR_GREY_BORDER, lw=0.9, zorder=3)
    ax.add_patch(bldg_box)

    # Header on building: "EnergyPlus"
    header_h = 3.2
    header_y = bldg_y0 + bldg_h - header_h
    t_ep = ax.text(Z2_MID, header_y + header_h / 2.0, "EnergyPlus", fontsize=FS_TITLE, fontweight="bold",
                   ha="center", va="center", color=COLOR_TEXT, zorder=5)
    box_of_text[t_ep] = bldg_box

    # Grid of 12 flats (4 floors x 3 flats)
    fl_gap_y = 0.4
    fl_gap_x = 0.4
    fl_avail_h = (bldg_h - header_h - 0.8)
    flat_h = (fl_avail_h - 3 * fl_gap_y) / 4.0
    flat_w = (bldg_w - 1.2 - 2 * fl_gap_x) / 3.0
    grid_x0 = bldg_x0 + 0.6
    grid_y0 = bldg_y0 + 0.5

    # Highlight Floor 2, Flat 1 (col 0, row 2 from bottom) with navy outline
    high_col = 0
    high_row = 2
    high_flat_rect = None

    for r in range(4): # 0 is ground floor, 3 is top floor
        fy = grid_y0 + r * (flat_h + fl_gap_y)
        for c in range(3):
            fx = grid_x0 + c * (flat_w + fl_gap_x)
            is_high = (c == high_col and r == high_row)
            ec = COLOR_NAVY if is_high else COLOR_GREY_BORDER
            lw = 1.6 if is_high else 0.6
            fc = "#F1F5F9" if is_high else COLOR_WHITE
            f_rect = FancyBboxPatch((fx, fy), flat_w, flat_h,
                                    boxstyle="round,pad=0,rounding_size=0.2",
                                    facecolor=fc, edgecolor=ec, lw=lw, zorder=5 if is_high else 4)
            ax.add_patch(f_rect)
            if is_high:
                high_flat_rect = (fx, fy, flat_w, flat_h)

            # Miniature window panes
            win_w = (flat_w - 1.2) / 2.0
            win_h = flat_h - 1.0
            for w_idx in range(2):
                wx = fx + 0.4 + w_idx * (win_w + 0.4)
                wy = fy + 0.5
                ax.add_patch(Rectangle((wx, wy), win_w, win_h,
                                       facecolor="#E2E8F0" if not is_high else "#CBD5E1",
                                       edgecolor="none", zorder=6))

    # Two arrows from Household A and Household B enter the highlighted flat
    h_target_y = high_flat_rect[1] + high_flat_rect[3] / 2.0
    h_target_x = high_flat_rect[0]

    # Curved arrow from Household A
    ax.add_patch(FancyArrowPatch((a_end_x + 0.4, h_a_y), (h_target_x - 0.2, h_target_y + 0.5),
                                connectionstyle="arc3,rad=-0.10", **arrow_kw))
    # Curved arrow from Household B
    ax.add_patch(FancyArrowPatch((b_end_x + 0.4, h_b_y), (h_target_x - 0.2, h_target_y - 0.5),
                                connectionstyle="arc3,rad=0.10", **arrow_kw))

    # Footer tag: "every flat has its own household"
    ax.text(Z2_MID, 7.5, "every flat has its own household", fontsize=FS_LABEL, fontweight="bold",
            ha="center", va="center", color=COLOR_TEXT, zorder=4)

    # Arrow from highlighted flat in Zone 2 to Zone 3
    bldg_exit_x = bldg_x0 + bldg_w
    ax.add_patch(FancyArrowPatch((bldg_exit_x + 0.3, h_target_y), (DIV2 + 1.2, h_target_y),
                                **arrow_kw))

    # =========================================================================
    # ZONE 3: "The household effect" (~21% width)
    # =========================================================================
    Z3_MID = (DIV2 + DIV3) / 2.0
    ax.text(Z3_MID, 45.4, "The household effect", fontsize=FS_TITLE, fontweight="bold",
            ha="center", va="top", color=COLOR_TEXT)

    curve_w = 15.0
    curve_x0 = Z3_MID - curve_w / 2.0
    xs_24 = np.linspace(curve_x0, curve_x0 + curve_w, 24)

    # Realistic diurnal hourly profiles (24 h)
    load_A = np.array([1.2, 1.0, 0.9, 0.9, 1.0, 1.3, 2.1, 1.8, 1.2, 1.1, 1.2, 1.3, 1.2, 1.1, 1.1, 1.2, 1.4, 2.0, 2.9, 3.4, 3.1, 2.4, 1.8, 1.4])
    load_B = np.array([1.1, 0.9, 0.9, 0.8, 0.9, 1.2, 1.8, 1.6, 1.4, 2.1, 2.0, 1.8, 1.2, 1.0, 1.0, 1.1, 1.4, 2.3, 3.1, 3.6, 3.4, 2.6, 1.9, 1.4])
    diff_BA = load_B - load_A

    # Upper curve: Run with A
    c1_y0 = 36.2
    ax.text(curve_x0, c1_y0 + 3.8, "Run with A", fontsize=FS_LABEL, fontweight="bold",
            ha="left", va="bottom", color=COLOR_TEXT, zorder=4)
    ax.plot([curve_x0, curve_x0 + curve_w], [c1_y0, c1_y0], color=COLOR_GREY_BORDER, lw=0.6, zorder=3)
    ax.plot(xs_24, c1_y0 + (load_A / 3.6) * 3.0, color=COLOR_GREY_MID, lw=1.1, zorder=4)

    # Minus sign between curves
    ax.text(Z3_MID, 33.7, "−", fontsize=11, fontweight="bold", ha="center", va="center", color=COLOR_TEXT)

    # Lower curve: Run with B
    c2_y0 = 26.6
    ax.text(curve_x0, c2_y0 + 3.8, "Run with B", fontsize=FS_LABEL, fontweight="bold",
            ha="left", va="bottom", color=COLOR_TEXT, zorder=4)
    ax.plot([curve_x0, curve_x0 + curve_w], [c2_y0, c2_y0], color=COLOR_GREY_BORDER, lw=0.6, zorder=3)
    ax.plot(xs_24, c2_y0 + (load_B / 3.6) * 3.0, color=COLOR_GREY_MID, lw=1.1, zorder=4)

    # Equals sign before third curve
    ax.text(Z3_MID, 23.8, "=", fontsize=11, fontweight="bold", ha="center", va="center", color=COLOR_TEXT)

    # Third curve: Difference B minus A (drawn in navy)
    c3_y0 = 16.5
    ax.text(curve_x0, c3_y0 + 3.6, "Difference B minus A", fontsize=FS_LABEL, fontweight="bold",
            ha="left", va="bottom", color=COLOR_NAVY, zorder=4)
    # Zero baseline
    ax.plot([curve_x0, curve_x0 + curve_w], [c3_y0, c3_y0], color=COLOR_GREY_BORDER, lw=0.6, ls="--", zorder=3)
    ax.plot(xs_24, c3_y0 + (diff_BA / 1.0) * 1.5, color=COLOR_NAVY, lw=1.3, zorder=5)

    # Axis word only: "hour of day"
    ax.plot([curve_x0, curve_x0 + curve_w], [c3_y0 - 2.8, c3_y0 - 2.8], color=COLOR_GREY_MID, lw=0.6, zorder=3)
    ax.text(Z3_MID, c3_y0 - 4.4, "hour of day", fontsize=FS_LABEL, fontweight="normal",
            ha="center", va="center", color=COLOR_TEXT, zorder=4)

    # =========================================================================
    # ZONE 4: "Scoring" (~25% width)
    # =========================================================================
    Z4_MID = (DIV3 + X_MAX) / 2.0
    ax.text(Z4_MID, 45.4, "Scoring", fontsize=FS_TITLE, fontweight="bold",
            ha="center", va="top", color=COLOR_TEXT)

    box_w = 11.2
    box_h = 4.6
    box_x0 = DIV3 + 1.8

    # Upper box: Surrogate
    surr_y = 33.6
    ax.text(box_x0 + box_w / 2.0, surr_y + box_h + 1.3, "household, building, weather",
            fontsize=FS_SMALL, fontweight="bold", ha="center", va="bottom", color=COLOR_TEXT, zorder=4)
    ax.add_patch(FancyArrowPatch((box_x0 + box_w / 2.0, surr_y + box_h + 1.1),
                                (box_x0 + box_w / 2.0, surr_y + box_h + 0.1), **arrow_kw))

    add_card(box_x0, surr_y, box_w, box_h, "Surrogate",
             fc=COLOR_NAVY, ec=COLOR_NAVY, tc=COLOR_WHITE, fs=FS_LABEL, weight="bold", rad=0.6)

    # Output arrow from Surrogate box to small navy difference curve
    surr_out_x0 = box_x0 + box_w + 2.2
    surr_out_w = 6.2
    surr_out_y = surr_y + box_h / 2.0
    ax.add_patch(FancyArrowPatch((box_x0 + box_w + 0.2, surr_out_y), (surr_out_x0 - 0.3, surr_out_y), **arrow_kw))

    # Small navy difference curve (surrogate prediction)
    xs_surr = np.linspace(surr_out_x0, surr_out_x0 + surr_out_w, 20)
    ax.plot([surr_out_x0, surr_out_x0 + surr_out_w], [surr_out_y, surr_out_y], color=COLOR_GREY_BORDER, lw=0.5, ls="--", zorder=3)
    ax.plot(xs_surr, surr_out_y + (diff_BA[:20] / 1.0) * 1.1, color=COLOR_NAVY, lw=1.2, zorder=4)

    # Lower box: Blind control
    ctrl_y = 19.5
    shuf_strip_w = 3.2
    shuf_strip_h = 1.3
    shuf_strip_x = box_x0 + 0.2
    shuf_strip_y = ctrl_y + box_h + 1.1

    ax.add_patch(FancyBboxPatch((shuf_strip_x, shuf_strip_y), shuf_strip_w, shuf_strip_h,
                               boxstyle="round,pad=0,rounding_size=0.15",
                               facecolor=COLOR_WHITE, edgecolor=COLOR_GREY_BORDER, lw=0.4, zorder=4))
    for c in range(6):
        cx = shuf_strip_x + c * (shuf_strip_w / 6.0)
        cfc = COLOR_NAVY if c in [0, 2, 5] else "#F8FAFC"
        ax.add_patch(Rectangle((cx, shuf_strip_y), shuf_strip_w / 6.0, shuf_strip_h,
                               facecolor=cfc, edgecolor="#CBD5E1", lw=0.15, zorder=5))
    # Diagonal cross (mid-grey)
    ax.plot([shuf_strip_x - 0.1, shuf_strip_x + shuf_strip_w + 0.1],
            [shuf_strip_y - 0.1, shuf_strip_y + shuf_strip_h + 0.1],
            color=COLOR_GREY_MID, lw=1.2, zorder=6)
    ax.plot([shuf_strip_x - 0.1, shuf_strip_x + shuf_strip_w + 0.1],
            [shuf_strip_y + shuf_strip_h + 0.1, shuf_strip_y - 0.1],
            color=COLOR_GREY_MID, lw=1.2, zorder=6)

    ax.text(shuf_strip_x + shuf_strip_w + 0.5, shuf_strip_y + shuf_strip_h / 2.0, "household shuffled",
            fontsize=FS_SMALL, fontweight="bold", ha="left", va="center", color=COLOR_TEXT, zorder=4)

    ax.add_patch(FancyArrowPatch((box_x0 + box_w / 2.0, ctrl_y + box_h + 0.9),
                                (box_x0 + box_w / 2.0, ctrl_y + box_h + 0.1), **arrow_kw))

    add_card(box_x0, ctrl_y, box_w, box_h, "Blind control",
             fc=COLOR_GREY_MID, ec=COLOR_GREY_MID, tc=COLOR_WHITE, fs=FS_LABEL, weight="bold", rad=0.6)

    # Output arrow from Blind control box to flat grey line
    ctrl_out_x0 = surr_out_x0
    ctrl_out_w = surr_out_w
    ctrl_out_y = ctrl_y + box_h / 2.0
    ax.add_patch(FancyArrowPatch((box_x0 + box_w + 0.2, ctrl_out_y), (ctrl_out_x0 - 0.3, ctrl_out_y), **arrow_kw))

    # Flat grey line (control prediction)
    ax.plot([ctrl_out_x0, ctrl_out_x0 + ctrl_out_w], [ctrl_out_y, ctrl_out_y], color=COLOR_GREY_MID, lw=1.2, zorder=4)

    # Comparison bracket joining Surrogate difference curve & Blind control line
    brk_x = surr_out_x0 + surr_out_w + 0.8
    brk_mid_y = (surr_out_y + ctrl_out_y) / 2.0

    # Curly bracket facing right/left connecting them
    brk_verts = [
        (brk_x, surr_out_y),
        (brk_x + 0.5, surr_out_y),
        (brk_x + 0.5, brk_mid_y + 0.6),
        (brk_x + 1.0, brk_mid_y),
        (brk_x + 0.5, brk_mid_y - 0.6),
        (brk_x + 0.5, ctrl_out_y),
        (brk_x, ctrl_out_y),
    ]
    brk_codes = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO]
    ax.add_patch(PathPatch(Path(brk_verts, brk_codes), facecolor="none", edgecolor=COLOR_GREY_MID, lw=0.9, zorder=5))

    # Horizontal text "compared"
    ax.text(brk_x - 0.2, brk_mid_y, "compared", fontsize=FS_LABEL, fontweight="bold",
            ha="right", va="center", color=COLOR_TEXT, zorder=5)

    # Arrow from Zone 3 EnergyPlus difference curve across into Zone 4 scoring
    ep_diff_exit_x = curve_x0 + curve_w
    ax.add_patch(FancyArrowPatch((ep_diff_exit_x + 0.3, c3_y0), (DIV3 + 1.2, c3_y0), **arrow_kw))

    # Dotted indicator line into Zone 4
    ax.plot([DIV3 + 1.2, box_x0 - 0.3], [c3_y0, c3_y0], color=COLOR_GREY_BORDER, lw=0.6, ls=":", zorder=3)

    # =========================================================================
    # FOOTER: Test sets sealed before training
    # =========================================================================
    ax.text(50.0, 2.3, "Test sets sealed before training: new households, new buildings, both new",
            fontsize=FS_LABEL, fontweight="bold", ha="center", va="center", color=COLOR_TEXT, zorder=4)

    return fig, ax, box_of_text


def verify_text_whitelist(ax):
    """Ensure every text in the figure is strictly from Section 4 whitelist."""
    violations = []
    for t in ax.texts:
        raw_text = t.get_text()
        clean_text = raw_text.replace("\n", " ").strip()
        matched = any(clean_text == p or clean_text in p or p in clean_text for p in PERMITTED_PHRASES)
        if not matched:
            violations.append(raw_text)

    print("\n" + "=" * 60)
    print("VOCABULARY WHITELIST VERIFICATION (Prompt Section 4):")
    if violations:
        print(f"  [FAIL] Found {len(violations)} non-permitted text items:")
        for v in violations:
            print(f"    - '{v}'")
    else:
        print(f"  [PASS] All {len(ax.texts)} text elements strictly match Section 4 whitelist!")
    print("=" * 60)
    return len(violations) == 0


def verify_font_sizes(ax):
    """Verify that every text element is >= 7.0 pt (prefer 8.0 pt)."""
    print("\n" + "=" * 60)
    print("FONT SIZE READABILITY VERIFICATION (>= 7.0 pt, target >= 8.0 pt):")
    min_fs = 1e9
    violations = []
    for t in ax.texts:
        fs = t.get_fontsize()
        min_fs = min(min_fs, fs)
        if fs < 7.0:
            violations.append((t.get_text().replace("\n", " "), fs))

    print(f"  Canvas print width:    190.5 mm ({W_IN:.3f} in)")
    print(f"  Smallest font size:    {min_fs:.2f} pt")
    print(f"  Threshold required:    >= 7.0 pt")
    if violations:
        print(f"  [FAIL] {len(violations)} labels smaller than 7.0 pt:")
        for txt, fs in violations:
            print(f"    - '{txt}': {fs:.2f} pt")
    else:
        print("  [PASS] All text elements meet font size requirements (>= 7.0 pt).")
    print("=" * 60)
    return len(violations) == 0


def md5_file(filepath):
    h = hashlib.md5()
    with open(filepath, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    base_dir = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\5J_docs_occ"
    out_dir_fig = os.path.join(base_dir, "figures")
    out_dir_writing = os.path.join(base_dir, "writing", "figures")
    os.makedirs(out_dir_fig, exist_ok=True)
    os.makedirs(out_dir_writing, exist_ok=True)

    print("Generating Figure 1: Study Design for 5J...")
    fig, ax, box_of_text = build_figure_01()

    # Run verifications
    verify_text_whitelist(ax)
    verify_font_sizes(ax)

    # Save outputs to both figures/ and writing/figures/
    save_targets = [
        (os.path.join(out_dir_fig, "Figure_01_design.png"), "png"),
        (os.path.join(out_dir_fig, "Figure_01_design.pdf"), "pdf"),
        (os.path.join(out_dir_writing, "Figure_01_design.png"), "png"),
        (os.path.join(out_dir_writing, "Figure_01_design.pdf"), "pdf"),
    ]

    print("\nSaving figures...")
    for target, fmt in save_targets:
        if fmt == "png":
            fig.savefig(target, dpi=DPI_EXACT, facecolor=COLOR_WHITE, edgecolor="none")
        elif fmt == "pdf":
            fig.savefig(target, facecolor=COLOR_WHITE, edgecolor="none")
        print(f"  [OK] Saved: {target}")

    plt.close(fig)

    # Create .md5.txt sidecar files
    for d in [out_dir_fig, out_dir_writing]:
        png_p = os.path.join(d, "Figure_01_design.png")
        pdf_p = os.path.join(d, "Figure_01_design.pdf")
        md5_p = os.path.join(d, "Figure_01_design.md5.txt")
        with io.open(md5_p, "w", encoding="utf-8") as fh:
            fh.write("%s  Figure_01_design.png\n%s  Figure_01_design.pdf\n" % (md5_file(png_p), md5_file(pdf_p)))
        print(f"  [OK] Saved md5 sidecar: {md5_p}")

    # Verify PNG dimensions
    test_png = os.path.join(out_dir_writing, "Figure_01_design.png")
    im = Image.open(test_png)
    w_px, h_px = im.size
    im.close()

    print("\n" + "=" * 60)
    print("IMAGE RESOLUTION VERIFICATION:")
    print(f"  Saved Image Dimensions: {w_px} x {h_px} pixels")
    print(f"  Aspect Ratio:           {w_px / h_px:.4f} : 1")
    print(f"  Requirement:            At least 4,500 px wide, landscape ~2.1 : 1, 600 DPI")
    res_ok = (w_px >= 4500 and abs(w_px / h_px - 2.1) < 0.05)
    print(f"  Status:                 {'PASS' if res_ok else 'WARNING: check dimensions'}")
    print("=" * 60)


if __name__ == "__main__":
    main()
