# sourced by every V3 sbatch script (bash). Nothing here runs anything.
ROOT=/speed-scratch/o_iseri/3J_V3
export REPO=$ROOT/repo
export EPLUS_IDD=$REPO/Energy+.idd          # the local C:\EnergyPlusV24-2-0\Energy+.idd, uploaded
export OMP_NUM_THREADS=1
PY=/speed-scratch/o_iseri/envs/step4/bin/python
CODE=$REPO/3J_docs_occ_nTemp/writing/implementation/IMP/scripts/V3
