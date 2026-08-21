# -*- coding: utf-8 -*-
"""
4J / Step 5.1 -- APPLY `D-S5-9` (a): put `marginals_it.csv`'s HOUSEHOLD-basis
`strat_hh_type` rows on CONVENTION A.

WHY THIS IS A SEPARATE FILE FROM THE BUILDER
============================================
`4thJ_step5_build_it_microdata.py` only ever EMITS into `outputs_step5/`. This
module is the only thing in Step 5 that MUTATES an already-shipped marginal, and
that difference is worth a file boundary: a reader can see, without reading any
code, exactly which script is allowed to change a file that other steps consume.

WHAT IS BEING CHANGED AND WHY
=============================
`marginals_it.csv` carried its `strat_hh_type` household rows from Eurostat
`cens_11htts_r2`, a FULL COUNT. Eurostat classifies a household holding a family
nucleus PLUS other resident people under its nucleus's type -- CONVENTION B.
ONS (`QS112UK`) and INE put it in `other_complex` -- CONVENTION A -- and the UK
cannot express B at all, because `QS112UK` publishes "Other household types" as
one indivisible class.

`FINDING 60`: `es` and `uk` were on A and `it` on B, in already-shipped files,
and nothing had ever compared them. Convention A was adopted for the PERSON
files, which is what the `G6.1` rake consumes. That left Italy's own household
table contradicting Italy's own person table. `D-S5-9` was ruled (a): rebuild
the household rows on A from the ISTAT 1 % microdata.

WHAT IT COSTS, AND THE COST IS NOT HIDDEN
=========================================
The five rows stop being a full count. They become a 1 % self-weighting sample
estimate. Their accuracy is not asserted: the same sample, tabulated on
convention B, reproduces the Eurostat full count to within 1.49 % on its worst
category, and that like-for-like score is recomputed on every build.

WHAT IT DOES NOT TOUCH
======================
Every other row of `marginals_it.csv` -- age, sex, economic status -- is left
BYTE-IDENTICAL, and that is verified after the write rather than intended before
it. `11-14` in particular keeps its published-table derivation, because
`ETA_CLASSI` bottoms out at "0-14" and the band cannot be recovered from the
microdata at any price.

`econ_11plus_it.csv` is NOT touched either. `D-S5-7`'s basis effect measured
0.178 pp, but this sample's own noise against the published tract table measured
0.207 pp -- larger than the effect it would correct -- so rewriting it would
trade a known signed bias for a bigger unsigned random one.
"""

import io
import os
import sys
import csv
import shutil
import hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'Step5_docs', 'outputs_step5')
TARGET = os.path.join(OUT, 'marginals_it.csv')
SOURCE = os.path.join(OUT, 'hhtype_household_it.csv')
BACKUP = TARGET + '.bak_dS59'

FIELD = 'strat_hh_type'
CATS = ['one_person', 'couple_no_children', 'couple_with_children',
        'single_parent_with_children', 'other_complex', 'unknown']


class ApplyError(Exception):
    pass


def need(cond, msg):
    if not cond:
        raise ApplyError(msg)


def say(*a):
    sys.stdout.write(' '.join(str(x) for x in a) + '\n')


def md5(path):
    h = hashlib.md5()
    fh = open(path, 'rb')
    while True:
        b = fh.read(1 << 20)
        if not b:
            break
        h.update(b)
    fh.close()
    return h.hexdigest()


def read_rows(path):
    """Return (data_rows, comment_lines). Comment lines start with '#'."""
    out = []
    fh = io.open(path, encoding='utf-8')
    for row in csv.reader(fh):
        if not row or row[0].startswith('#') or row[0] == 'field':
            continue
        out.append(row)
    fh.close()
    return out


def main():
    need(os.path.exists(SOURCE),
         'hhtype_household_it.csv does not exist. Run '
         '4thJ_step5_build_it_microdata.py first -- this module never computes '
         'a marginal, it only installs one.')
    need(os.path.exists(TARGET), 'marginals_it.csv does not exist')

    before_md5 = md5(TARGET)
    say('marginals_it.csv md5 before  %s' % before_md5)

    # ---- backup, and VERIFY it before the original is touched -------------
    shutil.copyfile(TARGET, BACKUP)
    need(os.path.getsize(BACKUP) > 0, 'backup %s is empty' % BACKUP)
    need(md5(BACKUP) == before_md5,
         'backup md5 does not match the original; refusing to write')
    say('backup written and verified  %s' % os.path.basename(BACKUP))

    # ---- the replacement rows ---------------------------------------------
    new = {}
    for row in read_rows(SOURCE):
        need(row[0] == FIELD,
             'hhtype_household_it.csv carries field %r' % row[0])
        new[row[1]] = row
    need(sorted(new) == sorted(CATS),
         'hhtype_household_it.csv categories %r != %r'
         % (sorted(new), sorted(CATS)))

    # ---- rewrite, line by line, preserving everything else verbatim -------
    src_lines = io.open(TARGET, encoding='utf-8', newline='').readlines()
    out_lines = []
    seen = []
    for ln in src_lines:
        if ln.startswith(FIELD + ','):
            cat = ln.split(',')[1]
            need(cat in new, 'marginals_it.csv has an unexpected %s category '
                             '%r' % (FIELD, cat))
            need(cat not in seen, '%s appears twice' % cat)
            seen.append(cat)
            row = new[cat]
            # csv.writer, not string join: the derivation field contains commas
            # and must stay quoted exactly as the writer would quote it.
            buf = io.StringIO()
            csv.writer(buf, lineterminator=u'\n').writerow(row)
            out_lines.append(buf.getvalue())
        else:
            out_lines.append(ln)
    need(sorted(seen) == sorted(CATS),
         'marginals_it.csv held %s rows %r, expected %r' % (FIELD, seen, CATS))
    need(len(out_lines) == len(src_lines),
         'line count changed %d -> %d' % (len(src_lines), len(out_lines)))
    io.open(TARGET, 'w', encoding='utf-8', newline='').write(u''.join(out_lines))

    # ---- verify AFTER the write, against the file on disk -----------------
    # 1. every non-strat_hh_type line is byte-identical to the backup
    bk = io.open(BACKUP, encoding='utf-8', newline='').readlines()
    now = io.open(TARGET, encoding='utf-8', newline='').readlines()
    need(len(bk) == len(now), 'line count differs from the backup')
    changed = 0
    for a, b in zip(bk, now):
        if a.startswith(FIELD + ','):
            changed += 1
            continue
        need(a == b, 'a line outside %s changed:\n  was %r\n  now %r'
                     % (FIELD, a, b))
    need(changed == len(CATS),
         'expected exactly %d changed lines, saw %d' % (len(CATS), changed))
    say('%d rows replaced; every other line byte-identical to the backup'
        % changed)

    # 2. the field, as written, is a partition
    tot_share = 0.0
    tot_count = 0
    base = None
    for row in read_rows(TARGET):
        if row[0] != FIELD:
            continue
        tot_share += float(row[3])
        tot_count += int(row[2])
        if base is None:
            base = int(row[5])
        need(int(row[5]) == base,
             '%s rows disagree on base_count' % FIELD)
    need(abs(tot_share - 1.0) < 1e-7,
         '%s shares AS WRITTEN sum to %.12f; rake() refuses beyond 1e-6'
         % (FIELD, tot_share))
    need(tot_count == base,
         '%s counts sum to %d but base_count is %d' % (FIELD, tot_count, base))
    say('shares sum to %.12f, counts sum to base_count %d' % (tot_share, base))

    # ---- what moved --------------------------------------------------------
    was = {}
    for row in read_rows(BACKUP):
        if row[0] == FIELD:
            was[row[1]] = (int(row[2]), float(row[3]))
    say('--- D-S5-9 (a) applied: convention B -> convention A ---')
    say('  %-30s %12s %12s %10s' % ('category', 'was', 'now', 'change pp'))
    for c in CATS:
        w = was.get(c, (0, 0.0))
        n = new[c]
        say('  %-30s %12d %12d %+10.3f'
            % (c, w[0], int(n[2]), 100.0 * (float(n[3]) - w[1])))
    say('marginals_it.csv md5 after   %s' % md5(TARGET))
    say('OK')


if __name__ == '__main__':
    try:
        main()
    except ApplyError as e:
        sys.stderr.write('REFUSED: %s\n' % e)
        sys.exit(1)
