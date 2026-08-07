# -*- coding: utf-8 -*-
"""ref_submit.docx = ref_final.docx + the journal's export rules:
12 pt Times Roman, double spaced, automatic page numbers in a centred footer.
Captions and table cells stay single spaced."""
import zipfile, re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WNS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
RNS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
zin = zipfile.ZipFile("ref_final.docx")
parts = {n: zin.read(n) for n in zin.namelist()}
order = zin.namelist()[:]
zin.close()

TIMES = ('<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" '
         'w:eastAsia="Times New Roman" w:cs="Times New Roman"/>')
DOUBLE = '<w:spacing w:after="0" w:line="480" w:lineRule="auto"/>'
SINGLE = '<w:spacing w:after="0" w:line="240" w:lineRule="auto"/>'

# ---- 1. document defaults: Times, 12 pt, double spaced -----------------------
s = parts["word/styles.xml"].decode("utf-8")
s = re.sub(r'<w:rFonts w:asciiTheme[^/]*/>', TIMES, s, count=1)
s = re.sub(r'<w:pPrDefault>\s*<w:pPr>.*?</w:pPr>\s*</w:pPrDefault>',
           '<w:pPrDefault><w:pPr>' + DOUBLE + '</w:pPr></w:pPrDefault>', s, count=1, flags=re.S)

# ---- 2. captions single spaced (they are 10 pt already) ---------------------
def add_ppr(sid, frag):
    global s
    m = re.search(r'(<w:style [^>]*w:styleId="%s"[^>]*>)(.*?)(</w:style>)' % sid, s, re.S)
    if not m:
        print("   ! missing style:", sid); return
    body = m.group(2)
    body = (body.replace("<w:pPr>", "<w:pPr>" + frag, 1) if "<w:pPr>" in body
            else re.sub(r"(</w:name>)", r"\1<w:pPr>" + frag + "</w:pPr>", body, count=1))
    s = s[:m.start(2)] + body + s[m.end(2):]
for sid in ["Caption", "TableCaption", "ImageCaption"]:
    if re.search(r'w:styleId="%s"' % sid, s):
        add_ppr(sid, SINGLE)
parts["word/styles.xml"] = s.encode("utf-8")

# ---- 3. footer part with an automatic PAGE field ----------------------------
RPR = '<w:rPr>' + TIMES + '<w:sz w:val="24"/><w:szCs w:val="24"/></w:rPr>'
def run(inner): return "<w:r>" + RPR + inner + "</w:r>"
footer = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<w:ftr xmlns:w="%s" xmlns:r="%s"><w:p><w:pPr>%s<w:jc w:val="center"/></w:pPr>%s%s%s%s%s</w:p></w:ftr>'
    % (WNS, RNS, SINGLE,
       run('<w:fldChar w:fldCharType="begin"/>'),
       run('<w:instrText xml:space="preserve"> PAGE </w:instrText>'),
       run('<w:fldChar w:fldCharType="separate"/>'),
       run("<w:t>1</w:t>"),
       run('<w:fldChar w:fldCharType="end"/>')))
parts["word/footer1.xml"] = footer.encode("utf-8")
order.append("word/footer1.xml")

ct = parts["[Content_Types].xml"].decode("utf-8")
ct = ct.replace("</Types>",
    '<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-'
    'officedocument.wordprocessingml.footer+xml"/></Types>')
parts["[Content_Types].xml"] = ct.encode("utf-8")

rels = parts["word/_rels/document.xml.rels"].decode("utf-8")
used = {int(x) for x in re.findall(r'Id="rId(\d+)"', rels)}
rid = "rId%d" % (max(used) + 1 if used else 1)
rels = rels.replace("</Relationships>",
    '<Relationship Id="%s" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
    'relationships/footer" Target="footer1.xml"/></Relationships>' % rid)
parts["word/_rels/document.xml.rels"] = rels.encode("utf-8")

doc = parts["word/document.xml"].decode("utf-8")
assert "footerReference" not in doc
doc = doc.replace("<w:sectPr>", '<w:sectPr><w:footerReference w:type="default" r:id="%s"/>' % rid, 1)
parts["word/document.xml"] = doc.encode("utf-8")

zout = zipfile.ZipFile("ref_submit.docx", "w", zipfile.ZIP_DEFLATED)
for n in order:
    zout.writestr(n, parts[n])
zout.close()

# ---- verify -----------------------------------------------------------------
from xml.etree import ElementTree as ET
z = zipfile.ZipFile("ref_submit.docx")
assert z.testzip() is None
for n in z.namelist():
    if n.endswith(".xml") or n.endswith(".rels"):
        ET.fromstring(z.read(n))
sx = z.read("word/styles.xml").decode("utf-8")
print("all", len(z.namelist()), "parts parse as XML")
print("Times in docDefaults :", "Times New Roman" in sx.split("</w:rPrDefault>")[0])
print("default size         :", re.search(r'<w:sz w:val="(\d+)"', sx).group(1), "half-points")
print("double spacing       :", 'w:line="480"' in sx.split("</w:pPrDefault>")[0])
print("footer wired         :", rid, "|", 'footerReference' in z.read("word/document.xml").decode("utf-8"))
