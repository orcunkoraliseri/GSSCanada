# -*- coding: utf-8 -*-
"""Assemble the blinded Supplementary Material package for Building Simulation.

Document = the four already-written SI table sets, with internal working-file
           provenance and report-style "> Note:" blockquotes removed.
Data     = derived / aggregate outputs only. NO Statistics Canada microdata and
           no row-level derivative of it.

HELD BACK (see README): the activity harmonization crosswalk. Its leaf-code counts
are 182 / 265 / 64 / 123, where section 3.1 and Table B2 both state 182 / 264 / 64 / 121.
Shipping it would put a countable contradiction in front of a reviewer.
"""
import os, re, io, sys, shutil, csv
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = "C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/2J_docs_occ_nTemp"
OUT = ROOT + "/writing/submission/submissionDocs/Supplementary_Material"
DATA = OUT + "/data"
os.makedirs(DATA, exist_ok=True)

SPECS = [
    ("S1_sheu_calibration_48_cells.csv", "Step9_docs/cluster_run_results.csv",
     "The binding calibration gate. Per dwelling-by-year cell: simulated equipment and lighting "
     "energy, the SHEU target, the percent deviation, and the PASS/FAIL verdict."),
    ("S2_campaign_annual_by_household.csv", "outputs_step8/agg/agg_annual.csv",
     "One row per simulated household-year across the 6,000-run campaign: end-use energy, "
     "conditioned floor area, EUI, load factor, peak-to-average ratio, midday share, mean peak hour."),
    ("S3_campaign_peak_by_household.csv", "outputs_step8/agg/agg_peak.csv",
     "Annual and mean daily peak demand, peak hour and peak day of year, per simulated household-year."),
    ("S4_stock_peak_by_cell.csv", "outputs_step8/agg/agg_stock_peak.csv",
     "Stock-aggregated peak statistics per archetype-city-year cell: circular mean peak hour, its "
     "circular standard deviation, and the evening-peaking fraction."),
    ("S5_enduse_annual_heating_cooling.csv", "outputs_step8/agg/agg_enduse_annual.csv",
     "Heating and cooling energy by fuel, per cell and sampled household."),
    ("S6_loadshape_profiles_hourly.csv", "Step9_docs/loadshape_profiles.csv",
     "Mean hourly building-level and zone-level equipment, lighting and facility demand, baseline "
     "arm against activity arm, for every cell and year."),
    ("S7_peak_hours_by_arm.csv", "Step9_docs/peak_hours.csv",
     "Peak hour of the equipment and lighting channels, baseline arm against activity arm."),
    ("S8_peak_shift_summary.csv", "Step9_docs/peak_shift_summary.csv",
     "Peak-hour displacement between the two arms: the null result reported in section 5.4."),
]

def head_cols(p):
    with open(p, encoding="utf-8-sig", newline="") as fh:
        return next(csv.reader(fh))

manifest = []
for name, src, desc in SPECS:
    dst = DATA + "/" + name
    shutil.copyfile(ROOT + "/" + src, dst)
    n = sum(1 for _ in open(dst, encoding="utf-8-sig")) - 1
    cols = head_cols(dst)
    manifest.append((name, n, len(cols), desc, cols))
    print("  %-40s %7s rows %3d cols" % (name, format(n, ","), len(cols)))

# ------------------------------------------------------------------ document
def clean(text):
    text = re.sub(r"^# .*?\n", "", text, count=1)              # drop the file's own H1
    text = re.sub(r"^\*Source:\*[^\n]*\n", "", text, flags=re.M)  # drop working-doc provenance
    # report-style blockquotes -> ordinary paragraphs
    text = re.sub(r"^> (?:\*\*)?Note:?(?:\*\*)?\s*", "", text, flags=re.M)
    text = re.sub(r"^> ", "", text, flags=re.M)
    # internal file names -> prose
    for pat, rep in [
        (r"`Step9_docs/prototype/activity_loads\.py`", "an early prototype of the end-use module"),
        (r"`09_activityDrivenLoads\.py`", "the end-use load module"),
        (r"`augmented_diaries\.csv`", "the augmented diary pool"),
    ]:
        text = re.sub(pat, rep, text)
    text = re.sub(r"^\s*---\s*\n", "", text, count=1)
    return re.sub(r"\n{3,}", "\n\n", text).strip()

b2 = open(ROOT + "/writing/tables/SI/Table_B1_B2.md", encoding="utf-8").read()
# the "Raw-code magnitudes" column is 14 unresolved '⚠ check source' cells -> drop the column
b2 = re.sub(r"^\| Code \| Category \| Raw-code magnitudes[^|]*\| Notes \|$",
            "| Code | Category | Notes |", b2, flags=re.M)
b2 = re.sub(r"^\|---\|---\|---\|---\|$", "|---|---|---|", b2, flags=re.M)
b2 = re.sub(r"^(\| \d+ \| [^|]*)\| ⚠ check source \|", r"\1|", b2, flags=re.M)
# the note pointing at an unshipped working file
b2 = re.sub(r"^> Note: Per-code breakdown.*?\n", "", b2, flags=re.M | re.S)
b2 = re.sub(r"^Note: Per-code breakdown[^\n]*\n", "", b2, flags=re.M)
assert "check source" not in b2, "placeholder survived"

parts = [clean(open(ROOT + "/writing/tables/SI/Table_A1_A2_A3.md", encoding="utf-8").read()),
         clean(b2),
         clean(open(ROOT + "/writing/tables/SI/Table_C1_C2.md", encoding="utf-8").read()),
         clean(open(ROOT + "/writing/tables/SI/Appendix_D_deviations.md", encoding="utf-8").read())]

idx = ["| File | Rows | Columns | Contents |", "|---|---:|---:|---|"]
dic = []
for name, n, c, desc, cols in manifest:
    idx.append("| `%s` | %s | %d | %s |" % (name, format(n, ","), c, desc))
    dic.append("**`%s`** — %s\n\n%s\n" % (name, desc, ", ".join("`%s`" % x for x in cols)))

doc = """# Supplementary Material

*From "How Much" to "When": Forecasting the Residential Energy Load Shape from a Calibrated
Behavioural Occupancy Time-Series (Canada, 2005 to 2030)*

This file accompanies the manuscript. It contains the reference tables cited in the text
(Tables A1 to A3, B1 and B2), two further validation tables (C1 and C2), a register of documented
deviations and corrections (Appendix D), and an index of the derived data files distributed
alongside it.

## Data availability and licensing

The source microdata are not redistributed here. The analysis draws on two Statistics Canada
public-use microdata products, the General Social Survey Time Use files (Cat. 45-25-0001, and the
individual cycles 12M0019X, 12M0024X and 89M0034X) and the Census Public Use Microdata File
(Cat. 98M0001X). Both are obtained directly from Statistics Canada under its own terms of use, and
no record-level file derived from them is included in this package.

What is included is the derived layer: the calibration evidence and the aggregate outputs of the
simulation campaign. Every file listed below is an output of the pipeline described in the
manuscript rather than a redistribution of survey records, and together they are sufficient to
reproduce every calibration gate and every load-shape statistic the paper reports. The larger
derived products, namely the augmented diary set, the per-household hourly load traces and the
analysis code, remain available from the corresponding author.

### Data files

%s

### Column dictionary

%s

---

%s
""" % ("\n".join(idx), "\n".join(dic), "\n\n---\n\n".join(parts))

open(OUT + "/Supplementary_Material.md", "w", encoding="utf-8", newline="").write(doc)

# ------------------------------------------------------------------ gates
probes = ["Orcun", "Iseri", "Caroline", "Hachem", "Concordia", "NSERC", "Voltage",
          "orcunkoral", "o_iseri", "@concordia", "C:\\Users", "C:/Users"]
print("\nSupplementary_Material.md  %d chars" % len(doc))
print("blinding (document) :", {p: doc.count(p) for p in probes if doc.count(p)} or "clean")
print("placeholders        :", {m: doc.count(m) for m in ["check source", "[confirm]", "TODO", "TBD"] if doc.count(m)} or "none")
print("working-doc refs    :", re.findall(r"`[\w/]+\.(?:md|py|xlsx|sh)`", doc) or "none")
print("blockquotes         :", len(re.findall(r"^> ", doc, re.M)))
leaks = 0
for name, *_ in manifest:
    t = open(DATA + "/" + name, encoding="utf-8-sig", errors="replace").read()
    b = {p: t.count(p) for p in probes if t.count(p)}
    if b:
        leaks += 1; print("  !! LEAK in", name, b)
print("blinding (data)     :", "clean across %d files" % len(manifest) if not leaks else "%d LEAKS" % leaks)
print("total data size     : %.1f MB" % (sum(os.path.getsize(DATA + "/" + n) for n, *_ in manifest) / 1e6))
