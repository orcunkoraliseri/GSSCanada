import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


def plot_canada_climate_zones() -> None:
    """
    Spectrum-style infographic of Canadian simulation regions and ASHRAE climate zones.
    Designed for Section 3.5 (Building Energy Modeling Framework) of the journal paper.
    """

    # ── 1. Load data ──────────────────────────────────────────────────────
    csv_path = Path(__file__).parent / "tables" / "canada_simulation_regions.csv"
    df = pd.read_csv(csv_path)

    # ── 2. Define visual mapping ──────────────────────────────────────────
    # Spectrum order: mildest → most severe
    zones_order = ["5C", "5B", "5A", "6B", "6A", "7A"]

    # One distinct color per zone (cold → warm spectrum)
    zone_colors = {
        "5C": "#2ca02c",  # green   — marine/mild
        "5B": "#bcbd22",  # yellow  — semi-arid
        "5A": "#1f77b4",  # blue    — cold-humid moderate
        "6B": "#ff7f0e",  # orange  — cold-dry
        "6A": "#9467bd",  # purple  — cold-humid heating-dominant
        "7A": "#d62728",  # red     — strongly heating-dominant
    }

    # ── 3. Setup figure ───────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(18, 10))

    # Spectrum line
    ax.hlines(y=0, xmin=0.5, xmax=6.5, color="gray", linewidth=3, zorder=1)

    # Mild ←→ Severe labels (above the line)
    ax.text(0.5, 0.02, "← Mild", ha="left", va="bottom",
            fontsize=11, fontstyle="italic", color="gray")
    ax.text(6.5, 0.02, "Severe →", ha="right", va="bottom",
            fontsize=11, fontstyle="italic", color="gray")

    # ── 4. Plot each zone ─────────────────────────────────────────────────
    for i, zone in enumerate(zones_order):
        x = i + 1
        color = zone_colors[zone]
        subset = df[df["ASHRAE Climate Zone"] == zone]

        # Cities: 2 per line inside a single text box
        cities = subset["City"].tolist()
        city_lines = [", ".join(cities[j:j + 2]) for j in range(0, len(cities), 2)]
        city_str = "\n".join(city_lines)

        # Climate character: pull directly from CSV, break at semicolons
        raw_char = subset["Climate Character"].iloc[0]
        char_str = raw_char.replace("; ", "\n").replace(";", "\n")

        # Zone node on the spectrum
        ax.scatter(x, 0, s=900, c=color, zorder=2,
                   edgecolors="black", linewidth=1.5)

        # Zone label just above the node
        ax.text(x, 0.04, f"Zone {zone}",
                ha="center", va="bottom",
                fontweight="bold", fontsize=14, color=color,
                bbox=dict(facecolor="white", edgecolor="none", alpha=0.9))

        # Climate character box (above the zone label)
        ax.text(x, 0.12, char_str,
                ha="center", va="bottom", fontsize=10,
                bbox=dict(facecolor="#f8f9fa", edgecolor=color,
                          boxstyle="round,pad=0.6", alpha=0.95))

        # Cities box (below the spectrum line)
        ax.text(x, -0.06, f"Cities:\n{city_str}",
                ha="center", va="top", fontsize=10,
                bbox=dict(facecolor="white", edgecolor="gray",
                          boxstyle="round,pad=0.6", alpha=0.95))

    # ── 5. Formatting ────────────────────────────────────────────────────
    ax.axis("off")
    ax.set_ylim(-0.60, 0.60)
    ax.set_xlim(0.2, 6.8)

    fig.suptitle(
        "Figure 3.5.1: Canadian Simulation Regions by ASHRAE Climate Zone",
        fontweight="bold", fontsize=18, y=0.96)

    plt.tight_layout()
    plt.savefig(Path(__file__).parent / "tables" / "canada_climate_zones.png",
                dpi=300, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    plot_canada_climate_zones()
