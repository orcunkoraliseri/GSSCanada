# -*- coding: utf-8 -*-
"""Pre-upload gate. Runs on the files that will actually be uploaded."""
import zipfile, re, io, sys, collections
from xml.etree import ElementTree as ET
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
q = lambda t: "{%s}%s" % (W, t)

for label, f in [("MASTER", sys.argv[1]), ("BLINDED", sys.argv[2])]:
    z = zipfile.ZipFile(f)
    doc = z.read("word/document.xml").decode("utf-8")
    sty = z.read("word/styles.xml").decode("utf-8")
    r = ET.fromstring(doc)
    paras = [(p, "".join(t.text or "" for t in p.iter(q("t")))) for p in r.iter(q("p"))]
    txt = "\n".join(t for _, t in paras)
    intbl = {id(x) for tbl in r.iter(q("tbl")) for x in tbl.iter(q("p"))}
    caps = [t for p, t in paras
            if any(ps.get(q("val")) == "Caption" for ps in p.iter(q("pStyle")))]

    print("\n===== %s  (%s)" % (label, f.split("/")[-1]))
    print("  paras %d | imgs %d | tables %d | links %d | captions %d | pagebreaks %d"
          % (len(paras), len([n for n in z.namelist() if n.startswith("word/media/")]),
             len(list(r.iter(q("tbl")))), doc.count("<w:hyperlink"), len(caps),
             doc.count('w:type="page"')))
    # journal form
    print("  'Figure N' left in text :", len(re.findall(r"\bFigures?\s+S?\d", txt)) or "0  OK")
    print("  'Fig. N' references     :", len(re.findall(r"\bFigs?\.\s*S?\d", txt)))
    print("  caption forms           :",
          collections.Counter(re.match(r"(Fig\.|Table)\s*S?\d+", c).group(1)
                              for c in caps if re.match(r"(Fig\.|Table)\s*S?\d+", c)),
          "| non-conforming:", [c[:40] for c in caps if not re.match(r"(Fig\.|Table)\s*S?\d+", c)] or "none")
    print("  '(Author, year)' commas :", len(re.findall(r"[A-Za-z]\.?,\s(?:19|20)\d\d[a-z]?\)", txt)) or "0  OK")
    print("  duplicate alt captions  :", sum(1 for c in caps if re.fullmatch(r"Fig\. S?\d+", c.strip())) or "0  OK")
    # export format
    print("  default font / size     :",
          re.search(r'w:ascii="([^"]+)"', sty.split("</w:rPrDefault>")[0]).group(1),
          re.search(r'<w:sz w:val="(\d+)"', sty).group(1) + " half-pt")
    print("  double spacing default  :", 'w:line="480"' in sty.split("</w:pPrDefault>")[0])
    print("  page-number footer      :", "footerReference" in doc and "word/footer1.xml" in z.namelist())
    print("  line numbers            :", "PRESENT (bad)" if "<w:lnNumType" in doc else "none  OK")
    szs = {s.get(q("val")) for p in r.iter(q("p")) if id(p) in intbl for s in p.iter(q("sz"))}
    print("  table text sizes        :", szs, "(20 = 10 pt)")
    print("  inline colours          :", set(re.findall(r'w:color w:val="([0-9A-Fa-f]{6})"', doc)) or "none  OK")
    # residue
    for probe in ["Note.", "Reading of the matrix", "Originality with respect",
                  "[confirm]", "earlier version of this table", "corrected Step-8"]:
        if txt.count(probe):
            print("  !! residue %-28s %d" % (probe, txt.count(probe)))
    if label == "BLINDED":
        for probe in ["Orcun", "Caroline", "ORCID", "NSERC", "Voltage-Age", "CRediT",
                      "Acknowledgement", "Concordia", "orcunkoral"]:
            if txt.count(probe): print("  !! BLINDING LEAK %-20s %d" % (probe, txt.count(probe)))
        else: print("  blinding residue        : 0 for all 9 probes")
