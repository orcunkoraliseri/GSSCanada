"""_verify_warnings.py — evidence for Step5_6_warnings_investigation.md.

Deterministic, read-only. Quantifies the load-bearing defences for the
calibrated-J3 Step-5 non-PASS gates:
  (A) AT_HOME 2.2/6.1 is a day-type COMPOSITION artefact, not a model deficit
      -> within-stratum syn-vs-obs per-slot diff (raked ~exact)
      -> composition-held aggregate diff (collapses 4.4pp -> ~0.2pp)
  (B) night-slot (1-8 = 04:00-08:00) act30 breakdown behind the 67.5% sleep gate

Run:  cd <repo root> && py 2J_docs_occ_nTemp/Step5_docs/_verify_warnings.py
"""
import collections
from pathlib import Path
import numpy as np, pandas as pd

_HERE = Path(__file__).resolve().parent                  # 2J_docs_occ_nTemp/Step5_docs/
_BASE = _HERE.parent.parent                              # GSSCanada-main/
EXCL  = _BASE / "0_Occupancy" / "Outputs_21CEN22GSS" / "aug_pipeline" / "21CEN22GSS_aug_Full_Schedules_excl.csv"

HOM = [f"hom30_{i:03d}" for i in range(1, 49)]
ACT = [f"act30_{i:03d}" for i in range(1, 49)]
STRATA = [1, 2, 3]


def _share(d):
    v = d["DDAY_STRATA"].value_counts(normalize=True)
    return {int(s): round(float(v.get(s, 0)) * 100, 2) for s in STRATA}


def main():
    df = pd.read_csv(str(EXCL),
                     usecols=lambda c: c in (["DDAY_STRATA", "IS_SYNTHETIC"] + HOM + ACT),
                     low_memory=False)
    obs = df[df["IS_SYNTHETIC"] == 0]
    syn = df[df["IS_SYNTHETIC"] == 1]
    print(f"N total {len(df):,}  obs {len(obs):,}  syn {len(syn):,}")
    print(f"DDAY_STRATA % : obs {_share(obs)} | syn {_share(syn)} | all {_share(df)}")

    print("\n[A] within-stratum synthetic-vs-observed per-slot AT_HOME |diff| (raked => ~0):")
    for s in STRATA:
        o = obs[obs["DDAY_STRATA"] == s][HOM].values.mean(0)
        y = syn[syn["DDAY_STRATA"] == s][HOM].values.mean(0)
        print(f"  stratum {s}: max {np.abs(o - y).max()*100:.4f} pp   mean {np.abs(o - y).mean()*100:.4f} pp")

    agg_all = df[HOM].values.mean(0)
    agg_obs = obs[HOM].values.mean(0)
    print(f"\n[A] aggregate ALL-vs-OBS per-slot max|diff| (= gate 2.2): "
          f"{np.abs(agg_all - agg_obs).max()*100:.2f} pp")

    comp_obs = {s: float((obs["DDAY_STRATA"] == s).mean()) for s in STRATA}
    allm = {s: df[df["DDAY_STRATA"] == s][HOM].values.mean(0) for s in STRATA}
    held = sum(comp_obs[s] * allm[s] for s in STRATA)
    print(f"[A] COMPOSITION-HELD ALL-vs-OBS per-slot max|diff|: "
          f"{np.abs(held - agg_obs).max()*100:.4f} pp  (mean {np.abs(held - agg_obs).mean()*100:.4f} pp)")

    night = ACT[:8]                                       # slots 1-8 = 04:00-08:00
    vals = df[night].values.ravel()
    tot = len(vals)
    c = collections.Counter(vals.tolist())
    print("\n[B] night slots 1-8 act30 breakdown (top 6):")
    for k, v in sorted(c.items(), key=lambda x: -x[1])[:6]:
        print(f"  act {int(k):>2}: {v/tot*100:.2f}%")


if __name__ == "__main__":
    main()
