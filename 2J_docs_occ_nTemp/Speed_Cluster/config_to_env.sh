#!/encs/bin/bash
# config_to_env.sh — YAML → env-export translator (yq-based)
# Usage (source from job script): source config_to_env.sh configs/F8.yaml
# Sets: export VAR=value for each env key present; export PY_ARGS for argparse flags.
# Missing keys → no emission → 04D_train.py uses its built-in defaults unchanged.
# Falls back to config_to_env.py when yq is unavailable.

YAML_FILE="${1:?Usage: source config_to_env.sh configs/TRIAL.yaml}"

if ! command -v yq &>/dev/null; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
    eval "$("$PYTHON" "${SCRIPT_DIR}/config_to_env.py" "$YAML_FILE")"
    return 0
fi

_yq_val() { yq ".$1 // empty" "$YAML_FILE" 2>/dev/null; }

# ── Env-var keys ──────────────────────────────────────────────────────────────
declare -A _ENV_MAP=(
    [lambda_act]=LAMBDA_ACT
    [lambda_home]=LAMBDA_HOME
    [lambda_cop]=LAMBDA_COP
    [lambda_marg]=LAMBDA_MARG
    [marg_mode]=MARG_MODE
    [aux_stratum_lambda]=AUX_STRATUM_LAMBDA
    [spouse_neg_weight]=SPOUSE_NEG_WEIGHT
    [aux_stratum_head]=AUX_STRATUM_HEAD
    [cop_pos_weight]=COP_POS_WEIGHT
    [cop_alone_pw]=COP_ALONE_PW
    [activity_boosts]=ACTIVITY_BOOSTS
    [data_side_sampling]=DATA_SIDE_SAMPLING
    [sched_sample_p]=SCHED_SAMPLE_P
    [home_label_smooth]=HOME_LABEL_SMOOTH
)

for yaml_key in "${!_ENV_MAP[@]}"; do
    _val=$(_yq_val "$yaml_key")
    if [ -n "$_val" ]; then
        export "${_ENV_MAP[$yaml_key]}=$_val"
    fi
done

# ── Argparse-flag keys ────────────────────────────────────────────────────────
PY_ARGS=""

for flag in data_dir batch_size max_epochs patience lr d_model n_heads n_enc_layers n_dec_layers; do
    _val=$(_yq_val "$flag")
    if [ -n "$_val" ]; then
        PY_ARGS="$PY_ARGS --${flag} $_val"
    fi
done

# Boolean store_true flags
for flag in fp16 sample; do
    _val=$(_yq_val "$flag")
    if [ "$_val" = "true" ]; then
        PY_ARGS="$PY_ARGS --$flag"
    fi
done

export PY_ARGS
