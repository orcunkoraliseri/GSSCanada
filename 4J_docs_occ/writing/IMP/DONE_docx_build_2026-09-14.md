# Word-build recipe for 4J_manuscript_submission.docx — DONE 2026-09-14

Built and proved entirely on a scratchpad copy
(`...\a0d226f8-af02-41b1-942a-30fdfffd767e\scratchpad\docxbuild\`). The live markdown and
the live `.docx` were never written to — only read. Verified at the end of this task:
`grep -Fc` for the raw-LaTeX author-line marker against the live `.md` still returns `1`
(unchanged), and the live `.docx`'s mtime is untouched.

## 1. Pandoc

`pandoc --version` -> **pandoc 3.9.0.2** (features +server +lua, Lua 5.4). Installed and
on PATH; no install step was needed or attempted.

## 2. How the existing .docx was actually built

Unzipped a copy of `4J_manuscript_submission.docx` read-only and inspected
`docProps/app.xml`, `docProps/core.xml`, `word/media/`, `word/_rels/document.xml.rels`,
`[Content_Types].xml`, `word/styles.xml`, `word/document.xml`.

- **Images:** 8 PNGs in `word/media/` (`rId44,53,56,82,88,92,98,104.png`), one per
  `![...](figures/...)` reference in the markdown (graphical abstract + Figures 1-7).
  All 8 are embedded byte-for-byte unchanged — their md5s match the source PNGs in
  `writing/submission/figures/` exactly (checked with `md5sum`, both sides).
- **Pandoc version signature:** `docProps/app.xml` and `core.xml` carry no pandoc
  version string (pandoc docx output never writes one) — NOT FOUND by inspection of
  those two files, as expected; nothing in this task depended on it.
- **Reference/template docx: a reference docx WAS used**, and it was found — not assumed.
  `writing/submission/extra/build_scripts/ref_submit.docx` exists (alongside
  `ref_submit_single.docx` and `post.py`, a table-formatting post-processor unrelated to
  D1/D2). This directory was **not** inside `tools/`, which is why the original "no build
  script anywhere" search missed it — worth flagging since `post.py` is a leftover partial
  build step (10 pt/single-spaced tables) that this task's script does not need and does
  not call.
  Evidence that `ref_submit.docx` is the one actually used:
  - `word/styles.xml` of the live `.docx` uses `Times New Roman` for body/heading fonts,
    black-forced color, `w:jc val="both"` (justified), and default paragraph spacing
    `line="240"` (single). A plain `pandoc file.md -o out.docx` with **no** reference doc
    instead uses Word's theme fonts (`asciiTheme="minorHAnsi"`), `w:spacing after="200"`,
    no justification — clearly different.
  - Rebuilding with `--reference-doc=ref_submit.docx` reproduces `line="240"` exactly.
    `ref_submit_single.docx` instead carries `line="480"` (double-spaced) — ruled out.
  - The `<w:sectPr>` (footer/footnote section properties) of the live `.docx` is
    **character-for-character identical** to a build made with `--reference-doc=ref_submit.docx`.
  - Strongest evidence: rebuilding with this exact recipe reproduces the **same**
    `word/media/rIdNN.png` relationship-id numbers as the live `.docx`
    (`rId44, rId53, rId56, rId82, rId88, rId92, rId98, rId104` — identical set, both times).
    rId allocation order depends on document structure, so this match is not
    coincidental. This recipe (pandoc 3.9.0.2 + `--reference-doc=ref_submit.docx`,
    no other flags) is confirmed as what produced the shipped `.docx`, defects and all.

## 3. D1 — author-line superscript

**Exact markdown source** (`writing/submission/4J_manuscript_submission.md:21`, confirmed
unique with `grep -Fc`, count = 1):
```
Orcun Koral Iseri\textsuperscript{1,\*}
```
This is raw LaTeX. Pandoc's markdown reader does not interpret LaTeX macros embedded in a
plain paragraph — it passes `\textsuperscript{1,\*}` through as literal text with no
formatting. Confirmed by building the unpatched source and grepping the resulting
`word/document.xml`:
```
BEFORE (unpatched):
<w:r><w:t xml:space="preserve">Orcun Koral Iseri</w:t></w:r></w:p>
<w:p>...<w:t xml:space="preserve">1 Gina Cody School of Engineering...</w:t></w:r></w:p>
<w:p>...<w:t xml:space="preserve">*</w:t></w:r>...
```
No `w:vertAlign` anywhere near the author name — this exactly matches what the live
`.docx` itself contains (checked first, same text, same absence of superscript formatting).

**Fix (candidate a, applied):** rewrite to pandoc's native superscript syntax:
```
Orcun Koral Iseri^1,\*^
```
Built this version and grepped `word/document.xml`:
```
AFTER (fixed):
<w:r><w:t xml:space="preserve">Orcun Koral Iseri</w:t></w:r>
<w:r><w:rPr><w:vertAlign w:val="superscript" /></w:rPr><w:t xml:space="preserve">1,*</w:t></w:r></w:p>
```
Real Word superscript run property present. No filter or reference-doc trick was needed.

## 4. D2 — duplicate figure captions

**Pattern in the markdown** (8 occurrences, `writing/submission/4J_manuscript_submission.md`
lines 41/96/100/633/741/769/844/928):
```
![Figure N](figures/Figure_0N_....png)

**Figure N.** - <caption text>
```
Pandoc's `implicit_figures` markdown extension (on by default) promotes a standalone
`![alt](img)` paragraph into a Figure block and **auto-generates its own caption
paragraph from the alt text**. Confirmed by building the unpatched source and counting
caption-shaped paragraphs in `word/document.xml`:

```
BEFORE (unpatched, matches the live .docx exactly):
  pandoc auto-generated "ImageCaption"-style paragraphs: 8  (text: "Graphical abstract","Figure 1"…"Figure 7")
  document's own bold caption paragraphs:                 8  (text: "Graphical abstract.","Figure 1."…"Figure 7.")
  TOTAL caption paragraphs:                               16
```
Raw XML for the first figure, showing the two adjacent captions:
```
<w:p><w:pPr><w:pStyle w:val="ImageCaption" /></w:pPr><w:r><w:t>Graphical abstract</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="BodyText" /></w:pPr><w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>Graphical abstract.</w:t></w:r></w:p>
```

**Fix tested — two candidates:**
- (a) empty the alt text (`![](figures/...)`) — works for the caption count, but a
  quick side-test broke image embedding entirely (`[WARNING] Could not fetch resource...`)
  when pandoc's working directory didn't resolve `figures/` — fragile, and it requires
  editing all 8 markdown lines.
- (b) `--from=markdown-implicit_figures` (disable the extension) — **preferred and used**.
  Zero markdown edits. Rebuilt and recounted:
```
AFTER (--from=markdown-implicit_figures):
  pandoc auto-generated "ImageCaption"-style paragraphs: 0
  document's own bold caption paragraphs:                8
  TOTAL caption paragraphs:                              8
```
Image embedding unaffected: still 8 files in `word/media/`, still byte-identical md5s to
the source PNGs.

## 5. The build script

`4J_docs_occ/tools/4thJ_build_submission_docx.sh` (new file, only file written under the
live repo other than this report). Carries both fixes:
- D2 via the `--from=markdown-implicit_figures` pandoc flag (no source edit needed).
- D1 via a guarded, uniqueness-checked find/replace applied **only to a disposable temp
  copy** of the markdown (never the live `.md`) — idempotent: if the live `.md` has
  already been hand-edited to the native `^1,\*^` form, the script detects that and skips
  the rewrite instead of erroring or double-applying.
- Also uses `--reference-doc=extra/build_scripts/ref_submit.docx`, confirmed above as the
  actual styling source of the shipped `.docx` (Times New Roman, single-spacing,
  justified body, matching section/footer properties).
- Backs up the existing output `.docx` into `writing/submission/previous/` before
  overwriting, guarded with `[ -s "$BACKUP" ] || exit 1`.
- Prints the md5 of every embedded image and the caption-paragraph count of the freshly
  built `.docx` at the end, so every run proves D1/D2 rather than being trusted blind.
- Full comment block at the top explains what each flag does and why, including why the
  `cd` into the temp build dir is required (pandoc resolves relative image paths against
  the working directory, not the markdown file's own directory — this was found the hard
  way: a first version of the script silently dropped all 8 images until the `cd` was
  added; fixed before this report was written).

**Proof run — scratchpad only, never against live files.** Assembled a throwaway repo
layout under scratch (`tools/`, `writing/submission/{figures,extra/build_scripts,previous}`)
and ran the script against it three times:
1. Fresh build from the raw-LaTeX source: `D1: rewrote raw-LaTeX superscript marker...`,
   built successfully, 8 image md5s printed, caption count `8`, superscript check `PASS`.
2. Re-run after hand-editing the scratch source to the native `^1,\*^` form:
   `D1: source already carries the native superscript marker - nothing to rewrite.` —
   idempotent, still builds correctly.
3. Guarded-backup test: placed an **empty** file at the scratch output `.docx` path and
   re-ran — script printed `FATAL: backup at ... is empty or missing, aborting.` and
   exited `1` without touching anything further, as required.

The script was never invoked against `writing/submission/` in the real repo. Confirmed
afterward: live `.md` still contains the raw-LaTeX marker (`grep -Fc` = 1), live `.docx`
mtime unchanged.

## 6. Markdown edits another agent must apply (exact guarded pairs)

Only one edit is needed for D1 (D2 needs no markdown edit at all — it's a pandoc flag
carried by the build script). Verified unique in the **live** file with `grep -Fc`
(count = 1) before writing this section; no writes were made to the live file.

**File:** `4J_docs_occ/writing/submission/4J_manuscript_submission.md`

OLD (exact, line 21):
```
Orcun Koral Iseri\textsuperscript{1,\*}
```
NEW (exact):
```
Orcun Koral Iseri^1,\*^
```

Note: the build script above already applies this same rewrite on the fly to a disposable
temp copy, so the `.docx` build is already correct even before this line is hand-edited.
Applying it to the live markdown is optional cleanup (removes now-redundant raw LaTeX,
matches what actually renders), not required for the next build to be correct — the script
is idempotent either way (see 5.2 above).

## 7. Command to run when the content is final

```bash
4J_docs_occ/tools/4thJ_build_submission_docx.sh
```
(no arguments needed — defaults to
`writing/submission/4J_manuscript_submission.md` ->
`writing/submission/4J_manuscript_submission.docx`, backing up the previous `.docx` into
`writing/submission/previous/` first). Point the first argument at a different markdown
path to dry-run against a copy instead.

## What was NOT verified

- Whether Word itself (not just the OOXML) renders the superscript and single-caption
  fixes visually correctly — only the underlying XML was inspected (`w:vertAlign`,
  caption-paragraph counts), per the task's own verification method. No Word install was
  used to open the file.
- `post.py`'s table-formatting behaviour was read but not exercised — out of scope for
  D1/D2, not called by the new script.
- Whether `ref_submit.docx` is pandoc's unmodified default reference doc with only
  spacing/fonts changed, or a deeper custom template — page-margin/`sectPr` diff was
  spot-checked and matched; no exhaustive style-by-style diff was done since it wasn't
  needed to explain D1/D2 or to reproduce the live styling.
