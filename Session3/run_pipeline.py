#!/usr/bin/env python3
"""
Complete GNews Pipeline Runner
Orchestrates data fetching and analysis in sequence.
"""

import subprocess
import sys
import os


def run_command(cmd: list, description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n{'=' * 70}")
    print(f"Step: {description}")
    print('=' * 70)
    
    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error running {description}: {e}")
        return False
    except FileNotFoundError:
        print(f"[ERROR] Command not found. Ensure Python is in PATH.")
        return False


def check_api_key() -> bool:
    """Check if GNews API key is configured."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv('GNEWS_API_KEY', '')
        
        if not api_key or api_key == 'your_api_key_here':
            print("[ERROR] GNEWS_API_KEY not configured in .env")
            print("\nTo configure:")
            print("1. Visit https://gnews.io/")
            print("2. Create a free account")
            print("3. Obtain API key")
            print("4. Add to .env file:")
            print("   GNEWS_API_KEY=your_actual_key")
            return False
        return True
    except ImportError:
        print("[ERROR] python-dotenv not installed. Run: pip install python-dotenv")
        return False


def main():
    print("\n" + "=" * 70)
    print("GNews Data Pipeline - Complete Orchestration")
    print("=" * 70)
    
    # Check prerequisites
    print("\nChecking prerequisites...")
    
    if not check_api_key():
        sys.exit(1)
    
    print("[OK] API key configured")
    
    # Check dependencies
    try:
        import requests
        print("[OK] requests library installed")
    except ImportError:
        print("[ERROR] requests not installed. Run: pip install requests")
        sys.exit(1)
    
    # Run pipeline steps
    success = True
    
    # Step 1: Fetch data
    success = run_command(
        [sys.executable, 'gnews_pipeline.py'],
        "Fetch headlines from GNews API"
    ) and success
    
    if not success:
        print("\n[ERROR] Data fetching failed. Cannot proceed to analysis.")
        sys.exit(1)
    
    # Step 2: Analyze data
    success = run_command(
        [sys.executable, 'analyze_headlines.py'],
        "Analyze headlines and answer 8 questions"
    ) and success
    
    # Summary
    print("\n" + "=" * 70)
    if success:
        print("[OK] Pipeline Complete")
        print("\nGenerated files:")
        print("  - headlines.csv              (Main database)")
        print("  - headlines_long_titles.csv  (Filtered headlines > 6 words)")
        print("\nNext steps:")
        print("  1. Review headlines.csv for raw data")
        print("  2. Check analysis output above for all 8 answers")
        print("  3. Run again to add new headlines (duplicates prevented)")
    else:
        print("[ERROR] Pipeline encountered errors")
        sys.exit(1)
    print("=" * 70)


if __name__ == "__main__":
    main()
