# J2 (single-channel) vs J3 Leg-2 (two-channel "2-split") — Steps 4–7 comparison

**Pre-Step-8 gate review · compiled 2026-06-26.** Side-by-side of the occupancy pipeline between
**Journal 2 (Leg-1)** — single-channel *residential* occupancy (AT_HOME) — and **Journal 3, Leg-2
("2-split")** — the *two-channel* joint model that adds *office* occupancy (AT_WORK) alongside the
residential leg. Per-step detail is in `Step{4,5,6,7}_compare.md`; this file is the cross-step summary.

---

## The one structural change, threaded through every step

J3 Leg-2 is **J2 plus a second occupancy channel**. The residential (AT_HOME) leg is largely
*preserved* from J2; everything new in J3 exists to carry, calibrate, and wire the **office (AT_WORK)**
leg next to it. The defining design choice shows up at the BEM end as an **asymmetry**:

| Channel | J3 treatment in BEM (Step 7) | Why |
|---|---|---|
| **Residential** AT_HOME | **REPLACE** — per-household EnergyPlus schedule (same wiring as J2) | each dwelling is one zone with one household |
| **Office** AT_WORK | **MODULATE** — population *presence fraction* per office archetype × day-type × hour (× WFH band) | offices are shared; you shape the temporal profile, keep NECB/ASHRAE peak density |

A second pervasive change: **2030 is now three WFH sensitivity bands** (conservative 17.5% / hybrid
30% / fullyhybrid 40%) instead of J2's single 2030 scenario.

---

## Cross-step validation scorecard

| Step | J2 (Leg-1) | J3 Leg-2 (2-split) | Net read |
|---|---|---|---|
| **4 — Augmentation** | v5 shipped: **21 P / 1 W / 0 hard-FAIL** | **68 P / 1 W / 2 FAIL** | J3 runs a *much* larger gate set; the 2 FAILs are a structural work-peak floor + an unobservable day-type-ordering gate (1 diary/person) |
| **5 — Census linkage** | excl final: **30 P / 0 W / 4 FAIL** | **20 P / 1 W / 3 FAIL** | J3's 3 FAILs are all **inherited from the locked Step-4 base** (AT_HOME slot, AT_WORK slot, colleagues); 2 of J2's "FAILs" were a validator night-window bug J3 fixed |
| **6 — Forecasting** | **35 / 35 PASS** (2 documented deviations) | sign-off **"HEALTHY"** (no P/W/F count format) | both clean; J3's one accepted residual = weekday business-hours home under-prediction (~14 pp MAD), inherited from Step-4 lock, documented not gamed |
| **7 — BEM integration** | 2022 **29/0/0**, 2030 **28/0/0** | 2022 **32/0/0**, 2030 **43/0/0** | both fully clean; J3's higher counts = extra office + channel-consistency sections. J3 opened at 2/11 FAIL on 2026-06-26, cleared by fix-bundle A/B/C |

**Bottom line:** every step validates clean or with only **documented / inherited** residuals. No open
hard failure that is novel to J3 — the residuals all trace back to the deliberately *locked* Step-4
model, and are recorded honestly.

---

## What's genuinely new in J3 at each step

- **Step 4 (model).** Second output head (AT_WORK NAT) + `work_30min.csv` input + 48 `wrk30_*`
  columns. New *multi-head training discipline*: uncertainty weighting, PCGrad gradient surgery,
  diversity-preserving diurnal loss (prevents head collapse — J2 used fixed loss weights).
  **Float-aware rake** (04L) replaces the plain marginal rake, closing the 25–30% "FLOATING"
  (work-activity-but-no-location) records to 0%. Conditioning vector grew `d_cond 90 → 119`
  (NAICS, TELEWORK, WORK_SCHEDULE). Notably, **no architecture search was needed** — J2 burned 40+
  trials to find the J3 topology; Leg-2 reused it and tuned with one 6-variant HPT sweep.
- **Step 5 (linkage).** Adds employment / NOCS / NAICS / TELEWORK and **office-archetype** assignment
  (Knowledge / Public / Sales), emitting `wrk30` and a gated colleagues channel next to AT_HOME.
  Found & fixed a **province-coding bug** (`_PROVINCE_TO_REGION`) that had made ~70% of the diary pool
  unreachable; hardened row-count and per-person aggregation asserts.
- **Step 6 (forecast).** Three WFH bands (111,024 rows = 3 × 37,008 vs J2's 37,008). **Calibration
  B + C** chain (vs J2's single marginal rake): B caps weekday non-business work to the 2022 observed
  profile; C is a 3-stage post-hoc pass (weekend work cap → weekend home restore → activity
  donor-resample conditional on location). Diagnosed & fixed a **cross-day KNN self-pairing** bug
  (bands were identical) and proved TELEWORK is a flat band lever (bands come from post-hoc reweight).
- **Step 7 (BEM).** Entirely new **office output** `office_presence_multiplier_{2022,2030}.csv`
  (archetype × BAND × day-type × hour). Office uses **raw absolute AT_WORK_fraction as the schedule**
  (OD-7B: keep density, replace shape), not baseline×multiplier. Residential side is J2's wiring
  unchanged. 2030 source is the calibration-**C** `_C` file.

---

## Caveats / things to flag for the paper

1. **Inherited Step-4 residuals.** AT_HOME slot drift (~8.6 pp), AT_WORK slot drift (~10.2 pp), and
   colleagues (~4.4 pp) propagate from the *locked* Step-4 model down through Steps 5 & 6, and surface
   as the weekday business-hours home under-prediction in Step 6. They are documented and not gamed,
   but they are the main honest limitation of the two-channel result. Frame as a known floor, not a bug.
2. **Population-scale gap.** J2 links ~286 K persons / 144,507 HH (Census 2021); J3 Leg-2 links
   ~30 K persons / 23,150 HH (Census 2025 vintage + employed-enriched 2-split stock). The ~9.5×
   difference reflects census vintage/extraction and the employed-only enrichment of the office leg —
   **this needs an explicit explanation in the methods** so reviewers don't read it as a coverage loss.
3. **Calibration-C now modifies *weekend* `wrk30`.** The old "wrk30 never modified" note applied to
   weekday only; Step-7 fix-bundle C consciously caps weekend office work (425,428 person-slots, WE
   wrk30 18.6% → 6.6% toward observed 2022). Disclose in the calibration description.
4. **Office MODULATE is a modelling decision (OD-7A…E), not an empirical given.** The choice to keep
   NECB density and replace only the temporal shape (and to emit a peak-normalized multiplier but use
   the raw fraction as the default consumer input) should be stated as a design choice with rationale.
5. **Step-7 metabolic / Step-9 split.** J3 residential schema is 13 cols vs J2's 17 — J3 defers the
   four Step-9 activity-load columns (Equipment/Lighting fractions + design W) to the 2-split Step 9
   (OD-7D), so don't expect them in the Step-7 deliverable.

---

## Readiness for Step 8

All four steps are validated and the Step-7 deliverables exist (residential `BEM_Schedules_2split_*`
+ office `office_presence_multiplier_*`, 2030 sourced from the `_C` file). The only open items are
**documented inherited residuals**, not blockers. **Green light to scope Step 8** (EnergyPlus +
the new `office_integration.py`), carrying caveats 1–4 above into the paper's limitations/methods.

**Files in this folder:** `Step4_compare.md`, `Step5_compare.md`, `Step6_compare.md`,
`Step7_compare.md`, `README.md` (this index).
