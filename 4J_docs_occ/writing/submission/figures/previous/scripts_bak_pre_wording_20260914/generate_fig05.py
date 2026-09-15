# -*- coding: utf-8 -*-
# Recoloured 2026-09-14 (second pass, author request).  House palette is now the
# Tol muted set: colour-blind safe and separable in greyscale by lightness as well
# as by line style / marker / hatch.
#   Spain  #CC6677 rose    Britain #332288 indigo   Italy #44AA99 teal
#   secondary series #DDCC77 sand   negative channel #882255 wine
#   reference and threshold lines #000000   all value labels #111111
# Explanatory notes and verdict lines were REMOVED from inside the image on the
# same request; that text now lives in the manuscript prose, not in the picture.
# No plotted value was changed by either edit.
import matplotlib.pyplot as plt
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

c_bar = '#332288'       # Slate steel blue
c_marker = '#1D1350'

for i, d in enumerate(data_rev):
    y = y_pos[i]
    low = d["mult_low"]
    high = d["mult_high"]
    
    # Range bar
    ax.barh(y, high - low, left=low, height=0.38, color=c_bar, edgecolor='#1D1350', lw=1.0, zorder=3)
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

fig.suptitle("Figure 5: Joint Structure: Every Band Exceeded, Several Times Over",
             fontsize=11.5, fontweight='bold', y=0.96)

plt.subplots_adjust(left=0.28, right=0.96, top=0.87, bottom=0.15)

prompts_dir = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\4J_docs_occ\writing\submission\figures\Prompts_Images"
figures_dir = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\4J_docs_occ\writing\submission\figures"

out1 = os.path.join(prompts_dir, "Figure_05_joint_structure.png")
out1_alias = os.path.join(prompts_dir, "4thJ_figure05_joint_structure.png")
out2 = os.path.join(figures_dir, "Figure_05_joint_structure.png")

plt.savefig(out1, dpi=300)
plt.savefig(out1_alias, dpi=300)
plt.savefig(out2, dpi=300)
print(f"Generated Figure 5: {out1} ({os.path.getsize(out1)} bytes)")
