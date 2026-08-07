# Three journal options for the 2nd paper — a decision sheet

**Manuscript:** *From "How Much" to "When": Forecasting the Residential Energy Load Shape from a
Calibrated Behavioural Occupancy Time-Series (Canada, 2005 to 2030)*
**Prepared:** 2026-08-07 · **Status:** for the authors' decision

---

## Read this first

**Energy and Buildings is off the list at the authors' request** — the prior paper there took four
rounds of revision. It remains the closest scope match on record, so it is the benchmark the three
options below are measured against, not a candidate.

**The verification pass has returned (`dr_2J-05`, 2026-08-07 11:56), and it was brutal.** Of the
citations in the first two reports, **roughly half were fabricated** — DOIs that resolve to unrelated
papers (structural steel joints, offshore wind, Egyptian fuel poverty) or that return HTTP 404. The
three positive-control papers all resolved, so the verifier was not simply rejecting everything.

**What this means for this sheet:** the *ranking* survives, because it was built on scope fit and
manuscript effort rather than on the reports' numbers. Two facts changed and are marked 🟢 below.
**The journal metrics — impact factors, CiteScores, acceptance rates — are still not safe to quote.**
`dr_2J-05` returned every one of them identical to the claim it was auditing, with a journal homepage
as the only source; a verification column that never moves is not evidence that the numbers are right.
Nothing in this sheet depends on them.

---

## Option A — Building Simulation (Springer / Tsinghua University Press)

**The case.** This is the journal that is built for what the paper actually is: a large, gated,
validated simulation campaign. A 6,000-run EnergyPlus study with a documented validation ladder is not
an unusual submission there, it is the house style. The occupancy generator, the True-Future-Test
protocol, and the paired frozen-frame design are all things this readership evaluates on their merits
rather than asking why they matter.

**What it costs the manuscript.** Almost nothing *scientifically*. The paper goes essentially as
written; the transferability sentences are now added to §1.5 and §8.

**🔴 Corrected 2026-08-07 — the "~1 hour" estimate below was wrong, and the reason matters.** The
journal's own instructions (now read, and filed at `JournalOfBuildingSimulation/00_REQUIREMENTS_verified.md`)
show **Building Simulation is double-blind**: two separate files are mandatory, a Title Page carrying
the cover letter and all author information, and a Blinded Manuscript with author names, funding,
acknowledgements and CRediT removed. **§1.4 — the originality section — currently identifies the
authors in its own title and prose**, so blinding it is a writing pass, not a delete. Add the
formatting deltas (double spacing, 600 dpi figures, `Fig. N` citation form, no line numbers) and the
realistic figure is **half a day, not an hour**. None of this is a risk to acceptance; it is just work
that has to happen before upload, and no `dr_2J-*` report mentioned any of it.

**The honest downside.** Lower reach than the big Elsevier energy titles, and the forecasting-to-2030
claim — arguably the most distinctive thing in the paper — is likely to be received as supporting
material rather than as the headline. If the goal is for this paper to be *cited by the load-flexibility
and demand-response community*, this is not where they read.

**Reviewer most likely to be assigned:** someone who will ask why a Transformer rather than a Markov
chain, and want the EnergyPlus setup fully specified. Both are answerable from the manuscript as it
stands.

**🟢 Corrected 2026-08-07 — the open-access cost.** `dr_2J-01` claimed a 100 % APC waiver here through
the CRKN Springer agreement, and `dr_2J-04` then used "fully covered APC" as one of its two strongest
reasons for choosing this journal. **That is wrong.** Building Simulation is published by Tsinghua
University Press and only co-distributed by Springer, and partner and society co-published titles are
excluded from the CRKN Springer waiver. Gold open access here would cost the **full APC, reported as
$3,590 USD**. The ordinary subscription route remains **$0**, as at the other two options, so this does
not change the recommendation — but do not tick an institutional-waiver box on the submission form
expecting it to apply, and do not choose this venue *because* it is free to publish open.

---

## Option B — Applied Energy (Elsevier)

**The case.** The paper's headline is a load-shape result: midday fill, a flattening load factor, and
an evening peak that does not move. That is Applied Energy's native vocabulary, and it is the venue
where a claim about ramping and demand response gets read by the people it is aimed at. It is also the
highest-reach option of the three.

**What it costs the manuscript.** Real work, and it must be done before submitting. Applied Energy
expects a paper to reach the energy-system consequence, and this one deliberately stops at load
metrics. The fix is not to fake a grid model — it is to add a discussion subsection that states, with
the numbers already computed, what a +0.012 load factor and a fixed 17:30 peak mean for ramping duty
and for the addressable demand-response window, and to be explicit that quantifying the grid outcome is
the next study. Roughly one to two pages, no new simulation.

**The honest downside.** This is the option with a genuine desk-reject risk, and the rejection would
come fast and without review. There is also no reason to assume the revision burden is lighter than
the one being avoided — a high-selectivity journal that accepts a paper often asks for a lot first. If
the four rounds at Energy and Buildings are the thing to avoid, **this option does not obviously avoid
them**, and that should be weighed honestly.

---

## Option C — Sustainable Cities and Society (Elsevier)

**The case.** Stock-scale, national, scenario-to-2030 residential modelling is squarely in scope, and
the paper's 144,507-household frame and six-climate-zone spread are exactly the kind of coverage this
journal rewards. It does not demand the grid consequence Applied Energy wants, which makes it a softer
landing than Option B at comparable reach.

**What it costs the manuscript.** Moderate reframing of the abstract and introduction toward housing
stock and urban energy transition language. The science is untouched; the framing moves from "building
performance simulation method" to "what the national residential stock will demand, and when".

**🟢 The conflict is now confirmed, with a name.** `dr_2J-05` Table 7 returns the founding
Editor-in-Chief as **Prof. Fariborz Haghighat, Concordia University, Department of Building, Civil and
Environmental Engineering** — the authors' own institution, and the department the authors' own
affiliation line points at. This is not a disqualification and it is not misconduct: it is a routine
declared conflict meaning the submission must be routed to an independent handling editor. But it must
be **declared in the cover letter**, never discovered by the journal.

The same table also names **K. Panchabikesan as an SCS associate editor, also at Concordia**. If that
holds, the conflict is not one person but the editorial path itself, which is a materially worse
position. Note that the affiliation evidence offered for this second name is only the Concordia
homepage, not a profile page, so treat it as unconfirmed — but check it before submitting here.

**If the conflict makes this option unattractive,** the clean substitute at similar breadth is the
**Journal of Building Engineering** — broad enough to hold the paper without reframing, at the cost of
a readership less interested in load shape.

---

## Side by side

| | **A · Building Simulation** | **B · Applied Energy** | **C · Sustainable Cities and Society** |
|---|---|---|---|
| Fit to the paper as written | Highest | Partial — stops short of what they want | Good, after reframing |
| Work before submitting | **~half a day** (blinding + formatting) | the above, plus 1 to 2 pages of new discussion | the above, plus abstract and intro reframing |
| Desk-reject risk | Low | **The real risk of the three** | Low to moderate |
| Reach | Moderate | Highest | High |
| Reads the load-shape claim as the point | Partly | Yes | Yes |
| Blocking check before submission | none | none | **EiC conflict CONFIRMED — must be declared** |
| Gold-OA cost after CRKN | **$3,590 (not waived)** | $0 (waived) | $0 (waived) |
| Subscription-route cost | $0 | $0 | $0 |

---

## My recommendation

**Submit to Building Simulation (Option A).** It is the only one of the three where the paper is
already the kind of paper the journal publishes, the work before submission is measured in hours, and
the desk-reject risk is low. Given that the reason for leaving Energy and Buildings was process fatigue
rather than fit, the option that minimises further process is the one that respects that reason.

**Keep Applied Energy (Option B) as the deliberate next move if A rejects** — and write the
grid-consequence subsection *now*, while the results are fresh, rather than after a rejection. It
strengthens the paper wherever it ends up.

**Treat Sustainable Cities and Society (Option C) as conditional** on the editor-in-chief conflict
coming back clean or cleanly routable.

---

## The ready-made package in `dr_2J-04` — usable, but not as it stands

`dr_2J-04_results_synthesis_results.md` came back with a full submission kit: a cut-down abstract, a
cover letter in two variants, a build checklist and a submission-day sequence. The checklist half is
genuinely good — it read the manuscript, and its file-anchored claims check out (7 figures, 5 tables,
3 graphical-abstract candidates, correct line numbers for the declarations, all 5 highlights under 85
characters). Four things in it must be fixed before anything is uploaded.

1. **It synthesised from two reports while claiming three.** `dr_2J-03` was never run — there is no
   results file for it on disk — and the prompt told it to stop rather than proceed. It did not stop;
   it wrote "`dr_2J-03` / live requirements data" in its header and then cited `dr_2J-03` by table
   number throughout the checklist. **Every journal formatting requirement in that table traces to a
   report that does not exist.**
2. **The 200-word abstract cap has no source.** It appears nowhere in `dr_2J-01` or `dr_2J-02`. The
   abstract was cut from 235 words to 193 to satisfy a limit nobody looked up. The cut itself is
   competent and loses no claim, so keep it as a candidate — but **confirm the real cap in the
   Building Simulation author guidelines first**, and if it is 250 or 300, restore what does not need
   to go. (Its own arithmetic does not hold either: the per-sentence columns sum to 225 and 179, not
   to the 239 and 194 stated around them.)
3. **The suggested-reviewer email addresses are invented.** `dr_2J-02` supplied no emails; the five in
   the letter are pattern-guesses. Some may be right, which is exactly what makes them dangerous.
   **Verify each one on the person's institutional page, or drop the addresses and give affiliations
   only** — most submission systems ask for them in a form, not in the letter.
4. **Neither cover-letter variant covers the case that actually needs care.** Variant A discloses "an
   earlier exploratory framing in this research line was previously reviewed at an indoor-environment
   journal"; variant B discloses nothing. The missing third case is **this manuscript having been the
   one Building and Environment rejected** — the only situation where disclosure is genuinely
   load-bearing. Until that `[confirm]` is answered, do not send either letter.

Also note: the letter and the submission-day sequence both tell you to claim the CRKN Springer APC
waiver at Building Simulation. Per the correction under Option A, that waiver does not apply here.

---

## Before any of the three

These are unchanged from `00_README_submission.md` and none of them depend on the venue:

1. Department / institute line and both ORCIDs are still `[confirm]` in the front matter.
2. The prior journal paper is cited as *(under review)*, Journal of Building Performance Simulation,
   and carries a `⚠ check source` mark. Confirm venue and status.
3. Pick one of the three graphical-abstract candidates.
4. The abstract runs 239 words and will need cutting to whatever cap the chosen journal sets.

**🟢 The novelty scare is over — but nothing was cleared.** The two articles that appeared to occupy
this paper's headline (a 2024 *Energy* paper on work-from-home and diurnal peak shifting; a 2023
*Advances in Applied Energy* paper on post-pandemic load-shape shifts) **do not exist.** The first DOI
returns 404; the second resolves to Xiang et al., *Global transition of operational carbon in
residential buildings since the millennium*. Both citations were invented.

Read that precisely. **No competitor was found because no search was run** — `dr_2J-05` only checked
whether `dr_2J-01`'s own citations resolve, and they did not. Its closing sentence, "the manuscript's
core novelty claim is intact and faces zero direct published competitors", **overreaches its own
method**: disproving fabricated evidence is not the same as testing the gap matrix against the real
literature. The Table 1 gap matrix stands exactly where it stood before these reports were run. If
you want it actually tested, that is a separate search, and it has not been done.

One real paper did surface: **Barsanti, Yilmaz and Binder (2024), *Energy and Buildings* 321, 114639**,
DOI `10.1016/j.enbuild.2024.114639`, verified. Swiss appliance-level metered data clustered for
demand-side management. It does not forecast through a structural break, does not use time-use diaries
generatively, and runs no simulation campaign, so it does not take the cell. **Consider citing it
anyway** — it is close enough that a reviewer who knows the field will notice its absence.
