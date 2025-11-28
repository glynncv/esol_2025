#!/usr/bin/env python3
"""
Export Windows 11 Pending Devices by Site
Shows detailed information about devices that are eligible for Windows 11 upgrade but haven't been upgraded yet
"""

import pandas as pd
import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add the scripts directory to the path
sys.path.append(str(Path(__file__).parent))

from separated_esol_analyzer import ConfigManager
from data_utils import get_data_file_path, add_data_file_argument, validate_data_file

def export_site_win11_pending(df, site_name, esol_config, win11_config):
    """Export Windows 11 pending devices for a specific site

    Args:
        df: DataFrame with EUC device data
        site_name: Name of the site to analyze
        esol_config: ESOL configuration dictionary
        win11_config: Windows 11 configuration dictionary

    Returns:
        DataFrame with pending devices or None if site not found
    """
    data_mapping = esol_config['data_mapping']
    os_col = data_mapping['os_column']
    current_os_col = data_mapping['current_os_column']
    edition_col = data_mapping['edition_column']
    action_col = data_mapping['action_column']
    site_col = data_mapping['site_column']
    device_name_col = data_mapping['device_name_column']

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

def main():
    """Main entry point for export script"""
    parser = argparse.ArgumentParser(description='Export Windows 11 pending devices for a specific site')
    add_data_file_argument(parser, 'Path to EUC_ESOL.xlsx file')
    parser.add_argument('--site', '-s', default='Gillingham', help='Site name to analyze (default: Gillingham)')
    parser.add_argument('--output', '-o', help='Output CSV file (default: auto-generated with site name in data/processed/)')
    parser.add_argument('--list-sites', action='store_true', help='List all available sites')
    args = parser.parse_args()

    # Load configuration
    # Find project root (go up from scripts/ to project root)
    project_root = Path(__file__).resolve().parent.parent
    config_path = str(project_root / 'config')
    config_manager = ConfigManager(config_path=config_path)
    esol_config = config_manager.get_esol_criteria()
    win11_config = config_manager.get_win11_criteria()

    # Read the Excel file
    data_file = get_data_file_path(args.data_file)
    validate_data_file(data_file)
    df = pd.read_excel(data_file)

    # List sites if requested
    if args.list_sites:
        site_col = esol_config['data_mapping']['site_column']
        sites = sorted([s for s in df[site_col].unique() if pd.notna(s)])
        print("\nAvailable sites:")
        for site in sites:
            print(f"  - {site}")
        return

    # Export pending devices for specified site
    pending_devices = export_site_win11_pending(df, args.site, esol_config, win11_config)

    # Export to CSV for further analysis
    if pending_devices is not None and len(pending_devices) > 0:
        if args.output:
            output_file = Path(args.output)
            output_file.parent.mkdir(parents=True, exist_ok=True)
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            processed_dir = project_root / 'data' / 'processed'
            processed_dir.mkdir(parents=True, exist_ok=True)
            output_file = processed_dir / f'{args.site.lower().replace(" ", "_")}_pending_win11_{timestamp}.csv'
        pending_devices.to_csv(output_file, index=False)
        print(f"\nDetailed pending devices exported to: {output_file}")

if __name__ == "__main__":
    main()
