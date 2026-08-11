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
  1. ONE SOURCE PASS. The document is assembled once, into a single in-memory string.
     `3J_full_manuscript.md` is that string verbatim. `readySubmission.md` is that same
     string put through ONE deterministic transform, `strip_for_submission()`. The two
     files differ only by a transform that is code, re-runnable and printed as a manifest
     on every build -- never by a hand edit.
  2. A CAMPAIGN STAMP is prepended to the working draft, naming the arm, the frozen source
     directory and its scorecard. Even if a future edit breaks mechanism 1, the stamp makes
     a divergence visible instead of silent.

USER DECISION 2026-08-06: the submission copy must be a plain paper -- no notes added
during the build process. The working draft keeps every one of them. Nothing is deleted
from any source file in `chapters/` or `tables/`; the strip happens here, at assembly.

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
    "Chapter_08_Conclusion.md",
    "Chapter_09_References.md",
    "Chapter_10_Supplementary.md",
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


# ---------------------------------------------------------------------------
# The submission transform. Everything it removes is build apparatus: a note we
# wrote to ourselves during the build, or an internal file path. Nothing it removes
# is a result, a caveat about the science, or a literature reference.
#
# Named explicitly rather than pattern-guessed, so a reviewer can audit the list.
# A heading NOT on this list is kept. Adding to it is a deliberate act.
# ---------------------------------------------------------------------------
DROP_HEADINGS = [
    re.compile(r"^##\s+Sources\b", re.I),                    # internal file paths, not literature
    re.compile(r"^##\s+Manager notes\b", re.I),              # written to ourselves at review
    re.compile(r"^##\s+Discrepancy flagged to the manager\b", re.I),
    re.compile(r"^#\s+Appendix: (tables|figures) not inlined", re.I),
]

# Headings that stay, but whose wording is an instruction to us rather than to a reader.
RENAME_HEADINGS = [
    (re.compile(r"^##\s+Provenance key \(do not cite a project-chosen threshold to the literature\)\s*$"),
     "## Threshold provenance"),
    (re.compile(r"^##\s+What was confirmed against the source files, and what was not\s*$"),
     "## Scope of verification"),
]

# `check source` is our own to-do marker. A submission needs a reader-facing
# convention instead -- and it must still be VISIBLE, because an unfilled cell that
# looks filled is the one outcome worse than an ugly one.
#
# The marker wraps across line breaks in the source files, so a literal-string replace
# silently misses those. It missed 2 of 25 on the first run and still printed a count,
# which read as complete. Match on whitespace, and assert afterwards.
MARK = u"⚠ check source"
MARK_RE = re.compile(u"⚠\\s+check\\s+source", re.UNICODE)
GLYPH_RE = re.compile(u"⚠\\s*")
# USER DECISION 2026-08-09: the substitution is now self-explanatory prose, and the
# legend that used to be inserted after the abstract is gone. `n/r` needed a legend --
# a blockquote at the top of the paper explaining a symbol -- and a legend reads as an
# internal report, not as a paper. "not reported" needs nothing. The marker is still
# VISIBLE, which is the whole point of the convention; only the apparatus around it went.
MARK_SUB = "not reported"


# An inline source pointer, as opposed to a `## Sources` heading. These sit in the SI
# under each correction and each improvement round. They point at paths inside this
# repository, which no reader of the paper can resolve, so they are apparatus. The
# CLAIM they support is never touched -- only the pointer line.
# Guarded: a block is dropped only if it actually contains a repository path, so a
# pointer to a real published source survives.
#
# 🔴 The first version of this pattern allowed a leading `**`, and on its first run it
# deleted a paragraph headed `**Source of truth, and what is explicitly not the source of
# truth.**` -- a CAVEAT, naming the stale docx that must not be cited. It was caught only
# because every removal was diffed by hand before being accepted. A bolded lead-in phrase
# is prose; a pointer starts plain and reaches a colon almost immediately. Require both.
SRC_BLOCK = re.compile(r"^Source(?:s)?\b[^:\n*]{0,32}:\s")
REPO_PATH = re.compile(r"(Leg2_2-split|Leg3_4-split|improvements/v[0-9]|deepResearch/|"
                       r"Step[0-9]_docs|eSim_bem_utils|\.py\b|\.md\b)")


# BUILD NOTES. A note addressed to us, sitting inside a line that IS paper content.
#
# The case that forced this: two entries in the Chapter 1 reference list carried a
# "DOI DISPUTED, DO NOT SUBMIT UNTIL RESOLVED" banner. The reference line itself is
# literature and must ship; the banner is a note to ourselves and must not. Neither
# DROP_HEADINGS (which works on whole sections) nor the `check source` marker (which
# is a cell value) could separate them, so the banner rode into readySubmission.md.
#
# An HTML comment is the right carrier: it is invisible in any rendered view of the
# working draft, it survives verbatim in the draft's source for us to read, and it is
# removed here by one named rule. It is NOT a way to hide an unresolved problem -- see
# the unresolved-notes report printed at the end of main(), which is loud on purpose.
BUILD_NOTE_RE = re.compile(r"[ \t]*<!--\s*BUILD NOTE\b.*?-->", re.S)

# Any other HTML comment. Runs AFTER BUILD_NOTE_RE so the BUILD NOTE count stays its own
# number in the manifest and in the unresolved-notes report.
HTML_COMMENT_RE = re.compile(r"[ \t]*<!--.*?-->", re.S)


# A line that means the source list is over and the paper has resumed.
#
# 🔴 THIS PATTERN WAS TOO WIDE AND IT LEAKED A WHOLE SECTION, 2026-08-08.
# It used to also accept a bare markdown table row (`|`) and an image (`![`). But an
# apparatus section is perfectly entitled to contain a table: the `## Manager notes`
# block under Table 6 opens with a three-row verdict tally. The drop therefore ENDED at
# that tally, and everything after it -- "Manager decision", "Recorded reason", a
# "Written reopen trigger", and five references to an internal decision ID -- was
# written straight into readySubmission.md. The residue check did not catch it, because
# the check looked for the surviving *heading*, and the heading is exactly the one line
# that had been removed correctly.
#
# A CAPTION is a strong signal that the paper has resumed, and a caption is what the
# original bug (a deleted `**Table 4.**` line) was actually about. A table row is a weak
# one. Only the strong signal is honoured now. Anything inside a dropped section stays
# dropped until a heading, a rule, a caption, or an image.
#
# 🔴 AN IMAGE IS A STRONG SIGNAL TOO, AND NARROWING THIS PATTERN DELETED ONE, 2026-08-11.
# `![` was removed from this pattern together with the bare table row, because the two were
# taken out in one edit. They are not the same strength of signal. An apparatus block is
# prose and repository paths; it never contains a figure. When Figure S3 came to sit
# directly after a table whose file ends in a `## Sources` block, the section drop ran past
# the image and stopped only at the caption below it, so the submission copy carried
# "Figure S3." with no figure above it -- 14 images against 15 captions. NOTHING FAILED:
# the loss check counts CAPTIONS, and the caption is exactly the line that survived. The
# image is re-admitted here as a resume signal, and counted below.
CONTENT_RESUMES = re.compile(r"^(\*\*(Table|Figure|Graphical)\b|!\[)")

# Content markers that must survive the strip intact. Counted before and after.
CAPTION = re.compile(r"^\*\*(?:Table|Figure) [A-Z]?\d+\.\*\*", re.M)
# An image is content too, and counting captions does not count images: the one defect
# this file has now produced twice was a caption surviving while its figure did not.
IMAGE = re.compile(r"^!\[[^\]]*\]\(([^)]+)\)", re.M)


def _drop_inline_source_blocks(lines):
    """Remove `Source: <repo path>` blocks, blank-line delimited. Returns (kept, n_dropped)."""
    kept, i, dropped = [], 0, 0
    while i < len(lines):
        if SRC_BLOCK.match(lines[i]):
            j = i
            while j < len(lines) and lines[j].strip():
                j += 1
            block = "\n".join(lines[i:j])
            if REPO_PATH.search(block):
                dropped += j - i
                while j < len(lines) and not lines[j].strip():
                    j += 1                      # swallow the blank line after it too
                i = j
                continue
        kept.append(lines[i])
        i += 1
    return kept, dropped


def strip_for_submission(doc):
    """Return (clean_doc, manifest). Removes build apparatus only; reports every removal."""
    lines = doc.splitlines()
    out, manifest = [], []
    dropping = None          # heading text of the section currently being dropped
    dropped_lines = 0

    for line in lines:
        if dropping is not None:
            # A dropped section ends at the next h1/h2, at a horizontal rule, OR at the
            # first line that is plainly content again.
            # 🔴 Without that last clause this deleted the `**Table 4.**` caption, which
            # sat between a `## Sources` heading and the next `##`. A section drop that
            # runs to the next heading assumes everything in between belongs to the
            # section. It does not.
            if (re.match(r"^#{1,2}\s", line) or line.strip() == "---"
                    or CONTENT_RESUMES.match(line)):
                manifest.append((dropping, dropped_lines))
                dropping, dropped_lines = None, 0
                # fall through: this line is evaluated normally below
            else:
                dropped_lines += 1
                continue

        if any(p.match(line) for p in DROP_HEADINGS):
            dropping, dropped_lines = line.strip(), 1
            continue

        for pat, repl in RENAME_HEADINGS:
            if pat.match(line):
                manifest.append(("RENAMED: %s -> %s" % (line.strip(), repl), 0))
                line = repl
                break

        out.append(line)

    if dropping is not None:
        manifest.append((dropping, dropped_lines))

    out, n_src = _drop_inline_source_blocks(out)
    if n_src:
        manifest.append(("inline `Source:` pointers into this repository", n_src))

    clean = "\n".join(out)

    # Drop the campaign stamp: it is build provenance, not paper content.
    if clean.startswith("<!-- CAMPAIGN IDENTIFIER"):
        end = clean.find("\n\n#")
        if end > 0:
            manifest.append(("CAMPAIGN IDENTIFIER block", clean[:end].count("\n") + 1))
            clean = clean[end + 1:].lstrip("\n")

    n_notes = len(BUILD_NOTE_RE.findall(clean))
    if n_notes:
        clean = BUILD_NOTE_RE.sub("", clean)
        manifest.append(("BUILD NOTE comments (notes to ourselves inside paper content)", n_notes))

    # Every OTHER html comment. Same carrier, same reason, different name: an
    # `<!-- APPARATUS NOTE ... -->` records why a line is the way it is, survives in the
    # working draft's source for us to read, and has no business in a submitted paper.
    # This rule exists because the alternative was to DELETE those notes from the source
    # files, and deleting the note deletes the reason.
    n_html = len(HTML_COMMENT_RE.findall(clean))
    if n_html:
        clean = HTML_COMMENT_RE.sub("", clean)
        manifest.append(("other HTML comments (apparatus notes in the source files)", n_html))

    n_marks = len(MARK_RE.findall(clean))
    clean = MARK_RE.sub(MARK_SUB, clean)
    if n_marks:
        manifest.append(("'check source' marker rewritten as '%s'" % MARK_SUB, n_marks))

    # The bare warning glyph is used elsewhere to open a disclosure note. Keep the note,
    # drop the glyph: a submitted paper does not carry our console symbols.
    n_glyph = len(GLYPH_RE.findall(clean))
    if n_glyph:
        clean = GLYPH_RE.sub("Note. ", clean)
        manifest.append(("bare warning glyph rewritten as 'Note.'", n_glyph))

    # Tidy: never more than one blank line, never two rules in a row.
    # Line-based, not regex: three sections dropped in sequence leave three rules, and a
    # single non-overlapping re.sub collapses the first pair and silently leaves the third.
    clean = re.sub(r"\n{3,}", "\n\n", clean)
    tidy, last_rule = [], False
    for line in clean.split("\n"):
        if line.strip() == "---":
            if last_rule:
                continue                       # a rule already stands here
            last_rule = True
        elif line.strip():
            last_rule = False
        tidy.append(line)
    clean = "\n".join(tidy)
    clean = re.sub(r"\n{3,}", "\n\n", clean)
    clean = re.sub(r"(?:\n|\s|-)*$", "", clean) + "\n"      # no trailing rule

    # POST-CONDITION. A transform that reports "23 rewritten" is reporting its own
    # numerator; it says nothing about what it failed to see. Check the residue instead.
    residue = []
    if u"⚠" in clean:
        residue.append("warning glyph still present")
    # Dropping a section's HEADING is not dropping the section. These phrases live in the
    # BODY of the apparatus blocks, so they catch a truncated drop that the heading-level
    # residue checks below are structurally unable to see.
    for pat, label in ((re.compile(r"Manager decision|Manager notes|Recorded reason|"
                                   r"Written reopen trigger|flagged to the manager"),
                        "the body of a manager-notes block"),
                       (re.compile(r"BUILD NOTE"), "a BUILD NOTE"),
                       (re.compile(r"DO NOT SUBMIT"), "a DO NOT SUBMIT banner"),
                       (re.compile(r"^##\s+Sources\b", re.I | re.M), "a Sources heading"),
                       (re.compile(r"^##\s+Manager notes\b", re.I | re.M), "a Manager notes heading"),
                       (re.compile(r"CAMPAIGN IDENTIFIER"), "the campaign stamp"),
                       (re.compile(r"^---\s*\n---\s*$", re.M), "two horizontal rules in a row")):
        if pat.search(clean):
            residue.append(label + " survived the strip")
    if residue:
        raise AssertionError("submission strip incomplete: " + "; ".join(residue))

    # 🔴 THE LOSS CHECK, and it is a different check from the one above.
    # The residue check asks "did any apparatus survive?". It is completely blind to
    # "did any content disappear?". The strip deleted the `**Table 4.**` caption and
    # every arm above still passed; a human reader found it. Count the captions on both
    # sides and name the difference.
    before = set(CAPTION.findall(doc))
    after = set(CAPTION.findall(clean))
    lost = sorted(before - after)
    if lost:
        raise AssertionError("submission strip DELETED content: %s" % ", ".join(lost))

    # The same check, on images. A caption with no figure above it is not a caption.
    lost_img = sorted(set(IMAGE.findall(doc)) - set(IMAGE.findall(clean)))
    if lost_img:
        raise AssertionError("submission strip DELETED %d image(s): %s"
                             % (len(lost_img), ", ".join(lost_img)))
    n_cap, n_img = len(CAPTION.findall(clean)), len(IMAGE.findall(clean))
    manifest.append(("captions %d, images %d, both counted after the strip" % (n_cap, n_img), 0))

    # USER DECISION 2026-08-09: no thematic breaks in the submission copy.
    # pandoc renders a markdown `---` as a VML rectangle, and Word names that shape
    # "Horizontal Line" -- 60 of them in the built .docx, one per section separator. They
    # are a drafting device for reading the working draft, not typography a journal wants.
    #
    # This runs LAST, after the residue and loss checks, on purpose. The strip's
    # section-drop loop uses `---` as a terminator and the residue check tests for two
    # rules in a row; removing the rules earlier would quietly disarm both.
    #
    # One rule in this document sits directly under a paragraph with no blank line above
    # it. That is the shape that makes a SETEXT heading, and it was written up as a second
    # bug found here -- wrongly. Pandoc's markdown only reads setext from a SINGLE-line
    # header, and this is a six-line paragraph, so pandoc renders it as a `<p>` and a rule.
    # Checked by running that fragment through pandoc rather than by reading the spec.
    # Recorded because the claim was in this comment for an hour before it was tested.
    n_rules = sum(1 for l in clean.split("\n") if l.strip() == "---")
    if n_rules:
        clean = "\n".join(l for l in clean.split("\n") if l.strip() != "---")
        clean = re.sub(r"\n{3,}", "\n\n", clean)
        manifest.append(("horizontal rules (Word renders each as a 'Horizontal Line' shape)",
                         n_rules))
    if "\n---\n" in clean:
        raise AssertionError("a horizontal rule survived the thematic-break strip")

    return clean, manifest


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
    wrapped_captions = []

    for chapter in ORDER:
        lines = read(os.path.join(CH, chapter)).splitlines()
        i = 0
        while i < len(lines):
            line = lines[i]
            m = TBL_PAT.match(line) or FIG_PAT.match(line)
            if not m:
                parts.append(line)
                i += 1
                continue

            # 🔴 A CAPTION IS ONE BLOCK, AND IT USED TO BE CUT IN HALF.
            # The chapter sources are hard-wrapped, so a caption longer than one line
            # continued on the lines after the placeholder. The old loop matched only the
            # placeholder line and appended the continuation as ordinary chapter text --
            # which landed it AFTER the inserted image, i.e. the figure was inserted into
            # the middle of its own caption. Nothing failed: the caption count was right,
            # the residue check was clean, and the built .docx read "Figure 7. four-channel
            # EUI trajectory across the 2005, 2010, 2015", then the image, then "and 2022
            # GSS Time-Use cycles ...". Read the whole block here instead.
            j = i + 1
            cont = []
            while j < len(lines) and lines[j].strip():
                cont.append(lines[j])
                j += 1
            caption = ("**%s.**%s" % (m.group("lbl"), m.group("rest"))).rstrip()
            if cont:
                wrapped_captions.append("%s (%s, %d line(s) of continuation)"
                                        % (m.group("lbl"), chapter, len(cont)))
                caption = caption + "\n" + "\n".join(cont)
            i = j

            fname = m.group("f")
            if fname.endswith(".md"):
                # USER DECISION 2026-08-11: a TABLE caption sits ABOVE its table.
                p, body = inline_table(fname)
                if p:
                    inlined_tables.append(fname)
                parts.append("%s\n\n%s\n" % (caption, body))
            else:
                # USER DECISION 2026-08-11: a FIGURE caption sits BELOW its figure.
                p = find(fname, [FIG, FIG_SI])
                if p:
                    inlined_figs.append(fname)
                    rel = os.path.relpath(p, BASE).replace("\\", "/")
                    parts.append("![%s](%s)\n\n%s\n" % (m.group("lbl"), rel, caption))
                else:
                    parts.append("*(figure file %s NOT FOUND)*\n\n%s\n" % (fname, caption))
        parts.append("\n\n---\n")

    # Anything not inlined goes into an explicit appendix. Nothing is dropped silently.
    all_tables = sorted(
        [f for f in os.listdir(TBL) if f.endswith(".md")]
        + [f for f in os.listdir(TBL_SI) if f.endswith(".md")]
    )
    # Files that live in tables/ but are deliberately NOT part of the manuscript.
    #
    # 🔴 Removing a placeholder is not enough to cut a table. The leftovers appendix is
    # built by DIFFING the directory against what was inlined, so a table whose
    # placeholder is deleted does not disappear -- it reappears in the appendix, in full.
    # That is the correct default (nothing is lost silently) and exactly wrong here.
    #
    # These two files stay on disk on purpose. Appendix_C_corrections.md is a live source
    # for f5_figure_check.py's C4 and C6 arms, which cross-foot Figure S1's occupiable
    # shares against it; deleting it would break a check that has already caught two real
    # defects. Cutting a table from the SUBMISSION is not the same as deleting a project
    # artefact, and this distinction is the whole reason the exclusion is by name here
    # rather than by moving files around.
    EXCLUDED_TABLES = {
        # Authors' decision, 2026-08-08: the v0-v5 improvement-round ledger and the
        # corrections appendix are this project's internal sprint board, not supplementary
        # material for a journal. Columns like "Gates moved / Bands moved" and round labels
        # are development apparatus.
        "Table_B1_improvement_rounds.md",
        "Appendix_C_corrections.md",
    }
    excluded_present = sorted(t for t in all_tables if t in EXCLUDED_TABLES)
    all_tables = [t for t in all_tables if t not in EXCLUDED_TABLES]
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
    clean, manifest = strip_for_submission(doc)

    # ONE string, TWO files, ONE transform between them. This is mechanism 1.
    #
    # User decision, 2026-08-08: fullSet/ shows ONE document and it is the final one.
    # The working draft is not final, so it is written to fullSet/previous/ instead of
    # beside the submission copy. This is a PATH change only -- both files are still
    # written from the same in-memory string on every build, so the loss check, the
    # residue check and the manifest all still compare the same two things.
    prev = os.path.join(BASE, "previous")
    if not os.path.isdir(prev):
        os.makedirs(prev)
    draft = os.path.join(prev, "3J_full_manuscript.md")     # working copy, apparatus intact
    subm = os.path.join(BASE, "readySubmission.md")         # submission copy, apparatus stripped
    for path, text in ((draft, doc), (subm, clean)):
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)

    print("assembled %d chapters" % len(ORDER))
    print("  tables inlined at a placeholder : %d  %s" % (len(inlined_tables), inlined_tables))
    print("  tables appended to the appendix : %d  %s" % (len(left_tables), left_tables))
    # Printed, not silent: a cut the build does not announce is a cut nobody can audit.
    print("  tables EXCLUDED from the paper   : %d  %s" % (len(excluded_present), excluded_present))
    # Vacuity guard. If a name in EXCLUDED_TABLES matches nothing on disk it is excluding
    # nothing, and the set reads as effective when it is not -- the same failure class as a
    # check that passes because it looked at zero items.
    missing_excl = sorted(EXCLUDED_TABLES - set(excluded_present))
    if missing_excl:
        print("  !! EXCLUDED_TABLES names %d file(s) that do not exist: %s"
              % (len(missing_excl), missing_excl))
    print("  figures inlined at a placeholder: %d  %s" % (len(inlined_figs), inlined_figs))
    print("  figures appended to the appendix: %d  %s" % (len(left_figs), left_figs))
    # Printed because a wrapped caption is the shape that used to be split by its own
    # figure. It is handled correctly now, but a caption that needs a second line is also
    # a caption that is drifting past the house limit, so it is reported rather than absorbed.
    print("  captions that wrapped onto a second line: %d  %s"
          % (len(wrapped_captions), wrapped_captions))

    print("\nSUBMISSION STRIP -- every removal named, nothing dropped silently:")
    total = 0
    for what, n in manifest:
        total += n
        print("  %5s  %s" % (("-%d" % n) if n else "  ~", what))
    print("  %d apparatus lines removed; %d -> %d lines."
          % (total, doc.count("\n") + 1, clean.count("\n") + 1))
    print("  Source files in chapters/ and tables/ were NOT modified; they keep everything.")

    for path, text in ((draft, doc), (subm, clean)):
        with io.open(path, encoding="utf-8") as fh:
            got = hashlib.md5(fh.read().encode("utf-8")).hexdigest()
        exp = hashlib.md5(text.encode("utf-8")).hexdigest()
        print("  %-24s %s  %s" % (os.path.basename(path), got, "OK" if got == exp else "MISMATCH"))

    # A note removed from the paper is not a problem solved. The strip makes the
    # submission copy clean; this report makes sure that cleanliness is never mistaken
    # for readiness. Every BUILD NOTE is an open item blocking submission, listed here.
    # A note that has been ANSWERED is rewritten in place as `BUILD NOTE RESOLVED <date> by <what>`
    # and keeps the words "BUILD NOTE", deliberately: the strip regex and the residue check both key
    # on that phrase, so a resolved note is still removed from the submission copy and still refused
    # if it survives. What changes is only whether it is counted as blocking. Deleting the note
    # instead would delete the reason, which is the part worth keeping.
    all_notes = BUILD_NOTE_RE.findall(doc)
    notes = [n for n in all_notes if not re.match(r"[ \t]*<!--\s*BUILD NOTE RESOLVED\b", n)]
    n_resolved = len(all_notes) - len(notes)
    if n_resolved:
        print("\n  %d BUILD NOTE(s) marked RESOLVED, not counted as blocking:" % n_resolved)
        for note in all_notes:
            if re.match(r"[ \t]*<!--\s*BUILD NOTE RESOLVED\b", note):
                one = " ".join(note.split()).replace("<!--", "").replace("-->", "").strip()
                print("     + %s" % (one[:120] + (" ..." if len(one) > 120 else "")))
    print("\nUNRESOLVED BUILD NOTES -- each one blocks submission:")
    if not notes:
        print("  none. Nothing in the manuscript is waiting on an external answer.")
    else:
        print("  !! %d open. readySubmission.md is CLEAN but NOT READY." % len(notes))
        for note in notes:
            one = " ".join(note.split())
            one = one.replace("<!-- BUILD NOTE:", "").replace("-->", "").strip()
            print("     - %s" % (one[:150] + (" ..." if len(one) > 150 else "")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
