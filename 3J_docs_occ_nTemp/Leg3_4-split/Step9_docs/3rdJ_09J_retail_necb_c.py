#!/usr/bin/env python3
"""V2-D9: give the retail channel NECB's RETAIL space type instead of the OFFICE one it runs today.

TWO DEFECTS, DELIBERATELY SEPARABLE (`--density-only` / `--schedule-only`), because they are very
different sizes and folding them into one edit would make the smaller one unfalsifiable.

1. DENSITY. All four retail `People` objects carry 0.040015 person/m2 = 24.97 m2/person, which is
   NECB's `Office (WholeBuilding)` value (3.72 occ/1000 ft2). NECB `Retail - sales` is 3.10, i.e.
   29.97 m2/person = 0.033368 person/m2. Retail is modelled ~20 % more crowded than the standard it
   claims to follow. This is the LARGE half: it touches 100 % of the channel.

2. SCHEDULE. `NECB-C-*` is absent from the IDF entirely (`grep -c "NECB-C-"` = 0). But three of the
   four retail `People` objects already carry an INJECTED schedule that supersedes NECB, so the swap
   only reaches `LargeHotel Retail` -- 368 m2, 7.8 % of the channel. This is the SMALL half, and its
   annual integral barely moves: NECB-A is 2,245 occupied-hour equivalents against NECB-C's 2,269.
   What changes is the DISTRIBUTION: NECB-A is shut every Saturday and Sunday, NECB-C peaks at 0.9 on
   Saturday. A retail floor closed at weekends is the defect worth fixing here, not the annual total.

WHAT THIS SCRIPT WILL NOT DO. It does not touch the injected schedules, lighting, or equipment. It
does not touch any non-retail channel. `--verify` re-reads its own output and refuses if either is
false, because "confined to retail" is the claim most worth failing on.

    python 3rdJ_09J_retail_necb_c.py <src.idf> <dst.idf> [--density-only|--schedule-only] [--verify]
"""
import json
import os
import re
import sys

# NECB 2011 Table A-8.4.3.2.(1) space types, via f8_necb_schedule_evidence/space_types_NECB2011.json
OFFICE_DENSITY = 0.040015          # person/m2, = 3.72 occ/1000 ft2, what retail runs today
RETAIL_OCC_PER_1000FT2 = 3.10      # NECB `Retail - sales`
FT2_PER_1000 = 1000.0 / 10.7639104
RETAIL_DENSITY = RETAIL_OCC_PER_1000FT2 / FT2_PER_1000     # -> 0.033368 person/m2

RETAIL_ZONELISTS = ("Retail Back_Space", "Retail Retail", "Retail Point_of_Sale",
                    "LargeHotel Retail")
UNINJECTED_ZONELIST = "LargeHotel Retail"
NECB_C = "NECB-C-Occupancy"
NECB_A = "NECB-A-Occupancy"

_HERE = os.path.dirname(os.path.abspath(__file__))
_SCHED_JSON = os.path.join(_HERE, "..", "..", "improvements", "v2",
                           "f8_necb_schedule_evidence", "sched_NECB2011.json")

_DAYTYPE_IDF = {"Default|Wkdy": "Weekdays", "Sat": "Saturday",
                "Sun|Hol": "Sunday Holidays AllOtherDays"}


def people_blocks(txt):
    """[(start, end, body)] for each People object. Objects are ';'-terminated, not blank-line
    separated -- an IDF written by a different tool may not have the blank lines at all."""
    out = []
    for m in re.finditer(r"(?im)^People,\s*$", txt):
        end = txt.find(";", m.start())
        if end < 0:
            raise SystemExit("REFUSING: unterminated People object at offset %d" % m.start())
        end = txt.find("\n", end) + 1
        out.append((m.start(), end, txt[m.start():end]))
    return out


def field(body, label):
    m = re.search(r"^\s*([^,;!]*?)\s*[,;]\s*!-\s*" + re.escape(label), body, re.M)
    return m.group(1) if m else None


def build_necb_c_schedule():
    """Emit `NECB-C-Occupancy` as Schedule:Compact, straight from the shipped NECB library.

    Values are NOT typed in here. They are read from the same evidence file V2-F8 was closed on, so
    this cannot drift from the source it claims -- and if the file is missing the script refuses
    rather than falling back to a hand-copied profile.
    """
    if not os.path.isfile(_SCHED_JSON):
        raise SystemExit("REFUSING: NECB schedule library not found at %s -- refusing to "
                         "hand-write the profile" % _SCHED_JSON)
    with open(_SCHED_JSON) as f:
        rows = json.load(f)["tables"]["schedules"]["table"]
    got = {r["day_types"]: r["values"] for r in rows if r["name"] == NECB_C}
    missing = [d for d in _DAYTYPE_IDF if d not in got]
    if missing:
        raise SystemExit("REFUSING: %s missing day types %s in the library" % (NECB_C, missing))
    lines = ["Schedule:Compact,", "    %s," % NECB_C, "    Fraction,", "    Through: 12/31,"]
    for key, idf_day in _DAYTYPE_IDF.items():
        vals = got[key]
        if len(vals) != 24:
            raise SystemExit("REFUSING: %s/%s has %d values, expected 24" % (NECB_C, key, len(vals)))
        lines.append("    For: %s," % idf_day)
        for h, v in enumerate(vals):
            lines.append("    Until: %02d:00," % (h + 1))
            lines.append("    %.4f," % v)
    lines[-1] = lines[-1].rstrip(",") + ";"
    return "\n".join(lines) + "\n"


def convert(src, dst, do_density=True, do_schedule=True):
    with open(src, errors="replace") as f:
        txt = f.read()

    # Asked of the ORIGINAL text, before any edit. The first version asked it after rewriting the
    # People objects and so matched the `NECB-C-Occupancy,  !- Number of People Schedule Name` line
    # this run had just written -- a guard that fires on its own output, refusing every clean IDF.
    # A schedule DEFINITION is what must be absent, so the pattern is anchored to Schedule:Compact.
    already = re.search(r"(?im)^Schedule:Compact,\s*\n\s*%s\s*," % re.escape(NECB_C), txt)

    blocks = people_blocks(txt)
    retail = []
    for s, e, body in blocks:
        zl = (field(body, "Zone or ZoneList or Space or SpaceList Name") or "").strip()
        if zl in RETAIL_ZONELISTS:
            retail.append((s, e, body, zl))
    if len(retail) != len(RETAIL_ZONELISTS):
        raise SystemExit("REFUSING: expected People objects on %d retail ZoneLists, found %d (%s). "
                         "The zone naming changed and a blind edit would miss or over-reach."
                         % (len(RETAIL_ZONELISTS), len(retail), [r[3] for r in retail]))

    report = []
    n_swap = 0
    # Rewrite back-to-front so earlier offsets stay valid.
    for s, e, body, zl in sorted(retail, key=lambda r: -r[0]):
        new = body
        if do_density:
            dens = field(body, "People per Floor Area")
            if dens is None or abs(float(dens) - OFFICE_DENSITY) > 1e-9:
                raise SystemExit("REFUSING: %s carries People per Floor Area %r, not the office "
                                 "value %.6f this fix is defined against" % (zl, dens, OFFICE_DENSITY))
            new = re.sub(r"^(\s*)[^,;!]*?(\s*,\s*!-\s*People per Floor Area)",
                         lambda m: "%s%.6f%s" % (m.group(1), RETAIL_DENSITY, m.group(2)),
                         new, count=1, flags=re.M)
        sched = (field(body, "Number of People Schedule Name") or "").strip()
        swapped = False
        if do_schedule:
            # The rule is "a retail zone still on the OFFICE NECB schedule gets the RETAIL one",
            # not "this named zone". Zone names were hardcoded at first, which was wrong in both
            # directions: injected arms leave `LargeHotel Retail` uninjected while the uninjected
            # `Default_NECB` control has ALL FOUR on NECB-A, and a name-keyed rule would have
            # converted one quarter of the control and called it done.
            if sched == NECB_A:
                new = new.replace(NECB_A, NECB_C, 1)
                swapped = True
            elif not sched.startswith("MXU_"):
                raise SystemExit("REFUSING: %s carries schedule %r -- neither %s nor an injected "
                                 "MXU_ schedule. Unknown state; not guessing." % (zl, sched, NECB_A))
        report.append((zl, body != new, sched, swapped))
        n_swap += 1 if swapped else 0
        txt = txt[:s] + new + txt[e:]

    if do_schedule:
        if already:
            raise SystemExit("REFUSING: a %s schedule definition is already present -- this IDF was "
                             "already converted" % NECB_C)
        txt += "\n" + build_necb_c_schedule()

    with open(dst, "w") as f:
        f.write(txt)
    return report, n_swap


def verify(src, dst, do_density=True, do_schedule=True, n_swap=0):
    """Re-read the OUTPUT. The claim being tested is 'confined to retail', and the only way that can
    fail honestly is by counting every line that differs, not by trusting the edit path."""
    a = open(src, errors="replace").read().split("\n")
    b = open(dst, errors="replace").read().split("\n")
    ok = True

    # Every changed line, ignoring the appended schedule block.
    import difflib
    changed = [l for l in difflib.unified_diff(a, b, n=0, lineterm="")
               if l.startswith(("+", "-")) and not l.startswith(("+++", "---"))]
    sched_lines = build_necb_c_schedule().count("\n") if do_schedule else 0
    # Substantive == carries a `!- <field>` comment. The appended schedule block is emitted without
    # any, so this separates the two cleanly. The first version instead pattern-matched the appended
    # block's numeric lines -- and `[0-9.]+[,;]` also matched the NEW `0.033368,` density lines,
    # so the verifier hid four of the ten edits it existed to count and reported 6/10 as a failure.
    # A verifier that UNDER-counts is worse than one that over-counts: it fails honest output, and
    # the natural next move is to "fix" the edit that was never wrong.
    edits = [l for l in changed if "!-" in l]
    exp_density = len(RETAIL_ZONELISTS) * 2 if do_density else 0     # one - and one + per object
    exp_sched = 2 * n_swap if do_schedule else 0
    n_exp = exp_density + exp_sched
    print("  [%s] exactly %d substantive line edits (%d density, %d schedule); found %d"
          % ("PASS" if len(edits) == n_exp else "FAIL", n_exp, exp_density, exp_sched, len(edits)))
    ok &= len(edits) == n_exp
    for l in edits:
        print("        %s" % l.strip()[:110])

    # No non-retail People object may have moved.
    pa = {(field(x[2], "Zone or ZoneList or Space or SpaceList Name") or "").strip(): x[2]
          for x in people_blocks("\n".join(a))}
    pb = {(field(x[2], "Zone or ZoneList or Space or SpaceList Name") or "").strip(): x[2]
          for x in people_blocks("\n".join(b))}
    moved = [z for z in pa if pa[z] != pb.get(z)]
    stray = [z for z in moved if z not in RETAIL_ZONELISTS]
    print("  [%s] no non-retail People object changed -- %d People objects, %d moved, %d stray"
          % ("PASS" if not stray else "FAIL", len(pa), len(moved), len(stray)))
    ok &= not stray
    if do_schedule:
        print("  [%s] NECB-C-Occupancy appended (%d lines)"
              % ("PASS" if NECB_C in "\n".join(b) else "FAIL", sched_lines))
        ok &= NECB_C in "\n".join(b)
    return ok


def main():
    a = sys.argv[1:]
    flags = {x for x in a if x.startswith("--")}
    pos = [x for x in a if not x.startswith("--")]
    if len(pos) != 2:
        raise SystemExit("usage: %s <src.idf> <dst.idf> [--density-only|--schedule-only] [--verify]"
                         % sys.argv[0])
    do_d = "--schedule-only" not in flags
    do_s = "--density-only" not in flags
    src, dst = pos
    print("V2-D9  retail -> NECB `Retail - sales`   density=%s schedule=%s" % (do_d, do_s))
    print("  density %.6f -> %.6f person/m2  (%.2f -> %.2f m2/person)"
          % (OFFICE_DENSITY, RETAIL_DENSITY, 1 / OFFICE_DENSITY, 1 / RETAIL_DENSITY))
    rep, n_swap = convert(src, dst, do_d, do_s)
    for zl, ch, sched, sw in sorted(rep):
        print("  %-24s was=%-38s %s%s" % (zl, sched[:38], "edited" if ch else "unchanged",
                                          "  [A->C]" if sw else ""))
    print("  schedule swaps: %d of %d retail ZoneLists" % (n_swap, len(RETAIL_ZONELISTS)))
    if "--verify" in flags:
        print("")
        sys.exit(0 if verify(src, dst, do_d, do_s, n_swap) else 1)


if __name__ == "__main__":
    main()
