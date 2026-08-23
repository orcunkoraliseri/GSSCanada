"""`FINDING 97` regression: the KV derivation must read `layer_types`, and the
guard must refuse a pool larger than the device.

Runs on a laptop. No GPU, no vLLM engine -- `engine_facts` reads only attribute
chains, so the engine is faked from the models' REAL shipped configs.
"""
import importlib
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

tp = importlib.import_module("4thJ_step7_throughput")

OK = FAIL = 0


def check(label, got, want):
    global OK, FAIL
    if got == want:
        OK += 1
        print("  ok   %-52s %s" % (label, got))
    else:
        FAIL += 1
        print("  FAIL %-52s got %r want %r" % (label, got, want))


class Obj(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)


def fake(hf, blocks, block_size=16, max_model_len=2048):
    cache = Obj(num_gpu_blocks=blocks, block_size=block_size,
                gpu_memory_utilization=0.9)
    model = Obj(hf_config=hf, max_model_len=max_model_len, dtype="torch.bfloat16")
    return Obj(llm_engine=Obj(vllm_config=Obj(
        cache_config=cache, model_config=model,
        parallel_config=Obj(tensor_parallel_size=1))))


# The two real shapes, from the configs the engine loaded on job 1286208.
OLMO_LAYERS = ["sliding_attention"] * 3 + ["full_attention"]
OLMO = Obj(num_attention_heads=32, num_key_value_heads=32, hidden_size=4096,
           num_hidden_layers=32, head_dim=128, vocab_size=100278,
           layer_types=OLMO_LAYERS * 8, sliding_window=4096)
QWEN = Obj(num_attention_heads=28, num_key_value_heads=4, hidden_size=3584,
           num_hidden_layers=28, head_dim=128, vocab_size=152064)

print("-- 1. the hybrid is read as a hybrid, not as 32 full layers")
o = tp.engine_facts(fake(OLMO, 29074))
check("layer_types counted", o["layer_types"],
      {"sliding_attention": 24, "full_attention": 8})
check("full-attention layers", o["full_attention_layers"], 8)
check("hybrid flagged", o["hybrid_attention"], True)
check("sliding window carried", o["sliding_window"], 4096)
check("KV bytes/token (corrected)", o["kv_bytes_per_token"], 131072)
check("KV bytes/token (old assumption kept)",
      o["kv_bytes_per_token_all_layers_assumption"], 524288)
check("the old figure is exactly 4x the new",
      o["kv_bytes_per_token_all_layers_assumption"] // o["kv_bytes_per_token"], 4)

print("-- 2. a uniform model is untouched by the fix")
q = tp.engine_facts(fake(QWEN, 65126))
check("no layer_types -> None", q["layer_types"], None)
check("hybrid not flagged", q["hybrid_attention"], False)
check("full layers = all layers", q["full_attention_layers"], 28)
check("KV bytes/token unchanged", q["kv_bytes_per_token"], 57344)
check("no phantom assumption row",
      q.get("kv_bytes_per_token_all_layers_assumption"), 57344)

print("-- 3. the corrected pools land within a GiB of each other, as they must")
GIB = 1024. ** 3
o_gib = o["kv_cache_tokens"] * o["kv_bytes_per_token"] / GIB
q_gib = q["kv_cache_tokens"] * q["kv_bytes_per_token"] / GIB
check("OLMo pool GiB", round(o_gib, 3), 56.785)
check("Qwen pool GiB", round(q_gib, 3), 55.65)
check("gap under 2 GiB", abs(o_gib - q_gib) < 2.0, True)
old_gib = o["kv_cache_tokens"] * o["kv_bytes_per_token_all_layers_assumption"] / GIB
check("the SHIPPED figure was 227.141", round(old_gib, 3), 227.141)

print("-- 4. the guard: it fires on the old number and is silent on the new one")
DEVICE = 74.506  # one nvidia_a100_7g.80gb
check("old figure exceeds the device", old_gib > DEVICE, True)
check("old figure is >3x the device", round(old_gib / DEVICE, 2), 3.05)
check("corrected figure fits", o_gib < DEVICE, True)
check("Qwen always fitted", q_gib < DEVICE, True)

print("-- 5. a zero parent-process peak is null, never a measured zero")
check("peak 0 -> None", (round(0 / GIB, 3) if 0 else None), None)

print("-- 6. the shipped artefact still says what this test was written from")
art = os.path.join(os.path.dirname(_HERE),
                   "Step7_docs", "outputs_step7", "throughput_comparison.json")
if os.path.exists(art):
    rows = {r["model"]: r for r in json.load(open(art))["rows"]}
    check("job 1286208 OLMo bytes/token", rows["allenai/Olmo-3-1025-7B"]["kv_bytes_per_token"],
          524288)
    check("job 1286208 OLMo blocks", rows["allenai/Olmo-3-1025-7B"]["num_gpu_blocks"], 29074)
    check("job 1286208 peak was 0.0",
          rows["allenai/Olmo-3-1025-7B"]["torch_peak_allocated_gib"], 0.0)
else:
    print("  .... artefact not present, section skipped")

print("\n%d ok, %d FAILED" % (OK, FAIL))
sys.exit(1 if FAIL else 0)
