"""T9-13 IDENTITY PROBE -- does r = 1 actually behave as a no-op?

Why this exists. Arm E scored 3 FAIL / 2 PASS / 1 UNTESTABLE against pre-registered predictions.
P4 (residential) came in at +51.4 % against a predicted +8..+18 %. The obvious reading is "the
T9-11 blow-up is back", but the r distribution refutes that: mean r_wd 1.09-1.16, median ~1.11,
max 1.574, and ZERO households above 2.0. Those r values cannot produce +51 %.

The decisive case is `Y2022`. The T9-13 reference IS Y2022, so r must be ~1 there by construction,
and the measured r confirms it (r_wd mean 0.984, r_we 0.979). **Volume scaling with r = 1 is
required to be a no-op.** Yet Y2022 residential DHW energy is 1.412x the uninjected prototype.

Arm C is not a confound: its DHW is bit-identical to `Default_NECB` in every channel and every
scenario (ratio 1.000 across the board), so E/C is E/prototype.

The identity being tested, from the T9-13 specification:

    Peak_Flow_Rate' = P * R                      R = max_d r(d)
    f_new(t)        = s_proto(t) * r(d) / R
    => volume       = P * R * mean_t[s_proto * r/R] = P * mean_t[s_proto * r]
    => volume ratio = weighted mean of r(d)      -- R cancels, exactly

So the probe computes, per residential WaterUse:Equipment object, the quantity that actually
drives annual volume:

    V = Peak_Flow_Rate * (5 * mean_wd(schedule) + 2 * mean_we(schedule)) / 7

for the INJECTED cell and for the UNINJECTED `Default_NECB` cell of the same geometry, and reports
sum(V_inj) / sum(V_necb). Under the identity that ratio must equal the r reported in the same
cell's provenance file. If it does not, the defect is in the injector, not in the occupancy input.

Why the existing audit cannot see this. D1 (night share), D2 (peak hour), D3 (fraction <= 1) and
D5 (r saturation) are ALL scale-invariant -- multiplying an entire schedule by a constant leaves
every one of them unchanged. Only D4 speaks to volume, and it evidently checks a quantity that is
not the peak-times-schedule product, because D4 recorded 0 violations across all 56 cells while
this ratio is 1.41 where it must be 1.00. That blind spot is the finding, whatever the cause
turns out to be.

Usage (on the cluster, via sbatch):
    python 3rdJ_09E_dhw_identity_probe.py <injected_cell_dir> <necb_cell_dir>
"""
from __future__ import annotations

import os
import re
import sys
from collections import defaultdict

RESID_TOKENS = ("APARTMENT", "DWELL", "HIGHRISE", "RESI")


def parse(path):
    txt = open(path, "r", errors="replace").read()
    txt = re.sub(r"!.*", "", txt)
    objs = defaultdict(list)
    for blk in txt.split(";"):
        f = [x.strip() for x in blk.split(",")]
        while f and f[0] == "":
            f.pop(0)
        if not f:
            continue
        objs[f[0].upper()].append(f)
    return objs


def _day_from_interval(f):
    vals, prev = [0.0] * 24, 0
    rest = f[4:]
    for i in range(0, len(rest) - 1, 2):
        t, v = rest[i], rest[i + 1]
        m = re.match(r"(?:Until:\s*)?(\d+):(\d+)", t, re.I)
        if not m:
            continue
        try:
            v = float(v)
        except ValueError:
            continue
        end = int(m.group(1)) * 60 + int(m.group(2))
        for h in range(24):
            if prev <= h * 60 < end:
                vals[h] = v
        prev = end
    return vals


def _for_field_is_ambiguous(up):
    """True when one `For:` field names BOTH a weekday and a weekend day type.

    Guard added 2026-08-03 after `3rdJ_09H_volume_identity_indep.py` measured this reader against
    EnergyPlus's own reported volume and found it 36.9 % low. The day-type chain below is
    first-match-wins, so a field written as

        For: Weekdays Saturday Sunday Holidays SummerDesignDay WinterDesignDay AllOtherDays

    (the hotel laundry schedules -- the largest DHW draw in the tower) matches "SATURDAY" first and
    collapses ALL SEVEN day types onto the weekend bucket, leaving the weekday profile at 0.0. The
    reader then reports mean 0.0833 for a schedule whose true annual mean is 0.2917: a factor 3.5.

    The reader is NOT silently rewritten -- its published output is the residential-only 0.9647
    figure, and residential schedules never use this form (verified: residential closes against
    EnergyPlus at 1.00006 even with the defect live). Instead the ambiguous case is refused, so it
    surfaces through the existing `n_unres` / WARNING path in main() rather than being mis-read.
    Anything that needs commercial objects must use the corrected reader in 3rdJ_09H.
    """
    weekday = "WEEKDAY" in up
    weekend = ("WEEKEND" in up) or ("SATURDAY" in up) or ("SUNDAY" in up)
    return weekday and weekend


def compact_profiles(f):
    """Schedule:Compact -> (weekday 24h, weekend 24h). Takes the FIRST Through period; the
    injector writes a single annual Through, and if that ever stops being true this probe should
    be revisited rather than silently averaging periods that differ.

    Returns (None, None) on a `For:` field this reader cannot resolve unambiguously -- see
    _for_field_is_ambiguous()."""
    wd, we = [0.0] * 24, [0.0] * 24
    cur, prev = None, 0
    seen_through = 0
    for tok in f[3:]:
        t = tok.strip()
        if not t:
            continue
        up = t.upper()
        if up.startswith("THROUGH"):
            seen_through += 1
            if seen_through > 1:
                break
            continue
        if up.startswith("FOR"):
            prev = 0
            if _for_field_is_ambiguous(up):
                return None, None
            if "WEEKEND" in up or "SATURDAY" in up or "SUNDAY" in up:
                cur = "we"
            elif "ALLDAY" in up or "ALLOTHERDAY" in up or "ALL DAY" in up:
                cur = "all"
            else:
                cur = "wd"
            continue
        m = re.match(r"UNTIL:\s*(\d+):(\d+)", up)
        if m:
            _pending[0] = int(m.group(1)) * 60 + int(m.group(2))
            continue
        try:
            v = float(t)
        except ValueError:
            continue
        end = _pending[0]
        for h in range(24):
            if prev <= h * 60 < end:
                if cur in ("wd", "all"):
                    wd[h] = v
                if cur in ("we", "all"):
                    we[h] = v
        prev = end
    return wd, we


_pending = [0]


def build_resolver(O):
    day_i = {f[1].upper(): f for f in O.get("SCHEDULE:DAY:INTERVAL", [])}
    day_h = {f[1].upper(): f for f in O.get("SCHEDULE:DAY:HOURLY", [])}
    wk_d = {f[1].upper(): f for f in O.get("SCHEDULE:WEEK:DAILY", [])}
    yr = {f[1].upper(): f for f in O.get("SCHEDULE:YEAR", [])}
    comp = {f[1].upper(): f for f in O.get("SCHEDULE:COMPACT", [])}

    def day24(name):
        k = name.upper()
        if k in day_h:
            try:
                return [float(x) for x in day_h[k][3:27]]
            except ValueError:
                return None
        if k in day_i:
            return _day_from_interval(day_i[k])
        return None

    def resolve(name):
        k = name.upper()
        if k in comp:
            wd, we = compact_profiles(comp[k])
            if wd is None:
                return None, None, "Compact: REFUSED, multi-day-type For: (use 3rdJ_09H reader)"
            return wd, we, "Compact"
        if k in yr:
            wk = yr[k][3]
            f = wk_d.get(wk.upper())
            if not f:
                return None, None, f"week '{wk}' missing"
            mon, sat, sun = day24(f[3]), day24(f[8]), day24(f[2])
            if mon is None:
                return None, None, f"day of week '{wk}' unresolved"
            sat = sat or mon
            sun = sun or mon
            we = [(a + b) / 2.0 for a, b in zip(sat, sun)]
            return mon, we, f"Year->{wk}"
        return None, None, "unresolved"

    return resolve


def volume_table(idf_path, label):
    O = parse(idf_path)
    resolve = build_resolver(O)
    rows, total, n_unres = [], 0.0, 0
    for f in O.get("WATERUSE:EQUIPMENT", []):
        nm = f[1]
        if not any(t in nm.upper() for t in RESID_TOKENS):
            continue
        try:
            peak = float(f[3])
        except (ValueError, IndexError):
            peak = 0.0
        sch = f[4] if len(f) > 4 else ""
        wd, we, prov = resolve(sch)
        if wd is None:
            n_unres += 1
            rows.append((nm, peak, None, None, 0.0, prov, sch))
            continue
        mwd, mwe = sum(wd) / 24.0, sum(we) / 24.0
        v = peak * (5 * mwd + 2 * mwe) / 7.0
        total += v
        rows.append((nm, peak, mwd, mwe, v, prov, sch))
    print(f"\n=== {label}: {len(rows)} residential WaterUse:Equipment objects "
          f"({n_unres} unresolved) ===")
    print(f"  {'object':<46}{'peak m3/s':>12}{'mean_wd':>9}{'mean_we':>9}{'V':>13}  sched")
    for nm, peak, mwd, mwe, v, prov, sch in rows[:10]:
        if mwd is None:
            print(f"  {nm[:46]:<46}{peak:>12.3e}{'--':>9}{'--':>9}{'--':>13}  {prov} [{sch[:28]}]")
        else:
            print(f"  {nm[:46]:<46}{peak:>12.3e}{mwd:>9.4f}{mwe:>9.4f}{v:>13.4e}  {prov}")
    if len(rows) > 10:
        print(f"  ... {len(rows) - 10} more")
    print(f"  SUM V = {total:.6e}   (peak x schedule-mean, the quantity annual volume follows)")
    return total, n_unres


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    inj_dir, necb_dir = sys.argv[1], sys.argv[2]

    def find_idf(d):
        for n in os.listdir(d):
            if n.endswith(".idf") and "injected" in n:
                return os.path.join(d, n)
        for n in os.listdir(d):
            if n.endswith(".idf"):
                return os.path.join(d, n)
        raise SystemExit(f"no idf in {d}")

    vi, ui = volume_table(find_idf(inj_dir), f"INJECTED  {os.path.basename(inj_dir)}")
    vn, un = volume_table(find_idf(necb_dir), f"UNINJECTED {os.path.basename(necb_dir)}")

    print("\n" + "=" * 78)
    if vn <= 0:
        print("FATAL: uninjected volume is zero -- cannot form a ratio.")
        raise SystemExit(1)
    if ui or un:
        print(f"WARNING: {ui} injected / {un} uninjected objects unresolved. The ratio below")
        print("         excludes them and is therefore a LOWER-CONFIDENCE number, not a verdict.")
    ratio = vi / vn
    print(f"VOLUME RATIO (injected / uninjected) = {ratio:.4f}")
    print("\nThe identity requires this to equal the population-weighted mean of r for this cell.")
    print("Provenance r for Y2022__Tall__MTL: r_wd mean 0.9841, r_we mean 0.9792 -> expect ~0.98.")
    print("If the ratio is materially above that, the excess is introduced by the injector and")
    print("not by the occupancy input, and the audit's D1/D2/D3/D5 cannot see it because all four")
    print("are scale-invariant.")


if __name__ == "__main__":
    main()
