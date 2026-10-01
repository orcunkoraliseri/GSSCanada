"""Build the 1J R1 manuscript .docx from 1J_manuscript_R1.md (the .md is never modified).

Steps: include generated tables ([[TABLE n = path]] markers), number citations [@key; @key2] in order of first
appearance, write the numbered reference list from R1_references.md, then pandoc (2J submission reference doc),
post.py and eb_layout.py (double spacing + line numbers) from the 2J build scripts.

Gate: `--final` refuses to build while any [[...]] marker remains in the text or in a cited reference entry.
Without `--final` it builds a DRAFT and lists the open markers.
`--anon` (with `--final`) writes 1J_manuscript_R1_anonymous.docx for the journal's anonymous review copy: author block,
CRediT and funding text removed, "by the same authors" dropped, and the two self-citation entries anonymised. Each
anonymising patch prints its own line; the build refuses if any author name, affiliation or e-mail is left.
"""
import os
import re
import subprocess
import sys

SRC = os.path.dirname(os.path.abspath(__file__))  # manuscript/resources: .md sources + this script
MAN = os.path.dirname(SRC)  # manuscript/: built .docx files (the upload folder)
ROOT = os.path.normpath(os.path.join(MAN, "..", ".."))
BS = os.path.join(ROOT, "2J_docs_occ_nTemp", "writing", "submission", "extra", "build_scripts")
SCR = os.environ.get("TEMP", MAN)
FINAL = "--final" in sys.argv
ANON = "--anon" in sys.argv

src = open(os.path.join(SRC, "1J_manuscript_R1.md"), encoding="utf-8").read()


def include(m):
    path = os.path.normpath(os.path.join(MAN, "..", m.group(1).strip()))
    return open(path, encoding="utf-8").read().strip()


src = re.sub(r"\[\[TABLE [A-Z]?\d+ = ([^\]]+)\]\]", include, src)

ANON_TEXT = "Removed for anonymous review."
ANON_PATCHES = [
    ("author block", r"\nOrcun Koral Iseri\^a.*?\n\\\* Corresponding author\.[^\n]*\n", "\n"),
    ("same authors", r"a companion study by the same authors \[", "a companion study ["),
    ("CRediT", r"(# CRediT authorship contribution statement\n\n)[^\n]+", r"\g<1>" + ANON_TEXT),
    ("funding", r"(# Funding\n\n)[^\n]+", r"\g<1>" + ANON_TEXT),
]
if ANON:
    for name, pat, new in ANON_PATCHES:
        src, n = re.subn(pat, new, src, count=1, flags=re.S)
        print(f"ANON PATCH {name}: {'APPLIED' if n == 1 else 'MISSING'}")
        if n != 1:
            raise SystemExit(f"ANON BUILD REFUSED: patch '{name}' did not apply")

refs = {}
checks = {}
for line in open(os.path.join(SRC, "R1_references.md"), encoding="utf-8"):
    m = re.match(r"^([a-z0-9_]+): (.+)$", line.strip())
    if m:
        refs[m.group(1)] = m.group(2)
    m = re.match(r"^CHECK ([a-z0-9_]+):", line.strip())
    if m:
        checks[m.group(1)] = True
if ANON:
    for k in ("iseri2026b", "iseri2026esim"):
        refs[k] = "Anonymised for review."
        print(f"ANON PATCH reference {k}: APPLIED")

order = []


def cite(m):
    keys = [k.strip().lstrip("@") for k in m.group(1).split(";")]
    nums = []
    for k in keys:
        if k not in refs:
            raise SystemExit(f"UNKNOWN CITATION KEY: {k}")
        if k not in order:
            order.append(k)
        nums.append(order.index(k) + 1)
    nums = sorted(set(nums))
    # compress runs: 1,2,3 -> 1-3
    parts, i = [], 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        parts.append(f"{nums[i]}–{nums[j]}" if j - i >= 2 else ", ".join(str(n) for n in nums[i:j + 1]))
        i = j + 1
    return "[" + ", ".join(parts) + "]"


src = re.sub(r"\[(@[^\]]+)\]", cite, src)
reflist = "\n\n".join(f"[{i + 1}] {refs[k]}" for i, k in enumerate(order))
src = re.sub(r"\[\[REFERENCES[^\]]*\]\]", lambda m: reflist, src)

open_markers = re.findall(r"\[\[[^\]]*\]\]", src)
unchecked = [k for k in order if k in checks]
print(f"citations: {len(order)} references cited; {len(refs) - len(order)} entries unused: "
      f"{sorted(set(refs) - set(order))}")
print(f"open markers: {len(open_markers)}")
for mk in open_markers:
    print("   ", mk[:110])
print(f"references still marked CHECK for the author: {len(unchecked)}: {unchecked}")
if FINAL and (open_markers or unchecked):
    raise SystemExit("FINAL BUILD REFUSED: open markers or unchecked references remain")

words = len(re.sub(r"!\[[^\]]*\]\([^)]*\)|\|[^\n]*\||\$\$.*?\$\$", " ", src.split("# CRediT")[0], flags=re.S).split())
print(f"approx. words before declarations (tables/figures/equations excluded): {words}")

tmp_md = os.path.join(SCR, "r1_build.md")
open(tmp_md, "w", encoding="utf-8").write(src)
if ANON:
    # third-person citations of the co-author's published work are allowed (journal's anonymous-review guidance)
    third_person = [refs[k] for k in ("hachem2025", "hachem2023") if k in order]
    body = src.replace(reflist, "\n\n".join(refs[k] for k in order if k not in ("hachem2025", "hachem2023")))
    left = re.findall(r"iseri|hachem|vermette|concordia|gina cody|volt-age|oseri@|same authors", body, re.I)
    print(f"ANON CHECK third-person reference entries kept: {len(third_person)}")
    print(f"ANON CHECK identifying words left: {len(left)} {sorted(set(w.lower() for w in left))}")
    if left:
        raise SystemExit("ANON BUILD REFUSED: identifying words remain")
out_name = ("1J_manuscript_R1_anonymous.docx" if ANON else "1J_manuscript_R1.docx") if FINAL else "1J_manuscript_R1_DRAFT.docx"
tmp_docx = os.path.join(SCR, "r1_pandoc.docx")
r = subprocess.run(["pandoc", tmp_md, "-f", "markdown", "-t", "docx", "--reference-doc",
                    os.path.join(BS, "ref_submit.docx"), "--columns=10", "--resource-path=" + MAN,
                    "-o", tmp_docx], capture_output=True, text=True)
print("pandoc rc", r.returncode, "stderr:", r.stderr.strip() or "(none)")
assert r.returncode == 0
tmp_post = os.path.join(SCR, "r1_post.docx")
r2 = subprocess.run([sys.executable, os.path.join(BS, "post.py"), tmp_docx, tmp_post], capture_output=True, text=True)
print("post.py rc", r2.returncode, r2.stdout.strip()[-300:], r2.stderr.strip()[-300:])
r3 = subprocess.run([sys.executable, os.path.join(BS, "eb_layout.py"), tmp_post if r2.returncode == 0 else tmp_docx,
                     os.path.join(MAN, out_name)], capture_output=True, text=True)
print("eb_layout.py rc", r3.returncode, r3.stdout.strip()[-300:], r3.stderr.strip()[-300:])
assert r3.returncode == 0
print("written", os.path.join(MAN, out_name))
