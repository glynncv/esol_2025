"""Trend analysis for OKR historical data.

This module provides the TrendAnalyzer class which calculates week-over-week
changes and trends from historical OKR snapshots.
"""
from typing import Dict, Optional, List
from datetime import datetime
import pandas as pd


class TrendAnalyzer:
    """Analyze trends and week-over-week changes in OKR data.

    Compares current snapshots with historical data to identify improvements,
    regressions, and trends over time.
    """

    @staticmethod
    def calculate_overall_trends(current: Dict, previous: Optional[Dict]) -> Dict:
        """Calculate week-over-week trends for overall scores.

        Args:
            current: Current overall_scores dict
            previous: Previous overall_scores dict (or None)

        Returns:
            Dict with trend indicators:
            {
                'okr_score_delta': float,
                'okr_score_trend': str ('↑', '↓', '→'),
                'kr1_delta': float,
                'kr1_trend': str,
                'kr2_delta': float,
                'kr2_trend': str,
                'kr3_delta': float,
                'kr3_trend': str,
                'kr4_delta': float,
                'kr4_trend': str,
                'has_history': bool,
                'days_since_previous': int
            }
        """
        if previous is None:
            return {
                'okr_score_delta': 0.0,
                'okr_score_trend': '→',
                'kr1_delta': 0.0,
                'kr1_trend': '→',
                'kr2_delta': 0.0,
                'kr2_trend': '→',
                'kr3_delta': 0.0,
                'kr3_trend': '→',
                'kr4_delta': 0.0,
                'kr4_trend': '→',
                'has_history': False,
                'days_since_previous': 0
            }

        # Calculate deltas
        okr_delta = current['okr_score'] - previous['okr_score']
        kr1_delta = current['kr1_score'] - previous['kr1_score']
        kr2_delta = current['kr2_score'] - previous['kr2_score']
        kr3_delta = current['kr3_score'] - previous['kr3_score']
        kr4_delta = current['kr4_score'] - previous['kr4_score']

        # Calculate days between snapshots
        current_time = datetime.fromisoformat(current.get('timestamp', datetime.now().isoformat()))
        previous_time = datetime.fromisoformat(previous.get('timestamp', datetime.now().isoformat()))
        days_diff = (current_time - previous_time).days

        return {
            'okr_score_delta': okr_delta,
            'okr_score_trend': TrendAnalyzer._get_trend_arrow(okr_delta),
            'kr1_delta': kr1_delta,
            'kr1_trend': TrendAnalyzer._get_trend_arrow(kr1_delta),
            'kr2_delta': kr2_delta,
            'kr2_trend': TrendAnalyzer._get_trend_arrow(kr2_delta),
            'kr3_delta': kr3_delta,
            'kr3_trend': TrendAnalyzer._get_trend_arrow(kr3_delta),
            'kr4_delta': kr4_delta,
            'kr4_trend': TrendAnalyzer._get_trend_arrow(kr4_delta),
            'has_history': True,
            'days_since_previous': days_diff
        }

    @staticmethod
    def calculate_country_trends(current_df: pd.DataFrame,
                                previous_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate week-over-week trends for country scores.

        Args:
            current_df: Current country_scores DataFrame
            previous_df: Previous country_scores DataFrame

        Returns:
            DataFrame with added trend columns
        """
        if len(previous_df) == 0:
            # No history - add empty trend columns
            current_df = current_df.copy()
            current_df['okr_score_delta'] = 0.0
            current_df['okr_score_trend'] = '→'
            return current_df

        # Merge current and previous on Country
        merged = current_df.merge(
            previous_df[['Country', 'okr_score']],
            on='Country',
            how='left',
            suffixes=('', '_prev')
        )

        # Calculate deltas
        merged['okr_score_delta'] = merged.apply(
            lambda row: row['okr_score'] - row['okr_score_prev']
            if pd.notna(row.get('okr_score_prev')) else 0.0,
            axis=1
        )

        # Add trend arrows
        merged['okr_score_trend'] = merged['okr_score_delta'].apply(
            TrendAnalyzer._get_trend_arrow
        )

        # Drop previous score column
        merged = merged.drop(columns=['okr_score_prev'], errors='ignore')

        return merged

    @staticmethod
    def calculate_sdm_trends(current_df: pd.DataFrame,
                            previous_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate week-over-week trends for SDM scores.

        Args:
            current_df: Current sdm_scores DataFrame
            previous_df: Previous sdm_scores DataFrame

        Returns:
            DataFrame with added trend columns
        """
        if len(previous_df) == 0:
            # No history - add empty trend columns
            current_df = current_df.copy()
            current_df['okr_score_delta'] = 0.0
            current_df['okr_score_trend'] = '→'
            return current_df

        # Merge current and previous on SDM
        merged = current_df.merge(
            previous_df[['SDM', 'okr_score']],
            on='SDM',
            how='left',
            suffixes=('', '_prev')
        )

        # Calculate deltas
        merged['okr_score_delta'] = merged.apply(
            lambda row: row['okr_score'] - row['okr_score_prev']
            if pd.notna(row.get('okr_score_prev')) else 0.0,
            axis=1
        )

        # Add trend arrows
        merged['okr_score_trend'] = merged['okr_score_delta'].apply(
            TrendAnalyzer._get_trend_arrow
        )

        # Drop previous score column
        merged = merged.drop(columns=['okr_score_prev'], errors='ignore')

        return merged

    @staticmethod
    def calculate_burndown_trends(current_snapshots: List[Dict]) -> Dict:
        """Calculate burndown velocity trends over time.

        Args:
            current_snapshots: List of historical snapshots (chronologically sorted)

        Returns:
            Dict with burndown trend analysis:
            {
                'kr1_velocity': float (devices per day),
                'kr2_velocity': float (devices per day),
                'kr3_velocity': float (% points per day),
                'kr4_velocity': float (devices per day),
                'trend_direction': str ('improving', 'declining', 'stable'),
                'projection_kr1_days_to_zero': int,
                'projection_kr2_days_to_zero': int
            }
        """
        if len(current_snapshots) < 2:
            return {
                'kr1_velocity': 0.0,
                'kr2_velocity': 0.0,
                'kr3_velocity': 0.0,
                'kr4_velocity': 0.0,
                'trend_direction': 'stable',
                'projection_kr1_days_to_zero': None,
                'projection_kr2_days_to_zero': None,
                'has_sufficient_history': False
            }

        # Get first and last snapshots for velocity calculation
        first = current_snapshots[0]
        last = current_snapshots[-1]

        first_time = datetime.fromisoformat(first['timestamp'])
        last_time = datetime.fromisoformat(last['timestamp'])
        days_elapsed = max(1, (last_time - first_time).days)

        # Calculate velocities (change per day)
        kr1_velocity = (first['overall_scores']['kr1_value'] - last['overall_scores']['kr1_value']) / days_elapsed
        kr2_velocity = (first['overall_scores']['kr2_value'] - last['overall_scores']['kr2_value']) / days_elapsed
        kr3_velocity = (last['overall_scores']['kr3_value'] - first['overall_scores']['kr3_value']) / days_elapsed
        kr4_velocity = (first['overall_scores']['kr4_value'] - last['overall_scores']['kr4_value']) / days_elapsed

        # Determine overall trend direction
        positive_trends = sum([
            kr1_velocity > 0,  # Reducing ESOL 2024 is good
            kr2_velocity > 0,  # Reducing ESOL 2025 is good
            kr3_velocity > 0,  # Increasing Win11 is good
            kr4_velocity > 0   # Reducing kiosks is good
        ])

        if positive_trends >= 3:
            trend_direction = 'improving'
        elif positive_trends <= 1:
            trend_direction = 'declining'
        else:
            trend_direction = 'stable'

        # Project days to zero for KR1 and KR2
        kr1_current = last['overall_scores']['kr1_value']
        kr2_current = last['overall_scores']['kr2_value']

        kr1_days_to_zero = int(kr1_current / kr1_velocity) if kr1_velocity > 0 else None
        kr2_days_to_zero = int(kr2_current / kr2_velocity) if kr2_velocity > 0 else None

        return {
            'kr1_velocity': kr1_velocity,
            'kr2_velocity': kr2_velocity,
            'kr3_velocity': kr3_velocity,
            'kr4_velocity': kr4_velocity,
            'trend_direction': trend_direction,
            'projection_kr1_days_to_zero': kr1_days_to_zero,
            'projection_kr2_days_to_zero': kr2_days_to_zero,
            'has_sufficient_history': True,
            'days_elapsed': days_elapsed,
            'snapshots_analyzed': len(current_snapshots)
        }

    @staticmethod
    def _get_trend_arrow(delta: float, threshold: float = 0.5) -> str:
        """Get trend arrow based on delta value.

        Args:
            delta: Change value
            threshold: Minimum change to show arrow (default: 0.5)

        Returns:
            Trend arrow: '↑' (up), '↓' (down), or '→' (flat)
        """
        if delta > threshold:
            return '↑'
        elif delta < -threshold:
            return '↓'
        else:
            return '→'
