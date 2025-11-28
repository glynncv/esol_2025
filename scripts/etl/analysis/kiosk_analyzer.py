"""Kiosk device analysis module for reprovisioning and migration tracking."""
from typing import Dict
import pandas as pd
from datetime import datetime


class KioskAnalyzer:
    """Analyze kiosk device data for reprovisioning and Windows 11 migration.

    Provides centralized kiosk analysis including edition breakdowns,
    LTSC migration status, and Windows 11 upgrade tracking.
    """

    def __init__(self, config_manager):
        """Initialize kiosk analyzer with configuration.

        Args:
            config_manager: ConfigManager instance for accessing criteria
        """
        self.esol_config = config_manager.get_esol_criteria()
        self.win11_config = config_manager.get_win11_criteria()
        self.data_mapping = self.esol_config['data_mapping']

        # Cache column names for performance
        self.edition_col = self.data_mapping['edition_column']
        self.os_col = self.data_mapping['os_column']

        # Cache Win11 patterns
        self.win11_patterns = self.win11_config['win11_patterns']
        self.win11_pattern = '|'.join(self.win11_patterns)

    def calculate_kiosk_counts(self, kiosk_df: pd.DataFrame,
                               total_devices: int) -> Dict[str, int]:
        """Calculate kiosk device counts and edition breakdown.

        Args:
            kiosk_df: DataFrame containing only kiosk devices (pre-filtered)
            total_devices: Total device count for context

        Returns:
            Dictionary with kiosk counts:
            - total_devices: Total device count (for context)
            - total_kiosk: Total kiosk device count
            - enterprise_count: Enterprise kiosk count
            - ltsc_count: LTSC kiosk count
            - enterprise_pct: Enterprise percentage of kiosks
            - ltsc_pct: LTSC percentage of kiosks
        """
        total_kiosk = len(kiosk_df)

        # Calculate Enterprise and LTSC counts
        enterprise_count = (kiosk_df[self.edition_col] == 'Enterprise').sum()
        ltsc_count = (kiosk_df[self.edition_col] == 'LTSC').sum()

        # Calculate percentages
        enterprise_pct = (
            round((enterprise_count / total_kiosk) * 100, 2)
            if total_kiosk > 0 else 0
        )
        ltsc_pct = (
            round((ltsc_count / total_kiosk) * 100, 2)
            if total_kiosk > 0 else 0
        )

        return {
            'total_devices': total_devices,
            'total_kiosk': int(total_kiosk),
            'enterprise_count': int(enterprise_count),
            'ltsc_count': int(ltsc_count),
            'enterprise_pct': enterprise_pct,
            'ltsc_pct': ltsc_pct
        }

    def calculate_ltsc_win11_migration(self, kiosk_df: pd.DataFrame) -> Dict[str, int]:
        """Calculate LTSC kiosk Windows 11 migration status.

        Args:
            kiosk_df: DataFrame containing only kiosk devices (pre-filtered)

        Returns:
            Dictionary with LTSC migration metrics:
            - ltsc_kiosk_count: Total LTSC kiosk devices
            - ltsc_not_win11_count: LTSC kiosks not yet on Win11
            - ltsc_not_win11_pct: Percentage not yet migrated
        """
        # Filter for LTSC kiosk devices
        ltsc_kiosk_df = kiosk_df[kiosk_df[self.edition_col] == 'LTSC']
        ltsc_kiosk_count = len(ltsc_kiosk_df)

        # Check for Windows 11 patterns
        ltsc_not_win11_count = (
            ~ltsc_kiosk_df[self.os_col].str.contains(
                self.win11_pattern, case=False, na=False
            )
        ).sum()

        # Calculate percentage
        ltsc_not_win11_pct = (
            round((ltsc_not_win11_count / ltsc_kiosk_count) * 100, 2)
            if ltsc_kiosk_count > 0 else 0
        )

        return {
            'ltsc_kiosk_count': int(ltsc_kiosk_count),
            'ltsc_not_win11_count': int(ltsc_not_win11_count),
            'ltsc_not_win11_pct': ltsc_not_win11_pct
        }
