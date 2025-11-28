"""OKR aggregation module for multi-level analysis.

This module provides the OKRAggregator class which calculates OKR scores
across organizational dimensions (overall, country, SDM, site).

Leverages existing analyzers (ESOL, Win11, Kiosk) and adds aggregation logic.
"""
import pandas as pd
from typing import Dict, List
from datetime import datetime


class OKRAggregator:
    """Aggregate OKR scores across organizational dimensions.

    Calculates OKR scores at multiple levels:
    - Overall (organization-wide)
    - By Country
    - By SDM (Service Delivery Manager)
    - By Site

    Uses existing analyzers for business logic and adds aggregation capabilities.
    """

    def __init__(self, config_manager):
        """Initialize OKR aggregator with configuration.

        Args:
            config_manager: ConfigManager instance for accessing OKR criteria
        """
        self.okr_config = config_manager.get_okr_criteria()
        self.esol_config = config_manager.get_esol_criteria()

        # Cache OKR weights and targets
        self.weights = self.okr_config['okr_weights']
        self.targets = self.okr_config['targets']
        self.thresholds = self.okr_config['status_thresholds']

        # Cache ESOL categories for KR calculations
        self.esol_categories = self.esol_config['esol_categories']

    def calculate_okr_scores(self, esol_counts: Dict, win11_counts: Dict,
                           kiosk_counts: Dict) -> Dict:
        """Calculate overall OKR scores from analyzer results.

        Args:
            esol_counts: Results from ESOLAnalyzer.calculate_esol_counts()
            win11_counts: Results from Win11Analyzer.calculate_win11_counts()
            kiosk_counts: Results from KioskAnalyzer.calculate_kiosk_counts()

        Returns:
            Dict with OKR scores:
            {
                'total_devices': int,
                'kr1_score': float (0-100),
                'kr2_score': float (0-100),
                'kr3_score': float (0-100),
                'kr4_score': float (0-100),
                'okr_score': float (0-100, weighted),
                'status': str ('ON TRACK', 'CAUTION', 'AT RISK'),
                'status_icon': str
            }
        """
        total_devices = esol_counts['total_devices']

        # KR1: ESOL 2024 remediation (target: 0%)
        kr1_current = esol_counts.get('esol_2024', 0)
        kr1_pct = (kr1_current / total_devices) * 100 if total_devices > 0 else 0
        kr1_target = self.targets['kr1_target_percentage']
        # Inverse score: 0 devices = 100%, more devices = lower score
        kr1_score = max(0, 100 - (kr1_pct / 1.0) * 100) if kr1_pct > 0 else 100

        # KR2: ESOL 2025 remediation (target: 0%)
        kr2_current = esol_counts.get('esol_2025', 0)
        kr2_pct = (kr2_current / total_devices) * 100 if total_devices > 0 else 0
        kr2_target = self.targets['kr2_target_percentage']
        # Inverse score: 0 devices = 100%, more devices = lower score
        kr2_score = max(0, 100 - (kr2_pct / 5.0) * 100) if kr2_pct > 0 else 100

        # KR3: Windows 11 compatibility (target: 90%)
        kr3_current = win11_counts.get('win11_adoption_pct', 0)
        kr3_target = self.targets['kr3_target_percentage']
        kr3_score = min(100, (kr3_current / kr3_target) * 100) if kr3_target > 0 else 100

        # KR4: Kiosk re-provisioning (target: 0 devices)
        kr4_current = kiosk_counts.get('enterprise_count', 0)
        kr4_target = self.targets['kr4_target_count']
        kr4_score = 100.0 if kr4_current <= kr4_target else 0.0

        # Calculate weighted OKR score
        okr_score = (
            kr1_score * (self.weights['kr1_esol_2024'] / 100) +
            kr2_score * (self.weights['kr2_esol_2025'] / 100) +
            kr3_score * (self.weights['kr3_win11_compatibility'] / 100) +
            kr4_score * (self.weights['kr4_kiosk_reprovisioning'] / 100)
        )

        # Determine status
        if okr_score >= self.thresholds['on_track_min_progress']:
            status = 'ON TRACK'
            status_icon = '🟢'
        elif okr_score >= self.thresholds['caution_min_progress']:
            status = 'CAUTION'
            status_icon = '🟡'
        else:
            status = 'AT RISK'
            status_icon = '🔴'

        return {
            'total_devices': total_devices,
            'kr1_score': round(kr1_score, 1),
            'kr1_value': kr1_current,
            'kr1_pct': round(kr1_pct, 2),
            'kr2_score': round(kr2_score, 1),
            'kr2_value': kr2_current,
            'kr2_pct': round(kr2_pct, 2),
            'kr3_score': round(kr3_score, 1),
            'kr3_value': round(kr3_current, 2),
            'kr4_score': round(kr4_score, 1),
            'kr4_value': kr4_current,
            'okr_score': round(okr_score, 1),
            'status': status,
            'status_icon': status_icon
        }

    def aggregate_by_dimension(self, df_enriched: pd.DataFrame,
                              dimension: str,
                              esol_analyzer, win11_analyzer, kiosk_analyzer,
                              edition_col: str = None, data_loader=None) -> pd.DataFrame:
        """Calculate OKR scores aggregated by organizational dimension.

        Args:
            df_enriched: DataFrame with Country and SDM columns (from DataLoader.enrich)
            dimension: Dimension to aggregate by ('Country', 'SDM', 'Site Location')
            esol_analyzer: ESOLAnalyzer instance
            win11_analyzer: Win11Analyzer instance
            kiosk_analyzer: KioskAnalyzer instance

        Returns:
            pd.DataFrame with one row per dimension value, sorted by OKR score descending:
            Columns: dimension, total_devices, kr1-4 scores, okr_score, status
        """
        if dimension not in df_enriched.columns:
            raise ValueError(f"Dimension '{dimension}' not found in DataFrame. Available: {df_enriched.columns.tolist()}")

        results = []
        unique_values = df_enriched[dimension].unique()

        for value in unique_values:
            if pd.isna(value) or value == 'Unknown':
                continue

            # Filter data for this dimension value
            dim_df = df_enriched[df_enriched[dimension] == value]

            # Calculate counts using analyzers
            esol_counts = esol_analyzer.calculate_esol_counts(dim_df)

            # For Win11, need Enterprise devices
            # Get edition column from esol_analyzer if available, otherwise use provided edition_col
            edition_column = getattr(esol_analyzer, 'edition_col', edition_col) or 'LTSC or Enterprise'
            enterprise_df = dim_df[dim_df[edition_column] == 'Enterprise']
            if len(enterprise_df) > 0:
                win11_counts = win11_analyzer.calculate_win11_counts(enterprise_df)
            else:
                # No Enterprise devices in this dimension
                win11_counts = {
                    'total_enterprise': 0,
                    'enterprise_win11_count': 0,
                    'enterprise_esol_count': 0,
                    'total_enterprise_win11_path': 0,
                    'current_win11_pct': 0,
                    'win11_adoption_pct': 0
                }

            # For Kiosk - use data_loader if provided, otherwise try kiosk_analyzer method
            if data_loader:
                kiosk_df = data_loader.filter_kiosk_devices(dim_df)
            elif hasattr(kiosk_analyzer, '_filter_kiosk_devices'):
                kiosk_df = kiosk_analyzer._filter_kiosk_devices(dim_df)
            else:
                # Fallback: create empty DataFrame
                kiosk_df = pd.DataFrame()
            
            if len(kiosk_df) > 0:
                kiosk_counts = kiosk_analyzer.calculate_kiosk_counts(kiosk_df, len(dim_df))
            else:
                kiosk_counts = {
                    'total_devices': len(dim_df),
                    'total_kiosk': 0,
                    'enterprise_count': 0,
                    'enterprise_pct': 0,
                    'ltsc_count': 0,
                    'ltsc_pct': 0
                }

            # Calculate OKR scores for this dimension
            scores = self.calculate_okr_scores(esol_counts, win11_counts, kiosk_counts)

            # Add dimension info
            scores[dimension] = value

            results.append(scores)

        # Convert to DataFrame and sort by OKR score
        df_results = pd.DataFrame(results)
        if len(df_results) > 0:
            df_results = df_results.sort_values('okr_score', ascending=False)

        return df_results

    def aggregate_by_country(self, df_enriched: pd.DataFrame,
                            esol_analyzer, win11_analyzer, kiosk_analyzer,
                            edition_col: str = None, data_loader=None) -> pd.DataFrame:
        """Calculate OKR scores by country.

        Args:
            df_enriched: DataFrame with Country column
            esol_analyzer, win11_analyzer, kiosk_analyzer: Analyzer instances
            edition_col: Name of edition column (optional, will try to get from analyzer)
            data_loader: DataLoader instance for filtering (optional)

        Returns:
            pd.DataFrame with country-level OKR scores
        """
        return self.aggregate_by_dimension(
            df_enriched, 'Country', esol_analyzer, win11_analyzer, kiosk_analyzer, edition_col, data_loader
        )

    def aggregate_by_sdm(self, df_enriched: pd.DataFrame,
                        esol_analyzer, win11_analyzer, kiosk_analyzer,
                        edition_col: str = None, data_loader=None) -> pd.DataFrame:
        """Calculate OKR scores by SDM.

        Args:
            df_enriched: DataFrame with SDM column
            esol_analyzer, win11_analyzer, kiosk_analyzer: Analyzer instances
            edition_col: Name of edition column (optional, will try to get from analyzer)
            data_loader: DataLoader instance for filtering (optional)

        Returns:
            pd.DataFrame with SDM-level OKR scores
        """
        return self.aggregate_by_dimension(
            df_enriched, 'SDM', esol_analyzer, win11_analyzer, kiosk_analyzer, edition_col, data_loader
        )

    def aggregate_by_site(self, df_enriched: pd.DataFrame, site_col: str,
                         esol_analyzer, win11_analyzer, kiosk_analyzer,
                         edition_col: str = None, data_loader=None) -> pd.DataFrame:
        """Calculate OKR scores by site.

        Args:
            df_enriched: DataFrame with site column
            site_col: Name of site column (e.g., 'Site Location')
            esol_analyzer, win11_analyzer, kiosk_analyzer: Analyzer instances
            edition_col: Name of edition column (optional, will try to get from analyzer)
            data_loader: DataLoader instance for filtering (optional)

        Returns:
            pd.DataFrame with site-level OKR scores
        """
        return self.aggregate_by_dimension(
            df_enriched, site_col, esol_analyzer, win11_analyzer, kiosk_analyzer, edition_col, data_loader
        )

    def _filter_kiosk_devices_local(self, df: pd.DataFrame, kiosk_analyzer) -> pd.DataFrame:
        """Helper to filter kiosk devices using analyzer's method.

        Args:
            df: DataFrame to filter
            kiosk_analyzer: KioskAnalyzer instance

        Returns:
            pd.DataFrame with kiosk devices
        """
        # Use kiosk analyzer's filter method if available
        # This is a workaround since filter_kiosk_devices is in DataLoader
        kiosk_config = kiosk_analyzer.esol_config['kiosk_detection']
        device_patterns = kiosk_config['device_name_patterns']
        user_patterns = kiosk_config['user_loggedon_patterns']

        device_col = kiosk_analyzer.device_name_col
        user_col = kiosk_analyzer.data_mapping['user_columns']['last']

        device_pattern = '|'.join(device_patterns)
        user_pattern = '|'.join(user_patterns)

        device_mask = df[device_col].str.contains(device_pattern, na=False)
        user_mask = df[user_col].str.contains(user_pattern, case=False, na=False)

        return df[device_mask | user_mask]
