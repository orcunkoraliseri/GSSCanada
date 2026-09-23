"""P10R (runs inside every Speed task, before the cell): every file in <repo>/mirror_md5.txt must exist
with its recorded md5. Exit 0 = all match; 1 = at least one missing/mismatched (task must not run)."""
import hashlib, sys
from pathlib import Path

repo = Path(sys.argv[1])
bad = 0
for ln in (repo / "mirror_md5.txt").read_text(encoding="utf-8").splitlines():
    if not ln.strip():
        continue
    m, rel = ln.split("  ", 1)
    p = repo / rel
    if not p.is_file():
        print("MISSING", rel); bad += 1; continue
    h = hashlib.md5()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    if h.hexdigest() != m:
        print("MD5 MISMATCH", rel, h.hexdigest(), "!=", m); bad += 1
print(f"[mirror] {'OK' if not bad else 'FAIL'}: {bad} problem(s)")
sys.exit(1 if bad else 0)
