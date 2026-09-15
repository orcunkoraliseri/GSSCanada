# -*- coding: utf-8 -*-
"""Graphical abstract - HETUS_LLM_CrossNational_Pipeline.png

Built in code on 2026-09-14 on the author's instruction, after four generator
rounds failed on the one thing the picture must say: FINDING 288 / FINDING 291,
the held-out lane touching the model block, which reads as the held-out country
being trained on - the opposite of the paper's only result.

Every string is copied verbatim from the frozen 28-entry TEXT INVENTORY of
`Prompts_Images/4thJ_graphical_abstract.md` Section 10.  House palette only.
The held-out gap is asserted numerically before the file is written.
"""
import os
import math
import random
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import (FancyBboxPatch, Rectangle, Circle, Polygon,
                                FancyArrowPatch, Wedge)
from matplotlib.lines import Line2D

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]

ROSE, INDIGO, TEAL, SAND, WINE = "#CC6677", "#332288", "#44AA99", "#DDCC77", "#882255"
GREY_L, GREY_M, INK = "#F2F2F2", "#D0D0D0", "#111111"
NAVY = "#241A5E"


def tint(h, f):
    r, g, b = int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)
    return "#%02X%02X%02X" % (int(255 - (255 - r) * f),
                              int(255 - (255 - g) * f),
                              int(255 - (255 - b) * f))


W, H, DPI = 31.5, 12.2, 125
fig = plt.figure(figsize=(W, H), dpi=DPI)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W); ax.set_ylim(2.75, 14.95); ax.set_aspect("equal"); ax.axis("off")
fig.patch.set_facecolor("white")

measure = []


def T(x, y, s, size, ha="center", color=INK, weight="normal", allow=None, z=6):
    t = ax.text(x, y, s, ha=ha, va="center", fontsize=size, color=color,
                weight=weight, zorder=z)
    if allow:
        measure.append((t, allow))
    return t


def box(x, y, w, h, fc="white", ec=INK, lw=1.5, r=0.18, z=3, ls="solid"):
    p = FancyBboxPatch((x, y), w, h,
                       boxstyle="round,pad=0,rounding_size=%s" % r,
                       facecolor=fc, edgecolor=ec, linewidth=lw,
                       linestyle=ls, zorder=z)
    ax.add_patch(p)
    return p


# ===================================================================== titles
T(W / 2, 14.45, "Cross-National Occupancy Generation with a Fine-Tuned Open-Weight LLM",
  22, weight="bold", allow=W - 2)
T(W / 2, 13.70,
  "Beaten by Real Diaries: A Pre-Registered Leave-One-Country-Out Test of a Fine-Tuned "
  "Language Model for Cross-National Occupancy Generation (HETUS; Spain, Italy, United Kingdom)",
  14, allow=W - 2)

# ================================================================= left panel
PX, PW = 0.45, 4.75
box(PX, 6.20, PW, 6.40, fc="#F8F8F8", ec=GREY_M, lw=1.2, r=0.25, z=1)

CW = PW - 0.50
CX = PX + 0.25


def icon_calendar(x, y, s):
    ax.add_patch(FancyBboxPatch((x, y), s, s * 0.88,
                                boxstyle="round,pad=0,rounding_size=0.06",
                                facecolor="white", edgecolor=INDIGO, lw=1.6, zorder=5))
    ax.add_patch(Rectangle((x, y + s * 0.62), s, s * 0.26,
                           facecolor=INDIGO, edgecolor=INDIGO, zorder=5))
    for r_ in range(2):
        for c_ in range(3):
            ax.add_patch(Rectangle((x + 0.11 + c_ * 0.20, y + 0.13 + r_ * 0.20),
                                   0.10, 0.10, facecolor=INDIGO,
                                   edgecolor="none", zorder=6))


def icon_document(x, y, s):
    ax.add_patch(Polygon([(x, y), (x, y + s), (x + s * 0.68, y + s),
                          (x + s * 0.88, y + s * 0.78), (x + s * 0.88, y)],
                         closed=True, facecolor="white", edgecolor=INDIGO,
                         lw=1.6, zorder=5))
    for k in range(3):
        yy = y + 0.20 + k * 0.19
        ax.add_line(Line2D([x + 0.14, x + s * 0.72], [yy, yy],
                           color=INDIGO, lw=1.3, zorder=6))


def icon_people(x, y, s):
    for k, dx in enumerate((0.20, 0.58)):
        ax.add_patch(Circle((x + dx, y + s * 0.74), 0.135, facecolor=INDIGO,
                            edgecolor="none", zorder=5))
        ax.add_patch(Wedge((x + dx, y + s * 0.30), 0.27, 0, 180,
                           facecolor=INDIGO, edgecolor="none", zorder=5))


CARDS = [("National time-use surveys", 10.55, icon_calendar),
         ("HETUS framework", 8.65, icon_document),
         ("Census and population marginals", 6.75, icon_people)]
for label, cy, icon in CARDS:
    box(CX, cy, CW, 1.55, fc="white", ec=GREY_M, lw=1.3, r=0.16, z=4)
    icon(CX + 0.26, cy + 0.42, 0.72)
    T(CX + 1.22, cy + 0.775, label, 10.5, ha="left", weight="bold", allow=CW - 1.38)

# ====================================================================== lanes
LANE_X = 5.45
NB_X, NB_W = 15.60, 5.90
NB_Y, NB_H = 7.30, 5.10
HELD_GAP = 0.10 * W                       # the rule: one tenth of the image width
LANE3_END = NB_X - HELD_GAP

LANES = [("Country A", TEAL,  11.05, 1.30, NB_X,     "solid"),
         ("Country B", SAND,   9.45, 1.30, NB_X,     "solid"),
         ("Country C - held out", ROSE, 7.85, 1.30, LANE3_END, "dashed")]

for name, col, ly, lh, lend, ls in LANES:
    ax.add_patch(FancyBboxPatch((LANE_X, ly), lend - LANE_X, lh,
                                boxstyle="round,pad=0,rounding_size=0.20",
                                facecolor=tint(col, 0.22), edgecolor=col,
                                linewidth=1.8,
                                linestyle=(0, (6, 4)) if ls == "dashed" else "solid",
                                zorder=2))
    tile_w = 2.60
    box(LANE_X + 0.22, ly + 0.22, tile_w, lh - 0.44, fc="white", ec=GREY_M,
        lw=1.3, r=0.14, z=3)
    T(LANE_X + 0.22 + tile_w / 2, ly + lh / 2, name, 10.5, weight="bold",
      allow=tile_w - 0.2)
    T(9.62, ly + lh / 2, "episode diary", 11, allow=2.3)
    T(11.65, ly + lh / 2, "serialised record", 11, allow=2.5)
    for ax_ in (8.40, 10.45):
        if ax_ + 0.55 < lend:
            ax.add_patch(FancyArrowPatch((ax_, ly + lh / 2), (ax_ + 0.55, ly + lh / 2),
                                         arrowstyle="-|>", mutation_scale=15,
                                         linewidth=1.5, color=INK, zorder=4))

# ============================================================ the navy block
box(NB_X, NB_Y, NB_W, NB_H, fc=NAVY, ec=NAVY, lw=1.0, r=0.28, z=3)
T(NB_X + NB_W / 2, NB_Y + NB_H - 0.65,
  "One open-weight LLM, one recipe per held-out country", 12.5,
  color="white", weight="bold", allow=NB_W - 0.4)

# schematic transformer motif: four stacked layer bars, a fan between two of them
MB_X, MB_W = NB_X + 1.35, NB_W - 2.70
for k in range(4):
    yy = NB_Y + 1.95 + k * 0.42
    ax.add_patch(Rectangle((MB_X, yy), MB_W, 0.26,
                           facecolor="#6C63A8" if k % 2 else "#4A3F86",
                           edgecolor="none", zorder=4))
for a in range(6):
    for b in range(6):
        if (a + b) % 2 == 0:
            ax.add_line(Line2D([MB_X + 0.25 + a * (MB_W - 0.5) / 5.0,
                                MB_X + 0.25 + b * (MB_W - 0.5) / 5.0],
                               [NB_Y + 2.37, NB_Y + 2.79],
                               color="#8F87C4", lw=0.7, zorder=5))
ax.add_line(Line2D([MB_X + MB_W, MB_X + MB_W + 0.45],
                   [NB_Y + 2.60, NB_Y + 2.60], color="#8F87C4", lw=1.2, zorder=4))
box(MB_X + MB_W + 0.45, NB_Y + 2.32, 1.70, 0.56, fc="white", ec="white",
    lw=0.0, r=0.20, z=5)
T(MB_X + MB_W + 1.30, NB_Y + 2.60, "low-rank adapter", 9.5, color=NAVY,
  weight="bold", allow=1.6)
T(NB_X + NB_W / 2, NB_Y + 1.22, "conditioned on country, demographics, day type",
  10.5, color="white", allow=NB_W - 0.4)
T(NB_X + NB_W / 2, NB_Y + 0.62, "trained on the other two", 10.5,
  color="white", allow=NB_W - 0.4)

# ====================================== the short chain below the navy block
CH_Y, CH_H = 4.35, 1.15
box(15.60, CH_Y, 2.80, CH_H, fc=GREY_L, ec=INK, lw=1.4, r=0.16, z=3)
T(17.00, CH_Y + CH_H / 2, "published marginals", 10.5, allow=2.6)
box(20.90, CH_Y, 2.80, CH_H, fc=GREY_L, ec=INK, lw=1.4, r=0.16, z=3)
T(22.30, CH_Y + CH_H / 2, "synthetic population", 10.5, allow=2.6)
ax.add_patch(FancyArrowPatch((18.40, CH_Y + CH_H / 2), (20.90, CH_Y + CH_H / 2),
                             arrowstyle="-|>", mutation_scale=16, linewidth=1.6,
                             color=INK, zorder=4))
T(19.65, CH_Y + CH_H / 2 + 0.48, "iterative proportional fitting", 9.8, allow=2.4)

# ==================================================== the generation area (right)
GA_X, GA_W = 24.30, 6.50
RIBBONS = [(TEAL,  12.25, "solid"),
           (SAND,  11.45, "solid"),
           (ROSE,  10.65, "dashed")]
rng = random.Random(4)
for idx, (col, ry, ls) in enumerate(RIBBONS):
    rh = 0.58
    segs = []
    total = 0.0
    n = 22 + idx * 3
    for _ in range(n):
        v = 0.4 + rng.random()
        segs.append(v); total += v
    xx = GA_X + 0.55
    span = GA_W - 1.15
    for j, v in enumerate(segs):
        wseg = v / total * span
        shade = tint(col, 0.28 + 0.62 * ((j * 7 + idx * 3) % 5) / 4.0)
        ax.add_patch(Rectangle((xx, ry), wseg, rh, facecolor=shade,
                               edgecolor="white", linewidth=0.35, zorder=4))
        xx += wseg
    if ls == "dashed":
        ax.add_patch(Rectangle((GA_X + 0.55, ry), span, rh, facecolor="none",
                               edgecolor=col, linewidth=1.8,
                               linestyle=(0, (5, 3)), zorder=5))
    T(GA_X + 0.28, ry + rh / 2, "00", 9.5, allow=0.5)
    T(GA_X + GA_W - 0.28, ry + rh / 2, "24", 9.5, allow=0.5)

HB_X, HB_Y, HB_W, HB_H = GA_X, 8.30, GA_W, 1.75
box(HB_X, HB_Y, HB_W, HB_H, fc="white", ec=ROSE, lw=1.8, r=0.16, z=3,
    ls=(0, (5, 3)))
T(HB_X + HB_W / 2, HB_Y + 1.32, "held-out country", 11.5, weight="bold",
  allow=HB_W - 0.3)
T(HB_X + HB_W / 2, HB_Y + 0.82, "generated from published marginals only", 10,
  allow=HB_W - 0.3)
T(HB_X + HB_W / 2, HB_Y + 0.34, "compared against reweighted real diaries", 10,
  allow=HB_W - 0.3)

# the chain's arrow leaves the synthetic population and turns UP into that area
ax.add_line(Line2D([23.70, 23.90, 23.90], [CH_Y + CH_H / 2, CH_Y + CH_H / 2, 9.15],
                   color=INK, lw=1.6, solid_joinstyle="miter", zorder=4))
ax.add_patch(FancyArrowPatch((23.90, 9.15), (HB_X, 9.15), arrowstyle="-|>",
                             mutation_scale=16, linewidth=1.6, color=INK, zorder=4))

# ============================ lane three: down, under the block, up to ribbon 3
L3_Y = 7.85 + 1.30 / 2.0
BYPASS_Y = 6.30
RISER_X = 23.35
ax.add_line(Line2D([LANE3_END, LANE3_END, RISER_X, RISER_X, 25.60],
                   [L3_Y, BYPASS_Y, BYPASS_Y, 10.30, 10.30],
                   color=ROSE, lw=1.8, linestyle=(0, (5, 3)),
                   solid_joinstyle="miter", zorder=2))
ax.add_patch(FancyArrowPatch((25.60, 10.30), (25.60, 10.63),
                             arrowstyle="-|>", mutation_scale=15, linewidth=1.8,
                             color=ROSE, zorder=6))
T(LANE3_END - 1.60, BYPASS_Y + 0.78, "each country is held out in turn", 9.8,
  allow=3.2)
T(LANE3_END - 1.60, BYPASS_Y + 0.32, "never seen in training", 9.8, allow=3.2)

# ================================================================== right edge
RE_X, RE_W = GA_X, GA_W

# the small plan of packed footprints, behind and slightly right of the row
plan_x, plan_y = 28.35, 5.95
FOOT = [(0.00, 0.00, 0.78, 0.62), (0.83, 0.08, 0.60, 0.54),
        (1.48, 0.00, 0.70, 0.74), (0.04, 0.68, 0.66, 0.60),
        (0.75, 0.66, 0.62, 0.70), (1.42, 0.79, 0.74, 0.57)]
for (fx, fy, fw, fh) in FOOT:
    ax.add_patch(Rectangle((plan_x + fx, plan_y + fy), fw, fh, facecolor="none",
                           edgecolor="#BBBBBB", linewidth=1.0, zorder=1))
# one footprint is divided into six cells, and those cells fill it edge to edge
sx, sy, sw, sh = plan_x + 0.04, plan_y + 1.40, 2.12, 0.74
ax.add_patch(Rectangle((sx, sy), sw, sh, facecolor="none", edgecolor="#999999",
                       linewidth=1.2, zorder=1))
cw, ch = sw / 3.0, sh / 2.0
for i in range(3):
    for j in range(2):
        ax.add_patch(Rectangle((sx + i * cw, sy + j * ch), cw, ch, facecolor="none",
                               edgecolor="#BBBBBB", linewidth=0.8, zorder=1))
MK = "#999999"


def mark(k, x, y):
    """six different little marks; none of the six is a checkmark or a tick"""
    if k == 0:                                   # short zigzag
        ax.add_line(Line2D([x - .14, x - .05, x + .05, x + .14],
                           [y - .07, y + .07, y - .07, y + .07],
                           color=MK, lw=1.1, zorder=2))
    elif k == 1:                                 # wave
        xs = [x - .16 + t * .032 for t in range(11)]
        ax.add_line(Line2D(xs, [y + .07 * math.sin(t * 1.3) for t in range(11)],
                           color=MK, lw=1.1, zorder=2))
    elif k == 2:                                 # dot
        ax.add_patch(Circle((x, y), 0.055, facecolor=MK, edgecolor="none", zorder=2))
    elif k == 3:                                 # small cross
        ax.add_line(Line2D([x - .10, x + .10], [y - .10, y + .10],
                           color=MK, lw=1.1, zorder=2))
        ax.add_line(Line2D([x - .10, x + .10], [y + .10, y - .10],
                           color=MK, lw=1.1, zorder=2))
    elif k == 4:                                 # short bar
        ax.add_line(Line2D([x - .13, x + .13], [y, y], color=MK, lw=1.6, zorder=2))
    else:                                        # small spiral
        xs, ys = [], []
        for t in range(40):
            a_ = t * 0.38
            r_ = 0.010 + a_ * 0.016
            xs.append(x + r_ * math.cos(a_)); ys.append(y + r_ * math.sin(a_))
        ax.add_line(Line2D(xs, ys, color=MK, lw=0.9, zorder=2))


k = 0
for j in (1, 0):
    for i in range(3):
        mark(k, sx + (i + 0.5) * cw, sy + (j + 0.5) * ch)
        k += 1

# a flat row of four European residential building types
BR_Y = 6.15


def building(x, w, kind):
    if kind == 0:      # detached, pitched roof
        ax.add_patch(Rectangle((x, BR_Y), w, 0.85, facecolor=tint(INDIGO, 0.12),
                               edgecolor=INDIGO, linewidth=1.3, zorder=4))
        ax.add_patch(Polygon([(x - 0.08, BR_Y + 0.85), (x + w / 2, BR_Y + 1.35),
                              (x + w + 0.08, BR_Y + 0.85)], closed=True,
                             facecolor=tint(INDIGO, 0.30), edgecolor=INDIGO,
                             linewidth=1.3, zorder=4))
    elif kind == 1:    # terrace
        for t in range(3):
            ax.add_patch(Rectangle((x + t * w / 3.0, BR_Y), w / 3.0, 1.05,
                                   facecolor=tint(INDIGO, 0.10), edgecolor=INDIGO,
                                   linewidth=1.1, zorder=4))
    elif kind == 2:    # mid-rise block
        ax.add_patch(Rectangle((x, BR_Y), w, 1.45, facecolor=tint(INDIGO, 0.14),
                               edgecolor=INDIGO, linewidth=1.3, zorder=4))
        for r_ in range(3):
            for c_ in range(3):
                ax.add_patch(Rectangle((x + 0.12 + c_ * (w - 0.34) / 3.0,
                                        BR_Y + 0.18 + r_ * 0.40),
                                       0.16, 0.22, facecolor="white",
                                       edgecolor="none", zorder=5))
    else:              # tower
        ax.add_patch(Rectangle((x, BR_Y), w * 0.72, 1.85,
                               facecolor=tint(INDIGO, 0.18), edgecolor=INDIGO,
                               linewidth=1.3, zorder=4))
        for r_ in range(4):
            ax.add_patch(Rectangle((x + 0.10, BR_Y + 0.20 + r_ * 0.40),
                                   w * 0.72 - 0.20, 0.20, facecolor="white",
                                   edgecolor="none", zorder=5))


bx = RE_X + 0.15
for kind, bw in enumerate((0.95, 1.05, 0.95, 0.80)):
    building(bx, bw, kind)
    bx += bw + 0.10

# three schedule curves, one per lane colour, side by side in small white boxes
CBW, CBH, CBY = 2.10, 1.05, 4.30
CURVE = [(TEAL, RE_X), (SAND, RE_X + 2.20), (ROSE, RE_X + 4.40)]
for ci, (col, cbx) in enumerate(CURVE):
    box(cbx, CBY, CBW, CBH, fc="white", ec=GREY_M, lw=1.1, r=0.10, z=3)
    xs, ys = [], []
    for t in range(97):
        h_ = t / 4.0
        if ci == 0:
            v = 0.55 + 0.42 * math.sin((h_ - 6) / 24.0 * 2 * math.pi)
        elif ci == 1:
            v = (0.30 + 0.60 * math.exp(-((h_ - 8.0) ** 2) / 6.0)
                 + 0.55 * math.exp(-((h_ - 20.0) ** 2) / 9.0))
        else:
            v = 0.25 + 0.65 * math.exp(-((h_ - 14.0) ** 2) / 26.0)
        v = max(0.05, min(0.95, v))
        xs.append(cbx + 0.34 + (CBW - 0.72) * h_ / 24.0)
        ys.append(CBY + 0.16 + 0.72 * v)
    ax.add_line(Line2D(xs, ys, color=col, lw=1.8, zorder=5))
    T(cbx + 0.17, CBY + CBH / 2, "0", 9, allow=0.28)
    T(cbx + CBW - 0.19, CBY + CBH / 2, "24", 9, allow=0.38)

T(RE_X + RE_W / 2, 3.70, "occupancy-driven internal gains", 10, allow=RE_W)
T(RE_X + RE_W / 2, 3.18, "EnergyPlus schedules, one diary per dwelling", 10,
  allow=RE_W)

# ============================================ the rule this figure exists for
gap = NB_X - LANE3_END
if gap < 0.10 * W - 1e-9:
    raise SystemExit("ABORT: held-out lane gap %.2f is under one tenth of the width" % gap)
print("held-out lane stops %.2f in (%.1f%% of the image width) short of the model block"
      % (gap, 100.0 * gap / W))

fig.canvas.draw()
r = fig.canvas.get_renderer()
bad = [(t.get_text(), t.get_window_extent(renderer=r).width / DPI, a)
       for t, a in measure if t.get_window_extent(renderer=r).width / DPI > a]
for s_, got, a in bad:
    print("OVERFLOW %-46s drawn %.2f allowed %.2f" % (s_[:46], got, a))
if not bad:
    print("no text overflows its element")

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                   "HETUS_LLM_CrossNational_Pipeline.png")
fig.savefig(OUT, dpi=DPI, facecolor="white")
print("written", os.path.normpath(OUT), int(W * DPI), "x", int(H * DPI))
