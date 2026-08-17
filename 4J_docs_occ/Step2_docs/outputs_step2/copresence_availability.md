# Co-presence availability — Step 2, work item 2.3

### Companion to `crosswalk_copresence.csv`. Read alongside D-S2-2, D-S2-8, D-S2-9 in
### `4thJ_02_harmonisation.md`. Gate G2.8 reads the country × flag grid below; its wording is
### exactly the two strings `recorded` and `not recorded`, nothing else.

---

## COUNTRY × FLAG GRID — all six shared flags

| country | cop_alone | cop_partner | cop_children | cop_parent | cop_other_hh | cop_other_persons |
|---|---|---|---|---|---|---|
| es | recorded | recorded | recorded | recorded | recorded | recorded |
| uk | recorded | recorded | recorded | recorded | recorded | recorded |
| it | recorded | recorded | recorded | recorded | recorded | recorded |

All eighteen cells are `recorded`. Per D-S2-8, the widening from five shared flags to six was forced
by measurement: all three countries turned out to field parent co-presence (Spain in one field,
`PADRES`; the UK and Italy each as an OR of two fields), so `cop_parent` is not a flag any country
fails to record. **No cell in this grid is `not recorded`.** The distinction that matters for this
corpus is not "which flag is missing" but "which flag's row-level value can be genuinely missing"
(see the section below on explicit missingness) and "how the recorded definitions diverge" (the
children-flag section below).

---

## COUNTRY-EXTRA COLUMNS

| country | extra column | source field | what it is |
|---|---|---|---|
| es | *(none)* | — | Spain's six national fields map onto the six shared flags with no field left over: `SOLO`→`cop_alone`, `PAREJA`→`cop_partner`, `MENOR`→`cop_children`, `PADRES`→`cop_parent`, `OTMH`→`cop_other_hh`, `OTCON`→`cop_other_persons`. |
| uk | `cop_extra_uk_mother` | `WithMother` | The mother component of the `cop_parent` OR, kept as its own column because an OR that discards its inputs cannot be audited (D-S2-8). |
| uk | `cop_extra_uk_father` | `WithFather` | The father component of the `cop_parent` OR, kept for the same reason. |
| uk | `cop_extra_uk_na` | `WithNA` | "Sleep/Work/Education UK2000 concordance" — a backward-compatibility marker, **not** a presence flag and **not** missingness (see below). Carried as a named extra rather than folded into anything. |
| it | `cop_extra_it_madre` | `cmadre` | The mother component of the `cop_parent` OR. |
| it | `cop_extra_it_padre` | `cpadre` | The father component of the `cop_parent` OR. |
| it | `cop_extra_it_siblings` | `cfrate` | "With siblings." A genuine Italian extra — no other country fields a siblings co-presence flag. |

`WithMiss` (UK) is **not** listed as an extra here. It is a row-level missingness indicator that
applies across all six shared flags at once, not a co-presence category with its own semantic
content — see `crosswalk_copresence.csv`, `shared_flag=NOT_A_PRESENCE_FLAG`.

Per D-S2-2, **Step 5 may not condition on any extra column**, because a country-specific flag cannot
be a conditioning variable in a leave-one-country-out design.

---

## HOW EACH NATIONAL DEFINITION DIFFERS FROM THE SHARED FLAG

Most of the six shared flags are close translations of a "who is present" question and differ only
in wording (`SOLO`/`WithAlone`/`daso` all mean "alone"; `PAREJA`/`WithSpouse`/`cconiu` all mean "with
a spouse or partner"). Two flags carry a real definitional difference, and one of the two is the one
that matters most.

### `cop_children` — three different definitions, and the difference is not removable

| Country | Field | Cut-off | Where older children go |
|---|---|---|---|
| Spain | `MENOR` | **under 10**, living with you (a household-composition test) | `OTMH`, other household members |
| UK | `WithChild` | **0-7 years only** (verbatim DD label, `Pos.=44`) | `WithOther`, "other person(s) (incl. child 8+ years)" — verbatim DD label, `Pos.=45`, confirmed also by CTUR p. 11-12 §5.2: "only time with a child 0-7 years could be reported. Time with children 8-9 and 10-14 years will be reported as time with other members of the household." |
| Italy | `cfigli` | **no age bound stated anywhere in the delivery** | nowhere — Italy's flag has no spillover mechanism because it has no cut-off |

🔴 **Spain and the UK share a *structure*** — a cut-off, with the remainder spilling into the
household-others flag — **and differ only in where the cut sits, two years apart (10 vs. 8).**
Italy does not share that structure at all: it records "with children" without any stated age
boundary.

🔴 **`cop_children` may not be compared across countries in any step, gate or the paper.** A lower
UK prevalence than Spain's is the expected mechanical consequence of the UK's narrower 0-7 cut-off
against Spain's under-10 cut-off, not a finding about British or Spanish households. **Any Spain-UK
comparison that is nonetheless made must state the 10-versus-8 cut-off in the same sentence** it is
made in. This is a corpus limitation, reported in the methods per D-S2-8/D-S2-9, not a defect this
crosswalk can fix — the UK's 8-and-9-year-olds are already pooled into `WithOther` in the delivered
file and are not recoverable by any crosswalk.

### `cop_parent` — recorded as one field in Spain, as an OR of two fields in the UK and Italy

Spain's `PADRES` is a single field. The UK (`WithMother` OR `WithFather`) and Italy (`cmadre` OR
`cpadre`) each split parent co-presence by which parent. The OR is audited by keeping both national
components as their own extra columns (see above); no information is discarded in the packing, only
in the six-flag summary itself, which is the summary's job.

### The other four flags

`cop_alone`, `cop_partner`, `cop_other_hh` and `cop_other_persons` are recorded by all three
countries with no stated age bound, household-membership test or other qualifier beyond "who was
present" — no comparable divergence was found in the sources available to this task. This is not
the same claim as "the underlying survey instruments ask the question identically" (see WHAT I DID
NOT VERIFY in `proglog_step2_location_copresence.md`).

---

## NOT STATED IN CODEBOOK

* **Whether `WithOtherYK` absorbs any part of the UK's 8-and-over children population.** Neither the
  UK data dictionary's variable label for `WithOtherYK` ("With other(s) you know outside of HH") nor
  CTUR §5.2 addresses whether a child aged 8+ who is known to but not resident with the household
  would fall under `WithOtherYK` rather than `WithOther`. Both sources describe the split only as
  `WithChild` (0-7) against `WithOther` (8+, household members). Not assumed either way.
* **The literal Spanish and Italian codebook sentences defining each co-presence flag** (beyond the
  field's own name and, for Spain, the `1`/`6` Sí/No coding; for Italy, the empirically-established
  blank/ordinal domain). The LAYOUT workbook (`DISEnOS DE REGISTRO EET 2009 2010.xlsx`) and the
  METH PDF for Spain, and the TRACC-DG HTML for Italy, were not part of the file set delivered to
  this task — only `codebook_facts_spain.md`, `codebook_facts_italy.md` and their glosses were
  available. See `proglog_step2_location_copresence.md`, "WHAT I DID NOT VERIFY".

---

## EXPLICIT MISSING IS NOT ZERO

🔴 Per D-S2-2, widened by D-S2-8: **a flag a country never recorded is explicitly missing, never
0.** Zero means "recorded and absent" — the respondent was asked (in effect) and the flag was not
set. Missing means "not recorded" — the field carries no information at all for that episode.

In this corpus, after the six-flag widening, **no country fails to record any of the six shared
flags** (see the grid above), so the "flag never recorded, whole-column" case does not arise here.
But the same discipline applies at the **row level**, and it bites in exactly one place: the UK's
`WithMiss`. Where `WithMiss=1`, **all six of the UK's shared flags are MISSING for that episode, not
0** — CTUR p. 6 §3.2: "Co-presence data is deemed missing if the respondent provided no information
about co-presence in any time slot... a missing co-presence field has been added to the data to aid
with this." Spain and Italy declare no missingness column at all, so for them a flag is missing only
when the field is literally absent from the record (Italy's blank-space sentinel, F-IT-4); Spain has
no missing state for co-presence — every Spanish episode is "recorded" (M-1-style three-state
discipline).

🔴 **Collapsing "missing" into "0" is exactly the defect paper 1 identified as a source of load
*over*estimation**, and it is the reason `crosswalk_copresence.csv` never restates a value map: the
value map lives in that file and is imported, never duplicated, by whatever reads it (V2.f).

---

## LOCATION ASYMMETRY NOTE (ES vs. IT, D-S2-4)

Recorded here in addition to `crosswalk_unmapped_location.md`'s judgement-call table, because the
work order names this file explicitly for it. Per D-S2-4, Spain's location code `11` merges the
dwelling with the garage, vegetable plot, garden and grounds attached to it — one code covers both
what is inside the conditioned volume and what is outside it. **Italy splits what Spain merges**:
code `11` ("Casa propria") is the dwelling itself, and code `12` ("Casa propria, spazi aperti") is
its open/outdoor spaces. `crosswalk_location.csv` maps **both** Italian codes to `at_home`, so the
harmonised four-class location scheme reproduces Spain's merge rather than losing it. This means
Italy's location field alone already carries a piece of the indoor/outdoor distinction that, for
Spain, depends entirely on the `OUTDOOR_AT_HOME` activity-code exclusion list in
`outdoor_at_home.csv`. The asymmetry is real, is not resolved by this crosswalk (both countries end
up at the same four target classes, as D-S2-3 requires), and should be kept in mind by whoever
implements `indoor_presence = (LOC == 11) AND (ACT not in OUTDOOR_AT_HOME)` at the *class* level
(`target_class == at_home`) rather than the raw-code level.

---

## CODES I CONSIDERED AND REJECTED (outdoor_at_home.csv)

Recorded here, as the work order for `outdoor_at_home.csv` (deliverable 2) instructs. Candidates
examined and **not** added to `outputs_step2/outdoor_at_home.csv`, with the reason each was rejected
rather than guessed into the list:

| Country | Code | Label | Reason rejected |
|---|---|---|---|
| es | 343 | Cuidado de mascotas | "Pet care" — no basis in the label to say this happens outdoors rather than indoors (feeding, grooming); distinct from code 342, which is included. |
| es | 351 | Construcción, renovación de la vivienda | "Construction, renovation of the dwelling" — the label does not distinguish interior renovation from exterior/structural work; unlike code 322 ("exteriores de la vivienda"), there is no "exterior" qualifier here to anchor an outdoor classification. |
| es | 352 | Reparaciones de la vivienda | "Dwelling repairs" — same reasoning as 351: no exterior/interior qualifier in the label. |
| es | 354 | Mantenimiento de vehículos | "Vehicle maintenance" — plausibly done in a driveway or garage, but the label gives no basis to say it is outdoors rather than in an attached garage (which D-S2-4 already folds into `at_home` regardless); not added on label evidence alone. |
| it | 343 | Cura degli animali domestici | "Care of domestic/pet animals" — the explicit contrast with code 342 ("da cortile/allevamento", yard/farmyard animals, included) implies 343 is the indoor/pet case; rejected on that contrast. |
| it | 351 | Costruzione e ristrutturazione della propria abitazione | "Construction and renovation of own dwelling" — general, no "esterne" qualifier; ambiguous indoor/outdoor, same reasoning as Spain's 351. |
| it | 352 | Riparazioni nella propria abitazione: pitturare pareti, riparare impianti, ecc. | The label explicitly says "**nella** propria abitazione" (**inside** one's own dwelling) — this is explicitly indoor, not merely unclear, and is excluded on that stronger basis. |
| it | 353 | Costruzione, riparazione e cura di mobili o altri beni della propria abitazione | Furniture/household-goods repair — ordinarily an indoor activity; no outdoor qualifier in the label. |
| it | 354 | Manutenzione e riparazione di veicoli | "Vehicle maintenance and repair" — same reasoning as Spain's 354. |

A genuinely borderline case that **was** included, for transparency about the judgement: **code 342**
(`es Cuidado de animales domésticos` / `it Cura degli animali da cortile/allevamento`). Italy's label
at the same code position explicitly names "animali da cortile/allevamento" (yard/farmyard animals),
which is unambiguously outdoor; Spain's terser label at the same numeric position ("animales
domésticos") was read as the same category, since the two countries' lists share the same numbering
under D-S2-11 and Italy's fuller wording disambiguates Spain's terser one for the same code. This is
a defensible but not certain inference and is flagged as a judgement call rather than presented as
self-evident from either label alone.
