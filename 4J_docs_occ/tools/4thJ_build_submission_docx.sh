#!/bin/bash
# 4thJ_build_submission_docx.sh
#
# Repeatable, re-runnable pandoc build for 4J_docs_occ/writing/submission/4J_manuscript_submission.md
# -> 4J_manuscript_submission.docx.
#
# WHY THIS SCRIPT EXISTS
#   The .docx that shipped before this script was built by an unrecorded ad-hoc pandoc
#   command. It had two defects that must be fixed by the BUILD, not by hand-editing the
#   .docx (Word edits do not survive the next markdown-driven rebuild):
#     D1. The author line's affiliation-number / corresponding-author-asterisk marker is
#         written in the markdown as raw LaTeX ("\textsuperscript{1,\*}"). Pandoc's docx
#         writer does not interpret raw LaTeX inside a markdown paragraph, so it comes out
#         as literal, non-superscript text in Word: "1 Gina Cody School..." with no visual
#         link back to the author name.
#     D2. Every figure in the markdown is written as
#         "![Figure N](figures/....png)" immediately followed by the document's own bold
#         caption paragraph "**Figure N.** - ...". Pandoc's docx writer treats a standalone
#         image paragraph as an implicit Figure and AUTO-GENERATES its own caption
#         paragraph from the image's alt text ("Figure N"). Word therefore shows two
#         caption paragraphs per figure: pandoc's auto one, then the document's own bold
#         one. Confirmed on this file: 16 caption paragraphs in the unpatched build (8
#         pandoc-auto + 8 own), 8 after the fix below.
#
# HOW EACH FLAG / STEP FIXES ITS DEFECT
#   D1 fix (markdown-side, applied here to a TEMP COPY of the source, never to the live
#          .md): the raw-LaTeX marker "\textsuperscript{1,\*}" is rewritten, with a
#          guarded, uniqueness-checked find/replace, to pandoc's own native superscript
#          syntax "^1,\*^". Pandoc's markdown reader understands "^...^" natively and
#          emits a real <w:rPr><w:vertAlign w:val="superscript"/></w:rPr> run in
#          word/document.xml - this was verified by building and grepping the XML (see
#          writing/IMP/DONE_docx_build_2026-09-14.md for the before/after XML). This is
#          preferred over a Lua filter or reference-doc trick because it is the smallest,
#          most legible change and it is idempotent: if the live .md has ALREADY been hand-
#          edited to use "^1,\*^" (see step 6 of the task), this script detects that and
#          skips the rewrite rather than double-applying or erroring.
#   D2 fix (pandoc flag, no markdown edit needed at all):
#          --from=markdown-implicit_figures disables pandoc's "implicit figure" extension,
#          i.e. it stops pandoc from promoting a standalone "![alt](img)" paragraph into a
#          Figure block with its own auto-caption. The image is still embedded exactly as
#          before (verified: same image count, same md5s as without the flag) - only the
#          auto-generated caption paragraph disappears, leaving the document's own bold
#          caption as the sole caption. This was preferred over emptying the image alt text
#          in the markdown because it requires touching NOTHING in the markdown, and a
#          quick side-test of the alt-text-emptying approach broke image embedding when the
#          images directory was not resolved from the right working directory - the flag
#          has no such failure mode.
#   Reference doc: --reference-doc=extra/build_scripts/ref_submit.docx reproduces the
#          live document's styling (Times New Roman body/heading fonts, single line
#          spacing 240 twips, justified body paragraphs, same footer/footnote section
#          properties). This was identified, not assumed: word/styles.xml and the
#          <w:sectPr> of the shipped .docx were diffed against (a) a build with no
#          reference doc and (b) a build with this reference doc; only (b) matched, and a
#          build with this exact recipe reproduced the SAME word/media/rIdNN.png
#          relationship-id numbering as the shipped .docx, which is strong evidence this
#          reference doc (or one identical to it) is what was actually used. See the DONE
#          report for the diff evidence. ref_submit_single.docx (double-spaced, 480 twips)
#          was ruled out the same way - it does not match.
#
# USAGE
#   4J_docs_occ/tools/4thJ_build_submission_docx.sh [markdown_path] [output_docx_path]
#   Defaults: markdown_path  = 4J_docs_occ/writing/submission/4J_manuscript_submission.md
#             output_docx_path = 4J_docs_occ/writing/submission/4J_manuscript_submission.docx
#   Both paths are resolved relative to the submission/ directory that holds figures/,
#   extra/build_scripts/ref_submit.docx and previous/. Point markdown_path at a scratch
#   copy to dry-run this script without touching anything live.
#
# SAFETY
#   - Never edits the input markdown in place; the D1 rewrite happens on a throwaway temp
#     copy in $TMP_BUILD_DIR, which is removed on exit.
#   - Refuses to run if the existing output .docx would be overwritten without a backup:
#     the backup step is guarded with [ -s "$existing" ] so it never "succeeds" on an
#     empty/missing file, and the script exits 1 if the guarded backup copy fails.
#   - Prints, at the end, the md5 of every embedded image and the caption-paragraph count
#     in the freshly built .docx, so every run proves its own D1/D2 status rather than
#     asking anyone to trust it.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SUBMISSION_DIR="$(cd "$SCRIPT_DIR/../writing/submission" && pwd)"

MD_IN="${1:-$SUBMISSION_DIR/4J_manuscript_submission.md}"
DOCX_OUT="${2:-$SUBMISSION_DIR/4J_manuscript_submission.docx}"
REF_DOCX="$SUBMISSION_DIR/extra/build_scripts/ref_submit.docx"
PREVIOUS_DIR="$SUBMISSION_DIR/previous"

if ! command -v pandoc >/dev/null 2>&1; then
  echo "FATAL: pandoc not found on PATH. Install pandoc before running this script." >&2
  exit 1
fi
if [ ! -f "$MD_IN" ]; then
  echo "FATAL: markdown source not found: $MD_IN" >&2
  exit 1
fi
if [ ! -f "$REF_DOCX" ]; then
  echo "FATAL: reference docx not found: $REF_DOCX" >&2
  exit 1
fi

echo "pandoc version:"
pandoc --version | head -1

# ---------------------------------------------------------------------------
# 1. Guarded backup of the existing output .docx (if any) before we touch it.
# ---------------------------------------------------------------------------
mkdir -p "$PREVIOUS_DIR"
if [ -f "$DOCX_OUT" ]; then
  STAMP="$(date +%Y-%m-%d_%H%M%S)"
  BACKUP="$PREVIOUS_DIR/$(basename "${DOCX_OUT%.docx}").pre_build_${STAMP}.docx"
  cp "$DOCX_OUT" "$BACKUP"
  # Guard: a backup that is empty or missing is treated as a failed backup - do not
  # proceed to overwrite the live .docx on top of a backup that did not really happen.
  [ -s "$BACKUP" ] || { echo "FATAL: backup at $BACKUP is empty or missing, aborting." >&2; exit 1; }
  echo "Backed up existing docx -> $BACKUP"
else
  echo "No existing docx at $DOCX_OUT - skipping backup."
fi

# ---------------------------------------------------------------------------
# 2. D1 fix, applied to a TEMP copy of the markdown only (never the live source).
# ---------------------------------------------------------------------------
TMP_BUILD_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_BUILD_DIR"' EXIT

TMP_MD="$TMP_BUILD_DIR/$(basename "$MD_IN")"
cp "$MD_IN" "$TMP_MD"

# figures/ is referenced by relative path from the markdown's own directory - copy it
# alongside the temp markdown so image paths still resolve, without duplicating the
# (potentially large) directory tree unnecessarily: a symlink is enough on this platform's
# Git Bash, cp -r as a portable fallback.
MD_DIR="$(cd "$(dirname "$MD_IN")" && pwd)"
if [ -d "$MD_DIR/figures" ]; then
  ln -s "$MD_DIR/figures" "$TMP_BUILD_DIR/figures" 2>/dev/null || cp -r "$MD_DIR/figures" "$TMP_BUILD_DIR/figures"
fi

D1_OLD='Orcun Koral Iseri\textsuperscript{1,\*}'
D1_NEW='Orcun Koral Iseri^1,\*^'

D1_OLD_COUNT="$(grep -Fc "$D1_OLD" "$TMP_MD" || true)"
if [ "$D1_OLD_COUNT" -eq 1 ]; then
  py -3 - "$TMP_MD" "$D1_OLD" "$D1_NEW" <<'PYEOF'
import sys
path, old, new = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(path, encoding="utf-8").read()
n = s.count(old)
assert n == 1, "expected exactly 1 occurrence of D1 marker, found %d" % n
s = s.replace(old, new)
open(path, "w", encoding="utf-8").write(s)
PYEOF
  echo "D1: rewrote raw-LaTeX superscript marker to pandoc native superscript syntax."
elif [ "$D1_OLD_COUNT" -eq 0 ]; then
  D1_NEW_COUNT="$(grep -Fc "$D1_NEW" "$TMP_MD" || true)"
  if [ "$D1_NEW_COUNT" -ge 1 ]; then
    echo "D1: source already carries the native superscript marker - nothing to rewrite."
  else
    echo "FATAL: neither the raw-LaTeX D1 marker nor the native-superscript D1 marker was found in $MD_IN. The author line may have changed - update this script's D1_OLD/D1_NEW before rebuilding." >&2
    exit 1
  fi
else
  echo "FATAL: found $D1_OLD_COUNT occurrences of the D1 marker (expected exactly 1) - refusing to guess which one to fix." >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# 3. Build. --from=markdown-implicit_figures is the D2 fix (see header comment).
# ---------------------------------------------------------------------------
TMP_DOCX="$TMP_BUILD_DIR/out.docx"
# Run pandoc with cwd = the temp build dir so the markdown's relative image paths
# ("figures/....png") resolve against the figures/ we just copied/linked in there -
# pandoc resolves relative resource paths against the working directory, not against
# the markdown file's own directory, so this cd is required (a plain
# `pandoc "$TMP_MD" -o ...` run from the caller's cwd silently drops every image).
( cd "$TMP_BUILD_DIR" && pandoc \
  --from=markdown-implicit_figures \
  --reference-doc="$REF_DOCX" \
  "$(basename "$TMP_MD")" \
  -o "$TMP_DOCX" )

# Energy and Buildings layout (2026-09-23): double-spaced body text + continuous line numbers.
# Set EB_LAYOUT=0 to skip. The patch prints its own counts and exits 1 if a patch did not apply.
if [ "${EB_LAYOUT:-1}" = "1" ]; then
  py -3 "$SCRIPT_DIR/4thJ_docx_eb_layout.py" "$TMP_DOCX" "$TMP_BUILD_DIR/out_eb.docx"
  mv "$TMP_DOCX" "$TMP_BUILD_DIR/out_plain.docx"
  cp "$TMP_BUILD_DIR/out_eb.docx" "$TMP_DOCX"
else
  echo "EB_LAYOUT=0: layout patch skipped."
fi

cp "$TMP_DOCX" "$DOCX_OUT"
echo "Built -> $DOCX_OUT"

# ---------------------------------------------------------------------------
# 4. Self-proof: unzip the just-built docx and report image md5s + caption count.
# ---------------------------------------------------------------------------
UNZIP_DIR="$TMP_BUILD_DIR/unzipped"
mkdir -p "$UNZIP_DIR"
( cd "$UNZIP_DIR" && unzip -oq "$TMP_DOCX" )

echo ""
echo "=== md5 of every embedded image (word/media/) ==="
if [ -d "$UNZIP_DIR/word/media" ]; then
  md5sum "$UNZIP_DIR/word/media"/*.png 2>/dev/null || true
else
  echo "(no word/media directory found - no images embedded)"
fi

echo ""
echo "=== caption paragraph count in word/document.xml ==="
py -3 - "$UNZIP_DIR/word/document.xml" <<'PYEOF'
import re, sys
data = open(sys.argv[1], encoding="utf-8").read()
pandoc_auto = re.findall(r'<w:pStyle w:val="ImageCaption" */></w:pPr>', data)
own = re.findall(
    r'<w:b\s*/><w:bCs\s*/></w:rPr><w:t[^>]*>((?:Graphical abstract|Figure \d)\.[^<]*)</w:t>',
    data,
)
print("pandoc auto-generated captions:", len(pandoc_auto), "(must be 0 - D2 fix)")
print("document's own bold captions:  ", len(own), "(the real captions)")
print("TOTAL caption paragraphs:      ", len(pandoc_auto) + len(own))
PYEOF

echo ""
echo "=== superscript check (D1) ==="
if grep -q '<w:vertAlign w:val="superscript"' "$UNZIP_DIR/word/document.xml"; then
  echo "PASS: found a real Word superscript run in word/document.xml"
else
  echo "WARNING: no superscript run found in word/document.xml - check the author line."
fi

echo ""
echo "Build complete."
