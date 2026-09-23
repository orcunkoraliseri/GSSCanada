# Limitations checklist (P2/P13), 2026-09-23

Every point of the old §7 (archived at `writing/submission/previous/4J_manuscript_submission.md.pre_rewrite_20260923`,
lines 1139-1333) and its new home. "Main §5" = new Limitations section; "SI S11" = long form in the
supplement. A tick means the point was found in its new home after the rewrite.

| # | Old § | Point | New home | Done |
|---|---|---|---|---|
| 1 | 7.0 | Intro paragraph ("three limitations removed ... claims no longer exist") | deleted: meta text, no content | [x] |
| 2 | 7.1 | Three countries, one wave each; every fold trains on two; bounds generality | Main §5 para 1; SI S11 "Corpus size" | [x] |
| 3 | 7.1 | Held-in check misses on all six training-country cells; qualifies the transfer framing | Main §3.1 (P10 two sentences), §4.1, §6; SI S7.2 Table S2, S11 | [x] |
| 4 | 7.1 | No published floor on the number of source populations (search 2026-09-13); cuts both ways | Main §5 para 1 (undated sentence); SI S11 (dated) | [x] |
| 5 | 7.1 | Invariant-risk identifiability bounds do not apply (no invariance objective) | Main §5 para 1 (one sentence); SI S11 | [x] |
| 6 | 7.2 | Conditioning vector is demographic; what separates countries is institutional timing | Main §5 para 2, §4.4; SI S11 | [x] |
| 7 | 7.2 | The strongest positive result sharpens the objection (old: six-hour spread) | rewritten per P3 branch 2: Main §5 para 2 ("The appliance results support this reading"), §4.4; SI S11 | [x] |
| 8 | 7.2 | Does not rescue the comparison: the baseline received the same margins | Main §5 para 2, §4.3; SI S11 | [x] |
| 9 | 7.3 | Coverage and non-response; institutions, people without housing, hotel guests outside frame | Main §5 para 3; SI S11 | [x] |
| 10 | 7.3 | One or two diary days; multi-day dependence unobservable | Main §5 para 3; SI S11 | [x] |
| 11 | 7.3 | Three diary-day bases; only UK weight calendar-representative; re-based | Main §5 para 3, §2.1; SI S5, S11 | [x] |
| 12 | 7.3 | Italy scored against a published aggregate from a different survey round | Main §5 para 3, §2.1, §3.1; SI S7.2, S11 | [x] |
| 13 | 7.3 | UK household type unknown: 551 diaries (3.5 %); dropping moves error by 0.158 min/day | Main §5 para 3; SI S11 | [x] |
| 14 | 7.3 | Spain has no homemaker category | Main §5 para 3, §2.3; SI S3, S11 | [x] |
| 15 | 7.3 | Day type has no published marginal; assigned by calendar week | Main §5 para 3, §2.3; SI S3, S11 | [x] |
| 16 | 7.4 | Pretrained prior not uniform across countries; registered confound, unresolved, aligned with the split | Main §5 para 4; SI S11 | [x] |
| 17 | 7.5 | Constrained decoding not neutral; bias direction not quantified | Main §5 para 5, §3.4; SI S7.3, S11 | [x] |
| 18 | 7.5 | Generated output never raked (would close the gap by construction) | Main §5 para 5, §4.5; SI S11 | [x] |
| 19 | 7.6 | Heating-only intensities; never compared to a measured total | Main §5 para 6; SI S11 | [x] |
| 20 | 7.6 | No absolute cross-country comparison at the 10 % level (weather 5-11 %, sign differs) | Main §5 para 6, §2.1; SI S7.6, S11 | [x] |
| 21 | 7.6 | Archetype and observed-stock absolutes never placed side by side or differenced | Main §5 para 6; SI S11 | [x] |
| 22 | 7.6 | Fixed annual mean gain: redistribution only, annual channel null by design | Main §5 para 6, §2.5, §4.4; SI S11 | [x] |
| 23 | 7.6 | One thermal zone per dwelling: when, not where | Main §5 para 6; SI S11 | [x] |
| 24 | 7.7 | No per-dwelling prediction; mapping unvalidated per dwelling | Main §5 para 7; SI S11 | [x] |
| 25 | 7.7 | Primary-only trigger; secondary-only loads invisible and unbounded; laundry measured | Main §5 para 7, §3.5; SI S7.5, S11 | [x] |
| 26 | 7.7 | Ownership shares British, about two decades old, applied to Spain and Italy | Main §5 para 7; SI S11 | [x] |
| 27 | 7.7 | Hot-water check is a denominator mismatch, neither a model limitation nor a pass | Main §5 para 7, §3.5; SI S7.5, S11 | [x] |
| 28 | 7.8 | Reproducibility statistical, not bit-exact; observed-stock numerically stable | Main §5 para 8; SI S11 | [x] |
| 29 | 7.8 | Merged and unmerged adapters differ; intermediate files do not record which | Main §5 para 8; SI S1.6, S11 | [x] |
| 30 | 7.9 | Adapter weights not released (decided before training; reinforced by the privacy result) | Main §5 para 8, §3.7, Data availability; SI S11 | [x] |
| 31 | 7.9 | UK synthetic population withheld | Main §5 para 8, §3.7, Data availability; SI S11 | [x] |
| 32 | 7.9 | Spanish and Italian populations, code, checks, frozen pre-registration available | Data availability; SI S11 | [x] |
| 33 | 7.9 | Archetypes are the study's own construction, not an official TABULA product | Main §5 para 8; SI S11 | [x] |
| 34 | 7.9 | Institution not a Eurostat-recognised research entity; enquiry 2026-08-26 unanswered | Main §5 para 8 (undated); SI S11 (dated) | [x] |
| 35 | 7.10 | One training check never adjudicated (shuffle key omits a field) | Main §5 para 8 (one sentence); SI S1.6, S12 | [x] |
| 36 | 7.10 | One registered invariant built and self-tested, never scored on model output | Main §5 para 8 (same sentence); SI S12 | [x] |
| 37 | 7.10 | Documentation defect: full fine-tune manifest describes an adapter run; correction file | SI S12 only (documentation note, per brief) | [x] |
| 38 | 7.10 | Larger observed-stock campaign complete but not claimed; scoring found identical internal-gain series | Main §5 para 8 (one sentence), §2.5; SI S9, S12 | [x] |
| 39 | 7.10 | 840 Madrid cells in 84 buildings not completed; three Bologna courtyard buildings outside the method | SI S9, S12 | [x] |
| 40 | S5 (old SI) | "What the reader should not infer" (scaling curve, ceiling run, single-fold family, privacy not a passing audit, no scored result from the larger campaign, third digit) | Main §3.2, §3.7, §5; SI S6 (third digit), S11 | [x] |

New limitation points added by this round (not in the old §7):

| # | Point | Source | New home |
|---|---|---|---|
| N1 | Survey year confounded with country (2009-10, 2013-14, 2014-15) | plan §2, 2J unraised weaknesses | Main §5 para 1; SI S11 |
| N2 | One training seed per model; seed probe covers generation noise only | P5 brief | Main §2.6, §5 para 1; SI S11 |
| N3 | Pre-registration frozen internally; public deposit carries the submission date | D4 | Main §5 para 1 |
| N4 | Positioning (Appendix A) rests on the author's search, not a systematic review | plan §2 | Main §5 para 1 |
| N5 | Real-diary appliance pool unweighted; 100 dwellings, one year, one seed: no interval on peak hour | P3 wording limits | Main §5 para 7; SI S7.5, S11 |
| N6 | Timing checked only against real diaries through the same model, not measured national profiles (P8 not run) | plan P8 | Main §4.4, §5 para 7; SI S11 |
| N7 | British reference load profile about two decades old | old §5.8 | Main §5 para 7 |
| N8 | Sex is a conditioning stratum only, not analysed separately | E&B guide line 587 | Main §2.2, §5 para 3; SI S11 |
| N9 | Hourly heating differs from TABULA quasi-steady monthly figure by -36.7 to +136.6 % | old §5.11 | Main §5 para 6; SI S7.6 |
| N10 | UK archetypes parameterised from England's typology | old §2.3/§3.7 | Main §2.1, §5 para 6; SI S11 |

**Result: 40 of 40 old points ticked (38 with a home in the main text or data statement, 2 in the SI
only: #37 documentation defect and #39 the 840 cells / courtyard buildings, both moved to SI by the
brief). 10 new points added.**
