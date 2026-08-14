# Step 2 — Harmonisation. Validation.

### 4J HETUS LLM pipeline. Validation specification.
#### Implementation: `4thJ_02_harmonisation.md`. Parent: `../4thJ_00_HETUS_LLM_Pipeline.md`

---

## STATUS

**OPEN. Nothing built, no gate run, none seen failing.** All thresholds pre-registered.

---

## WHAT THIS STEP MUST PROVE

That four national files now speak one language **without the harmonisation having invented the
agreement**.

That distinction is the whole risk of this step. A crosswalk that maps every ambiguous national code
to the nearest target code will produce four beautifully agreeing distributions and will have
manufactured the paper's premise.

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
| **G2.8** Co-presence missingness | Missing collapsed into absent | For every country × flag, the value is one of {recorded, not recorded}, and no flag that `copresence_availability.md` calls "not recorded" contains a 0 in the data | **project-chosen** |
| **G2.9** Cross-country activity divergence | 🔴 **Over-harmonisation** — the mapping erasing real national difference | Level-1 time budgets must **still differ** between countries after harmonisation. Pre-registered: the maximum pairwise difference across the four countries, on at least **3 of the 10** Level-1 categories, must exceed **20 min/day**. If harmonisation makes four European countries look identical, it has smoothed them together | **project-chosen**, and it is deliberately a *floor* on disagreement |
| **G2.10** Against published aggregates | The mapping being internally consistent but wrong | Harmonised Level-1 time budgets within **±10 min/day** of each country's **own published** time-use tables for that wave | **project-chosen** tolerance; the reference is external |

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
| Drop all French respondents aged 11-14 | G2.7 (attrition trigger) | G2.4 |
| Write 0 into a flag declared "not recorded" | G2.8 | all others |
| 🔴 **Map every country's activity codes to the pooled modal code** | **G2.9** | G2.3, G2.4 — *time is conserved and days still close, which is exactly why G2.9 has to exist* |
| Shift one country's sleep budget by 40 min/day | G2.10 | G2.9 |
| 🔴 **Null perturbation: change nothing** | **nothing** | everything |

### Coverage clause

Cross-tab every perturbation against baseline. **The probe FAILs if any gate that passes on the real
data was never made to fall.** A perturbation set that only tests the gate it was named for will
print a complete-looking tally while a headline gate has never been exercised.

---

## VACUITY GUARDS

* **V2.a** — the runner FAILs if it harmonised fewer than **4** countries.
* **V2.b** — it prints, before any verdict, the number of source codes, mapped codes, unmapped codes
  and one-to-many rows it saw.
* **V2.c** — any national code, unit or field name not present in `codebook_facts_<country>.md` is
  **printed and refused**, never assumed harmless.
* **V2.d** — G2.6 is itself a vacuity guard; it must be run against the shipped exclusion list, not a
  copy inside the validator. 🔴 A second copy of a list drifts invisibly from the first — import it,
  never duplicate it.

---

## WHAT THIS STEP'S VALIDATION DOES **NOT** COVER

* It does not verify that HETUS harmonisation is *meaningful*, only that we applied it consistently.
  Whether two countries coding "eating" the same way actually observed the same behaviour is the
  paper's research question, not a gate.
* It does not test the indoor rule's **correctness**, only that it fires. Whether the exclusion list
  is the right list is a judgement against the ACL, made by a human, and recorded in the methods.
* 🔴 It does not cover **secondary activities**. HETUS records them; our episode tuple does not carry
  them. That is a scope decision inherited from Step 3, and if a later step needs them this step is
  where they were dropped.

---

## PROGRESS LOG

Append-only.

### 2026-08-14 — validation document created

* Ten gates, eleven perturbations, none run.
* 🔴 G2.9 is the gate this project would most easily have shipped without. Every other gate here asks
  *did we get it right*; G2.9 is the only one that asks *did we get it right without making it up*.
  It is written as a floor on disagreement precisely because the failure it catches looks like
  success in every other measurement.
