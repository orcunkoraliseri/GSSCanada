#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fig04_exclusivity.py -- Figure 4: Exclusivity Projection (Independent Heads to One-Hot Decode).

Source annotation block: Figure_04_exclusivity_projection.md. The individual raw-probability
bar heights on the left/right clusters are purely illustrative (the prompt's SCENE calls for
"a few bars shown overlapping ... to suggest raw conflicts" with no numeric value attached);
no number is drawn there. The only numbers on this figure are the two ISR values, both stated
verbatim in the annotation block.

Run:  py -3 writing/figures/fig04_exclusivity.py
Output: writing/figures/Figure_04_exclusivity_projection.pdf / .png
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig_style import SLATE, AMBER, TEAL, GREY, INK, WHITE, new_fig, box, arrow, footnote, save_both, wrap_text
from matplotlib.patches import Rectangle

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Figure_04_exclusivity_projection")

# ---------------------------------------------------------------------------
# LABELS -- every string drawn, verbatim from Figure_04_exclusivity_projection.md's
# "Annotations to overlay afterward" block. Checked by f5_figure_check.py C4.
# ---------------------------------------------------------------------------
LABELS = [
    "Independent binary heads (resid / AT_WORK / AT_RETAIL), calibrated logit-adjusted sigmoid outputs",
    "Threshold-Normalized Argmax Projection (decode-time)",
    "Mutually exclusive one-hot decode, 100% physical consistency",
    "Impossible-State Rate (ISR): slots with more than one of AT_HOME, AT_WORK, AT_RETAIL active",
    "raw ISR <= 0.5%",
    "0% after projection",
    "ISR <= 0.5% raw; = 0% after the decode-time projection (dr_L3-12)",
]


def bar_cluster(ax, cx, heights, colors, thresh, w=0.55, gap=0.25, base_y=0.0, scale=2.6):
    n = len(heights)
    total_w = n * w + (n - 1) * gap
    x0 = cx - total_w / 2.0
    for i, (h, c) in enumerate(zip(heights, colors)):
        bx = x0 + i * (w + gap)
        ax.add_patch(Rectangle((bx, base_y), w, h * scale, facecolor=c, edgecolor=INK, linewidth=1.0, zorder=4))
    if thresh is not None:
        ax.plot([x0 - 0.25, x0 + total_w + 0.25], [base_y + thresh * scale, base_y + thresh * scale], color=INK,
                 linewidth=1.1, linestyle="dashed", zorder=5)
    return x0, x0 + total_w


def main():
    W, H = 18.0, 7.0
    fig, ax = new_fig(W, H)

    base_y = 3.55
    colors = [SLATE, TEAL, GREY]

    # Left cluster: raw, conflicting (two bars co-occur above the dashed threshold)
    lx0, lx1 = bar_cluster(ax, 3.1, [0.78, 0.70, 0.30], colors, thresh=0.5, base_y=base_y)
    ax.text((lx0 + lx1) / 2.0, base_y + 2.6 * 1.0 + 0.15,
             wrap_text("Independent binary heads (resid / AT_WORK / AT_RETAIL), calibrated "
                       "logit-adjusted sigmoid outputs", 30),
             ha="center", va="bottom", fontsize=7.6, color=INK, linespacing=1.25)

    # Projection box
    box(ax, 6.6, base_y + 0.2, 3.6, 1.6, wrap_text("Threshold-Normalized Argmax Projection (decode-time)", 20),
        facecolor=AMBER, fontsize=8.6)
    arrow(ax, (lx1 + 0.3, base_y + 1.0), (6.6, base_y + 1.0))
    arrow(ax, (10.2, base_y + 1.0), (11.6, base_y + 1.0))

    # Right cluster: mutually exclusive, one-hot
    rx0, rx1 = bar_cluster(ax, 13.3, [0.0, 0.92, 0.0], colors, thresh=None, base_y=base_y)
    ax.text((rx0 + rx1) / 2.0, base_y + 2.6 * 1.0 + 0.15,
             wrap_text("Mutually exclusive one-hot decode, 100% physical consistency", 26),
             ha="center", va="bottom", fontsize=7.6, color=INK, linespacing=1.25)

    ax.text(9.5, base_y - 0.30,
             wrap_text("Impossible-State Rate (ISR): slots with more than one of AT_HOME, AT_WORK, "
                       "AT_RETAIL active", 78),
             ha="center", va="top", fontsize=7.6, color=INK, linespacing=1.3)

    # Before/after ISR mini bar-chart pair
    mini_y = 1.55
    mbw = 1.1
    ax.add_patch(Rectangle((6.6, mini_y), mbw, 0.10, facecolor=SLATE, edgecolor=INK, linewidth=1.0, zorder=4))
    ax.text(6.6 + mbw / 2.0, mini_y - 0.18, "raw", ha="center", va="top", fontsize=7.4, color=INK)
    ax.text(6.6 + mbw / 2.0, mini_y + 0.32, wrap_text("raw ISR <= 0.5%", 16), ha="center", va="bottom",
             fontsize=7.4, color=INK, linespacing=1.2)

    ax.add_patch(Rectangle((9.3, mini_y), mbw, 0.0, facecolor=AMBER, edgecolor=INK, linewidth=1.0, zorder=4))
    ax.plot([9.3, 9.3 + mbw], [mini_y, mini_y], color=INK, linewidth=1.2, zorder=4)
    ax.text(9.3 + mbw / 2.0, mini_y - 0.18, "after projection", ha="center", va="top", fontsize=7.4, color=INK)
    ax.text(9.3 + mbw / 2.0, mini_y + 0.32, wrap_text("0% after projection", 16), ha="center", va="bottom",
             fontsize=7.4, color=INK, linespacing=1.2)

    footnote(ax, W, 0.15,
             wrap_text("ISR <= 0.5% raw; = 0% after the decode-time projection (dr_L3-12)", 90),
             fontsize=8.2, color=INK)

    save_both(fig, OUT)


if __name__ == "__main__":
    main()
