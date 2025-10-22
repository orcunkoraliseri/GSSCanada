import pandas as pd
import pyreadstat
import re, os
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)  # Adjust as needed, or use None
def load_spss_file(file_path):
    print(f"Reading file: {file_path}...")
    df, meta = pyreadstat.read_sav(file_path)
    print("df_SPSS", df.head(10))
    return df, meta

def print_unique_counts(df):
    print("--- Calculating Unique Value Counts for Each Column ---")
    # Store original pandas display setting
    pd.set_option('display.max_rows', None)
    unique_counts = df.nunique()
    print(unique_counts)


if __name__ == '__main__':
    """
    C19PUMFM_NUM.SAV: This is the Main file containing the core socio-demographic data and the 24-hour time-use diary for all survey respondents.
    C19PUMFE_NUM.SAV: This is the Extended file containing the split-sample variables (e.g., culture, sports, social networks, transportation) that were asked of only a random subset of respondents.
    """
    GSS_2005_SPSS_full = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Data Sources/Canada_2005/Data Files SPSS/C19PUMFM_NUM.SAV"
    GSS_2005_SPSS_temporal = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Data Sources/Canada_2005/Data Files SPSS/C19PUMFE_NUM.SAV"

    GSS_2010_SPSS_temporal = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Data Sources/Canada_2010/Data_Donn‚es/C24EPISODE_withno_bootstrap.DAT"
    sps_syntax = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Data Sources/Canada_2010/Syntax_Syntaxe/SPSS/C24_Episode File_SPSS_withno_bootstrap.SPS"

    df_2005, meta = load_spss_file(GSS_2005_SPSS_temporal)
    print_unique_counts(df_2005)

