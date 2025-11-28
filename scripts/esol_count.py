import pandas as pd
import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add the scripts directory to the path
sys.path.append(str(Path(__file__).parent))

from separated_esol_analyzer import ConfigManager
from data_utils import add_data_file_argument
from etl.load_data import DataLoader
from etl.analysis import ESOLAnalyzer, BurndownCalculator
from etl.presentation import ESOLFormatter, BurndownFormatter, FileExporter

def main():
    """Analyze ESOL device counts by category and optionally export site summary table."""
    parser = argparse.ArgumentParser(description='Analyze ESOL device counts by category')
    add_data_file_argument(parser, 'Path to EUC_ESOL.xlsx file')
    parser.add_argument('--category', choices=['esol_2024', 'esol_2025', 'esol_2026', 'all'],
                         default='all', help='ESOL category to analyze (default: all)')
    parser.add_argument('--output', '-o', help='Output file for the report (optional - auto-saves to data/reports/ if not specified)')
    parser.add_argument('--site-table', action='store_true', help='Export ESOL devices and cost by site')
    parser.add_argument('--burndown', action='store_true', help='Generate ESOL replacement burndown report')

    args = parser.parse_args()

    # Load configuration and data using centralized loader
    # Find project root (go up from scripts/ to project root)
    project_root = Path(__file__).resolve().parent.parent
    config_path = str(project_root / 'config')
    config_manager = ConfigManager(config_path=config_path)
    loader = DataLoader(config_manager)
    esol_analyzer = ESOLAnalyzer(config_manager)
    burndown_calc = BurndownCalculator(config_manager)

    # Load raw data
    df = loader.load_raw_data(args.data_file)

    # Calculate ESOL counts and percentages using centralized analyzer (needed for burndown and regular reports)
    counts = esol_analyzer.calculate_esol_counts(df)
    percentages = esol_analyzer.calculate_esol_percentages(counts)

    if args.site_table:
        # Generate site summary table using centralized analyzer
        esol_df = loader.filter_esol_devices(df, categories=['2024', '2025', '2026'])
        site_data = esol_analyzer.generate_site_summary(esol_df)

        # Export using centralized method
        csv_file, json_file = esol_analyzer.export_site_summary(site_data)

        # Display using presentation formatter
        print(ESOLFormatter.format_site_summary_console(site_data))
        print(f"\nSite table exported to:")
        print(f"   CSV: {csv_file}")
        print(f"   JSON: {json_file}")
        print()
        
        # If only site-table was requested (no burndown), exit early
        if not args.burndown:
            return

    print(f"Total devices: {counts['total_devices']}")

    # Generate report content using presentation formatter
    report_content = ESOLFormatter.format_markdown_report(counts, percentages, args.category)

    # Console output using presentation formatter
    console_output = ESOLFormatter.format_console_summary(counts, percentages, args.category)
    print(console_output)
    
    # ESOL Burndown analysis if requested
    if args.burndown:
        # Calculate burndown using centralized calculator
        burndown_data = burndown_calc.calculate_esol_burndown(
            counts['esol_2024'],
            counts['esol_2025'],
            counts['esol_2026']
        )

        # Export burndown data using centralized method
        burndown_json, burndown_csv = burndown_calc.export_burndown_data(burndown_data, 'esol')

        # Generate burndown report using presentation formatter
        burndown_report_content = BurndownFormatter.format_esol_markdown_report(burndown_data)

        # Save burndown report using file exporter
        burndown_report_file = FileExporter.save_report(
            burndown_report_content,
            auto_prefix='ESOL_Burndown'
        )

        # Print burndown summary to console using presentation formatter
        console_summary = BurndownFormatter.format_esol_console_summary(burndown_data)
        print(console_summary)

        print(f"📊 Burndown data exported to:")
        print(f"   JSON: {burndown_json}")
        print(f"   CSV: {burndown_csv}")
        print(f"   Report: {burndown_report_file}")
        print()
    
    # Save report using file exporter
    saved_file = FileExporter.save_report(
        report_content,
        output_path=args.output,
        auto_prefix='ESOL_Count',
        auto_suffix=args.category
    )

    if args.output:
        print(f"Report saved to {saved_file}")
    else:
        print(f"Report auto-saved to {saved_file}")

if __name__ == "__main__":
    main() 