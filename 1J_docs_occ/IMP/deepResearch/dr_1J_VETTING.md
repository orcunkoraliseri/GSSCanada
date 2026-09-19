# Vetting of the six Gemini reports dr_1J-01 to dr_1J-06 (2026-09-19)

Vetted by the manager, offline, before any value enters the paper. Method: every quoted string in each
report was matched against the source files on disk (script and full output in the session scratchpad,
`vet_quotes.py`, `vet_short.py`; long quotes were re-checked with short key phrases because PDF text
extraction breaks long matches). The Gemini session's own action log (pasted by the author) was read to
see which sources it actually opened.

## Read this first: three things that break the round's design

1. **Gemini ran with access to our disk, so nothing was withheld.** It read `00_REVISION_PLAN.md` (the
   P1 to P10 list), `4J_manuscript_submission.md`, our microdata and the PUMF user guides. So:
   dr_1J-06 was *not* blind to P1 to P10, dr_1J-02 quoted our own household-size numbers back
   ("18.2 h at 1-person vs 5.2 h at 5-person", source given as "Internal manuscript text"), and
   dr_1J-03's Quebec counts were computed from our own files, which makes its control circular.
2. **"Opened in full" is not true for most outside papers.** The action log shows full-text downloads
   only for three arXiv PDFs (Borysov 2019, Garrido 2020, Johnsen 2021), the Yin 2024 copy on disk,
   our GSS 2005 and 2015 guides and the census PUMF guides. Every other paper was touched only through
   Crossref metadata or `search_web`. Quotes attributed to those papers are unverified and several are
   certainly invented (below).
3. **Gemini edited our plan.** It ticked §4 and wrote log entry (d), which claims "independent" review
   and "definitively disproving" the NHS hypothesis. Both claims are wrong; corrected in entry (e).

Quote match counts (exact string found on disk / partial / not found):
dr_1J-01 5/2/100, dr_1J-02 4/0/22, dr_1J-03 8/9/31, dr_1J-04 4/6/12, dr_1J-06 6/1/23 (dr_1J-06 rises to
about 20 of 22 PDF quotes when checked by key phrase; most misses were extraction artefacts).

## Verdict per report

### dr_1J-01 novelty search: FAILS as evidence; salvage the candidate list
- Control (Richardson 2008) found, but it is a famous paper, so the control proves little.
- 100 of 107 quotes cannot be traced to any opened text. One is certainly invented: the Yin 2024 row
  "quotes" *"stops at statistical activity modeling without physical building energy simulation"*,
  which is not in the Yin paper on disk; it is the report's own opinion in quote marks.
- The verdict "HOLDS: novelty claim holds firmly" is in the rescuing direction and rests on unread
  papers. **Do not use it.**
- Salvage (document identity only, the author must open each before citing):
  - **Dias dos Santos, Moghadasi and Paez (2025), Environment and Planning B, DOI 10.1177/23998083241280385**:
    said to harmonise seven Canadian GSS time-use cycles 1986 to 2015. If true, it is the closest
    Canadian multi-cycle precedent and must be cited and distinguished. Highest priority.
  - Chen et al. (2022) Applied Energy 325:119890 (ATUS plus ResStock), Osman et al. (2023) B&E 241:110490
    (GSS 2015), Mitra, Steinmetz, Chu and Cetin (2020) E&B 210:109713, Mitra, Chu and Cetin (2021)
    E&B 236:110791, Anderson and Torriti (2018) Energy Policy (UK 1974 to 2014).
  - Suspect metadata: Tanimoto et al. 2008 DOI (search in the log failed, DOI then appeared), Kleinebrahm
    2023 "Japanese microdata" (a German group), Wilke 2013 quote wording.

### dr_1J-02 cross-national findings: FAILS; the design was defeated
- Control passes: the three Yin quotes and the Table 4 values (17.2 to 15.3 h etc.) are on disk.
- But the Yin rows are filed under "total time at home", while Table 4 is sleep plus work plus
  housework. Work is not time at home. Misclassified.
- Our own numbers were echoed back and then "explained" (T4 row in section 3). An echo is not a finding.
- All other quotes (Sekar, Mitra/Cetin series, Richardson, Jeong, Koupaei, ONS) were never opened.
  Ranges like "1.6 to 2.4 additional hours" and "8 to 12 percentage points" have the shape of
  invented magnitudes.
- Salvage: BLS ATUS 2023 news release (work-at-home share 24 % in 2019, 34 % in 2022, 35 % in 2023);
  the author opens it before use.

### dr_1J-03 GSS and census methodology: PARTLY SURVIVES
Confirmed on disk:
- GSS 2005: 19,597 respondents, response rate 58.6 %, collection to mid-December, CATI,
  province-age-sex adjustment, bootstrap weights (12M0019GPE.pdf, pp. 9 to 23).
- GSS 2015: 17,390 usable responses, response rate 38.2 % (PUMF GSS 2015.pdf).
- 2006, 2011 and 2021 PUMF record counts and "smallest geographic unit is the CMA" (user guides).
- 2011 NHS response rate 68.6 % and the official caution sentence (NHS user guide, ch. 1).
Not supported:
- **Every 2010 (Cycle 24) and 2022 quote.** No 2010 or 2022 user guide is on disk (only data
  dictionaries) and the log shows none was fetched. The 2010 dictionaries say nothing about the
  weighting basis.
- The 2005 "aligned with ATUS" quote (not in the 2005 guide).
- Census response rates 96.5 / 97.8 / 97.4 % (not in the guides on disk).
- The 2016 PUMF household count: the report says 140,705; our `cen16.dat` (PRIHM = 1) gives **140,720**,
  and the 2016 user guide's own text says "140,720 private households". The report's figure is wrong.
  The 2016 person count (343,330) and the 2021 counts (361,915 persons, 149,789 households) are correct.
- Quebec counts: computed by Gemini from our microdata, then presented as guide quotes. Control void.
- Section 4's "true anomaly is the 264-code classification" is an interpretation the prompt forbade.
  Struck.
**P3 status:** not closed by this report. The chronology alone (GSS 2010 collected before the May 2011
NHS) is enough to delete the NHS sentence. The replacement sentence must say the 2010 dip is
unexplained unless the Cycle 24 user guide is opened and quoted. Also note: the paper gives the 2006
Census response rate as 93.5 % (PDF pp. 5 and 13); verify that number in WP2.

### dr_1J-04 validation methods: PARTLY SURVIVES
Confirmed in the downloaded PDFs:
- Borysov 2019: SRMSE on marginal, bivariate and trivariate distributions ("Following Hu et al."),
  Pearson r and R2, Cramer's V for all pairs, nearest-sample distance for diversity, rule-based checks
  for impossible combinations ("driving license", "no silver bullet").
- Garrido 2020: sampling zeros defined as test-set combinations absent from training; the recovered
  share "should approach 1"; structural zeros counted alongside.
- Johnsen 2021: an empirical conditional-table baseline drawn from the training set; SRMSE mean and
  spread across cross-validation folds (0.564 is on p. 8).
- **None of the three papers mentions random seeds.** The seed statements are not from them.
Not supported:
- Sun and Erath 2015, Badu-Marfo 2022, Salvini and Miller 2005, Waddell 2002, Harland 2012 quotes (never
  opened). The Waddell quote says the model "outperformed simple carry-forward and linear extrapolation
  models", which are exactly our prompt's baselines: framing echo. Salvini DOI is malformed.
- False claim that our prompt supplied two wrong DOIs. It supplied none.
- "No paper drifts a latent space" = not found in a short search, not evidence of absence.
- The 5-seed protocol is advice, not a finding. The pass rule was not touched (good).

### dr_1J-05 StatCan 2024 to 2026 tables: SURVIVES (control passed)
- Control table 98-10-0041-01 was taken from the official CSV (download is in the log). Checked by a
  read-only helper against `cen21.dat` (Quebec PR = 24, PRIHM = 1, 37,512 households; WEIGHT is one
  constant in Quebec, so weighted = unweighted): 1p 35.12 %, 2p 34.57 %, 3p 12.79 %, 4p 11.42 %,
  5+ 6.09 %. Every share is within 0.02 points of the report. **Control passes.**
- Montreal is identifiable in both 2016 and 2021 PUMFs: variable `CMA`, code 462 (both user guides);
  40,003 person records in 2016 and 41,978 in 2021.
- Useful result: **no 2024 to 2026 table exists for household size or dwelling type**, for Quebec or
  Montreal. The 2025 cohort can be checked only on age and sex, labour force status, class of worker,
  hours and occupation (Quebec), and commuting and work-from-home (May 2024).
- Copied values (work-from-home 18.4 % Quebec, 20.6 % Montreal; mode shares) are not yet checked;
  re-read them on the Daily pages before use.

### dr_1J-06 mock second reviewer: PARTLY SURVIVES
- Its PDF quotes and page numbers are real (checked by key phrase).
- Not independent: 12 of its 15 points are P1 to P10, which it read in our plan. They confirm pages
  only.
- **Three new points, not in our plan, confirmed in the PDF:**
  - N1: "Canadian residential codes should consider correction factors of approximately +10% for
    heating and -20% for cooling" (p. 22), drawn from one city, one weather file, four archetypes.
  - N2: the jump from a 17.4 % peak cooling reduction to "18% cooling oversizing" (p. 22) is not
    explained.
  - N3: Objective 2 promises results "across Canadian climate zones" (p. 4); only Montreal is simulated.
- Overlap section: unverified. The eSim title it gives, with "(1992-2022)", does not match any file
  we hold, and the "companion" Energy and Buildings paper (10.1016/j.enbuild.2026.117155) needs the
  author's confirmation. The author knows their own publications; no agent should chase this.
- "Pool of 100 single-detached households" (M6) is unverified.

## Carried into the plan
New plan items P11 (N1), P12 (N2), P13 (N3) and P14 (overlap and prior-version disclosure); P3
wording updated; §4 literature list gains the Dias dos Santos et al. (2025) item.
