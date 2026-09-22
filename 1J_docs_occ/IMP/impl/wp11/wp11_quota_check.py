"""
WP11 item 4 pre-flight helper: best-effort parser for `quota -s` output, used to
decide whether a draw-block array task has enough /speed-scratch headroom to start
(needs >= 400 G free before running).

Task doc: 1J_docs_occ/IMP/impl/2026-09-22_WP11_stage4d_draws.md, item 4.

`quota -s`'s exact column layout was not captured before this script was written --
the task doc's "8.7 T used of 10.0 T" figure was read informally by the manager, not
from a saved `quota -s` transcript (see the task doc's WHAT I DID NOT VERIFY). This
parser takes every size token (e.g. "8.7T", "8771G") found anywhere in the `quota -s`
output, converts each to GB, and treats the SMALLEST as used space and the LARGEST as
the limit -- `quota -s` conventionally lists (blocks-used, soft-quota, hard-limit) on
one line with blocks-used <= soft-quota <= hard-limit, and soft and hard limits are
frequently equal, so "second-largest" is not safe (it can tie the limit); "smallest"
is robust to that tie as long as the account is currently under quota.

If fewer than two size tokens are found anywhere in the input, this prints
PARSE_FAILED and returns exit 1 -- the caller must treat that as FAIL (fail closed:
never assume space is free just because parsing didn't work).

Usage: python wp11_quota_check.py <path to saved quota -s output>
Prints exactly one line: "USED_GB=.. LIMIT_GB=.. FREE_GB=.." or "PARSE_FAILED".
"""
import re
import sys

MULT = {"K": 1.0 / 1024 / 1024, "M": 1.0 / 1024, "G": 1.0, "T": 1024.0}


def parse_quota_gb(text):
    # Manager fix 2026-09-22: the first version took min/max over EVERY size token in
    # the whole `quota -s` page. The real page (captured by the manager) lists five
    # volumes, so min was /nettemp's "0.0K" and max was 10.0T -> ~10 T "free", a check
    # that could never fail. Now: only the line whose first field is "/speed-scratch";
    # its size tokens are, in order, used, warn, limit.
    for line in text.splitlines():
        fields = line.split()
        if not fields or fields[0] != "/speed-scratch":
            continue
        vals = []
        for tok in re.findall(r"[0-9]+(?:\.[0-9]+)?[KMGT](?![A-Za-z])", line, flags=re.IGNORECASE):
            vals.append(float(tok[:-1]) * MULT[tok[-1].upper()])
        if len(vals) < 3:
            return None
        return vals[0], vals[2]
    return None


def main():
    if len(sys.argv) != 2:
        print("PARSE_FAILED")
        return 1
    with open(sys.argv[1], "r", encoding="utf-8", errors="replace") as f:
        text = f.read()
    parsed = parse_quota_gb(text)
    if parsed is None:
        print("PARSE_FAILED")
        return 1
    used_gb, limit_gb = parsed
    free_gb = limit_gb - used_gb
    print(f"USED_GB={used_gb:.1f} LIMIT_GB={limit_gb:.1f} FREE_GB={free_gb:.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
