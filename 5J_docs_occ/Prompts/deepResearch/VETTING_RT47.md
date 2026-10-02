# Vetting RT47 (reference support), 2026-10-01 14:17 EDT, 5J manager

Report: `RT47_reference_support.md` + `RT47_pages.log` (64 lines), returned by the author's outside tool on 2026-10-01.
Verdict: **MIXED.** The registry fields (Part 1) and the method sources (Part 2) are usable; the context quotes (Part 3) are not
usable until opened; Section A misjudges our list.

## Checks
1. **Claims about our own material (step 1).** Section A says "none [of the 17] is completely correct as written because all
   14 journal and technical report entries lack author initials, several omit full paper titles". False for the draft: it
   judged the short summary list in the T47 prompt, not `writing/5J_manuscript_draft.md`, which already carries full titles
   and initials for 11 of the 14. Discarded.
2. **Provenance (step 3).** The tool's own run log shows Crossref API calls for all 14 DOIs plus the negative control, so the
   Part 1 field values were read from the registry. Usable as document identity.
3. **Read-level contradiction.** Section G question 1 lists 14 documents opened in full and names Dai et al. 2025, Baetens and
   Saelens 2016 and Park and Park 2023 as "described only", yet Sections E and H mark them, and every other Part 3 source
   (Johari, Ferrando, Yan, Hong, O'Brien, Abbasabadi, Kavousian, Jones, Firth, Westermann, Ballarini, Caputo, Widen 2009), as
   "read full text". The quoted sentences in Section E (for example the Johari et al. 2020 quote) cannot be trusted as quotes.
   Part 3 is a LEAD LIST only; no sentence or number from it (for example "240-fold", "up to 3-fold", "38 dwellings") enters the
   paper unless the author opens the source.
4. **Controls.** Positive controls (Crawley 2001, 11 authors; Loga 2016) match the draft's own entries. Negative control
   returned not found. Pass.
5. **Rescuing direction (step 7).** None: no suggestion to change the method or a threshold.
6. **ASHRAE 2014.** Exists (catalogue), clause `CLAUSE NOT OPENED`; the "criteria remain" sentence comes from secondary
   literature, so the author's item on the 2014 clause stays open.

## Applied to the draft (14:16, backup in the manager's scratchpad `5J_manuscript_draft_pre_rt47.md`; md5 -> 6ea62229...)
* Initials from the registry: Dabirian S., Alamatsaz K., Eicker U.; He M., Lee T., Taylor S., Firth S. K., Lomas K.; Li Y.,
  Bae Y., Im P.
* Osman and Ouf title completed (": Data, methods, and applications").
* Method sources added in text and in References (canonical, low risk): HETUS guidelines (Eurostat, 2009) at Section 2.1;
  EnergyPlus 23.1 documentation (U.S. Department of Energy, 2023); ERA5 (Hersbach et al., 2020); histogram gradient boosting
  (Pedregosa et al., 2011; Ke et al., 2017); temporal convolution network (Bai et al., 2018); Transformer (Vaswani et al.,
  2017); cluster bootstrap (Davison and Hinkley, 1997). PyTorch is not named in the draft, so Paszke et al. was not added.
* Rule check re-run 14:16: exit 0, all plants fired, 0 citations without a reference (35 in text, 24 keys). One "uncited"
  hit is the checker failing to parse the author key "U.S." (the citation is in the text): a checker limit, not a draft defect.

## Left to the author (registry differs from the draft; the author knows these sources)
* Iseri et al. 2026: the registry gives the third author as **Sinan Kalkan** (draft: "Kalkan, B.").
* ISTAT 2016: the report gives the title as "I tempi della vita quotidiana. Anno 2014"; the draft has a longer title.
* Year of online versus print: Pan et al. (online 2024, print 2026, 19(5)), Park and Park (online 2023, print 2024, 17(3)),
  Dabirian et al. (online 2024, print 2025). Pick one rule for the journal.
* Part 3 context sources: open any you want to cite; the report's quotes are not usable as they stand.
* Part 4 data credits (INE, ISTAT, TABULA wording): check on the owners' pages; the INE wording matches our 2026-09-28 record.
* Section G question 3 names CityTFT (Dai et al., 2025) as a district surrogate; T46 (novelty search) should report it.
