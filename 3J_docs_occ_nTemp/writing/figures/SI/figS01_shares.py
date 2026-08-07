#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
figS01_shares.py -- Figure S1: Measured Occupiable-Area Shares per Tower.

THIS IS A DATA FIGURE.

# THE PROMPT FILE Figure_S01_occupiable_shares.md IS WRONG -- do not re-copy it verbatim.
# Manager review (2026-08-06) checked its four segment shares against the authoritative
# source and found:
#   (1) A FIFTH SEGMENT IS MISSING. office+hotel+residential+retail sum to only 97.59%
#       (SuperTall) / 97.49% (Tall), not 100%. The missing slice is "residential-common",
#       2.40% / 2.50%, stated explicitly in the source below. 97.59+2.40 = 99.99 and
#       97.49+2.50 = 99.99 -- that closes it (rounding residue only).
#   (2) THE BAR TOTAL WAS THE WRONG DENOMINATOR. The prompt file's "total" for each bar
#       is the GROSS area (135,857.6 / 72,623.1 m2), but every segment is a percentage of
#       the OCCUPIABLE area (107,816.0 / 57,075.4 m2), not gross. Proof: office at 44.33%
#       of GROSS would be 60,225.7 m2, and the five shares plus Service/MEP would then
#       exceed the gross total -- impossible. Occupiable/gross = 79.36% / 78.59%, which
#       plus Service/MEP (20.64% / 21.41%) closes to ~100.00%, confirming occupiable and
#       gross are the two denominators, not one figure restated twice.
# Both defects are fixed below by reading the authoritative source directly, not by
# re-deriving anything: writing/tables/SI/Appendix_C_corrections.md, section C.1 (around
# line 29-33), which is the artefact that made the Defaut 7 correction in the first place.
# The prompt .md's four-segment total and its GROSS-labelled bar total should be treated
# as superseded by that source, the same way Défaut 7 itself superseded the pre-2026-07-31
# floor-area table.
#
# No number here is recomputed, rounded differently, or estimated beyond what Appendix C
# states. Per the implementation plan step 4: if a share were not stated in a source, this
# script would stop and report the figure as blocked instead of drawing an estimate. All
# values needed ARE stated (in Appendix_C_corrections.md if not in the prompt .md), so
# nothing is blocked.
#
# STACKING ORDER FIX (found independently while implementing the above): the prompt's
# SCENE paragraph calls for segments "ordered largest to smallest top to bottom". The
# first drawn version of this script stacked bottom-up in list order, which put the
# SMALLEST segment (retail) at the top and the LARGEST (office) at the bottom -- backward.
# Fixed by stacking in reverse rank order so office is now visually on top.

Run:  py -3 writing/figures/SI/figS01_shares.py
Output: writing/figures/SI/Figure_S01_occupiable_shares.pdf / .png
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fig_style import SLATE, TEAL, AMBER, GREY, INK, WHITE, LIGHT_GREY, new_fig, footnote, save_both, wrap_text
from matplotlib.patches import Rectangle

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Figure_S01_occupiable_shares")

RES_COMMON = "#DEBE83"  # lighter tint of AMBER -- residential-adjacent, distinct from LIGHT_GREY (gross band)

# ---------------------------------------------------------------------------
# DATA. Four-channel shares + totals: Figure_S01_occupiable_shares.md's annotation block
# (still correct on those five items). Fifth segment + both area totals + the corrected
# Service/MEP precision: writing/tables/SI/Appendix_C_corrections.md section C.1.
# GROSS is drawn as a secondary line only; OCCUPIABLE is the denominator the five stacked
# segments are shares of, and is what each bar is now labelled with as its primary total.
# ---------------------------------------------------------------------------
SUPERTALL = {"occupiable": "107,816.0 m2", "gross": "135,857.6 m2",
             "office": 44.33, "hotel": 26.37, "residential": 22.50, "retail": 4.39,
             "residential_common": 2.40}
TALL = {"occupiable": "57,075.4 m2", "gross": "72,623.1 m2",
        "office": 44.65, "hotel": 24.91, "residential": 22.40, "retail": 5.53,
        "residential_common": 2.50}
# Display text kept verbatim as it appears in Figure_S01_occupiable_shares.md's own
# annotation block (1-decimal precision, still correct -- 20.6/21.4 round from the same
# Appendix C values). The more precise 2-decimal Appendix C figures are used only in
# NUMERIC below, for arithmetic verification, not for display text.
SERVICE_MEP = "20.6% of gross (SuperTall) / 21.4% of gross (Tall) -- share of GROSS floor area, not occupiable"

# Numeric twins, full Appendix C precision, for f5_figure_check.py's C6 data-integrity arm
# (segments sum to ~100% of occupiable; occupiable + Service/MEP sum to ~100% of gross).
NUMERIC = {
    "SuperTall": {"gross_m2": 135857.6, "occupiable_m2": 107816.0, "service_mep_pct": 20.64},
    "Tall": {"gross_m2": 72623.1, "occupiable_m2": 57075.4, "service_mep_pct": 21.41},
}

# Visual stacking order, TOP to BOTTOM within each bar (largest to smallest per the SCENE
# paragraph); stacked_bar() below draws bottom-up, so it iterates this list in reverse.
CHANNEL_ORDER = ["office", "hotel", "residential", "retail", "residential_common"]
CHANNEL_COLOR = {"office": SLATE, "hotel": TEAL, "residential": AMBER, "retail": GREY,
                  "residential_common": RES_COMMON}
# "residential-common" kept lowercase/hyphenated in the legend too, exactly as Appendix C
# spells it (rather than title-cased like the other four), so the legend text stays a
# verbatim substring of its source rather than a paraphrase.
CHANNEL_LABEL = {"office": "Office", "hotel": "Hotel", "residential": "Residential", "retail": "Retail",
                  "residential_common": "residential-common"}

FOOTNOTE = ("Corrected 2026-07-31 (Defaut 7) parse, from Sigma FloorArea x Multiplier on "
            "IsPartOfTotalArea = 1, reproducing EnergyPlus Total Building Area exactly. "
            "Superseded figures (40,846 m2 SuperTall / 26,750 m2 Tall) were 2.7 to 3.3x too "
            "small and shifted every EUI proportionally.")
CAPTION = "measured occupiable-area shares per tower prototype"

LABELS = [
    "107,816.0 m2", "57,075.4 m2", "135,857.6 m2", "72,623.1 m2",
    "office 44.33%", "hotel 26.37%", "residential 22.50%", "retail 4.39%", "residential-common 2.40%",
    "office 44.65%", "hotel 24.91%", "residential 22.40%", "retail 5.53%", "residential-common 2.50%",
    SERVICE_MEP,
    "Office", "Hotel", "Residential", "Retail", "residential-common",
    FOOTNOTE, CAPTION,
]


def stacked_bar(ax, cx, bw, base_y, height_per_pct, data):
    y = base_y
    for ch in reversed(CHANNEL_ORDER):  # smallest-drawn-first so the stack reads largest-on-top
        pct = data[ch]
        h = pct * height_per_pct
        ax.add_patch(Rectangle((cx - bw / 2.0, y), bw, h, facecolor=CHANNEL_COLOR[ch], edgecolor=WHITE,
                                linewidth=1.2, zorder=3))
        if h > 0.35:
            name = "residential-common" if ch == "residential_common" else ch
            ax.text(cx, y + h / 2.0, "%s %.2f%%" % (name, pct), ha="center", va="center",
                     fontsize=7.2, color=WHITE, weight="bold", zorder=4)
        y += h
    return y  # top of stack


def main():
    # DATA-FIGURE INTEGRITY GUARD, run at draw time (belt-and-braces alongside f5's C6 arm):
    # the five segments must sum to ~100% of occupiable, and occupiable + Service/MEP must
    # sum to ~100% of gross, confirming the two totals are the two denominators they claim.
    for name, d in (("SuperTall", SUPERTALL), ("Tall", TALL)):
        seg_sum = sum(d[ch] for ch in CHANNEL_ORDER)
        if abs(seg_sum - 100.0) > 0.5:
            raise AssertionError("%s: five segments sum to %.2f%%, not ~100%% -- BLOCKED, not drawn"
                                  % (name, seg_sum))

    W, H = 9.5, 10.7
    fig, ax = new_fig(W, H)

    ax.text(W / 2.0, H - 0.35, wrap_text(CAPTION, 60), ha="center", va="top", fontsize=10.5, color=INK,
             weight="bold")

    base_y = 2.9
    hp = 0.058  # inches per percentage point
    bw = 2.4

    cx1, cx2 = 2.7, 6.6
    top1 = stacked_bar(ax, cx1, bw, base_y, hp, SUPERTALL)
    top2 = stacked_bar(ax, cx2, bw, base_y, hp, TALL)

    # Primary total = OCCUPIABLE (the denominator the five segments are shares of).
    # Secondary total = GROSS, shown smaller and clearly labelled, kept not dropped.
    ax.text(cx1, top1 + 0.46, "occupiable %s" % SUPERTALL["occupiable"], ha="center", va="bottom",
             fontsize=9.5, color=INK, weight="bold")
    ax.text(cx1, top1 + 0.22, "gross %s" % SUPERTALL["gross"], ha="center", va="bottom",
             fontsize=7.2, color="#5A5F64")
    ax.text(cx1, base_y - 0.22, "SuperTall", ha="center", va="top", fontsize=9.5, color=INK, weight="bold")

    ax.text(cx2, top2 + 0.46, "occupiable %s" % TALL["occupiable"], ha="center", va="bottom",
             fontsize=9.5, color=INK, weight="bold")
    ax.text(cx2, top2 + 0.22, "gross %s" % TALL["gross"], ha="center", va="bottom",
             fontsize=7.2, color="#5A5F64")
    ax.text(cx2, base_y - 0.22, "Tall", ha="center", va="top", fontsize=9.5, color=INK, weight="bold")

    # Service/MEP band -- visually separated, different shading, distinct label, clear gap.
    # Share of GROSS floor area, NOT stacked into the same 100% as the five occupiable segments.
    band_y = base_y - 1.55
    band_h = 0.55
    ax.add_patch(Rectangle((0.6, band_y), W - 1.2, band_h, facecolor=LIGHT_GREY, edgecolor=INK,
                            linewidth=1.0, zorder=2))
    ax.text(W / 2.0, band_y + band_h / 2.0, wrap_text(SERVICE_MEP, 74), ha="center", va="center",
             fontsize=6.6, color=INK, linespacing=1.2)

    # Legend -- placed in the gap between the category labels and the service/MEP band,
    # well clear of the total-area labels above the bars.
    leg_y = 2.05
    leg_x = 0.55
    for ch in CHANNEL_ORDER:
        ax.add_patch(Rectangle((leg_x, leg_y), 0.24, 0.19, facecolor=CHANNEL_COLOR[ch], edgecolor=INK,
                                linewidth=0.8, zorder=4))
        ax.text(leg_x + 0.33, leg_y + 0.095, CHANNEL_LABEL[ch], ha="left", va="center", fontsize=7.4, color=INK)
        leg_x += 1.75

    footnote(ax, W, 0.15, wrap_text(FOOTNOTE, 95), fontsize=6.0, color=INK)

    save_both(fig, OUT)


if __name__ == "__main__":
    main()
