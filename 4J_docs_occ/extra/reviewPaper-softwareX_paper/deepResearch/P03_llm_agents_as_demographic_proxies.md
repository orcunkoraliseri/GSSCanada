# P03. LLM agents as demographic proxies: what "internal consistency across personas" is actually worth, and the documented failure modes

Paste `00_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections used. Section D applies (we run on a shared single-node SLURM GPU, A100 MIG slices).

## Why we are asking

There is a fast-growing practice of instantiating LLM agents with demographic personas and treating
their outputs as behavioural data — in building energy, in social science, in market research. The
standard validation move is: *give agents different demographic priors, show that they behave
differently and in directions consistent with those priors, conclude the priors "propagate".*

We want to know **what that demonstration is worth**, because we are about to be judged on a
neighbouring claim ourselves, and because we suspect the answer is "less than it looks".

Specifically: a language model has a strong pretrained prior about what a 68-year-old retiree does
compared to a 30-year-old professional. If persona-conditioned agents differ in the expected
direction, that may show the demographic conditioning is working — or it may only show the model has
absorbed the stereotype, which it would exhibit whether or not the conditioning pipeline is
correctly wired to real microdata. **These two are not distinguished by a between-persona difference
test.** We want to know whether the literature has recognised this and what it recommends instead.

## What we need

### Item 1. The silicon-sampling literature and its verdict

1. Establish the state of work on **LLMs as survey respondents / synthetic respondents / silicon
   sampling**. Start from the well-known early positive results and follow the critical literature
   forward to 2026. Give resolvable identifiers for each.
2. On **marginal fidelity**: do persona-conditioned LLMs reproduce the marginal distributions of the
   attribute they are conditioned on? With what measured error?
3. 🔴 On **joint fidelity**: do they reproduce the **correlations between attributes**, or only the
   marginals? This is the failure mode we care most about, because our own evaluation has already
   caught an analogous defect — a repair that fixed a marginal and left the joint distribution wrong.
4. On **within-group variance**: is there measured evidence of **variance collapse** — LLM personas
   from a group being more homogeneous than real members of that group? Quantified, if anyone has
   quantified it.
5. On **caricature**: measured evidence that minority or out-group personas are rendered as
   stereotypes. Which studies, which measurement?
6. On **US-centrism / cultural drift**: evidence that non-US personas drift toward US behavioural
   norms. This bears directly on our leave-one-country-out design.

### Item 2. The methodological question — what test would actually be informative?

🔴 This is the item we most want answered, and it may not have a clean literature answer. Say so if
it does not.

1. Has anyone **named and criticised** the "different personas behave differently, therefore the
   conditioning works" inference? Is there a term for it?
2. What is the recommended stronger design? Candidates we can think of — tell us which have been
   used and how they performed:
   * comparing agent behaviour against **held-out real behavioural data** for the same demographic
     cell, not against other agents;
   * an **ablation** that scrambles the persona–stratum pairing and checks the differences vanish;
   * a **placebo persona** — a demographically null or fictitious stratum — that should produce no
     systematic difference;
   * checking whether the differences track the **grounding data** or track the **model's prior**,
     e.g. by conditioning on a stratum whose real behaviour is counter-stereotypical.
3. Is there published work testing whether the persona effect **survives** when the grounding data
   contradicts the model's prior? That is the decisive experiment and we would like to know if it
   exists.

### Item 3. Does fine-tuning on real microdata fix it, or mask it?

We fine-tune an open-weight model on real harmonised diaries rather than prompting a hosted model
with a persona description. Establish whether that changes the picture:

1. Evidence on whether **fine-tuning on real individual-level microdata** repairs the failure modes
   in Item 1, or merely reduces their surface visibility.
2. Any study that compares **prompted persona** against **fine-tuned on real records** on the same
   task, with the same evaluation.
3. Failure modes specific to fine-tuning here: memorisation of individual records (a disclosure
   risk for us), mode collapse, loss of the tail.
4. 🔴 If the evidence says fine-tuning does **not** fix demographic joint-distribution fidelity, that
   is a limitation we must write into our own paper. We would rather learn it from you than from a
   reviewer.

### Item 4. In building energy specifically

1. Which building-energy papers use LLM agents with demographic personas for occupant behaviour, and
   **how does each validate the agent layer**? Tabulate: what was compared, against what reference,
   with what statistic, and whether any measured human data entered the comparison at all.
2. Is there **any** building-energy LLM-agent paper that validates against measured occupant data
   (metered, smart-thermostat, survey-response, field DR participation)? If none, say none — that is
   a publishable gap and we want to know it is open.
3. What benchmark datasets would make such a validation possible? We are aware of a public smart
   thermostat dataset; what else exists, and what are the access conditions?

### Item 5. The ethics and framing question

Briefly, and for the write-up rather than the method:

1. What is the current state of the argument about whether LLM-simulated respondents may
   legitimately **substitute** for human subjects, versus only **generate hypotheses**?
2. Are there venue or funder positions on this we should know about?
3. What language do careful papers use to scope such claims? We want the phrasing, not the debate.

## What would make this answer wrong

If the critical literature we assume exists is thin, or if the positive results are stronger than we
are giving them credit for, say so in the first sentence of Section A. We are looking for the state
of the evidence, not for support for a position we already hold.
