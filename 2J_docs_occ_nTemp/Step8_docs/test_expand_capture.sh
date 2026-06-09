#!/encs/bin/bash
#SBATCH --job-name=test_exp_cap
#SBATCH --partition=ps
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:10:00
#SBATCH --output=/speed-scratch/o_iseri/ep_wrappers/test_expcap_%j.out

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python

# Source IDF from original smoke run
SRC_IDF=/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected/smoke/SingleD__Montreal_6A/sample_001_HH130192/2022/Scenario_2022.idf
IDD=/speed-scratch/o_iseri/ep_wrappers/Energy+.idd

$PYTHON - <<'PYEOF'
import subprocess, os, shutil, tempfile

expand_exe = "/speed-scratch/o_iseri/ep_wrappers/ExpandObjects"
src_idf = "/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected/smoke/SingleD__Montreal_6A/sample_001_HH130192/2022/Scenario_2022.idf"
idd = "/speed-scratch/o_iseri/ep_wrappers/Energy+.idd"

# Test A: capture_output=False (like simulation.py with quiet=False)
run_a = "/speed-scratch/o_iseri/ep_wrappers/test_exp_run_A"
os.makedirs(run_a, exist_ok=True)
shutil.copy2(src_idf, os.path.join(run_a, "in.idf"))
shutil.copy2(idd, os.path.join(run_a, "Energy+.idd"))
print("=== Test A: capture_output=False ===", flush=True)
r = subprocess.run([expand_exe], cwd=run_a, capture_output=False)
print(f"Exit code: {r.returncode}  expanded.idf exists: {os.path.exists(os.path.join(run_a, 'expanded.idf'))}", flush=True)

# Test B: capture_output=True (like simulation.py with quiet=True)
run_b = "/speed-scratch/o_iseri/ep_wrappers/test_exp_run_B"
os.makedirs(run_b, exist_ok=True)
shutil.copy2(src_idf, os.path.join(run_b, "in.idf"))
shutil.copy2(idd, os.path.join(run_b, "Energy+.idd"))
print("=== Test B: capture_output=True ===", flush=True)
r = subprocess.run([expand_exe], cwd=run_b, capture_output=True)
print(f"Exit code: {r.returncode}  expanded.idf exists: {os.path.exists(os.path.join(run_b, 'expanded.idf'))}", flush=True)
print(f"stdout: {r.stdout[:500].decode(errors='replace')}", flush=True)
print(f"stderr: {r.stderr[:500].decode(errors='replace')}", flush=True)
PYEOF
