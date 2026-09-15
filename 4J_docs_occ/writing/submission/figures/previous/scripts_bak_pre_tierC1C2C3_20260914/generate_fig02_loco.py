# -*- coding: utf-8 -*-
"""Figure 2 - the leave-one-country-out design and the two nulls.

Built in code on 2026-09-14 on the author's instruction, after four generator
rounds failed on the one thing the figure exists to prove: FINDING 276 /
FINDING 287 / FINDING 290, an arrow ARRIVING at the published-marginals box
instead of leaving it, which reads as the method producing the reference.

Every string is copied verbatim from the frozen 29-entry TEXT INVENTORY of
`Prompts_Images/4thJ_figure02_loco_design.md` Section 12, and every number is
the measured value.  No value is altered.  House palette only.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from matplotlib.lines import Line2D

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
plt.rcParams["hatch.linewidth"] = 1.1

ROSE, INDIGO, TEAL, SAND, WINE = "#CC6677", "#332288", "#44AA99", "#DDCC77", "#882255"
GREY_L, GREY_M, INK = "#F2F2F2", "#D0D0D0", "#111111"


def tint(h, f):
    r, g, b = int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)
    return "#%02X%02X%02X" % (int(255 - (255 - r) * f),
                              int(255 - (255 - g) * f),
                              int(255 - (255 - b) * f))


W, H, DPI = 22.0, 7.3, 175
fig = plt.figure(figsize=(W, H), dpi=DPI)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W); ax.set_ylim(1.70, 9.00); ax.set_aspect("equal"); ax.axis("off")
fig.patch.set_facecolor("white")

measure = []


def T(x, y, s, size, ha="center", color=INK, weight="normal", allow=None, zorder=6):
    t = ax.text(x, y, s, ha=ha, va="center", fontsize=size, color=color,
                weight=weight, zorder=zorder)
    if allow:
        measure.append((t, allow))
    return t


def box(x, y, w, h, fc="white", ec=INK, lw=1.6, hatch=None, r=0.18, z=3):
    p = FancyBboxPatch((x, y), w, h,
                       boxstyle="round,pad=0,rounding_size=%s" % r,
                       facecolor=fc, edgecolor=ec, linewidth=lw, zorder=z)
    if hatch:
        p.set_hatch(hatch)
    ax.add_patch(p)
    return p


# ============================================================ GROUP ONE (left)
TILE_X, TILE_W, TILE_H = 0.65, 2.60, 1.20
box(0.45, 5.55, 3.00, 3.00, fc="none", ec=GREY_M, lw=1.4, r=0.22, z=2)  # enclosure

box(TILE_X, 7.15, TILE_W, TILE_H, fc=ROSE, ec=ROSE, r=0.22, z=3)
T(TILE_X + TILE_W / 2, 7.92, "Spain", 14, color="white", weight="bold", allow=TILE_W - 0.2)
T(TILE_X + TILE_W / 2, 7.46, "training", 11, color="white", allow=TILE_W - 0.2)

box(TILE_X, 5.75, TILE_W, TILE_H, fc=TEAL, ec=TEAL, r=0.22, z=3)
T(TILE_X + TILE_W / 2, 6.52, "Italy", 14, color="white", weight="bold", allow=TILE_W - 0.2)
T(TILE_X + TILE_W / 2, 6.06, "training", 11, color="white", allow=TILE_W - 0.2)

box(TILE_X, 3.80, TILE_W, TILE_H, fc="white", ec=INDIGO, lw=3.2, r=0.22, z=3)
T(TILE_X + TILE_W / 2, 4.57, "United Kingdom", 14, color=INDIGO, weight="bold", allow=TILE_W - 0.2)
T(TILE_X + TILE_W / 2, 4.11, "held out", 11, color=INDIGO, allow=TILE_W - 0.2)

T(1.95, 3.25, u"73,254 diaries · 2,024,068 episodes", 10.5, allow=3.3)

# ============================================== GROUP TWO (middle): shared input
MX, MW = 4.25, 4.20
MY, MH = 3.90, 2.20
box(MX, MY, MW, MH, fc=GREY_L, ec=INK, lw=2.0, r=0.20, z=3)
T(MX + MW / 2, 5.62, "Britain's published census marginals", 12, weight="bold", allow=MW - 0.3)
T(MX + MW / 2, 5.00, u"age · sex · household type · economic status", 10, allow=MW - 0.3)
T(MX + MW / 2, 4.38, "published before either candidate existed", 10, allow=MW - 0.3)

# ============================================== GROUP TWO: the two method boxes
BX, BW, BH = 9.10, 4.30, 1.90
TOP_Y, BOT_Y = 6.60, 2.60

box(BX, TOP_Y, BW, BH, fc="white", ec=INDIGO, lw=2.4, r=0.20, z=3)
T(BX + BW / 2, TOP_Y + 1.25, "Fine-tuned language model", 12.5, weight="bold", allow=BW - 0.3)
T(BX + BW / 2, TOP_Y + 0.62, "7.30 B backbone, low-rank adapter", 10.5, allow=BW - 0.3)

box(BX, BOT_Y, BW, BH, fc="white", ec=WINE, lw=2.4, r=0.20, z=3)
box(BX, BOT_Y, BW, BH, fc=tint(SAND, 0.22), ec=tint(SAND, 0.80), lw=0.0, hatch="///", r=0.20, z=3)
box(BX, BOT_Y, BW, BH, fc="none", ec=WINE, lw=2.4, r=0.20, z=4)
PLATE = dict(facecolor="white", edgecolor="none", boxstyle="square,pad=0.30")
T(BX + BW / 2, BOT_Y + 1.25, "Raked donor pool", 12.5, weight="bold",
  allow=BW - 0.3).set_bbox(PLATE)
T(BX + BW / 2, BOT_Y + 0.62, "real Spanish and Italian diaries, reweighted", 10.5,
  allow=BW - 0.3).set_bbox(PLATE)

# ============================================================ GROUP THREE (right)
SX, SW = 15.60, 4.00
SY, SH = 6.90, 1.70
box(SX, SY, SW, SH, fc="white", ec=INK, lw=1.8, r=0.20, z=3)
T(SX + SW / 2, SY + 1.12, "Time-budget mean absolute error", 12, weight="bold", allow=SW - 0.3)
T(SX + SW / 2, SY + 0.52, "against Britain's published tables", 10.5, allow=SW - 0.3)

BASE = 3.00
SCALE = 3.00 / 65.0
PAIRS = [(58.91, 21.79, "Y25-44", 16.50),
         (60.44, 19.21, "Y45-64", 17.70),
         (21.24, 18.54, "Y_GE65", 18.90)]
BW_BAR, OFF = 0.45, 0.26

ax.add_line(Line2D([SX, SX + SW], [BASE, BASE], color="#000000", linewidth=1.4, zorder=4))
ax.add_line(Line2D([SX, SX], [BASE, 6.30], color="#000000", linewidth=1.4, zorder=4))
T(SX + 0.06, 6.55, "minutes per day, lower is better", 10, ha="left", allow=3.4)

for model_v, null_v, band, pc in PAIRS:
    ax.add_patch(Rectangle((pc - OFF - BW_BAR / 2, BASE), BW_BAR, model_v * SCALE,
                           facecolor=INDIGO, edgecolor="#1D1350", linewidth=1.0, zorder=5))
    p = Rectangle((pc + OFF - BW_BAR / 2, BASE), BW_BAR, null_v * SCALE,
                  facecolor=tint(SAND, 0.85), edgecolor=WINE, linewidth=1.0,
                  hatch="///", zorder=5)
    ax.add_patch(p)
    T(pc - OFF, BASE + model_v * SCALE + 0.20, "%.2f" % model_v, 10)
    T(pc + OFF, BASE + null_v * SCALE + 0.20, "%.2f" % null_v, 10)
    T(pc, BASE - 0.38, band, 10.5)

T(SX + SW / 2, 2.05, "The null wins 9 of 9. Closest miss 2.70 min/day.", 10.5,
  weight="bold", allow=SW)

# ------------------------------------------------------------ ground truth
GX, GY, GW, GH = 20.20, 6.95, 1.50, 1.50
box(GX, GY, GW, GH, fc=GREY_L, ec=GREY_M, lw=1.2, r=0.18, z=3)
for k in range(4):
    yy = GY + GH - 0.32 - k * 0.28
    ax.add_line(Line2D([GX + 0.22, GX + GW - 0.22], [yy, yy],
                       color=GREY_M, linewidth=2.0, zorder=4))
T(GX + GW / 2, GY - 0.38, "ground truth", 10, allow=GW + 0.4)
ax.add_line(Line2D([SX + SW, GX], [7.70, 7.70], color="#999999", linewidth=1.4,
                   linestyle=(0, (4, 3)), zorder=2))

# ================================================================== the arrows
AR = dict(arrowstyle="-|>", mutation_scale=20, linewidth=2.0, color=INK,
          zorder=4, shrinkA=0, shrinkB=0)
heads = []


def elbow(pts, color=INK):
    """polyline with an arrowhead on the final segment only"""
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    ax.add_line(Line2D(xs[:-1], ys[:-1], color=color, linewidth=2.0,
                       solid_joinstyle="miter", zorder=4))
    d = dict(AR); d["color"] = color
    ax.add_patch(FancyArrowPatch(pts[-2], pts[-1], **d))
    heads.append(pts[-1])


# line one: out of the enclosure holding Spain and Italy, forking to both methods
E_X, E_Y = 3.45, 7.05
elbow([(E_X, E_Y), (3.85, E_Y), (3.85, 8.00), (BX, 8.00)])
elbow([(E_X, E_Y), (3.85, E_Y), (3.85, 3.00), (BX, 3.00)])

# line two: OUT of the shared marginals box, forking to both methods.
# this box is a source: no arrowhead touches it anywhere.
elbow([(MX + MW, 5.00), (8.75, 5.00), (8.75, 7.10), (BX, 7.10)])
elbow([(MX + MW, 5.00), (8.75, 5.00), (8.75, 4.00), (BX, 4.00)])

# line three: one arrow from each method box into the scoring box, never merging
elbow([(BX + BW, 7.55), (14.50, 7.55), (14.50, 7.95), (SX, 7.95)])
elbow([(BX + BW, 3.55), (14.50, 3.55), (14.50, 7.15), (SX, 7.15)])

T(14.50, 8.30, "5,200 generated diaries", 10, allow=2.15)
T(14.50, 3.90, "reweighted real diaries", 10, allow=2.15)

# ------------------------------------------------- mechanical arrowhead audit
assert len(heads) == 6, "six arrowheads exactly, got %d" % len(heads)
on_top = [h for h in heads if abs(h[0] - BX) < 1e-9 and TOP_Y <= h[1] <= TOP_Y + BH]
on_bot = [h for h in heads if abs(h[0] - BX) < 1e-9 and BOT_Y <= h[1] <= BOT_Y + BH]
on_sco = [h for h in heads if abs(h[0] - SX) < 1e-9 and SY <= h[1] <= SY + SH]
on_marg = [h for h in heads if MX <= h[0] <= MX + MW and MY <= h[1] <= MY + MH]
print("arrowheads  top method box %d | bottom method box %d | scoring box %d | marginals box %d"
      % (len(on_top), len(on_bot), len(on_sco), len(on_marg)))
assert (len(on_top), len(on_bot), len(on_sco), len(on_marg)) == (2, 2, 2, 0)

fig.canvas.draw()
r = fig.canvas.get_renderer()
bad = [(t.get_text(), t.get_window_extent(renderer=r).width / DPI, a)
       for t, a in measure if t.get_window_extent(renderer=r).width / DPI > a]
for s, got, a in bad:
    print("OVERFLOW %-48s drawn %.2f allowed %.2f" % (s, got, a))
if not bad:
    print("no text overflows its element")

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                   "Figure_02_loco_design.png")
fig.savefig(OUT, dpi=DPI, facecolor="white")
print("written", os.path.normpath(OUT), int(W * DPI), "x", int(H * DPI))
