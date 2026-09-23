"""
sentence_length_count.py

Baseline / re-check tool for prose sentence length across the 3J manuscript chapters.

Usage:
    PYTHONIOENCODING=utf-8 py -3 writing/implementation/IMP/scripts/sentence_length_count.py

Rerunnable after a rewrite without editing: chapter files are discovered by globbing
`writing/chapters/Chapter_*.md` relative to the repo's `3J_docs_occ_nTemp` root (found by
walking up from this script's location), so new/renamed chapters are picked up automatically.
`.bak` files and anything not ending in `.md` are excluded by the glob itself.

--- Stripping rules (what counts as "prose") ---
Before sentence-splitting, each line of a chapter file is classified and either kept or
dropped from the prose stream:
  1. Code fences: lines between a pair of ``` (or ~~~) fence markers are dropped entirely
     (toggle a boolean on each fence line, drop everything while the toggle is on, and drop
     the fence line itself).
  2. ATX headings: a line starting with 1-6 `#` characters (optionally indented) is dropped.
     Headings are labels, not sentences.
  3. Markdown table rows: a line that (after stripping) starts with `|`, OR a table
     separator/alignment row like `|---|:---:|---|` or `---|---`, is dropped. Table cell text
     is not prose in the sense this script measures (it is not written as flowing sentences).
  4. Reference-style link/footnote definition lines (`[^1]: ...`, `[label]: url`) and raw HTML
     comment lines (`<!-- ... -->`) are dropped as non-prose scaffolding.
  5. Blank lines are kept as paragraph separators (they end the current sentence buffer) but
     contribute no words.
  6. Everything else (including list-item text, e.g. `- some sentence.`) is kept as prose;
     a leading list marker (`-`, `*`, `+`, or `1.`) is stripped so it doesn't get counted as
     a word or confuse sentence splitting.

Line numbers reported in the output are the 1-indexed line in the ORIGINAL file where each
kept prose line begins; a sentence's reported line is where its first word appeared.

--- Sentence splitting method (approximate, documented, not abbreviation-aware) ---
Prose lines belonging to the same paragraph (contiguous run of kept, non-blank lines) are
joined with a single space into one paragraph buffer, keeping track of which original line
each character position falls on. A sentence boundary is then any position where a run of
`.`, `!`, or `?` (one or more, to catch `...`, `?!`, etc.) is followed by whitespace and then
either (a) an uppercase letter, (b) end of paragraph, or (c) another sentence-ending
punctuation mark. This deliberately does NOT special-case abbreviations (e.g. "Dr.", "e.g.",
"Fig. 3") -- those will sometimes be split as if they ended a sentence. This is a known
approximation; the report is for relative/before-after comparison, not a publishable NLP
metric.

--- Word counting ---
A sentence is whitespace-split into tokens. Before counting, markdown emphasis markers
(`*`, `_`, `**`, `__`) are stripped from each token (so `*occupancy*` counts as one word,
not zero or two), as are surrounding backticks for inline code. Empty tokens after stripping
are not counted.
"""

import glob
import os
import re
import sys

# ---------------------------------------------------------------------------
# Locate repo root (the directory containing `writing/chapters/`) by walking
# up from this script's location, so the script works regardless of CWD.
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def find_repo_root(start):
    d = start
    for _ in range(10):
        if os.path.isdir(os.path.join(d, "writing", "chapters")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    raise SystemExit("Could not locate 'writing/chapters' by walking up from %s" % start)


REPO_ROOT = find_repo_root(SCRIPT_DIR)
CHAPTERS_GLOB = os.path.join(REPO_ROOT, "writing", "chapters", "Chapter_*.md")

FENCE_RE = re.compile(r"^\s*(```|~~~)")
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s")
TABLE_ROW_RE = re.compile(r"^\s*\|")
TABLE_SEP_RE = re.compile(r"^\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")
FOOTNOTE_DEF_RE = re.compile(r"^\s*\[\^?[^\]]+\]:\s")
HTML_COMMENT_RE = re.compile(r"^\s*<!--.*-->\s*$")
LIST_MARKER_RE = re.compile(r"^(\s*)([-*+]|\d+\.)\s+")

WORD_TOKEN_STRIP_RE = re.compile(r"^[*_`]+|[*_`]+$")

# Sentence boundary: one or more of . ! ? , followed by whitespace, followed by
# an uppercase letter OR another sentence-ending punctuation mark.
SENTENCE_END_RE = re.compile(r'([.!?]+)(\s+)(?=[A-Z]|[.!?"\'])')


def strip_to_prose_lines(text):
    """
    Return a list of (line_no, prose_text) for lines that count as prose.
    Blank lines are represented as (line_no, "") to preserve paragraph breaks.
    """
    lines = text.splitlines()
    out = []
    in_fence = False
    for i, raw in enumerate(lines, start=1):
        if FENCE_RE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if not raw.strip():
            out.append((i, ""))
            continue
        if HEADING_RE.match(raw):
            continue
        if TABLE_ROW_RE.match(raw):
            continue
        if TABLE_SEP_RE.match(raw) and ("-" in raw or ":" in raw) and "|" in raw:
            continue
        if FOOTNOTE_DEF_RE.match(raw):
            continue
        if HTML_COMMENT_RE.match(raw):
            continue
        cleaned = LIST_MARKER_RE.sub("", raw)
        out.append((i, cleaned.strip()))
    return out


def group_into_paragraphs(prose_lines):
    """
    Group contiguous non-blank prose lines into paragraphs. Each paragraph is
    returned as a list of (line_no, text) tuples (blank-line separators removed).
    """
    paragraphs = []
    current = []
    for line_no, text in prose_lines:
        if text == "":
            if current:
                paragraphs.append(current)
                current = []
        else:
            current.append((line_no, text))
    if current:
        paragraphs.append(current)
    return paragraphs


def split_sentences_with_lines(paragraph):
    """
    paragraph: list of (line_no, text) tuples for one paragraph.
    Returns list of (sentence_text, start_line_no).
    Builds a joined buffer with a map from character offset -> line_no, splits
    on sentence boundaries, and reports the line_no at each sentence's start.
    """
    buf_parts = []
    offset_to_line = []  # offset_to_line[k] = line_no for character index k in buf
    for idx, (line_no, text) in enumerate(paragraph):
        if idx > 0:
            buf_parts.append(" ")
            offset_to_line.append(paragraph[idx][0])
        buf_parts.append(text)
        offset_to_line.extend([line_no] * len(text))
    buf = "".join(buf_parts)
    if not buf.strip():
        return []

    sentences = []
    start = 0
    for m in SENTENCE_END_RE.finditer(buf):
        end = m.end(1)  # end of the punctuation run, before the trailing whitespace
        sent = buf[start:end].strip()
        if sent:
            line_no = offset_to_line[start] if start < len(offset_to_line) else offset_to_line[-1]
            sentences.append((sent, line_no))
        start = m.end()  # resume after the whitespace
    tail = buf[start:].strip()
    if tail:
        line_no = offset_to_line[start] if start < len(offset_to_line) else offset_to_line[-1]
        sentences.append((tail, line_no))
    return sentences


def count_words(sentence):
    tokens = sentence.split()
    words = []
    for t in tokens:
        t2 = WORD_TOKEN_STRIP_RE.sub("", t)
        if t2:
            words.append(t2)
    return len(words)


def analyze_file(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    prose_lines = strip_to_prose_lines(text)
    paragraphs = group_into_paragraphs(prose_lines)
    all_sentences = []  # (sentence_text, line_no, word_count)
    for para in paragraphs:
        for sent, line_no in split_sentences_with_lines(para):
            wc = count_words(sent)
            all_sentences.append((sent, line_no, wc))
    return all_sentences


def main():
    files = sorted(glob.glob(CHAPTERS_GLOB))
    if not files:
        print("No chapter files found matching %s" % CHAPTERS_GLOB)
        sys.exit(1)

    per_file_stats = []  # (relpath, total_sentences, over30)
    global_longest = []  # (word_count, relpath, line_no, sentence_text)

    for path in files:
        relpath = os.path.relpath(path, REPO_ROOT).replace("\\", "/")
        sentences = analyze_file(path)
        total = len(sentences)
        over30 = sum(1 for (_, _, wc) in sentences if wc > 30)
        per_file_stats.append((relpath, total, over30))
        for sent, line_no, wc in sentences:
            global_longest.append((wc, relpath, line_no, sent))

    global_longest.sort(key=lambda x: x[0], reverse=True)
    top20 = global_longest[:20]

    # ---- Report ----
    print("=" * 78)
    print("SENTENCE LENGTH REPORT")
    print("Chapters glob: %s" % CHAPTERS_GLOB)
    print("=" * 78)
    print()
    print("%-45s %10s %10s %8s" % ("File", "Sentences", ">30 words", "%>30"))
    print("-" * 78)
    total_sentences_all = 0
    total_over30_all = 0
    for relpath, total, over30 in per_file_stats:
        pct = (100.0 * over30 / total) if total else 0.0
        print("%-45s %10d %10d %7.1f%%" % (relpath, total, over30, pct))
        total_sentences_all += total
        total_over30_all += over30
    print("-" * 78)
    pct_all = (100.0 * total_over30_all / total_sentences_all) if total_sentences_all else 0.0
    print("%-45s %10d %10d %7.1f%%" % ("TOTAL", total_sentences_all, total_over30_all, pct_all))
    print()

    print("=" * 78)
    print("TOP 20 LONGEST SENTENCES (overall)")
    print("=" * 78)
    for rank, (wc, relpath, line_no, sent) in enumerate(top20, start=1):
        loc = "%s:%d" % (relpath, line_no)
        display = sent if len(sent) <= 400 else (sent[:400] + " [truncated]")
        print("\n#%-2d  %3d words  %s" % (rank, wc, loc))
        print("     %s" % display)

    print()
    print("=" * 78)
    print("Done. Total files analyzed: %d" % len(files))


if __name__ == "__main__":
    main()
