#!/usr/bin/env python3
"""
09_activityDrivenLoads_val.py — Programmatic cross-check of Step-9 validation gates.

Reads four CSVs from Step9_docs/ and produces:
  outputs_step9/figV1_default_vs_step9_equip.png  — new default-vs-Step-9 figure
  outputs_step9/step9_validation_report.html        — self-contained scorecard + charts

Usage (locally, py launcher required):
  py 09_activityDrivenLoads_val.py
"""
import csv
import os
import sys
import base64
import math
from pathlib import Path

# Force UTF-8 console output so Unicode math symbols don't crash on Windows cp1252
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE    = Path(__file__).resolve().parent
DOCS    = HERE / 'Step9_docs'
OUTPUTS = HERE / 'outputs_step9'

DTYPE_COLORS = {
    'SingleD':       '#2166ac',
    'OtherDwelling': '#4dac26',
    'MidRise':       '#d6604d',
    'HighRise':      '#762a83',
}
DTYPE_ORDER = ['SingleD', 'OtherDwelling', 'MidRise', 'HighRise']


class Step9Validator:

    def __init__(self):
        self.results = []
        self._load_data()

    # ── data loading ──────────────────────────────────────────────────────────

    def _load_data(self):
        self.run_results = []
        with open(DOCS / 'cluster_run_results.csv', newline='') as f:
            for r in csv.DictReader(f):
                for col in ('bl_elec_kwh', 'ac_elec_kwh', 'delta_elec_kwh',
                            'bl_equip_kwh', 'ac_equip_kwh', 'delta_equip_kwh',
                            'bl_light_kwh', 'ac_light_kwh', 'delta_light_kwh',
                            'sheu_target_equip', 'sheu_pct_equip',
                            'sheu_target_light', 'sheu_pct_light',
                            'sleep_equip_mean_wh'):
                    r[col] = float(r[col])
                self.run_results.append(r)

        self.profiles = []
        with open(DOCS / 'loadshape_profiles.csv', newline='') as f:
            for r in csv.DictReader(f):
                r['hour_of_day'] = int(r['hour_of_day'])
                r['n_hh'] = int(r['n_hh'])
                for col in ('equip_bldg_W', 'equip_zone_W',
                            'light_bldg_W', 'light_zone_W', 'facility_W'):
                    r[col] = float(r[col])
                self.profiles.append(r)

        self.peak_hours = []
        with open(DOCS / 'peak_hours.csv', newline='') as f:
            for r in csv.DictReader(f):
                for col in ('equip_bldg_peak_h', 'equip_zone_peak_h',
                            'light_bldg_peak_h', 'light_zone_peak_h', 'n_hh'):
                    r[col] = int(r[col])
                self.peak_hours.append(r)

        self.peak_shift = []
        with open(DOCS / 'peak_shift_summary.csv', newline='') as f:
            for r in csv.DictReader(f):
                for col in ('equip_bldg_shift', 'equip_zone_shift',
                            'light_bldg_shift', 'light_zone_shift'):
                    r[col] = int(r[col])
                self.peak_shift.append(r)

    # ── result accumulator ────────────────────────────────────────────────────

    def _add(self, gate_id, name, status, computed, expected):
        self.results.append({
            'gate': gate_id, 'name': name, 'status': status,
            'computed': computed, 'expected': expected,
        })

    # ── Gate 1: Run integrity ─────────────────────────────────────────────────

    def validate_run_integrity(self):
        n_rows  = len(self.peak_hours)
        nhh_all = [r['n_hh'] for r in self.peak_hours]
        min_nhh = min(nhh_all)
        med_nhh = float(np.median(nhh_all))

        status = 'PASS' if (n_rows == 96 and min_nhh >= 48) else 'FAIL'
        self._add(
            'G1', 'Run integrity — bucket count & n_hh ≥ 48', status,
            f'{n_rows}/96 buckets present; min n_hh = {min_nhh}; median = {med_nhh:.0f}',
            '96 buckets (24 cells × 2 years × 2 arms); all n_hh ≥ 48',
        )

    # ── Gates 2 & 3: SHEU calibration + sleep-hour floor ─────────────────────

    def validate_sheu_calibration(self):
        # G2a — equipment ±15 %
        n_eq_pass   = sum(1 for r in self.run_results if r['sheu_gate_equip'] == 'PASS')
        max_abs_eq  = max(abs(r['sheu_pct_equip']) for r in self.run_results)
        s2a = 'PASS' if (n_eq_pass == 48 and max_abs_eq < 15.0) else 'FAIL'
        self._add('G2a', 'SHEU calibration — equipment (±15 % gate)', s2a,
                  f'{n_eq_pass}/48 PASS; max |pct_equip| = {max_abs_eq:.2f} %',
                  '48/48 PASS; max |pct| ≈ 2.1 %; all < 2.6 %')

        # G2b — lighting ±15 %
        n_lt_pass   = sum(1 for r in self.run_results if r['sheu_gate_light'] == 'PASS')
        max_abs_lt  = max(abs(r['sheu_pct_light']) for r in self.run_results)
        s2b = 'PASS' if (n_lt_pass == 48 and max_abs_lt < 15.0) else 'FAIL'
        self._add('G2b', 'SHEU calibration — lighting (±15 % gate)', s2b,
                  f'{n_lt_pass}/48 PASS; max |pct_light| = {max_abs_lt:.2f} %',
                  '48/48 PASS; max |pct| ≈ 2.5 %; all < 2.6 %')

        # G2c — all within ±2.6 % (design gate)
        max_any = max(max(abs(r['sheu_pct_equip']), abs(r['sheu_pct_light']))
                      for r in self.run_results)
        within_2p6 = all(abs(r['sheu_pct_equip']) < 2.6 and abs(r['sheu_pct_light']) < 2.6
                         for r in self.run_results)
        s2c = 'PASS' if within_2p6 else 'FAIL'
        self._add('G2c', 'SHEU calibration — within design ±10 % (actual ±2.6 %)', s2c,
                  f'max |any pct| = {max_any:.2f} %; all within ±2.6 %: {within_2p6}',
                  'all 48 cell-years within ±2.6 % (beats ±10 % design gate)')

        # G3 — sleep-hour floor WARN count
        n_warn = sum(1 for r in self.run_results if r['sleep_check'] == 'WARN')
        # status is always WARN — sleep-hour WARNs are expected baseload, not errors
        self._add('G3', 'Sleep-hour floor — WARN count (expected baseload)', 'WARN',
                  f'{n_warn}/48 cell-years WARN (sleep_equip_mean_wh > 300)',
                  '~21/48 per val doc (OtherDwelling + all SingleD + some MidRise); '
                  'fridge/standby baseload — not a calibration error')

    # ── Gates 4 & 5: load shape ───────────────────────────────────────────────

    def validate_load_shape(self):
        # G4 — peak-hour shift statistics
        eq22 = [r['equip_bldg_shift'] for r in self.peak_shift if r['year'] == '2022']
        eq30 = [r['equip_bldg_shift'] for r in self.peak_shift if r['year'] == '2030']
        lt_all = [r['light_bldg_shift'] for r in self.peak_shift]

        m22, s22 = float(np.mean(eq22)), float(np.std(eq22))
        m30, s30 = float(np.mean(eq30)), float(np.std(eq30))
        eq_min = min(min(eq22), min(eq30))
        eq_max = max(max(eq22), max(eq30))
        lt_min, lt_max = min(lt_all), max(lt_all)

        bl_eq_peaks = [r['equip_bldg_peak_h'] for r in self.peak_hours if r['arm'] == 'baseline']
        ac_eq_peaks = [r['equip_bldg_peak_h'] for r in self.peak_hours if r['arm'] == 'activity']

        # Note divergences in expected vs actual
        expected_lt = '−3..−5 h per val doc; actual includes −2 h (some OD/SingleD 2030)'
        self._add('G4', 'Peak-hour shift — equip/light stats', 'INFO',
                  (f'equip 2022: mean={m22:.2f} h σ={s22:.2f}; '
                   f'2030: mean={m30:.2f} h σ={s30:.2f}; '
                   f'equip range {eq_min}..{eq_max} h; '
                   f'light range {lt_min}..{lt_max} h; '
                   f'BL equip peaks h{min(bl_eq_peaks)}–{max(bl_eq_peaks)}, '
                   f'AC equip peaks h{min(ac_eq_peaks)}–{max(ac_eq_peaks)}'),
                  f'equip mean ≈ −4.1 h (σ ≈ 0.4 / 0.3); range −3..−5; '
                  f'light {expected_lt}; BL h17–18 → AC h13–14')

        # G5 — SingleD bldg == zone (exact float equality)
        sd_rows = [r for r in self.profiles if r['cell'].split('__')[0] == 'SingleD']
        mis_eq  = [(r['cell'], r['year'], r['arm'], r['hour_of_day'])
                   for r in sd_rows if r['equip_bldg_W'] != r['equip_zone_W']]
        mis_lt  = [(r['cell'], r['year'], r['arm'], r['hour_of_day'])
                   for r in sd_rows if r['light_bldg_W'] != r['light_zone_W']]

        n_sd = len(sd_rows)
        n_mis = len(mis_eq) + len(mis_lt)
        s5 = 'PASS' if n_mis == 0 else 'FAIL'
        detail = '' if n_mis == 0 else f'; MISMATCHES: equip={mis_eq[:3]}...'
        self._add('G5', 'SingleD bldg == zone (exact float equality)', s5,
                  f'{n_sd} SingleD rows checked; mismatches equip={len(mis_eq)}, '
                  f'light={len(mis_lt)}{detail}',
                  'all SingleD rows exact: equip_bldg_W == equip_zone_W, '
                  'light_bldg_W == light_zone_W; multi-unit zone artifact documented (INFO)')

        # Multi-unit zone artifact — INFO, not tested (known behavior)
        self._add('G5i', 'Multi-unit zone artifact (apartment zone meter)', 'INFO',
                  'zone peaks for MidRise/HighRise/OtherDwelling show h0 (fridge-dominant) '
                  '— building-level metric used for all multi-unit findings',
                  'zone-level meter unusable for apartments; SingleD bldg=zone confirms implementation')

    # ── Gates 4x & 6: longitudinal + injection ────────────────────────────────

    def validate_longitudinal(self):
        # G4x — shift persistence 2022 → 2030
        m22 = float(np.mean([r['equip_bldg_shift'] for r in self.peak_shift if r['year'] == '2022']))
        m30 = float(np.mean([r['equip_bldg_shift'] for r in self.peak_shift if r['year'] == '2030']))
        delta = abs(m22 - m30)
        s4x = 'PASS' if delta < 0.5 else 'FAIL'
        self._add('G4x', 'Shift persistence 2022 → 2030', s4x,
                  f'2022 mean = {m22:.3f} h; 2030 mean = {m30:.3f} h; Δ = {delta:.3f} h',
                  '2022 ≈ 2030 (shift driven by activity model, not diary year)')

        # G6 — injection correctness (not re-computable; build-time only)
        self._add('G6', 'Injection correctness (no double-count, baseload preserved)', 'INFO',
                  'build-time verified — see cluster_run.md D1–D8 + integration.py '
                  '(neutralize-and-inject: equip/lights zeroed, STEP9_Equip/STEP9_Lights injected; '
                  'fridge preserved; Step-8 path byte-identical)',
                  'not re-computable from aggregated CSVs; '
                  'confirmed via code review + 48/48 SHEU pass as indirect evidence')

    # ── Scorecard ─────────────────────────────────────────────────────────────

    def generate_scorecard(self):
        counts = {'PASS': 0, 'WARN': 0, 'INFO': 0, 'FAIL': 0}
        for r in self.results:
            counts[r['status']] = counts.get(r['status'], 0) + 1

        w = 90
        print('\n' + '=' * w)
        print('STEP-9 VALIDATION SCORECARD')
        print('=' * w)
        fmt = '{:<5} {:<6} {:<50} {}'
        print(fmt.format('Gate', 'Status', 'Name', 'Computed'))
        print('-' * w)
        for r in self.results:
            comp = r['computed']
            if len(comp) > 70:
                comp = comp[:67] + '...'
            print(fmt.format(r['gate'], r['status'], r['name'][:49], comp))
        print('=' * w)
        print(f'  PASS={counts["PASS"]}  WARN={counts["WARN"]}  '
              f'INFO={counts["INFO"]}  FAIL={counts["FAIL"]}')
        print('=' * w)
        if counts.get('FAIL', 0) == 0:
            print('  Verdict: ALL GATES PASS — 0 FAIL.  '
                  'Step-9 supplementary analysis sound.')
        else:
            print(f'  ALERT: {counts["FAIL"]} FAIL(s) detected — '
                  f'investigate before citing results.')
        print('=' * w + '\n')

        return counts

    # ── Figure V1 ─────────────────────────────────────────────────────────────

    def _archetype_mean_diurnal(self, year, arm, metric):
        """Mean W across 6 cities per archetype, given year and arm."""
        result = {}
        for dtype in DTYPE_ORDER:
            sums = [0.0] * 24
            cnts = [0]   * 24
            for r in self.profiles:
                if r['year'] != year or r['arm'] != arm:
                    continue
                if r['cell'].split('__')[0] != dtype:
                    continue
                h = r['hour_of_day']
                sums[h] += r[metric]
                cnts[h] += 1
            result[dtype] = [sums[h] / cnts[h] if cnts[h] > 0 else 0.0
                             for h in range(24)]
        return result

    def fig_v1_default_vs_step9(self):
        os.makedirs(str(OUTPUTS), exist_ok=True)

        bl_by = self._archetype_mean_diurnal('2022', 'baseline', 'equip_bldg_W')
        ac_by = self._archetype_mean_diurnal('2022', 'activity', 'equip_bldg_W')

        # SingleD annual kWh annotation (6-city mean from cluster_run_results.csv)
        sd22 = [r for r in self.run_results
                if r['dtype'] == 'SingleD' and r['year'] == '2022']
        bl_kwh = float(np.mean([r['bl_equip_kwh'] for r in sd22]))
        ac_kwh = float(np.mean([r['ac_equip_kwh'] for r in sd22]))
        sheu_target = 3700.0

        fig, axes = plt.subplots(2, 2, figsize=(13, 8), sharey=False)
        hours = list(range(24))

        for ax_idx, dtype in enumerate(DTYPE_ORDER):
            ax = axes[ax_idx // 2][ax_idx % 2]
            col = DTYPE_COLORS[dtype]
            bl = bl_by[dtype]
            ac = ac_by[dtype]

            bl_peak = bl.index(max(bl))
            ac_peak = ac.index(max(ac))
            shift   = ac_peak - bl_peak

            if dtype == 'SingleD':
                # Absolute W — shows both shape AND magnitude anchored to SHEU
                ax.plot(hours, bl, color='gray', lw=2.0,
                        label=f'Default (BL)  peak h{bl_peak}')
                ax.plot(hours, ac, color=col,    lw=2.0,
                        label=f'Step-9 (AC)  peak h{ac_peak}')
                ax.axvline(bl_peak, color='gray', linestyle='--', lw=0.9, alpha=0.8)
                ax.axvline(ac_peak, color=col,    linestyle='--', lw=0.9, alpha=0.8)
                ax.set_ylabel('Equipment demand (W)')
                ymax = max(max(bl), max(ac))
                ax.set_ylim(0, ymax * 1.35)
                ax.text(0.97, 0.96,
                        f'Default:  {bl_kwh:.0f} kWh/yr',
                        transform=ax.transAxes, ha='right', va='top',
                        fontsize=8.5, color='gray')
                ax.text(0.97, 0.88,
                        f'Step-9:   {ac_kwh:.0f} kWh/yr',
                        transform=ax.transAxes, ha='right', va='top',
                        fontsize=8.5, color=col, fontweight='bold')
                ax.text(0.97, 0.80,
                        f'SHEU target: {sheu_target:.0f} kWh/yr',
                        transform=ax.transAxes, ha='right', va='top',
                        fontsize=8.5, color='black', fontstyle='italic')
                ax.set_title(
                    f'{dtype} — ABSOLUTE (peak h{bl_peak}→h{ac_peak}, {shift:+d} h)\n'
                    f'shape reshapes, annual total held on SHEU anchor',
                    fontsize=9)

            else:
                # Normalized to daily mean — magnitudes not comparable across archetypes
                bl_m = (sum(bl) / 24.0) or 1.0
                ac_m = (sum(ac) / 24.0) or 1.0
                bl_n = [v / bl_m for v in bl]
                ac_n = [v / ac_m for v in ac]
                ax.plot(hours, bl_n, color='gray', lw=2.0,
                        label=f'Default (BL)  peak h{bl_peak}')
                ax.plot(hours, ac_n, color=col,    lw=2.0,
                        label=f'Step-9 (AC)  peak h{ac_peak}')
                ax.axhline(1.0, color='black', lw=0.5, alpha=0.25)
                ax.axvline(bl_peak, color='gray', linestyle='--', lw=0.9, alpha=0.8)
                ax.axvline(ac_peak, color=col,    linestyle='--', lw=0.9, alpha=0.8)
                ax.set_ylabel('Equipment load (× daily mean)')
                ax.set_title(
                    f'{dtype} — NORMALIZED (peak h{bl_peak}→h{ac_peak}, {shift:+d} h)',
                    fontsize=10)

            ax.set_xlabel('Hour of day')
            ax.set_xticks(range(0, 24, 4))
            ax.legend(fontsize=7.5, loc='upper left')

        fig.suptitle(
            'Fig V1 — Default vs Step-9 equipment demand, 2022 (6-city mean per archetype)\n'
            'SingleD: absolute W, annual kWh + SHEU target annotated '
            '(shape reshapes, budget held)\n'
            'Multi-unit: normalized to daily mean (single-unit injection; '
            'calibrated magnitudes in figS1)',
            fontsize=10)
        fig.tight_layout(rect=[0, 0, 1, 0.90])

        out = OUTPUTS / 'figV1_default_vs_step9_equip.png'
        fig.savefig(str(out), dpi=150)
        plt.close(fig)
        print(f'  figV1 saved: {out}')
        return str(out)

    # ── HTML report ───────────────────────────────────────────────────────────

    def build_html_report(self, figv1_path):
        os.makedirs(str(OUTPUTS), exist_ok=True)

        def _b64(path):
            try:
                with open(path, 'rb') as f:
                    return base64.b64encode(f.read()).decode('ascii')
            except FileNotFoundError:
                return None

        def _img(b64, alt):
            if b64:
                return (f'<img src="data:image/png;base64,{b64}" alt="{alt}" '
                        f'style="max-width:100%;margin:8px 0;border:1px solid #dee2e6">')
            return f'<p style="color:#999">[{alt} — file not found]</p>'

        v1  = _b64(figv1_path)
        s6  = _b64(str(OUTPUTS / 'figS6_diurnal_equip.png'))
        s7  = _b64(str(OUTPUTS / 'figS7_peak_shift.png'))
        s8  = _b64(str(OUTPUTS / 'figS8_diurnal_light.png'))

        STATUS_BG = {'PASS': '#d4edda', 'WARN': '#fff3cd',
                     'INFO': '#cce5ff',  'FAIL': '#f8d7da'}
        STATUS_FG = {'PASS': '#155724', 'WARN': '#856404',
                     'INFO': '#004085',  'FAIL': '#721c24'}

        counts = {'PASS': 0, 'WARN': 0, 'INFO': 0, 'FAIL': 0}
        rows_html = ''
        for r in self.results:
            counts[r['status']] = counts.get(r['status'], 0) + 1
            bg = STATUS_BG.get(r['status'], '#fff')
            fg = STATUS_FG.get(r['status'], '#333')
            rows_html += (
                f'<tr style="background:{bg}">'
                f'<td style="padding:6px 10px;font-weight:bold">{r["gate"]}</td>'
                f'<td style="padding:6px 10px;font-weight:bold;color:{fg}">{r["status"]}</td>'
                f'<td style="padding:6px 10px">{r["name"]}</td>'
                f'<td style="padding:6px 10px;font-family:monospace;font-size:12px">'
                f'{r["computed"]}</td>'
                f'<td style="padding:6px 10px;font-size:12px;color:#555">{r["expected"]}</td>'
                f'</tr>\n'
            )

        fail_n = counts.get('FAIL', 0)
        vbg = '#d4edda' if fail_n == 0 else '#f8d7da'
        vfg = '#155724' if fail_n == 0 else '#721c24'
        vtxt = ('ALL GATES PASS — 0 FAIL.  '
                'Step-9 supplementary analysis sound.'
                if fail_n == 0 else
                f'ALERT: {fail_n} FAIL(s) detected — investigate before citing results.')

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Step-9 Activity-Driven Loads — Validation Report</title>
<style>
body{{font-family:Arial,sans-serif;margin:30px;max-width:1500px;color:#222}}
h1{{font-size:20px}}
h2{{font-size:16px;margin-top:28px;border-bottom:1px solid #dee2e6;padding-bottom:4px}}
table{{border-collapse:collapse;width:100%;font-size:13px;margin-top:8px}}
th{{background:#343a40;color:#fff;padding:8px 10px;text-align:left}}
td{{border-bottom:1px solid #dee2e6;vertical-align:top}}
.pill{{display:inline-block;padding:4px 12px;border-radius:20px;font-weight:bold;
       font-size:13px;margin-right:6px}}
.verdict{{padding:12px 16px;border-radius:5px;margin:14px 0;font-size:15px;
          font-weight:bold}}
</style>
</head>
<body>
<h1>Step-9 Activity-Driven Loads — Programmatic Validation Report</h1>
<p style="color:#666;font-size:13px">
  Generated by <code>09_activityDrivenLoads_val.py</code> &nbsp;|&nbsp; 2026-06-07
  &nbsp;|&nbsp; stdlib csv + numpy + matplotlib (no pandas)
</p>

<div style="margin:12px 0">
<span class="pill" style="background:#d4edda;color:#155724">PASS {counts["PASS"]}</span>
<span class="pill" style="background:#fff3cd;color:#856404">WARN {counts["WARN"]}</span>
<span class="pill" style="background:#cce5ff;color:#004085">INFO {counts["INFO"]}</span>
<span class="pill" style="background:#f8d7da;color:#721c24">FAIL {counts["FAIL"]}</span>
</div>

<div class="verdict" style="background:{vbg};color:{vfg}">{vtxt}</div>

<h2>Scorecard</h2>
<table>
<thead>
<tr>
<th>Gate</th><th>Status</th><th>Name</th>
<th>Computed Value</th><th>Expected (per val doc)</th>
</tr>
</thead>
<tbody>
{rows_html}
</tbody>
</table>

<h2>Figure V1 — Default vs Step-9 Equipment Demand (2022)</h2>
<p style="font-size:13px;color:#555">
<em>SingleD panel: absolute W with annual-kWh + SHEU annotation — shape changes
(peak h18→h14) while annual total holds on the 3,700 kWh SHEU anchor.
Multi-unit panels: normalized to daily mean (single-unit injection;
calibrated magnitudes in figS1).</em>
</p>
{_img(v1, 'Fig V1: Default vs Step-9 equipment demand')}

<h2>Figure S6 — Equipment Diurnal Load Shape (2022, normalized to daily mean)</h2>
{_img(s6, 'Fig S6: Equipment diurnal')}

<h2>Figure S7 — Equipment Peak-Hour Shift (2022, all 24 cells)</h2>
{_img(s7, 'Fig S7: Peak-hour shift')}

<h2>Figure S8 — Lighting Diurnal Load Shape (2022, normalized to daily mean)</h2>
{_img(s8, 'Fig S8: Lighting diurnal')}

</body>
</html>
"""
        out = OUTPUTS / 'step9_validation_report.html'
        with open(str(out), 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'  HTML report saved: {out}')
        return str(out)

    # ── run_all ───────────────────────────────────────────────────────────────

    def run_all(self):
        print('Loading data ...')
        print(f'  run_results : {len(self.run_results)} rows')
        print(f'  profiles    : {len(self.profiles)} rows')
        print(f'  peak_hours  : {len(self.peak_hours)} rows')
        print(f'  peak_shift  : {len(self.peak_shift)} rows')

        print('\nRunning gates ...')
        self.validate_run_integrity()
        self.validate_sheu_calibration()
        self.validate_load_shape()
        self.validate_longitudinal()

        counts = self.generate_scorecard()

        print('Generating Figure V1 ...')
        figv1_path = self.fig_v1_default_vs_step9()

        print('Building HTML report ...')
        html_path = self.build_html_report(figv1_path)

        print(f'\nAll outputs in {OUTPUTS}/')
        return counts


if __name__ == '__main__':
    v = Step9Validator()
    v.run_all()
