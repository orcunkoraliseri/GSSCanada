# `tools/4thJ_step10_nocore_preflight.py` — seen failing, 2026-09-03

Task: §12 box 4 (I-4), run-book check — the preflight guard must be seen FAILING today on the
410 retained Step 10 manifests and on the engine as it is (core-era). No EnergyPlus, no network,
no cluster; read-only.

## Command

```
C:/Users/o_iseri/AppData/Local/Programs/Python/Python313/python.exe tools/4thJ_step10_nocore_preflight.py \
    --manifests Step10_docs/outputs_step10/realstock_campaign/manifests
```

## Result

`checked=410 failed=410` — every one of the 410 retained Step 10 manifests fails the guard,
exit code 1.

Failure reasons (all four fire on every manifest, since the 410 are Step 10 manifests, not
campaign `C2` ones):

* `scheme=None (want nocore_equal_area)` — the field does not exist on a Step 10 manifest.
* `status=None (want direct)` — same.
* `check.verdict is missing` — same.
* `engine sha256=316fe7a66ca62f7f55050a45d43a2cff0f8b5704af0881a099ad050d80bb150b != pinned TBD_by_owner`
  — **`V10.i` applied**: the digest of `openubem/geometry/european_residential.py` was
  **re-measured today**, not copied from the review document. `ENGINE_DIGEST_PIN` is set to the
  literal string `TBD_by_owner` by design — no no-core engine build exists (`D-EU-84`, `D-EU-87`
  open, carry-in "identified, not ordered"), so this arm of the guard fails by construction until
  the owner pins a real digest after the carry-in lands. **Never move `ENGINE_DIGEST_PIN` to make
  a run pass.**

## Reading

This is the correct state for 2026-09-03: no manifest on disk is eligible for the no-core
campaign (none carry the no-core scheme fields, because none were produced by a no-core engine),
and the guard says so on every one of them rather than passing vacuously. `SEEN NOT FAILING`
would have been the wrong result and would have meant the guard was broken; `SEEN FAILING` on
410/410 is the guard working as designed.

No manifest was retrofitted. No gate moved. No EnergyPlus was invoked.

---

## Re-verified after the `D-IMP-4` re-home — 2026-09-03

The guard was renamed `tools/4thJ_step12_preflight.py` → `tools/4thJ_step10_nocore_preflight.py`
when the no-core campaign became **Step 10 campaign `C2`** and `Step12_docs/` was retired. Logic
unchanged (`ENGINE_DIGEST_PIN` still the literal `TBD_by_owner`, still set only by the owner).
Re-run under the new name on the same 410 retained `C1` manifests:

`checked=410 failed=410`, exit code **1**, engine
`sha256=316fe7a66ca62f7f55050a45d43a2cff0f8b5704af0881a099ad050d80bb150b` — byte-identical to the
digest measured earlier today, so the engine has not moved and the guard is still **SEEN FAILING**,
not passing vacuously under a new filename. No manifest retrofitted, no gate moved, no EnergyPlus.
