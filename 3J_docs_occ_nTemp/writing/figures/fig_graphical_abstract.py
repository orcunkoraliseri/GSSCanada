#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fig_graphical_abstract.py -- Graphical Abstract: Four Populations, One Tower.

Generates:
  writing/figures/graphicalAbstract.png
  writing/figures/graphicalAbstract.pdf
"""
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig_style import SLATE, AMBER, TEAL, GREY, INK, WHITE, new_fig, box, arrow, footnote, save_both, wrap_text
from matplotlib.patches import Rectangle, FancyBboxPatch, Polygon

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "graphicalAbstract")

def main():
    W, H = 16.0, 7.0
    fig, ax = new_fig(W, H)

    # Panel Dividers (subtle background shading)
    ax.add_patch(Rectangle((0.3, 0.6), 4.5, 5.8, facecolor="#FAF8F5", edgecolor="#E5E0D8", linewidth=1.0, zorder=1))
    ax.add_patch(Rectangle((5.1, 0.6), 4.2, 5.8, facecolor="#FAF8F5", edgecolor="#E5E0D8", linewidth=1.0, zorder=1))
    ax.add_patch(Rectangle((9.6, 0.6), 6.1, 5.8, facecolor="#FAF8F5", edgecolor="#E5E0D8", linewidth=1.0, zorder=1))

    # Panel Titles
    ax.text(2.55, 6.0, "Four Populations", ha="center", va="center", fontsize=11, weight="bold", color=INK)
    ax.text(7.20, 6.0, "One Tower", ha="center", va="center", fontsize=11, weight="bold", color=INK)
    ax.text(12.65, 6.0, "Peak Hours", ha="center", va="center", fontsize=11, weight="bold", color=INK)

    # LEFT PANEL: Four populations
    pop_y = [4.8, 3.8, 2.8, 1.8]
    pop_colors = [AMBER, SLATE, GREY, TEAL]
    pop_labels = ["Households", "Workforce", "Customers", "Guests"]
    pop_icons = ["1.", "2.", "3.", "4."]

    for y, color, label, icon in zip(pop_y, pop_colors, pop_labels, pop_icons):
        box(ax, 0.6, y - 0.35, 3.6, 0.7, f"{icon}  {label}", facecolor=color, fontsize=9.0, textcolor=WHITE)

    ax.text(2.55, 1.0, "1 model, 3 survey heads\n+ 1 side-track", ha="center", va="center", fontsize=7.5, color=GREY)

    # Arrow from Left to Center Panel
    arrow(ax, (4.3, 3.3), (5.4, 3.3), color=INK, lw=1.5)

    # CENTER PANEL: One Tower
    tower_x = 6.2
    tower_w = 2.0
    tower_y0 = 1.4
    tower_h = 4.1

    # Main tower outline
    ax.add_patch(Rectangle((tower_x, tower_y0), tower_w, tower_h, facecolor=WHITE, edgecolor=INK, linewidth=1.5, zorder=3))

    # Building bands (Teal hotel top, Amber residential upper, Slate office lower, Grey retail ground)
    ax.add_patch(Rectangle((tower_x + 0.05, tower_y0 + 3.1), tower_w - 0.1, 0.9, facecolor=TEAL, edgecolor=INK, linewidth=0.8, zorder=4))
    ax.text(tower_x + tower_w / 2.0, tower_y0 + 3.55, "Hotel", color=WHITE, weight="bold", fontsize=8.0, ha="center", va="center", zorder=5)

    ax.add_patch(Rectangle((tower_x + 0.05, tower_y0 + 2.0), tower_w - 0.1, 1.05, facecolor=AMBER, edgecolor=INK, linewidth=0.8, zorder=4))
    ax.text(tower_x + tower_w / 2.0, tower_y0 + 2.525, "Residential", color=WHITE, weight="bold", fontsize=8.0, ha="center", va="center", zorder=5)

    ax.add_patch(Rectangle((tower_x + 0.05, tower_y0 + 0.5), tower_w - 0.1, 1.45, facecolor=SLATE, edgecolor=INK, linewidth=0.8, zorder=4))
    ax.text(tower_x + tower_w / 2.0, tower_y0 + 1.225, "Office", color=WHITE, weight="bold", fontsize=8.0, ha="center", va="center", zorder=5)

    ax.add_patch(Rectangle((tower_x + 0.05, tower_y0 + 0.05), tower_w - 0.1, 0.4, facecolor=GREY, edgecolor=INK, linewidth=0.8, zorder=4))
    ax.text(tower_x + tower_w / 2.0, tower_y0 + 0.25, "Retail", color=WHITE, weight="bold", fontsize=7.5, ha="center", va="center", zorder=5)

    ax.text(7.20, 1.0, "1 envelope, 1 plant", ha="center", va="center", fontsize=7.5, color=GREY)

    # Arrow from Center to Right Panel
    arrow(ax, (8.4, 3.3), (9.8, 3.3), color=INK, lw=1.5)

    # RIGHT PANEL: Diurnal Curves & Peak Hours
    chart_x0 = 10.2
    chart_y0 = 1.6
    chart_w = 4.8
    chart_h = 3.6

    # Chart axes
    ax.plot([chart_x0, chart_x0 + chart_w], [chart_y0, chart_y0], color=INK, linewidth=1.2, zorder=3)
    ax.plot([chart_x0, chart_x0], [chart_y0, chart_y0 + chart_h], color=INK, linewidth=1.2, zorder=3)

    hours = np.linspace(0, 24, 200)

    # Curve functions
    res_curve = np.exp(-((hours - 12.1) / 3.5)**2)
    off_curve = np.exp(-((hours - 11.9) / 3.0)**2)
    ret_curve = np.exp(-((hours - 12.3) / 3.2)**2)
    hot_curve = np.exp(-((hours - 18.9) / 2.5)**2)
    bldg_curve = 0.35 * res_curve + 0.35 * off_curve + 0.15 * ret_curve + 0.15 * hot_curve

    def to_cx(h):
        return chart_x0 + (h / 24.0) * chart_w

    def to_cy(val):
        return chart_y0 + val * (chart_h - 0.4)

    # Plot channel curves
    ax.plot(to_cx(hours), to_cy(res_curve), color=AMBER, linewidth=1.8, label="Residential", zorder=4)
    ax.plot(to_cx(hours), to_cy(off_curve), color=SLATE, linewidth=1.8, label="Office", zorder=4)
    ax.plot(to_cx(hours), to_cy(ret_curve), color=GREY, linewidth=1.8, label="Retail", zorder=4)
    ax.plot(to_cx(hours), to_cy(hot_curve), color=TEAL, linewidth=1.8, label="Hotel", zorder=4)

    # Whole building curve
    ax.plot(to_cx(hours), to_cy(bldg_curve), color=INK, linewidth=2.5, linestyle="--", label="Whole Building", zorder=5)

    # Midday Peak Marker
    ax.plot([to_cx(12.0), to_cx(12.0)], [chart_y0, to_cy(1.0)], color=INK, linestyle=":", linewidth=0.9, zorder=2)
    ax.text(to_cx(12.0), to_cy(1.02), "~12h", fontsize=7.5, weight="bold", color=INK, ha="center")

    # Hotel Peak Marker
    ax.plot([to_cx(18.9), to_cx(18.9)], [chart_y0, to_cy(1.0)], color=TEAL, linestyle=":", linewidth=0.9, zorder=2)
    ax.text(to_cx(18.9), to_cy(1.02), "~19h", fontsize=7.5, weight="bold", color=TEAL, ha="center")

    # Whole Building Peak Marker
    ax.plot([to_cx(15.0), to_cx(15.0)], [chart_y0, to_cy(0.72)], color=INK, linestyle=":", linewidth=0.9, zorder=2)
    ax.text(to_cx(15.0), to_cy(0.75), "~15h", fontsize=7.5, weight="bold", color=INK, ha="center")

    # Axis Labels
    ax.text(chart_x0 + chart_w / 2.0, chart_y0 - 0.35, "Hour of Day (0..24)", fontsize=8.0, ha="center", color=INK)

    # Coincidence factor badge
    ax.add_patch(FancyBboxPatch((chart_x0 + 2.6, chart_y0 + 2.8), 2.0, 0.6, boxstyle="round,pad=0.0,rounding_size=0.08",
                               linewidth=1.0, edgecolor=INK, facecolor="#FFF8DC", zorder=6))
    ax.text(chart_x0 + 3.6, chart_y0 + 3.1, "Coincidence factor\n< 1.0 (median 0.94)", fontsize=7.0, weight="bold", color=INK, ha="center", va="center", zorder=7)

    # Legend
    leg_x = chart_x0 + 0.2
    leg_y = chart_y0 + 3.2
    for i, (c, l) in enumerate([(AMBER, "Residential"), (SLATE, "Office"), (GREY, "Retail"), (TEAL, "Hotel")]):
        lx = leg_x + (i % 2) * 1.3
        ly = leg_y - (i // 2) * 0.25
        ax.add_patch(Rectangle((lx, ly), 0.2, 0.12, facecolor=c, edgecolor=INK, linewidth=0.6))
        ax.text(lx + 0.25, ly + 0.06, l, fontsize=6.5, color=INK, va="center")

    footnote(ax, W, 0.15,
             "Four Populations, One Tower -- 3 midday channels peak near ~12h; hotel peaks at ~19h; whole building peaks at ~15h",
             fontsize=8.0, color=INK)

    save_both(fig, OUT)

if __name__ == "__main__":
    main()
