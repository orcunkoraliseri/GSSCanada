#!/encs/bin/bash
SDIR=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs
PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
cd "$SDIR"
$PYTHON 3rdJ_04L_joint_rake_2split.py --r5_dir "$SDIR/outputs_step4/sweep/R11" --output_dir "$SDIR/outputs_step4/sweep/R11_raked" --temperature 0.8 > /speed-scratch/o_iseri/logs/R11_rake.log 2>&1 && $PYTHON 3rdJ_04_augmentationGSS_2split_val.py --step4_dir "$SDIR/outputs_step4/sweep/R11_raked" > /speed-scratch/o_iseri/logs/R11_rakeval_val.log 2>&1
