# 4J — cross-step analysis, Steps 0–11

### What the whole pipeline actually produced, read in one place, before any manuscript text is written
#### Written 2026-09-13 (last+264), immediately after Step 11 closed. Parent: `../4thJ_00_HETUS_LLM_Pipeline.md`. Writing notes: `4thJ_writeup_notes.md`.

---

## 0. HOW THIS DOCUMENT WAS MADE, AND WHAT IT IS NOT

🔴 **This is an ANALYSIS of records already on disk. Nothing here was re-computed, no gate was re-run,
no threshold was touched, and no number was invented.** Every figure below is read out of a step's own
implementation or validation document, or out of the artefact that document names. Where a document
and its artefact disagree, the disagreement is printed rather than resolved.

⚪ **It is not a manuscript, not an outline, and not a decision document.** It raises no `D-` decision
and rules nothing. Its job is to let the writing phase start from one consistent picture instead of
eleven separate append-only logs.

🔴 **Three reading rules this pipeline enforces on itself, and which this document obeys:**

1. **The header is never the state.** Nearly every step document's `## STATUS` header is stale — Steps
   2, 3, 4, 5, 6, 7, 9 and 11 all carry a header saying `OPEN` or `PLANNED` that a later dated entry
   contradicts. The convention is additive: **the last dated entry governs and the header is not
   rewritten.** Anyone quoting a status from a header is quoting a superseded sentence.
2. **A closed step is not a passing step.** Step 4 closes with four failing gates and says so in its
   own words: *"Closing is not passing: never write Step 4 up as clean."* The same is true of Steps 5,
   6, 7, 9 and 11.
3. **A failing gate's perturbation demonstrates nothing.** Where a gate already FAILs at baseline, its
   registered mutation is reported `ALREADY_FAILING_AT_BASELINE`, never as a hit. Several coverage
   clauses in this project read FAIL **for vacuity, not for weakness**, and those two must never be
   collapsed.

---

## 1. THE PIPELINE IN ONE PAGE

| Step | What it delivered | Final state |
|---|---|---|
| **0** | Feasibility gate — four kill-switch questions to external research | CLOSED 2026-08-14. **One switch FIRED:** trained weights may not be released (data agreement, not model licence). No code, no data, no gates |
| **1** | Corpus acquisition — HETUS, three countries, one wave each | CLOSED for Step 2's purposes. **ES 15 PASS / 0 FAIL · IT 12 PASS / 1 FAIL · UK 13 PASS / 1 FAIL**, both FAILs real data properties, not defects |
| **2** | Harmonisation — one activity/location/co-presence alphabet | SHIPPED. **16 PASS / 1 FAIL (`G2.18`) / 1 NOT CHECKED (`G2.10`)**. 2,024,068 episodes, 73,254 diaries |
| **3** | Serialisation and tokenisation | DONE. **19 of 20 PASS**, coverage clause PASS. 73,254 records, 0 dropped |
| **4** | The fine-tuned LLM (LoRA on OLMo-3-7B) | CLOSED **with four permanently failing gates** — `G4.1`, `G4.3`, `G4.6`, `G4.12`. *"Closing is not passing"* |
| **5** | Conditioning and population linkage (IPF) | CLOSED. **34 PASS / 2 FAIL** of 36 gate-fold verdicts. Definition of Done **4 of 5, by declared exception** |
| **6** | **Transfer — leave one country out. Where the paper is won or lost** | CLOSED **on a negative result.** The transfer bar `G6.1` **FAILS 9 of 9**; the privacy audit is **a refusal** |
| **7** | Constrained generation and schedule production | Effectively closed. **21 PASS / 6 FAIL** on the reported leg; schedule board **6 PASS / 0 FAIL** |
| **8** | BEM simulation on TABULA archetypes | CLOSED, *"no open decision"*. Final rotated board **0 FAILs, `G8.7` permanent INFO**. 13,108 runs re-run once |
| **9** | Activity-driven end-use loads | **16 PASS / 2 FAIL / 1 INFO / 1 NOT CHECKED** (offline). Battery 13 HIT / 0 MISS / 2 already-failing |
| **10** | Real-stock UBEM on observed building stock | `C1` core-era: run, scored, **archived and NOT REPORTED**. `C2` no-core: **fully run (35,290 cells) and NEVER SCORED** — `R8` refuses `--scored` |
| **11** | End-use loads at stock scale — **the last step** | CLOSED. **14 PASS / 2 FAIL / 1 INFO / 1 NOT CHECKED** over 18 gates. Battery 18 HIT / 0 MISS / 1 already-failing |

🔴 **There is no Step 12.** `D-IMP-4`, 2026-09-03, on the author's own words *"i want clean pipeline,
not extra step like 12"*. **The pipeline is Steps 0–11 and Step 11 is terminal** — nothing consumes its
appliance-electricity and DHW output. What follows Step 11 is this analysis and the manuscript.

---

## 2. THE FOUR RESULTS THE PAPER ACTUALLY HAS

Everything else in eleven steps is machinery, provenance or a bar on what may be said. **These four are
the findings.**

### 2.1 🔴 RESULT ONE — THE TRANSFER CLAIM FAILS, AND IT FAILS CLEANLY

**`G6.1`, the pre-registered transfer bar, FAILS 9 of 9.** A raked pool of **real donor diaries** from
the other two countries, re-weighted by IPF to the held-out country's published marginals, reproduces
that country's time budget **two to six times better than the fine-tuned model**, on **every band of
every fold**.

| Fold | Model MAE (3 bands) | Raked-donor null | Margin |
|---|---|---|---|
| `es` | 36.81 / 34.52 / 44.32 | 9.94 / 8.82 / 11.81 | −26.9 / −25.7 / −32.5 |
| `uk` | 58.91 / 60.44 / 21.24 | 21.79 / 19.21 / 18.54 | −37.1 / −41.2 / **−2.70** (closest miss) |
| `it` | 62.24 / 33.95 / 35.84 | 19.51 / 13.85 / 15.51 | −42.7 / −20.1 / −20.3 |

🔴 **This is the paper's headline and it was pre-registered as the objective, not discovered as a
disappointment.** Author decision 4, taken 2026-08-14 before anything was trained, made beating the
raked-donor null *the* test. Author decision 3 removed the forecast that papers 2 and 3 both had, so
there is no softer claim to retreat to. `RL06` had already warned that the LLM loses to a from-scratch
conditional Transformer on every axis **except cross-national transfer** — so the paper was framed on
transfer, and transfer is what failed.

**Every other transfer gate agrees, which is what makes it clean rather than fragile:**
`G6.4` level-1 budget MAPE ≤ 15 % → **0 of 9 PASS**. `G6.5` (AND of three frozen criteria) → **9/9
FAIL**. `G6.6` held-in regression → **6/6 FAIL**. `G6.7` fictional-country control → **3/3 FAIL**, and
the split under `D-S6-13` shows it is not inert: the steering arm (R² ≥ 0.80) **PASSES** in all three
folds while the amplitude arm (slope ≥ 0.80) fails at **0.40–0.53** — *the model steers in the right
direction and delivers about half the amplitude.* `G6.8` joint structure → model arm FAILs sequence
and marginal in all three folds under both weight bases (dwell-time W1 **5–6.7×** its band; TVD
**3.3–4.7×**; diurnal JSD **4.6–7.9×**). `G6.9` nearest-neighbour → **9/9 FAIL**.

⚪ **And more capacity does not rescue it, from two directions measured independently.**
**(i) Backbone size:** 1.48 B → 7 B (4.7×) moved mean MAE **42.05 → 43.14** — *worse* — and `G6.4` went
1/9 PASS → **0/9**. **(ii) Trainable parameters:** the ceiling run trained **all 7,377,965,056**
parameters against the adapter's 79,953,920 (**92×**), everything else identical, and ended with a
**higher** train loss at every epoch (+0.0073 / +0.0071 / +0.0052). `FINDING 155`: *92× the trainable
parameters buys nothing.* **(iii) A different backbone:** the Qwen2.5-7B arm costs +24 % wall and
+16 % VRAM and buys nothing a gate can see — the only separating gate is `G4.9`, which Qwen fails.

🔴 **The one sentence that must survive review:** the four never-passing Step 4 gates (`G4.1`, `G4.3`,
`G4.6`, `G4.12`) are **not** why transfer failed. Each was diagnosed to its own mechanism — a noise
floor wider than its own band, an unsourced 0.15-nat bar, a band no trained adapter can satisfy, and a
shuffle that changes at most one of six prefix fields. **The model conditions, and it still loses.**

### 2.2 🟢 RESULT TWO — ONE APPLIANCE MODEL, THREE DIARIES, PEAKS SIX HOURS APART

`FINDING 142`, Step 9. The appliance-electricity peak of the generated stock falls at
**Spain 14:00 (503 W) · Italy 18:00 (404 W) · Britain 20:00 (416 W)**.

⚪ **One appliance set, one set of published parameters, one calibration, one trigger — the only thing
that differs between the three is the diary.** So the entire six-hour spread is the activity data
speaking, and this is the clearest positive result the end-use half of the pipeline has.

🔴 **It is the same measurement as `G9.12`'s FAIL, read from the other side.** `G9.12` scores the stock
load shape against CREST's reference statistics, which are **UK-2000**. A Spanish load shape built from
Spanish diaries is *supposed* to disagree with a British reference. Reported as a **shape result at
stock scale**, never as an accuracy claim, and never for a single dwelling (`G11.13`).

### 2.3 🔴 RESULT THREE — THE OCCUPANCY→HEATING EFFECT IS A NULL, AND THE ONE CLAIM THAT SURVIVED IS ABOUT GEOMETRY

This one has to be told with its history, because the history is the result.

The occupancy sweep holds the annual mean of `phi_int` at exactly **3.0 W/m²** at every level of `f`
by construction, so it **redistributes gain in time and can never add or remove energy**. Before the
rotation fix the campaign reported a peak effect that beat the between-diary spread. Then
`FINDING 141` landed: `D-S2-5` harmonised every diary onto a **04:00** day origin, EnergyPlus reads a
`Schedule:File` from **midnight**, and so **all 13,108 runs had applied occupancy four hours early.**
Everything was re-emitted and re-run.

**Post-rotation, at `f = 1.00` — these are the numbers that stand:**

| | `es` | `uk` | `it` |
|---|---|---|---|
| Peak effect | +2.7145 % | +0.0393 % | −0.6332 % |
| Between-diary spread | 4.9837 | 2.3797 | 1.5959 |
| **Ratio** | **0.54** | **0.02** | **0.40** |
| Annual median | **−1.5100 %** | **−0.3605 %** | **−0.4178 %** |

🔴 **Both channels are null.** The annual effect was already smaller than the between-diary spread in
all three folds before the rotation (`FINDING 134`); after it, **every annual median is negative at
every level of `f` in every fold** — the sign of the annual channel was a statement about the clock,
not about occupancy. And the peak claim, which `FINDING 134`'s own test had spared, **is now felled by
that same test**, with the sign flipping in Italy.

🟢 **What survives, and it is worth having:** the effect is **monotone in dwelling class in all three
folds, and the ordering is identical on both sides of the rotation** — `AB` largest everywhere,
**+3.46 / +1.04 / +0.50 %** at `f = 1.00`. **That is a claim about surface-to-volume ratio, not about
the clock.** The annual peak's *hour* never moves at any `f` in any fold, because it is the thermostat
recovery hour set in the IDF and not rotated.

🟢 **A second, cheaper null that is also a deliverable:** the whole day-to-year **chaining convention**
moves peak demand by **0.289 / 0.194 / 0.028 %** against `G7.18`'s 25 % trigger — not approached in any
fold, with seed noise beating rule effect on every metric. Decision 14 closed on it: `independent`,
seed 1, **and the empirical null itself is the published deliverable**, not the chosen rule.

⚪ **Real stock, independently, says the same thing.** Step 10's `C1` campaign: `f = 1.00` against
`f = 0.00` moves annual heating **under half a percent** (it −0.38…+0.45 %, uk −0.21…+0.10 %) while
moving the hourly peak up to **+7.92 %** and the peak hour by up to **41 hours** (`FINDING 184`). Same
conservation-by-construction cause. **Every claim from this design is a peak-and-timing claim.**

### 2.4 🔴 RESULT FOUR — THE PRIVACY AUDIT IS A REFUSAL, AND IT IS A MEASUREMENT, NOT A POSITION

`G6.10`, the loss-based membership-inference bar, reads **AUC 0.6645 against a registered ≤ 0.65** —
**FAIL**, z = 1.70 over the bar. The untuned-base floor is clean at 0.4886, which is what makes 0.6645
readable as membership signal rather than a split artefact. `G6.11` PASSES (0.5594 ≤ 0.75), `G6.12`
verbatim extraction PASSES (0 of 103 rare records), `G6.13` is **2 PASS / 1 FAIL** — `uk` fails.

**Under the pre-registration's own terms this is a refusal: the weights are not released, and the `uk`
synthetic population is withheld with them.** `es` and `it` ship.

🔴 **Three sentences the write-up must not produce**, all recorded in the audit itself:
never *"the privacy audit passed"* or *"4 of 4"* — it ships **two registered FAILs and one partial**;
the perplexity gap (0.0570 > 0.05) is **not independent confirmation**, because it fails on the
**permuted** adapter too (0.0511, `FINDING 116`) and therefore measures overfit of the diary *language*
rather than membership; and the Leg-5 coverage clause reads FAIL **for vacuity** — the same injections
do fell `G6.10` on all three Leg-4 folds.

⚪ **`D-S6-16` is the honest edge:** a pure-memorisation ceiling control scores **0.6496**, only 0.0149
below the reported 0.6645. Ruled (a′) on 2026-08-28 — it changes the methods wording, it does not gate
the release, because `G6.10`'s own registered FAIL already does.

---

## 3. THE FAILURES, GROUPED BY MECHANISM RATHER THAN BY GATE

🔴 **Eight gates across three steps are ONE finding.** Reporting them as eight separate failures would
overstate the number of things wrong with this pipeline by a factor of four.

### 3.1 The laundry mechanism — `D-S9-1` — `G9.6`, `G9.12`, `G11.6`, `G11.12`

`D-S9-1`, ruled (d) on 2026-08-20: **the appliance trigger fires from the PRIMARY HETUS activity code
alone**; secondary activity (`act2`) is dropped from calibration entirely. This mirrors what all four
source models (CREST, Widén, LoadProfileGenerator, RAMP) do natively — it was the conservative choice,
and its cost was declared at the time.

**Laundry is the archetypal secondary activity** — you start the machine and go and do something else.
So the model cannot see most laundry **by ruling**, and four gates measure the size of that:

- **`G9.6` FAIL** — eligible laundry minutes per dwelling-year measured at **es 2,462 / uk 1,589 /
  it 781** against a washing machine that needs 195.91 cycles × 138 min = **27,036 minutes**.
  Modelled/published ratio **0.776 / 0.179 / 0.092**.
- **`G9.12` FAIL** — stock load-shape R² **0.2967 / 0.4106 / 0.0346** against 0.85, at n = 100.
- **`G11.6` FAIL** at stock scale — three appliances 74–84 % below CREST's published cycle count and
  the laundry appliances **SATURATED**, in both folds.
- **`G11.12` FAIL** at stock scale — R² **0.4347** (`uk`, 7,602 flats) and **0.0781** (`it`, 29,902
  flats). `FINDING 272`: **CREST's reference profile is >77 % laundry at 11:00** while this model
  suppresses laundry starts **80–90 %**.

⚪ **Two much larger, independently drawn populations failing the same way is evidence the measurement
is real, not a defect to chase a PASS on.** No band was ever moved, at either scale. `G11.12` was
explicitly **not** reclassified `INFO`, because `D-S11-1`'s criterion is a *basis* mismatch and this is
a real shape correlation that could have passed if the shape had matched.

🔴 **`FINDING 137` is the sting and belongs in the same paragraph:** the generated diaries **do** carry
`act2` — **29.816 % of episodes, 26.308 % of modelled minutes**, over 29 distinct codes. The ruling
still stands (it rests on its precondition being unsatisfiable, not on serialisation), but the write-up
cannot say the information is absent. **It is present and deliberately unused.**

### 3.2 The denominator mechanism — `D-S11-1` — `G9.7`, `G11.7`

`G9.7` measured DHW at **100.16 / 117.65 / 91.06 L per person-day** against a registered 30–50 band and
failed by 2–4×. Work item 11.2 read the source instead of re-measuring, and found three things:
the band **was never Jordan & Vajen's** (they publish **200 L/day per DWELLING**, no per-person figure
and no 60 °C anywhere) — it traces to **Fuentes, Arce & Salom (2018)**, a source that appeared in no
citation table in this project until `FINDING 167` added it; the temperature explanation is **refuted**,
not merely unconfirmed; and **`G9.7`'s scored quantity is exactly `200 / n_members`** to within 0.0005
over all 300 rows — **the gate was measuring household size, not the DHW model.**

Ruled **(d)(ii) → (b)**: `G9.7` and `G11.7` are **permanent `INFO`**, **the band is NOT moved** (still
30–50 in the checker), and the medians are still printed as outside it. The gap is reported as a
**denominator incompatibility**, never as a model failure and never as a pass.

🔴 **The lesson that generalises, and it cost a detector:** retiring a gate silently retires the
mutation it detected. `G9.7` was the only detector of `scale_dhw_by_2`, so `D-S11-2` added **`G9.15`**
— stock **mean** L/dwelling/day against Jordan & Vajen's own 200 ± 10 %, a scale/regression arm and
explicitly **not** an external validation. It PASSES at **200.79 / 201.01 / 199.47** and was **seen
failing** at 401.58 / 402.03 / 398.93 on doubled draws. **`G11.18` inherits it and PASSES at stock
scale: 202.41 (`uk`) / 200.35 (`it`).**

### 3.3 The unsatisfiable-band mechanism — Step 4's four gates

Not one of these four is a statement about the model; each is a statement about its own check.

| Gate | Measured | Why it cannot pass |
|---|---|---|
| `G4.1` | band 0.80–1.25, width **0.45** | Its own sampling-noise floor on **frozen weights** is **0.529 / 0.658 / 0.385** — wider than the entire band. The verdict is seed-dependent: the same `it` adapter returns FAIL ×4 and PASS ×1. Ships FAIL, **RESOLUTION-LIMITED AT N=600** |
| `G4.3` | rise must be ≥ 0.15 nats/token; measured **0.068–0.106** | The sign is always right, and the no-adapter baseline rises only 0.0001–0.0011 — the fine-tune's rise is **84×–1062×** the untrained baseline. The 0.15 bar has **no justification anywhere** in the thresholds file |
| `G4.6` | merge drift < 1e-4; measured **2.7e-4–7.6e-4** | Scaling the adapter down **1000×** does not shrink the drift — it plateaus an order of magnitude above the band. **Only an adapter that learned nothing passes.** And the drift is behaviourally real: merged vs unmerged produce different diaries in **81–96 %** of cases |
| `G4.12` | CE rise ≥ 0.15 **and** MI drop ≥ 0.10 | Its shuffle key omits `strat_econ_status`, so it changes **at most 1 of 6** prefix fields and for **55–64 %** of diaries changes **nothing at all** — yet is asked to move CE as much as a full permutation |

🔴 **`G4.12` was never put to the author and carries no decision ID.** It ships FAIL by inertia. That is
the one item in this group a reviewer could fairly call unfinished.

⚪ **`G4.6` has a live consequence nobody closed:** merged and unmerged adapters produce different
populations, and **no artefact in Steps 5–8 records which one produced it.**

### 3.4 The reference mechanism — `G8.7`, `G8.1`–`G8.4`

`FINDING 44` found that `G8.1`–`G8.4` had been given ASHRAE Guideline 14 tolerances **against no
reference series at all**, and that every candidate reference either did not exist or **inverted the
claim** — scoring against the flat 4.0 W/m² foil would make the gate pass exactly when the paper's own
claim succeeds. `D-S8-1` (a) re-cast all four as **reproducibility tripwires** against an independent
re-run; they now read exactly 0 and **prove nothing about accuracy**, which is written on the gate row
itself.

`G8.7` compares EnergyPlus hourly-dynamic output to TABULA's monthly quasi-steady-state `q_h_nd` —
**a model-to-model structural comparison, not a compliance test** — and is **permanently INFO with no
band that will ever be created**. Its underlying number is worth stating anyway because it is large and
country-correlated: **+136.6 % (es) / −29.6 % (uk) / −36.7 % (it)**, a 166-percentage-point spread whose
**sign flips by country and therefore aligns with the LOCO fold**. Spain's mechanism is measured: TABULA
counts gains over a **539-hour** heating season, EnergyPlus at 20 °C heats for **2,901 hours**.

---

## 4. WHAT THE PAPER MAY NOT SAY — the consolidated bar list

🔴 **These are not stylistic preferences. Each was written after a specific near-miss, and several were
written after the wrong sentence had already been drafted once.**

**On the model and the gates**
1. Never write Step 4 up as clean, or Step 5 as "5 of 5" / "36 of 36", or Step 3's battery as "20 of 20".
2. Never write *"the privacy audit passed"* or *"4 of 4"*.
3. Never report `G4.1` as improved by the backbone or by the ceiling — **only the verdict is comparable**;
   every difference measured is inside the seed floor.
4. Never say *"the full fine-tune reduced over-dispersion"* — forbidden by this project's own prior ruling.
5. Never call the memorisation-ceiling control fully unconditional — `P(body | country)` survives its
   permutation; only 5 of 6 prefix fields are de-associated.
6. Never present the backbone comparison as a scaling claim — **two points is not a curve**.
7. Never raise `--max-len` on one arm and still call two arms "the same recipe". The Llama arms carry
   **no measured truncation rate**; never write that the arms truncated equally.
8. Quote every `--selftest` result **with its `--n-diaries`** (`FINDING 153`).

**On energy numbers**
9. Every EUI in this project is **HEATING-ONLY** and may never be compared to a whole-building EUI or a
   measured total.
10. **No cross-fold comparison of absolute demand is safe to ±10 %** — the weather station alone is
    worth 5–11 % of heating demand, and its sign differs by fold.
11. **No artefact ever places an absolute Step 8 EUI beside an absolute Step 10 EUI** (`G10.12`). Only
    control-referenced relative deltas cross, computed inside each step's own basis, and even those are
    reported side by side, **never differenced**.
12. **Cell-level use of Step 10's certified 149 is BARRED everywhere** (`D-EU-31`), the `it` cell range
    45.08–156.70 is **WITHDRAWN**, and the `it` fold figure carries its tolerance or is not quoted:
    **108.25 kWh/m² ± 0.16 %**, the tolerance itself measured on **35 of the 74** cells. Write
    *numerically stable, not bitwise reproducible*, and **never** that 108.25 was re-measured.
13. Never quote Step 8's **pre-rotation** numbers. Read `Step8_docs/docs/2026-08-26_D-S9-3a_the-rotated-re-run.md`
    before quoting any Step 8 number at all.
14. The withdrawn line *"occupancy is 17–60× the convention's range"* must not be repeated — it now
    reads **9.4× / 0.2× / 22.6×**, and in Britain both quantities sit below the between-diary spread.
15. The published **15–50 %** occupancy band is **not the comparison this design supports** — switching
    the entire gain off is worth only +40.5 / +19.7 / +20.1 %.
16. Never quote `G8.7`'s 6.1 pp envelope headline without its class table — `it`/`AB` is still 0.656 and
    `uk`/`AB` **over**-states at 1.137.

**On stock-scale and per-dwelling claims**
17. **No per-dwelling prediction, at any scale** (`G11.13`, limitation E1). Scale raises confidence in
    the aggregate and does nothing for the individual household.
18. **No claim that Step 9's FAILs were a small-sample artefact.** Stock scale confirmed them.
19. An **Arm F** stock total is a **LOWER BOUND**, labelled as one, with **no numeric bias magnitude
    attached** — the magnitude is refused because the only available figures rest on a citation whose
    own CrossRef line returns a different paper.
20. **Arm D and Arm F never share a colour scale or a legend**, and Arm D is selected on footprint
    convexity, so **no stock-level EUI may be quoted from it**.
21. No cross-population R² comparison without the `G11.16` population declaration.
22. **No `G10N.x` result exists.** `C2` ran; `R8` still refuses `--scored`; Step 11 scored only its own
    `G11.x` board on those cells.

**On provenance and wording**
23. Never quote `RL27`'s variable names into the methods, the code or a data statement — the
    percentages are right to two decimals and **all three column names are wrong**.
24. Write UK fieldwork as *"April 2014 to December 2015 with an interruption"*, never "continuously"
    (September 2015 carries zero diaries).
25. Never write that the 3-digit corpus decision was vindicated — it buys exactly **one** published
    distinction (ACL 331 Laundry vs 332 Ironing). The corpus decision is justified on **microdata
    fidelity**.
26. Do not quote Step 2's superseded unknown-band shares (UK 6.3 % / IT 13.5 %) — the corrected figures
    are **ES 0.0000 / UK 0.5192 / IT 4.2435 %**. The wrong figures are deliberately left in older log
    entries as the audit trail that caught them.
27. **Verified reference ≠ verified content.** `FUENTES-2018` is CrossRef-verified; **nobody has read
    the paper**, and the 30–50 figure inside it is still unverified. The drafted passages say so.

---

## 5. THE LIMITATIONS, AS THEY NOW STAND

The governing table is `4thJ_00_HETUS_LLM_Pipeline_Overview.md` §limitations. **Three were REMOVED, not
answered** — and removing them is honest, because the claims they limited no longer exist.

| Code | Statement | State |
|---|---|---|
| A1 | Inherits the source surveys' coverage and non-response bias | active |
| A2 | 1–2 diary days per respondent; multi-day dependence largely unobservable | active |
| A3 | Hotel guests, institutions and homeless people are outside the frame | active |
| B1 | The pretrained model's world knowledge is **not uniform across countries** — pre-registered as a confound, **not resolved** | active, and load-bearing |
| B2 | Transfer is scored against aggregates only | active |
| ~~C1~~ | *"two waves is not a trend"* | **REMOVED** — no temporal claim exists any more |
| ~~C2~~ | Recent waves confound pandemic and mode change | **REMOVED** — those waves are not in the corpus |
| ~~C3~~ | Pooling waves teaches the instrument, not behaviour | **REMOVED** 2026-08-14 — one wave per country |
| C4 | **The corpus is three countries and LOCO trains on two** | active, rewritten by decision 16 |
| D1 | Constrained decoding renormalises over allowed tokens — not neutral | active, and **measured**: `G7.9` FAILs 3/3 at parity size |
| D2 | Post-hoc raking would fix margins but weaken the claim | resolved by rule: never rake our own output |
| E1 | The activity-to-load mapping is unvalidated **per dwelling** | active — **bounds every downstream energy claim** |
| E2 | Reproducibility is statistical, not bit-exact | active, and measured twice |
| F1 | Trained weights are not released | active — `RL10`, reinforced by `G6.10` |
| F2 | The European archetypes are **our own construction** from TABULA | active |
| F3 | Concordia is not a Eurostat-recognised research entity | active; enquiry sent 2026-08-26, no reply |

**Step-level limitations that are not in that table but belong in the paper:**
**E2-bis** — CREST's **UK-2000 appliance-ownership shares are applied unchanged to Spain and Italy.**
**A load that is only ever recorded as a secondary activity is invisible to the trigger, and the size of
that is unbounded** — no published measurement exists to bound it.
The **`it` fold is scored against a Eurostat aggregate from a different survey wave** (2008-09) than its
own microdata (2013-14) — so the LOCO result is **not basis-uniform across its folds**.
The UK's `strat_hh_type = unknown` cell (**551 diaries, 3.48 % of the fold**) is **un-quantifiable on
the model side**: 0 of every generated-diary count carries that value, because the census-marginal
population has no such category. Its measured cost is bounded: dropping it moves whole-fold MAE by
**+0.158 min/day**.
**One thermal zone per dwelling** — the model can say occupancy redistributes gains in **time**, never
**where** in the dwelling.
**Spain's synthetic population has no `homemaker` category at all**, because the Spanish census has none.
**`strat_day_type` has no published marginal in any country** and is assigned exogenously by calendar week.

---

## 6. THE HONEST GAPS — what was never scored, never ruled, or never read

🔴 **A reviewer will find these. Better that the paper names them first.**

1. **`G10N.x` was never scored.** Step 10's `C2` campaign ran to completion — **35,290 cells across
   three districts** — and its gate board was never executed, because `R8` refuses `--scored` and the
   author never lifted it. There is no `4thJ_gates_step10*.py`. **`Step10_docs/`'s own two documents
   still say "SPEC ONLY. NOTHING COMPUTED"** and were never revised; the board and `Step11_docs/` carry
   the correction.
2. **`D-S9-2` items 1–6, 8 and 9 are formally un-ruled.** All are implemented at their recommended
   option and none blocks anything, but the record's own "Author's ruling" block is still a blank
   template. Item 7 was ruled with `D-S11-1`.
3. **`G4.12` has no decision ID and was never adjudicated.**
4. **`G6.14` was never scored against generated model output.** The mechanism is built and self-tested
   9/9 and demonstrated failing correctly on a wall-clock-frame perturbation of real Italian diaries —
   but the transfer claim was never measured against it.
5. **`G4.11` FAILs on the shipped ceiling manifest, deliberately.** The manifest describes a LoRA run
   for a job whose log says *"FULL fine-tune, no adapter"* (`FINDING 157`). The manifest was **not
   edited** — a correction sidecar sits beside it, and **the methods must quote the sidecar**.
6. **Step 2's `--selftest` fixed-run result is reported in prose but not corroborated by a saved report
   on disk** — both on-disk selftest artefacts truncate at the pre-fix crash point.
7. **Step 1's M-8 strata re-run** has no artefact directory; reported-but-not-independently-verifiable.
8. **Fuentes et al. (2018) has never been read**, and it is the true source of a band this project
   scored against for weeks.
9. **Madrid's 840 failed cells / 84 buildings were left unrepaired by deliberate choice**, and Bologna's
   3 courtyard buildings (30 cells) are permanently un-simulable by this method.
10. **`G11.4` is NOT CHECKED offline** — 3 of 4 DOIs need network. Not a defect; it resolves online.

---

## 7. THE FIVE PROCESS LESSONS THIS PROJECT PAID FOR

Worth a short subsection in the paper, because they are transferable and each one cost a re-run.

1. **A gate scores a quantity AND detects a mutation — retiring the first silently retires the second.**
   `G9.7` → INFO left `scale_dhw_by_2` caught by nothing until `G9.15` was built.
2. **A crash is not a FAIL.** Step 2's `--selftest` raised `KeyError` and the battery reported *nothing*
   — not a partial result — so every perturbation after the crash point was unreachable.
3. **An empty population has not been satisfied; it has not been ASKED.** Several gates returned PASS on
   zero rows before being taught to return `NOT_EVALUABLE`.
4. **A re-run that reproduces the old answer exactly is evidence the fix did not reach the tool.**
   `FINDING 147`: the first rotated re-run came back bit-identical across 9,000 runs because a script
   bypassed the emitter.
5. **The check can be the artefact that is wrong.** `FINDING 151` (a ×10 multiplier that is inert
   against a zero denominator), `FINDING 154` (a first-check-wins histogram that reads like a diagnosis),
   `FINDING 126` (a parser blind to the only real object shape it would ever meet) — three times, the
   discriminating work was happening somewhere other than where the number implied.

---

## 8. WHAT THE MANUSCRIPT LOOKS LIKE FROM HERE — a reading, not a decision

⚪ **Offered as an analysis of what the evidence supports. The shape of the paper is the author's call.**

**The claim the evidence supports:** *one open-weight LLM, fine-tuned once on a harmonised three-country
HETUS corpus, generates activity-resolved diaries that carry country-specific structure all the way into
simulated building loads — and still does not beat a raked pool of real donor diaries at reproducing a
held-out country.* Both halves are measured, on a pre-registered bar, and neither was chosen after the
fact.

**Why that is publishable rather than a null to be buried:** the hard null was declared the objective
before training (author decision 4); the transfer framing was forced by `RL06` before any fold was run;
the corpus, the thresholds and the pre-registration were frozen (`prereg.md` md5 `e4243e07…`, verified
live at every closure); the failure is **uniform across nine fold-band cells and six independent gates**,
not marginal; and **capacity was eliminated as an explanation from three directions** — backbone size,
trainable-parameter count and a different backbone family.

**What the paper still has that is positive:** a six-hour cross-country spread in appliance peak
produced by nothing but the diary (§2.2); a dwelling-class ordering that survives a four-hour phase error
(§2.3); two clean nulls that are deliverables in their own right (chaining convention, annual heating
channel); and a validation apparatus — 200-plus gates, mutation batteries with coverage clauses, and
gates **seen failing** before being trusted — that is itself a contribution to how this kind of work
gets checked.

**What needs the author before drafting starts** — four items only, listed in §9.

---

## 9. OPEN QUESTIONS FOR THE AUTHOR, BEFORE ANY MANUSCRIPT TEXT

1. **Is `C2` reported at all?** It ran to completion (35,290 cells) and has never been scored, because
   `R8` refuses `--scored`. Either it is lifted and the `G10N.x` board is run, or `C2` is described as a
   compute campaign whose gate board was deliberately not read. **Both are defensible; they are different
   papers' worth of Step 10.**
2. **Does `D-S9-2`'s blank ruling block get filled?** Eight items are implemented at their recommended
   option and formally un-ruled. Filling it costs one line and removes a reviewer's easiest question.
3. **Target venue.** It decides length, whether the validation apparatus gets its own section, and
   whether the negative result leads the abstract.
4. **Does anyone read Fuentes et al. (2018)?** It is the real source of the 30–50 L band. The drafted
   limitation currently says outright that nobody has read it.

---

## 10. `FINDING 275` — THE STEERING ARM WAS NEVER MEASURED ON THE REPORTED MODEL (added 2026-09-13, last+267)

🔴 **Found while drafting the manuscript, from the Step 6 document itself. The sentence this project
quotes most — *"the model steers correctly and delivers about half the amplitude"* — is HALF measured on
the model the paper reports.**

`G6.7` splits under `D-S6-13` into a **STEERING** arm (R² ≥ 0.80 on `AC2`) and an **AMPLITUDE** arm
(pooled slope ≥ 0.80 over five channels, `AC4-8` excluded by name).

* The split values this project quotes — **steering R² 0.8455 / 0.9808 / 0.9836**, **amplitude pooled
  slope 0.2666 / 0.4612 / 0.3785** — are dated 2026-08-22 on the **Leg-4** artefacts, i.e. the **1.48 B
  pilot** (`4thJ_06_transfer.md:2330-2333`, `:2523-2541`).
* The **Leg-5** (reported 7 B) section carries **only** a slope column headed *"slope (need ≥ 0.80)"* at
  **0.4153 / 0.5329 / 0.4049** (`:2989-2993`). **No Leg-5 steering R² exists anywhere in `Step6_docs`** —
  a full-text search finds every occurrence inside the Leg-4 entry and none in the Leg-5 section.
* ⚪ **Second, smaller discrepancy in the same place:** the Leg-5 slope printed against the ≥ 0.80 bar is
  the **six-channel pre-split** figure. `D-S6-13`'s ruled definition is **five channels**. The ruled
  definition was never applied to Leg-5, and the stored `g67_leg5_*.json` does not say which set it used.

**Consequences, all of them handled in the manuscript rather than left open:**

1. 🔴 The abstract, the highlights, §1.5, §5.4, §6.2 and §7.10 of `writing/submission/4J_manuscript_submission.md`
   now state the amplitude result as **measured on the reported model** and the steering result as
   **inherited from the pilot arm**. Both readings of the slope are printed in §5.4.
2. ⚪ **The fix is one generation run** against an existing control, and it is named in §7.10 as unfinished
   rather than assumed. If it is run, the steering arm must be scored under the **five-channel** definition
   and the amplitude arm re-printed under the same definition, so the two stop disagreeing.
3. 🔴 **Until then, nobody may write *"the model steers correctly and delivers half the amplitude"*
   about the 7 B model without the qualifier.** The 1.48 B pilot supports it. The reported model supports
   only the second half.

⚪ This is the `feedback_verify_progress_log_claims` rule paying for itself: the number was correct, the
document was correct, and the **attribution** of the number to the reported model was made in summary and
never checked against the leg it came from.

---

## PROVENANCE

Assembled 2026-09-13 from four independent read-only harvests of the step documents and their artefacts
(Steps 0–3, 4–6, 7–9, Step 10 + the two parent plan files), reconciled against
`Prompts/RESUME.md` and `4thJ_CHECKLIST.html`. Numbers carrying an artefact citation in the source
harvests were spot-checked against the underlying `.json`/`.txt`/`.csv` by those passes; §6 lists the
four places where a prose claim has **no** corroborating artefact on disk. 🔴 **Before any figure in
this document reaches the manuscript, re-derive it from the artefact the step document names** — this
project's own standing rule, and the one that caught `FINDING 149`, `FINDING 151` and the `D-S2-20`
errata.
