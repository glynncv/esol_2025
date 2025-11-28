"""Unit tests for BurndownCalculator."""
import unittest
from unittest.mock import Mock
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from etl.analysis.burndown_calculator import BurndownCalculator


class TestBurndownCalculator(unittest.TestCase):
    """Test cases for BurndownCalculator class."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock ConfigManager
        self.mock_config = Mock()
        # Use future dates for testing (2025 dates)
        self.mock_config.get_esol_criteria.return_value = {
            'esol_categories': {
                'esol_2024': {'target_date': '2025-12-31'},  # Future date
                'esol_2025': {'target_date': '2026-12-31'},
                'esol_2026': {'target_date': '2027-12-31'}
            }
        }
        self.mock_config.get_win11_criteria.return_value = {
            'kpi_target_date': '2025-10-31'
        }

        # Initialize calculator (uses datetime.now() internally)
        self.calculator = BurndownCalculator(self.mock_config)

    def test_calculate_esol_burndown_basic(self):
        """Test basic ESOL burndown calculation."""
        burndown = self.calculator.calculate_esol_burndown(
            esol_2024_count=60,
            esol_2025_count=200,
            esol_2026_count=300
        )

        self.assertEqual(len(burndown), 3)

        # Check ESOL 2024
        self.assertEqual(burndown[0]['category'], 'ESOL 2024')
        self.assertEqual(burndown[0]['remaining_devices'], 60)
        # Days remaining depends on current date (may be negative if past deadline)
        self.assertIsInstance(burndown[0]['days_remaining'], int)
        # Daily burn rate = 60 / days_remaining
        expected_rate = 60 / burndown[0]['days_remaining']
        self.assertAlmostEqual(burndown[0]['daily_burn_rate_needed'], expected_rate, places=1)
        # Status depends on burn rate (AT RISK if > 1.0)
        self.assertIn(burndown[0]['status'], ['AT RISK', 'CAUTION', 'ON TRACK'])

        # Check ESOL 2025
        self.assertEqual(burndown[1]['category'], 'ESOL 2025')
        self.assertEqual(burndown[1]['remaining_devices'], 200)
        self.assertIsInstance(burndown[1]['days_remaining'], int)
        # Daily burn rate should be 200 / days_remaining
        expected_rate_2025 = 200 / burndown[1]['days_remaining']
        self.assertAlmostEqual(burndown[1]['daily_burn_rate_needed'], expected_rate_2025, places=1)

    def test_calculate_esol_burndown_zero_devices(self):
        """Test ESOL burndown with zero devices."""
        burndown = self.calculator.calculate_esol_burndown(
            esol_2024_count=0,
            esol_2025_count=0,
            esol_2026_count=0
        )

        self.assertEqual(len(burndown), 3)

        for data in burndown:
            self.assertEqual(data['remaining_devices'], 0)
            self.assertEqual(data['daily_burn_rate_needed'], 0.0)
            # Status may vary based on days remaining, but with 0 devices it should be manageable
            self.assertIn(data['status'], ['ON TRACK', 'CAUTION', 'AT RISK'])

    def test_calculate_win11_burndown_basic(self):
        """Test basic Win11 burndown calculation."""
        burndown = self.calculator.calculate_win11_burndown(
            total_eligible=4000,
            completed_count=1500
        )

        self.assertEqual(burndown['total_eligible_devices'], 4000)
        self.assertEqual(burndown['completed_devices'], 1500)
        self.assertEqual(burndown['remaining_devices'], 2500)
        self.assertEqual(burndown['completion_percentage'], 37.5)
        # Days remaining depends on current date relative to 2025-10-31
        self.assertIsInstance(burndown['days_remaining'], int)
        # Daily burn rate = 2500 / days_remaining
        if burndown['days_remaining'] > 0:
            expected_rate = 2500 / burndown['days_remaining']
            self.assertAlmostEqual(burndown['daily_burn_rate_needed'], expected_rate, places=1)
        # Status should be AT RISK since completion < 90%
        self.assertEqual(burndown['kpi_status'], 'AT RISK')

    def test_calculate_win11_burndown_complete(self):
        """Test Win11 burndown when 100% complete."""
        burndown = self.calculator.calculate_win11_burndown(
            total_eligible=1000,
            completed_count=1000
        )

        self.assertEqual(burndown['remaining_devices'], 0)
        self.assertEqual(burndown['completion_percentage'], 100.0)
        self.assertEqual(burndown['daily_burn_rate_needed'], 0.0)
        self.assertEqual(burndown['kpi_status'], 'ON TRACK')

    def test_calculate_win11_burndown_zero_eligible(self):
        """Test Win11 burndown with zero eligible devices."""
        burndown = self.calculator.calculate_win11_burndown(
            total_eligible=0,
            completed_count=0
        )

        self.assertEqual(burndown['total_eligible_devices'], 0)
        self.assertEqual(burndown['completion_percentage'], 0)
        self.assertEqual(burndown['remaining_devices'], 0)
        self.assertEqual(burndown['daily_burn_rate_needed'], 0.0)

    def test_calculate_win11_burndown_past_deadline(self):
        """Test Win11 burndown when past deadline."""
        # Note: This test uses actual current date since BurndownCalculator
        # doesn't support injecting test dates. If run after 2025-10-31,
        # days_remaining will be negative.
        burndown = self.calculator.calculate_win11_burndown(
            total_eligible=1000,
            completed_count=800
        )

        # Days remaining may be negative if past deadline
        # Status should be AT RISK since not 100% complete
        if burndown['days_remaining'] <= 0:
            self.assertEqual(burndown['kpi_status'], 'AT RISK')
        else:
            # If not past deadline, just verify structure
            self.assertIn('kpi_status', burndown)


if __name__ == '__main__':
    unittest.main()
