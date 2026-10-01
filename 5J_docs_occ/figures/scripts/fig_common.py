# -*- coding: utf-8 -*-
"""Shared style and helpers for the 5J Step 8 data figures (Figures 2 to 4). Speed job only (matplotlib, Agg).
House style follows generate_5J_graphical_abstract.py: sans-serif (Arial, else DejaVu Sans), text >= 8 pt, PDF fonts embedded (type 42).
"""
import hashlib, io, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "DejaVu Sans", "Helvetica"],
    "font.size": 8, "axes.labelsize": 8, "axes.titlesize": 8, "xtick.labelsize": 8, "ytick.labelsize": 8,
    "legend.fontsize": 8, "figure.dpi": 100, "savefig.dpi": 300,
    "pdf.fonttype": 42, "ps.fonttype": 42,
    "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
    "xtick.major.size": 2.5, "ytick.major.size": 2.5, "axes.spines.top": False, "axes.spines.right": False,
    "lines.linewidth": 0.8, "axes.edgecolor": "#111111", "axes.labelcolor": "#111111", "text.color": "#111111",
    "xtick.color": "#111111", "ytick.color": "#111111",
})
MM = 1.0 / 25.4
W1, W2 = 90 * MM, 190 * MM
TEXT = "#111111"
GRID = "#E2E8F0"
BAND = "#111111"
# models
MODEL_COLOUR = {"S": "#0F2942", "C": "#64748B", "B1": "#E69F00", "B0": "#56B4E9"}
MODEL_MARKER = {"S": "o", "C": "s", "B1": "^", "B0": "D"}
# test lists
LISTS = ["test_new_households", "test_new_buildings", "test_both_new"]
LIST_NAME = {"test_new_households": "New households", "test_new_buildings": "New buildings", "test_both_new": "Both new"}
LIST_COLOUR = {"test_new_households": "#0072B2", "test_new_buildings": "#E69F00", "test_both_new": "#CC79A7"}
COUNTRIES = ["es", "it"]
CLASSES = ["SFH", "TH", "MFH", "AB"]
CELLS = [(c, k) for c in COUNTRIES for k in CLASSES]
CELL_X = [0.0, 1.0, 2.0, 3.0, 4.8, 5.8, 6.8, 7.8]          # a gap between Spain and Italy
COUNTRY_NAME = {"es": "Spain", "it": "Italy"}
TARGETS = ["heating", "cooling", "equipment", "total_elec"]
TARGET_NAME = {"heating": "Heating", "cooling": "Cooling", "equipment": "Equipment", "total_elec": "Total electricity"}


def md5_file(p):
    h = hashlib.md5()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def cell_axis(ax, bottom):
    """x axis of a country x class dot plot: class ticks, country names under the bottom row."""
    ax.set_xlim(-0.7, 8.5)
    ax.set_xticks(CELL_X)
    ax.set_xticklabels([k for _, k in CELLS] if bottom else [], rotation=90 if bottom else 0)
    ax.tick_params(axis="x", length=2.5 if bottom else 0)
    ax.grid(axis="y", color=GRID, lw=0.5, zorder=0)
    ax.set_axisbelow(True)
    if bottom:
        tr = ax.get_xaxis_transform()
        ax.text(1.5, -0.62, COUNTRY_NAME["es"], transform=tr, ha="center", va="top", fontsize=8)
        ax.text(6.3, -0.62, COUNTRY_NAME["it"], transform=tr, ha="center", va="top", fontsize=8)
        # y = -0.62 of the axis height clears the rotated class labels (about 0.35 of the height)


def save_figure(fig, stem, outdir, inputs, extra_lines=()):
    """Writes <outdir>/<stem>.png (300 dpi) and .pdf, and <outdir>/<stem>.md5.txt (md5 of both images and of every input table)."""
    os.makedirs(outdir, exist_ok=True)
    png, pdf = os.path.join(outdir, stem + ".png"), os.path.join(outdir, stem + ".pdf")
    fig.savefig(png, dpi=300, facecolor="white")
    fig.savefig(pdf, facecolor="white")
    with io.open(os.path.join(outdir, stem + ".md5.txt"), "w", encoding="utf-8") as fh:
        fh.write("%s  %s.png\n%s  %s.pdf\n" % (md5_file(png), stem, md5_file(pdf), stem))
        for p in inputs:
            fh.write("%s  INPUT %s\n" % (md5_file(p), p))
        for ln in extra_lines:
            fh.write(ln + "\n")
    return png, pdf
