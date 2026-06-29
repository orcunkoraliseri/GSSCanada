"""office_runner.py — Step 8C: Office campaign single-run driver (3J Leg-2).

One invocation = one deterministic EnergyPlus run for a single
(office_archetype × envelope × CZ × scenario) cell.

SLURM usage (see run_office_array.sh):
    Cell index SLURM_ARRAY_TASK_ID ∈ [0..251]
    idx → (arch_idx, env_idx, cz_idx, scen_idx) via int division / modulo.

Local smoke-test usage:
    py office_runner.py \\
        --archetype Office_Knowledge \\
        --envelope  Tall \\
        --cz        6A \\
        --scenario  2022 \\
        --out-dir   outputs_step8/office

The script:
  1. Locates the v24.2 office IDF (from outputs_step8/office_idfs_v242/).
  2. Locates the EPW for the CZ (from BEM_Setup/WeatherFile/).
  3. Calls office_integration.inject_office_schedules() → modified IDF.
  4. Runs EnergyPlus 24.2 via the Singularity SIF.
  5. Parses hourly meters from eplusout.sql → hourly_meters.csv (8760 rows).

Cluster-side python: /speed-scratch/o_iseri/envs/step4/bin/python
Cluster-side SIF   : /speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif

2026-06-28 built.
"""
from __future__ import annotations
import os
import sys
import argparse
import subprocess
import sqlite3
import csv
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent  # Step8_docs/
sys.path.insert(0, str(HERE))

# ---------------------------------------------------------------------------
# Scenario → BAND mapping (office multiplier uses BAND, not year label)
# ---------------------------------------------------------------------------
SCENARIO_TO_BAND = {
    "2005":                "observed",
    "2010":                "observed",
    "2015":                "observed",
    "2022":                "observed",
    "2030-conservative":   "conservative",
    "2030-hybrid":         "hybrid",
    "2030-fullyhybrid":    "fullyhybrid",
}

SCENARIO_TO_YEAR = {
    "2005": "2005", "2010": "2010", "2015": "2015", "2022": "2022",
    "2030-conservative": "2030", "2030-hybrid": "2030", "2030-fullyhybrid": "2030",
}

# CZ → (envelope_family, EPW city substring)
CZ_MAP = {
    "5A": ("CAN_MTL", "Toronto"),
    "5B": ("CAN_MTL", "Kelowna"),
    "5C": ("CAN_MTL", "Vancouver"),
    "6A": ("CAN_MTL", "Montreal"),
    "6B": ("CAN_MTL", "Calgary"),
    "7A": ("CAN_CLG", "Winnipeg"),
}
# The two envelope building sizes
ENVELOPE_IDF_SUBSTR = {
    "Tall":      "TallBuilding",
    "SuperTall": "SuperTallBuilding",
}

VALID_ARCHETYPES = {"Office_Knowledge", "Office_Public", "Office_Sales"}
VALID_ENVELOPES  = {"Tall", "SuperTall"}
VALID_CZ         = set(CZ_MAP)

ARCHETYPES = sorted(VALID_ARCHETYPES)
ENVELOPES  = ["Tall", "SuperTall"]
CZ_LIST    = ["5A", "5B", "5C", "6A", "6B", "7A"]
SCENARIOS  = ["2005", "2010", "2015", "2022",
               "2030-conservative", "2030-hybrid", "2030-fullyhybrid"]

# Singularity SIF path (cluster; overridable via env var)
DEFAULT_SIF = "/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif"
SIF = os.environ.get("EPLUS_SIF", DEFAULT_SIF)


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------
def _find_one(folder: str, ext: str, substr: str) -> str | None:
    import glob as _g
    hits = [p for p in _g.glob(os.path.join(folder, f"*{ext}"))
            if substr.lower() in os.path.basename(p).lower()]
    return hits[0] if hits else None


def _locate_idf(step8_docs: Path, envelope: str, cz: str) -> str:
    """Find the v24.2 office IDF for this (envelope, CZ) pair."""
    env_family, _ = CZ_MAP[cz]
    idf_dir = step8_docs / "outputs_step8" / "office_idfs_v242" / env_family
    substr   = ENVELOPE_IDF_SUBSTR[envelope]
    path = _find_one(str(idf_dir), ".idf", substr)
    if path is None:
        raise FileNotFoundError(
            f"Office IDF not found for envelope={envelope}, cz={cz} "
            f"(family={env_family}, substr='{substr}') in {idf_dir}\n"
            f"Run 3rdJ_08C0_idf_transition.sh first."
        )
    return path


def _locate_epw(base_dir: Path, cz: str) -> str:
    _, city_substr = CZ_MAP[cz]
    epw_dir = base_dir / "BEM_Setup" / "WeatherFile"
    path = _find_one(str(epw_dir), ".epw", city_substr)
    if path is None:
        raise FileNotFoundError(
            f"EPW not found for CZ={cz} (city='{city_substr}') in {epw_dir}"
        )
    return path


def _locate_multiplier_csv(step8_docs: Path, scenario: str) -> str:
    year = SCENARIO_TO_YEAR[scenario]
    s7_out = step8_docs.parent / "Step7_docs" / "outputs_step7"
    hist   = step8_docs / "outputs_step8" / "historical_schedules"
    candidates = [
        hist / f"office_presence_multiplier_{year}.csv",
        s7_out / f"office_presence_multiplier_{year}.csv",
        s7_out / f"office_presence_multiplier_2030.csv",  # fallback for 2030 bands
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    raise FileNotFoundError(
        f"office_presence_multiplier for scenario={scenario} (year={year}) not found. "
        f"Searched: {candidates}"
    )


# ---------------------------------------------------------------------------
# EnergyPlus runner
# ---------------------------------------------------------------------------
def run_energyplus_via_sif(idf_path: str, epw_path: str, out_dir: str) -> int:
    """Run EnergyPlus 24.2 via Singularity SIF. Returns exit code."""
    os.makedirs(out_dir, exist_ok=True)
    idf_abs = os.path.abspath(idf_path)
    epw_abs = os.path.abspath(epw_path)
    # Use --bind to expose both the IDF dir and output dir inside the container
    idf_dir = os.path.dirname(idf_abs)
    cmd = [
        "singularity", "exec",
        "--bind", f"{idf_dir}:{idf_dir}",
        "--bind", f"{os.path.abspath(out_dir)}:{os.path.abspath(out_dir)}",
        "--bind", f"{os.path.dirname(epw_abs)}:{os.path.dirname(epw_abs)}",
        SIF,
        "/EnergyPlus/energyplus",
        "-d", os.path.abspath(out_dir),
        "-w", epw_abs,
        "-r",       # expand objects
        idf_abs,
    ]
    print(f"  [E+] {' '.join(cmd[:6])} ... {os.path.basename(idf_abs)}", flush=True)
    proc = subprocess.run(cmd, capture_output=False, text=True)
    return proc.returncode


# ---------------------------------------------------------------------------
# Hourly meter extraction
# ---------------------------------------------------------------------------
def _extract_hourly_meters(out_dir: str) -> str | None:
    """Parse eplusout.sql → hourly_meters.csv. Return path or None if failed."""
    sql = os.path.join(out_dir, "eplusout.sql")
    if not os.path.exists(sql):
        return None
    out_csv = os.path.join(out_dir, "hourly_meters.csv")
    try:
        conn = sqlite3.connect(sql)
        cur = conn.cursor()
        # Collect all Meter (type=2) hourly (interval=1) report variable keys
        cur.execute("""
            SELECT rv.ReportVariableIndex, rv.KeyValue, rv.Name, rv.Units
            FROM ReportVariableIndexes rv
            JOIN ReportVariableData_Dictionary rdd ON rv.ReportVariableIndex = rdd.ReportVariableIndex
            WHERE rdd.ReportDataDictionaryIndex IN (
                SELECT ReportDataDictionaryIndex FROM ReportDataDictionary
                WHERE ReportingFrequency = 'Hourly'
            )
        """)
        vars_map = {}
        for row in cur.fetchall():
            vars_map[row[0]] = f"{row[1]}:{row[2]} [{row[3]}]"
    except Exception:
        # Try simpler query (schema varies between E+ versions)
        try:
            conn = sqlite3.connect(sql)
            cur = conn.cursor()
            cur.execute("SELECT ReportDataDictionaryIndex, KeyValue, Name, Units "
                        "FROM ReportDataDictionary WHERE ReportingFrequency='Hourly'")
            vars_map = {row[0]: f"{row[1]}:{row[2]} [{row[3]}]" for row in cur.fetchall()}
        except Exception as e2:
            print(f"  WARN: could not parse sql ({e2}); hourly_meters.csv not written.")
            conn.close()
            return None

    try:
        cur.execute("SELECT ReportDataDictionaryIndex, TimeIndex, Value FROM ReportData "
                    "ORDER BY TimeIndex, ReportDataDictionaryIndex")
        rows = cur.fetchall()
    except Exception:
        conn.close()
        return None
    conn.close()

    if not rows:
        print("  WARN: no ReportData rows in sql.")
        return None

    # Pivot: rows per hour, columns per variable
    from collections import defaultdict
    by_hour: dict = defaultdict(dict)
    for dict_idx, t_idx, val in rows:
        col = vars_map.get(dict_idx, str(dict_idx))
        by_hour[t_idx][col] = val

    hours_sorted = sorted(by_hour.keys())
    if len(hours_sorted) not in (8760, 8784):
        print(f"  WARN: expected 8760/8784 hours, got {len(hours_sorted)}")

    all_cols = sorted({c for h in by_hour.values() for c in h})
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["Hour"] + all_cols)
        w.writeheader()
        for hour_i, t in enumerate(hours_sorted, 1):
            row = {"Hour": hour_i}
            row.update({c: by_hour[t].get(c, 0.0) for c in all_cols})
            w.writerow(row)
    print(f"  hourly_meters.csv: {len(hours_sorted)} rows, {len(all_cols)} vars → {out_csv}")
    return out_csv


# ---------------------------------------------------------------------------
# Main entry
# ---------------------------------------------------------------------------
def run_office_cell(
    archetype: str, envelope: str, cz: str, scenario: str,
    out_root: str, step8_docs: Path, base_dir: Path,
    skip_done: bool = True,
) -> dict:
    band  = SCENARIO_TO_BAND[scenario]
    label = f"{archetype}__{envelope}__{cz}"
    cell_dir = os.path.join(out_root, label, scenario)

    if skip_done and os.path.exists(os.path.join(cell_dir, "hourly_meters.csv")):
        print(f"[SKIP] {label}/{scenario} already has hourly_meters.csv.")
        return {"status": "skipped", "cell": label, "scenario": scenario}

    os.makedirs(cell_dir, exist_ok=True)

    idf_orig = _locate_idf(step8_docs, envelope, cz)
    epw      = _locate_epw(base_dir, cz)
    mult_csv = _locate_multiplier_csv(step8_docs, scenario)

    print(f"\n=== Office cell: {label} | scenario={scenario} ===")
    print(f"  IDF    : {os.path.basename(idf_orig)}")
    print(f"  EPW    : {os.path.basename(epw)}")
    print(f"  MultCSV: {os.path.basename(mult_csv)}")
    print(f"  Band   : {band}", flush=True)

    # Copy IDF to cell_dir so each run writes its own outputs
    from office_integration import inject_office_schedules
    mod_idf = os.path.join(cell_dir, f"Office_{archetype}_{envelope}_{cz}_{scenario}.idf")
    inject_office_schedules(
        idf_path=idf_orig,
        output_path=mod_idf,
        multiplier_csv=mult_csv,
        office_archetype=archetype,
        band=band,
    )

    rc = run_energyplus_via_sif(mod_idf, epw, cell_dir)
    if rc != 0:
        print(f"  WARN: EnergyPlus returned exit code {rc}")

    hourly = _extract_hourly_meters(cell_dir)
    status = "ok" if (hourly and rc == 0) else ("ep_warn" if hourly else "fail")

    end_file = os.path.join(cell_dir, "eplusout.end")
    ep_success = False
    if os.path.exists(end_file):
        with open(end_file) as f:
            ep_success = "Completed Successfully" in f.read()

    return {
        "status": status, "cell": label, "scenario": scenario,
        "ep_success": ep_success, "hourly_csv": hourly,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell-idx",   type=int, default=None,
                    help="SLURM_ARRAY_TASK_ID [0..251]; overrides all --arch/env/cz/scenario")
    ap.add_argument("--archetype",  default=None)
    ap.add_argument("--envelope",   default=None, choices=ENVELOPES)
    ap.add_argument("--cz",         default=None, choices=CZ_LIST)
    ap.add_argument("--scenario",   default=None)
    ap.add_argument("--out-dir",    default=None)
    ap.add_argument("--no-skip",    action="store_true")
    args = ap.parse_args()

    step8_docs = HERE
    base_dir   = step8_docs.parent.parent.parent  # GSSCanada-main/
    out_root   = args.out_dir or str(step8_docs / "outputs_step8" / "office")

    if args.cell_idx is not None:
        idx = args.cell_idx
        na, ne, nc, ns = len(ARCHETYPES), len(ENVELOPES), len(CZ_LIST), len(SCENARIOS)
        if not (0 <= idx < na * ne * nc * ns):
            raise ValueError(f"--cell-idx {idx} out of range [0, {na*ne*nc*ns-1}]")
        scen_idx = idx % ns
        cz_idx   = (idx // ns) % nc
        env_idx  = (idx // (ns * nc)) % ne
        arch_idx = idx // (ns * nc * ne)
        archetype = ARCHETYPES[arch_idx]
        envelope  = ENVELOPES[env_idx]
        cz        = CZ_LIST[cz_idx]
        scenario  = SCENARIOS[scen_idx]
        print(f"[cell-idx={idx}] arch={archetype} env={envelope} cz={cz} scen={scenario}")
    else:
        if not all([args.archetype, args.envelope, args.cz, args.scenario]):
            ap.error("Provide --cell-idx OR (--archetype --envelope --cz --scenario)")
        archetype = args.archetype
        envelope  = args.envelope
        cz        = args.cz
        scenario  = args.scenario

    result = run_office_cell(
        archetype=archetype, envelope=envelope, cz=cz, scenario=scenario,
        out_root=out_root, step8_docs=step8_docs, base_dir=base_dir,
        skip_done=not args.no_skip,
    )
    print(f"\nResult: {result}")


if __name__ == "__main__":
    main()
