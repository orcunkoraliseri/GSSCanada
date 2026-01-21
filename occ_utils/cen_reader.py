"""
Census DTYPE Distribution Reader

Reads all Census filtered files (2006, 2011, 2016, 2021) and plots
the distribution of DTYPE (Dwelling Type) column across years.

This is for validating DTYPE consistency across Census years.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


def main():
    """Read all Census files and compare DTYPE distributions."""
    
    BASE_DIR = Path("/Users/orcunkoraliseri/Desktop/Postdoc/eSim/Occupancy")
    CENSUS_DIR = BASE_DIR / "Outputs_CENSUS"
    OUTPUT_DIR = BASE_DIR / "Outputs_CENSUS"
    
    # Census files to read
    census_files = {
        "2006": CENSUS_DIR / "cen06_filtered.csv",
        "2011": CENSUS_DIR / "cen11_filtered.csv", 
        "2016": CENSUS_DIR / "cen16_filtered.csv",
        "2021": CENSUS_DIR / "cen21_filtered.csv"
    }
    
    # DTYPE Mapping (Code -> Description) - Census 2006 standard
    dtype_map = {
        1: "SingleD",    # Single Detached
        2: "SemiD",      # Semi-Detached
        3: "Attached",   # Row/Attached
        4: "DuplexD",    # Duplex
        5: "HighRise",   # High-Rise Apartment (5+ stories)
        6: "MidRise",    # Mid-Rise Apartment (<5 stories)
        7: "OtherA",     # Other Attached
        8: "Movable",    # Mobile Home
    }
    
    print("=" * 60)
    print("  CENSUS DTYPE DISTRIBUTION ANALYSIS")
    print("=" * 60)
    
    # Collect DTYPE stats from each file
    dtype_data = {}
    
    for year, filepath in census_files.items():
        print(f"\n--- Census {year} ---")
        
        if not filepath.exists():
            print(f"   ⚠️ File not found: {filepath.name}")
            continue
            
        # Read file
        df = pd.read_csv(filepath, low_memory=False)
        print(f"   Loaded: {len(df):,} rows")
        
        # Check for DTYPE column
        if 'DTYPE' not in df.columns:
            print(f"   ⚠️ DTYPE column not found. Available: {list(df.columns)[:10]}")
            continue
        
        # Get DTYPE distribution
        dtype_counts = df['DTYPE'].value_counts().sort_index()
        print(f"   DTYPE unique values: {sorted(df['DTYPE'].dropna().unique())}")
        print(f"   DTYPE distribution:")
        for code, count in dtype_counts.items():
            pct = count / len(df) * 100
            label = dtype_map.get(int(code), f"Unknown({code})")
            print(f"      {code} ({label}): {count:,} ({pct:.1f}%)")
        
        # Store for plotting
        dtype_data[year] = dtype_counts
    
    # Create comparison plot
    if len(dtype_data) > 0:
        print("\n" + "=" * 60)
        print("  GENERATING COMPARISON PLOT")
        print("=" * 60)
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        axes = axes.flatten()
        
        colors = sns.color_palette("viridis", 8)
        
        for idx, (year, counts) in enumerate(dtype_data.items()):
            ax = axes[idx]
            
            # Map codes to labels
            labels = [dtype_map.get(int(c), f"Unk({c})") for c in counts.index]
            values = counts.values
            
            # Plot
            bars = ax.bar(labels, values, color=colors[:len(labels)])
            ax.set_title(f"Census {year} - DTYPE Distribution", fontsize=12, fontweight='bold')
            ax.set_xlabel("Dwelling Type")
            ax.set_ylabel("Count of Households")
            ax.tick_params(axis='x', rotation=45)
            
            # Add percentage labels
            total = values.sum()
            for bar, val in zip(bars, values):
                pct = val / total * 100
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + total*0.01,
                       f'{pct:.1f}%', ha='center', va='bottom', fontsize=8)
        
        # Hide unused axes
        for idx in range(len(dtype_data), 4):
            axes[idx].axis('off')
        
        plt.tight_layout()
        
        # Save plot
        output_path = OUTPUT_DIR / "Census_DTYPE_Comparison.png"
        plt.savefig(output_path, dpi=150)
        plt.close()
        
        print(f"\n   ✅ Plot saved to: {output_path.name}")
    
    print("\n" + "=" * 60)
    print("  ANALYSIS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
