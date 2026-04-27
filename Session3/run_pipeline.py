#!/usr/bin/env python3
"""
GNews Pipeline Runner
Runs data fetching + analysis in sequence.
"""

import subprocess
import sys
import os
from dotenv import load_dotenv


def run_command(cmd, description):
    print("\n" + "=" * 70)
    print(f"Step: {description}")
    print("=" * 70)

    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description} failed: {e}")
        return False


def check_api_key():
    load_dotenv()
    api_key = os.getenv("GNEWS_API_KEY")

    if not api_key or api_key == "your_api_key_here":
        print("[ERROR] GNEWS_API_KEY not configured in .env")
        return False

    print("[OK] API key configured")
    return True


def main():
    print("\n" + "=" * 70)
    print("GNews Data Pipeline - Orchestration")
    print("=" * 70)

    print("\nChecking prerequisites...")

    if not check_api_key():
        sys.exit(1)

    try:
        import requests
        print("[OK] requests installed")
    except ImportError:
        print("[ERROR] requests not installed (pip install requests)")
        sys.exit(1)

    # Step 1: Fetch data
    if not run_command(
        [sys.executable, "gnews_pipeline.py"],
        "Fetching headlines"
    ):
        sys.exit(1)

    # Step 2: Analyze data
    if not run_command(
        [sys.executable, "analyze_headlines.py"],
        "Analyzing headlines"
    ):
        sys.exit(1)

    # Success summary
    print("\n" + "=" * 70)
    print("[OK] Pipeline completed successfully")
    print("\nGenerated files:")
    print("  - headlines.csv")
    print("  - headlines_long_titles.csv")
    print("\nDone.")
    print("=" * 70)


if __name__ == "__main__":
    main()