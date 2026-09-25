#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""p9_figures_plain.py (2026-09-25): replace internal code labels with plain journal labels in the
five Step-9 data figures (Figure_07_longitudinal_4ch, Figure_08_eui_4ch, Figure_09_diurnal_4ch,
Figure_10_peakhour_4ch, Figure_11_scenario_4ch), redrawn from the SAME P10R data with the SAME
Step-9 code (Leg3_4-split/Step9_docs/3rdJ_09_activityDrivenLoads_4split.py, loaded unmodified,
never edited). Builds on top of the already-installed title/dash removal
(`p9_figures_notitle.py`, 2026-09-25): this script's own R0 baseline is that NOTITLE render (the
render logic that produced what is currently installed), not the raw titled Step-9 output.

Label changes made (verbatim, see rewrite_log.md section "Figure labels made plain 2026-09-25"
for the full old -> new table and the caption phrases the manuscript must carry):
  - Figure_09_diurnal_4ch: the top-left cell tag text ("B_central__SuperTall__CLG") is REMOVED
    entirely (no replacement figure text; the caption must name the cell in plain words instead
    -- see rewrite_log.md). Legend "residential_common" -> "residential common",
    "service_MEP" -> "service and plant".
  - Figure_07_longitudinal_4ch: x tick labels "Y2005"/"Y2010"/"Y2015"/"Y2022" -> "2005"/"2010"/
    "2015"/"2022" (both panels). Left y label "energy Δ% vs 2005" -> "energy change from 2005
    (%)".
  - Figure_11_scenario_4ch: y label "channel energy Δ% vs B_central" -> "channel energy
    change vs central scenario (%)". x tick labels "sens_<channel>_cons"/"sens_<channel>_opt" ->
    "<channel> conservative"/"<channel> optimistic"; "B_central" -> "central" (BUNDLES =
    ["B_cons", "B_central", "B_opt"] in the Step-9 source -> conservative/central/optimistic).
  - Figure_08_eui_4ch, Figure_10_peakhour_4ch: NO label change (already plain after the notitle
    round: "EUI"/"kWh/m2/yr"/"CFA basis" are defined in the main text nomenclature table, and the
    peak-hour x label already uses a plain hyphen with no underscore/code token). Verified
    identical, not just untouched by inspection -- see check M2 below.
  - Panel labels kept as-is (documented already in p9_figures_notitle.py and unchanged here):
    "winter · weekday" / "summer · weekday" (Figure_09); "<channel> lever  (...)"
    (Figure_11). Neither contains an underscore, "Y20", "CLG", "MTL" or an en/em dash.

What this script proves, in order, all before anything is written to writing/figures or
writing/submission/figures:
  R0  my own copy of the notitle fig_*_nt functions (identical to p9_figures_notitle.py, not
      re-edited here) reproduces the CURRENTLY INSTALLED PNG/PDF byte for byte, on the P10R agg
      arm, at 600 dpi. This is the baseline this script edits, not the raw titled Step-9 output.
  D0  the SEEN-FAILING control: the plain-label checks below (no "_", "Y20", "CLG", "MTL", en/em
      dash in ANY figure text), run against that same currently-installed (notitle) render, must
      FIND at least one violation. If they do not fail here, the checks are not trustworthy and
      the script stops.
  PL  the plain-label re-render: same input dataframes (built by the unmodified s9.build_*
      functions), same artists, only the text substitutions listed above applied. Figures 08 and
      10 use the notitle functions unchanged (no substitution needed).
  D1  the plain-label checks now PASS on every one of the five new figures.
  M   per-figure mapping check: the SPECIFIC old strings this task named are present in the R0
      (old) render and ABSENT from the PL (new) render, and the SPECIFIC new strings are present
      in the PL render only. For Figure_08/Figure_10 (no intended change): the full non-title text
      list (xlabel, ylabel, tick labels, legend, free text) is EXACTLY IDENTICAL old vs new.
  A   the plotted data (every Line2D, Patch/boxplot and Collection/scatter/fill_between array,
      per axis) is identical between the R0 render and the PL render -- proves no data changed.

Only if R0, D0(seen failing), D1, M and A all hold does --install copy the five new PNG/PDF pairs
into writing/figures/ and writing/submission/figures/, after archiving the current (notitle) ones.
Run: PYTHONIOENCODING=utf-8 py -3 p9_figures_plain.py [--install]
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
ARCH = "_archive_pre_plain_2026-09-25"

STEP9_FIGS = {"fig_longitudinal_4ch.png": "Figure_07_longitudinal_4ch",
              "fig_eui_4ch.png": "Figure_08_eui_4ch",
              "fig_diurnal_4ch.png": "Figure_09_diurnal_4ch",
              "fig_peakhour_4ch.png": "Figure_10_peakhour_4ch",
              "fig_scenario_4ch.png": "Figure_11_scenario_4ch"}

BAD_CHARS = ("–", "—")  # en dash, em dash
BAD_SUBSTR = ("_", "Y20", "CLG", "MTL")  # code tokens this task requires gone from figure text
N = {"pass": 0, "fail": 0}

# Plain-label maps, straight from the Step-9 module constants (never hand-typed independent of
# them): BUNDLES = ["B_cons", "B_central", "B_opt"] -> conservative/central/optimistic;
# THEME keys "residential_common"/"service_MEP" are the two non-tenant channels in ALL_CH.
PLAIN_CH_LEGEND = {"residential_common": "residential common", "service_MEP": "service and plant"}
PLAIN_SENS = {}
for _ch in ("office", "retail", "hotel"):
    PLAIN_SENS[f"sens_{_ch}_cons"] = f"{_ch} conservative"
    PLAIN_SENS[f"sens_{_ch}_opt"] = f"{_ch} optimistic"
PLAIN_SENS["B_central"] = "central"


def rec(tag, ok, detail):
    N["pass" if ok else "fail"] += 1
    print(f"  [{'PASS' if ok else 'FAIL'}] {tag:4s} {detail}")


def md5(p):
    with open(p, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def load_s9():
    """Load the Step-9 script UNMODIFIED. Never edited, never monkey-patched in place."""
    spec = importlib.util.spec_from_file_location("step9_4split_plain", STEP9_PY)
    s9 = importlib.util.module_from_spec(spec)
    sys.modules["step9_4split_plain"] = s9
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


# ------------------------------------------------------------------- NT: title/dash-removed copy
# Verbatim from p9_figures_notitle.py (NOT re-edited here): this is the render logic that produced
# what is CURRENTLY INSTALLED. It is this script's R0 baseline, not the raw titled Step-9 output.

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
    ax.set_xlabel("weekday peak hour [h] - load-weighted CIRCULAR mean (caveat 3)")
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


# --------------------------------------------------------------------------- PL: plain-label copy
# Each function is a copy of the corresponding *_nt function above, with ONLY the text
# substitutions documented in the module docstring applied. No data value, axis range, colour,
# marker, dpi or layout parameter is touched. fig_eui and fig_peakhour need no substitution (their
# _nt version is already plain), so the PL render step below calls fig_eui_nt/fig_peakhour_nt
# directly for those two.

def fig_diurnal_pl(s9, diur, outdir, _save, cell=None):
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
            ax.fill_between(range(24), bottom, bottom + y, label=PLAIN_CH_LEGEND.get(c, c),
                             color=s9.THEME[c], alpha=.85)
            bottom += y
        ax.set_title(f"{season} · weekday"), ax.set_xlabel("hour"), ax.grid(alpha=.3)
        ax.set_xticks(range(0, 24, 3))
    axes[0].set_ylabel("stacked load [kW]")
    axes[1].legend(fontsize=7, loc="upper right", ncol=2)
    # cell tag ("B_central__SuperTall__CLG") removed entirely -- no fig.text call. The plain
    # phrase for the caption to carry instead is recorded in rewrite_log.md.
    return _save(fig, outdir, "fig_diurnal_4ch.png")


def fig_scenario_pl(s9, scen, outdir, _save):
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
        # tick POSITIONS/DATA unchanged (still keyed on the original scenario tag strings, so the
        # categorical x locations match the R0 render exactly); only the displayed TEXT is remapped.
        ax.set_xticklabels([PLAIN_SENS[t] for t in tags])
    axes[0].set_ylabel("channel energy change vs central scenario (%)")
    return _save(fig, outdir, "fig_scenario_4ch.png")


def fig_longitudinal_pl(s9, lon, outdir, _save):
    plt = s9.plt
    eras_plain = [e.replace("Y", "") for e in s9.ERAS]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    for c in s9.TENANT:
        for ax, col, lab in ((axes[0], "energy_pct_vs_2005", "energy change from 2005 (%)"),
                             (axes[1], "midday_share", "weekday midday share")):
            g = lon[lon["channel"] == c].groupby("scenario")[col].mean().reindex(s9.ERAS)
            ax.plot(s9.ERAS, g.to_numpy(), "-o", color=s9.THEME[c], label=c)
            ax.set_ylabel(lab), ax.grid(alpha=.3)
    axes[1].legend(fontsize=8)
    # x tick TEXT only remapped ("Y2005" -> "2005", ...); the plotted x DATA passed to ax.plot
    # above is still the original s9.ERAS strings, so the categorical positions are unchanged.
    axes[0].set_xticklabels(eras_plain)
    axes[1].set_xticklabels(eras_plain)
    return _save(fig, outdir, "fig_longitudinal_4ch.png")


def render_plain(s9, tabs, d, outdir, dpi, pdf):
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
    fig_diurnal_pl(s9, d["diurnal"], outdir, _save)
    fig_peakhour_nt(s9, tabs["ls"], outdir, _save)
    fig_scenario_pl(s9, tabs["scen"], outdir, _save)
    fig_longitudinal_pl(s9, tabs["lon"], outdir, _save)
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
    """Collect every numeric array drawn by any Line2D / Patch / Collection on every axis. Tick
    labels and titles are NOT included here (they are allowed, and expected, to change -- checked
    separately by check_labels / the M-series mapping checks)."""
    out = {"axes": []}
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
    return out


def data_equal(a, b):
    return a["axes"] == b["axes"]


def collect_all_text(fig):
    """suptitle text, per-axis title text (all three loc positions), and every OTHER text string
    (xlabel, ylabel, tick labels, legend, free-standing fig/ax text) -- kept in separate buckets so
    a caller can apply different rules to titles vs. everything else."""
    suptitle = fig._suptitle.get_text() if fig._suptitle is not None else ""
    ax_titles = []
    other = []
    for ax in fig.axes:
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


# Per-figure exact set of ax titles that are intentionally KEPT (panel labels the caption does not
# carry -- documented in p9_figures_notitle.py and unchanged by this script). Everything else must
# be empty. None of these contain "_", "Y20", "CLG", "MTL" or an en/em dash.
ALLOWED_AX_TITLES = {
    "Figure_09_diurnal_4ch": {"winter · weekday", "summer · weekday"},
    "Figure_11_scenario_4ch": {"office lever  ('conservative', 'hybrid', 'fullyhybrid')",
                               "retail lever  (0.9, 0.97, 1.05)",
                               "hotel lever  (0.92, 1.0, 1.05)"},
    "fig_presence_by_channel": {"(a) Office", "(b) Retail", "(c) Hotel", "(d) Residential"},
    "fig_codeschedule_vs_survey": {"(a) Office", "(b) Retail", "(c) Hotel", "(d) Residential",
                                   "(e) Whole building", "(f) Coincidence factor"},
}


def _bad_strings(strings):
    return [s for s in strings if s and (any(ch in s for ch in BAD_CHARS)
                                          or any(sub in s for sub in BAD_SUBSTR))]


def check_plain(fig, label, allow_ax_titles=False):
    """(c) fig.suptitle always empty, and every ax title is either empty or (only when
    allow_ax_titles) exactly one of the documented, intentionally-kept panel labels; (b) no text
    ANYWHERE in the figure (suptitle, ax titles at all 3 loc positions, axis labels, legend
    entries, tick labels, free text) contains an en/em dash or one of the code-token substrings
    "_" / "Y20" / "CLG" / "MTL"."""
    suptitle, ax_titles, other = collect_all_text(fig)
    allowed = ALLOWED_AX_TITLES.get(label, set()) if allow_ax_titles else set()
    leftover_titles = [t for t in ax_titles if t.strip() and t not in allowed]
    has_bad_title = bool(suptitle.strip()) or bool(leftover_titles)
    kept_titles = [t for t in ax_titles if t.strip() and t in allowed]
    all_text = [suptitle] + ax_titles + other
    flagged = _bad_strings(all_text)
    return has_bad_title, bool(flagged), ([suptitle] + ax_titles), flagged, kept_titles


def main():
    install = "--install" in sys.argv
    tmp = tempfile.mkdtemp(prefix="p9figpl_")
    print(f"P9 figures (plain labels) | temp {tmp}")

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

    d_r0, d_pl = (os.path.join(tmp, x) for x in ("r0_600", "pl_600"))
    os.makedirs(d_r0)
    os.makedirs(d_pl)

    s9_a = load_s9()
    d_a, tabs_a = build_frames(s9_a, AGG_NEW)
    print("\nR0  notitle fig_*_nt functions (unchanged from p9_figures_notitle.py), P10R arm, "
          "600 dpi -- reproduce CURRENTLY INSTALLED files")
    w_r0 = render_notitle(s9_a, tabs_a, d_a, d_r0, 600, pdf=True)
    r0_figs = {}
    for src, base in STEP9_FIGS.items():
        cur_png, cur_pdf = os.path.join(FIGS, base + ".png"), os.path.join(FIGS, base + ".pdf")
        rec("R0", md5(w_r0[src]) == md5(cur_png), f"{base}.png: notitle re-render {md5(w_r0[src])[:8]} vs current {md5(cur_png)[:8]}")
        rec("R0", md5(w_r0[src][:-4] + ".pdf") == md5(cur_pdf), f"{base}.pdf: notitle re-render vs current")

    print("\nD0  SEEN-FAILING control: run the plain-label checks on the (still code-labelled) "
          "R0 render")
    s9_b = load_s9()
    d_b, tabs_b = build_frames(s9_b, AGG_NEW)
    d_r0b = os.path.join(tmp, "r0_for_checks")
    os.makedirs(d_r0b)

    def _save_keepfig(fig, _outdir, fname):
        p = os.path.join(_outdir, fname)
        fig.savefig(p, dpi=140, bbox_inches="tight")
        figs_seen[fname] = fig
        return p

    figs_seen = {}
    fig_eui_nt(s9_b, tabs_b["eui"], d_r0b, _save_keepfig)
    fig_diurnal_nt(s9_b, d_b["diurnal"], d_r0b, _save_keepfig)
    fig_peakhour_nt(s9_b, tabs_b["ls"], d_r0b, _save_keepfig)
    fig_scenario_nt(s9_b, tabs_b["scen"], d_r0b, _save_keepfig)
    fig_longitudinal_nt(s9_b, tabs_b["lon"], d_r0b, _save_keepfig)
    any_title, any_bad = False, False
    for src, base in STEP9_FIGS.items():
        ht, hb, titles, flagged, _kept = check_plain(figs_seen[src], base, allow_ax_titles=False)
        any_title = any_title or ht
        any_bad = any_bad or hb
        print(f"    {base}: title present={ht} bad-text present={hb} {flagged!r}")
    rec("D0", any_bad, "at least one of the 5 notitle figures still has a code-label token "
                       "('_'/'Y20'/'CLG'/'MTL') or an en/em dash somewhere (seen failing)")

    print("\nPL  plain-label re-render, same P10R data, same code otherwise")
    s9_c = load_s9()
    d_c, tabs_c = build_frames(s9_c, AGG_NEW)
    figs_pl = {}

    def _save_pl_keepfig(fig, _outdir, fname):
        p = os.path.join(d_pl, fname)
        fig.savefig(p, dpi=600, bbox_inches="tight")
        fig.savefig(p[:-4] + ".pdf", bbox_inches="tight", metadata={"CreationDate": None, "ModDate": None})
        figs_pl[fname] = fig
        return p

    fig_eui_nt(s9_c, tabs_c["eui"], d_pl, _save_pl_keepfig)
    fig_diurnal_pl(s9_c, d_c["diurnal"], d_pl, _save_pl_keepfig)
    fig_peakhour_nt(s9_c, tabs_c["ls"], d_pl, _save_pl_keepfig)
    fig_scenario_pl(s9_c, tabs_c["scen"], d_pl, _save_pl_keepfig)
    fig_longitudinal_pl(s9_c, tabs_c["lon"], d_pl, _save_pl_keepfig)

    print("\nD1  plain-label checks on the NEW figures -- must now pass")
    for src, base in STEP9_FIGS.items():
        ht, hb, titles, flagged, kept = check_plain(figs_pl[src], base, allow_ax_titles=True)
        rec("D1", not ht, f"{base}: no leftover descriptive title (suptitle+ax titles {titles!r}; "
                          f"kept panel labels {kept!r})")
        rec("D1", not hb, f"{base}: no code-label token or en/em dash in any text ({flagged!r})")

    print("\nM   per-figure label-mapping check: exact old strings gone, exact new strings present")
    _, _, other_r0_07 = collect_all_text(figs_seen["fig_longitudinal_4ch.png"])
    _, _, other_pl_07 = collect_all_text(figs_pl["fig_longitudinal_4ch.png"])
    for old in ("Y2005", "Y2010", "Y2015", "Y2022", "energy Δ% vs 2005"):
        rec("M07", old in other_r0_07, f"Figure_07 old text present in R0: {old!r}")
        rec("M07", old not in other_pl_07, f"Figure_07 old text absent from PL: {old!r}")
    for new in ("2005", "2010", "2015", "2022", "energy change from 2005 (%)"):
        rec("M07", new in other_pl_07, f"Figure_07 new text present in PL: {new!r}")

    _, _, other_r0_09 = collect_all_text(figs_seen["fig_diurnal_4ch.png"])
    _, _, other_pl_09 = collect_all_text(figs_pl["fig_diurnal_4ch.png"])
    for old in ("B_central__SuperTall__CLG", "residential_common", "service_MEP"):
        rec("M09", old in other_r0_09, f"Figure_09 old text present in R0: {old!r}")
        rec("M09", old not in other_pl_09, f"Figure_09 old text absent from PL: {old!r}")
    for new in ("residential common", "service and plant"):
        rec("M09", new in other_pl_09, f"Figure_09 new text present in PL: {new!r}")
    rec("M09", "B_central__SuperTall__CLG" not in other_pl_09 and
              not any(t.startswith("B_") for t in other_pl_09 if t),
        "Figure_09: cell tag removed entirely, no replacement text added")

    _, _, other_r0_11 = collect_all_text(figs_seen["fig_scenario_4ch.png"])
    _, _, other_pl_11 = collect_all_text(figs_pl["fig_scenario_4ch.png"])
    old_11 = ["sens_office_cons", "sens_office_opt", "sens_retail_cons", "sens_retail_opt",
              "sens_hotel_cons", "sens_hotel_opt", "B_central", "channel energy Δ% vs B_central"]
    new_11 = ["office conservative", "office optimistic", "retail conservative", "retail optimistic",
              "hotel conservative", "hotel optimistic", "central",
              "channel energy change vs central scenario (%)"]
    for old in old_11:
        rec("M11", old in other_r0_11, f"Figure_11 old text present in R0: {old!r}")
        rec("M11", old not in other_pl_11, f"Figure_11 old text absent from PL: {old!r}")
    for new in new_11:
        rec("M11", new in other_pl_11, f"Figure_11 new text present in PL: {new!r}")

    for src, base, tag in (("fig_eui_4ch.png", "Figure_08_eui_4ch", "M08"),
                            ("fig_peakhour_4ch.png", "Figure_10_peakhour_4ch", "M10")):
        _, _, other_r0 = collect_all_text(figs_seen[src])
        _, _, other_pl = collect_all_text(figs_pl[src])
        rec(tag, other_r0 == other_pl, f"{base}: full non-title text list IDENTICAL old vs new "
                                        f"(no label change intended) -- {other_r0!r}")

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
        captured = {}
        orig_save_both = m.save_both

        def _wrap(fig, out, dpi=300, _orig=orig_save_both, _cap=captured):
            _cap["fig"] = fig
            return _orig(fig, out, dpi)

        m.save_both = _wrap
        m.main()
        fig = captured["fig"]
        ht, hb, titles, flagged, kept = check_plain(fig, name, allow_ax_titles=True)
        rec("P3", not ht, f"{name}: already has no descriptive figure title (only panel labels {kept!r})")
        rec("P3", not hb, f"{name}: already has no code-label token or en/em dash ({flagged!r})")
        _plt.close(fig)

    print("\nA   plotted-data identity: R0 vs PL, per axis, every line/patch/collection array")
    s9_d = load_s9()
    d_d, tabs_d = build_frames(s9_d, AGG_NEW)
    figs_r0_mem = {}

    def _save_r0_keepfig(fig, _outdir, fname):
        figs_r0_mem[fname] = fig
        return None

    fig_eui_nt(s9_d, tabs_d["eui"], "/unused", _save_r0_keepfig)
    fig_diurnal_nt(s9_d, d_d["diurnal"], "/unused", _save_r0_keepfig)
    fig_peakhour_nt(s9_d, tabs_d["ls"], "/unused", _save_r0_keepfig)
    fig_scenario_nt(s9_d, tabs_d["scen"], "/unused", _save_r0_keepfig)
    fig_longitudinal_nt(s9_d, tabs_d["lon"], "/unused", _save_r0_keepfig)

    for src, base in STEP9_FIGS.items():
        old_data = extract_fig_data(base, figs_r0_mem[src])
        new_data = extract_fig_data(base, figs_pl[src])
        rec("A", data_equal(old_data, new_data), f"{base}: line/patch/collection arrays identical, old vs new")
    for fig in figs_r0_mem.values():
        s9_d.plt.close(fig)
    for fig in figs_seen.values():
        s9_b.plt.close(fig)

    print(f"\nCONTROLS: {N['pass']} PASS / {N['fail']} FAIL")
    if N["fail"]:
        print("NOT INSTALLED: a control failed")
        for fig in figs_pl.values():
            s9_c.plt.close(fig)
        shutil.rmtree(tmp, ignore_errors=True)
        return 1

    if not install:
        print("dry run: nothing installed (use --install)")
        for fig in figs_pl.values():
            s9_c.plt.close(fig)
        shutil.rmtree(tmp, ignore_errors=True)
        return 0

    print("\nINSTALL (md5 before -> after)")
    for src, base in STEP9_FIGS.items():
        for ext in ("png", "pdf"):
            s = os.path.join(d_pl, src) if ext == "png" else os.path.join(d_pl, src[:-4] + ".pdf")
            for dst_dir in (FIGS, SUBFIGS):
                dst = os.path.join(dst_dir, f"{base}.{ext}")
                shutil.copyfile(s, dst)
                print(f"  {os.path.relpath(dst, J3)}  {before[dst]} -> {md5(dst)}")

    for fig in figs_pl.values():
        s9_c.plt.close(fig)
    shutil.rmtree(tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
