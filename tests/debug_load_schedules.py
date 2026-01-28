
import os
import sys
# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bem_utils import integration

def debug_load():
    csv_path = "BEM_Setup/BEM_Schedules_2005.csv"
    print("Loading schedules...")
    all_schedules = integration.load_schedules(csv_path)
    
    hh_id = "61274"
    if hh_id in all_schedules:
        data = all_schedules[hh_id]
        print(f"\n--- HH {hh_id} ---")
        print(f"Keys: {data.keys()}")
        
        if 'Weekend' in data:
            print(f"Weekend entries count: {len(data['Weekend'])}")
            print("First 5 entries:")
            for e in data['Weekend'][:5]:
                print(e)
                
            # Check transformed list logic
            hours_map = {x['hour']: x['occ'] for x in data['Weekend']}
            occ_list = [hours_map.get(h, 0.0) for h in range(24)]
            print(f"\nTransformed 0-24 list: {occ_list}")
        else:
            print("MISSING 'Weekend' key!")
    else:
        print(f"HH {hh_id} NOT FOUND!")

if __name__ == "__main__":
    debug_load()
