#!/bin/tcsh
#SBATCH --job-name=T01_athome_gap
#SBATCH -p ps
#SBATCH -c 32
#SBATCH --mem=64G
#SBATCH -t 7-00:00:00
#SBATCH -o /speed-scratch/o_iseri/2J_revision/T01/slurm_%j.out
#SBATCH -e /speed-scratch/o_iseri/2J_revision/T01/slurm_%j.err

set WORKDIR = /speed-scratch/o_iseri/2J_revision/T01
set OUTDIR = /speed-scratch/o_iseri/2J_revision/T01/out
mkdir -p $OUTDIR

/speed-scratch/o_iseri/envs/step4/bin/python $WORKDIR/athome_gap.py \
    --workdir $WORKDIR \
    --outdir $OUTDIR \
    --panel-manifest $WORKDIR/panel_manifest.csv
