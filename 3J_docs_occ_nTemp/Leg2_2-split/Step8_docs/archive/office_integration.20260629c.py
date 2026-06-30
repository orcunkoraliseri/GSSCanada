"""office_integration.py — Step 8C: Office MODULATE schedule injection (3J Leg-2).

Injects occupancy-coupled People / Lights / ElectricEquipment Schedule:Compact
objects into a PNNL Tall or SuperTall office IDF (post-v24.2 transition), using
the AT_WORK_fraction from `office_presence_multiplier_{year}.csv`.

Design decisions (locked §4b / §5, 3rdJ_08_simulation_2split.md):
  People   :  schedule = AT_WORK_fraction(t); density (people/m²) UNCHANGED.
  Lights   :  L(t) = max(Lmin=0.15, η=1.0 × O(t) × D=1.0) — D=1.0 because
               Daylighting:Controls IS present in the IDFs (confirmed 8C.0 audit);
               E+ applies daylighting reduction on top of the injected schedule.
               LPD (W/m²) UNCHANGED.
  Equipment:  P(t) = Pbase + (1−Pbase)×O(t), Pbase=0.20. Plug density UNCHANGED.
  Interpolate to Timestep = No on all injected schedules (OD-8H).

Tag-2 zone routing (§4b §3):
  office-tagged zones      → inject multiplier (OpenOffice, ClosedOffice,
                             Conference, Dining, Classroom, Restroom, and
                             generic zones whose name contains "office" or "office ZN")
  "Resi_bot_Office ZN"    → BASELINE (building-management office on resi floor)
  apartment/MEP/retail    → untouched

Usage:
    from office_integration import inject_office_schedules
    inject_office_schedules(
        idf_path="..._v242.idf",
        output_path="out/Modified.idf",
        multiplier_csv="office_presence_multiplier_2022.csv",
        office_archetype="Office_Knowledge",
        band="observed",
    )

Standalone CLI (smoke test):
    py office_integration.py \\
        --idf BEM_Setup/Buildings/CAN_MTL/TallBuilding_..._v242.idf \\
        --out /tmp/modified.idf \\
        --csv outputs_step8/historical_schedules/office_presence_multiplier_2022.csv \\
        --archetype Office_Knowledge --band observed

2026-06-28 built.
"""
from __future__ import annotations
import os
import sys
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Constants (locked)
# ---------------------------------------------------------------------------
_LMIN  = 0.15   # minimum lights fraction (OD-8B)
_PBASE = 0.20   # equipment standby fraction (OD-8B)

# Zone-name keywords → office-tagged (case-insensitive)
_OFFICE_ZONE_KW = [
    "openoffice", "closedoffice", "conference", "dining",
    "classroom", "restroom", "officezone", "office zn",
]
# Zones that must NOT be injected (residential/MEP/ambiguous floor offices)
_BASELINE_ZONE_KW = [
    "resi_bot_office", "mechanical", "mep", "lobby", "stair",
    "elevator", "corridor", "retail", "hotel", "apartment",
]

OFFICE_ARCHETYPES = {"Office_Knowledge", "Office_Public", "Office_Sales"}
VALID_BANDS = {"observed", "conservative", "hybrid", "fullyhybrid"}


def _zone_tag(zone_name: str) -> str:
    """Return 'office', 'baseline', or 'skip' for a zone name."""
    n = zone_name.lower().strip()
    for kw in _BASELINE_ZONE_KW:
        if kw in n:
            return "baseline"
    for kw in _OFFICE_ZONE_KW:
        if kw in n:
            return "office"
    # Generic fallback — contain "office" but not in baseline list
    if "office" in n:
        return "office"
    return "skip"


def _build_compact_fields(name: str, wd_vals: list, we_vals: list) -> list:
    """Build the Schedule:Compact field list (Through 12/31, WD + WE 24-h)."""
    fields = [
        name, "Fraction",
        "Through: 12/31",
        "For: Weekdays SummerDesignDay WinterDesignDay",
    ]
    for h, v in enumerate(wd_vals):
        fields += [f"Until: {h+1:02d}:00", f"{v:.4f}"]
    fields += ["For: Weekends Holidays AllOtherDays"]
    for h, v in enumerate(we_vals):
        fields += [f"Until: {h+1:02d}:00", f"{v:.4f}"]
    return fields


def inject_office_schedules(
    idf_path: str,
    output_path: str,
    multiplier_csv: str,
    office_archetype: str,
    band: str = "observed",
    verbose: bool = True,
) -> dict:
    """Inject occupancy-coupled schedules into an office IDF.

    Parameters
    ----------
    idf_path        : v24.2 IDF (TallBuilding or SuperTallBuilding).
    output_path     : destination IDF path (parent dir created if needed).
    multiplier_csv  : path to `office_presence_multiplier_{year}.csv`.
    office_archetype: "Office_Knowledge" | "Office_Public" | "Office_Sales".
    band            : "observed" | "conservative" | "hybrid" | "fullyhybrid".

    Returns
    -------
    dict with keys: n_office_zones, n_baseline_zones, n_skip_zones,
                    wd_peak_people, wd_peak_lights, wd_peak_equip, archetype, band.
    """
    try:
        from eppy.modeleditor import IDF
    except ImportError:
        raise ImportError("eppy not installed: pip install eppy")

    if office_archetype not in OFFICE_ARCHETYPES:
        raise ValueError(f"office_archetype must be one of {OFFICE_ARCHETYPES}")
    if band not in VALID_BANDS:
        raise ValueError(f"band must be one of {VALID_BANDS}")

    # 1. Load multiplier CSV
    df = pd.read_csv(multiplier_csv)
    df.columns = df.columns.str.strip()
    sub = df[(df["office_archetype"] == office_archetype) & (df["BAND"] == band)]
    if sub.empty:
        raise ValueError(f"No rows for archetype={office_archetype}, band={band} "
                         f"in {os.path.basename(multiplier_csv)}")

    wd = sub[sub["Day_Type"] == "Weekday"].sort_values("Hour")["AT_WORK_fraction"].values
    we = sub[sub["Day_Type"] == "Weekend"].sort_values("Hour")["AT_WORK_fraction"].values
    assert len(wd) == 24 and len(we) == 24, \
        f"Multiplier CSV must have 24h WD + 24h WE; got {len(wd)},{len(we)}"

    wd_lgt = np.clip([max(_LMIN, v) for v in wd], 0, 1).tolist()
    we_lgt = np.clip([max(_LMIN, v) for v in we], 0, 1).tolist()
    wd_eq  = np.clip([_PBASE + (1 - _PBASE) * v for v in wd], 0, 1).tolist()
    we_eq  = np.clip([_PBASE + (1 - _PBASE) * v for v in we], 0, 1).tolist()

    # 2. Open IDF
    idd_path = _find_idd(idf_path)
    IDF.setiddname(idd_path)
    idf = IDF(idf_path)

    # 3. Create Schedule:Compact objects
    tag = f"{office_archetype}_{band}"
    ppl_name = f"OFC_People_{tag}"
    lgt_name = f"OFC_Lights_{tag}"
    eq_name  = f"OFC_Equip_{tag}"

    def _make_sch(name, wd_v, we_v):
        s = idf.newidfobject("Schedule:Compact")
        s.obj = ["Schedule:Compact"] + _build_compact_fields(name, wd_v, we_v)
        return s

    _make_sch(ppl_name, wd.tolist(), we.tolist())
    _make_sch(lgt_name, wd_lgt, we_lgt)
    _make_sch(eq_name,  wd_eq,  we_eq)

    if verbose:
        print(f"  Schedules created: {ppl_name}, {lgt_name}, {eq_name}")
        print(f"  WD peak: people={max(wd):.3f}  lights={max(wd_lgt):.3f}  equip={max(wd_eq):.3f}")

    # 4. Inject per zone
    n_office = n_baseline = n_skip = 0
    injected_zones = []
    ambiguous = []

    all_zone_names = {z.Name for z in idf.idfobjects.get("ZONE", [])}

    for obj_class, sch_field, sch_name, interp_field in [
        ("PEOPLE",           "Schedule_Name",           ppl_name, None),
        ("LIGHTS",           "Schedule_Name",           lgt_name, "Interpolate_to_Timestep"),
        ("ELECTRICEQUIPMENT","Schedule_Name",            eq_name,  "Interpolate_to_Timestep"),
    ]:
        objs = idf.idfobjects.get(obj_class, [])
        for obj in objs:
            zone = getattr(obj, "Zone_or_ZoneList_Name", "")
            tag_result = _zone_tag(zone)
            if tag_result == "office":
                try:
                    setattr(obj, sch_field, sch_name)
                    if interp_field:
                        try:
                            setattr(obj, interp_field, "No")
                        except Exception:
                            pass
                    if obj_class == "PEOPLE":
                        injected_zones.append(zone)
                        n_office += 1
                except Exception as e:
                    if verbose:
                        print(f"  WARN: could not set {obj_class}.{sch_field} for zone={zone}: {e}")
            elif tag_result == "baseline":
                if obj_class == "PEOPLE":
                    n_baseline += 1
            else:
                if obj_class == "PEOPLE":
                    # Log unrecognised zones for manager review
                    ambiguous.append(zone)
                    n_skip += 1

    # Set Interpolate=No on People schedule too (OD-8H)
    for obj in idf.idfobjects.get("PEOPLE", []):
        zone = getattr(obj, "Zone_or_ZoneList_Name", "")
        if _zone_tag(zone) == "office":
            try:
                setattr(obj, "Interpolate_to_Timestep", "No")
            except Exception:
                pass

    if verbose:
        print(f"  Zone routing: office={n_office} baseline={n_baseline} skip={n_skip}")
        if ambiguous:
            print(f"  Ambiguous zones (routed to skip): {list(set(ambiguous))}")
        if injected_zones:
            print(f"  Injected into: {list(set(injected_zones))}")

    # Provenance log
    log_path = output_path + ".provenance.txt"
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"archetype={office_archetype}\n")
        f.write(f"band={band}\n")
        f.write(f"multiplier_csv={multiplier_csv}\n")
        f.write(f"n_persons_rows_consumed={len(sub)}\n")
        f.write(f"density_basis=NECB 0.040 ppl/m2 (Number_of_People unchanged)\n")
        f.write(f"n_office_zones={n_office}\n")
        f.write(f"n_baseline_zones={n_baseline}\n")
        f.write(f"n_skip_zones={n_skip}\n")
        f.write(f"ambiguous_zones={list(set(ambiguous))}\n")
        f.write(f"Lmin={_LMIN}  eta=1.0  D=1.0  Pbase={_PBASE}\n")
        f.write("Note: Daylighting:Controls PRESENT in IDFs -- E+ applies "
                "daylighting reduction multiplicatively on top of injected schedule.\n")

    idf.saveas(output_path)
    if verbose:
        print(f"  Saved: {output_path}")

    return {
        "n_office_zones": n_office,
        "n_baseline_zones": n_baseline,
        "n_skip_zones": n_skip,
        "wd_peak_people": float(max(wd)),
        "wd_peak_lights": float(max(wd_lgt)),
        "wd_peak_equip": float(max(wd_eq)),
        "archetype": office_archetype,
        "band": band,
    }


def _find_idd(idf_path: str) -> str:
    """Locate Energy+.idd adjacent to or near the IDF; raise if not found."""
    candidates = [
        os.path.join(os.path.dirname(idf_path), "Energy+.idd"),
        os.path.join(os.path.dirname(idf_path), "..", "Energy+.idd"),
        "Energy+.idd",
    ]
    for c in candidates:
        if os.path.exists(c):
            return os.path.abspath(c)
    # Fall back to eppy's bundled IDD (may not match v24.2 — best effort)
    try:
        import eppy
        bundled = os.path.join(os.path.dirname(eppy.__file__), "resources", "iddfiles",
                               "Energy+9-0-0.idd")
        if os.path.exists(bundled):
            return bundled
    except Exception:
        pass
    raise FileNotFoundError(
        "Energy+.idd not found near the IDF. Place the v24.2 Energy+.idd "
        "in the same directory as the IDF or export EPLUS_IDD=/path/Energy+.idd."
    )


# ---------------------------------------------------------------------------
# CLI smoke test
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--idf",        required=True)
    ap.add_argument("--out",        required=True)
    ap.add_argument("--csv",        required=True)
    ap.add_argument("--archetype",  required=True)
    ap.add_argument("--band",       default="observed")
    args = ap.parse_args()

    result = inject_office_schedules(
        idf_path=args.idf,
        output_path=args.out,
        multiplier_csv=args.csv,
        office_archetype=args.archetype,
        band=args.band,
    )
    print(f"\nResult: {result}")


if __name__ == "__main__":
    main()
