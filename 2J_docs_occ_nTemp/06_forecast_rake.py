"""
06_forecast_rake.py — Phase 8B-6: 2030 AT_HOME Forecast Raking.

Projects per-(DDAY_STRATA × slot) observed AT_HOME marginals from cycles
2005→2010→2015→2022 forward to 2030 via linear OLS, then rakes
2030_synthetic_diaries.csv to match the projected targets.

Reuses _rake_binary_slot / _boundary_mask from 05_postlink_rake.py
(minimal-flip, boundary-preferred, seed=42). hom30 only — hard {0,1}.

Steps:
  1. Load augmented_diaries.csv (IS_SYNTHETIC==0), compute per-
     (CYCLE_YEAR × DDAY_STRATA × slot) mean hom30 → 4×3×48 table.
  2. Fit OLS (rate ~ year) per (DDAY_STRATA × slot), project to 2030,
     clamp [0,1] → target_2030[3×48].
  3. Model-vs-projection comparison: unraked 2030 hom30 rates vs targets.
  4. Rake 2030_synthetic_diaries.csv → target_2030 (hom30 only, all rows,
     minimal-flip, boundary-preferred, seed=42).
  5. Validate: swap raked file → run 06_longitudinalForecastingGSS_val.py
     → restore original. Report all gates.
  6. Cleanup + summary.

Writes 2030_synthetic_diaries_raked.csv atomically. Never modifies originals.
Run from any directory; paths derived from script location.
"""

import io
import os
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
import subprocess
import shutil
import numpy as np
import pandas as pd
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
_HERE          = Path(__file__).resolve().parent          # 2J_docs_occ_nTemp/
_BASE          = _HERE.parent                              # GSSCanada-main/
_FORECAST_DIR  = _BASE / "0_Occupancy" / "Outputs_21CEN22GSS" / "forecast_2030"
_STEP4_DIR     = _HERE / "outputs_step4"
_VALIDATOR     = (_BASE / "eSim_occ_utils" / "25CEN22GSS_classification"
                  / "06_longitudinalForecastingGSS_val.py")

_AUG_PATH      = _STEP4_DIR / "augmented_diaries.csv"
_DIARIES_2030  = _FORECAST_DIR / "2030_synthetic_diaries.csv"
_RAKED_OUT     = _FORECAST_DIR / "2030_synthetic_diaries_raked.csv"

# Column lists
N_SLOTS   = 48
HOM_COLS  = [f"hom30_{s:03d}" for s in range(1, N_SLOTS + 1)]
ACT_COLS  = [f"act30_{s:03d}" for s in range(1, N_SLOTS + 1)]
STRATA    = [1, 2, 3]
STRATA_LBL = {1: "WD", 2: "Sat", 3: "Sun"}
CYCLES    = [2005, 2010, 2015, 2022]
TARGET_YEAR = 2030

HOME_ACTS = {2, 3, 5, 6, 7, 10}  # HH Work, Caregiving, Sleep, Eating, PersonalCare, PassiveLeisure


# ── _rake_binary_slot / _boundary_mask (from 05_postlink_rake.py) ─────────────

def _boundary_mask(arr, t):
    """(n, T) binary float → (n,) bool: slot t is at run boundary."""
    val_t = arr[:, t]
    left  = (arr[:, t - 1] != val_t) if t > 0             else np.ones(len(arr), dtype=bool)
    right = (arr[:, t + 1] != val_t) if t < arr.shape[1] - 1 else np.ones(len(arr), dtype=bool)
    return left | right


def _rake_binary_slot(arr_col, target_count, boundary, rng):
    """Flip arr_col (in-place 1-D view) to hit target_count ones.
    Prefers boundary records; breaks ties with rng. Returns flip count."""
    n_cur = int(np.sum(arr_col == 1.0))
    delta = target_count - n_cur
    if delta == 0:
        return 0
    if delta > 0:
        candidates = np.where(arr_col == 0.0)[0]
        n_flip = min(delta, len(candidates))
    else:
        candidates = np.where(arr_col == 1.0)[0]
        n_flip = min(-delta, len(candidates))
    if n_flip == 0:
        return 0
    bnd_pri = boundary[candidates].astype(np.int8)
    noise   = rng.random(len(candidates))
    order   = np.lexsort((noise, -bnd_pri))
    chosen  = candidates[order[:n_flip]]
    arr_col[chosen] = 1.0 - arr_col[chosen]
    return n_flip


# ── Step 1: Observed marginals ─────────────────────────────────────────────────

def compute_observed_marginals(aug_path):
    """
    Returns obs_rates: dict[(cycle_year, stratum)] → np.ndarray shape (48,)
    using IS_SYNTHETIC==0 rows only.
    """
    print(f"\n[Step 1] Loading augmented_diaries.csv ...", flush=True)
    usecols = ["CYCLE_YEAR", "DDAY_STRATA", "IS_SYNTHETIC"] + HOM_COLS
    df = pd.read_csv(str(aug_path), usecols=usecols, low_memory=False)
    print(f"  Loaded {len(df):,} total rows", flush=True)

    obs = df[df["IS_SYNTHETIC"] == 0].copy()
    print(f"  IS_SYNTHETIC==0 rows: {len(obs):,}", flush=True)

    obs_rates = {}
    for yr in CYCLES:
        for s in STRATA:
            sub = obs[(obs["CYCLE_YEAR"] == yr) & (obs["DDAY_STRATA"] == s)]
            if len(sub) == 0:
                print(f"  [WARN] year={yr} strata={s}: 0 rows", flush=True)
                obs_rates[(yr, s)] = np.zeros(N_SLOTS)
            else:
                obs_rates[(yr, s)] = sub[HOM_COLS].values.astype(float).mean(axis=0)
    print(f"  Observed marginals computed for {len(obs_rates)} (year×stratum) cells", flush=True)
    return obs_rates


# ── Step 2: Structural-break p=1 projection to 2030 ───────────────────────────
#
# Method: "COVID = permanent level shift, underlying growth continues"
#   1. Fit pre-COVID slope on cycles 2005/2010/2015 only.
#   2. jump_st = obs[2022,s,t] - trend_st(2022)          (2022 residual above trend)
#   3. target_2030[s,t] = obs[2022,s,t] + 8 * pre_slope  (= trend_st(2030) + jump)
#   4. Clamp [0,1].
#
# Expected sanity: WD ~78.4%, WE ~80.4%.

PRE_COVID_CYCLES = [2005, 2010, 2015]

def project_to_2030(obs_rates):
    """
    Structural-break projection: pre-COVID trend (2005/2010/2015) + permanent
    COVID level shift. Returns target_2030 shape (3, 48), pre_slopes (3, 48),
    and per-stratum report dict.
    """
    print(f"\n[Step 2] Structural-break p=1 projection to {TARGET_YEAR} ...", flush=True)
    pre_years = np.array(PRE_COVID_CYCLES, dtype=float)
    target      = np.zeros((3, N_SLOTS))
    pre_slopes  = np.zeros((3, N_SLOTS))
    n_clamped   = 0

    for si, s in enumerate(STRATA):
        pre_matrix = np.stack([obs_rates[(yr, s)] for yr in PRE_COVID_CYCLES], axis=0)  # (3, 48)
        obs_2022   = obs_rates[(2022, s)]                                                 # (48,)
        for t in range(N_SLOTS):
            coef = np.polyfit(pre_years, pre_matrix[:, t], 1)   # slope, intercept
            pre_slopes[si, t] = coef[0]
            # target = obs_2022[t] + 8 * slope  (equiv. trend_2030 + jump)
            raw = obs_2022[t] + 8.0 * coef[0]
            clamped = max(0.0, min(1.0, raw))
            if clamped != raw:
                n_clamped += 1
            target[si, t] = clamped

    print(f"  Slots clamped to [0,1]: {n_clamped}", flush=True)

    # Reporting
    print(f"\n  Structural-break 2030 targets per stratum:", flush=True)
    print(f"  {'Strata':<8} {'Daily AT_HOME %':>15} {'In [55,90]?':>12} {'vs 2022 (dpp)':>14}", flush=True)
    print(f"  {'-'*55}", flush=True)

    reports = {}
    for si, s in enumerate(STRATA):
        daily_2030 = target[si].mean() * 100
        daily_2022 = obs_rates[(2022, s)].mean() * 100
        delta      = daily_2030 - daily_2022
        in_range   = 55.0 <= daily_2030 <= 90.0
        print(f"  {STRATA_LBL[s]:<8} {daily_2030:>15.2f}% {str(in_range):>12} {delta:>+14.2f} pp", flush=True)
        reports[s] = {"daily_2030": daily_2030, "daily_2022": daily_2022, "delta": delta, "in_range": in_range}

    print(f"\n  NOTE: COVID-persists assumption — 2022 level shift treated as permanent;", flush=True)
    print(f"  underlying pre-COVID growth projected forward. Model-vs-projection override", flush=True)
    print(f"  is INTENDED (user/manager call: adopt COVID-persists target).", flush=True)

    return target, pre_slopes, None, reports


# ── Step 3: Model-vs-projection comparison ─────────────────────────────────────

def compare_model_vs_projection(df_2030, target_2030):
    """
    Computes existing unraked 2030 per-(stratum × slot) hom30 rates, then
    reports per-stratum daily |Δ| and per-slot max |Δ| vs target_2030.
    """
    print(f"\n[Step 3] Model-vs-projection comparison ...", flush=True)
    model_rates = np.zeros((3, N_SLOTS))
    for si, s in enumerate(STRATA):
        sub = df_2030[df_2030["DDAY_STRATA"] == s]
        if len(sub) == 0:
            print(f"  [WARN] stratum {s}: 0 rows in 2030 diaries", flush=True)
        else:
            model_rates[si] = sub[HOM_COLS].values.astype(float).mean(axis=0)

    print(f"\n  Per-stratum daily |Δ| (model vs projection):", flush=True)
    print(f"  {'Strata':<8} {'Model daily%':>13} {'Target daily%':>14} {'|Δ| pp':>10} {'Flag?':>8}", flush=True)
    print(f"  {'-'*60}", flush=True)

    max_slot_delta = {}
    daily_deltas   = {}
    for si, s in enumerate(STRATA):
        model_daily  = model_rates[si].mean() * 100
        target_daily = target_2030[si].mean() * 100
        daily_d      = abs(model_daily - target_daily)
        slot_deltas  = np.abs(model_rates[si] - target_2030[si]) * 100
        max_slot_d   = slot_deltas.max()
        flag = "FLAG" if daily_d > 3.0 or max_slot_d > 8.0 else "ok"
        print(f"  {STRATA_LBL[s]:<8} {model_daily:>13.2f}% {target_daily:>14.2f}% {daily_d:>10.2f} pp {flag:>8}", flush=True)
        daily_deltas[s]   = daily_d
        max_slot_delta[s] = max_slot_d

    print(f"\n  Per-stratum per-slot max |Δ| (model vs projection):", flush=True)
    for si, s in enumerate(STRATA):
        print(f"    {STRATA_LBL[s]}: max slot |Δ| = {max_slot_delta[s]:.2f} pp", flush=True)

    return model_rates, daily_deltas, max_slot_delta


# ── Step 4: Rake 2030 diaries ─────────────────────────────────────────────────

def rake_2030(df_2030, target_2030):
    """
    Rakes all rows of 2030_synthetic_diaries.csv per (DDAY_STRATA × slot) so
    hom30 rate == target_2030[si, t]. hom30 only. Returns raked df + stats.
    """
    print(f"\n[Step 4] Raking 2030 diaries ...", flush=True)
    n_total = len(df_2030)
    print(f"  Total rows: {n_total:,}", flush=True)

    # Hard-binary pre-assertion
    hom_pre = df_2030[HOM_COLS].values.astype(float)
    assert set(np.unique(hom_pre[~np.isnan(hom_pre)])).issubset({0.0, 1.0}), \
        "hom30 not hard 0/1 before raking"
    print(f"  hom30 pre-rake: hard 0/1 confirmed", flush=True)

    hom_pre_copy = hom_pre.copy()   # for coherence cost

    rng = np.random.default_rng(42)
    total_flips = 0
    df_work = df_2030.copy()
    hom_arr_full = df_work[HOM_COLS].values.astype(float)

    for si, s in enumerate(STRATA):
        s_mask   = (df_work["DDAY_STRATA"] == s).values
        s_idx    = np.where(s_mask)[0]
        if len(s_idx) == 0:
            print(f"  stratum {s}: 0 rows — skip", flush=True)
            continue
        hom_arr_s = hom_arr_full[s_idx]          # (n_s, 48) — view into full array
        n_s = len(s_idx)

        for t in range(N_SLOTS):
            tgt = max(0, min(n_s, int(round(target_2030[si, t] * n_s))))
            bnd = _boundary_mask(hom_arr_s, t)
            total_flips += _rake_binary_slot(hom_arr_s[:, t], tgt, bnd, rng)

        hom_arr_full[s_idx] = hom_arr_s
        print(f"  stratum {si+1} ({STRATA_LBL[s]}): {n_s} rows raked", flush=True)

    df_work[HOM_COLS] = hom_arr_full
    hom_post = hom_arr_full

    # Hard-binary post-assertion
    assert set(np.unique(hom_post[~np.isnan(hom_post)])).issubset({0.0, 1.0}), \
        "hom30 not hard 0/1 after raking — ABORT"
    assert len(df_work) == n_total, f"Row count changed: {len(df_work)} != {n_total}"
    print(f"  Assertions: hom30 hard 0/1 OK; row count {len(df_work):,} OK", flush=True)
    print(f"  Total hom30 flips: {total_flips:,}", flush=True)

    # Coherence cost: hom30 1→0 AND act30 in HOME_ACTS
    flipped_1to0 = (hom_pre_copy == 1.0) & (hom_post == 0.0)
    act_arr      = df_work[ACT_COLS].values.astype(float)
    incoherence  = 0
    for t in range(N_SLOTS):
        col_flip = flipped_1to0[:, t]
        if not col_flip.any():
            continue
        acts_t = act_arr[col_flip, t]
        incoherence += int(np.isin(acts_t, list(HOME_ACTS)).sum())

    total_1to0 = int(flipped_1to0.sum())
    total_0to1 = int(((hom_pre_copy == 0.0) & (hom_post == 1.0)).sum())
    print(f"  Flips 1→0 (away-ified): {total_1to0:,}", flush=True)
    print(f"  Flips 0→1 (homed-back): {total_0to1:,}", flush=True)
    print(f"  Act/hom incoherences (1→0 AND act30 ∈ HOME_ACTS): {incoherence:,}", flush=True)

    return df_work, total_flips, total_1to0, total_0to1, incoherence


# ── Step 5: Validate ───────────────────────────────────────────────────────────

def validate_raked(df_raked, target_2030):
    """
    Swap raked file into FORECAST_DIR/2030_synthetic_diaries.csv,
    run 06_longitudinalForecastingGSS_val.py, restore original.
    Returns (validator_output, gate_results, residuals).
    """
    print(f"\n[Step 5] Validation ...", flush=True)

    orig_path   = _DIARIES_2030
    backup_path = _FORECAST_DIR / "2030_synthetic_diaries_ORIG_BAK.csv"
    tmp_swap    = _FORECAST_DIR / "2030_synthetic_diaries.tmp"

    # Write raked file to tmp in FORECAST_DIR
    print(f"  Writing raked to tmp ...", flush=True)
    df_raked.to_csv(str(tmp_swap), index=False)

    # Backup original
    shutil.copy2(str(orig_path), str(backup_path))
    print(f"  Backed up original → {backup_path.name}", flush=True)

    # Place raked
    os.replace(str(tmp_swap), str(orig_path))
    print(f"  Raked file placed at {orig_path.name}", flush=True)

    # Run validator
    validator_out = ""
    try:
        print(f"  Running validator ...", flush=True)
        env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
        result = subprocess.run(
            [sys.executable, str(_VALIDATOR)],
            capture_output=True, text=True, encoding="utf-8", timeout=300,
            env=env
        )
        validator_out = result.stdout + ("\n[STDERR]\n" + result.stderr if result.stderr.strip() else "")
        print(validator_out, flush=True)
    except Exception as e:
        print(f"  [ERROR] Validator failed: {e}", flush=True)
        validator_out = f"ERROR: {e}"
    finally:
        # Always restore original
        os.replace(str(backup_path), str(orig_path))
        print(f"  Original restored from backup.", flush=True)

    # ── Parse section-5 gate verdicts from validator output ──────────────────
    gate_results = _parse_gates(validator_out)

    # ── Residual: raked rates vs target_2030 ─────────────────────────────────
    residuals = {}
    for si, s in enumerate(STRATA):
        sub = df_raked[df_raked["DDAY_STRATA"] == s]
        if len(sub) == 0:
            continue
        raked_rates = sub[HOM_COLS].values.astype(float).mean(axis=0)
        res = np.abs(raked_rates - target_2030[si]) * 100
        residuals[s] = {"max_pp": float(res.max()), "mean_pp": float(res.mean())}
    print(f"\n  Raked-vs-target residual (should be ≈0 by construction):", flush=True)
    for s in STRATA:
        if s in residuals:
            print(f"    {STRATA_LBL[s]}: max {residuals[s]['max_pp']:.3f} pp  mean {residuals[s]['mean_pp']:.3f} pp", flush=True)

    return validator_out, gate_results, residuals


def _parse_gates(output):
    """Extract PASS/FAIL/WARN for sections 5.x from validator stdout."""
    import re
    gates = {}
    pattern = re.compile(r"\[\s*(PASS|FAIL|WARN|SKIP)\s*\]\s*([\d\.]+[^:]+):\s*(.*)")
    for line in output.splitlines():
        m = pattern.search(line)
        if m:
            verdict = m.group(1)
            name    = m.group(2).strip()
            value   = m.group(3).strip()
            gates[name] = (verdict, value)
    return gates


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("=" * 72, flush=True)
    print("06_forecast_rake.py — Phase 8B-6: 2030 AT_HOME Forecast Raking", flush=True)
    print("=" * 72, flush=True)

    # ── Step 0: Assert inputs exist ──────────────────────────────────────────
    print("\n[Step 0] Checking inputs ...", flush=True)
    for p, label in [(_AUG_PATH, "augmented_diaries.csv"),
                     (_DIARIES_2030, "2030_synthetic_diaries.csv"),
                     (_FORECAST_DIR / "reconstructed_2022_diaries.csv", "reconstructed_2022_diaries.csv"),
                     (_VALIDATOR, "06_longitudinalForecastingGSS_val.py")]:
        ok = p.exists()
        print(f"  {'OK' if ok else 'MISSING'}: {label} — {p}", flush=True)
        if not ok:
            raise FileNotFoundError(f"Required file not found: {p}")

    # Schema check on 2030 file
    df_2030 = pd.read_csv(str(_DIARIES_2030), low_memory=False)
    print(f"\n  2030 diaries: {len(df_2030):,} rows × {df_2030.shape[1]} cols", flush=True)
    for req in ["occID", "CYCLE_YEAR", "DDAY_STRATA"] + HOM_COLS[:3]:
        assert req in df_2030.columns, f"Column '{req}' missing from 2030 diaries"
    for unexpected in ["IS_SYNTHETIC", "HH_ID"]:
        if unexpected in df_2030.columns:
            print(f"  [WARN] Unexpected column '{unexpected}' present", flush=True)
    assert set(df_2030["DDAY_STRATA"].unique()) == {1, 2, 3}, "DDAY_STRATA not {1,2,3}"
    assert set(df_2030["CYCLE_YEAR"].unique()) == {2030}, "CYCLE_YEAR not {2030}"
    print(f"  Schema assertions passed.", flush=True)

    # ── Steps 1 & 2 ──────────────────────────────────────────────────────────
    obs_rates           = compute_observed_marginals(_AUG_PATH)
    target_2030, slopes, intercepts, proj_reports = project_to_2030(obs_rates)

    # ── Step 3 ────────────────────────────────────────────────────────────────
    model_rates, daily_deltas, max_slot_deltas = compare_model_vs_projection(df_2030, target_2030)

    # ── Rake: Step 4 ──────────────────────────────────────────────────────────
    df_raked, total_flips, n_1to0, n_0to1, incoherence = rake_2030(df_2030, target_2030)

    # Write deliverable atomically
    print(f"\n  Writing raked deliverable → {_RAKED_OUT.name} ...", flush=True)
    tmp_path = str(_RAKED_OUT) + ".tmp"
    df_raked.to_csv(tmp_path, index=False)
    n_written = sum(1 for _ in open(tmp_path, encoding="utf-8")) - 1
    assert n_written == len(df_raked), f"Write row mismatch: {n_written} != {len(df_raked)}"
    os.replace(tmp_path, str(_RAKED_OUT))
    print(f"  WRITTEN: {n_written:,} rows → {_RAKED_OUT}", flush=True)

    # ── Step 5: Validate ──────────────────────────────────────────────────────
    validator_out, gate_results, residuals = validate_raked(df_raked, target_2030)

    # ── Raked WD/WE daily AT_HOME vs 2022 (continuity) ───────────────────────
    print(f"\n  Raked 2030 daily AT_HOME vs observed 2022 (continuity check):", flush=True)
    print(f"  {'Strata':<8} {'Raked 2030%':>12} {'Obs 2022%':>10} {'Δ pp':>8}", flush=True)
    print(f"  {'-'*45}", flush=True)
    for si, s in enumerate(STRATA):
        sub_raked = df_raked[df_raked["DDAY_STRATA"] == s]
        raked_daily = sub_raked[HOM_COLS].values.astype(float).mean() * 100 if len(sub_raked) > 0 else float("nan")
        obs_2022_daily = obs_rates[(2022, s)].mean() * 100
        delta = raked_daily - obs_2022_daily
        print(f"  {STRATA_LBL[s]:<8} {raked_daily:>12.2f}% {obs_2022_daily:>10.2f}% {delta:>+8.2f} pp", flush=True)

    # ── Gate summary ─────────────────────────────────────────────────────────
    print(f"\n{'='*72}", flush=True)
    print("GATE SUMMARY — Phase 8B-6", flush=True)
    print(f"{'='*72}", flush=True)

    # Projection plausibility
    all_in_range = all(r["in_range"] for r in proj_reports.values())
    print(f"\n  Projected targets plausibility:", flush=True)
    for s, r in proj_reports.items():
        flag = "PASS" if r["in_range"] else "FAIL"
        print(f"    {STRATA_LBL[s]}: {r['daily_2030']:.2f}% daily AT_HOME — {flag} (gate 55–90%)", flush=True)
        print(f"      COVID: {r['delta']:+.2f} pp vs 2022 — linear-through-2022 carries COVID elevation forward", flush=True)

    # Model-vs-projection delta (labelled INTENDED — user/manager COVID-persists call)
    print(f"\n  Model-vs-projection |Δ| per stratum (INTENDED — COVID-persists override):", flush=True)
    any_flag = False
    for s in STRATA:
        daily_d = daily_deltas[s]
        max_d   = max_slot_deltas[s]
        # Divergence is expected/intended; report size but do not trigger stop
        flag = "INTENDED" if daily_d > 3.0 or max_d > 8.0 else "ok"
        print(f"    {STRATA_LBL[s]}: daily |Δ| {daily_d:.2f} pp  max slot |Δ| {max_d:.2f} pp — {flag}", flush=True)

    # Validator gate scorecard (section 5 checks)
    print(f"\n  Validator gate scorecard (section 5/6 checks):", flush=True)
    all_gates_pass = True
    for name, (verdict, value) in sorted(gate_results.items()):
        tag = verdict
        if tag == "FAIL":          # WARN is not a gate failure
            all_gates_pass = False
        print(f"    [{tag}] {name}: {value}", flush=True)
    if not gate_results:
        print(f"    (No gate lines parsed from validator output — check validator output above)", flush=True)
        all_gates_pass = None

    # Residual
    print(f"\n  Raked-vs-target residual:", flush=True)
    for s, r in residuals.items():
        print(f"    {STRATA_LBL[s]}: max {r['max_pp']:.3f} pp  mean {r['mean_pp']:.3f} pp", flush=True)

    # Coherence cost
    total_syn_slots = len(df_raked) * N_SLOTS
    pct = incoherence / total_syn_slots * 100
    print(f"\n  Act/hom coherence cost: {incoherence:,} new incoherences = {pct:.2f}% of slot-records", flush=True)

    # 8B-6 verdict
    print(f"\n{'='*72}", flush=True)
    print("8B-6 DECISION GATE VERDICT:", flush=True)
    if all_gates_pass is False:
        print("  *** FAIL ***  One or more validator gates fail post-rake. Investigate.", flush=True)
    elif all_gates_pass is True and all_in_range:
        print("  *** PASS ***  Validator gates pass. Targets plausible (COVID-persists).", flush=True)
        print("  Model-vs-projection override is INTENDED (user/manager COVID-persists call).", flush=True)
        print("  Report the override delta size above — do not stop.", flush=True)
    else:
        print("  *** UNCLEAR — see gate details above ***", flush=True)
    print(f"{'='*72}", flush=True)


if __name__ == "__main__":
    main()
