import sqlite3
import os
import glob

def check_results():
    # Find the latest results directory
    base_dir = "0_BEM_Setup/SimResults"
    dirs = glob.glob(os.path.join(base_dir, "Neighbourhood_Comparative_*"))
    if not dirs:
        print("No results found.")
        return
    
    # latest_dir = sorted(dirs)[-1]
    latest_dir = "0_BEM_Setup/SimResults/Neighbourhood_Comparative_1768427696"
    print(f"Checking results in: {latest_dir}")
    
    scenarios = ["Default", "2015", "2025", "2005"]
    
    results = {}
    
    for sc in scenarios:
        sql_path = os.path.join(latest_dir, sc, "eplusout.sql")
        if not os.path.exists(sql_path):
            print(f"  {sc}: SQL not found.")
            continue
            
        try:
            conn = sqlite3.connect(sql_path)
            c = conn.cursor()
            
            # Get Total Energy (Annual)
            query_energy = """
                SELECT Value 
                FROM ReportData 
                WHERE ReportDataDictionaryIndex IN (
                    SELECT ReportDataDictionaryIndex 
                    FROM ReportDataDictionary 
                    WHERE Name IN ('InteriorLights:Electricity', 'InteriorEquipment:Electricity')
                    AND ReportingFrequency = 'Monthly'
                )
            """
            c.execute(query_energy)
            total_j = sum(row[0] for row in c.fetchall())
            
            # Get Total Area
            # Usually in TabularDataWithStrings -> Input Verification and Results Summary -> Zone Summary -> Total -> Area
            # But let's check standard "Zone Summary" table
            query_area = """
                SELECT Value 
                FROM TabularDataWithStrings 
                WHERE ReportName = 'Input Verification and Results Summary' 
                AND ReportForString = 'Entire Facility' 
                AND TableName = 'Zone Summary' 
                AND RowName = 'Total' 
                AND ColumnName = 'Area'
            """
            c.execute(query_area)
            area_row = c.fetchone()
            area = float(area_row[0]) if area_row else 0.0
            
            results[sc] = {'Energy_J': total_j, 'Area_m2': area}
            
            conn.close()
            
        except Exception as e:
            print(f"  {sc}: Error {e}")
            
    print("\nRESULTS SUMMARY:")
    print(f"{'Scenario':<10} | {'Total Energy (GJ)':<18} | {'Total Area (m2)':<15} | {'EUI (kWh/m2)':<15}")
    print("-" * 65)
    
    base_energy = results.get('Default', {}).get('Energy_J', 0)
    
    for sc in scenarios:
        if sc in results:
            e_j = results[sc]['Energy_J']
            a_m2 = results[sc]['Area_m2']
            e_gj = e_j / 1e9
            eui = (e_j / 3.6e6) / a_m2 if a_m2 > 0 else 0
            
            ratio = f"{e_j/base_energy:.2f}x" if base_energy > 0 else "-"
            
            print(f"{sc:<10} | {e_gj:<18.2f} | {a_m2:<15.2f} | {eui:<15.2f} ({ratio})")

if __name__ == "__main__":
    check_results()
