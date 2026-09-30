#!/bin/tcsh
# Submit the WP4 chain (run on the login node: only sbatch is used). At most 24 CPUs at any time:
#   smoke 3 | 7 trainings x 3 = 21 (+ sens2025 3 = 24) | 7 scorings x 3 = 21 (+ sens2025 3 = 24) | aggregate 1
set J = /speed-scratch/o_iseri/1J_rerun/wp4/code/wp4_job.sh
set L = /speed-scratch/o_iseri/1J_rerun/logs
set C = "-A chachemv -p ps -t 7-00:00:00"

set j0 = `sbatch --parsable $C -c 3 --mem=32G -J wp4_smoke -o $L/wp4_smoke_%j.out $J smoke`
echo "smoke $j0"

set tr = ""
foreach s ( 1 2 3 4 5 )
    set j = `sbatch --parsable $C -c 3 --mem=32G -J wp4_tr_s${s}_ld128 -o $L/wp4_train_s${s}_ld128_%j.out --dependency=afterok:$j0 $J train --seed $s --latent 128`
    echo "train seed $s ld128 $j"
    set tr = "${tr}:${j}"
end
foreach L2 ( 64 256 )
    set j = `sbatch --parsable $C -c 3 --mem=32G -J wp4_tr_s1_ld${L2} -o $L/wp4_train_s1_ld${L2}_%j.out --dependency=afterok:$j0 $J train --seed 1 --latent $L2`
    echo "train seed 1 ld$L2 $j"
    set tr = "${tr}:${j}"
end

set js = `sbatch --parsable $C -c 3 --mem=32G -J wp4_sens2025 -o $L/wp4_sens2025_%j.out --dependency=afterok:$j0 $J sens2025`
echo "sens2025 $js"

set sc = ""
foreach s ( 1 2 3 4 5 )
    set j = `sbatch --parsable $C -c 3 --mem=32G -J wp4_sc_s${s}_ld128 -o $L/wp4_score_s${s}_ld128_%j.out --dependency=afterok${tr} $J score --seed $s --latent 128`
    echo "score seed $s ld128 $j"
    set sc = "${sc}:${j}"
end
foreach L2 ( 64 256 )
    set j = `sbatch --parsable $C -c 3 --mem=32G -J wp4_sc_s1_ld${L2} -o $L/wp4_score_s1_ld${L2}_%j.out --dependency=afterok${tr} $J score --seed 1 --latent $L2`
    echo "score seed 1 ld$L2 $j"
    set sc = "${sc}:${j}"
end

set ja = `sbatch --parsable $C -c 1 --mem=16G -J wp4_aggregate -o $L/wp4_aggregate_%j.out --dependency=afterok${sc},afterany:$js $J aggregate`
echo "aggregate $ja"
