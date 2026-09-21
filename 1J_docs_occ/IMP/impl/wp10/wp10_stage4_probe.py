"""
WP10 Stage 4: cheap, non-EnergyPlus probe of whether the REAL draw_manifest.csv's
household ids can actually be found in the CURRENTLY STAGED BEM_Schedules_{year}.csv
files, for all six neighbourhoods, draw 1. No simulation is run -- this only loads
the five schedule CSVs once (integration.load_schedules, region='Quebec', the same
call _run_mc_neighbourhood makes) and calls the real, patched
_wp10_select_households_for_draw() for each neighbourhood.

Written because a manual sample (10 households, NUS_RC1 draw 1) found the manifest's
own hh_pr disagreeing with the staged April file's PR column for 2 of 10 households
(hh_id 31360: manifest says Quebec, staged 2005 file says Ontario; hh_id 2750:
manifest says Quebec, staged 2015 file says Atlantic) -- since
integration.load_schedules(..., region='Quebec') drops any row whose PR != 'Quebec',
those two households would not even be loaded into all_schedules[year], which the
manifest-driven selection has no fallback for (by design -- Ruling B, G4.1).

Run: (cluster) /speed-scratch/o_iseri/GSSCanada/venv/bin/python wp10_stage4_probe.py
"""
import sys

sys.path.insert(0, "/speed-scratch/o_iseri/1J_rerun/code")
import eSim_bem_utils.main as m  # noqa: E402
from eSim_bem_utils import integration, neighbourhood  # noqa: E402

NEIGHBOURHOODS = ["NUS_RC1", "NUS_RC2", "NUS_RC3", "NUS_RC4", "NUS_RC5", "NUS_RC6"]
IDF_DIR = "/speed-scratch/o_iseri/1J_rerun/code/BEM_Setup/Neighbourhoods"
MANIFEST_PATH = "/speed-scratch/o_iseri/1J_rerun/stage2/draw_manifest.csv"


def main():
    manifest_lookup = m._load_mc_draw_manifest(MANIFEST_PATH)

    schedule_files = m._build_schedule_file_map()
    all_schedules = {}
    for year, csv_path in schedule_files.items():
        schedules = integration.load_schedules(csv_path, dwelling_type=None, region="Quebec")
        all_schedules[year] = schedules
        print(f"PROBE: loaded {year} -> {len(schedules)} households after Quebec filter, from {csv_path}")

    year_scenarios = list(m.COMPARATIVE_YEARS)

    summary = {}
    for nu in NEIGHBOURHOODS:
        idf_path = f"{IDF_DIR}/{nu}.idf"
        building_dtypes = neighbourhood.get_building_dtypes_from_idf(idf_path)
        n_buildings = len(building_dtypes)
        print(f"PROBE: {nu} n_buildings={n_buildings} dtypes={building_dtypes}")

        try:
            result = m._wp10_select_households_for_draw(
                nu, 1, year_scenarios, all_schedules, n_buildings, manifest_lookup
            )
            print(f"PROBE: {nu} draw 1 -- SUCCEEDED, all manifest households found in staged schedules")
            for year in year_scenarios:
                ids = [r["hh_id"] for r in result.get(year, [])]
                print(f"  {nu} {year}: {ids}")
            summary[nu] = "OK"
        except RuntimeError as e:
            print(f"PROBE: {nu} draw 1 -- FAILED: {e}")
            summary[nu] = f"FAILED: {e}"

    print()
    print("PROBE SUMMARY:")
    for nu in NEIGHBOURHOODS:
        print(f"  {nu}: {summary[nu]}")
    n_ok = sum(1 for v in summary.values() if v == "OK")
    print(f"PROBE SUMMARY: {n_ok} of {len(NEIGHBOURHOODS)} neighbourhoods would succeed at draw 1 "
          f"with the CURRENTLY STAGED BEM_Schedules_{{year}}.csv files")
    print("PROBE DONE")


if __name__ == "__main__":
    main()
