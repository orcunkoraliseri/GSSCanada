"""P10R: stage the self-contained upload tree for the Speed campaign (local, copies only; no network).

Builds <stage>/repo/<repo-relative path> for every file the P10R cell runner reads, plus
<stage>/mirror_md5.txt ("md5  relpath"), <stage>/logs/ and <stage>/campaign_P10R/ (empty). The manager
then uploads it with ONE scp -r (see P10R_fix.md). In-job, p10r_verify_mirror.py re-checks every md5.

    py -3 p10r_stage_speed.py [STAGE_DIR]     (default C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/P10R_speed_stage)
"""
import hashlib, shutil, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
J3 = "3J_docs_occ_nTemp"
L3 = f"{J3}/Leg3_4-split"
STAGE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/P10R_speed_stage")


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


files = sorted(p.relative_to(REPO).as_posix() for p in (REPO / "eSim/eSim_bem_utils").glob("*.py"))
files += [f"{L3}/Step8_docs/{n}" for n in ("3rdJ_08P_probe_driver.py", "3rdJ_08D_campaign_cells.py",
                                           "3rdJ_08D_campaign_cell_P10R.py", "3rdJ_08D_campaign_P10R_speed.sh")]
files += [f"{L3}/Step9_docs/{n}" for n in ("3rdJ_09J_retail_necb_c.py", "3rdJ_09H_plant_resize_probe.py",
                                           "3rdJ_09H_dhw_plant_topology.py", "3rdJ_09H_resize_campaign_cell.py",
                                           "3rdJ_09H_hotel_dT_decompose.py")]
files += [f"{J3}/writing/implementation/IMP/scripts/p10r_verify_mirror.py"]
files += sorted(p.relative_to(REPO).as_posix() for p in (REPO / L3 / "Step7_docs/outputs_step7_P10R").glob("*")
                if "_BAK_" not in p.name)
files += sorted(p.relative_to(REPO).as_posix() for p in (REPO / L3 / "Step8_docs/outputs_step8/historical_schedules").glob("*.csv"))
for city, tag in (("CAN_MTL", "Z6"), ("CAN_CLG", "Z7A")):
    for b in ("Tall", "SuperTall"):
        files.append(f"{J3}/Leg2_2-split/Step8_docs/outputs_step8/office_idfs_v242/{city}/"
                     f"{b}Building_90.1-2019_6A_Buffalo_NECB17_{tag}_v242.idf")
files += ["BEM_Setup/WeatherFile/CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx_6A.epw",
          "BEM_Setup/WeatherFile/CAN_AB_Calgary-Canadian.Olympic.Park.Upper.712350_TMYx_6B.epw"]

lines, total = [], 0
for rel in files:
    src = REPO / rel
    if not src.is_file():
        raise SystemExit(f"REFUSING: missing {src}")
    dst = STAGE / "repo" / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    m = md5(dst)
    assert m == md5(src), rel
    lines.append(f"{m}  {rel}")
    total += dst.stat().st_size
idd = Path(r"C:\EnergyPlusV24-2-0\Energy+.idd")
shutil.copy2(idd, STAGE / "repo/Energy+.idd")
lines.append(f"{md5(STAGE / 'repo/Energy+.idd')}  Energy+.idd")
(STAGE / "logs").mkdir(exist_ok=True)
(STAGE / "campaign_P10R").mkdir(exist_ok=True)
(STAGE / "mirror_md5.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
(STAGE / "repo" / "mirror_md5.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"staged {len(lines)} files, {total / 1e6:.1f} MB (+ IDD) -> {STAGE}")
print(f"md5 list: {STAGE / 'mirror_md5.txt'}")
