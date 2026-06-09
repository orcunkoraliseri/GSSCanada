#!/encs/bin/bash
#SBATCH --job-name=test_fresh_idf
#SBATCH --partition=ps
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=00:20:00
#SBATCH --output=/speed-scratch/o_iseri/ep_wrappers/test_fresh_%j.out

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python

$PYTHON - <<'PYEOF'
import subprocess, os
from concurrent.futures import ProcessPoolExecutor, as_completed

EP = "/speed-scratch/o_iseri/ep_wrappers/energyplus"
EPW = "/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/BEM_Setup/WeatherFile/CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx_6A.epw"
SMOKE = "/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected/smoke/SingleD__Montreal_6A"

jobs = [
    {"name": "HH130192", "dir": f"{SMOKE}/sample_001_HH130192/2022"},
    {"name": "HH79136",  "dir": f"{SMOKE}/sample_002_HH79136/2022"},
    {"name": "HH42121",  "dir": f"{SMOKE}/sample_003_HH42121/2022"},
]

def run_ep_fresh(job):
    d = job["dir"]
    idf = os.path.join(d, "expanded.idf")
    cmd = [EP, "-w", EPW, "-d", d, idf]
    print(f"  {job['name']}: idf_size={os.path.getsize(idf)} bytes", flush=True)
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=180)
        if r.returncode == 0:
            return f"{job['name']}: SUCCESS exit=0"
        else:
            out = r.stdout[:1000].decode(errors="replace") if r.stdout else ""
            err = r.stderr[:200].decode(errors="replace") if r.stderr else ""
            return f"{job['name']}: FAIL exit={r.returncode}\nSTDOUT:{out}\nSTDERR:{err}"
    except subprocess.TimeoutExpired:
        return f"{job['name']}: TIMEOUT still running — OK"
    except Exception as e:
        return f"{job['name']}: EXCEPTION {e}"

print("Testing E+ on fresh smoke IDFs (3 parallel separate dirs)", flush=True)
with ProcessPoolExecutor(max_workers=3) as ex:
    futures = {ex.submit(run_ep_fresh, j): j for j in jobs}
    for fut in as_completed(futures):
        print(fut.result(), flush=True)
print("Done", flush=True)
PYEOF
