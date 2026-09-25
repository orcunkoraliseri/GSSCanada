"""hotel_obs 2026-09-25: which printed numbers move when the 2030 hotel level changes.

Compares the marker table written before the hotel switch (archived) with the one written after
(p10r_marker_values.py re-run on the new agg_P10R / outputs_step9_P10R). Prints every marker whose
new value changed, with the text it had, so the chapter edit can be made by hand (the --apply path
refuses because the chapters were edited after the stage-2b backup).

CONTROL: the 20 cells that do not read the hotel 2030 CSVs (past years and the code building) must give
markers that do NOT move; any marker whose definition uses only those scenarios and moves is printed as
UNEXPECTED. Also prints the count of unchanged rows, so an empty diff is not mistaken for a skipped run.
"""
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
J3 = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
OLD = os.path.join(J3, "Leg3_4-split", "_archive_pre_hotel_obs_2026-09-25", "IMP_data_P10R", "P10R_marker_table.csv")
NEW = os.path.join(J3, "writing", "implementation", "IMP", "data", "P10R", "P10R_marker_table.csv")

o = pd.read_csv(OLD, dtype=str, keep_default_na=False)
n = pd.read_csv(NEW, dtype=str, keep_default_na=False)
if os.path.getmtime(NEW) <= os.path.getmtime(OLD):
    sys.exit("NEW marker table is not newer than the archived one: re-run p10r_marker_values.py first")
o = o[o.row_type == "marker"].set_index(["file", "line", "idx"])
n = n[n.row_type == "marker"].set_index(["file", "line", "idx"])
assert o.index.equals(n.index), "marker rows differ between the two tables"
j = o[["marker_text", "metric_definition", "new_value", "new_computed"]].join(
    n[["new_value", "new_computed", "status"]], rsuffix="_hot")
moved = j[j.new_value != j.new_value_hot]
same = j[j.new_value == j.new_value_hot]
past_only = ("Y2022", "Y2005", "Y2010", "Y2015", "Default_NECB")
print(f"markers: {len(j)}  moved: {len(moved)}  unchanged: {len(same)}")
for (f, ln, i), r in moved.iterrows():
    uses_2030 = any(k in r.metric_definition for k in ("B_", "2030", "sens_", "scenario", "bundle"))
    flag = "" if uses_2030 else "  UNEXPECTED (definition names no 2030 scenario)"
    print(f"{f}:{ln}#{i}  printed-before '{r.new_value}' -> now '{r.new_value_hot}'   [{r.metric_definition[:90]}]{flag}")
raw_moved = j[(j.new_value == j.new_value_hot) & (j.new_computed != j.new_computed_hot)]
print(f"\nrows whose raw value moved but the printed value did not: {len(raw_moved)}")
