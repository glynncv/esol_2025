import pandas as pd
import argparse
from pathlib import Path
from datetime import datetime
import sys

# Add the scripts directory to the path
sys.path.append(str(Path(__file__).parent))

from separated_esol_analyzer import ConfigManager
from data_utils import get_data_file_path, add_data_file_argument, validate_data_file

def main():
    """Analyze Kiosk EUC counts by category and export summary report."""
    parser = argparse.ArgumentParser(description='Analyze Kiosk EUC counts by category')
    add_data_file_argument(parser, 'Path to EUC_ESOL.xlsx file')
    parser.add_argument('--output', '-o', help='Output file for the report (optional - auto-saves to data/reports/ if not specified)')
    
    args = parser.parse_args()
    
    # Load configuration
    config_manager = ConfigManager()
    esol_config = config_manager.get_esol_criteria()
    kiosk_config = esol_config['kiosk_detection']
    data_mapping = esol_config['data_mapping']
    
    # Read the Excel file
    data_file = get_data_file_path(args.data_file)
    validate_data_file(data_file)
    df = pd.read_excel(data_file)
    
    # Filter for Kiosk EUCs based on YAML configuration
    device_name_col = data_mapping['device_name_column']
    user_loggedon_col = data_mapping['user_columns']['current']
    
    # Build kiosk detection patterns from config
    device_patterns = '|'.join(kiosk_config['device_name_patterns'])
    user_patterns = '|'.join(kiosk_config['user_loggedon_patterns'])
    
    kiosk_mask = (
        df[device_name_col].str.contains(device_patterns, case=not kiosk_config['case_sensitive'], na=False) |
        df[user_loggedon_col].str.contains(user_patterns, case=not kiosk_config['case_sensitive'], na=False)
    )
    kiosk_df = df[kiosk_mask]
    
    total_kiosk = len(kiosk_df)
    total_devices = len(df)
    
    # Calculate Enterprise and LTSC counts
    edition_col = data_mapping['edition_column']
    os_col = data_mapping['os_column']
    enterprise_count = (kiosk_df[edition_col] == 'Enterprise').sum()
    ltsc_count = (kiosk_df[edition_col] == 'LTSC').sum()
    
    # Calculate Windows 11 migration status for LTSC Kiosk machines
    ltsc_kiosk_df = kiosk_df[kiosk_df[edition_col] == 'LTSC']
    ltsc_kiosk_count = len(ltsc_kiosk_df)
    
    # Check for Windows 11 patterns
    win11_patterns = esol_config['windows11_compatibility']['win11_patterns']
    win11_pattern = '|'.join(win11_patterns)
    ltsc_not_win11_count = (~ltsc_kiosk_df[os_col].str.contains(win11_pattern, case=False, na=False)).sum()
    
    # Calculate percentages
    enterprise_pct = round((enterprise_count / total_kiosk) * 100, 2) if total_kiosk > 0 else 0
    ltsc_pct = round((ltsc_count / total_kiosk) * 100, 2) if total_kiosk > 0 else 0
    ltsc_not_win11_pct = round((ltsc_not_win11_count / ltsc_kiosk_count) * 100, 2) if ltsc_kiosk_count > 0 else 0
    
    # Generate report content
    report_lines = []
    report_lines.append(f"# Kiosk EUC Count Analysis - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    report_lines.append(f"**Total devices analyzed:** {total_devices:,}")
    report_lines.append(f"**Total Kiosk EUCs:** {total_kiosk:,}")
    report_lines.append("")
    report_lines.append("## Kiosk EUC Breakdown")
    report_lines.append(f"- **Total # of Kiosk EUCs:** {total_kiosk:,}")
    report_lines.append(f"- **Total # (%) of Kiosk EUCs that are Enterprise:** {enterprise_count:,} ({enterprise_pct}%)")
    report_lines.append(f"- **Total # (%) of Kiosk EUCs that are LTSC:** {ltsc_count:,} ({ltsc_pct}%)")
    report_lines.append("")
    report_lines.append("## LTSC Kiosk Windows 11 Migration Status")
    report_lines.append(f"- **Total # of LTSC Kiosk EUCs:** {ltsc_kiosk_count:,}")
    report_lines.append(f"- **Total # (%) of LTSC Kiosk EUCs not yet migrated to Windows 11:** {ltsc_not_win11_count:,} ({ltsc_not_win11_pct}%)")
    report_lines.append("")
    report_lines.append("**Note:** LTSC Kiosk devices are excluded from the 2025 Windows 11 push strategy.")
    report_lines.append("Only Enterprise Kiosk devices are targeted for Windows 11 migration.")
    
    # Print to console
    print(f"Total # of Kiosk EUCs: {total_kiosk:,}")
    print(f"Total # (%) of Kiosk EUCs that are Enterprise: {enterprise_count:,} ({enterprise_pct}%)")
    print(f"Total # (%) of Kiosk EUCs that are LTSC: {ltsc_count:,} ({ltsc_pct}%)")
    print(f"Total # (%) of LTSC Kiosk EUCs not yet migrated to Windows 11: {ltsc_not_win11_count:,} ({ltsc_not_win11_pct}%)")
    
    # Save report
    report_content = "\n".join(report_lines)
    
    if args.output:
        # User specified output path
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"📄 Report saved to {output_path}")
    else:
        # Auto-save to data/reports/ with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = Path('data/reports')
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = output_dir / f'Kiosk_Count_{timestamp}.md'
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"📄 Report auto-saved to {filename}")

if __name__ == "__main__":
    main()
