# Location crosswalk — unmapped codes and judgement calls

### 4J HETUS LLM pipeline. Step 2, work item 2.2 companion to `crosswalk_location.csv`.

Per D-S2-3, every national location code is mapped explicitly, by its label, to one of the four
target classes (`at_home`, `other_place`, `private_transport`, `public_transport`), or it appears
here as unmapped, with a reason. No code was tested by numeric range.

---

## UNMAPPED LOCATION CODES

| country | code | label | reason |
|---|---|---|---|
| es | 00 | Lugar o medio de transporte no especificado | The label itself conflates two different things the four target classes separate: "place" and "means of transport", explicitly "not specified" which of the two. Nothing in METH pp. 124-126 or in `codebook_facts_spain.md` resolves which of the four classes this code belongs to. Not guessed. |
| uk | 90 | Unspecified transport mode | Unlike codes 30 ("Unspecified **private** transport mode") and 40 ("Unspecified **public** transport mode"), code 90's label does not say which kind of transport. `group1=9` is its own residual group, distinct from the private (`group1=3`) and public (`group1=4`) blocks, giving no basis to assign it to either. Not guessed. |
| uk | 99 | Illegible location or transport mode | The label states the record itself is illegible — it is not a real location or mode, and cannot be assigned to any of the four classes without inventing one. |
| it | 97 | Frase che non descrive luogo o mezzo | The label states the response text does not describe a place or a means of transport at all ("phrase that does not describe a place or means"); it is not a real location/mode value. |
| it | 98 | Mezzo di trasporto non specificato | Same defect as the UK's code 90: the label says "means of transport not specified" with no qualifier distinguishing private from public, and CLS-var14 gives no further basis to choose. Not guessed. |
| it | 99 | Luogo/mezzo non specificato | The label itself conflates "place" and "means" ("Luogo/mezzo"), explicitly unspecified as to which — the same defect as Spain's code 00. Not guessed. |

**Unexplained residue: 0.** Every one of these six codes is accounted for here, with a reason tied
to its own label; none is silently dropped (G2.1).

---

## LOCATION CODES WHOSE CLASS NEEDED A JUDGEMENT

| country | code | label | class chosen | rule |
|---|---|---|---|---|
| es | 10 | Lugar no especificado | other_place | Code means "place not specified"; grouped among the stationary place codes 10-14 (METH pp. 124-126), not the transport codes. Classified as `other_place` because it denotes an unspecified place, not the home code (11) and not a transport mode. |
| es | 30 | Medio de transporte no especificado | private_transport | Code means "transport mode not specified". Finding F-ES-3 (`codebook_facts_spain.md`) and METH p. 126 place code 30 structurally inside the private-transport block 30-39, distinct from the separately listed public-transport code 41. Classified as `private_transport` on that structural placement in the codebook, not on the label's wording alone. |
| uk | 0 | Unspecified location | other_place | Code means "unspecified location" with no further qualifier. Classified as `other_place` because it is not the home code (11) and nothing in the codebook gives a basis to place it in either transport class. |
| uk | 10 | Unspecified location (not travelling) | other_place | The "(not travelling)" qualifier rules out both transport classes. Classified as `other_place` because it is not the home code (11). |
| it | 12 | Casa propria, spazi aperti | at_home | 🔴 **The D-S2-4 asymmetry.** Per D-S2-4, Spain's code 11 merges dwelling plus yard and garden into a single "Home" code (METH p. 124). Italy splits this into an indoor code (11, Casa propria) and an outdoor-spaces code (12, Casa propria, spazi aperti). Both Italian codes are mapped to `at_home` so the four-class scheme lines up with Spain's single merged code — this reproduces, rather than removes, D-S2-4's merge. This is also recorded in `outputs_step2/copresence_availability.md` and it is the reason `outputs_step2/outdoor_at_home.csv` matters more for Italy than for Spain: Italy's location field alone already distinguishes indoor (11) from outdoor-at-home (12), while Spain's single code 11 relies entirely on the `OUTDOOR_AT_HOME` activity exclusion list to make the same distinction. |
| it | 49 | Luogo non specificato | other_place | Code means "place not specified". Classified as `other_place` because it is not the home code (11/12) and is grouped among the place codes (11-49), not the transport codes (50-63). |
| it | 55 | Gommone, barca | private_transport | Small private recreational craft (dinghy/motorboat). Classified as `private_transport` by its placement in the private-means block 50-56 ("Altri mezzi privati"), structurally distinct from the public-conveyance block 57-63, which separately lists "Nave" (ship, code 62) as public transport. |

---

## COUNTS

### Per country — source codes seen, mapped, unmapped

| country | source codes seen | mapped (in `crosswalk_location.csv`) | unmapped (above) |
|---|---|---|---|
| es | 20 | 19 | 1 |
| uk | 35 | 33 | 2 |
| it | 53 | 50 | 3 |

Each row reconciles exactly: seen = mapped + unmapped, for all three countries (self-check 1).

### Per country × target_class — how many source codes map to each class

| country | at_home | other_place | private_transport | public_transport | total mapped |
|---|---|---|---|---|---|
| es | 1 | 11 | 6 | 1 | 19 |
| uk | 1 | 12 | 10 | 10 | 33 |
| it | 2 | 34 | 7 | 7 | 50 |

**No (country × class) cell is zero.** All twelve cells above are non-empty, so there is nothing to
flag loudly here for G2.11 at the source-crosswalk level. This is a necessary but not sufficient
condition for G2.11 to pass once `harmonised.parquet` is built (episode weights, not source-code
counts, are what the actual gate checks), but a zero cell at this stage would have meant G2.11 could
not possibly pass downstream, and none of the twelve cells are zero.
