"""
HPC job progress monitor — checks every 4 hours.

Usage:
    python check_hpc_progress.py

Requires OpenSSH on Windows (already present if you used scp/ssh above).
You will be prompted for your password at each check unless you have SSH keys set up.
Press Ctrl+C to stop monitoring.
"""

import subprocess
import time
from datetime import datetime

USER = "o_iseri"
HOST = "speed.encs.concordia.ca"
RESULTS_DIR = "/speed-scratch/o_iseri/GSSCanada/results/BatchAll_MC_N20_v2"
HOODS = ["NUS_RC1", "NUS_RC2", "NUS_RC3", "NUS_RC4", "NUS_RC5", "NUS_RC6"]
CHECK_INTERVAL_HOURS = 4


def ssh(cmd: str) -> str:
    result = subprocess.run(
        ["ssh", f"{USER}@{HOST}", cmd],
        capture_output=True, text=True
    )
    return result.stdout.strip()


def check_queue() -> list[str]:
    out = ssh(f"squeue -u {USER} -o '%.18i %.9P %.12j %.8u %.2t %.10M %.6D %R'")
    lines = out.splitlines()
    return lines


def check_iterations() -> dict:
    counts = {}
    for hood in HOODS:
        hood_dir = f"{RESULTS_DIR}/{hood}/{hood}"
        # Count iter_* dirs that contain at least one eplusout.sql
        out = ssh(
            f"find {hood_dir} -maxdepth 3 -name 'eplusout.sql' 2>/dev/null"
            f" | awk -F/ '{{print $(NF-2)}}' | grep '^iter_' | sort -u | wc -l"
        )
        try:
            counts[hood] = int(out)
        except ValueError:
            counts[hood] = "?"
    return counts


def check_csv_exists() -> dict:
    exists = {}
    for hood in HOODS:
        csv = f"{RESULTS_DIR}/{hood}/{hood}/aggregated_eui.csv"
        out = ssh(f"test -f {csv} && echo yes || echo no")
        exists[hood] = out.strip() == "yes"
    return exists


def print_report(queue_lines: list, iter_counts: dict, csv_exists: dict) -> bool:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"\n{'='*55}")
    print(f"  HPC Progress Report — {now}")
    print(f"{'='*55}")

    running_ids = [l for l in queue_lines if " R " in l or " PD " in l]
    if running_ids:
        print("\nActive SLURM tasks:")
        for line in queue_lines:
            print(f"  {line}")
    else:
        print("\n  No active SLURM tasks — all jobs finished or not yet queued.")

    print(f"\nIteration counts (completed sims per neighbourhood):")
    for hood, count in iter_counts.items():
        csv_mark = " [CSV ready]" if csv_exists.get(hood) else ""
        bar = "#" * (count if isinstance(count, int) else 0)
        print(f"  {hood}: {str(count):>3}/20  {bar}{csv_mark}")

    all_done = not running_ids
    csvs_ready = sum(csv_exists.values())
    print(f"\n  aggregated_eui.csv present: {csvs_ready}/6 neighbourhoods")

    if all_done:
        print("\n  ✓ All jobs finished. Ready to download CSVs and run interim_report_gen.py.")

    return all_done


def main():
    print("Monitoring HPC job 900364 — checking every 4 hours. Press Ctrl+C to stop.")
    while True:
        try:
            queue = check_queue()
            iters = check_iterations()
            csvs = check_csv_exists()
            all_done = print_report(queue, iters, csvs)

            if all_done:
                break

            next_check = datetime.fromtimestamp(
                time.time() + CHECK_INTERVAL_HOURS * 3600
            ).strftime("%H:%M")
            print(f"\n  Next check at {next_check}. Sleeping...")
            time.sleep(CHECK_INTERVAL_HOURS * 3600)

        except KeyboardInterrupt:
            print("\nMonitoring stopped.")
            break


if __name__ == "__main__":
    main()
