#!/usr/bin/env python3
"""V5-F6 -- prove the 300 dpi result figures show the SAME numbers as the shipped 140 dpi ones.

WHY THIS EXISTS. Figures 7 to 11 are the manuscript's only data figures and the shipped copies are
140 dpi, below Elsevier's artwork minimum. Re-rendering them is easy. Proving that the re-render is
the same figure and not a different one is the whole problem, and it is not a problem you can eyeball
away: a plot of the wrong campaign arm looks exactly as convincing as a plot of the right one.

THE CHECK THAT ACTUALLY DECIDES IT, and why the obvious one is not enough.

  The obvious check is to downsample the new 300 dpi PNG to the old pixel size and compare. That
  check was written first and it PASSED on figures built from the WRONG aggregate directory: for
  every figure the difference against its own original was the smallest of the five, which reads
  like a match. It is not. Re-rendering the wrong data still produces the same layout, the same
  colours and the same axis labels, so most of the pixels agree no matter what the bars say.

  C1 below is the check that decides it. Re-render at the ORIGINAL dpi and require the bytes to be
  identical to the shipped file. That isolates the pipeline from the resolution: if the same code,
  reading the same inputs, reproduces the shipped PNG exactly, then the only thing a dpi change can
  alter is the number of pixels. If it does not reproduce, nothing about the 300 dpi version can be
  trusted, whatever a pixel-difference score says.

  🔴 C1 was seen failing, on a real defect, before it was trusted. The Step-9 script's own
  `DEFAULT_AGG` points at `outputs_step8/agg`, which is the SUPERSEDED arm; the canonical
  deliverable was built from `outputs_step8/agg_deliverable`. On the default, four of five figures
  differed from the shipped bytes and the rebuilt tables differed in EUI, peak hour, and 16
  `verdict_asmodelled` cells. A default inside a pipeline script is not provenance.

FIVE CHECKS:
  C1  re-rendering at the ORIGINAL dpi reproduces every shipped figure byte for byte.
  C2  a 300 dpi copy exists for every shipped figure, and its embedded dpi metadata says so.
  C3  the pixel dimensions scaled by the dpi ratio, so the figure is larger in pixels and unchanged
      in inches. A figure that gained pixels by being redrawn at a different size is not the same
      figure on the page.
  C4  the two arms are actually distinguishable, so C1 CAN fail: rendering from the superseded
      aggregate directory must NOT reproduce the shipped bytes. A check that cannot fail is a
      comment.
  C5  the manuscript copy under writing/figures/ matches the 300 dpi source byte for byte, so the
      thing verified here is the thing that ships.

    py -3 f6_figure_replot_equivalence.py [--falsify]

--falsify inverts C1: it renders from the superseded arm and reports whether C1 still catches it.
"""
import argparse
import hashlib
import importlib.util
import io
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))            # 3J_docs_occ_nTemp/
STEP9_PY = os.path.join(ROOT, "Leg3_4-split", "Step9_docs", "3rdJ_09_activityDrivenLoads_4split.py")
STEP8 = os.path.join(ROOT, "Leg3_4-split", "Step8_docs", "outputs_step8")
AGG_CANON = os.path.join(STEP8, "agg_deliverable")
AGG_SUPERSEDED = os.path.join(STEP8, "agg")
DELIV = os.path.join(ROOT, "Leg3_4-split", "Step9_docs", "outputs_step9_deliverable")
SHIPPED = os.path.join(DELIV, "figures")
HIRES = os.path.join(DELIV, "figures_hires")
WRITING_FIGS = os.path.join(ROOT, "writing", "figures")

ORIGINAL_DPI = 140
TARGET_DPI = 600            # combination art minimum is 500 (RV10 item 7c); 600 clears it

# the manuscript name each Step-9 figure is copied to
MANUSCRIPT = {"fig_longitudinal_4ch.png": "Figure_07_longitudinal_4ch.png",
              "fig_eui_4ch.png": "Figure_08_eui_4ch.png",
              "fig_diurnal_4ch.png": "Figure_09_diurnal_4ch.png",
              "fig_peakhour_4ch.png": "Figure_10_peakhour_4ch.png",
              "fig_scenario_4ch.png": "Figure_11_scenario_4ch.png"}

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
_N = {"pass": 0, "fail": 0}


def rec(tag, ok, detail):
    _N["pass" if ok else "fail"] += 1
    print("  [%s] %-3s %s" % ("PASS" if ok else "FAIL", tag, detail))


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def render(agg_dir, dpi, outdir):
    """Render the five Step-9 figures with the Step-9 module's own plotting code."""
    spec = importlib.util.spec_from_file_location("step9_4split", STEP9_PY)
    s9 = importlib.util.module_from_spec(spec)
    sys.modules["step9_4split"] = s9
    spec.loader.exec_module(s9)

    written = {}

    def _save(fig, _outdir, fname):
        p = os.path.join(outdir, fname)
        fig.savefig(p, dpi=dpi, bbox_inches="tight")
        s9.plt.close(fig)
        written[fname] = p
        return p

    s9._save = _save
    d = s9.load_agg(agg_dir)
    eui = s9.build_eui(d["annual"], d["meta"])
    s9.SCEN_OF.update(dict(zip(d["meta"]["cell_tag"], d["meta"]["scenario"])))
    ls = s9.build_loadshape(d["peak"], d["diurnal"])
    scen = s9.build_scenario(eui, d["annual"])
    lon = s9.build_longitudinal(eui, ls)
    s9.fig_eui(eui, outdir)
    s9.fig_diurnal(d["diurnal"], outdir)
    s9.fig_peakhour(ls, outdir)
    s9.fig_scenario(scen, outdir)
    s9.fig_longitudinal(lon, outdir)
    return written


def main(falsify):
    from PIL import Image

    arm = AGG_SUPERSEDED if falsify else AGG_CANON
    print("V5-F6 -- Step-9 figure replot equivalence%s" % ("   FALSIFY MODE" if falsify else ""))
    print("  rendering from %s" % os.path.relpath(arm, ROOT).replace("\\", "/"))
    print("  shipped figures in %s\n" % os.path.relpath(SHIPPED, ROOT).replace("\\", "/"))

    tmp = tempfile.mkdtemp(prefix="f6_")
    try:
        repro = render(arm, ORIGINAL_DPI, tmp)

        # ---- C1 ------------------------------------------------- byte-identical reproduction
        bad = []
        for fname in sorted(MANUSCRIPT):
            ship = os.path.join(SHIPPED, fname)
            if fname not in repro or not os.path.isfile(ship):
                bad.append((fname, "MISSING"))
            elif md5(repro[fname]) != md5(ship):
                bad.append((fname, "%s vs shipped %s" % (md5(repro[fname])[:8], md5(ship)[:8])))
        rec("C1", not bad,
            "all %d figure(s) reproduce byte for byte at %d dpi" % (len(MANUSCRIPT), ORIGINAL_DPI)
            if not bad else "%d figure(s) do NOT reproduce -- the 300 dpi copies cannot be trusted:"
            % len(bad))
        for fname, why in bad:
            print("        %s  %s" % (fname, why))

        # ---- C4 ---------------------------------------------------- can C1 fail at all
        # Always the SUPERSEDED arm, in both modes. The question C4 answers is fixed -- "would C1
        # notice the wrong input?" -- and it must not change meaning depending on which arm the run
        # happens to be testing. (Written the other way first: in --falsify it then rendered the
        # CANONICAL arm, found all five matching, and reported FAIL for the one situation that is
        # correct by construction.)
        tmp2 = tempfile.mkdtemp(prefix="f6_alt_")
        try:
            alt = render(AGG_SUPERSEDED, ORIGINAL_DPI, tmp2)
            collisions = [f for f in MANUSCRIPT
                          if f in alt and os.path.isfile(os.path.join(SHIPPED, f))
                          and md5(alt[f]) == md5(os.path.join(SHIPPED, f))]
        finally:
            shutil.rmtree(tmp2, ignore_errors=True)
        rec("C4", len(collisions) < len(MANUSCRIPT),
            "%d of %d figure(s) differ between the canonical and superseded aggregate arms, "
            "so C1 can fail" % (len(MANUSCRIPT) - len(collisions), len(MANUSCRIPT)))
        if collisions:
            print("        identical in both arms, no signal here: %s" % ", ".join(sorted(collisions)))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ---- C2 ------------------------------------------------------------ hi-res exists, dpi tagged
    missing, wrongdpi = [], []
    for fname in sorted(MANUSCRIPT):
        p = os.path.join(HIRES, fname)
        if not os.path.isfile(p):
            missing.append(fname)
            continue
        d = Image.open(p).info.get("dpi", (0, 0))[0]
        if round(d) < TARGET_DPI:
            wrongdpi.append((fname, d))
    rec("C2", not missing and not wrongdpi,
        "%d hi-res figure(s) present, all tagged >= %d dpi" % (len(MANUSCRIPT), TARGET_DPI)
        if not missing and not wrongdpi
        else "missing: %s; under-tagged: %s" % (missing or "none", wrongdpi or "none"))

    # ---- C3 ------------------------------------------------------------ same inches, more pixels
    ratio = TARGET_DPI / float(ORIGINAL_DPI)
    off = []
    for fname in sorted(MANUSCRIPT):
        a, b = os.path.join(SHIPPED, fname), os.path.join(HIRES, fname)
        if not (os.path.isfile(a) and os.path.isfile(b)):
            continue
        (w0, h0), (w1, h1) = Image.open(a).size, Image.open(b).size
        # `bbox_inches="tight"` measures the ink bounding box and rounds it to whole pixels
        # independently at each dpi, so a few pixels of drift is arithmetic, not a layout change.
        # The bound is relative and sub-percent: changing figsize or a font size moves the
        # dimensions by percent-level amounts, which this still catches.
        tol_w, tol_h = max(4, 0.005 * w0 * ratio), max(4, 0.005 * h0 * ratio)
        if abs(w1 - w0 * ratio) > tol_w or abs(h1 - h0 * ratio) > tol_h:
            off.append((fname, "%dx%d -> %dx%d, expected ~%dx%d"
                        % (w0, h0, w1, h1, round(w0 * ratio), round(h0 * ratio))))
    rec("C3", not off,
        "every figure scaled by exactly %.4fx in both axes, so its printed size is unchanged" % ratio
        if not off else "%d figure(s) changed physical size, not just resolution:" % len(off))
    for fname, why in off:
        print("        %s  %s" % (fname, why))

    # ---- C5 ------------------------------------------------------------ what ships is what passed
    drift = []
    for src, dst in sorted(MANUSCRIPT.items()):
        a, b = os.path.join(HIRES, src), os.path.join(WRITING_FIGS, dst)
        if not os.path.isfile(b):
            drift.append((dst, "not in writing/figures/"))
        elif not os.path.isfile(a):
            drift.append((dst, "no hi-res source"))
        elif md5(a) != md5(b):
            drift.append((dst, "source %s vs manuscript %s" % (md5(a)[:8], md5(b)[:8])))
    rec("C5", not drift,
        "every manuscript figure is byte-identical to the verified hi-res source"
        if not drift else "%d manuscript figure(s) are not the file this check verified:" % len(drift))
    for dst, why in drift:
        print("        %s  %s" % (dst, why))

    print("\n  %d PASS / %d FAIL" % (_N["pass"], _N["fail"]))
    if falsify:
        print("  FALSIFY MODE: C1 is EXPECTED to fail above. If it passed, C1 is not checking "
              "what it claims to.")
    return 0 if _N["fail"] == 0 else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--falsify", action="store_true",
                    help="render from the SUPERSEDED aggregate arm; C1 must fail")
    sys.exit(main(ap.parse_args().falsify))
