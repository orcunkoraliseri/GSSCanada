#!/bin/bash
#SBATCH --job-name=4J_s4_qwen
#SBATCH --partition=ps
#SBATCH --gres=gpu:nvidia_a100_7g.80gb:1
#SBATCH --mem=192G
#SBATCH --cpus-per-task=8
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/4J_step4_qwen_%j.out

# Step 4 -- THE COMPARISON ARM. `Qwen/Qwen2.5-7B`, the SAME recipe, ONE pre-named fold.
#   usage: sbatch 4thJ_step4_qwen_fold.sh [fold]        # default es
#
# 🔴 PRE-REGISTERED, NOT OPTIONAL. `Step6_docs/outputs_step6/prereg.md`: the pre-named
# fold "is used for exactly two single-fold measurements -- the ceiling run (full
# fine-tune, 8-bit AdamW) and the comparison arm (`Qwen/Qwen2.5-7B`) -- and BOTH MUST BE
# REPORTED AS SINGLE-FOLD. Quoting either as a general result across the corpus would be
# quoting one fold as three." The ceiling landed 2026-08-26 (job 1287378). This is the
# other one.
#
# 🔴 WHAT IT ANSWERS, AND WHAT IT DOES NOT. `4thJ_04_finetuneLLM.md:62`: it "states what
# the alternative backbone cost". It is NOT a gate, it carries NO G4.x id, and no number
# from it may be written up as one. `RL18` recommended Qwen and was wrong twice (a
# mis-counted token figure and a Llama licence clause that does not exist); Qwen was
# RETAINED as the named comparison arm rather than discarded, so the paper can report what
# the alternative would have cost instead of asserting it.
#
# 🔴 SAME RECIPE, DELIBERATELY. LoRA r=32 rsLoRA on all seven projections, bf16, 3 epochs,
# effective batch 2 x 8 = 16, `--max-len 1280` -- every one of them identical to
# `4thJ_step4_leg5_fold.sh`. None of it is re-tuned for Qwen. Re-tuning any of it would
# make this a comparison of two schedules instead of two backbones, which is the one thing
# the arm exists not to be.
#
# 🔴 AND THE ONE PLACE THAT ASSUMPTION IS FRAGILE -- READ THE TRUNCATION LINE.
# Qwen tokenises the same diary at about 1.5x the length: 303 tokens against OLMo's 200,
# and the `311` marker at 3 tokens against 1 (`4thJ_04_finetuneLLM.md:97`). The trainer
# slices `(prefix + body)[:max_len]` SILENTLY. `--max-len 1280` should clear a ~790-token
# worst case with room, but "should" is not a measurement, so the trainer now COUNTS
# truncated records and prints
#     TRUNCATION train tokenizer=Qwen/Qwen2.5-7B max_len=1280 : N of M records truncated
# for every run, OLMo arms included, so this arm has a baseline to be read against.
# 🔴 IF N IS NOT 0 THE LOSS COMPARISON IS CONTAMINATED and must be reported with the
# truncation rate beside it. Do NOT silently raise `--max-len` to make N zero -- that
# changes the recipe and breaks the comparison in the other direction. It is a decision
# for the author, not for a launcher.
#
# 🔴 G4.2's DELIMITER BASIS IS TOKENIZER-DEPENDENT. `delimiter_token_ids()` is computed
# from whichever tokenizer is loaded, so this arm's delimiter/content split is measured on
# Qwen's vocabulary and is NOT numerically comparable to the OLMo arms' G4.2 readings.
# The VERDICT is comparable; the numbers are not. Same discipline as the ceiling run.
#
# 🔴 G4.8 asserts tokenizer IDENTITY against the base checkpoint first (`D-S4-2`), so it
# asserts Qwen's tokenizer here. A PASS means "this really is the Qwen tokenizer", not
# "this matches OLMo".
#
# The backbone and its revision are resolved by the trainer from `staged_weights.json`
# (`Qwen/Qwen2.5-7B` @ d149729398750b98c0af14eb82c78cfe92750796, role `comparison_arm`,
# 14.196 GiB, 4 safetensors), never from this file.
#
# LoRA in bf16, no quantisation, therefore NO `bitsandbytes` and `envs/step4` is untouched
# -- only the `ceiling` run-type ever needed it.

set -x
FOLD=${1:-es}

# 🔴 The fold is PRE-NAMED. `es` was fixed 2026-08-14, before any fold trained, and it did
# not move when France left the corpus. A second argument is accepted so a deliberate
# off-registration run is possible, but it is refused by default: an arm silently run on a
# different fold from the ceiling is not a comparison of backbones either.
if [ "$FOLD" != "es" ]; then
    echo "🔴 REFUSING fold '$FOLD'. The comparison arm is pre-registered on the pre-named"
    echo "   fold 'es' (prereg.md), the same fold the ceiling ran on. Running it elsewhere"
    echo "   is a NEW registered decision, not a launcher flag. If that decision has been"
    echo "   made, record it first and then edit this guard."
    exit 1
fi

ENVDIR=/speed-scratch/o_iseri/envs/step4
RUNDIR=/speed-scratch/o_iseri/4J_step4/runs_leg5_qwen
DIAG=/speed-scratch/o_iseri/4J_step4/diagnostics_leg5_qwen

export HF_HOME=/speed-scratch/o_iseri/hf_cache
export PIP_CACHE_DIR=/speed-scratch/o_iseri/pip_cache
export TMPDIR=/speed-scratch/o_iseri/tmp
export TOKENIZERS_PARALLELISM=false
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

cd /speed-scratch/o_iseri

"$ENVDIR/bin/python" -m py_compile 4thJ_step4_train.py 4thJ_step4_diagnostics.py \
    4thJ_step4_genperturb.py
if [ $? -ne 0 ]; then
    echo "SYNTAX ERROR -- qwen arm not started"
    exit 1
fi

export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

mkdir -p "$RUNDIR" "$DIAG"

# 🔴 `--out` is REDIRECTED for the same reason the Leg-5 folds redirect it:
# `4thJ_step4_diagnostics.py:413` names its output `generated_<run_type>_<fold>.jsonl`
# with no leg and no backbone in the filename. `runs_leg5_qwen` / `diagnostics_leg5_qwen`
# keep this arm off every path the reported Leg-5 folds wrote to -- the cache-key-collision
# class of `FINDING 8`, which has now cost this project twice.
"$ENVDIR/bin/python" -u 4thJ_step4_train.py \
    --fold "$FOLD" --leg 5 --run-type qwen \
    --gen-stratified-k 6 --gen-batch 8 \
    --batch-size 2 --grad-accum 8 --eval-batch-size 4 --max-len 1280 \
    --out "$RUNDIR"
RC=$?
echo "qwen arm training exit status: $RC"

ADAPTER=$RUNDIR/leg5_qwen_fold_$FOLD/adapter
if [ ! -d "$ADAPTER" ]; then
    echo "NO ADAPTER AT $ADAPTER -- diagnostics cannot run. Recorded as a GAP, not a pass."
    exit 1
fi

"$ENVDIR/bin/python" -u 4thJ_step4_diagnostics.py \
    --fold "$FOLD" --leg 5 --run-type qwen --adapter "$ADAPTER" \
    --out "$DIAG" \
    --gen-stratified-k 6 --gen-batch 8 --ce-n 256 --max-len 1280

GEN=$DIAG/generated_qwen_$FOLD.jsonl
if [ -s "$GEN" ]; then
    "$ENVDIR/bin/python" -u 4thJ_step4_genperturb.py \
        --fold "$FOLD" --generated "$GEN" --perturbation all
else
    echo "NO GENERATED FILE AT $GEN -- generation-side perturbations skipped, and that is"
    echo "recorded as a gap, not as a pass."
fi

# The pre-registration is untouched by any of the above. Proving it, not assuming.
md5sum /speed-scratch/o_iseri/4J_step4/prereg.md
cat /speed-scratch/o_iseri/4J_step4/prereg.md.md5
ls -l "$RUNDIR"
