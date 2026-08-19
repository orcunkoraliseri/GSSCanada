#!/bin/bash
#SBATCH --job-name=4J_s4_perturb
#SBATCH --partition=ps
#SBATCH --gres=gpu:1
#SBATCH --mem=64G
#SBATCH --cpus-per-task=4
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/4J_step4_perturb_%j.out

# Step 4 -- "EVERY GATE MUST BE SEEN FAILING", the TRAINING-SIDE half.
#
# Eleven short runs on fold es: the null baseline plus ten perturbations. Short is the
# point -- these runs exist to move a detector, not to train a model, so they use a
# 600-record proportional cap and 2 epochs. Two epochs and not one because G4.9 is a
# forgetting gate and a single reading cannot regress from itself.
#
# The generation-side gates (G4.1, G4.3, G4.4, G4.12) are NOT scored here. They need a
# trained adapter and enough generations to satisfy V4.a, and they belong to
# 4thJ_step4_diagnostics.py / 4thJ_step4_genperturb.py.

set -x
ENVDIR=/speed-scratch/o_iseri/envs/step4
export HF_HOME=/speed-scratch/o_iseri/hf_cache
export PIP_CACHE_DIR=/speed-scratch/o_iseri/pip_cache
export TMPDIR=/speed-scratch/o_iseri/tmp
export TOKENIZERS_PARALLELISM=false
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

cd /speed-scratch/o_iseri

# Syntax first. A NameError forty minutes into an eleven-run battery costs the battery.
"$ENVDIR/bin/python" -m py_compile 4thJ_step4_train.py 4thJ_step4_perturbtable.py \
    4thJ_step4_diagnostics.py
if [ $? -ne 0 ]; then
    echo "SYNTAX ERROR -- battery not started"
    exit 1
fi

# The swap_tokenizer perturbation needs a DIFFERENT tokenizer on disk. It is staged here,
# with the network on, BEFORE the offline discipline is imposed -- so no training run is
# ever able to reach out mid-job.
"$ENVDIR/bin/python" -c "from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('bert-base-uncased')"

export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

RUNS=/speed-scratch/o_iseri/4J_step4/runs_perturb
mkdir -p "$RUNS"

COMMON="--fold es --leg 4 --run-type perturb --epochs 2 --limit-train 600 --gen-n 16 --batch-size 1 --grad-accum 16 --max-len 1280 --out $RUNS"

# --- the null baseline FIRST. Nothing below can be scored without it. ---
"$ENVDIR/bin/python" -u 4thJ_step4_train.py $COMMON

# collapse_content added 2026-08-18: G4.2 had no perturbation at all and so sat in the
# coverage clause's `never made to fall` list. It flattens every episode to one constant
# while leaving every delimiter and every <eor> in place, which is the exact condition
# G4.2 halts on (delimiter loss < 0.05 AND activity entropy < 1.5, strict on both arms).
for P in pad_labels_1pct perturb_merged_weight strip_eor_1pct swap_tokenizer \
         collapse_content sequential_countries drop_revision leak_1pct edit_prereg \
         no_prefix freeze_adapter ; do
    echo "############ PERTURBATION $P ############"
    "$ENVDIR/bin/python" -u 4thJ_step4_train.py $COMMON --perturbation "$P"
done

# --- score it ---
echo "############ SCORING ############"
"$ENVDIR/bin/python" -u 4thJ_step4_perturbtable.py --runs "$RUNS" --fold es \
    --out /speed-scratch/o_iseri/4J_step4/perturb_table_train_side_es.txt

# The real pre-registration is untouched by any of the above. Proving it, not assuming it.
md5sum /speed-scratch/o_iseri/4J_step4/prereg.md
cat /speed-scratch/o_iseri/4J_step4/prereg.md.md5

# --- 🔴 FINDING 13: the ONLY demonstration G4.3 and G4.12 can ever get -----------------
#
# Neither gate appears in this battery's ORDER list (they are conditioning gates, scored
# on an adapter) and neither appears in 4thJ_step4_genperturb.py's EXPECTED map (which
# covers G4.1, G4.4 and G4.7). `no_prefix` is the only lever in the project that fells
# them: it trains with an EMPTY prefix, so a prefix shuffle cannot raise cross-entropy
# (G4.3) and a within-stratum permutation cannot degrade anything (G4.12). Until now that
# adapter was thrown away with the other ten, and DoD item 6 would have gone unmet for
# two gates with nothing on the record saying why.
#
# EXPECTED, written before the run and not edited afterwards:
#   G4.3   FAIL   -- no prefix was ever seen, so shuffling it changes nothing
#   G4.12  FAIL   -- ditto, at the within-stratum level
# If either PASSES here, the gate is not measuring conditioning and that is a FINDING.
# Two arms, because one is not a demonstration. Both adapters are trained on the SAME
# 600-record cap, so the null arm answers the question the no_prefix arm cannot: did the
# gate fall because the prefix was removed, or because 600 records condition on nothing?
# G4.3 already read 0.0616 at 4,000 records, so that confound is live, not hypothetical.
NOPFX=$RUNS/leg4_perturb_fold_es__PERTURB_no_prefix/adapter
CTRL=$RUNS/leg4_perturb_fold_es/adapter
for ARM in ctrl nopfx ; do
    if [ "$ARM" = ctrl ]; then AD=$CTRL; else AD=$NOPFX; fi
    if [ ! -d "$AD" ]; then
        echo "NO $ARM ADAPTER AT $AD -- the G4.3 / G4.12 demonstration is INCOMPLETE and"
        echo "DoD item 6 stays UNMET for both gates. This is a gap, not a pass."
        continue
    fi
    echo "############ G4.3 / G4.12 DEMONSTRATION, arm=$ARM ############"
    mkdir -p /speed-scratch/o_iseri/4J_step4/diagnostics_demo_$ARM
    "$ENVDIR/bin/python" -u 4thJ_step4_diagnostics.py \
        --fold es --leg 4 --run-type perturb --adapter "$AD" \
        --out /speed-scratch/o_iseri/4J_step4/diagnostics_demo_$ARM \
        --gen-stratified-k 6 --gen-batch 8 --ce-n 256 --max-len 1280
done

# --- 🔴 FINDING 22: the ONLY budget at which `G4.2` can be demonstrated ----------------
#
# Job 1270491 pinned the clean delimiter loss at 0.1094 to four decimal places across five
# different perturbations. That is a training FLOOR at 600 records, not a coincidence.
# `G4.2` halts on `delimiter_loss < 0.05` AND `gen_entropy < 1.5`, strict on both arms
# (V4.d), so its FIRST arm sits a factor of 2.2 BELOW anything this budget can reach. The
# arm is not a statement about the perturbation at all -- it says the model has learned the
# format almost perfectly -- and an undertrained model cannot satisfy it however its content
# is mangled. `G4.2` was mis-classified as mechanical; it is a model-quality gate.
#
# TWO ARMS, for the same reason the G4.3/G4.12 demonstration above has two: one arm cannot
# separate "the perturbation fell the gate" from "the budget fell the gate".
#
# EXPECTED, written before the run and not edited afterwards:
#   ctrl      G4.2 PASS   -- delim below 0.05, entropy ~2.8 (format learned, content real)
#   collapse  G4.2 FAIL   -- delim below 0.05, entropy ~0.000 (format learned, content dead)
#
# 🔴 If the CTRL arm's delimiter loss does not fall below 0.05 at 4,000 records, this
# demonstration is VOID and is reported VOID -- the collapse arm failing would then show
# nothing at all -- and `G4.2` moves to the Leg-4 folds, where the budget is another order
# of magnitude larger. That fallback is declared HERE, in advance, so it can never be
# presented afterwards as though it were a result.
#
# 🔴 SEPARATE run directory. Sharing $RUNS would overwrite the 600-record collapse_content
# detectors file and the main table above would then be scored with one row trained at a
# different budget from the other ten.
RUNS_G42=/speed-scratch/o_iseri/4J_step4/runs_g42_demo
mkdir -p "$RUNS_G42"
COMMON_G42="--fold es --leg 4 --run-type perturb --epochs 2 --limit-train 4000 --gen-n 16 --batch-size 1 --grad-accum 16 --max-len 1280 --out $RUNS_G42"

echo "############ G4.2 DEMONSTRATION, arm=ctrl (limit-train 4000) ############"
"$ENVDIR/bin/python" -u 4thJ_step4_train.py $COMMON_G42

echo "############ G4.2 DEMONSTRATION, arm=collapse (limit-train 4000) ############"
"$ENVDIR/bin/python" -u 4thJ_step4_train.py $COMMON_G42 --perturbation collapse_content

echo "############ G4.2 DEMONSTRATION, read the two arms ############"
"$ENVDIR/bin/python" -u 4thJ_step4_perturbtable.py --runs "$RUNS_G42" --fold es \
    --out /speed-scratch/o_iseri/4J_step4/g42_demo_es.txt
echo "NOTE: the coverage clause printed by the line above covers the TWO-RUN G4.2"
echo "demonstration ONLY. The battery's real clause is perturb_table_train_side_es.txt."
