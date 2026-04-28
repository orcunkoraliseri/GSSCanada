# Executive Summary

### 1. What was the aim of the model?
The goal of the Step 4 deep learning model is to **generate synthetic residential occupancy and activity sequences**. 
Specifically, it is designed to take a respondent's demographic profile (a 76-dimensional vector) and their behavior on one type of day (e.g., a Weekday), and generate their behavior for the other types of days (e.g., Saturday and Sunday). 

For each of the 48 time slots in a day (30-minute resolution), the model must concurrently predict 11 features:
*   What the person is doing (1 of 14 **Activities**).
*   Where they are (Binary **AT_HOME** state).
*   Who they are with (9 binary **Co-presence** indicators, like Spouse, Children, Friends).

### 2. What was the issue?
The current model architecture (an Autoregressive Conditional Transformer) hit a **structural performance floor** during its hyperparameter tuning phase (at trial F10a). It could not reduce its errors any further, failing critical validation thresholds.

The core structural failures were:
*   **The "Stuck-State" (Exposure Bias):** Because the model predicts sequentially (autoregressively), once it strongly predicted someone was `AT_HOME`, that high-confidence prediction fed into the next time slot. The model would get "stuck" at home and fail to generate realistic transitions.
*   **Conditioning Collapse:** The decoder network essentially started ignoring the demographic inputs (who the person is) and the target day (what day it is trying to predict). It collapsed into just generating a "generic average" sequence.
*   **Sampling Bias:** The data it was being trained on was accidentally over-representing weekends (by ~2.3x). Because the model was ignoring its demographic conditioning, it defaulted to this weekend-heavy average, resulting in outputs where people stayed home way too much.

### 3. What is the solution?
To overcome these structural limits, the proposed solution involves a 5-point architectural overhaul derived strictly from the project's own diagnostic plans:

1.  **Cross-Attention for Conditioning:** Instead of just adding demographic data to the model's layers (which it proved it could ignore), use "Cross-Attention." This forces the model's decoder to explicitly look at the demographic and day-type inputs when making predictions.
2.  **Scheduled Sampling & Slot-Dropout:** During training, randomly hide the previous time slot's `AT_HOME` status from the model. This forces the model to look at the broader context of the sequence rather than lazily relying on the immediate previous step, preventing the "stuck-state."
3.  **Label Smoothing:** Prevent the model from ever being "100% sure" about a prediction (capping confidence at 95%). This stops the mathematical saturation that was locking the sequence in place.
4.  **Proportional Target Sampling:** Fix the data pipeline so the model is trained on a mathematically balanced ratio of Weekdays vs. Weekends, removing the baseline bias.
5.  **Decoder Capacity Expansion:** Increase the underlying size of the Transformer (`d_model` and `d_ff`). The model simply didn't have enough parameters to simultaneously juggle 14 activities, location, and 9 different co-presence channels across different demographic groups.

---

# Architectural Diagnostics & Proposal Report (Strict Document Baseline)

## 1. Observation of the Problem (The "Stuck-State")
Based on the `step4_training.md` and `04_augmentationGSS_hpc.md` logs, the Step 4 Conditional Transformer underwent an exhaustive 10-stage hyperparameter sweep (F1 through F10). The model hit a structural performance floor at trial **F10a** (composite score 1.306), failing to meet the hard validation gates for `AT_HOME` bias (6.98 pp gap vs target ≤ 5.3) and Activity JS divergence (0.0686 vs target ≤ 0.05). 

The documents explicitly conclude: *"Single-axis hyperparameter exploration is exhausted... a floor, not a tuning gap. The remaining headroom... is structural: decoder capacity / attention pattern / loss formulation, not loss weights or pos_weight tuning."*

The core structural failures diagnosed in the documents are:
*   **H3 — Autoregressive Feedback Amplification (Exposure Bias):** The `home_head` sigmoid outputs become saturated (>0.70). Because the model is trained with teacher-forcing but generates autoregressively, this saturated prediction is fed back into the next slot's input, causing the model to get "stuck" at home (cascading error).
*   **H4 — Decoder Ignores Conditioning:** The decoder body's gradient dominates the zero-initialized FiLM layers. Consequently, the model ignores the demographic conditioning (`cond_vec`) and target stratum (`tgt_strata`), defaulting to a corpus-average output.
*   **H1 — Training-Pair Target-Stratum Sampling Bias:** Because the 04C pairs are sampled uniformly across target strata rather than proportionally to the population, the decoder is trained on a diary distribution that is ~2.3× over-represented in weekends, pulling the corpus-average towards high-AT_HOME weekend behavior.

## 2. Understanding the Variables (From Step 3 Validation)
To design the architectural fix, the model must map exactly to the variables verified in `step3_validation_report.html` and `00_GSS_Occupancy_Pipeline.md`:

*   **Temporal Strata (`DDAY_STRATA`):** 3 categories (1=Weekday, 2=Saturday, 3=Sunday). The model observes 1 and must generate the other 2.
*   **Sequence Resolution:** 48 slots (downsampled from 144 to 30-minute intervals to reduce Transformer sequence length 3× and attention cost 9×).
*   **Input/Output Tokens (11 features per slot):**
    *   `occACT`: 14 grouped activity categories.
    *   `AT_HOME`: Binary (1=Home, 0=Away).
    *   `Co-presence`: 9 binary columns (`Alone`, `Spouse`, `Children`, `parents`, `otherInFAMs`, `otherHHs`, `friends`, `others`, `colleagues`). 
*   **Conditioning Vector (`d_cond` = 76):** 12 categorical demographics (one-hot), 1 continuous (`TOTINC`), and metadata (`CYCLE_YEAR`, `COLLECT_MODE`, `TOTINC_SOURCE`).

## 3. Proposed Better Architecture (Explicitly from the Documents)
The `step4_training.md` document explicitly outlines the required architectural interventions to address these structural limits (specifically in *Section 5: Candidate fixes* and *Section 10.7*). 

Based strictly on the project's own planned trajectory, the next architectural iteration must incorporate the following:

### A. Cross-Attention Conditioning (Fixes H4)
*   **Document Proposal (F4b):** Replace the current additive `strata_linear` + FiLM layers with **cross-attention over a compact stratum/cond embedding**.
*   **Rationale:** The current architecture passes conditioning via residual addition and FiLM, which the decoder has proven it can ignore. Cross-attention gives the decoder explicit attention pointers to the conditioning signal, forcing it to differentiate between Weekday and Weekend generations and resolving the `Spouse` explosion caused by the MLP auxiliary head (F8).

### B. Scheduled Sampling & Slot-Dropout (Fixes H3)
*   **Document Proposal (F3a / F3b):** Implement **Scheduled Sampling** or **Slot-Dropout** on the teacher-forcing auxiliary input.
*   **Rationale:** To fix the autoregressive feedback amplification (where the model gets stuck at home), the training loop in `04D_train.py` must close the train-inference mismatch. By randomly zeroing out the `AT_HOME` channel of `dec_aux_seq` during training (p=0.2 per slot), the decoder is forced to rely on broader context rather than just the previous-slot's `AT_HOME` feedback. 

### C. Label Smoothing for Saturation (Fixes H3)
*   **Document Proposal (F3c):** Break `home_head` saturation by adding label smoothing to the BCE loss.
*   **Rationale:** Mapping the targets from {0, 1} to {0.05, 0.95} ensures the sigmoid logits stay bounded, directly addressing the observed saturation where $\sigma > 0.70$ locks the inference loop.

### D. Proportional Target Sampling (Fixes H1)
*   **Document Proposal (F1a / F1b):** Rewrite `04C_training_pairs.py` so that target strata are sampled proportionally to the population, OR add a **target-stratum-inverse-frequency weight** to the per-pair loss in `04D_train.py`.
*   **Rationale:** This removes the 67% weekend over-representation in the supervision signal, eliminating the baseline push towards high-AT_HOME weekend diaries.

### E. Decoder Capacity Expansion
*   **Document Proposal:** The final verdict in F10a cites "decoder capacity" as a primary structural ceiling.
*   **Rationale:** The current 6-layer, 8-head, $d_{model}=256$ Transformer is under-parameterized for simultaneously tracking 14 activities, location, and 9 co-presence channels across 4 cycles. The next architecture should expand `d_model` and the feed-forward dimension (`d_ff`), supported by transitioning to Multi-GPU (DDP) training as outlined in the HPC plan.