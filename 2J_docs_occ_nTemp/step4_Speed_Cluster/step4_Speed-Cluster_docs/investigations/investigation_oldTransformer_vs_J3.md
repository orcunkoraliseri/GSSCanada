# Old Transformer Pipeline vs J3 — Head-to-Head

## Summary

**The question.** J3 plateaus at composite 0.6355, edge of two gates (Spouse Δ=2.03 vs 2.0; act_JS=0.0191 vs 0.022). Six J5 variants + the J3-HPT bundle haven't beaten it. The user observed the *old* Transformer pipeline performed strongly on what felt like a harder problem. Is J3's architecture wrong?

**The answer.** Probably partly, yes — but the metric framing matters too.

**Key findings.**
1. **The two models are not solving the same problem.** Old does same-day classification (predict the diary you saw, scored as per-slot accuracy). J3 does cross-strata generation (synthesize the 2 unobserved DDAY_STRATA per respondent, scored as distributional JS divergence). The "old beat a harder problem" claim is not directly comparable — they were never measured on the same metric.
2. **On the activity axis alone, J3 is doing the same 14-way task at finer time resolution (48 vs 24 slots) with vastly less demographic conditioning per token.** Old broadcasts 24 categorical embeddings + 4 continuous onto *every* slot token. J3 collapses to one `cond_vec` injected only at CLS + 3 cross-attn key/value tokens. Slot-level decisions in J3 must route demographic signal across attention; old had zero routing distance.
3. **9+ demographic fields were dropped** (Kinship, NuclearFamily-*, Citizenship, Internet/Mobile/Car ownership, Home ownership, Room count, EcoSector, JobType). Several are structurally tied to AT_HOME and co-presence (the gates J3 is tight on).
4. **Old had no activity-class re-weighting**; J3 boosts Work ×5, Transit ×3, Social ×2. The boosts induce over-prediction of these classes, which fights act_JS directly.
5. **Old had no pair-based supervision noise.** J3's K=5 demographic-neighbor pairing imposes an irreducible neighbor-disagreement floor on act_JS.
6. **Old's FFN was 10240 wide** (≈30× d_model); J3's is 1536 (4×). Massive expressivity gap on the activity classifier.

**Ranked suspicions for why J3 plateaus** (full detail in §6):

| Rank | Hypothesis | Single-axis experiment | Cost |
|---|---|---|---|
| HIGHEST | Per-slot demographic broadcast was lost in J3 (§6.1) | J3-PSB: concat `cond_vec` to every slot token before `slot_linear` | 1 retrain, code edit |
| HIGH | Demographic schema 9+ fields narrower (§6.2) | J3-DemoWide: audit Step-2 outputs, restore Kinship/NuclearFam/HomeOwn/RoomCount/Internet/Mobile/Car | 1 retrain, 04A edit |
| MEDIUM | `ACTIVITY_BOOSTS=1` prior fights act_JS (§6.3) | J3-NB: `export ACTIVITY_BOOSTS=0`, retrain | 1 retrain, env-var only |
| DIAGNOSTIC ✓ | Cross-strata pair noise is an irreducible floor (§6.4) | **K=5 neighbor-disagreement JS = 0.1888 (measured)** | done |
| LOWER | FFN width 1536 too narrow (§6.5) | Already partly tested by J3-HPT S_hi/S_lo | in-flight |

**Empirical neighbor-floor finding (external diagnostic).** The §6.4 diagnostic has been run: pairwise JS divergence across the K=5 demographic-neighbor diaries is **0.1888**. The supervisory targets contradict each other at JS=0.1888 — the training signal is intrinsically very noisy at the individual-pair level. J3 currently scores `act_JS=0.0191` on the *aggregate* cell-level distributional metric (not the same granularity as the pair-level floor), so the floor does not directly cap J3's reported metric, but it does tell us that the **act_JS axis has limited headroom against a noisy target distribution** — any further compression on act_JS is fighting neighbor disagreement, not model capacity. This re-weights the priorities: experiments aimed at the **AT_HOME and Spouse Δ gates (§6.1, §6.2)** are higher-yield than experiments aimed at act_JS (§6.3).

**Recommended next step (revised).** §6.1 — J3-PSB per-slot demographic broadcast. Targets the actual blocker gates (AT_HOME RMS, Spouse Δ — see §S1 for why binary heads are hardest), expected to help both binary heads and activity simultaneously, and is the architectural change most directly addressing the load-bearing diff vs old. ~5.5 h cluster wall clock, modest code edit in `04B_model_J3.py`. §6.3 (`ACTIVITY_BOOSTS=0`) remains valuable but is demoted to a secondary experiment given the neighbor-floor result.

**What this investigation does NOT settle.** Whether old-pipeline weights, scored on J3's distributional metric on J3's cross-strata generation task, would beat 0.6355. That experiment was never run because the old pipeline was never built to generate unobserved days. The architectural lessons (§6.1, §6.2) can be ported into J-series; the metric-framing lesson cannot be undone.

---

## S1. Why the "easy" binary outputs are actually harder in J3

The user's question: J3 plays a harder generative task than old's predictive task, and old performed well on the activity head. So why is *our* hardest problem in J3 the binary outputs (AT_HOME, co-presence) — which should be the easiest? Activity is 14-way, AT_HOME and co-presence are binary. Cardinality says binary is easier; J3's results say the opposite. This chapter explains the paradox. **None of these are excuses for the architecture — they are concrete reasons to expect AT_HOME / co-presence to be J3's pain point regardless of total task difficulty.**

### S1.1 The 1-channel → 9-channel reduction was lost

Old collapsed *all* co-presence into a single `withNOBODY` binary (`Transformer_pipeline.py:255-257, 558, 1466`). One channel, one binary call per slot. J3 keeps 9 separate channels (Alone, Spouse, Children, parents, otherInFAMs, otherHHs, friends, others, colleagues). Each must be calibrated separately, per slot, per cell. The "binary" framing is misleading — J3 is doing **9 simultaneous binary tasks with cross-channel dependencies** (Alone is mutex with the others; Spouse↔Children are correlated; colleagues is conditional on Work). Old's task is *one* binary call. J3's is 9. The cardinality of the supervision signal is ≈9× larger, not smaller, than activity's 14-way single call.

### S1.2 Activity has an AR decoder; binary heads do not (and AR cuts both ways)

In J3, activity is generated **autoregressively** — slot t's activity sees the (predicted) activity at slot t-1 (`04B_model_J3.py:933-991`). This gives the activity head a built-in temporal smoother: even if encoder routing is weak, the AR causal stream propagates a coherent activity trajectory. AT_HOME and co-presence are **NAT** (non-autoregressive) heads off the Arm-2 fusion (`04B_model_J3.py:995-1024`). They see encoder memory + cond + activity probs *only*, with no autoregressive feedback between slot t and slot t-1 on the binary axis itself. Temporal patterns in AT_HOME ("home → home → home → away → away" runs) must be reconstructed purely from encoder self-attention. Old got around this by not having a generative task at all — it predicted the diary in front of it.

**The AR cascade-of-errors caveat.** AR is not a free win even for activity. Because J3 generates an *unobserved* day, a wrong activity at slot t feeds into slot t+1 and can compound: a wrong "Work" at 8 AM keeps "Work" plausible at 9 AM, 10 AM, ... and indirectly anchors the Arm-2 AT_HOME head toward "away" for the same slots. The old pipeline never had this failure mode — it predicted every slot in parallel against the *observed* diary, with no compounding generative drift. So in J3, AR helps activity get *plausible* trajectories but can hurt the binary heads through indirect coupling via `act_probs` → Arm-2 fusion.

### S1.3 Per-slot demographic loss hurts NAT heads more than AR heads

§6.1's per-slot broadcast loss is **asymmetric** in its damage. The AR decoder can route demographic signal *temporally* through its causal stream — if the model figures out "this respondent is a 35-year-old commuter" at slot 1, that information rides along into slot 2's hidden state. The NAT binary heads cannot do this; each slot's home/cop call is computed in parallel from the encoder memory at that position. So when the encoder fails to route the CLS demographic signal to slot t, the binary head at slot t has *no recourse*. Old's per-slot broadcast made this routing free. J3 made it the encoder's full responsibility — and the binary heads, having no AR fallback, eat the cost first.

### S1.4 The demographic schema dropped exactly the fields binary heads need most

The 9+ fields removed in J3 (Kinship, Nuclear-Family-Profile, Nuclear-Family-Typology, Citizenship, Internet/Mobile/Car ownership, Home ownership, Room count, EcoSector, JobType — see §2 and §6.2) are **structurally tied to AT_HOME and co-presence**, not to activity:
- **Home ownership + Room count + Internet** ⇒ AT_HOME (own-vs-rent and WFH capacity directly predict time at home).
- **Kinship + NuclearFamily-Profile + NuclearFamily-Typology** ⇒ co-presence channels (Spouse / Children / parents / otherInFAMs are *literally* about household composition; without these fields, the model is guessing).
- **Mobile / Car ownership** ⇒ commute structure, which sets the windows where co-presence with friends/colleagues is even possible.

Activity is less demographically anchored — meal times, sleep, leisure follow population-wide diurnal patterns the encoder can pick up from the slot signal itself. The binary heads do not have that luxury.

### S1.5 Imbalanced BCE without `pos_weight` collapses rare channels

Co-presence channels have very different positive rates. Alone and Spouse are common; parents, otherInFAMs, colleagues, friends are rare. Plain BCE-with-logits on a 5%-positive channel rewards "always predict 0" because that already scores 95% accuracy. `pos_weight` is the standard fix; J3 disabled it on 2026-04-22 (`04D_train.py:688-697`) because it destabilized AT_HOME calibration. So rare cop channels train against an unweighted BCE and the model under-predicts them — which directly inflates `COP max-gap` and Spouse Δ. **Old never hit this problem because it only had one channel; class imbalance on `withNOBODY` is balanced (≈50/50 across slots).**

### S1.6 `cop_avail` per-slot masking creates non-uniform supervision

J3's `cop_avail` mask zeroes the BCE denominator where source data is NaN (`04D_train.py:223-249`; `04A_dataset_assembly.py:67-87`). Different cycles + different channels have different missingness rates — colleagues is force-zeroed for 2005/2010 (`04A_dataset_assembly.py:339-342`). The effective sample size per channel per slot is uneven. The model trains on a patchwork supervision signal. Old had a uniform single-channel signal with no per-slot/per-channel holes.

### S1.7 Metric framing: AT_HOME RMS is per-cell, not global

Old's AT_HOME metric was binary accuracy on the observed test set — a single scalar averaged across all slots, respondents, and days. J3's gate is **RMS across (CYCLE_YEAR × DDAY_STRATA) cells** in percentage points. The marginal-bias loss term (`04D_train.py:184-193`) enforces only the *global* AT_HOME mean. The model can match the grand mean and still be 5+ pp off in individual cells. The metric is structurally harsher than what old was scored on, *and* the only loss-side regularizer aimed at it operates at the wrong granularity. Spouse Δ is similar — it is the max-across-cells gap, not the global average. So even with perfect marginal-bias loss, the cell-level gates can stay open.

### S1.8 The activity head benefits from class-boost calibration, the binary heads don't

`ACTIVITY_BOOSTS` ×5/×3/×2 (`04D_train.py:677-681`) gives the activity head an aggressive curriculum. There is no equivalent for AT_HOME or co-presence — no per-channel boost, no per-slot reweighting. So even within J3's loss landscape, activity has more loss-shaping attention than the binary heads. Combined with AR feedback, that explains why J3 ends up closer-to-gate on the *harder-cardinality* task than on the *easier-cardinality* tasks.

### S1.9 Synthesis

The binary outputs look easy by cardinality but are harder in J3 for **six independent reasons** stacked on top of the architectural diff (§6.1):

| Reason | Affects AT_HOME | Affects co-presence |
|---|---|---|
| 1ch→9ch reduction lost | — | Severe |
| No AR feedback in NAT heads | Moderate | Moderate |
| Encoder-only demographic routing | Severe | Severe |
| Schema dropped binary-relevant fields | Severe (HomeOwn/RoomCount/Internet) | Severe (Kinship/NuclearFamily) |
| BCE rare-class collapse w/o pos_weight | Mild | Severe (Spouse-Δ in particular) |
| Per-cell metric vs global marg-bias regularizer | Severe | Severe |

**Practical takeaway.** The user's intuition is sound: binary *should* be easier. The reason it isn't, in J3 specifically, is that J3 made several decisions that disproportionately tax the binary heads — and the §6.1 single-axis port (per-slot demographic broadcast) is expected to help the binary heads **more** than the activity head, because the binary heads have no AR fallback. This re-prioritizes the §6 ranking somewhat: if the goal is "close the AT_HOME and Spouse gates," then §6.1 (per-slot broadcast) and §6.2 (restore Kinship/NuclearFamily/HomeOwn/RoomCount/Internet) are even higher-priority than §6.3 (`ACTIVITY_BOOSTS=0`), because §6.3 only moves the activity gate.

**Revised recommended sequencing.**
1. **§6.4 diagnostic first** (10 min, local) — measure neighbor-disagreement floor so we know if act_JS has headroom at all.
2. **§6.1 (J3-PSB)** — per-slot demographic broadcast. Single architecture change, expected to help both binary heads and activity simultaneously.
3. **§6.2 (J3-DemoWide)** — restore the dropped binary-relevant Census/HH fields. Step-2 audit needed first; then 04A extension.
4. **§6.3 (J3-NB)** — only if act_JS is still the bottleneck after §6.1+§6.2.

---

## 0. Why this investigation

J3 ships at composite 0.6355 but lives on the edge of two gates (Spouse Δ=2.03 vs 2.0 wall after `spouse_neg_weight` tuning; act_JS=0.0191 against a 0.022 inflection). Six J5 axis variants (A/B/C/F + J_old + J5-X1/X1b) all failed to beat it; the J3-HPT bundle (T/L/S_lo/S_hi/R_lo/R_hi) is in flight but is single-knob hyperparameter, not architecture. The user observation under test: the *old* `examples/cloud_computing/Transformer_pipeline.py` reportedly performed strongly on a problem that — once we read both data pipelines end-to-end — turns out to be **easier in some dimensions and harder in others** than J3's. The hypothesis: when we re-architected to encoder→decoder + cross-attention conditioning, we lost (i) per-slot demographic broadcast, (ii) every-step demographic re-injection in attention, and (iii) the rich continuous Census/HH structure (Marital, Kinship, Citizenship, FamTypo, Internet/Phone/Car ownership, Home/Room, Eco/Job sectors) that the old pipeline fed as 24 separate learned embeddings. J3 reduces all of that to a single `cond_vec` injected only at the CLS token and once per decoder layer as a cross-attention key/value.

## 1. Problem framing (what each model is asked to predict)

| Dimension | Old Transformer | J3 |
|---|---|---|
| Source sequence length | 24 hourly slots (`X_train.reshape(-1, 24, ...)`, `Transformer_pipeline.py:270-272`) | 48 × 30-min slots (`04A_dataset_assembly.py:32`) |
| Generation task | **Single-day classification per slot** (no other-day generation) — model predicts the *observed* day's labels from its own features. No "synthesize the unobserved DDAY_STRATA" task. | **Cross-strata diary synthesis**: given diary at one DDAY_STRATA, generate diary at the *other two* DDAY_STRATA via AR decoder (`04D_train.py:104-120` pair construction; `04B_model_J3.py:957-991` Arm-1 AR loop). |
| Activity taxonomy | 14 classes (`output_dim_activity = len(set(y_activity_train.flatten()))`, `Transformer_pipeline.py:1233, 1464`; 14 from `mapping={1..14}` in `2ndJ_datapreprocessing.py:475-481`) | 14 classes (`04B_model_J3.py:57`, `n_activity_classes: 14`) — **same width** |
| Location/AT_HOME | 18-class `location` head, then thresholded with sigmoid > 0.5 to binary in eval (`Transformer_pipeline.py:556-557, 801-802`). **Note: `output_dim_location=1` at training**, `Transformer_pipeline.py:1465`, so trained as a single binary BCE, not 18-way — the 18-cat `PLACE` mapping happens upstream in `2ndJ_datapreprocessing.py:488` but is collapsed to a binary `location` column by the time `data_preprocess()` consumes it (`Transformer_pipeline.py:255-257`). | Binary AT_HOME head, BCE (`04B_model_J3.py:891-893`, `04D_train.py:178-180`) — **same** |
| Co-presence channels | **1** binary channel: `withNOBODY` (`Transformer_pipeline.py:558, 1466`), `output_dim_withNOB=1` | **9** binary channels (Alone, Spouse, Children, parents, otherInFAMs, otherHHs, friends, others, colleagues), masked BCE (`04A_dataset_assembly.py:28-31`; `04D_train.py:219-249`) |
| Per-respondent observations | One diary per respondent, used as both input and target (no missing-day prediction) | One observed diary, two *unobserved* strata generated; pair training matches src on one strata to demographic-neighbor on a different strata (`04C_training_pairs.py:139-172`) |
| Demographic features | **24 separate categorical embeddings** + 4 continuous (`Transformer_pipeline.py:411-496`): Education, Employment, Gender, FamTypology, NumFamMembers, AgeClass, Region, MarStat, Kins, OccProf, FamTypo, OccSeqNum, Citizenship, Internet, MobilePhone, CarOwn, FamTypoSimple, HomeOwn, RoomCount, EcoSector, JobType, OCCinHH, season, weekend | **One pre-computed `cond_vec`** (`04A_dataset_assembly.py:39-44, 162`): one-hot of {AGEGRP, SEX, MARSTH, HHSIZE, PR, CMA, KOL, LFTAG, HRSWRK, NOCS, COW, DDAY_STRATA} + standardized TOTINC + binary {COLLECT_MODE, TOTINC_SOURCE} — **12 cat + 1 cont + 2 bin = 15 fields total** (no Kinship, no Nuclear-Family-Profile, no Citizenship, no Internet/Phone/Car/Home/Room ownership, no Eco/Job sector split) |
| Per-slot demographics | **Broadcast: every one of 24 slots carries all 24 embeddings concatenated as part of its token** (`Transformer_pipeline.py:573-610` — each embedding `.reshape(-1, 24, dim)` then `torch.cat(..., dim=2)`) | **Single CLS token at position 0** of the encoder carries demographics (`04B_model_J3.py:919-924`); decoder re-injects demographics as 3 cross-attention tokens per layer (`04B_model_J3.py:112-122`) — but never re-broadcast onto each output position |
| Day-type signal in input | `week_or_weekend` and `months_season` are embeddings broadcast onto every slot (`Transformer_pipeline.py:600-601`) | DDAY_STRATA one-hot only present at: CLS token (via cond_vec), Arm-2 fusion concat (`04B_model_J3.py:1007-1013`), and 1-of-3 cross-attn tokens in Arm-1 (`04B_model_J3.py:111-116`) |
| Temporal resolution | 1-hour | 30-min |

**Critical first-question answer.** The output space is **not strictly harder** in J3. The activity head is the same width (14). J3 *replaces* the old 18-class location head (collapsed-to-binary in training anyway) with a binary AT_HOME — that's a wash. The genuine added difficulty is the **9-channel co-presence vs old's 1 `withNOBODY` channel**, AND the cross-strata synthesis framing (the old model never had to generate a day it didn't see). But on the activity axis alone — the dimension J3 is now tight on (act_JS=0.0191 against 0.022) — J3 is doing **the same activity-classification task at a finer time resolution (48 vs 24 slots) with vastly less demographic conditioning per token**.

## 2. Data preprocessing — old vs new

| Dimension | Old (`2ndJ_datapreprocessing.py` + `Transformer_pipeline.py:122-293`) | J3 (`04A_dataset_assembly.py` + `04C_training_pairs.py`) |
|---|---|---|
| Activity harmonization | 14 categories built by `load_map_and_save(... columns_to_map="ACTCODE/TUI_01", mapping={1..14})` per cycle (`2ndJ_datapreprocessing.py:474-481, 515-525, 560-563, 599-606`). All 4 cycles harmonized to the same 14-way taxonomy. | 14-class activity, same taxonomy by claim. Source is `act30_001..048` already harmonized upstream in Step 2 (not in 04A). (`04A_dataset_assembly.py:296-297`) |
| AT_HOME / location | 18-class `occPRE`, then collapsed to a single `location` binary column before preprocessing (`Transformer_pipeline.py:255-257`). The 18-cat mapping in `2ndJ_datapreprocessing.py:488` is upstream of the collapse. | Binary `hom30_001..048` from Step 3; AT_HOME index 0 of aux_seq (`04A_dataset_assembly.py:300-301, 202`) |
| Co-presence | **Merged into a single `withNOBODY` (binary) target column**; the granular `Alone/Spouse/Children/parents/otherHHs/friends/others` columns produced by `merge_coPresence` in `2ndJ_datapreprocessing.py:500-504, 542-546, 581-584, 627-630` are **collapsed before the Transformer ever sees them**. Result: 1-d binary target, `output_dim_withNOB=1`. | 9 binary channels kept separate; per-slot availability mask `cop_avail` derived from NaN (`04A_dataset_assembly.py:67-87`); colleagues forced 0 for 2005/2010 (`04A_dataset_assembly.py:339-342`) |
| Normalization | `RobustScaler` on continuous columns excluding binary + categorical + targets (`Transformer_pipeline.py:214-219`) | `StandardScaler` on TOTINC only (`04A_dataset_assembly.py:127-143`) |
| Categorical encoding | Integer label-encoded → fed to `nn.Embedding` (lookup table) per column (`Transformer_pipeline.py:179-180, 468-496`) | One-hot pre-computed into `cond_vec` (`04A_dataset_assembly.py:110-125`) — **no learned demographic embeddings at all** |
| Train/val/test split | 50/25/25 by Household_ID × Occupant_ID stratified on `months_season × week_or_weekend` (`Transformer_pipeline.py:122-138, 222-227`); k-fold stratified is an alternative path (`Transformer_pipeline.py:301-314`) | 70/15/15 by row position stratified on `CYCLE_YEAR × DDAY_STRATA` (`04A_dataset_assembly.py:172-196`). Within-cycle pairing only (`04C_training_pairs.py:139-152`) |
| Padding / variable length | None — every respondent is forced to exactly 24 episodes by `grouped.filter(lambda x: len(x) != 24)` (`Transformer_pipeline.py:152-154`); rows that don't fit are **dropped** | None — every respondent is exactly 48 × 30-min slots by Step-3 construction |
| Masking | None of the targets are masked; missing co-presence is collapsed into the single `withNOBODY` value | `cop_avail` per-slot per-channel mask drives BCE denominator (`04D_train.py:223-249`); home_label_smooth, marginal-bias regularizer, spouse_neg_weight, colleagues-zero-for-2005/2010 are all loss-side levers (`J3.yaml:22-34`) |
| Pair construction | **No pair construction.** Each diary is its own input *and* target; no cross-day prediction. Sequence is the 24 slots × (24 categorical embeddings + 4 continuous) of *that* respondent on *that* observed day. | Demographic K=5 neighbor search within the same `CYCLE_YEAR`, on a *different* DDAY_STRATA; 1-of-K resampled each epoch (`04C_training_pairs.py:139-172`; `04D_train.py:91-98`) |
| Sampling weighting | Inverse-frequency *not* applied; classes weighted only via `nn.CrossEntropyLoss` reduction='mean' (`Transformer_pipeline.py:962-964`) — no per-class weight tensor | `WeightedRandomSampler` by 1/strata_count + optional WGHT_PER (`04D_train.py:738-754`); inverse-sqrt-freq activity class weights with Work×5/Transit×3/Social×2 manual boosts (`04D_train.py:671-686`) |
| Per-respondent supervision count | **1 diary = 1 supervision signal** for that respondent's observed day | **2 cross-strata pairs** per source respondent (one per non-observed stratum), and `proportional_targets` G1 mode replicates Sat/Sun→WD pairs 5× (`04C_training_pairs.py:131-138`) |

**Load-bearing flags from this table:**
- **Old's flattened co-presence into one binary `withNOBODY` is a dramatically easier supervision signal.** A single "is the respondent alone or not" target is closed-form decidable from the activity head's behaviour; J3's 9-way co-presence requires the model to disambiguate Spouse vs Children vs parents vs friends at the channel level, with per-channel BCE and per-cycle availability holes (Section 1.3 of `investigation_Training_setp4v2.md`).
- **Old's pair task is the diary-it-already-saw**, J3's is *generate the day-it-did-not-see*. This is not a small difference; it changes the entire generative framing.
- **Old's far richer demographic schema** (24 categorical fields incl. Kinship, NuclearFamily slot, Citizenship, Internet/Phone/Car ownership, Home/Room, Eco/Job sector) gives the model orders of magnitude more conditioning signal per token; J3 dropped 9+ of those fields between pipelines.

## 3. Model architecture — old vs J3

### 3.1 Old Transformer (`Transformer_pipeline.py:410-635`)

- **Tokenizer/embedding**: Per-slot, 24 categorical features each go through a dedicated `nn.Embedding(num_cats_i, min(embed_size=50, num_cats_i//2 + 1..2))` (`Transformer_pipeline.py:436-496`). All 24 embeddings are reshaped to `(-1, 24, embedding_dim_i)`, then **concatenated along the feature dim with the 4 continuous features** (`Transformer_pipeline.py:573-610`). Result: every one of the 24 slots carries the full demographic + temporal signal as its token vector. `input_size = sum(embedding_dims) + num_continuous_features`.
- **Positional encoding**: `LearnablePositionalEncoding(seq_len=20000, embed_dim=input_size)` (`Transformer_pipeline.py:395-405, 542`). Trainable, broadcast-added.
- **Encoder structure**: Plain `nn.TransformerEncoderLayer(d_model=input_size, nhead=4, dim_feedforward=d_feed=10240, batch_first=True, activation=ReLU)` × `num_hidden_layers=3` (default after tuning, `Transformer_pipeline.py:1452-1454, 545-548`).
- **Attention masks**: None. Bidirectional self-attention across all 24 slots, no causal mask.
- **Conditioning fusion**: At every slot, via concat-and-encode. There is no "CLS token" and no cross-attention to a separate conditioning vector — the conditioning *is* part of each token.
- **Decoder**: **None.** Encoder-only. The encoder output goes directly to three parallel heads.
- **Output heads** (`Transformer_pipeline.py:556-558, 625-633`):
  - `activity_dense = Linear(input_size, output_dim_activity=14)` after `ReLU` activation on encoder output → softmax CE.
  - `location_dense = Linear(input_size, 1)` after Dropout(0.25)+Tanh → BCE.
  - `withNOB_dense  = Linear(input_size, 1)` after Dropout(0.1)+Tanh → BCE.
- **Inference**: Greedy / argmax (`evaluate_and_save_afterTuning` uses `torch.max(activity_output, 2)` and `torch.round(torch.sigmoid(...))`, `Transformer_pipeline.py:1602-1605`). **No temperature, no AR loop, no sampling.**

### 3.2 J3 (`04B_model_J3.py:787-1079` — `JSeriesHybrid`, `model_type="J3"`)

- **Tokenizer/embedding**: Activity goes through a single `nn.Embedding(14, d_act=32)` (`04B_model_J3.py:839`). Per-slot token = `Linear(d_act + 1 + 9 = 42, d_model=384)` applied to `[act_emb | AT_HOME | 9 cop channels]` (`04B_model_J3.py:840, 914-915`). **Demographics enter only at the CLS token**, not the slot token.
- **Positional encoding**: Sinusoidal, registered buffer (`04B_model_J3.py:30-43, 853-854`). Encoder length 49 (CLS + 48), decoder length 48.
- **Trunk encoder**: 6 layers, `d_model=384, n_heads=8, d_ff=1536, dropout=0.1, activation=GELU` (`J3.yaml:14-19`; `04B_model_J3.py:857-863`).
- **CLS token**: `cls_mlp = Sequential(Linear(d_cond + 32, 256), GELU, Linear(256, 384))` consumes `[cond_vec | cycle_emb]` once and produces a single conditioning vector at position 0 of the encoder (`04B_model_J3.py:843-848, 918-922`).
- **Arm 1 — AR activity decoder** (`04B_model_J3.py:866-869, 933-991`): Custom `CrossAttnDecoder` × 6 layers; each layer = self-attn → cross-attn(encoder memory) → cross-attn(3 conditioning tokens: demo / cycle / strata) → FFN (`04B_model_J3.py:82-97`). Activity-only slot input (`arm1_slot_proj: Linear(d_act, d_model)`, no AT_HOME feedback, `04B_model_J3.py:852, 940`). Causal mask. BOS token. Generates 14-way activity tokens autoregressively.
- **Arm 2 — NAT binary head fusion** (`04B_model_J3.py:872-880, 995-1024`): Per-slot concat of `[memory_slot (d_model) | act_probs_projected (d_model via arm2_act_proj, J3-only) | cond_vec (d_cond) | cycle_emb (32) | strata_oh (3)]` → `Linear(d_model + d_model + d_cond + 32 + 3, d_model)`. This is J3's defining diff vs J1/J2/J2_5: `arm2_act_proj = Linear(14, 384)` projects soft act probs to d_model **before** the concat, so the activity signal doesn't get drowned by the 384-d memory (`04B_model_J3.py:875-880`).
- **Output heads** (`04B_model_J3.py:885-897`):
  - `act_head = Linear(d_model=384, 14)` from decoder hidden — Arm 1 only.
  - `home_head = Sequential(Linear(384, 384), Tanh, Linear(384, 1))` — Arm 2.
  - `cop_head  = Sequential(Linear(384, 384), Tanh, Linear(384, 9))` — Arm 2.
- **Inference** (`04E_inference.py:160-171`; `04B_model_J3.py:1054-1079`): AR with **multinomial sampling at temperature τ=0.8** for activity head (`04E_inference.py:66`), Arm-2 NAT pass for home/cop, post-hoc Spouse clip when AT_HOME=0, plus post-hoc Sleep@night→home=1, Work→home=0, colleagues=0 for 2005/2010 (`04E_inference.py:89-108, 181-183`).

### 3.3 Component-by-component comparison

| Component | Old Transformer | J3 |
|---|---|---|
| Trunk type | Encoder-only, bidirectional self-attention, no causal mask | Encoder (49 tokens, CLS + 48) + 6-layer cross-attn AR decoder |
| Trunk depth | 3 layers (after tuning) | 6 enc + 6 dec layers |
| Heads / d_model | nhead=4 / `d_model=input_size` (≈ sum of 24 embeddings + 4 cont, in the hundreds), `d_ff=10240` | nhead=8 / `d_model=384` / `d_ff=1536` |
| Activation | ReLU on attention layers; Tanh on binary heads | GELU on attention; Tanh on binary heads |
| Positional encoding | Learnable, length 20000 | Sinusoidal, length 49/48 |
| Demographic injection | Concatenated to *every* token (24 categorical embeddings + 4 continuous broadcast to all 24 slots), per-slot, all layers | Once at CLS token (encoder); once per decoder layer as 3 cross-attn key/value tokens; once per slot in Arm-2 fusion concat |
| # distinct demographic features carried | 24 categorical + 4 continuous = **28 distinct learned signals** per token | 12 one-hot cat + 1 cont + 2 bin = **15 fields** flattened into one `cond_vec` |
| Conditioning learnability | Each demographic field has its own embedding table — gradient flows independently | Single fixed pre-computed one-hot vector → one MLP — no per-field representational capacity, all interactions go through cls_mlp |
| Day-type signal | `week_or_weekend` embedding broadcast at every slot, every layer | DDAY_STRATA one-hot at CLS, decoder cross-attn token, and Arm-2 fusion — but never as part of the slot token in the encoder pass |
| Output framing | Per-slot 3-way multi-task: 14-CE + 1-BCE + 1-BCE | Per-slot 3-way: 14-CE (AR) + 1-BCE (NAT) + 9-BCE-masked (NAT) + marginal-bias term |
| Generation | Greedy argmax | AR multinomial at τ=0.8 |
| Cross-day generation | **No** — predicts the diary it saw | **Yes** — generates 2 unseen DDAY_STRATA per respondent |

## 4. Loss function & training loop

### 4.1 Old (`Transformer_pipeline.py:717-840, 962-971`, hyperparams in `Transformer_bash.slurm` + `Transformer_num_features.json`)

- Loss = `w_act * CE(act) + w_loc * BCE(loc) + w_NOB * BCE(withNOB)` with weights normalized so they sum to 1 (`Transformer_pipeline.py:771-777`). Default `w_act = w_loc = w_NOB = 1` (`Transformer_pipeline.py:1449-1451`).
- `cr_act = CrossEntropyLoss(reduction='mean')` — **no class weights, no boosts** (`Transformer_pipeline.py:962`).
- `cr_loc = cr_NOB = BCEWithLogitsLoss(reduction='mean')` — no pos_weight, no mask, no marginal term, no label smoothing (`Transformer_pipeline.py:963-964`).
- Optimizer: `Adam(lr=4e-4)` (best Optuna pick from `Transformer_num_features.json:1`), with `ReduceLROnPlateau(mode='min', factor=0.95, patience=5)` (`Transformer_pipeline.py:966, 971`).
- Batch size: 128 (from `Transformer_num_features.json`).
- `d_feed`: 10240 (huge FFN), `embed_size=50`, `nhead=4`, `num_hidden_layers=3` (`Transformer_pipeline.py:1452-1461`).
- Gradient clipping: `clip_grad_norm_(..., max_norm=25)` (`Transformer_pipeline.py:787`).
- Early stopping: validation **loss stability** with `min_delta=1e-4` and `patience=50` epochs (`Transformer_pipeline.py:998-1107`); plus a hard accuracy ceiling of 0.96 (`Transformer_pipeline.py:1112-1115`).
- Epochs: not stated in `Transformer_bash.slurm`; `trainEvaluate_afterTuning(... epochBase=500)` default (`Transformer_pipeline.py:1377`).
- Tracked metric: per-task accuracy (activity multi-class accuracy, location/withNOB binary accuracy).
- Wall time budget: 3 days (`Transformer_bash.slurm:11`).

### 4.2 J3 (`04D_train.py:125-278`, hyperparams in `J3.yaml`)

- Total = `LAMBDA_ACT*act_CE + LAMBDA_HOME*home_BCE + LAMBDA_COP*cop_BCE_masked + LAMBDA_MARG*marg + LAMBDA_AUX*aux + LAMBDA_LOGIC*logic` (`04D_train.py:261-268`).
- `J3.yaml`: `lambda_act=1.0`, `lambda_home=0.7` *(memory note: true J3 trained at 0.9)*, `lambda_cop=0.3`, `lambda_marg=0.1`, `marg_mode=global`. Activity CE has **inverse-sqrt-frequency class weights + boosts** ×5 on Work, ×3 on Transit, ×2 on Social (`04D_train.py:671-686`). Home BCE is plain BCE-with-logits (pos_weight disabled 2026-04-22, `04D_train.py:688-697`). Cop BCE is masked by per-slot `cop_avail` and uses `spouse_neg_weight=0.45` to down-weight Spouse=True (`04D_train.py:212-249`, `J3.yaml:29`). Home target label-smoothed at 0.05 (`04D_train.py:159-161`, `J3.yaml:34`).
- Marginal-bias term: `|sigmoid(home_logits).mean() - home_tgt.mean()|` averaged per-batch (`04D_train.py:184-193`).
- Optimizer: `AdamW(lr=5e-5, weight_decay=1e-2)` (`04D_train.py:779`, `J3.yaml:13`) with `ReduceLROnPlateau(mode='min', factor=0.95, patience=5)` on val_score (`04D_train.py:786-788`).
- Batch size: 256 (`J3.yaml:10`).
- Gradient clipping: `max_norm=25.0` for J-series (`04D_train.py:865`).
- Early stopping: patience=15 (`J3.yaml:12`) on validation `val_score = val_JS + 0.5 * home_gap` (`04D_train.py:408-413`).
- Max epochs: 100 (`J3.yaml:11`).
- AR-cascade design: Arm 1 sees activity-only decoder input (no AT_HOME feedback) — broken on purpose to prevent error compounding (`04B_model_J3.py:933-955` and J-series investigation history).

### 4.3 Comparison

| Dim | Old | J3 |
|---|---|---|
| LR | 4e-4 | 5e-5 (**8× smaller**) |
| Weight decay | 0 (plain Adam) | 1e-2 (AdamW) |
| Batch size | 128 | 256 |
| Loss-axis count | 3 (act-CE, loc-BCE, NOB-BCE) | 6 (act-CE, home-BCE, cop-BCE-masked, marg, [aux], [logic]) |
| Class re-weighting | None | inv-sqrt-freq × manual boosts ×5/×3/×2 |
| Channel-level bias regularizer | None | `spouse_neg_weight=0.45`, marg loss, home_label_smooth, cop_avail mask, per-cycle colleagues mask |
| Early stopping signal | val loss stability | val_JS + 0.5·home_gap (combined gate-aware score) |
| Inference temperature | argmax | τ=0.8 multinomial |

**Load-bearing flags:**
- The old pipeline has **no class re-weighting and no boosts** — Work/Transit/Social are not artificially upweighted. J3's `ACTIVITY_BOOSTS` (×5/×3/×2) is a strong prior that the model *will* over-produce these classes; act_JS is being held back partly by this prior because real-world Work prevalence < boost-induced predicted Work prevalence. This is testable.
- Old's LR is 8× larger and batch size 2× smaller — the effective gradient step is much bigger. J3's conservative LR may be undertraining the activity head.

## 5. Inference & evaluation

| Dim | Old | J3 |
|---|---|---|
| Inference framing | Predict labels on the diary the model has already seen (test-set forward pass), `evaluate_and_save_afterTuning` (`Transformer_pipeline.py:1602-1632`) | Generate **unobserved-stratum** diaries via AR for all 64,061 respondents × 2 unobserved strata; copy observed where stratum matches (`04E_inference.py:111-200`) |
| Decoding | `torch.max(activity_output, 2)` argmax; `torch.round(sigmoid(...))` for binary heads | Multinomial sampling at τ=0.8 for activity; sigmoid > 0.5 for binary heads; AR feedback for activity only |
| Post-hoc rules | None | Sleep at night → home=1, Work → home=0, Spouse zeroed when home=0, colleagues zeroed for 2005/2010 (`04E_inference.py:89-108, 178-183`) |
| Metric — activity | Per-class precision/recall/F1, micro-accuracy (`Transformer_pipeline.py:1722-1724`) | Jensen-Shannon divergence between predicted and observed 14-class activity distributions per (CYCLE_YEAR × DDAY_STRATA) cell (`04D_train.py:296-301, 388-405`); hard gate act_JS ≤ 0.05 |
| Metric — location/home | Binary accuracy | AT_HOME RMS-across-strata in pp; hard gate ≤ 5.3 pp |
| Metric — copresence | Binary accuracy on the single `withNOBODY` channel | Spouse-Δ-from-observed in pp + COP max-gap per channel; hard gates Spouse ≤ 5 pp, composite < 1.045 |
| Comparability | Same-day classification accuracy is **not** the same metric family as cross-strata distributional divergence. Old's "I got 80% activity accuracy" tells you nothing about whether old would have closed J3's gates if scored the same way. | Distributional + per-cell calibration metrics |

**Finding.** The old pipeline's reported performance is in *accuracy on the observed day*, which is a strictly easier metric than J3's *distributional fidelity on the generated unobserved day*. We cannot directly compare J3=0.6355 vs an old "activity accuracy ≈ X%" — they measure different things. **The user's claim that "old beat a harder problem" needs to be re-examined: in the metric J3 is held to, the old pipeline was never measured.**

## 6. Verdict: what is likely load-bearing

Ranked by suspicion they explain why J3 plateaus. For each: the specific difference, why it might matter information-theoretically, and a single-axis experiment.

### 6.1 (HIGHEST) Per-slot demographic broadcast vs single-CLS conditioning

Old re-injects all 28 demographic signals onto every one of 24 slots (`Transformer_pipeline.py:573-610`). J3 condenses to one `cond_vec` and exposes it at *only three injection points*: the CLS token (`04B_model_J3.py:918-922`), the decoder cross-attn token (`04B_model_J3.py:111-116`), and the Arm-2 fusion concat (`04B_model_J3.py:1011-1024`). For 48 slot-level decisions like "is Work plausible at slot t for this respondent profile," the encoder must learn to *route* the demographic signal from CLS to position t through self-attention. The old model has zero routing distance — the demographics are in the slot token itself.

**Why this might matter.** Activity micro-distributions per respondent cluster *strongly* by employment status × age × CMA × HRSWRK × NOCS, and the old pipeline gave the attention layers the full joint distribution as a flat per-slot feature, while J3 expects the attention mechanism to reconstruct it. With 6 layers and 8 heads, J3 *can* route it, but every wasted unit of routing capacity is capacity not spent on temporal patterning. This would manifest exactly as J3 does: activity JS plateaus near the gate, and the binary heads need explicit per-slot re-injection (Arm-2 fusion was the J3 fix and it closed AT_HOME RMS, supporting the hypothesis that per-slot demographic broadcast is load-bearing).

**Single-axis experiment (J3-PSB, "Per-Slot Broadcast"):** Modify `04B_model_J3.py` `_encode()` to concatenate `cond_vec.unsqueeze(1).expand(-1, 48, -1)` to each slot's input before the `slot_linear` projection. New slot_linear input dim becomes `d_act + 10 + d_cond`. Keep CLS token unchanged. Single change, single retrain, full HPC.

### 6.2 (HIGH) Demographic schema width — 9+ Census/HH fields dropped

The old pipeline carried Kinship, Nuclear-Family-Profile, Nuclear-Family-Typology, Nuclear-Family-OccSeqNumber, Citizenship, Internet/Mobile/Car ownership, Home ownership, Room count, EcoSector, JobType (`Transformer_pipeline.py:411-465`). J3 carries only AGEGRP/SEX/MARSTH/HHSIZE/PR/CMA/KOL/LFTAG/HRSWRK/NOCS/COW/DDAY_STRATA + TOTINC + COLLECT_MODE + TOTINC_SOURCE (`04A_dataset_assembly.py:39-44`). The dropped features include household-composition signals (Kinship, NuclearFamily-*), tech-adoption signals (Internet/Mobile/Car) and dwelling signals (Home/Room) — all of which plausibly predict at-home time and co-presence.

**Why this might matter.** AT_HOME rate is structurally tied to home ownership and room count (you spend more time at home if you own it / have more space / can WFH because Internet). Co-presence channels are structurally tied to Kinship + NuclearFamily (Spouse, Children, parents only meaningful given those fields). Dropping them stripped exactly the supervisory channels the cop gate needs.

**Caveat:** Some of these may not be in the 2022 cycle of the GSS file J3 uses (the schema was harmonized down to a common subset across 4 cycles). Confirmation requires checking the upstream Step-2 harmonization output. If the fields *are* available in upstream CSVs but were dropped in 04A, this is a cheap fix.

**Single-axis experiment (J3-DemoWide):** Audit Step-2 outputs (`outputs_step2/`) for Kinship / NuclearFamily / HomeOwnership / RoomCount / Internet / Mobile / Car columns. For any present in ≥3 of 4 cycles, extend `CAT_COLS` in `04A_dataset_assembly.py:39-44`. Rebuild `cond_vec`, re-pair, retrain J3 unchanged. Expected `d_cond` increase: +50–80 dims.

### 6.3 (MEDIUM) ACTIVITY_BOOSTS prior is fighting act_JS

`04D_train.py:677-681` upweights Work/Transit/Social activity-CE by 5/3/2× as a diagnostic prior. act_JS measures distribution match; the boosts induce **over-prediction** of these classes (the model is rewarded for being right on Work, penalised heavily for being wrong, so it overshoots Work prevalence). J3 sits at act_JS=0.0191 against a 0.022 inflection — a 0.003 budget. Removing the boost would shift predicted activity marginals toward observed marginals; this is precisely the gradient act_JS rewards.

**Why this might matter.** J3 was tuned with these boosts on (the boosts predate J3). Old pipeline had **no class weighting at all** — yet "performed strongly." The old result without boosts is consistent with the boost being unnecessary or counter-productive for J3 at the JS-divergence metric.

**Single-axis experiment (J3-NoBoost):** Single env-var change: `ACTIVITY_BOOSTS=0`. Retrain J3 from scratch. Predict act_JS will drop ~0.002 and Work-cell calibration will improve; risk is per-class Work F1 falls slightly. Cheapest experiment in this list.

### 6.4 (DIAGNOSTIC — MEASURED) Cross-strata generation framing is a different task

Old never generates an unobserved day — the supervision signal is the diary in front of it. J3 must generate diaries it has never seen for the same respondent on a different DDAY_STRATA, using a *demographic-neighbor* as teacher (`04C_training_pairs.py:139-172`). Pair-based supervision injects neighbor-noise: the target diary is from someone *similar*, not the respondent themselves. This is a fundamentally noisier supervision regime.

**Why this might matter.** Even if every architectural choice were optimal, the target itself is a sample from `p(diary | demographics, target_strata)` — and the K=5 nearest neighbors define an empirical posterior with non-zero variance. The model can never achieve zero error against neighbor diaries because the neighbors disagree with each other.

**Empirical result (measured).** K=5 pairwise JS divergence floor across neighbor diaries = **0.1888**. The supervisory targets disagree among themselves at JS=0.1888 on average.

**Interpretation.**
- The 0.1888 number is the *pair-level* disagreement (any two of the K=5 neighbors). J3's reported `act_JS=0.0191` is the *aggregate cell-level* distributional gap (cycle × stratum × averaged across respondents). These are not the same granularity, so 0.0191 < 0.1888 does *not* mean J3 is already past the floor — they live on different axes.
- However, 0.1888 is large enough to confirm that the supervisory signal at the per-respondent pair level is intrinsically very noisy. Any further compression on act_JS at the cell-level metric is fighting that pair-level noise indirectly through gradient variance during training. The cell-level act_JS gate has *limited* headroom, not *zero* headroom.
- **Implication for §6.3.** The expected gain from `ACTIVITY_BOOSTS=0` may be small if act_JS is already close to its noise-limited compression on cell-level marginals. The experiment is still cheap enough to be worth running, but its priority drops below §6.1 and §6.2 which target the AT_HOME and Spouse Δ gates — the gates J3 is actually tight on for reasons unrelated to the neighbor floor.

### 6.5 (LOWER) FFN width: 10240 vs 1536

Old `d_feed=10240` (`Transformer_pipeline.py:1185, 1461`) — a 10× larger FFN than J3's 1536 (`J3.yaml:19`). With d_model in the few-hundreds range, that's a huge expressivity buffer. J3's 4× ratio (`d_ff/d_model = 1536/384 = 4`) is standard but unambitious; the old's ~30× ratio is unusually large.

**Why this might matter.** Activity-classification at slot resolution benefits from wide MLP-style memorization of (demographic, slot, prev-slot)→activity mappings. The old pipeline had enormous FFN capacity to memorize these joint statistics. J3 may be too narrow at the FFN axis specifically.

**Single-axis experiment:** This is already partly in the J3-HPT bundle (the `S_hi`/`S_lo` runs sweep d_model/d_ff scaling). If S_hi doesn't move, FFN is not the bottleneck; if S_hi gains, FFN is.

## 7. Recommended next step (revised after §6.4 measurement)

The §6.4 diagnostic was run externally and returned a K=5 pairwise neighbor JS floor of **0.1888**, confirming the supervisory signal is intrinsically noisy. This re-orders the experiment priority away from "improve act_JS" and toward "close the binary-head gates" (AT_HOME RMS, Spouse Δ), which are the gates that are tight for reasons orthogonal to neighbor noise.

**Pick (primary): §6.1 — J3-PSB per-slot demographic broadcast.** Architectural change with the highest expected impact across all three gates simultaneously, and per §S1.3 expected to help the binary heads *more* than the activity head (the binary heads have no AR fallback to compensate for failed CLS→slot routing).

- **Edit.** `04B_model_J3.py` `_encode()`: concatenate `cond_vec.unsqueeze(1).expand(-1, 48, -1)` to each slot's input before the `slot_linear` projection. Update `slot_linear` input dim to `d_act + 10 + d_cond`. Keep CLS token unchanged so the two paths coexist.
- **Tag.** `J3-PSB`. Same `J3.yaml` config otherwise.
- **Cost.** One full HPC retrain ~5 h + inference/scoring ~30 min = **~5.5 h wall clock**.
- **Gate.** Composite < 0.6355 AND (AT_HOME RMS < 4.57 pp OR Spouse |Δ| < 2.03 pp). Either binary gate closing meaningfully is a win; act_JS movement is secondary.

**Secondary: §6.3 — `ACTIVITY_BOOSTS=0`.** Cheap (env-var flip), but expected gain is now bounded by the neighbor floor (§6.4 result). Run only if §6.1 succeeds and we want to refine the activity gate further, or in parallel as a "cheap-to-try" sanity check.

**Tertiary: §6.2 — J3-DemoWide.** Requires Step-2 output audit before the 04A edit; potentially highest ceiling for AT_HOME and Spouse Δ (the dropped fields are exactly the binary-head predictors per §S1.4), but more upstream work. Schedule after §6.1 result is in.

**Sequence.** §6.1 → (read result, decide) → either §6.2 (if binary gates still open) or §6.3 (if act_JS still the bottleneck). Do not parallel-launch all three; each retrain costs 5 h of GPU time and we want the §6.1 architecture result to inform §6.2's data-pipeline scope.
