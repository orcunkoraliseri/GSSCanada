#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""p9_figures_notitle.py (2026-09-25): remove in-figure titles and en/em dashes from the five
Step-9 data figures (Figure_07_longitudinal_4ch, Figure_08_eui_4ch, Figure_09_diurnal_4ch,
Figure_10_peakhour_4ch, Figure_11_scenario_4ch), redrawn from the SAME P10R data with the SAME
Step-9 code (Leg3_4-split/Step9_docs/3rdJ_09_activityDrivenLoads_4split.py, loaded unmodified,
never edited). The two P3 figures (fig_presence_by_channel, fig_codeschedule_vs_survey) already
carry no in-figure title and no en/em dash in any figure text -- checked, not touched.

What this script proves, in order, all before anything is written to writing/figures or
writing/submission/figures:

  R0  my own copy of the unmodified Step-9 fig_* functions (called via s9.fig_eui etc., exactly
      like p9_figures.py's render_s9) reproduces the CURRENTLY INSTALLED PNG/PDF byte for byte,
      on the P10R agg arm, at 600 dpi. This proves my harness (paths, dpi, pdf metadata handling)
      matches what installed the current files.
  D0  the SEEN-FAILING control: my title/dash checks, run against those same (unchanged) figures,
      must FIND a title on all five and an em/en dash on at least one. If they do not fail here,
      the checks are not trustworthy and the script stops.
  NT  the title-removed re-render: same input dataframes (built by the unmodified s9.build_*
      functions), same artists, only the ax.set_title/fig.suptitle calls removed (or, for the one
      case where the removed title carried information the caption does not -- the diurnal
      figure's specific building/city cell -- a short non-title text label is kept instead), and
      the one en-dash in the peak-hour x-axis label replaced with a plain hyphen.
  D1  the title/dash checks now PASS on every one of the five new figures.
  A   the plotted data (every Line2D, Patch/boxplot and Collection/scatter/fill_between array,
      per axis) is identical between the R0 render and the NT render -- proves no data changed.

Only if R0, D0(seen failing), D1 and A all hold does --install copy the five new PNG/PDF pairs
into writing/figures/ and writing/submission/figures/, after archiving the current ones.
Run: PYTHONIOENCODING=utf-8 py -3 p9_figures_notitle.py [--install]
"""
from __future__ import annotations

import hashlib
import importlib.util
import os
import shutil
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
J3 = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
LEG3 = os.path.join(J3, "Leg3_4-split")
STEP9_PY = os.path.join(LEG3, "Step9_docs", "3rdJ_09_activityDrivenLoads_4split.py")
STEP8 = os.path.join(LEG3, "Step8_docs", "outputs_step8")
AGG_NEW = os.path.join(STEP8, "agg_P10R")
FIGS = os.path.join(J3, "writing", "figures")
SUBFIGS = os.path.join(J3, "writing", "submission", "figures")
ARCH = "_archive_pre_notitle_2026-09-25"

STEP9_FIGS = {"fig_longitudinal_4ch.png": "Figure_07_longitudinal_4ch",
              "fig_eui_4ch.png": "Figure_08_eui_4ch",
              "fig_diurnal_4ch.png": "Figure_09_diurnal_4ch",
              "fig_peakhour_4ch.png": "Figure_10_peakhour_4ch",
              "fig_scenario_4ch.png": "Figure_11_scenario_4ch"}

BAD = ("–", "—")  # en dash, em dash
N = {"pass": 0, "fail": 0}


def rec(tag, ok, detail):
    N["pass" if ok else "fail"] += 1
    print(f"  [{'PASS' if ok else 'FAIL'}] {tag:4s} {detail}")


def md5(p):
    with open(p, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def load_s9():
    """Load the Step-9 script UNMODIFIED. Never edited, never monkey-patched in place."""
    spec = importlib.util.spec_from_file_location("step9_4split_notitle", STEP9_PY)
    s9 = importlib.util.module_from_spec(spec)
    sys.modules["step9_4split_notitle"] = s9
    spec.loader.exec_module(s9)
    return s9


def build_frames(s9, agg_dir):
    d = s9.load_agg(agg_dir)
    eui = s9.build_eui(d["annual"], d["meta"])
    s9.SCEN_OF.update(dict(zip(d["meta"]["cell_tag"], d["meta"]["scenario"])))
    ls = s9.build_loadshape(d["peak"], d["diurnal"])
    scen = s9.build_scenario(eui, d["annual"])
    lon = s9.build_longitudinal(eui, ls)
    return d, dict(eui=eui, ls=ls, scen=scen, lon=lon)


# ---------------------------------------------------------------------- R0: unmodified re-render
def render_unmodified(s9, tabs, d, outdir, dpi, pdf):
    """Exactly p9_figures.py's render_s9 body: calls the Step-9 module's OWN fig_* functions,
    completely unmodified, only redirecting where _save writes and at what dpi."""
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
    s9.fig_eui(tabs["eui"], outdir)
    s9.fig_diurnal(d["diurnal"], outdir)
    s9.fig_peakhour(tabs["ls"], outdir)
    s9.fig_scenario(tabs["scen"], outdir)
    s9.fig_longitudinal(tabs["lon"], outdir)
    return written


# ------------------------------------------------------------------- NT: title/dash-removed copy
# Each function below is a literal copy of the corresponding function in
# Leg3_4-split/Step9_docs/3rdJ_09_activityDrivenLoads_4split.py (as read 2026-09-25), calling the
# SAME module constants (s9.TENANT, s9.THEME, s9.BENCH, s9.ALL_CH, s9.SENS, s9.LEVER_ORDER) and the
# SAME matplotlib pyplot object (s9.plt), so the only difference from the original is:
#   - ax.set_title(...) / fig.suptitle(...) calls removed, EXCEPT the per-panel season title in
#     fig_diurnal (identifies which of the two panels is winter vs summer -- the caption does not)
#     and the per-panel channel+lever title in fig_scenario (identifies which of the three panels
#     is which channel -- the caption does not; neither original title contained a dash);
#   - fig_diurnal: the removed suptitle was the ONLY place the specific building/city cell
#     (`cell`) was recorded; the caption ("Diurnal load per channel, central 2030 scenario",
#     chapters_v2/SI_additions.md:18) does not name it, so a short non-title text label
#     (fig.text, not ax.set_title/fig.suptitle) keeps it;
#   - fig_peakhour: the x-axis label's en dash ("... [h] – load-weighted ...") replaced by a
#     plain hyphen; no other character changed.
# No data value, axis, label, legend, colour, size or dpi is touched.

def fig_eui_nt(s9, eui, outdir, _save):
    plt = s9.plt
    fig, ax = plt.subplots(figsize=(9, 4.6))
    xs = np.arange(len(s9.TENANT))
    for i, c in enumerate(s9.TENANT):
        s = eui[eui["channel"] == c]["eui_CFA_kWh_m2"]
        ax.boxplot(s.dropna(), positions=[i], widths=0.5, patch_artist=True,
                   boxprops=dict(facecolor=s9.THEME[c], alpha=.55), medianprops=dict(color="k"))
        b = s9.BENCH[c]
        if b["lo"] is not None:
            ax.add_patch(plt.Rectangle((i - .32, b["lo"]), .64, b["hi"] - b["lo"],
                                       color="green", alpha=.10, zorder=0))
            ax.hlines(b["central"], i - .32, i + .32, color="green", lw=1.4, zorder=1)
    ax.set_xticks(xs)
    ax.set_xticklabels(s9.TENANT)
    ax.set_ylabel("EUI [kWh/m$^2$/yr], CFA basis")
    # title removed: "Step 9 §R1 -- per-channel EUI vs as-modelled band (green) ..."; no panel
    # information lost (single panel, benchmarked visually by the green band).
    ax.grid(alpha=.3, axis="y")
    return _save(fig, outdir, "fig_eui_4ch.png")


def fig_diurnal_nt(s9, diur, outdir, _save, cell=None):
    cell = cell or sorted(diur["cell_tag"].unique())[0]
    fig, axes = s9.plt.subplots(1, 2, figsize=(12, 4.2), sharey=True)
    for ax, season in zip(axes, ("winter", "summer")):
        d = diur[(diur["cell_tag"] == cell) & (diur["season"] == season) & (diur["daytype"] == "WD")
                 & (diur.get("metric", "energy_W") == "energy_W")]
        bottom = np.zeros(24)
        for c in s9.ALL_CH:
            y = d[d["channel"] == c].sort_values("hour")["W"].to_numpy() / 1000.0
            if len(y) != 24:
                continue
            ax.fill_between(range(24), bottom, bottom + y, label=c, color=s9.THEME[c], alpha=.85)
            bottom += y
        ax.set_title(f"{season} · weekday"), ax.set_xlabel("hour"), ax.grid(alpha=.3)
        ax.set_xticks(range(0, 24, 3))
    axes[0].set_ylabel("stacked load [kW]")
    axes[1].legend(fontsize=7, loc="upper right", ncol=2)
    # fig.suptitle removed: "Step 9 §R2 -- coincident four-channel diurnal load · {cell}".
    # The specific cell it is not carried by the caption -> kept as a short, non-title label.
    fig.text(0.01, 0.99, cell, ha="left", va="top", fontsize=7.5, color="dimgray")
    return _save(fig, outdir, "fig_diurnal_4ch.png")


def fig_peakhour_nt(s9, ls, outdir, _save):
    plt = s9.plt
    fig, ax = plt.subplots(figsize=(8.5, 4.2))
    for i, c in enumerate(s9.TENANT):
        h = ls[ls["channel"] == c]["wd_peak_hour_circular"].dropna()
        ax.scatter(h, np.full(len(h), i) + np.random.default_rng(0).normal(0, .05, len(h)),
                   s=22, color=s9.THEME[c], alpha=.7)
        if len(h):
            ax.scatter([h.mean()], [i],
                       marker="|", s=600, color="k", zorder=5)
    ax.set_yticks(range(len(s9.TENANT)))
    ax.set_yticklabels(s9.TENANT)
    ax.set_xlim(0, 24), ax.set_xticks(range(0, 25, 3)), ax.grid(alpha=.3, axis="x")
    ax.set_xlabel("weekday peak hour [h] - load-weighted CIRCULAR mean (caveat 3)")  # en dash -> hyphen
    # title removed: "Step 9 §R2 -- peak timing per channel, all 56 cells"; panel already
    # identified by the y tick labels (channel names).
    return _save(fig, outdir, "fig_peakhour_4ch.png")


def fig_scenario_nt(s9, scen, outdir, _save):
    plt = s9.plt
    fig, axes = plt.subplots(1, 3, figsize=(13, 4), sharey=True)
    for ax, (ch, tags) in zip(axes, s9.SENS.items()):
        sub = scen[(scen["channel"] == ch) & (scen["scenario"].isin(tags))]
        piv = sub.pivot_table(index=["building", "city"], columns="scenario",
                              values="energy_pct_vs_Bcentral")
        for tag in tags:
            if tag in piv.columns:
                ax.scatter([tag] * len(piv), piv[tag], s=40, color=s9.THEME[ch], alpha=.8)
        ax.axhline(0, color="k", lw=.8)
        ax.set_title(f"{ch} lever  {s9.LEVER_ORDER[ch]}", fontsize=9)
        ax.tick_params(axis="x", rotation=20, labelsize=7), ax.grid(alpha=.3, axis="y")
    axes[0].set_ylabel("channel energy Δ% vs B_central")
    # fig.suptitle removed: "Step 9 §R3 -- one-at-a-time scenario response ...". Per-panel
    # titles kept: they are the only place identifying which of the three panels is which channel.
    return _save(fig, outdir, "fig_scenario_4ch.png")


def fig_longitudinal_nt(s9, lon, outdir, _save):
    plt = s9.plt
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    for c in s9.TENANT:
        for ax, col, lab in ((axes[0], "energy_pct_vs_2005", "energy Δ% vs 2005"),
                             (axes[1], "midday_share", "weekday midday share")):
            g = lon[lon["channel"] == c].groupby("scenario")[col].mean().reindex(s9.ERAS)
            ax.plot(s9.ERAS, g.to_numpy(), "-o", color=s9.THEME[c], label=c)
            ax.set_ylabel(lab), ax.grid(alpha=.3)
    axes[1].legend(fontsize=8)
    # fig.suptitle removed: "Step 9 §R4 -- longitudinal 2005→2022 ...". Panel already
    # identified by each axis's own ylabel.
    return _save(fig, outdir, "fig_longitudinal_4ch.png")


def render_notitle(s9, tabs, d, outdir, dpi, pdf):
    written = {}

    def _save(fig, _outdir, fname):
        p = os.path.join(outdir, fname)
        fig.savefig(p, dpi=dpi, bbox_inches="tight")
        if pdf:
            fig.savefig(p[:-4] + ".pdf", bbox_inches="tight", metadata={"CreationDate": None, "ModDate": None})
        s9.plt.close(fig)
        written[fname] = p
        return p

    fig_eui_nt(s9, tabs["eui"], outdir, _save)
    fig_diurnal_nt(s9, d["diurnal"], outdir, _save)
    fig_peakhour_nt(s9, tabs["ls"], outdir, _save)
    fig_scenario_nt(s9, tabs["scen"], outdir, _save)
    fig_longitudinal_nt(s9, tabs["lon"], outdir, _save)
    return written


# --------------------------------------------------------------------- artist-data extraction
def _round(a, nd=9):
    """Round to nd decimals when numeric; a categorical axis (e.g. era labels 'Y2005', ...) is
    passed straight through as plain strings, exact-match compared instead."""
    arr = np.asarray(a)
    if arr.dtype.kind in "fc":
        return np.round(arr.astype(float), nd)
    if arr.dtype.kind in "iub":
        return arr.astype(float)
    try:
        return np.round(arr.astype(float), nd)
    except (ValueError, TypeError):
        return np.asarray([str(v) for v in arr])


def extract_fig_data(png_path_stub, fig):
    """Collect every numeric array drawn by any Line2D / Patch / Collection on every axis, plus
    every text string EXCEPT the axes title / figure suptitle (those are allowed to change)."""
    out = {"axes": [], "texts_nontitle": []}
    for ax in fig.axes:
        a = {"lines": [], "patches": [], "collections": []}
        for ln in ax.lines:
            x, y = ln.get_data()
            a["lines"].append((_round(x).tolist(), _round(y).tolist()))
        for p in ax.patches:
            try:
                v = p.get_path().vertices
                a["patches"].append(_round(v).tolist())
            except Exception:
                pass
        for c in ax.collections:
            try:
                off = c.get_offsets()
                if off is not None and len(off):
                    a["collections"].append(("offsets", _round(np.asarray(off)).tolist()))
            except Exception:
                pass
            try:
                for path in c.get_paths():
                    a["collections"].append(("path", _round(path.vertices).tolist()))
            except Exception:
                pass
        a["lines"].sort(key=repr)
        a["patches"].sort(key=repr)
        a["collections"].sort(key=repr)
        out["axes"].append(a)
        for lab, txt in (("xlabel", ax.get_xlabel()), ("ylabel", ax.get_ylabel())):
            out["texts_nontitle"].append(txt)
        for t in ax.texts:
            out["texts_nontitle"].append(t.get_text())
        leg = ax.get_legend()
        if leg is not None:
            out["texts_nontitle"].extend(h.get_text() for h in leg.get_texts())
    for t in fig.texts:
        out["texts_nontitle"].append(t.get_text())
    return out


def data_equal(a, b):
    if a["axes"] != b["axes"]:
        return False
    return True


def collect_title_dash(fig):
    """suptitle text, per-axis title text, and every OTHER text string, separately."""
    suptitle = fig._suptitle.get_text() if fig._suptitle is not None else ""
    ax_titles = []
    other = []
    for ax in fig.axes:
        # ax.get_title() alone only reads the CENTER-located title; matplotlib also supports
        # independent "left" and "right" titles (used by the P3 figures' "(a) Office" panel
        # labels via set_title(..., loc="left")) -- check all three, or a left/right title would
        # silently never be inspected.
        for loc in ("center", "left", "right"):
            ax_titles.append(ax.get_title(loc=loc))
        other.append(ax.get_xlabel())
        other.append(ax.get_ylabel())
        for t in ax.texts:
            other.append(t.get_text())
        leg = ax.get_legend()
        if leg is not None:
            other.extend(h.get_text() for h in leg.get_texts())
        for lbl in ax.get_xticklabels() + ax.get_yticklabels():
            other.append(lbl.get_text())
    for t in fig.texts:
        other.append(t.get_text())
    return suptitle, ax_titles, other


# Per-figure exact set of ax titles that are intentionally KEPT, because they are panel labels
# the caption does not carry (documented in the module docstring above and in the rewrite log),
# not the old descriptive per-figure title. Everything else must be empty.
ALLOWED_AX_TITLES = {
    "Figure_09_diurnal_4ch": {"winter · weekday", "summer · weekday"},
    "Figure_11_scenario_4ch": {"office lever  ('conservative', 'hybrid', 'fullyhybrid')",
                               "retail lever  (0.9, 0.97, 1.05)",
                               "hotel lever  (0.92, 1.0, 1.05)"},
    # the two P3 figures (untouched by this script) already use exactly this pattern -- short
    # panel labels, not a descriptive figure title -- confirmed against the source in
    # writing/figures/fig_presence_by_channel.py and fig_codeschedule_vs_survey.py.
    "fig_presence_by_channel": {"(a) Office", "(b) Retail", "(c) Hotel", "(d) Residential"},
    "fig_codeschedule_vs_survey": {"(a) Office", "(b) Retail", "(c) Hotel", "(d) Residential",
                                   "(e) Whole building", "(f) Coincidence factor"},
}


def check_no_title_no_dash(fig, label, allow_ax_titles=False):
    """(b) no en/em dash anywhere; (c) fig.suptitle always empty, and every ax title is either
    empty or (only when allow_ax_titles) exactly one of the documented, intentionally-kept panel
    labels for this figure -- never the old descriptive title."""
    suptitle, ax_titles, other = collect_title_dash(fig)
    allowed = ALLOWED_AX_TITLES.get(label, set()) if allow_ax_titles else set()
    leftover_titles = [t for t in ax_titles if t.strip() and t not in allowed]
    has_bad_title = bool(suptitle.strip()) or bool(leftover_titles)
    kept_titles = [t for t in ax_titles if t.strip() and t in allowed]
    all_text = [suptitle] + ax_titles + other
    dashed = [s for s in all_text if any(ch in s for ch in BAD)]
    has_dash = bool(dashed)
    return has_bad_title, has_dash, ([suptitle] + ax_titles), dashed, kept_titles


def main():
    install = "--install" in sys.argv
    tmp = tempfile.mkdtemp(prefix="p9fignt_")
    print(f"P9 figures (notitle) | temp {tmp}")

    before = {}
    for base in STEP9_FIGS.values():
        for ext in ("png", "pdf"):
            p = os.path.join(FIGS, f"{base}.{ext}")
            before[p] = md5(p)
            a = os.path.join(FIGS, ARCH, f"{base}.{ext}")
            assert os.path.getsize(a) > 0 and md5(a) == before[p], f"archive of {p} missing or differs"
            s = os.path.join(SUBFIGS, f"{base}.{ext}")
            before[s] = md5(s)
            sa = os.path.join(SUBFIGS, ARCH, f"{base}.{ext}")
            assert os.path.getsize(sa) > 0 and md5(sa) == before[s], f"archive of {s} missing or differs"

    d_r0, d_nt = (os.path.join(tmp, x) for x in ("r0_600", "nt_600"))
    os.makedirs(d_r0)
    os.makedirs(d_nt)

    s9_a = load_s9()
    d_a, tabs_a = build_frames(s9_a, AGG_NEW)
    print("\nR0  unmodified Step-9 fig_* functions, P10R arm, 600 dpi -- reproduce current install")
    w_r0 = render_unmodified(s9_a, tabs_a, d_a, d_r0, 600, pdf=True)
    r0_figs = {}
    for src, base in STEP9_FIGS.items():
        cur_png, cur_pdf = os.path.join(FIGS, base + ".png"), os.path.join(FIGS, base + ".pdf")
        rec("R0", md5(w_r0[src]) == md5(cur_png), f"{base}.png: unmodified re-render {md5(w_r0[src])[:8]} vs current {md5(cur_png)[:8]}")
        rec("R0", md5(w_r0[src][:-4] + ".pdf") == md5(cur_pdf), f"{base}.pdf: unmodified re-render vs current")

    print("\nD0  SEEN-FAILING control: run the title/dash checks on the (still titled) R0 render")
    s9_b = load_s9()
    d_b, tabs_b = build_frames(s9_b, AGG_NEW)
    d_r0b = os.path.join(tmp, "r0_for_checks")
    os.makedirs(d_r0b)

    def _save_keepfig(fig, _outdir, fname):
        # like the real _save, but returns the fig object too, via a side dict
        p = os.path.join(_outdir, fname)
        fig.savefig(p, dpi=140, bbox_inches="tight")
        figs_seen[fname] = fig
        return p

    figs_seen = {}
    s9_b._save = _save_keepfig
    s9_b.fig_eui(tabs_b["eui"], d_r0b)
    s9_b.fig_diurnal(d_b["diurnal"], d_r0b)
    s9_b.fig_peakhour(tabs_b["ls"], d_r0b)
    s9_b.fig_scenario(tabs_b["scen"], d_r0b)
    s9_b.fig_longitudinal(tabs_b["lon"], d_r0b)
    any_title, any_dash = False, False
    for src, base in STEP9_FIGS.items():
        ht, hd, titles, dashed, _kept = check_no_title_no_dash(figs_seen[src], base, allow_ax_titles=False)
        any_title = any_title or ht
        any_dash = any_dash or hd
        print(f"    {base}: title present={ht} ({titles!r}) dash present={hd} {dashed!r}")
    rec("D0", any_title, "at least one of the 5 old figures has a non-empty title (seen failing)")
    rec("D0", any_dash, "at least one of the 5 old figures has an en/em dash in some text (seen failing)")
    for fig in figs_seen.values():
        s9_b.plt.close(fig)

    print("\nNT  title/dash-removed re-render, same P10R data, same code otherwise")
    s9_c = load_s9()
    d_c, tabs_c = build_frames(s9_c, AGG_NEW)
    figs_nt = {}
    orig_save_ref = {}

    def _save_nt_keepfig(fig, _outdir, fname):
        p = os.path.join(d_nt, fname)
        fig.savefig(p, dpi=600, bbox_inches="tight")
        fig.savefig(p[:-4] + ".pdf", bbox_inches="tight", metadata={"CreationDate": None, "ModDate": None})
        figs_nt[fname] = fig
        return p

    fig_eui_nt(s9_c, tabs_c["eui"], d_nt, _save_nt_keepfig)
    fig_diurnal_nt(s9_c, d_c["diurnal"], d_nt, _save_nt_keepfig)
    fig_peakhour_nt(s9_c, tabs_c["ls"], d_nt, _save_nt_keepfig)
    fig_scenario_nt(s9_c, tabs_c["scen"], d_nt, _save_nt_keepfig)
    fig_longitudinal_nt(s9_c, tabs_c["lon"], d_nt, _save_nt_keepfig)

    print("\nD1  title/dash checks on the NEW figures -- must now pass")
    for src, base in STEP9_FIGS.items():
        ht, hd, titles, dashed, kept = check_no_title_no_dash(figs_nt[src], base, allow_ax_titles=True)
        rec("D1", not ht, f"{base}: no leftover descriptive title (suptitle+ax titles {titles!r}; "
                          f"kept panel labels {kept!r})")
        rec("D1", not hd, f"{base}: no en/em dash in any text ({dashed!r})")

    print("\nP3  the two already-compliant P3 figures (fig_presence_by_channel, "
          "fig_codeschedule_vs_survey) are verified, NOT touched, NOT re-installed")
    import importlib.util as _ilu
    import matplotlib.pyplot as _plt
    P3_FIGS = {"fig_presence_by_channel": None, "fig_codeschedule_vs_survey": None}
    for name in P3_FIGS:
        spec = _ilu.spec_from_file_location(f"{name}_check", os.path.join(FIGS, name + ".py"))
        m = _ilu.module_from_spec(spec)
        spec.loader.exec_module(m)
        m.OUT = os.path.join(tmp, "p3check", name)
        os.makedirs(os.path.dirname(m.OUT), exist_ok=True)
        # fig_style.save_both closes the figure once it writes it, so capture the fig object
        # (still fully intact off-screen) via a thin wrapper around the module's OWN save_both,
        # rather than reading matplotlib's current-figure state after main() returns.
        captured = {}
        orig_save_both = m.save_both

        def _wrap(fig, out, dpi=300, _orig=orig_save_both, _cap=captured):
            _cap["fig"] = fig
            return _orig(fig, out, dpi)

        m.save_both = _wrap
        m.main()
        fig = captured["fig"]
        ht, hd, titles, dashed, kept = check_no_title_no_dash(fig, name, allow_ax_titles=True)
        rec("P3", not ht, f"{name}: already has no descriptive figure title (only panel labels {kept!r})")
        rec("P3", not hd, f"{name}: already has no en/em dash ({dashed!r})")
        _plt.close(fig)
    print("  (panel labels like '(a) Office' are ax.set_title calls in these two scripts, but "
          "they are short panel identifiers, not descriptive figure titles -- see check output above)")

    print("\nA   plotted-data identity: R0 vs NT, per axis, every line/patch/collection array")
    # re-render R0 in-memory (not from disk) so the artists are still alive for comparison
    s9_d = load_s9()
    d_d, tabs_d = build_frames(s9_d, AGG_NEW)
    figs_r0_mem = {}

    def _save_r0_keepfig(fig, _outdir, fname):
        figs_r0_mem[fname] = fig
        return None

    s9_d._save = _save_r0_keepfig
    s9_d.fig_eui(tabs_d["eui"], "/unused")
    s9_d.fig_diurnal(d_d["diurnal"], "/unused")
    s9_d.fig_peakhour(tabs_d["ls"], "/unused")
    s9_d.fig_scenario(tabs_d["scen"], "/unused")
    s9_d.fig_longitudinal(tabs_d["lon"], "/unused")

    for src, base in STEP9_FIGS.items():
        old_data = extract_fig_data(base, figs_r0_mem[src])
        new_data = extract_fig_data(base, figs_nt[src])
        rec("A", data_equal(old_data, new_data), f"{base}: line/patch/collection arrays identical, old vs new")
    for fig in figs_r0_mem.values():
        s9_d.plt.close(fig)

    print(f"\nCONTROLS: {N['pass']} PASS / {N['fail']} FAIL")
    if N["fail"]:
        print("NOT INSTALLED: a control failed")
        for fig in figs_nt.values():
            s9_c.plt.close(fig)
        shutil.rmtree(tmp, ignore_errors=True)
        return 1

    if not install:
        print("dry run: nothing installed (use --install)")
        for fig in figs_nt.values():
            s9_c.plt.close(fig)
        shutil.rmtree(tmp, ignore_errors=True)
        return 0

    print("\nINSTALL (md5 before -> after)")
    for src, base in STEP9_FIGS.items():
        for ext in ("png", "pdf"):
            s = os.path.join(d_nt, src) if ext == "png" else os.path.join(d_nt, src[:-4] + ".pdf")
            for dst_dir in (FIGS, SUBFIGS):
                dst = os.path.join(dst_dir, f"{base}.{ext}")
                shutil.copyfile(s, dst)
                print(f"  {os.path.relpath(dst, J3)}  {before[dst]} -> {md5(dst)}")

    for fig in figs_nt.values():
        s9_c.plt.close(fig)
    shutil.rmtree(tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
