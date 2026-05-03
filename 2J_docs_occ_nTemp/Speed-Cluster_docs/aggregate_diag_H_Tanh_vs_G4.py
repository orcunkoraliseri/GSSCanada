"""
aggregate_diag_H_Tanh_vs_G4.py — H-Tier-1.5 local post-processing.

Reads the 8 diagnostic artefacts produced by diagnostic_H_Tanh_vs_G4.py
(4 per tag: logits, probs, per_slot_bce, per_epoch_home) and writes:
    logit_histogram.png
    prob_histogram.png
    per_slot_bce.png
    per_epoch_home.png
    diagnostics_H_Tanh_vs_G4.md

All outputs land in --data_dir (the pulled diagnostics_H_Tanh_vs_G4/ folder).

Usage (locally, after scp pull):
    python Speed-Cluster_docs/aggregate_diag_H_Tanh_vs_G4.py \\
        --data_dir 2J_docs_occ_nTemp/Speed-Cluster_docs/diagnostics_H_Tanh_vs_G4
"""

import argparse
import os
from datetime import date

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


TAGS   = ["G4", "H_Tanh"]
COLORS = {"G4": "#1f77b4", "H_Tanh": "#d62728"}


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--data_dir", required=True,
                   help="Path to local diagnostics_H_Tanh_vs_G4/ directory")
    return p.parse_args()


def load_artefacts(data_dir):
    artefacts = {}
    for tag in TAGS:
        logits_path = os.path.join(data_dir, f"{tag}_home_logits.npy")
        probs_path  = os.path.join(data_dir, f"{tag}_home_probs.npy")
        bce_path    = os.path.join(data_dir, f"{tag}_home_bce.npy")
        slot_path   = os.path.join(data_dir, f"{tag}_per_slot_bce.csv")
        epoch_path  = os.path.join(data_dir, f"{tag}_per_epoch_home.csv")

        for p in [logits_path, probs_path, bce_path, slot_path]:
            if not os.path.isfile(p):
                raise FileNotFoundError(f"Missing artefact: {p}")

        artefacts[tag] = {
            "logits":     np.load(logits_path).flatten(),
            "probs":      np.load(probs_path).flatten(),
            "bce":        np.load(bce_path),
            "per_slot":   pd.read_csv(slot_path),
            "per_epoch":  pd.read_csv(epoch_path) if os.path.isfile(epoch_path) else None,
        }
    return artefacts


def plot_logit_histogram(artefacts, out_path):
    fig, ax = plt.subplots(figsize=(8, 4))
    all_logits = np.concatenate([artefacts[t]["logits"] for t in TAGS])
    bins = np.linspace(all_logits.min(), all_logits.max(), 80)
    for tag in TAGS:
        ax.hist(artefacts[tag]["logits"], bins=bins, alpha=0.6,
                color=COLORS[tag], label=tag, density=True)
    ax.set_xlabel("Pre-sigmoid home logit")
    ax.set_ylabel("Density")
    ax.set_title("Panel 1 — Pre-sigmoid home logit distribution (val set)")
    ax.legend()
    ax.axvline(0, color="k", lw=0.8, ls="--", alpha=0.5)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"  saved {out_path}")


def plot_prob_histogram(artefacts, out_path):
    fig, ax = plt.subplots(figsize=(8, 4))
    bins = np.linspace(0, 1, 51)
    for tag in TAGS:
        ax.hist(artefacts[tag]["probs"], bins=bins, alpha=0.6,
                color=COLORS[tag], label=tag, density=True)
    ax.set_xlabel("Predicted P(AT_HOME=1)")
    ax.set_ylabel("Density")
    ax.set_title("Panel 2 — Predicted home-probability distribution (val set)")
    ax.legend()
    ax.axvline(0.5, color="k", lw=0.8, ls="--", alpha=0.5)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"  saved {out_path}")


def plot_per_slot_bce(artefacts, out_path):
    fig, ax = plt.subplots(figsize=(10, 4))
    slots = np.arange(48)
    slot_labels = [f"{(4 + s // 2) % 24:02d}:{30*(s%2):02d}" for s in slots]
    for tag in TAGS:
        bce_slot = artefacts[tag]["per_slot"]["bce"].values
        ax.plot(slots, bce_slot, color=COLORS[tag], label=tag, lw=1.5, marker=".", ms=3)
    ax.set_xticks(slots[::4])
    ax.set_xticklabels(slot_labels[::4], rotation=45, ha="right", fontsize=7)
    ax.set_xlabel("Time slot (4:00 AM → 3:30 AM)")
    ax.set_ylabel("Mean BCE")
    ax.set_title("Panel 3 — Per-slot home BCE (val set)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"  saved {out_path}")


def plot_per_epoch_home(artefacts, out_path):
    fig, ax = plt.subplots(figsize=(8, 4))
    any_data = False
    for tag in TAGS:
        df = artefacts[tag]["per_epoch"]
        if df is not None and len(df) > 0:
            ax.plot(df["epoch"], df["home"], color=COLORS[tag], label=tag, lw=1.5)
            any_data = True
    if not any_data:
        ax.text(0.5, 0.5, "No training log data", transform=ax.transAxes, ha="center")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Train home BCE loss")
    ax.set_title("Panel 4 — Per-epoch home loss (training log)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"  saved {out_path}")


def summarise(artefacts):
    summary = {}
    for tag in TAGS:
        logits = artefacts[tag]["logits"]
        probs  = artefacts[tag]["probs"]
        bce    = artefacts[tag]["bce"]
        df_slot = artefacts[tag]["per_slot"]
        df_ep   = artefacts[tag]["per_epoch"]

        frac_conf = float(np.mean((probs < 0.05) | (probs > 0.95)))
        frac_mid  = float(np.mean((probs > 0.4) & (probs < 0.7)))
        top3_slots = df_slot.nlargest(3, "bce")[["slot", "bce"]].values.tolist()
        final_home = float(df_ep["home"].iloc[-1]) if df_ep is not None and len(df_ep) > 0 else None

        summary[tag] = {
            "logit_min":   float(logits.min()),
            "logit_max":   float(logits.max()),
            "logit_mean":  float(logits.mean()),
            "logit_std":   float(logits.std()),
            "frac_confident": frac_conf,
            "frac_mid":    frac_mid,
            "mean_bce":    float(bce.mean()),
            "top3_slots":  top3_slots,
            "final_home":  final_home,
            "n_epochs":    len(df_ep) if df_ep is not None else None,
        }
    return summary


def write_markdown(summary, artefacts, out_path):
    g4 = summary["G4"]
    ht = summary["H_Tanh"]

    bce_gap  = ht["mean_bce"] - g4["mean_bce"]
    home_gap = None
    if g4["final_home"] is not None and ht["final_home"] is not None:
        home_gap = ht["final_home"] - g4["final_home"]

    # Per-slot rows where H_Tanh penalty > G4
    df_g4 = artefacts["G4"]["per_slot"]
    df_ht = artefacts["H_Tanh"]["per_slot"]
    diff  = df_ht["bce"].values - df_g4["bce"].values
    top3_worse_idx = np.argsort(diff)[-3:][::-1]
    top3_worse = [(int(s), float(diff[s])) for s in top3_worse_idx]

    lines = [
        "# H-Tier-1.5 — H_Tanh vs G4 diagnostic dump",
        f"Date: {date.today()}",
        "",
        "## Hypothesis",
        "",
        "H_Tanh wraps `home_head` and `cop_head` as `nn.Sequential(nn.Tanh(), nn.Linear(d_model, n))`.",
        "The Tanh bounds the incoming hidden state to `[−1, 1]`, so the resulting pre-sigmoid logit is",
        "bounded to `[−|w|, +|w|]` where `w` is the Linear weight magnitude.",
        "If `|w|` stayed small during training, predicted probabilities cluster around 0.5–0.7 instead",
        "of G4's bimodal 0.05/0.95 — raising BCE even when the binarized AT_HOME gap holds.",
        "",
        "**If CONFIRMED:** fix is a learnable scalar `α` before the Tanh (`α·tanh(h) → Linear`),",
        "recovering G4's confident regime while staying bounded. Cheap, env-var-gated.",
        "**If REFUTED:** composite regression is a deeper conditioning issue; advance to Tier-2 H_Time.",
        "",
        "---",
        "",
        "## Panel 1 — Pre-sigmoid logit distribution",
        "",
        "| Stat | G4 | H_Tanh |",
        "|------|-----|--------|",
        f"| min  | {g4['logit_min']:.3f} | {ht['logit_min']:.3f} |",
        f"| max  | {g4['logit_max']:.3f} | {ht['logit_max']:.3f} |",
        f"| mean | {g4['logit_mean']:.3f} | {ht['logit_mean']:.3f} |",
        f"| std  | {g4['logit_std']:.3f} | {ht['logit_std']:.3f} |",
        "",
        "![logit histogram](logit_histogram.png)",
        "",
        "---",
        "",
        "## Panel 2 — Predicted probability distribution",
        "",
        "| Fraction | G4 | H_Tanh |",
        "|----------|-----|--------|",
        f"| p < 0.05 or p > 0.95 (confident) | {g4['frac_confident']:.3f} | {ht['frac_confident']:.3f} |",
        f"| 0.4 < p < 0.7 (mid-range)         | {g4['frac_mid']:.3f} | {ht['frac_mid']:.3f} |",
        "",
        "![prob histogram](prob_histogram.png)",
        "",
        "---",
        "",
        "## Panel 3 — Per-slot home BCE",
        "",
        "Top-3 slots where H_Tanh penalty exceeds G4 (Δ = H_Tanh − G4):",
        "",
        "| Slot | Δ BCE |",
        "|------|-------|",
    ]
    for slot, delta in top3_worse:
        time_str = f"{(4 + slot//2)%24:02d}:{30*(slot%2):02d}"
        lines.append(f"| {slot} ({time_str}) | {delta:+.4f} |")

    lines += [
        "",
        "![per-slot BCE](per_slot_bce.png)",
        "",
        "---",
        "",
        "## Panel 4 — Per-epoch home loss",
        "",
    ]
    if g4["final_home"] is not None and ht["final_home"] is not None:
        lines += [
            f"- G4 final-epoch home loss: **{g4['final_home']:.4f}**  ({g4['n_epochs']} epochs)",
            f"- H_Tanh final-epoch home loss: **{ht['final_home']:.4f}**  ({ht['n_epochs']} epochs)",
            f"- Gap (H_Tanh − G4): **{home_gap:+.4f}**",
        ]
    lines += [
        "",
        "Overall mean val-set BCE gap (H_Tanh − G4):",
        f"  G4 = {g4['mean_bce']:.4f}  |  H_Tanh = {ht['mean_bce']:.4f}  |  Δ = {bce_gap:+.4f}",
        "",
        "![per-epoch home loss](per_epoch_home.png)",
        "",
        "---",
        "",
        "## Verdict",
        "",
        "> **LEAVE BLANK** — manager fills in after reading the panels:",
        "> BOUNDING ARTEFACT CONFIRMED / REFUTED / INCONCLUSIVE",
        "",
        "---",
        "",
        "## Recommended next move",
        "",
        "> **LEAVE BLANK** — manager fills in.",
        "",
    ]

    with open(out_path, "w") as f:
        f.write("\n".join(lines))
    print(f"  saved {out_path}")


def main():
    args = parse_args()
    data_dir = args.data_dir

    print("Loading artefacts ...")
    artefacts = load_artefacts(data_dir)

    print("Plotting ...")
    plot_logit_histogram(artefacts, os.path.join(data_dir, "logit_histogram.png"))
    plot_prob_histogram( artefacts, os.path.join(data_dir, "prob_histogram.png"))
    plot_per_slot_bce(   artefacts, os.path.join(data_dir, "per_slot_bce.png"))
    plot_per_epoch_home( artefacts, os.path.join(data_dir, "per_epoch_home.png"))

    print("Writing markdown report ...")
    summary = summarise(artefacts)
    write_markdown(
        summary, artefacts,
        os.path.join(data_dir, "diagnostics_H_Tanh_vs_G4.md"),
    )

    print("\nDone. Outputs:")
    for f in sorted(os.listdir(data_dir)):
        fp = os.path.join(data_dir, f)
        if os.path.isfile(fp):
            print(f"  {fp}")


if __name__ == "__main__":
    main()
