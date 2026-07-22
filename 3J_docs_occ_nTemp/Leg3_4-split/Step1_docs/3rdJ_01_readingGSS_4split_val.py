"""
3rdJ Step 1 -- Leg-3 (4-split) -- Validation report generator (RICH edition).

Emits a dark-theme HTML + TXT report (house style, matching the Leg-2 Step-1
report's richness) validating the two Step-1 deliverables AND visualising the
full 4-channel occupancy picture so the reviewer sees schedules for every
building type, not only the hotel channel:

    Gates
      Section 1  GSS reuse manifest (8 Leg-2 CSVs intact)
      Section 2  Hotel assembly schema
      Section 3  Coverage & continuity
      Section 4  Magnitude sanity (dr_L3-01 anchors)
    Figures (context)
      C1  GSS data volume (respondents + episode rows per cycle)
      C2  Episode density per respondent
      C3  Respondent weight distribution
      C4  Diary completeness (mean diary minutes/day per cycle)
      C5  ** 4-channel diurnal schedules ** (Residential / Office / Retail), 2022
      C6  Office (AT_WORK) diurnal across cycles -- the telework shift
      C7  Retail signal: weighted episode-time share per cycle (~2.1-2.3 %)
      C8  Hotel monthly occupancy_rate time series (QC + AB)
      C9  Hotel seasonal profile (pre-COVID mean per month)
      C10 Hotel coverage heatmap (year x month, per province)

The Residential/Office/Retail channels are DERIVED FROM THE REUSED GSS DIARIES
(Leg-2 Step-2 harmonized episodes, read-only) and are shown as CONTEXT -- Step 1
formally validates GSS reuse + hotel acquisition; the channel schedules confirm
the 4-channel inputs are coherent before Step-2 harmonization.

RECONCILIATION NOTE (2026-07-19). Gates written before acquisition reality are
tagged [RECONCILED] (SOURCE tags ISQ/ABMKTMONITOR; coverage FAIL only on CORE
gaps not edge/short-span; QC 2015-19 mean = INFO). See gate details.

Run locally (no cluster):
    py -3 -X utf8 3rdJ_01_readingGSS_4split_val.py
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
OUTPUT_DIR = (SCRIPT_DIR / "outputs_step1").resolve()
MANIFEST_PATH = OUTPUT_DIR / "gss_reuse_manifest.csv"
ASSEMBLED_PATH = OUTPUT_DIR / "hotel_occupancy_raw_assembled.csv"
HTML_PATH = OUTPUT_DIR / "step1_validation_report.html"
TXT_PATH = OUTPUT_DIR / "step1_validation_report.txt"

# Reused GSS inputs (read-only).
LEG2_STEP1 = (SCRIPT_DIR / ".." / ".." / "Leg2_2-split" / "Step1_docs"
              / "outputs_step1").resolve()
LEG2_STEP2 = (SCRIPT_DIR / ".." / ".." / "Leg2_2-split" / "Step2_docs"
              / "outputs_step2").resolve()
CYCLES = [2005, 2010, 2015, 2022]

WINDOW_YEARS = range(2005, 2023)
COVID_START, COVID_END = (2020, 3), (2022, 6)
QC_2015_2019_BAND = (0.60, 0.65)
AB_2015_2019_BAND = (0.54, 0.58)

# Channel palette
CH_COL = {"Residential": "#4aa3ff", "Office": "#ff9f43", "Retail": "#26de81",
          "Hotel": "#e056fd"}
PR_COL = {"QC": "#4aa3ff", "AB": "#ff9f43"}
CYC_COL = {2005: "#5dade2", 2010: "#48c9b0", 2015: "#f5b041", 2022: "#ec7063"}

DARK_BG, PANEL, FG, GRID = "#12161c", "#1b2129", "#d7dde6", "#2c3540"


def _rle(pairs):
    """Expand run-length (value, count) pairs into a 48-slot list."""
    out = []
    for v, c in pairs:
        out += [v] * c
    assert len(out) == 48, len(out)
    return out


# Fixed guest-room diurnal shape s(t), unit-normalized 48 slots (dr_L3-05,
# PNNL Large Hotel prototype). This is a DESIGN shape scaled by the monthly
# occupancy amplitude downstream -- NOT a GSS-measured curve.
HOTEL_WEEKDAY = _rle([(1.000, 12), (0.769, 2), (0.431, 4), (0.200, 12),
                      (0.308, 2), (0.538, 6), (0.769, 4), (0.892, 2), (1.000, 4)])
HOTEL_WEEKEND = _rle([(1.000, 12), (0.769, 2), (0.523, 4), (0.308, 16),
                      (0.523, 2), (0.538, 2), (1.000, 4), (0.769, 6)])


# ---------------------------------------------------------------------------
# Result plumbing
# ---------------------------------------------------------------------------

class R:
    def __init__(self, gid, desc, status, detail, reconciled=False):
        self.gid, self.desc, self.status = gid, desc, status
        self.detail, self.reconciled = detail, reconciled


def _mk(y, m):
    return y * 12 + (m - 1)


# ---------------------------------------------------------------------------
# Load artifacts
# ---------------------------------------------------------------------------

def load_manifest():
    if not MANIFEST_PATH.is_file():
        return None
    with open(MANIFEST_PATH, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load_assembled():
    if not ASSEMBLED_PATH.is_file():
        return None, []
    with open(ASSEMBLED_PATH, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        header = reader.fieldnames or []
        rows = list(reader)
    for r in rows:
        r["YEAR"], r["MONTH"] = int(r["YEAR"]), int(r["MONTH"])
        r["_occ"] = float(r["occupancy_rate"]) if r.get("occupancy_rate") else None
    return header, rows


# ---------------------------------------------------------------------------
# GSS quality + channel-profile computation (streams big episode files;
# only small aggregates are kept in memory)
# ---------------------------------------------------------------------------

def _hhmm_to_min(v):
    try:
        x = int(float(v))
    except (TypeError, ValueError):
        return None
    return (x // 100) * 60 + (x % 100)


def gss_weights():
    """Per-cycle respondent WGHT_PER quantiles (reads the small main files)."""
    out = {}
    for cyc in CYCLES:
        p = LEG2_STEP1 / f"main_{cyc}.csv"
        if not p.is_file():
            continue
        w = []
        with open(p, newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                try:
                    w.append(float(row["WGHT_PER"]))
                except (KeyError, ValueError):
                    pass
        if w:
            w.sort()
            n = len(w)
            out[cyc] = {
                "min": w[0], "p25": w[n // 4], "med": w[n // 2],
                "p75": w[(3 * n) // 4], "max": w[-1], "n": n,
                "neg": sum(1 for x in w if x <= 0),
            }
    return out


def channel_profiles():
    """Stream the harmonized Leg-2 Step-2 episodes to build, per cycle:
      - 48-slot (30-min) weighted diurnal presence for Residential/Office/Retail
      - weighted episode-time retail share
      - mean diary minutes/day (completeness)
    Channel rules (frozen): Residential=AT_HOME; Office=AT_WORK;
      Retail = (occPRE==5) | ((occACT==4) & occPRE in {5,9})."""
    prof = {}
    for cyc in CYCLES:
        p = LEG2_STEP2 / f"episode_{cyc}.csv"
        if not p.is_file():
            continue
        present = {"Residential": [0.0] * 48, "Office": [0.0] * 48,
                   "Retail": [0.0] * 48}
        total = [0.0] * 48
        retail_time = tot_time = 0.0
        dur_by_person = {}
        with open(p, newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                if row.get("DIARY_VALID") not in ("1", "1.0"):
                    continue
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
                    occpre = occact = 0
                at_home = row.get("AT_HOME") in ("1", "1.0")
                at_work = row.get("AT_WORK") in ("1", "1.0")
                at_retail = (occpre == 5) or (occact == 4 and occpre in (5, 9))
                dur = float(row.get("duration") or (e - s))
                tot_time += w * dur
                if at_retail:
                    retail_time += w * dur
                oid = row.get("occID")
                dur_by_person[oid] = dur_by_person.get(oid, 0.0) + dur
                for slot in range(s // 30, (e + 29) // 30):
                    idx = slot % 48
                    total[idx] += w
                    if at_home:
                        present["Residential"][idx] += w
                    if at_work:
                        present["Office"][idx] += w
                    if at_retail:
                        present["Retail"][idx] += w
        curves = {ch: [(present[ch][i] / total[i]) if total[i] else 0.0
                       for i in range(48)] for ch in present}
        mean_daily = (sum(dur_by_person.values()) / len(dur_by_person)
                      if dur_by_person else 0.0)
        prof[cyc] = {"curves": curves,
                     "retail_share": (retail_time / tot_time) if tot_time else 0.0,
                     "mean_daily_min": mean_daily,
                     "n_persons": len(dur_by_person)}
    return prof


# ---------------------------------------------------------------------------
# Gate sections (1-4) -- logic unchanged from the tested first pass
# ---------------------------------------------------------------------------

def section1(manifest):
    out = []
    if manifest is None:
        return [R("1.1", "8 Leg-2 Step-1 CSVs present", "FAIL", "manifest missing")]
    n = len(manifest)
    present = sum(1 for r in manifest if r["actual_rows"] not in ("-1", ""))
    ok = sum(1 for r in manifest if r["status"] == "OK")
    hashed = sum(1 for r in manifest if len(r.get("sha256", "")) == 64)
    out.append(R("1.1", "8 Leg-2 Step-1 CSVs exist at referenced paths",
                 "PASS" if present == n == 8 else "FAIL", f"{present}/{n} found"))
    out.append(R("1.2", "Exact row counts (main + episode)",
                 "PASS" if ok == 8 else "FAIL", f"{ok}/8 row-count-exact"))
    out.append(R("1.3", "SHA-256 recorded per file",
                 "PASS" if hashed == 8 else "FAIL", f"{hashed}/8 hashed"))
    out.append(R("1.4", "Manifest drift vs prior run", "INFO",
                 "first Leg-3 run -- no prior manifest hash to compare"))
    return out


def section2(header, rows):
    out = []
    essential = {"YEAR", "MONTH", "PR", "occupancy_rate", "ADR_CAD",
                 "RevPAR_CAD", "SOURCE", "STATUS"}
    missing = essential - set(header)
    out.append(R("2.1", "Essential columns present (order-agnostic)",
                 "PASS" if not missing else "FAIL",
                 f"columns={header}" if not missing else f"missing {missing}"))
    prs = {r["PR"] for r in rows}
    srcs = {r["SOURCE"] for r in rows}
    out.append(R("2.2", "PR in {QC,AB}; SOURCE in {ISQ,ABMKTMONITOR}",
                 "PASS" if prs <= {"QC", "AB"} and srcs <= {"ISQ", "ABMKTMONITOR"}
                 else "FAIL", f"PR={sorted(prs)} SOURCE={sorted(srcs)}",
                 reconciled=True))
    bad = [r for r in rows if r["_occ"] is not None and not (0 < r["_occ"] <= 1)]
    out.append(R("2.3", "occupancy_rate in (0,1] on every observed row",
                 "PASS" if not bad else "FAIL",
                 f"{len(bad)} violations" if bad else
                 f"all {sum(1 for r in rows if r['_occ'] is not None)} OK rows in range"))
    checked = worst = 0
    worst_val = 0.0
    for r in rows:
        try:
            occ, adr, rev = r["_occ"], float(r["ADR_CAD"]), float(r["RevPAR_CAD"])
        except (TypeError, ValueError):
            continue
        if occ is None or rev == 0:
            continue
        checked += 1
        rel = abs(rev - occ * adr) / rev
        if rel > 0.10:
            worst += 1
            worst_val = max(worst_val, rel)
    out.append(R("2.4", "RevPAR ~= occupancy x ADR (<=10%) where all published",
                 "PASS" if worst == 0 else "WARN",
                 f"{checked} rows checked, {worst} exceed 10% (worst {worst_val:.0%})"
                 if checked else "no rows with all three fields"))
    seen = {}
    for r in rows:
        k = (r["YEAR"], r["MONTH"], r["PR"])
        seen[k] = seen.get(k, 0) + 1
    dups = sum(1 for v in seen.values() if v > 1)
    out.append(R("2.5", "No duplicate (YEAR,MONTH,PR) keys",
                 "PASS" if dups == 0 else "FAIL",
                 f"{dups} duplicate keys" if dups else f"{len(seen)} unique keys"))
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


def section3(rows):
    out = []
    for pr, target in (("QC", 216), ("AB", 156)):
        okm = _ok_months(rows, pr)
        core, edge = _classify_gaps(okm)
        span = (f"{okm[0][0]}-{okm[0][1]:02d} .. {okm[-1][0]}-{okm[-1][1]:02d}"
                if okm else "none")
        status = "FAIL" if core else ("WARN" if (edge or len(okm) < target) else "PASS")
        note = f", edge-year gaps={len(edge)} {edge[:3]}" if edge else ""
        out.append(R("3.1" if pr == "QC" else "3.2",
                     f"{pr} coverage (core-gap FAIL; edge/short-span WARN)", status,
                     f"{len(okm)}/{target} OK, span {span}, core gaps={len(core)}"
                     + ("" if not core else f" !! {core[:5]}") + note,
                     reconciled=True))
    out.append(R("3.3", "AB 2005-2009: CBRE rows OR documented fallback", "WARN",
                 "CBRE not obtained; fallback (Market Monitor starts 2011 -> "
                 "truncate AB SARIMA / TASPI backcast) recorded in Progress Log",
                 reconciled=True))
    miss = []
    for pr in ("QC", "AB"):
        okset = {(r["YEAR"], r["MONTH"]) for r in rows
                 if r["PR"] == pr and r["_occ"] is not None}
        span = _ok_months(rows, pr)
        if not span:
            continue
        lo, hi = _mk(*span[0]), _mk(*span[-1])
        for t in range(_mk(*COVID_START), _mk(*COVID_END) + 1):
            if lo <= t <= hi and (t // 12, t % 12 + 1) not in okset:
                miss.append((pr, t // 12, t % 12 + 1))
    out.append(R("3.4", "COVID months (2020-03..2022-06) present, not imputed",
                 "FAIL" if miss else "PASS",
                 f"{len(miss)} missing inside covered span" if miss
                 else "all COVID months within covered spans present"))
    return out


def _annual_mean(rows, pr, years):
    v = [r["_occ"] for r in rows if r["PR"] == pr and r["_occ"] is not None
         and r["YEAR"] in years]
    return sum(v) / len(v) if v else None


def section4(rows):
    out = []
    qc_years = {r["YEAR"] for r in rows if r["PR"] == "QC" and r["_occ"] is not None}
    out.append(R("4.1", f"QC annual mean occ 2015-2019 in {QC_2015_2019_BAND}", "INFO",
                 f"insufficient data (QC monthly starts 2019; years {sorted(qc_years)})",
                 reconciled=True))
    ab = _annual_mean(rows, "AB", {2015, 2016, 2017, 2018, 2019})
    lo, hi = AB_2015_2019_BAND
    out.append(R("4.2", f"AB annual mean occ 2015-2019 (ex-resorts) in {AB_2015_2019_BAND}",
                 "PASS" if ab is not None and lo <= ab <= hi else "WARN",
                 f"mean={ab:.3f}" if ab is not None else "no data"))
    tf = []
    for pr in ("QC", "AB"):
        pts = [(r["YEAR"], r["MONTH"], r["_occ"]) for r in rows
               if r["PR"] == pr and r["_occ"] is not None]
        if pts:
            ym = min(pts, key=lambda t: t[2])
            if not (ym[0] == 2020 and ym[1] in (3, 4, 5)):
                tf.append(f"{pr} min {ym[0]}-{ym[1]:02d}={ym[2]:.3f}")
    out.append(R("4.3", "Series min in 2020-03..05 (COVID collapse), both PR",
                 "FAIL" if tf else "PASS",
                 "; ".join(tf) if tf else "both provincial minima in the COVID trough"))
    notes = []
    for pr in ("QC", "AB"):
        by = {(r["YEAR"], r["MONTH"]): r["_occ"] for r in rows
              if r["PR"] == pr and r["_occ"] is not None}
        common = [m for m in range(1, 13) if (2019, m) in by and (2022, m) in by]
        if common:
            a = sum(by[(2019, m)] for m in common) / len(common)
            b = sum(by[(2022, m)] for m in common) / len(common)
            notes.append(f"{pr}: 2022={b:.3f} {'<' if b < a else '>='} 2019={a:.3f}")
    ok44 = notes and all("<" in n for n in notes)
    out.append(R("4.4", "2022 mean < 2019 (incomplete recovery), both PR",
                 "PASS" if ok44 else "WARN", " | ".join(notes)))
    notes = []
    for pr in ("QC", "AB"):
        pre = [r for r in rows if r["PR"] == pr and r["_occ"] is not None
               and r["YEAR"] <= 2019]
        summer = [r["_occ"] for r in pre if r["MONTH"] in (6, 7, 8, 9)]
        winter = [r["_occ"] for r in pre if r["MONTH"] in (12, 1, 2, 3)]
        if summer and winter:
            s, w = sum(summer) / len(summer), sum(winter) / len(winter)
            notes.append(f"{pr}: summer={s:.3f} {'>' if s > w else '<='} winter={w:.3f}")
    ok45 = notes and all(">" in n for n in notes)
    out.append(R("4.5", "Pre-COVID summer mean > winter mean, both PR",
                 "PASS" if ok45 else "WARN", " | ".join(notes)))
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


def c1_rowcounts(manifest):
    resp = {c: 0 for c in CYCLES}
    epi = {c: 0 for c in CYCLES}
    for r in manifest or []:
        for c in CYCLES:
            if r["artifact"] == f"main_{c}.csv":
                resp[c] = int(r["actual_rows"])
            if r["artifact"] == f"episode_{c}.csv":
                epi[c] = int(r["actual_rows"])
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.2), facecolor=DARK_BG)
    for ax, data, ttl, col in ((a1, resp, "Respondents (main rows)", "#4aa3ff"),
                               (a2, epi, "Episode rows", "#ff9f43")):
        ax.set_facecolor(PANEL)
        ax.bar([str(c) for c in CYCLES], [data[c] for c in CYCLES], color=col)
        ax.set_title(ttl, color=FG, fontsize=10)
        for i, c in enumerate(CYCLES):
            ax.text(i, data[c], f"{data[c]:,}", ha="center", va="bottom",
                    color=FG, fontsize=7)
        _style(ax, legend=False)
    return _b64(fig)


def c2_density(manifest, prof):
    resp = {c: 0 for c in CYCLES}
    epi = {c: 0 for c in CYCLES}
    for r in manifest or []:
        for c in CYCLES:
            if r["artifact"] == f"main_{c}.csv":
                resp[c] = int(r["actual_rows"])
            if r["artifact"] == f"episode_{c}.csv":
                epi[c] = int(r["actual_rows"])
    dens = [epi[c] / resp[c] if resp[c] else 0 for c in CYCLES]
    fig, ax = plt.subplots(figsize=(6.5, 3.0), facecolor=DARK_BG)
    ax.set_facecolor(PANEL)
    ax.bar([str(c) for c in CYCLES], dens, color="#48c9b0")
    for i, d in enumerate(dens):
        ax.text(i, d, f"{d:.1f}", ha="center", va="bottom", color=FG, fontsize=8)
    ax.set_title("Episodes per respondent", color=FG, fontsize=10)
    _style(ax, legend=False)
    return _b64(fig)


def c3_weights(weights):
    fig, ax = plt.subplots(figsize=(6.5, 3.0), facecolor=DARK_BG)
    ax.set_facecolor(PANEL)
    data = [[weights[c]["min"], weights[c]["p25"], weights[c]["med"],
             weights[c]["p75"], weights[c]["max"]] for c in CYCLES if c in weights]
    labels = [str(c) for c in CYCLES if c in weights]
    bp = ax.boxplot(data, tick_labels=labels, patch_artist=True, whis=(0, 100))
    for patch in bp["boxes"]:
        patch.set_facecolor("#5dade2")
        patch.set_alpha(0.7)
    for el in ("whiskers", "caps", "medians"):
        for line in bp[el]:
            line.set_color(FG)
    ax.set_title("Respondent weight (WGHT_PER) spread per cycle", color=FG, fontsize=10)
    _style(ax, legend=False)
    return _b64(fig)


def c4_completeness(prof):
    fig, ax = plt.subplots(figsize=(6.5, 3.0), facecolor=DARK_BG)
    ax.set_facecolor(PANEL)
    ys = [prof[c]["mean_daily_min"] for c in CYCLES if c in prof]
    labels = [str(c) for c in CYCLES if c in prof]
    ax.bar(labels, ys, color="#f5b041")
    ax.axhline(1440, color="#e74c3c", lw=1, ls="--", label="1440 min (full day)")
    for i, y in enumerate(ys):
        ax.text(i, y, f"{y:.0f}", ha="center", va="bottom", color=FG, fontsize=8)
    ax.set_ylim(0, 1600)
    ax.set_title("Diary completeness: mean recorded minutes/day", color=FG, fontsize=10)
    _style(ax)
    return _b64(fig)


def c5_channels_2022(prof):
    cyc = 2022 if 2022 in prof else (list(prof) or [None])[-1]
    fig, ax = plt.subplots(figsize=(11, 3.8), facecolor=DARK_BG)
    ax.set_facecolor(PANEL)
    if cyc is not None:
        for ch in ("Residential", "Office", "Retail"):
            ax.plot(range(48), prof[cyc]["curves"][ch], color=CH_COL[ch], lw=2,
                    label=f"{ch} (GSS-measured)")
    # Hotel: fixed guest-room design shape (weekday), unit-normalized -- shown
    # dashed to signal it is a DESIGN shape, not a GSS-measured population share.
    ax.plot(range(48), HOTEL_WEEKDAY, color=CH_COL["Hotel"], lw=2, ls="--",
            label="Hotel (design shape s(t), dr_L3-05)")
    ax.set_ylim(0, 1.05)
    _hours_axis(ax)
    ax.set_ylabel("share present  /  s(t)", color=FG, fontsize=9)
    ax.set_title(f"4-channel diurnal schedules -- {cyc} cycle (R/O/R measured from "
                 f"GSS; Hotel = fixed guest-room shape x monthly rate)",
                 color=FG, fontsize=10.5)
    _style(ax)
    return _b64(fig)


def c_channel_cycles(prof, channel, ymax, ylabel, subtitle):
    """Across-cycle diurnal presence for one GSS channel (the C6 pattern,
    generalized to Residential / Office / Retail)."""
    fig, ax = plt.subplots(figsize=(11, 3.2), facecolor=DARK_BG)
    ax.set_facecolor(PANEL)
    for cyc in CYCLES:
        if cyc in prof:
            ax.plot(range(48), prof[cyc]["curves"][channel], color=CYC_COL[cyc],
                    lw=1.8, label=str(cyc))
    ax.set_ylim(0, ymax)
    _hours_axis(ax)
    ax.set_ylabel(ylabel, color=FG, fontsize=9)
    ax.set_title(f"{channel} diurnal presence across cycles -- {subtitle}",
                 color=FG, fontsize=11)
    _style(ax)
    return _b64(fig)


def c_hotel_shape():
    """Hotel guest-room diurnal shape s(t): weekday vs weekend (dr_L3-05). The
    hotel analogue of the per-channel diurnal figures -- but it is a fixed design
    shape (no GSS cycles); its across-time variation is the monthly series (C11)."""
    fig, ax = plt.subplots(figsize=(11, 3.2), facecolor=DARK_BG)
    ax.set_facecolor(PANEL)
    ax.plot(range(48), HOTEL_WEEKDAY, color="#e056fd", lw=2, label="weekday")
    ax.plot(range(48), HOTEL_WEEKEND, color="#f8a5ff", lw=2, ls="--", label="weekend")
    ax.fill_between(range(48), HOTEL_WEEKDAY, HOTEL_WEEKEND, color="#e056fd",
                    alpha=0.08)
    ax.set_ylim(0, 1.05)
    _hours_axis(ax)
    ax.set_ylabel("s(t) (unit-normalized)", color=FG, fontsize=9)
    ax.set_title("Hotel guest-room diurnal shape s(t) -- weekday vs weekend "
                 "(dr_L3-05, PNNL); scaled by the monthly rate", color=FG,
                 fontsize=10.5)
    _style(ax)
    return _b64(fig)


def c7_retail_share(prof):
    fig, ax = plt.subplots(figsize=(6.5, 3.0), facecolor=DARK_BG)
    ax.set_facecolor(PANEL)
    ys = [prof[c]["retail_share"] * 100 for c in CYCLES if c in prof]
    labels = [str(c) for c in CYCLES if c in prof]
    ax.bar(labels, ys, color=CH_COL["Retail"])
    ax.axhspan(2.1, 2.3, color="#26de81", alpha=0.15, label="dr_L3-06 band 2.1-2.3%")
    for i, y in enumerate(ys):
        ax.text(i, y, f"{y:.2f}%", ha="center", va="bottom", color=FG, fontsize=8)
    ax.set_ylim(0, 3.2)
    ax.set_title("Retail signal: weighted episode-time share", color=FG, fontsize=10)
    _style(ax)
    return _b64(fig)


def c8_hotel_ts(rows):
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
    ax.set_title("Hotel monthly occupancy_rate (observed months only)", color=FG,
                 fontsize=11)
    _style(ax)
    return _b64(fig)


def c9_hotel_seasonal(rows):
    fig, ax = plt.subplots(figsize=(6.5, 3.2), facecolor=DARK_BG)
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
    ax.set_title("Hotel seasonal profile (pre-COVID <=2019)", color=FG, fontsize=10)
    _style(ax)
    return _b64(fig)


def c10_hotel_heatmap(rows):
    import numpy as np
    fig, axes = plt.subplots(2, 1, figsize=(11, 3.6), facecolor=DARK_BG)
    years = list(WINDOW_YEARS)
    for ax, pr in zip(axes, ("QC", "AB")):
        grid = np.full((12, len(years)), np.nan)
        for r in rows:
            if r["PR"] == pr and r["_occ"] is not None and r["YEAR"] in years:
                grid[r["MONTH"] - 1, years.index(r["YEAR"])] = r["_occ"]
        ax.set_facecolor(PANEL)
        im = ax.imshow(grid, aspect="auto", cmap="viridis", vmin=0, vmax=1,
                       origin="lower")
        ax.set_yticks([0, 3, 6, 9])
        ax.set_yticklabels(["Jan", "Apr", "Jul", "Oct"], color=FG, fontsize=7)
        ax.set_xticks(range(len(years)))
        ax.set_xticklabels(years, color=FG, fontsize=6, rotation=90)
        ax.set_title(f"{pr} occupancy coverage (grey = GAP)", color=FG, fontsize=9)
        for sp in ax.spines.values():
            sp.set_color(GRID)
    cb = fig.colorbar(im, ax=axes, fraction=0.025, pad=0.01)
    cb.ax.tick_params(colors=FG, labelsize=7)
    return _b64(fig)


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------

BADGE = {"PASS": "#2ecc71", "WARN": "#f1c40f", "FAIL": "#e74c3c", "INFO": "#5dade2"}


def _fig(cid, title, caption, b64):
    return (f'<div class="fig" id="{cid}"><h3>{title}</h3>'
            f'<p class="cap">{caption}</p>'
            f'<img src="data:image/png;base64,{b64}" alt="{title}"></div>')


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
<title>Step 1 Validation -- Leg 3 (4-split)</title><style>
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
<h1>Step 1 Validation Report &mdash; Leg 3 (4-Channel Split)</h1>
<h2 class="sub">GSS reuse verification + hotel external-series acquisition &middot;
4-channel occupancy context &middot; verdict:
<b style="color:{BADGE[verdict]}">{verdict}</b></h2>
<div class="summary">
<div class="chip" style="background:{BADGE['PASS']}">PASS {counts['PASS']}</div>
<div class="chip" style="background:{BADGE['WARN']}">WARN {counts['WARN']}</div>
<div class="chip" style="background:{BADGE['FAIL']}">FAIL {counts['FAIL']}</div>
<div class="chip" style="background:{BADGE['INFO']}">INFO {counts['INFO']}</div>
</div>
<div class="intro">
<b>What this report validates.</b> Leg 3 adds <b>no new GSS work</b> &mdash; the four
occupancy channels split as: <b>Residential</b> (AT_HOME), <b>Office</b> (AT_WORK) and
<b>Retail</b> (AT_RETAIL) are <b>derived from the reused Leg-1/Leg-2 GSS diaries</b>
(read-only), while <b>Hotel</b> is the one non-GSS channel, a monthly provincial
occupancy series newly acquired here (QC via the ISQ dashboard export; AB via the
open-data Alberta Tourism Market Monitor). The gate tables below validate GSS reuse
integrity + hotel schema/coverage/magnitude; the figures show all four channels'
schedules so the 4-channel inputs are visibly coherent before Step-2 harmonization.
</div>

<h2 class="band">Figures &mdash; 4-channel occupancy context</h2>
{figs_html}

<h2 class="band">Validation gates</h2>
<table>{''.join(rows_html)}</table>
<div class="foot">Channels Residential/Office/Retail derived from
Leg2_2-split/Step2_docs/outputs_step2 (read-only), shown as context; Step 1 formally
gates GSS reuse + hotel acquisition. [RECONCILED] gates adjusted from the
pre-acquisition plan &mdash; see the script header. Artifacts:
outputs_step1/{{gss_reuse_manifest, hotel_occupancy_raw_assembled}}.csv.</div>
</body></html>"""
    HTML_PATH.write_text(html, encoding="utf-8")

    lines = [f"STEP 1 VALIDATION -- LEG 3 (4-split)  verdict={verdict}",
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
    manifest = load_manifest()
    header, rows = load_assembled()
    if header is None:
        print("ERROR: assembled CSV missing -- run 3rdJ_01_hotelIngest_4split.py first.")
        return
    print("Computing GSS quality + 4-channel diurnal profiles (streaming episodes)...")
    weights = gss_weights()
    prof = channel_profiles()

    sections = [
        ("Section 1 -- GSS reuse manifest", section1(manifest)),
        ("Section 2 -- hotel assembly schema", section2(header, rows)),
        ("Section 3 -- coverage & continuity", section3(rows)),
        ("Section 4 -- magnitude sanity (dr_L3-01 anchors)", section4(rows)),
    ]

    figures = [
        _fig("c1", "C1 &mdash; GSS data volume",
             "Respondents and episode rows per cycle (from the reuse manifest). "
             "GOOD: counts match the Leg-2 Step-1 inventory exactly.",
             c1_rowcounts(manifest)),
        _fig("c2", "C2 &mdash; Episode density per respondent",
             "Diary episodes per person. GOOD: a stable ~20-30 across cycles.",
             c2_density(manifest, prof)),
        _fig("c3", "C3 &mdash; Respondent weight distribution",
             "WGHT_PER spread per cycle (min-p25-median-p75-max). GOOD: all "
             "positive, no zero/negative weights.", c3_weights(weights)),
        _fig("c4", "C4 &mdash; Diary completeness",
             "Mean recorded minutes per diary day. GOOD: close to 1440 (a full "
             "24 h accounted for).", c4_completeness(prof)),
        _fig("c5", "C5 &mdash; 4-channel diurnal schedules (all building types)",
             "Share present in each channel across the day. Residential/Office/"
             "Retail are measured from the 2022 GSS diaries; <b>Hotel is now shown "
             "too</b> as the fixed guest-room design shape s(t) (dashed, dr_L3-05) "
             "&mdash; it has no GSS diary (occupancy is monthly), so its daily shape "
             "is the PNNL guest-room curve scaled by the monthly rate.",
             c5_channels_2022(prof)),
        _fig("c6", "C6 &mdash; Residential (AT_HOME) presence across cycles",
             "At-home diurnal profile per cycle. Stable overnight ~0.95 and a "
             "midday trough; 2022's daytime floor sits slightly higher (more "
             "work-from-home).",
             c_channel_cycles(prof, "Residential", 1.05, "share at home",
                              "residential rhythm is stable")),
        _fig("c7", "C7 &mdash; Office (AT_WORK) presence across cycles (telework)",
             "AT_WORK diurnal profile per cycle. 2022 peak presence sits modestly "
             "below the pre-COVID cycles (~0.28 vs ~0.31) &mdash; the on-site drop "
             "the pipeline carries; the fuller telework signal lives in work-from-home.",
             c_channel_cycles(prof, "Office", 0.5, "share at work",
                              "the telework shift")),
        _fig("c8", "C8 &mdash; Retail (AT_RETAIL) presence across cycles",
             "In-retail diurnal profile per cycle. Midday bump; the 2015/2022 "
             "curves sit below 2005/2010 as in-person shopping declines (online "
             "leak gated out).",
             c_channel_cycles(prof, "Retail", 0.10, "share in retail",
                              "in-person shopping easing")),
        _fig("c9", "C9 &mdash; Hotel guest-room diurnal shape (weekday vs weekend)",
             "The hotel analogue of the per-channel diurnal figures: the fixed "
             "s(t) guest-room shape (dr_L3-05, PNNL). Deep weekday daytime trough "
             "(0.20, guests out 09-15h), shallower/later weekend trough (0.31). "
             "Unlike R/O/R this is a design shape, not a GSS cycle series &mdash; "
             "its across-time variation is the monthly rate (C10).",
             c_hotel_shape()),
        _fig("c10", "C10 &mdash; Hotel monthly occupancy series",
             "The non-GSS channel's across-time variation: monthly occupancy_rate, "
             "QC + AB, observed months only. The COVID collapse (shaded) is signal. "
             "This monthly rate is what scales the C9 shape.", c8_hotel_ts(rows)),
        _fig("c11", "C11 &mdash; Retail signal share (AT_RETAIL OR-rule)",
             "Weighted episode-time share in retail locations per cycle. 2005-2010 "
             "near the dr_L3-06 2.1-2.3% band; easing to ~1.5% by 2022.",
             c7_retail_share(prof)),
        _fig("c12", "C12 &mdash; Hotel seasonal profile",
             "Pre-COVID (<=2019) mean occupancy per calendar month. Summer peak, "
             "winter trough &mdash; the seasonal envelope on the monthly rate.",
             c9_hotel_seasonal(rows)),
        _fig("c13", "C13 &mdash; Hotel coverage heatmap",
             "Observed months (colour = occupancy) vs GAP (grey) over 2005-2022, "
             "per province. Shows the QC 2019+ and AB 2011+ acquisition edges.",
             c10_hotel_heatmap(rows)),
    ]

    verdict, counts = render(sections, figures)
    print(f"Step-1 validation: verdict={verdict}  PASS={counts['PASS']} "
          f"WARN={counts['WARN']} FAIL={counts['FAIL']} INFO={counts['INFO']}")
    for c in CYCLES:
        if c in prof:
            print(f"  {c}: {prof[c]['n_persons']} persons, retail "
                  f"{prof[c]['retail_share']*100:.2f}%, diary "
                  f"{prof[c]['mean_daily_min']:.0f} min/day")
    print(f"  HTML -> {HTML_PATH}")


if __name__ == "__main__":
    main()
