#!/bin/bash
#SBATCH --job-name=4J_s4_ds614probe
#SBATCH --partition=ps
#SBATCH --mem=32G
#SBATCH --cpus-per-task=2
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/4J_step4_ds614probe_%j.out

# `D-S6-14` -- the POISONED_CONTROL interlock, SEEN REFUSING in BOTH directions.
#
# `4thJ_step4_train.py:1032-1044` refuses (i) a production run-type on the permuted
# manifest and (ii) `--run-type permuted` on the clean one. The four control jobs
# 1286896-1286899 show the interlock ACCEPTING. A guard that has only been seen
# accepting is not a guard -- `FINDING 56`, where a 600/600 PASS turned out to be a
# model-repo default covering for a broken harness.
#
# CPU ONLY. No `--gres`: both refusals happen when the manifest is read, hundreds of
# lines before any weight is loaded, so this must not take a GPU away from the Leg-5
# control (1286896) that is already queued behind `Resources`.
#
# 🔴 BOTH arms MUST exit non-zero. An arm that exits 0 means the interlock did not
# fire and the control's isolation is unproven.

set -x
ENVDIR=/speed-scratch/o_iseri/envs/step4
export HF_HOME=/speed-scratch/o_iseri/hf_cache
export TMPDIR=/speed-scratch/o_iseri/tmp
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export PYTHONIOENCODING=utf-8
export TOKENIZERS_PARALLELISM=false

CLEAN=/speed-scratch/o_iseri/4J_step4/shard_manifest.json
POISON=/speed-scratch/o_iseri/4J_step4/shard_manifest_permuted_control.json
cd /speed-scratch/o_iseri || exit 1

echo "=============== ARM 1: production run-type on the POISONED manifest ==============="
echo "expected: REFUSED (non-zero). If this trains, the poisoned corpus can reach a"
echo "reported model."
"$ENVDIR/bin/python" -u 4thJ_step4_train.py \
    --fold es --leg 4 --run-type primary --shard-manifest "$POISON" \
    --out /speed-scratch/o_iseri/4J_step4/runs_ds614_probe_MUSTNOTEXIST
A1=$?
echo "ARM 1 exit: $A1"

echo "=============== ARM 2: --run-type permuted on the CLEAN manifest ==============="
echo "expected: REFUSED (non-zero). If this trains, the 'ceiling' would be measured on"
echo "the real corpus and would not be a ceiling at all."
"$ENVDIR/bin/python" -u 4thJ_step4_train.py \
    --fold es --leg 4 --run-type permuted --shard-manifest "$CLEAN" \
    --out /speed-scratch/o_iseri/4J_step4/runs_ds614_probe_MUSTNOTEXIST
A2=$?
echo "ARM 2 exit: $A2"

echo "=============== VERDICT ==============="
if [ "$A1" -ne 0 ] && [ "$A2" -ne 0 ]; then
    echo "INTERLOCK SEEN REFUSING IN BOTH DIRECTIONS -- arm1=$A1 arm2=$A2"
else
    echo "🔴 INTERLOCK DID NOT FIRE -- arm1=$A1 arm2=$A2. The control's isolation is"
    echo "UNPROVEN and D-S6-14 may not be closed on it."
fi
ls -d /speed-scratch/o_iseri/4J_step4/runs_ds614_probe_MUSTNOTEXIST 2>/dev/null \
    && echo "🔴 A RUN DIRECTORY WAS CREATED -- inspect before trusting either arm."
