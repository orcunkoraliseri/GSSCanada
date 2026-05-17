# Step 4 Training Log — v4 (J5 Series)

---

## Progress Log

### 2026-05-17 — J5-X1 + J5-X1b bundle build (Sonnet employee task)

**Timestamp:** 2026-05-17

**Objective:** Build and stage the J5-X1 + J5-X1b sequential bundle for submission to the Speed HPC cluster. Both variants test the head-input-starvation hypothesis (binary heads re-routed from shallow Arm-2 NAT fusion to activity decoder output), with and without the `.detach()` gradient barrier.

---

#### Files edited / created

| Action | Path |
|--------|------|
| ARCHIVE | `2J_docs_occ_nTemp/step4_Speed_Cluster/archive/04B_model_pre_J5_X1.py` — predecessor state before J5_X1/X1b edit |
| EDITED  | `2J_docs_occ_nTemp/04B_model.py` — added J5_X1/X1b branches in `JSeriesHybrid.__init__`, `forward()`, `infer()`; added `_arm1_decode_tf_full()` helper |
| CREATED | `2J_docs_occ_nTemp/step4_Speed_Cluster/configs/J5_X1.yaml` — J3 byte-for-byte, `model_type: J5_X1` |
| CREATED | `2J_docs_occ_nTemp/step4_Speed_Cluster/configs/J5_X1b.yaml` — J3 byte-for-byte, `model_type: J5_X1b` |
| EDITED  | `2J_docs_occ_nTemp/04D_train.py` — extended MODEL_TYPE allow-lists to include J5_X1, J5_X1b; added J5 config block; added `_DEBUG_GRAD` env-var guard and backward unit test |
| EDITED  | `2J_docs_occ_nTemp/04E_inference.py` — extended `_mtype` allow-list to include J5_X1, J5_X1b |
| CREATED | `2J_docs_occ_nTemp/step4_Speed_Cluster/jobs/J5_X1_bundle.sh` — bundled sbatch script (J5_X1 train→eval→J5_X1b train→eval) |
| CREATED | `2J_docs_occ_nTemp/step4_Speed-Cluster_docs/step4_training_v4.md` — this file |

---

#### Archive command run

```
cp 2J_docs_occ_nTemp/04B_model.py \
   2J_docs_occ_nTemp/step4_Speed_Cluster/archive/04B_model_pre_J5_X1.py
```

Covers both J5-X1 and J5-X1b (they share the same predecessor state, as specified).

---

#### Model changes summary (`04B_model.py`)

- `JSeriesHybrid.__init__`: added `self._mtype = _mtype`; extended `arm2_act_proj` condition from `("J3","J4_1","J4_2","J4_3")` to include `"J5_X1","J5_X1b"` — modules defined but bypassed in forward/infer.
- New method `_arm1_decode_tf_full(dec_act_seq, tgt_strata, memory, cond_vec, cycle_idx)` — returns `(act_logits, dec_out)`. Used only by J5_X1/X1b head routing.
- `forward()`: for J5_X1/X1b, calls `_arm1_decode_tf_full`; sets `binary_input = dec_out.detach()` (J5_X1) or `binary_input = dec_out` (J5_X1b). For all other model types, existing Arm-2 path unchanged.
- `infer()`: same branch — calls `_arm1_decode_tf_full` with AR-generated tokens for a teacher-forcing pass to get decoder hidden states; feeds result to binary heads. Arm-2 path unchanged for J3/J4_x.

---

#### Partition cap check result

**Finding: pg partition very likely caps at 24h.** All existing J-series sbatch scripts (`job_step4_J1.sh` through `job_step4_J4_3.sh`) use `--time=24:00:00`. The bundle script requests `--time=38:00:00` (34h estimate + 4h buffer). If sbatch rejects the 38h request with "Invalid time specification", split into two jobs:

- Job A (J5_X1): train + eval — `--time=24:00:00`
- Job B (J5_X1b): train + eval — `--time=24:00:00`, submitted with `--dependency=afterok:<jobA_id>`

The bundle script includes these instructions in its comment header.

---

#### Module check result

Scripts checked: `04B_model.py`, `04D_train.py`, `04E_inference.py`, `04F_validation.py`.

All imports: `torch`, `numpy`, `pandas`, `scipy`, `matplotlib`, `json`, `csv`, `argparse`, `importlib`, `math`, `os`, `sys`, `time`.

Cluster env `step4` (`requirements_step4.txt`): `torch>=2.0,<2.5`, `numpy>=1.24`, `pandas>=2.0`, `scikit-learn>=1.3`, `matplotlib>=3.7`, `scipy>=1.11`.

**Result: all packages present. No install/precheck line added to sbatch script.**

---

#### Git commit

Commit message: `[ml]: add J5-X1 + J5-X1b bundle for binary-head re-route experiment`

Files committed: archive copy, `04B_model.py`, both YAML configs, `04D_train.py`, `04E_inference.py`, `jobs/J5_X1_bundle.sh`, this progress log.

---

#### Hand-off commands

locally: `scp -r GSSCanada-main/2J_docs_occ_nTemp/ o_iseri@speed.encs.concordia.ca:~/step4_Speed_Cluster/`

on the cluster: `cd ~/step4_Speed_Cluster && sbatch jobs/J5_X1_bundle.sh`

**If pg caps at 24h** (expected — see cap check above):

on the cluster (Job A): `cd ~/step4_Speed_Cluster && sbatch --time=24:00:00 --job-name=J5_X1_A jobs/J5_X1_bundle.sh`

Then after Job A completes — submit Job B separately with the J5_X1b half of the script. Manager to prepare the split scripts if needed.

---

**Status:** STAGED — awaiting user scp + sbatch.
