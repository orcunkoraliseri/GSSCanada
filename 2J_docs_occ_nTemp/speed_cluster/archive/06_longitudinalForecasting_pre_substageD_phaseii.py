"""
06_longitudinalForecasting.py
Step 6 — Model 2: Longitudinal Forecasting (2005–2030)

Four-stage progressive fine-tuning + forecasting Transformer trained on
augmented GSS diary data across four cycles (2005/2010/2015/2022).

IMPORT NOTE: The task spec references eSim_dynamicML_mHead.py for Model 1
decoder import. Code inspection confirms that file is a TensorFlow CVAE for
Census demographic modeling and is not the diary Transformer. The PyTorch
ConditionalTransformer (Model 1) lives in 04B_model.py and is imported here
via importlib (filename starts with digit). This deviation is documented in
the Progress Log.

Usage:
    py 06_longitudinalForecasting.py --stage A --smoke   # local smoke test
    python 06_longitudinalForecasting.py --stage all     # full HPC run (14 hrs)
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from scipy.spatial.distance import jensenshannon
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, Dataset

warnings.filterwarnings("ignore", category=UserWarning)

# ── Paths ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR   = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[1]
MODEL_SRC    = PROJECT_ROOT / "2J_docs_occ_nTemp"

DATA_PATH    = MODEL_SRC / "outputs_step4" / "augmented_diaries.csv"
FEAT_CFG_PATH = MODEL_SRC / "outputs_step4" / "step4_feature_config.json"
MODELS_DIR   = PROJECT_ROOT / "0_Occupancy" / "Models_Step6"
FORECAST_DIR = PROJECT_ROOT / "0_Occupancy" / "Outputs_21CEN22GSS" / "forecast_2030"
INPUTS_DIR   = PROJECT_ROOT / "0_Occupancy" / "Inputs_Step6"

for _d in (MODELS_DIR, FORECAST_DIR, INPUTS_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# ── Import ConditionalTransformer from 04B_model.py via importlib ─────────────
# 04B_model.py starts with a digit so plain import fails; importlib required.
sys.path.insert(0, str(MODEL_SRC))
_model_mod         = importlib.import_module("04B_model")
ConditionalTransformer = _model_mod.ConditionalTransformer
DEFAULT_CONFIG     = _model_mod.DEFAULT_CONFIG
TEST_CONFIG        = _model_mod.TEST_CONFIG

# ── Feature config ─────────────────────────────────────────────────────────────
with open(FEAT_CFG_PATH) as _f:
    _cfg = json.load(_f)

D_COND       = _cfg["d_cond"]             # 77
CYCLE_MAP    = {int(k): v for k, v in _cfg["cycle_map"].items()}
COP_PREFIXES = _cfg["cop_col_names"]      # ["Alone","Spouse","Children",...]
FEAT_PARTS   = _cfg["feature_parts"]
CYCLE_YEARS  = sorted(CYCLE_MAP.keys())   # [2005, 2010, 2015, 2022]

ACT_COLS = [f"act30_{i:03d}" for i in range(1, 49)]
HOM_COLS = [f"hom30_{i:03d}" for i in range(1, 49)]
# COP: config prefix → CSV column name (prefix + "30")
COP_CSV_PREFIXES = [p + "30" for p in COP_PREFIXES]
COP_COLS = [[f"{px}_{i:03d}" for i in range(1, 49)] for px in COP_CSV_PREFIXES]

N_SLOTS = 48
N_ACT   = 14
N_COP   = 9


# ── Conditioning vector builder ────────────────────────────────────────────────

def build_cond_vec(df: pd.DataFrame) -> np.ndarray:
    """Build (N, D_COND=77) conditioning matrix from demographic columns."""
    parts = []
    for feat_name, spec in FEAT_PARTS.items():
        t = spec["type"]
        if t == "one-hot":
            n = spec["n_cats"]
            ohe = np.zeros((len(df), n), dtype=np.float32)
            if feat_name in df.columns:
                cats = spec["categories"]
                for i, v in enumerate(df[feat_name].astype(str)):
                    idx = cats.get(v, cats.get("-1", 0))
                    ohe[i, idx] = 1.0
            parts.append(ohe)
        elif t == "continuous":
            mu, sigma = spec["mean"], spec["std"]
            if feat_name in df.columns:
                vals = df[feat_name].astype(float).fillna(mu)
                norm = ((vals - mu) / (sigma + 1e-8)).values.reshape(-1, 1)
            else:
                norm = np.zeros((len(df), 1), dtype=np.float32)
            parts.append(norm.astype(np.float32))
        elif t == "binary":
            if feat_name in df.columns:
                vals = df[feat_name].fillna(0).astype(float).values.reshape(-1, 1)
            else:
                vals = np.zeros((len(df), 1), dtype=np.float32)
            parts.append(vals.astype(np.float32))

    cond = np.concatenate(parts, axis=1)
    # Enforce exact d_cond dimension
    if cond.shape[1] < D_COND:
        pad = np.zeros((len(cond), D_COND - cond.shape[1]), dtype=np.float32)
        cond = np.concatenate([cond, pad], axis=1)
    return cond[:, :D_COND]


# ── Tensor extraction from a DataFrame slice ──────────────────────────────────

def df_to_tensors(df: pd.DataFrame) -> dict:
    """Convert a DataFrame slice to the model-ready tensor dict."""
    df = df.reset_index(drop=True)
    act_arr  = (df[ACT_COLS].values.astype(np.int64) - 1).clip(0, N_ACT - 1)
    hom_arr  = df[HOM_COLS].values.astype(np.float32)
    cop_arr  = np.stack(
        [df[cols].fillna(0.0).values.astype(np.float32) for cols in COP_COLS],
        axis=2
    )  # (N, 48, 9)
    aux_arr  = np.concatenate([hom_arr[:, :, None], cop_arr], axis=2)  # (N, 48, 10)
    cop_avail = np.stack(
        [df[cols].notna().values.astype(np.float32) for cols in COP_COLS],
        axis=2
    )  # (N, 48, 9)
    cond     = build_cond_vec(df)
    cycle_idx = df["CYCLE_YEAR"].map(CYCLE_MAP).fillna(0).values.astype(np.int64)
    cycle_yr  = df["CYCLE_YEAR"].values.astype(np.int64)
    strata    = df["DDAY_STRATA"].values.astype(np.int64)

    return {
        "act_t":    torch.from_numpy(act_arr),
        "aux_t":    torch.from_numpy(aux_arr),
        "avail_t":  torch.from_numpy(cop_avail),
        "cond_t":   torch.from_numpy(cond),
        "cyc_t":    torch.from_numpy(cycle_idx),
        "yr_t":     torch.from_numpy(cycle_yr),
        "str_t":    torch.from_numpy(strata),
    }


# ── Dataset ────────────────────────────────────────────────────────────────────

class DiaryDataset(Dataset):
    """
    Cross-strata pairs from the same occID (within one cycle).
    Each item is (source_row_idx, target_row_idx) with src ≠ tgt stratum.
    """

    def __init__(self, df: pd.DataFrame):
        tensors     = df_to_tensors(df)
        self.act_t  = tensors["act_t"]
        self.aux_t  = tensors["aux_t"]
        self.avail_t = tensors["avail_t"]
        self.cond_t = tensors["cond_t"]
        self.cyc_t  = tensors["cyc_t"]
        self.yr_t   = tensors["yr_t"]
        self.str_t  = tensors["str_t"]

        df = df.reset_index(drop=True)
        self.pairs: list[tuple[int, int]] = []
        for _, grp in df.groupby("occID"):
            idxs = list(grp.index)
            if len(idxs) < 2:
                # self-pair for single-stratum respondents
                self.pairs.append((idxs[0], idxs[0]))
            else:
                for si in range(len(idxs)):
                    for ti in range(len(idxs)):
                        if si != ti:
                            self.pairs.append((idxs[si], idxs[ti]))

    def __len__(self) -> int:
        return len(self.pairs)

    def __getitem__(self, i: int) -> dict:
        s, t = self.pairs[i]
        return {
            "act_seq":       self.act_t[s],
            "aux_seq":       self.aux_t[s],
            "cond_vec":      self.cond_t[s],
            "cycle_idx":     self.cyc_t[s],
            "cycle_year":    self.yr_t[s],
            "dec_act_seq":   self.act_t[t],
            "dec_aux_seq":   self.aux_t[t],
            "dec_cop_avail": self.avail_t[t],
            "tgt_strata":    self.str_t[t],
        }


# ── TrendEncoder ──────────────────────────────────────────────────────────────

class TrendEncoder(nn.Module):
    """
    Small Transformer encoder for temporal activity drift.

    Input:  3-token sequence of flattened DRIFT_MATRIXes
            drift_dim = 14 activities × 3 strata = 42 per matrix
    Output: projected 2030 activity distribution per stratum (drift_dim)

    Architecture: d_model=64, 2 layers, 4 heads.
    """

    def __init__(self, drift_dim: int, d_model: int = 64,
                 n_heads: int = 4, n_layers: int = 2) -> None:
        super().__init__()
        self.proj_in  = nn.Linear(drift_dim, d_model)
        enc_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=n_heads,
            dim_feedforward=d_model * 4,
            dropout=0.1, activation="gelu", batch_first=True,
        )
        self.encoder  = nn.TransformerEncoder(
            enc_layer, num_layers=n_layers, norm=nn.LayerNorm(d_model)
        )
        self.proj_out = nn.Linear(d_model, drift_dim)

    def forward(self, drift_seq: torch.Tensor) -> torch.Tensor:
        """
        drift_seq: (B, 3, drift_dim)
        Returns:   (B, drift_dim) — 2030-projected activity distribution
        """
        x = self.proj_in(drift_seq)       # (B, 3, d_model)
        x = self.encoder(x)               # (B, 3, d_model)
        return self.proj_out(x[:, -1, :]) # last token → 2030 projection


# ── Drift vector loader ───────────────────────────────────────────────────────

def _load_drift_vec(path: Path) -> torch.Tensor:
    """Load DRIFT_MATRIX CSV; sort by (strata, activity); return obs_proportion as (42,) float32 tensor."""
    dm = pd.read_csv(path)
    dm = dm.sort_values(["strata", "activity"]).reset_index(drop=True)
    return torch.tensor(dm["obs_proportion"].values, dtype=torch.float32)


# ── JS divergence utilities ────────────────────────────────────────────────────

def _act_dist(arr: np.ndarray) -> np.ndarray:
    """Flatten int activity array → (14,) probability vector."""
    counts = np.bincount(arr.flatten(), minlength=N_ACT).astype(np.float64)
    return counts / max(counts.sum(), 1)


def compute_drift_matrix(
    model:      nn.Module,
    cycle_df:   pd.DataFrame,
    device:     torch.device,
) -> pd.DataFrame:
    """
    Compute JS divergence per {14 activities × 3 DDAY_STRATA} between
    model-predicted and observed activity distributions in cycle_df.

    The model uses each row as both encoder input and decoder query
    (self-reconstruction with teacher forcing). Predicted logits capture
    what the model assigns as activity probability given its learned weights.

    Returns DataFrame: [activity, strata, obs_proportion, pred_proportion, js_divergence]
    """
    model.eval()
    records = []
    BS = 256

    for strata_val in [1, 2, 3]:
        sub = cycle_df[cycle_df["DDAY_STRATA"] == strata_val].reset_index(drop=True)
        if len(sub) == 0:
            continue

        tensors = df_to_tensors(sub)
        act_t   = tensors["act_t"]
        aux_t   = tensors["aux_t"]
        cond_t  = tensors["cond_t"]
        cyc_t   = tensors["cyc_t"]
        str_t   = tensors["str_t"]

        obs_dist  = _act_dist(act_t.numpy())
        pred_cnts = np.zeros(N_ACT, dtype=np.float64)

        with torch.no_grad():
            for b0 in range(0, len(sub), BS):
                b1 = min(b0 + BS, len(sub))
                batch = {
                    "act_seq":     act_t[b0:b1].to(device),
                    "aux_seq":     aux_t[b0:b1].to(device),
                    "cond_vec":    cond_t[b0:b1].to(device),
                    "cycle_idx":   cyc_t[b0:b1].to(device),
                    "dec_act_seq": act_t[b0:b1].to(device),
                    "dec_aux_seq": aux_t[b0:b1].to(device),
                    "tgt_strata":  str_t[b0:b1].to(device),
                }
                out = model(batch)
                preds = out["act_logits"].argmax(dim=-1).cpu().numpy()
                cnts  = np.bincount(preds.flatten(), minlength=N_ACT)
                pred_cnts += cnts

        pred_dist = pred_cnts / max(pred_cnts.sum(), 1)
        eps       = 1e-10

        for act_idx in range(N_ACT):
            p, q = float(obs_dist[act_idx]), float(pred_dist[act_idx])
            m = (p + q) / 2.0
            js = 0.0
            if m > 0:
                if p > 0:
                    js += 0.5 * p * np.log(p / m)
                if q > 0:
                    js += 0.5 * q * np.log(q / m)
            records.append({
                "activity":        act_idx + 1,
                "strata":          strata_val,
                "obs_proportion":  round(p, 6),
                "pred_proportion": round(q, 6),
                "js_divergence":   round(max(js, 0.0), 6),
            })

    return pd.DataFrame(records)


# ── Training loop helpers ──────────────────────────────────────────────────────

def _train_one_epoch(model, loader, optimizer, device) -> float:
    model.train()
    total, n = 0.0, 0
    for batch in loader:
        batch = {k: v.to(device) for k, v in batch.items()}
        out   = model(batch)
        act_loss  = F.cross_entropy(
            out["act_logits"].reshape(-1, N_ACT),
            batch["dec_act_seq"].reshape(-1),
        )
        home_loss = F.binary_cross_entropy_with_logits(
            out["home_logits"],
            batch["dec_aux_seq"][:, :, 0].float(),
        )
        cop_loss  = F.binary_cross_entropy_with_logits(
            out["cop_logits"],
            batch["dec_aux_seq"][:, :, 1:].float(),
        )
        loss = act_loss + 0.5 * home_loss + 0.3 * cop_loss
        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        total += loss.item()
        n     += 1
    return total / max(n, 1)


def _train_one_epoch_weighted(
    model: nn.Module,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
    recency_weights: dict,
    hom_weight_2022: float = 1.0,
) -> float:
    """One training epoch applying per-sample recency scalar multiplier on act_loss.
    hom_weight_2022 > 1.0 up-weights home_loss for 2022 rows to amplify AT_HOME signal."""
    model.train()
    total, n = 0.0, 0
    for batch in loader:
        batch = {k: v.to(device) for k, v in batch.items()}
        out   = model(batch)
        B, T  = batch["dec_act_seq"].shape

        w = torch.tensor(
            [recency_weights.get(int(yr.item()), 1.0) for yr in batch["cycle_year"]],
            dtype=torch.float32, device=device,
        )  # (B,)
        act_loss = (
            F.cross_entropy(
                out["act_logits"].reshape(B * T, N_ACT),
                batch["dec_act_seq"].reshape(B * T),
                reduction="none",
            ).reshape(B, T).mean(dim=1) * w
        ).mean()

        home_targets = batch["dec_aux_seq"][:, :, 0].float()
        if hom_weight_2022 != 1.0:
            home_raw = F.binary_cross_entropy_with_logits(
                out["home_logits"], home_targets, reduction="none"
            ).mean(dim=1)  # (B,)
            hom_w = torch.where(
                batch["cycle_year"] == 2022,
                torch.full_like(home_raw, hom_weight_2022),
                torch.ones_like(home_raw),
            )
            home_loss = (home_raw * hom_w).mean()
        else:
            home_loss = F.binary_cross_entropy_with_logits(
                out["home_logits"], home_targets
            )

        cop_loss  = F.binary_cross_entropy_with_logits(
            out["cop_logits"], batch["dec_aux_seq"][:, :, 1:].float()
        )
        loss = act_loss + 0.5 * home_loss + 0.3 * cop_loss
        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        total += loss.item()
        n     += 1
    return total / max(n, 1)


def _val_js(model, loader, device) -> float:
    model.eval()
    pred_all, true_all = [], []
    with torch.no_grad():
        for batch in loader:
            batch = {k: v.to(device) for k, v in batch.items()}
            out   = model(batch)
            pred_all.append(out["act_logits"].argmax(-1).cpu().numpy().flatten())
            true_all.append(batch["dec_act_seq"].cpu().numpy().flatten())
    p   = np.bincount(np.concatenate(pred_all), minlength=N_ACT).astype(np.float64)
    q   = np.bincount(np.concatenate(true_all), minlength=N_ACT).astype(np.float64)
    eps = 1e-10
    p  /= max(p.sum(), 1)
    q  /= max(q.sum(), 1)
    return float(jensenshannon(p + eps, q + eps))


def _val_js_by_strata(model: nn.Module, loader: DataLoader, device: torch.device) -> dict:
    """Compute JS divergence per DDAY_STRATA; returns {1: js_wd, 2: js_sat, 3: js_sun}."""
    model.eval()
    preds: dict = {1: [], 2: [], 3: []}
    trues: dict = {1: [], 2: [], 3: []}
    with torch.no_grad():
        for batch in loader:
            batch = {k: v.to(device) for k, v in batch.items()}
            out   = model(batch)
            pred  = out["act_logits"].argmax(-1).cpu().numpy()
            true  = batch["dec_act_seq"].cpu().numpy()
            st    = batch["tgt_strata"].cpu().numpy()
            for b in range(len(st)):
                s = int(st[b])
                if s in preds:
                    preds[s].extend(pred[b].flatten().tolist())
                    trues[s].extend(true[b].flatten().tolist())
    eps = 1e-10
    result = {}
    for s in [1, 2, 3]:
        p = np.bincount(preds[s], minlength=N_ACT).astype(np.float64) if preds[s] else np.zeros(N_ACT)
        q = np.bincount(trues[s], minlength=N_ACT).astype(np.float64) if trues[s] else np.zeros(N_ACT)
        p /= max(p.sum(), 1)
        q /= max(q.sum(), 1)
        result[s] = float(jensenshannon(p + eps, q + eps))
    return result


def _at_home_rate_wd(
    model:  nn.Module,
    df:     pd.DataFrame,
    device: torch.device,
) -> tuple:
    """
    Returns (obs_wd_at_home_rate, pred_wd_at_home_rate) for WD rows (DDAY_STRATA==1).
    AT_HOME rate = mean of hom30 columns across all rows × 48 slots.
    Predicted rate uses sigmoid(home_logits) in self-reconstruction mode.
    Replaces the mean-JS COVID signal gate, which measured per-activity marginal
    divergence and was insensitive to the AT_HOME joint aggregate shift.
    """
    model.eval()
    wd_df = df[df["DDAY_STRATA"] == 1].reset_index(drop=True)
    if len(wd_df) == 0:
        return 0.0, 0.0
    tensors  = df_to_tensors(wd_df)
    act_t    = tensors["act_t"]
    aux_t    = tensors["aux_t"]
    cond_t   = tensors["cond_t"]
    cyc_t    = tensors["cyc_t"]
    str_t    = tensors["str_t"]
    obs_rate = float(aux_t[:, :, 0].numpy().mean())
    pred_hom: list = []
    BS = 256
    with torch.no_grad():
        for b0 in range(0, len(wd_df), BS):
            b1 = min(b0 + BS, len(wd_df))
            batch = {
                "act_seq":     act_t[b0:b1].to(device),
                "aux_seq":     aux_t[b0:b1].to(device),
                "cond_vec":    cond_t[b0:b1].to(device),
                "cycle_idx":   cyc_t[b0:b1].to(device),
                "dec_act_seq": act_t[b0:b1].to(device),
                "dec_aux_seq": aux_t[b0:b1].to(device),
                "tgt_strata":  str_t[b0:b1].to(device),
            }
            out = model(batch)
            pred_hom.append(torch.sigmoid(out["home_logits"]).cpu().numpy())
    pred_rate = float(np.concatenate(pred_hom, axis=0).mean())
    return obs_rate, pred_rate


# ── Sub-stage A — Base Training on 2005 ───────────────────────────────────────

def run_substage_a(args, df: pd.DataFrame, device: torch.device) -> None:
    print("\n" + "=" * 60)
    print("SUB-STAGE A — Base Training on 2005 Data")
    print("=" * 60)

    df2005 = df[df["CYCLE_YEAR"] == 2005].copy()
    max_epochs = 3 if args.smoke else 100
    if args.smoke:
        df2005 = df2005.sample(frac=0.05, random_state=42)
        print(f"[SMOKE] {len(df2005):,} rows, max {max_epochs} epochs")
    else:
        print(f"Using {len(df2005):,} 2005 rows, max {max_epochs} epochs")

    # 70/20/10 split stratified by DDAY_STRATA
    train_df, temp_df = train_test_split(
        df2005, test_size=0.30, stratify=df2005["DDAY_STRATA"], random_state=42
    )
    val_df, test_df = train_test_split(
        temp_df, test_size=0.333, stratify=temp_df["DDAY_STRATA"], random_state=42
    )
    print(f"Split: train={len(train_df):,}  val={len(val_df):,}  test={len(test_df):,}")

    cfg = TEST_CONFIG.copy() if args.smoke else DEFAULT_CONFIG.copy()
    cfg["d_cond"] = D_COND
    model = ConditionalTransformer(cfg).to(device)
    n_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Model params: {n_params:,}  d_model={cfg['d_model']}")

    bs           = 16 if args.smoke else 256
    train_ds     = DiaryDataset(train_df)
    val_ds       = DiaryDataset(val_df)
    train_loader = DataLoader(train_ds, batch_size=bs, shuffle=True,  num_workers=0, drop_last=True)
    val_loader   = DataLoader(val_ds,   batch_size=bs, shuffle=False, num_workers=0)

    optimizer  = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-4)
    patience   = 5
    best_js    = float("inf")
    best_state = None
    wait       = 0

    print(f"\n{'Epoch':>6}  {'train_loss':>12}  {'val_JS':>8}")
    for epoch in range(1, max_epochs + 1):
        train_loss = _train_one_epoch(model, train_loader, optimizer, device)
        val_js     = _val_js(model, val_loader, device)
        print(f"{epoch:6d}  {train_loss:12.4f}  {val_js:8.4f}")

        if val_js < best_js:
            best_js    = val_js
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
            wait       = 0
        else:
            wait += 1
            if wait >= patience:
                print(f"  Early stop at epoch {epoch} (patience={patience})")
                break

    if best_state is not None:
        model.load_state_dict(best_state)

    ckpt_path = MODELS_DIR / "W_2005.pt"
    torch.save({"model_state": model.state_dict(), "config": cfg, "val_js": best_js}, ckpt_path)
    print(f"\nSaved {ckpt_path}  (best val JS={best_js:.4f})")

    # DRIFT_MATRIX_0510: apply W_2005 to 2010 held-out
    print("\nComputing DRIFT_MATRIX_0510 on 2010 data ...")
    df2010 = df[df["CYCLE_YEAR"] == 2010].copy()
    if args.smoke:
        df2010 = df2010.sample(frac=0.05, random_state=42)

    drift_df   = compute_drift_matrix(model, df2010, device)
    drift_path = FORECAST_DIR / "DRIFT_MATRIX_0510.csv"
    drift_df.to_csv(drift_path, index=False)
    print(f"Saved {drift_path}  ({len(drift_df)} rows)")

    n_sig = (drift_df["js_divergence"] > 0.01).sum()
    print(f"Activities with drift > 0.01: {n_sig} / {len(drift_df)}")
    print(f"Mean JS (all activities × strata): {drift_df['js_divergence'].mean():.4f}")
    print("\nSub-stage A complete.")


# ── Sub-stage B — Progressive Fine-Tuning (3 Phases) ─────────────────────────

def run_substage_b(args, df: pd.DataFrame, device: torch.device) -> None:
    print("\n" + "=" * 60)
    print("SUB-STAGE B — Progressive Fine-Tuning (3 Phases)")
    print("=" * 60)

    max_epochs = 3 if args.smoke else 100
    bs         = 16 if args.smoke else 256
    patience   = 5

    # ── Internal helpers ────────────────────────────────────────────────

    def _load_ckpt(path: Path, label: str):
        if not path.exists():
            raise FileNotFoundError(
                f"{label} not found at {path}. Prior sub-stage must complete first."
            )
        ckpt = torch.load(path, map_location=device)
        m    = ConditionalTransformer(ckpt["config"]).to(device)
        m.load_state_dict(ckpt["model_state"])
        print(f"Loaded {label} (val_JS={ckpt['val_js']:.4f})")
        return m, ckpt["config"]

    def _build_pool(cycles: list) -> pd.DataFrame:
        sub = df[df["CYCLE_YEAR"].isin(cycles)].copy()
        if args.smoke:
            sub = (
                sub.groupby("CYCLE_YEAR", group_keys=False)
                   .apply(lambda x: x.sample(frac=0.05, random_state=42))
                   .reset_index(drop=True)
            )
        return sub

    def _split_70_20(pool: pd.DataFrame):
        tr, temp = train_test_split(
            pool, test_size=0.30, stratify=pool["DDAY_STRATA"], random_state=42
        )
        va, _ = train_test_split(
            temp, test_size=0.333, stratify=temp["DDAY_STRATA"], random_state=42
        )
        return tr, va

    def _fine_tune(model: nn.Module, train_df, val_df, rw: dict, hom_weight_2022: float = 1.0):
        train_ds     = DiaryDataset(train_df)
        val_ds       = DiaryDataset(val_df)
        train_loader = DataLoader(train_ds, batch_size=bs, shuffle=True,  num_workers=0, drop_last=True)
        val_loader   = DataLoader(val_ds,   batch_size=bs, shuffle=False, num_workers=0)
        optimizer    = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-4)
        best_js, best_state, wait = float("inf"), None, 0
        print(f"  {'Epoch':>6}  {'train_loss':>12}  {'val_JS':>8}")
        for epoch in range(1, max_epochs + 1):
            tr_loss = _train_one_epoch_weighted(
                model, train_loader, optimizer, device, rw, hom_weight_2022
            )
            val_js  = _val_js(model, val_loader, device)
            print(f"  {epoch:6d}  {tr_loss:12.4f}  {val_js:8.4f}")
            if val_js < best_js:
                best_js    = val_js
                best_state = {k: v.clone() for k, v in model.state_dict().items()}
                wait       = 0
            else:
                wait += 1
                if wait >= patience:
                    print(f"  Early stop at epoch {epoch} (patience={patience})")
                    break
        if best_state is not None:
            model.load_state_dict(best_state)
        return model, best_js

    def _tft_report(model: nn.Module, tft_df: pd.DataFrame, tag: str, gate: float) -> dict:
        eval_df = (
            tft_df.sample(frac=0.05, random_state=42).reset_index(drop=True)
            if args.smoke else tft_df
        )
        tft_ds  = DiaryDataset(eval_df)
        tft_ldr = DataLoader(tft_ds, batch_size=bs, shuffle=False, num_workers=0)
        js      = _val_js_by_strata(model, tft_ldr, device)
        wd, sat, sun = js[1], js[2], js[3]
        print(f"[{tag}] JS_WD={wd:.4f} JS_Sat={sat:.4f} JS_Sun={sun:.4f}")
        passed = wd < gate and sat < gate and sun < gate
        print(f"  Gate < {gate}: {'PASS' if passed else 'FAIL'}")
        return js

    # ────────────────────────────────────────────────────────────────────
    # Phase 2: 2005+2010 → W_2010_ft
    # ────────────────────────────────────────────────────────────────────
    print("\n--- Phase 2: 2005+2010 → W_2010_ft ---")
    model, cfg = _load_ckpt(MODELS_DIR / "W_2005.pt", "W_2005.pt")

    pool2       = _build_pool([2005, 2010])
    tr2, va2    = _split_70_20(pool2)
    print(f"  train={len(tr2):,}  val={len(va2):,}")
    model, bj2  = _fine_tune(model, tr2, va2, {2005: 0.10, 2010: 0.20})

    df_tft2015  = df[df["CYCLE_YEAR"] == 2015].reset_index(drop=True)
    _tft_report(model, df_tft2015, "TRUE_FUTURE_TEST_2015", gate=0.20)

    print("\nComputing DRIFT_MATRIX_1015 on 2015 data ...")
    dm_src = df_tft2015.sample(frac=0.05, random_state=42).reset_index(drop=True) if args.smoke else df_tft2015
    drift_1015 = compute_drift_matrix(model, dm_src, device)
    drift_1015.to_csv(FORECAST_DIR / "DRIFT_MATRIX_1015.csv", index=False)
    print(f"Saved DRIFT_MATRIX_1015.csv ({len(drift_1015)} rows)")

    torch.save({"model_state": model.state_dict(), "config": cfg, "val_js": bj2},
               MODELS_DIR / "W_2010_ft.pt")
    print(f"Saved W_2010_ft.pt (val_JS={bj2:.4f})")

    # ────────────────────────────────────────────────────────────────────
    # Phase 3: 2005+2010+2015 → W_2015_ft
    # ────────────────────────────────────────────────────────────────────
    print("\n--- Phase 3: 2005+2010+2015 → W_2015_ft ---")
    model, cfg = _load_ckpt(MODELS_DIR / "W_2010_ft.pt", "W_2010_ft.pt")

    pool3       = _build_pool([2005, 2010, 2015])
    tr3, va3    = _split_70_20(pool3)
    print(f"  train={len(tr3):,}  val={len(va3):,}")
    model, bj3  = _fine_tune(model, tr3, va3, {2005: 0.10, 2010: 0.20, 2015: 0.30})

    df_tft2022  = df[df["CYCLE_YEAR"] == 2022].reset_index(drop=True)
    _tft_report(model, df_tft2022, "TRUE_FUTURE_TEST_2022", gate=0.20)

    print("\nComputing DRIFT_MATRIX_1522 on 2022 data ...")
    dm_src2 = df_tft2022.sample(frac=0.05, random_state=42).reset_index(drop=True) if args.smoke else df_tft2022
    drift_1522 = compute_drift_matrix(model, dm_src2, device)
    drift_1522.to_csv(FORECAST_DIR / "DRIFT_MATRIX_1522.csv", index=False)
    print(f"Saved DRIFT_MATRIX_1522.csv ({len(drift_1522)} rows)")

    # AT_HOME aggregate check (replaces mean-JS COVID signal gate).
    # The prior gate compared mean per-activity WD JS across DRIFT matrices, which is
    # insensitive to the joint AT_HOME aggregate shift. This check directly measures
    # whether the model's predicted WD AT_HOME rate for 2022 inputs tracks the observed
    # 70.6% rate vs the 2015 baseline (~64.5%). If suppression > 5pp, Phase 4 will
    # apply hom_weight_2022=2.0 to amplify the hom30 loss for 2022 rows.
    print("\nAT_HOME aggregate check (2015 vs 2022 WD) ...")
    at_src_2015 = df[df["CYCLE_YEAR"] == 2015].reset_index(drop=True)
    at_src_2022 = df_tft2022
    if args.smoke:
        at_src_2015 = at_src_2015.sample(frac=0.05, random_state=42)
        at_src_2022 = at_src_2022.sample(frac=0.05, random_state=42)
    obs_2015, pred_2015 = _at_home_rate_wd(model, at_src_2015, device)
    obs_2022, pred_2022 = _at_home_rate_wd(model, at_src_2022, device)
    obs_gap  = obs_2022  - obs_2015
    pred_gap = pred_2022 - pred_2015
    suppress = (obs_2022 - pred_2022) > 0.05
    print(f"[AT_HOME_CHECK] obs_2015_wd={obs_2015:.3f}  pred_2015_wd={pred_2015:.3f}")
    print(f"[AT_HOME_CHECK] obs_2022_wd={obs_2022:.3f}  pred_2022_wd={pred_2022:.3f}")
    print(f"[AT_HOME_CHECK] obs_gap={obs_gap * 100:+.1f}pp  pred_gap={pred_gap * 100:+.1f}pp")
    print(f"[AT_HOME_CHECK] {'PASS' if not suppress else 'FAIL'} — "
          f"suppression={(obs_2022 - pred_2022) * 100:.1f}pp (threshold <=5pp)")
    hom_boost = 2.0 if suppress else 1.0
    if suppress:
        print(f"  AT_HOME signal suppressed — Phase 4 will use hom_weight_2022={hom_boost}.")

    torch.save({"model_state": model.state_dict(), "config": cfg, "val_js": bj3},
               MODELS_DIR / "W_2015_ft.pt")
    print(f"Saved W_2015_ft.pt (val_JS={bj3:.4f})")

    # ────────────────────────────────────────────────────────────────────
    # Phase 4: all 4 cycles → W_2022_ft
    # ────────────────────────────────────────────────────────────────────
    print("\n--- Phase 4: all 4 cycles → W_2022_ft ---")
    if hom_boost != 1.0:
        print(f"  hom_weight_2022={hom_boost} active (AT_HOME suppression detected in Phase 3)")
    model, cfg = _load_ckpt(MODELS_DIR / "W_2015_ft.pt", "W_2015_ft.pt")

    pool4       = _build_pool([2005, 2010, 2015, 2022])
    tr4, va4    = _split_70_20(pool4)
    print(f"  train={len(tr4):,}  val={len(va4):,}")
    model, bj4  = _fine_tune(
        model, tr4, va4,
        {2005: 0.10, 2010: 0.20, 2015: 0.30, 2022: 0.40},
        hom_weight_2022=hom_boost,
    )

    # Post-Phase 4 AT_HOME verification
    print("\nAT_HOME verification on W_2022_ft ...")
    at_v2022 = df[df["CYCLE_YEAR"] == 2022].reset_index(drop=True)
    if args.smoke:
        at_v2022 = at_v2022.sample(frac=0.05, random_state=42)
    obs_v, pred_v = _at_home_rate_wd(model, at_v2022, device)
    suppress_v    = (obs_v - pred_v) > 0.05
    print(f"[AT_HOME_FINAL] obs_2022_wd={obs_v:.3f}  pred_2022_wd={pred_v:.3f}")
    print(f"[AT_HOME_FINAL] {'PASS' if not suppress_v else 'FAIL'} — "
          f"suppression={(obs_v - pred_v) * 100:.1f}pp (threshold <=5pp)")

    torch.save({"model_state": model.state_dict(), "config": cfg, "val_js": bj4},
               MODELS_DIR / "W_2022_ft.pt")
    print(f"Saved W_2022_ft.pt (val_JS={bj4:.4f})")
    print(f"\n[SUBSTAGE_B_COMPLETE] W_2022_ft val_JS={bj4:.4f}")


# ── Sub-stage C — Pooled Recency-Weighted Training + TrendEncoder ─────────────

def run_substage_c(args, df: pd.DataFrame, device: torch.device) -> None:
    print("\n" + "=" * 60)
    print("SUB-STAGE C — Pooled Recency-Weighted Training + TrendEncoder")
    print("=" * 60)

    # ── Step 1: Load drift vectors ─────────────────────────────────────
    for dm_name in ("DRIFT_MATRIX_0510.csv", "DRIFT_MATRIX_1015.csv", "DRIFT_MATRIX_1522.csv"):
        p = FORECAST_DIR / dm_name
        if not p.exists():
            raise FileNotFoundError(f"{dm_name} not found at {p}. Run Sub-stages A and B first.")

    vec_0510 = _load_drift_vec(FORECAST_DIR / "DRIFT_MATRIX_0510.csv")
    vec_1015 = _load_drift_vec(FORECAST_DIR / "DRIFT_MATRIX_1015.csv")
    vec_1522 = _load_drift_vec(FORECAST_DIR / "DRIFT_MATRIX_1522.csv")
    drift_dim = vec_0510.shape[0]  # 42
    print(f"Drift vectors loaded: dim={drift_dim}")

    # ── Step 2: Pretext / model load — resume branch or fresh start ────
    trend_enc = TrendEncoder(drift_dim=drift_dim).to(device)
    pooled_ckpt_path = MODELS_DIR / "W_pooled_2030.pt"
    enc_ckpt_path    = MODELS_DIR / "trend_encoder_2030.pt"
    resume_active = bool(getattr(args, "resume", False)) and pooled_ckpt_path.exists() and enc_ckpt_path.exists()

    if resume_active:
        print(f"\n[RESUME] Found on-disk W_pooled_2030.pt + trend_encoder_2030.pt — skipping pretext and W_2022_ft.pt warm start.")
        pooled_ckpt = torch.load(pooled_ckpt_path, map_location=device)
        cfg = pooled_ckpt["config"]
        model = ConditionalTransformer(cfg).to(device)
        strict_load = not args.smoke
        missing, unexpected = model.load_state_dict(pooled_ckpt["model_state"], strict=strict_load)
        if (missing or unexpected) and strict_load:
            raise RuntimeError(
                f"[FATAL] Resume load mismatch: {len(missing)} missing, {len(unexpected)} unexpected keys "
                f"in W_pooled_2030.pt. 04B_model.py architecture diverged. Missing: {missing[:5]}... Unexpected: {unexpected[:5]}..."
            )
        enc_ckpt = torch.load(enc_ckpt_path, map_location=device)
        trend_enc.load_state_dict(enc_ckpt["encoder_state"])
        resumed_val_js = float(pooled_ckpt.get("val_js", float("inf")))
        print(f"  Loaded W_pooled_2030.pt (val_JS={resumed_val_js:.4f})")
        print(f"  Loaded trend_encoder_2030.pt (drift_dim={enc_ckpt.get('drift_dim', drift_dim)})")
    else:
        # Step 2a: Pretext training of TrendEncoder (500 gradient steps)
        pretext_input  = torch.stack(
            [vec_0510, vec_1015, torch.zeros(drift_dim)], dim=0
        ).unsqueeze(0).to(device)                          # (1, 3, 42)
        pretext_target = vec_1522.unsqueeze(0).to(device)  # (1, 42)

        pretext_opt = torch.optim.Adam(trend_enc.parameters(), lr=1e-3)
        print("\n[PRETEXT] Training TrendEncoder (500 steps, MSE) ...")
        pretext_loss_val = 0.0
        for _ in range(500):
            pretext_opt.zero_grad()
            pred = trend_enc(pretext_input)
            pretext_loss = F.mse_loss(pred, pretext_target)
            pretext_loss.backward()
            pretext_opt.step()
            pretext_loss_val = pretext_loss.item()
        print(f"[PRETEXT] Final MSE: {pretext_loss_val:.6f}")

        # Step 2b: Joint-training warm start from W_2022_ft.pt
        ckpt_path = MODELS_DIR / "W_2022_ft.pt"
        if not ckpt_path.exists():
            raise FileNotFoundError(f"W_2022_ft.pt not found at {ckpt_path}. Run Sub-stage B first.")
        ckpt = torch.load(ckpt_path, map_location=device)
        cfg  = ckpt["config"]
        model = ConditionalTransformer(cfg).to(device)
        strict_load = not args.smoke
        missing, unexpected = model.load_state_dict(ckpt["model_state"], strict=strict_load)
        if missing or unexpected:
            msg = f"Partial load: {len(missing)} missing, {len(unexpected)} unexpected keys."
            if strict_load:
                raise RuntimeError(
                    f"[FATAL] {msg} 04B_model.py architecture diverged from W_2022_ft.pt. "
                    f"Aborting to prevent silent bad training. Missing: {missing[:5]}... Unexpected: {unexpected[:5]}..."
                )
            print(f"  [WARN] {msg} (smoke mode, strict=False permitted; local 04B_model.py differs from cluster).")
        print(f"\nLoaded W_2022_ft.pt (val_JS={ckpt['val_js']:.4f})")
        resumed_val_js = float("inf")

    # Drift sequence for joint training: [0510, 1015, 1522]
    drift_seq = torch.stack([vec_0510, vec_1015, vec_1522], dim=0).unsqueeze(0).to(device)  # (1, 3, 42)

    max_epochs = 3 if args.smoke else 100
    bs         = 16 if args.smoke else 256

    # Pool all 4 cycles; 5% smoke sample per cycle
    pool = df.copy()
    if args.smoke:
        pool = (
            pool.groupby("CYCLE_YEAR", group_keys=False)
                .apply(lambda x: x.sample(frac=0.05, random_state=42))
                .reset_index(drop=True)
        )

    # 70/20 split (replicates _split_70_20 from run_substage_b)
    tr_pool, temp = train_test_split(
        pool, test_size=0.30, stratify=pool["DDAY_STRATA"], random_state=42
    )
    va_pool, _ = train_test_split(
        temp, test_size=0.333, stratify=temp["DDAY_STRATA"], random_state=42
    )
    va_2022 = va_pool[va_pool["CYCLE_YEAR"] == 2022].reset_index(drop=True)
    print(f"train={len(tr_pool):,}  val(2022)={len(va_2022):,}")

    train_ds     = DiaryDataset(tr_pool)
    val_ds       = DiaryDataset(va_2022)
    train_loader = DataLoader(train_ds, batch_size=bs, shuffle=True,  num_workers=0, drop_last=True)
    val_loader   = DataLoader(val_ds,   batch_size=bs, shuffle=False, num_workers=0)

    recency_weights = {2005: 0.10, 2010: 0.20, 2015: 0.30, 2022: 0.40}
    # Weekend up-weighting (added 2026-05-15) — Sub-stage D Phase i backcasting showed
    # weekend JS stuck at ~0.18 across all stages while WD reached ~0.07. Ratios 1:2:2
    # (WD:Sat:Sun) re-normalized to mean=1.0 over uniform strata distribution so total
    # loss magnitude is unchanged; only gradient *direction* per stratum shifts.
    stratum_weights = {1: 0.6, 2: 1.2, 3: 1.2}
    optimizer = torch.optim.AdamW(
        list(model.parameters()) + list(trend_enc.parameters()),
        lr=1e-4, weight_decay=1e-4,
    )

    patience         = 5
    best_js          = resumed_val_js  # seeded from disk ckpt if --resume, else +inf
    best_model_state = None
    best_enc_state   = None
    wait             = 0

    print(f"\n{'Epoch':>6}  {'train_loss':>12}  {'val_JS':>8}")
    for epoch in range(1, max_epochs + 1):
        # Compute trend_target once per epoch with gradient enabled (joint training)
        trend_enc.train()
        trend_target = trend_enc(drift_seq)  # (1, 42)

        model.train()
        total_loss_sum, n_batches = 0.0, 0
        for batch in train_loader:
            batch = {k: v.to(device) for k, v in batch.items()}
            out   = model(batch)
            B, T  = batch["dec_act_seq"].shape

            # Recency × stratum weights per sample
            r = torch.tensor(
                [recency_weights.get(int(yr.item()), 1.0) for yr in batch["cycle_year"]],
                dtype=torch.float32, device=device,
            )  # (B,)
            s = torch.tensor(
                [stratum_weights.get(int(st.item()), 1.0) for st in batch["tgt_strata"]],
                dtype=torch.float32, device=device,
            )  # (B,)
            w = r * s  # (B,) — combined recency × stratum weight

            # Primary loss: recency × stratum-weighted act CE + home BCE + cop BCE
            act_loss = (
                F.cross_entropy(
                    out["act_logits"].reshape(B * T, N_ACT),
                    batch["dec_act_seq"].reshape(B * T),
                    reduction="none",
                ).reshape(B, T).mean(dim=1) * w
            ).mean()
            home_loss = F.binary_cross_entropy_with_logits(
                out["home_logits"], batch["dec_aux_seq"][:, :, 0].float()
            )
            cop_loss = F.binary_cross_entropy_with_logits(
                out["cop_logits"], batch["dec_aux_seq"][:, :, 1:].float()
            )
            primary_loss = act_loss + 0.5 * home_loss + 0.3 * cop_loss

            # Aux KL loss: decoder predicted activity distribution vs trend projection
            pred_dist  = out["act_logits"].softmax(dim=-1).mean(dim=(0, 1))          # (14,)
            trend_pool = trend_target.squeeze(0).reshape(3, 14).mean(dim=0)           # (14,)
            trend_pool = trend_pool.softmax(dim=-1)
            aux_loss   = F.kl_div(
                pred_dist.clamp(min=1e-10).log(),
                trend_pool.detach(),
                reduction="batchmean",
            )
            total_loss = primary_loss + 0.1 * aux_loss

            optimizer.zero_grad()
            total_loss.backward()
            torch.nn.utils.clip_grad_norm_(
                list(model.parameters()) + list(trend_enc.parameters()), 1.0
            )
            optimizer.step()
            total_loss_sum += total_loss.item()
            n_batches += 1

        train_loss = total_loss_sum / max(n_batches, 1)
        val_js     = _val_js(model, val_loader, device)
        print(f"{epoch:6d}  {train_loss:12.4f}  {val_js:8.4f}")

        if val_js < best_js:
            best_js          = val_js
            best_model_state = {k: v.clone() for k, v in model.state_dict().items()}
            best_enc_state   = {k: v.clone() for k, v in trend_enc.state_dict().items()}
            wait             = 0
            # Persist immediately so a SLURM time-limit kill keeps the best epoch.
            torch.save(
                {"model_state": model.state_dict(), "config": cfg, "val_js": best_js},
                MODELS_DIR / "W_pooled_2030.pt",
            )
            torch.save(
                {"encoder_state": trend_enc.state_dict(), "drift_dim": drift_dim},
                MODELS_DIR / "trend_encoder_2030.pt",
            )
            print(f"  [CKPT] saved epoch {epoch} val_JS={best_js:.4f}")
        else:
            wait += 1
            if wait >= patience:
                print(f"  Early stop at epoch {epoch} (patience={patience})")
                break

    if best_model_state is not None:
        model.load_state_dict(best_model_state)
    if best_enc_state is not None:
        trend_enc.load_state_dict(best_enc_state)

    # ── Step 4: Save outputs ───────────────────────────────────────────
    torch.save(
        {"model_state": model.state_dict(), "config": cfg, "val_js": best_js},
        MODELS_DIR / "W_pooled_2030.pt",
    )
    torch.save(
        {"encoder_state": trend_enc.state_dict(), "drift_dim": drift_dim},
        MODELS_DIR / "trend_encoder_2030.pt",
    )
    print(f"\n[SUBSTAGE_C_COMPLETE] W_pooled_2030 val_JS={best_js:.4f}")


# ── Sub-stage D — Phase i: 2022 Backcasting Reconstruction ───────────────────

def run_substage_d(args, df: pd.DataFrame, device: torch.device) -> None:
    """
    Two-phase inference (HPC for full run; smoke supported locally).

    Phase i — 2022 Backcasting (implemented below):
        Load W_pooled_2030. Self-reconstruct 2022 augmented schedules with
        joint-style drift sequence [0510, 1015, 1522]. Compute JS per
        stratum vs observed 2022. Gate: JS < 0.10 per stratum.

    Phase ii — 2030 Forward Forecast (NOT YET IMPLEMENTED):
        Blocked on scenario_2030_features.csv. Will use trend_encoder_2030
        forward projection + pretext-style sequence [1015, 1522, zeros].
    """
    print("\n" + "=" * 60)
    print("SUB-STAGE D — Phase i: 2022 Backcasting Reconstruction")
    print("=" * 60)

    # ── Load W_pooled_2030 (strict gated on smoke; cluster path strict=True) ─
    ckpt_path = MODELS_DIR / "W_pooled_2030.pt"
    if not ckpt_path.exists():
        raise FileNotFoundError(
            f"W_pooled_2030.pt not found at {ckpt_path}. Run Sub-stage C first."
        )
    ckpt = torch.load(ckpt_path, map_location=device)
    cfg  = ckpt["config"]
    model = ConditionalTransformer(cfg).to(device)
    strict_load = not args.smoke
    missing, unexpected = model.load_state_dict(ckpt["model_state"], strict=strict_load)
    if missing or unexpected:
        msg = f"Partial load: {len(missing)} missing, {len(unexpected)} unexpected keys."
        if strict_load:
            raise RuntimeError(
                f"[FATAL] {msg} 04B_model.py architecture diverged from W_pooled_2030.pt. "
                f"Aborting Phase i to prevent silent bad inference. "
                f"Missing: {missing[:5]}... Unexpected: {unexpected[:5]}..."
            )
        print(f"  [WARN] {msg} (smoke mode, strict=False permitted; local 04B_model.py differs from cluster).")
    print(f"Loaded W_pooled_2030.pt (val_JS={ckpt['val_js']:.4f})")

    enc_path = MODELS_DIR / "trend_encoder_2030.pt"
    if enc_path.exists():
        print(f"  Found trend_encoder_2030.pt (reserved for Phase ii; not used in backcasting).")
    else:
        print(f"  [WARN] trend_encoder_2030.pt missing — Phase ii will fail when implemented.")

    # ── Build 2022 cohort ──────────────────────────────────────────────────
    val_2022 = df[df["CYCLE_YEAR"] == 2022].reset_index(drop=True)
    if args.smoke:
        val_2022 = (
            val_2022.groupby("DDAY_STRATA", group_keys=False)
                    .apply(lambda x: x.sample(frac=0.05, random_state=42))
                    .reset_index(drop=True)
        )
    print(f"2022 cohort: {len(val_2022):,} rows")

    # ── Per-stratum self-reconstruction + JS ───────────────────────────────
    model.eval()
    BS = 256
    eps = 1e-10
    js_per_stratum: dict = {}
    at_home_obs_wd  = None
    at_home_pred_wd = None
    out_records: list = []

    for strata_val in [1, 2, 3]:
        sub = val_2022[val_2022["DDAY_STRATA"] == strata_val].reset_index(drop=True)
        if len(sub) == 0:
            continue
        tensors = df_to_tensors(sub)
        act_t   = tensors["act_t"]
        aux_t   = tensors["aux_t"]
        cond_t  = tensors["cond_t"]
        cyc_t   = tensors["cyc_t"]
        str_t   = tensors["str_t"]

        obs_acts = act_t.numpy()             # (N, 48) ints 0..13
        obs_hom  = aux_t[:, :, 0].numpy()    # (N, 48)

        recon_acts_all: list = []
        recon_hom_all:  list = []
        with torch.no_grad():
            for b0 in range(0, len(sub), BS):
                b1 = min(b0 + BS, len(sub))
                batch = {
                    "act_seq":     act_t[b0:b1].to(device),
                    "aux_seq":     aux_t[b0:b1].to(device),
                    "cond_vec":    cond_t[b0:b1].to(device),
                    "cycle_idx":   cyc_t[b0:b1].to(device),
                    "dec_act_seq": act_t[b0:b1].to(device),
                    "dec_aux_seq": aux_t[b0:b1].to(device),
                    "tgt_strata":  str_t[b0:b1].to(device),
                }
                out = model(batch)
                recon_acts_all.append(out["act_logits"].argmax(dim=-1).cpu().numpy())
                recon_hom_all.append(
                    (torch.sigmoid(out["home_logits"]) > 0.5).cpu().numpy().astype(np.int64)
                )
        recon_acts = np.concatenate(recon_acts_all, axis=0)  # (N, 48) ints 0..13
        recon_hom  = np.concatenate(recon_hom_all,  axis=0)  # (N, 48) ints 0/1

        # JS divergence on activity distribution (predicted vs observed)
        p = np.bincount(recon_acts.flatten(), minlength=N_ACT).astype(np.float64)
        q = np.bincount(obs_acts.flatten(),  minlength=N_ACT).astype(np.float64)
        p /= max(p.sum(), 1)
        q /= max(q.sum(), 1)
        js = float(jensenshannon(p + eps, q + eps))
        js_per_stratum[strata_val] = js

        if strata_val == 1:
            at_home_obs_wd  = float(obs_hom.mean())
            at_home_pred_wd = float(recon_hom.mean())

        recon_acts_out = (recon_acts + 1).astype(np.int64)  # back to 1..14
        occ_ids = sub["occID"].values if "occID" in sub.columns else np.arange(len(sub))
        for i in range(len(sub)):
            rec = {
                "occID":       occ_ids[i],
                "CYCLE_YEAR":  2022,
                "DDAY_STRATA": strata_val,
            }
            for j in range(48):
                rec[ACT_COLS[j]] = int(recon_acts_out[i, j])
                rec[HOM_COLS[j]] = int(recon_hom[i, j])
            out_records.append(rec)

    # ── Save reconstructed_2022_diaries.csv ────────────────────────────────
    out_df = pd.DataFrame(out_records)
    out_path = FORECAST_DIR / "reconstructed_2022_diaries.csv"
    out_df.to_csv(out_path, index=False)
    print(f"\nSaved reconstructed_2022_diaries.csv ({len(out_df):,} rows) to {out_path}")

    # ── Gate evaluation ────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("Phase i Gate Evaluation (JS per stratum, gate: < 0.10)")
    print("=" * 60)
    all_pass = True
    for s in [1, 2, 3]:
        if s not in js_per_stratum:
            continue
        js  = js_per_stratum[s]
        tag = "PASS" if js < 0.10 else "FAIL"
        all_pass = all_pass and (js < 0.10)
        label = {1: "WD", 2: "Sat", 3: "Sun"}[s]
        print(f"  Stratum {s} ({label}): JS={js:.4f}  [{tag}]")

    if at_home_obs_wd is not None:
        diff_pp = (at_home_pred_wd - at_home_obs_wd) * 100.0
        at_tag  = "PASS" if abs(diff_pp) <= 2.0 else "FAIL"
        all_pass = all_pass and (abs(diff_pp) <= 2.0)
        print(
            f"\n  WD AT_HOME: obs={at_home_obs_wd*100:.1f}%  "
            f"pred={at_home_pred_wd*100:.1f}%  diff={diff_pp:+.1f}pp  [{at_tag}]"
        )

    status = "COMPLETE" if all_pass else "GATE_FAIL"
    print(f"\n[SUBSTAGE_D_PHASE_I_{status}]")


# ── Orchestrator ──────────────────────────────────────────────────────────────

def run_all(args, df: pd.DataFrame, device: torch.device) -> None:
    run_substage_a(args, df, device)
    run_substage_b(args, df, device)
    run_substage_c(args, df, device)
    run_substage_d(args, df, device)


# ── Sub-step 6A standalone audit block ────────────────────────────────────────

def run_input_audit(df: pd.DataFrame) -> None:
    passes = []

    def chk(ok: bool, msg: str) -> None:
        tag = "[PASS]" if ok else "[FAIL]"
        print(f"{tag} {msg}")
        passes.append(ok)

    print("\n" + "=" * 60)
    print("SUB-STEP 6A — Input Audit")
    print("=" * 60)

    chk(abs(len(df) - 192_183) <= 10, f"Row count: {len(df):,} (expected ~192,183 ±10)")

    cy = set(df["CYCLE_YEAR"].unique())
    chk(cy == {2005, 2010, 2015, 2022}, f"CYCLE_YEAR in {sorted(cy)}")
    print("  Per-cycle counts:")
    for yr, cnt in df["CYCLE_YEAR"].value_counts().sort_index().items():
        print(f"    {yr}: {cnt:,}")

    ds = set(df["DDAY_STRATA"].unique())
    chk(ds == {1, 2, 3}, f"DDAY_STRATA in {sorted(ds)}")
    print("  Per-cycle × per-stratum counts:")
    for (yr, st), cnt in df.groupby(["CYCLE_YEAR", "DDAY_STRATA"]).size().items():
        print(f"    {yr} / strata={st}: {cnt:,}")

    chk("IS_SYNTHETIC" in df.columns, "IS_SYNTHETIC column present")
    print("  IS_SYNTHETIC per cycle:")
    for (yr, s), cnt in df.groupby(["CYCLE_YEAR", "IS_SYNTHETIC"]).size().items():
        lbl = "synthetic" if s == 1 else "observed"
        print(f"    {yr} / IS_SYNTHETIC={int(s)} ({lbl}): {cnt:,}")

    act_ok = all(c in df.columns for c in ACT_COLS)
    hom_ok = all(c in df.columns for c in HOM_COLS)
    chk(act_ok and hom_ok, f"All 96 act30/hom30 columns present")

    act_v = df[ACT_COLS].values
    chk(int(act_v.min()) >= 1 and int(act_v.max()) <= 14,
        f"act30 range: [{int(act_v.min())}, {int(act_v.max())}] (expected [1, 14])")

    hom_v = set(np.unique(df[HOM_COLS].values))
    chk(hom_v <= {0, 1}, f"hom30 values: {sorted(hom_v)} (expected {{0, 1}})")

    print("\nAT_HOME mean per cycle (weekday only, DDAY_STRATA=1):")
    expected = {2005: 62.7, 2010: 62.3, 2015: 64.5, 2022: 70.6}
    for yr in CYCLE_YEARS:
        mask = (df["CYCLE_YEAR"] == yr) & (df["DDAY_STRATA"] == 1)
        mean_h = df.loc[mask, HOM_COLS].values.mean() * 100
        exp    = expected.get(yr, float("nan"))
        diff   = mean_h - exp
        print(f"  {yr}: {mean_h:.1f}%  (expected ~{exp:.1f}%,  diff={diff:+.1f}pp)")

    print(f"\n{'=' * 50}")
    print(f"6A AUDIT: {sum(passes)}/{len(passes)} checks passed")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Step 6 Longitudinal Forecasting")
    parser.add_argument("--stage",
                        choices=["A", "B", "C", "D", "all"], default="all",
                        help="Sub-stage to run")
    parser.add_argument("--smoke", action="store_true",
                        help="5%% data, 3 epochs max — CPU local test")
    parser.add_argument("--resume", action="store_true",
                        help="Resume Sub-stage C from on-disk W_pooled_2030.pt + trend_encoder_2030.pt (skip pretext + W_2022_ft.pt warm start)")
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    print(f"Loading {DATA_PATH} ...")
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df):,} rows x {len(df.columns)} cols")

    run_input_audit(df)

    stage_fn = {
        "A":   run_substage_a,
        "B":   run_substage_b,
        "C":   run_substage_c,
        "D":   run_substage_d,
        "all": run_all,
    }
    stage_fn[args.stage](args, df, device)
