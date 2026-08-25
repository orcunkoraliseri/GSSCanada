#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Selftest for work item 8.1.

Two halves, and the second is the one that matters.

  A. ARITHMETIC --- checks the four rulings were applied, on the manifest.
     Cheap, and it can be fooled: it re-derives what the builder derived.

  B. ROUND-TRIP --- runs EnergyPlus on every archetype IDF and reads the
     U-factor E+ itself computed back out of the tabular output.  This is the
     only check that can catch a construction that is arithmetically right and
     physically wrong: `Material:NoMass` resistance, surface films, the
     capacitive layer's own resistance and the thermal-bridging supplement all
     have to land on TABULA's number without anybody's arithmetic being
     trusted.  `FINDING 56` discipline --- a check that cannot fail is not a
     check, so half A alone would not do.

The weather file used in half B is whatever EnergyPlus ships, and that stays
true now that item 8.2 is CLOSED (`D-S8-4`).  It is deliberate, not laziness: a
U-factor round-trip must not depend on the climate, and running this half on the
study's own EPWs would let a weather regression pass itself off as an envelope
result.  The run is a validity probe, never a result.
"""

import argparse
import csv
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile

TOL_U = 0.01          # W/(m2.K), absolute, on the E+ round-trip
TOL_REL = 0.005       # 0.5 % relative, whichever is looser
TOL_AREA = 1e-6       # relative, on quantities that must be exact by algebra

# EN ISO 6946, the same values the builder subtracts.
R_SI = {"wall": 0.13, "roof": 0.10, "floor": 0.17}
R_SE = {"wall": 0.04, "roof": 0.04, "floor": 0.00}

OK, BAD = [], []


def check(name, cond, detail=""):
    (OK if cond else BAD).append((name, detail))
    print("  %-58s %s%s" % (name, "ok" if cond else "FAILED",
                            ("   " + detail) if detail and not cond else ""))


def near(a, b, tol_abs, tol_rel):
    return abs(a - b) <= max(tol_abs, tol_rel * max(abs(a), abs(b)))


# ---------------------------------------------------------------- half A
def half_a(base):
    mp = os.path.join(base, "archetype_idf_manifest.csv")
    rows = list(csv.DictReader(io.open(mp, encoding="utf-8")))
    print("\nA. ARITHMETIC  (%d archetypes)" % len(rows))

    check("A1  88 archetypes: 24 es + 32 uk + 32 it", len(rows) == 88,
          "got %d" % len(rows))
    for fold, n in (("es", 24), ("uk", 32), ("it", 32)):
        got = sum(1 for r in rows if r["fold"] == fold)
        check("A2  fold %s resolves %d cells" % (fold, n), got == n, "got %d" % got)

    # 4b: the UK matrix closes only because merged rows span their periods.
    uk = {(r["cls"], r["cell_period"]) for r in rows if r["fold"] == "uk"}
    check("A3  4b(a) fills GB.05, GB.06, GB.08 for AB",
          all(("AB", "GB.%02d" % p) in uk for p in (5, 6, 8)))
    check("A4  UK matrix is 32/32, no cell missing", len(uk) == 32, "got %d" % len(uk))
    span = [r for r in rows if re.search(r"\.\d{2}-\d{2}\.", r["code"])]
    check("A4b only merged-span rows serve cells, and only in uk: "
          "AB.02 + AB.05 + AB.06 + AB.08",
          sorted(r["idf"] for r in span) ==
          ["uk_AB_GB02.idf", "uk_AB_GB05.idf", "uk_AB_GB06.idf", "uk_AB_GB08.idf"],
          repr(sorted(r["idf"] for r in span)))
    check("A4c the three cells the table left EMPTY are filled by AB.04-08",
          all(any(r["idf"] == "uk_AB_GB%02d.idf" % p and
                  r["code"] == "GB.ENG.AB.04-08.ApartmentBuildings.SyAv.005"
                  for r in rows) for p in (5, 6, 8)))
    check("A4d 4a beats 4b on GB.04: the Gen row wins over the span row",
          any(r["idf"] == "uk_AB_GB04.idf" and ".Gen." in r["code"] for r in rows),
          [r["code"] for r in rows if r["idf"] == "uk_AB_GB04.idf"])

    # 1(a) + D-S8-3(a): footprint, height, glazing split and the SOLVED aspect.
    #
    # A5 replaces the old "aspect is 1.5 everywhere" check, which D-S8-3(a)
    # made false by design.  The invariant is no longer a shape; it is a
    # CONSERVATION, and it is conditional on how the shape was obtained:
    #   aspect_source == "tabula"    -> the modelled OPAQUE wall must equal
    #                                   TABULA's published A_Wall exactly
    #   aspect_source == "fallback"  -> the shape must be exactly 1 : 1.5
    # Both halves can fail, and they fail on different rows, so neither can be
    # satisfied by satisfying the other.  FINDING 56 discipline.
    bad_plate = bad_h = bad_win = 0
    bad_conserve, bad_fb_shape, bad_order, bad_reason = [], [], [], []
    REASONS = {"no_real_root", "glazing_does_not_fit", "no_wall_area"}
    for r in rows:
        w, d = float(r["width"]), float(r["depth"])
        a_ref, n_st, h_room = float(r["a_ref"]), float(r["n_storey"]), float(r["h_room"])
        if not near(w * d, a_ref / n_st, 0.0, TOL_AREA):
            bad_plate += 1
        if not near(float(r["height"]), n_st * h_room, 0.0, TOL_AREA):
            bad_h += 1
        if not near(float(r["win_face"]) * 4.0, float(r["win_total"]), 1e-9, TOL_AREA):
            bad_win += 1
        if w < d - 1e-9:
            bad_order.append(r["code"])          # long axis must stay E-W
        # Re-derive the opaque wall FROM W, D, H and the glazing.  Reading
        # `a_wall_box` back would make this a no-op -- the stored column
        # survives a reverted geometry untouched, and the injection battery
        # caught exactly that on 2026-08-25.
        h, wt = float(r["height"]), float(r["win_total"])
        a_wall_geom = 2.0 * (w + d) * h - wt
        if not near(a_wall_geom, float(r["a_wall_box"]), 1e-6, TOL_AREA):
            bad_conserve.append("%s manifest a_wall_box %.3f is not the box's own %.3f"
                                % (r["code"], float(r["a_wall_box"]), a_wall_geom))
        src, why = r["aspect_source"], r["aspect_fallback"]
        if src == "tabula":
            if why:
                bad_reason.append("%s: tabula row carries reason %r" % (r["code"], why))
            if not near(a_wall_geom, float(r["a_wall_tabula"]), 1e-6, TOL_AREA):
                bad_conserve.append("%s box %.3f vs TABULA %.3f"
                                    % (r["code"], a_wall_geom,
                                       float(r["a_wall_tabula"])))
        elif src == "fallback":
            if why not in REASONS:
                bad_reason.append("%s: reason %r not in %s" % (r["code"], why, REASONS))
            if not near(w / d, 1.5, 0.0, TOL_AREA):
                bad_fb_shape.append("%s W/D %.6f" % (r["code"], w / d))
        else:
            bad_reason.append("%s: aspect_source %r" % (r["code"], src))

    check("A5  D-S8-3(a) solved rows conserve TABULA's A_Wall exactly",
          not bad_conserve, "; ".join(bad_conserve[:4]))
    check("A5b D-S8-3(a) fallback rows are exactly 1 : 1.5",
          not bad_fb_shape, "; ".join(bad_fb_shape[:4]))
    check("A5c every fallback declares a reason, no solved row does",
          not bad_reason, "; ".join(bad_reason[:4]))
    check("A5d 1(a) long axis stays East-West: W >= D on every row",
          not bad_order, "; ".join(bad_order[:4]))
    check("A6  1(a) footprint = A_C_Ref / n_Storey", bad_plate == 0, "%d off" % bad_plate)
    check("A7  1(a) height = n_Storey * h_room", bad_h == 0, "%d off" % bad_h)
    check("A8  1(a) glazing split equally over 4 facades", bad_win == 0, "%d off" % bad_win)

    # The compass-sum fallback must fire, and only where the ruling said.
    fb = [r["code"] for r in rows if r["win_source"] != "A_Window_1+2"]
    check("A9  compass-sum fallback fires exactly once, on ES.ME.MFH.05",
          fb == ["ES.ME.MFH.05.Gen.ReEx.001"], repr(fb))

    # 3(a): total capacity conserved.
    bad_c = 0
    for r in rows:
        want = 45.0 * 3600.0 * float(r["a_ref"])
        got = float(r["c_areal_j"]) * float(r["a_opaque_box"])
        if not near(got, want, 1.0, TOL_AREA):
            bad_c += 1
    check("A10 3(a) c_m * A_C_Ref conserved over the opaque envelope",
          bad_c == 0, "%d off" % bad_c)
    check("A11 3(a) no construction was clamped",
          all(not r["clamped"] for r in rows),
          ";".join(r["code"] for r in rows if r["clamped"]))

    # No window may be larger than the wall that holds it.  Under D-S8-3(a)
    # this stopped being a formality: the solved boxes are elongated, and on
    # 12 archetypes a quarter of the glazing does not fit on the narrow
    # facade.  A12 is what the `glazing_does_not_fit` fallback exists to keep
    # true, so if the fallback ever stops firing this is the check that says
    # so -- not the geometry, which would still look fine.
    check("A12 no facade exceeds the 0.94 window-to-wall cap",
          all(not r["wwr_over_limit"] for r in rows),
          ";".join(r["code"] for r in rows if r["wwr_over_limit"])[:200])

    # A13 is a REGRESSION guard, not an arithmetic one: it pins the fallback
    # census that FINDING 117 is written from.  If a TABULA re-read, a
    # reselection or a units change moves any of these, the finding's numbers
    # are stale and must be re-derived before they are quoted again.
    fb = [r for r in rows if r["aspect_source"] == "fallback"]
    cen = {}
    for r in fb:
        cen[r["aspect_fallback"]] = cen.get(r["aspect_fallback"], 0) + 1
    want = {"no_real_root": 26, "glazing_does_not_fit": 12}
    check("A13 fallback census is 26 no_real_root + 12 glazing_does_not_fit",
          cen == want, "got %r" % cen)
    byfold = {}
    for r in fb:
        byfold[r["fold"]] = byfold.get(r["fold"], 0) + 1
    check("A14 fallbacks by fold are es 11, uk 10, it 17 (FINDING 117)",
          byfold == {"es": 11, "uk": 10, "it": 17}, "got %r" % byfold)
    th = sum(1 for r in fb if r["cls"] == "TH")
    check("A15 19 of the 26 no-real-root rows are terraced houses",
          th == 19 and sum(1 for r in fb
                           if r["cls"] == "TH"
                           and r["aspect_fallback"] == "no_real_root") == 19,
          "TH fallbacks %d" % th)
    return rows


# ---------------------------------------------------------------- half B
def parse_tbl(path):
    """Pull U-Factor with Film per surface out of eplustbl.csv."""
    txt = io.open(path, encoding="utf-8", errors="replace").read()
    out = {}
    for block in re.split(r"\n\s*\n", txt):
        if "U-Factor with Film" not in block:
            continue
        rdr = list(csv.reader(io.StringIO(block)))
        hdr = None
        for row in rdr:
            if any("U-Factor with Film" in c for c in row):
                hdr = row
                continue
            if hdr and len(row) >= len(hdr) and row[1].strip():
                try:
                    iw = [k for k, c in enumerate(hdr) if "U-Factor with Film" in c][0]
                    inf = [k for k, c in enumerate(hdr) if "U-Factor no Film" in c][0]
                    out[row[1].strip().upper()] = (float(row[inf]), float(row[iw]))
                except (ValueError, IndexError):
                    pass
    return out


def half_b(base, eplus, epw, limit):
    mp = os.path.join(base, "archetype_idf_manifest.csv")
    rows = list(csv.DictReader(io.open(mp, encoding="utf-8")))
    if limit:
        rows = rows[:limit]
    arch = os.path.join(base, "archetypes")
    print("\nB. ENERGYPLUS ROUND-TRIP  (%d runs, weather = %s)"
          % (len(rows), os.path.basename(epw)))
    print("   the weather file is E+'s own ON PURPOSE --- item 8.2 is closed, but a "
          "U-factor must not depend on climate")

    tmp = tempfile.mkdtemp(prefix="4j_s8_")
    failed_run, u_off, no_tbl, film_gap = [], [], [], []
    worst = (0.0, "")
    try:
        for k, r in enumerate(rows):
            d = os.path.join(tmp, "r%03d" % k)
            os.makedirs(d)
            shutil.copy(os.path.join(arch, r["idf"]), os.path.join(d, "in.idf"))
            p = subprocess.run([eplus, "-w", epw, "-d", d, "-r",
                                os.path.join(d, "in.idf")],
                               cwd=d, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
            err = os.path.join(d, "eplusout.err")
            sev = 0
            if os.path.exists(err):
                sev = io.open(err, encoding="utf-8", errors="replace").read().count("** Severe")
            if p.returncode != 0 or sev:
                failed_run.append((r["idf"], p.returncode, sev))
                continue
            tbl = os.path.join(d, "eplustbl.csv")
            if not os.path.exists(tbl):
                no_tbl.append(r["idf"])
                continue
            got = parse_tbl(tbl)
            uw = float(r["u_wall"]) + float(r["dub"])
            ur = float(r["u_roof"]) + float(r["dub"])
            targets = {"W_SOUTH": (uw, "wall"), "W_EAST": (uw, "wall"),
                       "W_NORTH": (uw, "wall"), "W_WEST": (uw, "wall"),
                       "S_ROOF": (ur, "roof")}
            for surf, (u_tab, kind) in targets.items():
                if surf not in got:
                    continue
                nofilm, withfilm = got[surf]
                # what the builder actually controls: the construction alone
                want_nofilm = 1.0 / (1.0 / u_tab - R_SI[kind] - R_SE[kind])
                dev = abs(nofilm - want_nofilm)
                if dev > worst[0]:
                    worst = (dev, "%s %s: E+ %.4f vs required %.4f"
                             % (r["idf"], surf, nofilm, want_nofilm))
                if not near(nofilm, want_nofilm, TOL_U, TOL_REL):
                    u_off.append((r["idf"], surf, nofilm, want_nofilm))
                # what E+ will actually simulate, against TABULA's own number
                film_gap.append((withfilm - u_tab) / u_tab)
            if (k + 1) % 20 == 0:
                print("   ... %d/%d" % (k + 1, len(rows)))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    check("B1  every archetype IDF runs, 0 severe errors",
          not failed_run, "; ".join("%s rc=%s sev=%s" % f for f in failed_run[:5]))
    check("B2  every run writes a tabular envelope summary",
          not no_tbl, "; ".join(no_tbl[:5]))
    check("B3  E+'s construction U (no film) is 1/(1/U_TABULA - Rsi - Rse)",
          not u_off,
          "; ".join("%s %s E+ %.3f vs %.3f" % u for u in u_off[:5]))
    print("   worst deviation seen: %.5f W/(m2.K)   %s" % worst)
    if film_gap:
        film_gap.sort()
        n = len(film_gap)
        print("\n   B4  NOT a pass/fail --- the film-convention gap, measured.")
        print("       E+ reports and simulates with its OWN surface films; "
              "TABULA's U is EN ISO 6946 with fixed 0.13 / 0.04.")
        print("       (U_Eplus_withfilm - U_TABULA) / U_TABULA over %d surfaces:"
              % n)
        print("       min %+.2f %%   median %+.2f %%   max %+.2f %%"
              % (100 * film_gap[0], 100 * film_gap[n // 2], 100 * film_gap[-1]))
        print("       This does not go away and must be declared. It is NOT "
              "uniform: it grows with U, so it is correlated with")
        print("       construction period, and through the period mix with "
              "country. See FINDING 111.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("--eplus", default=r"C:\EnergyPlusV24-2-0\energyplus.exe")
    ap.add_argument("--epw", default=None)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--skip-eplus", action="store_true")
    a = ap.parse_args()

    half_a(a.base)
    if not a.skip_eplus:
        epw = a.epw or os.path.join(os.path.dirname(a.eplus), "WeatherData",
                                    "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")
        if os.path.exists(a.eplus) and os.path.exists(epw):
            half_b(a.base, a.eplus, epw, a.limit)
        else:
            check("B0  EnergyPlus and a weather file are available", False,
                  "%s / %s" % (a.eplus, epw))

    print("\n%d ok, %d FAILED" % (len(OK), len(BAD)))
    for n, d in BAD:
        print("  FAILED %s  %s" % (n, d))
    return 1 if BAD else 0


if __name__ == "__main__":
    sys.exit(main())
