#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fig03_transformer.py -- Figure 3: Three-Head Transformer + Non-GSS Hotel Side-Track.

# HARD RULE (do not violate): this figure must never render the string "4 heads"
# anywhere on the canvas. It reads "3 GSS heads + 1 non-GSS side-track" -- the
# existing PNG's "4 heads" shorthand is explicitly rejected by the prompt file.
# f5_figure_check.py C3 scans every figure script for this exact string.

Source annotation block: Figure_03_three_head_transformer.md. Box labels not covered
by the annotation block (Diary Input, Resid/AT_WORK/AT_RETAIL Output, Exclusivity
Projection, Hotel Side-Track (non-GSS), Tourism Stats) are quoted verbatim from that
same file's SCENE paragraph, which is part of the prompt .md and is what f5's C4 arm
checks against.

Run:  py -3 writing/figures/fig03_transformer.py
Output: writing/figures/Figure_03_three_head_transformer.pdf / .png
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig_style import (SLATE, AMBER, TEAL, GREY, INK, WHITE,
                        new_fig, box, arrow, lane, title_banner, footnote, save_both, wrap_text)
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Figure_03_three_head_transformer")

ICON_Z = 6

# ---------------------------------------------------------------------------
# LABELS -- every string drawn, verbatim from Figure_03_three_head_transformer.md
# (Annotations block for the callouts/heads/banner; SCENE paragraph, quoted, for
# the plain structural box names). Checked by f5_figure_check.py C4.
# ---------------------------------------------------------------------------
LABELS = [
    "3 GSS heads + 1 non-GSS side-track",
    "Shared Transformer encoder",
    "Head 1: resid",
    "Head 2: AT_WORK",
    "Head 3: AT_RETAIL",
    "loss weights a_resid : a_work : a_retail = 1.0 : 0.5 : 0.3",
    "fixed-weight scalarization + PCGrad (SLAW/UW dropped, unstable on the ~2% AT_RETAIL head)",
    "pos_weight = 49; inference-time logit shift = -ln(49) is approximately 3.89",
    "warmup 5 epochs (heads only) then joint fine-tuning 15 epochs with PCGrad",
    "decode temperature T = 0.7 + 2-slot minimum-dwell constraint",
    "decode thresholds 0.50 / 0.40 / 0.15 (resid / AT_WORK / AT_RETAIL)",
    "SARIMA(1,1,1)(1,1,1,12) per province; population-aggregate monthly series, no GSS "
    "respondents behind it -- bypasses the Transformer entirely",
    "Diary Input", "Resid Output", "AT_WORK Output", "AT_RETAIL Output",
    "Exclusivity Projection", "Hotel Side-Track (non-GSS)", "Tourism Stats",
]


def icon_sarima(ax, cx, cy, s=0.20, color=WHITE):
    xs_ = [cx - s, cx - s * 0.5, cx, cx + s * 0.5, cx + s]
    ys_ = [cy - s * 0.3, cy + s * 0.5, cy - s * 0.5, cy + s * 0.5, cy - s * 0.3]
    ax.plot(xs_, ys_, color=color, linewidth=1.4, zorder=ICON_Z)


def main():
    W, H = 20.0, 11.6
    fig, ax = new_fig(W, H)

    title_banner(ax, W, 11.15, "3 GSS heads + 1 non-GSS side-track", fontsize=16, color=INK)

    # Bracket grouping the three GSS lanes -- a visual grouping shape, no text of its own.
    grp = FancyBboxPatch((0.25, 4.25), 16.9, 6.35, boxstyle="round,pad=0.0,rounding_size=0.15",
                          linewidth=1.0, edgecolor="#C9C3B8", facecolor="none", linestyle="dashed", zorder=1)
    ax.add_patch(grp)

    # Diary Input -> Shared Transformer encoder
    box(ax, 0.6, 6.85, 1.7, 1.3, wrap_text("Diary Input", 14), facecolor=GREY, fontsize=8.6)
    box(ax, 2.9, 6.1, 2.6, 2.8, wrap_text("Shared Transformer encoder", 14), facecolor=SLATE, fontsize=9.2)
    arrow(ax, (2.3, 7.5), (2.9, 7.5))

    lanes_y = [9.15, 7.5, 5.35]  # top, middle (matches encoder centre), bottom
    head_labels = ["Head 1: resid", "Head 2: AT_WORK", "Head 3: AT_RETAIL"]
    out_labels = ["Resid Output", "AT_WORK Output", "AT_RETAIL Output"]
    hbw, hbh = 2.5, 1.35
    obw, obh = 2.1, 1.35
    head_x, out_x = 6.4, 9.6

    for i, cy in enumerate(lanes_y):
        hy = cy - hbh / 2.0
        box(ax, head_x, hy, hbw, hbh, wrap_text(head_labels[i], 16), facecolor=SLATE, fontsize=8.8)
        conn = None if i == 1 else ("arc3,rad=%.2f" % (0.20 if i == 0 else -0.20))
        arrow(ax, (5.5, 7.5), (head_x, cy), connectionstyle=conn)
        oy = cy - obh / 2.0
        box(ax, out_x, oy, obw, obh, wrap_text(out_labels[i], 15), facecolor=TEAL, fontsize=8.2)
        arrow(ax, (head_x + hbw, cy), (out_x, cy))

    # Exclusivity Projection -- tall box the three output lanes converge into
    ep_x, ep_w = 12.6, 2.7
    ep_y, ep_h = lanes_y[2] - obh / 2.0, (lanes_y[0] + obh / 2.0) - (lanes_y[2] - obh / 2.0)
    box(ax, ep_x, ep_y, ep_w, ep_h, wrap_text("Exclusivity Projection", 12), facecolor=AMBER, fontsize=9.4)
    for cy in lanes_y:
        arrow(ax, (out_x + obw, cy), (ep_x, ep_y + ep_h / 2.0),
              connectionstyle=None if cy == lanes_y[1] else ("arc3,rad=%.2f" % (0.15 if cy > lanes_y[1] else -0.15)))

    # Callouts near the head/output cluster
    ax.text(head_x + (out_x + obw - head_x) / 2.0, 4.15,
             wrap_text("loss weights a_resid : a_work : a_retail = 1.0 : 0.5 : 0.3", 46),
             ha="center", va="top", fontsize=7.6, color=INK, linespacing=1.25)
    ax.text(head_x + (out_x + obw - head_x) / 2.0, 3.55,
             wrap_text("fixed-weight scalarization + PCGrad (SLAW/UW dropped, unstable on the "
                       "~2% AT_RETAIL head)", 50),
             ha="center", va="top", fontsize=7.2, color=INK, linespacing=1.25)
    ax.text(2.2, 5.55,
             wrap_text("warmup 5 epochs (heads only) then joint fine-tuning 15 epochs with PCGrad", 26),
             ha="center", va="top", fontsize=7.0, color=INK, linespacing=1.25)

    # Rare-class callout on the AT_RETAIL head (bottom lane) ONLY -- per the annotation
    # block ("Rare-class callout on the AT_RETAIL head only"), not the three heads as a
    # group. Sits in the gap between lane 2 and lane 3, but a short dashed leader line
    # anchors it explicitly to the top edge of the Head 3: AT_RETAIL box, so it reads as
    # attached to that one head rather than floating in empty space.
    head3_top = lanes_y[2] + hbh / 2.0
    callout_y = head3_top + 0.35
    ax.text(head_x + hbw / 2.0, callout_y,
             wrap_text("pos_weight = 49; inference-time logit shift = -ln(49) is approximately 3.89", 34),
             ha="center", va="bottom", fontsize=6.8, color=AMBER, linespacing=1.2)
    ax.plot([head_x + hbw / 2.0, head_x + hbw / 2.0], [head3_top, callout_y - 0.06], color=AMBER,
             linewidth=1.0, linestyle="dashed", zorder=2)

    # Decode + threshold callouts, on the Exclusivity Projection box
    ax.text(ep_x + ep_w / 2.0, ep_y - 0.20,
             wrap_text("decode temperature T = 0.7 + 2-slot minimum-dwell constraint", 26),
             ha="center", va="top", fontsize=6.8, color=INK, linespacing=1.25)
    ax.text(ep_x + ep_w / 2.0, ep_y - 0.95,
             wrap_text("decode thresholds 0.50 / 0.40 / 0.15 (resid / AT_WORK / AT_RETAIL)", 26),
             ha="center", va="top", fontsize=6.8, color=INK, linespacing=1.25)

    # Hotel Side-Track: physically separate, dashed boundary, own input/output, NO arrow
    # from the Shared Encoder or the three-lane bracket.
    hs_x, hs_y, hs_w, hs_h = 6.4, 0.55, 5.9, 1.9
    lane(ax, hs_x, hs_y, hs_w, hs_h, edgecolor=AMBER, dashed=True)
    ax.add_patch(Rectangle((hs_x + 0.15, hs_y + 0.15), hs_w - 0.3, hs_h - 0.3, facecolor=AMBER,
                            edgecolor="none", zorder=2))
    ax.text(hs_x + hs_w / 2.0, hs_y + hs_h / 2.0 + 0.15, wrap_text("Hotel Side-Track (non-GSS)", 22),
             ha="center", va="center", fontsize=9.0, color=WHITE, weight="bold", zorder=6, linespacing=1.2)
    icon_sarima(ax, hs_x + hs_w / 2.0, hs_y + hs_h * 0.22, s=0.24, color=WHITE)

    box(ax, 2.9, hs_y + hs_h / 2.0 - 0.6, 2.6, 1.2, wrap_text("Tourism Stats", 14), facecolor=GREY, fontsize=8.4)
    arrow(ax, (5.5, hs_y + hs_h / 2.0), (hs_x, hs_y + hs_h / 2.0), color=AMBER)
    arrow(ax, (hs_x + hs_w, hs_y + hs_h / 2.0), (hs_x + hs_w + 1.1, hs_y + hs_h / 2.0), color=AMBER)

    footnote(ax, W, 0.12,
             wrap_text("SARIMA(1,1,1)(1,1,1,12) per province; population-aggregate monthly series, "
                       "no GSS respondents behind it -- bypasses the Transformer entirely", 100),
             fontsize=7.6, color=AMBER)

    save_both(fig, OUT)


if __name__ == "__main__":
    main()
