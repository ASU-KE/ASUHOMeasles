"""
State-Specific Measles Surveillance Data Scraper
Pulls data directly from state health department websites to give proper credit
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from bs4 import BeautifulSoup
import json
import re
from typing import Dict, List, Optional, Tuple

class SouthwestStatesScraper:
    """
    Scrapes measles surveillance data from Southwest state health departments.
    Gives proper attribution and credit to each state's public health system.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ASU Health Observatory Measles Surveillance Dashboard'
        })
        
        # State-specific endpoints and update schedules
        self.state_configs = {
            'TX': {
                'name': 'Texas',
                'agency': 'Texas Department of State Health Services',
                'update_schedule': 'Weekly on Tuesdays',
                'endpoints': {
                    'main': 'https://www.dshs.texas.gov/measles',
                    'outbreak': 'https://www.dshs.texas.gov/news-alerts/measles-outbreak-2025',
                    'data_api': 'https://www.dshs.texas.gov/api/measles-data'  # If available
                }
            },
            'NM': {
                'name': 'New Mexico', 
                'agency': 'New Mexico Department of Health',
                'update_schedule': 'Tuesday and Friday before noon MST',
                'endpoints': {
                    'main': 'https://www.nmhealth.org/about/erd/ideb/mog/',
                    'dashboard': 'https://www.nmhealth.org/data/measles-dashboard/',
                    'cases': 'https://www.nmhealth.org/about/erd/ideb/mog/news/'
                }
            },
            'UT': {
                'name': 'Utah',
                'agency': 'Utah Department of Health and Human Services',
                'update_schedule': 'Weekdays by 3:00 PM MST',
                'endpoints': {
                    'main': 'https://epi.utah.gov/measles-response/',
                    'surveillance': 'https://epi.utah.gov/measles/',
                    'ibis': 'https://ibis.utah.gov/ibisph-view/indicator/view/MeasCas.UT_US.html'
                }
            },
            'CA': {
                'name': 'California',
                'agency': 'California Department of Public Health', 
                'update_schedule': 'Weekly',
                'endpoints': {
                    'main': 'https://www.cdph.ca.gov/Programs/CID/DCDC/Pages/Immunization/measles.aspx',
                    'surveillance': 'https://www.cdph.ca.gov/Programs/OPA/Pages/measles-data.aspx'
                }
            },
            'NV': {
                'name': 'Nevada',
                'agency': 'Nevada Division of Public and Behavioral Health',
                'update_schedule': 'Weekly',
                'endpoints': {
                    'main': 'https://dpbh.nv.gov/Reg/CD/measles/',
                    'surveillance': 'https://dpbh.nv.gov/Programs/CD/CD-Home/'
                }
            },
            'AZ': {
                'name': 'Arizona',
                'agency': 'Arizona Department of Health Services',
                'update_schedule': 'Weekly', 
                'endpoints': {
                    'main': 'https://www.azdhs.gov/preparedness/epidemiology-disease-control/infectious-disease-epidemiology/index.php#communicable-diseases',
                    'surveillance': 'https://www.azdhs.gov/documents/preparedness/epidemiology-disease-control/measles-surveillance-data.pdf'
                }
            }
        }

    def get_current_epi_week(self) -> Tuple[int, int]:
        """Calculate current CDC epidemiological week and year."""
        today = datetime.now()
        
        # CDC epi week starts on Sunday
        # Find the first epi week of the year
        jan4 = datetime(today.year, 1, 4)  # Week containing Jan 4 is always week 1
        jan4_weekday = jan4.weekday()  # Monday = 0, Sunday = 6
        
        # Find the Sunday of week 1
        if jan4_weekday == 6:  # Jan 4 is Sunday
            week1_sunday = jan4
        else:
            week1_sunday = jan4 - timedelta(days=(jan4_weekday + 1) % 7)
        
        # Calculate current epi week
        days_diff = (today - week1_sunday).days
        current_epi_week = (days_diff // 7) + 1
        
        # Handle year boundaries
        if current_epi_week <= 0:
            # We're in the last epi week of previous year
            return 52, today.year - 1
        elif current_epi_week >= 53:
            # Check if this should be week 1 of next year
            next_jan4 = datetime(today.year + 1, 1, 4)
            next_jan4_weekday = next_jan4.weekday()
            if next_jan4_weekday <= 3:  # Thu, Fri, Sat, Sun (Thu=3, Fri=4, Sat=5, Sun=6)
                return 1, today.year + 1
            else:
                return 53, today.year
        
        return min(current_epi_week, 53), today.year

    def scrape_texas_data(self) -> Optional[Dict]:
        """
        Scrape measles data from Texas DSHS.
        Texas updates weekly on Tuesdays.
        """
        try:
            # Get the main measles outbreak page
            response = self.session.get(self.state_configs['TX']['endpoints']['outbreak'], timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for case count in the content
            content_text = soup.get_text()
            
            # Search for case count patterns
            case_patterns = [
                r'(\d+)\s+cases?\s+have\s+been\s+confirmed',
                r'reporting\s+(\d+)\s+confirmed\s+cases',
                r'total\s+of\s+(\d+)\s+measles\s+cases'
            ]
            
            current_week_cases = 0
            for pattern in case_patterns:
                match = re.search(pattern, content_text, re.IGNORECASE)
                if match:
                    current_week_cases = int(match.group(1))
                    break
            
            # Get previous week data (this would require parsing historical updates)
            # For now, we'll set this to 0 and implement proper historical tracking
            previous_week_cases = 0  # TODO: Implement historical data tracking
            
            return {
                'state': 'TX',
                'state_name': 'Texas',
                'current_week_cases': current_week_cases,
                'previous_week_cases': previous_week_cases,
                'data_source': 'Texas Department of State Health Services',
                'source_url': self.state_configs['TX']['endpoints']['outbreak'],
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'update_schedule': self.state_configs['TX']['update_schedule']
            }
            
        except Exception as e:
            logging.error(f"Error scraping Texas data: {e}")
            return None

    def scrape_new_mexico_data(self) -> Optional[Dict]:
        """
        Scrape measles data from New Mexico DOH.
        Updates Tuesday and Friday before noon MST.
        """
        try:
            # Get the main measles page
            response = self.session.get(self.state_configs['NM']['endpoints']['main'], timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            content_text = soup.get_text()
            
            # Look for case count
            case_patterns = [
                r'New\s+Mexico.*?reports?\s+(\d+)\s+measles\s+cases?',
                r'total\s+of\s+(\d+)\s+cases?',
                r'(\d+)\s+confirmed\s+cases?'
            ]
            
            current_week_cases = 0
            for pattern in case_patterns:
                match = re.search(pattern, content_text, re.IGNORECASE)
                if match:
                    current_week_cases = int(match.group(1))
                    break
            
            previous_week_cases = 0  # TODO: Implement historical tracking
            
            return {
                'state': 'NM',
                'state_name': 'New Mexico',
                'current_week_cases': current_week_cases,
                'previous_week_cases': previous_week_cases,
                'data_source': 'New Mexico Department of Health',
                'source_url': self.state_configs['NM']['endpoints']['main'],
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'update_schedule': self.state_configs['NM']['update_schedule']
            }
            
        except Exception as e:
            logging.error(f"Error scraping New Mexico data: {e}")
            return None

    def scrape_utah_data(self) -> Optional[Dict]:
        """
        Scrape measles data from Utah DHHS.
        Updates weekdays by 3:00 PM MST.
        """
        try:
            response = self.session.get(self.state_configs['UT']['endpoints']['main'], timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            content_text = soup.get_text()
            
            # Look for case count in Utah's format
            case_patterns = [
                r'total\s+of\s+(\d+)\s+positive\s+measles\s+cases',
                r'(\d+)\s+confirmed\s+cases?\s+in\s+Utah',
                r'Utah.*?(\d+).*?cases?'
            ]
            
            current_week_cases = 0
            for pattern in case_patterns:
                match = re.search(pattern, content_text, re.IGNORECASE)
                if match:
                    current_week_cases = int(match.group(1))
                    break
            
            previous_week_cases = 0  # TODO: Implement historical tracking
            
            return {
                'state': 'UT',
                'state_name': 'Utah',
                'current_week_cases': current_week_cases,
                'previous_week_cases': previous_week_cases,
                'data_source': 'Utah Department of Health and Human Services',
                'source_url': self.state_configs['UT']['endpoints']['main'],
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'update_schedule': self.state_configs['UT']['update_schedule']
            }
            
        except Exception as e:
            logging.error(f"Error scraping Utah data: {e}")
            return None

    def scrape_california_data(self) -> Optional[Dict]:
        """
        Scrape measles data from California DPH.
        """
        try:
            response = self.session.get(self.state_configs['CA']['endpoints']['main'], timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            content_text = soup.get_text()
            
            # California case patterns
            case_patterns = [
                r'California.*?(\d+).*?measles\s+cases?',
                r'(\d+)\s+confirmed\s+cases?\s+in\s+California',
                r'total\s+of\s+(\d+)\s+cases?'
            ]
            
            current_week_cases = 0
            for pattern in case_patterns:
                match = re.search(pattern, content_text, re.IGNORECASE)
                if match:
                    current_week_cases = int(match.group(1))
                    break
            
            return {
                'state': 'CA',
                'state_name': 'California',
                'current_week_cases': current_week_cases,
                'previous_week_cases': 0,  # TODO: Historical tracking
                'data_source': 'California Department of Public Health',
                'source_url': self.state_configs['CA']['endpoints']['main'],
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'update_schedule': self.state_configs['CA']['update_schedule']
            }
            
        except Exception as e:
            logging.error(f"Error scraping California data: {e}")
            return None

    def scrape_nevada_data(self) -> Optional[Dict]:
        """
        Scrape measles data from Nevada DPBH.
        """
        try:
            response = self.session.get(self.state_configs['NV']['endpoints']['main'], timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            content_text = soup.get_text()
            
            # Nevada case patterns
            current_week_cases = 0  # Will need to implement proper parsing
            
            return {
                'state': 'NV',
                'state_name': 'Nevada',
                'current_week_cases': current_week_cases,
                'previous_week_cases': 0,
                'data_source': 'Nevada Division of Public and Behavioral Health',
                'source_url': self.state_configs['NV']['endpoints']['main'],
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'update_schedule': self.state_configs['NV']['update_schedule']
            }
            
        except Exception as e:
            logging.error(f"Error scraping Nevada data: {e}")
            return None

    def scrape_arizona_data(self) -> Optional[Dict]:
        """
        Scrape measles data from Arizona DHS.
        """
        try:
            response = self.session.get(self.state_configs['AZ']['endpoints']['main'], timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            content_text = soup.get_text()
            
            # Arizona case patterns - they often have county-specific data
            current_week_cases = 0  # Will need specific parsing for Arizona format
            
            return {
                'state': 'AZ',
                'state_name': 'Arizona',
                'current_week_cases': current_week_cases,
                'previous_week_cases': 0,
                'data_source': 'Arizona Department of Health Services',
                'source_url': self.state_configs['AZ']['endpoints']['main'],
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'update_schedule': self.state_configs['AZ']['update_schedule']
            }
            
        except Exception as e:
            logging.error(f"Error scraping Arizona data: {e}")
            return None

    def scrape_all_states(self) -> pd.DataFrame:
        """
        Scrape measles data from all Southwest states and return as DataFrame.
        """
        scrapers = {
            'TX': self.scrape_texas_data,
            'NM': self.scrape_new_mexico_data,
            'UT': self.scrape_utah_data,
            'CA': self.scrape_california_data,
            'NV': self.scrape_nevada_data,
            'AZ': self.scrape_arizona_data
        }
        
        all_data = []
        current_epi_week, current_year = self.get_current_epi_week()
        
        for state_code, scraper_func in scrapers.items():
            try:
                state_data = scraper_func()
                if state_data:
                    state_data['epi_week'] = current_epi_week
                    state_data['epi_year'] = current_year
                    all_data.append(state_data)
                else:
                    # Fallback with zero cases if scraping fails
                    all_data.append({
                        'state': state_code,
                        'state_name': self.state_configs[state_code]['name'],
                        'current_week_cases': 0,
                        'previous_week_cases': 0,
                        'data_source': self.state_configs[state_code]['agency'],
                        'source_url': 'Data unavailable',
                        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'update_schedule': self.state_configs[state_code]['update_schedule'],
                        'epi_week': current_epi_week,
                        'epi_year': current_year
                    })
                    
            except Exception as e:
                logging.error(f"Failed to scrape {state_code}: {e}")
                continue
        
        df = pd.DataFrame(all_data)
        
        # Add attribution information
        df['collection_method'] = 'State health department web scraping'
        df['attribution'] = df.apply(
            lambda row: f"Data courtesy of {row['data_source']}", axis=1
        )
        
        return df

    def save_historical_data(self, df: pd.DataFrame, filepath: str = 'data/southwest_measles_weekly.csv'):
        """
        Save current data and maintain historical record for week-over-week comparisons.
        """
        try:
            # Try to load existing data
            try:
                historical_df = pd.read_csv(filepath)
                historical_df['last_updated'] = pd.to_datetime(historical_df['last_updated'])
            except FileNotFoundError:
                historical_df = pd.DataFrame()
            
            # Add current data
            current_df = df.copy()
            current_df['last_updated'] = pd.to_datetime(current_df['last_updated'])
            
            # Combine with historical data
            if not historical_df.empty:
                all_data = pd.concat([historical_df, current_df], ignore_index=True)
                # Remove duplicates, keeping latest
                all_data = all_data.drop_duplicates(
                    subset=['state', 'epi_week', 'epi_year'], 
                    keep='last'
                )
            else:
                all_data = current_df
            
            # Save updated dataset
            all_data.to_csv(filepath, index=False)
            logging.info(f"Historical data saved to {filepath}")
            
        except Exception as e:
            logging.error(f"Error saving historical data: {e}")

# Integration function for data_manager.py
def load_southwest_weekly_surveillance_data() -> pd.DataFrame:
    """
    Function to integrate with existing data_manager.py
    Returns weekly surveillance data for Southwest states with proper attribution.
    """
    scraper = SouthwestStatesScraper()
    
    # Scrape current data
    current_data = scraper.scrape_all_states()
    
    # Save for historical tracking
    scraper.save_historical_data(current_data)
    
    # Calculate previous week cases from historical data if available
    try:
        historical_df = pd.read_csv('data/southwest_measles_weekly.csv')
        current_epi_week = current_data['epi_week'].iloc[0] if not current_data.empty else 1
        
        for idx, row in current_data.iterrows():
            # Look for previous week data
            prev_week_data = historical_df[
                (historical_df['state'] == row['state']) & 
                (historical_df['epi_week'] == current_epi_week - 1)
            ]
            if not prev_week_data.empty:
                current_data.at[idx, 'previous_week_cases'] = prev_week_data['current_week_cases'].iloc[0]
                
    except Exception as e:
        logging.warning(f"Could not load historical data for comparison: {e}")
    
    return current_data
