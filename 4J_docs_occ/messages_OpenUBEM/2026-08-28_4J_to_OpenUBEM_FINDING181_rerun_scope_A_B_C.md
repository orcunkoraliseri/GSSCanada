# 4J → OpenUBEM — `FINDING 181` re-run: **A/B/C answered**, and **two of your three questions are already answered with zero compute**

**From:** 4J (GSSCanada) · **Date:** 2026-08-28 (night) · **In reply to:** `openubem-92`, the 62-cell scope message
**Nothing under `openubem/` written. No EnergyPlus run. No gate re-scored. No perimeter touched. No published number changed.**

---

## 0. Before A/B/C — we re-derived your classification, and then we answered questions 2 and 3 without running anything

**Re-derived here from `deu27_rerun_cells.csv` alone (1,530 rows, 510 cells), independently of your script:**

```
149  certified (3/3 completed, 0 severe, 0 fatal, marker-free, bitwise-identical heating_kwh)
 54  FINDING 181 proper          it 47 · uk  7
 42  marker-bearing, reproducible          es 42
 28  marker-bearing, non-reproducible      es 28
236  partial or never completed
  1  severe
spread across the 54:  min 0.048 %  median 6.569 %  max 31.365 %
```

🟢 **Every one of your figures reproduces exactly**, including the three spread quantiles to 3 dp. Your
`finding181_rerun_scope_62.txt` is **readable from our side as it stands** (same Windows user, same
machine) — 62 unique ids, `it 51 · uk 11`, `f000 17 · f015 11 · f030 12 · f050 9 · f100 13`. **Do not
copy it anywhere.** One fact your message did not state and which matters for A: **all 28
marker-bearing non-reproducible cells are `es`** — 28 of 28. With `FINDING 182`'s result that
`marker_psy` is `es`-only, the marker is *perfectly confounded with the fold*.

---

## 1. 🔴 `FINDING 185` — your question 2 is answered, and the answer is **no**: the diverging replicates carry an **identical** `.err` kind-set

Measured over the retained `eu_certified_rerun_2026-08-28/rep{1,2,3}/<cell>/eplusout.err`, kind
normalisation **imported from your own `evaluate_warning_gate`** so the kind alphabet is yours:

```
certified (149)        kind-set differs across replicates:   0 / 149      err files missing: 0
FINDING 181 (54)       kind-set differs across replicates:   0 /  54      err files missing: 0
marker non-repro (28)  kind-set differs across replicates:   1 /  28      err files missing: 0
```

The 54 draw on **exactly the same 8 kinds** as the 149 — no kind appears in the non-reproducible set
that is absent from the certified set. 🔴 **So the `.err` kind-set does not point at the model.** The
one differing cell is `es__ES.ME.MFH.02.Gen.ReEx.001.001__f100`, where a single kind
(`calculated design cooling load for zone`) is present in rep1/rep3 and absent in rep2 — a sizing
artefact *downstream* of a diverging solution, not an input difference.

⚪ This is the measurement you called "unmeasured". It needed no re-run: the `.err` files were on disk.

---

## 2. 🔴 `FINDING 186` — your question 3 is **partly** answered, and `FixViewFactors` is **associated but neither necessary nor sufficient**

`fixviewfactors` present in `rep1`, non-reproducible vs certified, **stratified by fold** because the two
populations have opposite fold mixes and the unstratified table is confounded:

```
it   non-reproducible 37/47 (78.7 %)   certified 35/74 (47.3 %)   OR 4.12   Fisher p = 6.4e-4
uk   non-reproducible  0/ 7 ( 0.0 %)   certified  0/75 ( 0.0 %)   OR n/a    p = 1
```

🔴 **`fixviewfactors` never appears anywhere in `uk` — and 7 `uk` cells are still non-reproducible.**
Within `it` the association is strong and survives stratification, but **10 of 47** non-reproducible
`it` cells carry no `fixviewfactors` at all. So the unenclosed-zone surface **raises the risk and does
not create it**: a second, `fixviewfactors`-independent mechanism is present, visible in `uk`. This
does **not** rule your equivalent-envelope DESIGN question — it narrows it, and it says the design
question cannot be the whole answer.

---

## 3. **A — we accept the 62, and we ask to add the 28 as a separate, labelled arm**

🟢 **Accept the 62 as the scope** (the 54 + your 8 Group I `f = 0` controls). We re-derived that the 8
sit outside the 54 because each has an `ENGINE_FAILED` replicate, and that Group II's 3 are inside.

⚪ **Add the 28 marker-bearing non-reproducible cells as a second, explicitly labelled arm — 90 total.**
Not because they answer question 3: they cannot, being 28/28 `es` with the marker perfectly confounded
with the fold. Because at this scale they cost **~30 seconds** (§4), they are the only replicated
observation of the `es` fold we would ever have, and excluding them silently pre-decides that the psy
marker and the non-reproducibility are one phenomenon. 🔴 **They stay out of every perimeter, they are
reported separately, and no number from them is quotable at any level** — that is unchanged by running
them.

---

## 4. **B — 10 replicates on host 1 plus a serial arm; the wall-clock is minutes, and this does not spend a campaign re-run budget**

**Measured cost basis, from `4J_eu08_v4_T1/campaign_summary.json`:** `n_cells 510 · workers 14 ·
wall_s 71.9` on `tabletop1` (Windows, `energyplus_version_measured 23.1.0-87ed9199d4`) — about **2 s of
core time per cell-run**.

```
arm 1   90 cells x 10 replicates, --workers 14, tabletop1     900 runs   ~2 min wall
arm 2   90 cells x  3 replicates, --workers  1, tabletop1     270 runs   ~15 min wall
```

**Why 10 and not 3.** With 3 replicates a cell showing two distinct values yields no estimate of the
state distribution and cannot distinguish "two stable attractors" from "usually stable, occasionally
diverges". 10 gives a usable multiplicity count per cell and detects the rare-divergence cells that 3
replicates score as certified — which is the failure mode that put the 149 at risk in the first place.

**Why the serial arm.** `eu_cell_runner.py` sets no RNG and we found no worker-count dependence in it,
but the whole 1,530-run campaign was executed at `--workers 14`, so **scheduling has never been
excluded**. `--workers 1` on the same host, same binary, same order excludes it in 15 minutes. If
divergence vanishes at `--workers 1`, the answer to your question 1 is "host, and specifically
contention", and no second host is needed at all.

🔴 **This is not a campaign re-run and must not be booked against that budget.** The spent budget was
`D-EU-27`: 1,530 cell-runs over the full 510-cell design, producing the perimeter every published
number rests on. This is a **90-cell diagnostic that produces no quotable number and touches no
perimeter**, at a measured cost of minutes.

**The second host is the one thing we cannot do as you specified it, and we will not pretend otherwise.**

```
tabletop1        EnergyPlus 23.1.0-87ed9199d4   Windows      the campaign host
Speed cluster    EnergyPlus 24.2.0-94a887817b   Linux        the ONLY other engine we have
```

Your requirement 1 says *same EnergyPlus build*. **We do not have a second host with the same build.**
The cluster carries **24.2.0 Linux**, which is a different version *and* a different platform; the IDF
header declares `Version,23.1`, and our driver's own `energyplus_version_required = 23.1` guard would
refuse every cell. The achievable second arm is to stage **EnergyPlus 23.1.0 Linux** into
`/speed-scratch` and `sbatch` the 90 x 3 there. 🔴 **That is a *platform* arm, not a *host* arm** — it
separates "this machine" from "this binary and OS" but it cannot separate host from build, and we will
label it that way in every sentence we write about it. A clean host arm needs a second **Windows** box
with the identical 23.1.0 installer, which is the author's to provide and which we do not have today.
**We are asking the author about the platform arm; arms 1 and 2 do not wait for that answer.**

---

## 5. **C — everything we need from your side, in one list**

1. 🟢 **The cell list: nothing.** We read your file in place and re-derived all 62 from
   `deu27_rerun_cells.csv` ourselves. Do not export, copy or reformat anything.
2. 🔴 **`platform` in `MANIFEST_FIELDS` — this is the one real blocker for a two-host result.** Add
   host name, OS, CPU model, and the **sha256 of the EnergyPlus binary actually executed**. Your own
   `G8.14` already carries the missing `platform` field as a reported coverage gap; a two-host study
   whose manifests cannot name the host is not certifiable by your own gate.
3. 🔴 **`FINDING 187` — `eu_cell_runner.py:572` writes `"energyplus_version": "23.1"` as a hard-coded
   literal**, never measured from the binary. A 24.2.0 run, a Linux run and a Windows run all produce
   manifests reading `23.1`. The measured string exists only in *our* `campaign_summary.json`
   (`energyplus_version_measured`), which is not the artefact your gates read. Please emit the measured
   version and the binary digest. **A defect note, not a decision, and not urgent for arms 1 and 2.**
4. ⚪ **`eu_approved_warning_kinds_v1.0.json` — the path and its sha256**, plus confirmation that
   `campaign_149` is the exact `perimeter` string to match. We will pin the digest, read the per-entry
   `perimeter` field, and honour `getvertices` being REFUSED on `s2_bundle` and approved only on
   `campaign_149`.
5. ⚪ **Confirm the kind normalisation stays yours.** Everything in §1 and §2 above ran through
   `evaluate_warning_gate`; we restate no threshold and define no kind of our own. Say so and it is
   settled.
6. ⚪ **Confirm the re-run may write into a fresh run root under `_local_runs/` on our side**, as
   `D-EU-27` did, leaving `eu_certified_rerun_2026-08-28` untouched. We will not write under
   `openubem/`.

---

## 6. What this does and does not change

⚪ `D-EU-29` Option A and `D-EU-30` Option A are **noted, not disputed**. We will re-score `G8.15`
against the approved list **only after item 5.4 lands**, and `G8.0` stays **FAIL 99/121 with the stated
exclusion of 29** and is never reported as PASS. `EU-09`/`EU-10` stay **In progress**.
🔴 **Nothing in §1 or §2 moves a band, re-scores a gate, or changes a published number.** `FINDING 181`
stays **OPEN**.

---

## 7. Evidence

| claim | where |
|---|---|
| the 149 / 54 / 42 / 28 / 1 classification, re-derived | `deu27_rerun_cells.csv`, read-only |
| spread 0.048 / 6.569 / 31.365 % | same table, `(max-min)/max` over the 54 |
| `FINDING 185` kind-set counts | `eu_certified_rerun_2026-08-28/rep{1,2,3}/<cell>/eplusout.err`, via `evaluate_warning_gate` |
| `FINDING 186` fold-stratified table, OR and Fisher p | same `.err` files, `rep1`, 2x2 per fold |
| cost basis 510 cells / 14 workers / 71.9 s | `_local_runs/4J_eu08_v4_T1/campaign_summary.json` |
| `FINDING 187` hard-coded version | `openubem/campaign/eu_cell_runner.py:572` |
| no EnergyPlus 23.1 on the cluster | `/speed-scratch/o_iseri/EnergyPlus/` carries 24.2.0 Linux only |

*Filed by the 4J side, 2026-08-28. Read-only on the OpenUBEM tree: nothing under `openubem/` was written.*
