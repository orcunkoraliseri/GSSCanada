#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
assemble_3J.py -- build the combined 3J manuscript from the chapter/table/figure sources.

Run:  py -3 writing/fullSet/assemble_3J.py     (from 3J_docs_occ_nTemp/)

THE 2J LESSON THIS SCRIPT EXISTS TO PREVENT.
`2J_full_manuscript.md` and `readySubmission.md` silently diverged: one was built on a
superseded campaign, both carried the same modification date, and the difference was
invisible until every table was rebuilt from its own data.

Two mechanisms here, deliberately belt-and-braces:
  1. ONE SOURCE PASS. The document is assembled once, into a single in-memory string,
     and that same string is written to both output files. They cannot differ.
  2. A CAMPAIGN STAMP is prepended to both, naming the arm, the frozen source directory
     and its scorecard. Even if a future edit breaks mechanism 1, the stamp makes a
     divergence visible instead of silent.

Placeholders honoured inside a chapter, at the start of a line:
    **Table 5.** *(insert `Table_05_eui_bands.md` here)*
    **Figure 7.** *(insert `Figure_07_eui_4ch.png` here)*
Anything not inlined at a placeholder is appended to an explicit appendix and REPORTED,
so nothing is dropped quietly.
"""

import hashlib
import io
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))          # .../writing/fullSet
WRITING = os.path.dirname(BASE)                            # .../writing
CH = os.path.join(WRITING, "chapters")
TBL = os.path.join(WRITING, "tables")
TBL_SI = os.path.join(TBL, "SI")
FIG = os.path.join(WRITING, "figures")
FIG_SI = os.path.join(FIG, "SI")

ORDER = [
    "Chapter_00_FrontMatter.md",
    "Chapter_01_Introduction.md",
    "Chapter_02_Datasets.md",
    "Chapter_03_Methods.md",
    "Chapter_04_ExperimentalDesign.md",
    "Chapter_05_Results.md",
    "Chapter_06_Discussion.md",
    "Chapter_07_Limitations.md",
    "Chapter_08_Conclusion.md",
]

# The arm the paper reports. Read from
# Leg3_4-split/Step9_docs/outputs_step9_deliverable/_PROVENANCE.md, identity block.
CAMPAIGN_STAMP = """<!-- CAMPAIGN IDENTIFIER -- do not edit by hand; written by assemble_3J.py -->

> **Campaign identifier.** Every measured number in this manuscript comes from
> `Leg3_4-split/Step9_docs/outputs_step9_deliverable/`, frozen 2026-08-06 00:05, registered in
> `improvements/v2/V2-G1_FROZEN_DELIVERABLE.md`.
> Arm: **base + V2-D9 (retail `NECB-C`) + V2-D10 (per-object DHW resize)**.
> Cells **56 / 56**. Scorecard **17 PASS / 10 INFO / 3 FAIL** over 30 gates; the three FAILs
> (`S9-EUI-office`, `S9-EUI-retail`, `S9-EUI-hotel`) are **left failing on purpose**.
> Platform `win32`, EnergyPlus 24.2.0 build `94a887817b`.
> The identically-named sibling `outputs_step9/` (2026-07-31) is **superseded** and is not a source
> for anything here; it inverts the hotel result.
>
> This file and its sibling in `fullSet/` were written from **one assembly pass** of the same
> in-memory document. If they ever differ, one of them was edited by hand after the build.

"""

TBL_PAT = re.compile(r"^\*\*(?P<lbl>Table [A-Z]?\d+)\.\*\*\s*\*\(insert `(?P<f>[^`]+)` here\)\*(?P<rest>.*)$")
FIG_PAT = re.compile(r"^\*\*(?P<lbl>Figure S?\d+|Graphical abstract)\.\*\*\s*\*\(insert `(?P<f>[^`]+)` here\)\*(?P<rest>.*)$")


def find(name, dirs):
    for d in dirs:
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    return None


def read(p):
    with io.open(p, encoding="utf-8") as fh:
        return fh.read()


def inline_table(name):
    """Return a table file's body, minus its own top-level heading."""
    p = find(name, [TBL, TBL_SI])
    if not p:
        return None, "*(table file %s NOT FOUND)*" % name
    lines = read(p).splitlines()
    out = [l for l in lines if not re.match(r"^#\s", l)]
    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()
    return p, "\n".join(out)


def main():
    missing_ch = [c for c in ORDER if not os.path.exists(os.path.join(CH, c))]
    if missing_ch:
        sys.stderr.write("MISSING CHAPTERS: %s\n" % ", ".join(missing_ch))
        return 2

    parts = [CAMPAIGN_STAMP]
    inlined_tables, inlined_figs = [], []

    for chapter in ORDER:
        for line in read(os.path.join(CH, chapter)).splitlines():
            mt = TBL_PAT.match(line)
            if mt:
                p, body = inline_table(mt.group("f"))
                if p:
                    inlined_tables.append(mt.group("f"))
                parts.append("**%s.**%s\n\n%s\n" % (mt.group("lbl"), mt.group("rest"), body))
                continue
            mf = FIG_PAT.match(line)
            if mf:
                fname = mf.group("f")
                p = find(fname, [FIG, FIG_SI])
                if p:
                    inlined_figs.append(fname)
                    rel = os.path.relpath(p, BASE).replace("\\", "/")
                    parts.append("**%s.**%s\n\n![%s](%s)\n" % (mf.group("lbl"), mf.group("rest"), mf.group("lbl"), rel))
                else:
                    parts.append("**%s.**%s\n\n*(figure file %s NOT FOUND)*\n" % (mf.group("lbl"), mf.group("rest"), fname))
                continue
            parts.append(line)
        parts.append("\n\n---\n")

    # Anything not inlined goes into an explicit appendix. Nothing is dropped silently.
    all_tables = sorted(
        [f for f in os.listdir(TBL) if f.endswith(".md")]
        + [f for f in os.listdir(TBL_SI) if f.endswith(".md")]
    )
    left_tables = [t for t in all_tables if t not in inlined_tables]
    if left_tables:
        parts.append("\n# Appendix: tables not inlined at a placeholder\n")
        parts.append(
            "*These table files exist in `writing/tables/` but no chapter carried an "
            "`*(insert ... here)*` placeholder for them. They are appended in full rather than "
            "dropped. Placing them is an editorial pass, not a data question.*\n"
        )
        for t in left_tables:
            p, body = inline_table(t)
            parts.append("\n## %s\n\n%s\n" % (t, body))

    all_figs = sorted(
        [f for f in os.listdir(FIG) if f.lower().endswith(".png")]
        + [f for f in os.listdir(FIG_SI) if f.lower().endswith(".png")]
    )
    left_figs = [f for f in all_figs if f not in inlined_figs]
    if left_figs:
        parts.append("\n# Appendix: figures not inlined at a placeholder\n")
        for f in left_figs:
            p = find(f, [FIG, FIG_SI])
            rel = os.path.relpath(p, BASE).replace("\\", "/")
            parts.append("\n**%s**\n\n![%s](%s)\n" % (f, f, rel))

    doc = "\n".join(parts)

    # ONE string, TWO files. This is mechanism 1.
    outs = [os.path.join(BASE, "3J_full_manuscript.md"), os.path.join(BASE, "readySubmission.md")]
    for o in outs:
        with io.open(o, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(doc)

    h = hashlib.md5(doc.encode("utf-8")).hexdigest()
    print("assembled %d chapters" % len(ORDER))
    print("  tables inlined at a placeholder : %d  %s" % (len(inlined_tables), inlined_tables))
    print("  tables appended to the appendix : %d  %s" % (len(left_tables), left_tables))
    print("  figures inlined at a placeholder: %d  %s" % (len(inlined_figs), inlined_figs))
    print("  figures appended to the appendix: %d  %s" % (len(left_figs), left_figs))
    print("  document md5 (both files)       : %s" % h)
    for o in outs:
        with io.open(o, encoding="utf-8") as fh:
            got = hashlib.md5(fh.read().encode("utf-8")).hexdigest()
        print("  %-24s %s  %s" % (os.path.basename(o), got, "OK" if got == h else "MISMATCH"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
