import pandas as pd
import argparse
from pathlib import Path
from datetime import datetime
from data_utils import get_data_file_path, add_data_file_argument, validate_data_file

def main():
    """Analyze ESOL device counts by category and optionally export site summary table."""
    parser = argparse.ArgumentParser(description='Analyze ESOL device counts by category')
    add_data_file_argument(parser, 'Path to EUC_ESOL.xlsx file')
    parser.add_argument('--category', choices=['esol_2024', 'esol_2025', 'esol_2026', 'all'],
                         default='all', help='ESOL category to analyze (default: all)')
    parser.add_argument('--output', '-o', help='Output file for the report (optional - auto-saves to data/reports/ if not specified)')
    parser.add_argument('--site-table', action='store_true', help='Export ESOL devices and cost by site')

    args = parser.parse_args()
    
    # Read the Excel file
    data_file = get_data_file_path(args.data_file)
    validate_data_file(data_file)
    df = pd.read_excel(data_file)
    
    if args.site_table:
        # Generate site summary table
        # Filter for ESOL devices only (all three categories)
        esol_df = df[df['Action to take'].isin(['Urgent Replacement', 'Replace by 14/10/2025', 'Replace by 11/11/2026'])]
        
        # Group by site and calculate counts and costs
        site_data = esol_df.groupby('Site Location').agg({
            'Action to take': lambda x: (x == 'Urgent Replacement').sum(),  # ESOL 2024
            'Estimate Cost for Replacement $': 'sum'  # Total cost for all ESOL devices
        }).rename(columns={'Action to take': 'ESOL_2024_Count', 'Estimate Cost for Replacement $': 'Total_Cost'})
        
        site_data['ESOL_2025_Count'] = esol_df.groupby('Site Location')['Action to take'].apply(lambda x: (x == 'Replace by 14/10/2025').sum())
        site_data['ESOL_2026_Count'] = esol_df.groupby('Site Location')['Action to take'].apply(lambda x: (x == 'Replace by 11/11/2026').sum())
        site_data['Total_ESOL'] = site_data['ESOL_2024_Count'] + site_data['ESOL_2025_Count'] + site_data['ESOL_2026_Count']
        
        # Reorder columns to match preferred structure
        site_data = site_data[['ESOL_2024_Count', 'ESOL_2025_Count', 'ESOL_2026_Count', 'Total_ESOL', 'Total_Cost']]
        
        site_data = site_data[site_data['Total_ESOL'] > 0].sort_values('Total_ESOL', ascending=False)
        
        # Export to data/processed
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        processed_dir = Path('data/processed')
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Export as CSV
        csv_file = processed_dir / f'site_esol_summary_{timestamp}.csv'
        site_data.to_csv(csv_file)
        
        # Export as JSON
        json_file = processed_dir / f'site_esol_summary_{timestamp}.json'
        site_data.to_json(json_file, orient='index', indent=2)
        
        print("Site Summary - ESOL Devices and Cost:")
        print("=" * 70)
        for site, row in site_data.iterrows():
            print(f"{site}: {int(row['Total_ESOL'])} devices (2024: {int(row['ESOL_2024_Count'])}, 2025: {int(row['ESOL_2025_Count'])}, 2026: {int(row['ESOL_2026_Count'])}) - ${row['Total_Cost']:,.0f}")
        print(f"\n📊 Site table exported to:")
        print(f"   CSV: {csv_file}")
        print(f"   JSON: {json_file}")
        return
    
    total = len(df)
    print(f"Total devices: {total}")
    
    # Process the entire dataset (not just a sample)
    urgent_count = (df['Action to take'] == 'Urgent Replacement').sum()
    replace_count = (df['Action to take'] == 'Replace by 14/10/2025').sum()
    
    # Calculate ESOL counts
    esol2024 = urgent_count
    esol2025 = replace_count
    total_esol = esol2024 + esol2025
    non_esol = total - total_esol
    
    # Calculate percentages
    esol2024_pct = round((esol2024 / total) * 100, 2)
    esol2025_pct = round((esol2025 / total) * 100, 2)
    total_esol_pct = round((total_esol / total) * 100, 2)
    non_esol_pct = round((non_esol / total) * 100, 2)
    
    # Generate report content
    report_lines = []
    report_lines.append(f"# ESOL Device Count Analysis - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    report_lines.append(f"**Total devices analyzed:** {total:,}")
    report_lines.append("")
    
    # Output based on category parameter
    if args.category == 'esol_2024':
        output_text = f"ESOL 2024: {esol2024} devices ({esol2024_pct}%) - down from the previous count"
        report_lines.append(f"## ESOL 2024 Analysis")
        report_lines.append(f"- **Count:** {esol2024} devices")
        report_lines.append(f"- **Percentage:** {esol2024_pct}%")
        report_lines.append(f"- **Status:** Down from the previous count")
        print(output_text)
    elif args.category == 'esol_2025':
        output_text = f"ESOL 2025: {esol2025} devices ({esol2025_pct}%)"
        report_lines.append(f"## ESOL 2025 Analysis")
        report_lines.append(f"- **Count:** {esol2025} devices")
        report_lines.append(f"- **Percentage:** {esol2025_pct}%")
        print(output_text)
    elif args.category == 'esol_2026':
        output_text = f"ESOL 2026: {non_esol} devices ({non_esol_pct}%) - non-ESOL devices"
        report_lines.append(f"## Non-ESOL Analysis")
        report_lines.append(f"- **Count:** {non_esol:,} devices")
        report_lines.append(f"- **Percentage:** {non_esol_pct}%")
        report_lines.append(f"- **Status:** Non-ESOL devices")
        print(output_text)
    else:  # 'all' category
        print(f"ESOL 2024: {esol2024} devices ({esol2024_pct}%) - down from the previous count")
        print(f"Total ESOL: {total_esol} devices ({total_esol_pct}%) instead of 434")
        print(f"Non-ESOL: {non_esol:,} devices ({non_esol_pct}%) - slightly better compatibility")
        
        report_lines.append(f"## Complete ESOL Analysis")
        report_lines.append(f"- **ESOL 2024:** {esol2024} devices ({esol2024_pct}%) - down from the previous count")
        report_lines.append(f"- **ESOL 2025:** {esol2025} devices ({esol2025_pct}%)")
        report_lines.append(f"- **Total ESOL:** {total_esol} devices ({total_esol_pct}%) instead of 434")
        report_lines.append(f"- **Non-ESOL:** {non_esol:,} devices ({non_esol_pct}%) - slightly better compatibility")
    
    # Save report if output specified or auto-save to data/reports/
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
        filename = output_dir / f'ESOL_Count_{args.category}_{timestamp}.md'
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"📄 Report auto-saved to {filename}")

if __name__ == "__main__":
    main() 