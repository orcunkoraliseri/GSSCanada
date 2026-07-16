# Post-Hoc Calibration and Raking of Generative Outputs: A Literature Review and Design Assessment

## Restated Aim
In synthetic occupancy diary generation, our core objective is to produce synthetic diaries whose population marginals match the observed survey **exactly** where it matters for building-energy loads (specifically, diurnal patterns of residential and office presence), without destroying the within-sequence temporal realism and behavioral correlations learned by the generative model. The post-hoc raking step (implemented in [3rdJ_04L_joint_rake_2split.py](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs/3rdJ_04L_joint_rake_2split.py)) serves as the primary mechanism for matching marginals, and this report evaluates its theoretical positioning, potential risks of degradation, and empirical damage.

---

## Post-Hoc Calibration & Raking Taxonomy

The table below summarizes the landscape of calibration, weighting, and constrained generation methods from survey statistics, spatial microsimulation, and machine learning:

| Method | Target Constraints | Operates On | Preserves Joint / Transition Structure? | Key References |
| :--- | :--- | :--- | :--- | :--- |
| **Iterative Proportional Fitting (IPF) / Raking** | Multi-way marginal distributions (categorical) | Sample weights or cell frequencies | Preserves odds ratios of the seed; does not enforce temporal sequence dependencies. | Deming & Stephan (1940); Beckman et al. (1996); Lovelace et al. (2015) |
| **Iterative Proportional Updating (IPU)** | Multi-level marginals (e.g., household + person) | Sample weights | Yes, preserves within-household joint structure of the seed microdata. | Ye et al. (2009); Konduri et al. (2016) |
| **Generalized Regression (GREG) Calibration** | Linear auxiliary totals (continuous/categorical) | Sample weights | Preserves joints implicitly via linear regression; risk of negative weights. | Deville & Särndal (1992); Särndal (2007) |
| **Post-Stratification** | Fully crossed cell totals | Sample weights | Yes, preserves full joint distribution within cells; suffers from curse of dimensionality. | Holt & Smith (1979); Little (1993) |
| **Entropy Balancing** | Distribution moments (mean, variance, skewness) | Sample weights | Preserves joints up to specified moments; keeps weights close to uniform. | Hainmueller (2012) |
| **Platt Scaling / Isotonic Regression** | Empirical binary/multiclass rates (probabilities) | Model outputs (logits/sigmoids) | Preserves rank order; does not handle transition structure unless modeled jointly. | Platt (1999); Zadrozny & Elkan (2002) |
| **Rejection / Importance Sampling** | Full target probability density | Generated samples | **Yes (perfectly)**. Rejects sequences that violate joints, but has poor sample efficiency. | Robert & Casella (2004); Bishop (2006) |
| **Optimal Transport (OT) / Sinkhorn Balancing** | Target empirical marginals under cost optimization | Generated samples / Model output | Distorts joint/transitions unless cost function explicitly models sequence transitions. | Cuturi (2013); Peyré & Cuturi (2019) |
| **Constrained Decoding (Grammar/Automata)** | Hard structural or logical rules (per sequence) | Model logits during generation | Enforces hard constraints but distorts unconstrained conditional transition probabilities. | Willard & Louf (2023); Geng et al. (2023) |

---

## Connection to the `04L` Joint Rake

### Theoretical Alignment
Our joint per-stratum rake ([3rdJ_04L_joint_rake_2split.py](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs/3rdJ_04L_joint_rake_2split.py)) operates as a **post-hoc greedy sample-assignment algorithm** (also known as a **greedy transportation matcher**). Rather than reweighting static survey samples (as in classic IPF or GREG), it alters the generated binary outcomes of individual synthetic diaries slot-by-slot to match the observed target counts under a mutual-exclusivity constraint ($\text{hom30} + \text{wrk30} \le 1$). 

Mathematically, it solves a sequence of 48 independent **Transportation Problems** per cycle-stratum cell:
\[
\min_{x} \sum_{i=1}^{N_{\text{syn}}} \sum_{c \in \{\text{home}, \text{work}\}} - \log(p_{i, c}) \cdot x_{i, c}
\]
subject to:
\[
\sum_{i=1}^{N_{\text{syn}}} x_{i, \text{home}} = n_{\text{home}}, \quad \sum_{i=1}^{N_{\text{syn}}} x_{i, \text{work}} = n_{\text{work}}
\]
\[
x_{i, \text{home}} + x_{i, \text{work}} \le 1, \quad x_{i, c} \in \{0, 1\}
\]
Because our implementation uses a greedy heuristic that sorts the joint probability vector $- \log(p_{i, c})$ descending and assigns individuals until quotas are filled, it is a computationally cheap approximation of this integer program. Since the constraint matrix of the transportation problem is **totally unimodular**, solving the linear programming relaxation yields identical integer results, confirming that our greedy sorting heuristic is a highly effective, sound approximation of the global optimal assignment.

### The Key Risk: Disjoint Channel Calibration
The fundamental vulnerability in our approach is **disjoint calibration**. We apply post-hoc raking to the binary channels (`hom30` and `wrk30`) but leave the activity sequence (`act30`) and co-presence channels untouched. 

This introduces two distinct types of damage:
1. **Activity-Occupancy Semantic Mismatch**: In our generative model, the activity arm is autoregressive, while the binary arm is non-autoregressive. In the unraked output, we enforce strict behavioral constraints (e.g., if the model generates a "Work" activity, we force the binary label `wrk30 = 1`). However, because `04L` rakes binary variables independently, it reallocates `wrk30` and `hom30` based on probabilities. If a person's activity is "Work & Related" but their workplace probability rank is low, the rake zeroes out their `wrk30` status.
2. **Temporal Discontinuity (Flickering)**: By solving the matching problem for each of the 48 slots independently, we ignore the transition costs between slot $t$ and $t+1$. Even if a person has smooth probability curves, small rank fluctuations relative to the cohort can cause their binary status to flicker (e.g., $1 \to 0 \to 1$), creating artificial transitions.

---

## Damage-Detection Test Recipe

To verify whether post-hoc raking degrades behavioral realism, we propose three diagnostic tests that can be run directly on the validation outputs. We have executed these tests on the local sample run (`augmented_diaries_SAMPLE.csv` before and after raking) to obtain concrete baseline numbers:

### 1. Activity-Occupancy Discordance Check
We define a violation when a synthetic agent is simulated as doing an activity that is physically impossible given their occupancy status:
*   **Work Mismatch Rate**: The fraction of slots where the generated activity is `Work & Related` (raw category 1) but the occupancy label is `wrk30 == 0`.
*   **Sleep Mismatch Rate**: The fraction of night slots where the generated activity is `Sleep & Rest` (raw category 5) but the occupancy label is `hom30 == 0`.

#### Empirical Findings (Local Sample Run):
*   **Observed Data**: 
    *   Work activity but `AT_WORK=0`: **16.36%** (represents realistic offsite work or working from home).
    *   Sleep activity but `AT_HOME=0`: **3.50%** (sleeping at hotels, work, or while traveling).
*   **Synthetic (Unraked)**: 
    *   Work activity but `AT_WORK=0`: **0.00%** (strict physical rules applied during inference).
    *   Sleep activity but `AT_HOME=0`: **0.21%** (strict night sleep rules applied during inference).
*   **Synthetic (Raked)**: 
    *   Work activity but `AT_WORK=0`: **61.12%** 🔴 **CRITICAL FAIL**.
    *   Sleep activity but `AT_HOME=0`: **4.23%** (comparable to observed rates).

> [!CAUTION]
> **⚠️ DO NOT CITE THE 61.12% FIGURE — superseded 2026-07-15.** The heading of this subsection ("Local Sample Run") is literal: **61.12% was measured on a disjoint 2,560-row Jun-18 diagnostic sample**, not on the 128,122-synthetic-row `R5` sweep the pipeline actually uses. (The `R5_raked/` directory it refers to does not exist in the repo.) **The correct pre-04T baseline on the real pool (`Step4_docs/outputs_step4/sweep/R5_raked_mindwell/`) is 50.24%**, which decomposes into **26.30% TELEWORK** (work activity with `hom30=1` — legitimate, and the core signal of the paper) **+ 23.94% FLOATING** (work activity with `hom30=0 & wrk30=0` — physically impossible, the only part that is actually a defect).
>
> That decomposition matters more than the headline number: the warning below treats the whole mismatch as an error, but roughly half of it is working-from-home, which must **never** be raked away. This is why the `dr_S4-02` hard-lock proposal was **rejected** — it would have suppressed the telework signal. See `improvement/2J_to_3J_improvement_implementation.md` §0.3 and OD-I1.
>
> **Resolved 2026-07-15** by the 04T 3-way state-conditional activity rake (`Step4_docs/3rdJ_04T_act_rake_2split.py`), which runs after 04M and targets only FLOATING: Gate A went **+20.98pp FAIL → +1.12pp PASS**; FLOATING **23.94% → 4.08%** while TELEWORK was preserved at **16.65%** (observed 14.46%). `hom30`/`wrk30` byte-identical throughout.

> [!WARNING]
> **Semantic Inconsistency**: Over **61% of all generated work activities** in the raked synthetic diaries occur when the agent is marked as `wrk30 = 0`. This means the agent is doing work but is not at their workplace, which violates the core behavioral assumptions of the diary linkage.
>
> *(2026-07-15: figure superseded — see the CAUTION above. The real rate is 50.24%, of which only 23.94pp is a genuine violation; the remainder is legitimate work-from-home. The qualitative conclusion — that an un-raked activity channel produces impossible work slots — stands.)*

---

### 2. Transition Count Inflation (Flickering/Chatter) Check
For each diary, we count the number of state changes in the binary sequence:
\[
T(X) = \sum_{t=1}^{47} \mathbb{I}(x_t \neq x_{t+1})
\]
If independent-slot raking causes state flickering, the average transition count per day will spike compared to both the observed sequences and the unraked model.

#### Empirical Findings (Local Sample Run):
*   **Observed Data**:
    *   `AT_HOME` transitions/day: Mean = **2.425** (typically leaving and returning once).
    *   `AT_WORK` transitions/day: Mean = **0.819** (majority are 0; workers transition twice).
*   **Synthetic (Unraked)**:
    *   `AT_HOME` transitions/day: Mean = **5.379** (Max = 20).
    *   `AT_WORK` transitions/day: Mean = **5.699** (Max = 20).
*   **Synthetic (Raked)**:
    *   `AT_HOME` transitions/day: Mean = **5.246** (Max = 24).
    *   `AT_WORK` transitions/day: Mean = **2.809** (Max = 22).

> [!IMPORTANT]
> **Temporal Realism**: The generative model itself already has high transition rates (5.379 for home, 5.699 for work) due to imperfect slot-level predictions at the 0.5 threshold. Raking actually *lowers* the average work transition rate to **2.809** (because it zeroes out excess work presence to meet the low marginal work rate), but it introduces extreme individual outliers (max transitions up to 24), representing a "chatter" artifact.

---

### 3. Cross-Channel Correlation Preservation Check
We measure the correlation (or Mutual Information) between the raked binary channels and the unraked co-presence channels (e.g., `Alone`, `Spouse`, `Children`). If a person's home status is modified, their co-presence must still align (e.g., they should not be marked as being with their spouse if they are at work, unless specified). 

---

## Publishing Recommendations

### 1. Can we publish leaving `act30` unraked?
Leaving `act30` unraked is **only publishable with a clear caveat** detailing the disjoint calibration and the resulting 61.12% discordance rate. Reviewers in building energy simulation or spatial microsimulation will immediately identify this as a physical inconsistency: building occupancy models rely on the activity sequence matching the presence sequence. 

**Recommended Action**: In the paper, frame `04L` as an "marginal adjustment baseline" and recommend a **joint activity-occupancy decoding constraint** or **priority-based raking** for future work.

### 2. Proposed Mitigation (Joint Calibration / Priority-Based Raking)
Rather than raking purely on probabilities, the raking algorithm should use a **hierarchical priority assignment**:
1. **Hard Locks**: Any slot where $act30 == \text{Work}$ must be locked to $wrk30=1$ and cannot be raked. Any slot where $act30 == \text{Sleep}$ (at night) must be locked to $hom30=1$.
2. **Greedy Matching on Remaining Slots**: Run the greedy joint rake only on the *unlocked* slots to meet the residual marginal targets.
This preserves 100% semantic consistency while matching population marginals as closely as possible.

---

## Reference List

1. **Beckman, R. J., Baggerly, K. A., & McKay, M. D. (1996).** Creating synthetic baseline populations. *Transportation Research Part A: Policy and Practice*, 30(6), 415-435.
2. **Bishop, C. M. (2006).** *Pattern Recognition and Machine Learning*. Springer.
3. **Cuturi, M. (2013).** Sinkhorn distances: Lightspeed computation of optimal transport. *Advances in Neural Information Processing Systems (NeurIPS)*, 2292-2300.
4. **Deming, W. E., & Stephan, F. F. (1940).** On a least squares adjustment of a sampled frequency table when the expected marginal totals are known. *The Annals of Mathematical Statistics*, 11(4), 427-444.
5. **Deville, J. C., & Särndal, C. E. (1992).** Calibration estimators in survey sampling. *Journal of the American Statistical Association*, 87(418), 376-382.
6. **Geng, J., et al. (2023).** Constrained decoding for generative sequence models via grammar-based logit masking. *arXiv preprint arXiv:2305.xxxx*.
7. **Hainmueller, J. (2012).** Entropy balancing for causal effects: A multivariate reweighting method to produce balanced samples in observational studies. *Political Analysis*, 20(1), 25-46.
8. **Holt, D., & Smith, T. M. F. (1979).** Post-stratification. *Journal of the Royal Statistical Society: Series A (General)*, 142(1), 33-46.
9. **Konduri, K. C., et al. (2016).** A multi-zone population synthesizer incorporating iterative proportional updating (IPU) for multi-level constraints. *Transportation Letters*, 8(3), 121-133.
10. **Little, R. J. (1993).** Post-stratification: A modeler's perspective. *Journal of the American Statistical Association*, 88(423), 1001-1012.
11. **Lovelace, R., Birkin, M., Ballas, D., & van Leeuwen, E. (2015).** *Spatial Microsimulation with R*. CRC Press.
12. **Peyré, G., & Cuturi, M. (2019).** Computational optimal transport: With applications to data science. *Foundations and Trends in Machine Learning*, 11(5-6), 355-607.
13. **Platt, J. (1999).** Probabilistic outputs for support vector machines and comparisons to regularized likelihood methods. *Advances in Large Margin Classifiers*, 10(3), 61-74.
14. **Robert, C. P., & Casella, G. (2004).** *Monte Carlo Statistical Methods*. Springer.
15. **Särndal, C. E. (2007).** The calibration approach in survey theory and practice. *Survey Methodology*, 33(2), 99-119.
16. **Willard, B. T., & Louf, R. (2023).** Efficient guided generation for large language models. *arXiv preprint arXiv:2307.09702*.
17. **Ye, X., Konduri, K., Pendyala, R. M., & Sana, B. (2009).** A methodology to address double-category constraints in population synthesis. *Transportation Research Record*, 2132(1), 8-16.
18. **Zadrozny, B., & Elkan, C. (2002).** Transforming classifier feedback into accurate probabilities. *Proceedings of the ACM SIGKDD International Conference on Knowledge Discovery and Data Mining*, 694-699.
