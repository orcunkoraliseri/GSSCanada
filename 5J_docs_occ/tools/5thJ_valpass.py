#!/usr/bin/env python
"""5J Step 8 part D: validation pass on the manuscript draft (text only, offline).

One process. Runs every gate on the clean draft, then on a planted copy (written to a scratch folder),
and checks that every plant raised its section count.

Usage: py -3.13 tools/5thJ_valpass.py --scratch <dir>

Exit code: 0 = ran, every plant fired; 1 = a plant did not fire; 2 = could not run (missing input, exception).
Hits on the clean draft never change the exit code: they are the report.

Gate 2.2 (DOI lookup against Crossref) is NOT done here by order of the coordinator: DOIs are only listed as text.
No network access of any kind is used by this script.
"""
import argparse
import bisect
import hashlib
import os
import re
import sys
import traceback
import unicodedata
from collections import Counter

ROOT = "C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/5J_docs_occ/"
DRAFT = ROOT + "writing/5J_manuscript_draft.md"
PIPELINE = ROOT + "5thJ_00_Occupancy_Surrogate_Pipeline.md"
SOURCES = [
    "Step8_docs/impl/2026-10-01_wp6_draft.md", "Step8_docs/impl/2026-10-01_wp6_s38.md",
    "Step8_docs/impl/2026-10-01_wp6_s38_text.md", "Step6_docs/outputs_step6/RESULTS.md",
    "Step7_docs/outputs_step7/district_check_summary.md", "Step7_docs/outputs_step7/speed.md",
    "Step7_docs/outputs_step7/district_spread.csv", "Step7_docs/impl/2026-10-01_wp5_district.md",
    "Step5_docs/outputs_step5/winner.md", "Step5_docs/outputs_step5/models.md",
    "Step5_docs/outputs_step5/step5_rules.md", "Step4_docs/outputs_step4/perturbations.md",
    "Step2_docs/outputs_step2/campaign_design.md",
]
RESULTS = ROOT + "Step6_docs/outputs_step6/RESULTS.md"
FIG_DIR = ROOT + "writing/"
FIG_SCRIPT_DIR = ROOT + "figures/scripts/"

SECTIONS = ["1.1", "1.2a", "1.2b", "1.3", "1.4", "2.1", "2.2a", "2.2b", "2.3", "3.1", "3.2", "3.3", "3.4", "4.1"]


def p(*a):
    print(*a)


def md5(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def read_lines(path):
    with open(path, encoding="utf-8") as f:
        return f.read().split("\n")


def norm(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", s.lower())


def sentence_at(line, off):
    """Sentence of `line` that holds character offset `off`."""
    if line.lstrip().startswith("|"):
        return line.strip()[:200]
    starts = [0] + [m.end() for m in re.finditer(r"(?<=[.?!])\s+(?=[A-Z0-9*(\[])", line)]
    s = max(x for x in starts if x <= off)
    later = [x for x in starts if x > off]
    e = min(later) if later else len(line)
    return line[s:e].strip()


def sentences(line):
    if line.lstrip().startswith("|"):
        return [line.strip()]
    parts = re.split(r"(?<=[.?!])\s+(?=[A-Z0-9*(\[])", line)
    return [x.strip() for x in parts if x.strip()]


# ----------------------------------------------------------------------------------------------
# Region helpers
# ----------------------------------------------------------------------------------------------
def find_line(lines, startswith):
    for i, l in enumerate(lines):
        if l.startswith(startswith):
            return i
    return None


def regions(lines):
    ref = find_line(lines, "# References")
    cre = find_line(lines, "# CRediT")
    nom_start = find_line(lines, "# Nomenclature")
    auth = find_line(lines, "## Author Information")
    abst = find_line(lines, "## Abstract")
    ai = None
    for i, l in enumerate(lines):
        if l.startswith("#") and "Declaration of generative AI" in l:
            ai = i
    if None in (ref, cre, auth, abst, ai):
        raise RuntimeError("missing heading: ref=%s cre=%s auth=%s abst=%s ai=%s" % (ref, cre, auth, abst, ai))
    ai_end = ai + 1
    while ai_end < len(lines) and not lines[ai_end].startswith("# "):
        ai_end += 1
    return dict(ref=ref, cre=cre, auth=auth, abst=abst, ai=ai, ai_end=ai_end, nom=nom_start)


# ----------------------------------------------------------------------------------------------
# Gate 1.1 numbers
# ----------------------------------------------------------------------------------------------
NUM = re.compile(r"(?<![\w.])\d[\d,]*(?:\.\d+)?(?!\d)")
SCI = re.compile(r"(?<![\w.])\d(?:\.\d+)?e[-+]?\d+(?![\w])")
HASH = re.compile(r"\b[0-9a-f]{7,}\b")


def to_float(tok):
    return float(tok.replace(",", ""))


def decimals(tok):
    t = tok.replace(",", "")
    return len(t.split(".")[1]) if "." in t else 0


_pool_cache = {}


def build_pool(missing):
    if "pool" in _pool_cache:
        return _pool_cache["pool"]
    texts = []
    for rel in SOURCES:
        path = ROOT + rel
        if not os.path.isfile(path):
            missing.append(rel)
            continue
        with open(path, encoding="utf-8", errors="replace") as f:
            texts.append(f.read())
    raw = HASH.sub(" ", "\n".join(texts))
    toks = set()
    vals = set()
    for m in NUM.finditer(raw):
        t = m.group(0).rstrip(",")
        t = t.replace(",", "")
        toks.add(t)
        try:
            vals.add(float(t))
        except ValueError:
            pass
    scis = set(m.group(0) for m in SCI.finditer(raw))
    base = sorted(vals)
    pool = dict(toks=toks, sci=scis, base=base,
                k=sorted(v / 1000.0 for v in vals), c=sorted(v * 100.0 for v in vals))
    _pool_cache["pool"] = pool
    return pool


def has_near(arr, v, tol):
    i = bisect.bisect_left(arr, v - tol - 1e-12)
    return i < len(arr) and arr[i] <= v + tol + 1e-12


CITE_YEAR_PAREN = re.compile(r"(?<=[A-Za-z\u00C0-\u017F.]), (?:19|20)\d\d[a-z]?(?=[);,])")
CITE_YEAR_NARR = re.compile(r"(?<=[A-Za-z\u00C0-\u017F.]) \((?:19|20)\d\d[a-z]?\)")
REFWORD = re.compile(r"\b(?:Sections?|Figures?|Tables?|Appendix|Eq\.|Equations?)\s+[A-Z]?\.?\d+(?:\.\d+)*"
                     r"(?:\s*(?:to|and|,|-)\s*\d+(?:\.\d+)*)*")
CLAUSE = re.compile(r"\bclause\s+[\d.]+")
IMG = re.compile(r"!\[[^\]]*\]\([^)]*\)")
BRACKET = re.compile(r"\[[^\]]*\]")


def clean_for_numbers(line):
    """Blank (same length) every span that must not be read as a data number."""
    s = line
    if s.startswith("#"):
        return " " * len(s)
    s = re.sub(r"^(\s*)\d+\.\s", lambda m: m.group(1) + " " * (len(m.group(0)) - len(m.group(1))), s)
    for rx in (IMG, BRACKET, CITE_YEAR_PAREN, CITE_YEAR_NARR, REFWORD, CLAUSE):
        s = rx.sub(lambda m: " " * len(m.group(0)), s)
    return s


def gate_numbers(lines, reg, missing):
    pool = build_pool(missing)
    out = []      # unmatched
    weak = []     # matched only by rounding or scaling
    kinds = Counter()
    n_total = 0
    in_scope = []
    for i, l in enumerate(lines):
        if i >= reg["cre"]:
            break
        if reg["auth"] <= i < reg["abst"]:
            continue
        in_scope.append(i)
    for i in in_scope:
        raw = lines[i]
        c = clean_for_numbers(raw)
        sci_spans = []
        for m in SCI.finditer(c):
            n_total += 1
            ok = m.group(0) in pool["sci"]
            kinds["exact" if ok else "unmatched"] += 1
            if not ok:
                out.append((i + 1, m.group(0), sentence_at(raw, m.start())))
            sci_spans.append((m.start(), m.end()))
        for m in NUM.finditer(c):
            if any(a <= m.start() < b for a, b in sci_spans):
                continue
            tok = m.group(0).rstrip(",")
            n_total += 1
            t = tok.replace(",", "")
            v = to_float(tok)
            d = decimals(tok)
            tol = 0.5 * 10 ** (-d)
            if t in pool["toks"]:
                kinds["exact"] += 1
                if "." not in t and v < 100:
                    kinds["exact_small_int_coincidence_prone"] += 1
                continue
            if has_near(pool["base"], v, tol):
                kinds["rounded"] += 1
                weak.append((i + 1, tok, "rounded", sentence_at(raw, m.start())))
                continue
            if has_near(pool["k"], v, tol):
                kinds["kwh_to_mwh"] += 1
                weak.append((i + 1, tok, "kwh_to_mwh", sentence_at(raw, m.start())))
                continue
            if has_near(pool["c"], v, tol):
                kinds["fraction_to_pct"] += 1
                weak.append((i + 1, tok, "fraction_to_pct", sentence_at(raw, m.start())))
                continue
            kinds["unmatched"] += 1
            out.append((i + 1, tok, sentence_at(raw, m.start())))
    return out, weak, kinds, n_total


# ----------------------------------------------------------------------------------------------
# Gate 1.2 verdict counts
# ----------------------------------------------------------------------------------------------
COUNT_RX = re.compile(r"(\d+(?:\s*(?:,|and|or|to)\s*\d+)*)\s+of\s+(\d+)")
VERDICT_RX = re.compile(r"\bpass(?:es|ed|ing)?\b|\bfail\w*|\bnot evaluable\b|NOT_EVALUABLE", re.I)


def gate_counts(lines, reg, res_lines):
    counts = []
    verd = []
    res_tokens = []
    for j, rl in enumerate(res_lines):
        res_tokens.append((j + 1, set(re.findall(r"(?<![\w.])\d+(?![\w])", rl)), rl))
    for i, l in enumerate(lines):
        if i >= reg["ref"] or (reg["auth"] <= i < reg["abst"]) or l.startswith("#"):
            continue
        c = IMG.sub(lambda m: " " * len(m.group(0)), l)
        for m in COUNT_RX.finditer(c):
            xs = re.findall(r"\d+", m.group(1))
            y = m.group(2)
            need = set(xs) | {y}
            src = None
            for ln, toks, rl in res_tokens:
                if need <= toks and re.search(r"(?:of|/)\s*" + y + r"(?!\d)", rl):
                    src = (ln, rl.strip()[:160])
                    break
            counts.append((i + 1, m.group(0), src))
        for s in sentences(c):
            if VERDICT_RX.search(s):
                verd.append((i + 1, s))
    return counts, verd


# ----------------------------------------------------------------------------------------------
# Gates 1.3 and 1.4
# ----------------------------------------------------------------------------------------------
G13 = [r"\bfirst\b", r"to our knowledge", r"\bnovel\b", r"for the first time", r"\bno previous\b",
       r"\bnobody\b", r"\bnever been\b"]
G14 = [r"first building energy surrogate", r"first hourly residential stock surrogate",
       r"first to score a surrogate on differences"]


def gate_phrases(lines, reg, pats, upto):
    hits = []
    for i, l in enumerate(lines):
        if i >= upto:
            break
        for pt in pats:
            for m in re.finditer(pt, l, re.I):
                hits.append((i + 1, m.group(0), sentence_at(l, m.start())))
    return hits


# ----------------------------------------------------------------------------------------------
# Gates 2.1 and 2.2
# ----------------------------------------------------------------------------------------------
NAMEW = r"[A-Z][\w\u00C0-\u017F'\u2019-]+"


def cite_key(name, year):
    first = re.match(NAMEW, name.strip())
    return (norm(first.group(0)) if first else norm(name), year)


def intext_cites(lines, reg):
    cites = []
    for i, l in enumerate(lines):
        if i >= reg["ref"] or (reg["auth"] <= i < reg["abst"]) or l.startswith("#"):
            continue
        c = IMG.sub(lambda m: " " * len(m.group(0)), l)
        for m in re.finditer(r"\(([^()]*?(?:19|20)\d\d[a-z]?[^()]*)\)", c):
            for piece in m.group(1).split(";"):
                piece = piece.strip()
                y = re.search(r"\b((?:19|20)\d\d)[a-z]?\b", piece)
                if not y or not re.match(NAMEW, piece):
                    continue
                name = piece[:y.start()].rstrip(", ")
                if not name:
                    continue
                cites.append((i + 1, cite_key(name, y.group(1)), piece))
        for m in re.finditer(r"(" + NAMEW + r"(?: and " + NAMEW + r")?(?: et al\.)?) \(((?:19|20)\d\d)[a-z]?\)", c):
            cites.append((i + 1, cite_key(m.group(1), m.group(2)), m.group(0)))
    return cites


def reference_entries(lines, reg):
    ents = []
    cur = []
    start = None
    for i in range(reg["ref"] + 1, len(lines)):
        l = lines[i]
        if l.strip() == "":
            if cur:
                ents.append((start, " ".join(x.strip() for x in cur)))
                cur = []
            continue
        if not cur:
            start = i + 1
        cur.append(l)
    if cur:
        ents.append((start, " ".join(x.strip() for x in cur)))
    out = []
    for ln, txt in ents:
        first = re.match(NAMEW, txt)
        y = re.search(r"\(((?:19|20)\d\d)[a-z]?\)", txt)
        doi = re.search(r"(10\.\d{4,9}/\S+)", txt)
        d = doi.group(1).rstrip(".") if doi else None
        out.append((ln, (norm(first.group(0)) if first else "?", y.group(1) if y else "?"), txt, d))
    return out


def gate_citations(lines, reg):
    cites = intext_cites(lines, reg)
    refs = reference_entries(lines, reg)
    refkeys = {r[1] for r in refs}
    citekeys = {c[1] for c in cites}
    no_ref = [(ln, k, txt) for ln, k, txt in cites if k not in refkeys]
    uncited = [(ln, k, txt[:90]) for ln, k, txt, d in refs if k not in citekeys]
    dois = [(ln, k, d) for ln, k, txt, d in refs if d]
    return cites, refs, no_ref, uncited, dois


# ----------------------------------------------------------------------------------------------
# Gate 2.3
# ----------------------------------------------------------------------------------------------
def gate_credits(lines, reg):
    hits = []
    rx = re.compile(r"\bINE\b|\bISTAT\b|UK Data Service|\bUKDS\b|Sullivan|Gershuny|Instituto Nacional|Istituto Nazionale")
    for i, l in enumerate(lines):
        if i >= reg["ref"] or l.startswith("#"):
            continue
        for s in sentences(IMG.sub("", l)):
            if rx.search(s):
                hits.append((i + 1, s))
    return hits


def required_wording():
    if not os.path.isfile(PIPELINE):
        return None
    out = []
    rx = re.compile(r"Elaboraci|say changes were made|Sullivan and Gershuny|do not suggest INE|acknowledge each source|"
                    r"cite and acknowledge|clause 11|clause 12")
    for i, l in enumerate(read_lines(PIPELINE)):
        if rx.search(l):
            out.append((i + 1, l.strip()[:600]))
    return out


# ----------------------------------------------------------------------------------------------
# Gates 3.1 to 3.3
# ----------------------------------------------------------------------------------------------
TOOLS = [r"\bClaude\b", r"\bAnthropic\b", r"\bGemini\b", r"Google DeepMind", r"\bGPT\b", r"\bChatGPT\b",
         r"\bOpenAI\b", r"\bCopilot\b", r"\bLLMs?\b", r"language model", r"\bSonnet\b", r"\bOpus\b"]


def gate_tools(lines, reg):
    hits = []
    for i, l in enumerate(lines):
        if i >= reg["ref"] or reg["ai"] <= i < reg["ai_end"]:
            continue
        for pt in TOOLS:
            for m in re.finditer(pt, l, re.I):
                hits.append((i + 1, m.group(0), sentence_at(l, m.start())))
    return hits


META_CS = [r"\bFINDING\b", r"\b5J\b", r"\bG5J\b", r"\bWP\d*\b", r"\bB4\b"]
META_CI = [r"not comparable", r"stated here", r"see above", r"placeholder", r"\bTBD\b", r"\bTODO\b",
           r"\bSteps?\s+[1-8]\b", r"\bmanager\b", r"\bemployee\b", r"\bledger\b", r"\bsbatch\b", r"Speed cluster",
           r"\bjobs?\b", r"our earlier draft", r"previous version", r"as decided"]


def gate_meta(lines, reg):
    hits = []
    for i, l in enumerate(lines):
        if i >= reg["ref"]:
            break
        t = IMG.sub(lambda m: " " * len(m.group(0)), l)
        for pt in META_CS:
            for m in re.finditer(pt, t):
                hits.append((i + 1, m.group(0), sentence_at(l, m.start())))
        for pt in META_CI:
            for m in re.finditer(pt, t, re.I):
                hits.append((i + 1, m.group(0), sentence_at(l, m.start())))
        for m in re.finditer(r"\[", t):
            hits.append((i + 1, "[", sentence_at(l, m.start())))
    return hits


FAIL_RX = re.compile(r"\bfail(?:ure|ures|ed|s|ing)?\b", re.I)
GATE_WORDS = re.compile(r"\bgate|\btest\b|\btests\b|\bband|\bpass|occupancy-effect|\bclaim|\bcontrol|\bcell|\bscorer|\bskill|"
                        r"\bverdict|ASHRAE|\bcheck|\binterval|\bmust fail|stand-in", re.I)


def gate_failwords(lines, reg):
    hits = []
    for i, l in enumerate(lines):
        if i >= reg["ref"]:
            break
        t = IMG.sub(lambda m: " " * len(m.group(0)), l)
        for m in FAIL_RX.finditer(t):
            s = sentence_at(l, m.start())
            mark = "GATE" if GATE_WORDS.search(s) else "PROSE"
            hits.append((i + 1, m.group(0), mark, s))
    return hits


# ----------------------------------------------------------------------------------------------
# Gates 3.4 and 4.1
# ----------------------------------------------------------------------------------------------
def gate_figures(lines, reg):
    out = []
    for i, l in enumerate(lines):
        if i >= reg["ref"]:
            break
        for m in re.finditer(r"!\[Figure (\d+)\]\(([^)]+)\)", l):
            n = int(m.group(1))
            path = FIG_DIR + m.group(2)
            exists = os.path.isfile(path)
            stem = os.path.splitext(os.path.basename(m.group(2)))[0]  # Figure_05_district_spread
            rest = re.sub(r"^Figure_\d+_", "", stem)
            cands = ["fig%02d_%s.py" % (n, rest)]
            if n == 5:
                cands.append("fig05_data.py")
            if n == 2:
                cands.append("fig02_plot.py")
            found = [c for c in cands if os.path.isfile(FIG_SCRIPT_DIR + c)]
            out.append((i + 1, n, m.group(2), exists, found, cands))
    return out


def gate_data_statement(lines, reg):
    i0 = find_line(lines, "# Data availability")
    if i0 is None:
        raise RuntimeError("no Data availability heading")
    j = i0 + 1
    while j < len(lines) and not lines[j].startswith("# "):
        j += 1
    sec = [(k + 1, lines[k]) for k in range(i0 + 1, j) if lines[k].strip()]
    uk = []
    for ln, t in sec:
        for m in re.finditer(r"\bUK\b|United Kingdom|\bUKDS\b|UK Data Service|\bweights?\b|\bschedules?\b|released|redistribut|shared|share",
                             t, re.I):
            uk.append((ln, m.group(0), sentence_at(t, m.start())))
    prom = []
    for ln, t in sec:
        for s in sentences(t):
            if re.search(r"available|released|redistribut|shared|deposit|repository", s, re.I):
                prom.append((ln, s))
    return sec, uk, prom


# ----------------------------------------------------------------------------------------------
# One full run on one file
# ----------------------------------------------------------------------------------------------
def run_all(path, verbose, label):
    lines = read_lines(path)
    reg = regions(lines)
    missing = []
    R = {}
    R["1.1"] = gate_numbers(lines, reg, missing)
    res_lines = read_lines(RESULTS) if os.path.isfile(RESULTS) else []
    R["1.2"] = gate_counts(lines, reg, res_lines)
    R["1.3"] = gate_phrases(lines, reg, G13, reg["ref"])
    R["1.4"] = gate_phrases(lines, reg, G14, reg["ref"])
    R["2"] = gate_citations(lines, reg)
    R["2.3"] = gate_credits(lines, reg)
    R["3.1"] = gate_tools(lines, reg)
    R["3.2"] = gate_meta(lines, reg)
    R["3.3"] = gate_failwords(lines, reg)
    R["3.4"] = gate_figures(lines, reg)
    R["4.1"] = gate_data_statement(lines, reg)
    R["missing"] = missing
    # items with keys, for the plant comparison
    items = {
        "1.1": [((a, b), (a, b, c)) for a, b, c in R["1.1"][0]],
        "1.2a": [((a, b), (a, b, c)) for a, b, c in R["1.2"][0]],
        "1.2b": [((a, s[:60]), (a, s)) for a, s in R["1.2"][1]],
        "1.3": [((a, b), (a, b, c)) for a, b, c in R["1.3"]],
        "1.4": [((a, b), (a, b, c)) for a, b, c in R["1.4"]],
        "2.1": [((ln, k), (ln, k, txt)) for ln, k, txt in R["2"][2]],
        "2.2a": [((ln, k), (ln, k, txt)) for ln, k, txt in R["2"][3]],
        "2.2b": [((ln, d), (ln, k, d)) for ln, k, d in R["2"][4]],
        "2.3": [((a, b[:40]), (a, b)) for a, b in R["2.3"]],
        "3.1": [((a, b), (a, b, c)) for a, b, c in R["3.1"]],
        "3.2": [((a, b), (a, b, c)) for a, b, c in R["3.2"]],
        "3.3": [((a, b), (a, b, m, c)) for a, b, m, c in R["3.3"]],
        "3.4": [((a, n), (a, n, pth, ex, fd)) for a, n, pth, ex, fd, cd in R["3.4"]],
        "4.1": [((a, b), (a, b, c)) for a, b, c in R["4.1"][1]],
    }
    R["items"] = items
    R["counts"] = {k: len(v) for k, v in items.items()}
    if verbose:
        print_report(R, lines, reg, label)
    return R


def print_report(R, lines, reg, label):
    p("=" * 100)
    p("REPORT ON", label)
    p("=" * 100)
    if R["missing"]:
        p("MISSING SOURCE FILES (named in the task, not found, not searched for):", R["missing"])
    un, weak, kinds, ntot = R["1.1"]
    p("\n--- GATE 1.1 numbers ---")
    p("numbers read: %d; match kinds: %s" % (ntot, dict(kinds)))
    p("UNMATCHED numbers: %d (not necessarily wrong: a list for the manager)" % len(un))
    for ln, tok, sent in un:
        p("  UNMATCHED L%d  %s  | %s" % (ln, tok, sent[:300]))
    wk = [w for w in weak if ("." in w[1] or to_float(w[1]) >= 100)]
    p("WEAK matches (only by rounding or scale, number has decimals or is >= 100): %d" % len(wk))
    for ln, tok, kind, sent in wk:
        p("  WEAK L%d  %s  (%s)  | %s" % (ln, tok, kind, sent[:200]))
    counts, verd = R["1.2"]
    p("\n--- GATE 1.2 verdict counts ---")
    p("'x of y' counts: %d; of these without a RESULTS.md line: %d" % (len(counts), sum(1 for c in counts if c[2] is None)))
    for ln, txt, src in counts:
        p("  COUNT L%d  %s  -> %s" % (ln, txt, ("RESULTS.md:%d %s" % src) if src else "no source line"))
    p("sentences with pass / fail / not evaluable: %d" % len(verd))
    for ln, s in verd:
        p("  VERDICT L%d  %s" % (ln, s[:400]))
    p("\n--- GATE 1.3 claim words ---  hits: %d" % len(R["1.3"]))
    for ln, w, s in R["1.3"]:
        p("  1.3 L%d  [%s]  %s" % (ln, w, s[:400]))
    p("\n--- GATE 1.4 not-claimed phrases ---  hits: %d" % len(R["1.4"]))
    for ln, w, s in R["1.4"]:
        p("  1.4 L%d  [%s]  %s" % (ln, w, s[:400]))
    cites, refs, no_ref, uncited, dois = R["2"]
    p("\n--- GATE 2.1 in-text citations without a reference entry ---  %d (of %d in-text citations, %d distinct keys)"
      % (len(no_ref), len(cites), len({c[1] for c in cites})))
    for ln, k, txt in no_ref:
        p("  2.1 ORPHAN CITATION L%d  %s  | %s" % (ln, k, txt))
    p("\n--- GATE 2.2a reference entries never cited ---  %d (of %d entries)" % (len(uncited), len(refs)))
    for ln, k, txt in uncited:
        p("  2.2a UNCITED REFERENCE L%d  %s  | %s" % (ln, k, txt))
    p("reference keys parsed:", ", ".join("%s/%s" % r[1] for r in refs))
    p("\n--- GATE 2.2b DOIs printed as text (NO lookup was made; left to the external check) ---  %d" % len(dois))
    for ln, k, d in dois:
        p("  DOI L%d  %s  %s" % (ln, k, d))
    p("\n--- GATE 2.3 licence credit sentences ---  %d" % len(R["2.3"]))
    for ln, s in R["2.3"]:
        p("  2.3 L%d  %s" % (ln, s[:400]))
    rw = required_wording()
    p("required wording (lines of 5thJ_00_Occupancy_Surrogate_Pipeline.md that state it):")
    if rw is None:
        p("  PIPELINE FILE NOT FOUND")
    else:
        for ln, t in rw:
            p("  PIPE L%d  %s" % (ln, t))
    p("\n--- GATE 3.1 tool names outside the AI declaration ---  hits: %d" % len(R["3.1"]))
    for ln, w, s in R["3.1"]:
        p("  3.1 L%d  [%s]  %s" % (ln, w, s[:400]))
    p("\n--- GATE 3.2 meta and process notes ---  hits: %d" % len(R["3.2"]))
    for ln, w, s in R["3.2"]:
        p("  3.2 L%d  [%s]  %s" % (ln, w, s[:400]))
    p("\n--- GATE 3.3 failure words (GATE/PROSE is the script's suggestion) ---  hits: %d" % len(R["3.3"]))
    for ln, w, m, s in R["3.3"]:
        p("  3.3 L%d  [%s]  %s  | %s" % (ln, w, m, s[:400]))
    p("\n--- GATE 3.4 figures ---")
    for ln, n, pth, ex, fd, cd in R["3.4"]:
        p("  FIG L%d  Figure %d  %s  file %s  script %s" % (ln, n, pth, "EXISTS" if ex else "MISSING",
                                                          ", ".join(fd) if fd else "NOT FOUND (tried %s)" % ", ".join(cd)))
    sec, uk, prom = R["4.1"]
    p("\n--- GATE 4.1 data statement ---")
    for ln, t in sec:
        p("  DATA L%d  %s" % (ln, t))
    p("promises (sentences with available / released / shared ...): %d" % len(prom))
    for ln, s in prom:
        p("  PROMISE L%d  %s" % (ln, s[:400]))
    p("UK, weights, schedules, release words in the section: %d" % len(uk))
    for ln, w, s in uk:
        p("  4.1 FLAG L%d  [%s]  %s" % (ln, w, s[:300]))


# ----------------------------------------------------------------------------------------------
# Planting
# ----------------------------------------------------------------------------------------------
PLANTS = [
    # (section it must raise, anchor prefix of the line, text appended)
    ("3.1", "**Figure 3.**", " Drawn with Claude."),
    ("1.3", "Households differ, and the difference", " To our knowledge, this has not been done."),
    ("3.3", "**The noise floor is zero.**", " This is a failure of the design."),
    ("1.1", "The pinned model meets the load bands in 21 of 32 cells", " The mean run used 7,777 kWh."),
    # informational probes (not counted in the exit code): a fake decimal must fire, a fake small integer may not
    ("probe", "In the works read for this study, none of these surrogates", " Ratio 0.4137 and 37 flats."),
    ("2.1", "A learned surrogate of the simulation would remove the cost.", " This is known (Smith et al., 2019)."),
    ("3.2", "A new household in this study has a new composition", " [TBD]"),
]


def make_planted(src_lines, dst):
    lines = list(src_lines)
    for sec, anchor, add in PLANTS:
        idx = [i for i, l in enumerate(lines) if l.startswith(anchor)]
        if len(idx) != 1:
            raise RuntimeError("plant anchor %r found %d times" % (anchor, len(idx)))
        lines[idx[0]] = lines[idx[0]] + add
    with open(dst, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", required=True)
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    p("5thJ_valpass run (offline, no web request of any kind)")
    if not os.path.isfile(DRAFT):
        p("DRAFT NOT FOUND:", DRAFT)
        return 2
    md_before = md5(DRAFT)
    p("draft:", DRAFT)
    p("draft md5 before:", md_before)
    lines = read_lines(DRAFT)
    p("draft lines:", len(lines))
    os.makedirs(a.scratch, exist_ok=True)
    planted_path = os.path.join(a.scratch, "draft_planted.md")
    make_planted(lines, planted_path)
    p("planted copy:", planted_path, "md5", md5(planted_path))

    clean = run_all(DRAFT, True, "CLEAN DRAFT")
    planted = run_all(planted_path, False, "PLANTED COPY")

    p("\n" + "=" * 100)
    p("PLANTED COPY: hits that are new compared with the clean draft")
    p("=" * 100)
    for sec in SECTIONS:
        ck = Counter(k for k, d in clean["items"][sec])
        new = []
        for k, d in planted["items"][sec]:
            if ck[k] > 0:
                ck[k] -= 1
            else:
                new.append(d)
        for d in new:
            p("  NEW in %s: %s" % (sec, str(d)[:300]))

    p("\n" + "=" * 100)
    p("COUNTS PER SECTION: clean vs planted")
    p("=" * 100)
    p("%-6s %6s %8s %6s" % ("gate", "clean", "planted", "delta"))
    for sec in SECTIONS:
        c, pl = clean["counts"][sec], planted["counts"][sec]
        p("%-6s %6d %8d %6d" % (sec, c, pl, pl - c))
    p("(1.2a = 'x of y' counts, 1.2b = pass/fail sentences, 2.1 = citations without reference, 2.2a = uncited references,")
    p(" 2.2b = DOIs listed as text, no lookup made)")

    p("\nPLANT TABLE")
    all_fired = True
    toks = [t for _, t, _ in planted["1.1"][0]]
    p("  probe (informational, not in exit code): fake decimal 0.4137 in unmatched list: %s; fake small integer 37 in unmatched list: %s"
      % ("YES, fired" if "0.4137" in toks else "NO", "YES, fired" if "37" in toks else "NO (small integers match by coincidence: known limit of gate 1.1)"))
    for sec, anchor, add in PLANTS:
        if sec == "probe":
            continue
        d = planted["counts"][sec] - clean["counts"][sec]
        fired = d >= 1
        all_fired &= fired
        p("  plant %-45s section %-4s delta %+d  %s" % (repr(add.strip())[:45], sec, d, "FIRED" if fired else "DID NOT FIRE"))
    md_after = md5(DRAFT)
    p("\ndraft md5 after: ", md_after, "UNCHANGED" if md_after == md_before else "CHANGED (!)")
    if md_after != md_before:
        return 2
    code = 0 if all_fired else 1
    p("\nEXIT CODE %d: %s" % (code, {0: "ran, every plant fired", 1: "a plant did not fire",
                                       2: "could not run"}[code]))
    return code


if __name__ == "__main__":
    try:
        rc = main()
    except Exception:
        traceback.print_exc()
        print("EXIT CODE 2: could not run (exception)")
        rc = 2
    sys.exit(rc)
