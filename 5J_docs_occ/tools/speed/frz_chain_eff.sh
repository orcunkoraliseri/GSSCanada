#!/bin/bash
# login node: sbatch only. fix 1 chain. $1 = job id of the effgood stand-ins job, $2 = job id of frz_mkfloors
F=/speed-scratch/o_iseri/5J/freeze
cd $F
O=$F/out/standins
B1="--b1 $O/weakb1"
CT="--control $O/effbldmean"
S() { sbatch --parsable -J $1 --dependency=$2 frz_score.sbatch "$3"; }
D1=afterok:$1
A1=$(S sc_effgood $D1 "--pred $O/effgood $B1 $CT --secondary --selftest 20")
A2=$(S sc_effdeleted $D1 "--pred $O/effdeleted $B1 $CT")
A3=$(S sc_effbldmean $D1 "--pred $O/effbldmean $B1 $CT")
A4=$(S sc_effshift2 $D1 "--pred $O/effshift2 $B1 $CT")
echo "A $A1 $A2 $A3 $A4"
DA=afterany:$A1:$A2:$A3:$A4
B1J=$(S sc_effctrl $DA "--pred $O/effgood $B1 --control $O/effgood")
B2J=$(S sc_highfloor $DA,afterok:$2 "--pred $O/effgood $B1 $CT --floors $F/out/floors_PLANTED_HIGH.json")
echo "B $B1J $B2J"
C1=$(sbatch --parsable --dependency=afterany:$B1J:$B2J frz_summarize_eff.sbatch)
echo "C summary $C1"
