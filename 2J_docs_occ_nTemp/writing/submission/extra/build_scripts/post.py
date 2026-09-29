# -*- coding: utf-8 -*-
"""Post-process a pandoc build.
- table text 10 pt and single spaced;
- table column widths set from the cell content (author comment 2026-09-25);
- figure and table captions, and figure images, centred (author comment 2026-09-25);
- Title style 16 pt bold instead of 28 pt (author comment 2026-09-25).
usage: py post.py <in.docx> <out.docx>"""
import zipfile, re, io, sys, html
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SZ = '<w:sz w:val="20"/><w:szCs w:val="20"/>'
SINGLE = '<w:spacing w:after="0" w:line="240" w:lineRule="auto"/>'
CELL_MAR = ('<w:tblCellMar><w:left w:w="72" w:type="dxa"/>'
            '<w:right w:w="72" w:type="dxa"/></w:tblCellMar>')
PAD = 144              # left + right cell margin, twips
CH = 95                # twips per character of 10 pt Times New Roman, a slightly generous mean
TEXT_W = 9360          # text width in twips: Letter, 1 in margins (the page Word gives these files)
CAPTION = re.compile(r"^(Figure|Table) (S\d+|[A-Z]\.\d+|\d+)\.(\s|$)")
src, dst = sys.argv[1], sys.argv[2]

zin = zipfile.ZipFile(src)
x = zin.read("word/document.xml").decode("utf-8")
styles = zin.read("word/styles.xml").decode("utf-8")

def text(frag):
    return html.unescape("".join(re.findall(r"<w:t(?: [^>]*)?>([^<]*)</w:t>", frag)))

def fix_run(m):
    r = m.group(0)
    if "<w:rPr>" in r:
        r = re.sub(r'<w:sz w:val="\d+"\s*/>|<w:szCs w:val="\d+"\s*/>', "", r)
        return r.replace("<w:rPr>", "<w:rPr>" + SZ, 1)
    return r.replace("<w:r>", "<w:r><w:rPr>" + SZ + "</w:rPr>", 1)

def fix_para(m):
    p = m.group(0)
    p = re.sub(r'<w:spacing [^/]*/>', "", p)
    if "<w:pPr>" in p:
        return p.replace("<w:pPr>", "<w:pPr>" + SINGLE, 1)
    return p.replace("<w:p>", "<w:p><w:pPr>" + SINGLE + "</w:pPr>", 1)

def col_widths(texts_by_col, total):
    """Width of each column in proportion to its mean cell length (body rows), never narrower
    than its longest unbreakable word (header included; Word breaks after a hyphen)."""
    need, pref = [], []
    for col in texts_by_col:
        toks = [t for c in col for t in re.split(r"[\s/]+|(?<=-)", c) if t]
        longest = max([len(t) for t in toks] or [1])
        need.append(longest * CH + PAD)
        body = col[1:] or col
        pref.append(max(sum(len(c) for c in body) / float(len(body)), longest, 1.0))
    if sum(need) >= total:                       # cannot honour every word: scale the minima
        return [int(total * n / float(sum(need))) for n in need]
    w = [None] * len(need)
    while True:                                  # pin columns that fall below their minimum
        free = [i for i in range(len(w)) if w[i] is None or w[i] != need[i]]
        rest = total - sum(need[i] for i in range(len(w)) if i not in free)
        sp = sum(pref[i] for i in free)
        trial = {i: rest * pref[i] / sp for i in free}
        low = [i for i in free if trial[i] < need[i]]
        if not low:
            for i in free: w[i] = int(trial[i])
            break
        for i in low: w[i] = need[i]
    w[-1] += total - sum(w)
    return w

def set_widths(tbl):
    if "gridSpan" in tbl or tbl.count("<w:tbl>") > 1:
        return tbl, False
    grid = [int(g) for g in re.findall(r'<w:gridCol w:w="(\d+)"\s*/>', tbl)]
    rows = re.findall(r"<w:tr[ >].*?</w:tr>", tbl, re.S)
    cells = [re.findall(r"<w:tc>.*?</w:tc>", r, re.S) for r in rows]
    if not grid or any(len(c) != len(grid) for c in cells):
        return tbl, False
    cols = [[text(r[j]) for r in cells] for j in range(len(grid))]
    w = col_widths(cols, TEXT_W)
    tbl = re.sub(r"<w:tblGrid>.*?</w:tblGrid>",
                 "<w:tblGrid>" + "".join('<w:gridCol w:w="%d"/>' % v for v in w) + "</w:tblGrid>",
                 tbl, count=1, flags=re.S)
    def fix_row(m):
        k = [0]
        def fix_tc(mc):
            tc = mc.group(0); j = k[0]; k[0] += 1
            tcw = '<w:tcW w:w="%d" w:type="dxa"/>' % w[j]
            if re.search(r"<w:tcW [^>]*/>", tc):
                return re.sub(r"<w:tcW [^>]*/>", tcw, tc, count=1)
            if "<w:tcPr>" in tc:
                return tc.replace("<w:tcPr>", "<w:tcPr>" + tcw, 1)
            return tc.replace("<w:tc>", "<w:tc><w:tcPr>" + tcw + "</w:tcPr>", 1)
        return re.sub(r"<w:tc>.*?</w:tc>", fix_tc, m.group(0), flags=re.S)
    tbl = re.sub(r"<w:tr[ >].*?</w:tr>", fix_row, tbl, flags=re.S)
    if "<w:tblCellMar>" not in tbl.split("</w:tblPr>")[0]:
        tbl = tbl.replace("<w:tblLook ", CELL_MAR + "<w:tblLook ", 1)
    return tbl, True

def in_table(tbl):
    tbl, ok = set_widths(tbl)
    tbl = re.sub(r"<w:r>.*?</w:r>", fix_run, tbl, flags=re.S)
    return re.sub(r"<w:p>.*?</w:p>|<w:p/>", fix_para, tbl, flags=re.S), ok

def centre(p, keep_next):
    extra_first = "<w:keepNext/>" if keep_next else ""
    if "<w:pPr>" not in p:
        return p.replace("<w:p>", "<w:p><w:pPr>%s<w:jc w:val=\"center\"/></w:pPr>" % extra_first, 1)
    ppr = re.search(r"<w:pPr>.*?</w:pPr>", p, re.S).group(0)
    new = re.sub(r"<w:jc [^>]*/>", "", ppr)
    if extra_first and not re.search(r"<w:keepNext\s*/>", new):
        new = re.sub(r"(<w:pStyle [^>]*/>)", r"\1" + extra_first, new, count=1) \
            if "<w:pStyle " in new else new.replace("<w:pPr>", "<w:pPr>" + extra_first, 1)
    tail = "<w:rPr>" if "<w:rPr>" in new else "</w:pPr>"
    new = new.replace(tail, '<w:jc w:val="center"/>' + tail, 1)
    return p.replace(ppr, new, 1)

counts = {"cap": 0, "img": 0}
def fix_body_para(m):
    p = m.group(0)
    if "<w:drawing>" in p:
        counts["img"] += 1
        return centre(p, True)          # the image stays on the page of its caption below
    first_run = re.search(r"<w:r>.*?</w:r>", p, re.S)
    t = text(p).strip()
    if first_run and re.search(r"<w:b\s*/>", first_run.group(0)) and CAPTION.match(t):
        counts["cap"] += 1
        return centre(p, t.startswith("Table"))   # a table caption stays with its table
    return p

out, pos, n, nw = [], 0, 0, 0
for m in re.finditer(r"<w:tbl>.*?</w:tbl>", x, re.S):
    out.append(re.sub(r"<w:p>.*?</w:p>", fix_body_para, x[pos:m.start()], flags=re.S))
    t, ok = in_table(m.group(0)); out.append(t); pos = m.end(); n += 1; nw += ok
out.append(re.sub(r"<w:p>.*?</w:p>", fix_body_para, x[pos:], flags=re.S))
x = "".join(out)

m = re.search(r'<w:style [^>]*w:styleId="Title".*?</w:style>', styles, re.S)
title_ok = False
if m:
    st = m.group(0)
    st2 = re.sub(r'<w:sz w:val="\d+"\s*/>', '<w:sz w:val="32"/>', st)
    st2 = re.sub(r'<w:szCs w:val="\d+"\s*/>', '<w:szCs w:val="32"/>', st2)
    if not re.search(r"<w:b\s*/>", st2):
        st2 = re.sub(r"(<w:rFonts [^>]*/>)", r"\1<w:b/><w:bCs/>", st2, count=1)
    styles = styles.replace(st, st2, 1)
    title_ok = 'w:val="32"' in st2

zout = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
for it in zin.infolist():
    d = zin.read(it.filename)
    if it.filename == "word/document.xml": d = x.encode("utf-8")
    if it.filename == "word/styles.xml": d = styles.encode("utf-8")
    zout.writestr(it, d)
zout.close(); zin.close()

from xml.etree import ElementTree as ET
z = zipfile.ZipFile(dst); assert z.testzip() is None
for nm in z.namelist():
    if nm.endswith(".xml") or nm.endswith(".rels"): ET.fromstring(z.read(nm))
print("%s -> %s | tables %d | widths set %d | captions centred %d | images centred %d | title 16pt %s | xml ok"
      % (src, dst, n, nw, counts["cap"], counts["img"], title_ok))
