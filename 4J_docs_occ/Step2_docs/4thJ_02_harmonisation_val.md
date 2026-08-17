# Step 2 — Harmonisation. Validation.

### 4J HETUS LLM pipeline. Validation specification.
#### Implementation: `4thJ_02_harmonisation.md`. Parent: `../4thJ_00_HETUS_LLM_Pipeline.md`

---

## STATUS

**OPEN. Nothing built, no gate run, none seen failing.** All thresholds pre-registered.

---

## WHAT THIS STEP MUST PROVE

That **three** national files now speak one language **without the harmonisation having invented the
agreement** *(superseded: "four", decision 16 excluded France)*.

That distinction is the whole risk of this step. A crosswalk that maps every ambiguous national code
to the nearest target code will produce three beautifully agreeing distributions and will have
manufactured the paper's premise.

🔴 **Added 2026-08-16, and it is the same risk in the opposite direction.** D-S2-6-a found that Spain's
episodes split on co-presence change while the UK's and Italy's do not, so **Spain has more and
shorter episodes by construction.** That is a manufactured *dis*agreement, and no gate here detects it
because none can — it is a property of the reconstruction, not of the data. It is handled by a
prohibition instead: **no cross-country comparison of episode count or mean episode duration, anywhere.**

---

## GATES

| ID | What it detects | Threshold | Provenance |
|---|---|---|---|
| **G2.1** Crosswalk totality | Codes quietly dropped in mapping | Every source code either maps to a target code **or** appears in `crosswalk_unmapped.md` with a reason. Unexplained residue: **0** | **project-chosen** |
| **G2.2** Crosswalk citation | A mapping row invented rather than read | 100 % of mapping rows carry a codebook page reference | **project-chosen** |
| **G2.3** Mass conservation | Time created or destroyed by the mapping | Total weighted minutes per country **unchanged** by harmonisation, to within floating-point tolerance (`< 1e-6` relative) | **derived** — a relabelling cannot change duration |
| **G2.4** Post-filter duration closure | A filter that breaks the day | `sum(duration) == 1440` for 100 % of surviving diaries | **derived from the instrument** |
| **G2.5** One-to-many audit | The arbitrary heuristic hiding in an ambiguous mapping | Every one-to-many mapping row is flagged, counted and carries a written rule. Count of **unflagged** one-to-many rows: 0 | **project-chosen** |
| **G2.6** Indoor-rule reachability | An exclusion list that never fires, i.e. a rule that does nothing | The `OUTDOOR_AT_HOME` exclusion must change `indoor_presence` for a **non-zero** number of episodes in **every** country. 🔴 A country where it fires zero times means either that country records no gardening at home, or the rule is not wired in | **project-chosen**, and it is a vacuity guard on a rule, not a threshold on data |
| **G2.7** Filter attrition, per clause per country | A filter that silently guts one country | Reported, not thresholded. 🔴 **Escalate if any single clause removes more than 15 % of one country's respondents while removing less than 5 % of another's** — that is a country-specific instrument difference wearing a filter's clothes | **project-chosen** trigger |
| **G2.8** Co-presence missingness | Missing collapsed into absent | For every country × flag, the value is one of {recorded, not recorded}, and no flag that `copresence_availability.md` calls "not recorded" contains a 0 in the data. 🔴 **After D-S2-2 the country × flag grid covers the shared flags *and* every country-extra column**, so an extra that was silently zero-filled for the countries that do not field it fails here. 🔴 **After D-S2-8 the shared set is SIX, not five** — the grid gains `cop_parent` — and the UK's `WithMiss` rows must read *missing*, never 0, on all six | **project-chosen** |
| **G2.9** Cross-country activity divergence | 🔴 **Over-harmonisation** — the mapping erasing real national difference | Level-1 time budgets must **still differ** between countries after harmonisation. Pre-registered: the maximum pairwise difference across the **three** countries, on at least **3 of the 10** Level-1 categories, must exceed **20 min/day**. If harmonisation makes three European countries look identical, it has smoothed them together | **project-chosen**, and it is deliberately a *floor* on disagreement. 🔴 **Updated 2026-08-15 for the three-country corpus (decision 16), and the threshold was NOT touched.** Note which direction this moves: three countries give **3 pairs instead of 6**, so there are half as many chances to clear 20 min/day — **the gate becomes harder to pass, not easier.** That is why the 20 min/day and 3-of-10 figures stay exactly where they were pre-registered |
| **G2.10** Against published aggregates | The mapping being internally consistent but wrong | Harmonised Level-1 time budgets within **±10 min/day** of each country's **own published** time-use tables for that wave | **project-chosen** tolerance; the reference is external |
| **G2.11** Location class coverage | 🔴 **A whole travel mode or place class silently vanishing** — the defect D-S2-3 was written against | In `harmonised.parquet`, **every target location class is non-empty for every country.** Count of (country × class) cells with zero episodes: **0**. Escalate, additionally, if any country's weighted share of a class is **below one tenth** of the smallest share among the other **two** *(superseded: "three", decision 16)* — total elimination is the loud form, a mode surviving in one country and not its neighbours is the quiet one | **project-chosen**; the non-emptiness half is **derived** — no European country recorded a year with zero public-transport episodes |
| **G2.12** Spanish rotation round-trip | 🔴 **The cyclic rotation D-S2-5 requires, silently losing or duplicating time at the splice** | Rotating `harmonised.parquet`'s Spanish rows **back** to their native 06:00 origin must reproduce the Step 1 Spanish table exactly on `ACT`, `LOC` and every co-presence flag, for **100 %** of diaries. Mismatching diaries: **0** | **derived** — a cyclic rotation is invertible by construction, so any mismatch is a bug and not a judgement call. 🔴 **This is the executable form of D-S2-5's own requirement**, which said the rotation must be invertible and was until now stated nowhere a runner could read it |
| **G2.13** Secondary-crosswalk separateness | 🔴 **Italy's `catcon` resolved through the *primary* activity table** — the silent form of the defect D-S2-7 was written against | **0** Italian `act2` source codes may be resolved through `crosswalk_activity.csv`. Every one comes from `crosswalk_activity_secondary.csv`, and every row of the latter carries a `source_list` column naming `CLS-var13` for Italy | **derived from the codebook** — F-IT-3 states `catcon` is a different and coarser classification, *not* a truncation of `catpri`, so a mapping that resolves it through the primary list is wrong by the delivery's own documentation, not by our preference |
| **G2.15** Secondary-crosswalk agreement, Spain and the UK | 🔴 **A hand edit to one of two files the codebook says must agree.** D-S2-10 confirmed Spain's `ASECU` and the UK's `What_Oth1` are coded in their countries' **primary** activity lists, so their secondary rows are truncations of primary rows, not independent mappings | For **Spain and the UK only**: every row of `crosswalk_activity_secondary.csv` must map its source code to the same 2-digit target that `crosswalk_activity.csv` gives that code, truncated. Disagreeing rows: **0**. 🔴 **Italy is excluded from this gate by construction** — `catcon` is a different list and `G2.13` requires it to disagree | **derived from the codebook** — LAYOUT `F DIARIO2` rows 32/37 and METH p. 49 / p. 65-66 for Spain, F-UK-2 for the UK. 🔴 **This gate and `G2.13` are opposites and both must hold**: Spain and the UK must agree with the primary table, Italy must never touch it |
| **G2.16** Level-1 is derived from the target, not from the source | 🔴 **The UK's own division carried through as the harmonised Level-1.** D-S2-11: the UK codes sleep as `110`, division `1`, which in the target numbering is *Employment*. Carrying the source `group1` through puts about eight hours a day of British sleep into Employment | In `harmonised.parquet`, `act_level1 == act[0]` for **100 %** of episodes, in every country, where `act` is the 3-digit target code. Violating episodes: **0**. Additionally every `act` value must appear in the shipped `activity_target_list.csv` (`V2.h`) | **derived** — Level-1 *is* the first digit of the target code by construction, so any disagreement is a bug and not a judgement. 🔴 **It exists because `G2.9` cannot catch this**: mis-filing one country's sleep into another division makes the countries differ *more*, and `G2.9` is a floor on disagreement. `G2.10` would catch it only if a published reference table is actually obtained, which is not yet true |
| **G2.14** Co-presence value-map integrity | 🔴 **Spain's `1 = yes, 6 = no` recoded by truthiness** — `bool(6)` is `True`, so a bare cast makes every Spanish respondent co-present with everybody at once | Count of episodes where `cop_alone` is set **and** any other shared flag is also set: **0**, in every country. Additionally, every national co-presence value encountered must appear in the shipped `crosswalk_copresence.csv` value map; an unrecognised value is printed and refused (`V2.c`), never coerced | **derived from the instrument** — a respondent cannot be alone and accompanied in the same episode. 🔴 If a country's delivery genuinely permits both, that is a **finding to report before this gate is touched**, not a reason to relax it |

---

## 🔴 G2.9 AND G2.10 ARE THE TWO THAT MATTER, AND THEY PULL AGAINST EACH OTHER

G2.10 asks: did we get each country right? G2.9 asks: did we get them right *separately*?

A crosswalk can pass G2.10 on every country and still have destroyed the paper, if it did so by
mapping each country toward a common centre. And G2.9 alone can be satisfied by a broken mapping that
scatters the countries. **Neither is sufficient; both are required, and they are recorded as a pair.**

🔴 **G2.10's reference must be a published national table, not a re-tabulation of the same
microdata we are harmonising.** If the "published" figure was itself computed from the public-use
file, the reference and the target share an ancestor and the gate cannot fail. Confirm the
provenance of every reference figure before quoting the gate as evidence.

---

## EVERY GATE MUST BE SEEN FAILING

Each perturbation applies to a copy, and must break **exactly one** gate.

| Perturbation | Must fail | Must stay clean |
|---|---|---|
| Delete one row from `crosswalk_activity.csv` | G2.1 | G2.3 |
| Strip the page reference from one mapping row | G2.2 | G2.1 |
| Scale one country's durations by 1.01 | G2.3 | G2.4 (it stays proportional — verify) |
| Round one duration to the nearest 7 minutes | G2.4 | G2.3 |
| Add a one-to-many row without a rule | G2.5 | G2.1 |
| Empty the `OUTDOOR_AT_HOME` list | **G2.6** | all others |
| ~~Drop all French respondents aged 11-14~~ 🔴 **Drop all Spanish respondents aged 10-14** *(rewritten 2026-08-16: France is excluded by decision 16, so the original perturbation cannot be run at all; Spain now carries the binding age floor)* | G2.7 (attrition trigger) | G2.4 |
| Write 0 into a flag declared "not recorded" | G2.8 | all others |
| 🔴 **Map every country's activity codes to the pooled modal code** | **G2.9** | G2.3, G2.4 — *time is conserved and days still close, which is exactly why G2.9 has to exist* |
| Shift one country's sleep budget by 40 min/day | G2.10 | G2.9 |
| 🔴 **Remap every Spanish public-transport code to private transport** | **G2.11** | G2.1, G2.3, G2.4, G2.9, G2.10 — *every code still maps, time is conserved, days still close and no activity budget moves. That is the whole point: the defect is a relabelling, and a relabelling is invisible to every other gate here* |
| 🔴 **Rotate Spain the wrong way** — cyclic shift by **−2 h** instead of +2 h | **G2.12** | **all ten others** — *and this is the whole reason the perturbation is a wrong-direction rotation rather than a dropped tail. A cyclic rotation conserves every minute, closes every day at 1440, maps every code and leaves each activity's 24-hour budget **exactly** unchanged, so G2.3, G2.4, G2.9 and G2.10 cannot see it. Only Spain's phase is wrong, and only against the Step 1 table does that show* |
| 🔴 **Add Italy's `catcon` codes as rows in `crosswalk_activity.csv` and delete Italy's rows from `crosswalk_activity_secondary.csv`** | **G2.13** | G2.1, G2.3, G2.4, G2.9, G2.10 — *every code still maps, nothing is unmapped, time is conserved, days close and no primary activity budget moves. The Italian secondary field is simply relabelled through the wrong list, which is invisible to every other gate here* |
| 🔴 **Recode Spain's co-presence with `bool(x)`** (so `6`, meaning "no", becomes `True`) | **G2.14** | G2.1 through G2.11 — *no code is unmapped, time is conserved, days close, no activity budget moves and no location class empties. Every Spanish respondent is simply alone **and** with everyone at once. This is the perturbation that proves the gate was worth writing* |
| 🔴 **Re-point one Spanish secondary-crosswalk row at a different 2-digit target from the one its primary row gives** | **G2.15** | G2.13 — *Italy is untouched and still resolves through its own list*; G2.1, because the code is still mapped and still cited. **The only thing wrong is that two files the codebook says must agree no longer do** |
| 🔴 **Carry the UK's source `group1` into `act_level1` instead of deriving it from the target code** | **G2.16** | G2.1, G2.2, G2.3, G2.4, G2.9, G2.10 — *every code still maps and is still cited, time is conserved, days close, and the countries now differ **more**, so the floor-on-disagreement gate is happier, not unhappier. That inversion is the entire reason this gate exists* |
| 🔴 **Null perturbation: change nothing** | **nothing** | everything |

### Coverage clause

Cross-tab every perturbation against baseline. **The probe FAILs if any gate that passes on the real
data was never made to fall.** A perturbation set that only tests the gate it was named for will
print a complete-looking tally while a headline gate has never been exercised.

---

## VACUITY GUARDS

* **V2.a** — the runner FAILs if it harmonised fewer than **3** countries. 🔴 **Moved from 4 to 3 on
  2026-08-15 for one reason only: author decision 16 excluded France, so the corpus is three.** Like
  `V1.a`, this guard is a restatement of the corpus decision in executable form and moves only when
  that decision moves, by a dated author call. **It is not a precedent for relaxing a guard that
  fires.**
* **V2.b** — it prints, before any verdict, the number of source codes, mapped codes, unmapped codes
  and one-to-many rows it saw.
* **V2.c** — any national code, unit or field name not present in `codebook_facts_<country>.md` is
  **printed and refused**, never assumed harmless.
* **V2.d** — G2.6 is itself a vacuity guard; it must be run against the shipped exclusion list, not a
  copy inside the validator. 🔴 A second copy of a list drifts invisibly from the first — import it,
  never duplicate it.
* **V2.e** — 🔴 **G2.11 reads its class list from the shipped `crosswalk_location.csv`, and FAILs if
  that file defines fewer than the four target classes** (at-home, other place, private transport,
  public transport). Without this, deleting the public-transport class from the crosswalk would make
  G2.11 pass with nothing left to check — a gate that cannot fire, checking for a class that no longer
  exists. The class list is imported, never restated inside the validator.
* **V2.f** — 🔴 **`G2.14` reads its value map and its shared-flag list from the shipped
  `crosswalk_copresence.csv`, and FAILs if that file defines fewer than the SIX shared flags** (alone,
  partner, children, parent, other household members, other persons — D-S2-8). Exactly `V2.e`'s
  argument transplanted: a gate that checks the alone-versus-accompanied contradiction against a
  crosswalk which no longer defines "alone" passes by having nothing to look at. And 🔴 **the value map
  is imported, never restated in the validator** — a second copy of Spain's `1 = yes, 6 = no` is the
  precise place where the bug `G2.14` exists to catch would reappear on the checking side.
  🔴 **Extended 2026-08-16 by D-S3-1:** `V2.f` also FAILs if the shipped file has no `bit_position`
  column, or if its positions are not exactly `{0,1,2,3,4,5}`, one per shared flag. Step 3 packs the
  six flags into one integer and reads the bit order **from this file**; if Step 2 ships it without
  the column, the encoder will hard-code an order and `G3.14 (b)` will have nothing independent to
  check against. **The column is Step 2's responsibility because the flags are defined here**, and the
  cheapest place to catch its absence is the step that writes it.
* **V2.h** — 🔴 **`G2.16` reads the target vocabulary from the shipped `activity_target_list.csv`, and
  FAILs if that file is absent, if any target code is not exactly three digits, or if any `act` value
  in `harmonised.parquet` is not in it.** Same argument as `V2.e` and `V2.f`, third instance: a gate
  that checks membership in a list it builds itself out of the data it is auditing cannot fail. The
  list is imported, never derived from `harmonised.parquet` and never restated inside the validator.
* **V2.i** — 🔴 **The runner prints `harmonised.parquet`'s full column list before any verdict, and
  FAILs if any column name contains `origin`.** D-S2-5 prohibited a per-country origin column reaching
  Step 3, because it leaks country identity into leave-one-country-out; until now that prohibition
  existed only in prose, where no runner could read it. The native origin belongs in `filter_report.md`
  and in file-level metadata, never in a row. Printing the whole column list is the `V2.b` half: a
  column that should not be there is easiest to see next to the ones that should.
* **V2.g** — 🔴 **Italy's durations are asserted, not assumed.** `catcon`'s delivery imposes no slot and
  it is only an *observation* that every measured Italian duration is a multiple of 10 minutes
  (D-S2-6). Any Italian duration that is not a multiple of 10 is **printed and refused**, never
  rounded to the grid. A transform that silently rounds turns a data question into a clean-looking
  table.

---

## WHAT THIS STEP'S VALIDATION DOES **NOT** COVER

* It does not verify that HETUS harmonisation is *meaningful*, only that we applied it consistently.
  Whether two countries coding "eating" the same way actually observed the same behaviour is the
  paper's research question, not a gate.
* It does not test the indoor rule's **correctness**, only that it fires. Whether the exclusion list
  is the right list is a judgement against the ACL, made by a human, and recorded in the methods.
* 🔴 ~~It does not cover **secondary activities**.~~ **Partly superseded 2026-08-16 by D-S2-7.**
  `G2.13` now covers the one thing that could go silently wrong — Italy's `catcon` being resolved
  through the primary activity list. What remains uncovered is unchanged and is still worth saying:
  **the episode tuple `DUR,ACT,LOC,COP` does not carry `ACT2`**, so secondary activity is harmonised
  into `harmonised.parquet` and then not serialised. That is a Step 3 scope decision, and **this step
  is where a later step should look for the field it wants.**
* 🔴 It does not cover the **composition of `cop_parent`** — that the UK's and Italy's OR of their two
  parent columns is formed correctly, and that both components survive as extras (D-S2-8). No gate
  here fires if the OR is built from the mother column alone. **This is recorded as a hole, not
  patched**, on the same footing the D-S2-3 hole was recorded before `G2.11` closed it: a gate for it
  is proposed to the author rather than added here, and it needs its own perturbation.
* 🔴 It does not cover the **children-flag definition divergence** (Spain under-10, UK 0-7, Italy
  unbounded), and no gate can: the UK's 8-and-9-year-olds are already pooled into `WithOther` and are
  unrecoverable. It is a corpus limitation reported in the methods, and the prohibition on comparing
  that flag across countries is enforced by review, not by a runner.

---

## PROGRESS LOG

Append-only.

### 2026-08-14 — validation document created

* Ten gates, eleven perturbations, none run.
* 🔴 G2.9 is the gate this project would most easily have shipped without. Every other gate here asks
  *did we get it right*; G2.9 is the only one that asks *did we get it right without making it up*.
  It is written as a floor on disagreement precisely because the failure it catches looks like
  success in every other measurement.

### 2026-08-14 — effect of decisions D-S2-1 to D-S2-4

* **G2.8 widened, not relaxed.** The country × flag grid now covers the country-extra columns as well
  as the five shared flags (D-S2-2). An extra zero-filled for the three countries that do not field
  it is exactly the "missing collapsed into absent" defect G2.8 exists to catch, and before this
  change the extra columns sat outside the gate entirely.
* **No gate here detects the defect D-S2-3 was written against.** `RL02`'s range rule would have
  dropped every Spanish public-transport episode, and it would have passed G2.1 through G2.10: the
  codes are all mapped, time is conserved, days still close, and one missing mode moves a Level-1
  budget by less than G2.10's tolerance. **This is recorded as a hole, not patched.** A gate for it
  is proposed to the author rather than added here — the proposal is per-country non-emptiness of
  every target location class, with public transport named, and it needs its own perturbation.
* **Nothing above changes a threshold.** No band was moved, and no gate was made easier to pass.
* Still nothing built, no Step 2 gate run, none seen failing.

### 2026-08-14 — G2.11 added, on the author's word

The hole recorded in the entry above is now closed rather than left standing. Author approved,
2026-08-14.

* **G2.11 — location class coverage.** Every target location class must be non-empty for every
  country, plus a share-based escalation trigger for the quiet form. The step now has **eleven gates
  and twelve perturbations**, still none run.
* 🔴 **Its perturbation is a relabelling, not a deletion, and that is deliberate.** Deleting the
  Spanish public-transport episodes would break G2.4 as well — the day would stop summing to 1440 —
  so it would fail two gates and prove nothing about G2.11's own detection power. Remapping those
  codes to private transport conserves time, closes every day, maps every code and moves no activity
  budget. **Ten gates stay green and only G2.11 falls.** That is the measure of what was missing.
* **The non-emptiness half is derived, not project-chosen.** No European country recorded a survey
  year with zero public-transport episodes, and that reference does not come from the crosswalk being
  audited — which is the property `RL02`'s range rule never had.
* **V2.e is what keeps it from becoming vacuous.** A gate that checks four classes against a
  crosswalk which no longer defines four classes passes by having nothing to look at. The class list
  is imported from the shipped file and its length is checked before any verdict.
* **No existing gate or threshold was altered to make room for it.** Purely additive.

### 2026-08-16 — 🔴 **G2.12, G2.13, G2.14 and V2.f, V2.g added, as the executable form of D-S2-6 to D-S2-8**

The three heterogeneities were decided in the implementation document today. **A decision without a
gate is exactly what this project forbids**, so each of the three arrives here with the defect it
permits and the perturbation that proves the gate can see it. The step now has **fourteen gates and
fifteen perturbations, still none run.**

* **`G2.12` — Spanish rotation round-trip.** D-S2-5 already *required* the rotation to be invertible;
  that requirement lived nowhere a runner could read it. It is **derived, not project-chosen** — a
  cyclic rotation is invertible by construction, so a mismatch is a bug, not a judgement.
  🔴 **Its perturbation is a wrong-*direction* rotation, not a dropped tail, and that is the point:** a
  cyclic shift conserves every minute, closes every day at 1440, maps every code and leaves every
  activity's 24-hour budget *exactly* unchanged. G2.3, G2.4, G2.9 and G2.10 are structurally blind to
  it. Only Spain's phase is wrong, and only against the Step 1 table does that show. A dropped tail
  would have broken G2.4 as well and proved nothing about G2.12's own detection power — the same
  argument that shaped `G2.11`'s perturbation.
* **`G2.13` — secondary-crosswalk separateness.** Also **derived from the codebook**, not chosen:
  F-IT-3 states `catcon` is a different and coarser classification than `catpri`, *not* a truncation,
  so resolving it through the primary table is wrong by the delivery's own documentation. 🔴 **The
  defect is silent by nature** — Italian secondary codes are two digits and would mostly *find a
  match* in the primary list while meaning something else. Every other gate here stays green.
* **`G2.14` — co-presence value-map integrity.** Spain codes `1 = yes` and `6 = no`, and **`6` is
  truthy.** A recode written as `bool(x)` or `x != 0` makes every Spanish respondent alone *and* with
  everybody, on every episode, and passes G2.1 through G2.11 without a murmur: no code unmapped, time
  conserved, days closed, no budget moved, no location class emptied. **Derived from the instrument** —
  a respondent cannot be alone and accompanied in the same episode. 🔴 If a delivery turns out to
  permit both, that is a finding to report *before* the gate is touched.
* **`V2.f`** transplants `V2.e`'s argument to co-presence: the shared-flag list and the value map are
  **imported from the shipped `crosswalk_copresence.csv`**, and the guard FAILs below six flags.
  🔴 **A second copy of Spain's `1/6` map inside the validator is the precise place `G2.14`'s own bug
  would reappear on the checking side.** `V2.g` refuses any Italian duration that is not a multiple of
  10 rather than rounding it — an observation about the delivery must not become an assumption in the
  transform.
* **`G2.8` widened again, not relaxed:** the country × flag grid now covers **six** shared flags, since
  D-S2-8 promoted `cop_parent` from a supposed Spanish extra to a flag all three countries record.
* **One stale perturbation rewritten, and it could not have been run as written:** *"drop all French
  respondents aged 11-14"* becomes *"drop all Spanish respondents aged 10-14"*. France is excluded by
  decision 16 and Spain now carries the binding age floor. `G2.11`'s escalation clause likewise reads
  "the other **two**" rather than "the other three".
* **Three holes recorded rather than patched:** no gate checks that `cop_parent`'s OR is built from
  *both* national components; no gate can check the children-flag definition divergence, because the
  UK's 8-and-9-year-olds are unrecoverably pooled into `WithOther`; and Spain's within-episode `ACT2`
  disagreement rate is unmeasurable downstream. 🔴 **The first is proposed to the author, exactly as
  the D-S2-3 hole was before `G2.11` closed it. The second and third are methods-section limitations.**
* **No existing threshold was moved.** Every addition here is additive, and two of the three new gates
  are derived rather than project-chosen.

### 2026-08-16 (later) — `V2.f` extended, no gate added

D-S3-1 (Step 3) packs the six co-presence flags into one decimal integer 0-63 and reads the bit order
from `crosswalk_copresence.csv`. `V2.f` therefore also FAILs if that file ships without a
`bit_position` column, or if its positions are not exactly `{0,1,2,3,4,5}`, one per shared flag.

🔴 **This is a vacuity extension, not a new gate, and the distinction matters.** Nothing new is being
*checked about the data*; what is being checked is that the file Step 3's `G3.14 (b)` audits against
actually contains the thing it audits. A missing column would not make `G3.14 (b)` fail — it would
make it **unable to run**, which this project counts as a worse outcome than a failure because it
looks like silence rather than a problem.

**Still fourteen gates and fifteen perturbations in this step.** The count is unchanged, deliberately.

### 2026-08-16 (later) — 🔴 **`G2.15` added. It is the mirror image of `G2.13`, and both must hold**

D-S2-10 confirmed from the Spanish codebook that `ASECU` is coded in the **same** list as the primary
activity — LAYOUT `F DIARIO2` rows 32/37, METH p. 49, METH p. 65-66 — as the UK's secondary already was
(F-UK-2). Only Italy uses a separate list.

That creates a defect class nothing here could catch. For Spain and the UK, `crosswalk_activity.csv` and
`crosswalk_activity_secondary.csv` **must agree** on any code they share, because the codebook says
they are the same list. Two files required to agree, with nothing comparing them, is where a hand edit
to one of them lives forever.

**`G2.15`** — for **Spain and the UK only**, every secondary-crosswalk row maps its source to the same
2-digit target the primary crosswalk gives that code, truncated. Disagreeing rows: **0**. 🔴 **Italy is
excluded by construction**, because `G2.13` requires Italy's codes never to be resolvable through the
primary table at all.

🔴 **The two gates pull in opposite directions and that is deliberate.** `G2.13` fails if Italy's
secondary codes *can* be found in the primary list; `G2.15` fails if Spain's and the UK's *cannot*.
A single "the secondary crosswalk is consistent with the primary one" gate would have been wrong for
one country or the other, whichever way it was written — and the version that felt natural (secondary
activity has its own list, so it should never match the primary) would have been wrong for **two of the
three countries**. The generalisation was the trap; the codebooks were the way out.

**Its perturbation is narrow on purpose:** re-point one Spanish secondary row at a different 2-digit
target from its primary row. `G2.13` stays clean — Italy is untouched. `G2.1` stays clean — the code is
still mapped and still cited. **The only thing wrong is that two files which must agree no longer do**,
which is exactly the state `G2.15` exists to name.

**Also recorded, from the same evidence pass, and neither produced a gate:**

* **The UK's `WithOther` scope is now quoted rather than inferred** (data dictionary `Pos. = 45`,
  verbatim *"With other person(s) (incl. child 8+ years)"*), so `G2.8`'s reference is firmer, but its
  threshold is untouched. The children-flag divergence is still **undetectable by any gate** — Spain
  cuts at 10, the UK at 8, Italy not at all — and is still handled by prohibition, not by a check.
* 🔴 **A new `NOT STATED IN CODEBOOK`:** whether `WithOtherYK` absorbs any of the 8+ children
  population. Neither source addresses it. Recorded in the exclusions below rather than assumed
  irrelevant.
* **Spain's `ASECU` blank sentinel is single-sourced** — LAYOUT row 38 only; METH is silent across all
  127 pages. `V2.c` refuses unrecognised values regardless, so nothing depends on the blank convention
  being right, but a convention resting on one document is written down as resting on one document.

**Step 2 is now fifteen gates and sixteen perturbations, none run.**

### 2026-08-16 (later still) — 🔴 **`G2.16` and `V2.h` added, because `G2.9` is a floor and floors do not catch this**

D-S2-11 fixed the activity target as a shipped 3-digit list built from two agreeing deliveries. It also
exposed a defect class this document did not cover.

**The defect.** The UK codes sleep `110`, in its own division `1`; in the target numbering division `1`
is Employment. If the harmonisation carries the UK's source `group1` through as `act_level1` instead of
taking the first digit of the *target* code, roughly eight hours a day of British sleep is filed under
Employment.

🔴 **Every existing gate lets it through, and one of them lets it through for an instructive reason.**
`G2.1` is clean — every code still maps. `G2.2` is clean — every row still cites. `G2.3` and `G2.4` are
clean — a relabelling conserves time and still closes the day at 1440. And **`G2.9` is not merely blind
to it, it is made happier by it**: `G2.9` is a *floor* on cross-country disagreement, and mis-filing one
country's sleep into another division increases the disagreement. A gate that becomes easier to pass in
the presence of the defect is worse than no gate, because it reads as evidence. `G2.10` is the only
existing gate that would see it, and only once a published national table is actually obtained — which
has not happened.

**`G2.16`** — `act_level1 == act[0]` for **100 %** of episodes in every country, 0 violations, and every
`act` value must be present in the shipped `activity_target_list.csv`. It is **derived**, not chosen:
Level-1 *is* the first digit of the target code by construction, so a disagreement is a bug and there is
no threshold to argue about.

**Its perturbation** carries the UK's `group1` into `act_level1`. `G2.1`, `G2.2`, `G2.3`, `G2.4`, `G2.9`
and `G2.10` all stay clean, which is the point being demonstrated rather than an incidental note.

**`V2.h`** — the third instance of the same vacuity argument that produced `V2.e` and `V2.f`: `G2.16`
imports the target list from the shipped file and FAILs if it is absent, if any target code is not
exactly three digits, or if any harmonised `act` is missing from it. 🔴 **A membership gate that builds
its own reference list out of the data it audits cannot fail**, so the list is never derived from
`harmonised.parquet` and never restated inside the validator.

**What this still does not cover, said plainly:** `G2.16` proves the Level-1 column is consistent with
the 3-digit target. It does **not** prove the 3-digit target is the right one for a given UK label. That
rests on `G2.2` (the row is cited, so a human can check it) and on `G2.10` (external reference), and
`G2.10` is not yet checkable. The 277-row UK mapping is therefore the largest piece of unverified
judgement in this step, and it is recorded as such rather than covered by a gate that cannot see it.

**Step 2 is now sixteen gates, seventeen perturbations, `V2.a`-`V2.h`, none run.**

### 2026-08-16 (later still) — D-S2-12: `harmonised.parquet` has a written record contract, and `V2.i` makes one prohibition executable

`harmonised.parquet` had been named in five places in this document and specified in none. Step 1
wrote its intermediate record down and every later step gained from it; work item 2.4 could not be
handed to anyone until Step 2 did the same.

**Three choices in it are decisions rather than bookkeeping.**

🔴 **The raw fields stay.** `act_raw`, `act2_raw` and `loc_raw` ride along beside the harmonised
columns. This is the D-S2-8 argument reused: a transform that discards its inputs cannot be audited.
It also keeps `act2_raw`'s and `loc_raw`'s three states (M-1) from being flattened, which
harmonisation would otherwise do quietly.

🔴 **Two index columns and a split flag, because the rotation changes the episode count.** D-S2-5
warned that rotating Spain to 04:00 splits the episode straddling the origin, so Spain's Step 2 count
is a *different quantity* from the 430,754 `G1.1` pinned. `episode_index` is the Step 2 index,
`episode_index_step1` is Step 1's carried unchanged, and `split_at_origin` marks both halves.
**`G2.12`'s round trip is only mechanically possible because those exist** - without them, rejoining
the halves would be guesswork, and a gate whose reference has to be guessed at is not a gate.

🔴 **`origin_hour` is not a column, and that prohibition is now executable.** D-S2-5 stated it in
prose, where no runner can read it, which is the same failure mode D-S2-5's own invertibility
requirement had until `G2.12` was written. `V2.i` prints the full column list before any verdict and
FAILs on any column name containing `origin`. The native origin goes to `filter_report.md` and to
file-level metadata instead.

**Types were stated because the defaults are wrong here.** The six shared flags and every country
extra are **nullable boolean** - `null` is not-recorded, `False` is recorded-and-absent, and D-S2-2
already established that collapsing the two destroys the field paper 1 named as the source of load
overestimation. `indoor_presence` is `null`, never `False`, where `loc_raw` is recorded-and-blank.
`act` is a 3-character zero-padded **string**: `011` is not `11`, and an integer column would silently
make it so.

**No threshold was moved. Step 2 is sixteen gates, seventeen perturbations, `V2.a`-`V2.i`.**

### 2026-08-16 (overnight) — 🟢 **Work items 2.2 and 2.3 ACCEPTED**

`crosswalk_location.csv`, `outdoor_at_home.csv`, `crosswalk_copresence.csv`,
`crosswalk_unmapped_location.md` and `copresence_availability.md` are in `outputs_step2/`. Every
numeric claim below was **re-derived by the manager from the shipped CSVs**, not read off the
employee's summary.

**2.2, the location crosswalk.** 108 delivered source codes (ES 20, UK 35, IT 53); **102 mapped**
(ES 19, UK 33, IT 50), **6 left unmapped** (ES `00`; UK `90`, `99`; IT `97`, `98`, `99`) because
each label conflates two of the four target classes with nothing in the codebook to break the tie.
Reconciliation is exact per country: 20 = 19 + 1, 35 = 33 + 2, 53 = 50 + 3. **`target_class` takes
exactly the four permitted strings and nothing else; zero empty citations.** Every
(country × class) cell is non-empty — ES 1/11/6/1, UK 1/12/10/10, IT 2/34/7/7 in
at_home / other_place / private_transport / public_transport order — so **`G2.11` has no zero cell
to fire on at the vocabulary level**. 🔴 That is necessary, not sufficient: `G2.11` is stated on
*episodes*, and these are source-code counts. It is re-checked against `harmonised.parquet`.

**No code was classed by numeric range**, per D-S2-3. Seven rows carried a written rule rather than
a label match, and the two that matter are IT `12` (*"Casa propria, spazi aperti"* → `at_home`,
**deliberately reproducing the D-S2-4 merge that Spain's single code `11` already performs** — the
asymmetry is resolved *into* the merge, not around it) and IT `55` (*"Gommone, barca"* →
`private_transport`, against the separately-listed *"Nave"* in the public block).

**2.3, co-presence.** 54 rows. **`bit_position` is exactly `{0,1,2,3,4,5}` and the map to the six
shared flags is one-to-one** (`cop_alone`→0 … `cop_other_persons`→5), which is the condition
`V2.f` tests. All three countries carry all six flags; zero empty `national_definition_verbatim`,
zero empty `citation`. **Spain's `1 = yes` / `6 = no` value map is written on every Spanish row**,
not stated once in prose — a bare truthy cast of `6` would make every Spanish respondent co-present
with everyone simultaneously, which is exactly the bug `G2.14` exists to catch, and the antidote is
now data the runner reads. 🔴 **The UK's `WithMother`/`WithFather` and Italy's `cmadre`/`cpadre`
each survive twice**: once mapped into `cop_parent`, once as their own `EXTRA:` row. D-S2-8's
argument, reused: an OR that discards its inputs cannot be audited.

**`outdoor_at_home.csv` holds four codes — `322`, `341`, `342`, `344` — and that shortness is
argued, not accidental.** The manager's first reading flagged the absence of `351` (construction /
renovation), `352` (repairs) and `354` (vehicle maintenance) against this step's own indoor-rule
example, which names *"outdoor construction"*. The employee had already recorded all three, plus
ES/IT `343` and IT `353`, in a **codes-considered-and-rejected table** with a per-code reason: none
of `351`/`354` carries an exterior qualifier the way `322` carries *"exteriores de la vivienda"* /
*"parti esterne"*, and **IT `352` says *"riparazioni **nella** propria abitazione"* — explicitly
*inside*, so it is excluded on positive evidence rather than on doubt.** The list stays at four.
An outdoor-construction code that no delivered national list actually carries is recorded as a gap;
it is not conjured by promoting an ambiguous code, which is D-S2-3's argument again.

Code `342` is the one genuinely borderline inclusion and is labelled as such: Spain's
*"Cuidado de animales domésticos"* is ambiguous alone, and it was included because Italy's label at
the **same code under the shared D-S2-11 numbering** reads *"animali da cortile/allevamento"*.
ES/IT `343` (pets) is excluded on the same contrast. **All four codes were confirmed by the manager
to exist in the shipped `activity_target_list.csv`** — the cross-employee check that no single
employee could perform.

🔴 **The one real limitation, and it is the employee's own disclosure.** The delivered inputs for
this task were the `codebook_facts_*.md` summaries, **not** the Spanish LAYOUT workbook, the METH
PDF, or the Italian TRACC-DG files. So the UK's `national_definition_verbatim` cells *are* literal
DD variable-label quotes, while **most Spanish and Italian cells are a verbatim field name plus an
attributed gloss, each labelled as not a literal codebook sentence.** That was the right call — the
alternatives were fabricating Spanish and Italian codebook prose, or leaving a column blank that the
contract requires — but it stands as unverified against the primary source, and it is recorded here
rather than smoothed over so that a later reader does not mistake the column for a quotation.


---

## 🔴 DECIDED 2026-08-16 (overnight) — D-S2-13: THE AGE FLOOR IS **11**, BECAUSE ITALY CANNOT EXPRESS **10**

### The finding

Work item 2.4 says *"Filter: age ≥ 10"*, derived as the highest of the participating minima
(ES **10**, UK **8**, IT **3**). **That filter is not evaluable on Italy.**

`codebook_facts_italy.md`, F-IT-2: ISTAT applied statistical disclosure control to this public-use
file, and among the recodings, age was collapsed into `claseta2`'s eleven bands — *"which is why no
exact age variable exists in this delivery at all"*. The bands were read directly from
`METADATI/Classificazioni/uso_tempo_Classificazione_Anno 2013_Individui_var20.html`:

```
01  fino a 2       05  15-24      09  55-64
02  3-5            06  25-34      10  65-74
03  6-10           07  35-44      11  75 e piu'
04  11-14          08  45-54
```

🔴 **Band `03` is `6-10`. The floor of 10 falls strictly inside it.** Ages 6, 7, 8 and 9 fail the
filter and age 10 passes, and Italy's delivery cannot tell them apart. Spain's `EDAD` and the UK's
`DVAge` are exact integers, so the filter is exactly evaluable there and only there.

### Why the two obvious repairs are both wrong

* **Drop band `03` for Italy, keep the floor at 10.** Italy then starts at 11 while Spain and the UK
  keep their 10-year-olds. That is a **country-correlated difference in age support at the
  boundary** — manufactured by our own filter, not by the source surveys — arriving in a
  leave-one-country-out design. It is the same class of leak `V2.i` exists to stop when it forbids
  an `origin` column.
* **Keep band `03` for Italy, keep the floor at 10.** Italy then contributes 6-, 7-, 8- and
  9-year-olds — ages **Spain structurally cannot supply**, its own minimum being 10. Same leak, other
  direction, and this one also silently breaks the filter's stated meaning.

### The decision, and the rule it comes from

The age floor exists so that **every country can supply every age the corpus contains**. Under
disclosure control that guarantee needs one more clause, because a country can fail to supply an age
either by not surveying it or by not being able to *name* it:

> 🔴 **The harmonised age floor is the lowest age that every participating country can both supply
> and express exactly.** Take the highest of the participating minimum ages; then, if that value
> falls strictly inside a band in any country's delivered age variable, raise the floor to the first
> value that *begins* a band in that country.

Applied: the highest minimum is **10** (Spain). 10 falls strictly inside Italy's band `03` (`6-10`).
Italy's next band, `04`, begins at **11**. **The floor is 11.** It is exactly expressible in all
three countries — Italy as `claseta2 >= "04"`, Spain as `EDAD >= 11`, the UK as `DVAge >= 11` — and
all three can supply it.

### What this reverses, and what it does not

🔴 **This moves the floor back from 10 to 11 and therefore reverses the 11 → 10 move made with
decision 16.** It must be read by the author, and it is written here rather than buried in a runner.
But note precisely what it is and is not:

* It is **not** the France rule returning. 11 was France's minimum age; that is a coincidence of
  arithmetic. This 11 comes from Italian disclosure-control banding and would hold with France
  permanently gone.
* It is **not a relaxed threshold.** It is *more* restrictive than 10, it removes respondents rather
  than admitting them, and **it cannot be motivated by making any gate pass** — no gate has been run
  on harmonised data yet, so there is nothing here that could have been fitted to a result. This is
  the distinction the standing rule against moving thresholds is protecting, and it is on the right
  side of it.
* It is **reversible at zero cost**: the runner takes the floor as a command-line parameter with no
  default, `filter_report.md` prints the floor it used and the per-country expression it compiled it
  into, and the loss from raising 10 → 11 is counted per country so the price is visible rather than
  argued.

**Consequences for 2.4.** `filter_report.md` must additionally report, per country, the respondents
removed by the age clause **and** — for Italy alone — a line stating that the clause was evaluated on
a band, naming the band, so that no later reader mistakes Italy's age filter for an exact one.
*(Supersedes: "Filter: age ≥ 10" in work item 2.4.)*


---

### 2026-08-16 (overnight) — 🟢 **Work item 2.1 ACCEPTED**, and `crosswalk_unmapped.md` assembled

`crosswalk_activity.csv`, `crosswalk_activity_secondary.csv` and `crosswalk_unmapped_activity.md`
are in `outputs_step2/`, alongside the `activity_target_list.csv` D-S2-11 requires. **Every figure
below was re-derived by the manager from the shipped CSVs**, before and again after the correction
described at the end.

**The target vocabulary is a shipped file, not an assumption.** `activity_target_list.csv` holds
**158 three-digit target codes**, every one exactly three characters, with `level1 == target_code[0]`
and `level2 == target_code[:2]` on all 158 rows — **the shipped vocabulary already satisfies
`G2.16`'s own condition on itself**, before a single episode is harmonised. Evidence is declared per
row: **86 `two_source`**, **55 `single_source`**, **17 `conflict_resolved`**.

🔴 **The 55 single-source rows are a deviation from D-S2-11 as literally written** — "two citations
per row" — and they are declared as such in a column rather than smoothed into looking like
agreement. **The 17 conflict rows are the ones that mattered**, because a conflict resolved without
a written rule is precisely where an arbitrary heuristic hides. All seventeen carry both national
labels verbatim and a written resolution. Two examples of the kind of thing they contain: code `121`
is *"Pausa para la comida"* in Spain and *"Secondo lavoro"* in Italy; code `111` is main **and**
secondary job in Spain but main job only in Italy, so target `111` took Italy's narrower meaning and
Spain's scope-broadening is recorded as a limitation rather than hidden inside an equals sign.

**The crosswalk itself.** 531 rows — ES 114, IT 144, UK 273. Manager checks, all independent of the
employee's own:

* **Every one of the 531 target codes exists in `activity_target_list.csv`.** Zero orphans.
* **Zero one-to-many mappings.** Work item 2.1 requires a one-to-many mapping to carry a written
  rule; there are none to carry one.
* **Every target code is exactly three characters.**
* **16 rows flagged `ambiguous=1`, each with a written rule** — 14 of them the UK's, chiefly its
  top-level *"unspecified X"* catch-alls (`0`, `1000`, `4000`, `5000`, `6000`, `7000`, `8000`).
* Counts reconcile exactly per country: ES 116 = 114 + 2, IT 146 = 144 + 2, UK 277 = 273 + 4.

**The secondary crosswalk is genuinely separate, and that is now demonstrated rather than asserted.**
421 rows. `G2.15` — for Spain and the UK the secondary target must agree with the primary crosswalk —
holds with **zero violations across all 387 ES/UK rows**. `G2.13`'s opposite requirement holds too:
**Italy's 34 secondary codes come from `CLS-var13` and share exactly zero codes with Italy's own 144
primary source codes.** D-S2-7 predicted `catcon` is not a truncation of `catpri`; the intersection
is empty, which is the strongest form that prediction could take.

🔴 **One correction was required before acceptance, and it is recorded because of what it was.** The
first delivery mapped the UK's `1310` *"Lunch break"* to target `139` while leaving Spain's `121`
*"Pausa para la comida"* — the same concept — **unmapped**. Both rationales were individually true,
and together they were incoherent: either `139` is an adequate home for a lunch break or it is not.
As shipped it would have meant **Spain silently loses its lunch-break episodes while the UK keeps
them**, a country-correlated difference in the harmonised data manufactured by our own crosswalk and
not by any source survey — arriving in a leave-one-country-out design, which is exactly where a
country-shaped artefact does its damage. The employee was told the two treatments must match and was
**not** told which to choose. Resolution: ES `121` → `139`, `ambiguous=1`, matching UK `1310`, with
cross-referencing rules on both rows; Italy was checked for the same concept and has no primary
lunch-break code, its secondary `CLS-var13` code `11` *"Pausa pranzo"* already being handled. Counts
moved to ES 114 mapped / 2 unmapped and 531 rows / 16 ambiguous / 8 unmapped, and the manager
re-ran every check above against the corrected files.

**`crosswalk_unmapped.md` now exists**, assembled by the manager from the two employee documents,
which stay in place as the citable originals. It is the single register `G2.1` reads: **8 unmapped
activity codes and 6 unmapped location codes, 14 in all**, each with a reason. The activity eight are
Spain's `399` and `900`, Italy's `90` and `997`, and the UK's `9000`, `9940`, `9980` and `9999` —
almost all of them diary-quality markers (*"illegible activity"*, *"queryable"*, *"a phrase that does
not describe an activity"*) rather than activities, which is the right thing for a target vocabulary
of real activities not to contain. 🔴 **Each yields a `null` in `act`, and the null is readable
precisely because the code is listed here.** Nothing is dropped.

**Step 2's four crosswalks are now all built and accepted.** The remaining work is 2.4 and the gate
runner.


---

## ⏳ STEP 2 — the gate runner is now in flight too, 2026-08-16 overnight

Task doc: `Prompts/4thJ_employee_step2_gates_2026-08-16.md`. Builds
`tools/4thJ_gates_step2.py` — **sixteen gates, seventeen perturbations, nine guards `V2.a`-`V2.i`,
one coverage clause.**

It is deliberately sequenced **behind** 2.4 but started **now**: the employee writes the whole
runner, unit-tests it against a small synthetic parquet built by hand to the D-S2-12 contract,
**demonstrates it can make each gate fail on demand**, then waits for the manager to clear it against
the real `harmonised.parquet`. A gate nobody has seen fail is not known to work, and that can be
established before the data exists.

**Two things the task doc pins down that are easy to get wrong later:**

* 🔴 **`G2.10` has no published national reference table in our hands.** It is `NOT CHECKED` with that
  one-line reason and stays **outside the scored set**. The employee is forbidden to substitute a
  re-tabulation of our own data — a gate whose reference derives from the source it audits cannot
  fail, so a green `G2.10` built that way would be worse than an unchecked one.
* 🔴 **`G2.13` and `G2.15` are opposites and both must hold.** Italy's `act2` must resolve *only*
  through the secondary crosswalk; Spain's and the UK's secondary rows must *agree* with the primary
  table truncated. A single "the secondary crosswalk is consistent" gate would silently pick one and
  drop the other.

The recurring instruction across `V2.d`/`V2.e`/`V2.f`/`V2.h` — **import the shipped list, never
restate it in the validator** — is the one that matters most, and the shipped files are all in place
to be imported: `outdoor_at_home.csv`, `crosswalk_location.csv`'s `target_class`,
`crosswalk_copresence.csv`'s six flags + value map + `bit_position`, `activity_target_list.csv`.


---

## 🔴 DECIDED 2026-08-16 (overnight) — D-S2-14: `start_min` HAS A PER-COUNTRY REFERENCE POINT, AND STEP 1 NEVER STATED IT

### The finding, raised by the 2.4 employee and re-measured by the manager

D-S2-5 gives the rotation as `offset = (native_origin_hour - 4) * 60`, which is **0 for Italy**
because Italy's diary origin is 04:00. That formula silently assumes `start_min == 0` means the
diary's own origin. **For Italy it does not.**

Measured directly on `episodes_italy.parquet`, and confirmed by the manager on all three countries:

| country | first episode's `start_min`, every diary | max `start_min` | max `start + duration` | rows ending past 1440 | diaries summing to 1440 |
|---|---|---|---|---|---|
| Spain | **0** (19,295 / 19,295) | 1430 | 1440 | **0** | 19,295 / 19,295 |
| UK | **0** (16,533 / 16,533) | 1430 | 1440 | **0** | 16,533 / 16,533 |
| **Italy** | **240** (41,229 / 41,229) | 1430 | **1680** | **35,060** | 41,229 / 41,229 |

🔴 **Italy's `start_min` is wall-clock minutes since midnight**, carried through from the raw
`oraini*60 + minini`, and never re-based to the diary's own 04:00 start. `240` is 04:00. The 1680
maximum is 04:00 the following day. The 35,060 rows ending past 1440 are the one-per-diary episode
that crosses midnight. Spain and the UK are diary-relative; Italy is not.

**With D-S2-5's formula as written, the runner produced 32,161 spurious Italian "splits"** and stopped
on its own guard rather than absorbing them — which is the guard working. Every Italian diary still
sums to exactly 1440, so **no time was lost at Step 1 and nothing already accepted is invalidated**:
`G1.1`'s Spanish 430,754 is untouched, and Italy's duration closure holds under either reading. The
information is intact; only its reference point was unstated.

### Why this was invisible until now

Step 1's record contract names `start_min` and never says **what minute zero means**. A convention
that is never written down cannot be checked, so no Step 1 gate could have failed on this — it is the
same shape as a gate whose reference derives from the source it audits. **This is recorded as a real
gap in the Step 1 contract**, and it is exactly the sort of thing that only surfaces when a second
step tries to use the field for arithmetic.

### The decision

**The reference point is a declared per-country property, and the rotation offset is derived from it
rather than from the diary origin alone.** Let `reference_minutes` be the wall-clock time that
`start_min == 0` denotes:

```
reference_minutes:  ES 360 (06:00)   UK 240 (04:00)   IT 0 (00:00)
offset      = (reference_minutes - 240) mod 1440
new_start   = (start_min + offset)     mod 1440
```

which yields **ES +120, UK 0, IT +1200 (equivalently −240)**. The two countries D-S2-5 got right stay
exactly as they were — this **generalises** D-S2-5, it does not overturn it. D-S2-5's arithmetic was
correct wherever the reference happened to coincide with the diary origin, which was true for Spain
and the UK and false for Italy.

🔴 **The correction is self-testing, and that is why it is safe to make.** It predicts **exactly zero
Italian splits**: Italy's diary runs 240 → 1680, which maps to 0 → 1440 and therefore straddles
nothing. If the corrected runner reports any Italian split at all, the correction is wrong and must
come back here. Spain still splits — its 06:00 origin genuinely straddles 04:00 — and the UK still
does not.

**The runner asserts the reference rather than trusting this table**: for each country it checks that
every diary's `episode_index == 0` episode starts at the declared `reference`-relative value
(ES 0, UK 0, **IT 240**), and 🔴 **that the rotated intervals tile `[0, 1440)` exactly once per
diary**. That tiling assertion is the general invariant; it would have caught this at Step 1 had the
contract stated a reference at all.

*(Generalises, does not supersede, D-S2-5's offset formula.)*

---

## 🔴 DECIDED 2026-08-16 (overnight) — D-S2-15: `V2.i` AS WRITTEN REJECTS THE RECORD CONTRACT'S OWN COLUMN

`V2.i` says it **"FAILs if any column name contains `origin`."** D-S2-12 requires the column
**`split_at_origin`**. As written, the guard fails the contract it is guarding — and `G2.12`'s round
trip is only mechanically possible because `split_at_origin` exists, so obeying `V2.i` literally
would take out the rotation gate with it. Found by the 2.4 employee against its own pre-write
assertion.

**Decision.** `V2.i` fails on any column name containing `origin` **other than the exact name
`split_at_origin`**, and 🔴 **it additionally FAILs if `split_at_origin` is absent.** The exception is
turned into a positive requirement so it cannot become a hole.

**This is a correction, not a relaxation, and the distinction is checkable.** What `V2.i` exists to
stop is a **per-country origin value** reaching Step 3 and leaking country identity into
leave-one-country-out — `origin_hour` and anything like it. `split_at_origin` is a per-episode boolean
that carries no country-specific value and is required by the contract. The leak stays closed;
`origin_hour` is still refused. Nothing was widened to make a failing thing pass — the guard had
never been run.

*(Amends `V2.i` in `4thJ_02_harmonisation_val.md`. The Step 2 gate runner implements the amended
form.)*


---

### 2026-08-16 (overnight) — 🟢 **Work item 2.4 ACCEPTED**, with one column set reversed and the UK re-running

`harmonised.parquet` exists: **2,024,068 episodes** — ES 446,547, UK 567,381, IT 1,010,140 — plus
`filter_report.md` and `tools/4thJ_harmonise_step2.py`. Three unchained `sbatch` jobs, age floor
**11** passed as a parameter with no default. **Every figure below was re-derived by the manager from
the parquet itself, not read off the report.**

**The reconciliation closes exactly**: input 2,096,043 − age-removed 90,890 + splits 18,915 =
**2,024,068 = output**.

🔴 **D-S2-14's self-test passed on the first attempt, and this is the load-bearing result of the
night.** The correction predicted **exactly zero Italian splits**, and Italy returned zero — with
37,830 Spanish split half-rows and zero for the UK, which is precisely the pattern a 06:00 origin
rotated to 04:00 produces and a 04:00 origin does not. Italy's two new assertions both passed:
**all 38,260 diaries start at `start_min` 240**, and **every diary's rotated intervals partition
`[0, 1440)` once, no gaps and no overlaps.** The manager independently confirmed the tiling across
**all 73,254 diaries in all three countries**, with `min(start_min) = 0` and
`max(start_min + duration_min) = 1440`. A correction that stakes itself on a number and then hits it
is worth more than one that is merely argued.

**Gate conditions already satisfiable on the shipped table** (checked by the manager, though the
battery has not run):

* **`G2.16`** — `act_level1 == act[0]` and `act_level2 == act[:2]` on **all 2,015,359 non-null `act`
  episodes, zero mismatches**, every code exactly three characters, every value a member of the
  shipped `activity_target_list.csv`.
* **`G2.11`** — 🔴 **zero empty (country × class) cells on *episodes***, which is the gate's actual
  condition. The crosswalk-level check recorded when 2.2 was accepted was necessary but not
  sufficient; this is the sufficient one. The smallest cell is Spanish public transport at 3,808
  episodes — small, and not zero.
* **`G2.14`** — **zero alone-and-accompanied contradictions in all three countries.** 🔴 And the
  number that proves the gate was worth writing: **Spain's `cop_alone` is `True` on 0.350 of
  episodes**, not the near-1.0 that `bool(6)` would have produced. The value map was read from the
  shipped crosswalk and applied; it was not truthy-cast.
* **`V2.i`** (amended form, D-S2-15) — the only column containing `origin` is `split_at_origin`, and
  it is present.
* **Nullable booleans behaved**: the UK carries **68,464 episodes null across all six shared flags**
  — `WithMiss` expressed as missingness rather than as a presence category — while Spain and Italy,
  which field all six, carry none. Missing was not collapsed into absent.

**Two employee judgement calls confirmed by the manager.** `indoor_presence` is `null` wherever `act`
is null, because `act NOT IN OUTDOOR_AT_HOME` is not evaluable on an unknown activity and `False`
would assert "not indoors" on no evidence. `WithMiss` stays missingness and does not become a
`cop_extra` column, since the shipped crosswalk tags it `NOT_A_PRESENCE_FLAG`.

🔴 **One employee decision was reversed: four recorded UK columns must not be dropped.** The runner
excluded `act2_extra_uk_2`, `act2_extra_uk_3`, `weight_dia_a` and `weight_dia_b` on the reading that
D-S2-12's column list is a closed enumeration, and flagged the tension with D-S2-7's prose rather
than burying it. **The list is not closed** — it already ends `cop_extra_<country>_<field> ...`, a
pattern rather than a name — and the principle underneath it is the one this project has now invoked
three times: **a transform that discards its inputs cannot be audited.** It is why the three `*_raw`
columns ride along at all. Dropping four recorded fields at the Step 2 boundary also **pre-empts a
question D-S2-7 explicitly reserves for Step 3**: Step 1 decides what is kept, Step 3 decides what is
serialised, and Step 2 is not the place to answer the second. The UK alone re-runs carrying them;
Spain and Italy are untouched. **The re-run must return exactly 567,381 rows and exactly 0 splits —
adding columns may not move a single row.**

🔴 **A state overload to record before anyone reads `act2` as documented.** D-S2-12 says `act2` null
means *not recorded*. In the shipped table **587 episodes (57 Spanish, 530 UK) are null because a
recorded secondary code did not map** — a different state wearing the same value. No fourth state is
being added: the distinction is recoverable from `act2_raw`, which is carried for exactly this
purpose, so D-S2-12's own argument is doing its job. But it is written down here because a later
reader treating `act2 IS NULL` as "the instrument did not field it" would be wrong 587 times.

**Also inherited from Step 1 and disclosed rather than patched**: `act2_raw`'s *not recorded* state
occurs **zero times in all three countries**. Spain's `ASECU` and Italy's `catcon` are fixed-width
fields with a blank convention only, and the UK's genuine `-9` sentinel was already folded into the
blank state by Step 1's own documented choice — zero literal `-9` values survive in 587,632 UK rows.
**Acceptance test 5 is therefore a partial pass, and is reported as one rather than as a pass.**

**The age floor cost, now measured** (D-S2-13): the age clause removed **155 Spanish respondents /
3,122 episodes**, **340 UK respondents / 20,251 episodes**, and **2,969 Italian respondents / 67,517
episodes**. Italy's larger loss is the band effect and is exactly what D-S2-13 predicted it would be —
`claseta2 >= "04"` removes the whole `6-10` band, and `filter_report.md` carries the required line
saying so in terms, so no later reader mistakes Italy's age filter for an exact one.


### 2026-08-16 (overnight, later) — the UK re-run landed; **2.4 is closed** and the gate runner is cleared

The UK re-ran alone (job 1252983) carrying `act2_extra_uk_2`, `act2_extra_uk_3`, `weight_dia_a` and
`weight_dia_b`. Manager re-verification of the rebuilt `harmonised.parquet`:

* **2,024,068 rows, 40 columns** — ES 446,547, **UK 567,381 (unchanged to the row)**, IT 1,010,140.
* **Splits ES 37,830 / IT 0 / UK 0** — unchanged.
* **All 73,254 diaries still tile `[0,1440)`**; `G2.16` still zero mismatches; `act2` nulls still 587.
* All four columns present; the only column containing `origin` is still `split_at_origin`.

🔴 **That is the point of the check: adding four columns moved zero rows.** A re-run that had shifted
a single episode would have meant the column set was entangled with the transform, and the whole
delivery would have gone back.

Disclosure lines were added to every `filter_report_*.md` fragment for the `indoor_presence` nulls
(**ES 290, UK 18,325, IT 8,112**) and for the `act2` overload, plus a dedicated section in
`filter_report.md` stating that **all 587 `act2 = null` episodes are the unmapped-code case and none
is the not-recorded case**, with the instruction to separate them via `act2_raw`.

**Work item 2.4 is closed. Step 2's only remaining work is the validation battery**, which has been
cleared against this table with the six baseline measurements above handed over **as independent
targets to reproduce, not as numbers to reconcile to** — a battery that agrees with the manager
because it was told the answer is not a battery.


---

### 2026-08-16 (overnight) — 🟢 **THE STEP 2 BATTERY RAN. 15 of 15 scored gates PASS, 15 of 15 SEEN FAILING, coverage satisfied.**

`tools/4thJ_gates_step2.py`, run against the real 2,024,068-row `harmonised.parquet`. Reports in
`Step2_docs/gates_step2_out/real_run/`. **The manager read the reports directly rather than a
summary.**

**Baseline: all nine vacuity guards PASS, all fifteen scored gates PASS, `G2.10` `NOT CHECKED`.**

| | |
|---|---|
| `G2.3` mass conservation | max relative diff **1.3e-16** — exact to floating point |
| `G2.4` day closure | **0** diaries off 1440; **0** failing the D-S2-14 tiling invariant |
| `G2.6` indoor-rule reachability | fires in **all three** countries — ES 1,704, UK 3,883, IT 4,849 |
| `G2.7` attrition | **0** escalations; removed ES 0.803 %, UK 4.107 %, IT 7.201 % |
| `G2.9` cross-country divergence | **6 of 10** Level-1 categories exceed 20 min/day, floor is 3 |
| `G2.11` location coverage | **0** empty (country × class) cells, 0 escalations |
| `G2.12` Spanish round-trip | **0** mismatching diaries and episodes |
| `G2.14` co-presence integrity | **0** contradictory episodes |
| `G2.16` Level-1 derivation | **0** mismatches, **0** `act` values outside the shipped target list |

🔴 **`G2.9` is the one to read twice.** It is a *floor* on disagreement, and 6 of 10 categories clear
20 min/day against a requirement of 3. **Harmonisation did not smooth three European countries into
each other** — which is the failure this project would most easily have shipped without noticing,
because every other gate here asks whether we got it right and only `G2.9` asks whether we got it
right *without making it up*.

🔴 **`G2.12` deserves its own line for what it declined to do.** It reports 0 mismatches *and*
separately reports that **155 whole Spanish diaries present in Step 1 are absent from
`harmonised.parquet`** — the age filter — and refuses to count them as rotation mismatches. A
round-trip gate that had counted a filtered diary as a bug would have produced 155 phantom failures
and taught us to distrust it.

**The perturbation sweep: 17 ran, the null one moved nothing, and every scored gate was made to
fall.**

```
gates that PASS at baseline and were NEVER made to fall: []
coverage clause: PASS
```

`shift_sleep_budget` reports **`DID NOT FIRE`** against `G2.10`, correctly: a perturbation cannot
fell a gate that is not being scored. **That is the honest reading and it is recorded as `DID NOT
FIRE`, not quietly dropped** — the same discipline that keeps `G2.10` itself at `NOT CHECKED` rather
than green.

🔴 **`G2.10` stays `NOT CHECKED`, with its reason, outside the fifteen-gate tally.** We hold no
published national time-use table. A re-tabulation of our own harmonised data would share an ancestor
with the thing it audits and could not fail, so it was not substituted. **An unchecked gate is worth
more than a gate that cannot fail.**

### 🔴 What the sweep found out about the perturbation table itself

**One clean-violation, and the spec asked for it.** The `scale_duration` row predicts `G2.3` falls
while `G2.4` stays clean, with the parenthetical *"(it stays proportional — verify)"*. **Verified,
and the prediction is wrong**: scaling a country's durations by 1.01 puts the day at 1454.4, so
`G2.4`'s closure must break — 38,260 diaries on real data, and the same result on synthetic fixtures.

**The perturbation was NOT adjusted.** The standing rule is that a perturbation is never edited
because of its result, and this is exactly the case it protects. **The consequence is recorded
instead: `G2.3` is never demonstrated to fall independently of `G2.4`.** Every scenario in the table
that breaks mass conservation also breaks day closure, so `G2.3`'s detection power is real but not
isolated. A perturbation corrupting **weights** rather than durations would isolate it — it would
change total weighted minutes while leaving every day summing to 1440. 🔴 **That is a recommendation
for the author, not a change made here**: adding a row to a pre-registered table is the author's call.

**Three further side effects, visible in the cross-tab and not caught by the acceptance tests
because the table does not list them as must-stay-clean.** They are recorded so nobody later reads
them as defects:

* **`shift_sleep_budget` also fells `G2.4`** — moving a sleep budget by 40 min/day breaks the 1440
  closure. Second perturbation in the table whose blast radius was not anticipated.
* **`pool_modal_code` also fells `G2.6`** — mapping every activity to the pooled modal code means the
  `OUTDOOR_AT_HOME` list can never fire, so the vacuity guard on the rule correctly reports that the
  rule has stopped doing anything. The guard is working, not failing.
* **`spain_cop_bool` also fells `G2.12`** — the round-trip compares every co-presence flag, so
  corrupting Spain's co-presence necessarily breaks it. By design.

**`V2.g` FAILs under both duration perturbations** (Italian durations stop being multiples of 10).
A guard firing under a perturbation aimed elsewhere is information about blast radius, **not a gate
failure**, and is recorded here so it is not misread as one.

**Step 2's definition of done is met on all five points.** Four crosswalks cited and complete; the
indoor rule implemented with its exclusion list stored as data and imported by the validator rather
than restated; co-presence availability documented with missing distinguished from absent;
`harmonised.parquet` and `filter_report.md` emitted; and **all gates PASS with each one seen
failing.**


---

## 🔴 DECIDED 2026-08-16 (overnight) — D-S2-16: `country` IS LOWERCASE FROM STEP 3 ONWARD, AND THE JOIN MUST ASSERT IT MATCHED

### The near-miss

The gate employee disclosed it rather than absorbing it, which is the only reason it is here:
**`harmonised.parquet`'s `country` column holds `ES` / `UK` / `IT`, and every crosswalk file holds
`es` / `uk` / `it`.** The validator lowercases both sides before any comparison.

🔴 **Un-normalised, every gate would have found zero rows for every country and PASSED VACUOUSLY.**
That is a far worse failure than the mismatch itself: sixteen green gates, a clean coverage cross-tab,
and nothing actually checked. It would have looked exactly like the result we got.

**No vacuity guard would have caught it.** `V2.a` counts the countries present in
`harmonised.parquet` — three, correctly — and says nothing about whether the *join* matched anything.
`V2.b` prints crosswalk counts, also correct on their own. Every guard we wrote checks an artefact in
isolation; **none checks that two artefacts actually met.**

### The decision

1. **`country` is lowercase — `es`, `uk`, `it` — in every artefact from Step 3 onward.** Step 2's
   shipped `harmonised.parquet` keeps `ES`/`UK`/`IT` rather than being rewritten: the file is
   validated, and a cosmetic rewrite would invalidate a battery result that took the whole night to
   earn. **Step 3's loader lowercases on read**, and this line is why.
2. 🔴 **Any join between a national artefact and a crosswalk must assert it matched.** The rule, and
   it generalises past this instance: *after joining, the number of distinct join-key values that
   matched must be non-zero for every country, and the runner FAILs if it is not.* A join that
   silently matches nothing is the vacuity failure mode our guards were not built to see, and it is
   cheaper to assert than to detect after the fact.
3. **Recommended for the Step 3 battery: a guard of the `V3.x` family stating exactly that.** 🔴 Not
   added to Step 2's `V2.a`-`V2.i` here — Step 2's battery has run and its guard set is closed;
   reopening it retroactively to add a guard that would have passed anyway buys nothing and costs the
   result its provenance.

### Two smaller carries from the same fragment

* 🔴 **`G2.12`'s Spanish co-presence column lookup is hardcoded** (`cop_solo`, `cop_pareja`,
  `cop_menor`, `cop_extra_es_padres`, `cop_otmh`, `cop_otcon`) and **fails silently**: if Step 1 ever
  renames those columns, the reconstruction produces all-null flags and `G2.12` reports spurious
  mismatches rather than an error. It is a column-address lookup, not a value map — the `1=yes/6=no`
  map is still imported from the shipped crosswalk — but it is the one place in the battery where a
  rename degrades into a wrong answer instead of a loud one.
* **`G2.11`'s escalation share uses `weight_dia`.** The val doc says only "weighted"; the employee
  chose the diary-level weight to match every other diary-level aggregate in the runner, and flagged
  it rather than assuming. **Author's call if it should be `weight_ind`** — it changes no verdict at
  baseline, where the escalation count is 0.

---

### 2026-08-16 (overnight) — 🟢 **STEP 2 IS CLOSED**

All five points of the definition of done are met, and the evidence for each is in this log above:
four crosswalks with every row cited and every unmapped code registered; the indoor rule implemented
with its exclusion list stored as data and **imported** by the validator rather than restated;
co-presence availability documented with missing distinguished from absent; `harmonised.parquet`
(2,024,068 episodes) and `filter_report.md` emitted with removals counted per clause per country; and
**fifteen scored gates PASS with all fifteen seen failing.**

🔴 **Standing Step-2 state to quote wherever Step 2 is cited:**

* **`G2.10` is `NOT CHECKED`**, not passed — we hold no published national time-use table, and a
  re-tabulation of our own data would share an ancestor with the thing it audits.
* **`G2.3` is not demonstrated independently of `G2.4`** — the `scale_duration` perturbation fells
  both, and the pre-registered table has no perturbation that isolates mass conservation.
* **The age floor is 11, not 10** (D-S2-13), because Italy's disclosure-control banding cannot express
  10. This reverses decision 16's 11 → 10 move and is **awaiting the author's confirmation**.
* **`act2 IS NULL` is overloaded** for 587 episodes, resolvable from `act2_raw`.
* **`act2_raw`'s *not recorded* state occurs zero times** in all three countries, inherited from
  Step 1.

**Step 3 is unblocked.** It consumes `harmonised.parquet`, and `crosswalk_copresence.csv`'s
`bit_position` column is present and verified `{0,...,5}` one-to-one, which is what `G3.14 (b)` needs
as a reference the encoder did not author.

