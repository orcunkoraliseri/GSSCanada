#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fig06_hotel.py -- Figure 6: Hotel Side-Track (Tourism Statistics to SARIMA to
Guest-Room Multiplier).

Source annotation block: Figure_06_hotel_sidetrack.md. Box labels not covered by the
annotation block ("Monthly Rate", "Hotel Multiplier", "to Guest-Room Schedule") are
quoted verbatim from that same file's SCENE paragraph.

Run:  py -3 writing/figures/fig06_hotel.py
Output: writing/figures/Figure_06_hotel_sidetrack.pdf / .png
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig_style import SLATE, AMBER, GREY, INK, WHITE, new_fig, box, arrow, footnote, save_both, wrap_text
from matplotlib.patches import Rectangle, Ellipse

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Figure_06_hotel_sidetrack")

ICON_Z = 6

# ---------------------------------------------------------------------------
# LABELS -- every string drawn, verbatim from Figure_06_hotel_sidetrack.md's
# "Annotations to overlay afterward" block (plus SCENE-quoted structural names).
# Checked by f5_figure_check.py C4.
# ---------------------------------------------------------------------------
LABELS = [
    "ISQ monthly occupancy series (QC)", "CBRE monthly occupancy series (AB)",
    "SARIMA(1,1,1)(1,1,1,12) per province",
    "COVID indicator, 2020-03 to 2022-06",
    "hotel_multiplier(t, month, PR) = s(t) x monthly_rate(month, PR)",
    "overnight plateau 1.00, 22:00 to 06:00", "day trough 0.200, weekday", "day trough 0.308, weekend",
    "Backcast gate: QC + AB, 2015 to 2019, MAE < 0.05",
    "2030 bands: 0.92 / 1.00 / 1.05",
    "this entire channel bypasses the Transformer -- population-aggregate monthly series, "
    "no GSS respondents behind it",
    "Monthly Rate", "Hotel Multiplier", "to Guest-Room Schedule",
]


def icon_table(ax, cx, cy, s=0.16, color=WHITE):
    ax.add_patch(Ellipse((cx, cy + s * 0.8), s * 1.6, s * 0.7, facecolor=color, edgecolor="none", zorder=ICON_Z))
    ax.add_patch(Rectangle((cx - s * 0.8, cy - s * 0.8), s * 1.6, s * 1.6, facecolor=color, edgecolor="none", zorder=ICON_Z))
    ax.add_patch(Ellipse((cx, cy - s * 0.8), s * 1.6, s * 0.7, facecolor=color, edgecolor="none", zorder=ICON_Z))


def icon_wave(ax, cx, cy, s=0.5, color=WHITE):
    import numpy as np
    xs_ = np.linspace(-s, s, 40)
    ys_ = cy + 0.35 * s * np.sin(xs_ / s * 3.0)
    ax.plot(cx + xs_, ys_, color=color, linewidth=1.4, zorder=ICON_Z)


def step_curve(ax, x0, y0, w, h, base, color=INK, lw=1.8):
    """Two-level step: high plateau, dip, high plateau -- not a smooth sine."""
    xs_ = [x0, x0 + w * 0.30, x0 + w * 0.30, x0 + w * 0.70, x0 + w * 0.70, x0 + w]
    ys_ = [base + h, base + h, base, base, base + h, base + h]
    ax.plot(xs_, ys_, color=color, linewidth=lw, zorder=ICON_Z)


def main():
    W, H = 19.5, 11.0
    fig, ax = new_fig(W, H)

    # Inputs
    box(ax, 0.4, 8.5, 2.1, 1.0, wrap_text("ISQ monthly occupancy series (QC)", 15), facecolor=GREY, fontsize=6.9)
    icon_table(ax, 0.4 + 2.1 - 0.25, 8.5 + 1.0 - 0.25)
    box(ax, 0.4, 7.1, 2.1, 1.0, wrap_text("CBRE monthly occupancy series (AB)", 16), facecolor=GREY, fontsize=6.9)
    icon_table(ax, 0.4 + 2.1 - 0.25, 7.1 + 1.0 - 0.25)

    # SARIMA Forecast box, amber, with COVID indicator dashed band
    sx, sy, sw, sh = 3.1, 6.9, 4.5, 2.8
    box(ax, sx, sy, sw, sh, "SARIMA Forecast", "SARIMA(1,1,1)(1,1,1,12) per province",
        facecolor=AMBER, fontsize=10.5, subfontsize=7.8)
    icon_wave(ax, sx + sw * 0.30, sy + sh * 0.72, s=0.55)
    band_x = sx + sw * 0.68
    ax.add_patch(Rectangle((band_x, sy + 0.15), sw * 0.20, sh - 0.3, facecolor="none", edgecolor=WHITE,
                            linewidth=1.3, linestyle="dashed", zorder=ICON_Z))
    ax.text(band_x + sw * 0.10, sy + 0.65, wrap_text("COVID indicator, 2020-03 to 2022-06", 11),
             ha="center", va="top", fontsize=6.2, color=WHITE, linespacing=1.15)

    arrow(ax, (2.5, 8.5), (sx, sy + sh * 0.78))
    arrow(ax, (2.5, 7.6), (sx, sy + sh * 0.30))

    # Backcast Gate validation card, below SARIMA
    gx, gy, gw, gh = sx, 5.35, sw, 1.15
    box(ax, gx, gy, gw, gh, "Backcast Gate", "QC + AB, 2015 to 2019, MAE < 0.05",
        facecolor=WHITE, edgecolor=INK, textcolor=INK, fontsize=8.4, subfontsize=7.2, lw=1.3)
    ax.text(gx + 0.28, gy + gh / 2.0, "✓", ha="center", va="center", fontsize=15, color="#1E6B3A",
             weight="bold", zorder=6)
    ax.plot([sx + sw * 0.3, sx + sw * 0.3], [sy, gy + gh], color=INK, linewidth=1.0, zorder=2)

    # Monthly Rate box
    mrx, mry, mrw, mrh = 8.4, 7.6, 2.7, 1.6
    box(ax, mrx, mry, mrw, mrh, wrap_text("Monthly Rate", 14), facecolor=SLATE, fontsize=9.6)
    arrow(ax, (sx + sw, sy + sh * 0.55), (mrx, mry + mrh / 2.0))

    # Diurnal Shape s(t) box, separate, with a two-level step-curve icon
    dx, dy, dw, dh = 3.1, 1.6, 4.5, 3.1
    box(ax, dx, dy, dw, dh, "", facecolor=SLATE, fontsize=9.6)
    ax.text(dx + dw / 2.0, dy + dh - 0.30, "Diurnal Shape s(t)", ha="center", va="top",
             fontsize=9.6, color=WHITE, weight="bold", zorder=6)
    step_curve(ax, dx + 0.55, dy + dh * 0.42, dw - 1.1, 0.55, dy + dh * 0.42, color=WHITE)
    ax.text(dx + dw / 2.0, dy + 0.28,
             wrap_text("overnight plateau 1.00, 22:00 to 06:00 -- day trough 0.200, weekday -- "
                       "day trough 0.308, weekend", 40),
             ha="center", va="bottom", fontsize=6.4, color=WHITE, linespacing=1.2)

    # Hotel Multiplier box -- both paths converge here
    hx, hy, hw, hh = 12.4, 4.6, 3.6, 2.6
    box(ax, hx, hy, hw, hh, "Hotel Multiplier", "", facecolor=GREY, fontsize=10.0)
    ax.text(hx + hw / 2.0, hy + 0.34,
             wrap_text("hotel_multiplier(t, month, PR) = s(t) x monthly_rate(month, PR)", 28),
             ha="center", va="bottom", fontsize=6.6, color=WHITE, linespacing=1.2)

    arrow(ax, (mrx + mrw, mry + mrh / 2.0), (hx, hy + hh * 0.75), connectionstyle="arc3,rad=-0.15")
    arrow(ax, (dx + dw, dy + dh * 0.5), (hx, hy + hh * 0.25), connectionstyle="arc3,rad=0.15")

    # Output arrow, labelled "to Guest-Room Schedule"
    arrow(ax, (hx + hw, hy + hh / 2.0), (hx + hw + 1.8, hy + hh / 2.0), color=INK, lw=1.8)
    ax.text(hx + hw + 0.9, hy + hh / 2.0 + 0.25, "to Guest-Room Schedule", ha="center", va="bottom",
             fontsize=8.0, color=INK)
    ax.text(hx + hw + 0.9, hy + hh / 2.0 - 0.25, wrap_text("2030 bands: 0.92 / 1.00 / 1.05", 20),
             ha="center", va="top", fontsize=7.2, color=INK, linespacing=1.2)

    footnote(ax, W, 0.25,
             wrap_text("this entire channel bypasses the Transformer -- population-aggregate monthly "
                       "series, no GSS respondents behind it", 100),
             fontsize=8.2, color=AMBER)

    save_both(fig, OUT)


if __name__ == "__main__":
    main()
