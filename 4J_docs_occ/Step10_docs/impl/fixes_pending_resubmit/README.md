# `fixes_pending_resubmit/` — prepared, NOT applied

🔴 **Nothing in this directory has been applied to anything.** The deployed runner on Speed and the
local copy of `tools/4thJ_step10_nocore_campaign.py` are byte-unchanged. IT (`1315014`) is running
against that exact file and UK (`1315015`) is PENDING on it; applying any of this now would mean the
campaign built its IDFs two different ways, which is not a campaign.

Diagnosis and evidence: `../2026-09-10_C2-failure-root-cause-and-resubmit-package.md`.
Per-building classification: `../C2_failure_families.csv` (101 buildings, 0 unclassified).

| file | family | bldgs / cells | owner | state |
|---|---|---|---|---|
| `FIX_C_interzone_construction.patch` | C | 7 / 70 | **this repo** | written, compiles, **verified against the real refused IDFs**, not applied |
| `FIX_B_ring_hygiene.spec.md` | A + B + E | 75 / 750 | OpenUBEM | spec + acceptance test, handed over, no patch written |
| `FIX_D_fragment_routing.spec.md` | D (+ E) | 19 / 190 | geomeppy / OpenUBEM | spec + detector, handed over, no patch written |

## Order of operations for a re-submission

1. `C2` finishes (IT, then UK). Report it as it stands, cells split by family. Our 70 cells are
   reported as **ours**.
2. Author decides which remedies are in scope. `FIX_C` is the only one this repository may write.
3. Re-pre-registration: new frozen prereg, new md5. `FIX_C`, the proposed `R12` refusal, and the
   `EU_FLOOR`-on-interzone-plates physics choice are all **basis changes** and must be named in it.
4. Any upstream geometry fix arrives as a **new emission**, announced in full (sha + line endings +
   counts + which row builder) and consumed only after that announcement — never installed over the
   tree a job is reading.
5. Apply `FIX_C_interzone_construction.patch`, then see the acceptance tests fail and pass:
   - rebuild the 7 class-C buildings → `grep -c "reverse order"` on each `eplusout.err` = 0;
   - `R12` seen **refusing** a deliberately mis-assigned surface before it is trusted;
   - `4J_s10_verify_fix_c.py` re-run over the rebuilt IDFs → `OLD_bad > 0`, `NEW_bad == 0`.
6. Launch a **new campaign** over the full population. Re-running only the failed buildings and
   pooling the result with `T07` would put two instruments under one campaign name — the failed set
   is a diagnostic population, never a result population.

## Applying the patch, when the time comes

```bash
cd 4J_docs_occ
patch -p0 --dry-run < Step10_docs/impl/fixes_pending_resubmit/FIX_C_interzone_construction.patch
```

The patch is against `tools/4thJ_step10_nocore_campaign.py` at the `C2`-deployed revision (LF line
endings — check with `file`/`wc` before and after; `PIN 2` is line-ending dependent). Take a backup
first (`.bak_pre_fixc`) and verify it is non-empty before touching the original.
