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

fig, ax = plt.subplots(figsize=(12, 7.2), dpi=300)

hours = list(range(24))

spain = [
    161.0065, 167.1608, 152.1853, 183.7966, 88.2520, 86.4613, 90.2884, 231.1866, 322.3911, 288.9154,
    209.8567, 261.4761, 283.1428, 329.5136, 502.8777, 288.2443, 237.4997, 276.7177, 278.3329, 436.4504,
    359.7059, 375.2607, 321.2966, 216.3090
]

italy = [
    257.7229, 205.4651, 168.9858, 192.3412, 87.1615, 86.4866, 95.4819, 246.0244, 240.4165, 226.5512,
    197.5258, 154.0847, 275.6615, 235.6975, 253.3758, 280.1487, 232.5131, 235.8322, 403.5225, 322.3697,
    330.7499, 307.4528, 332.0188, 290.9912
]

britain = [
    163.9499, 120.1332, 104.7535, 137.8746, 86.2880, 92.6489, 92.8075, 215.0523, 215.0066, 269.7648,
    297.1429, 198.7250, 255.4478, 348.0092, 327.7575, 333.2554, 287.5917, 268.0605, 243.6590, 310.9027,
    416.1349, 347.0145, 324.7435, 254.8932
]

# Highlight the 6-hour span between 14:00 and 20:00
ax.axvspan(14, 20, color='#F0F4F8', alpha=0.85, zorder=1)
ax.axvline(14, color='#7090B0', linestyle=':', linewidth=1.2, zorder=2)
ax.axvline(20, color='#7090B0', linestyle=':', linewidth=1.2, zorder=2)

# Plot lines
ax.plot(hours, spain, label='Spain', color='#E69F00', linestyle='-', linewidth=2.0, marker='o', markersize=4.5, zorder=4)
ax.plot(hours, italy, label='Italy', color='#7B3294', linestyle='-.', linewidth=2.0, marker='^', markersize=4.5, zorder=4)
ax.plot(hours, britain, label='Britain', color='#0072B2', linestyle='--', linewidth=2.0, marker='s', markersize=4.5, zorder=4)

# 6-hour span callout bracket/text
ax.annotate('', xy=(14, 535), xytext=(20, 535),
            arrowprops=dict(arrowstyle='<->', color='#2B4263', lw=1.3), zorder=6)
ax.text(17, 545, "six hours", ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#1B365D')

# Peak annotations
# Spain peak at 14:00 (502.88)
ax.scatter([14], [spain[14]], color='#E69F00', s=70, edgecolor='#000000', lw=1.2, zorder=6)
ax.annotate('Spain 14:00, 503 W', xy=(14, spain[14]), xytext=(12.8, 508),
            arrowprops=dict(arrowstyle='->', color='#E69F00', lw=1.0),
            ha='right', va='bottom', fontsize=8.5, fontweight='bold', color='#8A5B00',
            bbox=dict(boxstyle='round,pad=0.25', facecolor='#FFF7ED', edgecolor='#FBD38D', lw=0.7))

# Italy peak at 18:00 (403.52)
ax.scatter([18], [italy[18]], color='#7B3294', s=70, edgecolor='#000000', lw=1.2, zorder=6)
ax.annotate('Italy 18:00, 404 W', xy=(18, italy[18]), xytext=(16.8, 435),
            arrowprops=dict(arrowstyle='->', color='#7B3294', lw=1.0),
            ha='right', va='bottom', fontsize=8.5, fontweight='bold', color='#4A1E5C',
            bbox=dict(boxstyle='round,pad=0.25', facecolor='#F7F2FA', edgecolor='#D6BCE0', lw=0.7))

# Britain peak at 20:00 (416.13)
ax.scatter([20], [britain[20]], color='#0072B2', s=70, edgecolor='#000000', lw=1.2, zorder=6)
ax.annotate('Britain 20:00, 416 W', xy=(20, britain[20]), xytext=(21.0, 445),
            arrowprops=dict(arrowstyle='->', color='#0072B2', lw=1.0),
            ha='left', va='bottom', fontsize=8.5, fontweight='bold', color='#1A365D',
            bbox=dict(boxstyle='round,pad=0.25', facecolor='#EBF8FF', edgecolor='#BEE3F8', lw=0.7))

ax.set_xlim(-0.5, 23.5)
ax.set_ylim(0, 580)
ax.set_xticks([0, 3, 6, 9, 12, 15, 18, 21, 23])
ax.set_xticklabels(['00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00', '23:00'], fontsize=9)
ax.set_xlabel("Hour of day", fontsize=9.5, labelpad=8)
ax.set_ylabel("Mean appliance electricity, watts per dwelling", fontsize=9.5, labelpad=8)
ax.tick_params(axis='both', labelsize=9)

ax.grid(True, linestyle=':', alpha=0.5, color='#CCCCCC')
ax.set_axisbelow(True)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

ax.legend(loc='upper left', frameon=True, facecolor='#FFFFFF', edgecolor='#CCCCCC', fontsize=9.5)

# Verdict line beneath chart
verdict_text = "One appliance model. One calibration. One trigger rule. Only the diary differs, and the peak moves six hours."
plt.figtext(0.5, 0.12, verdict_text, ha='center', va='bottom', fontsize=10, fontweight='bold', color='#111111')

# Two notes at bottom
note_a = textwrap.fill("(a) This is a shape and timing result. It is not an accuracy claim, and it is never reported for an individual dwelling.", 150)
note_b = textwrap.fill("(b) Scored against a published British reference load shape assembled around the year 2000, this same measurement is a failing check. A Spanish load shape built from Spanish diaries is supposed to disagree with a British reference, and the band was not moved.", 150)

notes_text = f"{note_a}\n{note_b}"
plt.figtext(0.08, 0.02, notes_text, ha='left', va='bottom', fontsize=7.2, style='italic', color='#444444',
            linespacing=1.3, bbox=dict(boxstyle='square,pad=0.4', facecolor='#FDFDFD', edgecolor='#E0E0E0', lw=0.7))

fig.suptitle("Figure 6: One Appliance Model, Three Diaries, Peaks Six Hours Apart",
             fontsize=11.5, fontweight='bold', y=0.96)

plt.subplots_adjust(left=0.10, right=0.96, top=0.88, bottom=0.25)

prompts_dir = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\4J_docs_occ\writing\submission\figures\Prompts_Images"
figures_dir = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\4J_docs_occ\writing\submission\figures"

out1 = os.path.join(prompts_dir, "Figure_06_appliance_peaks.png")
out1_alias = os.path.join(prompts_dir, "4thJ_figure06_appliance_peaks.png")
out2 = os.path.join(figures_dir, "Figure_06_appliance_peaks.png")

plt.savefig(out1, dpi=300)
plt.savefig(out1_alias, dpi=300)
plt.savefig(out2, dpi=300)
print(f"Generated Figure 6: {out1} ({os.path.getsize(out1)} bytes)")
