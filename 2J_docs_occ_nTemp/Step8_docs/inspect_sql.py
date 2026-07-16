import sqlite3
import pandas as pd
import os

path = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\BEM_Setup\SimResults\MonteCarlo_N60_1771010812\iter_1\2025\eplusout.sql"

if not os.path.exists(path):
    print(f"File not found: {path}")
else:
    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tables:", [t[0] for t in tables])
        
        if ('ReportData',) in tables or ('ReportDataDictionary',) in tables:
             # Check available report variables
             print("\nSearching for Heating/Cooling Variables:")
             cursor.execute("SELECT DISTINCT Name FROM ReportDataDictionary WHERE Name LIKE '%Heating%' OR Name LIKE '%Cooling%' OR Name LIKE '%Electricity%' ORDER BY Name")
             for row in cursor.fetchall():
                 print(row[0])
                 
             # Check data count
             cursor.execute("SELECT Count(*) FROM ReportData")
             count = cursor.fetchone()[0]
             print(f"\nReportData Row Count: {count}")
        else:
             print("\nNo ReportData table found (Time Series data missing)")

        conn.close()

    except Exception as e:
        print(f"Error: {e}")
