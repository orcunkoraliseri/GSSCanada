# -*- coding: utf-8 -*-
"""Journal-form pass: Fig. N / Table N, no duplicate alt-text captions, no comma
before the year in author-year citations. Applied identically to master + blinded."""
import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SUB = "C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/2J_docs_occ_nTemp/writing/submission"
FILES = [SUB + "/2J_manuscript_submission.md",
         SUB + "/submissionDocs/Blinded_Manuscript.md"]

for path in FILES:
    src = open(path, encoding="utf-8").read()
    t = src
    n = {}

    # 1. empty the image alt text -> pandoc stops emitting a duplicate caption line
    t, n["alt_emptied"] = re.subn(r"!\[Figure [^\]]*\]\(", "![](", t)

    # 2. caption run-ins -> journal form
    t, n["fig_captions"] = re.subn(r"^\*\*Figure (S?\d+)\.\*\* ", r"Fig. \1 ", t, flags=re.M)
    t, n["tbl_captions"] = re.subn(r"^\*\*Table (\d+)\.\*\* ",  r"Table \1 ", t, flags=re.M)

    # 3. in-text references -> Fig. N / Figs. N (headings left alone)
    lines = t.split("\n")
    c_sing = c_plur = 0
    for i, l in enumerate(lines):
        if l.startswith("#"):
            continue
        l, k = re.subn(r"\bFigures (?=S?\d)", "Figs. ", l); c_plur += k
        l, k = re.subn(r"\bFigure (?=S?\d)",  "Fig. ",  l); c_sing += k
        lines[i] = l
    t = "\n".join(lines)
    n["fig_refs"], n["figs_refs"] = c_sing, c_plur

    # 4. author-year citations: "(Author et al., 2020)" -> "(Author et al. 2020)"
    #    only inside the display text of a [text](#ref-...) cross-reference
    def decomma(m):
        return "[" + re.sub(r",(\s*(?:19|20)\d\d[a-z]?)$", r"\1", m.group(1)) + "](#" + m.group(2) + ")"
    t, _ = re.subn(r"\[([^\]]+)\]\(#(ref-[^)]+)\)", decomma, t)
    n["citations_decommaed"] = sum(
        1 for a, b in re.findall(r"\[([^\]]+)\]\(#(ref-[^)]+)\)", src)
        if re.search(r",\s*(?:19|20)\d\d[a-z]?$", a))

    open(path, "w", encoding="utf-8", newline="").write(t)
    print(path.split("/")[-1], n)
