#!/usr/bin/env python3
"""
Technical Debt Remediation OKR Tracker Generator
Analyzes EUC_ESOL.xlsx and generates comprehensive multi-level OKR report with historical trends

Generates OKR analysis at multiple organizational levels:
- Overall organization-wide scores
- Breakdown by country
- Breakdown by SDM (Service Delivery Manager)
- Breakdown by site location

NEW Features (Foundation-First Enhancement):
- Historical snapshot tracking (auto-saved to data/history/)
- Week-over-week trend analysis with visual indicators (↑↓→)
- Burndown velocity calculations across all KRs
- Excel export with historical trends sheets
- Projection forecasting for KR completion dates

Requirements:
    pip install pandas openpyxl pyyaml

Usage:
    python okr_tracker.py [--data-file EUC_ESOL.xlsx] [--output okr_report.md] [--excel]
    python okr_tracker.py [--data-file EUC_ESOL.xlsx] [--console] [--level country|sdm|site]
"""

import pandas as pd
import json
import argparse
import sys
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

# Import shared data utilities
from data_utils import get_data_file_path, add_data_file_argument, validate_data_file

# Import new ETL modules
from separated_esol_analyzer import ConfigManager
from etl.load_data import DataLoader
from etl.analysis import ESOLAnalyzer, Win11Analyzer, KioskAnalyzer, OKRAggregator
from etl.analysis.historical_store import HistoricalDataStore
from etl.analysis.trend_analyzer import TrendAnalyzer
from etl.presentation import OKRFormatter
from etl.presentation.file_exporter import FileExporter



def main():
    """Main function with command line interface for multi-level OKR analysis"""
    parser = argparse.ArgumentParser(
        description='Generate Multi-Level Technical Debt Remediation OKR Tracker',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    add_data_file_argument(parser, 'Path to EUC_ESOL.xlsx file')
    parser.add_argument('--output', '-o',
                       help='Output markdown file (auto-saves to data/reports/ if not specified)')
    parser.add_argument('--console', '-c', action='store_true',
                       help='Print console summary instead of generating markdown report')
    parser.add_argument('--level', '-l', choices=['country', 'sdm', 'site', 'all'],
                       default='all',
                       help='Organizational level for analysis (default: all)')
    parser.add_argument('--excel', '-x', action='store_true',
                       help='Also export results to Excel format with historical trends')
    parser.add_argument('--excel-output',
                       help='Custom path for Excel export (requires --excel)')

    args = parser.parse_args()

    try:
        print("=" * 80)
        print("MULTI-LEVEL OKR TRACKER")
        print("=" * 80)
        print()

        # Phase 1: Load and enrich data
        print("[1/4] Loading and enriching data...")
        data_file = get_data_file_path(args.data_file)
        validate_data_file(data_file)

        # Initialize ConfigManager and DataLoader
        # Find project root (go up from scripts/ to project root)
        project_root = Path(__file__).resolve().parent.parent
        config_path = str(project_root / 'config')
        config_manager = ConfigManager(config_path=config_path)
        loader = DataLoader(config_manager)
        df = loader.load_raw_data(data_file)
        df_enriched = loader.enrich_with_location_data(df)

        # Print enrichment summary
        enrichment_summary = loader.get_site_enrichment_summary()
        # Calculate enrichment stats from enriched DataFrame
        total_sites = df_enriched[loader.site_col].nunique()
        mapped_sites = df_enriched[df_enriched['Country'] != 'Unknown']['Country'].count() > 0
        unique_countries = df_enriched['Country'].nunique()
        unique_sdms = df_enriched['SDM'].nunique()
        mapped_count = len(df_enriched[df_enriched['Country'] != 'Unknown'])
        mapping_rate = (mapped_count / len(df_enriched)) * 100 if len(df_enriched) > 0 else 0
        
        print(f"  ✓ Loaded {len(df):,} devices")
        print(f"  ✓ Enriched with location data:")
        print(f"    - {total_sites} sites")
        print(f"    - {mapped_count:,} devices mapped ({mapping_rate:.1f}%)")
        print(f"    - {unique_countries} countries")
        print(f"    - {unique_sdms} SDMs")
        print()

        # Phase 2: Run analyzers
        print("[2/4] Calculating OKR metrics at all levels...")
        esol_analyzer = ESOLAnalyzer(config_manager)
        win11_analyzer = Win11Analyzer(config_manager)
        kiosk_analyzer = KioskAnalyzer(config_manager)
        okr_aggregator = OKRAggregator(config_manager)

        # Calculate overall scores
        esol_counts = esol_analyzer.calculate_esol_counts(df_enriched)
        # Filter for Enterprise devices for Win11 analysis
        enterprise_df = loader.filter_enterprise_devices(df_enriched)
        win11_counts = win11_analyzer.calculate_win11_counts(enterprise_df)
        # Filter for kiosk devices
        kiosk_df = loader.filter_kiosk_devices(df_enriched)
        kiosk_counts = kiosk_analyzer.calculate_kiosk_counts(kiosk_df, len(df_enriched))
        overall_scores = okr_aggregator.calculate_okr_scores(esol_counts, win11_counts, kiosk_counts)

        print(f"  ✓ Overall OKR Score: {overall_scores['okr_score']:.1f}/100 {overall_scores['status_icon']}")
        print()

        # Phase 3: Calculate multi-level aggregations
        print("[3/4] Aggregating by organizational levels...")
        country_scores = pd.DataFrame()
        sdm_scores = pd.DataFrame()
        site_scores = pd.DataFrame()

        if args.level in ['country', 'all']:
            country_scores = okr_aggregator.aggregate_by_country(
                df_enriched, esol_analyzer, win11_analyzer, kiosk_analyzer,
                loader.edition_col, loader
            )
            print(f"  ✓ Calculated scores for {len(country_scores)} countries")

        if args.level in ['sdm', 'all']:
            sdm_scores = okr_aggregator.aggregate_by_sdm(
                df_enriched, esol_analyzer, win11_analyzer, kiosk_analyzer,
                loader.edition_col, loader
            )
            print(f"  ✓ Calculated scores for {len(sdm_scores)} SDMs")

        if args.level in ['site', 'all']:
            site_scores = okr_aggregator.aggregate_by_site(
                df_enriched, loader.site_col, esol_analyzer, win11_analyzer, kiosk_analyzer,
                loader.edition_col, loader
            )
            print(f"  ✓ Calculated scores for {len(site_scores)} sites")
        print()

        # Phase 3.5: Historical tracking and trend analysis
        print("[3.5/4] Analyzing trends and saving historical snapshot...")
        historical_store = HistoricalDataStore()

        # Add timestamp to overall_scores for historical tracking
        overall_scores['timestamp'] = datetime.now().isoformat()

        # Get previous snapshot for trend calculation
        previous_snapshot = historical_store.get_previous_snapshot(days_back=7)
        all_snapshots = historical_store.get_all_snapshots()

        # Calculate trends
        trend_data = None
        burndown_trends = None

        if previous_snapshot:
            trend_data = TrendAnalyzer.calculate_overall_trends(
                overall_scores, previous_snapshot['overall_scores']
            )
            # Only calculate trends for requested levels
            if args.level in ['country', 'all'] and len(country_scores) > 0:
                country_scores = TrendAnalyzer.calculate_country_trends(
                    country_scores, previous_snapshot['country_scores_df']
                )
            if args.level in ['sdm', 'all'] and len(sdm_scores) > 0:
                sdm_scores = TrendAnalyzer.calculate_sdm_trends(
                    sdm_scores, previous_snapshot['sdm_scores_df']
                )
            print(f"  ✓ Calculated trends vs {trend_data['days_since_previous']} days ago")
        else:
            print(f"  ℹ No previous snapshot found - this is the first run")

        # Calculate burndown trends if sufficient history
        if len(all_snapshots) >= 2:
            burndown_trends = TrendAnalyzer.calculate_burndown_trends(all_snapshots)
            print(f"  ✓ Calculated burndown velocity from {len(all_snapshots)} snapshots")

        # Save current snapshot
        snapshot_path = historical_store.save_snapshot(
            overall_scores, country_scores, sdm_scores, site_scores
        )
        print(f"  ✓ Saved snapshot to: {snapshot_path}")
        print()

        # Phase 4: Generate output
        print("[4/4] Generating output...")

        if args.console:
            # Console summary output
            console_output = OKRFormatter.format_console_summary(
                overall_scores, country_scores, sdm_scores
            )
            print()
            print(console_output)

        else:
            # Generate comprehensive markdown report with trends
            report = OKRFormatter.format_executive_dashboard(
                overall_scores, country_scores, sdm_scores, site_scores,
                trend_data=trend_data, burndown_trends=burndown_trends
            )

            # Save markdown report
            if args.output:
                output_path = Path(args.output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
            else:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_dir = project_root / 'data' / 'reports'
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = output_dir / f'OKR_Executive_Dashboard_{timestamp}.md'

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)

            print(f"  ✓ Executive dashboard saved to: {output_path}")

            # Export to Excel if requested
            if args.excel:
                excel_path = FileExporter.export_okr_to_excel(
                    overall_scores, country_scores, sdm_scores, site_scores,
                    historical_snapshots=all_snapshots,
                    output_path=args.excel_output
                )
                print(f"  ✓ Excel export saved to: {excel_path}")

            print()

            # Print summary
            print("=" * 80)
            print("SUMMARY")
            print("=" * 80)
            print(f"Overall Score:     {overall_scores['okr_score']:.1f}/100 {overall_scores['status_icon']} {overall_scores['status']}")
            print(f"Total Devices:     {overall_scores['total_devices']:,}")
            print(f"Countries:         {len(country_scores)}")
            print(f"SDMs:              {len(sdm_scores)}")
            print(f"Sites:             {len(site_scores)}")
            print()
            print("Key Results:")
            print(f"  KR1 (ESOL 2024):  {overall_scores['kr1_score']:.1f}/100 ({overall_scores['kr1_value']} devices)")
            print(f"  KR2 (ESOL 2025):  {overall_scores['kr2_score']:.1f}/100 ({overall_scores['kr2_value']} devices)")
            print(f"  KR3 (Win11):      {overall_scores['kr3_score']:.1f}/100 ({overall_scores['kr3_value']:.1f}%)")
            print(f"  KR4 (Kiosk):      {overall_scores['kr4_score']:.1f}/100 ({overall_scores['kr4_value']} devices)")
            print("=" * 80)

    except KeyboardInterrupt:
        print("\n[STOP] Generation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()


# Example usage:
"""
# Basic usage - generates comprehensive executive dashboard with historical tracking
python okr_tracker.py

# With custom data file
python okr_tracker.py --data-file path/to/EUC_ESOL.xlsx

# Console summary output (no file generation)
python okr_tracker.py --console

# Export to Excel format with historical trends
python okr_tracker.py --excel

# Focus on specific organizational level
python okr_tracker.py --level country
python okr_tracker.py --level sdm
python okr_tracker.py --level site

# With custom output files
python okr_tracker.py --output data/reports/monthly_okr_dashboard.md
python okr_tracker.py --excel --excel-output data/reports/okr_dashboard.xlsx

# Full example with all options
python okr_tracker.py \
    --data-file data/raw/EUC_ESOL.xlsx \
    --output "data/reports/OKR_Dashboard_$(date +%Y%m%d).md" \
    --excel \
    --level all

# Historical tracking features:
# - Automatically saves snapshots to data/history/
# - Shows week-over-week trends with arrows (↑↓→)
# - Calculates burndown velocity across all KRs
# - Displays historical comparison in reports
# - Exports historical trends to Excel sheets
"""