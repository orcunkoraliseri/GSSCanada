#!/usr/bin/env bash
# hotel_obs 2026-09-25: downstream re-run after the 36 hotel cells finished and agg_P10R was re-aggregated.
# Same commands as the 2026-09-25 01:00-05:00 UTC P10R round (recipe: RESUME top box / progress log 15:10 UTC).
# Each step prints its own STEP line and exit code, so a skipped step is visible.
set -u
export PYTHONIOENCODING=utf-8
J3="C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp"
S8="$J3/Leg3_4-split/Step8_docs"; S9="$J3/Leg3_4-split/Step9_docs"; SC="$J3/writing/implementation/IMP/scripts"
D="$J3/writing/implementation/IMP/data/P10R"

n=$(ls "$S8/outputs_step8/agg_P10R" 2>/dev/null | wc -l)
echo "STEP 0 agg_P10R entries: $n"

echo "STEP 1 Step-9 scorer"
( cd "$S9" && py -3 3rdJ_09_activityDrivenLoads_4split.py --agg-dir ../Step8_docs/outputs_step8/agg_P10R \
    --outdir outputs_step9_P10R > outputs_step9_P10R/_stdout_score.txt 2>&1 ); echo "STEP 1 exit=$?"
tail -3 "$S9/outputs_step9_P10R/_stdout_score.txt"

echo "STEP 2 gates (d)+(e) on 56 cells"
cells=(); idfs=()
for c in "$S8"/campaign_local_P10R/*/; do
  t=$(basename "$c"); [ "$t" = "_logs" ] && continue
  cells+=("$c"); idfs+=("$c/injected_resized.idf")
done
echo "STEP 2 cells=${#cells[@]}"
( cd "$SC" && py -3 p10r_gates.py --cells "${cells[@]}" --idf "${idfs[@]}" \
    --registry "$J3/Leg3_4-split/Step7_docs/outputs_step7_P10R/P10R_products_registry.json" \
    --out p10r_gates_C_de_56_hotel_obs.json > p10r_gates_C_de_56_hotel_obs.out 2>&1 ); echo "STEP 2 exit=$? (1 expected: out-of-scope cells, as before)"
grep -c -- "-> ok" "$SC/p10r_gates_C_de_56_hotel_obs.out"; grep -- "-> " "$SC/p10r_gates_C_de_56_hotel_obs.out" | grep -vc -- "-> ok"

echo "STEP 3 P10 old-vs-new table"
( cd "$SC" && py -3 p10r_old_vs_new.py > "$D/P10R_old_vs_new.out" 2>&1 ); echo "STEP 3 exit=$?"

echo "STEP 4 P3 --arm P10R"
( cd "$SC" && py -3 p3_code_schedule_comparison.py --arm P10R > "$D/P3_P10R_run.out" 2>&1 ); echo "STEP 4 exit=$?"
tail -3 "$D/P3_P10R_run.out"
echo "POST DONE"
