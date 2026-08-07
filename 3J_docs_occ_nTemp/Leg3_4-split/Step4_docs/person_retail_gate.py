#!/usr/bin/env python
"""V3-J1 -- the person-level retail gate (RW9).

WHY THIS EXISTS
---------------
V2-E1 established that all ten RW/RETM gates report identical statuses on a pool
whose retail vectors have been permuted between people within (cycle x day-type x
province): the named retail battery measures MARGINALS, not person-level skill.
The fix was written down on 2026-08-05 as deliverable item 2 and was never built.
This is it.

WHAT IT MEASURES
----------------
For every synthetic row belonging to person p, the partner is p's OWN observed
row.  Two statistics, both expressed RELATIVE TO A PERMUTATION NULL so that
neither can be inflated by the sample size:

  J1a  participation -- does the model know WHO shops
       P(syn has any retail | obs has any retail), against the null

  J1b  timing        -- among pairs where both sides shop, does it know WHEN
       mean |syn AND obs| over active slots, against the null

THE NULL, AND THE ONE TERM IN IT THAT IS LOAD-BEARING
-----------------------------------------------------
    cell = (CYCLE_YEAR, PR, syn DDAY_STRATA, the person's observed DDAY_STRATA)

A true pair ALWAYS has observed strata != synthetic strata -- a person's two
synthetic rows are the two strata that are not their own diary day.  Permuting
over the first three terms only would let some shuffled partners share the
synthetic row's strata, and they could then agree more for a reason that has
nothing to do with person identity.  The null would be measuring day type.
V2-E1 paid for this lesson with a global shuffle that broke the day-type and
province conditioning RW6/RW7 legitimately read: A PERTURBATION THAT CHANGES
MORE THAN ONE THING CANNOT ATTRIBUTE WHAT IT BREAKS.

BANDS -- pre-registered 2026-08-06 in improvements/v3/V3-J1_PREREGISTRATION.md,
BEFORE any statistic was computed.  PASS lift >= 0.10 AND z >= 5; WARN lift >=
0.02; FAIL below.  Under the null hypothesis this gate exists to test -- the
generator retains no person-level retail information -- the lift is 0, so the
bar is a minimum detectable retention rather than a tolerance around a
reference.  The z requirement can only ever downgrade a verdict, never upgrade
one.

Read-only: nothing here writes to the pool or to any shipped artefact.
"""

import numpy as np
import pandas as pd

RET_COLS = [f"ret30_{i:03d}" for i in range(1, 49)]


def chan_cols(channel="ret30"):
    """The 48 half-hour columns of one channel (ret30 / hom30 / wrk30)."""
    return [f"{channel}_{i:03d}" for i in range(1, 49)]
META_COLS = ["occID", "CYCLE_YEAR", "DDAY_STRATA", "PR", "IS_SYNTHETIC"]
DEMO_COLS = ["AGEGRP", "SEX", "LFTAG"]

# Pre-registered bands. Not to be edited in response to a result.
PASS_LIFT, WARN_LIFT, PASS_Z = 0.10, 0.02, 5.0
N_PERM = 200
SEED = 42


def load_pool(path, with_demographics=True, channel="ret30"):
    """Load only the columns the gate needs.  ~53-56 of the pool's 644."""
    cols = META_COLS + chan_cols(channel) + (DEMO_COLS if with_demographics else [])
    df = pd.read_csv(path, usecols=cols)
    return df


def build_pairs(df, demo_null=False, channel="ret30"):
    """Pair every synthetic row with its own person's observed row.

    Returns (syn_R, obs_R, cell_codes, n_dropped_rows, n_singleton_cells).
    A cell that cannot be permuted (fewer than 2 distinct persons) is EXCLUDED
    AND COUNTED -- never silently dropped, because a null computed over cells
    that cannot be shuffled is a null that cannot fail.
    """
    obs = df[df.IS_SYNTHETIC == 0]
    syn = df[df.IS_SYNTHETIC == 1]

    key_obs = pd.MultiIndex.from_arrays([obs.occID, obs.CYCLE_YEAR])
    obs_pos = pd.Series(np.arange(len(obs)), index=key_obs)
    key_syn = pd.MultiIndex.from_arrays([syn.occID, syn.CYCLE_YEAR])
    partner = obs_pos.reindex(key_syn).to_numpy()

    unmatched = int(np.isnan(partner).sum())
    keep = ~np.isnan(partner)
    partner = partner[keep].astype(np.int64)
    syn = syn[keep]

    cols = chan_cols(channel)
    obs_R_all = obs[cols].to_numpy(dtype=bool)
    syn_R = syn[cols].to_numpy(dtype=bool)
    obs_R = obs_R_all[partner]

    parts = [syn.CYCLE_YEAR.to_numpy(), syn.PR.to_numpy(),
             syn.DDAY_STRATA.to_numpy(),
             obs.DDAY_STRATA.to_numpy()[partner]]
    if demo_null:
        for c in DEMO_COLS:
            parts.append(obs[c].to_numpy()[partner])
    # Factorise the stacked tuple rather than reaching for a MultiIndex helper:
    # this is stable across pandas versions and makes the cell definition
    # readable as one array of columns.
    stacked = np.column_stack(parts)
    _, cell = np.unique(stacked, axis=0, return_inverse=True)

    counts = np.bincount(cell)
    singleton = counts < 2
    keep2 = ~singleton[cell]
    n_singleton_rows = int((~keep2).sum())

    return (syn_R[keep2], obs_R[keep2], cell[keep2],
            unmatched, n_singleton_rows, int(singleton.sum()))


def _stats(syn_R, obs_R):
    """The two raw (not yet null-relative) statistics."""
    syn_any = syn_R.any(axis=1)
    obs_any = obs_R.any(axis=1)
    n_obs_any = int(obs_any.sum())
    a = float((syn_any & obs_any).sum()) / n_obs_any if n_obs_any else np.nan

    both = syn_any & obs_any
    n_both = int(both.sum())
    b = float((syn_R[both] & obs_R[both]).sum()) / n_both if n_both else np.nan
    return a, b, n_obs_any, n_both


def _within_cell_permutation(cell, rng):
    """One uniform permutation of row order WITHIN each cell.

    Sorting by (cell, random) is a within-cell shuffle in a single lexsort --
    no Python loop over the ~500 cells, and no cell can leak into another.
    """
    return np.lexsort((rng.random(cell.shape[0]), cell))


def evaluate(syn_R, obs_R, cell, n_perm=N_PERM, seed=SEED):
    """Observed statistics, their permutation nulls, lifts, z-scores."""
    rng = np.random.default_rng(seed)
    order = np.argsort(cell, kind="stable")          # rows grouped by cell
    cell_s = cell[order]
    syn_s, obs_s = syn_R[order], obs_R[order]

    obs_a, obs_b, n_obs_any, n_both = _stats(syn_s, obs_s)

    null_a = np.empty(n_perm)
    null_b = np.empty(n_perm)
    for k in range(n_perm):
        p = _within_cell_permutation(cell_s, rng)
        a, b, _, _ = _stats(syn_s, obs_s[p])
        null_a[k], null_b[k] = a, b

    out = {}
    for name, val, null in (("a", obs_a, null_a), ("b", obs_b, null_b)):
        # An all-NaN null is a legitimate arm (the zero-retail perturbation),
        # not an error -- it is turned into an explicit FAIL-with-reason by
        # verdict().  Suppress the warning so the output cannot be read as a
        # crash the run got away with.
        with np.errstate(invalid="ignore"):
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                m = float(np.nanmean(null)) if np.isfinite(null).any() else np.nan
                sd = float(np.nanstd(null, ddof=1)) if np.isfinite(null).sum() > 1 else np.nan
        if not np.isfinite(val) or not np.isfinite(m) or m == 0:
            lift, z = np.nan, np.nan
        else:
            lift = val / m - 1.0
            z = (val - m) / sd if sd > 0 else np.inf
        out[name] = dict(value=val, null_mean=m, null_sd=sd, lift=lift, z=z)

    out["n_pairs"] = int(syn_R.shape[0])
    out["n_obs_any"] = n_obs_any
    out["n_both"] = n_both
    out["n_cells"] = int(np.unique(cell).size)
    out["n_perm"] = n_perm
    return out


def verdict(res):
    """Apply the pre-registered bands.  Returns (level, reason)."""
    lift, z, val = res["lift"], res["z"], res["value"]
    if not np.isfinite(val):
        return "fail", ("statistic UNDEFINED -- no pair on which it is computable "
                        "(the pool carries no synthetic retail, or no pair has "
                        "retail on both sides); reported as FAIL rather than as 0.0")
    if not np.isfinite(lift):
        return "fail", ("null mean is zero -- lift undefined; reported as FAIL "
                        "rather than as 0.0")
    if lift >= PASS_LIFT and z >= PASS_Z:
        return "pass", f"lift {lift:+.4f} >= {PASS_LIFT} and z {z:.1f} >= {PASS_Z}"
    if lift >= PASS_LIFT:
        return "warn", (f"lift {lift:+.4f} clears {PASS_LIFT} but z {z:.1f} is "
                        f"below {PASS_Z} -- the null is not stable enough to call it")
    if lift >= WARN_LIFT:
        return "warn", f"lift {lift:+.4f} is in [{WARN_LIFT}, {PASS_LIFT})"
    return "fail", (f"lift {lift:+.4f} is below {WARN_LIFT} -- the generated retail "
                    f"day is no more like this person's own observed day than a "
                    f"same-cell stranger's")


def run(path, n_perm=N_PERM, seed=SEED, demo_null=False, df=None, channel="ret30"):
    """Convenience entry point.  `df` lets a caller pass a mutated copy."""
    if df is None:
        df = load_pool(path, channel=channel)
    syn_R, obs_R, cell, unmatched, drop_rows, drop_cells = build_pairs(
        df, demo_null, channel)
    res = evaluate(syn_R, obs_R, cell, n_perm, seed)
    res["unmatched_syn_rows"] = unmatched
    res["rows_in_unshuffleable_cells"] = drop_rows
    res["unshuffleable_cells"] = drop_cells
    res["channel"] = channel
    res["demo_null"] = demo_null
    res["a_verdict"], res["a_reason"] = verdict(res["a"])
    res["b_verdict"], res["b_reason"] = verdict(res["b"])
    return res


def format_lines(res, tag="RW9"):
    """The gate's report lines, in the validator's own style."""
    a, b = res["a"], res["b"]
    return [
        (res["a_verdict"], tag,
         f"Person-level retail PARTICIPATION vs within-cell shuffle null: "
         f"P(syn any | obs any) = {a['value']:.6f} vs null {a['null_mean']:.6f} "
         f"+/- {a['null_sd']:.6f} => lift {a['lift']:+.4f}, z {a['z']:.1f} "
         f"({res['n_obs_any']:,} pairs with observed retail; {res['n_perm']} "
         f"permutations; {res['a_reason']})"),
        (res["b_verdict"], tag,
         f"Person-level retail TIMING vs within-cell shuffle null: "
         f"mean |syn AND obs| = {b['value']:.6f} vs null {b['null_mean']:.6f} "
         f"+/- {b['null_sd']:.6f} => lift {b['lift']:+.4f}, z {b['z']:.1f} "
         f"({res['n_both']:,} pairs with retail on both sides; {res['b_reason']})"),
        ("info", tag,
         f"Coverage: {res['n_pairs']:,} person-matched pairs across "
         f"{res['n_cells']:,} shuffle cells; {res['unmatched_syn_rows']:,} synthetic "
         f"rows had no observed partner; {res['rows_in_unshuffleable_cells']:,} rows "
         f"in {res['unshuffleable_cells']:,} cells too small to permute were EXCLUDED "
         f"(a null computed over cells that cannot be shuffled cannot fail)"),
    ]


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="V3-J1 person-level channel gate (RW9)")
    ap.add_argument("pool")
    ap.add_argument("--n-perm", type=int, default=N_PERM)
    ap.add_argument("--channel", default="ret30",
                    help="ret30 (the gate) | hom30 | wrk30 (cross-channel diagnostic)")
    ap.add_argument("--demo-null", action="store_true",
                    help="tighten the null with AGEGRP x SEX x LFTAG (diagnostic)")
    a = ap.parse_args()
    r = run(a.pool, n_perm=a.n_perm, demo_null=a.demo_null, channel=a.channel)
    tag = "RW9" if (a.channel == "ret30" and not a.demo_null) else           f"DIAG[{a.channel}{'+demo' if a.demo_null else ''}]"
    for lvl, t, txt in format_lines(r, tag):
        print(f"[{lvl.upper():4s}] {t} | {txt}")
