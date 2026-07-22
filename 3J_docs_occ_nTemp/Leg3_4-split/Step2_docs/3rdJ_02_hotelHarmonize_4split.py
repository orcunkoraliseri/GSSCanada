"""
3rdJ Step 2 -- Leg-3 (4-split) -- Hotel series harmonization (Delta D).

Turns the Step-1 raw assembly (hotel_occupancy_raw_assembled.csv, full
2005-2022 x {QC,AB} grid with GAP-marked cells) into the CANONICAL monthly
series the downstream SARIMA (Step 6) consumes:

    0_Occupancy/external/hotel_occupancy_monthly.csv
        YEAR, MONTH, PR, occupancy_rate, ADR_CAD, RevPAR_CAD, SOURCE, SPLICED

plus a validation copy in outputs_step2/ and an optional market-level side
file (Calgary / Edmonton) for validation context only.

What harmonization does here (the GSS side needs no re-run -- retail lives in
the reused Leg-2 episodes and is validated by the sibling validator):

  1. Load the Step-1 grid (both provinces, all 216 months each; observed +
     GAP rows).
  2. AB splice at the Jan-2010 boundary (dr_L3-01):
         Occupancy_Spliced = Occupancy_CBRE x mean(ABDASH_2010)/mean(CBRE_2010)
     is only meaningful if a pre-2010 CBRE provincial series exists to splice
     ONTO the dashboard series. It does NOT (read_cbre_ab_archive returned []
     at Step 1 -- the proprietary CBRE archive was not obtained). So the
     documented Delta-D fallback applies: emit the single-source Market Monitor
     AB series (2011-2022), SPLICED = 0 on every row, and record the decision.
     The Step-6 SARIMA level-shift dummy D_splice is therefore moot.
  3. Finalize the canonical schema: drop the long PROVENANCE prose (it lives in
     the Step-1 raw assembly for audit), add the SPLICED provenance flag, keep
     the full 2005-2022 grid so GAP months are explicit (blank occupancy_rate;
     Step-6 truncates training to each province's covered window -- NOT imputed
     here).

Run locally (no cluster):
    py -3 -X utf8 3rdJ_02_hotelHarmonize_4split.py
"""

from __future__ import annotations

import csv
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

# Step-1 raw assembly (read-only input).
STEP1_ASSEMBLED = (
    SCRIPT_DIR / ".." / "Step1_docs" / "outputs_step1"
    / "hotel_occupancy_raw_assembled.csv"
).resolve()

# Optional market-level long CSV (Calgary / Edmonton / Resorts) from the AB
# harvest -- used only to emit the non-gated markets side file if present.
AB_MARKETS_LONG = (
    SCRIPT_DIR / ".." / "deepResearch_v2" / "hotel_ab_monthly_2012_2022.csv"
).resolve()

# Canonical output (repo external dir) + validation copy.
EXTERNAL_DIR = (SCRIPT_DIR / ".." / ".." / ".." / "0_Occupancy" / "external").resolve()
CANONICAL_PATH = EXTERNAL_DIR / "hotel_occupancy_monthly.csv"

OUTPUT_DIR = (SCRIPT_DIR / "outputs_step2").resolve()
CANONICAL_COPY = OUTPUT_DIR / "hotel_occupancy_monthly.csv"
MARKETS_COPY = OUTPUT_DIR / "hotel_occupancy_monthly_markets.csv"

WINDOW_YEARS = range(2005, 2023)
PROVINCES = ("QC", "AB")

CANON_FIELDS = [
    "YEAR", "MONTH", "PR", "occupancy_rate", "ADR_CAD", "RevPAR_CAD",
    "SOURCE", "SPLICED",
]

# Market-level geographies to carry through to the side file (occupancy only).
AB_MARKET_GEOS = ("Calgary", "Edmonton", "AlbertaResorts")


# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------

def load_raw_assembly(path: Path = STEP1_ASSEMBLED) -> list[dict]:
    """Read the Step-1 assembly. Returns the full grid as dict rows with a
    parsed float `_occ` (None on GAP)."""
    if not path.is_file():
        raise FileNotFoundError(
            f"Step-1 assembly missing: {path}\n"
            f"Run 3rdJ_01_hotelIngest_4split.py first.")
    rows = []
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            r["YEAR"], r["MONTH"] = int(r["YEAR"]), int(r["MONTH"])
            occ = (r.get("occupancy_rate") or "").strip()
            r["_occ"] = float(occ) if occ else None
            rows.append(r)
    return rows


# ---------------------------------------------------------------------------
# Delta-D step 2 -- AB splice (moot fallback path)
# ---------------------------------------------------------------------------

def splice_ab_2010(rows: list[dict]) -> dict:
    """Apply the dr_L3-01 AB Jan-2010 splice IF a pre-2010 CBRE provincial
    series is present to splice onto the dashboard series.

    In the acquired reality the AB series is single-source (Alberta Tourism
    Market Monitor, SOURCE=ABMKTMONITOR, starting 2011) with no CBRE archive,
    so there is nothing to splice: SPLICED is set to 0 on every AB row and the
    calibration factor is undefined. Returns a small decision record for the
    Progress Log / validator. QC never needs splicing.
    """
    ab_sources = {r["SOURCE"] for r in rows
                  if r["PR"] == "AB" and r["_occ"] is not None}
    has_cbre = "CBRE" in ab_sources

    for r in rows:
        r["SPLICED"] = "0"

    if not has_cbre:
        first_ab = min((r["YEAR"] * 12 + r["MONTH"] for r in rows
                        if r["PR"] == "AB" and r["_occ"] is not None),
                       default=None)
        span = (f"{first_ab // 12}-{first_ab % 12:02d}" if first_ab else "none")
        return {
            "applied": False,
            "reason": (
                "no CBRE pre-2010 series acquired -- single-source Market "
                f"Monitor AB (starts {span}); splice + D_splice dummy moot; "
                "Step-6 truncates AB SARIMA training to the covered window"),
            "factor": None,
            "ab_sources": sorted(ab_sources),
        }

    # Splice path (kept for completeness -- not exercised without CBRE).
    def _mean(pr, y0, m0, y1, m1, src=None):
        vals = [r["_occ"] for r in rows if r["PR"] == pr and r["_occ"] is not None
                and (y0, m0) <= (r["YEAR"], r["MONTH"]) <= (y1, m1)
                and (src is None or r["SOURCE"] == src)]
        return sum(vals) / len(vals) if vals else None

    dash_2010 = _mean("AB", 2010, 1, 2010, 12, src="ABMKTMONITOR")
    cbre_2010 = _mean("AB", 2010, 1, 2010, 12, src="CBRE")
    factor = (dash_2010 / cbre_2010) if (dash_2010 and cbre_2010) else 1.0
    for r in rows:
        if r["PR"] == "AB" and r["SOURCE"] == "CBRE" and r["_occ"] is not None:
            r["_occ"] = round(r["_occ"] * factor, 4)
            r["occupancy_rate"] = f"{r['_occ']:.4f}"
            r["SPLICED"] = "1"
    return {"applied": True, "reason": "CBRE spliced onto dashboard level",
            "factor": factor, "ab_sources": sorted(ab_sources)}


# ---------------------------------------------------------------------------
# Finalize canonical schema
# ---------------------------------------------------------------------------

def finalize_schema(rows: list[dict]) -> list[dict]:
    """Project onto the canonical column set, preserving the full grid (GAP
    months kept with blank occupancy). Sorted PR, YEAR, MONTH."""
    out = []
    for r in sorted(rows, key=lambda x: (x["PR"], x["YEAR"], x["MONTH"])):
        occ = r.get("occupancy_rate") or ""
        out.append({
            "YEAR": r["YEAR"], "MONTH": r["MONTH"], "PR": r["PR"],
            "occupancy_rate": (f"{float(occ):.4f}" if occ else ""),
            "ADR_CAD": (r.get("ADR_CAD") or "").strip(),
            "RevPAR_CAD": (r.get("RevPAR_CAD") or "").strip(),
            "SOURCE": (r.get("SOURCE") or "").strip(),
            "SPLICED": r.get("SPLICED", "0"),
        })
    return out


def _write(path: Path, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


# ---------------------------------------------------------------------------
# Optional market-level side file (validation context only, non-gated)
# ---------------------------------------------------------------------------

def build_markets_side_file(path: Path = AB_MARKETS_LONG) -> int:
    """Emit occupancy for Calgary / Edmonton / AlbertaResorts from the AB
    harvest long CSV, so the reviewer can see the market composition behind the
    'AlbertaExclResorts' provincial driver. Non-gated; skipped if the harvest
    long CSV is absent. Returns the number of rows written (0 if skipped)."""
    if not path.is_file():
        print(f"[markets] AB harvest long CSV absent ({path.name}) -- side file skipped.")
        return 0
    rows = []
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            geo = (r.get("GEO") or "").strip()
            metric = (r.get("metric") or "").strip()
            val = (r.get("value") or "").strip()
            if geo not in AB_MARKET_GEOS or metric != "occupancy_rate" or not val:
                continue
            try:
                y, m = int(r["YEAR"]), int(r["MONTH"])
            except (ValueError, KeyError):
                continue
            if y not in WINDOW_YEARS:
                continue
            rows.append({"YEAR": y, "MONTH": m, "PR": "AB", "MARKET": geo,
                         "occupancy_rate": f"{float(val):.4f}"})
    rows.sort(key=lambda x: (x["MARKET"], x["YEAR"], x["MONTH"]))
    _write(MARKETS_COPY, ["YEAR", "MONTH", "PR", "MARKET", "occupancy_rate"], rows)
    geos = sorted({r["MARKET"] for r in rows})
    print(f"[markets] {len(rows)} market-level rows ({geos}) -> {MARKETS_COPY.name}")
    return len(rows)


# ---------------------------------------------------------------------------
# __main__
# ---------------------------------------------------------------------------

def main() -> None:
    rows = load_raw_assembly()
    decision = splice_ab_2010(rows)
    canon = finalize_schema(rows)

    _write(CANONICAL_PATH, CANON_FIELDS, canon)
    _write(CANONICAL_COPY, CANON_FIELDS, canon)
    build_markets_side_file()

    # Coverage summary (observed months per PR).
    cov = {pr: sum(1 for r in canon if r["PR"] == pr and r["occupancy_rate"])
           for pr in PROVINCES}
    print()
    print(f"[harmonize] canonical -> {CANONICAL_PATH}")
    print(f"[harmonize] copy      -> {CANONICAL_COPY}")
    print(f"[harmonize] rows: {len(canon)} total")
    for pr in PROVINCES:
        grid = sum(1 for r in canon if r["PR"] == pr)
        print(f"[harmonize]   {pr}: grid {grid}/216, observed {cov[pr]}")
    print(f"[harmonize] AB splice applied: {decision['applied']} "
          f"({decision['reason']})")


if __name__ == "__main__":
    main()
