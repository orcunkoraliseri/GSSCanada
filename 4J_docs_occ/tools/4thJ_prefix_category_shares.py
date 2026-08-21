#!/usr/bin/env python
"""
4J -- the cross-country category-share comparison, one block per prefix field.

WHY THIS EXISTS
---------------
`Resources/preprocessing_precedents.md` section 5: the 2nd paper's
`outputs_step2/column_categories_comparison.txt` printed every harmonised
column's category share for each wave on adjacent lines, and two whole classes
of defect fell out of it without a gate being written --

  1. a DTYPE SPLIT -- `2005: [1.0: ...]` against `2015: [1: ...]`, the same
     column float in two waves and int in two others, so any code comparing
     category keys as strings silently matches nothing;
  2. an EMPTY FIELD -- `MODE 2005: []`, the field simply absent from that wave.

This is the 4J equivalent, per COUNTRY instead of per wave. It would have shown
`FINDING 48` -- the `(11-14, econ)` country fingerprint, deterministic and with
no overlap between the three countries -- on sight, instead of after Step 2 had
logged it as an Italian non-response asymmetry.

WHAT IT IS NOT
--------------
🔴 Not a gate. It asserts nothing and fails nothing. It is a DIAGNOSTIC, printed
so a human sees the shape of every stratum field side by side across the three
countries before deciding anything about them. Nothing downstream reads it.

🔴 It reads `harmonised.parquet` only -- the corpus, our own data, all three
countries. It touches no census marginal, so it cannot contaminate a held-out
fold: the LOCO rule bites on using a country's OWN microdata to set its OWN
target, and there is no target here.

  usage: py -3 4thJ_prefix_category_shares.py <harmonised.parquet> [out.txt]
"""
import sys
import io

import pandas as pd

# The frozen six-field prefix (tools/encoder.py), plus the two fields that were
# considered and dropped, so their absence is visible rather than assumed.
PREFIX = ["country", "strat_age_band", "strat_sex", "strat_hh_type",
          "strat_econ_status", "strat_day_type"]
ALSO = ["season", "strat_mode", "strat_scheme"]   # dropped: D-S2-19, D-S3-11


def shares(df, col, countries):
    """{country: [(category, n, pct, dtype_repr), ...]} at the DIARY level."""
    out = {}
    for c in countries:
        sub = df[df["country"] == c]
        if col not in sub.columns:
            out[c] = None
            continue
        vc = sub[col].value_counts(dropna=False)
        tot = int(vc.sum())
        rows = []
        for cat, n in vc.items():
            # repr(), not str() -- the whole point is to expose 1.0 vs 1 vs "1".
            rows.append((repr(cat), int(n), 100.0 * n / tot if tot else 0.0))
        rows.sort(key=lambda r: (-r[1], r[0]))
        out[c] = rows
    return out


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else None

    df = pd.read_parquet(src)
    # One row per DIARY, not per episode: a stratum field is a property of the
    # diarist, and episode counts would weight it by how talkative the diary is.
    # A DIARY is (country, pid, diary_day). `hid` is the HOUSEHOLD and `pid`
    # alone is the PERSON -- deduplicating on either collapses several diaries
    # into one and silently reweights every stratum share.
    for cand in (["country", "pid", "diary_day"], ["country", "pid"], ["pid"]):
        if all(c in df.columns for c in cand):
            key = cand
            break
    else:
        key = None
    if key is not None:
        n_before = len(df)
        df = df.drop_duplicates(subset=key)
        key = "+".join(key)
    else:
        n_before = len(df)
    countries = sorted(df["country"].unique().tolist())

    buf = []
    w = buf.append
    w("=== 4J prefix-field category shares, by country (DIARY level) ===")
    w("source: %s" % src)
    w("unit:   one row per %s  (%d diaries from %d episodes)"
      % (key or "EPISODE -- no diary key found, READ WITH CARE", len(df), n_before))
    w("n:      %s" % ", ".join("%s=%d" % (c, int((df["country"] == c).sum()))
                               for c in countries))
    w("")
    w("Categories are printed with repr(), so 1 / 1.0 / '1' look different here")
    w("BECAUSE THEY ARE DIFFERENT. An empty list means the field is absent or")
    w("all-null for that country. Not a gate -- read it, do not trust it.")
    w("")

    for col in PREFIX + ALSO:
        present = col in df.columns
        w("--- Field: %s%s" % (col, "" if present else "   [NOT IN CORPUS]"))
        if not present:
            w("    absent from harmonised.parquet in all countries")
            w("")
            continue
        s = shares(df, col, countries)
        # the union of categories, so a country missing one is visible as a gap
        allcats = []
        for c in countries:
            for cat, _, _ in (s[c] or []):
                if cat not in allcats:
                    allcats.append(cat)
        for c in countries:
            rows = s[c]
            if not rows:
                w("  %-3s: []" % c)
                continue
            w("  %-3s: [%s]" % (c, ", ".join("%s: %.2f%%" % (cat, pct)
                                             for cat, n, pct in rows)))
        missing = {c: [x for x in allcats if x not in [r[0] for r in (s[c] or [])]]
                   for c in countries}
        flag = {c: v for c, v in missing.items() if v}
        if flag:
            w("  !! category present in some countries and ABSENT in others:")
            for c, v in sorted(flag.items()):
                w("     %-3s missing %s" % (c, ", ".join(v)))
        # dtype split detector: the same field carrying different python types
        types = {}
        for c in countries:
            for cat, _, _ in (s[c] or []):
                types.setdefault(c, set()).add(
                    "float" if cat.replace(".", "", 1).replace("-", "", 1).isdigit()
                    and "." in cat else
                    "int" if cat.lstrip("-").isdigit() else
                    "str" if cat.startswith(("'", '"')) else "other")
        allt = set()
        for v in types.values():
            allt |= v
        if len(allt) > 1:
            w("  !! DTYPE SPLIT: %s" % "; ".join("%s=%s" % (c, "/".join(sorted(v)))
                                                 for c, v in sorted(types.items())))
        w("")

    # The one cross-tab the precedent would have caught: age band x econ status.
    if "strat_age_band" in df.columns and "strat_econ_status" in df.columns:
        w("--- Cross-tab: strat_econ_status within strat_age_band (FINDING 48)")
        w("    Printed because a UNIVARIATE view cannot show a country fingerprint")
        w("    that lives in a PAIR. A band whose econ value is one category in")
        w("    each country, with no overlap, is a LOCO leak, not a coincidence.")
        w("")
        for band in ["11-14", "75+"]:
            sub = df[df["strat_age_band"] == band]
            if not len(sub):
                continue
            w("  band %s:" % band)
            for c in countries:
                ss = sub[sub["country"] == c]
                if not len(ss):
                    w("    %-3s: []" % c)
                    continue
                vc = ss["strat_econ_status"].value_counts(dropna=False)
                tot = int(vc.sum())
                top = ", ".join("%s: %d/%d = %.1f%%" % (repr(k), int(v), tot,
                                                        100.0 * v / tot)
                                for k, v in vc.items())
                w("    %-3s: %s" % (c, top))
            w("")

    text = "\n".join(buf) + "\n"
    if dst:
        io.open(dst, "w", encoding="utf-8", newline="\n").write(text)
        print("written: %s (%d lines)" % (dst, len(buf) + 1))
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
