#!/usr/bin/env python3
"""
3rdJ_06_calibrate_C_4split.py  (2026-07-23)  --  Step 6 Track A Part 2 (Leg-3 4-split)

ONE combined post-hoc, no-retrain calibration chain on the RAW 2030 deliverable
(the runbook names exactly one combined script -- do not split into two):

  Stage B  -- weekday work-tail trim            (Calibration-B port, per band)
  [global 04M min-dwell pass -- 3rdJ_04M_mindwell_4split.py, subprocess]
  Stage C0 -- weekend work cap                   (Calibration-C Stage 0 port)
  Stage C1 -- weekend home restore + local mindwell (Calibration-C Stage 1 port)
  Stage RETAIL -- retail cap, target-anchored     ([Leg-3 NEW])
  Stage C2 -- activity restore, 4-state donor     (Calibration-C Stage 2 port, +RETAIL state)

Fork bases (Leg-2, verbatim mechanics per the builder prompt):
  Leg2_2-split/Step6_docs/calibrate_weekday_work_2split.py                (Stage B)
  Leg2_2-split/Step6_docs/3rdJ_06_calibrate_C_activity_weekend_2split.py  (Stage C0/C1/C2)
  (forked from the FIXED, current version -- mtime 2026-07-17 -- NOT the
   archive/..._pre_mutexfix.py variant, per runbook SS6H(a).)

INPUT = the RAW per-band 2030 diaries (2030_diaries_{band}_raw.csv), i.e.
PRE-mindwell (confirmed against runbook line 66-67: "No 04L marginal rake on
the forecast year ... Canonical deliverable: ... the calibration-B/C ports
... run against observed-2022 anchors exactly as in Leg 2" -- the Leg-2 base
scripts both take the RAW/PRE-calibration deliverable as their Input A, never
the build's own *_mindwell.csv intermediate, which would double-apply
mindwell smoothing before Stage B even runs). The 3 raw per-band CSVs are
concatenated in-process into one combined frame identical in content to the
cluster's own 2030_synthetic_diaries_4split_raw.csv (that 81MB combined file
itself is intentionally NOT downloaded/read, per the Step-0 staging note).

DESIGN DELTA vs the Leg-2 file-based pipeline: Leg-2 staged each stage's
output as an intermediate CSV (..._calibrated.csv, ..._calibrated_mindwell.csv)
before Calibration-C read the next one back in. This Leg-3 script keeps
every stage in-memory in ONE process and writes ONLY the final canonical
`_C` deliverable -- this satisfies the runbook's "ONE combined file" intent
and sidesteps the "non-_C glob hazard" file-hygiene requirement entirely
(no superseded intermediate CSVs are ever created in outputs_step6/). The
04M min-dwell smoothing itself still shells out to the REAL
3rdJ_04M_mindwell_4split.py (not a re-implementation) via a CSV round-trip
through a throwaway tempfile.mkdtemp() directory outside outputs_step6/, so
the canonical production min-dwell logic is used verbatim, not re-derived.

3-WAY MUTEX GUARD -- priority order DECIDED by the manager: work > retail > home.
Rationale (recorded per the task instructions): work is the most
behaviorally-constrained / least-ambiguous signal (a work slot implies a
verifiable employment commitment); retail implies a verifiable trip (a
person cannot be simultaneously elsewhere); home is the default/residual
state, the correct one to yield when a conflict must be broken. Implemented
as a HARD gate after EVERY single-channel smoothing/raking pass touching
any of {home, work, retail} (per runbook SS6H(b)): recompute all 3 pairwise
conflict masks, resolve deterministically by the priority order above, print
the count cleared, then hard-`assert` 0 remain -- AssertionError abort, never
warn (the Leg-2 2026-07-17 mutex-bug lesson: 4,280 impossible cells reached
a 72-task re-sim because no downstream validator checked mutex either).

Retail cap stage ([Leg-3 NEW], target-anchored per runbook line 67): caps
2030 per-slot retail (ret30) at observed-2022 profile x lever value. NEVER
delta-subtraction (the Leg-2 over-correction lesson) -- every flip decision
recomputes the CURRENT per-slot rate fresh immediately before deciding how
many person-slots to move, rather than reusing a rate/delta cached from an
earlier snapshot. Upward flips (need MORE retail) recruit exclusively from
the OUT state (hom30==0 & wrk30==0 & ret30==0) -- never poach from home/work,
which would itself create a fresh mutex conflict. Downward flips (need LESS
retail) simply clear ret30 1->0, leaving the row as generic OUT (state is
re-derived correctly by Stage C2's activity restore below). Default lever =
"plateau" (0.97, the Plateau/Resilient Central scenario) -- this produces
the ONE canonical deliverable; the other two named scenarios (shift=0.90,
conservative; renaissance=1.05, optimistic) are available via
--retail_lever for a cheap re-run of this same script (runbook line 59:
"Sensitivity bands = re-run, not retrain") without needing a second
model-side pass.

I/O:
  Input  (2030, x3 bands): Step6_docs/outputs_step6/2030_diaries_{band}_raw.csv
  Input  (2022 observed):  Step5_docs/outputs_step5/3rdJ_25CEN_aug_Full_Aggregated_excl.csv
  Output (canonical):      Step6_docs/outputs_step6/2030_synthetic_diaries_4split_calibrated_mindwell_C.csv

seed=42 throughout (Calibration-B, C0, C1, retail-cap, C2 all draw from ONE
np.random.default_rng(42), advanced sequentially in stage order -- matches
the Leg-2 base scripts' single-seed discipline). pandas + numpy only.
Vectorized per-slot x state group draws -- never a per-row Python loop for
the O(N) donor-resample stage. Atomic write (.tmp -> os.replace) + one
_BAK_<date> backup. CPU, expected a few minutes on 111,024 rows (3 bands x
37,008).

2026-07-30 FIX (3rdJ_L3_improvements_step5_6_7.md SS A.1-A.7) -- Stage B
(cap_band_stageB) and Stage C0 (run_stage_C0) were UNIDIRECTIONAL trims
(guard `if rate <= target: continue` / `if p_30 <= p_obs: continue`): they
could only push work-presence DOWN toward the observed-2022 target, never
lift a synthetic-decoder deficit. Since the trained decoder under-produces
AT_WORK, calibration was AMPLIFYING the bias instead of correcting it
(measured: -10.51pp work-presence, 2030 vs OBS2022, vs a ~2.4pp between-band
WFH signal -- the bias was 4-5x the signal). Both stages are now
bidirectional: an UP branch (mirroring the already-bidirectional Stage C1
template, :452-509) lifts a deficit by recruiting candidates EXCLUSIVELY
from the OUT state (hom==0 & wrk==0 & ret==0) -- mutex-safe by construction,
never poaching home/retail -- and prefers extending an existing work block's
tail/head before creating an isolated flip (mirrors the DOWN trim's own
trail/lead/anyone preference, :349-357). Stage B's UP branch also sets
ACT=WORK_ACT_0IDX on lifted slots (inverse of the DOWN trim's SLEEP/PASSIVE
reset, :362-363); Stage C0 does not touch ACT on either branch, matching its
own pre-existing DOWN branch and Stage C1's HOME UP/DOWN branches (ACT is
fully re-derived downstream by Stage C2's 4-state donor resample regardless
of what Stage B/C0/C1/Retail did to it in the interim).

Anchor purification (A.7): `obs22` (Input B, IN_B) was read via
`CYCLE_YEAR==2022` with NO `IS_SYNTHETIC` filter, so Stage B/C0 targets were
computed against a pool contaminated 44.5% overall / 27.6% weekday / 87.1%
Saturday / 86.7% Sunday with synthetic (already-decoded) diaries -- and
Stage C0 consumes exactly the weekend anchor. `--pure-anchor` (default ON)
filters obs22 to IS_SYNTHETIC==0; `--no-pure-anchor` reproduces the
contaminated baseline for comparison. `--out_tag TAG` redirects the output
to `..._C_TAG.csv` instead of the canonical `..._C.csv` -- use for any
non-canonical/test run; the canonical deliverable
(2030_synthetic_diaries_4split_calibrated_mindwell_C.csv, MD5 7c105ef3...,
111,024 rows, produced 2026-07-23 by the pre-fix asymmetric code) is NEVER
overwritten by this script's default path.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent                 # Step6_docs/
BASE = HERE.parent.parent.parent                       # GSSCanada-main/
OUT_DIR = HERE / "outputs_step6"

STEP4_DIR = HERE.parent / "Step4_docs"
MINDWELL_SCRIPT = STEP4_DIR / "3rdJ_04M_mindwell_4split.py"

IN_B = (BASE / "3J_docs_occ_nTemp" / "Leg3_4-split" / "Step5_docs" / "outputs_step5"
        / "3rdJ_25CEN_aug_Full_Aggregated_excl.csv")
OUT_C = OUT_DIR / "2030_synthetic_diaries_4split_calibrated_mindwell_C.csv"

# ---------------------------------------------------------------------------
# Column groups
# ---------------------------------------------------------------------------
N_SLOTS = 48
HOM = [f"hom30_{i:03d}" for i in range(1, N_SLOTS + 1)]
WRK = [f"wrk30_{i:03d}" for i in range(1, N_SLOTS + 1)]
RET = [f"ret30_{i:03d}" for i in range(1, N_SLOTS + 1)]
ACT = [f"act30_{i:03d}" for i in range(1, N_SLOTS + 1)]

BIZ = list(range(10, 26))            # 0-indexed business slots 11-26
BIZ_SET = set(BIZ)
# Raw act30 code table (0-indexed here; raw code = idx+1) -- AUTHORITATIVE, confirmed
# against 3rdJ_03_mergingGSS_4split.py::BEM_PRIORITY and the ACT_LABELS dict reused
# verbatim across Step2/Step5 (3rdJ_02_harmonizeGSS_4split_val.py,
# 3rdJ_05_censusLinkage_4split_val.py): 1=Work, 2=HH Work, 3=Caregiving, 4=Purchasing,
# 5=Sleep&Rest, 6=Eating, 7=Personal Care, 8=Education, 9=Socializing, 10=Passive
# Leisure, 11=Active Leisure, 12=Community, 13=Travel, 14=Misc/Idle. NOTE: this is
# DIFFERENT from the main build script's ACT_NAMES list (3rdJ_06_longitudinalForecasting
# _4split.py) -- that list is a DRIFT_MATRIX column-LABEL order only, not the raw act30
# code order; naively porting Leg-2's "(0, 13, 10)" 0-indexed constants (its own,
# internally-consistent 2-split code table) would have silently mislabeled every
# Stage-B work-tail-trim flip. Verified empirically: pooled raw 2030 act30 code
# distribution has code 5 as the dominant ~26.9% share (consistent with Sleep&Rest
# being the most common activity), code 14 only ~8.1% -- confirms the ACT_LABELS
# table above, not the ACT_NAMES list, is authoritative for raw code values.
WORK_ACT_0IDX, SLEEP_ACT_0IDX, PASSIVE_ACT_0IDX = 0, 4, 9   # 0-indexed
NIGHT = set(list(range(0, 12)) + list(range(44, 48)))         # 00:00-06:00 & 22:00-24:00

BANDS = ["conservative", "hybrid", "fullyhybrid"]
WEEKEND_STRATA = [2, 3]
WEEKDAY_STRATA = [1]
SMALL_CELL = 20

# State codes (4-way, extends Leg-2's 3-way OUT/HOME/WORK with RETAIL)
STATE_OUT, STATE_HOME, STATE_WORK, STATE_RETAIL = 0, 1, 2, 3
STATE_NAMES = {STATE_OUT: "OUT", STATE_HOME: "HOME", STATE_WORK: "WORK", STATE_RETAIL: "RETAIL"}

DAYTIME_IDX = list(range(10, 26))
DAYTIME_HOM = [HOM[i] for i in DAYTIME_IDX]

LEVERS = {"plateau": 0.97, "shift": 0.90, "renaissance": 1.05}

MET = {
    0: 0, 1: 125, 2: 175, 3: 190, 4: 195, 5: 70, 6: 105,
    7: 170, 8: 110, 9: 90, 10: 85, 11: 245, 12: 105, 13: 140, 14: 135,
}


# ---------------------------------------------------------------------------
# 3-way mutex guard (hard gate; the runbook's belt-and-braces final pass)
# ---------------------------------------------------------------------------
def resolve_and_assert_mutex(out: pd.DataFrame, label: str) -> None:
    """
    [runbook SS6H(b)/(c)] Recompute all 3 pairwise conflict masks
    (home&work, home&retail, work&retail), resolve deterministically by
    priority work > retail > home, print the count cleared, then hard-assert
    0 remain. Never warn -- AssertionError abort on any residual conflict.
    """
    hom_v = out[HOM].values
    wrk_v = out[WRK].values
    ret_v = out[RET].values

    hw = (hom_v == 1) & (wrk_v == 1)
    hr = (hom_v == 1) & (ret_v == 1)
    wr = (wrk_v == 1) & (ret_v == 1)
    n_hw, n_hr, n_wr = int(hw.sum()), int(hr.sum()), int(wr.sum())
    n_total = n_hw + n_hr + n_wr

    if n_total > 0:
        # Priority: work > retail > home. A HOME&WORK conflict -> drop HOME
        # (work wins). A HOME&RETAIL conflict -> drop HOME (retail wins). A
        # WORK&RETAIL conflict -> drop RETAIL (work wins). Apply in-place.
        hom_v = hom_v.copy()
        ret_v = ret_v.copy()
        hom_v[hw] = 0
        hom_v[hr] = 0
        ret_v[wr] = 0
        out.loc[:, HOM] = hom_v
        out.loc[:, RET] = ret_v
        print(f"  [6H MUTEX] {label}: cleared home&work={n_hw:,} (->home=0), "
              f"home&retail={n_hr:,} (->home=0), work&retail={n_wr:,} (->retail=0) "
              f"[priority work > retail > home]", flush=True)
    else:
        print(f"  [6H MUTEX] {label}: 0 violations (clean)", flush=True)

    # Hard re-check post-resolution (the actual gate)
    hom_v2 = out[HOM].values
    wrk_v2 = out[WRK].values
    ret_v2 = out[RET].values
    n_hw2 = int(((hom_v2 == 1) & (wrk_v2 == 1)).sum())
    n_hr2 = int(((hom_v2 == 1) & (ret_v2 == 1)).sum())
    n_wr2 = int(((wrk_v2 == 1) & (ret_v2 == 1)).sum())
    assert n_hw2 == 0 and n_hr2 == 0 and n_wr2 == 0, (
        f"[6H MUTEX GUARD FAIL] {label}: residual conflicts after resolution "
        f"home&work={n_hw2}, home&retail={n_hr2}, work&retail={n_wr2} -- abort "
        f"per the hard-assertion discipline (never warn)."
    )


# ---------------------------------------------------------------------------
# Min-dwell smoother (ported verbatim from 3rdJ_04M_mindwell_4split.py's own
# apply_min_dwell(), reused here ONLY for Stage C1's LOCAL weekend-hom30-only
# pass; the GLOBAL pass shells out to the real script -- see call_mindwell()).
# ---------------------------------------------------------------------------
def apply_min_dwell(arr: np.ndarray, min_dwell: int = 2) -> tuple[np.ndarray, int]:
    if min_dwell <= 1:
        return arr.copy(), 0
    arr = arr.copy()
    n_rows, n_cols = arr.shape
    total_changed = 0
    for _pass in range(min_dwell):
        changed_this_pass = 0
        for i in range(n_cols):
            col_i = arr[:, i]
            if i == 0:
                right = arr[:, 1]
                flip = col_i != right
                arr[flip, i] = right[flip]
                changed_this_pass += int(flip.sum())
            elif i == n_cols - 1:
                left = arr[:, n_cols - 2]
                flip = col_i != left
                arr[flip, i] = left[flip]
                changed_this_pass += int(flip.sum())
            else:
                left = arr[:, i - 1]
                right = arr[:, i + 1]
                flip = (col_i != left) & (col_i != right)
                arr[flip, i] = left[flip]
                changed_this_pass += int(flip.sum())
        total_changed += changed_this_pass
        if changed_this_pass == 0:
            break
    return arr, total_changed


def call_mindwell_global(df: pd.DataFrame) -> pd.DataFrame:
    """Shell out to the REAL 3rdJ_04M_mindwell_4split.py via a CSV round-trip
    through a throwaway tempdir (outside outputs_step6/, so no intermediate
    files are ever left beside the canonical deliverable)."""
    tmpdir = tempfile.mkdtemp(prefix="calibC4split_mindwell_")
    in_csv = os.path.join(tmpdir, "in.csv")
    out_csv = os.path.join(tmpdir, "out.csv")
    try:
        df.to_csv(in_csv, index=False)
        cmd = [sys.executable, str(MINDWELL_SCRIPT), "--in_csv", in_csv, "--out_csv", out_csv]
        print(f"  [MINDWELL] calling {MINDWELL_SCRIPT.name} on {len(df):,} rows ...", flush=True)
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(result.stdout[-3000:])
            print(result.stderr[-3000:])
            raise RuntimeError(f"04M min-dwell subprocess failed (exit {result.returncode})")
        out = pd.read_csv(out_csv, low_memory=False)
        print(f"  [MINDWELL] complete, {len(out):,} rows returned", flush=True)
        return out
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ---------------------------------------------------------------------------
# Atomic write
# ---------------------------------------------------------------------------
def atomic_write(df: pd.DataFrame, path: Path) -> None:
    today = datetime.date.today().isoformat()
    if path.exists():
        bak = path.parent / f"{path.stem}_BAK_{today}{path.suffix}"
        if not bak.exists():
            shutil.copy2(path, bak)
            print(f"  Backed up -> {bak.name}", flush=True)
    tmp_path = str(path) + ".tmp"
    df.to_csv(tmp_path, index=False)
    os.replace(tmp_path, str(path))
    print(f"  WROTE {path.name}: {len(df):,} rows", flush=True)


def md5_of(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------
def classify_wfh_day(home2d: np.ndarray) -> np.ndarray:
    return home2d[:, BIZ].mean(1) >= 0.5


def daymean(a: np.ndarray) -> float:
    return float(a.mean())


def met_proxy(df: pd.DataFrame) -> dict:
    wd_mask = df["DDAY_STRATA"] == 1
    result = {}
    for band in BANDS:
        sub = df[wd_mask & (df["BAND"] == band)]
        if len(sub) == 0:
            result[band] = float("nan")
            continue
        arr = sub[ACT].values.astype(float)
        met_arr = np.vectorize(lambda v: MET.get(int(v) if not np.isnan(v) else 0, 0))(arr)
        result[band] = float(met_arr.mean())
    return result


# ---------------------------------------------------------------------------
# Stage B -- weekday work-tail trim (Calibration-B port, per band)
# ---------------------------------------------------------------------------
def cap_band_stageB(W, H, A, R, target, rng):
    """Bidirectional per-slot weekday work calibration toward `target`.

    DOWN (rate > target): trim work-block tails to home -- UNCHANGED from
    the original cap_band()/calibrate_weekday_work_2split.py port. Candidate
    order prefers block TAILS (next slot already OUT), then LEADS (previous
    slot already OUT), then anyone -- shrinks blocks from their edges rather
    than gutting the middle.

    UP (rate < target) -- [2026-07-30 FIX, A.5]: lift a deficit instead of
    leaving it uncorrected (the original unidirectional `continue`-on-deficit
    guard is what amplified the decoder's under-production of AT_WORK into
    the shipped deliverable). Mirror image of the DOWN branch:
      - candidates recruited EXCLUSIVELY from the OUT state
        (hom==0 & wrk==0 & ret==0) -- mutex-safe by construction, matches
        run_stage_C1's UP branch (:474-485) and the mutex invariant in A.5/
        A.6 (never poach a home or retail slot to satisfy work).
      - order prefers extending an existing work block's TAIL (previous slot
        t-1 already WORK -- this OUT slot is a chronological continuation),
        then its HEAD (next slot t+1 already WORK), then an isolated flip
        LAST -- avoids fabricating an orphan work half-hour in the middle of
        an at-home day (block-coherence, mirrors the DOWN branch's own
        trail/lead/anyone preference order).
      - ACT is set to WORK_ACT_0IDX on lifted slots -- the exact inverse of
        the DOWN branch's SLEEP/PASSIVE reset, so AT_WORK_fraction and the
        activity channel do not diverge within this stage.

    Also reads R (ret30) on the DOWN branch so a trim candidate is never
    poached from a slot where the person is simultaneously flagged
    AT_RETAIL (mutex-safe by construction; ret30==1 & wrk30==1 should
    already be impossible post-decode, this is belt-and-braces).

    Returns (n_down, n_up).
    """
    N = W.shape[0]
    n_down = 0
    n_up = 0
    for t in range(47, -1, -1):
        if t in BIZ_SET:
            continue
        rate = W[:, t].mean()
        if rate > target[t]:
            # ---------------------------------------------------- DOWN ----
            n_remove = int(round((rate - target[t]) * N))
            if n_remove <= 0:
                continue
            at_work = np.where(W[:, t] == 1)[0]
            if len(at_work) == 0:
                continue
            trail = at_work if t == 47 else at_work[W[at_work, t + 1] == 0]
            lead = np.array([], int) if t == 0 else at_work[W[at_work, t - 1] == 0]
            order, seen = [], set()
            for grp in (trail, lead, at_work):
                for i in rng.permutation(len(grp)):
                    p = int(grp[i])
                    if p not in seen:
                        seen.add(p)
                        order.append(p)
            for p in order[:n_remove]:
                W[p, t] = 0
                if R[p, t] == 0:      # never raise home on a (should-be-impossible) retail slot
                    H[p, t] = 1
                if A[p, t] == WORK_ACT_0IDX:
                    A[p, t] = SLEEP_ACT_0IDX if t in NIGHT else PASSIVE_ACT_0IDX
                n_down += 1
        elif rate < target[t]:
            # ------------------------------------------------------ UP ----
            n_add = int(round((target[t] - rate) * N))
            if n_add <= 0:
                continue
            cand = np.where((H[:, t] == 0) & (W[:, t] == 0) & (R[:, t] == 0))[0]
            if len(cand) == 0:
                continue
            extend_tail = np.array([], int) if t == 0 else cand[W[cand, t - 1] == 1]
            extend_head = np.array([], int) if t == 47 else cand[W[cand, t + 1] == 1]
            order, seen = [], set()
            for grp in (extend_tail, extend_head, cand):
                for i in rng.permutation(len(grp)):
                    p = int(grp[i])
                    if p not in seen:
                        seen.add(p)
                        order.append(p)
            for p in order[:n_add]:
                W[p, t] = 1
                A[p, t] = WORK_ACT_0IDX
                n_up += 1
    return n_down, n_up


def run_stage_B(out: pd.DataFrame, obs22: pd.DataFrame, rng) -> None:
    print("\n" + "=" * 70, flush=True)
    print("[STAGE B] Weekday work-tail trim (per band, seed=42)", flush=True)
    print("=" * 70, flush=True)

    owe = obs22[(obs22["DDAY_STRATA"] == 1) & (obs22["LFTAG"] == 1)]
    target = owe[WRK].values.astype(float).mean(0)
    print(f"  observed 2022 weekday-employed n={len(owe):,}  "
          f"WORK day-mean target={target.mean():.4f}")

    for band in BANDS:
        mask = ((out["BAND"] == band) & (out["DDAY_STRATA"] == 1)
                & (out["LFTAG"] == 1)).values
        idx = np.where(mask)[0]
        if len(idx) == 0:
            print(f"  [{band}] no weekday-employed rows"); continue
        W = out.loc[mask, WRK].values.astype(float).copy()
        H = out.loc[mask, HOM].values.astype(float).copy()
        R = out.loc[mask, RET].values.astype(float).copy()
        A = (out.loc[mask, ACT].values.astype(int) - 1).copy()

        wfh0 = classify_wfh_day(H).mean()
        w0, h0 = daymean(W), daymean(H)
        nf_down, nf_up = cap_band_stageB(W, H, A, R, target, rng)
        wfh1 = classify_wfh_day(H).mean()
        w1, h1 = daymean(W), daymean(H)

        out.loc[mask, WRK] = W
        out.loc[mask, HOM] = H
        out.loc[mask, ACT] = A + 1

        print(f"  [{band}] weekday-employed n={len(idx):,}  "
              f"DOWN(trim)={nf_down:,}  UP(lift)={nf_up:,}  "
              f"WORK {w0:.4f}->{w1:.4f}  HOME {h0:.4f}->{h1:.4f}  "
              f"WFH-day share {wfh0:.4f}->{wfh1:.4f} (should be ~unchanged)")

    resolve_and_assert_mutex(out, "post-StageB")


# ---------------------------------------------------------------------------
# Stage C0 -- weekend work cap (Calibration-C Stage 0 port)
# ---------------------------------------------------------------------------
def run_stage_C0(out: pd.DataFrame, obs22: pd.DataFrame, rng) -> None:
    """Weekend work calibration toward the observed-2022 weekend target.

    DOWN (p_30 > p_obs): trim work 1->0 -- UNCHANGED from the original
    trim-only port (plain random choice among working slots, no
    block-coherence in the pre-fix code either).

    UP (p_30 < p_obs) -- [2026-07-30 FIX, A.5]: lift a deficit instead of
    leaving it uncorrected (this was the second unidirectional
    `continue`-on-deficit guard: the weekend anchor's own Stage C0 target
    could never be reached from below). Candidates are recruited
    EXCLUSIVELY from the OUT state (hom==0 & wrk==0 & ret==0) -- mutex-safe
    by construction, identical recruiting rule to Stage B's UP branch and
    run_stage_C1's UP branch -- and ordered to extend an existing work
    block's tail (previous slot already WORK), then head (next slot already
    WORK), then an isolated flip last (block-coherence, same preference
    order as Stage B's DOWN trim, applied here even though this stage's own
    pre-existing DOWN branch does not use it, specifically to avoid
    fabricating an orphan work half-hour on an otherwise at-home weekend
    day). ACT is left untouched on both branches here, matching this
    stage's own DOWN branch and Stage C1's HOME branches -- Stage C2's
    4-state donor resample re-derives ACT from the final hom/wrk/ret state
    regardless.

    [2026-07-30 MANAGER DECISION, A.7] Sat and Sun no longer get separate
    targets -- ONE pooled Sat+Sun weekend target is used for BOTH strata.
    Trigger: with --pure-anchor ON, the purified per-stratum target's own
    SE was the same order as (Sat) or larger than (Sun) the contamination
    bias it was removing (Sat SE 1.40pp vs bias 1.37pp; Sun SE 1.57pp vs
    bias 0.33pp) -- a per-day purified target trades a known bias for
    noise of the same size or larger, which is not a fix. Pooling is also
    justified by the data, not just convenience: real Sat (0.0716) and
    real Sun (0.0778) differ by only 0.62pp, well within either single-day
    SE -- statistically indistinguishable. Pooled n~208 brings the SE to
    ~1.0pp while keeping most of the purification's bias removal.
    """
    print("\n" + "=" * 70, flush=True)
    print("[STAGE C0] Weekend work cap (bidirectional, seed=42)", flush=True)
    print("=" * 70, flush=True)

    # [MANAGER DECISION] pooled Sat+Sun target, computed ONCE, used for BOTH strata
    obs_we_pooled = obs22[obs22["DDAY_STRATA"].isin(WEEKEND_STRATA)]
    n_we_pooled = len(obs_we_pooled)
    target_wrk_pooled = (obs_we_pooled[WRK].mean().values.astype(float)
                          if n_we_pooled > 0 else None)
    if n_we_pooled > 0:
        we_daymean = obs_we_pooled[WRK].values.astype(float).mean(axis=1)
        se_pooled = (float(we_daymean.std(ddof=1) / np.sqrt(n_we_pooled))
                     if n_we_pooled > 1 else float("nan"))
        n_sat = int((obs22["DDAY_STRATA"] == 2).sum())
        n_sun = int((obs22["DDAY_STRATA"] == 3).sum())
        print(f"  [POOLED WEEKEND TARGET] Sat+Sun n={n_we_pooled:,} (Sat={n_sat:,}, Sun={n_sun:,})  "
              f"day-mean={target_wrk_pooled.mean():.4f}  SE={se_pooled * 100:.2f}pp")
    else:
        print("  [POOLED WEEKEND TARGET] no observed weekend rows available")

    total_down = total_up = 0
    for stratum in WEEKEND_STRATA:
        d30_mask = (out["DDAY_STRATA"] == stratum).values
        n = int(d30_mask.sum())
        if target_wrk_pooled is None or n == 0:
            continue
        target_wrk = target_wrk_pooled   # SAME pooled target for both Sat and Sun
        wrk_s = out.loc[d30_mask, WRK].values.astype(float).copy()
        hom_s = out.loc[d30_mask, HOM].values.astype(float)   # [FIX] read-only, for OUT-state candidates
        ret_s = out.loc[d30_mask, RET].values.astype(float)   # [FIX] read-only, for OUT-state candidates
        n_down = n_up = 0
        for s in range(N_SLOTS):
            p_obs = float(target_wrk[s])
            p_30 = float(wrk_s[:, s].mean())          # always fresh, never cached (target-anchored)
            if p_30 > p_obs + 1e-9:
                # ------------------------------------------------ DOWN ----
                n_flip = int(round((p_30 - p_obs) * n))
                if n_flip <= 0:
                    continue
                working_idx = np.where(wrk_s[:, s] == 1)[0]
                if len(working_idx) == 0:
                    continue
                n_flip = min(n_flip, len(working_idx))
                chosen = rng.choice(working_idx, size=n_flip, replace=False)
                wrk_s[chosen, s] = 0.0
                n_down += n_flip
            elif p_30 < p_obs - 1e-9:
                # -------------------------------------------------- UP ----
                n_flip = int(round((p_obs - p_30) * n))
                if n_flip <= 0:
                    continue
                cand = np.where((hom_s[:, s] == 0) & (wrk_s[:, s] == 0) & (ret_s[:, s] == 0))[0]
                if len(cand) == 0:
                    continue
                extend_tail = np.array([], int) if s == 0 else cand[wrk_s[cand, s - 1] == 1]
                extend_head = np.array([], int) if s == N_SLOTS - 1 else cand[wrk_s[cand, s + 1] == 1]
                order, seen = [], set()
                for grp in (extend_tail, extend_head, cand):
                    for i in rng.permutation(len(grp)):
                        p = int(grp[i])
                        if p not in seen:
                            seen.add(p)
                            order.append(p)
                n_flip = min(n_flip, len(order))
                chosen = order[:n_flip]
                wrk_s[chosen, s] = 1.0
                n_up += n_flip
        out.loc[d30_mask, WRK] = wrk_s
        lbl = "Sat" if stratum == 2 else "Sun"
        rate_after = float(wrk_s.mean())
        # reporting-only: this stratum's OWN (unpooled) observed day-mean, to show
        # the resulting gap against its own single-day truth, not just the pooled target
        obs_own = obs22[obs22["DDAY_STRATA"] == stratum]
        own_mean = float(obs_own[WRK].values.mean()) if len(obs_own) > 0 else float("nan")
        gap_vs_own_pp = (rate_after - own_mean) * 100.0
        print(f"  Stratum {stratum} ({lbl}): n={n:,}  DOWN(1->0)={n_down:,}  UP(0->1)={n_up:,}  "
              f"rate after={rate_after:.4f}  pooled target={float(target_wrk.mean()):.4f}  "
              f"own-day target={own_mean:.4f}  gap vs own-day={gap_vs_own_pp:+.2f}pp")
        total_down += n_down
        total_up += n_up
    print(f"  [STAGE C0 summary] total DOWN={total_down:,}  total UP={total_up:,}")

    resolve_and_assert_mutex(out, "post-StageC0")


# ---------------------------------------------------------------------------
# Stage C1 -- weekend home restore + local mindwell (Calibration-C Stage 1)
# ---------------------------------------------------------------------------
def run_stage_C1(out: pd.DataFrame, obs22: pd.DataFrame, rng) -> None:
    """Weekend home restore toward the observed-2022 weekend HOME target.

    [2026-07-30 MANAGER DECISION #2] Sat and Sun no longer get separate HOME
    targets -- ONE pooled Sat+Sun weekend target used for BOTH strata,
    mirroring Stage C0's WRK pooling (same function). Trigger: the purified
    (IS_SYNTHETIC==0) per-day HOME targets diverge sharply -- Saturday
    81.19% (n=103) vs Sunday 76.71% (n=105), +4.48pp -- but the difference
    is NOT statistically significant (SE_diff 2.72pp, z=+1.65), and the
    per-day purified targets INVERT the Sat/Sun ordering relative to both
    the contaminated pool (Sat 72.65% < Sun 77.13%) and the ordinary
    Sunday-more-at-home expectation. A per-day purified HOME target would
    bake a non-significant Sat/Sun inversion into the deliverable, which
    propagates into the per-Day_Type residential BEM schedules and on into
    energy. Pooling preserves the correctly-purified weekend MEAN (78.93%
    pooled on n=208, SE 1.37pp, vs (81.19+76.71)/2=78.95% simple average of
    the two per-day means -- consistent, so pooling only REDISTRIBUTES
    between Saturday and Sunday, it does not change the weekend average)
    while dropping the spurious day-to-day inversion. This corrects an
    inconsistency: Stage C0 (work) was already pooled on exactly this
    "indistinguishable days" reasoning; Stage C1 (home) was left per-day,
    and home turned out to be where the large per-day divergence actually
    is.
    """
    print("\n" + "=" * 70, flush=True)
    print("[STAGE C1] Weekend home restore (seed=42) + local min-dwell", flush=True)
    print("=" * 70, flush=True)

    # [MANAGER DECISION #2] pooled Sat+Sun HOME target, computed ONCE, used for BOTH strata
    obs_we_pooled = obs22[obs22["DDAY_STRATA"].isin(WEEKEND_STRATA)]
    n_we_pooled = len(obs_we_pooled)
    target_hom_pooled = (obs_we_pooled[HOM].mean().values.astype(float)
                          if n_we_pooled > 0 else None)
    if n_we_pooled > 0:
        we_daymean = obs_we_pooled[HOM].values.astype(float).mean(axis=1)
        se_pooled = (float(we_daymean.std(ddof=1) / np.sqrt(n_we_pooled))
                     if n_we_pooled > 1 else float("nan"))
        n_sat = int((obs22["DDAY_STRATA"] == 2).sum())
        n_sun = int((obs22["DDAY_STRATA"] == 3).sum())
        print(f"  [POOLED WEEKEND HOME TARGET] Sat+Sun n={n_we_pooled:,} (Sat={n_sat:,}, Sun={n_sun:,})  "
              f"day-mean={target_hom_pooled.mean():.4f}  SE={se_pooled * 100:.2f}pp")
    else:
        print("  [POOLED WEEKEND HOME TARGET] no observed weekend rows available")

    for stratum in WEEKEND_STRATA:
        d30_mask = (out["DDAY_STRATA"] == stratum).values
        n = int(d30_mask.sum())
        if target_hom_pooled is None or n == 0:
            continue
        target = target_hom_pooled   # SAME pooled target for both Sat and Sun
        hom_s = out.loc[d30_mask, HOM].values.astype(float)
        wrk_s = out.loc[d30_mask, WRK].values.astype(float)
        ret_s = out.loc[d30_mask, RET].values.astype(float)   # [Leg-3 NEW] extend candidate mask
        n_up = n_dn = 0
        for s in range(N_SLOTS):
            p_obs = float(target[s])
            p_30 = float(hom_s[:, s].mean())        # fresh each slot (target-anchored)
            diff = p_obs - p_30
            if abs(diff) < 1e-9:
                continue
            if diff > 0:
                n_flip = int(round(diff * n))
                if n_flip <= 0:
                    continue
                # [Leg-3] candidates require ret30==0 too (never poach a retail slot)
                cands = np.where((hom_s[:, s] == 0) & (wrk_s[:, s] == 0) & (ret_s[:, s] == 0))[0]
                if len(cands) == 0:
                    continue
                n_flip = min(n_flip, len(cands))
                chosen = rng.choice(cands, size=n_flip, replace=False)
                hom_s[chosen, s] = 1.0
                n_up += n_flip
            else:
                n_flip = int(round((-diff) * n))
                if n_flip <= 0:
                    continue
                cands = np.where((hom_s[:, s] == 1) & (wrk_s[:, s] == 0))[0]
                if len(cands) == 0:
                    continue
                n_flip = min(n_flip, len(cands))
                chosen = rng.choice(cands, size=n_flip, replace=False)
                hom_s[chosen, s] = 0.0
                n_dn += n_flip
        out.loc[d30_mask, HOM] = hom_s
        lbl = "Sat" if stratum == 2 else "Sun"
        # reporting-only: this stratum's OWN (unpooled) observed day-mean, to show
        # the resulting gap/redistribution against its own single-day truth
        rate_after = float(hom_s.mean())
        obs_own = obs22[obs22["DDAY_STRATA"] == stratum]
        own_mean = float(obs_own[HOM].values.mean()) if len(obs_own) > 0 else float("nan")
        gap_vs_own_pp = (rate_after - own_mean) * 100.0
        print(f"  Stratum {stratum} ({lbl}): n={n:,}  UP(OUT->HOME)={n_up:,}  "
              f"DOWN(HOME->OUT)={n_dn:,}  rate after={rate_after:.4f}  "
              f"pooled target={float(target.mean()):.4f}  own-day target={own_mean:.4f}  "
              f"gap vs own-day={gap_vs_own_pp:+.2f}pp")

    # Local min-dwell smoother restricted to weekend hom30 rows (ported apply_min_dwell)
    we_mask = out["DDAY_STRATA"].isin(WEEKEND_STRATA).values
    hom_we = out.loc[we_mask, HOM].values.astype(float)
    hom_we_smooth, n_md = apply_min_dwell(hom_we, min_dwell=2)
    out.loc[we_mask, HOM] = hom_we_smooth
    print(f"  Local min-dwell (weekend hom30 only): {n_md:,} slots changed")

    resolve_and_assert_mutex(out, "post-StageC1")


# ---------------------------------------------------------------------------
# Stage RETAIL -- retail cap, target-anchored ([Leg-3 NEW])
# ---------------------------------------------------------------------------
def run_stage_retail(out: pd.DataFrame, obs22: pd.DataFrame, rng, lever_value: float, lever_name: str) -> None:
    print("\n" + "=" * 70, flush=True)
    print(f"[STAGE RETAIL] Retail cap, target-anchored (lever={lever_name}={lever_value}, seed=42)", flush=True)
    print("=" * 70, flush=True)

    total_up = total_dn = 0
    for stratum in (1, 2, 3):
        obs_str = obs22[obs22["DDAY_STRATA"] == stratum]
        d30_mask = (out["DDAY_STRATA"] == stratum).values
        n = int(d30_mask.sum())
        if len(obs_str) == 0 or n == 0:
            continue
        target = obs_str[RET].mean().values.astype(float) * lever_value    # target-anchored, set directly
        hom_s = out.loc[d30_mask, HOM].values.astype(float)
        wrk_s = out.loc[d30_mask, WRK].values.astype(float)
        ret_s = out.loc[d30_mask, RET].values.astype(float)
        n_up = n_dn = 0
        for s in range(N_SLOTS):
            p_target = float(target[s])
            p_cur = float(ret_s[:, s].mean())       # always recomputed fresh -- never a cached delta
            if abs(p_cur - p_target) < 1e-9:
                continue
            if p_cur < p_target:
                n_flip = int(round((p_target - p_cur) * n))
                if n_flip <= 0:
                    continue
                # recruit ONLY from OUT state (never poach home/work -- would create a fresh conflict)
                cands = np.where((hom_s[:, s] == 0) & (wrk_s[:, s] == 0) & (ret_s[:, s] == 0))[0]
                if len(cands) == 0:
                    continue
                n_flip = min(n_flip, len(cands))
                chosen = rng.choice(cands, size=n_flip, replace=False)
                ret_s[chosen, s] = 1.0
                n_up += n_flip
            else:
                n_flip = int(round((p_cur - p_target) * n))
                if n_flip <= 0:
                    continue
                cands = np.where(ret_s[:, s] == 1)[0]
                if len(cands) == 0:
                    continue
                n_flip = min(n_flip, len(cands))
                chosen = rng.choice(cands, size=n_flip, replace=False)
                ret_s[chosen, s] = 0.0            # leaves OUT state; Stage C2 re-derives act30
                n_dn += n_flip
        out.loc[d30_mask, RET] = ret_s
        lbl = {1: "WD", 2: "Sat", 3: "Sun"}[stratum]
        print(f"  Stratum {stratum} ({lbl}): n={n:,}  UP(OUT->RETAIL)={n_up:,}  "
              f"DOWN(RETAIL->OUT)={n_dn:,}  rate after={float(ret_s.mean()):.4f}  "
              f"target(obs22 x lever)={float(target.mean()):.4f}")
        total_up += n_up
        total_dn += n_dn
    print(f"  [STAGE RETAIL summary] total UP={total_up:,}  total DOWN={total_dn:,}")

    resolve_and_assert_mutex(out, "post-StageRetail")


# ---------------------------------------------------------------------------
# Stage C2 -- activity restore, 4-state donor resample (Calibration-C Stage 2)
# ---------------------------------------------------------------------------
def run_stage_C2(out: pd.DataFrame, obs22: pd.DataFrame, rng) -> None:
    print("\n" + "=" * 70, flush=True)
    print("[STAGE C2] Activity restore (4-state: OUT/HOME/WORK/RETAIL, vectorized)", flush=True)
    print("=" * 70, flush=True)

    obs_hom = obs22[HOM].values.astype(float)
    obs_wrk = obs22[WRK].values.astype(float)
    obs_ret = obs22[RET].values.astype(float)
    obs_act = obs22[ACT].values.astype(float)

    def state_of(hom_s, wrk_s, ret_s):
        return np.where(wrk_s == 1, STATE_WORK,
               np.where(ret_s == 1, STATE_RETAIL,
               np.where(hom_s == 1, STATE_HOME, STATE_OUT)))

    print("  Building 2022 fallback pools (all-slot per state) ...", flush=True)
    fallback: dict[int, list] = {STATE_OUT: [], STATE_HOME: [], STATE_WORK: [], STATE_RETAIL: []}
    for s in range(N_SLOTS):
        st_s = state_of(obs_hom[:, s], obs_wrk[:, s], obs_ret[:, s])
        ak_s = obs_act[:, s]
        for st in (STATE_OUT, STATE_HOME, STATE_WORK, STATE_RETAIL):
            vals = ak_s[st_s == st]
            vals = vals[~np.isnan(vals) & (vals >= 0)]
            if len(vals) > 0:
                fallback[st].append(vals)
    for st in (STATE_OUT, STATE_HOME, STATE_WORK, STATE_RETAIL):
        fallback[st] = np.concatenate(fallback[st]).astype(float) if fallback[st] else np.array([5.0])
        print(f"    Fallback pool [{STATE_NAMES[st]}]: {len(fallback[st]):,} samples")

    out_hom = out[HOM].values.astype(float)
    out_wrk = out[WRK].values.astype(float)
    out_ret = out[RET].values.astype(float)
    out_act = out[ACT].values.astype(float)

    total_cells = total_fallback = total_assigned = 0
    for s in range(N_SLOTS):
        obs_st_s = state_of(obs_hom[:, s], obs_wrk[:, s], obs_ret[:, s])
        obs_ak_s = obs_act[:, s]
        out_st_s = state_of(out_hom[:, s], out_wrk[:, s], out_ret[:, s])
        for st in (STATE_OUT, STATE_HOME, STATE_WORK, STATE_RETAIL):
            pool = obs_ak_s[obs_st_s == st]
            pool = pool[~np.isnan(pool) & (pool >= 0)]
            if len(pool) < SMALL_CELL:
                pool = fallback[st]
                total_fallback += 1
            idx_2030 = np.where(out_st_s == st)[0]
            if len(idx_2030) == 0:
                continue
            draws = rng.choice(pool, size=len(idx_2030), replace=True)
            out_act[idx_2030, s] = draws.astype(float)
            total_cells += 1
            total_assigned += len(idx_2030)
    out[ACT] = out_act
    print(f"  Cells processed: {total_cells} (of {N_SLOTS * 4} = 48x4 possible)")
    print(f"  Cells using fallback pool: {total_fallback}")
    print(f"  Total person-slots reassigned: {total_assigned:,}")

    resolve_and_assert_mutex(out, "post-StageC2")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--retail_lever", choices=list(LEVERS.keys()), default="plateau",
                     help="Retail scenario for the retail-cap stage (default: plateau=0.97, "
                          "the Plateau/Resilient Central scenario -- produces the canonical "
                          "deliverable). shift=0.90 / renaissance=1.05 are re-runs for "
                          "sensitivity, not retrain (runbook line 59).")
    ap.add_argument("--pure-anchor", dest="pure_anchor", action="store_true", default=True,
                     help="[2026-07-30 FIX, A.7] Filter the obs22 anchor (Input B) to "
                          "IS_SYNTHETIC==0 before computing Stage B/C0 targets (default: ON). "
                          "The uncontrolled anchor is contaminated 44.5%% overall / 27.6%% "
                          "weekday / 87.1%% Saturday / 86.7%% Sunday.")
    ap.add_argument("--no-pure-anchor", dest="pure_anchor", action="store_false",
                     help="Disable anchor purification -- reproduces the contaminated-anchor "
                          "baseline (measurement/comparison use only).")
    ap.add_argument("--out_tag", default="",
                     help="Optional filename tag inserted before the extension, e.g. 'v2' "
                          "writes 2030_synthetic_diaries_4split_calibrated_mindwell_C_v2.csv "
                          "instead of the canonical *_C.csv. Use for any non-canonical/test "
                          "run -- the canonical deliverable (MD5 7c105ef3...) must never be "
                          "overwritten. Leave empty (default) to preserve canonical behavior.")
    args = ap.parse_args()
    lever_value = LEVERS[args.retail_lever]
    if args.out_tag:
        out_c_path = OUT_DIR / f"{OUT_C.stem}_{args.out_tag}{OUT_C.suffix}"
    else:
        out_c_path = OUT_C

    rng = np.random.default_rng(42)

    print("=" * 70)
    print("3rdJ_06_calibrate_C_4split.py -- Calibration B+C + retail cap + 3-way mutex")
    print(f"  Retail lever: {args.retail_lever} = {lever_value}")
    print(f"  Pure anchor (IS_SYNTHETIC==0 filter): {args.pure_anchor}")
    print(f"  Output: {out_c_path}")
    print("=" * 70)

    # ── Load raw 2030 (3 bands concatenated), Input A ──────────────────────────
    print("\n[LOAD] Input A (2030 raw, 3 bands) ...")
    frames = []
    for band in BANDS:
        p = OUT_DIR / f"2030_diaries_{band}_raw.csv"
        if not p.exists():
            raise FileNotFoundError(f"Input A missing: {p}")
        frames.append(pd.read_csv(p, low_memory=False))
    out = pd.concat(frames, ignore_index=True)
    print(f"  Combined rows: {len(out):,}  BAND={sorted(out['BAND'].unique())}  "
          f"DDAY_STRATA counts={out['DDAY_STRATA'].value_counts().to_dict()}")
    assert len(out) >= 100_000, f"Input A unexpectedly small ({len(out)} rows)"

    # ── Load observed-2022 (Input B) ────────────────────────────────────────────
    print("\n[LOAD] Input B (2022 observed) ...")
    if not IN_B.exists():
        raise FileNotFoundError(f"Input B not found: {IN_B}")
    needed_b = set(HOM + WRK + RET + ACT + ["DDAY_STRATA", "LFTAG", "CYCLE_YEAR", "IS_SYNTHETIC"])
    obs_full = pd.read_csv(IN_B, low_memory=False, usecols=lambda c: c in needed_b)
    obs22_all = obs_full[obs_full["CYCLE_YEAR"] == 2022].reset_index(drop=True)
    print(f"  Input B rows (all cycles): {len(obs_full):,}  |  2022 subset: {len(obs22_all):,}  |  "
          f"DDAY_STRATA counts={obs22_all['DDAY_STRATA'].value_counts().to_dict()}")

    # ── [2026-07-30 FIX, A.7] Anchor contamination measurement + purification ──
    print("\n[ANCHOR] IS_SYNTHETIC contamination in obs22 (measure, then act per --pure-anchor):")
    strata_lbl = {None: "Global", 1: "Weekday", 2: "Saturday", 3: "Sunday"}
    for strat, lbl in strata_lbl.items():
        sub = obs22_all if strat is None else obs22_all[obs22_all["DDAY_STRATA"] == strat]
        n = len(sub)
        n_syn = int((sub["IS_SYNTHETIC"] == 1).sum()) if n else 0
        pct = 100.0 * n_syn / n if n else float("nan")
        print(f"    {lbl:9s}: synthetic {n_syn:,}/{n:,} = {pct:.1f}%")

    # SE of the purified weekend target vs the size of the contamination bias
    # being removed -- MEASURE AND REPORT, do not silently decide (A.7 caveat).
    for strat, lbl in ((2, "Saturday"), (3, "Sunday")):
        all_sub = obs22_all[obs22_all["DDAY_STRATA"] == strat]
        real_sub = all_sub[all_sub["IS_SYNTHETIC"] == 0]
        if len(real_sub) == 0 or len(all_sub) == 0:
            continue
        real_daymean = real_sub[WRK].values.astype(float).mean(axis=1)
        all_daymean = all_sub[WRK].values.astype(float).mean(axis=1)
        real_mean = float(real_daymean.mean())
        real_se = float(real_daymean.std(ddof=1) / np.sqrt(len(real_daymean)))
        all_mean = float(all_daymean.mean())
        bias_pp = (all_mean - real_mean) * 100.0
        verdict = ("SAME ORDER AS BIAS -- flag for manager (pool Sat+Sun or smooth?)"
                   if real_se * 100.0 >= 0.5 * abs(bias_pp) else
                   "smaller than the bias being removed")
        print(f"    [SE CHECK] {lbl}: n_real={len(real_sub):,} (of {len(all_sub):,})  "
              f"real work-mean={real_mean:.4f} +/- SE={real_se * 100.0:.2f}pp  "
              f"contaminated-pool mean={all_mean:.4f}  bias(contam-real)={bias_pp:+.2f}pp  "
              f"-> SE is {verdict}")

    if args.pure_anchor:
        obs22 = obs22_all[obs22_all["IS_SYNTHETIC"] == 0].reset_index(drop=True)
        print(f"  [PURE-ANCHOR ON] obs22 filtered to IS_SYNTHETIC==0: "
              f"{len(obs22_all):,} -> {len(obs22):,} rows")
    else:
        obs22 = obs22_all
        print(f"  [PURE-ANCHOR OFF] obs22 left contaminated (--no-pure-anchor): {len(obs22):,} rows")

    # ── Snapshots for integrity checks ──────────────────────────────────────────
    wd_mask_orig = out["DDAY_STRATA"].isin(WEEKDAY_STRATA).values
    hom_wd_orig = out.loc[wd_mask_orig, HOM].values.copy()

    # ── Baseline diagnostics ────────────────────────────────────────────────────
    print("\n[BASELINE] Pre-calibration diagnostics:")
    act_before = out[ACT].values.astype(float)
    sleep_before = float((act_before == 5).mean())     # act code 5 = Sleep & Rest (1-indexed, ACT_LABELS)
    print(f"  Sleep (code 5) share BEFORE: {sleep_before:.4f}")
    met_before = met_proxy(out)
    print(f"  WD mean Metabolic proxy BEFORE (W): "
          + "  ".join(f"{b}={met_before[b]:.1f}" for b in BANDS))
    retail_before = float(out[RET].values.mean())
    print(f"  Overall retail (ret30) rate BEFORE: {retail_before:.4f}")

    # ── Stage chain ──────────────────────────────────────────────────────────────
    run_stage_B(out, obs22, rng)

    print("\n" + "=" * 70)
    print("[GLOBAL MINDWELL] 3rdJ_04M_mindwell_4split.py on the full post-StageB frame")
    print("=" * 70)
    out = call_mindwell_global(out)
    resolve_and_assert_mutex(out, "post-GlobalMindwell")

    # wrk30 integrity: unchanged by the global mindwell + StageB's own tail-trim
    # already finished writing wrk30 for good -- from here on wrk30 must never
    # move again except inside Stage C0's explicit weekend trim.
    wrk_after_B_mindwell = out[WRK].values.copy()

    run_stage_C0(out, obs22, rng)

    # wrk30 snapshot AFTER Stage C0 (weekday untouched throughout; weekend
    # intentionally capped once in C0) -- from here on wrk30 must be frozen.
    wrk_locked = out[WRK].values.copy()

    run_stage_C1(out, obs22, rng)
    assert (out[WRK].values == wrk_locked).all(), "INTEGRITY FAIL: wrk30 modified in Stage C1!"
    print("  [OK] wrk30 untouched since Stage C0 (Stage C1 integrity verified)")
    # Note: weekday hom30 (hom_wd_orig) is intentionally NOT re-asserted unchanged here --
    # Stage B legitimately moves weekday hom30 (work-tail trims flip WORK->HOME); only
    # Stage C0 onward must leave weekday hom30/wrk30 alone, which the wrk30 check above covers.

    run_stage_retail(out, obs22, rng, lever_value, args.retail_lever)
    assert (out[WRK].values == wrk_locked).all(), "INTEGRITY FAIL: wrk30 modified in Stage RETAIL!"
    print("  [OK] wrk30 untouched by Stage RETAIL")

    run_stage_C2(out, obs22, rng)
    assert (out[WRK].values == wrk_locked).all(), "INTEGRITY FAIL: wrk30 modified in Stage C2!"
    print("  [OK] wrk30 untouched by Stage C2 (activity-only stage)")

    # ── Verification diagnostics (post-calibration) ─────────────────────────────
    print("\n[VERIFY] Post-calibration diagnostics:")
    act_after = out[ACT].values.astype(float)
    sleep_after = float((act_after == 5).mean())
    print(f"  [1] Sleep (code 5) share: {sleep_before:.4f} -> {sleep_after:.4f}")

    met_after = met_proxy(out)
    for band in BANDS:
        print(f"  [2] WD mean Metabolic proxy [{band}]: {met_before[band]:.1f} -> {met_after[band]:.1f} W")

    we_mask_out = out["DDAY_STRATA"].isin(WEEKEND_STRATA)
    we_day_after = float(out.loc[we_mask_out, DAYTIME_HOM].values.mean())
    print(f"  [3] WE daytime (slots 11-26) hom30 AFTER: {we_day_after:.4f}")

    wd_mask_out = out["DDAY_STRATA"] == 1
    print("  [4] WD daytime hom30 by band (should be conservative < hybrid < fullyhybrid):")
    wd_day_after = {}
    for band in BANDS:
        v = float(out.loc[wd_mask_out & (out["BAND"] == band), DAYTIME_HOM].values.mean())
        wd_day_after[band] = v
        print(f"      {band}: {v:.4f}")
    wfh_ok = wd_day_after["conservative"] < wd_day_after["hybrid"] < wd_day_after["fullyhybrid"]
    print(f"      Ordering conservative < hybrid < fullyhybrid: {'PASS' if wfh_ok else 'FAIL'}")

    retail_after = float(out[RET].values.mean())
    print(f"  [5] Overall retail (ret30) rate: {retail_before:.4f} -> {retail_after:.4f} "
          f"(target obs22 x {lever_value} = {float(obs22[RET].values.mean()) * lever_value:.4f})")

    n_conflict_final = int(((out[HOM].values == 1) & (out[WRK].values == 1)).sum()
                            + ((out[HOM].values == 1) & (out[RET].values == 1)).sum()
                            + ((out[WRK].values == 1) & (out[RET].values == 1)).sum())
    print(f"  [6] Final 3-way mutex conflicts: {n_conflict_final} (must be 0)")
    assert n_conflict_final == 0

    # ── Atomic write ─────────────────────────────────────────────────────────────
    print(f"\n[WRITE] {out_c_path.name}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    atomic_write(out, out_c_path)
    md5 = md5_of(out_c_path)
    print(f"  MD5: {md5}")

    print("\n" + "=" * 70)
    print("CALIBRATION CHAIN COMPLETE")
    print(f"  Output: {out_c_path}")
    print(f"  MD5:    {md5}")
    print("=" * 70)


if __name__ == "__main__":
    main()
