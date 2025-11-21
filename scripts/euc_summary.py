#!/usr/bin/env python3
"""EUC Device Inventory Summary Script - Extracts key metrics for cross-tool validation."""

import pandas as pd
import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

# Add the scripts directory to the path
sys.path.append(str(Path(__file__).parent))

from separated_esol_analyzer import ConfigManager
from data_utils import get_data_file_path, add_data_file_argument, validate_data_file

def main():
    """Extract core EUC metrics and generate standardized summary report."""
    parser = argparse.ArgumentParser(description='EUC device inventory summary for validation')
    add_data_file_argument(parser, 'Path to EUC_ESOL CSV/Excel file')
    parser.add_argument('--output', '-o', help='Output file (optional)')
    parser.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')
    parser.add_argument('--quiet', action='store_true', help='Quiet mode for automation')
    args = parser.parse_args()

    # Load configuration
    config_manager = ConfigManager()
    esol_config = config_manager.get_esol_criteria()
    win11_config = config_manager.get_win11_criteria()
    data_mapping = esol_config['data_mapping']
    esol_categories = esol_config['esol_categories']
    kiosk_config = esol_config['kiosk_detection']

    # Get column names from config
    action_col = data_mapping['action_column']
    current_os_col = data_mapping['current_os_column']
    edition_col = data_mapping['edition_column']
    device_name_col = data_mapping['device_name_column']
    user_columns = data_mapping['user_columns']
    last_user_col = user_columns['last']

    # Get ESOL action values from config
    esol_2024_action = esol_categories['esol_2024']['action_value']
    esol_2025_action = esol_categories['esol_2025']['action_value']
    esol_2026_action = esol_categories['esol_2026']['action_value']

    # Get Windows 11 patterns from config
    win11_patterns = win11_config['win11_patterns']
    win11_pattern = '|'.join(win11_patterns)

    # Get kiosk detection patterns from config
    device_patterns = kiosk_config['device_name_patterns']
    user_patterns = kiosk_config['user_loggedon_patterns']

    # Load data
    try:
        data_file = get_data_file_path(args.data_file)
        validate_data_file(data_file)

        df = pd.read_excel(data_file) if data_file.endswith('.xlsx') else pd.read_csv(data_file)
        required_cols = [action_col, current_os_col, edition_col, device_name_col, last_user_col]
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"Missing required columns. Expected: {required_cols}")
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        sys.exit(1)

    # Extract metrics
    total_devices = len(df)
    enterprise_count = len(df[df[edition_col] == 'Enterprise'])
    ltsc_count = len(df[df[edition_col] == 'LTSC'])
    esol_2024 = len(df[df[action_col] == esol_2024_action])
    esol_2025 = len(df[df[action_col] == esol_2025_action])
    esol_2026 = len(df[df[action_col] == esol_2026_action])
    total_esol = esol_2024 + esol_2025 + esol_2026

    # Windows 11 (Enterprise baseline)
    enterprise_df = df[df[edition_col] == 'Enterprise']
    enterprise_win11 = len(enterprise_df[enterprise_df[current_os_col].str.contains(win11_pattern, case=False, na=False)])
    win11_adoption = round((enterprise_win11 / enterprise_count) * 100, 1) if enterprise_count > 0 else 0
    enterprise_esol = len(enterprise_df[enterprise_df[action_col].isin([esol_2024_action, esol_2025_action])])
    win11_compatibility = round(((enterprise_win11 + enterprise_esol) / enterprise_count) * 100, 1) if enterprise_count > 0 else 0

    # Kiosk detection (using patterns from config)
    device_pattern = '|'.join(device_patterns)
    user_pattern = '|'.join(user_patterns)
    kiosk_mask = df[device_name_col].str.contains(device_pattern, na=False) | df[last_user_col].str.contains(user_pattern, case=False, na=False)
    total_kiosks = len(df[kiosk_mask])
    enterprise_kiosks = len(df[kiosk_mask & (df[edition_col] == 'Enterprise')])
    ltsc_kiosks = len(df[kiosk_mask & (df[edition_col] == 'LTSC')])
    
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
Data Source: {Path(data_file).name}

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
    
    # Save report
    if args.output:
        Path(args.output).write_text(output_str, encoding='utf-8')
        if not args.quiet: print(f"Summary saved to {args.output}")
    else:
        # Auto-save to data/reports/ with timestamped filename
        output_dir = Path('data/reports')
        output_dir.mkdir(parents=True, exist_ok=True)
        extension = '.json' if args.format == 'json' else '.txt'
        filename = output_dir / f'EUC_Summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}{extension}'
        filename.write_text(output_str, encoding='utf-8')
        if not args.quiet: print(f"Report auto-saved to {filename}")
    
    if not args.quiet: print(output_str)
    return 0

if __name__ == "__main__":
    exit(main())
