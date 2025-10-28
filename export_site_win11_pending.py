#!/usr/bin/env python3
"""
Export Windows 11 Pending Devices by Site
Shows detailed information about devices that are eligible for Windows 11 upgrade but haven't been upgraded yet
"""

import pandas as pd
import yaml
import argparse
from pathlib import Path
from datetime import datetime

def export_site_win11_pending(site_name, output_file=None):
    """Export Windows 11 pending devices for a specific site"""
    
    # Load configuration
    config_file = Path('config/esol_criteria.yaml')
    win11_config_file = Path('config/win11_criteria.yaml')
    
    with open(config_file, 'r') as f:
        esol_config = yaml.safe_load(f)
    
    with open(win11_config_file, 'r') as f:
        win11_config = yaml.safe_load(f)
    
    data_mapping = esol_config['data_mapping']
    os_col = data_mapping['os_column']
    current_os_col = data_mapping['current_os_column']
    edition_col = data_mapping['edition_column']
    action_col = data_mapping['action_column']
    site_col = data_mapping['site_column']
    device_name_col = data_mapping['device_name_column']
    
    # Load data
    data_file = Path('data/raw/EUC_ESOL.xlsx')
    df = pd.read_excel(data_file)
    
    # Filter for specified site
    site_df = df[df[site_col] == site_name].copy()
    
    if len(site_df) == 0:
        print(f"❌ Site '{site_name}' not found in data")
        return None
    
    # Filter for Enterprise devices
    enterprise_df = site_df[site_df[edition_col] == 'Enterprise'].copy()
    
    print(f"\n{'='*80}")
    print(f"{site_name.upper()} WINDOWS 11 PENDING DEVICES")
    print(f"{'='*80}")
    print(f"\nTotal {site_name} Devices: {len(site_df)}")
    print(f"Total Enterprise Devices: {len(enterprise_df)}")
    
    # Get ESOL actions to exclude
    migration_categories = win11_config['migration_categories']
    esol_categories = esol_config['esol_categories']
    migration_actions = [esol_categories[cat]['action_value'] for cat in migration_categories]
    
    # Get Windows 11 patterns
    win11_patterns = win11_config['win11_patterns']
    win11_pattern = '|'.join(win11_patterns)
    
    # Step 1: Filter for eligible devices (excluding ESOL 2024/2025)
    eligible_mask = ~enterprise_df[action_col].isin(migration_actions)
    eligible_df = enterprise_df[eligible_mask].copy()
    
    print(f"\nEnterprise devices excluding ESOL 2024/2025: {len(eligible_df)}")
    
    # Show ESOL excluded devices
    esol_devices = enterprise_df[enterprise_df[action_col].isin(migration_actions)]
    if len(esol_devices) > 0:
        print(f"\nESOL excluded devices ({len(esol_devices)}):")
        print(f"  Categories: {migration_actions}")
        for _, row in esol_devices.iterrows():
            print(f"  - {row[device_name_col]}: {row[action_col]}")
    
    # Step 2: Filter for devices that support Win11 (capability check)
    win11_supported_mask = eligible_df[os_col].str.contains(win11_pattern, case=False, na=False)
    win11_supported_df = eligible_df[win11_supported_mask].copy()
    
    print(f"\nEnterprise devices that support Win11 (capability): {len(win11_supported_df)}")
    
    # Step 3: Check which devices are already upgraded
    current_os_mask = win11_supported_df[current_os_col].str.contains(win11_pattern, case=False, na=False)
    upgraded_df = win11_supported_df[current_os_mask].copy()
    pending_df = win11_supported_df[~current_os_mask].copy()
    
    print(f"\nUpgraded to Win11: {len(upgraded_df)}")
    print(f"Pending upgrade: {len(pending_df)}")
    
    # Show pending devices
    if len(pending_df) > 0:
        print(f"\n{'='*80}")
        print(f"PENDING WINDOWS 11 DEVICES IN {site_name.upper()} ({len(pending_df)} devices)")
        print(f"{'='*80}")
        print(f"\n{'Device Name':<20} {'Current OS':<20} {'EOSL Supported':<20} {'Action':<30}")
        print("-"*80)
        
        for _, row in pending_df.iterrows():
            device = row[device_name_col]
            current_os = str(row[current_os_col])
            eosl_supported = str(row[os_col])
            action = str(row[action_col])
            
            print(f"{device:<20} {current_os:<20} {eosl_supported:<20} {action:<30}")
    else:
        print("\n✅ No pending Windows 11 devices in Gillingham!")
    
    # Summary
    print(f"\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")
    print(f"Total Enterprise: {len(enterprise_df)}")
    print(f"Win11 Eligible: {len(win11_supported_df)}")
    print(f"Win11 Upgraded: {len(upgraded_df)}")
    print(f"Pending: {len(pending_df)}")
    print(f"\nEligibility %: {(len(win11_supported_df)/len(enterprise_df)*100):.1f}%")
    print(f"Upgrade % (of eligible): {(len(upgraded_df)/len(win11_supported_df)*100):.1f}%")
    print(f"Pending % (of eligible): {(len(pending_df)/len(win11_supported_df)*100):.1f}%")
    
    return pending_df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Export Windows 11 pending devices for a specific site')
    parser.add_argument('--site', '-s', default='Gillingham', help='Site name to analyze (default: Gillingham)')
    parser.add_argument('--output', '-o', help='Output CSV file (default: auto-generated with site name)')
    parser.add_argument('--list-sites', action='store_true', help='List all available sites')
    args = parser.parse_args()
    
    # List sites if requested
    if args.list_sites:
        data_file = Path('data/raw/EUC_ESOL.xlsx')
        df = pd.read_excel(data_file)
        config_file = Path('config/esol_criteria.yaml')
        with open(config_file, 'r') as f:
            esol_config = yaml.safe_load(f)
        site_col = esol_config['data_mapping']['site_column']
        sites = sorted([s for s in df[site_col].unique() if pd.notna(s)])
        print("\nAvailable sites:")
        for site in sites:
            print(f"  - {site}")
        exit(0)
    
    # Export pending devices for specified site
    pending_devices = export_site_win11_pending(args.site, args.output)
    
    # Export to CSV for further analysis
    if pending_devices is not None and len(pending_devices) > 0:
        if args.output:
            output_file = args.output
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'{args.site.lower().replace(" ", "_")}_pending_win11_{timestamp}.csv'
        pending_devices.to_csv(output_file, index=False)
        print(f"\nDetailed pending devices exported to: {output_file}")

