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
    """Analyze Windows 11 EUC counts focused on Enterprise devices and export summary report."""
    parser = argparse.ArgumentParser(description='Analyze Windows 11 EUC counts for Enterprise devices')
    add_data_file_argument(parser, 'Path to EUC_ESOL.xlsx file')
    parser.add_argument('--output', '-o', help='Output file for the report (optional - auto-saves to data/reports/ if not specified)')
    parser.add_argument('--site-table', action='store_true', help='Generate site-level breakdown table of Windows 11 migration workload')
    parser.add_argument('--burndown', action='store_true', help='Generate Windows 11 upgrade burndown report')
    args = parser.parse_args()
    
    # Load configuration
    config_manager = ConfigManager()
    esol_config = config_manager.get_esol_criteria()
    win11_config = config_manager.get_win11_criteria()
    data_mapping = esol_config['data_mapping']
    
    # Read the Excel file
    data_file = get_data_file_path(args.data_file)
    validate_data_file(data_file)
    df = pd.read_excel(data_file)
    
    # Get column mappings
    os_col = data_mapping['os_column']  # EOSL Latest OS Build Supported - used for Win11 eligibility
    current_os_col = data_mapping['current_os_column']  # Current OS Build - used for Win11 upgrade status
    edition_col = data_mapping['edition_column']
    action_col = data_mapping['action_column']
    site_col = data_mapping['site_column']
    
    # Filter for Enterprise EUCs only (the 2025 Windows 11 push target)
    enterprise_mask = df[edition_col] == 'Enterprise'
    enterprise_df = df[enterprise_mask]
    
    # Get Windows 11 patterns and ESOL actions
    win11_patterns = win11_config['win11_patterns']
    win11_pattern = '|'.join(win11_patterns)
    
    # Get ESOL actions to exclude them
    migration_categories = win11_config['migration_categories']
    migration_actions = [esol_config['esol_categories'][cat]['action_value'] for cat in migration_categories]
    
    # Calculate Windows 11 eligible devices (Enterprise devices that SUPPORT Win11, excluding ESOL)
    eligible_mask = (
        ~enterprise_df[action_col].isin(migration_actions) &
        enterprise_df[os_col].str.contains(win11_pattern, case=False, na=False)
    )
    eligible_df = enterprise_df[eligible_mask]
    total_eligible = len(eligible_df)
    
    # Count eligible Enterprise EUCs already on Windows 11 (check current OS installation)
    enterprise_win11_mask = eligible_df[current_os_col].str.contains(win11_pattern, case=False, na=False)
    enterprise_win11_count = len(eligible_df[enterprise_win11_mask])
    
    # Count Enterprise EUCs that will get Windows 11 via ESOL replacement
    enterprise_esol_mask = enterprise_df[action_col].isin(migration_actions)
    enterprise_esol_count = len(enterprise_df[enterprise_esol_mask])
    
    # Calculate totals
    total_enterprise = len(enterprise_df)
    total_enterprise_win11_path = enterprise_win11_count + enterprise_esol_count
    win11_adoption_pct = round((total_enterprise_win11_path / total_enterprise) * 100, 2) if total_enterprise > 0 else 0
    current_win11_pct = round((enterprise_win11_count / total_enterprise) * 100, 2) if total_enterprise > 0 else 0
    
    # Site-level analysis if requested
    if args.site_table:
        # Generate comprehensive site summary for Windows 11 deployment
        site_data = enterprise_df.groupby(site_col).agg({
            'Device Name': 'count'  # Total Enterprise devices per site
        }).rename(columns={'Device Name': 'Total_Devices'})
        
        # Calculate Windows 11 eligible devices (Enterprise devices excluding ESOL 2024/2025 that support Win11)
        eligible_mask = ~enterprise_df[action_col].isin(migration_actions)
        eligible_df = enterprise_df[eligible_mask]
        
        # Filter for devices that support Win11 (EOSL Latest OS Build Supported)
        win11_supported_mask = eligible_df[os_col].str.contains(win11_pattern, case=False, na=False)
        win11_supported_df = eligible_df[win11_supported_mask]
        
        eligible_counts = win11_supported_df.groupby(site_col)['Device Name'].count()
        site_data['Win11_Eligible_Count'] = site_data.index.map(eligible_counts).fillna(0).astype(int)
        
        # Calculate Windows 11 devices (of those eligible, how many have Win11 OS)
        # Check Current OS Build for devices that are already upgraded
        current_os_col = data_mapping['current_os_column']  # Use Current OS Build for upgrade status
        win11_upgraded_mask = (
            win11_supported_df[current_os_col].str.contains(win11_pattern, case=False, na=False)
        )
        win11_upgraded_df = win11_supported_df[win11_upgraded_mask]
        win11_counts = win11_upgraded_df.groupby(site_col)['Device Name'].count()
        site_data['Win11_Count'] = site_data.index.map(win11_counts).fillna(0).astype(int)
        
        # Calculate Pending devices (of those eligible, how many are still pending upgrade)
        site_data['Pending_Count'] = site_data['Win11_Eligible_Count'] - site_data['Win11_Count']
        
        # Calculate percentages
        site_data['Win11_Eligible_Pct'] = (site_data['Win11_Eligible_Count'] / site_data['Total_Devices'] * 100).round(1)
        # Win11 and Pending percentages are relative to eligible devices
        site_data['Win11_Pct'] = (site_data['Win11_Count'] / site_data['Win11_Eligible_Count'] * 100).round(1)
        site_data['Pending_Pct'] = (site_data['Pending_Count'] / site_data['Win11_Eligible_Count'] * 100).round(1)
        
        # Handle division by zero for sites with no eligible devices
        site_data['Win11_Pct'] = site_data['Win11_Pct'].fillna(0)
        site_data['Pending_Pct'] = site_data['Pending_Pct'].fillna(0)
        
        # Ensure all count columns are integers (no decimals)
        site_data['Total_Devices'] = site_data['Total_Devices'].astype(int)
        site_data['Win11_Eligible_Count'] = site_data['Win11_Eligible_Count'].astype(int)
        site_data['Win11_Count'] = site_data['Win11_Count'].astype(int)
        site_data['Pending_Count'] = site_data['Pending_Count'].astype(int)
        
        # Reorder columns
        site_data = site_data[['Total_Devices', 'Win11_Eligible_Count', 'Win11_Eligible_Pct', 
                              'Win11_Count', 'Win11_Pct', 'Pending_Count', 'Pending_Pct']]
        
        # Filter for sites with devices and sort by total devices
        site_data = site_data[site_data['Total_Devices'] > 0].sort_values('Total_Devices', ascending=False)
        
        # Export to data/processed
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        processed_dir = Path('data/processed')
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Export as CSV
        csv_file = processed_dir / f'site_win11_summary_{timestamp}.csv'
        site_data.to_csv(csv_file)
        
        # Export as JSON
        json_file = processed_dir / f'site_win11_summary_{timestamp}.json'
        site_data.to_json(json_file, orient='index', indent=2)
        
        print("\nSite Summary - Windows 11 Deployment Status:")
        print("=" * 120)
        print(f"{'Site':<25} | {'Total':<6} | {'Win11 Eligible':<15} | {'Win11':<15} | {'Pending':<15}")
        print(f"{'':<25} | {'Devices':<6} | {'# (%) Eligible':<15} | {'# (%) Upgraded':<15} | {'# (%) Pending':<15}")
        print("-" * 120)
        
        for site, row in site_data.iterrows():
            print(f"{site:<25} | {int(row['Total_Devices']):>6} | {int(row['Win11_Eligible_Count']):>3} ({row['Win11_Eligible_Pct']:>4.1f}%) | {int(row['Win11_Count']):>3} ({row['Win11_Pct']:>4.1f}%) | {int(row['Pending_Count']):>3} ({row['Pending_Pct']:>4.1f}%)")
        
        print(f"\n📊 Site breakdown exported to:")
        print(f"   CSV: {csv_file}")
        print(f"   JSON: {json_file}")
        print()
    
    # Burndown analysis if requested
    if args.burndown:
        # Generate Windows 11 upgrade burndown report
        
        # Get KPI target date from config
        target_date_str = win11_config.get('kpi_target_date', '2025-10-31')
        target_date = datetime.strptime(target_date_str, '%Y-%m-%d')
        current_date = datetime.now()
        days_remaining = (target_date - current_date).days
        
        # Calculate burndown metrics (total_eligible already calculated above - only Win11 eligible devices)
        completed_count = enterprise_win11_count
        remaining_count = total_eligible - completed_count
        completion_percentage = round((completed_count / total_eligible) * 100, 1) if total_eligible > 0 else 0
        
        # Calculate daily burn rate needed
        daily_burn_rate_needed = remaining_count / days_remaining if days_remaining > 0 else 0
        
        # Generate burndown data
        burndown_data = {
            'analysis_date': current_date.strftime('%Y-%m-%d'),
            'target_date': target_date_str,
            'days_remaining': days_remaining,
            'total_eligible_devices': total_eligible,
            'completed_devices': completed_count,
            'remaining_devices': remaining_count,
            'completion_percentage': completion_percentage,
            'daily_burn_rate_needed': round(daily_burn_rate_needed, 2),
            'kpi_status': 'ON TRACK' if completion_percentage >= 100 else 'AT RISK'
        }
        
        # Export burndown data
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        processed_dir = Path('data/processed')
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Export as JSON
        burndown_json = processed_dir / f'win11_burndown_{timestamp}.json'
        import json
        with open(burndown_json, 'w') as f:
            json.dump(burndown_data, f, indent=2)
        
        # Export as CSV for historical tracking
        burndown_csv = processed_dir / f'win11_burndown_{timestamp}.csv'
        burndown_df = pd.DataFrame([burndown_data])
        burndown_df.to_csv(burndown_csv, index=False)
        
        # Generate burndown report
        burndown_report = f"""# Windows 11 Upgrade Burndown Report - {current_date.strftime('%Y-%m-%d %H:%M:%S')}

## KPI Target
**Target Date:** {target_date_str}
**Target:** 100% of eligible EUCs upgraded
**Days Remaining:** {days_remaining}

## Current Status
**Total Eligible Devices:** {total_eligible:,}
**Completed Upgrades:** {completed_count:,}
**Remaining Upgrades:** {remaining_count:,}
**Completion Percentage:** {completion_percentage}%

## Burndown Analysis
**Daily Burn Rate Needed:** {daily_burn_rate_needed:.2f} devices/day
**KPI Status:** {burndown_data['kpi_status']}

## Risk Assessment
"""
        
        if days_remaining > 0:
            if daily_burn_rate_needed > 1:
                burndown_report += f"- **🔴 HIGH RISK:** Need to upgrade {daily_burn_rate_needed:.2f} devices per day\n"
            elif daily_burn_rate_needed > 0.5:
                burndown_report += f"- **🟡 MEDIUM RISK:** Need to upgrade {daily_burn_rate_needed:.2f} devices per day\n"
            else:
                burndown_report += f"- **🟢 LOW RISK:** Only {daily_burn_rate_needed:.2f} devices per day needed\n"
        else:
            burndown_report += f"- **{'✅ TARGET MET' if completion_percentage >= 100 else '❌ TARGET MISSED'}**\n"
        
        burndown_report += f"""
## Recommendations
1. **Focus on sites with highest pending counts**
2. **Accelerate upgrade process if burn rate is insufficient**
3. **Monitor progress weekly to stay on track**
4. **Consider resource reallocation if behind schedule**

---
*Report generated: {current_date.strftime('%Y-%m-%d %H:%M:%S')}*
*Data exported to: {burndown_json} and {burndown_csv}*
"""
        
        # Save burndown report
        reports_dir = Path('data/reports')
        reports_dir.mkdir(parents=True, exist_ok=True)
        burndown_report_file = reports_dir / f'Win11_Burndown_{timestamp}.md'
        burndown_report_file.write_text(burndown_report, encoding='utf-8')
        
        # Print burndown summary to console
        print("\n🔥 Windows 11 Upgrade Burndown Analysis:")
        print("=" * 60)
        print(f"Target Date: {target_date_str}")
        print(f"Days Remaining: {days_remaining}")
        print(f"Total Eligible: {total_eligible:,}")
        print(f"Completed: {completed_count:,} ({completion_percentage}%)")
        print(f"Remaining: {remaining_count:,}")
        print(f"Daily Burn Rate Needed: {daily_burn_rate_needed:.2f} devices/day")
        print(f"KPI Status: {burndown_data['kpi_status']}")
        print(f"\n📊 Burndown data exported to:")
        print(f"   JSON: {burndown_json}")
        print(f"   CSV: {burndown_csv}")
        print(f"   Report: {burndown_report_file}")
        print()
    
    # Calculate KPI metrics (total_eligible already calculated above - only Win11 eligible devices)
    eligible_upgraded_pct = round((enterprise_win11_count / total_eligible) * 100, 2) if total_eligible > 0 else 0
    eligible_pending_count = total_eligible - enterprise_win11_count
    eligible_pending_pct = round((eligible_pending_count / total_eligible) * 100, 2) if total_eligible > 0 else 0
    
    # Generate report content
    report_content = f"""# Windows 11 EUC Analysis - Enterprise Focus - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Enterprise EUC Windows 11 Strategy
**Total Enterprise EUCs:** {total_enterprise:,}
**Enterprise EUCs already on Windows 11:** {enterprise_win11_count:,} ({current_win11_pct}%)
**Enterprise EUCs getting Windows 11 via ESOL replacement:** {enterprise_esol_count:,}
**Total Enterprise Windows 11 adoption path:** {total_enterprise_win11_path:,} ({win11_adoption_pct}%)

## Windows 11 Upgrade KPI (Target: 100% by Oct 2025)
**Total Windows 11 Eligible EUCs:** {total_eligible:,} (excluding ESOL replacement devices)
**Already Upgraded:** {enterprise_win11_count:,} ({eligible_upgraded_pct}%)
**Pending Upgrade:** {eligible_pending_count:,} ({eligible_pending_pct}%)
**KPI Status:** {"🟢 ON TRACK" if eligible_upgraded_pct >= 100 else "🔴 AT RISK"} - {eligible_pending_count:,} devices need upgrade by Oct 2025

## Summary
- **Current Windows 11 adoption:** {current_win11_pct}% of Enterprise EUCs
- **Projected Windows 11 adoption:** {win11_adoption_pct}% of Enterprise EUCs (via replacement + upgrade)
- **Upgrade KPI Progress:** {eligible_upgraded_pct}% of eligible devices upgraded
- **LTSC devices excluded:** Not part of 2025 Windows 11 push strategy"""
    
    # Print to console
    print(f"Total Enterprise EUCs: {total_enterprise:,}")
    print(f"Enterprise EUCs already on Windows 11: {enterprise_win11_count:,} ({current_win11_pct}%)")
    print(f"Enterprise EUCs getting Windows 11 via ESOL replacement: {enterprise_esol_count:,}")
    print(f"Total Enterprise Windows 11 adoption path: {total_enterprise_win11_path:,} ({win11_adoption_pct}%)")
    print()
    print("🎯 Windows 11 Upgrade KPI (Target: 100% by Oct 2025):")
    print(f"Total Windows 11 Eligible EUCs: {total_eligible:,} (excluding ESOL replacement)")
    print(f"Already Upgraded: {enterprise_win11_count:,} ({eligible_upgraded_pct}%)")
    print(f"Pending Upgrade: {eligible_pending_count:,} ({eligible_pending_pct}%)")
    print(f"KPI Status: {'🟢 ON TRACK' if eligible_upgraded_pct >= 100 else '🔴 AT RISK'} - {eligible_pending_count:,} devices need upgrade by Oct 2025")
    
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