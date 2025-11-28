"""Unit tests for presentation formatters."""
import unittest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from etl.presentation import Win11Formatter, ESOLFormatter, KioskFormatter, BurndownFormatter


class TestWin11Formatter(unittest.TestCase):
    """Test cases for Win11Formatter class."""

    def test_format_markdown_report_without_kpi(self):
        """Test markdown report generation without KPI data."""
        counts = {
            'total_enterprise': 1000,
            'enterprise_win11_count': 400,
            'enterprise_esol_count': 200,
            'total_enterprise_win11_path': 600,
            'current_win11_pct': 40.0,
            'win11_adoption_pct': 60.0
        }

        report = Win11Formatter.format_markdown_report(counts)

        # Check required sections
        self.assertIn("# Windows 11 EUC Count Analysis", report)
        self.assertIn("**Total Enterprise devices:** 1,000", report)
        self.assertIn("## Windows 11 Status", report)
        self.assertIn("400 devices", report)
        self.assertIn("200 devices", report)
        # Should not have KPI section
        self.assertNotIn("## Windows 11 Upgrade KPI", report)

    def test_format_markdown_report_with_kpi(self):
        """Test markdown report generation with KPI data."""
        counts = {
            'total_enterprise': 1000,
            'enterprise_win11_count': 400,
            'enterprise_esol_count': 200,
            'total_enterprise_win11_path': 600,
            'current_win11_pct': 40.0,
            'win11_adoption_pct': 60.0
        }
        kpi_data = {
            'total_eligible': 800,
            'upgraded_pct': 50.0,
            'pending_count': 400
        }

        report = Win11Formatter.format_markdown_report(counts, kpi_data=kpi_data)

        # Check required sections
        self.assertIn("# Windows 11 EUC Count Analysis", report)
        self.assertIn("## Windows 11 Upgrade KPI", report)
        self.assertIn("**Total Windows 11 Eligible EUCs:** 800", report)
        self.assertIn("**Already Upgraded:** 400 (50.0%)", report)
        self.assertIn("**Pending Upgrade:** 400", report)
        self.assertIn("## Summary", report)

    def test_format_console_summary(self):
        """Test console summary formatting."""
        counts = {
            'total_enterprise': 1000,
            'enterprise_win11_count': 400,
            'enterprise_esol_count': 200,
            'total_enterprise_win11_path': 600,
            'current_win11_pct': 40.0,
            'win11_adoption_pct': 60.0
        }

        console = Win11Formatter.format_console_summary(counts, 800, 50.0, 400)

        self.assertIn("Total Enterprise EUCs: 1,000", console)
        self.assertIn("400 (40.0%)", console)
        self.assertIn("Windows 11 Upgrade KPI", console)
        self.assertIn("Total Windows 11 Eligible EUCs: 800", console)


class TestESOLFormatter(unittest.TestCase):
    """Test cases for ESOLFormatter class."""

    def test_format_markdown_report_all_categories(self):
        """Test ESOL markdown report with all categories."""
        counts = {
            'total_devices': 5000,
            'esol_2024': 50,
            'esol_2025': 150,
            'esol_2026': 200,
            'total_esol': 400,
            'non_esol': 4600
        }
        percentages = {
            'esol_2024_pct': 1.0,
            'esol_2025_pct': 3.0,
            'esol_2026_pct': 4.0,
            'total_esol_pct': 8.0,
            'non_esol_pct': 92.0
        }

        report = ESOLFormatter.format_markdown_report(counts, percentages, 'all')

        self.assertIn("# ESOL Device Count Analysis", report)
        self.assertIn("**Total devices analyzed:** 5,000", report)
        self.assertIn("## ESOL Category Breakdown", report)
        self.assertIn("**ESOL 2024:** 50 devices", report)
        self.assertIn("**ESOL 2025:** 150 devices", report)
        self.assertIn("**ESOL 2026:** 200 devices", report)

    def test_format_markdown_report_single_category(self):
        """Test ESOL markdown report with single category."""
        counts = {
            'total_devices': 5000,
            'esol_2024': 50,
            'esol_2025': 150,
            'esol_2026': 200,
            'total_esol': 400,
            'non_esol': 4600
        }
        percentages = {
            'esol_2024_pct': 1.0,
            'esol_2025_pct': 3.0,
            'esol_2026_pct': 4.0,
            'total_esol_pct': 8.0,
            'non_esol_pct': 92.0
        }

        report = ESOLFormatter.format_markdown_report(counts, percentages, 'esol_2025')

        self.assertIn("# ESOL Device Count Analysis", report)
        self.assertIn("## ESOL 2025 Analysis", report)
        self.assertIn("**Count:** 150 devices", report)
        self.assertIn("**Percentage:** 3.0%", report)


class TestKioskFormatter(unittest.TestCase):
    """Test cases for KioskFormatter class."""

    def test_format_markdown_report(self):
        """Test Kiosk markdown report generation."""
        counts = {
            'total_devices': 5000,
            'total_kiosk': 500,
            'enterprise_count': 300,
            'enterprise_pct': 60.0,
            'ltsc_count': 200,
            'ltsc_pct': 40.0
        }
        ltsc_migration = {
            'ltsc_kiosk_count': 200,
            'ltsc_not_win11_count': 150,
            'ltsc_not_win11_pct': 75.0
        }

        report = KioskFormatter.format_markdown_report(counts, ltsc_migration)

        self.assertIn("# Kiosk EUC Count Analysis", report)
        self.assertIn("**Total Kiosk EUCs:** 500", report)
        self.assertIn("## Kiosk EUC Breakdown", report)
        self.assertIn("300", report)
        self.assertIn("60.0%", report)


class TestBurndownFormatter(unittest.TestCase):
    """Test cases for BurndownFormatter class."""

    def test_format_esol_markdown_report(self):
        """Test ESOL burndown markdown report."""
        burndown_data = [
            {
                'category': 'ESOL 2024',
                'target_date': '2024-12-31',
                'days_remaining': 30,
                'remaining_devices': 50,
                'daily_burn_rate_needed': 1.67,
                'status': 'AT RISK'
            },
            {
                'category': 'ESOL 2025',
                'target_date': '2025-12-31',
                'days_remaining': 395,
                'remaining_devices': 150,
                'daily_burn_rate_needed': 0.38,
                'status': 'ON TRACK'
            }
        ]

        report = BurndownFormatter.format_esol_markdown_report(burndown_data)

        self.assertIn("# ESOL Replacement Burndown Report", report)
        self.assertIn("## ESOL Category Burndown Analysis", report)
        self.assertIn("ESOL 2024", report)
        self.assertIn("ESOL 2025", report)
        self.assertIn("AT RISK", report)
        self.assertIn("ON TRACK", report)

    def test_format_win11_markdown_report(self):
        """Test Win11 burndown markdown report."""
        burndown_data = {
            'target_date': '2025-10-31',
            'days_remaining': 312,
            'total_eligible_devices': 4000,
            'completed_devices': 1500,
            'remaining_devices': 2500,
            'completion_percentage': 37.5,
            'daily_burn_rate_needed': 8.01,
            'kpi_status': 'AT RISK'
        }

        report = BurndownFormatter.format_win11_markdown_report(burndown_data)

        self.assertIn("# Windows 11 Upgrade Burndown Report", report)
        self.assertIn("## KPI Target", report)
        self.assertIn("2025-10-31", report)
        self.assertIn("4,000", report)
        self.assertIn("1,500", report)
        self.assertIn("2,500", report)
        self.assertIn("37.5%", report)


if __name__ == '__main__':
    unittest.main()
