#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
figS02_levers.py -- Figure S2: One Scenario Lever per Channel.

Source annotation block: Figure_S02_scenario_levers.md.

Run:  py -3 writing/figures/SI/figS02_levers.py
Output: writing/figures/SI/Figure_S02_scenario_levers.pdf / .png
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fig_style import SLATE, AMBER, TEAL, GREY, INK, WHITE, new_fig, footnote, save_both, wrap_text
from matplotlib.patches import Circle, Rectangle

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Figure_S02_scenario_levers")

ICON_Z = 6

# ---------------------------------------------------------------------------
# LABELS -- every string drawn, verbatim from Figure_S02_scenario_levers.md's
# "Annotations to overlay afterward" block. Checked by f5_figure_check.py C4.
# ---------------------------------------------------------------------------
LABELS = [
    "Residential -- no scenario lever (REPLACE injection, GSS-driven, not a code-density modulation)",
    "conservative", "hybrid", "fullyhybrid",
    "0.90", "0.97 (default)", "1.05",
    "0.92", "1.00", "1.05",
    "one lever per channel -- re-runnable sensitivity bands, the Leg-2 reviewer-defusing pattern",
    "Residential has no lever.",
    "Residential", "Office", "Retail", "Hotel",
]


def slider(ax, cx, cy, w, color, positions):
    ax.plot([cx - w / 2.0, cx + w / 2.0], [cy, cy], color=INK, linewidth=1.8, zorder=4)
    n = len(positions)
    for i, lab in enumerate(positions):
        tx = cx - w / 2.0 + w * i / (n - 1)
        ax.plot([tx, tx], [cy - 0.10, cy + 0.10], color=INK, linewidth=1.4, zorder=4)
        ax.text(tx, cy - 0.28, wrap_text(lab, 12), ha="center", va="top", fontsize=6.8, color=INK,
                 linespacing=1.15)
        if i == 1:
            ax.add_patch(Circle((tx, cy), 0.16, facecolor=color, edgecolor=INK, linewidth=1.2, zorder=5))


def no_lever_glyph(ax, cx, cy, w, color=GREY):
    ax.plot([cx - w / 2.0, cx + w / 2.0], [cy, cy], color=color, linewidth=1.8, zorder=4)
    ax.add_patch(Circle((cx, cy), 0.16, facecolor=color, edgecolor=INK, linewidth=1.2, zorder=5))


def main():
    W, H = 15.0, 6.5
    fig, ax = new_fig(W, H)

    lanes_x = [1.9, 5.6, 9.3, 13.0]
    lane_w = 3.0
    slider_y = 3.6

    # Residential -- no lever
    no_lever_glyph(ax, lanes_x[0], slider_y, lane_w * 0.6)
    ax.text(lanes_x[0], slider_y - 0.45, "Residential has no lever.", ha="center", va="top",
             fontsize=8.0, color=GREY, weight="bold")
    ax.text(lanes_x[0], slider_y - 0.95,
             wrap_text("Residential -- no scenario lever (REPLACE injection, GSS-driven, not a "
                       "code-density modulation)", 22),
             ha="center", va="top", fontsize=6.8, color=INK, linespacing=1.25)

    # Office -- conservative / hybrid / fullyhybrid
    slider(ax, lanes_x[1], slider_y, lane_w * 0.75, SLATE, ["conservative", "hybrid", "fullyhybrid"])

    # Retail -- 0.90 / 0.97 (default) / 1.05
    slider(ax, lanes_x[2], slider_y, lane_w * 0.75, TEAL, ["0.90", "0.97 (default)", "1.05"])

    # Hotel -- 0.92 / 1.00 / 1.05
    slider(ax, lanes_x[3], slider_y, lane_w * 0.75, AMBER, ["0.92", "1.00", "1.05"])

    lane_names = ["Residential", "Office", "Retail", "Hotel"]
    lane_colors = [GREY, SLATE, TEAL, AMBER]
    for x, name, c in zip(lanes_x, lane_names, lane_colors):
        ax.add_patch(Rectangle((x - 0.85, 5.35), 1.7, 0.72, facecolor=c, edgecolor=INK, linewidth=1.2, zorder=3))
        ax.text(x, 5.71, name, ha="center", va="center", fontsize=9.4, color=WHITE, weight="bold", zorder=6)

    footnote(ax, W, 0.30,
             wrap_text("one lever per channel -- re-runnable sensitivity bands, the Leg-2 "
                       "reviewer-defusing pattern", 90),
             fontsize=8.4, color=INK)

    save_both(fig, OUT)


if __name__ == "__main__":
    main()
