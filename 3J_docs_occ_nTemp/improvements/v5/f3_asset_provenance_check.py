#!/usr/bin/env python3
"""V5-F3 -- verify manuscript assets by CONTENT against the frozen arm.

WHY THIS EXISTS, and why F1 is not enough. `f1_frozen_input_check.py` catches a *script* that names
or assembles a superseded path. It cannot catch the failure this one is for: a figure copied out of
`Step9_docs/outputs_step9/` (2026-07-31, superseded) into `writing/figures/` and renamed on the way
to `Figure_07_eui_4ch.png`. After the rename there is no path string left to check. The only thing
that still carries the origin is the bytes.

THE COLLISION. The frozen arm `outputs_step9_deliverable/` and its superseded sibling
`outputs_step9/` carry the SAME 11 filenames. Ten differ. One -- `fig_diurnal_4ch.png` -- is
byte-identical in both.

🔴 That one file is reported AMBIGUOUS, never PASS. A content check has no signal there: both
directories are correct answers. Reporting it as PASS would claim coverage this check does not have,
which is the same class of error the check was written to catch.

THE REGISTRY IS NOT HARD-CODED. Expected md5s are read from the freeze document
(`improvements/v2/V2-G1_FROZEN_DELIVERABLE.md`, section "Step-9 deliverable assets"). The superseded
hashes are computed from disk at run time. If a later round freezes a different arm and updates the
freeze doc, this check follows it.

FIVE CHECKS:
  C1  no manuscript asset matches a SUPERSEDED-arm hash.
  C2  every manuscript asset that looks like a Step-9 asset matches a FROZEN hash (or is ambiguous).
  C3  the registry is non-empty and every hash in it is 32 hex chars -- a registry that silently came
      up empty, or carries a truncated/typed hash, passes everything.
  C4  every frozen hash in the registry actually matches the file on disk. The freeze doc is a claim
      about the tree; if it has drifted, C1/C2 are checking against fiction.
  C5  at least one asset in the registry is distinguishable between the two arms, so C1 CAN fail.
      A check that cannot fail is not a check, it is a comment. This also PRINTS the ambiguous set,
      so the gap is stated rather than hidden.

    python f3_asset_provenance_check.py [--falsify]

--falsify copies a superseded figure into a temp tree under a manuscript filename and scans that
instead, so C1 is seen failing on a real line rather than assumed to work.
"""
import argparse
import hashlib
import io
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
IMPROVEMENTS = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(IMPROVEMENTS, ".."))          # 3J_docs_occ_nTemp/
FREEZE_DOC = os.path.join(IMPROVEMENTS, "v2", "V2-G1_FROZEN_DELIVERABLE.md")
FROZEN_DIR = os.path.join(ROOT, "Leg3_4-split", "Step9_docs", "outputs_step9_deliverable")
SUPERSEDED_DIR = os.path.join(ROOT, "Leg3_4-split", "Step9_docs", "outputs_step9")
WRITING = os.path.join(ROOT, "writing")

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SECTION = "## Step-9 deliverable assets"
# | `figures/fig_eui_4ch.png` | `b17ca5e2...` |
ROW = re.compile(r"^\|\s*`([A-Za-z0-9_./-]+)`\s*\|\s*`([0-9a-fA-F]+)`\s*\|")
ASSET_EXT = (".png", ".csv", ".json", ".html")

_N = {"pass": 0, "fail": 0}


def rec(tag, ok, detail):
    _N["pass" if ok else "fail"] += 1
    print("  [%s] %-3s %s" % ("PASS" if ok else "FAIL", tag, detail))


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def registry():
    """{relpath: md5} read from the freeze document's asset section only."""
    with io.open(FREEZE_DOC, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.startswith(SECTION))
    except StopIteration:
        return {}
    out = {}
    for line in lines[start + 1:]:
        if line.startswith("## "):                    # next section ends the block
            break
        m = ROW.match(line)
        if m:
            out[m.group(1)] = m.group(2).lower()
    return out


def hashes_in(root):
    """{md5: [relpath, ...]} for one arm on disk."""
    out = {}
    for dirpath, _dirs, files in os.walk(root):
        for name in files:
            if not name.lower().endswith(ASSET_EXT):
                continue
            p = os.path.join(dirpath, name)
            rel = os.path.relpath(p, root).replace("\\", "/")
            out.setdefault(md5(p), []).append(rel)
    return out


def manuscript_assets(root):
    """[(relpath, md5)] for every asset under the writing tree."""
    out = []
    if not os.path.isdir(root):
        return out
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d != "archive"]   # archived copies are history, not claims
        for name in files:
            if not name.lower().endswith(ASSET_EXT):
                continue
            p = os.path.join(dirpath, name)
            out.append((os.path.relpath(p, root).replace("\\", "/"), md5(p)))
    return sorted(out)


def build_falsify_tree():
    """A manuscript tree containing one figure copied from the SUPERSEDED arm."""
    tmp = tempfile.mkdtemp(prefix="f2_falsify_")
    figs = os.path.join(tmp, "figures")
    os.makedirs(figs)
    # the copy is renamed on the way in -- exactly the case F1 cannot see
    shutil.copyfile(os.path.join(SUPERSEDED_DIR, "figures", "fig_eui_4ch.png"),
                    os.path.join(figs, "Figure_07_eui_4ch.png"))
    # and one honest copy from the frozen arm, so the check is not trivially all-red
    shutil.copyfile(os.path.join(FROZEN_DIR, "figures", "fig_peakhour_4ch.png"),
                    os.path.join(figs, "Figure_09_peakhour_4ch.png"))
    return tmp


def main(falsify):
    reg = registry()
    frozen_disk = hashes_in(FROZEN_DIR)
    sup_disk = hashes_in(SUPERSEDED_DIR)

    frozen_hashes = set(reg.values())
    sup_hashes = set(sup_disk)
    ambiguous = frozen_hashes & sup_hashes          # identical in both arms -> no signal

    print("V5-F3 -- manuscript asset provenance%s" % ("   FALSIFY MODE" if falsify else ""))
    print("  registry, read from %s:" % os.path.relpath(FREEZE_DOC, ROOT).replace("\\", "/"))
    print("    %d asset(s) registered; %d superseded-arm hash(es) on disk"
          % (len(reg), len(sup_disk)))

    scan_root = build_falsify_tree() if falsify else WRITING
    assets = manuscript_assets(scan_root)
    print("  scanning %d asset(s) in %s\n"
          % (len(assets), scan_root if falsify else os.path.relpath(scan_root, ROOT).replace("\\", "/")))

    # ---- C1 -------------------------------------------------------------- superseded bytes
    hits = [(rel, h) for rel, h in assets if h in sup_hashes and h not in ambiguous]
    rec("C1", not hits,
        "no manuscript asset carries superseded-arm bytes" if not hits
        else "%d asset(s) copied from the SUPERSEDED arm:" % len(hits))
    for rel, h in hits:
        print("        %s  (md5 %s)  == outputs_step9/%s" % (rel, h[:8], ", ".join(sup_disk[h])))

    # ---- C2 -------------------------------------------------------------- unknown bytes
    known = frozen_hashes | sup_hashes
    unknown = [(rel, h) for rel, h in assets if h not in known]
    rec("C2", not unknown,
        "every scanned asset traces to a known arm" if not unknown
        else "%d asset(s) match neither arm (regenerated? edited? another source?):" % len(unknown))
    for rel, h in unknown:
        print("        %s  (md5 %s)" % (rel, h[:8]))

    # ---- C3 -------------------------------------------------------------- registry sane
    bad = [k for k, v in reg.items() if len(v) != 32 or not re.fullmatch(r"[0-9a-f]{32}", v)]
    rec("C3", bool(reg) and not bad,
        "%d registered hash(es), all 32 hex chars" % len(reg) if reg and not bad
        else "registry empty or malformed: %s" % (bad or "EMPTY"))

    # ---- C4 -------------------------------------------------------------- registry vs disk
    drift = []
    for rel, want in reg.items():
        p = os.path.join(FROZEN_DIR, rel)
        if not os.path.isfile(p):
            drift.append((rel, want, "MISSING ON DISK"))
        else:
            got = md5(p)
            if got != want:
                drift.append((rel, want, got))
    rec("C4", not drift,
        "every registered hash matches the frozen arm on disk" if not drift
        else "%d registered hash(es) do not match the tree:" % len(drift))
    for rel, want, got in drift:
        print("        %s  doc %s  disk %s" % (rel, want[:8], got[:8] if got != "MISSING ON DISK" else got))

    # ---- C5 -------------------------------------------------------------- can C1 fail at all
    distinguishable = frozen_hashes - ambiguous
    rec("C5", bool(distinguishable),
        "%d of %d registered asset(s) are distinguishable between arms, so C1 can fail"
        % (len(distinguishable), len(reg)) if distinguishable
        else "every registered asset is identical in both arms -- C1 is vacuous")
    if ambiguous:
        names = sorted({n for h in ambiguous for n in frozen_disk.get(h, [])})
        print("        AMBIGUOUS, byte-identical in both arms -- content cannot establish origin:")
        for n in names:
            print("          %s   (record its provenance at copy time; this check will never see it)" % n)

    if not assets:
        print("\n  ⚠ no manuscript assets scanned yet -- C1/C2 are vacuous until figures are copied.")
        print("    Run with --falsify to confirm C1 still fails on a real superseded copy.")

    if falsify:
        shutil.rmtree(scan_root, ignore_errors=True)

    print("\n  %d PASS / %d FAIL" % (_N["pass"], _N["fail"]))
    return 0 if _N["fail"] == 0 else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--falsify", action="store_true",
                    help="scan a temp tree containing a superseded figure renamed to a manuscript name")
    a = ap.parse_args()
    sys.exit(main(a.falsify))
