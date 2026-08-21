#!/bin/sh
# D-S5-3 (ruled 2026-08-20): build the economic-status marginal over the WHOLE
# synthetic population (age 11+), not just the 16-74 base the censuses publish.
#   usage: sh 4thJ_step5_econ11plus.sh <outputs_step5_dir>
#
# The censuses publish economic activity for 16-74 only (KS601UK; the Spanish
# microdata was cut to the same base deliberately). The synthetic population
# starts at 11, so three age slices have NO published economic status:
#
#   11-14   -> `unknown`   D-S5-3 as ruled. It is a declared value of the field
#                          for all three countries, it is what Italy's own data
#                          uses, and it asserts nothing the source does not say.
#   age 15  -> `unknown`   NOT covered by D-S5-3 as put. Assigned by the SAME
#                          argument: KS601UK starts at 16, so the census is
#                          equally silent here. 🔴 ONE-LINE CONFIRMATION OWED.
#   75+     -> `retired`   D-S5-3 as ruled. Corpus-modal in all three countries
#                          but NOT clean in Spain: uk 95.4 %, it 71.9 %,
#                          es only 58.9 % (251 homemaker + 539 other_inactive
#                          at 75+). Quote the Spanish figure wherever this
#                          marginal is used.
#
# The age-15 slice is never counted directly: it is the residual of the four
# bases already in marginals_<c>.csv, so it cannot drift away from them.
#   age15 = base(11+) - band(11-14) - base(16-74) - band(75+)
# For the UK it is independently checkable against QS103UK C_AGE_015 minus the
# scaled DC1104EW communal count; the two agree to 0.19 persons.
set -e
D="$1"

for C in uk es; do
  M="$D/marginals_$C.csv"
  [ -s "$M" ] || { echo "SKIP $C: $M missing or empty"; continue; }
  awk -F',' -v C="$C" -v OUT="$D/econ_11plus_$C.csv" '
    $1=="strat_age_band"      { if($2=="11-14") a1114=$3; if($2=="75+") a75=$3; b11=$6 }
    $1=="strat_econ_status"   { e[$2]=$3; b1674=$6; src=$7; url=$9; dl=$10 }
    END{
      age15 = b11 - a1114 - b1674 - a75
      unk   = a1114 + age15
      e["retired"]  = e["retired"] + a75
      e["unknown"]  = unk
      n = split("employed unemployed student retired homemaker other_inactive unknown", K, " ")
      tot = 0
      for(i=1;i<=n;i++) if(e[K[i]] != "") tot += e[K[i]]
      printf "" > OUT
      printf "field,category,count,share,base_name,base_count,source_table,derivation,source_url,download_date,status\n" > OUT
      for(i=1;i<=n;i++){
        k = K[i]
        if(e[k] == ""){
          printf "strat_econ_status,%s,,,persons_aged_11_and_over_in_private_households,%.2f,%s,NOT_SEPARABLE,%s,%s,NOT_SEPARABLE_RELA_has_no_homemaker_category_FINDING_51\n", k, tot, src, url, dl >> OUT
          continue
        }
        d = "published_16_74"
        if(k=="unknown")  d = "D-S5-3_band_11-14_plus_age_15_residual"
        if(k=="retired")  d = "published_16_74_plus_D-S5-3_band_75plus"
        printf "strat_econ_status,%s,%.2f,%.6f,persons_aged_11_and_over_in_private_households,%.2f,%s,%s,%s,%s,D-S5-3_APPLIED\n", k, e[k], e[k]/tot, tot, src, d, url, dl >> OUT
      }
      printf "# D-S5-3 applied %s: 11-14 -> unknown, 75+ -> retired, age 15 -> unknown (extension, confirmation owed)\n", C >> OUT
      printf "# base_11plus %.2f  band_11-14 %.2f  base_16_74 %.2f  band_75+ %.2f  age_15_residual %.2f\n", b11, a1114, b1674, a75, age15 >> OUT
      printf "# partition_sum %.2f  residual_vs_base_11plus %.2f\n", tot, tot - b11 >> OUT
      printf "%s  age15=%.2f (%.3f%% of 11+)  unknown=%.2f (%.3f%%)  retired=%.2f (%.3f%%)  partition %.2f vs base %.2f  residual %.2f\n",
             C, age15, 100*age15/b11, unk, 100*unk/tot, e["retired"], 100*e["retired"]/tot, tot, b11, tot-b11
    }' "$M"
done
