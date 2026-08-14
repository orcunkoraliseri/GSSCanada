#!/usr/bin/env python
"""
4J: read Meta's Llama licences and find out what Section 1.b actually says.

Why this is not a formality. Every plan document disqualifies Llama on one sentence:
"Section 1.b forbids using Llama outputs to improve any other non-Llama model", taken from
RL18 B08. Job 1234216 searched the Llama 3.1 licence Meta publishes on GitHub for that exact
phrase and DID NOT FIND IT. Either the phrasing differs, or the clause belongs to an earlier
Llama version and 3.1 relaxed it. Those two possibilities have opposite consequences for the
model-family decision, so the text gets printed in full rather than searched for a phrase we
expected to be there.

Llama 2 and Llama 3 carried an anti-distillation clause. Whether Llama 3.1 kept it, replaced
it with a naming requirement, or dropped it is the question. Print every clause that mentions
outputs, improving a model, or a model name, for each licence version we can reach.

CPU only, text only.
Run with sbatch. Never on the login node.
"""

import re
import sys
import traceback
import urllib.request

GH = "https://raw.githubusercontent.com/meta-llama/llama-models/main/models/%s/LICENSE"
SOURCES = [
    ("Llama 3.1", GH % "llama3_1"),
    ("Llama 3.2", GH % "llama3_2"),
    ("Llama 3.3", GH % "llama3_3"),
    ("Llama 3",   GH % "llama3"),
    ("Llama 2",   "https://raw.githubusercontent.com/meta-llama/llama/main/LICENSE"),
]

# Words whose presence or absence decides the question.
PROBES = ["improve", "output", "derivative", "Llama Materials", "name", "distill"]


def fetch(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 4J-check"})
    with urllib.request.urlopen(req, timeout=timeout) as fh:
        return fh.read().decode("utf-8", "replace")


def sentences(text):
    flat = re.sub(r"\s+", " ", text)
    return re.split(r"(?<=[.;])\s+", flat)


def report(label, url):
    print("=" * 78)
    print("%s" % label)
    print("URL %s" % url)
    try:
        text = fetch(url)
    except Exception as exc:
        print("   COULD NOT FETCH -- %s: %s" % (type(exc).__name__, str(exc)[:160]))
        return
    print("   %d bytes" % len(text))

    # 1. the whole of clause 1 verbatim, which is where the disputed sentence lives
    flat = re.sub(r"\s+", " ", text)
    m = re.search(r"1\.\s*License Rights and Redistribution(.{0,4000}?)(?:2\.\s*Additional|"
                  r"2\.\s*Commercial|$)", flat, re.S)
    if m:
        print("-- Clause 1 verbatim ------------------------------------------------------")
        body = m.group(1).strip()
        for i in range(0, len(body), 110):
            print("   %s" % body[i:i + 110])
    else:
        print("-- could not locate a clause 1 heading; printing the first 1500 characters")
        for i in range(0, min(1500, len(flat)), 110):
            print("   %s" % flat[i:i + 110])

    # 2. every sentence containing a probe word, so nothing is missed by a heading regex
    print("-- sentences mentioning the decisive words --------------------------------")
    seen = set()
    for s in sentences(text):
        low = s.lower()
        if any(p.lower() in low for p in PROBES) and s not in seen:
            seen.add(s)
            print("   * %s" % s.strip()[:320])

    # 3. the counts, so absence is stated as a measurement
    print("-- probe counts -----------------------------------------------------------")
    low = text.lower()
    for p in PROBES:
        print("   %-18s %d" % (p, low.count(p.lower())))
    for phrase in ["improve any other large language model",
                   "improve any other model",
                   "otherwise improve an AI model",
                   "improve an AI model"]:
        print('   "%s"  ->  %d' % (phrase, low.count(phrase.lower())))


def main():
    print("4J: what Meta's licences actually say about outputs")
    for label, url in SOURCES:
        try:
            report(label, url)
        except Exception:
            print("UNEXPECTED FAILURE on %s" % label)
            traceback.print_exc()
    print()
    print("HOW TO READ IT")
    print(" 1. if Llama 3.1 carries only a NAMING requirement and no anti-improvement clause,")
    print("    then RL18 B08 is wrong and Llama was disqualified on a clause from an older")
    print("    licence version. That does not automatically requalify Llama, but the reason")
    print("    written in the plan documents would be false and must be rewritten.")
    print(" 2. a licence we could not fetch proves nothing about it.")


if __name__ == "__main__":
    main()
