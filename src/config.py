# config.py
# New Zealand LSAP Bond Sales Data Collection Configuration

import os
from datetime import datetime

# =============================================================================
# DATA SOURCE CONFIGURATION
# =============================================================================

BASE_URL = 'https://www.rbnz.govt.nz/statistics/series/reserve-bank/open-market-operations'
PROVIDER_NAME = 'Reserve Bank of New Zealand'
DATASET_NAME = 'NZ_LSAP_BOND_SALES'
COUNTRY = 'New Zealand'
CURRENCY = 'NZD'

# =============================================================================
# TIMESTAMPED FOLDERS CONFIGURATION
# =============================================================================

# Generate timestamp for this run (format: YYYYMMDD_HHMMSS)
RUN_TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M%S')

# Use timestamped folders to avoid conflicts between runs
USE_TIMESTAMPED_FOLDERS = True

# =============================================================================
# WEB SCRAPING SELECTORS
# =============================================================================

SELECTORS = {
    # Hero section with metadata (release date, next release)
    'hero_metadata': 'div.hero__metadata',
    'released_date': 'div.hero__metadata-item time[datetime]',
    'released_date_container': 'div.hero__metadata-item:has(div.hero__metadata-title:contains("Released:"))',

    # Download card section
    'download_card': 'div.download-card',
    'download_link': 'a.download-card__link',
    'download_href': 'href',

    # Alternative selectors for the Excel file
    'data_files_section': 'div#article-content',
    'xlsx_link': 'a[href*="hd3.xlsx"]',
}

# =============================================================================
# FILE NAMING CONFIGURATION
# =============================================================================

# Source filename from RBNZ website
SOURCE_FILENAME = 'hd3.xlsx'

# Output filename pattern: hd3_YYYYMMDD.xlsx
# Where YYYYMMDD is the release date
OUTPUT_FILENAME_PATTERN = 'hd3_{date}.xlsx'

# =============================================================================
# BROWSER CONFIGURATION
# =============================================================================

HEADLESS_MODE = False  # Set to True for production
DEBUG_MODE = True
WAIT_TIMEOUT = 60  # Seconds
PAGE_LOAD_DELAY = 5  # Seconds
DOWNLOAD_WAIT_TIME = 10  # Seconds to wait for download to complete
NAVIGATE_MAX_RETRIES = 3  # Retries for page navigation

# =============================================================================
# OUTPUT CONFIGURATION
# =============================================================================

# Get project root (parent of src folder)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Base directories
BASE_DOWNLOAD_DIR = os.path.join(PROJECT_ROOT, 'downloads')
BASE_OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'output')
BASE_LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')

# Apply timestamping if enabled
if USE_TIMESTAMPED_FOLDERS:
    DOWNLOAD_DIR = os.path.join(BASE_DOWNLOAD_DIR, RUN_TIMESTAMP)
    OUTPUT_DIR = os.path.join(BASE_OUTPUT_DIR, RUN_TIMESTAMP)
    LOG_DIR = os.path.join(BASE_LOG_DIR, RUN_TIMESTAMP)
else:
    DOWNLOAD_DIR = BASE_DOWNLOAD_DIR
    OUTPUT_DIR = BASE_OUTPUT_DIR
    LOG_DIR = BASE_LOG_DIR

# Latest folder (always contains most recent extraction)
LATEST_DOWNLOAD_DIR = os.path.join(BASE_DOWNLOAD_DIR, 'latest')
LATEST_OUTPUT_DIR = os.path.join(BASE_OUTPUT_DIR, 'latest')
LATEST_LOG_DIR = os.path.join(BASE_LOG_DIR, 'latest')

# Log file naming
LOG_FILE_PATTERN = 'nz_lsap_{timestamp}.log'

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

# Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = 'DEBUG' if DEBUG_MODE else 'INFO'

# Log format
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Console output
LOG_TO_CONSOLE = True
LOG_TO_FILE = True

# =============================================================================
# DATE FORMATS
# =============================================================================

# Date format for filename (YYYYMMDD)
FILENAME_DATE_FORMAT = '%Y%m%d'

# Date format for parsing from website (ISO format)
ISO_DATE_FORMAT = '%Y-%m-%d'

# =============================================================================
# ERROR HANDLING
# =============================================================================

# Maximum retries for download failures
MAX_DOWNLOAD_RETRIES = 3
RETRY_DELAY = 2.0  # Seconds between retries

# Continue processing even if download fails
CONTINUE_ON_ERROR = False
