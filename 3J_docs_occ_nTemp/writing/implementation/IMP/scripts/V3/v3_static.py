"""V3 static IDF comparator: object-level, with every schedule REFERENCE replaced by the schedule's
expanded content, so an injected MXU_* schedule and the NECB schedule it copies compare equal when
(and only when) EnergyPlus would see the same values on every day type of every month.

Scope of the schedule engine: Schedule:Compact (Through / For / Until, Interpolate not used in these
files), Schedule:Constant. Other schedule classes are referenced by NAME (not expanded) -- fine here
because the only schedules the injector writes or re-points are Schedule:Compact.
Missing day types in a Schedule:Compact are expanded as 0.0, which is what EnergyPlus does with them
(warning "Missing day types will have 0.0 values").

Output-reporting objects (Output:*, OutputControl:*) and object order are ignored.

    py -3 v3_static.py <a.idf> <b.idf>      -> prints differing objects, exit 0 if none
"""
import hashlib
import re
import sys

DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Holiday",
        "SummerDesignDay", "WinterDesignDay", "CustomDay1", "CustomDay2"]
WEEKDAYS = DAYS[1:6]
MONTH_END = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
IGNORE_PREFIX = ("OUTPUT:", "OUTPUTCONTROL:")
SCHED_FIELDS = {  # class -> 0-based field indexes that hold schedule names
    "PEOPLE": (2, 9, 14, 16, 17, 18),
    "LIGHTS": (2,), "ELECTRICEQUIPMENT": (2,), "GASEQUIPMENT": (2,),
    "WATERUSE:EQUIPMENT": (3, 4, 5, 6, 8, 9),
}


def objects(txt):
    out = []
    for m in re.finditer(r"(?m)^([A-Za-z][A-Za-z0-9:]*),[ \t]*(?:!.*)?\r?$", txt):
        end = txt.find(";", m.end())
        raw = "".join(re.sub(r"!.*", "", l) for l in txt[m.end():end].split("\n"))
        out.append((m.group(1).upper(), [f.strip() for f in raw.split(",")]))
    return out


def _day_tokens(s):
    t = s.split(":", 1)[1].upper().split()
    days, fill = set(), False
    for x in t:
        if x in ("WEEKDAYS", "WEEKDAY"):
            days |= set(WEEKDAYS)
        elif x in ("WEEKENDS", "WEEKEND"):
            days |= {"Saturday", "Sunday"}
        elif x in ("HOLIDAYS", "HOLIDAY"):
            days.add("Holiday")
        elif x == "ALLDAYS":
            days |= set(DAYS)
        elif x == "ALLOTHERDAYS":
            fill = True
        else:
            hit = [d for d in DAYS if d.upper() == x]
            if not hit:
                raise ValueError("unknown day token %r" % x)
            days.add(hit[0])
    return days, fill


def expand_compact(fields):
    """-> tuple over 12 months x 12 day types of 48 half-hour values (rounded 1e-9)."""
    table = {}
    month0 = 1
    i = 2
    blocks = []                     # (month_from, month_to, [(days, fill, [(until_min, val)])])
    cur = None
    while i < len(fields):
        f = fields[i]
        fl = f.lower()
        if fl.startswith("through"):
            mm, dd = [int(x) for x in f.split(":", 1)[1].strip().split("/")]
            if dd != MONTH_END[mm - 1]:
                raise ValueError("Through date not at month end: %s" % f)
            cur = [month0, mm, []]
            blocks.append(cur)
            month0 = mm + 1
            i += 1
        elif fl.startswith("for"):
            days, fill = _day_tokens(f)
            cur[2].append([days, fill, []])
            i += 1
        elif fl.startswith("until"):
            hh, mi = [int(x) for x in f.split(":", 1)[1].strip().split(":")]
            cur[2][-1][2].append((hh * 60 + mi, float(fields[i + 1])))
            i += 2
        elif fl.startswith("interpolate"):
            if f.split(":", 1)[1].strip().lower() not in ("no",):
                raise ValueError("Interpolate not supported: %s" % f)
            i += 1
        else:
            raise ValueError("unexpected Schedule:Compact field %r" % f)
    for m_from, m_to, fors in blocks:
        claimed = {}
        for days, fill, pairs in fors:
            prof = []
            for slot in range(48):
                slot_end = (slot + 1) * 30      # an `Until: t` value covers the interval ending at t
                if any(u % 30 for u, _ in pairs):
                    raise ValueError("Until not on a 30-min grid")
                j = next(k for k, (u, _) in enumerate(pairs) if u >= slot_end)
                prof.append(round(pairs[j][1], 9))
            target = [d for d in DAYS if d not in claimed] if fill else [d for d in days if d not in claimed]
            for d in target:
                claimed[d] = tuple(prof)
        for m in range(m_from, m_to + 1):
            for d in DAYS:
                table[(m, d)] = claimed.get(d, tuple([0.0] * 48))
    return tuple(table[(m, d)] for m in range(1, 13) for d in DAYS)


def schedule_map(objs):
    sm = {}
    for cls, f in objs:
        if cls == "SCHEDULE:COMPACT":
            sm[f[0].upper()] = ("C", hashlib.md5(repr(expand_compact(f)).encode()).hexdigest()[:16])
        elif cls == "SCHEDULE:CONSTANT":
            sm[f[0].upper()] = ("K", round(float(f[2]), 9))
    return sm


def _norm(v):
    try:
        return repr(round(float(v), 9))
    except ValueError:
        return v.upper()


def canonical(path, rename_people=False):
    objs = objects(open(path, errors="replace").read())
    sm = schedule_map(objs)
    out = []
    for cls, f in objs:
        if cls.startswith(IGNORE_PREFIX) or cls in ("SCHEDULE:COMPACT", "SCHEDULE:CONSTANT"):
            continue
        g = [_norm(x) for x in f]
        for k in SCHED_FIELDS.get(cls, ()):
            if k < len(g) and g[k] and g[k].upper() in sm:
                g[k] = "SCHED%s" % (sm[g[k].upper()],)
        # IDD defaults written out explicitly by eppy == left blank (PEOPLE: Cold/Heat Stress
        # Temperature Threshold, IDD default 15.56 / 30, 0-based fields 27/28 in E+ 24.2).
        if cls == "PEOPLE" and len(g) >= 29 and g[27:29] == ["15.56", "30.0"]:
            g[27], g[28] = "", ""
        while g and g[-1] == "":
            g.pop()
        out.append((cls, tuple(g)))
    return sorted(out)


def compare(a, b, max_show=40):
    ca, cb = canonical(a), canonical(b)
    from collections import Counter
    A, B = Counter(ca), Counter(cb)
    only_a = sorted((A - B).elements())
    only_b = sorted((B - A).elements())
    lines = ["only in A (%d):" % len(only_a)] + ["  %s %s" % (c, list(g)[:6]) for c, g in only_a[:max_show]]
    lines += ["only in B (%d):" % len(only_b)] + ["  %s %s" % (c, list(g)[:6]) for c, g in only_b[:max_show]]
    digest_a = hashlib.md5(repr(ca).encode()).hexdigest()
    digest_b = hashlib.md5(repr(cb).encode()).hexdigest()
    return {"n_only_a": len(only_a), "n_only_b": len(only_b), "digest_a": digest_a,
            "digest_b": digest_b, "classes_only_a": sorted({c for c, _ in only_a}),
            "classes_only_b": sorted({c for c, _ in only_b}), "report": "\n".join(lines)}


def digest(path):
    return hashlib.md5(repr(canonical(path)).encode()).hexdigest()


if __name__ == "__main__":
    r = compare(sys.argv[1], sys.argv[2])
    print(r["report"])
    print("digest A", r["digest_a"], " digest B", r["digest_b"])
    sys.exit(0 if r["n_only_a"] == 0 and r["n_only_b"] == 0 else 1)
