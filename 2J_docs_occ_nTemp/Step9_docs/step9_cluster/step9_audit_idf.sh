#!/encs/bin/bash
#SBATCH --job-name=s9_audit
#SBATCH --partition=ps
#SBATCH --mem=8G
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --output=/speed-scratch/o_iseri/step9_run/logs/s9_audit_%j.out
#SBATCH --error=/speed-scratch/o_iseri/step9_run/logs/s9_audit_%j.err

# Audit: dump every ElectricEquipment + Lights object from one SF and one apt IDF
# to confirm double-count (SF) and Watts/Area no-op (NECB apt) mechanisms.
# Runs on the OLD activity IDFs from the pre-fix run.

. /encs/pkg/modules-5.3.1/root/init/bash

GCMAIN=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main
ROOT=/speed-scratch/o_iseri/step9_run
PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
S8DOCS=$GCMAIN/2J_docs_occ_nTemp/Step8_docs

echo "=== Step 9 IDF Audit ==="
echo "Node: $(hostname)  Date: $(date)"

export ENERGYPLUS_DIR=$ROOT

$PYTHON - <<'PYAUDIT'
import os, sys
sys.path.insert(0, "/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/2J_docs_occ_nTemp/Step8_docs")
sys.path.insert(0, "/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/2J_docs_occ_nTemp")

import glob as _g
from eSim_bem_utils_2J import config
from eppy.modeleditor import IDF

ROOT = "/speed-scratch/o_iseri/step9_run"
IDF.setiddname(config.resolve_idd_path())

CELLS = [
    ("SingleD__Winnipeg_7A",  "SF"),
    ("HighRise__Montreal_6A", "Apt"),
]

def get_zone(obj):
    for f in ('Zone_or_ZoneList_or_Space_or_SpaceList_Name',
              'Zone_or_ZoneList_Name', 'Zone_Name'):
        v = getattr(obj, f, None)
        if v: return str(v).strip()
    return str(obj.obj[2]).strip() if len(obj.obj) > 2 else '?'

for cell_label, tag in CELLS:
    pattern = f"{ROOT}/idfs/{cell_label}/activity/*/2022/Scenario_2022.idf"
    hits = sorted(_g.glob(pattern))
    if not hits:
        print(f"\n[{tag}] No IDF found at {pattern}")
        continue
    idf_path = hits[0]
    print(f"\n{'='*70}")
    print(f"[{tag}] {cell_label}")
    print(f"  IDF: {os.path.relpath(idf_path, ROOT)}")
    idf = IDF(idf_path)

    # People zone
    people = idf.idfobjects.get('PEOPLE', [])
    print(f"\n  People objects ({len(people)}):")
    for p in people:
        print(f"    {p.Name!s:35s} zone={get_zone(p)}")

    # Equipment
    equip = idf.idfobjects.get('ELECTRICEQUIPMENT', [])
    print(f"\n  ElectricEquipment objects ({len(equip)}):")
    print(f"  {'Name':35s} {'Method':20s} {'DL_W':>10s} {'WpA':>10s} {'Schedule':30s} Zone")
    for e in equip:
        m  = getattr(e, 'Design_Level_Calculation_Method', '?') or '?'
        dl = getattr(e, 'Design_Level', '')
        wpa= getattr(e, 'Watts_per_Zone_Floor_Area', '')
        sc = getattr(e, 'Schedule_Name', '') or ''
        zn = get_zone(e)
        dl_s = f"{float(dl):.1f}" if dl not in ('', None) else '-'
        wpa_s= f"{float(wpa):.3f}" if wpa not in ('', None) else '-'
        print(f"  {str(e.Name):35s} {m:20s} {dl_s:>10s} {wpa_s:>10s} {sc:30s} {zn}")

    # Lights
    lights = idf.idfobjects.get('LIGHTS', [])
    print(f"\n  Lights objects ({len(lights)}):")
    print(f"  {'Name':35s} {'Method':20s} {'LL_W':>10s} {'WpA':>10s} {'Schedule':30s} Zone")
    for l in lights:
        m  = getattr(l, 'Design_Level_Calculation_Method', '?') or '?'
        ll = getattr(l, 'Lighting_Level', '')
        wpa= getattr(l, 'Watts_per_Zone_Floor_Area', '')
        sc = getattr(l, 'Schedule_Name', '') or ''
        zn = get_zone(l)
        ll_s = f"{float(ll):.1f}" if ll not in ('', None) else '-'
        wpa_s= f"{float(wpa):.3f}" if wpa not in ('', None) else '-'
        print(f"  {str(l.Name):35s} {m:20s} {ll_s:>10s} {wpa_s:>10s} {sc:30s} {zn}")
PYAUDIT

echo "=== Audit DONE ==="
