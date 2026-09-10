# 2026-09-08 (last+44) — the campaign `C2` runner exists, and three record corrections

#### Tool: `tools/4thJ_step10_nocore_campaign.py`. Spec: `../4thJ_10_nocoreRealStock.md` §§4–7. Prereg: `../prereg_step10_nocore_DRAFT.md`, md5 `1bc21094b0e09e3ac4332fa2e80abf75`.
#### Nothing simulated. No EnergyPlus invoked. No gate scored. No band moved. No pin moved. Nothing written under `OpenUBEM/`.

---

## 0. WHY THIS WAS DONE TODAY

The author asked whether Step 11 could start, on the reading that "Madrid and
London are complete" on `openubem-6e`'s **EU Recut Progress** board. The answer
was no — Step 11 items `11.3`–`11.7` all depend on Step 10 `C2` cells, and
`11.1`/`11.2` (the only Step-10-free items) were done 2026-08-27. The author
then ruled: **build the `C2` runner while we wait.** That is what this records.

🔴 **Step 11 did not start, no Step 11 item was touched, and Step 11 remains
PLANNED / nothing built.**

---

## 1. WHAT WAS BUILT

`tools/4thJ_step10_nocore_campaign.py` — the runner campaign `C2` did not have.
It reads the emitted layout payloads, keeps the buildings the author's ruled
basis admits, gives every drawn flat its own independent series, builds one IDF
per (building, case, `f`), runs EnergyPlus, and writes a manifest carrying all
fifteen fields of spec §5.

🔴 **It is not an edit of `tools/4thJ_step10_realstock_campaign.py`.** That file
is `C1` — 41 Lyon footprints, `prereg.md` `e4243e07…`, `G10.x`, closed and
archived. It was not opened for writing and is not re-scored.

🔴 **It scores nothing.** No `G10N.x` verdict is computed, written or implied by
this tool under any flag. `--scored` exists only so that the refusal against it
is reachable and can be seen failing.

### 1.1 Two things it imports rather than restates

| imported | from | why restating it would be a defect |
|---|---|---|
| the eligibility ruling (`classify`, both digest pins, `payload_paths`) | `4thJ_step10_nocore_preflight.py` | the author ruled the basis once; two implementations of one ruling is how a campaign quietly acquires two populations |
| the Case A / Case B pairing and the per-dwelling seed policy | `4thJ_step10_paired.py` → `4thJ_step10_assign.py` | `G10N.20` inherits `G10.20` verbatim; reproducing the pairing would make the simulated pair a different pair from the emitted one — the exact defect the gate exists to catch, committed by the tool the gate reads |

### 1.2 Three places `C2` is deliberately not `C1`

1. **Zones come FROM the payload, never re-derived.** `C1` re-probed the layout
   engine and had to argue at length that a successful probe must not promote a
   census-refused building. Here there is nothing to promote: the plate was cut
   by the pinned engine and the flats it drew are the flats we simulate.
2. **Per-zone areas are DECLARED, not assumed.** `C1` had to split footprint
   area equally across zones (`zone_areas_basis = assumed_equal`) and flagged
   that as exactly the case that turns `G10.13`'s area-weighted arm green for
   the wrong reason. The no-core payload draws every flat, so areas are computed
   by shoelace from the payload's own vertices. That weakness does not carry
   over.
3. **Each district uses its OWN national TABULA registry**, named by the
   payload's `archetype_id`. `C1` ran the Lyon census under FR TABULA and
   relabelled the folds; `C2`'s districts are each their own real stock.

### 1.3 `N_u`, and the one thing the runner refuses to compute

```
N_u := sum over floors of len(floor["zones"])        <- what the gates read
```

and never `units_per_floor × storeys`. `units_per_floor` is the MAXIMUM
per-storey count, not a constant (`FINDING 246` / `FINDING 266`).
`dwellings_total` and `k` are written to the manifest as **provenance**, and
`dwelling_deficit` is **reported, never gated** — the census cuts one `k` per
building, the engine re-derives `k` per storey, and the two legitimately
disagree.

🔴 `status` is one of the fifteen §5 manifest fields, and the runner writes it
from **our own** classification. The payload carries no `status` key — asserting
one on the payload was the 2026-09-03 defect the author's basis ruling replaced,
and it is not reintroduced here under a different name.

---

## 2. THE TEN REFUSALS, ALL SEEN FAILING, EACH WITH A PASSING CONTROL

Per `feedback_gates_must_be_seen_failing.md`. Every refusal below was **run and
observed to fire**; every control was **run and observed to pass**.

| # | refusal | seen failing on | control that passes |
|---|---|---|---|
| — | no mode given | `--district IT-BOL-GALVANI2` alone → `rc=2` | `--dry-run` proceeds |
| `R1` | prereg md5 ≠ frozen | scratch text → `16bc3707… != 1bc21094…` | the real frozen file → `1bc21094…` |
| `R2` | district not authorised | Madrid `--dry-run`, London `--shakedown` → `rc=1` | Bologna passes |
| `R3` | France is never a fold | Lyon `--dry-run` → `rc=1`, not waivable by any authorisation | n/a — no control exists, and that is the point |
| `R4` | either engine digest ≠ pin | **fires today, on the live tree**: `6a14f428… != 8e1dcda1…` | our pinned artefact `Step10_docs/impl/engine_pin_20260908/` passes both |
| `R5` | any payload FAILs the ruled basis | one scratch payload given `…_SOMETHING_NEW` → refused, whole population | same set minus that file → `eligible=1 fail=0` |
| `R6` | EnergyPlus ≠ 23.1, MEASURED | fake binary reporting `22.2.0` → refused | fake binary reporting `23.1.0` → `measured version = 23.1.0` |
| `R7` | unpaired / non-unique / non-deterministic cells | a Case-B-only cell → `cases present are ['B']` | the real 10,360-cell list passes |
| `R8` | a scored run was requested | Bologna `--shakedown --scored` → refused, quoting the author's sentence | `--shakedown` alone proceeds |
| `R9` | pinned EPW missing | `WEATHER_DIR` pointed at an empty directory → refused | the real directory passes |
| `R10` | payload set digest ≠ expected | `--expect-payload-digest deadbeef` → refused | the true digest → proceeds |

🔴 **`R2` is `D-EU-55` in code.** The author's sentence is **quoted verbatim** in
the `AUTHORISED` table, not summarised, and Bologna is its only entry. The
refusal for any other district names what would be needed: *a SECOND sentence
from the author*, and says that editing the table without one is the same act as
moving a pinned digest.

🔴 **`R3` sits ahead of `R2` on purpose.** Refusing France is a rule, not a cost,
and no authorisation can reach it.

### 2.1 `R10` is new, and it is the one this week's situation demanded

The payload set's digest is the sha256 over `sha256 relpath` for every payload,
sorted. A run can therefore be pinned to the emission it was authorised against.
**A campaign that spans two emissions is two campaigns** — and with a
re-emission announced but not landed, that is not a hypothetical.

Measured today, Bologna: `64d6768f8bdfa88d26d334aa8aa1ceae10408e6f63fabccd07a0d66ff8842d21`.

---

## 3. THE POPULATION REPRODUCES, FROM A THIRD INDEPENDENT PATH

Bologna dry run, against our pinned engine artefact:

```
PREFLIGHT OK  district=IT-BOL-GALVANI2 fold=it mode=shakedown scores=False
  population: 1211 payloads -> 1036 eligible / 175 Arm F excluded / 0 FAIL
  REPORTED NOT GATED: 0 best-effort
  REPORTED NOT GATED: partition_audit passed=false on 980, worst 1.651e-04 (FINDING 258)
  cells: 1036 buildings x 2 cases x 5 f = 10360
  payload_set_sha256=64d6768f...
  SCORES NOTHING: no G10N.x verdict is computed by this tool.
```

1,036 / 175 / 0 and 980 / 1.651e-04 match the pre-registered figures exactly.
That is now **three** independent paths to the same population (the spec's census
arithmetic, the preflight guard, and this runner's own reader).

⚪ **10,360 cells is an enumeration, not a plan to run 10,360 cells.** The
shakedown is Bologna only, scores nothing, and its size is the author's to set.

---

## 4. 🔴 THREE CORRECTIONS TO OUR OWN RECORD, MEASURED TODAY

`openubem-20` was asked for a status read and answered with measured facts. Two
of its five answers change what we had written; one of its answers is itself
wrong and is corrected here.

### 4.1 The engine is `6a14f428…`, it is COMMITTED, and `fd1214a6…` was stale

Our record said `european_residential.py` was **uncommitted and mid-edit** at
`fd1214a6…`. Measured here today:

```
european_residential.py   6a14f428a6d8c267...   149,238 bytes   != pin 8e1dcda1...
european_nocore.py        21d723d5479076d0...    91,468 bytes   == pin 21d723d5...  EXACT
```

`openubem-20` reports the last commit touching it is `fda7f067` ("95% recut
dwelling schemes, delta merge harvest, Wall-B second pass"), **already landed**,
and that no new commit is pending from their side.

🔴 **So the engine has changed AND been committed. `R4` fires on the live tree
today and that is correct.** The pin was **NOT** moved. A new pin is the
**author's**, and it is now a live question rather than a deferred one.

⚪ Their LF-normalised `git show` hashes (`1bf3ddc…` / `6de4c66d…`) again do not
reproduce our pins — our two pins are the CRLF working-tree form. That is the
third independent confirmation of the standing rule: **record the commit AND the
line-ending convention beside every future digest.**

### 4.2 The two counts are two PIPELINES, not two denominators of one thing

This is the answer to the author's question, and it is stronger than the one we
gave from our own record alone.

| | what it counts | Madrid | London | Bologna | Lyon |
|---|---|---|---|---|---|
| **EU Recut Progress board** | buildings with a current-hash EUI in the **T06a EnergyPlus recut wave** | 1,186 / 1,194 | 1,242 / 1,242 | 1,158 / 1,220 | 528 / 530 |
| **`layouts/` payloads we consume** | the **`D-EU-110` side-car emission** (2026-09-08 morning) | 1,175 | 451 | 1,211 | 297 |

🔴 **The board will never signal the announcement we are waiting for.**
`openubem-20` states plainly that it monitors only the T06a wave, that
harvest/T06b has not started, and that the merged re-emission + side-car install
+ announcement is a **separate track (`D-EU-109`)** it is not running and has no
visibility into. **Do not infer an ETA from that board**, and do not read
"London 100 % drained" as "London's layouts are complete".

### 4.3 London's 451 is CONFIRMED still current — the 255 have not landed

Their `STATE_european_locations_v5.md` (`D-EU-110` note ii) gives the mechanism
we had recorded: the emitter's `row_map` excludes 255 buildings that carry
`platform` / `energyplus_version` but no `run_seconds` — the `D-EU-108`
coverage-recovery batch (187 age-inherited + 68 straddle), inside the merged
`D-EU-109` re-emission and its 1,534-case Speed campaign, **which has not run**.

🔴 It sits in a **different** Speed campaign from the board's four jobs, so
**London's 451 will not move when T06a drains.** Our "dated snapshot" framing
holds and the reason for it is now confirmed from their side.

### 4.4 🔴 WHERE `openubem-20` IS WRONG, measured here

They report that `partition_audit` is "always null (0/451, 0/1,211 populated)"
and that "Madrid has the key on only 130/1,175 files, none populated."

Measured directly, on all 2,837 payloads:

```
Madrid    files=1175  has_key=1175  passed=1100  area_error_fraction=1100  topology_subfields=0
London    files= 451  has_key= 451  passed= 439  area_error_fraction= 439  topology_subfields=0
Bologna   files=1211  has_key=1211  passed=1036  area_error_fraction=1036  topology_subfields=0
```

* The key is present on **100 % of all three districts, Madrid included** — not
  130 of 1,175.
* `passed` and `area_error_fraction` **are** populated, on exactly the eligible
  buildings, one for one (1,100 / 439 / 1,036). Those are the numbers `FINDING
  258` was measured from in the first place, so "always null" cannot be right.
* 🟢 **Their load-bearing claim is nonetheless CONFIRMED**: the four topology
  sub-fields (`failures`, `gap_area_m2`, `overlap_area_m2`, `outside_area_m2`)
  are present on **0 of 2,837**. The installed side-cars predate the emitter
  code at HEAD (`scripts/emit_eu11_layout_sidecars.py:541-550`).

🔴 **So `FINDING 258` stays unresolvable on this payload, and which of
`AREA_GAP` / `AREA_OVERLAP` / `OUTSIDE_FOOTPRINT` fired is still unknowable.**
The decision is unchanged and still right: `partition_audit` is **REPORTED,
NEVER GATED**. Gating it would discard 1,773 of 2,575 sound buildings.

⚪ **A peer's measurement is evidence, not an authority.** Their fifth answer was
checked before it was carried, and the part of it that was wrong did not enter
our record as fact.

---

## 5. WHAT IS OWED, AND TO WHOM

🔴 **The author, and only the author:**

1. **A new engine pin.** `european_residential.py` is now `6a14f428…`,
   committed at `fda7f067`. Our pin `8e1dcda1…` is the pre-recut engine. Record
   the commit **and** the line-ending convention beside whatever is pinned.
2. **A second `D-EU-55` sentence**, if Madrid or London is ever to run. `R2`
   refuses them until then, by name.
3. **Whether the shakedown runs on the CURRENT payload or waits for the
   `D-EU-109` re-emission.** The runner is ready either way; `R10` is what makes
   the choice explicit and auditable.

⚪ **Not owed to anyone:** nothing on this page needs OpenUBEM. `R4` firing is
their tree being ahead of our pin, which is the expected state.

---

## 6. THE NEVER-LIST, UNCHANGED

* Never move `ENGINE_DIGEST_PIN` or `NOCORE_DIGEST_PIN` to make a run pass, and
  never rewrite a guard's field names so a population passes — the same act.
* Never file a `C2` result under a `G10.x` ID; never re-open or re-score `C1`.
* Never promote Arm F to Arm D, and never pool the two.
* Never quote a best-effort building's EUI as a clean cut.
* Never run Lyon as a fold, a diary, or a Step 11 campaign.
* Never re-create a Step 12. The pipeline ends at Step 11.

---

## 7. ADDENDUM, same day — the peer confirmed our correction, and named a defect we already had

`openubem-20` re-ran its count recursively and **withdrew** the figure of §4.4:
Madrid `has_key=1175`, `passed`/`area_error_fraction` `=1100` — our numbers
exactly.

🔴 **Their bug was OUR bug, verbatim.** Their check globbed only
`layouts/relation/` and missed `layouts/way/`. That is the *same* defect we found
in our own preflight guard earlier on 2026-09-08 — it walked one directory level,
saw Madrid and London as **zero files**, and reported exit 0. Two independent
tools, the same day, on the same nested tree, made the same mistake in opposite
directions: ours under-counted to a silent PASS, theirs under-counted to a false
"always null". ⚪ **The nesting is the hazard, not either tool.** Anything that
reads these payloads walks recursively or it is wrong — and an empty or
suspiciously small scan must REFUSE, never pass. The runner uses the guard's own
`payload_paths` (`os.walk`) for exactly this reason.

🟢 **Independently confirmed by both sides now:** the four topology sub-fields are
on **0 of 2,837**. That is the claim to keep relying on, and `FINDING 258` stays
unresolvable on this payload.

### 7.1 🔴 LONDON'S 451 HAS AN ANNOUNCED SUCCESSOR — NOT SCHEDULED

Their author's direction: once the current wave is harvested, **London's side-car
export is to be re-run to cover the full 706**, not the 451 subset it is frozen
at. A `D-EU-110`-style re-emission, **not yet scheduled**, and not run by the
monitoring session.

⚪ **This is the fourth foreseen re-pre-registration, and nothing needs redoing to
absorb it.** `R10` already pins a run to a payload-set digest, so a London run
cannot silently span the 451 emission and its 706 successor. 🔴 **Do not build
anything that assumes 451 is final for London** — keep it pre-registered as a
DATED SNAPSHOT and let the digest carry the date.

### 7.2 A framing correction from their author, accepted

Not "our model" vs "their simulation" as two systems: **OpenUBEM built these
European location models for GSSCanada in the first place — one shared build**,
and 4J is GSSCanada's team working from the same models. ⚪ Worth carrying into
the paper's provenance sentence, which should not describe 4J as an independent
downstream consumer of someone else's geometry. **No number and no gate changes.**

---

## 8. ADDENDUM, same day — `PIN 2` TAKEN ON THE AUTHOR'S CONFIRMATION, AND THE SIDE-CAR FILTER FINDING

Three things happened after §7, all on the author's reply to the chat summary.

### 8.1 🔴 THE ENGINE PIN MOVED — `PIN 1` → `PIN 2`, AUTHORISED, AND IT CHANGED NOTHING

The author's words: **"lets go. i give confirmation."** — in reply to *"Waiting on you: a new software lock for the changed file."*
That is the only kind of authority that may move a pin.

Measured on the live tree at the moment of pinning:

| file | sha256 (CRLF, as checked out) | bytes | commit | tree |
|---|---|---|---|---|
| `openubem/geometry/european_residential.py` | `6a14f428a6d8c26745af3e1483080bf31e3026ebb94702f90ac7eadc4ad2afd3` | 149,238 | `fda7f067` *"feat(eu): implement 95% recut dwelling schemes, delta merge harvest, and Wall-B second pass validation"* (2026-09-08 14:34 −0400) | clean |
| `openubem/geometry/european_nocore.py` | `21d723d5479076d0a57416ff92fd67a98fca8a33ff19343132415c144ff6b8ae` | 91,468 | `4431f2fe` (2026-09-07) | clean |

🔴 **The cutter did NOT move.** `european_nocore.py` is byte-identical across `PIN 1` and `PIN 2`; only the residential engine advanced.

🔴 **LINE-ENDING CONVENTION RECORDED WITH THE VALUE, as the standing rule now requires: CRLF, the bytes as checked out on this machine.** `git show fda7f067:openubem/geometry/european_residential.py | sha256sum` yields the LF blob and does **not** reproduce `6a14f428…`. A digest without its convention is not a pin.

`PIN 1` is **superseded, not deleted** — its value, its commit, and the path to its bytes stay in the source beside `PIN 2`, in a comment that also states *why* the move was allowed.

**Bytes materialised as our own artefact**, so the pinned state is reproducible from our repo independently of the peer's tree — the same practice as `PIN 1`:

```
Step10_docs/impl/engine_pin_20260908b/european_residential.py   6a14f428…  149,238 B
Step10_docs/impl/engine_pin_20260908b/european_nocore.py        21d723d5…   91,468 B
```

Both re-hash to the pinned values from the copy. `engine_pin_20260908/` (the `PIN 1` bytes) was **not** touched.

**SEEN HOLDING AND SEEN FAILING**, both required:

| # | what was pointed at | expected | observed |
|---|---|---|---|
| A | live tree (`PIN 2` bytes) | PASS | `rc=0`, `engine_sha256=6a14f428… pin=6a14f428…` |
| B | `engine_pin_20260908/` (`PIN 1` bytes) | REFUSE | `rc=1`, `REFUSE: engine sha256=8e1dcda1… != pinned 6a14f428…` |

🟢 **THE PROOF THAT THIS WAS NOT A PIN MOVED TO MAKE A RUN PASS: the population is bit-for-bit the same on both sides of the move.**

```
before (PIN 1, engine_pin_20260908/):  checked=1211 eligible=1036 excluded_armF=175 failed=0
after  (PIN 2, live tree):             checked=1211 eligible=1036 excluded_armF=175 failed=0
audit passed=false 980 of 1036, worst area_error_fraction=1.651e-04   — identical
payload_set_sha256 64d6768f8bdfa88d26d334aa8aa1ceae10408e6f63fabccd07a0d66ff8842d21 — identical
C2 dry run: 1036 x 2 cases x 5 f = 10360 cells — identical
```

Nothing was failing that this made pass; no number moved; no `G10N.x` was scored before or after. The move is attributable to the engine legitimately advancing and landing as a commit, and to nothing else.

⚪ **`R4` was doing its job the whole time.** Before the pin it refused on the live tree — correctly, because the tree no longer matched what we had pinned. The refusal was the guard working, not a defect, and the fix was an author decision rather than a code change.

🔴 **Still true, and the reason `PIN 2` may not be the last one:** the announced `D-EU-111`/`D-EU-112` re-emission may land further commits on either file. If it does, `R4` will refuse again, and that will again be the author's call — never ours.

### 8.2 🔴 A CORRECTION WE OWED THE AUTHOR — "layout division comes before simulations" IS RIGHT, AND OUR EXPLANATION WAS TOO STRONG

§7 told the author that the peer's progress board and our `layouts/` payloads are two pipelines, and therefore *"London 100 % drained" ≠ "London's layouts are complete"*. The author pushed back: **"this is nonsense, layout division comes before simulations, please solve."**

Read against the peer's source, **the author is right about the mechanism and our framing was misleading.** `scripts/emit_eu11_layout_sidecars.py`:

```python
    if district == "GB-LDN-STDUNSTANS":
        rows, _ = _gb_rows(gdf, records)            # line 199
    ...
    # Filter rows to only those that were simulated in EU-11
    row_map = {str(r["building_id"]): r for r in rows
               if str(r["building_id"]) in simulated_ids}
```

So London's **451 of 706** is **two filters stacked, and neither is a law of physics**:

1. `_gb_rows` alone, without `_gb_terrace_recovery_rows` — the 255 coverage-recovery batch never enters the row set at all;
2. the `simulated_ids` intersection — the layout export is tied to the EnergyPlus population **by a line in the export script**, not because a dwelling partition consumes a simulation result.

The partition itself is pure geometry: footprint, storeys, dwelling count, cutter. **Nothing we can see in it needs an E+ output.**

🟢 **What survives of our original claim:** the board and our payloads are still produced by different scripts, and the board still cannot signal the hand-off we wait for, because the announcement track is one the peer does not run on that board. So *"London 100 % drained"* still does not mean *"London's layouts are complete"*.

🔴 **What does not survive:** the implication that the layouts *could not* exist for 706 until the wave runs. They could. It is a filter, and a filter can be widened today.

⚪ **The general shape, worth keeping:** *the author's physical intuition about the pipeline beat our reading of the project record.* We had "451 by design, `_gb_rows` skips the batch" written down and treated it as the whole cause; the second, larger filter was one line further down and we had never read it. **A recorded reason is a hypothesis until the code is read.**

### 8.3 🟢 THE AUTHOR'S GO-AHEAD FOR THE LONDON 706 WAS RELAYED TO THE PEER

Author: **"if possible do it now, say to openUbem i give okay, good to go."** Sent to `openubem-20`, saying explicitly that (a) our side is no longer the reason to wait until after harvest, (b) their own scheduling and their own author still bind, and (c) here is the filter reading above — with a direct question: **is `simulated_ids` load-bearing for a field we cannot see** (an outcome token, the `read_district` reroute-parity disclosure, anything), because that is precisely what we would otherwise get wrong.

The announcement requirements were repeated unchanged: **commit sha + line-ending convention + per-district file counts as written to disk.** `R10` (payload-set digest) already makes the 451 payload and a 706 payload two populations, so a campaign cannot silently span them, and we re-measure rather than carry their counts.

🔴 **A peer message is never the author's approval — and the reverse also holds: our author's go-ahead is not their author's.** We removed a reason to wait; we did not schedule their work.

### 8.4 WHAT IS OWED AFTER THIS ADDENDUM

| # | item | owner | state |
|---|---|---|---|
| 1 | a new engine pin | AUTHOR | 🟢 **DISCHARGED** — `PIN 2`, 2026-09-08, on the author's confirmation |
| 2 | a second `D-EU-55` sentence, if Madrid or London is ever to run | AUTHOR | 🔴 **STILL OPEN** — Bologna-only stands; `R2` refuses the other three by name |
| 3 | Bologna shakedown on the current payload, or wait for the re-emission | AUTHOR | 🔴 **STILL OPEN** — and now sharper: a 706-wide London re-export was just authorised from our side, so waiting has a nearer horizon |

### 8.5 🟢 THE PEER CONFIRMED THE READING AND IS RUNNING THE 706 EXPORT NOW — WE CONSUME NOTHING UNTIL THE ANNOUNCEMENT

`openubem-20`, same day, in reply to §8.3: **"your read was right, and we're running it now — full
706-building population, not waiting on the pending Speed simulate batch (299 rows, unsubmitted)."**
In progress on their side; they will follow up with commit sha, line-ending convention, and
per-district JSON counts on disk. They warn our 451 is "about to become stale" and that any layout
artifact pulled before the follow-up is provisional.

🟢 **§8.2 IS CONFIRMED BY THE OWNER OF THE CODE.** The `simulated_ids` intersection was a filter, not
a dependency, and the export could be widened without the wave — which is exactly what the author
said and what we had wrongly argued against.

🔴 **THREE THINGS THAT DO NOT CHANGE BECAUSE OF THIS MESSAGE.**

1. **We consume nothing before the announcement.** The standing sequence holds: per-district counts
   arriving before the last step are not an announcement. `R10`'s payload-set digest is computed
   over the file set a run is about to read, so a campaign spanning two emissions refuses rather
   than mixing them — a provisional artifact cannot silently enter a run.
2. **We re-measure rather than carry their counts.** A peer's measurement is evidence, never an
   authority — the same rule that caught their `partition_audit` claim in §7.
3. **Our 451 is not invalidated, it is SUPERSEDED BY A DELIBERATE ACT.** It was pre-registered as a
   DATED SNAPSHOT precisely because this was foreseen. Replacing it is a **re-pre-registration** the
   author signs, append-only, with its own md5 superseding the last — not a silent swap. ⚪ The
   failure mode worth naming: a payload that changes *without* an announcement. That is what `R10`
   exists to catch, and it is unaffected by their good intentions here.

⚪ **ONE NUMBER DOES NOT RECONCILE, AND IT WAS PUT TO THEM.** They say the pending Speed batch is
**299 rows**. Our record has London's uncovered remainder at **255** (187 age-inherited + 68
straddle, `D-EU-108`) inside the 1,534-case `D-EU-109` array, and **451 + 255 = 706 exactly**. Both
can be true if the 299 is a different set — a re-simulate list, or a union with rows already covered
— but if the 706 export contains buildings whose rows come from a builder we have not seen, that
changes **which eligibility tokens we should expect**, not merely the count. Asked as a fourth
announcement requirement: **which builder produced the added rows.** Also still outstanding from
§8.3: **is `simulated_ids` load-bearing for any field, or was dropping it purely a widening?**

🔴 **Nothing was pulled, nothing was measured against the new export, no population was re-derived,
and the prereg was NOT touched.** The next act on our side is the author's, not ours.

### 8.6 🔴 THE LONDON 706 LANDED AND WE MEASURED IT — IT IS NOT AT THE CANONICAL PATH, IT CARRIES 12 FAILS INCLUDING 6 REGRESSIONS, AND IT SETTLES `FINDING 258`

`openubem-20` announced completion the same day with commit `48690c71299f3ebf91958051586dfe2ab8eeba4e`
(⚪ **code and outputs are UNCOMMITTED working-tree changes on top of that sha — the payload is not
reproducible from a commit**, a declared limitation), `core.autocrlf=true` / CRLF JSON, 706 files,
and the real cause of the 255: the London branch called only `_gb_rows` and skipped the
terrace-recovery / neighbour-imputation pass `_gb_impute_rows` that `run_eu_s2_district_campaign.py
::prepare` also runs. ⚪ **So the `simulated_ids` filter of §8.2 was real but was NOT the whole
cause** — our reading was closer than the record but still not the mechanism. **Measured, not
carried.**

#### (a) 🔴 IT IS AT A DIFFERENT PATH FROM THE OTHER THREE DISTRICTS

```
706  2026-09-08 19:39  openubem/outputs/eu_evidence/EU-11/GB-LDN-STDUNSTANS_final_2026-09-07/layouts
451  2026-09-08 06:51  openubem/outputs/3D/eu_GB-LDN-STDUNSTANS_data/layouts          <- CANONICAL
451  2026-09-08 06:51  docs/docs_ACTIVE/europeanLocations/outputs_3D/eu_GB-...  /layouts
```
Madrid 1,175 / Bologna 1,211 / Lyon 297 all sit at the **canonical** path, which for London still
holds the **old 451**. 🔴 **A campaign that reads "the district's layouts directory" therefore takes
the NEW Bologna and the OLD London, silently.** Put to them: install it at the canonical path, or
declare the evidence path authoritative for London and not the others. **We do not guess.**
⚪ The directory is named `_final_2026-09-07` and was written 2026-09-08.

#### (b) 🔴 TWELVE FAILS WHERE THERE WERE ZERO — AND SIX ARE LOST ELIGIBLE BUILDINGS

Our preflight on the 706, under `PIN 2`: **685 eligible / 9 Arm F excluded / 12 FAILED.** The old
451 failed **none**. All 12 carry `DWELLING_LAYOUT_EMITTED_INTERZONE_MISMATCH_REROUTED` — the token
the author's ruled basis FAILS, and the one that makes Lyon unusable. Transitions **inside our
frozen 451**:

| count | before | after |
|---|---|---|
| 433 | `IMPUTED_COUNT` | `IMPUTED_COUNT` (unchanged) |
| 7 | `FALLBACK_PENDING_LAYOUT` | unchanged (Arm F) |
| **6** | **`IMPUTED_COUNT`** | **`INTERZONE_MISMATCH_REROUTED`** — 🔴 **eligible buildings LOST** |
| 5 | `FALLBACK_PENDING_LAYOUT` | `INTERZONE_MISMATCH_REROUTED` |
| +1 | — | brand-new building, also rerouted |

🔴 **This is a regression inside the recut, not a widening.** Examples `way/298850491`,
`way/393505346`. Reported to them before they call it final. **Whether the 706 replaces the 451 is
the author's ruling, not ours** — and it is no longer a free swap, because it costs six buildings.

#### (c) ⚪ NOT ADDITIVE — ALL 451 FILES CHANGED, AND FIVE LAYOUTS GENUINELY MOVED

Every one of the 451 has different bytes. For most, the only differing top-level keys are
`partition_audit` and `best_effort_failed_checks` — the promised additions. But **5 buildings'
layouts really changed**: the 451's zone total moved **1,728 → 1,813** and the `dwelling_count` sum
moved with it. 🔴 **So `uk`'s contribution to the ruled `C2` population of 26,764 zones is no longer
1,728.** Totals for the record: **706 buildings / 2,515 zones; eligible 685 / 2,316 zones.**
🔴 **This is a re-pre-registration the author signs, never an append and never a silent swap.**

#### (d) 🟢 `FINDING 258` IS DIAGNOSED — IT IS A TOPOLOGY GAP, EXACTLY AS WE CORRECTED

The new payload carries `failures`, `gap_area_m2`, `overlap_area_m2`, `outside_area_m2` on **697 of
706** (the 451 carried only `passed` + `area_error_fraction`, which is why the question was
unanswerable). **53** buildings fail the audit:

```
32  (AREA_GAP, AREA_OVERLAP, OUTSIDE_FOOTPRINT)
18  (AREA_GAP, OUTSIDE_FOOTPRINT)
 2  (AREA_GAP,)
 1  (OUTSIDE_FOOTPRINT,)

gap      nonzero 52 of 53   max 1.9184e-02 m²   median(nonzero) 5.002e-03 m²
overlap  nonzero 32 of 53   max 7.155e-03 m²    median(nonzero) 2.490e-03 m²
outside  nonzero 51 of 53   max 1.7534e-02 m²   median(nonzero) 4.014e-03 m²
```

🟢 **Against a topology tolerance of `footprint_area × 1e-9` these are four to five orders of
magnitude over, while `area_error_fraction` clears the `AREA_CONSERVATION` bar of 0.01 by ~100×.
That is the correction we made to our OWN record on 2026-09-08, now confirmed by data rather than by
argument: `FINDING 258` is a TOPOLOGY GAP and `area_error_fraction` was never the quantity that
failed.** 🔴 **The decision is unchanged: `partition_audit` is REPORTED, NEVER GATED.** ⚪ **The
FROZEN prereg still says "rounding residue"; the next re-pre-registration must carry the correction,
and it can now cite measured gap/overlap/outside areas instead of an inference.**

🔴 **NOTHING HAS BEEN CONSUMED.** No population was re-derived from the 706, no prereg was touched,
no `C2` run was started against it. Two things must land first, **both the author's**: the path
question, and whether a payload that costs six eligible buildings replaces the one we froze.

#### (e) 🟢 THE PEER CLOSED THE LOOP AND ADOPTED THE NESTING CONVENTION

`openubem-20`, same day: *"recorded your convention suggestion in our plan doc (layouts/ is live
payload only, superseded emissions live as siblings, never children). Matches all three of your
recursive counts. Nothing further needed from us on London or FINDING 258."*

🟢 So both defects are closed on their side and the rule that caused the 1,157 is now written down
where it will be enforced next time. ⚪ **This changes nothing on ours.** A peer message is never the
author's approval: the 706 is measured and installed, and whether it **replaces** the frozen 451 at
the cost of six eligible buildings is still the author's re-pre-registration, unsigned. 🔴 **We
re-measure after any further peer change; a count is never carried.**

---

## 9 🔴 THE `C2` RUNNER HAD NEVER BUILT AN IDF — THREE HARNESS DEFECTS FOUND BY A FOUR-CELL SMOKE, AND `RE-PRE-REGISTRATION 2`

Author's sentence, 2026-09-08: *"continue as you recommend lets go use bigger datasets"*. Read as
**two** rulings — adopt the London 706, and run the authorised district at full size — and
explicitly **not** as a third: it names no district and does not mention EnergyPlus, so `D-EU-55`
is **not** widened and `R2` was observed still refusing Madrid and London after it was given.

### 9.1 🔴 Three defects, all of them in OUR harness, none in the physics

The `C2` runner was built, reviewed and shipped in the previous session with ten refusals seen
firing — and **it had never once produced an IDF**, because nothing had ever run a real cell.
The first dry-run against real Bologna payloads failed immediately.

| # | symptom | cause | fix |
|---|---|---|---|
| 1 | `KeyError: 'shadow_method'` on every cell | upstream's `IDF_HEADER_TEMPLATE` carries a `ShadowCalculation` block; our formatter supplied 5 of 8 fields | the three constants are now **imported** from `scripts/run_eu_s2_campaign.py`, never typed here |
| 2 | `HVACTemplate:* objects found ... not supported directly` — fatal in 0.06 s | the heating controls emit `HVACTemplate:Zone:IdealLoadsAirSystem`; the binary refuses to read it unexpanded | invoke with **`-x`** (ExpandObjects), upstream's own flag |
| 3 | **3 of 4 cells** died with `remove: ... used by another process: "readvars.audit"` | `-r` runs ReadVarsESO, which writes `readvars.audit` into the **process working directory**, not into `-d`; parallel workers shared one cwd | **`cwd=run_dir`** with **`-d .`**, upstream's own invocation |

🔴 **Defect 3 is the dangerous one.** It does not look like a harness bug: it looks like scattered
physics failures, it varies with worker count, and it would have salted a 10,360-cell campaign with
false `ENERGYPLUS_FAILED` cells that no downstream gate could distinguish from real ones. ⚪ **All
three were found by running four cells before launching ten thousand — the whole argument for a
smoke run, in one afternoon.** ⚪ **None of them is a physics change:** every value that entered the
IDF came from upstream's own constants, imported, so this campaign holds no second opinion about
shading, expansion or output extraction.

### 9.2 🟢 The four-cell and sixteen-cell smokes, and what the physics looked like

After defect 3, **16 of 16 cells completed** (2 buildings x 2 cases x 5 `f`, 91 s wall on 16
workers, EnergyPlus ~28-30 s each). Building `27410`, 16 zones, 3,754.5 m²:

```
case A  f=1.00   cf 1.0000   annual 185,352.7 kWh   EUI 49.368 kWh/m2
case B  f=1.00   cf 0.9681   annual 185,486.6 kWh   EUI 49.404 kWh/m2
```

🟢 **Case A's coincidence factor is exactly 1 and Case B's is below it** — the paired synchronised
control behaves as a control and the independent-series case diversifies. ⚪ **This is a harness
observation on two buildings and is NOT a result:** nothing is scored, `G10N.x` is not computed, and
the authorisation on record is a shakedown that scores nothing.

### 9.3 🟢 `RE-PRE-REGISTRATION 2` — the London 706 is now the pre-registered population

`Step10_docs/prereg_step10_nocore_DRAFT.md`, **473 -> 596 lines**, append-only; the pre-RR2 bytes are
kept at `Step10_docs/impl/prereg_step10_nocore_DRAFT.bak_20260908_pre_rr2`.

```
frozen md5   1bc21094b0e09e3ac4332fa2e80abf75  ->  055331f285426a9928ca8f124fab7cc3
md5sum -c Step10_docs/prereg_step10_nocore_DRAFT.md.md5   ->  OK
```

Population, **re-measured by us** with the ruled basis, never carried from the peer:

```
es   1,175 payloads   1,100 ELIGIBLE  (11,244 zones)    75 Arm F    0 FAIL
uk     706 payloads     685 ELIGIBLE  ( 2,316 zones)     9 Arm F   12 FAIL   <- was 451/439/1,728
it   1,211 payloads   1,036 ELIGIBLE  (13,792 zones)   175 Arm F    0 FAIL
fr     297 payloads       0 ELIGIBLE  (     0 zones)   101 Arm F  196 FAIL   <- baseline, never a fold
THREE FOLDS  2,821 eligible buildings   27,352 Arm D zones   (was 26,764)
```

⚪ **The trade is recorded in both directions so it can never be quoted one-sided: +246 eligible
buildings and +588 Arm D zones, at the price of SIX buildings that used to be eligible and are now
`INTERZONE_MISMATCH_REROUTED`.** All twelve London FAILs stay FAIL; none is admitted.

🔴 **`R1` SEEN FAILING AGAINST THE SUPERSEDED TEXT.** The pre-RR2 file was temporarily restored and
the runner refused **by name**: *"R1 pre-registration md5 1bc21094… != frozen 055331f2… -- that is
the RE-PRE-REGISTRATION-1 text, before the author's 2026-09-08 sentence … uk 439 -> 685 eligible, C2
population 26,764 -> 27,352 Arm D zones"*. The live file was restored and re-verified `OK`.

### 9.4 🟢 THE BOLOGNA SHAKEDOWN IS RUNNING, AT FULL SIZE

```
python 4thJ_step10_nocore_campaign.py --district IT-BOL-GALVANI2 --shakedown --workers 16 --limit 0
1,036 buildings x 2 cases x 5 f = 10,360 cells      log: _local_runs/step10_nocore_bologna_20260908.log
payload_set_sha256 = 64d6768f8bdfa88d26d334aa8aa1ceae10408e6f63fabccd07a0d66ff8842d21
prereg_md5 in the preflight report = 055331f285426a9928ca8f124fab7cc3   (RR2, not the superseded text)
```

⚪ It is detached from any agent session and estimated at **~16 h** on 16 of 20 cores. 🔴 **An earlier
launch was KILLED THREE MINUTES IN, deliberately**: it had passed preflight under the old frozen md5,
so every manifest it wrote would have cited a **superseded pre-registration**. Re-freezing first and
restarting cost three minutes and bought a campaign whose provenance is not something to explain
later.

### 9.5 🟢 `--diary-diversity` IS RULED: `reseed`

The author's sentence is read as `reseed` — one trigger run per **drawn flat**, ownership redrawn, so
no two flats carry a byte-identical load series. `replicate` (100 runs per fold copied onto thousands
of flats) is the smaller dataset the sentence declines.

🔴 **What `reseed` does NOT do, recorded beside the ruling so it is never overstated: it does not
widen the occupancy pool.** Presence still comes from the **100** diaries Step 7 shipped, bound to
the flat by the `C2` manifest. `reseed` varies OWNERSHIP and the stochastic draw, never **who lives
there**. A stock-scale number computed this way remains evidence about geometry and aggregation.

🔴 **The flag still has NO DEFAULT, and a contradicting value is now refused BY NAME.** Both seen
firing, with the ruled mode passing as the control:

```
S9   --diary-diversity unset      -> REFUSE ... has NO DEFAULT ... That is the author's ruling
S9b  --diary-diversity replicate  -> REFUSE ... contradicts the ruling on record. The author ruled
                                     'reseed' on 2026-09-08 (...). Running the other mode needs a
                                     second sentence; passing it on the command line is not that
                                     sentence.
```

### 9.6 ⚪ What this session did NOT do

- It did **not** widen `D-EU-55`. **`R2` was observed refusing Madrid and London after the author's
  sentence was given**, because the sentence names no district and does not mention EnergyPlus.
- It did **not** move an engine digest pin, admit a rerouted payload, gate `partition_audit`, or
  re-open `C1`.
- It did **not** score anything: no `G10N.x`, no `G11.x`, no verdict, no band.
- It did **not** run Step 11. Items 11.4-11.7 stay PLANNED until the shakedown's cells exist.

### 9.7 🔴 OWED, AND NOW ONLY TWO — BOTH THE AUTHOR'S

1. **A second `D-EU-55` sentence naming Madrid and/or London**, if the other two folds are ever to
   run. One line naming the district is the whole requirement.
2. **Whether the shakedown, once finished, may be READ as a scored `G10N.x` result.** The
   authorisation on record says it scores nothing; `R8` refuses `--scored` until a second sentence
   says otherwise.

---

## 10 🔴 THE AUTHOR'S SECOND AND THIRD `D-EU-55` SENTENCES, THE MOVE TO SPEED, AND FOUR MORE HARNESS DEFECTS THAT ONLY A REAL RUN COULD FIND

Record for 2026-09-08 (last+48). Author's instructions, quoted and not summarised:

```
SENTENCE 2   "you choose as you reccommend also finish all three cities, not important order,
              for any computation simulation use 32 cpu of all speed reserouces, lets go"
SENTENCE 3   "all neighbourhoods done you can go until the end thank you"
             (separately)  "and update this one ...\Prompts\RESUME.md i am sleeping see you
              in the morning"
```

**Nothing scored. No `G10N.x` verdict computed. No pin moved. Nothing written under `OpenUBEM/`.**

### 10.1 These ARE a `D-EU-55` sentence, and "lets go use bigger datasets" was not — the difference, stated

`D-EU-55` asks for the author's own words naming what may run. The earlier sentence named a
*dataset size*; it was refused, and `R2` was **observed refusing Madrid and London after it was
given**. These two name all three of the things that were missing:

| what `D-EU-55` needs | the words that supply it |
|---|---|
| the districts | "all three cities" · "all neighbourhoods" |
| the act | "for any computation simulation" · "go until the end" |
| the resource | "32 cpu of all speed reserouces" |

🔴 **Two things they still do not do.**
1. **They do not reach Lyon.** `FR-LYO-HAUTCOEURPENTES` carries **no fold** — `R3` fires before
   `R2` is read and says in the code that it *is not waivable by any authorisation* — and its
   eligible population is **zero of 297 payloads**. **A sentence that says "all" does not create a
   fold.**
2. **They do not authorise a scored read.** Neither says "score"; "you choose as you reccommend"
   delegates *method*, not a pre-registered verdict. `scores` stays `False` on all three districts
   and `R8` still refuses `--scored`. ⚪ **This costs nothing, which is the whole argument: the
   cells a scored campaign writes and the cells this campaign writes are the same cells.** Scoring
   is a downstream read of finished manifests. Waiting loses no compute; inventing the sentence
   loses the only thing pre-registration is for.

### 10.2 `RE-PRE-REGISTRATION 3`, appended five times in one night, every superseded md5 named

596 → 1,006 lines, append-only, backup `impl/prereg_step10_nocore_DRAFT.bak_20260908_pre_rr3`, and
the byte prefix was **verified identical after every append**, not asserted.

```
055331f285426a9928ca8f124fab7cc3   RR2                      cited by the running Windows shakedown
ffe7eb39490b698d291e7332e89789fb   RR3.1-RR3.8              NEVER CITED BY ANY RUN
0dde360489096662781450a75c092e1e   + RR3.9  / RR3.10        NEVER CITED BY ANY RUN
b944706a79d1ebd4da78a309c184ef84   + RR3.11 / RR3.12        NEVER CITED BY ANY RUN
32ec52baf058a3da08cb78ac9808152f   + RR3.13 / RR3.14        NEVER CITED BY ANY RUN
7ce1c0417440798e0ca5d0b32a47d6c4   + RR3.15 / RR3.16        the pin the Speed campaigns run under
```

**All five superseded values are in `PREREG_MD5_SUPERSEDED`, so a run against any of them is refused
by name rather than by silence.** ⚪ Three of those appends are **corrections to text frozen minutes
earlier**: a staging digest that could not be the one that ships (`RR3.9`), a gloss that said
something the rule does not say (`RR3.11`), and two defects found after a freeze (`RR3.13`,
`RR3.15`) — each of which only a real EnergyPlus run on the new machine could have shown.
**Correcting a frozen section by appending is the discipline; quietly re-freezing it is not.**

### 10.3 The move to Speed, and what was verified ON Speed rather than assumed

The cluster had **no EnergyPlus at all** — not in `/encs/pkg` (310 packages listed), no module
(`module avail` matches `cilkplus` and nothing else), no singularity, no apptainer. It was installed
into scratch **from inside `sbatch`**, never on the login node:
`EnergyPlus-23.1.0-87ed9199d4-Linux-Ubuntu20.04-x86_64` on **AlmaLinux 9.8**, partition `ps`, every
job at the 7-day walltime floor.

🟢 **The three things that had to survive a byte copy did survive, and were checked there:**

```
prereg md5   7ce1c0417440798e0ca5d0b32a47d6c4   == the frozen sidecar          -> R1 passes
engine       6a14f428a6d8c26745af3e1483080bf31e3026ebb94702f90ac7eadc4ad2afd3  == PIN 2
nocore       21d723d5479076d0a57416ff92fd67a98fca8a33ff19343132415c144ff6b8ae  == NOCORE pin
```

⚪ **`PIN 2` is CRLF-dependent and it matched — which is exactly why the tree was shipped as a tar
and not cloned.** A `git clone` on Linux would have normalised the line endings and `R4` would have
refused, correctly, on an engine that is character-for-character the same code.

🟢 **The populations reproduce on a second operating system, from the staged bytes:**

```
ES-MAD-BERRUGUETE   1175 payloads -> 1100 eligible /  75 Arm F / 0 FAIL   11,000 cells
IT-BOL-GALVANI2     1211 payloads -> 1036 eligible / 175 Arm F / 0 FAIL   10,360 cells
GB-LDN-STDUNSTANS    706 payloads -> REFUSED BY R5 (see 10.7)
payload_set_sha256  es edd31fd9a79bb2695b1698b9019f1a4c913f5fe299f4d7de3384597db2e687c6
                    it 64d6768f8bdfa88d26d334aa8aa1ceae10408e6f63fabccd07a0d66ff8842d21
```

**Both payload digests are identical to the ones measured on Windows** — the digest normalises `\`
to `/` before hashing, so it is genuinely platform-independent — and both campaigns are pinned to
theirs with `--expect-payload-digest` (`R10`).

🟢 **Four refusals seen firing ON SPEED, with the two campaigns passing as controls:** `R3` on Lyon,
`R8` on `--scored` (its message quoting the author's own sentences back), `R5` on London, and the
extended `R6` on a deliberately wrong `ENERGYPLUS_PATH`.

⚪ **One environment note worth keeping.** Speed's default `python3` is **3.9**, which cannot even
import upstream's `X | None` annotations (`TypeError: unsupported operand type(s) for |`). A bare
`module load python/3.12.0` **did not change `python3`** — the working path is
`/encs/pkg/python-3.12.0/root/bin/python3`, and the venv lives at `opt/venv312`.

### 10.4 🔴 THE TRAP IN THE ENGINE-IDENTITY FIELD — the obvious check does not work

Moving the compute puts two different EnergyPlus binaries in play. The manifest records
`energyplus_build_hash`, so it looks as though engine identity is covered. **Measured, not assumed:
it is not.** That hash is the **source commit of the release** — `87ed9199d4` — and it is the same
string printed by the Windows build on this box (confirmed by reading a finished local manifest) and
by every official Linux build of 23.1.0. **The field that appears to separate the two engines does
not separate them at all.**

**The only manifest field that carries the distinction is `platform`** (`Windows 11 AMD64` locally).
The rule taken, written into the runner beside `AUTHORISED` and into `RR3.4`: **one campaign, one
engine build.** Madrid and Bologna run on the Linux binary. The Windows Bologna run is a
**shakedown** and is **never pooled** with them.

### 10.5 DEFECT 4 — a `/` in a building id reached a filesystem path, and every Madrid cell died

Bologna's ids are bare numbers; **Madrid's and London's are `relation/<n>` and `way/<n>`, and the
slash is part of the identity.** It was going straight into `cell_id`, which was then used as a
directory name, an `.idf` name and an output name:

```
es__relation/12582232__caseA__f000    HARNESS_ERROR
FileNotFoundError: ...\es__relation\12582232__caseA__f000\es__relation\12582232__caseA__f000.idf
```

**The fix keeps the identity and changes only the paths.** `cell_id` still carries the slash; a
derived `cell_slug` (`/` → `-`) is used for every path; **both go into the manifest** so a cell's
path can be checked against the identity it claims. **`R7` was extended, not relaxed** — it now
refuses if the slug is ever not one-to-one with the cell id, because two identities collapsing onto
one path would have one finished cell silently overwrite another. Seen failing, then seen passing,
on the same Madrid cells, and the run directories on Speed now read
`es__relation-12582232__caseA__f000`.

### 10.6 DEFECT 5 — two dependencies invisible to an import scan, because the imports are LAZY

Madrid's real cells on Speed died `ModuleNotFoundError: No module named 'geomeppy'`. The import sits
**inside `build_idf_for_cell`**, not at module top level, so the pre-submit scan that found
`numpy`/`pandas`/`shapely`/`geopandas`/`scipy` **could not see it**. `eppy` is in the same position,
and `joblib` came in behind an OpenUBEM submodule.

⚪ **A top-level import scan is not a dependency check.** Scan indented `import` lines too, then
prove it by importing the real modules on the target machine — which is now what the setup job does,
module by module, printing OK or FAIL for each, and looping until the chain closes.

### 10.7 🔴 DEFECT 6 — a hard-coded Windows path chose the SCHEMA, and its failure mode was a warning

`openubem.config` resolves the EnergyPlus IDD from `ENERGYPLUS_PATH`, defaulting to
`C:\EnergyPlusV23-1-0`. On Speed that path does not exist and **eppy does not stop** — it copies its
own **bundled IDD v8.0.0** into a temp file and continues, printing one line:

```
EnergyPlus 23.1 IDD not found at C:\EnergyPlusV23-1-0/Energy+.idd; falling back to eppy bundled
IDD v8.0.0 (BuildingSurface:Detailed field shift will cause fatal errors under EnergyPlus 9.6+)
```

**A v8 IDD shifts `BuildingSurface:Detailed`'s fields**, so every IDF would have been written
against a schema fifteen versions older than the binary running it. SEEN: **8 of 8 Madrid cells
`HARNESS_ERROR` behind that single line**, which scrolls past above the failures.

🟢 **`R6` is extended, not relaxed:** it already measured the version from the binary, and now also
refuses when the IDD is **missing** or comes from a **different install than the binary**. Seen
failing on a deliberately wrong `ENERGYPLUS_PATH` on both machines, with the unmodified box passing
as the control. On Speed the fix is upstream's own hook — `ENERGYPLUS_PATH` set to the install that
owns the binary — and **no constant was typed into our file**.

🔴 **The general lesson, and it is the `readvars.audit` lesson again: a fallback that warns is more
dangerous than a crash.** It converts a configuration error into a physics error somewhere else, and
every downstream gate sees only the symptom.

### 10.7b 🔴 DEFECT 7 — the same slash one level down, in the per-flat gain CSV FILE NAME

Fixing the slash in the **cell** path was not enough. Each drawn flat's gain series is written to
`run_dir / "<zone name>_gain.csv"` and upstream puts only that path's **basename** into
`Schedule:File`. With a Madrid zone named `relation/12582232_F0_dwelling_0`, the file landed in a
`relation/` subdirectory while the IDF asked for the bare name:

```
** Severe ** Schedule:File="EU_STEP8_GAINSCHEDULE_RELATION/12582232_F3_DWELLING_2_F000",
             File Name: "12582232_F3_dwelling_2_gain.csv" not found.
** Fatal ** ProcessScheduleInput ... Reference severe error count=18
            Program exited before simulations began.
```

**Same principle again: the zone name is identity and is unchanged in the IDF; only the file name is
slugged.** **`R7` was extended a second time** — it now refuses when two zone names in one building
slug to the same gain-csv name, because that collision would have one flat's series overwrite
another's **and EnergyPlus would run happily on the survivor**: a wrong answer with no error
anywhere, which is worse than the fatal above. Verified by reading the built IDF, then by running
two real Madrid cells through to completion on this box.

### 10.7c 🔴 MADRID CELLS COMPLETE AND CARRY `COMPLETED_WITH_UNSTABLE_MARKERS` — reported, not fixed

```
es__relation/12582232__caseA__f000   COMPLETED_WITH_UNSTABLE_MARKERS
EnergyPlus itself: "Completed Successfully -- 24 Warning; 0 Severe Errors"
matched marker: "Temperature out of range [-100. to 200.] (PsyPsatFnTemp)",
                Routine=PsyTwbFnTdbWPb, DURING SIZING, 1 time total,
                during Warmup 0 times, Input Temperature = -126.17 C
```

🔴 **This is not the thing the screen was written for.** `UNSTABLE_MARKERS` exists because *a
diverging heat balance EnergyPlus still calls a success* — an annual run whose zone air balance
never converges. What fired is **one psychrometric warning inside the sizing period**, zero during
warmup, with a clean annual run. The screen is behaving conservatively and exactly as written; the
label is simply broader than the condition it targets.

⚪ **What was deliberately NOT done: the marker list was not narrowed.** Editing a screen so results
stop being labelled is the same act as moving a pin, and it would have been done here on a sample of
two cells. The screen stays as it is, every affected Madrid cell will carry the label, and the label
is recorded per cell in `completion_status` where it can be **counted** at the end. Whether a
sizing-period psychrometric warning should be separated from a genuine heat-balance divergence is a
**pre-registration question for the author**, answerable from the finished campaign rather than from
two buildings.

⚪ **Seven harness defects this week, every one found by running a handful of cells before running
eleven thousand, and not one of them a physics change.** ⚪ And they are one pattern, not seven:
**an identity string reaching a place that is not a name.** Bologna's ids are bare integers, so none
of it was visible until a district with `relation/` and `way/` ids was authorised.

### 10.8 🔴 LONDON IS REFUSED BY `R5`, AND THE AUTHOR'S SENTENCE DOES NOT CHANGE THAT

```
REFUSE: R5 12 payload(s) classify FAIL under the ruled basis and a partial population is not a
campaign; first three: way/1054785382.json, way/1057093131.json, way/1057529443.json
  -- geometry_outcome='DWELLING_LAYOUT_EMITTED_INTERZONE_MISMATCH_REROUTED' -- core-era payload
```

These are the **same 12** `RE-PRE-REGISTRATION 2` adopted the 706 knowing about, six of them
regressions against the frozen 451. Nothing new has broken. What is new is that **London is now
authorised, so a gate that was always there finally fires.**

🔴 **Authorisation is permission to run. It is not permission to pass a gate.** `D-EU-55` and `R5`
are independent and the author's sentence reaches only the first. Two things would unblock London
and **neither is ours**:

1. **OpenUBEM re-emits those 12 payloads without the interzone reroute** — the fix that costs
   nothing scientifically. **Reported to them** with the three file names, and with the note that
   the other 694 classify correctly and that Madrid and Bologna pass cleanly from the same emission.
2. **The author re-pre-registers `INTERZONE_MISMATCH_REROUTED` as EXCLUDED rather than FATAL** — a
   change to the eligibility BASIS, which is a band change and not a tweak, and which would also
   cost six buildings that were eligible in the frozen 451.

⚪ **What was NOT done: `R5` was not relaxed, `--limit` was not used to skirt it, and no partial
London population was run.** A campaign that quietly drops its failures is what `R5` exists to
prevent.

### 10.9 What is running

```
SPEED   4J_c2_ES   job 1314969   ES-MAD-BERRUGUETE   11,000 cells   31 cpu   RUNNING  speed-08
SPEED   4J_c2_IT   job 1314970   IT-BOL-GALVANI2     10,360 cells   31 cpu   QUEUED behind it
LOCAL   PID 49648               IT-BOL-GALVANI2     10,360 cells   16 workers, Windows
both Speed jobs: -t 7-00:00:00, partition ps, venv312, ENERGYPLUS_PATH set to the staged install
```

🔴 **THE ONE DEVIATION FROM THE AUTHOR'S WORDS, AND IT IS DELIBERATE: 31 cpu, NOT 32.** The Slurm
association cap is **exactly `cpu=32` across all of the author's running jobs** — which is almost
certainly why "32" is the number in the sentence. A 32-cpu job therefore **cannot start while any
other job of theirs holds even one core**, and their own Lyon re-emission array has a straggler
(`1314065_11`, 1 cpu) that has been running **7 h 27 m** while its 32 siblings finished in between
28 s and 3 h 10 m. Submitted at 32, both campaigns sat in `AssocGrpCpuLimit` and would have sat
there all night; resubmitted at 31, Madrid started immediately.

⚪ **Why this is a throughput choice and not a result choice:** worker count enters nothing the
manifests record. It was a result choice once — the `readvars.audit` collision made outcomes depend
on how many workers ran — and that is exactly why it was fixed with `cwd=run_dir`. One line from the
author puts it back to 32.

⚪ **And it is deliberately NOT a `RE-PRE-REGISTRATION` change.** Worker count is not a
pre-registered quantity, and amending the frozen text now would put the **already-running** campaign
on a superseded md5 — the precise thing the first Bologna launch was killed for.

- Both Speed jobs are pinned to their payload digest, run under prereg `7ce1c041…`, and **score
  nothing**. Outputs land in `/speed-scratch/o_iseri/4J_step10_nocore/out/<district>/cells/`.
- 🔴 **They run SEQUENTIALLY, not in parallel** — 31 + 31 exceeds the 32-cpu cap, so Bologna starts
  when Madrid ends. Expect Madrid first, then Bologna.
- 🟢 **The local Windows Bologna shakedown is left running rather than killed**, and gains a purpose
  it did not have: **the same 1,036 Bologna buildings through two different EnergyPlus 23.1.0
  binaries at identical pins.** Any difference between them is a **measured platform sensitivity** —
  reported, never gated, never pooled. ⚪ It stays a shakedown; being useful does not promote it.
  Its manifests read `platform: Windows 11 AMD64`, `prereg_md5: 055331f2…`, `authorisation.mode:
  shakedown` — all correct for what it is. At 22:30 it had written **662 of 10,360 cells** at ≈11
  cells/min, which lands it mid-morning.

### 10.10 WHAT WAS NOT DONE — the list that matters more than the list above

- No pin moved: `ENGINE_DIGEST_PIN`, `NOCORE_DIGEST_PIN`, `REQUIRED_EP_VERSION` all untouched, and
  both engine digests were **re-verified on the new machine** rather than trusted.
- **No guard relaxed — two were tightened, `R7` twice.** `R7` now refuses a non-injective cell
  path slug AND a gain-csv name collision inside a building; `R6` now refuses a foreign or missing
  IDD. `R5` and `R8` still refuse. **The `UNSTABLE_MARKERS` screen was NOT narrowed** even though it
  now labels Madrid cells.
- No score, no `G10N.x`, no `G11.x`, no band, no verdict.
- Lyon not admitted; Arm F not promoted; Arm D and Arm F not pooled; `C1` not re-opened.
- The frozen sections above each correction were **not edited** — every correction is an append, and
  the byte prefix was checked each time.
- Nothing written under `OpenUBEM/`; the peer was told about the 12 payloads, not asked to grant
  anything.
- Step 11 not run. Items 11.4–11.7 stay PLANNED until cells exist.

### 10.11 🔴 OWED — NOW ONE ITEM, AND IT IS THE AUTHOR'S

**Whether the finished cells may be READ as a scored `G10N.x` result.** `R8` refuses `--scored`
until a sentence says so. The compute does not wait on it; only the reading does.

⚪ A second thing is owed by **OpenUBEM, not by the author**: the 12 rerouted London payloads. Until
they are re-emitted, London has no campaign — and that is a payload defect, not a permission
problem.

---

## 11. THE CAMPAIGNS RAN, AND THEY FOUND THE DEFECT THEMSELVES — 2026-09-08, after midnight

Record: `Step10_docs/prereg_step10_nocore_DRAFT.md` `RE-PRE-REGISTRATION 4`. **No pin moved, no guard
relaxed, nothing scored, no `G10N.x` verdict, nothing written under `OpenUBEM/`.**

### 11.1 What eighty cells of eleven thousand showed

Madrid started clean — preflight OK, 1,100 eligible of 1,175, payload digest matched, 11,000 cells —
and then:

```
  12582232   10 of 10   COMPLETED_WITH_UNSTABLE_MARKERS
  12582233   10 of 10   COMPLETED_WITH_UNSTABLE_MARKERS
  12628570    2 of 10   COMPLETED_WITH_UNSTABLE_MARKERS  (in flight)
  12582234   10 of 10   ENERGYPLUS_FAILED
  12638102   10 of 10   HARNESS_ERROR
```

🔴 **Both failures are per-building and total** — every case, every `f` level. **That shape is the
finding.** A race, a worker collision or a machine fault scatters; a property of the building does
not. Two of the first five buildings failed completely, which is a rate no campaign should be allowed
to discover on day three.

### 11.2 🔴 DEFECT 8 — five distinct flats, one name, and a guard that could not see it

The traceback did not exist anywhere on the cluster: **a failed cell writes no manifest**, and the
runner's `campaign_results.json` is written only after the last of eleven thousand cells returns
(§11.5). It was obtained by **reproducing the building deterministically on Windows**:

```
ValueError: European heating controls already emitted for zone
            'relation/12638102_F0_dwelling_0'
  openubem/idf/european_controls.py:48  in add_european_heating_controls
```

Read from the payload file itself, not through our reader:

```
layouts/relation/12638102.json   storeys 5   dwellings_total 1
  zone names:   relation/12638102_F0_dwelling_0   x5
```

🔴 **Five flats with different coordinates and different floor levels carry one identity.** The
storey index does not advance in the name when a building has one dwelling per floor — every storey
is `F0_dwelling_0`. `zone_records` copies `zone["name"]` verbatim, so **this is upstream's emission,
not our reading of it.**

**Measured on the frozen payload sets:**

```
ES-MAD-BERRUGUETE   1,100 eligible   233 buildings  21.2%   435 extra flats
IT-BOL-GALVANI2     1,036 eligible    35 buildings   3.4%    35 extra flats
GB-LDN-STDUNSTANS   still refused earlier by `R5`; unchanged
byte-identical duplicate groups 0 · geometrically distinct 233
buildings whose `zone_count_emitted` exceeds the count of DISTINCT names: 233 ES, 35 IT
```

⚪ **`zone_count_emitted` is commented in the runner as "what the gates read".** On a fifth of Madrid
it counts flats that cannot be told apart. **That is a population defect, and no amount of compute
turns it into a result.**

### 11.3 🔴 The blind spot was ours, and it was one word of reasoning

`RR3.15` had extended `R7` against gain-csv collisions the night before. It compared the wrong two
things:

```python
if len(set(slugged)) != len(set(names)):     # WRONG — set(names) collapses the duplicate too
if len(set(slugged)) != len(names):          # RIGHT — one csv per drawn flat
```

**A guard written to catch collisions collapsed the duplicates before counting them, and so passed
itself.** It caught two *distinct* names that slug alike; it was blind to *one name used twice* —
the plainer fault of the two.

🟢 **Seen failing on both real populations and seen passing on a control identical but for the
duplicated name:**

```
ES-MAD  REFUSED  R7 relation/12638102 emits 5 drawn flats under only 1 distinct gain csv name
ES-MAD  CONTROL PASSES  {'n_buildings': 1100, 'n_cells': 11000}
IT-BOL  REFUSED  R7 29680 emits 2 drawn flats under only 1 distinct gain csv name
IT-BOL  CONTROL PASSES  {'n_buildings': 1036, 'n_cells': 10360}
```

⚪ **`R7` tightened a third time; never relaxed.** ⚪ **Eight defects, one pattern, unchanged: an
identity string reaching a place that is not a name.** This is the pattern at its purest — the
identity is not mangled by a path, it is **not unique to begin with**.

⚪ **Upstream's refusal is what saved the numbers.** Had `add_european_heating_controls` not raised,
five flats would have written one gain csv in turn and **EnergyPlus would have run the survivor
happily** — one household's occupancy standing in for five, no error anywhere, in a fifth of Madrid.
**Third time this week the dangerous case was the one that kept going.**

### 11.4 🔴 All three runs stopped, and that follows from the guard rather than from judgment

```
scancel 1314969 1314970       Madrid (running 13m41s), Bologna (queued)
Stop-Process -Id 49648        the local Windows Bologna shakedown, at 1,424 of 10,360 cells
1314065_11                    the author's Lyon array straggler — NOT touched, it is theirs
```

🔴 **A corrected `R7` refuses both populations at preflight**, verified end to end on this machine
after the fix. A run whose preflight a corrected guard refuses cannot produce a `C2` result;
continuing it would have spent days of the author's allocation building a population that is not the
one on record.

⚪ **The author's *"you can go until the end"* is permission to run. It is not permission to pass a
gate.** `RR3` recorded that ruling for London, which is somebody else's district; applying it to the
author's own is the only thing that makes the ruling worth having written.

⚪ **The local shakedown was stopped too and the case for keeping it did not survive.** Its remaining
purpose was a cross-platform comparison against the Speed campaign; with that cancelled and both
populations refused there is nothing to compare, and *"it is only a shakedown"* is precisely the
exception that dissolves a rule.

⚪ **Nothing is lost as evidence and none of it is reusable as a result.** Madrid's partial log is
kept at `camp_ES_1314969.out.partial_keep` (165 lines, 81 status lines, 22 manifests). If the author
rules the affected buildings EXCLUDED, the population and its digest change, a re-pre-registration
follows, and every cell is rebuilt under it regardless.

### 11.5 🔴 A reporting defect in our own runner, recorded and deliberately NOT fixed tonight

A failing cell writes **no manifest**; its error and traceback live in `campaign_results.json`, which
is written **only after the eleven-thousandth cell returns**. For the whole of a multi-day run every
failure's diagnosis exists **in RAM only**, and a cancelled or walled job loses all of it. **This is
why defect 8 had to be reproduced on a second machine to be read at all.**

⚪ **Not fixed silently between two jobs.** What a run writes is part of the record a campaign
produces; the change belongs in the next re-pre-registration alongside the author's ruling.

### 11.6 ⚪ Reported, not gated — building `relation/12582234`

All ten of its cells died `ENERGYPLUS_FAILED`, and EnergyPlus said why:

```
** Severe ** GetSurfaceData: There are 47 degenerate surfaces; ... number of sides < 3
** Severe ** CalcCoordinateTransformation: Invalid dot product, surface="... STOREY 0 FLOOR 0001_1"
             (440293.987,4478595.557,0.000)
             (440295.762,4478592.694,0.000)
             (440295.762,4478592.694,0.000)
** Fatal  ** ... Program exited before simulations began.   48 Severe Errors
```

Repeated consecutive vertices — a zero-length edge — in **absolute UTM coordinates around
4.5 × 10⁶ m**, where a millimetre of separation is at the edge of what double precision preserves
through a coordinate transform. **This is a geometry property the engine measured, not a harness
fault.** One building of the five reached is far too small a sample to quote a rate; it is written
down so it is not rediscovered as news.

### 11.7 🔴 WHAT IS OWED, AND BY WHOM — the list is now three, and none of them is compute

⚪ **OpenUBEM's:** the no-core dwelling-layout emitter must advance the storey index in the zone name
when a building has one dwelling per floor. Reported with the building, the payload path and the
measured counts. 🔴 **We do not rename a zone to make a run pass** — manufacturing an identity the
emitter did not emit is the same act as moving a pin, and it would file five different flats' loads
under names we invented. **Their other owed item, London's 12 rerouted payloads, still stands.**

🔴 **The author's, and this file will not assume it:** whether the 233 Madrid and 35 Bologna
buildings are **EXCLUDED** from the population, as Arm F is, or remain **FATAL**, as `R5`'s 12
London payloads are. A **basis change, therefore a band change**, costing 21% of Madrid. **No
`--limit`, no filter and no partial population was used to get past it.**

🔴 **The author's, unchanged from last night:** whether the finished cells may be READ as a scored
`G10N.x` result. `R8` still refuses `--scored`. ⚪ **It now waits on the population question, because
there are no finished cells to read.**

⚪ **Step 11 items 11.4–11.7 stay PLANNED.** The seam is unaffected: none of this touches the lumped
internal gain or the appliance/DHW split.

---

## 12 🔴 DEFECT 8 IS RETRACTED — THE DEFECT IS OURS, AND IT IS THE POPULATION RULE ITSELF

**2026-09-09.** OpenUBEM replied (their dated file
`docs/docs_ACTIVE/europeanLocations/messages_GSSCanada/2026-09-09_OpenUBEM_to_4J_finding268_retracted.md`)
that the repeated zone name is **not an emitter defect**: it is **one zone drawn on every storey it
spans**, and they will not re-emit ES/IT for it. **A peer measurement is never carried — it was
re-measured here, on this machine, over every payload, before a word of it was accepted.**

### 12.1 Re-measured here, all payloads, not a sample

```
eu_ES-MAD-BERRUGUETE_data/layouts  1,175 files   233 buildings with a repeated zone name   435 extra entries
eu_IT-BOL-GALVANI2_data/layouts    1,211 files    35 buildings with a repeated zone name    35 extra entries
eu_GB-LDN-STDUNSTANS_data/layouts    706 files   630 buildings with a repeated zone name   787 extra entries
eu_FR-LYO-HAUTCOEURPENTES_data/lay.  297 files    22 buildings with a repeated zone name    31 extra entries

repeated entries whose zone object is BYTE-IDENTICAL (md5 of canonical json):   ALL of them
repeated entries whose geometry actually differs:                               0 of 1,288
```

The exemplar decides it. `layouts/relation/12638102.json` — `storeys 5`, **`dwellings_total 1`** —
holds the same zone object in all five `floors[]` rows:

```
storey_index 0  z_floor_m  0.0    zone md5 af87011a3802193a0e81a34b44f850e2   z_floor 0.0  z_ceiling 15.0
storey_index 1  z_floor_m  3.0    zone md5 af87011a3802193a0e81a34b44f850e2   z_floor 0.0  z_ceiling 15.0
storey_index 2  z_floor_m  6.0    zone md5 af87011a3802193a0e81a34b44f850e2   z_floor 0.0  z_ceiling 15.0
storey_index 3  z_floor_m  9.0    zone md5 af87011a3802193a0e81a34b44f850e2   z_floor 0.0  z_ceiling 15.0
storey_index 4  z_floor_m 12.0    zone md5 af87011a3802193a0e81a34b44f850e2   z_floor 0.0  z_ceiling 15.0
```

One dwelling occupying a five-storey house, **extruded once from 0.0 m to 15.0 m**. The field that
advances 0/3/6/9/12 is `floors[i].z_floor_m` — the **storey row's** elevation, not the zone's. Our
`zone_records()` reads `float(zone.get("z_floor", z_floor))`, i.e. it falls back to the storey row's
elevation, which is why five identical zones read as five distinct plates here and did not read as
byte-identical duplicates. **Our "geometrically distinct 233" was measuring the row, not the zone.**

Their invariant holds exactly, and it was checked on every eligible building, not argued:

```
eu_ES-MAD-BERRUGUETE   eligible 1,100   distinct zone names == dwellings_total   1,100 of 1,100   violations 0
eu_IT-BOL-GALVANI2     eligible 1,036   distinct zone names == dwellings_total   1,036 of 1,036   violations 0
```

So **nothing was going to overwrite five households' gain csvs — there is one household and one
csv.** The `ValueError` at `european_controls.py:48` is **that guard working as designed**: it
refuses a second emission of one zone, which is exactly what a per-storey-row loop attempts. `R7`
was refusing a real fault; it was simply not the fault named.

### 12.2 🔴 The real defect is the PRE-REGISTERED POPULATION RULE, and it is frozen

`§ N_u` of the runner, quoting the author's viewer ruling:

```
N_u  :=  sum over floors of len(floor["zones"])          <- what gates read
```

A zone that spans `n` storeys is counted `n` times by that rule. Measured over the eligible
population, entries versus distinct zones:

```
eu_ES-MAD-BERRUGUETE   1,100 buildings   entries 11,244   distinct 10,809   over-count   435
eu_GB-LDN-STDUNSTANS     685 buildings   entries  2,316   distinct  1,529   over-count   787   (34%)
eu_IT-BOL-GALVANI2     1,036 buildings   entries 13,792   distinct 13,757   over-count    35
                                         -------------    ------------      -----------
                                 TOTAL   entries 27,352   distinct 26,095   over-count 1,257
```

`27,352` is **exactly** the pre-registered `C2` population
(`prereg_step10_nocore_DRAFT.md:525` — "es 11,244 / uk 2,316 / it 13,792"). **The frozen
pre-registration counts 1,257 dwellings that do not exist**, London worst at a third of its stock.

🔴 **This is not a guard to relax and not a line to edit.** Correcting `N_u` to distinct zones is a
**basis change, therefore a band change** — the author's re-pre-registration, no one else's. The
prereg `e1f2822a800932ff099c15aed6be7ead` stays **untouched** until then. `R7` stays as it is: while
`N_u` counts entries, the runner would still attempt a second emission per spanned storey, and `R7`
refusing that is correct.

### 12.3 What OpenUBEM says is real, and what is coming

⚪ **London's reroute is real, ours to wait on, and it GREW.** `FINDING 263` (non-deterministic
near-duplicate-vertex reroute path), not fixed, no fix authorised. Their recut re-prepared every
district larger: **London 17 of 1,240 (was 12 of 706), Madrid 73 of 1,187, Bologna 93 of 1,215.**
The `2026-09-08 19:53` touch on `eu_GB-LDN-STDUNSTANS_data/layouts` was **not** a remedy
re-emission, which is why it was never announced. Their recommendation — pre-register the rerouted
buildings as excluded and score the remainder — is **the author's call, recorded, not taken.**

⚪ **A re-emission of all four districts' side-cars is in flight** (their task `T07`,
`scripts/emit_eu11_layout_sidecars.py`, recut trees `<DISTRICT>_recut_2026-09-08`): Madrid
1,175 → 1,187, Lyon 509 → 529 (side-cars for the first time), London 706 → 1,240, Bologna
1,211 → 1,215. **A population and provenance change, not a zone-naming change.** 🔴 **Consume
nothing until they announce sha, line endings, per-district counts and the row builder.** Every
count in this file is measured against the payloads frozen at `2026-09-08 06:51` and is superseded
by that announcement, never silently swapped.

### 12.4 🔴 What is owed, corrected

⚪ **OpenUBEM owes nothing on the zone name.** `FINDING 268` is retracted on both sides. Their
London reroute item stands, and it is now larger than it was.

🔴 **The author's, and it is now a different question than last night's.** Not "drop the 233 and 35"
— there is nothing wrong with those buildings. It is: **the frozen population of 27,352 counts
1,257 spanned zones more than once, and the corrected population is 26,095.** That is a
re-pre-registration and a band change. **Nothing runs until it is made** — not because a gate is
being negotiated, but because the campaign's registered population is not the stock on disk.

---

## §12.5 — THE CORRECTED POPULATION IS READABLE DIRECTLY FROM THE PAYLOAD (`dwellings_total`)

Upstream (`openubem-20`, 2026-09-09 06:18) confirmed the retraction is two-sided — our ES 233/435,
IT 35/35, LDN 630/787, LYO 22/31, the 0-of-1,288 md5 result, the 1,100/1,100 and 1,036/1,036
invariant and our `zone_records()` `z_floor` fallback are recorded on their side under
`FINDING 268` (`docs/docs_EXPLANATION/OpenUBEM_debug_References.md`, and §5 of
`messages_GSSCanada/2026-09-09_OpenUBEM_to_4J_finding268_retracted.md`).

They added one item that bears on the author's pending ruling, offered as a note and **not** as a
request: the corrected count needs **no de-duplication at all** — `dwellings_total` per building
(or `dwelling_count` per storey group) is the field **the emitter treats as authoritative**, so it
is the safer basis to re-pre-register against than "distinct zone names", even though both give the
same number.

**Re-measured here before carrying it** (all payloads, every district, outcomes
`{DWELLING_LAYOUT_EMITTED, DWELLING_LAYOUT_EMITTED_IMPUTED_COUNT}`):

```
ES   buildings= 1100  entries= 11244  distinct= 10809  sum(dwellings_total)= 10809  mismatches=0
LDN  buildings=  685  entries=  2316  distinct=  1529  sum(dwellings_total)=  1529  mismatches=0
IT   buildings= 1036  entries= 13792  distinct= 13757  sum(dwellings_total)= 13757  mismatches=0
LYO  buildings=  105  entries=   617  distinct=   586  sum(dwellings_total)=   586  mismatches=0
TOTAL ES+LDN+IT      entries=27352  distinct=26095  sum(dwellings_total)=26095
```

`missing_dwellings_total = 0` in every district; **zero buildings** where `dwellings_total` differs
from the distinct zone-name count — 2,926 of 2,926 agree, London included. §12.1's invariant was
proven on ES and IT only; this extends it to **London and Lyon**, which were the untested half.

Consequences for the ruling, and nothing more:

- The choice is unchanged in value — **27,352 (frozen rule) against 26,095 (real dwellings)** — but
  the corrected side is now available as a **read of one declared field**, not as a derived count.
- That removes the only technical argument for keeping the sum-over-floors rule (that the corrected
  population would need a de-duplication step the payload does not support). It does not remove the
  discipline: **a basis change is a band change and is the author's re-pre-registration.**
- 🔴 Still changed nothing: not `N_u`, not the prereg, not `R7`. `dwellings_total` remains
  PROVENANCE under the frozen record; it becomes a basis only if the author re-pre-registers it.

Upstream's `T07` four-district re-emission is still in flight — the merged results harvest that
precedes it is two districts of four complete. **Consume nothing** until they announce sha, line
endings, per-district file counts and the row builder. Every number above is measured against the
present stock (ES/IT 2026-09-08 06:51, LDN 2026-09-08 19:53) and is superseded the moment that
announcement lands.

---

## §13 — THE POPULATION RULE IS AMENDED, THE INSTRUMENT IS CORRECTED, NOTHING IS LAUNCHED

The author ruled on 2026-09-09 by delegation — *"no need to ask me anything keep goin as you
receommend"* — after being shown both candidates (27,352 / 26,095), the measurement, and the
statement that correcting the count is a basis change. Recorded as a delegation, not as a number
the author picked.

**The amendment.** `Step10_docs/prereg_step10_nocore_AMENDMENT_2026-09-09_population.md`,
md5 `86afe2043657f0bccf679c0781fd3d42`. The frozen DRAFT is **unedited and still frozen** — md5
re-verified `e1f2822a800932ff099c15aed6be7ead`, and `R1` still passes against it. Superseded values
are NAMED in the amendment, never overwritten in the DRAFT.

```
SUPERSEDED:  N_u := sum over floors of len(floor["zones"])   = 27,352  (es 11,244/uk 2,316/it 13,792)
IN FORCE:    N_u := distinct zone names == `dwellings_total` = 26,095  (es 10,809/uk 1,529/it 13,757)
```

**The instrument, all changes additive — no refusal relaxed, no pin moved, no field renamed:**

- `zone_records()` now returns one record per DWELLING (byte-identical storey repeats collapsed to
  the first occurrence) and no longer reads the storey row's `z_floor_m` as the zone's elevation.
- **New refusal `R11`**, two clauses: a repeated name with DIFFERENT geometry refuses (that is the
  genuine two-flats-one-name fault `DEFECT 8` was hunting, now caught instead of collapsed); and a
  building whose distinct dwellings differ from its declared `dwellings_total` refuses.
- `preflight_report.json` gains `dwellings_registered` and
  `payload_zone_entries_superseded_basis`, so the gap is auditable without re-deriving it.
- `R7`'s "one gain csv per flat" clause is **untouched**. It was refusing correctly all along
  because `N_u` counted entries; with the population corrected it passes on its own terms.
- Backup before the edit: `tools/4thJ_step10_nocore_campaign.py.bak_pre_l53`. Line endings verified
  LF before and after (an intermediate write had flipped the file to CRLF; restored byte-exactly).

**Seen passing, and seen still refusing** (`--dry-run`, this machine):

```
ES-MAD-BERRUGUETE   PREFLIGHT OK  1100 eligible / 75 Arm F / 0 FAIL  11000 cells
                    dwellings registered 10809  (superseded rule 11244)
IT-BOL-GALVANI2     PREFLIGHT OK  1036 eligible / 175 Arm F / 0 FAIL 10360 cells
                    dwellings registered 13757  (superseded rule 13792)
GB-LDN-STDUNSTANS   REFUSE R5     12 payloads INTERZONE_MISMATCH_REROUTED
FR-LYO-HAUTCOEURPENTES  REFUSE R3 the French baseline, not waivable
```

The runner's own numbers reproduce the independent sweep exactly. Both districts that pass are the
ones that passed nothing yesterday: `R7` refused every Madrid and Bologna cell.

**Geometry smoke** (`--limit 45 --dry-run` — builds IDFs, invokes no binary). The building that
died `HARNESS_ERROR` yesterday now builds:

```
es__relation-12638102__caseA__f000   1 ZONE   1 gain csv   dwellings_total 1
                                     vertex z 0.0 -> 15.0 m  (all five storeys, nothing lost)
es__relation-12582232__caseA__f000  18 ZONEs 18 gain csvs   dwellings_total 18
```

🔴 The correction removes 1,257 duplicate COUNTS. It removes no floor area, no volume, no building.

**Band change.** Every per-dwelling quantity now has a denominator smaller by 1,257 (es −435,
uk −787, it −35). No threshold VALUE changed and no `G10N.x` clause was touched. Nothing has ever
been scored under either basis, so no verdict is invalidated — there are none.

**NOT launched, and why.** Madrid and Bologna pass; London cannot until the rerouted payloads are
re-emitted or the author rules them excluded. Running the two that pass today would put London on a
different emission later, and `R10` says it in the file: *"a campaign that spans two emissions is
two campaigns."* Upstream's `T07` re-emission of all four districts is in flight
(Madrid 1,175→1,187, Lyon 509→529, London 706→1,240, Bologna 1,211→1,215). The campaign holds until
that lands, is announced (sha, line endings, per-district counts, row builder) and is re-measured
here. 🔴 **26,095 is the population of the 2026-09-08 emission, not a constant** — the amendment
pre-registers the RULE; the COUNT is re-derived at every preflight.

**Still open, deliberately not decided here:** the rerouted buildings. Upstream's exclusion
recommendation stays recorded, not taken — membership is a different act from counting, and their
re-emission is the better remedy.

⚪ Stale artefacts: `Step10_docs/outputs_step10_nocore/cells/` still holds 1,427 cell records from
2026-09-08 written under the superseded basis. Kept as prior evidence; not a current population;
overwritten by the next authorised run.

---

## §14 — 2026-09-09, 07:1x. THE PAYLOAD STOCK ON DISK IS NO LONGER THE EMISSION WE MEASURED

Measured, not inferred. Triggered by nothing more than an idle notice from `openubem-20`; I looked
at the shared tree before assuming it was unchanged, and it is not.

**What the three fold districts do now.** `--dry-run`, same runner, same machine, minutes after §13
recorded all three preflight results:

```
ES-MAD-BERRUGUETE   REFUSE R5   628 payloads FAIL   e.g. scheme='ruled_grid_1x1' (want nocore_equal_area)
IT-BOL-GALVANI2     REFUSE R5   620 payloads FAIL   e.g. scheme='ruled_grid_2x1'
GB-LDN-STDUNSTANS   REFUSE R5    38 payloads FAIL   e.g. scheme='ruled_grid_3x2'
FR-LYO-HAUTCOEURPENTES  REFUSE R3  (unchanged, not waivable)
```

Yesterday ES passed with 1,100 eligible and IT with 1,036. Nothing in our tools changed between
§13 and this section — the runner is byte-identical, `R7` is still untouched, `R11` is still in.
**What changed is the stock.**

**What is on disk now.** Whole-tree census, every payload, computed here:

```
eu_ES-MAD-BERRUGUETE_data  files= 961  digest=06388b0cc322c9ae9924700b8492bde93f7a787bc259b94ed5ae432fa253a4bd
   schemes  None 767 | ruled_grid_1x1 115 | ruled_grid_2x1 63 | i_shape 6 | l_shape 5 | 2x2 3 | 3x2 1 | narrow 1
   outcomes INTERZONE_MISMATCH_REROUTED 434 | FALLBACK_PENDING_LAYOUT 333 | EMITTED 194
eu_GB-LDN-STDUNSTANS_data  files=  82  digest=11969243edb6c5eaded6a2fc40b9cd5a99bc0965b96ba58bd9c8045782008e2f
   outcomes FALLBACK_PENDING_LAYOUT 44 | REROUTED 21 | EMITTED_IMPUTED_COUNT 17
eu_IT-BOL-GALVANI2_data    files=1204  digest=18e461875623f81964c3bf66d8fdd733d77badc662484f029388df537a993200
   outcomes FALLBACK_PENDING_LAYOUT 584 | REROUTED 395 | EMITTED_IMPUTED_COUNT 225
eu_FR-LYO-HAUTCOEURPENTES_data files=297 digest=3a53862284d9d54e958869548f081535264d7197dbb332bf515f3f346239e5f3
   outcomes EMITTED_IMPUTED_COUNT 105 | FALLBACK_PENDING_LAYOUT 101 | REROUTED 91
```

🔴 **Zero payloads carry `scheme='nocore_equal_area'` in any district.** This is the CORE-ERA
emission: every layout file is dated 2026-09-01 10:20–10:21. The 2026-09-08 no-core emission that
§12/§13 measured — ES 1,100 buildings / 11,244 entries / 10,809 dwellings, IT 1,036 / 13,792 /
13,757, LDN 685 / 2,316 / 1,529 — is **not in the tree any more**. Its only surviving trace is
London's `layouts_pre_D-EU-113_backup_2026-09-08/` (451 files, `scheme='nocore_equal_area'`,
`DWELLING_LAYOUT_EMITTED_IMPUTED_COUNT`), which is the superseded 451-filter set, not the 706.

**The tree is internally inconsistent right now.** `sources.json`, `buildings.csv` and `index.html`
in each district were rewritten today at 06:47, and London's `sources.json` already declares the
`T07` target — `"layouts_coverage": "1190 dwelling layout ruled, 50 massing box, 2 no IDF of 1242
residential"` — while `layouts/` beside it holds 82 core-era files from 09-01. Metadata has landed;
the layouts have not. The most economical reading is a re-emission IN FLIGHT, the tree reset to a
clean core-era state before the no-core layouts are written back. I do not assert the mechanism;
the timestamps, the schemes and the digests above are the facts.

**What this does NOT change.**

- The population RULE stands exactly as pre-registered on 2026-09-09
  (`prereg_step10_nocore_AMENDMENT_2026-09-09_population.md`, md5
  `86afe2043657f0bccf679c0781fd3d42`): `N_u := distinct zone names == dwellings_total`.
- The measurement of 26,095 stands as a measurement OF THE 2026-09-08 EMISSION. The amendment said
  so in advance, in §7 and again in bold: *"26,095 is the population of the 2026-09-08 emission,
  not a constant."* Today is that sentence being cashed, one day after it was written.
- `R11`, `R7`, `R5`, `R10` are untouched. Nothing is relaxed to make this stock pass — and nothing
  will be. A campaign against a core-era stock is not campaign `C2`.

**What it vindicates.** The decision in §13 not to launch Madrid and Bologna. Had they been
launched last night against the 2026-09-08 emission, the run would now be pointing at a tree whose
payloads have been replaced under it mid-flight; the manifests would name a `payload_set_sha256`
that no longer exists on disk, and the reporting defect already recorded (a failing cell writes no
manifest; `campaign_results.json` only after the last of 11,000 cells) would have hidden it until
the end. `R10`'s "a campaign that spans two emissions is two campaigns" was the right refusal for
the right reason.

**What is done about it: nothing is consumed.** The standing rule holds unchanged — consume nothing
from upstream until they announce sha + line endings + per-district counts + which row builder. The
digests above are recorded as the STATE OF THE TREE AT 07:1x on 2026-09-09, not as a new pin and
not as a population. When `T07` lands and is announced, every count is re-derived here from the new
stock; none is carried.

**Next action, unchanged in kind, sharper in fact:** wait for the announcement, then re-run
`--dry-run` per district, check `dwellings_registered` against the new `sum(dwellings_total)`, and
only then ask whether all three fold districts pass on ONE emission.

### §14.1 — the mechanism, confirmed in upstream's own code (2026-09-09, ~07:3x)

`openubem-20` answered the census: the metadata/layouts split is **their defect, not a re-emission
artefact**, and they named the line. I verified it here before recording it, as always.

`scripts/generate_eu_3d_viewers.py`, in `build_district`:

```python
    eu17_layouts_dir = idf_evidence_root / "layouts"
    target_layouts_dir = target_data_dir / "layouts"
    n_sidecars = sum(1 for _ in eu17_layouts_dir.glob("**/*.json")) if eu17_layouts_dir.exists() else 0
    if eu17_layouts_dir.exists() and n_sidecars > 0:
        if target_layouts_dir.exists():
            shutil.rmtree(target_layouts_dir)
        shutil.copytree(eu17_layouts_dir, target_layouts_dir)
```

Every viewer rebuild **deletes** the mirrored `layouts/` and re-copies it wholesale from the EU-17
rebuild tree — which is the 2026-09-01 core-era set. So each install of the 2026-09-08 no-core
payloads was silently undone by the next rebuild, including the 06:47 one whose `sources.json` I
measured. Independent confirmation of the copy source, counted here:

```
EU-17 source layouts   ES 961 | LDN 82 | IT 1204 | LYO 297
live mirrored layouts  ES 961 | LDN 82 | IT 1204 | LYO 297   <- identical, file for file
```

Their fix is ruling `D-EU-115`, in flight: copy EU-17 first, then overlay the EU-11 trees
oldest-to-newest so the mirror and the viewer's own reads cannot diverge again, and re-emit the
side-cars over the FULL recut population from the recut IDFs — single-vintage, not a
539-recut-plus-706-older mix. They note our `R10` would have called that mix two campaigns.

**On their request to discard the four 07:15 digests.** Not consumed, and not carried — but not
erased either. They are kept in §14 and in `RESUME.md` last+54 explicitly labelled **the state of a
broken intermediate tree, VOID as a pin and VOID as a population**. Deleting a measurement because
it turned out to describe a defect is the one thing this project does not do; naming it superseded
is. Nothing downstream reads them.

🔴 **Advance warning to carry into the next preflight.** Their re-emission covers the full
population per district, not the simulated delta, so the payload counts will be LARGER than the
1,100 / 1,036 / 685 buildings seen on the 2026-09-08 emission. `R11` clause (b) refuses a building
whose distinct dwellings differ from its declared `dwellings_total` — that clause is per building
and is unaffected by the population growing. **A bigger count at the next preflight is a different
emission, not a regression, and it is still re-derived here and never carried.** The amendment's
sentence stands: the RULE is pre-registered, the COUNT is measured per emission.

---

## §15 — 2026-09-09, ~07:5x. `T07` LANDED, VERIFIED HERE, AND ALL THREE FOLD DISTRICTS PASS ON ONE EMISSION

`openubem-20` announced the re-emission with everything the standing rule demands: row builder
(`scripts/emit_eu11_layout_sidecars.py`, run per district against
`openubem/outputs/eu_evidence/EU-11/<D>_recut_2026-09-08` with `--population-manifest`), where to
scan, per-district file counts, digests, line endings and a scheme census. Nothing below is carried
from that message; every number is re-derived here.

### 15.1 The tree on disk IS the announced emission

Their digest recipe was described, not published as code: "sha256 over the sorted list of relative
paths, each followed by a NUL and the sha256 of that file's bytes". My first reading (hex digest)
did not reproduce it, so I swept ten constructions against the smallest district. The recipe is
**relpath + NUL + the RAW 32 sha256 bytes**, no separator between records. With it:

```
ES-MAD-BERRUGUETE       1174 files  MATCH  ca49f91bc87d5425eb97dac4a6a8cd5065a0efc6b13772cc1ed71c777c7ac3c3
FR-LYO-HAUTCOEURPENTES   509 files  MATCH  be9d15aa6092d176868e1042be0d72682354c659c6442db81aab60cbf9ab48a1
GB-LDN-STDUNSTANS       1240 files  MATCH  80418b06b0f58f34a1116f5ee77ef11da98258945f998b80fbcfc56440f065a1
IT-BOL-GALVANI2         1211 files  MATCH  7557ec52c4137c7a55fb0b1d69a3c04878eefd5a1bd4f4e1c0a28f0aa8c71602
```

All four reproduce byte-for-byte. File counts match. Every layout file is dated 2026-09-09 (the
install), none before the 2026-09-08 recut.

**Line endings, measured file by file:** CRLF-only 1174 / 509 / 1240 / 1211 — **100 %, zero LF-only,
zero mixed** — and every file lacks a final newline, exactly as announced. We normalise on read; the
tree is not reflowed here. (`PIN 2` remains CRLF-dependent; nothing about it is touched.)

**Scheme and outcome census, ours:**

```
                    nocore_equal_area   scheme null + FALLBACK_PENDING_LAYOUT (empty floors)
ES-MAD                        1151                        23
FR-LYO                         496                        13
GB-LDN                        1207                        33
IT-BOL                        1171                        40
outcomes ES : EMITTED 1099 | BEST_EFFORT 49 | FALLBACK 23 | BEST_EFFORT_IMPUTED 2 | IMPUTED 1
outcomes LYO: IMPUTED 484 | FALLBACK 13 | BEST_EFFORT_IMPUTED 12
outcomes LDN: IMPUTED 1189 | FALLBACK 33 | BEST_EFFORT_IMPUTED 18
outcomes IT : IMPUTED 1036 | BEST_EFFORT_IMPUTED 135 | FALLBACK 40
has_unconditioned_core true --- 0 of 0 in all four districts (verified, not assumed)
```

🔴 **Zero `ruled_grid_*`, zero `INTERZONE_MISMATCH_REROUTED`, in any district.** The `FINDING 263`
reroute that refused London under `R5` for two days **does not exist in this emission**. London
passes without any ruling on exclusion: upstream's recommendation to exclude the rerouted buildings
was recorded and never taken, and re-emission turned out to be the remedy, exactly as §7 of the
amendment said it might.

### 15.2 The population, re-derived under the amended rule

`R11` clause (b) checked independently over every payload with non-empty `floors`:

```
                buildings   entries   distinct == dwellings_total   mismatches
ES-MAD               1151     12411        11976 == 11976                0
FR-LYO                496      7145         6786 ==  6786                0
GB-LDN               1207      5187         3910 ==  3910                0
IT-BOL               1171     15740        15705 == 15705                0
```

4,025 of 4,025 drawn buildings agree, zero mismatches, none missing — the amended rule holds on a
second, independently emitted stock. Fold total (es+uk+it) **31,591 dwellings**; the superseded
sum-over-floors rule would have registered 33,338.

### 15.3 Preflight — first time all three fold districts pass on ONE emission

```
ES-MAD-BERRUGUETE  PREFLIGHT OK  1174 payloads -> 1151 eligible / 23 Arm F / 0 FAIL  11510 cells
                   dwellings registered 11976 (superseded rule 12411)
                   payload_set_sha256 575960f547ce462a3754eaa8d1f84090f721b5fb7ca135324bb46b6769929486
IT-BOL-GALVANI2    PREFLIGHT OK  1211 payloads -> 1171 eligible / 40 Arm F / 0 FAIL  11710 cells
                   dwellings registered 15705 (superseded rule 15740)
                   payload_set_sha256 2cc6ba9512be91fae8974f9ade1dd55a8cc61683b66b4d23997abd214cd161a3
GB-LDN-STDUNSTANS  PREFLIGHT OK  1240 payloads -> 1207 eligible / 33 Arm F / 0 FAIL  12070 cells
                   dwellings registered 3910 (superseded rule 5187)
                   payload_set_sha256 1d575d0f7bfcddc7a1637c6d3c4803526d54f84060b3393bbe1cf8fb24bcfc18
FR-LYO             REFUSE R3 (unchanged, not waivable, and upstream is not asking us to run it)
```

Campaign size **35,290 cells** over 3,529 buildings. Those three `payload_set_sha256` values are the
runner's own construction (not upstream's recipe) and are what `--expect-payload-digest` must be
given at launch so `R10` can refuse a stock that moves under the run again.

`FINDING 258` under the new emission, still REPORTED NOT GATED: `partition_audit passed=false` on
796 / 1115 / 162 buildings, worst `area_error_fraction` 1.168e-04 / 1.651e-04 / 9.960e-05 — an order
of magnitude smaller than the 1.9e-2 seen on the old stock, still above a rounding residue.

### 15.4 Geometry smoke on the new payloads (IDFs built, no binary invoked)

```
uk__way-1054662329__caseA__f000    ZONE 1  gain csv 1  names 1  dwellings_total 1   z 0.00->9.00 m,  3 storeys
uk__relation-6171463__caseA__f000  ZONE 17 gain csv 17 names 17 dwellings_total 17  z 0.00->6.00 m,  2 storeys
es__relation-12582234__caseA__f000 ZONE 21 gain csv 21 names 21 dwellings_total 21  z 0.00->15.00 m, 5 storeys
```

Zones == gain series == dwellings == the payload's own declared count, on three buildings of three
different shapes, and every zone spans the building's full height. The corrected basis and the new
emission agree.

### 15.5 Recorded, not disputed: their `FINDING 269`

They report 29 buildings (Madrid 6, Lyon 20, Bologna 3) with a valid IDF and no layout payload, and
say no energy number is affected. Counted here, raw files: IDFs 1194 / 530 / 1240 / 1382 against
payloads 1174 / 509 / 1240 / 1211. The raw gaps (20 / 21 / 0 / 171) do NOT equal their stated
6 / 20 / 0 / 3, but the IDF tree is named by opaque 16-hex ids (`000faf0e6178d6ed.idf`), so
basenames cannot be reconciled with `relation/way` payload ids without their manifest mapping — the
counts are not comparable and I am not claiming a contradiction. **Not load-bearing for `C2` either
way:** our population is payload-driven, so a building with an IDF and no payload is simply not in
the campaign, and nothing here consumes their pooled EUI.

⚪ `eu_GB-LDN-STDUNSTANS_data/layouts_pre_D-EU-113_backup_2026-09-08/` was still present in both
mirrors at census time although they said it was being deleted. It is a SIBLING of `layouts/`, not
nested inside it, so our recursive read never sees it — unlike the trap of 2026-09-08. Re-check
before launch anyway.

### 15.6 What now blocks the launch — and it is ours, not upstream's

Every external blocker is gone: one emission, all three fold districts, zero FAIL, zero reroutes,
population verified on both sides, digests reproduced. What remains is the defect this project
recorded against its own runner and deliberately did not hurry: **a failing cell writes no manifest,
and `campaign_results.json` is written only after the LAST cell.** At 35,290 cells that means the
whole run is unreadable until it ends, and defect 8 already proved what that costs — it had to be
reproduced on a second machine to be seen at all. Launching 35,290 blind cells straight after a
two-day sequence of stock defects would be the one avoidable mistake left.

So the next act is the one already pre-registered as belonging here: a second amendment covering
per-cell manifest writing and incremental results, additive, no refusal relaxed, then launch with
`--expect-payload-digest` pinned per district. Nothing is scored, nothing is launched, and no band
is quoted until the per-dwelling denominators are re-derived on 31,591.

### §15.7 — corrections exchanged, 2026-09-09 ~08:1x (their reply, and one of ours to make)

**Ours to make: the 1,382 Bologna IDFs were my artefact, not their count.** They report 1,220 (1,215
top-level + 5 nested) and they are right. Broken down here:

```
find -name '*.idf' under IT-BOL-GALVANI2_recut_2026-09-08   = 1382
   idfs/ top level                                            1215
   idfs/<hash>/<hash>.idf  nested                                 5
   local_out/<hash>/ ... EnergyPlus RUN directories            162   (81 dirs x 2)
```

The `local_out` files sit beside `eplusout.eso` / `eplusout.err` / `Energy+.idd` — they are a
solver's working copies, not district IDFs. A recursive `find` swept them in. Their 1,220 stands;
my 1,382 is withdrawn. (Madrid 1,194, Lyon 530, London 1,240 agreed with them exactly.)

**Theirs to make, accepted:** `FINDING 269` is **27**, not 29 — ES-MAD 6, FR-LYO 18, GB-LDN 0,
IT-BOL 3; Lyon was double-counted. And the two measurements are different by construction, both
right: `FINDING 269` counts only buildings whose manifest DECLARES an emitted dwelling layout and
still has no payload, while a raw IDF-minus-payload gap also includes buildings that legitimately
get no layout (massing boxes, rerouted geometries). Nothing here is load-bearing for `C2` in either
form — our population is payload-driven.

**Also theirs, accepted:** the digest wording. They have corrected their protocol record to say
"raw digest bytes"; the recipe is relpath + NUL + the raw 32 bytes, as reconstructed in §15.1.

⚪ **The backup directory is deleted in ONE mirror, not both.** After their message:

```
docs/docs_ACTIVE/europeanLocations/outputs_3D/eu_GB-LDN-STDUNSTANS_data/layouts_pre_..._2026-09-08  GONE
openubem/outputs/3D/eu_GB-LDN-STDUNSTANS_data/layouts_pre_D-EU-113_backup_2026-09-08                451 files, PRESENT
```

The surviving one is in the tree our runner actually reads (`LAYOUT_ROOT`). It is a SIBLING of
`layouts/`, so a recursive read of `layouts/` still never sees it, and the preflight numbers in §15.3
are unaffected — but the two mirrors are not the same directory, which is itself worth knowing after
`D-EU-115`. Reported to them; not our tree to delete.

---

## §16 — 2026-09-09, ~08:0x. AMENDMENT 2: A RUN CAN NOW BE READ WHILE IT RUNS

The reporting defect recorded on 2026-09-08 and deliberately not hurried is closed, as a
**re-pre-registration made BEFORE the campaign runs** — the only honest time to make it.
`Step10_docs/prereg_step10_nocore_AMENDMENT_2026-09-09b_reporting.md`, md5
`0269860953ad0521fe2a3a2f5972d188`. The frozen DRAFT is untouched: md5 re-verified
`e1f2822a800932ff099c15aed6be7ead` afterwards, `R1` still passes. Amendment 1 (population) stands
unchanged beside it.

**The defect.** (a) a failing cell wrote NO file — its status lived in RAM for the whole run;
(b) `campaign_results.json` was written only after the LAST cell. At 35,290 cells that is a campaign
nobody can read until it ends, and `DEFECT 8` already had to be reproduced on a second machine
because the machine that hit it had nothing on disk.

**What changed — additive, backup `4thJ_step10_nocore_campaign.py.bak_pre_l56` md5
`25b16567f2f94d0bc24637d57fbbca8f`, LF-only verified before and after (77,239 bytes, md5
`ad8a586d0a681057cb3552e082165669`):**

1. `write_failure_record()` — a cell that does not complete writes `cells_failed/<slug>.json` with
   its identity, the pins it ran under, the failure dict including the traceback tail, wall seconds
   and a timestamp. 🔴 `"record_kind": "FAILURE_NOT_A_RESULT"`, and it goes to `cells_failed/`,
   **never** to `cells/` — `cells/` is the manifest population `G10N.14` reads, and a failure record
   there could be mistaken for a result.
2. `run_cell()` is now a thin wrapper; the 2026-09-08 body is `run_cell_inner()`, unchanged on the
   success path. The wrapper cannot rescue a cell or soften a status. A failure while WRITING the
   record is caught and reported beside the original (`failure_record_written: false`), never
   allowed to mask it.
3. `campaign_progress.jsonl` — one flushed line per finished cell after a `RUN_HEADER` carrying
   district, planned cells, `payload_set_sha256`, `prereg_md5`, `engine_sha256`, workers. Opened in
   APPEND mode so a second run cannot erase the first run's evidence.
4. `campaign_status.json` — counts by completion status, rewritten every `PROGRESS_EVERY = 25` cells
   and once at the end, saying in the file that it is in flight.
5. Closing print names the non-completing cells and where their records are; the docstring gained a
   `--- reporting ---` block.

🔴 **No refusal relaxed, added or renamed; no manifest field changed; `R7` and `R11` untouched;
`campaign_results.json` still written at the end and still the complete record.** Proof the
population path is undisturbed: ES preflight after the change returns the same 1,151 eligible,
11,510 cells, 11,976 dwellings and the same digest `575960f5…` as §15.3.

**Seen failing** — the shipped runner imported unmodified, `run_cell` called with geometry missing:

```
returned completion_status: HARNESS_ERROR      failure_record_written: True
record_kind: FAILURE_NOT_A_RESULT              traceback captured: True
identity kept: es__relation/12582234__caseA__f000 | relation/12582234 | fold es
cells/ untouched: True
```

**Seen working** — a real two-cell shakedown (`--shakedown --limit 2`, EnergyPlus 23.1.0, scratch
`--out`): both cells COMPLETED, the JSONL carried its header and one line per cell written as each
finished, `campaign_status.json` read `cells_finished 2 / completed 2`, and `campaign_results.json`
still landed at the end. Manifests: 18 zones, `cf` 1.0, `unstable_markers ["Temperature out of
range"]` → `COMPLETED_WITH_UNSTABLE_MARKERS`, handled exactly as before — this amendment does not
change how markers are treated.

**Seen NOT firing where it must not:** `--dry-run --limit 3` wrote progress, status, results and
preflight files and **no `cells_failed/` directory**. `DRY_RUN` is excluded by name, so a smoke
cannot manufacture failure evidence.

**Launch conditions now.** (1) one emission all three fold districts pass — met by `T07`; (2) the
population rule pre-registered and the count re-derived at preflight — met, 31,591 dwellings;
(3) a run readable while it runs — met here; (4) `--expect-payload-digest` pinned per district at
launch — **not optional, the stock moved twice in two days**: ES `575960f5…`, IT `2cc6ba95…`,
UK `1d575d0f…`. Per-dwelling bands must be re-derived on 31,591 before any verdict is quoted; there
are no verdicts to invalidate because nothing has ever been scored.

⚪ Upstream closed their arc: the backup directory is now deleted in BOTH mirrors (verified here —
zero `layouts_pre_D-EU-113_backup_2026-09-08` directories remain anywhere under `OpenUBEM/`), they
recorded its 451 files and a checksum first, and they wrote the two-mirror point into their plan doc.
`FINDING 258`, `263` and `269` stay open by their ruling with no fix planned in that arc.

---

## 17. THE LAUNCH — `C2` submitted to Speed, 2026-09-09

The four launch conditions recorded in §16 were met, so `C2` was launched. This section is the
record of WHAT was launched, WHAT was verified before it started, and WHAT was deliberately moved
aside so that nothing from a superseded emission can be read as part of this campaign.

### 17.1 What was on Speed before, and why none of it could be used

The 2026-09-08 deployment was still in place. It was **not** reusable, and the check that proved it
is the same one that caught the stock swap on 2026-09-09:

```
shipped tree, payload counts:  ES 1175   LYO 297   LDN 706   IT 1211
T07 emission, payload counts:  ES 1174   LYO 509   LDN 1240  IT 1211
shipped frozen prereg md5   :  7ce1c0417440798e0ca5d0b32a47d6c4
frozen prereg md5 in force  :  e1f2822a800932ff099c15aed6be7ead
shipped runner md5          :  6bd2e4e0f7af002251cd29900fd6b4ca   (pre-Amendment 2)
runner md5 in force         :  ad8a586d0a681057cb3552e082165669
```

Three of the four line up with a different campaign than the one authorised. The cancelled ES job
`1314969` on that tree had also finished 83 cells with **60 `COMPLETED_WITH_UNSTABLE_MARKERS`, 13
`ENERGYPLUS_FAILED` and 10 `HARNESS_ERROR`** — a 28 % non-completion rate whose diagnosis was
unreachable, because that runner wrote no file for a failing cell. That is precisely the defect
Amendment 2 closed, and it is why this launch is readable and that one was not.

Nothing was deleted. `tree`, `out` and `runs` were renamed `*_superseded_2026-09-08` inside the
sbatch job, so the cancelled run's 60 manifests survive as evidence of a different emission and can
never be swept into `C2`'s population.

### 17.2 What was shipped, and how it was proved to arrive intact

The tree was rebuilt from the **exact file list of the previous deployment** — 6,675 paths — so that
nothing the runner needs could be silently dropped by a hand-written include rule. Every one of them
existed locally: `copied=2756 missing=0`, with `__pycache__` excluded (stale bytecode is a hazard,
not a dependency) and `openubem/outputs/**` replaced wholesale by the T07 stock. The two amendments
travel with the tree, so the run carries the record of what it ran under.

Shipped as a **tar, never a clone** (`PIN 2` is CRLF-dependent):

```
4J_s10_tree_T07_20260909.tar.gz   79,481,159 bytes   6,922 files
sha256 local  39ff25dc79ea1c406effd1b307eae3a415d8b69200897ba335b99eb0c2c006bc
sha256 remote 39ff25dc79ea1c406effd1b307eae3a415d8b69200897ba335b99eb0c2c006bc   <- byte-identical
```

### 17.3 Deploy + preflight on the cluster, job `1315012` (COMPLETED, 00:05:04)

Extraction and every check ran **inside `sbatch`** — the login node is zero-compute.

```
files extracted                6922
runner md5                     ad8a586d0a681057cb3552e082165669   <- in force
frozen prereg md5              e1f2822a800932ff099c15aed6be7ead   == its own sidecar
Amendment 2 md5                0269860953ad0521fe2a3a2f5972d188
payload counts                 ES 1174   LYO 509   LDN 1240   IT 1211   <- T07
nested backup directories      none
```

Preflight, all three fold districts, each pinned to its own digest — identical to the numbers
derived on Windows in §15, on a different platform, from a tar:

```
ES-MAD-BERRUGUETE  1174 -> 1151 eligible / 23 Arm F / 0 FAIL   11510 cells   11976 dwellings
IT-BOL-GALVANI2    1211 -> 1171 eligible / 40 Arm F / 0 FAIL   11710 cells   15705 dwellings
GB-LDN-STDUNSTANS  1240 -> 1207 eligible / 33 Arm F / 0 FAIL   12070 cells    3910 dwellings
                                                       total   35290 cells   31591 dwellings
```

Two refusals were **seen firing on the cluster, on the launch tree, minutes before the launch** —
a pin that is never observed refusing is not a pin:

```
R10  ES given a digest that is not its own
     "REFUSE: R10 payload set digest 575960f5... != expected 0000...  -- the emission on
      disk is not the one this run was authorised against.  A campaign that spans two
      emissions is two campaigns."
R3   Lyon
     "REFUSE: R3 ... Lyon is a physical baseline ...  This refusal is not waivable by any
      authorisation."
```

### 17.4 The launch itself

```
1315013  4J_c2_ES  ES-MAD-BERRUGUETE  digest 575960f5...  11510 cells   RUNNING on salus, 31 cpu
1315014  4J_c2_IT  IT-BOL-GALVANI2    digest 2cc6ba95...  11710 cells   PENDING (afterok:1315013)
1315015  4J_c2_UK  GB-LDN-STDUNSTANS  digest 1d575d0f...  12070 cells   PENDING (afterok:1315014)
```

Decisions taken and why:

* **31 cpu, one district at a time, chained `afterok`.** The Slurm association cap is `cpu=32`
  across ALL of this user's jobs, so three concurrent districts would each get a third of the
  cores and finish no sooner in total. Sequential gives each district the full allocation, keeps
  every job far inside the 7-day walltime (~32 h each at the measured rate), leaves one core for
  the author, and makes ES readable and reviewable while IT and UK are still queued. `afterok`
  also means a failed or cancelled ES stops the chain instead of burning four days.
* **`--expect-payload-digest` on every job**, per district. Not optional: the stock moved twice in
  two days, and `R10` is the only thing that notices it moving *under* a running campaign.
* **`--shakedown`**, which is the authorisation on record. `--scored` remains refused by `R8`;
  this run scores nothing.
* **One engine build for the whole campaign** — the Linux 23.1.0 in `opt/`, `PIN 2` verified by
  `R4` at every preflight. The Windows two-cell shakedown of §16 is never pooled with it.

🔴 **This is a RUN, not a verdict.** No `G10N.x` is computed by this tool; per-dwelling bands must
be re-derived on 31,591 before any number is quoted.

---

## 18. READING THE RUN — the first failure class, diagnosed from disk (2026-09-09)

Amendment 2 was made so that a campaign could be read while it runs. Within six minutes of the
launch it earned itself: `campaign_status.json` at 25 cells showed **15 completed / 10
`ENERGYPLUS_FAILED`**, and the ten failures had a record each on disk. Under the pre-amendment
runner this would have been ten lines of stdout and nothing else — exactly the state that forced
`DEFECT 8` to be reproduced on a second machine.

### 18.1 The failures are one building, not a rate

The ten failure records are ten cells of a SINGLE building:

```
es__relation-12582234__caseA__f000 f015 f030 f050 f100
es__relation-12582234__caseB__f000 f015 f030 f050 f100
```

That is the whole 2 cases x 5 `f` grid for `relation/12582234`. Every other cell finished. So the
"40 % failure" the first status file appears to show is not a rate at all: it is one building whose
geometry EnergyPlus refuses, multiplied by the ten cells that building owns. 🔴 **A per-cell
percentage computed over a partial run is meaningless while cells are grouped by building; the unit
of this failure class is the BUILDING.** At the first check with 46 cells finished, buildings
touched = 5, buildings failed = 1.

### 18.2 What the engine actually refused

From `runs/ES-MAD-BERRUGUETE/es__relation-12582234__caseA__f000/eplusout.err`:

```
** Warning ** GetSurfaceData: Very small surface area[1.99055E-004],
              Surface=BLOCK RELATION/12582234_0 STOREY 0 FLOOR 0001_1
   ... 40 more of the same, 1.99E-4 and 2.21E-4 m2 ...
** Warning ** GetSurfaceData: There are 80 coincident/collinear vertices; These have been deleted
** Severe  ** GetSurfaceData: There are 47 degenerate surfaces; ... number of sides < 3
** Severe  ** CalcCoordinateTransformation: Invalid dot product,
              surface="BLOCK RELATION/12582234_0 STOREY 0 FLOOR 0001_1":
              (440293.987,4478595.557,   0.000)
              (440295.762,4478592.694,   0.000)
              (440295.762,4478592.694,   0.000)
**  Fatal  ** CalcCoordinateTransformation: Program terminates due to preceding condition.
EnergyPlus Terminated--Fatal Error Detected. 123 Warning; 48 Severe Errors;
Elapsed Time=00hr 00min  1.11sec
```

The third vertex repeats the second. EnergyPlus deleted 80 coincident vertices, 47 surfaces fell
below three sides, and the coordinate transformation of the first of them terminated the run before
the simulation began. `returncode 1`, `unstable_markers: []`, one second of engine time — the cell
cost ~271 wall seconds, essentially all of it building the 959 KB IDF.

### 18.3 The payload is NOT malformed — measured, not assumed

The obvious suspicion is a bad layout. It is wrong. A read-only census of every zone polygon in the
three fold districts (`scan_degenerate.py`, shoelace area + consecutive-vertex distance):

```
ES-MAD-BERRUGUETE   1174 buildings  12411 zone polygons   dup-vertex 0   tiny-area 0
IT-BOL-GALVANI2     1211 buildings  15740 zone polygons   dup-vertex 0   tiny-area 0
GB-LDN-STDUNSTANS   1240 buildings   5187 zone polygons   dup-vertex 0   tiny-area 0
```

Not one payload polygon has a repeated vertex or an area below 1e-2 m2. `relation/12582234`'s
smallest zone is **60.03 m2**. The 1.99e-4 m2 surfaces do not exist in the payload; they are
manufactured downstream, when the storey plates are extruded and intersected into an IDF.

### 18.4 What DOES distinguish the building: a millimetre edge

Sweeping the minimum distance between any two vertices of any zone polygon, per building
(`scan_tol.py`, `mingap_all.py` -> `mingap.csv`, 3,625 rows):

```
the failing building : min vertex gap 0.001000 m | min edge 0.001000 m | min zone area 60.03 m2

district min-vertex-gap (ES): min 0.001000  p05 0.0010  median 0.6895
buildings with two zone vertices closer than 0.001 m :  73 (6.2 %)
                                            0.01  m : 140 (11.9 %)
                                            0.1   m : 260 (22.1 %)
```

Exactly 1.000 mm, on the nose, and it is not unique — it is a floor, which is the signature of a
snap tolerance in the regularization step, not of noise. Across the three fold districts:

| district | buildings | min gap <= 1 mm | min gap <= 10 mm |
|---|---|---|---|
| ES-MAD-BERRUGUETE | 1174 | 96 (8.2 %) | 140 (11.9 %) |
| IT-BOL-GALVANI2 | 1211 | 147 (12.1 %) | 251 (20.7 %) |
| GB-LDN-STDUNSTANS | 1240 | 16 (1.3 %) | 32 (2.6 %) |

A 1 mm edge is below EnergyPlus's own coincident-vertex tolerance, so the two ends collapse to one
point, the surface loses a side, and `GetSurfaceData` calls it degenerate. That is the mechanism,
and it is consistent with every line of the `.err`.

### 18.5 🔴 The predictor OVER-SELECTS — stated before anyone quotes it as a forecast

Of the five buildings run by the first check, **two** carry a 1 mm gap:

```
relation/12582232  0.034986   completed
relation/12582233  0.953555   completed
relation/12582234  0.001000   ENERGYPLUS_FAILED  x10 cells
relation/12628570  0.001000   completed          (all cells)
relation/12638102  0.025495   completed
```

`relation/12628570` has the same millimetre edge and ran to completion. So a millimetre gap is
NECESSARY-looking but demonstrably NOT SUFFICIENT: whether the collapse drops a surface below three
sides depends on where the edge sits in the plate. 🔴 **The 140 / 251 / 32 counts are a CEILING on
exposure, not a forecast of failures, and must never be quoted as an expected loss.** The real rate
comes from the run, at the end, over buildings.

### 18.6 What is NOT being done about it

- Nothing in the instrument is changed mid-campaign. The engine is `PIN 2`; the runner is
  `ad8a586d0a681057cb3552e082165669`; a run that changes its instrument at cell 46 is not a run.
- No cell is retried, rescued, reclassified or excluded. Amendment 2 says so in its own §5.
- No building is dropped from the population to make the completion rate look better. The
  population was fixed at preflight: 1,151 / 1,171 / 1,207 eligible.
- The failure is upstream geometry, not our harness — unlike `DEFECT 4` (the `/` in `relation/n`
  reaching a filesystem path) and the shared-cwd `readvars.audit` collision, both of which were ours
  and both of which were fixed before launch. The distinction matters: those made physics-shaped
  noise out of a harness bug; this is the engine correctly refusing a bad solid.
- 🔴 A campaign that ends with N buildings in `cells_failed/` is a campaign with a stated completion
  rate, not a campaign that passed. Per-dwelling denominators are re-derived on the dwellings that
  actually produced results, and the shortfall against 31,591 is reported, never absorbed.

### 18.7 The stock did not move under the run — re-checked, not assumed

A peer session announced a North American re-simulation arc and measured three of its open defects
against our four districts (zone multipliers: census of all 4,171 recut IDFs, no value other than 1;
district heating in non-hot-water end uses: 81 preserved Bologna `.sql`, no row above zero, and they
stated plainly that 81 is a sample not a census; negative zone volumes: the "Indicated Zone Volume"
string absent from all 81, against 8,160 of 8,160 in their North American run 4). Their conclusion
was that nothing they gave us moves.

That is a measurement, so it is evidence — and it was still re-measured here rather than carried.
The runner's own `--expect-payload-digest` was pointed at the local tree for all three fold
districts, minutes after the peer's message:

```
ES  575960f547ce462a3754eaa8d1f84090f721b5fb7ca135324bb46b6769929486   PREFLIGHT OK
    1174 payloads -> 1151 eligible / 23 Arm F / 0 FAIL, 11510 cells, 11976 dwellings
IT  2cc6ba9512be91fae8974f9ade1dd55a8cc61683b66b4d23997abd214cd161a3   matches the pin
UK  1d575d0f7bfcddc7a1637c6d3c4803526d54f84060b3393bbe1cf8fb24bcfc18   matches the pin
```

All three are byte-for-byte the digests the three submitted jobs pin. `D-EU-115`'s
`rmtree`+`copytree` has not fired again. (The IT and UK lines above were obtained by handing `R10` a
truncated prefix on purpose, so the refusal printed the full digest it had computed — the refusal
working is the evidence.)

### 18.8 First widening of the sample — the over-selection is now measured, not inferred (10:25 EDT)

Ninety cells finished, nine buildings complete (each building owns exactly ten cells, so the sample
is nine whole buildings, not a ragged edge). Every building was cross-checked against `mingap.csv`
BEFORE looking at its outcome:

```
relation/12582232  min gap 0.034986   completed
relation/12582233  min gap 0.953555   completed
relation/12582234  min gap 0.001000   ENERGYPLUS_FAILED  (all 10)
relation/12628570  min gap 0.001000   completed
relation/12628571  min gap 0.001000   completed
relation/12638102  min gap 0.025495   completed
relation/12638103  min gap 0.001000   completed
relation/12700585  min gap 0.262665   completed
relation/12702625  min gap 0.242745   completed
```

Four of the nine carry the millimetre edge; **three of those four completed**. The signature is
still perfectly NECESSARY in this sample (no building without a 1 mm gap has failed) and now
measurably far from sufficient: 1 failure in 4 exposed buildings, not 4 in 4.

🔴 This sharpens §18.5 rather than softening it. The 140 / 251 / 32 exposure counts remain a
CEILING; on this sample the realised rate inside the exposed set is one in four, and one in nine
over buildings — but nine buildings is nine buildings. **No rate is quoted as the campaign's rate
until the campaign ends.** Status at this reading: 80 `COMPLETED_WITH_UNSTABLE_MARKERS`, 10
`ENERGYPLUS_FAILED`, ES `1315013` RUNNING on `salus`, IT `1315014` and UK `1315015` still PENDING on
`afterok`.

### 18.9 Can it be solved? Yes — and not by us, and not during this run

The mechanism is now specific enough to say what a fix would be, so it is worth stating plainly what
each candidate costs:

1. **Upstream raises the snap tolerance.** The 1.000 mm floor is a regularization constant in the
   layout emitter; anything at or below EnergyPlus's coincident-vertex tolerance will be welded
   away by the engine and can drop a surface below three sides. Snapping at, say, 10 mm — or welding
   vertices closer than the engine's own tolerance before emission — removes the whole class. This
   is the real fix. 🔴 It is a NEW EMISSION: new payload digests, therefore a new campaign, and
   `R10` would refuse the running one the moment the stock changed under it. It cannot be adopted
   mid-run and must not be requested as an urgent mid-run patch.
2. **We weld vertices in our own IDF construction.** Technically the smallest change, and refused:
   it is an instrument change at cell 46 of 35,290. A run that changes its instrument mid-way is not
   a run. It also silently moves geometry the emitter pre-registered, which is the same act as
   renaming a zone to make a run pass.
3. **Drop the exposed buildings.** Refused outright — the population was fixed at preflight
   (1,151 / 1,171 / 1,207 eligible) and shrinking it to improve a completion rate is exactly the
   move this project has refused everywhere else.

🔴 **So the answer this run gives is: nothing changes now.** The campaign runs to the end, the
completion rate is stated over buildings, the shortfall against 31,591 dwellings is reported and
never absorbed, and the millimetre measurement is handed to the geometry side as a MEASUREMENT — not
as a request to re-emit mid-run — so that the next emission can close the class properly.

### 18.10 The constant found in source, re-measured here, and the author's ruling (10:40 EDT)

`openubem-20` answered the measurement by finding the cause in their own source, without using our
numbers. Re-measured in our local checkout before carrying anything:

```
openubem/geometry/european_nocore.py:131   g = set_precision(g, 0.001)
openubem/geometry/european_nocore.py:616   return set_precision(g, 0.001)
openubem/geometry/european_nocore.py:620   return set_precision(g.buffer(0), 0.001)
openubem/geometry/layoutGenerator.py:112   VERTEX_SNAP_M = 0.005   # "well under E+ 1 cm coincident tol"
openubem/idf/surfaces.py:702               footprint = shapely.set_precision(footprint, 0.005)
```

So the 1.000 mm floor measured in §18.4 is a literal constant, not an artefact of the data. One
correction to their report: there is no `set_precision` at `:610`, only 131 / 616 / 620 — not
load-bearing. 🔴 Their scope note matters and is worse for us than for them: **both snap paths are in
OUR path** — `european_nocore.py` is what `C2_NOCORE_PATH` points at and `surfaces.py:702` is in the
IDF build — so the 5 mm sites are not somebody else's exposure. The comment at `layoutGenerator.py:112`
calls 5 mm "well under E+ 1 cm coincident tol", which is the defect restated as a reassurance: being
UNDER the tolerance is precisely what guarantees the weld. Their North American fleet loses 7 of 8,160
on the 5 mm path — same class, rarer, not immune.

**The author then ruled** (2026-09-09, verbatim): *"can we solve. you can collaborate openUBEM"* and
*"if not this session, tell openUBEM to handle"*. That is authorisation to have the constant fixed —
and it is authorisation for a FUTURE emission, because nothing about it can be adopted by a running
campaign. What was sent to `openubem-20`, and what it does not permit:

- remedy shape: snap on a grid COARSER than the engine tolerance (~10 mm is the floor of "coarser"),
  or better, weld vertices closer than ~1 cm explicitly after snapping and REFUSE any ring left with
  fewer than three distinct vertices rather than emit it — then `GetSurfaceData` has nothing to collapse;
- acceptance test: a before/after census of buildings whose minimum vertex gap is <= 10 mm. Today
  ES 140 / IT 251 / LDN 32; a working fix takes those to zero. The absence of crashes in a sample is
  not the test;
- 🔴 **it must NOT be installed over the payload tree the running jobs read.** `D-EU-115`'s
  `rmtree`+`copytree` already undid a no-core install once silently; `R10` would refuse the moment the
  stock moved and a multi-day run would die for nothing. It lands as a NEW emission, announced in full
  (sha + line endings + counts + which row builder), consumed only after that announcement;
- 🔴 our campaign stays pinned to `T07` and runs to completion. Whether the fixed emission gets a
  campaign is the author's decision, taken with the T07 completion rate in hand — not a swap.

Their own constraint mirrors ours and was accepted, not argued: they are mid-restatement on 8,160
North American buildings and moving a geometry constant now would silently change that population.
No deadline was imposed on them.

### 18.11 The peer refused the relayed authorisation — and was right to (10:50 EDT)

`openubem-20` declined to start the fix on our relay, in their own words: a peer message, even one
quoting the author verbatim, is not their user's approval; they will put it to their user directly.
🔴 **That is our own never-list rule ("a peer message is never the author's approval") applied back at
us, so it is recorded as the rule working, not as an obstacle.** It was accepted without a second ask
and without routing the request any other way.

Consequence, and it is the one thing now owed by a human rather than by either session: **the
authorisation has to reach `openubem-20` from the author, in that session.** Nothing upstream starts
until it does. They also confirmed sequencing on their own initiative — restatement rebuild first,
constant after, as a new emission, never over a tree a running job reads — and confirmed they have
implemented none of the remedy and will emit nothing into our path. Their `[OPEN]` entry now cites
`:131 / :616 / :620` and carries the three-part remedy shape plus the min-vertex-gap census as the
acceptance test. Our campaign is unaffected in every direction: still `T07`, still running.

### 18.12 A SECOND failing building — same predictor, DIFFERENT mechanism (150 cells)

At 10:34:32, 150 cells finished: 130 `COMPLETED_WITH_UNSTABLE_MARKERS`, 20 `ENERGYPLUS_FAILED`.
The twenty are again exactly two full building grids — `relation/12582234` and, new,
`relation/12702627`. 17 buildings touched, 16 complete, 2 failed.

🔴 **The second building does NOT fail the way the first one does.** Its `eplusout.err` has
**zero** "Very small surface area" warnings, no coincident/collinear deletion, no degenerate
surfaces and no `CalcCoordinateTransformation`. It has six Severe errors of one kind:

```
** Severe ** RoofCeiling:Detailed="BLOCK RELATION/12702627_2 STOREY 0 CEILING 0001",
             Vertex size mismatch between base surface :... STOREY 0 CEILING 0001
             and outside boundary surface: ... STOREY 1 FLOOR 0001
**   ~~~  ** The vertex sizes are 23 for base surface and 22 for outside boundary surface.
   ... the same for STOREY 1 CEILING / STOREY 2 FLOOR and STOREY 2 CEILING / STOREY 3 FLOOR ...
**  Fatal ** GetSurfaceData: Errors discovered, program terminates.
EnergyPlus Terminated--Fatal Error Detected. 3 Warning; 6 Severe Errors; Elapsed Time=0.26sec
```

A ceiling and the floor directly above it are the SAME plate seen from two sides. One copy has 23
vertices and the other 22. That mismatch is in the IDF **as written** — EnergyPlus deleted nothing
here; it read two halves of an interzone pair that no longer agree and refused. So the snap did not
merely make a sliver: on one of the two copies it removed a near-duplicate vertex and on the other
it did not. Same root cause family (a snap floor below what the pair-matching needs), different
symptom, and it terminates in 0.26 s instead of 1.11 s.

Deterministic, not stochastic: all ten cells of the building carry the identical six Severe errors.

**Cross-check against `mingap.csv` for all sixteen finished buildings:**

```
relation/12582232  0.034986  completed          relation/12702626  0.001000  completed
relation/12582233  0.953555  completed          relation/12702627  0.001000  ENERGYPLUS_FAILED
relation/12582234  0.001000  ENERGYPLUS_FAILED  relation/12702628  0.001000  completed
relation/12628570  0.001000  completed          relation/12702629  0.034482  completed
relation/12628571  0.001000  completed          relation/12702630  0.316621  completed
relation/12638102  0.025495  completed          relation/12702631  0.352389  completed
relation/12638103  0.001000  completed          relation/12702632  0.043658  completed
relation/12700585  0.262665  completed
relation/12702625  0.242745  completed
```

**Eight of sixteen carry the 1.000 mm edge; both failures are among those eight; six of the eight
completed.** The predictor stays perfectly necessary in this sample and is now measured at **2 of 8
exposed (25 %)** — up from 1 of 4, on twice the sample. 🔴 The 140 / 251 / 32 exposure counts remain
a CEILING; 25 % of a ceiling is still not a forecast, and it is quoted here as a measurement of this
sample, nothing more.

**What this changes for the remedy.** The fix sent to the geometry session was framed as "snap
coarser than the engine tolerance". This second mechanism says that is necessary but not the whole
shape: **the two copies of an interzone plate must be snapped identically, or matched after
snapping** — a coarser floor applied independently to a ceiling and to the floor above it can still
produce 23 vs 22. The acceptance test is unchanged and still covers both (the census of buildings
with min vertex gap <= 10 mm must go to zero), because both mechanisms live on the same exposed set.

**What this changes in the run: nothing.** Instrument, population and pins untouched at cell 150.

### 18.13 The "second" mechanism is the DOMINANT one — and the mismatch is always exactly one vertex (330 cells)

At 10:58:21, 319 cells had finished: 279 `COMPLETED_WITH_UNSTABLE_MARKERS`, 40 `ENERGYPLUS_FAILED`.
Thirty-two buildings had a complete ten-cell grid; **four of them failed** — `relation/12582234`,
`relation/12702627`, `relation/12713026`, `relation/12725306` — and a fifth, `relation/12800464`,
was already failing its first cells in flight.

🔴 **§18.12 called the vertex-size mismatch "the second mechanism". That framing is now wrong by
count.** Every new failure is mechanism (b). One building fails the way §18.2 describes; **four
fail the way §18.12 describes.** The `CalcCoordinateTransformation` route is the rare one.

Each of the three new buildings was read, not assumed. The absence list of §18.12 reproduces
exactly — for all three, and for the in-flight fifth:

```
                       small-area  coincident  degenerate  CalcCoordTransform  Vertex mismatch
relation/12713026           0           0           0              0                 yes
relation/12725306           0           0           0              0                 yes
relation/12800464           0           0           0              0                 yes
```

Nothing was deleted by the engine in any of them. The defect is in the IDF as written.

#### The new measurement: the two copies differ by EXACTLY ONE vertex, every time

EnergyPlus prints the pair sizes, and reports each plate twice (once from each side):

```
relation/12702627   23 vs 22   (x3 plates)
relation/12713026    8 vs  9   (x2 plates)
relation/12725306   15 vs 14   (x1 plate)
relation/12800464    8 vs  9   (x4 plates)
```

Never two, never three — **always one**. That is a much sharper statement than "the two faces were
snapped independently": it says a single snap merged **one** vertex pair on one copy of the plate
and left the other copy alone. A wholesale re-polygonization of one face would not land on a
difference of one, four buildings running. It also explains why the run time is a fraction of a
second: `GetSurfaceData` refuses before geometry processing gets anywhere.

#### The predictor, re-measured on 32 buildings — still perfectly necessary, still far from sufficient

```
complete-grid buildings          : 32
  carrying the 1.000 mm edge     : 14
    of those FAILED              :  4   (12582234, 12702627, 12713026, 12725306)
    of those COMPLETED           : 10
failures NOT on the 1.000 mm edge:  0
```

The in-flight fifth, `relation/12800464`, also reads exactly `0.001000`. So across three
independent enlargements of the sample — 4, then 8, then 14 exposed buildings — **no building
without the millimetre edge has ever failed, and the failure share among exposed buildings has sat
at 25 %, 25 %, 29 %.** 🔴 The 140 / 251 / 32 exposure counts remain a **CEILING**, and the ~29 %
is a sample statistic from one district's first thirty-two buildings, not a forecast. Neither
number may be quoted as an expected loss.

Building-level state at this read: **4 failed of 32 complete (12.5 %)**, one more failing in flight.

#### What this changes in the run: nothing

No cell retried, no building dropped, no instrument touched at cell 330. `C2` stays pinned to
`T07`. What it changes is the remedy's centre of gravity: the clause that matters most upstream is
**snap the two copies of an interzone plate identically (or re-match after snapping)** — the
coarser-tolerance clause alone would not have saved four of these five buildings. The acceptance
test is unchanged, because both mechanisms live on the same exposed set: the census of buildings
with a minimum vertex gap of 10 mm or less (ES 140 / IT 251 / LDN 32) must go to zero.

🔴 **The falsifier for the paragraph above, stated so it can be checked cheaply: a difference of
TWO.** "Always exactly one" is a claim, and it is refutable by the next failing building. If any
plate ever prints vertex sizes differing by more than one, that means two independent merges on one
copy, and the coarser-tolerance clause goes back in front of the identical-snap clause. So the
reading procedure for every newly failing building is: read the `vertex sizes are X ... and Y` lines,
not just the `Fatal`. This is the same discipline that found the second mechanism in the first place
— §18.12 exists because someone looked instead of assuming.

### 18.14 Fourth enlargement, 349 cells — the discriminator hardens, nothing new appears

Read at 11:05 EDT, one hour and one minute of ES wall time. **349 cells of 11,510 — 299
`COMPLETED_WITH_UNSTABLE_MARKERS`, 50 `ENERGYPLUS_FAILED`**, IT `1315014` and UK `1315015` still
PENDING on `afterok`. The 50 failures are still exactly five whole buildings, ten cells each:

```
relation/12582234   relation/12702627   relation/12713026   relation/12725306   relation/12800464
```

`relation/12800464` — the building that was failing in flight at §18.13 — has now completed its
grid, all ten cells `ENERGYPLUS_FAILED`, which is the determinism check passing again. **No sixth
failing building has appeared.** Buildings touched 37; complete ten-cell grids **34**, of which five
failed: **5 of 34 (14.7 %)**.

The predictor, re-measured on the 34 complete grids rather than carried from §18.13:

```
complete grids                34
carrying the 1.000 mm edge    15   -> 5 failed, 10 completed   (33 %)
off the millimetre edge       19   -> 0 failed
```

🔴 **Zero failures off the millimetre edge, now across nineteen buildings.** Four independent
enlargements have given the same shape — exposed 4, 8, 14, 15 with shares 25 %, 25 %, 29 %, 33 % —
and the off-edge column has never once been non-zero. That is the discriminator hardening, and it is
still a **ceiling on exposure, never an expected loss**: two thirds of the exposed buildings ran to
completion.

Because no new building failed, **the difference-of-two falsifier had nothing to be checked
against this window.** It is not confirmed by silence; it is simply untested since §18.13, and the
reading procedure stands for the next failing building.

One building now in flight is worth naming for the reading that follows, as EXPOSURE and not as a
forecast: `relation/12837457` has a minimum vertex gap of **0.006000 m** — inside the 10 mm
acceptance census but NOT on the 1.000 mm floor. Every failure so far has sat exactly on that floor.
🔴 If that building fails, it is the first failure off the millimetre edge and the discriminator
narrows from "a 1 mm snap floor" to something wider; if it completes, the floor stands. Either way
it is read, not predicted.

#### What this changes in the run: nothing

No cell retried, no building dropped, no pin moved, no instrument touched at cell 349. `C2` stays
pinned to `T07`. The completion rate is still stated over BUILDINGS at the end, and the per-dwelling
bands are still re-derived on the dwellings that actually produced results against 31,591.

### 18.15 🔴 THREE CORRECTIONS AT 596 CELLS — the millimetre discriminator is falsified, and the third mechanism is OURS

Read at 11:26 EDT, 1:21:52 of ES wall time. **596 cells of 11,510 — 516
`COMPLETED_WITH_UNSTABLE_MARKERS`, 80 `ENERGYPLUS_FAILED`.** Eight whole buildings now, ten cells
each. Three of them are new since §18.14, and reading them — rather than assuming they were more of
the same — overturned two things this document asserted one section ago.

#### Correction 1 🔴 "Zero failures off the millimetre edge" is FALSE. §18.14 is wrong.

`relation/13113580` failed all ten cells with a **minimum vertex gap of 1.040812 m**. Not a
millimetre. Not inside the 10 mm acceptance census. A metre. The number was re-measured straight
from the payload rather than carried from `mingap.csv`, and the two agree:

```
relation/13113580   floors 3, zones per floor 5,5,5
  floor 0: (nverts,mingap) = (6, 2.012587) (7, 1.040812) (6, 2.265635) (6, 2.182) (4, 7.502632)
  BUILDING MIN VERTEX GAP: 1.040812 m
```

§18.14 said the off-edge column "has never once been non-zero" and called that the discriminator
hardening. One read later it is non-zero. 🔴 **The millimetre edge is NOT a necessary condition for
this failure class, and the acceptance test as written in §18.12–18.14 — the census of buildings
with a minimum vertex gap of 10 mm or less must go to zero — is INSUFFICIENT. It would not have
caught this building.** That has to reach `openubem-20`, because it changes what "fixed" means: a
snap-tolerance change alone can pass that census and still leave this building dead.

What it does NOT overturn: the mechanism or the off-by-one signature. `13113580` is mechanism (b),
nothing deleted, and its plates print

```
The vertex sizes are 7 for base surface and 8 for outside boundary surface.   (x2 plates)
   base    : BLOCK RELATION/13113580_3 STOREY 1 CEILING 0001_1
   partner : BLOCK RELATION/13113580_4 STOREY 2 FLOOR 0001_3
```

**7 versus 8 — a difference of exactly one, the fifth building in a row.** The difference-of-two
falsifier still has not fired. So the identical-snap / re-match clause survives; what dies is the
claim that a sub-millimetre gap is what triggers it. Something merges or splits one vertex on one
copy of an interzone plate in a building whose closest two vertices are a metre apart, and the
`set_precision` constants cannot be the whole story.

⚪ One tempting reading, recorded and explicitly NOT claimed: the payload has a 7-vertex zone and no
8-vertex zone anywhere, which looks like a vertex being ADDED to one copy rather than merged away.
It is not evidence, because the payload's vertex counts do not survive the build in general — for
`relation/12702627` the reported pair is 23 vs 22 and the payload has only 4, 9, 15 and 34. Counts
change downstream routinely. The honest statement is the narrow one: the mismatch is manufactured
during the build, and a millimetre gap is not required to manufacture it.

#### Correction 2 🔴 There is a THIRD mechanism, and it belongs to US, not upstream

`relation/12863111`, all ten cells, 8 warnings and exactly **one** severe:

```
** Severe  ** GetSurfaceData: Construction EU_ROOF_CONSTRUCTION of interzone surface
   BLOCK RELATION/12863111_8 STOREY 0 ROOF 0001_2 does not have the same materials in the
   reverse order as the construction EU_FLOOR_CONSTRUCTION of adjacent surface
   BLOCK RELATION/12863111_7 STOREY 1 FLOOR 0001_2
**  Fatal  ** GetSurfaceData: Errors discovered, program terminates.
```

No vertex mismatch, no coincident deletion, no degenerate surface, no `CalcCoordinateTransformation`.
This is not geometry at all. Block `_8` is shorter than block `_7`, so `_8`'s storey-0 roof is an
INTERIOR partition against `_7`'s storey-1 floor. The payload says the same thing: this building has
9 zones on floor 0 and 8 on floors 1–4, so one zone stops short.

The cause is in this repository, in `tools/4thJ_step10_nocore_campaign.py`, lines 1038–1045:

```python
for surface in idf.idfobjects["BUILDINGSURFACE:DETAILED"]:
    kind = str(surface.Surface_Type).upper()
    if kind == "WALL":                      surface.Construction_Name = wall
    elif kind in ("ROOF", "ROOFCEILING"):   surface.Construction_Name = roof
    elif kind in ("FLOOR", "CEILING"):      surface.Construction_Name = floor
```

The two faces of one interzone plate carry different `Surface_Type` values, so this loop hands one
of them `EU_ROOF` and the other `EU_FLOOR`. EnergyPlus requires an interzone pair to carry
constructions that are exact material reverses; two different no-mass constructions are not. The
loop assigns by surface type and never asks whether the surface is interzone.

🔴 **§18.6 says "the failure is upstream geometry, not our harness". That sentence is WRONG for this
building, and it is corrected here rather than quietly left standing.** It remains right for the
other seven.

🔴 **It is not being fixed during the run, and that is the same rule applied to ourselves that we
applied to upstream.** Changing the instrument at cell 596 would mean the campaign built its IDFs
two different ways, which is not a campaign. This is a defect recorded, reproduced and left alone —
the same handling the reporting defect got before it became Amendment 2, and it belongs in the next
re-pre-registration for the same reason.

🔴 **Consequence for the end of the run: the failing buildings must be reported SPLIT BY MECHANISM.**
Buildings killed by our own construction assignment must never be counted as upstream geometry
losses. Attributing our own defect to someone else's emission would be the reporting equivalent of
moving a pin.

#### Correction 3 — mechanism (a) is no longer a single building

`relation/13033801` is the second building on the `CalcCoordinateTransformation` route: 72 very
small surfaces (8.14e-4 m²), a coincident-vertex deletion, a degenerate-surface severe, three
`CalcCoordinateTransformation` lines, 379 warnings and 93 severe errors, Fatal in 0.51 s. Its
minimum vertex gap is 0.001000 m. So (a) has two buildings and (b) has five.

#### A predictor measured and REJECTED

Since the construction defect needs a short block abutting a taller one, "zone count varies between
floors" looked like a cheap census. It was measured — ES 587 of 1174 (50.0 %), IT 1004 of 1211
(82.9 %), LDN 146 of 1240 (11.8 %) — and then checked against the buildings that have actually
finished:

```
varying zone count :  5 failed, 27 completed
constant zone count:  3 failed, 31 completed
```

🔴 **It does not discriminate, so it is rejected, not quoted.** Most short-block roofs are genuinely
exterior — the neighbouring blocks do not overlap — and the census would have condemned half of
Madrid and four fifths of Bologna for a defect that has killed one building. Recorded so that nobody
picks it up later as a screening rule.

#### Where the numbers stand

```
cells                     596 of 11,510    516 completed-with-markers / 80 failed
buildings touched         60
complete ten-cell grids   66  ->  8 failed  (12.1 %)
on the 1.000 mm edge      23  ->  7 failed, 16 completed   (30 %)
off the millimetre edge   43  ->  1 failed, 42 completed
mechanism (a) CalcCoordinateTransformation : 2 buildings
mechanism (b) vertex size mismatch         : 5 buildings  (all off by exactly one)
mechanism (c) OUR construction assignment  : 1 building
```

Every one of the eight failed all ten of its cells with the same severe counts and the same Fatal
line, so all three mechanisms are deterministic properties of the geometry or of the build, not
chance.

#### What this changes in the run: nothing

No cell retried, no building dropped, no pin moved, no line of the instrument touched at cell 596 —
including the construction loop, which is now a known defect of ours and stays exactly as it is
until this campaign ends. `C2` stays pinned to `T07`.

### 18.16 🔴 THE RINGS ARE IDENTICAL IN THE FILE — the remedy clause is dead, and the millimetre is manufactured by the build

`openubem-20` proposed, with no ask attached, to stop predicting the failure from payload gaps and
measure the thing itself: pull the two named surfaces out of the **emitted IDF** and compare their
vertex rings, count and coordinates, *before* EnergyPlus reads them. They stated the consequence in
advance and in both directions — if the rings already differ in the file, their emitter is writing
two independent rings; if they match and EnergyPlus still complains, the cause moved downstream and
they are wrong about the whole mechanism.

The test was available on disk here, unbuilt and unrun: the runner's cleanup loop deletes the `.idf`
only on the **success** path (after the manifest is written), so every failing cell still holds the
exact file EnergyPlus refused. No rebuild, no re-run, no change to anything.

#### The measurement

`scratchpad/rings.sh` / `rings2.sh` — for each of the five mechanism-(b) buildings, parse
`eplusout.err` for every `Vertex size mismatch between base surface : ... and outside boundary
surface: ...` line, then pull both surfaces out of the emitted IDF and compare the rings as written.

```
relation-12702627   6 pairs named   every pair: SAME COUNT (34 vs 34), xy-multiset identical
relation-12713026   4 pairs named   every pair: SAME COUNT (25 vs 25), xy-multiset identical
relation-12725306   2 pairs named   every pair: SAME COUNT (32 vs 32), xy-multiset identical
relation-12800464   8 pairs named   every pair: SAME COUNT (10 vs 10), xy-multiset identical
relation-13113580   2 pairs named   every pair: SAME COUNT ( 9 vs  9), xy-multiset identical
```

**22 named pairs across five buildings, and not one of them differs in the file.** The partner ring
is the base ring reversed — same vertices, opposite winding, which is exactly what an interzone pair
is supposed to be. For `relation/13113580`:

```
base    BLOCK RELATION/13113580_3 STOREY 0 CEILING 0001_1   n=9
  (440432.594,4479115.030) (440432.906,4479116.336) (440435.235,4479126.652)
  (440427.990,4479128.397) (440426.252,4479120.872) (440426.253,4479120.872)
  (440425.522,4479117.708) (440427.530,4479117.267) (440427.291,4479116.254)
partner BLOCK RELATION/13113580_4 STOREY 1 FLOOR 0001_3     n=9
  the same nine points, reversed
```

#### 🔴 Consequence 1 — the load-bearing remedy clause is DEAD

Since §18.10 the remedy carried in every artefact and in every message to `openubem-20` has been
**"snap the two copies of an interzone plate identically, or re-match after snapping."** That clause
is now falsified by direct observation: **the two copies ARE identical, to the last decimal, in the
file EnergyPlus read.** There is nothing to snap identically that is not already identical.

The vertex-count difference the engine reports — 7 versus 8, 23 versus 22 — is therefore produced
**inside EnergyPlus, after it reads the file**, when it removes coincident and collinear vertices
from each surface separately. The only asymmetry between the two copies is their winding direction.

⚪ **NOT claimed:** that the winding is *why* one copy loses an extra vertex. That is a candidate,
not a cause. EnergyPlus's cleanup source has not been read here, and no measurement in this campaign
distinguishes "the walk is order-dependent" from any other explanation. The measured statement is
the narrow one: the two rings enter the engine identical and leave its cleanup different.

#### 🔴 Consequence 2 — the millimetre is real, but the BUILD makes it, not the payload

This resolves the puzzle §18.15 opened. `relation/13113580`'s payload zone ring has **7 vertices and
a minimum gap of 1.040812 m**. The same plate in the emitted IDF has **9 vertices, including a pair
1 mm apart** — `(440426.252, 4479120.872)` and `(440426.253, 4479120.872)`. Across whole files
(`scratchpad/gap_idf.sh`, minimum edge length of every `BuildingSurface:Detailed`):

```
building              surfaces   surfaces with an edge < 10 mm   min edge (m)   outcome
relation/12582232          152                    0               0.034986      completed
relation/12582233          175                    0               0.953555      completed
relation/12628570          204                    5               0.001000      COMPLETED
relation/12582234          443                   78               0.000118      failed (a)
relation/12702627          280                   96               0.001000      failed (b)
relation/12713026          174                   95               0.001000      failed (b)
relation/12725306          215                  112               0.001000      failed (b)
relation/12800464          535                   60               0.000437      failed (b)
relation/12863111          328                   56               0.001000      failed (c, OURS)
relation/13033801          503                  172               0.000091      failed (a)
relation/13113580          165                   36               0.000447      failed (b)
```

Minimum edges of 1.18e-4, 4.37e-4, 9.1e-5 m are **below** the 1 mm floor that the payload census
found, and `13113580` has 36 such surfaces while its payload has no gap under a metre. 🔴 **The
sub-millimetre geometry is manufactured between the payload and the IDF — in the extrude/intersect
path our runner drives (`openubem.idf.surfaces.extrude_geometry` plus geomeppy's surface
intersection).** That is why `mingap.csv` could never have caught `13113580`, and it is a second,
independent reason the ≤ 10 mm payload census cannot be the acceptance test.

🔴 **It also means an upstream snap-tolerance change is not guaranteed to touch this failure class at
all.** The offending vertices are not in the payload. `openubem-20` must be told before they spend a
rebuild on it.

#### A replacement discriminator — measured, promising, and NOT adopted

The min-edge census inside the emitted IDF separates the sample cleanly: eight failing buildings at
36–172 surfaces under 10 mm, two completed buildings at zero. But `relation/12628570` **completed**
with five such surfaces and a minimum edge of exactly 1.000 mm, so the boundary is not at zero, and
**three completed buildings is not a control group.** 🔴 It is recorded as a candidate and is not a
rule. The same discipline that rejected the payload census and the varying-zone-count predictor
applies here: it becomes a discriminator when it has been measured against a population, not before.

⚪ One column of `gap_idf.sh` is void and is flagged rather than left standing: its "interzone" count
read the outside-boundary field at token index 5, but EnergyPlus 23.1's `BuildingSurface:Detailed`
carries `Space Name` there. That column printed 0 everywhere and means nothing. Nothing above rests
on it — the ring comparison names its surfaces from the `.err`, not from that field.

#### State at this read, and what changed in the run: nothing

```
2026-09-09 11:37:01   ES 1315013 RUNNING on salus, 1:37:31 wall
775 cells of 11,510    695 COMPLETED_WITH_UNSTABLE_MARKERS / 80 ENERGYPLUS_FAILED
the same eight buildings, ten cells each; IT 1315014 and UK 1315015 PENDING
```

No cell retried, no building dropped, no pin moved, no line of the instrument touched — including
the construction loop of §18.15, which remains a known defect of ours and stays as it is until this
campaign ends. `C2` stays pinned to `T07`. Every file read above was read; none was written.

### 18.17 🔴 THE FALSIFIER FIRED — mechanism (b) SPLITS IN TWO, and §18.16's "the remedy clause is dead" is CORRECTED

Two things arrived at once: `openubem-20` asked whether the §18.16 ring comparison compared
coordinates *exactly*, and the campaign produced two new failing buildings. Both answers change what
§18.16 concluded, and one of them corrects it.

#### 1. The peer's precision question — my comparison DID round, and re-running exact found their gap here too

They reported an August Lyon case (`BATIMENT0000000240879534_part0`) where a matched pair agreed in
vertex count but differed in the **tenth decimal digit** of a coordinate, and asked whether my parse
would have seen it. It would not have. `rings2.sh` compared `round(x, 6)` — a micrometre grid — so a
sub-nanometre divergence was invisible to it. Re-run at full precision (`scratchpad/rings3.sh`:
raw coordinate **strings** as written, exact float multisets, and worst nearest-neighbour distance):

```
relation-12702627   6 pairs  34v34   strings identical   worst nn = 0.0
relation-12713026   4 pairs  25v25   strings identical   worst nn = 0.0
relation-12725306   2 pairs  32v32   strings identical   worst nn = 0.0
relation-12800464   8 pairs  10v10   strings identical   worst nn = 0.0
relation-13113580   2 pairs   9v9    strings DIFFER      worst nn = 9.385703304198744e-10 m
                    base    440426.2522241166   4479120.87184088
                    partner 440426.25222411647  4479120.871840879
```

**20 of 22 pairs are byte-identical as written; 2 are not.** So §18.16's "not one pair differs in
the file" is true of 20 of 22 and false of 2, and the peer's Lyon observation reproduces in Madrid,
in a different corpus, at the same order of magnitude. Their gap is closed in the direction they did
not assume: it exists here.

⚪ **NOT claimed:** that 0.94 nanometres causes the failure. It cannot move a 0.01 m coincidence
test. But it lands on one member of `13113580`'s **1 mm** vertex pair — a near-degenerate triple is
exactly where a collinearity sign can flip on a nanometre — so it is recorded as live, not
dismissed, with the engine's cleanup source still unread.

#### 2. 🔴 The difference-of-two falsifier fired — as a difference of NINE

Since §18.11 the standing instruction has been: *if a difference of two ever appears, record it and
tell `openubem-20`.* `relation/4154505`:

```
** Severe ** ... base surface :BLOCK RELATION/4154505_2 STOREY 1 FLOOR 0001_7
             and outside boundary surface: BLOCK RELATION/4154505_4 STOREY 0 CEILING 0001_1
**  ~~~   ** The vertex sizes are 3 for base surface and 12 for outside boundary surface.
```

**Three against twelve.** Not one, not two — nine. The "always exactly one vertex" regularity that
made the engine-side stripping story look tidy is gone.

#### 3. 🔴 CORRECTION to §18.16 — the two copies are NOT always identical in the file

Ring comparison on the two new buildings (`scratchpad/rings4.sh`):

```
relation-4154554   8 pairs   37 v 37    strings identical, floats identical, worst nn 0.0
                   ... engine still reports 13 vs 12   -> engine-side, as §18.16 found
relation-4154505   base ring n=3   against partner ring n=15
                   four coordinates present in one ring and absent from the other
                   worst nearest-neighbour distance = 7.300123080542104 m
```

**Seven point three metres.** That is not rounding, not snapping and not engine cleanup — the two
faces our build hands EnergyPlus as one interzone pair are **different plates**. The pairs also
cross blocks (`_2 STOREY 1 FLOOR` matched against `_4 STOREY 0 CEILING`), which is what a wrong
adjacency assignment looks like. Note also that the file holds 3 and 15 while the engine reports 3
and 12 — so both effects are present in this building at once: the file already differs, *and*
cleanup strips the partner from 15 to 12.

🔴 **So mechanism (b) is two mechanisms:**

```
(b1) written IDENTICAL, engine diverges after reading   12702627, 12713026, 12725306,
                                                        12800464, 4154554
     (and 13113580, identical to 9.4e-10 m)
(b2) written GENUINELY DIFFERENT                        4154505
```

🔴 **§18.16's Consequence 1 is corrected, not withdrawn.** "Snap the two copies identically, or
re-match after snapping" is dead for **(b1)** — there is nothing there to snap. It is **alive for
(b2)**, where the two copies really are different and re-matching is exactly the right repair. I
told `openubem-20` their mechanism was dead; it is dead for five buildings of seven and correct for
one, and they must be told that before they act on my earlier message. The generalisation was mine,
it was made on a sample of five buildings, and the sample grew.

⚪ Not claimed: which of (b1)/(b2) is the larger class. Seven buildings is not a population.

#### 4. A new symptom, and a zero-length edge

`relation/4154505` also carries three `CheckConvexity: Surface="..." is non-planar` severes — a
symptom not seen in the earlier eight. Its emitted IDF has a **minimum edge length of exactly
0.000000 m** — two consecutive vertices at the same point — with 226 of 529 surfaces under 10 mm.
`relation/4154554`: 290 of 610, minimum edge 0.001000 m. Refreshed census (`gap_idf2.out`)
otherwise unchanged from §18.16, and the discriminator stays a 🔴 **CANDIDATE, NOT A RULE** — the
completed side is still three buildings.

Payload minimum gaps for the two new buildings are **0.005000 m** and **0.001000 m**, both inside
the ≤ 10 mm census — which does not rescue the census, because `13113580` at 1.04 m is still
outside it. The census remains neither necessary nor sufficient. `relation/12837457`
(payload gap 0.006 m) has still **not** failed; the absence check still holds.

#### State at this read, and what changed in the run: nothing

```
2026-09-09 11:45:43   ES 1315013 RUNNING on salus, 1:44:26 wall
800 cells of 11,510    711 COMPLETED_WITH_UNSTABLE_MARKERS / 89 ENERGYPLUS_FAILED
TEN buildings now failing, ten cells each; progress file at 825 lines; IT/UK PENDING
```

No cell retried, no building dropped, no pin moved, no line of the instrument touched — the
construction defect of §18.15 included. `C2` stays pinned to `T07`. Every file above was read; none
was written.

### 18.18 (b2) IS ONE BUILDING OF SEVEN — and a fourth defect found in the emitted file that does NOT explain the failures

`openubem-20` accepted the (b1)/(b2) split and said the part that matters on their side is (b2),
because pairing a floor in one block with a ceiling in another 7.3 m away is a *matching* defect and
not a tolerance question. Two things were measurable here without waiting for their trip: how large
(b2) actually is, and whether the matching is sound anywhere else.

#### 0. The void column of §18.16 is replaced by a correct one

§18.16 flagged a column that read the outside-boundary field at token index 5. Verified empirically
this time by printing the tokens of a real object rather than trusting a field list:

```
[1] Name  [2] Surface Type  [3] Construction  [4] Zone Name  [5] Space Name (EMPTY here)
[6] Outside Boundary Condition   [7] Outside Boundary Condition Object   [8] Sun Exposure ...
```

So index 5 was `Space Name` and genuinely meant nothing, as recorded; **6 and 7** are the fields
that matter, and everything below uses them.

#### 1. (b2) is confined to a single building

Every retained IDF, every surface whose boundary condition is `Surface`, matched against its named
partner (`scratchpad/adj2.sh`):

```
building        interzone   partner missing   count differs   centroids > 0.5 m   max centroid gap
12582232  (ok)         54          0                0                0                0.0000
12582233  (ok)         38          0                0                0                0.0000
12628570  (ok)         62          0                0                0                0.0000
12582234  (a)         139          0                0                0                0.0000
13033801  (a)         226          0                0                0                0.0000
12702627 (b1)         136          0                0                0                0.0000
12713026 (b1)          88          0                0                0                0.0000
12725306 (b1)          98          0                0                0                0.0000
12800464 (b1)         170          0                0                0                0.0000
13113580 (b1)          60          0                0                0                0.0000
4154554  (b1)         368          0                0                0                0.0000
12863111  (c)         141          0                0                0                0.0000
4154505  (b2)         160          0                9                6                3.7584
```

**One building of thirteen carries every count mismatch and every separated pair.** Nothing else on
disk — failing or completed — has a single interzone pair whose two faces are written with different
vertex counts or whose centroids are apart at all. So on the sample that exists, **(b1) is six
buildings and (b2) is one.** 🔴 Still not a population: thirteen buildings, three of them completed.
The claim is about the sample, not the district.

#### 2. 🔴 A fourth defect in the emitted file: many-to-one interzone pairing

The same census turned up a column I did not go looking for — surfaces whose named partner names a
*different* surface back. Listing concrete cases (`scratchpad/adj3.sh`) shows what it is, and it is
not a parser artefact:

```
A: BLOCK RELATION/13113580_1 STOREY 0 CEILING 0001_2   n=3  -> B
B: BLOCK RELATION/13113580_4 STOREY 1 FLOOR 0001_1     n=3  -> BLOCK .../13113580_4 STOREY 0 CEILING 0001_2
   surfaces claiming B as their partner: 2      surfaces claiming A as their partner: 0
```

**Two ceilings declare the same floor as their outside boundary object; the floor can only name one
of them back; the other is left dangling** — an interzone surface pointing at a partner that points
elsewhere. Counts of such orphans:

```
12582234  31 of 139   13033801  24 of 226   12800464  20 of 170   4154505  12 of 160
13113580  10 of  60   12863111   1 of 141
12702627, 12713026, 12725306, 4154554 : 0     12582232, 12582233, 12628570 (completed) : 0
```

#### 3. ⚪ NOT claimed: that this causes anything

Tested directly rather than assumed (`scratchpad/adj4.sh`) — are the orphaned surfaces the ones the
engine complains about?

```
building     orphans   surfaces named in the .err   named AND orphaned   named NOT orphaned
12702627        0                 6                        0                    6
12713026        0                 4                        0                    4
12725306        0                 2                        0                    2
12800464       20                 8                        0                    8
13113580       10                 4                        2                    2
4154505        12                15                        3                   12
4154554         0                 8                        0                    8
```

**Five of fifty-five named surfaces are orphaned, and three buildings fail with no orphans at all.**
The orphaned pairings are largely disjoint from the surfaces EnergyPlus names, so this is 🔴 **a
fourth defect in the file we emit, not a fourth failure mechanism.** It is recorded because a
model whose interzone surfaces do not pair one-to-one has an ill-posed heat balance on the orphan
regardless of whether the run reaches the point of noticing — and because three of the six buildings
carrying it are not (b2) at all.

⚪ Also not attributed: whether the many-to-one pairing is made by our runner or by the upstream
build path it drives (`extrude_geometry` plus geomeppy's surface intersection and matching). Neither
source has been read here. It is in the same stretch of the pipeline as the sub-millimetre edges of
§18.16 — between payload and IDF — and that is as far as the measurement goes.

⚪ It is not offered as a discriminator either: four of the ten failing buildings have zero orphans,
and the completed side is still three buildings.

`relation/4164893`, `4164894` and `4164895` appear in the retained-IDF listing because their cells
were **in flight** at read time, not because they failed. They are excluded from every count above.

#### State at this read, and what changed in the run: nothing

The campaign was not polled again for this section; the state of §18.17 stands (800 cells, ten
failing buildings). No cell retried, no building dropped, no pin moved, no line of the instrument
touched. `C2` stays pinned to `T07`. Every file above was read; none was written.

### 18.19 🔴 THREE NEW FAILING BUILDINGS — our own defect DOUBLES, and §18.18's "(b2) is one building" is CORRECTED twice over

The run moved from 800 to 925 finished cells and added three buildings to the failing set. Each was
diagnosed from its retained `.err` and `.idf` before anything else was said about it. Nothing was
retried, re-run, rebuilt or excluded; every file below was read, none written.

```
2026-09-09 12:01:52   ES 1315013 RUNNING on salus, 1:58:07 wall
925 cells of 11,510    806 COMPLETED_WITH_UNSTABLE_MARKERS / 119 ENERGYPLUS_FAILED
campaign_progress.jsonl 940 lines (status lags by PROGRESS_EVERY = 25)
THIRTEEN failing buildings; IT 1315014 and UK 1315015 PENDING
```

#### 🔴 `relation/4164962` — mechanism (c). THE DEFECT IS OURS, AND IT IS NOW TWO BUILDINGS.

8 warnings, **one** severe, and that severe is ours:

```
** Severe ** GetSurfaceData: Construction EU_ROOF_CONSTRUCTION of interzone surface
  BLOCK RELATION/4164962_3 STOREY 0 ROOF 0001_2 does not have the same materials in the
  reverse order as the construction EU_FLOOR_CONSTRUCTION of adjacent surface
  BLOCK RELATION/4164962_2 STOREY 1 FLOOR 0001_2
**  Fatal ** GetSurfaceData: Errors discovered, program terminates.
vertex size lines: none.   coincident lines: 0.
```

Identical in kind to `relation/12863111` (§18.15): a short block's storey-0 roof is an interior
partition against a taller block's storey-1 floor, and `tools/4thJ_step10_nocore_campaign.py` lines
1038–1045 assign constructions **by `Surface_Type` alone**, never asking whether the surface is
interzone. 🔴 **Mechanism (c) is now 2 of 13 failing buildings, not 1 of 10.** Still NOT FIXED and
still not to be fixed mid-run — the same rule we applied to upstream, applied to ourselves. It
belongs in the next re-pre-registration. 🔴 At the end this building is reported under **our** defect
and is never counted as an upstream geometry loss.

#### `relation/4165178` — mechanism (b1)

8 severes, i.e. 4 interzone pairs each named twice, all inside block `_1` between consecutive
storeys, reporting **9 vs 10** and **10 vs 9**. The exact-precision ring test (`rings5.sh`, raw
coordinate strings, `rings3.sh` method):

```
8 pairs   n=11   strings_identical=True   floats_identical=True   worst_nn_xy=0.0
```

Eleven vertices written, byte-identical in both copies, and the engine reports nine against ten. 🔴
**(b1) is now 7 buildings** — written identical, divergence manufactured inside EnergyPlus's own
coincident/collinear stripping.

#### `relation/4165180` — mechanism (a)

```
** Warning ** GetSurfaceData: There are 39 coincident/collinear vertices; These have been deleted...
** Severe  ** GetSurfaceData: There are 24 degenerate surfaces
** Severe  ** CalcCoordinateTransformation: Invalid dot product,
              surface="BLOCK RELATION/4165180_1 STOREY 0 CEILING 0001_3"
**  Fatal  ** CalcCoordinateTransformation: Program terminates due to preceding condition.
28 warnings / 2 severe
```

The signature of §18.10 exactly. 🔴 **(a) is now 3 buildings.** At this read its grid is incomplete
(4 of 10 cells), so it is counted as a failing building but its grid is not yet closed.

#### 🔴 The tally, split by mechanism

```
(a) coincident deletion -> degenerate -> CalcCoordinateTransformation   3   12582234 13033801 4165180
(b1) two copies written IDENTICAL, engine diverges after reading        7   12702627 12713026 12725306
                                                                            12800464 13113580 4154554 4165178
(b2) two copies written GENUINELY DIFFERENT                             1   4154505
(c) OUR construction assignment                                         2   12863111 4164962
                                                                       ---
                                                                       13
```

⚪ Thirteen buildings with three completed controls is still not a population, and no class is
claimed to be the larger one.

#### 🔴 CORRECTION 1 to §18.18 — "COUNT_DIFFERS is confined to `4154505`" is no longer true

The adjacency census re-run over all retained IDFs (`adj5.out`, 16 files with content) finds the
written-different property in **two** buildings, not one:

```
relation-4154505   interzone 160  asym 12  COUNT_DIFFERS 9  centroid>0.5m 6  max_centroid 3.7584
relation-4164962   interzone  37  asym  1  COUNT_DIFFERS 2  centroid>0.5m 0  max_centroid 0.3027
every other building (including all three completed)   COUNT_DIFFERS 0   max_centroid 0.0000
```

Deduplicated to pairs (`adj7.sh`; the census column counts each direction separately), `4164962`
carries exactly one:

```
COUNT 8 vs 9   centroid 0.3027 m   partner names it back = True
   A: BLOCK RELATION/4164962_2 STOREY 0 CEILING 0001_1
   B: BLOCK RELATION/4164962_2 STOREY 1 FLOOR 0001_1
```

🔴 **And `4164962` does not fail with mechanism (b) at all** — it has no vertex-mismatch severe. So a
plate pair written with two different vertex counts is **not sufficient** to produce the vertex-size
mismatch failure. That is the second property this campaign has had to demote: the sub-10 mm edge
census and now this one are both candidates, neither is a discriminator.

#### 🔴 CORRECTION 2 — (b2) in `4154505` is NOT "one plate written twice, differently"

Deduplicated (`adj8.sh`), the nine direction-counts are six pairs, and they are the same three-block
chain repeated once per storey:

```
COUNT  3 vs 15  centroid 3.7584 m  back_ref=False
   A: BLOCK RELATION/4154505_2 STOREY 1 FLOOR 0001_7      (3 vertices)
   B: BLOCK RELATION/4154505_4 STOREY 0 CEILING 0001_1    (15 vertices)
COUNT 15 vs  3  centroid 3.7584 m  back_ref=True
   A: BLOCK RELATION/4154505_4 STOREY 0 CEILING 0001_1    (15 vertices)
   B: BLOCK RELATION/4154505_5 STOREY 1 FLOOR 0001_1      (3 vertices)
   ... the same two shapes again at storeys 2 and 3, identical 3.7584 m offset
```

Block `_2`'s floor names block `_4`'s ceiling, which does **not** name it back; `_4`'s ceiling names
block `_5`'s floor instead. 🔴 So (b2) here is **the many-to-one pairing defect of §18.18 wearing a
different hat** — three plates in three blocks wrongly chained, not one plate emitted twice with
different rings. The remedy clause stays ALIVE for (b2), but what it points at is the **pairing**,
not the ring: re-matching is the repair, snapping is not.

#### The fourth defect, re-measured on the new buildings — still not the cause

```
building     orphans / interzone     named in .err     named AND orphaned
4165178          24 / 110                  8                    0
4165180          10 /  68                  -                    -   (mechanism (a), no mismatch lines)
4164962           1 /  37                  -                    -   (mechanism (c), no mismatch lines)
```

🔴 `4165178` carries 24 orphaned interzone surfaces and **not one of them is a surface EnergyPlus
named**. The running total is **5 of 63** named surfaces orphaned, across four failing buildings with
zero orphans at all. Unchanged verdict: a real defect in the file we emit, **not** a failure
mechanism and **not** a discriminator; unattributed to either codebase, neither source read.

#### The min-edge census, refreshed — and weaker, not stronger

```
relation/4164962   128 surf    31 under 10mm   min edge 0.000000   <-- second zero-length edge
relation/4165178   278 surf    63 under 10mm   min edge 0.000624
relation/4165180   194 surf    36 under 10mm   min edge 0.000268
completed 12582232 / 12582233 / 12628570        0 / 0 / 5          min 0.034986 / 0.953555 / 0.001000
```

`4164962` reaches an **exactly zero-length edge** — two consecutive vertices at the same point, the
second building to do so after `4154505` — and yet it dies of *our* construction assignment, with no
geometry severe at all. 🔴 That is a direct demonstration that the census cannot be read as a cause.
It remains a CANDIDATE, NOT A RULE, and it has now been weakened by its own next data point.

#### State: nothing changed

No cell retried, no building dropped, no pin moved, no line of the instrument touched — including
both construction-loop buildings. `C2` stays pinned to `T07`. `relation/4165181` and
`relation/4165182` hold IDFs because their cells are IN FLIGHT, not because they failed;
`relation/4165181` had no `.err` at this read. Evidence: `scratchpad/new3.out`, `new4.sh`,
`rings5.out`, `gap_idf3.out`, `adj5.out`, `adj6.sh`, `adj7.sh`, `adj8.sh`; `campaign_status.json` at
12:01:52.

### 18.20 🔴 A BUILDING CARRIES OUR DEFECT **AND** AN UPSTREAM ONE — the end-of-run split needs a MIXED class, or it will overcount our loss

At 12:14:18 EDT the run reached **1,000 cells of 11,510 — 870 `COMPLETED_WITH_UNSTABLE_MARKERS` /
130 `ENERGYPLUS_FAILED`**, `campaign_progress.jsonl` at 1,021 lines, ES `1315013` 2:14:05 wall on
`salus`, IT and UK PENDING. **Fourteen failing buildings**; `relation/4165180` closed its grid at ten
cells, and `relation/4165181` and `relation/4165182` **completed** — confirming they were in flight,
not failing, as §18.19 said. One new building: `relation/4179135`.

#### `relation/4179135` — mechanism (c), OURS, but NOT ours alone

```
12 warnings / 3 severe
** Severe ** GetSurfaceData: Construction EU_ROOF_CONSTRUCTION of interzone surface
   BLOCK RELATION/4179135_9 STOREY 0 ROOF 0001_2 does not have the same materials in the reverse
   order as EU_FLOOR_CONSTRUCTION of BLOCK RELATION/4179135_8 STOREY 1 FLOOR 0001_2
** Severe ** CheckConvexity: Surface="BLOCK RELATION/4179135_8 STOREY 0 CEILING 0001_3" is non-planar.
** Severe ** CheckConvexity: Surface="BLOCK RELATION/4179135_9 STOREY 0 ROOF 0001_2" is non-planar.
**  Fatal ** GetSurfaceData: Errors discovered, program terminates.
```

The construction severe is ours — the same `Surface_Type`-only assignment at
`tools/4thJ_step10_nocore_campaign.py` lines 1038–1045 that produced `12863111` (§18.15) and
`4164962` (§18.19). **But it is not the only fatal-triggering severe in the file.** The two
`CheckConvexity` non-planar severes are geometry, they are not ours, and `GetSurfaceData` terminates
on the accumulated error count. Repairing our construction loop would **not** have saved this
building.

#### 🔴 The reporting consequence, and it is a correction to how §18.15/§18.19 framed (c)

`cmix.sh` separates the severes of all three (c) buildings:

```
building            distinct severes    ours (reverse order)    other severes
12863111                   1                   yes              none        -> PURE (c)
4164962                    1                   yes              none        -> PURE (c)
4179135                    3                   yes              2x CheckConvexity non-planar  -> MIXED
```

🔴 **At the end, "failing buildings split by mechanism" must carry a MIXED class.** Counting
`4179135` under our defect would claim a building our fix would have rescued when it would not have;
counting it as upstream would hide our defect in it. Both are wrong. The rule is: **a building is
charged to our defect only when our severe is the ONLY severe in its `.err`.** On the sample so far
that is **two** buildings (`12863111`, `4164962`), with `4179135` reported as mixed. ⚪ Note the same
mixing exists inside the upstream classes — `4154505` carries three `CheckConvexity` non-planar
severes alongside its vertex mismatches — but there both severes are upstream, so no attribution line
is crossed.

#### Censuses refreshed — nothing moved

```
relation/4179135   197 surf   47 under 10mm   min edge 0.000272
                   interzone 63   asym 3   COUNT_DIFFERS 0   max_centroid 0.0000
```

The written-different property therefore stays at **2 of 17** measured IDFs (`4154505`, `4164962`) —
§18.19's correction holds and does not grow. The orphan defect gains a small seventh case (3 orphans of 63 interzone surfaces).
The three completed controls are unchanged at 0 / 0 / 5 surfaces under 10 mm and `asym 0`.

#### 🔴 The tally

```
(a)  coincident -> degenerate -> CalcCoordinateTransformation   3   12582234 13033801 4165180
(b1) two copies written IDENTICAL, engine diverges              7   12702627 12713026 12725306 12800464
                                                                    13113580 4154554 4165178
(b2) pairing tangle (see §18.19)                                1   4154505
(c)  OUR construction assignment, ALONE                         2   12863111 4164962
     OUR construction assignment + upstream geometry (MIXED)    1   4179135
                                                               ---
                                                               14
```

⚪ Fourteen buildings against three retained completed controls (`4165181`/`4165182` completed, so their IDFs were deleted on the success path and they are not controls) is still not a population; no class is claimed
to be the larger one. Nothing was retried, dropped, moved or patched — including the construction
loop. `C2` stays pinned to `T07`. Evidence: `scratchpad/new5.sh`, `cmix.sh`, `gap_idf.sh`,
`adj2.sh`; `campaign_status.json` at 12:14:18.


### 18.21 🔴 THE PURE/MIXED RULE APPLIED TO ALL FOURTEEN — (b1) is the ONLY class whose cause is established on every member

§18.20 introduced the rule on the one building that forced it. `openubem-20` adopted it and then
applied it back against their own side, observing that `4154505` — the single building (b2) rests on
— carries non-planar severes too, so its cause is not established either. That is their inference
from my rule, so it was **re-measured here rather than carried**: `sevmix.sh` classifies every severe
in every failing building's `.err` and reports the distinct kinds.

```
building            severes   kinds
12582234               2      GetSurfaceData:degenerate x1   CalcCoordinateTransformation:dot-product x1
13033801               2      GetSurfaceData:degenerate x1   CalcCoordinateTransformation:dot-product x1
4165180                2      GetSurfaceData:degenerate x1   CalcCoordinateTransformation:dot-product x1
12702627               6      VertexSizeMismatch x6
12713026               4      VertexSizeMismatch x4
12725306               2      VertexSizeMismatch x2
12800464               8      VertexSizeMismatch x8
13113580               2      VertexSizeMismatch x2
4154554                8      VertexSizeMismatch x8
4165178                8      VertexSizeMismatch x8
4154505               18      VertexSizeMismatch x15   CheckConvexity:non-planar x3
12863111               1      GetSurfaceData:OUR-construction x1
4164962                1      GetSurfaceData:OUR-construction x1
4179135                3      CheckConvexity:non-planar x2   GetSurfaceData:OUR-construction x1
```

#### 🔴 The rule needs one sharpening, and the measurement is what sharpens it

Stated as "the only severe in the file", the rule would make all three mechanism-(a) buildings mixed
— they each carry two severes. But those two are **one causal chain**, documented in §18.10:
coincident deletion produces degenerate surfaces, and the degenerate surface is what makes
`CalcCoordinateTransformation` fail on its dot product. Two severe *kinds*, one mechanism, one owner.

So the rule is about **attribution across owners**, not severe multiplicity:

- **a building is charged to our defect only when no severe other than ours appears in its `.err`;**
- within a single owner, several severe kinds do not cross an attribution line — but they do mean a
  *within-owner mechanism* claim is not established for that building.

#### 🔴 What the measurement then says, class by class

```
(a)  3   12582234 13033801 4165180   two severe kinds, ONE documented chain, upstream   cause established
(b1) 7   12702627 12713026 12725306 12800464 13113580 4154554 4165178
                                     VERTEX MISMATCH AND NOTHING ELSE                   cause established
(b2) 1   4154505                     15 mismatches + 3 non-planar, both upstream        NOT established
(c)  2   12863111 4164962            our severe, alone, nothing else                    cause established
     1   4179135                     our severe + 2 non-planar, TWO OWNERS              MIXED, not established
```

🔴 **`openubem-20`'s inference against themselves is confirmed here, independently:** `4154505` is the
only building (b2) has, and it carries three `CheckConvexity ... is non-planar` severes alongside its
fifteen vertex mismatches. **"The mis-paired plates are why this building died" is NOT established**
and is not claimed in this record either. The pairing tangle of §18.19 remains a real defect in the
emitted file; it is no longer offered with a fatality claim attached.

🔴 **And the same measurement strengthens (b1), which was not the point of running it:** all seven
(b1) buildings carry **vertex-size-mismatch severes and no other kind at all** — 6, 4, 2, 8, 2, 8 and
8 of them respectively, zero non-planar, zero degenerate, zero construction. (b1) is therefore the
**only** class in this campaign whose stated cause is established on **every** member. ⚪ Still not
claimed: that (b1) is the larger class in Madrid, or that seven buildings against three retained
completed controls is a population.

#### Unchanged

Nothing retried, dropped, moved or patched; `C2` stays pinned to `T07`; the construction loop is
still ours, still unfixed, still deferred to the next re-pre-registration. Evidence:
`scratchpad/sevmix.sh`; §18.20 for the rule this refines.


### 18.22 🔴 AN EIGHTH (b1) BUILDING — and inside (b1) the vertex difference is EXACTLY ONE, every pair, no exceptions

```
2026-09-09 12:31:28   ES 1315013 RUNNING on salus, 2:28:41 wall
1,050 cells of 11,510   900 COMPLETED_WITH_UNSTABLE_MARKERS / 150 ENERGYPLUS_FAILED
campaign_progress.jsonl 1,064 lines      FIFTEEN failing buildings      IT/UK PENDING
```

`relation/4466638` is new and it is **(b1), pure**. `sevmix.sh`: 4 severes, **all
`VertexSizeMismatch`, no other kind** — no non-planar, no degenerate, no construction, so under the
across-owners rule of §18.20/§18.21 its cause is established. `rings6.sh` (raw coordinate strings):

```
4 pairs   n=34   strings_identical=True   floats_identical=True   worst_nn_xy=0.0
engine reports 15 vs 16 and 16 vs 15
486 surfaces, 189 under 10 mm, min edge 0.001000; interzone 238, asym 0, COUNT_DIFFERS 0
```

Thirty-four vertices written byte-identical in both copies, and the engine reads fifteen against
sixteen. **(b1) is now 8 buildings.** The written-different property stays at 2 of 18 measured IDFs
and the orphan count for this building is zero.

#### 🔴 The regularity this exposes, which was worth running for its own sake

`vsz.sh` collects every distinct `The vertex sizes are X ... and Y` pair across all nine mechanism-(b)
buildings:

```
12702627   22v23  23v22
12713026    8v9    9v8
12725306   14v15  15v14
12800464    8v9    9v8
13113580    7v8
4154554    12v13  13v12
4165178     9v10  10v9
4466638    15v16  16v15
------------------------------------------------- (b1), eight buildings: DIFFERENCE IS ALWAYS ONE
4154505    11v12  12v11   AND   12v3  3v12         <-- the only exception in the campaign
```

🔴 **Inside (b1) the difference is exactly one, in every pair of every building, with no
exceptions.** That is what "the engine strips one extra vertex from one of two identical copies"
predicts, and it is now observed on eight buildings rather than asserted from five.

🔴 **The difference-of-two falsifier fired exactly once, and it fired in the one building whose cause
is not established.** `4154505` carries both patterns at once — ordinary `11v12` pairs *and* the
`12v3` pair — and it is the building that also carries the three-block pairing tangle (§18.19) and
three `CheckConvexity` non-planar severes (§18.21). So the exception is not an exception *to (b1)*;
it belongs to the building that was already excluded from (b1) on independent evidence. ⚪ NOT
claimed: that the exception is *caused* by the pairing tangle or by the non-planarity. Three
defects co-locate in one building; nothing here orders them.

⚪ Also not claimed: that a difference of exactly one is *sufficient* for (b1) membership, or that it
will hold on the ninth building. It is a regularity on the sample, stated as one, and it has a
falsifier that has already fired once and can fire again.

#### Unchanged

Nothing retried, dropped, moved or patched; `C2` stays pinned to `T07`. Tally: **(a) 3, (b1) 8,
(b2) 1, (c) 2 pure + 1 mixed = 15.** Evidence: `scratchpad/sevmix.sh`, `rings6.sh`, `vsz.sh`,
`b8.sh`, `gap_idf.sh`, `adj2.sh`; `campaign_status.json` at 12:31:28.


### 18.23 🔴 THE MISMATCH ARITHMETIC IS ACCOUNTED FOR — the engine's read count is `written − (edges under 10 mm)`, in every pair of all eight (b1) buildings

```
2026-09-09 12:39:16   ES 1315013 RUNNING on salus
1,100 cells of 11,510   950 COMPLETED_WITH_UNSTABLE_MARKERS / 150 ENERGYPLUS_FAILED
campaign_progress.jsonl 1,101 lines     FIFTEEN failing buildings, unchanged     IT/UK PENDING
```

No new failing building this read: fifty more cells finished and all fifty completed. What follows
is not a new building, it is a measurement on the eight already in (b1).

§18.22 recorded that the two engine-read vertex counts always differ by exactly one. It did **not**
say where either number comes from. `vred.sh` / `vred2.sh` take each surface named in a
`Vertex size mismatch` severe, pull **that ring** out of the IDF the engine refused, and compare the
written vertex count against the two counts the engine reports — alongside the number of edges in
that same ring shorter than 10 mm.

```
building     written  edges<10mm  written-k  engine reports   identity
12702627       34         11          23       23 / 22          MATCH
12713026       25         17           8        8 /  9          MATCH
12725306       32         18          14       14 / 15          MATCH
12800464       10          1           9        9 /  8          MATCH
13113580        9          1           8        8 /  7          MATCH
4154554        37         25          12       12 / 13          MATCH
4165178        11          1          10       10 /  9          MATCH
4466638        34         19          15       15 / 16          MATCH
------------------------------------------------------------------------------
4154505        15          3          12       12 / 11          MATCH   (its ordinary pairs)
4154505         3          1           2        3 / 12       NO-MATCH   (the 12v3 pair)
```

🔴 **In every one of the eight (b1) buildings, one of the two engine counts is exactly the written
count minus the number of sub-10 mm edges in that ring, and the other is that value plus or minus
one.** Eight of eight, every named pair, no exceptions.

So the severe is no longer only described, it is **accounted for**. The engine is collapsing the
short edges — many of them, not one: `4154554` writes 37 vertices and the engine reads 12 and 13,
because 25 of its 37 edges are under 10 mm. §18.22's "the engine strips one extra vertex" was right
about the *difference* and wrong about the *scale*: what happens is a wholesale collapse that both
copies undergo, and the two copies land one apart.

#### What this does NOT establish

⚪ **The tolerance is not pinned.** Within these rings the largest edge below 10 mm is 0.005099 m and
the smallest at or above it is 0.026926 m, so any threshold between roughly 5 mm and 27 mm gives the
same identity. The 10 mm figure was chosen in an earlier window for unrelated reasons and was not
tuned to this test; that is why the identity is evidence and not a fit. But it does not measure the
engine's tolerance.

⚪ **Why one copy keeps one more short edge than the other is still unknown.** The two rings are
written byte-identical (§18.22), so the asymmetry is produced during the read, not in the file.
Nothing here identifies which edge survives or why.

⚪ **Short edges do not predict failure.** `12628570` COMPLETED carrying 5 surfaces with an edge
under 10 mm. The identity explains the arithmetic of a mismatch once one occurs; it is not a
discriminator, and §18.10's demotion of the min-edge census stands.

#### What it does resolve, and it is the falsifier

🔴 **The `12v3` exception is now explained, and explained as a different defect.** `4154505`'s
ordinary pairs obey the identity like every (b1) building does. Its `12v3` pair does not, and cannot:
the base ring is written with **three** vertices and one sub-10 mm edge, which predicts two, while the
engine reports 3 against 12. A three-vertex plate is not a collapsed sixteen-vertex plate. That pair
is the many-to-one pairing tangle of §18.19 — a 3-vertex plate matched to a 15-vertex plate in
another block — surfacing in the same error text. So the campaign's single counterexample to §18.22
is not a counterexample to the collapse mechanism at all; it is the second defect in that building
wearing the first one's error message. ⚪ Still NOT claimed that either defect causes the other.

#### 🔴 CORRECTION OWED TO THE PEER

`openubem-20` wrote, this round, that "(b1) now has the strongest cause and the weakest hold on us,
because two rings written byte-identical cannot be an upstream emission defect", and used it to keep
the partner-names-it-back check first. The first half is right; **the conclusion does not follow.**
(b1) is not a difference *between the two copies* — but it is driven entirely by the short edges
inside the ring, and §18.10 established that those short edges are **manufactured between payload and
IDF** (`13113580`'s payload ring is 7 vertices with a minimum gap of 1.040812 m; its IDF ring is 9
vertices with a 0.000447 m edge, and that one edge is exactly the `k=1` that produces its 7-versus-8).
So (b1) has a strong hold on whatever code creates the short edges. ⚪ That code has still not been
read on either side, so this is **not** an attribution to their emitter or to our runner — it names
the question, not the owner. Their measurement order may still be right; the reason they gave for it
is not.

#### Unchanged

Nothing retried, dropped, moved or patched; `C2` stays pinned to `T07`. Tally unchanged: **(a) 3,
(b1) 8, (b2) 1, (c) 2 pure + 1 mixed = 15 of 1,100 cells.** Evidence: `scratchpad/vred.sh`,
`vred2.sh`; `campaign_status.json` at 12:39:16.


### 18.24 🔴 (b1) SPLITS BY THE ORIGIN OF ITS SHORT EDGES — five buildings whose short edges sit EXACTLY on a 1 mm grid, three that sit below any grid

`openubem-20` sent one piece of director-side arithmetic: their two snap floors are 1 mm and 5 mm,
`13113580`'s 0.447 mm edge is below both, therefore "whatever produces that edge acts after or
outside the snap, and a coarser grid on its own would not remove it." Per the standing rule a peer
measurement is evidence and is re-measured before it is carried. Re-measured here — against my own
data rather than their tree, which I have neither read nor been authorised to read — **the
conclusion is right for three of the eight (b1) buildings and wrong for the other five.**

`vgrid.sh` takes the first ring named in each building's mismatch severes, lists every edge under
10 mm, and asks whether each edge's three coordinate deltas are exact multiples of 1 mm (to 1e-6 of
a grid step):

```
building     short edges   deltas on 1 mm grid   shortest edge, as deltas
12702627         11              11 of 11        +0.000000  -0.001000  +0.000000
12713026         17              17 of 17        +0.000000  -0.001000  +0.000000
12725306         18              18 of 18        +0.000000  +0.001000  +0.000000
4154554          25              25 of 25        +0.000000  -0.001000  +0.000000
4466638          19              19 of 19        +0.000000  -0.001000  +0.000000
----------------------------------------------------------------------------------
12800464          1               0 of 1         -0.000418  -0.000130  +0.000000
13113580          1               0 of 1         -0.000436  +0.000101  +0.000000
4165178           1               0 of 1         -0.000583  -0.000222  +0.000000
----------------------------------------------------------------------------------
4154505           1               0 of 1         +0.000227  +0.000285  +0.000000   (tangle ring)
```

🔴 **In five of the eight, EVERY short edge in the failing ring is an exact 1 mm grid step, and the
shortest ones are single axis-aligned 1 mm moves.** That is precisely what a 1 mm snap floor emits.
None of them lie on a 5 mm grid. 🔴 **In the other three, no short edge lies on any grid** — the
deltas are arbitrary sub-millimetre numbers — and each of those three rings carries exactly **one**
short edge, against eleven to twenty-five in the grid group.

So (b1) splits cleanly in two by the origin of its short edges, while the arithmetic identity of
§18.23 holds identically across both halves. ⚪ This is a split **within** (b1), not a new mechanism
and not a new class: the counts are produced the same way in all eight.

#### What follows and what does not

⚪ **Exact 1 mm quantisation is consistent with a 1 mm snap having produced these edges; it does not
identify which code snapped.** Neither extrude/intersect path has been read on either side. The
finding names the question more sharply, it still does not name the owner.

⚪ **It is NOT claimed that a coarser grid would make these five buildings run.** It would remove
those edges — that much follows from their being exact grid steps — but whether the cells then
complete has not been measured, and will not be measured while `C2` is running.

🔴 **The peer's clause is therefore half right and must not be carried whole.** "A coarser grid on
its own would not remove it" holds for `12800464`, `13113580` and `4165178`, whose short edges sit
below any grid; it does not hold for `12702627`, `12713026`, `12725306`, `4154554` and `4466638`,
whose short edges *are* the grid. The corresponding half of the older "raise the snap grid above
10 mm" remedy is revived for those five as a **question**, not as a remedy — it was buried at §18.10
on the strength of `13113580`, and `13113580` turns out to be in the minority half.

⚪ Their snap-floor line numbers (`european_nocore.py:131,616,620`, `surfaces.py:702`) are recorded
as their measurement and are NOT carried as verified — that is their tree, unread here.

#### Unchanged

Nothing retried, dropped, moved or patched; `C2` stays pinned to `T07`. Tally unchanged: **(a) 3,
(b1) 8, (b2) 1, (c) 2 pure + 1 mixed = 15.** Evidence: `scratchpad/vgrid.sh`; §18.23 for the
identity that holds across both halves.

### 18.25 🔴 A SIXTEENTH BUILDING APPEARS — `way-1237260791`, read at 1,325 cells, pure vertex-size-mismatch signature, NOT folded into (b1)

Poll at 13:17 EDT (1,325 of 11,510 cells finished, up from 1,225): `ENERGYPLUS_FAILED` moved 150 →
160, exactly one building's worth. `cells_failed/` now lists sixteen distinct building slugs — the
same fifteen of §18.10–§18.24 plus one new one, `way-1237260791`. Read-only (`new5.sh`/`sevmix.sh`
equivalent, dispatched to a fresh agent, no file on the cluster touched): `eplusout.err` for
`es__way-1237260791__caseA__f000` (confirmed on disk; sibling dirs exist for caseB and f000/f015/
f030/f050/f100 — this building's `f` grid is NOT f000/f005/f010/f015/f020 as assumed when the check
was dispatched, corrected on read rather than guessed).

**12 Severe + 1 Fatal, 3 Warning** ("Sizing Error Summary: 3 Warning; 12 Severe Errors"). Every
severe is the same shape — `Vertex size mismatch` between a `STOREY n CEILING` surface and the
`STOREY n+1 FLOOR` surface it shares as outside-boundary partner, sizes alternating 5 vs 4, for
n = 0..6 on element `_3` of the building:

```
** Severe ** RoofCeiling:Detailed="BLOCK WAY/1237260791_3 STOREY 0 CEILING 0001_1", Vertex size
   mismatch between base surface :BLOCK WAY/1237260791_3 STOREY 0 CEILING 0001_1 and outside
   boundary surface: BLOCK WAY/1237260791_3 STOREY 1 FLOOR 0001_2
   ~~~ The vertex sizes are 5 for base surface and 4 for outside boundary surface.
[... same pattern repeated for each STOREY 1/2, 2/3, 3/4, 4/5, 5/6 CEILING/FLOOR pair ...]
**  Fatal  ** GetSurfaceData: Errors discovered, program terminates.
```

`cells_failed/es__way-1237260791__caseA__f000.json`: `completion_status: "ENERGYPLUS_FAILED"`,
`returncode: 1`, `zone_count_emitted: 42`, `n_u: 1` — no error text beyond the returncode, the same
missing-manifest defect as defect 4 of RESUME.md §5.

**What this establishes.** The severe set is PURE vertex-size-mismatch: zero coincident/collinear
deletion, zero degenerate surface, zero `CalcCoordinateTransformation` dot-product, zero
`CheckConvexity` non-planar, zero interzone-construction line. That is the same *signature shape*
that defines (b1) across all eight of its members (§18.21's pure/mixed sweep). By signature shape
alone this building looks like a candidate ninth (b1) member.

**What this does NOT establish, and is not claimed.** Signature shape is not the arithmetic. §18.23's
identity (`written − k = one engine-read count, the other one away`) and §18.24's grid/below-grid
split have NOT been checked against this building's own rings — `rings2.sh`, `vsz.sh`, `vred2.sh`,
`vgrid.sh` have not been run on it. It is recorded here as `(?)` in RESUME.md §2, not as a ninth
(b1) building, until that arithmetic is actually measured. Nothing retried, dropped, moved, patched
or scored — `C2` stays pinned to `T07`; this is a read, not a fix.

Also unexplained, still not chased: `campaign_progress.jsonl` (1,340 lines at last check) keeps
running 5-10 lines ahead of `cells_finished` in `campaign_status.json` — first noticed at 1,225/1,232,
holding at similar magnitude since. Flagged only.

Evidence: `cells_failed/es__way-1237260791__caseA__f000.json`; `eplusout.err` for the same cell,
read 13:1x EDT 2026-09-09; `campaign_status.json` at 13:17 EDT (cells_finished 1,325); `RESUME.md`
§1–§2, this addendum.

### 18.26 `way-1237260791` — full ring diagnostic run, result: NOT a ninth (b1) building, same symptom, different mechanism

Following §18.25's read-only flag (signature matched (b1) but arithmetic not checked), a fresh
read-only agent ran the full established methodology (§18.23's `rings2`/`vred2` identity, §18.24's
`vgrid`, and the `13113580`-precedent payload/IDF gap comparison) against this building's 6
surface pairs. Files used, nothing modified: the built IDF
(`.../es__way-1237260791__caseA__f000.idf`) and the source payload, streamed directly out of
`stage/stage_layouts.tar.gz` member `openubem/outputs/3D/eu_ES-MAD-BERRUGUETE_data/layouts/way/
1237260791.json` (never extracted to disk).

**rings2 — written counts.** All 6 pairs write 6 vertices on both the ceiling and floor side,
identically at every storey interface (n = 0..5) — the floor plan repeats verbatim (payload
`floors[0]` vs `floors[1]` zone lists are byte-identical).

**vred2 — written − k identity** (k = ring edges under 10 mm, including the wraparound edge):

```
pair(n)  side          written  k  written-k  engine reports  identity
0        base(Ceil)       6     1     5         {5,4}         = 5 exactly, 4 is one away
0        partner(Floor)   6     1     5         {5,4}         = 5 exactly, 4 is one away
1..5     (both sides, repeats identically)
```

Every ring independently computes written−k = 5. The engine's pair-level readings are {5,4} for
all six pairs, same as (b1). **But** in every established (b1) member the two rings of a pair
carry DIFFERENT written/k values, so each ring's own arithmetic explains its OWN reported number
(one ring's written−k lands on 5, the other's independently lands on 4). Here both rings are
identical (6 written, k=1, written−k=5) — so whichever ring the engine reports as "4" is NOT
explained by that ring's own edge count. The identity holds at the pair level (both numbers ∈
{5,4}, off by at most 1) but not at the per-ring level the way it does for the eight established
members.

**vgrid — the one short edge per ring:**

```
pair(n)  side           short edges  on 1mm grid  dist(m)       dx(m)         dy(m)         dz(m)
0        base(Ceil)         1           False     0.000142802  +0.000121594  -0.000074882   0.0
0        partner(Floor)     1           False     0.000142802  -0.000121594  +0.000074882   0.0
1..5     (both sides, same magnitude and signs, repeats identically)
```

Neither dx nor dy is a 1 mm multiple (0.1216 mm / 0.0749 mm) — sub-millimetre, arbitrary, no grid
signature. Magnitude class matches the three below-grid (b1) members (`12800464` `13113580`
`4165178`), not the five on-grid ones.

**gap_idf / adjacency — the payload trace, mirroring the `13113580` precedent.** The owning zone's
own polygon (`.../F0_dwelling_3`, `.../F1_dwelling_3` — zone names verified directly against the
IDF's Zone Name field) is clean: **6 vertices, 2.4697437 m minimum edge gap**, nothing tight,
nothing plausibly snapped into a sub-mm edge. Tracing the IDF ring's 6 written vertices individually
against the payload instead shows the ring is **not that zone's own polygon**: 4 of its 6 vertices
match — to double precision — the *entire* 4-vertex footprint of the **adjacent** zone
(`dwelling_1`), and the other 2 are a near-duplicate split of a single point that IS in
`dwelling_3`'s own footprint (`(440494.55232069106, 4478857.409496305)` — one copy matches to
~1e-10 m, the other offset by ~0.1216 mm in x, ~0.0749 mm in y: exactly the manufactured short
edge). Verified by full coordinate trace for pair n=0; zone-ownership pattern confirmed to repeat
for n=3, and the numeric identity (edge counts, short-edge magnitude) is identical across all six
pairs by construction (repeated floor plan), not re-derived pair by pair.

**What this establishes.** The written IDF ring for this building's element `_3` interfaces is a
splice across two different zones' vertex sets (adjacent zone's whole footprint + one duplicated
corner of the owning zone), not a snap/regularization of the owning zone's own ring. Every
established (b1) member's short edge sits inside the OWNING zone's own ring (payload has a tight
gap or an identical ring that gets a manufactured sub-mm edge on the IDF side); this building's
does not — the owning zone's payload polygon has no tight gap anywhere. That is a different
generator defect (wrong-zone vertex sourcing during ring construction) producing the same error
text (`Vertex size mismatch`, same 5-vs-4 shape) as (b1)'s snap-tolerance mechanism.

**Conclusion: `way-1237260791` is NOT a ninth (b1) building.** It matches (b1) at the signature
level only (pure vertex-size-mismatch, sub-mm below-grid short edge). The two things §18.25 flagged
as unchecked — the per-ring arithmetic and the payload/IDF gap trace — both come back showing a
different underlying mechanism. Recorded in `RESUME.md` §2 as `(?)`, n = 1 — one building does not
make a class, and this is not asserted as a new named mechanism, only as demonstrably NOT (b1).
Nothing retried, dropped, moved, patched or scored; `C2` stays pinned to `T07`.

Evidence: fresh read-only agent's raw output (IDF path and payload tar member above); `RESUME.md`
§2, edited in place; §18.23 (written−k identity, 8/8 established members); §18.24 (grid/below-grid
split); §18.25 (the signature-only read this addendum resolves).

### 18.27 🔴 `way-1237260791` ROOT-CAUSED — a fourth mechanism, owned by OpenUBEM/geomeppy, NOT our runner; blast radius is real; NOT fixed under the author's delegated fix-authority rule

A dispatched read-only investigation (agent `ac01a5d4a6f30f351`, ~21 minutes, 86 tool uses) was
asked to root-cause §18.26's finding and bound its blast radius, strictly read-only throughout.
It confirmed the runner actually deployed for `C2` (local copy md5 matches the Speed copy
byte-for-byte) and confirmed the OpenUBEM checkout's `openubem/idf/surfaces.py` (local checkout at
`C:\Users\o_iseri\Desktop\OpenUBEM`) is byte-identical to the Speed-deployed copy. It then fetched
the real payload used by the running job (`stage_layouts.tar.gz` member
`.../ES-MAD-BERRUGUETE_data/layouts/way/1237260791.json`) and the real built IDF, and **reproduced
the exact defect locally**: fed the real `dwelling_1`/`dwelling_3` payload vertices through the
installed `geomeppy` library's own `intersect()`/`is_hole()` functions and got fragments matching
the real IDF's written fragments vertex-for-vertex (to floating-point rounding). Nothing was
written to any project file, Speed path, or the SLURM queue.

**Root cause.** Not in `zones_for_cell`/`build_idf_for_cell` in our runner
(`4thJ_step10_nocore_campaign.py:956-1027`) — those read each zone's own payload polygon unmodified
and call `extrude_geometry(idf, zones, [])` once (line 1027); `dwelling_3`'s payload ring (6
vertices, 2.4697437 m min gap) is confirmed untouched by our code. The splice is inside
**`openubem/idf/surfaces.py`'s `extrude_geometry()`**, specifically its single, whole-building call
`idf.intersect_match()` at **`surfaces.py:927`**, which delegates to third-party **geomeppy**:

- `geomeppy/idf.py:48-57` -> `intersect()` -> `geomeppy/geom/intersect_match.py:18-39`
  (`intersect_idf_surfaces`)
- `geomeppy/geom/surfaces.py:135-148` (`get_adjacencies`) runs an **unscoped, all-pairs
  `combinations(surfaces, 2)` sweep (line 144) over every surface in the entire building** — not
  limited to genuinely adjacent zones.
- `geomeppy/geom/surfaces.py:169-201` (`populate_adjacencies`): for any two coplanar surfaces (same
  distance-from-origin and same/opposite normal, `surfaces.py:180-184`), it computes
  `poly1.intersect(poly2)` (`surfaces.py:186`).

`dwelling_1` (4 verts) and `dwelling_3` (6 verts) are side-by-side, same-floor zones sharing exactly
one vertex — a point-touch, not a shared wall edge. Both storey-0 ceilings sit at `z=3`, both facing
`+z` (same normal, not opposite). Directly confirmed via geomeppy's own `is_hole()` (constructed
both real `Polygon3D`s and called it both directions) that this is **not** a hole/courtyard case
(`is_hole` returns `False` both ways) — but `poly1.intersect(poly2)` still returns a **non-empty,
degenerate sliver triangle** at the touch point (edge length `0.142802 mm`, exactly the manufactured
short edge already measured at §18.26). **Bug (A):** geomeppy's polygon intersection returns a
spurious non-zero-area result for two polygons that only touch at a point.

Because `is_hole()` is `False`, `geomeppy/geom/polygons.py:625-644` (`intersect`) falls into its
`else` branch and additionally computes `poly1.difference(poly2)` and `poly2.difference(poly1)`.
Back in `populate_adjacencies` (`surfaces.py:189-198`), the resulting fragments are routed to
`new_s1` vs `new_s2` **purely by matching normal vector** — but `dwelling_1`'s and `dwelling_3`'s
ceilings have the **identical** normal, so this routing cannot tell the fragments apart: **every
fragment (including `dwelling_1`'s own full-footprint "difference" piece) gets attached to both
zones' fragment lists.** **Bug (B).**

`intersect_idf_surfaces` (`geomeppy/geom/intersect_match.py:31-39`) then **replaces** each original
surface with these fragments, named `<name>_1`, `<name>_2`, ... Exactly what the built IDF shows:
`dwelling_3`'s storey-0 ceiling was replaced by three fragments — `Ceiling 0001_1` =
`dwelling_1`'s whole rectangle + the split touch-point, `Ceiling 0001_2` = the bare sliver
triangle, `Ceiling 0001_3` = `dwelling_3`'s own true remainder — and the mirror contamination is
visible on `dwelling_1`'s own side too: its `Storey 0 Ceiling 0001_2` is `dwelling_3`'s entire true
hexagon, correctly (self-consistently) paired with `dwelling_3`'s own `Storey 1 Floor 0001_3`. Local
reproduction against the real coordinates returns four fragments matching these IDF fragments
exactly.

Two existing OpenUBEM safety nets do **not** catch this: `_repair_mismatched_horizontal_pairs`
(`surfaces.py:493-544`) only inspects same-type pairs — a legitimate ceiling/floor interfloor pair
is explicitly exempted by design — and `find_mismatched_interzone_pairs` (`surfaces.py:547-571`)
only flags a **vertex-count** mismatch; both written copies here have 6 vertices, so no count-based
check fires. `_snap_shared_interzone_vertices` ("FINDING 221") was checked and **ruled out**: it
filters zones by a `"mode"` key our runner never sets on any zone dict (confirmed by a full-file
grep — the only `"mode"` occurrences in the runner are unrelated `mode: 'campaign'` authorization
fields at lines 238/269/279), so it is a no-op for every `C2` zone.

**Same bug as (c)? Definitively no.** The recorded class-(c) defect at
`4thJ_step10_nocore_campaign.py:1038-1045` is a post-hoc `Construction_Name` assignment loop keyed
only on `Surface_Type`, giving the two faces of one interzone plate non-reversed materials — a
**materials** problem with zero geometric effect, producing "does not have the same materials in
the reverse order", living entirely in **our own runner**. `way-1237260791`'s defect is a
**vertex/geometry** corruption inside `openubem/idf/surfaces.py`'s `extrude_geometry()` -> geomeppy's
`intersect_match()`, entirely upstream of and untouched by our runner, producing "Vertex size
mismatch" — the same text family as (b1)/(b2) but a mechanism distinct from both: unlike (b1)
(§18.23-18.24: rings written **identically** on both copies, divergence introduced by EnergyPlus's
own read), the two written copies here are **not** identical (one genuinely contains another zone's
vertices). Unlike (b2) (§18.17-18.18: a whole surface paired to the **wrong partner object**), the
partner pairing here is **correct** (ceiling and floor of the same block, same storey interface) —
only the vertex **content** is contaminated. A fourth, distinct mechanism, named `(d)`.

**Blast radius.** Real, and larger than one building. Within `way-1237260791` alone, the same
mechanism fires at least twice: `dwelling_1`<->`dwelling_3` (the one that tripped the fatal) **and**
`dwelling_1`<->`dwelling_2` (visible in `dwelling_1`'s own `Storey 0 Ceiling 0001_3`/`0001_4`
fragments, paired against `dwelling_2`'s floor fragments). The general trigger condition — two
same-floor zones whose payload polygons touch at exactly one shared vertex and no shared edge, both
horizontal, same-facing normal — is generic to `nocore_equal_area`/`room_layout` partitions with
≥3 dwellings meeting around one interior corner, not specific to this OSM building. Critically,
**most instances of this defect will not trip a fatal at all** — a fatal only happens when the
manufactured sliver's near-duplicate vertex pair straddles EnergyPlus's own internal
coincident-vertex collapse threshold asymmetrically between the two written copies (the same
coincidence that governs (b1)). Where the split lands cleanly on both copies, **the wrong-zone
surface is written, paired, and simulated to "completion" with no visible symptom** — a zone
silently gains (or the wrong zone silently gets attributed) a horizontal surface, and hence
area/adjacency/conduction, that does not belong to it. Neither safety net above would catch this.
A read-only data check to bound this later, without building any IDF or running EnergyPlus: for
every building's payload, per floor, for every pair of zones, compute the shared-vertex set between
their `coords_m` rings; flag any pair sharing **exactly one** point with **no** edge of either zone
collinear through that point with an edge of the other (mirroring geomeppy's own `is_hole` test).
O(zones squared) per floor, needs no engine run. Proposed, not yet run.

**Decision, applying the author's delegated fix-authority rule (RESUME.md last+58s) to this first
real case: NOT fixed.** The criterion — important AND impacting a large amount of data — is
plausibly cleared by the evidence above. But this lives two levels outside our own tree (OpenUBEM's
`extrude_geometry`, and beneath that, third-party `geomeppy`); per this project's own standing rule
a change under `openubem/` (or its dependency) is issued by its owner, not us, and any authorisation
must go to `openubem-20` from the author directly, exactly as for the (b1)/(b2) snap-tolerance fix
— never assumed from a peer message or from this delegation. A same-tree detector-only alternative
(extending `find_mismatched_interzone_pairs`) was also considered, but that function equally lives
under `openubem/`, not our runner. Independently, any geometry or detector change — theirs or ours —
is a basis change, and none lands mid-campaign (ES `1315013` RUNNING, IT/UK still PENDING) without
breaking "one campaign, one code version." Both blockers hold regardless of the delegated fix
authority. Recorded as defect `(d)`, fifth on the list, NOT fixed, deferred to the next
re-pre-registration — flagged HIGH PRIORITY there given the blast-radius evidence, unlike the other
four. A read-only blast-radius census (described above) was dispatched next, strictly to size
exposure — no IDF, no engine, no code or campaign change.

Nothing retried, dropped, moved, patched or scored; `C2` stays pinned to `T07`.

Evidence: investigation agent `ac01a5d4a6f30f351`'s full report (root-cause trace, blast-radius
reasoning, fix sketch); `RESUME.md` §2/§3/§5/§8/top-block, edited in place, addendum last+58t;
`memory/project_4j_hetus_llm.md` last+58t.

### 18.28 🔴 BLAST-RADIUS CENSUS RETURNED — defect `(d)`'s trigger topology is present in ~22% of the entire building stock, all three districts

A dispatched read-only agent, following §18.27's proposed method, scanned the actual live payload
trees for all three districts — located under `openubem/outputs/3D/` (the tree
`4thJ_step10_nocore_campaign.py` itself reads, not the older `eu_evidence/EU-11/..._2026-09-08`
staging snapshots, confirmed stale duplicates): ES-MAD-BERRUGUETE 1,174 buildings, IT-BOL-GALVANI2
1,211, GB-LDN-STDUNSTANS 1,240 (Lyon's 509 present but out of scope, not scanned). For every
building, per floor, for every pair of zones, it computed the shared-vertex set between the two
zones' `coords_m` rings.

**Result.** 790 of 3,625 buildings (~22%) contain at least one zone pair sharing EXACTLY one vertex
with no shared edge — the defect's geometric precondition — split ES 349/1,174, IT 332/1,211, UK
109/1,240, 6,994 matching pairs total. Vertex-match tolerance was swept from 1e-9 m to 0.5 m with
IDENTICAL counts throughout (shared vertices are exactly float-coincident by construction; tolerance
choice is not a sensitivity concern here). **Ground-truth check passed**: `way-1237260791`'s own
confirmed defect pair (`dwelling_1`↔`dwelling_3`) is caught by this signature.

**A stricter filter was tried and rejected.** A collinearity test (excluding a shared point where an
edge of either zone runs collinear through it, meant to separate a genuine point-touch from an
end-to-end wall-line continuation) was also computed — it produces a **false negative on the one
confirmed ground-truth case**: `way-1237260791`'s own defect pair has a locally collinear edge at
the touch point, yet the investigation (§18.27) independently proved that exact pair triggers the
real bug. The collinearity test is therefore unreliable on this dataset and is not carried forward;
the loose "shared-vertex-count == 1" signature is reported as the defensible number (0/1174 ES, 1/1211
IT with 4 pairs, 0/1240 UK under the strict filter — numbers recorded but not trusted).

**What this number is and is not.** It is an upper bound on EXPOSURE to the defect's geometric
precondition, not a count of confirmed silent corruption. §18.27 already established the bug can
fire without any visible symptom (most instances would not throw a fatal — only when the sliver's
near-duplicate vertex pair straddles EnergyPlus's own collapse threshold asymmetrically), so this
census cannot by itself say how many of the 790 actually have corrupted geometry, only that they
carry the topology that makes it possible. Confirming actual corruption on any of the other 789
would require re-running geomeppy's own `populate_adjacencies()` logic (or an equivalent) against
each candidate pair — out of scope for a read-only, no-engine, no-code-change census, not attempted.

**Observed, not concluded.** 13 of the other 15 known-failing buildings also carry this same
signature elsewhere in their own geometry — the 3 exceptions (`relation-12702627`,
`relation-12713026`, `relation-12725306`) show none; every zone pair on every floor of those three
shares two or more vertices, consistent with their already-established (b1) manufactured-short-edge
mechanism rather than a point touch. 13/15 (87%) against the general 22% rate is a notable gap, but
presence of the topology elsewhere in a building's geometry does not establish that this mechanism
caused that building's specific fatal — each of the 15 already has its own independently-confirmed
mechanism ((a)/(b1)/(b2)/(c)), and none is reclassified on this evidence alone. Left open.

**Decision unchanged.** The blockers recorded at §18.27 — the fix lives in code owned upstream
(OpenUBEM / third-party geomeppy), never edited unilaterally by this project, and any change (theirs
or a same-tree detector of ours) is a basis change that cannot land mid-campaign (ES `1315013`
RUNNING, IT/UK still PENDING) — concern who may change what and when, not magnitude; a larger number
does not unlock either door. `(d)` stays recorded, NOT fixed, deferred to the next
re-pre-registration — now flagged HIGH PRIORITY with a quantified, cross-district,
ground-truth-validated size (~22%, 790 buildings) rather than a qualitative "plausibly
wide-reaching."

Nothing retried, dropped, moved, patched or scored; `C2` stays pinned to `T07`.

Evidence: dispatched census agent's full report (method, per-district counts, 20 example matches,
caveats — vertex-match tolerance sweep, collinearity-filter rejection, T-junction undercounting
caveat); `RESUME.md` top block/§2/§3/§5, edited in place, addendum last+58u;
`memory/project_4j_hetus_llm.md` last+58u.

### 18.29 🔴 THE 52-59 NEW FAILING BUILDINGS READ AND PARTIALLY CLASSIFIED — one clean genuine (b1) match, one broken-adjacency case that fits NOTHING established, and a SIXTH signature family found (zero/near-zero surface area) — read-only, nothing retried

Read-only, `'bash -s' < script` over SSH throughout, no retries/patches/cancels. Snapshot taken
20:30-20:37 EDT 2026-09-09: `campaign_status.json` — `cells_finished` 9,350→9,550 while this read ran,
`ENERGYPLUS_FAILED` 750→770 (75→77 buildings; the last two are NOT covered below, they appeared after
the building list was pulled — flag for the next read). `payload_set_sha256`
`575960f547ce462a3754eaa8d1f84090f721b5fb7ca135324bb46b6769929486` UNCHANGED — the stock did not move
under this read. `1315013` (ES) still `RUNNING` on `salus`, 31 cpu, 10:33 elapsed; `1315014`/`1315015`
(IT/UK) still `PENDING (Dependency)`.

**Building list re-derived from `cells_failed/*.json` filenames** (never assumed from the prior
19:23 EDT count): `find`-free `ls | sed` over the out-directory, 76 distinct building ids, one of
them (`way-435932082`) carrying only 3 of 10 failed-cell files — **in flight, not a settled failure**,
excluded. **75 settled failing buildings.** Subtracting the 16 already classified (§2/§18.1-§18.28)
leaves **59 new buildings, ALL of them `way-` ids** — zero `relation-` ids among the new failures,
a pattern worth flagging on its own: every building classified through §18.28 that was NOT `way-1237260791`
was a `relation-` id, and now the run has moved entirely into `way-` territory.

#### First pass — error-text signature triage (cheap, bulk, all 59)

`.err` (`eplusout.err`) severe/fatal category counts pulled for all 59 at once (script kept, not
reproduced here in full — see the ledger). Six signature buckets fell out:

```
G1  40   pure "Vertex size mismatch" (RoofCeiling route), nothing else
G2   7   same, PLUS CheckConvexity non-planar / coincident on the same building
G3   5   CalcCoordinateTransformation route (coincident -> degenerate -> invalid dot product)
G4   3   CheckConvexity non-planar + "Zero or negative surface area" on the SAME surface
G5   2   construction-reverse-order severe ALONE (matches (c)-PURE's exact text)
G6   2   "Zero or negative surface area" ALONE, no CheckConvexity, no vertex mismatch
```

**G3 (5) — CONFIRMED (a).** Full `.err` for `way-380242658` read in full: "27 coincident/collinear
vertices...deleted" -> "12 degenerate surfaces" -> `CalcCoordinateTransformation: Invalid dot
product` -> Fatal — the identical route, in the identical order, as the three established `(a)`
members. No further check needed; textual match is exact and this route has no other known cause in
this project. **`(a)` grows 3 -> 8**: adds `way-380242658 way-420411321 way-435509266 way-435510996
way-435638255`.

**G5 (2) — CONFIRMED (c)-PURE.** `way-428478249` and `way-435398513` each carry exactly ONE distinct
severe — `GetSurfaceData: Construction ... does not have the same materials in the reverse order as
...` — word-for-word the same defect as `12863111`/`4164962` (our own `Surface_Type`-only assignment,
`tools/4thJ_step10_nocore_campaign.py` lines 1038-1045), and nothing else in either file. **`(c)`-PURE
grows 2 -> 4**: adds `way-428478249 way-435398513`. (No new MIXED-(c) member found this pass.)

#### The vertex-mismatch family (G1+G2, 47 buildings) — SAME error text as both `(b1)` and `(d)`, and it is NOT one mechanism

Full ring-level inspection (Name/Zone/OBC-Object/vertex-list fields pulled straight from the `.idf`,
matched case-insensitively — the IDF writes `Block way/<id> Storey n Ceiling/Floor ...` in mixed
case, EnergyPlus's own messages report it in upper case, a trap for a first `grep`) was run on two
members as a discriminating test, not all 47:

- **`way-195286070`, pair `STOREY 3 CEILING 0001_2` / `STOREY 4 FLOOR 0001_2`: matches `(b1)` cleanly.**
  Both surfaces write **6** vertices. The two 6-point sets are **byte-identical**, just reordered
  (ceiling's 1,2,3,4,5,6 = floor's 3,2,1,6,5,4). The short edge is between the ceiling's own vertices 4
  and 5 (`440413.91351057764,4478804.158370443` vs `440413.9136430542,4478804.1582430275`), length
  **~0.18 mm — below any 1 mm grid**, same magnitude class as `(b1)`'s three below-grid members
  (`12800464`, `13113580`, `4165178`). This is a genuine, additional `(b1)`-below-grid instance.
- **`way-310738153`, first mismatch pair `STOREY 1 FLOOR 0001_3` (block `_0`) / `STOREY 0 CEILING
  0001_1` (block `_3`): matches NEITHER `(b1)` NOR `(d)`.** The floor writes only **3** vertices, two
  of them near-duplicates (`440351.9893079577,4478694.490033096` vs
  `440351.9892748771,4478694.490021322`) — a collapsed, near-degenerate triangle, not a 6-vs-5-or-4
  near-miss. Worse: the pairing is **asymmetric**. The floor's own `Outside Boundary Condition Object`
  field names the ceiling (`_3 Storey 0 Ceiling 0001_1`) as its partner, but that ceiling's OWN
  `Outside Boundary Condition Object` field names a **third, different surface** —
  `_2 Storey 1 Floor 0001_1` — as ITS partner, not the floor that claims it. A -> B, B -> C, not
  A -> B, B -> A. Neither `(b1)`'s byte-identical-reordered-ring signature nor `(d)`'s
  cross-zone-vertex-sourcing-inside-an-otherwise-consistent-pair signature covers a dangling,
  one-directional adjacency link. **Flagged as its own open question, not forced into `(a)`, `(b1)`,
  `(b2)`, `(c)`, or `(d)`.** Named nothing yet — one building is not a pattern, same standard applied
  to `(d)` before its own root-cause (§18.25).

**The other 45 vertex-mismatch buildings (38 of G1, 7 of G2) were NOT individually ring-checked.**
They share the textual "Vertex size mismatch" / RoofCeiling signature with both confirmed examples
above, which is not sufficient by itself to place them — exactly the lesson of §18.16-§18.17, where
the same textual symptom split into two mechanisms once the rings were actually compared. **Held as
"vertex-mismatch family, sub-mechanism undetermined," 45 buildings**, pending the same
Name/OBC-Object/vertex-list read done on the two examples above. This is flagged as the concrete next
step, not attempted further here — 45 buildings at this level of manual inspection is exactly the
"next session scopes it" scale the delegated fix-authority ruling (last+58s) reserves for the author,
even though this is measurement, not a fix.

#### G4 + G6 (5 buildings) — a SIXTH signature, not seen in `(a)`-`(d)`

```
way-432864105   8 severes, ALL "Zero or negative surface area" (~9.1e-7 m^2), no CheckConvexity
way-433014323   2 severes, ALL "Zero or negative surface area" (~9.7e-7 m^2), no CheckConvexity
way-420409347   1 CheckConvexity non-planar + 1 zero-area severe on the SAME surface (STOREY 0 ROOF 0001_2)
way-434868516   2 CheckConvexity non-planar + 12 zero-area severes, overlapping and adjacent surfaces
way-435639208   4 CheckConvexity non-planar + 2 zero-area severes, overlapping and adjacent surfaces
```

None of these five carries a "Vertex size mismatch," a `CalcCoordinateTransformation`, a
coincident/collinear-deletion count, or a construction-reverse-order severe — the defining severe in
every one is `GetSurfaceData: Zero or negative surface area`, sometimes alone (`way-432864105`,
`way-433014323`), sometimes co-occurring with `CheckConvexity` non-planar on the same or an adjacent
surface (`way-420409347`, `way-434868516`, `way-435639208`). A near-zero-area, non-planar surface is
the textbook shape of a sliver polygon — which is suggestive of `(d)`'s root-caused mechanism (a
spurious sliver computed where two same-floor zones touch at one point, §18.27) manifesting as a
collapsed-area surface instead of a vertex-count mismatch — **but this is a hypothesis, not
established.** No cross-zone vertex-sourcing trace was run on any of these five. **Reported as a
distinct, unnamed sixth signature family, 5 buildings, NOT merged into `(d)` or any other class.**

#### Tally after this pass

```
(a)   CalcCoordinateTransformation route                        8   (was 3, +5)
(b1)  byte-identical rings, engine diverges                      9   (was 8, +1: way-195286070)
(b2)  pairing tangle, cause not established                      1   (unchanged)
(c)   construction assignment, PURE                               4   (was 2, +2)
(c)   construction assignment, MIXED                               1   (unchanged)
(d)   upstream sliver/adjacency, root-caused                       1   (unchanged)
(?)   dangling asymmetric OBC pair, undersized ring                1   NEW — way-310738153
(?)   zero/near-zero surface area, sometimes + non-planar          5   NEW — way-432864105, way-433014323,
                                                                        way-420409347, way-434868516,
                                                                        way-435639208
vertex-mismatch family, sub-mechanism undetermined                45   NOT individually checked
                                                                 ---
                                                                  75   settled failing buildings as of this read
```

Nothing retried, dropped, moved, patched or scored. `C2` stays pinned to `T07`. The two buildings
that failed between the list pull (75) and the final re-poll (77) are unread, flagged for the next
session, same read-only procedure.

Evidence: this fork's SSH transcript (script contents and raw `.err`/`.idf` excerpts quoted above);
`campaign_status.json` reads at 20:28 and 20:37 EDT; `RESUME.md` top block, superseded in place;
`memory/project_4j_hetus_llm.md` (pending the coordinating session's update).

### 18.30 🔴 A DURABLE PER-BUILDING FAILURE LOG BUILT FOR ALL 83 CURRENTLY-FAILING BUILDINGS, PLUS A REUSABLE REFRESH SCRIPT — read-only, nothing retried, one small classification gain and one new (a) member found

Author's instruction: *"for every fail, record the progress log, we can investigate based on these
records."* Read as a request for a durable, structured artefact, not a fix. Read-only throughout,
`'bash -s' < script` over SSH, no retries/patches/cancels; nothing on Speed touched beyond files
already read in §18.1-18.29.

#### What was re-derived, fresh, not carried

`cells_failed/*.json` re-listed at the start of this pass: **830 failed cells, exactly 83 distinct
building slugs** — every one of them now shows **10 of 10** failed-cell files (no in-flight
partials this time; `way-435932082`, which was 3-of-10 in-flight at the §18.29 read, has since
settled at 10 of 10). This confirms the `last+58x` count (830 cells / 83 buildings) rather than
assuming it. `campaign_status.json` at the start of this pass: `cells_finished` 10,625/11,510;
by the time the refresh script was smoke-tested at the end of this pass, `cells_finished` had moved
to 10,875/11,510, `ENERGYPLUS_FAILED` unchanged at 830 — **no new failing building appeared during
this pass's own runtime**, campaign is close to done. `payload_set_sha256` unchanged
(`575960f5...`).

Subtracting the 16 buildings classified through §18.28 and the 8 buildings confirmed in §18.29
(5×(a), 2×(c)-PURE, 1×(b1)) plus the 6 buildings §18.29 individually named but left open (the
one-off `way-310738153`, and the 5-member sixth-signature family) leaves **53 buildings this pass
had to place**: the 45 "vertex-mismatch family, undetermined" already flagged in §18.29 (never
before individually listed by id in this doc) plus **8 buildings that arrived after the §18.29 read**
(75 settled → 83).

#### Method: exactly §18.29's bulk triage, run over all 83 at once, plus one sharpening

For every one of the 83 buildings, one representative `eplusout.err` (`runs/ES-MAD-BERRUGUETE/es__<slug>__caseA__f000/eplusout.err`, or the first sibling cell directory found when `caseA__f000` was
absent) was grepped for six exact substrings, counted with `grep -c`, never assumed from memory:

```
vm  "Vertex size mismatch"
np  "is non-planar"                                              (CheckConvexity)
cc  "CalcCoordinateTransformation"
co  "coincident/collinear vertices"                               (feeds (a))
cn  "does not have the same materials in the reverse order"       (our own construction bug, (c))
za  "Zero or negative surface area"                                (the unnamed 6th family)
```

Two of §18.29's own rules are **exact-text-sufficient and need no ring check** — stated there for
(a) ("textual match is exact and this route has no other known cause in this project") and for
(c)-PURE (same standard, `12863111`/`4164962` precedent). Applying those two rules mechanically to
all 83 (not just the two dozen already checked) found:

**One new (a) member, not in this doc before this pass: `way-942352870`** — `cc=3 co=1`, `vm=0
np=0 cn=0 za=0`, identical signature to every established (a) member. It did not exist at the
§18.29 read (75 settled buildings); it is one of the 8 that arrived since. Confirmed **(a)** by the
same exact-text rule §18.29 used for its own G3 batch — no ring-level check needed or performed.
**`(a)` grows 8 → 9.**

**No new (c)-PURE, (c)-MIXED, or (b1) members found this pass.** The (b1)/(b2)/(d)/one-off classes
all require a ring-level IDF read to distinguish from each other (§18.16-18.27 is the whole reason
this project does not shortcut that read from text alone), and that read was explicitly kept out of
scope for this pass, per the task's own instruction. So every building whose signature is pure
"Vertex size mismatch" (with or without non-planar) — including the 8 new arrivals that are not
`way-942352870` — stays **signature-bucketed, confirmed_class blank**, exactly as the 45 already
were.

#### Final bucket tally, all 83 buildings, this pass

```
(a)   CalcCoordinateTransformation route                         9   (was 8, +1: way-942352870)
(b1)  byte-identical rings, engine diverges                      9   (unchanged)
(b2)  pairing tangle, cause not established                      1   (unchanged)
(c)   construction assignment, PURE                               4   (unchanged)
(c)   construction assignment, MIXED                               1   (unchanged)
(d)   upstream sliver/adjacency, root-caused                       1   (unchanged)
(?)   dangling asymmetric OBC pair, undersized ring                1   way-310738153 (unchanged)
(?)   zero/near-zero surface area, sometimes + non-planar          5   unchanged (no new members)
vertex-mismatch-only, sub-mechanism undetermined                  44   see reconciliation below
vertex-mismatch+nonplanar, sub-mechanism undetermined              8   see reconciliation below
                                                                 ---
                                                                  83   settled failing buildings
```

🔴 **Reconciliation, and a correction to how §18.29's "45 undetermined" is carried forward.**
§18.29's 45 was never itemised by building id, only counted. This pass's vertex-mismatch family
totals 52 (44 + 8) = the 45 pre-existing ones **plus 7 of the 8 buildings that arrived after the
§18.29 read** (the 8th arrival, `way-942352870`, resolved cleanly to (a) above). That arithmetic
(45 + 7 = 52, 8 new − 1 to (a) = 7 into the family) is offered as a reconciliation, not a proof —
because the 45 were never itemised, which specific 45 of the current 52 are the "old" ones cannot be
reconstructed member-for-member from the doc alone. **This pass also splits that single bucket into
two**, because the cheap triage already distinguishes them without a ring check —
`vertex-mismatch-only` (44 buildings, no CheckConvexity at all) and `vertex-mismatch+nonplanar` (8
buildings, CheckConvexity non-planar co-occurring, textually closer to (b2)'s shape). This is not a
new classification, only a finer bucket label. The CSV (below) is now the itemised record, by id, so
this ambiguity cannot recur on the next pass.

Two buildings are flagged for a future ring-level dive, not attempted here (out of scope): 
`way-428478238` (17 vertex-mismatch + a heavy **30** non-planar severes) and `way-435927686` (17 +
**16**) — both carry unusually large non-planar counts relative to the rest of the
`vertex-mismatch+nonplanar` bucket, which the cheap triage cannot explain further. `way-671908209`
(49 vertex-mismatch severes, zero non-planar) is the largest pure vertex-mismatch count in the
whole population, also flagged, also not chased.

#### The durable record: `Step10_docs/impl/C2_ES_failure_progress_log.csv`

One row per failing building, 83 rows, columns `building_id, n_failed_cells, confirmed_class,
signature_bucket, severe_message_counts_summary, first_documented_in, notes`. `confirmed_class` is
populated only for (a)/(b1)/(b2)/(c)-PURE/(c)-MIXED/(d) and cites the impl-doc section that
established it (never re-argued here); the one-off `way-310738153` and the 5-member sixth-signature
family carry a descriptive `signature_bucket` and an explicit note that they are ring-checked/
flagged-open, not assigned a class; the 52 vertex-mismatch-family buildings (44 + 8) carry
`signature_bucket` only, `confirmed_class` blank, and a note stating a ring check was not performed
this pass. This is now the single itemised source of truth for "which building is in which bucket"
— the doc's own prose tallies (§18.29, this section) are summaries of it, not the other way round.

#### The reusable refresh script: `4J_s10_failure_triage.sh`

Deployed to `/speed-scratch/o_iseri/4J_step10_nocore/tree/scripts/4J_s10_failure_triage.sh`
(matches the existing `4J_s10_*.sh` naming convention already in that directory), read-only,
executable. Usage: `bash tree/scripts/4J_s10_failure_triage.sh [DISTRICT]` (default
`ES-MAD-BERRUGUETE`), run over SSH exactly as every other read in this doc. It re-derives the
building list from `cells_failed/*.json`, greps the same six substrings above, and applies the same
two exact-text auto-classification rules ((a) and (c)-PURE/(c)-MIXED) mechanically, printing
`TRIAGE_ROW|...` lines and writing them to a timestamped file under
`out/<DISTRICT>/failure_triage_<stamp>.txt`. **Smoke-tested on the live ES district at the end of
this pass**: reproduced all 83 rows and all 14 auto-classifications (9×(a), 4×(c)-PURE, 1×
(c)-MIXED) identically to the manual pass above, with zero `UNRECOGNISED-COMBINATION` rows. Merging
a fresh run into the CSV is a documented 2-step manual diff (new `building_id`s only; established
ids never change signature), written in full as a comment block at the top of the script itself —
deliberately not automated further, because placing a building into (b1)/(b2)/(d)/one-off still
needs the ring-level read this project has never shortcut.

#### What this pass did NOT do

No ring-level IDF inspection on any of the 53 buildings this pass newly touched — that stays out of
scope, per the task's own instruction. No severe was re-interpreted, no building was moved out of an
already-confirmed class, nothing was retried, dropped, patched, or scored. `C2` stays pinned to
`T07`.

Evidence: this session's own SSH transcripts (`campaign_status.json` reads at the start and end of
this pass; the full 83-row triage dump; the deployed script and its smoke-test output);
`Step10_docs/impl/C2_ES_failure_progress_log.csv`;
`/speed-scratch/o_iseri/4J_step10_nocore/tree/scripts/4J_s10_failure_triage.sh`; `RESUME.md`
`last+58y`, prepended; `memory/project_4j_hetus_llm.md` (pending the coordinating session's
update).
