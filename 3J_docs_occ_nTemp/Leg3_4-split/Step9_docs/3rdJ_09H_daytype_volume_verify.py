#!/usr/bin/env python3
"""FINDING 9 at the OUTPUT level: does Saturday actually differ from Sunday in delivered volume?

Everything recorded about FINDING 9 so far is schedule-level. The smoke test (job 1171449) compared
IDF schedules before and after the fix; `D9` reads the saved IDF; `3rdJ_09F_daytype_loss.py` parses
IDFs with an independent reader. All three ask "is the right thing written into the IDF?" -- none of
them asks "did EnergyPlus deliver it?". Those are different questions, and the whole point of arm
H's volume series is that the second one is now answerable.

So: predict each channel's mean SATURDAY and mean SUNDAY hourly volume from the IDF (peak flow x
day-type profile, corrected reader), and measure the same two quantities from
`dhw_volume_hourly.csv` by binning the 8760 rows onto the run period's real calendar.

PRE-REGISTERED, 2026-08-03, before the first run:

  G1  For every drawing channel, |predicted/measured - 1| <= 1 % on BOTH Saturday and Sunday.
      1 % because the annual identity already closes to 0.00 %; a day-type split that is right
      should not be looser than the annual total it sums to.
  G2  office and retail must show Saturday != Sunday by more than 1 %.
      Their schedules carry separate `For: Saturday` and `For: Sunday ...` blocks post-FINDING-9.
      If the delivered volumes come out equal, the fix did not reach the simulation.
  G3  The two hotel laundry objects' channel must NOT be required to differ -- their prototype has
      one all-day block, Sat == Sun by construction, and the FINDING 9 smoke's discriminating
      prediction was exactly that F30 stays put. A hotel Sat/Sun difference near zero is a PASS
      for hotel, and G2 deliberately does not apply to it.

G2 and G3 are the pair that makes this test non-vacuous: one channel is required to move and
another is required not to. A bug that flattened all day types would fail G2; a bug that invented a
weekend difference everywhere would fail G3.

RESULT, arm H job 1171607, all 56 cells: **40 PASS / 16 FAIL**. The FAIL stands in the record. The
cause was located and it is in THIS PREDICTOR, not in the delivered volume:

  * The first version read `Schedule:Compact` only. The injector REWRITES a channel's DHW schedules
    as Schedule:Compact, so an injected channel is readable -- but a channel that was NOT requested
    for a cell keeps the prototype's `Schedule:Year -> Schedule:Week:Daily -> Schedule:Day:Interval`
    chain. `comp.get(sch)` returned None, the object was skipped, and the channel was predicted at
    0.0 while EnergyPlus delivered it in full (hotel: predicted 0.0000 vs measured 2.9237 m3/h).
  * The 16 FAILs are exactly the cells with an un-injected drawing channel, and nothing else:
    `Default_NECB` x4 (channels_requested=[] -- all four channels un-injected) and
    `Y2005`/`Y2010`/`Y2015` x12 (channels_requested=['office','retail','residential'], hotel
    un-injected because the QC hotel truth series starts in 2019). 40/40 fully-injected cells PASS.

Two things were changed in response, neither of them the band:
  1. the predictor now walks the Schedule:Year chain and Schedule:Constant, so an un-injected
     channel is predicted rather than skipped;
  2. an unreadable schedule is now an explicit, itemised FAIL. Silently predicting 0.0 for a
     schedule form the reader does not understand is how a -100 % error got attributed to the
     simulation instead of to the reader, and it is the failure mode this file must not have.

  RE-PRE-REGISTERED before re-running (2026-08-03, job 1171657): with the Schedule:Year chain read,
  the 16 cells go to PASS at the SAME 1 % band, the 40 already-passing cells are unchanged, and
  `n_unreadable` is 0 on all 56. If the year reader is wrong, the 16 miss the band -- they do not
  quietly become 0.0 again.

A separate limitation, recorded because it bounds what G2 proves: the office Sat/Sun ratio in the
zero-injection `Default_NECB` control is 2.5169 -- identical to four decimals to the fully-injected
arm-H cells. The Sat/Sun RATIO is inherited from the DOE prototype and is structurally invariant
under T9-13 (Saturday and Sunday both take the same weekend multiplier r_we, which cancels in the
ratio). So G2 separates "FINDING-9-fixed injector" from "pre-fix injector, which collapses Sat onto
Sun" -- its stated counterfactual -- but it does NOT separate "injected" from "not injected at all".
The gate that does that is G1, and G1 is what caught all 16.

    python 3rdJ_09H_daytype_volume_verify.py <cell_dir> [<cell_dir> ...]
"""
import importlib.util
import os
import re
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
TOL_MATCH = 0.01        # G1
TOL_DIFFER = 0.01       # G2
CHANNELS = ["office", "retail", "hotel", "residential"]

_spec = importlib.util.spec_from_file_location(
    "ind", os.path.join(HERE, "3rdJ_09H_volume_identity_indep.py"))
ind = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ind)
_p09e = ind._p09e

_DOW_INDEX = {"MONDAY": 0, "TUESDAY": 1, "WEDNESDAY": 2, "THURSDAY": 3,
              "FRIDAY": 4, "SATURDAY": 5, "SUNDAY": 6}


def start_dow(O):
    """Weekday index (Mon=0) of the run period's first day, read from the IDF."""
    for f in O.get("RUNPERIOD", []):
        for tok in f[5:]:
            k = str(tok).strip().upper()
            if k in _DOW_INDEX:
                return _DOW_INDEX[k]
    return 6      # the RunPeriod in these IDFs starts Sunday; only reached if it is missing


def _channel(name, sch):
    """Channel for one WaterUse:Equipment, from its schedule token or its own name.

    The schedule-token rule alone is not enough: the injector names residential schedules
    `MXU_Residential_DHWv2_HH<id>_...`, which carries no prototype token, so a token-only mapping
    silently sends all 27 residential objects to `unassigned` and predicts 0.0 volume for the
    channel. (It did, on the first run of this script -- caught by G1, which is the point of having
    predicted and measured side by side rather than only a Sat/Sun ratio.)
    """
    s, n = sch.upper(), name.upper()
    for tok, ch in (("HOTELLARGE", "hotel"), ("OFFICELARGE", "office"),
                    ("RETAILSTANDALONE", "retail"),
                    ("MXU_RESIDENTIAL", "residential"),
                    ("MIDRISEAPARTMENT", "residential"), ("HIGHRISEAPARTMENT", "residential")):
        if tok in s:
            return ch
    if any(t in n for t in _p09e.RESID_TOKENS):
        return "residential"
    return "unassigned"


def daytype_means(fields):
    """{day key: mean fraction} for a Schedule:Compact, first Through period only.

    Reuses ind._for_targets, so the day-type resolution is the same corrected logic the annual
    identity was verified with -- a second implementation here would be a second thing to be wrong.
    """
    days, assigned, targets = {}, set(), []
    until, prev, seen = 0, 0, 0
    import re
    for tok in fields[3:]:
        t = tok.strip()
        if not t:
            continue
        up = t.upper()
        if up.startswith("THROUGH"):
            seen += 1
            if seen > 1:
                break
            continue
        if up.startswith("FOR"):
            targets = sorted(ind._for_targets(t, assigned))
            assigned |= set(targets)
            for k in targets:
                days.setdefault(k, [0.0] * 24)
            prev = 0
            continue
        m = re.match(r"UNTIL:\s*(\d+):(\d+)", up)
        if m:
            until = int(m.group(1)) * 60 + int(m.group(2))
            continue
        try:
            v = float(t)
        except ValueError:
            continue
        for k in targets:
            for h in range(24):
                if prev <= h * 60 < until:
                    days[k][h] = v
        prev = until
    return {k: sum(v) / 24.0 for k, v in days.items()}


# ------------------------------------------------------------------------------------------------
# Schedule:Year chain reader -- for channels the injector did NOT rewrite as Schedule:Compact
# ------------------------------------------------------------------------------------------------
_CUM = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365]
# Schedule:Week:Daily field slots (f[0] is the object type): Sunday=2, Mon..Fri=3..7, Saturday=8
_WEEK_SLOT = {"sun": 2, "sat": 8}
_WEEK_WD_SLOTS = (3, 4, 5, 6, 7)


def _doy(month, day):
    return _CUM[max(1, min(12, month)) - 1] + day


def _day_mean(f):
    """Mean fraction over 24 h of one Schedule:Day:* object, or None if the form is unsupported."""
    t = f[0].upper()
    if t == "SCHEDULE:DAY:HOURLY":
        vals = []
        for tok in f[3:27]:
            try:
                vals.append(float(tok))
            except (TypeError, ValueError):
                pass
        return sum(vals) / 24.0 if len(vals) == 24 else None
    if t == "SCHEDULE:DAY:INTERVAL":
        hours = [0.0] * 24
        prev, pend = 0, None
        for tok in f[4:]:                       # f[3] is `Interpolate to Timestep`
            s = str(tok).strip()
            if not s:
                continue
            m = re.match(r"(?:UNTIL:\s*)?(\d+):(\d+)$", s.upper())
            if m:
                pend = int(m.group(1)) * 60 + int(m.group(2))
                continue
            try:
                v = float(s)
            except ValueError:
                continue
            if pend is None:
                continue
            for h in range(24):
                if prev <= h * 60 < pend:
                    hours[h] = v
            prev, pend = pend, None
        return sum(hours) / 24.0
    return None


def _year_index(O):
    yr = {f[1].upper(): f for f in O.get("SCHEDULE:YEAR", [])}
    wk = {f[1].upper(): f for f in O.get("SCHEDULE:WEEK:DAILY", [])}
    dy = {}
    for t in ("SCHEDULE:DAY:INTERVAL", "SCHEDULE:DAY:HOURLY"):
        for f in O.get(t, []):
            dy[f[1].upper()] = f
    const = {}
    for f in O.get("SCHEDULE:CONSTANT", []):
        try:
            const[f[1].upper()] = float(f[3])
        except (IndexError, ValueError):
            pass
    return yr, wk, dy, const


def yearly_daytype_means(idx, name):
    """{'sat','sun'} mean fractions for a Schedule:Year / Schedule:Constant, or None if unreadable.

    Week periods are weighted by their real day span, so a schedule that changes across the year is
    not read as its first week. Returns None -- never a silent 0.0 -- when any link in the
    Year -> Week:Daily -> Day:* chain is missing or of a form this reader does not support.
    """
    yr, wk, dy, const = idx
    key = name.upper()
    if key in const:
        return {"sat": const[key], "sun": const[key]}
    f = yr.get(key)
    if f is None:
        return None
    acc = {"sat": 0.0, "sun": 0.0}
    span, prev_end, i = 0, 0, 3
    while i + 4 < len(f):
        wf = wk.get(str(f[i]).strip().upper())
        try:
            end = _doy(int(float(f[i + 3])), int(float(f[i + 4])))
        except (ValueError, TypeError):
            return None
        ndays = max(0, end - prev_end)
        prev_end = end
        if ndays:
            if wf is None:
                return None                      # Schedule:Week:Compact, or a dangling reference
            for k, slot in _WEEK_SLOT.items():
                m = _day_mean(dy[str(wf[slot]).strip().upper()]) \
                    if str(wf[slot]).strip().upper() in dy else None
                if m is None:
                    return None
                acc[k] += m * ndays
            span += ndays
        i += 5
    if span == 0:
        return None
    return {k: v / span for k, v in acc.items()}


def predict_daytype(idf_path):
    """{channel: {'sat': m3/h, 'sun': m3/h}} mean hourly volume predicted per day type.

    Returns (per-channel prediction, start weekday, [unreadable object descriptions]). An object
    whose schedule cannot be read is NOT skipped silently -- it is returned and reported, because a
    silent skip predicts 0.0 and blames the simulation for the reader's gap.
    """
    O = _p09e.parse(idf_path)
    comp = {f[1].upper(): f for f in O.get("SCHEDULE:COMPACT", [])}
    idx = _year_index(O)
    out, unreadable = {}, []
    for f in O.get("WATERUSE:EQUIPMENT", []):
        try:
            peak = float(f[3])
        except (ValueError, IndexError):
            continue
        sch = (f[4] if len(f) > 4 else "").upper()
        cf = comp.get(sch)
        if cf is not None:
            means = daytype_means(cf)
        else:
            # not rewritten by the injector -- walk the prototype's Schedule:Year chain
            means = yearly_daytype_means(idx, sch)
            if means is None:
                if peak > 0:
                    unreadable.append("%s  <- %s" % (f[1], f[4] if len(f) > 4 else "(no schedule)"))
                continue
        ch = _channel(f[1], sch)
        d = out.setdefault(ch, {"sat": 0.0, "sun": 0.0})
        for key in ("sat", "sun"):
            # a day type with no block of its own draws nothing -- do NOT fall back to weekday
            d[key] += peak * means.get(key, 0.0) * 3600.0
    return out, start_dow(O), unreadable


def run(cell_dir):
    name = os.path.basename(cell_dir.rstrip("/\\"))
    print("=" * 86)
    print("CELL %s" % name)
    print("=" * 86)
    vol_p = os.path.join(cell_dir, "dhw_volume_hourly.csv")
    idf = None
    for n in sorted(os.listdir(cell_dir)):
        if n.endswith(".idf") and "injected" in n:
            idf = os.path.join(cell_dir, n)
            break
    if not os.path.isfile(vol_p) or idf is None:
        print("  SKIP: need dhw_volume_hourly.csv and an injected .idf")
        return None

    vol = pd.read_csv(vol_p)
    pred, dow0, unreadable = predict_daytype(idf)
    day = np.arange(len(vol)) // 24
    dow = (dow0 + day) % 7
    sat_m = dow == 5
    sun_m = dow == 6
    print("  run period starts on weekday index %d (Mon=0); %d Saturdays, %d Sundays in the series"
          % (dow0, sat_m.sum() // 24, sun_m.sum() // 24))
    print("")
    print("  %-13s %9s %9s %7s %9s %9s %7s %9s"
          % ("channel", "sat pred", "sat meas", "err %", "sun pred", "sun meas", "err %", "sat/sun"))

    g1 = g2 = True
    g2_seen = {}
    for ch in CHANNELS:
        col = "dhwvol_" + ch
        if col not in vol.columns:
            continue
        v = vol[col].to_numpy()
        if np.nansum(v) <= 0:
            continue
        ms = float(np.nanmean(v[sat_m]))
        mu = float(np.nanmean(v[sun_m]))
        ps = pred.get(ch, {}).get("sat", 0.0)
        pu = pred.get(ch, {}).get("sun", 0.0)
        es = (ps / ms - 1.0) if ms else float("nan")
        eu = (pu / mu - 1.0) if mu else float("nan")
        ratio = (ms / mu) if mu else float("nan")
        ok = (abs(es) <= TOL_MATCH) and (abs(eu) <= TOL_MATCH)
        g1 = g1 and ok
        g2_seen[ch] = abs(ratio - 1.0) if np.isfinite(ratio) else 0.0
        print("  %-13s %9.4f %9.4f %+6.2f %9.4f %9.4f %+6.2f %9.4f%s"
              % (ch, ps, ms, 100 * es, pu, mu, 100 * eu, ratio, "" if ok else "   <-- G1 FAIL"))

    print("")
    print("  [%s] G1  predicted vs measured within %.0f %% on both day types, every channel"
          % ("PASS" if g1 else "FAIL", 100 * TOL_MATCH))
    for ch in ("office", "retail"):
        if ch in g2_seen:
            hit = g2_seen[ch] > TOL_DIFFER
            g2 = g2 and hit
            print("  [%s] G2  %s Saturday differs from Sunday by %.2f %% (require > %.0f %%)"
                  % ("PASS" if hit else "FAIL", ch, 100 * g2_seen[ch], 100 * TOL_DIFFER))
    if "hotel" in g2_seen:
        print("  [INFO] G3  hotel Sat/Sun difference %.2f %% -- NOT required to move "
              "(prototype laundry is one all-day block)" % (100 * g2_seen["hotel"]))
    g4 = not unreadable
    print("  [%s] G4  every drawing WaterUse:Equipment schedule was READ, not skipped "
          "(%d unreadable)" % ("PASS" if g4 else "FAIL", len(unreadable)))
    for u in unreadable[:10]:
        print("         unreadable: %s" % u)
    return g1 and g2 and g4


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    res = []
    for d in sys.argv[1:]:
        res.append((os.path.basename(d.rstrip("/\\")), run(d)))
        print("")
    print("=" * 86)
    for nm, v in res:
        print("  %-30s %s" % (nm, "skipped" if v is None else ("PASS" if v else "FAIL")))
    tested = [v for _, v in res if v is not None]
    print("=" * 86)
    sys.exit(0 if tested and all(tested) else 1)


if __name__ == "__main__":
    main()
