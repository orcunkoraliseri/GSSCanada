"""usage: py addstate.py <section header e.g. '## Verified'> <fragment file>: appends fragment at the END of that section (before the next '## ')."""
import sys, io
p = "C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/5J_docs_occ/Step9_docs/impl/2026-10-01_wp9o_rebase_win5.md"
t = io.open(p, encoding="utf-8").read()
h, frag = sys.argv[1], io.open(sys.argv[2], encoding="utf-8").read().rstrip("\n") + "\n"
i = t.index("\n" + h + "\n") + 1
j = t.find("\n## ", i + len(h))
j = len(t) if j < 0 else j + 1
t = t[:j].rstrip("\n") + "\n" + frag + ("\n" + t[j:] if j < len(t) else "")
io.open(p, "w", encoding="utf-8", newline="").write(t)
