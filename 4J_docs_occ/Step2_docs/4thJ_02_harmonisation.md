# Step 2 — Harmonisation

### 4J HETUS LLM pipeline. Implementation specification.
#### Parent: `../4thJ_00_HETUS_LLM_Pipeline.md` Step 2. Validation: `4thJ_02_harmonisation_val.md`

---

## STATUS

**OPEN. Specified by `RL02`, adjudicated in part by `RL17`. Nothing built.**

---

## AIM

Turn **three** national episode tables into **one alphabet** *(superseded: "four", decision 16
excluded France)*: a single activity code list, a single
location code list, a single co-presence representation, a single time grid, one filter rule.

This step is where the paper's premise becomes real or fails quietly. If harmonisation is wrong, the
model learns four dialects and the transfer claim measures our mapping rather than HETUS's.

---

## WHAT IS ALREADY DECIDED — DO NOT RELITIGATE

| Decision | Source |
|---|---|
| **The `ACT` field keeps 3 digits** | Author decision 6. One wave per country, all four sharing one coding-list generation, so nothing spans the ACL 2000 break |
| Activity coding: 10 major groups, 36 two-digit subdivisions, identical between the 2008 and 2018 editions | `RL02` |
| ~~Location: 10-19 stationary, 20-39 transport, in one field.~~ **Retracted — see D-S2-3.** **11 = Home** stands | `RL02`, half of it falsified by the Spanish codebook |
| ~~Co-presence is **five binary flags**~~ **Five is the shared core, not the ceiling — see D-S2-2** | `RL02`, corrected by the Spanish codebook |
| 🔴 **Location 11 merges dwelling + yard + garden** | `RL02`, confirmed on the Spanish file and widened — see D-S2-4 |
| Indoor rule: `indoor = (LOC == 11) AND (ACT not in {gardening, outdoor construction, ...})` | `RL02`, adopted |
| ~~Filter: age ≥ 11, 04:00 origin, 10-minute grid, per-country diary-days flag~~ **Origin is no longer decided — see D-S2-1.** The other three clauses stand | Parent 2C |
| MTUS-69 is the bridge **only** if earlier waves are used in validation | Parent 2D, after decision 6 |

---

## 🔴 DECIDED 2026-08-14, AFTER THE SPANISH FILE

Four manager decisions forced by `../Step1_docs/outputs_step1/codebook_facts_spain.md`, findings
F-ES-1 to F-ES-4. Each one overrides a line that came from `RL02` and was never measured.

### ✅ D-S2-1 is CLOSED, 2026-08-15, as **D-S2-5 below**. The text that follows is kept as the record of why it was reopened; read D-S2-5 for the decided value.

### D-S2-1 — the day origin is **reopened**, and it does not close until all four codebooks are in hand

Spain's diary runs **06:00 to 06:00** (F-ES-1). No 04:00-origin day can be built from it: the two
hours from 04:00 to 06:00 belong to a different calendar day than the one the respondent reported on.

**04:00 is withdrawn as a decided value.** It was `RL02`'s standard, not a measured one, and one of
four countries has already broken it. Choosing the common origin now would mean choosing it from
one country and extending it by assumption, which is the defect this step exists to prevent.

* The origin is chosen **once UK, France and Italy codebooks are transcribed**, from the four measured
  origins, and it is recorded here as a fifth decision at that point.
* Until then no document may state an origin as decided, and **the Spanish reader's native 06:00
  indexing is left untouched** — re-indexing to a value we may not keep would destroy the only
  origin we have measured.
* What is already fixed: the harmonised day is **24 hours of 10-minute slots**, and the origin is a
  single constant shared by all four countries, not a per-country field.

### ✅ D-S2-5 — the day origin is **04:00**, reached by treating each diary as a CYCLIC day. Decided 2026-08-15.

D-S2-1 said the origin is chosen from every measured codebook **or not at all**. Author decision 16
excluded France, so **three is now every country in the corpus** and all three codebooks are in hand.
The measured origins:

| Country | Origin | Source |
|---|---|---|
| Spain | **06:00** | F-ES-1, INE `INTERVALO` 1 = 06:00-06:10 |
| Italy | **04:00** | QUEST-DG p.2, *"il diario inizia alle 4.00 del mattino"* |
| UK | **04:00** | F-UK-5, CTUR p. 2, `tid` 1 = 04:00-04:10 |

🔴 **A shared origin is not a preference, it is a requirement of leave-one-country-out.** If Spanish
days are serialised two hours out of phase with the others, the model learns "the shifted dialect is
Spain" and the transfer claim measures our indexing, not HETUS's. This is the same argument that keeps
country-extra co-presence flags out of `COP` in D-S2-2.

**No re-basing is possible, so the diary is treated as a cyclic 24-hour day.** Spain's respondent never
reported 04:00-06:00 *of the diary's own calendar day*; rotating a 06:00-origin diary to a 04:00 origin
takes those two hours from the **tail of the same diary** — the same respondent's following early
morning. That is a real splice and it is written down as one, not hidden in an index arithmetic.

**Origin = 04:00. Three reasons, in order of weight.**

1. 🔴 **It splices one country instead of two.** Rotating to 06:00 would require the same cyclic move on
   both the UK and Italy; rotating to 04:00 requires it on Spain alone.
2. **The splice lands in the sleep block.** At 04:00-06:00 the overwhelming majority of respondents in
   every one of the three countries are asleep, so the discontinuity falls at the least informative
   point of the day. **This is the whole reason both UK and Italy chose 04:00 natively**, and it is
   HETUS's own guideline origin.
3. Two of three deliveries already use it, so two of three need no transformation at all.

🔴 **Three consequences that must be implemented and checked, not assumed away.**

* **Spain's episode count will change.** The episode straddling 04:00 is split in two by the rotation.
  Spain's 430,754 is a Step 1 quantity pinned by `G1.1`; the Step 2 count is a **different quantity**
  and must be reported as such, exactly the way slot-level and episode-level `act2` counts were kept
  apart. **A Step 2 gate must assert `sum(DUR) == 1440` survives the rotation for 100 % of diaries.**
* **The rotation must be invertible.** The runner keeps the native origin per country as metadata, and
  a round-trip test rotates back and compares to the Step 1 table byte for byte.
* 🔴 **`origin_hour` is metadata, never a serialised field.** A per-country origin column reaching Step
  3 would leak country identity into LOCO by the front door after we closed the back one.
* **The Spanish reader is still not re-indexed.** Rotation happens in Step 2, on the harmonised table,
  where it is visible and testable. Step 1 keeps native indexing per country.

### D-S2-2 — co-presence: **five shared flags, plus country extras kept as named columns**

Spain fields **six** flags — `SOLO`, `PAREJA`, `PADRES`, `MENOR`, `OTMH`, `OTCON` (F-ES-2). The
harmonised schema is:

* **The five HETUS flags stay the shared core**, because they are what the other three cycles are
  expected to field and what makes the countries comparable at all.
* **`PADRES` is kept, as a country-extra column**, named and documented. It is **not** folded into
  "with other household members": that collapse is wrong for exactly the multigenerational household
  the flag marks, and paper 1 names co-presence handling as the source of load overestimation.
* **A flag a country never recorded is explicitly missing, never 0.** Zero is "recorded and absent".
* 🔴 **`MENOR` is not asserted equal to the HETUS "with children" flag.** Spain defines it as *minors
  under 10 living with you*, which is a household-composition test, not a parenthood test. It is
  mapped to the shared flag **with its national definition recorded on the mapping row**, and the
  same test is applied to each of the other three when its codebook arrives. If two countries turn
  out to define that flag differently, the difference is reported, not averaged away.
* Extras are named `cop_extra_<country>_<field>` so that no country's extra can be mistaken for a
  shared flag by a later step.

**Step 5 may not condition on any extra column**, because a country-specific flag cannot be a
conditioning variable in a leave-one-country-out design.

### D-S2-3 — location: **no range filter, anywhere.** Class membership is by explicit crosswalk

`RL02`'s "10-19 stationary, 20-39 transport" is **false for Spain** (F-ES-3). In the Spanish list
`21-29` are places, not transport, and **`41` is public transport** — above the range, and present in
the delivered file. A `10 <= LOC <= 39` filter drops every public-transport episode and mislabels
seven place codes as travel.

* **No step may test a location code by numeric range.** Membership comes from
  `crosswalk_location.csv`, code by code, cited to a codebook page.
* The target classes are **at-home / other place / private transport / public transport**, and
  every national code maps to exactly one, or is listed as unmapped.
* 🔴 **Public transport is a target class in its own right**, not a residue. A crosswalk that
  produces zero public-transport episodes for any country is a failure to be investigated, not a
  finding.
* The same treatment applies to the other three countries: their ranges are **measured, not assumed
  to be Spain's either.**

### D-S2-4 — code `11` is confirmed, and it also carries work-at-home

METH p. 124 defines `11` as house, garage, vegetable plot, garden or grounds attached to the
dwelling, **and states that working from home is coded `11` too** (F-ES-4).

* The indoor rule in 2.2 **stands** and becomes more load-bearing, not less: `LOC` alone cannot
  separate the conditioned volume from the grounds, and the `OUTDOOR_AT_HOME` exclusion list is the
  only thing that does.
* **Work-at-home is not excluded** — it is inside the conditioned volume, so it is indoor presence.
  But it means `LOC == 11` alone cannot tell "at home, not working" from "working at home", and
  **Step 9 needs that distinction for equipment load.** It comes from `ACT`, which is why the third
  digit is kept.
* The exclusion list is finalised **against each transcribed ACL**, and if the four lists disagree on
  which activities are outdoor-at-home, the disagreement is reported.

🔴 **The exclusion list in the indoor rule is finalised against the transcribed ACL, never guessed.**
A reviewer who knows HETUS will look for this rule specifically, and an invented exclusion list is
the easiest thing here to reject.

---

## 🔴 DECIDED 2026-08-16 — THE THREE HETEROGENEITIES, D-S2-6 TO D-S2-8

The parent document named three heterogeneities as **manager-owned inputs to the crosswalk, not
afterthoughts to it**: slot-versus-episode basis, secondary-activity arity and granularity, and
co-presence set membership. All three codebooks are now transcribed, so all three are decided here
from measured facts. Every claim below cites a finding ID in
`../Step1_docs/outputs_step1/codebook_facts_<country>.md`.

**Two of the three overturn a line this document previously listed as decided.** That is the same
pattern as D-S2-1 to D-S2-4 and it has the same cause: the line came from `RL02` and had never been
measured against more than one country.

### D-S2-6 — the harmonised basis is the **EPISODE**, on a 10-minute grid. Spain is the only country reconstructed, and the reconstruction must be **invertible**

Measured:

| Country | Delivered as | Origin | Duration |
|---|---|---|---|
| **Spain** | **144 fixed 10-minute slots**, one row per slot, indexed `INTERVALO`; episodes must be reconstructed | 06:00 | derived from slot runs |
| **UK** | **native episodes**, `uktus15_diary_ep_long.tab` | 04:00 | **stored**, `eptime`, in minutes (F-UK-1) |
| **Italy** | **native episodes**, minute-resolution clock fields `oraini`/`minini`/`orafin`/`minfin` | 04:00 | **computed**, not stored |

**The basis is the episode.** This is not a free choice: Step 3 serialises `DUR,ACT,LOC,COP` in
**episode form, not slot form**, so a slot-based harmonised table would have to be re-collapsed one
step later, and the collapse rule would then live outside this document where no Step 2 gate can see
it. Two of three countries also ship episodes natively; expanding them to 144 slots would discard
respondent-declared boundaries to manufacture a grid.

* **Italy is not re-slotted.** Its instrument imposes no slot, but every measured duration in the
  delivered file is a multiple of 10 minutes. 🔴 **That is an observation, not a guarantee** — the gate
  asserts it, the transform does not assume it. A non-multiple is printed and refused (`V2.c`), never
  rounded.
* **Italy's one wrapping episode per diary** (`orafin*60+minfin < oraini*60+minini`, 41,229 of 41,229
  diaries) is the midnight crossing and is handled by the same cyclic-day arithmetic as D-S2-5.
* **Spain's episodes arrive already reconstructed from Step 1** (430,754 episodes from 2,778,480
  slots), at native 06:00 indexing. Step 2 rotates them, per D-S2-5. **D-S2-5 stands unchanged**: the
  rotation splits the episode straddling 04:00, Spain's Step 2 episode count is therefore a different
  quantity from Step 1's pinned 430,754, and the rotation must round-trip back to the Step 1 table.

#### 🔴 D-S2-6-a — Spain's episode-boundary key, **measured 2026-08-16, and it is not benign**

A Spanish "episode" is an artefact of whichever columns the Step 1 reader compared between adjacent
slots. Read out of the reader rather than assumed (`../tools/4thJ_read_spain.py:347`, `COPRESENCE` at
`:126`), the key is verbatim:

```
key_cols = ["APRIN", "LUGAR"] + COPRESENCE
         = APRIN, LUGAR, SOLO, PAREJA, PADRES, MENOR, OTMH, OTCON
```

Two consequences, and the second is the one that matters.

* ✅ **The secondary activity is NOT in the key** (`:347`), so Spain is not over-split by a field only
  12.2 % of slots carry. That was the failure mode feared here and it did not happen.
* 🔴 **All six co-presence flags ARE in the key.** A Spanish episode therefore splits when *only*
  co-presence changes, with activity and location unchanged. **The UK and Italy ship
  respondent-declared episodes and do not split on that.** So Spain has systematically **more and
  shorter** episodes than the other two, **by construction, for a reason that has nothing to do with
  Spanish behaviour.**

**The prohibition below is therefore confirmed as necessary, not precautionary:**

* 🔴 **No cross-country comparison of episode count or mean episode duration may be made, in any step,
  in any gate, or in the paper.** Those are not the same measurement in Spain as in the other two.
* `G2.9`'s time budgets are unaffected — a time budget is invariant to how a day is cut into episodes,
  which is exactly why `G2.9` is stated on budgets and not on episodes. **Do not add an episode-count
  gate.**
* 🔴 **The key is NOT changed to match the UK and Italy.** Dropping co-presence from it would mean a
  Spanish episode could carry two different co-presence states, which is unrepresentable in
  `DUR,ACT,LOC,COP` — one tuple, one `COP`. The heterogeneity is real and is **reported**, not
  engineered away.
* Step 3 sees this as a distribution difference in `DUR` across countries. It is named here so that no
  later step reads it as a national finding.

The reader also records the native origin as a constant, `ORIGIN_HOUR = 6`, emitted into
`facts["origin_hour"]` (`:135`, `:496`) — which is the per-country metadata D-S2-5 requires for the
invertible rotation, and confirms Step 1 did not re-index Spain.

### D-S2-7 — secondary activity: **arity 1**, its own crosswalk, harmonised at **2 digits**

🔴 **This RETRACTS the line in work item 2.1 that says "the same crosswalk maps `act2_raw` … no second
crosswalk is built".** That line was true of Spain and the UK and is **false for Italy.**

Measured:

| Country | Field(s) | Classification | Coverage |
|---|---|---|---|
| **Spain** | `ASECU`, **1** | ~~not stated in the codebook facts~~ ✅ **same list as `APRIN`** — `Lista EET`, 3-digit; LAYOUT `F DIARIO2` rows 32/37, METH p. 49 and p. 65-66 (D-S2-10) | 12.2 % **of slots** (340,269 / 2,778,480), F-ES-6 |
| **UK** | `What_Oth1`, `What_Oth2`, `What_Oth3`, **3** | **same list as `whatdoing`** | 27.75 % / 2.72 % / 0.23 % **of episodes**, F-UK-2 |
| **Italy** | `catcon`, **1** | 🔴 **`CLS-var13`: 2-digit, 34 modalities, flat, and a *different, coarser* classification from `catpri` — not a truncation of it** | not measured in the facts file, F-IT-3 |

**Arity is 1.** `ACT2` is one field. The corpus minimum is 1; a second and third slot that only the UK
can ever fill is a country marker, and D-S2-2 already established that a field only one country
records cannot be a shared field in a leave-one-country-out design. The UK's second and third columns
are kept under the names Step 1 already gave them, `act2_extra_uk_2` and `act2_extra_uk_3`, under the
same rule as `cop_extra_*`: **named, carried, documented, and never serialised, never conditioned on.**

**Granularity is 2 digits, and only for `ACT2`.** Italy's `catcon` has 34 flat modalities in a list
that is not a refinement of the primary list, so **no third digit for Italian secondary activity
exists to be recovered.** Producing one would be fabrication. 🔴 **`ACT` keeps its 3 digits — author
decision 6 is untouched** — and the asymmetry is deliberate: Step 9's appliance triggering reads the
**primary** activity, which is where the third digit was needed.

* **A second crosswalk is built: `outputs_step2/crosswalk_activity_secondary.csv`**, same discipline as
  the primary — every row cited to a codebook page, every unmapped code listed, one-to-many rows
  flagged with a written rule.
* 🔴 **Italy's rows come from `CLS-var13`, never from `CLS-var12`.** Resolving `catcon` through the
  primary table is the specific defect this decision exists to prevent, and it is silent: the codes
  are two digits and would mostly *find a match* in the primary list while meaning something else.
* **Spain's and the UK's secondary rows may reuse their primary-list mappings**, collapsed to 2 digits,
  because in those two countries the secondary field genuinely is coded in the primary list (F-UK-2;
  ~~Spanish list not stated in the facts file and to be confirmed before the crosswalk is frozen~~
  ✅ **Spain CONFIRMED — see D-S2-10 immediately below**).

### ✅ **D-S2-10 — Spain's `ASECU` is the SAME list as the primary activity. Confirmed 2026-08-16**

The Spanish row of the table above read *"not stated in the codebook facts"*. It is now stated, from the
codebook itself, in three places (`outputs_step2/open_items_uk_withother_and_spain_asecu.md`):

* **LAYOUT, sheet `F DIARIO2`**: `APRIN` (row 32) and `ASECU` (row 37) carry the **identical**
  `Valores válidos = Lista EET`, and `ASECU` occupies positions 17-19 — **3 digits, the same width as
  `APRIN`**.
* **METH p. 49**, verbatim: *"Para la clasificación de la actividad secundaria se utilizaron los mismos
  códigos de la lista de actividades armonizada española 2009."*
* **METH p. 65-66**, the note printed immediately before the Annex I enumeration, verbatim:
  *"NOTA: Las actividades principales y secundarias se codificarán utilizando esta misma lista."*

🔴 **Spain does NOT follow Italy's pattern, and this was worth checking rather than assuming either way.**
Italy's `catcon` turned out to be a separate, coarser classification; the tempting generalisation was
that a secondary-activity field is *usually* its own list. It is not. **Two of three countries code
secondary activity in the primary list; exactly one does not.**

**What this changes, and what it does not.**

* `crosswalk_activity_secondary.csv` **still exists and D-S2-7 stands.** It is needed for Italy, and
  `G2.13` is unchanged.
* 🔴 **But it now holds rows of two different kinds, and confusing them is a defect.** For Spain and the
  UK, a secondary row is a **truncation** of a primary-list code to 2 digits. For Italy, it is a
  **crosswalk** from a different 34-modality list. **Italy's 2-digit target may never be computed as
  "the first two digits of the source code"** — the source is already 2-digit and means something else.
  The `source_list` column `G2.13` requires is what distinguishes the two kinds, and it is load-bearing
  for this reason as well.
* **A new gate follows, `G2.15`:** for Spain and the UK, every secondary-crosswalk row must agree with
  the primary crosswalk on the same source code, truncated to 2 digits. Two files that the codebook says
  must say the same thing are exactly where a hand edit to one of them goes unnoticed.
* **Spain's `ASECU` modality count is inherited, not independently enumerated.** LAYOUT points `ASECU`
  at the named list rather than re-listing it, so the 116 three-digit codes come from the primary
  enumeration (METH pp. 66-71) on the strength of the "same list" statements above. A citation
  enumerating `ASECU`'s codes under its own heading is **`NOT STATED IN CODEBOOK`**.
* **Sentinel: blank, and it is single-sourced.** LAYOUT row 38 documents *"Blanco"* — an empty field in
  the fixed-width record, not a reserved numeric value. 🔴 **METH does not corroborate it**; a direct
  search for *"blanco"* across all 127 pages returns only two unrelated hits (*"Libro blanco"*, a report
  title). The blank convention rests on one document, and is recorded as resting on one document. INE's
  separate diary-coding manual, referenced at METH p. 49, **is not in this delivery** and was not opened.
* **The three states survive: not recorded / recorded and blank / recorded with a value.** Blank is not
  a code and is never mapped to one. Italy's blank is a literal run of ASCII spaces of the field's
  declared width (F-IT-6); the UK's is the sentinel `-9`, "no answer/refused" (F-UK-2). 🔴 **A
  sentinel and a blank are not the same state and are not merged.**
* 🔴 **Coverage percentages are NOT comparable across countries as delivered.** Spain's 12.2 % is a
  share of *slots*, the UK's 27.75 % a share of *episodes*. Any coverage figure quoted anywhere must
  name its denominator. This is the same trap D-S2-6 names for episode counts.
* **Where Spain's slots disagree within one reconstructed episode**, the value already taken is the
  **first slot of the run** — `act2_raw=("ASECU", "first")`, `../tools/4thJ_read_spain.py:362`. Step 1
  made that choice and Step 2 consumes the parquet, so **Step 2 does not re-decide it and could not:
  the slots are gone by then.** It is recorded here as an inherited rule, not adopted as a new one.
  🔴 **The share of Spanish episodes whose slots were *not* constant in `ASECU` is consequently
  unmeasured, and cannot be measured downstream.** It is a one-line addition to the Step 1 reader's
  parse report or it is declared unmeasured in the methods. **It is not quietly dropped** — a
  first-value rule whose disagreement rate is unknown is a heuristic in hiding.

`ACT2` is carried in `harmonised.parquet`. **It is not in the Step 3 tuple** — that tuple is frozen as
`DUR,ACT,LOC,COP`. This step harmonises it correctly so that Step 9 and any later question can use it;
it does not add it to the serialisation.

### D-S2-8 — co-presence: **six shared flags**, not five. The parent flag is shared, and Spain's `1/6` coding is a live bug

Measured:

| Country | Flags | Coding | Explicit missingness column |
|---|---|---|---|
| **Spain** | **6**: `SOLO`, `PAREJA`, `PADRES`, `MENOR`, `OTMH`, `OTCON` | 🔴 **1 = yes, 6 = no** | **none** (F-ES-2) |
| **UK** | **9**: `WithAlone`, `WithSpouse`, `WithMother`, `WithFather`, `WithChild`, `WithOther`, `WithOtherYK`, `WithMiss`, `WithNA` | binary 0/1 | **`WithMiss`** (F-UK-4) |
| **Italy** | **8**: `daso`, `cmadre`, `cpadre`, `cconiu`, `cfigli`, `cfrate`, `afacon`, `aperco` | present = "1", absent = blank space | **none** (F-IT-4) |

**Three findings, each one changing what gets built.**

**1. 🔴 The parent flag is SHARED, and this corrects D-S2-2.** D-S2-2 carried Spain's `PADRES` as
`cop_extra_es_padres` on the belief that it was a Spanish extra. It is not: **all three countries
record parent co-presence.** Spain records it in one flag, the UK in two (`WithMother`, `WithFather`)
and Italy in two (`cmadre`, `cpadre`). So:

* **`cop_parent` becomes the sixth shared flag.** For the UK and Italy it is the logical OR of the two
  national components; for Spain it is `PADRES` directly.
* **The UK's and Italy's split survives as extras** — `cop_extra_uk_mother` / `_father`,
  `cop_extra_it_madre` / `_padre` — because an OR that discards its inputs cannot be audited.
* *(Superseded: "Spain's sixth flag `PADRES` is carried as `cop_extra_es_padres`. It is not merged."
  The no-merge half stands; the "Spanish extra" half was wrong.)* 🔴 **This is a widening of the shared
  core forced by measurement, not a relaxation.** Six flags every country records is strictly more
  comparable than five plus an orphan, and it moves in the direction D-S2-2 already pointed:
  *"five is the shared core, not the ceiling."*
* **Italy's `cfrate` (with siblings) is a genuine extra** — `cop_extra_it_siblings`. No other country
  fields it.

**2. 🔴 The "with children" flag means three different things, and the difference cannot be removed.**

* Spain `MENOR` — *minors under 10 who live with you*: a household-composition test.
* UK `WithChild` — **0-7 years only**; children **8 and over fall into `WithOther`**.
* Italy `cfigli` — with children, no age bound stated in the delivery.

The UK's boundary is strictly narrower than Spain's, and the 8-and-9-year-olds are **not recoverable**:
they are already pooled into `WithOther`, so no crosswalk can extract them. Harmonising to a common
age band is therefore impossible in the only direction that matters.

* **The flag is mapped, and all three national definitions are recorded verbatim on the mapping row**,
  per D-S2-2's existing rule.
* 🔴 **No claim in any step or in the paper may rest on a cross-country comparison of the children
  flag alone.** A lower UK prevalence is the expected consequence of a narrower definition, not a
  finding about British households. This is written down here so it cannot later be read as one.
* This is a **limitation of the corpus, reported in the methods**, not a defect of the crosswalk.

**3. 🔴 Missingness exists in one country only, and Spain's coding is a bug waiting to be written.**

* **`WithMiss` is the only declared missingness column in the corpus.** Where it is set, all six shared
  UK flags are **MISSING**, not 0. D-S2-2's rule — *a flag a country never recorded is explicitly
  missing, never 0* — now has exactly one country where it bites at the row level.
* 🔴 **`WithNA` is NOT a missingness flag** (F-UK-4). It is a backward-compatibility marker for
  episodes that would have been uncoded under the 2000-01 design (paid work, education, sleep). **It is
  never mapped and never read as missing.** Its name is the trap.
* **Spain and Italy declare no missingness column**, so for them a flag is missing only when the field
  is absent from the record — Italy's blank-space sentinel (F-IT-4). **Spain has no missing state for
  co-presence at all**; every Spanish episode is "recorded". That is a fact about the delivery and is
  stated as one, in the same three-state discipline M-1 imposed on `loc_raw`.
* 🔴 **Spain codes `1 = yes` and `6 = no`. `6` is truthy.** Any recode written as `bool(x)`, `x != 0`,
  `x > 0` or a bare cast makes **every Spanish respondent co-present with everybody, simultaneously,
  on every episode** — and it would pass mass conservation, day closure, crosswalk totality and every
  activity gate in this document without a murmur. **The recode is an explicit value map, and an
  unrecognised value is printed and refused (`V2.c`), never coerced.** `G2.14` exists to catch this.

~~**One mapping row is not yet safe to freeze.** The UK's `WithOther` (which includes children 8+) is
read as *other household members* and `WithOtherYK` (*"with other(s) you know outside of HH"*) as
*other persons*, on the strength of the latter's own label. 🔴 **`WithOther`'s scope is inferred, not
quoted from the CTUR variable list**, and it must be confirmed there before `crosswalk_copresence.csv`
is frozen. Recorded as an open item rather than folded in quietly.~~

### ✅ **D-S2-9 — the UK row is FROZEN. `WithOther`'s scope is now quoted, not inferred. 2026-08-16**

Confirmed against the delivery's own documents, in two independent places
(`outputs_step2/open_items_uk_withother_and_spain_asecu.md`):

* **The data dictionary's own variable label**, `uktus15_diary_ep_long`, `Pos. = 45`, verbatim:
  *"With other person(s) (incl. child 8+ years)"* — and `Pos. = 44`, verbatim: *"With child 0-7
  years"*. The scope was never an inference to begin with once the label was read.
* **CTUR p. 11-12, §5.2**, verbatim: *"in UKTUS 2014-15, only time with a child 0-7 years could be
  reported. Time with children 8-9 and 10-14 years will be reported as time with other members of the
  household."*

**The mapping stands as written and is frozen:** `WithOther` → *other household members*, `WithOtherYK`
→ *other persons*.

🔴 **And the confirmation sharpened the children-flag problem rather than closing it.** D-S2-8 recorded
that the flag "means three different things". It is more specific than that, and the specific form is
more useful:

| Country | Children flag | Cut-off | Where older children go |
|---|---|---|---|
| Spain | `MENOR` | under **10** | into `OTMH`, other household members |
| UK | `WithChild` | **0-7** | into `WithOther`, other household members — stated verbatim |
| Italy | `cfigli`-type | **none recorded** | nowhere; they stay in the children flag |

So Spain and the UK share a *structure* — a cut-off, with the remainder spilling into the
household-others flag — and differ only in where the cut sits, two years apart. **Italy does not share
that structure at all.** 🔴 The consequence is a prohibition, not a gate, because no gate can see this:
**`cop_children` may not be compared across countries in any step, gate or the paper**, and any
Spain-UK comparison that is nonetheless made must state the 10-versus-8 cut-off in the same sentence.
This joins D-S2-6-a's ban on cross-country episode-count comparison in the same category of
manufactured difference.

**One new hole, recorded because it was found and not resolved.** Whether `WithOtherYK` (*"other(s) you
know outside of HH"*) also absorbs any part of the 8+ children population — a child known to but not
living with the household — is **`NOT STATED IN CODEBOOK`.** Neither the data dictionary label nor
CTUR §5.2 addresses it; both describe the split only as `WithChild` (0-7) against `WithOther`. It is
not assumed to be irrelevant.

**No threshold anywhere was moved by D-S2-6, D-S2-7 or D-S2-8.**

---

## INPUTS

* `../Step1_docs/outputs_step1/episodes_<country>.parquet` — **three** files *(superseded: "four")*,
  and 🔴 **from the run-stamped directory of the accepted sixteen-gate round, never from a stale copy**
* `../Step1_docs/outputs_step1/codebook_facts_<country>.md` — the only authority on what each field
  means. **Not `RL02`, not `RL17`.** Those are hypotheses; the codebook is the fact.

---

## WORK ITEMS

### 2.1 — Build the activity crosswalk, from the codebooks

One table, four columns of national codes mapping to one target list. Because all four waves share a
coding-list generation, this should be close to the identity map — **and if it is not, that is a
finding about the corpus, not a licence to improvise.**

* Every mapping row carries the codebook page it came from.
* Every code that maps to nothing is **listed**, counted, and either resolved or declared. It is
  never silently dropped.
* 🔴 A one-to-many mapping requires a written rule and is flagged in the output, because a
  one-to-many mapping is where an arbitrary heuristic hides.

**Output:** `outputs_step2/crosswalk_activity.csv` + `crosswalk_unmapped.md`.

🔴 ~~**The same crosswalk maps `act2_raw`.** Secondary activity is coded in the same national list as
primary activity, so it is harmonised by the same table and **no second crosswalk is built**.~~
**RETRACTED 2026-08-16 by D-S2-7.** True of Spain and the UK, **false for Italy**: `catcon` is
`CLS-var13`, a separate 2-digit list of 34 modalities that is *not* a truncation of `catpri` (F-IT-3).
A second crosswalk **is** built — `crosswalk_activity_secondary.csv`, 2-digit target, arity 1 — and
Italy's rows come from `CLS-var13`, never from the primary table. See D-S2-7.

The three states of `act2` — not recorded, recorded and blank, recorded with a value — survive
harmonisation unchanged; **blank is not a code and is never mapped to one**, and a sentinel (the UK's
`-9`) is not the same state as a blank (Italy's ASCII spaces).

### 2.2 — Location crosswalk and the indoor rule

Same discipline, and **per D-S2-3 there is no numeric range test anywhere** — every national code is
mapped explicitly to one of at-home / other place / private transport / public transport, or listed
as unmapped. Then implement:

```
indoor_presence = (LOC == 11) AND (ACT not in OUTDOOR_AT_HOME)
```

`OUTDOOR_AT_HOME` is an explicit, versioned list derived from the ACL, stored as data rather than
inline in code, so the validation can read the same list the transform used. Per D-S2-4, work-at-home
is **not** in that list.

**Output:** `outputs_step2/crosswalk_location.csv`, `outputs_step2/outdoor_at_home.csv`.

🔴 `crosswalk_location.csv` carries an explicit **`target_class`** column holding one of the four
classes. Gate **G2.11** and vacuity guard **V2.e** import that column rather than restating the class
list, so the shipped crosswalk is the single place the classes are defined.

### 2.3 — Co-presence normalisation

Per D-S2-2, **as widened by D-S2-8**. 🔴 **Six shared flags, not five** — alone / with partner / with
children / **with a parent** / with other household members / with other persons — **plus every
country-specific extra, kept as its own named column.** All three countries record parent co-presence
(Spain `PADRES`; UK `WithMother` OR `WithFather`; Italy `cmadre` OR `cpadre`), so it is shared, and
the national components survive as extras because an OR that discards its inputs cannot be audited.

**Output `outputs_step2/crosswalk_copresence.csv`** alongside the availability document, carrying the
national definition of every mapped flag verbatim — the children flag especially, which means three
different things (D-S2-8).

🔴 **Added 2026-08-16 by D-S3-1: the file also carries a `bit_position` column, 0-5.** Step 3 packs the
six flags into a single decimal integer 0-63, and **the bit order lives here, in the file that defines
the flags — not in `encoder.py`.** The rule is one line and it is load-bearing: **the encoder reads the
order from this crosswalk and never hard-codes it.** An encoder and decoder that share a hard-coded
order round-trip perfectly through `G3.1` and mean something else entirely; `G3.14 (b)` is the gate
that catches it, and it can only do so because its reference is a file the encoder did not author.
The six positions must be exactly `{0,1,2,3,4,5}`, one per shared flag, and `V3.e` FAILs if they are
not.

* Countries that record fewer than six get the missing ones as **explicitly missing, never as 0**.
  Zero means "recorded and absent"; missing means "not recorded". Collapsing them destroys exactly
  the field paper 1 identified as the source of load **over**estimation.
* ~~Spain's sixth flag `PADRES` is carried as `cop_extra_es_padres`.~~ 🔴 **Corrected by D-S2-8:
  `PADRES` maps to the shared `cop_parent` flag, because the UK and Italy record the same thing in two
  columns each.** It is still **not** merged into "other household members".
* Every mapping row records the **national definition** of the flag it maps, not just its name.
* The packed on-wire form is fixed in Step 3, not here.

**Output:** `outputs_step2/copresence_availability.md` — which country records which flag, which
extras exist, and how each national definition differs from the shared flag it maps to.

### 2.4 — Apply the filter and emit the harmonised table

10-minute grid, per-country `diary_days` flag carried through. ✅ **The day origin is DECIDED —
04:00, cyclic rotation, D-S2-5 — and this work item is no longer blocked on it.**

🔴 **The age floor moves from 11 to 10, and it is derived, not chosen.** The rule is *the harmonised
floor is the highest of the participating countries' minimum ages*, so that every country can supply
every age the corpus contains. **11 was France's minimum.** With France excluded (decision 16) the
participating minima are Spain **10**, the UK **8** and Italy **3**, so the binding floor is **10**.
Filter: **age ≥ 10**. *(Superseded: "Age ≥ 11".)* 🔴 **This is not a widened band** — it is the same
rule evaluated over a different country set, and it must be re-evaluated again if France ever returns,
in which case it goes back to 11.

**Output:** `outputs_step2/harmonised.parquet`, one row per episode, plus
`outputs_step2/filter_report.md` counting exactly how many respondents and diaries each filter clause
removed, per country.

🔴 **Count what the filter removed, per clause, per country.** A filter that removes 3 % of Italy and
19 % of France is telling you something about France, and a single total hides it.

---

## OUTPUTS AND INTERFACES

| Artefact | Consumed by |
|---|---|
| `outputs_step2/harmonised.parquet` | Step 3 |
| `outputs_step2/crosswalk_*.csv` — activity, **activity_secondary**, location, **copresence** | Step 2 validation; the methods section |
| `outputs_step2/outdoor_at_home.csv` | Step 7D (diaries to schedules) and Step 2 validation |
| `outputs_step2/copresence_availability.md` | Step 5, which must not condition on a flag a country never recorded |
| `outputs_step2/filter_report.md` | Step 2 validation gate G2.7 |

---

## HOW IT RUNS

`sbatch`, partition `ps`, `-t 7-00:00:00`. CPU only. No GPU is needed anywhere in this step.

---

## WHAT BLOCKS THIS STEP

🔴 **Rewritten 2026-08-15.** Step 1.3 must have emitted **all three** episode tables — Spain, the UK
and Italy — and they all exist. ✅ **D-S2-1 no longer blocks work item 2.4**; the origin is decided
(D-S2-5, 04:00, cyclic rotation).

**What still blocks this step: nothing external.** The one remaining precondition is the
**sixteen-gate Step 1 re-run** on the three countries (M-1..M-5 changed the record contract, so Step 2
must consume parquets written to the current contract, not the previous one). 🔴 **That is our own
work on our own cluster, not a queue in another institution** — which is the whole point of decision
16. *(Superseded: "Step 1.3 must have emitted all four episode tables… 2.4 waits on UK, France and
Italy.")*

**What this step blocks:** Steps 3 onward. Also Step 9 — the appliance mapping needs 3-digit codes,
and this is the step that either preserves them or does not.

---

## DEFINITION OF DONE

1. **Four crosswalks — activity, secondary activity, location, co-presence** *(D-S2-7 added the
   secondary one; D-S2-8 made co-presence a shipped table)* — every row cited to a codebook page,
   every unmapped code listed.
2. The indoor rule implemented, its exclusion list stored as data, and the list justified from the ACL.
3. Co-presence availability documented per country, with missing distinguished from absent.
4. `harmonised.parquet` emitted, and the filter report counting removals per clause per country.
5. All Step 2 gates PASS **and each has been seen failing**.

---

## PROGRESS LOG

Append-only.

### 2026-08-14 — step document created

* 🔴 The single most consequential item here is **2.2**. Papers 2 and 3 were built on the assumption
  that presence in the conditioned volume is readable from the location field. `RL02` showed it is
  not, because code 11 merges dwelling, yard and garden. This step is where that correction either
  enters the pipeline or is lost.
* Author decision 6 removed the pressure to harmonise at 2-digit. **Do not reintroduce 2-digit
  pooling for convenience** — Step 9's appliance triggering needs the third digit, and once it is
  gone this step cannot give it back.

### 2026-08-14 — four decisions taken after the Spanish file, D-S2-1 to D-S2-4

* Findings F-ES-1 to F-ES-4 in `../Step1_docs/outputs_step1/codebook_facts_spain.md` are resolved as
  D-S2-1 to D-S2-4 above. **Three of the four overturn a line this document had listed as decided,
  and all three of those lines came from `RL02` rather than from a file.** The pattern is the point:
  the first country measured broke the standard in three places out of the handful it could touch.
* 🔴 **The 04:00 origin is withdrawn rather than replaced.** Author call, 2026-08-14: the origin is
  decided from four measured codebooks or not at all. Setting it to 06:00 now would be the same
  error in the other direction — one country generalised to four. Work item 2.4 is blocked on it.
* **Co-presence keeps the five-flag core and adds country extras beside it.** `PADRES` survives as
  `cop_extra_es_padres`. The shared core is what carries the transfer claim; the extras are what
  stop a recorded field from being thrown away. Step 5 may not condition on an extra.
* **`RL02`'s location range rule is retracted and no range test replaces it.** Spain's `41` is public
  transport, above the range `RL02` gave, and present in the file. Ranges are how this class of
  defect stays silent; an explicit code-by-code crosswalk is how it cannot.
* The other three countries' origins, flags and location ranges are **measured, not assumed to match
  Spain either.** Spain is the first measurement, not the new standard.

### 2026-08-15 — 🔴 **STEP 2 IS UNBLOCKED. D-S2-1 closes as D-S2-5. The age floor moves 11 → 10.**

**Author decision 16 excluded France**, so the corpus is Spain, the UK and Italy — three countries, all
built, all with transcribed codebooks. Three things follow, and the first is the one that mattered.

* ✅ **D-S2-1 closes as D-S2-5: the day origin is 04:00, reached by treating each diary as a cyclic
  24-hour day.** D-S2-1's own condition was *"chosen from every measured codebook or not at all"*, and
  three is now every country. Measured: Spain **06:00**, Italy **04:00**, UK **04:00**. 🔴 **No
  re-basing is possible in either direction** — a 06:00 diary contains no 04:00-06:00 of its own
  calendar day — so the rotation takes those two hours from the tail of the same diary, and **that
  splice is written down rather than hidden in index arithmetic.** 04:00 wins because it splices **one**
  country instead of two, because the splice lands in the sleep block (which is exactly why the UK and
  Italy chose it natively, and it is HETUS's own guideline origin), and because two of three deliveries
  then need no transformation at all.
* 🔴 **Three consequences that are implementation work, not notes:** Spain's episode count *will* change
  (the episode straddling 04:00 splits), so the Step 2 count is a different quantity from Step 1's
  pinned 430,754 and must be reported as one; the rotation must be **invertible**, with a round-trip
  test back to the Step 1 table; and **`origin_hour` is metadata, never a serialised field** — a
  per-country origin column reaching Step 3 would leak country identity into LOCO by the front door
  after D-S2-2 closed the back one.
* **The age floor moves from 11 to 10, and it is derived, not chosen.** The rule is *the highest of the
  participating countries' minimum ages*. **11 was France's.** Without France the minima are Spain 10,
  UK 8, Italy 3, so the floor is **10**. 🔴 **Not a widened band** — the same rule over a different
  country set, and it returns to 11 if France is ever re-admitted.
* **`V2.a` moves 4 → 3** and **`G2.9` now compares three countries.** 🔴 **`G2.9`'s threshold was NOT
  touched, and note which way it moves:** three countries give **3 pairs instead of 6**, so there are
  half as many chances to clear 20 min/day on 3 of 10 categories. **The gate gets harder, not easier**,
  which is precisely why the numbers stay where they were pre-registered.

🔴 **What still blocks Step 2, and it is ours:** the **sixteen-gate Step 1 re-run**. M-1 to M-5 changed
the record contract (three-state `loc_raw`, nullable weights), so Step 2 must consume parquets written
to the current contract. **Step 2 does not start on stale parquets.**

### 2026-08-16 — 🔴 **THE THREE HETEROGENEITIES ARE DECIDED: D-S2-6, D-S2-7, D-S2-8**

The parent document held three questions open as *manager-owned inputs to the crosswalk, not
afterthoughts to it*. All three codebooks are transcribed, so all three are now decided from measured
facts rather than left to be settled by whoever writes the transform first. **Two of the three
overturn a line this document listed as decided** — the same pattern, and the same cause, as D-S2-1 to
D-S2-4: the line came from `RL02` and had been measured against one country or none.

* **D-S2-6 — the basis is the EPISODE, on a 10-minute grid.** Forced, not chosen: Step 3 serialises
  episode form, so a slot-based table would be re-collapsed one step later under a rule living outside
  every Step 2 gate. Spain ships 144 fixed slots and is the only country reconstructed; the UK ships
  native episodes with a stored `eptime`; Italy ships native minute-resolution clock fields with no
  slot at all. **Italy is not re-slotted** — its durations are all multiples of 10 as delivered, and
  that is asserted by a gate, never assumed by the transform.
* 🔴 **D-S2-6-a, measured and NOT benign.** Spain's episode-boundary key is
  `APRIN, LUGAR + all six co-presence flags` (`../tools/4thJ_read_spain.py:347`). The good news is
  that the secondary activity is **not** in it, so Spain is not over-split by a field 12.2 % of slots
  carry. The bad news is that co-presence **is**: a Spanish episode splits when only co-presence
  changes, and the UK's and Italy's respondent-declared episodes do not. **Spain therefore has more
  and shorter episodes by construction, for a reason with nothing to do with Spanish behaviour.**
  Consequence, written down before anyone can read it as a finding: **no cross-country comparison of
  episode count or mean episode duration, in any step, in any gate, or in the paper.** Time budgets
  are unaffected, which is exactly why `G2.9` is stated on budgets. 🔴 **The key is not "fixed" to
  match the others** — dropping co-presence from it would let one episode carry two co-presence
  states, which `DUR,ACT,LOC,COP` cannot represent. The heterogeneity is reported, not engineered away.
* 🔴 **D-S2-7 retracts work item 2.1's "no second crosswalk is built".** That line was true of Spain
  and the UK and **false for Italy**: `catcon` is `CLS-var13`, 34 flat 2-digit modalities, *a different
  and coarser classification, not a truncation of `catpri`* (F-IT-3). Resolving Italian secondary codes
  through the primary table is the silent version of this defect — two-digit codes that mostly *find a
  match* while meaning something else. So: **arity 1** (corpus minimum; the UK's second and third
  columns become named extras that are never serialised and never conditioned on, exactly like
  `cop_extra_*`), **its own crosswalk**, and **2-digit granularity for `ACT2` only** because no third
  digit for Italian secondary activity exists to be recovered and inventing one is fabrication.
  🔴 **`ACT` keeps its 3 digits — decision 6 untouched** — and the asymmetry is deliberate: Step 9's
  appliance triggering reads the *primary* activity.
* **Also under D-S2-7:** coverage percentages are not comparable as delivered — Spain's 12.2 % is a
  share of slots, the UK's 27.75 % a share of episodes — so any coverage figure must name its
  denominator. And Spain's within-episode `ACT2` rule is **inherited, not adopted**: Step 1 already
  took the first slot of the run (`4thJ_read_spain.py:362`), and the share of episodes where the slots
  disagreed is **unmeasured and unmeasurable downstream**. It is a one-line addition to the Step 1
  parse report or it is declared unmeasured in the methods; it is not quietly dropped.
* 🔴 **D-S2-8 widens the shared co-presence core from five flags to six, and corrects D-S2-2.** D-S2-2
  carried Spain's `PADRES` as a Spanish extra. It is not one: **all three countries record parent
  co-presence** — Spain in one flag, the UK in two (`WithMother`, `WithFather`), Italy in two
  (`cmadre`, `cpadre`). `cop_parent` becomes the sixth shared flag, formed as an OR for the UK and
  Italy, **with the national components kept as extras because an OR that discards its inputs cannot
  be audited.** Six flags every country records is strictly more comparable than five plus an orphan,
  and it moves in the direction D-S2-2 already pointed: *five is the shared core, not the ceiling.*
  Italy's `cfrate` (siblings) is a genuine extra.
* 🔴 **The "with children" flag means three different things and the difference cannot be removed.**
  Spain's `MENOR` is *minors under 10 living with you*; the UK's `WithChild` is **0-7 only**, with
  children 8+ already pooled into `WithOther` and therefore **unrecoverable by any crosswalk**; Italy's
  `cfigli` carries no stated age bound. The flag is mapped with all three definitions recorded on the
  row, and **no claim anywhere may rest on a cross-country comparison of it alone** — a lower UK
  prevalence is a definition, not a fact about British households. A corpus limitation, reported in
  the methods, not a crosswalk defect.
* 🔴 **Two co-presence traps, both silent, both now written down.** `WithMiss` is the corpus's only
  declared missingness column, so D-S2-2's *missing is never 0* rule bites at row level in exactly one
  country; `WithNA` is **not** a missingness flag (F-UK-4) and its name is the trap. And **Spain codes
  `1 = yes`, `6 = no`, so `6` is truthy** — any recode written as `bool(x)` or `x != 0` makes every
  Spanish respondent co-present with everybody simultaneously on every episode, and it would pass mass
  conservation, day closure, crosswalk totality and every activity gate in this document without a
  murmur. `G2.14` exists for that one bug.
* **Two open items, named rather than folded in quietly:** the UK's `WithOther` scope is *inferred*
  from `WithOtherYK`'s label and must be confirmed against the CTUR variable list before
  `crosswalk_copresence.csv` is frozen; and Spain's secondary-activity code list is not stated in the
  codebook facts and must be confirmed before `crosswalk_activity_secondary.csv` is frozen.
* **No threshold anywhere was moved.** D-S2-6 to D-S2-8 add tables, columns and prohibitions; they
  relax nothing.

**Still blocked on the same one thing:** the sixteen-gate Step 1 re-run. Nothing above can be built
against a parquet written to the previous record contract.

### 2026-08-16 (later) — Step 3 sent one column back: `crosswalk_copresence.csv` gains `bit_position`

D-S3-1 fixed the `COP` packing at a single decimal integer 0-63 (measured, Speed job 1252633). That
decision has exactly one consequence in this step, and it is written here rather than in Step 3
because **this is the document that defines the flags**.

* `crosswalk_copresence.csv` carries a **`bit_position` column, 0-5**, one per shared flag.
* 🔴 **The encoder reads the bit order from this file and never hard-codes it.** An encoder and a
  decoder sharing a hard-coded order round-trip perfectly and mean something else; `G3.14 (b)` catches
  that only because its reference is a file the encoder did not author. Hard-coding the order removes
  the gate's independence without removing the gate, which is the worst of both.
* `V2.f` was extended to FAIL if the column is missing or its positions are not exactly `{0,...,5}`.
  Step 2 writes the file, so Step 2 is where its absence is cheapest to catch — Step 3 would find out
  only after building an encoder around a guess.

**Nothing else in this step changed.** D-S2-8's six flags, their national definitions and the value
maps are untouched; this adds a column, not a decision. Also worth recording: the packing measurement
came back at **8 tokens per episode, identical to the old single-digit `COP` field**, so **D-S2-8's
widening from one digit to six flags cost nothing** and no threshold anywhere needed relaxing to
accommodate it.

### 2026-08-16 (later) — 🔴 **D-S2-9 and D-S2-10: both open codebook items are CLOSED, from the codebooks**

The two items this document named as open rather than folding in quietly are now answered, each from the
delivery's own documents, with verbatim quotations and page references. Evidence file:
`outputs_step2/open_items_uk_withother_and_spain_asecu.md`.

**D-S2-9 — the UK's `WithOther` scope: CONFIRMED, and the mapping row is frozen.** The scope was never
an inference once the data dictionary label was read: `Pos. = 45`, verbatim *"With other person(s)
(incl. child 8+ years)"*, against `Pos. = 44`, *"With child 0-7 years"*. CTUR p. 11-12 §5.2 says the
same thing in prose independently. `WithOther` → *other household members*, `WithOtherYK` → *other
persons*, frozen.

🔴 **The confirmation made the children-flag problem sharper, not smaller, and that is the useful part.**
D-S2-8 said the flag "means three different things". The specific form is more actionable: **Spain and
the UK share a structure** — a cut-off with older children spilling into the household-others flag,
at **10** and **8** respectively — while **Italy has no cut-off at all**. So the failure is not
three-way symmetric: two countries differ by two years, the third differs in kind. **The prohibition
stands and is now precise:** `cop_children` is not comparable across countries in any step, gate or the
paper, and any Spain-UK comparison must state the 10-versus-8 cut-off in the same sentence.

**One new hole, recorded because it was found:** whether `WithOtherYK` also absorbs part of the 8+
children population — a child known to but not resident with the household — is **`NOT STATED IN
CODEBOOK`** in both sources. It is not assumed away.

**D-S2-10 — Spain's `ASECU`: the SAME list as the primary activity.** Stated three times: LAYOUT
`F DIARIO2` gives `APRIN` (row 32) and `ASECU` (row 37) the **identical** `Valores válidos = Lista EET`
at the same 3-digit width; METH p. 49 says *"se utilizaron los mismos códigos de la lista de actividades
armonizada española 2009"*; METH p. 65-66 says *"Las actividades principales y secundarias se
codificarán utilizando esta misma lista."*

🔴 **This was worth checking rather than generalising in either direction.** Italy's `catcon` being a
separate coarser list made "secondary activity gets its own classification" look like the rule. It is
not: **two of three countries code secondary activity in the primary list, exactly one does not.** Had
we assumed Spain matched Italy, we would have built a redundant Spanish crosswalk and had two files
free to drift apart with nothing checking them.

**Consequences, and D-S2-7 is not disturbed.** `crosswalk_activity_secondary.csv` still exists, still
needed for Italy, `G2.13` unchanged. But 🔴 **it now holds rows of two different kinds and confusing
them is a defect**: Spain's and the UK's rows are **truncations** of primary-list codes; Italy's are a
**crosswalk** from a different 34-modality list. **Italy's 2-digit target may never be computed as "the
first two digits of the source"** — the source is already two digits and means something else entirely.
The `source_list` column is what tells the two kinds apart, which is a second reason it is load-bearing.

**`G2.15` follows** — for Spain and the UK only, every secondary row must agree with the primary
crosswalk on the same code, truncated to 2 digits; 0 disagreements; Italy excluded by construction.
🔴 **`G2.13` and `G2.15` are opposites and both must hold**: Spain and the UK must agree with the primary
table, Italy must never touch it.

**Two things carried as inherited rather than measured**, so they are not mistaken for fresh evidence:
Spain's 116 three-digit modalities come from the **primary** enumeration (METH pp. 66-71) via the
"same list" statements — a listing under `ASECU`'s own heading is `NOT STATED IN CODEBOOK`. And the
blank-field sentinel rests on **one document only**, LAYOUT row 38 (*"Blanco"*); METH does not
corroborate it anywhere in 127 pages, and INE's separate diary-coding manual, referenced at METH p. 49,
is not in this delivery.

**No threshold was moved. Step 2 is now fifteen gates and sixteen perturbations.**
