# Tier B repair pass — 4J manuscript — 2026-09-14

File edited (only file touched): `writing/submission/4J_manuscript_submission.md`.
Backup taken before any edit: `writing/submission/previous/4J_manuscript_submission.md.bak_pre_tierB`
(1,418 lines, confirmed non-empty before use).
Method: guarded Python patch (`str.replace` with a pre-checked match count for every anchor,
abort-on-mismatch), run with `py -3`, in two passes (main patch, 39 anchors; a rewrap pass, 3
paragraphs whose line-length grew past the document's own wrap width after the main patch).
No band, gate, verdict or registered threshold was touched. No new file was created except this
report.

## PART 1 — table renumbering

VERIFIED. Read the live file first: tables were numbered 1, 2, 5, 6, 7, 8, 9, 10 (no 3, no 4),
and §3's own line named a non-existent "Table 4" as the location of the complete gate set
(`4J_manuscript_submission.md:208`, pre-edit).

- Renumbered 5→3, 6→4, 7→5, 8→6, 9→7, 10→8 in one pass via placeholders (`@@3@@`…`@@8@@`),
  covering both the bold caption line and every in-text mention (`Table 9 are taken from` →
  `Table 7`; `Table 10 reports the corrected values` → `Table 8`), then stripped the
  placeholders. Every replacement was count-asserted before being applied (1 for the single
  captions, 2 for the two tables that also had an in-text mention).
- The broken "Table 4" pointer in §3 (`...is given in Table 4.`) was repointed at the
  supplementary material. Checked `4J_supplementary_material.md:13` (`## S1. The registered
  check set`, read-only) — that is where the complete gate set with provenance marks actually
  lives. New text: "...is given in the supplementary material (S1, the registered check set)."
  (`4J_manuscript_submission.md:206-208`).
- Post-edit audit: `grep -noE "Table [0-9]+"` over the file resolves to exactly the set
  {1,2,3,4,5,6,7,8}, no gaps, and every caption (`**Table N.**`) has at least one in-text
  citation (see B4 below for the four that needed one added). Printed output:
  ```
  Table 1 Table 2 Table 3 Table 4 Table 5 Table 6 Table 7 Table 8
  ```

## PART 2 — Tier B items

**B1 — wrong section pointers.** VERIFIED, 9 sentences, all fixed. Verified each by opening the
target section named in the pointer and confirming (or refuting) it actually holds the content
claimed.
- `(§5.5)` → `(§5.6)` — membership-inference result is in §5.6 (privacy audit), not §5.5 (joint
  structure). `4J_manuscript_submission.md:33`.
- `see §6.1 for what this absence...` → `§6.4` — the literature-absence discussion is §6.4
  ("The absence in the literature, and what it licenses"), not §6.1 (capacity). `:57`.
- `§5.2 reports the size of that correction` → `§5.5` — the day-basis weighting correction's
  effect on verdicts is tested in §5.5 ("Verdicts are identical under the calendar-re-based
  weights and unweighted..."), not §5.2 (transfer gates). `:151`.
- `Both are reported in §5.4...` → `§5.7` — mask-intervention rate and decoding-neutrality are
  reported in §5.7 ("Constrained decoding is load-bearing..."), not §5.4 (steering/amplitude).
  `:393`.
- `The consequence is reported in §5.7.` → `§5.11` — the occupancy-to-heating sign flip is
  reported in §5.11, not §5.7. `:460`.
- `size is measured directly, in §5.6.` → `§5.9` — the laundry/secondary-activity measurement is
  §5.9 ("One mechanism behind four failing checks"), not §5.6 (privacy). `:493`.
- `reported in §5.6 and §7.6...` → `§5.10 and §7.7` — the hot-water denominator-mismatch
  resolution is §5.10 (results) and §7.7 (limitations), not §5.6/§7.6. `:507`.
- `...appliance peak reported in §5.6...` → `§5.8` (×2, §7.2 and §7.7) — the six-hour peak
  result is §5.8 ("One appliance model, three diaries, peaks six hours apart"), not §5.6.
  `:1189`, `:1279`.

**B2 — "activity bands" → "age bands".** VERIFIED against Table 3 (post-renumber), whose row
labels are `Y25-44`, `Y45-64`, `Y_GE65` — age bands, not activity bands. Fixed all four
occurrences: `4J_manuscript_submission.md:86, 171, 615, 952`. No remaining "activity band"
string in the file (grep confirms).

**B3 — Figure 2 never pointed at.** VERIFIED. Figure 2's caption sat at the end of §1.5 with no
body sentence directing the reader to it; §3.5 carries both arguments named in the brief (the
handicap argument at `:363-364` pre-edit, the flat-seed argument at `:356-357` pre-edit). Added
one sentence at the end of §3.5's circularity paragraph: "Figure 2 sets the design out
schematically, with the null's flat seed and the shared-reference argument that keeps the
comparison from being a handicap in either direction." (`4J_manuscript_submission.md:369-371`).

**B4 — tables never cited by number.** VERIFIED. Checked each renumbered table's section for an
existing in-text citation; four had none (Tables 1, 2, 7, 8 [post-renumber] already were cited).
Folded a number into an existing sentence in each case, using post-renumbering numbers:
- Table 3 (§5.1): "There is no subset of Table 3 in which the method worked." `:632-633`.
- Table 4 (§5.2): "Three of the checks in Table 4 carry readings that qualify..." `:665-666`.
- Table 5 (§5.3): "Three points about how Table 5 is to be read." `:698`.
- Table 6 (§5.5): "None of the four quantities in Table 6 was supplied in..." `:766-767`.

**B5 — three ranges for the same multiple.** VERIFIED, partially in scope. Opened Table 6
(post-renumber, "Joint structure never present in the conditioning prompt"): its "Multiple of
band" column runs 5.0-6.7 / 3.3-4.7 / 4.6-7.9 / 4.8-8.6, so the table's real overall min/max is
**3.3 to 8.6**. Found exactly one prose statement of this specific quantity that disagreed: the
Figure 5 caption context said "between three and nine times the band"; fixed to "between 3.3 and
8.6 times the band" (`4J_manuscript_submission.md:769-770`). §6.2's per-row breakdown ("five to
nearly seven... three to five... four to eight") already paraphrases three of the table's four
rows correctly and was left alone.
UNVERIFIED / not touched: the pervasive "factors of two to six" / "a factor of two to six"
phrase (8 occurrences: abstract, highlights-adjacent text, §1.5, §5.1, §6.1, §6.7, §7.2, §8)
describes a *different* quantity — the primary transfer bar's own model/null margin (Table 3,
post-renumber) — not the joint-structure multiple the brief's "3.3 to 8.6" figure comes from.
Recomputing Table 3's own per-cell ratios (model MAE / null MAE) from its printed numbers gives
a real range of roughly 1.15 (Britain, oldest band) to 3.91 (Spain, middle band), which does not
match "two to six" either. Because this is a different, separately-supportable headline claim
(not "the same multiple" as Table 6's column) and changing it risks altering what the paper
claims rather than how it says it, I left it untouched and flag it here for the author/next
pass rather than editing it on my own judgement.

**B6 — "five of six" held-in reading belongs to the pilot arm.** VERIFIED. Source:
`Step6_docs/4thJ_06_transfer.md:2492-2516` (`FINDING 93`), which states the 5/6→2/6 correction
explicitly on "the pilot" ("the pilot reproduces a country it trained on worse than the model
that never saw it"; "expected of a 1.48 B two-epoch pilot"). The manuscript's Table 4 (post-
renumber) row for held-in regression (clause 1, 6/6 FAIL) is unaffected — that reading is the
same on both arms per the source. Edited §5.2's clause-2 sentence to read: "...initially read as
passing in five of six cells on the pilot arm and on re-derivation passes in two."
(`4J_manuscript_submission.md:673-674`).

**B7.** Skipped — lives in the supplementary material, out of scope per the brief.

**B8 — conditioning vector source.** VERIFIED against
`Step5_docs/outputs_step5/marginals_provenance.md:1-50` and `:206-209` (basis frozen by
`D-S5-1` as "the national statistical offices... the census round is the primary"; UK source is
"Nomis, the ONS census dissemination API... Census year 2011"; Spain source is "INE, Censos de
Poblacion y Viviendas 2011"). §2.2's "four Eurostat dissemination tables covering age,
self-declared economic status, household composition, and start-time distribution" did not
match this and did not match §3.4's own field list (age band, sex, household type, economic
status — confirmed against the same source, which builds exactly those four fields). Corrected
§2.2 to: "come from four national census tables covering age, sex, household composition, and
economic status." (`4J_manuscript_submission.md:164-166`), now consistent with §3.4.

**B9 — nulls counted three ways.** VERIFIED. `writing/4thJ_crossStep_analysis.md:453` counts
"two clean nulls" but those are the day-chaining convention and the occupancy-to-heating null
(§5.11/§6.5 territory) — unrelated to Figure 2. Figure 2 sits at the end of §1.5 and is
captioned "the two nulls", but the transfer design it depicts is described twice in the body as
having three nulls: "the three nulls and which of them is the bar" (§4.1) and "the three
registered nulls" (§5.1) — primary raked-donor null plus two secondary nulls (single-donor-
country and pooled-average, matching `G6.1`/`G6.2`/`G6.3` in `Step6_docs/4thJ_06_transfer.md`).
Corrected the manuscript's Figure 2 caption only, to "the three nulls"
(`4J_manuscript_submission.md:102`), matching the body's own repeated count. Per the brief, the
figure script was not touched — **the image itself may still need a fix to draw three nulls
instead of one; flagging for whoever holds `figures/`.**

**B10 — one country, four names.** VERIFIED via grep count. Title and abstract both use "United
Kingdom" (`:1`, `:5`). Body prose uses "Britain"/"British" as the working term in roughly 35-40
places (tables, results, discussion — already in place before this pass and self-consistent).
"Great Britain" appeared exactly once (`§3.7`, archetype count), and is factually wrong there
too: the same paragraph states two sentences later that "the British typology published by
TABULA covers England only, with no Scottish or Welsh row" — so labelling the archetype count
"Great Britain" contradicts the paper's own next sentence. **Kept "Britain"/"British" as the
term** (not "United Kingdom") because it is the document's overwhelmingly dominant, internally
consistent working form throughout the body (established well before this pass), and rewriting
~40 instances — several as adjectives ("British diaries", "British fold") where "United Kingdom"
does not substitute grammatically — is a much larger, riskier edit than a Tier-B consistency fix;
flagging for the author if a full title-form sweep is wanted. Fixed the one true outlier:
"32 for Great Britain" → "32 for Britain" (`4J_manuscript_submission.md:408`).
"England-parameterised" (§2.3, §3.7) was left untouched, as instructed — that is the genuine,
load-bearing distinction about the archetypes, not about the diaries.

**B11 — HETUS recommendation vs "guidelines not read".** VERIFIED. §2.1 asserted "sits below the
HETUS recommendation" for the Italian age floor, while the same subsection two sentences later
and the reference-list note both state the guidelines have not been read and no claim about
HETUS's requirements is made (`4J_manuscript_submission.md:152-154`, `:1419-1420`, pre-existing,
untouched). Removed the assertion, kept the disclosure and the factual age-floor statement:
"The age floor differs. Spain begins at age 10, Britain at 8, and Italy at 3..."
(`4J_manuscript_submission.md:141-142`). No citation added.

## Found but NOT in this brief

- The "two to six" vs Table 3's own real per-cell ratio range (roughly 1.15-3.91) — see B5 above.
  This looks like the same class of defect as B5 but is a different quantity from the one the
  brief's "3.3 to 8.6" number supports, so I did not touch it.
- Figure 2's image reportedly draws one null against a now-corrected "three nulls" caption — the
  script/image itself is out of my scope (another agent holds `figures/`) but will still read as
  inconsistent until fixed there.

## Final checks

`wc -l` on the edited file: **1421** lines (was 1418; +3 net from rewrapping three paragraphs
that grew past the house wrap width after the Tier-B edits — no prose content was cut).

`Table [0-9]+` audit (grep -noE, values only): `1, 2, 3, 4, 5, 6, 7, 8` — no gaps, no duplicates,
every caption has an in-text citation.
