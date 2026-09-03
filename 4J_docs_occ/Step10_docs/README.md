# `Step10_docs/` — map and redirect

**Written 2026-09-03 under `D-IMP-4`.** Docket:
`../IMP/docs/DONE/2026-09-03_D-IMP-4_no-step-12-fold-into-step-10.md`.

🔴 **The pipeline is Steps 0–11. There is no Step 12.** The no-core real-stock work filed earlier
the same day as `Step12_docs/` was re-homed here as **Step 10's second campaign**; `Step12_docs/`
no longer exists. **Its backup was archived on 2026-09-03 to `../previous/Step12_docs.bak_dimp4/`** (it sat at `../Step12_docs.bak_dimp4/` for part of that day; every earlier mention of that path means the archived copy).

## Step 10 has two campaigns

| | `C1` — core-era | `C2` — no-core |
|---|---|---|
| **Documents** | `archive_C1_core_era/4thJ_10_ubemRealStock.md` + `_val.md` | `4thJ_10_nocoreRealStock.md` + `_val.md` + `prereg_step10_nocore_DRAFT.md` |
| **Gate series** | `G10.x` (spent, closed) | `G10N.x` (pre-registered, nothing scored) |
| **State** | **CLOSED** — 410 cells, 18 PASS / 2 FAIL / 1 INFO / 1 OPEN_INHERITED / 2 NOT_EVALUABLE | **SPEC ONLY** — no cell, no EnergyPlus |
| **Reported?** | 🔴 **No.** Method and reproducibility record only | ✅ Yes, once it runs |
| **Engine** | core-era `european_residential.py` | no-core build — does not exist yet |

**`C2` is the live Step 10.** It waits on the OpenUBEM blockers (engine carry-in, `D-EU-84`,
`D-EU-87`, `D-EU-88`) and on `D-EU-55` (no EnergyPlus without the owner's own sentence).

🔴 **`C1` is archived, not retracted.** Everything it scored stays true of the basis it was scored
on; it is not re-opened, not re-scored, not deleted. Not reporting it changes nothing in practice —
`G10.7` was INFO permanently, `FINDING 196` made the six Arm D EUIs lower bounds, and no
stock-level Arm D EUI was ever quotable.

## 📌 Redirect — paths written before 2026-09-03

Only the two `C1` **specification documents** moved. Their executed evidence did **not**:
`outputs_step10/`, `impl/`, `docs/` and the nine `../tools/4thJ_step10_*.py` scripts are still
where the closed record's own commands address them, deliberately, because moving executed
evidence would falsify commands recorded inside a closed record.

| Path written before 2026-09-03 | Resolves to |
|---|---|
| `Step10_docs/4thJ_10_ubemRealStock.md` | `Step10_docs/archive_C1_core_era/4thJ_10_ubemRealStock.md` |
| `Step10_docs/4thJ_10_ubemRealStock_val.md` | `Step10_docs/archive_C1_core_era/4thJ_10_ubemRealStock_val.md` |
| `Step12_docs/4thJ_12_nocoreRealStock.md` | `Step10_docs/4thJ_10_nocoreRealStock.md` |
| `Step12_docs/4thJ_12_nocoreRealStock_val.md` | `Step10_docs/4thJ_10_nocoreRealStock_val.md` |
| `Step12_docs/prereg_step12_DRAFT.md` | `Step10_docs/prereg_step10_nocore_DRAFT.md` |
| `Step12_docs/impl/*` | `Step10_docs/impl/*` (same two 2026-09-03 files) |
| `tools/4thJ_step12_preflight.py` | `tools/4thJ_step10_nocore_preflight.py` |
| `G12.x` / `V12.x` | `G10N.x` / `V10N.x` |
| `Step12_docs.bak_dimp4/` (repo root) | `previous/Step12_docs.bak_dimp4/` |

🔴 **Relative paths *inside* the archived `C1` documents resolve from `Step10_docs/`, one level
up** — they were not rewritten, because a closed record is not edited in place.
