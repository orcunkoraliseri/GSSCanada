# -*- coding: utf-8 -*-
"""5J check for the act2 rule prefix2_major. Reads a trigger log (never the data).
PASS only if: a `PATCH act2 OK match=prefix2_major ... prefix=33` line exists; its `chosen`
is the child with the most minutes (ties: lowest code); 33 is in the act2 map (the map
entry count on the first PATCH line is at least 5 = 4 unambiguous prefixes + chosen 33).
Usage: python 5thJ_check_act2.py <log>     exit 0 PASS, 1 FAIL."""
import re
import sys


def check(text):
    reasons = []
    m0 = re.search(r"PATCH act2 OK match=prefix2_major act2_map_entries=(\d+) ambiguous_prefixes=(\[.*?\])", text)
    if not m0:
        return ["no 'PATCH act2 OK match=prefix2_major act2_map_entries=' line"]
    lines = re.findall(r"PATCH act2 OK match=prefix2_major fold=(\w+) prefix=(\d\d) "
                       r"minutes=\{([^}]*)\} chosen=(\d+) profile=(\S+)", text)
    if not any(p == "33" for _, p, _, _, _ in lines):
        reasons.append("no per-prefix line for prefix 33")
    if int(m0.group(1)) < 5:
        reasons.append("act2 map has %s entries, expected >= 5 (33 missing)" % m0.group(1))
    for fold, pre, mins, chosen, prof in lines:
        d = dict((k, int(v)) for k, v in (kv.split(":") for kv in mins.split(",")))
        best = min(d, key=lambda c: (-d[c], c))
        if chosen != best:
            reasons.append("fold %s prefix %s: chosen %s but %s has the most minutes %s" % (fold, pre, chosen, best, d))
        if not prof or prof == "None":
            reasons.append("prefix %s has no profile" % pre)
    return reasons


if __name__ == "__main__":
    r = check(open(sys.argv[1], encoding="utf-8").read())
    print("FAIL %s" % r if r else "PASS")
    sys.exit(1 if r else 0)
