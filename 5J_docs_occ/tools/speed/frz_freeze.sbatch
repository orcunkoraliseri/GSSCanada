#!/bin/bash
#SBATCH -J frz_freeze
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=4G
#SBATCH -o /speed-scratch/o_iseri/5J/freeze/logs/freeze_%j.out
# Manager freeze, 2026-09-30. Uploaded first: gates_frozen.md.new, 5thJ_04_scorer.py.new (comment line 48 only).
# Order: keep old copies; show the scorer diff; sources check must PASS (gates 1.1, 1.2) else stop with exit 3 and NO lock file;
# test list refused BEFORE (val 4.2 first half); write the lock file; test lists open AFTER (names only, counts; no run file read).
PY=/speed-scratch/o_iseri/envs/step4/bin/python
F=/speed-scratch/o_iseri/5J/freeze; LOCK=/speed-scratch/o_iseri/5J/gates_frozen.md5
cd $F || exit 2
[ -e $LOCK ] && { echo "LOCK already exists, stop"; exit 4; }
mkdir -p $F/prefreeze && cp -p gates_frozen.md 5thJ_04_scorer.py prefreeze/ && echo "OLD copies kept in prefreeze/"
echo "== scorer diff (expect line 48 comment only)"; diff 5thJ_04_scorer.py 5thJ_04_scorer.py.new; echo "diff exit $?"
mv 5thJ_04_scorer.py.new 5thJ_04_scorer.py && mv gates_frozen.md.new gates_frozen.md
echo "== sources check"; $PY -u $F/5thJ_04_scorer.py --mode sources --sources $F/gates_frozen.md | tee sources_freeze.txt
grep -q "1.1.*PASS" sources_freeze.txt && grep -q "1.2.*PASS" sources_freeze.txt || { echo "GATE 1.1/1.2 not both PASS: NO FREEZE"; exit 3; }
echo "== BEFORE: a test list must be refused"
$PY -u -c "
import sys; sys.path.insert(0, '$F'); import split_loader as L
try: L.load_split('test_new_households'); print('BEFORE opened (WRONG)')
except PermissionError as e: print('BEFORE refused:', e)"
cd $F && md5sum gates_frozen.md 5thJ_04_scorer.py split_loader.py > $LOCK && chmod 444 $LOCK
echo "== LOCK written"; ls -la $LOCK; cat $LOCK
echo "== AFTER: test lists open (run id names only, counts)"
$PY -u -c "
import sys; sys.path.insert(0, '$F'); import split_loader as L
for n in ('test_new_households','test_new_buildings','test_both_new','b0_test','unused'):
    print('AFTER', n, 'opened, run ids', len(L.load_split(n)))"
echo "FREEZE DONE"; exit 0
