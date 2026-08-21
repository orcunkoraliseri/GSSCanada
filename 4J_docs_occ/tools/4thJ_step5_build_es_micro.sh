#!/bin/sh
# D-S5-4 (ruled b) + D-S5-5: tabulate the Spanish PRIVATE-HOUSEHOLD marginals from the
# Censo 2011 anonymised person microdata.
#   usage: sh 4thJ_step5_build_es_micro.sh <path to Microdatos_personas_nacional.zip>
# Universe (stated on line 2 of the INE record layout): "Un registro para cada persona
# residente en viviendas principales" -- i.e. private households only, which is exactly the
# HETUS frame. Verified: weighted total 46,574,725.58 = published 46,815,916.44 minus the
# 241,186.87 people usually resident in collective establishments (colectivos 01002.px),
# to within 4 persons.
# Fixed-width positions from Personas detallado_WEB.xls:
#   FACTOR 20-33 | EDAD 40-42 | SEXO 43 (1 Hombre, 6 Mujer) | RELA 123 | ESCUR1 135-136
# RELA has SIX categories and NO 'labores del hogar': homemaker cannot be separated (FINDING 51).
set -e
unzip -p "$1" | awk '
function band(a){ if(a<11)return "u11"; if(a<15)return "11-14"; if(a<25)return "15-24"; if(a<35)return "25-34"; if(a<45)return "35-44"; if(a<55)return "45-54"; if(a<65)return "55-64"; if(a<75)return "65-74"; return "75+" }
{
  w=substr($0,20,14)+0; a=substr($0,40,3)+0; s=substr($0,43,1); r=substr($0,123,1); e=substr($0,135,2); gsub(/ /,"",e)
  tot+=w; n++
  AG[band(a)]+=w
  if(a>=11){ p11+=w; if(s=="1") m11+=w; else if(s=="6") f11+=w }
  if(a>=16 && a<=74){
    b1674+=w
    if(r=="1")                 E["employed"]+=w
    else if(r=="2"||r=="3")    E["unemployed"]+=w
    else if(r=="6"&&e!="")     E["student"]+=w
    else if(r=="5")            E["retired"]+=w
    else if(r=="4"||r=="6")    E["other_inactive_incl_homemaker"]+=w
    else                       E["blank"]+=w
  }
}
END{
  printf "RECORDS\t%d\n", n
  printf "WEIGHTED_TOTAL_ALL_AGES\t%.2f\n", tot
  n2=split("u11 11-14 15-24 25-34 35-44 45-54 55-64 65-74 75+",B," ")
  for(i=1;i<=n2;i++) printf "AGE\t%s\t%.2f\n",B[i],AG[B[i]]
  printf "BASE11PLUS\t%.2f\nSEX\tmale\t%.2f\nSEX\tfemale\t%.2f\n", p11, m11, f11
  printf "BASE16_74\t%.2f\n", b1674
  n3=split("employed unemployed student retired other_inactive_incl_homemaker blank",K," ")
  s=0; for(i=1;i<=n3;i++){ printf "ECON1674\t%s\t%.2f\t%.6f\n",K[i],E[K[i]],E[K[i]]/b1674; s+=E[K[i]] }
  printf "ECON1674\tPARTITION_RESIDUAL\t%.2f\n", s-b1674
}'
