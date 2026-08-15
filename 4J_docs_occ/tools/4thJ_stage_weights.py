#!/usr/bin/env python3
"""4J Step 4.1 - pre-stage the model weights on /speed-scratch and record what was staged.

Three checkpoints, and the reason each is here:

  allenai/Olmo-3-1025-7B   Leg-5, the reported model
  allenai/OLMo-2-0425-1B   Leg-4, the pilot. Byte-identical tokenizer to Leg-5
  Qwen/Qwen2.5-7B          the named comparison arm, single pre-named fold

The deliverable is not the download. It is `staged_weights.json`, which records the
resolved commit hash of each repo. A model repo can be updated in place, so a
checkpoint named without a revision is not a reproducible checkpoint (Step 4, item 4.1,
gate G4.11).

Downloads only. No model is loaded, no GPU is touched, nothing is measured here.
"""

import json
import os
import sys
import time

REPOS = [
    ("allenai/Olmo-3-1025-7B", "leg5_primary"),
    ("allenai/OLMo-2-0425-1B", "leg4_pilot"),
    ("Qwen/Qwen2.5-7B", "comparison_arm"),
]

# Weights plus the config/tokenizer files. No .pth, no ONNX, no TF/Flax mirrors of
# the same tensors - those double the download for nothing.
ALLOW = ["*.safetensors", "*.json", "*.txt", "*.model", "*.py", "*.md"]
IGNORE = ["*.pth", "*.bin", "*.h5", "*.msgpack", "*.onnx", "*.gguf"]

OUT = "/speed-scratch/o_iseri/staged_weights.json"


def dir_bytes(path):
    total = 0
    for root, _dirs, files in os.walk(path):
        for f in files:
            fp = os.path.join(root, f)
            try:
                total += os.path.getsize(fp)
            except OSError:
                pass
    return total


def main():
    from huggingface_hub import snapshot_download
    from huggingface_hub import __version__ as hub_version

    print("huggingface_hub", hub_version, flush=True)
    print("HF_HOME =", os.environ.get("HF_HOME"), flush=True)

    record = {
        "written_by": "4thJ_stage_weights.py",
        "hf_home": os.environ.get("HF_HOME"),
        "huggingface_hub_version": hub_version,
        "repos": [],
    }

    failed = []
    for repo_id, role in REPOS:
        print("=" * 70, flush=True)
        print("STAGING", repo_id, "(" + role + ")", flush=True)
        t0 = time.time()
        entry = {"repo_id": repo_id, "role": role}
        try:
            path = snapshot_download(
                repo_id=repo_id,
                allow_patterns=ALLOW,
                ignore_patterns=IGNORE,
                max_workers=4,
            )
        except Exception as exc:  # noqa: BLE001 - the log is the deliverable
            print("FAILED", repo_id, type(exc).__name__, exc, flush=True)
            entry["status"] = "FAILED"
            entry["error"] = "%s: %s" % (type(exc).__name__, exc)
            record["repos"].append(entry)
            failed.append(repo_id)
            continue

        # The resolved commit hash is the point of this job. snapshot_download puts
        # the snapshot under .../snapshots/<commit_sha>/, so read it from the path
        # rather than from a second API call that could resolve a different revision.
        commit = os.path.basename(os.path.normpath(path))
        size = dir_bytes(path)
        entry.update(
            {
                "status": "OK",
                "revision": commit,
                "local_path": path,
                "bytes": size,
                "gib": round(size / (1024 ** 3), 3),
                "seconds": round(time.time() - t0, 1),
                "n_safetensors": len(
                    [f for f in os.listdir(path) if f.endswith(".safetensors")]
                ),
            }
        )
        print("  revision   ", commit, flush=True)
        print("  path       ", path, flush=True)
        print("  size       ", entry["gib"], "GiB", flush=True)
        print("  shards     ", entry["n_safetensors"], flush=True)
        print("  seconds    ", entry["seconds"], flush=True)
        record["repos"].append(entry)

    with open(OUT, "w") as fh:
        json.dump(record, fh, indent=2)
    print("=" * 70, flush=True)
    print("wrote", OUT, flush=True)

    if failed:
        print("STAGING INCOMPLETE:", ", ".join(failed), flush=True)
        return 1
    print("STAGING COMPLETE: 3 of 3", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
