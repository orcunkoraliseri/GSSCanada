"""Build the manuscript .docx: scratch copy with Eq. 17/18 tags swapped (Word cannot convert that form),
pandoc with the submission reference doc, then post.py unchanged. The .md is never modified."""
import os
import subprocess
import sys

MAN = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\2J_docs_occ_nTemp\writing\submission\rejection revision\manuscript"
BS = os.path.normpath(os.path.join(MAN, "..", "..", "extra", "build_scripts"))
SCR = os.environ.get("TEMP", os.path.dirname(os.path.abspath(__file__)))
BS_ = chr(92)

import re
src = open(os.path.join(MAN, "2J_manuscript_AE_revised.md"), encoding="utf-8").read()
# Word cannot convert a \tag in an equation that also holds "\qquad \text{...}" (the two comparison-arm
# equations, main Eq. 6 and Appendix Eq. B.12 since the 2026-09-22 IMP renumbering). Swap only those.
n = 0
def _swap(m):
    global n
    blk = m.group(0)
    if (BS_ + "qquad " + BS_ + "text") in blk and (BS_ + "tag{") in blk:
        n += 1
        return re.sub(r"\\tag\{([^}]*)\}", lambda t: BS_ + "qquad (" + t.group(1) + ")", blk)
    return blk
src = re.sub(r"\$\$.*?\$\$", _swap, src, flags=re.S)
print("tags replaced:", n)
assert n == 2
tmp_md = os.path.join(SCR, "main_build.md")
open(tmp_md, "w", encoding="utf-8").write(src)
tmp_docx = os.path.join(SCR, "main_pandoc.docx")
r = subprocess.run(["pandoc", tmp_md, "-f", "markdown", "-t", "docx", "--reference-doc",
                    os.path.join(BS, "ref_submit.docx"), "--columns=10", "--resource-path=" + MAN,
                    "-o", tmp_docx], capture_output=True, text=True)
print("pandoc rc", r.returncode, "stderr:", r.stderr.strip() or "(none)")
r2 = subprocess.run([sys.executable, os.path.join(BS, "post.py"), tmp_docx,
                     os.path.join(MAN, "2J_manuscript_AE_revised.docx")], capture_output=True, text=True)
print(r2.stdout.strip(), r2.stderr.strip())
