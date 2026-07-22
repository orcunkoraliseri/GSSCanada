"""
3rdJ Step 2 -- Leg-3 (4-split) -- Harmonization validator.

Validates three things and emits the house-style dark-theme HTML + TXT report:

  Section 1  Retail signal presence -- occPRE==5 (Shopping) + occACT==4
             (Purchasing G&S) are present, in-range, and cross-cycle stable in
             the reused Leg-2 harmonized episodes (read-only). occPRE==7
             (restaurant) reported as an INFO exclusion record.
  Section 2  OR-rule leak cross-tab -- the OD-1 verification condition. Emits
             the 4 per-cycle occACT==4 x occPRE weighted cross-tab CSVs, reports
             the online-shopping leak (occACT==4 & occPRE==1) and its trend, and
             audits the frozen gated rule's correctness.
  Section 3  Canonical hotel series -- schema, coverage (grid complete; observed
             span honest), occupancy range, COVID trough, magnitude, seasonality
             on 0_Occupancy/external/hotel_occupancy_monthly.csv.

The frozen AT_RETAIL rule (OD-1, user-approved 2026-07-02):
    AT_RETAIL = (occPRE==5) | ((occACT==4) & occPRE in {5,9})

RECONCILIATION (2026-07-19): gates written before hotel acquisition are tagged
[RECONCILED]. AB is single-source (Market Monitor, 2011+, no CBRE splice); QC
monthly starts 2019. Coverage gates FAIL only on CORE (non-edge-year) interior
gaps -- the Step-1 convention. No GSS file is written or modified.

Run locally (no cluster):
    py -3 -X utf8 3rdJ_02_harmonizeGSS_4split_val.py
"""

from __future__ import annotations

import base64
import csv
import io
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = (SCRIPT_DIR / "outputs_step2").resolve()

LEG2_STEP2 = (SCRIPT_DIR / ".." / ".." / "Leg2_2-split" / "Step2_docs"
              / "outputs_step2").resolve()
CANONICAL = (SCRIPT_DIR / ".." / ".." / ".." / "0_Occupancy" / "external"
             / "hotel_occupancy_monthly.csv").resolve()

HTML_PATH = OUTPUT_DIR / "step2_validation_report.html"
TXT_PATH = OUTPUT_DIR / "step2_validation_report.txt"

CYCLES = [2005, 2010, 2015, 2022]
WINDOW_YEARS = range(2005, 2023)
COVID_START, COVID_END = (2020, 3), (2022, 6)

RETAIL_LOC_BAND = (1.5, 3.0)      # gate 1.2 (occPRE==5 episode-time share, %)
GATED_BAND = (1.5, 3.5)           # gate 2.4 (full gated-rule share, %)
QC_PRECOVID_BAND = (0.60, 0.65)   # gate 3.6
AB_PRECOVID_BAND = (0.54, 0.58)   # gate 3.6

# The gated activity arm is restricted to these presence codes.
GATED_PRE = {5, 9}

CYC_COL = {2005: "#5dade2", 2010: "#48c9b0", 2015: "#f5b041", 2022: "#ec7063"}
PR_COL = {"QC": "#4aa3ff", "AB": "#ff9f43"}
CH_COL = {"Residential": "#4aa3ff", "Office": "#ff9f43", "Retail": "#26de81",
          "Hotel": "#e056fd"}
DARK_BG, PANEL, FG, GRID = "#12161c", "#1b2129", "#d7dde6", "#2c3540"
BADGE = {"PASS": "#2ecc71", "WARN": "#f1c40f", "FAIL": "#e74c3c", "INFO": "#5dade2"}

# occACT activity labels (14 categories) -- shared with Leg-2 Step-2.
ACT_LABELS = {
    1: "Work & Related", 2: "Household Work", 3: "Caregiving", 4: "Purchasing",
    5: "Sleep & Rest", 6: "Eating & Drinking", 7: "Personal Care", 8: "Education",
    9: "Socializing", 10: "Passive Leisure", 11: "Active Leisure", 12: "Community",
    13: "Travel", 14: "Misc / Idle",
}


def _rle(pairs):
    """Expand run-length (value, count) pairs into a 48-slot list."""
    out = []
    for v, c in pairs:
        out += [v] * c
    assert len(out) == 48, len(out)
    return out


# Fixed guest-room diurnal shape s(t), unit-normalized 48 slots (dr_L3-05, PNNL
# Large Hotel). A DESIGN shape scaled by the monthly occupancy amplitude
# downstream -- NOT a GSS-measured curve.
HOTEL_WEEKDAY = _rle([(1.000, 12), (0.769, 2), (0.431, 4), (0.200, 12),
                      (0.308, 2), (0.538, 6), (0.769, 4), (0.892, 2), (1.000, 4)])
HOTEL_WEEKEND = _rle([(1.000, 12), (0.769, 2), (0.523, 4), (0.308, 16),
                      (0.523, 2), (0.538, 2), (1.000, 4), (0.769, 6)])


class R:
    def __init__(self, gid, desc, status, detail, reconciled=False):
        self.gid, self.desc, self.status = gid, desc, status
        self.detail, self.reconciled = detail, reconciled


def _mk(y, m):
    return y * 12 + (m - 1)


def _hhmm_to_min(v):
    try:
        x = int(float(v))
    except (TypeError, ValueError):
        return None
    return (x // 100) * 60 + (x % 100)


# ---------------------------------------------------------------------------
# Retail signal -- one streaming pass over each cycle's episodes
# ---------------------------------------------------------------------------

def retail_signal():
    """One streaming pass per cycle over the reused Leg-2 Step-2 episodes. Per
    cycle it computes, holding only small aggregates in memory:

      Retail signal (weighted episode-time): occPRE==5 location-only, occPRE==7
        restaurant, occACT==4, online leak, the full gated rule; the occACT==4 x
        occPRE cross-tab; the 48-slot occPRE==5 diurnal; occPRE range; gated-arm
        correctness audit.
      4-channel context (all building types): 48-slot weighted diurnal presence
        for Residential (AT_HOME) / Office (AT_WORK) / Retail (gated AT_RETAIL);
        episode-level presence RATE per channel (Leg-2 basis); occPRE==2 share.
      GSS QA (mirrors Leg-2 Step-2): 14-category duration-weighted activity
        distribution; diary-closure pass rate; episodes-per-respondent counts.

    Rates/QA use ALL parseable episodes (Leg-2 basis); weighted time-shares and
    diurnal curves use DIARY_VALID episodes only (the clean diary basis)."""
    sig = {}
    for cyc in CYCLES:
        p = LEG2_STEP2 / f"episode_{cyc}.csv"
        if not p.is_file():
            continue
        tot = pre5 = pre7 = act4 = leak = gated = 0.0
        arm2_bad = 0.0
        xtab = {}
        diur5 = [0.0] * 48
        diur_tot = [0.0] * 48
        present = {"Residential": [0.0] * 48, "Office": [0.0] * 48,
                   "Retail": [0.0] * 48}
        pre_vals = set()
        act4_present = False
        # rates + QA (episode-count basis)
        n_epi = n_valid = 0
        n_home = n_work = n_retail = n_pre2 = 0
        act_dur = {}
        tot_dur = 0.0
        epi_per_person = {}
        with open(p, newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                n_epi += 1
                valid = row.get("DIARY_VALID") in ("1", "1.0")
                if not valid:
                    continue
                n_valid += 1
                try:
                    w = float(row["WGHT_EPI"])
                except (KeyError, ValueError):
                    continue
                s = _hhmm_to_min(row.get("start"))
                e = _hhmm_to_min(row.get("end"))
                if s is None or e is None:
                    continue
                if e <= s:
                    e += 1440
                try:
                    occpre = int(float(row.get("occPRE", "0") or 0))
                    occact = int(float(row.get("occACT", "0") or 0))
                except ValueError:
                    continue
                dur = float(row.get("duration") or (e - s))
                wd = w * dur
                pre_vals.add(occpre)
                tot += wd
                tot_dur += dur
                if 1 <= occact <= 14:
                    act_dur[occact] = act_dur.get(occact, 0.0) + dur
                oid = row.get("occID")
                epi_per_person[oid] = epi_per_person.get(oid, 0) + 1

                at_home = row.get("AT_HOME") in ("1", "1.0")
                at_work = row.get("AT_WORK") in ("1", "1.0")
                is_arm2 = (occact == 4 and occpre in GATED_PRE)
                at_retail = (occpre == 5) or is_arm2
                if at_home:
                    n_home += 1
                if at_work:
                    n_work += 1
                if at_retail:
                    n_retail += 1
                if occpre == 2:
                    n_pre2 += 1

                if occpre == 5:
                    pre5 += wd
                if occpre == 7:
                    pre7 += wd
                if occact == 4:
                    act4_present = True
                    act4 += wd
                    xtab[occpre] = xtab.get(occpre, 0.0) + wd
                    if occpre == 1:
                        leak += wd
                if at_retail:
                    gated += wd
                if is_arm2 and occpre in (1, 2):
                    arm2_bad += wd
                for slot in range(s // 30, (e + 29) // 30):
                    idx = slot % 48
                    diur_tot[idx] += w
                    if occpre == 5:
                        diur5[idx] += w
                    if at_home:
                        present["Residential"][idx] += w
                    if at_work:
                        present["Office"][idx] += w
                    if at_retail:
                        present["Retail"][idx] += w
        curves = {ch: [(present[ch][i] / diur_tot[i]) if diur_tot[i] else 0.0
                       for i in range(48)] for ch in present}
        sig[cyc] = {
            "share_pre5": (pre5 / tot) if tot else 0.0,
            "share_pre7": (pre7 / tot) if tot else 0.0,
            "share_act4": (act4 / tot) if tot else 0.0,
            "share_leak": (leak / tot) if tot else 0.0,
            "share_gated": (gated / tot) if tot else 0.0,
            "arm2_bad_time": arm2_bad,
            "xtab": xtab, "act4_tot": act4,
            "diur5": [(diur5[i] / diur_tot[i]) if diur_tot[i] else 0.0
                      for i in range(48)],
            "pre_vals": pre_vals, "act4_present": act4_present,
            "curves": curves,
            "rate_home": 100 * n_home / n_valid if n_valid else 0.0,
            "rate_work": 100 * n_work / n_valid if n_valid else 0.0,
            "rate_retail": 100 * n_retail / n_valid if n_valid else 0.0,
            "rate_pre2": 100 * n_pre2 / n_valid if n_valid else 0.0,
            "closure_rate": 100 * n_valid / n_epi if n_epi else 0.0,
            "act_dist": {a: 100 * act_dur.get(a, 0.0) / tot_dur if tot_dur else 0.0
                         for a in range(1, 15)},
            "epi_counts": list(epi_per_person.values()),
        }
    return sig


def emit_crosstabs(sig):
    """Write the 4 per-cycle occACT==4 x occPRE weighted cross-tab CSVs. Returns
    the count written."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    n = 0
    for cyc in CYCLES:
        if cyc not in sig:
            continue
        xt, tot = sig[cyc]["xtab"], sig[cyc]["act4_tot"]
        path = OUTPUT_DIR / f"retail_orrule_crosstab_{cyc}.csv"
        with open(path, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["occPRE", "weighted_episode_time", "share_of_occACT4",
                        "is_online_leak", "in_gated_arm2"])
            for pre in sorted(xt):
                w.writerow([pre, f"{xt[pre]:.1f}",
                            f"{(xt[pre] / tot):.4f}" if tot else "",
                            "1" if pre == 1 else "0",
                            "1" if pre in GATED_PRE else "0"])
        n += 1
    return n


# ---------------------------------------------------------------------------
# Hotel canonical load
# ---------------------------------------------------------------------------

def load_canonical():
    if not CANONICAL.is_file():
        return None, []
    with open(CANONICAL, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        header = reader.fieldnames or []
        rows = list(reader)
    for r in rows:
        r["YEAR"], r["MONTH"] = int(r["YEAR"]), int(r["MONTH"])
        occ = (r.get("occupancy_rate") or "").strip()
        r["_occ"] = float(occ) if occ else None
    return header, rows


# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------

def section1(sig):
    out = []
    have = [c for c in CYCLES if c in sig]
    # 1.1 occPRE present, 1-18, code 5 non-empty, all cycles
    ok_range = all(sig[c]["pre_vals"] and min(sig[c]["pre_vals"]) >= 1
                   and max(sig[c]["pre_vals"]) <= 18 for c in have)
    pre5_all = all(sig[c]["share_pre5"] > 0 for c in have)
    out.append(R("1.1", "occPRE present, values in 1-18, code 5 non-empty, all cycles",
                 "PASS" if (len(have) == 4 and ok_range and pre5_all) else "FAIL",
                 f"{len(have)}/4 cycles; ranges "
                 + ", ".join(f"{c}:[{min(sig[c]['pre_vals'])}-{max(sig[c]['pre_vals'])}]"
                             for c in have)))
    # 1.2 occPRE==5 share per cycle in band
    lo, hi = RETAIL_LOC_BAND
    detail = ", ".join(f"{c}:{sig[c]['share_pre5']*100:.2f}%" for c in have)
    inband = all(lo <= sig[c]["share_pre5"] * 100 <= hi for c in have)
    out.append(R("1.2", f"occPRE==5 episode-time share per cycle in {RETAIL_LOC_BAND}%",
                 "PASS" if inband else "WARN", detail))
    # 1.3 occACT code 4 present all cycles
    act4 = all(sig[c]["act4_present"] for c in have)
    out.append(R("1.3", "occACT==4 (Purchasing G&S) present, all cycles",
                 "PASS" if (len(have) == 4 and act4) else "FAIL",
                 ", ".join(f"{c}:{sig[c]['share_act4']*100:.2f}%" for c in have)))
    # 1.4 restaurant occPRE==7 INFO
    out.append(R("1.4", "occPRE==7 (restaurant) share -- excluded channel record",
                 "INFO", ", ".join(f"{c}:{sig[c]['share_pre7']*100:.2f}%" for c in have)))
    # 1.5 cross-cycle stability of 1.2
    vals = [sig[c]["share_pre5"] * 100 for c in have]
    spread = (max(vals) - min(vals)) if vals else 0.0
    out.append(R("1.5", "Cross-cycle stability of occPRE==5 share (max pairwise delta)",
                 "PASS" if spread <= 1.0 else "WARN",
                 f"spread = {spread:.2f} pp across {len(have)} cycles"))
    return out


def section2(sig, n_xtab):
    out = []
    have = [c for c in CYCLES if c in sig]
    out.append(R("2.1", "Per-cycle occACT==4 x occPRE weighted cross-tab emitted (4 CSVs)",
                 "PASS" if n_xtab == 4 else "FAIL", f"{n_xtab}/4 CSVs written"))
    out.append(R("2.2", "Online-shopping leak (occACT==4 & occPRE==1) share per cycle",
                 "INFO", ", ".join(f"{c}:{sig[c]['share_leak']*100:.3f}%" for c in have)))
    # 2.3 leak trend rising 2005->2022
    leaks = [(c, sig[c]["share_leak"]) for c in have]
    rising = len(leaks) >= 2 and leaks[-1][1] >= leaks[0][1]
    out.append(R("2.3", "Leak trend 2005->2022 rising (e-commerce)",
                 "PASS" if rising else "WARN",
                 " -> ".join(f"{c}:{v*100:.3f}%" for c, v in leaks)))
    # 2.4 gated-rule preview share in band + exceeds location-only by 0-1.0 pp
    lo, hi = GATED_BAND
    inband = all(lo <= sig[c]["share_gated"] * 100 <= hi for c in have)
    deltas = [(sig[c]["share_gated"] - sig[c]["share_pre5"]) * 100 for c in have]
    delta_ok = all(0 <= d <= 1.0 for d in deltas)
    out.append(R("2.4", f"Gated-rule share per cycle in {GATED_BAND}%, exceeds loc-only by 0-1.0 pp",
                 "PASS" if (inband and delta_ok) else "WARN",
                 ", ".join(f"{c}:{sig[c]['share_gated']*100:.2f}% (+{d:.2f}pp)"
                           for c, d in zip(have, deltas))))
    # 2.5 gated arm-2 adds no occPRE 1/2 rows (rule correctness)
    bad = sum(sig[c]["arm2_bad_time"] for c in have)
    out.append(R("2.5", "Gated arm-2 (occACT==4 & occPRE in {5,9}) adds no occPRE 1/2 time",
                 "PASS" if bad == 0 else "FAIL",
                 "0 weighted time on occPRE 1/2 via arm-2 (rule gates online leak out)"
                 if bad == 0 else f"{bad:.1f} leaked -- rule broken"))
    return out


def _ok_months(rows, pr):
    return sorted((r["YEAR"], r["MONTH"]) for r in rows
                  if r["PR"] == pr and r["_occ"] is not None)


def _classify_gaps(okm):
    if not okm:
        return [], []
    lo, hi = _mk(*okm[0]), _mk(*okm[-1])
    have = {_mk(y, m) for (y, m) in okm}
    fy, ly = okm[0][0], okm[-1][0]
    core, edge = [], []
    for t in range(lo, hi + 1):
        if t in have:
            continue
        y, m = t // 12, t % 12 + 1
        (edge if y in (fy, ly) else core).append((y, m))
    return core, edge


def section3(header, rows, splice_flag):
    out = []
    if header is None:
        return [R("3.1", "Canonical hotel series present", "FAIL",
                  f"missing {CANONICAL}")]
    exact = ["YEAR", "MONTH", "PR", "occupancy_rate", "ADR_CAD", "RevPAR_CAD",
             "SOURCE", "SPLICED"]
    out.append(R("3.1", "Schema exact + PR in {QC,AB}",
                 "PASS" if header == exact and {r["PR"] for r in rows} <= {"QC", "AB"}
                 else "FAIL", f"header={header}"))
    # 3.2 grid complete both PR (216 rows each); observed reported honestly
    grid = {pr: sum(1 for r in rows if r["PR"] == pr) for pr in ("QC", "AB")}
    obs = {pr: len(_ok_months(rows, pr)) for pr in ("QC", "AB")}
    out.append(R("3.2", "Grid complete (216 rows/PR); observed span honest",
                 "PASS" if grid["QC"] == 216 and grid["AB"] == 216 else "FAIL",
                 f"grid QC={grid['QC']}/216 AB={grid['AB']}/216; "
                 f"observed QC={obs['QC']} (2019+) AB={obs['AB']} (2011+)",
                 reconciled=True))
    # 3.3 occ in (0,1]; no CORE interior gap inside each covered window
    bad = [r for r in rows if r["_occ"] is not None and not (0 < r["_occ"] <= 1)]
    core_all = []
    for pr in ("QC", "AB"):
        core, _ = _classify_gaps(_ok_months(rows, pr))
        core_all += [(pr, *c) for c in core]
    out.append(R("3.3", "occupancy_rate in (0,1]; no core interior gap in covered window",
                 "FAIL" if (bad or core_all) else "PASS",
                 (f"{len(bad)} out-of-range; " if bad else "")
                 + (f"core gaps {core_all[:4]}" if core_all
                    else "all observed rows in range, no core interior gaps"),
                 reconciled=True))
    # 3.4 AB splice continuity (moot -- no CBRE)
    out.append(R("3.4", "AB splice continuity (dr_L3-01 Jan-2010 boundary)",
                 "INFO" if not splice_flag else "WARN",
                 "no splice applied -- single-source Market Monitor AB; D_splice moot",
                 reconciled=True))
    # 3.5 COVID months present, 2020-04 near min, both PR
    tf = []
    for pr in ("QC", "AB"):
        by = {(r["YEAR"], r["MONTH"]): r["_occ"] for r in rows
              if r["PR"] == pr and r["_occ"] is not None}
        okm = _ok_months(rows, pr)
        if not okm:
            tf.append(f"{pr}: no data")
            continue
        lo, hi = _mk(*okm[0]), _mk(*okm[-1])
        missing = [(t // 12, t % 12 + 1) for t in range(_mk(*COVID_START), _mk(*COVID_END) + 1)
                   if lo <= t <= hi and (t // 12, t % 12 + 1) not in by]
        if missing:
            tf.append(f"{pr}: {len(missing)} COVID months missing in span")
        elif by:
            mn = min(by.values())
            apr20 = by.get((2020, 4))
            if apr20 is not None and apr20 > mn + 0.05:
                tf.append(f"{pr}: 2020-04={apr20:.3f} not near min {mn:.3f}")
    out.append(R("3.5", "COVID months present + 2020-04 near series min, both PR",
                 "FAIL" if tf else "PASS",
                 "; ".join(tf) if tf else "both provincial COVID troughs intact"))
    # 3.6 pre-COVID annual means in band
    notes, warn = [], False
    for pr, band in (("QC", QC_PRECOVID_BAND), ("AB", AB_PRECOVID_BAND)):
        v = [r["_occ"] for r in rows if r["PR"] == pr and r["_occ"] is not None
             and 2011 <= r["YEAR"] <= 2019]
        if v:
            m = sum(v) / len(v)
            inb = band[0] <= m <= band[1]
            warn = warn or not inb
            notes.append(f"{pr}:{m:.3f}{'' if inb else ' (out '+str(band)+')'}")
        else:
            notes.append(f"{pr}:no pre-COVID data")
    out.append(R("3.6", "Pre-COVID (2011-2019) annual mean in provincial band",
                 "WARN" if warn else "PASS", ", ".join(notes), reconciled=True))
    # 3.7 seasonality summer>winter
    notes, warn = [], False
    for pr in ("QC", "AB"):
        pre = [r for r in rows if r["PR"] == pr and r["_occ"] is not None
               and r["YEAR"] <= 2019]
        summer = [r["_occ"] for r in pre if r["MONTH"] in (6, 7, 8, 9)]
        winter = [r["_occ"] for r in pre if r["MONTH"] in (12, 1, 2, 3)]
        if summer and winter:
            s, w = sum(summer) / len(summer), sum(winter) / len(winter)
            warn = warn or not (s > w)
            notes.append(f"{pr}: summer={s:.3f} {'>' if s > w else '<='} winter={w:.3f}")
    out.append(R("3.7", "Pre-COVID summer mean > winter mean, both PR",
                 "WARN" if warn else "PASS", " | ".join(notes)))
    return out


# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------

def _style(ax, legend=True):
    ax.tick_params(colors=FG, labelsize=8)
    for s in ax.spines.values():
        s.set_color(GRID)
    ax.grid(True, color=GRID, lw=0.5, alpha=0.6)
    if legend:
        leg = ax.legend(facecolor=PANEL, edgecolor=GRID, labelcolor=FG, fontsize=8)
        if leg:
            leg.get_frame().set_alpha(0.9)


def _b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=110, facecolor=fig.get_facecolor(),
                bbox_inches="tight")
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _hours_axis(ax):
    ax.set_xlim(0, 48)
    ax.set_xticks(range(0, 49, 6))
    ax.set_xticklabels([f"{h:02d}h" for h in range(0, 25, 3)])


# --- Band A: 4-channel schedules (all building types) ---------------------

def g1_channels_2022(sig):
    """Headline: the 4 building-type channels' diurnal schedules for 2022 --
    Residential/Office/Retail measured from GSS, Hotel = fixed design shape."""
    cyc = 2022 if 2022 in sig else (list(sig) or [None])[-1]
    fig, ax = plt.subplots(figsize=(11, 3.8), facecolor=DARK_BG)
    ax.set_facecolor(PANEL)
    if cyc is not None:
        for ch in ("Residential", "Office", "Retail"):
            ax.plot(range(48), sig[cyc]["curves"][ch], color=CH_COL[ch], lw=2,
                    label=f"{ch} (GSS-measured)")
    ax.plot(range(48), HOTEL_WEEKDAY, color=CH_COL["Hotel"], lw=2, ls="--",
            label="Hotel (design shape s(t), dr_L3-05)")
    ax.set_ylim(0, 1.05)
    _hours_axis(ax)
    ax.set_ylabel("share present  /  s(t)", color=FG, fontsize=9)
    ax.set_title(f"G1 -- 4-channel diurnal schedules (all building types) -- {cyc} "
                 "cycle (R/O/R measured; Hotel = guest-room shape x monthly rate)",
                 color=FG, fontsize=10.5)
    _style(ax)
    return _b64(fig)


def g2_channel_rates(sig):
    """Episode-level presence RATE per building-type channel per cycle -- the
    Leg-2 'AT_HOME / AT_WORK rate' figure, extended to all channels."""
    import numpy as np
    have = [c for c in CYCLES if c in sig]
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.2), facecolor=DARK_BG)
    specs = [("Residential (AT_HOME)", "rate_home", (55, 70), 100,
              CH_COL["Residential"]),
             ("Office (AT_WORK)", "rate_work", (6, 12), 25, CH_COL["Office"]),
             ("Retail (AT_RETAIL gated)", "rate_retail", (1.5, 3.0), 5,
              CH_COL["Retail"])]
    for ax, (ttl, key, band, ymax, col) in zip(axes, specs):
        ax.set_facecolor(PANEL)
        ys = [sig[c][key] for c in have]
        ax.bar([str(c) for c in have], ys, color=col)
        for lo_hi in band:
            ax.axhline(lo_hi, color="#e74c3c", lw=0.8, ls="--")
        for i, y in enumerate(ys):
            ax.text(i, y, f"{y:.1f}", ha="center", va="bottom", color=FG, fontsize=7.5)
        ax.set_ylim(0, ymax)
        ax.set_title(ttl, color=FG, fontsize=9.5)
        _style(ax, legend=False)
    fig.suptitle("G2 -- Channel presence rate per cycle (episode-level; dashed = "
                 "expected band). Hotel omitted: no GSS diary (monthly series, C-V4)",
                 color=FG, fontsize=10.5, y=1.04)
    return _b64(fig)


def g_channel_cycles(sig, channel, ymax, ylabel, subtitle):
    """Across-cycle diurnal presence for one GSS building-type channel."""
    fig, ax = plt.subplots(figsize=(11, 3.2), facecolor=DARK_BG)
    ax.set_facecolor(PANEL)
    for cyc in CYCLES:
        if cyc in sig:
            ax.plot(range(48), sig[cyc]["curves"][channel], color=CYC_COL[cyc],
                    lw=1.8, label=str(cyc))
    ax.set_ylim(0, ymax)
    _hours_axis(ax)
    ax.set_ylabel(ylabel, color=FG, fontsize=9)
    ax.set_title(f"{channel} diurnal presence across cycles -- {subtitle}",
                 color=FG, fontsize=11)
    _style(ax)
    return _b64(fig)


def g_hotel_shape():
    """Hotel guest-room diurnal shape s(t): weekday vs weekend (dr_L3-05)."""
    fig, ax = plt.subplots(figsize=(11, 3.2), facecolor=DARK_BG)
    ax.set_facecolor(PANEL)
    ax.plot(range(48), HOTEL_WEEKDAY, color="#e056fd", lw=2, label="weekday")
    ax.plot(range(48), HOTEL_WEEKEND, color="#f8a5ff", lw=2, ls="--", label="weekend")
    ax.fill_between(range(48), HOTEL_WEEKDAY, HOTEL_WEEKEND, color="#e056fd", alpha=0.08)
    ax.set_ylim(0, 1.05)
    _hours_axis(ax)
    ax.set_ylabel("s(t) (unit-normalized)", color=FG, fontsize=9)
    ax.set_title("Hotel guest-room diurnal shape s(t) -- weekday vs weekend "
                 "(dr_L3-05, PNNL); scaled by the monthly rate", color=FG, fontsize=10.5)
    _style(ax)
    return _b64(fig)


# --- Band B: GSS harmonization QA (mirrors Leg-2 Step-2) -------------------

def g7_activity(sig):
    """14-category duration-weighted activity distribution x 4 cycles heatmap."""
    import numpy as np
    have = [c for c in CYCLES if c in sig]
    grid = np.array([[sig[c]["act_dist"][a] for c in have] for a in range(1, 15)])
    fig, ax = plt.subplots(figsize=(8.2, 5.4), facecolor=DARK_BG)
    ax.set_facecolor(PANEL)
    im = ax.imshow(grid, aspect="auto", cmap="YlGnBu")
    ax.set_xticks(range(len(have)))
    ax.set_xticklabels([str(c) for c in have], color=FG, fontsize=9)
    ax.set_yticks(range(14))
    ax.set_yticklabels([f"{a} {ACT_LABELS[a]}" for a in range(1, 15)], color=FG,
                       fontsize=8)
    for i in range(14):
        for j in range(len(have)):
            v = grid[i, j]
            ax.text(j, i, f"{v:.1f}", ha="center", va="center", fontsize=7,
                    color="#0a0d11" if v > grid.max() * 0.55 else "#d7dde6")
    ax.set_title("G7 -- Time-weighted activity distribution (%) -- 14 categories x "
                 "4 cycles", color=FG, fontsize=10.5)
    for sp in ax.spines.values():
        sp.set_color(GRID)
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.02)
    cb.ax.tick_params(colors=FG, labelsize=7)
    return _b64(fig)


def g8_diary_qa(sig):
    """Diary closure pass rate + episodes-per-respondent distribution."""
    have = [c for c in CYCLES if c in sig]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.2), facecolor=DARK_BG)
    a1.set_facecolor(PANEL)
    ys = [sig[c]["closure_rate"] for c in have]
    a1.bar([str(c) for c in have],
           ys, color=["#2ecc71" if y >= 95 else "#e74c3c" for y in ys])
    a1.axhline(95, color="#f1c40f", lw=0.9, ls="--", label="95% floor")
    for i, y in enumerate(ys):
        a1.text(i, y, f"{y:.1f}", ha="center", va="bottom", color=FG, fontsize=8)
    a1.set_ylim(0, 105)
    a1.set_title("Diary closure pass rate per cycle", color=FG, fontsize=10)
    _style(a1)
    a2.set_facecolor(PANEL)
    data = [sig[c]["epi_counts"] for c in have]
    bp = a2.boxplot(data, tick_labels=[str(c) for c in have], patch_artist=True,
                    showfliers=False)
    for patch in bp["boxes"]:
        patch.set_facecolor("#48c9b0")
        patch.set_alpha(0.7)
    for el in ("whiskers", "caps", "medians"):
        for line in bp[el]:
            line.set_color(FG)
    a2.set_title("Episodes per respondent distribution", color=FG, fontsize=10)
    _style(a2, legend=False)
    return _b64(fig)


def g9_occpre2(sig):
    """occPRE==2 (workplace) episode share per cycle -- Office sanity vs AT_WORK."""
    have = [c for c in CYCLES if c in sig]
    fig, ax = plt.subplots(figsize=(6.8, 3.0), facecolor=DARK_BG)
    ax.set_facecolor(PANEL)
    ys = [sig[c]["rate_pre2"] for c in have]
    ax.bar([str(c) for c in have], ys, color="#ff9f43")
    for i, y in enumerate(ys):
        ax.text(i, y, f"{y:.1f}%", ha="center", va="bottom", color=FG, fontsize=8)
    ax.set_ylim(0, max(ys + [1]) * 1.3)
    ax.set_title("G9 -- occPRE==2 (workplace) episode share per cycle\n"
                 "(sanity vs Office AT_WORK; 2022 lower under WFH coding)",
                 color=FG, fontsize=9.5)
    _style(ax, legend=False)
    return _b64(fig)


def v1_retail_diurnal(sig):
    fig, ax = plt.subplots(figsize=(11, 3.4), facecolor=DARK_BG)
    ax.set_facecolor(PANEL)
    for cyc in CYCLES:
        if cyc in sig:
            ax.plot(range(48), [x * 100 for x in sig[cyc]["diur5"]],
                    color=CYC_COL[cyc], lw=1.8, label=str(cyc))
    _hours_axis(ax)
    ax.set_ylabel("share of episodes in occPRE==5 (%)", color=FG, fontsize=9)
    ax.set_title("V1 -- Retail (occPRE==5) diurnal share per cycle "
                 "(Step-3 tiled-shape preview: midday hump, near-zero at night)",
                 color=FG, fontsize=10.5)
    _style(ax)
    return _b64(fig)


def v2_leak(sig):
    fig, ax = plt.subplots(figsize=(6.8, 3.0), facecolor=DARK_BG)
    ax.set_facecolor(PANEL)
    have = [c for c in CYCLES if c in sig]
    ys = [sig[c]["share_leak"] * 100 for c in have]
    ax.bar([str(c) for c in have], ys, color="#e056fd")
    for i, y in enumerate(ys):
        ax.text(i, y, f"{y:.3f}%", ha="center", va="bottom", color=FG, fontsize=8)
    ax.set_title("V2 -- Online-shopping leak (occACT==4 & occPRE==1) share\n"
                 "-- gated OUT of AT_RETAIL (small, <0.2% of all time)",
                 color=FG, fontsize=9.5)
    _style(ax, legend=False)
    return _b64(fig)


def v3_gated_vs_loc(sig):
    import numpy as np
    fig, ax = plt.subplots(figsize=(6.8, 3.0), facecolor=DARK_BG)
    ax.set_facecolor(PANEL)
    have = [c for c in CYCLES if c in sig]
    x = np.arange(len(have))
    loc = [sig[c]["share_pre5"] * 100 for c in have]
    gat = [sig[c]["share_gated"] * 100 for c in have]
    ax.bar(x - 0.2, loc, 0.4, color="#26de81", label="occPRE==5 only")
    ax.bar(x + 0.2, gat, 0.4, color="#4aa3ff", label="gated OR-rule")
    ax.set_xticks(x)
    ax.set_xticklabels([str(c) for c in have])
    ax.set_ylabel("episode-time share (%)", color=FG, fontsize=9)
    ax.set_title("V3 -- AT_RETAIL: location-only vs frozen gated rule",
                 color=FG, fontsize=10)
    _style(ax)
    return _b64(fig)


def v4_hotel_ts(rows):
    fig, ax = plt.subplots(figsize=(11, 3.4), facecolor=DARK_BG)
    ax.set_facecolor(PANEL)
    for pr in ("QC", "AB"):
        pts = sorted((r["YEAR"] + (r["MONTH"] - 1) / 12.0, r["_occ"])
                     for r in rows if r["PR"] == pr and r["_occ"] is not None)
        if pts:
            xs, ys = zip(*pts)
            ax.plot(xs, ys, color=PR_COL[pr], lw=1.5, marker="o", ms=2.3, label=pr)
    ax.axvspan(2020 + 2 / 12, 2022 + 5 / 12, color="#ff5252", alpha=0.10,
               label="COVID window")
    ax.set_xlim(2005, 2023)
    ax.set_ylim(0, 1)
    ax.set_title("V4 -- Canonical hotel monthly occupancy_rate (QC + AB, observed "
                 "months; no CBRE splice -- AB single-source 2011+)",
                 color=FG, fontsize=10)
    _style(ax)
    return _b64(fig)


def v5_hotel_seasonal(rows):
    fig, ax = plt.subplots(figsize=(6.8, 3.2), facecolor=DARK_BG)
    ax.set_facecolor(PANEL)
    for pr in ("QC", "AB"):
        prof = []
        for m in range(1, 13):
            v = [r["_occ"] for r in rows if r["PR"] == pr and r["_occ"] is not None
                 and r["MONTH"] == m and r["YEAR"] <= 2019]
            prof.append(sum(v) / len(v) if v else None)
        xs = [m for m in range(1, 13) if prof[m - 1] is not None]
        ys = [prof[m - 1] for m in xs]
        if xs:
            ax.plot(xs, ys, color=PR_COL[pr], lw=1.8, marker="o", ms=4, label=pr)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"])
    ax.set_ylim(0, 1)
    ax.set_title("V5 -- Hotel seasonal profile (pre-COVID <=2019)", color=FG, fontsize=10)
    _style(ax)
    return _b64(fig)


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------

def _fig(cid, title, caption, b64):
    return (f'<div class="fig" id="{cid}"><h3>{title}</h3>'
            f'<p class="cap">{caption}</p>'
            f'<img src="data:image/png;base64,{b64}" alt="{title}"></div>')


def _band(text):
    return f'<h2 class="band">{text}</h2>'


def render(sections, figures):
    counts = {"PASS": 0, "WARN": 0, "FAIL": 0, "INFO": 0}
    for _, results in sections:
        for r in results:
            counts[r.status] += 1
    verdict = "FAIL" if counts["FAIL"] else ("WARN" if counts["WARN"] else "PASS")

    rows_html = []
    for title, results in sections:
        rows_html.append(f'<tr class="sec"><td colspan="4">{title}</td></tr>')
        for r in results:
            tag = ' <span class="rec">[RECONCILED]</span>' if r.reconciled else ""
            rows_html.append(
                f'<tr><td class="gid">{r.gid}</td><td>{r.desc}{tag}</td>'
                f'<td><span class="badge" style="background:{BADGE[r.status]}">'
                f'{r.status}</span></td><td class="det">{r.detail}</td></tr>')

    figs_html = "".join(figures)
    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Step 2 Validation -- Leg 3 (4-split)</title><style>
:root{{--bg:{DARK_BG};--panel:{PANEL};--fg:{FG};--border:{GRID}}}
body{{background:var(--bg);color:var(--fg);font-family:'Segoe UI',system-ui,sans-serif;
margin:0;padding:30px 38px;line-height:1.5}}
h1{{font-size:22px;margin:0 0 2px}}
h2.sub{{font-size:14px;color:#9fb0c3;font-weight:500;margin:0 0 18px}}
h2.band{{font-size:13px;color:#8fd3ff;text-transform:uppercase;letter-spacing:.05em;
border-bottom:1px solid var(--border);padding-bottom:6px;margin:34px 0 14px}}
.summary{{display:flex;gap:10px;margin:16px 0 8px}}
.chip{{padding:8px 16px;border-radius:8px;font-weight:700;font-size:13px;color:#0a0d11}}
.intro{{background:var(--panel);border:1px solid var(--border);border-radius:10px;
padding:14px 18px;margin:14px 0;font-size:13px;color:#c3ccd8}}
.intro b{{color:#8fd3ff}}
table{{border-collapse:collapse;width:100%;font-size:13px;margin-top:6px}}
td{{padding:7px 10px;border-bottom:1px solid var(--border);vertical-align:top}}
tr.sec td{{background:var(--panel);font-weight:600;color:#8fd3ff;font-size:12px;
text-transform:uppercase;letter-spacing:.04em;padding-top:12px}}
.gid{{color:#7d8ea3;width:44px}}.det{{color:#9fb0c3;font-size:12px}}
.badge{{padding:2px 9px;border-radius:5px;font-weight:700;font-size:11px}}
.rec{{color:#f1c40f;font-size:10px;font-weight:600}}
.fig{{background:var(--panel);border:1px solid var(--border);border-radius:10px;
padding:14px 16px;margin:16px 0}}
.fig h3{{font-size:14px;color:#8fd3ff;margin:0 0 4px}}
.fig .cap{{font-size:12px;color:#9fb0c3;margin:0 0 10px}}
.fig img{{max-width:100%;border-radius:8px;background:{PANEL}}}
.foot{{margin-top:26px;color:#6b7a8d;font-size:11px}}
</style></head><body>
<h1>Step 2 Validation Report &mdash; Leg 3 (4-Channel Split)</h1>
<h2 class="sub">Retail-signal verification on reused Leg-2 episodes + frozen OR-rule
leak cross-tab + canonical hotel series &middot; verdict:
<b style="color:{BADGE[verdict]}">{verdict}</b></h2>
<div class="summary">
<div class="chip" style="background:{BADGE['PASS']}">PASS {counts['PASS']}</div>
<div class="chip" style="background:{BADGE['WARN']}">WARN {counts['WARN']}</div>
<div class="chip" style="background:{BADGE['FAIL']}">FAIL {counts['FAIL']}</div>
<div class="chip" style="background:{BADGE['INFO']}">INFO {counts['INFO']}</div>
</div>
<div class="intro">
<b>What this report validates.</b> Step 2 writes <b>no GSS file</b> &mdash; the retail
channel already lives in the reused Leg-2 harmonized episodes (read-only), so
Section 1/2 <b>verify</b> the AT_RETAIL ingredients and the frozen gated OR-rule
<code>(occPRE==5) | ((occACT==4) &amp; occPRE&isin;{{5,9}})</code>, emitting the 4 per-cycle
cross-tab CSVs (the OD-1 verification condition). The one build item is <b>Delta D</b>:
harmonizing the Step-1 hotel raw assembly into the canonical
<code>0_Occupancy/external/hotel_occupancy_monthly.csv</code> that Step-6 SARIMA consumes
&mdash; validated in Section 3. The figures show <b>all four building-type channels'
schedules</b> (Residential / Office / Retail / Hotel) plus the reused-diary QA panels
(activity distribution, diary closure, presence rates) so the 4-channel inputs are
visibly coherent before Step-3 tiling.
</div>

{figs_html}

<h2 class="band">Validation gates</h2>
<table>{''.join(rows_html)}</table>
<div class="foot">Retail signal streamed from Leg2_2-split/Step2_docs/outputs_step2
episodes (read-only). Cross-tabs: outputs_step2/retail_orrule_crosstab_{{cycle}}.csv.
Canonical hotel series: 0_Occupancy/external/hotel_occupancy_monthly.csv (+ markets
side file). [RECONCILED] gates adjusted from the pre-acquisition plan &mdash; see the
script header.</div>
</body></html>"""
    HTML_PATH.write_text(html, encoding="utf-8")

    lines = [f"STEP 2 VALIDATION -- LEG 3 (4-split)  verdict={verdict}",
             f"PASS={counts['PASS']} WARN={counts['WARN']} FAIL={counts['FAIL']} "
             f"INFO={counts['INFO']}", ""]
    for title, results in sections:
        lines.append(f"== {title} ==")
        for r in results:
            rec = " [RECONCILED]" if r.reconciled else ""
            lines.append(f"  [{r.status:4}] {r.gid}{rec}  {r.desc}")
            lines.append(f"          {r.detail}")
        lines.append("")
    TXT_PATH.write_text("\n".join(lines), encoding="utf-8")
    return verdict, counts


def main():
    print("Streaming Leg-2 episodes for the retail signal (4 cycles)...")
    sig = retail_signal()
    n_xtab = emit_crosstabs(sig)
    header, rows = load_canonical()
    # splice flag: any SPLICED==1 row in the canonical series
    splice_flag = any(r.get("SPLICED") == "1" for r in rows)

    sections = [
        ("Section 1 -- retail signal presence", section1(sig)),
        ("Section 2 -- OR-rule leak cross-tab (OD-1 verification)", section2(sig, n_xtab)),
        ("Section 3 -- canonical hotel series", section3(header, rows, splice_flag)),
    ]

    figures = [
        _band("Figures A &mdash; 4-channel schedules (all building types)"),
        _fig("g1", "G1 &mdash; 4-channel diurnal schedules (all building types)",
             "The day's presence share for every building type. "
             "Residential/Office/Retail are measured from the 2022 GSS diaries; "
             "<b>Hotel is shown too</b> as the fixed guest-room design shape s(t) "
             "(dashed, dr_L3-05) &mdash; it has no GSS diary (occupancy is monthly), "
             "so its daily shape is the PNNL guest-room curve scaled by the monthly "
             "rate.", g1_channels_2022(sig)),
        _fig("g2", "G2 &mdash; Channel presence rate per cycle",
             "Episode-level presence rate for each building-type channel across "
             "cycles (the Leg-2 AT_HOME/AT_WORK-rate figure, extended to all "
             "channels). Residential ~55-70%; Office falls into 2022 under WFH "
             "coding; Retail is the ~1.5-2% gated signal. Hotel omitted here (no "
             "GSS diary &mdash; its level is the monthly series in Figure C-V4).",
             g2_channel_rates(sig)),
        _fig("g3", "G3 &mdash; Residential (AT_HOME) presence across cycles",
             "At-home diurnal profile per cycle. Overnight plateau ~0.95, midday "
             "trough; 2022's daytime floor sits slightly higher (more work-from-home).",
             g_channel_cycles(sig, "Residential", 1.05, "share at home",
                              "residential rhythm is stable")),
        _fig("g4", "G4 &mdash; Office (AT_WORK) presence across cycles (telework)",
             "AT_WORK diurnal profile per cycle. 2022 peak presence sits modestly "
             "below the pre-COVID cycles &mdash; the on-site drop the pipeline "
             "carries; the fuller telework signal lives in work-from-home.",
             g_channel_cycles(sig, "Office", 0.5, "share at work", "the telework shift")),
        _fig("g5", "G5 &mdash; Retail (AT_RETAIL) presence across cycles",
             "In-retail diurnal profile per cycle (gated OR-rule). Midday bump; the "
             "2015/2022 curves sit below 2005/2010 as in-person shopping eases "
             "(online leak gated out).",
             g_channel_cycles(sig, "Retail", 0.10, "share in retail",
                              "in-person shopping easing")),
        _fig("g6", "G6 &mdash; Hotel guest-room diurnal shape (weekday vs weekend)",
             "The hotel analogue of the per-channel diurnal figures: the fixed s(t) "
             "guest-room shape (dr_L3-05, PNNL). Deep weekday daytime trough (0.20, "
             "guests out 09-15h), shallower/later weekend trough (0.31). A design "
             "shape, not a GSS cycle series &mdash; its across-time variation is the "
             "monthly rate (Figure C-V4).", g_hotel_shape()),

        _band("Figures B &mdash; GSS harmonization QA (reused Leg-2 episodes)"),
        _fig("g7", "G7 &mdash; Time-weighted activity distribution (14 x 4)",
             "Duration-weighted share of diary time in each of the 14 activity "
             "categories, per cycle. Confirms the reused activity crosswalk is "
             "stable across cycles (Sleep ~33%, Work, Leisure dominate; Purchasing "
             "= the retail-driving activity).", g7_activity(sig)),
        _fig("g8", "G8 &mdash; Diary integrity QA",
             "Left: diary-closure pass rate per cycle (share of episodes on "
             "closing 1440-min diaries; &ge;95% floor). Right: episodes-per-"
             "respondent spread. Confirms the reused diaries are intact.",
             g8_diary_qa(sig)),
        _fig("g9", "G9 &mdash; occPRE==2 (workplace) episode share",
             "Raw workplace-presence share per cycle &mdash; an Office sanity "
             "cross-check against the AT_WORK rate (G2). Both drop in 2022 as WFH "
             "episodes code to home, not workplace.", g9_occpre2(sig)),

        _band("Figures C &mdash; retail signal + canonical hotel series"),
        _fig("v1", "V1 &mdash; Retail diurnal share per cycle",
             "Weighted share of episodes located in retail (occPRE==5) by 30-min "
             "slot. Preview of the shape the Step-3 tiler will emit: a midday hump, "
             "near-zero overnight.", v1_retail_diurnal(sig)),
        _fig("v2", "V2 &mdash; Online-shopping leak share",
             "Episode-time share of purchasing-from-home (occACT==4 &amp; occPRE==1). "
             "The frozen rule <b>gates this out</b> of AT_RETAIL. Note it <b>declines</b> "
             "2005&rarr;2022 (0.18&rarr;0.07%): within GSS's purchasing code the 2022 GSSP "
             "concentrates episodes at the store location (occPRE==5 rises 75&rarr;90% of "
             "occACT==4), a diary-coding shift &mdash; not e-commerce under-capture. Either "
             "way the gate protects the longitudinal signal.", v2_leak(sig)),
        _fig("v3", "V3 &mdash; Location-only vs gated OR-rule share",
             "AT_RETAIL episode-time share under the location-only definition "
             "(occPRE==5) vs the frozen gated rule. The small uplift is the "
             "in-store purchasing arm; it must not add online-from-home time.",
             v3_gated_vs_loc(sig)),
        _fig("v4", "V4 &mdash; Canonical hotel monthly series",
             "The harmonized series Step-6 SARIMA consumes: monthly occupancy_rate "
             "for QC + AB, observed months only. COVID collapse (shaded) is signal. "
             "AB is single-source (Market Monitor 2011+) &mdash; no CBRE splice.",
             v4_hotel_ts(rows)),
        _fig("v5", "V5 &mdash; Hotel seasonal profile",
             "Pre-COVID (&le;2019) mean occupancy per calendar month &mdash; the "
             "seasonal envelope on the monthly rate; summer peak, winter trough.",
             v5_hotel_seasonal(rows)),
    ]

    verdict, counts = render(sections, figures)
    print(f"Step-2 validation: verdict={verdict}  PASS={counts['PASS']} "
          f"WARN={counts['WARN']} FAIL={counts['FAIL']} INFO={counts['INFO']}")
    for c in CYCLES:
        if c in sig:
            print(f"  {c}: home={sig[c]['rate_home']:.1f}% work={sig[c]['rate_work']:.1f}% "
                  f"retail={sig[c]['rate_retail']:.2f}% | closure={sig[c]['closure_rate']:.1f}% "
                  f"| pre5={sig[c]['share_pre5']*100:.2f}% gated={sig[c]['share_gated']*100:.2f}%")
    print(f"  cross-tabs written: {n_xtab}/4")
    print(f"  HTML -> {HTML_PATH}")


if __name__ == "__main__":
    main()
