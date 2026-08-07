# -*- coding: utf-8 -*-
import zipfile, re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
zin = zipfile.ZipFile("ref_base.docx")
s = zin.read("word/styles.xml").decode("utf-8")

def edit(sid, fn):
    global s
    m = re.search(r'(<w:style [^>]*w:styleId="%s"[^>]*>)(.*?)(</w:style>)' % re.escape(sid), s, re.S)
    if not m:
        print("   ! missing:", sid); return False
    s = s[:m.start(2)] + fn(m.group(2)) + s[m.end(2):]
    return True

def set_rpr(body, frag, strip=()):
    for pat in strip:
        body = re.sub(pat, "", body)
    if "<w:rPr>" in body:
        return body.replace("<w:rPr>", "<w:rPr>" + frag, 1)
    return body + "<w:rPr>" + frag + "</w:rPr>"

def add_ppr(body, frag):
    if "<w:pPr>" in body:
        return body.replace("<w:pPr>", "<w:pPr>" + frag, 1)
    return re.sub(r"(</w:name>)", r"\1<w:pPr>" + frag + "</w:pPr>", body, count=1)

STRIP_COLOR = (r'<w:color[^/>]*/>', r'<w:color[^>]*>.*?</w:color>')
BLACK = '<w:color w:val="000000"/>'

# 1. justified body text
for sid in ["Normal", "BodyText", "Compact", "BlockText", "Abstract"]:
    edit(sid, lambda b: add_ppr(b, '<w:jc w:val="both"/>'))

# 2. headings black -- BOTH the paragraph style AND its linked Char style
for sid, sz in [("Heading1", 32), ("Heading2", 28), ("Heading3", 24),
                ("Heading4", 22), ("Heading5", 22), ("Heading6", 22)]:
    frag = BLACK + '<w:sz w:val="%d"/><w:szCs w:val="%d"/>' % (sz, sz)
    edit(sid, lambda b, f=frag: set_rpr(b, f, STRIP_COLOR))
    edit(sid + "Char", lambda b: set_rpr(b, BLACK, STRIP_COLOR))
for sid in ["Title", "TitleChar", "Subtitle", "SubtitleChar", "Author", "Date"]:
    edit(sid, lambda b: set_rpr(b, BLACK, STRIP_COLOR))

# 3. cross-reference links: black, no underline
edit("Hyperlink", lambda b: set_rpr(b, BLACK + '<w:u w:val="none"/>', STRIP_COLOR))

# 4. captions: centred, 10 pt
edit("Caption", lambda b: set_rpr(add_ppr(b, '<w:jc w:val="center"/>'),
                                  '<w:sz w:val="20"/><w:szCs w:val="20"/>'))

zout = zipfile.ZipFile("ref_final.docx", "w", zipfile.ZIP_DEFLATED)
for it in zin.infolist():
    d = zin.read(it.filename)
    if it.filename == "word/styles.xml": d = s.encode("utf-8")
    zout.writestr(it, d)
zout.close(); zin.close()

chk = zipfile.ZipFile("ref_final.docx").read("word/styles.xml").decode("utf-8")
print("\nVERIFY -- any non-black colour left in headings/hyperlink?")
bad = 0
for sid in ["Heading1","Heading1Char","Heading2","Heading2Char","Heading3","Heading3Char",
            "Heading4","Heading4Char","Title","TitleChar","Hyperlink","Caption"]:
    m = re.search(r'<w:style [^>]*w:styleId="%s"[^>]*>(.*?)</w:style>' % sid, chk, re.S)
    cols = re.findall(r'w:color w:val="([0-9A-Fa-f]{6})"', m.group(1)) if m else []
    theme = "themeColor" in (m.group(1) if m else "")
    flag = "OK " if all(c == "000000" for c in cols) and not theme else "BLUE"
    if flag == "BLUE": bad += 1
    print(f"   [{flag}] {sid:<16} colours={cols or ['inherit']}  themeColor={theme}")
print("\nremaining blue styles:", bad)
