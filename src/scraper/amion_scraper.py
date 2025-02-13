"""
Amion.com scraper module for ED Physician Compensation System.
"""
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

load_dotenv()

class AmionScraper:
    """Handles scraping shift data from amion.com."""
    
    def __init__(self):
        """Initialize scraper with credentials."""
        self.username = os.getenv('AMION_USERNAME')
        self.password = os.getenv('AMION_PASSWORD')
        self.base_url = 'https://amion.com'
        self.driver = None
    
    def setup_driver(self) -> None:
        """Initialize Selenium WebDriver."""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=options)
    
    def login(self) -> bool:
        """Log in to amion.com."""
        try:
            self.driver.get(f"{self.base_url}/login")
            
            # Wait for login form and input credentials
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_field = self.driver.find_element(By.NAME, "password")
            
            username_field.send_keys(self.username)
            password_field.send_keys(self.password)
            password_field.submit()
            
            # Verify login success
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "calendar"))
            )
            return True
            
        except Exception as e:
            raise Exception(f"Login failed: {str(e)}")
    
    def get_shifts(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Scrape shift data for the specified date range.
        
        Args:
            start_date: Start date for shift data
            end_date: End date for shift data
            
        Returns:
            List of dictionaries containing shift data
        """
        shifts = []
        try:
            self.setup_driver()
            if not self.login():
                raise Exception("Failed to log in to amion.com")
            
            current_date = start_date
            while current_date <= end_date:
                # Navigate to the calendar page for current_date
                date_str = current_date.strftime('%Y-%m-%d')
                self.driver.get(f"{self.base_url}/calendar/{date_str}")
                
                # Wait for calendar to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "shift"))
                )
                
                # Parse the page
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                day_shifts = self._parse_shifts(soup, current_date)
                shifts.extend(day_shifts)
                
                current_date += timedelta(days=1)
                
        finally:
            if self.driver:
                self.driver.quit()
        
        return shifts
    
    def _parse_shifts(self, soup: BeautifulSoup, date: datetime) -> List[Dict]:
        """Parse shift data from the page HTML."""
        shifts = []
        shift_elements = soup.find_all(class_="shift")
        
        for element in shift_elements:
            shift = {
                'date': date.strftime('%Y-%m-%d'),
                'physician_id': element.get('data-physician-id'),
                'start_time': element.get('data-start-time'),
                'end_time': element.get('data-end-time'),
                'shift_type': element.get('data-shift-type')
            }
            shifts.append(shift)
        
        return shifts
    
    def export_to_dataframe(self, shifts: List[Dict]) -> pd.DataFrame:
        """Convert shift data to pandas DataFrame."""
        return pd.DataFrame(shifts)