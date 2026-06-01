# **J-Series Architecture & Training Blueprint: The Hybrid AR-Encoder**

This document serves as the implementation guide for the **J-Series GSS Conditional Transformer**. It defines a Hybrid AR-Encoder architecture that strictly isolates the temporal activity sequencing (Autoregressive) from the spatial/social state predictions (Non-Autoregressive) to prevent feedback cascading.

All hyperparameters and structural choices have been rigorously derived from the F → G → H → I series data logs to recover the act\_JS floor of G4 while maintaining the AT\_HOME calibration of H\_Tanh.

## **1\. The Updated J-Series Architecture Blueprint**

The architecture is split into a Shared Base (Trunk), Arm 1 (Temporal Generator), and Arm 2 (Spatial/Social Evaluator).

| Target Output | Component / What to Include | Hyperparameters to Enforce | Justification / Context |
| :---- | :---- | :---- | :---- |
| **Shared Base** *(Global Memory)* | **6-Layer nn.TransformerEncoder** Ingests the 48-slot obs\_diary. | • d\_model=384 • d\_ff=1536 • n\_heads=8 • positional\_encoding=sinusoidal | **Capacity Baseline:** G3/G4 only achieved their record act\_JS (0.024/0.030) after this exact capacity bump. The NAT trunk must inherit these dimensions. |
| **1\. act\_seq** *(48 slots, 14-class)* | **G4 CrossAttnDecoder (AR)** Branches from trunk. Loops 48 times. | • lambda\_act=1.0 • sched\_sample\_p=0.0 | **Temporal Anchor:** Generates activities *without* looking at AT\_HOME. G4 proved scheduled sampling breaks co-presence; strictly enforce 0.0. |
| **2\. AT\_HOME** *(48 slots, binary)* | **NAT Per-Slot Fusion** Parallel execution *after* Arm 1 finishes. Fuses Memory \+ act\_seq \+ Cond. | • lambda\_home=0.7 • home\_label\_smooth=0.05 • Head: Tanh \-\> Linear \-\> Sigmoid | **State Evaluator:** Bounding with Tanh and restoring lambda\_home=0.7 prevents the regression seen in I1 and stabilizes the calibration gate (+5.19 pp). |
| **3\. copresence** *(9x48 slots, binary)* | **Parallel NAT Heads** Executes alongside AT\_HOME in Arm 2\. | • lambda\_cop=0.3 • spouse\_neg\_weight=0.45 • Head: Tanh \-\> Linear \-\> Sigmoid | **Social Corrector:** I1's fatal flaw was bumping spouse\_neg\_weight to 1.0. Reverting to 0.45 stops the model from over-predicting the minority class. |

## **2\. Required Training Config Updates (The "I1 Hygiene" Port)**

While the I1 architecture failed, its training loop "hygiene" successfully prevented the grad\_norm=inf explosions that plagued earlier NAT attempts (like H\_NAT). Implement the following in the training script:

1. **Precision:** Enforce strict **fp32**. Do not use fp16 or amp (mixed precision), as the parallel bounded heads are highly susceptible to gradient explosions under fp16.  
2. **Gradient Clipping:** Enforce **clip\_grad\_norm=25** before the optimizer step.  
3. **Learning Rate Scheduler:** Use **ReduceLROnPlateau** initialized with:  
   * lr \= 0.00005 (5e-5)  
   * factor \= 0.95  
   * patience \= 5

## **3\. In Summary (Implementation Notes for Coding Agent)**

**To the coding agent implementing this:**

You are building JSeriesHybrid(nn.Module). Your exact objective is to combine the 384 dimensional capacity and the Autoregressive Cross-Attention activity sequencing of the historical **G4** run, with the Tanh bounded spatial/social heads and lambda\_home=0.7 of the **H\_Tanh** run, executed in a Non-Autoregressive per-slot fusion pass from the **I1** run.

Your forward pass (or infer() method) should look strictly like this:

1. memory \= self.encoder(obs\_diary)  
2. act\_seq \= self.ar\_act\_decoder.generate(memory, cond\_vec, cycle\_emb, strata\_oh)  
3. home\_logits, cop\_logits \= self.nat\_binary\_head(memory, act\_seq, cond\_vec) *(Outputs all 48 slots simultaneously).*

Double-check the loss function weights (spouse\_neg\_weight=0.45, lambda\_home=0.7) to ensure we do not repeat the confounding variable violations of previous runs.