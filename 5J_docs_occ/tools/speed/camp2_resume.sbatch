#!/bin/bash
#SBATCH -J camp2C
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=8G
#SBATCH -o /speed-scratch/o_iseri/5J/campaign/integrity/resume_%j.out
# Part 2, Part C: resume check (failure class 61) on one real finished task: it_milan_2014 block 5.
R=/speed-scratch/o_iseri/5J/campaign
PY=/speed-scratch/o_iseri/envs/step4/bin/python
ARR=it_milan_2014; BLK=5
cd $R || exit 2
echo "host=$(hostname) start=$(date -Iseconds)"
IDS=$R/integrity/resume_ids.txt
tail -n +2 $R/plan/$ARR/block_$BLK.csv | cut -d, -f1 > $IDS
N=$(wc -l < $IDS)
echo "TASK $ARR block $BLK runs=$N (first $(head -n 1 $IDS), last $(tail -n 1 $IDS))"
case $(head -n 1 $IDS) in it_*) ;; *) echo "not an Italian task, abort"; exit 3;; esac
echo "--- 1 baseline plan"
$PY -u camp_plan.py | grep -E '^PLAN total|^PLAN_ARRAY '
mkdir -p $R/resume_test/done $R/resume_test/extracted/$ARR
while read id; do
  mv $R/done/$id.json $R/done/$id.err $R/resume_test/done/ || echo "MOVE_FAIL $id"
  mv $R/extracted/$ARR/$id.csv.gz $R/extracted/$ARR/$id.dwellings.csv $R/resume_test/extracted/$ARR/ || echo "MOVE_FAIL $id"
done < $IDS
echo "moved: done files $(ls $R/resume_test/done | wc -l) (expect $((2*N))), extracted files $(ls $R/resume_test/extracted/$ARR | wc -l) (expect $((2*N)))"
echo "--- 2 plan with the task's outputs moved away (done must drop by $N, todo rise by $N)"
$PY -u camp_plan.py | grep -E '^PLAN total|^PLAN_ARRAY '
sort $R/plan/todo_ids.txt > $R/integrity/todo_sorted.txt
sort $IDS > $R/integrity/ids_sorted.txt
if cmp -s $R/integrity/todo_sorted.txt $R/integrity/ids_sorted.txt; then SAME=YES; else SAME=NO; fi
echo "todo_ids.txt lines $(wc -l < $R/plan/todo_ids.txt); todo ids equal the task's ids: $SAME"
while read id; do
  mv $R/resume_test/done/$id.json $R/resume_test/done/$id.err $R/done/ || echo "BACK_FAIL $id"
  mv $R/resume_test/extracted/$ARR/$id.csv.gz $R/resume_test/extracted/$ARR/$id.dwellings.csv $R/extracted/$ARR/ || echo "BACK_FAIL $id"
done < $IDS
echo "moved back: resume_test/done left $(ls $R/resume_test/done | wc -l), resume_test/extracted left $(ls $R/resume_test/extracted/$ARR | wc -l); done/ now $(ls $R/done | wc -l)"
echo "--- 3 plan after moving back"
$PY -u camp_plan.py | grep -E '^PLAN total|^PLAN_ARRAY '
echo "todo_ids.txt lines $(wc -l < $R/plan/todo_ids.txt)"
echo "end=$(date -Iseconds)"
