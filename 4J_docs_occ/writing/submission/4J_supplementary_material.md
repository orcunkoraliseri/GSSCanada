# Supplementary material

Companion to *Can a fine-tuned language model generate time-use diaries for a country without survey
data? A pre-registered test against reweighted real diaries*.

Contents. S1 the registered check set, with each tolerance's provenance. S2 the model card. S3 the
conditioning prefix and its census sources. S4 campaign sizes. S5 survey details. S6 harmonisation,
serialisation and population-linkage checks in detail. S7 supplementary results (Figures S1 to S4,
Tables S2 to S5). S8 the schedule clock correction. S9 the observed-stock campaigns. S10 validation
conventions. S11 limitations in full. S12 open items and documentation notes. S13 the equations behind every
reported quantity (Eqs. (S1) to (S44)).

---

## S1. The registered check set

Tolerances are marked **P** where the threshold comes from a published external source, **C** where it
was chosen by this project and registered before use, and **H** where it is a heuristic with no external
authority. The provenance mark is part of the registration and was not assigned after the results were
seen. Verdicts are printed as PASS, FAIL or NOT CHECKED.

### S1.1 Corpus, harmonisation and serialisation

| Check | What it scores | Tolerance | Prov. | Verdict |
|---|---|---|---|---|
| Acquisition, 16 checks | delivery integrity, codebook coverage, weight bounds, manifest completeness | various | C | Spain 15 PASS; Italy 1 FAIL; UK 1 FAIL |
| Italy source URL | a per-file source URL exists in the delivery | present | C | FAIL, recorded as not found |
| UK activity labels | every delivered activity code is labelled | complete | C | FAIL, one code labelled nowhere in the delivery |
| Harmonisation, 18 checks | alphabet closure, episode conservation, slot tiling, unknown-band prevalence | various | C | 16 PASS, 1 FAIL, 1 NOT CHECKED |
| Unknown-band escalation | one country's unknown share against another's | 10x ratio | H | FAIL; the clause fires unconditionally against a zero share |
| National table agreement | harmonised budgets against a published national table | -- | -- | NOT CHECKED; no independent published table is held |
| Serialisation, 20 checks | round-trip fidelity, token length, terminator presence, stratum coverage | various | C | 19 of 20 PASS; every fault-injection test detected |
| Sequence length | median, 99th percentile, maximum | 300 / 700 / 1200 tokens | C | PASS at 256 / 632 / 1178 |
| Stratum completeness | no stratum coded unknown | zero | C | FAIL on the UK, 551 diaries, neither imputed nor dropped |

### S1.2 Training

| Check | What it scores | Tolerance | Prov. | Verdict |
|---|---|---|---|---|
| Within-stratum variance ratio | generated against real dispersion inside a stratum | 0.80 to 1.25 | C | FAIL, 3 of 3; resolution-limited, see S1.6 |
| Shuffled-prefix cross-entropy | rise when the prefix is permuted | at least 0.15 nats/token | **H, unsourced** | FAIL, 7 of 7; measured 0.068 to 0.106 |
| Adapter merge drift | maximum logit difference, merged against unmerged | below 1e-4 | H | FAIL, 4 of 4; measured 3.2e-4 to 7.3e-4 across those four scored runs |
| Loss masking | prompt and pad positions carry the ignore label | 100 per cent | C | PASS |
| Held-in probe loss | final checkpoint within 5 per cent of its own best | 5 per cent | C | PASS on OLMo 3 7B, FAIL on Qwen2.5-7B |
| Within-stratum shuffle | cross-entropy rise and mutual-information drop, conjoined | 0.15 nats and 0.10 | H | FAIL; no decision record, see S1.6 |
| Fold isolation | held-out-country records loaded during training | exactly zero | C | PASS, every run |
| Pre-registration precedence | live hash of the frozen file against its registered value | exact match | C | PASS, every run |

### S1.3 Conditioning and population linkage

| Check | What it scores | Tolerance | Prov. | Verdict |
|---|---|---|---|---|
| Raking convergence | worst absolute marginal deviation after fitting | below 1e-13 | C | PASS |
| Marginal provenance | both sides of any comparison carry the same marginal source | identical | C | PASS, enforced in code |
| Temperature calibration reporting | the chosen temperature and its sensitivity are reported | reported | C | PASS |
| Temperature calibration sensitivity | entropy step exceeds seed-to-seed re-run noise | ratio above 1 | C | **FAIL on Spain (0.51) and the UK (0.99), PASS on Italy (1.29)** |

Of 36 check-by-fold verdicts at this stage, 34 pass and 2 do not. Both are the temperature sensitivity
check, which on Spain and the UK shows an entropy step no larger than the seed-to-seed noise. No
temperature was re-tuned and no re-run was performed.

### S1.4 Transfer

| Check | What it scores | Tolerance | Prov. | Verdict |
|---|---|---|---|---|
| **Transfer bar** | model time-budget error against the raked donor pool | positive margin | **C, pre-registered** | **FAIL, 9 of 9** |
| Single-donor baselines | each donor country's own population as a comparison | positive margin | C | reported, six populations |
| Pooled-average baseline | the cross-country pooled average, demoted to secondary | positive margin | C | reported |
| Budget agreement | level-1 budget against published tables | MAPE at or below 15 per cent; absolute bar of 15 min/day for groups below 10 min/day | P | FAIL, 9 of 9 |
| Frozen limitation criteria | three pre-declared conditions (model error not below the baseline's; MAPE above 20 per cent; model and published budget on opposite sides of the HETUS mean) | a cell is marked if any one holds | C | FAIL, 9 of 9; fault-injection coverage not demonstrable, see S7.2 |
| Held-in regression | training-country prefixes clear the same bar, and no forgetting | 15 per cent | P | FAIL, 6 of 6 on clause 1 |
| Fictional country, direction | movement in the specified direction | R-squared at least 0.80 | C | PASS, 3 of 3, OLMo 3 7B |
| Fictional country, amplitude | movement of the specified size | slope at least 0.80 | C | FAIL, 3 of 3 |
| Joint structure, dwell time | largest Wasserstein distance of episode durations over ten activities, against real held-out diaries | 10.0 min | C | FAIL, 50.13 to 66.57 |
| Joint structure, transitions | total variation of the transition distribution | 0.050 | C | FAIL, 0.1623 to 0.2344 |
| Joint structure, daily shape | Jensen-Shannon divergence of time-of-day distributions, mean over activities | 0.015 (maximum at most 0.025) | C | FAIL, 0.0690 to 0.1189 |
| Joint structure, budget | worst of ten activity budgets against real held-out diaries | 8.0 min | C | FAIL, 38.26 to 68.67 |
| Transition rate | absolute error in mean transitions per diary | 1.50 | C | Markov comparator PASSES at an error of 0.264 |
| Country discrimination | nearer its own published table than any other, by margin | relative margin above 0.5 | C | FAIL, 9 of 9 |
| Hour-support constancy | completeness invariant of the binning | complete | C | built and self-tested; never scored on model output (S12) |

### S1.5 Privacy

| Check | What it scores | Tolerance | Prov. | Verdict |
|---|---|---|---|---|
| Loss-based membership inference | area under the curve, 2,000 per class; true-positive rate at 0.1 per cent false-positive rate | AUC at most 0.65; TPR at most 5 per cent | C | **FAIL, 0.6645**, base floor 0.4886 |
| Reference-based membership inference | against the untuned public base | at most 0.75 | C | PASS, 0.5594 |
| Prefix-prompted extraction | exact matches on strata with fewer than five records | zero | C | PASS, 0 of 103 |
| Distance to closest record | released synthetic set against training records | see S7.4 | C | PASS Spain, PASS Italy, **FAIL UK** |
| Perplexity gap | control, not independent | at most 0.05 | C | FAIL, 0.0570; also 0.0511 on a permuted adapter |
| Memorisation ceiling | random-label-permutation control | -- | -- | **INCONCLUSIVE AS A CEILING**, 0.6496 |

Two registered privacy checks are not met and one is partial, so this set is not a passing audit.

### S1.6 Four training checks that miss their tolerance for reasons that are not about the model

Four training-stage checks never pass in this study. Each was traced to its own instrument. The
distinction supports the main text's reading that the model conditions and still loses.

**The variance-ratio tolerance is narrower than its own noise floor in two folds.** A probe on frozen
weights over five seeds per fold returns a seed-alone spread of 0.529 in Spain, 0.658 in the UK and 0.385
in Italy. The acceptance band is 0.45 wide in total. The spread is wider than the band in Spain and the UK
and narrower in Italy. In Spain and the UK the check therefore cannot separate a model effect from seed
noise at the sample size it runs at, and it is marked resolution-limited. One apparent pass on one fold
was a one-in-five-seed artefact and was not kept.

**The cross-entropy-rise bar has no recorded provenance.** It is the only threshold in its group with none.
The measured rise is 0.068 to 0.106 nats per token, and its sign is correct in every run. The fine-tune
bought between 84 and 1,062 times the untrained baseline's conditioning response (same-run pairs). The
check does not clear a bar that nothing justifies.

**The merge-drift tolerance can be met only by an adapter that learned nothing.** Scaling the adapter down
by a factor of 1,000 does not bring the drift inside the tolerance; it plateaus an order of magnitude above
it, and only a zero-scale adapter passes. The drift is behaviourally real rather than numerical noise. In
the shipping precision, merged and unmerged adapters produce different diaries in 39 to 46 of 48 cases,
81 to 96 per cent, while the unmerged-against-unmerged control is clean in 48 of 48 in every fold.

**One check was never adjudicated.** Its shuffle key omits one of the six prefix fields, so it can change at
most one field, and for 55 to 64 per cent of diaries it changes nothing at all. It is nevertheless required
to move cross-entropy as much as a full permutation would. Its measured rise is 0.002 to 0.0069. It carries
no decision record (S12).

---

## S2. Model card

| | |
|---|---|
| Backbone, main model | OLMo 3 7B, `allenai/Olmo-3-1025-7B`, revision `a81bae42db3975be1671e27b9c9a56da1a9f980f`, 7.30 B parameters |
| Backbone, smaller model | OLMo 2 1B, `allenai/OLMo-2-0425-1B`, revision `a1847dff35000b4271fa70afc5db10fd29fedbdf`, 1.48 B parameters |
| Backbone, second family | Qwen2.5-7B, `Qwen/Qwen2.5-7B`, revision `d149729398750b98c0af14eb82c78cfe92750796`, Spanish fold only |
| Adaptation | low-rank adapter, rank 32, scaling 64, dropout 0.05, rank-stabilised |
| Target modules | all seven linear projections per block |
| Trainable parameters | 79,953,920 (1.0837 per cent of 7,377,965,056) |
| Full fine-tune control | all 7,377,965,056 parameters, Spanish fold only |
| Objective | next-token cross-entropy, completion-only masking, unweighted |
| Epochs | 3 |
| Batch size / gradient accumulation | 2 / 8 |
| Learning rate | 1e-4, constant, no warmup or schedule |
| Optimiser | AdamW |
| Precision | bfloat16 |
| Maximum sequence length | 1,280 tokens |
| Seed | one fixed seed per trained model; no multi-seed training replication |
| Hardware | one A100 GPU partition |
| Wall time, OLMo 3 7B | Spain 11:00 h, UK 10:05 h, Italy 7:28 h |
| Checkpoint selection | none; the final checkpoint of the last epoch is used |
| Tokeniser | the backbone's own vocabulary, no tokens added |
| Decoding | grammar-constrained; temperature 1.30 / 1.10 / 1.20 (Spain / UK / Italy); nucleus sampling disabled |

No learning-rate schedule or warmup is applied; this is what the training code does, and no design
record chose it.

---

## S3. The conditioning prefix and its census sources

Six fields, frozen before training, reduced from an original nine.

| Field | Values | Source of the marginal used to build the synthetic population |
|---|---|---|
| country | 3 | -- |
| age band | 8 | national census age table |
| sex | 2 | national census sex table |
| household type | 6 in the alphabet, 5 raked | national census household table; the European census hub for Italy |
| economic status | 7 in the alphabet, **5 raked for Spain** | national census economic-activity table; on-demand microdata for Spain |
| day type | 3 | **no published marginal in any country; assigned at 5/7, 1/7, 1/7** |

The marginal sources are the census dissemination service for the UK, the 2011 census releases for
Spain, and, for Italy, a combination of the national census tract release and the European census hub,
because the Italian tract file publishes no household-type table. Iterative proportional fitting runs over
the four-way joint of age, sex, household type and economic status, starting from a uniform seed over the
admissible cells; a donor-seeded table was declared as a sensitivity only. The raked donor baseline is
raked onto the shares of this synthetic population on five variables, including day type at the
calendar-week shares. Expansion to 100,000 persons per
country is by deterministic largest-remainder integerisation, so the synthetic population carries no
sampling seed. The output is a person-level table; households are not assembled.

---

## S4. Campaign sizes

| Campaign | Composition | Total |
|---|---|---|
| Generation, per fold | 5,200 constrained + 5,200 unconstrained | 10,400 per fold |
| Held-in regression | 600 x 6 configurations | 3,600 |
| Fictional-country control | 600 x 5 levels x 3 folds | 9,000 |
| Archetype simulation | 88 archetypes x (1 control + 4 levels x 10 diaries) + 440 re-runs | 4,048 |
| Day-chaining experiment | 3 folds x 6 rule points x 5 seeds x 100 dwellings | 9,000 |
| Calendar probe | 3 folds x (10 + 10) | 60 |
| **Archetype campaign total** | executed twice, see S8 | **13,108** |
| Observed stock, heating campaign | completed cells: Madrid 11,340 / Bologna 11,680 / London 12,070 | **35,090 cells**; 3,529 buildings, 31,591 dwellings; not used in the paper (S9) |
| Observed stock, exploratory layout | different subdivision layout, exploratory, not used in the paper | 410 cells |
| Stock-scale end use | London 7,602 flats in 1,200 buildings; Bologna 29,902 flats in 1,126 buildings | 2 folds |
| Appliance timing by diary source | 3 folds x 3 diary sources (generated, real, raked donor), 100 dwellings, one year | 9 runs |

The count of 5,200 unconstrained diaries per fold was verified when that batch was generated. The
unconstrained files on disk were later replaced by a larger batch drawn for a different check, so the
decoding-neutrality comparison of the main text refers to the batch as generated.

---

## S5. Survey details

**Table S1.** - The three national time-use surveys as delivered.

| | Spain | United Kingdom | Italy |
|---|---|---|---|
| Instrument | INE *Encuesta de Empleo del Tiempo* | UK Time Use Survey (UKTUS), UK Data Service SN 8128 | ISTAT *Uso del Tempo* |
| Wave | 2009-10 | 2014-15 | 2013-14 |
| Delivered form | 144 fixed 10-minute slots | native episodes | native episodes, explicit clock times |
| Diaries | 19,295 | 16,533 | 41,229 |
| Episodes as delivered | 430,754 | 587,632 | 1,077,657 |
| Diary days per respondent | 1 | up to 2 (8,259 of 8,274 gave both) | 1 |
| Minimum age | 10 | 8 | 3 (proxy for 3 to 10) |
| Diary weight variable | `FACTORF` | `dia_wt_a` | `coefi2` |
| Weight convention | expansion | normalised, mean 1.000 | expansion |
| Calibration target | INE age-by-sex projection, by autonomous community | 2014 mid-year estimates, age and sex margins | ISTAT sex by nine age classes, regional totals |
| Access | open download, no credential | End User Licence, free registration | ISTAT public-use file |

Spain's episodes are reconstructed from its slot grid; the reconstruction is deterministic and is
verified against the grid it came from. Spain's episode boundaries are therefore an inference from a grid,
while the other two countries' are recorded. The Italian corpus contains diaries completed by parents for
children aged 3 to 10.

The three weights are each calibrated to their own national reference, and no two are calibrated to the
same table. They also target three different diary-day bases, and only the UK weight represents the
calendar week. Left uncorrected, this shifts at-home time by about one percentage point in Spain and Italy
and by essentially nothing in the UK. Every diary is reweighted to the calendar week before any statistic
is computed. Both the 2008 and the 2018 HETUS guidelines recommend two diary days per respondent, one
weekday and one weekend day, and accept a single day while noting that it leaves intra-personal variation
unmeasured (Eurostat, 2009, §2.2.1; Eurostat, 2019, §2.2.1). Of the three surveys, only the UK survey
follows the two-day recommendation.

Two delivery properties are recorded as data properties. One UK activity code appears in the data and is
labelled nowhere in the delivery. The Italian file carries no per-file source URL, so its acquisition
manifest records the field as not found.

---

## S6. Harmonisation, serialisation and population linkage in detail

**Harmonisation.** Harmonisation yields 2,024,068 episodes over 73,254 diaries, down from 2,096,043
episodes and 77,057 diaries as delivered. The episode difference closes exactly: 90,890 episodes are
removed below the age-11 floor, net of 18,915 episodes created when the 04:00 day start splits an episode
across the new boundary. The diary difference falls on the same age-11 floor, applied per respondent. Of
eighteen registered checks, seventeen were scored and sixteen passed. The exception is an escalation
clause that fires when one country's unknown-category share exceeds another's by a factor of ten. It fires
unconditionally whenever the comparison country's share is exactly zero, because any positive number
exceeds ten times zero; the check is at fault, not the data. One further check was not performed, because
no independent published national table is held. A re-tabulation of the project's own harmonised data
would share an ancestor with the reference and could never come up short.

Activity codes are mapped at the three-digit level from each country's primary activity variable. At the
published level the third digit buys exactly one distinction; it is kept for microdata fidelity, not for
published distinguishing power. One transition rule in the original design, expressed in terms of a
workplace location, could not be enforced because the harmonised location alphabet has no workplace class.
The corresponding check was demoted to a reported rate before generation.

**Why margins do not certify the joint.** During development, a correction that repaired one marginal left
the corresponding joint badly wrong: it generated more than fifteen hundred employed thirteen-year-olds
from a single donor day. It was found only because the joint was inspected directly. This is why every
stage of the study scores quantities that were never in the prompt and treats marginal agreement as a
precondition rather than as evidence.

**Serialisation.** The prefix was reduced to six fields from an original nine before training. Records
have a median length of 256 tokens, a 99th percentile of 632 and a maximum of 1,178. All 73,254 diaries
serialise, with no rows and no diaries dropped. Nineteen of twenty registered checks pass at baseline, and
all twenty-one injected faults were detected by the check they targeted. The single exception is the
stratum-completeness check: 551 UK diaries carry a household type recorded as unknown. No row is imputed
or dropped, and the check is left unmet because the category exists in the data.

**Population linkage.** The four-way joint table is fitted to a worst absolute marginal deviation below
1e-13. Of 36 check-by-fold verdicts, 34 pass (S1.3). Day type is assigned at calendar-week proportions,
and Spain is fitted on five of seven economic-status categories.

---

## S7. Supplementary results

### S7.1 Primary comparison

![Figure S1](figures/Figure_03_nine_cells.png)

**Figure S1.** - Time-budget mean absolute error of the model and the raked donor pool in the nine cells.

The exact margins are -26.8784, -25.6944 and -32.5068 minutes per day for Spain (ages 25-44, 45-64, 65
and over), -37.113, -41.2313 and -2.698 for the UK, and -42.7338, -20.0943 and -20.335 for Italy. The
model-to-baseline error ratio ranges from 1.1461 (UK, 65 and over) to 3.9119 (Spain, 45-64).

### S7.2 Further transfer checks

**Limitation criteria.** The fault-injection coverage of this check is not demonstrable, for vacuity rather
than weakness: every cell already falls short at baseline, so no injected fault can show detection.

**In-sample regression.** Table S2 gives the six in-sample cells of OLMo 3 7B. A pair "a on b" is the model
of the fold that holds out country a, scored on training country b. The bar is a worst-band MAPE of at most
15 per cent. The same check scored on the real corpus gives 4.64 per cent in Spain, 5.96 per cent in the UK
and 11.50 per cent in Italy, so the bar can be met. A second clause of this check was first read as passing
in five of six cells on the 1B model and, on re-derivation, passes in two.

**Table S2.** - In-sample check of OLMo 3 7B on its training countries.

| Fold (held out) | Training country scored | Worst-band MAPE (per cent) | Worst-band MAE (min/day) | Verdict |
|---|---|---:|---:|---|
| Spain | Italy | 158.07 | 49.06 | FAIL |
| Spain | UK | 33.10 | 45.79 | FAIL |
| Italy | Spain | 53.94 | 88.10 | FAIL |
| Italy | UK | 48.93 | 51.28 | FAIL |
| UK | Spain | 45.88 | 71.36 | FAIL |
| UK | Italy | 151.49 | 44.27 | FAIL |

**Country discrimination.** In the Italian fold's youngest band the margin is -0.4555: Italy's own real
diaries are nearer to Spain's published table than to Italy's. This is the different survey round of
Italy's published budget appearing as a measurement.

**Capacity.** Table S3 gives the three capacity interventions.

**Table S3.** - Three capacity interventions.

| Intervention | Change | Effect on the transfer result |
|---|---|---|
| Backbone size | 1.48 B to 7.30 B, a factor of 4.9 | mean error 42.05 to 43.14 minutes per day, worse; 4 cells better, 5 worse |
| Trainable parameters | 79,953,920 to 7,377,965,056, a factor of 92 | higher training loss at every epoch; adapter 0.508305 against full fine-tune 0.513494 at the last epoch |
| Backbone family | Qwen2.5-7B, same recipe, Spanish fold | about 22 per cent more wall time, 16 per cent more memory; only the held-in probe-loss check separates the two |

The full fine-tune and the adapter tie on content loss. No claim is made that the full fine-tune changed
dispersion in either direction.

**Fictional-country control, exact values.** Only the age-band mix of the conditioning population is tilted.
Direction is scored on the study group that the tilt targets; amplitude is the slope pooled over the five
outcome groups other than leisure. For OLMo 3 7B, the direction $R^2$ is 0.9897, 0.9914 and 0.9941
(Spain, UK, Italy) and the pooled amplitude slope is 0.4153, 0.5329 and 0.4049. For OLMo 2 1B, $R^2$ is
0.8455, 0.9808 and 0.9836 and the slope 0.2666, 0.4612 and 0.3785. Both are computed over the same five
activity groups, with the leisure group excluded by name.

### S7.3 Joint structure and decoding

![Figure S2](figures/Figure_05_joint_structure.png)

**Figure S2.** - Four structural properties, each as a multiple of its tolerance, across the three folds.

Without the grammar mask, the valid-diary rate is 6.88 per cent in Spain, 30.96 per cent in the UK and
10.65 per cent in Italy (358, 1,610 and 554 of 5,200), against a requirement of 99.90 per cent. The mask
intervened in 93.16, 69.84 and 89.62 per cent of the generated population. The decoding-neutrality check,
at 5,169, 5,066 and 5,065 valid diaries, has a worst three-digit activity code off by 101.02, 29.60 and 48.87 minutes per day
against a tolerance of plus or minus 5.0.

### S7.4 Privacy

The loss-based attack scores an AUC of 0.6645, 1.70 standard deviations over the ceiling of 0.65; the
untuned-base floor on the same construction is 0.4886. The reference-based attack scores 0.5594 against a
ceiling of 0.75. Prefix-prompted extraction on strata with fewer than five records finds 0 exact matches in
103 attempts. The distance-to-closest-record check passes on Spain and Italy; on the UK, the test-set median
distance of 0.4236 lies above the size-matched training interval of 0.4028 to 0.4167. The perplexity gap is
0.0570 against a ceiling of 0.05, and 0.0511 on a randomly permuted adapter, so it measures fit to the
language of diaries rather than membership. The memorisation control scores 0.6496, only 0.0149 below the
attack, and moved by 0.102 when capacity increased, so it does not bound the attack.

### S7.5 Appliance and hot-water loads

![Figure S3](figures/Figure_06_appliance_peaks.png)

**Figure S3.** - Mean appliance electricity by hour of day from the generated diaries, three folds.

**Table S4.** - Peak and runner-up hour of stock appliance electricity (W per dwelling), 100 dwellings, one year.

| Country | Generated diaries | Real diaries (unweighted) | Raked donor diaries |
|---|---|---|---|
| Spain | 14:00, 502.9 W (2nd: 19:00, 436.5 W) | 21:00, 421.5 W (2nd: 13:00, 405.9 W) | 19:00, 408.5 W (2nd: 20:00, 402.5 W) |
| Italy | 18:00, 403.5 W (2nd: 22:00, 332.0 W) | 19:00, 444.4 W (2nd: 20:00, 411.7 W) | 21:00, 396.5 W (2nd: 20:00, 379.4 W) |
| United Kingdom | 20:00, 416.1 W (2nd: 13:00, 348.0 W) | 18:00, 427.2 W (2nd: 19:00, 415.7 W) | 21:00, 425.9 W (2nd: 20:00, 411.3 W) |

Only the diary source differs between the three columns. The real pool holds 5,200 diaries per country,
drawn uniformly from that country's diaries. The raked donor pool holds 5,200 diaries per country, drawn
from the other two countries' diaries with probability proportional to the raked weight; it contains no
diary from the target country. Re-running the generated-diary case reproduced the stock series behind the
peaks byte for byte in all three folds; in two folds, one per-dwelling annual total differed by 0.001 kWh
through last-digit rounding across computing platforms.

**Secondary activity.** The generated diaries carry a secondary activity on 29.816 per cent of episodes and
26.308 per cent of modelled minutes, across 29 distinct codes. The trigger never reads it.

**Laundry.** Eligible laundry minutes per dwelling-year are 2,462 in Spain, 1,589 in the UK and 781 in Italy,
against 27,036 required by the reference washing machine's published cycle count. After calibration,
modelled washing-machine cycles reach 0.776, 0.179 and 0.092 of the published count. Load-shape agreement
is $R^2$ = 0.2967, 0.4106 and 0.0346 against a floor of 0.85. At stock scale, on 7,602 London flats and
29,902 Bologna flats, agreement is 0.4347 and 0.0781. Three appliances run 74 to 84 per cent below the
published cycle count while the laundry appliances saturate. The reference profile is more than 77 per cent
laundry at 11:00, and this model suppresses laundry starts by 80 to 90 per cent. No tolerance was moved at
either scale.

**Hot water.** The registered per-person check measured 100.16, 117.65 and 91.06 litres per person per day
against a band of 30 to 50. The modelling source publishes 200 litres per day per dwelling at a 35 kelvin
rise, with no per-person figure. The band traces instead to a review (Fuentes et al., 2018). The scored
quantity reduces to 200 divided by household size, to within 0.0005 over all 300 rows, so the check measured
household size rather than the hot-water model. It is kept as informational, with its band unchanged. A
replacement check scores the stock mean per dwelling against the source's 200 litres, plus or minus ten per
cent. It was shown to detect deliberately doubled draws (about 401 litres) before being used. It passes at
200.79, 201.01 and 199.47 litres, and at stock scale at 202.41 and 200.35. It is a consistency check, not an
external validation.

### S7.6 Heating

**Table S5.** - Occupancy effect on heating at full sensitivity ($f = 1$).

| | Spain | United Kingdom | Italy |
|---|---:|---:|---:|
| Peak effect | +2.7145 % | +0.0393 % | -0.6332 % |
| Between-diary spread | 4.9837 % | 2.3797 % | 1.5959 % |
| Ratio of effect to spread | 0.54 | 0.02 | 0.40 |
| Annual median effect | -1.5100 % | -0.3605 % | -0.4178 % |

![Figure S4](figures/Figure_07_heating_null.png)

**Figure S4.** - Occupancy effect on heating: peak effect against the between-diary spread (A), the annual channel (B1) and apartment buildings (B2).

The apartment-building effect is +3.4617, +1.0421 and +0.5002 per cent. The hour of the annual peak never
moves at any sensitivity level in any fold, because it is the thermostat recovery hour of the model.

**Dynamic against quasi-steady-state heating.** Simulated hourly heating demand differs from TABULA's
published quasi-steady-state monthly figure by +136.6 per cent in Spain, -29.6 per cent in the UK and -36.7
per cent in Italy. In Spain, the published method counts gains over a 539-hour heating season, while the
simulation heats for 2,901 hours at the same set point. This is a structural comparison between two models,
kept as informational.

**Exploratory observed-stock layout (410 cells).** In an exploratory run with a different subdivision layout, moving from no occupancy signal to the
full signal moves annual heating by under half a per cent, while it moves the hourly peak by up to 7.92 per
cent and the peak hour by up to 41 hours. It is not a scored result of this study.

**Weather.** Stations were selected by scoring 44 candidates against TABULA's published monthly
temperatures. The UK selection margin between the two best candidates was 0.002 K. The choice is worth 5 to
11 per cent of heating demand.

---

## S8. The schedule clock correction

Harmonisation places every diary on a 04:00 day start, the native start of two of the three surveys. The
schedule writer emits an EnergyPlus `Schedule:File` whose first value carries no time-of-day field, and
EnergyPlus reads that first value as midnight. Every one of the 13,108 simulations in the first archetype
campaign therefore applied its occupancy signal four hours early. The fix is a single cyclic rotation of the
whole annual series, applied before any perturbation. It was verified three ways: a bit-identical
reproduction of the old result with rotation disabled; agreement with an independently written
implementation in the end-use step on all 8,760 hourly values of 100 dwellings; and a byte-identical re-run
of a schedule-free control. All 13,108 runs were then re-executed, and no pre-rotation number is used.

After rotation, the occupancy effect on annual heating is negative in every fold at every level of $f$, and
the peak effect falls below the between-diary spread in all three folds. The ordering across dwelling
classes is the same before and after the correction.

The gain conservation of Eq. (3) of the main text is enforced in the schedule emitter and was measured. One
build held the annual mean to within four parts in ten million of the reference value rather than exactly,
because the multiplier had been written to six decimal places; the check that found it is now a guard.

---

## S9. The observed-stock campaigns

**Heating campaign.** This campaign applies a subdivision rule under which a floor plate divides into
dwellings only, every square metre belongs to a flat, nothing is narrower than two metres, and one flat is
one thermal zone. It covers 3,529 buildings and 31,591 dwellings in districts of Madrid, Bologna and London,
with 35,090 completed simulation cells (Madrid 11,340, Bologna 11,680, London 12,070). Building footprints,
construction years and dwelling counts come from national open registries, and each building carries the
archetype identifier emitted by the stock pipeline. Its checks were scored after the results of this paper
were fixed. That scoring found that, in a small number of cells, dwellings holding different diaries
produced byte-identical internal-gain series. No scored result from this campaign is used in the paper. In
Madrid, 170 cells in 17 buildings did not complete and were not repaired. Three courtyard buildings in
Bologna are outside what this subdivision method can simulate. A Lyon district was kept in the wider project
as a physical baseline only and is never a denominator for any result.

**Exploratory layout (410 cells).** An exploratory campaign of 410 cells, with a different subdivision layout, is
reported in S7.6 for completeness only. Two of its provenance links are missing: five manifest
fields are written on zero of the 410 cells, and the rotation declaration is absent from every cell
manifest, although the convention is declared correctly upstream. Neither was written retroactively.

**Stock-scale end use.** The appliance and hot-water model runs on two districts, 7,602 flats in 1,200
London buildings and 29,902 flats in 1,126 Bologna buildings. Forty-nine buildings carrying floor-averaged
rather than per-flat diaries are excluded, never scored and never estimated.

---

## S10. Validation conventions

Every threshold is registered with its provenance marked as published, project-chosen or heuristic (S1).
Where a threshold carries no external authority, the verdict is kept and the missing provenance is stated.

Every check is paired with a fault-injection test: a deliberately injected fault must be detected by the
check that targets it before the check's passing verdict is trusted. The coverage summary distinguishes
three states: a check that passed and was seen to detect the injected fault; a check that passed but whose
detection could not be demonstrated; and a check that already fell short at baseline and therefore cannot
demonstrate detection. Results of the third kind are reported as already unmet, not as detections.

Three further conventions apply. A check that returns a verdict on zero rows reports that it is not
evaluable, not that it passed. A check whose reference cannot be obtained reports as not checked; two such
appear in this work, both citation checks requiring network access. And authorisation to run a campaign is
not authorisation to read it as a scored result: the tooling emits no scored verdict until a second,
separate authorisation is recorded.

Five practical lessons follow from this study. A check scores a quantity and also detects a class of fault,
so retiring it for the first reason also retires the second; when the per-person hot-water check became
informational, a replacement detector had to be built. A crash is not a partial result: a self-test that
raised an exception made every later fault unreachable while the summary still looked populated. An empty
population has not been satisfied; several checks returned passes on zero rows before they were taught to
report that they were not evaluable. A re-run that reproduces the previous answer exactly may mean the fix
did not reach the tool; a bit-identical result across nine thousand simulations was traced to a script that
bypassed the emitter. And the check itself can be the faulty artefact: a multiplier inert against a zero
denominator, a first-match histogram that read like a diagnosis, and a parser blind to the only object shape
it would meet were all found by asking what the instrument was doing.

---

## S11. Limitations in full

**Corpus size.** The corpus is three countries with one wave each, and every fold trains on two. What was
measured is that a model fine-tuned on two European countries does not beat a donor pool drawn from those
same two countries. Whether the same model trained on eight or twenty source countries would beat the same
baseline is not measured. The author searched survey statistics, small-area estimation, spatial
microsimulation and the domain-generalisation literature for a published floor on the number of source
populations below which cross-population transfer is not expected to succeed, and found none stated as a
rule (search of 2026-09-13). The study cannot defend its result by pointing to such a threshold, and the
result cannot be dismissed by pointing to one. Identifiability results for invariant-risk estimators bound
the number of training environments needed to separate invariant from environment-specific structure, but
they apply to estimators with an explicit invariance objective. The model here is a low-rank adapter
trained by next-token prediction, with no such objective.

**In-sample shortfall.** The held-in check does not clear its bar on any of the six training-country cells
(Table S2). The shortfall is therefore not confined to transfer.

**Survey year.** The three waves are 2009-10, 2013-14 and 2014-15, so survey year is confounded with
country, and therefore with the leave-one-country-out split.

**The conditioning vector.** The model receives demographic margins: age, sex, economic status, household
structure and day type. What separates a Spanish weekday from a UK one is largely not demographic: the hour
the working day ends, the hour of the main meal, school and shop hours, latitude and the time of sunset.
None of that can be recovered from age and employment tables. The appliance-timing results are consistent
with this: real diaries carry country timing, and neither synthetic source does. This limits the design,
not the comparison, because the raked donor pool received the same margins and no more.

**Survey and frame.** The study inherits the coverage and non-response of three national surveys. People in
institutions, people without housing and hotel guests are outside the sampling frame. Respondents give one
or two diary days each, so multi-day dependence is largely unobservable. The three files target different
diary-day bases; every diary is reweighted to the calendar week. The Italian fold is scored against a
published aggregate from a different survey round than its microdata. The UK household-type cell coded
unknown covers 551 diaries, 3.5 per cent of that fold, and no generated diary can carry it because the
census has no such category; dropping the cell moves whole-fold MAE by 0.158 minutes per day. Spain's
synthetic population has no homemaker category, and day type is assigned by calendar week. Sex is a
conditioning stratum and is not analysed separately.

**Pretrained prior.** A pretrained backbone has read very different amounts of text about Spain, Italy and
the UK, in different languages and from different periods. Nothing in the design separates what fine-tuning
taught about a country from what pretraining already contained. This confound was pre-registered and is
unresolved. In a leave-one-country-out design it is aligned with the split by construction.

**Constrained decoding.** Renormalising the sampling distribution over the allowed tokens changes the
distribution being sampled. The neutrality check misses its tolerance in all three folds at parity sample
size, and the direction of the resulting bias is not quantified. Generated output is never raked, because
raking would close the marginal gap by construction and the agreement would measure the raking.

**Training seeds.** Each model was trained with one seed. The seed-to-seed probe on frozen weights measures
generation noise only.

**Energy claims.** Every energy-use intensity is heating-only and may not be compared with a whole-building
or measured total. No cross-country comparison of absolute demand is safe at the ten per cent level, because
the weather file alone is worth 5 to 11 per cent of heating demand and its sign differs by fold. Every
cross-fold claim is therefore about timing, shape or ordering. Absolute intensities from the archetype and
observed-stock campaigns are never placed side by side or differenced. The sensitivity design holds annual
internal gain fixed, so it can redistribute gain in time but never add or remove energy over a year. Each
dwelling is one thermal zone, so the study can say when gains move but not where in a dwelling. The UK
archetypes are parameterised from England's typology.

**Per-dwelling claims and the appliance model.** No per-dwelling prediction is made at any scale. Moving
from archetypes to tens of thousands of real buildings raises confidence in an aggregate and does nothing
for an individual household. The trigger fires from the primary recorded activity only, so a load recorded
only as a secondary activity is invisible to it; the total of such loads has no published bound. The
ownership shares are from the UK and about two decades old and are applied unchanged to Spain and Italy, so no
ownership-dependent quantity should be read as country-specific. The real-diary pool behind the appliance
timing is unweighted. Each appliance run covers 100 dwellings for one year with one seed, so the peak hour
carries no interval, and the peaks are flat-topped. Timing is checked against real diaries through the same
model, not against measured national load profiles, so the result concerns appliance timing, not load
shape. The hot-water comparison is a denominator mismatch and is reported neither as a model limitation
nor as a pass.

**Reproducibility.** Reproduction gives the same statistics, not the same bytes, and this was measured.
Results from the observed-stock campaign are numerically stable rather than bitwise reproducible. Merged and
unmerged adapters produce measurably different populations, and no intermediate artefact records which of
the two produced it.

**Release.** The adapter weights are not released. The decision was taken before training, on the terms of
the data agreements rather than any model licence, and is reinforced by the membership-inference result.
The UK synthetic population is withheld with the weights. The Spanish and Italian synthetic populations,
the code, the check implementations and the frozen pre-registration file are available as stated in the
data availability statement. The archetypes are this study's own construction from TABULA parameters and
are not an official TABULA product. The author's institution is not a Eurostat-recognised research entity;
an enquiry was sent on 2026-08-26 and had received no reply when this material was prepared.

**What should not be inferred.** The backbone comparison is two points and is not a scaling curve. The full
fine-tune is a ceiling run on one fold, and the second model family was tested on one fold. The privacy set
is not a passing audit. The memorisation control does not bound what it was built to bound, and the
perplexity gap is not independent confirmation. No scored result is taken from the larger observed-stock
campaign.

---

## S12. Open items and documentation notes

**One check was never adjudicated.** The within-stratum shuffle check (S1.6) ships unmet, without a decision
record. Its shuffle key omits one of the six prefix fields.

**One invariant was built but never exercised on model output.** The hour-support constancy invariant was
built, passed its self-test and detected a deliberately injected fault on real diaries, but it was never
scored against generated output. It is not counted as passed.

**Full fine-tune manifest.** The manifest shipped with the full fine-tune control describes a low-rank adapter
run, while that job's own log records a full fine-tune with no adapter. The manifest was not edited; a
correction file sits beside it, and the numbers in this paper come from the correction file.

**Training-record label.** The comparison table in the training record labels the main model's column with
the wrong backbone family. The manifest and the run configuration identify it correctly.

**Observed-stock campaign.** The larger observed-stock campaign ran to completion, but no scored result from
it is used (S9). In Madrid, 170 cells in 17 buildings did not complete, and three courtyard buildings in
Bologna are outside the subdivision method.

## S13. Equations

This section defines the quantities reported in Sections 2 and 3 of the main text. Throughout, $a$ indexes activity categories, $b$ one of the three scored age bands (25-44, 45-64, and 65 and over), $c$ a country and $i$ a diary. Every diary covers 1,440 minutes in ten-minute steps. Eqs. (1)-(6) of the main text are used here and not repeated.

### S13.1 Time budgets and the primary comparison

The time budget of a set of diaries $S$ is the weighted mean number of minutes per day spent in each of the six HETUS activity groups:

$$\hat{B}_S(a) = \frac{\sum_{i\in S} w_i \sum_{e\in i} d_e\,\mathbb{1}\!\left[\kappa(c_e)=a\right]}{\sum_{i\in S} w_i}, \qquad a\in\mathcal{A} \qquad (\mathrm{S1})$$

Here $\mathcal{A}$ is the set of the six groups of Section 2.6, and $w_i$ is the weight of diary $i$: 1 for a generated diary, the raking weight of Eq. (2) for a donor diary, and the calendar-week weight of Eq. (S13) for a real diary of the held-out country. The index $e$ runs over the episodes of diary $i$, $d_e$ is the duration of episode $e$ in minutes, $c_e$ its three-digit primary activity code, and $\kappa(\cdot)$ the map from codes to groups. The map follows the leading digit, except that codes 995-997 and 999 (unspecified time) belong to no group, code 998 belongs to leisure, and code 910 (travel to and from work) stays in travel. The published budget $B^{\mathrm{pub}}(a)$ is read from the Eurostat table for the same country and age band; its travel budget is the sum of seven published sub-categories.

The error and the margin of one cell are those of Eq. (5), with $\hat{B}(a) = \hat{B}_S(a)$ for the candidate's diaries in the band. The inequality $m > 0$ is strict, so a baseline scored against itself ($m = 0$) does not pass. The donor pool is raked on the whole population and restricted to the age band afterwards.

### S13.2 Percentage error and the absolute bar

Each published group is assigned a scoring basis from its published value alone, in minutes per day:

$$\text{group } a \text{ is } \begin{cases} \text{a zero cell, met if } \hat{B}(a) < 0.01\times 1440, & B^{\mathrm{pub}}(a) < 0.5,\\ \text{a floor cell, met if } \left|\hat{B}(a) - B^{\mathrm{pub}}(a)\right| < 15, & 0.5 \le B^{\mathrm{pub}}(a) < 10,\\ \text{scored on } \mathrm{APE}(a) = 100\,\left|\hat{B}(a) - B^{\mathrm{pub}}(a)\right| / B^{\mathrm{pub}}(a), & B^{\mathrm{pub}}(a) \ge 10 \end{cases} \qquad (\mathrm{S2})$$

with $\mathrm{APE}(a)$ in per cent. Percentage errors are not taken below 10 minutes per day because a small denominator makes them unstable (Hyndman and Koehler, 2006). The mean absolute percentage error of one band is

$$\mathrm{MAPE} = \frac{1}{|\mathcal{A}^{\mathrm{APE}}|}\sum_{a\in\mathcal{A}^{\mathrm{APE}}} \mathrm{APE}(a), \qquad \text{met if } \mathrm{MAPE}\le 15 \text{ and every zero and floor cell is met} \qquad (\mathrm{S3})$$

where $\mathcal{A}^{\mathrm{APE}}$ is the set of groups of the band scored on APE (Hyndman and Koehler, 2006).

For a model scored on a country it was trained on, the in-sample check takes the worst band:

$$\mathrm{MAPE}^{\mathrm{worst}} = \max_{b}\ \mathrm{MAPE}_b, \qquad \text{met if } \mathrm{MAPE}^{\mathrm{worst}}_{\mathrm{in}} \le 15 \ \text{ and }\ \mathrm{MAPE}^{\mathrm{worst}}_{\mathrm{in}} - \mathrm{MAPE}^{\mathrm{worst}}_{\mathrm{out}} \le 0 \qquad (\mathrm{S4})$$

Here $\mathrm{MAPE}_b$ is Eq. (S3) in band $b$, the maximum runs over the three scored bands, and the subscripts in and out denote the same country scored as a training country and as the held-out country.

The three frozen limitation criteria mark a cell if any one of them holds:

$$\mathrm{MAE}^{\mathrm{model}} \ge \mathrm{MAE}^{\mathrm{base}}, \quad\text{or}\quad \mathrm{MAPE} > 20, \quad\text{or}\quad \exists a:\ \left|B^{\mathrm{pub}}(a) - \bar{B}^{\mathrm{EU}}(a)\right| \ge 2 \ \wedge\ \operatorname{sgn}\!\left(B^{\mathrm{pub}}(a) - \bar{B}^{\mathrm{EU}}(a)\right) \ne \operatorname{sgn}\!\left(\hat{B}(a) - \bar{B}^{\mathrm{EU}}(a)\right) \qquad (\mathrm{S5})$$

Here $\bar{B}^{\mathrm{EU}}(a)$ is the unweighted mean of the published budgets of all HETUS countries with a complete profile in the same band. The floor of 2 minutes per day excludes differences within the rounding of the published table.

### S13.3 The raked donor baseline

The donor diaries are raked by Eq. (2), starting from $w_i = 1$, over the five variables $v \in \mathcal{V}$ = {age band, sex, household type, economic status, day type}, one variable at a time. The target shares $T_v(k)$ are the shares of the held-out country's synthetic population (Eqs. (S10)-(S12)), which is the fitted form of its published margins; day type is at calendar-week shares. The resulting weights are a calibration estimator in the sense of Deville and Särndal (1992): they depart from the starting weights as little as the margins allow. Weights are not integerised. Full sweeps over $\mathcal{V}$ are repeated until

$$\max_{v\in\mathcal{V},\,k}\ 100\,\left|C_v(k) - T_v(k)\right| \le 0.5 \qquad (\mathrm{S6})$$

in percentage points, with at most 200 sweeps. A pool that does not converge, or a target category that no donor carries, stops the comparison. The weights therefore approximate the raking solution to within 0.5 percentage points on every margin, rather than reaching its exact optimum.

The effective sample size of the raked donor diaries in one band is

$$n_{\mathrm{eff}} = \frac{\left(\sum_{i} w_i\right)^2}{\sum_{i} w_i^2} \qquad (\mathrm{S7})$$

where the sums run over the donor diaries in the band.

### S13.4 Bootstrap interval of the margin

For replicate $j = 1,\dots,R$ with $R = 2{,}000$, the generated diaries of each band are resampled with replacement at their original number. The donor pool is resampled with replacement within each donor country at its original number, re-raked by Eqs. (2) and (S6) onto the same targets, and restricted to the band. The replicate margin is

$$m^{*}_{j} = \mathrm{MAE}^{\mathrm{base}*}_{j} - \mathrm{MAE}^{\mathrm{model}*}_{j} \qquad (\mathrm{S8})$$

where the starred errors are those of Eq. (5) on the resampled sets. Replicates whose re-raking does not converge are excluded and counted. The 95 % interval is the percentile interval of the $R'$ retained replicates:

$$\left[\,q_{0.025},\ q_{0.975}\,\right], \qquad q_p = m^{*}_{(\lfloor \xi\rfloor)} + \left(\xi-\lfloor \xi\rfloor\right)\left(m^{*}_{(\lceil \xi\rceil)} - m^{*}_{(\lfloor \xi\rfloor)}\right), \quad \xi=(R'-1)\,p \qquad (\mathrm{S9})$$

Here $m^{*}_{(k)}$ is the $k$-th smallest replicate margin, counted from $k = 0$.

### S13.5 Synthetic population

A four-way table $\Psi$ over age band, sex, household type and economic status is initialised on the structurally admissible cells, $\Psi^{(0)} \propto M$. Here $M$ is the 0/1 admissibility mask (for example, no person aged 11-14 lives alone), and the row of ages 11-14 is scaled by the donor countries' economic-status mix at those ages. Each margin variable $v$ is then fitted in turn:

$$\Psi(\mathbf{k}) \leftarrow \Psi(\mathbf{k})\,\frac{\pi_v(k_v)}{\Psi_v(k_v)}, \qquad \text{until } \max_{v}\max_{k}\left|\Psi_v(k)-\pi_v(k)\right| < 10^{-13} \qquad (\mathrm{S10})$$

Here $\mathbf{k}$ is a cell of the table, $k_v$ its category on variable $v$, $\Psi_v$ the current margin of $\Psi$ on $v$ as a share, and $\pi_v$ the published marginal share, with at most 5,000 sweeps. Zero cells stay zero. Fitting a joint table onto published margins by iterative proportional fitting follows Beckman et al. (1996).

Day type, which has no published margin, is added as an independent fifth variable at calendar-week shares:

$$\Psi_5(\mathbf{k},\tau) = \Psi(\mathbf{k})\,\delta_\tau, \qquad \delta=\left(\tfrac{5}{7},\,\tfrac{1}{7},\,\tfrac{1}{7}\right) \text{ for (weekday, Saturday, Sunday)} \qquad (\mathrm{S11})$$

The fitted table is expanded to $N = 100{,}000$ persons by the largest-remainder rule:

$$n_{\mathbf{k}} = \left\lfloor N\,\Psi_5(\mathbf{k})\right\rfloor + \mathbb{1}\!\left[\mathbf{k}\in\mathcal{R}\right] \qquad (\mathrm{S12})$$

Here $\mathbf{k}$ runs over the cells of the five-way table, and $\mathcal{R}$ is the set of the $N-\sum_{\mathbf{k}}\lfloor N\,\Psi_5(\mathbf{k})\rfloor$ cells with the largest fractional parts of $N\,\Psi_5(\mathbf{k})$, ties broken by cell index. No random draw is involved, in contrast to the probabilistic integerisation of Lovelace and Ballas (2013).

### S13.6 Calendar-week weights

Each real diary's survey weight $w_i$ is post-stratified to the calendar week within its country:

$$w^{\mathrm{cal}}_i = w_i\,\frac{\delta_{\tau(i)}}{\hat{\delta}_{c,\tau(i)}}, \qquad \hat{\delta}_{c,\tau} = \frac{\sum_{i'\in c,\ \tau(i')=\tau} w_{i'}}{\sum_{i'\in c} w_{i'}} \qquad (\mathrm{S13})$$

Here $\tau(i)$ is the day type of diary $i$, $\delta_\tau$ the calendar-week share of Eq. (S11), and $\hat{\delta}_{c,\tau}$ the weighted share of day type $\tau$ in country $c$ before re-basing. The total weight of each country is unchanged.

### S13.7 Joint structure

In this subsection the activity of an episode is the first digit of its three-digit code (ten activities), and every distribution is weighted by $w^{\mathrm{cal}}_i$ of Eq. (S13). The reference is the real diaries of the held-out country and the candidate is the generated diaries.

Dwell times. For activity $a$, let $F^{\mathrm{ref}}_a$ and $F^{\mathrm{cand}}_a$ be the weighted empirical distribution functions of the durations of the reference and candidate episodes of that activity. The first-order Wasserstein distance (see Ramdas et al., 2017) is evaluated exactly on the merged sorted support $x_{(1)}<\dots<x_{(n)}$:

$$W_1(a) = \int \left|F^{\mathrm{ref}}_a(x)-F^{\mathrm{cand}}_a(x)\right|dx = \sum_{k=1}^{n-1}\left|F^{\mathrm{ref}}_a(x_{(k)})-F^{\mathrm{cand}}_a(x_{(k)})\right|\left(x_{(k+1)}-x_{(k)}\right), \qquad W_1^{\max}=\max_{a}W_1(a) \qquad (\mathrm{S14})$$

in minutes, where the maximum runs over activities with at least 30 episodes on each side. Consecutive episodes of the same activity are not merged.

Transitions. The mean number of activity changes per diary is

$$\bar{n} = \frac{\sum_i w_i\,n_i}{\sum_i w_i}, \qquad \Delta\bar{n}=\left|\bar{n}^{\mathrm{ref}}-\bar{n}^{\mathrm{cand}}\right| \qquad (\mathrm{S15})$$

where $n_i$ is the number of consecutive episode pairs in diary $i$ whose activities differ. With $\omega(a,a')$ the weighted share of changes from activity $a$ to activity $a'\neq a$, pooled over diaries, the total variation distance (Levin et al., 2009) is

$$\mathrm{TVD} = \tfrac{1}{2}\sum_{(a,a')}\left|\omega^{\mathrm{ref}}(a,a')-\omega^{\mathrm{cand}}(a,a')\right| \qquad (\mathrm{S16})$$

Daily shape. For activity $a$, let $p_a(s)$ be the weighted share of all time spent in $a$ that falls in ten-minute slot $s = 1,\dots,144$. The Jensen-Shannon divergence (Lin, 1991), in bits, is

$$\mathrm{JSD}(p,q) = H\!\left(\tfrac{p+q}{2}\right)-\tfrac{1}{2}H(p)-\tfrac{1}{2}H(q), \qquad H(p)=-\sum_{s}p_s\log_2 p_s \qquad (\mathrm{S17})$$

with $p=p^{\mathrm{ref}}_a$ and $q=p^{\mathrm{cand}}_a$; it lies between 0 and 1. The reported value is the mean over activities, and the check also bounds the maximum over activities.

Time budget. The time-budget error on this scale is the largest absolute difference over the ten activities:

$$\Delta B_{\max} = \max_{a}\left|\hat{B}'_{\mathrm{ref}}(a)-\hat{B}'_{\mathrm{cand}}(a)\right| \qquad (\mathrm{S18})$$

Here $\hat{B}'(a)$ is the weighted mean number of minutes per day in first-digit activity $a$. This error differs from the MAE of Eq. (5): it compares two sets of diaries rather than a set with a published table, and it takes the worst of ten activities rather than the mean of six groups.

### S13.8 The fictional-country control

The age-band mix of the held-out country's synthetic population is tilted exponentially:

$$\pi_\lambda(j) = \frac{\pi_0(j)\,e^{\lambda j}}{\sum_{j'}\pi_0(j')\,e^{\lambda j'}}, \qquad \lambda_\ell=-\lambda_{\max}+2\lambda_{\max}\,\frac{\ell}{n_\lambda-1},\quad \ell=0,\dots,n_\lambda-1 \qquad (\mathrm{S19})$$

Here $j = 0,\dots,7$ indexes the eight age bands from the youngest, $\pi_0$ is the observed mix, $n_\lambda = 5$ is the number of levels and $\lambda_{\max} = 0.6$. All other prefix fields keep their composition within each band, and every prefix carries a country token absent from training.

The expected budget at level $\ell$ is the average, over the $n_{\mathrm{pre}} = 600$ prefixes drawn at that level, of the donor budget of each prefix's stratum:

$$x_{\ell}(a) = \frac{1}{n_{\mathrm{pre}}}\sum_{j=1}^{n_{\mathrm{pre}}} \hat{B}^{\mathrm{donor}}_{\varsigma_j}(a) \qquad (\mathrm{S20})$$

Here $\varsigma_j$ is the stratum of prefix $j$, and $\hat{B}^{\mathrm{donor}}_{\varsigma}(a)$ is Eq. (S1) over the donor diaries of stratum $\varsigma$. When a stratum holds fewer than five donor diaries, prefix fields are dropped one at a time until at least five are available.

The response of Eq. (6) is fitted by ordinary least squares of the generated budget $y$ on the expected budget $x$, each group centred on its own mean across the five levels before pooling:

$$\hat{\beta} = \frac{\sum x_c\,y_c}{\sum x_c^{2}}, \qquad R^{2} = \frac{\left(\sum x_c\,y_c\right)^{2}}{\sum x_c^{2}\,\sum y_c^{2}}, \qquad x_c=x_{\ell}(a)-\bar{x}(a),\ \ y_c=y_{\ell}(a)-\bar{y}(a) \qquad (\mathrm{S21})$$

Here $y_{\ell}(a)$ is Eq. (S1) over the diaries generated at level $\ell$, and the sums run over the (level, group) points being fitted. Two clauses are scored:

$$\text{direction: } \hat{\beta}_{\mathrm{study}}>0 \ \wedge\ R^2_{\mathrm{study}}\ge 0.80; \qquad \text{amplitude: } \hat{\beta}_{\mathcal{A}\setminus\{\mathrm{leisure}\}}\ge 0.80 \qquad (\mathrm{S22})$$

The direction fit uses the study group alone. The amplitude fit pools the five groups other than leisure, which is excluded because the six groups sum to the whole day and leisure absorbs the remainder.

### S13.9 Country discrimination

Let $\mathrm{MAE}_c$ be the error of Eq. (5) between the generated budget and the published table of country $c$, $c_0$ the held-out country, and $c' = \arg\min_{c\neq c_0}\mathrm{MAE}_c$ the nearest other country. Then

$$\rho = \frac{\mathrm{MAE}_{c'}-\mathrm{MAE}_{c_0}}{\mathrm{MAE}\!\left(B^{\mathrm{pub}}_{c_0},B^{\mathrm{pub}}_{c'}\right)}, \qquad \text{met if } \arg\min_c \mathrm{MAE}_c=c_0 \ \text{ and } \ \rho>0.5 \qquad (\mathrm{S23})$$

where the denominator is the MAE between the two published profiles. A model lying exactly on its own published table scores $\rho = 1$; one equidistant from both tables scores $\rho = 0$.

### S13.10 Markov-chain comparator

Each diary is written as 144 states $a_t$, the first-digit activity in slot $t$. For day type $\tau$ and slot $t = 0,\dots,142$,

$$\mathbb{P}_{\tau,t}(a'\mid a) = \frac{N_{\tau,t}(a\to a')}{\sum_{a''} N_{\tau,t}(a\to a'')}, \qquad \text{or } \ \mathbb{P}_{\tau,t+1}(a')=\frac{N_{\tau,t+1}(a')}{\sum_{a''} N_{\tau,t+1}(a'')} \ \text{ if state } a \text{ is unseen at } t \qquad (\mathrm{S24})$$

Here $N_{\tau,t}(a\to a')$ is the unweighted count of training diaries in state $a$ at slot $t$ and state $a'$ at slot $t+1$, and $N_{\tau,t+1}(a')$ the count in state $a'$ at slot $t+1$. The first state is drawn from the distribution at slot 0. The construction follows the first-order time-inhomogeneous chain of Richardson et al. (2008), whose states are numbers of active occupants rather than activities.

### S13.11 Privacy audit

The score of a record is the mean negative log-likelihood of its diary body under a model $\theta$:

$$\mathcal{L}_\theta(i) = -\frac{1}{|\mathcal{T}_i|}\sum_{t\in\mathcal{T}_i}\log p_\theta\!\left(o_{i,t}\mid o_{i,<t}\right), \qquad s^{\mathrm{loss}}_i=-\mathcal{L}_{\mathrm{tuned}}(i) \qquad (\mathrm{S25})$$

Here $\mathcal{T}_i$ is the set of body-token positions of record $i$ (the prefix is excluded) and $o_{i,t}$ its $t$-th token. Members are training-split diaries of the training countries, and non-members are their held-back split, in the membership-inference setting of Shokri et al. (2017).

The reference-calibrated score subtracts the same record's loss under the untuned backbone:

$$s^{\mathrm{ref}}_i = \mathcal{L}_{\mathrm{base}}(i)-\mathcal{L}_{\mathrm{tuned}}(i) \qquad (\mathrm{S26})$$

where the base model is the pretrained backbone at the revision the adapter was trained from. The area under the receiver operating characteristic curve is computed from ranks:

$$\mathrm{AUC} = \frac{R_1-\tfrac{1}{2}n_1(n_1+1)}{n_1\,n_0} \qquad (\mathrm{S27})$$

Here $R_1$ is the sum of the mid-ranks of the $n_1$ member scores among all $n_1+n_0$ scores, and $n_0$ is the number of non-members. The true-positive rate at a false-positive rate of 0.1 % is

$$\mathrm{TPR}_{0.001} = \frac{1}{n_1}\sum_{i\in\mathrm{mem}}\mathbb{1}\!\left[s_i>\vartheta\right], \qquad \vartheta=\text{the }k\text{-th largest non-member score},\ k=\lfloor 0.001\,n_0\rfloor \qquad (\mathrm{S28})$$

and is not defined when $k<1$. The perplexity-gap control is

$$G_{\mathrm{PPL}} = \frac{\left|\mathrm{PPL}_{\mathrm{non}}-\mathrm{PPL}_{\mathrm{mem}}\right|}{\mathrm{PPL}_{\mathrm{mem}}}, \qquad \mathrm{PPL}_{\mathrm{mem}}=\exp\!\Big(\tfrac{1}{n_1}\sum_{i\in\mathrm{mem}} \mathcal{L}_{\mathrm{tuned}}(i)\Big) \qquad (\mathrm{S29})$$

with $\mathrm{PPL}_{\mathrm{non}}$ defined in the same way over the $n_0$ non-members; the control is met below 0.05.

Distance to closest record. Each diary is written as its 144 ten-minute primary activity codes $z_i(s)$. For a generated diary $i$ and a reference set $\mathcal{D}$,

$$d(i,j)=\frac{1}{144}\sum_{s=1}^{144}\mathbb{1}\!\left[z_i(s)\ne z_j(s)\right], \qquad \mathrm{DCR}_i=\min_{j\in\mathcal{D}}d(i,j), \qquad \mathrm{NNDR}_i=\frac{d_{(1)}(i)}{d_{(2)}(i)} \qquad (\mathrm{S30})$$

where $d_{(1)}$ and $d_{(2)}$ are the smallest and second-smallest distances ($\mathrm{NNDR}_i=1$ if $d_{(2)}=0$). Location, secondary activity and co-presence are not part of the distance. The check is not met if any DCR is zero, or if more than 0.1 % of records have an NNDR below 0.33. DCR and NNDR are used with a holdout set by Platzer and Reutterer (2021).

The memorisation clause compares the median DCR to the held-back split with a size-matched distribution for the training split:

$$\text{not met if } \ \operatorname{med}\!\left(\mathrm{DCR}^{\mathrm{test}}\right) > \mathcal{Q}_{0.975}\left\{\operatorname{med}\!\left(\mathrm{DCR}^{\mathrm{train}}_{(j)}\right)\right\}_{j=1}^{200} \qquad (\mathrm{S31})$$

Here $\mathrm{DCR}^{\mathrm{train}}_{(j)}$ is computed against the $j$-th random subset of the training split, drawn without replacement at the size of the held-back split, and $\mathcal{Q}_{0.975}$ is the 0.975 quantile, taken as an order statistic of the 200 subset medians.

### S13.12 Decoding neutrality

With $\bar{d}_k$ the mean minutes per diary in three-digit activity code $k$,

$$\Delta_{\mathrm{dec}} = \max_{k}\left|\bar{d}^{\,\mathrm{con}}_k-\bar{d}^{\,\mathrm{val}}_k\right|, \qquad \text{met if } \Delta_{\mathrm{dec}}\le 5.0 \qquad (\mathrm{S32})$$

in minutes per day, where con denotes the diaries generated under the grammar and val the structurally valid subset of the diaries generated without it.

### S13.13 Activity-triggered appliances

Eligibility. Dwelling $d$ is eligible for appliance $k$ in minute $t$ if at least one member is an active occupant whose primary activity is mapped to the appliance's CREST activity profile. An active occupant is at home, with a primary activity other than codes 011 and 012, which count as present but not active:

$$\mathcal{E}_{d,k}(t)=\max_{i\in d}\ \mathbb{1}\!\left[\text{member } i \text{ active at } t\right]\mathbb{1}\!\left[c_{i,t}\in\mathcal{C}_k\right], \qquad E_k=\frac{1}{N_{\mathrm{dw}}}\sum_{d}\sum_{t\in\text{year}}\mathcal{E}_{d,k}(t) \qquad (\mathrm{S33})$$

Here $c_{i,t}$ is member $i$'s primary activity code in minute $t$, $\mathcal{C}_k$ the set of codes mapped to the profile of appliance $k$, and $E_k$ the mean number of eligible minutes per dwelling-year over all $N_{\mathrm{dw}}$ dwellings. For the active-occupancy profile every active minute is eligible, and for cold appliances every minute is. The appliance states (off, running, restart delay) follow the CREST model (Richardson et al., 2010).

Start probability. In each eligible minute an idle appliance starts with a constant probability $h_k$. Its starting value $h^{(0)}_k$ is Eq. (4) with $C = C_k$, $E = E_k$, $L = L_k$ and $D = D_k$, where 525,600 is the number of minutes in a year. A non-positive denominator, or $h^{(0)}_k \ge 1$, stops the run. Calibrating a start probability to a published annual count follows Richardson et al. (2010, Section 2.7); Eq. (4) applies this idea to minute-level diary eligibility. The probability is then rescaled until the stock reproduces the published count:

$$h^{(n+1)}_k=\min\!\left(0.999,\ \frac{h^{(n)}_k}{\varphi^{(n)}_k}\right), \qquad \varphi^{(n)}_k=\frac{\hat{C}^{(n)}_k}{C_k}, \qquad \text{until } \max_k\left|\varphi^{(n)}_k-1\right|\le 0.02 \ \text{ or } n=6 \qquad (\mathrm{S34})$$

Here $\hat{C}^{(n)}_k$ is the simulated mean number of cycles per owning dwelling-year at pass $n$. An appliance whose ratio changes by less than 0.01 between passes while below 0.98 is held fixed and reported as saturated, and appliances with $C_k < 0.5$ are excluded.

The number of eligible minutes skipped before the next start is drawn as

$$K=\left\lfloor \frac{\ln(1-u)}{\ln(1-h_k)}\right\rfloor, \qquad u\sim\mathcal{U}(0,1) \qquad (\mathrm{S35})$$

which is the geometric waiting time of a per-minute Bernoulli draw with probability $h_k$. A started cycle runs for

$$L^{\mathrm{run}}=\begin{cases}\max\!\left(1,\operatorname{round}\,\mathcal{N}\!\left(L_k,(L_k/10)^2\right)\right), & k \text{ with a normally distributed cycle length},\\ \max\!\left(1,\operatorname{round}\!\left(70\,(-\ln(1-u))^{1.1}\right)\right), & k \text{ a television},\\ L_k, & \text{otherwise} \end{cases} \qquad (\mathrm{S36})$$

minutes. It runs to completion after the triggering activity ends, and pauses while no occupant is active, except for cold appliances, laundry and a few custom appliances.

Peak hour. Let $P_d(j,t)$ be the electricity demand of dwelling $d$ on day $j$ in clock hour $t$, as mean power over the hour after the 04:00 diary origin is rotated to midnight. Then

$$\bar{P}(t)=\frac{1}{N_{\mathrm{dw}}\,N_{\mathrm{day}}}\sum_{j}\sum_{d}P_d(j,t), \qquad t^{*}=\arg\max_{t}\bar{P}(t) \qquad (\mathrm{S37})$$

where $t^{*}$ is reported as the hour beginning and $\bar{P}(t^{*})$ as the peak power per dwelling, in W.

Load-shape agreement with the reference profile is the squared Pearson correlation over the 24 hourly values:

$$R^2_{\mathrm{LS}}=\frac{\left[\sum_t\left(\bar{P}(t)-\langle\bar{P}\rangle\right)\left(P^{\mathrm{ref}}(t)-\langle P^{\mathrm{ref}}\rangle\right)\right]^2}{\sum_t\left(\bar{P}(t)-\langle\bar{P}\rangle\right)^2\,\sum_t\left(P^{\mathrm{ref}}(t)-\langle P^{\mathrm{ref}}\rangle\right)^2} \qquad (\mathrm{S38})$$

Here $P^{\mathrm{ref}}$ is the expected diurnal appliance power built from the published CREST activity statistics and appliance parameters (Richardson et al., 2010), and angle brackets denote 24-hour means. The check requires $R^2_{\mathrm{LS}}\ge 0.85$.

### S13.14 Domestic hot water

For draw category $j$ (short, medium, bath, shower), the start probability per eligible minute is

$$h_j=\frac{N_j}{E_j-N_j\left(L_j-1\right)}, \qquad N_j=365\,\nu_j\,\frac{V_{\mathrm{day}}}{200} \qquad (\mathrm{S39})$$

Here $\nu_j$ is the published number of draws per day, $L_j$ the draw duration in minutes, $E_j$ the mean eligible minutes per dwelling-year for the category's driver activities, and $V_{\mathrm{day}}$ the daily volume per dwelling in litres (200 litres in Jordan and Vajen, 2001, Table 1). The flow of each draw is

$$\dot{V}=\max\!\left(0.2,\ 0.2\,\operatorname{round}\!\left(\dot{V}'/0.2\right)\right), \qquad \dot{V}'\sim\mathcal{N}\!\left(\mu_j,\ (0.2\,\sigma_j)^2\right) \qquad (\mathrm{S40})$$

in litres per minute, where $\mu_j$ is the mean flow and $\sigma_j = 2$ the spread of Jordan and Vajen (2001, Table 1). The spread is read in units of the 0.2 l/min flow step, so the standard deviation is 0.4 l/min.

### S13.15 Occupancy-driven internal gains and the heating response

The presence signal of a household of $n_{\mathrm{hh}}$ members in hour $t$ is

$$g(t)=\frac{1}{n_{\mathrm{hh}}}\sum_{i=1}^{n_{\mathrm{hh}}}\frac{1}{60}\sum_{t'\in t}\mathbb{1}\!\left[\text{member } i \text{ present in minute } t'\right] \qquad (\mathrm{S41})$$

where a member is present when at home and not in an outdoor activity at home, so $g(t)$ lies between 0 and 1. The internal gain is then Eq. (3), with $\overline{g}$ the mean of $g(t)$ over the 8,760 hours of the year. The value $\bar{\phi} = 3.0$ W/m² is the TABULA boundary condition of the European comparison rows EU.SUH and EU.MUH (IWU, n.d.); the national rows differ.

For archetype cell $k$ and level $f$, let $Q_{k,f,\eta}$ be the annual peak hourly heating demand per unit floor area when the cell is driven by household $\eta$, and $\bar{Q}_{k,f}$ its mean over the $N_{\mathrm{hh}}$ households of the cell's ensemble. Then

$$\Delta Q_{k,f}=100\,\frac{\bar{Q}_{k,f}-\bar{Q}_{k,0}}{\bar{Q}_{k,0}}, \qquad \mathrm{CV}_{k,f}=100\,\frac{\mathrm{sd}_\eta\!\left(Q_{k,f,\eta}\right)}{\bar{Q}_{k,f}} \qquad (\mathrm{S42})$$

in per cent. The peak effect of a fold is the median of $\Delta Q_{k,1}$ over cells, the spread between diaries is the median of $\mathrm{CV}_{k,1}$ over cells, and the annual effect is defined in the same way on annual heating energy per unit floor area.

### S13.16 Fine-tuning

Each adapted weight matrix is

$$W = W_0 + \gamma\,\mathbf{B}\mathbf{A}, \qquad \mathbf{B}\in\mathbb{R}^{d_{\mathrm{out}}\times r},\ \mathbf{A}\in\mathbb{R}^{r\times d_{\mathrm{in}}},\ \gamma=\frac{\alpha}{\sqrt{r}} \qquad (\mathrm{S43})$$

Here $W_0\in\mathbb{R}^{d_{\mathrm{out}}\times d_{\mathrm{in}}}$ is the frozen pretrained weight, $\mathbf{A}$ and $\mathbf{B}$ are the only trained matrices, $r = 32$ is the rank and $\alpha = 64$ the scaling constant, so $\gamma \approx 11.3$ under rank-stabilised scaling; the original form uses $\alpha/r$. Adapters are applied to the seven linear projections of every block, with dropout 0.05 on the adapter input (Hu et al., 2022).

The training objective is the next-token cross-entropy over diary-body tokens only:

$$\mathcal{L}(\theta)=-\frac{1}{\sum_i|\mathcal{T}_i|}\sum_i\sum_{t\in\mathcal{T}_i}\log p_\theta\!\left(o_{i,t}\mid o_{i,<t}\right) \qquad (\mathrm{S44})$$

Here the sums run over the records of a batch and $\mathcal{T}_i$ is as in Eq. (S25); prefix and padding positions carry no loss.

---

## References cited only in the supplementary material

The supplementary material cites Eurostat (2009), Eurostat (2019) and Fuentes et al. (2018); full entries are
in the reference list of the main paper.
