"""D-S4-8 -- does the one-key fix actually repair G4.7? Seen, not asserted.

WHY THIS EXISTS
---------------
The investigation
(`Step4_docs/investigation/2026-08-23_G4.7_generation_does_not_terminate.md`) proved the
mechanism: `transformers/generation/utils.py:2835` masks an already-finished row only
when `has_eos_stopping_criteria` is true (`:2737`), which only `EosTokenCriteria` sets,
which `:1336` appends only when the model's generation config names an EOS --
and `Olmo-3-1025-7B` ships a `generation_config.json` with NO `eos_token_id`.

The FIX -- passing `eos_token_id=tokenizer.eos_token_id` beside `stop_strings` -- was
read off that guard's condition. 🔴 Reading a fix off a condition is not the same as
seeing it work, and this project does not accept the first for the second. This script
runs BOTH arms, back to back, on the same prefixes and the same seed:

    arm CONTROL : stop_strings only                 <- what Leg-5 `es` ran
    arm FIXED   : stop_strings + eos_token_id       <- the proposed repair

PRE-DECLARED, BEFORE THE FIRST RUN. What the fix must produce, or it is not the fix:

  1. FIXED  n_ends_with_eor == n           (G4.7 would PASS on this sample)
  2. FIXED  n_more_than_one_eor == 0       (the batch-padding fingerprint is gone)
  3. FIXED  new-token counts VARY within a batch
                                           (CONTROL's are constant per batch -- that
                                            constancy IS the defect, job 1286484)
  4. FIXED  n_eos_emitted == 0             (the EOS is here for its side effect on the
                                            mask; if it starts firing on its own it is
                                            cutting diaries short and the fix is wrong)
  5. BOTH   n_contains_eor == n            (G4.16: the model closes diaries in both
                                            arms. If this moves, the arms differ by
                                            something other than the mask and the
                                            comparison is void.)

🔴 IF CONTROL COMES BACK CLEAN, THE WHOLE RESULT IS VOID -- not a pass for the fix. A
control that does not reproduce the failure cannot show anything was repaired, and this
script says so rather than reporting the FIXED arm on its own.

The two arms share the seed, so they are not the same texts: temperature 1.0 sampling
diverges the moment the mask changes what a finished row emits. This compares
DISTRIBUTIONS OF TERMINATION, not texts, and that is all it claims.

Usage (GPU, sbatch only):
  REPLAY_N=16 REPLAY_BATCH=8 python 4thJ_step4_g47_fixcheck.py
"""
import os
import json

os.environ.setdefault("HF_HOME", "/speed-scratch/o_iseri/hf_cache")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

EOR = "<eor>"
REPO = "allenai/Olmo-3-1025-7B"
REV = "a81bae42db3975be1671e27b9c9a56da1a9f980f"
ADAPTER = "/speed-scratch/o_iseri/4J_step4/runs_leg5/leg5_primary_fold_es/adapter"
GEN = "/speed-scratch/o_iseri/4J_step4/diagnostics_leg5/generated_primary_es.jsonl"
N = int(os.environ.get("REPLAY_N", "16"))
BATCH = int(os.environ.get("REPLAY_BATCH", "8"))
MAXNEW = int(os.environ.get("REPLAY_MAXNEW", "1280"))
SEED = 42
OUT = os.environ.get("FIXCHECK_OUT", "/speed-scratch/o_iseri/4J_step4/g47_fixcheck.json")

print("transformers", transformers.__version__, "torch", torch.__version__, flush=True)

tok = AutoTokenizer.from_pretrained(REPO, revision=REV)
if tok.pad_token_id is None:
    tok.pad_token = tok.eos_token
eor_ids = tok(EOR, add_special_tokens=False)["input_ids"]
print("eor ids", eor_ids, "eos", tok.eos_token_id, repr(tok.eos_token),
      "pad", tok.pad_token_id, repr(tok.pad_token), flush=True)

# The root cause itself, printed rather than described: what the model repo ships.
try:
    gc_cfg = transformers.GenerationConfig.from_pretrained(REPO, revision=REV)
    print("generation_config eos_token_id ->", gc_cfg.eos_token_id,
          "  (None is the defect: no EosTokenCriteria, no padding mask)", flush=True)
except Exception as exc:                                    # pragma: no cover
    print("could not load GenerationConfig:", exc, flush=True)

model = AutoModelForCausalLM.from_pretrained(REPO, revision=REV,
                                             torch_dtype=torch.bfloat16)
model = PeftModel.from_pretrained(model, ADAPTER)
model.to("cuda" if torch.cuda.is_available() else "cpu")
model.eval()
model.config.use_cache = True
dev = next(model.parameters()).device
print("device", dev, flush=True)

recs = [json.loads(l) for l in open(GEN, encoding="utf-8")][:N]
prefixes = [r["prompt_text"].split("|", 1)[0] + "|" for r in recs]
print("prefixes", len(prefixes), "batch", BATCH, "max_new", MAXNEW, flush=True)


def run_arm(name, extra_kw):
    """One generation pass over all prefixes. Seed reset so both arms start equal."""
    print("=" * 78, flush=True)
    print("ARM %s   generate kwargs beyond the common ones: %s"
          % (name, {k: (v if not hasattr(v, "name_or_path") else "<tokenizer>")
                    for k, v in extra_kw.items()}), flush=True)
    print("=" * 78, flush=True)
    torch.manual_seed(SEED)
    old = tok.padding_side
    tok.padding_side = "left"
    rows = []
    try:
        with torch.no_grad():
            for i in range(0, len(prefixes), BATCH):
                chunk = prefixes[i:i + BATCH]
                enc = tok(chunk, add_special_tokens=False, return_tensors="pt",
                          padding=True).to(dev)
                plen = enc["input_ids"].shape[1]
                gen = model.generate(**enc, max_new_tokens=MAXNEW, do_sample=True,
                                     temperature=1.0, top_p=1.0,
                                     pad_token_id=tok.pad_token_id, **extra_kw)
                for j in range(gen.shape[0]):
                    ids = gen[j].tolist()
                    new = ids[plen:]
                    # the decode the trainer itself does -- pads dropped, so this is the
                    # text G4.7 and G4.16 would actually be scored on
                    txt = tok.decode(ids, skip_special_tokens=True)
                    row = {"i": i + j, "batch": i // BATCH,
                           "n_new_tokens": len(new),
                           "n_new_nonpad": sum(1 for t in new
                                               if t != tok.pad_token_id),
                           "pad_tail": sum(1 for t in reversed(new)
                                           if t == tok.pad_token_id),
                           "ends_with_eor": txt.rstrip().endswith(EOR),
                           "n_eor_in_text": txt.count(EOR),
                           "eos_emitted": tok.eos_token_id in new}
                    rows.append(row)
                    print("  seq %2d [b%d] new=%4d nonpad=%4d padtail=%4d  "
                          "ends=%-5s n_eor=%2d eos=%s"
                          % (row["i"], row["batch"], row["n_new_tokens"],
                             row["n_new_nonpad"], row["pad_tail"],
                             row["ends_with_eor"], row["n_eor_in_text"],
                             row["eos_emitted"]), flush=True)
    finally:
        tok.padding_side = old

    n = len(rows)
    # per-batch spread of NONPAD length. Under the defect every row in a batch runs to
    # the slowest member, so this is 0 for every batch; repaired, rows stop when they
    # are done and it is > 0.
    spreads = {}
    for r in rows:
        spreads.setdefault(r["batch"], []).append(r["n_new_nonpad"])
    per_batch_spread = {b: (max(v) - min(v)) for b, v in spreads.items()}
    summ = {"arm": name, "n": n,
            "n_ends_with_eor": sum(1 for r in rows if r["ends_with_eor"]),
            "n_contains_eor": sum(1 for r in rows if r["n_eor_in_text"] >= 1),
            "n_more_than_one_eor": sum(1 for r in rows if r["n_eor_in_text"] > 1),
            "n_eos_emitted": sum(1 for r in rows if r["eos_emitted"]),
            "n_with_pad_tail": sum(1 for r in rows if r["pad_tail"] > 0),
            "per_batch_nonpad_spread": per_batch_spread,
            "n_batches_with_zero_spread": sum(1 for v in per_batch_spread.values()
                                              if v == 0),
            "rows": rows}
    print("ARM %s SUMMARY %s"
          % (name, json.dumps({k: v for k, v in summ.items() if k != "rows"})),
          flush=True)
    return summ


control = run_arm("CONTROL (stop_strings only -- what Leg-5 es ran)",
                  {"stop_strings": [EOR], "tokenizer": tok})
fixed = run_arm("FIXED (stop_strings + eos_token_id -- D-S4-8)",
                {"stop_strings": [EOR], "tokenizer": tok,
                 "eos_token_id": tok.eos_token_id})

# ------------------------------------------------------------------ the pre-declared
print("=" * 78, flush=True)
print("D-S4-8 PRE-DECLARED CHECKS", flush=True)
print("=" * 78, flush=True)

n = control["n"]
checks = []


def chk(key, ok, text):
    checks.append({"check": key, "ok": bool(ok), "text": text})
    print("  %-28s %s  %s" % (key, "PASS" if ok else "🔴 FAIL", text), flush=True)


# 0 -- the control must reproduce the failure, or nothing below means anything
control_reproduces = (control["n_ends_with_eor"] < n
                      or control["n_more_than_one_eor"] > 0)
chk("0 control reproduces",
    control_reproduces,
    "CONTROL ends_with_eor %d/%d, %d texts carry >1 <eor>, %d of %d batches have ZERO "
    "length spread. If this is clean the comparison is VOID."
    % (control["n_ends_with_eor"], n, control["n_more_than_one_eor"],
       control["n_batches_with_zero_spread"], len(control["per_batch_nonpad_spread"])))

chk("1 fixed terminates",
    fixed["n_ends_with_eor"] == n,
    "FIXED ends_with_eor %d/%d (G4.7 would %s on this sample)"
    % (fixed["n_ends_with_eor"], n,
       "PASS" if fixed["n_ends_with_eor"] == n else "FAIL"))

chk("2 fingerprint gone",
    fixed["n_more_than_one_eor"] == 0,
    "FIXED texts carrying more than one <eor>: %d (was %d in CONTROL)"
    % (fixed["n_more_than_one_eor"], control["n_more_than_one_eor"]))

chk("3 lengths decouple",
    all(v > 0 for v in fixed["per_batch_nonpad_spread"].values()),
    "FIXED per-batch nonpad spread %s vs CONTROL %s. Zero means the rows are still "
    "locked to the slowest member of their batch."
    % (fixed["per_batch_nonpad_spread"], control["per_batch_nonpad_spread"]))

chk("4 eos never fires alone",
    fixed["n_eos_emitted"] == 0,
    "FIXED sequences that emitted %s: %d. Non-zero means the EOS is cutting diaries "
    "short on its own, which is NOT what it was added for."
    % (tok.eos_token_id, fixed["n_eos_emitted"]))

chk("5 G4.16 unmoved",
    control["n_contains_eor"] == n and fixed["n_contains_eor"] == n,
    "contains <eor>: CONTROL %d/%d, FIXED %d/%d. The model closes diaries in both arms; "
    "the arms differ only in the mask."
    % (control["n_contains_eor"], n, fixed["n_contains_eor"], n))

all_ok = all(c["ok"] for c in checks)
if not control_reproduces:
    verdict = ("🔴 VOID -- the CONTROL arm did not reproduce the failure, so nothing here "
               "shows the fix repaired anything. Do NOT quote the FIXED arm. Read why "
               "the control came back clean first (sample too small? wrong adapter? "
               "prefixes not the failing ones?).")
elif all_ok:
    verdict = ("🟢 D-S4-8 FIX SEEN WORKING on %d sequences at batch %d: CONTROL "
               "%d/%d terminate, FIXED %d/%d, and all five pre-declared checks hold. "
               "This is a GENERATION-side demonstration on the `es` adapter; it does "
               "not re-score any gate and it is not a fold result."
               % (n, BATCH, control["n_ends_with_eor"], n, fixed["n_ends_with_eor"], n))
else:
    verdict = ("🔴 THE FIX IS NOT DEMONSTRATED. %d of %d pre-declared checks failed: %s. "
               "Do not apply it to a fold run."
               % (sum(1 for c in checks if not c["ok"]), len(checks),
                  [c["check"] for c in checks if not c["ok"]]))
print(verdict, flush=True)

out = {"decision": "D-S4-8", "transformers": transformers.__version__,
       "repo": REPO, "revision": REV, "adapter": ADAPTER,
       "n": n, "batch": BATCH, "max_new_tokens": MAXNEW, "seed": SEED,
       "eor_ids": eor_ids, "eos_token_id": tok.eos_token_id,
       "pad_token_id": tok.pad_token_id,
       "control": control, "fixed": fixed,
       "checks": checks, "control_reproduces_failure": control_reproduces,
       "verdict": verdict,
       "scope": "generation-side demonstration on the es adapter. NOT a gate score, NOT "
                "a fold result, and it says nothing about G4.1."}
with open(OUT, "w") as fh:
    json.dump(out, fh, indent=2, default=str)
print("wrote", OUT, flush=True)
