# -*- coding: utf-8 -*-
"""Post-process a pandoc build: table text 10 pt and single spaced.
usage: py post.py <in.docx> <out.docx>"""
import zipfile, re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SZ = '<w:sz w:val="20"/><w:szCs w:val="20"/>'
SINGLE = '<w:spacing w:after="0" w:line="240" w:lineRule="auto"/>'
src, dst = sys.argv[1], sys.argv[2]

zin = zipfile.ZipFile(src)
x = zin.read("word/document.xml").decode("utf-8")

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

def in_table(tbl):
    tbl = re.sub(r"<w:r>.*?</w:r>", fix_run, tbl, flags=re.S)
    return re.sub(r"<w:p>.*?</w:p>|<w:p/>", fix_para, tbl, flags=re.S)

out, pos, n = [], 0, 0
for m in re.finditer(r"<w:tbl>.*?</w:tbl>", x, re.S):
    out.append(x[pos:m.start()]); out.append(in_table(m.group(0))); pos = m.end(); n += 1
out.append(x[pos:])
x = "".join(out)

zout = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
for it in zin.infolist():
    d = zin.read(it.filename)
    if it.filename == "word/document.xml": d = x.encode("utf-8")
    zout.writestr(it, d)
zout.close(); zin.close()

from xml.etree import ElementTree as ET
z = zipfile.ZipFile(dst); assert z.testzip() is None
for nm in z.namelist():
    if nm.endswith(".xml") or nm.endswith(".rels"): ET.fromstring(z.read(nm))
print("%s -> %s | tables %d | xml ok" % (src, dst, n))
