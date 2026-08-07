# V4-B4 — results: the 2J manuscript's EUI table, recomputed for every published run

**2026-08-06.** Companion to `V4-B4_PREREGISTRATION.md`. Read that first — the predictions below were
written before a single corrected number existed, and **one of them failed.**

---

## 0. What changed about the method, and why it is an improvement

The pre-registration planned a **400-run sample fetched from Speed**, because the raw outputs were
assumed to be cluster-only. **They are not.** All 6,000 run directories of the current aggregate are
on this machine (`BEM_Setup/SimResults_Step8/campaign_N50/`, 8,384 `eplustbl.csv` present).

So the sample was replaced by a **census: 6,000 of 6,000 published runs recomputed.** No estimator, no
confidence interval, no sampling caveat. The pre-registered predictions were not touched — a census
can only test them harder.

The 400-run Speed fetch **ran anyway and is retained** as an independent cross-campaign check
(§5). 399/400 arrived; one `scp` returned rc=255.

---

## 1. Three guards, all passed, before any corrected number was read

1. **The published table is reproduced, not quoted.** The plain mean of `eui_kWh_m2` over each
   archetype's 1,500 rows reproduces `readySubmission.md`'s Table 5 to the rounding shown
   (2022: 200.0 / 169.6 / 114.9 / 127.8 → 200 / 170 / 115 / 128).
2. **Every run's shipped value is reproduced from its own file.** `abs(shipped − published) < 0.01`
   for **6,000 of 6,000**. Zero guard failures, zero missing files.
3. 🔴 **The corrected definition is checked against a path the defect cannot touch.** Everything above
   is measured on the *same* tabular table the defect lives in, so agreement there proves only that I
   parsed it the way the shipped code did. The corrected **electricity** total was therefore compared
   against `elec_facility_kWh`, which `08_simulation_plots.py` builds by summing the **hourly meter
   stream** (J/h) — a separate EnergyPlus output that no version of `calculate_eui()` reads.
   **400 runs, 200 SI and 200 IP, all five years: max disagreement 0.067 %**, and the 0.0667 %
   constant on the IP side is the `kBtu→kWh` constant's own rounding. **The corrected numbers survive
   an independent path.**

---

## 2. The pre-registered predictions

| ID | prediction | verdict |
|---|---|---|
| **Q1** | all four archetype means fall | ✅ **PASS** |
| **Q2** | SingleD's corrected mean lands below 186.1; the "≈+12 % above upper" verdict does not survive | ✅ **PASS** — 115.00 (2022). It does not merely clear the upper bound, it lands below the **lower** one |
| **Q3** | at least one archetype now reported "within band" moves below its lower bound | ✅ **PASS** — **both** MidRise and HighRise do |
| **Q4** | the campaign is uniformly SI, so exactly one defect operates | ❌ 🔴 **FAILED** — **3,000 SI / 3,000 IP**, split cleanly **by archetype** |
| **Q5** | the correction factor is not a constant; spread > 5 % | ✅ **PASS** — 1.0572 to 2.0461, **93.5 %** |

🔴 **Q4 is the one that taught something.** I predicted uniformity and got an exact 50/50:

| archetype | units reported | runs |
|---|---|---|
| `SingleD`, `OtherDwelling` | `gal`, `gal/min`, `kBtu`, `kBtuh` — **IP** | 1,500 each |
| `MidRise`, `HighRise` | `GJ`, `m3`, `W`, `m3/s` — **SI** | 1,500 each |

The split is **not** by year (600/600 in each of the five) and **not** by city (500/500 in each of the
six). It is by **archetype**, i.e. by which IDF the run started from. A prediction that the campaign
was "uniform" was a prediction about a property nobody had ever checked.

---

## 3. The mechanism — and it is not the one B2 would have predicted

`published = corrected + d1 + d2`, decomposed for every run. **Reconstruction error, maximum over
6,000 runs: 0.0005 kWh/m².** The identity is exact, not fitted.

| archetype | published | corrected | `d1` demand-block | `d2` water-as-energy | `d1` % | `d2` % |
|---|--:|--:|--:|--:|--:|--:|
| `SingleD` | 200.40 | **118.44** | 0.24 | 81.72 | 0.1 % | **40.8 %** |
| `OtherDwelling` | 121.00 | **106.70** | 0.20 | 14.10 | 0.2 % | 11.7 % |
| `MidRise` | 158.75 | **104.68** | 54.07 | 0.00 | **34.1 %** | 0.0 % |
| `HighRise` | 120.69 | **75.95** | 44.73 | 0.00 | **37.1 %** | 0.0 % |

**Why the unit system decides which defect bites** — the missing piece, and it is about *magnitude*,
not about which branch the code takes:

- The peak-demand table reports power. **SI reports it in `W`** — for a 7,060 m² tower that is
  ~150,000, and adding 150,000 "kWh" to an annual total is a third of the answer.
  **IP reports the same quantity in `kBtuh`**, ~3.4× smaller, and a house's peak is ~34 kBtuh against
  a 221 m² denominator: **0.24 kWh/m², i.e. nothing.**
- The water guard is `if 'm3' in str(units)`. **SI water is `m3` and is correctly dropped —
  `d2` is exactly 0.00.** **IP water is `gal`**, a number in the tens of thousands, and it is summed
  as kWh.

So the two defects are **complementary in effect, not in presence**: each run carries both, and in
each run the unit system makes one of them negligible and the other decisive.

⚖️ **This refines a `V4-B2` sentence rather than overturning it.** B2 said *"every run has exactly one
of the two defects, decided by SI-vs-IP."* On SI runs that is **exactly true** (`d2` = 0.00). On IP
runs both are present and `d1` is 0.1–0.2 %. **The claim should have been "one of the two dominates".**
Recorded here rather than quietly reworded there.

**Independent corroboration:** `SingleD`'s water share is **40.8 %** here and was **38 %** in Leg-2's
entirely separate campaign. Two campaigns, two codebases' copies of the same function, same mechanism.

---

## 4. The corrected table

Bands are **NRCan SHEU-2019 Tables 3.3a/3.3b and do not move.** Only the simulated column changes.

### 4.1 `readySubmission.md` Table 5 — the live submission copy

| archetype | band | 2022 pub → **corr** | 2022 verdict | 2030 pub → **corr** | 2030 verdict |
|---|---|--:|---|--:|---|
| `SingleDetached` | 130.6 – 186.1 | 200.0 → **115.00** | **No — above upper (+7 %)** → 🔴 **No — BELOW lower** | 204.5 → **116.25** | **No — above upper (+10 %)** → 🔴 **No — BELOW lower** |
| `OtherDwelling` | 136.1 – 186.1 | 114.9 → **99.99** | No — below lower (16 %) → **No — below lower (27 %)** | 116.3 → **100.80** | below → **further below** |
| `MidRise` | 111.1 – 216.7 | 169.6 → **107.74** | Yes → 🔴 **No — BELOW lower** | 164.4 → **107.73** | Yes → 🔴 **No — BELOW lower** |
| `HighRise` | 113.9 – 147.2 | 127.8 → **78.21** | Yes → 🔴 **No — BELOW lower** | 125.9 → **78.59** | Yes → 🔴 **No — BELOW lower** |

**With the paper's own ×1.11 per-dwelling-unit renormalisation** (apartments only): MidRise 2022
**119.59 → back INSIDE** its band; HighRise **86.81 → still below**. The manuscript's sentence that the
renormalisation "places both apartment archetypes inside their SHEU ranges in both years" **is now
true of one of the two.**

### 4.2 Pooled five-year means

| archetype | published | **corrected** | verdict |
|---|--:|--:|---|
| `SingleD` | 200.40 | **118.44** | BELOW |
| `OtherDwelling` | 121.00 | **106.70** | BELOW |
| `MidRise` | 158.75 | **104.68** | BELOW |
| `HighRise` | 120.69 | **75.95** | BELOW |

🔴 **All four archetypes fall below their SHEU regional-average ranges once corrected.** The published
table reported one above, one below and two inside. **Three of the four band verdicts change, and the
two that read "Yes" are among them.**

---

## 5. 🔴 A second, independent defect in the writing set: `2J_full_manuscript.md` is on a superseded campaign

Found while tracing, not looked for. The two writing files **disagree with each other**, and the
disagreement is not the correction:

| file | Table 5 | reproduces from |
|---|---|---|
| `readySubmission.md` | two-panel, 2022 **and** 2030 (200 / 170 / 115 / 128) | `2J_docs_occ_nTemp/outputs_step8/agg/` — the **current** aggregate, with 2022+2030 from the 2026-07-11 local re-sim |
| `2J_full_manuscript.md` | single column (208 / 152 / 128 / 117) | Speed's `SimResults_Step8_corrected_v2/` — the campaign the two-panel fix **superseded** |

Both files carry the same mtime (Aug 4 17:55), so the staleness is invisible from the filesystem. It
was found by reproducing each table from its own data. **The full manuscript is wrong on two counts —
the wrong campaign and the defect — and the campaign error was not on anyone's list.**

The 399-run Speed fetch confirms the superseded campaign is contaminated the same way (SingleD
206.90 → 122.50, HighRise 116.92 → 75.53), so **no conclusion depends on which campaign is used. The
verdicts change either way.**

---

## 6. What I have NOT done, and why

🔴 **I have not written a new scientific interpretation into the paper.** §5.2 currently spends three
paragraphs defending the single-detached over-band reading as "a genuine, heating-driven elevation
rather than a denominator mismatch". **That defence is now defending an artefact and has to go.**
What replaces it — the obvious candidate being that a model built on a NECB-2017 / NBC-9.36 envelope
should sit *below* survey averages drawn from the existing stock — is **an authorial claim, not a
measurement**, and it is the user's to make or reject.

**Also flagged, not changed:** §3/§4's "maximum archetype EUI change was +2.85 %" phase-invariance
statement compares two campaigns that are **both** contaminated. The ratio may well survive, but I
cannot re-derive the v1 campaign from anything on this machine, so **it is marked unverified rather
than left implying it was checked.**

**No band value moved. No gate moved. Nothing under `Leg2_2-split/` was touched** — `V4-B2` owns that
and is closed. **No EnergyPlus cell was run.**

---

## 7. Reopen triggers

1. Any re-aggregation of Step 8 **must** be preceded by fixing `calculate_eui()` itself — pin
   `ReportName = 'AnnualBuildingUtilityPerformanceSummary'` and make the water guard unit-system
   agnostic. Until that lands, **every number this function produces is wrong in one of two ways**,
   and re-running the pipeline reproduces the defect faithfully.
2. If `2J_full_manuscript.md` is ever the submission vehicle rather than `readySubmission.md`, it
   needs the **campaign** fix as well as the correction — §5.
3. If the v1 campaign is recovered, re-derive the +2.85 % phase-invariance figure on corrected values
   and either confirm the sentence or replace it.
