#!/bin/bash
#SBATCH --job-name=4J_s7_fix
#SBATCH --partition=ps
#SBATCH --gres=gpu:nvidia_a100_2g.20gb:1
#SBATCH --mem=32G
#SBATCH --cpus-per-task=4
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/4J_step7_envfix_%j.out

# Remove `flashinfer-python` from envs/step7 ONLY.
#
# It is an OPTIONAL vLLM accelerator, not a requirement. vLLM reaches it through
# `find_spec("flashinfer.comm")` in its all-reduce fusion pass and skips the pass
# when the module is absent; with it present on Python 3.10 the import dies at
# module scope on `array.array[int]`, a subscription that is only legal from
# Python 3.12. The venv is 3.10 (it inherits envs/step4's interpreter), so the
# package can never load here and its only effect is to abort the engine.
#
# Additive: envs/step4 is not touched, and nothing is installed or upgraded.

set -x
ENVDIR=/speed-scratch/o_iseri/envs/step7
export TMPDIR=/speed-scratch/o_iseri/tmp
export PYTHONIOENCODING=utf-8

"$ENVDIR/bin/python" -V
"$ENVDIR/bin/python" -m pip list --format=freeze | grep -i flashinfer
"$ENVDIR/bin/python" -m pip uninstall -y flashinfer-python flashinfer
echo "uninstall exit: $?"

echo "===== the module must now be GONE ====="
"$ENVDIR/bin/python" -c "import importlib.util as u; print('flashinfer spec:', u.find_spec('flashinfer'))"

echo "===== vLLM must still import and still see the OLMo architectures ====="
"$ENVDIR/bin/python" -c "
import vllm
from vllm.model_executor.models.registry import ModelRegistry
print('vllm', vllm.__version__)
a = [m for m in ModelRegistry.get_supported_archs() if 'lmo' in m]
print('olmo archs:', sorted(a))
from vllm.sampling_params import StructuredOutputsParams
print('StructuredOutputsParams present:', StructuredOutputsParams is not None)
"
echo "vllm import exit: $?"

echo "===== envs/step4 must be UNCHANGED ====="
/speed-scratch/o_iseri/envs/step4/bin/python -c "import torch; print('step4 torch', torch.__version__)"
