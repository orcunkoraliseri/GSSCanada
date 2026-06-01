# **J-4.1, J-4.2, and J-4.3 Training Blueprint: The "Absolute Precision" Legs**

**Objective:** Push AT\_HOME and co-presence accuracy beyond the J3 clearances, targeting absolute precision (approaching 0 pp gaps) by resolving the final theoretical blindspots in the Arm 2 Spatial/Social Evaluator.

While J3 successfully introduced context-awareness via the Soft Activity Embedding and Non-Causal Refinement layer, it still relies on flat parallel predictions. The next three legs iteratively introduce explicit time, state dependencies, and logic constraints.

## **Leg 1: J-4.1 (Explicit Temporal Context Injection)**

**The Hypothesis:** In J3, Arm 2 sees the *sequence* of activities but has no explicit anchor for the *absolute time of day* other than the Trunk's original positional encodings (which get diluted). A "Sleep" activity at 2:00 PM means something different for spatial probabilities than "Sleep" at 2:00 AM.

**The Fix:** Inject explicit Time-of-Day (TOD) and Day-of-Week (DOW) embeddings directly into Arm 2's fused\_seq *before* the Non-Causal Refinement layer.

* **Architecture Update (Arm 2):**  
  * Create self.tod\_emb \= nn.Embedding(48, d\_model)  
  * Create self.dow\_emb \= nn.Embedding(3, d\_model) (for Weekday, Saturday, Sunday)  
  * During the Arm 2 fusion step:  
    fused\_seq \= memory \+ act\_emb \+ cond\_vec\_broadcast \+ self.tod\_emb(slot\_indices) \+ self.dow\_emb(strata)  
  * Pass this temporally anchored fused\_seq into the arm2\_refiner.  
* **Expected Outcome:** Tighter AT\_HOME variance across the specific Weekday vs. Weekend strata, as the model explicitly correlates time-of-day with location.

## **Leg 2: J-4.2 (Hierarchical State Dependency)**

**The Hypothesis:** Currently, AT\_HOME and the 9 co-presence channels are predicted strictly in parallel at the very end of Arm 2\. However, human social states are highly dependent on spatial states (e.g., your probability of being with "colleagues" plummets if AT\_HOME=1).

**The Fix:** Break the parallel head structure into a causal chain: predict AT\_HOME first, then condition the co-presence predictions on that spatial state.

* **Architecture Update (Arm 2):**  
  * Step 1: home\_logits \= self.arm2\_home\_head(refined\_seq)  
  * Step 2: home\_probs\_detached \= torch.sigmoid(home\_logits).detach() (Detaching prevents co-presence BCE from altering the Home head's gradients).  
  * Step 3: cop\_input \= torch.cat(\[refined\_seq, home\_probs\_detached\], dim=-1)  
  * Step 4: cop\_logits \= self.arm2\_cop\_head(cop\_input)  
* **Expected Outcome:** Significant reduction in co-presence errors (especially the Spouse and Alone channels) because the co-presence head dynamically adjusts its probabilities based on whether the model has already decided the person is at home or out.

## **Leg 3: J-4.3 (Differentiable Logic Constraints / PINN)**

**The Hypothesis:** The residual Alone channel asymmetry (especially in 2005/2010 where colleagues is missing) is structural. Instead of fixing it via a post-hoc python script (Step 4.5), we can force the neural network to learn the rules of mutual exclusivity during training by penalizing illogical states.

**The Fix:** Introduce an Auxiliary Logic Loss term inspired by Physics-Informed Neural Networks (PINNs).

* **Training Loop Update (Loss Function):**  
  * Define a differentiable penalty for mutually exclusive states. If Alone is high, all others must be low.  
  * cop\_probs \= torch.sigmoid(cop\_logits)  
  * p\_alone \= cop\_probs\[:, :, 0\] (assuming 0 is Alone)  
  * p\_others \= torch.sum(cop\_probs\[:, :, 1:\], dim=-1) (sum of Spouse, Children, friends, etc.)  
  * loss\_logic \= torch.mean(p\_alone \* p\_others) (This term only grows if the model tries to predict both Alone and Spouse/Friends/etc. at the same time).  
  * Total Loss: Loss \= CE\_act \+ lambda\_home\*BCE\_home \+ lambda\_cop\*BCE\_cop \+ lambda\_logic\*loss\_logic (start with lambda\_logic \= 0.1).  
* **Expected Outcome:** The network will self-correct the Alone channel asymmetry directly in its weights, entirely eliminating the need for post-processing scripts before EnergyPlus integration.

## **Implementation Strategy**

1. **J-4.1 (Temporal Injection):** Run this first. It is an extremely lightweight change to the infer() method and introduces very few new parameters.  
2. **J-4.2 (Hierarchical):** Run this building off the J-4.1 trunk. The .detach() trick is crucial here to keep the gradients isolated, exactly as we did between Arm 1 and Arm 2\.  
3. **J-4.3 (Logic Loss):** This is purely a loss function change. Run this on top of the J-4.2 architecture. If J-4.3 succeeds, you have achieved a mathematically "perfect" generator that requires zero downstream data cleaning.