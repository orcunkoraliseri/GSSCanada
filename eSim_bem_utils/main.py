"""
BEM Integration & Simulation Tool - Main Entry Point.

Provides a menu-driven interface for:
1. Visualizing building models
2. Running simulations with custom schedules
3. Viewing performance results
"""
import os
import sys
import glob
import platform
import time
import csv

# Windows: reconfigure stdout/stderr to UTF-8 so Unicode characters (e.g. →, —) in
# integration.py verbose output do not raise charmap codec errors on cp1252 consoles.
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass  # reconfigure not available on older Python TextIOWrapper

# Add project root to path so eSim_bem_utils can be imported when running directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eSim_bem_utils import integration, simulation, plotting, visualizer, idf_optimizer, neighbourhood, config, reporting

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BEM_SETUP_DIR = os.path.join(BASE_DIR, "BEM_Setup")
BUILDINGS_DIR = os.path.join(BEM_SETUP_DIR, "Buildings")
WEATHER_DIR = os.path.join(BEM_SETUP_DIR, "WeatherFile")
SIM_RESULTS_DIR = os.path.join(BEM_SETUP_DIR, "SimResults")
PLOT_RESULTS_DIR = os.path.join(BEM_SETUP_DIR, "SimResults_Plotting")
NEIGHBOURHOODS_DIR = os.path.join(BEM_SETUP_DIR, "Neighbourhoods")

# Comparative simulation scenario configuration
# Order matters for plot legends (left-to-right chronological).
COMPARATIVE_YEARS = ('2005', '2010', '2015', '2022', '2025')
COMPARATIVE_SCENARIOS = COMPARATIVE_YEARS + ('Default',)

def _build_schedule_file_map() -> dict:
    """Return {year: BEM_Schedules_<year>.csv path} for all comparative years."""
    return {
        year: os.path.join(BEM_SETUP_DIR, f"BEM_Schedules_{year}.csv")
        for year in COMPARATIVE_YEARS
    }


# EnergyPlus Configuration from config module
ENERGYPLUS_DIR = config.ENERGYPLUS_DIR
ENERGYPLUS_EXE = config.ENERGYPLUS_EXE
IDD_FILE = config.IDD_FILE


def get_region_from_epw(epw_path: str) -> str:
    """
    Infers the region/province from the EPW filename.
    Mappings based on standard Canadian EPW naming (e.g., CAN_QC_Montreal).
    
    Returns:
        Region name (e.g., "Quebec", "Ontario") or None if not found.
    """
    filename = os.path.basename(epw_path).upper()
    
    # Map common codes/cities to Region Names matches 'PR' column in CSV
    # PR Mapping: Atlantic, Quebec, Ontario, Prairies, Alberta, BC
    
    mapping = {
        '_BC_': "BC",
        '_AB_': "Alberta",
        '_ON_': "Ontario",
        '_QC_': "Quebec",
        '_MB_': "Prairies", # Manitoba
        '_SK_': "Prairies", # Saskatchewan
        '_NB_': "Atlantic", # New Brunswick
        '_NS_': "Atlantic", # Nova Scotia
        '_PE_': "Atlantic", # PEI
        '_NL_': "Atlantic", # Newfoundland
    }
    
    # 1. Check for explicit Province Code (e.g. CAN_QC_...)
    for code, region in mapping.items():
        if code in filename:
            return region
            
    # 2. Fallback to major city names if code not explicit
    city_map = {
        'VANCOUVER': "BC",
        'VICTORIA': "BC",
        'CALGARY': "Alberta",
        'EDMONTON': "Alberta",
        'TORONTO': "Ontario",
        'OTTAWA': "Ontario",
        'MONTREAL': "Quebec",
        'QUEBEC': "Quebec",
        'WINNIPEG': "Prairies",
        'HALIFAX': "Atlantic",
        'MONCTON': "Atlantic"
    }
    
    for city, region in city_map.items():
        if city in filename:
            return region
            
    return None



def _sort_key_by_city(filepath: str) -> tuple:
    """Extract city name from filepath for consistent sorting.

    Recognizes Canadian city names in both IDF and EPW filenames
    so that files for the same city get the same sort position.

    Args:
        filepath: Full or basename path to an IDF or EPW file.

    Returns:
        Tuple of (city_name, basename) for stable sorting.
        Files without a recognized city sort after those with one.
    """
    basename = os.path.basename(filepath).upper()
    cities = [
        'CALGARY', 'EDMONTON', 'HALIFAX', 'MONTREAL', 'MONCTON',
        'OTTAWA', 'QUEBEC', 'TORONTO', 'VANCOUVER', 'VICTORIA',
        'WINNIPEG',
    ]
    for city in cities:
        if city in basename:
            return (0, city, basename)
    return (1, '', basename)


def select_file(files: list, prompt_text: str) -> str:
    """Display file selection menu and return selected file path."""
    print(f"\n{prompt_text}")
    for i, f in enumerate(files):
        print(f"  {i+1}. {os.path.basename(f)}")
    
    while True:
        try:
            choice = input(f"Select number (1-{len(files)}): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(files):
                return files[idx]
        except ValueError:
            pass
        print("Invalid selection. Try again.")


def select_simulation_mode() -> str:
    """
    Display simulation mode sub-menu and return selected mode.
    
    Returns:
        str: Selected mode ('standard', 'weekly', or 'comparison')
    """
    print("\n[Simulation Mode Selection]")
    print("  1. Standard Simulation (full year)")
    print("  2. Fast Simulation (24 TMY weeks, ~2.5x faster)")
    print("  3. Comparison Mode (runs Standard + Fast, generates report)")
    
    sim_modes = ['standard', 'weekly', 'comparison']
    mode_names = {
        'standard': 'Standard (Full Year)',
        'weekly': 'Fast (24 TMY Weeks)',
        'comparison': 'Comparison Mode'
    }
    
    while True:
        try:
            mode_choice = input("Select mode (1-3): ").strip()
            mode_idx = int(mode_choice) - 1
            if 0 <= mode_idx < len(sim_modes):
                selected_mode = sim_modes[mode_idx]
                print(f"\nSelected Mode: {mode_names[selected_mode]}")
                return selected_mode
        except ValueError:
            pass
        print("Invalid selection. Try again.")


def _run_simulations_with_fallback(jobs: list, ep_path: str) -> dict:
    """Run simulations via ProcessPoolExecutor; fall back to sequential on Windows crash.

    ProcessPoolExecutor is known to deadlock or raise BrokenProcessPool on Windows
    when child processes fail to spawn (Task 26 / Session 7 known issue). This
    wrapper catches any such exception and re-runs all jobs one-at-a-time using
    simulation.run_simulation() so the Monte Carlo loop can complete without manual
    intervention. The return format matches run_simulations_parallel().
    """
    try:
        return simulation.run_simulations_parallel(jobs, ep_path)
    except Exception as e:
        print(f"\n[WARN] ProcessPoolExecutor failed ({type(e).__name__}: {e}).")
        print("[WARN] Falling back to sequential single-process execution (Windows fallback).")

        successful = []
        failed = []
        start = time.time()
        for i, job in enumerate(jobs, 1):
            name = job.get('name', os.path.basename(job['idf']))
            print(f"  [{i}/{len(jobs)}] Running {name} sequentially...")
            result = simulation.run_simulation(
                idf_path=job['idf'],
                epw_path=job['epw'],
                output_dir=job['output_dir'],
                ep_path=ep_path,
                n_jobs=1,
                quiet=True
            )
            if result['success']:
                successful.append(result)
                print(f"  [{i}/{len(jobs)}] [OK] {name}")
            else:
                failed.append(result)
                print(f"  [{i}/{len(jobs)}] [FAIL] {name}: {result.get('message', '')}")

        return {
            'successful': successful,
            'failed': failed,
            'total_time': time.time() - start
        }


def option_visualize_building() -> None:
    """Option 1: Visualize a building or neighbourhood model in 3D."""
    print("\n=== Visualize Building/Neighbourhood Model ===")
    
    # Collect IDF files from both buildings and neighbourhoods directories
    idf_files = []
    
    # Single buildings
    building_files = glob.glob(os.path.join(BUILDINGS_DIR, "*.idf"))
    if not building_files:
        building_files = glob.glob(os.path.join(BUILDINGS_DIR, "**", "*.idf"), recursive=True)
    idf_files.extend(building_files)
    
    # Neighbourhoods
    neighbourhood_files = glob.glob(os.path.join(NEIGHBOURHOODS_DIR, "*.idf"))
    idf_files.extend(neighbourhood_files)
    
    if not idf_files:
        print(f"Error: No IDF files found in {BUILDINGS_DIR} or {NEIGHBOURHOODS_DIR}")
        return
    
    selected_idf = select_file(idf_files, "Select IDF to visualize:")
    visualizer.visualize_idf(selected_idf)


def option_run_simulation() -> None:
    """Option 2: Run BEM simulations with schedule injection."""
    print("\n=== Run BEM Simulation ===")
    
    # 0. Select Simulation Mode
    selected_sim_mode = select_simulation_mode()
    
    # 1. Select Year / Schedule File
    schedule_files = glob.glob(os.path.join(BEM_SETUP_DIR, "BEM_Schedules_*.csv"))
    schedule_files.sort()
    if not schedule_files:
        print(f"Error: No schedule CSV files found in {BEM_SETUP_DIR}")
        return
    
    selected_schedule_csv = select_file(schedule_files, "Select Schedule File:")
    year_tag = os.path.basename(selected_schedule_csv).replace('.csv', '')
    
    # 2. Select Base IDF
    idf_files = glob.glob(os.path.join(BUILDINGS_DIR, "*.idf"))
    if not idf_files:
        idf_files = glob.glob(os.path.join(BUILDINGS_DIR, "**", "*.idf"), recursive=True)
    
    idf_files.sort(key=_sort_key_by_city)

    if not idf_files:
        print(f"Error: No IDF files found in {BUILDINGS_DIR}")
        return
        
    selected_idf = select_file(idf_files, "Select Base IDF Building Model:")
    
    # [AUTOMATION] Automatically prepare/optimize the selected IDF
    print(f"\nVerifying and preparing {os.path.basename(selected_idf)}...")
    idf_optimizer.prepare_idf_for_simulation(
        selected_idf, 
        verbose=True, 
        standardize_schedules=True
    )
    
    # 3. Select Dwelling Type Filter
    dwelling_types = ['SingleD', 'Attached', 'DuplexD', 'SemiD', 
                      'MidRise', 'HighRise', 'Movable', 'OtherA', 'All']
    print("\nSelect Dwelling Type for Schedule Filter:")
    for i, dt in enumerate(dwelling_types):
        print(f"  {i+1}. {dt}")
    
    while True:
        try:
            dt_choice = input(f"Select number (1-{len(dwelling_types)}): ").strip()
            dt_idx = int(dt_choice) - 1
            if 0 <= dt_idx < len(dwelling_types):
                selected_dtype = dwelling_types[dt_idx]
                if selected_dtype == 'All':
                    selected_dtype = None
                break
        except ValueError:
            pass
        print("Invalid selection. Try again.")
    
    # 5. Load Schedules (region=None: all PRs visible to EPW auto-resolution, Task 27)
    schedules = integration.load_schedules(selected_schedule_csv, dwelling_type=selected_dtype, region=None)

    # 6. Simulation Settings — Auto-select 1 random household
    print(f"\nTotal Households found: {len(schedules)}")

    import random
    all_hh_ids = list(schedules.keys())
    hh_ids = random.sample(all_hh_ids, 1)

    print(f"Auto-selected household: {hh_ids[0]}")

    # Auto-select EPW from household PR (Task 27)
    hh_pr = integration.get_household_pr(schedules[hh_ids[0]])
    selected_epw = config.resolve_epw_path(hh_pr, WEATHER_DIR)
    selected_region = get_region_from_epw(selected_epw)
    print(f"  Auto-selected EPW for HH {hh_ids[0]} (PR='{hh_pr}'): {os.path.basename(selected_epw)}")
    
    # 7. Generate IDFs and Prepare Jobs
    jobs = []
    
    batch_name = f"Batch_{year_tag}_{selected_sim_mode}_{int(time.time())}"
    batch_dir = os.path.join(SIM_RESULTS_DIR, batch_name)
    if not os.path.exists(batch_dir):
        os.makedirs(batch_dir)
        
    print(f"Output Directory: {batch_dir}")
    print("\n[Applying Speed Optimizations]")
    
    modes_to_run = ['standard', 'weekly'] if selected_sim_mode == 'comparison' else [selected_sim_mode]
    
    for hh_id in hh_ids:
        hh_dir = os.path.join(batch_dir, f"HH_{hh_id}")
        if not os.path.exists(hh_dir):
            os.makedirs(hh_dir)
            
        for mode in modes_to_run:
            # Sub-directory to avoid output conflicts (eplusout.sql)
            if len(modes_to_run) > 1:
                run_dir = os.path.join(hh_dir, mode)
            else:
                run_dir = hh_dir
            os.makedirs(run_dir, exist_ok=True)
            
            suffix = f"_{mode}" if len(modes_to_run) > 1 else ""
            hh_idf_name = f"HH_{hh_id}{suffix}.idf"
            hh_idf_path = os.path.join(run_dir, hh_idf_name)
            
            try:
                integration.inject_schedules(
                    selected_idf, hh_idf_path, hh_id, schedules[hh_id],
                    epw_path=selected_epw,
                    run_period_mode=mode
                )
                
                # Export schedule for debugging
                integration.export_schedule_csv(
                    schedules[hh_id], hh_id, year_tag, 
                    SIM_RESULTS_DIR, batch_name=batch_name
                )
                
                job_name = f"HH_{hh_id}{suffix}"
                jobs.append({
                    'idf': hh_idf_path,
                    'epw': selected_epw,
                    'output_dir': run_dir,
                    'name': job_name,
                    'mode': mode # for post-processing
                })
            except Exception as e:
                print(f"Error preparing HH {hh_id} (Mode: {mode}): {e}")
            
    # 8. Run Simulations
    if not jobs:
        print("No jobs generated.")
        return
    
    # Show expected speedup
    speedup_info = {
        'standard': '1.0x (baseline)',
        'weekly': '~2.5x faster',
        'comparison': 'runs Standard + Fast, generates report'
    }
    print(f"\nExpected Speedup: {speedup_info[selected_sim_mode]}")
        
    confirm = input(f"Ready to run {len(jobs)} simulations. Proceed? (y/n): ")
    if confirm.lower() != 'y':
        print("Aborted.")
        return
        
    results = simulation.run_simulations_parallel(jobs, ENERGYPLUS_EXE)
    
    # 9. Plot Results and/or Comparative Report
    if results['successful']:
        print("\nGenerating Plots...")
        
        if selected_sim_mode == 'comparison':
            # Group results by HH and Compare
            hh_results = {}
            for res in results['successful']:
                name = res['name'] # e.g. HH_1_standard
                parts = name.split('_')
                if len(parts) >= 3:
                    mode = parts[-1]
                    hh_id = '_'.join(parts[1:-1])
                    if hh_id not in hh_results: hh_results[hh_id] = {}
                    hh_results[hh_id][mode] = res
            
            for hh_id, modes in hh_results.items():
                if 'standard' in modes and 'weekly' in modes:
                    print(f"  Generating Comparison Report for HH {hh_id}...")
                    
                    std_eui = plotting.process_single_result(modes['standard']['output_dir'], scaling_factor=1.0)
                    fast_eui = plotting.process_single_result(modes['weekly']['output_dir'], scaling_factor=52.0/24.0)
                    
                    comparison_data = {
                        'Standard (Full Year)': std_eui,
                        'Fast (24 Weeks)': fast_eui
                    }
                    
                    plotting.plot_comparative_eui(
                        comparison_data, f"{hh_id}_Val", PLOT_RESULTS_DIR, 
                        idf_name=os.path.basename(selected_idf)
                    )
        else:
            scaling_factor = 52.0 / 24.0 if selected_sim_mode == 'weekly' else 1.0
            try:
                plotting.plot_eui_histogram(
                    results['successful'], 
                    title=f"EUI_Distribution_{year_tag}_{selected_sim_mode}",
                    output_dir=PLOT_RESULTS_DIR,
                    scaling_factor=scaling_factor
                )
            except Exception as e:
                print(f"Error generating plot: {e}")
            
    print("\nSimulation complete.")



def option_validation_simulation() -> None:
    """Option 9: Run validation simulation against reference data (Refactored Flow)."""
    import sqlite3
    
    print("\n=== Validation Simulation ===")
    print("Simulates existing IDFs and compares EUI against IECC reference values.")
    
    # 0. Select Simulation Mode
    selected_sim_mode = select_simulation_mode()

    # 1. Load Reference Data
    ref_csv_path = os.path.join(BEM_SETUP_DIR, "Reference-Validation", "IECC_residential_simulation_results_Canadian_Cities.csv")
    if not os.path.exists(ref_csv_path):
        print(f"Error: Validation CSV not found at {ref_csv_path}")
        return
    
    ref_data = {} # Key: ASHRAE Zone (str), Value: 2021 Standard EUI (float)
    try:
        with open(ref_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                zone = row['ASHRAE Zone'].strip().upper()
                try:
                    eui = float(row['2021 Standard (kWh/m2)'])
                    ref_data[zone] = eui
                except ValueError:
                    pass
    except Exception as e:
        print(f"Error reading validation CSV: {e}")
        return
        
    print(f"Loaded reference data for zones: {', '.join(ref_data.keys())}")
    
    # 2. Select Base IDF Building Model
    idf_files = glob.glob(os.path.join(BUILDINGS_DIR, "*.idf"))
    if not idf_files:
        print(f"Error: No IDF files found in {BUILDINGS_DIR}")
        return

    # Filter for those with CZ indicators (optional, but helpful to highlight validation targets)
    # But user wants to SELECT. So show ALL, maybe sort?
    idf_files.sort(key=_sort_key_by_city)
    selected_idf = select_file(idf_files, "Select Base IDF Building Model:")
    name = os.path.basename(selected_idf).replace('.idf', '')
    
    # Detect Zone from filename for reference lookup
    detected_zone = None
    for zone in ref_data.keys():
        if f"CZ{zone}" in name.upper() or f" {zone} " in name.upper():
            detected_zone = zone
            break
            
    if detected_zone:
        print(f"Detected Climate Zone: {detected_zone} (Reference EUI: {ref_data[detected_zone]} kWh/m2)")
    else:
        print("Warning: Could not detect Climate Zone (CZ) from filename. Reference comparison may be unavailable.")
    
    # 3. Prepare Job
    batch_name = f"Validation_{int(time.time())}"
    batch_dir = os.path.join(SIM_RESULTS_DIR, batch_name)
    os.makedirs(batch_dir, exist_ok=True)
    
    run_dir = os.path.join(batch_dir, name)
    os.makedirs(run_dir, exist_ok=True)
    
    print(f"\n[Critical Step] Optimizing IDF in-place at {run_dir}...")
    run_idf_path = os.path.join(run_dir, os.path.basename(selected_idf))
    
    try:
        # Prepare IDF (Speed optimize but DO NOT standardize schedules - Validation needs original schedules)
        # However, user prompt said "Version updated to 24.2. Physics optimizations applied."
        # This matches `prepare_idf_for_simulation` with `standardize_schedules=False`.
        
        idf_optimizer.prepare_idf_for_simulation(
            idf_path=selected_idf,
            output_path=run_idf_path,
            verbose=True,
            standardize_schedules=False, 
            run_period_mode=selected_sim_mode if selected_sim_mode != 'comparison' else 'standard'
        )
        
        # 4. Auto-detect Weather File (EPW)
        epw_files = glob.glob(os.path.join(WEATHER_DIR, "*.epw"))
        target_epw = None
        
        # Mapping logic
        zone_epw_map = {
            '5A': ['TORONTO', 'BUFFALO', 'ON'],
            '5C': ['VANCOUVER', 'VICTORIA', 'BC'],
            '6A': ['MONTREAL', 'OTTAWA', 'QUEBEC', 'QC'],
            '7':  ['CALGARY', 'EDMONTON', 'WINNIPEG', 'AB', 'MB'],
            '8':  ['YELLOWKNIFE']
        }
        
        search_terms = []
        if detected_zone:
            search_terms = zone_epw_map.get(detected_zone, [])
        
        # Also try to match city name from IDF name?
        city_map = {'TORONTO': 'TORONTO', 'VANCOUVER': 'VANCOUVER', 'MONTREAL': 'MONTREAL', 'CALGARY': 'CALGARY'}
        for city in city_map:
            if city in name.upper():
                search_terms.insert(0, city)
        
        if search_terms:
            for epw in epw_files:
                epw_base = os.path.basename(epw).upper()
                if any(term in epw_base for term in search_terms):
                    target_epw = epw
                    break
        
        if not target_epw and epw_files:
            target_epw = epw_files[0]
            print(f"Warning: Could not auto-detect EPW. Using fallback: {os.path.basename(target_epw)}")
        elif target_epw:
            print(f"Auto-selected Weather File: {os.path.basename(target_epw)}")
        else:
            print("Error: No EPW files found.")
            return

        # 5. Run 1 Simulation
        jobs = [{
            'idf': run_idf_path,
            'epw': target_epw,
            'output_dir': run_dir,
            'name': name,
            'zone': detected_zone
        }]
        
        print("\nStarting simulation...")
        results = simulation.run_simulations_parallel(jobs, ENERGYPLUS_EXE)
        
        # 6-8. Process Results
        if results['successful']:
            print("\n=== Validation Results ===")
            
            sql_path = os.path.join(run_dir, 'eplusout.sql')
            if os.path.exists(sql_path):
                conn = sqlite3.connect(sql_path)
                eui_data = plotting.calculate_eui(conn)
                conn.close()
                
                # Scaling if Fast Mode
                factor = 52.0/24.0 if selected_sim_mode == 'weekly' else 1.0
                if factor != 1.0:
                    eui_data = plotting.scale_eui_results(eui_data, factor)
                
                sim_eui = eui_data.get('eui', 0)
                ref_eui = ref_data.get(detected_zone, 0)
                
                print(f"Model:     {name}")
                print(f"Zone:      {detected_zone}")
                print(f"Sim EUI:   {sim_eui:.2f} kWh/m2")
                print(f"Ref EUI:   {ref_eui:.2f} kWh/m2")
                
                if ref_eui > 0:
                    diff = (sim_eui - ref_eui) / ref_eui * 100
                    print(f"Diff %:    {diff:+.1f}%")
                else:
                    print("Diff %:    N/A (No Ref)")
                
                # Plot Bar Chart
                print("\nGenerating Validation Comparison Plot...")
                try:
                    plotting.plot_validation_comparison(
                        sim_eui, ref_eui, PLOT_RESULTS_DIR, name, str(detected_zone)
                    )
                except Exception as pl_err:
                     print(f"Plotting Error: {pl_err}")

            else:
                print("Error: eplusout.sql not found.")
                
    except Exception as e:
        print(f"Error in validation workflow: {e}")
        import traceback
        traceback.print_exc()


def option_comparative_simulation() -> None:
    """Option 3: Run comparative simulation across 2025, 2015, 2005, and Default."""
    import random
    import sqlite3

    print("\n=== Comparative Simulation (6 Scenarios) ===")
    print("This will run 6 simulations for a randomly selected household:")
    for year in COMPARATIVE_YEARS:
        print(f"  - {year} Schedules")
    print("  - Default (No schedule injection)")

    # 0. Select Simulation Mode
    selected_sim_mode = select_simulation_mode()

    # 0b. Select Baseline Schedule Set (Task 23)
    print("\nSelect Baseline Schedule Set for Default scenario:")
    print("  1. MidRise  — DOE MidRise Apartment (default; existing runs unchanged)")
    print("  2. SF Detached — IECC SF Detached / HPXML BAHSP (robustness check only)")
    baseline_choice = input("Select (1-2, default=1): ").strip()
    selected_baseline = 'sf_detached' if baseline_choice == '2' else 'midrise'
    print(f"  Baseline: {selected_baseline}")

    # 1. Select Base IDF
    idf_files = glob.glob(os.path.join(BUILDINGS_DIR, "*.idf"))
    if not idf_files:
        idf_files = glob.glob(os.path.join(BUILDINGS_DIR, "**", "*.idf"), recursive=True)
    
    idf_files.sort(key=_sort_key_by_city)

    if not idf_files:
        print(f"Error: No IDF files found in {BUILDINGS_DIR}")
        return
        
    selected_idf = select_file(idf_files, "Select Base IDF Building Model:")

    # [AUTOMATION] Automatically prepare/optimize the selected IDF
    print(f"\nVerifying and preparing {os.path.basename(selected_idf)}...")
    idf_optimizer.prepare_idf_for_simulation(
        selected_idf, 
        verbose=True, 
        standardize_schedules=True
    )
    
    # 2. Select Dwelling Type Filter
    dwelling_types = ['SingleD', 'Attached', 'DuplexD', 'SemiD',
                      'MidRise', 'HighRise', 'Movable', 'OtherA', 'All']
    print("\nSelect Dwelling Type for Schedule Filter:")
    for i, dt in enumerate(dwelling_types):
        print(f"  {i+1}. {dt}")

    while True:
        try:
            dt_choice = input(f"Select number (1-{len(dwelling_types)}): ").strip()
            dt_idx = int(dt_choice) - 1
            if 0 <= dt_idx < len(dwelling_types):
                selected_dtype = dwelling_types[dt_idx]
                if selected_dtype == 'All':
                    selected_dtype = None
                break
        except ValueError:
            pass
        print("Invalid selection. Try again.")

    # 3. Load schedules from all years (region=None: all PRs visible to SSE matcher)
    schedule_files = _build_schedule_file_map()

    all_schedules = {}
    common_hh_ids = None

    for year, csv_path in schedule_files.items():
        if not os.path.exists(csv_path):
            print(f"Warning: {csv_path} not found, skipping {year}")
            continue

        schedules = integration.load_schedules(csv_path, dwelling_type=selected_dtype, region=None)
        all_schedules[year] = schedules

        hh_ids = set(schedules.keys())
        if common_hh_ids is None:
            common_hh_ids = hh_ids
        else:
            common_hh_ids = common_hh_ids.intersection(hh_ids)

    if not all_schedules:
        print("Error: No schedule files could be loaded.")
        return

    # 4. Randomly select one household from the first available year
    # But filtering for one that resembles "Standard Working Day"
    first_year = list(all_schedules.keys())[0]
    first_candidates = list(all_schedules[first_year].keys())

    first_hh = integration.find_best_match_household(all_schedules[first_year], first_candidates)
    target_hhsize = all_schedules[first_year][first_hh].get('metadata', {}).get('hhsize', 0)

    print(f"\nRandomly selected Household: {first_hh} (from {first_year})")
    print(f"  Matching by household size: {target_hhsize} persons")

    # 5. Auto-select EPW from household PR (Task 27)
    hh_pr = integration.get_household_pr(all_schedules[first_year][first_hh])
    selected_epw = config.resolve_epw_path(hh_pr, WEATHER_DIR)
    print(f"  Auto-selected EPW for HH {first_hh} (PR='{hh_pr}'): {os.path.basename(selected_epw)}")
    selected_region = get_region_from_epw(selected_epw)
    
    # 6. Prepare jobs for all 6 scenarios
    batch_name = f"Comparative_HH{target_hhsize}p_{int(time.time())}"
    batch_dir = os.path.join(SIM_RESULTS_DIR, batch_name)
    os.makedirs(batch_dir, exist_ok=True)
    print(f"Output Directory: {batch_dir}")

    jobs = []
    scenarios = list(COMPARATIVE_SCENARIOS)
    
    for scenario in scenarios:
        scenario_dir = os.path.join(batch_dir, scenario)
        os.makedirs(scenario_dir, exist_ok=True)
        
        idf_name = f"Scenario_{scenario}.idf"
        idf_path = os.path.join(scenario_dir, idf_name)
        
        try:
            if scenario == 'Default':
                # Optimize with selected baseline (midrise or sf_detached)
                idf_optimizer.prepare_idf_for_simulation(
                    selected_idf, idf_path, verbose=True,
                    run_period_mode=selected_sim_mode,
                    baseline=selected_baseline,
                )
            elif scenario in all_schedules:
                # Find a household with matching hhsize
                matching_hhs = [
                    hh_id for hh_id, data in all_schedules[scenario].items()
                    if data.get('metadata', {}).get('hhsize', 0) == target_hhsize
                ]
                
                if matching_hhs:
                    # Select the one that best matches standard working day
                    candidates = matching_hhs
                    year_hh = integration.find_best_match_household(all_schedules[scenario], candidates)
                else:
                    # Fallback to random if no exact match
                    year_hh = random.choice(list(all_schedules[scenario].keys()))
                    actual_size = all_schedules[scenario][year_hh].get('metadata', {}).get('hhsize', '?')
                    print(f"  Warning: No {target_hhsize}-person HH found in {scenario}, using {actual_size}-person")
                    
                print(f"  {scenario}: Using HH {year_hh} ({target_hhsize} persons)")
                integration.inject_schedules(
                    selected_idf, idf_path, year_hh,
                    all_schedules[scenario][year_hh],
                    epw_path=selected_epw,
                    sim_results_dir=SIM_RESULTS_DIR,
                    batch_name=batch_name,
                    run_period_mode=selected_sim_mode
                )
                
                # Export schedule for debugging
                integration.export_schedule_csv(
                    all_schedules[scenario][year_hh], year_hh, scenario,
                    SIM_RESULTS_DIR, batch_name=batch_name
                )
            else:
                print(f"  Skipping {scenario} - no schedules available")
                continue
            
            jobs.append({
                'idf': idf_path,
                'epw': selected_epw,
                'output_dir': scenario_dir,
                'name': scenario
            })
        except Exception as e:
            print(f"Error preparing {scenario}: {e}")
    
    if not jobs:
        print("No jobs generated.")
        return
    
    # 7. Run all 4 simulations in parallel
    confirm = input(f"\nReady to run {len(jobs)} simulations in parallel. Proceed? (y/n): ")
    if confirm.lower() != 'y':
        print("Aborted.")
        return
    
    results = simulation.run_simulations_parallel(jobs, ENERGYPLUS_EXE)
    
    # 8. Extract EUI results from each simulation
    print("\nExtracting results...")
    eui_results = {}
    
    for job in jobs:
        scenario = job['name']
        sql_path = os.path.join(job['output_dir'], 'eplusout.sql')
        
        if not os.path.exists(sql_path):
            print(f"  Warning: SQL file not found for {scenario}")
            continue
        
        try:
            conn = sqlite3.connect(sql_path)
            eui_data = plotting.calculate_eui(conn)
            conn.close()
            
            # Upscale results if Fast Simulation (24 weeks -> 52 weeks)
            scaling_factor = 52.0 / 24.0 if selected_sim_mode == 'weekly' else 1.0
            eui_data = plotting.scale_eui_results(eui_data, scaling_factor)
            
            eui_results[scenario] = eui_data
            
            # Generate individual breakdown plot
            plotting.plot_eui_breakdown(eui_data, 
                os.path.join(PLOT_RESULTS_DIR, f"Comparative_HH_{first_hh}_{scenario}.png"))
            
        except Exception as e:
            print(f"  Error extracting {scenario}: {e}")
    
    # 9a. Extract Time-Series Data (New Feature)
    print("\nExtracting time-series data (Meters)...")
    meter_results = {}
    
    for job in jobs:
        scenario = job['name']
        sql_path = os.path.join(job['output_dir'], 'eplusout.sql')
        
        try:
            conn = sqlite3.connect(sql_path)
            meter_data = plotting.get_meter_data(conn)
            conn.close()
            
            if meter_data:
                scaling_factor = 52.0 / 24.0 if selected_sim_mode == 'weekly' else 1.0
                meter_data = plotting.scale_meter_results(meter_data, scaling_factor)
                meter_results[scenario] = meter_data
        except Exception as e:
            print(f"  Error extracting meters for {scenario}: {e}")
            
    # 9. Generate comparative plots
    if eui_results:
        print("\nGenerating comparative EUI bar chart...")
        plotting.plot_comparative_eui(eui_results, first_hh, PLOT_RESULTS_DIR, 
            region=selected_region, idf_name=os.path.basename(selected_idf))
        
    if meter_results:
        print("Generating annual time-series plots (kWh/m²)...")
        # Get floor area from one of the results (should be same/similar for same building)
        floor_area = 0.0
        if eui_results:
            first_res = list(eui_results.values())[0]
            floor_area = first_res.get('conditioned_floor_area', 0.0) or first_res.get('total_floor_area', 0.0)
            
        planting_floor_area = floor_area if floor_area > 0 else 0.0
        
        plotting.plot_comparative_timeseries_subplots(
            meter_results, first_hh, PLOT_RESULTS_DIR, 
            floor_area=planting_floor_area,
            region=selected_region,
            idf_name=os.path.basename(selected_idf),
            sim_mode=selected_sim_mode
        )
    
    print("\nComparative simulation complete.")


def option_visualize_results() -> None:
    """Option 5: Visualize existing simulation results."""
    print("\n=== Visualize Performance Results ===")
    
    # Find batch folders (both standard batches and comparative runs)
    batch_dirs = glob.glob(os.path.join(SIM_RESULTS_DIR, "Batch_*")) + \
                 glob.glob(os.path.join(SIM_RESULTS_DIR, "Comparative_*"))
    
    batch_dirs = [d for d in batch_dirs if os.path.isdir(d)]
    
    if not batch_dirs:
        print(f"No simulation batches found in {SIM_RESULTS_DIR}")
        return
    
    # Sort by modification time (newest first)
    batch_dirs.sort(key=os.path.getmtime, reverse=True)
    
    print("\nAvailable Simulation Batches:")
    for i, d in enumerate(batch_dirs):
        print(f"  {i+1}. {os.path.basename(d)}")
    
    while True:
        try:
            choice = input(f"Select batch (1-{len(batch_dirs)}): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(batch_dirs):
                selected_batch = batch_dirs[idx]
                break
        except ValueError:
            pass
        print("Invalid selection. Try again.")
    
    # Find household directories in batch
    hh_dirs = [d for d in glob.glob(os.path.join(selected_batch, "HH_*")) 
               if os.path.isdir(d)]
    
    if not hh_dirs:
        print("No household results found in batch.")
        return
    
    print(f"\nFound {len(hh_dirs)} household results. Processing...")
    
    # Process each result
    simulation_results = [{'output_dir': d} for d in hh_dirs]
    
    batch_name = os.path.basename(selected_batch)
    year_tag = "_".join(batch_name.split("_")[1:-1])  # Extract year tag
    
    try:
        plotting.plot_eui_histogram(
            simulation_results, 
            title=f"EUI_Distribution_{year_tag}",
            output_dir=PLOT_RESULTS_DIR
        )
        print(f"\nPlots saved to: {PLOT_RESULTS_DIR}")
    except Exception as e:
        print(f"Error generating plots: {e}")


def option_neighbourhood_simulation() -> None:
    """Option 4: Run simulation with a neighbourhood IDF (multiple buildings)."""
    print("\n--- Neighbourhood Simulation ---")
    print("This option runs a simulation with per-building occupancy profiles.")
    
    # 0. Select Simulation Mode
    selected_sim_mode = select_simulation_mode()

    # 1. Select Neighbourhood IDF
    idf_files = glob.glob(os.path.join(NEIGHBOURHOODS_DIR, "*.idf"))
    idf_files.sort(key=_sort_key_by_city)
    if not idf_files:
        print(f"No IDF files found in {NEIGHBOURHOODS_DIR}")
        return

    print("\nAvailable Neighbourhood IDFs:")
    selected_idf = select_file(idf_files, "Select Neighbourhood IDF:")

    # 2. Detect number of buildings
    n_buildings = neighbourhood.get_num_buildings_from_idf(selected_idf)
    print(f"\nDetected {n_buildings} buildings in the neighbourhood.")

    if n_buildings == 0:
        print("Error: Could not detect buildings. Check IDF structure.")
        return

    # 3. Select Schedule CSV
    # schedule_dir = os.path.join(BASE_DIR, "Occupancy") # Old path
    schedule_dir = BEM_SETUP_DIR
    csv_files = glob.glob(os.path.join(schedule_dir, "BEM_Schedules_*.csv"))
    if not csv_files:
        print("No BEM schedule CSV files found.")
        return
    selected_csv = select_file(csv_files, "Select Schedule CSV:")

    # 4. Load and filter households (region=None: all PRs visible, Task 27)
    print(f"\nLoading households from CSV...")
    all_schedules = integration.load_schedules(selected_csv, region=None)

    # 5. Filter for Typical Working Day profile
    print("\nFiltering for households matching 'Typical Working Day' profile...")
    scored_matches = integration.filter_matching_households(all_schedules)
    
    if not scored_matches:
        print("Error: No valid households found matching the profile.")
        return

    sorted_hh_ids = [hh for hh, score in scored_matches]
    best_score = scored_matches[0][1]
    worst_selected_idx = min(len(scored_matches), n_buildings) - 1
    worst_score = scored_matches[worst_selected_idx][1]
    
    print(f"  Selected top matches from {len(scored_matches)} candidates.")
    print(f"  Score Range (SSE): {best_score:.4f} (Best) to {worst_score:.4f}")

    import random
    # Randomly sample from the top quarter of SSE-ranked candidates (Task 2)
    top_cut = max(n_buildings, len(sorted_hh_ids) // 4)
    sample_pool = sorted_hh_ids[:top_cut]
    print(f"  Sampling pool: {len(sample_pool)} candidates (top_cut={top_cut}) for {n_buildings} buildings.")
    if len(sample_pool) >= n_buildings:
        hh_ids = random.sample(sample_pool, n_buildings)
    else:
        hh_ids = [random.choice(sample_pool) for _ in range(n_buildings)]
    schedules_list = [{**all_schedules[hh_id], 'hh_id': hh_id} for hh_id in hh_ids]

    print(f"\nAssigned {n_buildings} randomized occupancy profiles to buildings.")

    # Auto-select EPW from dominant PR across selected households (Task 27)
    from collections import Counter
    pr_counts = Counter(
        integration.get_household_pr(all_schedules[hh_id]) for hh_id in hh_ids
    )
    dominant_pr = pr_counts.most_common(1)[0][0] if pr_counts else ''
    selected_epw = config.resolve_epw_path(dominant_pr, WEATHER_DIR)
    selected_region = get_region_from_epw(selected_epw)
    print(f"  Auto-selected EPW (dominant PR='{dominant_pr}'): {os.path.basename(selected_epw)}")

    # 6. Prepare the IDF (explode shared objects)
    run_id = f"Neighbourhood_{int(time.time())}"
    run_dir = os.path.join(SIM_RESULTS_DIR, run_id)
    os.makedirs(run_dir, exist_ok=True)

    prepared_idf_path = os.path.join(run_dir, "prepared.idf")
    print(f"\nPreparing neighbourhood IDF...")
    neighbourhood.prepare_neighbourhood_idf(selected_idf, prepared_idf_path, n_buildings)

    # 7. Inject schedules
    final_idf_path = os.path.join(run_dir, "neighbourhood_final.idf")
    print(f"\nInjecting schedules...")
    integration.inject_neighbourhood_schedules(
        prepared_idf_path, final_idf_path, schedules_list,
        original_idf_path=selected_idf, epw_path=selected_epw,
        run_period_mode=selected_sim_mode
    )
    
    # Export all used schedules for debugging
    for hh_schedule in schedules_list:
        hh_id = hh_schedule['hh_id']
        integration.export_schedule_csv(
            hh_schedule, str(hh_id), 'Neighbourhood',
            SIM_RESULTS_DIR, batch_name=run_id
        )

    # 8. Run simulation
    print(f"\nStarting EnergyPlus simulation...")
    result = simulation.run_simulation(
        idf_path=final_idf_path,
        epw_path=selected_epw,
        output_dir=run_dir,
        ep_path=ENERGYPLUS_DIR,
        quiet=True
    )

    # 9. Generate Plots
    if result.get('success', False):
        print("\nGenerating Neighbourhood Plots...")
        try:
            # Ensure plot directory exists
            os.makedirs(PLOT_RESULTS_DIR, exist_ok=True)
            
            # Process the simulation results and generate EUI breakdown plot
            scaling_factor = 52.0 / 24.0 if selected_sim_mode == 'weekly' else 1.0
            eui_results = plotting.process_single_result(
                output_dir=run_dir,
                plot_output_dir=PLOT_RESULTS_DIR,
                scaling_factor=scaling_factor
            )
            
            if eui_results:
                print(f"\n--- Neighbourhood Energy Summary ---")
                floor_area = eui_results.get('conditioned_floor_area') or eui_results.get('total_floor_area', 0)
                print(f"Total Floor Area: {floor_area:.1f} m²")
                print(f"Total EUI: {eui_results.get('eui', 0):.1f} kWh/m²-year")

                # Print breakdown by end-use (normalized per m²)
                end_uses = eui_results.get('end_uses_normalized') or eui_results.get('end_uses', {})
                if end_uses:
                    print("\nEnd-Use Breakdown (kWh/m²-year):")
                    for use, val in sorted(end_uses.items(), key=lambda x: -x[1]):
                        if val > 0.1:
                            print(f"  {use}: {val:.2f}")
                            
                print(f"\nPlot saved to: {PLOT_RESULTS_DIR}")
                            
        except Exception as e:
            print(f"Error generating plots: {e}")
    else:
        print(f"\nSimulation failed. Check error log in {run_dir}")

    print(f"\n{'='*60}")
    print(f"Neighbourhood simulation complete!")
    print(f"Results saved to: {run_dir}")
    print(f"{'='*60}")


def option_comparative_neighbourhood_simulation() -> None:
    """Option 5: Run comparative neighbourhood simulation (2025/2015/2005/Default)."""
    import random
    import sqlite3
    
    print("\n=== Comparative Neighbourhood Simulation (6 Scenarios) ===")
    print("This will run 6 parallel simulations for a neighbourhood:")
    for year in COMPARATIVE_YEARS:
        print(f"  - {year} Schedules")
    print("  - Default (No schedule injection)")
    
    # 0. Select Simulation Mode
    selected_sim_mode = select_simulation_mode()
    
    # 1. Select Neighbourhood IDF
    neighbourhood_files = glob.glob(os.path.join(NEIGHBOURHOODS_DIR, "*.idf"))
    neighbourhood_files.sort(key=_sort_key_by_city)
    if not neighbourhood_files:
        print(f"Error: No IDF files found in {NEIGHBOURHOODS_DIR}")
        return
    
    print("\nAvailable Neighbourhood IDFs:")
    selected_idf = select_file(neighbourhood_files, "\nSelect Neighbourhood IDF:")
    
    # 2. Get building count
    n_buildings = neighbourhood.get_num_buildings_from_idf(selected_idf)
    print(f"\nDetected {n_buildings} buildings in the neighbourhood.")
    
    # For neighbourhood simulations, we load all dwelling types (schedules from mixed buildings)
    selected_dtype = None

    # 3. Load schedules from all years (region=None: all PRs visible, Task 27)
    schedule_files = _build_schedule_file_map()

    all_schedules = {}
    for year, csv_path in schedule_files.items():
        if not os.path.exists(csv_path):
            print(f"Warning: {csv_path} not found, skipping {year}")
            continue

        schedules = integration.load_schedules(csv_path, dwelling_type=selected_dtype, region=None)
        if len(schedules) >= n_buildings:
            all_schedules[year] = schedules
            print(f"  {year}: Loaded {len(schedules)} households")
        else:
            print(f"  {year}: Only {len(schedules)} households (need {n_buildings}), skipping")

    if not all_schedules:
        print("Error: No schedule files with enough households could be loaded.")
        return

    # 6. Select households for consistency - match by hhsize AND profile
    first_year = list(all_schedules.keys())[0]
    first_schedules = all_schedules[first_year]
    
    # Filter for Typical Working Day profile
    print(f"\nFiltering {first_year} households for Typical Working Day profile...")
    scored_matches = integration.filter_matching_households(first_schedules)
    
    if not scored_matches:
        print("Error: No valid households found matching the profile.")
        return
        
    sorted_hh_ids = [hh for hh, score in scored_matches]
    best_score = scored_matches[0][1]
    worst_idx = min(len(scored_matches), n_buildings) - 1
    print(f"  Selected top matches from {len(scored_matches)} candidates.")
    print(f"  Score Range (SSE): {best_score:.4f} to {scored_matches[worst_idx][1]:.4f}")

    # Select n_buildings households (cycling top matches)
    base_hhs = []
    for i in range(n_buildings):
        base_hhs.append(sorted_hh_ids[i % len(sorted_hh_ids)])
    
    # Get hhsize profile for these base households
    hhsize_profile = []
    for hh_id in base_hhs:
        hhsize = first_schedules[hh_id].get('metadata', {}).get('hhsize', 2)
        hhsize_profile.append(hhsize)
    
    print(f"\nSelected {n_buildings} households from {first_year} (profile-filtered)")
    print(f"  Household sizes: {hhsize_profile[:5]}... (matching for other years)")

    # Auto-select EPW from dominant PR across base households (Task 27)
    from collections import Counter
    pr_counts = Counter(
        integration.get_household_pr(first_schedules[hh_id]) for hh_id in base_hhs
    )
    dominant_pr = pr_counts.most_common(1)[0][0] if pr_counts else ''
    selected_epw = config.resolve_epw_path(dominant_pr, WEATHER_DIR)
    selected_region = get_region_from_epw(selected_epw)
    print(f"  Auto-selected EPW (dominant PR='{dominant_pr}'): {os.path.basename(selected_epw)}")

    # 7. Create batch directory
    batch_name = f"Neighbourhood_Comparative_{int(time.time())}"
    batch_dir = os.path.join(SIM_RESULTS_DIR, batch_name)
    os.makedirs(batch_dir, exist_ok=True)
    print(f"\nOutput Directory: {batch_dir}")
    
    # 8. Prepare jobs for all 6 scenarios
    jobs = []
    scenarios = list(COMPARATIVE_SCENARIOS)

    for scenario in scenarios:
        scenario_dir = os.path.join(batch_dir, scenario)
        os.makedirs(scenario_dir, exist_ok=True)
        
        prepared_idf = os.path.join(scenario_dir, "prepared.idf")
        final_idf = os.path.join(scenario_dir, f"Scenario_{scenario}.idf")
        
        try:
            if scenario == 'Default':
                # Prepare neighbourhood (creates People/Lights/Equipment objects)
                # Then inject default residential schedules (no occupancy modification)
                print(f"\n  {scenario}: Preparing IDF with default residential schedules...")
                neighbourhood.prepare_neighbourhood_idf(selected_idf, prepared_idf, n_buildings)
                integration.inject_neighbourhood_default_schedules(prepared_idf, final_idf, n_buildings, verbose=True, run_period_mode=selected_sim_mode)
            elif scenario in all_schedules:
                # Find matching households by hhsize
                schedules_list = []
                year_schedules = all_schedules[scenario]
                
                # Filter this year's schedules by profile first
                print(f"    Filtering {scenario} candidates by profile...")
                scored_year_matches = integration.filter_matching_households(year_schedules)
                sorted_year_hhs = [hh for hh, s in scored_year_matches]
                
                used_hhs = set(s.get('hh_id') for s in schedules_list)

                for target_hhsize in hhsize_profile:
                    # Per-building SSE matching — same logic as single-building mode (Task 5)
                    size_candidates = [
                        hh for hh in sorted_year_hhs
                        if year_schedules[hh].get('metadata', {}).get('hhsize', 0) == target_hhsize
                        and hh not in used_hhs
                    ]

                    if size_candidates:
                        hh_id = integration.find_best_match_household(year_schedules, size_candidates)
                        data = year_schedules[hh_id]
                        used_hhs.add(hh_id)
                    else:
                        print(f"    Warning: No unused {target_hhsize}-person HH found in {scenario} matching profile.")
                        # Fallback: best SSE match regardless of hhsize
                        remaining = [hh for hh in sorted_year_hhs if hh not in used_hhs]
                        if remaining:
                            hh_id = integration.find_best_match_household(year_schedules, remaining)
                            data = year_schedules[hh_id]
                            used_hhs.add(hh_id)
                            print(f"      Fallback: Used {data.get('metadata', {}).get('hhsize')}p HH instead.")
                        else:
                            print(f"      Critical: No households left in {scenario}!")
                            continue

                    schedules_list.append({**data, 'hh_id': hh_id})
                
                print(f"\n  {scenario}: Preparing IDF and injecting {len(schedules_list)} schedules...")
                neighbourhood.prepare_neighbourhood_idf(selected_idf, prepared_idf, n_buildings)
                integration.inject_neighbourhood_schedules(
                    prepared_idf, final_idf, schedules_list,
                    original_idf_path=selected_idf, epw_path=selected_epw,
                    sim_results_dir=SIM_RESULTS_DIR,
                    batch_name=batch_name,
                    run_period_mode=selected_sim_mode
                )
                
                # Export all used schedules for debugging
                for sched in schedules_list:
                    hh_id = sched.get('hh_id', 'unknown')
                    integration.export_schedule_csv(
                        sched, str(hh_id), scenario,
                        SIM_RESULTS_DIR, batch_name=batch_name
                    )
            else:
                print(f"  Skipping {scenario} - no schedules available")
                continue
            
            jobs.append({
                'idf': final_idf,
                'epw': selected_epw,
                'output_dir': scenario_dir,
                'name': scenario
            })
            
        except Exception as e:
            print(f"Error preparing {scenario}: {e}")
            import traceback
            traceback.print_exc()
    
    if not jobs:
        print("No jobs generated.")
        return
    
    # 9. Run all simulations in parallel
    # confirm = input(f"\nReady to run {len(jobs)} simulations in parallel. Proceed? (y/n): ")
    confirm = 'y'
    if confirm.lower() != 'y':
        print("Aborted.")
        return
    
    print("\nStarting parallel simulations...")
    results = simulation.run_simulations_parallel(jobs, ENERGYPLUS_EXE)
    
    # 10. Extract EUI results
    print("\nExtracting results...")
    eui_results = {}
    
    for job in jobs:
        scenario = job['name']
        sql_path = os.path.join(job['output_dir'], 'eplusout.sql')
        
        if not os.path.exists(sql_path):
            print(f"  Warning: SQL file not found for {scenario}")
            continue
        
        try:
            conn = sqlite3.connect(sql_path)
            eui_data = plotting.calculate_eui(conn)
            
            # Upscale
            scaling_factor = 52.0 / 24.0 if selected_sim_mode == 'weekly' else 1.0
            eui_data = plotting.scale_eui_results(eui_data, scaling_factor)
            
            conn.close()
            
            eui_results[scenario] = eui_data
            print(f"  {scenario}: EUI = {eui_data.get('eui', 0):.1f} kWh/m²-year")
            
        except Exception as e:
            print(f"  Error extracting {scenario}: {e}")
    
    # 11. Generate comparative plots
    if eui_results:
        print("\nGenerating comparative plots...")
        os.makedirs(PLOT_RESULTS_DIR, exist_ok=True)
        
        # Generate individual breakdown for each scenario
        for scenario, eui_data in eui_results.items():
            plot_path = os.path.join(PLOT_RESULTS_DIR, f"Neighbourhood_{batch_name}_{scenario}_breakdown.png")
            plotting.plot_eui_breakdown(eui_data, plot_path)
        
        # Generate comparative bar chart
        plotting.plot_comparative_eui(
            eui_results, 
            f"Neighbourhood_{n_buildings}bldg", 
            PLOT_RESULTS_DIR,
            region=selected_region,
            idf_name=os.path.basename(selected_idf)
        )
    
    # 12. Extract and generate time-series plots
    print("\nExtracting time-series data (Meters)...")
    meter_results = {}
    
    for job in jobs:
        scenario = job['name']
        sql_path = os.path.join(job['output_dir'], 'eplusout.sql')
        
        try:
            conn = sqlite3.connect(sql_path)
            meter_data = plotting.get_meter_data(conn)
            conn.close()
            
            if meter_data:
                scaling_factor = 52.0 / 24.0 if selected_sim_mode == 'weekly' else 1.0
                meter_data = plotting.scale_meter_results(meter_data, scaling_factor)
                meter_results[scenario] = meter_data
        except Exception as e:
            print(f"  Error extracting meters for {scenario}: {e}")
    
    if meter_results:
        print("Generating monthly time-series plots (kWh/m²)...")
        # Get floor area from one of the results
        floor_area = 0.0
        if eui_results:
            first_res = list(eui_results.values())[0]
            floor_area = first_res.get('conditioned_floor_area', 0.0) or first_res.get('total_floor_area', 0.0)
        
        plotting.plot_comparative_timeseries_subplots(
            meter_results, 
            f"Neighbourhood_{n_buildings}bldg", 
            PLOT_RESULTS_DIR,
            floor_area=floor_area,
            region=selected_region,
            idf_name=os.path.basename(selected_idf),
            sim_mode=selected_sim_mode
        )
        
        print(f"\nPlots saved to: {PLOT_RESULTS_DIR}")
    
    print(f"\n{'='*60}")
    print(f"Comparative Neighbourhood Simulation complete!")
    print(f"Results saved to: {batch_dir}")
    print(f"{'='*60}")

def option_kfold_comparative_simulation() -> None:
    """Option 4: Monte Carlo Comparative Simulation.

    Samples N random households per scenario (Task 16: default N=20).
    Reports mean ± std EUI per end-use across the N samples, with error bars
    in the comparative bar chart so reviewer uncertainty is quantified.
    Raw per-sample values are also saved to CSV for post-hoc analysis.
    """
    import random
    import sqlite3
    import numpy as np

    print("\n=== Monte Carlo Comparative Simulation ===")
    print("Samples N households per scenario and reports mean ± std EUI.")
    print("Increase N for tighter confidence intervals (N=20 default, N=30 production).")
    
    # 0. Select Simulation Mode
    selected_sim_mode = select_simulation_mode()
    
    # 1. Select Base IDF
    idf_files = glob.glob(os.path.join(BUILDINGS_DIR, "*.idf"))
    if not idf_files:
        idf_files = glob.glob(os.path.join(BUILDINGS_DIR, "**", "*.idf"), recursive=True)
    
    idf_files.sort(key=_sort_key_by_city)

    if not idf_files:
        print(f"Error: No IDF files found in {BUILDINGS_DIR}")
        return
        
    selected_idf = select_file(idf_files, "Select Base IDF Building Model:")
    
    # 2. Select Weather File
    # TODO(Task 27 follow-up): replace interactive select with config.resolve_epw_path()
    #   using the dominant PR across sampled households, same pattern as Options 2/3/5/6.
    epw_files = glob.glob(os.path.join(WEATHER_DIR, "*.epw"))
    epw_files.sort(key=_sort_key_by_city)

    if not epw_files:
        print(f"Error: No EPW files found in {WEATHER_DIR}")
        return

    selected_epw = select_file(epw_files, "Select Weather File:")

    # 2b. Infer Region from Weather File
    selected_region = get_region_from_epw(selected_epw)
    if selected_region:
        print(f"\nDetected Region from Weather File: {selected_region}")
    else:
        print("\nRegion could not be inferred from Weather File (will load all regions).")
    
    # 3. Select Dwelling Type Filter
    dwelling_types = ['SingleD', 'Attached', 'DuplexD', 'SemiD', 
                      'MidRise', 'HighRise', 'Movable', 'OtherA', 'All']
    print("\nSelect Dwelling Type for Schedule Filter:")
    for i, dt in enumerate(dwelling_types):
        print(f"  {i+1}. {dt}")
    
    while True:
        try:
            dt_choice = input(f"Select number (1-{len(dwelling_types)}): ").strip()
            dt_idx = int(dt_choice) - 1
            if 0 <= dt_idx < len(dwelling_types):
                selected_dtype = dwelling_types[dt_idx]
                if selected_dtype == 'All':
                    selected_dtype = None
                break
        except ValueError:
            pass
        print("Invalid selection. Try again.")
    
    # 4. Select Monte Carlo sample size N (Task 16)
    # Each sample draws a different random household per scenario; mean ± std across N
    # gives the uncertainty interval shown in result bar charts.
    while True:
        try:
            k_input = input("\nEnter Monte Carlo sample size N (default=20, minimum=5): ").strip()
            if not k_input:
                iter_count = 20
            else:
                iter_count = int(k_input)
            if iter_count < 1:
                print("Sample size must be at least 1.")
                continue
            break
        except ValueError:
            print("Invalid number. Try again.")

    total_sims = 1 + iter_count * len(COMPARATIVE_YEARS)
    print(f"\nThis will run 1 Default + {iter_count} samples × "
          f"{len(COMPARATIVE_YEARS)} year scenarios = {total_sims} total simulations.")
    print(f"  Results will be reported as mean ± std across the {iter_count} samples.")
    confirm = input("Proceed? (y/n): ")
    if confirm.lower() != 'y':
        print("Aborted.")
        return
    
    # 5. Load schedules from all years
    schedule_files = _build_schedule_file_map()

    all_schedules = {}
    for year, csv_path in schedule_files.items():
        if not os.path.exists(csv_path):
            print(f"Warning: {csv_path} not found, skipping {year}")
            continue
        schedules = integration.load_schedules(csv_path, dwelling_type=selected_dtype, region=selected_region)
        all_schedules[year] = schedules

    if not all_schedules:
        print("Error: No schedule files could be loaded.")
        return

    # 6. Create output directory
    batch_name = f"MonteCarlo_N{iter_count}_{int(time.time())}"
    batch_dir = os.path.join(SIM_RESULTS_DIR, batch_name)
    os.makedirs(batch_dir, exist_ok=True)
    print(f"\nOutput Directory: {batch_dir}")
    
    # 7. Run Default simulation ONCE (it's the same for all iterations)
    print("\n--- Running Default Simulation (once) ---")
    default_dir = os.path.join(batch_dir, "Default")
    os.makedirs(default_dir, exist_ok=True)
    default_idf_path = os.path.join(default_dir, "Scenario_Default.idf")
    
    idf_optimizer.prepare_idf_for_simulation(
        selected_idf, default_idf_path, verbose=False,
        run_period_mode=selected_sim_mode,
        meter_frequency='Hourly'
    )
    
    default_job = {
        'idf': default_idf_path,
        'epw': selected_epw,
        'output_dir': default_dir,
        'name': 'Default'
    }
    _run_simulations_with_fallback([default_job], ENERGYPLUS_EXE)

    # Extract Default results
    default_eui_data = None
    default_meter_data = None
    default_hourly_data = None
    default_sql_path = os.path.join(default_dir, 'eplusout.sql')
    if os.path.exists(default_sql_path):
        try:
            conn = sqlite3.connect(default_sql_path)
            default_eui_data = plotting.calculate_eui(conn)
            default_meter_data = plotting.get_meter_data(conn)
            default_hourly_data = plotting.get_hourly_meter_data(conn)

            # Upscale
            scaling_factor = 52.0 / 24.0 if selected_sim_mode == 'weekly' else 1.0
            default_eui_data = plotting.scale_eui_results(default_eui_data, scaling_factor)

            if default_meter_data:
                default_meter_data = plotting.scale_meter_results(default_meter_data, scaling_factor)
            conn.close()
            print("  Default simulation complete.")
        except Exception as e:
            print(f"  Error extracting Default: {e}")
    
    # 8. Monte Carlo Loop (only year scenarios, not Default)
    year_scenarios = list(COMPARATIVE_YEARS)
    scenarios = list(COMPARATIVE_SCENARIOS)
    # Track full results for reporting
    all_run_results = {s: [] for s in scenarios}
    all_eui_results = {s: [] for s in scenarios}
    all_meter_results = {s: [] for s in scenarios}
    
    # Pre-populate Default results K times (same for all K - no variance)
    if default_eui_data:
        default_result = {
            'eui_data': default_eui_data,
            'meter_data': default_meter_data,
            'hourly_data': default_hourly_data
        }
        for _ in range(iter_count):
            all_eui_results['Default'].append(default_eui_data)
            if default_meter_data:
                all_meter_results['Default'].append(default_meter_data)
            all_run_results['Default'].append(default_result)
    
    # Pre-filter candidates by profile (like Option 7)
    candidate_pool = []
    pool_year = None
    for yr in all_schedules:
        if all_schedules[yr]:
            scored_matches = integration.filter_matching_households(
                all_schedules[yr]
            )
            if scored_matches:
                pool_year = yr
                pool_size = max(iter_count * 2, len(scored_matches) // 2)
                candidate_pool = [
                    hh for hh, s in scored_matches[:pool_size]
                ]
                break

    if not candidate_pool:
        print("\nError: No matching households found in any year. "
              "Try a different dwelling type or region.")
        return

    print(f"\nCandidate pool: {len(candidate_pool)} households "
          f"(from {pool_year}, {len(scored_matches)} profile-filtered)")
    
    for k in range(iter_count):
        print(f"\n--- Iteration {k+1}/{iter_count} ---")
        
        # Randomly select a household from the filtered pool
        first_hh = random.choice(candidate_pool)
        target_hhsize = all_schedules[pool_year][first_hh].get(
            'metadata', {}
        ).get('hhsize', 0)
        print(f"  Target household size: {target_hhsize} persons")
        
        # Prepare jobs for this iteration
        iter_dir = os.path.join(batch_dir, f"iter_{k+1}")
        os.makedirs(iter_dir, exist_ok=True)
        
        jobs = []
        for scenario in year_scenarios:  # Only 2025, 2015, 2005 (Default already done)
            scenario_dir = os.path.join(iter_dir, scenario)
            os.makedirs(scenario_dir, exist_ok=True)
            
            idf_name = f"Scenario_{scenario}.idf"
            idf_path = os.path.join(scenario_dir, idf_name)
            
            try:
                if scenario in all_schedules:
                    # Find a household with matching hhsize
                    matching_hhs = [
                        hh_id for hh_id, data in all_schedules[scenario].items()
                        if data.get('metadata', {}).get('hhsize', 0) == target_hhsize
                    ]
                    
                    if matching_hhs:
                        year_hh = random.choice(matching_hhs)
                    else:
                        year_hh = random.choice(list(all_schedules[scenario].keys()))
                    
                    hh_schedule = all_schedules[scenario][year_hh]
                    
                    integration.inject_schedules(
                        selected_idf, idf_path, year_hh,
                        hh_schedule,
                        epw_path=selected_epw,
                        sim_results_dir=SIM_RESULTS_DIR,
                        batch_name=f"{batch_name}/iter_{k+1}",
                        run_period_mode=selected_sim_mode,
                        output_frequency='Hourly'
                    )
                    
                    # Export schedule to CSV for debugging
                    integration.export_schedule_csv(
                        hh_schedule, str(year_hh), scenario,
                        SIM_RESULTS_DIR, batch_name=f"{batch_name}/iter_{k+1}"
                    )
                else:
                    continue
                
                jobs.append({
                    'idf': idf_path,
                    'epw': selected_epw,
                    'output_dir': scenario_dir,
                    'name': scenario
                })
            except Exception as e:
                print(f"    Error preparing {scenario}: {e}")
        
        if not jobs:
            print(f"  No jobs for iteration {k+1}, skipping.")
            continue
        
        # Run simulations for this iteration
        print(f"  Running {len(jobs)} simulations...")
        _run_simulations_with_fallback(jobs, ENERGYPLUS_EXE)

        # Extract EUI results
        for job in jobs:
            scenario = job['name']
            sql_path = os.path.join(job['output_dir'], 'eplusout.sql')
            
            if not os.path.exists(sql_path):
                continue
            
            try:
                conn = sqlite3.connect(sql_path)
                eui_data = plotting.calculate_eui(conn)
                
                # Upscale
                scaling_factor = 52.0 / 24.0 if selected_sim_mode == 'weekly' else 1.0
                eui_data = plotting.scale_eui_results(eui_data, scaling_factor)
                
                all_eui_results[scenario].append(eui_data)
                
                # Also extract meter data for time-series
                meter_data = plotting.get_meter_data(conn)
                if meter_data:
                    meter_data = plotting.scale_meter_results(meter_data, scaling_factor)
                    all_meter_results[scenario].append(meter_data)
                
                # Reporting: Extract hourly data if available
                # (Note: Requires ReportingFrequency=3 in output variables)
                hourly_data = plotting.get_hourly_meter_data(conn)
                
                # Helper dictionary for reporting
                run_result = {
                    'eui_data': eui_data,
                    'meter_data': meter_data,
                    'hourly_data': hourly_data
                }
                all_run_results[scenario].append(run_result)

                conn.close()
            except Exception as e:
                print(f"    Error extracting {scenario}: {e}")
    
    # 8. Aggregate results (mean ± std)
    print("\n=== Aggregating Results ===")
    
    # Get all end-use categories from the first valid result
    sample_result = None
    for s in scenarios:
        if all_eui_results[s]:
            sample_result = all_eui_results[s][0]
            break
    
    if not sample_result:
        print("Error: No valid results collected.")
        return
    
    # Use normalized end uses (kWh/m²) for proper EUI comparison
    end_uses = sample_result.get('end_uses_normalized', {})
    if not end_uses:
        # Fallback to raw end_uses if normalized not available
        end_uses = sample_result.get('end_uses', {})
    categories = list(end_uses.keys())
    
    aggregated = {'mean': {}, 'std': {}}
    
    for scenario in scenarios:
        results_list = all_eui_results[scenario]
        if not results_list:
            continue
            
        aggregated['mean'][scenario] = {}
        aggregated['std'][scenario] = {}
        
        for cat in categories:
            # Use end_uses_normalized for kWh/m² (same as single comparative)
            values = [r.get('end_uses_normalized', r.get('end_uses', {})).get(cat, 0.0) for r in results_list]
            aggregated['mean'][scenario][cat] = float(np.mean(values)) if values else 0.0
            aggregated['std'][scenario][cat] = float(np.std(values)) if len(values) > 1 else 0.0
            
    # 9. Generate Report (CSV)
    print("\nGenerating Detailed Report...")
    try:
        report_gen = reporting.ReportGenerator(all_run_results, batch_dir, region=selected_region or "Unknown")
        report_path = report_gen.generate_report()
    except Exception as e:
        print(f"Error generating report: {e}")

    
    # 9. Save aggregated CSV (mean ± std summary)
    csv_path = os.path.join(batch_dir, "aggregated_eui.csv")
    with open(csv_path, 'w') as f:
        f.write("EndUse," + ",".join([f"{s}_mean,{s}_std" for s in scenarios]) + "\n")
        for cat in categories:
            row = [cat]
            for s in scenarios:
                mean_val = aggregated['mean'].get(s, {}).get(cat, 0.0)
                std_val = aggregated['std'].get(s, {}).get(cat, 0.0)
                row.extend([f"{mean_val:.4f}", f"{std_val:.4f}"])
            f.write(",".join(row) + "\n")
    print(f"Saved aggregated CSV to: {csv_path}")

    # 9b. Save raw per-sample EUI CSV so the user can compute additional statistics (Task 16)
    raw_csv_path = os.path.join(batch_dir, "raw_samples_eui.csv")
    with open(raw_csv_path, 'w', newline='') as f:
        header = ["sample", "scenario"] + categories
        f.write(",".join(header) + "\n")
        for s in scenarios:
            for i, eui_data in enumerate(all_eui_results[s]):
                end_use_vals = eui_data.get('end_uses_normalized', eui_data.get('end_uses', {}))
                row = [str(i + 1), s] + [f"{end_use_vals.get(cat, 0.0):.4f}" for cat in categories]
                f.write(",".join(row) + "\n")
    print(f"Saved raw sample CSV to: {raw_csv_path}")

    # 10. Generate plot with error bars
    plot_path = os.path.join(PLOT_RESULTS_DIR, f"MonteCarlo_Comparative_EUI_{batch_name}.png")
    plotting.plot_kfold_comparative_eui(
        aggregated, categories, plot_path,
        K=iter_count, region=selected_region, idf_name=os.path.basename(selected_idf)
    )
    
    # 11. Aggregate meter data and generate time-series plot
    # Get meter names from sample
    sample_meter = None
    for s in scenarios:
        if all_meter_results[s]:
            sample_meter = all_meter_results[s][0]
            break
    
    if sample_meter:
        meter_names = list(sample_meter.keys())
        aggregated_meters = {'mean': {}, 'std': {}}
        
        for scenario in scenarios:
            meter_list = all_meter_results[scenario]
            if not meter_list:
                continue
            aggregated_meters['mean'][scenario] = {}
            aggregated_meters['std'][scenario] = {}
            
            for meter in meter_names:
                # Each meter has 12 monthly values
                all_values = [m.get(meter, [0]*12) for m in meter_list]
                # Stack: shape (K, 12)
                stacked = np.array(all_values)
                aggregated_meters['mean'][scenario][meter] = np.mean(stacked, axis=0).tolist()
                aggregated_meters['std'][scenario][meter] = np.std(stacked, axis=0).tolist() if len(stacked) > 1 else [0]*12
        
        # Get floor area from sample EUI result
        floor_area = sample_result.get('conditioned_floor_area', 0.0) or sample_result.get('total_floor_area', 0.0)
        
        ts_plot_path = os.path.join(PLOT_RESULTS_DIR, f"MonteCarlo_TimeSeries_{batch_name}.png")
        plotting.plot_kfold_timeseries(
            aggregated_meters, meter_names, ts_plot_path,
            floor_area=floor_area, K=iter_count, region=selected_region,
            idf_name=os.path.basename(selected_idf), sim_mode=selected_sim_mode
        )

    print(f"\nMonte Carlo Comparative Simulation complete. Results in: {batch_dir}")


def option_batch_comparative_neighbourhood_simulation() -> None:
    """Option 7: Monte Carlo Comparative Neighbourhood Simulation (runs iter_count iterations, averages results)."""
    import random
    import sqlite3
    import numpy as np

    print("\n=== Monte Carlo Comparative Neighbourhood Simulation ===")
    print("This runs comparative neighbourhood simulations multiple times with different random household sets,")
    print("then averages results to reduce selection bias.")
    
    # 0. Select Simulation Mode
    selected_sim_mode = select_simulation_mode()
    
    # 1. Select Neighbourhood IDF
    neighbourhood_files = glob.glob(os.path.join(NEIGHBOURHOODS_DIR, "*.idf"))
    neighbourhood_files.sort(key=_sort_key_by_city)
    if not neighbourhood_files:
        print(f"Error: No IDF files found in {NEIGHBOURHOODS_DIR}")
        return
    
    print("\nAvailable Neighbourhood IDFs:")
    selected_idf = select_file(neighbourhood_files, "\nSelect Neighbourhood IDF:")
    
    # 2. Get building count
    n_buildings = neighbourhood.get_num_buildings_from_idf(selected_idf)
    print(f"\nDetected {n_buildings} buildings in the neighbourhood.")
    
    if n_buildings == 0:
        print("Error: Could not detect buildings. Check IDF structure.")
        return

    # 3. Select Weather File
    # TODO(Task 27 follow-up): replace interactive select with config.resolve_epw_path()
    #   using dominant PR across selected neighbourhood households, same pattern as Options 5/6.
    epw_files = glob.glob(os.path.join(WEATHER_DIR, "*.epw"))
    epw_files.sort(key=_sort_key_by_city)

    if not epw_files:
        print(f"Error: No EPW files found in {WEATHER_DIR}")
        return

    selected_epw = select_file(epw_files, "Select Weather File:")
    
    # 3b. Infer Region from Weather File
    selected_region = get_region_from_epw(selected_epw)
    if selected_region:
        print(f"\nDetected Region from Weather File: {selected_region}")
    else:
        print("\nRegion could not be inferred from Weather File (will load all regions).")
    
    # 4. Select iteration count
    while True:
        try:
            k_input = input("\nEnter iteration count (iter_count=) (default=5): ").strip()
            if not k_input:
                iter_count = 5
            else:
                iter_count = int(k_input)
            if iter_count < 1:
                print("Iteration count must be at least 1.")
                continue
            break
        except ValueError:
            print("Invalid number. Try again.")

    total_sims = iter_count * len(COMPARATIVE_YEARS) + 1
    print(f"\nThis will run 1 Default + ({iter_count} iterations × "
          f"{len(COMPARATIVE_YEARS)} scenarios) = {total_sims} total simulations.")
    confirm = input("Proceed? (y/n): ")
    if confirm.lower() != 'y':
        print("Aborted.")
        return
    
    # 5. Load schedules from all years
    schedule_files = _build_schedule_file_map()

    all_schedules = {}
    # We load all dwelling types for neighbourhoods
    selected_dtype = None

    for year, csv_path in schedule_files.items():
        if not os.path.exists(csv_path):
            print(f"Warning: {csv_path} not found, skipping {year}")
            continue
        schedules = integration.load_schedules(csv_path, dwelling_type=selected_dtype, region=selected_region)
        if len(schedules) >= n_buildings:
            all_schedules[year] = schedules
            print(f"  {year}: Loaded {len(schedules)} households")
        else:
            print(f"  {year}: Only {len(schedules)} households (need {n_buildings}), skipping")

    if not all_schedules:
        print("Error: No schedule files could be loaded.")
        return
    
    # 6. Create output directory
    batch_name = f"MonteCarlo_Neighbourhood_N{iter_count}_{int(time.time())}"
    batch_dir = os.path.join(SIM_RESULTS_DIR, batch_name)
    os.makedirs(batch_dir, exist_ok=True)
    print(f"\nOutput Directory: {batch_dir}")
    
    # 7. Run Default simulation ONCE (it's the same for all iterations)
    print("\n--- Running Default Simulation (once) ---")
    default_dir = os.path.join(batch_dir, "Default")
    os.makedirs(default_dir, exist_ok=True)
    
    prepared_idf = os.path.join(default_dir, "prepared.idf")
    final_idf = os.path.join(default_dir, "Scenario_Default.idf")
    
    # Prepare neighbourhood with default logic
    neighbourhood.prepare_neighbourhood_idf(selected_idf, prepared_idf, n_buildings)
    integration.inject_neighbourhood_default_schedules(prepared_idf, final_idf, n_buildings, original_idf_path=selected_idf, verbose=False)
    
    default_job = {
        'idf': final_idf,
        'epw': selected_epw,
        'output_dir': default_dir,
        'name': 'Default'
    }
    simulation.run_simulations_parallel([default_job], ENERGYPLUS_EXE)
    
    # Extract Default results
    default_eui_data = None
    default_meter_data = None
    default_sql_path = os.path.join(default_dir, 'eplusout.sql')
    if os.path.exists(default_sql_path):
        try:
            conn = sqlite3.connect(default_sql_path)
            default_eui_data = plotting.calculate_eui(conn)
            default_meter_data = plotting.get_meter_data(conn)
            conn.close()
            print("  Default simulation complete.")
            print(f"  Default EUI: {default_eui_data.get('eui', 0):.1f} kWh/m²-year")
        except Exception as e:
            print(f"  Error extracting Default: {e}")
    
    # 8. Monte Carlo Loop (only year scenarios)
    year_scenarios = list(COMPARATIVE_YEARS)
    scenarios = list(COMPARATIVE_SCENARIOS)
    all_eui_results = {s: [] for s in scenarios}
    all_meter_results = {s: [] for s in scenarios}
    
    # Pre-populate Default results (same for all iterations)
    if default_eui_data:
        # Replicate Default result iter_count times so it has same weight/variance (std=0)
        # Or just append once and handle it?
        # For plot, we need list of values. Since Default is constant, we append it iter_count times.
        for _ in range(iter_count):
            all_eui_results['Default'].append(default_eui_data)
            all_meter_results['Default'].append(default_meter_data)

    first_year = list(all_schedules.keys())[0]

    # Pre-compute sorted household lists per scenario — identical every iteration (Task 3)
    print("\nPre-computing household rankings per scenario...")
    sorted_year_hhs_cache = {}
    for scenario in year_scenarios:
        if scenario not in all_schedules:
            continue
        sorted_year_hhs_cache[scenario] = [
            hh for hh, _ in integration.filter_matching_households(all_schedules[scenario])
        ]
        print(f"  {scenario}: {len(sorted_year_hhs_cache[scenario])} ranked candidates")

    # Pre-compute first_year candidate pool — identical every iteration (Task 3)
    first_schedules = all_schedules[first_year]
    first_year_scored = integration.filter_matching_households(first_schedules)
    pool_size = max(n_buildings * 2, len(first_year_scored) // 2)
    candidate_pool = [hh for hh, s in first_year_scored[:pool_size]]
    print(f"  Base year ({first_year}) pool: {len(candidate_pool)} candidates for hhsize sampling\n")

    for k in range(iter_count):
        print(f"\n--- Iteration {k+1}/{iter_count} ---")

        # Sample n_buildings distinct households from the pre-computed pool
        if len(candidate_pool) < n_buildings:
            print(f"  Warning: Candidate pool smaller than N ({len(candidate_pool)} < {n_buildings}). Using duplication.")
            base_hhs = [random.choice(candidate_pool) for _ in range(n_buildings)]
        else:
            base_hhs = random.sample(candidate_pool, n_buildings)
        
        # Get hhsize profile for matching
        hhsize_profile = []
        for hh_id in base_hhs:
            hhsize = first_schedules[hh_id].get('metadata', {}).get('hhsize', 2)
            hhsize_profile.append(hhsize)
            
        print(f"  Selected {n_buildings} households (Sizes: {hhsize_profile[:5]}...)")
        
        # Prepare jobs for this iteration
        iter_dir = os.path.join(batch_dir, f"iter_{k+1}")
        os.makedirs(iter_dir, exist_ok=True)
        
        jobs = []
        
        for scenario in year_scenarios:
            if scenario not in all_schedules:
                continue
                
            scenario_dir = os.path.join(iter_dir, scenario)
            os.makedirs(scenario_dir, exist_ok=True)
            
            prepared_idf = os.path.join(scenario_dir, "prepared.idf")
            final_idf = os.path.join(scenario_dir, f"Scenario_{scenario}.idf")
            
            try:
                # Find matching households logic (filtered by profile)
                schedules_list = []
                year_schedules = all_schedules[scenario]

                # Use pre-computed sorted list (Task 3)
                sorted_year_hhs = sorted_year_hhs_cache[scenario]

                used_hhs = set()

                for target_hhsize in hhsize_profile:
                    # Per-building SSE matching — same logic as single-building mode (Task 5)
                    size_candidates = [
                        hh for hh in sorted_year_hhs
                        if year_schedules[hh].get('metadata', {}).get('hhsize', 0) == target_hhsize
                        and hh not in used_hhs
                    ]

                    if size_candidates:
                        hh_id = integration.find_best_match_household(year_schedules, size_candidates)
                        data = year_schedules[hh_id]
                        used_hhs.add(hh_id)
                    else:
                        # Fallback: best SSE match regardless of hhsize
                        remaining = [hh for hh in sorted_year_hhs if hh not in used_hhs]
                        if remaining:
                            hh_id = integration.find_best_match_household(year_schedules, remaining)
                            data = year_schedules[hh_id]
                            used_hhs.add(hh_id)
                            print(f"      Fallback: Used {data.get('metadata', {}).get('hhsize')}p HH instead.")
                        else:
                            print(f"      Critical: No households left in {scenario}!")
                            continue

                    schedules_list.append({**data, 'hh_id': hh_id})
                
                neighbourhood.prepare_neighbourhood_idf(selected_idf, prepared_idf, n_buildings)
                integration.inject_neighbourhood_schedules(
                    prepared_idf, final_idf, schedules_list,
                    original_idf_path=selected_idf, epw_path=selected_epw,
                    sim_results_dir=SIM_RESULTS_DIR,
                    batch_name=f"{batch_name}/iter_{k+1}"
                )
                
                # Export all used schedules for debugging (Iter 1 only to save space, or all?)
                # User specifically asked for it, so let's export for all iters or just first?
                # Let's export for ALL to be safe, but organize by iter
                if k == 0: # Export only for first iteration to avoid spamming 100s of CSVs?
                    # Or maybe export for all but in subfolders?
                    # The user said "option 7 do not generate schedule... we can not see"
                    # Let's export for every iteration.
                    for sched in schedules_list:
                        hh_id = sched.get('hh_id', 'unknown')
                        integration.export_schedule_csv(
                            sched, str(hh_id), f"{scenario}_Iter{k+1}",
                            SIM_RESULTS_DIR, batch_name=batch_name
                        )

                jobs.append({
                    'idf': final_idf,
                    'epw': selected_epw,
                    'output_dir': scenario_dir,
                    'name': scenario
                })
                
            except Exception as e:
                print(f"    Error preparing {scenario}: {e}")
        
        if not jobs:
            print(f"  No jobs for iteration {k+1}, skipping.")
            continue
            
        # Run simulations
        simulation.run_simulations_parallel(jobs, ENERGYPLUS_EXE)
        
        # Extract EUI results
        for job in jobs:
            scenario = job['name']
            sql_path = os.path.join(job['output_dir'], 'eplusout.sql')
            
            if not os.path.exists(sql_path):
                continue
            
            try:
                conn = sqlite3.connect(sql_path)
                eui_data = plotting.calculate_eui(conn)
                all_eui_results[scenario].append(eui_data)
                
                meter_data = plotting.get_meter_data(conn)
                if meter_data:
                    all_meter_results[scenario].append(meter_data)
                conn.close()
            except Exception as e:
                print(f"    Error extracting {scenario}: {e}")
                
    # 9. Aggregate results (mean ± std)
    print("\n=== Aggregating Results ===")
    
    # Get all end-use categories from sample
    sample_result = None
    for s in scenarios:
        if all_eui_results[s]:
            sample_result = all_eui_results[s][0]
            break
            
    if not sample_result:
        print("Error: No valid results collected.")
        return
        
    end_uses = sample_result.get('end_uses_normalized', {}) or sample_result.get('end_uses', {})
    categories = list(end_uses.keys())
    
    aggregated = {'mean': {}, 'std': {}}
    
    for scenario in scenarios:
        results_list = all_eui_results[scenario]
        if not results_list:
            continue
            
        aggregated['mean'][scenario] = {}
        aggregated['std'][scenario] = {}
        
        for cat in categories:
            values = [r.get('end_uses_normalized', r.get('end_uses', {})).get(cat, 0.0) for r in results_list]
            aggregated['mean'][scenario][cat] = float(np.mean(values)) if values else 0.0
            aggregated['std'][scenario][cat] = float(np.std(values)) if len(values) > 1 else 0.0
            
    # 10. Save CSV
    csv_path = os.path.join(batch_dir, "aggregated_eui.csv")
    with open(csv_path, 'w') as f:
        f.write("EndUse," + ",".join([f"{s}_mean,{s}_std" for s in scenarios]) + "\n")
        for cat in categories:
            row = [cat]
            for s in scenarios:
                mean_val = aggregated['mean'].get(s, {}).get(cat, 0.0)
                std_val = aggregated['std'].get(s, {}).get(cat, 0.0)
                row.extend([f"{mean_val:.4f}", f"{std_val:.4f}"])
            f.write(",".join(row) + "\n")
    print(f"Saved aggregated CSV to: {csv_path}")
    
    # 11. Plot Monte Carlo EUI
    plot_path = os.path.join(PLOT_RESULTS_DIR, f"MonteCarlo_Neighbourhood_EUI_{batch_name}.png")
    plotting.plot_kfold_comparative_eui(
        aggregated, categories, plot_path,
        K=iter_count, region=selected_region, idf_name=os.path.basename(selected_idf)
    )
    
    # 12. Plot Monte Carlo Time-Series
    sample_meter = None
    for s in scenarios:
        if all_meter_results[s]:
            sample_meter = all_meter_results[s][0]
            break

    if sample_meter:
        meter_names = list(sample_meter.keys())
        aggregated_meters = {'mean': {}, 'std': {}}

        for scenario in scenarios:
            meter_list = all_meter_results[scenario]
            if not meter_list:
                continue
            aggregated_meters['mean'][scenario] = {}
            aggregated_meters['std'][scenario] = {}

            for meter in meter_names:
                all_values = [m.get(meter, [0]*12) for m in meter_list]
                stacked = np.array(all_values)
                aggregated_meters['mean'][scenario][meter] = np.mean(stacked, axis=0).tolist()
                aggregated_meters['std'][scenario][meter] = np.std(stacked, axis=0).tolist() if len(stacked) > 1 else [0]*12

        floor_area = sample_result.get('conditioned_floor_area', 0.0) or sample_result.get('total_floor_area', 0.0)

        ts_plot_path = os.path.join(PLOT_RESULTS_DIR, f"MonteCarlo_Neighbourhood_TimeSeries_{batch_name}.png")
        plotting.plot_kfold_timeseries(
            aggregated_meters, meter_names, ts_plot_path,
            floor_area=floor_area, K=iter_count, region=selected_region,
            idf_name=os.path.basename(selected_idf), sim_mode=selected_sim_mode
        )

    print(f"\nMonte Carlo Neighbourhood Simulation complete. Results in: {batch_dir}")


def main_menu() -> None:
    """Display main menu and handle user selection."""
    print("=" * 60)
    print(" BEM Integration & Simulation Tool")
    print("=" * 60)
    
    while True:
        print("\nOptions:")
        print("  1. Visualize a building")
        print("  2. Run a simulation, single building")
        print("  3. Comparative simulation, single building (2005/2010/2015/2022/2025/Default)")
        print("  4. Monte Carlo Comparative, single building (averaged over iterations) (2005/2010/2015/2022/2025/Default)")
        print("  5. Neighbourhood simulation (multi-building)")
        print("  6. Comparative neighbourhood (2005/2010/2015/2022/2025/Default)")
        print("  7. Batch Comparative Neighbourhood Simulation (Monte Carlo) (2005/2010/2015/2022/2025/Default)")
        print("  8. Visualize performance results")
        print("  9. Run Validation Simulation (Existing IDFs vs Reference)")
        print("  q. Quit")
        
        choice = input("\nSelect option: ").strip().lower()
        
        if choice == '1':
            option_visualize_building()
        elif choice == '2':
            option_run_simulation()
        elif choice == '3':
            option_comparative_simulation()
        elif choice == '4':
            option_kfold_comparative_simulation()
        elif choice == '5':
            option_neighbourhood_simulation()
        elif choice == '6':
            option_comparative_neighbourhood_simulation()
        elif choice == '7':
            option_batch_comparative_neighbourhood_simulation()
        elif choice == '8':
            option_visualize_results()
        elif choice == '9':
            option_validation_simulation()
        elif choice == 'q':
            print("\nGoodbye!")
            break
        else:
            print("Invalid option. Please select 1-8 or q.")


def main():
    """Main entry point."""
    main_menu()


if __name__ == "__main__":
    main()
