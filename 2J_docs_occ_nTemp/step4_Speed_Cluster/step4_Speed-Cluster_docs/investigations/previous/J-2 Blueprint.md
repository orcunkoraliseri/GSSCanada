# **J-2 Architecture & Training Blueprint: The Context-Aware Hybrid**

This document defines the **J2** upgrade for the Step-4 GSS Conditional Transformer.

**The Goal:** Improve the AT\_HOME and co-presence performance of the J1 Hybrid AR-Encoder.

**The Diagnosis:** J1's Arm 2 processed spatial states as isolated per-slot decisions (memory\_t \+ act\_probs\_t ![][image1] home\_t). It lacked the ability to contextualize the *generated activity sequence* (e.g., looking at a previous "Travel" block to inform the current "Socializing" location).

**The Fix:** Upgrade Arm 2 with a Soft Activity Embedding and a lightweight Non-Causal Transformer Refinement layer, creating a true sequence-to-sequence spatial evaluator without breaking J1's gradient isolation.

## **1\. Architectural Upgrades (Focus: Arm 2\)**

The Trunk and Arm 1 (AR Activity Generator) remain perfectly identical to J1. All changes are strictly confined to **Arm 2**.

| J2 Upgrade | Implementation Details | Why it improves AT\_HOME & Co-presence |
| :---- | :---- | :---- |
| **1\. Soft Activity Embedding** | Instead of concatenating the raw 14-dim act\_probs directly to the 384-dim memory, project it first: act\_emb \= act\_probs @ W\_act (where W\_act is a learnable Linear(14, d\_model)). | The raw 14-dim probability vector was likely being "drowned out" by the 384-dim memory vector in J1. Projecting it to d\_model allows the network to learn rich semantic representations of the soft activities before fusion. |
| **2\. Non-Causal Refinement Layer** | Pass the fused Arm 2 sequence \[memory \+ act\_emb \+ cond\_vec\] through a 1-layer or 2-layer nn.TransformerEncoder (d\_model=384, n\_heads=8). | **The critical fix.** This allows Arm 2 to look forward and backward at the *detached* activity sequence. It can now learn rules like: *"If 'Travel' happened at t-1 and 'Social' is at t, AT\_HOME is highly likely 0."* |
| **3\. Deep Tanh Heads** | Replace the flat Linear \-\> Tanh \-\> Linear head with a slightly deeper MLP: Linear(384, 1024\) \-\> GELU \-\> Dropout(0.1) \-\> Linear(1024, K) \-\> Tanh \-\> Sigmoid. | Increases the capacity of the final binary classifiers to model complex non-linear interactions between demographic constraints and sequence contexts. |

## **2\. Updated Implementation Flow (model.infer())**

To the coding agent implementing this in 04B\_model.py under elif \_mtype \== "J2":

1. **Context Phase (Trunk):** memory \= self.encoder(obs\_diary)  
2. **Sequencing Phase (Arm 1 \- Identical to J1):** act\_logits \= self.ar\_act\_decoder.generate(memory, cond\_vec, cycle\_emb, strata\_oh)  
3. **State Resolution Phase (Arm 2 \- UPGRADED):**  
   * *A. Detach & Softmax:* act\_probs \= softmax(act\_logits.detach(), dim=-1)  
   * *B. Soft Embed:* act\_emb \= self.arm2\_act\_proj(act\_probs) *(Linear: 14 \-\> 384\)*  
   * *C. Fuse:* Add/concat memory, act\_emb, and broadcasted condition vectors.  
   * *D. Contextualize:* refined\_arm2\_seq \= self.arm2\_refiner(fused\_seq) *(1-layer TransformerEncoder)*  
   * *E. Classify:* home\_probs, cop\_probs \= self.arm2\_deep\_heads(refined\_arm2\_seq)

## **3\. Training Config Adjustments (configs/J2.yaml)**

Retain the strict "I1 Hygiene" that successfully prevented gradient explosions in the J1 smoke test, with minor tweaks for the added Arm 2 depth.

* **Precision:** fp32 (Strictly enforced, no mixed precision).  
* **Gradient Clipping:** clip\_grad\_norm=25  
* **Learning Rate:** Keep 5e-5 with ReduceLROnPlateau(factor=0.95, patience=5).  
* **Loss Weights:** Keep J1's perfectly balanced weights to avoid confounding variables:  
  * lambda\_home \= 0.7  
  * spouse\_neg\_weight \= 0.45  
  * home\_label\_smooth \= 0.05  
* **Dropout:** Ensure dropout=0.1 is active inside the new arm2\_refiner to prevent the refinement layer from overfitting to the soft activity probabilities.

## **4\. Summary for the Operator**

By introducing the **Soft Activity Embedding** and the **Non-Causal Refinement Layer**, you are giving Arm 2 the "eyes" to see the full context of the day without violating the .detach() barrier that keeps Arm 1 stable. This directly targets the structural limitation that was holding back AT\_HOME and co-presence accuracy in J1.

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABMAAAAXCAYAAADpwXTaAAAAt0lEQVR4XmNgGAWjgDpAQUGBQ05OLk1UVJQHXY4cwCgvL98KNNAYXYIsADIIaGAvkMmCLkcOYAR6twBoaByIjSIDlBAA2iRJClZSUgKaJTcfyJ6soqLCBzZIXFycGyhQDcSzSMVAw3YA6a9A3Aw0kB3FhaQAWVlZE6Ahq6WlpWXQ5UgCQAOEgQYtVlRUlEeXIxkADcoChnMEujjJAJRogYZNlZGRkUaXIwcwqqur84JodIlRMMAAAJV7J+RoCL8jAAAAAElFTkSuQmCC>