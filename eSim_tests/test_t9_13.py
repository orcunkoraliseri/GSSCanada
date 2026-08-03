"""T9-13 (DHW volume scaling) primitive tests.

Rewritten into the repo 2026-08-02. The previous copy lived in a session scratchpad and was lost
with it, which left the "22/22 primitive tests pass" claim in 3rdJ_L3_improvements_step9.md
unreproducible. This file is tracked so the claim can be re-checked at any time.

Covers the original suite plus the two defects found on 2026-08-02:
  FINDING 3 -- residential must take the T9-13 path under reference="baseline_series"
  FINDING 4 -- reference_occ_mean must be PER DAY TYPE, not one flat scalar

Run:  py -3 eSim_tests/test_t9_13.py
Exit code 0 = all pass. No pytest dependency (the repo does not ship one).
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eSim_bem_utils.commercial_integration import (      # noqa: E402
    apply_dhw_volume_scaling,
    audit_dhw_shape_preservation,
    DHW_MODEL_VOLUME_SCALED,
    _ALL_DAYTYPES,
    _WEEKDAY_DAYTYPES,
    _build_compact_fields_by_daytype,
)

_RESULTS = []


def check(name, cond, detail=""):
    _RESULTS.append((name, bool(cond), detail))
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f"   [{detail}]" if detail and not cond else ""))


# The real prototype office DHW weekday/weekend profile, read from
# TallBuilding_90.1-2019_6A_Buffalo_NECB17_Z6_v242.idf (OfficeLarge BLDG_SWH_SCH). Using the actual
# shape rather than a toy one means these tests exercise the numbers the campaign will really see.
PROTO_WD = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.07, 0.19, 0.35, 0.38, 0.39, 0.47,
            0.57, 0.54, 0.34, 0.33, 0.44, 0.26, 0.21, 0.15, 0.17, 0.08, 0.05, 0.05]
PROTO_WE = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.07, 0.07, 0.10, 0.12, 0.12, 0.15,
            0.13, 0.14, 0.10, 0.09, 0.09, 0.06, 0.06, 0.06, 0.06, 0.08, 0.04, 0.04]

FLAT = [0.5] * 24


def mean(v):
    return sum(v) / len(v)


def nightshare(v):
    t = sum(v)
    return sum(v[0:6]) / t if t > 1e-12 else float("nan")


def rec(info, name="obj", channel="office"):
    return {"name": name, "channel": channel, "model": "T9-13_volume_scaled", "t9_13": info}


# ---------------------------------------------------------------------------
print("\n-- group 1: identity and no-op --")
# ---------------------------------------------------------------------------
new_wd, new_we, info = apply_dhw_volume_scaling(PROTO_WD, PROTO_WE, FLAT, FLAT, FLAT, FLAT)
check("T1 r == 1 when occ == ref", abs(info["r_wd"] - 1) < 1e-12 and abs(info["r_we"] - 1) < 1e-12)
check("T2 no-op reproduces the prototype bit-for-bit", new_wd == PROTO_WD and new_we == PROTO_WE)
check("T3 is_noop flag set", info["is_noop"] is True)
check("T4 peak_multiplier == 1 on a no-op", abs(info["peak_multiplier"] - 1) < 1e-12)

# ---------------------------------------------------------------------------
print("\n-- group 2: shape preservation is an identity --")
# ---------------------------------------------------------------------------
occ_wd, occ_we = [0.74 * 0.5] * 24, [2.079 * 0.5] * 24      # B_central office r's
new_wd, new_we, info = apply_dhw_volume_scaling(PROTO_WD, PROTO_WE, occ_wd, occ_we, FLAT, FLAT)
check("T5 weekday night share unchanged",
      abs(nightshare(new_wd) - nightshare(PROTO_WD)) < 1e-9)
check("T6 weekday peak hour unchanged",
      new_wd.index(max(new_wd)) == PROTO_WD.index(max(PROTO_WD)))
check("T7 weekend peak hour unchanged",
      new_we.index(max(new_we)) == PROTO_WE.index(max(PROTO_WE)))
check("T8 shape is a pure scalar multiple of the prototype",
      all(abs(n * max(PROTO_WD) - p * max(new_wd)) < 1e-9 for n, p in zip(new_wd, PROTO_WD)))

# ---------------------------------------------------------------------------
print("\n-- group 3: volume and the Fraction bound --")
# ---------------------------------------------------------------------------
R = info["R"]
check("T9 achieved weekday volume ratio == r_wd",
      abs((mean(new_wd) / mean(PROTO_WD)) * R - info["r_wd"]) < 1e-6)
check("T10 achieved weekend volume ratio == r_we",
      abs((mean(new_we) / mean(PROTO_WE)) * R - info["r_we"]) < 1e-6)
check("T11 max(f_new) <= max(s_proto) -- Fraction bound never clips",
      max(new_wd + new_we) <= max(PROTO_WD + PROTO_WE) + 1e-12)
check("T12 R == max(r_wd, r_we)", abs(R - max(info["r_wd"], info["r_we"])) < 1e-9)
check("T13 physical flow is independent of R (P*R * s*r/R == P*s*r)",
      abs(max(new_wd) * R - max(PROTO_WD) * info["r_wd"]) < 1e-9)

# ---------------------------------------------------------------------------
print("\n-- group 4: guards --")
# ---------------------------------------------------------------------------
bad_wd, bad_we, bad_info = apply_dhw_volume_scaling(PROTO_WD, PROTO_WE, FLAT, FLAT,
                                                    [0.0] * 24, [0.0] * 24)
check("T14 zero reference mean returns an error, not a silent 1.0",
      bad_wd is None and "error" in bad_info)
_, _, clip = apply_dhw_volume_scaling(PROTO_WD, PROTO_WE, [5.0] * 24, [5.0] * 24, FLAT, FLAT,
                                      r_max=3.0)
check("T15 r saturating at r_max is reported, not hidden", clip["r_clipped_at_r_max"] is True)
check("T16 r_max actually caps r", abs(clip["r_wd"] - 3.0) < 1e-9)
cap_wd, _, cap = apply_dhw_volume_scaling(PROTO_WD, PROTO_WE, [1.0] * 24, [1.0] * 24, FLAT, FLAT,
                                          peak_policy="cap")
check("T17 peak_policy='cap' holds R at <= 1", cap["R"] <= 1.0 + 1e-12)
check("T18 'cap' with r > 1 clips the schedule and the clip is visible in new_max",
      cap["new_max"] <= 1.0 + 1e-12 and cap["new_max"] > cap["proto_max"] - 1e-12)

# ---------------------------------------------------------------------------
print("\n-- group 5: the audit must be able to FAIL --")
# ---------------------------------------------------------------------------
_, _, good = apply_dhw_volume_scaling(PROTO_WD, PROTO_WE, occ_wd, occ_we, FLAT, FLAT)
a_good = audit_dhw_shape_preservation([rec(good)], verbose=False)
check("T19 audit passes on genuine T9-13 output", a_good["pass"] is True)

a_empty = audit_dhw_shape_preservation([], verbose=False)
check("T20 audit on an EMPTY list is a FAIL, not a vacuous PASS", a_empty["pass"] is False)

# The T9-11 signature: night share moved and the peak hour moved. This is the arm-D failure.
t911 = dict(good, proto_nightshare_wd=0.0354, new_nightshare_wd=0.3730,
            proto_peakhour_wd=7, new_peakhour_wd=0)
a_t911 = audit_dhw_shape_preservation([rec(t911)], verbose=False)
check("T21 audit FAILS on the T9-11 signature (D1 night share)",
      a_t911["pass"] is False and a_t911["counts"]["D1"] == 1)
check("T22 audit FAILS on the T9-11 signature (D2 peak hour)", a_t911["counts"]["D2"] == 1)

t_bound = dict(good, proto_max=0.57, new_max=0.91)
check("T23 audit FAILS when the Fraction bound was restored by clipping (D3)",
      audit_dhw_shape_preservation([rec(t_bound)], verbose=False)["counts"]["D3"] == 1)

t_vol = dict(good, new_mean_wd=good["new_mean_wd"] * 1.5)
check("T24 audit FAILS when the achieved volume ratio != the intended one (D4)",
      audit_dhw_shape_preservation([rec(t_vol)], verbose=False)["counts"]["D4"] == 1)

t_clip = dict(good, r_clipped_at_r_max=True)
check("T25 audit FAILS when an object saturated at r_max (D5)",
      audit_dhw_shape_preservation([rec(t_clip)], verbose=False)["counts"]["D5"] == 1)

check("T26 audit FAILS on a record with no T9-13 info at all (D0)",
      audit_dhw_shape_preservation([{"name": "x", "channel": "office", "t9_13": {}}],
                                   verbose=False)["pass"] is False)

# ---------------------------------------------------------------------------
print("\n-- group 6: FINDING 3 -- the audit cannot pass by omission (D6) --")
# ---------------------------------------------------------------------------
four = ("office", "retail", "hotel", "residential")
commercial_only = [rec(good, "o", "office"), rec(good, "r", "retail"), rec(good, "h", "hotel")]
a_missing = audit_dhw_shape_preservation(commercial_only, verbose=False, expect_channels=four)
check("T27 a requested channel contributing 0 objects is a FAIL (D6)",
      a_missing["pass"] is False and a_missing["counts"]["D6"] == 1)
check("T28 the D6 violation names the missing channel",
      any("residential" in str(x.get("detail", "")) for x in a_missing["violations"]))
check("T29 without expect_channels the same input still passes -- i.e. D6 is what closes the hole",
      audit_dhw_shape_preservation(commercial_only, verbose=False)["pass"] is True)
all_four = commercial_only + [rec(good, "res", "residential")]
check("T30 all requested channels present -> PASS",
      audit_dhw_shape_preservation(all_four, verbose=False, expect_channels=four)["pass"] is True)
check("T31 a channel NOT requested is not demanded (deliberate hotel absence stays legal)",
      audit_dhw_shape_preservation(
          [rec(good, "o", "office"), rec(good, "r", "retail"), rec(good, "res", "residential")],
          verbose=False, expect_channels=("office", "retail", "residential"))["pass"] is True)

# ---------------------------------------------------------------------------
print("\n-- group 7: FINDING 4 -- the reference must be per day type --")
# ---------------------------------------------------------------------------
# Office Y2022: mean_wd = 0.253013, mean_we = 0.065079. These are the shipped reference values.
ref = DHW_MODEL_VOLUME_SCALED["reference_occ_mean"]["office"]
o_wd, o_we = [ref["wd"]] * 24, [ref["we"]] * 24

_, _, per_dt = apply_dhw_volume_scaling(PROTO_WD, PROTO_WE, o_wd, o_we,
                                        [ref["wd"]] * 24, [ref["we"]] * 24)
check("T32 per-day-type reference makes the BASELINE an exact no-op",
      abs(per_dt["r_wd"] - 1) < 1e-9 and abs(per_dt["r_we"] - 1) < 1e-9)

# The old scalar form, for comparison: one 5/2-weighted weekly mean for both day types.
weekly = (5 * ref["wd"] + 2 * ref["we"]) / 7.0
_, _, scalar = apply_dhw_volume_scaling(PROTO_WD, PROTO_WE, o_wd, o_we,
                                        [weekly] * 24, [weekly] * 24)
check("T33 a FLAT scalar reference does NOT make the baseline a no-op",
      abs(scalar["r_wd"] - 1) > 0.2 and abs(scalar["r_we"] - 1) > 0.2,
      f"r_wd={scalar['r_wd']} r_we={scalar['r_we']}")
check("T34 the scalar form double-counts the day-type asymmetry",
      abs(scalar["r_we"] / scalar["r_wd"] - ref["we"] / ref["wd"]) < 1e-6)
check("T35 and the double-count is large enough to matter (>3x distortion)",
      (ref["we"] / ref["wd"]) < 0.33)

REF_MAP = DHW_MODEL_VOLUME_SCALED["reference_occ_mean"]
check("T36 shipped reference_occ_mean is per-day-type for every channel",
      all(isinstance(v, dict) and "wd" in v and "we" in v for v in REF_MAP.values()))
check("T37 shipped reference covers all four declared channels",
      set(DHW_MODEL_VOLUME_SCALED["reference_occ_mean"]) ==
      set(DHW_MODEL_VOLUME_SCALED["channels"]))
check("T38 shipped reference values are all strictly positive",
      all(v["wd"] > 0 and v["we"] > 0
          for v in DHW_MODEL_VOLUME_SCALED["reference_occ_mean"].values()))

# ---------------------------------------------------------------------------
print("\n-- group 8: pre-registered edge case -- an all-zero occupancy household --")
# ---------------------------------------------------------------------------
# 11 of 7175 households have mean_wd == 0. If drawn, D2 fires legitimately. Recorded so that a
# post-arm-E FAIL of this exact shape is read as the known edge case, not as a shape bug.
z_wd, z_we, z = apply_dhw_volume_scaling(PROTO_WD, PROTO_WE, [0.0] * 24, [0.5] * 24, FLAT, FLAT)
check("T39 a zero-occupancy weekday yields an identically zero weekday schedule",
      z_wd is not None and max(z_wd) == 0.0)
check("T40 and the audit FAILS it on D2, loudly rather than silently",
      audit_dhw_shape_preservation([rec(z)], verbose=False)["counts"]["D2"] == 1)

# ---------------------------------------------------------------------------
print("\n-- group 9: FINDING 9 -- Saturday must carry its OWN prototype curve --")
# ---------------------------------------------------------------------------
# The real RetailStandalone BLDG_SWH_SCH shape: a busy Saturday and a much quieter Sunday. This is
# the pair the old reader collapsed (`sun or sat`) and the old writer emitted to "For: Weekends".
SAT = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.05, 0.10, 0.30, 0.55, 0.60, 0.62,
       0.60, 0.58, 0.55, 0.52, 0.48, 0.40, 0.30, 0.20, 0.10, 0.05, 0.0, 0.0]
SUN = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.05, 0.10, 0.15, 0.20,
       0.22, 0.22, 0.20, 0.18, 0.15, 0.10, 0.05, 0.0, 0.0, 0.0, 0.0, 0.0]


def by_dt(wd, sat, sun, hol=None):
    m = {d: list(wd) for d in _WEEKDAY_DAYTYPES}
    m["Saturday"], m["Sunday"] = list(sat), list(sun)
    m["Holidays"] = list(hol if hol is not None else sun)
    return m


PROTO_BY_DT = by_dt(PROTO_WD, SAT, SUN)

# --- the defect itself, reproduced then fixed ---
_, _, i_old = apply_dhw_volume_scaling(PROTO_WD, SUN, FLAT, FLAT, FLAT, FLAT)
_, _, i_new = apply_dhw_volume_scaling(PROTO_WD, SUN, FLAT, FLAT, FLAT, FLAT,
                                       proto_by_daytype=PROTO_BY_DT)
check("T41 the collapsed weekend really did differ from Saturday (the defect is real)",
      abs(mean(SAT) - mean(SUN)) > 0.05, f"sat={mean(SAT):.4f} sun={mean(SUN):.4f}")
check("T42 at r == 1 every day type now reproduces its own prototype exactly",
      all(abs(i_new["daytype_ratio"][d] - 1.0) < 1e-9 for d in i_new["daytype_ratio"]))
check("T43 the per-day-type map is reported as multi-profile",
      i_new["n_distinct_daytypes"] == 3, str(i_new["n_distinct_daytypes"]))
check("T44 without the map there is no day-type evidence at all (D8 cannot run)",
      i_old.get("daytype_ratio") is None)

# --- D8 SEEN FAILING: hand it exactly what the old writer produced ---
# Saturday written with SUNDAY's curve is the FINDING 9 signature. Everything else identical.
i_bad = dict(i_new)
i_bad["daytype_ratio"] = dict(i_new["daytype_ratio"])
i_bad["daytype_ratio"]["Saturday"] = round(mean(SUN) / mean(SAT), 8)   # what collapsing achieves
a_bad = audit_dhw_shape_preservation([rec(i_bad)], verbose=False)
a_good = audit_dhw_shape_preservation([rec(i_new)], verbose=False)
check("T45 D8 FAILS on the collapsed-Saturday signature", a_bad["counts"]["D8"] == 1)
check("T46 and the violation names Saturday", any(
    x["check"] == "D8" and "Saturday" in x["detail"] for x in a_bad["violations"]))
check("T47 the same object PASSES once Saturday carries its own curve",
      a_good["pass"] and a_good["counts"]["D8"] == 0)
check("T48 D4 alone does NOT catch it -- which is why D8 had to exist",
      a_bad["counts"]["D4"] == 0)

# --- D8 is not vacuous: it must also fail when r != 1 and a day type is off ---
_, _, i_r = apply_dhw_volume_scaling(PROTO_WD, SUN, [0.75] * 24, [0.25] * 24, FLAT, FLAT,
                                     proto_by_daytype=PROTO_BY_DT)
check("T49 with r_wd != r_we the weekday/weekend ratios differ as intended",
      abs(i_r["daytype_ratio"]["Monday"] - i_r["daytype_ratio"]["Sunday"]) > 1e-6)
check("T50 Saturday and Sunday share the weekend ratio (same class, own shapes)",
      abs(i_r["daytype_ratio"]["Saturday"] - i_r["daytype_ratio"]["Sunday"]) < 1e-9)
i_r_bad = dict(i_r, daytype_ratio=dict(i_r["daytype_ratio"]))
i_r_bad["daytype_ratio"]["Saturday"] *= 1.05
check("T51 D8 still fails at r != 1 (the gate is not an r == 1 special case)",
      audit_dhw_shape_preservation([rec(i_r_bad)], verbose=False)["counts"]["D8"] == 1)

# --- an object with no map is UNCHECKED, never a silent pass ---
a_unk = audit_dhw_shape_preservation([rec(i_old)], verbose=False)
check("T52 an object with no per-day-type map is reported as D8-unchecked",
      a_unk["d8_unchecked"] == ["obj"])

# --- the writer ---
fields = _build_compact_fields_by_daytype("TEST_SCH", PROTO_BY_DT)
fors = [f for f in fields if str(f).startswith("For:")]
check("T53 the writer emits one block per distinct profile", len(fors) == 3, str(fors))
check("T54 Saturday and Sunday are separate blocks",
      any("Saturday" in f and "Sunday" not in f for f in fors)
      and any("Sunday" in f and "Saturday" not in f for f in fors), str(fors))
check("T55 the weekday block still carries the design days",
      any("Weekdays" in f and "SummerDesignDay" in f for f in fors), str(fors))
check("T56 the final block carries AllOtherDays so coverage is total",
      fors[-1].endswith("AllOtherDays"), str(fors))
one = _build_compact_fields_by_daytype("TEST1", by_dt(PROTO_WD, PROTO_WE, PROTO_WE))
check("T57 a genuine 2-profile prototype still emits exactly 2 blocks",
      len([f for f in one if str(f).startswith("For:")]) == 2)
try:
    _build_compact_fields_by_daytype("TEST2", {"Monday": PROTO_WD})
    _raised = False
except AssertionError:
    _raised = True
check("T58 an incomplete day-type map RAISES rather than filling silently", _raised)

# ---------------------------------------------------------------------------
n_pass = sum(1 for _, ok, _ in _RESULTS if ok)
n = len(_RESULTS)
print(f"\n{'=' * 70}\n{n_pass}/{n} primitive tests pass")
if n_pass != n:
    print("FAILURES:")
    for name, ok, detail in _RESULTS:
        if not ok:
            print(f"  - {name}  {detail}")
sys.exit(0 if n_pass == n else 1)
