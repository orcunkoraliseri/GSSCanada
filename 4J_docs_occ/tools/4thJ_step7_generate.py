# -*- coding: utf-8 -*-
"""Step 7, work item 7.3 -- constrained generation with vLLM + XGrammar.

  usage: python 4thJ_step7_generate.py --fold es --n 600 [--no-grammar]
                                       [--leg 4] [--out DIR]

Two modes, and the pair is the point:

  * **constrained**   -- the EBNF from `4thJ_step7_ebnf.py` is handed to vLLM's
    structured-output back-end, which is XGrammar. Output is valid by
    construction, and `G7.1`-`G7.4` cannot fail while it is on.
  * **`--no-grammar`** -- the same adapter, the same prompts, the same seed, the
    same temperature, with the mask OFF. This is work item 7.5's rejection-sampled
    control, and it is the only thing that makes the constrained batch's validity
    rate a MEASUREMENT rather than a tautology.

🔴 Under `D-S7-3` (a) every Leg-4 run is a REHEARSAL. Each output record carries
`"provenance": "LEG-4 PILOT -- NOT REPORTABLE"` in the file itself, not in a
README beside it, so a number lifted out of the artefact carries its own warning.

🔴 The oracle scores every generated record here, INCLUDING in constrained mode.
Trusting the back-end to have honoured its own grammar is exactly the assumption
`G7.10` exists to test; a constrained batch that the oracle rejects is a defect
in the back-end and must be visible, not assumed away.
"""

import argparse
import importlib
import json
import os
import random
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

grammar = importlib.import_module("4thJ_step7_grammar")
ebnf = importlib.import_module("4thJ_step7_ebnf")

PROVENANCE_LEG4 = "LEG-4 PILOT -- NOT REPORTABLE"


class NotRun(RuntimeError):
    """The run could not be performed. Distinct from the run producing bad output."""


def describe_vllm(vllm):
    print("vllm version : %s" % getattr(vllm, "__version__", "unknown"))
    for mod in ("vllm.sampling_params",):
        try:
            m = importlib.import_module(mod)
            print("%s: %s" % (mod, ", ".join(sorted(
                n for n in dir(m) if not n.startswith("_")))))
        except Exception as e:
            print("%s: unavailable (%s)" % (mod, e))


def structured_params(text):
    """Return (name, kwargs) attaching the EBNF to a SamplingParams call.

    vLLM renamed this twice. Detected, printed, and if neither name is present the
    run stops -- generating unconstrained output and filing it as constrained
    would be the worst possible outcome of an API change.
    """
    sp = importlib.import_module("vllm.sampling_params")
    cls = getattr(sp, "StructuredOutputsParams", None)
    if cls is not None:
        return "structured_outputs=StructuredOutputsParams(grammar=...)", \
               {"structured_outputs": cls(grammar=text)}
    cls = getattr(sp, "GuidedDecodingParams", None)
    if cls is not None:
        return "guided_decoding=GuidedDecodingParams(grammar=...)", \
               {"guided_decoding": cls(grammar=text)}
    raise NotRun("this vLLM exposes neither StructuredOutputsParams nor "
                 "GuidedDecodingParams; refusing to generate unconstrained output "
                 "and label it constrained")


def load_prefixes(path, n, seed):
    """A reproducible draw of `n` prefixes, and the draw is recorded.

    Not `[:n]`. 🔴 `FINDING 1`: a plain head-of-file cap on a country-ordered
    shard nearly trained the Step 4 pilot on Italy alone. These files are ordered
    by stratum, so a head cap here would generate one corner of the population and
    every downstream score would be of that corner.
    """
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    if not rows:
        raise NotRun("no prefixes in %s" % path)
    if n >= len(rows):
        return rows, len(rows)
    return random.Random(seed).sample(rows, n), len(rows)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--fold", required=True, choices=("es", "uk", "it"))
    ap.add_argument("--leg", type=int, default=4)
    ap.add_argument("--n", type=int, default=600)
    ap.add_argument("--no-grammar", action="store_true",
                    help="work item 7.5 control: same everything, mask OFF")
    ap.add_argument("--step2", required=True)
    ap.add_argument("--config", required=True, help="generation_config_<fold>.json")
    ap.add_argument("--prefixes", required=True, help="prefixes_<fold>.jsonl")
    ap.add_argument("--tag", default=None,
                    help="output filename tag; default constrained/nogrammar")
    ap.add_argument("--out", required=True)
    ap.add_argument("--gpu-mem", type=float, default=0.90)
    ap.add_argument("--max-model-len", type=int, default=2048)
    # torch.compile is OFF by default. `envs/step7` was created from `envs/step4`s
    # interpreter, so its stdlib lives under `envs/step4/lib/python3.10` while its
    # site-packages live under `envs/step7`; dynamo hashes the source of the stdlib
    # modules it traces and raises `Source mismatch for collections.abc`. Compilation
    # is a SPEED optimisation only -- eager mode produces the same tokens -- so the
    # rehearsal runs eager rather than have the environment shape the sampler.
    ap.add_argument("--compile", action="store_true",
                    help="opt back in to torch.compile (expected to fail here)")
    a = ap.parse_args(argv)

    with open(a.config, encoding="utf-8") as fh:
        cfg = json.load(fh)
    if cfg["fold"] != a.fold:
        raise NotRun("config is for fold %r, not %r" % (cfg["fold"], a.fold))

    mode = "UNCONSTRAINED (7.5 control)" if a.no_grammar else "CONSTRAINED"
    print("=" * 78)
    print("Step 7.3 generation -- fold %s, leg %d, %s, n=%d" % (a.fold, a.leg, mode, a.n))
    print("=" * 78)
    print("base       : %s @ %s" % (cfg["base_repo"], cfg.get("base_revision", "?")))
    print("adapter    : %s" % cfg["adapter"])
    print("temperature: %s  (basis: %s)" % (cfg["temperature"], cfg.get("temperature_basis")))
    print("top_p %s | top_k %s | max_new_tokens %s | seed %s"
          % (cfg["top_p"], cfg["top_k"], cfg["max_new_tokens"], cfg["generation_seed"]))

    if a.leg == 4:
        print("\n🔴 %s -- Leg-4 is the PILOT. D-S7-3 (a): this run rehearses the\n"
              "   pipeline, it does not produce a number for the paper.\n" % PROVENANCE_LEG4)

    if not os.path.isdir(cfg["adapter"]):
        raise NotRun("no adapter at %s" % cfg["adapter"])
    rank = None
    acfg = os.path.join(cfg["adapter"], "adapter_config.json")
    if os.path.exists(acfg):
        with open(acfg, encoding="utf-8") as fh:
            rank = json.load(fh).get("r")
    print("lora rank  : %s (read from adapter_config.json)" % rank)

    alph = grammar.build_alphabets(a.step2)
    # 🔴 `whole_record=False`. `FINDING 80`: the prompt already carries the six
    # prefix fields and the `|`, so the decoder must be masked with the COMPLETION
    # grammar. Handed the whole-record root, XGrammar matched the episodes against
    # `PF` -- which accepts any run of `[0-9a-zA-Z_+-]` -- and 16 of 16 diaries ran
    # to `max_tokens` inside prefix field six. The oracle and `G7.10` keep the
    # whole-record root; only what is handed to vLLM changes.
    text = ebnf.build_ebnf(alph, whole_record=False)
    print("EBNF       : %d chars, ACT %d | ACT2 %d | LOC %d | COP %d"
          % (len(text), len(alph["act"]), len(alph["act2"]),
             len(alph["loc"]), len(alph["cop"])))

    prefixes, n_pool = load_prefixes(a.prefixes, a.n, cfg.get("prompt_seed", 42))
    prompts = [r["prefix"] + grammar.PREFIX_BODY_SEP for r in prefixes]
    print("prompts    : %d drawn from a pool of %d, seed %s"
          % (len(prompts), n_pool, cfg.get("prompt_seed", 42)))

    import vllm
    describe_vllm(vllm)
    from vllm import LLM, SamplingParams
    from vllm.lora.request import LoRARequest

    sp_kwargs = dict(temperature=cfg["temperature"],
                     top_p=cfg["top_p"],
                     top_k=cfg["top_k"] if cfg["top_k"] else -1,
                     max_tokens=cfg["max_new_tokens"],
                     seed=cfg["generation_seed"],
                     stop=[grammar.EOR],
                     include_stop_str_in_output=True)
    if a.no_grammar:
        struct_name = "none (--no-grammar)"
    else:
        struct_name, extra = structured_params(text)
        sp_kwargs.update(extra)
    print("structured : %s" % struct_name)

    t0 = time.time()
    llm = LLM(model=cfg["base_repo"], revision=cfg.get("base_revision"),
              enable_lora=True, max_lora_rank=rank or 16,
              dtype="bfloat16", gpu_memory_utilization=a.gpu_mem,
              max_model_len=a.max_model_len, seed=cfg["generation_seed"],
              enforce_eager=not a.compile)
    load_s = time.time() - t0
    print("engine up in %.1f s" % load_s)

    params = SamplingParams(**sp_kwargs)
    t0 = time.time()
    outs = llm.generate(prompts, params,
                        lora_request=LoRARequest(a.fold, 1, cfg["adapter"]))
    gen_s = time.time() - t0
    print("generated %d diaries in %.1f s (%.2f diaries/s)"
          % (len(outs), gen_s, len(outs) / max(gen_s, 1e-9)))

    pol = grammar.TransitionPolicy.PERMISSIVE
    os.makedirs(a.out, exist_ok=True)
    # `--tag` exists for `G6.7`: five fictional-country levels share a fold and a
    # leg and would otherwise overwrite one another -- the cache-key-collision
    # class of `FINDING 8`. Default unchanged, so nothing already run moves.
    tag = a.tag or ("nogrammar" if a.no_grammar else "constrained")
    path = os.path.join(a.out, "generated_leg%d_%s_%s.jsonl" % (a.leg, a.fold, tag))

    n_valid = 0
    n_terminated = 0
    reasons = {}
    with open(path, "w", encoding="utf-8") as fh:
        for row, out in zip(prefixes, outs):
            body = out.outputs[0].text
            full = out.prompt + body
            ok, why = grammar.validate_record(full, alph, pol)
            n_valid += 1 if ok else 0
            n_terminated += 1 if full.endswith(grammar.EOR) else 0
            if not ok:
                key = why.split(" (")[0][:60]
                reasons[key] = reasons.get(key, 0) + 1
            rec = dict(row)
            rec.update({"text": full, "oracle_valid": ok, "oracle_reason": why,
                        "leg": a.leg, "grammar": not a.no_grammar,
                        "temperature": cfg["temperature"],
                        "generation_seed": cfg["generation_seed"],
                        "finish_reason": out.outputs[0].finish_reason,
                        "n_out_tokens": len(out.outputs[0].token_ids)})
            if a.leg == 4:
                rec["provenance"] = PROVENANCE_LEG4
            fh.write(json.dumps(rec, sort_keys=True) + "\n")

    print("\nvalid by the oracle : %d / %d (%.2f %%)"
          % (n_valid, len(outs), 100.0 * n_valid / max(len(outs), 1)))
    print("terminated with %s : %d / %d" % (grammar.EOR, n_terminated, len(outs)))
    if reasons:
        print("rejection reasons:")
        for k in sorted(reasons, key=lambda x: -reasons[x]):
            print("  %5d  %s" % (reasons[k], k))

    # 🔴 A constrained batch the oracle rejects is a back-end defect. Said loudly
    # here rather than left for whoever reads the parquet three steps later.
    if not a.no_grammar and n_valid != len(outs):
        print("\n🔴 THE MASK WAS ON AND %d RECORD(S) ARE STILL INVALID. Either the "
              "grammar\n   does not say what the oracle says, or vLLM did not apply it. "
              "Do not\n   score this batch." % (len(outs) - n_valid))

    summary = {
        "fold": a.fold, "leg": a.leg, "constrained": not a.no_grammar,
        "n": len(outs), "n_valid": n_valid, "n_terminated": n_terminated,
        "valid_rate": round(n_valid / max(len(outs), 1), 6),
        "engine_load_seconds": round(load_s, 2),
        "generate_seconds": round(gen_s, 2),
        "diaries_per_second": round(len(outs) / max(gen_s, 1e-9), 4),
        "structured_api": struct_name,
        "base_repo": cfg["base_repo"], "base_revision": cfg.get("base_revision"),
        "adapter": cfg["adapter"], "lora_rank": rank,
        "temperature": cfg["temperature"], "top_p": cfg["top_p"], "top_k": cfg["top_k"],
        "max_new_tokens": cfg["max_new_tokens"],
        "generation_seed": cfg["generation_seed"],
        "prompt_seed": cfg.get("prompt_seed", 42),
        "prefix_pool": n_pool,
        "rejection_reasons": reasons,
        "vllm_version": getattr(vllm, "__version__", "unknown"),
        "output": path,
    }
    if a.leg == 4:
        summary["provenance"] = PROVENANCE_LEG4
    spath = os.path.join(a.out, "generated_leg%d_%s_%s_summary.json" % (a.leg, a.fold, tag))
    with open(spath, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, sort_keys=True)
    print("\nwritten: %s\nwritten: %s" % (path, spath))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except NotRun as e:
        print("\n" + "=" * 78)
        print("GENERATION NOT RUN -- %s" % e)
        print("=" * 78)
        sys.exit(2)
