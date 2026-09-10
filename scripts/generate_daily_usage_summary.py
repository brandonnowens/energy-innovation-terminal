#!/usr/bin/env python3
"""
CLI Command / Cron Job Runner for Daily Application Usage and Information Summary.

Usage:
    python scripts/generate_daily_usage_summary.py
    python scripts/generate_daily_usage_summary.py --date 2026-09-10
    python scripts/generate_daily_usage_summary.py --stdout
"""

import sys
import argparse
from datetime import datetime
from pathlib import Path

# Ensure UTF-8 output across Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add backend to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "backend"))

from app.database import SessionLocal
from app.services.daily_usage_summary import generate_and_save_daily_summary, REPORTS_DIR


def main():
    parser = argparse.ArgumentParser(description="Generate Daily Application Usage & Corpus Summary Markdown.")
    parser.add_argument("--date", type=str, default=None, help="Target date in YYYY-MM-DD format (defaults to today).")
    parser.add_argument("--output-dir", type=str, default=None, help="Output directory for generated markdown report.")
    parser.add_argument("--stdout", action="store_true", help="Print generated markdown directly to stdout.")

    args = parser.parse_args()

    target_date = None
    if args.date:
        try:
            target_date = datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError:
            print(f"Error: Invalid date format '{args.date}'. Expected YYYY-MM-DD.", file=sys.stderr)
            sys.exit(1)

    out_dir = Path(args.output_dir) if args.output_dir else REPORTS_DIR

    print(f"[DailyUsageSummary] Inspecting database and compiling metrics for target date: {args.date or 'Today (UTC)'}...")
    
    with SessionLocal() as db:
        result = generate_and_save_daily_summary(db=db, target_date=target_date, output_dir=out_dir)

    stats = result.get("user_summary") or result.get("metrics_summary") or {}
    print(f"[DailyUsageSummary] User Usage Summary successfully generated!")
    print(f"  - Dated File  : {result['daily_file']}")
    print(f"  - Latest Copy : {result['latest_file']}")
    print(f"  - JSON Data   : {result['json_file']}")
    print(f"  - Key Stats   : {stats}")

    if args.stdout:
        print("\n" + "=" * 80)
        print(result["markdown_content"])
        print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
