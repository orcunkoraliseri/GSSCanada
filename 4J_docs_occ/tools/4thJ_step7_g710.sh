#!/bin/bash
#SBATCH --job-name=4J_s7_g710
#SBATCH --partition=ps
#SBATCH --mem=32G
#SBATCH --cpus-per-task=4
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/4J_step7_g710_%j.out

# `G7.10` -- oracle agreement. Step 7, work item 7.2.
#   usage: sbatch 4thJ_step7_g710.sh
#
# No GPU is requested and none is needed: XGrammar compiles and matches on the
# CPU, and neither recogniser involves a model. `G7.10` is the one Step 7 gate
# that can be settled before a single diary is generated, which is why it runs
# first under `D-S7-3` (a).
#
# The job builds its own working tree. `4thJ_step7_grammar_selftest.py` resolves
# the crosswalks as `../Step2_docs/outputs_step2` relative to itself and takes no
# argument, so rather than edit a closed 44-check artefact to add one, the tree
# is shaped to match what it already expects and the crosswalks are SYMLINKED --
# never copied, so there is one canonical set of codes and no chance of the gate
# reading a stale duplicate.
#
# The self-tests run BEFORE the gate. A green self-test does not make the gate
# pass, but a red one makes the gate's verdict meaningless, so the log carries
# both, in that order.

set -x
ENVDIR=/speed-scratch/o_iseri/envs/step7
STAGE=/speed-scratch/o_iseri
WORK=/speed-scratch/o_iseri/4J_step7
XWALK=/speed-scratch/o_iseri/4J/outputs_step2

export TMPDIR=/speed-scratch/o_iseri/tmp
export PYTHONIOENCODING=utf-8
export TOKENIZERS_PARALLELISM=false

if [ ! -x "$ENVDIR/bin/python" ]; then
    echo "NO STEP 7 ENV AT $ENVDIR -- run 4thJ_step7_env_build.sh first."
    exit 1
fi
if [ ! -f "$XWALK/activity_target_list.csv" ]; then
    echo "NO CROSSWALKS AT $XWALK -- refusing to build an alphabet from nothing."
    exit 1
fi

mkdir -p "$WORK/tools" "$WORK/Step2_docs" "$WORK/outputs_step7" || exit 1
ln -sfn "$XWALK" "$WORK/Step2_docs/outputs_step2"

for f in 4thJ_step7_grammar.py 4thJ_step7_grammar_selftest.py \
         4thJ_step7_ebnf.py 4thJ_step7_ebnf_selftest.py 4thJ_step7_g710.py; do
    if [ ! -f "$STAGE/$f" ]; then
        echo "MISSING $STAGE/$f -- scp it before submitting."
        exit 1
    fi
    cp "$STAGE/$f" "$WORK/tools/$f"
done
md5sum "$WORK/tools"/4thJ_step7_*.py

cd "$WORK/tools" || exit 1
"$ENVDIR/bin/python" -m py_compile 4thJ_step7_grammar.py 4thJ_step7_ebnf.py \
    4thJ_step7_g710.py
if [ $? -ne 0 ]; then
    echo "SYNTAX ERROR -- G7.10 not started"
    exit 1
fi

echo "===== grammar self-test ====="
"$ENVDIR/bin/python" -u 4thJ_step7_grammar_selftest.py
echo "grammar self-test exit: $?"

echo "===== EBNF self-test ====="
"$ENVDIR/bin/python" -u 4thJ_step7_ebnf_selftest.py
echo "EBNF self-test exit: $?"

echo "===== G7.10 ====="
"$ENVDIR/bin/python" -u 4thJ_step7_g710.py \
    --n 10000 --seed 20260822 \
    --step2 "$WORK/Step2_docs/outputs_step2" \
    --out "$WORK/outputs_step7"
echo "G7.10 exit status: $?   (0 = PASS, 1 = FAIL, 2 = NOT RUN)"

ls -l "$WORK/outputs_step7"
md5sum "$WORK/outputs_step7"/*
