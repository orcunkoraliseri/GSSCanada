#!/encs/bin/bash
#SBATCH --job-name=test_expand
#SBATCH --partition=ps
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:10:00
#SBATCH --output=/speed-scratch/o_iseri/ep_wrappers/test_expand_%j.out

SRC=/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected/smoke/SingleD__Montreal_6A/sample_001_HH130192/2022
TMPTEST=/speed-scratch/o_iseri/ep_wrappers/test_expand_run
rm -rf "$TMPTEST" && mkdir -p "$TMPTEST"

cp "$SRC/in.idf" "$TMPTEST/in.idf"
cp "$SRC/Energy+.idd" "$TMPTEST/Energy+.idd"

echo "=== Running ExpandObjects wrapper ==="
/speed-scratch/o_iseri/ep_wrappers/ExpandObjects > "$TMPTEST/expand_stdout.txt" 2>&1
EC=$?
echo "ExpandObjects exit code: $EC"
echo "--- stdout ---"
cat "$TMPTEST/expand_stdout.txt"
echo "--- files created ---"
ls -la "$TMPTEST/"
echo "=== expanded.idf exists: $([ -f $TMPTEST/expanded.idf ] && echo YES || echo NO) ==="
