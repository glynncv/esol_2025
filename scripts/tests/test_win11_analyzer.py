"""Unit tests for Win11Analyzer."""
import unittest
from unittest.mock import Mock
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from etl.analysis.win11_analyzer import Win11Analyzer


class TestWin11Analyzer(unittest.TestCase):
    """Test cases for Win11Analyzer class."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock ConfigManager
        self.mock_config = Mock()
        self.mock_config.get_esol_criteria.return_value = {
            'data_mapping': {
                'action_column': 'Action',
                'os_column': 'OS',
                'current_os_column': 'Current OS',
                'site_column': 'Site'
            },
            'esol_categories': {
                'esol_2024': {'action_value': 'ESOL 2024'},
                'esol_2025': {'action_value': 'ESOL 2025'}
            }
        }
        self.mock_config.get_win11_criteria.return_value = {
            'win11_patterns': ['Windows 11', 'Win11'],
            'migration_categories': ['esol_2024', 'esol_2025']
        }

        self.analyzer = Win11Analyzer(self.mock_config)

    def test_calculate_kpi_metrics_basic(self):
        """Test KPI calculation with basic counts."""
        counts = {
            'total_enterprise': 1000,
            'enterprise_win11_count': 400,
            'enterprise_esol_count': 200,
            'total_enterprise_win11_path': 600,
            'current_win11_pct': 40.0,
            'win11_adoption_pct': 60.0
        }

        kpi = self.analyzer.calculate_kpi_metrics(counts)

        # Total eligible = 1000 - 200 = 800
        self.assertEqual(kpi['total_eligible'], 800)
        # Upgraded pct = 400 / 800 * 100 = 50.0
        self.assertEqual(kpi['upgraded_pct'], 50.0)
        # Pending = 800 - 400 = 400
        self.assertEqual(kpi['pending_count'], 400)

    def test_calculate_kpi_metrics_zero_eligible(self):
        """Test KPI calculation when no eligible devices."""
        counts = {
            'total_enterprise': 200,
            'enterprise_win11_count': 0,
            'enterprise_esol_count': 200,  # All devices are ESOL
            'total_enterprise_win11_path': 200,
            'current_win11_pct': 0.0,
            'win11_adoption_pct': 100.0
        }

        kpi = self.analyzer.calculate_kpi_metrics(counts)

        # Total eligible = 200 - 200 = 0
        self.assertEqual(kpi['total_eligible'], 0)
        # Percentage should be 0 when no eligible devices
        self.assertEqual(kpi['upgraded_pct'], 0)
        # Pending = 0 - 0 = 0
        self.assertEqual(kpi['pending_count'], 0)

    def test_calculate_kpi_metrics_complete(self):
        """Test KPI calculation when 100% upgraded."""
        counts = {
            'total_enterprise': 1000,
            'enterprise_win11_count': 800,
            'enterprise_esol_count': 200,
            'total_enterprise_win11_path': 1000,
            'current_win11_pct': 80.0,
            'win11_adoption_pct': 100.0
        }

        kpi = self.analyzer.calculate_kpi_metrics(counts)

        # Total eligible = 1000 - 200 = 800
        self.assertEqual(kpi['total_eligible'], 800)
        # Upgraded pct = 800 / 800 * 100 = 100.0
        self.assertEqual(kpi['upgraded_pct'], 100.0)
        # Pending = 800 - 800 = 0
        self.assertEqual(kpi['pending_count'], 0)

    def test_calculate_kpi_metrics_partial(self):
        """Test KPI calculation with partial progress."""
        counts = {
            'total_enterprise': 5000,
            'enterprise_win11_count': 1500,
            'enterprise_esol_count': 1000,
            'total_enterprise_win11_path': 2500,
            'current_win11_pct': 30.0,
            'win11_adoption_pct': 50.0
        }

        kpi = self.analyzer.calculate_kpi_metrics(counts)

        # Total eligible = 5000 - 1000 = 4000
        self.assertEqual(kpi['total_eligible'], 4000)
        # Upgraded pct = 1500 / 4000 * 100 = 37.5
        self.assertEqual(kpi['upgraded_pct'], 37.5)
        # Pending = 4000 - 1500 = 2500
        self.assertEqual(kpi['pending_count'], 2500)


if __name__ == '__main__':
    unittest.main()
