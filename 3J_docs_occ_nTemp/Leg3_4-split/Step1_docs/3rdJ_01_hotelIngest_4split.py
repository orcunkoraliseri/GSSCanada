"""
3rdJ Step 1 -- Leg-3 (4-split) -- Hotel channel ingest + GSS reuse verification.

Section A -- GSS reuse verification (IMPLEMENTED).
    Leg-3 does no new GSS work at all: the Leg-1/Leg-2 Step-1 outputs
    (main_*.csv, episode_*.csv for 2005/2010/2015/2022) are reused verbatim,
    read-only. verify_gss_reuse() confirms those 8 files still exist with the
    exact expected row counts and records size + SHA-256 into a manifest so
    any drift in the Leg-2 chain is caught loudly, per the runbook
    (3rdJ_01_readingGSS_4split.md, "Section A -- GSS reuse verification").

Section B -- hotel raw ingest (PLANNED, Leg 3).
    Reads manually-downloaded ISQ (QC) / Alberta Economic Dashboard (AB) /
    CBRE archive (AB 2005-2009) files and assembles a first-pass
    hotel_occupancy_raw_assembled.csv. Blocked on manual downloads
    (see runbook "Manual acquisition step") -- stubbed only, not implemented
    in this pass.

Run locally (no cluster needed):
    py -3 -X utf8 3rdJ_01_hotelIngest_4split.py
"""

from __future__ import annotations

import csv
import hashlib
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent

# Leg-2 Step-1 outputs directory (read-only source; NEVER modified or copied).
LEG2_STEP1_DIR = (
    SCRIPT_DIR / ".." / ".." / "Leg2_2-split" / "Step1_docs" / "outputs_step1"
).resolve()

# Leg-3 Step-1 output directory (sibling of this script; created if missing).
OUTPUT_DIR = (SCRIPT_DIR / "outputs_step1").resolve()

MANIFEST_PATH = OUTPUT_DIR / "gss_reuse_manifest.csv"

# Section-B hotel raw inputs (transcribed from manual/open-data downloads).
HOTEL_RAW_DIR = (SCRIPT_DIR / "hotel_raw").resolve()
ISQ_QC_RAW = HOTEL_RAW_DIR / "ISQ_QC" / "isq_qc_province_monthly.csv"
# Alberta Tourism Market Monitor harvest (open.alberta.ca, OGLA), tidy long CSV
# YEAR,MONTH,GEO,metric,value,SOURCE,PROVENANCE,STATUS -- produced by the AB
# harvest step; may not exist yet.
AB_MKTMONITOR_RAW = (SCRIPT_DIR / ".." / "deepResearch_v2"
                     / "hotel_ab_monthly_2012_2022.csv").resolve()

ASSEMBLED_PATH = OUTPUT_DIR / "hotel_occupancy_raw_assembled.csv"

# Canonical hotel-channel window (per runbook): 2005-01 .. 2022-12, per province.
WINDOW_YEARS = range(2005, 2023)
PROVINCES = ("QC", "AB")

# Preferred AB geography for the provincial driver, in fallback order. The
# design driver is "Total Alberta excluding resorts"; Calgary (Zone 7A, the
# simulated market) is the documented fallback if that composite is absent.
AB_GEO_PREFERENCE = ("AlbertaExclResorts", "Calgary")

# Expected row counts (data rows, header excluded) -- from the runbook's
# "Data Source Inventory" §A table.
EXPECTED_ROWS = {
    "main_2005.csv": 19597,
    "main_2010.csv": 15390,
    "main_2015.csv": 17390,
    "main_2022.csv": 12336,
    "episode_2005.csv": 333654,
    "episode_2010.csv": 283287,
    "episode_2015.csv": 274108,
    "episode_2022.csv": 168078,
}

CHUNK_SIZE = 1024 * 1024  # 1 MiB streaming chunk for hashing / line counting


# ---------------------------------------------------------------------------
# Section A -- GSS reuse verification (IMPLEMENTED)
# ---------------------------------------------------------------------------


def _count_data_rows(path: Path) -> int:
    """Count data rows in a CSV (excludes the header row), streaming in
    fixed-size byte chunks so multi-hundred-MB episode files are never
    loaded into memory at once."""
    newline_count = 0
    last_byte = b""
    with open(path, "rb") as fh:
        while True:
            chunk = fh.read(CHUNK_SIZE)
            if not chunk:
                break
            newline_count += chunk.count(b"\n")
            last_byte = chunk[-1:]
    # If the file doesn't end with a trailing newline, the last line still
    # counts but wouldn't be captured by counting b"\n" alone.
    if last_byte and last_byte != b"\n":
        newline_count += 1
    # Subtract 1 for the header row.
    return max(newline_count - 1, 0)


def _sha256_of(path: Path) -> str:
    """Stream a file through SHA-256 in fixed-size chunks (never reads the
    whole file into memory at once)."""
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            chunk = fh.read(CHUNK_SIZE)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def verify_gss_reuse() -> bool:
    """Section A: for each of the 8 Leg-2 Step-1 CSVs, assert existence,
    assert exact row count, record size + SHA-256, and write one row per
    file to outputs_step1/gss_reuse_manifest.csv.

    Returns True iff all 8 files are OK (exist and row-count-exact).
    Exits the process non-zero (via caller) if any row is FAIL.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    rows = []
    all_ok = True

    for artifact, expected_rows in EXPECTED_ROWS.items():
        path = LEG2_STEP1_DIR / artifact
        exists = path.is_file()

        actual_rows = ""
        size_bytes = ""
        sha256_hex = ""
        status = "FAIL"

        if exists:
            actual_rows = _count_data_rows(path)
            size_bytes = path.stat().st_size
            sha256_hex = _sha256_of(path)
            status = "OK" if actual_rows == expected_rows else "FAIL"
        else:
            actual_rows = -1

        if status != "OK":
            all_ok = False

        rows.append(
            {
                "artifact": artifact,
                "path": str(path),
                "expected_rows": expected_rows,
                "actual_rows": actual_rows,
                "size_bytes": size_bytes,
                "sha256": sha256_hex,
                "status": status,
            }
        )

    with open(MANIFEST_PATH, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "artifact",
                "path",
                "expected_rows",
                "actual_rows",
                "size_bytes",
                "sha256",
                "status",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    ok_count = sum(1 for r in rows if r["status"] == "OK")
    total = len(rows)

    if all_ok:
        print(f"[Section A] GSS reuse verification: {ok_count}/{total} OK")
    else:
        print(
            f"[Section A] GSS reuse verification: {ok_count}/{total} OK "
            f"-- MISMATCH DETECTED, Leg-2 chain may have moved under us:"
        )
        for r in rows:
            if r["status"] != "OK":
                print(
                    f"    FAIL: {r['artifact']} -- expected {r['expected_rows']} "
                    f"rows, got {r['actual_rows']} (path={r['path']})"
                )

    print(f"[Section A] Manifest written to: {MANIFEST_PATH}")

    return all_ok


# ---------------------------------------------------------------------------
# Section B -- hotel raw ingest (IMPLEMENTED for the sources acquired so far).
#
# Provenance of the raw inputs (see project memory / runbook Progress Log):
#   QC -- ISQ "Enquete sur la frequentation des etablissements d'hebergement",
#         monthly provincial taux d'occupation + ADR + RevPAR, exported by hand
#         from the ISQ Power-BI dashboard (tab "Donnees mensuelles", filter
#         Territoire=Province) and transcribed to hotel_raw/ISQ_QC/ by
#         _transcribe_isq_qc_pdfs.py. Real coverage: 2019-2025 (2005-2018 GAP).
#   AB -- Alberta Tourism Market Monitor (open.alberta.ca, licence OGLA),
#         monthly, harvested + parsed into deepResearch_v2/
#         hotel_ab_monthly_2012_2022.csv. Coverage ~2012-2022.
#
# Each reader returns a list of dict records in the canonical schema:
#   {YEAR, MONTH, PR, occupancy_rate, ADR_CAD, RevPAR_CAD, SOURCE,
#    PROVENANCE, STATUS}
# occupancy_rate is a 0-1 fraction; missing metrics are "".
# ---------------------------------------------------------------------------

CANON_FIELDS = [
    "YEAR", "MONTH", "PR", "occupancy_rate", "ADR_CAD", "RevPAR_CAD",
    "SOURCE", "PROVENANCE", "STATUS",
]


def read_isq_qc(path: Path = ISQ_QC_RAW) -> list[dict]:
    """Read the transcribed ISQ QC provincial monthly series (stdlib only).
    Returns [] with a warning if the raw file is not present yet."""
    if not path.is_file():
        print(f"[Section B] read_isq_qc: raw file absent ({path}) -- skipping QC.")
        return []
    records = []
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            records.append({
                "YEAR": int(row["YEAR"]),
                "MONTH": int(row["MONTH"]),
                "PR": "QC",
                "occupancy_rate": row.get("occupancy_rate", "").strip(),
                "ADR_CAD": row.get("ADR_CAD", "").strip(),
                "RevPAR_CAD": row.get("RevPAR_CAD", "").strip(),
                "SOURCE": row.get("SOURCE", "ISQ").strip() or "ISQ",
                "PROVENANCE": row.get("PROVENANCE", "").strip(),
                "STATUS": row.get("STATUS", "OK").strip() or "OK",
            })
    print(f"[Section B] read_isq_qc: {len(records)} QC monthly rows from {path.name}")
    return records


def read_abdash_ab(path: Path = AB_MKTMONITOR_RAW,
                   geo_preference: tuple = AB_GEO_PREFERENCE) -> list[dict]:
    """Read the Alberta Tourism Market Monitor harvest (tidy long CSV) and pivot
    it into the canonical schema for PR=AB. Picks the first GEO available in
    `geo_preference` as the provincial driver (occupancy + ADR). Returns [] with
    a warning if the harvest CSV is not present yet (AB harvest still running)."""
    if not path.is_file():
        print(f"[Section B] read_abdash_ab: harvest absent ({path.name}) -- skipping AB.")
        return []

    # Gather value by (geo, year, month, metric).
    by_key: dict = {}
    geos_seen = set()
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            geo = (row.get("GEO") or "").strip()
            metric = (row.get("metric") or "").strip()
            val = (row.get("value") or "").strip()
            if not geo or not metric:
                continue
            geos_seen.add(geo)
            try:
                y, m = int(row["YEAR"]), int(row["MONTH"])
            except (ValueError, KeyError):
                continue
            by_key[(geo, y, m, metric)] = (val, (row.get("PROVENANCE") or "").strip())

    geo = next((g for g in geo_preference if g in geos_seen), None)
    if geo is None:
        print(f"[Section B] read_abdash_ab: no preferred GEO in {sorted(geos_seen)} "
              f"-- skipping AB.")
        return []

    months = sorted({(y, m) for (g, y, m, _) in by_key if g == geo})
    records = []
    for (y, m) in months:
        occ, prov = by_key.get((geo, y, m, "occupancy_rate"), ("", ""))
        adr, _ = by_key.get((geo, y, m, "ADR_CAD"), ("", ""))
        if not occ:
            continue
        records.append({
            "YEAR": y, "MONTH": m, "PR": "AB",
            "occupancy_rate": occ, "ADR_CAD": adr, "RevPAR_CAD": "",
            "SOURCE": "ABMKTMONITOR",
            "PROVENANCE": prov or f"Alberta Tourism Market Monitor, GEO={geo}",
            "STATUS": "OK",
        })
    print(f"[Section B] read_abdash_ab: {len(records)} AB monthly rows "
          f"(GEO={geo}) from {path.name}")
    return records


def read_cbre_ab_archive(*args, **kwargs) -> list[dict]:
    # Optional AB 2005-2009 gap fill from the proprietary CBRE archive.
    # Not acquired -- those months stay GAP (documented pipeline fallback:
    # truncate AB SARIMA training, or TASPI backcast regressor).
    return []


def assemble_raw_monthly(out_path: Path = ASSEMBLED_PATH) -> dict:
    """Section B assembler: build the full 2005-2022 x {QC,AB} monthly grid,
    fill it from the available readers, mark every unfilled cell GAP, and write
    outputs_step1/hotel_occupancy_raw_assembled.csv. Returns a small coverage
    summary dict. This is deliberately non-fatal: absent sources -> GAP rows,
    never an exception, so the step is runnable at any acquisition stage."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    observed = {}  # (PR, YEAR, MONTH) -> record
    for rec in (read_isq_qc() + read_abdash_ab() + read_cbre_ab_archive()):
        if rec["YEAR"] in WINDOW_YEARS and rec.get("occupancy_rate"):
            observed[(rec["PR"], rec["YEAR"], rec["MONTH"])] = rec

    rows = []
    coverage = {pr: {"OK": 0, "GAP": 0} for pr in PROVINCES}
    for pr in PROVINCES:
        for year in WINDOW_YEARS:
            for month in range(1, 13):
                rec = observed.get((pr, year, month))
                if rec:
                    rows.append({k: rec.get(k, "") for k in CANON_FIELDS})
                    coverage[pr]["OK"] += 1
                else:
                    rows.append({
                        "YEAR": year, "MONTH": month, "PR": pr,
                        "occupancy_rate": "", "ADR_CAD": "", "RevPAR_CAD": "",
                        "SOURCE": "ISQ" if pr == "QC" else "ABMKTMONITOR",
                        "PROVENANCE": "", "STATUS": "GAP",
                    })
                    coverage[pr]["GAP"] += 1

    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CANON_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[Section B] Assembled raw monthly -> {out_path}")
    for pr in PROVINCES:
        c = coverage[pr]
        total = c["OK"] + c["GAP"]
        print(f"[Section B]   {pr}: {c['OK']}/{total} OK ({c['GAP']} GAP)")
    return coverage


# ---------------------------------------------------------------------------
# __main__
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    ok = verify_gss_reuse()

    # Section B -- hotel raw ingest. Non-fatal: assembles whatever sources are
    # present (QC now; AB when the Market Monitor harvest lands) and marks the
    # rest GAP. Never blocks Section A's exit status.
    print()
    assemble_raw_monthly()

    if not ok:
        sys.exit(1)
    sys.exit(0)
