"""Unit tests for historical tracking features."""
import unittest
from unittest.mock import Mock, patch
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
import tempfile
import shutil

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from etl.analysis.historical_store import HistoricalDataStore
from etl.analysis.trend_analyzer import TrendAnalyzer


class TestHistoricalDataStore(unittest.TestCase):
    """Test cases for HistoricalDataStore class."""

    def setUp(self):
        """Set up test fixtures with temporary directory."""
        # Create temporary directory for test snapshots
        self.test_dir = tempfile.mkdtemp()
        self.store = HistoricalDataStore(history_dir=self.test_dir)

        # Create sample data
        self.overall_scores = {
            'okr_score': 85.5,
            'kr1_score': 90.0,
            'kr2_score': 80.0,
            'kr3_score': 85.0,
            'kr4_score': 90.0,
            'total_devices': 1000,
            'kr1_value': 10,
            'kr2_value': 50,
            'kr3_value': 85.0,
            'kr4_value': 5
        }

        self.country_scores = pd.DataFrame([
            {'Country': 'USA', 'okr_score': 85.0, 'total_devices': 500},
            {'Country': 'UK', 'okr_score': 80.0, 'total_devices': 300}
        ])

        self.sdm_scores = pd.DataFrame([
            {'SDM': 'John Doe', 'okr_score': 85.0, 'total_devices': 400}
        ])

        self.site_scores = pd.DataFrame([
            {'Site Location': 'New York', 'okr_score': 90.0, 'total_devices': 200}
        ])

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.test_dir)

    def test_save_snapshot(self):
        """Test saving a snapshot."""
        snapshot_path = self.store.save_snapshot(
            self.overall_scores, self.country_scores,
            self.sdm_scores, self.site_scores
        )

        # Verify file was created
        self.assertTrue(snapshot_path.exists())
        self.assertTrue(snapshot_path.name.startswith('okr_snapshot_'))
        self.assertTrue(snapshot_path.name.endswith('.json'))

    def test_get_latest_snapshot(self):
        """Test retrieving the latest snapshot."""
        # Save multiple snapshots
        self.store.save_snapshot(
            self.overall_scores, self.country_scores,
            self.sdm_scores, self.site_scores,
            timestamp=datetime.now() - timedelta(days=2)
        )
        self.store.save_snapshot(
            self.overall_scores, self.country_scores,
            self.sdm_scores, self.site_scores,
            timestamp=datetime.now() - timedelta(days=1)
        )

        # Get latest
        latest = self.store.get_latest_snapshot()

        self.assertIsNotNone(latest)
        self.assertEqual(latest['overall_scores']['okr_score'], 85.5)
        self.assertIsInstance(latest['country_scores_df'], pd.DataFrame)

    def test_get_previous_snapshot(self):
        """Test retrieving a snapshot from N days ago."""
        # Save snapshots at different times
        timestamp_old = datetime.now() - timedelta(days=7)
        timestamp_recent = datetime.now()

        self.store.save_snapshot(
            self.overall_scores, self.country_scores,
            self.sdm_scores, self.site_scores,
            timestamp=timestamp_old
        )
        self.store.save_snapshot(
            self.overall_scores, self.country_scores,
            self.sdm_scores, self.site_scores,
            timestamp=timestamp_recent
        )

        # Get previous snapshot (7 days back)
        previous = self.store.get_previous_snapshot(days_back=7)

        self.assertIsNotNone(previous)
        # Should be close to the old timestamp
        snapshot_time = datetime.fromisoformat(previous['timestamp'])
        diff = abs((snapshot_time - timestamp_old).total_seconds())
        self.assertLess(diff, 60)  # Within 1 minute

    def test_count_snapshots(self):
        """Test counting snapshots."""
        # Initially should be 0
        self.assertEqual(self.store.count_snapshots(), 0)

        # Save 3 snapshots
        for i in range(3):
            self.store.save_snapshot(
                self.overall_scores, self.country_scores,
                self.sdm_scores, self.site_scores,
                timestamp=datetime.now() - timedelta(days=i)
            )

        self.assertEqual(self.store.count_snapshots(), 3)


class TestTrendAnalyzer(unittest.TestCase):
    """Test cases for TrendAnalyzer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.current_scores = {
            'okr_score': 85.0,
            'kr1_score': 90.0,
            'kr2_score': 80.0,
            'kr3_score': 85.0,
            'kr4_score': 90.0,
            'kr1_value': 10,
            'kr2_value': 50,
            'kr3_value': 85.0,
            'kr4_value': 5,
            'timestamp': datetime.now().isoformat()
        }

        self.previous_scores = {
            'okr_score': 80.0,
            'kr1_score': 85.0,
            'kr2_score': 75.0,
            'kr3_score': 80.0,
            'kr4_score': 85.0,
            'kr1_value': 15,
            'kr2_value': 60,
            'kr3_value': 80.0,
            'kr4_value': 10,
            'timestamp': (datetime.now() - timedelta(days=7)).isoformat()
        }

    def test_calculate_overall_trends_with_history(self):
        """Test trend calculation with previous data."""
        trends = TrendAnalyzer.calculate_overall_trends(
            self.current_scores, self.previous_scores
        )

        # Should have history
        self.assertTrue(trends['has_history'])

        # OKR score improved by 5.0
        self.assertEqual(trends['okr_score_delta'], 5.0)
        self.assertEqual(trends['okr_score_trend'], '↑')

        # KR1 improved by 5.0
        self.assertEqual(trends['kr1_delta'], 5.0)
        self.assertEqual(trends['kr1_trend'], '↑')

        # Days since previous should be ~7
        self.assertGreaterEqual(trends['days_since_previous'], 6)
        self.assertLessEqual(trends['days_since_previous'], 8)

    def test_calculate_overall_trends_without_history(self):
        """Test trend calculation without previous data."""
        trends = TrendAnalyzer.calculate_overall_trends(
            self.current_scores, None
        )

        # Should not have history
        self.assertFalse(trends['has_history'])

        # All deltas should be 0
        self.assertEqual(trends['okr_score_delta'], 0.0)
        self.assertEqual(trends['kr1_delta'], 0.0)

        # All trends should be flat
        self.assertEqual(trends['okr_score_trend'], '→')
        self.assertEqual(trends['kr1_trend'], '→')

    def test_calculate_country_trends(self):
        """Test country-level trend calculation."""
        current_df = pd.DataFrame([
            {'Country': 'USA', 'okr_score': 85.0},
            {'Country': 'UK', 'okr_score': 80.0}
        ])

        previous_df = pd.DataFrame([
            {'Country': 'USA', 'okr_score': 80.0},
            {'Country': 'UK', 'okr_score': 82.0}
        ])

        result_df = TrendAnalyzer.calculate_country_trends(current_df, previous_df)

        # Should have trend columns
        self.assertIn('okr_score_delta', result_df.columns)
        self.assertIn('okr_score_trend', result_df.columns)

        # USA improved by 5.0
        usa_row = result_df[result_df['Country'] == 'USA'].iloc[0]
        self.assertEqual(usa_row['okr_score_delta'], 5.0)
        self.assertEqual(usa_row['okr_score_trend'], '↑')

        # UK declined by 2.0
        uk_row = result_df[result_df['Country'] == 'UK'].iloc[0]
        self.assertEqual(uk_row['okr_score_delta'], -2.0)
        self.assertEqual(uk_row['okr_score_trend'], '↓')

    def test_calculate_burndown_trends(self):
        """Test burndown trend calculation."""
        # Create snapshots showing improvement over time
        snapshots = [
            {
                'timestamp': (datetime.now() - timedelta(days=14)).isoformat(),
                'overall_scores': {
                    'kr1_value': 30,
                    'kr2_value': 100,
                    'kr3_value': 70.0,
                    'kr4_value': 20
                }
            },
            {
                'timestamp': (datetime.now() - timedelta(days=7)).isoformat(),
                'overall_scores': {
                    'kr1_value': 20,
                    'kr2_value': 75,
                    'kr3_value': 77.5,
                    'kr4_value': 15
                }
            },
            {
                'timestamp': datetime.now().isoformat(),
                'overall_scores': {
                    'kr1_value': 10,
                    'kr2_value': 50,
                    'kr3_value': 85.0,
                    'kr4_value': 10
                }
            }
        ]

        trends = TrendAnalyzer.calculate_burndown_trends(snapshots)

        # Should have sufficient history
        self.assertTrue(trends['has_sufficient_history'])

        # KR1 velocity should be positive (reducing devices)
        self.assertGreater(trends['kr1_velocity'], 0)

        # KR3 velocity should be positive (increasing percentage)
        self.assertGreater(trends['kr3_velocity'], 0)

        # Overall trend should be improving
        self.assertEqual(trends['trend_direction'], 'improving')

    def test_get_trend_arrow(self):
        """Test trend arrow generation."""
        # Significant increase
        self.assertEqual(TrendAnalyzer._get_trend_arrow(5.0), '↑')

        # Significant decrease
        self.assertEqual(TrendAnalyzer._get_trend_arrow(-5.0), '↓')

        # Small change (flat)
        self.assertEqual(TrendAnalyzer._get_trend_arrow(0.3), '→')
        self.assertEqual(TrendAnalyzer._get_trend_arrow(-0.3), '→')


if __name__ == '__main__':
    unittest.main()
