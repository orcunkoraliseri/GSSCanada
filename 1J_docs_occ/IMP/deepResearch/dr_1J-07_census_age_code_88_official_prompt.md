# Deep-Research Prompt dr_1J-07: what "age not available" (code 88) means on the Canadian Census individuals PUMF

> SCOPE GUARD, READ FIRST. Every answer must come from an **official Statistics Canada document you
> opened** (a PUMF user guide, codebook, data dictionary, record layout, or technical report), with its
> title, URL and page or section. We hold these microdata files, so every code and count you give will be
> checked against our own files. A fact you cannot find in a document must be written `NOT FOUND`.
> Do not explain the code from general knowledge of how census agencies work.

Run in: Gemini (live search). Save the answer as `dr_1J-07_census_age_code_88_official_results.md` in
this folder.

---

## Why we are asking

We build households from the **individuals** public-use microdata file (PUMF) of four Canadian censuses
and give each person a time-use diary from the General Social Survey. The age-group variable (`AGEGRP`)
on some of these files carries a code 88, labelled "not available". Our code had been treating those
persons as aged 75 and over. We have now decided how to handle them, and the paper must say, from the
official documentation, **what code 88 is**: why a person's age is withheld, which kinds of persons it
is withheld for, and whether Statistics Canada says the withheld persons differ from the rest.

This matters because if age is withheld for a particular kind of person (for example for confidentiality
in certain household situations), the missing persons are not a random slice of the population, and the
paper must say so.

## What we need

For each of these four files, answered **separately**: the 2006 Census individuals PUMF, the 2011
National Household Survey individuals PUMF, the 2016 Census individuals PUMF, the 2021 Census individuals
PUMF.

1. The exact title, catalogue number, URL and year of the user guide and of the codebook / data
   dictionary.
2. The full list of codes for `AGEGRP` (or the file's age-group variable, if named differently), as
   printed in the codebook, including every "not available", "not applicable" or suppression code.
3. **Whether code 88 (or any "not available" age code) exists on that file at all.** "Not present on this
   file" is a valid and useful answer; say which page shows the full code list.
4. The official reason a person's age is coded "not available": confidentiality suppression, a
   geography or household-type rule, non-response, or something else. Quote the sentence.
5. Which persons it applies to, if the documentation says (for example particular household sizes,
   provinces, relationships to the household reference person, or persons in collective dwellings).
6. The published frequency of code 88 (count or weighted count), if the codebook prints one.
   Do not compute it from anything else.
7. Whether any other variable on the same person is also withheld when age is withheld (for example
   household size, marital status, or the household or family identifiers).
8. Any Statistics Canada caution about analysing records with a "not available" age, or advice to
   exclude or keep them.

## Named leads

PUMF documentation for Statistics Canada catalogue 97M0001X / 98M0001X (Census and NHS public-use
microdata, individuals files) and 98M0002X; the "Public Use Microdata File (PUMF) User Guide" for each
census; the codebook or "Data dictionary" PDF that ships with each file; the Data Liberation Initiative
(DLI) and ODESI (Scholars Portal) pages for these files; university data library pages that host the
codebooks. These are leads: confirm every code on the page you open.

---

## Rules

- Quote the source for every fact, with page or section. Answer each census file separately; never write
  "the same as the previous census" unless the document says so.
- Do not guess why the age is withheld. If the reason is not written, the answer is `NOT FOUND`.
- Do not recommend how we should handle these persons. Report what the documents say only.
- `NOT FOUND` beats a guess. Do not reconstruct a number from other numbers.
- No em dashes and no en dashes in the report.

---

## Output format (follow exactly)

1. **Table A:** one row per census file and item (items 1 to 8). Columns: file, item, answer, exact
   quote, document title, URL, page.
2. **Code lists:** for each file, the full `AGEGRP` code list transcribed exactly as printed.
3. **Documents opened in full**, as a list (zero is a permitted answer), and for each item left
   `NOT FOUND`, one line on where you looked.
4. **What would have made you write `NOT FOUND` for item 4**, in one sentence per file.
