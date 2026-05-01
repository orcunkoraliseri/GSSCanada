# Step-4 G3 — Implementation Spec (cross-attention + decoder capacity)

> Manager-tier deliverable for builder (Sonnet) to implement on `04B_model.py`. Pairs with `step4_training_v2.md` (G3 task row, lines 47–55) and the Bundle-Submission Protocol (lines 56–64). No execution commands in this doc — just code-shape, config-shape, and verification checks.

---

## Aim

Replace FiLM conditioning with a **cross-attention path** over the same `dec_cond = [cond_vec ‖ cycle_emb ‖ strata_oh]` tensor that FiLM currently consumes, and lift decoder capacity (`d_model` 256 → 384, `d_ff` 1024 → 1536). Targets H4 (decoder ignores conditioning) plus the F10a-cited capacity ceiling. G1 (proportional pairs in `outputs_step4_G1/`) and G2 (`SCHED_SAMPLE_P=0.2`, `HOME_LABEL_SMOOTH=0.05`) are carried forward unchanged.

---

## Diff scope (the hard rule)

**Edit only:**
- `2J_docs_occ_nTemp/04B_model.py` — decoder rewrite + capacity bump.
- `2J_docs_occ_nTemp/configs/G3.yaml` — new file (G2 base + arch params).
- `2J_docs_occ_nTemp/configs/sweep_G23.yaml` — new combined driver `tags: [G2, G3]`.
- `2J_docs_occ_nTemp/configs/sweep_smoke_G23.yaml` — new combined smoke driver.
- `2J_docs_occ_nTemp/Speed_Cluster/config_to_env.sh` and `config_to_env.py` — only if `D_MODEL` / `D_FF` are not already plumbed (check first; G2 already added `SCHED_SAMPLE_P` / `HOME_LABEL_SMOOTH`, so the pattern is in place).

**Do NOT touch:**
- `04C_training_pairs.py` (G1 territory).
- `04D_train.py` training loop, loss fn, env-var defaults (G2 territory).
- `04E_inference.py`, `04F`, `04H`, `04I`, `04J`, `extract_metrics.py`.
- `submit_step4_array.sh`, `job_04D_train_array.sh` — no infra changes; the G2 smoke fixes (yq-independent `data_dir` extraction) already cover G3.

If a G3 change starts requiring an edit outside this list, **stop and re-plan** — bundle-submission only holds because G2 (`04D_train.py`) and G3 (`04B_model.py`) edit disjoint files (see `step4_training_v2.md` line 64).

---

## Architecture change

### Current (FiLM, to be replaced)

`04B_model.py:98` — `FiLMTransformerDecoder`:

```
forward(x, memory, tgt_mask, dec_cond):
    for layer, film in zip(layers, films):
        x = layer(x, memory, tgt_mask)        # standard self-attn → cross-attn(memory) → FFN
        x = film(x, dec_cond)                  # γ⊙x + β, γ/β from Linear(d_cond_dec, 2*d_model)
```

`FiLMLayer` (line 79) generates per-layer γ/β from `dec_cond`. `dec_cond` itself is built at `_build_dec_cond` (line 283):

```
dec_cond = cat([cond_vec, cycle_emb, strata_oh], dim=-1)   # (B, d_cond_dec)
```

There is also an additive `strata_linear` projection (line 178, 318) that broadcasts a `(B, 1, d_model)` strata embedding onto the decoder input — a redundant conditioning path. **Remove** it under G3.

### Replacement (cross-attention conditioning)

The decoder layer becomes a **two-cross-attn** block: the first cross-attn over the encoder memory (unchanged), the second cross-attn over a projected `dec_cond` token sequence. Order per layer:

1. Self-attention (causal, over decoder hidden states) — unchanged.
2. Cross-attention #1: query = decoder hidden, key/value = encoder memory `(B, 49, d_model)` — unchanged.
3. **NEW** Cross-attention #2: query = decoder hidden, key/value = projected `dec_cond` tokens — replaces FiLM γ/β.
4. FFN — unchanged.

**`dec_cond` projection.** `dec_cond` is currently a single `(B, d_cond_dec)` vector. For cross-attn we need a sequence. Two acceptable options — pick (b) for first pass:

- (a) Treat `dec_cond` as one token: project to `(B, 1, d_model)` via a `Linear(d_cond_dec, d_model)`. Cheap, minimal capacity bump on the conditioning side.
- (b) **Recommended.** Project the three semantic blocks separately into three tokens — one per block — then stack:
  - `tok_demo  = Linear(d_cond, d_model)(cond_vec)`               → `(B, d_model)`
  - `tok_cycle = Linear(d_cycle, d_model)(cycle_emb)`             → `(B, d_model)`
  - `tok_strata = Linear(3, d_model)(strata_oh)`                   → `(B, d_model)`
  - `cond_tokens = stack([tok_demo, tok_cycle, tok_strata], dim=1)` → `(B, 3, d_model)`

  Cross-attn over 3 tokens lets the decoder weight demographics vs. cycle vs. strata per slot per head — the structural reason H4 is the suspected blocker.

**Recommended layer module shape (PyTorch):**

```python
class CondCrossAttnDecoderLayer(nn.Module):
    def __init__(self, d_model, n_heads, d_ff, dropout=0.0):
        super().__init__()
        self.self_attn  = nn.MultiheadAttention(d_model, n_heads, dropout=dropout, batch_first=True)
        self.cross_mem  = nn.MultiheadAttention(d_model, n_heads, dropout=dropout, batch_first=True)
        self.cross_cond = nn.MultiheadAttention(d_model, n_heads, dropout=dropout, batch_first=True)
        self.ffn = nn.Sequential(nn.Linear(d_model, d_ff), nn.GELU(), nn.Linear(d_ff, d_model))
        self.ln1, self.ln2, self.ln3, self.ln4 = (nn.LayerNorm(d_model) for _ in range(4))
        self.drop = nn.Dropout(dropout)

    def forward(self, x, memory, cond_tokens, tgt_mask):
        x = x + self.drop(self.self_attn(self.ln1(x), self.ln1(x), self.ln1(x), attn_mask=tgt_mask, need_weights=False)[0])
        x = x + self.drop(self.cross_mem(self.ln2(x), memory, memory, need_weights=False)[0])
        x = x + self.drop(self.cross_cond(self.ln3(x), cond_tokens, cond_tokens, need_weights=False)[0])
        x = x + self.drop(self.ffn(self.ln4(x)))
        return x
```

Pre-LayerNorm pattern (LN-before-residual) — matches the F-series convention. Use `batch_first=True` to stay consistent with the rest of the model.

**Top-level decoder:**

```python
class CrossAttnDecoder(nn.Module):
    def __init__(self, d_model, n_heads, n_layers, d_ff, d_cond, d_cycle):
        super().__init__()
        self.proj_demo   = nn.Linear(d_cond,  d_model)
        self.proj_cycle  = nn.Linear(d_cycle, d_model)
        self.proj_strata = nn.Linear(3,       d_model)
        self.layers = nn.ModuleList([
            CondCrossAttnDecoderLayer(d_model, n_heads, d_ff) for _ in range(n_layers)
        ])
        self.norm = nn.LayerNorm(d_model)

    def forward(self, x, memory, cond_vec, cycle_emb, strata_oh, tgt_mask):
        cond_tokens = torch.stack([
            self.proj_demo(cond_vec),
            self.proj_cycle(cycle_emb),
            self.proj_strata(strata_oh),
        ], dim=1)                                    # (B, 3, d_model)
        for layer in self.layers:
            x = layer(x, memory, cond_tokens, tgt_mask)
        return self.norm(x)
```

The `aux_strata_head` (line 224) is **kept** — it operates on `layer0_hidden` and serves a different purpose (auxiliary stratum classification, F8-validated). Its tap point shifts from "FiLM-decorated layer 0 output" to "first cross-attn-decoder layer output"; the contract (a `(B, T, d_model)` tensor) is preserved.

### What gets deleted

- `FiLMLayer` class (line 79–96).
- `FiLMTransformerDecoder` class (line 98–127, exact range to be confirmed at edit time).
- `self.films` list, `self.strata_linear` (line 178), and the `dec_input + strata_emb` addition at line 318–319.
- The `decoder_layer = nn.TransformerDecoderLayer(...)` factory at line 205 (replaced by the new layer class).

The `_build_dec_cond` helper (line 283) **stays** but its output shape is reinterpreted: it still returns `(cond_vec, cycle_emb, strata_oh)` — refactor it to return the three tensors directly (drop the `cat`) since the new decoder consumes them separately.

---

## Capacity expansion

| Param      | F10a / G1 / G2 | G3   | Smoke (G3_smoke) |
|------------|----------------|------|------------------|
| `d_model`  | 256            | 384  | 64               |
| `d_ff`     | 1024           | 1536 | 256              |
| `n_heads`  | 8              | 8    | 4                |
| `n_enc_layers` | 6          | 6    | 2                |
| `n_dec_layers` | 6          | 6    | 2                |

Decoder param count rough estimate: each layer is ~`4·d_model²` (attn) + `2·d_model·d_ff` (FFN). At 256/1024 → ~786 K + 524 K = 1.3 M per layer; at 384/1536 → ~1.77 M + 1.18 M = 2.95 M per layer. Plus the new third cross-attn (`~4·d_model² ≈ 0.59 M`) and the three projection heads (`d_cond·d_model + d_cycle·d_model + 3·d_model ≈ 30 K + ~0.012 K · d_model`). Net: ~**2.4× decoder param count** vs. G2.

### Memory-fit verification (smoke does this)

Before spending a `pg` slot, the G3 smoke (`d_model=64, d_ff=256, batch=8`) must complete one epoch end-to-end. Assuming smoke is green, run a **single-batch dry-run on the full-size `d_model=384` config** before submitting full training: builder should add a tiny `--mem-probe` mode that runs one forward + backward at full size, prints peak GPU memory, and exits. If peak memory exceeds the `pg`-partition single-GPU budget (Speed `pg` is 32 GB; comfortable target ≤ 24 GB at `batch_size=256`), fall back in this order:

1. **Halve `d_ff`:** 1536 → 1280, then → 1024 (back to G2). FFN is the largest single contributor.
2. **Lower `d_model`:** 384 → 320. Affects all three attention blocks.
3. **Halve batch size:** 256 → 128 (last resort — slower convergence).
4. **DDP escalation:** only if (1)–(3) all fail. F-series stayed single-GPU; DDP is new infrastructure risk.

The first config that fits is the G3 config. Document the fallback in the Progress Log so the row's `composite` is interpretable.

---

## `configs/G3.yaml` schema

```yaml
# G3.yaml — G-series stage 3: Cross-attention conditioning + decoder capacity
# Inherits G2 (sched-sample + label-smooth) and G1 (proportional pairs) by reusing data_dir.
# Hard gates (unchanged): composite < 1.045 | AT_HOME <= +5.3 pp | Spouse <= +5 pp | act_JS <= 0.05
tag: G3
seed: 42

# Argparse flags (G2 base)
data_dir: outputs_step4_G1            # G1 pairs, carried forward
batch_size: 256
max_epochs: 100
patience: 15
lr: 5.0e-5
d_model: 384                          # ← G3 capacity bump (was 256)
n_heads: 8
n_enc_layers: 6
n_dec_layers: 6

# Architecture knobs (NEW — only used by G3 decoder)
d_ff: 1536                            # ← G3 capacity bump (was 1024)

# Loss weights (unchanged from F10a)
lambda_act: 1.0
lambda_home: 0.5
lambda_cop: 0.3
lambda_marg: 0.1
marg_mode: global

# Feature switches (F10a base)
aux_stratum_head: 1
aux_stratum_lambda: 0.1
spouse_neg_weight: 0.45
cop_pos_weight: 0
activity_boosts: 1
data_side_sampling: 0

# G2 knobs — carried forward (G3 is additive on conditioning, not a reset)
sched_sample_p: 0.2
home_label_smooth: 0.05
```

`d_ff` is the only key that may not yet be plumbed through `config_to_env.sh` — verify and add a `d_ff → D_FF` mapping if missing, mirroring the existing `d_model → D_MODEL` plumbing pattern. `04B_model.py` must read `D_FF` from env (with default = `4 * d_model` to stay backward-compat for F-series configs that omit it).

---

## `configs/sweep_G23.yaml` and `configs/sweep_smoke_G23.yaml`

```yaml
# sweep_G23.yaml — combined driver, G2 + G3 in one array submission
# Submit (cluster-tier action — Sonnet/builder owns this): bundle protocol, see step4_training_v2.md §Bundle-Submission Protocol.
tags:
  - G2
  - G3
```

```yaml
# sweep_smoke_G23.yaml — combined smoke driver, both tags must clear before any pg slot is paid for.
tags:
  - G2_smoke
  - G3_smoke
smoke: true
```

Per the F-series sweep precedent: the `smoke: true` flag at the sweep level (or a per-tag `_smoke` suffix that `config_to_env.sh` recognizes) triggers the smoke d_model=64 / 5-epoch path. Confirm the existing convention in `submit_step4_array.sh` before locking in the YAML shape — both styles have appeared in F-series sweep YAMLs.

---

## Verification (smoke gates before any pg slot)

1. **Independence check.** Set `SCHED_SAMPLE_P=0`, `HOME_LABEL_SMOOTH=0`, `D_MODEL=256`, `D_FF=1024`, `data_dir=outputs_step4_G1`, with the new cross-attn decoder — train one epoch, compare AT_HOME loss curve to a recorded G1 reference. **They will not match** (architecture differs) — but the curve must be stable, not divergent. If it diverges, the cross-attn block has an init / mask / shape bug.
2. **G3 smoke (chain `G3_smoke_<date>`).** Standard 5-epoch d_model=64 path. Pass criteria: 04D completes; 04E loads checkpoint without dim mismatch (the `data_dir`-extraction patch in `job_04D_train_array.sh` should already prevent the d_cond=76/77 bug that haunted G2 attempts c–e); 04F/H/I/J/extract_metrics complete; row appears in `results.csv` with all 6 columns. Metrics meaningless at smoke scale — pipeline-clean is the bar.
3. **Memory probe.** Before paying for the pg slot, run the `--mem-probe` dry-run at full size (see Capacity expansion §Memory-fit verification). Record peak GPU memory in the Progress Log row.
4. **Bundle integrity.** `sweep_G23.yaml` produces two trial directories under one job-array index, two `outputs_step4_G{2,3}/` outputs, two rows in `results.csv` — confirmed by inspecting `squeue` for two parallel `04D_array` indices and by `ls outputs_step4_G2/ outputs_step4_G3/` after extract_metrics lands.

---

## Risk register

| Risk                                                  | Mitigation                                                                            |
|-------------------------------------------------------|---------------------------------------------------------------------------------------|
| Cross-attn over 3 tokens collapses (attention picks one block, ignores the others) | Inspect `cross_cond` attention weights post-training (one-off diagnostic notebook, not a gate). If collapsed, fall back to (a) single-token projection. |
| Capacity bump exceeds pg single-GPU budget            | Fallback ladder in §Memory-fit verification; document in Progress Log.                |
| Removing additive `strata_linear` regresses AT_HOME    | Cross-attn `tok_strata` is the replacement signal; if AT_HOME degrades vs. G2 row, restore `strata_linear` as a thin residual path (one-line add) and rerun. |
| `aux_strata_head` tap point breaks under new decoder  | Layer-0 hidden state is still well-defined; just confirm shape `(B, T, d_model)` at the new tap.|
| `D_FF` env-var plumbing incomplete                    | Add `d_ff → D_FF` to `config_to_env.sh` + `config_to_env.py`; default `4 * D_MODEL`.   |
| F-series checkpoints can no longer be re-loaded       | Acceptable — G3 is a forward-only branch; F10a stays as a frozen comparison row.       |

---

## Handoff

When this spec is approved, builder (Sonnet) executes:

1. Implement the cross-attn decoder rewrite in `04B_model.py` per §Architecture change.
2. Add `D_FF` plumbing to `config_to_env.{sh,py}` if missing.
3. Write `configs/G3.yaml`, `configs/sweep_G23.yaml`, `configs/sweep_smoke_G23.yaml`.
4. Run G3 smoke — debug to green.
5. Memory probe at full size — record peak, choose final config from fallback ladder.
6. Submit combined `sweep_G23.yaml` once both G2 and G3 smokes are green (G2 is already running full training at the time of this spec — see `step4_training_v2.md` Progress Log; bundle-submission may degenerate to a G3-solo submission if G2-full lands first, which is acceptable).
7. Append per-stage Progress Log rows to `step4_training_v2.md` for: G3 implementation, G3 smoke result, G3 full submission, G3 results landing.

Manager re-engages on:
- Smoke-debug rounds if G3 smoke fails non-trivially.
- Reading `results.csv` once G2 and G3 rows are both present, against the four hard gates.
- Deciding G-series closure (ship G2 / ship G3 / pivot to data-quality work — see `step4_training_v2.md` Expected result).

---

## STATUS

`PRE-IMPL` — spec ready for builder. Implementation start gated only on builder bandwidth; G2-full training can run in parallel (currently job 906532_0 on `pg`). G3 does not depend on G2 results — both rows are independent evidence under the bundle-submission protocol.
