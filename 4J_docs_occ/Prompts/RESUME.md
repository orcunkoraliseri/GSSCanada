# 4J — MANAGER RESUME PROMPT

### Hand this to the next session as its first message. Fixed path, edited in place, never duplicated.
#### Last updated: 2026-08-15, after the Steps 4-9 audit, the four-fold Step 4 rewrite, Speed job 1245620, the Step 1 gate re-run that closed Spain, the arrival of the UK and Italian data, both parallel Step 1 rounds returning, and **the M-1 to M-5 decision round — Step 1 is now a SIXTEEN-gate specification and the next employee round is written and ready to run on Speed**.

---

## 🔴🔴 AUTHOR DECISION 16, 2026-08-15: **FRANCE IS EXCLUDED. THE CORPUS IS THREE COUNTRIES.**

*"Maintenant nous n'avons pas la France, et quand elle va venir je ne sais pas — exclure France sur les
plans et continuer. Je ne veux pas attendre une ou deux semaines de plus."* Progedo demande n°38663 has
no published turnaround and no arrival date. **The project does not wait on it.**

**The corpus is Italy 2013-14, Spain 2009-10, UK 2014-15. All three are built.** This amends decisions
6 and 11; it does not reopen 5, 13 or 15. Full text in the parent plan's progress log, last entry.

| Was | Is |
|---|---|
| Four countries | 🔴 **Three** |
| Four-fold rotation, LOCO trains on three | 🔴 **Three-fold, LOCO trains on TWO** |
| 6 Leg-5 + 4 Leg-4 jobs | 🔴 **5 Leg-5 + 3 Leg-4** |
| Step 8: four populations | 🔴 **three** |
| `V1.a` / `V2.a` FAIL below 4 | 🔴 **below 3** |
| C4: four countries, trains on three | 🔴 **C4: three, trains on two** |
| Step 2 age floor 11 (France's minimum) | 🔴 **10** (Spain's), by the same rule re-evaluated |

🔴 **`V1.a` moving 4 → 3 is the one change that must not be read as a gate fix.** It is decision 6 in
executable form and it moved **only** because the author moved decision 6, in writing, on a dated line.
**It is not a `--single-country` flag and it is not a precedent.** Every other guard keeps its
threshold.

✅ **The pre-named fold does NOT move: still held-out SPAIN.** The alphabetical-ISO rule (ES, FR, GB,
IT) returns ES with or without France, so the pre-registration written before anything was trained
survives untouched. 🔴 Had the rule selected France, the honest move would have been to re-run the rule
and say so loudly — never to slide to the next-best fold.

🔴 **If France arrives later — decided now, because deciding it later is the defect.**

* **Before any fold has been SCORED:** re-admit it in full, the corpus returns to four, every count
  above reverts. **This is the only window in which France can become training data.**
* **After the first fold is scored:** the design is frozen by decision 11. France becomes an **extra
  held-out country, reported separately** as an out-of-design transfer test. Never a fourth fold, never
  averaged into the rotation.
* **The window closes at Step 6's first score, not Step 4's first submission.** The two dates are weeks
  apart and the tempting reading is the later one.

**What this unblocks, and it is the point:** `V1.a` stops firing, **Step 1 becomes closable** as soon
as the sixteen-gate re-run passes, and **Step 2 is no longer blocked**. 🔴 **The critical path is now
entirely ours** — Step 1 re-run → Step 2 → Step 3 → training — with no queue in another institution on
it.

**What gets worse, stated rather than netted off:** LOCO on two training countries is the thinnest
version of this test that is still a test. C4 is rewritten. Track A rises in value again: 3 → 17 is a
larger multiple than 4 → 17.

**And still true:** there is no `corpus.jsonl` yet, because Steps 2 and 3 have not run. **Free capacity
on Speed does not shorten the path. Do not start a training job to use up an allocation.**

---

## YOUR ROLE

You are the **manager** on paper 4 (4J). You plan, you vet, you write specifications and employee
prompts. **You do not implement.** One employee round has run — Step 1 on Spain, 2026-08-14 — and its
output is in `../Step1_docs/outputs_step1/`. The next moves are the three remaining acquisitions, four
decisions the Spanish file forced, and one gate that has to be redesigned.

Read `../4thJ_00_HETUS_LLM_Pipeline.md` before doing anything else. It is 1,800 lines and it is the
only authority. `../4thJ_00_HETUS_LLM_Pipeline_Overview.md` is the map; the step folders
`../Step0_docs/` to `../Step9_docs/` are the working specifications.

---

## THE PAPER, IN FIVE LINES

Fine-tune **one open-weight LLM** on HETUS-harmonised time-use diary microdata so that it generates
activity-resolved occupant schedules for **any** country in the framework, and test that claim by
**holding one country out of training entirely**. Output drives EnergyPlus residential archetypes.

It exists because paper 1 (CENTUS, *Energy and Buildings* 357, 117155) **claimed HETUS
standardisation as the route to cross-national transfer and never tested it.** That untested sentence
is this paper.

---

## 🔴 STATE: SPAIN, THE UK AND ITALY ARE BUILT — **AND THAT IS NOW THE WHOLE CORPUS**

🔴 **Read the decision-16 block above first.** Everything below this line was written while France was
still expected, and where it says *"`V1.a` fires on three of four"* or *"France is the only acquisition
left"*, **that is superseded**. It is kept because the reasoning about the deliveries, the gates and
the heterogeneities is all still live — only France's status changed.

Updated 2026-08-14. **Step 1 has been executed on Spain, end to end.** The INE *Encuesta de Empleo del
Tiempo* 2009-2010 is downloaded and hashed, its codebooks are transcribed with citations, the reader
is written, and `episodes_spain.parquet` exists: **19,295 diaries, 2,778,480 slots, 430,754 episodes,
zero unparsed rows.** ✅ **The gate battery has since been redesigned and re-run, 2026-08-14:
fourteen gates, thirteen scored, thirteen PASS, `G1.7b` permanently `NOT CHECKED`, and the coverage
clause SATISFIED — every scored gate was made to fall by something in the set.** Output:
`../Step1_docs/outputs_step1/gate_report_step1_spain.txt`.

🔴 **Step 1 is nonetheless NOT done, and now for one reason only: `V1.a` fires on one country of
four.** That is the correct behaviour and it stays until the UK, France and Italy files exist. Nothing
inside the specification is outstanding. **Do not read "Spain's battery is green" as "Step 1 passed".**

### ✅ 2026-08-14, later the same day — the UK and Italian data ARRIVED. France is in the post.

The author delivered three items to `../Datasets/`. The manager inspected all three:

* **UK — complete.** UKDS **SN 8128**, UKTUS 2014-15, tab release, End User Licence. 587,632 lines in
  `uktus15_diary_ep_long.tab` and 11,422 in `uktus15_individual.tab`, both including the header, with
  all six data dictionaries and the NatCen and CTUR technical reports.
* **Italy — complete, and the wave is confirmed.** `Nota_metodologica-2013.pdf` states *"Periodo di
  riferimento: anno 2013-2014"*. 1,077,658 diary lines, 44,867 individual lines, record layouts and
  code lists inside the zip. 🔴 The accompanying `UsoTempo_2023_IT.zip` is the **volunteering module of
  a later wave and contains no diary at all** — excluded, and recorded as excluded.
* **France — NOT data.** The zip holds one PDF, the author's Progedo request receipt, **demande
  n°38663, submitted 2026-08-14, under review.** The requested item is the right one and is better
  than the national file: `[lil-1065] Emploi du temps (version pour Eurostat) - 2009-2010`.

**`V1.a` therefore goes from 1 of 4 to 3 of 4 and keeps firing.** It clears only when France lands.

🔴 **Reading the two new layouts turned up three heterogeneities the specification does not yet
cover.** All three are the manager's to close and none is an employee's to decide:

1. **Spain is the only slot-level file.** Italy and the UK are native episodes with explicit times, so
   Spain's first-of-run reconstruction has no analogue there. Step 9 was specified on 2026-08-14 to
   calibrate on **slots** — for IT and UK those slots must be rebuilt onto a grid, and that
   reconstruction is currently unwritten.
2. **Secondary activity is not one thing.** Spain: one, on the primary's 3-digit list. Italy: one, on a
   **coarser 34-code list** (`catcon`, confirmed a separate classification and not a truncation of
   `catpri` — F-IT-3). UK: **three** (`What_Oth1/2/3`). The record contract carries one `act2_raw`.
   Both employees were told to carry everything and decide nothing, and both did. ✅ **Three of the four
   coverage rates F-ES-6 closes on are now measured:** Spain 80,800 of 430,754 episodes (18.8 %), Italy
   257,998 of 1,077,657 (23.9 %), UK 163,105 / 15,968 / 1,353 of 587,632 (27.75 % / 2.72 % / 0.23 %).
3. **Co-presence sets differ** — Spain 6, Italy 8 (it splits mother from father, where Spain has a
   single `PADRES`), UK 9 including explicit `WithMiss`/`WithNA` missingness fields. `COP` needs a real
   cross-national rule at Step 2, not the Spain-shaped one.

Also: **the UK ships two diary weights**, `dia_wt_a` and `dia_wt_b`. Which one is used is
pre-registration-relevant and is **unmade**.

**Two employees ran in parallel on 2026-08-14 and BOTH RETURNED, 2026-08-15**, against
`4thJ_employee_step1_uk_2026-08-14.md` and `4thJ_employee_step1_italy_2026-08-14.md`: codebook facts →
reader → full fourteen-gate battery, per country. Because they ran concurrently, **neither wrote to
`acquisition_manifest.json` or to either Step 1 progress log** — each emitted a fragment
(`acquisition_manifest_<country>.json`, `proglog_entries_<country>.md`) and **the manager merges them.
Those two merges are still OUTSTANDING.** Results below.

🔴 **Each employee had to establish `G1.7b`'s fate from its OWN country's weighting methodology.**
Circularity is a property of the source and does not transfer from Spain. The same applied to whether
`G1.8` narrows. **Both did so, with their own page citations** — ISTAT `Nota_metodologica-2013.pdf`
p. 12 for Italy, NatCen p. 31 §7.4 for the UK. Neither inherited Spain's verdict.

### ✅ 2026-08-15 — THE UK AND ITALIAN BATTERIES ARE IN. Neither is clean, and that is the point.

Artefacts: `../Step1_docs/outputs_step1/gate_report_step1_uk.txt` and `..._italy.txt`. **Fourteen gates
each, eleven scored each.**

| | Italy | UK |
|---|---|---|
| PASS | 10 | 9 |
| FAIL on real, unperturbed data | 1 — `G1.6` | 2 — `G1.4`, `G1.7a` |
| `NOT CHECKED` | `G1.7b`, `G1.7c`, `G1.8` | `G1.7b`, `G1.7d`, `G1.8` |
| Coverage clause | SATISFIED | SATISFIED for the 9 that PASS |
| Episodes | 1,077,657 (41,229 diaries, 1/respondent) | 587,632 (16,533 person-days, 8,274 people, 2/respondent) |

**The `NOT CHECKED` sets differ by country and each difference is a real property of the delivery, not
a copied verdict:** Italy's `G1.7c` cannot run because `coefin`/`coefi2` exist in exactly one file, so
there is no cross-file restatement to compare; the UK's `G1.7c` **PASSES** because its weights are
restated in three files and were compared bit-identically, 0 mismatches of 16,533. The UK's `G1.7d`
cannot run because the delivery is tab-delimited with free-text decimals and ships no fixed-width
layout to check magnitudes against.

🔴 **What the manager verified personally against the raw files, rather than trusting the reports:**

* **Italy `G1.1`'s reference is genuinely external.** ISTAT's `!Leggimi.html` states `1077657` and
  `44866`; both match the parsed counts exactly. This is the one Italian gate whose reference does not
  come from the file it audits.
* **UK `4276` is real** — that activity code occurs **exactly once in 587,632 rows** and is labelled
  nowhere in the delivered dictionary. A genuine data defect.
* **UK `-9` in `WhereWhen` occurs 7,117 times, 1.211 %** — and `-9` in `What_Oth1` occurs **424,527**
  times, which is precisely the "recorded and blank" figure the reader reports. 🔴 **So the reader maps
  `-9` to blank for the three secondary-activity columns and leaves it raw in `loc_raw`. Half of the
  UK's `G1.4` failure is our own reader treating one sentinel two ways, not bad data.** See open item
  M-1 below.
* The gate runner prints "51 columns" for a 50-column file: `read_raw_tab` appends its own `_key`
  column before the count. Cosmetic, not a defect. Column resolution is by name throughout.

**Not verified independently, and recorded as such:** the perturbation batteries themselves, Italy's
`G1.2`/`G1.11` arithmetic, and every codebook citation beyond the two above. They are read from the
artefacts, which is the standard, but they were not re-derived.

### ✅ 2026-08-15 — THE FIVE MANAGER ITEMS ARE DECIDED. M-1 to M-5. **Step 1 is now SIXTEEN gates.**

Written into `../Step1_docs/4thJ_01_corpusAcquisition.md` (new section "CONTRACT CHANGES M-1 to M-5")
and its validation document (gate table, perturbation table, progress log). 🔴 **Do not reopen them
and do not re-derive them.**

🔴 **The reason none could be left standing as a red FAIL, and it is the load-bearing sentence of the
whole round:** a gate that FAILs at baseline **cannot be seen falling**, so every perturbation aimed at
it reads `DID NOT FIRE`. The three baseline FAILs had silenced **five arms** — Italy's md5 arm
entirely, three of the UK's code-list arms, and the UK's **entire weight arm**. 🔴 **That is also the
most seductive argument in the file, because "clearing the FAIL restores detection power" is what
gate-shopping sounds like from the inside.** Each decision was taken on whether the *threshold was
wrong*; the restored arm is recorded as a consequence, never as the reason. **Where the threshold was
right it did not move: `G1.6b` still FAILs on Italy.**

* **M-1, the `-9` sentinel — contract fixed, gate not.** `loc_raw` gains `act2_raw`'s three states.
  `G1.4` accepts a value as not-a-code **only if the delivery's own value label declares it a
  missingness sentinel**, cited in `codebook_facts`. No rule that negative values are sentinels.
  **`4276` (F-UK-9) still FAILs, which is the test of whether the amendment disarmed anything.** New
  gate **`G1.12`** is the compensating recount, built exactly like `G1.11`.
* **M-2, `G1.6` splits.** **`G1.6a` integrity** (md5, scored everywhere, no URL needed) + **`G1.6b`
  provenance** (URL + date, **threshold unchanged, Italy still FAILs**). The FAIL is a defect in our
  own custody record, not in the file — it clears when the author supplies the URL and date the
  Italian archive came from. Manifest gains `hashed_at` and `provenance_source`. 🔴 **An attested URL
  is as good as ours; an attested hash is not.** France: record URL, date and md5 in the browser.
* **M-3, `G1.7a` re-scoped**, not widened. Positive/finite/non-constant **on rows the delivery
  weighted**, **plus** a new clause: a missing weight on a row the delivery calls **productive** is a
  FAIL. 🔴 **Spain's `G1.7d` population precedent does NOT transfer** — Spain excluded rows carrying no
  diary; the 2 UK person-days carry one that sums to 1,440. **Step 1's population is every diary the
  survey collected; nothing is dropped for lacking a weight.** Weights become nullable.
* **M-4, `G1.7d` conditioned on the declared weighting convention.** *expansion* → `[1.0, 10^width)`;
  *normalised* → `> 0` and **mean within ±1 % of 1.0**; *not declared* → `NOT CHECKED`. Not a
  loosening — `>= 1.0` is true only of an expansion weight and **false** of a normalised one. 🔴 The
  upper-bound half still needs a layout width, so it **stays `NOT CHECKED` for the UK**.
* **M-5, `weight_dia` = `dia_wt_a`.** Our unit is the person-day, which is exactly what NatCen
  documents `dia_wt_a` for and the grain CTUR's own worked example uses it at; and it is the only one
  of the two that balances **day of week**, which is load-bearing for an occupancy paper. `dia_wt_b`
  carried as `weight_dia_b`. **Freezes into `prereg.md`.** One named reopen trigger: if the unit of
  analysis ever moves from the person-day to the person, `dia_wt_b` becomes correct and the choice is
  re-taken in writing **before** anything is trained.

**Six perturbations added, and two of them audit the decisions themselves:** `loc_undeclared_sentinel`
must fell `G1.4` or M-1 disarmed the membership test; `weight_blank_on_productive_row` must fell
`G1.7a` or M-3 removed power instead of redirecting it. 🔴 **If either does not fire, the decision it
audits is reversed — not the perturbation adjusted.**

🔴 **Nothing has been re-run.** All three countries were scored against fourteen gates. **All three
batteries must be re-run against sixteen**, and no country's report may be quoted against the current
validation document until then.

**Two more UK facts that bear on Step 2, both measured:** the diary origin hour is **04:00, not
Spain's 06:00** (F-UK-5), which is live input to the still-withdrawn D-S2-1; and `diary_day` must be
the **1st/2nd-day ordinal, not the day of week** — 3 respondents share a weekday across both their
days (F-UK-6). Minimum age is **8** in the UK and **3** in Italy, against Spain's 10.

Everything else in this folder tree is still a specification, and every threshold in it is
**pre-registered rather than measured**. Also measured: the tokenizer comparison and the licence
sweep, run on Speed on 2026-08-14 (jobs 1234211, 1234216, 1234219, `../tools/`).

Artefacts: `../Step1_docs/outputs_step1/`. Raw archives are on the **local workstation**, not yet on
`/speed-scratch`; the `scp` is outstanding and the manifest records that rather than implying it was
done.

---

## DECISIONS THAT ARE CLOSED — DO NOT REOPEN THEM

| # | Decision | Where |
|---|---|---|
| — | **The trained model will never be released.** Weights and adapters both. The releasable artefact is the synthetic diary corpus (CC BY 4.0) plus code (Apache 2.0) | `RL10` |
| — | **No forecast, no temporal claim, anywhere** | Author |
| 5 | **HETUS only. No Canada, no United States** | Author, 2026-08-14 |
| 6 | ~~Four countries~~ 🔴 **AMENDED by decision 16: THREE countries, one wave each — Italy 2013-14, Spain 2009-10, UK 2014-15. France excluded** | Author, 2026-08-14; amended by the author 2026-08-15 |
| 16 | 🔴 **France is excluded. The corpus is three countries and the rotation is three-fold.** Re-admittable only before the first fold is **scored** | Author, 2026-08-15 |
| 3 | **Backbone: OLMo 3 7B.** Leg-4 is the 1B pilot (correctness only), Leg-5 is the reported model | Our own tokenizer measurement, which overruled `RL18` |
| — | **`ACT` keeps 3 digits.** All four waves share one coding generation, so nothing forces 2-digit pooling | 1A-bis |
| 11 | **No country is held out. All are, in turn** — 🔴 **THREE-fold rotation after decision 16**. All three folds reported including the worst; **design frozen once any fold is evaluated**. Pre-named fold **unchanged: held-out Spain** | Author, 2026-08-14; length amended 2026-08-15 |
| 13 | **Two reproduction tiers:** Spain alone with no credentials, and Spain + UK with two free registrations for the transfer machinery | Author, 2026-08-14 |
| 15 | **Norway is rejected.** No ACL variable and no official recode in the Sikt delivery, only SSB's 167-code national list | `RL20`, vetted V12 |

🔴 **Decision 6 is a decision about newer waves as much as older ones.** UK 2020-21, Italy 2022-23,
Spain 2024-25 and France 2024-25 are all out, and **Eurostat will not release the HETUS 2020 round
before 2027**. There is no newer obtainable corpus. See 1B-bis.

---

## NEXT ACTIONS, IN ORDER

**1. File the Eurostat entity-recognition enquiry with Concordia's Office of Research.**
🔴 **AUTHOR-ONLY, and as of 2026-08-15 it is the ONE item in Step 1's definition of done that nobody
here can execute.** It goes to the Office of Research in the author's own name. Everything else in
Step 1 is either done or is the sixteen-gate re-run. **Step 1 cannot be signed off until this is sent
and the date recorded** — and after decision 16 it matters more, not less: with three countries
instead of four, Track A is the only route that widens the corpus, and it now widens it 3 → 17.
It was second on the list until `RL19` came back. It is now **first**, because `RL19` established that
national routes cannot widen the corpus: of 14 candidate countries, none is Tier 0 or 1, two need the
same institutional accreditation Eurostat does, and two are secure-enclave only. **Track A is not the
slow path to more countries; it is the only one.** With four countries, leave-one-country-out trains on
three, which is limitation C4. Send the enquiry, record the date. *"A report says Concordia is not
recognised"* is already known and is not the same as having asked.

**2. ✅ ACQUISITION IS COMPLETE. Spain, the UK and Italy are done and France is out (decision 16).**
🔴 **There is no acquisition left. Do not chase Progedo and do not open a new source.** The paragraph
below is kept for its findings about the Italian delivery, which still bear on Step 5's release
decision. *(Superseded opening: "France is the only acquisition left.")* UKDS SN 8128 arrived
2026-08-14 and is built. Italy came as ISTAT's own **mIcro.STAT public-use file** — 🔴 **not** the paper-1
copy and **not** the mFR research file (F-IT-1); it carries statistical disclosure control including
**deliberately injected missingness**, and ISTAT itself warns tabulations may differ from published
figures (F-IT-2). That bears on Step 5's release decision and is not a defect to fix. France
(Progedo/ADISP, demande 38663) **needs the author in person** and is the critical path. Work item 1.1 in
`../Step1_docs/4thJ_01_corpusAcquisition.md`. **Record each md5 at download time, not later.**

The Spain round ran from `4thJ_employee_step1_spain_2026-08-14.md` in this folder; the same prompt is
the template for each remaining country. 🔴 **Each reader is written against its own codebook, after
that codebook is in hand.** The Spanish reader (`../tools/4thJ_read_spain.py`) fixes the
intermediate-record contract the other three must meet, and Spain already broke that contract once —
see next action 4.

**3. ✅ DONE, 2026-08-14. G1.7 was redesigned, the runner was rewritten, and the whole battery re-ran
clean.** Employee round from `4thJ_employee_step1_gates_rerun_2026-08-14.md`. **Fourteen gates,
thirteen scored, thirteen PASS, `G1.7b` `NOT CHECKED`, coverage clause SATISFIED.** Counts held at
19,295 / 2,778,480 / 430,754. Nothing below needs doing again; it is kept because **the reasoning is
the reusable part — the other three countries get the same treatment and the same traps are waiting.**

* **`G1.7b` is retired, not repaired** — permanently `NOT CHECKED`, both numbers still printed so the
  circularity stays visible. INE calibrates to the figure it compared against (METH p. 34, step 3).
  🔴 **Do not delete it and do not resurrect it.** A retired gate that vanishes takes its hole with it.
* **`G1.7a` kept and tightened**: present, finite, strictly positive, **and more than one distinct
  value**. A constant column is the likeliest shape of "read the wrong bytes".
* **`G1.7c` is the actual replacement — cross-file weight identity.** One weight per person, restated
  in `CINDIV`, `DIARIO1`, `DIARIO2`, `MHOGAR`, must be bit-identical in all four. 🔴 **Recomputed by
  the runner from the raw fixed-width files using the layout offsets, never from the reader's
  output** — a check fed by the reader cannot detect a reader that read the wrong column.
* **`G1.7d` — magnitude against the declared layout** (`< 1e6`, `>= 1.0`). Its reference is the LAYOUT
  document, a different artefact from the microdata, which is what `G1.7b` never had.
* **Four perturbations, each isolating one gate.** The one that matters: replace a respondent's
  `FACTORF` with **another respondent's valid `FACTORF`** — positive, in range, correctly formatted,
  invisible to every other gate. `weight × 10` is struck from the table.
* **Honest boundary now written into the doc:** no gate checks that the weights are *right*. It cannot
  be done offline; `G1.7b` only looked as if it did.

✅ **The reader now carries `act2_raw`** in a nullable pandas `string` column, three states separable
through the parquet round-trip (ES: not recorded 0, recorded-and-blank 349,954, recorded-with-value
80,800 of 430,754 episodes), and `cop_padres` is renamed `cop_extra_es_padres` per D-S2-2.

🔴 **What the round found in the SPECIFICATION rather than in the data — read this before writing the
next country's prompt, because all three would have repeated:**

* **The gate count was wrong everywhere: twelve, actually fourteen.** `G1.1`-`G1.6`, `G1.7a`-`G1.7d`,
  `G1.8`-`G1.11`. Written when `G1.11` was added and the `G1.7` split was counted as two parts, not
  four, then copied into four documents. Corrected in the validation doc's live table and status; the
  earlier progress-log entries keep the wrong number because they are append-only.
* **`G1.11`'s threshold was not implementable as written.** It said a count of *slots* must equal a
  count in the *episode* table. Those are different quantities: **11,216 episodes mix a blank and a
  non-blank `ASECU`, and 13,009 carry more than one distinct value.** Corrected to the episode-level
  identity it was always for — the runner rebuilds episodes from the raw file with its own offsets,
  split key and first-of-run rule. 🔴 **Recorded as a basis change, not folded in quietly.**
* 🔴 **`999` is a real INE code** (row 117, *"Otro empleo del tiempo no especificado"*), so the
  pre-registered `act_raw`/`act2_raw` perturbation set a **legal** code and tested nothing. Now `99Z`.
  **Check every country's out-of-list sentinel against that country's own transcribed list.** A
  sentinel that is secretly valid is a perturbation that cannot fire, which is the coverage clause's
  own failure mode hiding one level down.
* **A first-draft `G1.7d` failed the NULL perturbation** — it read `MHOGAR`'s full 25,895 rows,
  including the 6,600 non-respondent members whose `FACTORF` is an all-zero placeholder. Restricted to
  the 19,295 respondents, the population `G1.7c` already used. **Accepted as the right population, not
  a loosened bound**; those rows carry no diary and enter no corpus. 🔴 **The null case catching it is
  the system working.**

**What did not attribute:** five perturbations moved more than their named gate, all row-removal or
row-rewrite collateral through `G1.5`, now also reaching `G1.2` and `G1.11`. Correct checks, poor
attributors, for a structural reason. Recorded in the validation Progress Log, **not tuned away**.

**Still true and still the rule for the next three countries:** counts must not move when a column is
added, the runner **imports nothing from the reader** for `G1.7c`/`G1.7d`/`G1.11` and prints both
offset transcriptions, and 🔴 **if the coverage clause FAILs, that is the deliverable** — inventing a
perturbation to make it green defeats the one thing the clause does.

**4. ✅ The four Spanish findings are decided, 2026-08-14, as D-S2-1 to D-S2-4.** Written into
`../Step2_docs/4thJ_02_harmonisation.md` (new section after the decided-list), its validation doc, and
the parent plan 2A/2B/2C/3B plus the plan progress log. Findings themselves in
`../Step1_docs/outputs_step1/codebook_facts_spain.md`.

* **D-S2-1, day origin: withdrawn, not replaced.** Spain runs 06:00 to 06:00 and no 04:00 day is
  constructible from it. The origin is chosen from **four measured codebooks or not at all** — picking
  06:00 from the one country we have measured is `RL02`'s error in the other direction. **Step 2 work
  item 2.4 is blocked on it.** The Spanish reader keeps its native 06:00 indexing meanwhile.
* **D-S2-2, co-presence: five shared flags plus country extras as named columns.** `PADRES` survives
  as `cop_extra_es_padres` and is never folded into "other household members". `MENOR` maps to the
  shared "with children" flag **with its national definition recorded**, because Spain's test is
  household composition, not parenthood. Extras are not Step 5 conditioning variables and are not
  serialised into `COP` — a symbol only one country can emit leaks country identity into LOCO.
* **D-S2-3, location: no numeric range test anywhere.** `RL02`'s "10-19 / 20-39" is retracted and
  nothing replaces it; membership is code-by-code from the Step 2 crosswalk into at-home / other
  place / private transport / public transport, with public transport a class in its own right.
* **D-S2-4, code `11`: confirmed and widened.** It merges dwelling, garage, garden and plot, **and
  working from home is `11` too.** The indoor rule stands; only the 3-digit `ACT` separates "at home,
  not working" from "working at home", which Step 9 needs.

🔴 **Three of the four overturned a line the plan listed as decided, and all three came from `RL02`
rather than from a file.** Every remaining `RL02` claim about file content is a hypothesis until a
codebook confirms it — and UK, France and Italy are measured from their own codebooks, **not assumed
to match Spain either.**

Also decided 2026-08-14: **G1.7 is redesigned** (next action 3), so the only thing between Step 1 and
done is an employee round on the gate runner.

✅ **The hole D-S2-3 left is closed: `G2.11`, location class coverage**, added on the author's word
2026-08-14. Every target location class must be non-empty for every country, plus a share-based
trigger for the quiet form, guarded by `V2.e` so it cannot pass by having no classes to check. **Its
perturbation is a relabelling, not a deletion** — deleting the episodes would also break G2.4 and
prove nothing about G2.11's own power; remapping Spanish public transport to private transport leaves
ten gates green and drops only G2.11. Step 2 now has **eleven gates and twelve perturbations, none
run**. G2.8 was widened to cover the extra co-presence columns; no threshold was moved.

**Still undecided from the Spanish round: F-ES-6**, secondary activity, non-blank on 12.2 % of slots
with nowhere in the record to put it. It is a Step 3 question, not Step 2, and it is untouched.

**4-bis. ✅ `RL22` and `RL23` are back, vetted, and both are negative. Nothing is acquired.** Record in
the plan, V15 to V18.

* **Italy 2022-23 does not exist as a file.** The diary microdata has never been released and no
  release date is published; what appeared on 10 February 2026 is the voluntary-work module, which
  the documentation says excludes the diaries. **There is nothing to request.** Recheck in 2027 with
  the HETUS 2020 round, not before.
* **UK 2020-21 is obtainable and not worth having.** The accessible file is the CTUR CaDDI online
  instrument: about **36 activity categories** against roughly 250 three-digit codes in UKTUS
  2014-15, and an **individual online panel with no household clustering**, so no whole-dwelling
  co-presence. Free, Tier 2, one hour of work — and the recommendation is **not to download it**,
  because each acquisition adds a licence with destruction and reporting duties for a file that
  supports no test we have.
* ✅ **Decision 6 is now on better evidence.** UK 2020-21 is out because the file is not a HETUS-coded
  household diary, not because of the mode-plus-lockdown confound. That is checkable by a reviewer.
* 🔴 **Both reports invented a fact about our own corpus:** `RL23` says Spain fields a two-day diary.
  **We measured one**, G1.9, and INE says one. **No variable name from either report may enter a
  document or a reader** — `RL22`'s come from behind a registration wall it could not pass, `RL23`'s
  from a paper questionnaire model with no URL.
* **Do not adopt `RL23`'s "108 codes in ACL 2008".** Our Spanish 2008-generation file uses **116**
  (F-ES-5), and the report is restating `RL02` rather than measuring.

**5. ✅ STEP 2 IS UNBLOCKED, 2026-08-15.** Harmonisation consumes **every** country's
`episodes_<country>.parquet` and after decision 16 that is three, all built. ✅ **D-S2-1 is also closed
— the day origin is decided as D-S2-5: 04:00, reached by treating each diary as a cyclic day**, which
splices only Spain and splices it inside the sleep block. The age floor moves 11 → **10**, because 11
was France's minimum and the rule is *the highest of the participating minima*.

🔴 **One precondition remains and it is ours: the sixteen-gate Step 1 re-run.** M-1..M-5 changed the
record contract, so Step 2 must consume parquets written to the current contract, not the previous one.
**Step 2 does not start on stale parquets.**

*(Superseded text follows.)* ~~**5. Step 2 still cannot start.** Harmonisation consumes all four `episodes_<country>.parquet`.~~ A
four-column crosswalk built from one country and extended by assumption is precisely the defect Step 2
exists to prevent. Step 0 is closed and is a record, not a work plan. **D-S2-1 to D-S2-4 changed what
Step 2 will do; they did not unblock it.**

**6. Decisions 11, 13 and 15 are closed — do not reopen them and do not re-derive them.** Two were
author calls and one was a report, which is exactly the mix a later session is most tempted to redo.

* **11, the held-out country: four-fold rotation.** Every country is held out in turn. All four folds
  are reported **including the worst**, and **the design freezes once any fold has been evaluated.**
  A random household hold-out inside the training countries is retained as an ordinary test set and
  **is never reported as transfer.**
* **13, the reproduction path: two tiers.** Spain alone with no credentials, and Spain + UK with two
  free registrations for the transfer machinery. The UK half is the manager's implementation, not the
  author's selection, and is the part to correct if it is wrong.
* **15, Norway: NO.** `RL20` found the Sikt delivery carries only SSB's **167-category national list**,
  no ACL variable at any depth, and **no official recode table anywhere** in SSB publications, the SSB
  `Klass` database or the Sikt metadata. `RL19`'s recode claim is retracted. **Rejected on the same
  screen as UK 2000-01. The four-country corpus stands and limitation C4 stands with it.**

**7. 🔴 Decision 14 is the only decision still open, and `RL21` proved it cannot be closed by reading.**
No published study has ever compared two or more day-to-year chaining rules on the same building with
the daily generator held fixed. No standard defines a protocol. IEA EBC Annex 66 and 79 are silent. **No
citable threshold exists**, so the 25 % figure is permanently project-chosen.

**It closes by our own experiment, in work item 7.6, or it does not close.** Three things were written
into that item and they are the reason the experiment is not what `RL17` proposed:

* **Rule 3 is swept, not fitted.** A two-day survey of 1 weekday + 1 weekend **cannot identify
  consecutive-day transitions**, so its persistence parameter cannot come from our corpus. Fitting it
  ourselves and comparing it against two rules we did not fit compares our bookkeeping against itself.
* **Record annual energy alongside peak.** `RL21` *infers* annual energy is insensitive. Measuring both
  costs nothing and converts an inference into our own number, which is what settled decision 3.
* **Compute the realistic activity-vocabulary value on held ISTAT data**, not from the report.

🔴 **No number from `RL21` may enter any document.** Its headline 15-35 % peak divergence is labelled a
measured fact in a report whose own `B1` says nobody has measured it, and it appears elsewhere in the
same report as 15-40 % and as 10-25 %. Full list in the plan document, V13.

**8. Compute the unique-sequence baseline on the held ISTAT data.** Still outstanding from the first
vetting round: `RL08`'s U > 0.98 benchmark was invented, `RL17` A7 returned `NOT FOUND`, and **Gate 6
is not trusted until the empirical value is computed on data we hold.** It shares a data source with
the activity-vocabulary value above, so the two are one job.

**8-bis. ✅ Weight pre-staging is DONE — Speed job `1245620`, 2026-08-14, 3 of 3, 33.34 GiB in eight
minutes.** `../tools/4thJ_stage_weights.sh`, partition `ps`, `sbatch`. Hashes copied into
`../Step4_docs/outputs_step4/staged_weights.json`:

| Repo | Revision |
|---|---|
| `allenai/Olmo-3-1025-7B` | `a81bae42db3975be1671e27b9c9a56da1a9f980f` |
| `allenai/OLMo-2-0425-1B` | `a1847dff35000b4271fa70afc5db10fd29fedbdf` |
| `Qwen/Qwen2.5-7B` | `d149729398750b98c0af14eb82c78cfe92750796` |

🔴 **The hashes are the deliverable, not the files.** `G4.11` fails a run whose manifest names a
checkpoint without one.

* 🔴 **A correction came out of writing it: compute nodes on `ps` DO have outbound network.** The plan's
  4F and the Step 4 document both said they did not, which implied the weights had to come down on the
  login node — an act the top rule forbids. The tokenizer jobs pip-installed and pulled from Hugging
  Face inside `sbatch`; so does 1245620. **Offline is a discipline we impose on training runs, not a
  property of the node.** Both documents are corrected.
* **`/speed-scratch` purges after 90 days**, and training is weeks away behind the UK and France
  acquisitions. **Re-run this job before the first training submission and re-read the hashes** — if a
  repo moved, the hash changes and that is exactly what the file exists to catch.

**9. Before Step 7 is sized: run the vLLM throughput comparison** on Leg-5 checkpoints. OLMo 3 7B has
**no grouped-query attention** — 32 KV heads over 32 layers gives about **512 KB per token** against
Qwen2.5-7B's 56 KB, roughly 9× and about 6× after our token saving. **That figure is arithmetic from
the config, not a benchmark**, and it must not be quoted as one.

---

## HOW THIS PROJECT WORKS — THE RULES THAT ARE NOT NEGOTIABLE

* 🔴 **Speed cluster: `sbatch` only.** Never a blocking `srun`, never bare python on the login node,
  not even a one-liner. Every job requests `-t 7-00:00:00`. Flagged three times; a fourth is account
  suspension.
* 🔴 **Deep research is external.** You never search literature or verify citations as the deliverable.
  You write the prompt file; the author runs it. Prompts and reports live in `../DeepResearchPrompts/`
  as `L<NN>` and `RL<NN>`.
* 🔴 **You never create images.** You write the prompt under
  `../writing/submission/figures/Prompts_Images/`; the author generates the figure.
* 🔴 **You never create anything that was not asked for.** If you think something is needed, ask in one
  sentence first.
* **Replies are short, plain English, one thing at a time**, even when the author writes French.
* **Progress Logs are append-only.** Never delete, reorder or reformat an existing entry.
* Never count lines with PowerShell — use `wc -l`. Verify a backup is non-empty before truncating.

---

## 🔴 HOW TO READ A RETURNED DEEP-RESEARCH REPORT

Five rounds have come back. **Every one contained content that was fabricated exactly where it
claimed to be verified**, and every one was caught by cheap offline checking. Before a single value
enters a document:

1. **Check what it says about our own work first.** It cannot see our results or our cluster. Anything
   it reports about them was quoted from the prompt or invented.
2. **A report that agrees with what you supplied has told you nothing.** `RL19`'s Part B returned the
   HETUS guidelines restated per country as though ten codebooks had been read.
3. **Make it obey an identity it cannot fake.** A DOI resolves or it does not. A licence clause exists
   or it does not. `RL19`'s Netherlands entry died the moment the DANS record was opened: restricted,
   unrequestable, superseded — against a claim of "opened in full, guess count 0".
4. **Read the negative controls as evidence, not as reassurance.** `RL19` defined "convenient" as all
   seven properties at once, so nothing could score, then reported zero. **A control that cannot fire
   is not a control** — the same vacuity we screen our own gates for.
5. **Every recommendation in the rescuing direction is a signal.** If a report concludes the data is
   obtainable, the licence permissive, the method right and the compute sufficient, treat the round as
   failed and re-run it.
6. **Salvage the route, not the table.** `RL19`'s value was a negative result plus the observation that
   no national archive ships the Eurostat-harmonised file — neither of which was its recommendation.
7. 🔴 **Check the report against itself before checking it against the world.** It is the cheapest test
   there is and it caught the worst defect in the fourth round: `RL21` reports **zero** studies
   measuring the difference between chaining rules, and then gives that difference as **15 to 35 %**,
   labelled a measured fact with high confidence. **A quantity that appears three times with three
   values, or a number that contradicts the report's own negative result, was never measured.**
8. **A report that returns the answer your prompt said it expected has told you less than it looks.**
   `L20` said a short negative was expected and `RL20` returned a short negative. That verdict is
   accepted **on its checkable details** — 167 categories, `akt1` to `akt144`, Notater 2012/03 — not on
   the report's own confidence. Write prompts that expect an answer, then believe the details rather
   than the conclusion.

The full record is V1 to V14 in the plan document. **Read V6, V11 and V13 before commissioning another
round**; they are what a failed round looks like from the inside, and V13 is what a *useful* round
looks like when its headline number is still unusable.

---

## GATE DESIGN, IF YOU TOUCH ANY VALIDATION DOCUMENT

Read `feedback_gates_must_be_seen_failing.md` in memory first — 46 failure classes, all from real 3J
work. The three that cost the most:

* **Every gate must be seen failing.** A perturbation table where each perturbation breaks exactly one
  gate, plus a **coverage clause** that fails the probe if a passing gate was never made to fall.
* **A gate whose reference derives from the source it audits cannot fail.** At least one check per step
  must arrive through a path the defect cannot reach.
* **A check that cannot distinguish "found nothing" from "could not run" is not a check.** Print
  `NOT CHECKED`, never a pass.

Step 7's G7.1 to G7.4 are labelled **enforcement confirmations**, not gates: they cannot fall while the
grammar mask is on, and counting them in a seen-failing tally would inflate it.

---

## WHERE THINGS ARE

| Path | What |
|---|---|
| `../4thJ_00_HETUS_LLM_Pipeline.md` | The authority. Decisions, vetting record V1-V14, all ten steps, limitations, progress log |
| `../4thJ_00_HETUS_LLM_Pipeline_Overview.md` | One-screen map, ASCII step boxes, open-decision count |
| `../Step0_docs/` … `../Step9_docs/` | Per-step implementation + validation specifications, and `outputs_stepN/` |
| `../DeepResearchPrompts/` | `L01`-`L21` prompts, `RL01`-`RL21` reports, master brief, README with the vetting checklist |
| `../tools/` | The three Speed scripts that produced our own measurements |
| `../writing/submission/figures/` | The graphical abstract PNG and its prompt |

🔴 **The master brief in `DeepResearchPrompts/` is stale** — it still says five countries, multi-wave
and Canada. `L19` carries a corrections block at the top that overrides it. **Any new prompt needs the
same block** until the brief is reissued.

---

## OPEN DECISIONS

**12 of 15 fully closed.** Only **14**, the day-to-year chaining rule, is genuinely open, and it now
closes by our own experiment rather than by any further reading. See next action 7.

Separately from the fifteen: the **four Spanish findings are now decided** as D-S2-1 to D-S2-4 (next
action 4, 2026-08-14), except that **D-S2-1 has no value yet** — it closes when all four codebooks are
in hand. ✅ **The G1.7 redesign is done, implemented and re-run** (next action 3).

✅ **F-ES-6 is decided, 2026-08-14: `act2_raw` is carried, not serialised.** It is in the Step 1 record
contract and in `harmonised.parquet`, with three states kept distinct — not recorded, recorded and
blank, recorded with a value. It is **not** in the `DUR,ACT,LOC,COP` tuple, because a field only Spain
is known to record would leak country identity into leave-one-country-out. **It closes on four
measured coverage rates** in `outputs_step3/act2_coverage.md`, not on a preference. Step 3, 3.2-bis.
New gate **`G1.11`** guards it: a reader that collapses "blank" into "not recorded" moves no row and
emits no illegal code, so nothing else in the battery can see it. **Step 1 has fourteen gates**
(`G1.1`-`G1.6`, `G1.7a`-`G1.7d`, `G1.8`-`G1.11`), thirteen scored and `G1.7b` permanently
`NOT CHECKED`. ✅ **`G1.11` has now run and passed on Spain: 80,800 non-blank episodes by both the
reader and the runner's independent rebuild** — but see next action 3 for the two things it exposed,
including that its own threshold was written slot-level and had to be corrected to episode-level.

🔴 **The specification is now complete and mutually consistent all the way to the first Speed training
job**, not only to Step 3 (audit of 2026-08-14, plan progress log, twelfth entry). Steps 4 to 9 were
read **against the closed decisions and against each other** rather than against themselves, which is
how all three defects were found — each lived between two documents that were correct alone.

* ✅ **Step 4 is four folds, not one run.** It was written for a single Leg-5 run while decision 11 had
  already made it four, and **Step 6 asserted Step 4's output contract said "one adapter per fold" when
  it did not.** Author decision 2026-08-14: **the ceiling run and the Qwen comparison arm are
  single-fold.** Six Leg-5 jobs, four Leg-4 jobs. Section 4D-bis in the plan, and the whole of
  `../Step4_docs/`.
* ✅ **The pre-named fold is held-out SPAIN — confirmed by the author 2026-08-14**, by a rule fixed in
  advance (alphabetical ISO code) and taken while nothing had been trained. It freezes into `prereg.md`
  before the first Leg-5 submission and **does not move after that**. 🔴 Naming it late would point the
  full fine-tune at whichever fold the primary run did worst on, which is selecting on the outcome.
* **New deadline:** `prereg.md` freezes before the first *training* submission, not before Step 6
  scores. Gates **`G4.13`** (fold isolation, counted from the shard the trainer loaded) and **`G4.14`**
  (pre-registration md5, recomputed from disk) plus `V4.f` to `V4.h`. **Step 4 has fourteen gates.**
* ✅ **Step 9's half of F-ES-6 was missing.** Step 3 keeps `act2_raw` and names Step 9 as the reason;
  Step 9 reads *generated* diaries, which carry none. Resolved: the trigger fires from the primary
  code, `act2` calibrates `P(appliance | activity)` on the real corpus, **`G9.14`** asserts it is never
  a runtime column. 🔴 **A trigger reading an absent column does not raise — it silently never fires.**
  If `act2` is ever serialised, it must be **before `corpus.jsonl` is emitted**.
* ✅ **Step 8's campaign is bound to the folds:** four populations, not sixteen, each country simulated
  under the adapter that held it out. **`G8.16`** + `V8.g`.

**What is deliberately NOT written: `prereg.md`.** Its second hold-out's stratification depends on a
corpus that does not exist. Drafting it now and editing it later is the exact defect `G4.14` catches.

🔴 **What is still needed to reach training, REWRITTEN 2026-08-15 after decision 16 — and every item
on it is ours:**

1. **The sixteen-gate Step 1 re-run on the three countries** (prompt written, runs on Speed).
2. The two manager merges, and the Eurostat enquiry sent with a date.
3. **Step 2** — crosswalks, the 04:00 cyclic rotation (D-S2-5), the age-10 filter, eleven gates.
4. **Step 3** — serialisation to `corpus.jsonl`.
5. **`prereg.md` frozen**, then the first Leg-5 submission.

✅ **Step 1's machinery is finished and has been through all three countries.** *(Superseded: "the
France acquisition, then Step 1 on France, then Step 2, then Step 3.")*

🔴 **Updated 2026-08-15: the five manager decisions M-1 to M-5 are TAKEN**, so the specification is
ready for France before France arrives — which was the point of settling them first, since France comes
by the same hand-delivered route that made Italy's `G1.6` fail and will land in the same hole. **M-2
is what France needs**: URL, date and md5 recorded in the browser at download time, `hashed_at` and
`provenance_source` filled in. What remains outstanding is **execution, not decision** — the
sixteen-gate re-run on three countries, then France, then Step 2.

**12** (household-joint generation) remains deferred as scope rather than open as a question: it is
known to be feasible, about 7,000 tokens for a four-person household week. `RL21` gave it a second
reason to exist — household role coherence across consecutive days is a household-level property that
per-person generation cannot enforce.

---

## FIRST THING TO SAY IN THE NEXT SESSION

Say in one sentence that **France is excluded (decision 16), the corpus is Spain + UK + Italy and all
three are built, and the sixteen-gate Step 1 re-run is the only thing between here and Step 2**, then
ask the author what they want next. **Do not begin acquisition, do not chase France, do not start a
training job, and do not commission another research round without being asked.**

### ✅ Both employees finished, 2026-08-15. All deliverables exist and were checked on disk:

| Country | Delivered |
|---|---|
| UK | `codebook_facts_uk.md`, `episodes_uk.parquet`, `parse_report_uk.txt`, `gate_report_step1_uk.txt`, `acquisition_manifest_uk.json`, `proglog_entries_uk.md`, `crosswalk_source_uk_{activity,location}.csv`, `../tools/4thJ_read_uk.py`, `4thJ_gates_step1_uk.py` |
| Italy | the same set, Italy-named, plus the third crosswalk `crosswalk_source_italy_activity2.csv` |

Raw archives unpacked to `_local_runs/4J/raw/{uk,italy}/` — note that tree is under **`GSSCanada\`**,
the parent of `GSSCanada-main\`.

**Merge 3 of 3 is DONE — the reports were verified against the artefacts**, see the STATE block for
exactly what was re-derived and what was not. **Merges 1 and 2 are still owed and neither is optional:**

1. ✅ **MERGE 1 IS DONE, 2026-08-15.** Both `proglog_entries_<country>.md` appended verbatim into
   `4thJ_01_corpusAcquisition.md` and `4thJ_01_corpusAcquisition_val.md`, each under a manager's note
   recording that (a) they appear **after** the M-1..M-5 and decision-16 entries although they describe
   earlier work — the log is append-only and was not reordered — and (b) which of their statements are
   already superseded. 🔴 **The note also records what was NOT independently verified:** the
   perturbation batteries, Italy's `G1.2`/`G1.11` arithmetic, and every codebook citation except the
   two the manager opened personally.
2. 🔴 **MERGE 2 IS DEFERRED ON PURPOSE, not forgotten.** The sixteen-gate employee round is **editing
   the two manifest fragments right now** — M-2 adds `hashed_at` and `provenance_source` to every
   archive entry. Merging them into `acquisition_manifest.json` before that round returns would
   produce a merged file that is stale the moment it is written. **Do merge 2 after the round reports,
   from the updated fragments.**

### ✅ M-1 to M-5 are DONE, 2026-08-15. The employee round is written and ready to run on Speed.

**Prompt: `4thJ_employee_step1_gates16_rerun_2026-08-15.md`, in this folder.** Scope: `4thJ_read_uk.py`
(M-1 only), all three `4thJ_gates_step1_<country>.py`, and one full sixteen-gate re-run on Spain, the
UK and Italy. Hand it to a **fresh** employee session.

🔴 **This round is also what closes the outstanding half of work item 1.1**: TASK 0 `scp`s the three
raw trees (145 + 320 + 145 MB) from `_local_runs/4J/raw/` to `/speed-scratch/o_iseri/4J/raw/`,
**re-verifies every md5 after the transfer**, and runs **one `sbatch -p ps -t 7-00:00:00` job per
country** — three jobs, never chained, so a country that crashes does not take the other two with it.

**This is the only Speed work available today**, and it is not a training job. See the "what is safe on
three countries" block at the top of this file before anyone reaches for the allocation.

🟡 **STATUS 2026-08-16, 00:30 — the round is RUNNING on Speed. Do not resubmit it.** The employee did
TASK 0 (three raw trees copied to `/speed-scratch/o_iseri/4J/raw/`, md5s re-verified after transfer)
and submitted **three jobs, one per country, unchained**: **`1251980` = `4J_g16_es`, `1251981` =
`4J_g16_it`, `1251982` = `4J_g16_uk`**. All three were `RUNNING` at 00:01:08 elapsed. Check them with
one `sacct -j 1251980,1251981,1251982 --format=JobID,JobName,State,ExitCode,Elapsed` — **one call, not
a loop.** The first poller was killed by exactly that mistake: a bash `while ... done` loop was sent to
the login shell, which is **tcsh**, and it died on "Illegal variable name" / "done: Command not found".
The jobs were never affected. 🔴 **Read the results in this order when they land:** the two audit
perturbations (`loc_undeclared_sentinel`, `weight_blank_on_productive_row`) first, then `V1.a`, then the
sixteen gates. **If either audit perturbation reports `DID NOT FIRE`, the decision it audits is
REVERSED — M-4 or M-3 respectively — and the perturbation is not touched.**

🔴 **STATUS 2026-08-16, 02:00 — that round COMPLETED (`0:0`; ES 18m32s, IT 1m39s, UK 2m24s) and its
`G1.6a` result is VOID. A second round is being prepared. Do not quote any `G1.6a` number from the
first one.** `G1.6a` FAILed on all three countries for a runner defect, not a data defect: the gate
trusted the manifest's `local_path` literally, and those are Windows workstation paths
(`C:/Users/o_iseri/...`) that do not exist on the cluster, so every file — PDFs and a `.doc` included —
reported "missing on disk". The archives are intact: TASK 0's own `md5sum` on the cluster matched all
13 files against the manifests before any job ran. **Manager verified all of this directly from
`Step1_docs/outputs_step1/gate_report_step1_*.txt`, not from the employee's summary.** Because `G1.6a`
FAILed at baseline it could not be seen falling, so `corrupt_archive_byte` reported `newly-failed []`
and Spain's `null` perturbation printed `🔴 NULL PERTURBATION MOVED A GATE` — the exact masking M-2
exists to prevent, reintroduced by a deployment bug.

Three decisions issued to the employee for the second round:
**M-6 — `G1.6a` resolves under `--raw` at invocation time**, keeping the manifest's relative sub-path,
and `local_path` stays in the manifest untouched as provenance. Two distinct problem strings, `md5
mismatch` vs `recorded location not resolvable under --raw`, so the two can never be confused again.
🔴 **Acceptance test, not optional: `corrupt_archive_byte` must be seen NEWLY failing `G1.6a` on all
three, and the `null` perturbation must move nothing on Spain. Otherwise the fix is rejected.**
**M-7 — sub-clause attribution when a gate FAILs at baseline for a pre-registered unrelated reason.**
UK's `G1.4` FAILs solely on `act2_raw` code `4276` (F-UK-9, deliberately preserved), which masks FOUR
UK perturbations including the `loc_undeclared_sentinel` audit. Compare the gate's own computed detail
per field instead of its verdict: `loc_raw` moving from `codes_outside_list=[]` to `['-8']` is FIRED at
sub-clause level. Additive only — it may never turn a FAIL into a PASS. **This is why M-1 was NOT
reversed despite `DID NOT FIRE` on the UK: the audit fired on ES and IT, and the UK case is masked by a
pre-existing deliberate FAIL, not refuted.**
**V1.a fired on IT and UK (2 of 3), clear on ES — a race, not a threshold regression.** The three jobs
are unchained and Spain takes 18 minutes, so IT and UK checked for the sibling parquet files before
Spain had written its own. 🔴 **Do NOT let a re-run "fix" this by finding the first round's leftover
parquet files on the cluster — a guard satisfied by stale files is not a guard.** Each round writes to
a run-stamped output subdirectory, and the vacuity guards run ONCE per round in a fourth job submitted
with `--dependency=afterok:<es>:<it>:<uk>`.

Untouched and staying that way: Italy's `G1.6b` FAIL (by design), UK's `G1.4` `4276` FAIL (by design),
the `local_path` fields, and merge 2 (still deferred until the fragments are final). Every `NOT CHECKED`
in the gate table — `G1.7b` on all three, `G1.7c` and `G1.8` on Italy, `G1.8` on the UK — must carry a
one-line reason from the spec before the table is accepted. `NOT CHECKED` is never a pass.

### Still the manager's, still open: the three heterogeneities

Slot-vs-episode basis, secondary-activity arity and granularity, and the co-presence sets. **All three
are Step 2/3 specification decisions.** Both employees were instructed to carry every recorded field
and decide none of it, so the material is in `codebook_facts_uk.md` and `codebook_facts_italy.md`.
🔴 **They are Step 2 questions — and after decision 16, Step 2 DOES start on three countries**, because
three is the corpus. Decide them on paper first; they are inputs to Step 2's crosswalk, not
afterthoughts to it. *(Superseded: "Step 2 does not start on three countries.")*

🔴 **Before touching any gate again, read `feedback_read_the_gates_own_doc.md`: additive fixes only,
and a basis change is written down as a basis change.** M-2, M-3 and M-4 were each recorded as basis
changes on 2026-08-15 rather than folded in quietly; do the same for whatever comes next.

🔴 **Step 1 is still not done — but the reason has changed, and this is the last paragraph that used to
say otherwise.** `V1.a` no longer fires: three of three, after decision 16. What is outstanding is the
**sixteen-gate re-run**, the two merges and the Eurostat enquiry. **Nothing external blocks it.**

🔴 **The crosswalk warning still stands and is not repealed by decision 16.** *"A crosswalk built from
some countries and extended by assumption is precisely the defect Step 2 exists to prevent"* — that
means all **three** must be transcribed from their own codebooks, which they are. It never meant "four
or nothing".

🔴 **Do not re-derive a closed decision because the list looks short**, and **do not chase France.** It
is excluded. If it turns up unasked, read the re-admission window in the decision-16 block before doing
anything with it — before the first fold is **scored**, it can come back; after, it can only ever be an
extra held-out test.

---

🔴 **HAND-OFF, 2026-08-16 21:30 — READ THIS FIRST. The second Step 1 round was NEVER SUBMITTED.**
The employee agent fixing the runners was **stopped mid-work** (it had burned 527k tokens re-reading
files). Nothing is running on Speed. No new job IDs exist. Every `G1.6a` number in this file is still
from the VOID first round.

**Exact state of the three gate runners in `4J_docs_occ/tools/`:**
* `4thJ_gates_step1_uk.py` — **M-6 and M-7 APPLIED** (edited 2026-08-16 21:19). It carries
  `resolve_archive()` resolving each archive under `--raw` while leaving `local_path` in the manifest as
  provenance, the two distinct problem strings, and a `subclauses` dict on `GateResult.add()` giving
  per-field sub-clause attribution for `G1.4`. **Local dry run was never completed — it is UNTESTED.**
* `4thJ_gates_step1_spain.py` — **UNTOUCHED.** No M-6, no M-7.
* `4thJ_gates_step1_italy.py` — **UNTOUCHED.** No M-6, no M-7.

**What the next session must do, in this order:**
1. Read the UK file as the reference implementation, then port M-6 and M-7 to Spain and Italy. Same two
   problem strings, same sub-clause dict. Do not invent a third wording.
2. Add the run-stamped output subdirectory, so each round writes somewhere new and **no leftover parquet
   from the first round can satisfy a vacuity guard.**
3. Move the vacuity guards `V1.a`–`V2.e` out of the per-country jobs into a **fourth job** submitted with
   `--dependency=afterok:<es>:<it>:<uk>`, run once per round. The first round's `V1.a` fired on IT and UK
   purely because the three jobs are unchained and Spain takes 18 minutes.
4. Dry-run all three locally on the Windows box before submitting. The first round's whole defect
   survived because the dry runs ran where the Windows `local_path` values happen to exist.
5. `sbatch` only, `-t 7-00:00:00` on all four jobs, one `sacct` per check and **never a loop** — the
   login shell is tcsh.

🔴 **Acceptance tests that decide whether the round is accepted at all** — these are not optional and a
green gate table without them means nothing:
* `corrupt_archive_byte` must be seen **newly failing** `G1.6a` on all three countries.
* The `null` perturbation must move **nothing** on Spain.
* M-7 must recover the four UK arms masked by the deliberate `G1.4` `4276` FAIL, including the
  `loc_undeclared_sentinel` audit of M-1.
* Every `NOT CHECKED` in the table — `G1.7b` all three, `G1.7c` and `G1.8` Italy, `G1.8` UK — carries a
  one-line reason from the spec. **`NOT CHECKED` is never a pass.**

Untouched by design and to stay that way: Italy's `G1.6b` FAIL, the UK's `G1.4` `4276` FAIL, the
`local_path` fields, and **merge 2 of 2** (`acquisition_manifest_uk.json` + `..._italy.json` →
`acquisition_manifest.json`), still deferred until the fragments are final.

**Cost note from the author, 2026-08-16:** a single employee agent spent ~517k tokens on this fix. Brief
the next one narrowly — point it at the UK file and this block, not at the whole document tree.

---

## 🔴 THE PATH FROM HERE TO STEP 3 — for the new session

Both downstream specs already exist and are largely adjudicated. **Nothing is built in either.** The
chain is strict: Step 2 cannot start until Step 1's re-run is accepted, and Step 3 cannot start until
Step 2 has emitted `harmonised.parquet`.

**Step 1 — close it.** The hand-off block above is the whole task list. Step 1 is done when the
sixteen-gate round passes with its acceptance tests **seen**, every `NOT CHECKED` carries a spec reason,
and merge 2 of 2 is applied to `acquisition_manifest.json`. One Step 1 item can never be done in-session:
**item 1.4, the Eurostat entity-recognition enquiry, is AUTHOR-ONLY.** Do not simulate it, do not mark it
done, do not let it block the rest.

**Step 2 — `Step2_docs/4thJ_02_harmonisation.md` (365 lines) + `..._val.md`.** Status: specified by
`RL02`, adjudicated in part by `RL17`, nothing built. Its `WHAT BLOCKS THIS STEP` section is already
rewritten for the three-country corpus and says the only remaining precondition is our own Step 1 re-run.
Eleven gates, twelve perturbations. Decided and not to be relitigated: `ACT` keeps 3 digits; location `11`
= home, merging dwelling, yard and garden; the indoor rule; age floor **10** and a 10-minute grid; day
origin **04:00 with cyclic rotation** (D-S2-5 — `RL02`'s 06:00 is an error we measured against the files:
ES 06:00, IT 04:00, UK 04:00). Still open and **manager-owned**: slot-vs-episode basis and secondary
activity arity/granularity. 🔴 **Step 2 must consume parquets written to the current record contract**
(M-1..M-5 changed it) — not the ones on the cluster from the void round.

**Step 3 — `Step3_docs/4thJ_03_serialisation.md` (297 lines) + `..._val.md`.** Status: format decided
(`RL07`), tokenizer decided by our own measurement (OLMo / dolma2 BPE, Speed jobs 1234177 / 1234199 /
1234216), implementation open. Decided: episode form not slot form; tuple `DUR,ACT,LOC,COP` with **no
`START`**; `LOC` is the real HETUS code read from `crosswalk_location.csv`, never hard-coded as a range;
**no tokens added to the vocabulary**; **no mnemonic remapping** (it costs 5.5 % on OLMo). Open by design:
`COP` packing, which must be **chosen by measurement and the measurement recorded**. **Co-presence set
membership is a Step 3 question, not a Step 2 one, and it is untouched** — it is the third of the three
heterogeneities and it is the manager's to decide.

**Reaching Step 3 in one session is realistic only if Step 1's round passes first time.** If it does not,
close Step 1 properly and stop there — a Step 2 built on an unaccepted Step 1 is worse than no Step 2.

---

## 🟡 STATUS 2026-08-16, evening — ROUND 2 IS COMMISSIONED AND RUNNING (employee session)

Author instruction, 2026-08-16: *finish Step 1, then Step 2, then continue to the end, updating each
document's Progress Log at every step*, and **use a fresh cheap employee agent for each round**.

**Prompt written: `4thJ_employee_step1_gates16_round2_2026-08-16.md`, in this folder.** It is deliberately
narrow — it points the employee at the UK reference implementation and the acceptance tests only, and
forbids reading the pipeline document, the step specifications and this file. The previous employee burned
517k tokens re-reading the tree and was stopped mid-work.

Its six tasks: port **M-6** and **M-7** from `4thJ_gates_step1_uk.py` to Spain and Italy; run-stamped
output dir `outputs_step1/run_<YYYYMMDD-HHMM>/` written by **both the reader and the gate runner**;
`V1.a` moved to a fourth job; local dry runs first; four `sbatch` jobs on `ps` at `-t 7-00:00:00`.

🔴 **MANAGER DECISION, 2026-08-16, and it narrows the previous hand-off on purpose: only `V1.a` moves to
the fourth job.** The earlier text said "move the vacuity guards `V1.a`–`V2.e`". `V1.b` (inputs printed
before any verdict), `V1.c` (status read from the computing process) and `V1.d` (unrecognised code printed
and refused) are **per-run properties of one country's battery**; hoisting them into a cross-country job
would make them unfalsifiable. Recorded here as a scope change rather than folded in quietly.

**Acceptance tests handed down verbatim** — `corrupt_archive_byte` newly failing `G1.6a` on all three; the
`null` perturbation moving nothing on Spain; M-7 recovering the four UK arms masked by the deliberate
`G1.4` `4276` FAIL; every `NOT CHECKED` carrying a spec reason. The employee **reports** an audit
perturbation that does not fire; it never decides the reversal.

**Deliverable the manager must merge when it returns:** `proglog_entries_round2.md` in the run dir. The
employee does not touch `4thJ_01_corpusAcquisition.md` or its validation document. **Merge 2 of 2 stays
deferred until the manifest fragments are final.**

---

## ✅ STEP 2 — THE THREE HETEROGENEITIES ARE DECIDED, 2026-08-16. D-S2-6, D-S2-7, D-S2-8

The parent document held three questions open as **manager-owned inputs to the crosswalk, not
afterthoughts to it**. All three are now closed from measured codebook facts and written into
`Step2_docs/4thJ_02_harmonisation.md` (decisions + Progress Log) and `..._val.md` (three new gates,
three perturbations, two vacuity guards, Progress Log). **Step 2 is now fully specified.** It is still
blocked on one thing and one thing only: the sixteen-gate Step 1 re-run.

**D-S2-6 — the basis is the EPISODE**, on a 10-minute grid. Forced, not chosen: Step 3 serialises
episode form, so a slot-based table would be re-collapsed one step later under a rule no Step 2 gate
can see. Spain ships 144 fixed slots (origin 06:00) and is the only country reconstructed; the UK ships
native episodes with a stored `eptime`; Italy ships native minute-resolution clock fields with no slot
at all. **Italy is not re-slotted** — its durations are all multiples of 10 as delivered, which `V2.g`
asserts and the transform never assumes.

🔴 **D-S2-6-a is the finding of the day.** Spain's episode-boundary key was read out of the Step 1
reader rather than assumed: `APRIN, LUGAR + all six co-presence flags`
(`tools/4thJ_read_spain.py:347`). The secondary activity is **not** in it — the feared over-split did
not happen. But co-presence **is**, so a Spanish episode splits when only co-presence changes, and the
UK's and Italy's respondent-declared episodes do not. **Spain has more and shorter episodes by
construction, for a reason with nothing to do with Spanish behaviour.** Consequence, written down
before anyone can read it as a result: **no cross-country comparison of episode count or mean episode
duration, in any step, in any gate, or in the paper.** Time budgets are invariant to how a day is cut,
which is exactly why `G2.9` is stated on budgets. 🔴 **The key is not "fixed" to match the others** —
dropping co-presence would let one episode carry two co-presence states, which `DUR,ACT,LOC,COP` cannot
represent. Reported, not engineered away.

🔴 **D-S2-7 retracts work item 2.1's "no second crosswalk is built".** True of Spain and the UK, **false
for Italy**: `catcon` is `CLS-var13`, 34 flat 2-digit modalities, *a different and coarser
classification, not a truncation of `catpri`* (F-IT-3). So: **arity 1** (corpus minimum — the UK's
second and third columns become named extras, never serialised, never conditioned on, exactly like
`cop_extra_*`); **its own crosswalk**; **2-digit granularity for `ACT2` only**, because no third digit
for Italian secondary activity exists to be recovered and inventing one is fabrication. 🔴 **`ACT`
keeps 3 digits — decision 6 untouched** — and the asymmetry is deliberate: Step 9 reads the *primary*
activity. Also: coverage percentages are **not** comparable as delivered (Spain 12.2 % of *slots*, UK
27.75 % of *episodes*), and Spain's within-episode `ACT2` rule is **inherited, not adopted** — Step 1
already took the first slot of the run, and the disagreement rate is unmeasurable downstream.

🔴 **D-S2-8 widens the shared co-presence core from five flags to six, correcting D-S2-2.** `PADRES` is
not a Spanish extra: **all three countries record parent co-presence** — Spain in one flag, the UK in
two (`WithMother`/`WithFather`), Italy in two (`cmadre`/`cpadre`). `cop_parent` becomes the sixth
shared flag, formed as an OR, **with the components kept as extras because an OR that discards its
inputs cannot be audited.** Six flags every country records beats five plus an orphan, and it moves in
the direction D-S2-2 already pointed. Italy's `cfrate` (siblings) is a genuine extra.

🔴 **Two co-presence traps, both silent.** `WithNA` is **not** a missingness flag (F-UK-4) — `WithMiss`
is, and it is the corpus's only one. And **Spain codes `1 = yes`, `6 = no`, so `6` is truthy**: any
recode written as `bool(x)` makes every Spanish respondent co-present with everybody at once, and it
would pass mass conservation, day closure, crosswalk totality and every activity gate without a murmur.
`G2.14` exists for that one bug.

🔴 **The "with children" flag means three different things and it cannot be fixed.** Spain's `MENOR` is
*minors under 10 living with you*; the UK's `WithChild` is **0-7 only**, with children 8+ already
pooled into `WithOther` and **unrecoverable by any crosswalk**; Italy's `cfigli` has no stated bound.
Mapped with all three definitions on the row, and **no claim anywhere may rest on comparing it across
countries** — a lower UK prevalence is a definition, not a fact about British households.

**Step 2 is now fourteen gates and fifteen perturbations.** New: `G2.12` Spanish rotation round-trip
(the executable form of D-S2-5's own invertibility requirement, which lived nowhere a runner could read
it); `G2.13` secondary-crosswalk separateness; `G2.14` co-presence value-map integrity. **Two of the
three are *derived*, not project-chosen.** New guards `V2.f` (six-flag list and the value map imported
from the shipped `crosswalk_copresence.csv`, never restated in the validator) and `V2.g` (a non-multiple
-of-10 Italian duration is refused, never rounded). 🔴 **`G2.12`'s perturbation is a wrong-*direction*
rotation, not a dropped tail**, because a cyclic shift conserves every minute, closes every day at 1440
and leaves every activity budget exactly unchanged — G2.3, G2.4, G2.9 and G2.10 are structurally blind
to it. A dropped tail would break G2.4 too and prove nothing, the same argument that shaped `G2.11`.

**One stale perturbation rewritten and it could not have been run as written:** *"drop all French
respondents aged 11-14"* → *"drop all Spanish respondents aged 10-14"*. **No threshold was moved
anywhere.**

### 🔴 Four open items carried out of Step 2, named rather than folded in quietly

1. **The UK's `WithOther` scope is inferred**, from `WithOtherYK`'s own label, not quoted from the CTUR
   variable list. Confirm there before `crosswalk_copresence.csv` is frozen.
2. **Spain's secondary-activity code list is not stated** in `codebook_facts_spain.md`. Confirm before
   `crosswalk_activity_secondary.csv` is frozen.
3. **No gate checks that `cop_parent`'s OR is built from *both* national components.** Recorded as a
   hole and **proposed to the author**, exactly as the D-S2-3 hole was before `G2.11` closed it.
4. **Spain's within-episode `ACT2` disagreement rate** is a one-line addition to the Step 1 reader's
   parse report, or it is declared unmeasured in the methods. Not quietly dropped.

### What happens next, in order

1. **Step 1 round 2 returns** → read the two audit perturbations first, then `V1.a`, then the sixteen
   gates. Verify against `gate_report_step1_*.txt` directly, never against the employee's summary.
2. **Merge 2 of 2** and the `proglog_entries_round2.md` merge into `4thJ_01_corpusAcquisition.md` and
   `..._val.md`, append-only, with a manager's note on what was **not** independently verified.
3. **Only then does Step 2 build.** It consumes the parquets from the accepted round's **run-stamped
   directory**, never a stale copy. 🔴 A Step 2 built on an unaccepted Step 1 is worse than no Step 2.
4. **Step 3** stays as specified: `DUR,ACT,LOC,COP`, episode form, no vocabulary additions, no mnemonic
   remapping. `COP` packing is still open and must be chosen **by measurement, with the measurement
   recorded** — and it now packs **six** flags, not five.

---

## 🟢 STEP 1 ROUND 2 IS SUBMITTED, 2026-08-16 21:40

**Speed jobs: ES `1252522`, IT `1252523`, UK `1252524`, vacuity `1252525`** (the last with
`--dependency=afterok:1252522:1252523:1252524`). All four `sbatch`, partition `ps`, `-t 7-00:00:00`.
Run stamp **`run_20260816-2140`**; outputs land in `Step1_docs/outputs_step1/run_20260816-2140/` and
on the cluster at `/speed-scratch/o_iseri/4J/outputs_step1/run_20260816-2140/`. 🔴 **Nothing is copied
back into the flat `outputs_step1/` directory.**

**What was built this round:** M-6 and M-7 ported from `4thJ_gates_step1_uk.py` into
`4thJ_gates_step1_spain.py` and `4thJ_gates_step1_italy.py`; `tools/4thJ_vacuity_step1.py` written,
carrying **`V1.a` only**; run-stamped output directory; four jobs instead of three.

### 🔴 The local dry runs, verified by the manager against the report files, not against a summary

**Spain is clean and the round-1 defect is gone.**

* `G1.6a` **PASS**, `8 archives checked, resolved under --raw=... (M-6, never local_path taken
  literally)`, and **`corrupt_archive_byte` made it fall.** Acceptance test 1 holds on Spain: the gate
  is no longer void.
* **`null` failed `[]`.** Acceptance test 2 holds. Round 1's `🔴 NULL PERTURBATION MOVED A GATE` was
  entirely an artefact of the baseline-FAIL masking M-6 removes.
* 🔴 **Both audit perturbations FIRED, so neither M-1 nor M-3 is reversed.**
  `loc_undeclared_sentinel` fell `G1.4` (sentinel `-8`, confirmed absent from the transcribed list);
  `weight_blank_on_productive_row` fell `G1.7a`. This was the one outcome that could have forced a
  decision reversal, and it did not.
* **15 gates scored, 15 PASS, 0 FAIL, 15 of 15 seen failing, coverage clause satisfied.** The
  sixteenth is `G1.7b`, **NOT CHECKED permanently** with its reason printed: METH p.34 step 3
  ratio-adjusts the weights to the same population projection the gate would compare against, *"so
  this comparison cannot fail. Printed as evidence of nothing, kept visible so the hole it retired
  does not get re-invented."*
* `V1.a` **FIRED** on the single-country dry run, which is exactly the cross-country race TASK 4 moves
  into job `1252525`. **Expected, not a regression.**
* **UK M-7:** all four arms masked by the deliberate `G1.4` `4276` FAIL — `act_to_outside_list`,
  `act2_to_outside_list`, `act2_extra_2_to_outside_list`, `loc_undeclared_sentinel` — each printed
  `FIRED (sub-clause level, M-7)`. 🔴 **Dry run only; not yet re-confirmed from the cluster's own
  round-2 report.**

**The 21:10 overwrite of the flat `outputs_step1/` files was the previous session, not this round** —
confirmed independently by the manager from mtimes and from the dry runs writing only to scratch.
Round 1's cluster reports survive as `.bak_2026-08-16`.

### 🔴 What the manager does when the jobs land, in this order

1. **The two audit perturbations first** — `loc_undeclared_sentinel`, `weight_blank_on_productive_row`
   — on all three countries. If either reports `DID NOT FIRE` and M-7 sub-clause masking does not
   explain it, **the decision it audits is REVERSED and the perturbation is not adjusted.**
2. **Then `V1.a`** in `vacuity_report_step1.txt`. It must now PASS, having found three parquets in the
   run-stamped directory. 🔴 **If it passes by finding stale files it has not passed.**
3. **Then the sixteen gates**, read from `gate_report_step1_<country>.txt` directly, never from an
   employee summary. Italy's `G1.6b` FAIL and the UK's `G1.4` `4276` FAIL are **expected and preserved**.
4. **Merge 2 of 2** — `acquisition_manifest_uk.json` + `..._italy.json` → `acquisition_manifest.json`.
5. **Merge `proglog_entries_round2.md`** into `4thJ_01_corpusAcquisition.md` and `..._val.md`,
   append-only, with a manager's note recording what was **not** independently verified.
6. **Only then does Step 2 build**, on the parquets from `run_20260816-2140`.

**Item 1.4, the Eurostat entity-recognition enquiry, is still AUTHOR-ONLY and still does not block.**

---

## 🟡 STEP 3 — UPDATED 2026-08-16, AND THE `COP` PACKING MEASUREMENT IS COMMISSIONED

Step 2's three heterogeneities land in Step 3's record format, and they had to land **before** the
packing was measured. Both Step 3 documents now carry the changes and a Progress Log entry.

* 🔴 **`COP` packs SIX flags, so the range is 0-63, not 0-31.** D-S2-8 promoted `cop_parent` to the
  shared core. A five-flag measurement would have been the right answer to the wrong question, which
  is why this reached Step 3 first.
* 🔴 **The `act2` leak argument is RETIRED — and it was the stronger of 3.2-bis's two reasons.** That
  section kept secondary activity out of the tuple mainly because it was measured on one country of
  four and might become a symbol only Spain could emit. **All three countries record one** (Spain
  `ASECU`, UK `What_Oth1`, Italy `catcon`), so **the branch that would have excluded it permanently is
  closed.** Only the token-cost argument survives, and that is a measurement, decided the way `COP`
  packing is. 🔴 **If the measurement puts `ACT2` in the tuple it must happen BEFORE `corpus.jsonl` is
  emitted** — a fifth element added later invalidates the corpus, the Step 7 grammar and every fold.
* **But D-S2-7 changed what would be serialised:** `ACT2` is arity 1 and **2-digit** (Italy's `catcon`
  is a different, coarser list), while `ACT` stays 3-digit. That asymmetry is now written into the
  record format instead of waiting to be discovered by whoever writes the encoder.
* **`act2_coverage.md` needs three rates, not four, and the bases are not interchangeable.** Spain
  12.2 % of slots / 18.8 % of episodes; UK 27.75 % of episodes; **Italy still unmeasured.** The UK and
  Italy ship episodes natively and have **no slot base at all**.
* **`G3.8` widened to six flags.** 🔴 **No `COP` gate is pre-registered until the measurement exists** —
  a threshold written ahead of its measurement is a threshold chosen to be passed.

**Commissioned on Speed:** the `COP` packing measurement. Five candidate encodings for the six bits
(single 0-63 integer; six characters; two octal digits; two hex characters; six comma-separated digits
as the do-nothing baseline), each measured **in situ** inside a full episode tuple and a full
25-episode diary, **sweeping all 64 values and reporting the worst case.** Deliverables
`Step3_docs/outputs_step3/cop_packing_measurement.md` and `proglog_cop_packing.md`; the employee
**recommends**, the manager decides.

🔴 **In situ and worst case are both deliberate, and both are scar tissue.** `RL18` reached the wrong
recommendation on this project by counting a bare fragment — 8 tokens for an episode that costs 11 in
context. And a packing that is 1 token for `7` and 2 for `63` costs 2; 64 values is small enough that
sampling it has no excuse.

---

## 🟢 STEP 1 ROUND 2 IS READ AND ACCEPTED — 2026-08-16, ~22:15

All four jobs COMPLETED, exit `0:0`: **1252522** ES (18 min), **1252523** IT, **1252524** UK,
**1252525** round-level vacuity. Run stamp `run_20260816-2140`. 🔴 **Read by the manager from
`gate_report_step1_<country>.txt` and `vacuity_report_step1.txt` directly, in the mandated order, never
from an employee summary.**

**The two audit perturbations fired everywhere. M-1 and M-3 STAND.** Spain and Italy: both
`failed`/`newly-failed` as pre-registered. The UK's `G1.4` FAILs at baseline on the real `4276` defect,
so its perturbation had nowhere to shake the gate from — and **M-7 recovered the observability**, with
per-field movement printed on all four masked arms and the status honestly stated as *unchanged, FAIL
both times*. 🔴 **M-7 did not flip a gate, which is exactly its design.**

🔴 **Round 1's `NULL PERTURBATION MOVED A GATE` alarm is RETIRED.** It was baseline-FAIL masking
throughout. Spain's `null` row now reads `failed []`.

**`V1.a`: PASS, 3 of 3, `['ES','IT','UK']`**, and the report states it scanned only this run's `--out`
directory, *"never a shared/leftover `outputs_step1/`"*. It did not pass on stale files.

**Gates.** Coverage clause satisfied in all three countries. Spain 15 scored / 15 PASS / 0 FAIL.
Italy 13 / 12 / **1 — `G1.6b`, expected**. UK 14 / 13 / **1 — `G1.4` on `4276`, expected.** Both
baseline FAILs survived, which is the point: a round that cleared them would have been evidence M-1 and
M-2 disarmed their gates. Every `NOT CHECKED` carries its reason on the same line, and each says why the
comparison **cannot** fail rather than why it was skipped.

### 🔴 One defect found, and it is a reporting defect — do not re-run for it

**The four reports disagree about `V1.a`.** Italy and the UK print `FIRED (2 of 3)`; Spain, which ran
last, prints `clear (3 of 3)`; the round-level report says `PASS`. Same guard, three answers.

Cause: each country's runner **still computes and prints `V1.a` itself**, while the other countries'
jobs are unfinished. `V1.a` moved to the chained fourth job to stop precisely that; the old print was
left behind.

* **`vacuity_report_step1.txt` is the authority.** The per-country `V1.a` lines in this round's reports
  are **stale artefacts and must not be quoted.**
* The print is being **removed** from all three runners, not relabelled — a guard printed twice with two
  answers is worse than not printed. `V1.b`/`V1.c`/`V1.d` stay per-country and are untouched.
* 🔴 **The battery is NOT re-run.** No scored result changes.

---

## 🔵 WHAT IS RUNNING RIGHT NOW, AND WHAT COMES NEXT

**Two employees are out.**

1. **Step 1 closure** — scp the run-stamped directory down from Speed, **merge 2 of 2**
   (`acquisition_manifest_uk.json` + `..._italy.json` → `acquisition_manifest.json`, `local_path` and
   `local_root` byte-for-byte untouched, backup first, entry counts reported), and remove the stale
   per-country `V1.a` print from the three runners. **Code only, no re-run, no job submitted.**
   Deliverable: `run_20260816-2140/proglog_merge2_and_v1a_fix.md`.
2. **Two Step 2 open items, read-only from the codebooks** — (a) the UK's `WithOther` scope: is the
   children column really **0-7 only**, with 8+ pooled unrecoverably? (b) Spain's `ASECU`: is it drawn
   from the **same** classification as the primary activity, or a **separate** list the way Italy's
   `catcon` turned out to be? 🔴 **`NOT STATED IN CODEBOOK` is a correct answer to either**; an inferred
   one is a task failure. Deliverable:
   `Step2_docs/outputs_step2/open_items_uk_withother_and_spain_asecu.md`.

**Already merged into the Step 1 documents** (append-only, both files): the round-2 acceptance with the
gate table, the two audit perturbations, the `V1.a` contradiction, and the employee's own "not
independently verified" list — which still contains two open items worth closing before Step 2 consumes
these parquets: **no md5 was run** between the cluster copies of the four tools and the local repo
copies, and the static reference files in the cluster's flat `outputs_step1/` were never checked
byte-identical to the ones the dry run used.

**Then, in order:**

1. Read the two employee deliverables. **Merge 2 of 2 is the last thing Step 1 owes.**
2. Decide the two open items from the evidence returned, and write them into
   `4thJ_02_harmonisation.md` — including the case where the answer is `NOT STATED`, which changes the
   crosswalk's mapping row rather than being quietly resolved.
3. 🔴 **Then Step 2 builds**, on the parquets in `run_20260816-2140`, against **fourteen gates and
   fifteen perturbations** and vacuity guards `V2.a`-`V2.g`.
4. Two Step 2 open items remain and are **not** blockers: no gate checks that `cop_parent`'s OR uses
   both national components (**author's call**), and Spain's within-episode `ACT2` disagreement rate is
   **unmeasurable downstream** because Step 1 already took first-of-run.
5. Italy's `act2` coverage is still unmeasured; `act2_coverage.md` is incomplete without it.

**Item 1.4, the Eurostat entity-recognition enquiry, is still AUTHOR-ONLY and still does not block.**

---

## 🟢 STEP 3 — `COP` PACKING IS DECIDED. D-S3-1, 2026-08-16

The measurement returned. **Speed job 1252633**, COMPLETED in 42 s, OLMo/dolma2 BPE, every candidate
measured in situ inside a full episode tuple and a full 25-episode diary, **all 64 values swept**.
Report: `Step3_docs/outputs_step3/cop_packing_measurement.md`.

**`COP` is a single decimal integer, 0-63.** Worst case per episode / per 25-episode diary: **decimal
8 / 200** (chosen); octal 8 / 200; hex 9 / 210; six characters 9 / 225; the six-comma-digit do-nothing
baseline **18 / 450**.

Three separate findings, and they are worth keeping separate:

* **Six flags cost nothing.** 8 tokens/episode is what the *old single-digit* `COP` field already cost,
  so **D-S2-8 imposed no token penalty** and nothing needed relaxing on its account.
* **The do-nothing baseline more than doubles the corpus** — 450 against 200. The saving is now
  measured, not asserted.
* 🔴 **Six-character binary was rejected by a pre-registered threshold, not by taste.** At 225 tokens
  per diary it exceeds **`G3.5`'s median band of 220** before a single real record exists. Adopting it
  would have meant moving `G3.5`. **The band did its job at the design stage** — the earliest and
  cheapest place a pre-registered threshold can ever pay for itself. Decimal beat octal only on
  auditability; nothing measured separates them.

**`G3.14` was pre-registered AFTER the number, and the order is the point.** Two sub-clauses, M-7
attribution applies: **(a)** every `COP` parses as an integer 0-63 with **no leading zeros** (`7` and
`07` are two spellings of one value); **(b)** per country and per flag, the count of episodes with that
bit set — decoded from the **`bit_position` column of `crosswalk_copresence.csv`** — equals the count in
`harmonised.parquet`. Guards `V3.e` (FAIL if that column is missing or not exactly `{0..5}`) and `V3.f`
(print both sides' prevalence first) came with it. **Step 3 is now fourteen gates, fifteen
perturbations.**

🔴 **The bit order lives in `crosswalk_copresence.csv`, and the encoder READS it — never hard-codes it.**
An encoder and decoder sharing a hard-coded order round-trip perfectly through `G3.1` and mean something
else; `G3.14 (b)` catches that **only because its reference is a file the encoder did not author**. This
was pushed back into **Step 2**, which is where the flags are defined: `V2.f` now FAILs if the column is
missing, because Step 2 writes the file and is the cheapest place to catch its absence.

🔴 **Recorded as open, honestly.** This was a **token-cost** measurement and answers only that. Whether
a packed integer is as **learnable** as six positional characters is unmeasured — the model must recover
64 arbitrary codes instead of reading six aligned slots. The packing **freezes when `corpus.jsonl` is
emitted**, so the only place to test it is a **Step 4 ablation on a subset, beforehand**. Not a blocker;
a decision with a known unmeasured edge.

Also carried forward unverified: the claimed vocabulary identity between `OLMo-2-0425-1B` and
`Olmo-3-1025-7B` was a **premise of the task, not re-derived**, and the earlier 200-token reference from
jobs 1234177/1234199/1234216 was quoted, not re-run.

---

## 🟠 ROUND 3 IS RUNNING — 2026-08-16, ~22:10. D-S1-6, the manifest union

**Merge 2 of 2 was REFUSED by the employee, and the refusal was correct.** `acquisition_manifest.json`
is **Spain's manifest, flat at the root** — there is no `"es"` key and there never was. The UK fragment's
own `_note` describes merging *"under a top-level 'uk' key alongside the existing 'es' entry"*, a
structure that does not exist. And the UK records provenance as `outer_archive`/`inner_archive`/
`delivered_files_md5[17]`, not as a `files[]` array, so **"number of archive entries" was not even a
common quantity** to verify a merge against. 🔴 **Merging anyway would have invented the provenance** —
the one thing this manifest exists to carry.

**D-S1-6.** `acquisition_manifest.json` is a **root-keyed union** `{"es":…, "it":…, "uk":…}`, each
country's entry carried across **unchanged, including its own field names**. No shape normalisation,
none at all. Every `local_path` and `local_root` survives verbatim. Spain's flat file is now also
`acquisition_manifest_spain.json`, which is what it should always have been called.

**Done:** union written, UK `_note` dropped and quoted; entry counts equal fragment-to-merged (es 8/8,
it 4/4, uk 19/19); a **programmatic** comparison found zero `local_path`/`local_root` string differences.
The three runners index their own country key and **raise if it is missing — never fall back to reading
the file flat**, which would let `G1.6a` pass on the old shape forever. All three `py_compile` cleanly,
which also closes the earlier "never syntax-checked" hole.

**Round 3 submitted.** Run stamp `run_20260816-2210`. **ES 1252724, IT 1252726, UK 1252727, vacuity
1252728** (`afterok`). 🔴 **Re-running was mandatory, not optional: `G1.6a`'s input changed shape, so its
basis changed, and a basis change is not an additive fix.** The `V1.a` print fix rides along — which
reverses the earlier decision not to re-run for it, and removes the contradiction from the archive
instead of annotating it.

### 🔴 WHAT ROUND 3 MUST SHOW, OR IT IS REJECTED

Read from `gate_report_step1_<country>.txt` and `vacuity_report_step1.txt` in
`run_20260816-2210` **directly**, never from a summary:

1. `G1.6a` still **PASS** on all three, reading the merged manifest.
2. `corrupt_archive_byte` still fells `G1.6a` on all three.
3. `strip_url_from_manifest` still fells `G1.6b` on the UK.
4. 🔴 **Italy's `G1.6b` and the UK's `G1.4` `4276` baseline FAILs are both STILL THERE.** If either
   clears, the merge broke something and the round is rejected.
5. `V1.a` **PASS 3 of 3** from the round-level report, and the three per-country reports contain **no
   `V1.a` verdict line at all**.

---

## ✅ BOTH STEP 2 CODEBOOK OPEN ITEMS ARE CLOSED — D-S2-9 AND D-S2-10, 2026-08-16

Evidence: `Step2_docs/outputs_step2/open_items_uk_withother_and_spain_asecu.md`, verbatim quotations
with page references throughout.

**D-S2-9 — the UK's `WithOther`: CONFIRMED, mapping frozen.** The data dictionary label says it
outright, `Pos. = 45`: *"With other person(s) (incl. child 8+ years)"*, against `Pos. = 44` *"With child
0-7 years"*. CTUR p. 11-12 §5.2 corroborates in prose independently. `WithOther` → *other household
members*, `WithOtherYK` → *other persons*.

🔴 **It sharpened the children-flag problem instead of closing it, and the sharper form is the useful
one.** Not "three different things" — **Spain and the UK share a structure**, a cut-off with older
children spilling into household-others, at **10** and **8**; **Italy has no cut-off at all.** Two
countries differ by two years, the third differs in kind. **`cop_children` may not be compared across
countries anywhere**, and any Spain-UK comparison must state the 10-versus-8 cut-off in the same
sentence.

**New `NOT STATED IN CODEBOOK`:** whether `WithOtherYK` absorbs any of the 8+ children population.
Neither source addresses it; not assumed away.

**D-S2-10 — Spain's `ASECU` is the SAME list as the primary activity.** Stated three times: LAYOUT
`F DIARIO2` gives `APRIN` (row 32) and `ASECU` (row 37) the identical `Valores válidos = Lista EET` at
the same 3-digit width; METH p. 49 *"se utilizaron los mismos códigos…"*; METH p. 65-66 *"NOTA: Las
actividades principales y secundarias se codificarán utilizando esta misma lista."*

🔴 **The generalisation was the trap.** Italy's `catcon` made "secondary activity gets its own
classification" look like the rule. **Two of three countries code it in the primary list; exactly one
does not.** Assuming Spain matched Italy would have built a redundant Spanish crosswalk with nothing
checking it against the primary one.

**Consequences.** `crosswalk_activity_secondary.csv` stands, `G2.13` unchanged — but it now holds **two
kinds of row**: truncations (ES, UK) and a real crosswalk (IT). 🔴 **Italy's 2-digit target may never be
computed as "the first two digits of the source"** — the source is already 2-digit and means something
else. The `source_list` column is what tells them apart.

**`G2.15` added** — for Spain and the UK only, every secondary row must agree with the primary crosswalk
on the same code truncated to 2 digits, **0** disagreements; Italy excluded by construction. 🔴 **`G2.13`
and `G2.15` are opposites and both must hold.** A single "the secondary crosswalk is consistent with the
primary" gate would have been wrong for one country or the other whichever way it was written.

**Inherited rather than measured, so it is not mistaken for evidence:** Spain's 116 modalities come from
the **primary** enumeration via the "same list" statements (a listing under `ASECU`'s own heading is
`NOT STATED`); and the blank sentinel rests on **one document only**, LAYOUT row 38, with METH silent
across 127 pages.

**Step 2 is now FIFTEEN gates and SIXTEEN perturbations**, `V2.a`-`V2.g`, none run.

---

## ▶️ NEXT, IN ORDER

1. **Read round 3** against the five-point checklist above. Merge its fragments
   (`run_20260816-2140/proglog_manifest_union_and_round3.md` is already written; the round-3 reports are
   not yet read by anyone).
2. **Then Step 2 builds**, on the parquets from the accepted run. Fifteen gates, sixteen perturbations,
   `V2.a`-`V2.g`, four crosswalks (activity, secondary activity, location, co-presence — the last
   carrying `bit_position` 0-5 for D-S3-1).
3. **Still open in Step 2 and NOT blockers:** no gate checks that `cop_parent`'s OR uses both national
   components (**author's call**); Spain's within-episode `ACT2` disagreement rate is **unmeasurable
   downstream**; Italy's `act2` coverage is **still unmeasured** and `act2_coverage.md` is incomplete
   without it; `WithOtherYK`'s scope re 8+ children is `NOT STATED`.
4. Then Step 3 builds, then `prereg.md` freezes, then the first Leg-5 submission, then Steps 4-9.

**Item 1.4, the Eurostat entity-recognition enquiry, is still AUTHOR-ONLY and still does not block.**
