"""Burndown presentation formatter for reports and console output."""
from typing import Dict, List, Union
from datetime import datetime


class BurndownFormatter:
    """Format burndown analysis results into reports and console output.

    Pure presentation layer - no business logic, only formatting.
    """

    @staticmethod
    def format_esol_markdown_report(burndown_data: List[Dict]) -> str:
        """Format ESOL burndown data into markdown report.

        Args:
            burndown_data: List of burndown dictionaries from BurndownCalculator.calculate_esol_burndown()

        Returns:
            Formatted markdown report string
        """
        current_date = datetime.now()
        report_lines = [
            f"# ESOL Replacement Burndown Report - {current_date.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## ESOL Category Burndown Analysis",
            "",
            "| Category | Target Date | Days Remaining | Remaining Devices | Daily Burn Rate Needed | Status |",
            "|----------|-------------|----------------|-------------------|----------------------|--------|"
        ]

        for data in burndown_data:
            status_icon = "🔴" if data['status'] == 'AT RISK' else "🟢"
            report_lines.append(
                f"| {data['category']} | {data['target_date']} | {data['days_remaining']} | "
                f"{data['remaining_devices']} | {data['daily_burn_rate_needed']} | {status_icon} {data['status']} |"
            )

        report_lines.extend([
            "",
            "## Risk Assessment",
            ""
        ])

        # Add risk details per category
        for data in burndown_data:
            if data['status'] == 'AT RISK':
                report_lines.append(
                    f"- **{data['category']}:** {data['remaining_devices']} devices need replacement "
                    f"in {data['days_remaining']} days ({data['daily_burn_rate_needed']} per day)"
                )

        report_lines.extend([
            "",
            "## Recommendations",
            "1. **Prioritize ESOL 2024 devices** - highest urgency with nearest deadline",
            "2. **Accelerate procurement and deployment** for devices at risk",
            "3. **Weekly tracking** to monitor burndown progress",
            "4. **Focus on high-cost sites** to maximize ROI of replacement efforts",
            ""
        ])

        return "\n".join(report_lines)

    @staticmethod
    def format_win11_markdown_report(burndown_data: Dict) -> str:
        """Format Windows 11 burndown data into markdown report.

        Args:
            burndown_data: Burndown dictionary from BurndownCalculator.calculate_win11_burndown()

        Returns:
            Formatted markdown report string
        """
        current_date = datetime.now()
        days_remaining = burndown_data['days_remaining']
        daily_burn_rate = burndown_data['daily_burn_rate_needed']
        completion_pct = burndown_data['completion_percentage']

        report = f"""# Windows 11 Upgrade Burndown Report - {current_date.strftime('%Y-%m-%d %H:%M:%S')}

## KPI Target
**Target Date:** {burndown_data['target_date']}
**Target:** 100% of eligible EUCs upgraded
**Days Remaining:** {days_remaining}

## Progress Summary
**Total Eligible Devices:** {burndown_data['total_eligible_devices']:,}
**Completed Upgrades:** {burndown_data['completed_devices']:,}
**Remaining Upgrades:** {burndown_data['remaining_devices']:,}
**Completion Percentage:** {completion_pct}%

## Burndown Analysis
**Daily Burn Rate Needed:** {daily_burn_rate:.2f} devices/day
**KPI Status:** {burndown_data['kpi_status']}

## Risk Assessment
"""

        if days_remaining > 0:
            if daily_burn_rate > 1:
                report += f"- **🔴 HIGH RISK:** Need to upgrade {daily_burn_rate:.2f} devices per day\n"
            elif daily_burn_rate > 0.5:
                report += f"- **🟡 MEDIUM RISK:** Need to upgrade {daily_burn_rate:.2f} devices per day\n"
            else:
                report += f"- **🟢 LOW RISK:** Only {daily_burn_rate:.2f} devices per day needed\n"
        else:
            report += f"- **{'✅ TARGET MET' if completion_pct >= 100 else '❌ TARGET MISSED'}**\n"

        report += f"""
## Recommendations
1. **Focus on sites with highest pending counts**
2. **Accelerate upgrade process if burn rate is insufficient**
3. **Monitor progress weekly to stay on track**
4. **Coordinate with IT teams** to maximize daily upgrade throughput

---
*Report generated from centralized burndown calculator*
"""

        return report

    @staticmethod
    def format_esol_console_summary(burndown_data: List[Dict]) -> str:
        """Format ESOL burndown summary for console output.

        Args:
            burndown_data: List of burndown dictionaries

        Returns:
            Formatted string for console display
        """
        lines = []
        lines.append("\n🔥 ESOL Replacement Burndown Analysis:")
        lines.append("=" * 60)

        for data in burndown_data:
            status_icon = "🔴" if data['status'] == 'AT RISK' else "🟢"
            lines.append(f"{data['category']}: {data['remaining_devices']} devices, {data['days_remaining']} days left")
            lines.append(f"  Daily burn rate needed: {data['daily_burn_rate_needed']} devices/day")
            lines.append(f"  Status: {status_icon} {data['status']}")
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def format_win11_console_summary(burndown_data: Dict) -> str:
        """Format Windows 11 burndown summary for console output.

        Args:
            burndown_data: Burndown dictionary

        Returns:
            Formatted string for console display
        """
        lines = []
        lines.append("\n🔥 Windows 11 Upgrade Burndown Analysis:")
        lines.append("=" * 60)
        lines.append(f"Target Date: {burndown_data['target_date']}")
        lines.append(f"Days Remaining: {burndown_data['days_remaining']}")
        lines.append(f"Total Eligible: {burndown_data['total_eligible_devices']:,}")
        lines.append(f"Completed: {burndown_data['completed_devices']:,} ({burndown_data['completion_percentage']}%)")
        lines.append(f"Remaining: {burndown_data['remaining_devices']:,}")
        lines.append(f"Daily Burn Rate Needed: {burndown_data['daily_burn_rate_needed']:.2f} devices/day")
        lines.append(f"KPI Status: {burndown_data['kpi_status']}")

        return "\n".join(lines)
