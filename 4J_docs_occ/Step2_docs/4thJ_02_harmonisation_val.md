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
