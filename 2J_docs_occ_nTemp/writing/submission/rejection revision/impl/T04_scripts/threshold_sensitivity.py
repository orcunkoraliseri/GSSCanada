#!/usr/bin/env python
"""
T04 / WP9 -- threshold provenance + sensitivity.

No results_index/results.csv was found anywhere in the repo (checked locally under
GSSCanada-main/2J_docs_occ_nTemp/step4_Speed_Cluster/** and outputs_step4/**, and on
Speed under /speed-scratch/o_iseri/GSSCanada/GSSCanada-main/2J_docs_occ_nTemp -- that
clone does not even contain a step4_Speed_Cluster directory). The consolidated CSV that
04_augmentationGSS_hpc.md / step4_training_v2.md describe (auto-rsynced by the YAML/array
orchestration refactor introduced after F8, see
DONE_step4_training.md line 816) is not present anywhere reachable from this repo -- it
was either never retained past the training window or lives on a scratch path that has
since been cleaned. This is recorded as NOT FOUND, not guessed.

Instead this script uses the gate-score table hand-transcribed (values only, not
re-derived) from the docs and diagnostics JSON that ARE in the repo -- the same
numbers the paper's own tables cite. Every row below has a source comment with
file:line (docs are relative to 2J_docs_occ_nTemp/step4_Speed_Cluster/step4_Speed-Cluster_docs/
unless noted).

Excluded: J5-F (scancelled at epoch 38, home_loss flatlined at 0.51 -- never produced a
final diagnostics_v4_statistical.json, so it has no composite score; step4_training_v4.md:921).
J5-D and J5-E were never run (D shelved on precondition failure, E gated on a diagnostic
that was never executed). J3-HPT-* bundle was cancelled mid-training with only partial
loss trajectories, no final gate scores (step4_training_v4.md:1108).
"""
import csv
import os

OUT_DIR = os.environ.get("T04_OUT_DIR", ".")

# name, composite, at_home_gap_rms_pp, spouse_gap_pp (signed), act_js_mean, source
TRIALS = [
    # step4_training_v4.md:341-344 (J3 at ship, production)
    ("J3",      0.6355, 4.57,  -2.03, 0.0191, "step4_training_v4.md:341-344"),
    # step4_training_v4.md:356-361 / 587-594 (J5-X1 bundle, 2026-05-18)
    ("J5_X1",   0.6667, 4.15,  -1.2,  0.0311, "step4_training_v4.md:356-361"),
    ("J5_X1b",  0.8086, 5.88,  -0.6,  0.0285, "step4_training_v4.md:356-361"),
    # step4_training_v4.md:736-741 (J5-X2/A/B parallel bundle, 2026-05-19/20)
    ("J5_X2",   0.6747, 4.42,  -1.89, 0.0297, "step4_training_v4.md:738-741"),
    ("J5_A",    0.6997, 5.57,  -2.43, 0.0267, "step4_training_v4.md:738-741"),
    ("J5_B",    0.6975, 5.20,   1.61, 0.0322, "step4_training_v4.md:738-741"),
    # cluster_outputs/outputs_step4_J5_C/diagnostics_J5_C.json (composite line 761,
    # at_home_gap_rms_pp line 756, Spouse.gap_pp line 15, act_js_mean line 758);
    # composite cross-checked against step4_training_v4.md:921
    ("J5_C",    0.6921, 6.8646, -3.2485, 0.03760, "diagnostics_J5_C.json:15,756,758,761"),
    # cluster_outputs/outputs_step4_J_old/diagnostics_J_old.json (same fields);
    # composite cross-checked against step4_training_v4.md:921
    ("J_old",   1.3750, 11.4881, -0.5262, 0.20815, "diagnostics_J_old.json:15,756,758,761"),
]

# Original published thresholds (paper text, and step4_training_v4.md:5 / :67)
ORIG = {
    "composite_max": 1.045,
    "at_home_max": 5.3,
    "spouse_abs_max": 5.0,
    "act_js_max": 0.05,
}

SHIFT_PCTS = [-0.20, -0.10, 0.0, 0.10, 0.20]


def gates_pass(trial, thr):
    name, composite, at_home, spouse, act_js, _src = trial
    p_composite = composite < thr["composite_max"]
    p_at_home = at_home <= thr["at_home_max"]
    p_spouse = abs(spouse) <= thr["spouse_abs_max"]
    p_act_js = act_js <= thr["act_js_max"]
    n_pass = sum([p_composite, p_at_home, p_spouse, p_act_js])
    return n_pass, (p_composite, p_at_home, p_spouse, p_act_js)


def make_thr(base, which, pct):
    """which in {'composite_max','at_home_max','spouse_abs_max','act_js_max','all'}"""
    thr = dict(base)
    keys = list(base.keys()) if which == "all" else [which]
    for k in keys:
        thr[k] = base[k] * (1.0 + pct)
    return thr


def run_scenario(label, thr):
    rows = []
    passers = []
    for t in TRIALS:
        n_pass, flags = gates_pass(t, thr)
        rows.append((t[0], n_pass, flags))
        if n_pass == 4:
            passers.append((t[0], t[1]))
    if passers:
        selected = min(passers, key=lambda x: x[1])[0]
    else:
        selected = "NONE"
    return rows, passers, selected


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, "threshold_sensitivity.csv")

    scenarios = []
    # (a) baseline / original thresholds
    scenarios.append(("baseline_original", ORIG))
    # (b) each threshold shifted individually, and all together, at each pct
    which_list = ["composite_max", "at_home_max", "spouse_abs_max", "act_js_max", "all"]
    for which in which_list:
        for pct in SHIFT_PCTS:
            if pct == 0.0:
                continue  # baseline already covered
            label = "%s_%+d pct" % (which, int(round(pct * 100)))
            thr = make_thr(ORIG, which, pct)
            scenarios.append((label, thr))

    with open(out_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "scenario", "composite_max", "at_home_max", "spouse_abs_max", "act_js_max",
            "trials_passing_4of4", "n_passing_4of4", "selected_model",
            "selected_composite", "matches_J3_only",
        ])
        for label, thr in scenarios:
            rows, passers, selected = run_scenario(label, thr)
            passer_names = ";".join(p[0] for p in passers)
            sel_composite = ""
            if selected != "NONE":
                sel_composite = dict((t[0], t[1]) for t in TRIALS)[selected]
            matches_j3_only = (len(passers) == 1 and passers[0][0] == "J3")
            w.writerow([
                label,
                round(thr["composite_max"], 6),
                round(thr["at_home_max"], 6),
                round(thr["spouse_abs_max"], 6),
                round(thr["act_js_max"], 6),
                passer_names,
                len(passers),
                selected,
                sel_composite,
                matches_j3_only,
            ])

    # Also print the baseline detail to the job log for a quick human read.
    print("=== (a) baseline / original thresholds: per-trial gate detail ===")
    print("%-8s %-6s %-8s %-7s %-6s %-8s" % ("trial", "N/4", "compos.", "at_home", "spouse", "act_js"))
    for t in TRIALS:
        n_pass, flags = gates_pass(t, ORIG)
        print("%-8s %-6s %-8s %-7s %-6s %-8s  flags=%s  src=%s" % (
            t[0], n_pass, t[1], t[2], t[3], t[4], flags, t[5]))
    n4 = [t[0] for t in TRIALS if gates_pass(t, ORIG)[0] == 4]
    print("Trials passing 4/4 at original thresholds:", n4)
    print("Reproduces paper's 'J3 only' claim:", n4 == ["J3"])
    print("Wrote:", out_path)


if __name__ == "__main__":
    main()
