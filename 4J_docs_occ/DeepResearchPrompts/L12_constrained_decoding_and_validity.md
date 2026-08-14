# L12. Guaranteeing a well-formed diary: constrained decoding, grammars, and the cost of enforcing structure

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
Sections C, D and F used.

## Why we are asking

A generated diary that is malformed is worthless: it cannot be injected into a building model. Our
required structure is strict. Every slot must be filled, every code must be in the coding list, exactly
one location applies per slot, durations must sum to a full day, and certain transitions are physically
impossible (a person cannot be asleep at home in one slot and at work in the next with no travel).

A language model will get this right most of the time and wrong some of the time. **Most of the time is
not good enough** when we are generating a million diaries, because one percent malformed is ten
thousand broken records, and silently discarding them biases the population toward whatever the model
finds easy.

There is now a mature ecosystem for constraining generation. We need to know what it can guarantee,
what it cannot, and what it costs.

## What we need

### Item 1. The landscape of constrained decoding

For each mechanism: what it guarantees, how it works in one paragraph, which libraries implement it,
which model families and serving stacks support it, and the throughput cost.

1. **Grammar-constrained decoding** with a formal grammar compiled to a finite state machine or
   pushdown automaton, masking the logits at each step.
2. **JSON schema or regular expression constrained generation.**
3. **Token masking written by hand**, which for a fixed-format output may be simpler and faster than any
   library. Given that our format is fixed-width and highly regular, is a hand-written mask actually
   the right answer? Say so if it is; we would rather write fifty lines of masking code than adopt a
   dependency.
4. **Post-hoc repair**: generate freely, then fix. When is this preferable, and what does it do to the
   distribution.
5. **Rejection and resampling**: generate, validate, discard and retry. Simple and safe, but it biases
   toward easy samples. Quantify the bias if the literature has done so.

### Item 2. What constraints can and cannot express

Some of our constraints are local and some are global.

1. **Local** constraints (this token must be a valid activity code) are trivially expressible by masking.
   Confirm.
2. **Global** constraints are the hard ones. Can a grammar enforce that **durations sum to exactly 1440
   minutes**? That is a counting constraint and a context-free grammar cannot count unboundedly, so we
   expect the answer to be a qualified no with a workaround. Give the honest answer and the workaround,
   for instance emitting a fixed number of slots so the count is structural rather than arithmetic.
3. Can a constraint express **transition legality** that depends on state (no work-to-sleep without an
   intervening travel episode)? This is a finite-state property so we expect yes; confirm and say how
   it is expressed.
4. Can it express **cross-field consistency**, for example that co-presence with a partner is only
   possible for respondents whose household contains a partner? This depends on the conditioning
   vector, so the automaton must be built per record. Is that supported, and what does it cost to
   compile a new automaton per generation?

### Item 3. The distributional cost of constraining

This is the item that matters most scientifically and is the one most likely to be glossed over.

1. Masking logits **renormalises the distribution over the allowed tokens**. What does that do to
   calibration? There is published work on this and it is not purely benign. Report what is known.
2. Is there evidence that constrained decoding **degrades quality** relative to unconstrained decoding
   plus filtering, on tasks where both are possible? Report both directions of the evidence, because
   the field disagrees.
3. For our specific concern: if the model was going to produce an invalid token, masking it forces the
   probability mass onto the valid alternatives, which may not be where a correct model would have put
   it. Is there a diagnostic that detects this? We want to be able to report **how often the constraint
   fired**, as a model-quality metric in its own right: a well-trained model should rarely need it. Is
   that an established practice? If not, we propose to make it one, and we want to know whether anyone
   has done it first.

### Item 4. The practical recommendation

1. Given a fine-tuned small model emitting a fixed-format sequence of a few hundred tokens, which
   mechanism would you use, at which library version, and how much throughput would it cost?
2. Does the mechanism you recommend work with the inference stack recommended in `L11` item 5, at
   compatible versions? A constrained-decoding library that only works with one serving engine, and an
   engine choice made for throughput, is a real conflict and we want it surfaced now.
3. What is the fallback if the recommended library does not support our chosen model?

### Item 5. Validation of validity

Independently of how we enforce structure, we must **measure** it.

1. Specify the validity checks as a list we can implement, each with a pass criterion.
2. State how validity should be reported in the paper: as a single percentage, per constraint, or per
   generation configuration. Is there a convention?
3. What is the correct treatment of invalid records in the reported results: discarded, repaired, or
   counted as failures? Say which is honest, and note that discarding is the option that flatters the
   result, which is why we are asking.

## Named leads

The documentation and papers for grammar-constrained and structured generation libraries, including the
`outlines`, `guidance`, `lm-format-enforcer`, `jsonformer` and `xgrammar` lineages, plus native
structured-output support in serving engines; published evaluations of the quality impact of
constrained decoding; the formal-language background where it bears on what a grammar can express.

## Hard constraints specific to this prompt

* **Distinguish a guarantee from a tendency.** If a mechanism makes invalid output impossible, say so.
  If it merely makes it unlikely, say that instead. Vendors and documentation blur this and we need it
  sharp.
* Version-pin, and state which model families each library actually supports today.
* Do not recommend a library whose last release is stale without saying so.
* Give the throughput cost as a measured or published number where one exists, and label it as an
  estimate where one does not.

## Deliverable

**Section C** is the recommended enforcement design, with the library, version, and where it sits in the
generation pipeline.

**Section B** carries the evidence on distributional cost from item 3.

**Section G** carries the answer on constraint-firing rate as a reported metric, and your negative
controls.
