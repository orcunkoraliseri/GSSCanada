import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_schedule_discrepancies() -> None:
    """
    Creates grouped bar charts to compare Default vs 2025 GSS patterns.
    Subplots are used to separate metrics by their units (Ratio, %, Watts).
    """
    # 1. Define the numerical data from the table
    data = {
        "Parameter": [
            "Mean weekday occupancy", 
            "Mean weekend occupancy",
            "Daytime occupancy (09-17)",
            "Mean metabolic rate",
            "Peak metabolic rate"
        ],
        "Default": [0.684, 0.684, 25.60, 95.0, 95.0],
        "2025 GSS": [0.465, 0.502, 27.60, 72.7, 95.0]
    }
    
    df = pd.DataFrame(data)
    
    # 2. Setup the figure and 3 subplots (1 row, 3 columns)
    fig, axes = plt.subplots(1, 3, figsize=(16, 6))
    
    # Colors for the groups
    color_default = '#1f77b4'  # Blue
    color_gss = '#ff7f0e'      # Orange
    bar_width = 0.35

    def create_grouped_bars(ax, slice_start: int, slice_end: int, title: str, ylabel: str) -> None:
        """Helper function to draw a grouped bar chart on a specific subplot axis."""
        sub_df = df.iloc[slice_start:slice_end]
        labels = sub_df['Parameter'].tolist()
        
        x = np.arange(len(labels))
        
        # Draw bars
        rects1 = ax.bar(x - bar_width/2, sub_df['Default'], bar_width, label='Default', color=color_default)
        rects2 = ax.bar(x + bar_width/2, sub_df['2025 GSS'], bar_width, label='2025 GSS', color=color_gss)
        
        # Formatting
        ax.set_ylabel(ylabel, fontweight='bold')
        ax.set_title(title, fontweight='bold')
        ax.set_xticks(x)
        
        # Wrap text for long labels
        wrapped_labels = [label.replace(' ', '\n') for label in labels]
        ax.set_xticklabels(wrapped_labels)
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Add text labels on top of the bars
        ax.bar_label(rects1, padding=3, fmt='%.3g')
        ax.bar_label(rects2, padding=3, fmt='%.3g')

    # 3. Plot Subplot 1: Occupancy Ratios (0-1)
    create_grouped_bars(axes[0], slice_start=0, slice_end=2, 
                        title='Mean Occupancy (Ratio 0-1)', ylabel='Occupancy Ratio')
    axes[0].set_ylim(0, 0.8) # Add headroom for labels

    # 4. Plot Subplot 2: Daytime Occupancy (%)
    create_grouped_bars(axes[1], slice_start=2, slice_end=3, 
                        title='Daytime Occupancy (%)', ylabel='Percentage (%)')
    axes[1].set_ylim(0, 35)

    # 5. Plot Subplot 3: Metabolic Rates (W)
    create_grouped_bars(axes[2], slice_start=3, slice_end=5, 
                        title='Metabolic Rates (W)', ylabel='Watts (W)')
    axes[2].set_ylim(0, 115)

    # 6. Global formatting
    plt.suptitle('Schedule Discrepancies: Default vs 2025 GSS Patterns', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.subplots_adjust(top=0.88) # Adjust layout so suptitle fits
    
    # Save the plot instead of showing it
    output_path = 'e_Sim_occ_utils/plotting/summary_discrepancies.png'
    # Wait, the path should be consistent.
    # The active doc is in eSim_occ_utils/plotting/
    output_path = '/Users/orcunkoraliseri/Desktop/Postdoc/occModeling/eSim_occ_utils/plotting/summary_discrepancies.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Plot saved to {output_path}")

if __name__ == "__main__":
    plot_schedule_discrepancies()
