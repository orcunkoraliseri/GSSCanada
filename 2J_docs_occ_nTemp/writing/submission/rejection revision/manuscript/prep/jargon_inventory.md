# Jargon inventory: self-defined labels in the archived manuscript

Built 2026-09-15 by T33 (WP10 prep). Source file: `archive/2J_manuscript_submission.md` (read in
chunks, never whole). "Count" below means the number of lines the term appears on (a term repeated
twice on one line still counts as one line). Line numbers are from the archived file as it stands now;
they will shift once WP10 starts editing a working copy, so re-grep before quoting a line number in the
new manuscript. Replacement suggestions are marked SUGGESTED; none are final wording.

| Term | Count (lines) | Line numbers | First-use line | Proposed plain replacement (SUGGESTED) |
|---|---|---|---|---|
| calibrated J3 | 5 | 115, 208, 215, 266, 304 | 115 | "the model" or "the generator" (after one plain description at first use: "a machine-learning model that fills in each person's missing days") |
| J3 | 7 | 115, 208, 210, 215, 266, 304, 455 | 115 | same as above; drop the code name entirely from the main text, keep it only in the SI table |
| True-Future-Test | 6 | 10, 24, 117, 122, 241, 616 | 10 | "future-year check" or "held-out-year test" |
| paired frozen-frame | 3 | 122, 439, 485 | 122 | "matched-household comparison" (same building and household compared only across years) |
| frozen frame (includes "frozen-frame" occurrences without "paired") | 6 | 122, 318, 325, 439, 485, 487 | 122 | same as above |
| Tier-1/Tier-2/Tier-3 | 2 | 225, 463 | 225 | "closest-match", "next-best match", "broad match" (or simply describe the fallback in one sentence, drop tier numbers from the main text) |
| FailSafe | 2 | 225, 463 | 225 | "last-resort match" (note: never actually used, 0.00% of cases; say so plainly) |
| COLLECT_MODE | 3 | 143, 208, 465 | 143 | "how the survey was collected (phone vs. online)" |
| DDAY_STRATA | 1 | 196 | 196 | "day-type group (weekday, Saturday, Sunday)" |
| Step-8 | 2 | 383, 461 | 383 | drop the step number; name the actual action ("the simulation run") |
| Step-9 | 2 | 421, 461 | 421 | drop the step number; name the actual action ("the end-use split") |
| occACT | 1 | 194 | 194 | "activity code" |
| gate / gates | 19 | 10, 23, 49, 115, 170, 202, 206, 208, 210, 227, 241, 247, 268, 310, 385, 398, 421, 473, 634 | 10 | "pass/fail check" or "quality check" |
| PASS | 4 | 241, 270, 310, 356 | 241 | "passed" (plain verb, keep only in SI scorecards) |
| WARN | 3 | 270, 310, 356 | 270 | "minor issue noted" |
| INFO | 2 | 270, 356 | 270 | "for information only, no issue" |
| C-VAE | 3 | 90, 105, 115 | 90 | keep the name but define it at first use (R1-D3): "a conditional variational autoencoder (C-VAE), a type of generative model used in our own earlier work" |
| MDLM | 2 | 115, 206 | 115 | keep only in SI; in main text say "a masked-diffusion alternative we tested" |
| SEDD | 2 | 115, 206 | 115 | keep only in SI; in main text say "a second diffusion alternative we tested" |
| calibration closure | 0 | (not found as a literal phrase) | n/a | not applicable as a text edit; this is the reviewer's own description (R2-6) of the SHEU-agreement framing, which does need rewriting so it is not read as independent validation |
| forecast | 33 | 3, 10, 17, 24, 59, 71, 77, 92, 97, 99, 107, 117, 120, 122, 188, 233, 235, 241, 318, 342, 368, 383, 385, 405, 409, 435, 437, 461, 467, 473, 479, 487, 613 | 3 (title) | already decided (R2-3, accepted): replace with "scenario-based projection" throughout, count only, no per-line suggestion needed |

## Additional coined/step labels found while reading (not on the starting list)
| Term | Count (lines) | Line numbers | First-use line | Proposed plain replacement (SUGGESTED) |
|---|---|---|---|---|
| DRIFT_MATRIX | 1 | 237 | 237 | "the year-to-year change table" |
| hindcast | 1 | 117 | 117 | ordinary English word, not jargon; no change needed |

## WHAT I DID NOT VERIFY
- Did not scan the Appendix/SI figure captions (lines 599 to end) for further occurrences of every term;
  counts above cover the main body (Front Matter through References, lines 1 to about 598) which is where
  reviewer 2's complaint is aimed.
- "gate" count includes a few incidental uses of the plain English word (e.g. "gate-selected") as well as
  the coined pass/fail sense; a human pass is needed before deciding which of the 19 lines need rewording
  versus which are fine as ordinary English.
- Did not re-run the search on any working copy; WP10 has not started, so no manuscript file exists yet
  under `manuscript/` besides this prep folder.
