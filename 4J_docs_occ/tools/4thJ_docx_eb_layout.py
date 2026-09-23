# -*- coding: utf-8 -*-
"""Energy and Buildings layout for a pandoc-built .docx: double-spaced body text and
continuous line numbers. Tables (style Compact / table cells) stay as built.

usage: py -3 4thJ_docx_eb_layout.py <in.docx> <out.docx>

Prints one line per patch with its count, so a patch that did not apply is visible.
Exit 1 if any patch applied zero times."""
import io, re, sys, zipfile

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
src, dst = sys.argv[1], sys.argv[2]

DOUBLE_STYLES = ("BodyText", "FirstParagraph", "Abstract", "Bibliography")
LNNUM = '<w:lnNumType w:countBy="1" w:restart="continuous"/>'

zin = zipfile.ZipFile(src)
styles = zin.read("word/styles.xml").decode("utf-8")
doc = zin.read("word/document.xml").decode("utf-8")

# 1. Double spacing on body-text paragraph styles.
n_double = 0
for sid in DOUBLE_STYLES:
    pat = re.compile(r'(<w:style [^>]*w:styleId="%s"[^>]*>)(.*?)(</w:style>)' % sid, re.S)
    m = pat.search(styles)
    if not m:
        print("style %s: not present (skipped)" % sid)
        continue
    body = m.group(2)
    if "<w:spacing" in body:
        body2 = re.sub(r'<w:spacing([^>]*?)\s*/>',
                       lambda s: '<w:spacing%s w:line="480" w:lineRule="auto"/>' % re.sub(
                           r'\s*w:line(Rule)?="[^"]*"', "", s.group(1)), body, count=1)
    elif "<w:pPr>" in body:
        body2 = body.replace("<w:pPr>", '<w:pPr><w:spacing w:line="480" w:lineRule="auto"/>', 1)
    elif "<w:pPr/>" in body:
        body2 = body.replace("<w:pPr/>", '<w:pPr><w:spacing w:line="480" w:lineRule="auto"/></w:pPr>', 1)
    else:
        body2 = re.sub(r'(</w:basedOn>|<w:basedOn [^>]*/>|<w:name [^>]*/>)',
                       lambda s: s.group(1) + '<w:pPr><w:spacing w:line="480" w:lineRule="auto"/></w:pPr>',
                       body, count=1)
    if body2 != body:
        styles = styles[:m.start(2)] + body2 + styles[m.end(2):]
        n_double += 1
        print("style %s: double spacing set" % sid)
print("PATCH double-spacing styles applied: %d" % n_double)

# 2. Continuous line numbers in every section.
# OOXML schema order inside sectPr: header/footerReference, footnotePr, endnotePr, type, pgSz,
# pgMar, paperSrc, pgBorders, lnNumType, pgNumType, cols, ... Word rejects out-of-order children,
# so lnNumType goes before the first child that must follow it (or before </w:sectPr>).
AFTER_LN = ("pgNumType", "cols", "formProt", "vAlign", "noEndnote", "titlePg", "textDirection",
            "bidi", "rtlGutter", "docGrid", "printerSettings", "sectPrChange")

def add_ln(m):
    body = m.group(2)
    if "<w:lnNumType" in body:
        return m.group(0)
    first = None
    for tag in AFTER_LN:
        k = body.find("<w:%s" % tag)
        if k >= 0 and (first is None or k < first):
            first = k
    if first is None:
        body = body + LNNUM
    else:
        body = body[:first] + LNNUM + body[first:]
    return m.group(1) + body + m.group(3)

doc, n_ln = re.subn(r'(<w:sectPr(?: [^>]*)?>)(.*?)(</w:sectPr>)', add_ln, doc, flags=re.S)
n_ln2 = 0
print("PATCH line numbers added to sections: %d" % (n_ln + n_ln2))

zout = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
for it in zin.infolist():
    data = zin.read(it.filename)
    if it.filename == "word/styles.xml":
        data = styles.encode("utf-8")
    elif it.filename == "word/document.xml":
        data = doc.encode("utf-8")
    zout.writestr(it, data)
zout.close()

if n_double == 0 or (n_ln + n_ln2) == 0:
    print("FAIL: a layout patch applied zero times")
    sys.exit(1)
print("OK: wrote %s" % dst)
