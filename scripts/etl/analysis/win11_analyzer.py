"""Windows 11 analysis module for upgrade tracking and KPI monitoring."""
from typing import Dict, Tuple
import pandas as pd
from datetime import datetime
from pathlib import Path


class Win11Analyzer:
    """Analyze Windows 11 migration progress for Enterprise devices.

    Provides centralized Windows 11 analysis including upgrade counts,
    adoption percentages, and site-level deployment tracking.
    """

    def __init__(self, config_manager):
        """Initialize Windows 11 analyzer with configuration.

        Args:
            config_manager: ConfigManager instance for accessing Win11 criteria
        """
        self.esol_config = config_manager.get_esol_criteria()
        self.win11_config = config_manager.get_win11_criteria()
        self.data_mapping = self.esol_config['data_mapping']

        # Cache column names for performance
        self.action_col = self.data_mapping['action_column']
        self.os_col = self.data_mapping['os_column']
        self.current_os_col = self.data_mapping['current_os_column']
        self.site_col = self.data_mapping['site_column']

        # Cache Win11 patterns
        self.win11_patterns = self.win11_config['win11_patterns']
        self.win11_pattern = '|'.join(self.win11_patterns)

        # Get ESOL migration actions to exclude from Win11 eligible count
        self.migration_categories = self.win11_config['migration_categories']
        self.migration_actions = [
            self.esol_config['esol_categories'][cat]['action_value']
            for cat in self.migration_categories
        ]

    def calculate_win11_counts(self, enterprise_df: pd.DataFrame) -> Dict[str, int]:
        """Calculate Windows 11 device counts for Enterprise devices.

        Args:
            enterprise_df: DataFrame containing Enterprise devices only

        Returns:
            Dictionary with Win11 counts:
            - total_enterprise: Total Enterprise devices
            - enterprise_win11_count: Enterprise devices currently on Win11
            - enterprise_esol_count: Enterprise ESOL devices getting Win11 via replacement
            - total_enterprise_win11_path: Total Enterprise on path to Win11
            - current_win11_pct: Current Win11 adoption percentage
            - win11_adoption_pct: Projected Win11 adoption percentage
        """
        total_enterprise = len(enterprise_df)

        # Count Enterprise devices currently on Windows 11 (excluding ESOL 2024/2025)
        enterprise_win11_mask = (
            enterprise_df[self.os_col].str.contains(self.win11_pattern, case=False, na=False) &
            ~enterprise_df[self.action_col].isin(self.migration_actions)
        )
        enterprise_win11_count = len(enterprise_df[enterprise_win11_mask])

        # Count Enterprise EUCs that will get Windows 11 via ESOL replacement
        enterprise_esol_mask = enterprise_df[self.action_col].isin(self.migration_actions)
        enterprise_esol_count = len(enterprise_df[enterprise_esol_mask])

        # Calculate totals
        total_enterprise_win11_path = enterprise_win11_count + enterprise_esol_count
        win11_adoption_pct = (
            round((total_enterprise_win11_path / total_enterprise) * 100, 2)
            if total_enterprise > 0 else 0
        )
        current_win11_pct = (
            round((enterprise_win11_count / total_enterprise) * 100, 2)
            if total_enterprise > 0 else 0
        )

        return {
            'total_enterprise': total_enterprise,
            'enterprise_win11_count': enterprise_win11_count,
            'enterprise_esol_count': enterprise_esol_count,
            'total_enterprise_win11_path': total_enterprise_win11_path,
            'current_win11_pct': current_win11_pct,
            'win11_adoption_pct': win11_adoption_pct
        }

    def generate_site_summary(self, enterprise_df: pd.DataFrame) -> pd.DataFrame:
        """Generate site-level Windows 11 deployment summary.

        Args:
            enterprise_df: DataFrame containing Enterprise devices only

        Returns:
            DataFrame with site-level summary containing columns:
            - Total_Devices: Total Enterprise devices per site
            - Win11_Eligible_Count: Devices eligible for Win11 upgrade
            - Win11_Eligible_Pct: Percentage of devices eligible
            - Win11_Count: Devices already upgraded to Win11
            - Win11_Pct: Percentage upgraded (of eligible)
            - Pending_Count: Devices pending upgrade
            - Pending_Pct: Percentage pending (of eligible)
            Sorted by Total_Devices descending
        """
        # Generate comprehensive site summary for Windows 11 deployment
        site_data = enterprise_df.groupby(self.site_col).agg({
            'Device Name': 'count'  # Total Enterprise devices per site
        }).rename(columns={'Device Name': 'Total_Devices'})

        # Calculate Windows 11 eligible devices (Enterprise excluding ESOL that support Win11)
        eligible_mask = ~enterprise_df[self.action_col].isin(self.migration_actions)
        eligible_df = enterprise_df[eligible_mask]

        # Filter for devices that support Win11
        win11_supported_mask = eligible_df[self.os_col].str.contains(
            self.win11_pattern, case=False, na=False
        )
        win11_supported_df = eligible_df[win11_supported_mask]

        eligible_counts = win11_supported_df.groupby(self.site_col)['Device Name'].count()
        site_data['Win11_Eligible_Count'] = (
            site_data.index.map(eligible_counts).fillna(0).astype(int)
        )

        # Calculate Windows 11 devices (of eligible, how many have Win11 OS)
        win11_upgraded_mask = win11_supported_df[self.current_os_col].str.contains(
            self.win11_pattern, case=False, na=False
        )
        win11_upgraded_df = win11_supported_df[win11_upgraded_mask]
        win11_counts = win11_upgraded_df.groupby(self.site_col)['Device Name'].count()
        site_data['Win11_Count'] = site_data.index.map(win11_counts).fillna(0).astype(int)

        # Calculate Pending devices (eligible but not yet upgraded)
        site_data['Pending_Count'] = (
            site_data['Win11_Eligible_Count'] - site_data['Win11_Count']
        )

        # Calculate percentages
        site_data['Win11_Eligible_Pct'] = (
            site_data['Win11_Eligible_Count'] / site_data['Total_Devices'] * 100
        ).round(1)

        # Win11 and Pending percentages are relative to eligible devices
        site_data['Win11_Pct'] = (
            site_data['Win11_Count'] / site_data['Win11_Eligible_Count'] * 100
        ).round(1)
        site_data['Pending_Pct'] = (
            site_data['Pending_Count'] / site_data['Win11_Eligible_Count'] * 100
        ).round(1)

        # Handle division by zero for sites with no eligible devices
        site_data['Win11_Pct'] = site_data['Win11_Pct'].fillna(0)
        site_data['Pending_Pct'] = site_data['Pending_Pct'].fillna(0)

        # Ensure all count columns are integers
        site_data['Total_Devices'] = site_data['Total_Devices'].astype(int)
        site_data['Win11_Eligible_Count'] = site_data['Win11_Eligible_Count'].astype(int)
        site_data['Win11_Count'] = site_data['Win11_Count'].astype(int)
        site_data['Pending_Count'] = site_data['Pending_Count'].astype(int)

        # Reorder columns
        site_data = site_data[[
            'Total_Devices', 'Win11_Eligible_Count', 'Win11_Eligible_Pct',
            'Win11_Count', 'Win11_Pct', 'Pending_Count', 'Pending_Pct'
        ]]

        # Filter for sites with devices and sort by total devices
        site_data = site_data[site_data['Total_Devices'] > 0].sort_values(
            'Total_Devices',
            ascending=False
        )

        return site_data

    def export_site_summary(self, site_data: pd.DataFrame) -> Tuple[Path, Path]:
        """Export site summary to CSV and JSON files.

        Args:
            site_data: DataFrame from generate_site_summary()

        Returns:
            Tuple of (csv_path, json_path)
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        processed_dir = Path('data/processed')
        processed_dir.mkdir(parents=True, exist_ok=True)

        # Export as CSV
        csv_file = processed_dir / f'site_win11_summary_{timestamp}.csv'
        site_data.to_csv(csv_file)

        # Export as JSON
        json_file = processed_dir / f'site_win11_summary_{timestamp}.json'
        site_data.to_json(json_file, orient='index', indent=2)

        return (csv_file, json_file)

    def calculate_kpi_metrics(self, counts: Dict[str, int]) -> Dict[str, any]:
        """Calculate Windows 11 upgrade KPI metrics.

        Args:
            counts: Dictionary from calculate_win11_counts()

        Returns:
            Dictionary with KPI metrics:
            - total_eligible: Total eligible devices (excluding ESOL)
            - upgraded_pct: Percentage of eligible devices already upgraded
            - pending_count: Count of devices pending upgrade
        """
        # Total eligible = Total Enterprise - ESOL replacement devices
        total_eligible = counts['total_enterprise'] - counts['enterprise_esol_count']

        # Percentage upgraded
        upgraded_pct = (
            round((counts['enterprise_win11_count'] / total_eligible) * 100, 2)
            if total_eligible > 0 else 0
        )

        # Pending upgrade count
        pending_count = total_eligible - counts['enterprise_win11_count']

        return {
            'total_eligible': total_eligible,
            'upgraded_pct': upgraded_pct,
            'pending_count': pending_count
        }
