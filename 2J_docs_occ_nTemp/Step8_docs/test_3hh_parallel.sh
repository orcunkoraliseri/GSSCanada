#!/encs/bin/bash
#SBATCH --job-name=test_3hh
#SBATCH --partition=ps
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=00:20:00
#SBATCH --output=/speed-scratch/o_iseri/ep_wrappers/test_3hh_%j.out

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python

$PYTHON - <<'PYEOF'
import subprocess, os
from concurrent.futures import ProcessPoolExecutor, as_completed

SMOKE = "/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected/smoke/SingleD__Montreal_6A"
EP = "/speed-scratch/o_iseri/ep_wrappers/energyplus"
EPW = "/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/BEM_Setup/WeatherFile/CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx_6A.epw"

# Each HH uses its own separate output dir
jobs = [
    {"name": "HH79136",  "dir": f"{SMOKE}/sample_002_HH79136/2022"},
    {"name": "HH42121",  "dir": f"{SMOKE}/sample_003_HH42121/2022"},
]

def run_ep(job):
    d = job["dir"]
    idf = os.path.join(d, "expanded.idf")
    cmd = [EP, "-w", EPW, "-d", d, idf]
    try:
        r = subprocess.run(cmd, check=True, capture_output=True, timeout=180)
        return f"{job['name']}: SUCCESS"
    except subprocess.TimeoutExpired:
        return f"{job['name']}: TIMEOUT (still running — OK)"
    except subprocess.CalledProcessError as e:
        out = e.stdout[:800].decode(errors="replace") if e.stdout else ""
        err = e.stderr[:200].decode(errors="replace") if e.stderr else ""
        return f"{job['name']}: FAIL exit={e.returncode}\n  stdout={out}\n  stderr={err}"
    except Exception as e:
        return f"{job['name']}: EXCEPTION {e}"

print("Running 2 HH E+ jobs in parallel (separate dirs)", flush=True)
with ProcessPoolExecutor(max_workers=2) as ex:
    futures = {ex.submit(run_ep, j): j for j in jobs}
    for fut in as_completed(futures):
        print(fut.result(), flush=True)
print("Done", flush=True)
PYEOF
