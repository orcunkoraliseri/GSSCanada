"""merge_v3_section4_into_baseline.py — splice the Fix v3 corrected §4 (gates + charts)
into the last intact full validation report, so every other section's plots/gates
(which a --section 4-only local run never touches) are preserved rather than lost.

Baseline = outputs_step8/step8_validation_report_v3_full_baseline.html (pulled intact
from the cluster, untouched since job 1069196 — the cancelled fix-v3 cluster jobs never
actually ran, so this file was never overwritten).
Patch    = outputs_step8/step8_validation_report_v3_section4_local.html (this session's
--section 4 local run against the corrected extractor/validator).

Output   = outputs_step8/step8_validation_report_v3_merged.html

Stdlib only (re). Not a general-purpose HTML merger — relies on this validator's
fixed per-section div/table structure (3rdJ_08_simulation_2split_val.py write_html()).
"""
import re

BASE_PATH = "outputs_step8/step8_validation_report_v3_full_baseline.html"
PATCH_PATH = "outputs_step8/step8_validation_report_v3_section4_local.html"
OUT_PATH = "outputs_step8/step8_validation_report_v3_merged.html"

STATUS_ORDER = ["PASS", "WARN", "INFO", "FAIL"]


def _section_block(html, sec, next_sec):
    """Extract '<div class=\'chart-section\' id=\'s{sec}\'>...' up to (not including) the
    next section's opening div."""
    start_pat = f"<div class='chart-section' id='s{sec}'>"
    end_pat = f"<div class='chart-section' id='s{next_sec}'>"
    i = html.index(start_pat)
    j = html.index(end_pat)
    return html[i:j]


def _master_rows_for_section(html, sec):
    """Rows in the §8 master table (with_section=True) belonging to this section —
    identified by '<td>§{sec}</td>' as the first <td> in the <tr>."""
    pat = re.compile(rf"<tr class='(\w+)-row'><td>§{sec}</td>.*?</tr>", re.DOTALL)
    return pat.findall(html), pat.sub("", html), pat


def main():
    baseline = open(BASE_PATH, encoding="utf-8").read()
    patch = open(PATCH_PATH, encoding="utf-8").read()

    # 1. Splice the per-section §4 div (gate table + charts) — patch's version replaces
    #    baseline's version wholesale.
    old_s4_block = _section_block(baseline, 4, 5)
    new_s4_block = _section_block(patch, 4, 5)
    merged = baseline.replace(old_s4_block, new_s4_block, 1)

    # 2. Splice the §4 rows inside the §8 master table (with_section=True rows carry a
    #    '§4' Sec column absent from the per-section table, so re-derive them from the
    #    patch's own master table, then insert at the same position in the merged doc).
    old_statuses, merged, _ = _master_rows_for_section(merged, 4)
    new_s4_master_rows = re.findall(r"<tr class='\w+-row'><td>§4</td>.*?</tr>", patch, re.DOTALL)
    new_statuses = [re.match(r"<tr class='(\w+)-row'>", r).group(1).upper() for r in new_s4_master_rows]

    # Insert point: right after the last §3 row / before the first §5 row in the master table.
    insert_after = re.search(r"<tr class='\w+-row'><td>§3</td>.*?</tr>", merged, re.DOTALL)
    matches_3 = list(re.finditer(r"<tr class='\w+-row'><td>§3</td>.*?</tr>", merged, re.DOTALL))
    if not matches_3:
        raise RuntimeError("no §3 master-table rows found — can't locate insert point")
    insert_at = matches_3[-1].end()
    merged = merged[:insert_at] + "".join(new_s4_master_rows) + merged[insert_at:]

    # 3. Recompute the scorecard tallies: baseline counts - old §4 counts + new §4 counts.
    m = re.search(r"Scorecard: (\d+) PASS · (\d+) WARN · (\d+) INFO · (\d+) FAIL", baseline)
    base_counts = {"PASS": int(m.group(1)), "WARN": int(m.group(2)),
                   "INFO": int(m.group(3)), "FAIL": int(m.group(4))}
    from collections import Counter
    old_c = Counter(s.upper() for s in old_statuses)
    new_c = Counter(new_statuses)
    final = {s: base_counts[s] - old_c.get(s, 0) + new_c.get(s, 0) for s in STATUS_ORDER}

    n_pass, n_warn, n_info, n_fail = final["PASS"], final["WARN"], final["INFO"], final["FAIL"]
    n_tot = n_pass + n_warn + n_fail
    pct = 100 * n_pass / n_tot if n_tot else 0

    merged = re.sub(
        r"Scorecard: \d+ PASS · \d+ WARN · \d+ INFO · \d+ FAIL",
        f"Scorecard: {n_pass} PASS · {n_warn} WARN · {n_info} INFO · {n_fail} FAIL",
        merged, count=2,  # title h2 + the same string doesn't appear elsewhere; safe count
    )
    merged = re.sub(r"(<div class=\"card ok\"><div class=\"num\">)\d+",
                     rf"\g<1>{n_pass}", merged)
    merged = re.sub(r"(<div class=\"card warn\"><div class=\"num\">)\d+",
                     rf"\g<1>{n_warn}", merged)
    merged = re.sub(r"(<div class=\"card info\"><div class=\"num\">)\d+",
                     rf"\g<1>{n_info}", merged)
    merged = re.sub(r"(<div class=\"card fail\"><div class=\"num\">)\d+",
                     rf"\g<1>{n_fail}", merged)
    merged = re.sub(r"(<div class=\"card pct\"><div class=\"num\">)[\d.]+%",
                     rf"\g<1>{pct:.0f}%", merged)

    open(OUT_PATH, "w", encoding="utf-8").write(merged)

    print(f"old §4 master-row statuses: {dict(old_c)}")
    print(f"new §4 master-row statuses: {dict(new_c)}")
    print(f"baseline tally: {base_counts}")
    print(f"merged tally:   {final}")
    print(f"images in merged doc: {merged.count('data:image/png')}")
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
