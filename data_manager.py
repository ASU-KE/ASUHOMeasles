"""
Data Manager for Measles Data Visualization
Handles data loading, backup, and validation
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
import requests
from pathlib import Path
import logging

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
                data[key] = static_data
                logging.info(f"Loaded static data: {key}")
            else:
                logging.error(f"Failed to load static data: {key}")
                return None

        # Download dynamic data with backup fallback
        for key, url in self.data_sources.items():
            downloaded_data = self.download_data(url)
            
            if downloaded_data is not None:
                # Convert to DataFrame if JSON
                if isinstance(downloaded_data, dict):
                    downloaded_data = pd.DataFrame(downloaded_data)
                    
                data[key] = downloaded_data
                self.save_backup(downloaded_data, key)
                logging.info(f"Downloaded fresh data: {key}")
                
            else:
                # Try to load from backup
                backup_data = self.load_backup(key)
                if backup_data is not None:
                    if isinstance(backup_data, dict):
                        backup_data = pd.DataFrame(backup_data)
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
        Process and clean raw data
        
        Args:
            raw_data (dict): Dictionary of raw datasets
            
        Returns:
            dict: Dictionary of processed datasets
        """
        processed = {}
        
        # Timeline data - already clean
        processed['timeline'] = raw_data['timeline']
        
        # US Measles data - already clean
        processed['usmeasles'] = raw_data['usmeasles']
        
        # MMR Coverage data
        processed['mmr'] = raw_data['mmr']
        
        # Process map data
        mmr_map = raw_data['mmr_map'].rename(columns={'Geography': 'geography'})
        usmap_cases = raw_data['usmap_cases']
        
        # Merge map data
        usmap = usmap_cases.merge(mmr_map, on='geography', how='left')
        usmap = usmap[usmap['year_x'] == 2025].copy()
        usmap['Estimate (%)'] = pd.to_numeric(usmap['Estimate (%)'], errors='coerce')
        processed['usmap'] = usmap
        
        # Process vaccine impact data
        vax_df = raw_data['vaccine_with']
        no_vax_df = raw_data['vaccine_without']
        
        vax_usa = vax_df[vax_df['iso'] == 'USA'].copy()
        no_vax_usa = no_vax_df[no_vax_df['iso'] == 'USA'].copy()
        
        merged_vaccine = pd.merge(no_vax_usa, vax_usa, on='year', suffixes=('_no_vaccine', '_vaccine'))
        merged_vaccine['lives_saved'] = (merged_vaccine['mean_deaths_no_vaccine'] - 
                                       merged_vaccine['mean_deaths_vaccine'])
        merged_vaccine['lives_saved_ub'] = (merged_vaccine['ub_deaths_no_vaccine'] - 
                                          merged_vaccine['lb_deaths_vaccine'])
        merged_vaccine['lives_saved_lb'] = (merged_vaccine['lb_deaths_no_vaccine'] - 
                                          merged_vaccine['ub_deaths_vaccine'])
        merged_vaccine = merged_vaccine.sort_values('year')
        
        processed['vaccine_impact'] = merged_vaccine
        
        return processed

    def validate_data(self, data):
        """
        Validate data quality and completeness
        
        Args:
            data (dict): Dictionary of datasets to validate
            
        Returns:
            dict: Validation results
        """
        validation_results = {}
        
        required_datasets = ['timeline', 'usmeasles', 'mmr', 'usmap', 'vaccine_impact']
        
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
                    
            # Add more specific validation as needed
            else:
                validation_results[dataset_name] = {'valid': True, 'rows': len(df)}
                
        return validation_results
