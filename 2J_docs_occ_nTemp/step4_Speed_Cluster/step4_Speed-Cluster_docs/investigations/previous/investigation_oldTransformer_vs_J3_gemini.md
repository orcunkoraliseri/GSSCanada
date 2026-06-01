# Investigation Report: Old Transformer Pipeline vs. J3

## Executive Summary
The hypothesis that the "old Transformer pipeline performed strongly on a harder problem" is structurally flawed. The old model and J3 were evaluated on fundamentally different tasks using entirely different metrics. Furthermore, empirical testing confirms that J3's performance plateau on activity classification is primarily caused by **irreducible noise in the training data generation process**, rather than an architectural deficiency in J3 itself. Lastly, while binary tasks like AT_HOME and co-presence seem intuitively easier, they are structurally much more difficult in the J3 pipeline due to the loss of critical demographic data and the compounding errors of autoregressive generation.

---

## 1. The Core Misalignment: Metrics and Framing
The two models were not solving the same problem:
*   **Old Pipeline (Same-Day Classification):** The old model took a diary, looked at its demographics, and predicted labels for *that exact same diary*. It was scored on per-slot classification accuracy.
*   **J3 Pipeline (Cross-Strata Generation):** J3 takes an observed diary and is asked to synthesize what the respondent did on an *unobserved* day (e.g., predicting a Sunday schedule based on a Tuesday observation). It is scored on distributional Jensen-Shannon (JS) divergence.

**Conclusion:** Comparing same-day accuracy to cross-strata JS divergence is invalid. J3 is solving a significantly harder generative task.

---

## 2. The Bottleneck: Irreducible Target Noise (Empirical Finding)
Because J3 is tasked with generating unobserved days, it is trained against $K=5$ demographically similar "neighbor" diaries. 

We ran a diagnostic to compute the natural disagreement between these 5 neighbors. 
*   **Result:** The pairwise JS divergence floor across K=5 neighbors is **`0.1888`**.
*   **Implication:** The target data is inherently chaotic. Even an infinitely capable model cannot achieve zero error because the supervisory targets contradict each other to a degree of `0.1888`. 
*   **J3's Performance:** J3 currently achieves an `act_JS` of `0.0191`. Given the noise floor, J3 is already extracting nearly all the possible signal from this highly noisy supervisory setup. No architectural change inside the J-series is likely to move the needle on this specific gate.

---

## 3. Why AT_HOME and Co-Presence Are Harder in J3
It is a sharp observation that binary classification (predicting 0 or 1 for AT_HOME or Co-presence) *should* intuitively be easier than 14-way activity classification. However, these tasks in J3 are structurally completely different from what the old model faced. Here is exactly why AT_HOME and co-presence have been the major blockers for J-series despite succeeding in the old predictive model:

### A. Co-Presence was Flattened in the Old Model
The old model did not actually predict who you were with. It only predicted a single binary channel called **`withNOBODY`**. 
* **Old Model:** Binary classification: "Is the respondent alone?" (Yes/No).
* **J3 Model:** 9-way multi-label binary classification: "Are they Alone? AND are they with a Spouse? AND Children? AND parents? AND colleagues? etc..."

Predicting "Alone" is closely tied to the activity (e.g., if Activity = Sleep, Alone is highly likely). But predicting the *exact social configuration* (Spouse vs. Children vs. friends) across 9 channels simultaneously requires much deeper sociodemographic context.

### B. J3 Dropped the Key Predictors for AT_HOME and Co-Presence
The old pipeline had an enormous advantage: it fed the model 24 categorical demographic fields. J3 dropped over 9 of them to simplify the pipeline. The dropped fields included:
* **Kinship & Nuclear Family Typology:** These are the *direct* predictors of co-presence. If you don't know the household composition, you are guessing blindly whether someone is with a "Spouse" or "Children".
* **Home Ownership, Room Count, Internet/Car Ownership:** These are strong structural predictors of AT_HOME rates (people with more rooms or who own their home spend measurably more time there). J3 is trying to predict AT_HOME without knowing if the respondent even owns a house or a car.

### C. J3 Lost "Per-Slot" Broadcast Routing
In the old model, the 24 demographic variables (like Age, Sex, Income) were copied and pasted onto *every single 1-hour time slot*. The neural network didn't have to "remember" who the person was while processing 2 PM; the data was right there.

J3 condenses all demographics into a single `CLS` token at the beginning of the sequence. To predict AT_HOME at 2 PM, the attention mechanism has to explicitly route that demographic signal across the sequence to the current time step. This wastes attention capacity on routing rather than temporal patterning.

### D. The Autoregressive "Cascade of Errors"
Because J3 is generating an unobserved day, it uses an Autoregressive (AR) decoder. This means it generates 8:00 AM, and feeds that result in to predict 8:30 AM. 
* If J3 makes a slight mistake on AT_HOME in the morning, that mistake is fed back into the next slot. The model can get "stuck" at home (or away) because the previous slot told it so. 
* The old model predicted every slot in parallel based strictly on the observed truth. It didn't suffer from compounding generative errors.

---

## 4. Additional Structural Regressions in J3
In addition to the demographic and routing differences mentioned above, J3 introduced a training prior that hinders its JS divergence scores:

*   **Artificial Activity Boosts:** J3 applies manual loss multipliers (`Work ×5`, `Transit ×3`, `Social ×2`). The old pipeline used unweighted Cross-Entropy. These boosts force J3 to systematically over-predict these classes, directly fighting the distributional matching required by the `act_JS` metric.

---

## 5. Recommendations for Future Work
When development on Step 4 resumes, the recommended sequence of experiments is:

*   **Experiment 1 (Cheapest): Disable Activity Boosts.** Set `ACTIVITY_BOOSTS=0` to remove the artificial weighting penalty and allow the model to naturally converge on the true population marginals. 
*   **Experiment 2 (Architectural): Per-Slot Broadcast.** Modify `04B_model_J3.py` to concatenate the demographic `cond_vec` onto every slot token before the linear projection, relieving the attention heads from routing duties.
*   **Experiment 3 (Data Pipeline): Restore Demographics.** Audit the `outputs_step2` directory to identify and re-inject the dropped Census fields (Kinship, Ownership, etc.) into the J3 input vector.

---

## 6. Graphical Abstract Prompt
*You can copy and paste the prompt below into Midjourney, DALL-E 3, or another image-generation LLM to create a visual comparison of the two pipelines.*

**Prompt for Image Generation LLM:**
> A high-quality, technical architectural machine learning diagram contrasting two different data pipelines side-by-side. Clean, professional vector graphic style, dark mode with neon blue and orange accents. The layout must clearly show a massive difference in complexity between the left and right sides.
> 
> Left Side (Title: "Predictive Task: Same-Day Classification (Easier)"):
> Visually straightforward and linear. The input is "Observed Day" connected to a massive, thick block labeled "Rich Demographics (24 Fields)" which is directly wired into every single time step of the network. A thick, straight arrow points directly to a box labeled "Predict Observed Day". The outputs are three simple gauges/dials: "Activity (14-class)", "Location (Binary)", and "Alone (Binary)". A floating tag says "Metric: Simple Accuracy". The vibe is a closed, direct 1-to-1 mapping.
> 
> Right Side (Title: "Generative Task: Cross-Strata Synthesis (Harder)"):
> Visually complex, cyclical, and branching. The input is "Observed Day (e.g., Tuesday)" with a much smaller block labeled "Lean Demographics (15 Fields)" attached only at the very beginning (a "CLS" node). A curving, generative, looping arrow points to a box labeled "Synthesize Unobserved Day (e.g., Sunday)". The outputs show an autoregressive loop (arrows feeding back into themselves) for "Activity", which then branches out into 10 parallel, separate binary gauges: "AT_HOME" and "9 Separate Co-Presence Channels (Spouse, Children, Colleagues, etc.)". A floating tag says "Metric: Distributional JS Divergence (Supervised by Noisy Neighbors)". The vibe is open-ended, cascading, and highly complex.
> 
> Include clear, crisp, legible text elements. Ensure the contrast between the "Predictive" straight-line architecture and the "Generative" looping/branching architecture is the focal point of the image.
