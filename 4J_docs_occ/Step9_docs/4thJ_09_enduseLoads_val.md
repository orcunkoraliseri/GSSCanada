# Step 9 — Activity-driven end-use loads. Validation.

### 4J HETUS LLM pipeline. Validation specification.
#### Implementation: `4thJ_09_enduseLoads.md`. Parent: `../4thJ_00_HETUS_LLM_Pipeline.md`

---

## STATUS

🟢 **RUN 2026-08-25 (night): 16 PASS / 3 FAIL over fourteen gates and five guards.** 🔴 **CORRECTED 2026-08-26, `FINDING 149`: the runner's own tally is `15 PASS / 3 FAIL / 1 NOT CHECKED` — the "16" counted `G9.4`'s NOT CHECKED as a PASS, which is what `V9.c` forbids. Per-gate verdicts unchanged; see the 2026-08-26 entry at the end.**
Fourteen gates declared here, fourteen scored -- the runner reads the gate IDs out of THIS DOCUMENT
and refuses to report a tally if the two sets differ, because a gate that exists only in prose
occupies the slot of the check that would have caught the defect.

🔴 **`G9.6`, `G9.7` and `G9.12` ship FAIL and no threshold was moved.** 🔴 **Their
registered perturbations therefore demonstrate nothing about them** and are reported as
`ALREADY_FAILING_AT_BASELINE`, never as hits.

⚪ **The battery found four defects in the GATES before it found anything else** -- `G9.5` probing
a code path the campaign could not reach, the `G9.3` perturbation felling `G9.1` as well, and
`G9.13`'s directory exclusion computed on an absolute path, which also disabled `V9.d`'s self-probe.
All four fixed additively. Record:
`docs/2026-08-25_items-9.1-9.5_the-mapping-the-trigger-and-the-campaign.md`.

**All thresholds pre-registered, and none of them edited.**

---

## WHAT THIS STEP MUST PROVE

That the appliance loads are **adapted from a validated lineage rather than invented**, and that they
are only claimed at the scale that lineage supports.

The technical gates below are the easy half. The provenance gates are the half that decides whether a
reviewer accepts the step at all.

---

## PROVENANCE GATES — THE ONES THAT MATTER MOST

| ID | What it detects | Threshold | Provenance |
|---|---|---|---|
| **G9.1** 🔴 Mapping citation completeness | An invented heuristic wearing a citation's clothes | **100 %** of rows in `activity_appliance_map.csv` carry a source model **and** the specific table or figure the value came from. A row citing only a paper is not cited | **project-chosen** |
| **G9.2** 🔴 VALIDATED labelling | A caveat presented as a method | **100 %** of rows carry VALIDATED or NOT VALIDATED **and** the validation scale. 🔴 **A row labelled VALIDATED with no scale is a FAIL, not a warning** | `RL13` |
| **G9.3** Unsourced-row honesty | A plausible number filling a gap | Every NOT VALIDATED row carries our written reasoning. Count of rows with neither a citation nor reasoning: **0** | **project-chosen** |
| **G9.4** Citation correctness | The Widén conflation, and its siblings | Every cited DOI resolves to the title it is cited under. 🔴 `RL08` gave Widén & Wäckelgård 2010 as *Applied Energy* 87(3):780-789; the correct entry is **87(6):1880-1892**, and 41(7):780-788 is the **different** 2009 lighting paper<br>🔴 **CORRECTED 2026-08-20, `FINDING 47`: this example was WRONG on three counts. `41(7):780-788` names no real paper; `41(7):781-789` is **RICHARDSON** et al. *Domestic lighting*; the real Widen lighting paper is **41(10):1001-1012** (`10.1016/j.enbuild.2009.05.002`); the Widen 2009 paper Step 9 needs is **41(7):753-768** (`10.1016/j.enbuild.2009.02.013`). `RL17`'s "CrossRef-verified" DOI `10.1016/j.enbuild.2009.02.006` resolves to *Estimation of passive cooling efficiency for environmental design in Brazil*. 🔴 **AND THE GATE MUST BE WIDENED: a title-only match would have PASSED our wrong note, because it carried no DOI. `G9.4` must also match volume, issue, page range and FIRST AUTHOR against CrossRef.** 🟢 **RULED 2026-08-20, item 12 (a), APPLIED: `G9.4` PASSES only when volume, issue, page range AND first-author surname all match the CrossRef record — never the title alone.** A title-only match is what let our own citation note pass while being wrong on three counts, and what let `RL17`'s "CrossRef-verified" DOI resolve to a passive-cooling paper about Brazil. 🔴 `V9.c` still governs the unreachable case: print `NOT CHECKED`, never `PASS`. | `RL17` A5, ~~verified~~ **FABRICATED — see `FINDING 47`** |

🔴 **G9.2's "no scale is a FAIL" clause exists because of a specific failure shape:** a presence-test
that merely asks *is a label present?* is satisfied by the label. The scale is the content, and a
document that also carries corrections will contain the right *kind* of token in the wrong place.

---

## BEHAVIOURAL GATES

| ID | Check | Target |
|---|---|---|
| **G9.5** | Cycle completion | An appliance triggered near the end of an activity episode **still runs its full rated cycle**. Asserted on synthetic edge cases, not just on the corpus |
| **G9.6** | Trigger rate | Per-appliance daily activation counts within the range the source model reports, per household size |
| **G9.7** | DHW volume | **30 to 50 L/person/day at 60 °C**, population median. Reported per country |
| **G9.8** | DHW event mix | Four-event structure present (short, medium, bath, shower) with the source model's proportions |
| **G9.9** 🔴 DHW **assignment** check | Re-open the saved IDF and assert every `WaterUse:Equipment` object still points at the schedule it was built with. **A value check cannot see a re-pointed object** — in 3J that hid a ×3.028 draw increase across 56 cells with zero violations reported |
| **G9.10** | Energy closure | Σ end-use loads reconciles with the total injected internal gain, within **0.5 %** |
| **G9.11** | 3-digit dependence | The mapping actually **uses** the third digit: the number of distinct ACL codes with distinct appliance rows must exceed the number of distinct 2-digit groups. 🔴 A mapping that resolves only at 2-digit did not need the corpus decision that preserved 3-digit codes, and that should be known. 🟢 **RULED 2026-08-20, item 11 (a): this gate is EXPECTED TO FAIL, and it is allowed to.** `RL25` established that **0 of 4** published end-use models (CREST, Widén, LPG, RAMP) resolve activity at 3 digits, so an appliance mapping sourced from the literature cannot pass it. 🔴 **The band is NOT relaxed** — relaxing a threshold because the answer came out wrong is the one move this project refuses. The failure is recorded as a FAIL and the 3-digit corpus decision is re-justified on **microdata fidelity** instead: the third digit exists in the source, and discarding it to make a gate pass would be discarding data to flatter a number |
| **G9.14** 🔴 Trigger inputs exist in the generated record | A trigger reading a column the generated diaries do not carry | The set of columns the trigger reads at runtime is a **subset** of the columns present in `../Step7_docs/outputs_step7/generated_<country>.parquet`, asserted against the file, not against a schema constant. 🔴 **`act2` is calibration-only and must not appear in this set.** A trigger reading an absent column does not raise — it silently never fires |

---

## SCALE GATES — BOUNDING THE CLAIM

| ID | Check | Target |
|---|---|---|
| **G9.12** | Stock-scale agreement | Aggregate load shape over ≥ 100 dwellings against the source models' published aggregate profiles, **R² ≥ 0.85** |
| **G9.13** 🔴 Per-dwelling non-claim | **No result in any output, table or figure is a per-dwelling prediction.** Asserted by a search over the results artefacts for per-dwelling framing |

**G9.13 is a gate on our own writing, and it is deliberate.** The source models validate at feeder
scale; a figure that shows one dwelling's predicted day invites exactly the claim the literature does
not support.

---

## EVERY GATE MUST BE SEEN FAILING

| Perturbation | Must fail | Must stay clean |
|---|---|---|
| Strip the table reference from one mapping row | **G9.1** | G9.2 |
| Label a row VALIDATED with no scale | **G9.2** | G9.1 |
| Add a row with a number and no source | G9.3 | G9.1 |
| Cite Widén 2010 as 87(3):780-789 | **G9.4** | G9.1 |
| Truncate an appliance cycle at episode end | **G9.5** | G9.6 |
| Double one appliance's trigger probability | G9.6 | G9.5 |
| Scale DHW draw by 2 | G9.7 | G9.8 |
| Collapse the four events into one | G9.8 | G9.7 |
| 🔴 **Re-point one `WaterUse:Equipment` at another schedule, leaving its values untouched** | **G9.9** | G9.7 — *the value check sees nothing, which is the whole point* |
| Drop one end use from the sum | G9.10 | G9.6 |
| Replace the mapping with a 2-digit one | **G9.11** | G9.10 |
| 🔴 **Add `act2` to the trigger's runtime input columns** | **G9.14** | G9.10, G9.6 — *the appliance simply never fires on that rule and every total still reconciles, which is why nothing else sees it* |
| Zero the load on 20 % of dwellings | G9.12 | G9.10 |
| Add a per-dwelling prediction figure | G9.13 | all others |
| 🔴 **Null perturbation: change nothing** | **nothing** | everything |

### Coverage clause

Cross-tab every perturbation against baseline; **FAIL the probe if any passing gate was never made to
fall.**

---

## VACUITY GUARDS

* **V9.a** — the runner FAILs if `activity_appliance_map.csv` has fewer rows than there are distinct
  ACL codes in the corpus that the mapping claims to cover, **and prints the shortfall**.
* **V9.b** — G9.1 to G9.4 print the row count they scanned before any verdict. A provenance check over
  an empty set passes for the wrong reason.
* **V9.c** — G9.4 resolves DOIs live where possible and **prints `NOT CHECKED` rather than passing**
  when it cannot reach the resolver. 🔴 A check that cannot distinguish *found nothing* from *could
  not run* is not a check.
* **V9.d** — G9.13's search must print the files it scanned and FAIL if it scanned fewer than the
  results directory contains. A green check that scanned nothing is decoration.
* **V9.e** — G9.2's presence test keys on the **structured field**, not on the presence of the word.
  A document containing a superseded quotation contains the right kind of token in the wrong place,
  and a naive presence test reads the correction as compliance.

---

## WHAT THIS STEP'S VALIDATION DOES **NOT** COVER

* It does **not** validate the source models themselves. We adapt CREST, Widén, LPG and RAMP; their
  own validation is theirs, and G9.12 checks only that our adaptation reproduces their aggregate
  behaviour.
* It does **not** establish per-dwelling accuracy, and G9.13 exists to stop us implying otherwise.
  **This is limitation E1 and it bounds every downstream energy claim in the paper.**
* It does **not** cover appliance stock ownership rates by country. If Italian and British dwellings
  own different appliances at different rates, that is a **country-level input we do not have**, and
  it is a real gap in a cross-national paper. State it in the methods rather than let G9.12's
  aggregate agreement imply it was handled.
* 🔴 It does **not** separate this step's contribution from the chaining rule (open decision 14). If
  chaining dominates peak demand, appliance-level realism is being measured through a convention that
  moves the answer more than it does.

---

## PROGRESS LOG

Append-only.

### 2026-08-14 — validation document created

* Thirteen gates, fourteen perturbations, none run.
* 🔴 G9.11 is unusual and worth keeping: it checks that a **corpus decision taken for this step** was
  worth taking. Author decision 6 preserved 3-digit activity codes partly so that the appliance
  trigger could distinguish laundry from cooking. If the delivered mapping resolves only at 2-digit,
  that decision bought nothing here — and it is better to know that than to assume it.

### 2026-08-14 (second entry) — G9.14, the gate for a rule that fails by staying silent

* **Fourteen gates, fifteen perturbations, none run.**
* 🔴 **G9.14 exists because the failure it catches produces no error and no wrong number.** A trigger
  rule reading `act2`, a column the generated diaries do not carry, does not raise: the appliance
  simply never fires.
  > 🔴 **CORRECTED FORWARD 2026-08-25, `FINDING 137`: THE GENERATED DIARIES DO CARRY `act2`.**
  > The episode tuple has five comma-fields and **29.816 % of shipped Leg-5 episodes** carry a
  > non-empty `act2`. So the failure mode described above -- "the appliance simply never fires" --
  > **cannot happen**; a trigger reading `act2` WOULD fire. The gate is re-specified as a POLICY
  > assertion (`D-S9-2` item 3): the trigger's runtime columns must be a subset of the generated
  > record's **and must not contain `act2`, because `D-S9-1` ruled (d)**. The registered
  > perturbation is unchanged and still fells it. Energy closure (G9.10) still reconciles, trigger rates (G9.6) still fall inside
  the source model's range for every rule that *did* fire, and the load is missing rather than wrong.
* **It asserts against the file, not against a schema constant.** A schema constant is written by the
  same hand as the trigger and would agree with it about a column neither has checked exists.

### 2026-08-25 (night) — 🟢 **THE BOARD IS RUN FOR THE FIRST TIME: 16 PASS / 3 FAIL, and the battery's COVERAGE CLAUSE PASSES.**

**Fourteen gates, five guards, all nineteen implemented.** The runner reads the gate IDs out of THIS
document and refuses to report a tally if what it scored differs from what is declared here — a gate
that exists only in prose occupies the slot of the check that would have caught the defect.

| | |
|---|---|
| `G9.1` PASS 61 | every load-bearing row names a source model and a table |
| `G9.2` PASS 192 | label and scale, keyed on the STRUCTURED field (`V9.e`) |
| `G9.3` PASS 149 | every NOT VALIDATED row carries reasoning or a citation |
| `G9.4` PASS 3 | CrossRef match on title, volume, issue, pages **and first author** |
| `G9.5` PASS | a cycle in the only eligible minute of the day ran all 60 minutes |
| **`G9.6` FAIL 60** | `FINDING 139`, saturation; 3 standby-only devices NOT_EVALUABLE |
| **`G9.7` FAIL 300** | medians 100.16 / 117.65 / 91.06 against the registered 30-50 band |
| `G9.8` PASS 12 | four DHW categories, within 3 pp of Table 1's portions |
| `G9.9` PASS 300 | assignment check, re-read off the SAVED IDF |
| `G9.10` PASS 300 | closure rebuilt from the saved IDF and the on-disk schedules |
| `G9.11` PASS 11 | `FINDING 140`, 6 vs 5 on CREST's rows, group 33 only |
| **`G9.12` FAIL 3** | R2 0.297 / 0.411 / 0.035 against 0.85 |
| `G9.13` PASS 28 | no per-dwelling framing; 2 negated mentions counted as denials |
| `G9.14` PASS 9 | runtime columns a subset, `act2` absent by policy |
| `V9.a`-`V9.e` PASS | each proven on a falsifier the same run |

🔴 **`G9.6`, `G9.7` and `G9.12` ship FAIL and NO BAND WAS MOVED.** All three are results:
saturation, a band whose basis its own source does not define, and a load shape that genuinely
disagrees with CREST's UK-2000 activity timing. 🔴 **Their three registered perturbations
therefore demonstrate nothing about them** and are reported `ALREADY_FAILING_AT_BASELINE`, never as
hits — the vacuity condition, the same shape Step 6 recorded for its Leg-5 coverage clause.

🟢 **The battery: 12 HIT / 0 MISS / 3 already-failing, null perturbation moved nothing,
COVERAGE CLAUSE PASS.** Every gate that passes at baseline was made to fall by something.

🔴 **The battery found FOUR defects in the gates themselves before it found anything else**,
all fixed additively: `G9.5` probed a synthetic case with the truncation switch defaulted off, so a
perturbed campaign could not reach it; the `G9.3` perturbation also felled `G9.1`, because the
planted row had no source at all; `G9.13`'s scratch-directory exclusion was computed on the ABSOLUTE
path, so scoring an output tree that itself sat under a `_`-prefixed directory made the gate skip the
artefacts it was pointed at; and that same bug disabled `V9.d`'s self-probe.

⚪ **`V9.a` gets a falsifier of ours** — drop an ACL code the corpus contains and watch the
shortfall print — because the registered table falsifies the fourteen gates and says nothing about
the five guards. `V9.b`, `V9.c`, `V9.d` and `V9.e` prove themselves by construction on every run.

⚪ **`G9.4` is implemented in its widened form** (`FINDING 47`): title alone is never enough, and a
citation with no DOI must carry a retrievable artefact and a recorded md5 instead — stricter than
the DOI clause, not a waiver of it. `V9.c` proves the NOT CHECKED path every run on an unresolvable
DOI.

⚪ **`G9.11`'s implementation was itself caught passing for the wrong reason** before it shipped:
the first version counted DHW rows into the signature and returned 9 vs 5 without saying where the
splits came from. It now prints the electricity-only breakdown beside the verdict, which is what
turned it into `FINDING 140`.

---

### 2026-08-26 — THE WHOLE GATE BOARD WAS RE-SCORED AFTER THE ROTATION AND CAME BACK IDENTICAL

⚪ **`D-S9-3` was ruled (a) and executed**, so every Step 8 artefact was rebuilt on schedules
rotated to midnight (`Step8_docs/docs/2026-08-26_D-S9-3a_the-rotated-re-run.md`). Step 9 was
re-scored afterwards to find out whether any of its verdicts depended on the defect.

🟢 **They did not.** `4thJ_step9_trigger.py` was re-run on all three folds, then
`4thJ_step9_aggregate.py`, then `4thJ_gates_step9.py --root . --offline`. Every per-gate verdict is
unchanged: `G9.6`, `G9.7` and `G9.12` fail for the reasons already recorded above, and `G9.4` is
NOT CHECKED on `V9.c`'s unresolvable-DOI path. A `diff -rq` of the 630-file output tree against a
snapshot taken before the re-run printed **nothing** and exited 0.

🔴 **`FINDING 149` — but the TALLY was wrong, and it was wrong in the one direction this
document forbids.** The runner prints
`counts: {"FAIL": 3, "NOT CHECKED": 1, "PASS": 15}`. The 2026-08-25 entries above say
**16 PASS / 3 FAIL over fourteen gates and five guards** — nineteen either way, so the missing
verdict is `G9.4`'s **NOT CHECKED**, counted by hand as a pass. `V9.c` exists to stop exactly that
substitution in code, and the prose performed it anyway. **Every "16 PASS / 3 FAIL" in this document
and in `4thJ_09_enduseLoads.md` is superseded by "15 PASS / 3 FAIL / 1 NOT CHECKED".** The earlier
entries are left standing because the log is append-only; nothing in the gates, thresholds or
checkers was changed to obtain the corrected line.

⚪ **This is the check, not a formality.** Step 9's presence schedules are rebuilt by
`4thJ_step7_schedules.py` and its trigger refuses to run unless all 100 reproduce the shipped CSVs
byte-for-byte — so had the rotation reached Step 9, the trigger would have refused, or the tree
would have differed. Neither happened. **No threshold was moved, no checker was edited to make a
gate pass**, and `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` is untouched.
