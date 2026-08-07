#!/usr/bin/env python3
"""V5-F2 -- fail when a round opens a task built on an item a previous round already closed.

WHY THIS EXISTS. Of the four decisions v4 put to the user on 2026-08-06, TWO were about work that
was already finished:

  V4-B1  rested on `V2-B4`, decided 2026-08-05, and `V2-D10`, EXECUTED the same evening -- locally,
         without the cluster. v4 described its execution as "blocked on compute". It was not.
  V4-B3  rested on `V2-A1`, run 2026-08-04, which had already falsified the premise. v4 gave it a
         13-August notification deadline for a notification nobody owed.

Both were written into the round from prose -- memory files, an audit document, superseded prompts.
The v2 plan's status table, which has an explicit terminal row for each, was never opened.
**Spending a user's decision on a question that already has an answer is worse than not asking it.**

The rule this enforces, adopted 2026-08-06: *never open an item naming a prior finding without
quoting that finding's terminal-status row.*

FOUR CHECKS:
  D1  every task in the round that names a CLOSED prior item quotes its status (one of the terminal
      words appears in the same task block).
  D2  no task in a live state (`open`, `ready`, `decided`, `partial`) rests on a closed prior item.
      D1 is satisfied by mentioning the word anywhere in the block; D2 asks the harder question --
      is this task alive on top of something already finished.
  D3  every prior ID the round names exists in the registry. A task citing `V2-D99` is as broken as
      one re-opening `V2-D10`, and citing an ID that does not exist is how prose becomes a task.
  D4  the round actually names at least one closed prior item. If it names none, D1 and D2 are
      vacuous and the run says nothing -- that is reported, not counted as a pass.

    python f2_no_reopen_check.py [--round v4] [--falsify]
"""
import argparse
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
IMPROVEMENTS = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(IMPROVEMENTS, ".."))
FIXTURES = os.path.join(HERE, "fixtures")

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# | ✅ | **V2-A1** | title | cost | deps | DONE 08-04 · B-13 withdrawn, no erratum owed |
STATUS_ROW = re.compile(r"^\|([^|\n]*)\|\s*\*\*(V\d-[A-Z]\d+)\*\*\s*\|(.*)\|\s*$", re.M)
TASK_HEAD = re.compile(r"^###\s+(?:~~)?\s*(V\d-[A-Z]\d+)\b(.*)$", re.M)
REF = re.compile(r"\bV(\d)-([A-Z]\d+)\b")

TERMINAL_WORDS = ("DONE", "DECIDED", "CLOSED", "WITHDRAWN", "EXECUTED", "FIXED",
                  "ACCEPTED-AS-DOCUMENTED", "FALSIFIED")
LIVE_STATES = ("open", "ready", "partial", "waiting")

_N = {"pass": 0, "fail": 0}


def rec(tag, ok, detail):
    _N["pass" if ok else "fail"] += 1
    print("  [%s] %-3s %s" % ("PASS" if ok else "FAIL", tag, detail))


def plans():
    """Every round plan on disk, oldest first."""
    out = []
    for r in sorted(os.listdir(IMPROVEMENTS)):
        d = os.path.join(IMPROVEMENTS, r)
        if not (os.path.isdir(d) and re.match(r"^v\d+$", r)):
            continue
        for name in sorted(os.listdir(d)):
            if name.endswith("_implementation.md"):
                out.append((r, os.path.join(d, name)))
    return out


def registry(exclude_round):
    """{id: (status_cell, round)} for every task row in every EARLIER round plan."""
    reg = {}
    for r, path in plans():
        if r == exclude_round:
            continue
        with io.open(path, encoding="utf-8") as fh:
            text = fh.read()
        for tick, tid, rest in STATUS_ROW.findall(text):
            cells = [c.strip() for c in rest.split("|")]
            status = cells[-1] if cells else ""
            closed = ("✅" in tick) or any(w in status.upper() for w in TERMINAL_WORDS)
            if tid not in reg or closed:
                reg[tid] = (status, r, closed)
    return reg


def tasks(plan_path):
    """[(id, heading, body)] for the round's own task sections."""
    with io.open(plan_path, encoding="utf-8") as fh:
        text = fh.read()
    heads = list(TASK_HEAD.finditer(text))
    out = []
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        out.append((m.group(1), m.group(0).strip(), text[m.start():end]))
    return out


def main(round_name, falsify):
    plan = (os.path.join(FIXTURES, "v4_plan_AS_FIRST_WRITTEN.md") if falsify
            else os.path.join(IMPROVEMENTS, round_name, "3rdJ_L3_%s_implementation.md" % round_name))
    reg = registry(round_name)
    closed = {k: v for k, v in reg.items() if v[2]}
    print("V5-F2 -- no-reopen check   (round: %s%s)"
          % (round_name, "   FALSIFY MODE" if falsify else ""))
    print("  registry: %d prior task rows, %d of them terminal, from %s"
          % (len(reg), len(closed), ", ".join(r for r, _ in plans() if r != round_name)))
    print("  plan: %s\n" % os.path.relpath(plan, ROOT).replace("\\", "/"))

    ts = tasks(plan)
    own = round_name.lstrip("v")            # same-round cross-references are not "prior items"
    d1, d2, d3, named_closed = [], [], [], []
    for tid, head, body in ts:
        refs = {"V%s-%s" % (a, b) for a, b in REF.findall(body) if a != own} - {tid}
        upper = body.upper()
        lower = body.lower()
        live = any(re.search(r"(?:state|status)\s*:?\s*\**\s*%s\b" % s, lower) or
                   ("`%s`" % s) in lower or (" %s " % s) in head.lower()
                   for s in LIVE_STATES)
        for ref in sorted(refs):
            if ref not in reg:
                d3.append((tid, ref))
                continue
            if not reg[ref][2]:
                continue
            named_closed.append((tid, ref))
            # D1 and D2 are evaluated INDEPENDENTLY on purpose. Chaining them with elif is how
            # V2-G5's falsifier ended up testing one check twice and the other not at all.
            if not any(w in upper for w in TERMINAL_WORDS):
                d1.append((tid, ref, reg[ref][0][:70]))
            if live and "~~" not in head and "WITHDRAWN" not in upper:
                d2.append((tid, ref, reg[ref][0][:70]))

    rec("D1", not d1, "every task naming a closed item quotes a terminal status"
        if not d1 else "%d task/item pair(s) name a closed item without quoting its status:" % len(d1))
    for tid, ref, st in d1:
        print("        %s names %s -- registry says: %s" % (tid, ref, st))

    rec("D2", not d2, "no live task rests on a closed prior item"
        if not d2 else "%d live task(s) rest on an item already closed:" % len(d2))
    for tid, ref, st in d2:
        print("        %s rests on %s -- registry says: %s" % (tid, ref, st))

    rec("D3", not d3, "every prior ID named by the round exists"
        if not d3 else "%d reference(s) to an ID that is in no plan:" % len(d3))
    for tid, ref in d3:
        print("        %s names %s -- not in any round plan" % (tid, ref))

    rec("D4", bool(named_closed),
        "the round names %d closed prior item(s), so D1/D2 are live" % len(named_closed)
        if named_closed else "the round names NO closed prior item -- D1 and D2 said nothing")

    print("\n  %d tasks read; %d PASS / %d FAIL" % (len(ts), _N["pass"], _N["fail"]))
    return 0 if _N["fail"] == 0 else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", default="v4")
    ap.add_argument("--falsify", action="store_true",
                    help="read fixtures/v4_plan_AS_FIRST_WRITTEN.md -- the two never-open tasks")
    a = ap.parse_args()
    sys.exit(main(a.round, a.falsify))
