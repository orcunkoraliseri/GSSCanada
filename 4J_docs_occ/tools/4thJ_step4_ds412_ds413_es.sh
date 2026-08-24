#!/bin/bash
#SBATCH --job-name=4J_s4_ds412_13
#SBATCH --partition=ps
#SBATCH --gres=gpu:nvidia_a100_7g.80gb:1
#SBATCH --mem=192G
#SBATCH --cpus-per-task=8
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/4J_s4_ds412_13_%j.out

# D-S4-12 + D-S4-13 -- the single combined job the author's execution order asks for.
#   usage: sbatch 4thJ_step4_ds412_ds413_es.sh          # fold es, Leg-5 adapter
#
# Three measurements, in the order they can invalidate each other:
#
#   ARM (a)  D-S4-12  G4.4 SCORER STABILITY. CPU only, no model. Re-scores the PRE-repair
#            generated set kept as a control. PREDICTION: evening ratio 0.544 +/- 0.01.
#            Runs FIRST because if the scorer is not stable, arm (b) measures nothing.
#   ARM (b)  D-S4-12  G4.4 SAMPLING SPREAD. Re-generates from the EXISTING Leg-5 adapter
#            under a SECOND seed. PREDICTION: spread < 0.10, which would leave H1 (the
#            eos_token_id repair changed the text) as the explanation of the FAIL -> PASS.
#   D-S4-13  G4.6 MERGE PARITY IN FLOAT32 on the SAME 48 prompts as the bf16 run. If
#            parity is restored, the divergence is bf16 truncation (C1); if it is not, a
#            structural merge defect (C2) survives.
#
# 🔴 NOTHING HERE IS A GATE VERDICT and nothing re-trains. The adapter is read, never
# written. `4thJ_step4_thresholds.py` and `prereg.md` are FROZEN and only read; the md5 of
# the prereg is printed at the end exactly as the fold runs do.
#
# 🔴 The bf16 merge-parity result is NOT overwritten: --out names a separate file.

set -x
FOLD=es
LEG=5
ADAPTER=/speed-scratch/o_iseri/4J_step4/runs_leg5/leg5_primary_fold_${FOLD}/adapter
[ -d "$ADAPTER" ] || { echo "no adapter at $ADAPTER"; exit 1; }

S4=/speed-scratch/o_iseri/4J_step4
ENVDIR=/speed-scratch/o_iseri/envs/step4
PY=$ENVDIR/bin/python
export HF_HOME=/speed-scratch/o_iseri/hf_cache
export TMPDIR=/speed-scratch/o_iseri/tmp
export TOKENIZERS_PARALLELISM=false

cd /speed-scratch/o_iseri
$PY -m py_compile 4thJ_step4_ds412_g44_rescore.py 4thJ_step4_diagnostics.py 4thJ_step4_g46_merge_parity.py || exit 1

# ---------------------------------------------------------------- ARM (a)
# The pre-repair set is scored FIRST (the stability call is made on the first file), the
# post-repair set second so both readings sit in one artefact.
PRE=$S4/diagnostics_leg5/generated_primary_${FOLD}.jsonl
POST=$S4/diagnostics_leg5_ds48/generated_primary_${FOLD}.jsonl
[ -s "$PRE" ]  || { echo "missing pre-repair control $PRE";  exit 1; }
[ -s "$POST" ] || { echo "missing post-repair set $POST";    exit 1; }
$PY -u 4thJ_step4_ds412_g44_rescore.py --fold $FOLD \
    --generated "$PRE" "$POST" \
    --out $S4/ds412_arm_a_g44_scorer_stability_${FOLD}.json || exit 1

# ---------------------------------------------------------------- ARM (b)
# Second seed, everything else identical: same adapter, same stratified draw size, same
# max length. The seed is DECLARED here, not chosen after seeing the result.
SEED2=20260824
OUTB=$S4/diagnostics_ds412_seed${SEED2}
mkdir -p $OUTB
$PY -u 4thJ_step4_diagnostics.py --fold $FOLD --run-type primary --leg $LEG \
    --adapter $ADAPTER --gen-n 600 --gen-stratified-k 6 --gen-batch 8 \
    --seed $SEED2 --out $OUTB || exit 1

# re-score BOTH seeds through the same scorer so the spread is a like-for-like difference
$PY -u 4thJ_step4_ds412_g44_rescore.py --fold $FOLD \
    --generated "$POST" "$OUTB/generated_primary_${FOLD}.jsonl" --mode spread \
    --out $S4/ds412_arm_b_g44_seed_spread_${FOLD}.json || exit 1

# ---------------------------------------------------------------- D-S4-13
$PY -u 4thJ_step4_g46_merge_parity.py --fold $FOLD --leg $LEG --adapter $ADAPTER \
    --n 48 --gen-batch 4 --max-new-tokens 1200 --dtype float32 \
    --out $S4/g46_merge_parity_leg${LEG}_${FOLD}_float32.json || exit 1

md5sum $S4/prereg.md
cat $S4/prereg.md.md5
md5sum $S4/../4thJ_step4_thresholds.py 2>/dev/null || md5sum /speed-scratch/o_iseri/4thJ_step4_thresholds.py
