#!/usr/bin/env python
"""
4J Step 6, section 5: the RAKED-DONOR NULL -- `G6.1`'s pre-registered bar.

`prereg.md` (FROZEN, md5 e4243e07cdd80c9c846b91f40e3e8c45) section 5:

    Real diaries from the N-1 pool, raked by IPF onto the held-out country's
    published marginals  ->  THE PRE-REGISTERED BAR

    "Construction, so it cannot be built favourably: IPF the REAL N-1 diaries
    onto the held-out country's published marginals -- the same marginals the
    model was given, the same geography, the same strata. A null built on
    different marginals from the model's is not a null, it is a handicap."

    "This is the only place raking is permitted in this project. It builds the
    null. It never touches our output."

WHAT THIS MODULE IS, AND IS NOT
-------------------------------
It is the raking engine and the comparison rule, with their guards. It is NOT a
scorer: `score_margin()` takes two already-computed metric values and applies
`V6.c`. Choosing the metric is `G6.1`'s business, not this module's.

🔴 IT CANNOT BE RUN END-TO-END TODAY. `rake()` needs the held-out country's
PUBLISHED marginals, which are Step 5 work item 5.1's deliverable
(`outputs_step5/marginals_<country>.csv` + `marginals_provenance.md`), and
`outputs_step5/` is EMPTY. So `G6.1`'s bar is blocked on Step 5.1 -- a dependency
that is in neither document. The algorithm and every guard below are testable
without it, and are tested in `4thJ_step6_rakeddonor_selftest.py`.

THE THREE WAYS THIS NULL COULD BE BUILT FAVOURABLY, EACH REFUSED IN CODE
------------------------------------------------------------------------
1. Raking the donors onto DIFFERENT marginals from the model's. `rake()` takes a
   `marginals_source` label and `score_margin()` refuses to compare two runs
   whose labels differ. prereg calls this "not a null, it is a handicap".
2. Leaving the held-out country in the donor pool. `rake()` FAILS if any donor
   carries it -- the pool is N-1 by definition, and a self-donor would make the
   null unbeatable for the right reason and the claim unfalsifiable.
3. A non-strict comparison. `V6.c`: the margin test is `> 0`, never `>= 0`, so
   that "the null scored against itself" -- exactly zero margin -- FAILS.
"""

import sys

#: `G5.1`'s tolerance, reused deliberately: a raked margin is a fitted margin and
#: is held to the same +-0.5 pp the synthetic population is held to.
MARGIN_TOL_PP = 0.5
MAX_ITER = 200


class RakeError(ValueError):
    pass


def _weighted_shares(donors, weights, var):
    tot = 0.0
    acc = {}
    for d, w in zip(donors, weights):
        acc[d[var]] = acc.get(d[var], 0.0) + w
        tot += w
    if tot <= 0:
        raise RakeError("total weight collapsed to %r while raking %r" % (tot, var))
    return {k: v / tot for k, v in acc.items()}


def rake(donors, target_marginals, held_out_country, marginals_source,
         collapse=None, tol_pp=MARGIN_TOL_PP, max_iter=MAX_ITER):
    """IPF the donor pool onto `target_marginals`.

    donors            list of dicts, each carrying the stratum variables and a
                      `country` key. These are REAL diaries from the N-1 pool.
    target_marginals  {variable: {category: share}}, shares summing to 1 per
                      variable. The held-out country's PUBLISHED marginals.
    held_out_country  ISO code that must NOT appear among the donors.
    collapse          optional {variable: {donor_category: target_category}},
                      applied to a COPY of the donors before raking. Required
                      whenever the held-out country publishes fewer categories
                      than the donor pool carries -- see Guard 5 and `FINDING
                      52`. Carried into the result and into `marginals_source`
                      so `score_margin` cannot compare a collapsed run with an
                      uncollapsed one.
    marginals_source  provenance label, carried into the result and compared by
                      `score_margin`. Refused if empty (`G5.6` / `V5.b` spirit:
                      a provenance field nobody fills is not provenance).

    Returns {"weights", "iterations", "max_dev_pp", "marginals_source",
             "n_donors", "held_out_country", "collapse"}.
    """
    if not donors:
        raise RakeError("empty donor pool -- a null over zero donors passes for the wrong reason")
    if not target_marginals:
        raise RakeError("no target marginals given")
    if not marginals_source or not str(marginals_source).strip():
        raise RakeError(
            "marginals_source is empty. prereg section 5 requires the null be raked onto the SAME "
            "published marginals the model was given; an unlabelled source cannot be shown to be "
            "the same one.")

    # Guard 2: the pool is N-1 by definition.
    intruders = sorted({d.get("country") for d in donors if d.get("country") == held_out_country})
    if intruders:
        raise RakeError(
            "the held-out country %r appears in the donor pool. The raked-donor null is built from "
            "the N-1 pool; a self-donor makes the null unbeatable for the right reason and the "
            "claim unfalsifiable." % held_out_country)

    # 🔴 `FINDING 52`. Applied BEFORE the per-variable checks so that Guard 5
    # sees the recoded pool, not the raw one. A collapse is a declared loss of
    # resolution, so it is stamped onto the provenance label: a run that folded
    # `homemaker` into `other_inactive` must never compare equal to one that
    # did not.
    if collapse:
        if not isinstance(collapse, dict):
            raise RakeError("collapse must be {variable: {donor_category: target_category}}")
        for var, cmap in sorted(collapse.items()):
            if var not in target_marginals:
                raise RakeError(
                    "collapse names variable %r, which is not among the target marginals. A recode "
                    "of a field nobody rakes on is a silent edit of the donor pool." % var)
            for src_cat, dst_cat in sorted(cmap.items()):
                if dst_cat not in target_marginals[var]:
                    raise RakeError(
                        "collapse sends %r -> %r but %r is not a category of target %r. Collapsing "
                        "into a category the target does not want deletes the donors twice over."
                        % (src_cat, dst_cat, dst_cat, var))
        donors = [dict(d) for d in donors]
        for d in donors:
            for var, cmap in collapse.items():
                if var in d and d[var] in cmap:
                    d[var] = cmap[d[var]]
        marginals_source = "%s|collapse=%s" % (
            str(marginals_source).strip(),
            ";".join("%s:%s>%s" % (v, a, b)
                     for v in sorted(collapse)
                     for a, b in sorted(collapse[v].items())))

    for var, tgt in target_marginals.items():
        missing = [d for d in donors if var not in d]
        if missing:
            raise RakeError("%d donors carry no %r field" % (len(missing), var))
        s = sum(tgt.values())
        if abs(s - 1.0) > 1e-6:
            raise RakeError("target marginal %r sums to %.6f, not 1.0" % (var, s))
        have = {d[var] for d in donors}
        empty = sorted(c for c, share in tgt.items() if share > 0 and c not in have)
        if empty:
            # 🔴 Never silently drop. A category the target wants and the pool
            # cannot supply is a real limit on the null, not a rounding issue.
            raise RakeError(
                "target %r wants categories %s that NO donor has. IPF cannot create them; dropping "
                "them silently would rake onto marginals different from the model's." % (var, empty))

        # 🔴 Guard 5 -- `FINDING 52`, the mirror image of the guard above, and
        # the dangerous direction. `factor` is built only from `tgt`, so a donor
        # whose category the target never names is multiplied by
        # `factor.get(..., 0.0)` and DELETED -- while `max_dev_pp` still reports
        # a perfect fit, because every category the target does name converged.
        # Measured on a 120-donor pool against Spain's five published bands:
        # 20 donors zeroed, 16.67 %% of the pool gone, max_dev_pp 5.6e-15.
        # A shrunken pool is a different null, so this is refused, not warned.
        orphan = sorted(c for c in have if c not in tgt)
        if orphan:
            raise RakeError(
                "%d donors carry %r categories %s that target %r never names. rake() would give "
                "them weight 0.0 and still report convergence. Pass `collapse` to fold them into a "
                "published category, or fix the marginal -- never let the pool shrink silently."
                % (sum(1 for d in donors if d[var] in orphan), var, orphan, var))

    weights = [1.0] * len(donors)
    max_dev_pp = None
    for it in range(1, max_iter + 1):
        for var, tgt in target_marginals.items():
            cur = _weighted_shares(donors, weights, var)
            factor = {}
            for cat, want in tgt.items():
                have = cur.get(cat, 0.0)
                factor[cat] = (want / have) if have > 0 else 0.0
            weights = [w * factor.get(d[var], 0.0) for d, w in zip(donors, weights)]
            if sum(weights) <= 0:
                raise RakeError("all weights went to zero while raking %r" % var)

        devs = []
        for var, tgt in target_marginals.items():
            cur = _weighted_shares(donors, weights, var)
            for cat, want in tgt.items():
                devs.append(abs(cur.get(cat, 0.0) - want) * 100.0)
        max_dev_pp = max(devs)
        if max_dev_pp <= tol_pp:
            break
    else:
        raise RakeError(
            "IPF did not converge in %d iterations: worst margin off by %.6g pp, tolerance %.6g pp. "
            "Reported as a failure, never as a result." % (max_iter, max_dev_pp, tol_pp))

    return {
        "weights": weights,
        "iterations": it,
        "max_dev_pp": max_dev_pp,
        "marginals_source": str(marginals_source).strip(),
        "n_donors": len(donors),
        "held_out_country": held_out_country,
        "collapse": dict(collapse) if collapse else None,
    }


def score_margin(model_value, null_value, lower_is_better, model_source, null_source):
    """`G6.1`: does the model beat the raked-donor null?

    🔴 `V6.c` -- the comparison is STRICT. "A prediction of movement must not be
    satisfiable by nothing moving." Scoring the null against itself gives a
    margin of exactly 0.0, and this returns PASS=False for it.

    🔴 Guard 1 -- both sides must have been scored against the SAME marginals.
    prereg section 5: "A null built on different marginals from the model's is
    not a null, it is a handicap."
    """
    if str(model_source).strip() != str(null_source).strip():
        raise RakeError(
            "model was scored against marginals %r and the null against %r. prereg section 5 "
            "requires the same marginals, same geography, same strata." % (model_source, null_source))
    margin = (null_value - model_value) if lower_is_better else (model_value - null_value)
    return {"margin": margin, "passes": margin > 0.0, "strict": True}


if __name__ == "__main__":
    print("Library module. Run 4thJ_step6_rakeddonor_selftest.py for its unit tests.",
          file=sys.stderr)
