#!/bin/bash
#SBATCH -J 5J_pilot_check
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=2G
#SBATCH -o /speed-scratch/o_iseri/5J/pilot/check_%j.out
# 5J pilot job 1: md5 every file the local list names, on the Speed copy; disk preflight; energyplus version.
# md5_local.txt lines: "<md5>  <path relative to pilot/>".  LOCAL_TEST=1 = md5 section only (used to test this script).
PILOT=${PILOT:-/speed-scratch/o_iseri/5J/pilot}
EP=${EP:-/speed-scratch/o_iseri/4J_step10_nocore/opt/EnergyPlus-23.1.0-87ed9199d4-Linux-Ubuntu20.04-x86_64}
cd "$PILOT" || { echo "no pilot dir $PILOT"; exit 2; }
: > md5_speed.txt
equal=0; differ=0; missing=0
while read -r want rel; do
  if [ -f "$rel" ]; then
    got=$(md5sum "$rel" | cut -d' ' -f1)
    echo "$got  $rel" >> md5_speed.txt
    if [ "$got" = "$want" ]; then equal=$((equal+1)); else differ=$((differ+1)); echo "DIFFER $rel want=$want got=$got"; fi
  else
    echo "MISSING  $rel" >> md5_speed.txt
    missing=$((missing+1)); echo "MISSING $rel"
  fi
done < md5_local.txt
echo "MD5 equal=$equal differ=$differ missing=$missing" | tee md5_summary.txt
if [ -z "$LOCAL_TEST" ]; then
  { echo "== date"; date; echo "== host"; hostname
    echo "== df -h /speed-scratch/o_iseri"; df -h /speed-scratch/o_iseri
    echo "== quota"; (quota -s 2>&1 || true)
    echo "== lfs quota"; (lfs quota -u o_iseri /speed-scratch 2>&1 || true)
    echo "== du -sh /speed-scratch/o_iseri"; (du -sh /speed-scratch/o_iseri 2>&1 || true)
    echo "== energyplus --version"; "$EP/energyplus" --version 2>&1
    echo "== /usr/bin/time"; ls -l /usr/bin/time 2>&1
  } > preflight.txt 2>&1
  grep -q "23.1.0-87ed9199d4" preflight.txt || { echo "energyplus version string not found in preflight.txt"; exit 3; }
fi
if [ "$differ" -ne 0 ] || [ "$missing" -ne 0 ]; then exit 1; fi
exit 0
