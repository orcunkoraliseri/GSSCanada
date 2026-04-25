"""
04Z_F3_compare.py — F3 sweep comparison

Reads diagnostics_v4_statistical.json from F1 baseline + 4 F3 configs,
ranks by composite_score (lower = better), and emits:
  - F3_sweep_ranking.md   (markdown table)
  - F3_sweep_comparison.html (styled HTML table)
  - F3_sweep_results.json (machine-readable)

Usage:
    python 04Z_F3_compare.py \
        --f1_json  outputs_step4/diagnostics_v4_statistical.json \
        --f3a_json outputs_step4_F3A/diagnostics_v4_statistical.json \
        --f3b_json outputs_step4_F3B/diagnostics_v4_statistical.json \
        --f3c_json outputs_step4_F3C/diagnostics_v4_statistical.json \
        --f3d_json outputs_step4_F3D/diagnostics_v4_statistical.json \
        --out_dir  deliveries/F3_sweep/F3_sweep_20260423
"""

import argparse
import json
import os
from datetime import datetime


CONFIGS = [
    ("F1",  "F1 baseline (pos_weight sign-flip fixed, manual boosts)"),
    ("F3-A", "baseline_balanced_bce (cop pos_weight + no manual act boosts)"),
    ("F3-B", "+stratum_marg (F3-A + per-CS marginal loss)"),
    ("F3-C", "+aux_stratum_head (F3-B + aux decoder head)"),
    ("F3-D", "+data_side_sampling (F3-B + wght_per × strata_inv_freq)"),
]

PASS_THRESHOLDS = {
    "cop_alone_gap_pp":    3.0,
    "cop_spouse_gap_pp":   3.0,
    "cop_friends_gap_pp":  3.0,
    "cop_parents_gap_pp":  3.0,
    "cop_colleagues_gap_pp": 3.0,
    "act_JS_mean":         0.05,
    "AT_HOME_gap_pp":      3.0,
}


def load_json(path: str) -> dict:
    if path is None or not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)


def extract_metrics(d: dict) -> dict:
    m = {}

    # Composite score — nested under d["composite"]["composite_score"]
    m["composite_score"] = d.get("composite", {}).get("composite_score", float("nan"))

    # AT_HOME bootstrap gap (pp) — key is "at_home" (lowercase), inner key "gap_pp"
    at_home = d.get("bootstrap_cis", {}).get("at_home", {})
    m["AT_HOME_gap_pp"] = at_home.get("gap_pp", float("nan"))
    m["AT_HOME_ci_lo"]  = at_home.get("gap_ci_lo_pp", float("nan"))
    m["AT_HOME_ci_hi"]  = at_home.get("gap_ci_hi_pp", float("nan"))

    # Co-presence gaps — inner key is "gap_pp" (not "mean_gap_pp")
    cop_gaps = d.get("bootstrap_cis", {}).get("copresence", {})
    for ch in ["Alone", "Spouse", "Children", "parents", "friends", "others", "colleagues"]:
        key = f"cop_{ch.lower()}_gap_pp"
        m[key] = cop_gaps.get(ch, {}).get("gap_pp", float("nan"))

    # Activity JS — stored in composite components, not in bootstrap_cis
    m["act_JS_mean"] = d.get("composite", {}).get("components", {}).get("act_js_mean", float("nan"))

    # Calibration MAE (Alone channel) — key is "mae" (lowercase)
    cal = d.get("calibration", {}).get("Alone", {})
    m["cal_Alone_MAE"] = cal.get("mae", float("nan"))

    return m


def pass_fail(m: dict) -> dict:
    pf = {}
    for k, thresh in PASS_THRESHOLDS.items():
        val = m.get(k, float("nan"))
        import math
        if math.isnan(val):
            pf[k] = "N/A"
        else:
            pf[k] = "PASS" if abs(val) <= thresh else "FAIL"
    return pf


def _fmt(v, decimals=3):
    import math
    if math.isnan(v):
        return "—"
    return f"{v:.{decimals}f}"


def build_rows(config_data: list) -> list:
    rows = []
    for tag, desc, metrics, pf in config_data:
        n_pass = sum(1 for v in pf.values() if v == "PASS")
        n_total = sum(1 for v in pf.values() if v != "N/A")
        rows.append({
            "tag": tag,
            "desc": desc,
            "composite": metrics["composite_score"],
            "AT_HOME_gap": metrics["AT_HOME_gap_pp"],
            "cop_alone_gap": metrics.get("cop_alone_gap_pp", float("nan")),
            "cop_spouse_gap": metrics.get("cop_spouse_gap_pp", float("nan")),
            "act_JS": metrics["act_JS_mean"],
            "cal_Alone_MAE": metrics["cal_Alone_MAE"],
            "pass_count": f"{n_pass}/{n_total}",
            "pf": pf,
        })
    # Sort by composite score ascending (lower = better); NaN last
    import math
    rows.sort(key=lambda r: (math.isnan(r["composite"]), r["composite"]))
    return rows


def write_markdown(rows: list, out_path: str):
    lines = [
        f"# F3 Sweep Ranking — generated {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "Composite score: `S = 0.20*AT_HOME_rms/10 + 0.35*cop_max_gap_pp/10 + 0.35*act_JS_mean*10 + 0.10*cop_cal_MAE*10`",
        "Lower = better. F1 baseline = 1.045.",
        "",
        "| Rank | Tag | Composite ↑ | AT_HOME gap (pp) | Alone gap (pp) | Spouse gap (pp) | Act JS | Cal Alone MAE | Pass |",
        "|------|-----|-------------|-----------------|----------------|-----------------|--------|---------------|------|",
    ]
    import math
    for rank, r in enumerate(rows, 1):
        winner = " **WINNER**" if rank == 1 and not math.isnan(r["composite"]) else ""
        lines.append(
            f"| {rank} | **{r['tag']}**{winner} | {_fmt(r['composite'])} "
            f"| {_fmt(r['AT_HOME_gap'])} "
            f"| {_fmt(r['cop_alone_gap'])} "
            f"| {_fmt(r['cop_spouse_gap'])} "
            f"| {_fmt(r['act_JS'])} "
            f"| {_fmt(r['cal_Alone_MAE'])} "
            f"| {r['pass_count']} |"
        )
    lines += [
        "",
        "## Per-metric pass/fail",
        "",
        "| Tag | " + " | ".join(PASS_THRESHOLDS.keys()) + " |",
        "|-----|" + "|".join(["------"] * len(PASS_THRESHOLDS)) + "|",
    ]
    for r in rows:
        cells = " | ".join(r["pf"].get(k, "N/A") for k in PASS_THRESHOLDS)
        lines.append(f"| {r['tag']} | {cells} |")

    lines += [
        "",
        "## Config descriptions",
        "",
    ]
    for r in rows:
        lines.append(f"- **{r['tag']}**: {r['desc']}")

    with open(out_path, "w") as f:
        f.write("\n".join(lines) + "\n")


def write_html(rows: list, out_path: str):
    import math
    cols = ["Rank", "Tag", "Composite ↓", "AT_HOME gap", "Alone gap", "Spouse gap", "Act JS", "Cal MAE", "Pass"]

    def cell_color(val, thresh, invert=False):
        if math.isnan(val):
            return ""
        ok = abs(val) <= thresh
        if invert:
            ok = not ok
        return ' style="background:#d4edda"' if ok else ' style="background:#f8d7da"'

    header = "".join(f"<th>{c}</th>" for c in cols)
    body_rows = []
    for rank, r in enumerate(rows, 1):
        winner = " ★" if rank == 1 and not math.isnan(r["composite"]) else ""
        tds = [
            f"<td>{rank}</td>",
            f"<td><strong>{r['tag']}{winner}</strong></td>",
            f"<td{cell_color(r['composite'], 1.045, invert=True)}>{_fmt(r['composite'])}</td>",
            f"<td{cell_color(r['AT_HOME_gap'], 3.0)}>{_fmt(r['AT_HOME_gap'])}</td>",
            f"<td{cell_color(r['cop_alone_gap'], 3.0)}>{_fmt(r['cop_alone_gap'])}</td>",
            f"<td{cell_color(r['cop_spouse_gap'], 3.0)}>{_fmt(r['cop_spouse_gap'])}</td>",
            f"<td{cell_color(r['act_JS'], 0.05)}>{_fmt(r['act_JS'])}</td>",
            f"<td>{_fmt(r['cal_Alone_MAE'])}</td>",
            f"<td>{r['pass_count']}</td>",
        ]
        body_rows.append("<tr>" + "".join(tds) + "</tr>")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>F3 Sweep Ranking</title>
<style>
  body {{ font-family: sans-serif; padding: 2em; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ border: 1px solid #ccc; padding: 6px 10px; text-align: center; }}
  th {{ background: #343a40; color: white; }}
  tr:nth-child(even) {{ background: #f8f9fa; }}
</style>
</head>
<body>
<h1>F3 Sweep Ranking</h1>
<p>Generated {datetime.now().strftime('%Y-%m-%d %H:%M')} &mdash;
   Composite score lower = better. F1 baseline = 1.045.<br>
   Green = passes threshold; red = fails.</p>
<table>
<thead><tr>{header}</tr></thead>
<tbody>{"".join(body_rows)}</tbody>
</table>
<h2>Config descriptions</h2>
<ul>
{"".join(f'<li><strong>{r["tag"]}</strong>: {r["desc"]}</li>' for r in rows)}
</ul>
</body>
</html>
"""
    with open(out_path, "w") as f:
        f.write(html)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--f1_json",  required=True)
    p.add_argument("--f3a_json", required=True)
    p.add_argument("--f3b_json", required=True)
    p.add_argument("--f3c_json", required=True)
    p.add_argument("--f3d_json", required=True)
    p.add_argument("--out_dir",  required=True)
    args = p.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    inputs = [
        ("F1",   args.f1_json),
        ("F3-A", args.f3a_json),
        ("F3-B", args.f3b_json),
        ("F3-C", args.f3c_json),
        ("F3-D", args.f3d_json),
    ]

    config_data = []
    for (tag, desc), (_, json_path) in zip(CONFIGS, inputs):
        d = load_json(json_path)
        if not d:
            print(f"  WARNING: {json_path} missing or empty — {tag} will show NaN")
        m = extract_metrics(d)
        pf = pass_fail(m)
        config_data.append((tag, desc, m, pf))

    rows = build_rows(config_data)

    md_path   = os.path.join(args.out_dir, "F3_sweep_ranking.md")
    html_path = os.path.join(args.out_dir, "F3_sweep_comparison.html")
    json_path = os.path.join(args.out_dir, "F3_sweep_results.json")

    write_markdown(rows, md_path)
    write_html(rows, html_path)

    results = {r["tag"]: {
        "composite_score": r["composite"],
        "AT_HOME_gap_pp":  r["AT_HOME_gap"],
        "cop_alone_gap_pp": r["cop_alone_gap"],
        "act_JS_mean": r["act_JS"],
        "pass_count":  r["pass_count"],
        "pass_fail":   r["pf"],
    } for r in rows}
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*60}")
    print("F3 sweep comparison complete")
    print(f"{'='*60}")
    import math
    winner = rows[0]
    if not math.isnan(winner["composite"]):
        print(f"  WINNER: {winner['tag']}  composite={winner['composite']:.4f}  passes={winner['pass_count']}")
    else:
        print("  WARNING: no valid composite scores found — check input JSONs")

    print(f"\n  Ranking:")
    for i, r in enumerate(rows, 1):
        print(f"    {i}. {r['tag']:6s}  score={_fmt(r['composite'])}  "
              f"AT_HOME={_fmt(r['AT_HOME_gap'])}pp  Alone={_fmt(r['cop_alone_gap'])}pp  "
              f"JS={_fmt(r['act_JS'])}  pass={r['pass_count']}")

    print(f"\n  Outputs:")
    print(f"    {md_path}")
    print(f"    {html_path}")
    print(f"    {json_path}")


if __name__ == "__main__":
    main()
