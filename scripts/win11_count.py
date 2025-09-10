import pandas as pd
import argparse
from pathlib import Path
from datetime import datetime
import sys

# Add the scripts directory to the path
sys.path.append(str(Path(__file__).parent))

from separated_esol_analyzer import ConfigManager

def main():
    """Analyze Windows 11 EUC counts focused on Enterprise devices and export summary report."""
    parser = argparse.ArgumentParser(description='Analyze Windows 11 EUC counts for Enterprise devices')
    parser.add_argument('--output', '-o', help='Output file for the report (optional - auto-saves to data/reports/ if not specified)')
    args = parser.parse_args()
    
    # Load configuration
    config_manager = ConfigManager()
    esol_config = config_manager.get_esol_criteria()
    win11_config = esol_config['windows11_compatibility']
    data_mapping = esol_config['data_mapping']
    
    # Read the Excel file
    df = pd.read_excel('data/raw/EUC_ESOL.xlsx')
    
    # Get column mappings
    os_col = data_mapping['os_column']
    edition_col = data_mapping['edition_column']
    action_col = data_mapping['action_column']
    
    # Filter for Enterprise EUCs only (the 2025 Windows 11 push target)
    enterprise_mask = df[edition_col] == 'Enterprise'
    enterprise_df = df[enterprise_mask]
    
    # Count Enterprise EUCs already on Windows 11
    win11_patterns = win11_config['win11_patterns']
    win11_pattern = '|'.join(win11_patterns)
    enterprise_win11_mask = enterprise_df[os_col].str.contains(win11_pattern, case=False, na=False)
    enterprise_win11_count = len(enterprise_df[enterprise_win11_mask])
    
    # Count Enterprise EUCs that will get Windows 11 via ESOL replacement
    migration_categories = win11_config['migration_categories']
    migration_actions = [esol_config['esol_categories'][cat]['action_value'] for cat in migration_categories]
    enterprise_esol_mask = enterprise_df[action_col].isin(migration_actions)
    enterprise_esol_count = len(enterprise_df[enterprise_esol_mask])
    
    # Calculate totals
    total_enterprise = len(enterprise_df)
    total_enterprise_win11_path = enterprise_win11_count + enterprise_esol_count
    win11_adoption_pct = round((total_enterprise_win11_path / total_enterprise) * 100, 2) if total_enterprise > 0 else 0
    current_win11_pct = round((enterprise_win11_count / total_enterprise) * 100, 2) if total_enterprise > 0 else 0
    
    # Generate report content
    report_content = f"""# Windows 11 EUC Analysis - Enterprise Focus - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Enterprise EUC Windows 11 Strategy
**Total Enterprise EUCs:** {total_enterprise:,}
**Enterprise EUCs already on Windows 11:** {enterprise_win11_count:,} ({current_win11_pct}%)
**Enterprise EUCs getting Windows 11 via ESOL replacement:** {enterprise_esol_count:,}
**Total Enterprise Windows 11 adoption path:** {total_enterprise_win11_path:,} ({win11_adoption_pct}%)

## Summary
- **Current Windows 11 adoption:** {current_win11_pct}% of Enterprise EUCs
- **Projected Windows 11 adoption:** {win11_adoption_pct}% of Enterprise EUCs (via replacement + upgrade)
- **LTSC devices excluded:** Not part of 2025 Windows 11 push strategy"""
    
    # Print to console
    print(f"Total Enterprise EUCs: {total_enterprise:,}")
    print(f"Enterprise EUCs already on Windows 11: {enterprise_win11_count:,} ({current_win11_pct}%)")
    print(f"Enterprise EUCs getting Windows 11 via ESOL replacement: {enterprise_esol_count:,}")
    print(f"Total Enterprise Windows 11 adoption path: {total_enterprise_win11_path:,} ({win11_adoption_pct}%)")
    
    # Save report
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(report_content, encoding='utf-8')
        print(f"📄 Report saved to {args.output}")
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = Path('data/reports')
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = output_dir / f'Win11_Count_{timestamp}.md'
        filename.write_text(report_content, encoding='utf-8')
        print(f"📄 Report auto-saved to {filename}")

if __name__ == "__main__":
    main()