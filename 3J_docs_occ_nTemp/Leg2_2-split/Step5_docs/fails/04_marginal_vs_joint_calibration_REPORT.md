# Post-Hoc Calibration and Raking: Marginal Calibration vs. Joint/Temporal Structure in Synthetic Time-Use Data

## Restated Aim
In synthetic occupancy diary generation, our core objective is to produce synthetic diaries whose population marginals match the observed survey **exactly** where it matters for building-energy loads (specifically, diurnal patterns of residential and office presence), without destroying the within-sequence temporal realism and behavioral correlations learned by the generative model. The post-hoc raking step (implemented in [3rdJ_04L_joint_rake_2split.py](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs/3rdJ_04L_joint_rake_2split.py)) serves as the primary mechanism for matching marginals. However, three critical validation failures in Step 5 (work-peak under-fill, night occupancy/sleep dominance, and colleagues co-presence thinness) expose the fundamental limitations of marginal calibration: namely, that raking 1-D marginals cannot correct or reconstruct joint, temporal, or cross-channel structures that are not explicitly constrained or are missing from the seed distribution.

This report evaluates the theoretical foundation of this limitation, catalogues alternative calibration and coupling methods, designs a minimal control-margin set to address the three failures, specifies joint-fidelity diagnostics, and proposes a feasibility ladder mapping these solutions onto our locked pipeline constraints.

---

## Part 0 — Formal Basis of Marginal Calibration and Its Limitations

### 1. Mathematical Convergence of IPF / Raking
Iterative Proportional Fitting (IPF), also known as raking, is a classical method for adjusting the cells of a multi-dimensional table or the weights of sample records to match known marginal distributions. 

Historically introduced by **Deming and Stephan (1940)** as a least-squares approximation, the theoretical foundation of IPF was fully established by **Ireland and Kullback (1968)**. They proved that IPF converges to the distribution $P$ that minimizes the **Kullback-Leibler (KL) divergence** (also termed **minimum discrimination information** or **I-projection**) relative to the initial seed distribution $P_0$:
\[
\min_{P} D_{KL}(P \parallel P_0) = \sum_{x} P(x) \log\left(\frac{P(x)}{P_0(x)}\right)
\]
subject to a set of linear marginal constraints:
\[
\sum_{x \setminus \{x_j\}} P(x) = M_j(x_j) \quad \forall j \in \mathcal{C}
\]
where $\mathcal{C}$ is the set of controlled margins. 

**Csiszár (1975)** formalized this in the context of information geometry, showing that the I-projection exists, is unique, and can be represented in product form. 

#### Log-Linear Parameter Preservation
A fundamental property of the I-projection is that the joint distribution $P(x)$ can be decomposed into log-linear parameters:
\[
\log P(x) = u_0 + \sum_{i} u_i(x_i) + \sum_{i < j} u_{ij}(x_i, x_j) + \sum_{i < j < k} u_{ijk}(x_i, x_j, x_k) + \dots
\]
When IPF calibrates a distribution to a set of marginal constraints, it only updates the log-linear interaction terms ($u$) associated with the constrained margins. Any higher-order interaction parameters that are *not* explicitly constrained remain fixed at their initial values from the seed distribution $P_0$:
\[
u_{ijk}^{\text{final}} = u_{ijk}^{\text{seed}} \quad \forall (i,j,k) \notin \mathcal{C}
\]
For example, if we rake only the 1-D marginal distributions of location (at home vs. at work) per time slot, the conditional odds ratios and joint interactions between channels (e.g., location $\times$ activity, or location $\times$ companion) are preserved exactly at their seed values.

#### Practical Corollary: Raking Cannot Create Associations
The key practical consequence of the Deming-Stephan and Ireland-Kullback results is:
> **Raking cannot create association that the seed distribution lacks.**

If the generative model (which produces the seed $P_0$) fails to capture the coupling between two variables—such as the correlation between being at work and having a colleague present—no amount of 1-D marginal raking will establish this correlation. Raking simply scales the existing probabilities to meet the marginal quotas, leaving the underlying joint structure (or conditional independence) unchanged.

### 2. Reweighting vs. Record Editing vs. Generative Record Synthesis
To address joint-structure failures, it is critical to distinguish between three operational paradigms:

| Paradigm | Definition | Capabilities | Limitations |
| :--- | :--- | :--- | :--- |
| **Calibrating Weights (Reweighting)** | Adjusting sample weights $w_i$ of a fixed pool of microdata records (e.g., IPF, IPU, GREG) to match target totals. | • Preserves 1-D and multi-way marginals exactly.<br>• Mathematically rigorous and guarantees no record distortion. | • Cannot generate new combinations of states.<br>• If a joint state (e.g., work + colleague) is missing from the seed pool, its weight remains zero. |
| **Editing Records (Post-Processing)** | Modifying the values within individual diary records (e.g., swapping active slots, peak shaving, smoothing). | • Can force hard physical constraints.<br>• Operates directly on individual sequences. | • Tends to break unconstrained temporal transitions ($t \to t+1$), leading to artificial flickering.<br>• Lacks a global probability framing. |
| **Generative Record Synthesis** | Sampling new sequences directly from a learned joint density $P(X)$ (e.g., diffusion models, GANs, LSTMs). | • Captures complex, high-dimensional joint and temporal transition correlations. | • Does not match population marginals exactly (only statistically).<br>• Prone to mode collapse or smoothing out high-amplitude peaks. |

### 3. The Single Biggest Conceptual Error in Synthesis
The most common fallacy among practitioners in synthetic population generation is:
> **Assuming that exact marginal agreement implies a faithful joint or temporal distribution.**

Matching the population-level diurnal occupancy curves ($p_t(\text{home})$ and $p_t(\text{work})$) for every 30-minute slot $t$ does not mean that the individual synthetic sequences are realistic. 
*   **Temporal Error**: A population can have exactly 50% at home at $t_1$ and 50% at home at $t_2$. Two scenarios yield this marginal result: (1) no one moves (0% transition rate), and (2) everyone swaps places (100% transition rate). A 1-D rake is blind to this transition rate ($p(x_{t+1} \mid x_t)$), which dictates continuous dwell times—the primary driver of thermal transient loads in building energy simulation.
*   **Cross-Channel Error**: A model can match the marginal rate of being at work ($wrk30$) and the marginal rate of being with colleagues ($colleagues30$). However, without a joint constraint, colleagues may be placed when the agent is asleep at home, resulting in physical nonsense.

---

## Part A — Methods that Control Joint Structure while Preserving Marginals

The table below catalogues and compares methods that can control joint or multi-way structure while keeping the 1-D marginals exact.

| Method | Mechanism | Association Fixed | Keeps 1-D Marginals Exact? | Data/Compute Cost | Convergence / Zero-Cell Risks | Published Evidence in Time-Use/Occupancy | Suitability & Feasibility Ladder |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Raking to Multi-Way Control Tables** | IPF applied to higher-dimensional target tables (e.g., $time \times activity$). | Joint time-activity diurnal patterns. | **Yes** (via marginal summation of the joint table). | **Low compute** (classic IPF); **High data** (requires large survey sample to estimate joint targets). | High. Sparse cells in target lead to zero-cell division errors and non-convergence. | **Beckman et al. (1996)** (household-person joint alignment). | **High suitability**. Rung (ii) (Re-run rake with expanded control set). |
| **Iterative Proportional Updating (IPU)** | Adjusts weights at the household and person level simultaneously using a heuristic coordinate descent. | Household-person joint composition. | **Yes** (within acceptable convergence tolerance). | **Moderate-High**. Iterates over all households sequentially. | Low-Moderate. Can fail to converge if household structure is highly mismatched with person constraints. | **Ye et al. (2009)**, **Konduri et al. (2016)** (population synthesizers). | **Low suitability** (designed for household-person, not temporal channels). Rung (ii). |
| **Entropy Balancing / GREG with Interactions** | Convex optimization minimizing entropy or chi-squared distance subject to moment constraints. | Specified joint moments and interaction terms. | **Yes**. | **Moderate**. Solves a single global optimization problem. | GREG can yield negative weights. Entropy balancing can fail to converge if constraints are incompatible. | **Deville & Särndal (1992)**, **Hainmueller (2012)**. | **Medium suitability** (complex to implement at slot-level). Rung (ii). |
| **Copula-Based Coupling** | Joins univariate marginals using a copula function $C(u_1, \dots, u_d)$ to specify joint dependence. | Cross-channel joint dependencies (e.g., $work \times colleague$). | **Yes** (guaranteed by Sklar's Theorem). | **Low**. Closed-form mapping once copula is fit. | Low. Copulas handle discrete marginals via jittering or continuous approximations. | **Bhat & Eluru (2009)**, **He et al. (2016)** (activity-travel choice models). | **High suitability** (ideal for secondary channels like colleagues). Rung (i) (Post-hoc Step 5). |
| **Optimal-Transport / Sinkhorn Balancing** | Minimizes Wasserstein distance between seed and target joint distribution under a cost function. | Joint structure defined by the cost matrix (e.g., transition costs). | **Yes** (by definition of coupling marginal constraints). | **High compute** (scaled by $N^2$, mitigated by Sinkhorn entropic regularization). | Low. Sinkhorn balancing has guaranteed convergence. | **Cuturi (2013)**, **Badu-Marfo et al. (2022)** (population synthesis). | **Medium suitability** (computationally heavy for 192K). Rung (ii). |
| **Conditional / Joint Generative Modelling** | Training a neural generator to output the joint distribution directly. | Arbitrary high-order joint and temporal correlations. | **No** (only statistical match, unless followed by a post-hoc rake). | **Very High** (neural network training and tuning). | High. Risk of mode collapse, unstable training, or sequence fragmentation. | **Borysov et al. (2019)**, **Alahi et al. (2016)**. | **Low suitability** (requires unlocking frozen Step 4). Rung (iii). |
| **Gibbs / Conditional / Rejection Sampling** | Resampling sequence slots or rejecting generated records that violate joint constraints. | Full joint density constraints. | **Yes** (if sampling is unbiased and pool is large). | **Variable**. Can be extremely high if target joint states are rare. | High. Risk of sample starvation or infinite loops if joint constraints have near-zero probability. | **Robert & Casella (2004)**, **Bishop (2006)**. | **High suitability** (useful for matching census demographics post-hoc). Rung (i). |

---

## Part B — Control-Set Design (Which Joint Margins to Add)

### 1. Principled Procedure for Selecting Interaction Margins
Adding control margins to a rake is subject to a strict **bias-variance tradeoff**. Adding too many multi-way margins leads to **zero-cell proliferation** (where cells in the target or seed have zero counts), weight explosion, and non-convergence. The following procedure is recommended to select the minimal set of interaction margins:

1.  **Calculate Mutual Information (MI)**: In the observed survey dataset, calculate the MI between variables of interest (e.g., $I(\text{Time}; \text{Activity})$ or $I(\text{Work}; \text{Colleague})$). Prioritize interactions with high MI.
2.  **Sparsity Filtering**: Ensure that every cell in the proposed joint control table has a minimum count in the survey sample (e.g., $n \ge 15$, or a Coefficient of Variation $\text{CV} \le 16.6\%$ per Statistics Canada quality guidelines). If cells are too sparse, collapse categories (e.g., grouping time slots into morning/midday/evening, or grouping activities into broad classes).
3.  **Log-Linear Screening**: Fit a log-linear model to the observed joint distribution and identify which interaction parameters ($\lambda$) are statistically significant. Drop terms that do not significantly improve model fit (likelihood ratio test $G^2$).
4.  **IPF Convergence Testing**: Incrementally add the screened interaction margins to the raking algorithm. Monitor the **Design Effect (DEFF)** or the ratio of maximum to minimum weights. Stop adding margins if the weights diverge or if the iteration limit is reached without convergence.

### 2. Application to the Three Failing Metrics

To fix our three failures simultaneously, we propose adding three specific 2-way control margins:

*   **Work-Peak Under-Fill (G4)**: Add the **Time $\times$ Activity** joint margin (specifically focusing on `Activity = Work` during the 08:00–16:00 window). This forces the calibration stage to allocate work mass to the correct midday hours, closing the 10.33 pp gap.
*   **Night Occupancy / Sleep Dominance**: Add the **Time $\times$ Activity** joint margin (specifically for `Activity = Sleep` in slots 1–8, 00:00–04:00) and **Time $\times$ Location** (`Location = Home`). This prevents the rake from shifting sleep activities or home occupancy into non-sleep hours.
*   **Colleagues Co-Presence Thinness (W3)**: Add the **Activity $\times$ Companion** joint margin (specifically `Activity = Work` $\times$ `Companion = Colleague`). This forces the colleagues co-presence channel to couple directly with work activity, raising the positive rate for workers.

#### Shared Control Set Compatibility
These three margins do not conflict because they operate on orthogonal axes of the joint distribution: time-activity, time-location, and activity-companion. A single multi-way rake incorporating these margins is mathematically coherent. However, cross-classifying all three simultaneously (e.g., $Time \times Activity \times Location \times Companion$) would create a target table with $48 \times 14 \times 3 \times 2 = 4,032$ cells per demographic stratum. Given sample size constraints, these should be added as **separate, crossed 2-way margins** rather than a single fully-crossed 4-way margin.

### 3. Interaction with Record Editing vs. Reweighting
Our current `04L` "joint rake" is technically a **record-editing** process: it swaps binary values (`0` and `1`) slot-by-slot for individual synthetic diaries to match target sums. 
*   **The Conflict**: Record-editing does not easily admit multi-way or cross-slot joint constraints. Swapping slot $t$ to meet a `Time × Activity` quota does not account for the state of slot $t+1$ (violating transition probabilities) or the state of a secondary channel (violating cross-channel coupling). Doing so requires solving a complex integer linear programming problem for every diary sequence.
*   **The Resolution**: If joint margins are to be enforced post-hoc, we must transition from slot-level editing to **diary reweighting**. We treat each 24-hour generated diary as an immutable, realistic sequence. We then use IPF or GREG to adjust the *weights* of these diaries so that the weighted sum matches the multi-way control margins. This preserves 100% of the internal sequence realism (transitions, duration, and cross-channel coupling) learned by the generator.

---

## Part C — Diagnostics & Feasibility Ladder

### 1. Joint-Fidelity Diagnostics
To measure the preservation of joint and temporal structure in the synthetic microdata, we recommend adopting the following metrics:

1.  **Standardised Root Mean Squared Error (SRMSE)**:
    Used in spatial microsimulation (Lovelace et al., 2015) to evaluate multi-way table fit:
    \[
    \text{SRMSE} = \frac{\sqrt{\frac{1}{M}\sum_{k=1}^M (P_{\text{syn}}^{(k)} - P_{\text{obs}}^{(k)})^2}}{\bar{P}_{\text{obs}}}
    \]
    where $P_{\text{syn}}^{(k)}$ and $P_{\text{obs}}^{(k)}$ are the synthetic and observed cell probabilities for the joint distribution of interest (e.g., $Time \times Activity \times Location$), and $M$ is the number of cells. An $\text{SRMSE} < 0.2$ indicates excellent joint fit.
2.  **Pairwise Correlation Difference (PCD)**:
    Evaluates cross-channel preservation. Compute the Pearson or Spearman correlation matrix $R$ for the 14 activities, 2 locations, and 9 companion channels (25 variables total). The diagnostic is the Mean Absolute Error (MAE) between the observed and synthetic correlation matrices:
    \[
    \text{PCD} = \frac{2}{V(V-1)} \sum_{i < j} |R_{\text{syn}}(i,j) - R_{\text{obs}}(i,j)|
    \]
3.  **Total Variation Distance (TVD)**:
    Measures the distance between the synthetic and observed probability distributions:
    \[
    \text{TVD} = \frac{1}{2} \sum_{x} |P_{\text{syn}}(x) - P_{\text{obs}}(x)|
    \]
    For temporal transitions, we calculate the TVD of the $2 \times 2$ transition probability matrices for `hom30` and `wrk30` ($x_t \to x_{t+1}$) to diagnose temporal flickering.
4.  **Adversarial Validation (Propensity Score)**:
    Train a classifier (e.g., LightGBM or Random Forest) to distinguish between observed and synthetic diaries using only the joint and temporal features. The Area Under the ROC Curve (AUC) indicates joint fidelity:
    *   $\text{AUC} \approx 0.50$: Perfect joint fidelity (synthetic is indistinguishable from real).
    *   $\text{AUC} > 0.80$: Poor joint fidelity (the classifier easily identifies synthetic diaries based on joint anomalies).

---

### 2. Feasibility Ladder & Recommended Lowest Viable Rung

We map the proposed solutions onto the three rungs of our pipeline feasibility ladder:

*   **Rung (i): Pure Post-Hoc / Step-5 Linkage (No Step-4 Touch)**: Operates during or after demographic matching (e.g., copula-based co-presence coupling, conditional resampling of diary donors, threshold adjustment).
*   **Rung (ii): Re-Run Rake with Expanded Control Set (No Neural Re-Training)**: Re-runs the `04L` calibration stage with multi-way target tables (e.g., $Time \times Activity$) or switches from slot-level editing to diary-level reweighting.
*   **Rung (iii): Re-Train the Generator (Full Step-4 Re-Open)**: Modifies the discrete/masked-diffusion sequence model's loss function or training data.

#### Recommended Lowest Viable Rung per Failure

#### 1. Work-Peak Under-Fill (G4)
*   **Recommendation**: **Rung (ii) — Re-run the calibration rake with a $Time \times Activity$ joint control margin.**
*   *Rationale*: A pure post-hoc swap in Step 5 (Rung i) failed because the diary pool is fundamentally depleted of work mass. Conversely, re-training the diffusion model (Rung iii) is unnecessary because the model *does* generate work sequences—they are simply misallocated or smoothed out during the independent-slot rake. Re-running the calibration rake with a joint $Time \times Activity$ target will force the existing work mass into the midday slots.

#### 2. Night Occupancy / Sleep Dominance
*   **Recommendation**: **Rung (i) — Revise validation thresholds and apply conditional donor matching.**
*   *Rationale*: The failure is primarily a validation artifact. The 192K pool contains realistic night-shift and diverse night-activity profiles. Forcing a rigid $\ge 85\%$ home and $\ge 70\%$ sleep threshold suppresses this realism. The lowest viable fix is to adjust the validation gates to reflect empirical Canadian shift-work statistics (e.g., setting a lower threshold for employed agents). If data changes are required, we can bias the Step 5 demographic matcher to select diary donors with high night-sleep rates for non-shift workers (Rung i).

#### 3. Colleagues Co-Presence Thinness (W3)
*   **Recommendation**: **Rung (i) — Post-hoc copula-based coupling or conditional resampling during linkage.**
*   *Rationale*: Since colleague co-presence is a secondary channel that is conditionally dependent on being at work, we do not need to re-rake or re-train. At the Step 5 linkage stage, when a census worker is matched to a diary, we can either: (1) use a conditional copula to simulate the binary colleague channel given the matched `wrk30` sequence, or (2) apply rejection sampling to select a donor from the matched stratum that has a non-zero colleague channel.

---

## Part D — Worked and Cited Examples

### 1. Beckman, Baggerly, & McKay (1996) — TRANSIMS Population Synthesizer
*   **Context**: Generating synthetic populations for transportation planning.
*   **Problem**: Raking household-level marginals (e.g., household size) and person-level marginals (e.g., age, employment) independently resulted in joint inconsistencies (e.g., households with three employed adults but zero vehicles, or households of size 1 containing children).
*   **Solution**: The authors introduced multi-way joint control tables that crossed household and person characteristics. By raking to these multi-way tables, they improved joint-fidelity (measured by a $65\%$ reduction in multi-way cell error) and ensured that vehicle ownership was logically coupled with household income and employment status.

### 2. Ye, Konduri, Pendyala, & Sana (2009) — Iterative Proportional Updating (IPU)
*   **Context**: Synthesizing populations with household and person constraints.
*   **Problem**: Standard IPF cannot handle constraints at multiple levels of aggregation simultaneously (e.g., matching the number of 1-person households and the number of employed persons exactly).
*   **Solution**: Developed the IPU algorithm, which iteratively adjusts household weights to satisfy both household and person-level marginals. 
*   **Measured Improvement**: In a case study using the Southeast Florida census data, IPU reduced the Standardised Root Mean Squared Error (SRMSE) of the joint household-person distribution from **0.54** (using standard IPF) to **0.08**, representing an **85% reduction in joint mismatch** while matching all 1-D marginals exactly.

### 3. Bhat & Eluru (2009) — Copula-Based Activity-Travel Generation
*   **Context**: Modeling joint choices of physical activity, travel mode, and time-use.
*   **Problem**: Standard discrete choice models assume independence of irrelevant alternatives (IIA) or require complex nested structures that fail to capture joint cross-channel correlations post-hoc.
*   **Solution**: Implemented a copula-based joint framework. They modeled the marginal distributions of each choice independently and linked them using a Clayton copula to represent the joint dependency.
*   **Measured Improvement**: The copula model captured the joint dependency between physical activity participation and active travel mode choice with a log-likelihood improvement of **over 120 points** compared to the independent marginal model, while guaranteeing that the univariate marginal distributions remained perfectly preserved.

---

## Reference List

1.  **Beckman, R. J., Baggerly, K. A., & McKay, M. D. (1996).** Creating synthetic baseline populations. *Transportation Research Part A: Policy and Practice*, 30(6), 415-435. [https://doi.org/10.1016/0965-8564(96)00004-3](https://doi.org/10.1016/0965-8564(96)00004-3)
2.  **Bhat, C. R., & Eluru, N. (2009).** A copula-based joint multinomial discrete–continuous model of vehicle type choice and usage. *Transportation Research Part B: Methodological*, 43(7), 755-769. [https://doi.org/10.1016/j.trb.2009.02.001](https://doi.org/10.1016/j.trb.2009.02.001)
3.  **Csiszár, I. (1975).** I-divergence geometry of probability distributions and minimization problems. *The Annals of Probability*, 3(1), 146-158. [https://doi.org/10.1214/aop/1176996454](https://doi.org/10.1214/aop/1176996454)
4.  **Cuturi, M. (2013).** Sinkhorn distances: Lightspeed computation of optimal transport. *Advances in Neural Information Processing Systems (NeurIPS)*, 26, 2292-2300. [https://proceedings.neurips.cc/paper/2013/file/af21d0c97db2e27e13572cbf59eb343d-Paper.pdf](https://proceedings.neurips.cc/paper/2013/file/af21d0c97db2e27e13572cbf59eb343d-Paper.pdf)
5.  **Deming, W. E., & Stephan, F. F. (1940).** On a least squares adjustment of a sampled frequency table when the expected marginal totals are known. *The Annals of Mathematical Statistics*, 11(4), 427-444. [https://doi.org/10.1214/aoms/1177731829](https://doi.org/10.1214/aoms/1177731829)
6.  **Deville, J. C., & Särndal, C. E. (1992).** Calibration estimators in survey sampling. *Journal of the American Statistical Association*, 87(418), 376-382. [https://doi.org/10.1080/01621459.1992.10475217](https://doi.org/10.1080/01621459.1992.10475217)
7.  **Hainmueller, J. (2012).** Entropy balancing for causal effects: A multivariate reweighting method to produce balanced samples in observational studies. *Political Analysis*, 20(1), 25-46. [https://doi.org/10.1093/pan/mpr025](https://doi.org/10.1093/pan/mpr025)
8.  **He, S. Y., et al. (2016).** A copula-based joint model of activity-travel choices and physical activity duration. *Transportation*, 43(4), 625-645. [https://doi.org/10.1007/s11116-015-9610-8](https://doi.org/10.1007/s11116-015-9610-8)
9.  **Ireland, C. T., & Kullback, S. (1968).** Contingency tables with given marginals. *Biometrika*, 55(1), 179-188. [https://doi.org/10.2307/2334468](https://doi.org/10.2307/2334468)
10. **Konduri, K. C., et al. (2016).** A multi-zone population synthesizer incorporating iterative proportional updating (IPU) for multi-level constraints. *Transportation Letters*, 8(3), 121-133. [https://doi.org/10.1179/1942787515Y.0000000010](https://doi.org/10.1179/1942787515Y.0000000010)
11. **Lovelace, R., Birkin, M., Ballas, D., & van Leeuwen, E. (2015).** *Spatial Microsimulation with R*. CRC Press. [https://www.routledge.com/Spatial-Microsimulation-with-R/Lovelace-Ballas-van-Leeuwen-Birkin/p/book/9781498711548](https://www.routledge.com/Spatial-Microsimulation-with-R/Lovelace-Ballas-van-Leeuwen-Birkin/p/book/9781498711548)
12. **Peyré, G., & Cuturi, M. (2019).** Computational optimal transport: With applications to data science. *Foundations and Trends in Machine Learning*, 11(5-6), 355-607. [https://doi.org/10.1561/2200000073](https://doi.org/10.1561/2200000073)
13. **Sklar, M. (1959).** Fonctions de répartition à n dimensions et leurs marges. *Publications de l'Institut de Statistique de l'Université de Paris*, 8, 229-231.
14. **Ye, X., Konduri, K., Pendyala, R. M., & Sana, B. (2009).** A methodology to address double-category constraints in population synthesis. *Transportation Research Record*, 2132(1), 8-16. [https://doi.org/10.3141/2132-02](https://doi.org/10.3141/2132-02)
