"""
2005 region-linkage spot-check, actv2 re-run (Task 4 step 2, 2J_to_3J_improvement_implementation.md).
READ-ONLY. Same definition as _2005_matchshare_probe.py (Task 3), re-run against the
actv2 pool (R5_raked_mindwell_actv2) and the fresh outputs_step5/ produced by today's
Step-5 re-run, for an apples-to-apples comparison with the Task-3 reference table.
"matched share" = each CYCLE_YEAR's fraction of the 30,273 matched output rows;
"pool share" = that cycle's fraction of the full augmented-diaries donor pool actually
used for this run (R5_raked_mindwell_actv2). Ratio near 1.0 across cycles == healthy linkage.
"""
import pandas as pd

POOL = (
    r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp"
    r"\Leg2_2-split\Step4_docs\outputs_step4\sweep\R5_raked_mindwell_actv2\augmented_diaries.csv"
)
FULL_SCHED = (
    r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp"
    r"\Leg2_2-split\Step5_docs\outputs_step5\3rdJ_25CEN_aug_Full_Schedules.csv"
)

print("Loading pool CYCLE_YEAR column ...")
pool = pd.read_csv(POOL, usecols=["CYCLE_YEAR"], low_memory=False)
pool_share = pool["CYCLE_YEAR"].value_counts(normalize=True).sort_index() * 100

print("Loading matched (Full_Schedules) CYCLE_YEAR column ...")
matched = pd.read_csv(FULL_SCHED, usecols=["CYCLE_YEAR"], low_memory=False)
matched_share = matched["CYCLE_YEAR"].value_counts(normalize=True).sort_index() * 100

print(f"\nPool rows: {len(pool):,}   Matched rows: {len(matched):,}")
print(f"\n{'CYCLE_YEAR':>10}  {'pool_share_%':>12}  {'matched_share_%':>16}  {'ratio':>6}")
for cyc in sorted(set(pool_share.index) | set(matched_share.index)):
    p = pool_share.get(cyc, 0.0)
    m = matched_share.get(cyc, 0.0)
    ratio = (m / p) if p > 0 else float("nan")
    print(f"{cyc:>10}  {p:>12.2f}  {m:>16.2f}  {ratio:>6.2f}")

print("\nDONE")
