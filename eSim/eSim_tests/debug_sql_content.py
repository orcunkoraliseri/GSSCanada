import sqlite3
import os
import glob

def inspect_sql():
    # Find any eplusout.sql file
    search_path = os.path.join(os.getcwd(), "BEM_Setup", "SimResults", "**", "eplusout.sql")
    sql_files = glob.glob(search_path, recursive=True)
    
    if not sql_files:
        print("No SQL files found to inspect.")
        return

    sql_path = sql_files[0]
    print(f"Inspecting: {sql_path}")
    
    conn = sqlite3.connect(sql_path)
    cursor = conn.cursor()
    
    print("\n--- EnvironmentPeriods Table ---")
    try:
        cursor.execute("SELECT * FROM EnvironmentPeriods")
        rows = cursor.fetchall()
        # get column names
        names = [description[0] for description in cursor.description]
        print(f"Columns: {names}")
        for row in rows:
            print(row)
    except Exception as e:
        print(f"Error reading EnvironmentPeriods: {e}")

    conn.close()

if __name__ == "__main__":
    inspect_sql()
