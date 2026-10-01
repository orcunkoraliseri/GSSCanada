#!/bin/bash
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=8G
#SBATCH -J hh_A1
# Gate A1: compare R/es_60 with the local reference copy; seen-failing: a copy with one byte changed must FAIL.
R=/speed-scratch/o_iseri/5J/households
PY=/speed-scratch/o_iseri/envs/step4/bin/python
$PY -u -c "import sys,numpy,pandas;print('python',sys.version.split()[0],'numpy',numpy.__version__,'pandas',pandas.__version__)"
TOOLS=/speed-scratch/o_iseri/5J/households/tools
$PY -u $TOOLS/hh_compare.py $R/ref/es_60 $R/es_60 A1_real; echo "A1 real exit=$?"
rm -rf $R/scratch_bad; mkdir -p $R/scratch_bad; cp -r $R/es_60 $R/scratch_bad/es_60
$PY -u - <<PYEOF
import glob
f = sorted(glob.glob("$R/scratch_bad/es_60/presence/*.csv"))[0]
b = bytearray(open(f, "rb").read())
i = len(b) // 2
print("SEEDFAIL changing one byte of", f, "offset", i, "from", chr(b[i]))
b[i] = ord("7") if b[i] != ord("7") else ord("8")
open(f, "wb").write(bytes(b))
PYEOF
$PY -u $TOOLS/hh_compare.py $R/ref/es_60 $R/scratch_bad/es_60 A1_seenfail; echo "A1 seenfail exit=$? (must be 1)"
