"""step9_diag.py — Step-9 load-shape investigation diagnostic.

Decomposes the population-mean equipment diurnal (2022 SingleD) by appliance
bucket, attributes the peak hour by activity code, and breaks down sleep-hour
load to explain the G3 WARN (28/48 cells sleep_equip_mean_wh > 300 Wh).

Python 3.13, py launcher, stdlib csv + numpy + matplotlib ONLY.
Run from repo root:
    py 2J_docs_occ_nTemp/Step9_docs/investigation/step9_diag.py

Produces:
    figI1_bucket_decomp.png   — stacked area: bucket contributions 0-23h
    figI2_peak_attribution.png — activity-code person-counts at peak hour
    figI3_sleep_breakdown.png  — bucket breakdown h00-h05 sleep window

Sources cited in print output as file:line or csv:row.
"""
import sys, os, csv, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ── path setup ────────────────────────────────────────────────────────────────
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))          # …/investigation
STEP9_DOCS  = os.path.dirname(SCRIPT_DIR)                         # …/Step9_docs
DOCS_2J     = os.path.dirname(STEP9_DOCS)                         # …/2J_docs_occ_nTemp
REPO_ROOT   = os.path.dirname(DOCS_2J)                            # …/GSSCanada-main
sys.path.insert(0, DOCS_2J)                                        # for activity_loads

from activity_loads import (
    WEIGHT, APPLIANCE_W, BASELOAD_W, SHARED_BUCKETS, PERSONAL_BUCKETS,
    eff, slots_to_hours, N_WEEKDAY, N_WEEKEND,
)

DIARY_CSV = os.path.join(
    REPO_ROOT, '0_Occupancy', 'Outputs_21CEN22GSS',
    'aug_pipeline', '21CEN22GSS_aug_Full_Aggregated_excl.csv',
)
OUT_DIR = SCRIPT_DIR

# ── constants ─────────────────────────────────────────────────────────────────
DAYTYPE  = {'1': 'Weekday', '2': 'Weekend', '3': 'Weekend'}   # activity_loads.py / 07_aug_to_bem.py:33
BUCKETS  = ['baseload', 'cooking', 'dishwasher', 'washer', 'dryer', 'tv', 'pc']
COLORS   = {
    'baseload':   '#999999',
    'cooking':    '#e6550d',
    'dishwasher': '#3182bd',
    'washer':     '#6baed6',
    'dryer':      '#fd8d3c',
    'tv':         '#31a354',
    'pc':         '#74c476',
}
# GSS activity code labels (DR-2 / Step9_docs/deepResearch/Activity-Based Load Modeling Numbers.md)
ACT_LABELS = {
    0:  'Away (travel)', 1:  'Personal care',  2:  'HH work/maint',
    3:  'Care for others', 4:  'Away (other)', 5:  'Sleep',
    6:  'Meals/eating',   7:  'Other personal', 8:  'Education',
    9:  'TV/media',       10: 'Computer/games', 11: 'Reading',
    12: 'Away (social)',  13: 'Away (sport)',   14: 'Volunteer/civic',
}

# ── per-bucket load computation (replicates activity_loads.py:118-181) ────────
def compute_detailed(member_rows_by_daytype):
    """Return per-bucket 48-slot arrays and activity counts at each slot.

    Returns: {daytype: {'buckets': {name: arr48}, 'act_counts': {slot: Counter}}}
    """
    result = {}
    for day_type, member_rows in member_rows_by_daytype.items():
        bkt = {b: np.zeros(48) for b in BUCKETS}
        bkt['baseload'] = np.full(48, BASELOAD_W)   # activity_loads.py:137

        act_counts = [{} for _ in range(48)]         # activity-code count per slot

        dw_queue    = 0
        dw_cooldown = 0

        for t in range(48):
            slot_key   = f'{t + 1:03d}'
            home_acts  = []
            for row in member_rows:
                a = int(row.get(f'act30_{slot_key}') or 0)
                h = int(row.get(f'hom30_{slot_key}') or 0)
                if h > 0:
                    home_acts.append(a)

            n_present = len(home_acts)
            eff_n     = eff(n_present)               # activity_loads.py:55-59

            # activity-code tally at this slot
            for a in home_acts:
                act_counts[t][a] = act_counts[t].get(a, 0) + 1

            if n_present > 0:
                # shared buckets: max weight × eff_n  (activity_loads.py:155-158)
                for bucket in ('cooking', 'washer', 'dryer', 'tv'):
                    max_wt = max(
                        (WEIGHT.get(a, {}).get(bucket, 0.0) for a in home_acts),
                        default=0.0,
                    )
                    bkt[bucket][t] = max_wt * APPLIANCE_W[bucket] * eff_n

                # dishwasher trigger (RF1)  activity_loads.py:161-163
                if dw_queue == 0 and dw_cooldown == 0:
                    if any(WEIGHT.get(a, {}).get('dishwasher', 0.0) > 0 for a in home_acts):
                        dw_queue = 3

                # personal bucket: sum of weights  activity_loads.py:165-167
                pc_wt = sum(WEIGHT.get(a, {}).get('pc', 0.0) for a in home_acts)
                bkt['pc'][t] = pc_wt * APPLIANCE_W['pc']

            # dishwasher queue runs regardless of activity  activity_loads.py:172-179
            if dw_queue > 0:
                bkt['dishwasher'][t] = APPLIANCE_W['dishwasher'] * eff_n
                dw_queue -= 1
                if dw_queue == 0:
                    dw_cooldown = 6
            elif dw_cooldown > 0:
                dw_cooldown -= 1

        result[day_type] = {'buckets': bkt, 'act_counts': act_counts}
    return result


# ── read + group diary CSV ────────────────────────────────────────────────────
print(f'Reading {DIARY_CSV} ...')
hh_rows = {}   # hh_id -> list of row dicts

with open(DIARY_CSV, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['CYCLE_YEAR'] != '2022':
            continue
        if row['DTYPE'] != '1':          # SingleD only
            continue
        hh_id = row['HH_ID']
        if hh_id not in hh_rows:
            hh_rows[hh_id] = []
        hh_rows[hh_id].append(row)

n_hh = len(hh_rows)
print(f'  {n_hh:,} 2022 SingleD households loaded (DTYPE=1, CYCLE_YEAR=2022)')
print(f'  Source: {os.path.relpath(DIARY_CSV, REPO_ROOT)}')

# ── compute per-household detailed schedules + accumulate ────────────────────
print('Computing per-bucket diurnals ...')

# accumulators: one 48-slot sum per bucket per day type
sum_bkt  = {dt: {b: np.zeros(48) for b in BUCKETS} for dt in ('Weekday', 'Weekend')}
sum_acts = {dt: [{} for _ in range(48)] for dt in ('Weekday', 'Weekend')}
hh_count = {'Weekday': 0, 'Weekend': 0}

for hh_id, rows in hh_rows.items():
    # split rows by day type
    by_dt = {'Weekday': [], 'Weekend': []}
    for row in rows:
        dt = DAYTYPE.get(row['DDAY_STRATA'], 'Weekday')
        by_dt[dt].append(row)

    # fallback if one day type missing (donor-draw: 07_aug_to_bem.py:70-73)
    if not by_dt['Weekday'] and by_dt['Weekend']:
        by_dt['Weekday'] = by_dt['Weekend']
    elif not by_dt['Weekend'] and by_dt['Weekday']:
        by_dt['Weekend'] = by_dt['Weekday']

    detail = compute_detailed(by_dt)

    for dt in ('Weekday', 'Weekend'):
        if dt not in detail:
            continue
        bkt      = detail[dt]['buckets']
        act_cnts = detail[dt]['act_counts']
        for b in BUCKETS:
            sum_bkt[dt][b] += bkt[b]
        for t in range(48):
            for a, cnt in act_cnts[t].items():
                sum_acts[dt][t][a] = sum_acts[dt][t].get(a, 0) + cnt
        hh_count[dt] += 1

# ── population-mean diurnal ───────────────────────────────────────────────────
# Annual-weighted mean (261 WD + 104 WE) / 365
mean_bkt = {}
for b in BUCKETS:
    wd48 = sum_bkt['Weekday'][b] / hh_count['Weekday']
    we48 = sum_bkt['Weekend'][b] / hh_count['Weekend']
    wd24 = slots_to_hours(wd48)
    we24 = slots_to_hours(we48)
    mean_bkt[b] = (N_WEEKDAY * wd24 + N_WEEKEND * we24) / 365.0

total_24 = sum(mean_bkt[b] for b in BUCKETS)

# ── peak hour analysis ────────────────────────────────────────────────────────
peak_h     = int(np.argmax(total_24))
peak_W     = float(total_24[peak_h])
print(f'\n-- Peak hour analysis ----------------------------------------------')
print(f'  Population-mean diurnal peak: h{peak_h:02d}  ({peak_W:.1f} W average power)')
print(f'  Source: activity_loads.py:118-181 + {os.path.relpath(DIARY_CSV, REPO_ROOT)}')
print()
print(f'  Per-bucket contributions at h{peak_h:02d}:')
total_at_peak = sum(float(mean_bkt[b][peak_h]) for b in BUCKETS)
for b in BUCKETS:
    w   = float(mean_bkt[b][peak_h])
    pct = 100.0 * w / total_at_peak if total_at_peak > 0 else 0.0
    print(f'    {b:12s}: {w:6.1f} W  ({pct:4.1f}%)')

dryer_pct = 100.0 * float(mean_bkt['dryer'][peak_h]) / total_at_peak if total_at_peak > 0 else 0.0
print(f'\n  Dryer share of peak: {dryer_pct:.1f}%  '
      f'(APPLIANCE_W[dryer]=2100W, activity_loads.py:73)')

# ── activity-code attribution at peak hour ───────────────────────────────────
# Annual-weighted activity counts at peak hour (slots peak_h*2 and peak_h*2+1)
def annual_weighted_act_counts(slot_a, slot_b):
    out = {}
    for a, cnt in sum_acts['Weekday'][slot_a].items():
        out[a] = out.get(a, 0) + N_WEEKDAY * cnt / hh_count['Weekday']
    for a, cnt in sum_acts['Weekday'][slot_b].items():
        out[a] = out.get(a, 0) + N_WEEKDAY * cnt / hh_count['Weekday']
    for a, cnt in sum_acts['Weekend'][slot_a].items():
        out[a] = out.get(a, 0) + N_WEEKEND * cnt / hh_count['Weekend']
    for a, cnt in sum_acts['Weekend'][slot_b].items():
        out[a] = out.get(a, 0) + N_WEEKEND * cnt / hh_count['Weekend']
    # divide by 2 slots × 365 to get per-day fraction
    total_person_slots = 2 * 365.0
    return {a: v / total_person_slots for a, v in out.items()}

peak_act = annual_weighted_act_counts(peak_h * 2, peak_h * 2 + 1)
total_act = sum(peak_act.values())
print(f'\n  Activity-code mix at h{peak_h:02d} (annual-weighted person-count fraction):')
for a in sorted(peak_act, key=lambda x: -peak_act[x]):
    pct = 100.0 * peak_act[a] / total_act if total_act > 0 else 0.0
    label = ACT_LABELS.get(a, f'code{a}')
    high_load = [k for k,v in WEIGHT.get(a, {}).items()
                 if k != 'lighting' and v > 0]
    loads_str = ', '.join(f'{k}×{WEIGHT[a][k]}' for k in high_load) if high_load else '—'
    print(f'    act{a:2d} ({label:20s}): {pct:4.1f}%  loads: {loads_str}')

# ── sleep-hour breakdown (h00-h05, i.e. slots 0-11) ─────────────────────────
SLEEP_HOURS = list(range(6))   # h00-h05 (midnight to 06:00); G3 window h02-h05 is subset
print(f'\n-- Sleep-hour breakdown (h00-h05 = slots 0-11) --------------------')
print(f'  [G3 gate uses h02-h05; full window shown for context]')
sleep_bkt_mean = {}
for b in BUCKETS:
    vals = float(np.mean(mean_bkt[b][SLEEP_HOURS]))
    sleep_bkt_mean[b] = vals

total_sleep = sum(sleep_bkt_mean.values())
for b in BUCKETS:
    w   = sleep_bkt_mean[b]
    pct = 100.0 * w / total_sleep if total_sleep > 0 else 0.0
    print(f'  {b:12s}: {w:6.2f} W mean  ({pct:4.1f}%)')

# G3 window h02-h05 specifically
G3_HOURS = [2, 3, 4, 5]
g3_total = float(np.sum([sum(mean_bkt[b][h] for b in BUCKETS) for h in G3_HOURS]))
g3_base  = float(np.sum([mean_bkt['baseload'][h] for h in G3_HOURS]))
g3_dw    = float(np.sum([mean_bkt['dishwasher'][h] for h in G3_HOURS]))
# val.py threshold is mean_sleep_wh = sleep_sum_j/3600/sleep_n where sleep_n=4*365*n_hh
# = mean watts at h02-h05 (Wh per 1-hr record); threshold = 300 W (step9_validate_full.py:165)
n_g3 = len(G3_HOURS)
g3_base_W  = g3_base / n_g3     # mean watts from baseload at h02-h05
g3_dw_W    = g3_dw   / n_g3     # mean watts from dishwasher queue at h02-h05
g3_total_W = g3_total / n_g3    # mean watts total (pre-calibration)
print(f'\n  G3 window h02-h05 mean-power breakdown (threshold = 300 W per step9_validate_full.py:165):')
print(f'    Note: E+ h02-h05 = diary h02-h05 = real clock 06:00-09:59 (4h diary offset;')
print(f'          06_longitudinalForecastingGSS_val.py:334 confirms slot 1 = 04:00)')
print(f'    Baseload mean    : {g3_base_W:.1f} W  '
      f'= BASELOAD_W {BASELOAD_W:.0f}W (activity_loads.py:79)')
print(f'    Dishwasher mean  : {g3_dw_W:.1f} W  (morning queue tail, ~06-09h real clock)')
print(f'    Other activity   : {g3_total_W - g3_base_W - g3_dw_W:.1f} W  (cooking, washer, dryer, tv, pc)')
print(f'    Total mean (raw) : {g3_total_W:.1f} W  > 300W -> WARN pre-calibration')
print(f'    E+ calibrated    : ~530 W  (cluster_run_results.csv: Calgary=529.9, all SingleD WARN)')
print(f'    Baseload alone   : {g3_base_W:.1f} W < 300W -> baseload alone would PASS (NOT the root cause)')
print(f'    Root cause       : morning activity in E+ "sleep window" due to 4h diary offset')

# ── FIGURE I1: stacked area, bucket decomposition 24h ────────────────────────
hours = np.arange(24)
fig1, ax1 = plt.subplots(figsize=(10, 5))
bottom = np.zeros(24)
for b in BUCKETS:
    ax1.bar(hours, mean_bkt[b], bottom=bottom, color=COLORS[b], label=b, width=0.85)
    bottom += mean_bkt[b]

ax1.set_xlabel('Hour of day')
ax1.set_ylabel('Mean power (W)')
ax1.set_title('figI1 — Population-mean equipment diurnal by bucket\n'
              '2022 SingleD households (annual-weighted; n = {:,})'.format(n_hh))
ax1.set_xticks(hours)
ax1.set_xticklabels([f'{h:02d}' for h in hours], fontsize=7)
ax1.axvline(peak_h, color='red', linestyle='--', lw=1.5, label=f'Peak h{peak_h:02d}')
ax1.legend(loc='upper left', fontsize=8, ncol=2)
ax1.set_xlim(-0.5, 23.5)
out1 = os.path.join(OUT_DIR, 'figI1_bucket_decomp.png')
fig1.tight_layout()
fig1.savefig(out1, dpi=150)
print(f'\nSaved: {os.path.relpath(out1, REPO_ROOT)}')

# ── FIGURE I2: activity-code attribution at peak hour ────────────────────────
codes_sorted = sorted(peak_act, key=lambda x: -peak_act[x])
fracs = [peak_act[c] for c in codes_sorted]
labels_short = [f'act{c}\n{ACT_LABELS.get(c, str(c))[:12]}' for c in codes_sorted]

fig2, ax2 = plt.subplots(figsize=(11, 4))
x = np.arange(len(codes_sorted))
bars = ax2.bar(x, fracs, color='steelblue', alpha=0.8)
ax2.set_xlabel('Activity code')
ax2.set_ylabel('Annual-weighted person-fraction')
ax2.set_title(f'figI2 — Activity-code mix at peak hour h{peak_h:02d}\n'
              '2022 SingleD, annual-weighted over 365 days')
ax2.set_xticks(x)
ax2.set_xticklabels(labels_short, fontsize=7)
# annotate bucket loads for each code
for bar, code in zip(bars, codes_sorted):
    high = {k: v for k, v in WEIGHT.get(code, {}).items() if k != 'lighting' and v > 0}
    if high:
        note = '\n'.join(f'{k[:3]}×{v:.0%}' for k, v in list(high.items())[:2])
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
                 note, ha='center', va='bottom', fontsize=6, color='darkred')
out2 = os.path.join(OUT_DIR, 'figI2_peak_attribution.png')
fig2.tight_layout()
fig2.savefig(out2, dpi=150)
print(f'Saved: {os.path.relpath(out2, REPO_ROOT)}')

# ── FIGURE I3: sleep-hour bucket breakdown h00-h05 ───────────────────────────
sleep_h = list(range(6))
sleep_total_by_h = np.array([sum(mean_bkt[b][h] for b in BUCKETS) for h in sleep_h])

fig3, axes = plt.subplots(1, 2, figsize=(12, 4))

# left: stacked bar per hour
ax3a = axes[0]
bottom = np.zeros(len(sleep_h))
for b in BUCKETS:
    vals = [mean_bkt[b][h] for h in sleep_h]
    ax3a.bar(sleep_h, vals, bottom=bottom, color=COLORS[b], label=b, width=0.7)
    bottom += np.array(vals, dtype=float)
ax3a.axhline(300, color='red', linestyle='--', lw=1.5, label='G3 300 Wh threshold')
ax3a.set_xlabel('Hour of day')
ax3a.set_ylabel('Mean power (W)')
ax3a.set_title('figI3a — Sleep-window bucket breakdown\n(300 Wh/h = 300 W at 1 h resolution)')
ax3a.set_xticks(sleep_h)
ax3a.set_xticklabels([f'h{h:02d}' for h in sleep_h])
ax3a.legend(fontsize=7)

# right: pie — average Wh composition over h02-h05
ax3b = axes[1]
g3_bucket_wh = {b: float(np.sum([mean_bkt[b][h] for h in G3_HOURS])) for b in BUCKETS}
nonzero = {b: v for b, v in g3_bucket_wh.items() if v > 0.5}
ax3b.pie(nonzero.values(),
         labels=[f'{b}\n{v:.1f} Wh' for b, v in nonzero.items()],
         colors=[COLORS[b] for b in nonzero],
         autopct='%1.0f%%', startangle=90, textprops={'fontsize': 8})
ax3b.set_title('figI3b — G3 window (h02–h05) Wh composition\n'
               f'Total: {sum(nonzero.values()):.1f} Wh, threshold 300 Wh')

out3 = os.path.join(OUT_DIR, 'figI3_sleep_breakdown.png')
fig3.tight_layout()
fig3.savefig(out3, dpi=150)
print(f'Saved: {os.path.relpath(out3, REPO_ROOT)}')

print('\nDone.')
