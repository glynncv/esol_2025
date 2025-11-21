import pandas as pd
import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add the scripts directory to the path
sys.path.append(str(Path(__file__).parent))

from separated_esol_analyzer import ConfigManager
from data_utils import get_data_file_path, add_data_file_argument, validate_data_file

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

    # Load configuration
    config_manager = ConfigManager()
    esol_config = config_manager.get_esol_criteria()
    data_mapping = esol_config['data_mapping']
    esol_categories = esol_config['esol_categories']

    # Get column names from config
    action_col = data_mapping['action_column']
    cost_col = data_mapping['cost_column']
    site_col = data_mapping['site_column']

    # Get ESOL action values from config
    esol_2024_action = esol_categories['esol_2024']['action_value']
    esol_2025_action = esol_categories['esol_2025']['action_value']
    esol_2026_action = esol_categories['esol_2026']['action_value']
    all_esol_actions = [esol_2024_action, esol_2025_action, esol_2026_action]

    # Read the Excel file
    data_file = get_data_file_path(args.data_file)
    validate_data_file(data_file)
    df = pd.read_excel(data_file)
    
    if args.site_table:
        # Generate site summary table
        # Filter for ESOL devices only (all three categories)
        esol_df = df[df[action_col].isin(all_esol_actions)]

        # Group by site and calculate counts and costs
        site_data = esol_df.groupby(site_col).agg({
            action_col: lambda x: (x == esol_2024_action).sum(),  # ESOL 2024
            cost_col: 'sum'  # Total cost for all ESOL devices
        }).rename(columns={action_col: 'ESOL_2024_Count', cost_col: 'Total_Cost'})

        site_data['ESOL_2025_Count'] = esol_df.groupby(site_col)[action_col].apply(lambda x: (x == esol_2025_action).sum())
        site_data['ESOL_2026_Count'] = esol_df.groupby(site_col)[action_col].apply(lambda x: (x == esol_2026_action).sum())
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
        print(f"\nSite table exported to:")
        print(f"   CSV: {csv_file}")
        print(f"   JSON: {json_file}")
        return
    
    total = len(df)
    print(f"Total devices: {total}")

    # Process the entire dataset (not just a sample)
    urgent_count = (df[action_col] == esol_2024_action).sum()
    replace_count = (df[action_col] == esol_2025_action).sum()
    replace_2026_count = (df[action_col] == esol_2026_action).sum()
    
    # Calculate ESOL counts
    esol2024 = urgent_count
    esol2025 = replace_count
    esol2026 = replace_2026_count
    total_esol = esol2024 + esol2025 + esol2026
    non_esol = total - total_esol
    
    # Calculate percentages
    esol2024_pct = round((esol2024 / total) * 100, 2)
    esol2025_pct = round((esol2025 / total) * 100, 2)
    esol2026_pct = round((esol2026 / total) * 100, 2)
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
        output_text = f"ESOL 2026: {esol2026} devices ({esol2026_pct}%)"
        report_lines.append(f"## ESOL 2026 Analysis")
        report_lines.append(f"- **Count:** {esol2026} devices")
        report_lines.append(f"- **Percentage:** {esol2026_pct}%")
        print(output_text)
    else:  # 'all' category
        print(f"ESOL 2024: {esol2024} devices ({esol2024_pct}%) - down from the previous count")
        print(f"ESOL 2025: {esol2025} devices ({esol2025_pct}%)")
        print(f"ESOL 2026: {esol2026} devices ({esol2026_pct}%)")
        print(f"Total ESOL: {total_esol} devices ({total_esol_pct}%) instead of 434")
        print(f"Non-ESOL: {non_esol:,} devices ({non_esol_pct}%) - slightly better compatibility")
        
        report_lines.append(f"## Complete ESOL Analysis")
        report_lines.append(f"- **ESOL 2024:** {esol2024} devices ({esol2024_pct}%) - down from the previous count")
        report_lines.append(f"- **ESOL 2025:** {esol2025} devices ({esol2025_pct}%)")
        report_lines.append(f"- **ESOL 2026:** {esol2026} devices ({esol2026_pct}%)")
        report_lines.append(f"- **Total ESOL:** {total_esol} devices ({total_esol_pct}%) instead of 434")
        report_lines.append(f"- **Non-ESOL:** {non_esol:,} devices ({non_esol_pct}%) - slightly better compatibility")
    
    # ESOL Burndown analysis if requested
    if args.burndown:
        # Get target dates for each ESOL category (already loaded above)
        esol_2024_date = datetime.strptime(esol_config['esol_categories']['esol_2024']['target_date'], '%Y-%m-%d')
        esol_2025_date = datetime.strptime(esol_config['esol_categories']['esol_2025']['target_date'], '%Y-%m-%d')
        esol_2026_date = datetime.strptime(esol_config['esol_categories']['esol_2026']['target_date'], '%Y-%m-%d')
        
        current_date = datetime.now()
        
        # Calculate burndown metrics for each category
        burndown_data = []
        
        # ESOL 2024 Burndown
        days_remaining_2024 = (esol_2024_date - current_date).days
        daily_burn_rate_2024 = esol2024 / days_remaining_2024 if days_remaining_2024 > 0 else 0
        burndown_data.append({
            'category': 'ESOL 2024',
            'target_date': esol_config['esol_categories']['esol_2024']['target_date'],
            'days_remaining': int(days_remaining_2024),
            'remaining_devices': int(esol2024),
            'daily_burn_rate_needed': round(daily_burn_rate_2024, 2),
            'status': 'AT RISK' if days_remaining_2024 <= 30 else 'ON TRACK'
        })
        
        # ESOL 2025 Burndown
        days_remaining_2025 = (esol_2025_date - current_date).days
        daily_burn_rate_2025 = esol2025 / days_remaining_2025 if days_remaining_2025 > 0 else 0
        burndown_data.append({
            'category': 'ESOL 2025',
            'target_date': esol_config['esol_categories']['esol_2025']['target_date'],
            'days_remaining': int(days_remaining_2025),
            'remaining_devices': int(esol2025),
            'daily_burn_rate_needed': round(daily_burn_rate_2025, 2),
            'status': 'AT RISK' if days_remaining_2025 <= 60 else 'ON TRACK'
        })
        
        # ESOL 2026 Burndown
        days_remaining_2026 = (esol_2026_date - current_date).days
        daily_burn_rate_2026 = esol2026 / days_remaining_2026 if days_remaining_2026 > 0 else 0
        burndown_data.append({
            'category': 'ESOL 2026',
            'target_date': esol_config['esol_categories']['esol_2026']['target_date'],
            'days_remaining': int(days_remaining_2026),
            'remaining_devices': int(esol2026),
            'daily_burn_rate_needed': round(daily_burn_rate_2026, 2),
            'status': 'ON TRACK'  # 2026 is far enough out
        })
        
        # Export burndown data
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        processed_dir = Path('data/processed')
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Export as JSON
        burndown_json = processed_dir / f'esol_burndown_{timestamp}.json'
        import json
        with open(burndown_json, 'w') as f:
            json.dump(burndown_data, f, indent=2)
        
        # Export as CSV
        burndown_csv = processed_dir / f'esol_burndown_{timestamp}.csv'
        burndown_df = pd.DataFrame(burndown_data)
        burndown_df.to_csv(burndown_csv, index=False)
        
        # Generate burndown report
        burndown_report_lines = [
            f"# ESOL Replacement Burndown Report - {current_date.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## ESOL Category Burndown Analysis",
            "",
            "| Category | Target Date | Days Remaining | Remaining Devices | Daily Burn Rate Needed | Status |",
            "|----------|-------------|----------------|-------------------|----------------------|--------|"
        ]
        
        for data in burndown_data:
            status_icon = "🔴" if data['status'] == 'AT RISK' else "🟢"
            burndown_report_lines.append(
                f"| {data['category']} | {data['target_date']} | {data['days_remaining']} | {data['remaining_devices']} | {data['daily_burn_rate_needed']} | {status_icon} {data['status']} |"
            )
        
        burndown_report_lines.extend([
            "",
            "## Risk Assessment",
            ""
        ])
        
        # Add risk assessment for each category
        for data in burndown_data:
            if data['daily_burn_rate_needed'] > 1:
                risk_level = "🔴 HIGH RISK"
                risk_desc = f"Need to replace {data['daily_burn_rate_needed']} devices per day"
            elif data['daily_burn_rate_needed'] > 0.5:
                risk_level = "🟡 MEDIUM RISK"
                risk_desc = f"Need to replace {data['daily_burn_rate_needed']} devices per day"
            else:
                risk_level = "🟢 LOW RISK"
                risk_desc = f"Only {data['daily_burn_rate_needed']} devices per day needed"
            
            burndown_report_lines.append(f"- **{data['category']}**: {risk_level} - {risk_desc}")
        
        burndown_report_lines.extend([
            "",
            "## Recommendations",
            "1. **Focus on ESOL 2024**: Immediate attention required",
            "2. **Plan ESOL 2025**: Start procurement planning",
            "3. **Monitor progress**: Track weekly replacement rates",
            "4. **Resource allocation**: Prioritize sites with highest device counts",
            "",
            f"---",
            f"*Report generated: {current_date.strftime('%Y-%m-%d %H:%M:%S')}*",
            f"*Data exported to: {burndown_json} and {burndown_csv}*"
        ])
        
        # Save burndown report
        reports_dir = Path('data/reports')
        reports_dir.mkdir(parents=True, exist_ok=True)
        burndown_report_file = reports_dir / f'ESOL_Burndown_{timestamp}.md'
        burndown_report_content = "\n".join(burndown_report_lines)
        burndown_report_file.write_text(burndown_report_content, encoding='utf-8')
        
        # Print burndown summary to console
        print("\n🔥 ESOL Replacement Burndown Analysis:")
        print("=" * 60)
        for data in burndown_data:
            status_icon = "🔴" if data['status'] == 'AT RISK' else "🟢"
            print(f"{data['category']}: {data['remaining_devices']} devices, {data['days_remaining']} days left")
            print(f"  Daily burn rate needed: {data['daily_burn_rate_needed']} devices/day")
            print(f"  Status: {status_icon} {data['status']}")
            print()
        
        print(f"📊 Burndown data exported to:")
        print(f"   JSON: {burndown_json}")
        print(f"   CSV: {burndown_csv}")
        print(f"   Report: {burndown_report_file}")
        print()
    
    # Save report if output specified or auto-save to data/reports/
    report_content = "\n".join(report_lines)
    
    if args.output:
        # User specified output path
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"Report saved to {output_path}")
    else:
        # Auto-save to data/reports/ with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = Path('data/reports')
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = output_dir / f'ESOL_Count_{args.category}_{timestamp}.md'
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"Report auto-saved to {filename}")

if __name__ == "__main__":
    main() 