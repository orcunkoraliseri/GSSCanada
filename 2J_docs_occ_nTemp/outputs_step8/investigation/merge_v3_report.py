"""merge_v3_report.py — 2JV3-E: splice the re-based §4 (gate rows + charts) from the
local --section 4 run into a COPY of the canonical step8_validation_report.html, and
recompute the scorecard/§8-summary counts. Canonical file is read-only here; the merged
output goes to a new file. One-off script, stdlib only (re).

Usage: py investigation/merge_v3_report.py
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))          # outputs_step8/investigation/
OUTPUTS_STEP8 = os.path.dirname(HERE)                        # outputs_step8/

CANONICAL = os.path.join(OUTPUTS_STEP8, "step8_validation_report.html")
LOCAL_S4 = os.path.join(OUTPUTS_STEP8, "step8_validation_report_v3_section4_local.html")
MERGED_OUT = os.path.join(OUTPUTS_STEP8, "step8_validation_report_v3_merged.html")

ROW_RE = re.compile(
    r'<tr class="[a-z]+-row"><td>(?P<id>[^<]+)</td><td>\[(?P<lvl>[A-Z]+)\]</td>'
    r'<td[^>]*>(?P<desc>.*?)</td></tr>',
    re.DOTALL,
)


def _extract_section_div(html, sid, next_sid):
    start_marker = f'<div class="chart-section" id="{sid}">'
    end_marker = f'<div class="chart-section" id="{next_sid}">'
    start = html.index(start_marker)
    end = html.index(end_marker)
    return html[start:end], start, end


def _row_html(lvl, gid, desc):
    cls = lvl.lower()
    return (f'<tr class="{cls}-row"><td>{gid}</td><td>[{lvl}]</td>'
            f'<td style="white-space:normal;word-wrap:break-word">{desc}</td></tr>')


def _extract_last_tbody_rows(html):
    """Parse gate rows from ONLY the §8 'Summary Table (all gates)' tbody — the last
    <tbody> in the document. Each gate also appears in its own §N gates_rows('N.')
    table earlier in the doc (identical <tr> markup), so scanning the whole document
    would double-count every gate."""
    last_open = html.rfind("<tbody>")
    last_close = html.index("</tbody>", last_open)
    body = html[last_open:last_close]
    return [m.groupdict() for m in ROW_RE.finditer(body)]


def main():
    canonical = open(CANONICAL, encoding="utf-8").read()
    local = open(LOCAL_S4, encoding="utf-8").read()

    # 1. Splice the §4 chart-section div (gate table + 3 charts) from local into a
    #    copy of canonical, replacing canonical's old §4 block wholesale.
    old_s4, s4_start, s4_end = _extract_section_div(canonical, "s4", "s5")
    new_s4, _, _ = _extract_section_div(local, "s4", "s5")
    merged = canonical[:s4_start] + new_s4 + canonical[s4_end:]

    # 2. Recompute the §8 summary table: drop canonical's old 4.* rows, splice in the
    #    local run's 4.* rows (local only ran §4, so ALL its summary rows are 4.*) at
    #    the position the old ones occupied.
    canonical_rows = _extract_last_tbody_rows(canonical)
    local_s4_rows = _extract_last_tbody_rows(local)
    assert local_s4_rows, "local §4 report has no gate rows to splice in"
    assert all(r["id"].startswith("4.") for r in local_s4_rows), \
        f"local report has non-4.* rows: {[r['id'] for r in local_s4_rows if not r['id'].startswith('4.')]}"

    other_rows, insert_at, inserted = [], None, False
    for r in canonical_rows:
        if r["id"].startswith("4."):
            if not inserted:
                insert_at = len(other_rows)
                inserted = True
            continue
        other_rows.append(r)
    if insert_at is None:
        insert_at = len(other_rows)
    final_rows = other_rows[:insert_at] + local_s4_rows + other_rows[insert_at:]

    # Recompute scorecard tallies from the final gate list (exclude INFO from pass rate,
    # matching build_html_report's own pct formula).
    n_pass = sum(1 for r in final_rows if r["lvl"] == "PASS")
    n_warn = sum(1 for r in final_rows if r["lvl"] == "WARN")
    n_info = sum(1 for r in final_rows if r["lvl"] == "INFO")
    n_fail = sum(1 for r in final_rows if r["lvl"] == "FAIL")
    n_tot = n_pass + n_warn + n_fail
    pct = 100 * n_pass / n_tot if n_tot else 0

    # 3. Rebuild the §8 "Summary Table (all gates)" <tbody> in the merged doc.
    #    Its <tbody> is the LAST one in the document (Section 8 is the final table).
    tbody_open = "<tbody>"
    last_open = merged.rfind(tbody_open)
    close_marker = "</tbody>"
    last_close = merged.index(close_marker, last_open)
    new_tbody_inner = "\n        ".join(_row_html(r["lvl"], r["id"], r["desc"]) for r in final_rows)
    merged = merged[:last_open + len(tbody_open)] + "\n        " + new_tbody_inner + "\n      " + merged[last_close:]

    # 4. Rebuild the top scorecard numbers (n_pass/n_warn/n_info/n_fail/pct).
    def _sub_number(html, card_cls, value):
        pattern = re.compile(
            rf'(<div class="score-card {card_cls}">\s*<div class="number">)[^<]+(</div>)'
        )
        new_html, n = pattern.subn(rf"\g<1>{value}\g<2>", html, count=1)
        assert n == 1, f"scorecard patch failed for {card_cls}"
        return new_html

    merged = _sub_number(merged, "ok", n_pass)
    merged = _sub_number(merged, "warn", n_warn)
    merged = _sub_number(merged, "info", n_info)
    merged = _sub_number(merged, "fail", n_fail)
    merged = _sub_number(merged, "pct", f"{pct:.0f}%")

    os.makedirs(os.path.dirname(MERGED_OUT), exist_ok=True)
    with open(MERGED_OUT, "w", encoding="utf-8") as fh:
        fh.write(merged)

    print(f"canonical total gates: {len(canonical_rows)}")
    print(f"old 4.* rows removed : {sum(1 for r in canonical_rows if r['id'].startswith('4.'))}")
    print(f"new 4.* rows spliced : {len(local_s4_rows)}")
    print(f"merged total gates   : {len(final_rows)}")
    print(f"scorecard: {n_pass} PASS / {n_warn} WARN / {n_info} INFO / {n_fail} FAIL ({pct:.0f}%)")
    print(f"wrote {MERGED_OUT}")


if __name__ == "__main__":
    main()
