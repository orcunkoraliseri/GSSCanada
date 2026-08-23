import json, collections
tp   = json.load(open("throughput_comparison.json"))
cfg  = json.load(open("throughput_evidence/olmo3_7b_config.json"))
lt   = collections.Counter(cfg["layer_types"])
GIB  = 1024**3
CARD = 80e9            # A100 80 GB, the named GRES
rows = {r["model"]: r for r in tp["rows"]}
o, q = rows["allenai/Olmo-3-1025-7B"], rows["Qwen/Qwen2.5-7B"]

def bpt(layers, kvh, hd, bytes_per=2):
    return 2 * layers * kvh * hd * bytes_per

full = lt["full_attention"]
out = {
  "layer_types": dict(lt),
  "sliding_window": cfg["sliding_window"],
  "max_model_len": o["max_model_len"],
  "reported": {
    "olmo_kv_bytes_per_token": o["kv_bytes_per_token"],
    "olmo_kv_cache_gib": o["kv_cache_gib"],
    "qwen_kv_cache_gib": q["kv_cache_gib"],
    "reported_ratio_bytes_per_token": round(o["kv_bytes_per_token"]/q["kv_bytes_per_token"], 4),
  },
}
# what the reported GiB implies against the physical card
out["impossibility"] = {
  "olmo_reported_gib": o["kv_cache_gib"],
  "physical_card_gib": round(CARD/GIB, 3),
  "times_the_whole_card": round(o["kv_cache_gib"]/(CARD/GIB), 3),
  "qwen_reported_gib": q["kv_cache_gib"],
  "qwen_fits": q["kv_cache_gib"] < CARD/GIB,
}
# full-attention-only accounting
bpt_full = bpt(full, o["num_key_value_heads"], o["head_dim"])
gib_full = o["kv_cache_tokens"] * bpt_full / GIB
out["full_attention_only"] = {
  "full_attention_layers": full,
  "sliding_attention_layers": lt["sliding_attention"],
  "kv_bytes_per_token": bpt_full,
  "implied_gib": round(gib_full, 3),
  "qwen_gib": q["kv_cache_gib"],
  "gap_to_qwen_gib": round(gib_full - q["kv_cache_gib"], 3),
  "ratio_bytes_per_token_vs_qwen": round(bpt_full/q["kv_bytes_per_token"], 4),
  "reported_over_corrected": round(o["kv_bytes_per_token"]/bpt_full, 4),
}
# the measured half, which is untouched by any of this
out["measured_and_sound"] = {
  "olmo_diaries_per_second": o["diaries_per_second"],
  "qwen_diaries_per_second": q["diaries_per_second"],
  "olmo_over_qwen": round(o["diaries_per_second"]/q["diaries_per_second"], 4),
  "olmo_output_tokens_per_diary": o["output_tokens_mean"],
  "qwen_output_tokens_per_diary": q["output_tokens_mean"],
  "output_tokens_olmo_over_qwen": round(o["output_tokens_mean"]/q["output_tokens_mean"], 4),
  "olmo_max_concurrency": o["max_concurrency_at_max_len"],
  "qwen_max_concurrency": q["max_concurrency_at_max_len"],
}
out["peak_memory"] = {
  "olmo_torch_peak_allocated_gib": o["torch_peak_allocated_gib"],
  "qwen_torch_peak_allocated_gib": q["torch_peak_allocated_gib"],
  "both_identically_zero": o["torch_peak_allocated_gib"] == 0.0 == q["torch_peak_allocated_gib"],
}
print(json.dumps(out, indent=2))
json.dump(out, open("throughput_evidence/recheck.json","w"), indent=2)
