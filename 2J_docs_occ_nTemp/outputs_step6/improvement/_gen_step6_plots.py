"""
_gen_step6_plots.py
Step-6 Improvement 3 — captions + 4 new figures (F_S2, F_S3, F_S5, F_S6), injected into the canonical
(joint-raked, CANONICAL POPULATION banner) step6_validation_report.html.

Mirrors the base64-figure-injection mechanism of
outputs_step5/_gen_step5_v2_plots.py: matplotlib -> base64 PNG data-URI ->
string-injected <img> at anchor tokens in the existing HTML. Idempotent
(guarded by an HTML comment marker) and self-contained (no external files/CDN).

Does NOT modify the validator (06_longitudinalForecastingGSS_val.py),
06_forecast_rake.py, or any eSim_*.py file. Does NOT re-run the validator —
the 35/35 tally text is left untouched; only <img>/caption HTML is injected.

What this script does:
  1. Archives the current (pre-figure) canonical report to
     previous/step6_validation_report_jointraked_prefig_20260710.html
     (byte-identical copy, made BEFORE any edit; skipped if already present).
  2. Adds a caption <div> under each of the 6 existing base64 <img> figures
     (S1 Training Convergence, S2 True-Future-Test, S3 DRIFT_MATRIX heatmaps,
     S4 2022 Backcasting overlay, S5 2030 Plausibility overlay, S7 Drift
     Summary bar) plus an `alt` attribute on each <img>.
  3. Adds 3 new figures:
       F_S2 - TFT JS bars redrawn with the CORRECT per-stratum gate (WD 0.20,
              Sat/Sun 0.22) since the original chart only draws one 0.20 line.
       F_S3 - WD (strata=1) per-activity JS divergence, DRIFT_MATRIX_1015 vs
              _1522 (the COVID-spanning transition), with the live re-derived
              mean delta — explicitly distinguished from the report's
              separately-hardcoded "0.2pp" (see caption; this is a real
              finding, not decoration: covid_signal_pp is computed in the
              validator source at L253 but never surfaces in any check).
       F_S5 - compact panel: each S5 plausibility metric plotted against its
              pass band, from the report's own printed numbers.
  4. Adds Section 6's FIRST chart: DDAY_STRATA distribution (WD/Sat/Sun) in
     the 2030 calibrated (joint-raked) population, with schema-readiness
     facts annotated (37,008 rows >= 37,000; act30 in {1..14}; hom30 in {0,1}).

Data sources (small files only, per task instructions):
  - 2030_synthetic_diaries_joint_raked.csv (~11 MB, 37,008 rows) for the
    Section-6 DDAY_STRATA chart (one column groupby + a schema re-check).
  - DRIFT_MATRIX_1015.csv / DRIFT_MATRIX_1522.csv (tiny, 43 rows each) for
    the F_S3 COVID-window comparison.
  - F_S2 / F_S5 use ONLY the numbers already printed in the report's own
    section tables (no file read) — same house rule as Step-5 Improvement 2.
  - augmented_diaries.csv (530 MB) is NEVER read by this script.

Run once (idempotent thereafter):
    py 2J_docs_occ_nTemp/outputs_step6/improvement/_gen_step6_plots.py
"""

from __future__ import annotations

import base64
import io
import re
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
JOINT_RAKED  = FORECAST_DIR / "2030_synthetic_diaries_joint_raked.csv"
DRIFT_1015   = FORECAST_DIR / "DRIFT_MATRIX_1015.csv"
DRIFT_1522   = FORECAST_DIR / "DRIFT_MATRIX_1522.csv"

STEP6_DIR = BASE / "2J_docs_occ_nTemp" / "outputs_step6"
REPORT    = STEP6_DIR / "step6_validation_report.html"          # source AND destination (in place)
PREV_DIR  = STEP6_DIR / "previous"
ARCHIVE   = PREV_DIR / "step6_validation_report_jointraked_prefig_20260710.html"

ACT_COLS = [f"act30_{i:03d}" for i in range(1, 49)]
HOM_COLS = [f"hom30_{i:03d}" for i in range(1, 49)]

MARKER = "<!-- STEP6_FIGURES_V1: captions + 3 new figures injected by _gen_step6_plots.py -->"

# ── Theme — light, matching the existing report's inline style exactly ─────
BLUE, GREEN, ORANGE, RED, PURPLE, TEAL = (
    "#1976d2", "#388e3c", "#e65100", "#c62828", "#7b1fa2", "#00838f")
NAVY = "#283593"
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


def cap_only(html_text: str) -> str:
    """Caption-only div for an EXISTING figure (no new chart)."""
    return (f'<div class="cap" style="background:#eef2fb;border-left:3px solid {NAVY};'
            f'border-radius:4px;padding:8px 12px;margin:6px 0 14px 0;font-size:12.5px;'
            f'color:#333;line-height:1.55;">{html_text}</div>')


def fig_block(title: str, caption_html: str, b64: str, accent: str = NAVY) -> str:
    """A titled, captioned NEW figure block (supplementary or Section-6 first chart)."""
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
    "<h2>1 — Training Convergence</h2>",
    "<h2>2 — True Future Test</h2>",
    "<h2>3 — DRIFT_MATRIX Plausibility</h2>",
    "<h2>4 — 2022 Backcasting Reconstruction</h2>",
    "<h2>5 — 2030 Schedule Plausibility</h2>",
    "<h2>6 — BEM Output Readiness</h2>",
    "<h2>7 — 2030 Drift Summary (2022→2030)</h2>",
    "CANONICAL POPULATION",
    "<body>",
]
missing = [a for a in REQUIRED_ANCHORS if a not in html]
if missing:
    sys.exit(f"ABORT: required anchor(s) not found — {missing}. No file written.")

IMG_RE = re.compile(
    r'<img src="data:image/png;base64,[A-Za-z0-9+/=]+" style="max-width:100%;margin:12px 0"/>'
)
n_imgs = len(IMG_RE.findall(html))
if n_imgs != 6:
    sys.exit(f"ABORT: expected exactly 6 existing <img> figures, found {n_imgs}. No file written.")

print("[0] anchors OK: 7 section headers + banner + body tag present; 6 existing <img> figures found.")

# ══════════════════════════════════════════════════════════════════════════
# 1. Archive the pre-figure canonical report FIRST (byte-identical)
# ══════════════════════════════════════════════════════════════════════════
PREV_DIR.mkdir(exist_ok=True)
if not ARCHIVE.exists():
    shutil.copy2(REPORT, ARCHIVE)
    print(f"[1] archived pre-figure report -> {ARCHIVE}")
else:
    print(f"[1] archive already present, leaving as-is -> {ARCHIVE}")

# ══════════════════════════════════════════════════════════════════════════
# 2. DATA for the 3 new figures
# ══════════════════════════════════════════════════════════════════════════
print("\n=== Re-derived data for new figures (small files only; no augmented_diaries.csv read) ===")

# ---- F_S3 data: WD per-activity JS, DRIFT_MATRIX_1015 vs _1522 (COVID window) ----
d1015 = pd.read_csv(DRIFT_1015)
d1522 = pd.read_csv(DRIFT_1522)
wd1015 = d1015[d1015["strata"] == 1].set_index("activity")["js_divergence"].sort_index()
wd1522 = d1522[d1522["strata"] == 1].set_index("activity")["js_divergence"].sort_index()
acts = sorted(set(wd1015.index) | set(wd1522.index))
v1015 = [float(wd1015.get(a, np.nan)) for a in acts]
v1522 = [float(wd1522.get(a, np.nan)) for a in acts]
mean1015_pct = float(wd1015.mean()) * 100
mean1522_pct = float(wd1522.mean()) * 100
covid_delta_pp = mean1522_pct - mean1015_pct
print(f"[2a] F_S3: WD mean JS 2010->2015 = {mean1015_pct:.4f}%  |  2015->2022 = {mean1522_pct:.4f}%  "
      f"|  live delta = {covid_delta_pp:+.4f}pp  (report's own printed 3.7 value is a DIFFERENT, "
      f"hardcoded quantity — 0.2pp — see caption)")

# ---- Section-6 data: DDAY_STRATA distribution + schema re-check, joint-raked file ----
df30 = pd.read_csv(JOINT_RAKED)
n_rows = len(df30)
strata_counts = df30["DDAY_STRATA"].value_counts().sort_index()
STRATA_LABEL = {1: "WD", 2: "Sat", 3: "Sun"}
strata_order = [1, 2, 3]
counts = [int(strata_counts.get(s, 0)) for s in strata_order]
shares = [c / n_rows * 100 for c in counts]
act_vals = df30[ACT_COLS].values
act_min, act_max = int(act_vals.min()), int(act_vals.max())
hom_vals = sorted(pd.unique(df30[HOM_COLS].values.ravel()))
print(f"[2b] Section-6: n_rows={n_rows:,}  counts(WD/Sat/Sun)={counts}  shares%={[round(s,2) for s in shares]}  "
      f"act30 range=[{act_min},{act_max}]  hom30 values={hom_vals}")

# ══════════════════════════════════════════════════════════════════════════
# 3. BUILD FIGURES
# ══════════════════════════════════════════════════════════════════════════

# ── F_S2 — TFT bars with the CORRECT per-stratum gate drawn ────────────────
strata_labels = ["WD", "Sat", "Sun"]
p2 = [0.0811, 0.2040, 0.1938]   # Phase 2: W_2010_ft on 2015-unseen (report table, checks 2.1)
p3 = [0.0619, 0.1817, 0.1843]   # Phase 3: W_2015_ft on 2022-unseen (report table, checks 2.2)
gates = [0.20, 0.22, 0.22]      # WD kept at 0.20; Sat/Sun widened to 0.22 (report note)
x = np.arange(3)
fig, ax = plt.subplots(figsize=(6.8, 3.7))
ax.bar(x - 0.2, p2, width=0.35, label="Phase 2 (W_2010_ft on 2015 unseen)", color=BLUE)
ax.bar(x + 0.2, p3, width=0.35, label="Phase 3 (W_2015_ft on 2022 unseen)", color=GREEN)
for xi, g in zip(x, gates):
    ax.plot([xi - 0.42, xi + 0.42], [g, g], color=RED, linestyle="--", linewidth=1.8)
ax.text(0, 0.205, "gate 0.20", color=RED, fontsize=8, ha="center", va="bottom")
ax.text(1.5, 0.225, "gate 0.22 (Sat/Sun, widened)", color=RED, fontsize=8, ha="center", va="bottom")
ax.annotate("Sat Phase-2 = 0.2040\n(+0.4pp over the original 0.20;\nclears the widened 0.22 gate)",
            xy=(1 - 0.2, 0.2040), xytext=(1.55, 0.14),
            arrowprops=dict(arrowstyle="->", color=ORANGE), fontsize=8, color=ORANGE)
ax.set_xticks(x); ax.set_xticklabels(strata_labels)
ax.set_ylabel("True Future Test JS")
ax.set_title("F_S2 · TFT JS with the correct per-stratum gate (supplements §2's single-gate chart)",
              fontsize=10.5)
ax.legend(fontsize=8, loc="upper left")
ax.set_ylim(0, 0.28)
plt.tight_layout()
F_S2 = _b64(fig)

# ── F_S3 — WD per-activity JS: pre- vs COVID-spanning transition ───────────
fig, ax = plt.subplots(figsize=(9.5, 3.9))
xi = np.arange(len(acts))
ax.bar(xi - 0.2, v1015, width=0.38, label="2010→2015 (pre-COVID)", color=BLUE)
ax.bar(xi + 0.2, v1522, width=0.38, label="2015→2022 (COVID-spanning)", color=RED)
ax.axhline(wd1015.mean(), color=BLUE, linestyle=":", linewidth=1.3)
ax.axhline(wd1522.mean(), color=RED, linestyle=":", linewidth=1.3)
ax.set_xticks(xi); ax.set_xticklabels([f"act{a}" for a in acts], fontsize=8)
ax.set_ylabel("WD (strata=1) JS divergence")
ax.set_title(f"F_S3 · WD activity-mix drift, pre- vs COVID-spanning transition — "
             f"live mean Δ = {covid_delta_pp:+.4f}pp", fontsize=10.5)
ax.legend(fontsize=8)
plt.tight_layout()
F_S3 = _b64(fig)

# ── F_S5 — each §5 metric vs its band, from the report's own printed numbers ─
metrics = [
    ("5.1 AT_HOME overall", 79.6959, 55, 90, "band"),
    ("5.3 Night sleep ≥70%", 75.7948, 70, 100, "floor"),
    ("5.4 Max act. share <60%", 38.0003, 0, 60, "ceiling"),
    ("5.6 WD continuity Δ ≤15pp", 4.2099, 0, 15, "ceiling"),
]
fig, axes = plt.subplots(1, 5, figsize=(13, 3.1))
for ax, (label, val, lo, hi, kind) in zip(axes[:4], metrics):
    ax.axhspan(lo, hi, color=GREEN, alpha=0.15)
    ax.bar([0], [val], width=0.5, color=BLUE)
    ax.axhline(hi if kind != "floor" else lo, color=RED, linestyle="--", linewidth=1.2)
    ax.set_xticks([]); ax.set_title(label, fontsize=8.5)
    ax.set_ylim(0, max(hi, val) * 1.25)
    ax.text(0, val + max(hi, val) * 0.03, f"{val:.2f}", ha="center", fontsize=8.5, fontweight="bold")
ax5 = axes[4]
ax5.bar([0, 1], [78.4, 80.3], width=0.5, color=[BLUE, GREEN])
ax5.set_xticks([0, 1]); ax5.set_xticklabels(["WD", "WE"], fontsize=8.5)
ax5.set_title("5.2 WD < WE", fontsize=8.5)
for xi2, v in zip([0, 1], [78.4, 80.3]):
    ax5.text(xi2, v + 2, f"{v:.1f}%", ha="center", fontsize=8.5, fontweight="bold")
ax5.set_ylim(0, 100)
fig.suptitle("F_S5 · Each §5 plausibility metric vs its pass band (all PASS)", fontsize=11, y=1.04)
plt.tight_layout()
F_S5 = _b64(fig)

# ── F_S6 — DDAY_STRATA distribution in the calibrated 2030 population ──────
fig, ax = plt.subplots(figsize=(7.2, 4.0))
colors = [BLUE, GREEN, ORANGE]
bars = ax.bar([STRATA_LABEL[s] for s in strata_order], counts, color=colors, edgecolor="white")
for b, c, sh in zip(bars, counts, shares):
    ax.text(b.get_x() + b.get_width() / 2, c + n_rows * 0.01, f"{c:,}\n({sh:.1f}%)",
            ha="center", va="bottom", fontsize=9)
ax.set_ylabel("Rows")
ax.set_title("F_S6 · DDAY_STRATA distribution — 2030 calibrated population\n"
             "(2030_synthetic_diaries_joint_raked.csv)", fontsize=10.5)
ax.set_ylim(0, max(counts) * 1.22)
txt = (f"n = {n_rows:,} rows (≥37,000, check 6.5)\n"
       f"act30 range = [{act_min},{act_max}] (check 6.3)\n"
       f"hom30 values = {hom_vals} (check 6.4)\n"
       f"all 3 strata present (check 6.6)")
ax.text(0.98, 0.97, txt, transform=ax.transAxes, ha="right", va="top", fontsize=8.5,
        bbox=dict(boxstyle="round", facecolor="#f5f7fb", edgecolor=GREEN, alpha=0.95))
plt.tight_layout()
F_S6 = _b64(fig)

print("\n[3] all 4 new figures rendered (F_S2, F_S3, F_S5, F_S6).")

# ══════════════════════════════════════════════════════════════════════════
# 4. CAPTIONS for the 6 EXISTING figures
# ══════════════════════════════════════════════════════════════════════════
CAP_S1 = cap_only(
    "Bar chart of the five persisted validation-JS checkpoints from Model-2 training: Sub-stage A "
    "(2005) 0.1369, then fine-tune checkpoints 2010_ft 0.1360, 2015_ft 0.1320, 2022_ft 0.1307, and the "
    "pooled 2030 checkpoint 0.1313 (purple). Dashed red = Sub-stage-A gate 0.15 (check 1.1); dotted "
    "orange = pooled gate 0.18 (check 1.2). The max fine-tune JS (0.1360, check 1.3) stays far below "
    "1.5×Sub-A = 0.2053, so no catastrophic forgetting across the three fine-tune phases. "
    "<b>Honesty note:</b> these are persisted training values (log-sourced from "
    "<code>06_longitudinalForecastingGSS.md</code>), not re-derived per-epoch — no per-epoch training-loss "
    "CSV was retained, so this chart plots the five final checkpoint values only, not a convergence curve."
)
CAP_S2 = cap_only(
    "Grouped bars: True-Future-Test JS for Phase 2 (W_2010_ft evaluated on unseen 2015 diaries, blue) and "
    "Phase 3 (W_2015_ft evaluated on unseen 2022 diaries, green), per stratum. The single red dashed line "
    "marks the original 0.20 gate; WD checks 2.1/2.2 (0.0811 / 0.0619) pass it directly. "
    "<b>Note:</b> the Sat/Sun gate was separately widened to 0.22 (not drawn here — see F_S2 below, which "
    "redraws both gates). Sat Phase-2 = 0.2040 is the one value that only clears the widened 0.22 gate "
    "(+0.4pp over the original 0.20, documented deviation); all five other values pass even the stricter "
    "original line."
)
CAP_S3 = cap_only(
    "Three side-by-side heatmaps (activity 1–14 × WD/Sat/Sun) of Jensen-Shannon divergence between "
    "observed and model-predicted activity shares, for the 2005→2010 (left), 2010→2015 (middle), and "
    "2015→2022 (right, spans COVID) transitions. Colour scale 0–0.015 JS. All three matrices are "
    "NaN/Inf-clean (checks 3.1/3.3/3.5) and each has ≥3 weekend activities with drift &gt;0.003 "
    "(checks 3.2b/3.4b/3.6b: 9, 10, 7 respectively). The WD drift&gt;0.001 counts (3.2/3.4/3.6: 1, 2, 1) "
    "are informational only, superseded by gate 3.7. <b>This heatmap does not itself mark a COVID signal — "
    "see F_S3 below</b>, which isolates and re-derives it directly from the matrix data."
)
CAP_S4 = cap_only(
    "48-slot AT_HOME(%) overlay per stratum: solid = observed 2022, dashed = reconstructed 2022 "
    "(Model-2 backcast). WD (blue), Sat (green), Sun (orange) pairs track closely all day. Reconstruction "
    "JS (all 48 slots, activity shares): WD 0.0630 (gate &lt;0.10, check 4.1); Sat 0.1637 and Sun 0.1618 "
    "(both under the re-baselined 0.20 gate — checks 4.2/4.3, originally &lt;0.10, widened after confirming "
    "a data-intrinsic weekend ceiling). WD AT_HOME level Δ = 1.37pp (check 4.4, gate ±2pp)."
)
CAP_S5 = cap_only(
    "48-slot AT_HOME(%) per stratum: solid = 2030 forecast (calibrated, joint-raked), dotted = observed "
    "2022. Headline 2030 plausibility (all PASS): overall AT_HOME 79.70% ∈[55,90] (5.1); WD 78.4% &lt; WE "
    "80.3% (5.2, structural ordering preserved); night-sleep dominance (slots 1–8) 75.79% ≥70% (5.3); "
    "no activity exceeds 60% share (max 38.00%, 5.4); WD AT_HOME continuity vs 2022 Δ=4.21pp, well inside "
    "±15pp (5.6). See F_S5 below for all five metrics plotted against their bands in one panel."
)
CAP_S7 = cap_only(
    "Mean 2022→2030 Jensen-Shannon drift per activity (×10⁻³), averaged across WD/Sat/Sun, from "
    "<code>2030_drift_summary.csv</code> (42 rows = 14 activities × 3 strata, check 7.1; 0 NaN, check 7.2). "
    "All bars sit well under 1×10⁻³ JS — consistent with the section's own note that post-COVID activity "
    "patterns are projected stable to 2030 under the Statistics Canada M1 scenario."
)

ALT = {
    "s1": "Bar chart of val JS per Model-2 training checkpoint against the Sub-A and pooled gates",
    "s2": "Grouped bar chart of True-Future-Test JS per phase and stratum against the 0.20 gate",
    "s3": "Three heatmaps of activity by stratum JS divergence across three GSS-cycle transitions",
    "s4": "Line chart of observed vs reconstructed 2022 AT_HOME percent across 48 slots per stratum",
    "s5": "Line chart of 2030 forecast vs observed 2022 AT_HOME percent across 48 slots per stratum",
    "s7": "Bar chart of mean 2022 to 2030 activity drift JS per activity code",
}

CAPS = {"s1": CAP_S1, "s2": CAP_S2, "s3": CAP_S3, "s4": CAP_S4, "s5": CAP_S5, "s7": CAP_S7}
EXTRA = {
    "s2": fig_block("F_S2 · TFT JS with the correct per-stratum gate (supplementary)",
                     "Same six JS values as the §2 chart, redrawn with the gate that actually applies to "
                     "each stratum (WD 0.20; Sat/Sun 0.22, widened per the weekend-variability finding). "
                     "Only Sat Phase-2 (0.2040) sits in the +0.4pp gap between the two gates — every other "
                     "value clears even the stricter 0.20 line.", F_S2, PURPLE),
    "s3": fig_block("F_S3 · WD activity-mix drift, pre- vs COVID-spanning transition (supplementary)",
                     f"Directly re-derives what the validator's <code>covid_signal_pp</code> computes "
                     f"internally (§3 source, line 253) but never surfaces in any printed check: the mean "
                     f"WD (strata=1) per-activity JS divergence, 2010→2015 vs 2015→2022. Re-derived here "
                     f"from <code>DRIFT_MATRIX_1015.csv</code> / <code>DRIFT_MATRIX_1522.csv</code>: mean WD "
                     f"JS = {mean1015_pct:.4f}% (2010→2015) vs {mean1522_pct:.4f}% (2015→2022), a live delta "
                     f"of {covid_delta_pp:+.4f}pp — i.e. WD activity-mix drift is if anything slightly "
                     f"<b>smaller</b> across the COVID-spanning transition, not larger. "
                     f"<b>Important distinction (verified in source):</b> this is a different quantity from "
                     f"the &ldquo;0.2pp&rdquo; shown in check 3.7 — that number is "
                     f"<code>TRAINING_KNOWN['at_home_residual_pp']</code>, a separately hardcoded, "
                     f"log-sourced value describing the W_2022_ft model's predicted-vs-observed WD AT_HOME "
                     f"(hom30) percentage-point gap, not a value derived from these activity-code drift "
                     f"matrices. The two are not interchangeable; this figure honestly re-derives the "
                     f"matrix-based quantity, it does not re-derive the hardcoded 0.2pp.", F_S3, RED),
    "s5": fig_block("F_S5 · Each §5 metric vs its pass band (supplementary)",
                     "One panel for the whole 2030 sanity story: bars 1–4 show AT_HOME overall, night "
                     "sleep, max activity share, and WD continuity-Δ against their shaded pass bands (red "
                     "dashed = the binding gate); panel 5 shows WD vs WE AT_HOME confirming the structural "
                     "WD&lt;WE ordering (5.2). All five clear their gates.", F_S5, TEAL),
}

# ══════════════════════════════════════════════════════════════════════════
# 5. INJECT
# ══════════════════════════════════════════════════════════════════════════
order = ["s1", "s2", "s3", "s4", "s5", "s7"]   # doc order of the 6 existing <img> figures
_counter = {"i": 0}


def _repl(m: re.Match) -> str:
    key = order[_counter["i"]]
    _counter["i"] += 1
    b64 = m.group(0).split("base64,", 1)[1].split('"', 1)[0]
    new_img = (f'<img src="data:image/png;base64,{b64}" alt="{ALT[key]}" '
               f'style="max-width:100%;margin:12px 0"/>')
    out = new_img + "\n" + CAPS[key]
    if key in EXTRA:
        out += "\n" + EXTRA[key]
    return out


new_html, n_subs = IMG_RE.subn(_repl, html)
if n_subs != 6:
    sys.exit(f"ABORT: substitution matched {n_subs} images, expected 6. No file written.")
print(f"[4] captioned + alt-tagged {n_subs} existing figures; injected 3 supplementary figures "
      f"(F_S2 in §2, F_S3 in §3, F_S5 in §5).")

# Section 6 — first chart, inserted right after its (currently empty) table
sec6_block = fig_block(
    "F_S6 · DDAY_STRATA distribution — first chart for §6 (new)",
    f"Bar chart of the DDAY_STRATA distribution in the 2030 calibrated population "
    f"(<code>2030_synthetic_diaries_joint_raked.csv</code>, {n_rows:,} rows): "
    f"WD {counts[0]:,} ({shares[0]:.1f}%), Sat {counts[1]:,} ({shares[1]:.1f}%), "
    f"Sun {counts[2]:,} ({shares[2]:.1f}%). Schema-readiness facts re-confirmed directly from this file: "
    f"row count {n_rows:,} ≥ 37,000 (check 6.5), act30 ∈ [{act_min},{act_max}] (check 6.3), "
    f"hom30 values = {hom_vals} (check 6.4), and all three strata present (check 6.6).",
    F_S6, GREEN,
)
new_html = insert_after(new_html, "<h2>6 — BEM Output Readiness</h2>", "</table>", sec6_block)
print("[5] injected §6's first chart (F_S6) after the existing empty-chart slot.")

# Idempotency marker — inserted last, right after <body>
new_html = new_html.replace("<body>", f"<body>\n{MARKER}", 1)

REPORT.write_text(new_html, encoding="utf-8")
print(f"\n[OK] wrote {REPORT}")
print(f"     before: 6 figures, 0 captions.  after: 10 figures (6 captioned-existing + 4 new: "
      f"F_S2, F_S3, F_S5, F_S6), incl. §6's first-ever chart (F_S6).")
print("=== DONE ===")
