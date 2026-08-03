#!/bin/bash
# 3J Leg-3 -- P4 diagnostic. Arm E residential DHW came in at +51.40 % against a pre-registered
# +8..+18 %, i.e. ABOVE the +40.8 % T9-11 blow-up that T9-13 was written to replace.
#
# Before calling that a defect or a result, the question is arithmetic: volume scales as
# P_i * mean_d r_i(d) (the R in Peak_Flow_Rate' = P*R cancels against the /R in f_new), so a +51 %
# total means the POPULATION-WEIGHTED MEAN of residential r is ~1.51. The residential reference is
# a single global scalar per day type (wd 0.635497 / we 0.732074, Y2022), so under a well-posed
# ratio the mean of r should be (2030 residential occupancy mean) / (2022 mean) -- and a 51 % rise
# in a DAILY-MEAN occupancy that already includes sleeping hours is not physically available.
#
# Two candidate explanations this probe separates:
#   (a) the DISTRIBUTION is skewed -- a minority of households carry very large r and dominate the
#       volume sum. Then the mean r is high but the median is near 1.
#   (b) the whole distribution is shifted -- median r is also ~1.5. Then it is not a tail effect,
#       it is the ratio itself being mis-posed (a scale/normalisation mismatch between the 2030
#       residential product and the Y2022 reference it is divided by).
# These predict different tables, so the probe can distinguish them rather than confirm either.
#SBATCH --job-name=3J_L3_residr
#SBATCH -p ps
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/step8_4split/campaign/logs/residr_%j.out

CAMP=/speed-scratch/o_iseri/step8_4split/campaign
CDIR=$CAMP/out_E_dhwvol/campaign_56d6e324
PY=/speed-scratch/o_iseri/envs/step4/bin/python

echo "### residential r distribution, arm E, one representative cell per bundle"
for TAG in B_cons__Tall__MTL B_central__Tall__MTL B_opt__Tall__MTL Y2022__Tall__MTL; do
  P=$CDIR/$TAG/injected.idf.provenance.txt
  if [ ! -f "$P" ]; then echo "  MISSING $TAG"; continue; fi
  echo "  -- $TAG"
  grep "^t9_13 residential " "$P" \
    | sed 's/.*r_wd=\([0-9.]*\) r_we=\([0-9.]*\).*/\1 \2/' \
    | $PY -c "
import sys, statistics as st
wd, we = [], []
for line in sys.stdin:
    p = line.split()
    if len(p) != 2: continue
    wd.append(float(p[0])); we.append(float(p[1]))
if not wd:
    print('    no residential t9_13 lines parsed'); raise SystemExit
def rep(name, v):
    v = sorted(v); n = len(v)
    q = lambda f: v[min(n-1, int(f*n))]
    print(f'    {name}: n={n}  mean={sum(v)/n:.4f}  median={st.median(v):.4f}  '
          f'p10={q(0.10):.4f}  p90={q(0.90):.4f}  max={v[-1]:.4f}  '
          f'frac>2={sum(1 for x in v if x>2)/n:.3f}')
rep('r_wd', wd); rep('r_we', we)
print(f'    mean of max(r_wd,r_we) = {sum(max(a,b) for a,b in zip(wd,we))/len(wd):.4f}')
"
done

echo
echo "### the 2 D2 violations in full, with surrounding context"
grep -h "^t9_13_VIOLATION" $CDIR/*/injected.idf.provenance.txt | sort -u

echo
echo "### the 6 cells whose audit did NOT pass, and their audited counts"
for D in $CDIR/*/; do
  P=$D/injected.idf.provenance.txt
  [ -f "$P" ] || continue
  L=$(grep "^t9_13_audit_pass=" "$P")
  case "$L" in *=True*) ;; *) echo "  $(basename $D): $L" ;; esac
done

echo
echo "### distribution of n_audited across all 56 cells (24/56 had exactly 47)"
grep -h "^t9_13_audit_pass=" $CDIR/*/injected.idf.provenance.txt \
  | sed 's/.*\(n_audited=[0-9]*\).*/\1/' | sort | uniq -c | sort -rn
