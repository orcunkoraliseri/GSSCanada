#!/bin/bash
#SBATCH --job-name=4J_s4_g42ds44
#SBATCH --partition=ps
#SBATCH --gres=gpu:nvidia_a100_2g.20gb:1
#SBATCH --mem=64G
#SBATCH --cpus-per-task=4
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/4J_step4_g42ds44_%j.out

# D-S4-4 -- re-score `G4.2` on the FORCED-DELIMITER basis. Two arms, nothing else.
#
# WHY ONLY TWO RUNS AND NOT THE WHOLE BATTERY. D-S4-4 re-points exactly one number,
# `delimiter_loss`, and exactly one gate reads it, `G4.2`. `content_loss` is deliberately
# unchanged on both bases, so `G4.9` -- which is seen falling and credited in DoD item 6 --
# is scored on the same input it was scored on before, and re-running it would only invite
# a re-reading of a verdict the ruling never touched. The other nine perturbations are in
# the same position. Re-running them would burn GPU hours to reproduce numbers that cannot
# have moved, and every reproduction is a chance to accidentally overwrite one that did.
#
# 🔴 SEPARATE run directory, for the reason the battery gives at its own G4.2 block: the
# pre-ruling detectors in runs_g42_demo/ are the evidence that `0.1022` was ever read, and
# the whole point of the re-run is to put the two bases side by side. Overwriting the old
# reading with the new one destroys the comparison the ruling has to be judged on.
#
# 🔴 IDENTICAL BUDGET, deliberately. `--epochs 2 --limit-train 4000 --gen-n 16` copied from
# 4thJ_step4_perturb_battery.sh's G4.2 block verbatim. If the budget moved as well as the
# basis, a delimiter loss that fell could not be attributed to either.
#
# PRE-REGISTERED OUTCOME, written before submission and not to be edited afterwards.
# Removing the act2 share from the last all-basis reading leaves roughly 0.075, which is
# STILL ABOVE the 0.05 band.
#   ctrl      forced delim ~0.075  -> ABOVE the band -> the demonstration is VOID
#   collapse  gen_entropy ~0.000   -> arm two falls, as it already did
# If the CTRL arm does not cross 0.05 on the forced basis, this run is reported VOID,
# `G4.2` stays in `never made to fall`, and the coverage clause stays FAIL. D-S4-4 makes
# the arm satisfiable in principle; it was never claimed to make it pass, and a pass that
# arrived only because the token set moved would be the band change this project refuses.
#
# KNOWN COLLATERAL, quoted with the lever every time it is used: `collapse_content` also
# fells `G4.9` at 4,000 records and above (FINDING 26). Dose-dependent, expected, declared.
#
# FINDING 2: ONE of our GPU jobs at a time. Check `squeue -u $USER` before submitting.

set -x
ENVDIR=/speed-scratch/o_iseri/envs/step4
export HF_HOME=/speed-scratch/o_iseri/hf_cache
export PIP_CACHE_DIR=/speed-scratch/o_iseri/pip_cache
export TMPDIR=/speed-scratch/o_iseri/tmp
export TOKENIZERS_PARALLELISM=false
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

cd /speed-scratch/o_iseri

"$ENVDIR/bin/python" -m py_compile 4thJ_step4_train.py 4thJ_step4_perturbtable.py
if [ $? -ne 0 ]; then
    echo "SYNTAX ERROR -- G4.2 re-run not started"
    exit 1
fi

export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

RUNS_DS44=/speed-scratch/o_iseri/4J_step4/runs_g42_ds44
mkdir -p "$RUNS_DS44"
COMMON_DS44="--fold es --leg 4 --run-type perturb --epochs 2 --limit-train 4000 --gen-n 16 --batch-size 1 --grad-accum 16 --max-len 1280 --out $RUNS_DS44"

echo "############ D-S4-4 re-score, arm=ctrl ############"
echo "### watch for the line beginning 'D-S4-4 delim(forced)=' -- if it prints"
echo "### 'NOTHING -- basis unchanged' for the dropped ids, the ruling did not apply"
echo "### and the two arms below are the OLD basis under a new directory name."
"$ENVDIR/bin/python" -u 4thJ_step4_train.py $COMMON_DS44

echo "############ D-S4-4 re-score, arm=collapse ############"
"$ENVDIR/bin/python" -u 4thJ_step4_train.py $COMMON_DS44 --perturbation collapse_content

echo "############ D-S4-4 re-score, read the two arms ############"
"$ENVDIR/bin/python" -u 4thJ_step4_perturbtable.py --runs "$RUNS_DS44" --fold es \
    --out /speed-scratch/o_iseri/4J_step4/g42_ds44_es.txt
echo "NOTE: the coverage clause printed above covers this TWO-RUN re-score ONLY."
echo "The battery's real clause remains perturb_table_train_side_es.txt."
