import os
import re
import pandas as pd
from pathlib import Path

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

def main():
    base_dir = Path("/Users/orcunkoraliseri/Desktop/Postdoc/occModeling")
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
    
    print(f"Saving to {out_path}")
    df.to_csv(out_path, index=False)
    print("Done!")

if __name__ == '__main__':
    main()
