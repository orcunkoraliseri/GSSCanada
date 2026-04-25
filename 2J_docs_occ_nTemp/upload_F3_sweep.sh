#!/bin/bash
# Run locally: bash upload_F3_sweep.sh
REMOTE=o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/occModeling/
cd "$(dirname "$0")"
scp 04A_dataset_assembly.py $REMOTE
scp 04B_model.py $REMOTE
scp 04C_training_pairs.py $REMOTE
scp 04D_train.py $REMOTE
scp 04Z_F3_compare.py $REMOTE
scp Speed_Cluster/job_04D_train_F3A.sh $REMOTE
scp Speed_Cluster/job_04D_train_F3B.sh $REMOTE
scp Speed_Cluster/job_04D_train_F3C.sh $REMOTE
scp Speed_Cluster/job_04D_train_F3D.sh $REMOTE
scp Speed_Cluster/job_04Z_F3_compare.sh $REMOTE
scp Speed_Cluster/submit_step4_F3_sweep.sh $REMOTE
echo "Upload complete."
