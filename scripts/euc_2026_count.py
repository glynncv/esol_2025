#!/usr/bin/env python3
"""
EUC 2026 Refresh Scope Counter

Counts the number of End User Computing (EUC) devices in scope for 2026 refresh
(i.e., where 'Action to take' == 'Replace by 11/11/2026') in the Excel file in data/raw.

Requirements:
    pip install pandas openpyxl

Usage:
    python euc_2026_count.py [filepath]
    # If no filepath is provided, defaults to data/raw/EUC_ESOL.xlsx
"""

import pandas as pd
import sys
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Count EUC devices in scope for 2026 refresh')
    parser.add_argument('filepath', nargs='?', default='data/raw/EUC_ESOL.xlsx', help='Path to the Excel file (default: data/raw/EUC_ESOL.xlsx)')
    args = parser.parse_args()

    filepath = Path(args.filepath)
    if not filepath.exists():
        print(f"❌ File not found: {filepath}")
        sys.exit(1)

    try:
        df = pd.read_excel(filepath, sheet_name='Export')
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        sys.exit(1)

    # Count devices in scope for 2026 refresh
    mask_2026 = df['Action to take'] == 'Replace by 11/11/2026'
    df_2026 = df[mask_2026]
    count_2026 = len(df_2026)
    total_devices = len(df)

    print(f"\nEUC 2026 Refresh Scope Summary for {filepath.name}")
    print(f"----------------------------------------------")
    print(f"Total devices: {total_devices:,}")
    print(f"Devices in scope for 2026 refresh (Action to take = 'Replace by 11/11/2026'): {count_2026:,}")
    if total_devices > 0:
        print(f"Percentage in scope: {count_2026 / total_devices * 100:.2f}%")
    else:
        print("No devices found in the file.")

    # Devices by site with cost
    print("\nDevices in scope for 2026 refresh by site:")
    export_rows = []
    if not df_2026.empty:
        if 'Site Location AD' in df_2026.columns and 'Cost for Replacement $' in df_2026.columns:
            site_group = df_2026.groupby('Site Location AD')
            print(f"{'Site':<30} {'Devices':>8} {'Total Cost':>18}")
            print("-" * 60)
            for site, group in site_group:
                count = len(group)
                cost = group['Cost for Replacement $'].sum()
                print(f"{site:<30} {count:>8} ${cost:>17,.0f}")
                export_rows.append({'Site': site, '# of Devices': count, 'Replacement Cost': cost})
            # Export to CSV
            export_df = pd.DataFrame(export_rows)
            export_df = export_df.sort_values(by='Replacement Cost', ascending=False)
            export_path = 'data/processed/euc_2026_site_summary.csv'
            export_df.to_csv(export_path, index=False)
            print(f"\nExported per-site summary to '{export_path}'")
        else:
            print("Required columns not found in the data.")
    else:
        print("No devices in scope for 2026 refresh.")

    # Total replacement cost
    if 'Cost for Replacement $' in df_2026.columns:
        total_cost = df_2026['Cost for Replacement $'].sum()
        print(f"\nTotal replacement cost for 2026 refresh: ${total_cost:,.0f}")
    else:
        print("\nCost for Replacement $ column not found in the data.")

if __name__ == "__main__":
    main() 