# Strata proposal — Task A2, D-S2-18 / M-8

### Proposed, not built. No crosswalk file exists yet; this is the input to the manager's decision,
### per D-S2-18 Rule 3. Sources are `codebook_facts_spain_strata.md`,
### `codebook_facts_italy_strata.md`, `codebook_facts_uk_strata.md` — read those for citations;
### this document does not repeat them in full.

Three rules bind every proposal below (D-S2-18 / this task's A2), restated here so each stratum's
verdict can be checked against them directly:

* **Rule 1** — a stratum any one country cannot supply is dropped for all three. Not triggered for
  any of the six strata: all six exist in all three deliveries.
* **Rule 2** — every target band must be a union of Italy's own bands wherever Italy delivers a
  stratum pre-banded. Italy pre-bands **age** (`claseta2`), **day type** (`gsett`) and **season**
  (`meseri`). Italy does **not** pre-band sex, household type or economic status — those three are
  raw categorical codes with no forced banding, though household type still has its own
  cross-country expressibility problem (below).
* **Rule 3** — a band only one country would emit is a defect, repaired by coarsening.

---

## 1. AGE — clean, Rule 2 satisfied exactly

**Proposed bands:** Italy's own eight populated `claseta2` bands at and above the age-11 floor
(D-S2-13/D-S2-17): `[11-14, 15-24, 25-34, 35-44, 45-54, 55-64, 65-74, 75+]`. `claseta2`'s three
sub-floor bands (`fino a 2`, `3-5`, `6-10`) are never populated post-filter and are not part of the
target set.

**Per-country source:**

| Target band | Spain (`EDAD`) | Italy (`claseta2`) | UK (`DVAge`) |
|---|---|---|---|
| 11-14 | `11 <= EDAD <= 14` | `04` | `11 <= DVAge <= 14` |
| 15-24 | `15 <= EDAD <= 24` | `05` | `15 <= DVAge <= 24` |
| 25-34 | `25 <= EDAD <= 34` | `06` | `25 <= DVAge <= 34` |
| 35-44 | `35 <= EDAD <= 44` | `07` | `35 <= DVAge <= 44` |
| 45-54 | `45 <= EDAD <= 54` | `08` | `45 <= DVAge <= 54` |
| 55-64 | `55 <= EDAD <= 64` | `09` | `55 <= DVAge <= 64` |
| 65-74 | `65 <= EDAD <= 74` | `10` | `65 <= DVAge <= 74` |
| 75+ | `EDAD >= 75` | `11` | `DVAge >= 75` |

Spain and the UK ship exact ages and can hit every one of Italy's eight boundaries exactly — no
band splits an Italian band, satisfying Rule 2 by construction. **`unknown` prevalence: 0.0 % in
all three countries** (measured, all three age fields fully populated).

---

## 2. SEX — clean, no rule bites

**Proposed bands:** `male`, `female`.

| Target | Spain (`SEXO`) | Italy (`sesso`) | UK (`DMSex`) |
|---|---|---|---|
| male | `1` | `1` | `1` |
| female | `6` | `2` | `2` |

**`unknown` prevalence: 0.0 %** in all three countries (measured, all three sex fields fully
populated, no sentinel observed).

---

## 3. DAY TYPE — clean once Italy's pre-banding is respected

**Proposed bands:** `weekday`, `saturday`, `sunday` — Italy's own `gsett` bands, verbatim (Rule 2:
Italy pre-bands this stratum to exactly these three).

| Target | Spain (`DDIASEM`) | Italy (`gsett`) | UK (`ddayw`, not `DiaryDay_Act`) |
|---|---|---|---|
| weekday | `1`-`5` (Mon-Fri) | `1` | `1` |
| saturday | `6` | `2` | `2` |
| sunday | `7` | `3` | `3` |

🔴 **The UK source is `ddayw`, not the already-carried `DiaryDay_Act`.** `ddayw` is UKDA's own
pre-collapsed weekday/Saturday/Sunday derived field (F-UK-17) and requires no further collapsing;
`DiaryDay_Act` (7-way) would need the same Mon-Fri grouping Spain's `DDIASEM` needs. Both UK fields
ride along as `_raw`/extra columns; `ddayw` is the proposed harmonisation source.

**`unknown` prevalence: 0.0 %** in all three countries (measured, all three day-type fields fully
populated).

---

## 4. SEASON — 🔴 Rule 2 blocks anything finer than a single band. Manager decision required.

**Finding, stated before a proposal:** Italy's `meseri` (Nov-Jan / Feb-Apr / May-Jul / Aug-Oct)
and Spain's `TRIM` (Jan-Mar / Apr-Jun / Jul-Sep / Oct-Dec, standard calendar quarters) are each
delivered pre-banded, and their boundaries are offset from each other by exactly one month at
every edge. Neither is a union of the other's bands. Spain carries no month-level field anywhere
in its delivery to re-bin from (F-ES-9); Italy is pre-banded by disclosure control and cannot be
read any finer (its own documentation states protective recoding was applied, `codebook_facts_italy.md`
F-IT-2). The UK alone ships a native month (`dmonth`) and could be aggregated into either
scheme — but aggregating the UK to match one country's quarters would still leave the *other*
country's quarters unreachable, since the two countries' own bandings do not share a common
non-trivial coarsening. **The only band set that is simultaneously a union of Italy's bands and
producible from Spain's `TRIM` is the single band spanning the whole fieldwork year.**

**Rule 2 does not name this exact situation** — it addresses one country splitting a band, not two
countries' own pre-banded schemes being mutually irreconcilable — but the consequence is the same:
no non-trivial target season classification is expressible in all three deliveries. 🔴 **This is
reported as a case for the manager, not resolved here, per this task's instruction to stop rather
than pick the convenient repair.** Two options, stated without a recommendation between them:

1. **Collapse season to one band** (`any_season`) for all three countries — technically satisfies
   Rules 1-3 but removes the stratum's entire conditioning value, and D-S2-18's own argument for
   why the seven design strata are load-bearing (Step 5's `RL09`) did not anticipate a degenerate
   single-valued stratum.
2. **Drop season from the prefix for all three countries**, on the same footing as a Rule-1 drop,
   even though technically every country supplies *some* season field — the fields just cannot be
   reconciled to a shared non-trivial banding. If season is dropped, the manager should confirm
   this does not reopen Step 5's `5B` argument the way dropping household type or economic status
   would (D-S2-18 says the loss is consequential specifically for those two; season was not named
   there).

**`unknown` prevalence, for reference regardless of which option is taken: 0.0 %** in all three
countries (all three season fields fully populated).

---

## 5. ECONOMIC STATUS — proposed, with a flagged missingness imbalance

**Proposed bands:** `employed`, `unemployed`, `student`, `retired`, `homemaker`, `other_inactive`,
`unknown`. Six substantive bands chosen as the coarsest common structure all three raw fields can
support without inventing a category no country's documentation names.

| Target band | Spain (`HRELACTIV`) | Italy (`newcondm`) | UK (`deconact`) |
|---|---|---|---|
| employed | `1` Ocupado/a | `1` Occupato | `1,2,3,5` (employee FT/PT, self-employed, other employment) |
| unemployed | `2` Parado/a | `2` In cerca di occupazione | `6` Unemployed (ILO) |
| student | `3` Estudiante | `5` Studente | `8` Student |
| retired | `4` Jubilado/a, prejubilado/a | `7` Ritirato dal lavoro | `7` Retired |
| homemaker | `8` Realizando tareas del hogar | `4` Casalinga | `9` Looking after family/home |
| other_inactive | `5,6,7,9` (incapacity/widow-orphan pension, volunteering, other inactivity) | `8` In altra condizione o inabile al lavoro | `10,11,13` (long-term sick/disabled, other reasons, under 16) |
| `unknown` | *(none — 0 % blank)* | blank `newcondm` | blank, `-9`, `-8`, `-1` |

🔴 **Rule 3 note:** collapsing Spain's incapacity pension (`5`), widow/orphan pension (`6`) and
social volunteering (`7`) into `other_inactive` alongside Italy's and the UK's single "other"
catch-alls is a genuine loss of Spain-specific detail, but keeping them separate would make three
of Spain's nine codes bands only Spain could ever emit — exactly the Rule-3 defect the task
requires repairing by coarsening rather than noting.

🔴 **`unknown` prevalence is concentrated, and it is not even across countries — flagged for the
manager per the task's explicit instruction:**

| Country | `unknown` count | Denominator | Prevalence |
|---|---|---|---|
| Spain | 0 | 25,895 | **0.0 %** |
| Italy | 6,067 | 44,866 | **13.5 %** |
| UK | 722 | 11,421 | **6.3 %** |

Italy's rate is roughly double the UK's and Spain carries none at all. Whether this reflects a
genuine data-collection difference (e.g. Italy fielding the question to a broader population that
includes more non-respondents) or a difference in how "blank" was defined at extraction is not
established here (see `codebook_facts_italy_strata.md`, "what is not established").

---

## 6. HOUSEHOLD TYPE — proposed, with the largest Rule 2/3 cost of the six strata

**Proposed bands:** `one_person`, `couple_no_children`, `couple_with_children`,
`single_parent_with_children`, `other_complex`, `unknown`. 🔴 **This band set does not distinguish
child age**, even though Spain (`TIPOHOG`, cutoff 25) and the UK (`dhhtype`, cutoff 15) each could
support *some* age-conditioned split on their own — because Italy's `tipfa2m` carries no age
qualifier on "children" anywhere in its code list (F-IT-16), so a target band that split on child
age could not be produced from the Italian file (Rule 2).

| Target band | Spain (`TIPOHOG`) | Italy (`tipfa2m`) | UK (`dhhtype`) |
|---|---|---|---|
| one_person | `1` | `1` | `1` |
| couple_no_children | `2` | `6,7,20,21` | `3`\* |
| couple_with_children | `3,4` | `8,9,22,23` | `2`\* |
| single_parent_with_children | `5,6` | `10,11,14,15,16,19,24,25,28,29,30,33` | `4,5`\* |
| other_complex | `7,8` | `2,3,4,5,34,35,36,37,38,39,40` | `6,7,8` |
| `unknown` | *(none — 0 % blank)* | *(none — 0 % blank)* | blank |

\* 🔴 **F-UK-18: the UK's `dhhtype=3` ("no children ≤15") cannot be told apart from a UK household
whose only children are 16+.** Spain's own `TIPOHOG` distinguishes truly childless (`2`) from
grown-children-only (`4`) households; the mapping above puts UK `3` under `couple_no_children`
and UK `2` under `couple_with_children`, which is right for households with a young child and right
for a genuinely childless couple, but **silently wrong for a UK couple whose children are all 16+**
(they would be coded `couple_no_children` here despite living with adult children, where the
Spanish/Italian equivalent household would be coded `couple_with_children`). This is a real,
documentation-confirmed measurement mismatch between the UK's field design and Spain's/Italy's,
not a gap in this transcription, and it cannot be closed from the delivered documentation alone.

🔴 **`unknown` prevalence:**

| Country | `unknown` count | Denominator | Prevalence |
|---|---|---|---|
| Spain | 0 | 9,541 households | 0.0 % |
| Italy | 0 | 19,093 households | 0.0 % |
| UK | 411 | 11,421 persons (household-level field, read at person grain) | 3.6 % |

Not heavily concentrated relative to the economic-status stratum, but worth carrying forward since
it is UK-only among the three.

---

## SUMMARY — every case where a D-S2-18 rule bit

* **Rule 1** (a country cannot supply the stratum at all): did not bite. All six strata exist in
  all three deliveries.
* **Rule 2** (target bands must be a union of Italy's own bands): bit on **age** (satisfied
  cleanly — Italy's 8 bands became the target), **day type** (satisfied cleanly — Italy's 3 bands
  became the target, sourced from the UK's matching `ddayw` rather than the coarser `DiaryDay_Act`),
  and **season** (🔴 **not satisfiable** beyond a single degenerate band — stopped, reported above,
  manager decision required). It also constrained **household type**, indirectly: Italy's
  `tipfa2m` carries no child-age qualifier, which is why the proposed household-type bands do not
  split on child age even though Spain and the UK could otherwise support it.
* **Rule 3** (a band only one country would emit is a defect, repair by coarsening): bit on
  **economic status** (Spain's three narrower inactive-pension codes folded into one
  `other_inactive` band alongside Italy's and the UK's single catch-alls) and on **household type**
  (the same coarsening logic, plus the UK's `dhhtype=3` ambiguity noted separately as a residual
  risk rather than a Rule-3 violation, since it is a definitional gap rather than a country-unique
  band).

**Stratum requiring a stop-and-report per this task's A2 instructions: SEASON.** No band set finer
than "whole year" satisfies Rule 2 across Spain and Italy's own pre-banded fields, and the choice
between dropping the stratum entirely and keeping a degenerate one-band placeholder is left to the
manager, per Task A3.

---

## WHAT I DID NOT VERIFY

* Whether the economic-status and household-type coarsening schemes proposed above are the ones
  the manager wants — these are proposals per Task A2, not decisions; A3 requires stopping here.
* Whether `newcondm`'s 13.5 % blank rate and `dhhtype`'s 3.6 % blank rate are missing-at-random or
  structurally correlated with any other stratum (e.g. concentrated in one age band or one region)
  — only the aggregate rate was measured, in the country-specific codebook files.
* What UK `deconact = -1` specifically represents, beyond the generic "item not applicable"
  sentinel meaning shared across the UK dictionary — not resolved from the delivered documentation.
* Whether Italy's `tipfa2m` codes not listed in the condensed table above (there are gaps in the
  numbering — e.g. codes `12`, `13`, `17`, `18`, `26`, `27`, `31`, `32` do not appear in CLS-var16's
  own enumeration) indicate additional real categories this proposal has folded incorrectly, or
  are simply unused code points. The condensed mapping above uses only the codes CLS-var16 actually
  lists; it was not cross-checked against `tipfa2m`'s full observed value set in the raw file
  beyond confirming 0 blanks and household-grain constancy (F-IT-15).
* No `sbatch` job was run and no cluster access was used for this task — all measurements above
  were made against the local unpacked delivery copies at `_local_runs/4J/raw/{spain,italy,uk}/`,
  consistent with Task A's own statement that it should need no job at all.
