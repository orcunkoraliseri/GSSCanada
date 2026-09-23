#!/bin/bash
# V3 smoke: 3 two-day runs (N, R, U on Tall/MTL) in ONE 1-CPU job, then N-vs-R / U-vs-R / N-vs-U.
# Expect: all three runs status=ok; N vs R PASS; U vs R FAIL (the contract changes lights/equip).
#SBATCH --job-name=3J_V3smoke
#SBATCH -p ps
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/3J_V3/logs/smoke_%j.out
source /speed-scratch/o_iseri/3J_V3/repo/3J_docs_occ_nTemp/writing/implementation/IMP/scripts/V3/v3_env.sh
cd $ROOT && md5sum -c --quiet mirror_md5.txt || { echo "FATAL: upload md5 mismatch (mirror_md5.txt)"; exit 1; }
echo "  [guard OK] all uploaded files match mirror_md5.txt"
cd $CODE || exit 1
echo "node $(hostname) $(date)"; $PY -V
for f in v3_lib.py v3_task.py v3_static.py v3_build_R.py v3_check.py v3_fixtures.py; do
  $PY -m py_compile $f || { echo "FATAL: $f does not compile under $($PY -V 2>&1)"; exit 1; }
done
[ -f "$EPLUS_IDD" ] || { echo "FATAL: no IDD at $EPLUS_IDD"; exit 1; }
RC=0
for t in 0 1 2; do $PY -u v3_task.py $ROOT/tasks_smoke.csv $t $ROOT/runs || RC=1; done
$PY - <<'PYEOF'
import glob, os, sys
sys.path.insert(0, ".")
import v3_check as C
root = "/speed-scratch/o_iseri/3J_V3/runs/smoke"
g = lambda a: (glob.glob(os.path.join(root, a + "__*")) or [None])[0]
for a, b in (("N", "R"), ("U", "R"), ("N", "U")):
    r = C.compare(g(a), g(b))
    print("SMOKE %s vs %s: %s ann=%s hr=%s worst_hr_col=%s" % (a, b, r["status"], r.get("worst_ann"),
          r.get("worst_hourly"), r.get("worst_hourly_col")))
PYEOF
echo "smoke done rc=$RC $(date)"
exit $RC
