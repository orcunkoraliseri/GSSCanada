#!/bin/bash
#SBATCH -J s5_void
#SBATCH -p ps
#SBATCH -c 1
#SBATCH --mem=2G
#SBATCH -t 7-00:00:00
#SBATCH -o /speed-scratch/o_iseri/5J/train/logs/s5_void_%j.out
T=/speed-scratch/o_iseri/5J/train
cd $T || exit 2
echo "start=$(date -Iseconds)"
echo "--- ls ckpt BEFORE"; ls $T/ckpt
[ -d $T/ckpt/S ] && mv $T/ckpt/S $T/ckpt/S_void_1404570
[ -d $T/ckpt/smoke ] && mv $T/ckpt/smoke $T/ckpt/smoke_void_1404569
echo "--- ls ckpt AFTER"; ls $T/ckpt
[ -e $T/ckpt/S ] && { echo "FAIL ckpt/S exists"; exit 4; }
[ -e $T/ckpt/smoke ] && { echo "FAIL ckpt/smoke exists"; exit 4; }
echo "VOID_OK end=$(date -Iseconds)"
