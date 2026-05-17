"""
04B_model.py — Conditional Transformer Encoder-Decoder architecture for Step 4.

Defines the ConditionalTransformer class that takes an observed 48-slot diary
(one DDAY_STRATA) and generates synthetic diaries for the other two strata,
conditioned on the respondent's demographic profile.

IMPORTANT: Because this filename begins with a digit, it cannot be imported
with a plain `import` statement.  Other scripts must use importlib:

    import importlib, sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    model_mod = importlib.import_module("04B_model")
    ConditionalTransformer = model_mod.ConditionalTransformer

This file is imported, NOT run directly.
"""

import math
import os
import torch
import torch.nn as nn
import torch.nn.functional as F

H_TIME_PE = int(os.environ.get("H_TIME_PE", "0"))


# ── Positional encoding ──────────────────────────────────────────────────────

def sinusoidal_pos_enc(max_len: int, d_model: int) -> torch.Tensor:
    """Standard sinusoidal positional encoding.

    Returns shape (1, max_len, d_model) — broadcast-ready over batch.
    All diaries start at 4:00 AM, so position encodes time-of-day implicitly.
    """
    pe = torch.zeros(1, max_len, d_model)
    pos = torch.arange(max_len, dtype=torch.float).unsqueeze(1)
    div = torch.exp(
        torch.arange(0, d_model, 2, dtype=torch.float) * (-math.log(10000.0) / d_model)
    )
    pe[0, :, 0::2] = torch.sin(pos * div)
    pe[0, :, 1::2] = torch.cos(pos * div)
    return pe


# ── Default hyperparameter config (HPC production settings) ─────────────────

DEFAULT_CONFIG = {
    "d_model":             256,
    "n_heads":             8,
    "d_ff":                1024,
    "N_enc":               6,
    "N_dec":               6,
    "d_act":               32,    # activity category embedding dim
    "d_cycle":             32,    # CYCLE_YEAR learned embedding dim
    "dropout":             0.1,
    "n_activity_classes":  14,
    "n_copresence":        9,
    "n_slots":             48,
    "d_cond":              None,  # set from step4_feature_config.json at runtime
}

# Local-test override: smaller model for CPU speed
TEST_CONFIG = {
    "d_model":             64,
    "n_heads":             4,
    "d_ff":                256,
    "N_enc":               2,
    "N_dec":               2,
    "d_act":               16,
    "d_cycle":             16,
    "dropout":             0.1,
    "n_activity_classes":  14,
    "n_copresence":        9,
    "n_slots":             48,
    "d_cond":              None,
}


# ── Cross-attention conditioning decoder (G3) ────────────────────────────────

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
        layer0_hidden = None
        for i, layer in enumerate(self.layers):
            x = layer(x, memory, cond_tokens, tgt_mask)
            if i == 0:
                layer0_hidden = x
        return self.norm(x), layer0_hidden


# ── Model ────────────────────────────────────────────────────────────────────

class ConditionalTransformer(nn.Module):
    """
    Conditional Transformer Encoder-Decoder for diary augmentation.

    Encoder processes the observed 48-slot diary (with demographic CLS token).
    Decoder generates the target-stratum diary via cross-attention over the
    encoder output.  Three output heads predict:
      - activity (14 categories, cross-entropy)
      - AT_HOME (binary, BCE)
      - co-presence (9 binary columns, BCE with availability mask)

    Args:
        config: dict with keys from DEFAULT_CONFIG.  d_cond must be set.
    """

    def __init__(self, config: dict):
        super().__init__()

        d_model  = config["d_model"]
        n_heads  = config["n_heads"]
        d_ff     = config["d_ff"]
        N_enc    = config["N_enc"]
        N_dec    = config["N_dec"]
        d_act    = config.get("d_act",   32)
        d_cycle  = config.get("d_cycle", 32)
        dropout  = config.get("dropout", 0.1)
        n_act    = config.get("n_activity_classes", 14)
        n_cop    = config.get("n_copresence", 9)
        n_slots  = config.get("n_slots", 48)
        d_cond   = config["d_cond"]   # pre-computed conditioning vector dim

        self.d_model  = d_model
        self.n_slots  = n_slots
        self.n_act    = n_act
        self.n_cop    = n_cop

        # ── Shared slot embedding (encoder & decoder) ────────────────────
        # occACT → Embedding(14, d_act), then concat with [AT_HOME + 9 co-pres]
        self.act_embedding = nn.Embedding(n_act, d_act)
        self.slot_linear   = nn.Linear(d_act + 1 + n_cop, d_model)  # +1 for AT_HOME

        # ── Encoder: CLS token (demographic conditioning) ────────────────
        # CYCLE_YEAR → learned embedding, concatenated with pre-computed cond_vec
        self.cycle_embedding = nn.Embedding(4, d_cycle)
        # MLP: (d_cond + d_cycle) → 256 → d_model
        self.cls_mlp = nn.Sequential(
            nn.Linear(d_cond + d_cycle, 256),
            nn.GELU(),
            nn.Linear(256, d_model),
        )

        # ── Decoder: BOS token ───────────────────────────────────────────
        # Learnable BOS token (start-of-sequence for decoder)
        self.bos_token = nn.Parameter(torch.randn(1, 1, d_model) * 0.02)

        # ── Sinusoidal positional encodings ──────────────────────────────
        # Encoder: 49 positions (1 CLS + 48 slots)
        # Decoder: 48 positions (BOS=pos 0 + 47 shifted GT slots)
        self.register_buffer("enc_pos_enc", sinusoidal_pos_enc(n_slots + 1, d_model))
        self.register_buffer("dec_pos_enc", sinusoidal_pos_enc(n_slots,     d_model))

        if H_TIME_PE:
            self.learnable_pe = nn.Parameter(torch.randn(1, n_slots, d_model) * 0.02)
            t_idx = torch.arange(n_slots, dtype=torch.float)
            cyc = torch.stack([
                torch.sin(2 * math.pi * t_idx / n_slots),
                torch.cos(2 * math.pi * t_idx / n_slots),
            ], dim=-1).unsqueeze(0)  # (1, 48, 2)
            self.register_buffer("cyclical_time", cyc)
            self.time_proj = nn.Linear(d_model + 2, d_model)

        # ── Transformer encoder ──────────────────────────────────────────
        enc_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=n_heads, dim_feedforward=d_ff,
            dropout=dropout, activation="gelu", batch_first=True,
        )
        self.encoder = nn.TransformerEncoder(
            enc_layer, num_layers=N_enc, norm=nn.LayerNorm(d_model)
        )

        # ── Transformer decoder (cross-attention conditioning, G3) ───────
        # CrossAttnDecoder: self-attn → cross-attn(memory) → cross-attn(3
        # conditioning tokens: demo, cycle, strata) → FFN, per layer.
        self.decoder = CrossAttnDecoder(
            d_model=d_model, n_heads=n_heads, n_layers=N_dec,
            d_ff=d_ff, d_cond=d_cond, d_cycle=d_cycle,
        )

        # ── Output heads ─────────────────────────────────────────────────
        # H_TANH_HEADS=1: wrap home/cop heads with Tanh pre-activation (H_Tanh trial).
        # H_TANH_HEADS=0 (default): plain Linear — identical to G4.
        _h_tanh = os.environ.get("H_TANH_HEADS", "0") == "1"
        self.act_head  = nn.Linear(d_model, n_act)  # → 14 activity logits
        self.home_head = (nn.Sequential(nn.Tanh(), nn.Linear(d_model, 1))
                          if _h_tanh else nn.Linear(d_model, 1))
        self.cop_head  = (nn.Sequential(nn.Tanh(), nn.Linear(d_model, n_cop))
                          if _h_tanh else nn.Linear(d_model, n_cop))

        # Optional auxiliary head: predicts target DDAY_STRATA (3-way CE) from
        # decoder layer-0 hidden mean-pool. Gated by config["aux_stratum_head"].
        if config.get("aux_stratum_head", False):
            self.aux_strata_head = nn.Sequential(
                nn.Linear(d_model, 64),
                nn.GELU(),
                nn.Linear(64, 3),
            )
        else:
            self.aux_strata_head = None

        self._init_weights()

    def _init_weights(self):
        """Xavier init for linear layers; normal for embeddings."""
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, nn.Embedding):
                nn.init.normal_(m.weight, std=0.02)

    # ── Slot embedding (shared) ──────────────────────────────────────────────

    def _embed_slots(self, act_seq: torch.Tensor, aux_seq: torch.Tensor) -> torch.Tensor:
        """
        Embed 48 multivariate slot tokens.

        act_seq : (B, T)      — int64, 0-indexed activity categories
        aux_seq : (B, T, 10)  — float32, [AT_HOME | 9 co-presence]
        Returns : (B, T, d_model)
        """
        act_emb    = self.act_embedding(act_seq)          # (B, T, d_act)
        slot_input = torch.cat([act_emb, aux_seq], dim=-1)  # (B, T, d_act+10)
        return self.slot_linear(slot_input)                 # (B, T, d_model)

    # ── Encoder ─────────────────────────────────────────────────────────────

    def encode(self, act_seq, aux_seq, cond_vec, cycle_idx) -> torch.Tensor:
        """
        Encode observed diary + demographic CLS token.

        Returns memory: (B, 49, d_model) — 1 CLS + 48 slot states.
        """
        B = act_seq.shape[0]

        # Slot embeddings with positional encoding at positions 1..48
        slot_emb = self._embed_slots(act_seq, aux_seq)         # (B, 48, d_model)
        slot_emb = slot_emb + self.enc_pos_enc[:, 1:, :]

        # CLS token: demographics + cycle year embedding, projected to d_model
        cycle_emb  = self.cycle_embedding(cycle_idx)            # (B, d_cycle)
        cls_input  = torch.cat([cond_vec, cycle_emb], dim=-1)   # (B, d_cond+d_cycle)
        cls_tok    = self.cls_mlp(cls_input).unsqueeze(1)        # (B, 1, d_model)
        cls_tok    = cls_tok + self.enc_pos_enc[:, :1, :]        # position 0

        enc_input = torch.cat([cls_tok, slot_emb], dim=1)       # (B, 49, d_model)
        return self.encoder(enc_input)                           # (B, 49, d_model)

    # ── Decoder (teacher-forcing mode) ──────────────────────────────────────

    def _build_dec_cond(self, cond_vec, cycle_idx, tgt_strata):
        """Returns (cond_vec, cycle_emb, strata_oh) for CrossAttnDecoder."""
        cycle_emb = self.cycle_embedding(cycle_idx)
        strata_oh = F.one_hot((tgt_strata - 1).clamp(0, 2), num_classes=3).float()
        return cond_vec, cycle_emb, strata_oh

    def decode(self, dec_act_seq, dec_aux_seq, tgt_strata, memory,
               cond_vec, cycle_idx):
        """
        Teacher-forcing decode: predicts target slots given ground-truth shifted input.

        dec_act_seq : (B, 48) — int64, target activity sequence
        dec_aux_seq : (B, 48, 10) — target [AT_HOME | co-pres]
        tgt_strata  : (B,) — int64, target DDAY_STRATA (1,2,3)
        memory      : (B, 49, d_model) — encoder output
        cond_vec    : (B, d_cond)
        cycle_idx   : (B,) — int64

        Returns act_logits (B,48,14), home_logits (B,48), cop_logits (B,48,9)
        """
        B, T = dec_act_seq.shape

        # Embed target slots
        tgt_emb = self._embed_slots(dec_act_seq, dec_aux_seq)   # (B, T, d_model)

        # Shift right: [BOS, slot_0, ..., slot_{T-2}]
        bos       = self.bos_token.expand(B, 1, -1)
        dec_input = torch.cat([bos, tgt_emb[:, :-1, :]], dim=1) # (B, T, d_model)

        # Positional encoding (positions 0..T-1)
        if H_TIME_PE:
            cyc = self.cyclical_time.expand(B, -1, -1)[:, :T, :]
            dec_input = self.time_proj(torch.cat([dec_input, cyc], dim=-1))
            dec_input = dec_input + self.learnable_pe[:, :T, :]
        else:
            dec_input = dec_input + self.dec_pos_enc[:, :T, :]

        # Cross-attention conditioning tensors
        cond_vec_d, cycle_emb_d, strata_oh_d = self._build_dec_cond(cond_vec, cycle_idx, tgt_strata)

        # Causal mask: each position attends only to itself and earlier positions
        causal_mask = nn.Transformer.generate_square_subsequent_mask(
            T, device=dec_input.device
        )
        dec_output, layer0_hidden = self.decoder(
            dec_input, memory, cond_vec_d, cycle_emb_d, strata_oh_d, causal_mask
        )  # dec_output: (B, T, d_model); layer0_hidden: (B, T, d_model)

        aux_logits = None
        if self.aux_strata_head is not None and layer0_hidden is not None:
            aux_logits = self.aux_strata_head(layer0_hidden.mean(dim=1))  # (B, 3)

        return (
            self.act_head(dec_output),               # (B, T, 14)
            self.home_head(dec_output).squeeze(-1),  # (B, T)
            self.cop_head(dec_output),               # (B, T, 9)
            aux_logits,                              # (B, 3) or None
        )

    # ── Forward (teacher-forcing, called during training) ────────────────────

    def forward(self, batch: dict) -> dict:
        """
        Full forward pass with teacher forcing.

        Expects batch keys:
          act_seq, aux_seq, cond_vec, cycle_idx  — encoder (observed diary)
          dec_act_seq, dec_aux_seq               — decoder targets (neighbor)
          tgt_strata                              — target DDAY_STRATA (1,2,3)
        """
        memory = self.encode(
            batch["act_seq"], batch["aux_seq"],
            batch["cond_vec"], batch["cycle_idx"],
        )
        act_logits, home_logits, cop_logits, aux_logits = self.decode(
            batch["dec_act_seq"], batch["dec_aux_seq"],
            batch["tgt_strata"], memory,
            batch["cond_vec"], batch["cycle_idx"],
        )
        return {
            "act_logits":  act_logits,
            "home_logits": home_logits,
            "cop_logits":  cop_logits,
            "aux_logits":  aux_logits,
        }

    # ── Inference (autoregressive generation) ────────────────────────────────

    @torch.no_grad()
    def generate(
        self,
        act_seq:   torch.Tensor,
        aux_seq:   torch.Tensor,
        cond_vec:  torch.Tensor,
        cycle_idx: torch.Tensor,
        tgt_strata: torch.Tensor,
        temperature: float = 0.8,
        home_threshold: float = 0.5,
    ):
        """
        Autoregressive generation for one or more respondents.

        act_seq    : (B, 48) — observed diary (encoder input)
        aux_seq    : (B, 48, 10) — observed aux sequence (encoder input)
        cond_vec   : (B, d_cond)
        cycle_idx  : (B,)
        tgt_strata : (B,) — target DDAY_STRATA (1,2,3)
        temperature: >0 → multinomial sampling; 0 → argmax (deterministic)
        home_threshold: sigmoid cutoff for AT_HOME decision (default 0.5).
                        Raising it reduces AT_HOME=1 predictions; because
                        home_tok is fed back into the decoder's aux input at
                        the next step, the choice cascades through the diary.

        Returns:
            gen_act  (B, 48) int64 — 0-indexed generated activity
            gen_home (B, 48) float32 — binary AT_HOME
            gen_cop  (B, 48, 9) float32 — binary co-presence
        """
        device = act_seq.device
        B      = act_seq.shape[0]

        memory = self.encode(act_seq, aux_seq, cond_vec, cycle_idx)

        # Cross-attn conditioning tensors (fixed for all decoder steps)
        cond_vec_g, cycle_emb_g, strata_oh_g = self._build_dec_cond(cond_vec, cycle_idx, tgt_strata)

        gen_acts       = []
        gen_homes      = []
        gen_cops       = []
        gen_cop_probs  = []

        # Decoder sequence starts with the BOS token at position 0
        bos_tok = self.bos_token.expand(B, 1, self.d_model)
        if not H_TIME_PE:
            bos_tok = bos_tok + self.dec_pos_enc[:, :1, :]
        dec_tokens = [bos_tok]

        for t in range(self.n_slots):
            dec_seq = torch.cat(dec_tokens, dim=1)           # (B, t+1, d_model)
            if H_TIME_PE:
                _sz = dec_seq.size(1)
                cyc = self.cyclical_time.expand(B, -1, -1)[:, :_sz, :]
                dec_seq = self.time_proj(torch.cat([dec_seq, cyc], dim=-1))
                dec_seq = dec_seq + self.learnable_pe[:, :_sz, :]
            causal_mask = nn.Transformer.generate_square_subsequent_mask(
                dec_seq.shape[1], device=device
            )
            dec_out, _ = self.decoder(dec_seq, memory,
                                      cond_vec_g, cycle_emb_g, strata_oh_g, causal_mask)
            out_t = dec_out[:, -1, :]                             # (B, d_model)

            # Activity head
            act_logits = self.act_head(out_t)                     # (B, 14)
            if temperature > 0:
                act_probs = F.softmax(act_logits / temperature, dim=-1)
                act_tok   = torch.multinomial(act_probs, 1).squeeze(-1)  # (B,)
            else:
                act_tok = act_logits.argmax(dim=-1)

            # AT_HOME head
            home_tok = (torch.sigmoid(self.home_head(out_t).squeeze(-1)) > home_threshold).float()

            # Co-presence head — raw σ for output, binary for AR feedback
            cop_probs = torch.sigmoid(self.cop_head(out_t))        # (B, 9) float in [0,1]
            cop_tok   = (cop_probs > 0.5).float()                  # (B, 9) binary — matches training

            gen_acts.append(act_tok)
            gen_homes.append(home_tok)
            gen_cops.append(cop_tok)
            gen_cop_probs.append(cop_probs)

            # Embed the just-generated slot to feed as next decoder input
            # Position t+1 in the decoder sequence (BOS was position 0)
            if t < self.n_slots - 1:
                aux_t    = torch.cat([home_tok.unsqueeze(-1), cop_tok], dim=-1)  # (B, 10)
                act_emb  = self.act_embedding(act_tok)                            # (B, d_act)
                slot_in  = torch.cat([act_emb, aux_t], dim=-1)                   # (B, d_act+10)
                slot_out = self.slot_linear(slot_in).unsqueeze(1)                 # (B, 1, d_model)
                if not H_TIME_PE:
                    slot_out = slot_out + self.dec_pos_enc[:, t + 1:t + 2, :]
                dec_tokens.append(slot_out)

        return (
            torch.stack(gen_acts,      dim=1),      # (B, 48) int64
            torch.stack(gen_homes,     dim=1),      # (B, 48) float32
            torch.stack(gen_cops,      dim=1),      # (B, 48, 9) float32 binary
            torch.stack(gen_cop_probs, dim=1),      # (B, 48, 9) float32 raw σ
        )


# ── Encoder-only (H_NAT) ─────────────────────────────────────────────────────

class EncoderOnlyOccupancyModel(nn.Module):
    """
    Encoder-only (non-AR) architecture for diary generation (H_NAT trial).

    Encodes the observed 48-slot diary with a CLS conditioning token, then
    refines with a 2-layer bidirectional TransformerEncoder.  Parallel heads
    predict all 48 target slots simultaneously in a single forward pass.

    No AR loop, no BOS token, no causal mask.
    Post-hoc safety net (in infer()): Spouse channel zeroed when AT_HOME=0.
    H-Tier-1.6 AR-cascade diagnostic modes A/B/C do not apply to this model.
    """

    SPOUSE_IDX = 1  # index in 9-channel cop tensor

    def __init__(self, config: dict):
        super().__init__()

        d_model = config["d_model"]
        n_heads = config["n_heads"]
        d_ff    = config["d_ff"]
        N_enc   = config["N_enc"]
        N_ref   = config.get("refinement_layers", 2)
        d_act   = config.get("d_act",   32)
        d_cycle = config.get("d_cycle", 32)
        dropout = config.get("dropout", 0.1)
        n_act   = config.get("n_activity_classes", 14)
        n_cop   = config.get("n_copresence", 9)
        n_slots = config.get("n_slots", 48)
        d_cond  = config["d_cond"]

        self.d_model = d_model
        self.n_slots = n_slots
        self.n_act   = n_act
        self.n_cop   = n_cop

        # Slot embedding (same as ConditionalTransformer)
        self.act_embedding = nn.Embedding(n_act, d_act)
        self.slot_linear   = nn.Linear(d_act + 1 + n_cop, d_model)

        # CLS token for encoder (same as ConditionalTransformer)
        self.cycle_embedding = nn.Embedding(4, d_cycle)
        self.cls_mlp = nn.Sequential(
            nn.Linear(d_cond + d_cycle, 256),
            nn.GELU(),
            nn.Linear(256, d_model),
        )

        # Sinusoidal PE: 49 positions (1 CLS + 48 slots)
        self.register_buffer("enc_pos_enc", sinusoidal_pos_enc(n_slots + 1, d_model))

        # 6-layer transformer encoder (same depth as G4)
        enc_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=n_heads, dim_feedforward=d_ff,
            dropout=dropout, activation="gelu", batch_first=True,
        )
        self.encoder = nn.TransformerEncoder(
            enc_layer, num_layers=N_enc, norm=nn.LayerNorm(d_model)
        )

        # Target stratum conditioning token prepended to refinement input
        self.strata_proj = nn.Linear(3, d_model)

        # 2-layer bidirectional refinement (no causal mask)
        ref_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=n_heads, dim_feedforward=d_ff,
            dropout=dropout, activation="gelu", batch_first=True,
        )
        self.refinement = nn.TransformerEncoder(
            ref_layer, num_layers=N_ref, norm=nn.LayerNorm(d_model)
        )

        # Parallel output heads
        self.act_head  = nn.Linear(d_model, n_act)
        self.home_head = nn.Linear(d_model, 1)
        self.cop_head  = nn.Linear(d_model, n_cop)

        self._init_weights()

    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, nn.Embedding):
                nn.init.normal_(m.weight, std=0.02)

    def _embed_slots(self, act_seq, aux_seq):
        act_emb    = self.act_embedding(act_seq)
        slot_input = torch.cat([act_emb, aux_seq], dim=-1)
        return self.slot_linear(slot_input)

    def _encode(self, act_seq, aux_seq, cond_vec, cycle_idx):
        slot_emb  = self._embed_slots(act_seq, aux_seq)
        slot_emb  = slot_emb + self.enc_pos_enc[:, 1:, :]
        cycle_emb = self.cycle_embedding(cycle_idx)
        cls_tok   = self.cls_mlp(torch.cat([cond_vec, cycle_emb], dim=-1)).unsqueeze(1)
        cls_tok   = cls_tok + self.enc_pos_enc[:, :1, :]
        return self.encoder(torch.cat([cls_tok, slot_emb], dim=1))  # (B, 49, d_model)

    def _refine(self, memory, tgt_strata):
        """Prepend target-stratum token, run bidirectional refinement, return slot outputs."""
        slots      = memory[:, 1:, :]  # (B, 48, d_model)
        strata_oh  = F.one_hot((tgt_strata - 1).clamp(0, 2), num_classes=3).float()
        cond_token = self.strata_proj(strata_oh).unsqueeze(1)     # (B, 1, d_model)
        refined    = self.refinement(torch.cat([cond_token, slots], dim=1))  # (B, 49, d_model)
        return refined[:, 1:, :]  # (B, 48, d_model) — drop strata token

    def forward(self, batch: dict) -> dict:
        """Teacher-forcing forward for training. Encodes source diary, refines to target."""
        memory = self._encode(batch["act_seq"], batch["aux_seq"],
                              batch["cond_vec"], batch["cycle_idx"])
        slots  = self._refine(memory, batch["tgt_strata"])
        return {
            "act_logits":  self.act_head(slots),               # (B, 48, 14)
            "home_logits": self.home_head(slots).squeeze(-1),  # (B, 48)
            "cop_logits":  self.cop_head(slots),               # (B, 48, 9)
            "aux_logits":  None,
        }

    @torch.no_grad()
    def infer(self, act_seq, aux_seq, cond_vec, cycle_idx, tgt_strata,
              apply_safety: bool = True):
        """
        Single-pass inference. Returns (gen_act, gen_home, gen_cop_probs).
        Post-hoc safety net: Spouse probability zeroed when AT_HOME=0 (apply_safety=True).
        gen_act is 0-indexed (compatible with validate() and 04J metrics pipeline).
        """
        memory = self._encode(act_seq, aux_seq, cond_vec, cycle_idx)
        slots  = self._refine(memory, tgt_strata)

        gen_act  = self.act_head(slots).argmax(dim=-1)                     # (B, 48) 0-indexed
        gen_home = (torch.sigmoid(self.home_head(slots).squeeze(-1)) > 0.5).float()  # (B, 48)
        cop_prob = torch.sigmoid(self.cop_head(slots))                     # (B, 48, 9)

        if apply_safety:
            # Zero Spouse when person is not home (post-hoc logical constraint)
            cop_prob = cop_prob.clone()
            cop_prob[:, :, self.SPOUSE_IDX] = (
                cop_prob[:, :, self.SPOUSE_IDX] * gen_home
            )

        return gen_act, gen_home, cop_prob


# ── Encoder-only faithful port (I1) ──────────────────────────────────────────

class IOccupancyModel(nn.Module):
    """
    I1: Faithful encoder-only port of examples/cloud_computing/Transformer_pipeline.py.

    Per-slot fusion at every position t in [0, 48):
      time-of-day embed + day-of-week embed + slot-index embed +
      source-diary activity at slot t + broadcast-concat with
      cond_vec (demographics) + cycle_emb + strata_oh.
    Projected to d_model, then + learnable PE (nn.Embedding(48, d_model)).
    Single nn.TransformerEncoder — no decoder, no causal mask, no token feedback.
    Heads: activity (Linear), AT_HOME (Linear→Tanh→Linear), co-presence (Linear→Tanh→Linear).
    infer(): cop_pred *= (home_pred>0.5) safety clip when apply_safety=True.
    """

    def __init__(self, config: dict):
        super().__init__()

        d_model = config["d_model"]
        n_heads = config["n_heads"]
        d_ff    = config["d_ff"]
        N_enc   = config["N_enc"]
        d_act   = config.get("d_act",   32)
        d_cycle = config.get("d_cycle", 32)
        dropout = config.get("dropout", 0.1)
        n_act   = config.get("n_activity_classes", 14)
        n_cop   = config.get("n_copresence", 9)
        n_slots = config.get("n_slots", 48)
        d_cond  = config["d_cond"]

        self.d_model = d_model
        self.n_slots = n_slots
        self.n_act   = n_act
        self.n_cop   = n_cop

        # Per-slot conditioning embedding dimensions
        d_tod  = 16   # time-of-day (slot → time, indexed by t)
        d_dow  = 8    # day-of-week (from tgt_strata 0..2)
        d_sidx = 16   # slot-index positional signal (indexed by t)

        self.act_emb   = nn.Embedding(n_act,   d_act)
        self.tod_emb   = nn.Embedding(n_slots, d_tod)
        self.dow_emb   = nn.Embedding(3,       d_dow)
        self.sidx_emb  = nn.Embedding(n_slots, d_sidx)
        self.cycle_emb = nn.Embedding(4,       d_cycle)

        # Per-slot projection: fused concat → d_model
        # concat dims: d_act + d_tod + d_dow + d_sidx + d_cycle + d_cond + 3 (strata_oh)
        d_fused = d_act + d_tod + d_dow + d_sidx + d_cycle + d_cond + 3
        self.slot_proj = nn.Linear(d_fused, d_model)

        # Learnable positional encoding (H_Time win carried forward)
        self.learnable_pe = nn.Embedding(n_slots, d_model)

        # Single TransformerEncoder — no decoder, no causal mask
        enc_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=n_heads, dim_feedforward=d_ff,
            dropout=dropout, activation="gelu", batch_first=True,
        )
        self.encoder = nn.TransformerEncoder(
            enc_layer, num_layers=N_enc, norm=nn.LayerNorm(d_model)
        )

        # Output heads (H_Tanh win: Tanh pre-activation on binary heads)
        self.act_head  = nn.Linear(d_model, n_act)
        self.home_head = nn.Sequential(
            nn.Linear(d_model, d_model), nn.Tanh(), nn.Linear(d_model, 1)
        )
        self.cop_head = nn.Sequential(
            nn.Linear(d_model, d_model), nn.Tanh(), nn.Linear(d_model, n_cop)
        )

        self._init_weights()

    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, nn.Embedding):
                nn.init.normal_(m.weight, std=0.02)

    def _fuse_and_encode(self, act_seq, cond_vec, cycle_idx, tgt_strata):
        """
        Build per-slot fused sequence and run through encoder.

        act_seq:    (B, T) int64  — source-diary activity (preserves source signal)
        cond_vec:   (B, d_cond)   — pre-computed demographic conditioning
        cycle_idx:  (B,) int64   — cycle year index 0..3
        tgt_strata: (B,) int64   — target stratum 1..3
        Returns:    (B, T, d_model)
        """
        B, T = act_seq.shape
        device = act_seq.device

        t_idx = torch.arange(T, dtype=torch.long, device=device)  # (T,)

        # Per-slot signals that vary by position
        act_emb_t  = self.act_emb(act_seq)                                    # (B, T, d_act)
        tod_emb_t  = self.tod_emb(t_idx).unsqueeze(0).expand(B, -1, -1)       # (B, T, d_tod)
        sidx_emb_t = self.sidx_emb(t_idx).unsqueeze(0).expand(B, -1, -1)      # (B, T, d_sidx)

        # Per-respondent signals broadcast across all T positions
        dow_idx   = (tgt_strata - 1).clamp(0, 2)                              # (B,)
        dow_emb_b = self.dow_emb(dow_idx).unsqueeze(1).expand(-1, T, -1)      # (B, T, d_dow)
        cyc_emb_b = self.cycle_emb(cycle_idx).unsqueeze(1).expand(-1, T, -1)  # (B, T, d_cycle)
        cond_b    = cond_vec.unsqueeze(1).expand(-1, T, -1)                   # (B, T, d_cond)
        strata_oh = F.one_hot(dow_idx, num_classes=3).float()                 # (B, 3)
        strata_b  = strata_oh.unsqueeze(1).expand(-1, T, -1)                  # (B, T, 3)

        # Fuse and project to d_model
        fused = torch.cat(
            [act_emb_t, tod_emb_t, dow_emb_b, sidx_emb_t, cyc_emb_b, cond_b, strata_b],
            dim=-1,
        )  # (B, T, d_fused)
        x = self.slot_proj(fused)                                              # (B, T, d_model)

        # Add learnable positional encoding
        pe = self.learnable_pe(t_idx).unsqueeze(0)                             # (1, T, d_model)
        x = x + pe

        return self.encoder(x)  # (B, T, d_model)

    def forward(self, batch: dict) -> dict:
        """Single-pass training forward. No AR loop, no causal mask."""
        enc = self._fuse_and_encode(
            batch["act_seq"], batch["cond_vec"],
            batch["cycle_idx"], batch["tgt_strata"],
        )
        return {
            "act_logits":  self.act_head(enc),                # (B, 48, 14)
            "home_logits": self.home_head(enc).squeeze(-1),   # (B, 48)
            "cop_logits":  self.cop_head(enc),                # (B, 48, 9)
            "aux_logits":  None,
        }

    @torch.no_grad()
    def infer(self, act_seq, aux_seq, cond_vec, cycle_idx, tgt_strata,
              apply_safety: bool = True):
        """
        Single-pass inference. aux_seq accepted for API compatibility but not used.
        apply_safety=True: zero all cop channels when AT_HOME=0 (spec requirement).
        Returns (gen_act [B,48], gen_home [B,48], cop_prob [B,48,9]).
        """
        enc = self._fuse_and_encode(act_seq, cond_vec, cycle_idx, tgt_strata)

        gen_act  = self.act_head(enc).argmax(dim=-1)                          # (B, 48) 0-indexed
        home_sig = torch.sigmoid(self.home_head(enc).squeeze(-1))             # (B, 48)
        gen_home = (home_sig > 0.5).float()
        cop_prob = torch.sigmoid(self.cop_head(enc))                          # (B, 48, 9)

        if apply_safety:
            cop_prob = cop_prob.clone()
            cop_prob *= gen_home.unsqueeze(-1)  # zero all cop channels when not home

        return gen_act, gen_home, cop_prob


# ── J-Series Hybrid (J1) ─────────────────────────────────────────────────────

class JSeriesHybrid(nn.Module):
    """
    J-series Hybrid AR-Encoder architecture (J1 / J2 / J2.5 / J3).

    Trunk:  6-layer TransformerEncoder (d_model=384, n_heads=8, d_ff=1536, sinusoidal PE).
    Arm 1:  G4 CrossAttnDecoder, activity-only AR loop, sched_sample_p=0.0.
            Does NOT consume AT_HOME at any step (no feedback cascade).
    Arm 2:  Per-slot NAT fusion → Tanh-gated binary heads (J1/J2 default).

    MODEL_TYPE variants (single-axis each, forked from frozen J1):
      J1  — baseline; all defaults below apply.
      J2  — config-only (lambda_home=0.90); architecture identical to J1.
      J2_5 — home_head replaced with Linear→GELU→Dropout→Linear (drops Tanh collapse);
              cop head unchanged; arm2_proj unchanged.
      J3  — arm2_act_proj: Linear(n_act, d_model) projects soft activity probs before
              Arm-2 concat (dim-balance fix); arm2_proj input grows by (d_model - n_act);
              heads and Arm-1 unchanged.

    Loss:   standard cop_loss_masked path (NOT I1 masked Spouse BCE).
    Infer:  clip-only Spouse safety at inference: cop_pred[:,:,1] *= (home_pred>0.5).

    Arm 2 act_probs note: softmax(act_logits.detach()) at training (soft, richer signal);
    one_hot(act_tokens).float() at inference (hard). Both are (B,48,n_act). The .detach()
    isolates gradients regardless, so training/inference mismatch is intentional and
    bounded — Arm 2 sees richer signal during learning, consistent one-hot at eval.
    """

    SPOUSE_IDX = 1

    def __init__(self, config: dict):
        super().__init__()

        d_model = config["d_model"]
        n_heads = config["n_heads"]
        d_ff    = config["d_ff"]
        N_enc   = config["N_enc"]
        N_dec   = config.get("N_dec", 6)
        d_act   = config.get("d_act",   32)
        d_cycle = config.get("d_cycle", 32)
        dropout = config.get("dropout", 0.1)
        n_act   = config.get("n_activity_classes", 14)
        n_cop   = config.get("n_copresence", 9)
        n_slots = config.get("n_slots", 48)
        d_cond  = config["d_cond"]

        self.d_model = d_model
        self.n_slots = n_slots
        self.n_act   = n_act
        self.n_cop   = n_cop
        _mtype = config.get("model_type", "J1")

        # ── Encoder: source-diary slot embedding (act + full aux) ────────
        self.act_embedding = nn.Embedding(n_act, d_act)
        self.slot_linear   = nn.Linear(d_act + 1 + n_cop, d_model)

        # ── CLS token: cycle + demographic conditioning ──────────────────
        self.cycle_embedding = nn.Embedding(4, d_cycle)
        self.cls_mlp = nn.Sequential(
            nn.Linear(d_cond + d_cycle, 256),
            nn.GELU(),
            nn.Linear(256, d_model),
        )

        # ── Arm 1: BOS token, sinusoidal PE, activity-only slot proj ────
        self.bos_token      = nn.Parameter(torch.randn(1, 1, d_model) * 0.02)
        self.arm1_slot_proj = nn.Linear(d_act, d_model)  # activity-only, no AT_HOME
        self.register_buffer("enc_pos_enc", sinusoidal_pos_enc(n_slots + 1, d_model))
        self.register_buffer("dec_pos_enc", sinusoidal_pos_enc(n_slots,     d_model))

        # ── Trunk: 6-layer TransformerEncoder ───────────────────────────
        enc_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=n_heads, dim_feedforward=d_ff,
            dropout=dropout, activation="gelu", batch_first=True,
        )
        self.encoder = nn.TransformerEncoder(
            enc_layer, num_layers=N_enc, norm=nn.LayerNorm(d_model)
        )

        # ── Arm 1: G4 CrossAttnDecoder ──────────────────────────────────
        self.arm1_decoder = CrossAttnDecoder(
            d_model=d_model, n_heads=n_heads, n_layers=N_dec,
            d_ff=d_ff, d_cond=d_cond, d_cycle=d_cycle,
        )
        self.act_head = nn.Linear(d_model, n_act)

        # ── Arm 2: per-slot fusion projection ────────────────────────────
        # J3: arm2_act_proj projects soft act probs (n_act → d_model) before concat.
        # J1/J2/J2.5: raw n_act-dim probs enter concat directly.
        if _mtype == "J3":
            self.arm2_act_proj = nn.Linear(n_act, d_model)
            d_arm2_in = d_model + d_model + d_cond + d_cycle + 3
        else:
            d_arm2_in = d_model + n_act + d_cond + d_cycle + 3
        self.arm2_proj = nn.Linear(d_arm2_in, d_model)

        # AT_HOME head (logit output; sigmoid applied externally in loss/infer).
        # J2_5: GELU+Dropout variant — hypothesis: Tanh gate causes σ=0.0 collapse.
        # J1/J2/J3: original Tanh-gated head.
        if _mtype == "J2_5":
            self.home_head = nn.Sequential(
                nn.Linear(d_model, d_model), nn.GELU(), nn.Dropout(dropout),
                nn.Linear(d_model, 1),
            )
        else:
            self.home_head = nn.Sequential(
                nn.Linear(d_model, d_model), nn.Tanh(), nn.Linear(d_model, 1)
            )
        # Co-presence head: Tanh-gated, 9-channel — unchanged across all J arms
        self.cop_head = nn.Sequential(
            nn.Linear(d_model, d_model), nn.Tanh(), nn.Linear(d_model, n_cop)
        )

        self._init_weights()

    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, nn.Embedding):
                nn.init.normal_(m.weight, std=0.02)

    # ── Encoder ─────────────────────────────────────────────────────────────

    def _encode(self, act_seq, aux_seq, cond_vec, cycle_idx):
        """Encode observed source diary. Returns memory (B, 49, d_model)."""
        act_emb  = self.act_embedding(act_seq)
        slot_emb = self.slot_linear(torch.cat([act_emb, aux_seq], dim=-1))
        slot_emb = slot_emb + self.enc_pos_enc[:, 1:, :]

        cycle_emb = self.cycle_embedding(cycle_idx)
        cls_tok   = self.cls_mlp(
            torch.cat([cond_vec, cycle_emb], dim=-1)
        ).unsqueeze(1)
        cls_tok   = cls_tok + self.enc_pos_enc[:, :1, :]

        return self.encoder(torch.cat([cls_tok, slot_emb], dim=1))

    # ── Arm 1 helpers ────────────────────────────────────────────────────────

    def _build_arm1_cond(self, cond_vec, cycle_idx, tgt_strata):
        cycle_emb = self.cycle_embedding(cycle_idx)
        strata_oh = F.one_hot((tgt_strata - 1).clamp(0, 2), num_classes=3).float()
        return cond_vec, cycle_emb, strata_oh

    def _arm1_decode_tf(self, dec_act_seq, tgt_strata, memory, cond_vec, cycle_idx):
        """
        Teacher-forced Arm 1 decode. Activity-only decoder inputs — no AT_HOME.
        Returns act_logits (B, 48, n_act).
        """
        B, T = dec_act_seq.shape
        act_emb   = self.act_embedding(dec_act_seq)       # (B, T, d_act)
        tgt_emb   = self.arm1_slot_proj(act_emb)          # (B, T, d_model)

        bos = self.bos_token.expand(B, 1, -1)
        dec_input = torch.cat([bos, tgt_emb[:, :-1, :]], dim=1)  # (B, T, d_model)
        dec_input = dec_input + self.dec_pos_enc[:, :T, :]

        cond_vec_d, cycle_emb_d, strata_oh_d = self._build_arm1_cond(
            cond_vec, cycle_idx, tgt_strata
        )
        causal_mask = nn.Transformer.generate_square_subsequent_mask(
            T, device=dec_input.device
        )
        dec_out, _ = self.arm1_decoder(
            dec_input, memory, cond_vec_d, cycle_emb_d, strata_oh_d, causal_mask
        )
        return self.act_head(dec_out)  # (B, T, n_act)

    def _arm1_generate(self, memory, cond_vec, cycle_idx, tgt_strata):
        """
        AR activity generation. No AT_HOME feedback. Returns (B, 48) int64 0-indexed.
        """
        B = memory.shape[0]
        device = memory.device
        cond_vec_d, cycle_emb_d, strata_oh_d = self._build_arm1_cond(
            cond_vec, cycle_idx, tgt_strata
        )

        bos_tok = self.bos_token.expand(B, 1, -1) + self.dec_pos_enc[:, :1, :]
        dec_tokens = [bos_tok]
        act_tokens = []

        for t in range(self.n_slots):
            dec_seq = torch.cat(dec_tokens, dim=1)
            causal_mask = nn.Transformer.generate_square_subsequent_mask(
                dec_seq.shape[1], device=device
            )
            dec_out, _ = self.arm1_decoder(
                dec_seq, memory, cond_vec_d, cycle_emb_d, strata_oh_d, causal_mask
            )
            out_t   = dec_out[:, -1, :]
            act_tok = self.act_head(out_t).argmax(-1)  # (B,) 0-indexed
            act_tokens.append(act_tok)

            if t < self.n_slots - 1:
                act_emb_t = self.act_embedding(act_tok)       # (B, d_act)
                slot_next = (
                    self.arm1_slot_proj(act_emb_t).unsqueeze(1)
                    + self.dec_pos_enc[:, t + 1:t + 2, :]
                )
                dec_tokens.append(slot_next)

        return torch.stack(act_tokens, dim=1)  # (B, 48) int64

    # ── Arm 2 helper ─────────────────────────────────────────────────────────

    def _arm2_fuse(self, memory, act_probs, cond_vec, cycle_idx, tgt_strata):
        """
        Per-slot NAT fusion.
        memory:    (B, 49, d_model) — CLS dropped internally
        act_probs: (B, 48, n_act)   — soft probs at train, one-hot at infer
        Returns:   (B, 48, d_model)
        J3: act_probs projected to d_model via arm2_act_proj before concat.
        """
        T         = self.n_slots
        slots_mem = memory[:, 1:, :]                                           # (B, 48, d_model)

        cycle_emb = self.cycle_embedding(cycle_idx)                            # (B, d_cycle)
        strata_oh = F.one_hot(
            (tgt_strata - 1).clamp(0, 2), num_classes=3
        ).float()                                                               # (B, 3)

        cond_b   = cond_vec.unsqueeze(1).expand(-1, T, -1)                    # (B, 48, d_cond)
        cycle_b  = cycle_emb.unsqueeze(1).expand(-1, T, -1)                   # (B, 48, d_cycle)
        strata_b = strata_oh.unsqueeze(1).expand(-1, T, -1)                   # (B, 48, 3)

        # J3: project activity distribution to d_model (detach already on act_probs)
        if hasattr(self, "arm2_act_proj"):
            act_emb = self.arm2_act_proj(act_probs)                            # (B, 48, d_model)
        else:
            act_emb = act_probs                                                 # (B, 48, n_act)

        fused = torch.cat(
            [slots_mem, act_emb, cond_b, cycle_b, strata_b], dim=-1
        )                                                                       # (B, 48, d_arm2_in)
        return self.arm2_proj(fused)                                            # (B, 48, d_model)

    # ── Forward (teacher-forcing, training) ──────────────────────────────────

    def forward(self, batch: dict) -> dict:
        """Full forward with teacher forcing. Arm 1 → Arm 2 (detached)."""
        memory = self._encode(
            batch["act_seq"], batch["aux_seq"],
            batch["cond_vec"], batch["cycle_idx"],
        )
        act_logits = self._arm1_decode_tf(
            batch["dec_act_seq"], batch["tgt_strata"],
            memory, batch["cond_vec"], batch["cycle_idx"],
        )  # (B, 48, n_act)

        act_probs = F.softmax(act_logits.detach(), dim=-1)  # (B, 48, n_act) — no grad to Arm 1
        arm2_feat = self._arm2_fuse(
            memory, act_probs, batch["cond_vec"],
            batch["cycle_idx"], batch["tgt_strata"],
        )  # (B, 48, d_model)

        return {
            "act_logits":  act_logits,
            "home_logits": self.home_head(arm2_feat).squeeze(-1),  # (B, 48)
            "cop_logits":  self.cop_head(arm2_feat),               # (B, 48, 9)
            "aux_logits":  None,
        }

    # ── Inference (AR Arm 1 → NAT Arm 2) ─────────────────────────────────────

    @torch.no_grad()
    def infer(self, act_seq, aux_seq, cond_vec, cycle_idx, tgt_strata,
              apply_safety: bool = True):
        """
        J1 inference: AR activity (Arm 1) then NAT binary heads (Arm 2).

        Returns (gen_act [B,48] int64, gen_home [B,48] float, cop_prob [B,48,9] float).
        apply_safety=True: Spouse cop_prob *= (home_pred > 0.5) clip-only (not masked BCE).
        """
        memory = self._encode(act_seq, aux_seq, cond_vec, cycle_idx)

        act_tokens = self._arm1_generate(memory, cond_vec, cycle_idx, tgt_strata)  # (B, 48)

        act_probs = F.one_hot(act_tokens, num_classes=self.n_act).float()  # (B, 48, n_act)
        arm2_feat = self._arm2_fuse(memory, act_probs, cond_vec, cycle_idx, tgt_strata)

        gen_home = (
            torch.sigmoid(self.home_head(arm2_feat).squeeze(-1)) > 0.5
        ).float()                                                     # (B, 48)
        cop_prob = torch.sigmoid(self.cop_head(arm2_feat))           # (B, 48, 9)

        if apply_safety:
            cop_prob = cop_prob.clone()
            cop_prob[:, :, self.SPOUSE_IDX] *= gen_home  # Spouse clip when not home

        return act_tokens, gen_home, cop_prob
