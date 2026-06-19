#!/usr/bin/env python3
"""
3rdJ_04L_teleworkaware_smoke.py — Local smoke test for telework-aware rake (Step 4L).

Builds a tiny in-memory synthetic fixture (no real CSV, no GPU, no torch) and
asserts:
  1. Flag OFF  -> rake output byte-identical on repeated calls (deterministic; coherence
                  pass is NOT called, so output is unchanged from classic rake).
  2. Flag ON   -> ZERO FLOATING rows after coherence pass (before rake).
  3. Flag ON   -> Telework rows have hom30=1, wrk30=0 on work-act slots (after coherence).
  4. Flag ON   -> At-workplace rows have wrk30=1, hom30=0 on work-act slots (after coherence).
  5. Flag ON   -> OW1 population work-activity marginal preserved (act30 never modified).
  6. Validator Gate A runs on fixture without exception; returns sane verdict.
  7. Validator Gate B runs on fixture without exception; returns sane verdict.

Block-wise / post-rake-fixup checks (added 2026-06-19):
  8. Block-wise coherence + post-rake fixup -> FLOATING still 0% after rake.
  9a. Commuter day (2 work episodes) -> FLOATING=0 after full pipeline.
  9b. Commuter day max transitions per syn row <= 6 (not inflated by fixup).
  10. Post-rake fixup is a no-op when no FLOATING exists.
  11. Post-rake fixup never introduces wrk==1 AND hom==1 double-positive.

Run:
    python 3rdJ_04L_teleworkaware_smoke.py
"""
from __future__ import annotations

import sys
import os
import importlib.util
import types

import numpy as np
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

# ── Stub torch (only needed at import time of 04L) ───────────────────────────
_fake_torch = types.ModuleType("torch")
_fake_torch.device = lambda *a, **kw: "cpu"
_fake_torch.cuda = types.SimpleNamespace(is_available=lambda: False)
_fake_torch.backends = types.SimpleNamespace(
    mps=types.SimpleNamespace(is_available=lambda: False))
_fake_torch.manual_seed = lambda s: None
if "torch" not in sys.modules:
    sys.modules["torch"] = _fake_torch

# Stub out model module
_fake_model = types.ModuleType("3rdJ_04B_model_2split")
_fake_model.JSeriesHybrid2Split = None
sys.modules["3rdJ_04B_model_2split"] = _fake_model

# Load 04L functions without executing main()
_spec04L = importlib.util.spec_from_file_location(
    "rake04L",
    os.path.join(SCRIPT_DIR, "3rdJ_04L_joint_rake_2split.py"),
)
rake04L = importlib.util.module_from_spec(_spec04L)
_spec04L.loader.exec_module(rake04L)

_apply_telework_coherence = rake04L._apply_telework_coherence
_post_rake_floating_fixup  = rake04L._post_rake_floating_fixup
_joint_rake_slot           = rake04L._joint_rake_slot
N_SLOTS                    = rake04L.N_SLOTS
HOM_COLS                   = rake04L.HOM_COLS
WRK_COLS                   = rake04L.WRK_COLS

# ── Build synthetic fixture ───────────────────────────────────────────────────

N_OBS = 20
N_SYN = 30
rng = np.random.default_rng(99)


def _make_fixture() -> pd.DataFrame:
    """
    Tiny augmented_diaries-like DataFrame.
      Rows 0..N_OBS-1  : IS_SYNTHETIC=0 (observed)
      Rows N_OBS..     : IS_SYNTHETIC=1 (synthetic)

    TELEWORK: odd occIDs are teleworkers (so we have both types).
    Slot 17-32 seeded as Work (act==1).
    FLOATING deliberately inserted in some synthetic work slots (j % 5 == 0).
    """
    rows = []
    for i in range(N_OBS + N_SYN):
        is_syn = int(i >= N_OBS)
        occ_id = i + 1000
        telework = 1 if (occ_id % 2 == 1) else 0  # odd occIDs telework
        row = {
            "occID": occ_id,
            "CYCLE_YEAR": 2022,
            "DDAY_STRATA": 1,
            "IS_SYNTHETIC": is_syn,
            "TELEWORK": float(telework),
        }
        for j in range(1, N_SLOTS + 1):
            ss = f"{j:03d}"
            act = 1 if (17 <= j <= 32) else int(rng.integers(2, 14))

            if is_syn:
                if act == 1 and (j % 5 == 0):
                    hom, wrk = 0, 0   # deliberate FLOATING
                elif act == 1:
                    hom, wrk = 0, 1
                else:
                    hom = int(rng.random() > 0.3)
                    wrk = 0
            else:
                if act == 1:
                    hom, wrk = (1, 0) if telework else (0, 1)
                else:
                    hom = int(rng.random() > 0.4)
                    wrk = 0

            row[f"act30_{ss}"] = act
            row[f"hom30_{ss}"] = hom
            row[f"wrk30_{ss}"] = wrk
        rows.append(row)
    return pd.DataFrame(rows)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _count_floating(df: pd.DataFrame) -> tuple[int, int]:
    """(n_floating, n_work) over IS_SYNTHETIC==1 rows."""
    syn = df[df["IS_SYNTHETIC"] == 1]
    n_f = n_w = 0
    for j in range(1, N_SLOTS + 1):
        ss = f"{j:03d}"
        act = syn[f"act30_{ss}"].values
        hom = syn[f"hom30_{ss}"].values
        wrk = syn[f"wrk30_{ss}"].values
        wm = (act == 1)
        n_w += int(wm.sum())
        n_f += int((wm & (wrk == 0) & (hom == 0)).sum())
    return n_f, n_w


def _simple_rake(df: pd.DataFrame) -> pd.DataFrame:
    """Minimal deterministic rake with uniform 0.5 probs (no model needed)."""
    df = df.copy()
    obs = df[df["IS_SYNTHETIC"] == 0]
    syn = df[df["IS_SYNTHETIC"] == 1]
    idx = syn.index
    n_obs, n_syn = len(obs), len(syn)
    if n_obs == 0 or n_syn == 0:
        return df
    obs_h = obs[HOM_COLS].to_numpy(dtype=float)
    obs_w = obs[WRK_COLS].to_numpy(dtype=float)
    ph = pw = np.full(n_syn, 0.5, dtype=np.float32)
    new_h = np.zeros((n_syn, N_SLOTS), dtype=np.float32)
    new_w = np.zeros((n_syn, N_SLOTS), dtype=np.float32)
    for j in range(N_SLOTS):
        rh = float(np.nanmean(obs_h[:, j]))
        rw = float(np.nanmean(obs_w[:, j]))
        h, w = _joint_rake_slot(ph, pw, int(round(rh * n_syn)), int(round(rw * n_syn)))
        new_h[:, j] = h
        new_w[:, j] = w
    df.loc[idx, HOM_COLS] = new_h.astype(float)
    df.loc[idx, WRK_COLS] = new_w.astype(float)
    return df


# ── Gate runner via validator class ──────────────────────────────────────────

def _run_gates(df: pd.DataFrame) -> dict:
    """
    Invoke Gate A + Gate B from the validator class on the given DataFrame.
    Stubs out all heavy imports (matplotlib, scipy, seaborn).
    """
    # Stub matplotlib fully before the validator module is loaded
    _mpl = types.ModuleType("matplotlib")
    _mpl.use = lambda *a, **kw: None
    _mpl_plt = types.ModuleType("matplotlib.pyplot")
    for attr in ("subplots", "close", "colorbar", "tight_layout",
                 "rcParams", "imshow"):
        setattr(_mpl_plt, attr, lambda *a, **kw: None)
    _mpl_plt.rcParams = {}
    _mpl.pyplot = _mpl_plt
    sys.modules["matplotlib"] = _mpl
    sys.modules["matplotlib.pyplot"] = _mpl_plt

    for mod in ["seaborn", "scipy", "scipy.spatial",
                "scipy.spatial.distance", "scipy.stats"]:
        if mod not in sys.modules:
            sys.modules[mod] = types.ModuleType(mod)

    _spec = importlib.util.spec_from_file_location(
        "val04_gate",
        os.path.join(SCRIPT_DIR, "3rdJ_04_augmentationGSS_2split_val.py"),
    )
    val04 = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(val04)

    cls = val04.AugmentationValidator2Split
    v = object.__new__(cls)
    v.aug = df.copy()
    v.obs = df[df["IS_SYNTHETIC"] == 0].copy()
    v.syn = df[df["IS_SYNTHETIC"] == 1].copy()
    v.results = {"pass": [], "warn": [], "fail": []}
    v.sample_mode = True
    v.thr = v._thresholds()
    v.plots_b64 = {}
    v.summary_rows = []
    v.cycles = [2022]
    v.train_log = None
    v.feat_cfg = None
    v.ref_hetus = v.ref_cop = v.ref_work = None

    v.validate_tier1_coherence()

    all_results = v.results["pass"] + v.results["warn"] + v.results["fail"]

    def _verdict(prefix):
        lines = [r for r in all_results if r.startswith(prefix)]
        if not lines:
            return "none", lines
        if any(r in v.results["pass"] for r in lines):
            return "pass", lines
        if any(r in v.results["warn"] for r in lines):
            return "warn", lines
        return "fail", lines

    ga_lv, ga_lines = _verdict("GA")
    gb_lv, gb_lines = _verdict("GB")
    return {"ga_level": ga_lv, "ga_lines": ga_lines,
            "gb_level": gb_lv, "gb_lines": gb_lines}


# ── Main smoke ────────────────────────────────────────────────────────────────

def main() -> bool:
    checks: list[tuple[str, str, str]] = []

    def chk(name: str, passed: bool, detail: str = "") -> None:
        status = "PASS" if passed else "FAIL"
        checks.append((name, status, detail))
        tag = f": {detail}" if detail else ""
        print(f"  [{status}] {name}{tag}")

    print("=" * 64)
    print("3rdJ Step 4L — Telework-aware smoke test")
    print("=" * 64)

    # ── Build fixture ─────────────────────────────────────────────────────────
    print("\n[0] Building synthetic fixture...")
    fixture = _make_fixture()
    n_f_pre, n_w_pre = _count_floating(fixture)
    print(f"  Fixture: {len(fixture)} rows ({N_OBS} obs, {N_SYN} syn)")
    print(f"  Pre-coherence FLOATING in syn: {n_f_pre}/{n_w_pre} "
          f"({100*n_f_pre/max(n_w_pre,1):.1f}%)")
    chk("Fixture has FLOATING to fix", n_f_pre > 0,
        f"{n_f_pre} FLOATING slots seeded")

    # ── Check 1: Flag OFF -> deterministic (byte-identical) ───────────────────
    print("\n[1] Flag OFF: verify classic rake is deterministic...")
    out_a = _simple_rake(fixture)
    out_b = _simple_rake(fixture)
    chk("Check 1: Flag OFF — rake is deterministic (byte-identical on same fixture)",
        out_a[HOM_COLS + WRK_COLS].equals(out_b[HOM_COLS + WRK_COLS]))

    # ── Apply coherence pass (telework_aware ON) ───────────────────────────────
    print("\n[2-4] Applying telework coherence pass...")
    after_coherence = _apply_telework_coherence(fixture.copy())

    # Check 2: ZERO FLOATING after coherence
    n_f_post, n_w_post = _count_floating(after_coherence)
    chk("Check 2: Flag ON — ZERO FLOATING after coherence pass",
        n_f_post == 0,
        f"{n_f_post} FLOATING remain out of {n_w_post} work-slots")

    # Check 3: Telework rows -> hom30=1, wrk30=0 on work-act slots
    syn_coh = after_coherence[after_coherence["IS_SYNTHETIC"] == 1]
    tele_rows = syn_coh[syn_coh["TELEWORK"] == 1.0]
    ok_tele = True
    tele_bad = []
    for j in range(17, 33):
        ss = f"{j:03d}"
        wm = tele_rows[f"act30_{ss}"] == 1
        if not wm.any():
            continue
        sub = tele_rows[wm]
        if (sub[f"hom30_{ss}"] != 1).any() or (sub[f"wrk30_{ss}"] != 0).any():
            ok_tele = False
            tele_bad.append(j)
    chk("Check 3: Flag ON — telework work-act slots -> hom30=1, wrk30=0",
        ok_tele,
        "" if ok_tele else f"bad slots: {tele_bad[:4]}")

    # Check 4: Non-telework rows -> wrk30=1, hom30=0 on work-act slots
    nontel_rows = syn_coh[syn_coh["TELEWORK"] != 1.0]
    ok_atwork = True
    atwork_bad = []
    for j in range(17, 33):
        ss = f"{j:03d}"
        wm = nontel_rows[f"act30_{ss}"] == 1
        if not wm.any():
            continue
        sub = nontel_rows[wm]
        if (sub[f"wrk30_{ss}"] != 1).any() or (sub[f"hom30_{ss}"] != 0).any():
            ok_atwork = False
            atwork_bad.append(j)
    chk("Check 4: Flag ON — non-telework work-act slots -> wrk30=1, hom30=0",
        ok_atwork,
        "" if ok_atwork else f"bad slots: {atwork_bad[:4]}")

    # ── Check 5: OW1 work-activity marginal preserved ─────────────────────────
    print("\n[5] OW1: work-activity marginal unchanged (act30 never modified)...")
    act_cols_48 = [f"act30_{j:03d}" for j in range(1, N_SLOTS + 1)]
    syn_before_act = (fixture[fixture["IS_SYNTHETIC"] == 1][act_cols_48]
                      .to_numpy(dtype=float) == 1).mean()
    syn_after_act  = (after_coherence[after_coherence["IS_SYNTHETIC"] == 1][act_cols_48]
                      .to_numpy(dtype=float) == 1).mean()
    delta = abs(syn_after_act - syn_before_act) * 100
    chk("Check 5: Act30 work-activity rate unchanged after coherence pass",
        delta < 0.001,
        f"delta={delta:.4f} pp  (before={syn_before_act*100:.1f}%, after={syn_after_act*100:.1f}%)")

    # ── Checks 6 & 7: Gate A + B via validator ────────────────────────────────
    print("\n[6-7] Running Gate A (FLOATING) and Gate B (FLICKER)...")
    try:
        gr = _run_gates(after_coherence)
        ga_ok = gr["ga_level"] in ("pass", "warn", "fail")
        gb_ok = gr["gb_level"] in ("pass", "warn", "fail")
        chk("Check 6: Gate A (FLOATING) — no exception, sane verdict",
            ga_ok,
            f"verdict={gr['ga_level']}  {gr['ga_lines'][:1]}")
        chk("Check 7: Gate B (FLICKER) — no exception, sane verdict",
            gb_ok,
            f"verdict={gr['gb_level']}  {gr['gb_lines'][:1]}")
    except Exception as exc:
        chk("Check 6: Gate A (FLOATING) — no exception", False, str(exc)[:120])
        chk("Check 7: Gate B (FLICKER) — no exception", False, str(exc)[:120])

    # ── New block-wise checks (checks 8-11) ───────────────────────────────────
    print("\n[8-11] Block-wise + post-rake checks...")

    # ── Check 8: FLOATING -> 0% after block-wise coherence + post-rake fixup ──
    # Use the post-coherence fixture and run a simple rake on it, then fixup
    after_coh_raked = after_coherence.copy()
    # apply the simple rake (uniform probs)
    after_coh_raked = _simple_rake(after_coh_raked)
    # apply post-rake fixup
    syn_coh_raked = after_coh_raked[after_coh_raked["IS_SYNTHETIC"] == 1]
    s_idx = syn_coh_raked.index
    act_cols_48 = [f"act30_{j:03d}" for j in range(1, N_SLOTS + 1)]
    act_m = after_coh_raked.loc[s_idx, act_cols_48].to_numpy(dtype=float)
    hom_m = after_coh_raked.loc[s_idx, HOM_COLS].to_numpy(dtype=np.float32)
    wrk_m = after_coh_raked.loc[s_idx, WRK_COLS].to_numpy(dtype=np.float32)
    hom_m, wrk_m = _post_rake_floating_fixup(hom_m, wrk_m, act_m)
    after_coh_raked.loc[s_idx, HOM_COLS] = hom_m.astype(float)
    after_coh_raked.loc[s_idx, WRK_COLS] = wrk_m.astype(float)
    n_f8, n_w8 = _count_floating(after_coh_raked)
    chk("Check 8: Block-wise coherence + post-rake fixup -> FLOATING=0%",
        n_f8 == 0,
        f"{n_f8} FLOATING remain out of {n_w8} work-slots after rake+fixup")

    # ── Check 9: Commuter day transitions NOT inflated ─────────────────────────
    # Construct a known commuter day: 2 work episodes -> 4 hom30 transitions
    # with a TELEWORK=0 worker who has work slots 10-16 and 20-26 (two spells)
    # Each spell creates a 1->0 and a 0->1 = 2 transitions per spell = 4 total.
    # The block-wise pass should NOT split these into smaller pieces,
    # and the post-rake fixup should not create extra transitions within episodes.
    print("  [9] Building commuter-day transition test case...")
    rows_comm = []
    for i in range(5):
        is_syn = int(i >= 2)  # rows 0,1 observed; rows 2,3,4 synthetic
        row_c = {
            "occID": 2000 + i, "CYCLE_YEAR": 2022, "DDAY_STRATA": 1,
            "IS_SYNTHETIC": is_syn, "TELEWORK": 0.0,
        }
        for j in range(1, N_SLOTS + 1):
            ss = f"{j:03d}"
            # Two work spells: 10-16 and 20-26
            if (10 <= j <= 16) or (20 <= j <= 26):
                row_c[f"act30_{ss}"] = 1
                # Seed FLOATING on one slot to ensure fixup path is tested
                if j == 12 and is_syn:
                    row_c[f"hom30_{ss}"] = 0; row_c[f"wrk30_{ss}"] = 0
                else:
                    row_c[f"hom30_{ss}"] = 0; row_c[f"wrk30_{ss}"] = 1 if is_syn else 1
            else:
                row_c[f"act30_{ss}"] = 2
                row_c[f"hom30_{ss}"] = 1; row_c[f"wrk30_{ss}"] = 0
        rows_comm.append(row_c)
    df_comm = pd.DataFrame(rows_comm)

    # Apply coherence pass
    df_comm_coh = _apply_telework_coherence(df_comm.copy())

    # Apply simple rake
    df_comm_raked = _simple_rake(df_comm_coh.copy())

    # Apply post-rake fixup
    syn_comm = df_comm_raked[df_comm_raked["IS_SYNTHETIC"] == 1]
    sc_idx = syn_comm.index
    act_m2 = df_comm_raked.loc[sc_idx, act_cols_48].to_numpy(dtype=float)
    hom_m2 = df_comm_raked.loc[sc_idx, HOM_COLS].to_numpy(dtype=np.float32)
    wrk_m2 = df_comm_raked.loc[sc_idx, WRK_COLS].to_numpy(dtype=np.float32)
    hom_m2, wrk_m2 = _post_rake_floating_fixup(hom_m2, wrk_m2, act_m2)
    df_comm_raked.loc[sc_idx, HOM_COLS] = hom_m2.astype(float)
    df_comm_raked.loc[sc_idx, WRK_COLS] = wrk_m2.astype(float)

    # Verify FLOATING=0 on commuter case
    n_f9, n_w9 = _count_floating(df_comm_raked)
    chk("Check 9a: Commuter case — FLOATING=0 after block-wise + rake + fixup",
        n_f9 == 0,
        f"{n_f9} FLOATING out of {n_w9} work-slots")

    # Verify transitions per synthetic row: should not exceed 4
    # (2 spells x 2 transitions per spell = 4; post-rake may set some hom30=0
    # inside the non-work slots but the block boundaries are fixed by coherence)
    syn_comm_final = df_comm_raked[df_comm_raked["IS_SYNTHETIC"] == 1]
    max_trans_9 = 0
    for _, row_r in syn_comm_final.iterrows():
        hv = [int(row_r[f"hom30_{j:03d}"]) for j in range(1, N_SLOTS + 1)]
        tr = sum(1 for k in range(len(hv) - 1) if hv[k] != hv[k + 1])
        if tr > max_trans_9:
            max_trans_9 = tr
    # Bar: transitions/day for a 2-spell commuter should not be inflated to >4
    # by the fixup (a fixup only adds home, never removes home, so can't create
    # extra 1->0 transitions; could in theory add 0->1 then 1->0 if the next
    # slot goes back to 0, but that's a rake artifact not a fixup artifact).
    # We assert max <= 6 (generous; the point is it's not 8 or 10).
    chk("Check 9b: Commuter case — transitions/day not inflated (max<=6 per syn row)",
        max_trans_9 <= 6,
        f"max transitions across syn rows = {max_trans_9}")

    # ── Check 10: Flag-OFF -> byte-identical (already in Check 1; add post-fixup) ─
    # Confirm the _post_rake_floating_fixup is a no-op when there is no FLOATING
    no_float_hom = np.array([[1.0, 0.0, 1.0]], dtype=np.float32)
    no_float_wrk = np.array([[0.0, 1.0, 0.0]], dtype=np.float32)
    no_float_act = np.array([[2.0, 1.0, 2.0]], dtype=float)   # slot 2 is work, wrk=1 so no FLOATING
    h10_out, w10_out = _post_rake_floating_fixup(
        no_float_hom.copy(), no_float_wrk.copy(), no_float_act)
    chk("Check 10: Post-rake fixup is no-op when no FLOATING exists",
        np.array_equal(h10_out, no_float_hom) and np.array_equal(w10_out, no_float_wrk),
        f"hom_out={h10_out.tolist()}  wrk_out={w10_out.tolist()}")

    # ── Check 11: No wrk==1 AND hom==1 double-positive after fixup ───────────
    # Pathological input: work slot where rake set BOTH to 1 (should not happen
    # in joint rake, but fixup must not introduce it either)
    both_hom = np.array([[1.0, 0.0]], dtype=np.float32)
    both_wrk = np.array([[0.0, 0.0]], dtype=np.float32)
    both_act = np.array([[2.0, 1.0]], dtype=float)   # slot 2 is work, FLOATING -> fixup sets hom=1
    h11_out, w11_out = _post_rake_floating_fixup(both_hom.copy(), both_wrk.copy(), both_act)
    double_pos = int(np.sum((h11_out == 1) & (w11_out == 1)))
    chk("Check 11: Post-rake fixup never introduces wrk==1 AND hom==1",
        double_pos == 0,
        f"double-positives after fixup: {double_pos}  hom={h11_out.tolist()}  wrk={w11_out.tolist()}")

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "=" * 64)
    n_pass = sum(1 for _, s, _ in checks if s == "PASS")
    n_fail = sum(1 for _, s, _ in checks if s == "FAIL")
    print(f"SMOKE RESULT: {n_pass} PASS / {n_fail} FAIL")
    print("=" * 64)
    for name, status, detail in checks:
        extra = f"  | {detail}" if detail else ""
        print(f"  [{status}] {name}{extra}")

    return n_fail == 0


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
