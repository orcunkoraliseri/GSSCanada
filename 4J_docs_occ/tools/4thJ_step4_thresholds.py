"""
Step 4 -- the single source of every threshold and every band.

V4.e: "the validator imports its thresholds from a single module. A second copy of a
band drifts invisibly from the first." The trainer imports this file too, so an in-run
detector and the post-hoc gate cannot disagree about where the line is.

🔴 NOTHING IN THIS FILE MAY BE CHANGED AFTER THE FIRST FOLD IS EVALUATED.
prereg.md section 9 freezes gates and thresholds once ANY fold has been scored. A change
made after seeing fold 1 contaminates folds 2 and 3 and does not show up in the output.
"""

# --- G4.1 within-stratum variance ratio -------------------------------------
G4_1_VR_LOW = 0.80
G4_1_VR_HIGH = 1.25
G4_1_MIN_STRATUM_N = 100      # strata smaller than this are not scored
V4_A_MIN_STRATA = 5           # fewer scorable strata than this => G4.1 FAILS, not skips

# 🔴 ASSUMPTION, recorded because neither the step doc nor the val doc defines
# "within-stratum variance" concretely. The quantity is the per-diary AT-HOME SHARE:
# sum(DUR where LOC == at_home) / sum(DUR). Chosen because it is the quantity this
# whole project exists to produce -- an occupancy schedule for a building model -- so a
# variance gate on it fails for reasons that matter downstream. Episode count per diary
# is computed and reported alongside it as a secondary, NOT scored.
G4_1_STATISTIC = "at_home_share"
G4_1_SECONDARY_REPORTED_NOT_SCORED = "episodes_per_diary"

# --- G4.2 delimiter vs content ----------------------------------------------
# V4.d: strict `<` on BOTH arms. A prediction of movement must not be satisfiable by
# nothing moving.
G4_2_DELIM_LOSS_HALT = 0.05
G4_2_ACT_ENTROPY_HALT_NATS = 1.5

# The single episode `collapse_content` writes in place of every real one. Field count and
# separators match a real episode exactly (dur,act,act2,loc,cop), so the FORMAT is intact
# and only the CONTENT is degenerate -- which is precisely the condition G4.2 halts on.
G4_2_COLLAPSE_EPISODE = "060,110,000,1,1"

# --- G4.3 shuffled-prefix cross-entropy -------------------------------------
G4_3_MIN_CE_RISE_NATS_PER_TOKEN = 0.15

# --- G4.4 slot-wise mutual information --------------------------------------
G4_4_EVENING_WINDOW = (18 * 60, 23 * 60)   # minutes from midnight, scored SEPARATELY
G4_4_MORNING_WINDOW = (6 * 60, 11 * 60)    # the control window
G4_4_SLOT_MINUTES = 30

# --- G4.5 padding labels ----------------------------------------------------
G4_5_REQUIRED_LABEL = -100
G4_5_REQUIRED_FRACTION = 1.0

# --- G4.6 adapter merge drift -----------------------------------------------
G4_6_MAX_LOGIT_DIFF = 1e-4
G4_6_SAMPLE_N = 64
# Execution parameter, NOT a band: how many of those 64 sequences are forwarded at once.
# FINDING 10 -- all 64 in one pass is a 32 GiB logit tensor and the gate OOMed. The
# statistic (max |logit difference| over every compared position) does not depend on it.
G4_6_MICRO_BATCH = 2

# --- G4.7 termination -------------------------------------------------------
G4_7_EOR = "<eor>"
G4_7_REQUIRED_FRACTION = 1.0

# --- G4.16 the model CAN close a diary --------------------------------------
# D-S4-8 (2026-08-23), companion to G4.7. G4.7 asks whether the returned text ENDS with
# <eor>; it cannot tell "the model never learned to close a diary" from "the harness
# never stopped generating". Leg-5 `es` read G4.7 107/600 while 600/600 of the same
# texts CONTAINED <eor> -- the model was fine, `generate()` was not. G4.16 reads the
# containment. Same threshold, on purpose: a model that cannot close a diary at all is
# as broken as one that never stops, and D-S4-7's split is only informative if both
# readings are scored.
G4_16_REQUIRED_FRACTION = 1.0

# --- G4.8 tokenizer round-trip ----------------------------------------------
G4_8_CASES = 1000

# --- G4.9 per-country probe stability ---------------------------------------
G4_9_MAX_REGRESSION_FRACTION = 0.05   # final within +5 % of its own best

# --- G4.10 memory and walltime ----------------------------------------------
G4_10_REPORTED_NOT_THRESHOLDED = True
G4_10_WALLTIME_DAYS = 7

# --- G4.13 fold isolation ---------------------------------------------------
G4_13_MAX_HELDOUT_RECORDS_IN_TRAIN = 0   # exactly zero. This does not move.

# --- corpus / format constants ----------------------------------------------
PREFIX_BODY_SEP = "|"
PREFIX_FIELDS = ["country", "strat_age_band", "strat_sex", "strat_hh_type",
                 "strat_econ_status", "strat_day_type"]
LOC_AT_HOME = "at_home"

# --- the recipe, RL05, DO NOT RELITIGATE ------------------------------------
LORA_R = 32
LORA_ALPHA = 64
LORA_DROPOUT = 0.05
LORA_TARGET_MODULES = ["q_proj", "k_proj", "v_proj", "o_proj",
                       "gate_proj", "up_proj", "down_proj"]
USE_RSLORA = True
DTYPE = "bfloat16"
EPOCHS_LEG5 = 3
SEED = 42

# --- G4.4's verdict rule ----------------------------------------------------
# 🔴 ASSUMPTION, pre-specified here BEFORE any fold has been scored (prereg.md
# section 9 freezes thresholds only once a fold has been evaluated, and none has).
# The val doc says G4.4 is "MI(attributes ; activity) computed per slot against the
# empirical curve" and gives no number. Without a number it is a plot, not a gate.
# Rule: within each scored window, the MEAN generated MI must reach at least this
# fraction of the mean empirical MI. Chosen at one half because the failure shape
# named in the val doc -- "demographically appropriate mornings, generic evenings" --
# is a gross loss of conditioning in one window, not a subtle one, and a tighter band
# would fail on sampling noise at the generation volumes this project can afford.
G4_4_MIN_MI_RATIO = 0.50

# --- G4.12 within-stratum shuffle ------------------------------------------
# "G4.3 and G4.4 must both degrade materially under the shuffle." Materially is
# defined here, in advance: the same 0.15 nats/token that G4.3 itself uses, so the
# shuffle has to move the metric by as much as the gate's own threshold rather than
# by any amount at all.
G4_12_MIN_CE_RISE_NATS_PER_TOKEN = G4_3_MIN_CE_RISE_NATS_PER_TOKEN
G4_12_MIN_MI_DROP_RATIO = 0.10   # generated MI must fall by at least this fraction
