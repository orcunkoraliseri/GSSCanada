# Generate Annual Energy Demand Table (4.3.1)

## Goal Description
Generate a summary table (Table 4.3.1) comparing the percentage change in Heating and Cooling demand for 2005, 2015, and 2025 scenarios relative to the "Default" baseline across three locations: Toronto (5A), Montreal (6A), and Winnipeg (7).

## User Review Required
> [!NOTE]
> The table will be formatted as "Heating % Change / Cooling % Change".
> Statistical significance (ANOVA, Tukey, Cohen's d) is already calculated in the individual reports and can be aggregated if needed, but the primary request is the % change table.

## Proposed Changes

### Script Development
#### [NEW] [generate_table_4.3.1.py](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/eSim_occ_utils/plotting/generate_table_4.3.1.py)
- **Input**: Reads the three existing Comparative Analysis Report CSVs:
    1. `Prairies_Comparative_Analysis_Report.csv` (Winnipeg)
    2. `Ontario_Comparative_Analysis_Report.csv` (Toronto)
    3. `Quebec_Comparative_Analysis_Report.csv` (Montreal)
- **Logic**:
    - For each location:
        - Extract Mean Heating & Cooling demand (kWh/m²) for "Default".
        - Extract Mean Heating & Cooling demand for "2005", "2015", "2025".
        - Calculate % Diff: `(Scenario - Default) / Default * 100`.
    - Format output as a Markdown table.
- **Output**:
    - Saves the table as a CSV file to `C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\eSim_occ_utils\plotting\Table_4.3.1_Annual_Energy_Demand.csv`.
    - Format: Rows=Scenarios, Cols=Cities, Cell Value="Heating % / Cooling %".

## Verification Plan
### Manual Verification
- Verify the calculated percentages against a manual spot check of the CSV values.
- Confirm the table structure matches the user's requested format.
