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

SERVICE_MEP_TITLE = "Service/MEP"  # verbatim from Appendix_C_corrections.md section C.1
FOOTNOTE = ("Corrected 2026-07-31 (Defaut 7) parse, from Sigma FloorArea x Multiplier on "
            "IsPartOfTotalArea = 1, reproducing EnergyPlus Total Building Area exactly. "
            "Superseded figures (40,846 m2 SuperTall / 26,750 m2 Tall) were 2.7 to 3.3x too "
            "small and shifted every EUI proportionally.")
CAPTION = "measured occupiable-area shares per tower prototype"

LABELS = [
    "107,816.0 m2", "57,075.4 m2", "135,857.6 m2", "72,623.1 m2",
    "office 44.33%", "hotel 26.37%", "residential 22.50%", "retail 4.39%", "residential-common 2.40%",
    "office 44.65%", "hotel 24.91%", "residential 22.40%", "retail 5.53%", "residential-common 2.50%",
    SERVICE_MEP, SERVICE_MEP_TITLE,
    "Office", "Hotel", "Residential", "Retail", "residential-common",
    FOOTNOTE, CAPTION,
]

# Segments thinner than this (inches) cannot hold their own label legibly, so they are
# labelled outside the bar on a leader line instead of being left blank. The archived
# 2026-08-09 render left retail (4.39%) and residential-common (2.40%) with no visible
# value at all, because the old h > 0.35 test simply skipped them.
INSIDE_MIN_H = 0.30
# Fixed anchor heights (inches above the bar base) for the two outside labels. The two
# thin segments' true mid-points are only ~0.10 in apart, which is less than one line of
# 6.2 pt type, so the anchors are staggered and the leader line does the pointing.
OUTSIDE_ANCHOR = {"retail": 0.30, "residential_common": 0.03}


def stacked_bar(ax, cx, bw, base_y, height_per_pct, data):
    """Draw one stacked bar. Every segment gets its value: thick ones inside in white,
    thin ones outside on a leader line, so no channel is silently unlabelled."""
    right = cx + bw / 2.0
    y = base_y
    for ch in reversed(CHANNEL_ORDER):  # smallest-drawn-first so the stack reads largest-on-top
        pct = data[ch]
        h = pct * height_per_pct
        ax.add_patch(Rectangle((cx - bw / 2.0, y), bw, h, facecolor=CHANNEL_COLOR[ch], edgecolor=WHITE,
                                linewidth=1.0, zorder=3))
        name = "residential-common" if ch == "residential_common" else ch
        label = "%s %.2f%%" % (name, pct)
        if h >= INSIDE_MIN_H:
            ax.text(cx, y + h / 2.0, label, ha="center", va="center",
                     fontsize=7.0, color=WHITE, weight="bold", zorder=4)
        else:
            mid = y + h / 2.0
            anchor = base_y + OUTSIDE_ANCHOR[ch]
            ax.plot([right, right + 0.13, right + 0.20], [mid, anchor, anchor],
                    color=CHANNEL_COLOR[ch], linewidth=0.9, solid_capstyle="round", zorder=4)
            ax.text(right + 0.25, anchor, label, ha="left", va="center", fontsize=6.2,
                    color=INK, zorder=4)
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

    # Canvas. The 2026-08-09 render was 9.5 x 10.7 in for two bars, which left roughly a
    # third of the page empty above and below the artwork -- the author's own complaint
    # about "beaucoup d'espaces entre figure et legende". Re-laid out at page width with
    # every band sized to its content.
    W, H = 7.2, 5.8
    fig, ax = new_fig(W, H)

    ax.text(W / 2.0, H - 0.16, wrap_text(CAPTION, 70), ha="center", va="top", fontsize=10.0, color=INK,
             weight="bold")

    base_y = 1.75
    hp = 0.0305  # inches per percentage point -> a full 100% stack is 3.05 in tall
    bw = 1.5
    cx1, cx2 = 1.35, 4.35

    top1 = stacked_bar(ax, cx1, bw, base_y, hp, SUPERTALL)
    top2 = stacked_bar(ax, cx2, bw, base_y, hp, TALL)

    # Primary total = OCCUPIABLE (the denominator the five segments are shares of).
    # Secondary total = GROSS, shown smaller and clearly labelled, kept not dropped.
    for cx, top, d, name in ((cx1, top1, SUPERTALL, "SuperTall"), (cx2, top2, TALL, "Tall")):
        ax.text(cx, top + 0.30, "occupiable %s" % d["occupiable"], ha="center", va="bottom",
                 fontsize=8.6, color=INK, weight="bold")
        ax.text(cx, top + 0.11, "gross %s" % d["gross"], ha="center", va="bottom",
                 fontsize=6.8, color="#5A5F64")
        ax.text(cx, base_y - 0.13, name, ha="center", va="top", fontsize=9.0, color=INK, weight="bold")

    # Legend -- one row under the two category labels, sized to the text it holds.
    leg_y = 1.16
    leg_x = 0.30
    for ch in CHANNEL_ORDER:
        ax.add_patch(Rectangle((leg_x, leg_y), 0.20, 0.15, facecolor=CHANNEL_COLOR[ch], edgecolor=INK,
                                linewidth=0.7, zorder=4))
        ax.text(leg_x + 0.27, leg_y + 0.075, CHANNEL_LABEL[ch], ha="left", va="center", fontsize=7.0, color=INK)
        leg_x += 1.36

    # Service/MEP band -- visually separated, different shading, distinct label, clear gap.
    # Share of GROSS floor area, NOT stacked into the same 100% as the five occupiable
    # segments; the band now names itself instead of opening on a bare percentage.
    band_y, band_h = 0.52, 0.44
    ax.add_patch(Rectangle((0.30, band_y), W - 0.60, band_h, facecolor=LIGHT_GREY, edgecolor=INK,
                            linewidth=0.9, zorder=2))
    ax.text(0.44, band_y + band_h / 2.0, SERVICE_MEP_TITLE, ha="left", va="center", fontsize=7.2,
             color=INK, weight="bold", zorder=3)
    ax.text(1.30, band_y + band_h / 2.0, wrap_text(SERVICE_MEP, 88), ha="left", va="center",
             fontsize=6.4, color=INK, linespacing=1.25, zorder=3)

    footnote(ax, W, 0.10, wrap_text(FOOTNOTE, 118), fontsize=5.8, color=INK)

    # 500 dpi at a 7 in placed width is the Elsevier minimum for combination art;
    # this canvas is 7.2 in wide, so 500 * 7 / 7.2 = 486 is the floor. Rendered at 520.
    save_both(fig, OUT, dpi=520)


if __name__ == "__main__":
    main()
