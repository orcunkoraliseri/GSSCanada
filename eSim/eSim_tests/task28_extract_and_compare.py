"""
Task 28 — External EUI validation against IECC 2021 reference.

Extracts the 2022-scenario total EUI from the four Task 26/27 batch directories,
joins against the IECC 2021 reference, computes deltas, and prints the
comparison table.  Results are cached to task28_extracted_eui.csv.

Usage:
    py -3 eSim_tests/task28_extract_and_compare.py
"""
import os
import sys
import csv

# Make eSim_tests importable from the project root
sys.path.insert(0, os.path.dirname(__file__))
from extract_option3_eui import extract_eui

BASE = os.path.join(os.path.dirname(__file__), "..", "BEM_Setup", "SimResults")

# ── batch registry ───────────────────────────────────────────────────────────
BATCHES = [
    {
        "label":    "Run A — Quebec (Task 27)",
        "zone":     "6A",
        "city":     "Montreal",
        "pr":       "Quebec",
        "hh":       "4893 (2005 CSV)",
        "batch_dir": os.path.join(BASE, "Comparative_HH1p_1775696179"),
    },
    {
        "label":    "Run B — Ontario (Task 27)",
        "zone":     "5A",
        "city":     "Toronto",
        "pr":       "Ontario",
        "hh":       "5203 (2005 CSV)",
        "batch_dir": os.path.join(BASE, "Comparative_HH1p_1775696280"),
    },
    {
        "label":    "Run C — Alberta (Task 27)",
        "zone":     "7",
        "city":     "Calgary",
        "pr":       "Alberta",
        "hh":       "11851 (2005 CSV)",
        "batch_dir": os.path.join(BASE, "Comparative_HH1p_1775696365"),
    },
    {
        "label":    "Task 26 anchor — Quebec",
        "zone":     "6A",
        "city":     "Montreal",
        "pr":       "Quebec",
        "hh":       "5326 (2022 CSV)",
        "batch_dir": os.path.join(BASE, "Comparative_HH1p_1775675140"),
    },
]

# ── IECC 2021 reference (kWh/m²) ─────────────────────────────────────────────
IECC_2021 = {
    "5A": 122.1,
    "5C": 122.1,
    "6A": 148.3,
    "7":  164.0,
    "8":  207.6,
}

SCENARIO = "2022"   # Task 28 uses the 2022 scenario for "current practice"
END_USES  = ["Heating", "Cooling", "Interior Lighting",
             "Interior Equipment", "Fans", "Water Systems"]


def verdict(delta_pct):
    abs_d = abs(delta_pct)
    if abs_d <= 20:
        return "PASS"
    if abs_d <= 35:
        return "WARN"
    return "FAIL"


def main():
    rows = []
    for b in BATCHES:
        bd = b["batch_dir"]
        if not os.path.isdir(bd):
            print(f"ERROR: batch dir not found: {bd}")
            sys.exit(1)
        print(f"Extracting: {os.path.basename(bd)} …")
        eui_map = extract_eui(bd, compute_total=True)
        sc = eui_map.get(SCENARIO)
        if sc is None:
            print(f"  ERROR: {SCENARIO} scenario not found in {bd}")
            sys.exit(1)
        sim_total = sc["Total"]
        ref       = IECC_2021[b["zone"]]
        delta_pct = (sim_total - ref) / ref * 100
        rows.append({
            "label":         b["label"],
            "zone":          b["zone"],
            "city":          b["city"],
            "pr":            b["pr"],
            "hh":            b["hh"],
            "area_m2":       sc["area_m2"],
            "Heating":       sc["Heating"],
            "Cooling":       sc["Cooling"],
            "Interior Lighting":  sc["Interior Lighting"],
            "Interior Equipment": sc["Interior Equipment"],
            "Fans":          sc["Fans"],
            "Water Systems": sc["Water Systems"],
            "sim_total":     sim_total,
            "iecc_2021":     ref,
            "delta_pct":     round(delta_pct, 1),
            "verdict":       verdict(delta_pct),
        })

    # ── write CSV cache ───────────────────────────────────────────────────────
    cache_path = os.path.join(os.path.dirname(__file__), "task28_extracted_eui.csv")
    fieldnames = ["label", "zone", "city", "pr", "hh", "area_m2",
                  "Heating", "Cooling", "Interior Lighting",
                  "Interior Equipment", "Fans", "Water Systems",
                  "sim_total", "iecc_2021", "delta_pct", "verdict"]
    with open(cache_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"\nCached to {cache_path}\n")

    # ── print comparison table ────────────────────────────────────────────────
    print("=" * 90)
    print("TASK 28 — STEP 3 COMPARISON TABLE  (Scenario: 2022 — current practice)")
    print("=" * 90)
    print(f"{'Zone':<5} {'City':<12} {'Simulated':>14} {'IECC 2021':>12} {'Delta (%)':>11} {'Verdict':<8}")
    print("-" * 65)
    for r in rows:
        sign = "+" if r["delta_pct"] >= 0 else ""
        print(f"{r['zone']:<5} {r['city']:<12} {r['sim_total']:>14.2f} {r['iecc_2021']:>12.1f} "
              f"{sign}{r['delta_pct']:>10.1f}% {r['verdict']:<8}  ({r['label']})")

    print()
    counts = {"PASS": 0, "WARN": 0, "FAIL": 0}
    for r in rows:
        counts[r["verdict"]] += 1
    print(f"Verdict counts — PASS: {counts['PASS']}, WARN: {counts['WARN']}, FAIL: {counts['FAIL']}")

    # ── check for escalation ─────────────────────────────────────────────────
    if counts["FAIL"] > 0:
        print("\n*** ESCALATION REQUIRED: one or more rows exceed ±35 % ***")
        sys.exit(2)
    else:
        print("\nAll rows within ±35 % — no escalation required.")

    return rows


if __name__ == "__main__":
    main()
