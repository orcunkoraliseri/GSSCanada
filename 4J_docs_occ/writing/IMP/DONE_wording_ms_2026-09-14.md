# Wording repair (failure -> limitation register) and two other edits - manuscript - 2026-09-14

Task doc: prompt given directly (three tasks: failure-word sweep, capacity-sentence softening,
section 7 held-in addition). Scope: `writing/submission/4J_manuscript_submission.md` only.

Backup taken and verified non-empty before any edit:
`writing/submission/previous/4J_manuscript_submission.md.bak_pre_wording`.

## Self-proof counts (grep / wc -l only, no PowerShell)

| Metric | Before | After |
|---|---:|---:|
| Total lines | 1421 | 1456 |
| Uppercase `FAIL` tokens (`\bFAIL\b`) | 6 | 6 (unchanged) |
| `failure` (case-insensitive, whole word) | 38 | 0 |
| `failures` | 2 | 0 |
| `fail` (whole word, includes the 6 `FAIL`) | 10 | 6 |
| `fails` | 30 | 0 |
| `failed` | 9 | 0 |
| `failing` | 30 | 0 |
| Combined family total (`\b(failure\|failures\|fail\|fails\|failed\|failing)\b`, case-insensitive) | 119 | 6 |
| Em dash (U+2014) | 0 | 0 |
| En dash (U+2013) | 0 | 0 |

The 6 remaining hits after the pass are exactly the 6 uppercase `FAIL` verdict tokens in Table 4
(Budget agreement, Frozen limitation criteria, Held-in regression, Fictional country, Joint
structure, Country discrimination), left verbatim as instructed. Every other occurrence - 113
prose instances - was rewritten. Line count rose by 35, entirely from re-wrapping the touched
paragraphs at ~100 columns plus the two new sentences added to §7.1 (Task 3); no paragraph was
shortened or dropped.

Method used throughout: `py -3`, guarded `str.count(old) == 1` before every replace, applied in 10
sequential batches (front matter as direct single-line substitutions; every hard-wrapped paragraph
from §2 onward dewrapped, edited, and re-wrapped with `textwrap.fill(width=100)`, with a follow-up
pass using `break_on_hyphens=False` to remove five awkward mid-hyphenated-word line breaks that the
first wrap pass introduced, e.g. "real-\nagainst-real"). Every touched paragraph was then re-read in
full from the file (not just grepped) to confirm it still reads correctly; excerpts below.

## Task 1 - replacement vocabulary chosen, and why

No mechanical one-for-one substitution was used; each sentence was reworded so the English stays
natural. Recurring patterns and the word chosen for each:

- **"the transfer bar/claim fails/failed"** -> "is not met" / "does not hold" / "falls short"
  (headline claims - §5.1 heading, Abstract, §1.4, Conclusion).
- **"a failing check/gate/bar"** -> "a check/gate that does not clear its bar" or "misses its bar"
  (used consistently for every individual check verdict in §5.2-§5.10, §6.5, §6.6, §7.5, §7.7, §7.9,
  §7.10).
- **"the failure" (noun, referring to the study's result)** -> "the shortfall" (used throughout
  §1.5, §5.2-§5.9, §6.1-§6.7, §8). Chosen because it is register-neutral, reads naturally as a
  repeated noun across many sentences, and is not itself an item on the excluded list.
- **"a hard failure" (engineering sense: the raking process halts rather than silently degrading)**
  -> "a hard stop" (§3.5) - preserves the "halts loudly" meaning without the excluded word.
- **"was seen failing" / "must be seen failing" (mutation-testing idiom: a check must register as
  not-clearing when a fault is deliberately injected, to prove it can detect that fault)** -> "was
  seen to catch the injected fault" / "must be shown to catch a deliberately injected fault" (used
  identically in §1.5, §3.3 intro, §3.9, §4.5, §5.10, §6.6, §8, so the idiom stays recognisable on
  re-read even though the literal word is gone).
- **"the one failure" / "the single failure" (one check out of many, singled out as an exception)**
  -> "the one exception" / "the single exception" (§3.1, §3.2) - fits the "sixteen passed, the
  one ___" sentence shape better than "shortfall" would.
- **"a crash is not a failure"** -> "a crash is not the same as a check that misses its bar" (§6.6) -
  the point being made is that a crash is a *different kind of thing* from a legitimate miss, so the
  rewrite keeps the contrast explicit rather than compressing it into one word.
- **"840 failed cells" (simulation cells, not a check verdict)** -> "840 cells that did not
  complete" (§7.10) - this "failed" was describing incomplete/errored simulation runs, not a gate
  verdict, so it gets a description of what actually happened rather than "shortfall" vocabulary.
- **"could not fail" (a circular check that cannot possibly disagree with itself)** -> "could never
  come up short" (§3.1).
- **"Frozen failure criteria" -> "Frozen limitation criteria"** and **"pre-declared failure
  conditions" -> "pre-declared limitation conditions"** (Table 4 row and its companion mention),
  exactly as specified, matching the supplementary-material repair.

## Task 2 - the three capacity sentences, as they now read

**Abstract** (compact form, inside *Key quantified results*):
> Across the range tested here, from 1.5 to 7.3 billion parameters, with the full-parameter tuning
> and the second model family each assessed on one fold, more capacity does not close the gap: a
> 4.7-fold larger backbone moves mean absolute error from 42.05 to 43.14 minutes per day, the wrong
> way; training all 7,377,965,056 parameters instead of the adapter's 79,953,920 ends at a higher
> training loss at every epoch; and a second 7 B model family changes nothing any gate resolves.

**§5.3** (heading, since in this manuscript's house style section headings already carry the full
topic sentence - e.g. §5.1, §5.9, §6.1 are likewise full sentences, not noun phrases):
> ### 5.3 More capacity does not close the gap, across 1.5 to 7.3 billion parameters, measured
> three ways

**§6.1**:
> What the shortfall is not is a capacity limitation, and this matters because capacity is the first
> explanation a reader will reach for. Three independent measurements argue against it, each within
> the scope actually tested: backbone size from 1.5 to 7.3 billion parameters, with the
> full-parameter tuning and the second model family each assessed on one fold. Increasing the
> backbone by a factor of 4.7 moved mean absolute error in the wrong direction [...]

All three carry both required elements: the tested range (1.5 to 7.3 B) and the one-fold scope of
the full-parameter tuning and the second-family comparison. The finding itself (capacity does not
close the gap) is unchanged - only the certainty of the claim is qualified, per the ruling.

## Task 3 - the held-in-regression addition to Section 7

Verified first, against the manuscript's own body text, exactly as instructed - no new number was
computed and no Step-6 file was opened. The reading is supported at two places:

- Table 4 (§5.2), row text (unchanged by this task other than the "Frozen limitation criteria"
  relabelling): `| Held-in regression | training-country prefixes must clear the same bar | MAPE at
  or below 15 per cent | FAIL, 6 of 6 |` - i.e. all 6 of 6 training-country cells miss the bar.
- §5.2 prose: "The held-in regression check was corrected downward during analysis rather than up.
  Its second clause was initially read as passing in five of six cells on the pilot arm and on
  re-derivation passes in two." This confirms the 6-of-6 figure is the corrected (worse), final
  number, not a stale or optimistic one.

"6 of 6" is fully supported. Added to the end of the first paragraph of §7.1 (placed there rather
than as a new subsection, since §7.1 is already the section about what the corpus and the split can
and cannot decide, and the addition directly qualifies that same question):

> One further limitation qualifies the paper's own transfer framing directly: the held-in regression
> check, which asks whether the model reproduces the training countries it has already seen, does
> not clear the same bar on any of the six training-country cells (Table 4). The shortfall is
> therefore not confined to transfer; the model misses the same bar in-sample, on countries it was
> trained on, which qualifies how much of the deficit the title's transfer framing can be read to
> explain.

## What was NOT changed, and why

- The 6 uppercase `FAIL` verdict tokens in Table 4 - registered gate-verdict definitions, per the
  explicit exception.
- Nothing else was declined; all three tasks reproduced as described and were applied in full.

## Files touched

- `writing/submission/4J_manuscript_submission.md` (edited).
- `writing/submission/previous/4J_manuscript_submission.md.bak_pre_wording` (backup, created before
  any edit).
- This report.

No other file under `writing/`, no supplement, no figure script, and no tool under `tools/` was
opened for writing.
