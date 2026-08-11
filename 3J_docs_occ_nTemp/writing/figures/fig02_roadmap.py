#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fig02_roadmap.py -- Figure 2: Three-Leg Roadmap (Leg 1 to Leg 2 to Leg 3).

Source annotation block: Figure_02_three_leg_roadmap.md.

DEVIATION FROM THE PROMPT'S "SCENE" TEXT, DELIBERATE: the SCENE paragraph (written
for an image-generation LLM) describes the "carried forward bit-identical" chain-link
connector running under all three legs, Leg 1 through Leg 3. The annotation block's
own caution note says otherwise: "Do not label Leg 1 to Leg 2 residential reuse as
'bit-identical' without a source ... only the Leg-2-to-Leg-3 residential+office reuse
is directly sourced (Step 3 note)." The annotations block is the authoritative text
per the implementation plan, so this script draws the connector spanning ONLY Leg 2
into Leg 3, not under Leg 1. This is reported back as a plan-doc contradiction.

Run:  py -3 writing/figures/fig02_roadmap.py
Output: writing/figures/Figure_02_three_leg_roadmap.pdf / .png
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig_style import (SLATE, AMBER, INK, WHITE,
                        new_fig, box, arrow, footnote, save_both, wrap_text)
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Polygon

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Figure_02_three_leg_roadmap")

PALE_GREY = "#DCD5C8"

# ---------------------------------------------------------------------------
# LABELS -- every string drawn, verbatim from Figure_02_three_leg_roadmap.md's
# "Annotations to overlay afterward" block. Checked by f5_figure_check.py C4.
# ---------------------------------------------------------------------------
LABELS = [
    "Residential (AT_HOME) -- complete, published separately",
    "+ Office (AT_WORK) -- complete, validated end-to-end 2026-07-01; "
    "People-schedule wiring-bug lesson learned here",
    "+ Retail (AT_RETAIL, GSS) + Hotel (non-GSS, tourism statistics) -- this paper",
    "Carried forward into the four-channel stage: the Step 7 base tower geometry is md5-verified "
    "byte-identical (4 IDF files); the Step 3 residential + office tiler paths are "
    "additive by design (retail kept in a separate CSV) but byte-equality was not "
    "verified -- see Table 6",
    "four occupancy channels driving four uses inside one building -- not four building archetypes",
]


ICON_Z = 6  # icons must draw above the box fill (zorder=3) and outline (zorder=4)


def icon_person(ax, cx, cy, s=0.30, color=INK):
    ax.add_patch(Circle((cx, cy + s * 0.65), s * 0.28, facecolor="none", edgecolor=color, linewidth=1.6, zorder=ICON_Z))
    body = Polygon([(cx - s * 0.35, cy - s * 0.55), (cx + s * 0.35, cy - s * 0.55), (cx, cy + s * 0.25)],
                    closed=True, facecolor="none", edgecolor=color, linewidth=1.6, zorder=ICON_Z)
    ax.add_patch(body)


def icon_briefcase(ax, cx, cy, s=0.30, color=INK):
    ax.add_patch(Rectangle((cx - s * 0.5, cy - s * 0.4), s, s * 0.7, facecolor="none", edgecolor=color,
                            linewidth=1.6, zorder=ICON_Z))
    ax.add_patch(Rectangle((cx - s * 0.18, cy + s * 0.3), s * 0.36, s * 0.2, facecolor="none", edgecolor=color,
                            linewidth=1.4, zorder=ICON_Z))
    ax.plot([cx - s * 0.5, cx + s * 0.5], [cy - s * 0.05, cy - s * 0.05], color=color, linewidth=1.1, zorder=ICON_Z)


def icon_bag(ax, cx, cy, s=0.30, color=INK):
    pts = [(cx - s * 0.45, cy - s * 0.5), (cx + s * 0.45, cy - s * 0.5), (cx + s * 0.32, cy + s * 0.35),
           (cx - s * 0.32, cy + s * 0.35)]
    ax.add_patch(Polygon(pts, closed=True, facecolor="none", edgecolor=color, linewidth=1.6, zorder=ICON_Z))
    ax.plot([cx - s * 0.2, cx - s * 0.2], [cy + s * 0.35, cy + s * 0.6], color=color, linewidth=1.3, zorder=ICON_Z)
    ax.plot([cx + s * 0.2, cx + s * 0.2], [cy + s * 0.35, cy + s * 0.6], color=color, linewidth=1.3, zorder=ICON_Z)


def icon_bed(ax, cx, cy, s=0.30, color=INK):
    ax.add_patch(Rectangle((cx - s * 0.55, cy - s * 0.3), s * 1.1, s * 0.4, facecolor="none", edgecolor=color,
                            linewidth=1.6, zorder=ICON_Z))
    ax.add_patch(Rectangle((cx - s * 0.45, cy - s * 0.05), s * 0.35, s * 0.25, facecolor="none", edgecolor=color,
                            linewidth=1.3, zorder=ICON_Z))
    ax.plot([cx - s * 0.5, cx - s * 0.5], [cy - s * 0.3, cy - s * 0.55], color=color, linewidth=1.3, zorder=ICON_Z)
    ax.plot([cx + s * 0.5, cx + s * 0.5], [cy - s * 0.3, cy - s * 0.55], color=color, linewidth=1.3, zorder=ICON_Z)


def icon_link(ax, cx, cy, s=0.14, color=AMBER):
    ax.add_patch(Circle((cx - s * 0.5, cy), s * 0.55, facecolor="none", edgecolor=color, linewidth=1.6, zorder=ICON_Z))
    ax.add_patch(Circle((cx + s * 0.5, cy), s * 0.55, facecolor="none", edgecolor=color, linewidth=1.6, zorder=ICON_Z))


def main():
    W, H = 20.0, 9.9
    fig, ax = new_fig(W, H)

    y0 = 2.6  # shared bottom for all three legs -- telescoping height AND width, aligned baseline

    # Leg 1: narrow, pale grey
    l1_x, l1_w, l1_h = 0.7, 2.6, 3.2
    box(ax, l1_x, y0, l1_w, l1_h, wrap_text("Residential only", 20), facecolor=PALE_GREY, edgecolor=INK,
        textcolor=INK, fontsize=11)
    icon_person(ax, l1_x + l1_w / 2.0, y0 + l1_h * 0.68, s=0.55, color=INK)

    arrow(ax, (l1_x + l1_w, y0 + l1_h / 2.0), (5.0, y0 + l1_h / 2.0), lw=3.2)

    # Leg 2: medium, slate-blue, contains Leg 1's person icon plus new briefcase icon
    l2_x, l2_w, l2_h = 5.0, 6.0, 4.8
    box(ax, l2_x, y0, l2_w, l2_h, wrap_text("Residential + Office", 20), facecolor=SLATE, textcolor=WHITE, fontsize=12)
    icon_person(ax, l2_x + l2_w * 0.32, y0 + l2_h * 0.72, s=0.55, color=WHITE)
    icon_briefcase(ax, l2_x + l2_w * 0.62, y0 + l2_h * 0.72, s=0.55, color=WHITE)

    arrow(ax, (l2_x + l2_w, y0 + l2_h / 2.0), (12.2, y0 + l2_h / 2.0), lw=3.2)

    # Leg 3: wide, amber OUTLINE, contains Leg 2's elements unchanged (small slate replica)
    # plus two new amber icons (shopping-bag, bed) -- addition, not replacement.
    l3_x, l3_w, l3_h = 12.2, 7.4, 6.4
    outline = FancyBboxPatch((l3_x, y0), l3_w, l3_h, boxstyle="round,pad=0.0,rounding_size=0.35",
                              linewidth=3.4, edgecolor=AMBER, facecolor=WHITE, zorder=3)
    ax.add_patch(outline)
    ax.text(l3_x + l3_w / 2.0, y0 + l3_h - 0.5, "Residential + Office + Retail + Hotel", ha="center", va="center",
             fontsize=13, color=AMBER, weight="bold", zorder=5)

    # Leg 2's content, unchanged, replicated inside Leg 3 (small slate box)
    rep_x, rep_y, rep_w, rep_h = l3_x + 0.5, y0 + 0.4, 2.8, 3.0
    box(ax, rep_x, rep_y, rep_w, rep_h, "", facecolor=SLATE, textcolor=WHITE, fontsize=8)
    icon_person(ax, rep_x + rep_w * 0.32, rep_y + rep_h * 0.58, s=0.42, color=WHITE)
    icon_briefcase(ax, rep_x + rep_w * 0.68, rep_y + rep_h * 0.58, s=0.42, color=WHITE)
    ax.text(rep_x + rep_w / 2.0, rep_y + 0.28, "carried forward", ha="center", va="center",
             fontsize=6.6, color=WHITE)

    # Two new Leg-3 icons, amber, to the right of the replica
    new_x = rep_x + rep_w + 1.1
    icon_bag(ax, new_x, rep_y + rep_h * 0.58, s=0.70, color=AMBER)
    ax.text(new_x, rep_y + rep_h * 0.58 - 0.75, "retail", ha="center", va="center", fontsize=7.6, color=AMBER)
    icon_bed(ax, new_x + 2.0, rep_y + rep_h * 0.58, s=0.70, color=AMBER)
    ax.text(new_x + 2.0, rep_y + rep_h * 0.58 - 0.75, "hotel", ha="center", va="center", fontsize=7.6, color=AMBER)

    # Full leg labels (verbatim), placed under each container in a shared caption band
    ax.text(l1_x + l1_w / 2.0, y0 - 0.20,
             wrap_text("Residential (AT_HOME) -- complete, published separately", 22),
             ha="center", va="top", fontsize=8.0, color=INK, linespacing=1.25)
    ax.text(l2_x + l2_w / 2.0, y0 - 0.20,
             wrap_text("+ Office (AT_WORK) -- complete, validated end-to-end 2026-07-01; "
                       "People-schedule wiring-bug lesson learned here", 42),
             ha="center", va="top", fontsize=8.0, color=INK, linespacing=1.25)
    ax.text(l3_x + l3_w / 2.0, y0 - 0.20,
             wrap_text("+ Retail (AT_RETAIL, GSS) + Hotel (non-GSS, tourism statistics) -- this paper", 40),
             ha="center", va="top", fontsize=8.0, color=INK, linespacing=1.25)

    # Chain-link "carried forward bit-identical" connector: Leg 2 into Leg 3 ONLY
    # (see module docstring -- the Leg 1 to Leg 2 span is explicitly not sourced).
    conn_y = 0.80
    ax.plot([l2_x, l3_x + l3_w], [conn_y, conn_y], color=AMBER, linewidth=1.6, zorder=2)
    for lx in (l2_x + l2_w * 0.5, (l2_x + l2_w + l3_x) / 2.0, l3_x + l3_w * 0.35, l3_x + l3_w * 0.75):
        icon_link(ax, lx, conn_y, s=0.14)
    ax.text((l2_x + l3_x + l3_w) / 2.0, conn_y - 0.18,
             wrap_text("Carried forward into the four-channel stage: the Step 7 base tower geometry is md5-verified "
                       "byte-identical (4 IDF files); the Step 3 residential + office tiler paths are "
                       "additive by design (retail kept in a separate CSV) but byte-equality was not "
                       "verified -- see Table 6", 100),
             ha="center", va="top", fontsize=7.2, color=AMBER, linespacing=1.3)

    footnote(ax, W, 9.35,
             wrap_text("four occupancy channels driving four uses inside one building -- "
                       "not four building archetypes", 90),
             fontsize=8.4, color=INK)

    save_both(fig, OUT)


if __name__ == "__main__":
    main()
