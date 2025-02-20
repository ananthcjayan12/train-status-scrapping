#!/usr/bin/env python3
"""
Train Status Scraper
This script scrapes train running status information from confirmtkt.com
"""

import os
import sys
import logging
import platform
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from utils.helpers import validate_train_number, calculate_date

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/train_status.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class TrainStatusScraper:
    """Class to handle train status scraping operations"""
    
    def __init__(self):
        """Initialize the scraper with webdriver setup"""
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://www.confirmtkt.com/train-running-status"
        self.driver = None
        self.setup_driver()

    def setup_driver(self):
        """Set up Chrome webdriver with appropriate options"""
        try:
            chrome_options = Options()
            # chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--remote-debugging-port=9222")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-popup-blocking")
            
            # Add additional options for M1/M2 Mac
            if platform.system() == 'Darwin' and platform.machine() == 'arm64':
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--disable-software-rasterizer")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(20)  # Increased wait time
            self.logger.info("WebDriver setup completed successfully")
        except Exception as e:
            self.logger.error(f"Failed to setup WebDriver: {str(e)}")
            raise

    def wait_and_find_element(self, by, value, timeout=20, retries=3):
        """
        Wait for element to be present and return it with retries
        
        Args:
            by: Type of locator
            value: Locator value
            timeout: Maximum time to wait (seconds)
            retries: Number of times to retry
            
        Returns:
            WebElement: Found element
        """
        for attempt in range(retries):
            try:
                wait = WebDriverWait(self.driver, timeout)
                element = wait.until(
                    EC.presence_of_element_located((by, value))
                )
                return element
            except Exception as e:
                if attempt == retries - 1:  # Last attempt
                    raise
                self.logger.warning(f"Attempt {attempt + 1} failed, retrying...")
                time.sleep(2)  # Wait before retry

    def enter_train_number(self, train_number: str) -> bool:
        """
        Enter train number and initiate search
        
        Args:
            train_number: Train number to search
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Wait for page to load completely
            self.wait_and_find_element(By.TAG_NAME, "body")
            
            # XPath for the input field
            input_xpath = "//input[@name='train']"
            
            # Find the input field using XPath
            input_field = self.wait_and_find_element(
                By.XPATH, 
                input_xpath,
                timeout=30  # Increased timeout
            )
            
            # Wait for the input field to be clickable using XPath
            wait = WebDriverWait(self.driver, 20)
            wait.until(EC.element_to_be_clickable((By.XPATH, input_xpath)))
            
            # Click the input field to focus
            input_field.click()
            time.sleep(1)  # Small pause after click
            
            # Re-find the input field to get a fresh reference and avoid stale element error
            input_field = self.wait_and_find_element(By.XPATH, input_xpath, timeout=30)

            
            # Type the train number with small delays between characters
            for digit in train_number:
                input_field.send_keys(digit)
                time.sleep(0.2)  # Slightly longer delay between keystrokes for typeahead
                
            self.logger.info(f"Entered train number: {train_number}")

            # Wait for typeahead suggestions to settle
            time.sleep(2)

            # Find and click the check status button using its ID
            self.logger.info("Waiting for check status button")
            check_status_btn = self.driver.find_element(By.ID, "getRunnungStatus")
            self.logger.info("Found check status button")
            check_status_btn.click()
            self.logger.info("Clicked check status button")
            
            # Wait for results to load
            self.wait_and_find_element(
                By.CLASS_NAME, 
                "train-update",
                timeout=30
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to enter train number: {str(e)}")
            return False

    def select_date(self, day_selection: int) -> bool:
        """
        Select the appropriate date based on day selection
        
        Args:
            day_selection (int): Day selection (1 for today, 2 for yesterday, etc.)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Wait for the date select element to be present
            date_select = self.wait_and_find_element(
                By.ID,
                "selectdate",
                timeout=30
            )
            
            # Map day_selection to the expected option
            day_map = {
                1: "today",
                2: "yesterday",
                3: "2 days ago",
                4: "3 days ago",
                5: "tommorrow"
            }
            
            # Find the option with matching data-day attribute
            target_day = day_map.get(day_selection, "today")  # Default to today if invalid selection
            
            # Find all options
            options = date_select.find_elements(By.TAG_NAME, "option")
            
            # Find and select the matching option
            for option in options:
                if option.get_attribute("data-day") == target_day:
                    option.click()
                    self.logger.info(f"Selected date: {option.get_attribute('value')}")
                    return True
                    
            self.logger.warning(f"Could not find date option for day selection: {day_selection}")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to select date: {str(e)}")
            return False

    def get_train_status(self, train_number: str, day_selection: int) -> dict:
        """
        Get the current status of a train
        
        Args:
            train_number (str): The train number to check
            day_selection (int): Day selection (1 for today, 2 for yesterday, etc.)
            
        Returns:
            dict: Train status information
        """
        try:
            # Validate train number
            if not validate_train_number(train_number):
                raise ValueError(f"Invalid train number format: {train_number}")

            # Navigate to the website
            self.driver.get(self.base_url)
            self.logger.info(f"Checking status for train number: {train_number}")
            
            # Wait for page to load completely
            time.sleep(5)  # Give extra time for page to load
            
            # Enter train number and check status
            if not self.enter_train_number(train_number):
                raise Exception("Failed to enter train number and get status")

            # Select the date
            if not self.select_date(day_selection):
                self.logger.warning("Could not select date, proceeding with default date")

            # Extract current status information
            try:
                # Get the last departed station
                departed_station = self.wait_and_find_element(
                    By.ID, "departed-stnCode"
                ).text.strip()
                
                # Get last updated time
                update_info = self.wait_and_find_element(
                    By.CLASS_NAME, "train-update__time"
                ).text.strip()
                
                # Get delay status from the table
                delay_status = "On time"  # Default value
                try:
                    delay_cell = self.wait_and_find_element(
                        By.CSS_SELECTOR, 
                        ".running-status .rs__station-row:last-child .col-xs-2:last-child"
                    )
                    if delay_cell.text.strip() != "-":
                        delay_status = delay_cell.text.strip()
                except:
                    self.logger.warning("Could not find delay status")

                # Get next station
                next_station = ""
                try:
                    next_station_row = self.wait_and_find_element(
                        By.CSS_SELECTOR,
                        ".running-status .rs__station-row:not(.passed):first-child .rs__station-name"
                    )
                    next_station = next_station_row.text.strip()
                except:
                    self.logger.warning("Could not find next station")
                
                return {
                    "train_number": train_number,
                    "current_status": {
                        "last_station": departed_station,
                        "next_station": next_station,
                        "last_updated": update_info,
                        "delay_status": delay_status
                    }
                }
                
            except (TimeoutException, NoSuchElementException) as e:
                self.logger.error(f"Failed to extract train status: {str(e)}")
                raise
            
        except Exception as e:
            self.logger.error(f"Error getting train status: {str(e)}")
            raise
        
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
            self.logger.info("WebDriver cleaned up successfully")

def main():
    """Main function to run the scraper"""
    try:
        # Get command line arguments
        if len(sys.argv) != 3:
            print("Usage: python train_status_scraper.py <train_number> <day_selection>")
            sys.exit(1)
            
        train_number = sys.argv[1]
        day_selection = int(sys.argv[2])
        
        # Initialize and run scraper
        scraper = TrainStatusScraper()
        try:
            result = scraper.get_train_status(train_number, day_selection)
            print(result)
        finally:
            scraper.cleanup()
            
    except Exception as e:
        logging.error(f"Application error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 