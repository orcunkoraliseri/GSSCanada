"""
_gen_step6_panel.py
Step-6 Improvement 4 (report-side) — injects TWO additive blocks into the canonical
(joint-raked, CANONICAL POPULATION banner, 35/35 PASS, 10-figure) step6_validation_report.html:

  1. A "Documented deviations — disposition (Option A)" panel, right after the
     CANONICAL POPULATION banner. Reproduces the agreed §2/§3/§4 deviation table
     (strict gate kept visible; relabel + document, no re-thresholding).
  2. A diagnostic (INFO, not a gate) work-from-home (WFH) figure in §5: the WD
     paid-work-at-home rate in the calibrated 2030 population vs the 2022 model
     backcast, both re-derived live from the small forecast_2030 CSVs.

Mirrors the base64/HTML-injection mechanism of _gen_step6_plots.py (Improvement 3)
in this same directory: matplotlib -> base64 PNG data-URI -> string-injected <img>
at anchor tokens in the existing HTML. Idempotent (guarded by its own HTML comment
marker, distinct from _gen_step6_plots.py's marker) and self-contained (no external
files/CDN). Does NOT modify the validator (06_longitudinalForecastingGSS_val.py),
06_forecast_rake.py, or any eSim_*.py file, and does NOT re-run the validator — the
35/35 tally text and the 10 existing figures are left byte-untouched; only new HTML
is inserted.

Paid-work act30 code -- CONFIRMED, not guessed:
  `02_harmonizeGSS.py` defines the canonical 14-category scheme used for both
  `occACT`/`act30`: ACT_LABELS = {1: "Work & Related", 2: "Household Work &
  Maintenance", ...} (source lines 354-369). `02_harmonizationGSS_actCodes.md`
  independently documents category 1 as "Work & Related -- Paid/unpaid work, job
  searching, overtime, work-related breaks". `06_forecast_rake.py`'s HOME_ACTS =
  {2,3,5,6,7,10} (line 62) comments code 2 as "HH Work" (household work, i.e.
  category 2, Household Work & Maintenance) -- confirming code 2 is NOT paid
  employment and ruling out the ambiguity the task flagged. => PAID_WORK_CODE = 1.

Data sources (small files only, per task instructions -- augmented_diaries.csv,
530 MB, is NEVER read):
  - 2030_synthetic_diaries_joint_raked.csv (~11 MB, 37,008 rows) -- calibrated
    2030 population (canonical).
  - reconstructed_2022_diaries.csv (~8 MB) -- the model's 2022 BACKCAST
    (explicitly NOT observed 2022; labelled as such throughout).

Run once (idempotent thereafter):
    py 2J_docs_occ_nTemp/outputs_step6/improvement/_gen_step6_panel.py
"""

from __future__ import annotations

import base64
import io
import shutil
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ── Paths (absolute) ────────────────────────────────────────────────────────
BASE         = Path(r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main")
FORECAST_DIR = BASE / "0_Occupancy" / "Outputs_21CEN22GSS" / "forecast_2030"
JOINT_RAKED  = FORECAST_DIR / "2030_synthetic_diaries_joint_raked.csv"          # ~11 MB
RECON_2022   = FORECAST_DIR / "reconstructed_2022_diaries.csv"                  # ~8 MB

STEP6_DIR = BASE / "2J_docs_occ_nTemp" / "outputs_step6"
REPORT    = STEP6_DIR / "step6_validation_report.html"          # source AND destination (in place)
PREV_DIR  = STEP6_DIR / "previous"
ARCHIVE   = PREV_DIR / "step6_validation_report_prepanel_20260710.html"

ACT_COLS = [f"act30_{i:03d}" for i in range(1, 49)]
HOM_COLS = [f"hom30_{i:03d}" for i in range(1, 49)]

PAID_WORK_CODE = 1   # "Work & Related" -- see module docstring for the 3-source confirmation

PRIOR_MARKER = "<!-- STEP6_FIGURES_V1: captions + 3 new figures injected by _gen_step6_plots.py -->"
MARKER = "<!-- STEP6_PANEL_V1: disposition panel + WFH diagnostic figure injected by _gen_step6_panel.py -->"

# ── Theme ────────────────────────────────────────────────────────────────────
BLUE, GREEN, ORANGE, RED, PURPLE, TEAL, GREY = (
    "#1976d2", "#388e3c", "#e65100", "#c62828", "#7b1fa2", "#00838f", "#616161")
AMBER = "#f57f17"
plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white",
    "font.family": "sans-serif", "font.size": 10,
})


def _b64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def fig_block(title: str, caption_html: str, b64: str, accent: str = TEAL) -> str:
    """A titled, captioned NEW figure block (matches _gen_step6_plots.py's style)."""
    return (
        f'<div style="background:#f5f7fb;border:1px solid #dde3f0;border-left:4px solid {accent};'
        f'border-radius:6px;padding:12px 16px;margin:10px 0 16px 0;">'
        f'<h4 style="color:{accent};margin:0 0 8px 0;font-size:13.5px;">{title}</h4>'
        f'<img src="data:image/png;base64,{b64}" alt="{title}" '
        f'style="max-width:100%;display:block;margin:4px 0 8px 0;border-radius:4px;"/>'
        f'<div class="cap" style="font-size:12.5px;color:#333;line-height:1.55;">{caption_html}</div>'
        f'</div>'
    )


def insert_after(html: str, anchor: str, needle: str, block: str) -> str:
    a_idx = html.index(anchor)          # raises ValueError if missing -> aborts loudly
    n_idx = html.index(needle, a_idx)
    at = n_idx + len(needle)
    return html[:at] + "\n" + block + html[at:]


def insert_before(html: str, anchor: str, needle: str, block: str) -> str:
    """Find `anchor`, then find `needle` after it, and insert `block` right BEFORE `needle`."""
    a_idx = html.index(anchor)          # raises ValueError if missing -> aborts loudly
    n_idx = html.index(needle, a_idx)
    return html[:n_idx] + "\n" + block + html[n_idx:]


# ══════════════════════════════════════════════════════════════════════════
# 0. Idempotency guard — check BEFORE any heavy work
# ══════════════════════════════════════════════════════════════════════════
if not REPORT.exists():
    sys.exit(f"ABORT: report not found: {REPORT}")

html = REPORT.read_text(encoding="utf-8")

if MARKER in html:
    print(f"[IDEMPOTENT] marker already present in {REPORT.name} — 0 insertions, nothing to do.")
    sys.exit(0)

# ── Anchor sanity check (abort loudly rather than inject garbage) ──────────
REQUIRED_ANCHORS = [
    PRIOR_MARKER,                 # Improvement 3 must have already run
    "CANONICAL POPULATION",
    "35/35 checks passed",
    "<h2>5 — 2030 Schedule Plausibility</h2>",
    "<h2>6 — BEM Output Readiness</h2>",
    "F_S5 · Each §5 metric vs its pass band (supplementary)",
    "<body>",
]
missing = [a for a in REQUIRED_ANCHORS if a not in html]
if missing:
    sys.exit(f"ABORT: required anchor(s) not found — {missing}. No file written. "
              f"(Run _gen_step6_plots.py first if PRIOR_MARKER is missing.)")

N_IMG_BEFORE = html.count("data:image/png;base64,")
if N_IMG_BEFORE != 10:
    sys.exit(f"ABORT: expected exactly 10 existing <img> figures (post-Improvement-3), "
              f"found {N_IMG_BEFORE}. No file written.")

print(f"[0] anchors OK: prior marker, banner, 35/35 tally, §5/§6 headers, F_S5 block present; "
      f"{N_IMG_BEFORE} existing <img> figures found.")

# ══════════════════════════════════════════════════════════════════════════
# 1. Archive the pre-panel canonical report FIRST (byte-identical)
# ══════════════════════════════════════════════════════════════════════════
PREV_DIR.mkdir(exist_ok=True)
if not ARCHIVE.exists():
    shutil.copy2(REPORT, ARCHIVE)
    print(f"[1] archived pre-panel report -> {ARCHIVE}")
else:
    print(f"[1] archive already present, leaving as-is -> {ARCHIVE}")

# ══════════════════════════════════════════════════════════════════════════
# 2. WFH DATA — re-derived live from the two small forecast_2030 CSVs
# ══════════════════════════════════════════════════════════════════════════
print(f"\n=== Paid-work act30 code = {PAID_WORK_CODE} ('Work & Related', confirmed from "
      f"02_harmonizeGSS.py ACT_LABELS L354-369 + 02_harmonizationGSS_actCodes.md category-1 "
      f"definition; 06_forecast_rake.py HOME_ACTS={{2,3,5,6,7,10}} L62 independently comments "
      f"code 2 as 'HH Work', i.e. Household Work & Maintenance, NOT paid employment) ===\n")


def wfh_wd_rate(path: Path, label: str) -> dict:
    """WD (DDAY_STRATA==1) share of person-slots where act30==PAID_WORK_CODE AND hom30==1,
    plus the 48-slot time-of-day profile of that same share."""
    df = pd.read_csv(path)
    wd = df[df["DDAY_STRATA"] == 1]
    act = wd[ACT_COLS].to_numpy()
    hom = wd[HOM_COLS].to_numpy()
    wfh_mask = (act == PAID_WORK_CODE) & (hom == 1)
    n_rows, n_slots_total = wd.shape[0], act.size
    rate_pct = float(wfh_mask.sum()) / n_slots_total * 100
    profile_pct = wfh_mask.mean(axis=0) * 100  # per-slot share, length 48
    print(f"[2] {label}: n_wd_rows={n_rows:,}  n_wd_slots={n_slots_total:,}  "
          f"n_wfh_slots={int(wfh_mask.sum()):,}  WD_WFH_rate={rate_pct:.4f}%  "
          f"(per-slot max={profile_pct.max():.3f}% at slot {int(profile_pct.argmax())+1})")
    return {"n_rows": n_rows, "rate_pct": rate_pct, "profile_pct": profile_pct}


d2030 = wfh_wd_rate(JOINT_RAKED, "2030 calibrated (joint-raked, canonical)")
d2022 = wfh_wd_rate(RECON_2022, "2022 backcast (reconstructed, NOT observed)")
delta_pp = d2030["rate_pct"] - d2022["rate_pct"]
print(f"\n[2] Delta (2030 calibrated − 2022 backcast) = {delta_pp:+.4f} pp. "
      f"{'DEGENERATE/near-zero — flagging, not fabricating a signal.' if abs(d2030['rate_pct']) < 0.05 or abs(d2022['rate_pct']) < 0.05 else 'Non-degenerate signal.'}")

# ══════════════════════════════════════════════════════════════════════════
# 3. BUILD THE WFH FIGURE — two panels: aggregate bar + 48-slot time profile
# ══════════════════════════════════════════════════════════════════════════
hours = [(i * 0.5) for i in range(48)]  # slot i (0-indexed) starts at hour i*0.5

fig, (axL, axR) = plt.subplots(1, 2, figsize=(11.5, 3.8), gridspec_kw={"width_ratios": [1, 2]})

# Left: aggregate WD WFH rate, 2030 vs 2022-backcast
bars = axL.bar(["2030\ncalibrated", "2022\nbackcast"],
                [d2030["rate_pct"], d2022["rate_pct"]],
                color=[ORANGE, GREY], width=0.55)
for b, v in zip(bars, [d2030["rate_pct"], d2022["rate_pct"]]):
    axL.text(b.get_x() + b.get_width() / 2, v + 0.08, f"{v:.2f}%", ha="center",
              fontsize=9.5, fontweight="bold")
axL.set_ylabel("WD person-slot share (%)")
axL.set_title("Aggregate WD WFH rate", fontsize=10)
axL.set_ylim(0, max(d2030["rate_pct"], d2022["rate_pct"]) * 1.35)

# Right: 48-slot time-of-day profile
axR.plot(hours, d2030["profile_pct"], color=ORANGE, linewidth=1.8, label="2030 calibrated (canonical)")
axR.plot(hours, d2022["profile_pct"], color=GREY, linewidth=1.8, linestyle="--",
          label="2022 backcast (NOT observed)")
axR.set_xticks([0, 6, 12, 18, 24])
axR.set_xlabel("Hour of day")
axR.set_ylabel("WFH share (%)")
axR.set_title("WD time-of-day WFH profile (48 slots)", fontsize=10)
axR.legend(fontsize=8.5, loc="upper right")
axR.set_xlim(0, 24)

fig.suptitle("DIAGNOSTIC — informational, not a gate — WD work-from-home rate "
              f"(act30={PAID_WORK_CODE} 'Work & Related' ∧ hom30=1)", fontsize=11, y=1.06, color=AMBER)
plt.tight_layout()
F_WFH = _b64(fig)
print("\n[3] WFH diagnostic figure rendered.")

# ══════════════════════════════════════════════════════════════════════════
# 4. THE "DOCUMENTED DEVIATIONS — DISPOSITION (OPTION A)" PANEL
# ══════════════════════════════════════════════════════════════════════════
DEVIATIONS_TABLE_ROWS = [
    dict(
        dev="§2 True-Future-Test <b>Saturday</b> JS",
        gate="0.20",
        obs="<b>0.2040</b> (+0.4 pp)",
        basis="True-Future-Test is an <b>unseen-cycle</b> test (test cycle never in training) &rarr; "
              "runs above within-cycle val JS <i>by design</i>; 0.2040 &#8810; uniform baseline &asymp; 0.5, "
              "within the &plusmn;0.02 documented tolerance",
        nonblocker="Saturday <b>activity-mix</b> only; occupancy (hom30/AT_HOME) drives EnergyPlus and is "
                    "unaffected; &sect;5 2030 Sat plausibility PASS",
        fig="F_S2",
    ),
    dict(
        dev="§3 COVID gate <b>redefinition</b>",
        gate="marginal-JS COVID check",
        obs="<b>AT_HOME aggregate residual 0.2 pp</b> (&le;5 pp)",
        basis="marginal-JS conflated drift with 14-activity noise; the AT_HOME aggregate residual measures "
              "the COVID structural break directly (primary research finding) and is the BEM-relevant quantity",
        nonblocker="occupancy-level metric; night AT_HOME PASS",
        fig="F_S3",
    ),
    dict(
        dev="§4 Weekend <b>backcast</b> re-baseline",
        gate="&lt; 0.10",
        obs="Sat <b>0.1637</b> / Sun <b>0.1618</b> (&lt; 0.20)",
        basis="the &lt; 0.10 gate was WD-calibrated; Sat/Sun have a <b>data-intrinsic ceiling</b> &mdash; the "
              "2022 backcast averages observed + synthetic-2022 rows, and Step-4 augmentation carries a "
              "systematic weekend AT_HOME bias (~+5&ndash;6 pp Sat/Sun; upstream of Step 6, unremovable by "
              "Step-6 tuning)",
        nonblocker="WD backcast <b>0.0630 PASS</b> the strict &lt; 0.10; weekend <b>activity-mix</b> only; "
                    "occupancy intact",
        fig="F_S5 / §4 overlay",
    ),
]

_rows_html = "".join(
    f"<tr><td>{r['dev']}</td><td>{r['gate']}</td><td>{r['obs']}</td><td>{r['basis']}</td>"
    f"<td>{r['nonblocker']}</td><td>{r['fig']}</td></tr>"
    for r in DEVIATIONS_TABLE_ROWS
)

DISPOSITION_PANEL = (
    '<div style="border:2px solid #f9a825;background:#fffde7;border-radius:6px;'
    'padding:14px 16px;margin:16px 0;font-size:13px;line-height:1.5;color:#3e3418">'
    '<h3 style="margin:0 0 8px 0;color:#8d6e00;font-size:15px;">Documented deviations &mdash; '
    'disposition (Option A)</h3>'
    '<p style="margin:0 0 10px 0;">Three Step-6 gates ship as PASS under a documented deviation rather '
    'than the original strict threshold. <b>Disposition = Option A:</b> relabel + document each as an '
    '<b>EXPECTED / documented deviation</b>, keep the strict gate visible alongside the observed value, '
    '<b>do not re-threshold</b>. No silent goalpost-moving.</p>'
    '<div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;font-size:12px;margin:8px 0">'
    '<thead><tr>'
    '<th style="background:#f9a825;color:#fff;padding:6px 8px;text-align:left">Deviation</th>'
    '<th style="background:#f9a825;color:#fff;padding:6px 8px;text-align:left">Strict gate</th>'
    '<th style="background:#f9a825;color:#fff;padding:6px 8px;text-align:left">Observed</th>'
    '<th style="background:#f9a825;color:#fff;padding:6px 8px;text-align:left">Basis (why the deviation is '
    'expected/defensible)</th>'
    '<th style="background:#f9a825;color:#fff;padding:6px 8px;text-align:left">BEM-non-blocker</th>'
    '<th style="background:#f9a825;color:#fff;padding:6px 8px;text-align:left">Evidence fig</th>'
    '</tr></thead><tbody style="background:#fffef5">' + _rows_html.replace(
        "<td>", '<td style="padding:6px 8px;border-bottom:1px solid #f0e2a0;vertical-align:top">'
    ) + '</tbody></table></div>'
    '<p style="margin:10px 0 4px 0"><b>&sect;3 hygiene note:</b> the validator computes '
    '<code>covid_signal_pp</code> (source line ~253) but <b>never uses it</b> &mdash; the shipped &sect;3 '
    '&ldquo;0.2 pp&rdquo; is a <i>separately-hardcoded</i> value. The redefinition is defensible and '
    'documented; wiring the check to the computed <code>covid_signal_pp</code> is a validator-hygiene '
    'follow-up for the next validator regeneration.</p>'
    '<p style="margin:4px 0 0 0"><b>Disposition:</b> strict gates are kept visible; the three are '
    '<b>relabelled EXPECTED / documented deviations</b>, not re-thresholded. A Step-4 J3 retrain (tracked '
    'separately) would let Bundle-3.18 &ldquo;Path A&rdquo; close &sect;4 and possibly &sect;2 Sat.</p>'
    '</div>'
)

print("[4] disposition panel HTML built (3-row table + 2 notes).")

# ══════════════════════════════════════════════════════════════════════════
# 5. INJECT — panel after the CANONICAL POPULATION banner; WFH figure in §5
# ══════════════════════════════════════════════════════════════════════════
new_html = insert_after(html, "CANONICAL POPULATION", "\n</div>\n", DISPOSITION_PANEL)
print("[5a] injected disposition panel right after the CANONICAL POPULATION banner.")

wfh_caption = (
    f"<b>DIAGNOSTIC &mdash; informational, not a gate.</b> &sect;5.5 WFH was never wired as a validator "
    f"check (Improvement 2 finding). WD (weekday, DDAY_STRATA=1) person-slot share where "
    f"act30={PAID_WORK_CODE} (&ldquo;Work &amp; Related&rdquo;, confirmed from <code>02_harmonizeGSS.py</code> "
    f"<code>ACT_LABELS</code> and independently from <code>02_harmonizationGSS_actCodes.md</code>; "
    f"<code>06_forecast_rake.py</code>'s <code>HOME_ACTS</code> code 2 = &ldquo;HH Work&rdquo; is household "
    f"work, not paid employment, ruling out that ambiguity) AND hom30=1 (at home): "
    f"<b>2030 calibrated (canonical) = {d2030['rate_pct']:.2f}%</b> vs "
    f"<b>2022 backcast (model reconstruction, <i>not</i> observed 2022) = {d2022['rate_pct']:.2f}%</b> "
    f"(&Delta; = {delta_pp:+.2f} pp). A hard gate vs <i>observed</i> 2022 is <b>deferred</b> to the next "
    f"validator pass &mdash; it needs the 530 MB <code>augmented_diaries.csv</code> read plus a validator "
    f"edit, both out of scope for this report-only pass."
)
wfh_block = fig_block(
    "DIAGNOSTIC &mdash; WD work-from-home rate, 2030 calibrated vs 2022 backcast (not a gate)",
    wfh_caption, F_WFH, AMBER,
)
new_html = insert_before(
    new_html,
    "F_S5 · Each §5 metric vs its pass band (supplementary)",
    "\n            </div>\n            <div class=\"section\">\n              <h2>6 — BEM Output Readiness</h2>",
    wfh_block,
)
print("[5b] injected WFH diagnostic figure into §5, after F_S5.")

N_IMG_AFTER = new_html.count("data:image/png;base64,")
if N_IMG_AFTER != N_IMG_BEFORE + 1:
    sys.exit(f"ABORT: expected {N_IMG_BEFORE + 1} images after injection, found {N_IMG_AFTER}. "
              f"No file written.")

# Idempotency marker — inserted last, right after <body> (alongside the Improvement-3 marker)
new_html = new_html.replace("<body>", f"<body>\n{MARKER}", 1)

# Sanity: tally / banner / prior marker must be byte-unchanged substrings
for must_have in ["35/35 checks passed", "CANONICAL POPULATION", PRIOR_MARKER]:
    if must_have not in new_html:
        sys.exit(f"ABORT (post-injection check): '{must_have}' missing from the new HTML. No file written.")

REPORT.write_text(new_html, encoding="utf-8")
print(f"\n[OK] wrote {REPORT}")
print(f"     before: {N_IMG_BEFORE} figures.  after: {N_IMG_AFTER} figures "
      f"(+1 WFH diagnostic). Disposition panel injected. Banner/35/35/prior-marker preserved.")
print("=== DONE ===")
