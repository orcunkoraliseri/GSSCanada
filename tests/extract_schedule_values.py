
import os
import sys
from eppy.modeleditor import IDF
# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bem_utils.config

# Define paths
sim_dir = "BEM_Setup/SimResults/Comparative_HH2p_1769592803"
idf_2005 = os.path.join(sim_dir, "2005", "Scenario_2005.idf")

def extract_schedule():
    print("=== Extracting Schedule Values ===")
    
    if not os.path.exists(idf_2005):
        print(f"2005 IDF not found: {idf_2005}")
        return
        
    IDF.setiddname(bem_utils.config.IDD_FILE)
    idf = IDF(idf_2005)
    
    # Target Schedule Name found from previous step
    sch_name = "Proj_LIGH_0_61274"
    
    print(f"Searching for Schedule: {sch_name}")
    
    # Try Schedule:Compact
    compacts = idf.idfobjects['SCHEDULE:COMPACT']
    target_sch = next((s for s in compacts if s.Name == sch_name), None)
    
    if target_sch:
        print("Found Schedule:Compact")
        # Print raw fields to see values
        # Compact schedule format: Name, Type, Field1, Field2...
        # We want to see the values "Until: HH:MM, Value"
        for field in target_sch.obj[3:]: 
            print(f"  {field}")
            
    else:
        print("Schedule not found in Schedule:Compact")

if __name__ == "__main__":
    extract_schedule()
