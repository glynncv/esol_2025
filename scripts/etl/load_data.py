#!/usr/bin/env python3
"""Centralized data loading for EUC device analysis.

This module provides the DataLoader class which serves as the single source of truth
for loading and filtering EUC device data. All analysis scripts should use this class
instead of implementing their own data loading logic.

Phase 1 of ETL restructuring: DATA CAPTURE layer
"""

import pandas as pd
import sys
import yaml
from pathlib import Path
from typing import Dict, Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from data_utils import get_data_file_path, validate_data_file


class DataLoader:
    """Handles all data loading and basic filtering operations.

    This class uses ConfigManager to ensure consistent column naming and
    filtering logic across all analysis scripts.

    Attributes:
        config_manager: Instance of ConfigManager for accessing YAML configs
        esol_config: ESOL criteria configuration
        win11_config: Windows 11 criteria configuration
        data_mapping: Column name mappings from config
    """

    def __init__(self, config_manager):
        """Initialize DataLoader with configuration.

        Args:
            config_manager: ConfigManager instance from separated_esol_analyzer
        """
        self.config_manager = config_manager
        self.esol_config = config_manager.get_esol_criteria()
        self.win11_config = config_manager.get_win11_criteria()
        self.data_mapping = self.esol_config['data_mapping']

        # Cache frequently used column names
        self.action_col = self.data_mapping['action_column']
        self.edition_col = self.data_mapping['edition_column']
        self.os_col = self.data_mapping['os_column']
        self.current_os_col = self.data_mapping['current_os_column']
        self.site_col = self.data_mapping['site_column']
        self.device_name_col = self.data_mapping['device_name_column']
        self.cost_col = self.data_mapping['cost_column']

        # Load site enrichment mappings (for multi-level OKR analysis)
        self.site_mapping = self._load_site_enrichment()

    def load_raw_data(self, file_path=None):
        """Load raw EUC device data from Excel/CSV file.

        Args:
            file_path: Optional path to data file. If None, uses default resolution
                      (user arg → env var → default path)

        Returns:
            pd.DataFrame: Raw device data

        Raises:
            FileNotFoundError: If data file cannot be found
        """
        data_file = get_data_file_path(file_path)
        validate_data_file(data_file)

        # Load based on file extension
        if data_file.endswith('.xlsx'):
            return pd.read_excel(data_file)
        elif data_file.endswith('.csv'):
            return pd.read_csv(data_file)
        else:
            raise ValueError(f"Unsupported file format: {data_file}")

    def filter_esol_devices(self, df, categories=None):
        """Filter DataFrame for ESOL devices by category.

        Args:
            df: DataFrame with device data
            categories: List of ESOL categories to include.
                       Options: ['2024', '2025', '2026'] or subset
                       Default: All categories

        Returns:
            pd.DataFrame: Filtered DataFrame with only ESOL devices
        """
        if categories is None:
            categories = ['2024', '2025', '2026']

        # Get ESOL action values from config
        esol_categories = self.esol_config['esol_categories']
        action_values = []

        if '2024' in categories or 'esol_2024' in categories:
            action_values.append(esol_categories['esol_2024']['action_value'])
        if '2025' in categories or 'esol_2025' in categories:
            action_values.append(esol_categories['esol_2025']['action_value'])
        if '2026' in categories or 'esol_2026' in categories:
            action_values.append(esol_categories['esol_2026']['action_value'])

        return df[df[self.action_col].isin(action_values)].copy()

    def filter_enterprise_devices(self, df, exclude_esol=False):
        """Filter DataFrame for Enterprise edition devices.

        Args:
            df: DataFrame with device data
            exclude_esol: If True, exclude ESOL 2024/2025 devices

        Returns:
            pd.DataFrame: Filtered DataFrame with only Enterprise devices
        """
        enterprise_df = df[df[self.edition_col] == 'Enterprise'].copy()

        if exclude_esol:
            # Exclude ESOL 2024 and 2025 devices (being replaced)
            migration_categories = self.win11_config['migration_categories']
            esol_categories = self.esol_config['esol_categories']
            migration_actions = [esol_categories[cat]['action_value'] for cat in migration_categories]
            enterprise_df = enterprise_df[~enterprise_df[self.action_col].isin(migration_actions)]

        return enterprise_df

    def filter_win11_devices(self, df, check_capability=False, check_installed=False):
        """Filter DataFrame for Windows 11 devices.

        Args:
            df: DataFrame with device data
            check_capability: If True, check 'EOSL Latest OS Build Supported' (device capability)
            check_installed: If True, check 'Current OS Build' (actual installation)

        Returns:
            pd.DataFrame: Filtered DataFrame with Win11 devices
        """
        # Get Win11 patterns from config
        win11_patterns = self.win11_config['win11_patterns']
        win11_pattern = '|'.join(win11_patterns)

        if check_capability and check_installed:
            # Device supports Win11 AND has Win11 installed
            capability_mask = df[self.os_col].str.contains(win11_pattern, case=False, na=False)
            installed_mask = df[self.current_os_col].str.contains(win11_pattern, case=False, na=False)
            return df[capability_mask & installed_mask].copy()
        elif check_capability:
            # Device supports Win11 (capability check)
            mask = df[self.os_col].str.contains(win11_pattern, case=False, na=False)
            return df[mask].copy()
        elif check_installed:
            # Device has Win11 installed (actual check)
            mask = df[self.current_os_col].str.contains(win11_pattern, case=False, na=False)
            return df[mask].copy()
        else:
            # Default: check installed
            mask = df[self.current_os_col].str.contains(win11_pattern, case=False, na=False)
            return df[mask].copy()

    def filter_kiosk_devices(self, df):
        """Filter DataFrame for kiosk devices using config patterns.

        Args:
            df: DataFrame with device data

        Returns:
            pd.DataFrame: Filtered DataFrame with kiosk devices
        """
        kiosk_config = self.esol_config['kiosk_detection']
        device_patterns = kiosk_config['device_name_patterns']
        user_patterns = kiosk_config['user_loggedon_patterns']

        # Get user column name (use 'last' user logged on)
        user_col = self.data_mapping['user_columns']['last']

        # Build pattern strings
        device_pattern = '|'.join(device_patterns)
        user_pattern = '|'.join(user_patterns)

        # Apply kiosk detection logic (OR condition)
        device_mask = df[self.device_name_col].str.contains(device_pattern, na=False)
        user_mask = df[user_col].str.contains(user_pattern, case=False, na=False)

        return df[device_mask | user_mask].copy()

    def get_esol_category_actions(self, category=None):
        """Get ESOL action value(s) from config.

        Args:
            category: Specific category ('esol_2024', 'esol_2025', 'esol_2026')
                     If None, returns all as dict

        Returns:
            str or dict: Action value(s) from config
        """
        esol_categories = self.esol_config['esol_categories']

        if category:
            return esol_categories[category]['action_value']
        else:
            return {
                'esol_2024': esol_categories['esol_2024']['action_value'],
                'esol_2025': esol_categories['esol_2025']['action_value'],
                'esol_2026': esol_categories['esol_2026']['action_value']
            }

    def _load_site_enrichment(self) -> Dict[str, Dict]:
        """Load site enrichment mapping from YAML configuration.

        Loads config/esol_sites_mapped.yaml which maps site locations to
        country and SDM for multi-level OKR analysis.

        Returns:
            Dict mapping site location to enrichment data:
            {
                'Gillingham': {
                    'Site Name': 'Gillingham - United Kingdom',
                    'Location': 'Gillingham',
                    'Country': 'United Kingdom',
                    'SDM': 'Proyer, Damon'
                },
                ...
            }
        """
        config_path = Path(__file__).parent.parent.parent / 'config' / 'esol_sites_mapped.yaml'

        if not config_path.exists():
            # Return empty dict if enrichment file doesn't exist (optional feature)
            return {}

        try:
            with open(config_path, 'r') as f:
                mappings = yaml.safe_load(f)

            # Convert list of mappings to dict keyed by 'Site Location'
            return {
                mapping['Site Location']: mapping
                for mapping in mappings
                if 'Site Location' in mapping
            }
        except Exception as e:
            print(f"Warning: Could not load site enrichment: {e}")
            return {}

    def enrich_with_location_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add Country and SDM columns to DataFrame based on site mapping.

        Uses the site enrichment mapping (config/esol_sites_mapped.yaml) to add
        organizational hierarchy columns for multi-level OKR analysis.

        Args:
            df: DataFrame with device data (must have site column)

        Returns:
            pd.DataFrame: Original DataFrame with added columns:
                - 'Country': Country name from site mapping
                - 'SDM': Service Delivery Manager from site mapping
                - 'Site Name': Full site name from site mapping

        Note:
            Sites not in mapping will have 'Unknown' values for new columns.
        """
        df_enriched = df.copy()

        # Add Country column
        df_enriched['Country'] = df_enriched[self.site_col].map(
            lambda x: self.site_mapping.get(x, {}).get('Country', 'Unknown')
        )

        # Add SDM column
        df_enriched['SDM'] = df_enriched[self.site_col].map(
            lambda x: self.site_mapping.get(x, {}).get('SDM', 'Unknown')
        )

        # Add Site Name column (full name)
        df_enriched['Site Name'] = df_enriched[self.site_col].map(
            lambda x: self.site_mapping.get(x, {}).get('Site Name', x)  # Default to site location if not found
        )

        return df_enriched

    def get_site_enrichment_summary(self) -> Dict:
        """Get summary statistics about site enrichment mapping.

        Returns:
            Dict with enrichment statistics:
            {
                'total_mapped_sites': int,
                'countries': List[str],
                'sdms': List[str],
                'unmapped_message': str
            }
        """
        if not self.site_mapping:
            return {
                'total_mapped_sites': 0,
                'countries': [],
                'sdms': [],
                'unmapped_message': 'Site enrichment not available'
            }

        # Extract unique countries and SDMs
        countries = sorted(set(
            mapping.get('Country', 'Unknown')
            for mapping in self.site_mapping.values()
            if mapping.get('Country')
        ))

        sdms = sorted(set(
            mapping.get('SDM', 'Unknown')
            for mapping in self.site_mapping.values()
            if mapping.get('SDM')
        ))

        return {
            'total_mapped_sites': len(self.site_mapping),
            'countries': countries,
            'sdms': sdms,
            'unmapped_message': f'{len(self.site_mapping)} sites mapped to {len(countries)} countries, {len(sdms)} SDMs'
        }
