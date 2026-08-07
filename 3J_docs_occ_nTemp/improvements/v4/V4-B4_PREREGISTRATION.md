# V4-B4 — the 2J manuscript's own EUI table, pre-registration

**Written 2026-08-06, before a single corrected number was read.** Opened because the user stated the
2J paper is **not submitted** (my record said it was — corrected) and pointed at three files that may
be changed: `writing/fullSet/2J_full_manuscript.md`, `writing/fullSet/readySubmission.md`, and
`writing/sharingCHV/2ndOcc_Journal.docx`.

---

## 0. Why this is a new item and not part of V4-B2

`V4-B2` corrected **Leg-2's Step-9 table** (`3J_docs_occ_nTemp/Leg2_2-split/Step9_docs/`):
211.7 / 177.5 / 140.0 / 143.0 kWh/m².

The **2J manuscript's Table 5** carries **different numbers** — 208.13 / 151.79 / 127.80 / 117.01 —
from a **different campaign** (`Step-8 v2 corrected`, jobs `953111` + `954135` + `8G`, verified
2026-06-10). 🔴 **Applying B2's correction factors to these numbers would be exactly the error
`V4-A1` made**: reasoning about one artefact from another artefact's figures. They are re-derived
from this campaign's own outputs or not at all.

---

## 1. What is established before any prediction

**The code path is the same, verified by reading it, not assumed.**
`Step8_docs/step8_aggval_v2.sh` runs `08_simulation_plots.py --rebuild-agg` against
`SimResults_Step8_corrected_v2/campaign_N50`; `08_simulation_plots.py:270` calls
`_plotting.calculate_eui(conn)` and assigns the result to `annual["eui_kWh_m2"]` (`:364-366`).
The engine is `Step8_docs/eSim_bem_utils_2J/plotting.py`, whose `calculate_eui()` carries **both**
defects at the same lines as the Leg-2 copy:

| | line | what it does | consequence |
|---|---|---|---|
| defect 1 | `:293-299` | queries `TabularDataWithStrings` for `End Uses By Subcategory` with **no `ReportName` filter** | the **peak-demand** copy of the table is summed into the annual total; `W` hits the `else: val_kwh = val` branch at `:343-345` and a watt is added as a kilowatt-hour |
| defect 2 | `:319` | `if 'm3' in str(units): continue` | **SI-only** water guard; an IP run's `gal` is not skipped and is summed as kWh |

**The published values are reproduced from the published aggregate**, not quoted: the plain mean of
`eui_kWh_m2` over each archetype's 1500 rows in `outputs_step8/agg/agg_annual.csv` gives
**SingleD 208.13 · MidRise 151.79 · OtherDwelling 127.79 · HighRise 117.01** — Table 5 exactly.

**The read path is validated before it is used.** `eplusout.sql` is 43 MB per run; `eplustbl.csv` is
1.75 MB and carries the same tabular reports. One probe run
(`HighRise__Calgary_6B/sample_001_HH115612/2022`, published `eui_kWh_m2` = 121.367) was fetched and
the shipped logic re-implemented against the CSV: **121.3667, diff 0.0003.** The CSV is a faithful
proxy. **If any sampled run fails the same ±0.01 reproduction guard, that run is reported, not
dropped.**

---

## 2. Sample, fixed now

- **100 runs per archetype, 400 total**, taken **systematically** — every 15th row of each
  archetype's 1500 rows after sorting by `(arch, city, year, sample)`. Deterministic, no RNG, and it
  spreads across all 6 cities and all 5 years by construction.
- Population is 1500 per archetype; the published figure is a **plain mean**, so the sample estimate
  is a mean with a t-interval, not a median with order statistics (that was B2's shape, and it does
  not transfer).

---

## 3. Predictions — written before the fetch

| ID | prediction | falsifier |
|---|---|---|
| **Q1** | All four archetype means **fall**. Both defects can only add energy. | any archetype's corrected mean ≥ its published mean |
| **Q2** | **SingleD's corrected mean lands below 186.1** — the SHEU upper bound it is currently reported as exceeding by ≈12 %. The manuscript's "**No — above upper (≈ +12%)**" verdict **does not survive**. | corrected SingleD ≥ 186.1 |
| **Q3** | **At least one archetype now reported "Yes — within band" moves below its lower bound.** | all of MidRise/HighRise stay inside their bands |
| **Q4** | **The unit system is uniform across the sample — every run SI** — so **exactly one** defect (the demand double-count) operates and the water guard never misfires. This is the claim B2's convenience sample could not make. | any sampled run reporting `gal`, `gal/min`, `kBtu` or `kBtuh` |
| **Q5** | The correction factor is **not a single constant**; its spread across runs exceeds **5 %**. Restating B2's refutation of uniformity on an independent campaign. | max/min factor < 1.05 |

🔴 **Q2 is the load-bearing one.** If it holds, §5.2's central defence — three paragraphs arguing the
over-band reading is "genuine, heating-driven elevation rather than a denominator mismatch" — is
**defending an artefact**. That paragraph goes, whatever else happens.

🔴 **Stated in advance, so it cannot be chosen afterwards:** a correction that moves an archetype from
"outside the band" to "inside the band" is **not** a result to be pleased about. Q3 exists precisely
because the honest outcome may be that a currently-passing archetype now fails. **No band value in
Table 5 moves.** The SHEU bands are sourced (Tables 3.3a/3.3b) and stay byte-identical; only the
simulated column changes.

---

## 4. What this item does not do

- It does not touch `Leg2_2-split/` or any Step-9 artefact — `V4-B2` owns those and is closed.
- It does not re-run a single EnergyPlus cell. **Retrieval only**, under the amended Speed rule.
- It does not decide the manuscript's fate. The user has said the paper is not submitted and may be
  changed; **what changes in the three writing files is applied only after the numbers are in.**
