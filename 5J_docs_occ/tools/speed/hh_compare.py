# -*- coding: utf-8 -*-
"""5J WP1 households: md5 compare of two output trees. usage: hh_compare.py <ref_dir> <new_dir> <label>
Every file in either tree is compared by md5. The two manifest lines that hold a LOCAL path
("hids_file", "corpus_path") are dropped from step9_manifest_*.json before hashing (they differ by
machine by construction); every other line must match. Prints one line per difference and a
final `COMPARE <label> PASS|FAIL ...` line; exit 0 on PASS, 1 on FAIL."""
import hashlib, os, sys

def files(root):
    out = {}
    for dp, _, fns in os.walk(root):
        for f in fns:
            p = os.path.join(dp, f)
            out[os.path.relpath(p, root).replace("\\", "/")] = p
    return out

def md5(path):
    data = open(path, "rb").read()
    if os.path.basename(path).startswith("step9_manifest_") and path.endswith(".json"):
        lines = data.decode("utf-8").splitlines(True)
        lines = [l for l in lines if '"hids_file"' not in l and '"corpus_path"' not in l]
        data = "".join(lines).encode("utf-8")
    return hashlib.md5(data).hexdigest()

def main():
    ref, new, label = sys.argv[1], sys.argv[2], sys.argv[3]
    a, b = files(ref), files(new)
    bad = 0
    for k in sorted(set(a) | set(b)):
        if k not in a:
            print("EXTRA in new: %s" % k); bad += 1
        elif k not in b:
            print("MISSING in new: %s" % k); bad += 1
        elif md5(a[k]) != md5(b[k]):
            print("DIFF: %s" % k); bad += 1
    print("COMPARE %s %s files_ref=%d files_new=%d different=%d" % (label, "PASS" if bad == 0 else "FAIL", len(a), len(b), bad))
    sys.exit(0 if bad == 0 else 1)

main()
