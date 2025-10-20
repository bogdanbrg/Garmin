#!/usr/bin/env python3
"""
Automated script to run the Garmin export with cadence data
"""
import subprocess
import sys
import time

def run_export():
    """Run the Garmin export script automatically."""
    print("Running Garmin export with cadence data...")
    
    # Run the test.py script and automatically select option 1 (30 days)
    process = subprocess.Popen(
        [sys.executable, "test.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Send "1" to select option 1 (30 days export)
    stdout, stderr = process.communicate(input="1\n")
    
    print("STDOUT:")
    print(stdout)
    
    if stderr:
        print("STDERR:")
        print(stderr)
    
    return process.returncode

if __name__ == "__main__":
    exit_code = run_export()
    print(f"\nExport completed with exit code: {exit_code}")
