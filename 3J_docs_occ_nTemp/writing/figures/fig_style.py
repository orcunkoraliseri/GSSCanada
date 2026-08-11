#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fig_style.py -- shared palette and drawing helpers for the eight 3J schematic figures.

Flat style only: no gradients, no shadows, no 3D. One palette, reused across all
eight scripts so they read as one visual family. Coordinates for every figure are
plain "inches" (ax.set_xlim/ylim matches the figsize), which keeps box placement
readable as layout arithmetic instead of fractions.

Determinism (this feeds f5_figure_check.py's C2 arm): PDF output must not embed a
build timestamp, or re-running the same script produces a different md5 even though
nothing changed. save_both() below explicitly suppresses PDF CreationDate/ModDate.
No random numbers, no wall-clock text, are used anywhere in the eight scripts.
"""

import hashlib
import os
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon, Rectangle
from matplotlib.path import Path as MplPath

# ---------------------------------------------------------------------------
# Palette (exact hex values from the implementation plan, step 1)
# ---------------------------------------------------------------------------
SLATE = "#4A6E82"   # Leg-2 inherited / GSS
AMBER = "#C08A2E"   # Leg-3 added / non-GSS
TEAL = "#4E8A7E"
GREY = "#8A8073"    # warm neutral
INK = "#23262A"
WHITE = "#FFFFFF"

# Supporting neutrals: tints of the five palette colours, used only for panel
# backgrounds / bands / dashed boundaries, never as a new hue.
PANEL_BG = "#F5F2EC"       # very light warm-grey, for background bands/panels
LIGHT_GREY = "#DCD5C8"     # service/MEP band (Figure S1), lighter than GREY
DASH_AMBER = "#C08A2E"     # dashed lane / boundary uses AMBER at reduced alpha

# The ONE explicitly sanctioned non-palette accent (Figure 5 wiring-gate card only,
# per that prompt file's Layout notes: "its own restrained red-brown outline accent").
GATE_RED = "#8C3A2B"

FONT = "DejaVu Sans"   # matplotlib default sans-serif, always available
matplotlib.rcParams["font.family"] = FONT
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["svg.fonttype"] = "none"


def wrap_text(s, width_chars):
    """Manually wrap a canonical label string at width_chars, inserting real newlines.

    matplotlib's `wrap=True` text argument only reflows against the figure's outer
    edge at draw time, not against a box -- it does not prevent text overflowing a
    box's own boundary. Every box/box_multi/diamond call in the eight scripts wraps
    its text explicitly with this function instead. The un-wrapped original string
    (with no inserted newline) is what belongs in each script's LABELS registry, so
    f5_figure_check.py can whitespace-normalize before comparing.
    """
    return "\n".join(textwrap.wrap(s, width=width_chars, break_long_words=False, break_on_hyphens=False))


def new_fig(w, h):
    """Return (fig, ax) with a plain white ground and axis off, in w x h 'inches'."""
    fig = plt.figure(figsize=(w, h), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor(WHITE)
    ax.set_facecolor(WHITE)
    return fig, ax


def box(ax, x, y, w, h, text, subtext=None, facecolor=SLATE, edgecolor=INK,
        textcolor=WHITE, fontsize=9.5, subfontsize=7.5, dashed=False, lw=1.3,
        rounding=0.10, zorder=3, ha="center", subtextcolor=None):
    """Flat rounded-rectangle box, (x, y) = lower-left corner, w/h in figure units."""
    style = "round,pad=0.0,rounding_size=%.3f" % (rounding * min(w, h))
    patch = FancyBboxPatch((x, y), w, h, boxstyle=style, linewidth=lw,
                            edgecolor=edgecolor, facecolor=facecolor,
                            linestyle="dashed" if dashed else "solid",
                            zorder=zorder)
    ax.add_patch(patch)
    cx = x + w / 2.0
    if subtext:
        ax.text(cx, y + h * 0.62, text, ha="center", va="center", fontsize=fontsize,
                 color=textcolor, weight="bold", zorder=zorder + 1, linespacing=1.15)
        ax.text(cx, y + h * 0.28, subtext, ha="center", va="center", fontsize=subfontsize,
                 color=subtextcolor or textcolor, zorder=zorder + 1, linespacing=1.15)
    else:
        ax.text(cx, y + h / 2.0, text, ha="center", va="center", fontsize=fontsize,
                 color=textcolor, weight="bold", zorder=zorder + 1, linespacing=1.15)
    return patch


def box_multi(ax, x, y, w, h, segments, text, subtext=None, edgecolor=INK, textcolor=WHITE,
              fontsize=8.6, subfontsize=6.8, lw=1.3, rounding=0.10, zorder=3, inset=0.035,
              subtextcolor=None):
    """Box whose fill is split into vertical colour stripes (multi-channel boxes 3/4/5/7).

    segments: list of (fraction, color) left to right, fractions sum to 1.0.
    Inner stripes are inset slightly so they never poke past the rounded outline.
    """
    ix, iy, iw, ih = x + inset, y + inset, w - 2 * inset, h - 2 * inset
    cx = ix
    for frac, color in segments:
        seg_w = iw * frac
        ax.add_patch(Rectangle((cx, iy), seg_w, ih, facecolor=color, edgecolor="none", zorder=zorder))
        cx += seg_w
    style = "round,pad=0.0,rounding_size=%.3f" % (rounding * min(w, h))
    outline = FancyBboxPatch((x, y), w, h, boxstyle=style, linewidth=lw, edgecolor=edgecolor,
                              facecolor="none", zorder=zorder + 1)
    ax.add_patch(outline)
    tx = x + w / 2.0
    if subtext:
        ax.text(tx, y + h * 0.62, text, ha="center", va="center", fontsize=fontsize,
                 color=textcolor, weight="bold", zorder=zorder + 2, linespacing=1.15)
        ax.text(tx, y + h * 0.28, subtext, ha="center", va="center", fontsize=subfontsize,
                 color=subtextcolor or textcolor, zorder=zorder + 2, linespacing=1.15)
    else:
        ax.text(tx, y + h / 2.0, text, ha="center", va="center", fontsize=fontsize,
                 color=textcolor, weight="bold", zorder=zorder + 2, linespacing=1.15)
    return outline


def diamond(ax, cx, cy, w, h, text, facecolor=SLATE, edgecolor=INK, textcolor=WHITE,
            fontsize=9.5, lw=1.3, zorder=3):
    """Flat diamond decision box centred at (cx, cy)."""
    pts = [(cx, cy + h / 2.0), (cx + w / 2.0, cy), (cx, cy - h / 2.0), (cx - w / 2.0, cy)]
    patch = Polygon(pts, closed=True, facecolor=facecolor, edgecolor=edgecolor,
                     linewidth=lw, zorder=zorder)
    ax.add_patch(patch)
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fontsize, color=textcolor,
             weight="bold", zorder=zorder + 1, linespacing=1.15)
    return patch


def arrow(ax, start, end, color=INK, lw=1.6, dashed=False, connectionstyle=None,
          zorder=2, mutation_scale=14):
    """Thin straight (or curved, via connectionstyle) connector with a small arrowhead."""
    patch = FancyArrowPatch(start, end, arrowstyle="-|>", color=color, linewidth=lw,
                             linestyle="dashed" if dashed else "solid",
                             connectionstyle=connectionstyle, mutation_scale=mutation_scale,
                             zorder=zorder, shrinkA=0, shrinkB=0)
    ax.add_patch(patch)
    return patch


def lane(ax, x, y, w, h, edgecolor=AMBER, facecolor="none", dashed=True, lw=1.4, zorder=1):
    """Dashed boundary rectangle marking a separate lane/side-track region."""
    patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.0,rounding_size=0.08",
                            linewidth=lw, edgecolor=edgecolor, facecolor=facecolor,
                            linestyle="dashed" if dashed else "solid", zorder=zorder)
    ax.add_patch(patch)
    return patch


def legend_swatches(ax, x, y, items, sw=0.28, sh=0.20, gap_x=1.9, fontsize=8.0,
                     textcolor=INK):
    """items: list of (color, label). Draws small square swatches left to right."""
    cx = x
    for color, label in items:
        ax.add_patch(Rectangle((cx, y), sw, sh, facecolor=color, edgecolor=INK, linewidth=0.8, zorder=4))
        ax.text(cx + sw + 0.08, y + sh / 2.0, label, ha="left", va="center", fontsize=fontsize,
                 color=textcolor, zorder=4)
        cx += gap_x
    return cx


def title_banner(ax, w, y, text, fontsize=13.5, color=INK):
    ax.text(w / 2.0, y, text, ha="center", va="center", fontsize=fontsize, color=color,
             weight="bold")


def footnote(ax, w, y, text, fontsize=6.6, color=INK, ha="center", x=None):
    ax.text(x if x is not None else w / 2.0, y, text, ha=ha, va="bottom", fontsize=fontsize,
            color=color, wrap=True)


def save_both(fig, out_path_no_ext, dpi=300):
    """Write <out_path_no_ext>.pdf and .png, both build-deterministic.

    `dpi` applies to the PNG only (the PDF is vector). It defaults to 300 so every
    existing caller is byte-unchanged; pass a higher value for figures that must
    clear a journal's raster minimum at printed width. Elsevier asks 500 dpi for
    combination art, so a figure drawn W inches wide and placed at ~7 in on the
    page needs dpi >= 500 * 7 / W.
    """
    os.makedirs(os.path.dirname(out_path_no_ext), exist_ok=True)
    pdf_path = out_path_no_ext + ".pdf"
    png_path = out_path_no_ext + ".png"
    # Suppress PDF /CreationDate and /ModDate so the byte stream (and its md5) is
    # a pure function of the drawing code, not of wall-clock time.
    fig.savefig(pdf_path, metadata={"CreationDate": None, "ModDate": None})
    fig.savefig(png_path, dpi=dpi)
    plt.close(fig)
    return pdf_path, png_path


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()
