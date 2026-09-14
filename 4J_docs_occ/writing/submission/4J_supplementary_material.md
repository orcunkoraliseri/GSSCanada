# Supplementary material

Companion to *Beaten by Real Diaries: A Pre-Registered Leave-One-Country-Out Test of a Fine-Tuned
Language Model for Cross-National Occupancy Generation*.

Two things are given here that the main text refers to and does not restate: the registered check set with
each band's provenance marked, and the model card. A third section records the threshold-provenance audit
in full, because three of this study's reported failures are failures of a band rather than of a model and
a reader is entitled to see which bands carry external authority and which do not.

---

## S1. The registered check set

Bands are marked **P** where the threshold comes from a published external source, **C** where it was
chosen by this project and registered before use, and **H** where it is a heuristic with no external
authority. The provenance mark is part of the registration and was not assigned after the results were
seen.

### S1.1 Corpus, harmonisation and serialisation

| Check | What it scores | Band | Prov. | Verdict |
|---|---|---|---|---|
| Acquisition, 16 checks | delivery integrity, codebook coverage, weight bounds, manifest completeness | various | C | Spain 15 PASS; Italy 1 FAIL; Britain 1 FAIL |
| Italy source URL | a per-file source URL exists in the delivery | present | C | FAIL, recorded as not found rather than fabricated |
| Britain activity labels | every delivered activity code is labelled | complete | C | FAIL, one code labelled nowhere in the delivery |
| Harmonisation, 18 checks | alphabet closure, episode conservation, slot tiling, unknown-band prevalence | various | C | 16 PASS, 1 FAIL, 1 NOT CHECKED |
| Unknown-band escalation | one country's unknown share against another's | 10x ratio | H | FAIL; the clause fires unconditionally against a zero share |
| National table agreement | harmonised budgets against a published national table | -- | -- | NOT CHECKED; no independent published table is held |
| Serialisation, 20 checks | round-trip fidelity, token length, terminator presence, stratum coverage | various | C | 19 of 20 PASS, coverage clause PASS |
| Sequence length | median, 99th percentile, maximum | 300 / 700 / 1200 tokens | C | PASS at 256 / 632 / 1178 |
| Stratum completeness | no stratum coded unknown | zero | C | FAIL on Britain by ruling, 551 diaries, not imputed and not dropped |

### S1.2 Training

| Check | What it scores | Band | Prov. | Verdict |
|---|---|---|---|---|
| Within-stratum variance ratio | generated against real dispersion inside a stratum | 0.80 to 1.25 | C | FAIL, 3 of 3; **resolution-limited**, see S1.6 |
| Shuffled-prefix cross-entropy | rise when the prefix is permuted | at least 0.15 nats/token | **H, unsourced** | FAIL, 7 of 7; measured 0.068 to 0.106 |
| Adapter merge drift | maximum logit difference, merged against unmerged | below 1e-4 | H | FAIL, 4 of 4; measured 2.7e-4 to 7.3e-4 |
| Loss masking | prompt and pad positions carry the ignore label | 100 per cent | C | PASS |
| Held-in probe loss | final checkpoint within 5 per cent of its own best | 5 per cent | C | PASS on the reported backbone, FAIL on the alternative family |
| Within-stratum shuffle | cross-entropy rise and mutual-information drop, conjoined | 0.15 nats and 0.10 | H | FAIL; **no decision record, see S1.6** |
| Fold isolation | held-out-country records loaded during training | exactly zero | C | PASS, every run |
| Pre-registration precedence | live hash of the frozen file against its registered value | exact match | C | PASS, every run |

### S1.3 Conditioning and population linkage

| Check | What it scores | Band | Prov. | Verdict |
|---|---|---|---|---|
| Raking convergence | worst absolute marginal deviation after fitting | below 1e-13 | C | PASS |
| Marginal provenance | both sides of any comparison carry the same marginal source | identical | C | PASS, enforced as a refusal |
| Temperature calibration reporting | the chosen temperature and its sensitivity are reported | reported | C | PASS |
| Temperature calibration sensitivity | entropy step exceeds seed-to-seed re-run noise | ratio above 1 | C | **FAIL on Spain (0.51) and Britain (0.99), PASS on Italy (1.29)** |

Thirty-six gate-fold verdicts, 34 PASS and 2 FAIL. This stage closes at four of five definition-of-done
items with the fifth taken as a declared exception. It is never to be written as complete, and the board is
never to be reported as 36 of 36.

### S1.4 Transfer

| Check | What it scores | Band | Prov. | Verdict |
|---|---|---|---|---|
| **Transfer bar** | model time-budget error against the raked-donor null | positive margin | **C, pre-registered** | **FAIL, 9 of 9** |
| Single-donor nulls | each donor country's own population as a comparison | positive margin | C | reported, six populations |
| Pooled-average null | the cross-country pooled average, demoted to secondary | positive margin | C | reported |
| Budget agreement | level-1 budget against published tables | MAPE at or below 15 per cent | P | FAIL, 9 of 9 |
| Frozen failure criteria | conjunction of three pre-declared conditions | any triggers | C | FAIL, 9 of 9; coverage clause FAIL **for vacuity** |
| Held-in regression | training-country prefixes clear the same bar, and no forgetting | 15 per cent | P | FAIL, 6 of 6 on clause 1 |
| Fictional country, steering | movement in the specified direction | R-squared at least 0.80 | C | PASS, **pilot arm only** |
| Fictional country, amplitude | movement of the specified size | slope at least 0.80 | C | FAIL, 3 of 3 |
| Joint structure, dwell time | Wasserstein distance of dwell-time distributions | 10.0 min | C | FAIL, 50.13 to 66.57 |
| Joint structure, transitions | total variation of the transition matrix | 0.050 | C | FAIL, 0.1623 to 0.2344 |
| Joint structure, diurnal | mean Jensen-Shannon divergence | 0.015 | C | FAIL, 0.0690 to 0.1189 |
| Joint structure, budget | time-budget error | 8.0 min | C | FAIL, 38.26 to 68.67 |
| Transition rate | transitions per day error | 1.50 | C | comparator PASSES at 0.264 |
| Country discrimination | nearer its own published table than any other, by margin | relative margin above 0.5 | C | FAIL, 9 of 9 |
| Hour-support constancy | completeness invariant of the binning | complete | C | **built, self-tested, never scored against model output** |

### S1.5 Privacy

| Check | What it scores | Band | Prov. | Verdict |
|---|---|---|---|---|
| Loss-based membership inference | area under the curve, 2,000 per class | at most 0.65 | C | **FAIL, 0.6645**, base floor 0.4886 |
| Reference-based membership inference | against the untuned public base | at most 0.75 | C | PASS, 0.5594 |
| Prefix-prompted extraction | exact matches on strata with fewer than five records | zero | C | PASS, 0 of 103 |
| Distance to closest record | released synthetic set against training records | see text | C | PASS Spain, PASS Italy, **FAIL Britain** |
| Perplexity gap | control, **not independent** | at most 0.05 | C | FAIL, 0.0570; also fails at 0.0511 on a permuted adapter |
| Memorisation ceiling | random-label-permutation control | -- | -- | **INCONCLUSIVE AS A CEILING**, 0.6496 |

This board ships two registered failures and one partial. It is never to be described as a passing audit
and never as four of four.

### S1.6 Three bands that failed for reasons that are not about the model

Three of the training-stage failures are properties of their own checks, and this study reports them as
such rather than as model defects. The distinction is load-bearing for the main text's claim that the
model conditions and still loses.

**The variance-ratio band is narrower than its own noise floor.** A probe on frozen weights over five
seeds per fold returns a seed-alone spread of 0.529, 0.658 and 0.385. The acceptance band is 0.45 wide in
total. The check cannot separate a model effect from seed noise at the sample size it runs at, and it
ships marked resolution-limited. One apparent pass on one fold was struck as a one-in-five-seed artefact
rather than kept, which is the direction that costs this study rather than helps it.

**The cross-entropy-rise bar has no recorded provenance.** It is the only band in its group with none. The
measured rise is 0.068 to 0.106 nats per token, the sign is correct in every run, and the untrained
backbone's rise on the same construction is 0.0001 to 0.0011, so the fine-tune bought between 84 and 1,062
times the untrained baseline's conditioning response. The check fails against a bar that nothing
justifies, and it is reported failing with that stated rather than adjusted.

**The merge-drift band is satisfiable only by an adapter that learned nothing.** Scaling the adapter down
by a factor of 1,000 does not bring the drift inside the band; it plateaus an order of magnitude above it,
and only a zero-scale adapter passes. The drift is behaviourally real rather than numerical noise: in the
shipping precision, merged and unmerged adapters produce different diaries in 39 to 46 of 48 cases, 81 to
96 per cent, while the unmerged-against-unmerged control is clean in 48 of 48 in every fold. A live
consequence of this remains open and is recorded in the main text: no intermediate artefact records which
of the two produced it.

**One check ships failing without ever having been adjudicated.** Its shuffle key omits one of the six
prefix fields, so it can change at most one field, and for 55 to 64 per cent of diaries it changes nothing
at all, while being required to move cross-entropy as much as a full permutation would. Its measured rise
is 0.002 to 0.0069. It carries no decision record and is reported as unfinished.

---

## S2. Model card

| | |
|---|---|
| Backbone, reported model | open-weight 7.30 B decoder, pinned revision |
| Backbone, pilot arm | 1.48 B, same family, pinned revision |
| Backbone, comparison arm | 7 B, different family, pinned revision, one fold only |
| Adaptation | low-rank adapter, rank 32, scaling 64, dropout 0.05, rank-stabilised |
| Target modules | all seven linear projections per block |
| Trainable parameters | 79,953,920 (1.0837 per cent of 7,377,965,056) |
| Objective | next-token cross-entropy, completion-only masking, **unweighted** |
| Epochs | 3 |
| Batch size / gradient accumulation | 2 / 8 |
| Learning rate | 1e-4, constant |
| Schedule / warmup | **none applied; reported as what the code does, not as a design choice** |
| Precision | bfloat16 |
| Maximum sequence length | 1,280 tokens |
| Seed | one fixed seed per training arm; no multi-seed training replication |
| Hardware | one A100 partition |
| Wall time | approximately 10 to 12 hours per fold |
| Checkpoint selection | none; the final checkpoint of the last epoch is the reported model |
| Tokeniser | the backbone's own vocabulary, no tokens added |
| Decoding | grammar-constrained; temperature 1.30 / 1.10 / 1.20 by fold; nucleus sampling disabled |

**One documentation defect is disclosed rather than corrected.** The manifest shipped with the full
fine-tune control describes a low-rank adapter run, while that job's own log records a full fine-tune with
no adapter. The manifest was deliberately not edited; a correction sidecar sits beside it, and the main
text quotes the sidecar. Separately, the comparison table in the training record labels the reported
model's column with the wrong backbone family, while the manifest and run configuration identify it
correctly. Both are printed as found.

---

## S3. The conditioning prefix

Six fields, frozen before training, reduced from an original nine.

| Field | Values | Source of the marginal used to build the synthetic population |
|---|---|---|
| country | 3 | -- |
| age band | 8 | national census age table |
| sex | 2 | national census sex table |
| household type | 6 in the alphabet, 5 raked | national census household table; the European census hub for Italy |
| economic status | 7 in the alphabet, **5 raked for Spain** | national census economic-activity table; on-demand microdata for Spain |
| day type | 3 | **no published marginal in any country; assigned exogenously at 5/7, 1/7, 1/7** |

Iterative proportional fitting runs over the four-way joint of age, sex, household type and economic
status. Expansion to 100,000 persons per country is by deterministic largest-remainder integerisation, so
the synthetic population carries no sampling seed. The output is a person-level table; households are not
assembled, and no result in the paper is a household-level claim.

---

## S4. Campaign sizes

| Campaign | Composition | Total |
|---|---|---|
| Generation, per fold | 5,200 constrained + 5,200 unconstrained | 10,400 per fold |
| Held-in regression | 600 x 6 configurations | 3,600 |
| Fictional-country control | 600 x 5 levels x 3 folds | 9,000 |
| Archetype simulation | (88 archetypes x 5 levels x 10 diaries) + 440 re-runs | 4,048 |
| Day-chaining experiment | 3 folds x 6 rule points x 5 seeds x 100 dwellings | 9,000 |
| Calendar probe | -- | 60 |
| **Archetype campaign total** | executed **twice**, see §3.8 | **13,108** |
| Observed stock, reported campaign | Madrid 11,510 / Bologna 11,710 / London 12,070 | **35,290 cells**, 3,529 buildings, 31,591 dwellings |
| Observed stock, earlier campaign | core-era layout, archived, not reported | 410 cells |
| Stock-scale end use | London 7,602 flats in 1,200 buildings; Bologna 29,902 flats in 1,126 buildings | 2 folds |

---

## S5. What the reader should not infer from this work

Collected here because each was written after a specific near-miss during the study, and several were
written after the wrong sentence had already been drafted once.

Every energy intensity in this work is heating-only and may not be compared to a whole-building figure or
to a measured total. No cross-country comparison of absolute demand is safe at the ten per cent level; the
weather file alone is worth five to eleven per cent and its sign differs by country. Absolute intensities
from the archetype campaign and from the observed-stock campaign are never placed side by side and never
differenced.

No per-dwelling prediction is made at any scale. The stock-scale confirmations raise confidence in
aggregates and do nothing for an individual household.

The backbone comparison is two points and is not a scaling curve. The full fine-tune is a ceiling run and
no claim is made that it changed dispersion in either direction. The alternative-family arm is single-fold.

The privacy board is not a passing audit. The memorisation control does not bound what it was built to
bound. The perplexity gap is not independent confirmation.

No scored result is claimed from the larger observed-stock campaign; its board was deliberately not read.

The third digit of the activity alphabet is justified on microdata fidelity and not on published
distinguishing power, where it buys exactly one distinction.

A verified reference is not verified content. The review that is the true source of the hot-water band
resolves correctly against CrossRef and has not been read by the authors.
