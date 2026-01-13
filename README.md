# New Zealand LSAP Bond Sales - Data Collection

Automated data collection system for Reserve Bank of New Zealand (RBNZ) Open Market Operations data.

## Overview

This runbook automates the process of:
1. Navigating to the RBNZ Open Market Operations statistics page
2. Extracting the data release date
3. Downloading the Open Market Operations Excel file (`hd3.xlsx`)
4. Renaming the file to `hd3_YYYYMMDD.xlsx` format (using release date)
5. Organizing files into timestamped folders with "latest" folder

## Architecture

This project follows a clean, modular architecture inspired by the CHEF_NOVARTIS runbook:

```
New_Zealand_LSAP_Bond_Sales/
├── src/
│   ├── config.py           # Configuration settings
│   ├── logger_setup.py     # Logging configuration
│   ├── scraper.py          # Web scraping with Selenium
│   └── orchestrator.py     # Main coordinator
├── downloads/              # Downloaded files (timestamped subfolders)
│   ├── YYYYMMDD_HHMMSS/
│   └── latest/
├── output/                 # Processed output files
│   ├── YYYYMMDD_HHMMSS/
│   └── latest/             # Always contains most recent file
├── logs/                   # Log files (timestamped subfolders)
│   ├── YYYYMMDD_HHMMSS/
│   └── latest/
├── project information/    # Project documentation
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Features

- **Timestamped Organization**: Each run creates timestamped folders for downloads, output, and logs
- **Latest Folder**: Always contains the most recent files for easy access
- **Automatic Date Extraction**: Reads the release date directly from the RBNZ website
- **Robust Logging**: Detailed logs for debugging and monitoring
- **Stealth Mode Selenium**: Uses undetected-chromedriver to avoid bot detection
- **Smart Chrome Detection**: Automatically detects Chrome version from Windows registry or executable
- **Download Monitoring**: Intelligent wait logic that monitors .crdownload files

## Prerequisites

1. **Python 3.8+**
2. **Google Chrome** browser installed
   - ChromeDriver is automatically downloaded and matched to your Chrome version

## Installation

1. Navigate to the project directory:
```bash
cd "D:\Projects\SIMBA-RUNBOOKS\New_Zealand_LSAP_Bond_Sales"
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Verify Chrome and ChromeDriver are installed:
```bash
chromedriver --version
```

## Usage

### Run the Complete Workflow

```bash
cd src
python orchestrator.py
```

This will:
1. Initialize logging
2. Launch Chrome browser
3. Navigate to RBNZ website
4. Extract release date
5. Download the Excel file
6. Rename and organize files
7. Generate timestamped outputs

### Test Individual Components

Test the scraper only:
```bash
cd src
python scraper.py
```

Test logging only:
```bash
cd src
python logger_setup.py
```

## Configuration

Edit `src/config.py` to customize:

### Browser Settings
```python
HEADLESS_MODE = False  # Set to True for production (no browser window)
DEBUG_MODE = True      # Enable detailed logging
WAIT_TIMEOUT = 20      # Selenium wait timeout in seconds
```

### Folder Settings
```python
USE_TIMESTAMPED_FOLDERS = True  # Create timestamped subfolders for each run
```

### Web Scraping Selectors
Update CSS selectors if the RBNZ website structure changes:
```python
SELECTORS = {
    'released_date': 'div.hero__metadata-item time[datetime]',
    'xlsx_link': 'a[href*="hd3.xlsx"]',
    # ... more selectors
}
```

## Output

### File Naming Convention
Downloaded files are renamed to: `hd3_YYYYMMDD.xlsx`

Where `YYYYMMDD` is the release date extracted from the RBNZ website.

Example: `hd3_20260112.xlsx` (for January 12, 2026 release)

### Folder Structure After Run

```
downloads/
├── 20260112_143022/
│   └── hd3.xlsx              # Original downloaded file
└── latest/
    └── hd3.xlsx              # Copy of latest download

output/
├── 20260112_143022/
│   └── hd3_20260112.xlsx     # Renamed file
└── latest/
    └── hd3_20260112.xlsx     # Always the most recent

logs/
├── 20260112_143022/
│   └── nz_lsap_20260112_143022.log
└── latest/
    └── nz_lsap_20260112_143022.log
```

## Data Source

**Website**: https://www.rbnz.govt.nz/statistics/series/reserve-bank/open-market-operations

**Data File**: Open markets operations - D3 (1995-current)

**File Format**: Excel (.xlsx)

**Update Frequency**: Daily

## Logging

Logs are written to:
- Console (real-time output)
- Timestamped log file: `logs/YYYYMMDD_HHMMSS/nz_lsap_YYYYMMDD_HHMMSS.log`
- Latest log file: `logs/latest/nz_lsap_YYYYMMDD_HHMMSS.log`

Log levels:
- `DEBUG`: Detailed information for debugging
- `INFO`: General information about progress
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical errors

## Troubleshooting

### ChromeDriver Issues

If you get ChromeDriver errors:
```bash
pip install webdriver-manager
```

Then the scraper will automatically download the correct ChromeDriver version.

### Selenium Timeout

If page loading times out, increase the timeout in `config.py`:
```python
WAIT_TIMEOUT = 30  # Increase from 20 to 30 seconds
```

### Download Not Detected

Increase the download wait time in `config.py`:
```python
DOWNLOAD_WAIT_TIME = 15  # Increase from 10 to 15 seconds
```

### Website Structure Changed

If CSS selectors don't work, inspect the RBNZ website and update selectors in `config.py`:
1. Open the website in Chrome
2. Right-click → Inspect
3. Find the updated element selectors
4. Update `SELECTORS` dictionary in `config.py`

## AWS Workspace Deployment

As per the runbook instructions:
> This data should be processed only via your AWS workspace.

To deploy on AWS:
1. Upload project folder to AWS workspace
2. Install dependencies: `pip install -r requirements.txt`
3. Install Chrome and ChromeDriver on AWS instance
4. Run in headless mode: Set `HEADLESS_MODE = True` in `config.py`
5. Schedule with cron or AWS Lambda for daily execution

## Related Projects

This runbook follows the same architecture as:
- **CHEF_NOVARTIS**: Novartis Pension Fund data collection
- **SNOWFALL_RUNBOOK**: Snowfall data scraping

## Support

For issues or questions:
1. Check logs in `logs/latest/`
2. Enable debug mode: `DEBUG_MODE = True` in `config.py`
3. Review the RBNZ website for structural changes
4. Check ChromeDriver compatibility with Chrome version

## License

Internal use only.
