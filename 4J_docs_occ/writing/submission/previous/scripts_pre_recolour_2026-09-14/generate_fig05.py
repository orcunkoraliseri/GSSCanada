# -*- coding: utf-8 -*-
# Recoloured 2026-09-14 to clear FINDING 279: every prompt in Prompts_Images/ bars
# green and red, and the first build drew the registered band line in dark red.
# House palette, colour-blind safe, greyscale safe:
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

fig, ax = plt.subplots(figsize=(12, 7.0), dpi=300)

data = [
    {
        "name": "Dwell-time Wasserstein distance",
        "mult_low": 5.0,
        "mult_high": 6.7,
        "detail": "band 10.0 min, measured 50.13 to 66.57"
    },
    {
        "name": "Transition-matrix total variation",
        "mult_low": 3.3,
        "mult_high": 4.7,
        "detail": "band 0.050, measured 0.1623 to 0.2344"
    },
    {
        "name": "Diurnal Jensen-Shannon divergence",
        "mult_low": 4.6,
        "mult_high": 7.9,
        "detail": "band 0.015, measured 0.0690 to 0.1189"
    },
    {
        "name": "Time-budget error",
        "mult_low": 4.8,
        "mult_high": 8.6,
        "detail": "band 8.0 min, measured 38.26 to 68.67"
    }
]

data_rev = list(reversed(data))
y_pos = list(range(len(data_rev)))

c_bar = '#3E6B99'       # Slate steel blue
c_marker = '#1B365D'

for i, d in enumerate(data_rev):
    y = y_pos[i]
    low = d["mult_low"]
    high = d["mult_high"]
    
    # Range bar
    ax.barh(y, high - low, left=low, height=0.38, color=c_bar, edgecolor='#1B365D', lw=1.0, zorder=3)
    ax.plot([low, high], [y, y], marker='o', markersize=6.5, color=c_marker, linestyle='none', zorder=4)
    
    # Range values inside bar
    ax.text((low + high)/2, y, f"{low} to {high} x", ha='center', va='center',
            color='#FFFFFF', fontweight='bold', fontsize=9, zorder=5)
    
    # Real units text at right
    ax.text(high + 0.35, y, d["detail"], ha='left', va='center', fontsize=8.5, color='#333333', style='italic')

# Vertical reference line at 1.0
ax.axvline(1.0, color='#000000', linestyle='-', linewidth=2.0, zorder=2)
ax.text(1.0, 3.55, "the registered band (1.0)", color='#000000', fontsize=8.5, fontweight='bold',
         ha='center', va='bottom')

ax.set_yticks(y_pos)
ax.set_yticklabels([d["name"] for d in data_rev], fontsize=9.5, fontweight='bold')
ax.set_xlim(0, 13.5)
ax.set_ylim(-0.6, 3.8)

ax.set_xlabel("Measured value as a multiple of the band registered before training\n(1.0 is the band. Anything to the right of it fails.)",
              fontsize=9.5, labelpad=8)
ax.tick_params(axis='x', labelsize=9)

ax.grid(axis='x', linestyle=':', alpha=0.5, color='#BBBBBB')
ax.set_axisbelow(True)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Verdict line beneath chart
verdict_text = "None of these quantities was in the prompt. All four fail, on every fold, at three to nine times their band."
plt.figtext(0.5, 0.12, verdict_text, ha='center', va='bottom', fontsize=10, fontweight='bold', color='#111111')

# Notes at bottom
note_a = textwrap.fill("(a) The model was conditioned on a time budget. Dwell times, transition structure and diurnal shape were never supplied to it and were never optimised for. They are what the joint distribution looks like when only its margins are specified.", 150)
note_b = textwrap.fill("(b) Verdicts are identical under the calendar-re-based weights and unweighted, so the failure is not an artefact of the weighting correction.", 150)

notes_text = f"{note_a}\n{note_b}"
plt.figtext(0.08, 0.02, notes_text, ha='left', va='bottom', fontsize=7.2, style='italic', color='#444444',
            linespacing=1.3, bbox=dict(boxstyle='square,pad=0.4', facecolor='#FDFDFD', edgecolor='#E0E0E0', lw=0.7))

fig.suptitle("Figure 5: Joint Structure: Every Band Exceeded, Several Times Over",
             fontsize=11.5, fontweight='bold', y=0.96)

plt.subplots_adjust(left=0.28, right=0.96, top=0.88, bottom=0.26)

prompts_dir = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\4J_docs_occ\writing\submission\figures\Prompts_Images"
figures_dir = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\4J_docs_occ\writing\submission\figures"

out1 = os.path.join(prompts_dir, "Figure_05_joint_structure.png")
out1_alias = os.path.join(prompts_dir, "4thJ_figure05_joint_structure.png")
out2 = os.path.join(figures_dir, "Figure_05_joint_structure.png")

plt.savefig(out1, dpi=300)
plt.savefig(out1_alias, dpi=300)
plt.savefig(out2, dpi=300)
print(f"Generated Figure 5: {out1} ({os.path.getsize(out1)} bytes)")
