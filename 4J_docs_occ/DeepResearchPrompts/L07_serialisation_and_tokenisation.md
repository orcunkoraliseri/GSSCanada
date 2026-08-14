# L07. Serialisation and tokenisation: how to turn a 144-slot diary plus demographics into tokens without wrecking either the model or the token budget

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
Sections C, D and E used. This is the single most consequential engineering decision in the project.

## Why we are asking

An LLM sees tokens. Our record is a structured object:

* roughly 20 to 25 categorical **non-temporal attributes** (country, region, household size, family
  type, age class, education, employment, dwelling attributes),
* three contextual attributes (season, day type, and in some designs the survey wave year),
* and a **sequence of 144 slots**, each carrying an activity code from a list of order one hundred, a
  location code from a short list, and a co-presence flag.

Naively written as text, one diary is a very long, extremely repetitive string. Written badly it costs
thousands of tokens per record, which multiplies training cost, caps how many records fit in a context,
and wastes most of the model's capacity on delimiters. Written well it might cost a few hundred.

We also do not know whether the numeric codes should stay numeric. There is a well-documented problem
with how language model tokenizers split numbers, and our codes are numbers that carry no numeric
meaning at all: activity code 411 is not four hundred and eleven, and it is not "between" 410 and 412.

## What we need

### Item 1. The serialisation options, compared on token cost and learnability

Lay out and compare, with evidence where evidence exists:

1. **Verbose key-value text**: `age_class: 45-54\nemployment: full-time\n...` then a slot list.
2. **Compact delimited**: a fixed field order with a single-character separator, no keys.
3. **Run-length or episode encoding**: instead of 144 slots, emit episodes as
   `(start, duration, activity, location, co-presence)`. A real diary has on the order of 15 to 30
   episodes per day, so this is roughly a fivefold to tenfold reduction in sequence length and it is
   also **how time-use data is natively collected**. State plainly whether you would choose this, and
   what it costs: it makes the slot grid implicit, so validity checking moves from "is every slot
   filled" to "do the durations sum to 1440 minutes".
4. **JSON or YAML**: expensive in tokens, but supported by every structured-output library.
5. **Custom special tokens**: add one token per activity code, per location code, and per attribute
   value, to the tokenizer.
6. **Numeric or symbolic recoding**: map each code to a short symbol chosen so that the base tokenizer
   maps it to exactly one token.

For each: estimated tokens per diary for a common tokenizer family, whether it is reversible without
ambiguity, whether it is robust to a single generation error, and any published evidence on which
format an LLM learns fastest.

**Give an actual token count**, computed with a named tokenizer at a named version, for one example
diary written in at least three of these formats. Show the example strings. This is the most useful
single thing you can give us.

### Item 2. The numeric tokenisation problem

1. Summarise what is actually known about how the tokenizers of the major open-weight families split
   numbers, per family, with sources. Some split digit by digit; some group digits; they differ.
2. State the consequence for **arbitrary categorical codes rendered as numbers**, which is our case.
3. What does the literature recommend: recode to letters or symbols, add custom tokens, use
   left-padded fixed-width digits, or something else? Cite evidence, and distinguish evidence from
   arithmetic tasks (where digit alignment matters) from evidence relevant to ours (where the numbers
   are labels and their internal structure is meaningless).

### Item 3. Adding tokens to the vocabulary: the practical procedure and its costs

If we add, say, 200 special tokens for activity and location codes:

1. What exactly must be done: tokenizer update, embedding matrix resize, initialisation strategy for
   the new rows, and whether the output head must be resized too (it must, in a tied-embedding model,
   so say what tying implies).
2. What is the documented **initialisation** advice for new embedding rows? Random initialisation of new
   tokens next to a trained embedding matrix is a known source of instability. Give the recommended
   approach and its source.
3. Does adding tokens break **LoRA**? Specifically: LoRA does not train the embedding matrix by
   default, so new token embeddings would remain at their initialisation. What is the standard fix,
   and does it change the memory arithmetic? This is a trap a first-timer would fall straight into and
   we want it named explicitly.
4. Does adding tokens break the **chat template**, the **tokenizer serialisation**, or any downstream
   inference engine? Name the ones that are known to be fragile about added tokens.
5. Is the alternative, choosing existing single-token strings from the vocabulary and mapping our codes
   onto them, actually better in practice? This avoids every problem above at the cost of readability.
   Say which you would do.

### Item 4. Where the conditioning vector goes

1. Prefix in the same token stream, versus a separate encoder, versus soft prompts or prefix tuning.
   For a decoder-only model, is there evidence that a long structured prefix is attended to properly
   over a 144-slot generation, or does conditioning decay along the sequence? **Conditioning decay
   would be fatal for us**, because our whole claim is that demographics drive the schedule. If
   evidence exists, cite it; if it does not, tell us what diagnostic would detect it.
2. Should the conditioning attributes be ordered from most to least predictive, or does order not
   matter? Is there evidence either way on attribute order in structured prompts?
3. Is there a published trick for **strengthening** conditioning in a decoder-only model, for example
   repeating the condition, classifier-free-guidance-style contrastive decoding, or interleaving the
   condition. Name what has evidence.

### Item 5. Sequence length and context budget

1. Given the format you recommend, what is the sequence length per record, and does it fit comfortably
   inside the native context of the models shortlisted in `L04`?
2. If we want to model **multi-day dependence** (a respondent's weekday and weekend day together, or a
   whole week), how does the budget change, and at what point do we need long-context handling?
3. If we want **household-level joint generation** (all members of one household in one sequence, so
   that co-presence is internally consistent), what does that cost, and is there any literature on
   generating multiple correlated agents in one sequence? This is a genuinely attractive design for us
   because co-presence consistency across household members is a documented weakness of the existing
   methods, so please treat it seriously rather than dismissing it on length.

### Item 6. Time-series-specific LLM work, and whether it is relevant

There is a body of work on applying LLMs to time series: reprogramming approaches, LLM-based forecasters
and pure numeric tokenisation schemes. There is also published scepticism about whether language models
help on time series at all.

1. Summarise both sides with citations.
2. State whether it applies to us. We suspect **not much**, because our sequences are categorical and
   short rather than continuous and long, and our task is population synthesis rather than forecasting.
   Confirm or correct that, and say why. We do not want to cite a body of work that a reviewer will
   correctly say is irrelevant.

## Named leads

Tokenizer documentation and tokenizer configuration files of the model families shortlisted in `L04`;
published studies of number tokenisation in LLMs; the `transformers` documentation on
`resize_token_embeddings`, `add_special_tokens` and tied embeddings; the `peft` documentation on
`modules_to_save` and on training embeddings alongside LoRA; the LLM-for-tabular-data literature for
serialisation-format ablations; the LLM-for-time-series literature and its published critiques.

## Hard constraints specific to this prompt

* **Give worked examples with real token counts.** An answer with no example string and no number is
  not usable.
* Name the tokenizer and its version for every count.
* **Do not recommend a format without saying what a single generation error does to it.** A format where
  one dropped delimiter shifts every subsequent slot is dangerous and we need that flagged.
* Do not conflate "the model can be prompted to output this format" with "this format is efficient to
  train on". They are different questions and we are asking the second.

## Deliverable

**Section B** carries the format comparison with measured token counts and the example strings.

**Section C** carries one recommended serialisation, written out in full as a specification we could
implement, including the exact handling of the conditioning prefix and the end-of-record marker.

**Section G** carries the added-token pitfalls from item 3, the conditioning-decay diagnostic from item
4, and your negative controls.
