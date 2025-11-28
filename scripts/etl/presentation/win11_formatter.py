"""Windows 11 presentation formatter for reports and console output."""
from typing import Dict
import pandas as pd
from datetime import datetime


class Win11Formatter:
    """Format Windows 11 analysis results into reports and console output.

    Pure presentation layer - no business logic, only formatting.
    """

    @staticmethod
    def format_markdown_report(counts: Dict[str, int], kpi_data: Dict = None) -> str:
        """Format Windows 11 analysis into markdown report.

        Args:
            counts: Dictionary from Win11Analyzer.calculate_win11_counts()
            kpi_data: Optional dictionary with KPI metrics (total_eligible, upgraded_pct, pending_count)

        Returns:
            Formatted markdown report string
        """
        report_lines = []
        report_lines.append(
            f"# Windows 11 EUC Count Analysis - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        report_lines.append("")
        report_lines.append(f"**Total Enterprise devices:** {counts['total_enterprise']:,}")
        report_lines.append("")
        report_lines.append("## Windows 11 Status")
        report_lines.append("")
        report_lines.append(
            f"- **Current Win11 Devices:** {counts['enterprise_win11_count']:,} devices "
            f"({counts['current_win11_pct']}%)"
        )
        report_lines.append(
            f"- **ESOL Replacement Path:** {counts['enterprise_esol_count']:,} devices "
            f"getting Win11 via new hardware"
        )
        report_lines.append(
            f"- **Total Win11 Adoption Path:** {counts['total_enterprise_win11_path']:,} devices "
            f"({counts['win11_adoption_pct']}%)"
        )
        report_lines.append("")

        # Add KPI section if data provided
        if kpi_data:
            total_eligible = kpi_data['total_eligible']
            upgraded_pct = kpi_data['upgraded_pct']
            pending_count = kpi_data['pending_count']

            report_lines.append("## Windows 11 Upgrade KPI (Target: 100% by Oct 2025)")
            report_lines.append(f"**Total Windows 11 Eligible EUCs:** {total_eligible:,} (excluding ESOL replacement devices)")
            report_lines.append(f"**Already Upgraded:** {counts['enterprise_win11_count']:,} ({upgraded_pct}%)")
            report_lines.append(f"**Pending Upgrade:** {pending_count:,}")

            kpi_status = "🟢 ON TRACK" if upgraded_pct >= 100 else "🔴 AT RISK"
            report_lines.append(f"**KPI Status:** {kpi_status} - {pending_count:,} devices need upgrade by Oct 2025")
            report_lines.append("")

            report_lines.append("## Summary")
            report_lines.append(f"- **Current Windows 11 adoption:** {counts['current_win11_pct']}% of Enterprise EUCs")
            report_lines.append(f"- **Projected Windows 11 adoption:** {counts['win11_adoption_pct']}% of Enterprise EUCs (via replacement + upgrade)")
            report_lines.append(f"- **Upgrade KPI Progress:** {upgraded_pct}% of eligible devices upgraded")
            report_lines.append(f"- **LTSC devices excluded:** Not part of 2025 Windows 11 push strategy")
            report_lines.append("")

        return "\n".join(report_lines)

    @staticmethod
    def format_console_summary(counts: Dict[str, int], total_eligible: int,
                               eligible_upgraded_pct: float, eligible_pending_count: int) -> str:
        """Format Windows 11 summary for console output.

        Args:
            counts: Dictionary from Win11Analyzer.calculate_win11_counts()
            total_eligible: Total eligible devices (excluding ESOL)
            eligible_upgraded_pct: Percentage of eligible devices upgraded
            eligible_pending_count: Count of eligible devices pending upgrade

        Returns:
            Formatted string for console display
        """
        lines = []
        lines.append(f"Total Enterprise EUCs: {counts['total_enterprise']:,}")
        lines.append(f"Enterprise EUCs already on Windows 11: {counts['enterprise_win11_count']:,} ({counts['current_win11_pct']}%)")
        lines.append(f"Enterprise EUCs getting Windows 11 via ESOL replacement: {counts['enterprise_esol_count']:,}")
        lines.append(f"Total Enterprise Windows 11 adoption path: {counts['total_enterprise_win11_path']:,} ({counts['win11_adoption_pct']}%)")
        lines.append("")
        lines.append("🎯 Windows 11 Upgrade KPI (Target: 100% by Oct 2025):")
        lines.append(f"Total Windows 11 Eligible EUCs: {total_eligible:,} (excluding ESOL replacement)")
        lines.append(f"Already Upgraded: {counts['enterprise_win11_count']:,} ({eligible_upgraded_pct}%)")
        lines.append(f"Pending Upgrade: {eligible_pending_count:,}")
        kpi_status = '🟢 ON TRACK' if eligible_upgraded_pct >= 100 else '🔴 AT RISK'
        lines.append(f"KPI Status: {kpi_status} - {eligible_pending_count:,} devices need upgrade by Oct 2025")

        return "\n".join(lines)

    @staticmethod
    def format_site_summary_console(site_data: pd.DataFrame) -> str:
        """Format site summary for console output.

        Args:
            site_data: DataFrame from Win11Analyzer.generate_site_summary()

        Returns:
            Formatted string for console display
        """
        lines = []
        lines.append("\nSite Summary - Windows 11 Deployment Status:")
        lines.append("=" * 120)
        lines.append(
            f"{'Site':<25} | {'Total':<6} | {'Win11 Eligible':<15} | "
            f"{'Win11':<15} | {'Pending':<15}"
        )
        lines.append(
            f"{'':<25} | {'Devices':<6} | {'# (%) Eligible':<15} | "
            f"{'# (%) Upgraded':<15} | {'# (%) Pending':<15}"
        )
        lines.append("-" * 120)

        for site, row in site_data.iterrows():
            lines.append(
                f"{site:<25} | {int(row['Total_Devices']):>6} | "
                f"{int(row['Win11_Eligible_Count']):>3} ({row['Win11_Eligible_Pct']:>4.1f}%) | "
                f"{int(row['Win11_Count']):>3} ({row['Win11_Pct']:>4.1f}%) | "
                f"{int(row['Pending_Count']):>3} ({row['Pending_Pct']:>4.1f}%)"
            )

        return "\n".join(lines)
