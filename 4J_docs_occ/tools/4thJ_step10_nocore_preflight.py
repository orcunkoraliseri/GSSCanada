"""4thJ_step10_nocore_preflight.py -- read-only preflight guard for Step 10 campaign C2 (no-core).

Written 2026-09-03 for IMP/docs/2026-09-03_nocore-pipeline-review-improvements.md, box 4 (I-4). Re-homed 2026-09-03 under D-IMP-4: there is no Step 12; this guards
Step 10 campaign C2, gate series G10N.x, specified in Step10_docs/nocore/.

Asserts, per manifest, that it is eligible for campaign C2 (no-core real stock):
  1. manifest["scheme"] == "nocore_equal_area"
  2. manifest["status"] == "direct"
  3. a check verdict is present (manifest["check"]["verdict"] is not None)
  4. the sha256 of openubem/geometry/european_residential.py on disk equals a pinned
     no-core digest (D-IMP-2 / D-EU-84 / D-EU-87 dependency)

The digest pin is TBD_by_owner: no no-core engine build exists yet, so this guard is
DESIGNED TO FAIL BY CONSTRUCTION until the owner pins a real digest after the engine
carry-in lands. Never edit ENGINE_DIGEST_PIN to make a run pass; it is set by the owner.

No EnergyPlus is invoked, no network call is made, no cluster job is submitted. This
script only reads manifests already on disk and hashes one file already on disk.

Usage:
  C:/Users/o_iseri/AppData/Local/Programs/Python/Python313/python.exe 4thJ_step10_nocore_preflight.py \
      --manifests <dir of *.json> [--engine <path to european_residential.py>]
"""
import argparse
import hashlib
import json
import os
import sys

ENGINE_DIGEST_PIN = "TBD_by_owner"  # never move this to make a run pass; owner sets it after carry-in

DEFAULT_ENGINE_PATH = (
    r"C:\Users\o_iseri\Desktop\OpenUBEM\openubem\geometry\european_residential.py"
)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def check_manifest(manifest, engine_digest):
    failures = []
    scheme = manifest.get("scheme")
    if scheme != "nocore_equal_area":
        failures.append("scheme=%r (want nocore_equal_area)" % (scheme,))
    status = manifest.get("status")
    if status != "direct":
        failures.append("status=%r (want direct)" % (status,))
    check = manifest.get("check") or {}
    verdict = check.get("verdict")
    if verdict is None:
        failures.append("check.verdict is missing")
    if engine_digest != ENGINE_DIGEST_PIN:
        failures.append(
            "engine sha256=%s != pinned %s" % (engine_digest, ENGINE_DIGEST_PIN)
        )
    return failures


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifests", required=True, help="directory of *.json manifests")
    ap.add_argument("--engine", default=DEFAULT_ENGINE_PATH)
    args = ap.parse_args()

    if not os.path.isfile(args.engine):
        print("REFUSE: engine file not found at %s" % args.engine)
        sys.exit(2)
    engine_digest = sha256_of(args.engine)

    n_checked = 0
    n_failed = 0
    for name in sorted(os.listdir(args.manifests)):
        if not name.endswith(".json"):
            continue
        path = os.path.join(args.manifests, name)
        with open(path, encoding="utf-8") as f:
            manifest = json.load(f)
        n_checked += 1
        failures = check_manifest(manifest, engine_digest)
        if failures:
            n_failed += 1
            print("FAIL %s: %s" % (name, "; ".join(failures)))

    print("checked=%d failed=%d engine_sha256=%s pin=%s" % (
        n_checked, n_failed, engine_digest, ENGINE_DIGEST_PIN))
    sys.exit(1 if n_failed else 0)


if __name__ == "__main__":
    main()
