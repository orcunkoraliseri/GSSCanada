# -*- coding: utf-8 -*-
"""4thJ_step10_weather_year.py -- apply the D-S10-1 ruling (2026-08-26, section 6).

The author ruled Option (A): pin the majority calendar year per fold --
    es -> 2010,  uk -> 2014,  it -> 2014
and directed (directive 2) that the section 1.4 value maps be applied to ENRICH THE
METADATA "without altering the underlying harmonised schema or invalidating Step 2
gates".

So this tool writes a SIDECAR and never touches `harmonised_*.parquet`. Gate W10.1
proves that by hashing the three inputs before and after and refusing on any change:
an edit in place would move Step 2's gate hashes and, downstream, the frozen
`corpus_md5 ca89d2295603c547f2384a40dd1909ba`.

Outputs, all under Step10_docs/outputs_step10/:
    weather_year_ruling.json        the fold -> EPW year pinning OpenUBEM's --year consumes
    diary_year_<fold>.parquet       per-diary calendar year and the BASIS for it
    weather_year_report.txt         the gate report, including the perturbation battery

Run:  python tools/4thJ_step10_weather_year.py            (build + gates)
      python tools/4thJ_step10_weather_year.py --perturb  (gates + prove they can fail)
"""
import hashlib
import io
import json
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
HARM = os.path.join(ROOT, "Step2_docs", "outputs_step2")
OUT = os.path.join(ROOT, "Step10_docs", "outputs_step10")
PREREG = os.path.join(ROOT, "Step6_docs", "outputs_step6", "prereg.md")
DOC = "IMP/docs/2026-08-26_D-S10-1_the-weather-year-is-recoverable.md"

RAW = r"C:\Users\o_iseri\Desktop\GSSCanada\_local_runs\4J\raw"
UK_TAB = os.path.join(RAW, "uk", "unpacked", "UK-TUS", "UKDA-8128-tab", "tab",
                      "uktus15_diary_ep_long.tab")

PREREG_MD5 = "e4243e07cdd80c9c846b91f40e3e8c45"

# ---- the ruling, section 6 table, transcribed once and asserted against the data ----
RULING = {"es": 2010, "uk": 2014, "it": 2014}

# ---- the section 1.4 value maps. `None` marks the one code that straddles. ----
# es: INE record layout -- TRIM 4 is "4o Trimestre (de 2009)", 1/2/3 are "de 2010".
#     Fieldwork 1 Oct 2009 - 30 Sep 2010, so the mapping is total and exact.
ES_MAP = {1: 2010, 2: 2010, 3: 2010, 4: 2009}
# it: meseri 1 = Nov, Dec, Jan; 2 = Feb-Apr; 3 = May-Jul; 4 = Aug-Oct, against the
#     ISTAT window 1 Nov 2013 - 31 Oct 2014. Only meseri 1 crosses the year boundary,
#     and the daily-diary delivery ships no month field to split it.
IT_MAP = {1: None, 2: 2014, 3: 2014, 4: 2014}

FAILURES = []


def gate(gid, ok, msg):
    tag = "PASS" if ok else "FAIL"
    line = "%-8s %s  %s" % (gid, tag, msg)
    print(line)
    if not ok:
        FAILURES.append(line)
    return line


def md5_of_file(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def harm_path(fold):
    return os.path.join(HARM, "harmonised_%s.parquet" % fold)


# --------------------------------------------------------------------------- build

def build_es(d, season_map=None):
    """es: pure value map on strat_season_raw. No join, no re-run, total coverage."""
    m = ES_MAP if season_map is None else season_map
    q = d.strat_season_raw.astype(int)
    out = d[["hid", "pid", "diary_day"]].copy()
    out["season_code"] = q.values
    out["diary_year"] = q.map(m).values
    out["basis"] = "exact:TRIM value label + INE fieldwork window"
    return out.drop_duplicates(["hid", "pid", "diary_day"])


def build_it(d, season_map=None):
    """it: exact for meseri 2/3/4; meseri 1 straddles and is ABSORBED per ruling 3."""
    m = IT_MAP if season_map is None else season_map
    q = d.strat_season_raw.astype(int)
    out = d[["hid", "pid", "diary_day"]].copy()
    out["season_code"] = q.values
    y = q.map(m)
    out["diary_year"] = y.values
    out["basis"] = ["exact:meseri + ISTAT window" if pd.notna(v)
                    else "absorbed:meseri=1 straddles Nov2013-Jan2014, no month field"
                    for v in y]
    # the ruling: the straddling quarter is absorbed into the pinned majority year
    out.loc[out.diary_year.isna(), "diary_year"] = RULING["it"]
    out["diary_year"] = out.diary_year.astype(int)
    return out.drop_duplicates(["hid", "pid", "diary_day"])


def build_uk(d, break_key=False):
    """uk: join the DELIVERED per-diary `dyear`. hid IS serial, pid IS serial_pnum."""
    raw = pd.read_csv(UK_TAB, sep="\t", usecols=["serial", "pnum", "daynum", "dyear"],
                      low_memory=False).drop_duplicates(["serial", "pnum", "daynum"])
    raw["k"] = (raw.serial.astype(str) + "_" + raw.pnum.astype(str)
                + "_" + raw.daynum.astype(str))
    lut = dict(zip(raw.k, raw.dyear))

    out = d[["hid", "pid", "diary_day"]].drop_duplicates().copy()
    suffix = "_X" if break_key else ""
    out["k"] = (out.pid.astype(str) + suffix + "_" + out.diary_day.astype(str))
    out["diary_year"] = out.k.map(lut)
    out["season_code"] = -1  # uk's harmonised season field is a month, not the basis
    out["basis"] = "exact:delivered dyear, joined on (serial, pnum, daynum)"
    return out.drop(columns=["k"])


# --------------------------------------------------------------------------- gates

def run_gates(built, before, perturbed_label=None):
    del FAILURES[:]
    lines = []
    head = "PERTURBATION: %s" % perturbed_label if perturbed_label else "REAL RUN"
    print("\n=== %s ===" % head)
    lines.append("=== %s ===" % head)

    # W10.1 -- the harmonised corpus was not touched
    same = all(md5_of_file(harm_path(f)) == before[f] for f in ("es", "uk", "it"))
    lines.append(gate("W10.1", same,
                      "harmonised_*.parquet md5 unchanged (sidecar only, Step 2 gates intact)"))

    # W10.2 -- es map is total, and reproduces the raw share
    es = built["es"]
    tot = len(es)
    n2010 = int((es.diary_year == 2010).sum())
    share = 100.0 * n2010 / tot
    ok = es.diary_year.notna().all() and set(es.season_code) <= {1, 2, 3, 4}
    lines.append(gate("W10.2", ok,
                      "es map total: %d/%d diaries carry a year, codes %s"
                      % (int(es.diary_year.notna().sum()), tot, sorted(set(es.season_code)))))
    lines.append(gate("W10.3", abs(share - 76.8) <= 1.0,
                      "es 2010 share %.1f %% (raw deliveries measured 76.8 %%, tol 1.0 pp)"
                      % share))

    # W10.4 -- uk join is complete
    uk = built["uk"]
    unmatched = int(uk.diary_year.isna().sum())
    lines.append(gate("W10.4", unmatched == 0,
                      "uk join unmatched diaries = %d of %d" % (unmatched, len(uk))))
    if unmatched == 0:
        s14 = 100.0 * float((uk.diary_year == 2014).sum()) / len(uk)
        lines.append(gate("W10.5", abs(s14 - 58.1) <= 2.0,
                          "uk 2014 share %.1f %% on the harmonised subset "
                          "(raw deliveries measured 58.1 %%, tol 2.0 pp)" % s14))
    else:
        lines.append(gate("W10.5", False, "uk share NOT CHECKED -- the join failed first"))

    # W10.6 -- it: exact where it can be, flagged where it cannot
    it = built["it"]
    absorbed = int(it.basis.str.startswith("absorbed").sum())
    ok = it.diary_year.notna().all() and (it.loc[it.season_code != 1, "diary_year"] == 2014).all()
    lines.append(gate("W10.6", ok,
                      "it meseri 2/3/4 all 2014 exactly; meseri=1 ABSORBED on %d of %d "
                      "diaries (%.1f %%) per ruling 3"
                      % (absorbed, len(it), 100.0 * absorbed / len(it))))

    # W10.7 -- the pinned year IS the measured majority in every fold
    rows = []
    for f in ("es", "uk", "it"):
        b = built[f]
        vc = b.diary_year.value_counts()
        maj = int(vc.idxmax()) if len(vc) else -1  # -1: the fold carries no year at all
        rows.append((f, RULING[f], maj, maj == RULING[f]))
    lines.append(gate("W10.7", all(r[3] for r in rows),
                      "pinned == measured majority: "
                      + ", ".join("%s pinned %d / majority %d" % (r[0], r[1], r[2]) for r in rows)))

    # W10.8 -- prereg is frozen
    live = md5_of_file(PREREG) if os.path.exists(PREREG) else "MISSING"
    lines.append(gate("W10.8", live == PREREG_MD5,
                      "prereg.md md5 live=%s recorded=%s" % (live, PREREG_MD5)))
    return lines


def main():
    perturb = "--perturb" in sys.argv
    if not os.path.isdir(OUT):
        os.makedirs(OUT)

    before = {f: md5_of_file(harm_path(f)) for f in ("es", "uk", "it")}
    print("input md5: " + ", ".join("%s=%s" % (f, before[f][:8]) for f in before))

    cols = ["hid", "pid", "diary_day", "strat_season_raw"]
    harm = {f: pd.read_parquet(harm_path(f), columns=cols) for f in ("es", "uk", "it")}

    built = {"es": build_es(harm["es"]),
             "uk": build_uk(harm["uk"]),
             "it": build_it(harm["it"])}

    report = run_gates(built, before)
    real_failed = list(FAILURES)

    # ---- the perturbation battery. A gate nobody has seen fail is not a gate. ----
    if perturb:
        report.append("")
        report.append("=== PERTURBATION BATTERY -- each must FELL its named gate ===")
        cases = [
            ("es map flipped: TRIM 4 -> 2010 (the 2009 quarter erased)", "W10.3",
             {"es": build_es(harm["es"], {1: 2010, 2: 2010, 3: 2010, 4: 2010}),
              "uk": built["uk"], "it": built["it"]}),
            ("uk join key broken: pid + '_X'", "W10.4",
             {"es": built["es"], "uk": build_uk(harm["uk"], break_key=True),
              "it": built["it"]}),
            ("it map flipped: meseri 2/3/4 -> 2013", "W10.6",
             {"es": built["es"], "uk": built["uk"],
              "it": build_it(harm["it"], {1: None, 2: 2013, 3: 2013, 4: 2013})}),
        ]
        for label, target, b in cases:
            run_gates(b, before, perturbed_label=label)
            hit = any(l.startswith(target) for l in FAILURES)
            report.append("%-46s -> %s %s" % (target, "FELL as required" if hit
                                              else "DID NOT FIRE  <-- the gate is asleep",
                                              "| " + label))
            if not hit:
                real_failed.append("PERTURBATION %s did not fell %s" % (label, target))

        # a control that must stay green: mis-pinning is caught by W10.7, not by luck
        saved = RULING["uk"]
        RULING["uk"] = 2015
        run_gates(built, before, perturbed_label="uk mis-pinned to 2015 (the minority year)")
        hit = any(l.startswith("W10.7") for l in FAILURES)
        RULING["uk"] = saved
        report.append("%-46s -> %s | uk mis-pinned to 2015"
                      % ("W10.7", "FELL as required" if hit else "DID NOT FIRE"))
        if not hit:
            real_failed.append("PERTURBATION uk mis-pin did not fell W10.7")

    if real_failed:
        print("\nREFUSING TO WRITE -- %d gate(s) failed:" % len(real_failed))
        for l in real_failed:
            print("  " + l)
        return 1

    # ---------------------------------------------------------------- write sidecar
    summary = {}
    for f in ("es", "uk", "it"):
        b = built[f].copy()
        b["diary_year"] = b.diary_year.astype(int)
        b.to_parquet(os.path.join(OUT, "diary_year_%s.parquet" % f), index=False)
        vc = b.diary_year.value_counts().sort_index()
        summary[f] = {"n_diaries": int(len(b)),
                      "by_year": {str(k): int(v) for k, v in vc.items()},
                      "pinned_year": RULING[f],
                      "pinned_share_pct": round(100.0 * float((b.diary_year == RULING[f]).sum())
                                                / len(b), 2),
                      "absorbed_diaries": int(b.basis.str.startswith("absorbed").sum())}

    ruling = {
        "decision": "D-S10-1",
        "status": "RULED_PINNED",
        "ruled_on": "2026-08-26",
        "ruled_by": "the author",
        "option": "A -- pin the majority calendar year per fold",
        "document": DOC,
        "epw_year": dict(RULING),
        "supersedes": "FINDING EU-S2-03 / MVP 12.8 RULED_NOT_PINNED for es, uk, it",
        "openubem_contract_freeze": "LIFTED",
        "note_it": ("meseri=1 (Nov 2013 - Jan 2014) straddles and the ISTAT daily-diary "
                    "delivery ships no month field; per ruling 3 it is ABSORBED into the "
                    "pinned majority year 2014, not interpolated"),
        "note_uk": ("58.1 % is a clear but not decisive majority; pinned to 2014 per "
                    "ruling 2 to keep one convention across all three folds"),
        "measured": summary,
        "prereg_md5": PREREG_MD5,
        "harmonised_md5": before,
        "corpus_untouched": True,
    }
    with io.open(os.path.join(OUT, "weather_year_ruling.json"), "w", encoding="utf-8") as fh:
        fh.write(json.dumps(ruling, indent=2, ensure_ascii=False))

    report.append("")
    report.append("WROTE weather_year_ruling.json and diary_year_{es,uk,it}.parquet")
    for f in ("es", "uk", "it"):
        report.append("  %s: pinned %d, %s of %d diaries (%.2f %%), absorbed %d"
                      % (f, RULING[f], summary[f]["by_year"].get(str(RULING[f])),
                         summary[f]["n_diaries"], summary[f]["pinned_share_pct"],
                         summary[f]["absorbed_diaries"]))
    with io.open(os.path.join(OUT, "weather_year_report.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(report) + "\n")
    print("\n".join(report[-5:]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
