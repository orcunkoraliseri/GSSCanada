#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""p9_figures_hotel_obs.py (2026-09-25): redraw the five Step-9 data figures (Figure_07..Figure_11) after the
2030 hotel recovery levels were switched to the observed 2023-2025 means (AB 0.597, QC 0.610) and the 36 affected
P10R cells were re-run. Uses the render_plain logic of p9_figures_plain.py (imported, not edited), which is the
logic that produced what is installed now.

Checks, in order, before anything is written to writing/figures or writing/submission/figures:
  C0  POSITIVE control: render_plain on the ARCHIVED pre-switch data
      (Leg3_4-split/_archive_pre_hotel_obs_2026-09-25/agg_P10R) reproduces the CURRENTLY INSTALLED PNG and PDF of
      all five figures byte for byte. Proves the renderer is the one that made the installed files and that the
      archive is the data they were drawn from.
  C1  SEEN-MOVING control: the same render on the NEW data (agg_P10R) must differ from the installed file for
      Figure_11 (the 2030 scenario figure, which reads the re-run cells). If it does not, the new data never
      reached the renderer. Figure_07 (2005-2022 only, no re-run cell) must stay byte-identical.
  D1  plain-label checks (p9_figures_plain.check_plain) pass on the five new figures.
Only if C0, C1 and D1 all hold does --install archive the current files into _archive_pre_hotel_obs_2026-09-25/
(md5 verified) in both folders and copy the new ones in.
Run: PYTHONIOENCODING=utf-8 py -3 p9_figures_hotel_obs.py [--install]
"""
from __future__ import annotations
import importlib.util
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("p9pl", os.path.join(HERE, "p9_figures_plain.py"))
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)

AGG_OLD = os.path.join(P.LEG3, "_archive_pre_hotel_obs_2026-09-25", "agg_P10R")
ARCH2 = "_archive_pre_hotel_obs_2026-09-25"
N = {"pass": 0, "fail": 0}


def rec(tag, ok, detail):
    N["pass" if ok else "fail"] += 1
    print(f"  [{'PASS' if ok else 'FAIL'}] {tag:3s} {detail}")


def render(agg, outdir):
    os.makedirs(outdir)
    s9 = P.load_s9()
    d, tabs = P.build_frames(s9, agg)
    return P.render_plain(s9, tabs, d, outdir, 600, True)


def keep_figs(agg):
    s9 = P.load_s9()
    d, tabs = P.build_frames(s9, agg)
    figs = {}

    def _k(fig, _o, fname):
        figs[fname] = fig
        return None

    P.fig_eui_nt(s9, tabs["eui"], "/unused", _k)
    P.fig_diurnal_pl(s9, d["diurnal"], "/unused", _k)
    P.fig_peakhour_nt(s9, tabs["ls"], "/unused", _k)
    P.fig_scenario_pl(s9, tabs["scen"], "/unused", _k)
    P.fig_longitudinal_pl(s9, tabs["lon"], "/unused", _k)
    return s9, figs


def main():
    install = "--install" in sys.argv
    tmp = tempfile.mkdtemp(prefix="p9hotelobs_")
    print(f"P9 figures after hotel_obs | temp {tmp}\n  old data {AGG_OLD}\n  new data {P.AGG_NEW}")
    assert os.path.isdir(AGG_OLD), AGG_OLD

    w_old = render(AGG_OLD, os.path.join(tmp, "old"))
    w_new = render(P.AGG_NEW, os.path.join(tmp, "new"))

    print("\nC0  positive control: old data -> currently installed files, byte for byte")
    for src, base in P.STEP9_FIGS.items():
        for ext in ("png", "pdf"):
            r = w_old[src] if ext == "png" else w_old[src][:-4] + ".pdf"
            for dd in (P.FIGS, P.SUBFIGS):
                cur = os.path.join(dd, f"{base}.{ext}")
                rec("C0", P.md5(r) == P.md5(cur), f"{os.path.relpath(cur, P.J3)}: {P.md5(r)[:8]} vs {P.md5(cur)[:8]}")

    print("\nC1  new data reaches the renderer (seen moving) and leaves the pre-2030 figure alone")
    moved = {}
    for src, base in P.STEP9_FIGS.items():
        moved[base] = P.md5(w_new[src]) != P.md5(os.path.join(P.FIGS, base + ".png"))
        print(f"    {base}: {'CHANGED' if moved[base] else 'identical'}")
    rec("C1", moved["Figure_11_scenario_4ch"], "Figure_11 (2030 scenarios) differs from the installed file")
    rec("C1", not moved["Figure_07_longitudinal_4ch"], "Figure_07 (2005-2022 only) is byte-identical")

    print("\nD1  plain-label checks on the new figures")
    s9, figs = keep_figs(P.AGG_NEW)
    for src, base in P.STEP9_FIGS.items():
        ht, hb, titles, flagged, kept = P.check_plain(figs[src], base, allow_ax_titles=True)
        rec("D1", not ht and not hb, f"{base}: no title, no code token or en/em dash ({flagged!r})")
        s9.plt.close(figs[src])

    print(f"\nCONTROLS: {N['pass']} PASS / {N['fail']} FAIL")
    if N["fail"] or not install:
        print("NOT INSTALLED: a control failed" if N["fail"] else "dry run: nothing installed (use --install)")
        shutil.rmtree(tmp, ignore_errors=True)
        return 1 if N["fail"] else 0

    print("\nINSTALL (archive, then md5 before -> after)")
    for src, base in P.STEP9_FIGS.items():
        if not moved[base]:
            print(f"  {base}: unchanged, not copied")
            continue
        for ext in ("png", "pdf"):
            new = w_new[src] if ext == "png" else w_new[src][:-4] + ".pdf"
            for dd in (P.FIGS, P.SUBFIGS):
                cur = os.path.join(dd, f"{base}.{ext}")
                arch = os.path.join(dd, ARCH2, f"{base}.{ext}")
                os.makedirs(os.path.dirname(arch), exist_ok=True)
                before = P.md5(cur)
                shutil.copyfile(cur, arch)
                assert os.path.getsize(arch) > 0 and P.md5(arch) == before, arch
                shutil.copyfile(new, cur)
                print(f"  {os.path.relpath(cur, P.J3)}  {before[:8]} -> {P.md5(cur)[:8]}")
    shutil.rmtree(tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
