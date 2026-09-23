"""P10R: line-level comparison of two IDFs (comments and whitespace stripped, header line ignored).
Prints the number of differing lines and the first differences. Read-only."""
import difflib, re, sys
def norm(p):
    out = []
    for ln in open(p, encoding="utf-8", errors="replace").read().splitlines():
        ln = re.sub(r"!.*", "", ln).strip()
        if ln:
            out.append(ln)
    return out
a, b = norm(sys.argv[1]), norm(sys.argv[2])
sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
n, ex = 0, []
for op, i1, i2, j1, j2 in sm.get_opcodes():
    if op != "equal":
        n += max(i2 - i1, j2 - j1)
        if len(ex) < int(sys.argv[3]) if len(sys.argv) > 3 else 8:
            ex.append((op, a[i1:i1 + 2], b[j1:j1 + 2]))
print(f"lines A={len(a)} B={len(b)} differing={n}")
for e in ex:
    print("  ", e)
