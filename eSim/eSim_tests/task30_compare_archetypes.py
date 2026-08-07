"""
Task 30 Steps 3–5 — EUI comparison table, trend-agreement verdict, and trend plot.

Reads the four batch directories (Worker reused from Task 26, plus the three new
archetype runs from task30_archetype_runs.py), extracts per-scenario EUI via
extract_option3_eui.py, builds the comparison table, computes trend agreement and
the 2022 magnitude envelope, and saves the trend plot.

Usage:
    py -3 eSim_tests/task30_compare_archetypes.py
"""
import os
import sys
import csv as csv_mod
import json

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))
from extract_option3_eui import extract_eui

TESTS_DIR       = os.path.dirname(__file__)
SIM_RESULTS_DIR = os.path.join(PROJECT_ROOT, "BEM_Setup", "SimResults")

WORKER_BATCH    = os.path.join(SIM_RESULTS_DIR, "Comparative_HH1p_1775675140")
MANIFEST_PATH   = os.path.join(TESTS_DIR, "task30_archetype_manifest.json")
OUT_CSV         = os.path.join(TESTS_DIR, "task30_archetype_eui_comparison.csv")
OUT_PNG         = os.path.join(TESTS_DIR, "task30_archetype_trend.png")

SCENARIOS    = ["2005", "2010", "2015", "2022", "2025"]   # exclude Default for trend
ALL_SCENARIOS = ["2005", "2010", "2015", "2022", "2025", "Default"]
END_USES     = ["Heating", "Cooling", "Interior Lighting", "Interior Equipment",
                "Fans", "Water Systems"]
YEAR_MAP     = {"2005": 2005, "2010": 2010, "2015": 2015, "2022": 2022, "2025": 2025}

# Envelope-check end-uses (the ones the paper's headline claims are about)
TREND_ENDUSES = ["Heating", "Cooling"]


def load_manifest():
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        return json.load(f)


def build_registry():
    """Return list of {archetype, batch_dir, hh_id} in canonical order."""
    manifest = load_manifest()
    archetype_to_batch = {r["archetype"]: r["batch_dir"] for r in manifest}
    archetype_to_hh    = {r["archetype"]: r["hh_id"]    for r in manifest}

    # Worker batch dir is fixed; hh_id was 5326 (2022 CSV) for Task 26
    registry = [
        {"archetype": "Worker",     "batch_dir": WORKER_BATCH, "hh_id": "5326"},
    ]
    for name in ["Student", "Retiree", "ShiftWorker"]:
        registry.append({
            "archetype": name,
            "batch_dir": archetype_to_batch[name],
            "hh_id":     archetype_to_hh[name],
        })
    return registry


def extract_all(registry):
    """Return {archetype: {scenario: {end_use: float, 'Total': float}}}."""
    data = {}
    for entry in registry:
        arch = entry["archetype"]
        bd   = entry["batch_dir"]
        print(f"  Extracting {arch}: {os.path.basename(bd)} ...")
        data[arch] = extract_eui(bd, compute_total=True)
    return data


def write_csv(data, registry):
    archetypes = [r["archetype"] for r in registry]
    # Wide format: scenario | arch-Heating | arch-Cooling | … | arch-Total
    fieldnames = ["Scenario"]
    for arch in archetypes:
        for eu in END_USES + ["Total"]:
            fieldnames.append(f"{arch}-{eu}")

    rows = []
    for sc in ALL_SCENARIOS:
        row = {"Scenario": sc}
        for arch in archetypes:
            sc_data = data[arch].get(sc)
            for eu in END_USES + ["Total"]:
                key = f"{arch}-{eu}"
                row[key] = f"{sc_data[eu]:.2f}" if sc_data else "MISSING"
        rows.append(row)

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv_mod.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"\nCSV saved: {os.path.basename(OUT_CSV)}")


def trend_verdict(data, registry):
    archetypes = [r["archetype"] for r in registry]
    print("\n" + "=" * 70)
    print("STEP 4 — TREND-AGREEMENT VERDICT")
    print("=" * 70)
    print(f"  Scenarios used for trend: 2005 -> 2025")
    print(f"  Endpoint end-uses checked: {TREND_ENDUSES}")
    print()

    sign_agreements = {}
    deltas = {}
    for eu in TREND_ENDUSES:
        signs = []
        arch_deltas = {}
        for arch in archetypes:
            v2005 = data[arch].get("2005", {}).get(eu, None)
            v2025 = data[arch].get("2025", {}).get(eu, None)
            if v2005 is None or v2025 is None:
                signs.append(None)
                arch_deltas[arch] = None
                continue
            d = v2025 - v2005
            signs.append(1 if d > 0 else (-1 if d < 0 else 0))
            arch_deltas[arch] = d
        deltas[eu] = arch_deltas
        # Count non-None signs
        valid = [s for s in signs if s is not None]
        majority = max(set(valid), key=valid.count) if valid else 0
        agree = sum(1 for s in valid if s == majority)
        sign_agreements[eu] = {"agree": agree, "total": len(valid),
                               "majority_sign": majority}
        sign_str = "+" if majority > 0 else ("-" if majority < 0 else "0")
        print(f"  {eu}: {agree}/{len(valid)} archetypes agree on sign={sign_str}")
        for arch in archetypes:
            d = arch_deltas.get(arch)
            if d is not None:
                sign = "+" if d >= 0 else ""
                print(f"      {arch:<14}: {sign}{d:.2f} kWh/m2/yr")

    # 2022 envelope
    print()
    print("  2022 magnitude envelope (max-min across archetypes):")
    envelope_results = {}
    for eu in TREND_ENDUSES + ["Total"]:
        vals = []
        for arch in archetypes:
            v = data[arch].get("2022", {}).get(eu, None)
            if v is not None:
                vals.append(v)
        if vals:
            rng = max(vals) - min(vals)
            mean_v = sum(vals) / len(vals)
            pct = rng / mean_v * 100 if mean_v else 0
            envelope_results[eu] = {"range": rng, "mean": mean_v, "pct": pct,
                                    "vals": {arch: data[arch].get("2022", {}).get(eu)
                                             for arch in archetypes}}
            print(f"      {eu:<22}: range={rng:.2f}, mean={mean_v:.2f}, "
                  f"envelope={pct:.1f}%  {[f'{v:.1f}' for v in vals]}")

    # Overall verdict
    print()
    heat_ok  = sign_agreements.get("Heating",  {}).get("agree", 0) >= 3
    cool_ok  = sign_agreements.get("Cooling",  {}).get("agree", 0) >= 3
    env_heat = envelope_results.get("Heating", {}).get("pct", 999)
    env_cool = envelope_results.get("Cooling", {}).get("pct", 999)
    env_tot  = envelope_results.get("Total",   {}).get("pct", 999)

    heat_env_ok = env_heat <= 15
    cool_env_ok = env_cool <= 15
    tot_env_ok  = env_tot  <= 15

    sign_pass    = heat_ok and cool_ok
    envelope_pass = heat_env_ok and cool_env_ok and tot_env_ok

    if sign_pass and envelope_pass:
        verdict = "PASS"
        reasoning = (
            f"Trend signs agree for Heating ({sign_agreements['Heating']['agree']}/4) "
            f"and Cooling ({sign_agreements['Cooling']['agree']}/4). "
            f"2022 envelope: Heating={env_heat:.1f}%, Cooling={env_cool:.1f}%, "
            f"Total={env_tot:.1f}% — all within ±15%."
        )
    else:
        verdict = "FAIL"
        reasons = []
        if not sign_pass:
            if not heat_ok:
                reasons.append(f"Heating sign agreement only "
                                f"{sign_agreements['Heating']['agree']}/4 (<3 required)")
            if not cool_ok:
                reasons.append(f"Cooling sign agreement only "
                                f"{sign_agreements['Cooling']['agree']}/4 (<3 required)")
        if not envelope_pass:
            for eu, ok, pct in [("Heating", heat_env_ok, env_heat),
                                 ("Cooling", cool_env_ok, env_cool),
                                 ("Total",   tot_env_ok,  env_tot)]:
                if not ok:
                    reasons.append(f"{eu} 2022 envelope={pct:.1f}% > 15%")
        reasoning = "; ".join(reasons)

    print(f"\n  VERDICT: {verdict}")
    print(f"  Reason:  {reasoning}")

    return {
        "verdict": verdict,
        "reasoning": reasoning,
        "sign_agreements": sign_agreements,
        "envelope": envelope_results,
        "deltas": deltas,
    }


def make_plot(data, registry):
    archetypes = [r["archetype"] for r in registry]
    years = [2005, 2010, 2015, 2022, 2025]
    sc_keys = ["2005", "2010", "2015", "2022", "2025"]

    plot_enduses = ["Heating", "Cooling", "Interior Equipment", "Water Systems"]
    titles       = ["Heating", "Cooling", "Equipment", "DHW"]
    colors       = {"Worker": "#1f77b4", "Student": "#ff7f0e",
                    "Retiree": "#2ca02c", "ShiftWorker": "#d62728"}

    fig, axes = plt.subplots(2, 2, figsize=(11, 7), sharex=True)
    axes = axes.flatten()

    for ax, eu, title in zip(axes, plot_enduses, titles):
        for arch in archetypes:
            vals = []
            for sc in sc_keys:
                sc_data = data[arch].get(sc)
                vals.append(sc_data[eu] if sc_data else None)
            valid = [(y, v) for y, v in zip(years, vals) if v is not None]
            if not valid:
                continue
            ys, vs = zip(*valid)
            ax.plot(ys, vs, marker="o", linewidth=1.5, markersize=4,
                    color=colors[arch], label=arch)
            # Annotate 2005->2025 delta
            if vals[0] is not None and vals[-1] is not None:
                d = vals[-1] - vals[0]
                sign = "+" if d >= 0 else ""
                ax.annotate(f"{sign}{d:.1f}", xy=(2025, vals[-1]),
                            xytext=(4, 0), textcoords="offset points",
                            fontsize=7, color=colors[arch])
        ax.set_title(title, fontsize=10)
        ax.set_ylabel("kWh/m\u00b2/yr", fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.set_xticks(years)
        ax.tick_params(axis="x", labelsize=8)

    axes[0].legend(fontsize=8, loc="upper right")
    fig.suptitle("Task 30 — Archetype Sensitivity: 2005-2025 EUI Trends\n"
                 "(Montreal 6A IDF, Montreal EPW; profile varies per archetype)",
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=130)
    print(f"Plot saved: {os.path.basename(OUT_PNG)}")


def print_full_table(data, registry):
    archetypes = [r["archetype"] for r in registry]
    print("\n" + "=" * 90)
    print("FULL EUI TABLE (kWh/m2/yr) — all scenarios, Total column")
    print("=" * 90)
    header = f"{'Scenario':<10}" + "".join(f"  {a+'-Total':>16}" for a in archetypes)
    print(header)
    print("-" * len(header))
    for sc in ALL_SCENARIOS:
        row = f"{sc:<10}"
        for arch in archetypes:
            sc_data = data[arch].get(sc)
            val = f"{sc_data['Total']:.2f}" if sc_data else "MISSING"
            row += f"  {val:>16}"
        print(row)
    print()
    # Also per-end-use for 2022 and trend scenarios
    for eu in ["Heating", "Cooling", "Interior Equipment", "Water Systems"]:
        print(f"  --- {eu} ---")
        header2 = f"  {'Scenario':<10}" + "".join(f"  {a:>14}" for a in archetypes)
        print(header2)
        for sc in ALL_SCENARIOS:
            row2 = f"  {sc:<10}"
            for arch in archetypes:
                sc_data = data[arch].get(sc)
                val = f"{sc_data[eu]:.2f}" if sc_data else "MISSING"
                row2 += f"  {val:>14}"
            print(row2)
        print()


if __name__ == "__main__":
    print("=" * 70)
    print("Task 30 Steps 3-5 — Archetype EUI comparison")
    print("=" * 70)

    registry = build_registry()
    print(f"\nBatches:")
    for r in registry:
        print(f"  {r['archetype']:<14}: HH {r['hh_id']:<8} "
              f"{os.path.basename(r['batch_dir'])}")

    print()
    data = extract_all(registry)
    write_csv(data, registry)
    print_full_table(data, registry)
    verd = trend_verdict(data, registry)
    make_plot(data, registry)

    # Save verdict JSON for the report script
    verd_out = os.path.join(TESTS_DIR, "task30_verdict.json")
    import json
    with open(verd_out, "w", encoding="utf-8") as f:
        # serialise only the scalar parts (vals dict has floats)
        out = {
            "verdict":   verd["verdict"],
            "reasoning": verd["reasoning"],
        }
        json.dump(out, f, indent=2)

    sys.exit(0 if verd["verdict"] == "PASS" else 2)
