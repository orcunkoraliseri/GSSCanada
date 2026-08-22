#!/bin/bash
#SBATCH --job-name=4J_s7_env
#SBATCH --partition=ps
#SBATCH --gres=gpu:nvidia_a100_2g.20gb:1
#SBATCH --mem=64G
#SBATCH --cpus-per-task=4
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/4J_step7_env_%j.out

# Step 7, work item 7.2 -- build the constrained-generation environment.
#   usage: sbatch 4thJ_step7_env_build.sh
#
# `D-S7-3` sub-question, ruled YES by the author on 2026-08-22: a NEW venv at
# envs/step7. envs/step4 is not touched by this script and must not be -- every
# Step 4 number on record was produced by it, and re-resolving its dependency set
# to satisfy vLLM would put those numbers on an environment that no longer exists.
#
# A GPU slice is requested even though this is an install job. `bitsandbytes` and
# `vllm` both run a CUDA probe at import; installing them without ever importing
# them on a GPU would report success for an environment nobody has exercised.
#
# NOTHING IS PINNED, deliberately. vLLM's Olmo-3 support is the thing being
# tested, not something to assert -- the job prints the resolved versions and
# then ASKS the registry which architectures it carries. If Olmo3ForCausalLM is
# absent, that is a finding for the author, not a reason to install a guess.

set -x
ENVDIR=/speed-scratch/o_iseri/envs/step7
BASEPY=/speed-scratch/o_iseri/envs/step4/bin/python

export HF_HOME=/speed-scratch/o_iseri/hf_cache
export PIP_CACHE_DIR=/speed-scratch/o_iseri/pip_cache
export TMPDIR=/speed-scratch/o_iseri/tmp
export TOKENIZERS_PARALLELISM=false

nvidia-smi

if [ ! -x "$BASEPY" ]; then
    echo "NO BASE INTERPRETER AT $BASEPY -- refusing to build."
    exit 1
fi

if [ ! -x "$ENVDIR/bin/python" ]; then
    "$BASEPY" -m venv "$ENVDIR"
    if [ ! -x "$ENVDIR/bin/python" ]; then
        echo "VENV CREATION FAILED at $ENVDIR"
        exit 1
    fi
    "$ENVDIR/bin/python" -m pip install --upgrade pip setuptools wheel
    # vllm pulls its own torch and its own xgrammar; both are named anyway so the
    # log records that they were asked for, not inherited by accident.
    "$ENVDIR/bin/python" -m pip install vllm xgrammar bitsandbytes
    # the generation side also needs the adapter loader and the corpus readers.
    "$ENVDIR/bin/python" -m pip install transformers peft accelerate pandas pyarrow
else
    echo "ENV ALREADY PRESENT AT $ENVDIR -- skipping install, running verification only."
fi

echo "===== envs/step4 UNTOUCHED CHECK ====="
ls -d /speed-scratch/o_iseri/envs/step4
"$BASEPY" -c "import torch; print('step4 torch still', torch.__version__)"

echo "===== RESOLVED VERSIONS ====="
"$ENVDIR/bin/python" - <<'PY'
import importlib, sys
print('python', sys.version.split()[0])
for m in ('torch', 'vllm', 'xgrammar', 'bitsandbytes', 'transformers',
          'peft', 'accelerate', 'numpy', 'pandas', 'pyarrow'):
    try:
        mod = importlib.import_module(m)
        print('%-14s %s' % (m, getattr(mod, '__version__', 'no __version__')))
    except Exception as e:
        print('%-14s MISSING (%s: %s)' % (m, type(e).__name__, e))
PY

echo "===== CUDA REACHABLE FROM THE NEW ENV ====="
"$ENVDIR/bin/python" - <<'PY'
import torch
print('cuda available :', torch.cuda.is_available())
if torch.cuda.is_available():
    print('device         :', torch.cuda.get_device_name(0))
    print('capability     :', torch.cuda.get_device_capability(0))
    print('bf16 supported :', torch.cuda.is_bf16_supported())
PY

echo "===== vLLM MODEL REGISTRY: WHICH OLMO ARCHITECTURES ARE NATIVE ====="
# Step4_docs/4thJ_04_finetuneLLM.md records Olmo2ForCausalLM as a generic
# Transformers fallback and Olmo3ForCausalLM as a native kernel. That claim was
# read from documentation. This asks the installed package.
"$ENVDIR/bin/python" - <<'PY'
try:
    from vllm.model_executor.models.registry import ModelRegistry
    archs = sorted(ModelRegistry.get_supported_archs())
    print('registry carries %d architectures' % len(archs))
    for a in archs:
        if 'lmo' in a:
            print('  NATIVE:', a)
    for want in ('Olmo3ForCausalLM', 'Olmo2ForCausalLM', 'OlmoForCausalLM'):
        print('%-20s %s' % (want, 'native' if want in archs else 'NOT NATIVE (generic fallback)'))
except Exception as e:
    print('REGISTRY QUERY FAILED (%s: %s)' % (type(e).__name__, e))
PY

echo "===== XGRAMMAR COMPILES A GRAMMAR AT ALL ====="
# The smallest possible end-to-end check: a two-symbol EBNF, compiled against a
# real tokenizer vocabulary. If this fails, G7.10 has no back-end and the whole
# ruling stalls here rather than three jobs later.
"$ENVDIR/bin/python" - <<'PY'
try:
    import xgrammar as xgr
    g = xgr.Grammar.from_ebnf('root ::= "a" | "b"\n')
    print('grammar object :', type(g).__name__)
    print('XGRAMMAR EBNF COMPILE: ok')
except Exception as e:
    print('XGRAMMAR EBNF COMPILE FAILED (%s: %s)' % (type(e).__name__, e))
PY

echo "===== bitsandbytes ON THIS GPU ====="
"$ENVDIR/bin/python" - <<'PY'
try:
    import torch, bitsandbytes as bnb
    from bitsandbytes.nn import Linear4bit
    lin = Linear4bit(64, 64, compute_dtype=torch.bfloat16).cuda()
    out = lin(torch.randn(2, 64, device='cuda', dtype=torch.bfloat16))
    print('Linear4bit forward:', tuple(out.shape), 'ok')
except Exception as e:
    print('BITSANDBYTES 4BIT FAILED (%s: %s)' % (type(e).__name__, e))
PY

echo "===== DONE ====="
