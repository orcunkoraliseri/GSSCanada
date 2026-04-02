# Project Setup and Dependencies

This project is tailored for generating synthetic residential occupancy schedules for Canadian housing and simulating them in EnergyPlus. To run this project on another machine, follow the requirements below.

## 1. System Requirements
- **Python**: 3.9 or higher is required.
- **EnergyPlus**: Version **24.2.0** is expected for building energy simulations.
    - **macOS**: Default path `/Applications/EnergyPlus-24-2-0`
    - **Windows**: Default path `C:\EnergyPlusV24-2-0`
- You can override the path by setting the `ENERGYPLUS_DIR` environment variable.

## 2. Python Libraries
Install the required libraries using the provided `requirements.txt`.

### Data Processing & Analysis
- `pandas`: Data manipulation (Census/GSS)
- `numpy`: Numerical computations
- `pyreadstat`: Reading SPSS (`.sav`/`.dat`) and SAS files
- `openpyxl`: Excel file support
- `scipy`: Statistical analysis

### Machine Learning & Statistics
- `scikit-learn`: Clustering (K-Means), PCA, and Regression
- `tensorflow`: Used for CVAE models
- `tqdm`: Progress bars for long-running pipelines

### Building Energy Modeling (BEM)
- `eppy`: EnergyPlus IDF manipulation
- `geomeppy`: Geometric manipulation of IDF files

### Visualization & Reporting
- `matplotlib`: Core plotting
- `seaborn`: Statistical visualization
- `fpdf`: PDF report generation
- `PyPDF2`: PDF manipulation

## 3. Installation Steps

1. **Install EnergyPlus**: Download and install EnergyPlus 24.2.0 from the official website.
2. **Setup Python Environment**:
   ```bash
   # Recommended: Create a virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 4. Configuration
Before running any scripts, ensure your data paths are correct:
- **Occupancy Data**: Check `eSim_occ_utils/occ_config.py`. You may need to set the `GSS_BASE_DIR` environment variable to point to your `0_Occupancy` folder.
- **EnergyPlus**: Check `eSim_bem_utils/config.py`. Ensure the path matches your installation.
