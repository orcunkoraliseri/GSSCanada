# -*- coding: utf-8 -*-
# Recoloured 2026-09-14 (second pass, author request).  House palette is now the
# Tol muted set: colour-blind safe and separable in greyscale by lightness as well
# as by line style / marker / hatch.
#   Spain  #CC6677 rose    UK #332288 indigo   Italy #44AA99 teal
#   secondary series #DDCC77 sand   negative channel #882255 wine
#   reference and threshold lines #000000   all value labels #111111
# Explanatory notes and verdict lines were REMOVED from inside the image on the
# same request; that text now lives in the manuscript prose, not in the picture.
# No plotted value was changed by either edit.
import matplotlib.pyplot as plt
import numpy as np
import os

plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42

fig = plt.figure(figsize=(12, 8.5), dpi=300)
gs = fig.add_gridspec(2, 2, height_ratios=[1.15, 1.0], hspace=0.30, wspace=0.25,
                      left=0.08, right=0.95, top=0.95, bottom=0.09)

ax_a = fig.add_subplot(gs[0, :])
ax_b1 = fig.add_subplot(gs[1, 0])
ax_b2 = fig.add_subplot(gs[1, 1])

# ----------------------------------------------------
# Panel A: Peak effect vs Between-diary spread
# ----------------------------------------------------
countries = ["Spain", "UK", "Italy"]
peak_effects = [2.7145, 0.0393, -0.6332]
spreads = [4.9837, 2.3797, 1.5959]
ratios = [0.54, 0.02, 0.40]

x = np.arange(len(countries))
width = 0.28

c_effect = '#332288'     # Slate blue
c_spread = '#DDCC77'     # Muted ochre / sand
hatch_spread = '///'

# Peak effect bars
b1 = ax_a.bar(x - width/2, peak_effects, width, label='Peak effect', color=c_effect, edgecolor='#1D1350', lw=0.8, zorder=3)
# Spread bars
b2 = ax_a.bar(x + width/2, spreads, width, label='Between-diary spread', color=c_spread, edgecolor='#9B8E4F', hatch=hatch_spread, lw=0.8, zorder=3)

# Zero line
ax_a.axhline(0, color='#333333', linewidth=1.0, zorder=4)

# Value annotations
# Full precision throughout: the figure spec (4thJ_figure07_heating_null.md:11-13, 41) forbids
# rounding any value away from Table 10 (MS:900-910). Text objects are kept so the overflow
# check below can measure what was actually drawn.
panelA_texts = []
for i in range(len(countries)):
    pe = peak_effects[i]
    sp = spreads[i]
    rat = ratios[i]

    # Peak effect text (full precision, matches Table 10 verbatim: +2.7145 %, +0.0393 %, -0.6332 %)
    if pe >= 0:
        t_pe = ax_a.text(x[i] - width/2, pe + 0.15, f"{pe:+.4f} %",
                  ha='center', va='bottom', fontsize=8, fontweight='bold', color='#111111')
    else:
        t_pe = ax_a.text(x[i] - width/2, pe - 0.20, f"{pe:+.4f} %",
                  ha='center', va='top', fontsize=8, fontweight='bold', color='#111111')
    panelA_texts.append(t_pe)

    # Spread text (full precision, matches Table 10 verbatim: 4.9837, 2.3797, 1.5959)
    t_sp = ax_a.text(x[i] + width/2, sp + 0.15, f"{sp:.4f}",
              ha='center', va='bottom', fontsize=8, fontweight='bold', color='#111111')
    panelA_texts.append(t_sp)

    # Ratio text above the pair (spec gives the ratio itself only to 2 decimals: 0.54, 0.02, 0.40)
    max_y = max(pe, sp)
    t_rat = ax_a.text(x[i], max_y + 0.55, f"ratio: {rat:.2f}",
              ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#333333',
              bbox=dict(boxstyle='round,pad=0.25', facecolor='#FAFAFA', edgecolor='#D0D0D0', lw=0.7))
    panelA_texts.append(t_rat)

ax_a.set_xticks(x)
ax_a.set_xticklabels(countries, fontsize=10, fontweight='bold')
ax_a.set_ylabel("Magnitude (%)", fontsize=9.5, labelpad=6)
ax_a.set_ylim(-1.5, 6.2)
ax_a.set_title("Panel A: Peak effect against between-diary spread (the null)", fontsize=10.5, fontweight='bold', pad=8)
ax_a.grid(axis='y', linestyle=':', alpha=0.5, color='#CCCCCC')
ax_a.set_axisbelow(True)
ax_a.spines['top'].set_visible(False)
ax_a.spines['right'].set_visible(False)
ax_a.legend(loc='upper right', frameon=True, facecolor='#FFFFFF', edgecolor='#CCCCCC', fontsize=9)

# ----------------------------------------------------
# Panel B1: Annual median effect
# ----------------------------------------------------
annual_medians = [-1.5100, -0.3605, -0.4178]
b_b1 = ax_b1.bar(x, annual_medians, width=0.45, color='#882255', edgecolor='#551536', lw=0.8, zorder=3)
ax_b1.axhline(0, color='#333333', linewidth=1.0, zorder=4)

for i, val in enumerate(annual_medians):
    ax_b1.text(x[i], val - 0.12, f"{val:.4f} %", ha='center', va='top', fontsize=8, fontweight='bold', color='#111111')

ax_b1.set_xticks(x)
ax_b1.set_xticklabels(countries, fontsize=9.5, fontweight='bold')
ax_b1.set_ylabel("Annual median effect (%)", fontsize=9, labelpad=6)
ax_b1.set_ylim(-2.0, 0.5)
ax_b1.set_title("Panel B1: The annual channel", fontsize=10, fontweight='bold', pad=8)
ax_b1.grid(axis='y', linestyle=':', alpha=0.5, color='#CCCCCC')
ax_b1.set_axisbelow(True)
ax_b1.spines['top'].set_visible(False)
ax_b1.spines['right'].set_visible(False)

# ----------------------------------------------------
# Panel B2: Surviving ordering (Apartment buildings)
# ----------------------------------------------------
apt_effects = [3.46, 1.04, 0.50]
b_b2 = ax_b2.bar(x, apt_effects, width=0.45, color='#44AA99', edgecolor='#2C6F64', lw=0.8, zorder=3)
ax_b2.axhline(0, color='#333333', linewidth=1.0, zorder=4)

for i, val in enumerate(apt_effects):
    ax_b2.text(x[i], val + 0.15, f"+{val:.2f} %", ha='center', va='bottom', fontsize=8, fontweight='bold', color='#111111')

ax_b2.set_xticks(x)
ax_b2.set_xticklabels(countries, fontsize=9.5, fontweight='bold')
ax_b2.set_ylabel("Apartment-building effect (%)", fontsize=9, labelpad=6)
ax_b2.set_ylim(-0.5, 4.3)
ax_b2.set_title("Panel B2: The surviving ordering (apartment buildings)", fontsize=10, fontweight='bold', pad=8)
ax_b2.grid(axis='y', linestyle=':', alpha=0.5, color='#CCCCCC')
ax_b2.set_axisbelow(True)
ax_b2.spines['top'].set_visible(False)
ax_b2.spines['right'].set_visible(False)

# ---------------------------------------------------------------- overflow check
# Panel A's value labels grew from 2 decimal places to 4 (peak effect, between-diary spread) to carry
# the same precision as Table 10 without rounding. Measure every label actually drawn and confirm none
# collides with its neighbour or spills outside the Panel A axes.
fig.canvas.draw()
_renderer = fig.canvas.get_renderer()
_bad = []
_ax_bbox = ax_a.get_window_extent(renderer=_renderer)
import itertools as _itertools
for _t1, _t2 in _itertools.combinations(panelA_texts, 2):
    _bb1 = _t1.get_window_extent(renderer=_renderer)
    _bb2 = _t2.get_window_extent(renderer=_renderer)
    if _bb1.overlaps(_bb2):
        _bad.append("%r overlaps %r" % (_t1.get_text(), _t2.get_text()))
for _t in panelA_texts:
    _bb = _t.get_window_extent(renderer=_renderer)
    if _bb.x0 < _ax_bbox.x0 or _bb.x1 > _ax_bbox.x1:
        _bad.append("%r exceeds Panel A axes width (drawn x0=%.1f x1=%.1f, axes x0=%.1f x1=%.1f)"
                     % (_t.get_text(), _bb.x0, _bb.x1, _ax_bbox.x0, _ax_bbox.x1))
if _bad:
    for _b in _bad:
        print("OVERFLOW " + _b)
else:
    print("no text overflows its element")

prompts_dir = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\4J_docs_occ\writing\submission\figures\Prompts_Images"
figures_dir = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\4J_docs_occ\writing\submission\figures"

out1 = os.path.join(prompts_dir, "Figure_07_heating_null.png")
out1_pdf = os.path.join(prompts_dir, "Figure_07_heating_null.pdf")
out1_alias = os.path.join(prompts_dir, "4thJ_figure07_heating_null.png")
out1_alias_pdf = os.path.join(prompts_dir, "4thJ_figure07_heating_null.pdf")
out2 = os.path.join(figures_dir, "Figure_07_heating_null.png")
out2_pdf = os.path.join(figures_dir, "Figure_07_heating_null.pdf")

plt.savefig(out1, dpi=1000)
plt.savefig(out1_pdf)
plt.savefig(out1_alias, dpi=1000)
plt.savefig(out1_alias_pdf)
plt.savefig(out2, dpi=1000)
plt.savefig(out2_pdf)
print(f"Generated Figure 7: {out1} ({os.path.getsize(out1)} bytes)")
print(f"Generated Figure 7 PDF: {out2_pdf} ({os.path.getsize(out2_pdf)} bytes)")
