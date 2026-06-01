"""
04B_model_MAMBA.py — Phase 6 Stage A Trial 7: Selective SSM decoder.

Replaces J3's Arm-1 AR transformer decoder with a simplified selective SSM
(state-space model) block in the Mamba S6 spirit (Gu & Dao 2024). Input-
dependent Δ creates a soft persistence prior — the SSM's discretised time
constant adapts per-slot to favour holding the previous activity unless the
input signal strongly suggests a change. Targets the over-fragmentation
failure mode (157× transition rate).

Real Mamba requires a custom CUDA kernel for the parallel scan. For Stage A
ranking we use a sequential scan in Python — slow but correct, and 48 slots
is small enough that scan time is dominated by encoder compute anyway. If
MAMBA wins, swap in mamba-ssm package's CUDA kernel for Stage C.

Filename begins with a digit — import via importlib.
"""

import importlib
import math
import os
import sys

import torch
import torch.nn as nn
import torch.nn.functional as F

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

_base = importlib.import_module("04B_model")
JSeriesHybrid = _base.JSeriesHybrid

D_STATE = 16        # SSM state dim
EXPAND  = 2         # MLP expansion factor in the Mamba block


class _MambaBlock(nn.Module):
    """One simplified Mamba S6 block. Input (B, T, D) → output (B, T, D).

    Input-dependent Δ, A_log, B, C projected from the input; sequential scan
    over T (Python loop). Δ is computed via softplus to keep step sizes positive.
    """

    def __init__(self, d_model: int, d_state: int = D_STATE, expand: int = EXPAND):
        super().__init__()
        d_inner = d_model * expand
        self.d_model = d_model
        self.d_inner = d_inner
        self.d_state = d_state

        self.in_proj = nn.Linear(d_model, d_inner * 2)
        self.conv1d  = nn.Conv1d(d_inner, d_inner, kernel_size=3, padding=2,
                                  groups=d_inner)
        self.act     = nn.SiLU()

        # x → Δ, B, C projections (input-dependent)
        self.x_proj   = nn.Linear(d_inner, d_state * 2 + d_state)
        self.dt_proj  = nn.Linear(d_state, d_inner)

        # Static A_log = log(-A); A diagonal, init in [1, d_state] range.
        A = torch.arange(1, d_state + 1, dtype=torch.float).unsqueeze(0).expand(d_inner, -1)
        self.A_log = nn.Parameter(torch.log(A))
        self.D     = nn.Parameter(torch.ones(d_inner))

        self.out_proj = nn.Linear(d_inner, d_model)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, T, D = x.shape
        xz = self.in_proj(x)                                            # (B, T, 2*d_inner)
        x_in, z = xz.chunk(2, dim=-1)                                   # each (B, T, d_inner)

        # Causal 1D conv with right-padded then sliced output
        x_conv = self.conv1d(x_in.transpose(1, 2))[:, :, :T].transpose(1, 2)  # (B, T, d_inner)
        x_conv = self.act(x_conv)

        # Project to Δ_raw, B_seq, C_seq
        x_dbc = self.x_proj(x_conv)
        dt_raw, B_seq, C_seq = torch.split(
            x_dbc, [self.d_state, self.d_state, self.d_state], dim=-1
        )
        dt = F.softplus(self.dt_proj(dt_raw))                            # (B, T, d_inner)

        A = -torch.exp(self.A_log)                                       # (d_inner, d_state)

        # Sequential scan (Python loop; correct but slow). For T=48 this is fine.
        h = torch.zeros(B, self.d_inner, self.d_state, device=x.device, dtype=x.dtype)
        ys = []
        for t in range(T):
            dt_t = dt[:, t, :]                                           # (B, d_inner)
            # ΔA  = exp(Δ ⊙ A)  broadcast over (B, d_inner, d_state)
            dA = torch.exp(dt_t.unsqueeze(-1) * A.unsqueeze(0))          # (B, d_inner, d_state)
            dB = dt_t.unsqueeze(-1) * B_seq[:, t, :].unsqueeze(1)        # (B, d_inner, d_state)
            h  = dA * h + dB * x_conv[:, t, :].unsqueeze(-1)             # (B, d_inner, d_state)
            y  = (h * C_seq[:, t, :].unsqueeze(1)).sum(dim=-1)           # (B, d_inner)
            ys.append(y)
        y = torch.stack(ys, dim=1)                                       # (B, T, d_inner)
        y = y + self.D.view(1, 1, -1) * x_conv                            # residual D path

        y = y * self.act(z)                                              # gated output
        return self.out_proj(y)                                          # (B, T, d_model)


class MAMBAHybrid(JSeriesHybrid):
    """J3 encoder + Arm-2 binaries; new Arm-1 = Mamba SSM stack."""

    def __init__(self, config: dict):
        cfg = dict(config)
        cfg["model_type"] = "J3"
        super().__init__(cfg)
        self._mtype = "MAMBA"

        d_model = config["d_model"]
        n_act   = config.get("n_activity_classes", 14)

        n_mamba_layers = 2   # depth small enough that scan stays cheap
        self.mamba_blocks = nn.ModuleList([
            _MambaBlock(d_model) for _ in range(n_mamba_layers)
        ])
        self.mamba_norm = nn.LayerNorm(d_model)
        self.mamba_act_head = nn.Linear(d_model, n_act)
        nn.init.xavier_uniform_(self.mamba_act_head.weight)
        nn.init.zeros_(self.mamba_act_head.bias)

    def _activity_logits(self, memory: torch.Tensor) -> torch.Tensor:
        """memory: (B, 49, d_model). Returns (B, 48, n_act)."""
        x = memory[:, 1:, :]
        for blk in self.mamba_blocks:
            x = x + blk(x)
        x = self.mamba_norm(x)
        return self.mamba_act_head(x)

    def forward(self, batch: dict) -> dict:
        memory = self._encode(
            batch["act_seq"], batch["aux_seq"],
            batch["cond_vec"], batch["cycle_idx"],
            tgt_strata=batch.get("tgt_strata"),
        )

        act_logits = self._activity_logits(memory)

        act_probs = F.softmax(act_logits.detach(), dim=-1)
        arm2_feat = self._arm2_fuse(
            memory, act_probs, batch["cond_vec"],
            batch["cycle_idx"], batch["tgt_strata"],
        )
        home_logits = self.home_head(arm2_feat).squeeze(-1)
        cop_logits  = self.cop_head(arm2_feat)

        return {
            "act_logits":  act_logits,
            "home_logits": home_logits,
            "cop_logits":  cop_logits,
            "aux_logits":  None,
        }

    @torch.no_grad()
    def infer(self, act_seq, aux_seq, cond_vec, cycle_idx, tgt_strata,
              apply_safety: bool = True):
        memory = self._encode(act_seq, aux_seq, cond_vec, cycle_idx,
                              tgt_strata=tgt_strata)
        act_logits = self._activity_logits(memory)
        gen_act = act_logits.argmax(dim=-1)

        act_probs = F.one_hot(gen_act, num_classes=self.n_act).float()
        arm2_feat = self._arm2_fuse(memory, act_probs, cond_vec, cycle_idx, tgt_strata)
        home_logits = self.home_head(arm2_feat).squeeze(-1)
        gen_home = (torch.sigmoid(home_logits) > 0.5).float()
        cop_prob = torch.sigmoid(self.cop_head(arm2_feat))

        if apply_safety:
            cop_prob = cop_prob.clone()
            cop_prob[:, :, self.SPOUSE_IDX] *= gen_home

        return gen_act, gen_home, cop_prob
