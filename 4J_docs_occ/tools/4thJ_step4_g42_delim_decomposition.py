# G4.2 arm one: where does the delimiter loss actually live?
# Plug-in ORACLE cross-entropy at every position whose TARGET is a delimiter char.
# Conditioning is spelled out per slot; plug-in estimates are optimistic, so these
# are floors for a model with that conditioning, not for an arbitrary model.
import json, math, sys
from collections import defaultdict, Counter

PATH = sys.argv[1]
rec_n = 0
dur_len = Counter(); cop_len = Counter()
act_len = Counter(); loc_vals = Counter()
# act2 presence conditional on (country, act)
a2 = defaultdict(lambda: [0, 0])          # key -> [empty, present]
a2_marg = [0, 0]
# DUR / COP "is the number finished?" conditional on the digit prefix
num_stop = {"dur": defaultdict(lambda: [0, 0]), "cop": defaultdict(lambda: [0, 0])}
episodes = 0
prefix_field_vals = [Counter() for _ in range(6)]

def note_number(kind, s):
    d = num_stop[kind]
    for i in range(1, len(s) + 1):
        pre = s[:i]
        d[pre][1 if i == len(s) else 0] += 1   # [continues, stops]

with open(PATH, encoding="utf-8") as fh:
    for line in fh:
        r = json.loads(line)
        t = r["text"]
        pre, body = t.split("|", 1)
        pf = pre.split(",")
        for i, v in enumerate(pf[:6]):
            prefix_field_vals[i][v] += 1
        rec_n += 1
        body = body[:-len("<eor>")] if body.endswith("<eor>") else body
        for ep in body.split(";"):
            if not ep:
                continue
            f = ep.split(",")
            if len(f) != 5:
                continue
            dur, act, act2, loc, cop = f
            episodes += 1
            dur_len[len(dur)] += 1; cop_len[len(cop)] += 1
            act_len[len(act)] += 1; loc_vals[loc] += 1
            note_number("dur", dur); note_number("cop", cop)
            k = (r["country"], act)
            j = 0 if act2 == "" else 1
            a2[k][j] += 1; a2_marg[j] += 1

def xent(table, which):
    """mean -log p of the observed outcome, restricted to outcome `which`,
    and the count of such events."""
    tot_nats, n = 0.0, 0
    for k, c in table.items():
        s = c[0] + c[1]
        if s == 0 or c[which] == 0:
            continue
        p = c[which] / s
        tot_nats += c[which] * (-math.log(p)); n += c[which]
    return (tot_nats / n if n else float("nan")), n, tot_nats

print("records %d  episodes %d  (%.1f episodes/record)" % (rec_n, episodes, episodes / rec_n))
print("DUR digit-lengths", dict(sorted(dur_len.items())))
print("COP digit-lengths", dict(sorted(cop_len.items())))
print("ACT digit-lengths", dict(sorted(act_len.items())))
print("LOC values", dict(loc_vals))
print("act2 empty %d present %d  P(empty)=%.4f" % (a2_marg[0], a2_marg[1],
                                                   a2_marg[0] / (a2_marg[0] + a2_marg[1])))
# --- slot-by-slot ---
h_a2_marg = -math.log(a2_marg[0] / (a2_marg[0] + a2_marg[1]))
m_a2, n_a2, nats_a2 = xent(a2, 0)
print("\nSLOT c3 (comma right after ACT's comma, i.e. the act2 slot)")
print("  marginal oracle      : %.4f nats over %d empty-act2 positions" % (h_a2_marg, a2_marg[0]))
print("  P(empty|country,act) : %.4f nats over %d positions   [%d distinct contexts]"
      % (m_a2, n_a2, len(a2)))
for kind in ("dur", "cop"):
    m, n, nats = xent(num_stop[kind], 1)
    print("SLOT %s-terminating delimiter, char-level P(stop|digits so far): %.4f nats over %d"
          % (kind.upper(), m, n))
    num_stop[kind + "_nats"] = nats

# --- aggregate to a predicted mean delimiter loss ---
# delimiter positions per episode: c1 (after DUR), c2 (after ACT), c3 (after ACT2),
# c4 (after LOC), ';' (after COP)  = 5 ; plus per record: 5 prefix commas + 1 '|'
dl_per_rec = 5 * (episodes / rec_n) + 6
D = 5 * episodes + 6 * rec_n
print("\ndelimiter positions: %d  (%.1f per record)" % (D, dl_per_rec))
nats_dur = xent(num_stop["dur"], 1)[2]
nats_cop = xent(num_stop["cop"], 1)[2]
print("PREDICTED MEAN DELIMITER LOSS (oracle, plug-in):")
print("  T1  numbers are single tokens (act2 term only)     : %.4f nats" % (nats_a2 / D))
print("  T2  digits emitted one at a time (act2+DUR+COP)    : %.4f nats"
      % ((nats_a2 + nats_dur + nats_cop) / D))
print("  measured on the real model (job 1274838, ep1)      : 0.1094 nats")
for i, c in enumerate(prefix_field_vals):
    amb = [v for v in c if any(w != v and w.startswith(v) for w in c)]
    print("prefix field %d: %d values, prefix-ambiguous: %s" % (i, len(c), amb or "none"))
