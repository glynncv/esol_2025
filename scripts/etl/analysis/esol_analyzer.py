"""ESOL-specific analysis module for device counts, costs, and site breakdowns."""
from typing import Dict, Tuple
import pandas as pd
from datetime import datetime
from pathlib import Path


class ESOLAnalyzer:
    """Analyze ESOL device data with category breakdowns and site-level summaries.

    Provides centralized ESOL analysis calculations including device counts,
    cost summaries, and site-level breakdowns for replacement planning.
    """

    def __init__(self, config_manager):
        """Initialize ESOL analyzer with configuration.

        Args:
            config_manager: ConfigManager instance for accessing ESOL criteria
        """
        self.esol_config = config_manager.get_esol_criteria()
        self.data_mapping = self.esol_config['data_mapping']
        self.esol_categories = self.esol_config['esol_categories']

        # Cache column names for performance
        self.action_col = self.data_mapping['action_column']
        self.cost_col = self.data_mapping['cost_column']
        self.site_col = self.data_mapping['site_column']

        # Cache ESOL action values
        self.esol_2024_action = self.esol_categories['esol_2024']['action_value']
        self.esol_2025_action = self.esol_categories['esol_2025']['action_value']
        self.esol_2026_action = self.esol_categories['esol_2026']['action_value']

    def calculate_esol_counts(self, df: pd.DataFrame) -> Dict[str, int]:
        """Calculate device counts for each ESOL category.

        Args:
            df: DataFrame containing device data

        Returns:
            Dictionary with ESOL counts:
            - total_devices: Total device count
            - esol_2024: ESOL 2024 device count
            - esol_2025: ESOL 2025 device count
            - esol_2026: ESOL 2026 device count
            - total_esol: Total ESOL devices (all categories)
            - non_esol: Non-ESOL devices
        """
        total = len(df)
        esol_2024 = (df[self.action_col] == self.esol_2024_action).sum()
        esol_2025 = (df[self.action_col] == self.esol_2025_action).sum()
        esol_2026 = (df[self.action_col] == self.esol_2026_action).sum()
        total_esol = esol_2024 + esol_2025 + esol_2026
        non_esol = total - total_esol

        return {
            'total_devices': total,
            'esol_2024': int(esol_2024),
            'esol_2025': int(esol_2025),
            'esol_2026': int(esol_2026),
            'total_esol': int(total_esol),
            'non_esol': int(non_esol)
        }

    def calculate_esol_percentages(self, counts: Dict[str, int]) -> Dict[str, float]:
        """Calculate percentage distributions for ESOL categories.

        Args:
            counts: Dictionary from calculate_esol_counts()

        Returns:
            Dictionary with percentages (rounded to 2 decimal places):
            - esol_2024_pct
            - esol_2025_pct
            - esol_2026_pct
            - total_esol_pct
            - non_esol_pct
        """
        total = counts['total_devices']
        if total == 0:
            return {
                'esol_2024_pct': 0.0,
                'esol_2025_pct': 0.0,
                'esol_2026_pct': 0.0,
                'total_esol_pct': 0.0,
                'non_esol_pct': 0.0
            }

        return {
            'esol_2024_pct': round((counts['esol_2024'] / total) * 100, 2),
            'esol_2025_pct': round((counts['esol_2025'] / total) * 100, 2),
            'esol_2026_pct': round((counts['esol_2026'] / total) * 100, 2),
            'total_esol_pct': round((counts['total_esol'] / total) * 100, 2),
            'non_esol_pct': round((counts['non_esol'] / total) * 100, 2)
        }

    def generate_site_summary(self, esol_df: pd.DataFrame) -> pd.DataFrame:
        """Generate site-level ESOL summary with counts and costs.

        Args:
            esol_df: DataFrame containing only ESOL devices (pre-filtered)

        Returns:
            DataFrame with site-level summary containing columns:
            - ESOL_2024_Count
            - ESOL_2025_Count
            - ESOL_2026_Count
            - Total_ESOL
            - Total_Cost
            Sorted by Total_ESOL descending, filtered to sites with ESOL devices
        """
        # Group by site and calculate counts and costs
        site_data = esol_df.groupby(self.site_col).agg({
            self.action_col: lambda x: (x == self.esol_2024_action).sum(),  # ESOL 2024
            self.cost_col: 'sum'  # Total cost for all ESOL devices
        }).rename(columns={
            self.action_col: 'ESOL_2024_Count',
            self.cost_col: 'Total_Cost'
        })

        # Add counts for other categories
        site_data['ESOL_2025_Count'] = esol_df.groupby(self.site_col)[self.action_col].apply(
            lambda x: (x == self.esol_2025_action).sum()
        )
        site_data['ESOL_2026_Count'] = esol_df.groupby(self.site_col)[self.action_col].apply(
            lambda x: (x == self.esol_2026_action).sum()
        )
        site_data['Total_ESOL'] = (
            site_data['ESOL_2024_Count'] +
            site_data['ESOL_2025_Count'] +
            site_data['ESOL_2026_Count']
        )

        # Reorder columns to match preferred structure
        site_data = site_data[[
            'ESOL_2024_Count',
            'ESOL_2025_Count',
            'ESOL_2026_Count',
            'Total_ESOL',
            'Total_Cost'
        ]]

        # Filter to sites with ESOL devices and sort by total
        site_data = site_data[site_data['Total_ESOL'] > 0].sort_values(
            'Total_ESOL',
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
        csv_file = processed_dir / f'site_esol_summary_{timestamp}.csv'
        site_data.to_csv(csv_file)

        # Export as JSON
        json_file = processed_dir / f'site_esol_summary_{timestamp}.json'
        site_data.to_json(json_file, orient='index', indent=2)

        return (csv_file, json_file)
