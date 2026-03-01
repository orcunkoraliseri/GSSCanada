# C-VAE Variable List — Comprehensive Extraction

Documenting all variables in the C-VAE pipeline, tracing them from their root origins (GSS Main vs. Episode files) through renaming, harmonization, and final model feature lists.

---

## 1. C-VAE Feature Variables & Their Root Source

This table lists every variable defined in [eSim_dynamicML_mHead.py](file:///Users/orcunkoraliseri/Desktop/Postdoc/eSim/eSim_occ_utils/25CEN22GSS_classification/eSim_dynamicML_mHead.py#L102-L122) as either a **Demographic Feature**, **Building Feature**, or **Continuous Column**.

| C-VAE Name | Role | Encoding | Root Origin | GSS Raw Name | Census Raw Name |
|---|---|---|---|---|---|
| **`YEAR`** | Demographic | One-hot | *Synthetic* | — | — |
| **`AGEGRP`** | Demographic | One-hot | **GSS Main** | `AGEGR10` | `AGEGRP` (2011-21) / `AgeGrp` (2006) |
| **`SEX`** | Demographic | One-hot | **GSS Main** | `GENDER2` | `SEX` (06-16) / `GENDER` (2021) |
| **`MARSTH`** | Demographic | One-hot | **GSS Main** | `MARSTAT` | `MarStH` (16,21) / `MARSTH` (11) / `MARST` (06) |
| **`HHSIZE`** | Demographic | One-hot | **GSS Main** | `HSDSIZEC` | Computed from `HH_ID` |
| **`EFSIZE`** | Demographic | One-hot | *Derived* | — | Computed from `EF_ID` |
| **`CFSIZE`** | Demographic | One-hot | *Derived* | — | Computed from `CF_ID` |
| **`KOL`** | Demographic | One-hot | **GSS Main** | `LAN_01` | `KOL` |
| **`ATTSCH`** | Demographic | One-hot | **GSS Main** | `EDC_10` | `ATTSCH` (11-21) / `AttSch` (06) |
| **`CIP`** | Demographic | One-hot | *Census-only* | — | `CIP` (06-11) / `CIP2011` (16) / `CIP2021` (21) |
| **`NOCS`** | Demographic | One-hot | **GSS Main** | `NOCLBR_Y` | `NOCS` (06-16) / `NOC21` (21) |
| **`GENSTAT`** | Demographic | One-hot | *Census-only* | — | `GENSTAT` |
| **`POWST`** | Demographic | One-hot | **GSS Main** | `CTW_140I` | `POWST` |
| **`CITIZEN`** | Demographic | One-hot | *Census-only* | — | `CITIZEN` |
| **`LFTAG`** | Demographic | One-hot | **GSS Main** | `ACT7DAYC` | `LFTAG` (11,16) / `LFACT` (06,21) |
| **`CF_RP`** | Demographic | One-hot | *Census-only* | — | `CF_RP` |
| **`COW`** | Demographic | One-hot | **GSS Main** | `WET_120` | `COW` |
| **`CMA`** | Demographic | One-hot | **GSS Main** | `LUC_RST` | `CMA` |
| **`CFSTAT`** | Demographic | One-hot | *Census-only* | — | `CFSTAT` |
| **`PR`** | Demographic | One-hot | **GSS Main** | `PRV` | `PR` (11-21) / `REGION` (06) |
| **`HRSWRK`** | Demographic | One-hot | **GSS Main** | `WHWD140G` | `HRSWRK` |
| **`MODE`** | Demographic | One-hot | **GSS Main** | `ATT_150C` | `MODE` |
| **`EMPIN`** | Demographic | Continuous | *Census-only* | — | `EMPIN` |
| **`TOTINC`** | Demographic | Continuous | **GSS Main** | `INC_C` | `TOTINC` |
| **`INCTAX`** | Demographic | Continuous | *Census-only* | — | `INCTAX` |
| **`BUILTH`** | Building | One-hot | *Census-only* | — | `BUILT` (all years, renamed) |
| **`CONDO`** | Building | One-hot | *Census-only* | — | `CONDO` |
| **`BEDRM`** | Building | One-hot | *Census-only* | — | `BEDRM` (11-21) / `BROOMH` (06, renamed) |
| **`ROOM`** | Building | One-hot | *Census-only* | — | `ROOM` |
| **`DTYPE`** | Building | One-hot | *Census-only* | — | `DTYPE` |
| **`REPAIR`** | Building | One-hot | *Census-only* | — | `REPAIR` |
| **`VALUE`** | Building | Continuous | *Census-only* | — | `VALUE` |

---

## 2. GSS Main File Columns (`COLS_MAIN`)

Extracted from the GSS 2022 Main SAS file ([eSim_dynamicML_mHead_alignment.py:26-48](file:///Users/orcunkoraliseri/Desktop/Postdoc/eSim/eSim_occ_utils/25CEN22GSS_classification/eSim_dynamicML_mHead_alignment.py#L26-L48)):

| GSS Raw Name | Renamed To | Description | C-VAE Field? |
|---|---|---|---|
| `PUMFID` | `occID` | Unique key | No (key) |
| `PRV` | `PR` | Province | ✅ Yes |
| `REGION` | *(kept)* | Region helper | No |
| `DDAY` | *(kept)* | Day of week | No |
| `HSDSIZEC` | `HHSIZE` | HH Size | ✅ Yes |
| `AGEGR10` | `AGEGRP` | Age Group | ✅ Yes |
| `GENDER2` | `SEX` | Sex | ✅ Yes |
| `MARSTAT` | `MARSTH` | Marital status | ✅ Yes |
| `LAN_01` | `KOL` | Official lang. | ✅ Yes |
| `EDC_10` | `ATTSCH` | School attendance | ✅ Yes |
| `ED_05` | `HDGREE` | Degree | No |
| `NOCLBR_Y` | `NOCS` | Occup. group | ✅ Yes |
| `NAIC22CY` | `NAICS` | Industry code | No |
| `ACT7DAYC` | `LFTAG` | Labor activity | ✅ Yes |
| `WET_120` | `COW` | Class of worker | ✅ Yes |
| `WHWD140G` | `HRSWRK` | Hours/week | ✅ Yes |
| `ATT_150C` | `MODE` | Commuting mode | ✅ Yes |
| `CTW_140I` | `POWST` | Work status | ✅ Yes |
| `INC_C` | `TOTINC` | Total income | ✅ Yes |
| `LUC_RST` | `CMA` | Urban vs Rural | ✅ Yes |
| `PHSDFLG`, `CXRFLAG`, `PARNUM` | — | Personal helpers | No |

---

## 3. GSS Episode File Columns

These columns come from the time-use diary file (`out22EP_ACT_PRE_coPRE.csv`) and are used downsteam in profile expansion and household aggregation.

| Name | Role | Description |
|---|---|---|
| `occID` | Key | Links to Main record |
| `EPINO` | Seq | Episode index |
| `start` / `end` | Time | Start/End (HHMM) |
| `occACT` | Activity | Activity code |
| `occPRE` | Presence | Home/Away (1=Home) |
| `Spouse`, `Children`, `Friends` | Social | Co-presence flags |
| `otherHHs`, `Others` | Social | Presence of others |

---

## 4. Harmonization Logic (10 Features)

The [alignment pipeline](file:///Users/orcunkoraliseri/Desktop/Postdoc/eSim/eSim_occ_utils/25CEN22GSS_classification/eSim_dynamicML_mHead_alignment.py) ensures both sources use the same categories:

1. **`harmonize_agegrp`**: Census (5-yr) → GSS (10-yr: 15-24, 25-34... 75+)
2. **`harmonize_hhsize`**: Capped at 5 (GSS: 5 or more)
3. **`harmonize_hrswrk`**: 1=Under 30, 2=30-59, 3=60+, 99=NA
4. **`harmonize_marsth`**: 1=Never, 2=Married/CL, 3=Sep/Div/Wid
5. **`harmonize_sex`**: GSS swapped (GSS 1→2, 2→1) for Census 1=Female, 2=Male
6. **`harmonize_kol`**: All kept [1, 2, 3, 4]
7. **`harmonize_nocs`**: GSS 1-10, 99=NA
8. **`harmonize_pr`**: 1=East, 2=QC, 3=ON, 4=Prairies, 5=BC, 6=North
9. **`harmonize_cow`**: 1=Employee, 2=Self-emp, 3=Unpaid
10. **`harmonize_mode`**: 1=Bike, 2=Driv, 3=Walk, 4=Transit, 5=Other, 9=NA

---

## 5. Census Preprocessing History

Processed via [eSim_datapreprocessing.py](file:///Users/orcunkoraliseri/Desktop/Postdoc/eSim/eSim_occ_utils/25CEN22GSS_classification/eSim_datapreprocessing.py):

| Action | Function | Logic |
|---|---|---|
| **Selection** | `read_select_and_save` | 32 specific census IDs/Demographics |
| **Filtering** | `filter_and_save` | Remove bad codes (88, 99, skip codes) |
| **Computing** | `feature_engineering` | Derive `HHSIZE`, `EFSIZE`, `CFSIZE` from group counts |
| **Formatting** | `get_dummies` | Convert categorical into One-Hot heads for C-VAE |
