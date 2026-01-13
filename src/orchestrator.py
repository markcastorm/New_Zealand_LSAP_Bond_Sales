#!/usr/bin/env python3
# orchestrator.py
# Main orchestrator for NZ LSAP Bond Sales data collection

import os
import sys
from datetime import datetime
import config
from logger_setup import setup_logging
from scraper import RBNZDownloader
import logging

logger = logging.getLogger(__name__)


def print_banner():
    """Print a welcome banner"""
    print("\n" + "="*70)
    print(" New Zealand LSAP Bond Sales - Data Collection System")
    print(" Reserve Bank of New Zealand - Open Market Operations")
    print("="*70 + "\n")


def print_configuration():
    """Print current configuration"""
    print("Configuration:")
    print("-" * 70)
    print(f"  Source: {config.BASE_URL}")
    print(f"  Provider: {config.PROVIDER_NAME}")
    print(f"  Downloads: {config.DOWNLOAD_DIR}")
    print(f"  Output: {config.OUTPUT_DIR}")
    print(f"  Latest: {config.LATEST_OUTPUT_DIR}")
    print(f"  Logs: {config.LOG_DIR}")
    print(f"  Run Timestamp: {config.RUN_TIMESTAMP}")
    print(f"  Headless Mode: {config.HEADLESS_MODE}")
    print("-" * 70 + "\n")


def main():
    """Main execution flow"""

    try:
        # Setup logging
        setup_logging()

        print_banner()
        print_configuration()

        # Step 1: Download Excel file from RBNZ
        print("STEP 1: Downloading Open Market Operations data")
        print("="*70)

        downloader = RBNZDownloader()
        result = downloader.download_report()

        if not result:
            logger.error("Download failed")
            print("\n[ERROR] Download failed. Exiting.")
            sys.exit(1)

        print(f"\n[SUCCESS] File downloaded and processed\n")
        logger.info(f"Successfully downloaded and processed file")

        # Step 2: Summary
        print("\n" + "="*70)
        print(" EXECUTION COMPLETE")
        print("="*70 + "\n")

        print("Summary:")
        print(f"  Release Date: {result['release_date']}")
        print(f"  Filename: {result['filename']}")
        print()

        print("Output files:")
        print(f"  Timestamped: {result['timestamped_path']}")
        print(f"  Latest: {result['latest_path']}")
        print()

        # Display file size
        file_size = os.path.getsize(result['timestamped_path'])
        print(f"  File size: {file_size:,} bytes ({file_size/1024:.2f} KB)")
        print()

        print("Directories:")
        print(f"  Output folder: {config.OUTPUT_DIR}")
        print(f"  Latest folder: {config.LATEST_OUTPUT_DIR}")
        print(f"  Download folder: {config.DOWNLOAD_DIR}")
        print(f"  Log folder: {config.LOG_DIR}")
        print()

        print("="*70 + "\n")

        logger.info("Orchestrator completed successfully")

        return 0

    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Process interrupted by user")
        logger.warning("Process interrupted by user")
        sys.exit(130)

    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {e}")
        logger.exception("Unexpected error in orchestrator")
        sys.exit(1)


if __name__ == '__main__':
    sys.exit(main())
