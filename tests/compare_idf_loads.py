
import os
import sys
from eppy.modeleditor import IDF
# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bem_utils.config

# Define paths
sim_dir = "BEM_Setup/SimResults/Comparative_HH2p_1769592803"
idf_default = os.path.join(sim_dir, "Default", "Scenario_Default.idf")
idf_2005 = os.path.join(sim_dir, "2005", "Scenario_2005.idf")

def compare_loads():
    print("=== Comparing Load Definitions ===")
    
    if not os.path.exists(idf_default):
        print(f"Default IDF not found: {idf_default}")
        return
    if not os.path.exists(idf_2005):
        print(f"2005 IDF not found: {idf_2005}")
        return
        
    IDF.setiddname(bem_utils.config.IDD_FILE)
    
    idf1 = IDF(idf_default)
    idf2 = IDF(idf_2005)
    
    print("\n--- LIGHTS ---")
    lights1 = idf1.idfobjects['LIGHTS']
    lights2 = idf2.idfobjects['LIGHTS']
    
    print(f"Default Lights Count: {len(lights1)}")
    print(f"2005 Lights Count:    {len(lights2)}")
    
    if lights1:
        l1 = lights1[0]
        print(f"Default Light[0] Name: {l1.Name}")
        # Try different potential field names or just print object
        try: print(f"  Lighting Level: {l1.Lighting_Level}")
        except: pass
        try: print(f"  Watts/Area:   {l1.Watts_per_Zone_Floor_Area}")
        except: pass
        print(f"  Schedule:     {l1.Schedule_Name}")
        
    if lights2:
        l2 = lights2[0]
        print(f"2005 Light[0] Name: {l2.Name}")
        try: print(f"  Lighting Level: {l2.Lighting_Level}")
        except: pass
        try: print(f"  Watts/Area:   {l2.Watts_per_Zone_Floor_Area}")
        except: pass
        print(f"  Schedule:     {l2.Schedule_Name}")
        
    print("\n--- ELECTRIC EQUIPMENT ---")
    eq1 = idf1.idfobjects['ELECTRICEQUIPMENT']
    eq2 = idf2.idfobjects['ELECTRICEQUIPMENT']
    
    print(f"Default Equip Count: {len(eq1)}")
    print(f"2005 Equip Count:    {len(eq2)}")
    
    if eq1:
        e1 = eq1[0]
        print(f"Default Equip[0] Name: {e1.Name}")
        try: print(f"  Design Level: {e1.Design_Level}")
        except: pass
        try: print(f"  Watts/Area:   {e1.Watts_per_Zone_Floor_Area}")
        except: pass
        print(f"  Schedule:     {e1.Schedule_Name}")

    if eq2:
        e2 = eq2[0]
        print(f"2005 Equip[0] Name: {e2.Name}")
        try: print(f"  Design Level: {e2.Design_Level}")
        except: pass
        try: print(f"  Watts/Area:   {e2.Watts_per_Zone_Floor_Area}")
        except: pass
        print(f"  Schedule:     {e2.Schedule_Name}")

if __name__ == "__main__":
    compare_loads()
