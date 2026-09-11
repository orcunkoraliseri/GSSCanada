#!/bin/bash
# READ-ONLY ring extractor for C2 failure triage (Step 10, campaign C2).
# Reads eplusout.err + the built .idf of ONE representative failed cell per building.
# Writes nothing but a /tmp scratch file it deletes. No python, no engine, no sbatch, no scancel.
# usage: bash -s <DISTRICT> <building_id> [building_id ...]
DISTRICT="$1"
R=/speed-scratch/o_iseri/4J_step10_nocore
RUNS="$R/runs/$DISTRICT"
PAIRAWK='
  /Vertex size mismatch between base surface/ {
    b=$0; sub(/.*base surface :/,"",b); sub(/ and outside boundary surface:.*/,"",b);
    o=$0; sub(/.*and outside boundary surface: /,"",o);
    gsub(/^[ \t]+|[ \t]+$/,"",b); gsub(/^[ \t]+|[ \t]+$/,"",o); base=b; other=o; next }
  /The vertex sizes are/ {
    n=$0; sub(/.*sizes are /,"",n); sub(/ for base surface and .*/,"",n);
    m=$0; sub(/.* for base surface and /,"",m); sub(/ for outside boundary surface.*/,"",m);
    if (base!="") { printf "###PAIR|%s|%s|%s|%s\n", base, other, n, m; base="" } }'
SURFAWK='
  function trim(s){ gsub(/^[ \t\r\n]+|[ \t\r\n]+$/,"",s); return s }
  BEGIN{ while ((getline l < NFILE) > 0) { l=trim(l); if (l!="") want[toupper(l)]=1 } RS=";" }
  { rec=$0; gsub(/!-[^\n]*/,"",rec); gsub(/[\r\n]/," ",rec);
    n=split(rec,f,",");
    if (n<12) next;
    if (toupper(trim(f[1]))!="BUILDINGSURFACE:DETAILED") next;
    if (!(toupper(trim(f[2])) in want)) next;
    printf "###SURF";
    for (i=2;i<=n;i++) printf "|%s", trim(f[i]);
    printf "\n" }'
for id in "${@:2}"; do
  [ -z "$id" ] && continue
  D=$(find "$RUNS" -maxdepth 1 -type d -iname "*${id}__*" 2>/dev/null | sort | head -1)
  echo "###BUILDING|$id"
  if [ -z "$D" ] || [ ! -f "$D/eplusout.err" ]; then echo "###MISSING"; continue; fi
  IDF=$(ls "$D"/*.idf 2>/dev/null | head -1)
  echo "###DIR|$D"
  grep -A1 "Vertex size mismatch" "$D/eplusout.err" | awk "$PAIRAWK"
  echo "###COUNTS|vm=$(grep -c 'Vertex size mismatch' "$D/eplusout.err")|np=$(grep -c 'is non-planar' "$D/eplusout.err")|za=$(grep -c 'Zero or negative surface area' "$D/eplusout.err")|cn=$(grep -c 'does not have the same materials in the reverse order' "$D/eplusout.err")|cc=$(grep -c 'CalcCoordinateTransformation' "$D/eplusout.err")|co=$(grep -c 'coincident/collinear vertices' "$D/eplusout.err")"
  grep 'Zero or negative surface area' "$D/eplusout.err" | sed 's/^/###ZA|/'
  grep 'is non-planar' "$D/eplusout.err" | sed 's/^/###NP|/'
  if [ -z "$IDF" ]; then echo "###NOIDF"; continue; fi
  T=$(mktemp /tmp/_c2names.XXXXXX)
  grep -A1 "Vertex size mismatch" "$D/eplusout.err" | awk "$PAIRAWK" | awk -F'|' '{print $2; print $3}' | sort -u > "$T"
  if [ -s "$T" ]; then awk -v NFILE="$T" "$SURFAWK" "$IDF"; fi
  rm -f "$T"
done
