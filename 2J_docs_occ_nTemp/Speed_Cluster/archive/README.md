# 04B_model.py architecture archive

Each file is a frozen snapshot of `2J_docs_occ_nTemp/04B_model.py` for one Step-4 trial-series state. Standing rule: every architecture edit copies the predecessor here in the same commit as the edit. Earlier files in this lineage were backfilled from `git log` after the rule was adopted.

## Lineage

| Snapshot file              | Series state | Source commit / equivalence                                                                 |
|----------------------------|--------------|---------------------------------------------------------------------------------------------|
| `04B_model_G1.py`          | G1           | `0fb5561` (F-final). G1 was config-only on the F-series architecture.                       |
| `04B_model_G2.py`          | G2           | `618b564` (architecture edit landed alongside G2/G3/G4 sweep configs). Identical to G3, G4. |
| `04B_model_G3.py`          | G3           | `618b564`. Identical to G2, G4.                                                             |
| `04B_model_G4.py`          | G4           | `618b564`. Original archive written by `7fcf872`.                                           |
| `04B_model_H_Tanh.py`      | H_Tanh       | `7fcf872` (H-Tier-1 pre-flight: H_Tanh / H4 / H6 env-var gates). Also H4, H6.               |
| `04B_model_H_Time.py`      | H_Time       | `b22f1a3` + uncommitted drift (learnable PE + cyclical time features). Same as `pre_HNAT`.  |
| `04B_model_pre_HNAT.py`    | H_Time       | Legacy name for H_Time snapshot — retained because `step4_training_v3.md` cites it.         |
| `04B_model_H_NAT.py`       | H_NAT        | Working tree at the H_NAT run (encoder-only stack added on top of H_Time). Same as `pre_I1`.|
| `04B_model_pre_I1.py`      | H_NAT        | Legacy name for H_NAT snapshot — retained because `step4_training_v3.md` cites it.          |
| `04B_model_J4.py`          | J4_1 / J4_2  | `04B_model.py` at J-4 series start (2026-05-08). Contains `enable_temporal_injection` (J4_1) and `enable_hierarchical_cop` (J4_2) flags. J4_3 uses frozen J3 arch — no separate snapshot needed. |
| `04D_train_J4.py`          | J4_3         | `04D_train.py` at J-4 series start (2026-05-08). Adds `LAMBDA_LOGIC` env var + `loss_logic = (p_alone * p_others).mean()` term to `compute_loss()`. Default `LAMBDA_LOGIC=0.0` keeps J1/J2/J3 unaffected. |
| (live `04B_model.py`)      | J4_1 / J4_2  | Enable flags: `enable_temporal_injection` (J4_1), `enable_hierarchical_cop` (J4_2). Archived as `04B_model_J4.py`. |

## Notes

- G2/G3/G4 share one architecture snapshot — only configs (`lambda_home`, `aux_stratum_*`, `activity_boosts`, etc.) differed across the three.
- H_Tanh / H4 / H6 also share one architecture snapshot, gated at runtime by env-vars.
- `pre_HNAT` and `pre_I1` are kept under their original filenames so existing v2/v3 docs stay valid; the `H_Time` and `H_NAT` files are the canonical post-rule names.
