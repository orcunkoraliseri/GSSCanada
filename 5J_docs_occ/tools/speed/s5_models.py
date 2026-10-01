# -*- coding: utf-8 -*-
"""5J Step 5 part C: the two sequence models (rules R6). Input x [B,192,n_dyn], static st [B,S]; output [B,24,3] (standardised
heating, cooling, equipment of the last 24 hours). Clipping at 0 kWh is done by the caller (train / predict), not here."""
import sys
sys.dont_write_bytecode = True
import torch
import torch.nn as nn
import torch.nn.functional as F

WIN, OUTH = 192, 24


class TCNBlock(nn.Module):
    def __init__(self, ch, dil):
        super().__init__()
        self.dil = dil
        self.ln = nn.LayerNorm(ch)                       # over channels only (keeps the block causal)
        self.conv1 = nn.Conv1d(ch, ch, 3, dilation=dil)
        self.conv2 = nn.Conv1d(ch, ch, 1)
        self.act = nn.GELU()

    def forward(self, x):                                # x [B,T,C]
        h = self.ln(x).transpose(1, 2)
        h = F.pad(h, (2 * self.dil, 0))                  # causal: left padding only
        h = self.conv2(self.act(self.conv1(h)))
        return x + h.transpose(1, 2)


class TCN(nn.Module):
    """Input projection, residual blocks of dilated causal Conv1d (kernel 3, dilation 2**(i mod 8): 1..128 once for 8 blocks,
    twice for 16 blocks; receptive field 511 h > 192), static vector projected and added at every time step, head on the
    last 24 steps."""
    def __init__(self, n_dyn, n_static, width, n_blocks):
        super().__init__()
        self.inp = nn.Linear(n_dyn, width)
        self.stat = nn.Linear(n_static, width)
        self.blocks = nn.ModuleList([TCNBlock(width, 2 ** (i % 8)) for i in range(n_blocks)])
        self.ln = nn.LayerNorm(width)
        self.head = nn.Linear(width, 3)

    def forward(self, x, st):
        h = self.inp(x) + self.stat(st)[:, None, :]
        for b in self.blocks:
            h = b(h)
        return self.head(self.ln(h[:, -OUTH:]))


class TransformerS(nn.Module):
    """Input projection to d_model, learned position embedding (192), static vector as one extra token, encoder layers
    (4 heads, feed-forward 4 x d_model, dropout 0.1, pre-norm), head on the last 24 positions."""
    def __init__(self, n_dyn, n_static, width, n_layers):
        super().__init__()
        self.inp = nn.Linear(n_dyn, width)
        self.pos = nn.Parameter(torch.randn(WIN, width) * 0.02)
        self.stat = nn.Linear(n_static, width)
        layer = nn.TransformerEncoderLayer(width, 4, 4 * width, 0.1, activation="gelu", batch_first=True, norm_first=True)
        self.enc = nn.TransformerEncoder(layer, n_layers, enable_nested_tensor=False)
        self.ln = nn.LayerNorm(width)
        self.head = nn.Linear(width, 3)

    def forward(self, x, st):
        h = self.inp(x) + self.pos[None]
        h = torch.cat([self.stat(st)[:, None, :], h], 1)         # token 0 = static
        h = self.enc(h)
        return self.head(self.ln(h[:, -OUTH:]))


def build_model(cfg, n_dyn, n_static):
    if cfg["family"] == "tcn":
        return TCN(n_dyn, n_static, cfg["width"], cfg["n_layers"])
    if cfg["family"] == "transformer":
        return TransformerS(n_dyn, n_static, cfg["width"], cfg["n_layers"])
    raise ValueError(cfg["family"])
