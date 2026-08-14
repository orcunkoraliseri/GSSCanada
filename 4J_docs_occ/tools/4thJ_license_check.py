#!/usr/bin/env python
"""
4J: read the licences ourselves, and count parameters ourselves.

Why. Every licence claim in this project so far came from the RL18 deep-research report,
and RL18 has already been caught in two factual errors (it counts "45" as 1 Qwen token
when it is 2, and its landscape table predates Qwen3 / Llama 4 / OLMo 3). The licence is
the load-bearing constraint of the whole 4J design: weights and adapters CANNOT be
released under the Eurostat and StatCan microdata agreements, so the ONLY releasable
artefact is the generated synthetic diary corpus. A backbone whose licence puts any
condition on generated text (Meta Llama Community Licence s.1.b) cannot be used. So the
licence must be read, not cited.

  Q1  what licence does each candidate actually carry, per the HF API and the LICENSE file
  Q2  is the repo gated (a gate is a second, separate condition on top of the licence)
  Q3  how many parameters does each repo really have, from safetensors metadata, so the
      "is there a Leg-4 pilot size" question is answered by measurement and not by the
      number in the repo name
  Q4  does any OLMo 3 base checkpoint exist below 7B that the name-search missed

CPU only, no model weights downloaded, config and metadata requests only.
Run with sbatch. Never on the login node.
"""

import json
import re
import sys
import traceback
import urllib.error
import urllib.request

INFO = "https://huggingface.co/api/models/%s"
RAW = "https://huggingface.co/%s/raw/main/%s"
LIST = "https://huggingface.co/api/models?author=%s&search=%s&limit=200&full=true"

# The candidates the measurement campaign has narrowed to, plus the ones we ruled out,
# so the ruling-out is on the record with its evidence and not just in a chat message.
REPOS = [
    ("allenai/Olmo-3-1025-7B",           "OLMo 3 base, current first choice"),
    ("allenai/Olmo-3-1125-32B",          "OLMo 3 base, largest"),
    ("allenai/OLMo-2-0425-1B",           "OLMo 2 base, the only sub-7B OLMo pilot size"),
    ("allenai/OLMo-2-1124-7B",           "OLMo 2 base, superseded by OLMo 3"),
    ("Qwen/Qwen2.5-0.5B",                "Qwen pilot size"),
    ("Qwen/Qwen2.5-1.5B",                "Qwen pilot size"),
    ("Qwen/Qwen2.5-3B",                  "Qwen, reported NON-COMMERCIAL, verify"),
    ("Qwen/Qwen2.5-7B",                  "Qwen, the RL18 recommendation"),
    ("Qwen/Qwen3-8B",                    "Qwen3, absent from RL18 entirely"),
    ("meta-llama/Llama-3.1-8B",          "Llama, ruled out on licence s.1.b, verify"),
    ("mistralai/Mistral-7B-v0.3",        "Mistral, tokenizer already measured as worse"),
]

# Filenames a repo may put its licence in.
LICENSE_FILES = ["LICENSE", "LICENSE.txt", "LICENSE.md", "LICENCE", "NOTICE"]

# Phrases that would make a licence incompatible with releasing a CC BY 4.0 corpus of
# model-generated text. We search for them literally rather than trusting a summary.
RED_FLAGS = [
    "improve any other large language model",
    "improve any other model",
    "non-commercial",
    "noncommercial",
    "research purposes only",
    "acceptable use policy",
    "output",
    "derivative works",
]


def fetch(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "4J-license-check"})
    with urllib.request.urlopen(req, timeout=timeout) as fh:
        return fh.read().decode("utf-8", "replace")


def api(repo):
    try:
        return json.loads(fetch(INFO % repo))
    except urllib.error.HTTPError as exc:
        return {"_error": "HTTP %s" % exc.code}
    except Exception as exc:
        return {"_error": "%s: %s" % (type(exc).__name__, str(exc)[:160])}


def params_of(meta):
    """Parameter count from safetensors metadata, in billions. 0 if not published."""
    st = meta.get("safetensors") or {}
    total = st.get("total")
    if not total:
        params = st.get("parameters") or {}
        total = sum(v for v in params.values() if isinstance(v, int))
    return (total or 0) / 1e9


def licence_text(repo):
    """Return (filename, text) for the first licence file that exists, else (None, '')."""
    for name in LICENSE_FILES:
        try:
            return name, fetch(RAW % (repo, name))
        except Exception:
            continue
    return None, ""


def check(repo, note):
    print("-" * 78)
    print("REPO   %s" % repo)
    print("NOTE   %s" % note)
    meta = api(repo)
    if "_error" in meta:
        print("STATUS COULD NOT READ -- %s" % meta["_error"])
        print("       a repo we cannot read proves nothing. It is not evidence of a licence.")
        return {"repo": repo, "license": "UNREADABLE", "gated": "?", "params": 0.0,
                "file": None, "flags": []}

    card = meta.get("cardData") or {}
    lic = card.get("license") or "not declared"
    lic_name = card.get("license_name") or ""
    lic_link = card.get("license_link") or ""
    gated = meta.get("gated", False)
    params = params_of(meta)
    tags = [t for t in (meta.get("tags") or []) if t.startswith("license:")]

    print("STATUS read ok")
    print("   cardData.license         %s" % lic)
    if lic_name:
        print("   cardData.license_name    %s" % lic_name)
    if lic_link:
        print("   cardData.license_link    %s" % lic_link)
    print("   license tags             %s" % (tags or "none"))
    print("   gated                    %s" % gated)
    print("   parameters (safetensors) %.2f B" % params)
    print("   downloads last month     %s" % meta.get("downloads", "?"))

    fname, text = licence_text(repo)
    flags = []
    if fname:
        print("   LICENSE file             %s, %d bytes" % (fname, len(text)))
        head = [ln.strip() for ln in text.splitlines() if ln.strip()][:6]
        for ln in head:
            print("      | %s" % ln[:110])
        low = text.lower()
        for phrase in RED_FLAGS:
            n = low.count(phrase)
            if n:
                flags.append(phrase)
                # Show the sentence around the FIRST hit, so the phrase is read in context.
                i = low.find(phrase)
                ctx = re.sub(r"\s+", " ", text[max(0, i - 200):i + 260]).strip()
                print("   >> contains %-38s x%d" % ('"%s"' % phrase, n))
                print("      ...%s..." % ctx[:400])
    else:
        print("   LICENSE file             none of %s present" % ", ".join(LICENSE_FILES))
        print("                            (the cardData tag is then the only statement)")

    return {"repo": repo, "license": lic, "gated": gated, "params": params,
            "file": fname, "flags": flags}


def sweep_olmo_sizes():
    """Q3/Q4: list every allenai OLMo repo with its measured parameter count."""
    print("=" * 78)
    print("Q3/Q4 -- every allenai OLMo repo, by MEASURED parameter count")
    print("=" * 78)
    seen = {}
    for term in ["OLMo", "Olmo"]:
        try:
            data = json.loads(fetch(LIST % ("allenai", term)))
        except Exception as exc:
            print("SEARCH %-6s COULD NOT FETCH -- %s" % (term, type(exc).__name__))
            continue
        print("SEARCH %-6s %d results" % (term, len(data)))
        for m in data:
            seen[m.get("id", "?")] = m
    if not seen:
        print("NOTHING FOUND -- no network to the HF API, or the naming changed.")
        return
    derived = ("instruct", "sft", "dpo", "rlvr", "think", "chat", "gguf",
               "rl-zero", "tokenizer", "preview", "hf", "sysprompt")
    rows = []
    for mid, m in seen.items():
        if any(t in mid.lower() for t in derived):
            continue
        rows.append((params_of(m), mid, (m.get("cardData") or {}).get("license", "?")))
    print()
    print("BASE checkpoints only, smallest first")
    print("   %-42s %10s  %s" % ("repo", "params B", "license"))
    for p, mid, lic in sorted(rows):
        print("   %-42s %10.2f  %s" % (mid, p, lic))
    small = [(p, mid) for p, mid, _ in rows if 0 < p <= 2.5 and "3" in mid.split("/")[-1][:7]]
    print()
    print("   OLMo 3 base checkpoints at or under 2.5B: %s"
          % (small if small else "NONE -- the family has no cheap pilot size"))


def main():
    print("4J licence and size verification")
    try:
        sweep_olmo_sizes()
    except Exception:
        print("UNEXPECTED FAILURE in the OLMo size sweep")
        traceback.print_exc()

    print()
    print("=" * 78)
    print("Q1/Q2 -- licence and gating, read from the repo itself")
    print("=" * 78)
    rows = []
    for repo, note in REPOS:
        try:
            rows.append(check(repo, note))
        except Exception:
            print("UNEXPECTED FAILURE on %s" % repo)
            traceback.print_exc()

    print()
    print("=" * 78)
    print("SUMMARY")
    print("%-34s %10s %8s %-26s %s"
          % ("repo", "params B", "gated", "license", "licence file"))
    for r in rows:
        print("%-34s %10.2f %8s %-26s %s"
              % (r["repo"], r["params"], r["gated"], str(r["license"])[:26],
                 r["file"] or "-"))

    print()
    print("PHRASES FOUND, per repo")
    for r in rows:
        if r["flags"]:
            print("   %-34s %s" % (r["repo"], ", ".join(r["flags"])))
    print()
    print("HOW TO READ IT")
    print(" 1. apache-2.0 puts NO condition on generated text. The synthetic diary corpus")
    print("    can then be released CC BY 4.0 with no upstream term attached to it.")
    print(' 2. a hit on "improve any other large language model" is the Llama s.1.b clause.')
    print("    It is the clause that disqualifies a backbone for this project.")
    print(" 3. gated=True is a SEPARATE condition from the licence. It means we must accept")
    print("    terms on an HF account before we can even read the weights.")
    print(" 4. a repo we could not read proves nothing. It is not evidence either way.")


if __name__ == "__main__":
    main()
