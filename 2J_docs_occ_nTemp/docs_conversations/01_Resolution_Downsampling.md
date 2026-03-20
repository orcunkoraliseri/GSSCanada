# Implementing Resolution Downsampling

**Conversation ID:** `8371b79a-0d79-4a1c-a219-b67f4a7285ad`  
**Date:** 2026-03-20

## Objective
The goal was to implement the resolution downsampling phase (Phase H) for the HETUS dataset. This involves:
- Converting 10-minute interval data (`hetus_wide.csv`) into 30-minute interval format (`hetus_30min.csv`).
- Implementing downsampling logic within `03_mergingGSS.py`.
- Handling activity and `AT_HOME` data through majority voting.
- Resolving 3-way activity ties using a defined BEM priority.
- Assembling the final 30-minute dataset and exporting it.
- Logging tasks 1 to 18 in the summary report.
