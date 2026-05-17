"""
diag_teacher_forcing.py — H-Tier-1.6 AR-cascade falsification diagnostic.

Three inference modes on the val set for one checkpoint:
  A — autoregressive (production path, temperature=0 deterministic)
  B — teacher-forced (decoder receives ground-truth dec_aux_seq for all 48 slots)
  C — oracle home-feedback (AR with true AT_HOME fed back; cop/act remain generated)

Metrics are imported from 04J_statistical_diagnostics (identical formulas to published gates).

Usage (via job_diag_TF.sh):
    python diag_teacher_forcing.py \\
        --checkpoint /speed-scratch/.../outputs_step4_G4/checkpoints/best_model.pt \\
        --data_dir   /speed-scratch/.../outputs_step4_G1 \\
        --output_dir /speed-scratch/.../diagnostics_tier_1_6 \\
        --tag G4 --tanh_heads 0

Outputs (in output_dir):
    tier_1_6_results.csv — appended with 3 rows (modes A/B/C) per run
"""

import argparse
import importlib
import os
import sys

import numpy as np
import pandas as pd
import torch
import torch.nn as nn

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR  = os.path.dirname(SCRIPT_DIR)   # one up: occModeling/ — contains 04B_model.py, 04J_*.py
sys.path.insert(0, MODEL_DIR)

# Read at module level so _oracle_home_generate() can see it without reimporting 04B_model
H_TIME_PE = int(os.environ.get("H_TIME_PE", "0"))

COP_COLS_9 = [
    "Alone", "Spouse", "Children", "parents",
    "otherInFAMs", "otherHHs", "friends", "others", "colleagues",
]


def parse_args():
    p = argparse.ArgumentParser(description="H-Tier-1.6 AR-cascade falsification diagnostic")
    p.add_argument("--checkpoint",  required=True,
                   help="Path to best_model.pt for this tag")
    p.add_argument("--data_dir",    required=True,
                   help="Dir containing step4_val.pt")
    p.add_argument("--output_dir",  required=True,
                   help="Dir for tier_1_6_results.csv (created if absent)")
    p.add_argument("--tag",         required=True,
                   help="G4 or H_Tanh — label in output CSV")
    p.add_argument("--tanh_heads",  type=int, required=True,
                   help="0=plain Linear heads (G4); 1=Tanh-wrapped (H_Tanh). "
                        "Must match the checkpoint. Sets H_TANH_HEADS env var.")
    return p.parse_args()


# ── Mode C: oracle home AR loop ───────────────────────────────────────────────

@torch.no_grad()
def _oracle_home_generate(model, act_t, aux_t, cond_t, cidx_t, strat_t):
    """
    AR generation with oracle AT_HOME feedback; cop+act remain model-generated.
    Isolates the AT_HOME→Spouse cascade: Spouse can only improve here if it
    is driven by home_tok fed back into the decoder.
    Returns: gen_acts (B,48), gen_homes (B,48), gen_cop_probs (B,48,9)
    """
    B      = act_t.shape[0]
    device = act_t.device

    memory                 = model.encode(act_t, aux_t, cond_t, cidx_t)
    cond_g, cyc_g, strat_g = model._build_dec_cond(cond_t, cidx_t, strat_t)
    true_home              = aux_t[:, :, 0]   # (B, 48) oracle AT_HOME ground truth

    gen_acts, gen_homes, gen_cop_probs = [], [], []

    bos = model.bos_token.expand(B, 1, model.d_model)
    if not H_TIME_PE:
        bos = bos + model.dec_pos_enc[:, :1, :]
    dec_tokens = [bos]

    for t in range(model.n_slots):
        dec_seq = torch.cat(dec_tokens, dim=1)
        if H_TIME_PE:
            _sz = dec_seq.size(1)
            cyc = model.cyclical_time.expand(B, -1, -1)[:, :_sz, :]
            dec_seq = model.time_proj(torch.cat([dec_seq, cyc], dim=-1))
            dec_seq = dec_seq + model.learnable_pe[:, :_sz, :]
        mask    = nn.Transformer.generate_square_subsequent_mask(dec_seq.shape[1], device=device)
        out, _  = model.decoder(dec_seq, memory, cond_g, cyc_g, strat_g, mask)
        out_t   = out[:, -1, :]

        act_tok   = model.act_head(out_t).argmax(dim=-1)                         # (B,)
        home_pred = (torch.sigmoid(model.home_head(out_t).squeeze(-1)) > 0.5).float()
        cop_probs = torch.sigmoid(model.cop_head(out_t))                          # (B,9) raw σ
        cop_tok   = (cop_probs > 0.5).float()

        gen_acts.append(act_tok)
        gen_homes.append(home_pred)
        gen_cop_probs.append(cop_probs)

        if t < model.n_slots - 1:
            oracle_h = true_home[:, t].to(device)                    # oracle home for feedback
            aux_fb   = torch.cat([oracle_h.unsqueeze(-1), cop_tok], dim=-1)      # (B,10)
            slot_emb = model.slot_linear(
                torch.cat([model.act_embedding(act_tok), aux_fb], dim=-1)
            ).unsqueeze(1)                                                        # (B,1,d_model)
            if not H_TIME_PE:
                slot_emb = slot_emb + model.dec_pos_enc[:, t + 1:t + 2, :]
            dec_tokens.append(slot_emb)

    return (
        torch.stack(gen_acts,      dim=1),    # (B, 48) int64
        torch.stack(gen_homes,     dim=1),    # (B, 48) float binary (predicted, not oracle)
        torch.stack(gen_cop_probs, dim=1),    # (B, 48, 9) raw σ
    )


# ── Inference dispatcher ──────────────────────────────────────────────────────

def _infer_mode(model, val_data, device, mode, batch_size=256):
    """
    Run val-set inference for one mode.
    Returns:
        act_np  (N, 48) int, 1-indexed (ready for act30_* columns)
        hom_np  (N, 48) float — sigmoid σ for mode B; binary float for A/C
        cop_np  (N, 48, 9) float — raw sigmoid σ
    """
    N       = len(val_data["act_seq"])
    act_out = np.empty((N, 48), dtype=np.int64)
    hom_out = np.empty((N, 48), dtype=np.float32)
    cop_out = np.empty((N, 48, 9), dtype=np.float32)

    for s in range(0, N, batch_size):
        e  = min(s + batch_size, N)
        at = val_data["act_seq"][s:e].to(device)
        ax = val_data["aux_seq"][s:e].to(device)
        cv = val_data["cond_vec"][s:e].to(device)
        ci = val_data["cycle_idx"][s:e].to(device)
        st = val_data["obs_strata"][s:e].to(device)

        with torch.no_grad():
            if mode == "A":
                ga, gh, _, gcp = model.generate(at, ax, cv, ci, st, temperature=0.0)
                act_out[s:e] = ga.cpu().numpy()
                hom_out[s:e] = gh.cpu().numpy()
                cop_out[s:e] = gcp.cpu().numpy()
            elif mode == "B":
                mem           = model.encode(at, ax, cv, ci)
                al, hl, cl, _ = model.decode(at, ax, st, mem, cv, ci)
                act_out[s:e]  = al.argmax(dim=-1).cpu().numpy()
                hom_out[s:e]  = torch.sigmoid(hl).cpu().numpy()
                cop_out[s:e]  = torch.sigmoid(cl).cpu().numpy()
            elif mode == "C":
                ga, gh, gcp  = _oracle_home_generate(model, at, ax, cv, ci, st)
                act_out[s:e] = ga.cpu().numpy()
                hom_out[s:e] = gh.cpu().numpy()
                cop_out[s:e] = gcp.cpu().numpy()

        print(f"  [Mode {mode}] {e}/{N}", flush=True)

    act_out = act_out + 1     # 0-indexed → 1-indexed for act30_* columns
    return act_out, hom_out, cop_out


# ── DataFrame builder ─────────────────────────────────────────────────────────

def _build_df(val_data, act_np, hom_np, cop_np, is_synthetic, cycle_year_col):
    """Assemble obs_aug or syn_aug DataFrame from arrays."""
    N     = act_np.shape[0]
    occ   = val_data.get("occ_ids", torch.arange(N)).numpy()
    strat = val_data["obs_strata"].numpy()
    d = {
        "occID":        occ,
        "CYCLE_YEAR":   cycle_year_col,
        "DDAY_STRATA":  strat,
        "IS_SYNTHETIC": is_synthetic,
    }
    for s in range(48):
        d[f"act30_{s+1:03d}"] = act_np[:, s]
    for s in range(48):
        d[f"hom30_{s+1:03d}"] = hom_np[:, s]
    for ci, cn in enumerate(COP_COLS_9):
        for s in range(48):
            d[f"{cn}30_{s+1:03d}"] = cop_np[:, s, ci]
    return pd.DataFrame(d)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    args = parse_args()
    os.environ["H_TANH_HEADS"] = str(args.tanh_heads)
    os.makedirs(args.output_dir, exist_ok=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[{args.tag}] device={device}  H_TANH_HEADS={args.tanh_heads}  H_TIME_PE={H_TIME_PE}")
    print(f"[{args.tag}] checkpoint : {args.checkpoint}")
    print(f"[{args.tag}] data_dir   : {args.data_dir}")
    print(f"[{args.tag}] output_dir : {args.output_dir}")

    # ── Import model and metric modules ───────────────────────────────────────
    model_mod = importlib.import_module("04B_model")
    ConditionalTransformer = model_mod.ConditionalTransformer

    # Metric functions imported from 04J — identical formulas to published gates
    diag_mod          = importlib.import_module("04J_statistical_diagnostics")
    run_bootstrap_cis = diag_mod.run_bootstrap_cis
    run_calibration   = diag_mod.run_calibration
    compute_composite = diag_mod.compute_composite_score

    # ── Load val data ─────────────────────────────────────────────────────────
    val_path = os.path.join(args.data_dir, "step4_val.pt")
    print(f"\n[{args.tag}] loading {val_path} ...")
    val_data = torch.load(val_path, map_location="cpu", weights_only=False)
    N = len(val_data["act_seq"])
    print(f"[{args.tag}] val respondents: {N}")

    # CYCLE_YEAR must be actual years (2005/2010/2015/2022) for 04J's CYCLES constant
    _idx_to_year = {0: 2005, 1: 2010, 2: 2015, 3: 2022}
    if "cycle_year" in val_data:
        cycle_year_col = val_data["cycle_year"].numpy()
    else:
        cycle_year_col = np.array(
            [_idx_to_year.get(int(i), int(i)) for i in val_data["cycle_idx"].numpy()]
        )
        print(f"[{args.tag}] WARNING: 'cycle_year' missing — mapped cycle_idx → year")

    # ── Load checkpoint ────────────────────────────────────────────────────────
    print(f"[{args.tag}] loading checkpoint ...")
    ckpt  = torch.load(args.checkpoint, map_location=device, weights_only=False)
    model = ConditionalTransformer(ckpt["model_config"]).to(device)
    model.load_state_dict(ckpt["model_state"])
    model.eval()
    print(f"[{args.tag}] epoch={ckpt.get('epoch','?')}  val_score={ckpt.get('val_score','?')}")

    # ── Ground-truth obs DataFrame (shared across all modes) ──────────────────
    obs_act = val_data["act_seq"].numpy() + 1       # (N,48) 1-indexed
    obs_hom = val_data["aux_seq"].numpy()[:, :, 0]  # (N,48) AT_HOME binary
    obs_cop = val_data["aux_seq"].numpy()[:, :, 1:] # (N,48,9) co-presence binary
    obs_aug = _build_df(val_data, obs_act, obs_hom, obs_cop, 0, cycle_year_col)

    # ── Run three modes and compute metrics ───────────────────────────────────
    rows = []
    for mode in ("A", "B", "C"):
        print(f"\n[{args.tag}] ── Mode {mode} {'(AR production)' if mode=='A' else '(teacher-forced)' if mode=='B' else '(oracle home)'} ──")
        syn_act, syn_hom, syn_cop = _infer_mode(model, val_data, device, mode)
        syn_aug  = _build_df(val_data, syn_act, syn_hom, syn_cop, 1, cycle_year_col)
        combined = pd.concat([obs_aug, syn_aug], ignore_index=True)

        print(f"  [{args.tag}|{mode}] bootstrap CIs ...")
        bs  = run_bootstrap_cis(obs_aug, syn_aug)
        print(f"  [{args.tag}|{mode}] calibration ...")
        cal = run_calibration(combined)
        print(f"  [{args.tag}|{mode}] composite score ...")
        comp = compute_composite(bs, cal, obs_aug, syn_aug)

        cmps      = comp["components"]
        spouse_pp = bs.get("copresence", {}).get("Spouse", {}).get("gap_pp", float("nan"))
        athome_pp = bs.get("at_home", {}).get("gap_pp", float("nan"))

        rows.append({
            "model":      args.tag,
            "mode":       mode,
            "composite":  comp["composite_score"],
            "athome_pp":  athome_pp,
            "spouse_pp":  spouse_pp,
            "act_js":     cmps["act_js_mean"],
            "athome_rms": cmps["at_home_gap_rms_pp"],
            "cop_maxgap": cmps["cop_max_gap_pp"],
            "cop_calmae": cmps["cop_cal_mae"],
        })
        g = rows[-1]
        print(f"  → composite={g['composite']:.4f}  AT_HOME_pp={g['athome_pp']:.2f}  "
              f"AT_HOME_rms={g['athome_rms']:.2f}pp  Spouse_pp={g['spouse_pp']:.2f}  "
              f"act_JS={g['act_js']:.4f}  cop_maxgap={g['cop_maxgap']:.2f}pp  "
              f"cop_calmae={g['cop_calmae']:.4f}")

    # ── Write CSV (append so G4 + H_Tanh accumulate in one file) ─────────────
    out_csv = os.path.join(args.output_dir, "tier_1_6_results.csv")
    df      = pd.DataFrame(rows)
    if os.path.exists(out_csv):
        df.to_csv(out_csv, mode="a", header=False, index=False)
    else:
        df.to_csv(out_csv, index=False)
    print(f"\n[{args.tag}] wrote {len(df)} rows → {out_csv}")

    # ── Mode A sanity check ────────────────────────────────────────────────────
    mode_a = df[df["mode"] == "A"].iloc[0]
    expected = "~1.256" if args.tag == "G4" else "~1.319"
    print(f"[{args.tag}] SANITY — Mode A composite={mode_a['composite']:.4f} "
          f"(published {expected}; val-only self-reconstruction may differ)")
    print(f"[{args.tag}] DONE")


if __name__ == "__main__":
    main()
