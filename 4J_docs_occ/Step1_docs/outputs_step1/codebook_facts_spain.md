# Codebook facts — Spain, INE *Encuesta de Empleo del Tiempo* 2009-2010

### Step 1, work item 1.2. Every fact below names the document and page or sheet it came from.
#### Compiled 2026-08-14 from the delivery itself. **No fact here comes from `RL01`, `RL02` or `RL17`.**

Two sources, both downloaded on 2026-08-14 and hashed in `acquisition_manifest.json`:

* **LAYOUT** — `DISEnOS DE REGISTRO EET 2009 2010.xlsx`, inside `disreg_emptiem0910.zip`.
  Cited as LAYOUT, sheet, row.
* **METH** — *Encuesta de Empleo del Tiempo 2009-2010. Metodología*, INE, 127 pages,
  `https://www.ine.es/metodologia/t25/t25304471.pdf`. Cited as METH p. N.

A fact that could not be found in either is written `NOT FOUND` and stays that way.

---

## THE REQUIRED FACTS

| Fact | Value | Where it came from |
|---|---|---|
| **File shape** | **Relational.** Eight fixed-width ASCII files: `DHOGAR` household, `MHOGAR` household members, `CINDIV` individual questionnaire, `DIARIO1` diary header, `DIARIO2` diary slots, `HTR1`/`HTR2` weekly work schedule, `SD` domestic-service module | LAYOUT, sheet *Diseños de registro*, rows 11-26 |
| **Native `START` / `DURATION`?** | **No.** The diary is delivered as **144 fixed 10-minute slots per diary**, one row per slot, indexed by `INTERVALO`. Episodes must be reconstructed | LAYOUT, sheet *F DIARIO2*, rows 27-31 and footnote row 65 |
| **Weight variables** | `FACTORF` in `DIARIO2`, `DIARIO1`, `CINDIV`, `MHOGAR`, `HTR1`, `HTR2`; `FACTOR_hogar` in `DHOGAR` and `SD`. Sixteen digits: **6 integers and 10 decimals** | LAYOUT, sheet *F DIARIO2*, row 63; sheet *F DHOGAR*, row 69 |
| **Activity coding list, edition** | The HETUS activity coding list in Spanish translation, nested to three digits. INE calls it the *Lista EET* and does not print an edition year | LAYOUT, sheet *F DIARIO2*, rows 32-33; METH pp. 66-71 |
| **Activity coding list, depth** | **3 digits.** Ten one-digit major groups, 33 two-digit subdivisions. INE's prose says **115** three-digit groups; the enumeration in Annex I contains **116**, and the delivered file uses exactly those 116. See the discrepancy note below | METH p. 22 for the prose; METH pp. 66-71 for the list; measured from `DIARIO2` for the file |
| **Location coding list** | 2-digit. `00` unspecified, `10-14` places at or around a dwelling and workplace, `21-29` other specified places, `30-39` private transport, **`41` public transport**. 20 codes in all | METH pp. 124-126 |
| **Co-presence fields** | 🔴 **Six, not five:** `SOLO`, `PAREJA`, `PADRES`, `MENOR`, `OTMH`, `OTCON`. Each coded **1 = yes, 6 = no** | LAYOUT, sheet *F DIARIO2*, rows 43-59 |
| **Slot length** | 10 minutes | LAYOUT, sheet *F DIARIO2*, row 27 |
| **Diary origin hour** | 🔴 **06:00.** `INTERVALO` 1 is 06:00-06:10 and `INTERVALO` 144 is 05:50-06:00 | LAYOUT, sheet *F DIARIO2*, rows 28-31 |
| **Minimum age** | **10.** One individual questionnaire and one diary per household member aged 10 or over | METH pp. 46 and 50 |
| **Diary days per respondent** | **1** | Measured: every `IDHOGAR`+`NPERS` appears once in `DIARIO1`, with one `DDIASEM`. Consistent with METH p. 46, one diary per member |
| **Collection mode** | **Paper, self-completion.** The diary is filled in by the respondent (*autocumplimentación*); the individual questionnaire is a personal interview or self-completion; the instruments are pre-printed paper questionnaires | METH pp. 46 and 50 for self-completion, p. 56 for "cuestionario papel" |

---

## COUNTS AS INE STATES THEM, AND AS WE MEASURED THEM

INE prints its own record counts, which is what makes gate G1.1 possible without asking anyone.

| File | INE states | We measured | |
|---|---|---|---|
| `DHOGAR` households | 9,541 | 9,541 | ✅ |
| `MHOGAR` household members | 25,895 | 25,895 | ✅ |
| `CINDIV` individual questionnaires | 19,295 | 19,295 | ✅ |
| `DIARIO1` diaries | 19,295 | 19,295 | ✅ |
| `DIARIO2` slots | 2,778,480 | 2,778,480 | ✅ |
| `HTR1` weekly schedules | 8,445 | not read this round | — |
| `HTR2` schedule days | 59,115 | not read this round | — |
| `SD` domestic-service persons | 1,025 | not read this round | — |

Source for the "INE states" column: LAYOUT, sheet *Diseños de registro*, rows 12-26. Every count
reconciles exactly, and each file's byte size is a whole multiple of its declared record width plus
CRLF, which is an independent way of arriving at the same number.

---

## 🔴 FINDINGS THAT CONTRADICT WHAT THE PLAN ASSUMES

These are recorded here, not acted on. Steps 2 and 3 are where they are resolved.

### F-ES-1 — the diary day starts at **06:00**, not 04:00

`Step2_docs/4thJ_02_harmonisation.md` lists "04:00 origin" as decided. Spain's diary runs 06:00 to
06:00. Nothing in the delivery lets a 04:00-origin day be built from a Spanish diary: the two hours
from 04:00 to 06:00 belong to a **different calendar day** than the one the respondent reported on.
This is a harmonisation decision, and it is one the manager has to take rather than the reader.

### F-ES-2 — co-presence has **six** flags in Spain, and one of them is not in the five-flag scheme

`RL02` reported five binary flags and Step 2 work item 2.3 is written around five: alone, partner,
children, other household members, other persons. Spain fields six. The extra one is **`PADRES`, with
a parent**, and `MENOR` is narrower than "children": it is *minors under 10 who live with you*.

The reader emits all six as named columns rather than packing them into the five-slot `cop_raw[5]`
of the intermediate-record contract. **That is a deliberate deviation from the Step 1 specification,**
taken because the alternative was to discard a recorded field. It needs a manager's decision before
Step 2. Collapsing `PADRES` into "other household members" is the obvious move and it is wrong for a
Spanish multigenerational household, which is exactly the case the flag exists to mark.

### F-ES-3 — location `41` sits outside the range the plan assumes

Step 2 records `RL02`'s claim as "10-19 stationary, 20-39 transport". The Spanish list is not built
that way:

* `10-14` are places: `11` home, `12` second home, `13` workplace or school, `14` someone else's home;
* `21-29` are **also places**, not transport: restaurant, shops, hotel, beach or pool, sports centre,
  street or open country, other specified place;
* `30-39` are **private** transport modes;
* **`41` is public transport** and is the only code above 39.

A filter written as `10 <= LOC <= 39` would silently drop **every public-transport episode** and would
mislabel seven stationary place codes as travel. `41` is observed in the delivered file.

### F-ES-4 — `RL02`'s home-code warning is confirmed, and it is worse than stated

METH p. 124 defines code `11` as "*Casa, garaje, huerta, jardín, finca..., siempre que esté situado en
el edificio de la vivienda o adosado a ella*" — house, garage, vegetable plot, garden or grounds, as
long as they are in or attached to the dwelling building. **It also says explicitly that working from
home is coded `11`.** So `11` merges the conditioned volume with the garage, the garden and the plot.
Presence in the conditioned volume is not recoverable from the location field alone, which is the
correction Step 2 work item 2.2 exists to carry.

### F-ES-5 — INE's own activity-group count is off by one

METH p. 22 says the classification has "10 groups, 33 and 115 groups" at one, two and three digits.
The Annex I enumeration on pp. 66-71 lists **116** three-digit codes, and the delivered `DIARIO2` uses
**exactly those 116**, no more and no fewer. The prose is wrong, not the list and not the file.
Recorded because a later step that trusts the sentence over the enumeration would build a 115-symbol
vocabulary and refuse one real code.

### F-ES-6 — secondary activity is recorded and the Step 1 record has nowhere to put it

`ASECU` is non-blank on **340,269 of 2,778,480 slots**, 12.2 %. The intermediate record specified in
Step 1 carries `act_raw` only. Nothing was dropped silently — the count is in the parse report — but
the contract has no field for it and the manager has to decide whether Step 3 wants one.

### M-1, 2026-08-15 — `loc_raw` sentinel table (required by the sixteen-gate specification)

Spain fields `LUGAR` on every one of the 2,778,480 `DIARIO2` slots (measured directly; the reader's
own V1.d refusal would raise if any slot's `LUGAR` were blank, and it never has). **There is no
delivery-declared missingness sentinel for `LUGAR`.** Per the sixteen-gate specification, "there is no
rule that negative values are sentinels and none may be invented" — no value is added to this table
without a citation to INE's own text, and none has been found.

| Field | Sentinel value | Delivery's own label | Citation | Measured count |
|---|---|---|---|---|
| `LUGAR` (`loc_raw`) | *(none declared)* | — | — | 0 of 2,778,480 slots / 0 of 430,754 episodes |

Consequence: `loc_raw` is state 3 ("recorded with a value") on all 430,754 Spanish episodes, confirmed
independently by `G1.12`'s raw recount from `DIARIO2` (own offsets, own first-of-run rule), which
matches the emitted parquet exactly.

### M-4, 2026-08-15 — weighting convention (required by the sixteen-gate specification)

**Convention: expansion.** METH p. 37 (the estimator definition, section on population estimation):
*"y d_j es el peso o factor de elevación"* — "and d_j is the weight or **expansion factor**." This is
the textbook definition of an expansion weight (a count of population units the sampled unit
represents), not a weight normalised to mean 1. Corroborated, not derived from, the observed
magnitudes: `FACTORF` ranges 264.94 to 113,238.82 (G1.7d), consistent with representing thousands of
real people per weighted respondent — but the convention is established from INE's own text, per the
work order's instruction, not inferred from this range. `G1.7d`'s bound is `[1.0, 10^6)`, from
`FACTORF`'s declared 6-integer-digit layout width (LAYOUT, sheet *F DIARIO2*, row 63).

### F-ES-7 — the entry point in `RL01` does not exist

`RL01` gives `cid=1254736176860` under `/dyngs/INEbase/es/operacion.htm`. That URL returns **HTTP
404**. The working operation is `cid=1254736176815` and the path carries no `/es/` segment. The
downloads themselves are at `https://www.ine.es/ftp/microdatos/emptiem/`. Recorded because the report
presented the dead URL as a Tier 1 read-in-full source.

---

## WHAT IS **NOT** ESTABLISHED HERE

* The activity list has been transcribed from INE's Spanish annex. It has **not** been aligned to the
  Eurostat HETUS ACL code by code. It looks like the same classification and it is nested the same
  way, but "looks like" is not a crosswalk, and the crosswalk is Step 2 work item 2.1.
* `HTR1`, `HTR2` and `SD` were not read. They are not inputs to any step in this pipeline.
* Nothing here says whether Spain is comparable to the other three countries. That is Step 2.
