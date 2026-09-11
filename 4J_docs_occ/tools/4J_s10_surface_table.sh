#!/bin/bash
# READ-ONLY: dump the surface table (name|type|construction|zone|obc|obc_object) of the built IDF
# of one representative failed cell per building. No engine, no job, no write.
DISTRICT="$1"; R=/speed-scratch/o_iseri/4J_step10_nocore; RUNS="$R/runs/$DISTRICT"
AWKP='
  function trim(s){ gsub(/^[ \t\r\n]+|[ \t\r\n]+$/,"",s); return s }
  BEGIN{ RS=";" }
  { rec=$0; gsub(/!-[^\n]*/,"",rec); gsub(/[\r\n]/," ",rec);
    n=split(rec,f,",");
    if (n<10) next;
    if (toupper(trim(f[1]))!="BUILDINGSURFACE:DETAILED") next;
    printf "###S|%s|%s|%s|%s|%s|%s\n", trim(f[2]),trim(f[3]),trim(f[4]),trim(f[5]),trim(f[7]),trim(f[8]) }'
for id in "${@:2}"; do
  D=$(find "$RUNS" -maxdepth 1 -type d -iname "*${id}__*" 2>/dev/null | sort | head -1)
  echo "###BUILDING|$id"
  IDF=$(ls "$D"/*.idf 2>/dev/null | head -1); [ -z "$IDF" ] && { echo "###NOIDF"; continue; }
  awk "$AWKP" "$IDF"
  grep 'does not have the same materials in the reverse order' "$D/eplusout.err" | sed 's/^/###CN|/'
done
