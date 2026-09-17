# -*- coding: utf-8 -*-
"""Generate Figure 1: Methods workflow diagram for Applied Energy.

Specifications from:
writing/submission/figures/Prompts_Images/Figure_01_workflow_prompt.md

- Double column width: 190 mm, target 600 DPI, white background.
- Colour-blind-safe palette (Okabe-Ito / ColorBrewer Set2).
- Sans-serif labels (Arial / Helvetica / DejaVu Sans).
- Single consistent font size for all box text.
- Single consistent font size for arrow labels.
- Plain rectangle boxes with rounded corners.
- Three horizontal bands: Data, Occupancy model, Building simulation and analysis.
- Exactly 24 boxes, exact verbatim labels.
- Exactly 33 arrows, solid except arrow 32 (dashed with label).
- Curved return arrows for persistence shares (15, 16, 17) to marginal raking (10).
- Side-by-side placement for 14, 15, 16 below 13, and 21, 22 side by side.
"""

import sys
import os
import argparse
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, PathPatch
from matplotlib.path import Path

# -----------------------------------------------------------------------------
# EXACT VERBATIM STRINGS (Mandatory assertion)
# -----------------------------------------------------------------------------
BOX_LABELS = {
    1: "GSS time-use diaries, 2005 to 2022",
    2: "Census microdata, 2021",
    3: "NRCan end-use reference",
    4: "Weather files",
    5: "Building archetype models",
    6: "IESO measured hourly data",
    7: "Diary harmonisation to 30-minute slots",
    8: "Generative day-type model",
    9: "Census-to-diary matching",
    10: "Marginal raking of at-home targets",
    11: "Household aggregation to schedules",
    12: "Activity-driven end-use loads",
    13: "2030 scenario construction",
    14: "Persistence share 1",
    15: "Persistence share 0.5",
    16: "Persistence share 0",
    17: "Household sampling per cell",
    18: "Building simulation",
    19: "Load-shape metrics per cell",
    20: "Stock aggregation to national figure",
    21: "Fixed schedule arm",
    22: "Average survey profile arm",
    23: "Paired difference and confidence interval",
    24: "Measured vs simulated comparison",
}

# Line wraps optimized for box shape while keeping 100% exact text
BOX_WRAPS = {
    1: "GSS time-use\ndiaries,\n2005 to 2022",
    2: "Census\nmicrodata,\n2021",
    3: "NRCan\nend-use\nreference",
    4: "Weather\nfiles",
    5: "Building\narchetype\nmodels",
    6: "IESO\nmeasured\nhourly data",
    7: "Diary\nharmonisation\nto 30-minute\nslots",
    8: "Generative\nday-type\nmodel",
    9: "Census-to-diary\nmatching",
    10: "Marginal\nraking of\nat-home targets",
    11: "Household\naggregation\nto schedules",
    12: "Activity-driven\nend-use loads",
    13: "2030 scenario\nconstruction",
    14: "Persistence\nshare 1",
    15: "Persistence\nshare 0.5",
    16: "Persistence\nshare 0",
    17: "Household\nsampling\nper cell",
    18: "Building\nsimulation",
    19: "Load-shape\nmetrics\nper cell",
    20: "Stock\naggregation to\nnational figure",
    21: "Fixed\nschedule\narm",
    22: "Average survey\nprofile arm",
    23: "Paired difference\nand confidence\ninterval",
    24: "Measured vs\nsimulated\ncomparison",
}

# Verify wraps restore verbatim text exactly
for k, v in BOX_WRAPS.items():
    restored = " ".join(v.split())
    expected = BOX_LABELS[k]
    assert restored == expected, f"Mismatch on box {k}: '{restored}' != '{expected}'"

BAND_TITLES = {
    "band1": "Data",
    "band2": "Occupancy\nmodel",
    "band3": "Building\nsimulation\nand analysis",
}

ARROW_LABEL_32 = "external check, not an input"

# -----------------------------------------------------------------------------
# STYLING & PALETTE (Okabe-Ito colour-blind safe)
# -----------------------------------------------------------------------------
COLOR_BAND1_BG = "#EDF3F8"       # Soft ice blue
COLOR_BAND1_BORDER = "#B8D5E5"
COLOR_BAND1_TITLE = "#0B4569"

COLOR_BAND2_BG = "#FDF6EC"       # Soft warm sand/amber
COLOR_BAND2_BORDER = "#EAD4B6"
COLOR_BAND2_TITLE = "#7B4406"

COLOR_BAND3_BG = "#F3EFF7"       # Soft lavender/purple
COLOR_BAND3_BORDER = "#D6CBE3"
COLOR_BAND3_TITLE = "#4A2E75"

COLOR_BOX_BG = "#FFFFFF"
COLOR_BOX_EDGE = "#2B3A4A"        # Deep slate
COLOR_BOX_TEXT = "#1A202C"

COLOR_ARROW = "#2D3748"           # Slate arrow
COLOR_ARROW_DASHED = "#3E4C5E"
COLOR_ARROW_LABEL = "#2D3748"

FONT_FAMILY = ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"]
FONT_SIZE_BOX = 5.9               # Uniform font size for ALL 24 boxes
FONT_SIZE_ARROW_LABEL = 5.6       # Uniform font size for arrow labels
FONT_SIZE_BAND_TITLE = 8.5        # Band margin titles


def build_figure(dpi=600):
    """Render the workflow diagram to a matplotlib figure."""
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = FONT_FAMILY

    # Canvas dimensions in mm (double-column width = 190 mm)
    WIDTH_MM = 190.0
    HEIGHT_MM = 158.0

    width_in = WIDTH_MM / 25.4
    height_in = HEIGHT_MM / 25.4

    fig = plt.figure(figsize=(width_in, height_in), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, WIDTH_MM)
    ax.set_ylim(0, HEIGHT_MM)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    # -------------------------------------------------------------------------
    # 1. BANDS
    # -------------------------------------------------------------------------
    MARGIN_LEFT = 3.0
    MARGIN_RIGHT = 188.0
    TITLE_W = 23.0
    BAND_X = MARGIN_LEFT
    BAND_W = MARGIN_RIGHT - MARGIN_LEFT

    # Vertical band extents (bottom to top):
    # Band 3: y = 4 to 56 (h = 52)
    # Band 2: y = 60 to 124 (h = 64)
    # Band 1: y = 128 to 155 (h = 27)
    band_defs = [
        ("band1", 128.0, 27.0, COLOR_BAND1_BG, COLOR_BAND1_BORDER, COLOR_BAND1_TITLE),
        ("band2", 60.0, 64.0, COLOR_BAND2_BG, COLOR_BAND2_BORDER, COLOR_BAND2_TITLE),
        ("band3", 4.0, 52.0, COLOR_BAND3_BG, COLOR_BAND3_BORDER, COLOR_BAND3_TITLE),
    ]

    for band_key, by, bh, bg_col, edge_col, title_col in band_defs:
        # Band background patch
        band_patch = FancyBboxPatch(
            (BAND_X, by), BAND_W, bh,
            boxstyle="round,pad=0,rounding_size=2.5",
            facecolor=bg_col, edgecolor=edge_col,
            linewidth=0.8, zorder=1
        )
        ax.add_patch(band_patch)

        # Divider line between title column and diagram
        div_x = BAND_X + TITLE_W
        ax.plot([div_x, div_x], [by + 2.0, by + bh - 2.0],
                color=edge_col, linewidth=0.8, linestyle=":", zorder=2)

        # Band title text on the left margin
        title_text = BAND_TITLES[band_key]
        ax.text(
            BAND_X + TITLE_W / 2.0, by + bh / 2.0,
            title_text,
            ha="center", va="center",
            fontsize=FONT_SIZE_BAND_TITLE,
            fontweight="bold",
            color=title_col,
            linespacing=1.2,
            zorder=3
        )

    # -------------------------------------------------------------------------
    # 2. BOX COORDINATES (cx, cy, width, height)
    # -------------------------------------------------------------------------
    boxes = {}

    # BAND 1: DATA (y in [128, 155])
    # 6 boxes flowing left to right
    b1_cy = 141.5
    boxes[1] = (38.0,  b1_cy, 18.0, 12.5)   # GSS diaries
    boxes[2] = (62.0,  b1_cy, 16.5, 12.5)   # Census microdata
    boxes[3] = (85.0,  b1_cy, 16.0, 12.5)   # NRCan end-use
    boxes[4] = (109.0, b1_cy, 15.0, 12.5)   # Weather files
    boxes[5] = (131.0, b1_cy, 17.5, 12.5)   # Building archetypes
    boxes[6] = (175.0, b1_cy, 16.5, 12.5)   # IESO measured hourly

    # BAND 2: OCCUPANCY MODEL (y in [60, 124])
    # Row 1 (upper flow): 7 -> 8 -> 9 -> 10 -> 12 -> 11
    b2_cy_top = 108.0
    boxes[7]  = (38.0,  b2_cy_top, 18.0, 13.5)  # Harmonisation (4 lines)
    boxes[8]  = (61.0,  b2_cy_top, 16.0, 12.5)  # Generative day-type
    boxes[9]  = (81.0,  b2_cy_top, 16.0, 12.5)  # Census matching
    boxes[10] = (102.0, b2_cy_top, 19.5, 12.5)  # Marginal raking (x: [92.25, 111.75])
    boxes[12] = (124.0, b2_cy_top, 18.0, 12.5)  # Activity end-use loads (x: [115.0, 133.0])
    boxes[11] = (148.0, b2_cy_top, 18.5, 12.5)  # Household aggregation (x: [138.75, 157.25])

    # Box 13 and Boxes 14, 15, 16 directly below 13
    # Placed at cx = 148.0, width 38.0 (x: [129.0, 167.0])
    # Open corridor on right: x in [167.0, 175.0] for Box 11 drop lines!
    # Open corridor on far right: x in [175.0, 188.0] for IESO dashed line!
    b2_13_cx = 148.0
    boxes[13] = (b2_13_cx, 87.0, 38.0, 9.8)
    boxes[14] = (135.0,    73.0, 12.0, 9.8)
    boxes[15] = (148.0,    73.0, 12.0, 9.8)
    boxes[16] = (161.0,    73.0, 12.0, 9.8)

    # BAND 3: BUILDING SIMULATION AND ANALYSIS (y in [4, 56])
    # 17: Sampling per cell
    boxes[17] = (38.0,  35.0, 18.0, 12.5)

    # 21, 22 side by side (comparison arms)
    boxes[21] = (62.0,  35.0, 15.5, 12.5)  # Fixed schedule arm
    boxes[22] = (81.0,  35.0, 16.5, 12.5)  # Average survey profile arm

    # 18: Building simulation
    boxes[18] = (106.0, 35.0, 18.5, 12.5)

    # 19: Load-shape metrics per cell
    boxes[19] = (131.0, 35.0, 18.0, 12.5)

    # Analysis output fan-out (right side of Band 3)
    boxes[20] = (158.0, 47.0, 24.0, 10.0)  # Stock aggregation
    boxes[23] = (158.0, 33.0, 24.0, 11.0)  # Paired difference & CI
    boxes[24] = (158.0, 17.0, 24.0, 11.0)  # Measured vs simulated

    # -------------------------------------------------------------------------
    # 3. DRAW BOXES
    # -------------------------------------------------------------------------
    box_patches = {}
    for box_id, (cx, cy, w, h) in boxes.items():
        rnd = 1.8 if box_id in (14, 15, 16) else 2.2
        patch = FancyBboxPatch(
            (cx - w / 2.0, cy - h / 2.0), w, h,
            boxstyle=f"round,pad=0,rounding_size={rnd}",
            facecolor=COLOR_BOX_BG,
            edgecolor=COLOR_BOX_EDGE,
            linewidth=1.0,
            zorder=4
        )
        ax.add_patch(patch)
        box_patches[box_id] = patch

        # Text label (exact consistent font size for ALL 24 boxes)
        label = BOX_WRAPS[box_id]
        ax.text(
            cx, cy, label,
            ha="center", va="center",
            fontsize=FONT_SIZE_BOX,
            color=COLOR_BOX_TEXT,
            linespacing=1.12,
            zorder=5
        )

    # -------------------------------------------------------------------------
    # 4. DRAW ARROWS (All 33)
    # -------------------------------------------------------------------------
    def get_edge(box_id, direction, offset=0.0):
        """Get anchor point on box boundary."""
        cx, cy, w, h = boxes[box_id]
        if direction == "top":
            return (cx + offset, cy + h / 2.0)
        elif direction == "bottom":
            return (cx + offset, cy - h / 2.0)
        elif direction == "left":
            return (cx - w / 2.0, cy + offset)
        elif direction == "right":
            return (cx + w / 2.0, cy + offset)
        raise ValueError(f"Unknown direction {direction}")

    def draw_straight_arrow(p1, p2, dashed=False, label=None):
        """Draw a straight arrow between two points."""
        ls = "--" if dashed else "-"
        arrow = FancyArrowPatch(
            p1, p2,
            arrowstyle="-|>",
            mutation_scale=9.0,
            color=COLOR_ARROW_DASHED if dashed else COLOR_ARROW,
            linewidth=1.0,
            linestyle=ls,
            zorder=3
        )
        ax.add_patch(arrow)

    def draw_orthogonal_arrow(points, dashed=False, label=None, label_rot=0, label_side="left"):
        """Draw multi-segment orthogonal arrow."""
        ls = "--" if dashed else "-"
        col = COLOR_ARROW_DASHED if dashed else COLOR_ARROW
        xs, ys = zip(*points)
        ax.plot(xs, ys, color=col, linewidth=1.0, linestyle=ls, zorder=3)
        ah = FancyArrowPatch(
            points[-2], points[-1],
            arrowstyle="-|>",
            mutation_scale=9.0,
            color=col,
            linewidth=1.0,
            linestyle=ls,
            zorder=3
        )
        ax.add_patch(ah)

        if label:
            # Place label along the longest segment
            max_len = -1
            best_seg = 0
            for i in range(len(points) - 1):
                slen = ((points[i+1][0] - points[i][0])**2 + (points[i+1][1] - points[i][1])**2)**0.5
                if slen > max_len:
                    max_len = slen
                    best_seg = i
            p_a = points[best_seg]
            p_b = points[best_seg + 1]
            mx = (p_a[0] + p_b[0]) / 2.0
            my = (p_a[1] + p_b[1]) / 2.0

            dx = -1.8 if label_side == "left" else 1.8
            t = ax.text(
                mx + dx, my, label,
                ha="center", va="center",
                rotation=label_rot,
                fontsize=FONT_SIZE_ARROW_LABEL,
                color=COLOR_ARROW_LABEL,
                style="italic",
                zorder=6
            )
            t.set_bbox(dict(facecolor="white", alpha=0.9, edgecolor="none", pad=1.0))

    def draw_curved_arrow(p1, p2, rad=0.25):
        """Draw an arc curved arrow with connectionstyle arc3."""
        arrow = FancyArrowPatch(
            p1, p2,
            arrowstyle="-|>",
            connectionstyle=f"arc3,rad={rad}",
            mutation_scale=9.0,
            color=COLOR_ARROW,
            linewidth=1.0,
            zorder=3
        )
        ax.add_patch(arrow)

    # -------------------------------------------------------------------------
    # Arrow 1: 1 -> 7 (GSS diaries -> Harmonisation)
    # -------------------------------------------------------------------------
    draw_straight_arrow(get_edge(1, "bottom"), get_edge(7, "top"))

    # -------------------------------------------------------------------------
    # Arrow 2: 7 -> 8 (Harmonisation -> Generative day-type)
    # -------------------------------------------------------------------------
    draw_straight_arrow(get_edge(7, "right"), get_edge(8, "left"))

    # -------------------------------------------------------------------------
    # Arrow 3: 7 -> 10 (Harmonisation -> Marginal raking)
    # Overhead track at y = 119.0
    # -------------------------------------------------------------------------
    p1 = get_edge(7, "top", offset=3.0)
    p2 = get_edge(10, "top", offset=-3.0)
    draw_orthogonal_arrow([
        p1,
        (p1[0], 119.0),
        (p2[0], 119.0),
        p2
    ])

    # -------------------------------------------------------------------------
    # Arrow 4: 8 -> 9 (Generative day-type -> Census matching)
    # -------------------------------------------------------------------------
    draw_straight_arrow(get_edge(8, "right"), get_edge(9, "left"))

    # -------------------------------------------------------------------------
    # Arrow 5: 9 -> 10 (Census matching -> Marginal raking)
    # -------------------------------------------------------------------------
    draw_straight_arrow(get_edge(9, "right"), get_edge(10, "left"))

    # -------------------------------------------------------------------------
    # Arrow 6: 2 -> 9 (Census microdata -> Census matching)
    # -------------------------------------------------------------------------
    p1 = get_edge(2, "bottom")
    p2 = get_edge(9, "top")
    draw_orthogonal_arrow([
        p1,
        (p1[0], 126.0),
        (p2[0], 126.0),
        p2
    ])

    # -------------------------------------------------------------------------
    # Arrow 7: 10 -> 11 (Marginal raking -> Household aggregation)
    # Overhead track at y = 117.0
    # -------------------------------------------------------------------------
    p1 = get_edge(10, "top", offset=3.0)
    p2 = get_edge(11, "top", offset=-3.0)
    draw_orthogonal_arrow([
        p1,
        (p1[0], 117.0),
        (p2[0], 117.0),
        p2
    ])

    # -------------------------------------------------------------------------
    # Arrow 8: 10 -> 12 (Marginal raking -> Activity end-use loads)
    # -------------------------------------------------------------------------
    draw_straight_arrow(get_edge(10, "right"), get_edge(12, "left"))

    # -------------------------------------------------------------------------
    # Arrow 9: 12 -> 11 (Activity end-use loads -> Household aggregation)
    # -------------------------------------------------------------------------
    draw_straight_arrow(get_edge(12, "right"), get_edge(11, "left"))

    # -------------------------------------------------------------------------
    # Arrow 10: 3 -> 12 (NRCan end-use -> Activity end-use loads)
    # -------------------------------------------------------------------------
    p1 = get_edge(3, "bottom")
    p2 = get_edge(12, "top")
    draw_orthogonal_arrow([
        p1,
        (p1[0], 126.0),
        (p2[0], 126.0),
        p2
    ])

    # -------------------------------------------------------------------------
    # Arrow 11: 7 -> 13 (Harmonisation -> 2030 scenario construction)
    # Enters left side of 13 at y = 87.0
    # -------------------------------------------------------------------------
    p1 = get_edge(7, "bottom", offset=2.0)
    p2 = get_edge(13, "left")
    draw_orthogonal_arrow([
        p1,
        (p1[0], 87.0),
        p2
    ])

    # -------------------------------------------------------------------------
    # Arrows 12, 13, 14: 13 -> 14, 15, 16 (2030 scenario -> Persistence shares)
    # -------------------------------------------------------------------------
    y_13_bot = boxes[13][1] - boxes[13][3] / 2.0
    draw_straight_arrow((boxes[14][0], y_13_bot), get_edge(14, "top"))
    draw_straight_arrow((boxes[15][0], y_13_bot), get_edge(15, "top"))
    draw_straight_arrow((boxes[16][0], y_13_bot), get_edge(16, "top"))

    # -------------------------------------------------------------------------
    # Arrows 15, 16, 17: Persistence shares 14, 15, 16 -> 10 (Marginal raking)
    # Curved return arrows looping back to box 10
    # -------------------------------------------------------------------------
    p_dest14 = get_edge(10, "bottom", offset=3.5)
    p_dest15 = get_edge(10, "bottom", offset=-0.5)
    p_dest16 = get_edge(10, "bottom", offset=-4.5)
    draw_curved_arrow(get_edge(14, "bottom"), p_dest14, rad=-0.36)
    draw_curved_arrow(get_edge(15, "bottom"), p_dest15, rad=-0.44)
    draw_curved_arrow(get_edge(16, "bottom"), p_dest16, rad=-0.50)

    # -------------------------------------------------------------------------
    # Arrow 18: 11 -> 17 (Household aggregation -> Household sampling per cell)
    # Exits RIGHT of Box 11 into open corridor at x = 168.0, drops to track y = 58.0
    # -------------------------------------------------------------------------
    p1 = get_edge(11, "right", offset=1.0)
    p2 = get_edge(17, "top", offset=-2.0)
    draw_orthogonal_arrow([
        p1,
        (168.0, p1[1]),
        (168.0, 58.0),
        (p2[0], 58.0),
        p2
    ])

    # -------------------------------------------------------------------------
    # Arrow 24: 11 -> 22 (Household aggregation -> Average survey profile arm)
    # Exits RIGHT of Box 11 into open corridor at x = 170.5, drops to track y = 53.5
    # -------------------------------------------------------------------------
    p1 = get_edge(11, "right", offset=-2.0)
    p2 = get_edge(22, "top", offset=2.0)
    draw_orthogonal_arrow([
        p1,
        (170.5, p1[1]),
        (170.5, 53.5),
        (p2[0], 53.5),
        p2
    ])

    # -------------------------------------------------------------------------
    # Arrow 23: 12 -> 21 (Activity end-use loads -> Fixed schedule arm)
    # Drops from bottom of Box 12 at x = 121.0 into track y = 55.5
    # -------------------------------------------------------------------------
    p1 = get_edge(12, "bottom", offset=-3.0)
    p2 = get_edge(21, "top")
    draw_orthogonal_arrow([
        p1,
        (p1[0], 55.5),
        (p2[0], 55.5),
        p2
    ])

    # -------------------------------------------------------------------------
    # Arrow 25: 12 -> 22 (Activity end-use loads -> Average survey profile arm)
    # Drops from bottom of Box 12 at x = 124.0 into track y = 51.5
    # -------------------------------------------------------------------------
    p1 = get_edge(12, "bottom", offset=0.0)
    p2 = get_edge(22, "top", offset=5.0)
    draw_orthogonal_arrow([
        p1,
        (p1[0], 51.5),
        (p2[0], 51.5),
        p2
    ])

    # -------------------------------------------------------------------------
    # Arrow 19: 17 -> 18 (Household sampling -> Building simulation, main path)
    # Runs under 21 & 22 at y = 18.0
    # -------------------------------------------------------------------------
    p1 = get_edge(17, "bottom")
    p2 = get_edge(18, "bottom", offset=-3.0)
    draw_orthogonal_arrow([
        p1,
        (p1[0], 18.0),
        (p2[0], 18.0),
        p2
    ])

    # -------------------------------------------------------------------------
    # Arrow 20: 4 -> 18 (Weather files -> Building simulation)
    # Drops cleanly through gap between Box 10 & 12 at x = 113.0
    # -------------------------------------------------------------------------
    p1 = get_edge(4, "bottom")
    p2 = get_edge(18, "top", offset=1.0)
    draw_orthogonal_arrow([
        p1,
        (p1[0], 126.0),
        (113.0, 126.0),
        (113.0, 49.0),
        (p2[0], 49.0),
        p2
    ])

    # -------------------------------------------------------------------------
    # Arrow 21: 5 -> 18 (Building archetype models -> Building simulation)
    # Drops cleanly through gap between Box 10 & 12 at x = 115.0
    # -------------------------------------------------------------------------
    p1 = get_edge(5, "bottom")
    p2 = get_edge(18, "top", offset=4.0)
    draw_orthogonal_arrow([
        p1,
        (p1[0], 126.0),
        (115.0, 126.0),
        (115.0, 49.0),
        (p2[0], 49.0),
        p2
    ])

    # -------------------------------------------------------------------------
    # Arrow 22: 17 -> 21 (Household sampling -> Fixed schedule arm)
    # -------------------------------------------------------------------------
    draw_straight_arrow(get_edge(17, "right", offset=1.0), get_edge(21, "left", offset=1.0))

    # -------------------------------------------------------------------------
    # Arrow 33: 17 -> 22 (Household sampling -> Average survey profile arm)
    # Loops over 21 at y = 44.0
    # -------------------------------------------------------------------------
    p1 = get_edge(17, "top", offset=3.0)
    p2 = get_edge(22, "top", offset=-3.0)
    draw_orthogonal_arrow([
        p1,
        (p1[0], 44.0),
        (p2[0], 44.0),
        p2
    ])

    # -------------------------------------------------------------------------
    # Arrow 26: 21 -> 18 (Fixed schedule arm -> Building simulation)
    # Runs under 22 at y = 24.0
    # -------------------------------------------------------------------------
    p1 = get_edge(21, "bottom")
    p2 = get_edge(18, "bottom", offset=-7.0)
    draw_orthogonal_arrow([
        p1,
        (p1[0], 24.0),
        (p2[0], 24.0),
        p2
    ])

    # -------------------------------------------------------------------------
    # Arrow 27: 22 -> 18 (Average survey profile arm -> Building simulation)
    # -------------------------------------------------------------------------
    draw_straight_arrow(get_edge(22, "right"), get_edge(18, "left"))

    # -------------------------------------------------------------------------
    # Arrow 28: 18 -> 19 (Building simulation -> Load-shape metrics per cell)
    # -------------------------------------------------------------------------
    draw_straight_arrow(get_edge(18, "right"), get_edge(19, "left"))

    # -------------------------------------------------------------------------
    # Arrow 29: 19 -> 20 (Load-shape metrics -> Stock aggregation)
    # -------------------------------------------------------------------------
    p1 = get_edge(19, "right", offset=2.0)
    p2 = get_edge(20, "left")
    draw_orthogonal_arrow([
        p1,
        (143.0, p1[1]),
        (143.0, p2[1]),
        p2
    ])

    # -------------------------------------------------------------------------
    # Arrow 30: 19 -> 23 (Load-shape metrics -> Paired difference & CI)
    # -------------------------------------------------------------------------
    p1 = get_edge(19, "right")
    p2 = get_edge(23, "left")
    draw_orthogonal_arrow([
        p1,
        (143.0, p1[1]),
        (143.0, p2[1]),
        p2
    ])

    # -------------------------------------------------------------------------
    # Arrow 31: 19 -> 24 (Load-shape metrics -> Measured vs simulated comparison)
    # -------------------------------------------------------------------------
    p1 = get_edge(19, "right", offset=-2.0)
    p2 = get_edge(24, "left")
    draw_orthogonal_arrow([
        p1,
        (143.0, p1[1]),
        (143.0, p2[1]),
        p2
    ])

    # -------------------------------------------------------------------------
    # Arrow 32: 6 -> 24 (IESO measured hourly data -> Measured vs simulated)
    # Long DASHED arrow crossing bands, labelled "external check, not an input"
    # -------------------------------------------------------------------------
    p1 = get_edge(6, "bottom")
    p2 = get_edge(24, "right")
    draw_orthogonal_arrow([
        p1,
        (p1[0], boxes[24][1]),
        p2
    ], dashed=True, label=ARROW_LABEL_32, label_rot=90, label_side="left")

    return fig


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dpi", type=int, default=600, help="DPI for output raster")
    parser.add_argument("--out", type=str, default=None, help="Output file path")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    figures_dir = os.path.dirname(script_dir)
    default_out = os.path.join(figures_dir, "Figure_01_workflow.png")
    out_path = args.out if args.out else default_out

    print(f"Rendering Figure 1 at {args.dpi} DPI...")
    fig = build_figure(dpi=args.dpi)
    fig.savefig(out_path, dpi=args.dpi, facecolor="white", edgecolor="none")
    plt.close(fig)
    print(f"Saved: {out_path}")

    # Also save a copy to Prompts_Images/Figure_01_workflow.png for reference
    prompts_images_out = os.path.join(figures_dir, "Prompts_Images", "Figure_01_workflow.png")
    fig = build_figure(dpi=args.dpi)
    fig.savefig(prompts_images_out, dpi=args.dpi, facecolor="white", edgecolor="none")
    plt.close(fig)
    print(f"Saved: {prompts_images_out}")

    # Also save vector PDF
    pdf_out = os.path.join(figures_dir, "Figure_01_workflow.pdf")
    fig = build_figure(dpi=args.dpi)
    fig.savefig(pdf_out, facecolor="white", edgecolor="none")
    plt.close(fig)
    print(f"Saved: {pdf_out}")

    # REMOVED 2026-09-17 (manager, T47): this block used to also write
    # Figure_01_pipeline.png in the figures directory. That filename belongs to a
    # DIFFERENT, retired figure (the axonometric pipeline overview still archived at
    # writing/figures/Figure_01_pipeline.png, with its own caption in
    # writing/figures/Figure_01_pipeline.md) and is hard-referenced by the archived
    # Building Simulation submission drafts under writing/submission/extra/ and
    # writing/submission/archive/. Writing this figure there silently overwrote the old
    # image on 2026-09-17 and left those captions describing a picture that was no longer
    # at that path. Do not reinstate it: this script may only write Figure_01_workflow.*.


if __name__ == "__main__":
    main()
