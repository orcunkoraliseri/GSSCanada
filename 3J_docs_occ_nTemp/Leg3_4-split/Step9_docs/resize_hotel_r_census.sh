#!/bin/bash
# Enumerate the hotel-DHW state of all 56 arm-H cells, so the r reader can be written once against
# the real distribution instead of being patched one refusal at a time. Pure grep, no python.
#SBATCH --job-name=3J_L3_hotelrcensus
#SBATCH -p ps
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/step8_4split/campaign/logs/hotelrcensus_%j.out

CDIR=/speed-scratch/o_iseri/step8_4split/campaign/out_H_allfix/campaign_233932d7

printf "%-34s %5s %5s %6s %6s %6s %6s  %s\n" cell nMXU nT913 hotReq hotFbk nApp nUnres channels
for d in $(ls "$CDIR"); do
  p="$CDIR/$d/injected.idf.provenance.txt"
  if [ ! -f "$p" ]; then printf "%-34s  NO PROVENANCE\n" "$d"; continue; fi
  nmxu=$(grep -c 'MXU_Hotel_DHWv2' "$p")
  nt913=$(grep -c '^t9_13 hotel ' "$p")
  req=$(grep -m1 '^channels_requested=' "$p" | sed 's/^channels_requested=//')
  fbk=$(grep -m1 '^fallback_channels=' "$p" | sed 's/^fallback_channels=//')
  napp=$(grep -m1 '^n_dhw_applied=' "$p" | sed 's/^n_dhw_applied=//')
  nunres=$(grep -m1 '^n_dhw_unresolved=' "$p" | sed 's/^n_dhw_unresolved=//')
  hotreq=no; case "$req" in *"'hotel'"*) hotreq=YES;; esac
  hotfbk=no; case "$fbk" in *"'hotel'"*) hotfbk=YES;; esac
  printf "%-34s %5s %5s %6s %6s %6s %6s  %s\n" "$d" "$nmxu" "$nt913" "$hotreq" "$hotfbk" "$napp" "$nunres" "$req"
done
RC=$?
echo "census done rc=$RC : $(date)"
exit $RC
