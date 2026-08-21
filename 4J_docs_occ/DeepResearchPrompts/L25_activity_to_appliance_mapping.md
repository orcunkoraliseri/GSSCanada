# L25. What does the published activity-to-appliance literature actually give us, table by table?

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.

---

## 🔴 CORRECTIONS TO THE MASTER BRIEF — READ THESE BEFORE THE BRIEF ITSELF

1. **The corpus is HETUS only.** Canada and the United States are out of the paper.
2. **One survey wave per country, not several.**
3. 🔴 **The corpus is THREE countries: Spain 2009-10, United Kingdom 2014-15, Italy 2013-14.** France
   was excluded on 2026-08-15.
4. **There is no forecast and no temporal claim anywhere in the paper.**
5. **The fine-tuned model will never be released.** Evaluation is leave-one-country-out transfer.

---

## The question, in one sentence

**For CREST, Widen et al., LoadProfileGenerator and RAMP, what is the actual published mapping from a
time-use activity code to an appliance event, at what activity resolution, with what trigger
probability, what rated power and cycle duration, and validated against what, at what scale?**

## Why it is being asked, so you can tell a useful answer from a complete one

Our step document carries one instruction in bold: **do not invent the mapping.** A validated lineage
already exists, several members of it are open source, and an ad-hoc heuristic is the single easiest
thing in this paper for a reviewer to reject. So we will adapt published logic to the HETUS activity
list rather than author a new one.

To do that we need the mappings **as tables**, not as descriptions of tables. Our validation gates are
written against that distinction and they are strict:

* **`G9.1`** — 100 % of rows in our `activity_appliance_map.csv` must carry a source model **and the
  specific table or figure the value came from**. 🔴 **A row citing only a paper is a FAIL.**
* **`G9.2`** — 100 % of rows carry `VALIDATED` or `NOT VALIDATED` **and the validation scale**. 🔴 **A
  row labelled `VALIDATED` with no scale is a FAIL, not a warning.**
* **`G9.3`** — every `NOT VALIDATED` row carries written reasoning. Rows with neither citation nor
  reasoning: **0**.
* **`G9.4`** — every cited DOI must resolve to the title it is cited under.

So the useful answer is one that lets us fill those columns. A summary of what CREST does is not
usable; the table number that carries its appliance list is.

---

# PART A — THE FOUR SOURCE MODELS, ONE SECTION EACH

For **each** of CREST (Richardson et al., 2010), Widen et al. (2009 lighting; 2010 activity patterns
and electricity demand), LoadProfileGenerator (Pflugradt, 2016) and RAMP (Lombardi et al., 2020),
report the following. Where an item does not exist for that model, write `NOT FOUND` rather than
substituting the nearest thing from another model.

**A1. The mapping itself.**
* Is there a published **table** mapping activity to appliance? Give the table or figure number and the
  document it is in, including whether it is in the paper, a supplement, a thesis, a manual or the
  source repository.
* What **activity classification** does it key on: TUS codes from a specific survey, a bespoke internal
  activity list, or something else? Name the survey and year if it is a TUS.
* At what **resolution**: how many distinct activity states does the mapping distinguish?

**A2. The trigger.**
* Is the mechanism a probability `P(appliance | activity)` per time step, a per-occurrence draw, a
  daily count, or something else? Quote the form.
* Are the probability values **published as numbers**, or only calibrated inside the code? If only in
  the code, name the file and the identifier.

**A3. The appliance side.**
* The appliance list, with rated power and cycle duration, and where those numbers are published.
* Whether cycles **run to completion** once started, and how the model handles a trigger arriving near
  the end of an activity episode. Our `G9.5` asserts full-cycle completion on synthetic edge cases and
  we need to know what the source model actually does.

**A4. Validation.**
* Against **what** measured data, at **what scale**: number of dwellings, feeder or district level, and
  the fit statistic reported.
* 🔴 **The scale is the part we most need**, because our own claim is bounded by it. Our step document
  already records that these models validate against aggregate demand over roughly 100 to 500
  dwellings with R2 above 0.90, and that individual single-dwelling prediction has high residual
  variance. **Confirm or correct that characterisation from the papers themselves**, with numbers.

**A5. Licence and reusability.**
* Is the implementation open source? Under which licence, checked on what date?
* Is the **mapping table** itself redistributable, separately from the code? These are not the same
  question and we need both answered.

---

# PART B — FITTING IT TO OUR DATA, WHERE WE EXPECT FRICTION

## B1. 🔴 Our activity codes are three digits, and that was a deliberate decision

Our corpus carries **158 three-digit HETUS target activity codes**, plus one sentinel `000` meaning
"the diary entry here was not a usable activity". An author decision fixed one survey wave per country
specifically so that nothing forces two-digit pooling, **and this step is the reason it was taken**:
the appliance trigger needs to tell laundry from cooking from washing from dishwashing, and two-digit
codes collapse exactly those distinctions.

Our gate `G9.11` then asks whether the mapping **actually uses** the third digit: the number of
distinct activity codes with distinct appliance rows must exceed the number of distinct two-digit
groups. 🔴 **A mapping that resolves only at two digits did not need the corpus decision that preserved
three, and we want to know that.**

**So: at what code depth do the four source models actually resolve?** If every one of them collapses
to something coarser than three digits, say so plainly. That is a finding we would act on, and it
would mean our third digit buys nothing downstream even though it cost a corpus decision.

## B2. 🔴 Our generated diaries carry no secondary activity

The generated record is a sequence of `duration, activity, secondary activity, location, co-presence`
tuples, but the **secondary activity field is not populated in generated output**. It exists in the
real corpus and is used, if at all, only to calibrate a probability.

This matters because an appliance triggered by an activity that is only ever **secondary** is exactly
the load a primary-only stream misses: a television on while eating, a washing machine running while
the respondent does something else.

**Question: do any of the four models drive from more than one concurrent activity stream?** We believe
all four drive from a single stream, which would make adapting them unchanged the conservative choice
rather than a compromise. **Confirm or refute, per model, from the paper or the code.** If any of them
does use a secondary or concurrent activity, name where and what it changes.

## B3. The load that is only ever secondary

Independently of B2: **is there published evidence on which domestic loads are systematically recorded
as secondary rather than primary in time-use diaries, and how much energy they represent?** If the
answer is that nobody has measured this, say so. It bounds an explicit limitation in our paper and a
clean negative is useful.

## B4. Domestic hot water

Our plan uses the **Jordan and Vajen** four-event tapping model, short draw, medium draw, bath, shower,
at roughly **30 to 50 L per person per day at 60 degrees Celsius**, driven by activity codes for
washing, showering, food preparation and laundry.

Report, from the sources themselves:
* the **published event definitions and their proportions**, with the table they come from;
* whether the 30 to 50 L per person per day figure is what the source actually says, and **at what
  reference temperature**. A volume quoted at a different temperature is a different quantity and we
  have already been caught once this month by a unit that looked like a number;
* which activity codes each source model uses as the DHW drivers, and at what resolution;
* whether any of the four models above already implements a DHW module, or whether DHW must come from
  a separate lineage.

---

# PART C — THE CITATION TRAP THIS SERIES HAS ALREADY HIT

🔴 **Read this before writing any reference.**

An earlier round in this series gave **Widen and Wackelgard (2010)** as *Applied Energy* **87(3):
780-789**. That is a conflation. Our vetting record concludes:

* the **2010** paper on activity patterns and electricity demand is *Applied Energy* **87(6):
  1880-1892**;
* ~~**41(7): 780-788** is a **different** paper, Widen et al. **2009**, in *Energy and Buildings*, on
  lighting;~~ 🔴 **THIS LINE WAS WRONG AND `RL25` EXPOSED IT. CORRECTED 2026-08-20, `FINDING 47`:**
  `41(7):780-788` names no real paper. `41(7):781-789` is **Richardson** et al., *Domestic lighting*
  (`10.1016/j.enbuild.2009.02.010`); the real Widen lighting paper is **41(10):1001-1012**
  (`10.1016/j.enbuild.2009.05.002`); and the Widen 2009 paper this step actually needs is
  **41(7):753-768**, *Constructing load profiles for household electricity and hot water from time-use
  data* (`10.1016/j.enbuild.2009.02.013`). The DOI `RL17` tabled as CrossRef-verified for the lighting
  paper, `10.1016/j.enbuild.2009.02.006`, resolves to *Estimation of passive cooling efficiency for
  environmental design in Brazil*. 🟢 **The instruction below — verify our correction rather than
  accept it — is what caught this. Keep it in every future prompt.**
* they are **two distinct real papers** and each must be cited for its own contribution.

**Verify both independently through CrossRef and report what the API returned for each.** If our own
correction above is itself wrong, say so; we would rather be corrected than confirmed.

---

# PART D — THE QUESTION WE MAY NOT HAVE THOUGHT TO ASK

You have now seen the design: activity-resolved daily diaries generated by a fine-tuned language model
for a country it never saw, assembled into annual schedules, driving European residential EnergyPlus
archetypes, with end-use loads triggered from the activity codes.

**Name the one thing most likely to be wrong with our activity-to-load step specifically.** Not a
generic risk. One specific checkable thing, with the evidence that makes you suspect it and the
cheapest test that would confirm or kill it.

Three candidates we have already thought of, so do not offer any of them as your answer: that
single-dwelling prediction has high residual variance; that a load recorded only as a secondary
activity is invisible to a primary-only stream; and that the mapping might not need three-digit codes.

---

## MANDATORY NEGATIVE CONTROLS FOR THIS REPORT

Answer all seven in plain sentences in Section G.

1. **List the papers, manuals and repositories you opened in full**, separated from those you cite from
   an abstract or a secondary description. **A citation is not evidence until opened.** Every
   quantitative value anywhere in your report must come from the first list.

2. **For how many of the four models did you find an actual published mapping table, as opposed to a
   prose description of one?** Give the number. **If it is zero, say zero.** Zero would change our plan
   immediately and is a more useful answer than four half-found tables.

3. **At what code depth does each model resolve?** Answer per model, as a number of distinct activity
   states. Do not answer "sufficiently detailed".

4. **Verify every DOI through CrossRef and report the title the API returned**, including the two Widen
   papers in Part C. State explicitly whether any DOI resolved to a different paper than the one you
   cited.

5. **Did you at any point give a rated power, a cycle duration or a trigger probability that you did
   not read in a source document?** Say where. An engineering-plausible wattage is not a citation, and
   `G9.1` will reject it.

6. **Count the convenient findings.** The convenient answers here are: all four models publish clean
   mapping tables, they all resolve at three digits, they all validate at dwelling scale, and they are
   all redistributable. 🔴 **If most of those came back convenient, stop and re-check.**

7. **Did you assume any of these models uses HETUS?** Say so explicitly per model. Several were built
   on national surveys that are not HETUS, and a mapping keyed on a different activity list is
   something we must **translate**, not adopt. If you cannot tell which survey a model keys on, say you
   cannot tell.

Also required, as in every round of this series:

* `NOT FOUND` beats an invented answer, always.
* Every version, threshold, quantity, licence or table reference carries **the date it was checked and
  the document it came from**.
* 🔴 **Do not reproduce or reconstruct the contents of a paywalled table.** Say it is paywalled and
  stop.
* Do not state, estimate or reproduce any result of our models, and do not comment on our hardware,
  our storage or our cluster. You cannot see them.
* Do not recommend a source model on grounds of popularity or ease of implementation. Recommend the one
  the evidence supports, or report that the evidence does not support one.
* No em dashes and no en dashes in the returned text.
