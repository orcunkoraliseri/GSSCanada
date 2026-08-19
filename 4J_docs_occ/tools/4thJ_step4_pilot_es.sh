#!/bin/bash
#SBATCH --job-name=4J_s4_pilot_es
#SBATCH --partition=ps
#SBATCH --gres=gpu:1
#SBATCH --mem=64G
#SBATCH --cpus-per-task=4
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/4J_step4_pilot_es_%j.out

# Step 4, work item 4.2 -- LEG-4 PILOT, FOLD 1 (held-out SPAIN), AND THE WHOLE CHAIN.
#
# "Run fold 1 of Leg-4 to completion and read it before submitting the other two. The
#  pilot exists to find wiring defects, and finding one after three jobs have run costs
#  three jobs." -- 4thJ_04_finetuneLLM.md section 4.2
#
# The success criterion is NOT a metric. It is that every detector in 4.4 fires when it
# should and stays silent when it should not.
#
# This job now runs the full chain in one submission -- train, save the adapter, then the
# conditioning diagnostics (G4.3, G4.4, G4.12) and the generation-side perturbations --
# because each stage needs the artefact the previous stage writes, and three separate
# jobs would each queue behind the same shared GPU.

set -x
ENVDIR=/speed-scratch/o_iseri/envs/step4
export HF_HOME=/speed-scratch/o_iseri/hf_cache
export PIP_CACHE_DIR=/speed-scratch/o_iseri/pip_cache
export TMPDIR=/speed-scratch/o_iseri/tmp
export TOKENIZERS_PARALLELISM=false
# FINDING 2: the 20 GB MIG slice is SHARED with other users' processes, so the memory
# available to this job is not ours to predict.
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

cd /speed-scratch/o_iseri

"$ENVDIR/bin/python" -m py_compile 4thJ_step4_train.py 4thJ_step4_diagnostics.py \
    4thJ_step4_genperturb.py 4thJ_step4_perturbtable.py
if [ $? -ne 0 ]; then
    echo "SYNTAX ERROR -- pilot not started"
    exit 1
fi

export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

RUNDIR=/speed-scratch/o_iseri/4J_step4/runs
ADAPTER=$RUNDIR/leg4_pilot_fold_es/adapter

# --- 1. train ---------------------------------------------------------------
# gen-stratified-k 6: G4.1 needs N >= 100 generated diaries in >= 5 strata (V4.a), and a
# random draw cannot deliver that at any volume this project can afford (FINDING 8).
"$ENVDIR/bin/python" -u 4thJ_step4_train.py \
    --fold es --leg 4 --run-type pilot \
    --epochs 2 --limit-train 4000 \
    --gen-stratified-k 6 --gen-batch 8 \
    --batch-size 1 --grad-accum 16 --eval-batch-size 4 --max-len 1280 \
    --out "$RUNDIR"

if [ ! -d "$ADAPTER" ]; then
    echo "NO ADAPTER AT $ADAPTER -- the diagnostics cannot run and this job stops here."
    exit 1
fi

# --- 2. conditioning diagnostics: G4.3, G4.4, G4.12 -------------------------
"$ENVDIR/bin/python" -u 4thJ_step4_diagnostics.py \
    --fold es --leg 4 --run-type pilot --adapter "$ADAPTER" \
    --gen-stratified-k 6 --gen-batch 8 --ce-n 256 --max-len 1280

# --- 3. generation-side perturbations ---------------------------------------
GEN=/speed-scratch/o_iseri/4J_step4/diagnostics/generated_pilot_es.jsonl
if [ -s "$GEN" ]; then
    "$ENVDIR/bin/python" -u 4thJ_step4_genperturb.py \
        --fold es --generated "$GEN" --perturbation all
else
    echo "NO GENERATED FILE AT $GEN -- generation-side perturbations skipped, and this "
    echo "is recorded as a gap, not as a pass."
fi

# The pre-registration is untouched by any of the above. Proved, not assumed.
md5sum /speed-scratch/o_iseri/4J_step4/prereg.md
cat /speed-scratch/o_iseri/4J_step4/prereg.md.md5
