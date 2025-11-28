"""OKR presentation formatter for multi-level reports.

This module provides the OKRFormatter class which formats OKR analysis results
into comprehensive reports at multiple organizational levels.

Pure presentation layer - no business logic, only formatting.
"""
from typing import Dict
import pandas as pd
from datetime import datetime


class OKRFormatter:
    """Format multi-level OKR analysis results into reports and console output.

    Pure presentation layer - no business logic, only formatting.
    """

    @staticmethod
    def format_executive_dashboard(overall_scores: Dict,
                                   country_scores: pd.DataFrame,
                                   sdm_scores: pd.DataFrame,
                                   site_scores: pd.DataFrame,
                                   trend_data: Dict = None,
                                   burndown_trends: Dict = None) -> str:
        """Format comprehensive multi-level OKR dashboard with trends.

        Args:
            overall_scores: Dict from OKRAggregator.calculate_okr_scores()
            country_scores: DataFrame from OKRAggregator.aggregate_by_country()
            sdm_scores: DataFrame from OKRAggregator.aggregate_by_sdm()
            site_scores: DataFrame from OKRAggregator.aggregate_by_site()
            trend_data: Optional dict from TrendAnalyzer.calculate_overall_trends()
            burndown_trends: Optional dict from TrendAnalyzer.calculate_burndown_trends()

        Returns:
            Formatted markdown report string
        """
        report_lines = []
        report_lines.append(
            f"# OKR Executive Dashboard - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        report_lines.append("")

        # Add trend info to overall score if available
        if trend_data and trend_data.get('has_history'):
            trend_arrow = trend_data['okr_score_trend']
            trend_delta = trend_data['okr_score_delta']
            days_since = trend_data['days_since_previous']
            report_lines.append(
                f"## Overall Score: {overall_scores['okr_score']:.1f}/100 "
                f"{overall_scores['status_icon']} {overall_scores['status']} "
                f"{trend_arrow} ({trend_delta:+.1f} vs {days_since}d ago)"
            )
        else:
            report_lines.append(
                f"## Overall Score: {overall_scores['okr_score']:.1f}/100 "
                f"{overall_scores['status_icon']} {overall_scores['status']}"
            )
        report_lines.append("")

        # Key Results Summary
        report_lines.append("### Key Results")
        report_lines.append("")
        kr1_icon = '🟢' if overall_scores['kr1_score'] >= 80 else '🟡' if overall_scores['kr1_score'] >= 60 else '🔴'
        kr2_icon = '🟢' if overall_scores['kr2_score'] >= 80 else '🟡' if overall_scores['kr2_score'] >= 60 else '🔴'
        kr3_icon = '🟢' if overall_scores['kr3_score'] >= 80 else '🟡' if overall_scores['kr3_score'] >= 60 else '🔴'
        kr4_icon = '🟢' if overall_scores['kr4_score'] >= 80 else '🟡' if overall_scores['kr4_score'] >= 60 else '🔴'

        # Add trend arrows to KR lines if available
        kr1_trend = f" {trend_data['kr1_trend']}" if trend_data and trend_data.get('has_history') else ""
        kr2_trend = f" {trend_data['kr2_trend']}" if trend_data and trend_data.get('has_history') else ""
        kr3_trend = f" {trend_data['kr3_trend']}" if trend_data and trend_data.get('has_history') else ""
        kr4_trend = f" {trend_data['kr4_trend']}" if trend_data and trend_data.get('has_history') else ""

        report_lines.append(
            f"- **KR1** (ESOL 2024 Remediation): {overall_scores['kr1_score']:.1f}/100 {kr1_icon}{kr1_trend} "
            f"({overall_scores['kr1_value']} devices, {overall_scores['kr1_pct']:.2f}%)"
        )
        report_lines.append(
            f"- **KR2** (ESOL 2025 Remediation): {overall_scores['kr2_score']:.1f}/100 {kr2_icon}{kr2_trend} "
            f"({overall_scores['kr2_value']} devices, {overall_scores['kr2_pct']:.2f}%)"
        )
        report_lines.append(
            f"- **KR3** (Windows 11 Adoption): {overall_scores['kr3_score']:.1f}/100 {kr3_icon}{kr3_trend} "
            f"({overall_scores['kr3_value']:.1f}% adoption)"
        )
        report_lines.append(
            f"- **KR4** (Kiosk Re-provisioning): {overall_scores['kr4_score']:.1f}/100 {kr4_icon}{kr4_trend} "
            f"({overall_scores['kr4_value']} devices)"
        )
        report_lines.append("")
        report_lines.append(f"**Total Devices Analyzed:** {overall_scores['total_devices']:,}")
        report_lines.append("")

        # Add burndown trends section if available
        if burndown_trends and burndown_trends.get('has_sufficient_history'):
            report_lines.append("### Burndown Trends")
            report_lines.append("")
            report_lines.append(
                f"**Overall Direction:** {burndown_trends['trend_direction'].upper()} "
                f"(based on {burndown_trends['snapshots_analyzed']} snapshots over {burndown_trends['days_elapsed']} days)"
            )
            report_lines.append("")
            report_lines.append("**Velocity (change per day):**")
            report_lines.append(f"- KR1 (ESOL 2024): {burndown_trends['kr1_velocity']:.2f} devices/day reduction")
            report_lines.append(f"- KR2 (ESOL 2025): {burndown_trends['kr2_velocity']:.2f} devices/day reduction")
            report_lines.append(f"- KR3 (Win11): {burndown_trends['kr3_velocity']:.2f}% points/day increase")
            report_lines.append(f"- KR4 (Kiosk): {burndown_trends['kr4_velocity']:.2f} devices/day reduction")
            report_lines.append("")

            # Add projections
            if burndown_trends['projection_kr1_days_to_zero']:
                report_lines.append(
                    f"**Projection:** KR1 reaches zero in ~{burndown_trends['projection_kr1_days_to_zero']} days "
                    f"at current velocity"
                )
            if burndown_trends['projection_kr2_days_to_zero']:
                report_lines.append(
                    f"**Projection:** KR2 reaches zero in ~{burndown_trends['projection_kr2_days_to_zero']} days "
                    f"at current velocity"
                )
            report_lines.append("")

        report_lines.append("---")
        report_lines.append("")

        # Country Breakdown
        if len(country_scores) > 0:
            report_lines.append(f"## Country Breakdown ({len(country_scores)} countries)")
            report_lines.append("")

            # Check if trend columns exist
            has_trends = 'okr_score_trend' in country_scores.columns

            if has_trends:
                report_lines.append("| Country | Score | Trend | Status | Devices | KR1 | KR2 | KR3 | KR4 |")
                report_lines.append("|---------|-------|-------|--------|---------|-----|-----|-----|-----|")

                for _, row in country_scores.iterrows():
                    trend_str = f"{row['okr_score_trend']} {row['okr_score_delta']:+.1f}"
                    report_lines.append(
                        f"| {row['Country']:<20} | {row['okr_score']:>5.1f} | {trend_str:>6} | "
                        f"{row['status_icon']} {row['status']:<10} | {row['total_devices']:>7,} | "
                        f"{row['kr1_score']:>4.1f} | {row['kr2_score']:>4.1f} | "
                        f"{row['kr3_score']:>4.1f} | {row['kr4_score']:>4.1f} |"
                    )
            else:
                report_lines.append("| Country | Score | Status | Devices | KR1 | KR2 | KR3 | KR4 |")
                report_lines.append("|---------|-------|--------|---------|-----|-----|-----|-----|")

                for _, row in country_scores.iterrows():
                    report_lines.append(
                        f"| {row['Country']:<20} | {row['okr_score']:>5.1f} | "
                        f"{row['status_icon']} {row['status']:<10} | {row['total_devices']:>7,} | "
                        f"{row['kr1_score']:>4.1f} | {row['kr2_score']:>4.1f} | "
                        f"{row['kr3_score']:>4.1f} | {row['kr4_score']:>4.1f} |"
                    )

            report_lines.append("")
            report_lines.append("---")
            report_lines.append("")

        # SDM Performance
        if len(sdm_scores) > 0:
            report_lines.append(f"## SDM Performance ({len(sdm_scores)} managers)")
            report_lines.append("")

            # Check if trend columns exist
            has_trends = 'okr_score_trend' in sdm_scores.columns

            if has_trends:
                report_lines.append("| SDM | Score | Trend | Status | Devices | KR1 | KR2 | KR3 | KR4 |")
                report_lines.append("|-----|-------|-------|--------|---------|-----|-----|-----|-----|")

                for _, row in sdm_scores.iterrows():
                    trend_str = f"{row['okr_score_trend']} {row['okr_score_delta']:+.1f}"
                    report_lines.append(
                        f"| {row['SDM']:<25} | {row['okr_score']:>5.1f} | {trend_str:>6} | "
                        f"{row['status_icon']} {row['status']:<10} | {row['total_devices']:>7,} | "
                        f"{row['kr1_score']:>4.1f} | {row['kr2_score']:>4.1f} | "
                        f"{row['kr3_score']:>4.1f} | {row['kr4_score']:>4.1f} |"
                    )
            else:
                report_lines.append("| SDM | Score | Status | Devices | KR1 | KR2 | KR3 | KR4 |")
                report_lines.append("|-----|-------|--------|---------|-----|-----|-----|-----|")

                for _, row in sdm_scores.iterrows():
                    report_lines.append(
                        f"| {row['SDM']:<25} | {row['okr_score']:>5.1f} | "
                        f"{row['status_icon']} {row['status']:<10} | {row['total_devices']:>7,} | "
                        f"{row['kr1_score']:>4.1f} | {row['kr2_score']:>4.1f} | "
                        f"{row['kr3_score']:>4.1f} | {row['kr4_score']:>4.1f} |"
                    )

            report_lines.append("")
            report_lines.append("---")
            report_lines.append("")

        # Top Priority Sites
        if len(site_scores) > 0:
            report_lines.append(f"## Top Priority Sites (Top 10 of {len(site_scores)})")
            report_lines.append("")
            report_lines.append("Prioritized by ESOL urgency and overall OKR score:")
            report_lines.append("")

            # Show top 10 sites
            top_sites = site_scores.head(10)

            for idx, (_, row) in enumerate(top_sites.iterrows(), 1):
                site_name = row.get('Site Location', 'Unknown')
                priority = "🔴 CRITICAL" if row['kr1_value'] > 5 or row['okr_score'] < 60 else \
                          "🟡 HIGH" if row['kr1_value'] > 0 or row['okr_score'] < 75 else \
                          "🟢 MEDIUM"

                report_lines.append(
                    f"{idx}. **{site_name}** - Score: {row['okr_score']:.1f} {row['status_icon']} "
                    f"({row['total_devices']} devices) {priority}"
                )
                report_lines.append(
                    f"   - ESOL 2024: {row['kr1_value']}, ESOL 2025: {row['kr2_value']}, "
                    f"Win11: {row['kr3_value']:.1f}%, Kiosk: {row['kr4_value']}"
                )
                report_lines.append("")

            report_lines.append("---")
            report_lines.append("")

        # Footer
        report_lines.append("## Notes")
        report_lines.append("")
        report_lines.append("**OKR Weights:**")
        report_lines.append("- KR1 (ESOL 2024): 25%")
        report_lines.append("- KR2 (ESOL 2025): 25%")
        report_lines.append("- KR3 (Win11): 40%")
        report_lines.append("- KR4 (Kiosk): 10%")
        report_lines.append("")
        report_lines.append("**Status Thresholds:**")
        report_lines.append("- 🟢 ON TRACK: ≥80%")
        report_lines.append("- 🟡 CAUTION: 60-79%")
        report_lines.append("- 🔴 AT RISK: <60%")

        return "\n".join(report_lines)

    @staticmethod
    def format_console_summary(overall_scores: Dict,
                               country_scores: pd.DataFrame,
                               sdm_scores: pd.DataFrame) -> str:
        """Format OKR summary for console output.

        Args:
            overall_scores: Dict from OKRAggregator.calculate_okr_scores()
            country_scores: DataFrame from OKRAggregator.aggregate_by_country()
            sdm_scores: DataFrame from OKRAggregator.aggregate_by_sdm()

        Returns:
            Formatted string for console display
        """
        lines = []
        lines.append("=" * 80)
        lines.append("OKR EXECUTIVE SUMMARY")
        lines.append("=" * 80)
        lines.append("")
        lines.append(
            f"Overall Score: {overall_scores['okr_score']}/100 "
            f"{overall_scores['status_icon']} {overall_scores['status']}"
        )
        lines.append("")
        lines.append("Key Results:")
        lines.append(f"  KR1 (ESOL 2024): {overall_scores['kr1_score']:.1f}/100 ({overall_scores['kr1_value']} devices)")
        lines.append(f"  KR2 (ESOL 2025): {overall_scores['kr2_score']:.1f}/100 ({overall_scores['kr2_value']} devices)")
        lines.append(f"  KR3 (Win11):     {overall_scores['kr3_score']:.1f}/100 ({overall_scores['kr3_value']:.1f}% adoption)")
        lines.append(f"  KR4 (Kiosk):     {overall_scores['kr4_score']:.1f}/100 ({overall_scores['kr4_value']} devices)")
        lines.append("")
        lines.append(f"Total Devices: {overall_scores['total_devices']:,}")
        lines.append("")

        # Country Summary
        if len(country_scores) > 0:
            lines.append("-" * 80)
            lines.append(f"COUNTRY BREAKDOWN ({len(country_scores)} countries)")
            lines.append("-" * 80)
            for _, row in country_scores.head(5).iterrows():
                lines.append(
                    f"  {row['Country']:<20} Score: {row['okr_score']:>5.1f} {row['status_icon']} "
                    f"({row['total_devices']:>5,} devices)"
                )
            if len(country_scores) > 5:
                lines.append(f"  ... and {len(country_scores) - 5} more countries")
            lines.append("")

        # SDM Summary
        if len(sdm_scores) > 0:
            lines.append("-" * 80)
            lines.append(f"SDM PERFORMANCE ({len(sdm_scores)} managers)")
            lines.append("-" * 80)
            for _, row in sdm_scores.iterrows():
                lines.append(
                    f"  {row['SDM']:<25} Score: {row['okr_score']:>5.1f} {row['status_icon']} "
                    f"({row['total_devices']:>5,} devices)"
                )
            lines.append("")

        lines.append("=" * 80)

        return "\n".join(lines)

    @staticmethod
    def format_country_detail_report(country_name: str,
                                     country_scores: Dict,
                                     site_scores: pd.DataFrame) -> str:
        """Format detailed report for a specific country.

        Args:
            country_name: Name of the country
            country_scores: OKR scores dict for this country
            site_scores: DataFrame with site-level scores for this country

        Returns:
            Formatted markdown report string
        """
        report_lines = []
        report_lines.append(f"# Country Detail Report: {country_name}")
        report_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")

        report_lines.append(
            f"## Country OKR Score: {country_scores['okr_score']}/100 "
            f"{country_scores['status_icon']} {country_scores['status']}"
        )
        report_lines.append("")

        report_lines.append("### Key Results")
        report_lines.append(f"- KR1: {country_scores['kr1_score']:.1f}/100 ({country_scores['kr1_value']} devices)")
        report_lines.append(f"- KR2: {country_scores['kr2_score']:.1f}/100 ({country_scores['kr2_value']} devices)")
        report_lines.append(f"- KR3: {country_scores['kr3_score']:.1f}/100 ({country_scores['kr3_value']:.1f}%)")
        report_lines.append(f"- KR4: {country_scores['kr4_score']:.1f}/100 ({country_scores['kr4_value']} devices)")
        report_lines.append("")

        report_lines.append(f"## Sites in {country_name} ({len(site_scores)})")
        report_lines.append("")

        if len(site_scores) > 0:
            report_lines.append("| Site | Score | Status | Devices |")
            report_lines.append("|------|-------|--------|---------|")

            for _, row in site_scores.iterrows():
                report_lines.append(
                    f"| {row.get('Site Location', 'Unknown'):<20} | "
                    f"{row['okr_score']:>5.1f} | {row['status_icon']} {row['status']:<10} | "
                    f"{row['total_devices']:>7,} |"
                )

        return "\n".join(report_lines)
