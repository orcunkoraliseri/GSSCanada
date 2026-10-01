# -*- coding: utf-8 -*-
"""5J Step 6 part B, collect job (Speed CPU job, Spain + Italy only). Reads ONLY the printed score files of the one scoring job
(score_<tag>.txt, stdout_reported_*.txt, openlog_<tag>.tsv = file names only, exit_<tag>.txt, jobid_<tag>.txt). It never opens a
truth or prediction file. Writes scores.parquet, SUMMARY.txt, bootstrap_intervals.csv, claims.txt and collect.log to --out.

Usage: s6_collect.py --score-dir /speed-scratch/o_iseri/5J/test/score --out /speed-scratch/o_iseri/5J/test/score_collect --job <scoring job id>
Exit: 0 all checks pass; 3 some check FAILED (outputs are still written); 5 a planted fault did NOT fire (the checks are not trusted).
A verdict is copied exactly as the scorer printed it.
"""
import argparse, io, os, re, sys
import numpy as np
import pandas as pd

LISTS = ["test_new_households", "test_new_buildings", "test_both_new"]
LIST_RUNS = {"test_new_households": 1107, "test_new_buildings": 813, "test_both_new": 207}   # verified in part A (final check job 1405162)
MODELS = ["S", "C", "B1", "B0", "SloES", "SloIT", "Sseed2", "Sseed3"]
COUNTRIES = ["es", "it"]
CLASSES = ["SFH", "TH", "MFH", "AB"]
TARGETS = ["heating", "cooling", "equipment", "total_elec"]
VERDICTS = ("PASS", "FAIL", "NOT_EVALUABLE")
GATE_RE = re.compile(r"^GATE (\S+) country=(\S+) class=(\S+) target=(\S+) VERDICT=(\S+) ?(.*)$")
NUM_FIELDS = {
    "G5J.1": ["runs", "ok", "bad"],
    "G5J.2": ["median_cvrmse", "median_abs_nmbe", "share_runs_in_band", "runs"],
    "G5J.3": ["r2", "sign", "skill_over_B1", "r2_B1", "pairs", "above_floor", "thr_kwh", "buildings", "households"],
    "G5J.4": [],
    "G5J.5": ["share_days_peak_within_1h", "dwelling_days"],
}


def expected_keys():
    ks = set()
    for c in COUNTRIES:
        for k in CLASSES:
            ks.add(("G5J.1", c, k, "ALL")); ks.add(("G5J.5", c, k, "total_elec"))
            for t in TARGETS:
                for g in ("G5J.2", "G5J.3", "G5J.4"):
                    ks.add((g, c, k, t))
    return ks


EXP_KEYS = expected_keys()
EXP_COUNT = {"G5J.1": 8, "G5J.2": 32, "G5J.3": 32, "G5J.4": 32, "G5J.5": 8}


def fnum(s):
    try:
        return float(s.rstrip("%,)"))
    except Exception:
        return float("nan")


def parse_gate(line):
    m = GATE_RE.match(line.rstrip("\n"))
    if not m:
        return None
    gate, c, k, t, v, rest = m.groups()
    row = {"gate": gate, "country": c, "class": k, "target": t, "verdict": v, "printed": rest.strip()}
    kv = dict(re.findall(r"(\w+)=([^\s\[\]]+)", rest))
    for f in NUM_FIELDS.get(gate, []):
        row[f] = fnum(kv[f]) if f in kv else float("nan")
    mi = re.search(r"ci95=\[([^,\]]+),([^\]]+)\]", rest)
    row["ci_lo"] = fnum(mi.group(1)) if mi else float("nan")
    row["ci_hi"] = fnum(mi.group(2)) if mi else float("nan")
    if gate == "G5J.4":
        mc = re.search(r"\(r2=(\S+) sign=(\S+) skill_ci_lo=([^)\s]+)\)", rest)
        row["ctrl_r2"], row["ctrl_sign"], row["ctrl_skill_ci_lo"] = ((fnum(mc.group(1)), fnum(mc.group(2)), fnum(mc.group(3))) if mc else (float("nan"),) * 3)
        row["flagged"] = "FLAGGED FOR WITHDRAWAL" in rest
    return row


def read_text(p):
    with io.open(p, encoding="utf-8", errors="replace") as fh:
        return fh.read().splitlines()


def parse_call(lines):
    """Returns dict: gates (list of rows), summary_gate, summary, scorer_exit, runs_printed, check23."""
    out = {"gates": [], "summary_gate": [], "summary": None, "scorer_exit": None, "runs_printed": None, "check23": None, "start": None}
    for ln in lines:
        if ln.startswith("GATE "):
            r = parse_gate(ln)
            out["gates"].append(r if r else {"bad_line": ln})
        elif ln.startswith("SUMMARY_GATE "):
            out["summary_gate"].append(ln)
        elif ln.startswith("SUMMARY "):
            out["summary"] = ln
        elif ln.startswith("SCORER_EXIT"):
            out["scorer_exit"] = ln
        elif ln.startswith("SCORER start"):
            out["start"] = ln
        elif ln.startswith("TASKS "):
            m = re.match(r"TASKS \d+ groups, (\d+) runs of split (\S+)", ln)
            if m:
                out["runs_printed"] = (int(m.group(1)), m.group(2))
        elif ln.startswith("CHECK 2.3 "):
            out["check23"] = ln
    return out


# ------------------------------------------------------------------------------------------ the checks (each returns a list of problem strings)
def check_counts(p):
    """val 2.1: one line per gate x country x class x target; counts per gate equal the validation layout; key set equal; no duplicates."""
    prob = []
    rows = [g for g in p["gates"] if "bad_line" not in g]
    if len(rows) != len(p["gates"]):
        prob.append("%d GATE line(s) the parser could not read" % (len(p["gates"]) - len(rows)))
    for g, n in EXP_COUNT.items():
        got = sum(1 for r in rows if r["gate"] == g)
        if got != n:
            prob.append("%s lines %d != %d" % (g, got, n))
    keys = [(r["gate"], r["country"], r["class"], r["target"]) for r in rows]
    if len(set(keys)) != len(keys):
        prob.append("duplicate gate line keys: %d" % (len(keys) - len(set(keys))))
    miss = EXP_KEYS - set(keys)
    extra = set(keys) - EXP_KEYS
    if miss:
        prob.append("missing keys e.g. %s (%d)" % (sorted(miss)[0], len(miss)))
    if extra:
        prob.append("unexpected keys e.g. %s (%d)" % (sorted(extra)[0], len(extra)))
    return prob


def check_verdicts(p):
    """val 2.2 (verdict domain) and 2.3 (every NOT_EVALUABLE has a reason)."""
    prob = []
    for r in p["gates"]:
        if "bad_line" in r:
            continue
        key = "%s %s %s %s" % (r["gate"], r["country"], r["class"], r["target"])
        if r["verdict"] not in VERDICTS:
            prob.append("verdict '%s' not in {PASS,FAIL,NOT_EVALUABLE}: %s" % (r["verdict"], key))
        if r["verdict"] == "NOT_EVALUABLE" and len(r["printed"]) < 3:
            prob.append("NOT_EVALUABLE without a reason: %s" % key)
    return prob


def check_exit(p, rc):
    """val 2.2: exit code consistent with the lines (scorer docstring: 0 all computed, 2 some NOT_EVALUABLE, 1 crashed; 1 wins)."""
    prob = []
    if p["summary"] is None:
        return ["no SUMMARY line"]
    m = re.match(r"SUMMARY PASS=(\d+) FAIL=(\d+) NOT_EVALUABLE=(\d+) crashed=(\w+)", p["summary"])
    if not m:
        return ["SUMMARY line unreadable: " + p["summary"][:80]]
    sp, sf, sn, crashed = int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4) == "True"
    rows = [r for r in p["gates"] if "bad_line" not in r]
    tp, tf, tn = [sum(1 for r in rows if r["verdict"] == v) for v in VERDICTS]
    if (sp, sf, sn) != (tp, tf, tn):
        prob.append("SUMMARY counts %s != tally of the GATE lines %s" % ((sp, sf, sn), (tp, tf, tn)))
    for ln in p["summary_gate"]:
        mg = re.match(r"SUMMARY_GATE (\S+) PASS=(\d+) FAIL=(\d+) NOT_EVALUABLE=(\d+)", ln)
        if not mg:
            prob.append("SUMMARY_GATE unreadable: " + ln[:60]); continue
        t3 = tuple(sum(1 for r in rows if r["gate"] == mg.group(1) and r["verdict"] == v) for v in VERDICTS)
        if t3 != (int(mg.group(2)), int(mg.group(3)), int(mg.group(4))):
            prob.append("SUMMARY_GATE %s counts differ from the GATE lines" % mg.group(1))
    exp = 1 if crashed else (2 if sn > 0 else 0)
    me = re.match(r"SCORER_EXIT (\d+)", p["scorer_exit"] or "")
    printed = int(me.group(1)) if me else None
    if printed is None:
        prob.append("no SCORER_EXIT line")
    elif printed != exp:
        prob.append("SCORER_EXIT %d but the lines imply %d" % (printed, exp))
    if rc is None:
        prob.append("no exit code file")
    elif rc != exp:
        prob.append("process exit code %s but the lines imply %d" % (rc, exp))
    return prob


def read_openlog(path):
    rows = []
    for ln in read_text(path)[1:]:
        f = ln.split("\t")
        rows.append(f)
    return rows


def check_opens(rows, n_runs_printed, list_name, job, jobid_file, check23):
    """TEST_OPENS: distinct truth files opened == runs of the list (printed by the scorer AND the part A count), each opened once,
    all by the one scoring job. Returns (n_truth, n_b0, problems)."""
    prob = []
    truth = [r[1] for r in rows if r[0] == "truth"]
    b0 = [r[1] for r in rows if r[0] == "truth_b0"]
    n = len(set(truth))
    if len(truth) != n:
        prob.append("%d truth rows but %d distinct run ids (a run opened twice)" % (len(truth), n))
    if n_runs_printed is not None and n != n_runs_printed:
        prob.append("truth opens %d != runs printed by the scorer %d" % (n, n_runs_printed))
    if n != LIST_RUNS[list_name]:
        prob.append("truth opens %d != runs of %s (%d)" % (n, list_name, LIST_RUNS[list_name]))
    if jobid_file != str(job):
        prob.append("job id of the call %s != the scoring job %s" % (jobid_file, job))
    if check23 is not None and "-> PASS" not in check23:
        prob.append("scorer CHECK 2.3 not PASS: " + check23[:100])
    return n, len(set(b0)), prob


def claim_word(npass, pes, pit, flagged):
    """6D claim rule (written 2026-09-30 before any test result). Withdrawn wins; holds = >=6/8 and >=3/4 in each country;
    partly = 3..5 of 8, or >=6 with one country below 3 of 4; does not hold = <=2."""
    if flagged >= 2:
        return "withdrawn"
    if npass >= 6 and pes >= 3 and pit >= 3:
        return "holds"
    if npass >= 3:
        return "partly"
    return "does not hold"


# ------------------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--score-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--job", required=True)
    a = ap.parse_args()
    sd = a.score_dir.rstrip("/") + "/"
    os.makedirs(a.out, exist_ok=True)
    plant_dir = a.out.rstrip("/") + "/plant/"
    os.makedirs(plant_dir, exist_ok=True)
    log = []

    def P(s):
        log.append(s); print(s, flush=True)

    P("COLLECT start job=%s score_dir=%s" % (a.job, sd))
    nbad = 0
    rows_all, sumlines = [], []
    calls = [(m, L) for L in LISTS for m in MODELS]
    parsed = {}
    for m, L in calls:
        tag = "%s_%s" % (m, L)
        f = sd + "score_%s.txt" % tag
        if not os.path.exists(f):
            P("CHECK %s present FAIL (no score file)" % tag); nbad += 1; continue
        p = parse_call(read_text(f))
        parsed[tag] = p
        rc = None
        if os.path.exists(sd + "exit_%s.txt" % tag):
            try:
                rc = int(read_text(sd + "exit_%s.txt" % tag)[0])
            except Exception:
                rc = None
        probs = [("counts", check_counts(p)), ("verdicts", check_verdicts(p)), ("exit", check_exit(p, rc))]
        jid = read_text(sd + "jobid_%s.txt" % tag)[0].strip() if os.path.exists(sd + "jobid_%s.txt" % tag) else "none"
        n_t, n_b, op = (0, 0, ["no openlog"])
        if os.path.exists(sd + "openlog_%s.tsv" % tag):
            n_t, n_b, op = check_opens(read_openlog(sd + "openlog_%s.tsv" % tag), p["runs_printed"][0] if p["runs_printed"] else None, L, a.job, jid, p["check23"])
        probs.append(("opens", op))
        P("TEST_OPENS %s %d %s (+ %d b0 truth files) %s" % (tag, n_t, jid, n_b, "OK" if not op else "FAIL " + "; ".join(op)))
        for nm, pr in probs[:3]:
            P("CHECK %s %s %s" % (tag, nm, "PASS" if not pr else "FAIL " + "; ".join(pr)))
        nbad += sum(1 for _, pr in probs if pr)
        sumlines.append("== %s (exit code %s, job %s) ==" % (tag, rc, jid))
        sumlines += p["summary_gate"]
        if p["summary"]:
            sumlines.append(p["summary"])
        if p["scorer_exit"]:
            sumlines.append(p["scorer_exit"])
        sumlines.append("CALL %s EXIT %s" % (tag, rc))
        for r in p["gates"]:
            if "bad_line" in r:
                continue
            d = dict(r); d.update({"tag": tag, "model": m, "list": L})
            rows_all.append(d)
    # reported calls: exit code, opens, and their CHECK/REPORTED lines verbatim
    for L in LISTS:
        tag = "reported_S_%s" % L
        rc = None
        if os.path.exists(sd + "exit_%s.txt" % tag):
            try:
                rc = int(read_text(sd + "exit_%s.txt" % tag)[0])
            except Exception:
                pass
        jid = read_text(sd + "jobid_%s.txt" % tag)[0].strip() if os.path.exists(sd + "jobid_%s.txt" % tag) else "none"
        sumlines.append("== %s (exit code %s, job %s) ==" % (tag, rc, jid))
        if os.path.exists(sd + "stdout_%s.txt" % tag):
            sumlines += [ln for ln in read_text(sd + "stdout_%s.txt" % tag) if ln.startswith(("CHECK", "REPORTED", "RUNS", "RUN_PROBLEM"))]
        sumlines.append("CALL %s EXIT %s" % (tag, rc))
        of = sd + "openlog_%s.tsv" % tag
        if os.path.exists(of):
            orows = read_openlog(of)
            tr = sorted(set(r[1] for r in orows if r[0] == "truth"))
            jobs = sorted(set(r[3] for r in orows if len(r) > 3))
            pr = []
            if len(tr) != LIST_RUNS[L]:
                pr.append("truth opens %d != runs of %s (%d)" % (len(tr), L, LIST_RUNS[L]))
            if jobs != [str(a.job)]:
                pr.append("job ids in the open log %s != %s" % (jobs, a.job))
            P("TEST_OPENS %s %d %s %s" % (tag, len(tr), ",".join(jobs), "OK" if not pr else "FAIL " + "; ".join(pr)))
            nbad += 1 if pr else 0
        else:
            P("TEST_OPENS %s 0 none FAIL no open log" % tag); nbad += 1
        if rc != 0:
            P("CHECK %s exit FAIL exit code %s (reported analysis, not a gate)" % (tag, rc)); nbad += 1
    # ---- outputs
    df = pd.DataFrame(rows_all)
    front = ["tag", "model", "list", "gate", "country", "class", "target", "verdict"]
    df = df[front + [c for c in df.columns if c not in front]]
    df.to_parquet(a.out.rstrip("/") + "/scores.parquet", index=False)
    g3 = df[df["gate"] == "G5J.3"]
    bi = g3[["tag", "model", "list", "country", "class", "target", "verdict", "skill_over_B1", "ci_lo", "ci_hi", "buildings", "households"]]
    bi.to_csv(a.out.rstrip("/") + "/bootstrap_intervals.csv", index=False)
    with io.open(a.out.rstrip("/") + "/SUMMARY.txt", "w", encoding="utf-8") as fh:
        fh.write("\n".join(sumlines) + "\n")
    # ---- claims (6D) by code from scores.parquet
    cl = []
    for L in LISTS:
        for t in TARGETS:
            for m in ("S", "Sseed2", "Sseed3"):
                sub = g3[(g3["model"] == m) & (g3["list"] == L) & (g3["target"] == t)]
                if len(sub) == 0:
                    cl.append("CLAIM %s %s %s: no G5J.3 lines" % (L, t, m)); continue
                npass = int((sub["verdict"] == "PASS").sum())
                pes = int(((sub["verdict"] == "PASS") & (sub["country"] == "es")).sum())
                pit = int(((sub["verdict"] == "PASS") & (sub["country"] == "it")).sum())
                ne = ["%s_%s" % (r["country"], r["class"]) for _, r in sub[sub["verdict"] == "NOT_EVALUABLE"].iterrows()]
                g4 = df[(df["gate"] == "G5J.4") & (df["model"] == m) & (df["list"] == L) & (df["target"] == t)]
                flagged = int(g4["flagged"].fillna(False).astype(bool).sum()) if "flagged" in g4 else 0
                word = claim_word(npass, pes, pit, flagged)
                tagc = "CLAIM" if m == "S" else "CLAIM_REPORTED_ONLY"
                cl.append("%s list=%s target=%s model=%s G5J.3_PASS=%d/8 es=%d/4 it=%d/4 NOT_EVALUABLE=%s G5J.4_FLAGGED=%d/8 6D_VERDICT=%s" %
                          (tagc, L, t, m, npass, pes, pit, ("[" + ",".join(ne) + "]") if ne else "[]", flagged, word))
    with io.open(a.out.rstrip("/") + "/claims.txt", "w", encoding="utf-8") as fh:
        fh.write("\n".join(cl) + "\n")
    P("OUTPUTS scores.parquet rows=%d, SUMMARY.txt lines=%d, bootstrap_intervals.csv rows=%d, claims.txt lines=%d" % (len(df), len(sumlines), len(bi), len(cl)))

    # ---- seen failing: planted faults on COPIES of one real score file / open log (unplanted result printed next to the planted one)
    nplant_bad = 0
    tag0 = "S_%s" % LISTS[0]
    if tag0 in parsed:
        src = read_text(sd + "score_%s.txt" % tag0)
        # 1 one missing GATE line
        i = next(i for i, ln in enumerate(src) if ln.startswith("GATE G5J.3 "))
        pl = src[:i] + src[i + 1:]
        with io.open(plant_dir + "score_plant_missing.txt", "w", encoding="utf-8") as fh:
            fh.write("\n".join(pl) + "\n")
        a0 = check_counts(parse_call(read_text(sd + "score_%s.txt" % tag0)))
        a1 = check_counts(parse_call(read_text(plant_dir + "score_plant_missing.txt")))
        fired = len(a1) > len(a0)
        P("PLANT missing_gate_line unplanted_problems=%d planted_problems=%d (%s) -> %s" % (len(a0), len(a1), a1[0] if a1 else "", "FIRED" if fired else "DID_NOT_FIRE"))
        nplant_bad += 0 if fired else 1
        # 2 a verdict outside the domain
        pl = list(src)
        jv = next(i for i, ln in enumerate(pl) if ln.startswith("GATE ") and "VERDICT=PASS" in ln)
        pl[jv] = pl[jv].replace("VERDICT=PASS", "VERDICT=MAYBE", 1)
        with io.open(plant_dir + "score_plant_verdict.txt", "w", encoding="utf-8") as fh:
            fh.write("\n".join(pl) + "\n")
        b0_ = check_verdicts(parse_call(read_text(sd + "score_%s.txt" % tag0)))
        b1_ = check_verdicts(parse_call(read_text(plant_dir + "score_plant_verdict.txt")))
        fired = len(b1_) > len(b0_)
        P("PLANT bad_verdict_word unplanted_problems=%d planted_problems=%d -> %s" % (len(b0_), len(b1_), "FIRED" if fired else "DID_NOT_FIRE"))
        nplant_bad += 0 if fired else 1
        # 3 a NOT_EVALUABLE line without a reason
        pl = list(src)
        j = next(i for i, ln in enumerate(pl) if ln.startswith("GATE "))
        mm = GATE_RE.match(pl[j])
        pl[j] = "GATE %s country=%s class=%s target=%s VERDICT=NOT_EVALUABLE" % mm.groups()[:4]
        with io.open(plant_dir + "score_plant_noreason.txt", "w", encoding="utf-8") as fh:
            fh.write("\n".join(pl) + "\n")
        c1_ = check_verdicts(parse_call(read_text(plant_dir + "score_plant_noreason.txt")))
        fired = len(c1_) > 0
        P("PLANT not_evaluable_without_reason planted_problems=%d -> %s" % (len(c1_), "FIRED" if fired else "DID_NOT_FIRE"))
        nplant_bad += 0 if fired else 1
        # 4 process exit code that disagrees with the lines (the real exit code plus one)
        rc_real = int(read_text(sd + "exit_%s.txt" % tag0)[0])
        e0 = check_exit(parse_call(read_text(sd + "score_%s.txt" % tag0)), rc_real)
        e1 = check_exit(parse_call(read_text(sd + "score_%s.txt" % tag0)), rc_real + 1)
        fired = len(e1) > len(e0)
        P("PLANT exit_code_vs_lines unplanted_problems=%d planted_problems=%d -> %s" % (len(e0), len(e1), "FIRED" if fired else "DID_NOT_FIRE"))
        nplant_bad += 0 if fired else 1
        # 5 one extra truth open (a run opened that is not in the list)
        of = sd + "openlog_%s.tsv" % tag0
        if os.path.exists(of):
            ol = read_text(of)
            with io.open(plant_dir + "openlog_plant.tsv", "w", encoding="utf-8") as fh:
                fh.write("\n".join(ol + ["truth\tPLANTED_RUN\tnowhere"]) + "\n")
            rp = parsed[tag0]["runs_printed"][0]
            _, _, q0 = check_opens(read_openlog(of), rp, LISTS[0], a.job, read_text(sd + "jobid_%s.txt" % tag0)[0].strip(), parsed[tag0]["check23"])
            _, _, q1 = check_opens(read_openlog(plant_dir + "openlog_plant.tsv"), rp, LISTS[0], a.job, read_text(sd + "jobid_%s.txt" % tag0)[0].strip(), parsed[tag0]["check23"])
            fired = len(q1) > len(q0)
            P("PLANT extra_truth_open unplanted_problems=%d planted_problems=%d -> %s" % (len(q0), len(q1), "FIRED" if fired else "DID_NOT_FIRE"))
            nplant_bad += 0 if fired else 1
        # 6 a claim rule check on made-up counts (the rule itself, no data)
        t6 = [claim_word(8, 4, 4, 0) == "holds", claim_word(6, 4, 2, 0) == "partly", claim_word(4, 2, 2, 0) == "partly", claim_word(2, 1, 1, 0) == "does not hold", claim_word(8, 4, 4, 2) == "withdrawn", claim_word(8, 4, 4, 1) == "holds"]
        P("PLANT claim_rule_table %s -> %s" % (t6, "FIRED" if all(t6) else "DID_NOT_FIRE"))
        nplant_bad += 0 if all(t6) else 1
    else:
        P("PLANT not run: %s was not collected" % tag0); nplant_bad += 1
    with io.open(a.out.rstrip("/") + "/collect.log", "w", encoding="utf-8") as fh:
        fh.write("\n".join(log) + "\n")
    P("COLLECT_DONE problems=%d planted_not_fired=%d" % (nbad, nplant_bad))
    with io.open(a.out.rstrip("/") + "/collect.log", "w", encoding="utf-8") as fh:
        fh.write("\n".join(log) + "\n")
    if nplant_bad:
        return 5
    return 3 if nbad else 0


if __name__ == "__main__":
    sys.exit(main())
