#!/bin/bash
# login node: sbatch only. Chain: stand-ins (1404309) -> group A (3 scorer jobs) -> group B (3) -> group C (2 planted + misc)
F=/speed-scratch/o_iseri/5J/freeze
cd $F
O=$F/out/standins
B1="--b1 $O/weakb1"
CT="--control $O/bldmean"
S() { sbatch --parsable -J $1 --dependency=$2 frz_score.sbatch "$3"; }
A1=$(S sc_good afterok:1404309 "--pred $O/good $B1 $CT --secondary --selftest 20")
A2=$(S sc_deleted afterok:1404309 "--pred $O/deleted $B1 $CT")
A3=$(S sc_trainmean afterok:1404309 "--pred $O/trainmean $B1 $CT")
echo "A $A1 $A2 $A3"
DA=afterany:$A1:$A2:$A3
B_1=$(S sc_bldmean $DA "--pred $O/bldmean $B1 $CT")
B_2=$(S sc_shift2 $DA "--pred $O/shift2 $B1 $CT")
B_3=$(S sc_ctrlgood $DA "--pred $O/good $B1 --control $O/good")
echo "B $B_1 $B_2 $B_3"
DB=afterany:$B_1:$B_2:$B_3
C1=$(S sc_crash $DB "--pred $O/good $B1 $CT --plant crash")
C2=$(S sc_highk $DB "--pred $O/good $B1 $CT --k 1e7")
C3=$(sbatch --parsable --dependency=$DB frz_misc.sbatch)
echo "C $C1 $C2 $C3"
