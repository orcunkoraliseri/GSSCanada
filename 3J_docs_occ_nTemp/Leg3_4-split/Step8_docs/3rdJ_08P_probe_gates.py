"""3rdJ_08P_probe_gates.py -- Step 8 (3J Leg-3 4-split) §P PROBE scorecard.

Run AFTER the 3rdJ_08P_probes.sh array (all 7 cells) has landed. Reads every
campaign_*/<cell_tag>/manifest.json plus the two per-cell CSVs (hourly_meters.csv,
channel_hourly.csv) and scores P1-P4 (3rdJ_08_simulation_4split_val.md §P; handoff
2026-07-28_employee_step8_probes_P1P4.md §3.4), using the AUDIT-W report() scorecard
idiom (3rdJ_08W_audit_wiring.py).

Scope boundary: residential is OUT (handoff §1). P1's residential leg is always
reported INFO/NOT-EXERCISED, never PASS/FAIL -- there is no specified rule for
collapsing the per-household residential product into one deterministic tower run.

Does NOT run the campaign, does NOT touch commercial_integration.py, and does NOT
perform the P3(a) second-hash rerun (that is a separate submission, handoff §4.6,
authorized only after this scorecard is in hand).

2026-07-28 built (P1-P4 armament, employee handoff). This script is written and
uploaded now per handoff §4.1-4.3 but is NOT submitted in this pass -- §4.5 submits
it, after the probe array lands and the manager authorizes the next step.

2026-07-28 LOCAL PORT (additive, Contrainte n3 -- see 3rdJ_08_implementation_improvements.md):
added a PLATFORM gate. Same EnergyPlus build does NOT guarantee bit-identical output across
compilers/libm/rounding (win32 vs Linux); the §P gates compare cells against each other, so
mixing a Windows-simulated cell with a Linux-simulated cell in the same campaign_* dir would
inject platform noise into the scenario signal. This is a NEW gate, not a relaxation of any
existing one -- it makes silent cross-platform comparison impossible. Reads the PLATFORM /
energyplus_version / energyplus_build fields 3rdJ_08P_probe_driver.py now writes into every
manifest.json (both engines).

2026-07-28 Defaut-3 companion gate: INPUTS_HASH cross-cell consistency. Same reasoning as
PLATFORM above, one level down -- P1 isolates ONE channel's effect by comparing a varied
cell against cell 1 (B_central), which is only a valid isolation if the OTHER (unvaried)
channels' Step-7 product files are IDENTICAL between the two manifests being compared. This
is a read-time cross-check over manifests already on disk (it does not re-run the driver's
write-time STALE-INPUTS GUARD, 3rdJ_08P_probe_driver.py::_check_inputs_hash_guard) -- it
catches the case where cells were regenerated at different times (e.g. only a subset
re-simulated after a product fix) and a P1 comparison would otherwise silently mix product
versions. Uses the per-channel csv_md5 already recorded in channels_requested (no new
manifest fields needed).
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import sys

import pandas as pd

# ---------------------------------------------------------------------------
# Paths (mirrors 3rdJ_08P_probe_driver.py's constants -- kept independent/standalone
# per the handoff: this script reads manifests + CSVs, it does not import the driver)
# ---------------------------------------------------------------------------
SCRATCH8 = "/speed-scratch/o_iseri/step8_4split"
PROBES_ROOT = SCRATCH8 + "/probes"
LOGS_DIR = SCRATCH8 + "/logs"
UPLOAD = SCRATCH8 + "/upload"
INJECTOR_PY = UPLOAD + "/eSim_bem_utils/commercial_integration.py"

# ---------------------------------------------------------------------------
# LOCAL (Windows) path defaults -- ADDITIVE, 2026-07-28 port, mirrors
# 3rdJ_08P_probe_driver.py's LOCAL_* block. None of the cluster constants above are
# touched; main() below selects which set to use via --engine (default: platform-
# detected). Needed so the PLATFORM gate (and everything else here) is actually
# runnable off-cluster, not just added dead code.
# ---------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
LOCAL_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
LOCAL_PROBES_ROOT = os.path.join(
    LOCAL_REPO_ROOT, "3J_docs_occ_nTemp", "Leg3_4-split", "Step8_docs", "probes_local")
LOCAL_INJECTOR_PY = os.path.join(LOCAL_REPO_ROOT, "eSim_bem_utils", "commercial_integration.py")

CELL_TAGS = {
    0: "baseline_necb", 1: "B_central", 2: "var_office", 3: "var_retail",
    4: "var_hotel", 5: "cycle_2022", 6: "fallback_retail",
}
VARIED_CHANNEL_OF_CELL = {2: "office", 3: "retail", 4: "hotel"}
CHANNELS_COMMERCIAL = ("office", "retail", "hotel")
METRICS = ("people", "lights", "equip")

RESULTS = []  # list of {"status": "PASS"/"WARN"/"FAIL"/"INFO", "gate": str, "detail": str}


def report(status: str, gate: str, detail: str) -> None:
    RESULTS.append({"status": status, "gate": gate, "detail": detail})


def md5_file(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _find_campaign_dirs():
    return sorted(d for d in glob.glob(os.path.join(PROBES_ROOT, "campaign_*")) if os.path.isdir(d))


def _load_manifest(campaign_dir: str, cell_idx: int):
    tag = CELL_TAGS[cell_idx]
    path = os.path.join(campaign_dir, tag, "manifest.json")
    if not os.path.isfile(path):
        return None, path
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f), path


def _max_abs_delta(df_a, df_b, col):
    if col not in df_a.columns or col not in df_b.columns:
        return None
    n = min(len(df_a), len(df_b))
    if n == 0:
        return None
    return float((df_a[col].iloc[:n] - df_b[col].iloc[:n]).abs().max())


def main() -> None:
    global PROBES_ROOT, LOGS_DIR, INJECTOR_PY

    ap = argparse.ArgumentParser(description="Score the Step-8 §P probe cell table.")
    ap.add_argument("--engine", choices=["auto", "cluster", "local"], default="auto",
                     help="auto (default) = platform-detected. cluster = original "
                          "/speed-scratch paths, unchanged. local = local repo checkout paths.")
    ap.add_argument("--outroot", type=str, default=None,
                     help="override the probes root dir (default: PROBES_ROOT on cluster, "
                          "LOCAL_PROBES_ROOT locally).")
    ap.add_argument("--repo-root", type=str, default=None,
                     help="engine=local only: override the repo checkout root (default: "
                          "auto-derived from this script's own location).")
    args = ap.parse_args()

    engine = args.engine
    if engine == "auto":
        engine = "local" if sys.platform == "win32" else "cluster"
    if engine == "cluster":
        PROBES_ROOT = args.outroot if args.outroot else PROBES_ROOT
        # LOGS_DIR / INJECTOR_PY keep their cluster defaults -- unchanged from before this port.
    else:
        repo_root = args.repo_root if args.repo_root else LOCAL_REPO_ROOT
        PROBES_ROOT = args.outroot if args.outroot else os.path.join(
            repo_root, "3J_docs_occ_nTemp", "Leg3_4-split", "Step8_docs", "probes_local")
        LOGS_DIR = os.path.join(PROBES_ROOT, "_logs")
        INJECTOR_PY = os.path.join(repo_root, "eSim_bem_utils", "commercial_integration.py")
    report("INFO", "setup", f"engine={engine} (arg={args.engine}, sys.platform={sys.platform}), "
           f"PROBES_ROOT={PROBES_ROOT}")

    campaigns = _find_campaign_dirs()
    if not campaigns:
        report("FAIL", "setup", f"no campaign_* directories found under {PROBES_ROOT}")
        _finish()
        return

    # Primary campaign = the one with the most of the 7 cells present (the main
    # 0-6 array). A P3(a) second-hash rerun (cell 1 only, done later per §4.6) would
    # show up as a second, smaller campaign_* dir and is scored separately in P3(a).
    primary = max(campaigns, key=lambda d: sum(
        1 for i in range(7) if os.path.isfile(os.path.join(d, CELL_TAGS[i], "manifest.json"))
    ))
    report("INFO", "setup", f"primary campaign dir = {primary}; all campaign_* dirs = {campaigns}")

    manifests, csvs_hourly, csvs_channel = {}, {}, {}
    for i in range(7):
        m, path = _load_manifest(primary, i)
        if m is None:
            report("FAIL", f"cell {i} manifest", f"missing: {path}")
            continue
        manifests[i] = m
        tag = CELL_TAGS[i]
        hourly_path = os.path.join(primary, tag, "hourly_meters.csv")
        channel_path = os.path.join(primary, tag, "channel_hourly.csv")
        if os.path.isfile(hourly_path):
            csvs_hourly[i] = pd.read_csv(hourly_path)
        if os.path.isfile(channel_path):
            csvs_channel[i] = pd.read_csv(channel_path)

    # =========================================================================
    # PLATFORM -- cross-platform contamination guard (2026-07-28 LOCAL PORT, Contrainte n3).
    # NEW gate: FAILs if the cells being compared in this campaign_* dir were not all
    # simulated on the same platform. Runs before P1/P2 so a platform mismatch is reported
    # once, up front, rather than as confusing noise scattered through every delta gate.
    # =========================================================================
    platforms = {}
    missing_platform = []
    for i in range(7):
        m = manifests.get(i)
        if m is None:
            continue
        p = m.get("PLATFORM")
        if p is None:
            missing_platform.append(i)
        else:
            platforms[i] = p
    if missing_platform:
        report("WARN", "PLATFORM field",
               f"cell(s) {missing_platform} have no PLATFORM field in manifest.json "
               f"(pre-LOCAL-PORT run, or driver run before this gate existed)")
    distinct = set(platforms.values())
    if len(distinct) > 1:
        report("FAIL", "PLATFORM consistency",
               f"mixed platforms across cells in {primary}: {platforms} -- cross-platform "
               f"comparisons are NOT valid (same EnergyPlus build != bit-identical output "
               f"across win32/Linux; see 3rdJ_08_implementation_improvements.md Contrainte n3)")
    elif platforms:
        report("PASS", "PLATFORM consistency",
               f"all {len(platforms)} cells with a PLATFORM field agree: {distinct.pop()!r}")
    else:
        report("WARN", "PLATFORM consistency", "no cell manifest carries a PLATFORM field -- "
               "cannot assess cross-platform contamination")

    # =========================================================================
    # INPUTS_HASH consistency -- Defaut-3 companion gate (2026-07-28). Runs before P1,
    # same placement rationale as PLATFORM above: report contamination once, up front,
    # rather than as confusing noise scattered through every P1 delta.
    # =========================================================================
    def _channel_csv_md5(manifest, channel):
        return (manifest.get("channels_requested", {}).get(channel) or {}).get("csv_md5")

    for varied_cell, channel in VARIED_CHANNEL_OF_CELL.items():
        if varied_cell not in manifests or 1 not in manifests:
            continue
        m_v, m_1 = manifests[varied_cell], manifests[1]
        for other in CHANNELS_COMMERCIAL:
            if other == channel:
                continue
            md5_v, md5_1 = _channel_csv_md5(m_v, other), _channel_csv_md5(m_1, other)
            if md5_v is None or md5_1 is None:
                report("WARN", f"INPUTS_HASH {other} (cell {varied_cell} vs cell 1)",
                       f"csv_md5 missing from channels_requested in one or both manifests "
                       f"(cell {varied_cell}={md5_v}, cell 1={md5_1})")
            elif md5_v != md5_1:
                report("FAIL", f"INPUTS_HASH {other} (cell {varied_cell} vs cell 1)",
                       f"unvaried channel '{other}' Step-7 product differs between cell "
                       f"{varied_cell} ({CELL_TAGS[varied_cell]}, csv_md5={md5_v}) and cell 1 "
                       f"(B_central, csv_md5={md5_1}) -- this comparison is contaminated, the "
                       f"two manifests were built from different product sets")
            else:
                report("PASS", f"INPUTS_HASH {other} (cell {varied_cell} vs cell 1)",
                       f"unvaried channel '{other}' csv_md5 matches ({md5_v})")

    # =========================================================================
    # P1 -- scenario-differentiation per channel
    # =========================================================================
    report("INFO", "P1 residential", "NOT EXERCISED -- collapse rule unspecified")

    for varied_cell, channel in VARIED_CHANNEL_OF_CELL.items():
        # (a) the one-at-a-time varied cell vs cell 1 (B_central)
        if varied_cell in csvs_channel and 1 in csvs_channel:
            df_v, df_1 = csvs_channel[varied_cell], csvs_channel[1]
            d_people = _max_abs_delta(df_v, df_1, f"{channel}_people")
            status = "PASS" if (d_people is not None and d_people > 0) else "FAIL"
            details = {m: _max_abs_delta(df_v, df_1, f"{channel}_{m}") for m in METRICS}
            report(status, f"P1 {channel} (cell {varied_cell} vs cell 1)", f"max|delta|={details}")
            for other in CHANNELS_COMMERCIAL:
                if other == channel:
                    continue
                other_details = {m: _max_abs_delta(df_v, df_1, f"{other}_{m}") for m in METRICS}
                report("INFO", f"P1 {other} unvaried (cell {varied_cell} vs cell 1)",
                       f"max|delta|={other_details} (expect ~0; large=cross-channel leakage)")
        else:
            report("FAIL", f"P1 {channel} (cell {varied_cell} vs cell 1)",
                   "missing channel_hourly.csv for one or both cells")

        # (b) cell 1 (B_central) vs cell 0 (baseline_necb, un-injected reference)
        if 1 in csvs_channel and 0 in csvs_channel:
            df_1, df_0 = csvs_channel[1], csvs_channel[0]
            d_people = _max_abs_delta(df_1, df_0, f"{channel}_people")
            status = "PASS" if (d_people is not None and d_people > 0) else "FAIL"
            details = {m: _max_abs_delta(df_1, df_0, f"{channel}_{m}") for m in METRICS}
            report(status, f"P1 {channel} (cell 1 vs cell 0)", f"max|delta|={details}")
        else:
            report("FAIL", f"P1 {channel} (cell 1 vs cell 0)",
                   "missing channel_hourly.csv for cell 0 or cell 1")

    # =========================================================================
    # P2 -- byte-identity tripwire (cells 0-5 only; cell 6 excluded by design)
    # =========================================================================
    md5s = {}
    for i in range(6):
        if i in manifests:
            md5s[i] = manifests[i].get("hourly_meters_csv", {}).get("md5")
    seen = {}
    dup_found = False
    for i, h in md5s.items():
        if h is None:
            report("WARN", f"P2 cell {i}", "hourly_meters.csv md5 missing from manifest")
            continue
        if h in seen:
            report("FAIL", "P2 byte-identity", f"cell {seen[h]} ({CELL_TAGS[seen[h]]}) and "
                   f"cell {i} ({CELL_TAGS[i]}) share md5 {h}")
            dup_found = True
        else:
            seen[h] = i
    if not dup_found and md5s:
        report("PASS", "P2 byte-identity", f"{len(seen)} distinct md5s among cells 0-5, no collisions "
               f"({md5s})")

    # =========================================================================
    # P3 -- stale-output guard
    # =========================================================================
    # (a) path/hash consistency for every campaign dir found. The full proof that a
    # wiring change flips the hash (and therefore the output path) requires the
    # second submission -- out of scope for THIS run, see handoff §4.6.
    current_inj_md5 = md5_file(INJECTOR_PY)[:8] if os.path.isfile(INJECTOR_PY) else None
    for cd in campaigns:
        base = os.path.basename(cd)
        if not base.startswith("campaign_"):
            report("FAIL", "P3a path structure", f"{cd} does not match campaign_<hash> naming")
            continue
        hash_in_path = base[len("campaign_"):]
        for i in range(7):
            m, _ = _load_manifest(cd, i)
            if m is None:
                continue
            if m.get("INJ_HASH") != hash_in_path:
                report("FAIL", "P3a path/manifest hash", f"{cd}/{CELL_TAGS[i]}: manifest "
                       f"INJ_HASH={m.get('INJ_HASH')} != path hash {hash_in_path}")
    if current_inj_md5 is not None:
        if os.path.basename(primary) == f"campaign_{current_inj_md5}":
            report("PASS", "P3a current-hash match", f"primary campaign dir hash matches live "
                   f"injector md5 ({current_inj_md5})")
        else:
            report("INFO", "P3a current-hash match", f"primary campaign dir = "
                   f"{os.path.basename(primary)}, live injector md5[:8] = {current_inj_md5} "
                   f"(differs -- injector was edited after the array ran, or this IS the "
                   f"pre-second-submission state; expected until §4.6 runs)")
    report("INFO", "P3a second-hash rerun", "not performed in this pass -- out of scope "
           "(handoff §4.6, requires manager authorization after this scorecard)")

    # (b) row count + mtime freshness, together (§6b.5)
    for i in range(7):
        tag = CELL_TAGS[i]
        cell_dir = os.path.join(primary, tag)
        idf_path = os.path.join(cell_dir, "injected.idf")
        if not os.path.isfile(idf_path):
            report("FAIL", f"P3b cell {i} ({tag})", f"injected.idf missing: {idf_path}")
            continue
        idf_mtime = os.path.getmtime(idf_path)
        for csv_name, cache in (("hourly_meters.csv", csvs_hourly), ("channel_hourly.csv", csvs_channel)):
            csv_path = os.path.join(cell_dir, csv_name)
            if not os.path.isfile(csv_path):
                report("FAIL", f"P3b cell {i} ({tag}) {csv_name}", "file missing")
                continue
            df = cache.get(i)
            n_rows = len(df) if df is not None else -1
            mtime = os.path.getmtime(csv_path)
            fresh = mtime > idf_mtime
            complete = (n_rows == 8760) and fresh
            status = "PASS" if complete else "FAIL"
            report(status, f"P3b cell {i} ({tag}) {csv_name}",
                   f"rows={n_rows} (want 8760), mtime={mtime:.0f} vs idf_mtime={idf_mtime:.0f} "
                   f"(fresh={fresh})")

    # =========================================================================
    # P4 -- fall-back loudness (cell 6, deliberately-missing retail CSV)
    # =========================================================================
    m6 = manifests.get(6)
    if m6 is None:
        report("FAIL", "P4 manifest", "cell 6 manifest missing")
    else:
        fb = m6.get("FALLBACK_LOUD")
        if fb == ["retail"]:
            report("PASS", "P4 FALLBACK_LOUD", f"cell 6 manifest FALLBACK_LOUD={fb}")
        else:
            report("FAIL", "P4 FALLBACK_LOUD", f"cell 6 manifest FALLBACK_LOUD={fb}, expected ['retail']")

        log_matches = sorted(glob.glob(os.path.join(LOGS_DIR, "8P_probe_*_6.out")))
        if not log_matches:
            report("FAIL", "P4 banner", f"no SLURM log matched 8P_probe_*_6.out under {LOGS_DIR}")
        else:
            found_banner = False
            hit_file = None
            for lp in log_matches:
                try:
                    with open(lp, "r", encoding="utf-8", errors="replace") as f:
                        if "!!! FALLBACK" in f.read():
                            found_banner = True
                            hit_file = lp
                            break
                except Exception:
                    continue
            status = "PASS" if found_banner else "FAIL"
            report(status, "P4 banner", f"'!!! FALLBACK' banner "
                   f"{'found in ' + hit_file if found_banner else 'NOT found'} (checked {log_matches})")

    if 6 in csvs_channel and 0 in csvs_channel:
        df6, df0 = csvs_channel[6], csvs_channel[0]
        retail_cols = [f"retail_{m}" for m in METRICS if f"retail_{m}" in df6.columns and f"retail_{m}" in df0.columns]
        n = min(len(df6), len(df0))
        identical = bool(retail_cols) and all((df6[c].iloc[:n] == df0[c].iloc[:n]).all() for c in retail_cols)
        max_d = max((_max_abs_delta(df6, df0, c) or 0.0) for c in retail_cols) if retail_cols else None
        status = "PASS" if identical else "FAIL"
        report(status, "P4 retail reversion identity",
               f"cell6 vs cell0 retail columns identical={identical}, max|delta|={max_d}")
    else:
        report("FAIL", "P4 retail reversion identity", "missing channel_hourly.csv for cell 0 or cell 6")

    _finish()


def _finish() -> None:
    print("\n=== §P PROBE SCORECARD ===")
    nP = nW = nF = nI = 0
    for r in RESULTS:
        print(f"[{r['status']}] {r['gate']} -- {r['detail']}")
        if r["status"] == "PASS":
            nP += 1
        elif r["status"] == "WARN":
            nW += 1
        elif r["status"] == "INFO":
            nI += 1
        else:
            nF += 1
    print(f"\nTOTAL: {nP}P / {nW}W / {nF}F / {nI} INFO")
    sys.exit(1 if nF > 0 else 0)


if __name__ == "__main__":
    main()
