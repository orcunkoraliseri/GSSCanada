# -*- coding: utf-8 -*-
"""5J Step 4: condense the scorer outputs of the perturbation rows into before/after lines (Speed job only; reads only out/score_*.txt)."""
import re, sys, collections
OUT = "/speed-scratch/o_iseri/5J/freeze/out/"
ROWS = [("good", "sc_good"), ("1 delete one run", "sc_deleted"), ("2 training mean per hour of year", "sc_trainmean"),
        ("3 building mean per flat (occupancy effect zero)", "sc_bldmean"), ("4 shift by 2 hours", "sc_shift2"),
        ("5 control = good stand-in", "sc_ctrlgood")]
GATES = ["G5J.1", "G5J.2", "G5J.3", "G5J.4", "G5J.5"]
pat = re.compile(r"^GATE (\S+) country=(\S+) class=(\S+) target=(\S+) VERDICT=(\S+) ?(.*)$")


def parse(tag):
    d = {}
    for ln in open(OUT + "score_%s.txt" % tag, encoding="utf-8", errors="replace"):
        m = pat.match(ln.rstrip("\n"))
        if m:
            d[(m.group(1), m.group(2), m.group(3), m.group(4))] = (m.group(5), m.group(6))
    return d


def main_eff():
    """fix 1 (additive): before/after lines on effgood, premise tables, CHECK 2.3 + SUMMARY + exit of EVERY tag."""
    EROWS = [("1 delete one run (effdeleted)", "sc_effdeleted"), ("2 training mean (reused sc_trainmean, base-free)", "sc_trainmean"),
             ("3 effect-good building mean (effbldmean)", "sc_effbldmean"), ("4 effgood shifted by 2 h (effshift2)", "sc_effshift2"),
             ("5 control = effgood (effctrl)", "sc_effctrl"), ("planted high floor (highfloor)", "sc_highfloor")]
    ebase = parse("sc_effgood")
    print("=== effgood (tag sc_effgood) SUMMARY lines")
    for ln in open(OUT + "score_sc_effgood.txt", encoding="utf-8", errors="replace"):
        if ln.startswith(("SUMMARY", "SCORER_EXIT", "SELFTEST", "CHECK 2.3")) or "SELFTEST" in ln[:12]:
            print("  " + ln.rstrip())
    for name, tag in EROWS:
        try:
            d = parse(tag)
        except Exception as e:
            print("ROW %s: no output (%s)" % (name, e)); continue
        print("=== ROW %s (tag %s)" % (name, tag))
        for g in GATES:
            c = collections.Counter(v[0] for k, v in d.items() if k[0] == g)
            b = collections.Counter(v[0] for k, v in ebase.items() if k[0] == g)
            changed = sorted((k[1:], ebase[k][0], v[0]) for k, v in d.items() if k[0] == g and k in ebase and ebase[k][0] != v[0])
            print("  %s before(effgood) PASS=%d FAIL=%d NE=%d | after PASS=%d FAIL=%d NE=%d | cells changed: %d" %
                  (g, b["PASS"], b["FAIL"], b["NOT_EVALUABLE"], c["PASS"], c["FAIL"], c["NOT_EVALUABLE"], len(changed)))
            if 0 < len(changed) <= 40:
                for ch in changed:
                    print("      changed %s: %s -> %s" % (" ".join(ch[0]), ch[1], ch[2]))
    for tag in ("sc_effbldmean", "sc_bldmean"):
        d = parse(tag)
        print("=== G5J.2 per class, country, target under %s (premise, val 2.1b)" % tag)
        for k in sorted(k for k in d if k[0] == "G5J.2"):
            print("    %s %s %s %s %s" % (k[2], k[1], k[3], d[k][0], d[k][1]))
    for tag in ("sc_good", "sc_effgood", "sc_highfloor", "sc_effctrl"):
        d = parse(tag)
        print("=== G5J.3 (and G5J.4 for effctrl) lines of %s" % tag)
        for k in sorted(k for k in d if k[0] == "G5J.3" or (tag == "sc_effctrl" and k[0] == "G5J.4")):
            print("  %s %s %s %s %s %s" % (k[0], k[2], k[1], k[3], d[k][0], d[k][1]))
    print("=== CHECK 2.3 / SUMMARY / SCORER_EXIT of EVERY tag")
    for tag in ("sc_pipetest", "sc_good", "sc_deleted", "sc_trainmean", "sc_bldmean", "sc_shift2", "sc_ctrlgood", "sc_crash", "sc_highk",
                "sc_effgood", "sc_effdeleted", "sc_effbldmean", "sc_effshift2", "sc_effctrl", "sc_highfloor"):
        try:
            for ln in open(OUT + "score_%s.txt" % tag, encoding="utf-8", errors="replace"):
                if ln.startswith(("CHECK 2.3", "SUMMARY PASS", "SCORER_EXIT")):
                    print("  [%s] %s" % (tag, ln.rstrip()[:230]))
        except Exception as e:
            print("  [%s] no output (%s)" % (tag, e))


if "--eff" in sys.argv:
    main_eff()
    sys.exit(0)

base = parse("sc_good")
for name, tag in ROWS:
    try:
        d = parse(tag)
    except Exception as e:
        print("ROW %s: no output (%s)" % (name, e)); continue
    print("=== ROW %s (tag %s)" % (name, tag))
    for g in GATES:
        c = collections.Counter(v[0] for k, v in d.items() if k[0] == g)
        b = collections.Counter(v[0] for k, v in base.items() if k[0] == g)
        changed = sorted(k[1:] for k, v in d.items() if k[0] == g and k in base and base[k][0] != v[0])
        print("  %s before(good) PASS=%d FAIL=%d NE=%d | after PASS=%d FAIL=%d NE=%d | cells whose verdict changed: %d" %
              (g, b["PASS"], b["FAIL"], b["NOT_EVALUABLE"], c["PASS"], c["FAIL"], c["NOT_EVALUABLE"], len(changed)))
    if tag == "sc_bldmean":
        print("  G5J.2 verdict per class, country, target under the building-mean stand-in (the premise, val 2.1b):")
        for k in sorted(k for k in d if k[0] == "G5J.2"):
            print("    %s %s %s %s %s" % (k[2], k[1], k[3], d[k][0], d[k][1]))
print("=== G5J.3 lines of the good stand-in")
for k in sorted(k for k in base if k[0] == "G5J.3"):
    print("  %s %s %s %s %s" % (k[2], k[1], k[3], base[k][0], base[k][1]))
