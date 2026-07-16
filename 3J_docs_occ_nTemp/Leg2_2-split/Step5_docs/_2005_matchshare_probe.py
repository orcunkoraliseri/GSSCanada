"""
2005 region-linkage spot-check (audit Item 1 / Task 3, 2J_to_3J_improvement_implementation.md).
READ-ONLY. Confirms 2005 GSS-cycle donors are matched in proportion to their pool
share (i.e. NOT collapsed to a ~9%-style linkage failure the way 2J's pre-fix 2005
PR-coding disjointness was). "Matched share" = each CYCLE_YEAR's fraction of the
30,274 matched output rows; "pool share" = that cycle's fraction of the full
augmented-diaries donor pool. Ratio near 1.0 across cycles == healthy linkage.
"""
import pandas as pd

POOL = (
    r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp"
    r"\Leg2_2-split\Step4_docs\outputs_step4\sweep\R5_raked_mindwell\augmented_diaries.csv"
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
