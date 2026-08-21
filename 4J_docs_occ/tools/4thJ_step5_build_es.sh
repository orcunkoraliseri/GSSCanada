#!/bin/sh
# Step 5.1 - build outputs_step5/marginals_es.csv from the two INE Censo 2011
# PC-Axis files stored verbatim in outputs_step5/raw/.
#
# The Spanish census is SAMPLE-BASED and grossed up, so every published value is
# a FLOAT, not an integer. Counts are therefore written with 2 decimals and no
# exact-integer residual test is possible; the residual is reported instead.
#
# usage: sh 4thJ_step5_build_es.sh <raw_dir> > marginals_es.csv
set -e
RAW="$1"
AGE="$RAW/es_03001_age_single_year_by_sex.px"
HH="$RAW/es_01011_household_structure_by_size.px"
U_AGE='https://www.ine.es/jaxi/files/_px/es/px/t20/e244/avance/p01/l0/03001.px?nocab=1'
U_HH='https://www.ine.es/jaxi/files/_px/es/px/t20/e244/hogares/p01/l0/01011.px?nocab=1'
D=2026-08-20

px_data() { tr '\r\n' '  ' < "$1" | sed 's/.*DATA=//' | tr -s ' ' '\n' | sed 's/;$//' | grep -v '^$'; }

echo 'field,category,count,share,base_name,base_count,source_table,source_cell_code,source_url,download_date,status'

# --- age (107 stub rows: Total + ages 0..104 + "105 y mas"; 9 heading cols:
#     Sexo{Ambos,Hombres,Mujeres} x Nacionalidad{Total,Esp,Ext}) ---
px_data "$AGE" | awk -v url="$U_AGE" -v d="$D" '{v[NR]=$1+0} END{
  c=9
  for(i=1;i<=107;i++){ t[i]=v[(i-1)*c+1]; m[i]=v[(i-1)*c+4]; f[i]=v[(i-1)*c+7] }
  b=0; for(a=11;a<=105;a++){ i=a+2; b+=t[i] }
  split("11:14 15:24 25:34 35:44 45:54 55:64 65:74 75:105",B," ")
  split("11-14 15-24 25-34 35-44 45-54 55-64 65-74 75+",N," ")
  s=0
  for(k=1;k<=8;k++){ split(B[k],ab,":"); lo=ab[1]+0; hi=ab[2]+0; x=0
    for(a=lo;a<=hi;a++){ i=a+2; x+=t[i] }
    printf "strat_age_band,%s,%.2f,%.6f,persons_aged_11_and_over,%.2f,03001.px,edad %d..%d summed,%s,%s,EXACT_SAMPLE_BASED_FLOAT\n",N[k],x,x/b,b,lo,hi,url,d
    s+=x }
  printf "# age_partition_sum=%.2f base_11plus=%.2f residual=%.4f\n",s,b,b-s
  M=0;F=0; for(a=11;a<=105;a++){ i=a+2; M+=m[i]; F+=f[i] }
  printf "strat_sex,male,%.2f,%.6f,persons_aged_11_and_over,%.2f,03001.px,Hombres x edad 11..105,%s,%s,EXACT\n",M,M/b,b,url,d
  printf "strat_sex,female,%.2f,%.6f,persons_aged_11_and_over,%.2f,03001.px,Mujeres x edad 11..105,%s,%s,EXACT\n",F,F/b,b,url,d
  printf "# sex_partition_sum=%.2f base_11plus=%.2f residual=%.4f\n",M+F,b,b-M-F
}'

# --- economic status: NOT PUBLISHED as a static census table for Spain ---
printf 'strat_econ_status,NOT_AVAILABLE,,,persons,,NONE,NONE,%s,%s,NO_STATIC_CENSUS_TABLE_see_provenance\n' \
  'https://www.ine.es/censos2011_datos/cen11_datos_resultados.htm' "$D"

# --- household type (12 stub rows x 7 size cols; col 1 = Total tamano) ---
px_data "$HH" | awk -v url="$U_HH" -v d="$D" '{v[NR]=$1+0} END{
  c=7
  for(i=1;i<=12;i++) t[i]=v[(i-1)*c+1]
  b=t[1]
  one   = t[2]+t[3]+t[4]+t[5]
  cnk   = t[8]
  cwk   = t[9]+t[10]
  spk   = t[6]+t[7]
  oth   = t[11]+t[12]
  printf "strat_hh_type,one_person,%.2f,%.6f,households,%.2f,01011.px,estructura 2+3+4+5,%s,%s,EXACT_WITHIN_BASE\n",one,one/b,b,url,d
  printf "strat_hh_type,couple_no_children,%.2f,%.6f,households,%.2f,01011.px,estructura 8,%s,%s,EXACT_WITHIN_BASE\n",cnk,cnk/b,b,url,d
  printf "strat_hh_type,couple_with_children,%.2f,%.6f,households,%.2f,01011.px,estructura 9+10,%s,%s,EXACT_WITHIN_BASE\n",cwk,cwk/b,b,url,d
  printf "strat_hh_type,single_parent_with_children,%.2f,%.6f,households,%.2f,01011.px,estructura 6+7,%s,%s,EXACT_WITHIN_BASE\n",spk,spk/b,b,url,d
  printf "strat_hh_type,other_complex,%.2f,%.6f,households,%.2f,01011.px,estructura 11+12,%s,%s,MAPPING_DECISION_see_provenance\n",oth,oth/b,b,url,d
  printf "strat_hh_type,unknown,0,0.000000,households,%.2f,01011.px,NONE,%s,%s,NOT_PUBLISHED_census_has_no_nonresponse_band\n",b,url,d
  s=one+cnk+cwk+spk+oth
  printf "# hh_partition_sum=%.2f published_base=%.2f residual=%.4f\n",s,b,b-s
  # nesting check: the four one-person structure cells must equal the "1 persona" size column
  col1=0; for(i=2;i<=12;i++) col1+=v[(i-1)*c+2]
  printf "# nesting_check one_person_structure=%.2f size_1persona_column=%.2f residual=%.4f\n",one,col1,col1-one
}'
