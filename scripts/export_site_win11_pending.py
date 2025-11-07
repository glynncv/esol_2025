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

def get_project_root():
    """Get the project root directory (parent of scripts/)"""
    return Path(__file__).parent.parent

def export_site_win11_pending(site_name, output_file=None):
    """Export Windows 11 pending devices for a specific site"""
    
    # Get project root for relative paths
    project_root = get_project_root()
    
    # Load configuration
    config_file = project_root / 'config/esol_criteria.yaml'
    win11_config_file = project_root / 'config/win11_criteria.yaml'
    
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
    data_file = project_root / 'data/raw/EUC_ESOL.xlsx'
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
    
    # EMEA file filters (matching EMEA_Win11_Pending.xlsx criteria):
    # - Current OS Build: Win10 1607, 1809, 1909, 21H2, 22H2, or Win7 (NOT Win11)
    # - EOSL Latest OS Build Supported: Win11 23H2 or Win11 24H2 (specific versions)
    # - Action to take: N/A, Redeploy, Replace by 11/11/2026, or Blank
    
    # Allowed current OS builds (matching EMEA file filter)
    allowed_current_os = ['Win10 1607', 'Win10 1809', 'Win10 1909', 'Win10 21H2', 'Win10 22H2', 'Win7']
    
    # Allowed EOSL Win11 versions (matching EMEA file filter)
    allowed_eosl_win11 = ['Win11 23H2', 'Win11 24H2']
    
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
    
    # Step 2: Filter for devices that support Win11 23H2 or 24H2 (capability check - matching EMEA file)
    eosl_win11_mask = eligible_df[os_col].isin(allowed_eosl_win11) | \
                      eligible_df[os_col].str.contains('Win11 23H2|Win11 24H2', case=False, na=False, regex=True)
    win11_supported_df = eligible_df[eosl_win11_mask].copy()
    
    print(f"\nEnterprise devices that support Win11 23H2 or 24H2 (capability): {len(win11_supported_df)}")
    
    # Step 3: Filter for devices with allowed current OS builds (NOT Win11 - matching EMEA file)
    # Use regex pattern without capture groups to avoid warning
    current_os_allowed_mask = win11_supported_df[current_os_col].isin(allowed_current_os) | \
                              win11_supported_df[current_os_col].str.contains('Win10 (?:1607|1809|1909|21H2|22H2)|Win7', 
                                                                              case=False, na=False, regex=True)
    win11_supported_df = win11_supported_df[current_os_allowed_mask].copy()
    
    print(f"\nEnterprise devices with allowed current OS (Win10 1607/1809/1909/21H2/22H2 or Win7): {len(win11_supported_df)}")
    
    # Step 4: Check which devices are already upgraded (for reporting, but EMEA file excludes these)
    # Note: EMEA file explicitly excludes Win11 from current OS filter, so all matching devices are pending
    current_os_win11_mask = win11_supported_df[current_os_col].str.contains(win11_pattern, case=False, na=False)
    upgraded_df = win11_supported_df[current_os_win11_mask].copy()
    pending_df = win11_supported_df[~current_os_win11_mask].copy()
    
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
        print("\n✅ No pending Windows 11 devices!")
    
    # Summary
    print(f"\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")
    print(f"Total Enterprise: {len(enterprise_df)}")
    print(f"Win11 Eligible: {len(win11_supported_df)}")
    print(f"Win11 Upgraded: {len(upgraded_df)}")
    print(f"Pending: {len(pending_df)}")
    
    # Calculate percentages with division by zero protection
    eligibility_pct = (len(win11_supported_df)/len(enterprise_df)*100) if len(enterprise_df) > 0 else 0
    upgrade_pct = (len(upgraded_df)/len(win11_supported_df)*100) if len(win11_supported_df) > 0 else 0
    pending_pct = (len(pending_df)/len(win11_supported_df)*100) if len(win11_supported_df) > 0 else 0
    
    print(f"\nEligibility %: {eligibility_pct:.1f}%")
    print(f"Upgrade % (of eligible): {upgrade_pct:.1f}%")
    print(f"Pending % (of eligible): {pending_pct:.1f}%")
    
    return pending_df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Export Windows 11 pending devices for a specific site')
    parser.add_argument('--site', '-s', default='Gillingham', help='Site name to analyze (default: Gillingham)')
    parser.add_argument('--output', '-o', help='Output CSV file (default: auto-generated with site name)')
    parser.add_argument('--list-sites', action='store_true', help='List all available sites')
    args = parser.parse_args()
    
    # Get project root for relative paths
    project_root = get_project_root()
    
    # List sites if requested
    if args.list_sites:
        data_file = project_root / 'data/raw/EUC_ESOL.xlsx'
        df = pd.read_excel(data_file)
        config_file = project_root / 'config/esol_criteria.yaml'
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
            # Resolve relative paths relative to project root, absolute paths as-is
            output_file = Path(args.output)
            if not output_file.is_absolute():
                output_file = project_root / output_file
            output_file.parent.mkdir(parents=True, exist_ok=True)
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            processed_dir = project_root / 'data/processed'
            processed_dir.mkdir(parents=True, exist_ok=True)
            output_file = processed_dir / f'{args.site.lower().replace(" ", "_")}_pending_win11_{timestamp}.csv'
        pending_devices.to_csv(output_file, index=False)
        print(f"\nDetailed pending devices exported to: {output_file}")

