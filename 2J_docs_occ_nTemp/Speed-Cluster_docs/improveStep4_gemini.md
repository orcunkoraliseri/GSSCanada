# Step 4 Training Improvements based on Cloud Computing Transformer

**Date:** 2026-04-30
**Status:** Proposal based on analysis of the successful `Transformer_pipeline.py` architecture.

This document outlines structural improvements for the Step-4 Conditional Transformer based on a review of the successful cloud computing sequence prediction model (`Transformer_pipeline.py`). The current Step-4 model (`04B_model.py`) struggles with autoregressive feedback (H3), sigmoid saturation, and conditioning collapse (H4). 

The cloud computing model handled a very similar multivariate sequence prediction task (Activity, Location, WithNOBODY) successfully by employing an architecture that fundamentally avoids these issues. Here are the proposed adaptations for Step 4.

## 1. Non-Autoregressive Generation (Solves H3 Exposure Bias)

**Analysis of Cloud Model:**
The cloud computing transformer is an **Encoder-only, non-autoregressive** model. It predicts all 24 time slots in parallel. It does not feed the predicted activity or location of `slot_t` back in as an input to predict `slot_t+1`. Instead, it relies entirely on the self-attention mechanism across the sequence to maintain temporal consistency (Markov properties of human behavior).

**Application to Step 4:**
Step 4 currently uses an autoregressive decoder. As documented in `step4_training_v2.md`, this creates severe exposure bias (H3). The attempted fixes (scheduled sampling `SCHED_SAMPLE_P=0.2` and label smoothing) successfully fixed AT_HOME but catastrophically broke the conditional Spouse co-presence channel (+15.39 pp error) because dropping the AT_HOME signal corrupted the downstream prediction path.

**Proposed Change:**
Convert the Step 4 `CrossAttnDecoder` to a **Non-Autoregressive Decoder (NAT)**.
*   **Remove the causal mask:** Drop `nn.Transformer.generate_square_subsequent_mask`. Allow bidirectional self-attention in the decoder.
*   **Remove token feedback:** Stop feeding `home_tok` and `cop_tok` back into the next step's input.
*   **Parallel prediction:** Feed a sequence of target time-slot embeddings (or just the positional encodings) into the decoder all at once, cross-attending to the observed memory, and predict all 48 slots simultaneously.
*   *Why this works:* It completely eliminates train/inference discrepancy (exposure bias) and removes the need for hacky scheduled sampling that broke the co-presence heads.

## 2. Pre-Linear Bounded Activations (Solves Sigmoid Saturation)

**Analysis of Cloud Model:**
The cloud model features a brilliant structural defense against logit explosion. For binary targets (`location`, `withNOB`), it applies a `Tanh` activation to the transformer hidden state *before* passing it to the final linear projection layer:
`location_output = self.location_dense(self.activation_binary(location_dropout(transformer_out)))` where `activation_binary` is `nn.Tanh()`.

**Application to Step 4:**
Step 4 explicitly suffers from "sigmoid > 0.70 lock-in" on the `home_head` (H3). Currently, `04B_model.py` maps `d_model` directly to logits via `nn.Linear(d_model, 1)`. If the hidden states grow large, the logits explode, and the sigmoid saturates, killing the gradient. F-series attempts to fix this with label smoothing caused side-effects.

**Proposed Change:**
Introduce a bounded activation (`nn.Tanh()`) or a strict `nn.LayerNorm(d_model)` immediately before the `home_head` and `cop_head` linear layers.
*   By bounding the inputs to the final `nn.Linear` layer, the magnitude of the resulting logits is strictly controlled by the linear layer's weights, preventing arbitrary hidden-state scaling from blowing up the logits and saturating the sigmoid.

## 3. Explicit Cyclical Temporal Embeddings

**Analysis of Cloud Model:**
Instead of relying solely on implicit sequence order, the cloud model explicitly computes sine and cosine values for the time of day (`hourStart_Activity`, `hourEnd_Activity`) and concatenates them into the input features for every slot.

**Application to Step 4:**
Step 4 relies purely on standard NLP sinusoidal positional encodings (`sinusoidal_pos_enc`) injected via addition. For time-use data, the actual time of day is a hard semantic feature (e.g., 3:00 AM vs. 5:00 PM), not just a relative sequence position.

**Proposed Change:**
Explicitly inject cyclical time-of-day features into the slot embeddings. 
*   Create a tensor of `[sin(2*pi*t/48), cos(2*pi*t/48)]` for $t \in [0, 47]$. 
*   Concatenate this 2D temporal feature directly into the decoder's input at each slot, alongside the positional encoding. This gives the decoder a strong, anchored signal of exactly what time of day it is currently generating, which is critical for scheduling tasks like sleeping and commuting.

## 4. Learnable Positional Encodings

**Analysis of Cloud Model:**
The cloud model utilizes a `LearnablePositionalEncoding` (`nn.Parameter`) initialized with small random values, rather than fixed deterministic sinusoidal frequencies.

**Application to Step 4:**
Human behavior is highly punctuated at specific times (e.g., exactly at 8:00 AM, 12:00 PM, 5:00 PM) due to societal norms, which doesn't perfectly map to smooth continuous sinusoidal waves.

**Proposed Change:**
Replace the fixed `sinusoidal_pos_enc` in `04B_model.py` with `nn.Parameter(torch.randn(1, 48, d_model) * 0.02)`. Let the model learn the exact embedding for "Slot 14 (7:00 AM)" based on the data, which allows it to capture sharp behavioral transitions that occur at specific hours.

---
### Summary of Recommended Next Steps for G4

If the current G3 (Cross-Attention) trial fails to close the Spouse and AT_HOME gates, the **G4 architecture** should pivot away from autoregression entirely:
1. **G4-NAT:** Implement Non-Autoregressive decoding (Parallel generation, no causal mask, no recurrent feedback).
2. **G4-Tanh:** Add `Tanh()` before `home_head` and `cop_head` to mechanically prevent saturation.
3. **G4-Time:** Replace fixed sinusoids with learnable positional embeddings + explicit cyclical sin/cos features.