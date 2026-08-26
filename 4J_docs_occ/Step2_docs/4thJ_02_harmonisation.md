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

## 🔴 DECIDED 2026-08-16 — D-S2-11: WHAT THE ACTIVITY CROSSWALK MAPS *TO*

### D-S2-11 — the target is a 3-digit list **defined by agreement between two delivered national lists**, never by one country and never by a document we do not hold

Work item 2.1 said "one target list" and never said which. It cannot be deferred any longer, because
every mapping row has to cite a page and a row cannot cite a page in a document that is not in the
delivery.

**The three source lists are not one list.** Step 1 emitted them and they can be read directly:

| Country | Rows | Sleep is | Level-1 of sleep |
|---|---|---|---|
| Spain | 116 (`crosswalk_source_spain_activity.csv`) | `011 Dormir` | `0` |
| Italy | 146 (`crosswalk_source_italy_activity.csv`) | `011 Dormire` | `0` |
| **UK** | **277** (`crosswalk_source_uk_activity.csv`) | **`110 Sleep`** | **`1`** |

🔴 **Spain and Italy share a numbering; the UK does not.** F-UK-10 already said so in words — *"the
coding list is the UK's own, not a verbatim Eurostat HETUS list"*, NATCEN Appendix H, a list built for
continuity with UKTUS 2000-01. So work item 2.1's expectation that the crosswalk "should be close to
the identity map" is **true for two countries and false for the third**, and per that work item's own
sentence that is *"a finding about the corpus, not a licence to improvise"*. It is recorded here as the
finding.

**The decision.** The harmonised target is a **3-digit code list shipped as
`outputs_step2/activity_target_list.csv`**, and it is constructed by this rule:

1. A code enters the target list only if **two of the three delivered national lists carry it with
   agreeing meaning**. In practice that is Spain and Italy, which is why the target ends up being the
   HETUS-2008-generation numbering — but the authority is *the two deliveries*, not Eurostat.
2. Every target row therefore carries **two independent citations**, one per country
   (`source_es_page`, `source_it_source`). A row with one citation is marked `single_source` and is
   still a target, so nothing is dropped, but it is visibly weaker evidence.
3. Where the two lists carry the same code with **disagreeing** meaning, the row is listed in
   `crosswalk_unmapped.md` as a **conflict** and resolved explicitly, never averaged.
4. `act_level1` is **the first digit of the target code**, always.

🔴 **Why not simply declare "the Eurostat HETUS 2008 ACL" the target.** Because we do not hold that
document. Every mapping row would then cite a page nobody in this project has read, `G2.2` would be
satisfied by a citation that cannot be checked, and the gate that exists to catch an invented mapping
row would be passing on invented citations. **A target list must be citable to the delivery, or the
citation gate is theatre.**

🔴 **Why not adopt the UK's list, or Spain's, as the target.** One country's list as the shared
vocabulary means two countries get crosswalked and one gets a free pass, and the free-riding country's
distribution becomes the reference the other two are pulled toward. That is precisely the
over-harmonisation failure `G2.9` exists to detect, installed deliberately at the design stage where
`G2.9` would then have to catch our own decision. Requiring **two** deliveries to agree before a code
is a target means no single country defines the vocabulary.

**Consequence for the UK, stated plainly so it is not discovered later:** the UK is the only country
whose activity crosswalk is real work rather than an identity check. All 277 UK codes are mapped by
label against `activity_target_list.csv`, every row citing NATCEN Appendix H on the source side and
the target list on the target side, and **every UK code that cannot be mapped is listed in
`crosswalk_unmapped.md`, never guessed.** `G2.1` counts them.

🔴 **And the defect this creates:** the UK's own `group1` column is *not* the harmonised Level-1 — UK
sleep sits in the UK's division `1`, which in the target numbering is Employment. Carrying the source
`group1` through would put roughly eight hours a day of British sleep into "Employment", and **`G2.9`
would not fire** — it asks countries to *differ*, and that defect makes them differ more. `G2.16`
below is the executable form of rule 4.

**Location is not affected and needs no target list.** Per D-S2-3 the location target is the four
classes carried in `crosswalk_location.csv`'s `target_class` column, so national location codes map
straight to a class and there is no shared numeric location vocabulary to construct.

### D-S2-12 — the record contract of `harmonised.parquet`, one row per episode

Step 1 fixed its intermediate record and every later step gained from its being written down. Step 2's
output has been named in five places in this document and specified in none, and work item 2.4 cannot
be handed to anyone until it is.

```
country, wave, hid, pid, diary_day,
episode_index, episode_index_step1, split_at_origin,
start_min, duration_min,
act, act_level1, act_level2,
act2, act2_level1,
loc_class, indoor_presence,
cop_alone, cop_partner, cop_children, cop_parent, cop_other_hh, cop_other_persons,
cop_extra_<country>_<field> ...,
act_raw, act2_raw, loc_raw,
mode, scheme, weight_ind, weight_dia
```

🔴 **The raw fields are kept, and it is the same argument D-S2-8 used to keep the national parent
columns:** a transform that discards its inputs cannot be audited. `act_raw`, `act2_raw` and `loc_raw`
ride along so that any later reader can re-derive the mapping from the shipped table alone, and so that
`act2_raw`'s and `loc_raw`'s three states (M-1) survive rather than being flattened by harmonisation.

🔴 **`origin_hour` is NOT a column, in this table or any other.** D-S2-5 said so and said it in prose
only, where a runner cannot read it. A per-country origin column reaching Step 3 leaks country identity
into leave-one-country-out by the front door after D-S2-2 closed the back one. The native origin is
written to `filter_report.md` and to the parquet's file-level metadata, never to a row. **`V2.i` is the
executable form**, and it FAILs on any column whose name contains `origin`.

**Two index columns, because the rotation changes the episode count.** D-S2-5 warned that rotating
Spain to 04:00 splits the episode straddling the origin, so Spain's Step 2 episode count is a
*different quantity* from the 430,754 that `G1.1` pinned. `episode_index` is the Step 2 index within
the diary in 04:00-origin order; `episode_index_step1` is Step 1's, carried unchanged; and
`split_at_origin` is `True` on both halves of a split episode and `False` everywhere else. **`G2.12`'s
round trip is only mechanically possible because those three columns exist** — without them, rejoining
the halves would be guesswork.

**Types, stated because the defaults are wrong here.** The six `cop_*` flags and every
`cop_extra_*` are **nullable boolean**: `null` is *not recorded*, `False` is *recorded and absent*, and
per D-S2-2 collapsing them destroys the field paper 1 identified as the source of load
overestimation. `indoor_presence` is nullable boolean and is `null`, never `False`, where `loc_raw` is
in its *recorded and blank* state. `act` is a 3-character zero-padded string, never an integer -
`011` is not `11`. `act2` is 2-character, same rule. `act_level1` and `act2_level1` are 1-character
strings and are **always the first character of their own target code** (`G2.16`).

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

**Output:** `outputs_step2/crosswalk_activity.csv` + `crosswalk_unmapped.md`, 🔴 **and
`outputs_step2/activity_target_list.csv`, which D-S2-11 added: the target vocabulary is a shipped file
with two citations per row, not an assumption.**

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
| 🔴 `outputs_step2/activity_target_list.csv` *(D-S2-11)* | Step 2 validation (`G2.2`, `G2.16`, `V2.h`); Step 9's appliance mapping, which needs the 3-digit target |
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

### 2026-08-16 (later still) — 🔴 **D-S2-11: the crosswalk's *target* is decided, and it is not Eurostat's list**

Work item 2.1 has said "one target list" since the document was created and never said which one. It
could not survive contact with the build: **every mapping row must cite a page, and a row cannot cite a
page in a document we do not hold.**

**The finding that forced it.** Step 1's own emitted source lists were read directly and they are not
one list. Spain and Italy both code sleep `011` in division `0`; **the UK codes it `110` in division
`1`.** F-UK-10 had already said the UK list is *"the UK's own, not a verbatim Eurostat HETUS list"*
(NATCEN Appendix H), built for continuity with UKTUS 2000-01. So work item 2.1's expectation of "close
to the identity map" holds for **two of three countries and fails for the third** — and by that work
item's own sentence, that is a finding about the corpus rather than a licence to improvise.

**Decided.** The target is a shipped 3-digit file, `outputs_step2/activity_target_list.csv`, and a code
enters it only when **two of the three deliveries carry it with agreeing meaning**, each row carrying
both citations. Single-sourced codes are still targets but are flagged `single_source`. Same-code
disagreements go to `crosswalk_unmapped.md` as conflicts, resolved explicitly, never averaged.

🔴 **The two rejected alternatives are the informative part.** *Declaring "the Eurostat HETUS 2008 ACL"
the target* would make every row cite a document nobody here has read — `G2.2` would then be satisfied
by uncheckable citations, and **the gate written to catch an invented mapping row would be passing on
invented provenance.** *Adopting one country's list* — the UK's, or Spain's — would crosswalk two
countries and give the third a free pass, making that country's distribution the centre the other two
are pulled toward. That is the over-harmonisation failure `G2.9` exists to detect, installed
deliberately at design time so that `G2.9` would have to catch our own decision. Requiring two
deliveries to agree means no single country owns the vocabulary.

**Consequence, named now rather than discovered later:** the UK is the only country whose activity
crosswalk is real work. 277 codes mapped by label, each citing NATCEN Appendix H on the source side and
the target list on the target side; anything unmappable is listed, never guessed.

🔴 **And the defect that consequence creates.** The UK's own `group1` is not the harmonised Level-1.
Carried through unchanged it files roughly eight hours a day of British sleep under *Employment* — and
**`G2.9` does not fire on it**, because `G2.9` is a *floor* on cross-country disagreement and this
defect makes the countries disagree more. `G2.10` would catch it only once a published national table
is actually in hand, which is not yet true. `G2.16` is added for exactly this, with the perturbation
that carries `group1` through.

**Location is untouched** — D-S2-3 already maps national location codes straight to the four classes in
`crosswalk_location.csv`, so there is no shared location vocabulary to construct and none is invented.

**No threshold was moved. Step 2 is now sixteen gates, seventeen perturbations, `V2.a`-`V2.h`.**

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

*(Superseded 2026-08-17 by D-S2-18: Step 3 is **not** unblocked. The table carries no conditioning
strata, so Step 3's nine-field prefix has no source. See below.)*

---

## ✅ DECIDED 2026-08-17 — D-S2-17: **THE AGE FLOOR IS 11. THE AUTHOR HAS RULED.**

D-S2-13 moved the floor from 10 to 11 on a measured property of the Italian delivery — `claseta2`
band `03` is `6-10`, so a floor of 10 falls strictly inside a band and cannot be expressed — and it
did so by **reversing the author's own decision-16 move**. That reversal was carried as an open item
awaiting the author from 2026-08-16 to 2026-08-17.

**Ruling, 2026-08-17: the floor stays at 11.** The choice put to the author was not 10 against 11; it
was *an exact floor of 11 in all three countries* against *a floor of 10 that is exact for Spain and
the UK and a band edge for Italy*. The author took exactness.

🔴 **A deep-research round was offered and was declined, on the manager's recommendation, and the
reason is worth keeping.** The age floor is not a literature question. It is a property of a file we
hold, and an external report cannot see our data — anything it stated about our corpus would have
been quoted back from the prompt or invented. That is failure mode 1 of the eight in `RESUME.md`'s
"how to read a returned report", and commissioning a round here would have manufactured exactly the
kind of citable-looking support a decision like this does not need.

**Consequence: nothing rebuilds on this account.** `harmonised.parquet` was built at floor 11, the
battery ran against it, and both stand. The measured cost stays as recorded: **ES 155 respondents /
3,122 episodes, UK 340 / 20,251, IT 2,969 / 67,517**, Italy's larger loss being the band effect
D-S2-13 predicted. `filter_report.md` already carries the line that says so in terms.

**The standing-state line changes from "awaiting the author's confirmation" to "confirmed by the
author 2026-08-17."** It is no longer an open item anywhere.

---

## 🔴🔴 DECIDED 2026-08-17 — D-S2-18: **THE CONDITIONING STRATA ARE STEP 2 COLUMNS, AND `harmonised.parquet` HAS NONE OF THEM**

### What was found, and how

Step 3 was about to be handed to an employee. Before writing the prompt the manager checked that
Step 3's inputs exist, and they do not.

**Step 3's record is a nine-field conditioning prefix plus the episode tuple** (`4thJ_03_serialisation.md`,
work item 3.1): `country`, `age band`, `sex`, `household type`, `economic status`, `day type`,
`season`, `MODE`, `SCHEME`.

🔴 **`harmonised.parquet` supplies three of the nine.** Read directly from the shipped file's schema,
40 columns: `country`, `mode`, `scheme` are there. **`age band`, `sex`, `household type`,
`economic status`, `day type` and `season` are not, in any form.** The age variable was used by the
D-S2-13 filter and then discarded rather than carried.

**This is the same shape as the `ES`/`es` near-miss recorded in D-S2-16, and it is worth naming as a
class.** D-S2-12 specified the record contract and is correct about everything it lists. Work item
3.1 specifies the record format and is correct about everything it requires. **Neither document is
wrong; the defect lives between them**, and it was found by reading one against the other rather than
by reviewing either. That is now the third defect of this class in this project, after `G9.14`'s
missing half of F-ES-6 and the Step 4 / Step 6 fold-contract mismatch.

🔴 **`G3.7` would have caught it — after `corpus.jsonl` was built.** Prefix completeness is a
pre-registered Step 3 gate with a threshold of zero records missing a field, so the corpus would have
been emitted, the gate would have failed on 100 % of records, and the rebuild would have cost Step 3
in full. The gate was doing its job; it just sits downstream of the cheapest place to fix this.

### Why the fields cannot simply be dropped

The obvious cheap move is to cut the prefix to what we hold. **It is not available**, and the reason
is in the parent plan rather than in this step:

> **5B.** *"`RL09` resolves it rather than picking a side: because the conditioning prefix contains
> the design strata (country, age, sex, household type, economic status, day type, season), the
> sampling mechanism is conditionally ignorable for `P(diary | X)`."*

**Step 5's unweighted-loss argument is carried by the prefix containing the design strata.** Remove
household type and economic status and the argument for training without design weights no longer
holds, which reopens a decision that `RL09` closed and that Step 5, Step 6 and the methods section
all stand on. The seven strata are load-bearing, not decorative.

### The decision

**An additive round rebuilds the strata into Step 1's readers and Step 2's harmoniser.** Four parts,
in this order, and the order is not negotiable:

1. **Step 1's `codebook_facts_<country>.md` gains the six strata sources**, each with its document and
   page or sheet citation, exactly as every other fact in those files is carried. A variable that
   does not exist in a delivery is written **`NOT FOUND`** and stays that way. 🔴 **No stratum source
   may be named from `RL02`, `RL17` or from the other two countries** — each country is established
   from its own codebook, which is the rule three of the four D-S2-1..4 findings were created by
   breaking.
2. **Step 1's three readers carry the national source values**, unharmonised, one column per stratum.
   Nothing is banded, mapped or collapsed at Step 1. **Step 1 decides what is kept; Step 2 decides
   what is harmonised; Step 3 decides what is serialised** — the same three-way split D-S2-7 reserved
   and the 2.4 employee was reversed for pre-empting.
3. **Step 2 gains a fifth crosswalk, `crosswalk_strata.csv`**, and the six harmonised columns below.
   Every row carries its citation, and every unmapped source value is registered in
   `crosswalk_unmapped.md` exactly as the other four crosswalks do.
4. **Work item 2.4 re-runs, and the Step 2 battery re-runs on the rebuilt table.** 🔴 **A validated
   result does not transfer to a table with a different column set.** The re-run must return
   **exactly 2,024,068 rows** — ES 446,547, UK 567,381, IT 1,010,140 — **and exactly 37,830 / 0 / 0
   splits.** Adding columns may not move a single row. That is the same acceptance test the UK
   column-set re-run passed on 2026-08-16, and it is the test that proves the column set is not
   entangled with the transform.

### The six new columns, and their raw carriers

Added to the D-S2-12 record contract:

```
strat_age_band,  strat_sex,  strat_hh_type,  strat_econ_status,  strat_day_type,  strat_season,
strat_age_band_raw, strat_sex_raw, strat_hh_type_raw, strat_econ_status_raw,
strat_day_type_raw, strat_season_raw
```

🔴 **Every harmonised stratum ships beside the national value it was derived from.** This is the
D-S2-8 argument reused for the third time — **a transform that discards its inputs cannot be
audited** — and it is why `act_raw`, `act2_raw` and `loc_raw` ride along already. The `_raw` columns
are **not** serialised into the prefix; they exist so the mapping can be re-derived from the shipped
table alone.

**All twelve are per-person or per-diary-day constants**, repeated on every episode of that diary.
They are not episode properties and no gate may treat them as ones.

### 🔴 Three rules that must be fixed **now**, before the measurement, or they will be decided by convenience later

**Rule 1 — a stratum any country cannot supply is dropped from the prefix for ALL countries, never
for one.** If the UK has no season variable, the answer is not "the UK emits `unknown`" and it is not
"the UK's prefix has eight fields". A symbol only one country can emit is a country marker, and a
country marker inside a leave-one-country-out design measures our bookkeeping rather than transfer.
**This is D-S2-2's leak argument applied to the prefix**, and it is written here rather than left to
whoever hits the missing variable. The loss goes into the limitations, and if the dropped stratum is
`household type` or `economic status`, **Step 5's 5B has to be re-argued before anything is trained.**

**Rule 2 — the harmonised bands must be expressible in every country's own delivery, and Italy is the
binding constraint.** Italy's age arrives pre-banded in `claseta2`'s eleven bands, so **every target
age band must be a union of `claseta2` bands.** This is D-S2-13's rule generalised from one threshold
to a whole classification: *the finest banding any country can express exactly.* A target band that
splits an Italian band cannot be produced from the Italian file and would be produced anyway, wrongly,
by whoever writes the mapping.

**Rule 3 — the band set is proposed from the three codebooks and approved by the manager before it is
built.** The employee transcribes, proposes and **stops**. It does not choose the bands. A
classification chosen by the person implementing it, against the data in front of them, is chosen to
be easy to produce.

### What was verified for this decision, and what was not

**Verified directly by the manager**, from the files rather than from any report:

* `harmonised.parquet`'s 40 column names, read from the parquet schema. The six strata are absent.
* The three Step 1 parquets' column names. They carry **some** national sources already — ES `EDAD`,
  `SEXO`, `HRELACTIV`, `trim`; IT `sesso`, `claseta2`, `meseri`; UK `DVAge`, `DMSex`, `DiaryDay_Act`
  — **and none of the three carries a household-type variable of any kind.**
* `codebook_facts_spain.md` in full: its required-facts table covers the diary fields and **has no
  entry for household type, economic status, day of week or season.** The Spanish delivery does hold
  the sources — `DHOGAR` and `MHOGAR` are named under *File shape*, `DDIASEM` under *Diary days per
  respondent* — but they are not transcribed and not read.
* Italy's `codebook_facts_italy.md` names `gsett` as a **day-type** variable and `meseri` as a
  **quarter**, both measured as one distinct value per respondent. The UK's names
  `uktus15_household.tab` and `uktus15_individual.tab` as delivered files.

**NOT verified, and it is the employee's first task, not an assumption to inherit:** which variable
in each delivery carries **household type** and **economic status**, whether the UK ships a **month or
season** variable at all, and what `claseta2`'s eleven bands actually are. 🔴 **Nothing above may be
treated as a variable name to code against.** They are the places to look.

### Two new gates, pre-registered here **before** the columns exist

Written into `4thJ_02_harmonisation_val.md` as **`G2.17`** (completeness and grain, two sub-clauses)
and **`G2.18`** (leak and Italian expressibility, two sub-clauses), with **four** perturbations and
two guards — **`V2.j`**, which imports the band vocabulary from `crosswalk_strata.csv` and prints the
country × band cross-tab, and **`V2.k`**, which asserts the rebuilt table reproduces the accepted
table's four fixed counts. 🔴 **The order is the point and it is the same order `G3.14` followed:**
the columns do not exist yet, so no threshold here can have been chosen to be passed.

**Step 2 goes from sixteen gates to eighteen, from seventeen perturbations to twenty-one, and from
nine vacuity guards to eleven.** The
previous battery result is not carried forward: it was earned against a sixteen-column-narrower table
and it is re-earned or it is not claimed.

---

### 2026-08-17 — 🔴 **STEP 2 IS REOPENED, AND STEP 3 IS BLOCKED AGAIN**

Two decisions today. One closes an open item at no cost; the other costs a rebuild.

* **D-S2-17 — the age floor is confirmed at 11 by the author.** Nothing rebuilds. The last open item
  from the overnight round is closed, and a deep-research round offered for it was declined because
  the question is a property of a file we hold and no external report can see it.
* 🔴 **D-S2-18 — `harmonised.parquet` carries none of the six conditioning strata Step 3's prefix
  needs.** Found by reading Step 3's work item 3.1 against D-S2-12's record contract before writing
  the Step 3 employee prompt. Both documents are correct alone. **Step 2 reopens for an additive
  round, and the Step 2 battery re-runs on the rebuilt table.**

🔴 **What this changes about the claim "Step 2 is closed", stated plainly rather than netted off:**
the definition of done was met on all five points on 2026-08-16 and the battery result was real.
**It was met against a record contract that was missing something Step 3 needs**, which is a defect in
the contract, not in the execution. The 2026-08-16 closure entry is left standing and is not rewritten
— this log is append-only — and this entry is what supersedes it.

**What does NOT reopen, and must not be re-derived:** the four crosswalks, the indoor rule, the
co-presence value map, D-S2-5's 04:00 cyclic rotation, D-S2-13's age floor, D-S2-14's `start_min`
reference point, and every row count above. The additive round **adds columns and changes nothing
else**, and its acceptance test is exactly that: 2,024,068 rows and 37,830 / 0 / 0 splits, unchanged
to the row.

**Cost, stated before it is spent:** one codebook-transcription and reader round on three countries,
one harmoniser round, one 2.4 re-run, one battery re-run of eighteen gates and twenty-one
perturbations. **Against the alternative**, which is emitting `corpus.jsonl`, failing `G3.7` on 100 %
of records, and rebuilding Step 3 as well.

---

## 🔴 DECIDED 2026-08-17 — D-S2-19: **THE BAND SET IS APPROVED, AND `season` IS DROPPED FROM THE PREFIX FOR ALL THREE COUNTRIES**

Task A of the additive round returned: six strata transcribed from each country's own codebook, none
`NOT FOUND`, and a proposed band set with one stratum stopped and referred up. Deliverables:
`Step1_docs/outputs_step1/codebook_facts_{spain,italy,uk}_strata.md` and `strata_proposal.md`. The
manager rules below on each of the six. **Rule 3 of D-S2-18 is discharged by this entry** — the band
set is now approved and may be built.

### 1. `season` — DROPPED. The prefix is eight fields, not nine.

**The finding, which is a property of the deliveries and not of our mapping:** Spain delivers season
pre-banded as `TRIM`, calendar quarters (Jan-Mar / Apr-Jun / Jul-Sep / Oct-Dec) and ships **no
month-level field anywhere** to re-bin from (F-ES-9). Italy delivers `meseri` pre-banded as Nov-Jan /
Feb-Apr / May-Jul / Aug-Oct, coarsened by ISTAT's own protective recoding (F-IT-2) and not readable
any finer. **The two schemes are offset by exactly one month at every edge and share no boundary.**
Any target band must be a union of whole bands on both sides; since the two boundary sets are
disjoint, the only such band is the whole fieldwork year. The UK's native `dmonth` is irrelevant to
this — it can be aggregated to either scheme, but no aggregation of it makes Spain's and Italy's
schemes reconcilable to each other.

**The ruling: `season` is dropped from the conditioning prefix for all three countries.** A
single-valued `any_season` band is rejected: it costs prefix tokens on every record, carries zero
conditioning information by construction, and would put a field in the frozen prefix that a later
reader would reasonably assume was informative. **A stratum that cannot be measured is dropped, not
spelled as a constant.**

🔴 **This is a Rule-1 drop by consequence rather than by letter.** D-S2-18's Rule 1 names the case
where a country cannot supply the stratum at all; here all three supply one and no two of them can be
reconciled. The consequence is identical — no shared non-trivial classification exists — and the
repair is the one Rule 1 prescribes: **drop for all three, never keep it for the two that happen to
agree.** Keeping season for Spain and the UK on a calendar-quarter basis and giving Italy `unknown`
would be a country marker of exactly the kind D-S2-2 forbids.

**Does this reopen Step 5's `5B`?** No. `RL09`'s conditional-ignorability argument is carried by the
design strata, and D-S2-18 named **household type and economic status** as the two whose loss would be
consequential. Both survive. Season is a fieldwork-timing variable, not a sampling-design stratum in
any of the three deliveries. **It goes into the limitations** — the model is not conditioned on season
and cannot be asked for a seasonal contrast — and `5B` is not re-argued.

🔴 **`strat_season_raw` is still built and still shipped.** The national value rides along unmapped, in
the table and never in the prefix, so that the irreconcilability above can be re-derived from the
shipped table alone and so that a future round can re-band it if a finer Spanish or Italian delivery
is ever obtained. This is D-S2-8's argument in its weakest form: **we keep the input to a transform we
decided not to perform.**

### 2. The five surviving strata — APPROVED as proposed

| Stratum | Approved bands | Binding constraint |
|---|---|---|
| `strat_age_band` | `11-14, 15-24, 25-34, 35-44, 45-54, 55-64, 65-74, 75+` | Italy's eight populated `claseta2` bands at and above the D-S2-17 floor; Spain's `EDAD` and the UK's `DVAge` are exact ages and hit every boundary |
| `strat_sex` | `male, female` | none; `SEXO=6` is female in Spain, which is the kind of code that is wrong if assumed |
| `strat_day_type` | `weekday, saturday, sunday` | Italy's own `gsett` split; **the UK source is `ddayw`, not `DiaryDay_Act`** |
| `strat_econ_status` | `employed, unemployed, student, retired, homemaker, other_inactive, unknown` | Rule 3: Spain's incapacity-pension, widow/orphan-pension and volunteering codes are folded into `other_inactive` rather than kept as Spain-only bands |
| `strat_hh_type` | `one_person, couple_no_children, couple_with_children, single_parent_with_children, other_complex, unknown` | Rule 2: Italy's `tipfa2m` carries no child-age qualifier, so **no band may split on child age** even though Spain's `TIPOHOG` (cutoff 25) and the UK's `dhhtype` (cutoff 15) could each support one alone |

**The prefix, frozen, eight fields:** `country` · `strat_age_band` · `strat_sex` · `strat_hh_type` ·
`strat_econ_status` · `strat_day_type` · `mode` · `scheme`.

### 3. How the `unknown` band is scored, pre-registered here before it is measured again

`unknown` prevalence is not even across the three countries — economic status: **ES 0.0000 %, UK 0.5192 %,
IT 4.2435 %**; household type: **ES 0.0000 %, IT 0.0000 %, UK 3.5141 %** (🔴 **corrected under `D-S2-20` Q1(a), 2026-08-26**; this line previously read UK 6.3 % / IT 13.5 % / UK 3.6 %, wrong by 12× and 3× — re-derived from `harmonised.parquet`, 73,254 diaries, `weight_dia`). A band two countries emit and the third
never does is a partial country marker, and the question of whether that fails D-S2-18's Rule 3 has to
be settled **before** the gate runs rather than by whoever reads its output.

🔴 **The ruling: `G2.18`'s leak clause scores band *availability*, not band *prevalence*.** A band that
is declared for all three countries and producible from all three deliveries is not a country marker,
even where its observed prevalence is zero. **Rejecting `unknown` on prevalence would leave only two
repairs — impute, or drop the affected rows — and dropping rows is closed off by this round's own
acceptance test, which forbids moving a single row.** The per-country prevalence table is printed by
`V2.j` and carried into the limitations, where the asymmetry belongs; it is not netted off.

### 4. Three risks carried into Task B, each with its required behaviour

1. 🔴 **Italy's `tipfa2m` codes not enumerated in CLS-var16** — `12, 13, 17, 18, 26, 27, 31, 32` are
   gaps in the documented code list. **If any of them is observed in the raw file, the run FAILs and
   the code is registered in `crosswalk_unmapped.md`. It is never folded into `other_complex` because
   that is where unrecognised codes look like they belong.** This is the D-S2-1..4 class again: a
   value mapped from a neighbouring country's shape rather than from its own codebook.
2. **UK `dhhtype = 3` cannot distinguish a childless couple from a couple whose children are all 16+**
   (F-UK-18), where Spain's `TIPOHOG` separates `2` from `4`. This is a real measurement mismatch
   between the UK's field design and the other two, it cannot be closed from the delivered
   documentation, and it is **recorded as a limitation, not repaired.** `strat_hh_type_raw` ships so
   the affected rows remain identifiable.
3. **UK `deconact = -1` maps to `unknown`** on the generic "not applicable" reading, which is the only
   reading the delivered dictionary supports. Stated as an assumption, not as an established fact.

### 5. What this changes about the additive round's arithmetic

**Eleven new columns, not twelve: five harmonised strata plus six `_raw` carriers.** `strat_season` is
not built; `strat_season_raw` is. `harmonised.parquet` goes **40 → 51 columns.**

🔴 **The four fixed row counts do not move.** 2,024,068 rows, ES 446,547 / UK 567,381 / IT 1,010,140,
splits 37,830 / 0 / 0, 73,254 diaries tiling `[0, 1440)` exactly once, `act2` nulls 587. Dropping a
stratum from the prefix drops a column, never a row. **Every acceptance test of D-S2-18 stands
unchanged except the column count.**

`4thJ_03_serialisation.md`'s work item 3.1 and its `G3.7` field list are amended to the eight-field
prefix. `V3.h` in `4thJ_03_serialisation_val.md` anticipated exactly this — it was written to count
the fields the corpus actually ships against the frozen list rather than against the number nine — and
needs no amendment.


---

## Additive round — Task B outcome (2026-08-17, late)

The build landed. Recorded here rather than left in an agent's context, per the no-parking /
state-on-disk rule now in `CLAUDE.md`.

### 1. The rebuilt table, as read from the file

**2,024,068 rows and 51 columns.** ES 446,547 / UK 567,381 / IT 1,010,140; splits 37,830 / 0 / 0;
`act2` nulls 587; 73,254 diaries tiling `[0, 1440)` exactly once; eleven `strat_*` columns present and
**no `strat_season`**, `strat_season_raw` shipping as D-S2-19 requires. Every one of the four frozen
counts held. The column count is the only thing that moved.

Step 1 gates re-ran verdict-for-verdict identical to the accepted run `run_20260816-2210`: Spain 15
scored / 15 PASS / 15 seen failing / `G1.7b` NOT CHECKED, Italy 13 scored with `G1.6b` still FAILing,
the UK 14 scored with `G1.4` still FAILing. **Both standing FAILs are confirmed unrepaired** — they
are the same two we already carry, not new damage from the additive round.

### 2. Three build failures, and what they were

All three were repaired and superseded; none is an open gap. They are kept here because each is a
class of defect the next reader should expect, not because any is outstanding.

1. **Italy `tipfa2m` is zero-padded in the raw file** (`08`, not `8`) while the codebook prose is
   unpadded. The reader built from the prose and matched nothing.
2. **UK `dhhtype` / `deconact` spell blank as a literal single space**, `" "`, not `""`.
3. 🔴 **Italy `newcondm` carried the same space sentinel, and the reader's own alphabet check could
   not see it** — the check called `.str.strip()` before comparing, which silently repaired the value
   it was supposed to catch. The defect surfaced one step downstream as a crosswalk-join failure with
   39,515 unmapped rows. **A validator that normalises its input before testing it cannot fail**, and
   this is the same family as the gates that cannot fail because their reference derives from the
   source they audit. It was caught only because D-S2-16's join assertion exists.

A fourth, non-data mistake: the first Italy and UK gate batteries ran in a directory missing
`parse_report_<country>.txt`, which scored `G1.5` as `NOT CHECKED` instead of PASS. **It was caught by
comparing gate *counts* against the reference run, not pass/fail totals** — a battery that silently
scores one gate fewer looks clean. Worth keeping as a check on every future battery.

### 3. Three assumptions the task doc did not decide — all three ACCEPTED

1. **Run-stamped provenance directory `run_20260817-strata`**, mirroring the accepted round. Accepted.
2. **Step 1's household-type join hard-FAILs on any unmatched row** (Spain), rather than only
   asserting the match is non-zero. Accepted — strictly stronger than D-S2-16 asks, and additive.
3. **An unmapped `strat_*` value FAILs the harmoniser rather than being nulled, for every stratum.**
   Accepted, and it is not optional: `G2.17 (a)` requires zero nulls in every shipped `strat_*`
   column, so nulling an unmapped value would only move the failure downstream into a gate. This
   generalises risk 1 above from `tipfa2m` to all six strata.

### 4. What is not done

The Step 2 battery — `G2.17`, `G2.18`, `V2.j`, `V2.k`, eighteen gates and twenty-one perturbations —
**has not run.** It is deliberately a different session from the one that built these columns.

---

### 2026-08-17 (night) — MANAGER'S MERGE NOTE: Task B's Step 2 fragment, appended verbatim below

Merged from `Step2_docs/outputs_step2/proglog_strata_step2.md`, the D-S2-18 / D-S2-19 additive round.
🔴 **Appended verbatim and unedited, append-only, not reordered.**

**What the manager verified independently:** that `harmonised.parquet` carries the eleven new columns
and that all eight prefix fields resolve for every record — established not from this fragment but
from two downstream Speed jobs (1255349, 1255620) that read the table fresh and serialised all eight
into 73,254 corpus records with a 100 % exact round-trip. **Zero rows and zero diaries were dropped by
either loader**, which is the check `V3.i` exists for and is the reason the table's row counts are
trustworthy: 446,547 / 1,010,140 / 567,381.

🔴 **NOT verified:** the 127 rows of `crosswalk_strata.csv` one by one, any single band assignment
against its source codebook, or the `unknown` declarations for the country/stratum pairs measured at
0.0 % prevalence. The fragment's own reasoning for those — **availability, not prevalence** (D-S2-19
§3) — is accepted as the decision it implements, not as a verified fact about the data.

**Two things a later reader will be tempted to get wrong.**

1. **`season` carries no rows in `crosswalk_strata.csv`, and that is correct, not a gap.** D-S2-19
   dropped it because Spain's `TRIM` and Italy's `meseri` are each delivered pre-banded and **offset
   by one month at every edge, sharing no boundary**, so the only band expressible in all three
   countries is the whole year. A degenerate `any_season` band was rejected: **a stratum that cannot
   be measured is dropped, not spelled as a constant.**
2. **`country` is `ES`/`UK`/`IT` in the parquet and `es`/`uk`/`it` in every crosswalk** (D-S2-16).
   Lowercase before any join, and FAIL loudly on a zero-match join rather than returning an empty
   result set. This has already been a near-miss once.

**Still open on Step 2 and awaiting the author, neither of them a blocker to Step 3:** whether
`G2.18`'s escalation clause should carry a whole-gate FAIL when `leak_bands = 0` (and whether
D-S2-19's quoted 6.3 % / 13.5 % should be corrected to **0.519 % / 4.243 %**), and whether to repair
the `scale_duration` → `G2.4` clean violation.

🔴 **2026-08-26 — BOTH WERE RE-MEASURED AND ARE NOW DOCKETED AS `D-S2-20`:**
`Step2_docs/impl/2026-08-26_D-S2-20_the-two-standing-step2-questions.md`. The correction is
confirmed from the parquet (**0.5192 % / 4.2435 %**, robust to the weight choice; `6.3 % / 13.5 %` is
wrong by 12× and 3×). 🔴 **`FINDING 151` changes what question 1 asks**: in both strata one
country's `unknown` share is exactly **0.0000 %**, so `tools/4thJ_gates_step2.py:1068`'s
`smallest_other * 10.0` bar is **0.0** and *any* positive share escalates — the ten-times threshold is
inert, and the gate is reporting a zero denominator, not a large imbalance. Recommendations: **1(a)**
keep the FAIL and publish `FINDING 151` with it; **2(a)** add the weight-scaling perturbation that can
separate `G2.3` from `G2.4`.

---

## Progress Log fragment — Task B, Step 2 (M-8 / D-S2-18 / D-S2-19 additive round)

**Fragment for the manager to merge. Not the Progress Log itself.**

### What was built

* `Step2_docs/outputs_step2/crosswalk_strata.csv` — the fifth crosswalk, 127 rows,
  `stratum, country, source_value, source_label, target_band, citation`. Built from
  `strata_proposal.md` and the three `codebook_facts_<country>_strata.md` files (Task A, accepted),
  against D-S2-19's approved band set. `season` carries **no rows** (dropped from the prefix,
  D-S2-19 §1). `unknown` is declared for `strat_econ_status` and `strat_hh_type` **for all three
  countries**, including the two country/stratum pairs measured at 0.0 % prevalence (Spain, both
  strata; Italy, household type) — per D-S2-19 §3, availability, not prevalence, is what matters.
  `strat_age_band`/`strat_sex`/`strat_day_type` carry no `unknown` row for any country (0.0 %
  measured, all three, all three strata; not part of the approved band set).
* Extended `tools/4thJ_harmonise_step2.py`: reads `crosswalk_strata.csv`, emits the five harmonised
  columns (`strat_age_band`, `strat_sex`, `strat_hh_type`, `strat_econ_status`, `strat_day_type`)
  beside the six `_raw` carriers. `strat_season_raw` ships with no harmonised partner. Age mapping is
  an exact categorical crosswalk join for Italy (already banded, `claseta2`) and a numeric-range
  `pd.cut` for Spain/UK, with bin edges parsed directly from the crosswalk's own `"11-14"`/`"75+"`
  style rows rather than hardcoded separately. Every stratum join asserts a non-zero match count and
  FAILs loudly (raises `SystemExit`) on any raw value not present in the crosswalk (D-S2-16) — no
  stratum may resolve to a silent null. `country` is lowercased via the existing
  `COUNTRY_CROSSWALK_TAG` mechanism already in the harmoniser (unchanged from D-S2-16's original fix).
* Italy's `tipfa2m` gap-code guard: if any of the eight undocumented CLS-var16 codes
  (`12,13,17,18,26,27,31,32`) is observed unmapped for `strat_hh_type`/it, the harmoniser FAILs
  explicitly rather than folding it into `other_complex`. **Measured this round: all eight occur 0
  times** in `uso_tempo_Microdati_Anno_2013_Individui.txt` (44,866 rows; 32 distinct non-blank
  `tipfa2m` codes observed, exactly the CLS-var16-documented set). The guard did not fire. Recorded
  in `crosswalk_unmapped.md` PART E with the measured frequency either way, per the task's explicit
  instruction.

### Three defects found and fixed, all caught by the pipeline's own refuse-rather-than-assume design
### (full detail in the Step 1 fragment)

1. Italy `tipfa2m` is zero-padded 2-digit — caught by the Step 1 reader's own domain check (job
   1254922 FAILed). Corrected in `crosswalk_strata.csv`'s `strat_hh_type`/it rows and the reader.
2. UK `dhhtype`/`deconact`'s blank sentinel is a literal single space, not an empty string — caught
   by the Step 1 reader's own domain check (job 1254923 FAILed). Corrected in the reader; the
   crosswalk's declared blank→`unknown` rows already used `""`, so no crosswalk change was needed.
3. **Italy `newcondm`'s blank sentinel is also a literal single space** — caught one step later, by
   **this harmoniser's own crosswalk-join assertion** (job 1254934 FAILed: `strat_econ_status (it):
   39515 episode(s) have a raw value not in crosswalk_strata.csv: [' ']`), not by the Step 1 reader,
   because the reader's own alphabet check used `.str.strip()` (which silently normalises `" "` to
   `""`) while the emitted raw column did not. This is the exact class of near-miss D-S2-16 exists to
   catch: a join that would otherwise have produced 39,515 silent nulls instead FAILed loudly.
   Corrected in the Step 1 reader (re-run, job 1254940), then the Italy harmoniser re-ran clean
   (job 1254952).

None was a policy question — all three were data-format mistakes in the crosswalk/reader I built,
fixed against the measured raw file rather than coded around.

### B5 acceptance test — the four fixed numbers, all confirmed exactly

| | ES | UK | IT |
|---|---|---|---|
| **episodes (target / measured)** | 446,547 / **446,547** ✅ | 567,381 / **567,381** ✅ | 1,010,140 / **1,010,140** ✅ |
| **splits (target / measured)** | 37,830 / **37,830** ✅ | 0 / **0** ✅ | 0 / **0** ✅ |

🔴 **Note on the "splits" unit**: the harmoniser's own log line ("splits at origin for es: 18915")
counts split *events* (one 04:00-crossing Spanish episode → two output rows). The task's acceptance
figure (37,830) counts *rows carrying `split_at_origin=True`* — two per event, `18,915 × 2 = 37,830`
— confirmed directly on the combined table (`combined.groupby("country")["split_at_origin"].sum()`).
Same underlying result, two different units; not a discrepancy.

**Combined `harmonised.parquet`**, built locally (`py`, not the cluster — a concatenation of three
already-computed parquets, same precedent as the 2026-08-16 combine): **2,024,068 rows, 51 columns**
(40 → 51, eleven new: five harmonised `strat_*` + six `strat_*_raw`, no `strat_season`). **73,254
diaries**, every one tiling `[0,1440)` exactly once (0 gap/overlap rows, 0 diaries not summing to
1440, checked directly on the combined table, not assumed from the per-country logs). **`act2` nulls
= 587** (exact). **Only `split_at_origin` contains "origin"** in any column name (checked directly:
`[c for c in combined.columns if "origin" in c.lower()] == ['split_at_origin']`). Age floor 11, passed
explicitly (`--age-floor 11`, no default) to all three harmoniser jobs.

Every stratum's crosswalk join matched 100 % of episodes for all three countries (printed by the
harmoniser and re-checked against the per-country `filter_report_<country>.md` addenda): ES 446,547/
446,547, UK 567,381/567,381, IT 1,010,140/1,010,140, for all five harmonised strata.

### Deliverables

`crosswalk_strata.csv`, updated `tools/4thJ_harmonise_step2.py`, `harmonised_{es,it,uk}.parquet`,
combined `harmonised.parquet` (51 columns), this fragment, plus a strata-specific addendum written
into each per-country `filter_report_<country>.md` (crosswalk join match counts per stratum).

### WHAT I DID NOT VERIFY

* I did **not** run the Step 2 gate battery (`G2.17`/`G2.18`/`V2.j`/`V2.k`) — per the task document,
  that is explicitly a different employee session's job, and running it here would make the
  column-build and the gate-scoring the same session, which the task forbids.
* I did not re-derive the other four crosswalks (activity, secondary activity, location, co-presence)
  or touch anything in the D-S2-12 base record contract — this round is additive by construction and
  the acceptance test (four fixed row counts, 51 columns, unchanged) is the check that the rest of
  the table was not disturbed.
* I did not independently verify that `crosswalk_strata.csv`'s citations resolve to the exact page/
  sheet named — they are copied from `codebook_facts_<country>_strata.md`'s own citation column,
  which I did not re-derive from the source documents myself (Task A's job, already accepted).
* Whether the `strat_econ_status`/`strat_hh_type` `unknown`-band prevalence asymmetry
  (ES 0.0000 %/UK 0.5192 %/IT 4.2435 % for econ status; ES 0.0000 %/IT 0.0000 %/UK 3.5141 % for household
  type — 🔴 corrected under `D-S2-20` Q1(a), 2026-08-26) is
  missing-at-random or structurally concentrated — not investigated here; D-S2-19 §3 already rules
  that this is scored on availability, not prevalence, so it does not gate this round, but the
  underlying data question is still open per `strata_proposal.md`'s own "WHAT I DID NOT VERIFY".
* The two named limitations D-S2-19 §4 requires carrying rather than repairing: UK `dhhtype=3`
  cannot separate a childless couple from one whose children are all 16+ (F-UK-18), and UK
  `deconact=-1` → `unknown` is the generic "not applicable" reading, an assumption. Both are recorded
  in `crosswalk_strata.csv`'s `source_label`/`citation` fields for the affected rows, not resolved.

---

### 2026-08-20 (night) — 🔴 **`FINDING 53`: THE THREE COUNTRIES' DIARY WEIGHTS TARGET THREE DIFFERENT DAY BASES, AND ONLY THE UK IS CALENDAR-REPRESENTATIVE.** Read-only measurement on `harmonised.parquet`; nothing rebuilt, no gate re-run, no verdict changed.

**How it surfaced.** `Resources/preprocessing_precedents.md` §5 recommends the 4J equivalent of the
2nd paper's per-wave category-share file. Built as `tools/4thJ_prefix_category_shares.py` →
`outputs_step2/prefix_category_shares.txt`. It re-derived every logged stratum claim exactly
(`FINDING 48` at 710/711, 1644/1644, 896/896; `D-S5-3`'s `75+` at es 58.9 / it 72.0 / uk 95.4 %;
`D-S3-14`'s UK `strat_hh_type = unknown` at 3.48 % = 551 diaries) — **and then showed something
nobody had looked at: `strat_day_type` is not on a common basis.**

⚪ **A unit trap caught on the way.** The first build deduplicated on `hid` and produced household-level
shares that silently contradicted every logged figure. **A diary is `(country, pid, diary_day)`** —
`hid` is the household, `pid` alone is the person, and the UK has 1.998 diaries per person. The fixed
key gives 73,254 diaries from 2,024,068 episodes, `ES=19,140 / IT=38,260 / UK=15,854`, and every
logged number then reproduces to the unit. The script now names its key in its own header.

#### The finding

| | weekday | saturday | sunday | what it is |
|---|---|---|---|---|
| a calendar week | 71.43 % | 14.29 % | 14.29 % | — |
| **`uk`** (`weight_dia` = `dia_wt_a`) | **71.45 %** | 14.32 % | 14.24 % | 🟢 the calendar week |
| **`es`** | **50.02 %** | 25.00 % | 24.98 % | 50/25/25, exact |
| **`it`** | **33.33 %** | 33.33 % | 33.33 % | one third each, exact |

🔴 **All three hit their figure to two decimals, so all three are deliberate design targets, not
sampling noise.** Unweighted the picture is different again (`es` 60.80 / `it` 34.50 / `uk` 50.12 %
weekday), which is the point: the weights are doing real work, just not the same work.

🔴 **This is the Step 1 `dia_wt_a` reasoning applied to one country only.** §1.3 chose `dia_wt_a` over
`dia_wt_b` with the explicit argument that *"Day of week is load-bearing for this paper… a weight
with no day-of-week adjustment would carry whatever day-type imbalance the fieldwork left, straight
into the thing we are modelling."* Measured: `weight_dia_b` puts the UK at **50.14 / 25.02 / 24.84**
— i.e. `dia_wt_b` is the UK's *Spanish-shaped* weight, and the decision to reject it was right. But
**ES and IT have no `_a` equivalent at all**: `weight_dia_a` and `weight_dia_b` are `ALL NULL` for
both. The imbalance the UK decision removed is still fully present in the other two folds.

#### What it moves, measured

At-home share of time, published weights against a calendar basis:

| | unweighted | published weight | calendar | published − calendar |
|---|---|---|---|---|
| `es` | 69.909 % | 69.552 % | 68.605 % | **+0.947 pp** |
| `it` | 72.694 % | 72.667 % | 71.367 % | **+1.300 pp** |
| `uk` | 70.267 % | 68.738 % | 68.741 % | **−0.003 pp** |

🔴 **Small in absolute terms, but country-correlated and zero for exactly one fold.** The published
weights overstate at-home time by 1.3 pp for Italy and 0.95 pp for Spain and by nothing for the UK,
on the single quantity this paper exists to produce. In LOCO that moves a fold's score for a reason
that has nothing to do with the model. ⚪ The `uk` row being −0.003 pp is the check that the
post-stratification method is right, not a result.

🔴 **It lands directly on `D-S6-3` item 2.** Whatever day basis the Eurostat scoring tables use, **at
most one of our three countries currently matches it.** This has to be settled before the first fold
is scored, and it is item 1 of `Prompts/previous/DECISIONS_OPEN_all13_ruled_2026-08-20.md` (all 13 items ruled `(a)` and applied 2026-08-20; it was `Prompts/DECISIONS_OPEN.md` when this entry was written).

#### The fix, if ruled

Post-stratification to the calendar week. Factors measured, not estimated:

| | weekday | saturday | sunday |
|---|---|---|---|
| `es` | ×1.4281 | ×0.5714 | ×0.5718 |
| `it` | ×2.1429 | ×0.4286 | ×0.4286 |
| `uk` | ×0.9998 | ×0.9979 | ×1.0034 |

🟢 **Additive form:** a NEW column `weight_dia_cal`, leaving `weight_dia` untouched, so **no Step 1 or
Step 2 gate is disturbed and nothing already passed has to be re-run.** Not applied — it is a basis
change and it is the author's to rule.

#### ⚪ A latent trap found at the same time: `diary_day` means three different things

| country | values | meaning |
|---|---|---|
| `es` | 1-7 | day of the week |
| `it` | 1-3 | the day **type** (1 weekday, 2 saturday, 3 sunday) |
| `uk` | 1-2 | **which of the respondent's two diaries** — not a day at all |

Cross-tabulated against `strat_day_type`, `es` and `it` are deterministic and `uk` is not (diary 1 is
3,937 weekday / 1,835 saturday / 2,160 sunday). **Nothing currently reads `diary_day` as a day of
week, so this is a latent trap and not a live bug** — but it is exactly the "same column, different
meaning per wave" class the precedent index records at
`Resources/preprocessing_precedents.md` §6 (GSS 2005 `80` against 2010 `80.1`), and it is why that
section says the crosswalk is per wave even when the variable name is identical.

#### ⚪ One quoted figure confirmed on its basis

`FINDING 51` quotes the Spanish corpus at **11.140 % homemaker**. Re-derived: that is the
**diary-weighted** share. Unweighted it is 11.996 % and person-level 11.996 %. The census comparison
(8.787 %) is a population share, so weighted-against-weighted is the right pairing and the finding
stands as written. ⚪ `it` is the country where the weighting moves homemaker most: 12.739 %
unweighted against **14.827 %** weighted.

**Nothing was rebuilt.** `harmonised.parquet` is untouched; the new file is a diagnostic that nothing
downstream reads.


#### 🟢 2026-08-20 (execution pass) — RULED `(a)` AND APPLIED

The author ruled item 1 as `(a)`. `weight_dia_cal` is now a column in `harmonised.parquet` and in
the three per-country files. **All three countries sit at `71.4286 / 14.2857 / 14.2857` on it and
each country's total weight is unchanged (rel diff <= `1.8e-16`)**, so it re-allocates across day
types rather than rescaling a country. ⚪ `89` UK episodes (2 diaries) carry a null `weight_dia`;
`weight_dia_cal` is null for exactly those and never `0.0`.

🟢 **Additivity proved twice rather than asserted.** On read-back all `51` pre-existing columns are
bit-identical (`41`/`44`/`48` in the per-country files), and **the full 18-gate battery was re-run
at baseline: every verdict line is byte-identical to the accepted 2026-08-17 run, the only
difference anywhere in the report being `V2.i`'s column listing, which now ends `'weight_dia_cal'`
and still PASSES.** ⚪ `G2.18` still FAILs `(a)` with the identical string — pre-existing, not a
regression.

New md5s: `harmonised.parquet` `54a53a5f82189194cdcc7fe873cded7b` (was
`2eb0d05fcd89e9e8ff8c983d6062d920`), `_es` `58da43376e29d80a5aeb32d4e7ebb341`, `_it`
`5be19d6282272d200c0fb59a3405c5f5`, `_uk` `c15576cbe51fcc37f5e819bd00534ec7`. Originals kept in
`outputs_step2/_bak_f53/`. No script anywhere hard-codes the old value.

🔴 **`weight_dia` is untouched, and this column does NOT settle what Step 6 scores on.**
`FINDING 54` (Step 6 doc) established that **no Eurostat table carries a day-type dimension**, so
the published tables sit on an undeclared national basis that cannot be selected. Which weight the
scoring reads is `D-S6-4`, and it is open.
