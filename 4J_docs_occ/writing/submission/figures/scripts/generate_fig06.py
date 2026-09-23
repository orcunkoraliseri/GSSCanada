# -*- coding: utf-8 -*-
"""Figure 6 - stock-mean hourly electricity per dwelling, three countries, three
diary sources.

REBUILT 2026-09-23 (P3 branch 2, "the claim narrows"). The prior version plotted
only the generated diaries and drew a withdrawn "six-hour spread" callout
between 14:00 and 20:00. P3 (`writing/submission/IMP/impl/P3_appliance_real_and_donor.md`,
result table 2026-09-23) ran the same appliance model against three diary
sources per held-out country -- generated, real (unweighted), raked donor --
and found the generated diaries do NOT carry the real peak-hour order. This
figure now shows all three sources, one small panel per country, so the reader
sees that directly instead of reading a withdrawn claim.

Every hourly value below is read straight from
`Step9_docs/outputs_step9_P3/<source>/<country>/stock_series_<country>.csv`
(mean electricity_w per hour of day, divided by 100 dwellings). No value is
altered. Re-verify with the same computation before trusting any change here:
the nine peaks must reproduce the P3 result table exactly
(Spain gen 14:00 502.9 / real 21:00 421.5 / donor 19:00 408.5;
 Italy gen 18:00 403.5 / real 19:00 444.4 / donor 21:00 396.5;
 UK    gen 20:00 416.1 / real 18:00 427.2 / donor 21:00 425.9).

House palette (Tol muted set, colour-blind safe), now assigned by SOURCE
(the panels already separate by country): generated #332288 indigo (solid,
circle), real diaries #CC6677 rose (dashed, square), raked donor diaries
#44AA99 teal (dash-dot, triangle). No annotation text is drawn in the image
(no "six hours", no spread arrow, no ranking) -- only a marked dot at each
line's peak hour. The journal caption carries the figure number and title.
"""
import csv
import os

import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42

HERE = os.path.dirname(os.path.abspath(__file__))
P3_ROOT = os.path.join(HERE, "..", "..", "..", "..", "Step9_docs", "outputs_step9_P3")


def hourly_mean_per_dwelling(path, n_dwellings=100):
    """Mean electricity_w at each hour of day, averaged over the year, per dwelling."""
    sums = [0.0] * 24
    counts = [0] * 24
    with open(path, newline='') as f:
        r = csv.DictReader(f)
        for row in r:
            h = int(row['timestep']) % 24
            sums[h] += float(row['electricity_w'])
            counts[h] += 1
    return [sums[h] / counts[h] / n_dwellings for h in range(24)]


COUNTRIES = [("es", "Spain"), ("it", "Italy"), ("uk", "UK")]
SOURCES = [
    ("generated", "Generated diaries", "#332288", "-", "o"),
    ("real", "Real diaries (unweighted)", "#CC6677", "--", "s"),
    ("raked", "Raked donor diaries", "#44AA99", "-.", "^"),
]

data = {}
for code, _ in COUNTRIES:
    data[code] = {}
    for source, _, _, _, _ in SOURCES:
        path = os.path.join(P3_ROOT, source, code, "stock_series_%s.csv" % code)
        data[code][source] = hourly_mean_per_dwelling(path)

# Reproduction check against the P3 result table (2026-09-23). If any of these
# nine values drifts, STOP -- do not trust the plotted figure.
EXPECTED_PEAKS = {
    ("es", "generated"): (14, 502.9), ("es", "real"): (21, 421.5), ("es", "raked"): (19, 408.5),
    ("it", "generated"): (18, 403.5), ("it", "real"): (19, 444.4), ("it", "raked"): (21, 396.5),
    ("uk", "generated"): (20, 416.1), ("uk", "real"): (18, 427.2), ("uk", "raked"): (21, 425.9),
}
_mismatch = []
for code, _ in COUNTRIES:
    for source, _, _, _, _ in SOURCES:
        series = data[code][source]
        peak_h = max(range(24), key=lambda h: series[h])
        peak_w = series[peak_h]
        exp_h, exp_w = EXPECTED_PEAKS[(code, source)]
        if peak_h != exp_h or abs(peak_w - exp_w) > 0.1:
            _mismatch.append("%s/%s: got %02d:00 %.1f W, expected %02d:00 %.1f W"
                              % (code, source, peak_h, peak_w, exp_h, exp_w))
if _mismatch:
    raise SystemExit("Figure 6 reproduction check FAILED:\n" + "\n".join(_mismatch))
print("Figure 6 reproduction check: all nine peaks match the P3 result table.")

hours = list(range(24))

fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.6), dpi=300, sharey=True)

for ax, (code, name) in zip(axes, COUNTRIES):
    for source, label, color, ls, marker in SOURCES:
        series = data[code][source]
        ax.plot(hours, series, color=color, linestyle=ls, marker=marker,
                 markersize=3.8, linewidth=1.6, label=label, zorder=3)
        peak_h = max(range(24), key=lambda h: series[h])
        ax.scatter([peak_h], [series[peak_h]], color=color, s=55,
                   edgecolor='#000000', linewidth=1.1, zorder=5)

    ax.set_title(name, fontsize=11, fontweight='bold', pad=8)
    ax.set_xlim(-0.5, 23.5)
    ax.set_xticks([0, 6, 12, 18, 23])
    ax.set_xticklabels(['00:00', '06:00', '12:00', '18:00', '23:00'], fontsize=8.5)
    ax.set_xlabel("Hour of day", fontsize=9.5, labelpad=6)
    ax.grid(True, linestyle=':', alpha=0.5, color='#CCCCCC')
    ax.set_axisbelow(True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

axes[0].set_ylabel("Mean electricity per dwelling (W)", fontsize=9.5, labelpad=8)
max_val = max(v for code, _ in COUNTRIES for source, _, _, _, _ in SOURCES for v in data[code][source])
axes[0].set_ylim(0, max_val * 1.08)

handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc='lower center', ncol=3, frameon=True,
           facecolor='#FFFFFF', edgecolor='#CCCCCC', fontsize=9.5,
           bbox_to_anchor=(0.5, -0.02))

plt.subplots_adjust(left=0.07, right=0.98, top=0.90, bottom=0.28, wspace=0.12)

prompts_dir = os.path.join(HERE, "..", "Prompts_Images")
figures_dir = os.path.join(HERE, "..")

out1 = os.path.join(prompts_dir, "Figure_06_appliance_peaks.png")
out1_pdf = os.path.join(prompts_dir, "Figure_06_appliance_peaks.pdf")
out1_alias = os.path.join(prompts_dir, "4thJ_figure06_appliance_peaks.png")
out1_alias_pdf = os.path.join(prompts_dir, "4thJ_figure06_appliance_peaks.pdf")
out2 = os.path.join(figures_dir, "Figure_06_appliance_peaks.png")
out2_pdf = os.path.join(figures_dir, "Figure_06_appliance_peaks.pdf")

plt.savefig(out1, dpi=1000)
plt.savefig(out1_pdf)
plt.savefig(out1_alias, dpi=1000)
plt.savefig(out1_alias_pdf)
plt.savefig(out2, dpi=1000)
plt.savefig(out2_pdf)
print(f"Generated Figure 6: {out2} ({os.path.getsize(out2)} bytes)")
print(f"Generated Figure 6 PDF: {out2_pdf} ({os.path.getsize(out2_pdf)} bytes)")
