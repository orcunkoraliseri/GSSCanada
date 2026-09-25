#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
assemble_3J_v2.py - build the 3J submission files from the revised chapters (chapters_v2/).

RUN (from anywhere):
    py -3 writing/fullSet/assemble_3J_v2.py              build, install, test the installed files
    py -3 writing/fullSet/assemble_3J_v2.py --selftest   feed deliberately broken copies of the
                                                         INSTALLED outputs to every check and confirm
                                                         each check fires (writes nothing)

READS (never writes): chapters_v2/00..11 + SI_additions.md, tables/Table_04_validation_gates.md,
tables/Table_07_limitations.md, tables/SI/Table_A1_A2.md, submission/figures/ (then figures/),
submission/extra/build_scripts/{ref_submit.docx, post.py}.

WRITES (the only four files it writes):
    submission/3J_manuscript_submission.md      submission/3J_manuscript_submission.docx
    submission/3J_supplementary_material.md     submission/Supplementary material.docx

FIRST RUN ONLY: the four pre-existing files are moved into
submission/archive/pre_v2_build_2026-09-25/ (copy, verify non-empty and same md5, then remove).
Later runs see a complete, non-empty archive and never archive their own output again.

DETERMINISTIC: same inputs give byte-identical .md and .docx (pandoc runs with a fixed
SOURCE_DATE_EPOCH; post.py copies zip entries with their original timestamps).

LAYOUT follows the 2J Applied Energy revision (2J_manuscript_AE_revised.md): YAML title; Abstract,
Highlights, Keywords as level-1 headings; sections 1 to 6; Nomenclature; Appendix A; Appendix B;
declarations; References. Figures are `![](path){width=16cm}` with the bold caption BELOW; table
captions sit ABOVE the table. Both .docx use ref_submit.docx (double spacing, as the 2J AE files),
then post.py (table text 10 pt, single spaced).

EXIT CODES
    0  every check PASS
    1  at least one of checks 1, 2, 3 FAIL (a build or content-integrity defect)
    3  checks 1 to 3 PASS but check 4 FAIL (citation/reference mismatch in the author's text;
       reported, not fixed by this script)
    2  build aborted before installing (missing input or figure, archive guard, pandoc error,
       SI plan changed shape). Nothing was overwritten in that case.
Checks 5 and 6 are REPORT lines (counts), never FAIL.
"""

import hashlib
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from xml.etree import ElementTree as ET

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))           # writing/fullSet
WRITING = os.path.dirname(HERE)                             # writing
CH = os.path.join(WRITING, "chapters_v2")
TBL = os.path.join(WRITING, "tables")
FIG = os.path.join(WRITING, "figures")
SUB = os.path.join(WRITING, "submission")
SUBFIG = os.path.join(SUB, "figures")
BS = os.path.join(SUB, "extra", "build_scripts")
ARCH = os.path.join(SUB, "archive", "pre_v2_build_2026-09-25")

CHAPTERS = [
    "00_FrontMatter.md", "01_Introduction.md", "02_Framework.md", "03_Results.md",
    "04_Discussion.md", "05_Limitations.md", "06_Conclusion.md", "07_Nomenclature.md",
    "08_AppendixA_Table1.md", "09_AppendixB_Equations.md", "10_Declarations.md",
    "11_References.md",
]
SI_PLAN = os.path.join(CH, "SI_additions.md")

MAIN_MD = os.path.join(SUB, "3J_manuscript_submission.md")
MAIN_DOCX = os.path.join(SUB, "3J_manuscript_submission.docx")
SI_MD = os.path.join(SUB, "3J_supplementary_material.md")
SI_DOCX = os.path.join(SUB, "Supplementary material.docx")
OUTPUTS = [MAIN_MD, MAIN_DOCX, SI_MD, SI_DOCX]

REF_DOC = os.path.join(BS, "ref_submit.docx")
POST = os.path.join(BS, "post.py")
SOURCE_DATE_EPOCH = "1790294400"                            # 2026-09-25 00:00 UTC, fixed

FIG_WIDTH = "{width=16cm}"

# ---------------------------------------------------------------------------------------------
# SI plan. The "Numbering of supplementary items" table in SI_additions.md supplies the captions
# (its Content column). The source of each item is fixed here and CROSS-CHECKED against the plan's
# Source column, so a change of plan stops the build instead of being followed silently.
# ---------------------------------------------------------------------------------------------
SI_ITEMS = [
    # (label, source file, text that must appear in the plan's Source cell)
    ("Table S1", os.path.join(TBL, "Table_04_validation_gates.md"), "Table_04_validation_gates.md"),
    ("Table S2", os.path.join(TBL, "Table_07_limitations.md"), "Table_07_limitations.md"),
    ("Table S3", os.path.join(TBL, "SI", "Table_A1_A2.md"), "Tables A1 and A2"),
    ("Table S4", SI_PLAN, "rewritten below"),
    ("Figure S1", "Figure_S01_occupiable_shares.png", "old Figure S1"),
    ("Figure S2", "Figure_S02_scenario_levers.png", "old Figure S2"),
    ("Figure S3", "Figure_S03_leg2_pipeline.png", "old Figure S3"),
    ("Figure S4", "Figure_02_three_leg_roadmap.png", "Figure_02_three_leg_roadmap.png"),
    ("Figure S5", "Figure_04_exclusivity_projection.png", "Figure_04_exclusivity_projection.png"),
    ("Figure S6", "Figure_09_diurnal_4ch.png", "Figure_09_diurnal_4ch.png"),
    ("Figure S7", "Figure_10_peakhour_4ch.png", "Figure_10_peakhour_4ch.png"),
]

# Journal-voice edits applied to the SI table sources at build time. Each must match EXACTLY
# ONCE (whitespace-insensitive); if a source file changes so that an edit no longer matches,
# the build stops and names the edit. Source files are never modified.
SI_EDITS = {
    "Table S1": [
        ("intro: process wording (pipeline steps, 'honesty') replaced",
         "Gates applied across Steps 4-9 of the four-channel pipeline reported here. The Provenance "
         "column classifies every threshold as exactly one of three kinds. This distinction is "
         "load-bearing for the paper's honesty: a project-chosen threshold is not literature, and "
         "must never be cited as if it were.",
         "The Provenance column classifies every threshold as exactly one of three kinds: a "
         "literature value, a heuristic, or a project-chosen value."),
        ("stale section pointer", "caught only on the output side (§3.5).",
         "caught only on the output side (Section S.2)."),
        ("heading written as an instruction to ourselves",
         "### Provenance key (do not cite a project-chosen threshold to the literature)",
         "### Threshold provenance"),
    ],
    "Table S2": [
        ("intro: process wording ('the source's own numbers') replaced",
         "The Discussion carries the deciding statements in full; the wording here is condensed to "
         "fit a cell. No verdict is paraphrased. Rows L5 and L7 carry the numbers of the reported "
         "runs; the other rows carry the source's own numbers.",
         "Section 5 of the main text states the limitations in full; the wording here is condensed "
         "to fit a cell. Rows L5 and L7 give values from the simulations reported in the main text; "
         "the other rows give design values or measurements made during model development."),
        ("merge note (rewrite_log Stage 2c item 12): L4 control value 85.45 -> 85.36",
         "The uninjected control scores 85.45 against a floor of 100.",
         "The uninjected control scores 85.36 against a floor of 100."),
        ("merge note (rewrite_log Stage 2c item 12): L6 measured claim removed",
         "Wrong in sign and order in 56 of 56 cells. Exposure takes 2 values across the campaign, "
         "not 56.",
         "Not evaluated in the reported runs."),
    ],
    "Table S3": [
        ("stale section pointer", "as disclosed in §3.2", "as described in Section S.1"),
        ("second table of the file becomes part (e) of Table S3",
         "**Table A2.** - AT_RETAIL codebook per GSS cycle.",
         "### (e) Per-cycle retail code mapping"),
    ],
    "Table S4": [
        ("cross-reference made explicit (main-text Table 4)", "ranges (Table 4)",
         "ranges (Table 4 of the main text)"),
    ],
}

HTML_COMMENT = re.compile(r"[ \t]*<!--.*?-->[ \t]*\n?", re.S)
FIG_PH = re.compile(r"^\*\*(?P<lbl>Figure S?\d+)\.\*\*\s*\*\(insert `(?P<f>[^`]+)` here\)\*\s*(?P<rest>.*)$")
DASHES = re.compile(u"[\u2012\u2013\u2014\u2015]")
RESIDUE = [
    (re.compile(r"manager", re.I), "'manager'"),
    (re.compile(r"\bold (Table|Figure)", re.I), "'old Table/Figure'"),
    (re.compile(r"MERGE NOTE|BUILD NOTE|APPARATUS NOTE"), "build note"),
    (re.compile(r"<!--"), "HTML comment"),
    (re.compile(r"\w\.(md|py|csv|json|docx)\b"), "file name"),
    (re.compile(r"Leg3_4-split|outputs_step|rewrite_log|chapters_v2|writing/"), "repository path"),
    (re.compile(r"\bSteps? \d"), "pipeline step number"),
    (re.compile(u"§"), "section sign (stale pointer)"),
    (re.compile(r"P10R|V2-[A-Z]\d|V3c"), "internal run ID"),
    (re.compile(r"^#+\s+(Sources|Manager notes|Discrepancy)", re.M), "apparatus heading"),
    (re.compile(r"reopen trigger", re.I), "reopen trigger"),
]


class BuildError(Exception):
    pass


def read(p):
    with io.open(p, encoding="utf-8") as fh:
        return fh.read().replace("\r\n", "\n")


def write(p, text):
    with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def md5_bytes(b):
    return hashlib.md5(b).hexdigest()


def md5_file(p):
    with open(p, "rb") as fh:
        return md5_bytes(fh.read())


def tidy(text):
    """Strip trailing spaces, collapse runs of blank lines, end with one newline."""
    text = "\n".join(l.rstrip() for l in text.split("\n"))
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip("\n") + "\n"


def ws_pattern(s):
    return re.compile(r"\s+".join(re.escape(w) for w in s.split()))


def apply_edits(label, text, log):
    for what, old, new in SI_EDITS.get(label, []):
        pat = ws_pattern(old)
        n = len(pat.findall(text))
        if n != 1:
            raise BuildError("%s edit '%s' matched %d times (expected exactly 1); the source changed, "
                             "update SI_EDITS" % (label, what, n))
        text = pat.sub(lambda m: new, text)
        log.append("%s: %s" % (label, what))
    return text


# ---------------------------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------------------------
def locate_png(name):
    """submission/figures first, then figures/; last resort a search of figures/ (archives skipped)."""
    for d in (SUBFIG, os.path.join(SUBFIG, "SI"), FIG, os.path.join(FIG, "SI")):
        p = os.path.join(d, name)
        if os.path.isfile(p):
            return p
    hits = []
    for root, dirs, files in os.walk(FIG):
        dirs[:] = sorted(d for d in dirs if not d.lower().lstrip("_").startswith("archive"))
        if name in files:
            hits.append(os.path.join(root, name))
    if len(hits) == 1:
        return hits[0]
    raise BuildError("figure file %s: %s" % (name, "NOT FOUND in submission/figures or figures"
                                             if not hits else "found %d copies: %s" % (len(hits), hits)))


def fig_block(label, png, caption):
    if not png.lower().endswith(".png"):
        raise BuildError("%s: %s is not a PNG" % (label, png))
    rel = os.path.relpath(png, SUB).replace("\\", "/")
    return "![](%s)%s\n\n**%s.** %s" % (rel, FIG_WIDTH, label, caption.strip())


def embed_figures(text, used):
    lines, out, i = text.split("\n"), [], 0
    while i < len(lines):
        m = FIG_PH.match(lines[i])
        if not m:
            out.append(lines[i])
            i += 1
            continue
        j, cont = i + 1, []
        while j < len(lines) and lines[j].strip():          # a caption wrapped onto more lines
            cont.append(lines[j])
            j += 1
        png = locate_png(m.group("f"))
        cap = " ".join([m.group("rest").strip()] + [c.strip() for c in cont])
        out.append(fig_block(m.group("lbl"), png, cap))
        used.append((m.group("lbl"), png))
        i = j
    return "\n".join(out)


# ---------------------------------------------------------------------------------------------
# Main manuscript
# ---------------------------------------------------------------------------------------------
def build_front(text, log):
    lines = text.split("\n")
    if not lines[0].startswith("# "):
        raise BuildError("00_FrontMatter.md must start with '# <title>'")
    title = lines[0][2:].strip()
    pre, sections, cur = [], {}, None
    order_seen = []
    for l in lines[1:]:
        m = re.match(r"^##\s+(.+?)\s*$", l)
        if m:
            cur = m.group(1)
            sections[cur] = []
            order_seen.append(cur)
            continue
        (pre if cur is None else sections[cur]).append(l)
    want = ["Abstract", "Highlights", "Keywords"]           # 2J AE order
    missing = [w for w in want if w not in sections]
    if missing:
        raise BuildError("front matter lacks section(s): %s" % missing)
    extra = [s for s in order_seen if s not in want]
    if order_seen[:3] != want:
        log.append("front matter: sections reordered %s -> %s (2J AE order)" % (order_seen, want + extra))
    pre = [l for l in pre if l.strip() != "---"]
    pre_txt = "\n".join(pre)
    pre_txt, n = re.subn(r"\\textsuperscript\{([^}]*)\}",
                         lambda m: "^" + m.group(1).replace(" ", "\\ ") + "^", pre_txt)
    if n:
        log.append("front matter: %d \\textsuperscript -> pandoc superscript (raw TeX is dropped in .docx)" % n)
    yaml = "---\ntitle: '%s'\n---\n" % title.replace("'", "''")
    body = [yaml, pre_txt]
    for s in want + extra:
        body.append("# %s\n\n%s" % (s, "\n".join(sections[s]).strip("\n")))
    return title, "\n\n".join(body)


def format_references(text, log):
    out, n_year, n_end = [], 0, 0
    for l in text.split("\n"):
        if l.strip() and not l.startswith("#"):
            l2, k = re.subn(r"^(.+?\(\d{4}[a-z]?\))\s(?!\.)", r"\1. ", l, count=1)
            n_year += k
            l = l2.rstrip()
            if not l.endswith((".", "]")):
                l += "."
                n_end += 1
        out.append(l)
    log.append("references: period after the year in %d entries, closing period added to %d (2J AE form)"
               % (n_year, n_end))
    return "\n".join(out)


def build_main(log, used):
    missing = [c for c in CHAPTERS if not os.path.isfile(os.path.join(CH, c))]
    if missing:
        raise BuildError("missing chapters: %s" % missing)
    parts, title = [], None
    for c in CHAPTERS:
        t = read(os.path.join(CH, c))
        t, n = HTML_COMMENT.subn("\n", t)
        if n:
            log.append("%s: %d HTML comment(s) removed" % (c, n))
        if c.startswith("00_"):
            title, t = build_front(t, log)
        else:
            nr = len([l for l in t.split("\n") if l.strip() == "---"])
            if nr:
                t = "\n".join(l for l in t.split("\n") if l.strip() != "---")
                log.append("%s: %d horizontal rule(s) removed" % (c, nr))
        if c.startswith("11_"):
            t = format_references(t, log)
        t = embed_figures(t, used)
        parts.append(t.strip("\n"))
    return title, tidy("\n\n".join(parts))


# ---------------------------------------------------------------------------------------------
# Supplementary material
# ---------------------------------------------------------------------------------------------
def parse_plan(plan_text):
    m = re.search(r"^## Numbering of supplementary items\s*\n(.*?)(?=^## |\Z)", plan_text, re.S | re.M)
    if not m:
        raise BuildError("SI_additions.md: 'Numbering of supplementary items' table not found")
    rows = []
    for l in m.group(1).split("\n"):
        if l.startswith("|") and not re.match(r"^\|[-\s|:]+\|$", l):
            cells = [c.strip() for c in l.strip().strip("|").split("|")]
            if cells[0] != "New SI item":
                rows.append(cells)
    labels = [r[0] for r in rows]
    want = [x[0] for x in SI_ITEMS]
    if labels != want:
        raise BuildError("SI plan items %s differ from the items this script knows %s; update SI_ITEMS"
                         % (labels, want))
    plan = {}
    for (label, src, token), row in zip(SI_ITEMS, rows):
        if token not in row[2]:
            raise BuildError("SI plan: %s source cell '%s' no longer names '%s'" % (label, row[2], token))
        plan[label] = row[1].rstrip(".")
    return plan


def plan_sections(plan_text):
    """Split SI_additions.md into its '## ' sections; return (S.n sections in order, Table S4 body)."""
    secs, cur = [], None
    for l in plan_text.split("\n"):
        m = re.match(r"^##\s+(.+?)\s*$", l)
        if m:
            cur = [m.group(1), []]
            secs.append(cur)
        elif cur is not None:
            cur[1].append(l)
    s_secs, s4 = [], None
    for head, body in secs:
        if head.startswith("Numbering of supplementary items"):
            continue
        if re.match(r"^S\.\d+\s", head):
            s_secs.append((head, "\n".join(body).strip("\n")))
        elif re.match(r"^Table S4\.", head):
            s4 = "\n".join(body).strip("\n")
        else:
            raise BuildError("SI_additions.md has a section this script does not place: '## %s'" % head)
    if s4 is None:
        raise BuildError("SI_additions.md: '## Table S4.' section not found")
    return s_secs, s4


def table_body(path, log):
    t = read(path)
    t = HTML_COMMENT.sub("\n", t)
    lines = t.split("\n")
    cut = next((i for i, l in enumerate(lines) if re.match(r"^##\s+Sources\b", l)), len(lines))
    log.append("%s: %d line(s) from '## Sources' to end of file not carried (file paths, review notes)"
               % (os.path.basename(path), len(lines) - cut))
    lines = [l for l in lines[:cut] if not re.match(r"^#\s", l) and l.strip() != "---"]
    lines = [("#" + l) if l.startswith("## ") else l for l in lines]     # one level under the caption
    return tidy("\n".join(lines)).strip("\n")


def build_si(title, log, used):
    plan_text = read(SI_PLAN)
    plan = parse_plan(plan_text)
    s_secs, s4 = plan_sections(plan_text)
    out = ["# Supplementary material", "*%s*" % title]
    for head, body in s_secs:
        out.append("## %s\n\n%s" % (head, body))
    out.append("## Supplementary tables")
    for label, src, _ in SI_ITEMS:
        if not label.startswith("Table"):
            continue
        if label == "Table S4":
            body = s4
        else:
            if not os.path.isfile(src):
                raise BuildError("%s source missing: %s" % (label, src))
            body = table_body(src, log)
        if label == "Table S3":
            n = [0]

            def sub_head(m):
                n[0] += 1
                return "### (%s) " % "abcd"[int(m.group(1)) - 1]
            body = re.sub(r"^### A1\.([1-4]) ", sub_head, body, flags=re.M)
            if n[0] != 4:
                raise BuildError("Table S3: expected 4 'A1.n' sub-headings, found %d" % n[0])
            log.append("Table S3: sub-headings A1.1 to A1.4 renamed (a) to (d)")
        body = apply_edits(label, body, log)
        out.append("**%s.** %s.\n\n%s" % (label, plan[label], body))
    out.append("## Supplementary figures")
    for label, name, _ in SI_ITEMS:
        if not label.startswith("Figure"):
            continue
        png = locate_png(name)
        out.append(fig_block(label, png, plan[label] + "."))
        used.append((label, png))
    return tidy("\n\n".join(out))


# ---------------------------------------------------------------------------------------------
# Archive guard, pandoc
# ---------------------------------------------------------------------------------------------
ARCH_MANIFEST = "ARCHIVE_COMPLETE.txt"


def is_v2_output(p):
    """True if p was written by this script (so it must never be archived as 'pre-v2')."""
    try:
        if p.endswith(".docx"):
            core = zipfile.ZipFile(p).read("docProps/core.xml").decode("utf-8", "replace")
            return "2026-09-25T00:00:00Z" in core           # the fixed SOURCE_DATE_EPOCH stamp
        t = read(p)
        return t.startswith("---\ntitle: '") or "\n## Supplementary tables\n" in t
    except Exception:
        return False


def archive_first_run():
    """Move the pre-v2 outputs into ARCH once, then write a manifest. Returns status lines.
    Refuses (BuildError) on: an empty archive copy, an empty current file, a manifest whose files are
    missing/empty/changed, or an attempt to archive a file this script itself wrote."""
    os.makedirs(ARCH, exist_ok=True)
    man = os.path.join(ARCH, ARCH_MANIFEST)
    msgs = []
    if os.path.isfile(man):
        for line in read(man).strip().split("\n"):
            h, name = line.split("  ", 1)
            dst = os.path.join(ARCH, name)
            if not (os.path.isfile(dst) and os.path.getsize(dst) > 0 and md5_file(dst) == h):
                raise BuildError("archive guard: %s is missing, empty or changed since it was archived" % dst)
        msgs.append("archive: complete (%s verified: %d file(s) non-empty, md5 unchanged); nothing re-archived"
                    % (ARCH_MANIFEST, len(read(man).strip().split("\n"))))
    else:
        for p in OUTPUTS:
            name = os.path.basename(p)
            dst = os.path.join(ARCH, name)
            if os.path.isfile(dst):
                if os.path.getsize(dst) == 0:
                    raise BuildError("archive guard: archive copy %s is EMPTY; refusing to continue" % dst)
                msgs.append("archive: %s already archived (%d bytes)" % (name, os.path.getsize(dst)))
                continue
            if not os.path.isfile(p):
                msgs.append("archive: %s absent and not archived (nothing to keep)" % name)
                continue
            if os.path.getsize(p) == 0:
                raise BuildError("archive: current %s is EMPTY; refusing to archive an empty file" % name)
            if is_v2_output(p):
                raise BuildError("archive: %s was written by this script, so the pre-v2 copy is already "
                                 "gone; refusing to archive this script's own output" % name)
            shutil.copy2(p, dst)
            if not (os.path.isfile(dst) and os.path.getsize(dst) > 0 and md5_file(dst) == md5_file(p)):
                raise BuildError("archive: copy of %s is missing, empty or differs; original left in place" % name)
            os.remove(p)
            msgs.append("archive: %s moved to %s (%d bytes, md5 verified)"
                        % (name, os.path.relpath(dst, WRITING), os.path.getsize(dst)))
        done = [os.path.basename(p) for p in OUTPUTS if os.path.isfile(os.path.join(ARCH, os.path.basename(p)))]
        with io.open(man, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join("%s  %s" % (md5_file(os.path.join(ARCH, n)), n) for n in done) + "\n")
        msgs.append("archive: %s written (%d file(s))" % (ARCH_MANIFEST, len(done)))
    # Guard: nothing is overwritten unless its pre-v2 copy sits non-empty in the archive, or it is
    # this script's own earlier output.
    for p in OUTPUTS:
        dst = os.path.join(ARCH, os.path.basename(p))
        if os.path.isfile(p) and not (os.path.isfile(dst) and os.path.getsize(dst) > 0) and not is_v2_output(p):
            raise BuildError("archive guard: %s exists, is not a v2 build, and has no non-empty archive copy" % p)
    return msgs


def pandoc_docx(md_path, docx_path, tmpdir):
    env = dict(os.environ, SOURCE_DATE_EPOCH=SOURCE_DATE_EPOCH)
    raw = os.path.join(tmpdir, "raw_" + os.path.basename(docx_path).replace(" ", "_"))
    r = subprocess.run(["pandoc", md_path, "-f", "markdown", "-t", "docx", "--reference-doc", REF_DOC,
                        "--resource-path", SUB, "-o", raw], cwd=SUB, env=env,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise BuildError("pandoc failed on %s: %s" % (md_path, r.stderr.strip()))
    warnings = [w for w in r.stderr.strip().split("\n") if w.strip()]
    if any("Could not fetch resource" in w for w in warnings):
        raise BuildError("pandoc could not find an image: %s" % warnings)
    post = os.path.join(tmpdir, "post_" + os.path.basename(raw))
    r2 = subprocess.run([sys.executable, POST, raw, post], capture_output=True, text=True,
                        encoding="utf-8", errors="replace")
    if r2.returncode != 0:
        raise BuildError("post.py failed: %s" % r2.stderr.strip())
    shutil.copyfile(post, docx_path)
    return warnings, r2.stdout.strip()


# ---------------------------------------------------------------------------------------------
# Checks. Each returns (status, details) with status in PASS / FAIL / REPORT.
# ---------------------------------------------------------------------------------------------
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def docx_paragraphs(docx):
    root = ET.fromstring(zipfile.ZipFile(docx).read("word/document.xml"))
    return ["".join(t.text or "" for t in p.iter(W + "t")) for p in root.iter(W + "p")]


def check1_media(docx, expected):
    """expected: list of (label, png path). Installed media md5 == source md5, count == placeholders."""
    z = zipfile.ZipFile(docx)
    media = sorted(n for n in z.namelist() if n.startswith("word/media/"))
    got = {}
    for n in media:
        got.setdefault(md5_bytes(z.read(n)), []).append(n)
    exp = {}
    for lbl, p in expected:
        exp.setdefault(md5_file(p), []).append(lbl)
    det = ["%d image(s) in word/media, %d figure placeholder(s)" % (len(media), len(expected))]
    ok = len(media) == len(expected)
    for h, lbls in sorted(exp.items()):
        if len(got.get(h, [])) != len(lbls):
            ok = False
            det.append("no byte-identical copy of %s (md5 %s) in the .docx" % ("/".join(lbls), h[:8]))
    for h, names in sorted(got.items()):
        if h not in exp:
            ok = False
            det.append("%s (md5 %s) matches no source PNG" % (", ".join(names), h[:8]))
    return ("PASS" if ok else "FAIL"), det


def check1_captions(docx, expected):
    paras = docx_paragraphs(docx)
    miss = [lbl for lbl, _ in expected if not any(p.startswith(lbl + ".") for p in paras)]
    return ("FAIL" if miss else "PASS"), (["caption paragraph missing: %s" % m for m in miss]
                                         or ["%d caption paragraph(s) found" % len(expected)])


def check2_markers(text):
    det = []
    for i, l in enumerate(text.split("\n"), 1):
        for pat, what in ((re.compile(r"\(insert"), "'(insert' placeholder"),
                          (re.compile(u"[\u27e6\u27e7]"), "marker bracket"),
                          (DASHES, "en/em dash")):
            for m in pat.finditer(l):
                det.append("line %d: %s: ...%s..." % (i, what, l[max(0, m.start() - 30):m.end() + 30]))
    return ("FAIL" if det else "PASS"), det or ["0 placeholders, 0 marker brackets, 0 en/em dashes"]


def check2_residue(text):
    det = []
    for i, l in enumerate(text.split("\n"), 1):
        for pat, what in RESIDUE:
            m = pat.search(l)
            if m:
                det.append("line %d: %s: ...%s..." % (i, what, l[max(0, m.start() - 30):m.end() + 30]))
    return ("FAIL" if det else "PASS"), det or ["no process notes, file names, paths or internal IDs"]


def check2_docx_text(docx):
    txt = "\n".join(docx_paragraphs(docx))
    st, det = check2_markers(txt)
    return st, det


REF_ITEM = r"(?:S?\d+|[A-Z]\.\d+)"
REF_RE = re.compile(r"\b(Figure|Table)s?\s+(%s(?:(?:\s*,\s*|\s+and\s+|\s+to\s+)%s)*)" % (REF_ITEM, REF_ITEM))


def cited_labels(text):
    cites = []
    for l in text.split("\n"):
        l = re.sub(r"^\*\*(Figure|Table) [^*]+\.\*\*", "", l)           # a caption's own label
        for m in REF_RE.finditer(l):
            kind, items = m.group(1), m.group(2)
            toks = re.split(r"\s*,\s*|\s+and\s+", items)
            for t in toks:
                r = re.match(r"^(S?)(\d+)\s+to\s+(S?)(\d+)$", t)
                if r:
                    for k in range(int(r.group(2)), int(r.group(4)) + 1):
                        cites.append("%s %s%d" % (kind, r.group(1), k))
                else:
                    cites.append("%s %s" % (kind, t.strip()))
    return cites


def caption_labels(text):
    return re.findall(r"^\*\*((?:Figure|Table) [A-Z]?\.?\d+)\.\*\*", text, re.M)


def consecutive(labels, prefix):
    nums = [int(l[len(prefix):]) for l in labels if re.fullmatch(re.escape(prefix) + r"\d+", l)]
    return nums, nums == list(range(1, len(nums) + 1))


def check3_numbering(main, si):
    det, ok = [], True
    mc, sc = caption_labels(main), caption_labels(si)
    for doc, caps, series in (("main", mc, ["Figure ", "Table ", "Table A."]),
                              ("SI", sc, ["Figure S", "Table S"])):
        for pre in series:
            nums, good = consecutive(caps, pre)
            det.append("%s %s: %s %s" % (doc, pre.strip(), nums, "consecutive" if good else "NOT CONSECUTIVE"))
            ok &= good
        dup = sorted(set(c for c in caps if caps.count(c) > 1))
        if dup:
            ok = False
            det.append("%s: duplicate caption(s) %s" % (doc, dup))
    stray = [c for c in mc if re.match(r"(Figure|Table) S\d", c)] + \
            [c for c in sc if not re.match(r"(Figure|Table) S\d", c)]
    if stray:
        ok = False
        det.append("caption in the wrong document: %s" % stray)
    have = set(mc) | set(sc)
    for doc, text in (("main", main), ("SI", si)):
        cites = cited_labels(text)
        bad = sorted(set(c for c in cites if c not in have))
        if bad:
            ok = False
            det.append("%s cites item(s) that do not exist: %s" % (doc, bad))
        else:
            det.append("%s: %d citation(s) of %d distinct item(s), all exist" % (doc, len(cites), len(set(cites))))
    uncited = [c for c in mc if c not in set(cited_labels(main))]
    if uncited:
        det.append("(info) main-text item(s) never cited in the main text: %s" % uncited)
    return ("PASS" if ok else "FAIL"), det


INITIALS = re.compile(r"^(?:[^\W\d_]\.-?)+$", re.U)


def ref_label(author):
    """'Barrero, J.M., Bloom, N. and Davis, S.J.' -> 'Barrero et al.'; organisations kept whole."""
    toks = author.replace(" and ", ", ").split(", ")
    if len(toks) >= 2 and len(toks) % 2 == 0 and all(INITIALS.match(t) for t in toks[1::2]):
        s = toks[0::2]
        return s[0] if len(s) == 1 else ("%s and %s" % (s[0], s[1]) if len(s) == 2 else s[0] + " et al.")
    return author.strip()


def parse_references(main):
    m = re.search(r"^# References\s*\n(.*)\Z", main, re.S | re.M)
    if not m:
        return [], main
    refs = []
    for l in m.group(1).split("\n"):
        if not l.strip():
            continue
        d = re.match(r"^(.+?) \((\d{4}[a-z]?)\)", l)
        if d:
            refs.append((ref_label(d.group(1)), d.group(2), l))
        else:
            refs.append((ref_label(l.split(", ")[0]), None, l))
    return refs, main[:m.start()]


def text_citations(body, labels=()):
    """Parenthetical '(Name, YYYY; ...)' and narrative 'Name (YYYY)'. For a narrative citation the
    longest known reference label that ends right before ' (YYYY)' wins (organisation names have
    spaces), else the one- or two-surname / 'et al.' form in front of the year."""
    found = []
    for m in re.finditer(r"\(([^()]*)\)", body):
        for piece in m.group(1).split(";"):
            piece = piece.strip()
            y = re.match(r"^(?P<a>[^,()]+?),\s+(?P<y>\d{4}[a-z]?)$", piece)
            if y:
                found.append((y.group("a").strip(), y.group("y")))
            elif piece:
                found.append((piece, None))           # candidate undated citation, filtered later
    for m in re.finditer(r" \((\d{4}[a-z]?)\)", body):
        before = body[max(0, m.start() - 150):m.start()]
        hit = sorted((l for l in labels if before.endswith(l)), key=len, reverse=True)
        if hit:
            found.append((hit[0], m.group(1)))
            continue
        n = re.search(r"\b([A-Z\u00C0-\u00DE][^\s(),;]*(?: et al\.| and [A-Z\u00C0-\u00DE][^\s(),;]*)?)$", before)
        if n:
            found.append((n.group(1), m.group(1)))
    return found


def check4_citations(main):
    refs, body = parse_references(main)
    if not refs:
        return "FAIL", ["no '# References' section found"]
    dated = {(a, y) for a, y, _ in refs if y}
    undated = {a for a, y, _ in refs if not y}
    cites = text_citations(body, {a for a, _, _ in refs})
    used, unmatched = set(), []
    for a, y in cites:
        if y:
            if (a, y) in dated:
                used.add((a, y))
            else:
                unmatched.append("%s, %s" % (a, y))
        elif a in undated:
            used.add((a, None))
    uncited = [l[:90] for a, y, l in refs if (a, y) not in used]
    det = ["%d reference entries; %d dated in-text citation(s) found" % (len(refs), len([c for c in cites if c[1]]))]
    det += ["cited in text, no reference entry: %s" % u for u in sorted(set(unmatched))]
    for a, y, l in refs:
        if (a, y) not in used:
            named = len(re.findall(re.escape(a), body))
            det.append("reference never cited: %s%s" % (l[:90], "  [its name appears %d time(s) in prose]" % named
                                                        if not y and named else ""))
    return ("FAIL" if unmatched or uncited else "PASS"), det


def check5_refneeded(main, si):
    det = []
    for doc, text in (("main", main), ("SI", si)):
        for i, l in enumerate(text.split("\n"), 1):
            for m in re.finditer(r"\[REF NEEDED[^\]]*\]", l):
                det.append("%s line %d: %s" % (doc, i, m.group(0)))
    return "REPORT", ["%d [REF NEEDED placeholder(s)" % len(det)] + det


def words(s):
    return len([w for w in re.split(r"\s+", s) if re.search(r"\w", w)])


def section(main, start_re, end_re):
    m = re.search(start_re + r".*?(?=" + end_re + r")", main, re.S | re.M)
    return m.group(0) if m else ""


def prose_only(s):
    out, in_math = [], False
    for l in s.split("\n"):
        if l.strip().startswith("$$"):
            in_math = not (l.strip().endswith("$$") and len(l.strip()) > 2) and not in_math
            continue
        if in_math or l.startswith("|") or l.startswith("![") or l.startswith("#"):
            continue
        out.append(re.sub(r"[*^]", "", l))
    return "\n".join(out)


def check6_words(main):
    body = section(main, r"^# 1\. Introduction", r"^# Nomenclature")
    abstract = section(main, r"^# Abstract\s*$", r"^# Highlights")
    abstract = "\n".join(abstract.split("\n")[1:])
    total = "\n".join(l for l in body.split("\n") if not l.startswith("#") and not l.startswith("!["))
    return "REPORT", [
        "main body, Introduction to Conclusion: %d words (prose and captions; headings, tables, "
        "display equations and image lines excluded)" % words(prose_only(body)),
        "main body including table cells: %d words" % words(re.sub(r"[|*^]", " ", total)),
        "abstract: %d words" % words(abstract),
    ]


def run_checks(main, si, main_used, si_used, pandoc_warn):
    res = []
    res.append(("1a", "main .docx images: md5 = source PNG, count = placeholders", check1_media(MAIN_DOCX, main_used)))
    res.append(("1b", "SI .docx images: md5 = source PNG, count = placeholders", check1_media(SI_DOCX, si_used)))
    res.append(("1c", "main .docx: every figure caption present", check1_captions(MAIN_DOCX, main_used)))
    res.append(("1d", "SI .docx: every figure caption present", check1_captions(SI_DOCX, si_used)))
    res.append(("1e", "pandoc warnings (math, images)",
                (("FAIL" if pandoc_warn else "PASS"), pandoc_warn or ["none"])))
    res.append(("2a", "main .md: placeholders / marker brackets / en-em dashes", check2_markers(main)))
    res.append(("2b", "SI .md: placeholders / marker brackets / en-em dashes", check2_markers(si)))
    res.append(("2c", "installed .docx text: same three probes, both files",
                _merge(check2_docx_text(MAIN_DOCX), check2_docx_text(SI_DOCX))))
    res.append(("2d", "main .md: no process notes, file names, internal IDs", check2_residue(main)))
    res.append(("2e", "SI .md: no process notes, file names, internal IDs", check2_residue(si)))
    res.append(("3", "Figure/Table numbering consecutive; every cited item exists", check3_numbering(main, si)))
    res.append(("4", "author-year citations <-> reference list (report; not fixed here)", check4_citations(main)))
    res.append(("5", "[REF NEEDED placeholders (report)", check5_refneeded(main, si)))
    res.append(("6", "word counts (report)", check6_words(main)))
    return res


def _merge(a, b):
    return ("FAIL" if "FAIL" in (a[0], b[0]) else "PASS"), ["main: " + x for x in a[1]] + ["SI: " + x for x in b[1]]


def print_results(res):
    for cid, what, (st, det) in res:
        print("CHECK %-3s %-70s %s" % (cid, what, st))
        for d in det:
            print("          - %s" % d)
    fails = [cid for cid, _, (st, _) in res if st == "FAIL"]
    if any(not f.startswith("4") for f in fails):
        return 1
    return 3 if fails else 0


# ---------------------------------------------------------------------------------------------
def build():
    log, main_used, si_used = [], [], []
    title, main = build_main(log, main_used)
    si = build_si(title, log, si_used)
    for m in archive_first_run():
        print(m)
    write(MAIN_MD, main)
    write(SI_MD, si)
    tmp = tempfile.mkdtemp(prefix="assemble_3J_v2_")
    try:
        w1, p1 = pandoc_docx(MAIN_MD, MAIN_DOCX, tmp)
        w2, p2 = pandoc_docx(SI_MD, SI_DOCX, tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("\nBUILD LOG (every transform applied at build time; sources untouched):")
    for l in log:
        print("  - " + l)
    print("  - post.py: %s" % p1.split("|", 1)[-1].strip())
    print("  - post.py: %s" % p2.split("|", 1)[-1].strip())
    print("\nINSTALLED:")
    for p in OUTPUTS:
        print("  %s  %8d bytes  md5 %s" % (os.path.relpath(p, WRITING), os.path.getsize(p), md5_file(p)))
    print("  figures: main %d, SI %d" % (len(main_used), len(si_used)))
    for lbl, p in main_used + si_used:
        print("    %-10s <- %s" % (lbl, os.path.relpath(p, WRITING)))
    # Every check reads the INSTALLED files back from disk, not the in-memory strings.
    main_i, si_i = read(MAIN_MD), read(SI_MD)
    print("\nCHECKS (on the installed files):")
    warn = ["main: " + w for w in w1] + ["SI: " + w for w in w2]
    return print_results(run_checks(main_i, si_i, main_used, si_used, warn))


# ---------------------------------------------------------------------------------------------
# Self-test: every check must FIRE on a deliberately broken copy of the installed outputs.
# ---------------------------------------------------------------------------------------------
def selftest():
    for p in OUTPUTS:
        if not os.path.isfile(p):
            raise BuildError("selftest needs the installed outputs; missing %s" % p)
    main, si = read(MAIN_MD), read(SI_MD)
    used_main, used_si = [], []
    for text, used in ((main, used_main), (si, used_si)):
        for m in re.finditer(r"^!\[\]\(([^)]+)\)\{[^}]*\}\n\n\*\*(Figure S?\d+)\.\*\*", text, re.M):
            used.append((m.group(2), os.path.normpath(os.path.join(SUB, m.group(1)))))
    results = []

    def expect(name, status_det, needle):
        st, det = status_det
        hit = st == "FAIL" and (needle is None or any(needle in d for d in det))
        results.append(hit)
        print("SELFTEST %-68s %s" % (name, "FIRED (FAIL as expected)" if hit else "NOT DETECTED  <-- check is blind"))
        if not hit:
            for d in det[:5]:
                print("          - %s" % d)

    tmp = tempfile.mkdtemp(prefix="assemble_3J_v2_selftest_")
    try:
        # 1: one image re-encoded (one byte appended) inside a copy of the installed .docx
        bad = os.path.join(tmp, "bad_bytes.docx")
        _rewrite_zip(MAIN_DOCX, bad, alter="first")
        expect("1a  one image's bytes changed inside the installed main .docx",
               check1_media(bad, used_main), "matches no source PNG")
        bad2 = os.path.join(tmp, "bad_count.docx")
        _rewrite_zip(SI_DOCX, bad2, alter="drop")
        expect("1b  one image removed from the installed SI .docx", check1_media(bad2, used_si), "no byte-identical copy")
        expect("1c  a figure the .docx does not contain is expected",
               check1_captions(MAIN_DOCX, used_main + [("Figure 99", used_main[0][1])]), "Figure 99")
        badmath = os.path.join(tmp, "badmath.md")
        write(badmath, "Text.\n\n$$\\begin{foo} x$$\n")
        warn, _ = pandoc_docx(badmath, os.path.join(tmp, "badmath.docx"), tmp)
        expect("1e  real pandoc run on unconvertible TeX math",
               (("FAIL" if warn else "PASS"), warn or ["no warning"]), "Could not convert TeX math")
        dashdocx = os.path.join(tmp, "dash.docx")
        write(os.path.join(tmp, "dash.md"), u"Years 2005\u20132022.\n")
        pandoc_docx(os.path.join(tmp, "dash.md"), dashdocx, tmp)
        expect("2c  en dash inside a real pandoc .docx", check2_docx_text(dashdocx), "en/em dash")
        # 2
        expect("2a  '(insert' placeholder left", check2_markers(main + "\n**Figure 9.** *(insert `x.png` here)*\n"), "(insert")
        expect("2a  marker bracket left", check2_markers(main + u"\nvalue \u27e6P10R:x\u27e7\n"), "marker bracket")
        expect("2b  en dash in SI", check2_markers(si + u"\n2005\u20132022\n"), "en/em dash")
        expect("2b  em dash in SI", check2_markers(si + u"\nword\u2014word\n"), "en/em dash")
        expect("2d  'manager' note in main", check2_residue(main + "\nThe manager decided this.\n"), "'manager'")
        expect("2e  'old Table' wording in SI", check2_residue(si + "\nSee old Table 7.\n"), "old Table")
        expect("2e  file path in SI", check2_residue(si + "\nFrom `Table_07_limitations.md`.\n"), "file name")
        # 3
        expect("3   figure number skipped (Figure 2 caption renamed Figure 3)",
               check3_numbering(main.replace("**Figure 2.**", "**Figure 3.**", 1), si), "NOT CONSECUTIVE")
        expect("3   cites a figure that does not exist (Figure 12)",
               check3_numbering(main + "\nAs Figure 12 shows.\n", si), "Figure 12")
        expect("3   cites an SI table that does not exist (Table S9)",
               check3_numbering(main + "\nSee Supplementary Table S9.\n", si), "Table S9")
        expect("3   SI table number skipped (Table S2 -> Table S5)",
               check3_numbering(main, si.replace("**Table S2.**", "**Table S5.**", 1)), "NOT CONSECUTIVE")
        # 4
        body_add = main.replace("# References", "Shown before (Nobody et al., 1999).\n\n# References", 1)
        expect("4   in-text citation with no reference entry", check4_citations(body_add), "Nobody et al., 1999")
        refs_add = main.rstrip("\n") + "\n\nZed, A. (2001). An uncited paper. *Journal*, 1, 1.\n"
        expect("4   reference entry cited nowhere", check4_citations(refs_add), "Zed, A. (2001)")
        drop = re.sub(r"^Wilke, U\..*\n", "", main, flags=re.M)
        expect("4   reference entry deleted (Wilke)", check4_citations(drop), "Wilke et al., 2013")
        # 5 and 6 are counts: show that they move with the input
        n0 = int(check5_refneeded(main, si)[1][0].split()[0])
        n1 = int(check5_refneeded(main + "\n[REF NEEDED: test]\n", si)[1][0].split()[0])
        ok5 = n1 == n0 + 1
        results.append(ok5)
        print("SELFTEST %-68s %s" % ("5   one [REF NEEDED added -> count %d -> %d" % (n0, n1), "MOVED" if ok5 else "DID NOT MOVE"))
        w0 = check6_words(main)[1][0]
        w1 = check6_words(main.replace("# 2. Proposed", "one two three four five six seven eight nine ten\n\n# 2. Proposed", 1))[1][0]
        g = lambda s: int(re.search(r": (\d+) words", s).group(1))
        ok6 = g(w1) == g(w0) + 10
        results.append(ok6)
        print("SELFTEST %-68s %s" % ("6   ten words added to Section 1 -> body count %d -> %d" % (g(w0), g(w1)),
                                     "MOVED" if ok6 else "DID NOT MOVE"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    blind = results.count(False)
    print("\nSELFTEST: %d of %d probes detected%s" % (results.count(True), len(results),
                                                    "" if not blind else "; %d BLIND" % blind))
    return 0 if not blind else 1


def _rewrite_zip(src, dst, alter):
    zin = zipfile.ZipFile(src)
    media = sorted(n for n in zin.namelist() if n.startswith("word/media/"))
    zout = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
    for it in zin.infolist():
        d = zin.read(it.filename)
        if media and it.filename == media[0]:
            if alter == "drop":
                continue
            d = d + b"\0"
        zout.writestr(it, d)
    zout.close()
    zin.close()


def main(argv):
    try:
        if "--selftest" in argv:
            return selftest()
        return build()
    except BuildError as e:
        print("BUILD ABORTED: %s" % e)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
