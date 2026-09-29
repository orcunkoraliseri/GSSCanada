# Step 5 — WP3: baselines and surrogate (GPU)

### 5J occupancy-aware surrogate. Implementation specification.
#### Parent: `../5thJ_00_Occupancy_Surrogate_Pipeline.md` Step 5. Validation: `5thJ_05_surrogateTraining_val.md`

Written 2026-09-28. Week 3 (12 to 18 Oct 2026). 🔴 GPU access ends about 31 Oct 2026.

---

## STATUS

⬜ NOT STARTED. Needs Step 4 closed (gates frozen by checksum).

## AIM

Train the honest baselines and the sequence surrogate on the development split, choose on the
validation split only, pin the winner, and train the occupancy-blind control. No test split is opened.

## WHAT IS ALREADY DECIDED — DO NOT RELITIGATE

| Decision | Where |
|---|---|
| B0 average schedule, B1 boosted trees, S sequence model (two families), C blind control | Parent Step 5 |
| Model chosen on the validation split only; winner pinned (code hash, seed, checkpoint md5) | Overview, key decisions |
| If S does not beat B1, that is reported | Overview, key decisions |
| Inputs: occupancy and activity sequence, building description, weather | Overview, aim |

## 5A. INPUTS AND OUTPUTS (O-4, DRAFT)

* **Per hour t, driver channels:** presence (number at home, number awake at home), activity shares for
  the load-driving activity groups used by the 4J mapping (cooking, laundry, cleaning, media, personal care;
  primary and secondary activity, lesson 13), hot-water draw from the schedule, weather (dry-bulb, dew
  point, global horizontal and direct normal radiation, wind), hour of day, day of week, holiday flag.
* **Static building vector:** class, every Latin hypercube parameter, floor area, climate ID as a
  category only in within-country folds (dropped in leave-one-country-out, lesson 14).
* **Window:** 7 days of drivers before and the 24 hours being predicted (O-4: 7-day history, 24 h out,
  rolled over the year with a 24 h stride). The first week uses the previous days of the same year,
  wrapped (DRAFT; checked against a no-wrap variant on validation).
* 🔴 **No EnergyPlus output is ever an input** (no past loads, no zone temperatures). The surrogate must
  replace EnergyPlus, not follow it.
* **Outputs:** hourly heating, cooling, electricity for the 24 hours, per dwelling. Loss on
  standardised targets per end use, summed; a second loss term on paired differences inside a batch is a
  DRAFT option, tried only on validation.
* Identical encodings in all countries: a field only one country records is dropped (lesson 14).

## 5B. MODELS

* **B0 (average schedule):** the EnergyPlus run of the building with its average schedule (Step 2). Its
  predicted occupancy effect is zero by construction; it is the floor for G5J.3.
* **B1 (boosted trees, CPU):** gradient-boosted trees on hourly features: current and lagged drivers
  (lags 1, 2, 3, 6, 12, 24, 48, 168 h), rolling means of presence and outdoor temperature over 24 and
  168 h, the static building vector. One model per end use. Tuned on validation with a fixed budget
  (DRAFT 50 trials).
* **S (sequence model, GPU):** two families, same inputs and outputs:
  (1) temporal convolution network over the 192-hour window;
  (2) Transformer encoder over the same window, building vector added as a token.
  Budget per family fixed in advance (DRAFT 12 configurations each, early stopping on validation loss).
  Winner = best validation score on G5J.2 and G5J.3 combined as frozen in Step 4 (rule written before
  training). Pinned: git or file hash of the code, seed, checkpoint md5.
* **C (blind control):** the winner's configuration retrained from scratch with each run's occupancy
  and activity channels taken from a random other run of the same country (seed fixed); building,
  weather and targets unchanged.
* One seed repeat of S and C (three seeds DRAFT) to see seed spread (4J seed-floor lesson).

## 5C. CLUSTER

* GPU jobs as in 4J (`4J_docs_occ/tools/4thJ_step4_leg5_fold.sh`): `--partition=ps`,
  `--gres=gpu:nvidia_a100_7g.80gb:1`, `--cpus-per-task=8`, `--mem=192G`, `--time=7-00:00:00`.
* Data loader reads the extracted parquet from `/speed-scratch/o_iseri/5J/campaign/extracted/` through
  the split reader of Step 3 (test refused).
* Every job writes: config, code hash, seed, GPU hours, loss per epoch, best checkpoint md5, validation
  scores per gate, to `impl/<date>_wp3_training.md` (ledger) and `outputs_step5/`.
* Checkpoints copied to the local disk (`GSSCanada\_5J_data\surrogate\checkpoints\`) after each winner is
  pinned, **except UK-trained weights**, which stay on Speed or the author's own storage (UK rule,
  licence clause 4: no public release).

## 5D. LEAVE-ONE-COUNTRY-OUT

Three extra trainings of the pinned winner (and of B1), each on two countries, for G5J.6. Same
configuration, no re-tuning.

## OUTPUTS

`outputs_step5/models.md` (every trained model: config, hash, seed, checkpoint md5, validation scores),
`outputs_step5/winner.md` (pinned), training logs, `impl/<date>_wp3_training.md`.

## PROGRESS LOG (append-only)
- 2026-09-28 (manager): doc written as a plan. Next: Step 4.
