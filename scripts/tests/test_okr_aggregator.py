"""Unit tests for OKRAggregator."""
import unittest
from unittest.mock import Mock, MagicMock
import sys
from pathlib import Path
import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from etl.analysis.okr_aggregator import OKRAggregator


class TestOKRAggregator(unittest.TestCase):
    """Test cases for OKRAggregator class."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock ConfigManager
        self.mock_config = Mock()
        self.mock_config.get_okr_criteria.return_value = {
            'okr_weights': {
                'kr1_esol_2024': 25,
                'kr2_esol_2025': 25,
                'kr3_win11_compatibility': 40,
                'kr4_kiosk_reprovisioning': 10
            },
            'targets': {
                'kr1_target_percentage': 0,
                'kr2_target_percentage': 0,
                'kr3_target_percentage': 90,
                'kr4_target_count': 0
            },
            'status_thresholds': {
                'caution_min_progress': 60,
                'on_track_min_progress': 80
            }
        }
        self.mock_config.get_esol_criteria.return_value = {
            'esol_categories': {
                'esol_2024': {'action_value': 'Urgent Replacement'},
                'esol_2025': {'action_value': 'Replace by 2025'}
            }
        }

        self.aggregator = OKRAggregator(self.mock_config)

    def test_calculate_okr_scores_perfect_score(self):
        """Test OKR calculation with perfect scores (all targets met)."""
        esol_counts = {
            'esol_2024': 0,
            'esol_2025': 0,
            'esol_2024_pct': 0.0,
            'esol_2025_pct': 0.0,
            'total_devices': 1000
        }
        win11_counts = {
            'win11_adoption_pct': 95.0,
            'total_enterprise': 1000
        }
        kiosk_counts = {
            'enterprise_kiosk_count': 0
        }

        scores = self.aggregator.calculate_okr_scores(
            esol_counts, win11_counts, kiosk_counts
        )

        # All KRs should have perfect scores
        self.assertEqual(scores['kr1_score'], 100.0)
        self.assertEqual(scores['kr2_score'], 100.0)
        self.assertGreaterEqual(scores['kr3_score'], 100.0)
        self.assertEqual(scores['kr4_score'], 100.0)

        # Overall score should be near 100 (weighted)
        self.assertGreater(scores['okr_score'], 95.0)

        # Status should be ON TRACK
        self.assertEqual(scores['status'], 'ON TRACK')
        self.assertEqual(scores['status_icon'], '🟢')

    def test_calculate_okr_scores_at_risk(self):
        """Test OKR calculation with poor scores (at risk)."""
        esol_counts = {
            'esol_2024': 100,
            'esol_2025': 500,
            'esol_2024_pct': 10.0,
            'esol_2025_pct': 50.0,
            'total_devices': 1000
        }
        win11_counts = {
            'win11_adoption_pct': 30.0,
            'total_enterprise': 1000
        }
        kiosk_counts = {
            'enterprise_kiosk_count': 100
        }

        scores = self.aggregator.calculate_okr_scores(
            esol_counts, win11_counts, kiosk_counts
        )

        # All KRs should have low scores
        self.assertLess(scores['kr1_score'], 50.0)
        self.assertLess(scores['kr2_score'], 50.0)
        self.assertLess(scores['kr3_score'], 50.0)

        # Overall score should be low
        self.assertLess(scores['okr_score'], 60.0)

        # Status should be AT RISK
        self.assertEqual(scores['status'], 'AT RISK')
        self.assertEqual(scores['status_icon'], '🔴')

    def test_calculate_okr_scores_caution(self):
        """Test OKR calculation with moderate scores (caution)."""
        # Adjusted values to produce CAUTION status (60-79% score)
        # KR1: 0.3% ESOL 2024 → score = max(0, 100 - (0.3/1)*100) = 70% (25% weight) = 17.5
        # KR2: 1% ESOL 2025 → score = max(0, 100 - (1/5)*100) = 80% (25% weight) = 20
        # KR3: 70% Win11 → score = (70/90)*100 = 77.78% (40% weight) = 31.11
        # KR4: 0 kiosks → score = 100% (10% weight) = 10
        # Total ≈ 78.6% (CAUTION range)
        esol_counts = {
            'esol_2024': 3,
            'esol_2025': 10,
            'esol_2024_pct': 0.3,
            'esol_2025_pct': 1.0,
            'total_devices': 1000
        }
        win11_counts = {
            'win11_adoption_pct': 70.0,
            'total_enterprise': 1000
        }
        kiosk_counts = {
            'enterprise_kiosk_count': 0
        }

        scores = self.aggregator.calculate_okr_scores(
            esol_counts, win11_counts, kiosk_counts
        )

        # Overall score should be in caution range (60-79)
        self.assertGreaterEqual(scores['okr_score'], 60.0)
        self.assertLess(scores['okr_score'], 80.0)

        # Status should be CAUTION
        self.assertEqual(scores['status'], 'CAUTION')
        self.assertEqual(scores['status_icon'], '🟡')

    def test_calculate_okr_scores_weighted_properly(self):
        """Test that OKR scores are weighted correctly."""
        esol_counts = {
            'esol_2024': 0,
            'esol_2025': 0,
            'esol_2024_pct': 0.0,
            'esol_2025_pct': 0.0,
            'total_devices': 1000
        }
        win11_counts = {
            'win11_adoption_pct': 0.0,  # KR3 fails (40% weight)
            'total_enterprise': 1000
        }
        kiosk_counts = {
            'enterprise_kiosk_count': 0
        }

        scores = self.aggregator.calculate_okr_scores(
            esol_counts, win11_counts, kiosk_counts
        )

        # KR1, KR2, KR4 perfect = 25 + 25 + 10 = 60%
        # KR3 zero = 0%
        # Total should be around 60%
        self.assertAlmostEqual(scores['okr_score'], 60.0, delta=5.0)

    def test_aggregate_by_dimension_basic(self):
        """Test basic aggregation by dimension."""
        # Create test DataFrame
        df = pd.DataFrame({
            'Country': ['UK', 'UK', 'France', 'France'],
            'Action': ['ESOL 2024', 'OK', 'ESOL 2025', 'OK'],
            'OS': ['Win10', 'Win11', 'Win10', 'Win11'],
            'Edition': ['Enterprise', 'Enterprise', 'Enterprise', 'Enterprise'],
            'Current User': ['user1', 'user2', 'user3', 'user4'],
            'Last User': ['user1', 'user2', 'user3', 'user4']
        })

        # Mock analyzers with required attributes
        esol_analyzer = Mock()
        esol_analyzer.edition_col = 'Edition'  # Required attribute
        esol_analyzer.calculate_esol_counts.return_value = {
            'esol_2024': 0,
            'esol_2025': 0,
            'esol_2024_pct': 0.0,
            'esol_2025_pct': 0.0,
            'total_devices': 2
        }

        win11_analyzer = Mock()
        win11_analyzer.calculate_win11_counts.return_value = {
            'win11_adoption_pct': 50.0,
            'total_enterprise': 2
        }

        kiosk_analyzer = Mock()
        kiosk_analyzer._filter_kiosk_devices.return_value = pd.DataFrame()  # Empty for no kiosks
        kiosk_analyzer.calculate_kiosk_counts.return_value = {
            'enterprise_kiosk_count': 0
        }

        result = self.aggregator.aggregate_by_dimension(
            df, 'Country', esol_analyzer, win11_analyzer, kiosk_analyzer
        )

        # Should have 2 countries
        self.assertEqual(len(result), 2)

        # Should have required columns
        self.assertIn('Country', result.columns)
        self.assertIn('okr_score', result.columns)
        self.assertIn('status', result.columns)
        self.assertIn('total_devices', result.columns)

    def test_aggregate_by_country(self):
        """Test aggregation by country."""
        df = pd.DataFrame({
            'Country': ['UK'] * 10 + ['France'] * 10,
            'Action': ['OK'] * 20,
            'OS': ['Win11'] * 20,
            'Edition': ['Enterprise'] * 20,
            'Current User': [f'user{i}' for i in range(20)],
            'Last User': [f'user{i}' for i in range(20)]
        })

        # Mock analyzers with perfect scores
        esol_analyzer = Mock()
        esol_analyzer.edition_col = 'Edition'
        esol_analyzer.calculate_esol_counts.return_value = {
            'esol_2024': 0,
            'esol_2025': 0,
            'esol_2024_pct': 0.0,
            'esol_2025_pct': 0.0,
            'total_devices': 10
        }

        win11_analyzer = Mock()
        win11_analyzer.calculate_win11_counts.return_value = {
            'win11_adoption_pct': 100.0,
            'total_enterprise': 10
        }

        kiosk_analyzer = Mock()
        kiosk_analyzer._filter_kiosk_devices.return_value = pd.DataFrame()
        kiosk_analyzer.calculate_kiosk_counts.return_value = {
            'enterprise_kiosk_count': 0
        }

        result = self.aggregator.aggregate_by_country(
            df, esol_analyzer, win11_analyzer, kiosk_analyzer
        )

        # Should have 2 countries
        self.assertEqual(len(result), 2)

        # All should have perfect scores
        for _, row in result.iterrows():
            self.assertGreater(row['okr_score'], 95.0)
            self.assertEqual(row['status'], 'ON TRACK')

    def test_aggregate_by_sdm(self):
        """Test aggregation by SDM."""
        df = pd.DataFrame({
            'SDM': ['Manager1', 'Manager1', 'Manager2', 'Manager2'],
            'Action': ['OK', 'OK', 'ESOL 2024', 'ESOL 2025'],
            'OS': ['Win11', 'Win11', 'Win10', 'Win10'],
            'Edition': ['Enterprise', 'Enterprise', 'Enterprise', 'Enterprise'],
            'Current User': ['user1', 'user2', 'user3', 'user4'],
            'Last User': ['user1', 'user2', 'user3', 'user4']
        })

        # Mock analyzers
        esol_analyzer = Mock()
        esol_analyzer.edition_col = 'Edition'  # Required attribute
        win11_analyzer = Mock()
        kiosk_analyzer = Mock()

        def esol_side_effect(df_slice):
            esol_count = (df_slice['Action'].str.contains('ESOL', na=False)).sum()
            return {
                'esol_2024': esol_count,
                'esol_2025': 0,
                'esol_2024_pct': (esol_count / len(df_slice)) * 100,
                'esol_2025_pct': 0.0,
                'total_devices': len(df_slice)
            }

        esol_analyzer.calculate_esol_counts.side_effect = esol_side_effect

        win11_analyzer.calculate_win11_counts.return_value = {
            'win11_adoption_pct': 50.0,
            'total_enterprise': 2
        }

        kiosk_analyzer._filter_kiosk_devices.return_value = pd.DataFrame()  # Empty for no kiosks
        kiosk_analyzer.calculate_kiosk_counts.return_value = {
            'enterprise_kiosk_count': 0
        }

        # Need to add SDM column for aggregation
        df['SDM'] = ['Manager1', 'Manager1', 'Manager2', 'Manager2']
        
        result = self.aggregator.aggregate_by_sdm(
            df, esol_analyzer, win11_analyzer, kiosk_analyzer
        )

        # Should have 2 SDMs
        self.assertEqual(len(result), 2)

        # Should be sorted by OKR score (descending)
        scores = result['okr_score'].tolist()
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_aggregate_by_site(self):
        """Test aggregation by site with priority sorting."""
        df = pd.DataFrame({
            'Site Location': ['Site1', 'Site1', 'Site2', 'Site2'],
            'Action': ['ESOL 2024', 'ESOL 2024', 'OK', 'OK'],
            'OS': ['Win10', 'Win10', 'Win11', 'Win11'],
            'Edition': ['Enterprise', 'Enterprise', 'Enterprise', 'Enterprise'],
            'Current User': ['user1', 'user2', 'user3', 'user4'],
            'Last User': ['user1', 'user2', 'user3', 'user4']
        })

        # Mock analyzers
        esol_analyzer = Mock()
        esol_analyzer.edition_col = 'Edition'  # Required attribute
        win11_analyzer = Mock()
        kiosk_analyzer = Mock()

        def esol_side_effect(df_slice):
            esol_2024 = (df_slice['Action'] == 'ESOL 2024').sum()
            return {
                'esol_2024': esol_2024,
                'esol_2025': 0,
                'esol_2024_pct': (esol_2024 / len(df_slice)) * 100,
                'esol_2025_pct': 0.0,
                'total_devices': len(df_slice)
            }

        esol_analyzer.calculate_esol_counts.side_effect = esol_side_effect

        win11_analyzer.calculate_win11_counts.return_value = {
            'win11_adoption_pct': 50.0,
            'total_enterprise': 2
        }

        kiosk_analyzer._filter_kiosk_devices.return_value = pd.DataFrame()  # Empty for no kiosks
        kiosk_analyzer.calculate_kiosk_counts.return_value = {
            'enterprise_kiosk_count': 0
        }

        result = self.aggregator.aggregate_by_site(
            df, 'Site Location', esol_analyzer, win11_analyzer, kiosk_analyzer
        )

        # Should have 2 sites
        self.assertEqual(len(result), 2)

        # Sites are sorted by OKR score (descending)
        # Site2 should be first (all OK devices, Win11 = higher OKR score)
        # Site1 has ESOL 2024 devices = lower OKR score
        first_site = result.iloc[0]
        self.assertEqual(first_site['Site Location'], 'Site2')
        
        # Verify sorting: Site2 (higher score) should come before Site1 (lower score)
        scores = result['okr_score'].tolist()
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_zero_devices(self):
        """Test handling of zero devices."""
        esol_counts = {
            'esol_2024': 0,
            'esol_2025': 0,
            'esol_2024_pct': 0.0,
            'esol_2025_pct': 0.0,
            'total_devices': 0
        }
        win11_counts = {
            'win11_adoption_pct': 0.0,
            'total_enterprise': 0
        }
        kiosk_counts = {
            'enterprise_kiosk_count': 0
        }

        scores = self.aggregator.calculate_okr_scores(
            esol_counts, win11_counts, kiosk_counts
        )

        # Should handle gracefully
        self.assertEqual(scores['total_devices'], 0)
        self.assertIsInstance(scores['okr_score'], float)


if __name__ == '__main__':
    unittest.main()
