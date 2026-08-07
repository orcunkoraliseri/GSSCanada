#!/usr/bin/env python3
"""Non-interactive test script for the BEM pipeline."""
import os
import sys
import shutil
import platform

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from eSim_bem_utils import integration, simulation

def test_pipeline():
    print("=" * 60)
    print("BEM Pipeline Test")
    print("=" * 60)
    
    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    bem_setup = os.path.join(base_dir, "BEM_Setup")
    schedule_csv = os.path.join(bem_setup, "BEM_Schedules_2025.csv")
    base_idf = os.path.join(bem_setup, "Buildings", 
                            "5A_DetachedHouse_gasfurnace_unheatedbsmt_IECC_2024.idf")
    
    # Find first EPW
    weather_dir = os.path.join(bem_setup, "WeatherFile")
    epw_files = [f for f in os.listdir(weather_dir) if f.endswith('.epw')]
    if not epw_files:
        print("ERROR: No EPW files found!")
        return False
    epw_path = os.path.join(weather_dir, epw_files[0])
    
    # Set IDD - Cross-platform EnergyPlus paths
    if platform.system() == 'Darwin':  # macOS
        idd_path = "/Applications/EnergyPlus-24-2-0/Energy+.idd"
        ep_dir = "/Applications/EnergyPlus-24-2-0"
    elif platform.system() == 'Windows':
        idd_path = r"C:\EnergyPlusV24-2-0\Energy+.idd"
        ep_dir = r"C:\EnergyPlusV24-2-0"
    else:  # Linux
        idd_path = "/usr/local/EnergyPlus-24-2-0/Energy+.idd"
        ep_dir = "/usr/local/EnergyPlus-24-2-0"
    
    if not os.path.exists(idd_path):
        print(f"ERROR: IDD not found at {idd_path}")
        return False
    os.environ["IDD_FILE"] = idd_path
    
    print(f"Schedule: {os.path.basename(schedule_csv)}")
    print(f"IDF: {os.path.basename(base_idf)}")
    print(f"EPW: {os.path.basename(epw_path)}")
    print()
    
    # 1. Load schedules
    print("[1/4] Loading schedules...")
    schedules = integration.load_schedules(schedule_csv)
    first_hh = list(schedules.keys())[0]
    print(f"      Testing with HH ID: {first_hh}")
    
    # 2. Setup output
    print("[2/4] Setting up output directory...")
    test_dir = os.path.join(base_dir, "Pipeline_Test_Output")
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    
    hh_idf_path = os.path.join(test_dir, f"HH_{first_hh}.idf")
    
    # 3. Inject schedules
    print("[3/4] Injecting schedules into IDF...")
    integration.inject_schedules(base_idf, hh_idf_path, first_hh, schedules[first_hh])
    print("      IDF generated successfully!")
    
    # 4. Run simulation
    print("[4/4] Running EnergyPlus simulation...")
    result = simulation.run_simulation(hh_idf_path, epw_path, test_dir, ep_dir)
    
    print()
    print("=" * 60)
    if result['success']:
        print("TEST PASSED!")
        print(f"Output: {result['output_dir']}")
        
        # Check for output files
        sql_file = os.path.join(test_dir, "eplusout.sql")
        html_file = os.path.join(test_dir, "eplustbl.htm")
        if os.path.exists(sql_file):
            print(f"  ✓ eplusout.sql ({os.path.getsize(sql_file) / 1024:.1f} KB)")
        if os.path.exists(html_file):
            print(f"  ✓ eplustbl.htm ({os.path.getsize(html_file) / 1024:.1f} KB)")
        return True
    else:
        print("TEST FAILED!")
        print(f"Error: {result['message']}")
        return False

if __name__ == "__main__":
    success = test_pipeline()
    sys.exit(0 if success else 1)
