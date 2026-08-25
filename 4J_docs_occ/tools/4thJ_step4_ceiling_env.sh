#!/bin/bash
#SBATCH --job-name=4J_s4_ceilenv
#SBATCH --partition=ps
#SBATCH --mem=32G
#SBATCH --cpus-per-task=4
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/4J_step4_ceilenv_%j.out

# Step 4 -- stage `bitsandbytes` for the CEILING run WITHOUT touching envs/step4.
#   usage: sbatch 4thJ_step4_ceiling_env.sh
#
# `D-S7-3` froze envs/step4 in one sentence: "every Step 4 number on record was
# produced by it, and re-resolving its dependency set would put those numbers on
# an environment that no longer exists." That ruling is why `bitsandbytes` was
# never installed, and it is not being relitigated here.
#
# So nothing is installed INTO envs/step4. `pip install --target` writes to a
# directory of its own and touches no site-packages; the ceiling job then puts
# that one directory on PYTHONPATH. The interpreter, torch, transformers and peft
# the ceiling run uses are then BYTE-FOR-BYTE the ones every LoRA run used, which
# is the whole point -- a recipe comparison run on a different dependency set is
# not a recipe comparison.
#
# 🔴 NO GPU IS REQUESTED, and that is a change of mind worth recording. The
# install itself needs no card, and the GPU allocation is capped at four
# concurrent jobs -- a five-minute install queued behind four multi-hour
# generation jobs would gate the ceiling run for hours for no measurement. The
# CUDA side of `bitsandbytes` is exercised where it has to be exercised anyway:
# `4thJ_step4_ceiling_fold.sh` builds a real `AdamW8bit` over real 7 B parameters
# on the 80 GB instance, and fails at optimiser construction if the binary is
# wrong. This job proves the install exists and imports; that job proves it runs.

set -x
ENVDIR=/speed-scratch/o_iseri/envs/step4
BNBDIR=/speed-scratch/o_iseri/envs/bnb_for_step4

export HF_HOME=/speed-scratch/o_iseri/hf_cache
export PIP_CACHE_DIR=/speed-scratch/o_iseri/pip_cache
export TMPDIR=/speed-scratch/o_iseri/tmp

nvidia-smi

if [ ! -x "$ENVDIR/bin/python" ]; then
    echo "NO STEP 4 ENV AT $ENVDIR -- refusing."
    exit 1
fi

echo "===== envs/step4 site-packages BEFORE ====="
BEFORE=$(ls "$ENVDIR"/lib/python*/site-packages | md5sum)
echo "$BEFORE"

mkdir -p "$BNBDIR" || exit 1
# 🔴 --no-deps IS LOAD-BEARING, and it is here because the first attempt (job
# 1287243, cancelled) proved it. Without it, pip resolved bitsandbytes'
# dependency on torch and began installing a SECOND torch -- a CUDA-13 build --
# into $BNBDIR. $BNBDIR goes on PYTHONPATH, and PYTHONPATH takes precedence over
# a venv's site-packages, so that torch would have SHADOWED envs/step4's
# torch 2.5.1+cu121 at run time. The ceiling run would then have been a full
# fine-tune on a different torch from every LoRA run it is meant to be compared
# against -- which is precisely the harm D-S7-3's freeze exists to prevent,
# arriving through the door built to respect it.
#
# bitsandbytes' dependencies -- torch and numpy -- are already in envs/step4.
"$ENVDIR/bin/python" -m pip install --no-deps --target "$BNBDIR" bitsandbytes
if [ $? -ne 0 ]; then
    echo "PIP INSTALL FAILED -- the ceiling run stays UNRUN and that is reported as"
    echo "a gap, not as a pass."
    exit 1
fi

echo "===== envs/step4 site-packages AFTER -- must be IDENTICAL ====="
AFTER=$(ls "$ENVDIR"/lib/python*/site-packages | md5sum)
echo "$AFTER"
if [ "$BEFORE" != "$AFTER" ]; then
    echo "🔴 envs/step4 CHANGED. D-S7-3's freeze is broken. STOP."
    exit 1
fi
echo "envs/step4 UNTOUCHED, confirmed by md5 of its own package listing."

echo "===== $BNBDIR must contain NOTHING BUT bitsandbytes ====="
ls "$BNBDIR"
for FORBIDDEN in torch numpy nvidia triton sympy networkx ; do
    if [ -e "$BNBDIR/$FORBIDDEN" ]; then
        echo "🔴 $BNBDIR CONTAINS $FORBIDDEN. On PYTHONPATH it would SHADOW the"
        echo "   copy in envs/step4 and the ceiling run would not be comparable to"
        echo "   any LoRA run. Re-install with --no-deps. STOPPING."
        exit 1
    fi
done
echo "no shadowing packages present."

echo "===== import probe ====="
PYTHONPATH="$BNBDIR" "$ENVDIR/bin/python" -c "
import torch, bitsandbytes as bnb
print('torch       ', torch.__version__, 'cuda', torch.cuda.is_available())
print('bitsandbytes', bnb.__version__)
from bitsandbytes.optim import AdamW8bit
if torch.cuda.is_available():
    p = torch.nn.Parameter(torch.randn(64, 64, device='cuda'))
    o = AdamW8bit([p], lr=1e-4)
    (p.sum()).backward(); o.step(); o.zero_grad()
    print('AdamW8bit    took a real step on a real CUDA tensor: OK')
else:
    print('AdamW8bit    IMPORTED but NOT exercised -- no card on this node. The')
    print('             ceiling run is what exercises it, and it will fail at')
    print('             optimiser construction if the binary is wrong.')
"
echo "probe exit: $?"

echo "===== the refusal path must still exist in the trainer ====="
grep -n "REFUSING rather than falling" /speed-scratch/o_iseri/4thJ_step4_train.py
