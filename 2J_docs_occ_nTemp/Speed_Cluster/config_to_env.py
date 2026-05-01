#!/usr/bin/env python3
"""
config_to_env.py — YAML → env-export translator (no external dependencies).
Usage: eval $(python config_to_env.py configs/F8.yaml)
Emits: export VAR=value  and  export PY_ARGS="--flag val ..."
Missing keys → not emitted → 04D_train.py uses its built-in defaults.
Parses simple flat key: value YAML only (no nested structures, no PyYAML needed).
"""
import sys

ENV_MAP = {
    "lambda_act":         "LAMBDA_ACT",
    "lambda_home":        "LAMBDA_HOME",
    "lambda_cop":         "LAMBDA_COP",
    "lambda_marg":        "LAMBDA_MARG",
    "marg_mode":          "MARG_MODE",
    "aux_stratum_lambda": "AUX_STRATUM_LAMBDA",
    "spouse_neg_weight":  "SPOUSE_NEG_WEIGHT",
    "aux_stratum_head":   "AUX_STRATUM_HEAD",
    "cop_pos_weight":     "COP_POS_WEIGHT",
    "cop_alone_pw":       "COP_ALONE_PW",
    "activity_boosts":    "ACTIVITY_BOOSTS",
    "data_side_sampling": "DATA_SIDE_SAMPLING",
    "sched_sample_p":     "SCHED_SAMPLE_P",
    "home_label_smooth":  "HOME_LABEL_SMOOTH",
}

FLAG_KEYS = [
    "data_dir", "batch_size", "max_epochs", "patience", "lr",
    "d_model", "n_heads", "n_enc_layers", "n_dec_layers",
]
BOOL_FLAGS = ["fp16", "sample"]


def parse_yaml_flat(path):
    """Parse a flat (no-nesting) YAML file without PyYAML."""
    cfg = {}
    with open(path) as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            if ":" not in line:
                continue
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            if val.lower() == "true":
                cfg[key] = True
            elif val.lower() == "false":
                cfg[key] = False
            elif val == "" or val == "null":
                cfg[key] = None
            else:
                try:
                    cfg[key] = int(val)
                except ValueError:
                    try:
                        cfg[key] = float(val)
                    except ValueError:
                        cfg[key] = val
    return cfg


cfg = parse_yaml_flat(sys.argv[1])

lines = []
py_args = []

for yaml_key, env_var in ENV_MAP.items():
    if yaml_key in cfg and cfg[yaml_key] is not None:
        lines.append(f"export {env_var}={cfg[yaml_key]}")

for flag in FLAG_KEYS:
    if flag in cfg and cfg[flag] is not None:
        py_args.append(f"--{flag} {cfg[flag]}")

for flag in BOOL_FLAGS:
    if cfg.get(flag) is True:
        py_args.append(f"--{flag}")

lines.append(f'export PY_ARGS="{" ".join(py_args)}"')
print("\n".join(lines))
