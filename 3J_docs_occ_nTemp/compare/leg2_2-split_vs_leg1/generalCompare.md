# General comparison — J2 (single-channel) vs J3 Leg-2 (two-channel): are the FAILs a problem?

**Purpose:** hold the headline scorecard table, then honestly anatomize every remaining FAIL so we
know exactly what each one is, whether it is a *real* problem, and whether it touches the BEM
deliverable. Companion to the per-step files (`Step4_compare.md` … `Step7_compare.md`) and `README.md`.

---

## Validation, side by side

```
┌────────────┬───────────────────────────┬───────────────────────────────────────────────┐
│    Step    │            J2             │                   J3 Leg-2                    │
├────────────┼───────────────────────────┼───────────────────────────────────────────────┤
│ 4 Augment  │ 21P/1W/0 hard-FAIL        │ 68P/1W/2FAIL (structural + unobservable)      │
├────────────┼───────────────────────────┼───────────────────────────────────────────────┤
│ 5 Linkage  │ 30P/0W/4FAIL              │ 20P/1W/3FAIL (all inherited from Step-4 lock) │
├────────────┼───────────────────────────┼───────────────────────────────────────────────┤
│ 6 Forecast │ 35/35 PASS                │ "HEALTHY" sign-off                            │
├────────────┼───────────────────────────┼───────────────────────────────────────────────┤
│ 7 BEM      │ 2022 29/0/0 · 2030 28/0/0 │ 2022 32/0/0 · 2030 43/0/0                     │
└────────────┴───────────────────────────┴───────────────────────────────────────────────┘
```

Same table, markdown:

| Step | J2 | J3 Leg-2 |
|---|---|---|
| 4 Augment | 21P / 1W / **0 hard-FAIL** | 68P / 1W / **2 FAIL** (structural + unobservable) |
| 5 Linkage | 30P / 0W / **4 FAIL** | 20P / 1W / **3 FAIL** (all inherited from Step-4 lock) |
| 6 Forecast | **35 / 35 PASS** | **"HEALTHY"** sign-off |
| 7 BEM | 2022 29/0/0 · 2030 28/0/0 | 2022 **32/0/0** · 2030 **43/0/0** |

---

## First, read the table correctly

A "FAIL" here does **not** mean "broken output." It means a metric crossed a **deliberately tight
gate** (most are ≤3 pp per-slot). The gates are strict on purpose so nothing slips through. So before
panicking, two things to internalize:

1. **J2's clean-looking columns are partly an illusion of weaker measurement.** J3 caught and fixed
   two validator bugs that were hiding real conditions in J2:
   - **Night-window bug.** J2 evaluated its overnight AT_HOME / sleep gates on slots 1–8 = **04:00–08:00**
     (the morning ramp), not 00:00–04:00. Two of J2's Step-5 "FAILs" (night sleep 67.46 %, night
     AT_HOME 83.18 %) are *artifacts of the wrong window* — on the correct window the same data passes
     at 91–94 %. J3 measures the right window.
   - **Swapped Work/Sleep activity codes** in J2's Step-4 validator confounded its work-peak gate, so
     J2's "work proxy 3.27 pp" was partly a code bug. J3's 10.33 pp is an *honest* measurement of the
     same model family.
2. **J3 simply runs far more gates and has a second channel that can fail.** Step-4: 71 checks (J3) vs
   21 (J2). J3 added OW1–OW6 (office) and W1–W4 (linkage work channel). More gates + a brand-new
   AT_WORK channel = more *opportunities* to trip a threshold, not worse fidelity per gate.

So "J3 has more FAILs" is mostly "J3 measures more things, more honestly." That should make you *more*
comfortable with J3, not less.

---

## Every remaining J3 FAIL, anatomized

| # | Step / gate | What it measures | Number (gate) | Root cause | Real problem? | Touches the BEM deliverable? |
|---|---|---|---|---|---|---|
| 1 | **S4 · G4** work-peak | `act30` activity-code work share at peak hours | 10.33 pp (≤3) | Locked Step-4 model's **activity head** under-produces "work" at peak. 04N filler hit a 0.1 pp structural floor (exact-marginal rake won't relocate enough mass). | Known model limitation, documented. **The AT_WORK *location* marginal is exact (0.03 pp)** — only the activity *label* channel is short. | **No** — office BEM uses the AT_WORK presence fraction (exact), not the act30 work label. |
| 2 | **S4 · OW5** day-type ordering | % respondents with WD ≥ Sat ≥ Sun office attendance | 63 % (≥90 %) | **Unobservable by construction**: GSS gives 1 diary day per person, so there is no ground truth for per-person WD/Sat/Sun ordering. Can't be raised without *inventing* an ordering assumption. | **No** — it's a data limitation, not a model defect. | No. |
| 3 | **S5 · 2.2** AT_HOME per-slot | worst single-slot AT_HOME deviation | 8.59 pp (≤3) | **= FAIL #1 re-measured downstream.** Same Step-4 work-mass gap → AT_HOME deficit in daytime slots. | Same as #1. Grand-mean AT_HOME is only 0.65–2.46 pp; this is one worst slot. | Residential BEM keys off `hom30` per-HH; aggregate fidelity is fine. Worst-slot only. |
| 4 | **S5 · W1** AT_WORK per-slot | worst single-slot AT_WORK deviation | 10.18 pp (≤3) | **= FAIL #1's twin** (same Step-4 origin, work side). | Same root. | Office BEM uses the *calibrated/raked* presence profile; the raw worst-slot gap is pre-calibration. |
| 5 | **S5 · W3** colleagues | colleagues co-presence vs observed | 4.37 pp (≤3) | Step-4 synthetic pool colleagues mean (~12.4 %) is thinner than observed (~21.2 %). **Rung-I hot-deck built to fix it; full production re-run still pending.** | Partly **open** — the only FAIL with an unfinished remedy. | Colleagues is not a BEM schedule input; informational for occupancy profiling. |
| 6 | **S6** weekday biz-hours home | weekday daytime home under-prediction | ~14 pp MAD (gate 0.10) | **Inherited from the locked Step-4 base** (same work-over / home-under tilt). Accepted residual in the "HEALTHY" sign-off; not gamed. | Same root as #1/#3. | Corrected by Step-6/7 calibration before BEM; the delivered schedules pass Step-7 gates. |

### Plain-language walkthrough — the two Step-4 fails (for non-specialist readers)

The model fills in each person's day in **two separate notebooks**, half-hour by half-hour:

- **Notebook A — Location:** "Are you physically at the office right now? yes/no" (this is `wrk30` /
  AT_WORK).
- **Notebook B — Activity:** one word for what you're doing — sleeping, eating, commuting,
  **working**, … (this is `act30`, a 14-code label).

Different parts of the model write these. A calibration/raking step forces **Notebook A** to match
real Canada *exactly*. Notebook B is not forced that hard.

**FAIL 1 — "G4 work-peak, 10.33 pp."** At the busiest hour, real GSS people write "working" in
**Notebook B** about **29 %** of the time; the model's synthetic people write it about **18 %** of the
time. That ~10-point shortfall trips the gate (it wants ≤3 pp). Why it isn't alarming:
- The **office energy schedule is built from Notebook A** (who is physically in the office), and
  Notebook A is exact (AT_WORK marginal 0.03 pp). The failing number lives in **Notebook B, which the
  office model never reads.**
- We tried a post-processing "filler" (stage 04N) to push more work into the peak in Notebook B. It
  moved the gap only **0.1 pp**, because the calibration enforces exact daily totals — to add work at
  the peak you must remove it somewhere else, and the constraints leave no room. So it is a
  **structural floor**, not a knob we forgot to turn.

**FAIL 2 — "OW5 day-type ordering, 63 %."** This gate asks: "for ≥90 % of people, is office attendance
Weekday ≥ Saturday ≥ Sunday?" Sounds obvious. The catch: **GSS surveys each person on only ONE day.**
We never observe the *same* person on a weekday *and* a Saturday *and* a Sunday — the model imagines
the other two days, so there is **no ground truth to grade against.** The 63 % just reflects the
model's imagined days; the only way to force it to 90 % is to hard-code "everyone works less on
weekends," which is **fabricating an assumption, not modeling.** So it is a **data limitation, not a
model error.**

**One line:** one fail is in a channel the BEM ignores (and is structurally stuck); the other can't
even be measured with one-day-per-person data. Neither corrupts the schedules going into Step 5/7/8.

### Plain-language walkthrough — the Step-5 linkage fails

**What Step 5 does:** it takes the synthetic diary *pool* from Step 4 and **attaches a matching diary
to every real Census person**, so each Census household gets an occupancy schedule. Crucially, **Step 5
invents no new behavior** — it copies Step-4 diaries onto Census people. So any imperfection from
Step 4 rides along, and the Step-5 validator simply re-measures home/work fidelity on the linked
population.

That's why the **3 J3 Step-5 fails are not new problems — they are the Step-4 fails seen again at a new
station:**

- **AT_HOME worst-slot 8.59 pp** and **AT_WORK worst-slot 10.18 pp** (gate ≤3 pp) = the **same
  Step-4 work-peak gap** ("Notebook B", above), re-measured on the linked people. These are *worst
  single half-hour* numbers; the all-day average home match is only ~2 pp. Step 5 *cannot* fix them
  because Step 4 is locked — it would have to rewrite the very diaries it is only supposed to copy.
- **Colleagues 4.37 pp** = the Step-4 synthetic pool has thinner "had colleagues around" rates
  (~12 %) than real life (~21 %). A targeted fix (the **Rung-I hot-deck**) is **built and smoke-tested
  but not yet production-run** — this is the one genuinely open Step-5 item. Colleagues is **not a BEM
  schedule input**, so it does not block Step 7/8.

**About "J2 had 4, J3 has 3":** J2's 4 included **two that were a validator bug**, not real failures —
J2 measured the overnight sleep/home gates on the *wrong hours* (slots 04:00–08:00 instead of
midnight–04:00), and one check was double-counted across two report sections. J3 fixed the window bug;
on the correct overnight window the same data passes at **91–94 %**. So J3's lower count is *honest,
not luck*. J3's 3 are: the two inherited Step-4 worst-slot gaps + the open colleagues item.

**Net:** Step 5 adds no new modeling error. Two fails are Step-4 re-measured (locked; in channels whose
aggregate marginals the linkage handles fine), and one (colleagues) has a built-but-unrun fix and is
not a BEM input.

### The thing that should settle it: they collapse to one root cause

Of the **6** remaining J3 FAILs/residuals:

- **#1, #3, #4, #6 are the same single fact** — the *locked* Step-4 generative model produces a bit
  too much "work" and too little "home" at peak weekday hours. Steps 5 and 6 just **re-measure that
  one Step-4 output at different stations**, so the same gap shows up 4 times. It is not 4 independent
  problems; it is one known model property, counted 4×.
- **#2 (OW5)** is **unobservable** — it cannot be passed without fabricating an assumption GSS data
  can't support. It is a data-limitation footnote, not a defect.
- **#5 (W3 colleagues)** is the **only genuinely open item** with an unfinished remedy (Rung-I
  hot-deck built, production re-run pending) — and colleagues is not even a BEM schedule input.

And critically — **the gates the BEM end-product actually depends on all PASS:**

- AT_WORK presence marginal (OW1): **0.03 pp — exact**
- Channel exclusivity hom30⊕wrk30 (OW6): **0 cells**
- Peak-timing shift (OW3): **0 slots**; night near-zero (OW4): **PASS**
- **Step 7 (the BEM deliverable itself): 0 FAIL both years** — 2022 32/0/0, 2030 43/0/0, including
  occupancy fidelity, weekend-marginal preservation, and WFH band ordering on both channels.

So the failures live on **tight per-slot worst-case deviations of an under-resourced channel**, while
the **aggregate marginals BEM consumes are clean**, and the **final BEM schedules pass everything**.

---

## Honest bottom line (the part that isn't just reassurance)

What is genuinely true and belongs in the paper's limitations:

1. The Step-4 model has a **real, modest work-peak / home-trough bias** (the locked base). It is the
   single source of FAILs #1, #3, #4, #6. We chose to **lock Step-4** and correct downstream by
   calibration rather than chase it in the model — that is a defensible, documented decision, and the
   *delivered* Step-7 schedules pass clean. State it as a known floor.
2. **W3 colleagues is the one loose end.** Rung-I is built but not production-run. Either finish the
   re-run before submission or document colleagues as an inherited Step-4 channel limitation. It does
   **not** block Step 8 (not a BEM input).
3. **Scale framing**: J3 links ~30 K persons (Census 2025, employed-enriched) vs J2's ~286 K
   (Census 2021). Different vintage/extraction — needs an explicit methods note so reviewers don't
   read it as lost coverage.

Everything else in the table is either a J2 measurement artifact that J3 fixed, an unobservable gate,
or the same one model property re-counted downstream.

**Verdict:** the FAILs are understood, mostly one root cause, and none of them corrupt the BEM
schedules that go into Step 8. Comfortable to proceed; carry items 1–3 into the paper's limitations.
