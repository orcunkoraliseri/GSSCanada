# -*- coding: utf-8 -*-
# Recoloured 2026-09-14 to clear FINDING 279: every prompt in Prompts_Images/ bars
# green and red, and the first build used green for Italy and red for the reference
# line and for one negative label. House palette, colour-blind safe, greyscale safe:
#   Spain   #E69F00 orange   Britain #0072B2 blue   Italy #7B3294 purple
#   reference and threshold lines #000000   all value labels #111111
# No plotted value was changed by this edit.
import matplotlib.pyplot as plt
import textwrap
import os

plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 0.8

fig = plt.figure(figsize=(12, 7.2), dpi=300)
gs = fig.add_gridspec(1, 2, width_ratios=[2.2, 1.0], wspace=0.28, left=0.08, right=0.96, top=0.88, bottom=0.25)

ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])

# Data for left panel
levels = [0, 1, 2, 3, 4]
folds_data = [
    {
        "name": "Spain held out",
        "y": [60.71, 59.15, 49.04, 34.19, 16.64],
        "slope": 0.4153,
        "color": "#E69F00",
        "marker": "o",
        "linestyle": "-"
    },
    {
        "name": "Britain held out",
        "y": [35.76, 34.06, 24.38, 18.77, 15.39],
        "slope": 0.5329,
        "color": "#0072B2",
        "marker": "s",
        "linestyle": "--"
    },
    {
        "name": "Italy held out",
        "y": [36.49, 28.55, 15.89, 12.42, 19.02],
        "slope": 0.4049,
        "color": "#7B3294",
        "marker": "^",
        "linestyle": "-."
    }
]

# Plot left panel
for d in folds_data:
    ax1.plot(levels, d["y"], label=d["name"], color=d["color"], marker=d["marker"],
             linestyle=d["linestyle"], linewidth=1.8, markersize=6.5)
    last_y = d["y"][-1]
    if d["name"] == "Spain held out":
        y_offset = -0.5
    elif d["name"] == "Britain held out":
        y_offset = -2.2
    else: # Italy
        y_offset = 1.8
    ax1.text(4.08, last_y + y_offset, f"slope {d['slope']:.4f}", color=d["color"],
             fontsize=8.5, fontweight='bold', va='center')

ax1.set_xlim(-0.2, 4.8)
ax1.set_ylim(8, 66)
ax1.set_xticks(levels)
ax1.set_xlabel("Conditioning level pushed along the tilt\n(falling is responding)", fontsize=9.5, labelpad=6)
ax1.set_ylabel("Distance to the fictional conditioning vector", fontsize=9.5, labelpad=6)
ax1.set_title("Response curves across five tilt levels", fontsize=10, fontweight='bold', pad=10)
ax1.grid(True, linestyle=':', alpha=0.5, color='#BBBBBB')
ax1.set_axisbelow(True)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.legend(loc='upper right', frameon=True, facecolor='#FFFFFF', edgecolor='#CCCCCC', fontsize=9)

# Right panel
bar_y = [2, 1, 0]
slopes = [d["slope"] for d in folds_data]
names = [d["name"] for d in folds_data]
colors = [d["color"] for d in folds_data]

bars = ax2.barh(bar_y, slopes, height=0.45, color=colors, edgecolor='#333333', lw=0.8)
for i, val in enumerate(slopes):
    ax2.text(val + 0.02, bar_y[i], f"{val:.4f}", va='center', ha='left', fontsize=8.5, fontweight='bold')

# Vertical reference line at 0.80
ax2.axvline(0.80, color='#000000', linestyle='-', linewidth=2.0, zorder=5)
ax2.text(0.80, 2.55, "registered floor 0.80", color='#000000', fontsize=8.5, fontweight='bold',
         ha='center', va='bottom')

ax2.set_yticks(bar_y)
ax2.set_yticklabels(names, fontsize=9)
ax2.set_xlim(0, 1.0)
ax2.set_ylim(-0.5, 2.7)
ax2.set_xlabel("Fitted slope", fontsize=9.5, labelpad=6)
ax2.set_title("Slopes vs registered floor", fontsize=10, fontweight='bold', pad=10)
ax2.grid(axis='x', linestyle=':', alpha=0.5, color='#BBBBBB')
ax2.set_axisbelow(True)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

# Text beneath right panel
ax2.text(0.5, -0.28, "Fails 3 of 3. The response is real\nand roughly half the required strength.",
         transform=ax2.transAxes, ha='center', va='top', fontsize=8, fontweight='bold', color='#111111')

fig.suptitle("Figure 4: The Fictional-Country Control: Direction Versus Amplitude",
             fontsize=11.5, fontweight='bold', y=0.96)

# Three notes at the bottom, nicely wrapped
note_a = textwrap.fill("(a) Direction was measured only on the smaller pilot model, where it passes at R-squared 0.8455, 0.9808 and 0.9836 against the same floor of 0.80. It was never recomputed on the model reported here and is inherited, not measured.", 145)
note_b = textwrap.fill("(b) These slopes are computed over six conditioning channels. The registered definition of this check counts five, with one excluded by name, and was never applied to the reported model.", 145)
note_c = textwrap.fill("(c) A low slope means under-response, not indifference. An indifferent model would give a flat line.", 145)

notes_text = f"{note_a}\n{note_b}\n{note_c}"
plt.figtext(0.08, 0.02, notes_text, ha='left', va='bottom', fontsize=7.2, style='italic', color='#444444',
            linespacing=1.3, bbox=dict(boxstyle='square,pad=0.4', facecolor='#FDFDFD', edgecolor='#E0E0E0', lw=0.7))

prompts_dir = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\4J_docs_occ\writing\submission\figures\Prompts_Images"
figures_dir = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\4J_docs_occ\writing\submission\figures"

out1 = os.path.join(prompts_dir, "Figure_04_amplitude_slope.png")
out1_alias = os.path.join(prompts_dir, "4thJ_figure04_amplitude_slope.png")
out2 = os.path.join(figures_dir, "Figure_04_amplitude_slope.png")

plt.savefig(out1, dpi=300)
plt.savefig(out1_alias, dpi=300)
plt.savefig(out2, dpi=300)
print(f"Generated Figure 4: {out1} ({os.path.getsize(out1)} bytes)")
