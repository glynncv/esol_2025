#!/usr/bin/env python3
"""EUC Device Inventory Summary Script - Extracts key metrics for cross-tool validation."""

import pandas as pd
import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path

def main():
    """Extract core EUC metrics and generate standardized summary report."""
    parser = argparse.ArgumentParser(description='EUC device inventory summary for validation')
    parser.add_argument('csv_file', help='Path to EUC_ESOL CSV/Excel file')
    parser.add_argument('--output', '-o', help='Output file (optional)')
    parser.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')
    parser.add_argument('--quiet', action='store_true', help='Quiet mode for automation')
    args = parser.parse_args()
    
    # Load data
    try:
        df = pd.read_excel(args.csv_file) if args.csv_file.endswith('.xlsx') else pd.read_csv(args.csv_file)
        required_cols = ['Action to take', 'OS Build', 'Enterprise or LTSC', 'Device Name', 'Last User LoggedOn']
        if not all(col in df.columns for col in required_cols):
            raise ValueError("Missing required columns")
    except Exception as e:
        print(f"Error loading data: {e}")
        return 1
    
    # Extract metrics
    total_devices = len(df)
    enterprise_count = len(df[df['Enterprise or LTSC'] == 'Enterprise'])
    ltsc_count = len(df[df['Enterprise or LTSC'] == 'LTSC'])
    esol_2024 = len(df[df['Action to take'] == 'Urgent Replacement'])
    esol_2025 = len(df[df['Action to take'] == 'Replace by 14/10/2025'])
    esol_2026 = len(df[df['Action to take'] == 'Replace by 11/11/2026'])
    total_esol = esol_2024 + esol_2025 + esol_2026
    
    # Windows 11 (Enterprise baseline)
    enterprise_df = df[df['Enterprise or LTSC'] == 'Enterprise']
    enterprise_win11 = len(enterprise_df[enterprise_df['OS Build'].str.contains('Win11', na=False)])
    win11_adoption = round((enterprise_win11 / enterprise_count) * 100, 1) if enterprise_count > 0 else 0
    enterprise_esol = len(enterprise_df[enterprise_df['Action to take'].isin(['Urgent Replacement', 'Replace by 14/10/2025'])])
    win11_compatibility = round(((enterprise_win11 + enterprise_esol) / enterprise_count) * 100, 1) if enterprise_count > 0 else 0
    
    # Kiosk detection
    kiosk_mask = df['Device Name'].str.contains('SHP', na=False) | df['Last User LoggedOn'].str.contains('kiosk', case=False, na=False)
    total_kiosks = len(df[kiosk_mask])
    enterprise_kiosks = len(df[kiosk_mask & (df['Enterprise or LTSC'] == 'Enterprise')])
    ltsc_kiosks = len(df[kiosk_mask & (df['Enterprise or LTSC'] == 'LTSC')])
    
    # Generate output
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data_hash = hashlib.md5(str(total_devices).encode()).hexdigest()[:8]
    
    if args.format == 'json':
        output_str = json.dumps({
            'timestamp': timestamp, 'total_devices': total_devices, 'enterprise_count': enterprise_count,
            'ltsc_count': ltsc_count, 'esol_2024': esol_2024, 'esol_2025': esol_2025, 'esol_2026': esol_2026,
            'win11_adoption': win11_adoption, 'win11_compatibility': win11_compatibility,
            'total_kiosks': total_kiosks, 'enterprise_kiosks': enterprise_kiosks, 'data_hash': data_hash
        }, indent=2)
    else:
        output_str = f"""=== EUC DEVICE INVENTORY SUMMARY ===
Analysis Timestamp: {timestamp}
Data Source: {Path(args.csv_file).name}

DEVICE INVENTORY OVERVIEW:
Total Devices: {total_devices:,}
Enterprise Devices: {enterprise_count:,} ({round((enterprise_count/total_devices)*100, 1)}%)
LTSC Devices: {ltsc_count:,} ({round((ltsc_count/total_devices)*100, 1)}%)

ESOL DEVICE BREAKDOWN:
ESOL 2024 (Urgent): {esol_2024:,} ({round((esol_2024/total_devices)*100, 1)}% of total)
ESOL 2025 (Oct 14): {esol_2025:,} ({round((esol_2025/total_devices)*100, 1)}% of total)
ESOL 2026 (Nov 11): {esol_2026:,} ({round((esol_2026/total_devices)*100, 1)}% of total)
Total Active ESOL: {total_esol:,} ({round((total_esol/total_devices)*100, 1)}% of total)

WINDOWS 11 STATUS (ENTERPRISE BASELINE):
Enterprise Win11 Devices: {enterprise_win11:,}
Win11 Adoption Rate: {win11_adoption}% (Enterprise only)
Win11 Compatibility Rate: {win11_compatibility}% (Enterprise baseline)
Projected Enterprise Win11: {enterprise_win11 + enterprise_esol:,} ({win11_compatibility}% adoption + ESOL replacement)

KIOSK DEVICE ANALYSIS:
Total Kiosk Devices: {total_kiosks:,}
Enterprise Kiosks: {enterprise_kiosks:,} ({round((enterprise_kiosks/total_kiosks)*100, 1) if total_kiosks > 0 else 0}% of total kiosks)
LTSC Kiosks: {ltsc_kiosks:,} ({round((ltsc_kiosks/total_kiosks)*100, 1) if total_kiosks > 0 else 0}% of total kiosks)
Enterprise Kiosks Needing LTSC: {enterprise_kiosks:,}

VALIDATION FINGERPRINT:
Data Hash: {data_hash}
Key Metric Sum: {total_devices + enterprise_count + total_esol + enterprise_win11 + total_kiosks}
Business Rule Version: YAML-2025-v1.0
==================================="""
    
    if args.output:
        Path(args.output).write_text(output_str, encoding='utf-8')
        if not args.quiet: print(f"Summary saved to {args.output}")
    elif not args.quiet: print(output_str)
    return 0

if __name__ == "__main__":
    exit(main())
