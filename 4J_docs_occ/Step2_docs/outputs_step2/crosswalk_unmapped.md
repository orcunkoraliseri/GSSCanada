# Step 2 — every source code that maps to nothing

### The single unmapped register `G2.1` reads. Assembled by the manager on 2026-08-16 from the two
### employee deliverables, which stay in place as the citable originals:
### `crosswalk_unmapped_activity.md` (work item 2.1) and `crosswalk_unmapped_location.md` (2.2).

**Totals across both crosswalks: 8 unmapped activity codes and 6 unmapped location codes, 14 in all.**
Every one is listed below with a reason. 🔴 **No code is silently dropped anywhere in Step 2** — a
code that maps to nothing yields a `null` in `harmonised.parquet` and appears here, and those two
facts are what make the null readable rather than mysterious.

---

# PART A — ACTIVITY (work item 2.1)

# Activity crosswalk -- unmapped codes, conflicts and vacuity counts

### Step 2 work item 2.1 / D-S2-11. Companion to `activity_target_list.csv`, `crosswalk_activity.csv` and `crosswalk_activity_secondary.csv`.

## UNMAPPED SOURCE CODES

| country | code | label | reason |
|---|---|---|---|
| es | 399 | Ayudas a adultos miembros del hogar no dependientes | ES code 399 ('Ayudas a adultos miembros del hogar no dependientes', help to NON-dependent adult household members) is a substantive category by Spain's own design; Italy's code 399 is a residual catch-all ('other specified/unspecified care or help to an adult family member'), which was adopted as target 399's resolved meaning. No agreed target denotes 'help to a non-dependent adult household member' as a distinct category. NOT FOUND IN DELIVERED CODEBOOK as an agreeing target. |
| es | 900 | Otros trayectos con un propósito, especificados o no | ES code 900 ('Otros trayectos con un proposito, especificados o no', other purposeful trips, unspecified) is Spain's own general residual travel category; Italy's code 900 denotes travel related to personal care specifically, which was adopted as target 900's resolved meaning. No agreed target in the shared vocabulary denotes a general 'other purposeful trips' residual. NOT FOUND IN DELIVERED CODEBOOK as an agreeing target. |
| it | 90 | SPOSTAMENTI SENZA FINALITÀ | Italy code 90 ('SPOSTAMENTI SENZA FINALITA', travel without a stated purpose) is a genuine 2-digit leaf activity code, not a group header (codebook_facts_italy.md finding F-IT-5). It cannot be represented as a 3-character target code without fabricating a third digit, and no agreed 3-digit target in the Spain-Italy shared vocabulary denotes 'travel without a stated purpose'. Listed under GROUP HEADER ROWS, NOT ACTIVITY CODES for visibility per the task specification's own naming, with this clarification that F-IT-5 documents it as a leaf code, not a header, so it is not mislabelled as one. |
| it | 997 | Frase che non descrive attivita' o utilizzo improprio delle caselle del diario | Italy code 997 ('Frase che non descrive attivita' o utilizzo improprio delle caselle del diario', a phrase that does not describe an activity, or improper use of the diary boxes) is a diary data-quality marker, not a real activity; Spain's own code 997 ('Otras actividades informales', other informal activities) denotes a genuine residual activity and was adopted as target 997's resolved meaning. Italy's 997 does not correspond to any activity in the target vocabulary. NOT FOUND IN DELIVERED CODEBOOK as an agreeing target. |
| uk | 9000 | Travel related to unspecified time use | UK's top-level 'travel related to unspecified time use' code denotes general/unspecified-purpose travel; no target in the Spain-Italy shared vocabulary denotes this (Spain's own equivalent code, 900, was resolved away in the Spain/Italy conflict at target 900 -- see crosswalk_unmapped_activity.md -- for the same underlying reason). NOT FOUND IN DELIVERED CODEBOOK as an agreeing target. |
| uk | 9940 | Punctuating activity | 'Punctuating activity' is a diary-formatting artefact, not a real activity (the same kind of defect as Italy's own code 997, itself unmapped -- see crosswalk_unmapped_activity.md). No activity in the target vocabulary corresponds to it. NOT FOUND IN DELIVERED CODEBOOK as an agreeing target. |
| uk | 9980 | Illegible activity | 'Illegible activity' denotes a diary entry that could not be read or transcribed, not a real recorded activity. No activity in the target vocabulary corresponds to it. NOT FOUND IN DELIVERED CODEBOOK as an agreeing target. |
| uk | 9999 | Queryable | 'Queryable' is a data-quality review flag, not a real recorded activity. No activity in the target vocabulary corresponds to it. NOT FOUND IN DELIVERED CODEBOOK as an agreeing target. |

## CONFLICTS BETWEEN THE SPANISH AND ITALIAN LISTS

Same 3-digit code, disagreeing meaning between the two delivered lists. Each is resolved explicitly below and the resolved row is carried into `activity_target_list.csv` with `evidence=conflict_resolved`.

### Code 111

* Spain (METH p. 66): "Trabajo principal y secundario"
* Italy (METADATI/Classificazioni/uso_tempo_Classificazione_Anno 2013_DiarioGiornaliero_var12.html): "Lavoro principale, formazione sul lavoro, altre attivita' svolte per lavoro"
* Resolution: IT's narrower 'main job only' meaning adopted (matches UK 1110 'Main job: Working time'); ES's own code 111 covers main AND secondary job time combined and is still mapped here because ES fields no separate secondary-job-time code; documented as a scope-broadening limitation.

### Code 121

* Spain (METH p. 66): "Pausa para la comida"
* Italy (METADATI/Classificazioni/uso_tempo_Classificazione_Anno 2013_DiarioGiornaliero_var12.html): "Secondo lavoro"
* Resolution: IT's 'Secondo lavoro' adopted (matches UK 1210 'Second job: Working time'). ES's own 121 'Pausa para la comida' (lunch break) is a different activity; it is not left unmapped -- see crosswalk_activity.csv, where ES-121 is mapped to target 139 (ambiguous=1), the same treatment given to the UK's own lunch-break code (1310), so the same real-world activity is not kept in one country's harmonised data and dropped in another's.

### Code 122

* Spain (METH p. 66): "Búsqueda de empleo"
* Italy (METADATI/Classificazioni/uso_tempo_Classificazione_Anno 2013_DiarioGiornaliero_var12.html): "Pausa caffè/brevi pause durante il secondo lavoro"
* Resolution: IT's meaning adopted, consistent with IT's internally coherent 121/122/123 second-job subgroup; ES's own 122 'Búsqueda de empleo' (job search) is redirected to target 139 in the crosswalk.

### Code 221

* Spain (METH p. 66): "Estudios durante el tiempo libre"
* Italy (METADATI/Classificazioni/uso_tempo_Classificazione_Anno 2013_DiarioGiornaliero_var12.html): "Studi e corsi espressivo-artistici"
* Resolution: IT's narrower, specific meaning adopted; ES's own 221 (general leisure-time study) is redirected to target 229 (IT's 'other/unspecified study and courses'), the closer semantic fit.

### Code 363

* Spain (METH p. 67): "Servicios personales"
* Italy (METADATI/Classificazioni/uso_tempo_Classificazione_Anno 2013_DiarioGiornaliero_var12.html): "Acquisto di servizi amministrativi per la casa e la famiglia"
* Resolution: IT's meaning adopted; ES's own 363 'Servicios personales' (personal services) is redirected to target 364 (IT's 'medical services, other paid personal services'), the closer semantic fit.

### Code 392

* Spain (METH p. 68): "Otras ayudas a adultos dependientes miembros del hogar"
* Italy (METADATI/Classificazioni/uso_tempo_Classificazione_Anno 2013_DiarioGiornaliero_var12.html): "Prestazioni sanitarie ad adulti disabili o malati della famiglia"
* Resolution: IT's narrower, specific meaning adopted; ES's own 392 ('other help to dependent adult household members') is broader and spans IT's 392/393/394 -- handled as an ambiguous row in the crosswalk.

### Code 399

* Spain (METH p. 68): "Ayudas a adultos miembros del hogar no dependientes"
* Italy (METADATI/Classificazioni/uso_tempo_Classificazione_Anno 2013_DiarioGiornaliero_var12.html): "Altre attivita' specificate e non di cura o aiuto ad adulti famiglia"
* Resolution: IT's residual-catchall meaning adopted; ES's own 399 (help to NON-dependent adult household members, a substantive category by ES's own design) has no IT equivalent and is UNMAPPED.

### Code 421

* Spain (METH p. 68): "Ayuda para la construcción y las reparaciones"
* Italy (METADATI/Classificazioni/uso_tempo_Classificazione_Anno 2013_DiarioGiornaliero_var12.html): "Cucinare come aiuto"
* Resolution: IT's meaning adopted, consistent with IT's internally coherent 421-429 'as help' subgroup; ES's own 421 (help with construction/repairs) is redirected to target 424, the closer semantic fit.

### Code 422

* Spain (METH p. 68): "Ayuda en el trabajo y en la agricultura"
* Italy (METADATI/Classificazioni/uso_tempo_Classificazione_Anno 2013_DiarioGiornaliero_var12.html): "Pulizia e riordino della casa come aiuto"
* Resolution: IT's meaning adopted; ES's own 422 (help in work and agriculture) is redirected to target 426 (IT's 'help in outside/extra-household work'), the closer semantic fit.

### Code 424

* Spain (METH p. 68): "Ayuda en el cuidado de niños de otro hogar"
* Italy (METADATI/Classificazioni/uso_tempo_Classificazione_Anno 2013_DiarioGiornaliero_var12.html): "Costruzioni e riparazioni come aiuto"
* Resolution: IT's meaning adopted; ES's own 424 (help caring for children of another household) is redirected to target 427 (IT's 'care of another household's children as help'), an exact semantic fit.

### Code 425

* Spain (METH p. 68): "Ayuda a adultos de otros hogares"
* Italy (METADATI/Classificazioni/uso_tempo_Classificazione_Anno 2013_DiarioGiornaliero_var12.html): "Acquisti di beni e servizi come aiuto"
* Resolution: IT's meaning adopted; ES's own 425 (help to adults of other households) is redirected to target 428 (IT's 'care of another household's adults as help'), the closer semantic fit.

### Code 812

* Spain (METH p. 70): "Lectura de libros"
* Italy (METADATI/Classificazioni/uso_tempo_Classificazione_Anno 2013_DiarioGiornaliero_var12.html): "Lettura di riviste periodiche"
* Resolution: IT's meaning adopted; ES's own 812 (reading books) is redirected to target 813 (IT's own 'Lettura di libri'/reading books), an exact semantic fit at a different code number.

### Code 822

* Spain (METH p. 70): "Ver DVD o vídeos"
* Italy (METADATI/Classificazioni/uso_tempo_Classificazione_Anno 2013_DiarioGiornaliero_var12.html): "Guardare programmi televisivi, film, video su PC o Internet"
* Resolution: IT's meaning adopted (a distinct online-viewing category ES's list does not carry); ES's own 822 (watching DVD or offline video) is redirected to target 821, whose IT label already spans television and recorded video (videocassette/DVD).

### Code 831

* Spain (METH p. 70): "Escuchar la radio"
* Italy (METADATI/Classificazioni/uso_tempo_Classificazione_Anno 2013_DiarioGiornaliero_var12.html): "Ascoltare musica"
* Resolution: IT's broader 'listening to music' meaning adopted; ES's own 831 (radio specifically) is still mapped here as the closest available target since no agreed target denotes 'radio' specifically; documented as an approximation, not an exact match.

### Code 832

* Spain (METH p. 70): "Escuchar grabaciones"
* Italy (METADATI/Classificazioni/uso_tempo_Classificazione_Anno 2013_DiarioGiornaliero_var12.html): "Ascoltare musica o radio su pc o Internet"
* Resolution: IT's internet/PC-specific meaning adopted; ES's own 832 ('recordings', i.e. offline recorded audio) is redirected to target 831, the closer semantic fit (both are passive, non-internet listening).

### Code 900

* Spain (METH p. 70): "Otros trayectos con un propósito, especificados o no"
* Italy (METADATI/Classificazioni/uso_tempo_Classificazione_Anno 2013_DiarioGiornaliero_var12.html): "Spostamenti per la cura della propria persona"
* Resolution: IT's specific meaning adopted, consistent with IT's own coherent by-purpose travel subgroup; ES's own 900 (a general 'other purposeful trips' residual) has no IT equivalent and is UNMAPPED.

### Code 997

* Spain (METH p. 71): "Otras actividades informales"
* Italy (METADATI/Classificazioni/uso_tempo_Classificazione_Anno 2013_DiarioGiornaliero_var12.html): "Frase che non descrive attivita' o utilizzo improprio delle caselle del diario"
* Resolution: ES's meaning adopted because it denotes a genuine residual activity category; IT's own 997 is a diary data-quality marker ('phrase that does not describe an activity or improper use of diary boxes'), not a real activity, and is UNMAPPED rather than forced into the target vocabulary.

## GROUP HEADER ROWS, NOT ACTIVITY CODES

| country | code | label | note |
|---|---|---|---|
| it | 90 | SPOSTAMENTI SENZA FINALITA | Named explicitly in the task specification as the illustrative example of a 2-digit row to set aside. Clarification: `codebook_facts_italy.md` finding F-IT-5 documents code 90 as a genuine 2-digit LEAF activity code ("a real, usable code, not a header"), not a group header in Italy's own classification. It is listed under this heading, as the task specification names it, because it cannot be represented as a 3-character target code without fabricating a third digit and no agreed target denotes its meaning ('travel without a stated purpose'); it is not a header, and is not mischaracterised as one beyond this heading's own label. See UNMAPPED SOURCE CODES above for the formal disposition. |

## SINGLE-SOURCE TARGET CODES

Count: **55** of 158 target codes (34.8 %) rest on a single delivery.

| target_code | target_label_en | source |
|---|---|---|
| 112 | Coffee break during main job | it |
| 113 | Travel during main job | it |
| 123 | Travel during second job | it |
| 129 | Other work-related activities, specified or not | es |
| 132 | Work-related activities outside working hours | it |
| 139 | Other work-related activities and job seeking | it |
| 200 | Unspecified study | es |
| 219 | Other activities related to school or university | it |
| 222 | Language study and courses | it |
| 223 | Computer use study and courses | it |
| 224 | Technical-operational study and courses | it |
| 229 | Other study and courses, specified or not | it |
| 300 | Unspecified household and family activities | es |
| 319 | Other food management, specified or not | it |
| 364 | Medical services and other paid personal services | it |
| 365 | Veterinary services for pets or farm animals | it |
| 372 | Household management using the internet | it |
| 393 | Company/accompanying an adult family member | it |
| 394 | Helping an adult family member with other activities | it |
| 426 | Help with work or agriculture to another household | it |
| 427 | Care of another household's children as help | it |
| 428 | Care of another household's adults as help | it |
| 515 | Children's socialising activities, unspecified | it |
| 516 | Talking with non-cohabiting people outside the home | it |
| 517 | Other social life activities carried out outside the home | it |
| 617 | Dance (as sport) | it |
| 714 | Listening to a story (respondents up to 17) | it |
| 734 | Playing with animals | it |
| 735 | Children's creative and artistic play (respondents up to 17) | it |
| 736 | Children's active play (respondents up to 17) | it |
| 813 | Reading books | it |
| 814 | Reading comics/magazines for children (respondents up to 17) | it |
| 829 | Watching television, DVD or videos, specified or not | es |
| 839 | Listening to radio or recordings, specified or not | es |
| 920 | Travel for study | es |
| 921 | Travel for school or university | it |
| 922 | Travel for other study or courses | it |
| 930 | Travel for other household and family activities | es |
| 931 | Travel for household upkeep | it |
| 940 | Travel for volunteer work and meetings | es |
| 941 | Travel for volunteer work | it |
| 942 | Travel for informal help to other households | it |
| 943 | Travel for social or religious participation | it |
| 950 | Travel for social life activities | es |
| 951 | Travel for social life | it |
| 971 | Travel for change of locality | it |
| 972 | Travel for leisure trips | it |
| 981 | Children's travel with both parents (respondents up to 17) | it |
| 982 | Children's travel with father, incl. non-resident (respondents up to 17) | it |
| 983 | Children's travel with mother, incl. non-resident (respondents up to 17) | it |
| 989 | Children's travel with other people (respondents up to 17) | it |
| 990 | Travel for change of locality | es |
| 996 | Activities related to other surveys | es |
| 998 | Unspecified free time | es |
| 999 | Other unspecified time use | es |

## AMBIGUOUS ROWS AND THEIR RULES

Count: **16** of 531 crosswalk rows (3.01 %) are flagged ambiguous=1, each with a written rule below.

| country | source_code | source_label | target_code | rule |
|---|---|---|---|---|
| es | 121 | Pausa para la comida | 139 | No target denotes 'meal/lunch break during work' specifically. Matching the treatment given to the UK's own code 1310 ('Activities related to employment: Lunch break'), which denotes the same concept and is mapped to the same target for the same reason, ES-121 is mapped to target 139 ('other work-related activities and job seeking'), the closest available catch-all under employment-related activities, rather than left unmapped -- so the same real-world activity is not kept in the UK's harmonised data and dropped from Spain's. |
| es | 392 | Otras ayudas a adultos dependientes miembros del hogar | 393 | ES 'other help to dependent adult household members' spans Italy's separate 392 (medical services), 393 (company/accompanying) and 394 (general help with tasks); mapped to 393 (company/accompanying) as the closest single dominant component. |
| uk | 0 | Unspecified personal care | 039 | UK's top-level 'unspecified personal care' catch-all spans targets 011 (sleep), 012 (sick in bed), 021 (eating/drinking), 031 (washing/dressing) and 039 (other, specified or not); mapped to 039 as the residual choice, per the group catch-all rule. |
| uk | 111 | Sleep: In bed not asleep | 011 | UK denotes lying in bed awake, not literally sleeping; could plausibly fall under target 011 (sleep, the sleep episode broadly construed) or 531 (passive leisure/resting); mapped to 011 to keep it within the same sleep episode block, consistent with the UK's own grouping of this code under its top-level 'Sleep' category (group1=1). |
| uk | 1000 | Unspecified employment | 129 | UK's top-level 'unspecified employment' catch-all spans main job (111), second job (121), coffee breaks (112/122), travel during work (113/123) and other work-related activities (129/132/139); mapped to 129 ('other work-related activities, specified or not'), the closest general catch-all for the whole employment domain, per the group catch-all rule. |
| uk | 1310 | Activities related to employment: Lunch break | 139 | No target denotes 'lunch break' specifically; mapped to target 139 ('other work-related activities and job seeking'), the closest available catch-all under employment-related activities, matching the treatment given to Spain's own code 121 ('Pausa para la comida'), which denotes the same concept and is mapped to the same target for the same reason (see crosswalk_activity.csv, country=es, source_code=121). |
| uk | 2210 | Free time study | 229 | UK's single undifferentiated 'Free time study' code could correspond to any of the target vocabulary's leisure-study subcategories (221 expressive-artistic, 222 language, 223 computer, 224 technical) or the residual 229; mapped to 229 ('other study and courses, specified or not') as the least assumption-laden choice, since the UK label gives no indication of subject. |
| uk | 3100 | Unspecified food management | 319 | UK's 'unspecified food management' spans targets 311 (food preparation/preservation), 312 (dish washing) and 319 (other, specified or not); mapped to 319, the group's own residual code, per the group catch-all rule. |
| uk | 3910 | Unspecified help to a non-dependent eg injured adult household member | 399 | 'Unspecified help' does not indicate whether the assistance was physical care, company/accompanying, or other help with tasks (targets 391/393/394); mapped to target 399 ('other care or help to an adult family member, not elsewhere classified') as the residual choice for an unspecified kind of help, per the group catch-all rule. |
| uk | 3920 | Unspecified help to a dependent adult household member | 399 | 'Unspecified help' does not indicate whether the assistance was physical care, company/accompanying, or other help with tasks (targets 391/393/394); mapped to target 399 ('other care or help to an adult family member, not elsewhere classified') as the residual choice for an unspecified kind of help, per the group catch-all rule. |
| uk | 4000 | Unspecified volunteer work and meetings | 439 | UK's top-level 'unspecified volunteer work and meetings' catch-all spans targets 411 (volunteer work), 431 (meetings), 432 (religious practice) and 439 (other, specified or not); mapped to 439 as the residual choice, per the group catch-all rule. |
| uk | 5000 | Unspecified social life and entertainment | 519 | UK's top-level 'unspecified social life and entertainment' catch-all spans both the target vocabulary's social-life subgroup (511-519) and entertainment/culture subgroup (521-529); mapped to 519 ('other social life, specified or not') as the nominal choice; could equally be 529, per the group catch-all rule. |
| uk | 6000 | Unspecified sports and outdoor activities | 619 | UK's top-level 'unspecified sports and outdoor activities' catch-all spans targets 611-619 (physical exercise), 621 (productive exercise) and 631 (other sports-related activities); mapped to 619 as the nominal choice (physical exercise being the largest sub-group), per the group catch-all rule. |
| uk | 7000 | Unspecified hobbies games and computing | 719 | UK's top-level 'unspecified hobbies, games and computing' catch-all spans targets 711-719 (arts/hobbies), 721-729 (computing) and 731-739 (games); mapped to 719 as the nominal choice (arts/hobbies being listed first in both source lists), per the group catch-all rule. |
| uk | 8000 | Unspecified mass media | 829 | UK's top-level 'unspecified mass media' catch-all spans the target vocabulary's reading (811-819), TV/video (821-829) and radio/music (831-839) subgroups; mapped to 829 as the nominal choice (TV/video being the most time-dominant mass-media activity), per the group catch-all rule; could equally be 819 or 839. |
| uk | 9890 | Other specified travel | 999 | UK's residual 'other specified travel' code does not indicate purpose and could fall under any travel target (910-989); no equivalently broad 'other travel, unspecified purpose' target exists (the closest, Spain's own code 900, was resolved away in the Spain/Italy conflict at target 900 and is unmapped); mapped to target 999 ('other unspecified time use'), the broadest residual available, per the group catch-all rule. |

### THE 14 UK ROWS FLAGGED AMBIGUOUS (COLUMN NOT VACUOUS)

**14 of the 277 UK rows are flagged ambiguous=1** (listed in the table above). The column is not vacuous for the UK. Most of the UK's 277 codes are simple many-to-one granularity mappings into the shared 3-digit target vocabulary (normal, not ambiguous per the task's own definition), but a genuine minority -- chiefly the UK's own top-level 'unspecified X' catch-all codes (e.g. `0`, `1000`, `4000`, `5000`, `6000`, `7000`, `8000`) and its finer dependent/non-dependent adult-help split (`3910`, `3920`) -- each spanned more than one candidate target code and required an explicit picked-by-rule choice, exactly the case the column exists to flag.

## COUNTS

Printed before any verdict, per V2.b.

| country | source codes seen | mapped | unmapped | ambiguous |
|---|---|---|---|---|
| es | 116 | 114 | 2 | 2 |
| it | 146 | 144 | 2 | 0 |
| uk | 277 | 273 | 4 | 14 |

| **all** | **539** | **531** | **8** | **16** |

---

# PART B — LOCATION (work item 2.2)

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

---

# PART E — STRATA (Task B, D-S2-18/D-S2-19, additive round 2026-08-17)

### Companion to `crosswalk_strata.csv`. Not a new work item -- appended to the single unmapped
### register per the same rule PART A-D follow: every source value that maps to nothing is listed here.

## Italy `tipfa2m` (household-type stratum) -- CLS-var16 enumeration gap codes

🔴 **Codes `12, 13, 17, 18, 26, 27, 31, 32` are not enumerated anywhere in CLS-var16**
(codebook_facts_italy_strata.md, F-IT-16; strata_proposal.md "WHAT I DID NOT VERIFY"). They are
**never folded into `other_complex`** -- that is where an unrecognised code looks like it belongs,
and D-S2-19 section 4.1 forbids it explicitly. `crosswalk_strata.csv` carries no row for any of the
eight. Per D-S2-19: **if any of them is observed in the raw file, the Step 2 harmonisation run FAILs**
rather than emitting a table with a silently-dropped or silently-folded household-type value.

| country | code | label | reason | observed frequency (this round) |
|---|---|---|---|---|
| it | 12 | NOT FOUND (gap in CLS-var16) | code number falls inside `tipfa2m`'s declared 1-40 range but is not assigned a label anywhere in CLS-var16's own enumeration | 0 |
| it | 13 | NOT FOUND (gap in CLS-var16) | same | 0 |
| it | 17 | NOT FOUND (gap in CLS-var16) | same | 0 |
| it | 18 | NOT FOUND (gap in CLS-var16) | same | 0 |
| it | 26 | NOT FOUND (gap in CLS-var16) | same | 0 |
| it | 27 | NOT FOUND (gap in CLS-var16) | same | 0 |
| it | 31 | NOT FOUND (gap in CLS-var16) | same | 0 |
| it | 32 | NOT FOUND (gap in CLS-var16) | same | 0 |

**Measured 2026-08-17** from the Step 1 Italy re-run (job 1254927, `tools/4thJ_read_italy.py`),
`italy_reader_facts.json`'s `tipfa2m_gap_codes_observed_frequency`: all eight gap codes occur **0**
times in `uso_tempo_Microdati_Anno_2013_Individui.txt` (44,866 person rows, 32 distinct non-blank
`tipfa2m` codes observed, exactly the CLS-var16-documented set). The Step 2 harmonisation run
(`tools/4thJ_harmonise_step2.py`) therefore did not FAIL on this condition. This does not resolve
whether the eight gaps are unused code points or undocumented categories (strata_proposal.md,
"WHAT I DID NOT VERIFY") -- it only establishes that none of them appears in this delivery.
