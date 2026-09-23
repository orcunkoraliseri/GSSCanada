# E (Supplementary Information) rewrite report

## Words
- Before: 4,575 (`wc -w E_SI_orig.md`). After: 4,784 (`wc -w E_SI_new.md`). The small growth comes from splitting sentences and from the new lead-in paragraphs for Table S2 and Figures S1 and S2.

## Sentences over 30 words
- None in prose. A scripted check shows one case at 32 words, but only because the bold run-in label is counted with the sentence: "**Consequence for the comparison with the earlier simulation campaign.** The schedule files used in this paper are numerically close to, but not identical to, those of the authors' earlier simulation campaign (Section 3.6)." The sentence itself is 25 words.
- Table cells were not rewritten (see below).

## Numbers
- No numbers were dropped, rounded or added. A scripted comparison of all numbers shows only the cross-reference changes listed below. Every other difference is punctuation, such as "2015," becoming "2015.".
- "1.8-2.1%" (Section S4) became "1.8 to 2.1%" (rule 5, ranges use "to"). "0.11 %" became "0.11%".

## Cross-references changed (old -> new)
- Section S10, prose: "Section 2.11's paired-difference interval (Eq. 16)" -> "The paired-difference interval of Section 2.6 (Eq. 5)".
- Table S3, two cells: "Plain pooled (Eq. 16)" -> "Plain pooled (Eq. 5)". This is the only change to table cells.
- "Section 3.6" (Section S8) was kept, as instructed.
- No other main-paper section, equation, table or figure numbers occur in the SI. "The main text" is referred to twice without a number, and both were kept.

## Layout and captions
- Table S1 caption kept as it was (already one short sentence). The paragraph that followed the caption ("Final model: ... out of more than 40 candidates tried") was moved into the S1 paragraph that cites Table S1.
- Table S2: a short lead-in paragraph now cites Table S2 before its caption. The facts come from the SI. The original S1 paragraph cited S1 and S2 together; now Table S2 is first cited right before it appears.
- Table S3: the note "All values are fractions; multiply by 100 for percentage points." was moved from under the table into the paragraph that cites it.
- Figures S1 and S2: the long captions were cut to one sentence each. All the removed content (sample sizes, bootstrap details, the stars, the 21 scenarios, the 19 of 21 result) is now in a new paragraph before each figure. The two figures are no longer back to back.

## Doubts
1. Table S1 is a model card made of four markdown sub-tables, divided by italic sub-headings and one note. They are not separated by full paragraphs. I treated them as one float (Table S1). If the manager's "no two tables in a row" check reads them as four tables, the sub-heading structure may need a decision.
2. One process-style clause was dropped from Table S2 (rule 6): "the underlying per-code crosswalk is not reproduced here". It has no number and states no research fact. Restore it if the author wants the pointer.
3. Existing inconsistency, not changed: the Table S1 notes give cross-attention co-presence errors as "20 or more percentage points", while Section S2 gives "19 to 23 percentage points". Both were kept exactly.
4. The Table S3 cells were changed for the Eq. 5 mapping, even though the rule says cells stay unchanged. Otherwise the table would point to the wrong equation.
