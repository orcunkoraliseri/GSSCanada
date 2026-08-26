# L29. How does the literature subdivide a **non-convex or courtyard** residential footprint into dwellings — and what is the energy cost of refusing to?

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
Sections C, D, E and F used.

**This prompt is for Step 10** (`Step10_docs/4thJ_10_ubemRealStock.md` §6), which is new scope added
2026-08-26. It deliberately does **not** re-ask the questions answered by the existing seven-part
floor-layout dossier — see "What we already hold" below. Answer only the residual.

---

## What we already hold, and must not be told again

`Step8_docs/IMP_step8/DeepResearch/` contains `DR01`–`DR07`:

* `DR01` state of the art in residential floor-layout generation;
* `DR02` floor-to-unit division and staircase buffer methods;
* `DR03` thermal-zoning resolution and energy sensitivity;
* `DR04` comparative matrix and synthesis for UBEM;
* `DR05`–`DR07` European standards, national codes, and adapting our engine to them.

From those we have already implemented: orthogonal grid subdivision (1×1, 2×1, 2×2, 3×2, 4×2), an
unconditioned stair core at roughly 8 % of gross floor area with a floating temperature and a
`b_u` of 0.50–0.80, a double-loaded corridor spine for larger slabs, and a habitability check requiring
each dwelling to hold at least 2.50 m of exterior facade contact.

**Do not restate any of that.** If your answer to a question below is "as in `DR02`", say that and move on.

---

## Why we are asking

Those rules were designed on **archetype boxes** — regular rectangular plates. We have now run them
against **observed footprints** from a real European city, and the yield is poor enough to threaten the
step:

* Of 297 layout-ready buildings in our first real site, the generator emitted a dwelling layout for
  **18**.
* **256 of 297** were refused as **non-convex or holding a courtyard**.
* Of a frozen 12-building ladder sample, **1** emitted a dwelling layout; **8** were non-convex refusals
  and **3** fell back for being narrower than 8 m.
* Buildings that refuse still simulate, via a `one_zone_per_floor` fallback — so we get an energy number,
  but not a dwelling-partitioned one.

European historic urban fabric is full of perimeter blocks, courtyard buildings, L-shapes and irregular
infill. **A dwelling-subdivision rule that only accepts convex plates excludes exactly the stock we came
to model**, and it excludes it in a way that is correlated with construction epoch and typology — so what
survives is not a random sample.

We must either extend the rule or declare the exclusion honestly. We would rather do the first, and if the
literature says the second is the correct move, we need that stated plainly so we can pre-register it.

---

## What we need

### Item 1. Published methods for non-convex and courtyard plates

For each method you find: the geometric approach, the building types it was demonstrated on, whether an
implementation is available, the licence, and a direct artefact link in Section F.

We specifically want to know how the literature handles:

1. **Courtyard / perimeter-block buildings** — where the plate is an annulus, and dwellings face both the
   street and the courtyard.
2. **L-, U-, T- and cross-shaped plates**, including whether decomposition into convex parts is the
   accepted approach and how the seams between parts are treated thermally.
3. **Very deep plates** where an interior region has no facade contact at all, and what is done with it —
   circulation, service, unconditioned, or merged into a neighbouring dwelling.
4. Whether **medial-axis, straight-skeleton, or rectangular-decomposition** methods are used in this
   context, and whether any of them are reported as robust on real cadastral geometry rather than on
   synthetic plates.

### Item 2. The energy cost of the fallback — this is the item we care about most

Our fallback is **one thermal zone per floor** for a building we cannot partition. We need to know what
that costs, because it decides whether the fallback buildings can be reported alongside partitioned ones.

1. What is the published difference in **annual heating demand** and in **peak heating power** between
   one-zone-per-floor and one-zone-per-dwelling for the same building?
2. Does the difference depend on the number of dwellings per floor?
3. Does it depend on whether inter-dwelling partitions are modelled as adiabatic or as heat-transferring
   surfaces?
4. **Is the fallback biased, or merely noisier?** A noisy fallback can be pooled with a caveat; a biased
   one cannot be pooled at all. `DR03` covers zoning resolution generally — we need the specific
   floor-versus-dwelling comparison, with a number.

### Item 3. Selection bias, and what an honest denominator looks like

1. Is there published guidance on reporting UBEM results when a geometric rule **excludes a
   non-random subset** of the stock?
2. Do published UBEM studies report their **geometry refusal rate** at all? If the norm is to report only
   the buildings that ran, that is itself a finding and belongs in Section A.
3. What is the accepted way to state a stock-level result whose partitioned subsample is convexity-
   selected? Reweighting, a stated exclusion, two separate populations, or something else?

### Item 4. Vertex limits and real cadastral rings

One of our twelve ladder buildings failed EnergyPlus outright: its true exterior ring carries **173
vertices** against the input data dictionary's ~120-vertex limit for a detailed building surface. Is
footprint simplification before extrusion standard practice in UBEM, what tolerance is used, and what is
the reported energy cost of simplifying? We need a defensible tolerance, not a convenient one.

### Item 5. A numerical-robustness question we hit ourselves

Our layout routine rotates the plate about the **coordinate origin** while the partition audit compares
areas against an **absolute** tolerance of 1e-8 m². Layout success therefore depends on the coordinate
reference system: the same building passes in UTM 31N and fails in Lambert-93 at an area-error fraction of
5.09e-12. We have ruled that censuses run in the native CRS with no reprojection.

Is there published guidance — UBEM, GIS or computational-geometry — on **relative versus absolute area
tolerances** for planar partition audits on projected coordinates? A short, well-sourced answer is enough;
we mainly want to know whether our fix is the standard one.

---

## Constraints you must respect

* Our engine builds **one EnergyPlus IDF per building**, from the true footprint extruded to real storey
  count, shaded by real neighbours. Recommendations requiring a different simulation topology are a
  **design change** and must be labelled as one.
* The unconditioned circulation core and the 2.50 m facade-contact habitability rule are **already ruled**
  and are not open for redesign. If the literature contradicts them, say so in Section E as a caveat we
  should carry, not as a change to make.
* We run on a shared SLURM cluster with CPU nodes; EnergyPlus gains nothing from GPUs. Any method whose
  cost scales badly with building count must say so in Section D.

## What would change our mind

If Item 2 shows the one-zone-per-floor fallback is **unbiased** relative to dwelling partitioning for
annual demand and merely noisier for peak, our refusal rate stops being a threat to the step and becomes a
caveat. Say that in the first sentence of Section A if it is what the evidence shows. Equally, if Item 1
finds **no** robust published method for courtyard plates, say that first — an honest "the field has not
solved this" lets us pre-register the exclusion instead of pretending to a coverage we do not have.
