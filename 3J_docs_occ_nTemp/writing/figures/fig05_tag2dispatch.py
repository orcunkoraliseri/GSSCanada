#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fig05_tag2dispatch.py -- Figure 5: Tag-2 Dispatch Inside One Tower.

Source annotation block: Figure_05_tag2_dispatch.md.

Run:  py -3 writing/figures/fig05_tag2dispatch.py
Output: writing/figures/Figure_05_tag2_dispatch.pdf / .png
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig_style import (SLATE, AMBER, GREY, INK, WHITE, GATE_RED,
                        new_fig, box, diamond, arrow, save_both, wrap_text)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Figure_05_tag2_dispatch")

# ---------------------------------------------------------------------------
# LABELS -- every string drawn, verbatim from Figure_05_tag2_dispatch.md's
# "Annotations to overlay afterward" block. Checked by f5_figure_check.py C4.
# ---------------------------------------------------------------------------
LABELS = [
    "Tag 2 exact-match routing key (per-Space, PNNL prototypes leave Space Type blank)",
    "apartment tags", "REPLACE", "Number_of_People = HHSIZE",
    "office / retail / guest-room tags", "MODULATE", "NECB baseline x channel fraction(t)",
    "amenity + service/MEP tags", "untouched NECB baseline",
    "measured 20.6% SuperTall / 21.4% Tall of gross",
    "missing channel", "NECB fallback", "additive-safe",
    "HARD WIRING GATE",
    "Number_of_People_Schedule_Name",
    "Schedule_Name",
    "the Leg-2 bug that passed every input-side check and was only caught output-side; "
    "Leg-3 runs a mandatory scenario-differentiation probe because of it",
]


def main():
    W, H = 19.0, 13.2
    fig, ax = new_fig(W, H)

    dcx, dcy = 2.3, 8.0
    diamond(ax, dcx, dcy, 3.3, 3.2, wrap_text("Tag 2 exact-match routing key (per-Space, PNNL "
                                               "prototypes leave Space Type blank)", 17),
            facecolor=SLATE, fontsize=7.6)

    lane_ys = [11.5, 9.17, 6.83, 4.5]
    lane_labels = ["apartment tags", "office / retail / guest-room tags",
                   "amenity + service/MEP tags", "missing channel"]
    out_titles = ["REPLACE", "MODULATE", "untouched NECB baseline", "NECB fallback"]
    out_subs = [
        "Number_of_People = HHSIZE",
        "NECB baseline x channel fraction(t)",
        "measured 20.6% SuperTall / 21.4% Tall of gross",
        "additive-safe",
    ]
    out_colors = [AMBER, SLATE, GREY, GREY]
    out_dashed = [False, False, False, True]

    ox, ow, oh = 10.0, 6.4, 1.75
    outcome_boxes_xy = []
    for i, ly in enumerate(lane_ys):
        arrow(ax, (dcx + 1.65, dcy + (ly - dcy) * 0.15), (ox, ly),
              connectionstyle="arc3,rad=%.3f" % (0.0 if abs(ly - dcy) < 0.01 else (0.12 if ly > dcy else -0.12)))
        lx = (dcx + 1.65 + ox) / 2.0
        ax.text(lx, ly + 0.32, wrap_text(lane_labels[i], 22), ha="center", va="bottom",
                 fontsize=7.6, color=INK, linespacing=1.2)
        oy = ly - oh / 2.0
        box(ax, ox, oy, ow, oh, out_titles[i], out_subs[i], facecolor=out_colors[i],
            dashed=out_dashed[i], fontsize=9.6, subfontsize=7.8)
        outcome_boxes_xy.append((ox, oy, ow, oh))

    # Hard Wiring Gate callout card -- red-brown outline, connected only to MODULATE (lane 2)
    gate_x, gate_y, gate_w, gate_h = 6.6, 0.35, 9.8, 2.55
    box(ax, gate_x, gate_y, gate_w, gate_h, "", facecolor=WHITE, edgecolor=GATE_RED, textcolor=INK, lw=2.2)
    ax.text(gate_x + gate_w / 2.0, gate_y + gate_h - 0.32, "HARD WIRING GATE", ha="center", va="top",
             fontsize=10.5, color=GATE_RED, weight="bold", zorder=6)

    fx, fy = gate_x + gate_w * 0.28, gate_y + gate_h * 0.42
    wx, wy = gate_x + gate_w * 0.72, gate_y + gate_h * 0.42
    ax.text(fx, fy, wrap_text("Number_of_People_Schedule_Name", 22), ha="center", va="center",
             fontsize=8.6, color="#1E6B3A", weight="bold", zorder=6, linespacing=1.2)
    ax.text(fx - 1.55, fy, "✓", ha="center", va="center", fontsize=20, color="#1E6B3A", weight="bold", zorder=6)

    ax.text(wx, fy, "Schedule_Name", ha="center", va="center", fontsize=8.6, color=GATE_RED,
             weight="bold", zorder=6)
    ax.text(wx + 1.75, fy, "✗", ha="center", va="center", fontsize=20, color=GATE_RED, weight="bold", zorder=6)

    ax.text(gate_x + gate_w / 2.0, gate_y + 0.18,
             wrap_text("the Leg-2 bug that passed every input-side check and was only caught "
                       "output-side; Leg-3 runs a mandatory scenario-differentiation probe "
                       "because of it", 92),
             ha="center", va="bottom", fontsize=6.9, color=INK, linespacing=1.25)

    # thin connecting line from the gate card up to the MODULATE outcome box only
    mod_x, mod_y, mod_w, mod_h = outcome_boxes_xy[1]
    ax.plot([mod_x + mod_w * 0.15, gate_x + gate_w * 0.5], [mod_y, gate_y + gate_h],
            color=GATE_RED, linewidth=1.0, linestyle="dashed", zorder=2)

    save_both(fig, OUT)


if __name__ == "__main__":
    main()
