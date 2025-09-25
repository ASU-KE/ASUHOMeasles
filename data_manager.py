"""
Data Manager for Measles Data Visualization
Handles data loading, backup, and validation with proper data type handling
Includes state-specific measles surveillance data scraping
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta, date
import requests
from pathlib import Path
import logging
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataManager:
    def __init__(self, data_dir="data", backup_dir="data/backups"):
        """
        Initialize DataManager with data and backup directories
        
        Args:
            data_dir (str): Directory for current data files
            backup_dir (str): Directory for backup data files
        """
        self.data_dir = Path(data_dir)
        self.backup_dir = Path(backup_dir)
        
        # Create directories if they don't exist
        self.data_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Initialize requests session for state scraping
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ASU Health Observatory Measles Surveillance Dashboard'
        })
        
        # Data source URLs
        self.data_sources = {
            'usmeasles': 'https://www.cdc.gov/wcms/vizdata/measles/MeaslesCasesYear.json',
            'usmap_cases': 'https://www.cdc.gov/wcms/vizdata/measles/MeaslesCasesMap.json',
            'vaccine_with': 'https://raw.githubusercontent.com/WorldHealthOrganization/epi50-vaccine-impact/refs/tags/v1.0/extern/raw/epi50_measles_vaccine.csv',
            'vaccine_without': 'https://raw.githubusercontent.com/WorldHealthOrganization/epi50-vaccine-impact/refs/tags/v1.0/extern/raw/epi50_measles_no_vaccine.csv'
        }
        
        # Static data file paths (stored in repo)
        self.static_files = {
            'timeline': 'data/timeline.csv',
            'mmr': 'data/MMRKCoverage.csv',
            'mmr_map': 'data/MMRKCoverage25.csv'
        }
        
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

    def download_data(self, url, timeout=30):
        """
        Download data from URL with error handling
        
        Args:
            url (str): URL to download from
            timeout (int): Request timeout in seconds
            
        Returns:
            dict or pd.DataFrame: Downloaded data
        """
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            
            if url.endswith('.json'):
                return response.json()
            else:
                # For CSV files
                from io import StringIO
                return pd.read_csv(StringIO(response.text))
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to download data from {url}: {e}")
            return None

    def save_backup(self, data, filename):
        """
        Save data as backup with timestamp
        
        Args:
            data: Data to save
            filename (str): Base filename for backup
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{filename}_{timestamp}"
        
        backup_path = self.backup_dir / backup_filename
        
        try:
            if isinstance(data, pd.DataFrame):
                backup_path = backup_path.with_suffix('.csv')
                data.to_csv(backup_path, index=False)
            else:
                backup_path = backup_path.with_suffix('.json')
                with open(backup_path, 'w') as f:
                    json.dump(data, f, indent=2)
                    
            logging.info(f"Backup saved: {backup_path}")
            
        except Exception as e:
            logging.error(f"Failed to save backup {backup_filename}: {e}")

    def load_backup(self, filename):
        """
        Load most recent backup file
        
        Args:
            filename (str): Base filename to look for
            
        Returns:
            Data from backup file or None if not found
        """
        # Find most recent backup
        backup_files = list(self.backup_dir.glob(f"{filename}_*"))
        
        if not backup_files:
            logging.warning(f"No backup found for {filename}")
            return None
            
        # Sort by modification time, get most recent
        most_recent = max(backup_files, key=lambda f: f.stat().st_mtime)
        
        try:
            if most_recent.suffix == '.csv':
                data = pd.read_csv(most_recent)
            else:
                with open(most_recent, 'r') as f:
                    data = json.load(f)
                    
            logging.info(f"Loaded backup: {most_recent}")
            return data
            
        except Exception as e:
            logging.error(f"Failed to load backup {most_recent}: {e}")
            return None

    def load_static_data(self, filename):
        """
        Load static data file from repository
        
        Args:
            filename (str): Path to static data file
            
        Returns:
            pd.DataFrame: Loaded data
        """
        try:
            filepath = Path(filename)
            if filepath.suffix == '.csv':
                return pd.read_csv(filepath)
            else:
                with open(filepath, 'r') as f:
                    return json.load(f)
                    
        except Exception as e:
            logging.error(f"Failed to load static file {filename}: {e}")
            return None

    def standardize_year_columns(self, df, year_col):
        """
        Standardize year columns to ensure consistent data types
        
        Args:
            df (pd.DataFrame): DataFrame to process
            year_col (str): Name of year column
            
        Returns:
            pd.DataFrame: DataFrame with standardized year column
        """
        if year_col in df.columns:
            # Convert to numeric, handling any string representations
            df[year_col] = pd.to_numeric(df[year_col], errors='coerce')
            # Convert to integer where possible
            df[year_col] = df[year_col].astype('Int64')  # Nullable integer
        return df

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

    def load_weekly_surveillance_data(self):
        """
        Load weekly epidemiological surveillance data for Southwest states.
        Pulls data directly from state health department websites.
        
        Returns:
            pd.DataFrame: Weekly surveillance data with current and previous week cases
        """
        try:
            logging.info("Loading Southwest states weekly measles surveillance data...")
            
            # Scrape current data
            current_data = self.scrape_all_states()
            
            # Save for historical tracking
            self.save_historical_data(current_data)
            
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
            
            if not current_data.empty:
                logging.info(f"Successfully loaded data from {len(current_data)} Southwest states")
                
                # Log data sources for attribution
                for _, row in current_data.iterrows():
                    logging.info(f"{row['state_name']}: {row['current_week_cases']} cases "
                               f"(Source: {row['data_source']})")
                
                return current_data
            else:
                logging.warning("No weekly surveillance data available, using fallback")
                return self.generate_fallback_weekly_data()
                
        except Exception as e:
            logging.error(f"Error loading weekly surveillance data: {e}")
            return self.generate_fallback_weekly_data()

    def generate_fallback_weekly_data(self):
        """
        Generate fallback weekly surveillance data when scraping fails.
        This ensures the dashboard always has data to display.
        """
        southwest_states = {
            'TX': 'Texas',
            'NM': 'New Mexico', 
            'UT': 'Utah',
            'CA': 'California',
            'NV': 'Nevada',
            'AZ': 'Arizona'
        }
        
        fallback_data = []
        current_epi_week = self.get_current_epi_week()[0]
        
        for state_code, state_name in southwest_states.items():
            fallback_data.append({
                'state': state_code,
                'state_name': state_name,
                'current_week_cases': 0,  # Conservative fallback
                'previous_week_cases': 0,
                'data_source': f'{state_name} Department of Health (Data temporarily unavailable)',
                'source_url': 'N/A',
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'update_schedule': 'Weekly',
                'epi_week': current_epi_week,
                'epi_year': datetime.now().year,
                'attribution': f'Data courtesy of {state_name} Department of Health'
            })
        
        return pd.DataFrame(fallback_data)

    def fetch_all_data(self):
        """
        Fetch all required data sources with fallback to backups
        
        Returns:
            dict: Dictionary containing all loaded datasets
        """
        data = {}
        
        # Load static files
        for key, filepath in self.static_files.items():
            static_data = self.load_static_data(filepath)
            if static_data is not None:
                # Standardize year columns if they exist
                if key == 'mmr' and 'year' in static_data.columns:
                    static_data = self.standardize_year_columns(static_data, 'year')
                data[key] = static_data
                logging.info(f"Loaded static data: {key}")
            else:
                logging.error(f"Failed to load static data: {key}")
                return None

        # Download dynamic data with backup fallback
        for key, url in self.data_sources.items():
            downloaded_data = self.download_data(url)
            
            if downloaded_data is not None:
                # Convert to DataFrame - handle both dict and list formats from JSON APIs
                if isinstance(downloaded_data, (dict, list)):
                    downloaded_data = pd.DataFrame(downloaded_data)
                
                # Standardize year columns
                if 'year' in downloaded_data.columns:
                    downloaded_data = self.standardize_year_columns(downloaded_data, 'year')
                    
                data[key] = downloaded_data
                self.save_backup(downloaded_data, key)
                logging.info(f"Downloaded fresh data: {key}")
                
            else:
                # Try to load from backup
                backup_data = self.load_backup(key)
                if backup_data is not None:
                    if isinstance(backup_data, (dict, list)):
                        backup_data = pd.DataFrame(backup_data)
                    
                    # Standardize year columns in backup data too
                    if isinstance(backup_data, pd.DataFrame) and 'year' in backup_data.columns:
                        backup_data = self.standardize_year_columns(backup_data, 'year')
                        
                    data[key] = backup_data
                    logging.warning(f"Using backup data for: {key}")
                else:
                    logging.error(f"No data available for: {key}")
                    return None

        # Process and merge data
        processed_data = self.process_data(data)
        return processed_data

    def process_data(self, raw_data):
        """
        Process and clean raw data with proper data type handling
        
        Args:
            raw_data (dict): Dictionary of raw datasets
            
        Returns:
            dict: Dictionary of processed datasets
        """
        processed = {}
        
        try:
            # Timeline data - already clean, ensure Year is numeric
            timeline = raw_data['timeline'].copy()
            if 'Year' in timeline.columns:
                timeline['Year'] = pd.to_numeric(timeline['Year'], errors='coerce')
            processed['timeline'] = timeline
            logging.info("Processed timeline data successfully")
            
            # US Measles data - ensure year is numeric
            usmeasles = raw_data['usmeasles'].copy()
            if 'year' in usmeasles.columns:
                usmeasles = self.standardize_year_columns(usmeasles, 'year')
            processed['usmeasles'] = usmeasles
            logging.info("Processed US measles data successfully")
            
            # MMR Coverage data - ensure year is numeric
            mmr = raw_data['mmr'].copy()
            if 'year' in mmr.columns:
                mmr = self.standardize_year_columns(mmr, 'year')
            processed['mmr'] = mmr
            logging.info("Processed MMR data successfully")
            
            # Process map data with proper data type handling
            logging.info("Processing map data...")
            mmr_map = raw_data['mmr_map'].rename(columns={'Geography': 'geography'})
            usmap_cases = raw_data['usmap_cases'].copy()
            
            # Ensure consistent data types for merge
            if 'year' in mmr_map.columns:
                mmr_map = self.standardize_year_columns(mmr_map, 'year')
            if 'year' in usmap_cases.columns:
                usmap_cases = self.standardize_year_columns(usmap_cases, 'year')
            
            # Debug: Check data types and sample data before merge
            logging.info(f"mmr_map columns: {list(mmr_map.columns)}")
            logging.info(f"usmap_cases columns: {list(usmap_cases.columns)}")
            
            # Merge map data
            usmap = usmap_cases.merge(mmr_map, on='geography', how='left')
            
            # Filter out NYC and DC as they are not states
            usmap = usmap[~usmap['geography'].isin(['New York City', 'District of Columbia'])].copy()
            
            # Debug merge results
            logging.info(f"After merge and filtering, usmap has {len(usmap)} rows")
            logging.info(f"Merge columns: {list(usmap.columns)}")
            
            # Handle year filtering - check both possible year columns
            year_col = 'year_x' if 'year_x' in usmap.columns else 'year'
            if year_col in usmap.columns:
                # Convert year column to numeric
                usmap[year_col] = pd.to_numeric(usmap[year_col], errors='coerce')
                available_years = usmap[year_col].dropna().unique()
                logging.info(f"Available years in merged data: {sorted(available_years)}")
                
                # Filter to 2025 data as specified in original code
                usmap_2025 = usmap[usmap[year_col] == 2025].copy()
                logging.info(f"After filtering to 2025: {len(usmap_2025)} rows")
                
                # If no 2025 data, use most recent year
                if len(usmap_2025) == 0:
                    logging.warning("No 2025 data found. Checking for most recent year instead...")
                    if len(usmap) > 0:
                        most_recent_year = usmap[year_col].max()
                        logging.info(f"Most recent year available: {most_recent_year}")
                        usmap_2025 = usmap[usmap[year_col] == most_recent_year].copy()
                        logging.info(f"Using {most_recent_year} data: {len(usmap_2025)} rows")
                
                usmap = usmap_2025
            
            # Convert Estimate (%) to numeric and handle any string values
            if 'Estimate (%)' in usmap.columns:
                usmap['Estimate (%)'] = pd.to_numeric(usmap['Estimate (%)'], errors='coerce')
            
            # Ensure cases column is numeric for calculations
            cases_col = next((c for c in ['cases_calendar_year', 'cases', 'Cases'] if c in usmap.columns), None)
            if cases_col and cases_col in usmap.columns:
                usmap[cases_col] = pd.to_numeric(usmap[cases_col], errors='coerce')
            
            processed['usmap'] = usmap
            logging.info("Processed map data successfully")
            
            # Process vaccine impact data
            logging.info("Processing vaccine impact data...")
            vax_df = raw_data['vaccine_with'].copy()
            no_vax_df = raw_data['vaccine_without'].copy()
            
            # Ensure year columns are consistent
            if 'year' in vax_df.columns:
                vax_df = self.standardize_year_columns(vax_df, 'year')
            if 'year' in no_vax_df.columns:
                no_vax_df = self.standardize_year_columns(no_vax_df, 'year')
            
            # Debug: Check vaccine data types
            logging.info(f"vax_df type: {type(vax_df)}")
            logging.info(f"no_vax_df type: {type(no_vax_df)}")
            
            # Filter for USA data
            vax_usa = vax_df[vax_df['iso'] == 'USA'].copy()
            no_vax_usa = no_vax_df[no_vax_df['iso'] == 'USA'].copy()
            
            # Merge vaccine data
            merged_vaccine = pd.merge(no_vax_usa, vax_usa, on='year', suffixes=('_no_vaccine', '_vaccine'))
            
            # Calculate lives saved - ensure numeric columns
            numeric_cols = ['mean_deaths_no_vaccine', 'mean_deaths_vaccine', 
                           'ub_deaths_no_vaccine', 'lb_deaths_vaccine',
                           'lb_deaths_no_vaccine', 'ub_deaths_vaccine']
            
            for col in numeric_cols:
                if col in merged_vaccine.columns:
                    merged_vaccine[col] = pd.to_numeric(merged_vaccine[col], errors='coerce')
            
            merged_vaccine['lives_saved'] = (merged_vaccine['mean_deaths_no_vaccine'] - 
                                           merged_vaccine['mean_deaths_vaccine'])
            merged_vaccine['lives_saved_ub'] = (merged_vaccine['ub_deaths_no_vaccine'] - 
                                              merged_vaccine['lb_deaths_vaccine'])
            merged_vaccine['lives_saved_lb'] = (merged_vaccine['lb_deaths_no_vaccine'] - 
                                              merged_vaccine['ub_deaths_vaccine'])
            merged_vaccine = merged_vaccine.sort_values('year')
            
            processed['vaccine_impact'] = merged_vaccine
            logging.info("Processed vaccine impact data successfully")
            
            # Add the new weekly surveillance data
            try:
                weekly_surveillance = self.load_weekly_surveillance_data()
                processed['weekly_surveillance'] = weekly_surveillance
                logging.info("Weekly surveillance data processed successfully")
            except Exception as e:
                logging.error(f"Error processing weekly surveillance data: {e}")
                processed['weekly_surveillance'] = self.generate_fallback_weekly_data()
            
            return processed
            
        except Exception as e:
            logging.error(f"Error in process_data: {e}")
            logging.error(f"Available keys in raw_data: {list(raw_data.keys())}")
            for key, value in raw_data.items():
                logging.error(f"{key}: type={type(value)}, shape={getattr(value, 'shape', 'No shape')}")
            return None

    def validate_data(self, data):
        """
        Validate data quality and completeness
        
        Args:
            data (dict): Dictionary of datasets to validate
            
        Returns:
            dict: Validation results
        """
        validation_results = {}
        
        required_datasets = ['timeline', 'usmeasles', 'mmr', 'usmap', 'vaccine_impact', 'weekly_surveillance']
        
        for dataset_name in required_datasets:
            if dataset_name not in data:
                validation_results[dataset_name] = {'valid': False, 'error': 'Dataset missing'}
                continue
                
            df = data[dataset_name]
            
            if df.empty:
                validation_results[dataset_name] = {'valid': False, 'error': 'Dataset is empty'}
                continue
                
            # Dataset-specific validation
            if dataset_name == 'timeline':
                required_cols = ['Year', 'Cases']
                missing_cols = [col for col in required_cols if col not in df.columns]
                if missing_cols:
                    validation_results[dataset_name] = {
                        'valid': False, 
                        'error': f'Missing columns: {missing_cols}'
                    }
                else:
                    validation_results[dataset_name] = {'valid': True, 'rows': len(df)}
                    
            elif dataset_name == 'usmeasles':
                required_cols = ['year', 'cases']
                missing_cols = [col for col in required_cols if col not in df.columns]
                if missing_cols:
                    validation_results[dataset_name] = {
                        'valid': False, 
                        'error': f'Missing columns: {missing_cols}'
                    }
                else:
                    validation_results[dataset_name] = {'valid': True, 'rows': len(df)}
                    
            elif dataset_name == 'weekly_surveillance':
                required_cols = ['state', 'state_name', 'current_week_cases', 'previous_week_cases']
                missing_cols = [col for col in required_cols if col not in df.columns]
                if missing_cols:
                    validation_results[dataset_name] = {
                        'valid': False, 
                        'error': f'Missing columns: {missing_cols}'
                    }
                else:
                    validation_results[dataset_name] = {'valid': True, 'rows': len(df)}
                    
            # Add more specific validation as needed
            else:
                validation_results[dataset_name] = {'valid': True, 'rows': len(df)}
                
        return validation_results
