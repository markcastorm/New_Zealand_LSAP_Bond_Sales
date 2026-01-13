# scraper.py
# Downloads Open Market Operations Excel file from Reserve Bank of New Zealand

import os
import time
import logging
import shutil
import winreg
from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
import config

# Setup logging
logger = logging.getLogger(__name__)


def get_chrome_version_from_registry():
    """
    Get Chrome version from Windows registry.
    Returns the major version number or None if not found.
    """
    try:
        # Try different registry locations (system-wide and user-specific)
        registry_locations = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Google\Chrome\BLBeacon"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\Google\Chrome\BLBeacon"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Google\Chrome\BLBeacon"),
            (winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon"),
        ]

        for hkey, key_path in registry_locations:
            try:
                key = winreg.OpenKey(hkey, key_path)
                version, _ = winreg.QueryValueEx(key, "version")
                winreg.CloseKey(key)

                # Extract major version (e.g., "120.0.6099.109" -> 120)
                major_version = int(version.split('.')[0])
                hkey_name = "HKEY_LOCAL_MACHINE" if hkey == winreg.HKEY_LOCAL_MACHINE else "HKEY_CURRENT_USER"
                logger.info(f"Chrome version detected from {hkey_name}\\{key_path}: {version} (major: {major_version})")
                return major_version
            except FileNotFoundError:
                continue
            except Exception as e:
                logger.debug(f"Error reading registry: {e}")
                continue

        # Fallback: try to get version from Chrome executable
        try:
            import subprocess
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
            ]

            for chrome_path in chrome_paths:
                if os.path.exists(chrome_path):
                    result = subprocess.run([chrome_path, "--version"], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        version_str = result.stdout.strip()
                        # Extract version like "Google Chrome 120.0.6099.109"
                        version = version_str.split()[-1]
                        major_version = int(version.split('.')[0])
                        logger.info(f"Chrome version detected from executable: {version} (major: {major_version})")
                        return major_version
        except Exception as e:
            logger.debug(f"Could not detect Chrome version from executable: {e}")

        logger.warning("Could not detect Chrome version from registry or executable")
        return None

    except Exception as e:
        logger.error(f"Error detecting Chrome version: {e}")
        return None


class RBNZDownloader:
    """Downloads Open Market Operations data from Reserve Bank of New Zealand"""

    def __init__(self):
        self.driver = None
        self.download_dir = None
        self.release_date = None
        self.logger = logger

    def setup_driver(self):
        """Initialize Chrome driver with download preferences using undetected-chromedriver"""

        # Create download directory with timestamp
        self.download_dir = os.path.abspath(config.DOWNLOAD_DIR)
        os.makedirs(self.download_dir, exist_ok=True)

        # Detect Chrome version from registry
        chrome_version = get_chrome_version_from_registry()
        if chrome_version:
            self.logger.info(f"Using Chrome major version: {chrome_version}")
        else:
            self.logger.warning("Chrome version not detected, using auto-detection")

        # Use undetected_chromedriver options
        chrome_options = uc.ChromeOptions()

        # Set download directory
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)

        if config.HEADLESS_MODE:
            chrome_options.add_argument('--headless=new')

        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')

        # Use undetected_chromedriver (stealth mode) with detected version
        self.driver = uc.Chrome(options=chrome_options, version_main=chrome_version)
        self.driver.set_page_load_timeout(config.WAIT_TIMEOUT)

        self.logger.info(f"Chrome driver initialized (stealth mode)")
        self.logger.info(f"Download directory: {self.download_dir}")

    def navigate_to_page(self):
        """Navigate to the Open Market Operations page"""

        self.logger.info(f"Navigating to {config.BASE_URL}")

        self.driver.get(config.BASE_URL)
        time.sleep(config.PAGE_LOAD_DELAY)

        self.logger.info("Page loaded successfully")

    def extract_release_date(self):
        """
        Extract the 'Released' date from the hero metadata section.
        Returns date string in YYYYMMDD format.
        """

        self.logger.info("Extracting release date from page...")

        try:
            wait = WebDriverWait(self.driver, config.WAIT_TIMEOUT)

            # Find all time elements with datetime attribute
            time_elements = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, config.SELECTORS['released_date']))
            )

            if not time_elements:
                raise Exception("No date elements found on page")

            # The first time element should be the "Released" date
            # It has a datetime attribute like "2026-01-12"
            release_date_element = time_elements[0]
            datetime_attr = release_date_element.get_attribute('datetime')

            if not datetime_attr:
                raise Exception("Could not find datetime attribute")

            self.logger.info(f"Found release date: {datetime_attr}")

            # Parse the ISO date format (YYYY-MM-DD) and convert to YYYYMMDD
            date_obj = datetime.strptime(datetime_attr, config.ISO_DATE_FORMAT)
            self.release_date = date_obj.strftime(config.FILENAME_DATE_FORMAT)

            self.logger.info(f"Formatted release date: {self.release_date}")
            return self.release_date

        except Exception as e:
            self.logger.error(f"Error extracting release date: {e}")
            # Fallback to today's date
            self.release_date = datetime.now().strftime(config.FILENAME_DATE_FORMAT)
            self.logger.warning(f"Using fallback date: {self.release_date}")
            return self.release_date

    def wait_for_download_complete(self, timeout=30):
        """
        Wait for download to complete by monitoring the download directory.
        Returns the downloaded file path.
        """
        self.logger.info(f"Waiting for download to complete (timeout: {timeout}s)...")

        end_time = time.time() + timeout
        expected_file = os.path.join(self.download_dir, config.SOURCE_FILENAME)

        while time.time() < end_time:
            # Check for .crdownload files (Chrome incomplete downloads)
            crdownload_files = [f for f in os.listdir(self.download_dir) if f.endswith('.crdownload')]

            if crdownload_files:
                self.logger.debug(f"Download in progress... ({crdownload_files[0]})")
                time.sleep(1)
                continue

            # Check if the expected file exists and has a reasonable size
            if os.path.exists(expected_file):
                file_size = os.path.getsize(expected_file)
                if file_size > 10000:  # More than 10KB
                    self.logger.info(f"Download complete: {file_size:,} bytes")
                    return expected_file

            time.sleep(1)

        raise Exception(f"Download timeout after {timeout} seconds")

    def download_excel_file(self):
        """
        Find and click the download link for hd3.xlsx, then wait for download to complete.
        Returns the path to the downloaded file.
        """

        self.logger.info("Looking for Excel download link...")

        try:
            wait = WebDriverWait(self.driver, config.WAIT_TIMEOUT)

            # Find the download link for hd3.xlsx
            download_link = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, config.SELECTORS['xlsx_link']))
            )

            download_url = download_link.get_attribute('href')
            self.logger.info(f"Found download link: {download_url}")

            # Clear any existing files
            expected_file = os.path.join(self.download_dir, config.SOURCE_FILENAME)
            if os.path.exists(expected_file):
                os.remove(expected_file)
                self.logger.debug("Removed existing file")

            # Click the download link
            self.logger.info("Clicking download link...")
            download_link.click()

            # Wait for download to complete
            downloaded_path = self.wait_for_download_complete(timeout=60)

            file_size = os.path.getsize(downloaded_path)
            self.logger.info(f"Downloaded file: {config.SOURCE_FILENAME}")
            self.logger.info(f"File size: {file_size:,} bytes ({file_size/1024:.2f} KB)")

            return downloaded_path

        except Exception as e:
            self.logger.error(f"Error downloading Excel file: {e}")
            raise

    def rename_and_move_file(self, downloaded_path):
        """
        Rename the downloaded file to hd3_YYYYMMDD.xlsx format
        and copy to both timestamped output folder and latest folder.
        """

        if not self.release_date:
            raise Exception("Release date not set. Cannot rename file.")

        # Generate new filename
        new_filename = config.OUTPUT_FILENAME_PATTERN.format(date=self.release_date)

        # Create output directories
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)
        os.makedirs(config.LATEST_OUTPUT_DIR, exist_ok=True)

        # Paths for timestamped output
        output_path = os.path.join(config.OUTPUT_DIR, new_filename)

        # Path for latest output
        latest_output_path = os.path.join(config.LATEST_OUTPUT_DIR, new_filename)

        # Copy to timestamped output folder
        shutil.copy2(downloaded_path, output_path)
        self.logger.info(f"Copied to timestamped output: {output_path}")

        # Copy to latest folder
        shutil.copy2(downloaded_path, latest_output_path)
        self.logger.info(f"Copied to latest output: {latest_output_path}")

        return {
            'timestamped_path': output_path,
            'latest_path': latest_output_path,
            'filename': new_filename,
            'release_date': self.release_date
        }

    def download_report(self):
        """
        Main method to download and process the RBNZ Open Market Operations file.
        Returns dictionary with file information.
        """

        try:
            self.setup_driver()
            self.navigate_to_page()

            # Step 1: Extract release date
            self.extract_release_date()

            # Step 2: Download the Excel file
            downloaded_path = self.download_excel_file()

            # Step 3: Rename and move to output folder
            result = self.rename_and_move_file(downloaded_path)

            self.logger.info("Download and processing complete")
            return result

        finally:
            if self.driver:
                self.driver.quit()
                self.logger.info("Browser closed")


def main():
    """Test the downloader"""
    from logger_setup import setup_logging

    setup_logging()

    downloader = RBNZDownloader()
    result = downloader.download_report()

    print("\nDownload complete!")
    print(f"  Release date: {result['release_date']}")
    print(f"  Filename: {result['filename']}")
    print(f"  Timestamped output: {result['timestamped_path']}")
    print(f"  Latest output: {result['latest_path']}")


if __name__ == '__main__':
    main()
