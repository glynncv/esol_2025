import pandas as pd
import argparse
from pathlib import Path
from datetime import datetime
import sys

# Add the scripts directory to the path
sys.path.append(str(Path(__file__).parent))

from separated_esol_analyzer import ConfigManager
from data_utils import add_data_file_argument
from etl.load_data import DataLoader
from etl.analysis import Win11Analyzer, BurndownCalculator
from etl.presentation import Win11Formatter, BurndownFormatter, FileExporter

def main():
    """Analyze Windows 11 EUC counts focused on Enterprise devices and export summary report."""
    parser = argparse.ArgumentParser(description='Analyze Windows 11 EUC counts for Enterprise devices')
    add_data_file_argument(parser, 'Path to EUC_ESOL.xlsx file')
    parser.add_argument('--output', '-o', help='Output file for the report (optional - auto-saves to data/reports/ if not specified)')
    parser.add_argument('--site-table', action='store_true', help='Generate site-level breakdown table of Windows 11 migration workload')
    parser.add_argument('--burndown', action='store_true', help='Generate Windows 11 upgrade burndown report')
    args = parser.parse_args()
    
    # Load configuration and data using centralized loader
    # Find project root (go up from scripts/ to project root)
    project_root = Path(__file__).resolve().parent.parent
    config_path = str(project_root / 'config')
    config_manager = ConfigManager(config_path=config_path)
    loader = DataLoader(config_manager)
    win11_analyzer = Win11Analyzer(config_manager)
    burndown_calc = BurndownCalculator(config_manager)

    # Load raw data
    df = loader.load_raw_data(args.data_file)

    # Filter for Enterprise EUCs only using centralized loader
    enterprise_df = loader.filter_enterprise_devices(df, exclude_esol=False)

    # Calculate Win11 counts using centralized analyzer
    counts = win11_analyzer.calculate_win11_counts(enterprise_df)
    
    # Site-level analysis if requested
    if args.site_table:
        # Generate site summary using centralized analyzer
        site_data = win11_analyzer.generate_site_summary(enterprise_df)

        # Export using centralized method
        csv_file, json_file = win11_analyzer.export_site_summary(site_data)

        # Display using presentation formatter
        print(Win11Formatter.format_site_summary_console(site_data))

        print(f"\n📊 Site breakdown exported to:")
        print(f"   CSV: {csv_file}")
        print(f"   JSON: {json_file}")
        print()
    
    # Burndown analysis if requested
    if args.burndown:
        # Calculate eligible devices (Enterprise excluding ESOL replacements)
        total_eligible = counts['total_enterprise'] - counts['enterprise_esol_count']
        completed_count = counts['enterprise_win11_count']

        # Calculate burndown using centralized calculator
        burndown_data = burndown_calc.calculate_win11_burndown(total_eligible, completed_count)

        # Export burndown data using centralized method
        burndown_json, burndown_csv = burndown_calc.export_burndown_data(burndown_data, 'win11')

        # Generate burndown report using presentation formatter
        burndown_report = BurndownFormatter.format_win11_markdown_report(burndown_data)

        # Save burndown report using file exporter
        burndown_report_file = FileExporter.save_report(
            burndown_report,
            auto_prefix='Win11_Burndown'
        )

        # Print burndown summary to console using presentation formatter
        console_summary = BurndownFormatter.format_win11_console_summary(burndown_data)
        print(console_summary)
        print(f"\n📊 Burndown data exported to:")
        print(f"   JSON: {burndown_json}")
        print(f"   CSV: {burndown_csv}")
        print(f"   Report: {burndown_report_file}")
        print()

    # Calculate KPI metrics using centralized analyzer
    kpi_metrics = win11_analyzer.calculate_kpi_metrics(counts)

    # Generate report content using presentation formatter with KPI data
    report_content = Win11Formatter.format_markdown_report(counts, kpi_data=kpi_metrics)

    # Print to console using presentation formatter
    console_output = Win11Formatter.format_console_summary(
        counts,
        kpi_metrics['total_eligible'],
        kpi_metrics['upgraded_pct'],
        kpi_metrics['pending_count']
    )
    print(console_output)

    # Save report using file exporter
    saved_file = FileExporter.save_report(
        report_content,
        output_path=args.output,
        auto_prefix='Win11_Count'
    )

    if args.output:
        print(f"📄 Report saved to {saved_file}")
    else:
        print(f"📄 Report auto-saved to {saved_file}")

if __name__ == "__main__":
    main()