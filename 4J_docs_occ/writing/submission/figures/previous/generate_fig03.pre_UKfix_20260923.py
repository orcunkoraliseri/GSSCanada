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

fig, ax = plt.subplots(figsize=(12, 7.2), dpi=300)

data = [
    ("Spain held out", "Y25-44", 36.81, 9.94, False),
    ("Spain held out", "Y45-64", 34.52, 8.82, False),
    ("Spain held out", "Y_GE65", 44.32, 11.81, False),
    ("Britain held out", "Y25-44", 58.91, 21.79, False),
    ("Britain held out", "Y45-64", 60.44, 19.21, False),
    ("Britain held out", "Y_GE65", 21.24, 18.54, True),
    ("Italy held out", "Y25-44", 62.24, 19.51, False),
    ("Italy held out", "Y45-64", 33.95, 13.85, False),
    ("Italy held out", "Y_GE65", 35.84, 15.51, False),
]

data_rev = list(reversed(data))

y_positions = []
cur_y = 0.0
for i, item in enumerate(data_rev):
    y_positions.append(cur_y)
    if i < len(data_rev) - 1:
        cur_fold = item[0]
        next_fold = data_rev[i+1][0]
        if cur_fold != next_fold:
            cur_y += 1.9
        else:
            cur_y += 1.2

bar_height = 0.42

c_model = '#332288'      # Slate steel blue
c_null = '#DDCC77'       # Muted ochre
hatch_null = '///'

for i, (fold, band, model_val, null_val, is_closest) in enumerate(data_rev):
    y = y_positions[i]
    
    # Upper bar: Model
    ax.barh(y + bar_height/2, model_val, height=bar_height, color=c_model, edgecolor='#1D1350',
            label='Fine-tuned language model' if i == len(data_rev)-1 else "")
    # Lower bar: Null
    ax.barh(y - bar_height/2, null_val, height=bar_height, color=c_null, edgecolor='#9B8E4F', hatch=hatch_null,
            label='Raked donor null' if i == len(data_rev)-1 else "")
    
    # Value labels
    ax.text(model_val + 0.8, y + bar_height/2, f"{model_val:.2f}", va='center', ha='left', fontsize=8.5, color='#111111')
    ax.text(null_val + 0.8, y - bar_height/2, f"{null_val:.2f}", va='center', ha='left', fontsize=8.5, color='#111111')
    
    # Closest miss callout
    if is_closest:
        ax.annotate('closest miss, 2.70 min/day',
                    xy=(model_val + 3.8, y + bar_height/2),
                    xytext=(model_val + 16.5, y),
                    arrowprops=dict(arrowstyle='->', color='#222222', lw=1.0),
                    va='center', ha='left', fontsize=8.5, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.35', facecolor='#FFFFFF', edgecolor='#888888', lw=0.8))

# Y-axis band labels
ax.set_yticks(y_positions)
ax.set_yticklabels([d[1] for d in data_rev], fontsize=9)

# Fold block labels on the left
fold_groups = {}
for i, d in enumerate(data_rev):
    fold = d[0]
    if fold not in fold_groups:
        fold_groups[fold] = []
    fold_groups[fold].append(y_positions[i])

for fold, ys in fold_groups.items():
    mid_y = sum(ys) / len(ys)
    ax.text(-8.0, mid_y, fold, va='center', ha='right', fontsize=9.5, fontweight='bold', color='#111111')

ax.set_xlim(0, 80)
ax.set_xlabel("Time-budget mean absolute error, minutes per day\n(lower is better)", fontsize=9.5, labelpad=8)
ax.tick_params(axis='x', labelsize=9)

ax.grid(axis='x', linestyle=':', alpha=0.5, color='#BBBBBB')
ax.set_axisbelow(True)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Legend at top right
leg = ax.legend(loc='upper right', bbox_to_anchor=(0.99, 0.99), frameon=True, facecolor='#FFFFFF', edgecolor='#CCCCCC', fontsize=9)
leg.get_frame().set_linewidth(0.8)

fig.suptitle("Figure 3: Time-Budget Mean Absolute Error Across Nine Cells", fontsize=11.5, fontweight='bold', y=0.97)

plt.subplots_adjust(left=0.22, right=0.96, top=0.91, bottom=0.10)

prompts_dir = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\4J_docs_occ\writing\submission\figures\Prompts_Images"
figures_dir = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\4J_docs_occ\writing\submission\figures"

out1 = os.path.join(prompts_dir, "Figure_03_nine_cells.png")
out1_alias = os.path.join(prompts_dir, "4thJ_figure03_nine_cells.png")
out2 = os.path.join(figures_dir, "Figure_03_nine_cells.png")

plt.savefig(out1, dpi=300)
plt.savefig(out1_alias, dpi=300)
plt.savefig(out2, dpi=300)
print(f"Generated Figure 3: {out1} ({os.path.getsize(out1)} bytes)")
