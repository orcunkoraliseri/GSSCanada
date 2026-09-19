
import os
import glob
import sys
from eppy.modeleditor import IDF
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BUILDINGS_DIR = os.path.join(BASE_DIR, "BEM_Setup", "Buildings")
# Setup IDD
IDD_FILE = "C:\\EnergyPlusV24-2-0\\Energy+.idd"
if not os.path.exists(IDD_FILE):
    print(f"Error: IDD not found at {IDD_FILE}")
    sys.exit(1)

IDF.setiddname(IDD_FILE)

def clean_duplicates(idf_path):
    print(f"Scanning {os.path.basename(idf_path)}...")
    try:
        idf = IDF(idf_path)
        
        # Check for duplicate names in Schedule:Compact
        schedules = idf.idfobjects['SCHEDULE:COMPACT']
        
        name_map = {} # Name -> [indices]
        duplicates_found = False
        
        # Collect indices of objects by name
        for i, sch in enumerate(schedules):
            name = sch.Name.upper()
            if "STANDARD_" in name: # Target only our generated schedules
                if name not in name_map:
                    name_map[name] = []
                name_map[name].append(sch)
        
        # Identify duplicates
        objects_to_remove = []
        for name, objs in name_map.items():
            if len(objs) > 1:
                print(f"  Found {len(objs)} copies of {name}. Removing duplicates...")
                duplicates_found = True
                # Keep the LAST one (arbitrary choice, or first? E+ normally keeps last loaded?)
                # Actually, usually safer to keep the last one if it overwrote earlier ones.
                # But here they are likely identical.
                # Remove all except the last one.
                objects_to_remove.extend(objs[:-1])
        
        if duplicates_found:
            for obj in objects_to_remove:
                idf.removeidfobject(obj)
            
            idf.saveas(idf_path)
            print(f"  [FIXED] Removed {len(objects_to_remove)} duplicate objects from {os.path.basename(idf_path)}")
        else:
            print("  No 'Standard_' duplicates found.")
            
    except Exception as e:
        print(f"  Error processing file: {e}")

def main():
    print("=== Cleaning IDF Duplicate Schedules ===")
    idf_files = glob.glob(os.path.join(BUILDINGS_DIR, "*.idf"))
    if not idf_files:
        print("No IDF files found.")
        return
        
    for f in idf_files:
        clean_duplicates(f)
        
    print("\nCleanup complete.")

if __name__ == "__main__":
    main()
