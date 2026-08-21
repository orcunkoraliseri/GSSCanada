# P06. ATUS operationalisation: stratum filters, multi-year weight pooling, and the weekend oversample

Paste `00_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections used except Section D, which is `not applicable to this prompt`.

## Why we are asking

Two reasons, and the second is the one that will still matter in a year.

**Immediate.** We need to be able to reproduce demographic stratum counts from public ATUS microdata,
because we keep encountering published stratum sizes we cannot reconstruct from the filter as
described. A worked, variable-level account of how ATUS strata are actually built would let us check
such numbers instead of guessing at them.

**Structural, and this is the real reason.** We work on the European HETUS series and we have already
been badly caught by a **day-base** problem: our three national samples turned out to sit on three
different implicit day bases — one calendar-representative, one at 50/25/25 weekday/Saturday/Sunday,
one at 33/33/33 — which moved a headline statistic by up to 1.3 percentage points in a
country-correlated way. ATUS has the same class of problem in a different form, it is much better
documented, and **we want the ATUS answer in order to check whether our HETUS handling is right.**

## What we need

### Item 1. The variable-level account

Give the actual ATUS variable names and their code values for each of the following, with the
authoritative source (BLS user's guide, data dictionary, or the ATUS-X / IPUMS documentation):

1. **Age.**
2. **Labour force status.** 🔴 Critically: how does ATUS distinguish *employed*, *unemployed —
   looking*, *unemployed — on layoff*, and *not in labour force*? Give the exact variable and every
   code value. We need this because "not employed" and "unemployed" are routinely used
   interchangeably in modelling papers and they are very different populations.
3. **Full-time versus part-time employment.**
4. **Household size**, and how "lives alone" is correctly identified.
5. **Presence and age of children in the household.**
6. **Retirement.** Is retirement directly recorded, or must it be inferred from age plus labour-force
   status? If inferred, what is the accepted convention?
7. **Where the activity took place** — the location variable used to distinguish at-home from
   workplace from elsewhere. Its full code list, and its universe (which respondents and which
   episodes it is defined for).
8. **Telework / work-at-home.** Which variables, in which years, and were they added or changed
   between 2022 and 2023?

### Item 2. Rough population shares, so counts can be sanity-checked

For ATUS 2022 and 2023 combined:

1. Confirm the **exact respondent counts** for 2022 and for 2023 in the public microdata files. We
   believe they sum to 16,684; confirm or correct.
2. Give the approximate **weighted and unweighted** share of respondents falling into each of these
   cells, so a published stratum count can be checked against an expectation:
   * full-time employed, living alone, age 25–44;
   * age 65+ and not employed;
   * full-time employed, children in household, age 35–54;
   * age 25–44 and **not employed** (i.e. unemployed *plus* not-in-labour-force);
   * age 25–44 and **unemployed only** (looking or on layoff).
3. 🔴 The last two are the point of the item: give both, separately, with their approximate
   unweighted counts. We expect them to differ by close to an order of magnitude, and if so that is a
   fact worth having in writing.

### Item 3. Weights, and the multi-year pooling rule — the important item

1. Name the ATUS person-level weight variable(s) and state exactly what each one is constructed to
   sum to.
2. 🔴 **What is the official rule for pooling multiple ATUS years?** Must the weights be divided by
   the number of years? Is there a separate multi-year weight? Quote the BLS guidance and give the
   page. This is a question modelling papers routinely skip and we want the citable answer.
3. What happens if you pool without rescaling — is the error a pure scale factor (harmless for
   probabilities) or does it distort relative shares between years?
4. Are there year-to-year changes in the ATUS weighting methodology, sample design, or population
   controls between 2022 and 2023 that make naive pooling unsafe?

### Item 4. The day-of-week design — the structural item

1. Describe the ATUS **day-of-week sample allocation**: what fraction of diary days are weekend days
   by design, and why.
2. 🔴 How do the person weights handle that oversample? Specifically: if a researcher **stratifies by
   day type first** and then computes weighted within-day-type probabilities, is the oversample
   already corrected, double-corrected, or uncorrected? Give the reasoning, not just the answer.
3. What is the correct procedure for producing a **calendar-week-representative** average from ATUS —
   the quantity a building simulation actually needs, since a building experiences 5 weekdays and 2
   weekend days?
4. Is there published guidance on **when a weekday/weekend split is preferable** to a
   weekday/Saturday/Sunday three-way split? Does the answer depend on the activity type?
5. 🔴 Then the transfer question: **does HETUS use the same design and the same weighting logic, or a
   different one?** Compare the two survey families on: day-of-week allocation, whether the day
   weight is separate from the person weight, and whether the harmonised HETUS files carry a
   calendar-representative day weight at all. If HETUS leaves this to the analyst while ATUS solves
   it in the weight, that is precisely what we need to know.

### Item 5. Secondary activities

1. Does ATUS record secondary activities at all, and if so which ones and in which years (we are
   aware of secondary childcare and secondary eating/drinking modules)?
2. What is documented about the **magnitude of the omission** — how much activity time is secondary,
   and which categories are most affected?
3. Does HETUS record secondary activities more completely than ATUS? If so, that is an advantage of
   our corpus we are currently not claiming.

## Section E

We want concrete sentences for our methods section about day bases and weight pooling — both for
ATUS, if we ever use it, and by analogy for what we must say about HETUS.
