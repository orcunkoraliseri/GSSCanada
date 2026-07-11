"""
_gen_step6_names.py
Step-6 Improvement 3 addendum — activity code -> NAME relabeling.

Adds a code->name legend table (safety net) and swaps in-place the three
figures whose axes show bare act30 codes (1-14), so they show activity
NAMES instead, in the canonical (joint-raked, CANONICAL POPULATION banner,
35/35 PASS, 11-figure incl. WFH diagnostic) step6_validation_report.html.

Mirrors the base64/HTML-injection mechanism of _gen_step6_plots.py
(Improvement 3) and _gen_step6_panel.py (Improvement 4) in this same
directory: matplotlib -> base64 PNG data-URI -> string-injected HTML at
anchor tokens, guarded by its own idempotency marker, byte-identical
predecessor archived first. Does NOT modify the validator
(06_longitudinalForecastingGSS_val.py), 06_forecast_rake.py, or any
eSim_*.py file, and does NOT re-run the validator — the 35/35 tally text,
the CANONICAL POPULATION banner, and the disposition panel are left
byte-untouched; this script only (a) inserts one new HTML block (the
legend table) and (b) swaps the base64 payload of 3 existing <img> tags
in place (figure COUNT unchanged: 11 before, 11 after).

ACT_LABELS -- CONFIRMED, not re-derived (per task instructions):
  `02_harmonizeGSS.py` ACT_LABELS, lines 354-369 -- the canonical
  14-category act30 scheme, copied verbatim below.

Figures relabeled (bare act30 codes -> ACT_LABELS names on-axis):
  - S3 (existing, Section 3): 3-panel DRIFT_MATRIX heatmap, y-axis was
    f"act{i}" -> now the ACT_LABELS name. Source: DRIFT_MATRIX_0510/1015/
    1522.csv (tiny, 43 rows each) -- same 3 files + same pivot_table logic
    the validator itself uses (06_longitudinalForecastingGSS_val.py
    L258-275), so the plotted VALUES are unchanged, only the y-tick text.
  - S7 (existing, Section 7): 2030 drift-summary bar chart, x-axis was
    mean_js.index.astype(str) (bare codes) -> now ACT_LABELS names.
    Source: 2030_drift_summary.csv (tiny, 42 rows) -- same groupby-mean
    logic the validator uses (L457-462), values unchanged, only x-tick text.
  - F_S3 (Improvement-3's own supplementary figure, Section 3): WD
    per-activity JS bars, x-axis was f"act{a}" -> now ACT_LABELS names.
    Source: DRIFT_MATRIX_1015.csv / DRIFT_MATRIX_1522.csv, same computation
    as _gen_step6_plots.py used (live mean delta re-derived and printed for
    cross-check against the figure's own on-report caption).

Figures with NO activity axis (F_S2 TFT phases, F_S5 metric panel, F_S6
DDAY, S1 training, S2 TFT, S4/S5 AT_HOME overlays, WFH diagnostic) are
untouched -- confirmed by reading 06_longitudinalForecastingGSS_val.py in
full: no "top-5 activity" bar chart exists anywhere in Section 4 or
Section 5 of the validator (grepped for head/nlargest/value_counts -- zero
matches), so that item from the task has nothing to regenerate; the
legend table + existing captions cover it.

Data sources (small files only; augmented_diaries.csv, 530 MB, is NEVER
read):
  - DRIFT_MATRIX_0510.csv / _1015.csv / _1522.csv (tiny, 43 rows each)
  - 2030_drift_summary.csv (tiny, 43 rows incl. header)

Run once (idempotent thereafter):
    py 2J_docs_occ_nTemp/outputs_step6/improvement/_gen_step6_names.py
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
BASE          = Path(r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main")
FORECAST_DIR  = BASE / "0_Occupancy" / "Outputs_21CEN22GSS" / "forecast_2030"
DRIFT_0510    = FORECAST_DIR / "DRIFT_MATRIX_0510.csv"
DRIFT_1015    = FORECAST_DIR / "DRIFT_MATRIX_1015.csv"
DRIFT_1522    = FORECAST_DIR / "DRIFT_MATRIX_1522.csv"
DRIFT_SUMMARY = FORECAST_DIR / "2030_drift_summary.csv"

STEP6_DIR = BASE / "2J_docs_occ_nTemp" / "outputs_step6"
REPORT    = STEP6_DIR / "step6_validation_report.html"          # source AND destination (in place)
PREV_DIR  = STEP6_DIR / "previous"
ARCHIVE   = PREV_DIR / "step6_validation_report_prenames_20260710.html"

STRATUM_LABEL = {1: "WD", 2: "Sat", 3: "Sun"}

# ACT_LABELS — verbatim from 02_harmonizeGSS.py L354-369 (CONFIRMED, do not re-derive)
ACT_LABELS = {
    1: "Work & Related",
    2: "Household Work & Maintenance",
    3: "Caregiving & Help",
    4: "Purchasing Goods & Services",
    5: "Sleep & Naps & Resting",
    6: "Eating & Drinking",
    7: "Personal Care",
    8: "Education",
    9: "Socializing",
    10: "Passive Leisure",
    11: "Active Leisure",
    12: "Community & Volunteer",
    13: "Travel",
    14: "Miscellaneous / Idle",
}

MARKER = ("<!-- STEP6_NAMES_V1: activity code -> name legend + renamed-axis "
          "figures injected by _gen_step6_names.py -->")
PRIOR_MARKER_3 = "STEP6_FIGURES_V1"   # _gen_step6_plots.py must have already run
PRIOR_MARKER_4 = "STEP6_PANEL_V1"     # _gen_step6_panel.py must have already run

S3_ALT  = "Three heatmaps of activity by stratum JS divergence across three GSS-cycle transitions"
S7_ALT  = "Bar chart of mean 2022 to 2030 activity drift JS per activity code"
FS3_ALT = "F_S3 · WD activity-mix drift, pre- vs COVID-spanning transition (supplementary)"
DISPOSITION_END_ANCHOR = "possibly &sect;2 Sat.</p></div>"

BLUE, RED = "#1976d2", "#c62828"
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


# ══════════════════════════════════════════════════════════════════════════
# 0. Idempotency guard — check BEFORE any heavy work
# ══════════════════════════════════════════════════════════════════════════
if not REPORT.exists():
    sys.exit(f"ABORT: report not found: {REPORT}")

html = REPORT.read_text(encoding="utf-8")

if MARKER in html:
    print(f"[IDEMPOTENT] marker already present in {REPORT.name} — 0 insertions, nothing to do.")
    sys.exit(0)

REQUIRED_ANCHORS = [
    PRIOR_MARKER_3,
    PRIOR_MARKER_4,
    "CANONICAL POPULATION",
    "35/35 checks passed",
    DISPOSITION_END_ANCHOR,
    f'alt="{S3_ALT}"',
    f'alt="{S7_ALT}"',
    f'alt="{FS3_ALT}"',
    "<body>",
]
missing = [a for a in REQUIRED_ANCHORS if a not in html]
if missing:
    sys.exit(f"ABORT: required anchor(s) not found — {missing}. No file written. "
              f"(Run _gen_step6_plots.py and _gen_step6_panel.py first if their markers are missing.)")

N_IMG_BEFORE = html.count("data:image/png;base64,")
if N_IMG_BEFORE != 11:
    sys.exit(f"ABORT: expected exactly 11 existing <img> figures (post-Improvement 3+4), "
              f"found {N_IMG_BEFORE}. No file written.")

print(f"[0] anchors OK: prior markers, banner, 35/35 tally, disposition-panel end, "
      f"S3/S7/F_S3 alt-texts all present; {N_IMG_BEFORE} existing <img> figures found.")

# ══════════════════════════════════════════════════════════════════════════
# 1. Archive the pre-names canonical report FIRST (byte-identical)
# ══════════════════════════════════════════════════════════════════════════
PREV_DIR.mkdir(exist_ok=True)
if not ARCHIVE.exists():
    shutil.copy2(REPORT, ARCHIVE)
    print(f"[1] archived pre-names report -> {ARCHIVE}")
else:
    print(f"[1] archive already present, leaving as-is -> {ARCHIVE}")

# ══════════════════════════════════════════════════════════════════════════
# 2. LEGEND TABLE — the safety net (14 code<->name pairs)
# ══════════════════════════════════════════════════════════════════════════
legend_rows = "".join(
    f'<tr><td style="padding:4px 10px;border-bottom:1px solid #e0e0e0;font-weight:bold;'
    f'text-align:center;color:#37474f">{code}</td>'
    f'<td style="padding:4px 10px;border-bottom:1px solid #e0e0e0">{name}</td></tr>'
    for code, name in sorted(ACT_LABELS.items())
)
LEGEND_TABLE = (
    '<div style="border:1px solid #b0bec5;background:#fafbfc;border-radius:6px;'
    'padding:14px 16px;margin:16px 0;font-size:13px;color:#222">'
    '<h3 style="margin:0 0 8px 0;color:#37474f;font-size:14.5px;">Activity code &rarr; name legend '
    '(act30, 14 categories)</h3>'
    '<p style="margin:0 0 8px 0;font-size:12px;color:#555">The canonical 14-category activity scheme '
    'used throughout this report (act30 codes 1&ndash;14). Source: <code>02_harmonizeGSS.py</code> '
    '<code>ACT_LABELS</code> (lines 354&ndash;369), confirmed verbatim. Any figure or table cell below '
    'that shows a bare activity code can be decoded here.</p>'
    '<div style="overflow-x:auto"><table style="border-collapse:collapse;font-size:12.5px;min-width:380px">'
    '<thead><tr>'
    '<th style="background:#37474f;color:#fff;padding:5px 10px;text-align:center">Code</th>'
    '<th style="background:#37474f;color:#fff;padding:5px 10px;text-align:left">Activity name</th>'
    '</tr></thead><tbody style="background:#ffffff">' + legend_rows + '</tbody></table></div>'
    '</div>'
)
print(f"[2] legend table built: {len(ACT_LABELS)} code<->name rows.")

# ══════════════════════════════════════════════════════════════════════════
# 3. REGENERATE S3 — DRIFT_MATRIX heatmap, y-axis = activity NAMES
#    (same 3 files + same pivot_table logic as the validator itself,
#     06_longitudinalForecastingGSS_val.py L258-275 — values unchanged,
#     only the y-tick text changes from f"act{i}" to the ACT_LABELS name)
# ══════════════════════════════════════════════════════════════════════════
d0510 = pd.read_csv(DRIFT_0510)
d1015 = pd.read_csv(DRIFT_1015)
d1522 = pd.read_csv(DRIFT_1522)
dm_dict = {"DRIFT_MATRIX_0510": d0510, "DRIFT_MATRIX_1015": d1015, "DRIFT_MATRIX_1522": d1522}

fig, axes = plt.subplots(1, 3, figsize=(13, 5.2), sharey=True)
for ax, (name, dm) in zip(axes, dm_dict.items()):
    pivot = dm.pivot_table(index="activity", columns="strata", values="js_divergence")
    pivot.columns = [STRATUM_LABEL.get(c, c) for c in pivot.columns]
    im = ax.imshow(pivot.values, aspect="auto", cmap="YlOrRd", vmin=0, vmax=0.015)
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, fontsize=9)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels([ACT_LABELS.get(int(i), f"act{i}") for i in pivot.index], fontsize=7.5)
    ax.set_title(name.replace("DRIFT_MATRIX_", "Drift "), fontsize=9)
    plt.colorbar(im, ax=ax, shrink=0.7)
fig.suptitle("DRIFT_MATRIX JS divergence (14 activities × 3 strata) — activity NAMES", fontsize=10)
plt.tight_layout()
S3_B64_NEW = _b64(fig)
print(f"[3] S3 heatmap regenerated: y-axis relabeled act1..act14 -> ACT_LABELS names "
      f"({len(dm_dict)} matrices, same DRIFT_MATRIX_0510/1015/1522.csv the original chart read; "
      f"pivot values unchanged, cross-checked pivot shape = {pivot.shape} per matrix).")

# ══════════════════════════════════════════════════════════════════════════
# 4. REGENERATE S7 — 2030 drift-summary bar, x-axis = activity NAMES
#    (same groupby-mean logic as the validator, L457-462 — values unchanged,
#     only the x-tick text changes from bare codes to ACT_LABELS names)
# ══════════════════════════════════════════════════════════════════════════
drift_summary = pd.read_csv(DRIFT_SUMMARY)
mean_js = drift_summary.groupby("activity")["js_divergence"].mean().sort_values(ascending=False)
labels7 = [ACT_LABELS.get(int(a), str(a)) for a in mean_js.index]

fig, ax = plt.subplots(figsize=(11, 4.6))
ax.bar(labels7, mean_js.values * 1000, color=BLUE)
ax.set_xlabel("Activity"); ax.set_ylabel("Mean JS (×10⁻³)")
ax.set_title("2022→2030 activity drift: mean JS per activity (across WD/Sat/Sun)")
plt.setp(ax.get_xticklabels(), rotation=40, ha="right", fontsize=8.5)
plt.tight_layout()
S7_B64_NEW = _b64(fig)
print(f"[4] S7 bar chart regenerated: x-axis relabeled bare codes -> ACT_LABELS names "
      f"(highest-drift activity: '{labels7[0]}' at {mean_js.values[0]*1000:.4f}×10⁻³ JS; "
      f"same 2030_drift_summary.csv groupby-mean the original chart used, 42 rows).")

# ══════════════════════════════════════════════════════════════════════════
# 5. REGENERATE F_S3 — WD per-activity JS bars, x-axis = activity NAMES
#    (same computation as _gen_step6_plots.py used for this figure)
# ══════════════════════════════════════════════════════════════════════════
wd1015 = d1015[d1015["strata"] == 1].set_index("activity")["js_divergence"].sort_index()
wd1522 = d1522[d1522["strata"] == 1].set_index("activity")["js_divergence"].sort_index()
acts = sorted(set(wd1015.index) | set(wd1522.index))
v1015 = [float(wd1015.get(a, np.nan)) for a in acts]
v1522 = [float(wd1522.get(a, np.nan)) for a in acts]
mean1015_pct = float(wd1015.mean()) * 100
mean1522_pct = float(wd1522.mean()) * 100
covid_delta_pp = mean1522_pct - mean1015_pct
print(f"[5a] F_S3 recompute cross-check: mean WD JS 2010->2015 = {mean1015_pct:.4f}%  |  "
      f"2015->2022 = {mean1522_pct:.4f}%  |  live delta = {covid_delta_pp:+.4f}pp "
      f"(compare vs the figure's own on-report caption — expect an exact match, since this is the "
      f"identical DRIFT_MATRIX_1015/1522.csv computation _gen_step6_plots.py already performed).")

fig, ax = plt.subplots(figsize=(11, 4.6))
xi = np.arange(len(acts))
ax.bar(xi - 0.2, v1015, width=0.38, label="2010→2015 (pre-COVID)", color=BLUE)
ax.bar(xi + 0.2, v1522, width=0.38, label="2015→2022 (COVID-spanning)", color=RED)
ax.axhline(wd1015.mean(), color=BLUE, linestyle=":", linewidth=1.3)
ax.axhline(wd1522.mean(), color=RED, linestyle=":", linewidth=1.3)
ax.set_xticks(xi)
ax.set_xticklabels([ACT_LABELS.get(a, f"act{a}") for a in acts], fontsize=8.5, rotation=40, ha="right")
ax.set_ylabel("WD (strata=1) JS divergence")
ax.set_title(f"F_S3 · WD activity-mix drift, pre- vs COVID-spanning transition — "
             f"live mean Δ = {covid_delta_pp:+.4f}pp", fontsize=10.5)
ax.legend(fontsize=8)
plt.tight_layout()
FS3_B64_NEW = _b64(fig)
print("[5b] F_S3 regenerated: x-axis relabeled act1..act14 -> ACT_LABELS names.")

# ══════════════════════════════════════════════════════════════════════════
# 6. SWAP the 3 images' base64 payloads in place (anchored on unique alt= text)
# ══════════════════════════════════════════════════════════════════════════

def swap_img(html_text: str, alt_text: str, new_b64: str, label: str) -> str:
    """Replace the base64 payload of the ONE <img alt="alt_text" .../> tag in html_text,
    preserving whatever comes between the alt="" and the closing "/>" (the style attr) verbatim.
    Uses direct string slicing (not re.sub with a replacement string) so base64 content can never
    be misinterpreted as a regex backreference."""
    pattern = re.compile(
        r'<img src="data:image/png;base64,[A-Za-z0-9+/=]+" alt="' + re.escape(alt_text) + r'"([^>]*)/>'
    )
    matches = list(pattern.finditer(html_text))
    if len(matches) != 1:
        sys.exit(f"ABORT: expected exactly 1 <img> match for {label} (alt={alt_text!r}), "
                  f"found {len(matches)}. No file written.")
    m = matches[0]
    tail = m.group(1)  # the style="..." (or other attrs) between alt="" and "/>", verbatim
    new_tag = f'<img src="data:image/png;base64,{new_b64}" alt="{alt_text}"{tail}/>'
    new_text = html_text[:m.start()] + new_tag + html_text[m.end():]
    print(f"[6] swapped {label} image base64 in place (attrs preserved: {tail.strip()[:60]}...).")
    return new_text


new_html = html
new_html = swap_img(new_html, S3_ALT, S3_B64_NEW, "S3 (§3 DRIFT_MATRIX heatmap)")
new_html = swap_img(new_html, S7_ALT, S7_B64_NEW, "S7 (§7 drift summary bar)")
new_html = swap_img(new_html, FS3_ALT, FS3_B64_NEW, "F_S3 (§3 supplementary per-activity JS bar)")

N_IMG_AFTER_SWAP = new_html.count("data:image/png;base64,")
if N_IMG_AFTER_SWAP != N_IMG_BEFORE:
    sys.exit(f"ABORT: figure count changed after swap ({N_IMG_BEFORE} -> {N_IMG_AFTER_SWAP}); "
              f"in-place swap must preserve the count. No file written.")

# ══════════════════════════════════════════════════════════════════════════
# 7. INJECT the legend table right after the disposition panel
# ══════════════════════════════════════════════════════════════════════════
idx = new_html.index(DISPOSITION_END_ANCHOR)  # raises ValueError if missing -> aborts loudly
at = idx + len(DISPOSITION_END_ANCHOR)
new_html = new_html[:at] + "\n" + LEGEND_TABLE + new_html[at:]
print("[7] injected the legend table right after the disposition panel.")

# Idempotency marker — inserted last, right after <body>
new_html = new_html.replace("<body>", f"<body>\n{MARKER}", 1)

# ══════════════════════════════════════════════════════════════════════════
# 8. Post-injection sanity checks — abort (without writing) rather than ship
#    a broken report
# ══════════════════════════════════════════════════════════════════════════
for must_have in ["35/35 checks passed", "CANONICAL POPULATION", PRIOR_MARKER_3, PRIOR_MARKER_4,
                   "Documented deviations"]:
    if must_have not in new_html:
        sys.exit(f"ABORT (post-injection check): '{must_have}' missing from the new HTML. No file written.")

N_IMG_FINAL = new_html.count("data:image/png;base64,")
if N_IMG_FINAL != N_IMG_BEFORE:
    sys.exit(f"ABORT (post-injection check): figure count drifted to {N_IMG_FINAL}, expected "
              f"{N_IMG_BEFORE}. No file written.")

for code, name in ACT_LABELS.items():
    if name not in new_html:
        sys.exit(f"ABORT (post-injection check): legend name '{name}' (code {code}) missing "
                  f"from the new HTML. No file written.")

REPORT.write_text(new_html, encoding="utf-8")
print(f"\n[OK] wrote {REPORT}")
print(f"     figures before: {N_IMG_BEFORE}.  figures after: {N_IMG_FINAL} (unchanged — 3 swapped "
      f"in place: S3, S7, F_S3). Legend table injected (14 rows). Banner/35-35/disposition-panel/"
      f"prior markers preserved.")
print("=== DONE ===")
