"""Burndown calculation module for tracking device migration and replacement progress."""
from datetime import datetime
from typing import Dict, List, Optional, Union
import pandas as pd


class BurndownCalculator:
    """Calculate burndown metrics for device migration and replacement tracking.

    Provides unified burndown calculations for both ESOL replacement and Windows 11
    upgrade projects, eliminating duplicate burndown logic across analysis scripts.
    """

    def __init__(self, config_manager):
        """Initialize burndown calculator with configuration.

        Args:
            config_manager: ConfigManager instance for accessing target dates and thresholds
        """
        self.esol_config = config_manager.get_esol_criteria()
        self.win11_config = config_manager.get_win11_criteria()
        self.current_date = datetime.now()

    def calculate_esol_burndown(self, esol_2024_count: int, esol_2025_count: int,
                                esol_2026_count: int) -> List[Dict[str, Union[str, int, float]]]:
        """Calculate burndown metrics for all ESOL categories.

        Args:
            esol_2024_count: Number of devices in ESOL 2024 category
            esol_2025_count: Number of devices in ESOL 2025 category
            esol_2026_count: Number of devices in ESOL 2026 category

        Returns:
            List of burndown data dictionaries, one per ESOL category with fields:
            - category: ESOL category name
            - target_date: Target date string (YYYY-MM-DD)
            - days_remaining: Days until target date
            - remaining_devices: Number of devices still needing replacement
            - daily_burn_rate_needed: Devices per day needed to meet target
            - status: Risk status ('AT RISK' or 'ON TRACK')
        """
        esol_categories = self.esol_config['esol_categories']

        # Parse target dates
        esol_2024_date = datetime.strptime(esol_categories['esol_2024']['target_date'], '%Y-%m-%d')
        esol_2025_date = datetime.strptime(esol_categories['esol_2025']['target_date'], '%Y-%m-%d')
        esol_2026_date = datetime.strptime(esol_categories['esol_2026']['target_date'], '%Y-%m-%d')

        burndown_data = []

        # ESOL 2024 Burndown
        days_remaining_2024 = (esol_2024_date - self.current_date).days
        daily_burn_rate_2024 = esol_2024_count / days_remaining_2024 if days_remaining_2024 > 0 else 0
        burndown_data.append({
            'category': 'ESOL 2024',
            'target_date': esol_categories['esol_2024']['target_date'],
            'days_remaining': int(days_remaining_2024),
            'remaining_devices': int(esol_2024_count),
            'daily_burn_rate_needed': round(daily_burn_rate_2024, 2),
            'status': 'AT RISK' if days_remaining_2024 <= 30 else 'ON TRACK'
        })

        # ESOL 2025 Burndown
        days_remaining_2025 = (esol_2025_date - self.current_date).days
        daily_burn_rate_2025 = esol_2025_count / days_remaining_2025 if days_remaining_2025 > 0 else 0
        burndown_data.append({
            'category': 'ESOL 2025',
            'target_date': esol_categories['esol_2025']['target_date'],
            'days_remaining': int(days_remaining_2025),
            'remaining_devices': int(esol_2025_count),
            'daily_burn_rate_needed': round(daily_burn_rate_2025, 2),
            'status': 'AT RISK' if days_remaining_2025 <= 60 else 'ON TRACK'
        })

        # ESOL 2026 Burndown
        days_remaining_2026 = (esol_2026_date - self.current_date).days
        daily_burn_rate_2026 = esol_2026_count / days_remaining_2026 if days_remaining_2026 > 0 else 0
        burndown_data.append({
            'category': 'ESOL 2026',
            'target_date': esol_categories['esol_2026']['target_date'],
            'days_remaining': int(days_remaining_2026),
            'remaining_devices': int(esol_2026_count),
            'daily_burn_rate_needed': round(daily_burn_rate_2026, 2),
            'status': 'ON TRACK'  # 2026 is far enough out
        })

        return burndown_data

    def calculate_win11_burndown(self, total_eligible: int, completed_count: int) -> Dict[str, Union[str, int, float]]:
        """Calculate burndown metrics for Windows 11 upgrade project.

        Args:
            total_eligible: Total number of devices eligible for Windows 11 upgrade
            completed_count: Number of devices already upgraded to Windows 11

        Returns:
            Dictionary with burndown data:
            - analysis_date: Date of analysis (YYYY-MM-DD)
            - target_date: Target completion date (YYYY-MM-DD)
            - days_remaining: Days until target date
            - total_eligible_devices: Total eligible for upgrade
            - completed_devices: Already upgraded count
            - remaining_devices: Still need upgrade
            - completion_percentage: Percent complete
            - daily_burn_rate_needed: Devices per day to meet target
            - kpi_status: 'ON TRACK' or 'AT RISK'
        """
        # Get KPI target date from config
        target_date_str = self.win11_config.get('kpi_target_date', '2025-10-31')
        target_date = datetime.strptime(target_date_str, '%Y-%m-%d')
        days_remaining = (target_date - self.current_date).days

        # Calculate metrics
        remaining_count = total_eligible - completed_count
        completion_percentage = round((completed_count / total_eligible) * 100, 1) if total_eligible > 0 else 0
        daily_burn_rate_needed = remaining_count / days_remaining if days_remaining > 0 else 0

        return {
            'analysis_date': self.current_date.strftime('%Y-%m-%d'),
            'target_date': target_date_str,
            'days_remaining': days_remaining,
            'total_eligible_devices': total_eligible,
            'completed_devices': completed_count,
            'remaining_devices': remaining_count,
            'completion_percentage': completion_percentage,
            'daily_burn_rate_needed': round(daily_burn_rate_needed, 2),
            'kpi_status': 'ON TRACK' if completion_percentage >= 100 else 'AT RISK'
        }

    def export_burndown_data(self, burndown_data: Union[List[Dict], Dict],
                            data_type: str = 'esol') -> tuple:
        """Export burndown data to JSON and CSV files.

        Args:
            burndown_data: Burndown data (list for ESOL, dict for Win11)
            data_type: Type of burndown data ('esol' or 'win11')

        Returns:
            Tuple of (json_path, csv_path) for exported files
        """
        from pathlib import Path
        import json

        timestamp = self.current_date.strftime('%Y%m%d_%H%M%S')
        processed_dir = Path('data/processed')
        processed_dir.mkdir(parents=True, exist_ok=True)

        # Export as JSON
        json_file = processed_dir / f'{data_type}_burndown_{timestamp}.json'
        with open(json_file, 'w') as f:
            json.dump(burndown_data, f, indent=2)

        # Export as CSV
        csv_file = processed_dir / f'{data_type}_burndown_{timestamp}.csv'
        if isinstance(burndown_data, list):
            # ESOL data is a list of dicts
            df = pd.DataFrame(burndown_data)
        else:
            # Win11 data is a single dict
            df = pd.DataFrame([burndown_data])
        df.to_csv(csv_file, index=False)

        return (json_file, csv_file)
