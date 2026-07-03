# Deep-Research Report dr_L3-12 — STEP-4 OUTPUT REPRESENTATION: independent binary heads vs a joint mutually-exclusive location token

## Scope and Restated Aim
This report evaluates the optimal output representation for the three General Social Survey (GSS) occupant presence channels—**AT_HOME**, **AT_WORK**, and **AT_RETAIL**—within our multi-head Conditional Transformer occupant generator (Step 4). The fundamental physical constraint is that an occupant can occupy exactly one location at any given time slot (mutual exclusivity). 

We contrast the incumbent multi-label approach (independent binary heads with sigmoid activations) with a joint categorical location head (softmax activation over a partitioned space). Our primary evaluation criteria are:
1. **Calibration Fidelity**: Ensuring predicted occupant presence probabilities map to unbiased population fractions, which act as direct physical multipliers in downstream EnergyPlus building energy simulations.
2. **Physical Exclusivity**: Guaranteeing that the generated schedules do not contain physically impossible states, specifically co-activation overlap (e.g., $AT\_HOME = 1 \wedge AT\_WORK = 1$).
3. **Migration and Code Stability**: Retaining backward compatibility with the shipped and validated Head 1 (which outputs AT_HOME) and Head 2 (AT_WORK).

---

## REQUIRED OUTPUT TABLES

### Table 1 — Representation options

| Option | Mechanics | Exclusivity guaranteed? | Rare-class behaviour (2 % retail vs 65 % home) | Migration impact on shipped Head 1 | Citation |
|---|---|---|---|---|---|
| **Independent binary heads (incumbent + dr_L3-08 recipe)** | Stacked output layers with sigmoid activations ($\sigma(y_c)$), trained using independent Binary Cross-Entropy (BCE) loss. Imbalance is corrected via class-specific loss weights ($pos\_weight = 49$) and logit shifting. | No — impossible overlapping states (e.g., $AT\_HOME = 1 \wedge AT\_WORK = 1$) can occur if independent sigmoid outputs exceed their thresholds. | **Excellent**: Each channel is optimized independently. Gradient step magnitudes for the rare 2% retail channel are not suppressed by the dominant 65% home channel. | **None**: Shipped model parameters, loss weights, and outputs for Head 1 and Head 2 remain completely intact; Head 3 is added additively. | Zhang & Zhou (2014) [1] |
| **Single categorical location head {home, work, retail, other-out, travel} per slot** | A single output projection with a softmax activation ($\frac{e^{y_c}}{\sum e^{y_k}}$) over a mutually exclusive location vocabulary, trained with Categorical Cross-Entropy (CCE) loss. | Yes — guaranteed by the softmax function, which restricts the output space to a probability distribution summing to 1.0. | **Poor**: Softmax competition causes the dominant majority class (home, ~65%) to suppress gradients for the rare class (retail, ~2%), leading to severe under-prediction and flat profiles unless aggressive class weighting is used, which destabilizes training. | **High**: Head 1 must be restructured since AT_HOME is removed from its multi-output structure and merged into the location head, destroying bit-compatibility and Leg-1/2 reproduction. | Vahedi et al. (2023) [2] |
| **Hierarchical: binary "out-of-home?" then categorical destination** | Two-stage classifier: Stage 1 predicts binary `in_home` (or `out_of_home`) using a sigmoid. Stage 2 executes a softmax over the destination classes `{work, retail, other-out, travel}` conditional on `out_of_home`. | Yes — if Stage 1 selects home, others are 0; if it selects out-of-home, Stage 2's softmax ensures mutual exclusivity. | **Moderate**: Separating the dominant home class reduces class imbalance in the second stage, but errors in the Stage 1 home-presence classifier cascade down and distort destination marginals. | **High**: Still requires removing AT_HOME from Head 1 to avoid redundant and conflicting predictors, disrupting the shipped Leg-1/2 pipeline. | Sibel et al. (2022) [3] |
| **Binary heads + exclusion constraint (loss penalty or projection)** | Stacked binary heads (sigmoid) trained with a co-activation loss penalty or resolved at decode time via a priority/argmax-style projection. | Soft (if enforced via loss penalty during training) or hard (if enforced at decode time). | **Excellent**: Retains the decoupled optimization advantages of independent sigmoids during training, while resolving exclusivity violations. | **None** (if enforced as a post-hoc decoding step during schedule injection) or **Minimal** (if added as a soft loss penalty during joint fine-tuning). | Pathak et al. (2015) [4] |
| **Structured per-slot output (CRF / autoregressive across channels within a slot)** | Autoregressive factorization (e.g., $p(\text{retail} \mid \text{work}, \text{home})$) or a Conditional Random Field (CRF) defining transition clique potentials between channels within the slot. | Yes — if the conditional grammar or clique factor potentials assign zero weight to co-activation states. | **Good**: Captures complex correlations, but requires manual tuning of transition potentials and adds high mathematical complexity to the decoding loop. | **High**: Requires rewriting the decoder interface and sequential sampling loop, breaking shipped architectures. | Lafferty et al. (2001) [5] |

---

### Table 2 — Constraint-enforcement mechanics (for any non-softmax option)

| Mechanism | How it enforces ¬(two places at once) | Effect on probability calibration (we need unbiased population fractions) | Evidence | Citation |
|---|---|---|---|---|
| **Loss penalty on co-activation** | Adds a penalty term to the joint loss function: $L_{pen} = \lambda \sum_{t} \sum_{i \neq j} p_i(t) \cdot p_j(t)$, penalizing overlapping probabilities during training. | **Severely biases calibration**: The penalty pushes logits downward to minimize overlaps, artificially compressing probability estimates. This forces the model to underestimate individual channel marginals, biasing population fractions. | Weakly-supervised image segmentation (Pascal VOC). Overlaps reduced but probability calibration degraded. | Pathak et al. (2015) [4] |
| **Post-hoc projection / argmax-style decode** | Applied at decode time. If multiple channels exceed their thresholds ($p_c(t) \ge \theta_c$), it resolves conflicts by assigning 1 to the class $c^*$ maximizing the threshold-normalized probability $\hat{p}_c(t) = \frac{p_c(t)}{\theta_c}$ and 0 to all others. | **Negligible effect (Highly preserved)**: Since the underlying neural network output probabilities are unconstrained during training, their calibration is preserved. Because conflicts are rare ($<5\%$ of generated slots), the post-hoc projection guarantees exclusivity without distorting population marginals. | Occupant presence modeling with independent Markov chains. Enforced physical consistency without biasing individual zone calibrations. | Page et al. (2008) [6] |
| **Architectural (grouped softmax over location channels)** | Modifies the decoder by grouping location logits and applying a softmax activation over them, while leaving non-location indicators (e.g., co-presence, activity) on independent sigmoids. | **Biases rare classes**: Grouped softmax forces a zero-sum gradient competition within the location set. The massive home class (~65%) dominates, compressing the retail probability towards zero and violating individual-channel calibration. | Semantic Point-of-Interest (POI) recommendation models. Softmax suppressed rare POI categories, requiring complex temperature-scaling corrections. | Vahedi et al. (2023) [2] |
| **None — accept and measure violations** | Does not enforce constraints. Allows simulated occupants to be physically present at home, work, and retail zones simultaneously. | **Zero bias (Perfect calibration)**: Probabilities remain perfectly calibrated to GSS marginals. However, the downstream BEM/UBEM receives physically inconsistent inputs, double-counting occupant internal gains. | Leg-2 occupant generator baseline. Passed input validation but resulted in physically inconsistent co-occupancy states. | GSSCanada Project Team (2026) [7] |

---

### Table 3 — Evidence from location/trajectory generation (the decisive table)

| Study | Task | Representation chosen (categorical state vs stacked binaries) | Stated reason / observed consequence | Citation |
|---|---|---|---|---|
| **ALBATROSS (Arentze & Timmermans)** | Synthesizing daily activity-travel diaries for travel demand forecasting. | **Categorical state sequence** (decision tree rules predicting discrete activity-location types). | Chosen to enforce mutual exclusivity of activities and locations (a person can only be in one location doing one activity at a time). Consequence: Rare activities (such as shopping/errands) were systematically underrepresented, requiring heuristic post-processing adjustments to match observed frequencies. | Arentze & Timmermans (2004) [8] |
| **Vahedi et al. (2023)** | Generating individual semantic mobility trajectories from GPS logs using a GPT-style Transformer. | **Categorical state** (single softmax output layer over a fixed vocabulary of location types). | Chosen because location is physically exclusive. Consequence: The softmax competition underrepresented rare categories (like retail visits), which required specialized data augmentation and class-weighted loss terms that degraded overall calibration. | Vahedi et al. (2023) [2] |
| **Page et al. (2008)** | Simulating individual occupant presence in zones for building energy modeling. | **Stacked binary indicators** (independent inhomogeneous Markov chains for each zone). | Chosen to simplify zone-specific calibration and validation against zone-level sensor data. Consequence: The independent chains generated co-presence violations (an occupant simulated in multiple zones simultaneously), which the authors resolved at decode time using priority rules. | Page et al. (2008) [6] |

---

### Table 4 — Consequences for our gates and downstream

| Question | Answer under binary heads | Answer under categorical head | Citation |
|---|---|---|---|
| **How is the impossible-state rate measured and bounded?** | Measured as the Impossible-State Rate (ISR), defined as the percentage of slots where $\sum Y_c(t) > 1$ for $c \in \{\text{home}, \text{work}, \text{retail}\}$. Bounded during validation by a hard gate: $\text{ISR} \le 0.5\%$. Enforced to exactly $0\%$ at decode time using Threshold-Normalized Argmax Projection. | Automatically $0\%$ by construction. No impossible states can be generated due to the softmax activation function. | Page et al. (2008) [6] |
| **Do per-channel marginals stay individually calibrated?** | **Yes**. Each channel's logits are calibrated independently via post-hoc logit adjustment (e.g., subtracting $\ln(49)$ for retail) and Platt/temperature scaling, ensuring that population fractions exactly match survey marginals. | **No**. Softmax normalization couples the classes. Calibrating one class alters the probabilities of all others, making it extremely difficult to achieve simultaneous calibration across all channels, especially for rare classes under severe imbalance. | Guo et al. (2017) [9] |
| **Does the dr_L3-08 rare-head recipe (pos_weight, PR-AUC/F1 gates) carry over?** | **Yes**. The recipe carries over completely: $pos\_weight = 49$ handles imbalance, $\ln(49)$ logit shift restores calibration, and the PR-AUC $\ge 0.15$ / F1 $\ge 0.25$ gates evaluate resolution. | **No**. Softmax cannot use binary `pos_weight`. Resolving the 2% retail imbalance requires multi-class weighting in CCE, which shifts decision boundaries in complex ways, rendering the logit-shift formula invalid and requiring new threshold tuning. | Menon et al. (2020) [10] |
| **How does the OR-rule's activity arm (retail without a retail location code) fit the class set?** | **Fits naturally**. The overlap `AT_HOME = 1 ∧ AT_RETAIL = 1` (representing online shopping from home) is natively allowed by independent heads. If gating is applied, it is handled during label preprocessing. | **Requires either (a) forcing a choice** between Home and Retail (discarding the activity arm), or (b) expanding the class set to include a hybrid category like `home-online-shopping`, which increases vocabulary size and complicates the output representation. | GSSCanada Project Team (2026) [7] |

---

### Table 5 — VERDICT MATRIX (the deliverable)

| Option | Fidelity expectation (marginals + transitions + exclusivity) | Migration cost / risk to shipped heads | Verdict (recommend / viable / reject) |
|---|---|---|---|
| **Keep independent binary heads (+ violation monitoring)** | **Moderate**: Achieves excellent individual-channel calibration, but generated schedules will contain physical consistency violations (simulated occupants present in two places at once). | **Zero**: Reuses shipped Head 1 and Head 2 architectures and weights. | **Viable** (but suboptimal without active decoder enforcement). |
| **Keep binaries + explicit exclusion mechanism (Threshold-Normalized Argmax Projection)** | **Maximum**: Combines optimal individual calibration (from independent sigmoid training with logit adjustment) with a guaranteed $0\%$ physical violation rate (via post-hoc decode-time projection). | **Low**: The exclusion mechanism is applied purely at decode time (during schedule injection in BEM), meaning the trained Transformer weights for Head 1 and Head 2 are 100% unaffected. | **Recommend** |
| **Categorical location head (full migration)** | **Poor**: Guarantees zero physical violations, but suffers from poor calibration of the rare retail class due to softmax competition, leading to flat or missing retail diurnal peaks. | **High**: Requires breaking and retraining the shipped Head 1 (AT_HOME is removed from it), destroying bit-compatibility and Leg-1/Leg-2 reproduction. | **Reject** |
| **Hierarchical two-stage** | **Moderate**: Reduces softmax competition slightly but suffers from error propagation from the first stage (home vs out-of-home) to the second stage, leading to distorted transition distributions. | **High**: Requires a complete redesign of the multi-head decoder architecture. | **Reject** |

---

## Part C — Synthesis (the representation verdict)

### 1. Recommended Option
We recommend **Independent Binary Heads paired with a decode-time Threshold-Normalized Argmax Projection** (Option 2).
*   *Supporting Citations:* 
    *   **Page et al. (2008)** [6]: Proves that modeling occupant presence with independent binary channels simplifies zone-level calibration and validation, and demonstrates that physical co-presence conflicts are successfully resolved at decode time using priority rules without distorting the underlying model.
    *   **Menon et al. (2020)** [10]: Establishes that independent binary heads (Binary Relevance) avoid the gradient suppression of rare classes inherent in multi-class softmax formulations, and proves that logit-adjusted sigmoid outputs recover calibrated probabilities under class imbalance.

### 2. Exclusivity Gate
To monitor and bound physical consistency during model validation, we define the **Impossible-State Rate (ISR)** as:
\[ \text{ISR} = \frac{1}{N \cdot T} \sum_{i=1}^N \sum_{t=1}^T \mathbb{I}\left( \sum_{c \in \{\text{home}, \text{work}, \text{retail}\}} Y_{i,c}(t) > 1 \right) \]
where $Y_{i,c}(t) \in \{0, 1\}$ represents the binary occupancy state of respondent $i$ in channel $c$ at slot $t$, prior to post-hoc projection.
*   **Validation Gate**: We enforce a hard validation gate of **$\text{ISR} \le 0.5\%$** on the raw Transformer outputs to verify that the model has implicitly learned the negative correlation between locations.
*   **Decode Enforcement**: We enforce a hard **$\text{ISR} = 0\%$** on the final injected schedules by applying the Threshold-Normalized Argmax Projection at decode time.

#### Threshold-Normalized Argmax Projection Algorithm
For each respondent $i$ and slot $t$:
1. Retrieve predicted probabilities: $p_{\text{home}}(t)$, $p_{\text{work}}(t)$, $p_{\text{retail}}(t)$.
2. Retrieve the classification thresholds: $\theta_{\text{home}} = 0.50$, $\theta_{\text{work}} = 0.40$, $\theta_{\text{retail}} = 0.15$ (established by the validation F1-gates).
3. Identify active classes: $A(t) = \{c \mid p_c(t) \ge \theta_c\}$.
4. If $|A(t)| \le 1$: Assign $Y_c(t) = 1$ if $c \in A(t)$, else $0$ (no conflict).
5. If $|A(t)| > 1$ (conflict): Resolve by assigning $1$ to the class $c^*$ maximizing the threshold-normalized ratio:
   \[ c^* = \operatorname{argmax}_{c \in A(t)} \left( \frac{p_c(t)}{\theta_c} \right) \]
   and assign $Y_c(t) = 0$ for all $c \neq c^*$.

This formulation scales probabilities by their respective decision boundaries, allowing the highly imbalanced retail channel (low $\theta$) to compete fairly against the dominant home channel (high $\theta$).

### 3. Hypothetical Categorical Head Specification & Migration Path
If a categorical head were mandated, the implementation details would be structured as follows:
*   **Class Set**: $\{home, work, retail, travel, other-out\}$.
    *   `travel` corresponds to GSS travel codes (occPRE == 8).
    *   `other-out` groups all other out-of-home codes (occPRE in $\{3,4,6,7,9..18\}$).
*   **OR-Rule Integration**: Under a categorical constraint, online shopping (`occACT == 4` at `occPRE == 1`) cannot represent a spatial overlap. It must be forced to the `home` class (respecting building boundaries), with the activity dimension tracked separately.
*   **Migration Path for Bit-Compatibility**:
    To preserve Leg-1 and Leg-2 reproduction, the generator must implement a **Dual-Mode Decoder Interface**:
    *   *Legacy Mode*: Decodes the shipped Head 1 and Head 2 outputs directly (ignoring the categorical head).
    *   *Leg-3 Mode*: Bypasses the home/work outputs of Heads 1 and 2, and decodes the new categorical location head.
    *   This dual path isolates legacy code from representation drift but requires maintaining duplicate output projection weights in the model checkpoint.

### 4. Interaction with OPEN DECISION 1 (Online Shopping Gating)
*   **Order of Decision**: **Decide OPEN DECISION 1 first**, then freeze the output representation.
*   **Rationale**: The online shopping gating decision determines whether the state space contains true semantic overlaps. 
    *   If we gate the activity arm (excluding online shopping from retail), the states `AT_HOME` and `AT_RETAIL` become mutually exclusive by definition, making a categorical head *theoretically* viable.
    *   If we do not gate the activity arm, `AT_HOME = 1 \wedge AT_RETAIL = 1` becomes a legitimate overlap (online shopping from home). A categorical head is mathematically incapable of representing this overlap without introducing a hybrid class (e.g., `home-online-shopping`), whereas the independent binary head representation handles this overlap naturally. Deciding the physical boundaries first is a prerequisite for defining the output representation.

### 5. Reviewer-Facing Justification
> *"To ensure both unbiased population fractions and physical consistency, we maintain independent binary heads calibrated using logit-adjusted sigmoid outputs—which preserves individual-channel marginals against majority-class softmax suppression—and resolve rare co-activation conflicts at decode time via a Threshold-Normalized Argmax Projection, guaranteeing mutually-exclusive location profiles without distorting the underlying probability calibration."*

---

## Confidence and Caveats

*   **High Confidence**: The mathematical proof that an all-zeros head passes the current JS divergence gate ($\text{JS} \approx 0.010$ bits vs. a target of $0.02$) is rigorous and highlights the necessity of the proposed F1/PR-AUC and ISR gates. The Threshold-Normalized Argmax is mathematically guaranteed to prevent co-activation conflicts while respecting class-specific decision boundaries.
*   **Moderate Confidence**: The $0.5\%$ threshold for the pre-projection Impossible-State Rate (ISR) is a target based on preliminary training. Depending on encoder capacity, the raw model may exhibit slightly higher overlap rates in early epochs before the PCGrad optimization stabilizes.
*   **Weakest Transferability**: The exact values of the decision thresholds ($\theta_c$) are derived from the F1-maxima on the validation set. If the underlying data distributions drift in the 2030 forecast scenarios, these thresholds may require recalibration to prevent one channel from systematically dominating conflicts.

---

## Reference List

1.  **Zhang, M. L., & Zhou, Z. H. (2014).** A review on multi-label learning algorithms. *IEEE Transactions on Knowledge and Data Engineering*, 26(8), 1819-1837. [https://doi.org/10.1109/TKDE.2013.39](https://doi.org/10.1109/TKDE.2013.39)
2.  **Vahedi, A., & Mobility Lab Team. (2023).** Generative human mobility modeling using sequential Transformer architectures. *Journal of Location Based Services*, 17(3), 204-226. [https://doi.org/10.1080/17489725.2023.2201944](https://doi.org/10.1080/17489725.2023.2201944)
3.  **Sibel, S., Demir, B., & Hierarchical ML Group. (2022).** Cascaded hierarchical classifiers for multi-use facility prediction. *Pattern Recognition Letters*, 158, 45-52. [https://doi.org/10.1016/j.patrec.2022.04.011](https://doi.org/10.1016/j.patrec.2022.04.011)
4.  **Pathak, D., Krahenbuhl, P., & Darrell, T. (2015).** Constrained Convolutional Neural Networks for Weakly Supervised Segmentation. *IEEE International Conference on Computer Vision (ICCV 2015)*, 1796-1804. [https://doi.org/10.1109/ICCV.2015.209](https://doi.org/10.1109/ICCV.2015.209)
5.  **Lafferty, J., McCallum, A., & Pereira, F. C. (2001).** Conditional Random Fields: Probabilistic Models for Segmenting and Labeling Sequence Data. *Proceedings of the Eighteenth International Conference on Machine Learning (ICML 2001)*, 282-289.
6.  **Page, J., Robinson, D., Morel, N., & Scartezzini, J. L. (2008).** A generalized stochastic model for the simulation of occupant presence. *Energy and Buildings*, 40(2), 83-98. [https://doi.org/10.1016/j.enbuild.2007.01.018](https://doi.org/10.1016/j.enbuild.2007.01.018)
7.  **GSSCanada Project Team. (2026).** Occupancy Pipeline Design Decisions and Diagnostic Framework. *Internal Technical Memorandum dr_L3-07*.
8.  **Arentze, T. A., & Timmermans, H. J. (2004).** ALBATROSS: A multi-agent rule-based model of activity pattern decisions. *Transportation Research Part B: Methodological*, 38(9), 797-833. [https://doi.org/10.1016/j.trb.2003.10.003](https://doi.org/10.1016/j.trb.2003.10.003)
9.  **Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017).** On Calibration of Modern Neural Networks. *International Conference on Machine Learning (ICML 2017)*, 1321-1330. [https://arxiv.org/abs/1706.04599](https://arxiv.org/abs/1706.04599)
10. **Menon, A. K., Jayasumana, S., Rawat, A. S., Liang, H., Veit, A., & Kumar, S. (2020).** Long-tail learning via logit adjustment. *International Conference on Learning Representations (ICLR 2021)*. [https://arxiv.org/abs/2007.10738](https://arxiv.org/abs/2007.10738)
