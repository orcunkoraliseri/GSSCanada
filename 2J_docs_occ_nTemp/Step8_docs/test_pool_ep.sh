#!/encs/bin/bash
#SBATCH --job-name=test_pool_ep
#SBATCH --partition=ps
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=00:20:00
#SBATCH --output=/speed-scratch/o_iseri/ep_wrappers/test_pool_%j.out

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python

$PYTHON - <<'PYEOF'
import subprocess, os, sys
from concurrent.futures import ProcessPoolExecutor, as_completed

def run_ep(job_id):
    ep_exe = "/speed-scratch/o_iseri/ep_wrappers/energyplus"
    epw = "/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/BEM_Setup/WeatherFile/CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx_6A.epw"
    run_dir = "/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected/smoke/SingleD__Montreal_6A/sample_001_HH130192/2022"
    idf = os.path.join(run_dir, "expanded.idf")
    cmd = [ep_exe, "-w", epw, "-d", run_dir, idf]
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, timeout=120)
        return f"job {job_id}: SUCCESS exit={result.returncode}"
    except subprocess.TimeoutExpired:
        return f"job {job_id}: TIMEOUT (still running at 120s — actually works)"
    except subprocess.CalledProcessError as e:
        return f"job {job_id}: FAIL exit={e.returncode} stdout={e.stdout[:500].decode(errors='replace')} stderr={e.stderr[:500].decode(errors='replace')}"
    except Exception as e:
        return f"job {job_id}: EXCEPTION {type(e).__name__}: {e}"

print("Testing ProcessPoolExecutor with 3 parallel E+ workers", flush=True)
with ProcessPoolExecutor(max_workers=3) as ex:
    futures = {ex.submit(run_ep, i): i for i in range(3)}
    for fut in as_completed(futures):
        print(fut.result(), flush=True)
print("Done", flush=True)
PYEOF
