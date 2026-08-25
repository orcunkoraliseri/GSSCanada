# -*- coding: utf-8 -*-
"""4J Step 9, work items 9.2 / 9.3 / 9.4 -- the two-stage trigger, DHW, and the
per-dwelling end-use profiles.

    python 4thJ_step9_trigger.py --root <4J_docs_occ> --fold es

WHAT IS ADAPTED AND WHAT IS OURS
--------------------------------
The state machine below is CREST's, reproduced from the open re-implementation
(`richardsonpy/classes/appliance.py`) rather than reinvented:

  * an appliance is OFF, in RESTART DELAY, or RUNNING;
  * a start event needs an eligible minute and fires with a constant hazard;
  * once started the cycle RUNS TO COMPLETION -- it is never truncated by the
    end of the activity episode, which is the behaviour `G9.5` exists to assert;
  * a running appliance PAUSES when active occupancy falls to zero, except for
    LEVEL (cold appliances), laundry, and CUSTOM -- CREST's own exception list;
  * TV cycle lengths are drawn from CREST's own Weibull-shaped approximation and
    the washing machine follows CREST's own staged power profile.

THE ONE ADAPTATION, STATED PLAINLY. CREST has no diary, so it simulates activity
from a Markov chain and reads `P(activity active at minute t)` out of a table of
TUS statistics. **We have the diary.** So the table look-up is replaced by the
diary's own 0/1 indicator: the appliance is eligible to start in minute `t` when
an ACTIVE occupant is doing an activity that the mapping joins to that
appliance's CREST profile. Nothing else changes.

Because the indicator is 0/1 and CREST's was a population share, the start hazard
has to be recalibrated or the appliance would fire orders of magnitude too often.
It is recalibrated with CREST'S OWN CALIBRATION EQUATION -- expected annual
starts = the published `Cycles per year (n)` -- with our measured eligible-minute
count in place of their `365*24*60 * p_occupancy * activity_probability`. That
preserves the published cycles-per-year at STOCK scale, which is exactly the
quantity `G9.6` tests, and lets the diary redistribute those cycles between
dwellings. A dwelling whose diaries never iron gets no iron cycles; under CREST
every dwelling irons at the national rate. That redistribution IS the step's
contribution, and it is also why the variance is larger than CREST's.

The geometric skip is an exact restatement of the per-minute Bernoulli draw, not
an approximation of it: with a constant hazard `h` over eligible minutes, the
number of eligible minutes until the next start is geometric with parameter `h`.
It is used because a per-minute loop over 33 appliances x 525,600 minutes x 100
dwellings does not finish.
"""
import argparse
import collections
import csv
import hashlib
import io
import json
import math
import os
import random
import sys

DAY_MINUTES = 1440
YEAR_MINUTES = 365 * DAY_MINUTES

# ACL codes that mean the occupant is present but NOT active. CREST's active
# occupancy is "at home and awake"; the diary says which is which, so this is
# read off the corpus rather than modelled.
INACTIVE_ACL = frozenset(["011", "012"])

# CREST's own exception list: these profiles do not pause when the last active
# occupant leaves. 7 = LEVEL, 2 = laundry, 8 = CUSTOM.
NO_PAUSE_PROFILES = frozenset([2, 7, 8])

# CREST's own special cases, keyed by appliance name rather than by row index.
TV_LIKE = frozenset(["TV 1", "TV 2", "TV 3"])
STAGED_POWER = {"Washing machine": 138, "Washer dryer": 198}
GAUSSIAN_CYCLE = frozenset(["Storage heaters", "Other electric space heating"])

# The washing-machine staged power profile, from CREST. (upper bound, watts)
WASHER_STAGES = [(8, 73), (29, 2056), (81, 73), (92, 73), (94, 250), (105, 73),
                 (107, 250), (118, 73), (120, 250), (131, 73), (133, 250),
                 (138, 568), (198, 2500)]


class TriggerError(RuntimeError):
    pass


# --------------------------------------------------------------------------
# the mapping, as data
# --------------------------------------------------------------------------
class Mapping(object):
    """`activity_appliance_map.csv`, indexed the two ways the trigger needs."""

    def __init__(self, path):
        self.rows = list(csv.DictReader(io.open(path, encoding="utf-8")))
        if not self.rows:
            raise TriggerError("%s is empty" % path)
        self.md5 = hashlib.md5(open(path, "rb").read()).hexdigest()

        self.appliances = collections.OrderedDict()
        self.acl_to_profile = {}
        self.dhw = collections.OrderedDict()
        self.dhw_drivers = collections.defaultdict(set)

        for r in self.rows:
            if r["end_use"] == "electricity":
                aid = r["appliance_id"]
                if aid not in self.appliances:
                    self.appliances[aid] = {
                        "id": aid,
                        "name": r["appliance_name"],
                        "group": r["appliance_group"],
                        "profile": int(r["crest_activity_index"]),
                        "rated_power_w": float(r["rated_power_w"]),
                        "standby_power_w": float(r["standby_power_w"]),
                        "cycle_len_min": int(r["mean_cycle_length_min"]),
                        "restart_delay_min": int(r["restart_delay_min"]),
                        "cycles_per_year": float(r["cycles_per_year"]),
                        "ownership_share": float(r["ownership_share"]),
                        "occupancy_dependent": int(r["occupancy_dependent"]),
                        "in_default_dwelling": int(r["in_default_dwelling"]),
                        "power_factor": float(r["power_factor"]),
                    }
                if not r["acl_code"].startswith("*"):
                    prof = int(r["crest_activity_index"])
                    prev = self.acl_to_profile.setdefault(r["acl_code"], prof)
                    if prev != prof:
                        raise TriggerError(
                            "ACL %s is mapped to two CREST profiles (%d and %d). "
                            "One activity cannot drive two states."
                            % (r["acl_code"], prev, prof))
            elif r["end_use"] == "dhw":
                did = r["appliance_id"]
                if did not in self.dhw:
                    self.dhw[did] = {
                        "id": did,
                        "name": r["appliance_name"],
                        "flow_l_per_min": float(r["dhw_flow_l_per_min"]),
                        "duration_min": int(r["dhw_duration_min"]),
                        "inc_per_day": float(r["dhw_inc_per_day"]),
                        "sigma": float(r["dhw_sigma"]),
                        "vol_per_load_l": float(r["dhw_vol_per_load_l"]),
                    }
                self.dhw_drivers[did].add(r["acl_code"])

        if not self.appliances:
            raise TriggerError(
                "the mapping carries no electricity rows. A trigger over an "
                "empty appliance set produces a flat series and every closure "
                "check still reconciles -- V9.b's failure shape.")

    # -- G9.14: what the trigger actually reads at runtime -------------------
    def runtime_input_columns(self):
        """The episode fields this trigger reads. Asserted by `G9.14`.

        It is built HERE, next to the code that reads them, so that it cannot
        drift from the reader. `act2` is absent because `D-S9-1` ruled (d), and
        for no other reason -- see FINDING 137: the generated record DOES carry
        `act2`, so its absence here is a policy, not an accident of the format.
        """
        return ["duration_min", "act", "loc_class"]


# --------------------------------------------------------------------------
# per-minute expansion of one pool day
# --------------------------------------------------------------------------
def day_minutes(day):
    """`(at_home[1440], acl[1440])` for one pool day, cached on the object."""
    cached = day.get("_s9")
    if cached is not None:
        return cached
    flags = day["flags"]
    acl = []
    for dur, act in day["acts"]:
        acl.extend([act] * dur)
    if len(acl) < DAY_MINUTES:
        acl.extend([None] * (DAY_MINUTES - len(acl)))
    elif len(acl) > DAY_MINUTES:
        acl = acl[:DAY_MINUTES]
    at_home = [bool(f) for f in flags]
    if len(at_home) != DAY_MINUTES:
        raise TriggerError("presence flags are %d minutes, expected %d"
                           % (len(at_home), DAY_MINUTES))
    out = (at_home, acl)
    day["_s9"] = out
    return out


def day_profile_index(day, acl_to_profile):
    """Per-pool-day eligibility, computed ONCE and cached on the day object.

    Returns `(prof_minutes, active_runs)`:

      * `prof_minutes[p]` -- sorted minutes in which THIS person is an ACTIVE
        occupant performing an activity that maps to CREST profile `p`, for
        p in 0..6 (6 = ACTIVE OCC, so it is every active minute);
      * `active_runs`     -- `[(start, end)]` half-open runs of active minutes.

    Cached because there are only a few thousand distinct pool days but tens of
    thousands of dwelling-days, and the same day is drawn hundreds of times.
    """
    key = "_s9prof"
    cached = day.get(key)
    if cached is not None:
        return cached
    at_home, acl = day_minutes(day)
    prof = dict((p, []) for p in range(7))
    runs = []
    run_start = None
    for t in range(DAY_MINUTES):
        code = acl[t]
        is_active = at_home[t] and code not in INACTIVE_ACL
        if is_active:
            if run_start is None:
                run_start = t
            prof[6].append(t)
            p = acl_to_profile.get(code)
            if p is not None and p < 6:
                prof[p].append(t)
        elif run_start is not None:
            runs.append((run_start, t))
            run_start = None
    if run_start is not None:
        runs.append((run_start, DAY_MINUTES))
    out = (prof, runs)
    day[key] = out
    return out


def day_acl_index(day):
    """`{acl_code: [minutes]}` over this person's ACTIVE minutes, cached.

    Same reason as `day_profile_index`: a few thousand distinct pool days are
    drawn tens of thousands of times, so the expansion is done once per day and
    never once per dwelling-day.
    """
    key = "_s9acl"
    cached = day.get(key)
    if cached is not None:
        return cached
    at_home, acl = day_minutes(day)
    idx = collections.defaultdict(list)
    for t in range(DAY_MINUTES):
        code = acl[t]
        if code and at_home[t] and code not in INACTIVE_ACL:
            idx[code].append(t)
    out = dict(idx)
    day[key] = out
    return out


def dwelling_day_dhw(member_days, day_index, dhw_drivers):
    """`{dhw_category_id: [eligible minutes]}` for one dwelling-day."""
    out = {}
    for did, codes in dhw_drivers.items():
        lists = []
        for m in member_days:
            idx = day_acl_index(m[day_index])
            for c in codes:
                got = idx.get(c)
                if got:
                    lists.append(got)
        out[did] = _merge_sorted(lists)
    return out


def _merge_sorted(lists):
    """Union of sorted minute lists, de-duplicated. Two people ironing in the
    same minute is ONE eligible minute for the iron, not two."""
    if not lists:
        return []
    if len(lists) == 1:
        return lists[0]
    seen = set()
    for L in lists:
        seen.update(L)
    return sorted(seen)


def dwelling_day(member_days, day_index, acl_to_profile):
    """`(elig_by_profile, active_flags)` for one dwelling on one calendar day."""
    prof_lists = collections.defaultdict(list)
    all_runs = []
    for m in member_days:
        prof, runs = day_profile_index(m[day_index], acl_to_profile)
        for p in range(7):
            if prof[p]:
                prof_lists[p].append(prof[p])
        all_runs.extend(runs)
    elig = dict((p, _merge_sorted(prof_lists.get(p, []))) for p in range(7))
    elig[7] = None                      # LEVEL: every minute; built on demand
    active = [False] * DAY_MINUTES
    for s0, e0 in all_runs:
        active[s0:e0] = [True] * (e0 - s0)
    return elig, active


ALL_MINUTES = list(range(DAY_MINUTES))


def eligible_for(elig, profile):
    return ALL_MINUTES if profile == 7 else elig.get(profile, [])


# --------------------------------------------------------------------------
# CREST's own cycle-length and power helpers
# --------------------------------------------------------------------------
def cycle_length(app, rng):
    if app["name"] in TV_LIKE:
        # CREST's approximation of TUS viewing time; mean about 73 minutes.
        return max(1, int(round(70.0 * (-math.log(1 - rng.random())) ** 1.1)))
    if app["name"] in GAUSSIAN_CYCLE:
        return max(1, int(round(rng.gauss(float(app["cycle_len_min"]),
                                          app["cycle_len_min"] / 10.0))))
    return max(1, int(app["cycle_len_min"]))


def cycle_power(app, elapsed):
    """Power in watts at `elapsed` minutes into the cycle (1-based)."""
    total = STAGED_POWER.get(app["name"])
    if total is None:
        return app["rated_power_w"]
    for upper, watts in WASHER_STAGES:
        if elapsed <= upper:
            return float(watts)
    return app["standby_power_w"]


# --------------------------------------------------------------------------
# calibration -- CREST's equation, our eligible-minute count
# --------------------------------------------------------------------------
def calibrate(app, eligible_per_year_stock, n_dwellings_owning):
    """Constant per-eligible-minute start hazard.

    CREST:      lambda = cycles / (year_minutes*p_occ - t_running - cycles*delay)
                hazard = lambda / mean_activity_probability
    Here:       hazard = cycles / (eligible - unavailable pro-rated to eligible)

    Returns `(hazard, mean_eligible_minutes_per_dwelling_year)`.
    """
    if n_dwellings_owning <= 0:
        return 0.0, 0.0
    mean_elig = float(eligible_per_year_stock) / n_dwellings_owning
    if mean_elig <= 0.0:
        # The stock never performs this activity. The appliance never fires, and
        # that is a RESULT, not a defect to be papered over with a floor.
        return 0.0, 0.0
    unavailable = app["cycles_per_year"] * (app["cycle_len_min"]
                                            + app["restart_delay_min"])
    available = mean_elig - unavailable * (mean_elig / float(YEAR_MINUTES))
    if available <= 0.0:
        raise TriggerError(
            "appliance %r would be busy for more eligible minutes than the "
            "stock supplies (%.1f eligible, %.1f unavailable). CREST's own "
            "calibration cannot be satisfied and the cause needs reading, not "
            "clamping." % (app["name"], mean_elig, unavailable))
    hazard = app["cycles_per_year"] / available
    if hazard >= 1.0:
        raise TriggerError(
            "appliance %r needs a start hazard of %.4f per eligible minute, "
            "which is not a probability. The eligible set is too small for the "
            "published cycles-per-year." % (app["name"], hazard))
    return hazard, mean_elig


# --------------------------------------------------------------------------
# the simulation
# --------------------------------------------------------------------------
def _geometric_skip(hazard, rng):
    """Eligible minutes to skip before the next start, Geometric(hazard).

    `hazard >= 1` means "start in the very next eligible minute". The campaign
    can never reach it -- `calibrate` refuses a hazard that is not a probability
    -- but the synthetic edge cases `G9.5` runs deliberately use 1.0, and a
    `math.log(0)` there would make the gate crash instead of score.
    """
    if hazard >= 1.0:
        return 0
    u = rng.random()
    return int(math.floor(math.log(1.0 - u) / math.log(1.0 - hazard)))


class ApplianceState(object):
    __slots__ = ("cycle_left", "delay_left", "elapsed", "cycles", "run_minutes")

    def __init__(self):
        self.cycle_left = 0
        self.delay_left = 0
        self.elapsed = 0
        self.cycles = 0
        self.run_minutes = 0


def simulate_day(app, state, hazard, elig, active, out, rng,
                 truncate_at_episode_end=False):
    """One dwelling-day for one appliance. Adds watt-deltas above standby.

    `out` is a 1440-long float list already carrying the standby baseline, so
    only `power - standby` is added here.
    """
    standby = app["standby_power_w"]
    profile = app["profile"]
    pauses = profile not in NO_PAUSE_PROFILES
    # PERTURBATION ONLY. `G9.5` asserts that a cycle started near the end of an
    # activity episode still runs to completion; this switch is the ONLY way to
    # make it stop, and the gate is worthless until it has been seen firing on it.
    elig_lookup = frozenset(elig) if truncate_at_episode_end else None
    elig_set = None
    t = 0
    ei = 0                       # index into `elig`
    while t < DAY_MINUTES:
        if state.cycle_left > 0:
            if pauses and not active[t]:
                t += 1           # CREST: the cycle waits for the occupant
                continue
            if elig_lookup is not None and profile < 6 and t not in elig_lookup:
                state.cycle_left = 0        # PERTURBATION ONLY: truncate
                state.delay_left = app["restart_delay_min"]
                t += 1
                continue
            state.elapsed += 1
            out[t] += cycle_power(app, state.elapsed) - standby
            state.cycle_left -= 1
            state.run_minutes += 1
            if state.cycle_left == 0:
                state.delay_left = app["restart_delay_min"]
            t += 1
            continue
        if state.delay_left > 0:
            state.delay_left -= 1
            t += 1
            continue
        # OFF and free to start: jump to the next eligible minute at or after t.
        if elig_set is None:
            elig_set = elig
        while ei < len(elig_set) and elig_set[ei] < t:
            ei += 1
        if ei >= len(elig_set):
            break                                # no eligible minute left today
        if hazard <= 0.0:
            break
        # Geometric skip over ELIGIBLE minutes -- exactly the per-minute
        # Bernoulli draw, without walking the minutes in between.
        skip = _geometric_skip(hazard, rng)
        ei += skip
        if ei >= len(elig_set):
            break
        t = elig_set[ei]
        state.cycle_left = cycle_length(app, rng)
        state.elapsed = 0
        state.cycles += 1
        ei += 1
    return out


def simulate_dhw_day(ev, hazard, elig, out, rng):
    """One dwelling-day for one DHW draw-off category. Adds litres per minute.

    Returns `(litres, n_events)` so the manifest can report the four-event mix
    that `G9.8` checks, rather than only the total that `G9.7` checks.
    """
    litres = 0.0
    events = 0
    if hazard <= 0.0 or not elig:
        return litres, events
    ei = 0
    while ei < len(elig):
        skip = _geometric_skip(hazard, rng)
        ei += skip
        if ei >= len(elig):
            break
        t = elig[ei]
        # Flow rate is spread around the mean with a Gaussian, as Table 1's
        # `sigma` column says, and discretised to the report's own 0.2 l/min.
        #
        # SIGMA IS READ IN UNITS OF THAT 0.2 l/min STEP, and that reading is a
        # decision (D-S9-2 item 6), not a transcription. Table 1 gives sigma = 2
        # for all four categories while category A's MEAN flow is 1 l/min: read
        # as 2 l/min, 31 % of category-A draws are negative, clipping biases the
        # mean upward and the model no longer reproduces Table 1's own derived
        # 200 l/day. Read as 2 steps = 0.4 l/min it reproduces them. The reading
        # that reproduces the source's own arithmetic is the one taken here.
        flow = rng.gauss(ev["flow_l_per_min"], ev["sigma"] * 0.2)
        flow = max(0.2, round(flow / 0.2) * 0.2)
        for k in range(ev["duration_min"]):
            if t + k < DAY_MINUTES:
                out[t + k] += flow
                litres += flow
        events += 1
        ei += 1
        while ei < len(elig) and elig[ei] < t + ev["duration_min"]:
            ei += 1
    return litres, events


# --------------------------------------------------------------------------
# the run
# --------------------------------------------------------------------------
def _import_step7(tools_dir):
    """Import the Step 7 schedule builder as a module.

    Deliberate: Step 9's dwellings, pool draws, chaining rule and calendar must
    be the SAME OBJECTS Step 8 simulated, or the loads would be injected into
    somebody else's occupancy. Re-implementing any of it here would produce a
    second parser and a second sampler, and the two would agree until they did
    not.
    """
    import importlib.util
    path = os.path.join(tools_dir, "4thJ_step7_schedules.py")
    spec = importlib.util.spec_from_file_location("step7_schedules", path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, tools_dir)
    spec.loader.exec_module(mod)
    return mod


def build_dwellings(root, fold, leg, year, seed, n_households, timestep_min,
                    verify_against_step8=True):
    """The 100 dwellings, their member-years, and their presence series."""
    s7 = _import_step7(os.path.join(root, "tools"))
    step2 = os.path.join(root, "Step2_docs", "outputs_step2")
    bitpos = s7.load_bit_positions(os.path.join(step2, "crosswalk_copresence.csv"))
    pool_path = os.path.join(root, "Step7_docs", "outputs_step7",
                             "generated_%s_%s_constrained.jsonl" % (leg, fold))
    pools, pool_meta = s7.load_pool(pool_path, step2, bitpos)
    cal = s7.year_day_types(year)
    rng = random.Random(seed)
    corpus = os.path.join(root, "Step3_docs", "outputs_step3",
                          "4J_step3_corpus.jsonl")
    households = s7.load_households(corpus, fold, n_households, rng, min_size=1)
    backoff = collections.Counter()

    out = []
    for hid, members in households:
        member_days = [s7.assemble_person_year(p, cal, "independent", rng, pools,
                                               backoff, 0.0)
                       for p in members]
        series = s7.household_year(member_days, timestep_min)
        out.append({"hid": hid, "members": member_days, "presence": series,
                    "n_members": len(members)})

    if verify_against_step8:
        shipped_dir = os.path.join(
            root, "Step7_docs", "outputs_step7", "schedules",
            "%s_%s_independent_seed1" % (leg, fold))
        _assert_same_dwellings(shipped_dir, fold, out)
    return out, pool_meta, s7


def _assert_same_dwellings(shipped_dir, fold, dwellings):
    """Refuse to run unless we rebuilt Step 8's dwellings EXACTLY.

    Not decoration. If the pool, the seed, the calendar or the draw order had
    drifted by one call, Step 9 would emit appliance loads for a different set of
    people and every downstream total would still reconcile. This is the only
    check that can see that.
    """
    if not os.path.isdir(shipped_dir):
        raise TriggerError(
            "cannot verify against Step 8: %s does not exist" % shipped_dir)
    n_checked = 0
    for d in dwellings:
        path = os.path.join(shipped_dir, "presence_HH_%s_%s.csv" % (fold, d["hid"]))
        if not os.path.exists(path):
            raise TriggerError(
                "Step 8 has no presence schedule for household %s. Step 9 is "
                "building a different set of dwellings from the one that was "
                "simulated." % d["hid"])
        ours = ["HH_%s_%s_Presence" % (fold, d["hid"])] + \
               ["%.6f" % v for v in d["presence"]]
        theirs = [ln.strip() for ln in
                  io.open(path, encoding="utf-8").read().splitlines() if ln.strip()]
        if ours != theirs:
            first = next((i for i, (a, b) in enumerate(zip(ours, theirs))
                          if a != b), min(len(ours), len(theirs)))
            raise TriggerError(
                "household %s does not reproduce Step 8's presence schedule; "
                "first difference at line %d (ours %r, shipped %r). Step 9 would "
                "be injecting loads into somebody else's occupancy."
                % (d["hid"], first,
                   ours[first] if first < len(ours) else "<short>",
                   theirs[first] if first < len(theirs) else "<short>"))
        n_checked += 1
    return n_checked


def sample_ownership(mapping, dwellings, rng, restrict_to_default_dwelling=True):
    """Which dwelling owns which appliance. CREST's `randomize()` behaviour.

    `restrict_to_default_dwelling` keeps only CREST's own default-dwelling set,
    which is what excludes electric space heating and electric water heating --
    the two groups that would double-count against Step 8's EnergyPlus heating
    and against item 9.3's DHW model. That exclusion is CREST'S OWN DEFAULT, not
    a judgement of ours. See D-S9-2 item 2.
    """
    owned = {}
    for d in dwellings:
        mine = []
        for app in mapping.appliances.values():
            if restrict_to_default_dwelling and not app["in_default_dwelling"]:
                continue
            if rng.random() < app["ownership_share"]:
                mine.append(app["id"])
        owned[d["hid"]] = mine
    return owned


# --------------------------------------------------------------------------
# pass 1 -- how many eligible minutes the stock actually supplies
# --------------------------------------------------------------------------
def count_eligible(dwellings, acl_to_profile, n_days):
    """Mean eligible minutes per dwelling-year, per CREST profile.

    Read off the diaries. This is the number CREST gets from a table of TUS
    statistics and we get from the corpus, and it is the ONLY thing the
    calibration below substitutes.
    """
    total = collections.Counter()
    for d in dwellings:
        for di in range(n_days):
            elig, _active = dwelling_day(d["members"], di, acl_to_profile)
            for p in range(7):
                total[p] += len(elig[p])
        total[7] += n_days * DAY_MINUTES
    n = float(len(dwellings))
    return dict((p, total[p] / n) for p in range(8))


def calibrate_all(mapping, mean_elig, dhw_scale_per_dwelling):
    """Start hazards for every appliance and every DHW category."""
    hazards = {}
    diag = {}
    for aid, app in mapping.appliances.items():
        elig = mean_elig.get(app["profile"], 0.0)
        h, m = calibrate(app, elig * 1.0, 1)
        hazards[aid] = h
        diag[aid] = {
            "name": app["name"], "profile": app["profile"],
            "mean_eligible_minutes_per_dwelling_year": round(m, 1),
            "cycles_per_year_target": app["cycles_per_year"],
            "hazard_per_eligible_minute": h,
        }
    dhw_haz = {}
    for did, ev in mapping.dhw.items():
        elig = mean_elig.get("dhw:" + did, 0.0)
        target = ev["inc_per_day"] * 365.0 * dhw_scale_per_dwelling
        if elig <= 0.0:
            dhw_haz[did] = 0.0
            diag["dhw:" + did] = {
                "name": ev["name"], "mean_eligible_minutes_per_dwelling_year": 0.0,
                "incidences_per_year_target": target,
                "hazard_per_eligible_minute": 0.0,
                "note": "the stock never performs this category's driver "
                        "activities, so the category never fires. Reported, not "
                        "floored.",
            }
            continue
        # A draw-off starts inside its driver episode and its remaining
        # `duration - 1` minutes are eligible minutes it consumes, so they are
        # subtracted in FULL rather than pro-rated over the year the way an
        # appliance cycle is: an appliance keeps running after the activity
        # stops, a tap does not. Expected eligible minutes per event are
        # `1/h + (duration - 1)`, so `h = target / (eligible - target*(d-1))`
        # reproduces Table 1's incidences/day exactly.
        unavailable = target * (ev["duration_min"] - 1)
        available = elig - unavailable
        if available <= 0.0:
            raise TriggerError(
                "DHW category %r cannot fit %d incidences of %d minutes into "
                "%.0f eligible minutes." % (ev["name"], int(target),
                                            ev["duration_min"], elig))
        h = target / available
        if h >= 1.0:
            raise TriggerError(
                "DHW category %r needs a hazard of %.4f per eligible minute, "
                "which is not a probability." % (ev["name"], h))
        dhw_haz[did] = h
        diag["dhw:" + did] = {
            "name": ev["name"],
            "mean_eligible_minutes_per_dwelling_year": round(elig, 1),
            "incidences_per_year_target": target,
            "hazard_per_eligible_minute": h,
        }
    return hazards, dhw_haz, diag


def count_eligible_dhw(dwellings, mapping, acl_to_profile, n_days):
    """Mean eligible minutes per dwelling-year for each DHW category.

    A DHW category is eligible in a minute when an ACTIVE occupant is doing one
    of the ACL codes the mapping names as its driver. THE DRIVER SET IS OURS --
    Jordan & Vajen place draw-offs by a probability function over the calendar,
    not by activity -- which is why every DHW row is labelled NOT VALIDATED.
    """
    total = collections.Counter()
    for d in dwellings:
        for di in range(n_days):
            for did, mins in dwelling_day_dhw(
                    d["members"], di, mapping.dhw_drivers).items():
                total["dhw:" + did] += len(mins)
    n = float(len(dwellings))
    return dict((k, v / n) for k, v in total.items())


# --------------------------------------------------------------------------
# pass 2 -- the campaign
# --------------------------------------------------------------------------
def to_timestep(minute_values, timestep_min):
    out = []
    for i in range(0, len(minute_values), timestep_min):
        chunk = minute_values[i:i + timestep_min]
        out.append(sum(chunk) / float(len(chunk)))
    return out


def measure_cycles(dwellings, mapping, owned, hazards, acl_to_profile, n_days,
                   seed):
    """Realised cycles per owning dwelling-year, appliances only.

    Cheap relative to a full run: no DHW, no timestep binning, no emission.
    Used by the calibration loop, which needs the COUNT and nothing else.
    """
    cycles = collections.Counter()
    owners = collections.Counter()
    for d in dwellings:
        rng = random.Random("s9cal|%d|%s" % (seed, d["hid"]))
        states = dict((aid, ApplianceState()) for aid in owned[d["hid"]])
        for aid in owned[d["hid"]]:
            owners[aid] += 1
        scratch = [0.0] * DAY_MINUTES
        for day_i in range(n_days):
            elig, active = dwelling_day(d["members"], day_i, acl_to_profile)
            for aid in owned[d["hid"]]:
                app = mapping.appliances[aid]
                simulate_day(app, states[aid], hazards[aid],
                             eligible_for(elig, app["profile"]), active,
                             scratch, rng)
        for aid in owned[d["hid"]]:
            cycles[aid] += states[aid].cycles
    return dict((aid, cycles[aid] / float(owners[aid]))
                for aid in owners if owners[aid])


def calibrate_to_published(dwellings, mapping, owned, hazards, acl_to_profile,
                           n_days, seed, tol=0.02, max_passes=6):
    """Scale each appliance's hazard until the STOCK MEAN cycles per year meets
    CREST's published `Cycles per year (n)`.

    🔴 WHY THIS LOOP EXISTS, MEASURED RATHER THAN ASSUMED. The closed-form
    calibration subtracts the minutes an appliance is busy PRO-RATED over the
    year, which is what CREST does. That is right when the activity probability
    is a small population share, and WRONG here: our eligibility indicator is
    0/1 and an appliance whose cycle coincides with the activity that triggers
    it -- a television during television-watching, a hob during cooking -- is
    busy through most of its OWN eligible minutes, not a year-averaged sample of
    them. The first campaign under the closed form delivered ratios of 0.46 to
    0.54 against the published cycles for exactly those appliances.

    Iterating to hit the published annual target is CREST's OWN procedure: the
    reference implementation bisects a `calibration_factor` against an annual
    consumption target for the same reason. The published cycles-per-year is the
    reference and it is never adjusted; only our hazard is.

    Returns `(hazards, trace)`. The trace is kept and written into the manifest,
    so a reader can see how far the closed form was off and in which direction.
    """
    hz = dict(hazards)
    trace = []
    prev = {}
    saturated = set()
    for p in range(max_passes):
        got = measure_cycles(dwellings, mapping, owned, hz, acl_to_profile,
                             n_days, seed)
        worst = 0.0
        worst_id = None
        step = {}
        for aid, mean_cycles in got.items():
            target = mapping.appliances[aid]["cycles_per_year"]
            # CREST carries three standby-only devices at 1e-05 cycles per
            # year -- an answering machine, a cordless telephone and a clock.
            # They are a standby wattage with no cycle, so "within range of the
            # published count" is not a question that can be asked of them.
            # Excluded from convergence, and reported by the gate as
            # NOT_EVALUABLE rather than as a pass or a failure.
            if target < 0.5:
                continue
            ratio = mean_cycles / target
            step[aid] = round(ratio, 4)
            if aid in saturated:
                continue
            # An appliance whose ratio stops responding to a larger hazard has
            # run out of eligible minutes: raising the hazard cannot buy cycles
            # that the corpus has no activity time for. Detected rather than
            # iterated against, so the loop reports a measurement instead of
            # spinning six times on a wall.
            if aid in prev and ratio > 0.0:
                if abs(ratio - prev[aid]) < 0.01 and ratio < 1.0 - tol:
                    saturated.add(aid)
                    continue
            prev[aid] = ratio
            if abs(ratio - 1.0) > worst:
                worst = abs(ratio - 1.0)
                worst_id = aid
            if ratio > 0.0 and hz.get(aid, 0.0) > 0.0:
                hz[aid] = min(0.999, hz[aid] / ratio)
        trace.append({"pass": p, "worst_abs_dev": round(worst, 4),
                      "worst_appliance": worst_id, "ratios": step,
                      "saturated": sorted(saturated)})
        if worst <= tol:
            break
    return hz, trace


def run_fold(root, fold, leg, year, seed, n_households, timestep_min, out_dir,
             dhw_l_per_day, restrict_default_dwelling=True,
             truncate_cycle_at_episode_end=False, drop_end_use=None,
             double_trigger_appliance=None, dhw_scale=1.0,
             collapse_dhw_events=False, extra_runtime_columns=(),
             force_two_digit_mapping=False, zero_load_share=0.0,
             verify_against_step8=True, map_path=None, calibration_passes=6):
    """One fold, end to end. Every keyword after `dhw_l_per_day` exists ONLY so
    the registered perturbation battery has something to perturb; all of them
    default to the correct behaviour and any non-default is stamped into the
    manifest so a perturbed run can never be mistaken for a campaign run."""
    if map_path is None:
        map_path = os.path.join(root, "Step9_docs", "outputs_step9",
                                "activity_appliance_map.csv")
    mapping = Mapping(map_path)
    acl_to_profile = dict(mapping.acl_to_profile)
    if force_two_digit_mapping:
        # PERTURBATION ONLY (G9.11's falsifier): collapse the join to two digits.
        acl_to_profile = dict((c[:2] + "0", p) for c, p in acl_to_profile.items())

    dwellings, pool_meta, _s7 = build_dwellings(
        root, fold, leg, year, seed, n_households, timestep_min,
        verify_against_step8=verify_against_step8)
    n_days = len(dwellings[0]["members"][0])

    own_rng = random.Random(seed * 7919 + 13)
    owned = sample_ownership(mapping, dwellings, own_rng,
                             restrict_to_default_dwelling=restrict_default_dwelling)

    mean_elig = count_eligible(dwellings, acl_to_profile, n_days)
    mean_elig.update(count_eligible_dhw(dwellings, mapping, acl_to_profile, n_days))
    hazards, dhw_haz, calib = calibrate_all(
        mapping, mean_elig, dhw_l_per_day * dhw_scale / 200.0)
    calib_trace = []
    if calibration_passes:
        hazards, calib_trace = calibrate_to_published(
            dwellings, mapping, owned, hazards, acl_to_profile, n_days, seed,
            max_passes=calibration_passes)
        for aid, h in hazards.items():
            calib[aid]["hazard_per_eligible_minute_calibrated"] = h
    if double_trigger_appliance:
        # PERTURBATION ONLY (G9.6's falsifier).
        if double_trigger_appliance not in hazards:
            raise TriggerError("no appliance %r to perturb"
                               % double_trigger_appliance)
        hazards[double_trigger_appliance] = min(
            0.999, hazards[double_trigger_appliance] * 2.0)

    n_ts_per_day = DAY_MINUTES // timestep_min
    per_dwelling = []
    stock_elec = [0.0] * (n_days * n_ts_per_day)
    stock_dhw = [0.0] * (n_days * n_ts_per_day)
    zero_after = int(round(len(dwellings) * (1.0 - zero_load_share)))

    for di_d, d in enumerate(dwellings):
        rng = random.Random("s9|%d|%s" % (seed, d["hid"]))
        states = dict((aid, ApplianceState()) for aid in owned[d["hid"]])
        standby = sum(mapping.appliances[aid]["standby_power_w"]
                      for aid in owned[d["hid"]])
        elec_ts = []
        dhw_ts = []
        by_appliance = collections.Counter()
        cycles = collections.Counter()
        dhw_litres = collections.Counter()
        dhw_events = collections.Counter()
        for day_i in range(n_days):
            elig, active = dwelling_day(d["members"], day_i, acl_to_profile)
            dhw_elig = dwelling_day_dhw(d["members"], day_i, mapping.dhw_drivers)
            minute = [standby] * DAY_MINUTES
            for aid in owned[d["hid"]]:
                app = mapping.appliances[aid]
                before = states[aid].run_minutes
                simulate_day(app, states[aid], hazards[aid],
                             eligible_for(elig, app["profile"]), active, minute,
                             rng,
                             truncate_at_episode_end=truncate_cycle_at_episode_end)
                by_appliance[aid] += states[aid].run_minutes - before
            water = [0.0] * DAY_MINUTES
            day_litres = {}
            for did, ev in mapping.dhw.items():
                if collapse_dhw_events and did != "dhw_cat_a":
                    continue          # PERTURBATION ONLY (G9.8's falsifier)
                lit, nev = simulate_dhw_day(ev, dhw_haz[did],
                                            dhw_elig.get(did, []), water, rng)
                day_litres[did] = (lit, nev)
            if drop_end_use == "dhw":
                water = [0.0] * DAY_MINUTES      # PERTURBATION ONLY (G9.10)
                day_litres = {}
            if di_d >= zero_after:
                minute = [0.0] * DAY_MINUTES     # PERTURBATION ONLY (G9.12)
                water = [0.0] * DAY_MINUTES
                day_litres = {}
            elec_ts.extend(to_timestep(minute, timestep_min))
            dhw_ts.extend(to_timestep(water, timestep_min))
            for did, (lit, nev) in day_litres.items():
                dhw_litres[did] += lit
                dhw_events[did] += nev
            dhw_litres["total"] += sum(v for v, _ in day_litres.values())
        for aid in owned[d["hid"]]:
            cycles[aid] = states[aid].cycles
        for i, v in enumerate(elec_ts):
            stock_elec[i] += v
        for i, v in enumerate(dhw_ts):
            stock_dhw[i] += v
        per_dwelling.append({
            "hid": d["hid"], "n_members": d["n_members"],
            "appliances": owned[d["hid"]],
            "cycles": dict(cycles),
            "run_minutes": dict(by_appliance),
            "elec_kwh": sum(elec_ts) * timestep_min / 60.0 / 1000.0,
            "dhw_litres": dhw_litres["total"],
            "dhw_litres_by_category": dict(
                (k, v) for k, v in dhw_litres.items() if k != "total"),
            "dhw_events_by_category": dict(dhw_events),
            "elec_ts": elec_ts, "dhw_ts": dhw_ts,
        })

    manifest = write_outputs(root, fold, out_dir, mapping, per_dwelling,
                             stock_elec, stock_dhw, calib, timestep_min, year,
                             seed, leg, pool_meta, mean_elig,
                             dhw_l_per_day, restrict_default_dwelling,
                             extra_runtime_columns, calib_trace, {
                                 "truncate_cycle_at_episode_end":
                                     truncate_cycle_at_episode_end,
                                 "drop_end_use": drop_end_use,
                                 "double_trigger_appliance":
                                     double_trigger_appliance,
                                 "dhw_scale": dhw_scale,
                                 "collapse_dhw_events": collapse_dhw_events,
                                 "force_two_digit_mapping": force_two_digit_mapping,
                                 "zero_load_share": zero_load_share,
                                 "restrict_default_dwelling":
                                     restrict_default_dwelling,
                             })
    return manifest


# --------------------------------------------------------------------------
# emission -- work item 9.4
# --------------------------------------------------------------------------
WATER_DENSITY_KG_L = 1.0
SPECIFIC_HEAT_WH_KG_K = 1.16          # Jordan & Vajen's own worked example


def idf_objects(hid, fold, elec_csv, dhw_csv, n_values, timestep_min,
                peak_flow_m3_s, elec_design_w):
    """`Schedule:File` + `ElectricEquipment` + `WaterUse:Equipment` for one
    dwelling, written so `G9.9` has an ASSIGNMENT to re-read.

    The schedule NAME is embedded in the equipment object, and the equipment
    object names the schedule it was built with, so re-opening the saved IDF and
    comparing the two is a real check. In 3J a value-only check missed a x3.028
    draw increase across 56 cells because the object had been re-pointed at a
    different schedule and its own numbers never moved.
    """
    name = "HH_%s_%s" % (fold, hid)
    hours = int(round(n_values * timestep_min / 60.0))
    out = []
    out.append(
        "Schedule:File,\n"
        "  %s_Appliance,            !- Name\n"
        "  Fraction,                !- Schedule Type Limits Name\n"
        "  %s,                      !- File Name\n"
        "  1,                       !- Column Number\n"
        "  1,                       !- Rows to Skip at Top\n"
        "  %d,                      !- Number of Hours of Data\n"
        "  Comma,                   !- Column Separator\n"
        "  No,                      !- Interpolate to Timestep\n"
        "  %d;                      !- Minutes per Item\n"
        % (name, elec_csv, hours, timestep_min))
    out.append(
        "Schedule:File,\n"
        "  %s_DHW,                  !- Name\n"
        "  Fraction,                !- Schedule Type Limits Name\n"
        "  %s,                      !- File Name\n"
        "  1,                       !- Column Number\n"
        "  1,                       !- Rows to Skip at Top\n"
        "  %d,                      !- Number of Hours of Data\n"
        "  Comma,                   !- Column Separator\n"
        "  No,                      !- Interpolate to Timestep\n"
        "  %d;                      !- Minutes per Item\n"
        % (name, dhw_csv, hours, timestep_min))
    out.append(
        "ElectricEquipment,\n"
        "  %s_Appliances,           !- Name\n"
        "  %s_Zone,                 !- Zone or ZoneList Name\n"
        "  %s_Appliance,            !- Schedule Name\n"
        "  EquipmentLevel,          !- Design Level Calculation Method\n"
        "  %.4f,                    !- Design Level {W}\n"
        "  ,                        !- Watts per Zone Floor Area\n"
        "  ,                        !- Watts per Person\n"
        "  0.0,                     !- Fraction Latent\n"
        "  1.0,                     !- Fraction Radiant\n"
        "  0.0;                     !- Fraction Lost\n"
        % (name, name, name, elec_design_w))
    out.append(
        "WaterUse:Equipment,\n"
        "  %s_DHW,                  !- Name\n"
        "  DomesticHotWater,        !- End-Use Subcategory\n"
        "  %.10f,                   !- Peak Flow Rate {m3/s}\n"
        "  %s_DHW,                  !- Flow Rate Fraction Schedule Name\n"
        "  %s_DHW_Target,           !- Target Temperature Schedule Name\n"
        "  %s_DHW_Hot,              !- Hot Water Supply Temperature Schedule\n"
        "  %s_DHW_Cold;             !- Cold Water Supply Temperature Schedule\n"
        % (name, peak_flow_m3_s, name, name, name, name))
    return "".join(out)


def write_series_csv(path, header, values):
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow([header])
        for v in values:
            w.writerow(["%.6f" % v])


def write_outputs(root, fold, out_dir, mapping, per_dwelling, stock_elec,
                  stock_dhw, calib, timestep_min, year, seed, leg, pool_meta,
                  mean_elig, dhw_l_per_day, restrict_default_dwelling,
                  extra_runtime_columns, calib_trace, perturbations):
    prof_dir = os.path.join(out_dir, "enduse_profiles", fold)
    if not os.path.isdir(prof_dir):
        os.makedirs(prof_dir)
    idf = []
    rows = []
    for d in per_dwelling:
        name = "HH_%s_%s" % (fold, d["hid"])
        peak_w = max(d["elec_ts"]) if d["elec_ts"] else 0.0
        peak_lpm = max(d["dhw_ts"]) if d["dhw_ts"] else 0.0
        elec_frac = [v / peak_w if peak_w else 0.0 for v in d["elec_ts"]]
        dhw_frac = [v / peak_lpm if peak_lpm else 0.0 for v in d["dhw_ts"]]
        elec_csv = "elec_%s.csv" % name
        dhw_csv = "dhw_%s.csv" % name
        write_series_csv(os.path.join(prof_dir, elec_csv),
                         name + "_ApplianceFraction", elec_frac)
        write_series_csv(os.path.join(prof_dir, dhw_csv),
                         name + "_DHWFraction", dhw_frac)
        idf.append(idf_objects(d["hid"], fold, elec_csv, dhw_csv,
                               len(elec_frac), timestep_min,
                               peak_lpm / 1000.0 / 60.0, peak_w))
        rows.append({
            "hid": d["hid"], "n_members": d["n_members"],
            "n_appliances": len(d["appliances"]),
            "elec_kwh_per_year": round(d["elec_kwh"], 3),
            "elec_peak_w": round(peak_w, 3),
            "dhw_litres_per_year": round(d["dhw_litres"], 1),
            "dhw_litres_per_day": round(d["dhw_litres"] / 365.0, 3),
            "dhw_litres_per_person_per_day": round(
                d["dhw_litres"] / 365.0 / d["n_members"], 3),
            "dhw_peak_l_per_min": round(peak_lpm, 3),
        })

    idf_path = os.path.join(out_dir, "step9_objects_%s.idf" % fold)
    with io.open(idf_path, "w", encoding="utf-8", newline="") as fh:
        fh.write("! 4J Step 9 -- activity-driven end-use loads, fold %s\n"
                 "! leg=%s year=%d seed=%d timestep=%dmin rule=independent\n"
                 "! map md5 %s\n\n"
                 % (fold, leg, year, seed, timestep_min, mapping.md5))
        fh.write("\n".join(idf))

    summ_path = os.path.join(out_dir, "enduse_by_dwelling_%s.csv" % fold)
    with io.open(summ_path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()),
                           lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    stock_path = os.path.join(out_dir, "stock_series_%s.csv" % fold)
    with io.open(stock_path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["timestep", "electricity_w", "dhw_l_per_min"])
        for i, (e, h) in enumerate(zip(stock_elec, stock_dhw)):
            w.writerow([i, "%.6f" % e, "%.6f" % h])

    cycles = collections.Counter()
    owners = collections.Counter()
    for d in per_dwelling:
        for aid in d["appliances"]:
            owners[aid] += 1
            cycles[aid] += d["cycles"].get(aid, 0)
    cycle_table = []
    for aid, app in mapping.appliances.items():
        if not owners[aid]:
            continue
        cycle_table.append({
            "appliance_id": aid, "appliance_name": app["name"],
            "crest_profile": app["profile"],
            "n_dwellings_owning": owners[aid],
            "cycles_per_dwelling_year_modelled":
                round(cycles[aid] / float(owners[aid]), 3),
            "cycles_per_year_published": app["cycles_per_year"],
            "ratio_modelled_over_published":
                round(cycles[aid] / float(owners[aid])
                      / app["cycles_per_year"], 5)
            if app["cycles_per_year"] else "",
        })
    cyc_path = os.path.join(out_dir, "cycles_%s.csv" % fold)
    with io.open(cyc_path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(cycle_table[0].keys()),
                           lineterminator="\n")
        w.writeheader()
        w.writerows(cycle_table)

    dhw_by_cat = collections.Counter()
    ev_by_cat = collections.Counter()
    for d in per_dwelling:
        for k, v in d.get("dhw_litres_by_category", {}).items():
            dhw_by_cat[k] += v
        for k, v in d.get("dhw_events_by_category", {}).items():
            ev_by_cat[k] += v

    clean = (not perturbations["truncate_cycle_at_episode_end"]
             and not perturbations["collapse_dhw_events"]
             and not perturbations["force_two_digit_mapping"]
             and perturbations["drop_end_use"] is None
             and perturbations["double_trigger_appliance"] is None
             and perturbations["zero_load_share"] == 0.0
             and perturbations["dhw_scale"] == 1.0
             and perturbations["restrict_default_dwelling"])

    manifest = {
        "fold": fold, "leg": leg, "year": year, "seed": seed,
        "rule": "independent",
        "timestep_min": timestep_min,
        "n_dwellings": len(per_dwelling),
        "n_people": sum(d["n_members"] for d in per_dwelling),
        "map_md5": mapping.md5,
        "pool": pool_meta,
        "restrict_to_crest_default_dwelling": restrict_default_dwelling,
        "dhw_reference_l_per_dwelling_day": dhw_l_per_day,
        "dhw_delta_t_k": 35.0,
        "runtime_input_columns": sorted(
            set(mapping.runtime_input_columns()) | set(extra_runtime_columns)),
        "mean_eligible_minutes_per_dwelling_year": dict(
            (str(k), round(v, 1)) for k, v in mean_elig.items()),
        "calibration": calib,
        "calibration_trace": calib_trace,
        "cycles": cycle_table,
        "dhw_litres_by_category": dict(dhw_by_cat),
        "dhw_events_by_category": dict(ev_by_cat),
        "stock_elec_kwh_per_dwelling_year": round(
            sum(stock_elec) * timestep_min / 60.0 / 1000.0 / len(per_dwelling), 3),
        # `stock_dhw` carries the MEAN l/min over each timestep, so litres are
        # `sum * timestep_min`, not `sum`. Caught by comparing the total against
        # Jordan & Vajen's own 200 l/day reference, which is exactly the kind of
        # check a units error survives when nobody makes it.
        "stock_dhw_l_per_dwelling_day": round(
            sum(stock_dhw) * timestep_min / 365.0 / len(per_dwelling), 3),
        "stock_dhw_l_per_person_day": round(
            sum(stock_dhw) * timestep_min / 365.0
            / sum(d["n_members"] for d in per_dwelling), 3),
        "perturbations": perturbations,
        "is_campaign_run": clean,
        "artefacts": {
            "idf": os.path.basename(idf_path),
            "by_dwelling": os.path.basename(summ_path),
            "stock_series": os.path.basename(stock_path),
            "cycles": os.path.basename(cyc_path),
            "profiles_dir": os.path.relpath(prof_dir, out_dir).replace("\\", "/"),
        },
    }
    man_path = os.path.join(out_dir, "step9_manifest_%s.json" % fold)
    io.open(man_path, "w", encoding="utf-8", newline="").write(
        json.dumps(manifest, indent=2, sort_keys=True))
    return manifest


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--fold", required=True)
    ap.add_argument("--leg", default="leg5")
    ap.add_argument("--year", type=int, default=2017)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--households", type=int, default=100)
    ap.add_argument("--timestep", type=int, default=60)
    ap.add_argument("--out", default=None)
    ap.add_argument("--dhw-l-per-day", type=float, default=200.0,
                    help="Jordan & Vajen's single-family-house reference. NOT "
                         "scaled by household size: that scaling is not in the "
                         "report and would be ours. See D-S9-2 item 5.")
    args = ap.parse_args(argv)
    out = args.out or os.path.join(args.root, "Step9_docs", "outputs_step9")
    m = run_fold(args.root, args.fold, args.leg, args.year, args.seed,
                 args.households, args.timestep, out, args.dhw_l_per_day)
    print("fold                       %s" % m["fold"])
    print("dwellings / people         %d / %d" % (m["n_dwellings"], m["n_people"]))
    print("electricity kWh/dwelling.y %.1f" % m["stock_elec_kwh_per_dwelling_year"])
    print("DHW l/dwelling.day         %.2f" % m["stock_dhw_l_per_dwelling_day"])
    print("DHW l/person.day           %.2f" % m["stock_dhw_l_per_person_day"])
    print("campaign run               %s" % m["is_campaign_run"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
