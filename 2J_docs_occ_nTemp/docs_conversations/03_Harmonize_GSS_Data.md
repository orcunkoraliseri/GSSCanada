# Harmonize GSS Data

**Conversation ID:** `afb4a398-409e-4682-ac02-ffb006e590f0`  
**Date:** 2026-03-20

## Objective
Modified GSS data harmonization scripts to exclude the 'MODE' column entirely.
- Commented out selection and processing in `01_readingGSS.py` and `02_harmonizeGSS.py`.
- Updated validation scripts (`01_readingGSS_val.py`, `02_harmonizeGSS_val.py`).
- This prevents failures in cycles (e.g., 2005) where 'MODE' was unavailable.
