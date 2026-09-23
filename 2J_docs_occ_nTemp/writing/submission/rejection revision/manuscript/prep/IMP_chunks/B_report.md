# Chunk B report (Methods, Appendix B, Nomenclature)

## Words (wc -w)
- Before: `B_methods_orig.md` 3561 (Section 2 plus symbol list).
- After: `B_methods_new.md` 3491; `B_appendixB_new.md` 839; `B_nomenclature_new.md` 469; total 4799.
  The growth comes from the four figure walk-throughs, one-symbol-per-line nomenclature, and the
  appendix lead-in sentences.

## Sentences over 30 words
- None in prose (script check, display equations and table rows excluded). Table 1 cells are unchanged
  apart from section numbers.

## Numbers dropped or changed
- No number dropped. All 18 equations checked verbatim against the original (only `\tag` changed).
- Old equation numbers (1 to 18) and old section numbers (2.7 to 2.12) no longer appear, by design.
- New numbers are only the figure walk-through values 0.6, 0.75 and 1.0 (plus 4 of 10, 6, 2), all taken
  word for word from the M1 and M2 prompt files.
- Hyphen ranges rewritten with "to": "0-1" -> "from 0 to 1"; "0-23" -> "0 to 23"; "09:00-17:00" ->
  "09:00 to 17:00"; "23:00-to-00:00 wrap" -> "wrap from 23:00 to 00:00".

## Cross-references changed (old -> new)
- Figure 1 caption "(Sections 2.1 to 2.12)" -> caption shortened; text says "Sections 2.1 to 2.6".
- Table 2 -> Table 1; stage column: (2.1, 2.2)/(2.3) -> (2.1, 2.2)/(2.2); (2.4)/(2.5) -> (2.3);
  (2.6) -> (2.4); (2.5, 2.8) -> (2.3, 2.5); (2.8, 2.9) -> (2.5); (3.6) kept.
- In text: Section 2.4 (matching) -> 2.3; 2.7 -> 2.5; 2.3 (raking) -> 2.2; 2.5 -> 2.3; 2.6 -> 2.4;
  2.10 -> 2.6. Sections 3.4, 3.8 and the Supplementary Information kept.
- Equations: 8, 9, 10, 12, 16, 18 -> 1 to 6; 1 to 7 -> B.1 to B.7; 11 -> B.8; 13 to 15 -> B.9 to B.11;
  17 -> B.12. Nomenclature uses the new numbers.

## Other moves
- Column names `slot_001`..`slot_144`, `home_001`..`home_144`, `act30_001`..`act30_048`,
  `hom30_001`..`hom30_048` moved from the main text to Appendix B (under B.1 and B.2).
- The inline hour-averaging formula ($\text{occ24}$) moved to Appendix B after Eq. B.7; the main
  text says it in words and points to Appendix B.
- Inline metric formulas (LF, midday, ramp, $\bar{x}$, jump) stay in the main text.
- The two zero-weight loss terms are one plain sentence in Appendix B.

## Doubts
- Original said training "maximizes" the negative log-likelihoods; I wrote "minimizes" (the correct
  sense for a loss). Author should confirm.
- The M3 prompt lists dishwasher among "Shared devices", while Eq. 1 treats the dishwasher as a
  separate term (also scaled by $\eta$). The text walk-through does not mention the dishwasher.
- Symbol clashes kept from the original and now stated in the Nomenclature: $a$ is archetype (Eq. 4)
  and activity (Eq. 1); $c$ is city (Eq. 4) and cell (Eq. 6).
- The Nomenclature follows the old symbol list only. Symbols defined only in the text ($n_t$,
  $P_{\text{dw}}$, $E_{\text{raw}}$, $E_{\text{tgt}}$, $y$, $\text{Pool}_c$, $t_{0.975,n-1}$, $n$,
  $\theta_i$, LF) are not added; the manager may want them.
- The phrase "the comparison arms" is used once as a name for the two simplified methods (old heading
  "Comparison arms").
