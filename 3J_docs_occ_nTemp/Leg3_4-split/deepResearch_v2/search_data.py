import os
import json

brain_dir = r"C:\Users\o_iseri\.gemini\antigravity\brain"
print("Scanning ALL transcripts in brain_dir for QC data tables...")
found_matches = []
for item in os.listdir(brain_dir):
    item_path = os.path.join(brain_dir, item)
    if os.path.isdir(item_path):
        transcript_path = os.path.join(item_path, ".system_generated", "logs", "transcript.jsonl")
        if os.path.exists(transcript_path):
            try:
                with open(transcript_path, 'r', encoding='utf-8', errors='ignore') as fh:
                    for i, line in enumerate(fh):
                        if 'QC' in line and ('2005' in line or '2022' in line) and ('occupancy_rate' in line or 'ADR_CAD' in line):
                            # Check if the line has the table or CSV content
                            if '2005,1,QC' in line or '2005-01' in line or '| 2005 | 1 | QC |' in line or '2005 | 1 | QC' in line:
                                print(f"Found completed table in {item} line {i}:")
                                print(line[:1500])
                                print("===")
                                found_matches.append((item, i))
                                break
            except Exception as e:
                pass
print(f"Scan done. Found {len(found_matches)} matching conversations.")
