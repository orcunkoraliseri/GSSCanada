#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
f5_figure_check.py -- the 3rdJ_schematics_implementation_plan.md Test method check,
in the f1/f2/f3/f4 idiom. Arms C1-C6, each provably able to fail, plus --falsify.

Run:  py -3 writing/implementation/f5_figure_check.py
      py -3 writing/implementation/f5_figure_check.py --falsify

C1  all eight expected output files (.pdf and .png) exist and are non-empty.
C2  every figure has a matching generator script, and RE-RUNNING that script (via a
    fresh subprocess) reproduces the same md5 as the file already on disk -- proves
    determinism live, not just "the file happens to be there".
C3  the string "4 heads" appears in no figure script except inside a comment that is
    itself forbidding it (the Figure 3 hazard: it must read "3 GSS heads + 1 non-GSS
    side-track").
C4  every string in a figure script's LABELS registry (the canonical, un-wrapped text
    handed to every box/diamond/text call in that script) appears, whitespace-
    normalized, as a substring of one of that figure's allowed source files (normally
    just its own prompt .md; figS01_shares.py is also allowed
    writing/tables/SI/Appendix_C_corrections.md, since a 2026-08-06 manager review found
    the prompt .md's own four-segment total is wrong -- see figS01_shares.py's module
    docstring). Scope note: this checks the LABELS registry each script declares, not a
    full bypass-proof static scan of every ax.text() call -- the same registry-plus-
    discipline idiom f4 uses for "every scanned file names a source".
C5  vacuity guard: FAIL if fewer than 8 figures were checked.
C6  DATA-FIGURE INTEGRITY (figS01_shares.py only, the one figure with real measured
    shares): (a) the five stacked segments per tower sum to 100% of OCCUPIABLE area
    within 0.5 pp: (b) occupiable_m2 + service_mep_pct-of-gross reconstructs 100% of
    GROSS within 0.5 pp, proving the bar's primary total is denominated in occupiable
    area, not gross, and that no segment (such as residential-common) was dropped. This
    is the arm that would have caught the manager's two 2026-08-06 findings (a missing
    fifth segment, and a bar total labelled with the wrong denominator) had it existed
    before them.

--falsify: for one real figure, (a) appends a synthetic 9th label to its LABELS list
that exists nowhere in any allowed source, confirming C4 catches it; (b) injects a live
(non-comment) "4 heads" code line into a copy of its source, confirming C3 catches it;
(c) corrupts figS01's SuperTall segment shares (drops residential-common) and confirms
C6 catches the resulting under-100% sum. Neither mutates the real files on disk.
"""
import ast
import hashlib
import importlib.util
import io
import os
import re
import subprocess
import sys

IMPL = os.path.dirname(os.path.abspath(__file__))            # .../writing/implementation
WRITING = os.path.dirname(IMPL)                               # .../writing
FIG = os.path.join(WRITING, "figures")
FIG_SI = os.path.join(FIG, "SI")
TABLES_SI = os.path.join(WRITING, "tables", "SI")
APPENDIX_C = os.path.join(TABLES_SI, "Appendix_C_corrections.md")

FOUR_HEADS = "4 heads"
FORBID_WORDS = re.compile(r"(must not|never|forbid|reject|hazard|do not|not violate|explicitly "
                           r"rejected)", re.I)

# (script path, prompt .md path, output base path without extension, outdir, extra C4 sources)
FIGURES = [
    ("fig01_pipeline.py", "Figure_01_pipeline_4split.md", "Figure_01_pipeline_4split", FIG, []),
    ("fig02_roadmap.py", "Figure_02_three_leg_roadmap.md", "Figure_02_three_leg_roadmap", FIG, []),
    ("fig03_transformer.py", "Figure_03_three_head_transformer.md", "Figure_03_three_head_transformer", FIG, []),
    ("fig04_exclusivity.py", "Figure_04_exclusivity_projection.md", "Figure_04_exclusivity_projection", FIG, []),
    ("fig05_tag2dispatch.py", "Figure_05_tag2_dispatch.md", "Figure_05_tag2_dispatch", FIG, []),
    ("fig06_hotel.py", "Figure_06_hotel_sidetrack.md", "Figure_06_hotel_sidetrack", FIG, []),
    ("figS01_shares.py", "Figure_S01_occupiable_shares.md", "Figure_S01_occupiable_shares", FIG_SI, [APPENDIX_C]),
    ("figS02_levers.py", "Figure_S02_scenario_levers.md", "Figure_S02_scenario_levers", FIG_SI, []),
]


def md5_of(path):
    h = hashlib.md5()
    with io.open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def norm_ws(s):
    return re.sub(r"\s+", " ", s).strip()


def read(p):
    with io.open(p, encoding="utf-8") as fh:
        return fh.read()


def extract_labels(script_text):
    """Parse the module-level `LABELS = [...]` assignment. Elements may be string
    literals directly, or bare Name references to an earlier module-level string
    constant (e.g. `LABELS = [..., FOOTNOTE, CAPTION]` where FOOTNOTE/CAPTION are
    assigned string literals higher up the file) -- resolved via a first pass over
    simple `NAME = "<string literal>"` assignments. Returns (labels, error)."""
    tree = ast.parse(script_text)
    consts = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            try:
                val = ast.literal_eval(node.value)
            except Exception:
                continue
            if isinstance(val, str):
                consts[node.targets[0].id] = val

    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name) and node.targets[0].id == "LABELS":
            if not isinstance(node.value, (ast.List, ast.Tuple)):
                return None, "LABELS is not a list/tuple literal"
            labels = []
            for elt in node.value.elts:
                try:
                    labels.append(ast.literal_eval(elt))
                    continue
                except Exception:
                    pass
                if isinstance(elt, ast.Name) and elt.id in consts:
                    labels.append(consts[elt.id])
                else:
                    return None, "LABELS element is not a string literal or a known module-level string constant: %s" \
                                  % ast.dump(elt)[:80]
            return labels, None
    return None, "no module-level LABELS = [...] found"


def check_c1():
    bad = []
    n = 0
    for script, md, base, outdir, extra in FIGURES:
        for ext in (".pdf", ".png"):
            n += 1
            p = os.path.join(outdir, base + ext)
            if not os.path.exists(p):
                bad.append("%s: MISSING" % os.path.relpath(p, WRITING))
            elif os.path.getsize(p) == 0:
                bad.append("%s: zero bytes" % os.path.relpath(p, WRITING))
    return (not bad, bad, n)


def check_c2():
    bad = []
    for script, md, base, outdir, extra in FIGURES:
        script_path = os.path.join(outdir, script)
        png_path = os.path.join(outdir, base + ".png")
        if not os.path.exists(script_path):
            bad.append("%s: generator script missing" % script)
            continue
        if not os.path.exists(png_path):
            bad.append("%s: no existing .png to compare against" % base)
            continue
        before = md5_of(png_path)
        proc = subprocess.run(["py", "-3", script_path], cwd=outdir, capture_output=True, text=True)
        if proc.returncode != 0:
            bad.append("%s: re-run failed (exit %d): %s" % (script, proc.returncode, proc.stderr[-300:]))
            continue
        after = md5_of(png_path)
        if before != after:
            bad.append("%s: md5 changed on re-run (%s -> %s) -- NOT deterministic" % (script, before, after))
    return (not bad, bad)


def scan_four_heads(script_text, label):
    """Return list of violation strings: '4 heads' present outside a forbidding comment."""
    bad = []
    for i, line in enumerate(script_text.splitlines(), start=1):
        if FOUR_HEADS in line:
            stripped = line.strip()
            is_comment = stripped.startswith("#")
            if is_comment and FORBID_WORDS.search(line):
                continue  # allowed: a comment forbidding the phrase
            bad.append("%s line %d: %r" % (label, i, line.strip()[:100]))
    return bad


def check_c3():
    bad = []
    for script, md, base, outdir, extra in FIGURES:
        script_path = os.path.join(outdir, script)
        if not os.path.exists(script_path):
            continue
        bad.extend(scan_four_heads(read(script_path), script))
    return (not bad, bad)


def check_c4():
    bad = []
    for script, md, base, outdir, extra in FIGURES:
        script_path = os.path.join(outdir, script)
        md_path = os.path.join(outdir, md)
        if not os.path.exists(script_path) or not os.path.exists(md_path):
            bad.append("%s: script or prompt .md missing" % script)
            continue
        labels, err = extract_labels(read(script_path))
        if err:
            bad.append("%s: %s" % (script, err))
            continue
        sources = [md_path] + list(extra)
        combined = norm_ws("\n".join(read(p) for p in sources if os.path.exists(p)))
        for lab in labels:
            if norm_ws(lab) not in combined:
                bad.append("%s: label not found in %s: %r"
                           % (script, ", ".join(os.path.basename(p) for p in sources), lab[:90]))
    return (not bad, bad)


def check_c5(n_checked):
    ok = n_checked >= 8
    return (ok, [] if ok else ["only %d figure(s) checked -- C1 to C4 would pass vacuously" % n_checked])


def load_module(mod_name, mod_dir):
    path = os.path.join(mod_dir, mod_name + ".py")
    spec = importlib.util.spec_from_file_location(mod_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check_segment_sums(channel_order, towers, tol=0.5):
    """(a) five segments sum to ~100% of occupiable, per tower."""
    bad = []
    for name, d in towers.items():
        s = sum(d[ch] for ch in channel_order)
        if abs(s - 100.0) > tol:
            bad.append("segments for %s sum to %.2f%%, not ~100%% (tol %.1f pp)" % (name, s, tol))
    return bad


def check_denominator_closes(numeric, tol=0.5):
    """(b) occupiable_m2 as a % of gross_m2, plus service_mep_pct, closes to ~100% of
    gross -- proves OCCUPIABLE and GROSS are the two denominators, not the same number
    restated, and that the bar's primary total (occupiable) is the one the segments
    actually divide."""
    bad = []
    for name, d in numeric.items():
        occ_pct_of_gross = 100.0 * d["occupiable_m2"] / d["gross_m2"]
        total = occ_pct_of_gross + d["service_mep_pct"]
        if abs(total - 100.0) > tol:
            bad.append("%s: occupiable-of-gross (%.2f%%) + Service/MEP (%.2f%%) = %.2f%%, "
                       "not ~100%% (tol %.1f pp)" % (name, occ_pct_of_gross, d["service_mep_pct"], total, tol))
    return bad


def check_c6():
    """Data-figure integrity, figS01_shares.py only. See module docstring."""
    mod = load_module("figS01_shares", FIG_SI)
    towers = {"SuperTall": mod.SUPERTALL, "Tall": mod.TALL}
    bad = check_segment_sums(mod.CHANNEL_ORDER, towers)
    bad += check_denominator_closes(mod.NUMERIC)
    return (not bad, bad)


TABLE_06 = os.path.join(WRITING, "tables", "Table_06_leg2_leg3_delta.md")

# A figure may only call an artefact "bit-identical" for a step Table 6 grades as an
# affirmative Yes. Today Step 7 alone qualifies, and only for the base prototype geometry.
BIT_IDENTICAL = re.compile(r"bit-identical|byte-identical", re.I)
STEP_REF = re.compile(r"Step\s*(\d)", re.I)
# Narrow on purpose. It must not swallow the defect it exists to catch, which read
# "residential + office paths bit-identical" and contained no negation at all.
NEGATED = re.compile(r"\bnot\b[^.;]{0,24}(bit-identical|byte-identical)|"
                     r"(bit-identical|byte-identical)[^.;]{0,24}\bnot\s+verified\b", re.I)


def table06_verdicts():
    """Read Table 6's evidence column from disk. Returns {step_number: affirmative_bool}.

    Deliberately parsed from the table itself rather than from any list kept in this
    file: the whole point of C7 is that the figures and the table cannot drift apart,
    and a hard-coded copy here would drift with them."""
    verdicts = {}
    for ln in read(TABLE_06).split("\n"):
        if not ln.startswith("| Step"):
            continue
        cells = [c.strip() for c in ln.split("|")]
        if len(cells) < 5:
            continue
        m = STEP_REF.match(cells[1])
        if not m:
            continue
        cell = cells[4].lstrip("*").strip()
        verdicts[int(m.group(1))] = cell.lower().startswith("yes")
    return verdicts


def check_c7(label_override=None):
    """CROSS-ARTEFACT CONSISTENCY. No figure LABELS entry may assert bit-identity for a
    step whose Table 6 evidence cell is not an affirmative Yes.

    This exists because on 2026-08-06 Figures 1 and 2 both stated "residential + office
    paths bit-identical" for Step 3, while Table 6 graded that same claim 'check source'
    and said in its own reason column that the prose assertion behind it is not
    acceptable evidence. Every other arm passed: C4 confirmed the label came from its
    prompt file, and the prompt file was itself the thing that was wrong."""
    verdicts = table06_verdicts()
    if not verdicts:
        return (False, ["Table 6 parsed to zero step rows -- C7 cannot run (do not read this as a pass)"])
    bad = []
    for script, md, base, outdir, extra in FIGURES:
        if label_override and label_override[0] == script:
            labels = label_override[1]
        else:
            labels, err = extract_labels(read(os.path.join(outdir, script)))
            if err:
                bad.append("%s: %s" % (script, err))
                continue
        for lab in labels:
            # Evaluate clause by clause. A caption may legitimately affirm bit-identity for
            # one step and deny it for another in the same sentence, which is exactly what
            # the corrected Figure 2 connector now does; scoring the whole string at once
            # would fail that correct caption and force the arm to be weakened.
            for clause in re.split(r";", lab):
                if not BIT_IDENTICAL.search(clause):
                    continue
                if NEGATED.search(clause):
                    continue          # a denial is not an assertion
                steps = [int(s) for s in STEP_REF.findall(clause)]
                if not steps:
                    bad.append("%s: asserts bit-identity but names no step, so it cannot be "
                               "checked against Table 6: %r" % (script, clause.strip()[:80]))
                    continue
                for st in steps:
                    if st not in verdicts:
                        bad.append("%s: names Step %d, absent from Table 6" % (script, st))
                    elif not verdicts[st]:
                        bad.append("%s: asserts bit-identity for Step %d, which Table 6 grades "
                                   "NOT affirmative: %r" % (script, st, clause.strip()[:80]))
    return (not bad, bad)


def run_falsify():
    print("  FALSIFY MODE\n")
    results = []

    # (a) C4 falsifier: append a synthetic, unregistered label to a real figure's LABELS
    script, md, base, outdir, extra = FIGURES[0]
    labels, err = extract_labels(read(os.path.join(outdir, script)))
    fake_labels = list(labels) + ["ZZZ synthetic ninth label never present in any prompt .md file"]
    sources = [os.path.join(outdir, md)] + list(extra)
    combined = norm_ws("\n".join(read(p) for p in sources if os.path.exists(p)))
    c4_bad = [lab for lab in fake_labels if norm_ws(lab) not in combined]
    c4_ok = not c4_bad
    print("  [%s] C4 falsifier (%s + 1 synthetic label): %s"
          % ("FAIL" if not c4_ok else "STILL PASSED", script,
             ("caught: %r" % c4_bad[0][:80]) if c4_bad else "NOT CAUGHT -- arm is broken"))
    results.append(("C4", c4_ok))

    # (b) C3 falsifier: inject a live "4 heads" code line into an in-memory copy of a script
    script3 = "fig03_transformer.py"
    real_text = read(os.path.join(FIG, script3))
    injected = real_text + "\nCAPTION_TEXT_NEVER_ACTUALLY_USED = \"4 heads\"  # not a comment, this is live code\n"
    c3_bad = scan_four_heads(injected, script3 + " (falsified copy)")
    c3_ok = not c3_bad
    print("  [%s] C3 falsifier (%s + 1 live '4 heads' line): %s"
          % ("FAIL" if not c3_ok else "STILL PASSED", script3,
             ("caught: %s" % c3_bad[0]) if c3_bad else "NOT CAUGHT -- arm is broken"))
    results.append(("C3", c3_ok))

    # (c) C6 falsifier: corrupt figS01's SuperTall shares in memory (drop residential-common,
    # reproducing exactly the manager's "missing fifth segment" defect) and confirm the
    # segment-sum check catches the resulting under-100% total.
    mod = load_module("figS01_shares", FIG_SI)
    corrupted_order = [c for c in mod.CHANNEL_ORDER if c != "residential_common"]
    corrupted_data = {k: v for k, v in mod.SUPERTALL.items() if k != "residential_common"}
    s = sum(corrupted_data[ch] for ch in corrupted_order)
    c6_bad = []
    if abs(s - 100.0) > 0.5:
        c6_bad = ["segments for SuperTall (residential-common dropped) sum to %.2f%%, not ~100%%" % s]
    c6_ok = not c6_bad
    print("  [%s] C6 falsifier (figS01 SuperTall, residential-common dropped): %s"
          % ("FAIL" if not c6_ok else "STILL PASSED", (c6_bad[0] if c6_bad else "NOT CAUGHT -- arm is broken")))
    results.append(("C6", c6_ok))

    # (d) C7 falsifier: replay the real 2026-08-06 defect. Re-inject the exact label
    # Figures 1 and 2 actually carried, and confirm C7 rejects it against Table 6.
    fig01 = FIGURES[0][0]
    defect = ["one tiler list entry appends AT_RETAIL; residential + office paths bit-identical"]
    c7_ok, c7_bad = check_c7(label_override=(fig01, defect))
    print("  [%s] C7a falsifier (%s + the real 2026-08-06 Step-3 label): %s"
          % ("FAIL" if not c7_ok else "STILL PASSED", fig01,
             ("caught: " + c7_bad[0]) if c7_bad else "NOT CAUGHT -- arm is broken"))
    results.append(("C7a", c7_ok))

    # (e) C7's OTHER branch. The real defect above named no step, so it was rejected by
    # the unlocatable-claim fallback and left the table-lookup branch unexercised. An arm
    # with two paths needs two falsifiers, or half of it is only assumed to work.
    located = ["Step 3 merge and tiling: residential + office paths bit-identical"]
    c7b_ok, c7b_bad = check_c7(label_override=(fig01, located))
    print("  [%s] C7b falsifier (%s + a Step-3 claim that DOES name its step): %s"
          % ("FAIL" if not c7b_ok else "STILL PASSED", fig01,
             ("caught: " + c7b_bad[0]) if c7b_bad else "NOT CAUGHT -- arm is broken"))
    results.append(("C7b", c7b_ok))

    # (f) C7 positive control. An arm that rejects everything is not a check. The one
    # claim Table 6 does license must survive.
    allowed = ["the Step 7 base tower geometry is md5-verified byte-identical (4 IDF files)"]
    c7c_ok, _ = check_c7(label_override=(fig01, allowed))
    print("  [%s] C7c control (a Step-7 claim Table 6 DOES license): %s"
          % ("PASS" if c7c_ok else "FAIL",
             "correctly allowed" if c7c_ok else "REJECTED -- C7 rejects everything, it is not a check"))

    print()
    still_passing = [cid for cid, ok in results if ok]
    for cid, ok in results:
        print("  falsifier: %s %s" % (cid, "failed as required -- it has teeth" if not ok
                                       else "STILL PASSED -- this arm is broken"))
    return 1 if still_passing else 0


def main():
    falsify = "--falsify" in sys.argv
    print("f5_figure_check.py -- 3J schematics check\n")

    if falsify:
        return run_falsify()

    c1_ok, c1_bad, n_files = check_c1()
    c2_ok, c2_bad = check_c2()
    c3_ok, c3_bad = check_c3()
    c4_ok, c4_bad = check_c4()
    c5_ok, c5_bad = check_c5(len(FIGURES))
    c6_ok, c6_bad = check_c6()
    c7_ok, c7_bad = check_c7()

    results = [
        ("C1", c1_ok, "all eight expected output files (.pdf + .png) exist and are non-empty "
                       "(%d files checked)" % n_files, c1_bad),
        ("C2", c2_ok, "every figure's script re-runs to the same md5 (determinism)", c2_bad),
        ("C3", c3_ok, "the string '4 heads' appears in no script outside a forbidding comment", c3_bad),
        ("C4", c4_ok, "every LABELS entry is a substring of an allowed source file", c4_bad),
        ("C5", c5_ok, "vacuity guard: 8 figures were checked", c5_bad),
        ("C6", c6_ok, "data-figure integrity: figS01 segments sum to ~100% of occupiable, and "
                       "occupiable + Service/MEP close to ~100% of gross", c6_bad),
        ("C7", c7_ok, "cross-artefact: no figure asserts bit-identity for a step Table 6 "
                       "grades as anything other than an affirmative Yes (%d step rows read)"
                       % len(table06_verdicts()), c7_bad),
    ]

    npass = 0
    for cid, ok, desc, detail in results:
        print("  [%s] %s  %s" % ("PASS" if ok else "FAIL", cid, desc))
        for d in detail[:20]:
            print("        %s" % d)
        if len(detail) > 20:
            print("        ... and %d more" % (len(detail) - 20))
        npass += 1 if ok else 0

    print("\n  %d PASS / %d FAIL" % (npass, len(results) - npass))
    return 0 if npass == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
