#!/bin/tcsh
# WP4 generic job: sbatch -A chachemv -p ps -t 7-00:00:00 -c <n> --mem=<m> -J <name> -o <log> wp4_job.sh <mode> [seed] [latent]
# modes: smoke | train | score | aggregate | sens2025   (see wp4_hindcast.py)
# Exit codes: 0 ok; 8 a protected file changed; 9 protected file md5 differs from the recorded one;
#             11 data copy differs from the Speed mirror (only checked in smoke); other = python failure.
setenv WP4_ROOT /speed-scratch/o_iseri/1J_rerun/wp4
setenv WP4_MH_DIR /speed-scratch/o_iseri/1J_rerun/occ2025/code/eSim_occ_utils/25CEN22GSS_classification
set PY = /speed-scratch/o_iseri/1J_rerun/venv2025/bin/python
set MH = $WP4_MH_DIR
set MIRROR = /speed-scratch/o_iseri/GSSCanada/GSSCanada-main/0_Occupancy/Outputs_CENSUS
echo "PYTHON USED: $PY"
echo "JOB: $SLURM_JOB_ID mode=$argv[1] args=($argv) cpus=$SLURM_CPUS_PER_TASK host=`hostname`"

echo "=== protected files md5 (START) ==="
set a0 = `md5sum $MH/eSim_datapreprocessing.py | cut -d' ' -f1`
set b0 = `md5sum $MH/eSim_dynamicML_mHead_alignment.py | cut -d' ' -f1`
set c0 = `md5sum $MH/previous/eSim_dynamicML_mHead.py | cut -d' ' -f1`
echo "$a0 eSim_datapreprocessing.py"
echo "$b0 eSim_dynamicML_mHead_alignment.py"
echo "$c0 previous/eSim_dynamicML_mHead.py"
if ( "$a0" != "c3a790229d498243224ac185f9557135" || "$b0" != "9dc07b6408ebd636b0f423e129d78e00" || "$c0" != "aec6e0a655e349cb7fdf63301bdbf147" ) then
    echo "PROTECTED FILE MD5 DIFFERS FROM RECORDED"
    exit 9
endif

if ( "$argv[1]" == "smoke" ) then
    echo "=== data md5: uploaded local copy (CR removed) vs Speed mirror ==="
    set bad = 0
    foreach y ( 06 11 16 21 )
        set f = $WP4_ROOT/data/cen${y}_filtered2.csv
        set mine = `md5sum $f | cut -d' ' -f1`
        set mine_lf = `tr -d '\r' < $f | md5sum | cut -d' ' -f1`
        set mir = `md5sum $MIRROR/cen${y}_filtered2.csv | cut -d' ' -f1`
        set mir_lf = `tr -d '\r' < $MIRROR/cen${y}_filtered2.csv | md5sum | cut -d' ' -f1`
        echo "cen${y}_filtered2 uploaded=$mine uploaded_noCR=$mine_lf mirror=$mir mirror_noCR=$mir_lf"
        if ( "$mine_lf" == "$mir_lf" ) then
            echo "DATA cen${y}: SAME CONTENT (after removing carriage returns)"
        else
            echo "DATA cen${y}: DIFFERENT CONTENT"
            @ bad++
        endif
    end
    echo "=== production models md5 (uploaded) ==="
    md5sum $WP4_ROOT/prod_models/cvae_encoder.keras $WP4_ROOT/prod_models/cvae_decoder.keras
    if ( $bad > 0 ) then
        echo "DATA MIRROR CHECK: FAILED ($bad files differ)"
        exit 11
    endif
    echo "DATA MIRROR CHECK: PASS"
endif

cd $WP4_ROOT/code
$PY wp4_hindcast.py $argv
set rc = $status
echo "PYTHON EXIT: $rc"

echo "=== protected files md5 (END) ==="
set a1 = `md5sum $MH/eSim_datapreprocessing.py | cut -d' ' -f1`
set b1 = `md5sum $MH/eSim_dynamicML_mHead_alignment.py | cut -d' ' -f1`
set c1 = `md5sum $MH/previous/eSim_dynamicML_mHead.py | cut -d' ' -f1`
echo "$a1 $b1 $c1"
if ( "$a0" != "$a1" || "$b0" != "$b1" || "$c0" != "$c1" ) then
    echo "PROTECTED FILE CHANGED DURING JOB"
    exit 8
endif
echo "PROTECTED FILES UNCHANGED: YES"
exit $rc
