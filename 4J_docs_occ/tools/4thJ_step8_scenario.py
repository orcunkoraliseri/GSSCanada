# -*- coding: utf-8 -*-
"""4J Step 8 --- THE SCENARIO PATH AND ITS CACHE KEY.  Written for 8.4, used by 8.5.

    "In 3J two nominally different scenarios produced byte-identical result
     files across all 56 cells and every scorecard stayed green, because the
     injector re-pointed nothing and nothing compared the OUTPUTS."

This module is deliberately small and it exists BEFORE the campaign, because
`G8.8` and `G8.9` can only be seen firing against a real scenario path and a
real cache.  Work item 8.4 exercises exactly this file; 8.5 imports it rather
than re-implementing it, so the thing the probes proved is the thing that runs.

WHAT A SCENARIO IS, EXACTLY
---------------------------
`D-S8-2` item 5 was ruled (c) and pre-registered:

    phi_int(t) = (1 - f) * 3.0  +  f * 3.0 * g(t) / mean_year(g(t))

with f in {0.00, 0.15, 0.30, 0.50, 1.00} and `f = 0` the control.  The IDF
carries the WATTS as `OtherEquipment E_PHI_INT`'s Design Level and the shape as
its Schedule Name, so a scenario is applied by writing a multiplier series

    m(t) = (1 - f) + f * g(t) / mean_year(g(t))

whose annual mean is EXACTLY 1.0 by construction, and re-pointing E_PHI_INT at
it.  The design level never moves, so the annual mean of phi_int stays exactly
3.0 W/m2 at every f --- which is what the pre-registration says, and it is
asserted here rather than trusted.

THREE TRAPS, EACH ONE ALREADY MET IN THIS PROJECT
--------------------------------------------------
  * `ScheduleTypeLimits Frac` is 0.0-1.0 and EnergyPlus CLIPS to it.  m(t) is
    above 1.0 wherever the household is more present than its own annual mean,
    so re-using `Frac` would silently flatten every peak the paper is about.
    A separate `PhiMult` limit is written, and `inject` refuses `Frac`.
  * `Interpolate to Timestep` must be `No` (`G8.13`), and the model runs at
    Timestep 6, so a `Yes` here would smear the hourly shape.  It is written
    `No` and the probe reads it back out of the SAVED IDF.
  * The cache key must contain every input that can change the result.  A key
    over the cell name alone is what `G8.9` exists to catch, so the broken key
    lives here too --- named `naive_cache_key`, never called by a runner.
"""
import hashlib
import io
import json
import os

FLAT_SCHEDULE_NAME = "SCH_ALWAYS_ON"        # what 8.1 built: a constant 1.0
PHI_SCHEDULE_NAME = "SCH_PHI_INT"           # what a scenario re-points to
PHI_TYPE_LIMITS = "PhiMult"                 # NOT Frac --- see the traps above
SWEEP_F = (0.00, 0.15, 0.30, 0.50, 1.00)    # D-S8-2 item 5, ruled (c)
PHI_INT_MEAN_W_M2 = 3.0                     # TABULA EU.SUH/EU.MUH, held at every f
HOURS = 8760


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_presence(path):
    """A Step 7 presence file as 8760 floats.  One header line, then the values."""
    with io.open(path, encoding="utf-8") as fh:
        lines = [ln.strip() for ln in fh if ln.strip() != ""]
    if len(lines) != HOURS + 1:
        raise ValueError("%s has %d non-empty lines, expected %d (header + %d)"
                         % (path, len(lines), HOURS + 1, HOURS))
    return [float(x) for x in lines[1:]]


def multiplier_series(g, f):
    """m(t) = (1 - f) + f * g(t)/mean(g).  Annual mean is exactly 1.0."""
    if not 0.0 <= f <= 1.0:
        raise ValueError("f = %r outside [0, 1]" % f)
    n = len(g)
    if n != HOURS:
        raise ValueError("presence has %d values, expected %d" % (n, HOURS))
    mean_g = sum(g) / n
    if mean_g <= 0.0:
        raise ValueError("mean presence is %r --- no shape to apply" % mean_g)
    m = [(1.0 - f) + f * x / mean_g for x in g]
    mean_m = sum(m) / n
    if abs(mean_m - 1.0) > 1e-9:
        raise AssertionError("multiplier mean %.12f != 1.0 --- the annual mean of "
                             "phi_int would move, and the pre-registration says "
                             "it does not" % mean_m)
    return m


WRITE_DECIMALS = 6          # what 8.4 wrote; kept as the DEFAULT so 8.4 reproduces


def write_multiplier_csv(dst, m, label, decimals=WRITE_DECIMALS):
    """One column, one header line --- what Schedule:File is told to expect.

    \U0001f534 `decimals` is a DECLARED parameter and not a formatting detail.
    `multiplier_series` asserts that the annual mean of `m(t)` is 1.0 to 1e-9,
    but it asserts it of the list in memory; the file EnergyPlus reads is this
    one, and at `%.6f` its mean sits 4.01e-07 away from 1.0.  That is
    3.0000012 W/m2 instead of the pre-registered 3.0 --- physically nothing, and
    a false statement all the same, of exactly the kind that survives when a
    transform checks its own numbers instead of its own output.

    The residue is bounded BY CONSTRUCTION at half a unit in the last place,
    `0.5 * 10**-decimals`, so the caller chooses the bound rather than measuring
    it afterwards.  The default stays 6 so that work item 8.4's artefacts and
    the md5s recorded in `probes_step8.json` reproduce byte-for-byte; work item
    8.5 asks for 10.
    """
    d = os.path.dirname(dst)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    fmt = "%." + str(int(decimals)) + "f\n"
    with io.open(dst, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(label + "\n")
        for x in m:
            fh.write(fmt % x)
    return dst


def _phi_block(text):
    """The OtherEquipment object named E_PHI_INT, located by NAME and not by index."""
    i = text.find("OtherEquipment,")
    while i != -1:
        j = text.find(";", i)
        if j == -1:
            break
        blk = text[i:j + 1]
        if "E_PHI_INT" in blk:
            return i, j + 1, blk
        i = text.find("OtherEquipment,", j)
    raise ValueError("no OtherEquipment object named E_PHI_INT in this IDF")


def inject(idf_text, csv_path, sched_name=PHI_SCHEDULE_NAME,
           type_limits=PHI_TYPE_LIMITS, interpolate="No"):
    """Re-point E_PHI_INT at a Schedule:File built from `csv_path`.

    Returns the new IDF text.  Refuses anything it cannot verify: the block must
    exist, it must currently name the flat schedule exactly once, the target
    name must not already be in the file, and the path must be writable into an
    IDF field at all.
    """
    if type_limits == "Frac":
        raise ValueError("Frac is 0.0-1.0 and EnergyPlus clips to it; the "
                         "multiplier exceeds 1.0 by construction")
    if interpolate != "No":
        raise ValueError("G8.13: Interpolate to Timestep must be No, got %r"
                         % interpolate)
    for ch in (",", ";", "!"):
        if ch in csv_path:
            raise ValueError("schedule path contains %r and cannot be an IDF field"
                             % ch)
    if sched_name in idf_text:
        raise ValueError("%s already present in this IDF" % sched_name)

    i, j, blk = _phi_block(idf_text)
    if blk.count(FLAT_SCHEDULE_NAME) != 1:
        raise ValueError("E_PHI_INT names %s %d times, expected exactly 1"
                         % (FLAT_SCHEDULE_NAME, blk.count(FLAT_SCHEDULE_NAME)))
    out = idf_text[:i] + blk.replace(FLAT_SCHEDULE_NAME, sched_name) + idf_text[j:]

    out += ("\n\nScheduleTypeLimits, %s, 0.0, 100.0, Continuous;\n"
            "Schedule:File,\n"
            "  %s,                    !- Name\n"
            "  %s,                    !- Schedule Type Limits Name\n"
            "  %s,                    !- File Name\n"
            "  1,                     !- Column Number\n"
            "  1,                     !- Rows to Skip at Top\n"
            "  %d,                    !- Number of Hours of Data\n"
            "  Comma,                 !- Column Separator\n"
            "  %s,                    !- Interpolate to Timestep\n"
            "  60;                    !- Minutes per Item\n"
            % (type_limits, sched_name, type_limits, csv_path, HOURS, interpolate))
    return out


def cache_key(parts):
    """Every input that can change the result, and nothing that cannot.

    `parts` is a dict; it is hashed canonically so key order cannot change the
    key.  What goes in is the caller's responsibility, and `G8.9` is what checks
    the caller got it right --- by CHANGING a schedule and requiring a re-run.
    """
    blob = json.dumps(parts, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def naive_cache_key(cell):
    """The 3J defect, kept by name so the probe can be seen firing on it.

    A key over the cell identity alone: change the schedule, change the weather,
    change the engine --- the key does not move and the stale directory is
    reused.  Nothing in a runner may call this.
    """
    return hashlib.sha256(("cell:" + cell).encode("utf-8")).hexdigest()
