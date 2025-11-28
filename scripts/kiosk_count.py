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
from etl.analysis import KioskAnalyzer
from etl.presentation import KioskFormatter, FileExporter

def main():
    """Analyze Kiosk EUC counts by category and export summary report."""
    parser = argparse.ArgumentParser(description='Analyze Kiosk EUC counts by category')
    add_data_file_argument(parser, 'Path to EUC_ESOL.xlsx file')
    parser.add_argument('--output', '-o', help='Output file for the report (optional - auto-saves to data/reports/ if not specified)')
    
    args = parser.parse_args()
    
    # Load configuration and data using centralized loader
    # Find project root (go up from scripts/ to project root)
    project_root = Path(__file__).resolve().parent.parent
    config_path = str(project_root / 'config')
    config_manager = ConfigManager(config_path=config_path)
    loader = DataLoader(config_manager)
    kiosk_analyzer = KioskAnalyzer(config_manager)

    # Load raw data
    df = loader.load_raw_data(args.data_file)

    # Filter for Kiosk EUCs using centralized loader
    kiosk_df = loader.filter_kiosk_devices(df)
    total_devices = len(df)

    # Calculate kiosk counts using centralized analyzer
    counts = kiosk_analyzer.calculate_kiosk_counts(kiosk_df, total_devices)

    # Calculate LTSC Win11 migration status using centralized analyzer
    ltsc_migration = kiosk_analyzer.calculate_ltsc_win11_migration(kiosk_df)

    # Generate report content using presentation formatter
    report_content = KioskFormatter.format_markdown_report(counts, ltsc_migration)

    # Print to console using presentation formatter
    console_output = KioskFormatter.format_console_summary(counts, ltsc_migration)
    print(console_output)

    # Save report using file exporter
    saved_file = FileExporter.save_report(
        report_content,
        output_path=args.output,
        auto_prefix='Kiosk_Count'
    )

    if args.output:
        print(f"📄 Report saved to {saved_file}")
    else:
        print(f"📄 Report auto-saved to {saved_file}")

if __name__ == "__main__":
    main()
