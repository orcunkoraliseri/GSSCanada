#!/bin/tcsh
# WP4 chain v2 (2026-09-29 evening), after smoke 1401430 FAILED only at the production-model load (keras 3.13 files on
# keras 3.10). Its hindcast part passed on the real data (1-epoch train, save, load, score, G4.1, G4.4), so the trainings
# start at once. The production-model check (probe, converted models + fingerprint) gates only sens2025.
# CPUs (1J cap 64): trainings 7x8 = 56 + probe 3 (+ sens2025 3 after it) <= 62; scorings 7x8 = 56 + sens2025 3 = 59.
set J = /speed-scratch/o_iseri/1J_rerun/wp4/code/wp4_job.sh
set L = /speed-scratch/o_iseri/1J_rerun/logs
set C = "-A chachemv -p ps -t 7-00:00:00"

set jp = `sbatch --parsable $C -c 3 --mem=32G -J wp4_probe -o $L/wp4_probe_%j.out $J probe`
echo "probe $jp"

set tr = ""
foreach s ( 1 2 3 4 5 )
    set j = `sbatch --parsable $C -c 8 --mem=32G -J wp4_tr_s${s}_ld128 -o $L/wp4_train_s${s}_ld128_%j.out $J train --seed $s --latent 128`
    echo "train seed $s ld128 $j"
    set tr = "${tr}:${j}"
end
foreach L2 ( 64 256 )
    set j = `sbatch --parsable $C -c 8 --mem=32G -J wp4_tr_s1_ld${L2} -o $L/wp4_train_s1_ld${L2}_%j.out $J train --seed 1 --latent $L2`
    echo "train seed 1 ld$L2 $j"
    set tr = "${tr}:${j}"
end

set js = `sbatch --parsable $C -c 3 --mem=32G -J wp4_sens2025 -o $L/wp4_sens2025_%j.out --dependency=afterok:$jp $J sens2025`
echo "sens2025 $js"

set sc = ""
foreach s ( 1 2 3 4 5 )
    set j = `sbatch --parsable $C -c 8 --mem=32G -J wp4_sc_s${s}_ld128 -o $L/wp4_score_s${s}_ld128_%j.out --dependency=afterok${tr} $J score --seed $s --latent 128`
    echo "score seed $s ld128 $j"
    set sc = "${sc}:${j}"
end
foreach L2 ( 64 256 )
    set j = `sbatch --parsable $C -c 8 --mem=32G -J wp4_sc_s1_ld${L2} -o $L/wp4_score_s1_ld${L2}_%j.out --dependency=afterok${tr} $J score --seed 1 --latent $L2`
    echo "score seed 1 ld$L2 $j"
    set sc = "${sc}:${j}"
end

set ja = `sbatch --parsable $C -c 1 --mem=16G -J wp4_aggregate -o $L/wp4_aggregate_%j.out --dependency=afterok${sc},afterany:$js $J aggregate`
echo "aggregate $ja"
