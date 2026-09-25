# Table A1 - Model card: the three-head conditional Transformer

<!-- APPARATUS NOTE 2026-08-11: the "Source in the project repository" column and its five explanatory
blocks were removed from this card on the author's instruction ("n'ajoute pas des textes d'explanation
pour des tableux ou des figures dans appendix"). They were file-and-line pointers into this repository,
which no reader can resolve, plus four disclosure notes and one essay. NOTHING DISCLOSED WAS DELETED
FROM THE PAPER, and that was checked disclosure by disclosure before cutting: the conditioning-width
drift and the frozen-versus-measured positive weight are properties of the design and are stated in the
rows below; the decode-temperature change is stated in the Decoding rows; the checkpoint-selection
deviation, which is the one that matters, is stated in Chapter 3 in full prose including the 0.0218 F1
gap, the four-of-five seed disagreement and the reason for not re-selecting. The predecessor is at
writing/archive/2026-08-11_pre_paper_pass/SI_Table_A1_A2.md. -->

### A1.1 Architecture

| Component | Specification |
|---|---|
| Backbone | Shared multi-head Transformer encoder-decoder, kept from the two-channel stage with targeted upgrades rather than replaced |
| Encoder | 6 layers, model width 256, 8 attention heads, approximately 29M parameters |
| Activity arm | Autoregressive decoder, 14 activity classes, 48 half-hour slots per day |
| Head 1 | Residential presence, unchanged from the earlier stages |
| Head 2 | Office presence, unchanged from the two-channel stage |
| Head 3 | Retail presence, new in this study; mirrors Head 2 off the same fused representation, with the activity arm's gradient barrier untouched |
| Co-presence head | 9-channel co-presence, unmodified by the retail addition |

### A1.2 Conditioning vector (width 120)

| Covariate group | Encoding |
|---|---|
| Demographics | One embedding per categorical field, concatenated and projected; 14 census fields plus the occupation, telework and work-schedule set |
| Day-type stratum | Embedding over three strata; drives diurnal shape |
| Cycle year | Continuous projection, never categorical, so the model extrapolates to an unseen 2030 |
| Collection mode | Low-capacity embedding, deliberately too small to leak physical signal |
| Retail | No retail-specific conditioning is added: retail presence is population-behavioural, not occupation-gated |

The width grew from 119 to 120 between the two stages because one demographic field gained a
missing-value category, an independent data-pipeline fix rather than part of the retail addition.

### A1.3 Training regimen

| Item | Value |
|---|---|
| Loss weights, residential : office : retail | 1.0 : 0.5 : 0.3 |
| Scalarization | Fixed-weight; dynamic weighters rejected as unstable on a task with about 2 % positives |
| Gradient surgery | PCGrad, pairwise across the three tasks, joint phase only |
| Class imbalance, retail | Positive-class weight 49 |
| Inference logit shift | $-\ln 49 \approx -3.89$, applied at decode only, never during training |
| Warmup phase | 5 epochs, Head 3 only trainable, learning rate 1e-3 |
| Joint phase | 15 epochs, all parameters trainable, learning rate 1e-4, PCGrad on, early stopping on the gate set |
| Dropout | 0.1, attention and residual only, never on output projections |
| Weight decay | 1e-4 |
| Label smoothing | Disabled; it distorts calibration on this task |
| Diary augmentation | None |
| Batch composition | Stratified 50 % weekday, 25 % Saturday, 25 % Sunday, inverse-cycle-frequency weighted |
| Survey weights | Applied inside the loss, clipped at the 99th percentile |
| Selection rule | Gate-first, then maximize retail F1 among survivors; no composite score. The shipped checkpoint deviates from this rule, as disclosed in §3.2 |
| Shipped scorecard | 147 PASS / 18 WARN / 1 FAIL; the single FAIL is a day-type ordering check pre-existing in the two-channel baseline, with no new failure introduced |

The design value of the positive-class weight is 49; the training split's measured positive rate implies
50.1056. The shipped model trains on 49.

### A1.4 Decoding

| Item | Value |
|---|---|
| Sampling | Temperature 0.7 with nucleus sampling at 0.9; the two-channel stage used 0.8 with no nucleus |
| Minimum dwell | At least 2 slots, 60 minutes, for work and retail events, applied after the exclusivity projection |
| Decision thresholds | 0.50 residential, 0.40 office, 0.15 retail, derived on validation |
| Exclusivity | Threshold-normalized argmax: a slot over threshold on more than one channel keeps only the channel with the largest threshold-normalized probability |
| Impossible-state rate | At most 0.5 % on raw output; 0 % on the injected schedules by construction |
| Rejected alternative | A categorical location head, which crushes the 2 % retail class and couples calibration |

---

**Table A2.** - AT_RETAIL codebook per GSS cycle.

| GSS cycle | Raw variable | Codes mapped to the unified shopping location | Status |
|---|---|---|---|
| 2005 (C19) | PLACE | 06 grocery and 07 other store or mall | confirmed |
| 2010 (C24) | PLACE | 06 and 07 | confirmed |
| 2015 (C29) | LOCATION | 306 | confirmed |
| 2022 (GSSP) | LOCATION | 3306 | confirmed |

<!-- BUILD NOTE RESOLVED 2026-08-11: the `# Table A2` heading was replaced with a bold caption line, which the assembler does not strip, and Chapter 3 now cites Table A2 at the AT_RETAIL derivation. Original note follows. TABLE A2 SHIPPED UNLABELLED AND UNCITED, and this was a build-mechanism defect, not a content one. This file carries TWO tables under two `# ` headings, but the conclusion chapter had ONE placeholder for it, and `assemble_3J.py`'s `inline_table()` strips every `^# ` line. So A1's label is supplied by the placeholder and A2's is deleted: everything from the AT_RETAIL codebook down ships as an unlabelled continuation of the model card, under no number, and no chapter cites "Table A2" anywhere. Verified in the built docx: "Table A1" appears 3 times, "Table A2" and "AT_RETAIL codebook" zero times, while A2's BODY is present in full. f4's C7 is structurally blind to this: it checks that every caption it FINDS is cited in prose, and this exhibit's caption is destroyed before C7 ever sees the document, so 22/22 passes while a 23rd exhibit rides along unnumbered. -->
In 2005 and 2010 two source codes are combined into one unified value; in 2015 and 2022 the single code
is already a merged grocery and general-merchandise bucket at the source. Grocery and general
merchandise are therefore not separable in the two later cycles, which is why the retail channel uses a
single retail archetype.

---

## Sources

- `Leg3_4-split/Step4_docs/3rdJ_04_augmentationGSS_4split.md` (Deltas A-I, CONTRACT section) and
  `3rdJ_04B_model_4split.py` (`PROD_CONFIG`, lines 86-92) - every architecture, conditioning, training
  and decoding value in Table A1, checked against the doc or the code rather than copied from the brief.
- `3rdJ_04_augmentationGSS_4split.md:298` - the `d_cond` 119 to 120 drift and its cause.
- `3rdJ_04_augmentationGSS_4split.md:274` - frozen `pos_weight` 49 vs measured 50.1056
  (`retail_pos_weight` in `step4_feature_config.json`).
- `3rdJ_04_augmentationGSS_4split.md:51` - shipped validator scorecard 147 PASS / 18 WARN / 1 FAIL.
- `3rdJ_04_augmentationGSS_4split.md:159-204` (`V3-H1`) and `3rdJ_04D_train_4split.py:881`/`:499` -
  the checkpoint-selection deviation, its composite `val_score`, the 4-of-5 seed disagreement, the
  0.0218 F1 gap and the three reopen triggers. Stated in Chapter 3 prose.
- `dr_L3-11`, `dr_L3-12`, `dr_L3-13` - the three design playbooks behind the backbone verdict, the
  output representation and the training regimen.
- `Leg3_4-split/Step2_docs/3rdJ_02_harmonizeGSS_4split.md` Delta A (`:34-43`), confirmed against
  `../../investigation/00_GSS_split_suitability_audit.md` §2 - the Table A2 codebook, all four cycles.

No em dashes or en dashes.
