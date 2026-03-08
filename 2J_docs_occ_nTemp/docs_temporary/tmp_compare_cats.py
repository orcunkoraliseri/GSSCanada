import pandas as pd
import os

CYCLES = [2005, 2010, 2015, 2022]
INPUT_DIR = "/Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/outputs_step2/"
OUTPUT_FILE = "/Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/outputs_step2/column_categories_comparison.txt"

def main():
    with open(OUTPUT_FILE, "w") as f:
        f.write("=== Column Category Comparison Across Cycles (Step 2 Data) ===\n\n")

        # Load all main dataframes from step 2
        dfs = {c: pd.read_csv(os.path.join(INPUT_DIR, f"main_{c}.csv")) for c in CYCLES}
        
        # Only include columns from the validation report (HARM_VARS)
        cols_to_check = ["SEX", "AGEGRP", "MARSTH", "HHSIZE", "CMA", "LFTAG", "HRSWRK", "KOL", "MODE", "TOTINC"]

        for col in cols_to_check:
            f.write(f"--- Column: {col} ---\n")
            for c in CYCLES:
                df = dfs[c]
                if col in df.columns:
                    # Calculate counts and percentages
                    counts = df[col].value_counts(dropna=True).sort_index()
                    total = counts.sum()
                    if total > 0:
                        pcts = (counts / total * 100).round(1)
                        dist_str = ", ".join([f"{val}: {pct}%" for val, pct in pcts.items()])
                        f.write(f"  {c}: [{dist_str}]\n")
                    else:
                        f.write(f"  {c}: []\n")
                else:
                    f.write(f"  {c}: <MISSING>\n")
            f.write("\n")

    print(f"Comparison saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
