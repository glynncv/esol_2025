"""Kiosk presentation formatter for reports and console output."""
from typing import Dict
from datetime import datetime


class KioskFormatter:
    """Format Kiosk analysis results into reports and console output.

    Pure presentation layer - no business logic, only formatting.
    """

    @staticmethod
    def format_markdown_report(counts: Dict[str, int], ltsc_migration: Dict[str, int]) -> str:
        """Format kiosk analysis into markdown report.

        Args:
            counts: Dictionary from KioskAnalyzer.calculate_kiosk_counts()
            ltsc_migration: Dictionary from KioskAnalyzer.calculate_ltsc_win11_migration()

        Returns:
            Formatted markdown report string
        """
        report_lines = []
        report_lines.append(
            f"# Kiosk EUC Count Analysis - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        report_lines.append("")
        report_lines.append(f"**Total devices analyzed:** {counts['total_devices']:,}")
        report_lines.append(f"**Total Kiosk EUCs:** {counts['total_kiosk']:,}")
        report_lines.append("")
        report_lines.append("## Kiosk EUC Breakdown")
        report_lines.append(f"- **Total # of Kiosk EUCs:** {counts['total_kiosk']:,}")
        report_lines.append(
            f"- **Total # (%) of Kiosk EUCs that are Enterprise:** "
            f"{counts['enterprise_count']:,} ({counts['enterprise_pct']}%)"
        )
        report_lines.append(
            f"- **Total # (%) of Kiosk EUCs that are LTSC:** "
            f"{counts['ltsc_count']:,} ({counts['ltsc_pct']}%)"
        )
        report_lines.append("")
        report_lines.append("## LTSC Kiosk Windows 11 Migration Status")
        report_lines.append(
            f"- **Total # of LTSC Kiosk EUCs:** {ltsc_migration['ltsc_kiosk_count']:,}"
        )
        report_lines.append(
            f"- **Total # (%) of LTSC Kiosk EUCs not yet migrated to Windows 11:** "
            f"{ltsc_migration['ltsc_not_win11_count']:,} ({ltsc_migration['ltsc_not_win11_pct']}%)"
        )
        report_lines.append("")
        report_lines.append(
            "**Note:** LTSC Kiosk devices are excluded from the 2025 Windows 11 push strategy."
        )
        report_lines.append(
            "Only Enterprise Kiosk devices are targeted for Windows 11 migration."
        )

        return "\n".join(report_lines)

    @staticmethod
    def format_console_summary(counts: Dict[str, int], ltsc_migration: Dict[str, int]) -> str:
        """Format kiosk analysis for console output.

        Args:
            counts: Dictionary from KioskAnalyzer.calculate_kiosk_counts()
            ltsc_migration: Dictionary from KioskAnalyzer.calculate_ltsc_win11_migration()

        Returns:
            Formatted string for console display
        """
        lines = []
        lines.append(f"Total # of Kiosk EUCs: {counts['total_kiosk']:,}")
        lines.append(
            f"Total # (%) of Kiosk EUCs that are Enterprise: "
            f"{counts['enterprise_count']:,} ({counts['enterprise_pct']}%)"
        )
        lines.append(
            f"Total # (%) of Kiosk EUCs that are LTSC: "
            f"{counts['ltsc_count']:,} ({counts['ltsc_pct']}%)"
        )
        lines.append(
            f"Total # (%) of LTSC Kiosk EUCs not yet migrated to Windows 11: "
            f"{ltsc_migration['ltsc_not_win11_count']:,} ({ltsc_migration['ltsc_not_win11_pct']}%)"
        )

        return "\n".join(lines)
