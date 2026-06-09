#!/usr/bin/env python3
"""step8_warmup_retry.py - retry failed E+ runs with Maximum Warmup Days = 120.

Walks the Step 8 campaign output directory.  For every Scenario_*.idf whose
output directory lacks a successful eplusout.end, patches the IDF's Building
object (Maximum Number of Warmup Days) to 120 and re-runs E+ via the existing
ENERGYPLUS_DIR wrapper.

Usage (on cluster, after main campaign):
    python step8_warmup_retry.py /speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected/campaign_N50

Environment:
    ENERGYPLUS_DIR  path to ep_wrappers dir (same as main campaign)
    IDD_FILE        path to Energy+.idd (same as main campaign)

Targets HighRise and MidRise cells where warmup oscillation is known.
Other archetypes are also checked; any failure triggers a retry.
"""
import os
import re
import shutil
import subprocess
import sys

CAMPAIGN_ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
EP_DIR = os.environ.get("ENERGYPLUS_DIR", "/usr/local/EnergyPlus-24-2-0")
EP_EXE = os.path.join(EP_DIR, "energyplus")
EXPAND_EXE = os.path.join(EP_DIR, "ExpandObjects")

# City label -> EPW keyword (mirrors STEP8_CITIES in main.py)
CITY_TO_EPW = {
    "Toronto_5A":   "Toronto",
    "Kelowna_5B":   "Kelowna",
    "Vancouver_5C": "Vancouver",
    "Montreal_6A":  "Montreal",
    "Calgary_6B":   "Calgary",
    "Winnipeg_7A":  "Winnipeg",
}

# WEATHER_DIR is four levels up from main.py = GSSCanada-main/BEM_Setup/WeatherFile
_HERE = os.path.dirname(os.path.abspath(__file__))
_BASE = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
WEATHER_DIR = os.path.join(_BASE, "BEM_Setup", "WeatherFile")


def _job_succeeded(out_dir):
    end = os.path.join(out_dir, "eplusout.end")
    if not os.path.exists(end):
        return False
    try:
        with open(end, "r", errors="ignore") as f:
            return "Completed Successfully" in f.read()
    except Exception:
        return False


def _find_epw(cell_label):
    """Derive EPW path from cell label '<arch>__<city>'."""
    parts = cell_label.split("__")
    city = parts[1] if len(parts) == 2 else ""
    keyword = CITY_TO_EPW.get(city, "")
    if not keyword:
        return None
    import glob
    matches = [p for p in glob.glob(os.path.join(WEATHER_DIR, "*.epw"))
               if keyword.upper() in os.path.basename(p).upper()]
    return matches[0] if matches else None


def _patch_warmup(idf_src, idf_dst, max_warmup=120):
    with open(idf_src, "r", errors="ignore") as f:
        content = f.read()
    patched = re.sub(
        r'(\d+)(\s*[,;]\s*!-\s*Maximum Number of Warmup Days)',
        lambda m: f'{max_warmup}{m.group(2)}',
        content, count=1, flags=re.IGNORECASE
    )
    if patched == content:
        print(f"  [WARN] Maximum Number of Warmup Days field not found in IDF; copying as-is")
    with open(idf_dst, "w") as f:
        f.write(patched)


def _run_ep(idf_path, epw_path, out_dir):
    in_idf = os.path.join(out_dir, "in.idf")
    shutil.copy2(idf_path, in_idf)
    idd_src = os.path.join(EP_DIR, "Energy+.idd")
    if os.path.exists(idd_src):
        shutil.copy2(idd_src, os.path.join(out_dir, "Energy+.idd"))
    if os.path.isfile(EXPAND_EXE):
        subprocess.run([EXPAND_EXE], cwd=out_dir, capture_output=True)
    sim_idf = os.path.join(out_dir, "expanded.idf")
    if not os.path.exists(sim_idf):
        sim_idf = in_idf
    result = subprocess.run(
        [EP_EXE, "-w", epw_path, "-d", out_dir, sim_idf],
        capture_output=True
    )
    return result.returncode == 0 and _job_succeeded(out_dir)


total = retried = recovered = no_epw = 0

# Group jobs by cell (cell = top-level subdir of campaign root)
for cell_name in sorted(os.listdir(CAMPAIGN_ROOT)):
    cell_dir = os.path.join(CAMPAIGN_ROOT, cell_name)
    if not os.path.isdir(cell_dir):
        continue
    if "__" not in cell_name:
        continue

    epw = _find_epw(cell_name)
    if epw is None:
        print(f"[SKIP - no EPW resolved] {cell_name}")
        no_epw += 1
        continue

    for dirpath, _, filenames in os.walk(cell_dir):
        for fn in filenames:
            if not (fn.startswith("Scenario_") and fn.endswith(".idf")):
                continue
            idf_path = os.path.join(dirpath, fn)
            out_dir = dirpath
            if _job_succeeded(out_dir):
                continue
            total += 1
            rel = os.path.relpath(idf_path, CAMPAIGN_ROOT)
            print(f"[RETRY] {rel}")
            patched = idf_path.replace(".idf", "_w120.idf")
            _patch_warmup(idf_path, patched)
            ok = _run_ep(patched, epw, out_dir)
            retried += 1
            if ok:
                recovered += 1
                print(f"  [OK] recovered with warmup-120")
            else:
                print(f"  [FAIL] still failing — document as exclusion")

print(f"\n=== Warmup retry complete ===")
print(f"  Failed jobs found : {total}")
print(f"  Retried (w120)    : {retried}")
print(f"  Recovered         : {recovered}")
print(f"  Persistent fail   : {retried - recovered}  (document as exclusions in 08_simulation_val.md)")
print(f"  Skipped (no EPW)  : {no_epw}")
