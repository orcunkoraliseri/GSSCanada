# -*- coding: utf-8 -*-
"""
4J / STEP 6, `G6.8` -- JOINT-STRUCTURE CHECKERS (dwell time, transitions, TVD).

🔴 NOTHING HERE IS A NEW GATE. `G6.8` is registered in our own pre-registered
spec, `Step6_docs/4thJ_06_transfer_val.md:44`:

    "Score quantities NEVER IN THE PROMPT: co-presence cross-tabs, transition
     entropy, dwell-time distributions conditioned on ATTRIBUTE PAIRS. All must
     clear their Tier 1 and Tier 2 thresholds on the held-out country."

and every threshold it inherits is already in the Overview's Tier 1 table:

    dwell-time distribution, Wasserstein-1 per activity   <= 10.0 min
    transitions per day, absolute error                   <= 1.50
    transition-matrix TVD                                 <= 0.050
    diurnal marginal divergence, JSD base-2      mean <= 0.015, max <= 0.025
    activity time budget error, min/day       <= 15.0 stratum, <= 8.0 population

**Only the checker was missing** (`grep` of `tools/` found no dwell-time or
transition implementation). This file is that checker and nothing more: it
designs no quantity, moves no band, and touches no other gate.

WHY THE MARGINAL ARM IS IN HERE TOO
===================================
`G6.8` exists to answer "it just echoes the marginals". That claim is only
refuted if the marginals are shown to be matched WHILE the joints are scored --
otherwise a candidate that fails everything would look like it passed `G6.8`'s
point. So the marginal arm (time budgets, diurnal JSD) is computed alongside and
reported, and the registered shuffled-diary control is the proof the two arms
are separable: it must PASS the marginal arm and FAIL the sequence arm.

🔴 WHAT IS AN ASSUMPTION HERE, RECORDED RATHER THAN BURIED
==========================================================
1. `MIN_CELL_N` = 100 diaries per conditioning cell. No document registers a
   minimum cell size for `G6.8`. 100 is taken from `G4_1_MIN_STRATUM_N`, the one
   precedent this project has already set for "too small to score". It is a
   SCORING PARAMETER, not a threshold: it decides what is scorable, never where
   the line is.
2. Transition-matrix TVD is computed on the JOINT distribution of (from, to)
   Level-1 pairs, pooled over diaries. The Tier 1 row names "transition-matrix
   TVD" without fixing joint-vs-row-normalised; the joint is bounded in [0, 1]
   without a per-row sample-size guard, so it is the one that can carry a fixed
   0.050 band honestly.
3. Level-1 activity = the FIRST DIGIT of the three-digit code, the 10 HETUS
   Level-1 categories the Overview's Tier 1 row counts.
4. 🟢 DIARY WEIGHTS. `D-S6-4` was RULED 2026-08-21: Step 6 scores on
   `weight_dia_cal` (the calendar-week re-basing, `FINDING 53`), with
   `weight_dia` available beside it as a DECLARED SENSITIVITY and never mixed
   into the headline. `--weight-field` now defaults to `weight_dia_cal` and is
   implemented; `--weight-field none` reproduces the old unweighted statistic
   exactly, which is what the selftest checks. Weights re-weight every
   DISTRIBUTION and no COUNT: `MIN_CELL_N` and `MIN_DWELL_N` stay unweighted.

Usage
-----
  # score a candidate file against a reference file
  py -3 tools/4thJ_step6_g68_joint.py --ref real.jsonl --cand gen.jsonl

  # the registered negative controls, built from the real corpus itself
  py -3 tools/4thJ_step6_g68_joint.py --corpus <corpus.jsonl> --country it \\
      --control shuffled_across
"""

import io
import os
import sys
import json
import math
import random
import argparse
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# ---------------------------------------------------------------------------
# REGISTERED THRESHOLDS -- copied from the Overview's Tier 1 table, which is the
# single source. They are repeated here as named constants so a reader can see
# what is being compared to what; they are NOT re-derived and NOT tuned.
# ---------------------------------------------------------------------------
G68_DWELL_W1_MAX_MIN = 10.0        # Tier 1, project-chosen (= one slot width)
G68_TRANSITIONS_MAX_ABS_ERR = 1.50  # Tier 1, project-chosen
G68_TRANSITION_TVD_MAX = 0.050      # Tier 1, project-chosen
G68_DIURNAL_JSD_MEAN_MAX = 0.015    # Tier 1, bits, base-2
G68_DIURNAL_JSD_MAX_MAX = 0.025     # Tier 1, bits, base-2
G68_BUDGET_MAX_MIN_STRATUM = 15.0   # Tier 1, min/day, per stratum
G68_BUDGET_MAX_MIN_POP = 8.0        # Tier 1, min/day, population

MIN_CELL_N = 100                    # ASSUMPTION 1 above
MIN_DWELL_N = 30                    # too few episodes to shape a distribution
SLOT_MINUTES = 10
N_SLOTS = 1440 // SLOT_MINUTES

PREFIX_BODY_SEP = "|"
PREFIX_FIELDS = ["country", "strat_age_band", "strat_sex", "strat_hh_type",
                 "strat_econ_status", "strat_day_type"]
EOR = "<eor>"

# The attribute PAIRS `G6.8` conditions on. Country is not one of them: on a
# LOCO fold every scored diary is the held-out country, so it is constant.
ATTRIBUTE_PAIRS = [("strat_age_band", "strat_sex"),
                   ("strat_age_band", "strat_day_type"),
                   ("strat_sex", "strat_econ_status"),
                   ("strat_hh_type", "strat_day_type")]


# ---------------------------------------------------------------------------
# parsing -- re-implemented rather than imported, for the reason the shard
# builder gives: a detector that shares a parser with the thing it audits
# cannot disagree with it.
# ---------------------------------------------------------------------------

def split_prefix_body(text):
    i = text.find(PREFIX_BODY_SEP)
    if i < 0:
        raise ValueError("no prefix separator")
    return text[:i], text[i + 1:]


def parse_record(text):
    """-> (prefix dict, [(dur, act, act2, loc, cop), ...]) or None."""
    try:
        pref, body = split_prefix_body(text)
    except ValueError:
        return None
    fields = pref.split(",")
    if len(fields) != len(PREFIX_FIELDS):
        return None
    d = dict(zip(PREFIX_FIELDS, fields))
    body = body.replace(EOR, "")
    eps = []
    for chunk in body.split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        parts = chunk.split(",")
        if len(parts) != 5:
            return None
        try:
            dur = int(parts[0])
        except ValueError:
            return None
        if dur <= 0:
            return None
        eps.append((dur, parts[1], parts[2], parts[3], parts[4]))
    if not eps:
        return None
    return d, eps


def level1(act):
    return act[0] if act else "?"


# --------------------------------------------------------------------------
# D-S6-4 -- DIARY WEIGHTS. RULED BY THE AUTHOR 2026-08-21.
#
# Step 6 scores on `weight_dia_cal`, the calendar-week re-based diary weight
# (`FINDING 53`), with `weight_dia` reported beside it as a DECLARED SENSITIVITY
# and never mixed into the headline number.
#
# WHY THE WEIGHT HAS TO BE JOINED IN RATHER THAN READ OFF THE CORPUS
# ------------------------------------------------------------------
# \U0001f534 `4J_step3_corpus.jsonl` carries NO weight column at all -- its
# records are `country, hid, pid, diary_day, split, text` and nothing else. The
# weights live in `harmonised.parquet`, one row per EPISODE, so they are joined
# on the diary key `(country upper-cased, pid, diary_day as a string)`, which is
# unique at 73,254 rows -- exactly the corpus size.
#
# WHAT THE WEIGHT DOES AND DOES NOT TOUCH
# ---------------------------------------
# It re-weights every DISTRIBUTION: dwell ECDFs, the transition joint,
# transitions per day, time budgets, the diurnal profile, co-presence. It does
# NOT touch any COUNT: `MIN_CELL_N` and `MIN_DWELL_N` still read the unweighted
# number of diaries and episodes, because sample size decides what is scorable
# and weight decides what it represents. A cell of three diaries carrying a
# large weight is still three diaries and is still skipped.
#
# \u26aa Weight scale is irrelevant and is not normalised: every statistic here
# is a weighted mean or a normalised distribution, and `G6.8` is always scored
# WITHIN one country. (The scales differ by orders of magnitude between
# countries -- ES mean 8490, IT 4255, UK 1.004 -- which is exactly why nothing
# in this module ever pools two countries' weights.)
# --------------------------------------------------------------------------

WEIGHT_FIELDS = ("weight_dia_cal", "weight_dia")
DEFAULT_WEIGHT_FIELD = "weight_dia_cal"          # D-S6-4, ruled
HARMONISED_DEFAULT = os.path.join("Step2_docs", "outputs_step2",
                                  "harmonised.parquet")


def load_weights(field, parquet=None):
    """-> {(COUNTRY, pid, diary_day): weight}. Raises rather than guessing."""
    if field not in WEIGHT_FIELDS:
        raise SystemExit("!!! unknown weight field %r; D-S6-4 ruled on %s"
                         % (field, " and ".join(WEIGHT_FIELDS)))
    try:
        import pandas as pd
    except ImportError:
        raise SystemExit("!!! --weight-field needs pandas to read %s"
                         % (parquet or HARMONISED_DEFAULT))
    path = parquet or HARMONISED_DEFAULT
    if not os.path.exists(path):
        raise SystemExit("!!! no harmonised parquet at %s -- pass --harmonised"
                         % path)
    df = pd.read_parquet(path, columns=["country", "pid", "diary_day", field])
    df = df.drop_duplicates(["country", "pid", "diary_day"])
    w = {}
    n_null = 0
    for c, pid, dd, v in zip(df["country"], df["pid"], df["diary_day"],
                             df[field]):
        if v != v or v is None:
            n_null += 1
            continue
        w[(str(c).upper(), str(pid), str(dd))] = float(v)
    return w, n_null


def load(path, country=None, limit=None, weights=None):
    """-> [(prefix dict, episodes, weight)].

    `weights` is None for the unweighted default, in which case every record
    carries 1.0 and every statistic reduces exactly to its unweighted form. A
    record the weight table does not key -- a GENERATED diary has no `pid` --
    is returned with weight `None` in the third slot ONLY transiently; the
    caller resolves it, and the count of unmatched records is reported by
    `load_report` so a silent fallback to 1.0 can never happen unseen.
    """
    out = []
    unmatched = 0
    dropped_null = 0
    with io.open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if country and r.get("country") != country:
                continue
            p = parse_record(r["text"])
            if p is None:
                continue
            if weights is None:
                w = 1.0
            else:
                key = (str(r.get("country", "")).upper(),
                       str(r.get("pid", "")), str(r.get("diary_day", "")))
                w = weights.get(key)
                if w is None:
                    if r.get("pid"):
                        # keyed but absent from the weight table: the diary has
                        # no weight on this basis. It is DROPPED, not silently
                        # promoted to 1.0 among numbers in the thousands.
                        dropped_null += 1
                        continue
                    unmatched += 1
                    w = 1.0
            out.append((p[0], p[1], w))
            if limit and len(out) >= limit:
                break
    load.last = {"path": path, "n": len(out), "unmatched_no_pid": unmatched,
                 "dropped_unweighted": dropped_null,
                 "weighted": weights is not None}
    return out


# ---------------------------------------------------------------------------
# the statistics
# ---------------------------------------------------------------------------

def dwell_times(recs):
    """Level-1 activity -> list of (episode duration in minutes, diary weight).

    D-S6-4: the weight rides on the SAMPLE, not on the count. Under the
    unweighted default every weight is 1.0 and the pairs reduce to the old
    list exactly."""
    d = collections.defaultdict(list)
    for r in recs:
        w = r[2]
        for e in r[1]:
            d[level1(e[1])].append((float(e[0]), w))
    return d


def wasserstein1(a, b):
    """W1 between two 1-D empirical distributions, in the samples' own units.

    Each sample is a list of (value, weight) pairs. D-S6-4: the ECDF is the
    WEIGHTED one; with every weight 1.0 it is identical to the unweighted ECDF,
    and the selftest proves that rather than asserting it.

    W1 = integral |F_a(x) - F_b(x)| dx, computed exactly on the merged support.
    No binning, no kernel: a binned W1 would inherit the bin width as a floor
    and the threshold is one slot width (10 min), which is the same order.
    """
    if not a or not b:
        return float("nan")
    # Accept a bare list of values as well as (value, weight) pairs: the unit
    # checks in the selftest call this directly with plain numbers, and a W1
    # that changed meaning depending on who called it would be worse than the
    # two lines it costs to accept both.
    a = [(float(x), 1.0) if not isinstance(x, tuple) else x for x in a]
    b = [(float(x), 1.0) if not isinstance(x, tuple) else x for x in b]
    a = sorted(a)
    b = sorted(b)
    xs = sorted(set(x for x, _ in a) | set(x for x, _ in b))
    na = float(sum(w for _, w in a))
    nb = float(sum(w for _, w in b))
    if na <= 0 or nb <= 0:
        return float("nan")
    ia = ib = 0
    ca = cb = 0.0
    total = 0.0
    for i in range(len(xs) - 1):
        x = xs[i]
        while ia < len(a) and a[ia][0] <= x:
            ca += a[ia][1]
            ia += 1
        while ib < len(b) and b[ib][0] <= x:
            cb += b[ib][1]
            ib += 1
        total += abs(ca / na - cb / nb) * (xs[i + 1] - x)
    return total


def transitions_per_day(recs):
    """Mean number of Level-1 activity CHANGES per diary."""
    if not recs:
        return float("nan")
    tot = 0.0
    den = 0.0
    for r in recs:
        seq = [level1(e[1]) for e in r[1]]
        tot += r[2] * sum(1 for i in range(1, len(seq)) if seq[i] != seq[i - 1])
        den += r[2]
    if den <= 0:
        return float("nan")
    return tot / den


def transition_dist(recs):
    """Joint distribution over (from, to) Level-1 pairs, changes only."""
    c = collections.Counter()
    for r in recs:
        seq = [level1(e[1]) for e in r[1]]
        for i in range(1, len(seq)):
            if seq[i] != seq[i - 1]:
                c[(seq[i - 1], seq[i])] += r[2]
    tot = float(sum(c.values()))
    if tot == 0:
        return {}
    return dict((k, v / tot) for k, v in c.items())


def tvd(pa, pb):
    keys = set(pa) | set(pb)
    return 0.5 * sum(abs(pa.get(k, 0.0) - pb.get(k, 0.0)) for k in keys)


def transition_entropy_bits(p):
    """Reported, not thresholded -- `G6.8` names it, Tier 1 sets no band."""
    return -sum(v * math.log(v, 2) for v in p.values() if v > 0)


def time_budgets(recs):
    """Level-1 activity -> mean minutes per diary."""
    tot = collections.Counter()
    n = 0.0
    for r in recs:
        for e in r[1]:
            tot[level1(e[1])] += r[2] * e[0]
        n += r[2]
    if n <= 0:
        n = 1.0
    return dict((k, v / n) for k, v in tot.items())


def diurnal(recs):
    """Level-1 activity -> 144-slot count vector (minutes-in-slot occupancy).

    🔴 The slot walk carries `FINDING 67`'s lesson: a diary that does not fill
    1440 minutes contributes to the slots it REACHES and to no others. Nothing
    is counted as "not doing activity X" because the diary ended early.
    """
    cur = dict()
    for r in recs:
        slot = 0
        for e in r[1]:
            n = e[0] // SLOT_MINUTES
            a = level1(e[1])
            v = cur.setdefault(a, [0.0] * N_SLOTS)
            for k in range(slot, min(slot + n, N_SLOTS)):
                v[k] += r[2]
            slot += n
            if slot >= N_SLOTS:
                break
    return cur


def jsd_bits(p, q):
    """Jensen-Shannon divergence, base 2, between two non-negative vectors.

    Bounded in [0, 1] bits by construction, so no `epsilon` is needed anywhere
    -- which is exactly why Tier 1 specifies bits and not a KL with a floor.
    """
    sp, sq = sum(p), sum(q)
    if sp <= 0 or sq <= 0:
        return float("nan")
    p = [x / sp for x in p]
    q = [x / sq for x in q]

    def h(v):
        return -sum(x * math.log(x, 2) for x in v if x > 0)
    m = [(a + b) / 2.0 for a, b in zip(p, q)]
    return h(m) - 0.5 * h(p) - 0.5 * h(q)


def copresence_tab(recs):
    """Reported. Share of MINUTES at each co-presence code."""
    c = collections.Counter()
    tot = 0.0
    for r in recs:
        for e in r[1]:
            c[e[4]] += r[2] * e[0]
            tot += r[2] * e[0]
    if not tot:
        return {}
    return dict((k, v / float(tot)) for k, v in c.items())


# ---------------------------------------------------------------------------
# scoring
# ---------------------------------------------------------------------------

def score_pair(ref, cand, label):
    """Every registered quantity, both arms, for one set of diaries."""
    out = {"label": label, "n_ref": len(ref), "n_cand": len(cand)}

    # --- SEQUENCE ARM (the joints -- what `G6.8` is for) ---
    dr, dc = dwell_times(ref), dwell_times(cand)
    w1 = {}
    for a in sorted(set(dr) & set(dc)):
        if len(dr[a]) >= MIN_DWELL_N and len(dc[a]) >= MIN_DWELL_N:
            w1[a] = wasserstein1(dr[a], dc[a])
    out["dwell_w1"] = w1
    out["dwell_w1_max"] = max(w1.values()) if w1 else float("nan")
    out["dwell_w1_worst_activity"] = (max(w1, key=w1.get) if w1 else None)

    tr, tc = transitions_per_day(ref), transitions_per_day(cand)
    out["transitions_ref"] = tr
    out["transitions_cand"] = tc
    out["transitions_abs_err"] = abs(tr - tc)

    pr, pc = transition_dist(ref), transition_dist(cand)
    out["transition_tvd"] = tvd(pr, pc)
    out["transition_entropy_bits_ref"] = transition_entropy_bits(pr)
    out["transition_entropy_bits_cand"] = transition_entropy_bits(pc)

    # --- MARGINAL ARM (what the candidate was HANDED) ---
    br, bc = time_budgets(ref), time_budgets(cand)
    berr = dict((a, abs(br.get(a, 0.0) - bc.get(a, 0.0)))
                for a in set(br) | set(bc))
    out["budget_err_min"] = berr
    out["budget_err_max_min"] = max(berr.values()) if berr else float("nan")

    ur, uc = diurnal(ref), diurnal(cand)
    js = {}
    for a in sorted(set(ur) & set(uc)):
        js[a] = jsd_bits(ur[a], uc[a])
    js = dict((k, v) for k, v in js.items() if v == v)
    out["diurnal_jsd"] = js
    out["diurnal_jsd_mean"] = (sum(js.values()) / len(js)) if js else float("nan")
    out["diurnal_jsd_max"] = max(js.values()) if js else float("nan")

    out["copresence_ref"] = copresence_tab(ref)
    out["copresence_cand"] = copresence_tab(cand)
    return out


def verdicts(s, budget_band=G68_BUDGET_MAX_MIN_POP):
    """PASS/FAIL per registered threshold. NaN is not a PASS."""
    def le(x, t):
        return (x == x) and x <= t
    return {
        "dwell_w1": le(s["dwell_w1_max"], G68_DWELL_W1_MAX_MIN),
        "transitions": le(s["transitions_abs_err"], G68_TRANSITIONS_MAX_ABS_ERR),
        "transition_tvd": le(s["transition_tvd"], G68_TRANSITION_TVD_MAX),
        "budgets": le(s["budget_err_max_min"], budget_band),
        "diurnal_jsd": (le(s["diurnal_jsd_mean"], G68_DIURNAL_JSD_MEAN_MAX)
                        and le(s["diurnal_jsd_max"], G68_DIURNAL_JSD_MAX_MAX)),
    }


SEQUENCE_ARM = ("dwell_w1", "transitions", "transition_tvd")
MARGINAL_ARM = ("budgets", "diurnal_jsd")


# ---------------------------------------------------------------------------
# 🔴 THE SAMPLE-SIZE-MATCHED FLOOR -- registered discipline, not a new design.
#
# Overview, "Statistical discipline, and it is not optional at this N":
#     "each is additionally reported as ... a sample-size-matched bootstrap,
#      where the synthetic-to-real divergence must not exceed the real-to-real
#      split-half divergence. That last comparison is the honest one."
#
# `FINDING 68` is why this is not optional at CELL level: measured on Italy, a
# second REAL sample fails the absolute Tier 1 bands in 65 of 68 attribute-pair
# cells. The bands are population-level and the cells are n >= 100, so at cell
# granularity the absolute band sits BELOW the finite-sample noise floor and a
# perfect model fails it. Both verdicts are emitted; neither is dropped.
# ---------------------------------------------------------------------------

FLOOR_REPEATS = 20     # the floor is the WORST of this many real-real splits,
                       # which is conservative in the candidate's favour and is
                       # stated as such rather than tuned.

FLOOR_KEYS = ("dwell_w1_max", "transitions_abs_err", "transition_tvd",
              "budget_err_max_min", "diurnal_jsd_mean", "diurnal_jsd_max")


def _sub(recs, idx, m):
    return [recs[i] for i in idx[:m]]


def score_with_floor(ref, cand, rng, repeats=FLOOR_REPEATS):
    """Return (test, floor, m). EVERY comparison is m vs m, so the floor is
    matched to the test in sample size and not merely in spirit."""
    m = min(len(ref) // 2, len(cand))
    if m < 2:
        return None, None, m
    floors = []
    for _ in range(repeats):
        idx = list(range(len(ref)))
        rng.shuffle(idx)
        s = score_pair(_sub(ref, idx, m), [ref[i] for i in idx[m:2 * m]], "floor")
        floors.append(s)
    floor = {}
    for k in FLOOR_KEYS:
        vals = [f[k] for f in floors if f[k] == f[k]]
        floor[k] = max(vals) if vals else float("nan")
    ri = list(range(len(ref)))
    ci = list(range(len(cand)))
    rng.shuffle(ri)
    rng.shuffle(ci)
    test = score_pair(_sub(ref, ri, m), _sub(cand, ci, m), "test")
    return test, floor, m


def floor_verdicts(test, floor):
    """A NaN on either side is not a PASS."""
    out = {}
    for k in FLOOR_KEYS:
        t, f = test[k], floor[k]
        out[k] = (t == t) and (f == f) and t <= f
    return out


def cells_of(recs, pair):
    d = collections.defaultdict(list)
    for r in recs:
        pref = r[0]
        d[(pref[pair[0]], pref[pair[1]])].append(r)
    return d


def score_conditioned(ref, cand, rng=None):
    """`G6.8`'s own words: dwell-time distributions conditioned on ATTRIBUTE
    PAIRS. Cells below `MIN_CELL_N` on either side are NOT SCORED, and how many
    were skipped is reported -- a gate that silently drops its hard cells is
    measuring the easy ones.

    Each cell carries TWO verdicts: `verdicts` against the absolute Tier 1
    bands, and `floor_verdicts` against the sample-size-matched real-real floor.
    See `FINDING 68` above for why the second exists."""
    rows = []
    skipped = 0
    for pair in ATTRIBUTE_PAIRS:
        cr, cc = cells_of(ref, pair), cells_of(cand, pair)
        for key in sorted(set(cr) & set(cc)):
            if len(cr[key]) < MIN_CELL_N or len(cc[key]) < MIN_CELL_N:
                skipped += 1
                continue
            s = score_pair(cr[key], cc[key],
                           "%s=%s x %s=%s" % (pair[0], key[0], pair[1], key[1]))
            s["verdicts"] = verdicts(s, budget_band=G68_BUDGET_MAX_MIN_STRATUM)
            if rng is not None:
                t, f, m = score_with_floor(cr[key], cc[key], rng)
                if t is not None:
                    s["floor_verdicts"] = floor_verdicts(t, f)
                    s["floor_m"] = m
                    s["floor"] = dict((k, f[k]) for k in FLOOR_KEYS)
                    s["test_at_m"] = dict((k, t[k]) for k in FLOOR_KEYS)
            rows.append(s)
        skipped += len(set(cr) ^ set(cc))
    return rows, skipped


# ---------------------------------------------------------------------------
# the registered negative controls, built from real diaries
# ---------------------------------------------------------------------------

def _to_slots(eps):
    """144 slots of (act, act2, loc, cop). Slots the diary never reaches are
    None -- never silently filled, per `FINDING 67`."""
    slots = [None] * N_SLOTS
    slot = 0
    for e in eps:
        n = e[0] // SLOT_MINUTES
        for k in range(slot, min(slot + n, N_SLOTS)):
            slots[k] = (e[1], e[2], e[3], e[4])
        slot += n
        if slot >= N_SLOTS:
            break
    return slots


def _to_episodes(slots):
    """Collapse a slot vector back to episodes, merging equal adjacent slots."""
    eps = []
    for s in slots:
        if s is None:
            continue
        if eps and eps[-1][1:] == s:
            eps[-1] = (eps[-1][0] + SLOT_MINUTES,) + s
        else:
            eps.append((SLOT_MINUTES,) + s)
    return eps


def control_shuffled_within(recs, rng):
    """Each diary's own slots permuted. Preserves that diary's time budget
    EXACTLY and destroys its sequence -- and also destroys the population's
    diurnal profile, which is why it is NOT the control the Overview's table
    describes. Built anyway, and reported, so the difference is visible."""
    out = []
    for r in recs:
        slots = [s for s in _to_slots(r[1]) if s is not None]
        rng.shuffle(slots)
        ne = _to_episodes(slots)
        if ne:
            out.append((r[0], ne, r[2]))
    return out


def control_shuffled_across(recs, rng):
    """🔴 THE REGISTERED CONTROL. For each slot index independently, permute
    which diary supplies that slot. The population's diurnal marginal and its
    time budgets are preserved EXACTLY -- every slot keeps its multiset of
    values -- while every within-diary sequence is destroyed. That is precisely
    the Overview's requirement: PASS marginals, FAIL transitions and dwell."""
    grids = [_to_slots(r[1]) for r in recs]
    n = len(grids)
    for k in range(N_SLOTS):
        col = [g[k] for g in grids]
        rng.shuffle(col)
        for i in range(n):
            grids[i][k] = col[i]
    out = []
    for r, g in zip(recs, grids):
        ne = _to_episodes(g)
        if ne:
            out.append((r[0], ne, r[2]))
    return out


def control_modal_collapse(recs, rng):
    """Every diary in a stratum replaced by that stratum's MODAL diary. The
    Overview registers this against DIVERSITY and the VARIANCE RATIO (Tier 2),
    not against `G6.8` -- it is run here to show which arms it does and does not
    move, so `G6.8` is never quoted as evidence against collapse."""
    by = collections.defaultdict(list)
    for r in recs:
        key = tuple(r[0][f] for f in PREFIX_FIELDS)
        by[key].append(r)
    modal = {}
    for key, group in by.items():
        c = collections.Counter()
        for g in group:
            c[tuple(g[1])] += 1
        modal[key] = list(c.most_common(1)[0][0])
    out = []
    for r in recs:
        out.append((r[0], modal[tuple(r[0][f] for f in PREFIX_FIELDS)], r[2]))
    return out


CONTROLS = {"shuffled_across": control_shuffled_across,
            "shuffled_within": control_shuffled_within,
            "modal_collapse": control_modal_collapse}


def split_half(recs, rng):
    """The registered null floor: real vs real. 'a sample-size-matched
    bootstrap, where the synthetic-to-real divergence must not exceed the
    real-to-real split-half divergence' -- Overview, statistical discipline."""
    idx = list(range(len(recs)))
    rng.shuffle(idx)
    h = len(idx) // 2
    return ([recs[i] for i in idx[:h]], [recs[i] for i in idx[h:2 * h]])


# ---------------------------------------------------------------------------

def report(s, v, indent="  "):
    print("%sn_ref=%d  n_cand=%d" % (indent, s["n_ref"], s["n_cand"]))
    print("%s%-4s dwell W1 max        %8.3f min   (<= %.1f)  worst act %s"
          % (indent, "PASS" if v["dwell_w1"] else "FAIL", s["dwell_w1_max"],
             G68_DWELL_W1_MAX_MIN, s["dwell_w1_worst_activity"]))
    print("%s%-4s transitions/day err %8.3f       (<= %.2f)  ref %.3f cand %.3f"
          % (indent, "PASS" if v["transitions"] else "FAIL",
             s["transitions_abs_err"], G68_TRANSITIONS_MAX_ABS_ERR,
             s["transitions_ref"], s["transitions_cand"]))
    print("%s%-4s transition TVD      %8.4f       (<= %.3f)"
          % (indent, "PASS" if v["transition_tvd"] else "FAIL",
             s["transition_tvd"], G68_TRANSITION_TVD_MAX))
    print("%s%-4s time budget err max %8.3f min"
          % (indent, "PASS" if v["budgets"] else "FAIL",
             s["budget_err_max_min"]))
    print("%s%-4s diurnal JSD    mean %8.5f max %.5f bits  (<= %.3f / %.3f)"
          % (indent, "PASS" if v["diurnal_jsd"] else "FAIL",
             s["diurnal_jsd_mean"], s["diurnal_jsd_max"],
             G68_DIURNAL_JSD_MEAN_MAX, G68_DIURNAL_JSD_MAX_MAX))
    print("%s     transition entropy  ref %.4f bits, cand %.4f bits (reported)"
          % (indent, s["transition_entropy_bits_ref"],
             s["transition_entropy_bits_cand"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref")
    ap.add_argument("--cand")
    ap.add_argument("--corpus")
    ap.add_argument("--country")
    ap.add_argument("--control", choices=sorted(CONTROLS))
    ap.add_argument("--split-half", action="store_true")
    ap.add_argument("--conditioned", action="store_true",
                    help="also score every attribute-pair cell (slow)")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--weight-field", default=DEFAULT_WEIGHT_FIELD,
                    help="D-S6-4, ruled 2026-08-21: the default is "
                         "`weight_dia_cal`. `weight_dia` is the declared "
                         "sensitivity. `none` scores unweighted and is kept "
                         "only so the ruling's effect can be measured.")
    ap.add_argument("--harmonised", default=None,
                    help="path to harmonised.parquet (default %s)"
                         % HARMONISED_DEFAULT)
    ap.add_argument("--json-out")
    args = ap.parse_args()

    wfield = (None if str(args.weight_field).lower() in ("none", "")
              else args.weight_field)
    weights = wnull = None
    if wfield:
        weights, wnull = load_weights(wfield, args.harmonised)

    rng = random.Random(args.seed)
    print("=" * 74)
    print("G6.8 -- JOINT-STRUCTURE CHECKERS (registered spec, Tier 1 bands)")
    print("=" * 74)
    if wfield:
        print("weights        : %s   (D-S6-4 ruled 2026-08-21%s)"
              % (wfield, "" if wfield == DEFAULT_WEIGHT_FIELD
                 else " -- \U0001f534 THIS IS THE DECLARED SENSITIVITY, "
                      "NOT THE HEADLINE"))
        print("               : %d weighted diaries in the table, %d rows "
              "carried a null weight and are not in it" % (len(weights), wnull))
    else:
        print("weights        : NONE -- \U0001f534 UNWEIGHTED, which D-S6-4 "
              "did NOT rule. Diagnostic use only.")
    print("min cell n     : %d   (assumption, from G4_1_MIN_STRATUM_N)" % MIN_CELL_N)
    print("seed           : %d" % args.seed)

    def _rep_load(tag):
        d = getattr(load, "last", None)
        if not d or not d["weighted"]:
            return
        if d["dropped_unweighted"] or d["unmatched_no_pid"]:
            print("  %-5s %s: %d diaries, %d DROPPED for carrying no weight, "
                  "%d had no pid to key on and were left at 1.0"
                  % (tag, os.path.basename(d["path"]), d["n"],
                     d["dropped_unweighted"], d["unmatched_no_pid"]))

    if args.ref and args.cand:
        ref = load(args.ref, limit=args.limit, weights=weights)
        _rep_load("ref")
        cand = load(args.cand, limit=args.limit, weights=weights)
        _rep_load("cand")
        title = "%s vs %s" % (os.path.basename(args.ref),
                              os.path.basename(args.cand))
    elif args.corpus:
        ref = load(args.corpus, country=args.country, limit=args.limit,
                   weights=weights)
        _rep_load("ref")
        if args.split_half:
            ref, cand = split_half(ref, rng)
            title = "REAL vs REAL, split-half null floor"
        elif args.control:
            cand = CONTROLS[args.control](ref, rng)
            title = "REAL vs CONTROL '%s'" % args.control
        else:
            raise SystemExit("--corpus needs --control or --split-half")
    else:
        raise SystemExit("give --ref/--cand, or --corpus with --control/--split-half")

    print("comparison     : %s" % title)
    print("")
    s = score_pair(ref, cand, title)
    v = verdicts(s)
    report(s, v)

    seq_fail = [k for k in SEQUENCE_ARM if not v[k]]
    mar_fail = [k for k in MARGINAL_ARM if not v[k]]
    print("")
    print("SEQUENCE arm : %s" % ("PASS" if not seq_fail
                                 else "FAIL (" + ", ".join(seq_fail) + ")"))
    print("MARGINAL arm : %s" % ("PASS" if not mar_fail
                                 else "FAIL (" + ", ".join(mar_fail) + ")"))

    out = {"summary": s, "verdicts": v, "title": title,
           "weight_field": wfield or "none",
           "weight_basis_ruled": "D-S6-4 (a), 2026-08-21: weight_dia_cal is "
                                 "the headline; weight_dia is the declared "
                                 "sensitivity; the two are never mixed",
           "is_headline_basis": (wfield == DEFAULT_WEIGHT_FIELD),
           "sequence_arm_pass": not seq_fail, "marginal_arm_pass": not mar_fail}

    if args.conditioned:
        print("")
        print("--- CONDITIONED ON ATTRIBUTE PAIRS " + "-" * 38)
        rows, skipped = score_conditioned(ref, cand, rng)
        nfail = nfail_floor = n_exceed = 0
        for r in rows:
            fv0 = r.get("floor_verdicts") or {}
            n_exceed += sum(1 for ok in fv0.values() if not ok)
            bad = [k for k, ok in r["verdicts"].items() if not ok]
            if bad:
                nfail += 1
            fv = r.get("floor_verdicts")
            fbad = [k for k, ok in fv.items() if not ok] if fv else None
            if fbad:
                nfail_floor += 1
            print("  %-52s band %-28s floor %s"
                  % (r["label"],
                     "PASS" if not bad else "FAIL: " + ",".join(bad),
                     ("PASS" if not fbad else "FAIL: " + ",".join(fbad))
                     if fv else "n/a"))
        print("")
        print("  %d cells scored, %d cells skipped below n=%d" %
              (len(rows), skipped, MIN_CELL_N))
        print("  vs ABSOLUTE Tier 1 bands              : %d FAIL" % nfail)
        # 🔴 The floor line is a FAMILY of tests and must be read against its own
        # null, not against zero. The test statistic and the FLOOR_REPEATS floor
        # draws are all m-vs-m, so under the null the test exceeds all R floors
        # with probability exactly 1/(R+1) per metric. Those expectations are
        # arithmetic, not a simulation, and they are printed so that "k cells
        # exceeded" is never mistaken for "k cells are broken".
        p1 = 1.0 / (FLOOR_REPEATS + 1)
        nm = len(FLOOR_KEYS)
        exp_cells = len(rows) * (1.0 - (1.0 - p1) ** nm)
        exp_metric = len(rows) * nm * p1
        print("  vs SAMPLE-SIZE-MATCHED real-real floor: %d cells with >=1 "
              "exceedance (null expects %.1f of %d)" % (nfail_floor, exp_cells,
                                                        len(rows)))
        print("                                          %d metric exceedances "
              "of %d (null expects %.1f)"
              % (n_exceed, len(rows) * nm, exp_metric))
        out["floor_repeats"] = FLOOR_REPEATS
        out["metric_exceedances"] = n_exceed
        out["metric_exceedances_expected_under_null"] = exp_metric
        out["cells_with_exceedance_expected_under_null"] = exp_cells
        out["cells_scored"] = len(rows)
        out["cells_failed"] = nfail
        out["cells_failed_vs_floor"] = nfail_floor
        out["cells_skipped"] = skipped
        out["cells"] = [{"label": r["label"], "verdicts": r["verdicts"],
                         "floor_verdicts": r.get("floor_verdicts"),
                         "floor_m": r.get("floor_m"),
                         "floor": r.get("floor"),
                         "test_at_m": r.get("test_at_m"),
                         "dwell_w1_max": r["dwell_w1_max"],
                         "transitions_abs_err": r["transitions_abs_err"],
                         "transition_tvd": r["transition_tvd"]} for r in rows]

    if args.json_out:
        io.open(args.json_out, "w", encoding="utf-8").write(
            json.dumps(out, indent=2, sort_keys=True, default=str))
        print("")
        print("wrote %s" % args.json_out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
