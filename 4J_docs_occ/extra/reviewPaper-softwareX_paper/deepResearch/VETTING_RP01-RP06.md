# Vetting record — RP01 … RP06

Vetted 2026-08-21, before any sentence of `REVIEW_SOFTX-D-26-00798R1.md` was changed.
Method: `feedback_deep_research_is_external` (re-derive, do not trust) plus the `FINDING 47`
rule — a citation must match **title, journal, volume, issue, pages and first author**, not
just title.

Every DOI below was resolved through the CrossRef REST API (`api.crossref.org/works/<doi>`)
and the returned metadata compared field by field against what the response claimed.

## Verdict

**All six responses are usable.** No fabricated reference was found — a better result than
`RL17`/`RL24`/`RL25`, where fabrication did occur. Four defects, listed below; two are real
citation errors and two are over-claims. None invalidates the substance of any response.

---

## Verified clean — 19 of 20 DOIs exact

Title, journal, volume, issue, pages and first author all matched for:

Richardson 2008 · Widén & Wäckelgård 2010 · Wilke 2013 · Aerts 2014 · Flett & Kelly 2016 ·
Page 2008 · Osman & Ouf 2021 · Vosoughkhosravi 2023 · Mitra 2020 · Mitra 2021 · Chen 2022 ·
Allcott 2011 · Ito, Ida & Tanaka 2018 · Gyamfi & Krumdieck 2011 · Albadi & El-Saadany 2008 ·
Andor 2020 · Snoke 2018 · Paninski 2003.

Also confirmed by CrossRef search, having been asserted without a DOI:

| Claim | Resolved to | Status |
|---|---|---|
| Deng & Peng 2026, *Buildings* 16(5) 887 (RP03 B11) | `10.3390/buildings16050887` | **exact** — a real, directly comparable LLM occupant-agent paper |
| Argyle 2023, *Political Analysis* 31(3) 337–351 (RP03 B2) | `10.1017/pan.2023.2` | **exact** |
| Bisbee 2024, *Political Analysis* 32(4) 401–416 (RP03 B3/B4) | `10.1017/pan.2024.5` | **exact** |
| Iseri 2026, *Energy and Buildings* 357, 117155 (RP03 B16) | `10.1016/j.enbuild.2026.117155` | **exact** — our own Paper 1 |

RP02 and RP04 each self-reported a citation defect they caught and corrected during their own
run (a wrong Widén DOI pointing at Orosa & Oliveira; a wrong Ito DOI; a wrong Torriti DOI).
Both corrections check out. That is the behaviour we want and it raises my confidence in both.

---

## Defect 1 — RP01, Buttitta 2020: DOI does not resolve, title and journal both wrong

RP01 reference 15 gives *"Buttitta, Finn & O'Donnell (2020), 'Active occupancy and domestic load
modelling: A UK survey-based stochastic approach', Building and Environment 178, 106886,
DOI 10.1016/j.buildenv.2020.106886"* and marks it **"Crossref verified"**.

`10.1016/j.buildenv.2020.106886` returns **HTTP 404**. CrossRef search finds no paper of that
title. The nearest real Buttitta paper is `10.1016/j.enbuild.2019.109577`, *Energy and Buildings*
**206**, 109577 — different journal, different volume, different title.

🔴 The "Crossref verified" annotation is therefore not reliable on its own. Treat it as a claim
to be checked, exactly like the underlying citation.

## Defect 2 — RP01, Malekpour Koupaei 2022: wrong pages and wrong first-author surname

RP01 gives pages **754–773** and first author **"Koupaei"**. CrossRef returns pages
**776–790** and family name **"Malekpour Koupaei"**. DOI, title, journal and volume/issue are
correct. Use `Sci. Technol. Built Environ.` 28(6), **776–790**, first author **Malekpour Koupaei**.

## Defect 3 — RP03, Cheng, Piccardi & Yang 2023 (CoMPosT): wrong pages

RP03 B5 gives EMNLP 2023 pp. **11335–11351**. CrossRef (`10.18653/v1/2023.emnlp-main.669`)
returns pp. **10853–10875**. Paper is real and the finding it supports is correctly described.

## Defect 4 — RP06, the ATUS multi-year pooling rule: right in effect, wrong as a citation

RP06 B11 states the official rule as *"divide `TUFINLWGT` by the number of pooled years K"* and
attributes it to *"BLS ATUS User's Guide, Ch. 7, Section 7.3, p. 71"*.

I downloaded the User's Guide and searched it. **It does not say that, and not at that page.**
What it actually says is two separate things:

1. **p. 37** — a weight-*comparability* rule RP06 omits entirely: which weight variable is valid
   for which span (`TU06FWGT` for 2003–05, `TUFINLWGT` for 2006–19 and 2021+, and **`TU20FWGT`
   for 2020, which is special**). Combining years with non-comparable weights is the actual
   documented hazard.
2. **p. 95–96** — *"When working with multiple years of ATUS data, the denominator is the sum of
   all days in the multi-year period. For example, when working with the 2003-06 data combined,
   the denominator would be 1,461 (365+366+365+365) days."*

Dividing the weight by K and dividing the day denominator by K are algebraically the same for
means and proportions, so RP06's **effect** claim (proportions unaffected, absolute totals
overcounted by K) stands. But the rule as phrased and located is not in the guide, and the
comparability requirement — the one that actually bites — was missed.

**Verified independently and correct in RP06:** `TELFS` code structure (1–2 employed, 3–4
unemployed, 5 NILF); the day-of-week allocation (*"10 percent of the sample is allocated to each
weekday, and 25 percent … to each weekend day"*, p. 13); that `TUFINLWGT` corrects it (*"the
weights … were constructed so that each day of the week is correctly represented"*, p. 37);
final weights are person-days; and secondary activities — verbatim, p. 57: *"With the exception
of the care of children under age 13, information on secondary activities is not collected in
ATUS."* (RP06 B18 adds eldercare; the guide's own definition names only children under 13.)

---

## Over-claims to not repeat as fact

* **RP03 B12** — *"exactly 0 published BEM LLM-agent studies validate against measured occupant
  microdata."* Sourced to the response's own systematic search and marked Tier 1. An absence
  found by one search is not a Tier 1 fact. Plausible and useful as a hypothesis; do not assert
  it in print without our own search. (`FINDING 47` is the precedent: a confident
  "CrossRef-verified" absence was wrong.)
* **RP06 B3** — the ~850 vs ~125 unweighted counts for age 25–44 not-employed vs unemployed.
  Marked "fact" but no computation is shown and no BLS table gives it. The **structural** claim
  (`TELFS ∈ {3,4}` vs `{3,4,5}`, differing by roughly an order of magnitude) is solid and is all
  the review relies on. The specific numbers are not verified — the review says "on the order of
  10² versus 10³" for that reason.
* **RP06 B15** — the 10/7 and 4/7 day-weight factors. Arithmetically implied by the design but
  **not stated in the User's Guide**. Do not quote them as documented.
* **RP05 B7/B8** — arXiv IDs 2605.19537, 2608.04714, 2606.26185. Not resolved (arXiv is not in
  CrossRef and these are within the last three months). Unverified; the review does not rely on
  them. The one RP05 claim the review does use — batch-size-dependent reduction kernels as the
  dominant cause, He (2025), Thinking Machines Lab — is well known independently.
* **RP02 ref 16** — self-flags that the CrossRef title for scikit-mobility differs from the one
  given. Harmless, but it shows the response's own title-matching was not always applied.
* **RP02 ref 19** — Chen, Liang, Hong & Luo 2017, *Applied Energy* 203, 321–333. Not verified;
  the title given may be conflated with a different Chen/Hong paper. Check before citing.
* **RP01/RP02 downstream energy percentages** (lighting 20–45%, HVAC 12–28%, DHW 30–60%) are
  Tier 2 and attributed to sensitivity studies rather than quoted from a table. The review states
  the direction and the mechanism, not these figures.

---

## What was used in the review, and on what basis

| Review point | Rests on | Basis |
|---|---|---|
| P1 grounding-table coverage | **nothing from RP01–RP06** | measured directly from the released package |
| P2 KL floor | RP02 B1/B3 for the theory | plus a bootstrap null I computed from the package's own tables |
| P3 durations | RP01 B16 / RP02 B8–B10 for the mechanism | plus measurement against durations shipped in the package |
| P4 lineage | RP01, all DOIs re-resolved | Buttitta dropped (Defect 1); Malekpour Koupaei corrected (Defect 2) |
| P5 stratum O4 | RP06 B2 (`TELFS` codes), verified | counts deliberately given only as orders of magnitude |
| P6 social norms | RP04 B5/B7/B15, all DOIs re-resolved | RP04's scoping correction adopted — it improved the point |
| P7 reproducibility | RP05 B2 | uncontroversial and independently known |

Nothing entered the review on the strength of a response alone.
