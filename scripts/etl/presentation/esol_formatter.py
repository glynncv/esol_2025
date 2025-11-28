"""ESOL presentation formatter for reports and console output."""
from typing import Dict
import pandas as pd
from datetime import datetime


class ESOLFormatter:
    """Format ESOL analysis results into reports and console output.

    Pure presentation layer - no business logic, only formatting.
    """

    @staticmethod
    def format_markdown_report(counts: Dict[str, int], percentages: Dict[str, float],
                                category: str = 'all') -> str:
        """Format ESOL analysis into markdown report.

        Args:
            counts: Dictionary from ESOLAnalyzer.calculate_esol_counts()
            percentages: Dictionary from ESOLAnalyzer.calculate_esol_percentages()
            category: Filter to specific category ('esol_2024', 'esol_2025', 'esol_2026', 'all')

        Returns:
            Formatted markdown report string
        """
        report_lines = []
        report_lines.append(
            f"# ESOL Device Count Analysis - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        report_lines.append("")
        report_lines.append(f"**Total devices analyzed:** {counts['total_devices']:,}")
        report_lines.append("")

        # Output based on category parameter
        if category == 'esol_2024':
            report_lines.append(f"## ESOL 2024 Analysis")
            report_lines.append(f"- **Count:** {counts['esol_2024']} devices")
            report_lines.append(f"- **Percentage:** {percentages['esol_2024_pct']}%")
            report_lines.append(f"- **Status:** Down from the previous count")
        elif category == 'esol_2025':
            report_lines.append(f"## ESOL 2025 Analysis")
            report_lines.append(f"- **Count:** {counts['esol_2025']} devices")
            report_lines.append(f"- **Percentage:** {percentages['esol_2025_pct']}%")
        elif category == 'esol_2026':
            report_lines.append(f"## ESOL 2026 Analysis")
            report_lines.append(f"- **Count:** {counts['esol_2026']} devices")
            report_lines.append(f"- **Percentage:** {percentages['esol_2026_pct']}%")
        else:  # 'all'
            report_lines.append("## ESOL Category Breakdown")
            report_lines.append("")
            report_lines.append(f"- **ESOL 2024:** {counts['esol_2024']} devices ({percentages['esol_2024_pct']}%)")
            report_lines.append(f"- **ESOL 2025:** {counts['esol_2025']} devices ({percentages['esol_2025_pct']}%)")
            report_lines.append(f"- **ESOL 2026:** {counts['esol_2026']} devices ({percentages['esol_2026_pct']}%)")
            report_lines.append(
                f"- **Total ESOL:** {counts['total_esol']} devices ({percentages['total_esol_pct']}%) "
                f"instead of 434"
            )
            report_lines.append(
                f"- **Non-ESOL:** {counts['non_esol']:,} devices ({percentages['non_esol_pct']}%) "
                f"- slightly better compatibility"
            )

        report_lines.append("")
        return "\n".join(report_lines)

    @staticmethod
    def format_console_summary(counts: Dict[str, int], percentages: Dict[str, float],
                               category: str = 'all') -> str:
        """Format ESOL summary for console output.

        Args:
            counts: Dictionary from ESOLAnalyzer.calculate_esol_counts()
            percentages: Dictionary from ESOLAnalyzer.calculate_esol_percentages()
            category: Filter to specific category

        Returns:
            Formatted string for console display
        """
        lines = []

        if category == 'esol_2024':
            lines.append(f"ESOL 2024: {counts['esol_2024']} devices ({percentages['esol_2024_pct']}%) - down from the previous count")
        elif category == 'esol_2025':
            lines.append(f"ESOL 2025: {counts['esol_2025']} devices ({percentages['esol_2025_pct']}%)")
        elif category == 'esol_2026':
            lines.append(f"ESOL 2026: {counts['esol_2026']} devices ({percentages['esol_2026_pct']}%)")
        else:  # 'all'
            lines.append(f"ESOL 2024: {counts['esol_2024']} devices ({percentages['esol_2024_pct']}%) - down from the previous count")
            lines.append(f"ESOL 2025: {counts['esol_2025']} devices ({percentages['esol_2025_pct']}%)")
            lines.append(f"ESOL 2026: {counts['esol_2026']} devices ({percentages['esol_2026_pct']}%)")
            lines.append(f"Total ESOL: {counts['total_esol']} devices ({percentages['total_esol_pct']}%) instead of 434")
            lines.append(f"Non-ESOL: {counts['non_esol']:,} devices ({percentages['non_esol_pct']}%) - slightly better compatibility")

        return "\n".join(lines)

    @staticmethod
    def format_site_summary_console(site_data: pd.DataFrame) -> str:
        """Format site summary for console output.

        Args:
            site_data: DataFrame from ESOLAnalyzer.generate_site_summary()

        Returns:
            Formatted string for console display
        """
        lines = []
        lines.append("Site Summary - ESOL Devices and Cost:")
        lines.append("=" * 70)

        for site, row in site_data.iterrows():
            lines.append(
                f"{site}: {int(row['Total_ESOL'])} devices "
                f"(2024: {int(row['ESOL_2024_Count'])}, "
                f"2025: {int(row['ESOL_2025_Count'])}, "
                f"2026: {int(row['ESOL_2026_Count'])}) "
                f"- ${row['Total_Cost']:,.0f}"
            )

        return "\n".join(lines)
