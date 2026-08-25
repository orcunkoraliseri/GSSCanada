#!/bin/bash
#SBATCH --job-name=4J_s7_gen
#SBATCH --partition=ps
#SBATCH --gres=gpu:nvidia_a100_2g.20gb:1
#SBATCH --mem=64G
#SBATCH --cpus-per-task=4
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/4J_step7_gen_%j.out

# Step 7, work item 7.3 -- generate one fold.
#   usage: sbatch 4thJ_step7_generate.sh <fold> <n> [--no-grammar]
#
# `FINDING 9`: the GRES is NAMED, never a bare `gpu:1`. A bare request lets Slurm
# hand out a slice already shared with three other processes, which is how the
# Step 4 pilot lost its memory footprint (`FINDING 2`).
#
# Leg 4 by default. Under `D-S7-3` (a) that is a REHEARSAL and the script stamps
# every record `LEG-4 PILOT -- NOT REPORTABLE` itself.

set -x
FOLD=${1:?usage: sbatch 4thJ_step7_generate.sh <es|uk|it> <n> [extra] [prefix_country] [tag]}
N=${2:-600}
EXTRA=${3:-}
LEG=${LEG:-4}
# 🟢 `G6.6` needs the FOLD's adapter driven by a DONOR country's prefixes, and
# `G6.7` needs five fictional-country levels that must not overwrite each other.
# Both are served by the same two optional arguments, and both default to the
# existing behaviour so every earlier invocation is unchanged.
PFX=${4:-$FOLD}
TAG=${5:-}

# `D-S7-4` (a), RULED 2026-08-22: the author MANDATED N >= 5,200 per fold for the
# Leg-5 campaign. `V7.a` refuses to score `G7.7`/`G7.8` below ten strata carrying
# 100 records, and against the real 228-stratum prefix pools that costs
# 5,115 / 5,203 / 4,850 for es / uk / it. A Leg-5 batch smaller than that produces
# gates that cannot be reported at all, so it is refused here rather than
# discovered afterwards.
# 🔴 `D-S6-15` item 3 (a), RULED 2026-08-24: the refusal is NARROWED to the six
# PRIMARY batches. `V7.a` is its only justification and `V7.a` is a Step 7 guard
# -- `grep -l "V7\.a" tools/4thJ_step6_{g66_heldin,g67_score,level1}.py` returns
# nothing. Applied to all 27 it would force the 21 auxiliary batches to 8.7x
# their rehearsal size for a reason that does not reach them, and would move
# `G6.6`/`G6.7` off the single N their own Leg-4 comparisons rest on.
#
# A batch is PRIMARY iff it takes both defaults: the fold's own prefixes and no
# tag. Every `G6.6` batch names a donor country, every `G6.7` level names a tag.
# The class is DERIVED from the invocation, never hand-labelled.
IS_PRIMARY=0
if [ -z "$TAG" ] && [ "$PFX" = "$FOLD" ]; then IS_PRIMARY=1; fi

if [ "$LEG" = "5" ] && [ "$IS_PRIMARY" = "1" ] && [ "$N" -lt 5200 ]; then
    echo "REFUSED: leg 5 PRIMARY batch with N=$N. D-S7-4 (a) mandates N >= 5200 per"
    echo "fold; below that V7.a cannot score G7.7/G7.8 and the batch is unreportable."
    exit 1
fi
if [ "$LEG" = "5" ] && [ "$IS_PRIMARY" = "0" ]; then
    echo "leg 5 AUXILIARY batch (prefixes=$PFX tag=$TAG): N=$N, the 5200 floor does"
    echo "not apply -- D-S6-15 item 3 (a). G6.6/G6.7 stay on their Leg-4 N."
fi

ENVDIR=/speed-scratch/o_iseri/envs/step7
STAGE=/speed-scratch/o_iseri
WORK=/speed-scratch/o_iseri/4J_step7
IN=/speed-scratch/o_iseri/4J_step5/inputs

export HF_HOME=/speed-scratch/o_iseri/hf_cache
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export TMPDIR=/speed-scratch/o_iseri/tmp
export PYTHONIOENCODING=utf-8
export TOKENIZERS_PARALLELISM=false
export VLLM_WORKER_MULTIPROC_METHOD=spawn
# `flashinfer` is UNINSTALLED from envs/step7 (it dies at module scope on
# Python 3.10: `array.array[int]` is only subscriptable from 3.12). vLLM reaches
# the all-reduce fusion pass through `find_spec` and skips it when absent, but
# `flashinfer_sampler_supported()` does a BARE import with no guard -- it returns
# False before that import only when this variable is 0. Env-only; nothing installed.
export VLLM_USE_FLASHINFER_SAMPLER=0

if [ ! -x "$ENVDIR/bin/python" ]; then
    echo "NO STEP 7 ENV AT $ENVDIR -- run 4thJ_step7_env_build.sh first."
    exit 1
fi
for f in "$IN/generation_config_${FOLD}.json" "$IN/prefixes_${PFX}.jsonl"; do
    if [ ! -s "$f" ]; then
        echo "MISSING $f -- scp the Step 5 inputs before submitting."
        exit 1
    fi
done

mkdir -p "$WORK/tools" "$WORK/outputs_step7" || exit 1
# 🔴 `encoder.py` and `decoder.py` are on this list because
# `4thJ_step7_grammar.py` imports `load_bit_positions` from `encoder` since
# `D-S7-5` (1). Job 1286241 died in 5 s on exactly this omission in the sibling
# script and it was still missing here.
for f in 4thJ_step7_grammar.py 4thJ_step7_ebnf.py 4thJ_step7_generate.py encoder.py decoder.py; do
    cp "$STAGE/$f" "$WORK/tools/$f" || exit 1
done
md5sum "$WORK/tools"/4thJ_step7_{grammar,ebnf,generate}.py

cd "$WORK/tools" || exit 1
"$ENVDIR/bin/python" -m py_compile 4thJ_step7_generate.py || exit 1

nvidia-smi

"$ENVDIR/bin/python" -u 4thJ_step7_generate.py \
    --fold "$FOLD" --leg "$LEG" --n "$N" $EXTRA \
    --step2 "$WORK/Step2_docs/outputs_step2" \
    --config "$IN/generation_config_${FOLD}.json" \
    --prefixes "$IN/prefixes_${PFX}.jsonl" \
    ${TAG:+--tag "$TAG"} \
    --out "$WORK/outputs_step7"
echo "generation exit status: $?   (0 = ok, 2 = NOT RUN)"

ls -l "$WORK/outputs_step7"
