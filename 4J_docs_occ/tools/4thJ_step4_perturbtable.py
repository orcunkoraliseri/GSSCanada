"""
Step 4 -- the TRAINING-SIDE perturbation battery, scored.

The val doc: "Each perturbation must break EXACTLY ONE gate ... Cross-tab every
perturbation against baseline; FAIL the probe if any gate that passes on the real model
was never made to fall."

THIS TABLE IS THE PRE-REGISTRATION. It is written before the battery is run and is
never edited after a result has been seen. If a perturbation fells a gate that is not
its own, that is a FINDING and is printed as one -- it is not quietly added here.

SCOPE, stated so it cannot be over-read. This battery scores only the gates that a
TRAINING run can fell. G4.1, G4.3, G4.4 and G4.12 are generation-side and conditioning
gates; they are scored by 4thJ_step4_genperturb.py and 4thJ_step4_diagnostics.py, on a
trained adapter and at generation volumes that satisfy V4.a. A gate that FAILS at
baseline here cannot be "seen falling" here, and is excluded from the coverage clause
with its reason printed rather than being silently dropped.
"""
import argparse
import json
import os
import sys

# perturbation -> (gate it MUST fell, gates that MUST stay clean)
EXPECTED = {
    "null":                  (None,     ["G4.2", "G4.5", "G4.6", "G4.7", "G4.8",
                                         "G4.9", "G4.11", "G4.13", "G4.14"]),
    "pad_labels_1pct":       ("G4.5",   ["G4.6"]),
    "perturb_merged_weight": ("G4.6",   ["G4.5"]),
    "strip_eor_1pct":        ("G4.7",   ["G4.13"]),
    "swap_tokenizer":        ("G4.8",   []),
    # Added 2026-08-18. G4.2 had NO perturbation at all, which is why it sat in
    # `never made to fall`. `collapse_content` leaves every delimiter and every <eor>
    # in place and replaces only the VALUES with one repeated episode, so the format is
    # learned trivially (delimiter loss -> ~0) while generated activity entropy -> ~0 and
    # both arms of the G4.2 halt cross together. Adding coverage is REQUIRED by the
    # coverage clause; no existing row is edited.
    "collapse_content":      ("G4.2",   ["G4.5", "G4.13", "G4.14"]),
    "sequential_countries":  ("G4.9",   ["G4.13"]),
    "drop_revision":         ("G4.11",  ["G4.5", "G4.6", "G4.7", "G4.8", "G4.13", "G4.14"]),
    "leak_1pct":             ("G4.13",  ["G4.5", "G4.7"]),
    "edit_prereg":           ("G4.14",  ["G4.5", "G4.6", "G4.7", "G4.8", "G4.9",
                                         "G4.11", "G4.13"]),
    # multi-gate by design, scored for COVERAGE ONLY -- the val doc marks these as
    # coverage cases because a perturbation that moves several gates cannot attribute
    # what it broke.
    "no_prefix":             ("__COVERAGE_ONLY__", []),
    "freeze_adapter":        ("__COVERAGE_ONLY__", []),
}

ORDER = ["G4.2", "G4.5", "G4.6", "G4.7", "G4.8", "G4.9", "G4.11", "G4.13", "G4.14"]


def verdicts(det):
    """Flatten every gate verdict in a detectors_*.json into {gate: verdict}."""
    out = {}
    for block in ["gates_at_start", "gates_at_end"]:
        for k, v in (det.get(block) or {}).items():
            if isinstance(v, dict) and "verdict" in v:
                out[k] = v["verdict"]
    # G4.1 and G4.2 live inside the per-epoch records
    eps = det.get("epochs") or []
    if eps:
        last = eps[-1]
        for k in ["G4.1", "G4.2"]:
            g = last.get(k)
            if isinstance(g, dict) and "verdict" in g:
                out[k] = g["verdict"]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True, help="directory holding the run subdirs")
    ap.add_argument("--fold", default="es")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    found = {}
    for sub in sorted(os.listdir(args.runs)):
        d = os.path.join(args.runs, sub)
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            if fn.startswith("detectors_") and fn.endswith(".json"):
                det = json.load(open(os.path.join(d, fn), "r", encoding="utf-8"))
                if det.get("fold") != args.fold:
                    continue
                if det.get("run_type") != "perturb":
                    continue
                p = det.get("perturbation") or "null"
                found[p] = verdicts(det)

    if "null" not in found:
        print("NO BASELINE RUN. The battery cannot be scored: every judgement here is "
              "relative to the unperturbed run, and there is nothing to be relative to.")
        sys.exit(2)

    base = found["null"]
    lines = []

    def w(s=""):
        print(s)
        lines.append(s)

    w("=" * 100)
    w("STEP 4 -- TRAINING-SIDE PERTURBATION BATTERY, fold %s" % args.fold)
    w("=" * 100)
    w()
    w("BASELINE (null perturbation) gate verdicts:")
    for g in ORDER + [k for k in sorted(base) if k not in ORDER]:
        if g in base:
            w("  %-7s %s" % (g, base[g]))
    w()

    passing_at_baseline = [g for g in base if base[g] == "PASS"]
    excluded = {g: base[g] for g in base if base[g] != "PASS"}
    if excluded:
        w("EXCLUDED FROM THE COVERAGE CLAUSE -- these gates do not PASS at baseline in "
          "this configuration, so they cannot be SEEN FALLING here. Excluding them is "
          "stated, not silent:")
        for g, v in sorted(excluded.items()):
            w("     %-7s %s" % (g, v))
        w()

    # ---- cross-tab ----
    hdr = "%-24s | %s" % ("perturbation", " ".join("%-7s" % g for g in ORDER))
    w(hdr)
    w("-" * len(hdr))
    for p in EXPECTED:
        if p not in found:
            w("%-24s | NOT RUN" % p)
            continue
        v = found[p]
        w("%-24s | %s" % (p, " ".join("%-7s" % (v.get(g, "-")) for g in ORDER)))
    w()

    # ---- attribution ----
    w("ATTRIBUTION -- what each perturbation actually moved, against baseline:")
    findings = []
    felled = set()
    for p, (target, clean) in EXPECTED.items():
        if p not in found:
            w("  %-24s NOT RUN" % p)
            continue
        v = found[p]
        moved = [g for g in base
                 if base[g] == "PASS" and v.get(g) not in (None, "PASS")]
        if target is None:
            if moved:
                w("  %-24s UNEXPECTED FALL -- FINDING: the null perturbation changed "
                  "nothing and yet moved %s. Either a gate is non-deterministic or the "
                  "run is not reproducible." % (p, moved))
                findings.append((p, moved))
            else:
                w("  %-24s OK  moved nothing, as pre-registered" % p)
            continue
        if target == "__COVERAGE_ONLY__":
            w("  %-24s coverage only, moved %s (no single-gate claim is made)"
              % (p, moved or "nothing"))
            felled.update(moved)
            continue
        # 🔴 FINDING 18 (job 1266911). This read `hit = v.get(target) not in (None,
        # "PASS")` and then credited `felled.add(target)` unconditionally. A gate already
        # FAILing at BASELINE therefore entered the credited list for free: G4.6 was
        # listed under `gates seen falling` two lines after being listed as EXCLUDED from
        # the clause for exactly that reason, in the same report. The verdict was not
        # affected -- the clause is computed against `passing_at_baseline` -- but the
        # printed evidence overstated itself by one gate, and had G4.6 ever been repaired
        # without this line being repaired the error would have survived into a GREEN
        # report. Being seen falling requires PASSing at baseline AND failing here.
        target_down = v.get(target) not in (None, "PASS")
        base_ok = base.get(target) == "PASS"
        hit = target_down and base_ok
        extra = [g for g in moved if g != target]
        if hit:
            felled.add(target)
        if target_down and not base_ok:
            status = "VOID"
        elif hit:
            status = "OK "
        else:
            status = "DID NOT FELL ITS GATE"
        w("  %-24s %s target %s -> %s" % (p, status, target, v.get(target, "-")))
        if target_down and not base_ok:
            w("      %-20s VOID -- %s was already %s at baseline, so it cannot be SEEN "
              "FALLING here and this row is NOT credited. The perturbation may well have "
              "worked; this run cannot show it." % ("", target, base.get(target, "?")))
        if extra:
            w("      %-20s UNEXPECTED FALL -- FINDING: also moved %s" % ("", extra))
            findings.append((p, extra))
        # 🔴 FINDING 23 (job 1270491). This loop had NO baseline condition -- the exact
        # twin of FINDING 18 above, in the other half of the same function. G4.6 FAILs at
        # baseline in this configuration, and G4.6 is listed as a STAY CLEAN requirement for
        # pad_labels_1pct, drop_revision and edit_prereg. All three were therefore printed as
        # having violated a requirement, in the same report that had already EXCLUDED G4.6
        # from the coverage clause for being down at baseline. Nothing had moved. A gate that
        # is already failing cannot be dirtied by a perturbation, and reporting it as such
        # manufactures collateral damage that did not occur. Verdict unaffected -- this loop
        # never appended to `findings` -- but the printed evidence overstated itself in three
        # rows out of eleven.
        for g in clean:
            if g not in v or g == target:
                continue
            if base.get(g) != "PASS":
                w("      %-20s %s NOT ASSESSABLE as STAY CLEAN -- already %s at baseline. "
                  "Stated, not silently dropped." % ("", g, base.get(g, "absent")))
                continue
            if v[g] not in ("PASS", "REPORTED_NOT_THRESHOLDED"):
                w("      %-20s was required to STAY CLEAN and did not: %s = %s"
                  % ("", g, v[g]))
    w()

    # ---- coverage clause ----
    never = [g for g in passing_at_baseline
             if g not in felled and g not in ("G4.10",)]
    w("COVERAGE CLAUSE")
    w("  gates PASSing at baseline: %s" % sorted(passing_at_baseline))
    w("  gates seen falling:        %s" % sorted(felled))
    w("  never made to fall:        %s" % (sorted(never) or "none"))
    verdict = "PASS" if not never else "FAIL"
    w("  COVERAGE CLAUSE VERDICT: %s" % verdict)
    if never:
        w("  A gate that has never been seen failing is not evidence. The battery does "
          "not pass until every one of these has a perturbation that fells it.")
    w()
    w("FINDINGS: %d" % len(findings))
    w("=" * 100)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
    sys.exit(0 if verdict == "PASS" and not findings else 1)


if __name__ == "__main__":
    main()
