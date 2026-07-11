"""_gen_v6_plots.py -- Task C (Step-4 Improvements, Improvement 3): three new
base64-embedded figures injected into step4_validation_report_v6.html via
anchor-based placeholder substitution ({{CHART_*}} tokens written into the v6
HTML copy). v5 generator (_gen_v5_plots.py) and step4_validation_report_v5.html
are NOT touched by this script -- v6 is a separate, additive file pair.

Figures:
  1. Cycle-representation funnel (Section 9.1)      -- {{CHART_CYCLE_FUNNEL}}
  2. act30 -> BEM sensitivity, before/after Task B   -- {{CHART_ACT30_SENSITIVITY}}
  3. PR-coding disjointness strip (Section 9.2)      -- {{CHART_PR_DISJOINT}}

All figure values are the already-measured Task A/B/C constants (see the
source comments on each function) -- this script does NOT re-load the
530MB augmented_diaries.csv / Full_Schedules.csv at runtime; those were
measured once (Task C, step C1) via improvement_planning/measure_shape_gaps_v2_samebasis.py
(re-run 2026-07-09, chunked) and a dedicated chunked pool/Matched_Keys check
(also 2026-07-09). See step4_improvements_implementation.md Task C Progress Log.

Run:  py -3 _gen_v6_plots.py     (idempotent -- safe to re-run)
"""
import os, sys, io, base64
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(HERE, "step4_validation_report_v6.html")


def fig_to_b64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=100)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()


# ---------------------------------------------------------------------------
# Figure 1 -- Cycle-representation funnel (anchor: Section 9.1)
#
# pool_pct / tier1_pct: unchanged v5-published Section 9.1 table (also
#   independently re-confirmed 2026-07-09 by a chunked groupby CYCLE_YEAR on
#   augmented_diaries.csv: 2005 57,663/192,183=30.0%, 2010 45,342=23.6%,
#   2015 52,170=27.1%, 2022 37,008=19.3% -- exact match).
# before_pct / after_pct: RE-DERIVED 2026-07-09 (independent audit + fix), live
#   from aug_pipeline/Full_Schedules.csv's own CYCLE_YEAR column, --full
#   flag-off vs --full --region-tier, 286,537 agents, seed 42. The originally
#   published after_pct (28.76/23.88/29.23/18.14%) was found to have no
#   supporting artifact -- the Tier-2b design it was attributed to was
#   fallback-only (capped at 1,352/286,537 = 0.47% of agents), mathematically
#   incapable of producing that result. Root-caused and fixed same day: Tier-2b
#   is now merged into Tier-2 (REGION-folded geography key applies to ALL
#   cycles at Tier-2 under --region-tier, not just as a 2005 post-hoc
#   fallback). Real result: 2005 nearly DOUBLES (9.03%->15.76%), not triples.
#   See step4_improvements_implementation.md, "INDEPENDENT AUDIT" +
#   "FIX IMPLEMENTED" Progress Log entries for the full derivation.
# ---------------------------------------------------------------------------
def make_fig1_cycle_funnel() -> str:
    cycles = [2005, 2010, 2015, 2022]
    pool_pct = [30.0, 23.6, 27.1, 19.3]
    tier1_pct = [0.0, 37.9, 36.9, 25.2]
    before_pct = [9.03, 32.52, 34.80, 23.66]
    after_pct = [15.76, 29.93, 32.04, 22.27]

    x = np.arange(len(cycles))
    w = 0.2
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    ax.bar(x - 1.5 * w, pool_pct, w, label="Pool supply (augmented_diaries.csv)", color="#8c8c8c")
    ax.bar(x - 0.5 * w, tier1_pct, w, label="Tier-1 expected share", color="#f0b429", hatch="//")
    ax.bar(x + 0.5 * w, before_pct, w, label="Matched share — before (flag off)", color="#C44E52", alpha=0.85)
    ax.bar(x + 1.5 * w, after_pct, w, label="Matched share — after (--region-tier, Task A, Tier-2 merge)", color="#55A868", alpha=0.9)

    for xi, v in zip(x + 1.5 * w, after_pct):
        ax.annotate(f"{v:.1f}%", (xi, v), textcoords="offset points", xytext=(0, 3),
                    ha="center", fontsize=8, fontweight="bold", color="#2c662d")
    for xi, v in zip(x + 0.5 * w, before_pct):
        ax.annotate(f"{v:.1f}%", (xi, v), textcoords="offset points", xytext=(0, 3),
                    ha="center", fontsize=7, color="#7a2020")

    ax.set_xticks(x)
    ax.set_xticklabels([str(c) for c in cycles])
    ax.set_ylabel("% (pool: of 192,183 pool diaries; matched: of 286,537 Census agents)")
    ax.set_title("Section 9.1 — Cycle-representation funnel: pool supply → Tier-1 expected → matched share\n"
                 "2005 has ample supply (30.0%) and 0.0% Tier-1 expectation; Task A's REGION Tier-2 merge nearly doubles its match (structural ceiling, see 9.3)")
    ax.legend(fontsize=8, loc="upper center", ncol=2)
    ax.set_ylim(0, max(pool_pct + tier1_pct + before_pct + after_pct) * 1.28)
    ax.grid(axis="y", linewidth=0.4, alpha=0.4)
    ax.set_axisbelow(True)
    plt.tight_layout()
    return fig_to_b64(fig)


# ---------------------------------------------------------------------------
# Figure 2 -- act30 -> BEM sensitivity, before/after Task B (anchor: the
# "Would raking all three heads..." note, Section 2/6 area)
#
# before/after: measure_shape_gaps_v2_samebasis.py RE-RUN 2026-07-09 (post
#   Tier-2-merge fix + Task-B re-rake on the corrected population) -- output:
#     calib_pre_rake  vs obs: Equipment mean|d| 12.0%, peak 26.1% @ h4;
#                              Lighting mean|d| 4.4pp, peak 11.8pp @ h18;
#                              Metabolic +4.3%  (unchanged -- reads
#                              augmented_diaries.csv, untouched by either fix)
#     calib_post_rake vs obs: Equipment mean|d| 4.9%,  peak 8.9% @ h5;
#                              Lighting mean|d| 1.1pp, peak 2.6pp @ h17;
#                              Metabolic -0.5%  (small movement from the
#                              pre-Tier-2-fix run's 4.3%/8.3%/1.0pp/-0.4%,
#                              since the corrected linkage shifts which rows
#                              are IS_SYNTHETIC -- all three plan targets
#                              still met with wide margin)
# v5_ref: the v5-published numbers (14.9% / 3.8pp / +1.9%) -- a DIFFERENT,
#   un-weighted basis (no WGHT_PER survey weighting) than the v2 method above;
#   shown only as a faint reference marker, never as the "before" bar.
# ---------------------------------------------------------------------------
def make_fig2_act30_sensitivity() -> str:
    channels = ["Equipment\n(peak-norm. shape, mean |Δ|)", "Lighting\n(shape, mean |Δ|)", "Metabolic\n(mean Δ)"]
    before = [12.0, 4.4, 4.3]     # %, pp, %
    after = [4.9, 1.1, -0.5]
    v5_ref = [14.9, 3.8, 1.9]     # different (unweighted) basis -- reference only
    units = ["%", "pp", "%"]

    x = np.arange(len(channels))
    w = 0.28
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.bar(x - w / 2 - 0.02, before, w, label="Before (raw Step-4 model, v2 same-basis)", color="#C44E52", alpha=0.85)
    ax.bar(x + w / 2 + 0.02, after, w, label="After (Task B joint rake, v2 same-basis)", color="#55A868", alpha=0.9)
    ax.scatter(x, v5_ref, marker="_", s=1400, linewidths=2.5, color="#999999", zorder=5,
               label="v5-published (different, unweighted basis — reference only)")

    ax.axhline(0, color="black", linewidth=0.8)
    for xi, v, u in zip(x - w / 2 - 0.02, before, units):
        ax.annotate(f"{v:.1f}{u}", (xi, v), textcoords="offset points",
                    xytext=(0, 4 if v >= 0 else -13), ha="center", fontsize=8)
    for xi, v, u in zip(x + w / 2 + 0.02, after, units):
        sign = "−" if v < 0 else ""
        ax.annotate(f"{sign}{abs(v):.1f}{u}", (xi, v), textcoords="offset points",
                    xytext=(0, 4 if v >= 0 else -13), ha="center", fontsize=8, fontweight="bold")

    ymax = max(before + v5_ref) * 1.35
    ax.set_ylim(min(after) - 1.5, ymax)
    ax.annotate("peak 26.1% @ h4 → 8.9% @ h5", (x[0], max(before[0], v5_ref[0]) + ymax * 0.06),
                ha="center", fontsize=7.5, color="#444")

    ax.set_xticks(x)
    ax.set_xticklabels(channels, fontsize=8.5)
    ax.set_ylabel("Gap vs observed GSS (% or pp — see channel label)")
    ax.set_title("Section 2/6 — act30 → BEM sensitivity: before vs after Task B joint rake\n"
                 "(same basis: hetus_30min.csv vs synthetic act30, peak-normalized equipment shape)")
    ax.legend(fontsize=7.5, loc="upper left")
    ax.grid(axis="y", linewidth=0.4, alpha=0.4)
    ax.set_axisbelow(True)
    plt.tight_layout()
    return fig_to_b64(fig)


# ---------------------------------------------------------------------------
# Figure 3 -- PR-coding disjointness strip (anchor: Section 9.2)
#
# Value sets: fixed constants from 05_census_linkage.py's REGION_FOLD +
#   step4_validation_report_v5.html Section 9.2 (Census SGC set) -- spot-checked
#   2026-07-09 (Task C, step C1) via a chunked read of augmented_diaries.csv:
#   2005 pool PR = {1,2,3,4,5} exactly; 2010/2015/2022 pool PR =
#   {10,11,12,13,24,35,46,47,48,59} exactly (all three cycles identical set).
#   Census PR = {10,24,35,46,48,59} is the report-published constant (not
#   independently re-checked against the Census file in this session).
# REGION_FOLD: SGC 10/11/12/13->1 (Atlantic), 24->2 (Quebec), 35->3 (Ontario),
#   46/47/48->4 (Prairies), 59->5 (BC); 2005 legacy codes 1..5 passthrough.
# ---------------------------------------------------------------------------
def make_fig3_pr_disjoint() -> str:
    region_names = ["1 — Atlantic", "2 — Québec", "3 — Ontario", "4 — Prairies", "5 — BC"]
    region_colors = ["#4C72B0", "#DD8452", "#55A868", "#8172B2", "#C44E52"]

    rows = [
        ("2005 pool\n(legacy 5-region)", [["1"], ["2"], ["3"], ["4"], ["5"]]),
        ("2010/2015/2022 pool\n(SGC)", [["10", "11", "12", "13"], ["24"], ["35"], ["46", "47", "48"], ["59"]]),
        ("Census 2021\n(SGC)", [["10"], ["24"], ["35"], ["46", "48"], ["59"]]),
    ]

    fig, ax = plt.subplots(figsize=(9.5, 4.6))
    n_rows = len(rows)
    n_cols = len(region_names)
    row_h = 1.0
    col_w = 1.0

    for ci in range(n_cols):
        ax.add_patch(plt.Rectangle((ci * col_w, -0.3), col_w, n_rows * row_h + 0.3,
                                    facecolor=region_colors[ci], alpha=0.10, edgecolor="none", zorder=0))
        ax.text(ci * col_w + col_w / 2, n_rows * row_h + 0.05, region_names[ci],
                ha="center", va="bottom", fontsize=8.5, fontweight="bold", color=region_colors[ci])

    for ri, (row_label, cells) in enumerate(rows):
        y = (n_rows - 1 - ri) * row_h
        ax.text(-0.15, y + row_h / 2, row_label, ha="right", va="center", fontsize=8.5)
        for ci, codes in enumerate(cells):
            x0 = ci * col_w
            box = plt.Rectangle((x0 + 0.06, y + 0.12), col_w - 0.12, row_h - 0.24,
                                 facecolor="white", edgecolor=region_colors[ci], linewidth=1.6, zorder=2)
            ax.add_patch(box)
            ax.text(x0 + col_w / 2, y + row_h / 2, ",".join(codes), ha="center", va="center",
                     fontsize=9, zorder=3)
        # thin connector lines to the row above within the same region column (the REGION_FOLD "bridge")
        if ri > 0:
            for ci in range(n_cols):
                x0 = ci * col_w + col_w / 2
                ax.plot([x0, x0], [y + row_h, y + row_h + 0.12], color=region_colors[ci],
                        linewidth=1.2, alpha=0.6, zorder=1)

    ax.set_xlim(-1.7, n_cols * col_w + 0.1)
    ax.set_ylim(-0.6, n_rows * row_h + 0.55)
    ax.axis("off")
    ax.set_title("Section 9.2 — PR-coding disjointness, bridged by REGION_FOLD\n"
                 "2005 pool PR {1..5} vs 2010/15/22 pool + Census PR (SGC) — disjoint raw codes, same REGION_FOLD column",
                 fontsize=10.5)
    ax.text((n_cols * col_w) / 2, -0.55,
            "REGION_FOLD (05_census_linkage.py): SGC 10/11/12/13→1, 24→2, 35→3, 46/47/48→4, 59→5;  "
            "2005 legacy codes 1..5 passthrough",
            ha="center", va="top", fontsize=7.5, color="#555")
    plt.tight_layout()
    return fig_to_b64(fig)


# ---------------------------------------------------------------------------
# Anchor-based injection into step4_validation_report_v6.html
# ---------------------------------------------------------------------------
PLACE = {
    "{{CHART_CYCLE_FUNNEL}}": ("Cycle-representation funnel (Section 9.1, before/after Task A)", make_fig1_cycle_funnel),
    "{{CHART_ACT30_SENSITIVITY}}": ("act30 to BEM sensitivity (Section 2/6, before/after Task B, same-basis)", make_fig2_act30_sensitivity),
    "{{CHART_PR_DISJOINT}}": ("PR-coding disjointness strip (Section 9.2, REGION_FOLD bridge)", make_fig3_pr_disjoint),
}


def main():
    if not os.path.exists(HTML):
        raise SystemExit(f"{HTML} not found -- copy step4_validation_report_v5.html to "
                          f"step4_validation_report_v6.html first (v5 stays untouched).")
    html = open(HTML, encoding="utf-8").read()

    inserted, skipped_present, skipped_missing_token = [], [], []
    for token, (alt, fn) in PLACE.items():
        if f'alt="{alt}"' in html:
            skipped_present.append(alt)
            continue
        if token not in html:
            skipped_missing_token.append(token)
            continue
        b64 = fn()
        img = f'<img src="data:image/png;base64,{b64}" alt="{alt}"/>'
        html = html.replace(token, img)
        inserted.append(alt)

    open(HTML, "w", encoding="utf-8").write(html)
    print(f"WROTE {os.path.basename(HTML)}: {os.path.getsize(HTML)/1024:.0f} KB")
    print(f"  inserted: {inserted or 'none'}")
    print(f"  skipped (already present, idempotency guard): {skipped_present or 'none'}")
    print(f"  skipped (token not found): {skipped_missing_token or 'none'}")
    remaining = html.count("{{CHART_")
    print(f"  remaining unresolved {{{{CHART_*}}}} tokens: {remaining}")


if __name__ == "__main__":
    main()
