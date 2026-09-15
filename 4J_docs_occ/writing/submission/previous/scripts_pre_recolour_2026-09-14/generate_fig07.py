# -*- coding: utf-8 -*-
# Recoloured 2026-09-14 to clear FINDING 279: every prompt in Prompts_Images/ bars
# green and red, and the first build used green for Italy and red for the reference
# line and for one negative label. House palette, colour-blind safe, greyscale safe:
#   Spain   #E69F00 orange   Britain #0072B2 blue   Italy #7B3294 purple
#   reference and threshold lines #000000   all value labels #111111
# No plotted value was changed by this edit.
import matplotlib.pyplot as plt
import numpy as np
import textwrap
import os

plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 0.8

fig = plt.figure(figsize=(12, 8.5), dpi=300)
gs = fig.add_gridspec(2, 2, height_ratios=[1.15, 1.0], hspace=0.38, wspace=0.25,
                      left=0.08, right=0.95, top=0.91, bottom=0.17)

ax_a = fig.add_subplot(gs[0, :])
ax_b1 = fig.add_subplot(gs[1, 0])
ax_b2 = fig.add_subplot(gs[1, 1])

# ----------------------------------------------------
# Panel A: Peak effect vs Between-diary spread
# ----------------------------------------------------
countries = ["Spain", "Britain", "Italy"]
peak_effects = [2.7145, 0.0393, -0.6332]
spreads = [4.9837, 2.3797, 1.5959]
ratios = [0.54, 0.02, 0.40]

x = np.arange(len(countries))
width = 0.28

c_effect = '#3E6B99'     # Slate blue
c_spread = '#D19C65'     # Muted ochre / sand
hatch_spread = '///'

# Peak effect bars
b1 = ax_a.bar(x - width/2, peak_effects, width, label='Peak effect', color=c_effect, edgecolor='#23405E', lw=0.8, zorder=3)
# Spread bars
b2 = ax_a.bar(x + width/2, spreads, width, label='Between-diary spread', color=c_spread, edgecolor='#63421C', hatch=hatch_spread, lw=0.8, zorder=3)

# Zero line
ax_a.axhline(0, color='#333333', linewidth=1.0, zorder=4)

# Value annotations
for i in range(len(countries)):
    pe = peak_effects[i]
    sp = spreads[i]
    rat = ratios[i]
    
    # Peak effect text
    if pe >= 0:
        ax_a.text(x[i] - width/2, pe + 0.15, f"{pe:+.2f} %" if abs(pe) > 0.1 else f"{pe:+.4f} %",
                  ha='center', va='bottom', fontsize=8, fontweight='bold', color='#111111')
    else:
        ax_a.text(x[i] - width/2, pe - 0.20, f"{pe:+.4f} %",
                  ha='center', va='top', fontsize=8, fontweight='bold', color='#111111')
        
    # Spread text
    ax_a.text(x[i] + width/2, sp + 0.15, f"{sp:.2f}",
              ha='center', va='bottom', fontsize=8, fontweight='bold', color='#111111')
    
    # Ratio text above the pair
    max_y = max(pe, sp)
    ax_a.text(x[i], max_y + 0.55, f"ratio: {rat:.2f}",
              ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#333333',
              bbox=dict(boxstyle='round,pad=0.25', facecolor='#F7FAFC', edgecolor='#CBD5E0', lw=0.7))

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

# Panel A text note beneath
ax_a.text(0.5, -0.16, "The effect is smaller than the spread between individual diaries in every fold, and its sign is not stable.",
          transform=ax_a.transAxes, ha='center', va='top', fontsize=9, fontweight='bold', color='#111111')

# ----------------------------------------------------
# Panel B1: Annual median effect
# ----------------------------------------------------
annual_medians = [-1.5100, -0.3605, -0.4178]
b_b1 = ax_b1.bar(x, annual_medians, width=0.45, color='#718096', edgecolor='#2D3748', lw=0.8, zorder=3)
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

# Line beneath B1
ax_b1.text(0.5, -0.22, "Every annual median is negative at every sensitivity level in every fold,\nso the sign was a statement about the clock rather than occupancy.",
           transform=ax_b1.transAxes, ha='center', va='top', fontsize=7.5, style='italic', color='#333333')

# ----------------------------------------------------
# Panel B2: Surviving ordering (Apartment buildings)
# ----------------------------------------------------
apt_effects = [3.46, 1.04, 0.50]
b_b2 = ax_b2.bar(x, apt_effects, width=0.45, color='#3E6B99', edgecolor='#23405E', lw=0.8, zorder=3)
ax_b2.axhline(0, color='#333333', linewidth=1.0, zorder=4)

for i, val in enumerate(apt_effects):
    ax_b2.text(x[i], val + 0.15, f"+{val:.2f} %", ha='center', va='bottom', fontsize=8, fontweight='bold', color='#111111')

ax_b2.set_xticks(x)
ax_b2.set_xticklabels(countries, fontsize=9.5, fontweight='bold')
ax_b2.set_ylabel("Peak heating effect (%)", fontsize=9, labelpad=6)
ax_b2.set_ylim(-0.5, 4.3)
ax_b2.set_title("Panel B2: The surviving ordering (apartment buildings)", fontsize=10, fontweight='bold', pad=8)
ax_b2.grid(axis='y', linestyle=':', alpha=0.5, color='#CCCCCC')
ax_b2.set_axisbelow(True)
ax_b2.spines['top'].set_visible(False)
ax_b2.spines['right'].set_visible(False)

# Line beneath B2
ax_b2.text(0.5, -0.22, "The effect is monotone in dwelling class in all three folds and ordering\nsurvives the correction. This is a claim about geometry, not behaviour.",
           transform=ax_b2.transAxes, ha='center', va='top', fontsize=7.5, style='italic', color='#333333')

# Figure Title
fig.suptitle("Figure 7: Occupancy into Heating is a Null, and What Survives Instead",
             fontsize=11.5, fontweight='bold', y=0.97)

# Two notes at the bottom of the figure
note_a = textwrap.fill("(a) A four-hour phase error invalidated the first campaign and correcting it changed the sign of the headline. These are the corrected values.", 150)
note_b = textwrap.fill("(b) Every claim this design supports is a peak and timing claim. In the observed-stock campaign, going from no occupancy signal to full occupancy signal moves annual heating by under half a per cent while moving the hourly peak by up to 7.92 per cent and the peak hour by up to 41 hours.", 150)

notes_text = f"{note_a}\n{note_b}"
plt.figtext(0.08, 0.015, notes_text, ha='left', va='bottom', fontsize=7.2, style='italic', color='#444444',
            linespacing=1.3, bbox=dict(boxstyle='square,pad=0.4', facecolor='#FDFDFD', edgecolor='#E0E0E0', lw=0.7))

prompts_dir = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\4J_docs_occ\writing\submission\figures\Prompts_Images"
figures_dir = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\4J_docs_occ\writing\submission\figures"

out1 = os.path.join(prompts_dir, "Figure_07_heating_null.png")
out1_alias = os.path.join(prompts_dir, "4thJ_figure07_heating_null.png")
out2 = os.path.join(figures_dir, "Figure_07_heating_null.png")

plt.savefig(out1, dpi=300)
plt.savefig(out1_alias, dpi=300)
plt.savefig(out2, dpi=300)
print(f"Generated Figure 7: {out1} ({os.path.getsize(out1)} bytes)")
