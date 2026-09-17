# -*- coding: utf-8 -*-
"""Figure 1 - the pipeline, Steps 0 to 11.

Built in code on 2026-09-14 on the author's instruction ("ok if possible you
create these failed images"), after four generator rounds failed to clear
FINDING 282 (canvas capped at 1376 x 768), FINDING 286 (a repeated word on
card 11) and FINDING 289 (two instruction words drawn as extra tiles).

EVERY string drawn here is copied verbatim from the frozen TEXT INVENTORY of
`Prompts_Images/4thJ_pipeline_steps_figure.md` Section 11.  No wording is
invented and no wording is altered.  House palette only; no green, no red.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch
from matplotlib.lines import Line2D

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]

# ---------------------------------------------------------------- palette
ROSE = "#CC6677"
INDIGO = "#332288"
TEAL = "#44AA99"
SAND = "#DDCC77"
WINE = "#882255"
GREY_L = "#F2F2F2"
GREY_M = "#D0D0D0"
INK = "#111111"


def tint(hexcol, frac):
    """Blend hexcol toward white; frac is the amount of hexcol kept."""
    r = int(hexcol[1:3], 16); g = int(hexcol[3:5], 16); b = int(hexcol[5:7], 16)
    r = int(255 - (255 - r) * frac)
    g = int(255 - (255 - g) * frac)
    b = int(255 - (255 - b) * frac)
    return "#%02X%02X%02X" % (r, g, b)


# ---------------------------------------------------------------- geometry
W, H = 44.4, 16.2
FIG_DPI = 100

fig = plt.figure(figsize=(W, H), dpi=FIG_DPI)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor("white")

CARD_W = 3.30
CARD_H = 5.20
CARD_Y = 6.90
PITCH = 3.60
X0 = 0.60


def cx(i):
    return X0 + (i + 0.5) * PITCH


# ---------------------------------------------------------------- title (1 line)
TITLE = "From harmonised time-use surveys to simulated building energy"
ax.text(W / 2.0, 15.50, TITLE, ha="center", va="center",
        fontsize=27, color=INK, weight="bold")

# ---------------------------------------------------------------- five bands
BAND_Y = 13.10
BAND_H = 1.45
bands = [
    ("DATA",   0, 2, tint(GREY_M, 0.55), BAND_H),
    ("MODEL",  3, 5, tint(TEAL, 0.25), BAND_H),
    ("CLAIM",  6, 7, tint(INDIGO, 0.42), BAND_H + 0.28),
    ("ENERGY", 8, 9, tint(ROSE, 0.25), BAND_H),
    ("STOCK", 10, 11, tint(SAND, 0.25), BAND_H),
]
for label, a, b, col, bh in bands:
    xa = cx(a) - CARD_W / 2.0
    xb = cx(b) + CARD_W / 2.0
    ax.add_patch(FancyBboxPatch((xa, BAND_Y), xb - xa, bh,
                                boxstyle="round,pad=0,rounding_size=0.22",
                                facecolor=col, edgecolor="none", zorder=1))
    ax.text((xa + xb) / 2.0, BAND_Y + bh / 2.0, label, ha="center", va="center",
            fontsize=22, color=INK, weight="bold", zorder=2)

# ---------------------------------------------------------------- the twelve cards
# (digit, title, [body lines], chip word)
CARDS = [
    (0,  "Feasibility gate",          ["data, prior art, method, release limits"], "cleared"),
    (1,  "Corpus",                    ["one harmonised wave per country"], "validated"),
    (2,  "Harmonisation",             ["common activity, location, co-presence"], "validated"),
    (3,  "Serialisation",             ["duration, activity, location, co-presence"], "validated"),
    (4,  "Fine-tuning",               ["one adapter per held-out country"], "decided"),
    (5,  "Population linkage",        ["synthetic population, then one day each",
                                       "two gates ship as declared exceptions"], "validated"),
    (6,  "Transfer test",             ["train on two, generate the third",
                                       "the bar: beat real diaries, reweighted"], "validated"),
    (7,  "Constrained generation",    ["well-formed diaries guaranteed at decoding"], "decided"),
    (8,  "Building simulation",       ["European residential archetypes",
                                       "the occupancy effect does not survive"], "validated"),
    (9,  "End-use loads",             ["published activity-to-appliance mappings",
                                       "three gates ship as declared limitations"], "validated"),
    (10, "Real-stock UBEM",           ["observed footprints, one diary per dwelling"], "validated"),
    (11, "Stock-scale end-use loads", ["same mapping, bands inherited unmoved"], "validated"),
]

# mechanical word-count guard, straight from the prompt's table
WORDCOUNTS = {0: [6], 1: [5], 2: [4], 3: [4], 4: [5], 5: [6, 6],
              6: [6, 6], 7: [5], 8: [3, 6], 9: [3, 6], 10: [6], 11: [5]}
for n, t, lines, chip in CARDS:
    got = [len(l.split()) for l in lines]
    if got != WORDCOUNTS[n]:
        raise SystemExit("ABORT card %d word count %s, expected %s" % (n, got, WORDCOUNTS[n]))

CHECK = u"✓"
CHIP_GLYPH = {"cleared": CHECK + " ", "validated": CHECK + CHECK + " ",
              "decided": "", "open": ""}

texts_to_measure = []   # (artist, allowed_width_in_units)

for n, title, lines, chip in CARDS:
    big = (n == 6)
    w = CARD_W + (0.25 if big else 0.0)
    h = CARD_H + (0.90 if big else 0.0)
    x = cx(n) - w / 2.0
    y = CARD_Y - (0.45 if big else 0.0)
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0,rounding_size=0.26",
                                facecolor=tint(INDIGO, 0.07) if big else "white",
                                edgecolor=INDIGO, linewidth=3.0 if big else 1.4,
                                zorder=3))
    top = y + h
    # digit circle
    ax.add_patch(Circle((x + 0.52, top - 0.60), 0.35, facecolor=INDIGO,
                        edgecolor="none", zorder=4))
    ax.text(x + 0.52, top - 0.60, str(n), ha="center", va="center",
            fontsize=13, color="white", weight="bold", zorder=5)
    # title
    t = ax.text(cx(n), top - 1.65, title, ha="center", va="center",
                fontsize=14.5 if big else 13.5, color=INK, weight="bold", zorder=5)
    texts_to_measure.append((t, w - 0.22))
    # body lines
    by = top - 2.50
    for k, line in enumerate(lines):
        bold = (big and line.startswith("the bar:"))
        t = ax.text(cx(n), by - k * 0.72, line, ha="center", va="center",
                    fontsize=10.0, color=INK, zorder=5,
                    weight="bold" if bold else "normal")
        texts_to_measure.append((t, w - 0.18))
    # chip
    label = CHIP_GLYPH[chip] + chip
    filled = chip in ("cleared", "validated", "decided")
    chw = max(0.095 * len(label) + 0.50, 1.35)
    chw = min(chw, w - 0.30)
    chx = cx(n) - chw / 2.0
    chy = y + 0.50
    ax.add_patch(FancyBboxPatch((chx, chy), chw, 0.75,
                                boxstyle="round,pad=0,rounding_size=0.30",
                                facecolor=INDIGO if filled else "white",
                                edgecolor=INDIGO, linewidth=1.6, zorder=4))
    t = ax.text(cx(n), chy + 0.375, label, ha="center", va="center",
                fontsize=11, color="white" if filled else INDIGO,
                weight="bold", zorder=5)
    texts_to_measure.append((t, chw - 0.10))

# ---------------------------------------------------------------- spine arrows
SPINE_Y = CARD_Y + CARD_H / 2.0
for n in range(11):
    xa = cx(n) + (CARD_W / 2.0) + (0.11 if n == 6 else 0.0)
    xb = cx(n + 1) - (CARD_W / 2.0) - (0.11 if n + 1 == 6 else 0.0)
    ax.add_patch(FancyArrowPatch((xa + 0.02, SPINE_Y), (xb - 0.02, SPINE_Y),
                                 arrowstyle="-|>", mutation_scale=16,
                                 linewidth=1.8, color=INK, zorder=2))

# ---------------------------------------------------------------- seven tiles
TILE_Y = 1.05
TILE_H = 1.50
BRACKET_Y = 5.00

# (label, tile centre x, list of (card index, x-offset on that card's bottom edge))
TILES = [
    ("pre-declared gate batteries",        None),          # square bracket, cards 1-5
    ("distributional fidelity",            [(6, -1.05)]),
    ("collapse, memorisation and privacy", [(6, 0.0)]),
    ("transfer margin",                    [(6, 1.05)]),
    ("structural validity",                [(7, 0.0)]),
    ("downstream energy",                  [(8, 0.0), (9, 0.0)]),
    ("basis and denominator",              [(10, 0.0), (11, 0.0)]),
]


def tile_w(label):
    return max(0.079 * len(label) + 0.62, 1.5)


# lay the seven tiles out left to right, each as near its target as a 0.70 gap allows
GAP = 0.70
targets_x = [cx(3), cx(6), cx(6), cx(6), cx(7),
             (cx(8) + cx(9)) / 2.0, (cx(10) + cx(11)) / 2.0]
widths = [tile_w(t[0]) for t in TILES]
# the three card-6 tiles are placed as one group centred on card 6
grp = widths[1] + widths[2] + widths[3] + 2 * GAP
gx = cx(6) - grp / 2.0
centres = [0.0] * 7
centres[1] = gx + widths[1] / 2.0
centres[2] = gx + widths[1] + GAP + widths[2] / 2.0
centres[3] = gx + widths[1] + GAP + widths[2] + GAP + widths[3] / 2.0
centres[0] = min(targets_x[0], gx - GAP - widths[0] / 2.0)
right = centres[3] + widths[3] / 2.0
for i in (4, 5, 6):
    centres[i] = max(targets_x[i], right + GAP + widths[i] / 2.0)
    right = centres[i] + widths[i] / 2.0
if right > W - 0.4:
    raise SystemExit("ABORT: tile row overruns the canvas at %.2f" % right)

TILES = [(lab, centres[i], tgt) for i, (lab, tgt) in enumerate(TILES)]

for _ti, (label, tcx, targets) in enumerate(TILES):
    tw = max(0.079 * len(label) + 0.62, 1.5)
    ax.add_patch(FancyBboxPatch((tcx - tw / 2.0, TILE_Y), tw, TILE_H,
                                boxstyle="round,pad=0,rounding_size=0.20",
                                facecolor=GREY_L, edgecolor=GREY_M,
                                linewidth=1.2, zorder=3))
    t = ax.text(tcx, TILE_Y + TILE_H / 2.0, label, ha="center", va="center",
                fontsize=10.5, color=INK, zorder=5)
    texts_to_measure.append((t, tw - 0.16))

    if targets is None:
        # one square bracket spanning cards 1 to 5, stem down to the tile
        xa = cx(1) - CARD_W / 2.0
        xb = cx(5) + CARD_W / 2.0
        ax.add_line(Line2D([xa, xb], [BRACKET_Y, BRACKET_Y],
                           color=GREY_M, linewidth=1.6, zorder=2))
        ax.add_line(Line2D([xa, xa], [BRACKET_Y, CARD_Y],
                           color=GREY_M, linewidth=1.6, zorder=2))
        ax.add_line(Line2D([xb, xb], [BRACKET_Y, CARD_Y],
                           color=GREY_M, linewidth=1.6, zorder=2))
        ax.add_line(Line2D([tcx, tcx], [TILE_Y + TILE_H, BRACKET_Y],
                           color=GREY_M, linewidth=1.6, zorder=2))
    else:
        for card_i, dx in targets:
            bx = cx(card_i) + dx
            by = CARD_Y - (0.45 if card_i == 6 else 0.0)
            mid = 3.60 + 0.30 * _ti
            ax.add_line(Line2D([tcx, tcx, bx, bx],
                               [TILE_Y + TILE_H, mid, mid, by],
                               color=GREY_M, linewidth=1.3,
                               solid_joinstyle="miter", zorder=2))

# ---------------------------------------------------------------- overflow check
fig.canvas.draw()
renderer = fig.canvas.get_renderer()
px_per_unit = FIG_DPI
bad = []
for t, allow in texts_to_measure:
    bb = t.get_window_extent(renderer=renderer)
    if bb.width / px_per_unit > allow:
        bad.append((t.get_text(), round(bb.width / px_per_unit, 2), round(allow, 2)))
if bad:
    for b in bad:
        print("OVERFLOW %-46s drawn %.2f allowed %.2f" % b)
else:
    print("no text overflows its element")

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                   "HETUS_LLM_Pipeline_Steps.png")
fig.savefig(OUT, dpi=FIG_DPI, facecolor="white")
print("written", os.path.normpath(OUT), int(W * FIG_DPI), "x", int(H * FIG_DPI))
