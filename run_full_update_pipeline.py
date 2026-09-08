"""
Single-Command Automated Data Ingestion & Executive Reports Pipeline.
Usage:
    python run_full_update_pipeline.py
    python run_full_update_pipeline.py --api-key "sk-..." --model "gpt-4o"
"""

import os
import sys

# Ensure backend package is in python path
root_dir = os.path.abspath(os.path.dirname(__file__))
backend_dir = os.path.join(root_dir, "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.ingest.pipeline_runner import run_data_refresh_and_report_pipeline

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run Full Data Refresh & Executive Report Generation Pipeline")
    parser.add_argument("--api-key", type=str, default=None, help="OpenAI API Key (optional)")
    parser.add_argument("--model", type=str, default="gpt-4o-mini", help="OpenAI Model (default: gpt-4o-mini)")
    args = parser.parse_args()

    run_data_refresh_and_report_pipeline(openai_api_key=args.api_key, model_name=args.model)
