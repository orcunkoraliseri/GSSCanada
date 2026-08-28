#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""4J Step 10 -- emit the ruled cell -> presence-series binding for the EU campaign.

WHAT THIS IMPLEMENTS. `D-S10-8`, ruled 2026-08-27:

    Deterministic rank-order mapping: archetype i (sorted by `archetype_id`
    within fold) maps to household i (`hid` sorted). 1 dwelling per cell. The
    5 levels of `f` share the identical presence series.

WHY A RANK ORDER AND NOT A STRATUM MATCH. The 510 spec rows are archetype-only:
a cell carries `archetype_id`, `epw_path`, `sensitivity_f`, `survey_fold` and
weather identity, and NO occupant attribute of any kind. There is therefore no
attribute on the cell side to match a household stratum against, and any
"matched" mapping would be inventing the join key it claims to use. A rank order
is the only mapping that is both deterministic and honest about carrying no
occupant semantics -- and it is recorded as such: the binding is ARBITRARY BUT
FIXED, never "representative".

WHY IT IS BIJECTIVE. Per fold the spec holds `es` 24, `uk` 36, `it` 42
archetypes against 100 shipped household series, so rank i is unique for every
archetype and no wrapping, reuse or modulo is ever reached. 🔴 If a future spec
raises any fold above 100 archetypes this script MUST refuse rather than wrap --
see `_bind_fold`. The refusal is the point: a silent modulo would give two
archetypes the same occupant and no gate downstream could see it.

WHY THE FOUR `f > 0` LEVELS SHARE ONE SERIES. `f` is the injection weight in
`phi(t) = 3.0 * ((1 - f) + f * g(t)/mean(g))`. Redrawing `g(t)` per level would
confound the sensitivity sweep with sampling noise, so the sweep would no longer
measure what it is named for. Ruled explicitly; asserted here.

WHICH BUNDLE PER FOLD. The ruled calendar year per fold (`D-S10-1`, and
`D-S10-7` which held `uk` at 2014): `es` 2010, `uk` 2014, `it` 2014. Passed in
explicitly rather than inferred, and the chosen bundle's own manifest `year` is
checked against the expectation -- a bundle on the wrong calendar is the
`D-S9-3` failure class and no length check can see it.

READ-ONLY on every input. Writes one JSON.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import io
import json
import os
import sys

#: Ruled calendar year per fold. `es`/`it` from `D-S10-1`; `uk` held at 2014 by
#: `D-S10-7` option (b) against a v1.0 spec that pins a y2015 EPW -- the repin to
#: `uk_london_2014_2015_y2014.epw` is asked of OpenUBEM as a `v1.1`.
RULED_YEAR = {"es": 2010, "uk": 2014, "it": 2014}

#: `D-S10-8`: one dwelling per archetype cell.
DWELLINGS_PER_CELL = 1

#: The five injection levels the spec carries. All five of one archetype share
#: one series; the four non-zero ones are the 408.
F_LEVELS = (0.0, 0.15, 0.3, 0.5, 1.0)


def sha256_of(path):
    h = hashlib.sha256()
    with io.open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_spec_archetypes(spec_path):
    """Return {fold: [archetype_id, ...]} sorted, read from the frozen spec.

    Sorted with Python's default string ordering and that ordering is RECORDED in
    the output, because "sorted" is not self-describing across locales or across
    a rename of the ids. A consumer reproducing this mapping must sort the same
    way, and the output names which way that is.
    """
    with io.open(spec_path, encoding="utf-8") as fh:
        spec = json.load(fh)
    cells = spec.get("cells") or spec.get("rows")
    if cells is None:
        raise SystemExit("spec carries neither 'cells' nor 'rows'")
    by_fold = collections.defaultdict(set)
    for c in cells:
        by_fold[c["survey_fold"]].add(c["archetype_id"])
    return {f: sorted(v) for f, v in by_fold.items()}, spec, len(cells)


def load_bundle_hids(bundle_dir, expect_fold, expect_year):
    """Return the bundle's hids SORTED, plus what its manifest actually says."""
    man_path = os.path.join(bundle_dir, "manifest.json")
    with io.open(man_path, encoding="utf-8") as fh:
        man = json.load(fh)
    if man["fold"] != expect_fold:
        raise SystemExit(
            "bundle %s is fold %s, expected %s" % (bundle_dir, man["fold"], expect_fold))
    if int(man["year"]) != int(expect_year):
        raise SystemExit(
            "🔴 bundle %s is calendar %s, ruled year is %s. Refusing: driving an "
            "EPW with a presence array on another year's calendar lands weekends "
            "on weekdays and no length check can see it."
            % (bundle_dir, man["year"], expect_year))
    hids = [h["hid"] for h in man["households"]]
    widths = sorted({len(h) for h in hids})
    if len(widths) != 1:
        raise SystemExit(
            "🔴 hids in %s are not fixed-width (%r) -- a string sort is then NOT a "
            "numeric sort and the ruled 'hid sorted' order is ambiguous. Refusing."
            % (bundle_dir, widths))
    return sorted(hids), man, widths[0]


def _bind_fold(fold, archetypes, hids):
    if len(archetypes) > len(hids):
        raise SystemExit(
            "🔴 fold %s has %d archetypes against %d shipped series. The ruled "
            "rank-order mapping is bijective only while archetypes <= series. "
            "REFUSING to wrap: a modulo would give two archetypes the same "
            "occupant and nothing downstream could see it. This needs a new "
            "ruling, not a fallback." % (fold, len(archetypes), len(hids)))
    return [
        {"rank": i, "archetype_id": a, "hid": hids[i],
         "presence_csv": "presence_HH_%s_%s.csv" % (fold, hids[i])}
        for i, a in enumerate(archetypes)
    ]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", required=True, help="eu_campaign_cell_spec_v1.0.json")
    ap.add_argument("--schedules-root", required=True,
                    help="Step7_docs/outputs_step7/schedules")
    ap.add_argument("--bundle", action="append", required=True, metavar="FOLD=DIRNAME",
                    help="e.g. --bundle es=leg5_es_independent_seed1_cal2010 "
                         "(repeat per fold). Named explicitly, never inferred.")
    ap.add_argument("--out", required=True)
    ap.add_argument("--supersedes", default=None, metavar="PATH",
                    help="a previously shipped binding artefact this one replaces. "
                         "Records its path, sha256 and the reason, so the earlier "
                         "file is retained and never edited in place (additive "
                         "labelling). Used for the v1.0 -> v1.1 spec repin.")
    ap.add_argument("--hash-series", action="store_true",
                    help="also record each bound series' sha256 (slower; reads "
                         "every CSV). Recommended for anything shipped.")
    a = ap.parse_args(argv)

    bundles = {}
    for item in a.bundle:
        if "=" not in item:
            raise SystemExit("--bundle wants FOLD=DIRNAME, got %r" % item)
        f, d = item.split("=", 1)
        bundles[f] = d

    by_fold, spec, n_cells = load_spec_archetypes(a.spec)

    missing = sorted(set(by_fold) - set(bundles))
    if missing:
        raise SystemExit("no --bundle given for fold(s): %s" % ", ".join(missing))

    out = {
        "artefact": "4J cell -> presence-series binding",
        "ruling": "D-S10-8, ruled 2026-08-27",
        "rule_statement": (
            "Within each survey_fold, sort the spec's distinct archetype_id values "
            "ascending (Python str ordering, i.e. byte/codepoint order) and sort the "
            "bundle's household hids ascending (fixed-width zero-padded strings, so "
            "this equals numeric order). Archetype at rank i is driven by the "
            "household at rank i. All five sensitivity_f levels of one archetype are "
            "driven by that same single series. One dwelling per cell."),
        "sort_order_declared": "python_str_ascending_on_both_sides",
        "dwellings_per_cell": DWELLINGS_PER_CELL,
        "f_levels_share_one_series": True,
        "f_levels": list(F_LEVELS),
        "semantics_warning": (
            "The binding carries NO occupant semantics. A spec cell holds no occupant "
            "attribute, so this is an arbitrary-but-fixed pairing, never a "
            "representative or stratum-matched one. It must never be described as "
            "matching households to archetypes."),
        "spec": {
            "path": os.path.basename(a.spec),
            "sha256": sha256_of(a.spec),
            "n_cells": n_cells,
        },
        "ruled_year_per_fold": RULED_YEAR,
        "binding_invariance": (
            "This binding keys on survey_fold and archetype_id only. Neither moves "
            "under a weather-only spec revision, so the cell -> series pairing is "
            "INVARIANT across eu_campaign_cell_spec v1.0 -> v1.1; only the spec "
            "digest recorded above moves. A runner must validate against the spec "
            "digest of the version it actually executes."),
        "folds": {},
    }

    if a.supersedes:
        out["supersedes"] = {
            "path": os.path.basename(a.supersedes),
            "sha256": sha256_of(a.supersedes),
            "retained": True,
            "reason": ("re-emitted against eu_campaign_cell_spec_v1.1.json (the "
                       "D-S10-7 uk weather repin). The superseded file is left "
                       "byte-identical on disk; it is not edited."),
        }

    for fold in sorted(by_fold):
        bdir = os.path.join(a.schedules_root, bundles[fold])
        hids, man, width = load_bundle_hids(bdir, fold, RULED_YEAR[fold])
        rows = _bind_fold(fold, by_fold[fold], hids)
        if a.hash_series:
            for r in rows:
                r["presence_sha256"] = sha256_of(os.path.join(bdir, r["presence_csv"]))
        out["folds"][fold] = {
            "bundle": bundles[fold],
            "bundle_year": man["year"],
            "bundle_seed": man["seed"],
            "bundle_rule": man["rule"],
            "bundle_rho": man["rho"],
            "rotated_to_midnight": man["rotated_to_midnight"],
            "diary_origin_hour": man["diary_origin_hour"],
            "n_series_shipped": len(hids),
            "hid_width": width,
            "n_archetypes": len(by_fold[fold]),
            "n_cells_bound": len(by_fold[fold]) * len(F_LEVELS),
            "bijective": True,
            "series_unused": len(hids) - len(by_fold[fold]),
            "binding": rows,
        }

    total_cells = sum(v["n_cells_bound"] for v in out["folds"].values())
    out["n_cells_bound_total"] = total_cells
    if total_cells != n_cells:
        raise SystemExit(
            "🔴 bound %d cells but the spec holds %d. Refusing to write a partial "
            "binding." % (total_cells, n_cells))

    with io.open(a.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
        fh.write("\n")

    print("wrote %s" % a.out)
    for fold in sorted(out["folds"]):
        v = out["folds"][fold]
        print("  %s  %d archetypes x %d f-levels = %d cells, on %d series (%d unused), year %s"
              % (fold, v["n_archetypes"], len(F_LEVELS), v["n_cells_bound"],
                 v["n_series_shipped"], v["series_unused"], v["bundle_year"]))
    print("  total %d cells bound against a spec of %d" % (total_cells, n_cells))
    return 0


if __name__ == "__main__":
    sys.exit(main())
