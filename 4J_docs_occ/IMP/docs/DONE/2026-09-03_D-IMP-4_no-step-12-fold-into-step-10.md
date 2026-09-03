# `D-IMP-4` — there is no Step 12; the no-core campaign is Step 10 campaign `C2`

**Date:** 2026-09-03 (same day as `D-IMP-1/2/3`, later session).
**Raised by:** the author, on reading the execution session's output.

## What the author said (verbatim)

> "i now realised the previous session added step 12 … why? no need new step, what i wanted to
> replace `Step10_docs` with nocore version, but it added new step, can you check"

> "but as i will use no core option for this project, we do not need step 10 with core results"

> "you recommend option a but i want to have clean pipeline, not extra step like 12, propose me
> something clean"

> "yes, do it, i want clean process, i am preparing the OpenUBEM results soon they will come in
> here, lets prepare this pipeline, thank you"

> "then archive older step 10 core version, no need to delete lets keep it"

## What had happened, and why

`D-IMP-2` (`IMP/docs/2026-09-03_nocore-pipeline-review-improvements.md` §4) offered three options.
Option **(b) — "amend Step 10 in place as campaign 2"** was **the author's own intent**, and it was
rejected in the review on the `Overview.md:683` registration rule (*two documents claiming one ID
on two bases is how a basis change hides as a fix*). The author's go-ahead — *"no more core plans,
nocore plans i want, lets go"* — was read as **(a) on all three**, which created `Step12_docs/`.
That reading took the recommended option where the author meant the rejected one. `D-IMP-4`
corrects the location and keeps the substance.

## The ruling

**No Step 12. The no-core campaign is Step 10's second campaign, `C2`. The core-era Step 10 is
archived, not deleted.**

| | ruled |
|---|---|
| Step 12 as a pipeline step | **abolished** — `Step12_docs/` deleted (backup `Step12_docs.bak_dimp4/`); the pipeline is **Steps 0–11** |
| the no-core campaign | **Step 10 campaign `C2`**, documents promoted to the top of `Step10_docs/` |
| the core-era campaign | **Step 10 campaign `C1`**, moved to `Step10_docs/archive_C1_core_era/` — archived, **not deleted**, not re-opened, not re-scored, not retracted |
| gate namespace | `G12.x` → **`G10N.x`**, `V12.x` → **`V10N.x`**; `G10.x` stays spent on `C1` |
| reporting | 🔴 **no `C1` result is reported**; `C2` is what gets reported once it runs |
| `D-IMP-2`'s substance | **kept in full** — separate gate namespace, own prereg, spec now, compute only after the OpenUBEM blockers clear |

## Why this is not the thing `Overview.md:683` forbids

The rule protects **gate IDs**, not step numbers: it forbids one ID scoring two bases. That is
satisfied here by `G10.x` (core-era, `C1`, closed) and `G10N.x` (no-core, `C2`, unscored), each
row of `G10N.x` naming the `G10.x` row it inherits from. A twelfth step was one way to buy that
separation; a distinct namespace inside Step 10 buys the same separation without an orphan step,
which is what the author asked for.

## What moved, and what deliberately did not

**Moved:** `Step12_docs/4thJ_12_nocoreRealStock.md` → `Step10_docs/4thJ_10_nocoreRealStock.md`;
`_val.md` likewise; `prereg_step12_DRAFT.md` → `Step10_docs/prereg_step10_nocore_DRAFT.md`;
`Step12_docs/impl/*` → `Step10_docs/impl/`; `tools/4thJ_step12_preflight.py` →
`tools/4thJ_step10_nocore_preflight.py`. `C1`'s two specification documents (and their `.bak`
siblings) → `Step10_docs/archive_C1_core_era/`.

🔴 **Did not move:** `Step10_docs/outputs_step10/`, `Step10_docs/impl/`'s pre-2026-09-03 notes,
`Step10_docs/docs/`, and the nine `tools/4thJ_step10_*.py` scripts. They are `C1`'s **executed
evidence**, addressed by path from ~30 recorded places including commands written inside a closed
record; relocating them would falsify those commands. `Step10_docs/README.md` is the redirect for
any path written before today.

🔴 **Did not change:** any threshold, any inheritance clause, any perturbation verdict, any scored
gate. `C1` stays **18 PASS / 2 FAIL / 1 INFO / 1 OPEN_INHERITED / 2 NOT_EVALUABLE**. No manifest
retrofitted, no number retracted, no EnergyPlus invoked, `prereg.md` md5
`e4243e07cdd80c9c846b91f40e3e8c45` never opened. Option (c) of `D-S10-1` and Option B of
`D-EU-31` stay refused.

## Check that closes this docket

The renamed preflight guard must still be **seen failing** — a rename must not turn a failing
guard into a vacuous pass. Re-run on the same 410 `C1` manifests:

```
checked=410 failed=410  exit 1
engine_sha256=316fe7a66ca62f7f55050a45d43a2cff0f8b5704af0881a099ad050d80bb150b  pin=TBD_by_owner
```

Digest byte-identical to this morning's measurement, so the engine has not moved and the guard is
still failing for the right four reasons. Record:
`Step10_docs/impl/2026-09-03_preflight-seen-failing.md`, second section.

## Still open, unchanged by this ruling

Campaign `C2` is **spec only**. It waits on the OpenUBEM engine carry-in of the no-core rule into
`european_residential.py`, `D-EU-84`, `D-EU-87`, `D-EU-88`, and on `D-EU-55` (no EnergyPlus without
the owner's own sentence). None of these is 4J's to fix. The author has said OpenUBEM results are
being prepared and will arrive here.
