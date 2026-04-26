# configs/_schema.md — YAML key schema for Step-4 sweep configs

Single source of truth. Every key in a trial YAML maps 1:1 to either an env var
(read by `04D_train.py` at module level) or an argparse flag (passed via `$PY_ARGS`).
Missing keys → no emission → `04D_train.py` uses its built-in defaults unchanged.

---

## Identity keys (not emitted to env or args — used by submit machinery)

| YAML key | Type   | Description                                       |
|----------|--------|---------------------------------------------------|
| `tag`    | string | Trial tag; must match filename stem (e.g. `F9a`) |
| `seed`   | int    | Reserved for future seeding; currently informational only |

---

## Env-var keys (emitted as `export VAR=value`)

| YAML key              | Env var               | Default in 04D_train.py | Notes                                       |
|-----------------------|-----------------------|--------------------------|---------------------------------------------|
| `lambda_act`          | `LAMBDA_ACT`          | `1.0`                    | CE loss weight for activity head            |
| `lambda_home`         | `LAMBDA_HOME`         | `0.5`                    | BCE loss weight for AT_HOME head            |
| `lambda_cop`          | `LAMBDA_COP`          | `0.3`                    | BCE loss weight for co-presence head        |
| `lambda_marg`         | `LAMBDA_MARG`         | `0.1`                    | Marginal-bias loss weight                   |
| `marg_mode`           | `MARG_MODE`           | `global`                 | `global` or `per_cs`                        |
| `aux_stratum_lambda`  | `AUX_STRATUM_LAMBDA`  | `0.1`                    | Aux stratum-head loss multiplier (F9-a axis)|
| `spouse_neg_weight`   | `SPOUSE_NEG_WEIGHT`   | `1.0`                    | Spouse cop BCE pos_weight override (F9-b axis); < 1 down-weights Spouse=True |
| `aux_stratum_head`    | `AUX_STRATUM_HEAD`    | `0`                      | `0` or `1`; enables aux stratum prediction head |
| `cop_pos_weight`      | `COP_POS_WEIGHT`      | `0`                      | `0` or `1`; enables per-channel cop pos_weights from feature_config |
| `cop_alone_pw`        | `COP_ALONE_PW`        | `1`                      | `0` overrides Alone pos_weight to 1.0 (sign-flip guard) |
| `activity_boosts`     | `ACTIVITY_BOOSTS`     | `1`                      | `0` disables manual Work/Transit/Social class-weight boosts |
| `data_side_sampling`  | `DATA_SIDE_SAMPLING`  | `0`                      | `1` multiplies sampler weights by WGHT_PER  |

---

## Argparse-flag keys (accumulated into `$PY_ARGS`)

| YAML key          | Argparse flag      | Default in argparse | Notes                              |
|-------------------|--------------------|---------------------|------------------------------------|
| `data_dir`        | `--data_dir`       | `outputs_step4`     | Input tensor dir (relative to occModeling/) |
| `batch_size`      | `--batch_size`     | `256`               |                                    |
| `max_epochs`      | `--max_epochs`     | `100`               |                                    |
| `patience`        | `--patience`       | `15`                | Early stopping patience            |
| `lr`              | `--lr`             | `5e-5`              | Peak learning rate                 |
| `d_model`         | `--d_model`        | `256`               |                                    |
| `n_heads`         | `--n_heads`        | `8`                 |                                    |
| `n_enc_layers`    | `--n_enc_layers`   | `6`                 |                                    |
| `n_dec_layers`    | `--n_dec_layers`   | `6`                 |                                    |
| `fp16`            | `--fp16`           | `false`             | Boolean; `true` → adds `--fp16`    |
| `sample`          | `--sample`         | `false`             | Boolean; `true` → adds `--sample` (smoke mode: d_model=64, 5 epochs, CPU-friendly) |

**Note:** `output_dir` and `checkpoint_dir` are NOT in the YAML — the job array script
derives them from `TRIAL_TAG` as `outputs_step4_${TRIAL_TAG}` and
`outputs_step4_${TRIAL_TAG}/checkpoints`.

---

## Sweep-level keys (read by `submit_step4_array.sh`, not passed to individual trials)

| YAML key  | Type          | Description                                              |
|-----------|---------------|----------------------------------------------------------|
| `tags`    | list[string]  | Ordered list of trial tags to run in the array           |
| `smoke`   | bool          | If `true`, adds `--sample` to all trials (smoke-test mode) |
