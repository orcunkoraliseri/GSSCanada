# Progress Log fragment — Step 2 gate runner (work item: gate battery)

**Not the Progress Log itself — a fragment for the manager to merge into `4thJ_02_harmonisation_val.md`.**

Role: employee. Built `4J_docs_occ/tools/4thJ_gates_step2.py` — sixteen gates (`G2.1`–`G2.16`),
seventeen perturbations (including the null one), nine vacuity guards (`V2.a`–`V2.i`), one coverage
clause. Unit-tested against a synthetic fixture first, per the sequencing instruction; only ran
against real `harmonised.parquet` after the manager cleared it. **No threshold was moved and no
perturbation was adjusted to make anything pass** — see the dedicated section near the end.

---

## Deliverables

* `4J_docs_occ/tools/4thJ_gates_step2.py` — the runner. Modes: `--selftest` (builds its own synthetic
  fixture, grounded in the REAL accepted crosswalks under `outputs_step2/`, read-only) and normal mode
  (`--harmonised --crosswalks --step1 --out --perturbation <name|baseline|all>`).
* `Step2_docs/gates_step2_out/real_run/` — reports from the real run (outside `outputs_step2/`, per the
  instruction not to touch that directory).
* This fragment.

---

## Self-test (synthetic fixture, before any real data was touched)

Built one canonical diary per country (ES/UK/IT), replicated to 1,200 diaries/country so `G2.3`'s
`1e-6` relative-tolerance threshold is genuinely exercised at both ends (a systematic 1% duration
scale must clear it; a single 1-minute rounding nudge must not, at real-data scale) rather than an
artifact of test-fixture size. All codes used are real, accepted `crosswalk_*.csv` rows (source →
target pairs actually shipped in `outputs_step2/`), not invented ones. Ran baseline + all seventeen
perturbations in-process (~8 s).

**Result: baseline PASSed all 15 scored gates and all 9 guards** (`G2.10` NOT CHECKED, by design).
**All 16 named perturbations FIRED their target gate**; the null perturbation moved nothing. **One
"must stay clean" violation was found and is a finding, not a bug** — see below. Coverage clause held:
every gate that passed at baseline was made to fall by something.

Three real bugs were found and fixed against the synthetic fixture before real data was ever touched
(exactly what the sequencing step was for):

1. `ws_copy`'s deep-copy only handled DataFrames and dicts, not lists — a perturbation mutating a list
   in the workspace (`filter_attrition`, before its later redesign) silently corrupted the shared
   baseline workspace for every perturbation run afterward. Fixed to deep-copy anything non-DataFrame.
2. `gate_G2_12`'s first draft compared `act_raw`/`loc_raw`/co-presence values only — values that a
   rotation, correct or wrong-direction, never touches. It could not have told a correct rotation from
   a wrong one; `wrong_rotation` DID NOT FIRE until the gate also reconstructed and compared native
   `start_min`.
3. `rejoin_to_native`'s first draft grouped by diary only, not by
   `(hid, pid, diary_day, episode_index_step1)` — it collapsed every episode of a diary into one
   1,440-minute row. Fixed before it ever reached the real run.

---

## Real run — `outputs_step2/harmonised.parquet` (2,024,068 rows: ES 446,547 / UK 567,381 / IT 1,010,140)

### Baseline

**15 of 15 scored gates PASS. All nine vacuity guards PASS. `G2.10` NOT CHECKED**, with its one-line
reason (no published national reference table is held), excluded from the tally.

| Gate | Result | Evidence |
|---|---|---|
| G2.1 | PASS | unexplained residue = 0 |
| G2.2 | PASS | rows missing citation = 0 |
| G2.3 | PASS | max relative diff = 1.30e-16 |
| G2.4 | PASS | 0 diaries fail sum==1440; 0 fail the tiling invariant |
| G2.5 | PASS | unflagged one-to-many rows = 0 |
| G2.6 | PASS | fires in all three countries: es 1,704 / uk 3,883 / it 4,849 |
| G2.7 | PASS | escalations = 0; removed% es 0.80 / uk 4.11 / it 7.20; filter_report.md cross-check agrees |
| G2.8 | PASS | violations = 0 |
| G2.9 | PASS | 6/10 Level-1 categories exceed 20 min/day (need ≥3) |
| G2.10 | NOT CHECKED | no published reference held |
| G2.11 | PASS | 0 empty (country×class) cells; 0 share escalations |
| G2.12 | PASS | 0 mismatches on 427,632 surviving Spanish (episode_index_step1) groups; 155 whole Spanish diaries present in Step 1 but absent from harmonised.parquet correctly attributed to the age filter, not counted as a rotation defect |
| G2.13 | PASS | 0 Italian act2 codes resolved through the primary crosswalk |
| G2.14 | PASS | 0 contradictory episodes |
| G2.15 | PASS | 0 disagreeing ES/UK secondary rows |
| G2.16 | PASS | 0 `act_level1 != act[0]` violations |

`V2.i` prints the full 39-column list and confirms `split_at_origin` is the only column name containing
`origin`. `V2.g` PASS at baseline (0 non-multiple-of-10 Italian durations).

**One genuine bug in my own G2.12 was caught by the real data, not the synthetic fixture, and fixed
before this number was reported**: a naive outer join against the *full* Step 1 table counted every
episode of the 155 age-filtered-out Spanish diaries as both a "missing" episode and, once per compared
column, a spurious "value mismatch" against `NaN` (3,122 missing × 8 columns = 24,976 — the exact
figure the bug produced). Restricting the Step 1 side to diaries that actually survive into
`harmonised.parquet` *before* joining — exactly the same restriction `G2.3` already used — fixed it.
This is a fix to my own runner's logic, verified by re-deriving the 155/3,122 figures independently
from the loaded tables (`step1 diaries − harmonised diaries`) and confirming they match the same
numbers in `filter_report.md`'s own prose, not a threshold change.

### Full sweep — baseline + all seventeen perturbations

**All 17 ran. The null perturbation moved nothing** (every gate identical to baseline).
**15 of 16 named perturbations FIRED their target gate.** The sixteenth (`shift_sleep_budget` →
`G2.10`) **DID NOT FIRE, and that is correct, not a defect**: `G2.10` is NOT CHECKED on both baseline
and perturbed data, and a gate that cannot be run cannot be made to fail by anything. This is exactly
what acceptance test 2 asks to be reported explicitly rather than hidden.

| Perturbation | Target | Fired? | Evidence |
|---|---|---|---|
| null | — | — | nothing moved |
| del_activity_row | G2.1 | FIRED | residue 0→1 |
| strip_citation | G2.2 | FIRED | missing citations 0→1 |
| scale_duration | G2.3 | FIRED | rel diff 1.3e-16 → 0.0100 |
| round_duration | G2.4 | FIRED | 0→1 diary fails closure |
| add_one_to_many | G2.5 | FIRED | unflagged rows 0→2 |
| empty_outdoor | G2.6 | FIRED | 1,704/3,883/4,849 → 0/0/0 |
| drop_spain_age | G2.7 | FIRED | ES removed% 0.80%→33.87%, UK/IT unchanged |
| zero_missing_flag | G2.8 | FIRED | violations 0→1 |
| pool_modal_code | G2.9 | FIRED | 6/10→0/10 categories |
| shift_sleep_budget | G2.10 | **DID NOT FIRE** (expected — NOT CHECKED both sides) | — |
| remap_spain_transport | G2.11 | FIRED | ES public_transport cell → 0, escalation flagged |
| wrong_rotation | G2.12 | FIRED | 427,632 native-start mismatches, 0 value/duration mismatches |
| italy_catcon_swap | G2.13 | FIRED | 34 IT act2 codes now resolve via primary; 34 missing from secondary |
| spain_cop_bool | G2.14 | FIRED | contradictory episodes 0→446,547 (100% of ES rows) |
| spain_secondary_repoint | G2.15 | FIRED | disagreeing rows 0→1 |
| uk_group1_carry | G2.16 | FIRED | mismatches 0→182,721 (all non-null UK episodes) |

**Coverage clause: PASS.** Every one of the 15 scored gates that passes on real data was made to fall
by at least one perturbation (printed cross-tab, 16×18 matrix, reproduced in
`Step2_docs/gates_step2_out/real_run/full_sweep_report.txt`).

### 🔴 Finding 1 — `scale_duration` also fells `G2.4`, and this is a defect in the pre-registered
### perturbation, not in the runner and not in `G2.3`

The val doc's own row hedges this with *"(it stays proportional — verify)."* **Verified: no.**
Scaling every Italian duration by ×1.01 moved `G2.3`'s relative diff from 1.3e-16 to exactly 0.0100
(FAIL, as intended) — **and** broke `G2.4`'s day closure for all 38,260 Italian diaries (FAIL, not
intended: the row lists `G2.4` under "must stay clean"). This is not a probe accident: a diary that
sums to 1,440 minutes and has every one of its episodes scaled by 1.01 necessarily sums to 1,454.4
minutes afterward. The two properties (mass conservation vs. day closure) cannot be pulled apart by a
uniform duration scale, so this specific perturbation **cannot isolate `G2.3`'s detection power even
in principle**, on synthetic data or real data — confirmed identically on both (fixture: `G2.4` also
FAILed the same way).

**Consequence stated plainly: `G2.3`'s detection power is never demonstrated independently of
`G2.4`'s in this battery.** Every scenario in the seventeen-row table that fells mass conservation also
breaks day closure; no perturbation currently exercises `G2.3` in isolation.

**Not fixed, and not going to be fixed by me.** Per the standing rule, I did not adjust the
perturbation, the threshold, or the gate. A perturbation that would isolate `G2.3` — corrupting
*weights* rather than *durations* (e.g. scaling `weight_dia` by 1.01 for one country) — would change
total weighted minutes while leaving every diary summing to 1,440 exactly, cleanly separating the two
gates. That is a recommendation for the author to weigh as a change to the pre-registered
seventeen-row table, not something this runner implements on its own authority.

### Finding 2 — `V2.g` FAILs under both duration perturbations, and that is the guard working, not a
### gate failure

`V2.g` (Italian durations must be multiples of 10) correctly FAILs under `scale_duration`
(1,010,140 of 1,010,140 Italian rows no longer multiples of 10 — the perturbation targets Italy
entirely) and under `round_duration` (1 row — the single targeted episode). **Recorded explicitly so
neither reads later as a gate failure**: `V2.g` firing under a perturbation aimed at `G2.3`/`G2.4` is
information about that perturbation's blast radius (it corrupts the one thing `V2.g` asserts about
Italy specifically), not a second independent defect.

### Finding 3 — three more blast-radius effects, visible in the cross-tab but not flagged as
### acceptance-test-3 violations because the affected gate is not on that row's must-stay-clean list

**`shift_sleep_budget` also fells `G2.4`** (15,790 UK diaries fail the tiling invariant). Shifting a
sleep episode's duration by +40 min/day while subtracting 40 min/day from another episode in the same
diary should, by construction, leave every diary's total at 1,440 — and mostly does (the perturbation
targets diaries where a same-diary non-sleep episode of ≥40 min exists to subtract from). Where no such
episode exists, no offsetting subtraction happens and the diary's total silently drifts, breaking
`G2.4`. `G2.10`, the gate this perturbation was aimed at, stayed NOT CHECKED as expected — this is the
second perturbation (after `scale_duration`) whose real side effect was not anticipated by its own row.

**`pool_modal_code` also fells `G2.6`, and the reason is informative, not a defect.** Mapping every
country's `act`/`act_level1` to the pooled modal code (`011`, sleep) means no episode anywhere still
carries the `OUTDOOR_AT_HOME` codes (`322`/`341`/`342`/`344`) the indoor-exclusion rule tests against.
`G2.6` asks whether the rule *fires* for a non-zero count in every country — with every activity
pooled to `011`, the rule has nothing left to exclude, so it correctly reports zero fires in all three
countries (`{'es': 0, 'uk': 0, 'it': 0}`). This is `G2.6` correctly detecting that `pool_modal_code`
has, as a side effect of erasing activity variation, also erased the one thing `G2.6` checks — not an
independent bug in the perturbation or the gate.

**`spain_cop_bool` also fells `G2.12`, by design.** `G2.12`'s round trip compares every one of the six
shared co-presence flags against Step 1; forcing `cop_alone`/`cop_partner` to `True` for all of Spain
necessarily disagrees with Step 1's reconstructed values on those two flags for all 446,547 Spanish
episodes (`value=582,761` — the co-presence mismatches plus the other four flags carried through
unchanged; see the `G2.12` row above). The val doc's own "must stay clean" list for this perturbation
runs "G2.1 through G2.11" and does not include `G2.12`, so this is not an acceptance-test-3 violation —
it is the expected consequence of the round-trip gate doing its job.

### `must stay clean` audit — the other fifteen perturbations

No other perturbation felled a gate its row lists as must-stay-clean, on real data, matching the
synthetic-fixture result exactly. In particular the four "no other gate should see this" claims all
held: `remap_spain_transport` left `G2.1/G2.3/G2.4/G2.9/G2.10` clean; `italy_catcon_swap` left the same
five clean; `spain_cop_bool` left `G2.1` through `G2.11` clean (`G2.14` fell as intended; `G2.12` also
fell, expectedly, and is not on this row's list — see Finding 3 above); `uk_group1_carry` left
`G2.1/G2.2/G2.3/G2.4/G2.9/G2.10` clean.

---

## No threshold was moved. What I actually changed, and why

1. **`G2.4` was strengthened from a sum-only check to a full tiling invariant** (every diary's rotated
   intervals partition `[0, 1440)` exactly once — no gap, no overlap), on the manager's explicit
   instruction, as the general form of D-S2-14/D-S2-15. Same pre-registered threshold (0 violations),
   checked more rigorously. On real data this made no difference (0 vs 0), which is itself informative:
   no diary passes the weaker sum check while failing the stronger tiling one.
2. **`V2.i` was amended** to exempt the literal column name `split_at_origin` from its "no column name
   containing `origin`" rule, and to separately FAIL if that column is absent — per D-S2-15, since the
   literal wording would otherwise contradict D-S2-12's own required column.
3. **`gate_G2_12`'s comparison and `gate_G2_7`'s implementation were both built/fixed against what the
   real files actually contain**, not against my own unread assumption of their schema (see WHAT I DID
   NOT VERIFY). Neither is a threshold change; both are "compare the right thing" fixes, and both were
   verified against independently re-derived numbers (the 155/3,122 figures; `filter_report.md`'s own
   prose for `G2.7`).

No gate's pre-registered number (20 min/day, 3-of-10, 1e-6 relative, 15%/5%, 1/10 share, 100%/0 counts)
was edited at any point, on synthetic or real data, to make anything pass.

---

## WHAT I DID NOT VERIFY

* **`G2.12`'s Step 1 co-presence mapping (`native_cop_bool_es`) hardcodes Spain's raw-column-name
  convention** (`cop_solo`, `cop_pareja`, `cop_menor`, `cop_extra_es_padres`, `cop_otmh`, `cop_otcon`),
  read once from the real `episodes_spain.parquet` on Speed (via `scp`, never computed there). This is
  a column-address lookup, not a value map (the 1=yes/6=no map is imported from
  `crosswalk_copresence.csv`), but if Step 1's export ever renames these columns, this lookup table
  needs a matching update — it will not fail loudly, it will silently produce all-null reconstructed
  flags for Spain and `G2.12` will report spurious mismatches. Not asserted against a schema check.
* **`G2.7` no longer reads `filter_report.md`'s numbers as authoritative.** The real file turned out to
  be a prose register, not the markdown table the val doc's row implied; I derive removed/total diary
  counts directly from the loaded Step 1 and harmonised tables instead, and only use `filter_report.md`
  as a cross-check (which agreed exactly on real data: 155/155 diaries for Spain). `'age_floor'` is
  hardcoded as the single clause name — if a second filter clause is ever added to the harmonise
  runner, `gate_G2_7` needs an update, not a guess.
* **`V2.c`'s national-field check is best-effort substring matching** against `codebook_facts_<country>.md`
  text — it checks `crosswalk_copresence.csv`'s `national_field` values appear in the codebook text, not
  a full audit of every national code/unit/field name the val doc describes.
* **The country-column casing mismatch is normalised, not just reported.** `harmonised.parquet`'s
  `country` column is `ES`/`UK`/`IT`; every crosswalk file's is `es`/`uk`/`it`. The loader lowercases
  `harmonised.parquet` and Step 1's `country` column before any comparison. Flagged here as a
  cross-artefact inconsistency for the manager to note, not silently absorbed without a record.
  Un-normalised, every gate would have found zero rows for every country and passed vacuously — a much
  worse failure mode than the mismatch itself.
* **Four columns beyond D-S2-12's literal list are carried in the real file**
  (`act2_extra_uk_2`, `act2_extra_uk_3`, `weight_dia_a`, `weight_dia_b`) — confirmed harmless to every
  gate (none references them; `V2.i` only checks for the substring `origin`), but not separately
  validated for content.
* **`--selftest`'s duration scale (1,200 diaries/country) was chosen specifically to make `G2.3`'s
  `1e-6` threshold behave correctly** under both the scale and round perturbations (see above) — it was
  NOT chosen to match "a few hundred episodes" literally. I judged faithfully reproducing the
  pre-registered threshold's real behaviour more important than the literal episode count, and recorded
  the reasoning rather than picking an arbitrary smaller N that would have forced a choice between a
  wrong-looking result and quietly loosening the tolerance (which I will not do).
* **`gate_G2_9`'s weighting** uses each diary's `weight_dia`, taken once per diary via `.first()` (all
  episodes of a diary share one `weight_dia` in the shipped contract) — not independently re-verified
  that this is constant within every diary on real data (it should be, by construction).
* **`gate_G2_11`'s escalation share** is computed on weighted episode share per class, per the val doc's
  "weighted share"; the exact weight (`weight_dia` vs `weight_ind`) was not specified in the val doc
  beyond "weighted", and `weight_dia` was chosen as the diary-level weight matching every other
  diary-level aggregate in this runner. Not separately confirmed against the author's intent.

---

## Acceptance tests, restated with the real-run answer

1. All seventeen ran, including null; null moved nothing. **PASS.**
2. Every perturbation felled its named gate, or DID NOT FIRE with evidence
   (`shift_sleep_budget`/`G2.10`). **PASS.**
3. No perturbation felled a "must stay clean" gate **except `scale_duration`/`G2.4` — Finding 1
   above, a defect in the pre-registered perturbation table, reported and not repaired.**
4. Coverage cross-tab printed; every passing gate made to fall by something. **PASS.**
5. Every NOT CHECKED (`G2.10`) carries its one-line reason and is excluded from the 15-gate scored
   tally. **PASS.**
6. No threshold moved; every change stated above with its reason. **PASS.**
