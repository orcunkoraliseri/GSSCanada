# T36. Licences, privacy and redistribution for non-survey occupancy data in a Canadian lab

> **Corrections 2026-09-18 (round 2).** Round 1 of this prompt failed vetting: invented co-authors,
> quotes that are not on their pages, named items dropped without a word, and no page opened. These
> rules add to everything below and win where they differ.
> * Paste the CrossRef-returned title beside every DOI in every table row.
> * A row without a resolving identifier (DOI, arXiv ID, or a landing page you opened) is not admitted.
> * Our own papers' rows are copied verbatim from brief section 2; never give one a title yourself.
> * Author list, year, volume and pages are pasted from the same CrossRef record
>   (`api.crossref.org/works/<DOI>`), never typed. If CrossRef lists two authors, you list two.
> * Every page you open, CrossRef and OpenAlex calls included, gets a line in `RT<NN>_pages.log`
>   (format in the runner). Every quote, variable name, licence, count and URL in the report must be
>   traceable to a log line. A claim with no log line is not admitted.
> * Every item and every named source below gets its own heading or card. If you could not find it,
>   write `NOT FOUND` and list the URLs you tried; they must be in the log.
> * Round 1 gave no URL at all. Every legal quote is copied from the official consolidated text
>   (Justice Laws, LégisQuébec, the TCPS 2 2022 page, EUR-Lex) with the article number and URL logged.
>   For TCPS 2, quote the chapter 5 articles on secondary use of both identifiable and non-identifiable
>   information.
> * All nine source classes of item 1 are answered, each with its own heading.
> * Every licence clause is quoted from the custodian's page with its URL logged. If you cannot tell
>   whether a licence covers the microdata or only derived products, say so.

Paste `00_MASTER_BRIEF.md` first (read its section 9). Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections used. Run in wave 6, after `T19`. Read with `T18`, which covered synthetic microdata from
surveys.

## Why we are asking

Our series ships synthetic schedules and code openly. Sources such as smart-thermostat programs,
smart-meter datasets, commercial mobility panels and household travel surveys come with terms that
may forbid redistribution, forbid derived products, or limit use to one project. A researcher in
Québec is also bound by federal and Québec privacy law and by university research ethics rules, and
European data carry GDPR terms. A source that cannot be used in a publishable, open workflow is not a
source for us. We need the rules that apply, quoted, per source class.

## What we need

### Item 1. Rules per source class

For each class (smart thermostat programs, open home-sensor datasets, smart-meter datasets, network
feeder data, aggregated mobility, commercial mobility panels, travel surveys, synthetic populations
from transport models, day-night population grids), take the two most likely datasets named in
`T20` to `T30` or found by you, and quote: the licence or terms; whether derived schedules may be
published; whether the dataset may be named and cited; whether ethics approval is required; any
restriction by the researcher's country.

### Item 2. Law and ethics that bind the researcher

Quote the relevant parts of: the Tri-Council Policy Statement (TCPS 2) on secondary use of data; Québec
Law 25 on personal information in research; PIPEDA where relevant; GDPR Article 89 and national
research exemptions where EU data are processed from Canada. Say which apply to aggregated data and
which only to personal data.

### Item 3. Disclosure risk of occupancy data

Evidence that presence data are sensitive (inference of absence for burglary, of health or religion
from routines). Works that assessed re-identification or disclosure risk of presence or smart-meter
data, and the mitigations used (aggregation, noise, synthetic release). Section C rows.

### Item 4. What can be released

For a hypothetical workflow that calibrates survey-generated schedules to one non-survey source, what
may be released: the calibrated synthetic schedules, the calibration targets, the code. Answer per
source class, citing item 1.

## Named leads

TCPS 2 (2022) text; Commission d'accès à l'information du Québec guidance; Office of the Privacy
Commissioner of Canada; EDPB guidelines on research; dataset terms of use; *Journal of Privacy and
Confidentiality*, *Proceedings on Privacy Enhancing Technologies*, *IEEE Transactions on Smart Grid*.

## Hard constraints specific to this prompt

* Quote legal and licence text; paraphrase is not admitted for any clause that decides release.
* This is not legal advice and must not be written as such; state what the texts say and flag where
  interpretation is needed.
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** answers first: which source classes allow publishing derived synthetic schedules openly,
and which forbid it.

**Section B** is items 1 and 2. **Section C** is item 3. **Section E** is item 4. **Section D** assesses
which forms of `A14` survive the release requirement. **Section G** carries your negative controls.
