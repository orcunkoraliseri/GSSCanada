#!/encs/bin/bash
#SBATCH --job-name=test_cap_true
#SBATCH --partition=ps
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:15:00
#SBATCH --output=/speed-scratch/o_iseri/ep_wrappers/test_cap_%j.out

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python

$PYTHON - <<'PYEOF'
import subprocess, os, sys

ep_exe = "/speed-scratch/o_iseri/ep_wrappers/energyplus"
epw = "/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/BEM_Setup/WeatherFile/CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx_6A.epw"
run_dir = "/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected/smoke/SingleD__Montreal_6A/sample_001_HH130192/2022"
idf = os.path.join(run_dir, "expanded.idf")

cmd = [ep_exe, "-w", epw, "-d", run_dir, idf]
print("Testing capture_output=True (mirrors simulation.py quiet=True)", flush=True)

try:
    result = subprocess.run(cmd, check=True, capture_output=True, timeout=30)
    print("SUCCESS exit:", result.returncode, flush=True)
    print("stdout last 500:", result.stdout[-500:].decode(errors="replace"), flush=True)
except subprocess.TimeoutExpired:
    print("Still running after 30s — works but slow", flush=True)
except subprocess.CalledProcessError as e:
    print("CalledProcessError exit:", e.returncode, flush=True)
    print("stdout:", e.stdout[:2000].decode(errors="replace") if e.stdout else "(empty)", flush=True)
    print("stderr:", e.stderr[:2000].decode(errors="replace") if e.stderr else "(empty)", flush=True)
except Exception as e:
    print("Exception:", type(e).__name__, e, flush=True)
PYEOF
