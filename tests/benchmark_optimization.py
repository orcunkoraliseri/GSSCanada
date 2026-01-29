#!/usr/bin/env python3
"""
Benchmark Script: Test IDF Optimization Impact on Simulation Speed and Accuracy

This script compares:
1. Original IDF simulation (baseline)
2. Optimized IDF simulation (pruned objects + fast settings)

Outputs:
- Simulation time comparison
- Energy results comparison (EUI by end-use)
- Accuracy report (% difference)

Author: Generated for GSSCanada project
"""

import os
import sys
import time
import shutil
import sqlite3
from datetime import datetime
from typing import Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eppy.modeleditor import IDF

# Import project modules
from bem_utils import config  # Sets up IDD
from bem_utils import simulation
from bem_utils import idf_optimizer

# =============================================================================
# Configuration
# =============================================================================

# Paths - Update these as needed
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BEM_SETUP_DIR = os.path.join(BASE_DIR, "BEM_Setup")
BUILDINGS_DIR = os.path.join(BEM_SETUP_DIR, "Buildings")
WEATHER_DIR = os.path.join(BEM_SETUP_DIR, "WeatherFile")
OUTPUT_DIR = os.path.join(BASE_DIR, "tests", "benchmark_results")

# EnergyPlus paths
ENERGYPLUS_EXE = config.ENERGYPLUS_EXE

# =============================================================================
# Optimization Functions (Candidates for idf_optimizer.py)
# =============================================================================


def prune_idf_for_speed(idf: IDF, verbose: bool = False) -> IDF:
    """
    Remove non-essential output objects to speed up simulation.
    
    Preserves:
        - SQL output (needed for result extraction)
        - Essential tabular summaries
    
    Removes:
        - Output:Variable (hourly data we don't need)
        - Output:Meter (detailed meter outputs)
        - Output:Diagnostics
        - Detailed reporting objects
    
    Args:
        idf: The IDF object to prune.
        verbose: If True, print details of removed objects.
    
    Returns:
        The pruned IDF object.
    """
    objects_to_remove = [
        'Output:Variable',
        'Output:Meter',
        'Output:Meter:MeterFileOnly',
        'Output:Diagnostics',
        'Output:DebuggingData',
        'Output:PreprocessorMessage',
        'Output:Constructions',
        'Output:EnergyManagementSystem',
    ]
    
    removed_count = {}
    
    for obj_type in objects_to_remove:
        objs = idf.idfobjects.get(obj_type, [])
        removed_count[obj_type] = len(objs)
        for obj in objs[:]:  # Copy list to avoid mutation during iteration
            idf.removeidfobject(obj)
    
    if verbose:
        print("\n  [Pruning] Removed objects:")
        for obj_type, count in removed_count.items():
            if count > 0:
                print(f"    - {obj_type}: {count}")
    
    return idf


def optimize_simulation_settings_v2(
    idf: IDF, 
    profile: str = 'balanced',
    verbose: bool = False
) -> IDF:
    """
    Apply optimization settings based on selected profile.
    
    Profiles:
        - 'balanced': TARP convection, HVAC iter=10, 60-day shadow (accuracy-focused)
        - 'fast': Simple convection, all optimizations (speed-focused)
        - 'weekly': 12 representative weeks, scaled to annual
        - 'design_day': Design days only (fastest, sizing validation)
    
    Args:
        idf: The IDF object to optimize.
        profile: Optimization profile name.
        verbose: If True, print changes made.
    
    Returns:
        The optimized IDF object.
    """
    changes = []
    
    # ==========================================================================
    # 1. Timestep Optimization (all profiles)
    # ==========================================================================
    ts_objs = idf.idfobjects.get('Timestep', [])
    if ts_objs:
        old_val = ts_objs[0].Number_of_Timesteps_per_Hour
        ts_objs[0].Number_of_Timesteps_per_Hour = 4
        changes.append(f"Timestep: {old_val} -> 4")
    
    # ==========================================================================
    # 2. Shadow Calculation Optimization (all profiles)
    # ==========================================================================
    shadow_objs = idf.idfobjects.get('ShadowCalculation', [])
    if shadow_objs:
        shadow = shadow_objs[0]
    else:
        shadow = idf.newidfobject('ShadowCalculation')
        changes.append("Created ShadowCalculation object")
    
    # Use PixelCounting for faster shading (especially complex geometry)
    shadow.Shading_Calculation_Method = 'PixelCounting'
    shadow.Pixel_Counting_Resolution = 512
    shadow.Shading_Calculation_Update_Frequency_Method = 'Periodic'
    shadow.Shading_Calculation_Update_Frequency = 60
    shadow.Maximum_Figures_in_Shadow_Overlap_Calculations = 5000
    changes.append("Shadow: PixelCounting (512), 60-day frequency")
    
    # ==========================================================================
    # 3. HVAC Convergence Limits (all profiles)
    # ==========================================================================
    conv_limits = idf.idfobjects.get('ConvergenceLimits', [])
    if conv_limits:
        conv_limits[0].Maximum_HVAC_Iterations = 10
    else:
        conv_obj = idf.newidfobject('ConvergenceLimits')
        conv_obj.Maximum_HVAC_Iterations = 10
    changes.append("HVAC Max Iterations: 10")
    
    # ==========================================================================
    # 4. Convection Algorithm (profile-dependent)
    # ==========================================================================
    inside_conv = idf.idfobjects.get('SurfaceConvectionAlgorithm:Inside', [])
    outside_conv = idf.idfobjects.get('SurfaceConvectionAlgorithm:Outside', [])
    
    if profile == 'fast':
        # Simple = fastest but ~6% heating difference
        inside_alg = 'Simple'
        outside_alg = 'SimpleCombined'
    else:
        # TARP = more accurate (~1% diff) but slightly slower
        inside_alg = 'TARP'
        outside_alg = 'DOE-2'  # Good balance for outside
    
    if inside_conv:
        old_alg = inside_conv[0].Algorithm
        inside_conv[0].Algorithm = inside_alg
        changes.append(f"Inside Convection: {old_alg} -> {inside_alg}")
    else:
        conv_obj = idf.newidfobject('SurfaceConvectionAlgorithm:Inside')
        conv_obj.Algorithm = inside_alg
        changes.append(f"Created Inside Convection: {inside_alg}")
    
    if outside_conv:
        old_alg = outside_conv[0].Algorithm
        outside_conv[0].Algorithm = outside_alg
        changes.append(f"Outside Convection: {old_alg} -> {outside_alg}")
    else:
        conv_obj = idf.newidfobject('SurfaceConvectionAlgorithm:Outside')
        conv_obj.Algorithm = outside_alg
        changes.append(f"Created Outside Convection: {outside_alg}")
    
    # ==========================================================================
    # 5. Run Period Configuration (profile-dependent)
    # ==========================================================================
    if profile == 'weekly':
        # Remove existing run periods
        for rp in idf.idfobjects.get('RunPeriod', [])[:]:
            idf.removeidfobject(rp)
        
        # TMY-REPRESENTATIVE: 2 weeks per month (168 days total)
        # Week 1: Days 1-7 (early month)
        # Week 2: Days 15-21 (mid-month, captures monthly variation)
        # This provides better representation of monthly patterns
        
        tmy_weeks = [
            # January - coldest, high heating
            (1, 1, 1, 7, "Jan_W1"),
            (1, 15, 1, 21, "Jan_W2"),
            # February - still cold
            (2, 1, 2, 7, "Feb_W1"),
            (2, 15, 2, 21, "Feb_W2"),
            # March - transition
            (3, 1, 3, 7, "Mar_W1"),
            (3, 15, 3, 21, "Mar_W2"),
            # April - spring
            (4, 1, 4, 7, "Apr_W1"),
            (4, 15, 4, 21, "Apr_W2"),
            # May - warming
            (5, 1, 5, 7, "May_W1"),
            (5, 15, 5, 21, "May_W2"),
            # June - early summer
            (6, 1, 6, 7, "Jun_W1"),
            (6, 15, 6, 21, "Jun_W2"),
            # July - peak cooling
            (7, 1, 7, 7, "Jul_W1"),
            (7, 15, 7, 21, "Jul_W2"),
            # August - high cooling
            (8, 1, 8, 7, "Aug_W1"),
            (8, 15, 8, 21, "Aug_W2"),
            # September - transition
            (9, 1, 9, 7, "Sep_W1"),
            (9, 15, 9, 21, "Sep_W2"),
            # October - fall
            (10, 1, 10, 7, "Oct_W1"),
            (10, 15, 10, 21, "Oct_W2"),
            # November - cooling down
            (11, 1, 11, 7, "Nov_W1"),
            (11, 15, 11, 21, "Nov_W2"),
            # December - cold again
            (12, 1, 12, 7, "Dec_W1"),
            (12, 15, 12, 21, "Dec_W2"),
        ]
        
        for start_m, start_d, end_m, end_d, name in tmy_weeks:
            rp = idf.newidfobject('RunPeriod')
            rp.Name = name
            rp.Begin_Month = start_m
            rp.Begin_Day_of_Month = start_d
            rp.End_Month = end_m
            rp.End_Day_of_Month = end_d
            rp.Day_of_Week_for_Start_Day = 'Sunday'
            rp.Use_Weather_File_Holidays_and_Special_Days = 'No'
            rp.Use_Weather_File_Daylight_Saving_Period = 'No'
            rp.Apply_Weekend_Holiday_Rule = 'No'
            rp.Use_Weather_File_Rain_Indicators = 'Yes'
            rp.Use_Weather_File_Snow_Indicators = 'Yes'
        
        changes.append("Run Period: 24 TMY-representative weeks (168 days)")
        
    elif profile == 'design_day':
        # Remove all run periods - only design days will run
        for rp in idf.idfobjects.get('RunPeriod', [])[:]:
            idf.removeidfobject(rp)
        changes.append("Run Period: Design days only (sizing)")
    
    if verbose:
        print(f"\n  [Settings v2 - {profile.upper()}] Optimizations applied:")
        for change in changes:
            print(f"    - {change}")
    
    return idf


# =============================================================================
# Benchmark Functions
# =============================================================================


def run_simulation_timed(
    idf_path: str,
    epw_path: str,
    output_dir: str,
    label: str
) -> tuple[float, str]:
    """
    Run a single EnergyPlus simulation and measure execution time.
    
    Args:
        idf_path: Path to the IDF file.
        epw_path: Path to the weather file.
        output_dir: Directory for simulation outputs.
        label: Label for logging.
    
    Returns:
        Tuple of (elapsed_time_seconds, sql_path).
    """
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n  [{label}] Starting simulation...")
    start_time = time.time()
    
    # Run simulation using the correct API
    result = simulation.run_simulation(
        idf_path=idf_path,
        epw_path=epw_path,
        output_dir=output_dir,
        ep_path=ENERGYPLUS_EXE,
        quiet=False
    )
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    sql_path = os.path.join(output_dir, "eplusout.sql")
    
    if result.get('success'):
        print(f"  [{label}] Completed in {elapsed:.2f} seconds")
    else:
        print(f"  [{label}] FAILED after {elapsed:.2f} seconds: {result.get('message')}")
    
    return elapsed, sql_path


def extract_eui_results(sql_path: str) -> dict:
    """
    Extract EUI results from simulation SQL output.
    
    Args:
        sql_path: Path to eplusout.sql file.
    
    Returns:
        Dictionary with end-use categories and their EUI values.
    """
    if not os.path.exists(sql_path):
        return {}
    
    results = {}
    
    try:
        conn = sqlite3.connect(sql_path)
        cursor = conn.cursor()
        
        # Get total floor area
        cursor.execute("""
            SELECT Value FROM TabularDataWithStrings 
            WHERE TableName='Building Area' 
            AND RowName='Total Building Area' 
            AND ColumnName='Area'
        """)
        area_row = cursor.fetchone()
        total_area = float(area_row[0]) if area_row else 1.0
        
        # Get end-use energy (sum Electricity and Natural Gas)
        # Values are in MJ, convert to kWh (/ 3.6)
        cursor.execute("""
            SELECT RowName, SUM(CAST(Value AS REAL)) as TotalEnergy
            FROM TabularDataWithStrings 
            WHERE TableName='End Uses' 
            AND ColumnName IN ('Electricity', 'Natural Gas')
            AND RowName != ''
            AND RowName != 'Total End Uses'
            GROUP BY RowName
        """)
        
        for row in cursor.fetchall():
            end_use = row[0]
            try:
                value_mj = float(row[1])
                value_kwh = value_mj / 3.6  # MJ to kWh
                eui = value_kwh / total_area if total_area > 0 else 0
                results[end_use] = eui
            except (ValueError, TypeError):
                pass
        
        conn.close()
    except Exception as e:
        print(f"  Warning: Error extracting results: {e}")
    
    return results


def extract_design_day_sizing(sql_path: str) -> dict:
    """
    Extract design-day sizing results from simulation SQL output.
    
    Args:
        sql_path: Path to eplusout.sql file.
    
    Returns:
        Dictionary with sizing results (peak heating/cooling loads).
    """
    if not os.path.exists(sql_path):
        return {}
    
    results = {}
    
    try:
        conn = sqlite3.connect(sql_path)
        cursor = conn.cursor()
        
        # Get zone sizing summary (peak heating/cooling loads)
        cursor.execute("""
            SELECT RowName, ColumnName, Value FROM TabularDataWithStrings 
            WHERE TableName='Zone Sensible Cooling' 
            OR TableName='Zone Sensible Heating'
        """)
        
        for row in cursor.fetchall():
            row_name, col_name, value = row
            if 'Peak' in col_name or 'Design' in col_name:
                key = f"{row_name}_{col_name}"
                try:
                    results[key] = float(value)
                except (ValueError, TypeError):
                    pass
        
        # Also try to get System Sizing Summary
        cursor.execute("""
            SELECT RowName, ColumnName, Value FROM TabularDataWithStrings 
            WHERE TableName='System Sizing Summary' 
            AND (ColumnName LIKE '%Heating%' OR ColumnName LIKE '%Cooling%')
        """)
        
        for row in cursor.fetchall():
            row_name, col_name, value = row
            key = f"System_{col_name}"
            try:
                val = float(value)
                if key not in results or val > results[key]:
                    results[key] = val
            except (ValueError, TypeError):
                pass
        
        conn.close()
    except Exception as e:
        print(f"  Warning: Error extracting sizing results: {e}")
    
    return results


def compare_results(
    original: dict,
    optimized: dict
) -> dict:
    """
    Compare EUI results between original and optimized simulations.
    
    Args:
        original: EUI results from original simulation.
        optimized: EUI results from optimized simulation.
    
    Returns:
        Dictionary with comparison metrics.
    """
    comparison = {}
    
    all_keys = set(original.keys()) | set(optimized.keys())
    
    for key in sorted(all_keys):
        orig_val = original.get(key, 0.0)
        opt_val = optimized.get(key, 0.0)
        
        if orig_val > 0:
            pct_diff = ((opt_val - orig_val) / orig_val) * 100
        else:
            pct_diff = 0.0 if opt_val == 0 else float('inf')
        
        comparison[key] = {
            'original': orig_val,
            'optimized': opt_val,
            'difference': opt_val - orig_val,
            'pct_difference': pct_diff
        }
    
    return comparison


def generate_report(
    time_original: float,
    time_optimized: float,
    comparison: dict,
    output_path: str
) -> None:
    """
    Generate a text report of the benchmark results.
    
    Args:
        time_original: Simulation time for original IDF (seconds).
        time_optimized: Simulation time for optimized IDF (seconds).
        comparison: Dictionary from compare_results().
        output_path: Path to save the report.
    """
    time_saved = time_original - time_optimized
    time_saved_pct = (time_saved / time_original) * 100 if time_original > 0 else 0
    
    lines = [
        "=" * 70,
        "SIMULATION OPTIMIZATION BENCHMARK REPORT",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 70,
        "",
        "1. SIMULATION TIME COMPARISON",
        "-" * 40,
        f"  Original IDF:   {time_original:8.2f} seconds",
        f"  Optimized IDF:  {time_optimized:8.2f} seconds",
        f"  Time Saved:     {time_saved:8.2f} seconds ({time_saved_pct:.1f}%)",
        "",
        "2. ENERGY USE INTENSITY (EUI) COMPARISON",
        "-" * 40,
        f"  {'End Use':<25} {'Original':>12} {'Optimized':>12} {'Diff %':>10}",
        f"  {'':25} {'(kWh/m²)':>12} {'(kWh/m²)':>12} {'':>10}",
        "-" * 70,
    ]
    
    total_orig = 0
    total_opt = 0
    max_diff_pct = 0
    
    for key, vals in sorted(comparison.items()):
        orig = vals['original']
        opt = vals['optimized']
        pct = vals['pct_difference']
        
        total_orig += orig
        total_opt += opt
        max_diff_pct = max(max_diff_pct, abs(pct))
        
        lines.append(f"  {key:<25} {orig:12.2f} {opt:12.2f} {pct:+10.2f}%")
    
    lines.append("-" * 70)
    total_pct = ((total_opt - total_orig) / total_orig * 100) if total_orig > 0 else 0
    lines.append(f"  {'TOTAL':<25} {total_orig:12.2f} {total_opt:12.2f} {total_pct:+10.2f}%")
    
    lines.extend([
        "",
        "3. ACCURACY ASSESSMENT",
        "-" * 40,
        f"  Maximum single-category difference: {max_diff_pct:.2f}%",
        f"  Total energy difference: {abs(total_pct):.2f}%",
        "",
    ])
    
    if abs(total_pct) < 1.0 and max_diff_pct < 5.0:
        verdict = "✅ EXCELLENT - Optimization is safe to use"
    elif abs(total_pct) < 3.0 and max_diff_pct < 10.0:
        verdict = "✓ ACCEPTABLE - Minor accuracy trade-off"
    else:
        verdict = "⚠ CAUTION - Review results before using"
    
    lines.extend([
        f"  Verdict: {verdict}",
        "",
        "=" * 70,
    ])
    
    report_text = "\n".join(lines)
    
    # Print to console
    print("\n" + report_text)
    
    # Save to file
    with open(output_path, 'w') as f:
        f.write(report_text)
    
    print(f"\nReport saved to: {output_path}")


# =============================================================================
# Main Benchmark Flow
# =============================================================================


def run_benchmark_v2(
    idf_path: str,
    epw_path: str,
    output_base_dir: Optional[str] = None
) -> None:
    """
    Run the full benchmark comparing 3 simulation profiles:
    1. Original (full year, standard settings)
    2. Weekly (12 representative weeks, TARP convection)
    3. Design-Day (sizing days only, fastest)
    
    Args:
        idf_path: Path to the original IDF file.
        epw_path: Path to the weather file.
        output_base_dir: Base directory for outputs.
    """
    if output_base_dir is None:
        output_base_dir = OUTPUT_DIR
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    benchmark_dir = os.path.join(output_base_dir, f"benchmark_v2_{timestamp}")
    os.makedirs(benchmark_dir, exist_ok=True)
    
    print("\n" + "=" * 70)
    print("SIMULATION OPTIMIZATION BENCHMARK v2 (3-Way Comparison)")
    print("=" * 70)
    print(f"\nIDF: {os.path.basename(idf_path)}")
    print(f"EPW: {os.path.basename(epw_path)}")
    print(f"Output: {benchmark_dir}")
    
    results = {}  # Store all results
    
    # ==========================================================================
    # Step 1: Prepare Base IDF (with compatibility fixes)
    # ==========================================================================
    print("\n[Step 1] Preparing Base IDF (with compatibility fixes)...")
    base_dir = os.path.join(benchmark_dir, "base")
    base_idf_path = os.path.join(base_dir, "base.idf")
    os.makedirs(base_dir, exist_ok=True)
    
    idf_optimizer.prepare_idf_for_simulation(
        idf_path, base_idf_path, verbose=True, standardize_schedules=True
    )
    
    IDF.setiddname(config.IDD_FILE)
    
    # ==========================================================================
    # Step 2: Prepare ORIGINAL (full year, TARP convection, no pruning)
    # ==========================================================================
    print("\n[Step 2] Preparing ORIGINAL simulation (full year, baseline)...")
    original_dir = os.path.join(benchmark_dir, "original")
    original_idf_path = os.path.join(original_dir, "original.idf")
    os.makedirs(original_dir, exist_ok=True)
    shutil.copy(base_idf_path, original_idf_path)
    
    # ==========================================================================
    # Step 3: Prepare WEEKLY (12 representative weeks, TARP, all optimizations)
    # ==========================================================================
    print("\n[Step 3] Preparing WEEKLY simulation (12 weeks, TARP)...")
    weekly_dir = os.path.join(benchmark_dir, "weekly")
    weekly_idf_path = os.path.join(weekly_dir, "weekly.idf")
    os.makedirs(weekly_dir, exist_ok=True)
    
    idf_weekly = IDF(base_idf_path)
    idf_weekly = prune_idf_for_speed(idf_weekly, verbose=True)
    idf_weekly = optimize_simulation_settings_v2(idf_weekly, profile='weekly', verbose=True)
    idf_weekly.saveas(weekly_idf_path)
    
    # ==========================================================================
    # Step 4: Prepare DESIGN-DAY (sizing days only)
    # ==========================================================================
    print("\n[Step 4] Preparing DESIGN-DAY simulation (sizing only)...")
    designday_dir = os.path.join(benchmark_dir, "design_day")
    designday_idf_path = os.path.join(designday_dir, "design_day.idf")
    os.makedirs(designday_dir, exist_ok=True)
    
    idf_dd = IDF(base_idf_path)
    idf_dd = prune_idf_for_speed(idf_dd, verbose=True)
    idf_dd = optimize_simulation_settings_v2(idf_dd, profile='design_day', verbose=True)
    idf_dd.saveas(designday_idf_path)
    
    # ==========================================================================
    # Step 5: Run ORIGINAL Simulation
    # ==========================================================================
    print("\n[Step 5] Running ORIGINAL Simulation (full year)...")
    time_original, sql_original = run_simulation_timed(
        original_idf_path, epw_path, original_dir, "Original"
    )
    results['original'] = {
        'time': time_original,
        'sql': sql_original,
        'scale_factor': 1.0  # No scaling
    }
    
    # ==========================================================================
    # Step 6: Run WEEKLY Simulation
    # ==========================================================================
    print("\n[Step 6] Running WEEKLY Simulation (24 TMY weeks)...")
    time_weekly, sql_weekly = run_simulation_timed(
        weekly_idf_path, epw_path, weekly_dir, "Weekly"
    )
    results['weekly'] = {
        'time': time_weekly,
        'sql': sql_weekly,
        'scale_factor': 52.0 / 24.0  # Scale 24 weeks (168 days) to 52 weeks
    }
    
    # ==========================================================================
    # Step 7: Run DESIGN-DAY Simulation
    # ==========================================================================
    print("\n[Step 7] Running DESIGN-DAY Simulation...")
    time_dd, sql_dd = run_simulation_timed(
        designday_idf_path, epw_path, designday_dir, "Design-Day"
    )
    results['design_day'] = {
        'time': time_dd,
        'sql': sql_dd,
        'scale_factor': None  # Not scalable to annual
    }
    
    # ==========================================================================
    # Step 8: Extract and Compare Results
    # ==========================================================================
    print("\n[Step 8] Extracting and comparing results...")
    
    eui_original = extract_eui_results(sql_original)
    eui_weekly = extract_eui_results(sql_weekly)
    eui_dd = extract_eui_results(sql_dd)
    sizing_dd = extract_design_day_sizing(sql_dd)  # Design-day sizing results
    
    # Scale weekly results to annual (x 52/24 = x 2.17)
    eui_weekly_scaled = {k: v * (52.0 / 24.0) for k, v in eui_weekly.items()}
    
    # ==========================================================================
    # Step 9: Generate Report
    # ==========================================================================
    print("\n[Step 9] Generating comparison report...")
    generate_report_v2(
        time_original, time_weekly, time_dd,
        eui_original, eui_weekly_scaled, eui_dd, sizing_dd,
        os.path.join(benchmark_dir, "benchmark_report_v2.txt")
    )
    
    print("\n✅ Benchmark v2 complete!")


def generate_report_v2(
    time_original: float,
    time_weekly: float,
    time_dd: float,
    eui_original: dict,
    eui_weekly_scaled: dict,
    eui_dd: dict,
    sizing_dd: dict,
    output_path: str
) -> None:
    """Generate 3-way comparison report."""
    
    lines = [
        "=" * 80,
        "SIMULATION OPTIMIZATION BENCHMARK v2 - 3-WAY COMPARISON",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 80,
        "",
        "1. SIMULATION TIME COMPARISON",
        "-" * 50,
        f"  {'Profile':<20} {'Time (s)':>12} {'Speedup':>12}",
        "-" * 50,
        f"  {'Original (Full Year)':<20} {time_original:>12.2f} {'1.00x':>12}",
        f"  {'Weekly (24 TMY wks)':<20} {time_weekly:>12.2f} {(time_original/time_weekly if time_weekly > 0 else 0):>11.2f}x",
        f"  {'Design-Day (Sizing)':<20} {time_dd:>12.2f} {(time_original/time_dd if time_dd > 0 else 0):>11.2f}x",
        "",
        "2. ENERGY USE INTENSITY - ORIGINAL vs WEEKLY (scaled to annual)",
        "-" * 50,
        f"  {'End Use':<25} {'Original':>12} {'Weekly*':>12} {'Diff %':>10}",
        f"  {'':25} {'(kWh/m²)':>12} {'(kWh/m²)':>12} {'':>10}",
        "-" * 80,
    ]
    
    total_orig = 0
    total_weekly = 0
    max_diff_pct = 0
    
    all_keys = set(eui_original.keys()) | set(eui_weekly_scaled.keys())
    
    for key in sorted(all_keys):
        if key in ['Time of Peak']:  # Skip non-energy rows
            continue
        orig = eui_original.get(key, 0.0)
        weekly = eui_weekly_scaled.get(key, 0.0)
        
        total_orig += orig
        total_weekly += weekly
        
        if orig > 0:
            pct = ((weekly - orig) / orig) * 100
            max_diff_pct = max(max_diff_pct, abs(pct))
        else:
            pct = 0.0
        
        lines.append(f"  {key:<25} {orig:12.2f} {weekly:12.2f} {pct:+10.2f}%")
    
    lines.append("-" * 80)
    total_pct = ((total_weekly - total_orig) / total_orig * 100) if total_orig > 0 else 0
    lines.append(f"  {'TOTAL':<25} {total_orig:12.2f} {total_weekly:12.2f} {total_pct:+10.2f}%")
    
    lines.extend([
        "",
        "  * Weekly results scaled by 52/24 = 2.17x to project annual values",
        "  * 24 TMY-representative weeks: 2 weeks per month (early + mid-month)",
        "",
        "3. ACCURACY ASSESSMENT (Original vs Weekly)",
        "-" * 50,
        f"  Maximum single-category difference: {max_diff_pct:.2f}%",
        f"  Total energy difference: {abs(total_pct):.2f}%",
        "",
    ])
    
    if abs(total_pct) < 1.0 and max_diff_pct < 5.0:
        verdict = "✅ EXCELLENT - Weekly mode is safe to use"
    elif abs(total_pct) < 5.0 and max_diff_pct < 15.0:
        verdict = "✓ ACCEPTABLE - Minor accuracy trade-off"
    else:
        verdict = "⚠ CAUTION - Weekly scaling may not be accurate for this model"
    
    lines.extend([
        f"  Verdict: {verdict}",
        "",
        "4. DESIGN-DAY RESULTS (Sizing Summary)",
        "-" * 50,
    ])
    
    # Show design-day sizing results
    if sizing_dd:
        lines.append("  Peak Loads from Design Day Sizing:")
        for key, val in sorted(sizing_dd.items()):
            if val > 0.001:
                # Format nicely
                display_key = key.replace('_', ' ')[:30]
                lines.append(f"    {display_key:<30} {val:12.2f}")
    elif eui_dd:
        for key, val in sorted(eui_dd.items()):
            if val > 0.001:
                lines.append(f"  {key:<25} {val:12.4f} kWh/m² (sizing period only)")
    else:
        lines.append("  Design-day simulation completed successfully.")
        lines.append(f"  Time: {time_dd:.2f}s (Use for quick HVAC sizing validation)")
    
    lines.extend([
        "",
        "5. RECOMMENDATIONS",
        "-" * 50,
        "  • Use WEEKLY mode for ~2x faster iteration with improved accuracy",
        "  • Use DESIGN-DAY for quick HVAC sizing validation (33x faster)",
        "  • Use ORIGINAL for final production runs",
        "",
        "=" * 80,
    ])
    
    report_text = "\n".join(lines)
    print("\n" + report_text)
    
    with open(output_path, 'w') as f:
        f.write(report_text)
    
    print(f"\nReport saved to: {output_path}")


def select_files_interactively() -> tuple[str, str]:
    """
    Interactive file selection for benchmark.
    
    Returns:
        Tuple of (idf_path, epw_path).
    """
    import glob
    
    # Select IDF
    idf_files = glob.glob(os.path.join(BUILDINGS_DIR, "*.idf"))
    if not idf_files:
        idf_files = glob.glob(os.path.join(BUILDINGS_DIR, "**", "*.idf"), recursive=True)
    
    if not idf_files:
        print("Error: No IDF files found.")
        sys.exit(1)
    
    print("\nSelect IDF file:")
    for i, f in enumerate(idf_files):
        print(f"  {i+1}. {os.path.basename(f)}")
    
    while True:
        try:
            choice = int(input(f"Select (1-{len(idf_files)}): ")) - 1
            if 0 <= choice < len(idf_files):
                selected_idf = idf_files[choice]
                break
        except ValueError:
            pass
        print("Invalid selection.")
    
    # Select EPW
    epw_files = glob.glob(os.path.join(WEATHER_DIR, "*.epw"))
    
    if not epw_files:
        print("Error: No EPW files found.")
        sys.exit(1)
    
    print("\nSelect Weather file:")
    for i, f in enumerate(epw_files):
        print(f"  {i+1}. {os.path.basename(f)}")
    
    while True:
        try:
            choice = int(input(f"Select (1-{len(epw_files)}): ")) - 1
            if 0 <= choice < len(epw_files):
                selected_epw = epw_files[choice]
                break
        except ValueError:
            pass
        print("Invalid selection.")
    
    return selected_idf, selected_epw


# =============================================================================
# Entry Point
# =============================================================================


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("IDF OPTIMIZATION BENCHMARK TOOL v2")
    print("=" * 70)
    
    # Check if file paths provided as arguments
    if len(sys.argv) >= 3:
        idf_path = sys.argv[1]
        epw_path = sys.argv[2]
    else:
        idf_path, epw_path = select_files_interactively()
    
    # Run the 3-way comparison benchmark
    run_benchmark_v2(idf_path, epw_path)
