#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P9 second pass (2026-09-25): regenerate the data figures from the P10R arm, with controls.

Figures (manuscript name -> source):
  Figure_07_longitudinal_4ch, Figure_08_eui_4ch, Figure_09_diurnal_4ch (SI S6), Figure_10_peakhour_4ch (SI S7),
  Figure_11_scenario_4ch: Step-9 plotting code (Leg3_4-split/Step9_docs/3rdJ_09_activityDrivenLoads_4split.py),
  rendered exactly as improvements/v5/f6_figure_replot_equivalence.py does (600 dpi, bbox tight), from an agg dir.
  fig_presence_by_channel, fig_codeschedule_vs_survey: writing/figures/<name>.py from the P3 figure data
  (frozen arm: writing/figures/*.csv; P10R: writing/figures/_P10R_figdata/*.csv).
Schematics (Figures 1 to 4 of the paper, graphical abstract, S1 to S5) are not touched.

Controls, all before anything is written to writing/:
  P1  the frozen arm, rendered with the same code, reproduces every current PNG byte for byte (and the PDF where
      the PDF was made by the same code);
  P2  the P10R arm rendered at 140 dpi reproduces the Step-9 P10R run's own figures (outputs_step9_P10R/figures);
  P3  Step-9 tables rebuilt from agg_P10R equal outputs_step9_P10R/*.csv (what the figure draws = what 03 reads);
  N1  the superseded agg arm does NOT reproduce the current PNGs; N2 the P10R render differs from the frozen one;
  S   figure data vs 03_Results Tables 3 and 4 (already P10R): spot checks must match; wrong-definition
      reads (wrong hours, bundle for single lever, frozen data, wrong scenario, wrong basis) must NOT match.
Only if every control passes: new PNG/PDF are copied to writing/figures/ and (Step-9 figures) writing/submission/figures/.
md5 before/after is printed. Read only on agg_* and outputs_step9_*; never writes there.
Run: PYTHONIOENCODING=utf-8 py -3 p9_figures.py [--install]
"""
from __future__ import annotations

import hashlib
import importlib.util
import os
import re
import shutil
import sys
import tempfile

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
J3 = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
LEG3 = os.path.join(J3, "Leg3_4-split")
STEP9_PY = os.path.join(LEG3, "Step9_docs", "3rdJ_09_activityDrivenLoads_4split.py")
STEP8 = os.path.join(LEG3, "Step8_docs", "outputs_step8")
AGG = {"old": os.path.join(STEP8, "agg_deliverable"), "new": os.path.join(STEP8, "agg_P10R"),
       "superseded": os.path.join(STEP8, "agg")}
S9NEW = os.path.join(LEG3, "Step9_docs", "outputs_step9_P10R")
FIGS = os.path.join(J3, "writing", "figures")
SUBFIGS = os.path.join(J3, "writing", "submission", "figures")
ARCH = "_archive_pre_P9_2026-09-25"
FIGDATA = {"old": FIGS, "new": os.path.join(FIGS, "_P10R_figdata")}
RESULTS = os.path.join(J3, "writing", "chapters_v2", "03_Results.md")
STEP9_FIGS = {"fig_longitudinal_4ch.png": "Figure_07_longitudinal_4ch",
              "fig_eui_4ch.png": "Figure_08_eui_4ch",
              "fig_diurnal_4ch.png": "Figure_09_diurnal_4ch",
              "fig_peakhour_4ch.png": "Figure_10_peakhour_4ch",
              "fig_scenario_4ch.png": "Figure_11_scenario_4ch"}
P3_FIGS = {"fig_presence_by_channel": ["fig_presence_by_channel_data.csv"],
           "fig_codeschedule_vs_survey": ["fig_codeschedule_vs_survey_profiles.csv", "fig_codeschedule_vs_survey_metrics.csv"]}
N = {"pass": 0, "fail": 0}


def rec(tag, ok, detail):
    N["pass" if ok else "fail"] += 1
    print(f"  [{'PASS' if ok else 'FAIL'}] {tag:4s} {detail}")


def md5(p):
    with open(p, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


# ------------------------------------------------------------------------------------------------ Step-9 figures
def load_s9():
    spec = importlib.util.spec_from_file_location("step9_4split_p9", STEP9_PY)
    s9 = importlib.util.module_from_spec(spec)
    sys.modules["step9_4split_p9"] = s9
    spec.loader.exec_module(s9)
    return s9


def render_s9(agg_dir, dpi, outdir, pdf=False):
    """f6_figure_replot_equivalence.render, plus an optional PDF of the same figure object."""
    s9 = load_s9()
    written = {}

    def _save(fig, _outdir, fname):
        p = os.path.join(outdir, fname)
        fig.savefig(p, dpi=dpi, bbox_inches="tight")
        if pdf:
            fig.savefig(p[:-4] + ".pdf", bbox_inches="tight", metadata={"CreationDate": None, "ModDate": None})
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
    return written, dict(eui=eui, ls=ls, scen=scen, lon=lon)


# ------------------------------------------------------------------------------------------------ P3 figures
def render_p3(name, data_dir, outdir):
    spec = importlib.util.spec_from_file_location(f"{name}_p9", os.path.join(FIGS, name + ".py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    out = os.path.join(outdir, name)
    m.OUT = out
    if name == "fig_presence_by_channel":
        m.DATA = os.path.join(data_dir, "fig_presence_by_channel_data.csv")
    else:
        m.PROF = os.path.join(data_dir, "fig_codeschedule_vs_survey_profiles.csv")
        m.MET = os.path.join(data_dir, "fig_codeschedule_vs_survey_metrics.csv")
    m.main()
    return {"png": out + ".png", "pdf": out + ".pdf"}


# ------------------------------------------------------------------------------------------------ spot checks
def circ(w):
    w = np.asarray(w, float)
    a = 2 * np.pi * np.arange(24) / 24
    m = np.arctan2((w * np.sin(a)).sum(), (w * np.cos(a)).sum())
    return float((m % (2 * np.pi)) / (2 * np.pi) * 24)


def mid_night(p, day=range(11, 15), night=(0, 1, 2, 3, 4, 22, 23)):
    p = np.asarray(p, float)
    return p[list(day)].mean() / p[list(night)].mean()


def t3(channel, measure):
    """Value printed in 03_Results Table 3, survey-based 2022 column (or code column)."""
    with open(RESULTS, encoding="utf-8") as fh:
        for line in fh:
            c = [x.strip() for x in line.strip().strip("|").split("|")]
            if len(c) == 4 and c[0] == channel and c[1].startswith(measure):
                return c[2], c[3]
    raise KeyError((channel, measure))


def t4(channel):
    with open(RESULTS, encoding="utf-8") as fh:
        for line in fh:
            c = [x.strip() for x in line.strip().strip("|").split("|")]
            if len(c) == 7 and c[0] == channel:
                return c
    raise KeyError(channel)


def results_text():
    with open(RESULTS, encoding="utf-8") as fh:
        return fh.read()


def spot_checks(tabs_new):
    print("\nS  figure data (P10R) vs 03_Results Tables 3 and 4 and text (already P10R)")
    met = {a: pd.read_csv(os.path.join(FIGDATA[a], "fig_codeschedule_vs_survey_metrics.csv")) for a in FIGDATA}
    prof = {a: pd.read_csv(os.path.join(FIGDATA[a], "fig_codeschedule_vs_survey_profiles.csv")) for a in FIGDATA}
    pres = {a: pd.read_csv(os.path.join(FIGDATA[a], "fig_presence_by_channel_data.csv")) for a in FIGDATA}

    def mmed(a, scen, ch, col):
        v = met[a][(met[a].scenario == scen) & (met[a].channel == ch)][col]
        assert len(v) == 4, (scen, ch, col, len(v))
        return float(v.median())

    def prof_med(a, scen, ch, fn):
        p = prof[a][(prof[a].scenario == scen) & (prof[a].channel == ch)]
        return float(np.median([fn(g.sort_values("hour").wd_kW.to_numpy()) for _, g in p.groupby(["building", "city"])]))

    def occ_peak(a, scen, ch):
        p = pres[a][(pres[a].scenario == scen) & (pres[a].channel == ch) & (pres[a].daytype == "WD")]
        return float(np.median([int(np.argmax(g.sort_values("hour").people.to_numpy()))
                                for _, g in p.groupby(["building", "city"])]))

    def hn(x):
        return f"{int(x)}" if float(x).is_integer() else f"{x:.1f}"

    eui, scen, lon = tabs_new["eui"], tabs_new["scen"], tabs_new["lon"]

    def t4fmt(ch, col):
        v = eui[eui.channel == ch][col]
        return f"{v.min():.2f}-{v.max():.2f} ({v.median():.2f})"

    def srange(sc, ch):
        v = scen[(scen.scenario == sc) & (scen.channel == ch)].energy_pct_vs_Bcentral
        lo, hi = v.min(), v.max()
        return f"{lo:+.2f} to {hi:+.2f}"

    txt = results_text()
    checks = [  # (figure, what, computed string, printed string)
        ("Fig 7 metrics", "office 2022 energy peak hour", f"{mmed('new', 'Y2022', 'office', 'wd_peak_hour_circular'):.2f}", t3("Office", "Energy peak")[1]),
        ("Fig 7 profile", "office 2022 energy peak hour (drawn curve)", f"{prof_med('new', 'Y2022', 'office', circ):.2f}", t3("Office", "Energy peak")[1]),
        ("Fig 7 profile", "office 2022 midday-to-night ratio (drawn curve)", f"{prof_med('new', 'Y2022', 'office', mid_night):.2f}", t3("Office", "Midday")[1]),
        ("Fig 7 profile", "retail 2022 midday-to-night ratio", f"{prof_med('new', 'Y2022', 'retail', mid_night):.2f}", t3("Retail", "Midday")[1]),
        ("Fig 7 profile", "hotel 2022 midday-to-night ratio", f"{prof_med('new', 'Y2022', 'hotel', mid_night):.2f}", t3("Hotel", "Midday")[1]),
        ("Fig 7 profile", "residential 2022 midday-to-night ratio", f"{prof_med('new', 'Y2022', 'residential', mid_night):.2f}", t3("Residential", "Midday")[1]),
        ("Fig 7 profile", "building 2022 midday-to-night ratio", f"{prof_med('new', 'Y2022', '_BUILDING', mid_night):.2f}", t3("Building", "Midday")[1]),
        ("Fig 7 panel f", "coincidence factor 6 ch, 2022", f"{mmed('new', 'Y2022', '_BUILDING', 'coincidence_factor_published_6ch'):.3f}", t3("Building", "Coincidence factor, six")[1]),
        ("Fig 7 panel f", "coincidence factor 6 ch, code", f"{mmed('new', 'Default_NECB', '_BUILDING', 'coincidence_factor_published_6ch'):.3f}", t3("Building", "Coincidence factor, six")[0]),
        ("Fig 5 data", "office 2022 occupant peak hour", hn(occ_peak('new', 'Y2022', 'office')), t3("Office", "Occupant")[1]),
        ("Fig 5 data", "retail 2022 occupant peak hour", hn(occ_peak('new', 'Y2022', 'retail')), t3("Retail", "Occupant")[1]),
        ("Fig 5 data", "hotel 2022 occupant peak hour", hn(occ_peak('new', 'Y2022', 'hotel')), t3("Hotel", "Occupant")[1]),
        ("Fig 5 data", "residential 2022 occupant peak hour", hn(occ_peak('new', 'Y2022', 'residential')), t3("Residential", "Occupant")[1]),
        ("Fig 9 (Figure_08_eui)", "office CFA range (median)", t4fmt("office", "eui_CFA_kWh_m2"), t4("Office")[3]),
        ("Fig 9 (Figure_08_eui)", "retail CFA range (median)", t4fmt("retail", "eui_CFA_kWh_m2"), t4("Retail")[3]),
        ("Fig 9 (Figure_08_eui)", "hotel CFA range (median)", t4fmt("hotel", "eui_CFA_kWh_m2"), t4("Hotel")[3]),
        ("Fig 9 (Figure_08_eui)", "residential CFA range (median)", t4fmt("residential", "eui_CFA_kWh_m2"), t4("Residential")[3]),
        ("Fig 9 (Figure_08_eui)", "retail simulations in range", f"{int((eui[eui.channel == 'retail'].verdict_asmodelled == 'PASS').sum())}/56", t4("Retail")[5]),
        ("Fig 9 (Figure_08_eui)", "hotel simulations in range", f"{int((eui[eui.channel == 'hotel'].verdict_asmodelled == 'PASS').sum())}/56", t4("Hotel")[5]),
        ("Fig 6 (Figure_07_long.)", "retail 2022 vs 2005, median (%)", f"{lon[(lon.scenario == 'Y2022') & (lon.channel == 'retail')].energy_pct_vs_2005.median():.2f}",
         "-4.40" if "(-4.40 %" in txt else "NOT IN 03"),
        ("Fig 6 (Figure_07_long.)", "office 2022 vs 2005, median (%)", f"{lon[(lon.scenario == 'Y2022') & (lon.channel == 'office')].energy_pct_vs_2005.median():.2f}",
         "-1.99" if "(-1.99 %)" in txt else "NOT IN 03"),
        ("Fig 8 (Figure_11_scen.)", "office, conservative WFH band alone", srange("sens_office_cons", "office"),
         "+1.07 to +1.65" if "+1.07 to +1.65 %" in txt else "NOT IN 03"),
        ("Fig 8 (Figure_11_scen.)", "retail, optimistic in-store share alone", srange("sens_retail_opt", "retail"),
         "+1.87 to +2.25" if "+1.87 to +2.25 %" in txt else "NOT IN 03"),
    ]
    for fig, what, got, want in checks:
        rec("S+", got == want, f"{fig}: {what}: figure data {got} vs 03 {want}")
    neg = [  # must NOT match
        ("Fig 7 profile", "office ratio with wrong hours (09-16 over 22-04)", f"{prof_med('new', 'Y2022', 'office', lambda p: mid_night(p, day=range(9, 17))):.2f}", t3("Office", "Midday")[1]),
        ("Fig 7 profile", "office ratio from the FROZEN figure data", f"{prof_med('old', 'Y2022', 'office', mid_night):.2f}", t3("Office", "Midday")[1]),
        ("Fig 7 panel f", "CF 6 ch from the 2030 central scenario (wrong scenario)", f"{mmed('new', 'B_central', '_BUILDING', 'coincidence_factor_published_6ch'):.3f}", t3("Building", "Coincidence factor, six")[1]),
        ("Fig 5 data", "retail occupant peak on the code schedule (wrong scenario)", hn(occ_peak('new', 'Default_NECB', 'retail')), t3("Retail", "Occupant")[1]),
        ("Fig 8", "office single lever read from the B_cons bundle", srange("B_cons", "office"), "+1.07 to +1.65"),
        ("Fig 9", "office range on the GFA-share basis (wrong basis)", t4fmt("office", "eui_GFAshare_kWh_m2"), t4("Office")[3]),
        ("Fig 7 metrics", "office peak hour on the hotel channel (wrong channel)", f"{mmed('new', 'Y2022', 'hotel', 'wd_peak_hour_circular'):.2f}", t3("Office", "Energy peak")[1]),
        ("Fig 5 data", "hotel occupant peak from the FROZEN data, code schedule", hn(occ_peak('old', 'Default_NECB', 'hotel')), t3("Hotel", "Occupant")[1]),
    ]
    for fig, what, got, want in neg:
        rec("S-", got != want, f"{fig}: {what}: {got} vs 03 {want} (must differ)")


def main():
    install = "--install" in sys.argv
    tmp = tempfile.mkdtemp(prefix="p9fig_")
    print(f"P9 figures | temp {tmp}")
    before = {}
    for base in list(STEP9_FIGS.values()) + list(P3_FIGS):
        for ext in ("png", "pdf"):
            p = os.path.join(FIGS, f"{base}.{ext}")
            before[p] = md5(p)
            a = os.path.join(FIGS, ARCH, f"{base}.{ext}")
            assert os.path.getsize(a) > 0 and md5(a) == before[p], f"archive of {p} missing or differs"
            if base in STEP9_FIGS.values():
                s = os.path.join(SUBFIGS, f"{base}.{ext}")
                before[s] = md5(s)
                sa = os.path.join(SUBFIGS, ARCH, f"{base}.{ext}")
                assert os.path.getsize(sa) > 0 and md5(sa) == before[s], f"archive of {s} missing or differs"
    try:
        print("\nStep-9 figures")
        d_old, d_new, d_sup, d_new140 = (os.path.join(tmp, x) for x in ("old600", "new600", "sup600", "new140"))
        for d in (d_old, d_new, d_sup, d_new140):
            os.makedirs(d)
        w_old, _ = render_s9(AGG["old"], 600, d_old, pdf=True)
        w_new, tabs_new = render_s9(AGG["new"], 600, d_new, pdf=True)
        w_sup, _ = render_s9(AGG["superseded"], 600, d_sup)
        w_140, _ = render_s9(AGG["new"], 140, d_new140)
        for src, base in STEP9_FIGS.items():
            cur_png, cur_pdf = os.path.join(FIGS, base + ".png"), os.path.join(FIGS, base + ".pdf")
            rec("P1", md5(w_old[src]) == md5(cur_png), f"{base}.png: frozen arm re-render {md5(w_old[src])[:8]} vs current {md5(cur_png)[:8]}")
            pdf_same = md5(w_old[src][:-4] + ".pdf") == md5(cur_pdf)
            print(f"  [info] {base}.pdf: frozen arm re-render {'reproduces' if pdf_same else 'does NOT reproduce'} the current PDF "
                  f"({md5(w_old[src][:-4] + '.pdf')[:8]} vs {md5(cur_pdf)[:8]})")
            rec("P2", md5(w_140[src]) == md5(os.path.join(S9NEW, "figures", src)),
                f"{src}: P10R at 140 dpi vs outputs_step9_P10R/figures")
            rec("N1", md5(w_sup[src]) != md5(cur_png), f"{base}.png: superseded agg arm does not reproduce the current PNG")
            rec("N2", md5(w_new[src]) != md5(w_old[src]), f"{base}.png: P10R render differs from the frozen render")
        # P3: rebuilt tables == Step-9 P10R outputs
        for key, fname, keys, cols in [("eui", "step9_eui_by_channel.csv", ["cell_tag", "channel"], ["eui_CFA_kWh_m2", "eui_GFAshare_kWh_m2"]),
                                       ("scen", "step9_scenario_response.csv", ["cell_tag", "channel"], ["energy_pct_vs_Bcentral"]),
                                       ("lon", "step9_longitudinal.csv", ["cell_tag", "channel"], ["energy_pct_vs_2005", "eui_CFA_kWh_m2"])]:
            ref = pd.read_csv(os.path.join(S9NEW, fname))
            got = tabs_new[key]
            mm = got.merge(ref, on=keys, suffixes=("_fig", "_s9"))
            dmax = max(float((mm[c + "_fig"] - mm[c + "_s9"]).abs().max()) for c in cols)
            rec("P3", len(mm) == len(ref) and dmax < 1e-9, f"{fname}: {len(mm)}/{len(ref)} rows matched, max |diff| {dmax:.1e}")
        v_eui = tabs_new["eui"]
        verd = (v_eui.merge(pd.read_csv(os.path.join(S9NEW, "step9_eui_by_channel.csv")), on=["cell_tag", "channel"])
                .pipe(lambda m: (m.verdict_asmodelled_x == m.verdict_asmodelled_y).all()))
        rec("P3", bool(verd), "step9_eui_by_channel.csv: verdict_asmodelled identical in all rows")

        print("\nP3-data figures")
        p3_new = {}
        for name in P3_FIGS:
            o_old, o_new = os.path.join(tmp, "p3old"), os.path.join(tmp, "p3new")
            os.makedirs(o_old, exist_ok=True)
            os.makedirs(o_new, exist_ok=True)
            r_old = render_p3(name, FIGDATA["old"], o_old)
            r_new = render_p3(name, FIGDATA["new"], o_new)
            p3_new[name] = r_new
            for ext in ("png", "pdf"):
                cur = os.path.join(FIGS, f"{name}.{ext}")
                rec("P1", md5(r_old[ext]) == md5(cur), f"{name}.{ext}: frozen figure data re-render vs current")
                rec("N2", md5(r_new[ext]) != md5(r_old[ext]), f"{name}.{ext}: P10R render differs from the frozen render")

        spot_checks(tabs_new)
        print(f"\nCONTROLS: {N['pass']} PASS / {N['fail']} FAIL")
        if N["fail"]:
            print("NOT INSTALLED: a control failed")
            return 1
        if not install:
            print("dry run: nothing installed (use --install)")
            return 0
        print("\nINSTALL (md5 before -> after)")
        for src, base in STEP9_FIGS.items():
            for ext in ("png", "pdf"):
                s = w_new[src] if ext == "png" else w_new[src][:-4] + ".pdf"
                for dst_dir in (FIGS, SUBFIGS):
                    dst = os.path.join(dst_dir, f"{base}.{ext}")
                    shutil.copyfile(s, dst)
                    print(f"  {os.path.relpath(dst, J3)}  {before[dst]} -> {md5(dst)}")
        for name, r in p3_new.items():
            for ext in ("png", "pdf"):
                dst = os.path.join(FIGS, f"{name}.{ext}")
                shutil.copyfile(r[ext], dst)
                print(f"  {os.path.relpath(dst, J3)}  {before[dst]} -> {md5(dst)}")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
