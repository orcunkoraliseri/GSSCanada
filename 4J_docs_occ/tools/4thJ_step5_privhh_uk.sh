#!/bin/sh
# D-S5-5: restrict the UK age and sex marginals to residents of PRIVATE HOUSEHOLDS.
#   usage: sh 4thJ_step5_privhh_uk.sh <outputs_step5_dir>
# Communal population by age/sex is published only for England and Wales (DC1104EW).
# Its band profile is scaled so the total equals the published UK communal count
# (QS419UK / KS101UK = 1,126,340), then subtracted from QS103UK / KS101UK.
set -e
D="$1"
R="$D/raw"

sed 's/^"//; s/","/\t/g; s/",/\t/' "$R/uk_DC1104EW_residence_type_by_sex_by_age.csv" \
| awk -F'\t' -v OFS='\t' '
  $2=="Lives in a communal establishment" && $3=="All persons"{a[$1]=$4}
  $2=="Lives in a communal establishment" && $3=="Males"{m=($1=="All categories: Age")?$4:m}
  $2=="Lives in a communal establishment" && $3=="Females"{f=($1=="All categories: Age")?$4:f}
  END{
    ew_tot = a["All categories: Age"]
    uk_tot = 1126340                       # QS419UK total = KS101UK communal, exact
    k      = uk_tot / ew_tot
    # 11-14 is the only band that needs a within-band split: DC1104EW publishes 10-14.
    # Assume the communal count is uniform across the five single years -> 4/5.
    b["11-14"] = 0.8 * a["Age 10 to 14"]
    b["15-24"] = a["Age 15"] + a["Age 16 to 17"] + a["Age 18 to 19"] + a["Age 20 to 24"]
    b["25-34"] = a["Age 25 to 29"] + a["Age 30 to 34"]
    b["35-44"] = a["Age 35 to 39"] + a["Age 40 to 44"]
    b["45-54"] = a["Age 45 to 49"] + a["Age 50 to 54"]
    b["55-64"] = a["Age 55 to 59"] + a["Age 60 to 64"]
    b["65-74"] = a["Age 65 to 69"] + a["Age 70 to 74"]
    b["75+"]   = a["Age 75 to 79"] + a["Age 80 to 84"] + a["Age 85 and over"]
    n = split("11-14 15-24 25-34 35-44 45-54 55-64 65-74 75+", B, " ")
    for(i=1;i<=n;i++) printf "COMM_AGE\t%s\t%.2f\n", B[i], k*b[B[i]]
    printf "COMM_SEX\tmale\t%.2f\n",   k*m
    printf "COMM_SEX\tfemale\t%.2f\n", k*f
    printf "SCALE\tew_communal\t%d\n", ew_tot
    printf "SCALE\tuk_communal\t%d\n", uk_tot
    printf "SCALE\tk\t%.8f\n", k
  }' > "$D/.comm_uk.tsv"
cat "$D/.comm_uk.tsv"

# --- economic activity: the same treatment, from DC1602EWla -------------------
# KS601UK mapping is reproduced exactly: economically-active full-time students are a
# DISJOINT category, not a subset of 'In employment' / 'Unemployed'.
# DC1602EWla's top age band is '65 and over'; the 65-74 slice is 40838/337435 = 0.121025,
# MEASURED against DC1104EW (the two tables agree on the 65+ communal total to the person).
# The economic composition within 65+ is assumed uniform -- the only assumption here.
sed 's/^"//; s/","/\t/g; s/",/\t/' "$R/uk_DC1602EW_residence_type_by_economic_activity_by_age.csv" \
| awk -F'\t' '
  $2=="Lives in a communal establishment"{ v[$1 SUBSEP $3]=$4+0 }
  END{
    k = 1126340/1004799
    s6574 = 40838/337435
    n=split("Age 16 to 24|Age 25 to 34|Age 35 to 49|Age 50 to 64|Age 65 and over",AB,"|")
    for(i=1;i<=n;i++){
      a=AB[i]; f=(a=="Age 65 and over")? s6574 : 1
      emp += f*(v[a,"Economically active: In employment: Total"] - v[a,"Economically active: In employment: Full-time students"])
      une += f*(v[a,"Economically active: Unemployed: Total"]    - v[a,"Economically active: Unemployed: Full-time students"])
      stu += f*(v[a,"Economically active: In employment: Full-time students"] + v[a,"Economically active: Unemployed: Full-time students"] + v[a,"Economically inactive: Student (including full-time students)"])
      ret += f*v[a,"Economically inactive: Retired"]
      hom += f*v[a,"Economically inactive: Looking after home or family"]
      oth += f*(v[a,"Economically inactive: Long-term sick or disabled"] + v[a,"Economically inactive: Other"])
      tot += f*v[a,"All categories: Economic activity"]
    }
    printf "ECON_COMM\temployed\t%.2f\nECON_COMM\tunemployed\t%.2f\nECON_COMM\tstudent\t%.2f\n", k*emp, k*une, k*stu
    printf "ECON_COMM\tretired\t%.2f\nECON_COMM\thomemaker\t%.2f\nECON_COMM\tother_inactive\t%.2f\n", k*ret, k*hom, k*oth
    printf "ECON_COMM\tTOTAL_16_74\t%.2f\nCHECK\tsum_parts\t%.2f\nCHECK\ts6574\t%.6f\n", k*tot, k*(emp+une+stu+ret+hom+oth), s6574
  }' > "$D/.comm_econ_uk.tsv"
cat "$D/.comm_econ_uk.tsv"
