#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fig01_pipeline.py -- Figure 1: End-to-End 4-Split Pipeline (Steps 1-9).

Source annotation block: Figure_01_pipeline_4split.md, "Annotations to overlay
afterward". Every string in LABELS below is a verbatim substring of that block
(whitespace-normalized), checked by writing/implementation/f5_figure_check.py (C4).

Run:  py -3 writing/figures/fig01_pipeline.py
Output: writing/figures/Figure_01_pipeline_4split.pdf / .png
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig_style import (SLATE, AMBER, GREY, WHITE,
                        new_fig, box, box_multi, arrow, lane, legend_swatches,
                        footnote, save_both, wrap_text)
from matplotlib.patches import Circle, Rectangle, Ellipse, FancyArrowPatch

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Figure_01_pipeline_4split")

# ---------------------------------------------------------------------------
# LABELS -- every string drawn on this figure, verbatim from the prompt .md's
# "Annotations to overlay afterward" block. f5_figure_check.py C4 checks each
# entry here is a substring of Figure_01_pipeline_4split.md.
# ---------------------------------------------------------------------------
LABELS = [
    "STEP 1", "STEP 2", "STEP 3", "STEP 4", "STEP 5", "STEP 6", "STEP 7", "STEP 8", "STEP 9",
    "Data Collection & Column Selection",
    "GSS columns + hotel source (ISQ QC / CBRE AB monthly series)",
    "Data Harmonization",
    "crosswalk + OR-rule; AT_RETAIL derivation; hotel series harmonization",
    "Merge & Tiling",
    "one tiler list entry appends AT_RETAIL; retail kept in a separate CSV (byte-equality not verified, Table 6)",
    "Three-GSS-Head Transformer",
    "heads = resid / AT_WORK / AT_RETAIL; hotel NOT in model",
    "Archetype Linkage",
    "residential Census linkage (single-channel stage); office NOCxNAICS (two-channel stage)",
    "Forecast 2030 + Hotel Side-Track",
    "GSS channels via drift matrix; hotel SARIMA(1,1,1)(1,1,1,12)",
    "BEM/UBEM Integration",
    "Tag-2 dispatch: apartment REPLACE; office/retail/guest-room MODULATE",
    "BEM Simulation",
    "56/56 cells; 2-city sweep CAN_MTL 6A + CAN_CLG 7A",
    "Activity-Driven End-Use Loads",
    "equipment + lighting; calibrated vs NRCan SCIEU",
    "Inherited from the two-channel stage (Residential AT_HOME, Office AT_WORK)",
    "Added by this study (Retail AT_RETAIL, Hotel non-GSS)",
    "Hotel side-track bypasses the Transformer entirely -- SARIMA, not the 3-head model",
    "Hotel Side-Track",
]


ICON_Z = 6  # icons must draw above the box fill (zorder=3) and STEP-number text (zorder=6)


def icon_db(ax, cx, cy, s=0.15, color=WHITE):
    ax.add_patch(Ellipse((cx, cy + s * 0.8), s * 1.6, s * 0.7, facecolor=color, edgecolor="none", zorder=ICON_Z))
    ax.add_patch(Rectangle((cx - s * 0.8, cy - s * 0.8), s * 1.6, s * 1.6, facecolor=color, edgecolor="none", zorder=ICON_Z))
    ax.add_patch(Ellipse((cx, cy - s * 0.8), s * 1.6, s * 0.7, facecolor=color, edgecolor="none", zorder=ICON_Z))


def icon_link(ax, cx, cy, s=0.15, color=WHITE):
    ax.add_patch(Circle((cx - s * 0.5, cy), s * 0.55, facecolor="none", edgecolor=color, linewidth=1.6, zorder=ICON_Z))
    ax.add_patch(Circle((cx + s * 0.5, cy), s * 0.55, facecolor="none", edgecolor=color, linewidth=1.6, zorder=ICON_Z))


def icon_nodes(ax, cx, cy, s=0.17, color=WHITE):
    pts = [(cx - s, cy - s * 0.6), (cx - s, cy + s * 0.6), (cx, cy), (cx + s, cy - s * 0.6), (cx + s, cy + s * 0.6)]
    for a, b in [(0, 2), (1, 2), (2, 3), (2, 4)]:
        ax.plot([pts[a][0], pts[b][0]], [pts[a][1], pts[b][1]], color=color, linewidth=1.1, zorder=ICON_Z)
    for p in pts:
        ax.add_patch(Circle(p, s * 0.15, facecolor=color, edgecolor="none", zorder=ICON_Z + 1))


def icon_calendar(ax, cx, cy, s=0.15, color=WHITE):
    ax.add_patch(Rectangle((cx - s, cy - s), 2 * s, 2 * s, facecolor="none", edgecolor=color, linewidth=1.4, zorder=ICON_Z))
    ax.plot([cx - s, cx + s], [cy + s * 0.3, cy + s * 0.3], color=color, linewidth=1.1, zorder=ICON_Z)
    ax.plot([cx - s * 0.3, cx - s * 0.3], [cy - s, cy + s], color=color, linewidth=1.0, zorder=ICON_Z)
    ax.plot([cx + s * 0.3, cx + s * 0.3], [cy - s, cy + s], color=color, linewidth=1.0, zorder=ICON_Z)


def icon_house(ax, cx, cy, s=0.16, color=WHITE):
    ax.add_patch(Rectangle((cx - s * 0.7, cy - s), 1.4 * s, 1.3 * s, facecolor="none", edgecolor=color,
                            linewidth=1.4, zorder=ICON_Z))
    ax.plot([cx - s * 0.9, cx, cx + s * 0.9], [cy + s * 0.3, cy + s * 1.1, cy + s * 0.3], color=color,
             linewidth=1.4, zorder=ICON_Z)


def icon_building(ax, cx, cy, s=0.16, color=WHITE):
    ax.add_patch(Rectangle((cx - s * 0.6, cy - s), 1.2 * s, 2 * s, facecolor="none", edgecolor=color,
                            linewidth=1.3, zorder=ICON_Z))
    for k in range(3):
        yy = cy - s * 0.55 + k * s * 0.55
        ax.plot([cx - s * 0.4, cx + s * 0.4], [yy, yy], color=color, linewidth=0.9, zorder=ICON_Z)


def icon_bars(ax, cx, cy, s=0.16, color=WHITE):
    heights = [0.6, 1.0, 0.75]
    for k, hh in enumerate(heights):
        x0 = cx - s * 0.9 + k * s * 0.9
        ax.add_patch(Rectangle((x0, cy - s), s * 0.6, 2 * s * hh, facecolor=color, edgecolor="none", zorder=ICON_Z))


def main():
    W, H = 22.0, 10.0
    fig, ax = new_fig(W, H)

    n = 9
    bw, gap = 2.0, 0.40
    total = n * bw + (n - 1) * gap
    x0 = (W - total) / 2.0
    y_main, bh = 6.5, 1.9
    xs = [x0 + i * (bw + gap) for i in range(n)]

    titles = [
        "Data Collection & Column Selection", "Data Harmonization", "Merge & Tiling",
        "Three-GSS-Head Transformer", "Archetype Linkage", "Forecast 2030 + Hotel Side-Track",
        "BEM/UBEM Integration", "BEM Simulation", "Activity-Driven End-Use Loads",
    ]
    subtitles = [
        "GSS columns + hotel source (ISQ QC / CBRE AB monthly series)",
        "crosswalk + OR-rule; AT_RETAIL derivation; hotel series harmonization",
        "one tiler list entry appends AT_RETAIL; retail kept in a separate CSV (byte-equality not verified, Table 6)",
        "heads = resid / AT_WORK / AT_RETAIL; hotel NOT in model",
        "residential Census linkage (single-channel stage); office NOCxNAICS (two-channel stage)",
        "GSS channels via drift matrix; hotel SARIMA(1,1,1)(1,1,1,12)",
        "Tag-2 dispatch: apartment REPLACE; office/retail/guest-room MODULATE",
        "56/56 cells; 2-city sweep CAN_MTL 6A + CAN_CLG 7A",
        "equipment + lighting; calibrated vs NRCan SCIEU",
    ]
    icons = [icon_db, None, icon_link, icon_nodes, None, icon_calendar, icon_house, icon_building, icon_bars]

    # box 1,2,8,9 = warm-grey (shared/untouched); 3,4,5,7 = split channel colours; 6 = slate (GSS only)
    for i in range(n):
        x = xs[i]
        title_wrapped = wrap_text(titles[i], 15)
        if i in (0, 1, 7, 8):
            box(ax, x, y_main, bw, bh, title_wrapped, facecolor=GREY, fontsize=10.5)
        elif i == 2:  # Merge & Tiling: half slate (resid+office) half amber (retail)
            box_multi(ax, x, y_main, bw, bh, [(0.5, SLATE), (0.5, AMBER)], title_wrapped, fontsize=10.5)
        elif i == 3:  # 3-Head Transformer: two heads slate, one amber
            box_multi(ax, x, y_main, bw, bh, [(0.667, SLATE), (0.333, AMBER)], title_wrapped, fontsize=9.6)
        elif i == 4:  # Archetype Linkage: resid+office slate, retail(+hotel) amber
            box_multi(ax, x, y_main, bw, bh, [(0.5, SLATE), (0.5, AMBER)], title_wrapped, fontsize=10.5)
        elif i == 5:
            box(ax, x, y_main, bw, bh, title_wrapped, facecolor=SLATE, fontsize=9.6)
        elif i == 6:  # BEM/UBEM Integration: mixed
            box_multi(ax, x, y_main, bw, bh, [(0.5, SLATE), (0.5, AMBER)], title_wrapped, fontsize=10.5)

        ax.text(x + 0.10, y_main + bh - 0.13, "STEP %d" % (i + 1), ha="left", va="top",
                 fontsize=8.0, color=WHITE, weight="bold", zorder=6)
        if icons[i] is not None:
            icons[i](ax, x + bw - 0.24, y_main + bh - 0.28)

        if i < n - 1:
            arrow(ax, (x + bw, y_main + bh / 2.0), (xs[i + 1], y_main + bh / 2.0))

        # caption block directly beneath the box, in the whitespace above the hotel lane
        cap = wrap_text(subtitles[i], 24)
        ax.text(x + bw / 2.0, y_main - 0.25, cap, ha="center", va="top", fontsize=7.3,
                 color="#3A3D40", linespacing=1.25)

    # Hotel side-track lane: begins under box 2 (i=1), passes under box 4 (i=3), rejoins at box 5 (i=4)
    lane_y, lane_h = 1.15, 1.30
    lane_x0 = xs[1] - 0.15
    lane_x1 = xs[4] + bw * 0.15
    lane(ax, lane_x0, lane_y, lane_x1 - lane_x0, lane_h, edgecolor=AMBER, dashed=True)
    ax.text(lane_x0 + 0.18, lane_y + lane_h - 0.22, "Hotel Side-Track", ha="left", va="top",
             fontsize=9.5, color=AMBER, weight="bold")

    # drop from box 2 bottom into the lane
    arrow(ax, (xs[1] + bw / 2.0, y_main - 1.0), (xs[1] + bw / 2.0, lane_y + lane_h - 0.05),
          color=AMBER, lw=1.4)
    # bypass curve routing under/around box 4 only
    bypass_start = (xs[2] + bw * 0.5, lane_y + lane_h / 2.0)
    bypass_end = (xs[4] - 0.05, lane_y + lane_h / 2.0)
    fap = FancyArrowPatch(bypass_start, bypass_end, connectionstyle="arc3,rad=-0.35", arrowstyle="-|>",
                           color=AMBER, linewidth=1.6, mutation_scale=14, zorder=2)
    ax.add_patch(fap)
    ax.text((bypass_start[0] + bypass_end[0]) / 2.0, lane_y + lane_h / 2.0 + 0.32,
             "bypass: routes under STEP 4 only", ha="center", va="bottom", fontsize=7.0, color=AMBER)
    # rejoin main chain at box 5
    arrow(ax, (lane_x1 - 0.10, lane_y + lane_h - 0.10), (xs[4] + bw / 2.0, y_main - 1.0), color=AMBER, lw=1.4,
          connectionstyle="arc3,rad=0.25")

    footnote(ax, W, lane_y - 0.22,
             wrap_text("Hotel side-track bypasses the Transformer entirely -- SARIMA, not the 3-head model", 90),
             fontsize=8.2, color=AMBER)

    legend_swatches(ax, x0, 0.30,
                     [(SLATE, "Inherited from the two-channel stage (Residential AT_HOME, Office AT_WORK)"),
                      (AMBER, "Added by this study (Retail AT_RETAIL, Hotel non-GSS)")],
                     sw=0.26, sh=0.20, gap_x=9.6, fontsize=8.4)

    save_both(fig, OUT)


if __name__ == "__main__":
    main()
