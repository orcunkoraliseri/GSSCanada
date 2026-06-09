#!/encs/bin/bash
#SBATCH --job-name=test_py_ep
#SBATCH --partition=ps
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:15:00
#SBATCH --output=/speed-scratch/o_iseri/ep_wrappers/test_py_%j.out

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
RUN=/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected/smoke/SingleD__Montreal_6A/sample_001_HH130192/2022
EPW=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/BEM_Setup/WeatherFile/CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx_6A.epw
EP_EXE=/speed-scratch/o_iseri/ep_wrappers/energyplus

echo "=== Python subprocess E+ test ==="

$PYTHON - <<'PYEOF'
import subprocess, os, sys

ep_exe = "/speed-scratch/o_iseri/ep_wrappers/energyplus"
epw = "/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/BEM_Setup/WeatherFile/CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx_6A.epw"
run_dir = "/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected/smoke/SingleD__Montreal_6A/sample_001_HH130192/2022"
idf = os.path.join(run_dir, "expanded.idf")

cmd = [ep_exe, "-w", epw, "-d", run_dir, idf]
print("CMD:", " ".join(cmd))
print("IDF exists:", os.path.exists(idf))
print("EPW exists:", os.path.exists(epw))
print("EP_EXE exists:", os.path.exists(ep_exe))
print("PATH:", os.environ.get("PATH", ""))

# Test 1: capture_output=False (visible)
print("\n--- Test 1: capture_output=False (first 5 lines only via timeout) ---")
try:
    result = subprocess.run(cmd, capture_output=False, timeout=10)
    print("Exit code:", result.returncode)
except subprocess.TimeoutExpired:
    print("Still running after 10s — E+ is working fine")
except Exception as e:
    print("Exception:", e)
PYEOF
