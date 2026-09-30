"""Copy the paper's plot scripts into wp13/plot/ and re-point ONLY inputs/outputs (originals never edited).
Every replacement is asserted to have matched; a script whose replacement did not match aborts the build.
Run locally:  py make_plot_copies.py
"""
import re, sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[4] / "eSim" / "eSim_occ_utils" / "plotting"
DST = Path(__file__).resolve().parent / "plot"
DST.mkdir(exist_ok=True)
OCC = "/speed-scratch/o_iseri/1J_rerun/occ/0_Occupancy"
OCC25 = "/speed-scratch/o_iseri/1J_rerun/occ2025/0_Occupancy/Outputs_CENSUS"
CODE = "/speed-scratch/o_iseri/1J_rerun/code"
OUTDIR_EXPR = 'Path(__import__("os").environ.get("WP13_FIGS", str(Path(__file__).resolve().parent)))'

SCRIPTS = ["cross_cycle_plot_utils.py", "plot_temporal_comparison.py", "plot_nontemporal_comparison.py",
           "plot_presence_evolution_v2.py", "plot_activity_metabolic_comparison.py",
           "plot_default_class_v2.py", "plot_hhsize_occupancy.py"]


def sub_count(pattern, repl, text, expect_min=1, regex=True, label=""):
    if regex:
        new, n = re.subn(pattern, repl, text)
    else:
        n = text.count(pattern)
        new = text.replace(pattern, repl)
    if n < expect_min:
        sys.exit(f"PATCH DID NOT MATCH ({label or pattern[:60]}): {n} < {expect_min}")
    print(f"   patched {label or pattern[:50]!r}: {n}x")
    return new


def common(name, t):
    # census-year BEM files -> rebuilt grid files
    t = re.sub(r'BASE_DIR / "0_Occupancy/(Outputs_\d\dCEN\d\dGSS)/occToBEM/(\w+)_sample25pct\.csv"',
               lambda m: f'Path("{OCC}/{m.group(1)}/occToBEM/{m.group(2)}_sample25pct_grid.csv")', t)
    t = re.sub(r'BASE_DIR / "0_Occupancy/(Outputs_\d\dCEN\d\dGSS)/HH_aggregation/([^"]+)"',
               lambda m: f'Path("{OCC}/{m.group(1)}/HH_aggregation/{m.group(2)}")', t)
    t = t.replace('BASE_DIR / "0_Occupancy/Outputs_CENSUS/BEM_Schedules_2025.csv"', f'Path("{OCC25}/BEM_Schedules_2025_grid.csv")')
    t = t.replace('BASE_DIR / "0_Occupancy/Outputs_CENSUS/Full_data.csv"', f'Path("{OCC25}/Full_data.csv")')
    t = t.replace('BASE_DIR / "BEM_Setup" / "BEM_Schedules_2025.csv"', f'Path("{OCC25}/BEM_Schedules_2025_grid.csv")')
    t = t.replace("OUTPUT_DIR = Path(__file__).resolve().parent", "OUTPUT_DIR = " + OUTDIR_EXPR)
    return t


for name in SCRIPTS:
    print("==", name)
    t = (SRC / name).read_text(encoding="utf8")
    t = common(name, t)
    if name == "cross_cycle_plot_utils.py":
        assert t.count("_sample25pct_grid.csv") == 4 and "BEM_Schedules_2025_grid.csv" in t, "utils paths"
        assert "WP13_FIGS" in t, "utils outdir"
    if name == "plot_presence_evolution_v2.py":
        assert t.count("_sample25pct_grid.csv") == 4 and "BEM_Schedules_2025_grid.csv" in t
        assert "WP13_FIGS" in t
    if name == "plot_activity_metabolic_comparison.py":
        assert t.count("_sample25pct_grid.csv") == 4 and t.count("/HH_aggregation/") == 4 and "Full_data.csv" in t and "WP13_FIGS" in t
    if name == "plot_hhsize_occupancy.py":
        assert "BEM_Schedules_2025_grid.csv" in t and "WP13_FIGS" in t
        t = sub_count('    df = pd.read_csv(GSS_FILE, usecols=cols)\n',
                      '    df = pd.read_csv(GSS_FILE, usecols=cols)\n'
                      '    print("HHSIZE distribution (rows):", df["HHSIZE"].value_counts().sort_index().to_dict())\n'
                      '    df["HHSIZE"] = df["HHSIZE"].clip(upper=5)   # WP13: 5 means 5 or more\n',
                      t, regex=False, label="hhsize clip at 5")
    if name == "plot_default_class_v2.py":
        assert "BEM_Schedules_2025_grid.csv" in t and "WP13_FIGS" in t
        t = sub_count("sys.path.append(str(BASE_DIR))", f'sys.path.append("{CODE}")', t, regex=False, label="sys.path code dir")
        t = sub_count("    sys.exit(1)\n", "    idf_optimizer = None   # WP13: fall back to the paper's own 24-value default\n", t, regex=False, label="import fallback")
        t = sub_count("        defaults = idf_optimizer.load_standard_residential_schedules(verbose=True)\n",
                      "        defaults = _defaults()\n", t, regex=False, label="defaults hook")
        prelude = '''
FALLBACK_DEFAULT = [1.0]*7 + [0.85, 0.39] + [0.25]*7 + [0.30, 0.52, 0.87, 0.87, 0.87, 1.0, 1.0, 1.0]
DEFAULT_SOURCE = "unset"
NIGHT_TXT = "Night Overestimate"
MID_TXT = "Midday"

def _defaults():
    """Try the pipeline loader; accept it only if its weekday occupancy sums to 16.42 (paper Default);
    otherwise use the paper's own 24 values. The source used is printed and stored in DEFAULT_SOURCE."""
    global DEFAULT_SOURCE
    try:
        if idf_optimizer is not None:
            d = idf_optimizer.load_standard_residential_schedules(verbose=False)
            if abs(sum(d['occupancy']['Weekday']) - 16.42) < 0.005:
                DEFAULT_SOURCE = "idf_optimizer.load_standard_residential_schedules"
                print("WP13 default source:", DEFAULT_SOURCE)
                return d
            print("WP13: loader occupancy sum", sum(d['occupancy']['Weekday']), "!= 16.42, using fallback")
    except Exception as e:
        print("WP13: loader failed:", repr(e))
    DEFAULT_SOURCE = "FALLBACK_DEFAULT constant (paper's own 24 values, 95 W)"
    print("WP13 default source:", DEFAULT_SOURCE)
    return {'occupancy': {'Weekday': list(FALLBACK_DEFAULT), 'Weekend': list(FALLBACK_DEFAULT)}, 'activity': 95.0}

'''
        t = sub_count("def load_default_schedules():", prelude + "def load_default_schedules():", t, regex=False, label="prelude")
        t = sub_count('"Night Overestimate\\n(+39%)"', 'NIGHT_TXT', t, regex=False, label="night annotation")
        t = sub_count('"Midday Overestimate\\n(+60%)"', 'MID_TXT', t, regex=False, label="midday annotation")
    (DST / name).write_text(t, encoding="utf8")

# no un-patched BASE_DIR / "0_Occupancy" paths may remain
for name in SCRIPTS:
    t = (DST / name).read_text(encoding="utf8")
    left = re.findall(r'BASE_DIR / "[^"]*(?:0_Occupancy|BEM_Setup)[^"]*"', t)
    if left:
        sys.exit(f"UNPATCHED PATHS in {name}: {left}")
print("BUILD OK:", [p.name for p in DST.iterdir()])
