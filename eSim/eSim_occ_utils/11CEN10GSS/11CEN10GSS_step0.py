import os
import re
import pandas as pd
from pathlib import Path
from typing import Optional

# =============================================================================
# GSS 2010 Activity Code → Harmonized Category (1-14)
# =============================================================================
# GSS 2010 ACTCODE uses SPSS implied-decimal format: stored integer / 10 = real code.
# e.g., stored 450 = 45.0, stored 11 = 1.1, stored 911 = 91.1.
# Mapping derived empirically from PRE fraction, mean duration, and time-of-day
# distributions. Verify against the GSS 2010 Activity Classification codebook
# (C24_Episode File_SPSS_withno_bootstrap.SPS) for any edge cases.
ACT_MAP_10 = {
    11:  1,    # Paid work at workplace (PRE=0.14, 201 min, midday)
    50:  4,    # Shopping/services (PRE=0.02, away)
    90:  13,   # Travel (PRE=0.00, 25 min)
    101: 6,    # Eating at home (PRE=0.98, 31 min, midday)
    110: 10,   # Passive leisure at home (PRE=0.98, 23 min)
    120: 2,    # Household work (PRE=0.99, 77 min, noon)
    140: 7,    # Personal care
    172: 7,    # Personal care, grooming (PRE=0.72)
    200: 2,    # Household work
    291: 2,    # Household work, other
    301: 3,    # Caregiving (PRE=0.05, mostly away)
    302: 3,    # Caregiving, other
    390: 13,   # Travel (PRE=0.00, 17 min)
    400: 7,    # Personal care / hygiene (PRE=0.96, 27 min, 20% nighttime)
    430: 6,    # Eating / meals (PRE=1.00, 33 min)
    440: 1,    # Paid work, away from home (PRE=0.00)
    450: 5,    # Sleep (PRE=0.97, 249 min, 82% nighttime)
    470: 2,    # Household work at home (PRE=0.91, afternoon)
    491: 13,   # Travel / work transit (PRE=0.00)
    751: 12,   # Volunteer activity
    752: 12,   # Volunteer activity
    792: 12,   # Civic / volunteer
    821: 9,    # Socializing away from home (PRE=0.17)
    841: 9,    # Socializing at home
    865: 9,    # Socializing, evening (PRE=0.98)
    891: 9,    # Social entertainment
    911: 10,   # Passive leisure / TV (PRE=0.98, 110 min, evening)
    931: 7,    # Personal care, evening / bathing (PRE=0.97, 73 min)
    940: 10,   # Passive leisure
    951: 11,   # Active leisure
}

def _map_actcode(code_raw):
    """Maps raw GSS 2010 ACTCODE integer to harmonized 1-14 category."""
    try:
        code = int(float(code_raw))
    except (ValueError, TypeError):
        return 14
    if code <= 0:
        return 0
    if code in ACT_MAP_10:
        return ACT_MAP_10[code]
    # Range-based fallback by leading digit of stored code
    first = int(str(code)[0])
    if first == 1:   return 7    # 1xx: Personal care
    elif first == 2: return 2    # 2xx: Household work
    elif first == 3: return 3    # 3xx: Caregiving
    elif first == 4: return 2    # 4xx: Household/personal (450=sleep handled above)
    elif first == 5: return 8    # 5xx: Education
    elif first == 6: return 4    # 6xx: Shopping/services
    elif first == 7: return 12   # 7xx: Volunteer/civic
    elif first == 8: return 9    # 8xx: Socializing
    elif first == 9: return 10   # 9xx: Leisure
    else:            return 13   # 10xx+: Travel


def _min_to_hhmm(minutes_raw):
    """Converts decimal minutes from midnight to HHMM integer (e.g. 540 → 900)."""
    try:
        m = int(float(minutes_raw)) % 1440
        return (m // 60) * 100 + (m % 60)
    except (ValueError, TypeError):
        return 0


def parse_sps_colspec(sps_filepath):
    colspec = []
    var_names = []
    var_pattern = re.compile(r'^/?\s*([A-Za-z_][A-Za-z0-9_]*)\s+(\d+)\s*-\s*(\d+)')
    with open(sps_filepath, 'r', encoding='utf-8', errors='replace') as f:
        in_data_list = False
        for line in f:
            if 'DATA LIST' in line.upper():
                in_data_list = True
                continue
            if in_data_list and line.strip() == '.':
                break
            if in_data_list:
                match = var_pattern.match(line)
                if match:
                    var_name = match.group(1)
                    start = int(match.group(2)) - 1
                    end = int(match.group(3))
                    var_names.append(var_name)
                    colspec.append((start, end))
    return var_names, colspec

def main(project_root: Optional[Path] = None):
    base_dir = Path(project_root) if project_root is not None else Path(__file__).resolve().parents[2]
    episode_dir = base_dir / "0_Occupancy/DataSources_GSS/Episode_files/GSS_2010_episode"
    
    dat_path = episode_dir / "C24EPISODE_withno_bootstrap.DAT"
    sps_path = episode_dir / "C24_Episode File_SPSS_withno_bootstrap.SPS"
    out_path = episode_dir / "out10EP_ACT_PRE_coPRE.csv"
    
    print(f"Parsing SPS: {sps_path}")
    var_names, colspec = parse_sps_colspec(sps_path)
    
    # Columns we actually need to read to save memory (or we can read all and filter later)
    # The required ones based on step 0:
    # RECID -> occID, EPINO, DDAY, ACTCODE, STARTMIN, ENDMIN, DURATION, PLACE, ALONE, SPOUSE, CHILDHSD, MEMBHSD
    need_cols = ['RECID', 'EPINO', 'DDAY', 'ACTCODE', 'STARTMIN', 'ENDMIN', 'DURATION', 'PLACE', 'ALONE', 'SPOUSE', 'CHILDHSD', 'MEMBHSD']
    
    extract_spec = []
    extract_names = []
    for col in need_cols:
        if col in var_names:
            idx = var_names.index(col)
            extract_spec.append(colspec[idx])
            extract_names.append(col)
            
    print(f"Reading DAT file: {dat_path}")
    df = pd.read_fwf(dat_path, colspecs=extract_spec, names=extract_names, dtype=str)
    
    # Rename RECID -> occID
    df = df.rename(columns={'RECID': 'occID'})
    
    # Clean up fields
    def clean_act(x):
        try:
            return int(float(x))
        except:
            return 999
    
    df['ACTCODE'] = df['ACTCODE'].apply(clean_act)
    
    df['PLACE'] = pd.to_numeric(df['PLACE'], errors='coerce').fillna(99).astype(int)
    # 1 = "Respondent's home". (From SPS code 01)
    df['PRE'] = (df['PLACE'] == 1).astype(int)
    
    # coPRE logic: MEMBHSD == 1 or SPOUSE == 1 or CHILDHSD == 1
    # First, cast to int safely
    for c in ['MEMBHSD', 'SPOUSE', 'CHILDHSD']:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(99).astype(int)
        
    df['coPRE'] = ((df['MEMBHSD'] == 1) | (df['SPOUSE'] == 1) | (df['CHILDHSD'] == 1)).astype(int)

    # --- Add harmonized columns expected by HH_aggregation ---

    # occACT: map raw 3-digit ACTCODE to harmonized 1-14 category
    df['occACT'] = df['ACTCODE'].apply(_map_actcode)

    # start / end: convert decimal minutes to HHMM format (e.g. 540 min → 900 = 9:00 AM)
    # HH_aggregation prefers 'start'/'end' (HHMM) over 'STARTMIN'/'ENDMIN' (raw minutes)
    df['start'] = df['STARTMIN'].apply(_min_to_hhmm)
    df['end']   = df['ENDMIN'].apply(_min_to_hhmm)

    # occPRE: alias for PRE, preferred column name in HH_aggregation
    df['occPRE'] = df['PRE']

    # Social columns renamed to match HH_aggregation social_cols conventions
    df['Spouse']      = df['SPOUSE']
    df['Children']    = df['CHILDHSD']
    df['otherInFAMs'] = df['MEMBHSD']

    print(f"Saving to {out_path}")
    df.to_csv(out_path, index=False)
    print("Done!")

if __name__ == '__main__':
    main()
